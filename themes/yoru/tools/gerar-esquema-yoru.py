#!/usr/bin/env python3
"""Esquema de cores KDE "Yoru" (夜, noite) — modo escuro, separado do tema Washi.
Uso: gerar-esquema-yoru.py SAIDA.colors   (também imprime a tabela de contraste)
"""
import sys

Y = dict(
    win="#1C1E2E", win2="#262940", view="#161826", view2="#1C1E2E", btn="#262940", btn2="#2F3250",
    head="#14151F", head2="#1C1E2E", headi="#1C1E2E",
    tip="#262940", tip2="#2F3250", tipfg="#E6E4EC", tipfgi="#9A9CB4",
    comp="#12131D", comp2="#1C1E2E", compfg="#E6E4EC",
    sel="#B3263B", sel2="#9E1F33", selfg="#F2F0F6", selfgi="#D8D6E2", sellink="#FFE7A8",
    fg="#E6E4EC", fgi="#9A9CB4", active="#E3B65A", link="#7FB0DB", visited="#B79BD6",
    neg="#F0707F", neu="#E3B65A", pos="#8FB36F", focus="#7FB0DB", hover="#E3B65A")

def rgb(h): return ",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))

def esquema(nome, c):
    sets = {"Window": (c["win"], c["win2"]), "View": (c["view"], c["view2"]), "Button": (c["btn"], c["btn2"]),
            "Header": (c["head"], c["head2"]), "Tooltip": (c["tip"], c["tip2"]),
            "Complementary": (c["comp"], c["comp2"]), "Selection": (c["sel"], c["sel2"])}
    out = [f"[ColorEffects:Disabled]\nColor={rgb(c['win2'])}\nColorAmount=0\nColorEffect=0\nContrastAmount=0.6\n"
           f"ContrastEffect=1\nIntensityAmount=0\nIntensityEffect=0\n",
           f"[ColorEffects:Inactive]\nChangeSelectionColor=true\nColor={rgb(c['win2'])}\nColorAmount=0.025\nColorEffect=2\n"
           f"ContrastAmount=0.1\nContrastEffect=2\nEnable=false\nIntensityAmount=0\nIntensityEffect=0\n"]
    for s, (bg, alt) in sets.items():
        fg = c["selfg"] if s == "Selection" else c["tipfg"] if s == "Tooltip" else c["compfg"] if s == "Complementary" else c["fg"]
        fgi = c["selfgi"] if s == "Selection" else c["tipfgi"] if s in ("Tooltip", "Complementary") else c["fgi"]
        grupos = [f"Colors:{s}"] + (["Colors:Header][Inactive"] if s == "Header" else [])
        for g in grupos:
            b = c["headi"] if g.endswith("Inactive") else bg
            out.append(f"""[{g}]
BackgroundAlternate={rgb(alt)}
BackgroundNormal={rgb(b)}
DecorationFocus={rgb(c['focus'])}
DecorationHover={rgb(c['hover'])}
ForegroundActive={rgb(c['selfg'] if s == 'Selection' else c['active'])}
ForegroundInactive={rgb(fgi)}
ForegroundLink={rgb(c['sellink'] if s == 'Selection' else c['link'])}
ForegroundNegative={rgb(c['neg'])}
ForegroundNeutral={rgb(c['neu'])}
ForegroundNormal={rgb(fg)}
ForegroundPositive={rgb(c['pos'])}
ForegroundVisited={rgb(c['visited'])}
""")
    out.append(f"[General]\nColorScheme={nome}\nName={nome}\nshadeSortColumn=true\n\n[KDE]\ncontrast=4\n")
    out.append(f"[WM]\nactiveBackground={rgb(c['head'])}\nactiveBlend={rgb(c['head'])}\nactiveForeground={rgb(c['fg'])}\n"
               f"inactiveBackground={rgb(c['headi'])}\ninactiveBlend={rgb(c['headi'])}\ninactiveForeground={rgb(c['fgi'])}\n")
    return "\n".join(out)

def lum(h):
    v = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]
def cr(a, b): return (max(lum(a), lum(b)) + .05) / (min(lum(a), lum(b)) + .05)
def mix(a, b, t): return "#%02X%02X%02X" % tuple(round(int(a[i:i+2], 16) * (1 - t) + int(b[i:i+2], 16) * t) for i in (1, 3, 5))

if __name__ == "__main__":
    open(sys.argv[1], "w").write(esquema("Yoru", Y))
    c = Y
    casos = [("texto / janela", c["fg"], c["win"]), ("texto / campos", c["fg"], c["view"]), ("texto / botões", c["fg"], c["btn"]),
             ("texto secundário / janela", c["fgi"], c["win"]), ("seleção", c["selfg"], c["sel"]), ("link / campos", c["link"], c["view"]),
             ("visitado / campos", c["visited"], c["view"]), ("erro / janela", c["neg"], c["win"]), ("aviso / janela", c["neu"], c["win"]),
             ("sucesso / janela", c["pos"], c["win"]), ("dica", c["tipfg"], c["tip"]),
             ("desabilitado / janela", mix(c["fg"], c["win"], 0.6), c["win"])]
    for n, a, b in casos:
        r = cr(a, b); print(f"{n:28s} {a} / {b}  {r:5.2f}:1  {'AAA' if r >= 7 else 'AA' if r >= 4.5 else '≥3' if r >= 3 else 'FALHA'}")
