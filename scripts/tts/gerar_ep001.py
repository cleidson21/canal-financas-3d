"""Geração controlada da narração do EP001 em segmentos (Gemini TTS via scripts.tts).

Uso (a partir da raiz do projeto):
    python -m scripts.tts.gerar_ep001 listar
    python -m scripts.tts.gerar_ep001 gerar --ids S01            # teste curto, 1 chamada
    python -m scripts.tts.gerar_ep001 gerar --ids S01 S02 --versao 1
    python -m scripts.tts.gerar_ep001 gerar --todos --versao 1 --confirmar

Salvaguardas: nunca sobrescreve WAV existente (uma nova tentativa exige --versao N diferente);
cada chamada à API é explícita e contada; sem --confirmar a geração completa é recusada.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.tts.config import TTSRequestConfig  # noqa: E402
from scripts.tts.generator import generate_speech  # noqa: E402

EP_DIR = ROOT / "episodios" / "EP001_dinheiro"
MANIFESTO = EP_DIR / "narracao.json"
SEG_DIR = ROOT / "audio" / "narracoes" / "EP001" / "segmentos"


def carregar() -> dict:
    return json.loads(MANIFESTO.read_text(encoding="utf-8"))


def wav_path(seg_id: str, versao: int) -> Path:
    return SEG_DIR / f"EP001_{seg_id}_V{versao}.wav"


def estilo(man: dict, seg: dict) -> str:
    return f"{man['estilo_geral']} Direção deste trecho: {seg['direcao']}"


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar")
    g = sub.add_parser("gerar")
    g.add_argument("--ids", nargs="*", default=[])
    g.add_argument("--todos", action="store_true")
    g.add_argument("--versao", type=int, default=1)
    g.add_argument("--confirmar", action="store_true", help="exigido para gerar mais de 2 segmentos")
    a = ap.parse_args()

    man = carregar()
    segs = {s["id"]: s for s in man["segmentos"]}
    if a.cmd == "listar":
        for s in man["segmentos"]:
            print(s["id"], len(s["texto"]), "chars", "|", s["texto"].splitlines()[0][:60])
        return 0

    ids = list(segs) if a.todos else a.ids
    unknown = [i for i in ids if i not in segs]
    if unknown or not ids:
        print("IDs inválidos ou ausentes:", unknown)
        return 2
    if len(ids) > 2 and not a.confirmar:
        print(f"Recusado: {len(ids)} chamadas à API. Reexecute com --confirmar.")
        return 2

    SEG_DIR.mkdir(parents=True, exist_ok=True)
    rc = 0
    for i in ids:
        s = segs[i]
        out = wav_path(i, a.versao)
        cfg = TTSRequestConfig(
            text=s["texto"],
            style=estilo(man, s),
            output_path=out,
            model=man["motor"]["modelo"],
            voice=man["motor"]["voz"],
            language=man["motor"]["idioma"],
            overwrite=False,
        )
        res = generate_speech(cfg)
        st = res.get("status")
        dur = (res.get("validation") or {}).get("duration_seconds")
        print(f"{i} -> {out.name}: {st} dur={dur}")
        if st not in ("success", "skipped_existing", "skipped_approved"):
            print(json.dumps(res, indent=2, ensure_ascii=False)[:1500])
            rc = 1
            break
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

