#!/usr/bin/env python3
"""Tema de ícones 'touge-pixel' (racing: preto, branco gelo, vermelho, amarelo). Grades do Washi sem alteração,
recoloridas; lançador = volante esportivo, "mostrar área de trabalho" = bandeira quadriculada.
Uso: gerar-tema-icones-touge.py PASTA_DESTINO   (cria PASTA_DESTINO/touge-pixel)
"""
import importlib.util, math, os, sys
MT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "marys", "tools", "gerar-tema-icones-marys.py")
spec = importlib.util.spec_from_file_location("marys_ic", MT); mi = importlib.util.module_from_spec(spec); spec.loader.exec_module(mi)
mi.PAL.clear(); mi.PAL.update({"k": "#111111", "w": "#F2F2F0", "p": "#D4D4D0", "r": "#D7141E", "d": "#8E0B12",
    "g": "#1E7A3A", "G": "#14522A", "y": "#F5C400", "Y": "#FFE14D", "s": "#E8E8E4", "S": "#D7141E",
    "b": "#3A6FD0", "B": "#1F4FB0", "m": "#8C9098", "c": "#F2F2F0"})
def contornar(g):
    out = [r[:] for r in g]
    for y in range(16):
        for x in range(16):
            if g[y][x] == "." and any(0 <= y + dy < 16 and 0 <= x + dx < 16 and g[y + dy][x + dx] != "."
                                      for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))): out[y][x] = "k"
    return "\n".join("".join(r) for r in out)
def volante():
    g = [["."] * 16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if 5.3 <= math.hypot(x - 7.5, y - 7.5) <= 7.0: g[y][x] = "k"              # aro preto fino
    for x in range(3, 13):
        if g[8][x] == ".": g[8][x] = "m"                                                # raios laterais
    for y in range(9, 14):
        if g[y][7] == ".": g[y][7] = "m"
        if g[y][8] == ".": g[y][8] = "m"                                                # raio inferior
    for y in range(6, 11):
        for x in range(6, 10):
            if math.hypot(x - 7.5, y - 8.0) <= 1.7: g[y][x] = "r"                     # centro vermelho
    g[1][7] = g[1][8] = g[0][7] = g[0][8] = "y"                                         # marca amarela de centro
    return "\n".join("".join(r) for r in g)
def bandeira():
    g = [["."] * 16 for _ in range(16)]
    for y in range(1, 15): g[y][2] = "m"
    for y in range(2, 10):
        for x in range(3, 14):
            yy = y + (1 if 6 <= x <= 9 else 0)                                           # leve ondulação
            if yy < 16: g[yy][x] = "k" if ((x - 3) // 2 + (y - 2) // 2) % 2 else "w"
    return contornar(g)
mi.DESENHOS["lancador"] = volante(); mi.DESENHOS["sakura"] = bandeira()
mi.INDEX = mi.INDEX.replace("Name=Mary's Pixel", "Name=Touge Pixel").replace(
    "Comment=Ícones pixel kawaii do tema Mary's (fallback: Breeze)", "Comment=Ícones pixel racing do tema Touge (fallback: Breeze)")
if __name__ == "__main__":
    raiz = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "touge-pixel"); n = 0
    for desenho, nomes in mi.te.APPS.items():
        s = mi.svg(mi.DESENHOS[desenho])
        for nome in nomes: mi.gravar(os.path.join(raiz, "apps/scalable"), nome, s); n += 1
    for chave, nomes in mi.te.PLACES.items():
        s = mi.svg(mi.te.pasta(mi.te.EMBLEMAS[chave]))
        for nome in nomes: mi.gravar(os.path.join(raiz, "places/scalable"), nome, s); n += 1
    s = mi.svg(mi.te.LIXEIRA)
    for nome in ["user-trash", "user-trash-full", "trash-empty"]: mi.gravar(os.path.join(raiz, "places/scalable"), nome, s); n += 1
    open(os.path.join(raiz, "index.theme"), "w").write(mi.INDEX); print(f"{raiz}: {n} arquivos")
