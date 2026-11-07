#!/usr/bin/env python3
"""Mary's v2 — 眠 "móbile de berço": a gatinha dorme dentro de uma lua crescente pendurada por fios,
sob uma constelação em forma de patinha. Série Ma Pixel 間 (docs/visual/filosofia-papeis-de-parede.md).
Herói: gata + lua; eco: a patinha-constelação; silêncio: o céu rosado e as nuvens macias.
Uso: .venv/bin/python themes/marys/tools/gerar-papel-de-parede-v2.py → wallpaper/movel-{480x270,1920x1080}.png
"""
import os, sys
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(AQUI, "../../.."))
sys.path.insert(0, os.path.join(PROJ, "scripts"))
from pixelarte import Tela, hexrgb, W, H

rng = np.random.default_rng(5)
t = Tela()
LINHA = "#7a4a5a"          # contorno macio (marrom-rosado), em vez de preto

# ---- céu ----------------------------------------------------------------------------------------------------
CEU = ["#cdb7e4", "#dcc0e6", "#e9c8e4", "#f4d2e2", "#fbdde2", "#fee8e4", "#fff2e8"]
t.bokashi(np.clip(t.yy / 230, 0, 1), CEU, transicao=.28)

def brilho(x, y, tam, cor="#ffffff"):
    x, y = int(x), int(y)
    t.px[y, x] = hexrgb(cor)
    for k in range(1, tam + 1):
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            if 0 <= y + dy < H and 0 <= x + dx < W:
                t.px[y + dy, x + dx] = hexrgb(cor if k < tam else "#f7d9ea")

for _ in range(40):                       # poeira de estrelas
    x, y = rng.integers(4, W - 4), rng.integers(4, 190)
    if 215 < x < 385 and 40 < y < 175: continue
    if rng.random() < .8: t.px[y, x] = hexrgb("#ffffff" if rng.random() < .5 else "#fff3c4")
    else: brilho(x, y, 1, "#fff8e0")

# ---- constelação-patinha (canto superior esquerdo) -----------------------------------------------------------
PAD = [(98, 98), (110, 104), (122, 98), (118, 88), (102, 88)]
DEDOS = [(88, 76), (101, 66), (119, 66), (132, 76)]
def pontilhado(a, b):
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])))
    for i in range(2, n - 1, 3):
        x = round(a[0] + (b[0] - a[0]) * i / n); y = round(a[1] + (b[1] - a[1]) * i / n)
        t.px[y, x] = hexrgb("#e7a3c6")
for a, b in zip(PAD, PAD[1:] + PAD[:1]): pontilhado(a, b)
for (x, y) in PAD: brilho(x, y, 1, "#fffaf0")
for a, b in [(DEDOS[0], DEDOS[1]), (DEDOS[1], DEDOS[2]), (DEDOS[2], DEDOS[3])]: pontilhado(a, b)
for (x, y) in DEDOS: brilho(x, y, 2, "#fffaf0")

# ---- nuvens macias embaixo -----------------------------------------------------------------------------------
def nuvem(cx, cy, larg, alt, cor="#fffaf6", sombra="#f6d3df", semente=0):
    r = np.random.default_rng(semente); m = np.zeros((H, W), bool)
    n = max(3, int(larg / alt * 1.6))
    for i in range(n):
        u = i / (n - 1) if n > 1 else .5
        rr = alt * (0.55 + 0.45 * np.sin(u * np.pi)) * r.uniform(.85, 1.05)
        m |= t.disco(cx - larg / 2 + u * larg, cy - rr * .35, rr)
    m &= t.yy <= cy + alt * .25
    t.pintar(m, cor)
    som = m & (t.yy > cy - alt * .05)
    t.pintar(som, sombra)
    t.pintar(Tela.contorno(m), "#eab9cf")
    return m
nuvem(70, 236, 150, 22, semente=1); nuvem(240, 248, 190, 24, semente=2); nuvem(420, 238, 150, 21, semente=3)
nuvem(10, 258, 120, 20, semente=4); nuvem(330, 262, 200, 22, semente=5); nuvem(480, 260, 110, 20, semente=6)
t.pintar(t.yy >= 262, "#f6d3df")
nuvem(410, 150, 46, 9, semente=7); nuvem(60, 165, 40, 8, semente=8)

