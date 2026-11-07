#!/usr/bin/env python3
"""Filme de apresentação: composição offline em Pillow, H.264 VA-API e trilha original sintetizada.
Uso: .venv/bin/python producao/apresentacao/renderizar.py
"""
from pathlib import Path
import math,subprocess,json,wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'renders/apresentacao-2026-11-07';OUT.mkdir(parents=True,exist_ok=True)
CAP=ROOT/'docs/visual/capturas/apresentacao-2026-11-07'
W,H,FPS,DURATION=1280,720,30,48
BG=(17,18,26);INK=(241,233,219);MUTED=(174,171,178);RED=(203,73,77)
FONT='/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'
if not Path(FONT).exists():FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
PIX='/usr/share/fonts/truetype/dotgothic16/DotGothic16-Regular.ttf'
def font(n,pixel=False):return ImageFont.truetype(PIX if pixel else FONT,n)
F={n:font(n) for n in [14,16,18,20,22,24,28,32,42,56,72]};FP={n:font(n,True) for n in [20,28,48,80]}
DATA=[('claro','washi','diamante','diamante','Washi','O entardecer encontra silêncio.'),('escuro','yoru','senbon','senbon','Yoru','Uma curva. Algumas lanternas.'),('marys','marys','movel','movel',"Mary’s",'Um lugar macio para pousar.'),('neontokyo','neontokyo','sinal','sinal','Neon Tokyo','A cidade também sabe falar baixo.'),('touge','touge','rastro','passagem','Touge','O caminho passa a fazer parte de casa.')]
def cover(im,w,h):
 ratio=max(w/im.width,h/im.height);im=im.resize((round(im.width*ratio),round(im.height*ratio)),Image.Resampling.LANCZOS)
 x=(im.width-w)//2;y=(im.height-h)//2;return im.crop((x,y,x+w,y+h))
old=[];new=[];screens=[]
for mode,folder,a,b,title,desc in DATA:
 old.append(cover(Image.open(ROOT/f'themes/{folder}/wallpaper/{a}-1920x1080.png').convert('RGB'),W,H))
 new.append(cover(Image.open(ROOT/f'themes/{folder}/wallpaper/{b}-refino-2026-11-07.png').convert('RGB'),W,H))
 screens.append(cover(Image.open(CAP/f'{mode}.png').convert('RGB'),1120,630))
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def text(im,xy,s,size=24,color=INK,pixel=False):ImageDraw.Draw(im).text(xy,s,font=FP[size] if pixel else F[size],fill=color)
def tint(im,opacity):return Image.blend(im,Image.new('RGB',im.size,BG),opacity)
def pan(im,p,amount=.025):
 z=1+amount*ease(p);cw=round(W/z);ch=round(H/z);x=round((W-cw)*(.3+.4*p));y=(H-ch)//2
 return im.crop((x,y,x+cw,y+ch)).resize((W,H),Image.Resampling.LANCZOS)
