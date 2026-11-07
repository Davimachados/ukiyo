#!/usr/bin/env python3
"""Gera o tema de ícones 'washi-pixel' (herda Breeze) a partir dos desenhos 16x16.

- apps: reaproveita os ícones aprovados na prévia (gerar-icones.py) com os nomes reais usados pelos .desktop
- places: pastas pixel com emblemas distintos (casa, documentos, downloads, música, imagens, vídeos...)
- tudo o que não existir aqui cai no Breeze (Inherits=breeze,hicolor)

Uso: gerar-tema-icones.py PASTA_DESTINO   (cria PASTA_DESTINO/washi-pixel)
"""
import importlib.util, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("icones", os.path.join(AQUI, "gerar-icones.py"))
ic = importlib.util.module_from_spec(spec); spec.loader.exec_module(ic)
PAL, ICONES, svg = ic.PAL, ic.ICONES, ic.svg

# ---------- pastas: base + emblema 6x5 sobreposto ----------
BASE_PASTA = """
................
................
.kkkkkk.........
.kyyyyyk........
.kyyyyyykkkkkkk.
.kkkkkkkkkkkkkk.
.kwwwwwwwwwwwwk.
.kwwwwwwwwwwwwk.
.kwwwwwwwwwwwwk.
.kwwwwwwwwwwwwk.
.kwwwwwwwwwwwwk.
.kwwwwwwwwwwwwk.
.kppppppppppppk.
.kkkkkkkkkkkkkk.
................
................
"""
EMBLEMAS = {  # 7 colunas x 5 linhas, colocado em x=5..11, y=7..11
    "folder":           None,
    "user-home":        ["...k...", "..kkk..", ".kkkkk.", "..k.k..", "..k.k.."],
    "user-desktop":     ["kkkkkkk", "kbbbbbk", "kbbbbbk", "kkkkkkk", "..kkk.."],
    "folder-documents": ["kkkkkk.", ".......", "kkkkkkk", ".......", "kkkk..."],
    "folder-download":  ["...G...", "...G...", ".GGGGG.", "..GGG..", "...G..."],
    "folder-music":     ["...kkkk", "...k..k", "...k..k", ".kkk.kk", ".kk..kk"],
    "folder-pictures":  [".....y.", "...k...", "..kGk..", ".kGGGk.", "kGGGGGk"],
    "folder-videos":    ["kkkkkkk", "k.rr..k", "k.rrr.k", "k.rr..k", "kkkkkkk"],
    "folder-publicshare": ["..b.b..", ".bbbbb.", "..b.b..", ".bbbbb.", "..b.b.."],
    "folder-templates": ["kkkkk..", "k...kk.", "k....k.", "k....k.", "kkkkkk."],
    "folder-red":       ["rrrrrrr", "rrrrrrr", "ddddddd", "rrrrrrr", "rrrrrrr"],
}
def pasta(emblema):
    g = [list(l) for l in BASE_PASTA.strip("\n").split("\n")]
    if emblema:
        for dy, linha in enumerate(emblema):
            for dx, c in enumerate(linha):
                if c != ".": g[7 + dy][5 + dx] = c
    return "\n".join("".join(l) for l in g)

LIXEIRA = """
................
.....kkkkkk.....
.....kwwwwk.....
..kkkkkkkkkkkk..
..kppppppppppk..
..kkkkkkkkkkkk..
...kwwkwwkwwk...
...kwwkwwkwwk...
...kwwkwwkwwk...
...kwwkwwkwwk...
...kwwkwwkwwk...
...kwwkwwkwwk...
...kwwkwwkwwk...
...kppppppppk...
...kkkkkkkkkk...
................
"""

APPS = {  # desenho -> nomes de ícone usados pelos apps (Icon= dos .desktop + aliases comuns)
    "pasta":     ["org.kde.dolphin", "system-file-manager", "dolphin"],
    "navegador": ["firefox-esr", "firefox", "web-browser", "internet-web-browser"],
    "terminal":  ["utilities-terminal", "org.kde.konsole", "konsole", "terminal"],
    "gravacao":  ["com.obsproject.Studio", "obs", "obs-studio"],
    "video":     ["kdenlive", "org.kde.kdenlive"],
    "audio":     ["audacity", "org.audacityteam.Audacity"],
    "config":    ["preferences-system", "systemsettings", "org.kde.systemsettings"],
    "lancador":  ["washi-lancador"],
    "sakura":    ["washi-sakura", "user-desktop-symbolic-washi"],
}
PLACES = {
    "folder": ["folder", "inode-directory", "folder-open"],
    "user-home": ["user-home", "folder-home"],
    "user-desktop": ["user-desktop", "folder-desktop"],
    "folder-documents": ["folder-documents"],
    "folder-download": ["folder-download", "folder-downloads"],
    "folder-music": ["folder-music"],
    "folder-pictures": ["folder-pictures", "folder-images"],
    "folder-videos": ["folder-videos", "folder-video"],
    "folder-publicshare": ["folder-publicshare", "folder-public"],
    "folder-templates": ["folder-templates"],
    "folder-red": ["folder-red"],
}

INDEX = """[Icon Theme]
Name=Washi Pixel
Comment=Ícones pixel 16×16 do tema Washi (fallback: Breeze)
Inherits=breeze,hicolor
# os ícones herdados do Breeze têm estilo ColorScheme-Text: sem isto ficam escuros em apps com esquema Sumi
FollowsColorScheme=true
Example=folder
DisplayDepth=32
Directories=apps/scalable,places/scalable

[apps/scalable]
Size=16
MinSize=8
MaxSize=512
Type=Scalable
Context=Applications

[places/scalable]
Size=16
MinSize=8
MaxSize=512
Type=Scalable
Context=Places
"""

def gravar(pasta_dest, nome, conteudo):
    os.makedirs(pasta_dest, exist_ok=True)
    with open(os.path.join(pasta_dest, nome + ".svg"), "w") as f: f.write(conteudo)

if __name__ == "__main__":
    raiz = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "washi-pixel")
    n = 0
    for desenho, nomes in APPS.items():
        s = svg(ICONES[desenho])
        for nome in nomes: gravar(os.path.join(raiz, "apps/scalable"), nome, s); n += 1
    for chave, nomes in PLACES.items():
        s = svg(pasta(EMBLEMAS[chave]))
        for nome in nomes: gravar(os.path.join(raiz, "places/scalable"), nome, s); n += 1
    s = svg(LIXEIRA)
    for nome in ["user-trash", "user-trash-full", "trash-empty"]:
        gravar(os.path.join(raiz, "places/scalable"), nome, s); n += 1
    with open(os.path.join(raiz, "index.theme"), "w") as f: f.write(INDEX)
    print(f"{raiz}: {n} arquivos")
