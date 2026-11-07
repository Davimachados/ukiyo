#!/usr/bin/env python3
"""Capturas autorizadas para apresentação. Restaura tema e estado Mostrar desktop."""
from pathlib import Path
import subprocess,time,re
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/visual/capturas/apresentacao-2026-11-07'
def run(*args):return subprocess.check_output(args,text=True).strip()
def db(*args):return run('qdbus6','org.kde.KWin','/KWin',*args)
mode=(Path.home()/'.local/state/ukiyo/modo').read_text().strip()
shown=db('org.freedesktop.DBus.Properties.Get','org.kde.KWin','showingDesktop')
def vd(*args):return run('qdbus6','org.kde.KWin','/VirtualDesktopManager',*args)
current=vd('org.freedesktop.DBus.Properties.Get','org.kde.KWin.VirtualDesktopManager','current')
desktops=run('qdbus6','--literal','org.kde.KWin','/VirtualDesktopManager','org.freedesktop.DBus.Properties.Get','org.kde.KWin.VirtualDesktopManager','desktops')
target=re.findall(r'[0-9a-f]{8}-[0-9a-f-]{27}',desktops)[-1]
try:
 vd('org.freedesktop.DBus.Properties.Set','org.kde.KWin.VirtualDesktopManager','current',target)
 for theme in ['claro','escuro','marys','neontokyo','touge']:
  run(str(ROOT/'modos/trocar-tema.sh'),theme,'--esperar');time.sleep(.7)
  vd('org.freedesktop.DBus.Properties.Set','org.kde.KWin.VirtualDesktopManager','current',target);time.sleep(1.0)
  run('spectacle','-b','-n','-f','-o',str(OUT/(theme+'.png')))
  print('capturado:',theme,flush=True)
finally:
 run(str(ROOT/'modos/trocar-tema.sh'),mode,'--esperar')
 vd('org.freedesktop.DBus.Properties.Set','org.kde.KWin.VirtualDesktopManager','current',current)
 db('org.kde.KWin.showDesktop','true' if shown.lower()=='true' else 'false')
 print('restaurado:',mode,'mostrar desktop:',shown,flush=True)
