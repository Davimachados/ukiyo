#!/usr/bin/env python3
"""Papel de parede "Entardecer Washi" — pixel art gerada por código (sem dependências).

Desenha em 480x270 (pixels "de verdade") e amplia por vizinho mais próximo (x4 = 1920x1080),
mantendo os pixels nítidos. Determinístico: mesma saída a cada execução.

Uso: gerar-papel-de-parede.py SAIDA.png [escala]
"""
import math, random, struct, sys, zlib

W, H = 480, 270
HORIZ = 170          # linha do horizonte / superfície do lago
SHORE = 236          # início da margem em primeiro plano
rnd = random.Random(1335)

def hx(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))

P = {k: hx(v) for k, v in {
    "ceu0": "#4A3358", "ceu1": "#7A4366", "ceu2": "#B8586A", "ceu3": "#E0805E",
    "ceu4": "#F0A95E", "ceu5": "#F6CF84", "ceu6": "#F9E3A6",
    "sol": "#FFF1C4", "sol2": "#FCE09A",
    "nuvem": "#F2B48A", "nuvem2": "#C9707A", "nuvem3": "#8E4F6E",
    "mont_l": "#5F4A70", "mont_r": "#836582", "neve_l": "#D8C3D3", "neve_r": "#FBEFE3",
    "colina": "#4A3B5A", "colina2": "#3A3049",
    "torii": "#C8102E", "torii_s": "#8E0B22", "sumi": "#2B2A28",
    "terra": "#2F3326", "musgo": "#6B8E4E", "musgo2": "#4F6B3A", "pedra": "#8C857A", "pedra2": "#5E5850",
    "lanterna": "#FFC857", "lanterna2": "#FFE7A8",
    "tronco": "#3A2A26", "tronco2": "#5A4038",
    "sak0": "#FFD6E0", "sak1": "#F4A7B9", "sak2": "#E07A97", "sak3": "#B5566F",
    "agua": "#3B3550",
}.items()}

img = [[P["ceu0"]] * W for _ in range(H)]

def px(x, y, c):
    if 0 <= x < W and 0 <= y < H: img[y][x] = c

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

def mix(a, b, t): return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

# --- céu em faixas com pontilhado ordenado (dithering 8-bit) ---
bands = [P[f"ceu{i}"] for i in range(7)]
for y in range(HORIZ):
    t = (y / (HORIZ - 1)) ** 0.85 * (len(bands) - 1)
    i = min(int(t), len(bands) - 2); f = t - i
    for x in range(W):
        img[y][x] = bands[i + 1] if f * 16 > BAYER[y % 4][x % 4] + 0.5 else bands[i]

# --- sol baixo, à direita da montanha ---
SX, SY, SR = 330, 146, 21
for y in range(SY - SR - 6, SY + SR + 6):
    for x in range(SX - SR - 6, SX + SR + 6):
        d = math.hypot(x - SX, y - SY)
        if d <= SR - 4: px(x, y, P["sol"])
        elif d <= SR: px(x, y, P["sol2"])
        elif d <= SR + 5 and (x + y) % 2 == 0: px(x, y, P["sol2"])   # halo pontilhado

# --- nuvens: faixas horizontais com base reta ---
def nuvem(x0, y0, comp, alt):
    for k in range(alt):
        a = x0 + k * 3 + rnd.randint(0, 2); b = x0 + comp - k * 4 - rnd.randint(0, 3)
        cor = P["nuvem"] if k < alt - 1 else P["nuvem2"]
        for x in range(a, b): px(x, y0 + k, cor)
    for x in range(x0 + 2, x0 + comp - 3): px(x, y0 + alt, P["nuvem3"])
for (x0, y0, c, a) in [(205, 38, 70, 3), (60, 58, 52, 2), (360, 70, 90, 3), (250, 96, 60, 2), (410, 30, 50, 2), (20, 104, 40, 2)]:
    nuvem(x0, y0, c, a)

# --- pássaros ---
for (bx, by) in [(298, 112), (308, 106), (286, 118), (316, 114)]:
    for dx, dy in [(-2, -1), (-1, 0), (0, 0), (1, 0), (2, -1)]:
        px(bx + dx, by + dy, P["nuvem3"])

# --- montanha (perfil côncavo, topo achatado) ---
MX, PEAK, MW = 170, 64, 140
def topo(x):
    u = max(0.0, abs(x - MX) - 6) / MW
    if u >= 1: return None
    return PEAK + (HORIZ - PEAK) * (1 - (1 - u) ** 2.2)
