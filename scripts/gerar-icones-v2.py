#!/usr/bin/env python3
"""Redesenho da família de aplicativos em pixel art 48×48. SVG, biblioteca padrão.
Versão independente; não substitui os temas instalados ou o gerador v1.
"""
from pathlib import Path
import math
ROOT=Path(__file__).resolve().parents[1];N=48
APPS={'arquivos':['org.kde.dolphin','system-file-manager','dolphin'],'navegador':['firefox-esr','firefox','web-browser','internet-web-browser'],'terminal':['utilities-terminal','org.kde.konsole','konsole','terminal'],'gravacao':['com.obsproject.Studio','obs','obs-studio'],'video':['kdenlive','org.kde.kdenlive'],'audio':['audacity','org.audacityteam.Audacity'],'config':['preferences-system','systemsettings','org.kde.systemsettings'],'spotify':['spotify','spotify-client','com.spotify.Client']}
THEMES={'washi':('#f8e9cd','#c15d53'),'yoru':('#eae4f1','#c88d88'),'marys':('#ffeaf0','#d47da8'),'neontokyo':('#d6f2f2','#80c7ce'),'touge':('#e9eef0','#cf7466')}
def mix(a,b,t):
 x=[int(a[i:i+2],16) for i in (1,3,5)];y=[int(b[i:i+2],16) for i in (1,3,5)]
 return '#'+''.join(f'{round(u+(v-u)*t):02x}' for u,v in zip(x,y))
class Sprite:
 def __init__(self):self.p={}
 def dot(self,x,y,c):
  if 0<=x<N and 0<=y<N:self.p[x,y]=c
 def rect(self,x,y,w,h,c):
  for yy in range(y,y+h):
   for xx in range(x,x+w):self.dot(xx,yy,c)
 def line(self,x,y,x1,y1,c,w=1):
  n=max(abs(x-x1),abs(y-y1))
  for i in range(n+1):
   t=i/max(1,n);self.rect(round(x+(x1-x)*t),round(y+(y1-y)*t),w,w,c)
 def oval(self,cx,cy,rx,ry,c):
  for y in range(N):
   for x in range(N):
    if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1:self.dot(x,y,c)
 def disc(self,x,y,r,c):self.oval(x,y,r,r,c)
 def poly(self,pts,c):
  for y in range(N):
   for x in range(N):
    inside=False;j=len(pts)-1
    for i,(xi,yi) in enumerate(pts):
     xj,yj=pts[j]
     if (yi>y+.5)!=(yj>y+.5) and x+.5<(xj-xi)*(y+.5-yi)/(yj-yi)+xi:inside=not inside
     j=i
    if inside:self.dot(x,y,c)
 def svg(self):
  out=[]
  for y in range(N):
   x=0
   while x<N:
    c=self.p.get((x,y))
    if c is None:x+=1;continue
    start=x
    while x<N and self.p.get((x,y))==c:x+=1
    out.append(f'<rect x="{start}" y="{y}" width="{x-start}" height="1" fill="{c}"/>')
  return '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48" shape-rendering="crispEdges">'+''.join(out)+'</svg>\n'
