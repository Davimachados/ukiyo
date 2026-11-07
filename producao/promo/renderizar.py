#!/usr/bin/env python3
"""Vídeo promocional do Ukiyo 浮世 (1920×1080, 30 fps, 55 s) — motion graphics em camadas, gerado por código.

Camadas: papel de parede em 2,5D (paralaxe por profundidade estimada), partículas em pixel por tema, kanji gigante
pixelado, capturas reais do sistema como cartões 3D com sombra, tipografia animada e transições em dissolve Bayer.
Codificação na GPU (h264_vaapi). Requer o .venv do projeto (Pillow + NumPy).

Uso:
  .venv/bin/python producao/promo/renderizar.py <insumos> <saida.mp4> [--trilha trilha.wav] [--quadros 3.0,12.5]
  (<insumos>: pasta com as capturas — ver producao/promo/README.md; --quadros grava só PNGs de conferência)
"""
import argparse, glob, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, DUR = 1920, 1080, 30, 55.0
PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
FONTES_SIS = "/usr/share/fonts/truetype"
def _fonte(*cands):
    for c in cands:
        for p in glob.glob(c):
            return p
    return os.path.join(FONTES_SIS, "dejavu/DejaVuSans-Bold.ttf")
F_PIXEL = _fonte(f"{FONTES_SIS}/dotgothic16/DotGothic16-Regular.ttf")
F_TIT = _fonte(os.path.expanduser("~/.claude/skills/synced/*/canvas-design/canvas-fonts/Outfit-Bold.ttf"), f"{FONTES_SIS}/noto/NotoSans-Bold.ttf")
F_TXT = _fonte(os.path.expanduser("~/.claude/skills/synced/*/canvas-design/canvas-fonts/InstrumentSans-Regular.ttf"), f"{FONTES_SIS}/noto/NotoSans-Regular.ttf")
F_CJK = {"b": "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "r": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"}
F_MONO = _fonte(os.path.expanduser("~/.claude/skills/synced/*/canvas-design/canvas-fonts/DMMono-Regular.ttf"), f"{FONTES_SIS}/dejavu/DejaVuSansMono.ttf")

# ---- linha do tempo (segundos; compasso = 2,5 s a 96 BPM) -------------------------------------------------------
T_TEMAS, DUR_TEMA = 5.0, 5.0
T_TROCA, T_HENSHU, T_ESTUDIO, T_FIM = 30.0, 35.0, 42.5, 47.5
TEMAS = [  # id, nome, kanji, rótulo, frase, horizonte (fração), cor de destaque, partícula
    ("claro", "Washi", "夕", "claro", "O sol pousado no cume.", 0.60, (247, 176, 120), "petalas"),
    ("escuro", "Yoru", "夜", "escuro", "Mil torii rumo à luz.", 0.50, (232, 105, 74), "vagalumes"),
    ("marys", "Mary's", "眠", "kawaii", "Uma lua para sonhar.", 0.70, (236, 143, 174), "brilhos"),
    ("neontokyo", "Neon Tokyo", "雨", "cyberpunk", "Um letreiro na chuva.", 0.72, (255, 63, 164), "chuva"),
    ("touge", "Touge", "峠", "montanha", "A estrada ao anoitecer.", 0.52, (255, 122, 90), "rastros"),
]
PAPEIS = {"claro": "washi/wallpaper/diamante-refino-2026-11-07.png", "escuro": "yoru/wallpaper/senbon-refino-2026-11-07.png",
          "marys": "marys/wallpaper/movel-refino-2026-11-07.png", "neontokyo": "neontokyo/wallpaper/sinal-refino-2026-11-07.png",
          "touge": "touge/wallpaper/passagem-refino-2026-11-07.png"}
FUNDO = np.array([14, 12, 26], np.float32)
CREME = (242, 235, 221)

# ---- utilidades ---------------------------------------------------------------------------------------------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def e_out(x): return 1 - (1 - x) ** 3
def e_inout(x): return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def e_expo(x): return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def e_back(x, s=1.4): x -= 1; return 1 + (s + 1) * x ** 3 + s * x ** 2

