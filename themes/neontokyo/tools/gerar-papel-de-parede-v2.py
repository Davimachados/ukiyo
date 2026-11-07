#!/usr/bin/env python3
"""Neon Tokyo v2 — 信号 "sinal na chuva": um único letreiro vertical enorme acende a rua molhada.
Série Ma Pixel 間 (docs/visual/filosofia-papeis-de-parede.md). Herói: o letreiro; eco: o reflexo partido no
asfalto; silêncio: a cidade em névoa e a chuva em ritmo regular. Um passante de guarda-chuva dá a escala.
Uso: .venv/bin/python themes/neontokyo/tools/gerar-papel-de-parede-v2.py → wallpaper/sinal-{480x270,1920x1080}.png
"""
import os, sys
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(AQUI, "../../.."))
sys.path.insert(0, os.path.join(PROJ, "scripts"))
from pixelarte import Tela, hexrgb, perfil_montanha, W, H

rng = np.random.default_rng(23)
t = Tela()
RUA = 196                                  # linha da calçada/rua
MAG, MAG_N, MAG_G = "#ff3fa4", "#ffd6f0", "#3a1538"     # tubo, núcleo, halo
CIA, CIA_N = "#26e0f0", "#d8fbff"

# ---- céu e névoa ------------------------------------------------------------------------------------------
t.bokashi(np.clip(t.yy / RUA, 0, 1) ** 0.9, ["#06061a", "#0a0b24", "#11112e", "#1a1538", "#2a1a44", "#3a1e4c"], transicao=.3)

