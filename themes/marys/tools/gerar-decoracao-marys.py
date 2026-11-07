#!/usr/bin/env python3
"""Decoração Aurorae 'MarysPixel' (kawaii rosa e creme). Usa o gerador do Washi sem alterá-lo:
carrega o módulo, troca a paleta em memória e grava o tema na pasta do Mary's.
Uso: gerar-decoracao-marys.py PASTA_DESTINO   (cria PASTA_DESTINO/MarysPixel)
"""
import importlib.util, json, os, re, sys

WASHI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "washi", "tools")
spec = importlib.util.spec_from_file_location("deco", os.path.join(WASHI, "gerar-decoracao.py"))
deco = importlib.util.module_from_spec(spec); spec.loader.exec_module(deco)

deco.C.update({
    "k": "#5A2E3F",   # contorno e tinta (ameixa)
    "w": "#FFF6EC",   # creme
    "p": "#F9D5DF",   # barra de título e botões (rosa claro)
    "q": "#FCE9EE",   # janela inativa
    "h": "#FFF6EC",   # botão em foco
    "r": "#D9578A", "d": "#A83A69",   # fechar
    "m": "#C9A9B4",   # moldura/tinta inativa
    "s": "#8A5A6A",   # título inativo
})
deco.ESTADOS.update({
    "normal":      ("p", "k", "k"),
    "foco":        ("h", "r", "k"),
    "pressionado": ("k", "w", "k"),
    "inativo":     ("q", "m", "m"),
})

def rgb(h): return ",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))
RC = re.sub(r"^ActiveTextColor=.*$", "ActiveTextColor=" + rgb(deco.C["k"]), deco.RC, flags=re.M)
RC = re.sub(r"^InactiveTextColor=.*$", "InactiveTextColor=" + rgb(deco.C["s"]), RC, flags=re.M)
META = json.loads(json.dumps(deco.META))
META["KPlugin"].update({"Id": "MarysPixel", "Name": "Mary's Pixel",
                        "Description": "Decoração pixel kawaii do tema Mary's (sem sombra, sem animação)"})

if __name__ == "__main__":
    raiz = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "MarysPixel")
    os.makedirs(raiz, exist_ok=True)
    open(os.path.join(raiz, "decoration.svg"), "w").write(deco.decoracao_svg())
    for arq, g in deco.BOTOES.items(): open(os.path.join(raiz, arq + ".svg"), "w").write(deco.botao_svg(g))
    open(os.path.join(raiz, "MarysPixelrc"), "w").write(RC)
    json.dump(META, open(os.path.join(raiz, "metadata.json"), "w"), ensure_ascii=False, indent=2)
    print(raiz)
