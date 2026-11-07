#!/usr/bin/env python3
"""Papel de parede "Mary's — gatinhos" — pixel art kawaii em rosa e creme (sem dependências).

Gato grande sentado (olhos brilhantes, bochechas rosadas), gato dormindo enrolado numa nuvem (zzz),
filhote com novelo, nuvens fofas, corações, estrelinhas, pegadas e o nome "Mary's" em letras pixel.
Gatos desenhados por formas, com contorno ameixa de 1 px calculado automaticamente.
480x270 ampliado por vizinho mais próximo (x4 = 1920x1080). Determinístico.
Uso: gerar-papel-de-parede-gatinhos.py SAIDA.png [escala]
"""
import math, random, struct, sys, zlib

W, H = 480, 270
rnd = random.Random(2020)
def hx(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
P = {k: hx(v) for k, v in {
    "ceu0": "#F6C9D6", "ceu1": "#F9D5DF", "ceu2": "#FBE2E8", "ceu3": "#FDEDEF", "ceu4": "#FFF4EE",
    "nuvem": "#FFFDF8", "nuvem2": "#FCE7EC", "nuvem3": "#F6CAD6",
    "linha": "#5A2E3F", "olho": "#4A2433", "brilho": "#FFFFFF",
    "creme": "#FFF1DC", "creme2": "#F6DDBE", "branco": "#FFFBF6", "branco2": "#EEDFE4",
    "caramelo": "#EBB58A", "caramelo2": "#D69466", "cinza": "#C9B7C2", "cinza2": "#A995A3",
    "rosa": "#F2A7BE", "rosa2": "#E26D96", "rosa3": "#C2457A", "bochecha": "#F7A8BF",
    "coracao": "#E26D96", "coracao2": "#F5B3C8", "estrela": "#FFE7A8", "estrela2": "#FFFFFF",
    "colina": "#FBDDE5", "colina2": "#F6CAD6", "colina3": "#F0B8C8", "pegada": "#F2A7BE",
    "lavanda": "#D9CCF0", "menta": "#CFEBDD",
}.items()}

img = [[P["ceu4"]] * W for _ in range(H)]
def px(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H: img[y][x] = c
def mix(a, b, t): return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

# ---------- céu: faixas lisas, transição curta pontilhada ----------
faixas = [P[f"ceu{i}"] for i in range(5)]
for y in range(H):
    t = min(1, y / 200) * (len(faixas) - 1)
    i = min(int(t), len(faixas) - 2); f = t - i
    g = max(0.0, (f - 0.8) / 0.2)
    for x in range(W): img[y][x] = faixas[i + 1] if g * 16 > BAYER[y % 4][x % 4] + 0.5 else faixas[i]

# ---------- camada de "sprite": formas com contorno automático ----------
class Sprite:
    def __init__(self): self.p = {}
    def elipse(self, cx, cy, rx, ry, c, so_dentro=None):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0 and (so_dentro is None or (x, y) in so_dentro):
                    self.p[(x, y)] = c
    def triangulo(self, a, b, c, cor):
        xs = [a[0], b[0], c[0]]; ys = [a[1], b[1], c[1]]
        def lado(p, q, r): return (r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])
        for y in range(int(min(ys)) - 1, int(max(ys)) + 2):
            for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
                d1, d2, d3 = lado(a, b, (x, y)), lado(b, c, (x, y)), lado(c, a, (x, y))
                if (d1 >= 0 and d2 >= 0 and d3 >= 0) or (d1 <= 0 and d2 <= 0 and d3 <= 0): self.p[(x, y)] = cor
    def ponto(self, x, y, c): self.p[(int(round(x)), int(round(y)))] = c
    def desenhar(self, contorno=True):
        if contorno:
            borda = set()
            for (x, y) in self.p:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if (x + dx, y + dy) not in self.p: borda.add((x + dx, y + dy))
            for (x, y) in borda: px(x, y, P["linha"])
        for (x, y), c in self.p.items(): px(x, y, c)

def olhos(sp, cx, cy, u, dormindo=False):
    for s in (-1, 1):
        ex = cx + s * 2.7 * u
        if dormindo:   # olhos fechados "︶"
            for k in range(-int(1.3 * u), int(1.3 * u) + 1):
                sp.ponto(ex + k, cy + 0.4 * u - (0 if abs(k) < u * 0.8 else -1) + 0.6 * u * (1 - (k / (1.3 * u)) ** 2) * 0 , P["linha"])
        else:
            for y in range(int(cy - 1.2 * u), int(cy + 1.2 * u) + 1):
                for x in range(int(ex - 0.8 * u), int(ex + 0.8 * u) + 1):
                    if ((x - ex) / (0.8 * u)) ** 2 + ((y - cy) / (1.2 * u)) ** 2 <= 1: sp.ponto(x, y, P["olho"])
            sp.ponto(ex - 0.3 * u, cy - 0.5 * u, P["brilho"])                  # brilho kawaii
            if u >= 4: sp.ponto(ex - 0.3 * u + 1, cy - 0.5 * u, P["brilho"]); sp.ponto(ex + 0.3 * u, cy + 0.5 * u, P["brilho"])

def rosto(sp, cx, cy, u, dormindo=False):
    olhos(sp, cx, cy, u, dormindo)
    sp.elipse(cx - 4.3 * u, cy + 2 * u, 1.2 * u, 0.6 * u, P["bochecha"]); sp.elipse(cx + 4.3 * u, cy + 2 * u, 1.2 * u, 0.6 * u, P["bochecha"])
    for dx in (0, 1) if u >= 3 else (0,):                                     # narizinho rosa
        sp.ponto(cx - 0.5 + dx, cy + 1.3 * u, P["rosa2"])
    OMEGA = ["x..x..x", ".xx.xx."]                                            # boquinha "ω" pixel
    e = max(1, round(u / 3)); ox = cx - 0.5 - 3 * e; oy = cy + 1.9 * u
    for yy, l in enumerate(OMEGA):
        for xx, c in enumerate(l):
            if c == "x":
                for a in range(e):
                    for b in range(e): sp.ponto(ox + xx * e + a, oy + yy * e + b, P["linha"])

def orelhas(sp, cx, cy, u, cor, interno=P["rosa"]):
    for s in (-1, 1):
        sp.triangulo((cx + s * 6.2 * u, cy - 1.0 * u), (cx + s * 5.4 * u, cy - 8.2 * u), (cx + s * 1.2 * u, cy - 4.4 * u), cor)
        sp.triangulo((cx + s * 5.2 * u, cy - 2.2 * u), (cx + s * 5.0 * u, cy - 6.4 * u), (cx + s * 2.6 * u, cy - 4.2 * u), interno)

def gato_sentado(cx, cy, u, corpo, sombra, barriga, manchas=None, rabo_lado=1):
    sp = Sprite()
    for k in range(40):                                                         # rabo curvado
        t = k / 39; a = math.pi * (0.95 - 1.1 * t)
        x = cx + rabo_lado * (6.2 * u + 3.2 * u * math.cos(a) * 0.9); y = cy + 9.5 * u - 4.8 * u * math.sin(a) - 2 * u * t
        sp.elipse(x, y, 1.25 * u, 1.25 * u, corpo)
    sp.elipse(cx, cy + 6.5 * u, 6.2 * u, 5.4 * u, corpo)                     # corpo
    sp.elipse(cx + 1.2 * u, cy + 8.5 * u, 4.6 * u, 3.0 * u, sombra, so_dentro=set(sp.p))   # sombra do corpo
    sp.elipse(cx, cy + 7.2 * u, 3.4 * u, 4.0 * u, barriga)                    # barriga
    orelhas(sp, cx, cy, u, corpo)
    sp.elipse(cx, cy, 6.6 * u, 5.3 * u, corpo)                                # cabeça
    if manchas:
        for (mx, my, mr, mc) in manchas: sp.elipse(cx + mx * u, cy + my * u, mr * u, mr * u * 0.8, mc, so_dentro=set(sp.p))
    sp.elipse(cx - 2.3 * u, cy + 11.4 * u, 1.7 * u, 1.0 * u, barriga); sp.elipse(cx + 2.3 * u, cy + 11.4 * u, 1.7 * u, 1.0 * u, barriga)
    rosto(sp, cx, cy, u)
    for s in ((-1, 1) if u >= 4 else ()):                                    # bigodes (só gatos grandes)
        for k in (-1, 1):
            for j in range(int(1.6 * u)):
                sp.ponto(cx + s * (7.0 * u + j), cy + 1.4 * u + k * (0.5 * u + j * 0.25), P["linha"])
    sp.desenhar()

def gato_dormindo(cx, cy, u, corpo, sombra):
    sp = Sprite()
    sp.elipse(cx + 2 * u, cy, 8.5 * u, 4.8 * u, corpo)                        # corpo enrolado
    sp.elipse(cx + 3 * u, cy + 2.2 * u, 6.0 * u, 2.4 * u, sombra, so_dentro=set(sp.p))
    for k in range(30):                                                         # rabo abraçando a frente
        t = k / 29; x = cx + 9 * u - 13 * u * t; y = cy + 4.2 * u + 0.8 * u * math.sin(t * math.pi)
        sp.elipse(x, y, 1.15 * u, 1.15 * u, corpo)
    orelhas(sp, cx - 5 * u, cy - 1.2 * u, u * 0.85, corpo)
    sp.elipse(cx - 5 * u, cy - 1.2 * u, 5.4 * u, 4.4 * u, corpo)
    rosto(sp, cx - 5 * u, cy - 1.0 * u, u * 0.85, dormindo=True)
    sp.desenhar()

def nuvem(cx, cy, larg, alt):
    sp = Sprite()
    n = max(3, int(larg / (alt * 0.9)))
    for i in range(n):
        x = cx - larg / 2 + larg * (i + 0.5) / n; r = alt * (0.75 + 0.35 * math.sin(i * 1.7 + cx))
        sp.elipse(x, cy - r * 0.4, r, r * 0.85, P["nuvem"])
    sp.elipse(cx, cy + alt * 0.2, larg * 0.55, alt * 0.55, P["nuvem"])
    for (x, y) in list(sp.p):
        if y > cy + alt * 0.15: sp.p[(x, y)] = P["nuvem2"]
        if y > cy + alt * 0.45: sp.p[(x, y)] = P["nuvem3"]
    sp.desenhar(contorno=False)

CORACAO = [".xx.xx.", "xhxxxxx", "xxxxxxx", ".xxxxx.", "..xxx..", "...x..."]
def coracao(x0, y0, e=1, cor=P["coracao"]):
    for y, l in enumerate(CORACAO):
        for x, ch in enumerate(l):
            if ch != ".":
                for a in range(e):
                    for b in range(e): px(x0 + x * e + a, y0 + y * e + b, P["coracao2"] if ch == "h" else cor)
def estrela(x, y, g=1):
    px(x, y, P["estrela2"])
    for d in range(1, g + 1):
        for (dx, dy) in ((d, 0), (-d, 0), (0, d), (0, -d)): px(x + dx, y + dy, P["estrela"])
def pegada(x, y, e=2):
    def bola(cx, cy, rx, ry):
        for yy in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for xx in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1: px(xx, yy, P["pegada"])
    bola(x, y, 1.6 * e, 1.3 * e)                                                       # almofada
    for (dx, dy) in ((-1.9, -2.0), (-0.65, -2.9), (0.65, -2.9), (1.9, -2.0)):          # 4 dedinhos separados
        bola(x + dx * e, y + dy * e, 0.55 * e, 0.6 * e)

# ---------- letras "Mary's" (5x7) ----------
FONTE = {
 "M": ["x...x", "xx.xx", "x.x.x", "x.x.x", "x...x", "x...x", "x...x"],
 "a": [".....", ".....", ".xxx.", "....x", ".xxxx", "x...x", ".xxxx"],
 "r": [".....", ".....", "x.xx.", "xx..x", "x....", "x....", "x...."],
 "y": [".....", ".....", "x...x", "x...x", ".xxxx", "....x", ".xxx."],
 "'": ["..x..", "..x..", ".x...", ".....", ".....", ".....", "....."],
 "s": [".....", ".....", ".xxxx", "x....", ".xxx.", "....x", "xxxx."],
}
def texto(t, x0, y0, e=3):
    x = x0
    for ch in t:
        g = FONTE[ch]
        for y, l in enumerate(g):
            for xx, c in enumerate(l):
                if c == "x":
                    for a in range(e):
                        for b in range(e):
                            px(x + xx * e + a + 1, y0 + y * e + b + 1, P["rosa"])        # sombra rosa
            for xx, c in enumerate(l):
                if c == "x":
                    for a in range(e):
                        for b in range(e): px(x + xx * e + a, y0 + y * e + b, P["linha"])
        x += (len(g[0]) + 1) * e

# ---------- composição ----------
for (x, y) in [(40, 50), (120, 26), (200, 60), (260, 20), (300, 92), (450, 40), (30, 120), (170, 110)]:
    estrela(x, y, 1 if rnd.random() < 0.6 else 2)
nuvem(70, 60, 70, 13); nuvem(250, 42, 90, 15); nuvem(440, 100, 60, 11); nuvem(170, 135, 50, 9)

texto("Mary's", 22, 18, 3)
coracao(132, 24, 2)

# colinas fofas no chão
for x in range(W):
    y1 = int(222 + 7 * math.sin(x / 23) + 3 * math.sin(x / 9 + 1)); y2 = int(238 + 5 * math.sin(x / 17 + 2))
    for y in range(y1, H): img[y][x] = P["colina"]
    for y in range(y2, H): img[y][x] = P["colina2"]
    if (x // 3) % 2 == 0: px(x, y1, P["nuvem"])
for y in range(252, H):
    for x in range(W):
        if rnd.random() < 0.025: img[y][x] = P["colina3"]
for (x, y) in [(18, 260), (38, 250), (58, 262), (78, 252), (420, 262), (440, 250), (460, 261)]: pegada(x, y, 2)

# gato dormindo numa nuvem (esquerda)
nuvem(92, 196, 92, 17)
gato_dormindo(96, 178, 3.2, P["branco"], P["nuvem2"])
for i, (zx, zy) in enumerate([(122, 152), (130, 143), (140, 133)]):     # zzz
    e = 1 + i // 2
    for k in range(3 * e + 1): px(zx + k, zy, P["rosa3"]); px(zx + k, zy + 3 * e, P["rosa3"]); px(zx + 3 * e - k, zy + k, P["rosa3"])

# filhote com novelo (centro-esquerda, acima da dock)
gato_sentado(210, 206, 2.2, P["caramelo"], P["caramelo2"], P["creme"], manchas=[(-3.5, -2.2, 2.0, P["creme"])], rabo_lado=-1)
NX, NY, NR = 246, 238, 8
for y in range(NY - NR, NY + NR + 1):
    for x in range(NX - NR, NX + NR + 1):
        if math.hypot(x - NX, y - NY) <= NR:
            c = P["rosa2"] if ((x - y) // 3) % 2 else P["rosa"]
            if math.hypot(x - NX, y - NY) > NR - 1.2: c = P["linha"]
            px(x, y, c)
for k in range(26): px(NX - NR - k, NY + 4 + int(2 * math.sin(k / 3)), P["rosa3"])                  # fio solto

# gato grande sentado (direita), creme com manchas caramelo
gato_sentado(372, 128, 7.2, P["creme"], P["creme2"], P["branco"],
             manchas=[(3.8, -2.8, 2.4, P["caramelo"]), (-4.6, 6.5, 2.2, P["caramelo"])])
coracao(302, 76, 2); coracao(454, 70, 1); coracao(318, 50, 1); coracao(438, 28, 2)
estrela(296, 118, 2); estrela(470, 140, 1)

# pétalas/confete rosa
for _ in range(40):
    x = rnd.randint(0, W - 1); y = rnd.randint(5, 215)
    if 300 < x < 450 and 60 < y < 230: continue
    px(x, y, P["rosa"] if rnd.random() < 0.7 else P["lavanda"])

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
    saida = sys.argv[1] if len(sys.argv) > 1 else "gatinhos.png"
    salvar(saida, int(sys.argv[2]) if len(sys.argv) > 2 else 4); print(saida)