B8 = np.array([[0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26], [12, 44, 4, 36, 14, 46, 6, 38],
               [60, 28, 52, 20, 62, 30, 54, 22], [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
               [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21]], np.float32) / 64 + 1 / 128
def bayer(h, w, bloco):
    """Limiar Bayer em blocos (para dissolves em pixel)."""
    ys = (np.arange(h) // bloco) % 8; xs = (np.arange(w) // bloco) % 8
    return B8[ys[:, None], xs[None, :]]
BAYER24 = bayer(H, W, 24)

def compor(fundo, rgba, x, y, alfa=1.0):
    """Compõe uma imagem RGBA (np float, 0–255) em (x, y) com opacidade extra."""
    h, w = rgba.shape[:2]; x0, y0 = int(round(x)), int(round(y))
    a0, b0 = max(0, x0), max(0, y0); a1, b1 = min(W, x0 + w), min(H, y0 + h)
    if a1 <= a0 or b1 <= b0 or alfa <= 0: return
    sub = rgba[b0 - y0:b1 - y0, a0 - x0:a1 - x0]
    a = sub[..., 3:4] / 255.0 * alfa
    fundo[b0:b1, a0:a1] = fundo[b0:b1, a0:a1] * (1 - a) + sub[..., :3] * a

def para_np(im): return np.asarray(im.convert("RGBA"), np.float32)

_cache_txt = {}
def texto(s, fonte, tam, cor=CREME, espac=0, pixel=False):
    """Texto renderizado em RGBA (cacheado). pixel=True: renderiza a 16 px e amplia sem suavizar."""
    k = (s, fonte, tam, cor, espac, pixel)
    if k in _cache_txt: return _cache_txt[k]
    if pixel:
        f = ImageFont.truetype(F_PIXEL, 16); esc = max(1, round(tam / 16))
        bb = f.getbbox(s); im = Image.new("L", (bb[2] + 4, 20), 0); d = ImageDraw.Draw(im); d.fontmode = "1"
        d.text((2, 0), s, font=f, fill=255); im = im.resize((im.width * esc, im.height * esc), Image.NEAREST)
    else:
        f = ImageFont.truetype(fonte, tam)
        fj = ImageFont.truetype(F_CJK["b" if fonte == F_TIT else "r"], int(tam * 0.92))   # japonês: Noto Sans CJK
        fo = lambda c: fj if ord(c) >= 0x2E80 else f
        larg = sum(fo(c).getlength(c) for c in s) + espac * max(0, len(s) - 1)
        asc, desc = f.getmetrics(); im = Image.new("L", (int(larg) + 8, asc + desc + 12), 0); d = ImageDraw.Draw(im)
        x = 4
        for c in s:
            dy = 4 + (int(tam * 0.06) if ord(c) >= 0x2E80 else 0)
            d.text((x, dy), c, font=fo(c), fill=255); x += fo(c).getlength(c) + espac
    rgba = np.zeros((im.height, im.width, 4), np.float32); rgba[..., :3] = cor; rgba[..., 3] = np.asarray(im, np.float32)
    _cache_txt[k] = rgba; return rgba

def revelar(fundo, rgba, x, y, p, sobe=24, alfa=1.0):
    """Entrada de texto: desliza para cima e revela da esquerda para a direita com borda suave."""
    if p <= 0: return
    q = e_out(p); h, w = rgba.shape[:2]
    corte = int(w * clamp(q * 1.15)); m = rgba.copy()
    if corte < w:
        borda = np.clip((corte - np.arange(w)) / 40.0, 0, 1)[None, :]
        m[..., 3] *= borda
    compor(fundo, m, x, y + (1 - q) * sobe, alfa * clamp(p * 2.2))

def dissolver_texto(fundo, rgba, x, y, p, bloco=8, alfa=1.0):
    """Entrada em dissolve Bayer (identidade pixel)."""
    if p <= 0: return
    h, w = rgba.shape[:2]; m = rgba.copy()
    m[..., 3] *= (bayer(h, w, bloco) < p)
    compor(fundo, m, x, y, alfa)

# ---- cartões 3D -----------------------------------------------------------------------------------------------------
def coef_persp(dst, src):
    """Coeficientes para Image.transform(PERSPECTIVE): mapeiam pontos de saída (dst) para a entrada (src)."""
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; b += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()

class Cartao:
    def __init__(self, im, raio=18, borda=(255, 255, 255, 90)):
        im = im.convert("RGBA"); w, h = im.size
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], raio, fill=255)
        im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(m))))
        ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], raio, outline=borda, width=2)
        self.im = im; self.w, self.h = w, h
        pad = 60; s = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
        ImageDraw.Draw(s).rounded_rectangle([pad, pad, pad + w, pad + h], raio, fill=150)
        self.sombra = s.filter(ImageFilter.GaussianBlur(26)); self.pad = pad

    def quad(self, cx, cy, escala, ry, rx, rz=0.0):
        """Cantos projetados de um retângulo girado em 3D (graus), centrado em (cx, cy)."""
        w, h = self.w * escala, self.h * escala; f = 1700.0
        ry, rx, rz = map(math.radians, (ry, rx, rz)); pts = []
        for (x, y) in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
            x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
            z = x * math.sin(ry); x = x * math.cos(ry)
            y2 = y * math.cos(rx) - z * math.sin(rx); z = y * math.sin(rx) + z * math.cos(rx)
            k = f / (f + z); pts.append((cx + x * k, cy + y2 * k))
        return pts

    def desenhar(self, fundo, cx, cy, escala=1.0, ry=0.0, rx=0.0, rz=0.0, alfa=1.0, sombra=1.0):
        if alfa <= 0.01: return
        q = self.quad(cx, cy, escala, ry, rx, rz)
        xs = [p[0] for p in q]; ys = [p[1] for p in q]
        x0, y0 = int(math.floor(min(xs))), int(math.floor(min(ys))); x1, y1 = int(math.ceil(max(xs))), int(math.ceil(max(ys)))
        if x1 < 0 or y1 < 0 or x0 > W or y0 > H: return
        if sombra > 0:   # sombra: mesmo quadrilátero, deslocado para baixo
            sq = [(x - x0 + 40, y - y0 + 40 + 30 * escala) for x, y in q]
            src = [(self.pad, self.pad), (self.pad + self.w, self.pad), (self.pad + self.w, self.pad + self.h), (self.pad, self.pad + self.h)]
            sw, sh = x1 - x0 + 80, y1 - y0 + 120
            s = self.sombra.transform((sw, sh), Image.PERSPECTIVE, coef_persp(sq, src), Image.BILINEAR)
            rgba = np.zeros((sh, sw, 4), np.float32); rgba[..., 3] = np.asarray(s, np.float32) * 0.85
            compor(fundo, rgba, x0 - 40, y0 - 40, alfa * sombra)
        dq = [(x - x0, y - y0) for x, y in q]
        src = [(0, 0), (self.w, 0), (self.w, self.h), (0, self.h)]
        im = self.im.transform((x1 - x0 + 1, y1 - y0 + 1), Image.PERSPECTIVE, coef_persp(dq, src), Image.BICUBIC)
        compor(fundo, para_np(im), x0, y0, alfa)