# ---- cidade em camadas (perspectiva atmosférica) -----------------------------------------------------------
def predios(base, hmin, hmax, larg, cor, janela, dens, semente):
    r = np.random.default_rng(semente); x = -int(r.integers(0, larg))
    m = np.zeros((H, W), bool); jan = []
    while x < W:
        lw = int(r.integers(larg // 2, larg)); topo = base - int(r.integers(hmin, hmax))
        m |= (t.xx >= x) & (t.xx < x + lw) & (t.yy >= topo) & (t.yy < base)
        if r.random() < .25:   # antena / caixa d'água
            m |= (t.xx == x + lw // 2) & (t.yy >= topo - r.integers(4, 12)) & (t.yy < topo)
        for wy in range(topo + 3, base - 2, 4):
            for wx in range(x + 2, x + lw - 2, 3):
                if r.random() < dens and 0 <= wx < W: jan.append((wy, wx, janela if r.random() < .8 else "#ffb35c"))
        x += lw + int(r.integers(0, 3))
    t.pintar(m, cor)
    for wy, wx, c in jan: t.px[wy, wx] = hexrgb(c)
    return m
far = predios(RUA - 30, 20, 70, 26, "#1c1840", "#3a3a7a", .10, 1)
# torre ao longe com luz vermelha
TX = 330
torre = t.mascara_poligono([(TX - 6, RUA - 30), (TX - 1, 40), (TX + 1, 40), (TX + 6, RUA - 30)])
t.pintar(torre, "#1c1840"); t.pintar((t.xx == TX) & (t.yy >= 28) & (t.yy < 40), "#1c1840")
t.px[27, TX] = hexrgb("#ff4a5a"); t.px[70, TX - 3] = hexrgb("#ff4a5a")
t.misturar(t.yy > 0, "#2a1a44", np.clip((t.yy - 110) / 90, 0, 1) * 0.5)         # névoa baixa
mid = predios(RUA - 6, 30, 100, 34, "#120f2a", "#2c3a78", .14, 2)
t.misturar(t.yy > 0, "#251a40", np.clip((t.yy - 150) / 60, 0, 1) * 0.35)

# ---- prédio da esquerda (perto) com o letreiro -------------------------------------------------------------
esq = (t.xx < 150) & (t.yy < RUA)
t.pintar(esq, "#0b0a18")
for y in range(14, RUA - 6, 22):                       # linhas de andar / janelas apagadas
    t.pintar((t.yy == y) & (t.xx < 150), "#141128")
    for x in range(10, 140, 16):
        if rng.random() < .3: t.pintar((t.xx >= x) & (t.xx < x + 8) & (t.yy > y + 5) & (t.yy < y + 14), "#151230")
t.pintar((t.xx == 149) & (t.yy < RUA), "#1d1838")
# prédio da direita (perto)
dir_ = (t.xx >= 410) & (t.yy < RUA)
t.pintar(dir_, "#0b0a18")
t.pintar((t.xx == 410) & (t.yy < RUA), "#1d1838")

# fios elétricos (catenárias)
for (x0, y0, x1, y1, flecha) in [(0, 36, 480, 22, 16), (0, 44, 480, 30, 18), (150, 60, 410, 54, 12)]:
    xs = np.arange(max(x0, 0), min(x1, W))
    u = (xs - x0) / (x1 - x0); ys = np.round(y0 + (y1 - y0) * u + flecha * 4 * u * (1 - u)).astype(int)
    t.px[ys, xs] = hexrgb("#05050e")

# ---- letreiro vertical: 深夜営業 ---------------------------------------------------------------------------
SX0, SY0, SW, SH_ = 104, 22, 40, 148
placa = (t.xx >= SX0) & (t.xx < SX0 + SW) & (t.yy >= SY0) & (t.yy < SY0 + SH_)
d = np.hypot(np.clip(np.abs(t.xx - (SX0 + SW / 2)) - SW / 2, 0, None), np.clip(np.abs(t.yy - (SY0 + SH_ / 2)) - SH_ / 2, 0, None))
halo = np.clip(1 - d / 46, 0, 1) ** 1.6
halo = np.clip(1 - d / 30, 0, 1)
t.misturar(~placa & (t.yy < RUA), MAG_G, np.round(halo * 3) / 3 * 0.85)
t.misturar(~placa & (t.yy < RUA), "#6a1f5c", np.clip(1 - d / 14, 0, 1) * 0.7)
t.pintar(placa, "#1a0b1e")
t.pintar(Tela.borda_interna(placa), MAG)
t.pintar(Tela.borda_interna(placa & ~Tela.borda_interna(placa)), "#7a1f5e")
# suportes
for y in (SY0 + 10, SY0 + SH_ - 12):
    t.pintar((t.yy >= y) & (t.yy < y + 2) & (t.xx >= SX0 - 6) & (t.xx < SX0), "#2a2440")
# caracteres em dobro (pixel 2×) a partir da fonte pixel 16
for i, ch in enumerate("深夜営業"):
    m16, _, _ = t.texto(ch, 0, 0, tam=16)
    glifo = m16[:17, :17]
    g2 = np.kron(glifo, np.ones((2, 2), bool))
    gx, gy = SX0 + 4, SY0 + 6 + i * 35
    m = np.zeros((H, W), bool); m[gy:gy + g2.shape[0], gx:gx + g2.shape[1]] = g2
    brilho1 = Tela.contorno(m) & placa
    t.pintar(Tela.contorno(m | brilho1) & placa, "#5a1748")
    t.pintar(brilho1, MAG)
    t.pintar(m, MAG_N)                       # núcleo claro do tubo, halo colorido em volta

# pequeno letreiro ciano à direita (rima): 喫茶
CX0, CY0 = 418, 92
pl2 = (t.xx >= CX0) & (t.xx < CX0 + 20) & (t.yy >= CY0) & (t.yy < CY0 + 38)
d2 = np.hypot(np.clip(np.abs(t.xx - (CX0 + 10)) - 10, 0, None), np.clip(np.abs(t.yy - (CY0 + 19)) - 19, 0, None))
t.misturar(~pl2 & (t.yy < RUA), "#0f3040", np.clip(1 - d2 / 22, 0, 1) * .8)
t.pintar(pl2, "#071a22"); t.pintar(Tela.borda_interna(pl2), CIA)
m, _, _ = t.texto("喫", CX0 + 2, CY0 + 2, tam=16); t.pintar(m, CIA_N)
m, _, _ = t.texto("茶", CX0 + 2, CY0 + 19, tam=16); t.pintar(m, CIA_N)

# máquina de venda (luz fria na calçada, direita)
VX0, VY0 = 430, RUA - 34
vm = (t.xx >= VX0) & (t.xx < VX0 + 22) & (t.yy >= VY0) & (t.yy < RUA)
t.misturar((np.abs(t.xx - (VX0 + 11)) < 30) & (t.yy < RUA) & (t.yy > VY0 - 14) & ~vm, "#18304a", .5)
t.pintar(vm, "#cfe8ff"); t.pintar(Tela.borda_interna(vm), "#5a7aa8")
for ry in range(VY0 + 4, VY0 + 18, 5):
    for rx in range(VX0 + 3, VX0 + 19, 4):
        t.pintar((t.yy >= ry) & (t.yy < ry + 3) & (t.xx >= rx) & (t.xx < rx + 2), ["#ff6a8a", "#46c0ff", "#ffd05a", "#7ae0a0"][(rx + ry) % 4])
t.pintar((t.yy >= VY0 + 22) & (t.yy < VY0 + 26) & (t.xx >= VX0 + 4) & (t.xx < VX0 + 18), "#2a3a5a")

# ---- rua molhada com reflexo --------------------------------------------------------------------------------
cima = t.px.copy()
for y in range(RUA, H):
    k = y - RUA
    src = RUA - 1 - int(k * 1.6)
    if src < 0: src = 0
    linha = cima[src].copy()
    if (y % 3 == 0) or rng.random() < .15: linha = linha * 0.35       # ondulação: linhas apagadas
    t.px[y] = np.roll(linha, int(rng.integers(-1, 2)), axis=0)
rua = t.yy >= RUA
t.px[rua] = t.px[rua] * np.array([0.55, 0.5, 0.7], np.float32) + np.array([6, 5, 14], np.float32)
t.pintar((t.yy == RUA) & (t.xx < 150), "#2a1e3a"); t.pintar((t.yy == RUA) & (t.xx >= 410), "#2a1e3a")
t.pintar((t.yy == RUA) & (t.xx >= 150) & (t.xx < 410), "#1d1838")
# faixa de pedestres em perspectiva (zebra), quase escondida sob o painel
for i in range(-9, 10):
    xa = 280 + i * 22; xb = 280 + i * 30
    faixa = t.mascara_poligono([(xa - 6, 236), (xa + 6, 236), (xb + 8, H), (xb - 8, H)])
    t.pintar(faixa & ((t.yy % 2 == 0) | (t.yy > 250)), "#2c2a44")

# ---- passante com guarda-chuva --------------------------------------------------------------------------------
PX, PY = 268, RUA + 2
corpo = t.mascara_poligono([(PX - 3, PY - 14), (PX + 3, PY - 14), (PX + 4, PY - 3), (PX - 4, PY - 3)])
pernas = ((t.xx == PX - 2) | (t.xx == PX + 2)) & (t.yy >= PY - 3) & (t.yy < PY)
cabeca = t.disco(PX, PY - 16, 2)
chuva_g = (t.yy <= PY - 18) & (t.yy >= PY - 26) & (((t.xx - PX) / 12) ** 2 + ((t.yy - (PY - 18)) / 8) ** 2 <= 1)
t.pintar(corpo | pernas | cabeca, "#07060f")
t.pintar(chuva_g, "#2a1a3a"); t.pintar(Tela.borda_interna(chuva_g) & (t.xx < PX), MAG)    # luz de borda do neon
t.pintar(Tela.borda_interna(chuva_g) & (t.xx >= PX) & (t.yy < PY - 22), "#5a3a6a")
t.pintar((t.xx == PX) & (t.yy > PY - 18) & (t.yy < PY - 15), "#07060f")
for y in range(PY + 1, PY + 18):                                                   # reflexo do passante
    if y % 2 == 0: t.pintar((t.yy == y) & (np.abs(t.xx - PX) <= 3 - (y - PY) // 8), "#140f22")

# ---- chuva em ritmo regular -------------------------------------------------------------------------------
gota = np.zeros((H, W), bool)
for x0 in range(-80, W, 7):
    off = int(rng.integers(0, 40)); comp = int(rng.integers(4, 8))
    for y0 in range(-20 + off, H, 38 + int(rng.integers(0, 10))):
        for k in range(comp):
            x, y = x0 + (y0 + k) // 3, y0 + k
            if 0 <= x < W and 0 <= y < H: gota[y, x] = True
perto_placa = np.clip(1 - d / 70, 0, 1)
t.misturar(gota & (t.yy < RUA), "#4a5a90", 0.75)
t.misturar(gota & (t.yy < RUA), "#ff7ac4", perto_placa)
t.misturar(gota & (t.yy >= RUA) & (t.yy % 2 == 0), "#3a4070", .5)
# respingos na rua
for _ in range(60):
    x, y = int(rng.integers(0, W)), int(rng.integers(RUA + 2, H - 4))
    t.pintar((t.yy == y) & (np.abs(t.xx - x) <= 1), "#3a3a62")

# ---- 雨夜 vertical + carimbo 間 ---------------------------------------------------------------------------
m, _, alt = t.texto("雨夜", 455, 18, tam=12, vertical=True, espaco=2); t.pintar(m, "#b8c8ff")
hx, hy = 452, 18 + alt + 4
s_ = (t.xx >= hx) & (t.xx < hx + 18) & (t.yy >= hy) & (t.yy < hy + 18)
t.pintar(s_, "#07141c"); t.pintar(Tela.borda_interna(s_), CIA)
m2, _, _ = t.texto("間", hx + 3, hy + 2, tam=12); t.pintar(m2, CIA_N)

out = os.path.join(PROJ, "themes/neontokyo/wallpaper/sinal")
t.salvar(out); print(out + "-1920x1080.png")
