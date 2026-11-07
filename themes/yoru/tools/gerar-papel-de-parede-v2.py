#!/usr/bin/env python3
"""Yoru v2 — 夜詣 "visita noturna": um túnel de mil torii que faz a curva rumo a uma luz que não se vê.
Série Ma Pixel 間 (docs/visual/filosofia-papeis-de-parede.md). Herói: a fila de portais em perspectiva;
eco: o reflexo deles na pedra molhada; silêncio: o céu entre as vigas e a curva escondida.
Uso: .venv/bin/python themes/yoru/tools/gerar-papel-de-parede-v2.py → wallpaper/senbon-{480x270,1920x1080}.png
"""
import os, sys
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(AQUI, "../../.."))
sys.path.insert(0, os.path.join(PROJ, "scripts"))
from pixelarte import Tela, hexrgb, ruido_valor, BAYER, W, H

rng = np.random.default_rng(11)
t = Tela(fundo="#0b0b1a")
VX, VY, F, CAMH, CAMX = 262, 150, 150.0, 1.0, -0.25

def xoff(z):            # a trilha curva para a direita ao longe
    return 0.0035 * max(z - 4, 0) ** 2.1

def proj(z, x, y):      # mundo → tela
    s = F / z
    return VX + s * (x + xoff(z) - CAMX), VY + s * (CAMH - y), s

# ---- céu ---------------------------------------------------------------------------------------------------
CEU = ["#07071a", "#0b0b22", "#11122e", "#1a1838", "#251d44", "#33224c"]
t.bokashi(np.clip(t.yy / VY, 0, 1) ** 1.3, CEU, transicao=.3)
for _ in range(120):
    x, y = rng.integers(0, W), rng.integers(0, VY - 30)
    t.px[y, x] = hexrgb(["#3a3f6e", "#6a6fa0", "#c8c8e8"][rng.choice(3, p=[.6, .3, .1])])
# ---- floresta (cedros) dos dois lados, silhueta ------------------------------------------------------------
for camada, (cor, base, amp, dens) in enumerate([("#121229", VY + 4, 70, 0.55), ("#0b0b1c", VY + 30, 120, 0.8)]):
    m = np.zeros((H, W), bool)
    for x0 in range(-10, W + 10, 9 if camada == 0 else 14):
        if rng.random() > dens: continue
        alt = amp * rng.uniform(.6, 1.0); topo = base - alt; larg = alt * 0.18
        m |= (t.yy >= topo) & (t.yy <= base) & (np.abs(t.xx - x0) <= (t.yy - topo) / alt * larg + 0.5)
        for k in range(4):   # ramos em camadas
            yk = topo + alt * (0.25 + 0.18 * k)
            m |= (np.abs(t.yy - yk) <= 1) & (np.abs(t.xx - x0) <= larg * (0.5 + 0.3 * k))
    m &= (t.yy <= VY + 40)
    t.pintar(m, cor)

# ---- chão --------------------------------------------------------------------------------------------------
chao = t.yy > VY
t.bokashi(np.clip((t.yy - VY) / (H - VY), 0, 1), ["#0d0b18", "#120e1e", "#171223", "#1b1427"], mask=chao, transicao=.4)

# geometria do caminho de pedra (por linha de tela: profundidade z e centro x)
zrow = np.full(H, np.inf); zrow[VY + 1:] = F * CAMH / (np.arange(VY + 1, H) - VY)
pedra = np.zeros((H, W), bool); junta = np.zeros((H, W), bool)
for y in range(VY + 1, H):
    z = zrow[y]; s = F / z
    cx = VX + s * (xoff(z) - CAMX); meia = s * 0.95
    pedra[y] = np.abs(t.xx[y] - cx) <= meia
    if y > VY + 1 and int(z * 2.2) != int(zrow[y - 1] * 2.2):      # junta transversal entre lajes
        junta[y] = pedra[y]
    # junta longitudinal (lajes alternadas)
    for k in (-0.32, 0.32):
        jx = int(round(cx + s * k + (s * 0.16 if int(z * 2.2) % 2 else 0)))
        if 0 <= jx < W: junta[y, jx] = True
t.pintar(pedra, "#211a30")
t.pintar(junta & pedra, "#141020")

# ---- torii (de longe para perto), com reflexo na pedra molhada --------------------------------------------
VERM = ["#120914", "#24101c", "#3b1422", "#5a1a28", "#7f2230", "#a52e36", "#cc4440", "#e8694a", "#f59a63"]
PRETO = ["#07060c", "#100c16", "#1a1420", "#2a1e2c", "#3c2a36"]
def luz(z):
    perto = np.exp(-(z - 1) / 6.5)
    fim = np.exp(-((z - 30) ** 2) / 40) * 0.85         # a luz escondida depois da curva
    lamp = 0.18 * (np.cos(z / 2.52 * 2 * np.pi) * .5 + .5)
    return float(np.clip(0.04 + perto * 0.85 + fim + lamp, 0, 0.8))

