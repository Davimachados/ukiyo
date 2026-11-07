#!/usr/bin/env python3
"""Compara os SVGs reais, em tamanho de dock e ampliados; somente gera documentação visual."""
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/visual/refino-icones-2026-11-07';OUT.mkdir(parents=True,exist_ok=True)
F='/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'
def font(n):return ImageFont.truetype(F,n)
def render(path,size):
 if path.suffix=='.png':return Image.open(path).convert('RGBA').resize((size,size),Image.Resampling.LANCZOS)
 root=ET.fromstring(path.read_text());n=int(root.attrib['viewBox'].split()[-1]);im=Image.new('RGBA',(n,n));d=ImageDraw.Draw(im)
 for r in root:
  if r.tag.endswith('rect'):
   x,y,w,h=[int(r.attrib[k]) for k in ['x','y','width','height']];d.rectangle((x,y,x+w-1,y+h-1),fill=r.attrib['fill'])
 return im.resize((size,size),Image.Resampling.NEAREST)
NAMES=[('Dolphin','org.kde.dolphin'),('Firefox','firefox-esr'),('Konsole','konsole'),('OBS','obs'),('Kdenlive','kdenlive'),('Audacity','audacity'),('Configurações','systemsettings'),('Spotify','spotify-client')]
spotify=next(iter((Path('/usr/share/spotify/icons')).glob('*64*.png')),None)
if not spotify:spotify=next(iter(Path('/usr/share/spotify/icons').glob('*.png')),None)
for theme in ['washi','yoru','marys','neontokyo','touge']:
 im=Image.new('RGB',(1440,660),'#161722');d=ImageDraw.Draw(im)
 d.text((48,30),theme.upper()+'  /  ÍCONES DOS APLICATIVOS',font=font(26),fill='#eee8de')
 d.text((48,77),'Mesmos aplicativos. Mais respiro, contornos leves e leitura em tamanho pequeno.',font=font(18),fill='#b9b3c2')
 d.text((48,132),'ATUAIS',font=font(16),fill='#a49baa');d.text((48,342),'PROPOSTA',font=font(16),fill='#e9cd9b')
 for i,(name,alias) in enumerate(NAMES):
  x=48+i*170
  for y,new in [(172,False),(382,True)]:
   path=ROOT/f'themes/{theme}'/('icons-refino' if new else 'icons')/(f'{theme}-pixel'+('-refino' if new else ''))/'apps/scalable'/f'{alias}.svg'
   if not path.exists() and alias=='spotify-client' and spotify:path=spotify
   if not path.exists():continue
   icon=render(path,96);im.paste(icon,(x+17,y),icon)
   icon=render(path,48);im.paste(icon,(x+41,y+110),icon)
  d.text((x+4,568),name,font=font(16),fill='#d9d3df')
 d.text((48,618),'Acima: ampliação para revisão. Abaixo: 48 px, próximo do tamanho da dock. Nada ativado.',font=font(15),fill='#a49baa')
 im.save(OUT/f'{theme}-comparacao.png')
# Visão geral da proposta: cinco paletas, sem mudar as cores dos apps.
im=Image.new('RGB',(1440,850),'#161722');d=ImageDraw.Draw(im)
d.text((48,25),'ukiyo  /  proposta de refino dos ícones',font=font(28),fill='#eee8de')
for row,theme in enumerate(['washi','yoru','marys','neontokyo','touge']):
 y=104+row*140;d.text((48,y+22),theme.title(),font=font(20),fill='#d9d3df')
 for i,(name,alias) in enumerate(NAMES):
  p=ROOT/f'themes/{theme}/icons-refino/{theme}-pixel-refino/apps/scalable/{alias}.svg';icon=render(p,72);im.paste(icon,(250+i*142,y),icon)
for i,(name,_) in enumerate(NAMES):d.text((240+i*142,806),name,font=font(14),fill='#aaa3b4')
im.save(OUT/'cinco-temas.png')
html='<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Ícones: antes e depois</title><style>body{background:#161722;color:#eee8de;font:18px system-ui;margin:32px}img{max-width:100%;height:auto}a{color:#e9cd9b}</style><h1>Refino dos ícones dos aplicativos</h1><p>Propostas em SVG, preservando os temas atuais. Nada instalado ou ativado.</p>'
for theme in ['washi','yoru','marys','neontokyo','touge']:html+=f'<h2>{theme.title()}</h2><a href="{theme}-comparacao.png"><img src="{theme}-comparacao.png" alt="Comparação {theme}"></a>'
(OUT/'comparacao.html').write_text(html)
print(OUT)
