#!/usr/bin/env python3
"""Proposta de ícones do dock: SVG pixel 24×24, somente biblioteca padrão.
Não instala nem altera os temas anteriores. Saídas separadas por tema em icons-refino/.
"""
from pathlib import Path
import math
ROOT=Path(__file__).resolve().parents[1]
N=24
PALETTES={
'washi':dict(ink='#292735',edge='#b6a99e',paper='#f3e9d5',shade='#d5c5a8',red='#b95053',red2='#7f343d',blue='#7395ad',blue2='#435a78',green='#7a9b79',green2='#466c56',gold='#d6ac69',dark='#333341'),
'yoru':dict(ink='#151624',edge='#9290a8',paper='#e5dfd8',shade='#aaa2b2',red='#cf7476',red2='#854856',blue='#8cabc1',blue2='#536d93',green='#94b29a',green2='#527664',gold='#d8b780',dark='#2c2b43'),
'marys':dict(ink='#643c51',edge='#d7aabf',paper='#fff3e6',shade='#e9c4ce',red='#d87f9f',red2='#a15377',blue='#b5a3cb',blue2='#84769f',green='#91bbab',green2='#588a7a',gold='#dfb77b',dark='#694d68'),
'neontokyo':dict(ink='#111321',edge='#60899a',paper='#dce9e6',shade='#8a9eaf',red='#d774a4',red2='#8a426b',blue='#7eb9c4',blue2='#426e8a',green='#90b7a7',green2='#487d75',gold='#d5bd88',dark='#25283f'),
 'touge':dict(ink='#242734',edge='#9ca6b2',paper='#eae9df',shade='#b1b8bc',red='#bd6567',red2='#803f4b',blue='#7f9fb7',blue2='#4d6886',green='#91a991',green2='#58735e',gold='#d2b179',dark='#303848')}
APPS={
 'arquivos':['org.kde.dolphin','system-file-manager','dolphin'],
 'navegador':['firefox-esr','firefox','web-browser','internet-web-browser'],
 'terminal':['utilities-terminal','org.kde.konsole','konsole','terminal'],
 'gravacao':['com.obsproject.Studio','obs','obs-studio'],
 'video':['kdenlive','org.kde.kdenlive'],
 'audio':['audacity','org.audacityteam.Audacity'],
 'config':['preferences-system','systemsettings','org.kde.systemsettings'],
 'spotify':['spotify','spotify-client','com.spotify.Client']}
class Grid:
 def __init__(self):self.p={}
 def dot(self,x,y,c):
  if 0<=x<N and 0<=y<N:self.p[x,y]=c
 def rect(self,x,y,w,h,c):
  for j in range(y,y+h):
   for i in range(x,x+w):self.dot(i,j,c)
 def line(self,x0,y0,x1,y1,c,width=1):
  steps=max(abs(x1-x0),abs(y1-y0))
  for k in range(steps+1):
   t=k/max(1,steps);x=round(x0+t*(x1-x0));y=round(y0+t*(y1-y0))
   self.rect(x,y,width,width,c)
 def disc(self,cx,cy,r,c):
  for y in range(N):
   for x in range(N):
    if (x-cx)**2+(y-cy)**2<=r*r:self.dot(x,y,c)
 def poly(self,pts,c):
  for y in range(N):
   for x in range(N):
    inside=False;j=len(pts)-1
    for i,(xi,yi) in enumerate(pts):
     xj,yj=pts[j]
     if (yi>y+.5)!=(yj>y+.5) and x+.5<(xj-xi)*(y+.5-yi)/(yj-yi)+xi:inside=not inside
     j=i
    if inside:self.dot(x,y,c)
 def frame(self,x,y,w,h,body):
  self.rect(x+1,y,w-2,h,'ink');self.rect(x,y+1,w,h-2,'ink');self.rect(x+1,y+1,w-2,h-2,body)
 def edge(self):
  # Fio externo discreto para leitura sobre o painel escuro, com margem de segurança.
  original=dict(self.p)
  for x,y in original:
   for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
    q=x+dx,y+dy
    if q not in original and 0<=q[0]<N and 0<=q[1]<N:self.p[q]='edge'
 def svg(self,pal):
  nodes=[]
  for y in range(N):
   x=0
   while x<N:
    c=self.p.get((x,y))
    if c is None:x+=1;continue
    start=x
    while x<N and self.p.get((x,y))==c:x+=1
    nodes.append(f'<rect x="{start}" y="{y}" width="{x-start}" height="1" fill="{pal[c]}"/>')
  return '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" shape-rendering="crispEdges">'+''.join(nodes)+'</svg>\n'
