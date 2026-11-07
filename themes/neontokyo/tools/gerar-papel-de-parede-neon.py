#!/usr/bin/env python3
"""Papel de parede "Neon Tokyo — rua na chuva" — pixel art cyberpunk gerada por código (sem dependências).

Prédios altos dos dois lados com letreiros neon verticais (caracteres pixel), horizonte de arranha-céus em
três profundidades com janelas acesas, névoa roxa, carros voadores com rastro, asfalto molhado com
reflexos e chuva em traços pixel. 480x270 ampliado por vizinho mais próximo (x4 = 1920x1080). Determinístico.
Uso: gerar-papel-de-parede-neon.py SAIDA.png [escala]
"""
import math, random, struct, sys, zlib

W, H = 480, 270
HOR = 188                      # linha da rua (base dos prédios)
rnd = random.Random(2077)
def hx(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
P = {k: hx(v) for k, v in {
    "ceu0": "#05060C", "ceu1": "#0A0C1C", "ceu2": "#130F2C", "ceu3": "#1F1238", "ceu4": "#2C1544",
    "longe": "#141830", "longe2": "#1B2040", "medio": "#0F1224", "medio2": "#161A33", "perto": "#08090F", "perto2": "#0E1018",
    "mag": "#FF2E88", "mag2": "#B0145E", "cia": "#00E5FF", "cia2": "#0088AA", "ama": "#FFE600", "ama2": "#A89500",
    "roxo": "#B266FF", "verde": "#39FF88", "branco": "#E6F1FF",
    "jan_c": "#2A6F8A", "jan_m": "#7A2050", "jan_a": "#8A7A20",
    "asfalto": "#0A0B12", "asfalto2": "#11131E", "faixa": "#3A3F55", "chuva": "#5A6A90", "chuva2": "#8FA3D0",
}.items()}
img = [[P["ceu0"]] * W for _ in range(H)]
def px(x, y, c):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H: img[y][x] = c
def mix(a, b, t): return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
def rect(x0, y0, x1, y1, c):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1): px(x, y, c)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

# ---------- céu com névoa roxa perto do horizonte ----------
faixas = [P[f"ceu{i}"] for i in range(5)]
for y in range(HOR):
    t = (y / (HOR - 1)) ** 1.3 * (len(faixas) - 1)
    i = min(int(t), len(faixas) - 2); f = t - i
    g = max(0.0, (f - 0.75) / 0.25)
    for x in range(W): img[y][x] = faixas[i + 1] if g * 16 > BAYER[y % 4][x % 4] + 0.5 else faixas[i]

def halo(cx0, cy0, cx1, cy1, cor, raio, forca=0.35):
    for y in range(int(cy0 - raio), int(cy1 + raio) + 1):
        for x in range(int(cx0 - raio), int(cx1 + raio) + 1):
            dx = max(cx0 - x, 0, x - cx1); dy = max(cy0 - y, 0, y - cy1); d = math.hypot(dx, dy)
            if 0 < d <= raio and 0 <= x < W and 0 <= y < H:
                img[y][x] = mix(img[y][x], cor, forca * (1 - d / raio) ** 1.5)

# ---------- horizonte em três profundidades ----------
def skyline(base, alt_min, alt_max, larg_min, larg_max, cor, cor2, janelas, dens, x0=0, x1=W, antena=0.3):
    x = x0
    while x < x1:
        w = rnd.randint(larg_min, larg_max); h = rnd.randint(alt_min, alt_max)
        topo = base - h
        rect(x, topo, x + w - 1, base, cor)
        rect(x + w - 2, topo + 1, x + w - 1, base, cor2)
        if rnd.random() < antena:
            ax = x + w // 2; rect(ax, topo - rnd.randint(4, 12), ax, topo, cor)
            px(ax, topo - 13, P["mag"] if rnd.random() < 0.5 else P["vermelho"] if "vermelho" in P else P["mag"])
        for yy in range(topo + 2, base - 1, 3):
            for xx in range(x + 1, x + w - 2, 2):
                if rnd.random() < dens: px(xx, yy, rnd.choice(janelas))
        x += w + rnd.randint(0, 2)
skyline(HOR - 30, 30, 85, 8, 18, P["longe"], P["longe2"], [P["jan_c"], P["jan_m"], P["jan_a"]], 0.18)
halo(0, HOR - 40, W, HOR - 25, P["roxo"], 30, 0.22)                       # névoa iluminada
skyline(HOR - 8, 40, 110, 12, 26, P["medio"], P["medio2"], [P["cia2"], P["mag2"], P["ama2"], P["jan_c"]], 0.22)

# carros voadores com rastro de luz
for (x, y, comp, cor) in [(120, 62, 28, P["mag"]), (300, 48, 22, P["cia"]), (360, 90, 18, P["ama"]), (60, 104, 14, P["cia"])]:
    for k in range(comp): px(x - k, y, mix(cor, img[y][x - k] if 0 <= x - k < W else cor, k / comp))
    rect(x, y - 1, x + 3, y + 1, P["perto2"]); px(x + 3, y, P["branco"]); px(x, y + 1, cor)

