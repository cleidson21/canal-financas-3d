#!/usr/bin/env python3
"""Confere se narracao.json e roteiro.md estão iguais e estima a duração.

Uso: python ferramentas/verificar_roteiro.py episodios/EP001_dinheiro
"""
import json, sys, pathlib

def main(pasta):
    pasta = pathlib.Path(pasta)
    roteiro = (pasta / "roteiro.md").read_text(encoding="utf-8")
    dados = json.loads((pasta / "narracao.json").read_text(encoding="utf-8"))
    erros, palavras = [], 0
    for seg in dados["segmentos"]:
        if seg["texto"] != "\n\n".join(seg["frases"]):
            erros.append(f'{seg["id"]}: "texto" não é a junção das "frases"')
        if seg["texto"] not in roteiro:
            erros.append(f'{seg["id"]}: texto não aparece literalmente em roteiro.md')
        palavras += len(seg["texto"].split())
    print(f"{len(dados['segmentos'])} segmentos, {palavras} palavras")
    print(f"duração estimada: {palavras/3:.0f} s a 3 p/s, {palavras/2.5:.0f} s a 2,5 p/s (a real vem dos áudios)")
    if erros:
        print("ERROS:"); [print(" -", e) for e in erros]; return 1
    print("OK: roteiro e narração conferem")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
