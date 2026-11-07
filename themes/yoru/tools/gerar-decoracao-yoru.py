#!/usr/bin/env python3
"""Decoração Aurorae 'YoruPixel' (modo escuro). Usa o gerador do Washi sem alterá-lo: carrega o módulo,
troca só a paleta em memória e grava o tema na pasta do Yoru.
Uso: gerar-decoracao-yoru.py PASTA_DESTINO   (cria PASTA_DESTINO/YoruPixel)
"""
import importlib.util, json, os, re, sys

WASHI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "washi", "tools")
spec = importlib.util.spec_from_file_location("deco", os.path.join(WASHI, "gerar-decoracao.py"))
deco = importlib.util.module_from_spec(spec); spec.loader.exec_module(deco)

# paleta Yoru (o dicionário C é compartilhado pelas funções do gerador)
deco.C.update({
    "k": "#0E0F18",   # contorno / moldura
    "w": "#E6E4EC",   # tinta clara dos botões
    "p": "#2F3250",   # barra de título e fundo dos botões (ativa)
    "q": "#22243A",   # barra/botões da janela inativa
    "h": "#3C4066",   # fundo do botão em foco (hover)
    "r": "#C8102E", "d": "#8E0B22",
    "m": "#5C5E78",   # moldura/tinta inativa
    "s": "#8C8EA6",   # título inativo
})
deco.ESTADOS.update({
    "normal":      ("p", "w", "k"),
    "foco":        ("h", "r", "k"),
    "pressionado": ("k", "w", "k"),
    "inativo":     ("q", "m", "m"),
})

def rgb(h): return ",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))
RC = re.sub(r"^ActiveTextColor=.*$", "ActiveTextColor=" + rgb(deco.C["w"]), deco.RC, flags=re.M)
RC = re.sub(r"^InactiveTextColor=.*$", "InactiveTextColor=" + rgb(deco.C["s"]), RC, flags=re.M)
META = json.loads(json.dumps(deco.META))
META["KPlugin"].update({"Id": "YoruPixel", "Name": "Yoru Pixel",
                        "Description": "Decoração pixel do modo escuro Yoru (sem sombra, sem animação)"})

if __name__ == "__main__":
    raiz = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "YoruPixel")
    os.makedirs(raiz, exist_ok=True)
    open(os.path.join(raiz, "decoration.svg"), "w").write(deco.decoracao_svg())
    for arq, g in deco.BOTOES.items(): open(os.path.join(raiz, arq + ".svg"), "w").write(deco.botao_svg(g))
    open(os.path.join(raiz, "YoruPixelrc"), "w").write(RC)
    json.dump(META, open(os.path.join(raiz, "metadata.json"), "w"), ensure_ascii=False, indent=2)
    print(raiz)
