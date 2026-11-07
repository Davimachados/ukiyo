"""pixelarte — base comum dos papéis de parede "Ma Pixel 間" (ver docs/visual/filosofia-papeis-de-parede.md).

Desenha numa tela pequena (480×270) com paleta curta e dithering ordenado (Bayer 8×8), e amplia ×4 por
vizinho mais próximo para 1920×1080 — pixel nítido, sem suavização.
Requer o ambiente do projeto: .venv/bin/python (Pillow + NumPy).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, ESCALA = 480, 270, 4
FONTE_PIXEL = "/usr/share/fonts/truetype/dotgothic16/DotGothic16-Regular.ttf"

_B2 = np.array([[0, 2], [3, 1]])
def _bayer(n):
    m = _B2
    while m.shape[0] < n:
        m = np.block([[4 * m, 4 * m + 2], [4 * m + 3, 4 * m + 1]])
    return (m + 0.5) / m.size
BAYER = _bayer(8)


def hexrgb(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def limiar(w=W, h=H, dx=0, dy=0):
    """Matriz de limiares Bayer do tamanho da tela (deslocável)."""
    ys = (np.arange(h)[:, None] + dy) % 8; xs = (np.arange(w)[None, :] + dx) % 8
    return BAYER[ys, xs]


class Tela:
    def __init__(self, w=W, h=H, fundo="#000000"):
        self.w, self.h = w, h
        self.px = np.zeros((h, w, 3), np.float32); self.px[:] = hexrgb(fundo)
        self.T = limiar(w, h)
        self.yy, self.xx = np.mgrid[0:h, 0:w].astype(np.float32)

    # ---- campos -------------------------------------------------------------------------------------
    def bokashi(self, campo, cores, mask=None, transicao=0.35):
        """Pinta faixas de cor ao longo de um campo escalar (0..1) com dither curto entre faixas vizinhas.
        transicao: fração da faixa ocupada pelo dither (pequena = faixas largas, como xilogravura)."""
        cores = [hexrgb(c) if isinstance(c, str) else np.asarray(c, np.float32) for c in cores]
        n = len(cores) - 1
        f = np.clip(campo, 0, 0.99999) * n
        base = np.floor(f).astype(int); fr = f - base
        fr = np.clip((fr - 0.5) / max(transicao, 1e-3) + 0.5, 0, 1)
        idx = np.where(fr > self.T, base + 1, base).clip(0, n)
        pal = np.stack(cores)
        img = pal[idx]
        if mask is None: self.px[:] = img
        else: self.px[mask] = img[mask]

    def misturar(self, mask, cor, alfa):
        """Mistura por dither: pinta `cor` onde alfa (escalar ou matriz 0..1) supera o limiar Bayer."""
        a = np.broadcast_to(np.asarray(alfa, np.float32), (self.h, self.w))
        m = mask & (a > self.T)
        self.px[m] = hexrgb(cor) if isinstance(cor, str) else cor

    def pintar(self, mask, cor):
        self.px[mask] = hexrgb(cor) if isinstance(cor, str) else cor

    # ---- formas -------------------------------------------------------------------------------------
    def mascara_poligono(self, pts):
        im = Image.new("1", (self.w, self.h), 0)
        ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=1)
        return np.array(im, bool)

    def mascara_desenho(self, fn):
        """fn(draw) desenha com fill=1 numa máscara 1-bit (sem antialias)."""
        im = Image.new("1", (self.w, self.h), 0); fn(ImageDraw.Draw(im)); return np.array(im, bool)

    def disco(self, cx, cy, r):
        return (self.xx - cx) ** 2 + (self.yy - cy) ** 2 <= r * r

    def texto(self, txt, x, y, tam=16, vertical=False, espaco=0):
        """Máscara de texto com a fonte pixel DotGothic16 (sem antialias). Retorna (máscara, largura, altura)."""
        f = ImageFont.truetype(FONTE_PIXEL, tam)
        im = Image.new("1", (self.w, self.h), 0); d = ImageDraw.Draw(im); d.fontmode = "1"
        if vertical:
            yy = y
            for ch in txt:
                d.text((x, yy), ch, font=f, fill=1); yy += tam + espaco
            return np.array(im, bool), tam, yy - y
        d.text((x, y), txt, font=f, fill=1)
        bb = d.textbbox((x, y), txt, font=f)
        return np.array(im, bool), bb[2] - bb[0], bb[3] - bb[1]

    # ---- utilidades ---------------------------------------------------------------------------------
    @staticmethod
    def contorno(mask):
        """Pixels de fora que tocam a máscara (4-vizinhança)."""
        m = mask
        viz = np.zeros_like(m)
        viz[1:] |= m[:-1]; viz[:-1] |= m[1:]; viz[:, 1:] |= m[:, :-1]; viz[:, :-1] |= m[:, 1:]
        return viz & ~m

    @staticmethod
    def borda_interna(mask):
        m = mask; e = np.ones_like(m)
        e[1:] &= m[:-1]; e[:-1] &= m[1:]; e[:, 1:] &= m[:, :-1]; e[:, :-1] &= m[:, 1:]
        return m & ~e

    def salvar(self, caminho_base):
        """Grava <base>-480x270.png e <base>-1920x1080.png."""
        im = Image.fromarray(np.clip(self.px + 0.5, 0, 255).astype(np.uint8), "RGB")
        im.save(f"{caminho_base}-{self.w}x{self.h}.png", optimize=True)
        im.resize((self.w * ESCALA, self.h * ESCALA), Image.NEAREST).save(
            f"{caminho_base}-{self.w * ESCALA}x{self.h * ESCALA}.png", optimize=True)
        return im


def ruido_valor(w, h, escala, semente=0, oitavas=3):
    """Ruído de valor suave (0..1) para nuvens, névoa e relevo."""
    rng = np.random.default_rng(semente)
    tot = np.zeros((h, w), np.float32); amp = 1.0; soma = 0
    for o in range(oitavas):
        s = escala / (2 ** o)
        gw, gh = int(w / s) + 3, int(h / s) + 3
        g = rng.random((gh, gw)).astype(np.float32)
        ys = np.arange(h) / s; xs = np.arange(w) / s
        y0 = np.floor(ys).astype(int); x0 = np.floor(xs).astype(int)
        fy = (ys - y0)[:, None]; fx = (xs - x0)[None, :]
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
        tot += amp * ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy)
        soma += amp; amp *= 0.5
    return tot / soma


def perfil_montanha(w, base, amp, escala, semente, picos=None):
    """Altura (y) de uma cordilheira por coluna: ruído 1D + picos opcionais [(x, y_topo, largura)]."""
    rng = np.random.default_rng(semente)
    xs = np.arange(w, dtype=np.float32); y = np.full(w, float(base))
    a = amp
    for o in range(5):
        s = escala / (2 ** o); n = int(w / s) + 3
        g = rng.random(n) * 2 - 1
        p = xs / s; i = np.floor(p).astype(int); f = p - i; f = f * f * (3 - 2 * f)
        y -= a * (g[i] * (1 - f) + g[i + 1] * f); a *= 0.45
    if picos:
        for px, ytopo, larg in picos:
            y = np.minimum(y, ytopo + np.abs(xs - px) / larg * (base - ytopo))
    return np.round(y).astype(int)