# ---- papel de parede em 2,5D --------------------------------------------------------------------------------------
class Paralaxe:
    def __init__(self, caminho, horizonte):
        im = Image.open(caminho).convert("RGB"); esc = 1.28 * W / im.width
        im = im.resize((int(im.width * esc), int(im.height * esc)), Image.BICUBIC)
        self.a = np.asarray(im, np.float32); self.h, self.w = self.a.shape[:2]
        y = np.arange(H) / H
        self.prof = np.where(y > horizonte, np.clip((y - horizonte) / (1 - horizonte), 0, 1) ** 1.2, 0.08 * (1 - y / horizonte) + 0.02)
        self.xs = np.arange(W, dtype=np.float32) - W / 2

    def quadro(self, t, desloc=(0.0, 0.0), zoom=1.0):
        """t ∈ [0,1]: câmera desliza e se aproxima; linhas próximas (prof→1) andam e crescem mais."""
        cx, cy = self.w / 2 + desloc[0], self.h / 2 + desloc[1]
        pan = (t - 0.5) * 120                                   # deslocamento lateral da câmera
        z = zoom * (1.0 + 0.05 * t) * (1 + 0.10 * t * self.prof)  # aproximação maior nas linhas próximas
        ys = np.clip(cy + (np.arange(H) - H / 2) / z - 12 * self.prof * t, 0, self.h - 1)
        xsrc = cx + pan * (0.25 + 0.75 * self.prof)[:, None] + self.xs[None, :] / z[:, None]
        xsrc = np.clip(xsrc, 0, self.w - 2); x0 = xsrc.astype(np.int32); fr = (xsrc - x0)[..., None]
        yi = ys.astype(np.int32)[:, None]
        return self.a[yi, x0] * (1 - fr) + self.a[yi, x0 + 1] * fr

