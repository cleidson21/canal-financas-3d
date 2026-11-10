"""Script executor da Missão TTS-0: validação do Gemini 3.8 Flash-Lite TTS e geração das narrações de teste."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.tts.config import DEFAULT_LANGUAGE, DEFAULT_MODEL, DEFAULT_VOICE, TTSRequestConfig
from scripts.tts.generator import generate_speech, verify_model_access

TEST_OUTPUT_DIR = PROJECT_ROOT / "audio" / "narracoes" / "EP001" / "testes"
SHORT_WAV_PATH = TEST_OUTPUT_DIR / "teste_acesso_flash_lite.wav"
NARRACAO_B_WAV_PATH = TEST_OUTPUT_DIR / "narracao_B_flash_lite_V1.wav"
REPORT_JSON_PATH = TEST_OUTPUT_DIR / "relatorio_missao_tts0.json"

SHORT_TEXT = "O sapato do Nico pediu demissão. E na vila dele, ninguém usava dinheiro."
SHORT_STYLE = (
    "Português brasileiro. Voz masculina adulta, natural e simpática, em ritmo de conversa. "
    "Humor observador e levemente irônico, sem estilo de locutor publicitário e sem exagerar "
    "nas emoções. Pequena pausa entre as frases."
)

NARRACAO_B_TEXT = (
    "O sapato do Nico pediu demissão.\n\n"
    "E na vila dele, ninguém usava dinheiro.\n\n"
    "Ele tinha um saco de batatas e achou que dava pra trocar por um par novo.\n\n"
    "Só que o sapateiro não queria batatas.\n\n"
    "Queria leite.\n\n"
    "Nico... aí complicou."
)

NARRACAO_B_STYLE = (
    "Narrador de um canal educativo de humor em português brasileiro. "
    "Voz masculina brasileira adulta, amigável e expressiva, parecendo uma pessoa contando "
    "uma história engraçada para um amigo. Não parecer uma aula formal, telejornal, anúncio "
    "ou propaganda. Priorize naturalidade, clareza e pausas naturais entre os parágrafos. "
    "Entonação: "
    "'O sapato do Nico pediu demissão' com humor seco e divertido; "
    "'E na vila dele, ninguém usava dinheiro' em tom de contextualização; "
    "'Ele tinha um saco de batatas e achou que dava pra trocar por um par novo' como explicação natural, sem pressa; "
    "'Só que o sapateiro não queria batatas' com mudança discreta de expectativa; "
    "'Queria leite' como revelação com ênfase; "
    "'Nico... aí complicou' com ironia leve e pausa antes da conclusão."
)


def main() -> int:
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "mission": "TTS-0",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "model": DEFAULT_MODEL,
        "voice": DEFAULT_VOICE,
        "language": DEFAULT_LANGUAGE,
        "step_1_access_check": None,
        "step_2_short_test": None,
        "step_3_narracao_b": None,
    }

    print("[1/3] Verificando credenciais, autenticação e disponibilidade do modelo...")
    access_info = verify_model_access(model=DEFAULT_MODEL)
    report["step_1_access_check"] = access_info

    if not access_info.get("authentication_valid") or not access_info.get("model_listed"):
        print("Interrompendo: falha na verificação de credenciais ou acesso ao catálogo do modelo.")
        REPORT_JSON_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1

    print("[2/3] Executando teste mínimo de geração (1 chamada curta)...")
    short_cfg = TTSRequestConfig(
        text=SHORT_TEXT,
        style=SHORT_STYLE,
        output_path=SHORT_WAV_PATH,
        model=DEFAULT_MODEL,
        voice=DEFAULT_VOICE,
        language=DEFAULT_LANGUAGE,
        overwrite=False,
    )
    short_result = generate_speech(short_cfg)
    report["step_2_short_test"] = short_result

    if short_result.get("status") not in ("success", "skipped_existing", "skipped_approved"):
        print("Interrompendo após falha no teste mínimo de geração (sem chamadas repetitivas).")
        REPORT_JSON_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1

    print("[3/3] Executando Narração B completa (1 chamada completa)...")
    narracao_b_cfg = TTSRequestConfig(
        text=NARRACAO_B_TEXT,
        style=NARRACAO_B_STYLE,
        output_path=NARRACAO_B_WAV_PATH,
        model=DEFAULT_MODEL,
        voice=DEFAULT_VOICE,
        language=DEFAULT_LANGUAGE,
        overwrite=False,
    )
    narracao_b_result = generate_speech(narracao_b_cfg)
    report["step_3_narracao_b"] = narracao_b_result

    REPORT_JSON_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Relatório técnico salvo em:", REPORT_JSON_PATH)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if narracao_b_result.get("status") in ("success", "skipped_existing", "skipped_approved") else 1


if __name__ == "__main__":
    raise SystemExit(main())

