#!/usr/bin/env python3
"""Gera o tema Aurorae 'WashiPixel' (decoração de janelas pixel, sem sombra).

Moldura: 2 px sumi + 2 px de borda washi2 interna, cantos em degrau de 2 px, linha sumi sob o título.
Botões: grades 12x12 de proposta-decoracao.py desenhadas a 2x (24 px), estados sem animação.
Medidas pensadas para escala 100% (pixels exatos).

Uso: gerar-decoracao.py PASTA_DESTINO   (cria PASTA_DESTINO/WashiPixel)
"""
import importlib.util, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("prop", os.path.join(AQUI, "proposta-decoracao.py"))
prop = importlib.util.module_from_spec(spec); spec.loader.exec_module(prop)
C, glifo_base, ESTADOS, estado_close, vazio = prop.C, prop.glifo, prop.ESTADOS, prop.estado_close, prop.vazio

# ---------------- medidas (px) ----------------
BORDA = 4                 # lateral/inferior: 2 sumi + 2 washi2
T_TOPO, T_ALT, T_BASE = 2, 26, 4          # título: linha sumi + área do título + (2 washi2 + 2 sumi)
TOPO = T_TOPO + T_ALT + T_BASE            # 32
BOT = 24
T_ALT_MAX, T_BASE_MAX = 26, 4             # maximizada: sem linha de cima nem bordas laterais
TOPO_MAX = T_ALT_MAX + T_BASE_MAX         # 30

# ---------------- glifos extras ----------------
def glifo(nome, fundo, tinta):
    if nome in ("pin", "min", "max", "restore", "close"): return glifo_base(nome, fundo, tinta)
    g = vazio(fundo)
    def p(x, y): g[y][x] = tinta
    if nome == "help":
        for x in range(4, 8): p(x, 2)
        p(3, 3); p(8, 3); p(8, 4); p(7, 5); p(6, 6); p(5, 6); p(5, 7); p(5, 9); p(6, 9)
    elif nome == "above":
        for x in range(3, 9): p(x, 2)
        for i in range(4): [p(x, 4 + i) for x in range(5 - i, 7 + i)]
        for y in range(8, 10): p(5, y); p(6, y)
    elif nome == "below":
        for x in range(3, 9): p(x, 9)
        for i in range(4): [p(x, 7 - i) for x in range(5 - i, 7 + i)]
        for y in range(2, 4): p(5, y); p(6, y)
    elif nome == "shade":
        for x in range(3, 9): p(x, 3); p(x, 4)
        for i in range(3): [p(x, 6 + i) for x in range(4 + i, 8 - i)]
    return g

# ---------------- SVG ----------------
def rects(grade, ox, oy, esc, borda=None):
    out = []
    n = len(grade)
    for y, linha in enumerate(grade):
        for x, c in enumerate(linha):
            if c == ".": continue
            cor = C[borda] if (borda and c == "k" and (x in (0, n - 1) or y in (0, n - 1))) else (C[c] if c in C else c)
            out.append(f'<rect x="{ox + x * esc}" y="{oy + y * esc}" width="{esc}" height="{esc}" fill="{cor}"/>')
    return "".join(out)

def doc(w, h, corpo):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" shape-rendering="crispEdges">\n{corpo}\n</svg>\n')

def botao_svg(nome):
    partes, x = [], 0
    mapa = [("active", "normal"), ("hover", "foco"), ("pressed", "pressionado"), ("deactivated", "inativo"),
            ("inactive", "inativo"), ("hover-inactive", "foco"), ("pressed-inactive", "pressionado"),
            ("deactivated-inactive", "inativo")]
    for prefixo, est in mapa:
        fundo, tinta, borda = estado_close(est) if nome == "close" else ESTADOS[est]
        partes.append(f'<g id="{prefixo}-center">{rects(glifo(nome, fundo, tinta), x, 0, 2, borda)}</g>')
        x += BOT + 4
    return doc(x, BOT, "\n".join(partes))