# ---- partículas em pixel ------------------------------------------------------------------------------------------
RNG = np.random.default_rng(15)
PART = {k: RNG.random((90, 4)) for k in ("petalas", "vagalumes", "brilhos", "chuva", "rastros", "intro")}
def particulas(fundo, tipo, t, alfa=1.0):
    P = PART[tipo]
    if tipo == "chuva":
        for i, (a, b, c, d) in enumerate(P):
            x = (a * W + t * 260) % W; y = (b * H + t * (900 + 500 * c)) % H; L = int(18 + 30 * c)
            xi, yi = int(x), int(y)
            for k in range(0, L, 4):
                xx, yy = xi + k // 3, yi + k
                if 0 <= xx < W - 4 and 0 <= yy < H - 4: fundo[yy:yy + 4, xx:xx + 2] = fundo[yy:yy + 4, xx:xx + 2] * (1 - 0.45 * alfa) + np.array([200, 190, 255]) * 0.45 * alfa
        return
    if tipo == "rastros":
        for i, (a, b, c, d) in enumerate(P[:14]):
            y = int(H * (0.55 + 0.4 * b)); comp = 260 + 300 * c; x = ((t * (500 + 400 * a) + d * 3000) % (W + comp)) - comp
            cor = np.array([255, 70, 60]) if i % 3 else np.array([255, 240, 210])
            x0, x1 = int(max(0, x)), int(min(W, x + comp))
            if x1 > x0:
                g = np.linspace(0, 1, x1 - x0)[:, None] ** 2 * 0.8 * alfa
                fundo[y:y + 4, x0:x1] = fundo[y:y + 4, x0:x1] * (1 - g) + cor * g
        return
    for i, (a, b, c, d) in enumerate(P):
        if tipo == "petalas":
            x = (a * W + t * (90 + 60 * c) + 40 * math.sin(t * 1.3 + d * 6)) % W; y = (b * H + t * (70 + 50 * d)) % H
            s = 8 if c > 0.6 else 4; cor = (251, 201, 214) if c > 0.3 else (238, 147, 174); op = 0.9
        elif tipo == "vagalumes":
            x = (a * W + 30 * math.sin(t * 0.7 + d * 9)) % W; y = (b * H - t * (14 + 20 * c)) % H
            s = 4 if c < 0.7 else 8; cor = (255, 211, 138); op = 0.5 + 0.5 * math.sin(t * (2 + 3 * d) + a * 9)
        elif tipo == "brilhos":
            x, y = a * W, b * H * 0.85; s = 4; cor = (255, 250, 240); op = max(0, math.sin(t * (1.5 + 2 * c) + d * 12)) ** 3
        else:   # intro
            x = a * W; y = (b * H - t * 30 * (0.3 + c)) % H; s = 4; cor = (217, 164, 65) if d > 0.8 else (120, 110, 160); op = 0.35 + 0.3 * math.sin(t * 2 + a * 7)
        xi, yi = int(x), int(y)
        if 0 <= xi < W - s and 0 <= yi < H - s:
            o = op * alfa; fundo[yi:yi + s, xi:xi + s] = fundo[yi:yi + s, xi:xi + s] * (1 - o) + np.array(cor) * o

def vinheta_e_grao(fundo, t):
    fundo *= VINHETA
    g = GRAO[int(t * FPS) % len(GRAO)]
    fundo += g

