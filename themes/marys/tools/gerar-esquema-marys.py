#!/usr/bin/env python3
"""Esquema de cores KDE "Marys" — tema kawaii rosa e creme (separado do Washi e do Yoru).
Reaproveita a função de montagem do gerador do Yoru (sem alterá-lo). Imprime a tabela de contraste.
Uso: gerar-esquema-marys.py SAIDA.colors
"""
import importlib.util, os, sys

YORU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "yoru", "tools", "gerar-esquema-yoru.py")
spec = importlib.util.spec_from_file_location("yoru", YORU); y = importlib.util.module_from_spec(spec); spec.loader.exec_module(y)

M = dict(
    win="#FFF6EC", win2="#FBE2E8", view="#FFFBF6", view2="#FFF6EC", btn="#FBE2E8", btn2="#F6CAD6",
    head="#F9D5DF", head2="#F6CAD6", headi="#FCE9EE",
    tip="#5A2E3F", tip2="#6E3A4E", tipfg="#FFF6EC", tipfgi="#E8C8D2",
    comp="#5A2E3F", comp2="#6E3A4E", compfg="#FFF6EC",
    sel="#C2457A", sel2="#A83A69", selfg="#FFFFFF", selfgi="#F9D5DF", sellink="#FFF0B3",
    fg="#5A2E3F", fgi="#8A5A6A", active="#C2457A", link="#B23A6A", visited="#7A5AB0",
    neg="#B8283C", neu="#9A5A10", pos="#2F7F5B", focus="#CC4F80", hover="#E26D96")

if __name__ == "__main__":
    s = y.esquema("Marys", M).replace("Name=Marys", "Name=Mary's")
    # fundo claro: esmaecer 45% (60% apagaria demais o texto desabilitado)
    s = s.replace("ContrastAmount=0.6\nContrastEffect=1\nIntensityAmount=0\nIntensityEffect=0", "ContrastAmount=0.45\nContrastEffect=1\nIntensityAmount=0\nIntensityEffect=0", 1)
    open(sys.argv[1], "w").write(s)
    c = M
    for n, a, b in [("texto / janela", c["fg"], c["win"]), ("texto / campos", c["fg"], c["view"]), ("texto / botões", c["fg"], c["btn"]),
                    ("texto / barra de título", c["fg"], c["head"]), ("secundário / janela", c["fgi"], c["win"]),
                    ("seleção", c["selfg"], c["sel"]), ("link / campos", c["link"], c["view"]), ("visitado / campos", c["visited"], c["view"]),
                    ("erro", c["neg"], c["win"]), ("aviso", c["neu"], c["win"]), ("sucesso", c["pos"], c["win"]),
                    ("foco (linha, não texto)", c["focus"], c["win"]), ("dica", c["tipfg"], c["tip"]),
                    ("desabilitado", y.mix(c["fg"], c["win"], 0.45), c["win"])]:
        r = y.cr(a, b); print(f"{n:28s} {a} / {b}  {r:5.2f}:1  {'AAA' if r >= 7 else 'AA' if r >= 4.5 else '≥3' if r >= 3 else 'FALHA'}")
