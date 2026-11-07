#!/usr/bin/env python3
"""Papel de parede "Yoru — rua do templo" — pixel art noturna gerada por código (sem dependências).

Rua de pedra em perspectiva até um templo, casas de madeira com janelas shoji acesas, lanternas
vermelhas (chōchin) nos beirais e num varal atravessando a rua, um torii no meio do caminho,
pagode ao fundo, lua crescente e estrelas. 480x270 ampliado por vizinho mais próximo (x4 = 1920x1080).
Determinístico. Uso: gerar-papel-de-parede-noite.py SAIDA.png [escala]
"""
import math, random, struct, sys, zlib

W, H = 480, 270
VX, VY = 240, 150          # ponto de fuga (horizonte)
rnd = random.Random(1945)

def hx(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
P = {k: hx(v) for k, v in {
    "ceu0": "#0B0C18", "ceu1": "#12142A", "ceu2": "#1A1D3A", "ceu3": "#242849", "ceu4": "#2F3358",
    "estrela": "#E6E4EC", "estrela2": "#8F93C0", "lua": "#F2EEDC", "lua2": "#D8D2B8", "halo": "#2C3060",
    "silh": "#0D0E1A", "silh2": "#141629", "templo": "#101120",
    "madeira": "#2A1E24", "madeira2": "#352630", "madeira3": "#22181E", "viga": "#17111A",
    "telhado": "#0F1020", "telhado2": "#1B1D33", "beiral": "#262A47",
    "shoji": "#F2C46B", "shoji2": "#D9A441", "grade": "#6B4A2A",
    "noren": "#B3263B", "noren2": "#2F3A6B",
    "chochin": "#C8102E", "chochin2": "#FF6B5B", "chochin3": "#FFB08A", "tampa": "#1A1414",
    "brilho": "#5A2A3A", "brilho2": "#7A3A3E",
    "pedra": "#34333F", "pedra2": "#2A2934", "junta": "#1C1B24", "reflexo": "#6E4A3A", "reflexo2": "#9A5A40",
    "torii": "#C8102E", "torii2": "#8E0B22", "sumi": "#0E0F18",
    "petala": "#B5566F",
}.items()}

img = [[P["ceu0"]] * W for _ in range(H)]
def px(x, y, c):
    if 0 <= x < W and 0 <= y < H: img[y][x] = c
def mix(a, b, t): return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def rect(x0, y0, x1, y1, c):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1): px(x, y, c)

# ---------- céu: faixas lisas com transição pontilhada curta ----------
faixas = [P[f"ceu{i}"] for i in range(5)]
for y in range(VY):
    t = (y / (VY - 1)) ** 1.1 * (len(faixas) - 1)
    i = min(int(t), len(faixas) - 2); f = t - i
    g = max(0.0, (f - 0.78) / 0.22)
    for x in range(W): img[y][x] = faixas[i + 1] if g * 16 > BAYER[y % 4][x % 4] + 0.5 else faixas[i]

# estrelas (esparsas, mais no alto)
for _ in range(90):
    x = rnd.randint(0, W - 1); y = int(rnd.random() ** 1.8 * 110)
    px(x, y, P["estrela"] if rnd.random() < 0.35 else P["estrela2"])
for (x, y) in [(60, 18), (150, 30), (330, 14), (440, 70), (20, 64)]:     # estrelas com brilho em cruz
    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]: px(x + dx, y + dy, P["estrela"] if (dx, dy) == (0, 0) else P["estrela2"])

# lua crescente com halo sólido
LX, LY, LR = 318, 34, 13
for y in range(LY - LR - 6, LY + LR + 7):
    for x in range(LX - LR - 6, LX + LR + 7):
        d = math.hypot(x - LX, y - LY)
        if LR < d <= LR + 4: px(x, y, mix(img[y][x], P["halo"], 0.6))
        elif d <= LR:
            if math.hypot(x - (LX + 6), y - (LY - 4)) > LR - 1:   # recorte = crescente
                px(x, y, P["lua"] if math.hypot(x - LX + 3, y - LY + 2) < LR - 3 else P["lua2"])
            else: px(x, y, mix(img[y][x], P["halo"], 0.35))