# ---- insumos (carregados uma vez por processo) ----------------------------------------------------------------------
A = {}
def carregar(insumos):
    global VINHETA, GRAO
    yy, xx = np.mgrid[0:H, 0:W]; r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    VINHETA = (1 - 0.32 * np.clip(r - 0.35, 0, 1) ** 1.5)[..., None].astype(np.float32)
    rg = np.random.default_rng(3); GRAO = [rg.normal(0, 3.2, (H, W, 1)).astype(np.float32) for _ in range(6)]
    A["par"] = {t[0]: Paralaxe(os.path.join(PROJ, "themes", PAPEIS[t[0]]), t[5]) for t in TEMAS}
    cap = lambda n: Image.open(os.path.join(insumos, n))
    A["desk"] = {t[0]: Cartao(cap(f"desk-{t[0]}.png"), raio=22) for t in TEMAS}
    A["desk_np"] = {t[0]: np.asarray(cap(f"desk-{t[0]}.png").convert("RGB"), np.float32) for t in TEMAS}
    j = {t: cap(f"janelas-{t}.png") for t in ("claro", "marys", "neontokyo")}
    A["henshu"] = Cartao(j["neontokyo"].crop((860, 60, 1890, 1000)), raio=14)
    A["henshu_zoom"] = Cartao(j["neontokyo"].crop((1440, 110, 1890, 700)), raio=14)
    A["dolphin"] = Cartao(j["marys"].crop((40, 60, 820, 530)), raio=14)
    A["konsole"] = Cartao(j["claro"].crop((40, 560, 820, 1000)), raio=14)
    A["kdenlive"] = Cartao(cap("kdenlive-escuro.png").crop((0, 30, 1920, 1040)), raio=16)
    A["tela"] = Cartao(cap("tela-touge.png").crop((730, 200, 1190, 860)), raio=14)
    A["barra"] = Cartao(cap("desk-neontokyo.png").crop((1060, 0, 1920, 34)), raio=8)
    A["spotify"] = Cartao(Image.open(os.path.join(PROJ, "widgets/spotify/preview/widget-demo.png")), raio=14)
    # vídeo vertical exportado pelo Henshū (para o celular)
    v = os.path.join(insumos, "henshu-vertical.mp4"); w_, h_ = 360, 640
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-vf", f"fps={FPS},scale={w_}:{h_}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    A["video"] = np.frombuffer(raw, np.uint8).reshape(-1, h_, w_, 3)
    ph = Image.new("RGBA", (w_ + 36, h_ + 36), 0); d = ImageDraw.Draw(ph)
    d.rounded_rectangle([0, 0, w_ + 35, h_ + 35], 46, fill=(18, 16, 28, 255), outline=(90, 84, 120, 255), width=3)
    A["celular"] = ph

