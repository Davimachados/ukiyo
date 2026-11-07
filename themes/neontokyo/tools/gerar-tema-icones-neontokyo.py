#!/usr/bin/env python3
"""Tema de ícones 'neontokyo-pixel'. Grades do Washi (sem alterá-las) recoloridas em neon + borda ciano de 1 px.
Uso: gerar-tema-icones-neontokyo.py PASTA_DESTINO   (cria PASTA_DESTINO/neontokyo-pixel)
"""
import importlib.util, os, sys
YT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "yoru", "tools", "gerar-tema-icones-yoru.py")
spec = importlib.util.spec_from_file_location("yoru_ic", YT); yi = importlib.util.module_from_spec(spec); spec.loader.exec_module(yi)
yi.PAL.clear(); yi.PAL.update({
    "k": "#05060C", "w": "#DCE8FF", "p": "#8FA3D0", "r": "#FF2E88", "d": "#B0145E", "g": "#39FF88", "G": "#1FAF5E",
    "y": "#FFE600", "Y": "#FFF27A", "s": "#FF7AB8", "S": "#FF2E88", "b": "#00E5FF", "B": "#0088AA", "m": "#5A6688",
    "o": "#00B8D4"})                                   # borda = brilho ciano
INDEX = yi.INDEX.replace("Name=Yoru Pixel", "Name=Neon Tokyo Pixel").replace(
    "Comment=Ícones pixel do modo escuro Yoru (fallback: Breeze Dark)", "Comment=Ícones pixel neon do tema Neon Tokyo (fallback: Breeze Dark)")
if __name__ == "__main__":
    raiz = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "neontokyo-pixel"); n = 0
    for desenho, nomes in yi.te.APPS.items():
        s = yi.svg(yi.com_borda(yi.ic.ICONES[desenho]))
        for nome in nomes: yi.gravar(os.path.join(raiz, "apps/scalable"), nome, s); n += 1
    for chave, nomes in yi.te.PLACES.items():
        s = yi.svg(yi.com_borda(yi.te.pasta(yi.te.EMBLEMAS[chave])))
        for nome in nomes: yi.gravar(os.path.join(raiz, "places/scalable"), nome, s); n += 1
    s = yi.svg(yi.com_borda(yi.te.LIXEIRA))
    for nome in ["user-trash", "user-trash-full", "trash-empty"]: yi.gravar(os.path.join(raiz, "places/scalable"), nome, s); n += 1
    open(os.path.join(raiz, "index.theme"), "w").write(INDEX); print(f"{raiz}: {n} arquivos")
