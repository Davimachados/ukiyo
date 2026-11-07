#!/usr/bin/env python3
"""Ícones pixel 16x16 do tema Washi → SVG (crispEdges). Desenhos originais/genéricos.
Uso: gerar-icones.py PASTA_SAIDA
"""
import os, sys

PAL = {
    "k": "#2B2A28",  # tinta sumi (contorno)
    "w": "#F2EBDD",  # washi
    "p": "#E4D9C4",  # papel sombra
    "r": "#C8102E",  # vermelho torii
    "d": "#8E0B22",  # vermelho escuro
    "g": "#6B8E4E",  # musgo
    "G": "#4F6B3A",  # musgo escuro
    "y": "#D9A441",  # ouro
    "Y": "#FFC857",  # lanterna
    "s": "#F4A7B9",  # sakura
    "S": "#E07A97",  # sakura escuro
    "b": "#5D7FA3",  # azul índigo suave
    "B": "#3E5675",  # índigo escuro
    "m": "#8C857A",  # pedra
}

ICONES = {
# lançador: torii sobre círculo de sol
"lancador": """
................
k..............k
kkkkkkkkkkkkkkkk
.krrrrrrrrrrrrk.
.kkkkkkkkkkkkkk.
...krk.kk.krk...
...krk.kk.krk...
.kkkrkkkkkkrkkk.
.krrrrrrrrrrrrk.
.kkkrkkkkkkrkkk.
...krk....krk...
...krk....krk...
...krk....krk...
...krk....krk...
..kkrkk..kkrkk..
..kkkkk..kkkkk..
""",
# gravação (OBS): câmera com ponto vermelho
"gravacao": """
................
................
..kkkkkkkkkk....
.kwwwwwwwwwwk...
.kwkkkkwwwwwkkk.
.kwkrrkwwwwwkwk.
.kwkrrkwwwwwkwk.
.kwkkkkwwwwwkwk.
.kwwwwwwwwwwkwk.
.kwwwkkkkwwwkkk.
.kwwkrrrrkwwk...
.kwwkrrrrkwwk...
.kwwwkkkkwwwk...
.kppppppppppk...
..kkkkkkkkkk....
................
""",
# edição de vídeo (Kdenlive): claquete
"video": """
................
.kkkkkkkkkkkkk..
.kwkrkwkrkwkrk..
.kkkkkkkkkkkkk..
.kkkkkkkkkkkkk..
.kwwwwwwwwwwwk..
.kwwwwwwwwwwwk..
.kwwkwwwwwwwwk..
.kwwkkkwwwwwwk..
.kwwkkkkkwwwwk..
.kwwkkkkkwwwwk..
.kwwkkkwwwwwwk..
.kwwkwwwwwwwwk..
.kppppppppppppk.
.kkkkkkkkkkkkk..
................
""",
# áudio (Audacity): forma de onda em pergaminho
"audio": """
................
.kkkkkkkkkkkkkk.
.kwwwwwwwwwwwwk.
.kwwwwwgwwwwwwk.
.kwwwwwgwwgwwwk.
.kwwgwwgwwgwwwk.
.kwwgwgggwggwwk.
.kgggggggggggwk.
.kwwgwgggwggwwk.
.kwwgwwgwwgwwwk.
.kwwwwwgwwgwwwk.
.kwwwwwgwwwwwwk.
.kwwwwwwwwwwwwk.
.kppppppppppppk.
.kkkkkkkkkkkkkk.
................
""",
# terminal (Konsole): janela sumi com >_
"terminal": """
................
.kkkkkkkkkkkkkk.
.krrkwwwwwwwwwk.
.kkkkkkkkkkkkkk.
.kkkkkkkkkkkkkk.
.kkwkkkkkkkkkkk.
.kkkwkkkkkkkkkk.
.kkkkwkkkkkkkkk.
.kkkwkkkkkkkkkk.
.kkwkkkkkkkkkkk.
.kkkkkkyyyyykkk.
.kkkkkkkkkkkkkk.
.kkkkkkkkkkkkkk.
.kkkkkkkkkkkkkk.
.kkkkkkkkkkkkkk.
................
""",
# navegador: globo com meridianos índigo
"navegador": """
................
.....kkkkkk.....
...kkbbwbbbkk...
..kbbbbwbbbbbk..
..kbbwwwwwwbbk..
.kbbbbbwbbbbbbk.
.kwwwwwwwwwwwwk.
.kbbgggwbbbbbbk.
.kbgggggbbbgggk.
.kbbgggwbbbgggk.
.kwwwwwwwwwwwwk.
..kbbbbwbgbbbk..
..kbbwwwwwwbbk..
...kkbbwbbbkk...
.....kkkkkk.....
................
""",
# arquivos (Dolphin): pasta de papel com selo
"pasta": """
................
................
.kkkkkk.........
.kyyyyyk........
.kyyyyyykkkkkkk.
.kkkkkkkkkkkkkk.
.kwwwwwwwwwwwwk.
.kwwwwwwwwwwwwk.
.krrrrrrkkrrrrk.
.kddddddyyddddk.
.krrrrrrkkrrrrk.
.kwwwwwwwwwwwwk.
.kppppppppppppk.
.kkkkkkkkkkkkkk.
................
................
""",
# configurações: engrenagem/brasão
"config": """
................
......kkkk......
...kk.kmmk.kk...
..kmmkkmmkkmmk..
..kmmmmmmmmmmk..
...kmmmkkmmmk...
.kkkmmkwwkmmkkk.
.kmmmkwrrwkmmmk.
.kmmmkwrrwkmmmk.
.kkkmmkwwkmmkkk.
...kmmmkkmmmk...
..kmmmmmmmmmmk..
..kmmkkmmkkmmk..
...kk.kmmk.kk...
......kkkk......
................
""",
# sakura (decorativo / mostrar área de trabalho)
"sakura": """
................
.......kk.......
......kssk......
..kk..kssk..kk..
.ksskkkSSkkkssk.
.kssssSyySsssk..
..kkssyYYyssk...
...kSyYYYYySk...
..kkssyYYyssk...
.kssssSyySssssk.
.ksskkkSSkkksk..
..kk..kssk..kk..
......kssk......
.......kk.......
................
................
""",
}

def svg(grid):
    linhas = [l for l in grid.strip("\n").split("\n")]
    assert len(linhas) == 16 and all(len(l) == 16 for l in linhas), [len(l) for l in linhas]
    rects = []
    for y, linha in enumerate(linhas):
        x = 0
        while x < 16:
            c = linha[x]
            if c == ".": x += 1; continue
            x0 = x
            while x < 16 and linha[x] == c: x += 1
            rects.append(f'<rect x="{x0}" y="{y}" width="{x - x0}" height="1" fill="{PAL[c]}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" '
            'shape-rendering="crispEdges">' + "".join(rects) + "</svg>\n")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "icones"
    os.makedirs(out, exist_ok=True)
    for nome, g in ICONES.items():
        with open(os.path.join(out, nome + ".svg"), "w") as f: f.write(svg(g))
    print(f"{len(ICONES)} ícones em {out}")
