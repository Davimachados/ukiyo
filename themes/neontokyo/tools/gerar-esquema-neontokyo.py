#!/usr/bin/env python3
"""Esquema de cores KDE "NeonTokyo" — cyberpunk magenta + ciano (separado dos outros temas).
Reaproveita a função de montagem do gerador do Yoru (sem alterá-lo). Imprime a tabela de contraste.
Uso: gerar-esquema-neontokyo.py SAIDA.colors
"""
import importlib.util, os, sys

YORU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "yoru", "tools", "gerar-esquema-yoru.py")
spec = importlib.util.spec_from_file_location("yoru", YORU); y = importlib.util.module_from_spec(spec); spec.loader.exec_module(y)

N = dict(
    win="#0B0D17", win2="#151A2E", view="#080A12", view2="#0B0D17", btn="#151A2E", btn2="#1E2440",
    head="#070810", head2="#0B0D17", headi="#0B0D17",
    tip="#151A2E", tip2="#1E2440", tipfg="#E6F1FF", tipfgi="#8A9BC0",
    comp="#05060C", comp2="#0B0D17", compfg="#E6F1FF",
    sel="#FF2E88", sel2="#D81B70", selfg="#0B0D17", selfgi="#2A0E1E", sellink="#05060C",
    fg="#E6F1FF", fgi="#8A9BC0", active="#00E5FF", link="#00E5FF", visited="#C38BFF",
    neg="#FF5C7A", neu="#FFE600", pos="#39FF88", focus="#00E5FF", hover="#FF2E88")

if __name__ == "__main__":
    s = y.esquema("NeonTokyo", N).replace("Name=NeonTokyo", "Name=Neon Tokyo")
    open(sys.argv[1], "w").write(s)
    c = N
    for n, a, b in [("texto / janela", c["fg"], c["win"]), ("texto / campos", c["fg"], c["view"]), ("texto / botões", c["fg"], c["btn"]),
                    ("secundário / janela", c["fgi"], c["win"]), ("seleção (texto escuro)", c["selfg"], c["sel"]),
                    ("link ciano / campos", c["link"], c["view"]), ("visitado / campos", c["visited"], c["view"]),
                    ("erro", c["neg"], c["win"]), ("aviso", c["neu"], c["win"]), ("sucesso", c["pos"], c["win"]),
                    ("foco (linha)", c["focus"], c["win"]), ("dica", c["tipfg"], c["tip"]),
                    ("desabilitado", y.mix(c["fg"], c["win"], 0.6), c["win"])]:
        r = y.cr(a, b); print(f"{n:26s} {a} / {b}  {r:5.2f}:1  {'AAA' if r >= 7 else 'AA' if r >= 4.5 else '≥3' if r >= 3 else 'FALHA'}")