# ---- cenas --------------------------------------------------------------------------------------------------------
def cena_intro(f, t):
    f[:] = FUNDO; particulas(f, "intro", t)
    k = texto("浮世", F_PIXEL, 16 * 22, CREME, pixel=True)
    dissolver_texto(f, k, (W - k.shape[1]) / 2, 250 - 30 * e_out(prog(t, 0.4, 3.5)), prog(t, 0.5, 2.0), bloco=22)
    tit = texto("U K I Y O", F_TIT, 64, CREME, espac=10)
    revelar(f, tit, (W - tit.shape[1]) / 2, 700, prog(t, 1.9, 2.9))
    sub = texto("Debian + KDE Plasma, redesenhado em pixel art", F_TXT, 36, (217, 164, 65))
    revelar(f, sub, (W - sub.shape[1]) / 2, 800, prog(t, 2.6, 3.6))
    linha = int(560 * e_out(prog(t, 2.2, 3.4)))
    if linha: f[786:788, W // 2 - linha // 2:W // 2 + linha // 2] = np.array([217, 164, 65], np.float32)
    if t > 4.5:   # dissolve para os temas
        p = prog(t, 4.5, 5.0); m = (BAYER24 < p)[..., None]
        f[:] = np.where(m, A["par"]["claro"].quadro(0.0), f)

def cena_tema(f, t, i):
    tid, nome, kanji, rot, frase, _, cor, part = TEMAS[i]
    tl = t - (T_TEMAS + i * DUR_TEMA); u = tl / DUR_TEMA
    f[:] = A["par"][tid].quadro(u)
    # escurece a esquerda para o texto (gradiente)
    f *= 0.58 if tid == "marys" else 0.72                                      # profundidade (tema claro: mais escuro)
    f[:, :1100] *= (0.45 + 0.55 * np.linspace(0, 1, 1100) ** 0.8)[None, :, None]
    particulas(f, part, tl + i * 7)
    k = texto(kanji, F_PIXEL, 16 * 30, cor, pixel=True)    # kanji grande em pixel, atrás do cartão (paralaxe lenta)
    compor(f, k, 1130 + 30 * u, 160 - 18 * u, 0.16 * clamp(tl * 2))
    # cartão do desktop entra pela direita e flutua
    pe = e_out(prog(tl, 0.15, 1.3)); flt = math.sin(tl * 1.4) * 6
    A["desk"][tid].desenhar(f, 1380 + 500 * (1 - pe), 560 + flt, 0.46 + 0.02 * u, ry=-24 + 8 * pe + 4 * u, rx=4, rz=-1.5,
                            alfa=clamp(pe * 1.4))
    cnt = texto(f"0{i + 1} / 05   TEMAS", F_MONO, 22, (200, 194, 214))
    revelar(f, cnt, 140, 300, prog(tl, 0.3, 0.9))
    tn = texto(nome, F_TIT, 128, CREME)
    revelar(f, tn, 132, 350, prog(tl, 0.45, 1.25), sobe=40)
    jp = texto(f"{kanji}  ·  {rot}", F_TXT, 40, cor)
    revelar(f, jp, 140, 520, prog(tl, 0.75, 1.5))
    fr = texto(frase, F_TXT, 46, CREME)
    revelar(f, fr, 140, 600, prog(tl, 1.0, 1.9))
    # saída: dissolve Bayer para o próximo tema (ou para a cena seguinte)
    if tl > DUR_TEMA - 0.5:
        p = prog(tl, DUR_TEMA - 0.5, DUR_TEMA); m = (BAYER24 < p)[..., None]
        prox = A["par"][TEMAS[i + 1][0]].quadro(0.0) if i < 4 else FUNDO
        f[:] = np.where(m, prox, f)

def cena_troca(f, t):
    tl = t - T_TROCA; f[:] = FUNDO
    ids = [x[0] for x in TEMAS]; k = int(tl / 0.42) % 5; p = (tl % 0.42) / 0.42
    fundo = A["desk_np"][ids[k]]
    f[:] = fundo * 0.35 + FUNDO * 0.65
    if p < 0.18: f[:] = f * (1 - (0.18 - p) * 2.2) + 255 * (0.18 - p) * 1.0   # flash a cada troca
    for j, d in enumerate((2, 1, 0)):   # pilha de desktops atrás
        kk = (k + d) % 5; pe = e_out(prog(tl, 0.1 * j, 0.8 + 0.1 * j))
        A["desk"][ids[kk]].desenhar(f, 1250 + 70 * d, 560 - 40 * d, 0.42 - 0.03 * d, ry=-20, rx=6, alfa=pe * (1 - 0.25 * d))
    A["tela"].desenhar(f, 470, 590, 0.95, ry=14, rx=2, alfa=e_out(prog(tl, 0.2, 1.0)))
    A["barra"].desenhar(f, 470, 170, 0.95, alfa=e_out(prog(tl, 0.5, 1.2)))
    t1 = texto("Troque de tema em menos de 1 segundo.", F_TIT, 58, CREME)
    revelar(f, t1, (W - t1.shape[1]) / 2 + 180, 880, prog(tl, 0.4, 1.3))
    t2 = texto("papel de parede · ícones · janelas · tela de bloqueio — num clique", F_TXT, 30, (200, 194, 214))
    revelar(f, t2, (W - t2.shape[1]) / 2 + 180, 960, prog(tl, 0.8, 1.6))
    if tl > 4.6:
        p = prog(tl, 4.6, 5.0); f[:] = f * (1 - p) + FUNDO * p

def cena_henshu(f, t):
    tl = t - T_HENSHU; f[:] = FUNDO
    par = A["par"]["neontokyo"].quadro(0.3 + 0.05 * tl / 7.5); f[:] = par * 0.22 + FUNDO * 0.78
    particulas(f, "intro", t, 0.6)
    if tl < 3.8:   # janela do Henshū em perspectiva, depois aproxima no chat
        pe = e_out(prog(tl, 0.1, 1.1)); z = e_inout(prog(tl, 1.8, 3.6))
        A["henshu"].desenhar(f, 1230 - 120 * z, 560 + 40 * z, 0.74 + 0.22 * z, ry=-16 * (1 - z) - 4, rx=3, alfa=pe * (1 - prog(tl, 3.4, 3.8)))
        A["henshu_zoom"].desenhar(f, 1330, 560, 1.15, ry=-6, alfa=prog(tl, 3.2, 3.6) * (1 - prog(tl, 3.6, 3.8)))
        t1 = texto("Henshū 編集", F_TIT, 104, CREME); revelar(f, t1, 120, 330, prog(tl, 0.3, 1.1), sobe=36)
        t2 = texto("Edite vídeos conversando.", F_TXT, 50, CREME); revelar(f, t2, 126, 480, prog(tl, 0.7, 1.5))
        t3 = texto("Claude ou Codex editam — você assiste.", F_TXT, 36, (120, 214, 236)); revelar(f, t3, 126, 560, prog(tl, 1.1, 1.9))
    else:          # celular tocando o vídeo exportado + recursos
        tc = tl - 3.8; pe = e_back(prog(tc, 0.0, 0.8))
        fi = min(len(A["video"]) - 1, int(tc * FPS)); ph = A["celular"].copy()
        ph.paste(Image.fromarray(A["video"][fi]), (18, 18))
        m = Image.new("L", ph.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, ph.width - 1, ph.height - 1], 46, fill=255)
        ph.putalpha(m); cel = Cartao(ph, raio=46, borda=(0, 0, 0, 0))
        cel.desenhar(f, 1340, 545, 1.08 * pe, ry=-12 + 8 * prog(tc, 0, 3.7), rx=3, alfa=clamp(pe))
        t1 = texto("Do bruto ao vídeo pronto", F_TIT, 70, CREME); revelar(f, t1, 120, 250, prog(tc, 0.1, 0.8))
        itens = [("文", "Transcrição local, sem internet"), ("字", "Legendas automáticas — até karaokê"),
                 ("縦", "Vertical 9:16 e horizontal 16:9"), ("編", "Abre no Kdenlive para o ajuste fino")]
        for n, (kj, s) in enumerate(itens):
            p = prog(tc, 0.5 + 0.35 * n, 1.2 + 0.35 * n)
            dissolver_texto(f, texto(kj, F_PIXEL, 48, (217, 164, 65), pixel=True), 124, 400 + n * 110, p, bloco=6)
            revelar(f, texto(s, F_TXT, 42, CREME), 210, 404 + n * 110, p)
    if tl > 7.0:
        p = prog(tl, 7.0, 7.5); f[:] = f * (1 - p) + FUNDO * p

