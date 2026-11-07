#!/usr/bin/env python3
"""Decoração Aurorae 'TougePixel' — barra preta racing, título branco, foco amarelo, fechar vermelho.
Usa o gerador do Washi sem alterá-lo (paleta trocada em memória).
Uso: gerar-decoracao-touge.py PASTA_DESTINO   (cria PASTA_DESTINO/TougePixel)
"""
import importlib.util, json, os, re, sys
WASHI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "washi", "tools")
spec = importlib.util.spec_from_file_location("deco", os.path.join(WASHI, "gerar-decoracao.py"))
deco = importlib.util.module_from_spec(spec); spec.loader.exec_module(deco)
deco.C.update({"k": "#111111", "w": "#F2F2F0", "p": "#1E1E1E", "q": "#E4E4E1", "h": "#333333",
               "r": "#D7141E", "d": "#8E0B12", "y": "#F5C400", "m": "#9A9A96", "s": "#555555"})
deco.ESTADOS.update({"normal": ("p", "w", "k"), "foco": ("h", "y", "k"), "pressionado": ("y", "k", "k"), "inativo": ("q", "m", "m")})
def rgb(h): return ",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))
RC = re.sub(r"^ActiveTextColor=.*$", "ActiveTextColor=" + rgb(deco.C["w"]), deco.RC, flags=re.M)
RC = re.sub(r"^InactiveTextColor=.*$", "InactiveTextColor=" + rgb(deco.C["s"]), RC, flags=re.M)
META = json.loads(json.dumps(deco.META))
META["KPlugin"].update({"Id": "TougePixel", "Name": "Touge Pixel", "Description": "Decoração pixel racing do tema Touge"})
if __name__ == "__main__":
    raiz = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "TougePixel"); os.makedirs(raiz, exist_ok=True)
    open(os.path.join(raiz, "decoration.svg"), "w").write(deco.decoracao_svg())
    for arq, g in deco.BOTOES.items(): open(os.path.join(raiz, arq + ".svg"), "w").write(deco.botao_svg(g))
    open(os.path.join(raiz, "TougePixelrc"), "w").write(RC)
    json.dump(META, open(os.path.join(raiz, "metadata.json"), "w"), ensure_ascii=False, indent=2); print(raiz)
