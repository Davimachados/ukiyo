#!/usr/bin/env python3
"""Tema de ícones 'marys-pixel' (kawaii rosa e creme). Usa as grades do Washi SEM alterá-las, recoloridas,
e troca o lançador por uma carinha de gato e o "mostrar área de trabalho" por uma patinha.
Uso: gerar-tema-icones-marys.py PASTA_DESTINO   (cria PASTA_DESTINO/marys-pixel)
"""
import importlib.util, math, os, sys

WASHI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "washi", "tools")
def carregar(nome, arq):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(WASHI, arq))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ic = carregar("icones", "gerar-icones.py")
te = carregar("tema", "gerar-tema-icones.py")

PAL = {"k": "#5A2E3F", "w": "#FFF6EC", "p": "#F9D5DF", "r": "#D9578A", "d": "#A83A69",
       "g": "#7CC4A0", "G": "#3F8F6B", "y": "#F2C46B", "Y": "#FFE08A", "s": "#F7B8CB", "S": "#E26D96",
       "b": "#A99BD6", "B": "#7A6BB0", "m": "#D6B8C3", "c": "#FFF1DC"}

GATO = "\n".join([
    "................",
    ".k............k.",
    ".kk..........kk.",
    ".ksk........ksk.",
    ".kssk......kssk.",
    ".kcckkkkkkkkcck.",
    "kcccccccccccccck",
    "kcckkcccccckkcck",
    "kcckkcccccckkcck",
    "kccccccrrcccccck",
    "ksssccckcckcsssk",
    "kccccccckkccccck",
    ".kcccccccccccck.",
    "..kkcccccccckk..",
    "....kkkkkkkk....",
    "................"])

def patinha():
    g = [["."] * 16 for _ in range(16)]
    def bola(cx, cy, rx, ry, c):
        for y in range(16):
            for x in range(16):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1: g[y][x] = c
    for (cx, cy) in ((3.6, 6.4), (6.3, 3.6), (9.7, 3.6), (12.4, 6.4)): bola(cx, cy, 1.7, 1.9, "s")
    bola(8.0, 10.6, 4.0, 3.2, "s"); bola(7.2, 10.0, 1.4, 1.0, "p")
    out = [r[:] for r in g]
    for y in range(16):
        for x in range(16):
            if g[y][x] == "." and any(0 <= y + dy < 16 and 0 <= x + dx < 16 and g[y + dy][x + dx] != "."
                                      for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))): out[y][x] = "k"
    return "\n".join("".join(r) for r in out)

def svg(grade_txt):
    rects = []
    for y, linha in enumerate(grade_txt.strip("\n").split("\n")):
        x = 0
        while x < 16:
            c = linha[x]
            if c == ".": x += 1; continue
            x0 = x
            while x < 16 and linha[x] == c: x += 1
            rects.append(f'<rect x="{x0}" y="{y}" width="{x - x0}" height="1" fill="{PAL[c]}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" '
            'shape-rendering="crispEdges">' + "".join(rects) + "</svg>\n")

DESENHOS = dict(ic.ICONES); DESENHOS["lancador"] = GATO; DESENHOS["sakura"] = patinha()
INDEX = te.INDEX.replace("Name=Washi Pixel", "Name=Mary's Pixel") \
    .replace("Comment=Ícones pixel 16×16 do tema Washi (fallback: Breeze)", "Comment=Ícones pixel kawaii do tema Mary's (fallback: Breeze)")
assert "FollowsColorScheme=true" in INDEX

def gravar(d, nome, conteudo):
    os.makedirs(d, exist_ok=True); open(os.path.join(d, nome + ".svg"), "w").write(conteudo)

if __name__ == "__main__":
    for l in GATO.split("\n"): assert len(l) == 16, l
    raiz = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "marys-pixel"); n = 0
    for desenho, nomes in te.APPS.items():
        s = svg(DESENHOS[desenho])
        for nome in nomes: gravar(os.path.join(raiz, "apps/scalable"), nome, s); n += 1
    for chave, nomes in te.PLACES.items():
        s = svg(te.pasta(te.EMBLEMAS[chave]))
        for nome in nomes: gravar(os.path.join(raiz, "places/scalable"), nome, s); n += 1
    s = svg(te.LIXEIRA)
    for nome in ["user-trash", "user-trash-full", "trash-empty"]: gravar(os.path.join(raiz, "places/scalable"), nome, s); n += 1
    open(os.path.join(raiz, "index.theme"), "w").write(INDEX)
    print(f"{raiz}: {n} arquivos")
