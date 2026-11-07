"""Legendas do Henshū: da transcrição (palavras com tempo no ARQUIVO) para frases no tempo da LINHA DO TEMPO.

- Transcrições ficam em cache por arquivo: <vídeo>/.henshu/transcricoes/<chave>.json (geradas por transcrever.py).
- As legendas revisáveis ficam em <vídeo>/legendas/legendas.json:
    {"versao": 1, "segmentos": [{"inicio": 0.4, "fim": 1.9, "texto": "olha só isso",
                                 "palavras": [{"p": "olha", "i": 0.4, "f": 0.7}, …]}]}
  Pode editar "texto" à vontade; se o número de palavras mudar, o karaokê distribui o tempo por igual.
- Saídas: ASS (queimado no vídeo, com estilos), SRT (para subir na plataforma), capítulos do YouTube.
"""
import hashlib, json, os, re

ARQ = os.path.join("legendas", "legendas.json")
LIMITES = {"vertical": dict(palavras=4, letras=24, dur=2.0), "horizontal": dict(palavras=9, letras=42, dur=4.0)}


def chave(path):
    st = os.stat(path)
    return hashlib.sha1(f"{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}".encode()).hexdigest()[:16]


def dir_cache(pasta):
    d = os.path.join(pasta, ".henshu", "transcricoes"); os.makedirs(d, exist_ok=True); return d


def cache_de(pasta, path):
    return os.path.join(dir_cache(pasta), chave(path) + ".json")


def faltando(pasta, clipes):
    """Arquivos usados no projeto que ainda não foram transcritos."""
    vistos, out = set(), []
    for c in clipes:
        if c["caminho"] in vistos or not c["audio"]: continue
        vistos.add(c["caminho"])
        if not os.path.exists(cache_de(pasta, c["caminho"])): out.append(c["caminho"])
    return out


def carregar(pasta):
    p = os.path.join(pasta, ARQ)
    if not os.path.exists(p): return None
    with open(p, encoding="utf-8") as f: return json.load(f)


def salvar(pasta, dados):
    p = os.path.join(pasta, ARQ); os.makedirs(os.path.dirname(p), exist_ok=True)
    if os.path.exists(p):   # guarda a versão anterior (revisões manuais não se perdem)
        os.replace(p, p + ".anterior")
    with open(p, "w", encoding="utf-8") as f: json.dump(dados, f, ensure_ascii=False, indent=1); f.write("\n")


def gerar(pasta, d, clipes):
    """Monta as frases a partir das transcrições em cache e do corte atual do projeto."""
    lim = LIMITES[d["formato"]["preset"]]
    palavras = []
    for n, c in enumerate(clipes):
        cp = cache_de(pasta, c["caminho"]) if c["audio"] else None
        if not cp or not os.path.exists(cp): continue
        with open(cp, encoding="utf-8") as f: tr = json.load(f)
        for w in tr["palavras"]:
            meio = (w["i"] + w["f"]) / 2
            if not (c["inicio"] <= meio < c["fim_real"]): continue
            ti = c["na_linha"] + (max(w["i"], c["inicio"]) - c["inicio"]) / c["velocidade"]
            tf = c["na_linha"] + (min(w["f"], c["fim_real"]) - c["inicio"]) / c["velocidade"]
            palavras.append({"p": w["p"].strip(), "i": round(ti, 3), "f": round(max(tf, ti + 0.05), 3), "clipe": n})
    palavras.sort(key=lambda w: w["i"])
    segs, atual = [], []
    def fecha():
        if atual:
            segs.append({"inicio": atual[0]["i"], "fim": atual[-1]["f"], "texto": " ".join(w["p"] for w in atual),
                         "palavras": [{"p": w["p"], "i": w["i"], "f": w["f"]} for w in atual]})
            atual.clear()
    for w in palavras:
        if atual:
            texto = " ".join(x["p"] for x in atual + [w])
            if (len(atual) >= lim["palavras"] or len(texto) > lim["letras"] or w["f"] - atual[0]["i"] > lim["dur"]
                    or w["i"] - atual[-1]["f"] > 0.7 or w["clipe"] != atual[-1]["clipe"]
                    or re.search(r"[.!?…]$", atual[-1]["p"])):
                fecha()
        atual.append(w)
    fecha()
    for a, b in zip(segs, segs[1:]):   # sem sobreposição e sem piscar entre frases próximas
        if b["inicio"] - a["fim"] < 0.25: a["fim"] = b["inicio"]
    return {"versao": 1, "segmentos": segs}


