"""Testes das Fases A–C do EP001 (roteiro, narração, temporização, legendas). Python puro.

Uso: python testes/test_ep001_narracao.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "episodios" / "EP001_dinheiro"
falhas: list[str] = []


def ok(cond: bool, msg: str):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        falhas.append(msg)


def dur(p: Path) -> float:
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


man = json.loads((EP / "narracao.json").read_text(encoding="utf-8"))
roteiro = (EP / "roteiro.md").read_text(encoding="utf-8")
timing = json.loads((EP / "timing.json").read_text(encoding="utf-8"))

# 1. Texto narrado literal == roteiro.md (fonte única)
for s in man["segmentos"]:
    ok(s["texto"] in roteiro.replace("\r\n", "\n"), f"{s['id']}: texto idêntico ao roteiro.md")
    ok(" ".join(s["frases"]) == " ".join(s["texto"].split()), f"{s['id']}: frases reconstroem o texto")

# 2. Pergunta única e sem CTA de curtir/inscrever
narrado = " ".join(s["texto"] for s in man["segmentos"]).lower()
ok(narrado.count("?") == 5 and man["segmentos"][-1]["texto"].count("?") == 1, "S08 contém exatamente uma pergunta final")
ok(not re.search(r"curt|compartilh|inscre|no v[ií]deo de hoje|canal", narrado), "sem CTA de curtir/inscrever nem frase de abertura proibida")

# 3. WAVs reais, válidos e coerentes com timing.json
tot = 0.0
for s in timing["segmentos"]:
    p = ROOT / s["wav"]
    ok(p.is_file(), f"{s['id']}: WAV existe")
    d = dur(p)
    tot += d
    ok(abs(d - s["duracao_s"]) < 0.01, f"{s['id']}: duração do timing == duração do WAV ({d:.2f}s)")
    ok(s["niveis"]["rms_fala_dbfs"] > -30, f"{s['id']}: áudio não silencioso (RMS fala {s['niveis']['rms_fala_dbfs']} dBFS)")
    ok(s["cobertura_asr"] >= 0.85, f"{s['id']}: cobertura ASR >= 85% ({s['cobertura_asr']})")
    ok(not (ROOT / s["wav"]).with_suffix(".wav.meta.json").exists() or json.loads((ROOT / s["wav"]).with_suffix(".wav.meta.json").read_text(encoding="utf-8"))["voice"] == "Puck", f"{s['id']}: voz Puck nos metadados")
full = ROOT / timing["narracao_completa"]
ok(abs(dur(full) - timing["duracao_narracao_s"]) < 0.01, "WAV completo == duracao_narracao_s")
ok(abs(dur(full) - (tot + 0.10 * len(timing["segmentos"]))) < 0.05, "WAV completo = soma dos segmentos + gaps")

# 4. Tempos monotônicos, dentro do áudio
prev = -1.0
mono = True
for s in timing["segmentos"]:
    for f in s["frases"]:
        for w in f["palavras"]:
            if w["inicio_s"] < prev - 1e-6 or w["fim_s"] < w["inicio_s"]:
                mono = False
            prev = w["inicio_s"]
        if not (s["inicio_global_s"] <= f["inicio_s"] < f["fim_s"] <= s["fim_global_s"] + 0.01):
            mono = False
ok(mono, "palavras/frases monotônicas e dentro do segmento")

# 5. SRT: sem sobreposição, texto == roteiro (ignorando pontuação), 2 linhas no máx., ordem
srt = (EP / "legendas" / "EP001_LEGENDAS.srt").read_text(encoding="utf-8")
blocos = [b for b in srt.strip().split("\n\n") if b.strip()]


def t2s(t: str) -> float:
    h, m, r = t.split(":")
    s, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


last, sobrepoe, linhas_ok, textos = -1.0, False, True, []
for b in blocos:
    ls = b.split("\n")
    a, z = [t2s(x.strip()) for x in ls[1].split("-->")]
    if a < last - 1e-6 or z <= a:
        sobrepoe = True
    last = z
    corpo = ls[2:]
    if len(corpo) > 2 or any(len(x) > 26 for x in corpo):
        linhas_ok = False
    textos.append(" ".join(corpo))
ok(not sobrepoe, f"SRT sem sobreposição ({len(blocos)} cues)")
ok(linhas_ok, "SRT: <= 2 linhas de <= 26 caracteres")


def norm(t: str) -> list[str]:
    return re.sub(r"[^a-zà-ú0-9]", " ", t.lower()).split()


ok(norm(" ".join(textos)) == norm(" ".join(s["texto"] for s in man["segmentos"])), "SRT contém exatamente as palavras narradas")
ok(last <= timing["duracao_narracao_s"] + 0.01, "último cue termina dentro da narração")
ass = (EP / "legendas" / "EP001_LEGENDAS.ass").read_text(encoding="utf-8-sig")
ok("PlayResX: 1080" in ass and "PlayResY: 1920" in ass and ass.count("Dialogue:") == len(blocos), "ASS 1080x1920 com mesmo nº de cues")

# 6. Integridade dos ativos anteriores (manifesto SHA-256 criado na Fase A)
mf = ROOT / "backups" / "MANIFESTO_EP001_BASE_V3_1_1.json"
if mf.is_file():
    migration = ROOT / "arquivo" / "EP001" / "MIGRACAO_ESTRUTURAL_001.json"
    relocated = {}
    if migration.is_file():
        for row in json.loads(migration.read_text(encoding="utf-8"))["files"]:
            if row["action"] in {"move", "relocate_blend", "delete_duplicate"}:
                relocated[row["path"]] = row["original_archive"] or row["destination"]
    for rel, h in json.loads(mf.read_text(encoding="utf-8"))["arquivos"].items():
        original = ROOT / rel
        p = original if original.is_file() else ROOT / relocated.get(Path(rel).as_posix(), rel)
        ok(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == h, f"intacto: {rel}")
else:
    ok(False, "manifesto de integridade ausente")

print("\nRESULTADO:", "OK" if not falhas else f"{len(falhas)} FALHA(S)")
sys.exit(1 if falhas else 0)