# ---- fios do móbile + estrelas penduradas ------------------------------------------------------------------
LX, LY, R1, R2, DY = 300, 98, 66, 64, 26      # lua: círculo externo (LX,LY,R1) menos interno (LX,LY-DY,R2)
yh = (R1 ** 2 - R2 ** 2 + (LY - DY) ** 2 - LY ** 2) / (2 * (LY - DY - LY))
xh = np.sqrt(R1 ** 2 - (yh - LY) ** 2)
CHIFRES = [(LX - xh, yh), (LX + xh, yh)]
def fio(a, b, cor="#c9a2b8"):
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
    for i in range(n + 1):
        x = int(round(a[0] + (b[0] - a[0]) * i / n)); y = int(round(a[1] + (b[1] - a[1]) * i / n))
        if 0 <= y < H and 0 <= x < W: t.px[y, x] = hexrgb(cor)
TOPO = (LX, -2)
for c in CHIFRES: fio(TOPO, (c[0], c[1] + 2))

def estrela(cx, cy, r, cor="#ffe7a3", sombra="#f6c97a"):
    pts = []
    for k in range(10):
        a = -np.pi / 2 + k * np.pi / 5; rr = r if k % 2 == 0 else r * .48
        pts.append((cx + rr * np.cos(a), cy + rr * np.sin(a)))
    m = t.mascara_poligono(pts)
    t.pintar(m, cor); t.pintar(m & (t.yy > cy + 1), sombra)
    t.pintar(Tela.contorno(m), LINHA)
    t.px[int(cy - 1), int(cx - 2)] = hexrgb("#fffaf0")
for x, comp, r in [(176, 52, 7), (206, 30, 5), (404, 40, 6), (432, 70, 8), (152, 22, 4)]:
    fio((x, -1), (x, comp - r))
    estrela(x, comp, r)

# ---- gatinha (desenhada antes da lua; a borda da lua passa na frente) --------------------------------------
PELO, PELO_S, MANCHA, MANCHA_S = "#fffaf2", "#f0dccd", "#f4b07a", "#d98b5a"
corpo = ((t.xx - 308) / 37) ** 2 + ((t.yy - 122) / 19) ** 2 <= 1
HX, HY, HR = 266, 110, 15
cabeca = t.disco(HX, HY, HR) | (((t.xx - HX) / (HR + 2)) ** 2 + ((t.yy - HY - 3) / (HR - 2)) ** 2 <= 1)
orelhaE = t.mascara_poligono([(253, 104), (255, 88), (265, 97)])
orelhaD = t.mascara_poligono([(270, 96), (281, 89), (281, 104)])
gato = corpo | cabeca | orelhaE | orelhaD
t.pintar(gato, PELO)
t.pintar(corpo & (t.yy > 126), PELO_S)                                      # sombra da barriga
mancha = corpo & (((t.xx - 326) / 16) ** 2 + ((t.yy - 112) / 10) ** 2 <= 1)
t.pintar(mancha, MANCHA); t.pintar(mancha & (t.yy > 116), MANCHA_S)
mancha_c = cabeca & (((t.xx - 274) / 8) ** 2 + ((t.yy - 99) / 7) ** 2 <= 1) | orelhaD
t.pintar(mancha_c, MANCHA)
t.pintar(t.mascara_poligono([(256, 101), (257, 92), (262, 98)]), "#f7a8b8")   # dentro da orelha
t.pintar(t.mascara_poligono([(273, 98), (279, 93), (279, 101)]), "#f7a8b8")
t.pintar(Tela.contorno(gato), LINHA)
t.pintar(Tela.borda_interna(cabeca) & corpo & (t.xx > HX + 6), LINHA)        # separa cabeça do corpo
t.pintar(Tela.borda_interna(cabeca) & corpo & (t.xx > HX + 6) & (t.yy < HY - 6), PELO)
# patinha dobrada sob o queixo
pata = ((t.xx - 280) / 6) ** 2 + ((t.yy - 125) / 3.5) ** 2 <= 1
t.pintar(pata, PELO); t.pintar(Tela.contorno(pata) & ~cabeca | (Tela.borda_interna(pata) & (t.yy > 125)), LINHA)
# rosto: olhos fechados ‿ ‿, boquinha ω, bochechas
for ex in (259, 272):
    for dx, dy in ((-2, 0), (-1, 1), (0, 1), (1, 1), (2, 0)):
        t.px[HY + 1 + dy, ex + dx] = hexrgb(LINHA)