# ---- formatos de saída -----------------------------------------------------------------------------------------
def _ts_srt(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def para_srt(dados):
    out = []
    for n, s in enumerate(dados["segmentos"], 1):
        out.append(f"{n}\n{_ts_srt(s['inicio'])} --> {_ts_srt(s['fim'])}\n{s['texto']}\n")
    return "\n".join(out)


def _ts_ass(t):
    cs = int(round(max(0, t) * 100)); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"


def _cor(hexrgb, alfa=0):
    h = hexrgb.lstrip("#"); return f"&H{alfa:02X}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def _esc(t):
    return t.replace("\\", "/").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def para_ass(dados, d):
    W, H = d["formato"]["largura"], d["formato"]["altura"]; lg = d["legendas"]
    vertical = d["formato"]["preset"] == "vertical"
    tam = lg["tamanho"] or (78 if vertical else 56)
    alin = {"base": 2, "centro": 5, "topo": 8}[lg["posicao"]]
    margem = int(H * (0.22 if vertical else 0.08)) if lg["posicao"] != "centro" else 0
    if lg["estilo"] == "pixel":
        fonte, prim, borda, fundo, bs, out = "DotGothic16", _cor("#F2EBDD"), _cor("#1B1A22"), _cor("#1B1A22", 0x30), 3, max(6, tam // 6)
    else:
        fonte, prim, borda, fundo, bs, out = "Noto Sans", _cor("#FFFFFF"), _cor("#000000"), _cor("#000000", 0x80), 1, max(3, tam // 11)
    destaque = _cor("#FFD84A") if lg["estilo"] != "pixel" else _cor("#E8694A")
    cab = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
           "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
           "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
           "MarginR, MarginV, Encoding\n"
           f"Style: Base,{fonte},{tam},{prim},{prim},{borda},{fundo},{0 if lg['estilo'] == 'pixel' else -1},0,0,0,100,100,0,0,"
           f"{bs},{out},0,{alin},{int(W * 0.08)},{int(W * 0.08)},{margem},1\n\n"
           "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    for s in dados["segmentos"]:
        palavras_txt = s["texto"].split()
        if lg["estilo"] == "karaoke" and palavras_txt:
            ws = s.get("palavras") or []
            if len(ws) != len(palavras_txt):   # texto revisado: distribui o tempo por igual
                passo = (s["fim"] - s["inicio"]) / len(palavras_txt)
                ws = [{"i": s["inicio"] + k * passo, "f": s["inicio"] + (k + 1) * passo} for k in range(len(palavras_txt))]
            for k, w in enumerate(ws):
                ini = s["inicio"] if k == 0 else w["i"]
                fim = ws[k + 1]["i"] if k + 1 < len(ws) else s["fim"]
                if fim <= ini: continue
                txt = " ".join(("{\\c" + destaque + "&}" + _esc(p) + "{\\r}") if j == k else _esc(p) for j, p in enumerate(palavras_txt))
                ev.append(f"Dialogue: 0,{_ts_ass(ini)},{_ts_ass(fim)},Base,,0,0,0,,{txt}")
        else:
            ev.append(f"Dialogue: 0,{_ts_ass(s['inicio'])},{_ts_ass(s['fim'])},Base,,0,0,0,,{_esc(s['texto'])}")
    return cab + "\n".join(ev) + "\n"


def capitulos_youtube(caps, total):
    """Texto para colar na descrição do YouTube (o primeiro capítulo precisa começar em 0:00)."""
    if not caps: return ""
    caps = sorted(caps, key=lambda c: c["inicio"])
    if caps[0]["inicio"] > 0: caps = [{"inicio": 0.0, "titulo": "Início"}] + caps
    def ts(t):
        t = int(t); h, r = divmod(t, 3600); m, s = divmod(r, 60)
        return f"{h}:{m:02}:{s:02}" if total >= 3600 else f"{m}:{s:02}"
    return "\n".join(f"{ts(c['inicio'])} {c['titulo']}" for c in caps) + "\n"


def ffmetadata(caps, total):
    """Capítulos embutidos no MP4 (players e o YouTube leem)."""
    caps = sorted(caps, key=lambda c: c["inicio"]); out = [";FFMETADATA1"]
    for i, c in enumerate(caps):
        fim = caps[i + 1]["inicio"] if i + 1 < len(caps) else total
        out += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(c['inicio'] * 1000)}", f"END={int(fim * 1000)}",
                "title=" + re.sub(r"([=;#\\\n])", r"\\\1", c["titulo"])]
    return "\n".join(out) + "\n"