def drawing(name,theme='yoru'):
 g=Sprite();light,accent=THEMES[theme];ink='#252738';cream=mix('#f2e6d2',light,.25)
 if name=='arquivos':
  # Pasta aberta, duas folhas e lombada visíveis. O corpo azul é sua silhueta.
  g.poly([(5,11),(19,11),(23,16),(41,16),(43,19),(41,40),(7,42),(4,38)],'#244258')
  g.poly([(6,12),(18,12),(22,17),(40,17),(41,19),(39,37),(7,39)],'#467e9a')
  g.rect(7,13,10,2,'#a8c9cd');g.rect(8,18,30,18,'#315e79')
  g.poly([(11,9),(32,7),(36,30),(14,32)],'#a4948c');g.poly([(12,9),(31,8),(34,29),(14,30)],cream)
  g.line(15,14,28,12,'#c2b5a3');g.line(15,18,29,16,'#d5c9b6')
  g.poly([(15,13),(37,13),(38,34),(15,35)],'#c4b8a4');g.poly([(16,14),(36,14),(36,32),(16,33)],'#fff3da')
  g.poly([(8,23),(42,21),(40,39),(9,42),(6,39)],'#244258');g.poly([(9,24),(41,22),(38,38),(10,40),(8,38)],'#68a9bd')
  g.poly([(10,26),(39,24),(37,35),(10,38)],'#82bed0');g.line(10,25,39,23,'#b4e0df');g.line(10,40,38,38,'#376b87')
  # Pequena dobra, sem selo decorativo que esconda a pasta.
  g.poly([(33,33),(38,31),(37,37),(32,38)],'#4b91ab');g.line(12,37,27,36,'#a6d1d5')
 elif name=='navegador':
  # Globo azul e cauda de raposa envolvendo-o: leitura de Firefox, não globo genérico.
  g.disc(24,24,18,'#293c71');g.disc(25,22,15,'#477da3');g.disc(27,19,11,'#79adc5')
  g.poly([(21,11),(28,9),(34,13),(32,18),(29,17),(25,20),(21,17)],'#b2d5d5')
  g.poly([(27,25),(33,22),(36,25),(32,29),(31,34),(27,32)],'#8eb8c5')
  g.poly([(11,6),(12,14),(7,20),(5,28),(8,36),(15,42),(24,44),(34,40),(41,32),(43,22),(40,12),(37,7),(36,19),(32,16),(30,23),(35,29),(30,35),(22,38),(15,35),(12,29),(13,22),(19,18),(14,17)],'#9f414b')
  g.poly([(11,8),(13,15),(9,23),(9,30),(14,37),(23,41),(32,38),(38,32),(41,24),(39,15),(37,11),(37,23),(33,20),(34,26),(37,29),(32,35),(24,38),(17,36),(13,31),(12,25),(15,20),(20,18),(14,17)],'#df754d')
  g.poly([(10,18),(9,26),(11,32),(17,37),(24,39),(31,36),(35,31),(30,33),(23,34),(18,31),(17,27),(19,23),(23,21),(19,19),(15,20)],'#f4ab62')
  g.poly([(10,17),(11,10),(14,18),(21,18),(25,22),(20,25),(16,25),(12,22)],'#f6ba72')
  g.poly([(15,23),(20,24),(24,22),(22,26),(17,27)],cream);g.rect(21,20,2,2,'#4e3449')
  g.line(17,37,23,39,'#ffe0a0');g.line(35,34,38,29,'#ee9b57')
 elif name=='terminal':
  # Pequeno terminal de bancada, vidro índigo e controles de cobre.
  g.poly([(5,7),(39,7),(43,11),(41,35),(38,38),(7,38),(4,34)],'#242431')
  g.poly([(6,8),(38,8),(41,11),(39,34),(37,36),(8,36),(6,33)],'#bcaa94')
  g.line(8,9,37,9,cream);g.poly([(9,12),(36,12),(37,14),(35,30),(10,31),(8,29)],'#4e4a61')
  g.poly([(10,13),(35,13),(35,29),(10,29)],'#252c41');g.line(11,14,33,14,'#3c485c')
  g.line(13,18,18,22,'#b9d8c9',2);g.line(18,22,13,26,'#b9d8c9',2);g.rect(23,26,8,2,'#dcb77a')
  g.rect(10,33,3,1,accent);g.rect(15,33,3,1,'#d5bf91');g.rect(33,32,3,2,'#796e6e')
  g.poly([(19,38),(30,38),(32,42),(36,42),(36,44),(13,44),(13,42),(17,42)],'#383440')
  g.rect(19,39,11,2,'#9f9082');g.rect(15,42,19,1,'#b9a893')
 elif name=='gravacao':
  # Disco fosco com três pás curvas. O emblema mantém a leitura de OBS.
  g.disc(23.5,23.5,20,'#171923');g.disc(23,22,19,'#4b4c57');g.disc(24,24,18,'#272a36');g.disc(25,26,15,'#20232e')
  blade=[(22,7),(29,7),(36,11),(39,16),(39,21),(36,25),(31,27),(26,26),(23,22),(23,18),(26,16),(30,17),(32,20),(34,18),(33,14),(29,12),(25,12),(22,15)]
  for a in [0,120,240]:
   r=math.radians(a);pts=[(24+(x-24)*math.cos(r)-(y-24)*math.sin(r),24+(x-24)*math.sin(r)+(y-24)*math.cos(r)) for x,y in blade]
   g.poly(pts,mix('#e5dfd5',light,.18))
  g.line(15,6,24,4,'#7a7d86');g.rect(32,38,3,2,accent)
 elif name=='video':
  # Claquete aberta e timeline com duas faixas; não repete a janela do terminal.
  g.poly([(6,19),(41,19),(41,42),(6,42)],'#26364e');g.rect(7,20,33,21,'#477c9b');g.rect(9,22,29,10,'#243d5b')
  g.poly([(20,23),(28,27),(20,31)],'#e8e5cb');g.rect(10,34,10,3,'#93c6ce');g.rect(22,34,14,3,'#c89b70');g.rect(10,38,5,1,'#a1cbd0');g.rect(18,38,18,1,'#6ca4b7')
  g.poly([(4,10),(36,3),(40,13),(7,20)],'#272b3b');g.poly([(6,11),(35,5),(38,12),(8,18)],cream)
  for x,y in [(11,10),(21,8),(31,6)]:g.poly([(x,y),(x+4,y-1),(x+8,y+5),(x+4,y+6)],'#45536a')
  g.line(9,21,38,21,'#a8cdd1');g.rect(7,18,3,3,'#bca98a');g.rect(8,18,1,1,cream)
 elif name=='audio':
  # Fones dourados, almofadas azuis e uma onda quente suspensa no centro.
  g.oval(23.5,22,18,19,'#29334b');g.oval(23.5,21,16,17,'#d5aa63');g.oval(23.5,22,12,14,'#7c5f45')
  # Abre o arco até a borda inferior (transparência real).
  for y in range(16,48):
   for x in range(12,36):
    if ((x-23.5)/12)**2+((y-22)/14)**2<=1 or y>25:g.p.pop((x,y),None)
  g.line(12,10,18,6,'#f6d598',2);g.line(19,5,27,5,'#e8ca91',2)
  g.poly([(5,22),(11,20),(14,23),(14,37),(11,40),(5,37)],'#27344d');g.poly([(6,23),(10,22),(12,24),(12,36),(10,38),(6,36)],'#507a9e');g.rect(7,24,2,11,'#8db6c8')
  g.poly([(34,23),(37,20),(43,22),(43,37),(37,40),(34,37)],'#27344d');g.poly([(36,24),(38,22),(42,23),(42,36),(38,38),(36,36)],'#507a9e');g.rect(37,24,2,11,'#8db6c8')
  for x,h in [(16,5),(20,11),(24,17),(28,10),(32,4)]:
   y=28-h//2;g.rect(x,y,2,h,'#be6c4c');g.rect(x,y,1,max(1,h-2),'#f2b96d')
 elif name=='config':
  # Engrenagem chanfrada: dentes distribuídos, metal claro e cubo âmbar.
  pts=[]
  for i in range(40):
   r=20 if i%5 in [1,2,3] else 16.5;a=2*math.pi*i/40-math.pi/2;pts.append((23.5+r*math.cos(a),23.5+r*math.sin(a)))
  g.poly(pts,'#48516a');pts2=[(23.5+(x-23.5)*.92,23.5+(y-23.5)*.92) for x,y in pts];g.poly(pts2,'#9fa9b5')
  for (x,y),c in list(g.p.items()):
   if c=='#9fa9b5':
    if x+y<40:g.p[x,y]='#d4d6d2'
    elif x+y>57:g.p[x,y]='#7c8a9e'
  g.disc(23.5,23.5,11,'#536078');g.disc(23,23,9,'#d2d2c9');g.disc(24,24,7,'#34384d');g.disc(24,23,4.5,'#ae7858');g.disc(23,22,3,'#e8bd7b')
  g.line(18,12,24,11,'#f3ead5');g.rect(21,21,2,2,'#ffe3a5')
 elif name=='spotify':
  # Disco de resina verde: relevo em planos, três ondas largas e bem separadas.
  g.disc(23.5,23.5,20,'#275a4d');g.disc(23.5,22.5,19,'#7dba84');g.disc(24,24,17.5,'#65a76e')
  for (x,y),c in list(g.p.items()):
   if c=='#65a76e' and x+y>55:g.p[x,y]='#4c8a61'
   elif c=='#65a76e' and x+y<35:g.p[x,y]='#91c78d'
  g.line(14,7,22,5,'#c7dfaa');g.line(10,10,12,8,'#b4d79c')
  for pts,w in [([(11,17),(17,15),(25,15),(33,17),(37,20)],3), ([(13,24),(19,22),(26,23),(33,26)],3), ([(15,31),(21,29),(27,30),(31,32)],2)]:
   for a,b in zip(pts,pts[1:]):g.line(*a,*b,'#254b42',w)
 # O tema colore pequenos reflexos e detalhes, sem apagar a identidade dos aplicativos.
 if theme!='yoru':
  strength={'washi':.07,'marys':.16,'neontokyo':.10,'touge':.04}[theme]
  for q,c in list(g.p.items()):
   rgb=[int(c[i:i+2],16) for i in (1,3,5)]
   if min(rgb)>95:g.p[q]=mix(c,light,strength)
 return g

def main():
 for theme in THEMES:
  out=ROOT/f'themes/{theme}/icons-v2/{theme}-pixel-art-v2';d=out/'apps/scalable';d.mkdir(parents=True,exist_ok=True)
  for name,aliases in APPS.items():
   svg=drawing(name,theme).svg()
   for alias in aliases:(d/(alias+'.svg')).write_text(svg)
  (out/'index.theme').write_text(f'[Icon Theme]\nName={theme.title()} — Pixel Art v2\nComment=Aplicativos redesenhados em pixel art 48×48\nInherits={theme}-pixel\nFollowsColorScheme=true\nDirectories=apps/scalable\n\n[apps/scalable]\nSize=48\nMinSize=16\nMaxSize=256\nType=Scalable\nContext=Applications\n')
  print(out.relative_to(ROOT))
if __name__=='__main__':main()
