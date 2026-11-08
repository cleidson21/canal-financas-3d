"""Consolida narração do EP001: WAV completo, timing.json, SRT e ASS a partir do alinhamento medido.

Entradas : narracao.json, WAVs dos segmentos, legendas/_alinhamento_asr.json
Saídas   : audio/narracoes/EP001/EP001_NARRACAO_COMPLETA_V{n}.wav (+ .meta.json)
           episodios/EP001_dinheiro/timing.json
           episodios/EP001_dinheiro/legendas/EP001_LEGENDAS.srt / .ass
Uso      : python -m scripts.legendas.montar_ep001 [--versao 1] [--gap 0.10]
Não aplica ganho/normalização ao áudio; apenas concatena (e registra níveis para avaliar continuidade).
"""
from __future__ import annotations

import argparse
import array
import json
import math
import re
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / "episodios" / "EP001_dinheiro"
SEG_DIR = ROOT / "audio" / "narracoes" / "EP001" / "segmentos"
OUT_DIR = ROOT / "audio" / "narracoes" / "EP001"

# Legenda: caixa segura (px em 1080x1920) e limites de leitura
MAX_CHARS_LINHA = 24
MAX_LINHAS = 2
MAX_DUR_CUE = 3.6


def ler_wav(p: Path):
    with wave.open(str(p)) as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, 24000), p
        a = array.array("h")
        a.frombytes(w.readframes(w.getnframes()))
    return a


def dbfs(a: array.array) -> dict:
    n = len(a)
    rms = math.sqrt(sum(x * x for x in a) / n) / 32768
    pk = max(abs(x) for x in a) / 32768
    # RMS apenas dos trechos com fala (janelas de 50 ms acima de -45 dBFS)
    step, blocos = 1200, []
    for i in range(0, n - step, step):
        r = math.sqrt(sum(x * x for x in a[i:i + step]) / step) / 32768
        if r > 0.006:
            blocos.append(r * r)
    rms_fala = math.sqrt(sum(blocos) / len(blocos)) if blocos else 0
    f = lambda v: round(20 * math.log10(v), 2) if v > 1e-9 else -240.0
    return {"rms_dbfs": f(rms), "rms_fala_dbfs": f(rms_fala), "pico_dbfs": f(pk)}


def limpar(txt: str) -> str:
    t = txt.strip()
    t = t.replace("...", "…")
    t = re.sub(r"[.,;:]+$", "", t)  # sem ponto/vírgula final visual
    return t


def cues(frases: list[dict]) -> list[dict]:
    """Agrupa palavras em cues de até 2 linhas curtas, quebrando preferencialmente em pontuação."""
    out = []
    for fr in frases:
        pal = fr["palavras"]
        # 1) separa em blocos por pausa real entre palavras (> 0,35 s)
        blocos, atual = [], [pal[0]]
        for p in pal[1:]:
            if p["inicio_s"] - atual[-1]["fim_s"] > 0.35:
                blocos.append(atual)
                atual = []
            atual.append(p)
        blocos.append(atual)
        # 2) divide blocos longos em partes equilibradas, preferindo pontuação
        for bl in blocos:
            txt = " ".join(x["palavra"] for x in bl)
            k = max(1, math.ceil(len(txt) / 40))
            partes, resto = [], list(bl)
            for rest_k in range(k, 0, -1):
                if rest_k == 1:
                    partes.append(resto)
                    break
                total = len(" ".join(x["palavra"] for x in resto))
                alvo, acc, corte, best = total / rest_k, 0, 1, None
                for i, w in enumerate(resto[:-1], 1):
                    acc += len(w["palavra"]) + 1
                    bonus = 6 if w["palavra"][-1] in ",;:…?!" or w["palavra"].endswith("...") else 0
                    score = abs(acc - alvo) - bonus
                    if best is None or score < best:
                        best, corte = score, i
                partes.append(resto[:corte])
                resto = resto[corte:]
            for pt in partes:
                out.append({"inicio": pt[0]["inicio_s"], "fim": pt[-1]["fim_s"],
                            "palavras": [x["palavra"] for x in pt]})
    return out


def quebrar_linhas(palavras: list[str]) -> list[str]:
    txt = limpar(" ".join(palavras))
    if len(txt) <= MAX_CHARS_LINHA:
        return [txt]
    melhor, md = None, 10**9
    ws = txt.split()
    for k in range(1, len(ws)):
        a, b = " ".join(ws[:k]), " ".join(ws[k:])
        d = abs(len(a) - len(b))
        if d < md:
            melhor, md = [a, b], d
    return melhor


