#!/usr/bin/env python3
"""Touge v2 — 峠 "longa exposição": nenhum carro aparece, só o rastro de luz que eles deixaram nas curvas.
Série Ma Pixel 間 (docs/visual/filosofia-papeis-de-parede.md). Herói: a fita vermelha de lanternas traseiras
descendo os grampos; eco: a fita branca de quem sobe e a cidade no vale; silêncio: a noite e as serras.
Uso: .venv/bin/python themes/touge/tools/gerar-papel-de-parede-v2.py → wallpaper/rastro-{480x270,1920x1080}.png
"""
import os, sys
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(AQUI, "../../.."))
sys.path.insert(0, os.path.join(PROJ, "scripts"))
from pixelarte import Tela, hexrgb, perfil_montanha, ruido_valor, W, H

rng = np.random.default_rng(31)
t = Tela()

# ---- céu, via láctea, estrelas ------------------------------------------------------------------------------
t.bokashi(np.clip(t.yy / 170, 0, 1), ["#04050f", "#070a1a", "#0b1024", "#10162e", "#172038", "#1f2a44"], transicao=.3)
faixa = np.exp(-((t.yy - (20 + t.xx * 0.22)) / 22) ** 2)            # via láctea diagonal
nuvem = ruido_valor(W, H, 40, semente=4)
t.misturar(t.yy < 150, "#141a36", np.clip(faixa * (nuvem * 1.4 - 0.2), 0, 1) * 0.7)
t.misturar(t.yy < 150, "#222a4c", np.clip(faixa * (nuvem * 1.6 - 0.8), 0, 1) * 0.8)
for _ in range(260):
    x, y = int(rng.integers(0, W)), int(rng.integers(0, 150))
    p = faixa[y, x]
    if rng.random() < 0.35 + p * 0.6:
        t.px[y, x] = hexrgb(["#3a4466", "#7480a8", "#dfe6ff"][rng.choice(3, p=[.55, .33, .12])])

# ---- serras em camadas ---------------------------------------------------------------------------------------
CAMADAS = [(150, 26, 140, 1, "#1b2440"), (168, 30, 100, 2, "#141b33"), (186, 22, 70, 3, "#0f1428")]
for base, amp, esc, sem, cor in CAMADAS:
    p = perfil_montanha(W, base, amp, esc, sem)
    m = t.yy >= p[None, :]
    t.pintar(m, cor)
    t.pintar(Tela.borda_interna(m) & (t.yy == p[None, :]), "#2a3554" if sem == 1 else cor)

# cidade no vale (esquerda), sob névoa
vale = perfil_montanha(W, 214, 6, 60, 9)
for _ in range(900):
    x = int(abs(rng.normal(0, 95))); y = int(rng.normal(206, 7))
    if 0 <= x < 230 and 192 < y < vale[x]:
        t.px[y, x] = hexrgb(["#ffb35c", "#ffd98a", "#ff7a4a", "#cfe0ff"][rng.choice(4, p=[.45, .25, .15, .15])])
t.misturar((t.yy > 190) & (t.yy < 222) & (t.xx < 260), "#1f2a44", np.clip(1 - np.abs(t.yy - 206) / 18, 0, 1) * 0.45)

