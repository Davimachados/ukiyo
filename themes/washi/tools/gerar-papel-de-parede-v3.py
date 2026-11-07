#!/usr/bin/env python3
"""Washi v3 — 夕 "Fuji de diamante": o sol pousa exatamente no cume do Fuji ao entardecer.
Série Ma Pixel 間 (docs/visual/filosofia-papeis-de-parede.md). Herói: sol no cume; eco: o reflexo partido
no lago; silêncio: o céu em bokashi. Ramo de sakura emoldura o canto.
Uso: .venv/bin/python themes/washi/tools/gerar-papel-de-parede-v3.py  →  wallpaper/diamante-{480x270,1920x1080}.png
"""
import os, sys
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(AQUI, "../../.."))
sys.path.insert(0, os.path.join(PROJ, "scripts"))
from pixelarte import Tela, hexrgb, perfil_montanha, ruido_valor, W, H

rng = np.random.default_rng(7)
t = Tela(fundo="#1d1b3a")
HZ = 176                      # linha d'água
SX, SY, SR = 304, 64, 15      # sol (pousado no cume)

# ---- céu: bokashi vertical + calor em volta do sol --------------------------------------------------------
CEU = ["#1d1b3a", "#2c2550", "#46305f", "#6b3a6b", "#94476e", "#bd5a6c", "#dc7a66", "#ef9d63", "#f7c271", "#fbe0a0"]
ty = t.yy / HZ
d = np.hypot((t.xx - SX) * 0.55, t.yy - SY)
calor = np.clip(1 - d / 210, 0, 1) ** 1.6
nucleo = np.exp(-d / 26)
ang = np.degrees(np.arctan2(t.yy - SY, t.xx - SX))
raios = (np.cos(np.radians(ang) * 11) > 0.80) & (ang < -18) & (ang > -162) & (d > SR + 6)   # raios do sol nascente
t.bokashi(np.clip(ty ** 1.15 * 0.74 + calor * 0.36 + nucleo * 0.3 + raios * 0.07 * np.clip(1 - d / 260, 0, 1), 0, 1),
          CEU, transicao=0.3)

# nuvens longas (faixas de xilogravura), iluminadas por baixo
for cy, x0, x1, esp in [(30, 20, 230, 2), (38, 70, 300, 1), (96, 330, 470, 2), (104, 360, 452, 1), (122, 150, 262, 1)]:
    ondul = np.sin(t.xx / 23 + cy) * 0.8
    corpo = (t.yy >= cy + ondul) & (t.yy < cy + esp + ondul) & (t.xx >= x0) & (t.xx < x1)
    pontas = np.clip(np.minimum(t.xx - x0, x1 - t.xx) / 26, 0, 1)
    t.misturar(corpo, "#7a3f6e" if cy < 60 else "#a54f6c", pontas)
    luz = (t.yy >= cy + esp + ondul) & (t.yy < cy + esp + 1 + ondul) & (t.xx >= x0 + 8) & (t.xx < x1 - 8)
    t.misturar(luz, "#f2a76a" if cy > 60 else "#c96a6c", pontas * 0.9)

# estrelas tênues no alto
for _ in range(26):
    x, y = rng.integers(0, W), rng.integers(1, 26)
    if abs(x - SX) > 60: t.px[y, x] = hexrgb("#8f86b8" if rng.random() < .7 else "#d9cfe8")

# ---- sol: raios largos e suaves (só para cima), disco ------------------------------------------------------
t.pintar(t.disco(SX, SY, SR), "#fff6dc")
t.pintar(t.disco(SX, SY, SR) & ~t.disco(SX, SY, SR - 1), "#fde7a8")

# ---- revoada (V) -------------------------------------------------------------------------------------------
for i, (bx, by) in enumerate([(372, 52), (381, 57), (363, 58), (390, 63), (355, 64)]):
    for dx, dy in [(-1, -1), (0, 0), (1, -1), (-2, -1), (2, -1)]:
        t.px[by + dy, bx + dx] = hexrgb("#3a2a52")

# ---- Fuji ------------------------------------------------------------------------------------------------
xs = np.arange(W)
dx = np.maximum(np.abs(xs - SX) - 5, 0) / 150.0
fuji_y = np.where(dx < 1.25, SY + 4 + (HZ - 10 - SY - 4) * (1 - np.clip(1 - dx / 1.25, 0, 1) ** 2.1), HZ)
fuji_y = np.round(fuji_y + np.sin(xs / 7.0) * (dx > .08) * 0.6).astype(int)
fuji = (t.yy >= fuji_y[None, :]) & (t.yy < HZ)
corpo_luz = np.clip(1 - np.abs(xs - SX) / 190, 0, 1)[None, :]
t.bokashi(np.clip((t.yy - SY) / (HZ - SY), 0, 1) * 0.6 + (1 - corpo_luz) * 0.4,
          ["#5d3f78", "#4a3369", "#3a2a5a", "#2c2249"], mask=fuji, transicao=0.4)
