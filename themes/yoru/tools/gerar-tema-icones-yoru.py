#!/usr/bin/env python3
"""Tema de ícones 'yoru-pixel' (modo escuro). Reaproveita as grades do Washi SEM alterá-las e acrescenta
uma borda externa clara de 1 px (sticker), para os contornos escuros não sumirem sobre fundo índigo.
Herda breeze-dark (ícones simbólicos claros) e segue o esquema de cores.
Uso: gerar-tema-icones-yoru.py PASTA_DESTINO   (cria PASTA_DESTINO/yoru-pixel)
"""
import importlib.util, os, sys

WASHI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "washi", "tools")
def carregar(nome, arq):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(WASHI, arq))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ic = carregar("icones", "gerar-icones.py")
te = carregar("tema", "gerar-tema-icones.py")

PAL = dict(ic.PAL); PAL["o"] = "#7A7DA0"          # cor da borda externa (≈4:1 sobre #1C1E2E)

def com_borda(grade_txt):
    g = [list(l) for l in grade_txt.strip("\n").split("\n")]
    out = [r[:] for r in g]
    for y in range(16):
        for x in range(16):
            if g[y][x] != ".": continue
            if any(0 <= y + dy < 16 and 0 <= x + dx < 16 and g[y + dy][x + dx] not in (".",)
                   for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                out[y][x] = "o"
    return "\n".join("".join(r) for r in out)

def svg(grade_txt):
    linhas = grade_txt.strip("\n").split("\n")
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

INDEX = te.INDEX.replace("Name=Washi Pixel", "Name=Yoru Pixel") \
    .replace("Comment=Ícones pixel 16×16 do tema Washi (fallback: Breeze)", "Comment=Ícones pixel do modo escuro Yoru (fallback: Breeze Dark)") \
    .replace("Inherits=breeze,hicolor", "Inherits=breeze-dark,breeze,hicolor")
assert "FollowsColorScheme=true" in INDEX and "breeze-dark" in INDEX

def gravar(d, nome, conteudo):
    os.makedirs(d, exist_ok=True); open(os.path.join(d, nome + ".svg"), "w").write(conteudo)

if __name__ == "__main__":
    raiz = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "yoru-pixel"); n = 0
    for desenho, nomes in te.APPS.items():
        s = svg(com_borda(ic.ICONES[desenho]))
        for nome in nomes: gravar(os.path.join(raiz, "apps/scalable"), nome, s); n += 1
    for chave, nomes in te.PLACES.items():
        s = svg(com_borda(te.pasta(te.EMBLEMAS[chave])))
        for nome in nomes: gravar(os.path.join(raiz, "places/scalable"), nome, s); n += 1
    s = svg(com_borda(te.LIXEIRA))
    for nome in ["user-trash", "user-trash-full", "trash-empty"]: gravar(os.path.join(raiz, "places/scalable"), nome, s); n += 1
    open(os.path.join(raiz, "index.theme"), "w").write(INDEX)
    print(f"{raiz}: {n} arquivos")
