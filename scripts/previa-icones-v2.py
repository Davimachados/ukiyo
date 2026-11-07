#!/usr/bin/env python3
"""Pranchas dos SVGs reais: conjunto ativo versus redesenho v2. Não ativa nada."""
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/visual/icones-v2-2026-11-07'
NAMES=[('Dolphin','org.kde.dolphin'),('Firefox','firefox-esr'),('Konsole','konsole'),('OBS','obs'),('Kdenlive','kdenlive'),('Audacity','audacity'),('Configurações','systemsettings'),('Spotify','spotify-client')]
F='/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'
def font(n):return ImageFont.truetype(F,n)
def render(p,size):
 root=ET.fromstring(p.read_text());n=int(root.attrib['viewBox'].split()[-1]);im=Image.new('RGBA',(n,n));d=ImageDraw.Draw(im)
 for r in root:
  if r.tag.endswith('rect'):
   x,y,w,h=[int(r.attrib[k]) for k in ['x','y','width','height']];d.rectangle((x,y,x+w-1,y+h-1),fill=r.attrib['fill'])
 return im.resize((size,size),Image.Resampling.NEAREST)
def path(theme,alias,new):return ROOT/f'themes/{theme}'/('icons-v2' if new else 'icons-refino')/(f'{theme}-pixel-art-v2' if new else f'{theme}-pixel-refino')/'apps/scalable'/f'{alias}.svg'
OUT.mkdir(parents=True,exist_ok=True)
for theme in ['yoru','washi','marys','neontokyo','touge']:
 im=Image.new('RGB',(1600,870),'#1b1d2b');d=ImageDraw.Draw(im)
 d.text((50,30),'ukiyo  /  REDESENHO DOS ÍCONES',font=font(28),fill='#f0e7d9')
 d.text((50,78),theme.upper()+' · Desenhos em tamanho ampliado e em 48 px.',font=font(18),fill='#b9b5c5')
 for new,y,label in [(False,165,'CONJUNTO ATIVO'),(True,465,'NOVA PROPOSTA')]:
  d.text((50,y-30),label,font=font(16),fill='#b6afbd' if not new else '#e2ba80')
  for i,(name,alias) in enumerate(NAMES):
   x=50+i*189;icon=render(path(theme,alias,new),144);im.paste(icon,(x+8,y+8),icon)
   small=render(path(theme,alias,new),48);im.paste(small,(x+56,y+175),small)
   d.text((x+8,y+237),name,font=font(16),fill='#dcd5df')
 d.text((50,820),'Ampliação acima · 48 px abaixo · redesenho de formas, cores e volumes · proposta para avaliação',font=font(16),fill='#b0a8ba')
 im.save(OUT/f'{theme}-antes-depois.png')
# Faixa em tamanho de uso: cada SVG em 48 pixels exatos.
im=Image.new('RGB',(920,180),'#1b1d2b');d=ImageDraw.Draw(im);d.text((30,20),'Nova proposta · tamanho real de 48 px',font=font(18),fill='#e8dfd8')
for i,(_,alias) in enumerate(NAMES):
 icon=render(path('yoru',alias,True),48);im.paste(icon,(45+i*107,80),icon)
im.save(OUT/'dock-48px.png')
html='<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Redesenho dos ícones v2</title><style>body{margin:32px;background:#1b1d2b;color:#eee5da;font:18px system-ui}img{max-width:100%;height:auto}a{color:#e2ba80}</style><h1>Redesenho dos ícones</h1><p>Nova proposta. Os ícones ativos continuam preservados.</p><h2>Em tamanho real</h2><img src="dock-48px.png" alt="Oito ícones a 48 pixels">'
for t in ['yoru','washi','marys','neontokyo','touge']:html+=f'<h2>{t.title()}</h2><a href="{t}-antes-depois.png"><img src="{t}-antes-depois.png" alt="Comparação {t}"></a>'
(OUT/'comparacao.html').write_text(html)
print(OUT)