# moldura: cada elemento é um retângulo de pixels; 'S' sumi/contorno, 'W' fundo do título, '.' transparente
def moldura(prefixo, contorno, fundo, ox):
    S, W = contorno, fundo
    els = {}
    tl = []
    for y in range(TOPO):
        if y < 2: tl.append([".", ".", S, S])
        elif y >= TOPO - 2: tl.append([S, S, S, S])
        else: tl.append([S, S, W, W])
    els["topleft"] = tl
    els["topright"] = [list(reversed(r)) for r in tl]
    els["top"] = [[S] if (y < 2 or y >= TOPO - 2) else [W] for y in range(TOPO)]
    els["left"] = [[S, S, W, W]]
    els["right"] = [[W, W, S, S]]
    els["center"] = [[W]]
    els["bottom"] = [[W], [W], [S], [S]]
    els["bottomleft"] = [[S, S, W, W], [S, S, W, W], [".", ".", S, S], [".", ".", S, S]]
    els["bottomright"] = [list(reversed(r)) for r in els["bottomleft"]]
    partes = []
    for nome, g in els.items():
        r = "".join(f'<rect x="{ox + x}" y="{y}" width="1" height="1" fill="{c}"/>'
                    for y, linha in enumerate(g) for x, c in enumerate(linha) if c != ".")
        partes.append(f'<g id="{prefixo}-{nome}">{r}</g>')
        ox += len(g[0]) + 3
    return partes, ox

def moldura_max(prefixo, contorno, fundo, ox):
    r = "".join(f'<rect x="{ox}" y="{y}" width="1" height="1" fill="{contorno if y >= TOPO_MAX - 2 else fundo}"/>' for y in range(TOPO_MAX))
    return [f'<g id="{prefixo}-center">{r}</g>'], ox + 4

def decoracao_svg():
    partes, ox = [], 0
    for pre, cont, fun in (("decoration", C["k"], C["p"]), ("decoration-inactive", C["m"], C["q"])):
        p, ox = moldura(pre, cont, fun, ox); partes += p
    for pre, cont, fun in (("decoration-maximized", C["k"], C["p"]), ("decoration-maximized-inactive", C["m"], C["q"])):
        p, ox = moldura_max(pre, cont, fun, ox); partes += p
    return doc(ox + 4, TOPO, "\n".join(partes))

def rgb(h): return ",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))

RC = f"""[General]
ActiveTextColor={rgb(C["k"])}
InactiveTextColor={rgb(C["s"])}
TitleAlignment=Center
TitleVerticalAlignment=Center
Animation=0
Shadow=false

[Layout]
BorderLeft={BORDA}
BorderRight={BORDA}
BorderBottom={BORDA}
TitleEdgeTop={T_TOPO}
TitleEdgeBottom={T_BASE}
TitleEdgeLeft={BORDA}
TitleEdgeRight={BORDA}
TitleBorderLeft=6
TitleBorderRight=6
TitleHeight={T_ALT}
ButtonWidth={BOT}
ButtonWidthMenu=16
ButtonHeight={BOT}
ButtonSpacing=3
ButtonMarginTop={(T_ALT - BOT) // 2}
ExplicitButtonSpacer=10
PaddingTop=0
PaddingBottom=0
PaddingLeft=0
PaddingRight=0
BorderLeftMaximized=0
BorderRightMaximized=0
BorderBottomMaximized=0
TitleEdgeTopMaximized=0
TitleEdgeBottomMaximized={T_BASE_MAX}
TitleEdgeLeftMaximized=4
TitleEdgeRightMaximized=4
ButtonMarginTopMaximized={(T_ALT_MAX - BOT) // 2}
"""

META = {"KPackageStructure": "KWin/Aurorae",
        "KPlugin": {"Id": "WashiPixel", "Name": "Washi Pixel",
                    "Description": "Decoração pixel do tema Washi (sem sombra, sem animação)",
                    "Authors": [{"Name": "Davi"}], "License": "CC-BY-SA-4.0", "Version": "1.0"}}

BOTOES = {"close": "close", "minimize": "min", "maximize": "max", "restore": "restore",
          "alldesktops": "pin", "help": "help", "keepabove": "above", "keepbelow": "below", "shade": "shade"}

if __name__ == "__main__":
    raiz = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "WashiPixel")
    os.makedirs(raiz, exist_ok=True)
    open(os.path.join(raiz, "decoration.svg"), "w").write(decoracao_svg())
    for arq, g in BOTOES.items(): open(os.path.join(raiz, arq + ".svg"), "w").write(botao_svg(g))
    open(os.path.join(raiz, "WashiPixelrc"), "w").write(RC)
    json.dump(META, open(os.path.join(raiz, "metadata.json"), "w"), ensure_ascii=False, indent=2)
    print(f"{raiz}: decoration.svg + {len(BOTOES)} botões + rc + metadata.json")