# neve (contraluz: lavanda fria) com sulcos
dedos = np.convolve(rng.integers(0, 14, W).astype(float), np.ones(3) / 3, mode="same")
dedos = np.where(rng.random(W) < 0.35, dedos, dedos * 0.25)
neve_lim = (SY + 4 + 24 + np.sin(xs * 0.21) * 2 + dedos * np.clip(1 - np.abs(xs - SX) / 70, 0, 1)).astype(int)
neve = fuji & (t.yy < neve_lim[None, :])
t.bokashi(np.clip((t.yy - SY) / 34, 0, 1), ["#e9d9ec", "#c9b3d9", "#9f86bd"], mask=neve, transicao=.4)
t.pintar(Tela.borda_interna(fuji) & (t.yy < SY + 50) & (t.yy > SY + 2), "#ffd98f")   # luz de borda
t.pintar(Tela.borda_interna(fuji) & (t.yy >= SY + 50) & (t.yy < SY + 80), "#d88a76")

# ---- serras em perspectiva atmosférica -------------------------------------------------------------------
for base, amp, esc, sem, cor, cor_top in [(HZ - 6, 18, 110, 3, "#5a3a6e", "#7b4a78"),
                                          (HZ - 2, 13, 70, 5, "#40305e", "#5a3a6e"),
                                          (HZ + 1, 9, 45, 9, "#2a2246", "#3a2c58")]:
    p = perfil_montanha(W, base, amp, esc, sem)
    m = (t.yy >= p[None, :]) & (t.yy < HZ)
    t.pintar(m, cor)
    t.pintar(Tela.borda_interna(m) & (t.yy == p[None, :]), cor_top)
    # copas minúsculas na serra mais próxima
    if sem == 9:
        for x in range(0, W, 3):
            if rng.random() < .55: t.px[max(p[x] - 1, 0), x] = hexrgb(cor)
