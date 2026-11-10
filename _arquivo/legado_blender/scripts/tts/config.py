"""Configurações centralizadas e verificação segura de credenciais para o módulo TTS."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = PROJECT_ROOT / ".env"

# Modelos Gemini 3.8 TTS
DEFAULT_MODEL = "gemini-3.8-flash-lite-tts"
ALTERNATIVE_MODEL = "gemini-3.8-flash-tts"
ALLOWED_MODELS = (DEFAULT_MODEL, ALTERNATIVE_MODEL)

# Idioma e voz padrão
DEFAULT_LANGUAGE = "pt-BR"
DEFAULT_VOICE = "Puck"
DEFAULT_SAMPLE_RATE = 24000

# Catálogo de vozes predefinidas documentadas na API Gemini TTS
DOCUMENTED_VOICES: Dict[str, Dict[str, str]] = {
    "Puck": {
        "gender": "Masculina",
        "profile": "Jovem adulto / adulto, natural, simpática, ritmo de conversa e ótimo timing para humor leve.",
    },
    "Charon": {
        "gender": "Masculina",
        "profile": "Adulta grave, calma, informativa e explicativa.",
    },
    "Orus": {
        "gender": "Masculina",
        "profile": "Adulta médio-grave, firme, serena e articulada.",
    },
    "Fenrir": {
        "gender": "Masculina",
        "profile": "Adulta expressiva, dinâmica e energética.",
    },
    "Iapetus": {
        "gender": "Masculina",
        "profile": "Adulta clara, amigável e cotidiana.",
    },
    "Umbriel": {
        "gender": "Masculina",
        "profile": "Adulta descontraída, suave e conversacional.",
    },
    "Enceladus": {
        "gender": "Masculina",
        "profile": "Adulta suave, próxima e intimista.",
    },
    "Algenib": {
        "gender": "Masculina",
        "profile": "Adulta com textura levemente rouca e expressiva.",
    },
    "Algieba": {
        "gender": "Masculina",
        "profile": "Adulta fluida e suave.",
    },
    "Alnilam": {
        "gender": "Masculina",
        "profile": "Adulta firme e direta.",
    },
    "Schedar": {
        "gender": "Masculina",
        "profile": "Adulta equilibrada e natural.",
    },
    "Achird": {
        "gender": "Masculina",
        "profile": "Adulta amigável e acessível.",
    },
    "Aoede": {
        "gender": "Feminina",
        "profile": "Adulta leve, expressiva e natural.",
    },
    "Kore": {
        "gender": "Feminina",
        "profile": "Adulta firme, clara e articulada.",
    },
    "Zephyr": {
        "gender": "Feminina",
        "profile": "Adulta brilhante, simpática e acolhedora.",
    },
}


@dataclass
class TTSRequestConfig:
    """Parâmetros configuráveis para geração de áudio via Gemini 3.8 TTS."""

    text: str
    style: str
    output_path: Path
    model: str = DEFAULT_MODEL
    voice: str = DEFAULT_VOICE
    language: str = DEFAULT_LANGUAGE
    speaker: Optional[str] = None
    sample_rate: int = DEFAULT_SAMPLE_RATE
    overwrite: bool = False
    protect_approved: bool = True
    generation_permit: Optional[Path] = None


def sanitize_message(text: str) -> str:
    """Remove qualquer possível chave de API ou token de mensagens de erro/log."""
    if not text:
        return ""
    api_key = get_api_key_silently()
    sanitized = text
    if api_key and len(api_key) > 4:
        sanitized = sanitized.replace(api_key, "[REDACTED_API_KEY]")
    # Redige padrões típicos de chaves Google AIza...
    sanitized = re.sub(r"AIza[0-9A-Za-z\-_]{20,}", "[REDACTED_API_KEY]", sanitized)
    return sanitized


def get_api_key_silently() -> Optional[str]:
    """Obtém a chave de API da variável de ambiente ou do .env local do projeto sem expô-la."""
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key

    if ENV_FILE_PATH.is_file():
        values = dotenv_values(ENV_FILE_PATH)
        dotenv_key = (values.get("GEMINI_API_KEY") or "").strip()
        if dotenv_key and dotenv_key != "coloque_sua_chave_aqui":
            return dotenv_key

    return None


def check_credentials() -> Dict[str, object]:
    """Verifica a presença de credenciais sem imprimir ou expor o valor da chave."""
    has_env_var = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    has_dotenv_file = ENV_FILE_PATH.is_file()
    has_dotenv_key = False

    if has_dotenv_file:
        values = dotenv_values(ENV_FILE_PATH)
        raw_val = (values.get("GEMINI_API_KEY") or "").strip()
        has_dotenv_key = bool(raw_val and raw_val != "coloque_sua_chave_aqui")

    source = (
        "environment_variable"
        if has_env_var
        else ("dotenv_file" if has_dotenv_key else "none")
    )

    return {
        "configured": has_env_var or has_dotenv_key,
        "source": source,
        "has_env_var": has_env_var,
        "has_dotenv_file": has_dotenv_file,
        "has_dotenv_key": has_dotenv_key,
    }