# ---------- caracteres neon pixel (pseudo-katakana 5x5) ----------
def glifo():
    g = [[0] * 5 for _ in range(5)]
    for _ in range(rnd.randint(2, 3)):                      # traços horizontais/verticais/diagonais
        tipo = rnd.choice("hvd")
        if tipo == "h":
            r = rnd.randint(0, 4); [g[r].__setitem__(c, 1) for c in range(rnd.randint(0, 1), rnd.randint(3, 4) + 1)]
        elif tipo == "v":
            c = rnd.randint(0, 4); [g[r].__setitem__(c, 1) for r in range(rnd.randint(0, 1), 5)]
        else:
            for k in range(5): g[k][4 - k if rnd.random() < 0.5 else k] = 1
    return g
def letreiro_vertical(x, y, n, cor, cor2, escala=1):
    larg = 5 * escala + 4; alt = n * (5 * escala + 2) + 3
    halo(x, y, x + larg, y + alt, cor, 10 * escala, 0.45)
    rect(x, y, x + larg, y + alt, P["perto"])
    for k in range(larg + 1): px(x + k, y, cor2); px(x + k, y + alt, cor2)
    for k in range(alt + 1): px(x, y + k, cor2); px(x + larg, y + k, cor2)
    for i in range(n):
        g = glifo(); oy = y + 2 + i * (5 * escala + 2)
        for r in range(5):
            for c in range(5):
                if g[r][c]:
                    rect(x + 2 + c * escala, oy + r * escala, x + 2 + c * escala + escala - 1, oy + r * escala + escala - 1, cor)
def letreiro_horizontal(x, y, texto_cor, cor2, n=3):
    larg = n * 7 + 4; halo(x, y, x + larg, y + 9, texto_cor, 9, 0.45)
    rect(x, y, x + larg, y + 9, P["perto"])
    for k in range(larg + 1): px(x + k, y, cor2); px(x + k, y + 9, cor2)
    for i in range(n):
        g = glifo()
        for r in range(5):
            for c in range(5):
                if g[r][c]: px(x + 3 + i * 7 + c, y + 2 + r, texto_cor)

# ---------- prédios da frente (esquerda e direita) ----------
def predio(x0, x1, topo, cor, cor2):
    rect(x0, topo, x1, HOR, cor)
    rect(x1 - 2, topo, x1, HOR, cor2)
    for yy in range(topo + 4, HOR - 4, 6):                   # andares com janelas apagadas/acesas
        for xx in range(x0 + 3, x1 - 4, 5):
            c = P["perto2"] if rnd.random() < 0.85 else rnd.choice([P["jan_c"], P["jan_m"]])   # poucas acesas
            rect(xx, yy, xx + 2, yy + 2, c)
predio(0, 58, 10, P["perto"], P["perto2"]); predio(58, 104, 46, P["perto"], P["perto2"])
predio(392, 438, 30, P["perto"], P["perto2"]); predio(438, 479, 0, P["perto"], P["perto2"])
letreiro_vertical(20, 30, 6, P["mag"], P["mag2"], 2)
letreiro_vertical(78, 64, 5, P["cia"], P["cia2"], 1)
letreiro_vertical(450, 18, 7, P["cia"], P["cia2"], 2)
letreiro_vertical(404, 52, 5, P["ama"], P["ama2"], 1)
letreiro_horizontal(110, 120, P["mag"], P["mag2"], 3)
letreiro_horizontal(338, 104, P["verde"], P["cia2"], 3)
letreiro_horizontal(250, 140, P["cia"], P["cia2"], 2)

# ---------- rua molhada com reflexos ----------
for y in range(HOR, H):
    for x in range(W):
        img[y][x] = P["asfalto"] if (x // 6 + y // 3) % 2 else P["asfalto2"]
for x in range(0, W, 24):                                    # faixa central tracejada
    rect(x, 228, x + 11, 229, P["faixa"])
rect(0, HOR, W - 1, HOR + 1, P["perto2"])
fontes = [(29, P["mag"], 18), (82, P["cia"], 9), (465, P["cia"], 18), (410, P["ama"], 9), (124, P["mag"], 12),
          (352, P["verde"], 12), (258, P["cia"], 8)]
for (xc, cor, larg) in fontes:                               # reflexos: faixas largas interrompidas
    y = HOR + 3
    while y < H:
        comp = rnd.randint(2, 4); w = max(2, int(larg * rnd.uniform(0.5, 0.9)))
        xo = xc + rnd.randint(-1, 1)
        forca = 0.55 * (1 - (y - HOR) / (H - HOR)) + 0.12
        for yy in range(y, min(H, y + comp)):
            for xx in range(xo - w // 2, xo + w // 2 + 1):
                if 0 <= xx < W: img[yy][xx] = mix(img[yy][xx], cor, forca)
        y += comp + rnd.randint(2, 4)

# ---------- chuva ----------
for _ in range(430):
    x = rnd.randint(-10, W); y = rnd.randint(0, H - 1)
    perto = rnd.random() < 0.25
    comp = 5 if perto else 3; cor = P["chuva2"] if perto else P["chuva"]
    for k in range(comp):
        xx, yy = x + k // 2, y + k
        if 0 <= xx < W and 0 <= yy < H: img[yy][xx] = mix(img[yy][xx], cor, 0.65 if perto else 0.45)
for _ in range(70):                                          # respingos no chão
    x = rnd.randint(0, W - 1); y = rnd.randint(HOR + 2, H - 1)
    px(x, y, P["chuva2"]); px(x - 1, y - 1, P["chuva"]); px(x + 1, y - 1, P["chuva"])

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
    saida = sys.argv[1] if len(sys.argv) > 1 else "neon.png"
    salvar(saida, int(sys.argv[2]) if len(sys.argv) > 2 else 4); print(saida)
