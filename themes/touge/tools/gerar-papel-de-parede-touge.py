#!/usr/bin/env python3
"""Papel de parede "Touge 峠 — curva da montanha" — pixel art noturna gerada por código (sem dependências).

Estrada de montanha com curva em grampo (faixa amarela, bordas brancas, guard-rail com refletores), dois carros
esportivos genéricos em drift (sem marcas) com fumaça dos pneus, faróis e lanternas, cidade iluminada no vale,
montanhas, estrelas, placa amarela de curva e o nome "TOUGE". 480x270 ampliado (x4 = 1920x1080). Determinístico.
Uso: gerar-papel-de-parede-touge.py SAIDA.png [escala]
"""
import math, random, struct, sys, zlib

W, H = 480, 270
rnd = random.Random(1983)
def hx(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
P = {k: hx(v) for k, v in {
    "ceu0": "#06070C", "ceu1": "#0B0E18", "ceu2": "#121726", "ceu3": "#1B2134",
    "estrela": "#E8E8F0", "estrela2": "#7C8299",
    "mont1": "#151A28", "mont2": "#10131E", "mont3": "#0B0D15", "mata": "#0E1410", "mata2": "#131B15",
    "cidade1": "#FF8A1E", "cidade2": "#FFD27A", "cidade3": "#F2F2F0", "cidade4": "#E8243C",
    "asfalto": "#24262C", "asfalto2": "#1D1F24", "borda": "#E8E8E4", "amarelo": "#F5C400",
    "trilho": "#9A9EA6", "trilho2": "#5E626A", "refletor": "#E8243C",
    "branco": "#F2F2F0", "branco2": "#C9CACC", "preto": "#141416", "preto2": "#2A2B30",
    "vermelho": "#D7141E", "vermelho2": "#8E0B12", "vidro": "#3A4A66", "vidro2": "#6E86A8",
    "pneu": "#0A0A0C", "aro": "#8C9098", "farol": "#FFF7D6", "lanterna": "#FF2A3A",
    "fumaca": "#C8CCD4", "fumaca2": "#8E939E", "contorno": "#08080A",
    "placa": "#F5C400", "placa2": "#141416", "poste": "#6E727A",
}.items()}
img = [[P["ceu0"]] * W for _ in range(H)]
def px(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H: img[y][x] = c
def mix(a, b, t): return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
def misturar(x, y, c, t):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H: img[y][x] = mix(img[y][x], c, t)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

# ---------- céu e estrelas ----------
faixas = [P[f"ceu{i}"] for i in range(4)]
for y in range(150):
    t = (y / 149) ** 1.2 * (len(faixas) - 1)
    i = min(int(t), len(faixas) - 2); f = t - i
    g = max(0.0, (f - 0.78) / 0.22)
    for x in range(W): img[y][x] = faixas[i + 1] if g * 16 > BAYER[y % 4][x % 4] + 0.5 else faixas[i]
for _ in range(110):
    x = rnd.randint(0, W - 1); y = int(rnd.random() ** 1.6 * 100)
    px(x, y, P["estrela"] if rnd.random() < 0.3 else P["estrela2"])

# ---------- montanhas ao fundo e cidade no vale ----------
def cordilheira(base, amp, freq, fase, cor):
    for x in range(W):
        y0 = int(base - amp * (0.6 * math.sin(x / freq + fase) + 0.4 * math.sin(x / (freq * 0.43) + fase * 2)))
        for y in range(y0, H): img[y][x] = cor
cordilheira(110, 22, 40, 0.5, P["mont1"])
# cidade no vale (faixa de luzes entre as montanhas do fundo e as da frente)
for _ in range(1300):
    x = rnd.randint(0, W - 1)
    if rnd.random() > 0.35 + 0.65 * math.sin(math.pi * x / W): continue      # rareia nas pontas
    y = 118 + int(rnd.random() ** 0.8 * 26) + int(6 * math.sin(x / 50))
    if True:
        c = rnd.choice([P["cidade1"], P["cidade1"], P["cidade2"], P["cidade3"], P["cidade4"]])
        px(x, y, c)
        if rnd.random() < 0.12: misturar(x, y - 1, c, 0.4)
cordilheira(150, 14, 30, 2.0, P["mont2"])
cordilheira(175, 10, 22, 4.1, P["mont3"])
def cume(base, amp, freq, fase, x): return int(base - amp * (0.6 * math.sin(x / freq + fase) + 0.4 * math.sin(x / (freq * 0.43) + fase * 2)))

# ---------- estrada em grampo ----------
def bezier(p0, p1, p2, p3, n):
    pts = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        pts.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return pts
trecho1 = bezier((520, 262), (360, 250), (120, 250), (70, 214), 140)       # perto, entrando na curva
trecho2 = bezier((70, 214), (30, 186), (110, 166), (210, 160), 110)        # o grampo
trecho3 = bezier((210, 160), (300, 155), (390, 150), (500, 148), 110)      # subindo, longe
caminho = trecho1 + trecho2[1:] + trecho3[1:]
N = len(caminho)
def largura(i): return 9 + 26 * (1 - i / (N - 1)) ** 1.4                    # perspectiva: mais larga perto
# terreno da encosta (grama escura) sob a estrada
for x in range(W):                                                            # encosta segue o cume da frente
    for y in range(cume(182, 8, 26, 1.3, x), H): img[y][x] = P["mata"] if (x // 5 + y // 4) % 3 else P["mata2"]
for i, (x, y) in enumerate(caminho):                                         # asfalto
    r = largura(i)
    for yy in range(int(y - r * 0.55) - 1, int(y + r * 0.55) + 2):
        for xx in range(int(x - r) - 1, int(x + r) + 2):
            if ((xx - x) / r) ** 2 + ((yy - y) / (r * 0.55)) ** 2 <= 1:
                px(xx, yy, P["asfalto"] if (xx // 4 + yy // 2) % 2 else P["asfalto2"])
def normal(i):
    a = caminho[max(0, i - 1)]; b = caminho[min(N - 1, i + 1)]
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
    return -dy / L, dx / L
for i, (x, y) in enumerate(caminho):                                         # bordas brancas e faixa amarela
    r = largura(i); nx, ny = normal(i)
    for lado in (-1, 1):
        px(x + lado * nx * r * 0.92, y + lado * ny * r * 0.5, P["borda"])
    if (i // 5) % 2 == 0: px(x, y, P["amarelo"]); px(x + 1, y, P["amarelo"]) if r > 20 else None
# guard-rail no lado externo do grampo (com refletores vermelhos)
for i in range(110, 250):
    x, y = caminho[i]; r = largura(i); nx, ny = normal(i)
    gx, gy = x - nx * (r + 4), y - ny * (r * 0.5 + 3)
    px(gx, gy, P["trilho"]); px(gx, gy + 1, P["trilho2"])
    if i % 9 == 0:
        for k in range(2, 6): px(gx, gy + k, P["trilho2"])
        px(gx, gy - 1, P["refletor"])

# placa amarela de curva (losango)
PX, PY = 40, 150
for k in range(0, 18): px(PX, PY + k, P["poste"])
for y in range(-7, 8):
    for x in range(-7, 8):
        if abs(x) + abs(y) <= 7: px(PX + x, PY - 6 + y, P["placa2"] if abs(x) + abs(y) == 7 else P["placa"])
for k in range(-3, 4): px(PX + k, PY - 6 - (2 if k < 0 else 2 - k), P["placa2"])             # seta de curva
px(PX + 3, PY - 7, P["placa2"]); px(PX + 3, PY - 5, P["placa2"]); px(PX - 3, PY - 3, P["placa2"]); px(PX - 3, PY - 2, P["placa2"])

# ---------- carros (sprites por formas, contorno automático) ----------
class Sprite:
    def __init__(self): self.p = {}
    def poligono(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            for k in range(len(pts)):
                (x1, y1), (x2, y2) = pts[k], pts[(k + 1) % len(pts)]
                if (y1 <= y < y2) or (y2 <= y < y1): xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(int(round(a)), int(round(b)) + 1): self.p[(x, y)] = c
    def elipse(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1: self.p[(x, y)] = c
    def desenhar(self):
        borda = {(x + dx, y + dy) for (x, y) in self.p for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - set(self.p)
        for (x, y) in borda: px(x, y, P["contorno"])
        for (x, y), c in self.p.items(): px(x, y, c)

def carro(x, y, s, corpo, corpo2, faixa, angulo=0.0):
    """Cupê esportivo genérico de perfil (frente à esquerda), levemente inclinado (drift)."""
    sp = Sprite()
    def T(px_, py_):                                         # escala + inclinação
        X = px_ * s; Y = py_ * s
        return (x + X * math.cos(angulo) - Y * math.sin(angulo), y + X * math.sin(angulo) + Y * math.cos(angulo))
    sp.poligono([T(0, 7), T(3, 5), T(9, 4.6), T(27, 4.4), T(31, 5.2), T(31, 9.6), T(0.5, 9.6)], corpo)   # carroceria
    sp.poligono([T(9, 4.7), T(12.5, 1.2), T(21, 1.0), T(25.5, 4.5)], corpo)                               # cabine
    sp.poligono([T(10.6, 4.4), T(13.2, 1.9), T(17.2, 1.8), T(17.2, 4.4)], P["vidro"])                    # vidro dianteiro
    sp.poligono([T(18.2, 4.4), T(18.2, 1.8), T(20.6, 1.8), T(23.8, 4.4)], P["vidro2"])                   # vidro traseiro
    sp.poligono([T(1, 7.4), T(31, 7.0), T(31, 7.9), T(1, 8.3)], faixa)                                    # faixa racing
    sp.poligono([T(0.5, 8.8), T(31, 8.8), T(31, 9.6), T(0.5, 9.6)], corpo2)                              # saia (sombra)
    sp.poligono([T(26.5, 3.4), T(31.5, 3.0), T(31.5, 3.8), T(26.5, 4.2)], P["preto"])                    # aerofólio
    for cx in (6.5, 24.5):                                                                                # rodas
        c = T(cx, 9.6); sp.elipse(c[0], c[1], 2.6 * s, 2.6 * s, P["pneu"]); sp.elipse(c[0], c[1], 1.3 * s, 1.3 * s, P["aro"])
    f = T(0.6, 6.6); sp.elipse(f[0], f[1], 0.9 * s, 0.6 * s, P["farol"])                                  # farol
    l = T(30.6, 6.0); sp.elipse(l[0], l[1], 0.7 * s, 0.6 * s, P["lanterna"])                              # lanterna
    sp.desenhar()
    return T

def fumaca(cx, cy, raio, n, direcao=1):
    for k in range(n):
        r = raio * (0.6 + k * 0.18); ox = cx + direcao * k * raio * 0.9 + rnd.uniform(-2, 2); oy = cy - k * raio * 0.25 + rnd.uniform(-1, 1)
        for y in range(int(oy - r), int(oy + r) + 1):
            for x in range(int(ox - r * 1.3), int(ox + r * 1.3) + 1):
                d = ((x - ox) / (r * 1.3)) ** 2 + ((y - oy) / r) ** 2
                if d <= 1:
                    t = 0.55 * (1 - d) * (1 - k / (n + 1)) + 0.12
                    if (x + y) % 2 == 0 or d < 0.5: misturar(x, y, P["fumaca"] if d < 0.45 else P["fumaca2"], t)

def facho(x0, y0, comp, abertura, cor, direcao=-1):
    for k in range(1, comp):
        w = k * abertura
        for d in range(-int(w), int(w) + 1):
            misturar(x0 + direcao * k, y0 + d * 0.5, cor, 0.22 * (1 - k / comp))

# carro de trás (preto/amarelo), menor, no topo do grampo
fumaca(206, 158, 4, 5, 1)
Tb = carro(176, 146, 0.95, P["preto"], P["preto2"], P["amarelo"], angulo=-0.12)
facho(*Tb(0.2, 6.6), 30, 0.35, P["farol"])
# carro da frente (branco/vermelho), saindo da curva, grande
fumaca(214, 238, 7, 6, 1)
Ta = carro(122, 214, 2.1, P["branco"], P["branco2"], P["vermelho"], angulo=-0.10)
facho(*Ta(0.2, 6.6), 60, 0.32, P["farol"])
for k in range(1, 26): misturar(Ta(31.2, 6.0)[0] + k, Ta(31.2, 6.0)[1] + k * 0.12, P["lanterna"], 0.35 * (1 - k / 26))   # rastro da lanterna

# ---------- nome "TOUGE" (5x7) ----------
FONTE = {"T": ["xxxxx", "..x..", "..x..", "..x..", "..x..", "..x..", "..x.."],
         "O": [".xxx.", "x...x", "x...x", "x...x", "x...x", "x...x", ".xxx."],
         "U": ["x...x", "x...x", "x...x", "x...x", "x...x", "x...x", ".xxx."],
         "G": [".xxxx", "x....", "x....", "x.xxx", "x...x", "x...x", ".xxx."],
         "E": ["xxxxx", "x....", "x....", "xxxx.", "x....", "x....", "xxxxx"]}
def texto(t, x0, y0, e=3):
    x = x0
    for ch in t:
        g = FONTE[ch]
        for camada, (dx, dy, cor) in enumerate(((1, 1, P["vermelho"]), (0, 0, P["branco"]))):
            for yy, l in enumerate(g):
                for xx, c in enumerate(l):
                    if c == "x":
                        for a in range(e):
                            for b in range(e): px(x + xx * e + a + dx, y0 + yy * e + b + dy, cor)
        x += 6 * e
texto("TOUGE", 22, 18, 3)
for k in range(0, 87, 6):                                                    # faixa quadriculada sob o nome
    for a in range(3):
        for b in range(3): px(22 + k + a, 44 + b, P["branco"]); px(25 + k + a, 47 + b, P["branco"])

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
    saida = sys.argv[1] if len(sys.argv) > 1 else "touge.png"
    salvar(saida, int(sys.argv[2]) if len(sys.argv) > 2 else 4); print(saida)