def cena_estudio(f, t):
    tl = t - T_ESTUDIO; f[:] = FUNDO
    par = A["par"]["escuro"].quadro(0.6); f[:] = par * 0.2 + FUNDO * 0.8
    pe = e_out(prog(tl, 0.0, 1.0)); pk = e_out(prog(tl, 0.35, 1.3))
    A["kdenlive"].desenhar(f, 1390, 500, 0.44 + 0.03 * tl / 5, ry=-22 + 6 * pe, rx=6, alfa=pe)
    A["konsole"].desenhar(f, 1600, 820, 0.56, ry=-14, rx=4, alfa=pk)
    t1 = texto("Estúdio na GPU", F_TIT, 96, CREME); revelar(f, t1, 120, 300, prog(tl, 0.2, 1.0), sobe=36)
    t2 = texto("FFmpeg + VA-API · OBS · Kdenlive", F_TXT, 40, (120, 214, 236)); revelar(f, t2, 126, 430, prog(tl, 0.6, 1.4))
    t3 = texto("tiktok — da pasta ao export em −14 LUFS", F_MONO, 30, (200, 194, 214)); revelar(f, t3, 126, 500, prog(tl, 0.9, 1.7))
    if tl > 4.5:
        p = prog(tl, 4.5, 5.0); f[:] = f * (1 - p) + FUNDO * p

