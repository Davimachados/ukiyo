#!/usr/bin/env python3
"""Tema de cursor 'washi-cursor' (Xcursor) gerado sem dependências.

Desenhos em grade 16x16; o contorno sumi é calculado automaticamente ao redor do preenchimento,
garantindo contraste sobre fundos claros e escuros. Tamanhos: 24 (1,5x), 32 (2x), 48 (3x), 64 (4x)
— 32/48/64 são múltiplos inteiros (pixels nítidos). Nomes ausentes caem no breeze_cursors.

Uso: gerar-cursores.py PASTA_DESTINO   (cria PASTA_DESTINO/washi-cursor/cursors + index.theme)
"""
import os, struct, sys

COR = {"w": 0xFFF2EBDD, "k": 0xFF2B2A28, "r": 0xFFC8102E, "y": 0xFFD9A441, "g": 0xFF4F6B3A}
TAM = [24, 32, 48, 64]

def grade(txt):
    l = txt.strip("\n").split("\n"); assert len(l) == 16 and all(len(x) == 16 for x in l), [len(x) for x in l]
    return [list(x) for x in l]

def contornar(g):
    """Pinta de sumi ('k') toda célula vazia vizinha (8-viz.) de uma célula preenchida."""
    out = [r[:] for r in g]
    for y in range(16):
        for x in range(16):
            if g[y][x] != ".": continue
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < 16 and 0 <= xx < 16 and g[yy][xx] not in (".", "k"):
                        out[y][x] = "k"
    return out

def de_mascara(pontos, cor="w"):
    g = [["."] * 16 for _ in range(16)]
    for (x, y) in pontos:
        if 0 <= x < 16 and 0 <= y < 16: g[y][x] = cor
    return contornar(g)

# --- desenhos manuais (já com contorno) ---
SETA = grade("""
k...............
kk..............
kwk.............
kwwk............
kwwwk...........
kwwwwk..........
kwwwwwk.........
kwwwwwwk........
kwwwwwwwk.......
kwwwwwwwwk......
kwwwwwkkkkk.....
kwwkwwk.........
kwk.kwwk........
kk..kwwk........
k....kwwk.......
.....kkk........
""")
MAO = grade("""
.....kk.........
....kwwk........
....kwwk........
....kwwk........
....kwwkkk......
....kwwkwwkkk...
....kwwkwwkwwkk.
.kk.kwwkwwkwwkwk
kwwkkwwwwwwwwkwk
kwwwkwwwwwwwwwwk
.kwwwwwwwwwwwwwk
..kwwwwwwwwwwwwk
...kwwwwwwwwwwk.
....kwwwwwwwwwk.
.....kwwwwwwwk..
.....kkkkkkkkk..
""")
PUNHO = grade("""
................
................
................
................
................
.....kkkkkkk....
....kwwkwwkwkk..
....kwwkwwkwwwk.
..kkkwwwwwwwwwk.
.kwwkwwwwwwwwwwk
.kwwwwwwwwwwwwwk
..kwwwwwwwwwwwwk
...kwwwwwwwwwwk.
....kwwwwwwwwwk.
.....kwwwwwwwk..
.....kkkkkkkkk..
""")
TEXTO = grade("""
................
.....kkk.kkk....
.....kwwkwwk....
.....kkkwkkk....
.......kwk......
.......kwk......
.......kwk......
.......kwk......
.......kwk......
.......kwk......
.......kwk......
.......kwk......
.....kkkwkkk....
.....kwwkwwk....
.....kkk.kkk....
................
""")
AMPULHETA = grade("""
................
...kkkkkkkkkk...
...kyyyyyyyyk...
....kwwwwwwk....
....kwrrrrwk....
.....kwrrwk.....
......kwwk......
.......kk.......
......kwwk......
.....kwwrwk.....
....kwwrrrwk....
....kwrrrrrk....
...kyyyyyyyyk...
...kkkkkkkkkk...
................
................
""")

