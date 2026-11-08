"""Alinhamento por palavras com ASR local (faster-whisper) -> timing.json do EP001.

O ASR ouve o WAV real e fornece timestamps por palavra. O TEXTO exibido continua sendo o do roteiro:
as palavras reconhecidas são alinhadas (difflib) às palavras do roteiro; palavras do roteiro sem par
herdam tempo interpolado entre vizinhas e são contadas em `interpoladas`. Se a cobertura for < 85 %,
o segmento é marcado `alinhamento: falhou`.

Uso: python -m scripts.legendas.align_ep001 [--versao 1] [--modelo small]
Saída: episodios/EP001_dinheiro/legendas/_alinhamento_asr.json (bruto) e timing.json (consolidado, via montar_timing).
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
EP = ROOT / "episodios" / "EP001_dinheiro"
SEG_DIR = ROOT / "audio" / "narracoes" / "EP001" / "segmentos"


def norm(w: str) -> str:
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)


def asr_palavras(wav: Path, modelo: str):
    from faster_whisper import WhisperModel

    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    # Decodifica via FFmpeg do projeto (evita incompatibilidade do PyAV): PCM16 mono 16 kHz -> float32
    import subprocess
    import numpy as np
    from scripts.pipeline_v3.audio_finalizer import resolve_ffmpeg_binaries

    ffmpeg, _ = resolve_ffmpeg_binaries()
    raw = subprocess.run([ffmpeg, "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    segs, _ = m.transcribe(audio, language="pt", word_timestamps=True, vad_filter=False,
                           beam_size=5, condition_on_previous_text=False)
    out = []
    for s in segs:
        for w in s.words or []:
            out.append({"w": w.word.strip(), "ini": float(w.start), "fim": float(w.end)})
    return out


def alinhar(seg: dict, asr: list, dur: float) -> dict:
    ref = []  # (frase_idx, palavra)
    for fi, fr in enumerate(seg["frases"]):
        for p in fr.split():
            ref.append((fi, p))
    a = [norm(x[1]) for x in ref]
    b = [norm(x["w"]) for x in asr]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    tempos = [None] * len(ref)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                tempos[i1 + k] = (asr[j1 + k]["ini"], asr[j1 + k]["fim"])
        elif tag == "replace" and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                tempos[i1 + k] = (asr[j1 + k]["ini"], asr[j1 + k]["fim"])
    cobertura = sum(t is not None for t in tempos) / max(1, len(ref))
    interp = 0
    # interpola lacunas
    i = 0
    while i < len(tempos):
        if tempos[i] is None:
            j = i
            while j < len(tempos) and tempos[j] is None:
                j += 1
            t0 = tempos[i - 1][1] if i > 0 else (asr[0]["ini"] if asr else 0.0)
            t1 = tempos[j][0] if j < len(tempos) else (asr[-1]["fim"] if asr else dur)
            n = j - i
            for k in range(n):
                tempos[i + k] = (t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n)
                interp += 1
            i = j
        else:
            i += 1
    frases = []
    for fi, fr in enumerate(seg["frases"]):
        ws = [{"palavra": ref[k][1], "inicio_s": round(tempos[k][0], 3), "fim_s": round(tempos[k][1], 3)}
              for k in range(len(ref)) if ref[k][0] == fi]
        frases.append({"indice": fi, "texto": fr, "inicio_s": ws[0]["inicio_s"], "fim_s": ws[-1]["fim_s"], "palavras": ws})
    return {"id": seg["id"], "duracao_s": round(dur, 3), "cobertura_asr": round(cobertura, 3),
            "interpoladas": interp, "asr_texto": " ".join(x["w"] for x in asr),
            "alinhamento": "ok" if cobertura >= 0.85 else "falhou", "frases": frases}


def main() -> int:
    import wave

    ap = argparse.ArgumentParser()
    ap.add_argument("--versao", type=int, default=1)
    ap.add_argument("--modelo", default="small")
    a = ap.parse_args()
    man = json.loads((EP / "narracao.json").read_text(encoding="utf-8"))
    res = []
    for s in man["segmentos"]:
        wav = SEG_DIR / f"EP001_{s['id']}_V{a.versao}.wav"
        with wave.open(str(wav)) as w:
            dur = w.getnframes() / w.getframerate()
        r = alinhar(s, asr_palavras(wav, a.modelo), dur)
        r["wav"] = str(wav.relative_to(ROOT)).replace("\\", "/")
        print(r["id"], r["alinhamento"], "cobertura", r["cobertura_asr"], "interp", r["interpoladas"])
        print("   ASR:", r["asr_texto"])
        res.append(r)
    (EP / "legendas").mkdir(exist_ok=True)
    (EP / "legendas" / "_alinhamento_asr.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if all(r["alinhamento"] == "ok" for r in res) else 1


if __name__ == "__main__":
    raise SystemExit(main())