# ---------- fundo: pagode e templo no ponto de fuga ----------
def pagode(cx, base, nivel_w, nivel_h, niveis, cor):
    y = base
    for k in range(niveis):
        w = nivel_w - k * 3
        rect(cx - w, y - 1, cx + w, y, cor)                 # beiral
        rect(cx - w + 3, y - nivel_h, cx + w - 3, y - 2, cor)
        if k % 2 == 0: px(cx, y - nivel_h // 2, P["shoji2"])   # janelinha acesa
        y -= nivel_h
    rect(cx, y - 8, cx, y, cor)                              # sorin (haste)
pagode(292, VY, 15, 10, 5, P["silh"])
# templo: telhado largo em curva no fim da rua
for x in range(VX - 34, VX + 35):
    u = abs(x - VX) / 34
    topo = int(VY - 22 + 6 * u * u)
    rect(x, topo, x, VY, P["templo"])
for x in range(VX - 38, VX + 39):
    u = abs(x - VX) / 38
    y = int(VY - 20 + 7 * u * u); px(x, y, P["beiral"]); px(x, y + 1, P["telhado2"])
for x in range(VX - 12, VX + 13, 6): rect(x, VY - 12, x + 3, VY - 4, P["shoji"])    # portas iluminadas

# ---------- rua em perspectiva ----------
def meia_rua(y): return 14 + (y - VY) / (H - VY) * 92            # meia largura do caminho
for y in range(VY, H):
    hw = meia_rua(y)
    for x in range(int(VX - hw), int(VX + hw) + 1):
        c = P["pedra"] if ((x // max(2, int(hw / 6))) + (y // 3)) % 2 else P["pedra2"]
        img[y][x] = c
    # juntas horizontais, mais espaçadas perto
    t = (y - VY) / (H - VY)
    if int((t ** 0.55) * 26) != int((((y + 1 - VY) / (H - VY)) ** 0.55) * 26):
        for x in range(int(VX - hw), int(VX + hw) + 1): px(x, y, P["junta"])

# ---------- casas dos dois lados ----------
ALTURA = 0.50                                      # altura da parede relativa à distância ao horizonte
def borda(s):                                      # s: 0 (fundo) .. 1 (frente na base da tela) .. >1 (fora)
    return VX - (14 + 92 * s), VY + (H - VY) * s   # x da borda esquerda da rua e y da base
divisas = [0.10, 0.18, 0.28, 0.40, 0.56, 0.78, 1.06, 1.45, 2.0, 2.7]
lanternas = []

def casa(lado, s0, s1, k):
    mad = [P["madeira"], P["madeira2"], P["madeira3"]][k % 3]
    xa, _ = borda(s0); xb, _ = borda(s1)
    for x in range(int(min(xa, xb)), int(max(xa, xb)) + 1):
        s = ((VX - x) - 14) / 92
        if s <= 0: continue
        yb = VY + (H - VY) * s; yt = VY - (H - VY) * ALTURA * s
        u = (s - s0) / (s1 - s0) if s1 != s0 else 0      # 0..1 ao longo da fachada
        xx = x if lado < 0 else 2 * VX - x
        for y in range(max(0, int(yt)), min(H, int(yb))):
            v = (yb - y) / (yb - yt)                   # 0 base .. 1 topo da parede
            c = mad
            if 0.40 < v < 0.68 and 0.18 < u < 0.82:    # janela shoji acesa com grade
                c = P["shoji"] if (int(u * 18) % 4 and int(v * 30) % 4) else P["grade"]
                if v > 0.62 or v < 0.44: c = P["shoji2"] if c != P["grade"] else c
            elif v < 0.30 and 0.25 < u < 0.75:         # porta com noren
                c = P["noren"] if (k % 2 == 0) else P["noren2"]
                if v < 0.12: c = mix(P["shoji2"], mad, 0.55)        # luz saindo por baixo
                elif int(u * 10) % 3 == 0: c = mix(c, P["viga"], 0.5)
            elif abs(v - 0.34) < 0.025 or u < 0.04 or u > 0.96: c = P["viga"]
            px(xx, y, c)
        # beiral (telhado em balanço) acima da parede
        esp = max(1, int(2 + 6 * s)); bal = int(3 + 9 * s)
        for y in range(int(yt) - esp, int(yt) + 1):
            for dx in range(0, bal):
                X = (x - dx) if lado < 0 else (2 * VX - x + dx)
                if (lado < 0 and dx > 0) or (lado > 0 and dx > 0): pass
                px(xx, y, P["telhado"] if y < int(yt) - 1 else P["beiral"])
        for y in range(int(yt) - esp - int(10 * s), int(yt) - esp):   # caimento do telhado
            px(xx, y, P["telhado2"] if (y + x) % 7 else P["telhado"])
    # lanterna na divisa (beiral)
    xs, _ = borda(s1)
    yt = VY - (H - VY) * ALTURA * s1
    lanternas.append(((xs if lado < 0 else 2 * VX - xs), yt + 3 + 4 * s1, s1))

for lado in (-1, 1):
    for k in range(len(divisas) - 1):
        casa(lado, divisas[k], divisas[k + 1], k + (0 if lado < 0 else 1))

# ---------- chōchin (lanterna de papel) ----------
def chochin(cx, cy, s):
    r = max(1.5, 2 + 6.5 * s); h = r * 1.35
    for y in range(int(cy - h - r), int(cy + h + r) + 1):      # halo sólido
        for x in range(int(cx - r * 2.2), int(cx + r * 2.2) + 1):
            d = math.hypot((x - cx) / (r * 2.2), (y - cy) / (h + r))
            if 0.62 < d <= 1.0 and 0 <= x < W and 0 <= y < H: img[y][x] = mix(img[y][x], P["brilho"], 0.5)
    for y in range(int(cy - h), int(cy + h) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            if ((x - cx) / r) ** 2 + ((y - cy) / h) ** 2 <= 1.0:
                q = ((x - cx) / r) ** 2 + ((y - cy) / h) ** 2
                c = P["chochin3"] if q < 0.18 else P["chochin2"] if q < 0.5 else P["chochin"]
                if r > 3 and int((y - cy + h) / max(1, h / 3)) % 2 == 0 and q > 0.5: c = mix(c, P["tampa"], 0.25)
                px(x, y, c)
    capa = max(1, int(r * 0.25))
    rect(cx - r * 0.6, cy - h - capa, cx + r * 0.6, cy - h, P["tampa"])
    rect(cx - r * 0.6, cy + h, cx + r * 0.6, cy + h + capa, P["tampa"])
    rect(cx, cy - h - capa - max(1, int(3 * s)), cx, cy - h - capa, P["tampa"])     # cordão
for (x, y, s) in sorted(lanternas, key=lambda l: l[2]):
    if 0.28 <= s < 2.0: chochin(x, y, s)      # sem lanternas nas casas distantes (fundo limpo)

# varal de lanternas atravessando a rua
for s_var in (0.78,):                       # um varal só, perto
    xl, _ = borda(s_var); xr = 2 * VX - xl
    yt = VY - (H - VY) * ALTURA * s_var + 2
    queda = 6 + 16 * s_var
    for x in range(int(xl), int(xr) + 1):
        u = (x - xl) / (xr - xl); y = yt + queda * 4 * u * (1 - u)
        px(x, int(y), P["sumi"])
    n = 6 if s_var < 0.5 else 7
    for i in range(1, n):
        u = i / n; x = xl + (xr - xl) * u; y = yt + queda * 4 * u * (1 - u)
        chochin(x, y + 2 + 5 * s_var, s_var * 0.75)

# ---------- torii atravessando a rua ----------
def torii(s):
    xl, yb = borda(s); xr = 2 * VX - xl
    alt = (H - VY) * s * 0.95
    top = yb - alt; esp = max(2, int(5 * s))
    for cx in (xl + 2, xr - 2 - esp):
        rect(cx, top + alt * 0.12, cx + esp, yb, P["torii"]); rect(cx + esp, top + alt * 0.12, cx + esp, yb, P["torii2"])
    rect(xl - 8 * s, top, xr + 8 * s, top + max(2, 4 * s), P["torii"])
    rect(xl - 9 * s, top - max(1, 2 * s), xr + 9 * s, top, P["sumi"])
    rect(xl - 2, top + alt * 0.22, xr + 2, top + alt * 0.22 + max(1, 3 * s), P["torii"])
    rect(VX - max(1, 2 * s), top + 3 * s, VX + max(1, 2 * s), top + alt * 0.22, P["torii2"])
torii(0.46)

# ---------- reflexos das lanternas na pedra molhada ----------
for (x, y, s) in lanternas:
    if s < 1.2:
        yb = VY + (H - VY) * s
        for k in range(int(4 + 20 * s)):
            yy = int(yb + 2 + k * 2)
            if yy >= H: break
            w = max(1, int((2 + 4 * s) * rnd.uniform(0.4, 1.0)))
            xx = int(x + (8 * s if x < VX else -8 * s))
            if abs(xx - VX) < meia_rua(min(H - 1, yy)):
                for d in range(-w, w + 1):
                    if rnd.random() < 0.8: px(xx + d, yy, P["reflexo2"] if k < 3 else P["reflexo"])

# lanternas de pedra (tōrō) na frente
def toro(cx, base, e):
    def r(x0, y0, x1, y1, c): rect(cx + x0 * e, base - y1 * e, cx + x1 * e, base - y0 * e, c)
    r(-6, 0, 6, 2, P["pedra2"]); r(-2, 3, 2, 11, P["pedra"]); r(-5, 12, 5, 13, P["pedra2"])
    r(-4, 14, 4, 20, P["pedra"]); r(-2, 15, 2, 19, P["shoji"]); r(-1, 16, 1, 18, P["lanterna"] if "lanterna" in P else P["shoji"])
    r(-8, 21, 8, 22, P["telhado"]); r(-6, 23, 6, 24, P["telhado"]); r(-1, 25, 1, 27, P["pedra"])
P["lanterna"] = hx("#FFE7A8")
toro(VX - 100, 262, 1); toro(VX + 100, 262, 1)

# pétalas escuras caindo (poucas)
for _ in range(35):
    x = rnd.randint(0, W - 1); y = rnd.randint(30, H - 1)
    px(x, y, P["petala"])

# ---------- PNG ----------
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
    saida = sys.argv[1] if len(sys.argv) > 1 else "noite.png"
    salvar(saida, int(sys.argv[2]) if len(sys.argv) > 2 else 4); print(saida)
