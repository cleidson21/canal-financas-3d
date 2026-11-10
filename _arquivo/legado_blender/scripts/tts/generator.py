"""Motor de geração de voz Gemini 3.8 TTS via Interactions API e gestão de metadados."""

from __future__ import annotations

import base64
import io
import json
import time
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from .config import (
    ALLOWED_MODELS,
    DEFAULT_MODEL,
    DEFAULT_SAMPLE_RATE,
    DOCUMENTED_VOICES,
    TTSRequestConfig,
    check_credentials,
    get_api_key_silently,
    sanitize_message,
)
from .validator import validate_wav_file


def get_metadata_path(wav_path: Union[str, Path]) -> Path:
    """Retorna o caminho do arquivo JSON de metadados associado ao arquivo WAV."""
    path = Path(wav_path)
    return path.with_suffix(path.suffix + ".meta.json")


def load_metadata(wav_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """Carrega os metadados técnicos de um arquivo WAV caso existam."""
    meta_path = get_metadata_path(wav_path)
    if meta_path.is_file():
        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def mark_as_approved(wav_path: Union[str, Path], approved: bool = True, notes: str = "") -> Path:
    """Marca ou desmarca um arquivo WAV como aprovado para impedir regeneração acidental."""
    path = Path(wav_path)
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo WAV não encontrado para aprovação: {path}")

    meta = load_metadata(path) or {}
    meta["approved"] = approved
    meta["approved_updated_at"] = datetime.now(timezone.utc).isoformat()
    if notes:
        meta["approval_notes"] = notes

    meta_path = get_metadata_path(path)
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta_path


def _classify_api_error(exc: Exception) -> Dict[str, Any]:
    """Classifica erros da API (permissão, cota/faturamento, modelo indisponível, rede) sem expor segredos."""
    raw_msg = sanitize_message(str(exc))
    status_code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    lower_msg = raw_msg.lower()

    category = "unknown_api_error"
    if status_code == 401 or "api_key_invalid" in lower_msg or "unauthenticated" in lower_msg:
        category = "authentication_error"
    elif status_code == 403 or "permission_denied" in lower_msg or "forbidden" in lower_msg:
        if "billing" in lower_msg:
            category = "billing_required_error"
        else:
            category = "permission_error"
    elif status_code == 429 or "resource_exhausted" in lower_msg or "quota" in lower_msg:
        if "free_tier" in lower_msg or "billing" in lower_msg or "limit: 0" in lower_msg:
            category = "quota_or_free_tier_unavailable"
        else:
            category = "rate_limit_or_quota_exceeded"
    elif status_code == 404 or "not_found" in lower_msg or "not found" in lower_msg:
        category = "model_unavailable_or_not_found"
    elif status_code == 400 or "invalid_argument" in lower_msg:
        category = "invalid_request_parameter"

    return {
        "error_type": type(exc).__name__,
        "status_code": status_code,
        "category": category,
        "message": raw_msg,
    }


def _create_client() -> genai.Client:
    """Instancia o cliente oficial google-genai usando a chave configurada."""
    api_key = get_api_key_silently()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY não encontrada na variável de ambiente nem no arquivo .env local."
        )
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(attempts=1)))


