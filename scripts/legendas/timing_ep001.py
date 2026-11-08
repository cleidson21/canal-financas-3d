"""Análise temporal dos WAVs do EP001: pausas medidas -> frases -> timing.json.

Método (sem inventar timestamps):
 1. Calcula o envelope RMS (janelas de 10 ms) de cada WAV real.
 2. Detecta silêncios internos >= --pausa-min (padrão 0,22 s) abaixo de um limiar relativo ao nível de fala.
 3. Cada segmento tem N frases; N-1 pausas MAIS LONGAS dentro da fala delimitam as frases. As pausas entre
    sentenças separadas por linha em branco são as maiores; se a contagem de pausas candidatas for menor que
    N-1, o segmento é marcado `alinhamento: "falhou"`.
 4. Palavras: tempos distribuídos dentro da frase proporcionalmente ao nº de sílabas estimado
    (marcado `precisao_palavra: "estimada"`). Os limites de frase são MEDIDOS; os de palavra, não.

Uso: python -m scripts.legendas.timing_ep001 [--versao 1]
"""
from __future__ import annotations

import argparse
import array
import json
import re
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EP = ROOT / "episodios" / "EP001_dinheiro"
SEG_DIR = ROOT / "audio" / "narracoes" / "EP001" / "segmentos"
JANELA = 0.010


def envelope(path: Path):
    with wave.open(str(path), "rb") as w:
        sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
        assert sw == 2 and ch == 1, "esperado PCM16 mono"
        data = array.array("h")
        data.frombytes(w.readframes(n))
    step = int(sr * JANELA)
    env = []
    for i in range(0, len(data) - step + 1, step):
        blk = data[i : i + step]
        env.append((sum(x * x for x in blk) / step) ** 0.5 / 32768.0)
    return env, len(data) / sr


def silencios(env, limiar):
    res, ini = [], None
    for i, v in enumerate(env):
        if v < limiar and ini is None:
            ini = i
        elif v >= limiar and ini is not None:
            res.append((ini * JANELA, i * JANELA))
            ini = None
    if ini is not None:
        res.append((ini * JANELA, len(env) * JANELA))
    return res


def silabas(p: str) -> int:
    return max(1, len(re.findall(r"[aeiouáéíóúâêôãõàü]+", p.lower())))


def analisar(seg: dict, wav: Path, pausa_min: float) -> dict:
    env, dur = envelope(wav)
    ordenado = sorted(env)
    fala = ordenado[int(len(env) * 0.9)]
    limiar = max(0.004, fala * 0.06)
    sil = silencios(env, limiar)
    ini = sil[0][1] if sil and sil[0][0] < 0.01 else 0.0
    fim = sil[-1][0] if sil and sil[-1][1] >= dur - 0.02 else dur
    internos = [(a, b) for a, b in sil if a > ini + 0.05 and b < fim - 0.05 and (b - a) >= pausa_min]
    frases = seg["frases"]
    need = len(frases) - 1
    out = {"id": seg["id"], "wav": str(wav.relative_to(ROOT)).replace("\\", "/"), "duracao_s": round(dur, 3),
           "fala_inicio_s": round(ini, 3), "fala_fim_s": round(fim, 3), "limiar_rms": round(limiar, 5),
           "pausas_internas": [[round(a, 3), round(b, 3)] for a, b in internos], "frases": []}
    if len(internos) < need:
        out["alinhamento"] = "falhou"
        out["motivo"] = f"{len(internos)} pausas detectadas, {need} necessárias"
        return out
    # as `need` maiores pausas delimitam as frases
    cortes = sorted(sorted(internos, key=lambda p: p[1] - p[0], reverse=True)[:need])
    limites = [ini] + [(a, b) for a, b in cortes] + [fim]
    t0 = ini
    for k, txt in enumerate(frases):
        if k < need:
            a, b = cortes[k]
            t1 = a
            prox = b
        else:
            t1 = fim
            prox = None
        palavras = txt.split()
        pesos = [silabas(p) for p in palavras]
        tot = sum(pesos)
        ts, ws = t0, []
        for p, pw in zip(palavras, pesos):
            d = (t1 - t0) * pw / tot
            ws.append({"palavra": p, "inicio_s": round(ts, 3), "fim_s": round(ts + d, 3)})
            ts += d
        out["frases"].append({"indice": k, "texto": txt, "inicio_s": round(t0, 3), "fim_s": round(t1, 3),
                              "palavras": ws, "precisao_frase": "medida", "precisao_palavra": "estimada"})
        if prox is not None:
            t0 = prox
    out["alinhamento"] = "ok"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--versao", type=int, default=1)
    ap.add_argument("--pausa-min", type=float, default=0.22)
    a = ap.parse_args()
    man = json.loads((EP / "narracao.json").read_text(encoding="utf-8"))
    res = [analisar(s, SEG_DIR / f"EP001_{s['id']}_V{a.versao}.wav", a.pausa_min) for s in man["segmentos"]
           if (SEG_DIR / f"EP001_{s['id']}_V{a.versao}.wav").is_file()]
    print(json.dumps([{k: r[k] for k in ("id", "duracao_s", "alinhamento", "fala_inicio_s", "fala_fim_s")}
                      | {"pausas": r["pausas_internas"]} for r in res], ensure_ascii=False, indent=1))
    (EP / "legendas").mkdir(exist_ok=True)
    (EP / "legendas" / "_analise_pausas.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if all(r["alinhamento"] == "ok" for r in res) else 1


if __name__ == "__main__":
    raise SystemExit(main())