# pagode distante numa colina à esquerda
PX, PY = 96, HZ - 7
for i, lg in enumerate([15, 13, 11, 9, 7]):
    y = PY - i * 5
    t.pintar((t.yy == y) & (abs(t.xx - PX) <= lg // 2), "#2a2246")
    t.pintar((t.yy == y - 1) & (abs(t.xx - PX) <= lg // 2 - 2), "#2a2246")
    t.pintar((t.yy == y - 1) & (abs(t.xx - PX) == lg // 2), "#2a2246")       # beirais curvos
    t.pintar((t.yy > y - 5) & (t.yy < y - 1) & (abs(t.xx - PX) <= 2), "#2a2246")
t.pintar((t.yy >= PY - 33) & (t.yy < PY - 22) & (t.xx == PX), "#2a2246")
t.pintar((t.yy >= PY) & (t.yy < HZ) & (abs(t.xx - PX) <= 3), "#2a2246")

# ---- torii na água ----------------------------------------------------------------------------------------
TX, TB = 412, HZ + 6
def torii(dst_cor, sombra):
    m = t.mascara_desenho(lambda d: (
        d.rectangle([TX - 13, TB - 30, TX - 11, TB], fill=1), d.rectangle([TX + 11, TB - 30, TX + 13, TB], fill=1),
        d.rectangle([TX - 16, TB - 26, TX + 16, TB - 25], fill=1),
        d.rectangle([TX - 19, TB - 33, TX + 19, TB - 31], fill=1),
        d.polygon([(TX - 22, TB - 35), (TX - 19, TB - 33), (TX - 19, TB - 31)], fill=1),
        d.polygon([(TX + 22, TB - 35), (TX + 19, TB - 33), (TX + 19, TB - 31)], fill=1),
        d.rectangle([TX - 1, TB - 31, TX + 1, TB - 26], fill=1)))
    t.pintar(m, dst_cor)
    t.pintar(m & ((t.xx == TX - 11) | (t.xx == TX + 13) | (t.yy == TB - 31)), sombra)
    return m

# ---- lago: reflexo espelhado com ondulação ----------------------------------------------------------------
cima = t.px.copy()
for y in range(HZ, H):
    k = y - HZ
    src = HZ - 1 - int(k * 1.15)
    if src < 0: src = 0
    desloc = int(round(np.sin(y * 0.9) * (0.4 + k * 0.035)))
    t.px[y] = np.roll(cima[src], desloc, axis=0)
lago = t.yy >= HZ
k = np.clip((t.yy - HZ) / (H - HZ), 0, 1)[..., None]
fator = np.array([0.72, 0.68, 0.88], np.float32) * (1 - k) + np.array([0.42, 0.40, 0.66], np.float32) * k
t.px[lago] = (t.px * fator + np.array([6, 6, 18], np.float32))[lago]
for _ in range(70):   # brilhos curtos de ondulação
    y = int(rng.integers(HZ + 2, H - 10)); x = int(rng.integers(0, W - 12)); n = int(2 + (y - HZ) / 12)
    if abs(x - SX) > 26: t.px[y, x:x + n] = t.px[y, x:x + n] * 1.18
# coluna de luz do sol: traços horizontais partidos
for y in range(HZ, H - 12):
    k = (y - HZ) / (H - HZ)
    larg = int(3 + k * 26 + rng.integers(0, 4))
    if rng.random() < 0.62 - k * 0.25:
        x0 = SX - larg // 2 + rng.integers(-3, 4)
        segs = 1 if k < 0.15 else rng.integers(1, 3)
        for s in range(segs):
            a = x0 + s * (larg // segs) + rng.integers(0, 3); b = a + max(2, larg // segs - rng.integers(2, 6))
            t.px[y, max(a, 0):min(b, W)] = hexrgb("#fff2c8" if k < .25 else ("#fbd88a" if k < .55 else "#ef9d63"))
t.pintar((t.yy == HZ) & (abs(t.xx - SX) < 22), "#fbe0a0")
# torii e seu reflexo
torii("#c8343b", "#8e2335")
for y in range(TB + 1, min(TB + 36, H)):
    src = 2 * TB - y
    linha = t.px[src, TX - 23:TX + 24].copy()
    vermelho = (linha[:, 0] > 120) & (linha[:, 1] < 90) & (linha[:, 2] < 90)
    ondula = (np.arange(47) + y * 2) % 5 != 0
    t.px[y, TX - 23:TX + 24][vermelho & ondula] = hexrgb("#7a2a40")
t.pintar((t.yy == TB) & (abs(t.xx - TX) < 20), "#3a2c58")

# ---- margem em primeiro plano (escura, juncos) — fica sob o painel ---------------------------------------
mg = perfil_montanha(W, H - 6, 5, 60, 21)
margem = t.yy >= mg[None, :]
t.pintar(margem, "#15122a")
for x in list(range(0, 120, 2)) + list(range(440, W, 2)):
    if rng.random() < .6:
        h = rng.integers(4, 15) * (1.0 if x < 120 else .7)
        t.pintar((t.xx == x) & (t.yy >= mg[x] - h) & (t.yy < mg[x]), "#15122a")

# ---- ramo de sakura (canto superior esquerdo) -------------------------------------------------------------
galhos = [[(-4, 6, 4), (40, 22, 3), (88, 30, 2), (130, 26, 1)],
          [(40, 22, 2), (62, 44, 2), (78, 70, 1)],
          [(88, 30, 2), (110, 48, 1), (126, 58, 1)],
          [(-4, 40, 3), (24, 52, 2), (46, 62, 1)],
          [(20, 15, 1), (34, 4, 1)]]
flores = []
for g in galhos:
    for (x0, y0, e0), (x1, y1, e1) in zip(g, g[1:]):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2)
        for i in range(n + 1):
            u = i / n; x = x0 + (x1 - x0) * u; y = y0 + (y1 - y0) * u + np.sin(u * np.pi) * 2
            e = e0 + (e1 - e0) * u
            t.pintar(t.disco(x, y, e / 2 + .3), "#2a1a2e")
            if rng.random() < 0.035: flores.append((x, y))
    flores.append(g[-1][:2])
FLOR = ["#7e3a5c", "#c45c84", "#ee93ae", "#fbc9d6", "#fff0f3"]
for (fx, fy) in flores:
    for _ in range(rng.integers(1, 3)):
        cx, cy, r = fx + rng.normal(0, 4), fy + rng.normal(0, 3), rng.uniform(2.2, 4.2)
        m = t.disco(cx, cy, r)
        luz = np.clip(1 - np.hypot(t.xx - cx + r * .4, t.yy - cy + r * .5) / (r * 1.4), 0, 1)
        t.bokashi(0.25 + luz * 0.75, FLOR, mask=m, transicao=.5)
        t.pintar(Tela.contorno(m) & (t.yy > cy) & ~(t.px[..., 0] > 200), "#5a2a48")
# pétalas caindo em progressão (grandes/perto → pequenas/longe), ao vento da esquerda
for i in range(34):
    u = i / 34
    x = 30 + u * 260 + rng.normal(0, 14); y = 40 + u * 120 + np.sin(u * 9) * 16 + rng.normal(0, 8)
    if x > SX - 70: continue
    s = 2 if u < .35 else 1
    x, y = int(x), int(y)
    if 0 <= y < HZ - 2 and 0 <= x < W - 2:
        t.px[y:y + s, x:x + s] = hexrgb("#fbc9d6" if s == 2 else "#ee93ae")
        if s == 2: t.px[y, x] = hexrgb("#fff0f3")

# ---- 夕凪 vertical + carimbo 間 --------------------------------------------------------------------------
m, _, alt = t.texto("夕凪", 455, 18, tam=12, vertical=True, espaco=2)
t.pintar(m, "#fbe0a0")
hx, hy = 452, 18 + alt + 4
t.pintar((t.xx >= hx) & (t.xx < hx + 18) & (t.yy >= hy) & (t.yy < hy + 18), "#c8343b")
m2, _, _ = t.texto("間", hx + 3, hy + 2, tam=12)
t.pintar(m2, "#fbe0a0")

out = os.path.join(PROJ, "themes/washi/wallpaper/diamante")
t.salvar(out); print(out + "-1920x1080.png")