def ts_srt(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def ts_ass(t: float) -> str:
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Legenda,Arial,66,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,90,90,480,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--versao", type=int, default=1)
    ap.add_argument("--gap", type=float, default=0.10, help="silêncio extra entre segmentos (s)")
    a = ap.parse_args()

    man = json.loads((EP / "narracao.json").read_text(encoding="utf-8"))
    ali = {r["id"]: r for r in json.loads((EP / "legendas" / "_alinhamento_asr.json").read_text(encoding="utf-8"))}
    sr = 24000
    gap_n = int(a.gap * sr)

    track = array.array("h")
    segs_out, todas_frases = [], []
    for s in man["segmentos"]:
        r = ali[s["id"]]
        assert r["alinhamento"] == "ok", f"{s['id']} sem alinhamento confiável"
        wav = SEG_DIR / f"EP001_{s['id']}_V{a.versao}.wav"
        data = ler_wav(wav)
        off = len(track) / sr
        meta = {}
        mp = Path(str(wav) + ".meta.json")
        if mp.is_file():
            meta = json.loads(mp.read_text(encoding="utf-8"))
        niveis = dbfs(data)
        frases = []
        for fr in r["frases"]:
            f = {**fr, "inicio_s": round(fr["inicio_s"] + off, 3), "fim_s": round(fr["fim_s"] + off, 3),
                 "palavras": [{**w, "inicio_s": round(w["inicio_s"] + off, 3), "fim_s": round(w["fim_s"] + off, 3)}
                              for w in fr["palavras"]]}
            frases.append(f)
        todas_frases.extend(frases)
        segs_out.append({
            "id": s["id"], "cena": s["cena"], "wav": str(wav.relative_to(ROOT)).replace("\\", "/"),
            "texto": s["texto"], "direcao_vocal": s["direcao"],
            "modelo": man["motor"]["modelo"], "voz": man["motor"]["voz"], "idioma": man["motor"]["idioma"],
            "duracao_s": round(len(data) / sr, 3), "inicio_global_s": round(off, 3),
            "fim_global_s": round(off + len(data) / sr, 3),
            "niveis": niveis, "cobertura_asr": r["cobertura_asr"], "palavras_interpoladas": r["interpoladas"],
            "asr_texto_conferencia": r["asr_texto"],
            "tokens_api": (meta.get("usage") or {}).get("total_tokens"),
            "aprovacao": "pendente (revisão auditiva humana necessária)",
            "frases": frases,
        })
        track.extend(data)
        track.extend(array.array("h", [0]) * gap_n)

    total = len(track) / sr
    wav_out = OUT_DIR / f"EP001_NARRACAO_COMPLETA_V{a.versao}.wav"
    if wav_out.exists():
        raise SystemExit(f"Recusado: {wav_out} já existe (não sobrescrever). Use outra --versao.")
    with wave.open(str(wav_out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(track.tobytes())

    lv = [x["niveis"]["rms_fala_dbfs"] for x in segs_out]
    timing = {
        "episodio": "EP001", "fps": 30, "fonte": "WAVs reais; limites de frase e palavra via ASR local (faster-whisper) alinhado ao roteiro",
        "narracao_completa": str(wav_out.relative_to(ROOT)).replace("\\", "/"),
        "duracao_narracao_s": round(total, 3), "alvo_editorial_s": [85, 100],
        "gap_entre_segmentos_s": a.gap,
        "continuidade_niveis": {"rms_fala_dbfs_min": min(lv), "rms_fala_dbfs_max": max(lv),
                                 "spread_db": round(max(lv) - min(lv), 2)},
        "segmentos": segs_out,
    }
    (EP / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- legendas ---
    cs = cues(todas_frases)
    ant_fim = 0.0
    for i, c in enumerate(cs):
        prox = cs[i + 1]["inicio"] if i + 1 < len(cs) else total
        c["ini"] = max(ant_fim, c["inicio"] - 0.05)
        c["fim_"] = max(c["ini"] + 0.3, min(c["fim"] + 0.18, prox - 0.06))
        ant_fim = c["fim_"]
        c["linhas"] = quebrar_linhas(c["palavras"])
    srt, ass = [], [ASS_HEADER]
    for i, c in enumerate(cs, 1):
        srt.append(f"{i}\n{ts_srt(c['ini'])} --> {ts_srt(c['fim_'])}\n" + "\n".join(c["linhas"]) + "\n")
        ass.append(f"Dialogue: 0,{ts_ass(c['ini'])},{ts_ass(c['fim_'])},Legenda,,0,0,0,,{{\\fad(60,60)}}" + "\\N".join(c["linhas"]))
    (EP / "legendas" / "EP001_LEGENDAS.srt").write_text("\n".join(srt), encoding="utf-8")
    (EP / "legendas" / "EP001_LEGENDAS.ass").write_text("\n".join(ass) + "\n", encoding="utf-8-sig")
    print(f"narração completa: {total:.2f}s | cues: {len(cs)} | spread RMS fala: {max(lv)-min(lv):.2f} dB")
    for x in segs_out:
        print(x["id"], f"{x['inicio_global_s']:6.2f}-{x['fim_global_s']:6.2f}", x["niveis"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