def sobrepor(base, mini, ox, oy):
    g = [r[:] for r in base]
    for y, linha in enumerate(mini):
        for x, c in enumerate(linha):
            if c != "." and 0 <= oy + y < 16 and 0 <= ox + x < 16: g[oy + y][ox + x] = c
    return g

MINI_AMP = ["kkkkkk", "kyyyyk", ".kwwk.", "..kk..", ".kwrk.", "kyyyyk", "kkkkkk"]
MINI_INT = ["kkkkk.", "krrrk.", "kkkrk.", ".krkk.", ".kkk..", ".krk..", ".kkk.."]
MINI_MAIS = ["..kkk.", "..kgk.", "kkkgkk", "kgggggk"[:6], "kkkgkk", "..kgk.", "..kkk."]

def setas_duplas(eixo):
    p = set()
    for y in range(3, 13): p |= {(7, y), (8, y)}
    for i in range(4):               # pontas de seta
        for x in range(7 - i, 9 + i): p |= {(x, 2 + i), (x, 13 - i)}
    if eixo == "h": p = {(y, x) for (x, y) in p}
    return de_mascara(p)

def diagonal(inv):
    p = set()
    for i in range(4, 12): p |= {(i, i), (i + 1, i), (i, i + 1)}
    for x in range(2, 8):
        for y in range(2, 8):
            if x + y <= 9: p.add((x, y))
            if (15 - x) + (15 - y) <= 9 or (x + y <= 9 and False): pass
    for x in range(8, 14):
        for y in range(8, 14):
            if x + y >= 21: p.add((x, y))
    if inv: p = {(15 - x, y) for (x, y) in p}
    return de_mascara(p)

def mover():
    p = set()
    for y in range(2, 14): p |= {(7, y), (8, y)}
    for x in range(2, 14): p |= {(x, 7), (x, 8)}
    for i in range(3):
        for x in range(7 - i, 9 + i): p |= {(x, 1 + i), (x, 14 - i)}
        for y in range(7 - i, 9 + i): p |= {(1 + i, y), (14 - i, y)}
    return de_mascara(p)

def mira():
    p = set()
    for t in range(1, 15):
        if not 6 <= t <= 9: p |= {(7, t), (8, t), (t, 7), (t, 8)}
    return de_mascara(p)

def proibido():
    import math
    p = {}
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 4.6 <= d <= 6.6: p[(x, y)] = "r"
            elif d < 4.6: p[(x, y)] = "w"
    for i in range(3, 13):
        for (x, y) in ((i, i), (i + 1, i)):
            if math.hypot(x - 7.5, y - 7.5) < 6.6: p[(x, y)] = "r"
    g = [["."] * 16 for _ in range(16)]
    for (x, y), c in p.items(): g[y][x] = c
    return contornar(g)