def portal(z, refl=False):
    L = luz(z)
    s = F / z
    pecas = []   # (máscara, paleta, brilho)
    def ret(x0, y0, x1, y1):
        X0, Y0, _ = proj(z, x0, y0); X1, Y1, _ = proj(z, x1, y1)
        if refl:
            gy = proj(z, 0, 0)[1]; Y0, Y1 = 2 * gy - Y0, 2 * gy - Y1
        return (t.xx >= min(X0, X1)) & (t.xx < max(X0, X1)) & (t.yy >= min(Y0, Y1)) & (t.yy < max(Y0, Y1))
    for lado in (-1, 1):
        xp = lado * 1.45
        pil = ret(xp - 0.17, 3.0, xp + 0.17, 0.5)
        base = ret(xp - 0.19, 0.5, xp + 0.19, 0.0)
        face = ret(xp - 0.17 * lado, 3.0, xp - 0.06 * lado, 0.5)   # lado interno (virado ao caminho) mais escuro
        pecas += [(pil, VERM, L), (face & pil, VERM, L * 0.72), (base, PRETO, L)]
    pecas.append((ret(-1.62, 2.55, 1.62, 2.40), VERM, L * 0.9))                 # nuki
    kas = ret(-1.85, 3.12, 1.85, 2.92)
    X0, Yk, _ = proj(z, -1.85, 3.12); X1, _, _ = proj(z, 1.85, 3.12)
    ponta = max(1, int(s * 0.07))
    if not refl:
        kas |= (t.yy >= Yk - ponta) & (t.yy < Yk) & ((np.abs(t.xx - X0) < s * 0.12) | (np.abs(t.xx - X1) < s * 0.12))
    pecas.append((kas, PRETO, L))
    pecas.append((ret(-1.6, 2.92, 1.6, 2.86), VERM, L * 0.8))                   # shimaki
    for m, pal, b in pecas:
        if refl:
            m = m & pedra & ((t.yy % 2) == 0) & (((t.xx + t.yy // 2) % 4) != 0)   # reflexo partido (linhas)
            b = b * 0.42
        if not m.any(): continue
        campo = np.full((H, W), np.clip(b, 0, 1), np.float32)
        if not refl:   # luz vem de baixo (lamparinas) → topo um pouco mais escuro
            gy = proj(z, 0, 0)[1]
            campo = np.clip(campo - np.clip((gy - t.yy) / (s * 3.2), 0, 1) * 0.22, 0, 1)
        t.bokashi(campo, pal, mask=m, transicao=.3)

ZS = np.arange(0.95, 38, 0.42)
for z in ZS[::-1]:
    portal(z, refl=True)
    # lamparina no pé dos pilares a cada 5 portais
    if int(round(z / 0.42)) % 6 == 0 and z > 1.4:
        for lado in (-1, 1):
            x, y, s = proj(z, lado * 1.02, 0.22)
            r = max(0.8, s * 0.09)
            poça = (np.abs(t.xx - x) < s * .35) & (np.abs(t.yy - (proj(z, 0, 0)[1])) < s * .06) & chao
            t.misturar(poça, "#4a2a2c", 0.35)
            gy0 = proj(z, 0, 0)[1]
            t.pintar((np.abs(t.xx - x) <= max(0.5, r * .45)) & (t.yy > y) & (t.yy <= gy0), "#2a1e2c")   # haste de pedra
            t.pintar((np.abs(t.xx - x) <= r * 1.3) & (np.abs(t.yy - (y - r * 1.2)) <= max(0.5, r * .25)), "#2a1e2c")  # chapéu
            t.pintar(t.disco(x, y, r), "#ffd38a")
            if r > 1.5: t.pintar(t.disco(x, y, r * .5), "#fff3cf")
    portal(z)

# brilho atrás da curva (onde a trilha some)
gx, gy, _ = proj(30, 0, 1.2)
brilho = np.exp(-(((t.xx - gx) / 26) ** 2 + ((t.yy - gy) / 14) ** 2))
t.misturar(brilho > 0.05, "#5a2e3c", brilho * 0.4)

# vaga-lumes / poeira de luz
for _ in range(18):
    x, y = int(rng.uniform(40, 440)), int(rng.uniform(60, VY + 40))
    t.px[y, x] = hexrgb("#ffd38a" if rng.random() < .5 else "#e8694a")

# ---- 夜詣 vertical + carimbo 間 -----------------------------------------------------------------------------
m, _, alt = t.texto("夜詣", 13, 18, tam=12, vertical=True, espaco=2)
t.pintar(m, "#e8d9b0")
hx, hy = 10, 18 + alt + 4
t.pintar((t.xx >= hx) & (t.xx < hx + 18) & (t.yy >= hy) & (t.yy < hy + 18), "#b52f35")
m2, _, _ = t.texto("間", hx + 3, hy + 2, tam=12); t.pintar(m2, "#f2e6c8")

out = os.path.join(PROJ, "themes/yoru/wallpaper/senbon")
t.salvar(out); print(out + "-1920x1080.png")