def base(t):
 if t<5:
  im=tint(pan(new[0],t/5),.55)
  text(im,(80,76),'UM DEBIAN. UM JEITO DE HABITAR.',16)
  y=278+round(20*(1-ease(t/1.5)))
  text(im,(76,y),'ukiyo',80,pixel=True)
  text(im,(82,y+107),'Minha distro. Meu ritmo. Minha casa.',28)
  ImageDraw.Draw(im).rectangle((82,619,137,623),fill=RED)
  text(im,(155,609),'Debian  ·  KDE Plasma  ·  identidade própria',18)
  return im
 if t<30:
  i=min(4,int((t-5)//5));p=((t-5)%5)/5
  a=pan(old[i],p,.018);b=pan(new[i],p,.018)
  # Uma passagem lenta da arte original ao refino, sem flashes.
  boundary=round(W*(1-ease((p-.22)/.5)))
  im=b.copy()
  if boundary>0:im.paste(a.crop((0,0,boundary,H)),(0,0))
  if 0<boundary<W:ImageDraw.Draw(im).rectangle((boundary-1,0,boundary+1,H),fill=INK)
  # Faixas discretas apenas dentro do filme; não são interface do sistema.
  overlay=Image.new('RGB',(W,124),BG);im.paste(Image.blend(im.crop((0,H-124,W,H)),overlay,.82),(0,H-124))
  text(im,(58,H-105),DATA[i][4],42)
  text(im,(60,H-49),DATA[i][5],18)
  label='ORIGEM' if p<.45 else 'REFINO'
  text(im,(1085,H-91),label,16)
  text(im,(1085,H-52),f'0{i+1} / 05',16,color=MUTED)
  return im
 if t<42.5:
  i=min(4,int((t-30)//2.5));p=((t-30)%2.5)/2.5
  im=Image.new('RGB',(W,H),BG)
  card=screens[i]
  scale=.92+.04*ease(p);width=round(1120*scale);height=round(630*scale)
  card=card.resize((width,height),Image.Resampling.LANCZOS)
  x=(W-width)//2;y=98+round(10*(1-ease(p)))
  ImageDraw.Draw(im).rectangle((x+10,y+12,x+width+10,y+height+12),fill=(7,8,13))
  im.paste(card,(x,y))
  text(im,(62,26),'O SEU DESKTOP, DO SEU JEITO.',20,pixel=True)
  text(im,(910,30),DATA[i][4]+'  /  KDE Plasma',16,color=MUTED)
  return im
 im=tint(pan(new[4],(t-42.5)/5.5),.5)
 text(im,(80,92),'FEITO PARA VIVER AQUI.',20,pixel=True)
 text(im,(76,274),'ukiyo',80,pixel=True)
 text(im,(82,384),'Debian na base. Sua identidade em cada detalhe.',24)
 text(im,(82,603),'Visual japonês  /  ferramentas próprias  /  espaço para criar',18)
 return im
# Trilha original: arpejos discretos, timbres de seno e triângulo; nenhuma captura de áudio.
def soundtrack():
 sr=48000;n=DURATION*sr;audio=np.zeros((n,2),np.float32)
 chords=[[57,60,64,71],[53,57,60,64],[48,55,60,64],[55,59,62,69],[50,57,60,65],[53,60,64,69],[48,55,59,64],[52,59,64,67]]
 def note(midi,start,dur,gain,panpos):
  a=int(start*sr);length=min(int(dur*sr),n-a)
  if length<=0:return
  t=np.arange(length)/sr;hz=440*2**((midi-69)/12)
  env=(1-np.exp(-t/0.025))*np.exp(-t/1.1)*np.minimum(1,np.maximum(0,(dur-t)/.3))
  sig=(np.sin(2*np.pi*hz*t)+.16*np.sin(2*np.pi*2*hz*t)+.045*np.sin(2*np.pi*3*hz*t))*env*gain
  audio[a:a+length,0]+=sig*math.sqrt((1-panpos)/2);audio[a:a+length,1]+=sig*math.sqrt((1+panpos)/2)
 for bar,chord in enumerate(chords):
  for k in range(8):note(chord[[0,2,1,3,2,1,3,2][k]]+12,bar*6+k*.75,2.8,.11,(-.3 if k%2 else .3))
  note(chord[0]-12,bar*6,5.5,.13,0)
 for delay,gain in [(.225,.16),(.45,.08)]:
  shift=int(delay*sr);audio[shift:]+=gain*audio[:-shift]
 fade=np.minimum(1,np.arange(n)/(sr*2))*np.minimum(1,(n-np.arange(n))/(sr*4));audio*=fade[:,None]
 peak=np.max(np.abs(audio));audio*=.63/max(peak,1e-6)
 path=OUT/'trilha-original.wav'
 with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((audio*32767).astype('<i2').tobytes())
 return path
if __name__=='__main__':
 track=soundtrack();video=OUT/'ukiyo-apresentacao-48s.mp4'
 cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-vaapi_device','/dev/dri/renderD128','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','pipe:0','-i',str(track),'-vf','format=nv12,hwupload,scale_vaapi=w=1920:h=1080','-c:v','h264_vaapi','-qp','20','-g','60','-c:a','aac','-b:a','192k','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar','48000','-t',str(DURATION),'-movflags','+faststart',str(video)]
 with (OUT/'render.log').open('w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for frame in range(DURATION*FPS):
    t=frame/FPS;im=base(t)
    # Dissolução curta entre capítulos; progressão contínua na montagem.
    cuts=[5,10,15,20,25,30,32.5,35,37.5,40,42.5]
    for cut in cuts:
     if cut<=t<cut+.4:
      im=Image.blend(base(cut-1/FPS),im,ease((t-cut)/.4));break
    fade=min(1,t/1.0,(DURATION-t)/1.4)
    if fade<1:im=Image.blend(Image.new('RGB',(W,H),BG),im,max(0,fade))
    proc.stdin.write(im.tobytes())
    if frame%(FPS*4)==0:print(f'{t:.0f}/{DURATION}s',flush=True)
   proc.stdin.close();rc=proc.wait()
  except BaseException:
   proc.kill();raise
 if rc:raise SystemExit('Falha no FFmpeg; consulte render.log')
 (OUT/'roteiro.json').write_text(json.dumps({'duracao':DURATION,'fps':FPS,'resolucao':'1920x1080','encoder':'h264_vaapi','trilha':'original sintetizada offline','capitulos':{'0–5':'abertura','5–30':'cinco comparações origem/refino','30–42.5':'capturas reais dos cinco temas com motion','42.5–48':'encerramento'}},ensure_ascii=False,indent=2))
 print(video,flush=True)