# ---- a montanha do passo (centro-direita) -------------------------------------------------------------------
xs = np.arange(W)
monte_y = (88 + ((xs - 330) / 130.0) ** 2 * 55 + (perfil_montanha(W, 0, 10, 40, 77) * -1)).astype(int)
monte = t.yy >= monte_y[None, :]
textura = ruido_valor(W, H, 6, semente=12, oitavas=2)
t.bokashi(np.clip((t.yy - 88) / 160 + (textura - .5) * .5, 0, 1), ["#111832", "#0d1229", "#0a0e21", "#070a18"], mask=monte, transicao=.5)
t.pintar(Tela.borda_interna(monte) & (t.yy <= monte_y[None, :] + 1), "#26304e")
# copas de pinheiro na crista
for x in range(0, W, 4):
    if monte_y[x] > 200: continue
    if rng.random() < .7:
        h = int(rng.integers(3, 8)); y0 = monte_y[x]
        for k in range(h):
            t.pintar((t.yy == y0 - k) & (np.abs(t.xx - x) <= (h - k) // 2), "#0d1229")

# ---- o traçado do passo: grampos (hairpins) ---------------------------------------------------------------
def grampo(a, b, lado, n=40):
    """semicírculo de a até b (ambos na mesma vertical ~), curvando para `lado` (-1 esq, +1 dir)."""
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; r = np.hypot(b[0] - a[0], b[1] - a[1]) / 2
    ang0 = np.arctan2(a[1] - cy, a[0] - cx)
    return [(cx + r * np.cos(ang0 - lado * np.pi * i / n) * 1.5, cy + r * np.sin(ang0 - lado * np.pi * i / n)) for i in range(n + 1)]
def reta(a, b, n=None):
    n = n or int(np.hypot(b[0] - a[0], b[1] - a[1]) * 2)
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]
P = [(468, 100), (262, 116), (262, 132), (420, 144), (420, 162), (238, 176), (238, 198), (480, 224)]
caminho = reta(P[0], P[1]) + grampo(P[1], P[2], +1) + reta(P[2], P[3]) + grampo(P[3], P[4], -1) + \
          reta(P[4], P[5]) + grampo(P[5], P[6], +1) + reta(P[6], P[7])
caminho = np.array(caminho)
# profundidade: topo = longe (fino), base = perto (grosso)
prof = np.clip((caminho[:, 1] - 96) / 130, 0, 1)

estrada = np.zeros((H, W), bool)
for (x, y), p in zip(caminho, prof):
    estrada |= t.disco(x, y, 1.2 + p * 2.6) if False else ((np.abs(t.xx - x) <= 1 + p * 2) & (np.abs(t.yy - y) <= 0.6 + p * 1.6))
t.pintar(estrada, "#161a2a")

# brilho difuso em volta dos rastros
dist = np.full((H, W), 99.0, np.float32)
for (x, y) in caminho[::3]:
    dist = np.minimum(dist, np.hypot(t.xx - x, (t.yy - y) * 1.6))
t.misturar(t.yy >= 0, "#3a1420", np.clip(1 - dist / 9, 0, 1) * 0.75)
t.misturar(t.yy >= 0, "#5a1a26", np.clip(1 - dist / 4, 0, 1) * 0.7)

def fita(desloc, cores, ini=0.0, fim=1.0):
    n = len(caminho)
    for i in range(int(n * ini), int(n * fim) - 1):
        (x0, y0), (x1, y1) = caminho[i], caminho[i + 1]
        dx, dy = x1 - x0, y1 - y0; L = np.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        p = prof[i]; off = desloc * (0.6 + p * 1.6)
        x, y = int(round(x0 + nx * off)), int(round(y0 + ny * off * 0.6))
        if 0 <= x < W and 0 <= y < H:
            t.px[y, x] = hexrgb(cores[0])
            if p > .45 and 0 <= y + 1 < H: t.px[y + 1, x] = hexrgb(cores[1])
# rastro vermelho (descendo) e branco-âmbar (subindo, só a metade de baixo)
fita(+1, ["#ff3b3b", "#c41f2c"])
fita(+2.2, ["#ff7a5a", "#ff3b3b"], 0.0, 1.0)
fita(-1, ["#fff4d6", "#ffd27a"], 0.45, 1.0)
fita(-2.2, ["#ffd27a", "#d89a40"], 0.62, 1.0)

# guard-rail com refletores (pontos) nas curvas próximas
for (x, y), p in list(zip(caminho, prof))[::9]:
    if p > .5:
        t.px[int(y + 3 + p * 2), int(x)] = hexrgb("#c9d2ea")

# ---- primeiro plano: pinheiros escuros à esquerda e guard-rail ------------------------------------------------
for x0, alt in [(-4, 120), (14, 92), (30, 140), (52, 80), (70, 104)]:
    topo = H - alt
    for k in range(alt):
        y = topo + k; larg = min(k * 0.32, 14) * (0.75 + 0.25 * np.sin(k * 0.9))
        t.pintar((t.yy == y) & (np.abs(t.xx - x0) <= larg), "#04050c")
gr = perfil_montanha(W, 252, 2, 200, 41)
t.pintar((t.yy >= gr[None, :]) & (t.xx > 60), "#05060e")
t.pintar((t.yy == gr[None, :] - 4) & (t.xx > 90), "#1c2236")
for x in range(96, W, 22):
    t.pintar((t.xx == x) & (t.yy >= gr[x] - 4) & (t.yy < gr[x] + 2), "#1c2236")
    t.px[gr[x] - 3, x] = hexrgb("#ff7a5a")

# ---- 峠道 vertical + carimbo 間 --------------------------------------------------------------------------------
m, _, alt = t.texto("峠道", 455, 18, tam=12, vertical=True, espaco=2); t.pintar(m, "#dfe6ff")
hx, hy = 452, 18 + alt + 4
t.pintar((t.xx >= hx) & (t.xx < hx + 18) & (t.yy >= hy) & (t.yy < hy + 18), "#c41f2c")
m2, _, _ = t.texto("間", hx + 3, hy + 2, tam=12); t.pintar(m2, "#fff4d6")

out = os.path.join(PROJ, "themes/touge/wallpaper/rastro")
t.salvar(out); print(out + "-1920x1080.png")
