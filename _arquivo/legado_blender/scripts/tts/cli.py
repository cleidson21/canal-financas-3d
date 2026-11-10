"""Interface de linha de comando (CLI) para o módulo TTS do projeto Canal Finanças 3D."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import (
    ALLOWED_MODELS,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
    DEFAULT_VOICE,
    DOCUMENTED_VOICES,
    TTSRequestConfig,
)
from .generator import generate_speech, mark_as_approved, verify_model_access
from .validator import validate_wav_file


def _cmd_check(args: argparse.Namespace) -> int:
    report = verify_model_access(model=args.model)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if (report["authentication_valid"] and report["model_listed"]) else 1


def _cmd_voices(_args: argparse.Namespace) -> int:
    print(json.dumps(DOCUMENTED_VOICES, indent=2, ensure_ascii=False))
    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    text = args.text
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8").strip()
    if not text:
        print("Erro: informe --text ou --text-file.", file=sys.stderr)
        return 1

    cfg = TTSRequestConfig(
        text=text,
        style=args.style,
        output_path=Path(args.output),
        model=args.model,
        voice=args.voice,
        language=args.language,
        speaker=args.speaker,
        overwrite=args.overwrite,
        generation_permit=Path(args.permit) if args.permit else None,
    )
    result = generate_speech(cfg)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") in ("success", "skipped_existing", "skipped_approved") else 1


def _cmd_validate(args: argparse.Namespace) -> int:
    res = validate_wav_file(args.wav_path)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0 if res.get("valid") else 1


def _cmd_approve(args: argparse.Namespace) -> int:
    meta_path = mark_as_approved(
        args.wav_path,
        approved=not args.unapprove,
        notes=args.notes or "",
    )
    print(f"Metadados atualizados em: {meta_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Utilitário de geração e validação de voz com Gemini 3.8 TTS"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="Verifica credenciais, autenticação e acesso ao modelo")
    p_check.add_argument("--model", default=DEFAULT_MODEL, choices=ALLOWED_MODELS)
    p_check.set_defaults(func=_cmd_check)

    p_voices = sub.add_parser("voices", help="Lista as vozes predefinidas documentadas")
    p_voices.set_defaults(func=_cmd_voices)

    p_gen = sub.add_parser("generate", help="Gera um arquivo WAV a partir de texto e direção vocal")
    p_gen.add_argument("--text", help="Texto literal da narração")
    p_gen.add_argument("--text-file", help="Arquivo UTF-8 contendo o texto literal da narração")
    p_gen.add_argument("--style", required=True, help="Instruções de interpretação (speech_metadata.style)")
    p_gen.add_argument("--output", required=True, help="Caminho do arquivo WAV de saída")
    p_gen.add_argument("--voice", default=DEFAULT_VOICE, help="Nome da voz predefinida (ex.: Puck, Charon, Orus)")
    p_gen.add_argument("--model", default=DEFAULT_MODEL, choices=ALLOWED_MODELS, help="Modelo TTS")
    p_gen.add_argument("--language", default=DEFAULT_LANGUAGE, help="Código de idioma (padrão: pt-BR)")
    p_gen.add_argument("--speaker", default=None, help="Identificador opcional do locutor")
    p_gen.add_argument("--overwrite", action="store_true", help="Legado: ignorado; WAVs existentes nunca são sobrescritos")
    p_gen.add_argument("--permit", help="Autorização de uso único; política remota continua bloqueada por padrão")
    p_gen.set_defaults(func=_cmd_generate)

    p_val = sub.add_parser("validate", help="Valida tecnicamente um arquivo WAV")
    p_val.add_argument("wav_path", help="Caminho do arquivo WAV")
    p_val.set_defaults(func=_cmd_validate)

    p_app = sub.add_parser("approve", help="Marca um arquivo WAV como aprovado para bloquear regeneração acidental")
    p_app.add_argument("wav_path", help="Caminho do arquivo WAV")
    p_app.add_argument("--notes", default="", help="Observações da aprovação")
    p_app.add_argument("--unapprove", action="store_true", help="Remove o bloqueio de aprovação")
    p_app.set_defaults(func=_cmd_approve)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