def drawing(name):
 g=Grid()
 if name=='arquivos':
  g.frame(3,5,9,6,'gold');g.frame(3,8,18,12,'shade');g.rect(4,9,16,2,'paper');g.poly([(3,11),(21,11),(19,20),(3,20)],'ink');g.poly([(4,12),(20,12),(18,19),(4,19)],'paper');g.rect(5,12,13,1,'gold');g.rect(5,17,13,2,'shade')
 elif name=='navegador':
  g.disc(11.5,11.5,9.5,'ink');g.disc(11.5,11.5,8.2,'blue2');g.disc(10,10,6.8,'blue')
  g.poly([(4,7),(8,5),(11,6),(10,9),(7,11),(5,10)],'paper');g.poly([(12,11),(16,10),(19,13),(16,16),(14,19),(12,16)],'green');g.rect(6,5,3,1,'shade');g.rect(4,12,3,2,'blue2')
 elif name=='terminal':
  g.frame(3,4,18,16,'dark');g.rect(4,5,16,3,'shade');g.rect(5,6,2,1,'red');g.rect(8,6,2,1,'gold');g.rect(11,6,2,1,'paper');g.line(6,11,9,14,'paper');g.line(9,14,6,17,'paper');g.rect(12,17,5,1,'gold')
 elif name=='gravacao':
  g.frame(3,7,14,12,'dark');g.poly([(17,10),(21,8),(21,18),(17,16)],'ink');g.poly([(18,11),(20,10),(20,16),(18,15)],'shade');g.disc(9.5,13,4.3,'ink');g.disc(9.5,13,3,'blue2');g.disc(9,12,1.5,'blue');g.rect(5,5,6,2,'ink');g.rect(6,5,4,1,'shade');g.rect(14,8,2,2,'red');g.rect(5,17,9,1,'shade')
 elif name=='video':
  g.frame(3,9,18,11,'blue2');g.rect(4,10,16,1,'blue');g.poly([(9,12),(15,15),(9,18)],'paper')
  g.poly([(2,5),(19,2),(21,7),(4,10)],'ink');g.poly([(3,5),(19,3),(20,6),(4,9)],'paper')
  for x,y in [(6,5),(11,4),(16,3)]:g.poly([(x,y),(x+2,y),(x+4,y+3),(x+2,y+3)],'dark')
 elif name=='audio':
  g.disc(11.5,10,8,'ink');g.disc(11.5,10,6,'blue');g.disc(11.5,10,4.5,'dark');g.rect(3,10,18,9,'dark');g.frame(3,11,5,8,'shade');g.frame(16,11,5,8,'shade');g.rect(4,12,2,5,'blue');g.rect(18,12,2,5,'blue')
  for x,a in [(9,2),(11,4),(13,3)]:g.rect(x,14-a//2,1,a,'green')
 elif name=='config':
  # Seis dentes e cubo aberto: silhueta menor e menos maciça que o brasão anterior.
  for a in range(0,360,60):
   rad=math.radians(a);x=round(11.5+7.5*math.cos(rad));y=round(11.5+7.5*math.sin(rad));g.rect(x-1,y-1,3,3,'ink')
  g.disc(11.5,11.5,7.5,'ink');g.disc(11.5,11.5,6.1,'shade');g.disc(11.5,11.5,3.4,'ink');g.disc(11.5,11.5,2,'blue');g.rect(8,6,5,1,'paper')
 elif name=='spotify':
  g.disc(11.5,11.5,9.5,'ink');g.disc(11.5,11.5,8.2,'green');g.poly([(5,6),(10,4),(15,5),(18,8),(17,8),(14,6),(9,5),(5,7)],'paper')
  for pts in [[(6,9),(10,8),(14,8),(18,10)],[(7,12),(11,11),(14,12),(17,13)],[(8,15),(11,14),(14,15),(16,16)]]:
   for a,b in zip(pts,pts[1:]):g.line(*a,*b,'ink')
 g.edge();return g

def main():
 report={}
 for theme,pal in PALETTES.items():
  target=ROOT/'themes'/theme/'icons-refino'/f'{theme}-pixel-refino';apps=target/'apps/scalable';apps.mkdir(parents=True,exist_ok=True)
  for name,aliases in APPS.items():
   icon=drawing(name).svg(pal)
   for alias in aliases:(apps/(alias+'.svg')).write_text(icon)
  (target/'index.theme').write_text(f'[Icon Theme]\nName={theme.title()} Pixel — Refino\nComment=Proposta pixel 24×24 para os aplicativos do dock\nInherits={theme}-pixel\nFollowsColorScheme=true\nExample=folder\nDirectories=apps/scalable\n\n[apps/scalable]\nSize=24\nMinSize=16\nMaxSize=256\nType=Scalable\nContext=Applications\n')
  report[theme]=str(target.relative_to(ROOT));print(report[theme])
 return report
if __name__=='__main__':main()