def verify_model_access(model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Verifica conectividade, autenticação e disponibilidade do modelo no catálogo.
    Nota: diferencia claramente autenticação/listagem de autorização efetiva de geração.
    """
    from .generation_policy import read, POLICY
    if read(POLICY).get('remote_checks_enabled') is not True:
        return dict(authentication_valid=False,model_listed=False,quota_status='unknown',
            billing_status='unknown',error={'category':'remote_checks_disabled',
            'message':'Verificação remota desativada; nenhuma chamada feita'})
    cred_status = check_credentials()
    result: Dict[str, Any] = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "sdk_version": genai.__version__,
        "target_model": model,
        "credentials": cred_status,
        "authentication_valid": False,
        "model_listed": False,
        "model_info": None,
        "available_tts_models": [],
        "generation_authorized_note": (
            "A presença no catálogo confirma autenticação e visibilidade do modelo, "
            "mas não comprova saldo de cota, camada gratuita ou ausência de cobrança."
        ),
        "error": None,
    }

    if not cred_status["configured"]:
        result["error"] = {
            "category": "missing_credentials",
            "message": "Nenhuma credencial GEMINI_API_KEY configurada.",
        }
        return result

    try:
        client = _create_client()
        tts_models = []
        for m in client.models.list():
            m_name = getattr(m, "name", "") or ""
            if "tts" in m_name.lower():
                tts_models.append(m_name)

        result["authentication_valid"] = True
        result["available_tts_models"] = tts_models

        model_obj = client.models.get(model=model)
        expected_id = model if model.startswith("models/") else f"models/{model}"
        result["model_listed"] = (
            getattr(model_obj, "name", "") == expected_id or expected_id in tts_models
        )
        result["model_info"] = {
            "name": getattr(model_obj, "name", None),
            "display_name": getattr(model_obj, "display_name", None),
            "description": getattr(model_obj, "description", None),
            "supported_actions": getattr(model_obj, "supported_actions", None),
            "input_token_limit": getattr(model_obj, "input_token_limit", None),
            "output_token_limit": getattr(model_obj, "output_token_limit", None),
        }
    except Exception as exc:
        result["error"] = _classify_api_error(exc)

    return result


def _ensure_wav_bytes(
    raw_bytes: bytes,
    mime_type: Optional[str],
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    channels: int = 1,
) -> tuple[bytes, str]:
    """
    Garante que os bytes de áudio possuam cabeçalho RIFF/WAVE válido.
    Retorna (wav_bytes, container_origin), onde container_origin indica se já veio como RIFF/WAV
    nativo da API ou se foi encapsulado a partir de PCM linear (audio/l16).
    """
    if len(raw_bytes) >= 12 and raw_bytes[:4] == b"RIFF" and raw_bytes[8:12] == b"WAVE":
        return raw_bytes, "native_riff_wav"

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels or 1)
        wf.setsampwidth(2)  # 16-bit PCM linear
        wf.setframerate(sample_rate or DEFAULT_SAMPLE_RATE)
        wf.writeframes(raw_bytes)
    return buffer.getvalue(), f"wrapped_from_{mime_type or 'pcm_l16'}"


def _extract_usage_metadata(interaction: Any) -> Dict[str, Any]:
    """Extrai informações reais de uso de tokens retornadas pela API, sem inventar estimativas."""
    usage_obj = getattr(interaction, "usage", None)
    if usage_obj is None:
        return {"reported_by_api": False}

    usage_dict: Dict[str, Any] = {"reported_by_api": True}
    if hasattr(usage_obj, "model_dump"):
        dumped = usage_obj.model_dump(exclude_none=True)
        usage_dict.update(dumped)
    else:
        for attr in (
            "total_input_tokens",
            "total_output_tokens",
            "total_tokens",
            "total_thought_tokens",
            "input_tokens",
            "output_tokens",
        ):
            val = getattr(usage_obj, attr, None)
            if val is not None:
                usage_dict[attr] = val

    return usage_dict


def generate_speech(config: TTSRequestConfig) -> Dict[str, Any]:
    """
    Gera um arquivo WAV utilizando a Interactions API do Gemini 3.8 TTS.
    Mantém o texto literal em `text` e instruções de atuação em `speech_metadata.style`.
    Evita regeneração acidental de arquivos existentes ou aprovados.
    """
    from .generation_policy import check_identity, check_reuse, reserve_generation, record_quota_block
    check_identity(config)
    if config.model not in ALLOWED_MODELS:
        raise ValueError(
            f"Modelo '{config.model}' não permitido. Modelos autorizados: {ALLOWED_MODELS}"
        )

    output_path = Path(config.output_path)
    existing_meta = load_metadata(output_path)

    # Proteção contra regeneração acidental de arquivos aprovados ou já existentes
    if output_path.is_file():
        canonically_approved = check_reuse(output_path)
        is_approved = canonically_approved or bool(existing_meta and existing_meta.get("approved") is True)
        if is_approved and config.protect_approved:
            return {
                "status": "skipped_approved",
                "output_path": str(output_path),
                "message": (
                    "Arquivo já marcado como APROVADO nos metadados. "
                    "Regeneração bloqueada para proteger o arquivo e evitar consumo de cota."
                ),
                "metadata": existing_meta,
            }
        return {
            "status": "skipped_existing",
            "output_path": str(output_path),
            "message": "Arquivo existente preservado; reutilize-o ou escolha uma nova versão.",
            "metadata": existing_meta,
        }

    if get_metadata_path(output_path).exists():
        raise FileExistsError('Metadados preexistentes preservados; usar nova saída')
    authorization = reserve_generation(config, get_api_key_silently() or '')
    client = _create_client()

    annotation: Dict[str, Any] = {
        "type": "speech_metadata",
        "style": config.style,
    }
    if config.speaker:
        annotation["speaker"] = config.speaker

    speech_cfg_entry: Dict[str, Any] = {
        "voice": config.voice,
        "language": config.language,
    }
    if config.speaker:
        speech_cfg_entry["speaker"] = config.speaker

    started_at = time.perf_counter()
    try:
        # Read-only catalog check; it does not establish quota or free billing.
        catalog_model = client.models.get(model=config.model)
        if getattr(catalog_model,'name',None) not in (config.model, 'models/'+config.model):
            raise RuntimeError('Catálogo retornou outro modelo; sem substituição automática')
        interaction = client.interactions.create(
            model=config.model,
            input=[
                {
                    "type": "user_input",
                    "content": [
                        {
                            "type": "text",
                            "text": config.text,
                            "annotations": [annotation],
                        }
                    ],
                }
            ],
            response_format={
                "type": "audio",
                "mime_type": "audio/wav",
            },
            generation_config={
                "speech_config": [speech_cfg_entry],
            },
        )
    except Exception as exc:
        elapsed = round(time.perf_counter() - started_at, 3)
        err_info = _classify_api_error(exc)
        if err_info['status_code'] == 429 or 'quota' in err_info['category']:
            record_quota_block(err_info)
        return {
            "status": "error",
            "elapsed_seconds": elapsed,
            "model": config.model,
            "voice": config.voice,
            "output_path": str(output_path),
            "error": err_info,
        }

    elapsed = round(time.perf_counter() - started_at, 3)
    output_audio = getattr(interaction, "output_audio", None)
    if output_audio is None or not getattr(output_audio, "data", None):
        return {
            "status": "error",
            "elapsed_seconds": elapsed,
            "model": config.model,
            "voice": config.voice,
            "output_path": str(output_path),
            "error": {
                "category": "empty_audio_response",
                "message": (
                    f"A chamada retornou status='{getattr(interaction, 'status', None)}', "
                    "porém sem conteúdo em output_audio."
                ),
            },
        }

    raw_data = output_audio.data
    if isinstance(raw_data, str):
        decoded_bytes = base64.b64decode(raw_data)
    elif isinstance(raw_data, (bytes, bytearray)):
        # Verifica se já são bytes binários WAV ou se são bytes base64 ASCII
        if raw_data[:4] == b"RIFF":
            decoded_bytes = bytes(raw_data)
        else:
            try:
                decoded_bytes = base64.b64decode(raw_data, validate=True)
            except Exception:
                decoded_bytes = bytes(raw_data)
    else:
        decoded_bytes = bytes(raw_data)

    reported_mime = getattr(output_audio, "mime_type", None)
    reported_sr = getattr(output_audio, "sample_rate", None) or config.sample_rate
    reported_channels = getattr(output_audio, "channels", None) or 1

    wav_bytes, container_origin = _ensure_wav_bytes(
        decoded_bytes,
        mime_type=reported_mime,
        sample_rate=reported_sr,
        channels=reported_channels,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('xb') as f:
        f.write(wav_bytes)

    validation = validate_wav_file(output_path)
    usage_info = _extract_usage_metadata(interaction)

    metadata: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "approved": False,
        "api_method": "client.interactions.create",
        "sdk_version": genai.__version__,
        "interaction_id": getattr(interaction, "id", None),
        "interaction_status": str(getattr(interaction, "status", None)),
        "elapsed_seconds": elapsed,
        "model": config.model,
        "voice": config.voice,
        "voice_catalog_info": DOCUMENTED_VOICES.get(config.voice),
        "language": config.language,
        "speaker": config.speaker,
        "text": config.text,
        "speech_metadata_style": config.style,
        "output_path": str(output_path),
        "api_reported_audio": {
            "mime_type": reported_mime,
            "sample_rate": getattr(output_audio, "sample_rate", None),
            "channels": getattr(output_audio, "channels", None),
            "container_origin": container_origin,
        },
        "validation": validation,
        "usage": usage_info,
        "generation_authorization": authorization,
        "parameters": {"sample_rate_requested":config.sample_rate,"speaker":config.speaker,
            "automatic_retry":False,"synthesis_attempts":1},
        "continuity_human_approval_required": True,
    }

    meta_path = get_metadata_path(output_path)
    with meta_path.open('x',encoding='utf-8') as f:
        json.dump(metadata,f,indent=2,ensure_ascii=False)

    return {
        "status": "success" if validation.get("valid") else "invalid_wav",
        "output_path": str(output_path),
        "metadata_path": str(meta_path),
        "metadata": metadata,
    }

