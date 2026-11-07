#!/usr/bin/env python3
"""Esquema de cores KDE "Touge" (峠) — racing claro: branco gelo, preto, vermelho e amarelo de faixa.
Reaproveita a função de montagem do gerador do Yoru (sem alterá-lo). Imprime a tabela de contraste.
Uso: gerar-esquema-touge.py SAIDA.colors
"""
import importlib.util, os, sys

YORU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "yoru", "tools", "gerar-esquema-yoru.py")
spec = importlib.util.spec_from_file_location("yoru", YORU); y = importlib.util.module_from_spec(spec); spec.loader.exec_module(y)

T = dict(
    win="#F2F2F0", win2="#E4E4E1", view="#FFFFFF", view2="#F2F2F0", btn="#E4E4E1", btn2="#D4D4D0",
    head="#E4E4E1", head2="#D4D4D0", headi="#ECECEA",
    tip="#111111", tip2="#2A2A2A", tipfg="#F2F2F0", tipfgi="#B5B5B0",
    comp="#111111", comp2="#1E1E1E", compfg="#F2F2F0",
    sel="#D7141E", sel2="#B0101A", selfg="#FFFFFF", selfgi="#F5D0D2", sellink="#FFE14D",
    fg="#111111", fgi="#555555", active="#D7141E", link="#1F4FB0", visited="#6A3FA0",
    neg="#C00018", neu="#8A6A00", pos="#1E7A3A", focus="#D7141E", hover="#F5C400")

if __name__ == "__main__":
    s = y.esquema("Touge", T).replace("Name=Touge", "Name=Touge 峠")
    s = s.replace("ContrastAmount=0.6\nContrastEffect=1\nIntensityAmount=0\nIntensityEffect=0",
                  "ContrastAmount=0.45\nContrastEffect=1\nIntensityAmount=0\nIntensityEffect=0", 1)   # fundo claro
    open(sys.argv[1], "w").write(s)
    c = T
    for n, a, b in [("texto / janela", c["fg"], c["win"]), ("texto / campos", c["fg"], c["view"]), ("texto / botões", c["fg"], c["btn"]),
                    ("secundário / janela", c["fgi"], c["win"]), ("seleção", c["selfg"], c["sel"]),
                    ("link / campos", c["link"], c["view"]), ("visitado / campos", c["visited"], c["view"]),
                    ("erro", c["neg"], c["win"]), ("aviso", c["neu"], c["win"]), ("sucesso", c["pos"], c["win"]),
                    ("foco (linha)", c["focus"], c["win"]), ("dica", c["tipfg"], c["tip"]),
                    ("desabilitado", y.mix(c["fg"], c["win"], 0.45), c["win"])]:
        r = y.cr(a, b); print(f"{n:24s} {a} / {b}  {r:5.2f}:1  {'AAA' if r >= 7 else 'AA' if r >= 4.5 else '≥3' if r >= 3 else 'FALHA'}")
