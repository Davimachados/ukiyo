#!/usr/bin/env python3
"""Decoração Aurorae 'NeonTokyoPixel' — moldura ciano neon, barra azul-noite, fechar magenta.
Usa o gerador do Washi sem alterá-lo (paleta trocada em memória).
Uso: gerar-decoracao-neontokyo.py PASTA_DESTINO   (cria PASTA_DESTINO/NeonTokyoPixel)
"""
import importlib.util, json, os, re, sys
WASHI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "washi", "tools")
spec = importlib.util.spec_from_file_location("deco", os.path.join(WASHI, "gerar-decoracao.py"))
deco = importlib.util.module_from_spec(spec); spec.loader.exec_module(deco)
deco.C.update({"k": "#00B8D4", "w": "#E6F1FF", "p": "#151A2E", "q": "#0B0D17", "h": "#1E2440",
               "r": "#FF2E88", "d": "#B0145E", "m": "#2E3A5A", "s": "#8A9BC0"})
deco.ESTADOS.update({"normal": ("p", "w", "k"), "foco": ("h", "r", "k"), "pressionado": ("k", "p", "k"), "inativo": ("q", "m", "m")})
def rgb(h): return ",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))
RC = re.sub(r"^ActiveTextColor=.*$", "ActiveTextColor=" + rgb(deco.C["w"]), deco.RC, flags=re.M)
RC = re.sub(r"^InactiveTextColor=.*$", "InactiveTextColor=" + rgb(deco.C["s"]), RC, flags=re.M)
META = json.loads(json.dumps(deco.META))
META["KPlugin"].update({"Id": "NeonTokyoPixel", "Name": "Neon Tokyo Pixel", "Description": "Decoração pixel cyberpunk do tema Neon Tokyo"})
if __name__ == "__main__":
    raiz = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "NeonTokyoPixel"); os.makedirs(raiz, exist_ok=True)
    open(os.path.join(raiz, "decoration.svg"), "w").write(deco.decoracao_svg())
    for arq, g in deco.BOTOES.items(): open(os.path.join(raiz, arq + ".svg"), "w").write(deco.botao_svg(g))
    open(os.path.join(raiz, "NeonTokyoPixelrc"), "w").write(RC)
    json.dump(META, open(os.path.join(raiz, "metadata.json"), "w"), ensure_ascii=False, indent=2); print(raiz)