for x in range(MX - MW - 6, MX + MW + 7):
    yt = topo(x)
    if yt is None: continue
    neve = PEAK + 20 + (3 if (x // 3) % 3 == 0 else 0) + (6 if (x // 5) % 4 == 1 and abs(x - MX) < 30 else 0)
    for y in range(int(yt), HORIZ):
        lado_dir = x >= MX
        if y < neve: c = P["neve_r"] if lado_dir else P["neve_l"]
        else:
            c = P["mont_r"] if lado_dir else P["mont_l"]
            if lado_dir and (y - int(yt)) < 2: c = mix(c, P["ceu5"], 0.35)   # borda iluminada pelo sol
        px(x, y, c)

# --- colinas em primeiro plano do horizonte ---
for x in range(W):
    y1 = int(152 + 6 * math.sin(x / 31) + 3 * math.sin(x / 11 + 1))
    for y in range(y1, HORIZ): px(x, y, P["colina"])
    y2 = int(161 + 4 * math.sin(x / 17 + 2) + 2 * math.sin(x / 7))
    for y in range(y2, HORIZ): px(x, y, P["colina2"])
# pagode distante na colina (silhueta)
PX0, PY = 452, 158
for k, (w, h) in enumerate([(15, 1), (9, 3), (13, 1), (7, 3), (11, 1), (5, 3), (1, 5)]):
    for y in range(PY - h, PY):
        for x in range(PX0 - w // 2, PX0 + w // 2 + 1): px(x, y, P["colina2"])
    PY -= h

# --- lago: reflexo espelhado com ondulações ---
acima = [row[:] for row in img]
for y in range(HORIZ, SHORE):
    d = y - HORIZ
    ry = HORIZ - 1 - int(d * 1.15)
    onda = (1 if (y // 2) % 3 == 0 else -1 if (y // 2) % 3 == 1 else 0) * (1 + d // 25)
    for x in range(W):
        if ry < 0: c = acima[0][x]
        else: c = acima[ry][min(W - 1, max(0, x + onda))]
        c = mix(c, P["agua"], min(0.85, 0.50 + d / 110))
        if (y % 5 == 0) and ((x + y * 3) // 7) % 5 == 0: c = mix(c, P["ceu6"], 0.35)   # brilhos
        img[y][x] = c
# trilha de luz do sol na água
for y in range(HORIZ + 2, SHORE, 2):
    meia = 3 + (y - HORIZ) // 5
    for x in range(SX - meia, SX + meia):
        if (x * 7 + y * 3) % 5 < 3: px(x, y, P["sol2"] if (x + y) % 4 else P["sol"])

# --- torii na água ---
def torii(ox, base, alt, refl=False):
    def r(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if refl:
                    yy = base + (base - y)
                    if HORIZ <= yy < SHORE: px(x, yy, mix(c, P["agua"], 0.55))
                else: px(x, y, c)
    top = base - alt
    # pilares
    for cx in (ox - 18, ox + 16):
        r(cx, top + 6, cx + 4, base, P["torii"]); r(cx + 4, top + 6, cx + 4, base, P["torii_s"])
    # kasagi (viga superior, pontas levantadas) + topo sumi
    r(ox - 28, top + 2, ox + 29, top + 4, P["torii"])
    r(ox - 27, top, ox + 28, top + 1, P["sumi"])
    r(ox - 30, top - 1, ox - 27, top, P["sumi"]); r(ox + 28, top - 1, ox + 31, top, P["sumi"])
    # shimaki / nuki
    r(ox - 24, top + 6, ox + 24, top + 7, P["torii_s"])
    r(ox - 23, top + 16, ox + 23, top + 18, P["torii"]); r(ox - 23, top + 18, ox + 23, top + 18, P["torii_s"])
    # gakuzuka (placa central)
    r(ox - 1, top + 7, ox + 1, top + 15, P["torii"])
torii(392, 222, 58, refl=True)
torii(392, 222, 58)
for x in range(370, 418):   # espuma na base
    if (x // 2) % 2 == 0 and not (372 <= x <= 379 or 406 <= x <= 413): px(x, 223, mix(P["ceu6"], P["agua"], 0.3))

# --- margem em primeiro plano ---
for x in range(W):
    yb = SHORE + int(2 * math.sin(x / 13) + 1.5 * math.sin(x / 5))
    for y in range(yb, H):
        c = P["terra"]
        if y < yb + 2: c = P["musgo"]
        elif y < yb + 5 and (x + y) % 3 == 0: c = P["musgo2"]
        elif rnd.random() < 0.05: c = P["musgo2"]
        img[y][x] = c
    if x % 7 == 0 and rnd.random() < 0.7:   # tufos de grama
        for k in range(rnd.randint(2, 4)): px(x, yb - k, P["musgo"])
for (sx, sy, sw) in [(250, 248, 9), (300, 252, 6), (455, 250, 7)]:   # pedras
    for y in range(sy, sy + 4):
        for x in range(sx - (y - sy), sx + sw + (y - sy)): px(x, y, P["pedra"] if y < sy + 2 else P["pedra2"])

# --- lanterna de pedra (tōrō) acesa ---
def toro(cx, base, s=1):
    def r(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): px(cx + x, base - y, c)
    r(-6 * s, 0, 6 * s, 2 * s, P["pedra2"])           # base
    r(-2 * s, 3 * s, 2 * s, 11 * s, P["pedra"])        # coluna
    r(-5 * s, 12 * s, 5 * s, 13 * s, P["pedra2"])      # plataforma
    r(-4 * s, 14 * s, 4 * s, 20 * s, P["pedra"])       # caixa de luz
    r(-2 * s, 15 * s, 2 * s, 19 * s, P["lanterna"])    # luz
    r(-1 * s, 16 * s, 1 * s, 18 * s, P["lanterna2"])
    r(-8 * s, 21 * s, 8 * s, 22 * s, P["pedra2"])      # telhado
    r(-6 * s, 23 * s, 6 * s, 24 * s, P["pedra2"])
    r(-1 * s, 25 * s, 1 * s, 27 * s, P["pedra"])       # ponta
    for y in range(-4, 30 * s):                          # brilho pontilhado
        for x in range(-12 * s, 12 * s + 1):
            d = math.hypot(x, y - 17 * s)
            if 6 * s < d < 11 * s and (x + y) % 3 == 0:
                gx, gy = cx + x, base - y
                if 0 <= gx < W and 0 <= gy < H: img[gy][gx] = mix(img[gy][gx], P["lanterna"], 0.45)
toro(446, 244, 1)
toro(272, 242, 1)

# --- cerejeira (sakura) à esquerda ---
def galho(x0, y0, x1, y1, esp, c):
    n = max(abs(x1 - x0), abs(y1 - y0)) + 1
    for i in range(n):
        t = i / max(1, n - 1)
        x = round(x0 + (x1 - x0) * t); y = round(y0 + (y1 - y0) * t)
        e = max(1, round(esp * (1 - 0.6 * t)))
        for dx in range(-e // 2, e - e // 2):
            px(x + dx, y, c); px(x + dx + 1, y, P["tronco2"] if dx == e - e // 2 - 1 else c)
galho(26, 270, 46, 200, 13, P["tronco"])
galho(46, 200, 58, 140, 9, P["tronco"])
galho(58, 140, 120, 92, 4, P["tronco"])
galho(54, 160, 10, 120, 4, P["tronco"])
galho(58, 140, 70, 70, 4, P["tronco"])
galho(70, 70, 140, 48, 2, P["tronco"])
galho(50, 182, 112, 170, 3, P["tronco"])
flores = [(120, 90, 20), (140, 50, 17), (72, 66, 22), (20, 116, 19), (100, 112, 16), (40, 84, 20),
          (6, 80, 16), (96, 40, 15), (160, 64, 11), (60, 108, 14), (128, 122, 10)]
tons = [P["sak0"], P["sak1"], P["sak2"], P["sak3"]]
for (fx, fy, fr) in flores:
    bolhas = [(fx, fy, fr * 0.75)] + [(fx + rnd.uniform(-fr, fr) * 0.7, fy + rnd.uniform(-fr, fr) * 0.55,
              fr * rnd.uniform(0.35, 0.55)) for _ in range(7)]
    for y in range(fy - fr - 4, fy + fr + 5):
        for x in range(fx - fr - 6, fx + fr + 7):
            dentro = [(bx, by, br) for (bx, by, br) in bolhas if math.hypot(x - bx, y - by) <= br + rnd.uniform(-1.2, 1.2)]
            if not dentro: continue
            # luz vem de cima-direita (sol): nível pela posição relativa à bolha mais próxima
            bx, by, br = min(dentro, key=lambda b: math.hypot(x - b[0], y - b[1]) / b[2])
            luz = ((y - by) - 0.5 * (x - bx)) / br          # -1 (iluminado) .. +1 (sombra)
            lv = (luz + 1) * 1.6 + (fy - y < -fr * 0.4) * 0.8
            i = int(lv); f = lv - i
            if f * 16 > BAYER[y % 4][x % 4] + 0.5: i += 1
            px(x, y, tons[max(0, min(3, i))])

# --- pétalas caindo ---
for _ in range(70):
    x = rnd.randint(0, W - 1); y = rnd.randint(20, SHORE + 20)
    if x > 200 and rnd.random() < 0.5: continue
    c = rnd.choice([P["sak0"], P["sak1"], P["sak1"], P["sak2"]])
    px(x, y, c)
    if rnd.random() < 0.4: px(x + 1, y, c)

# --- gravar PNG ampliado ---
def salvar(path, escala):
    raw = bytearray()
    for row in img:
        linha = bytearray()
        for (r, g, b) in row: linha += bytes((r, g, b)) * escala
        for _ in range(escala): raw += b"\x00" + linha
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", W * escala, H * escala, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        f.write(chunk(b"IEND", b""))

if __name__ == "__main__":
    saida = sys.argv[1] if len(sys.argv) > 1 else "entardecer.png"
    salvar(saida, int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    print(saida)
