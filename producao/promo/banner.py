#!/usr/bin/env python3
"""Banner do README (1280×400): faixas dos cinco papéis de parede pixeladas + título e subtítulo em DotGothic16.
Uso: .venv/bin/python producao/promo/banner.py [saida.png]   (padrão: docs/imagens/banner.png)
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
FONTE = "/usr/share/fonts/truetype/dotgothic16/DotGothic16-Regular.ttf"
PAPEIS = ["washi/wallpaper/diamante-refino-2026-11-07.png", "yoru/wallpaper/senbon-refino-2026-11-07.png",
          "marys/wallpaper/movel-refino-2026-11-07.png", "neontokyo/wallpaper/sinal-refino-2026-11-07.png",
          "touge/wallpaper/passagem-refino-2026-11-07.png"]
TITULO = "浮世 Ukiyo"
SUBTITULO = "Debian + KDE Plasma em pixel art · feito para criar vídeos"
BW, BH = 1280, 400


def pixel_texto(txt, escala, cor):
    f = ImageFont.truetype(FONTE, 16); bb = f.getbbox(txt)
    m = Image.new("L", (bb[2] + 2, bb[3] + 2), 0); d = ImageDraw.Draw(m); d.fontmode = "1"; d.text((0, 0), txt, font=f, fill=255)
    m = m.resize((m.width * escala, m.height * escala), Image.NEAREST)
    som = Image.new("RGBA", m.size, (12, 10, 24, 0)); som.putalpha(m)
    cam = Image.new("RGBA", m.size, cor + (0,)); cam.putalpha(m)
    return cam, som


def main(saida):
    ban = Image.new("RGB", (BW, BH)); fx = BW // 5
    for i, p in enumerate(PAPEIS):
        im = Image.open(os.path.join(PROJ, "themes", p)).convert("RGB"); s = BH / im.height
        im = im.resize((int(im.width * s), BH), Image.LANCZOS); cx = im.width // 2
        ban.paste(im.crop((cx - fx // 2, 0, cx - fx // 2 + fx, BH)), (i * fx, 0))
    ban = ban.resize((BW // 4, BH // 4), Image.BILINEAR).resize((BW, BH), Image.NEAREST)   # pixeliza (8-bit)
    arr = np.asarray(ban).astype(np.float32) * 0.55 + np.array([10, 8, 22]) * 0.45
    ban = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    t1, s1 = pixel_texto(TITULO, 6, (242, 235, 221)); x = (BW - t1.width) // 2
    ban.paste(s1, (x + 6, 116), s1); ban.paste(t1, (x, 110), t1)
    t2, s2 = pixel_texto(SUBTITULO, 2, (217, 164, 65)); x2 = (BW - t2.width) // 2
    ban.paste(s2, (x2 + 2, 262), s2); ban.paste(t2, (x2, 260), t2)
    selo = Image.new("RGB", (52, 52), (200, 52, 59)); ss, _ = pixel_texto("間", 3, (242, 235, 221))
    selo.paste(ss, ((52 - ss.width) // 2 + 1, (52 - ss.height) // 2 + 2), ss); ban.paste(selo, (BW - 80, BH - 80))
    ban.save(saida, optimize=True); print(saida)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJ, "docs/imagens/banner.png"))