for dx, dy in ((-2, 0), (-1, 1), (0, 0), (1, 1), (2, 0)):
    t.px[HY + 6 + dy, 266 + dx] = hexrgb(LINHA)
for bx in (255, 277):
    t.pintar((np.abs(t.xx - bx) <= 2) & (np.abs(t.yy - (HY + 5)) <= 0), "#f7a8b8")
    t.pintar((np.abs(t.xx - bx) <= 1) & (t.yy == HY + 6), "#f9c2cf")
# bigodes
for y0, x0, x1 in ((HY + 4, 247, 251), (HY + 7, 248, 252), (HY + 4, 281, 285), (HY + 7, 280, 284)):
    t.pintar((t.yy == y0) & (t.xx >= x0) & (t.xx <= x1), "#c99aa8")

# ---- lua crescente (tigela) por cima -----------------------------------------------------------------------
lua = t.disco(LX, LY, R1) & ~t.disco(LX, LY - DY, R2)
luz = np.clip(1 - np.hypot(t.xx - (LX - 30), t.yy - (LY + 40)) / 90, 0, 1)
t.bokashi(0.2 + luz * 0.8, ["#efc98f", "#f7dca6", "#fdebc2", "#fff6dc"], mask=lua, transicao=.4)
for cx, cy, r in [(262, 148, 3), (318, 154, 4), (348, 138, 2.5), (290, 158, 2)]:     # crateras
    c = t.disco(cx, cy, r) & lua
    t.pintar(c, "#f1d29b"); t.pintar(c & (t.yy < cy) & (t.xx < cx), "#e3bb80")
t.pintar(Tela.contorno(lua), LINHA)
t.pintar(Tela.borda_interna(lua) & (t.yy < LY + 30) & ~t.disco(LX, LY, R1 - 1), "#fffaf0")
# bochecha rosada na lua e brilho
t.pintar((np.abs(t.xx - 250) <= 3) & (np.abs(t.yy - 140) <= 1) & lua, "#f9c2cf")

# ---- cauda pendurada para fora, à direita ------------------------------------------------------------------
cauda = np.zeros((H, W), bool); ponta = np.zeros((H, W), bool)
pts = [(340, 120), (352, 116), (362, 118), (368, 126), (369, 138), (366, 150), (368, 160), (375, 164), (381, 160), (380, 154)]
seg = []
for a_, b_ in zip(pts, pts[1:]):
    n = 12
    for i in range(n): seg.append((a_[0] + (b_[0] - a_[0]) * i / n, a_[1] + (b_[1] - a_[1]) * i / n))
for i, (x, y) in enumerate(seg):
    u = i / len(seg); d_ = t.disco(x, y, 2.9 - u * 0.9)
    cauda |= d_
    if u > .72: ponta |= d_
t.pintar(cauda, PELO); t.pintar(ponta, MANCHA); t.pintar(cauda & (t.xx > 364) & (t.yy > 128) & ~ponta & (t.xx < 367), PELO_S)
t.pintar(Tela.contorno(cauda) & ~corpo, LINHA)

# ---- zzz -----------------------------------------------------------------------------------------------------
for (zx, zy, tam) in [(224, 66, 8), (212, 50, 10), (197, 30, 12)]:
    m, _, _ = t.texto("z", zx, zy, tam=tam); t.pintar(m, "#a487c4")

# ---- おやすみ vertical + carimbo 眠 + assinatura -------------------------------------------------------------
m, _, alt = t.texto("おやすみ", 455, 16, tam=12, vertical=True, espaco=1)
t.pintar(m, "#9b6f9e")
hx, hy = 452, 16 + alt + 4
selo = (t.xx >= hx) & (t.xx < hx + 18) & (t.yy >= hy) & (t.yy < hy + 18)
t.pintar(selo, "#ec8fae")
m2, _, _ = t.texto("眠", hx + 3, hy + 2, tam=12); t.pintar(m2, "#fff6f0")
m3, w3, _ = t.texto("Mary's", 0, 0, tam=16)
m3, _, _ = t.texto("Mary's", hx + 18 - w3, hy + 21, tam=16); t.pintar(m3, "#9b6f9e")
for dx, dy in ((0, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (1, 3)):
    t.px[hy + 29 + dy, hx + 18 - w3 - 8 + dx] = hexrgb("#ec8fae")

out = os.path.join(PROJ, "themes/marys/wallpaper/movel")
t.salvar(out); print(out + "-1920x1080.png")