# nome principal -> (grade, hotspot em pixels da grade, aliases)
CURSORES = {
    "left_ptr":   (SETA, (0, 0), ["default", "arrow", "top_left_arrow", "left_arrow", "context-menu", "right_ptr"]),
    "pointer":    (MAO, (5, 0), ["hand1", "hand2", "pointing_hand", "e29285e634086352946a0e7090d73106", "9d800788f1b08800ae810202380a0822"]),
    "openhand":   (MAO, (8, 8), ["grab", "9141b49c8149039304290b508d208c40", "5aca4d189052212118709018842178c0"]),
    "closedhand": (PUNHO, (8, 9), ["grabbing", "dnd-move", "dnd-none", "208530c400c041818281048008011002"]),
    "xterm":      (TEXTO, (8, 8), ["text", "ibeam"]),
    "watch":      (AMPULHETA, (8, 7), ["wait"]),
    "left_ptr_watch": (sobrepor(SETA, MINI_AMP, 10, 9), (0, 0), ["progress", "half-busy", "3ecb610c1bf2410f44200f48c40d3599", "00000000000000020006000e7e9ffc3f", "08e8e1c95fe2fc01f976f1e063a24ccd"]),
    "question_arrow": (sobrepor(SETA, MINI_INT, 10, 9), (0, 0), ["help", "whats_this", "left_ptr_help", "5c6cd98b3f3ebcb1f9c7f1c204630408", "d9ce0ab605698f320427677b8b9f8ecf"]),
    "copy":       (sobrepor(SETA, MINI_MAIS, 10, 9), (0, 0), ["dnd-copy", "1081e37283d90000800003c07f3ef6bf", "6407b0e94181790501fd1e167b474872"]),
    "crosshair":  (mira(), (8, 8), ["cross", "tcross", "cell", "plus"]),
    "fleur":      (mover(), (8, 8), ["move", "all-scroll", "size_all"]),
    "not-allowed": (proibido(), (8, 8), ["no-drop", "forbidden", "circle", "crossed_circle", "03b6e0fcb3499374a867c041f52298f0"]),
    "ns-resize":  (setas_duplas("v"), (8, 8), ["n-resize", "s-resize", "size_ver", "sb_v_double_arrow", "v_double_arrow", "row-resize", "split_v", "top_side", "bottom_side", "00008160000006810000408080010102"]),
    "ew-resize":  (setas_duplas("h"), (8, 8), ["e-resize", "w-resize", "size_hor", "sb_h_double_arrow", "h_double_arrow", "col-resize", "split_h", "left_side", "right_side", "028006030e0e7ebffc7f7070c0600140"]),
    "nwse-resize": (diagonal(False), (8, 8), ["nw-resize", "se-resize", "size_fdiag", "bd_double_arrow", "top_left_corner", "bottom_right_corner", "c7088f0f3e6c8088236ef8e1e3e70000"]),
    "nesw-resize": (diagonal(True), (8, 8), ["ne-resize", "sw-resize", "size_bdiag", "fd_double_arrow", "top_right_corner", "bottom_left_corner", "fcf1c3c7cd4491d801f1e1c78f100000"]),
}

def imagem(g, tam):
    esc = tam / 16; px = []
    for y in range(tam):
        for x in range(tam):
            c = g[min(15, int(y / esc))][min(15, int(x / esc))]
            px.append(0 if c == "." else COR[c])
    return px

def xcursor(g, hot):
    imgs = []
    for t in TAM:
        esc = t / 16
        hx, hy = min(t - 1, int(hot[0] * esc)), min(t - 1, int(hot[1] * esc))
        imgs.append((t, hx, hy, imagem(g, t)))
    ntoc = len(imgs); pos = 16 + ntoc * 12
    cab = struct.pack("<4sIII", b"Xcur", 16, 0x10000, ntoc); toc = b""; corpo = b""
    for (t, hx, hy, px) in imgs:
        toc += struct.pack("<III", 0xFFFD0002, t, pos + len(corpo))
        corpo += struct.pack("<IIIIIIIII", 36, 0xFFFD0002, t, 1, t, t, hx, hy, 0) + struct.pack(f"<{len(px)}I", *px)
    return cab + toc + corpo

if __name__ == "__main__":
    raiz = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "washi-cursor")
    cur = os.path.join(raiz, "cursors"); os.makedirs(cur, exist_ok=True)
    n = 0
    for nome, (g, hot, aliases) in CURSORES.items():
        with open(os.path.join(cur, nome), "wb") as f: f.write(xcursor(g, hot))
        for a in aliases:
            dst = os.path.join(cur, a)
            if os.path.lexists(dst): os.remove(dst)
            os.symlink(nome, dst); n += 1
    with open(os.path.join(raiz, "index.theme"), "w") as f:
        f.write("[Icon Theme]\nName=Washi Cursor\nComment=Cursor pixel do tema Washi (fallback: Breeze)\nInherits=breeze_cursors\n")
    print(f"{len(CURSORES)} cursores + {n} aliases em {cur}")