def cena_fim(f, t):
    tl = t - T_FIM; f[:] = FUNDO; particulas(f, "intro", t)
    ids = [x[0] for x in TEMAS]
    for j, tid in enumerate(ids):   # leque 3D de desktops
        pe = e_out(prog(tl, 0.1 * j, 1.0 + 0.1 * j)); ang = (j - 2) * 16 * pe
        A["desk"][tid].desenhar(f, W / 2 + (j - 2) * 230 * pe, 640 + abs(j - 2) * 30 * pe, 0.34, ry=-(j - 2) * 14 * pe + 4 * math.sin(tl * 0.8),
                                rx=10, rz=ang * 0.35, alfa=pe * 0.95)
    f[:420] *= np.linspace(0.35, 1.0, 420)[:, None, None]
    k = texto("浮世", F_PIXEL, 16 * 9, CREME, pixel=True); dissolver_texto(f, k, W / 2 - k.shape[1] - 30, 120, prog(tl, 0.8, 1.8), bloco=9)
    tt = texto("Ukiyo", F_TIT, 128, CREME); revelar(f, tt, W / 2 + 10, 120, prog(tl, 1.2, 2.0))
    t2 = texto("Código aberto · GPL-3.0 · arte CC BY-SA 4.0", F_TXT, 34, (217, 164, 65)); revelar(f, t2, (W - t2.shape[1]) / 2, 300, prog(tl, 1.8, 2.6))
    t3 = texto("github.com/Davimachados/ukiyo", F_MONO, 40, CREME); revelar(f, t3, (W - t3.shape[1]) / 2, 960, prog(tl, 2.4, 3.2))
    if tl > 6.3:
        p = prog(tl, 6.3, 7.5); f[:] = f * (1 - p)

def quadro(n):
    t = n / FPS; f = np.empty((H, W, 3), np.float32)
    if t < T_TEMAS: cena_intro(f, t)
    elif t < T_TROCA: cena_tema(f, t, min(4, int((t - T_TEMAS) / DUR_TEMA)))
    elif t < T_HENSHU: cena_troca(f, t)
    elif t < T_ESTUDIO: cena_henshu(f, t)
    elif t < T_FIM: cena_estudio(f, t)
    else: cena_fim(f, t)
    vinheta_e_grao(f, t)
    return np.clip(f, 0, 255).astype(np.uint8).tobytes()

def _init(insumos):
    carregar(insumos)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("insumos"); ap.add_argument("saida")
    ap.add_argument("--trilha"); ap.add_argument("--quadros"); ap.add_argument("--processos", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    a = ap.parse_args()
    if a.quadros:
        carregar(a.insumos)
        for t in a.quadros.split(","):
            Image.frombytes("RGB", (W, H), quadro(int(float(t) * FPS))).save(f"{a.saida}-{float(t):05.1f}.png")
        return
    total = int(DUR * FPS)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-vaapi_device", "/dev/dri/renderD128",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if a.trilha: cmd += ["-i", a.trilha]
    cmd += ["-vf", "format=nv12,hwupload", "-c:v", "h264_vaapi", "-profile:v", "high", "-rc_mode", "VBR", "-b:v", "14M", "-maxrate", "20M", "-g", "60"]
    if a.trilha: cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-movflags", "+faststart", a.saida]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(a.processos, initializer=_init, initargs=(a.insumos,)) as pool:
        for n, buf in enumerate(pool.imap(quadro, range(total), chunksize=6)):
            ff.stdin.write(buf)
            if n % 150 == 0: print(f"  quadro {n}/{total}", flush=True)
    ff.stdin.close(); ff.wait()
    print("pronto:", a.saida)

if __name__ == "__main__":
    main()
