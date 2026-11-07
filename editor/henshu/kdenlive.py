"""Exporta o projeto do Henshū para um projeto do Kdenlive (.kdenlive), para ajuste fino.

Escreve o formato clássico de documento do Kdenlive (versão 0.98, um "maintractor" com trilhas), que o Kdenlive
24.x abre e converte sozinho para o formato atual. Só biblioteca padrão.

O que vai para o Kdenlive:
- clipes em sequência com os cortes, velocidade (tom preservado), volume e "preencher" (efeito Transformar);
- transições: fade → efeitos de fade; dissolver → clipes alternados em V1/V2 com a composição Dissolver;
- textos → títulos do Kdenlive numa trilha própria; música → trilha de áudio em loop com fade final;
- legendas → <projeto>.kdenlive.ass + filtro de legendas (aparece como trilha de legendas);
- capítulos: gravados como guias, mas o Kdenlive 24.12 não os mostra ao abrir este formato (limitação conhecida;
  os capítulos continuam embutidos no MP4 exportado e em export/<nome>_capitulos.txt).
Testado abrindo no Kdenlive 24.12.3: trilhas, cortes, velocidade, fades, dissolver, preencher, títulos, música e legendas.
Uso: python3 -m henshu.kdenlive <pasta-do-vídeo>   →  imprime o caminho do .kdenlive
"""
import json, math, os, sys
from xml.etree import ElementTree as ET
from xml.dom import minidom
from . import projeto as P, legendas as L

FONTE = {"padrao": ("Noto Sans", 700), "pixel": ("DotGothic16", 400)}


def _prop(el, nome, valor):
    p = ET.SubElement(el, "property", {"name": nome}); p.text = str(valor); return p


class Doc:
    def __init__(self, d):
        self.fps = int(d["formato"]["fps"]); self.W = d["formato"]["largura"]; self.H = d["formato"]["altura"]
        self.mlt = ET.Element("mlt", {"LC_NUMERIC": "C", "version": "7.30.0", "producer": "main_bin"})
        self.n = 0; self.kid = 3; self.bin = []

    def f(self, s):                       # segundos → quadros
        return int(round(s * self.fps))

    def clock(self, quadros):             # quadros → "hh:mm:ss.mmm" (como o Kdenlive grava)
        s = quadros / self.fps; h = int(s // 3600); m = int((s % 3600) // 60)
        return f"{h:02d}:{m:02d}:{s - h * 3600 - m * 60:06.3f}"

    def produtor(self, props, quadros, no_bin=True, kid=None):
        pid = f"producer{self.n}"; self.n += 1
        if kid is None: self.kid += 1; kid = self.kid
        el = ET.SubElement(self.mlt, "producer", {"id": pid, "in": self.clock(0), "out": self.clock(max(quadros - 1, 0))})
        _prop(el, "length", quadros)
        for k, v in props.items(): _prop(el, k, v)
        _prop(el, "kdenlive:id", kid)
        if no_bin: self.bin.append((pid, kid, quadros))
        return pid, kid


def _titulo_xml(t, W, H, dur_q):
    familia, peso = FONTE[t["fonte"]]
    tam = int(t["tamanho"]); larg = int(W * 0.9); x = (W - larg) // 2
    alt = int(tam * 1.4 * (t["texto"].count("\n") + 1))
    y = {"topo": int(H * 0.12), "centro": (H - alt) // 2, "base": H - alt - int(H * 0.2)}[t["posicao"]]
    r, g, b = (int(t["cor"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    raiz = ET.Element("kdenlivetitle", {"duration": str(dur_q), "LC_NUMERIC": "C", "width": str(W), "height": str(H), "out": str(dur_q - 1)})
    item = ET.SubElement(raiz, "item", {"type": "QGraphicsTextItem", "z-index": "0"})
    pos = ET.SubElement(item, "position", {"x": str(x), "y": str(y)})
    ET.SubElement(pos, "transform").text = "1,0,0,0,1,0,0,0,1"
    cont = ET.SubElement(item, "content", {
        "font": familia, "font-pixel-size": str(tam), "font-weight": str(peso), "font-italic": "0", "font-underline": "0",
        "font-color": f"{r},{g},{b},255", "font-outline": str(max(2, tam // 14)), "font-outline-color": "0,0,0,220",
        "alignment": "4", "box-width": str(larg), "box-height": str(alt), "line-spacing": "0", "letter-spacing": "0",
        "shadow": "0;#64000000;3;3;3", "typewriter": "0;2;1;0;0"})
    cont.text = t["texto"]
    ET.SubElement(raiz, "startviewport", {"rect": f"0,0,{W},{H}"})
    ET.SubElement(raiz, "endviewport", {"rect": f"0,0,{W},{H}"})
    ET.SubElement(raiz, "background", {"color": "0,0,0,0"})
    return ET.tostring(raiz, encoding="unicode")


def _registro(pasta):
    return os.path.join(pasta, ".henshu", "kdenlive.json")


def _hash(path):
    import hashlib
    with open(path, "rb") as fh: return hashlib.sha256(fh.read()).hexdigest()


def _registrar(pasta, saida):
    os.makedirs(os.path.join(pasta, ".henshu"), exist_ok=True)
    try: reg = json.load(open(_registro(pasta)))
    except (OSError, ValueError): reg = {}
    reg[os.path.basename(saida)] = _hash(saida)
    json.dump(reg, open(_registro(pasta), "w"), indent=1)


def destino(pasta):
    """<nome>.kdenlive; se esse arquivo foi alterado no Kdenlive depois da última exportação (ajustes seus),
    não sobrescreve: usa <nome>-2.kdenlive, -3… (o primeiro livre ou ainda não mexido)."""
    nome = os.path.basename(pasta.rstrip("/"))
    try: reg = json.load(open(_registro(pasta)))
    except (OSError, ValueError): reg = {}
    n = 1
    while True:
        arq = os.path.join(pasta, f"{nome}.kdenlive" if n == 1 else f"{nome}-{n}.kdenlive")
        if not os.path.exists(arq) or reg.get(os.path.basename(arq)) == _hash(arq):
            return arq
        n += 1


def exportar(pasta, d=None):
    d = d or P.carregar(pasta)
    clipes, total = P.clipes_resolvidos(pasta, d)
    if not clipes: raise P.ErroProjeto("o projeto ainda não tem clipes")
    doc = Doc(d); W, H, fps = doc.W, doc.H, doc.fps
    vertical = d["formato"]["preset"] == "vertical"
    ET.SubElement(doc.mlt, "profile", {
        "description": "Vertical HD 30 fps" if vertical else "HD 1080p 30 fps", "width": str(W), "height": str(H),
        "frame_rate_num": str(fps), "frame_rate_den": "1", "progressive": "1", "sample_aspect_num": "1", "sample_aspect_den": "1",
        "display_aspect_num": "9" if vertical else "16", "display_aspect_den": "16" if vertical else "9", "colorspace": "709"})

    # ---- produtores de mídia (um por arquivo) e versões com velocidade (timewarp, vídeo e áudio separados)
    base, warp = {}, {}
    for c in clipes:
        if c["caminho"] not in base:
            q = doc.f(P.duracao_arquivo(c["caminho"]))
            base[c["caminho"]] = doc.produtor({"mlt_service": "avformat-novalidate", "resource": c["caminho"],
                                               "kdenlive:clipname": os.path.basename(c["caminho"])}, q)
        v = c["velocidade"]
        if abs(v - 1) > 1e-3:
            for audio in (False, True):
                k = (c["caminho"], v, audio)
                if k not in warp:
                    q = doc.f(P.duracao_arquivo(c["caminho"]) / v)
                    warp[k] = doc.produtor({"mlt_service": "timewarp", "resource": f"{v:g}:{c['caminho']}", "warp_speed": f"{v:g}",
                                            "warp_resource": c["caminho"], "warp_pitch": "1",
                                            "set.test_audio": "0" if audio else "1", "set.test_image": "1" if audio else "0"},
                                           q, no_bin=False, kid=base[c["caminho"]][1])
    musica = None
    if d.get("musica"):
        mp = os.path.normpath(os.path.join(pasta, d["musica"]["arquivo"]))
        musica = (mp, doc.f(P.duracao_arquivo(mp)))
        musica = (*doc.produtor({"mlt_service": "avformat-novalidate", "resource": mp, "kdenlive:clipname": os.path.basename(mp)}, musica[1]), musica[1])
    titulos = []
    for t in d["textos"]:
        q = max(1, doc.f(min(t["fim"], total)) - doc.f(t["inicio"]))
        pid, _ = doc.produtor({"mlt_service": "kdenlivetitle", "kdenlive:clipname": t["texto"].replace("\n", " ")[:40],
                               "kdenlive:clip_type": "2", "force_reload": "0", "xmldata": _titulo_xml(t, W, H, q)}, q)
        titulos.append((t, pid, q))

    # ---- bin
    main_bin = ET.Element("playlist", {"id": "main_bin"})
    _prop(main_bin, "kdenlive:docproperties.decimalPoint", ".")
    _prop(main_bin, "kdenlive:docproperties.version", "0.98")
    _prop(main_bin, "kdenlive:docproperties.profile", "vertical_hd_30" if vertical else "atsc_1080p_30")
    guias = [{"pos": doc.f(c["inicio"]), "comment": c["titulo"], "type": 0} for c in d["capitulos"]]
    _prop(main_bin, "kdenlive:docproperties.guides", json.dumps(guias, ensure_ascii=False))
    _prop(main_bin, "kdenlive:docproperties.guidesCategories", json.dumps([{"color": "#9b59b6", "comment": "Capítulos", "index": 0}], ensure_ascii=False))
    _prop(main_bin, "xml_retain", "1")
    for pid, kid, q in doc.bin:
        e = ET.SubElement(main_bin, "entry", {"producer": pid, "in": doc.clock(0), "out": doc.clock(max(q - 1, 0))}); _prop(e, "kdenlive:id", kid)
    doc.mlt.append(main_bin)
    black = ET.SubElement(doc.mlt, "producer", {"id": "black", "in": doc.clock(0), "out": doc.clock(doc.f(total) + fps)})
    for k, v in {"length": 2147483647, "eof": "continue", "resource": "black", "aspect_ratio": 1, "mlt_service": "color",
                 "kdenlive:playlistid": "black_track", "mlt_image_format": "rgba", "set.test_audio": 0}.items():
        _prop(black, k, v)   # fundo exatamente como o Kdenlive grava: produtor "black" dentro da playlist "black_track"
    pl_black = ET.SubElement(doc.mlt, "playlist", {"id": "black_track"})
    ET.SubElement(pl_black, "entry", {"producer": "black", "in": doc.clock(0), "out": doc.clock(doc.f(total) + fps)})

    # ---- distribui os clipes: um dissolver alterna a trilha (V1/V2 e A1/A2) para os clipes se sobreporem
    trilha = []; atual = 0
    for i, c in enumerate(clipes):
        if i > 0 and clipes[i - 1]["sobreposicao"] > 0: atual = 1 - atual
        trilha.append(atual)

    def entrada_clipe(pl, c, i, audio, pos_q):
        v = c["velocidade"]
        pid, kid = (warp[(c["caminho"], v, audio)] if abs(v - 1) > 1e-3 else base[c["caminho"]])
        ini = doc.f(c["inicio"] / v); dur = max(1, doc.f(c["na_linha"] + c["duracao"]) - doc.f(c["na_linha"]))
        e = ET.SubElement(pl, "entry", {"producer": pid, "in": doc.clock(ini), "out": doc.clock(ini + dur - 1)})
        _prop(e, "kdenlive:id", kid)
        ant = clipes[i - 1] if i > 0 else None
        fi = doc.f(ant["transicao"]["duracao"]) if ant and ant["transicao"]["tipo"] == "fade" else 0
        fo = doc.f(c["transicao"]["duracao"]) if c["transicao"]["tipo"] == "fade" and i < len(clipes) - 1 else 0
        if audio:   # sobreposição do dissolver vira crossfade de volume
            if ant and ant["sobreposicao"]: fi = doc.f(ant["sobreposicao"])
            if c["sobreposicao"]: fo = doc.f(c["sobreposicao"])
        def filtro(nome, a, b, props):
            fl = ET.SubElement(e, "filter", {"in": doc.clock(a), "out": doc.clock(b)})
            for k, val in props.items(): _prop(fl, k, val)
        if fi:
            filtro("in", ini, ini + fi, {"mlt_service": "volume", "kdenlive_id": "fadein", "gain": "0", "end": "1"} if audio
                   else {"mlt_service": "brightness", "kdenlive_id": "fade_from_black", "start": "0", "end": "1"})
        if fo:
            filtro("out", ini + dur - fo, ini + dur - 1, {"mlt_service": "volume", "kdenlive_id": "fadeout", "gain": "1", "end": "0"} if audio
                   else {"mlt_service": "brightness", "kdenlive_id": "fade_to_black", "start": "1", "end": "0"})
        if audio and abs(c["volume"] - 1) > 1e-3:
            db = -60 if c["volume"] <= 0.001 else 20 * math.log10(c["volume"])
            fl = ET.SubElement(e, "filter"); _prop(fl, "mlt_service", "volume"); _prop(fl, "kdenlive_id", "volume")
            _prop(fl, "level", f"00:00:00.000={db:.2f}")
        if not audio and c["enquadrar"] == "preencher" and c["largura_orig"] and c["altura_orig"]:
            s = max(W / c["largura_orig"], H / c["altura_orig"]); sw, sh = c["largura_orig"] * s, c["altura_orig"] * s
            x, y = -(sw - W) * c["foco_x"], -(sh - H) * c["foco_y"]
            fl = ET.SubElement(e, "filter")
            for k, val in {"mlt_service": "qtblend", "kdenlive_id": "qtblend", "rect": f"{x:.0f} {y:.0f} {sw:.0f} {sh:.0f} 1",
                           "rotation": "0", "compositing": "0", "distort": "0", "rotate_center": "1"}.items():
                _prop(fl, k, val)
        return dur

    def preencher_trilha(pl, itens):   # itens: [(inicio_q, gerador(pl) -> dur_q)]
        pos = 0
        for ini_q, ger in sorted(itens, key=lambda x: x[0]):
            if ini_q > pos: ET.SubElement(pl, "blank", {"length": doc.clock(ini_q - pos)})
            pos = max(pos, ini_q) + ger(pl)

    trilhas = []   # (nome, audio, itens) de baixo para cima, como o Kdenlive grava
    if musica:
        mid, mkid, mq = musica; tq = doc.f(total); itens = []; p = 0; vol = d["musica"]["volume"]
        while p < tq:
            dq = min(mq, tq - p)
            def ger(pl, dq=dq, ultimo=(p + mq >= tq)):
                e = ET.SubElement(pl, "entry", {"producer": mid, "in": doc.clock(0), "out": doc.clock(dq - 1)}); _prop(e, "kdenlive:id", mkid)
                fl = ET.SubElement(e, "filter"); _prop(fl, "mlt_service", "volume"); _prop(fl, "kdenlive_id", "volume")
                _prop(fl, "level", f"00:00:00.000={(-60 if vol <= 0.001 else 20 * math.log10(vol)):.2f}")
                if ultimo:
                    a = max(0, dq - doc.f(1.5)); fo = ET.SubElement(e, "filter", {"in": doc.clock(a), "out": doc.clock(dq - 1)})
                    for k, val in {"mlt_service": "volume", "kdenlive_id": "fadeout", "gain": "1", "end": "0"}.items(): _prop(fo, k, val)
                return dq
            itens.append((p, ger)); p += dq
        trilhas.append(("Música", True, itens))
    for n in (1, 0):   # A2, A1
        trilhas.append((f"Áudio {n + 1}", True, [(doc.f(c["na_linha"]), (lambda pl, c=c, i=i: entrada_clipe(pl, c, i, True, 0)))
                                                 for i, c in enumerate(clipes) if trilha[i] == n and c["audio"]]))
    for n in (0, 1):   # V1, V2
        trilhas.append((f"Vídeo {n + 1}", False, [(doc.f(c["na_linha"]), (lambda pl, c=c, i=i: entrada_clipe(pl, c, i, False, 0)))
                                                  for i, c in enumerate(clipes) if trilha[i] == n]))
    if titulos:
        def ger_t(pl, pid, q):
            e = ET.SubElement(pl, "entry", {"producer": pid, "in": doc.clock(0), "out": doc.clock(q - 1)}); return q
        trilhas.append(("Textos", False, [(doc.f(t["inicio"]), (lambda pl, pid=pid, q=q: ger_t(pl, pid, q))) for t, pid, q in titulos]))
    if not any(it for _, a, it in trilhas if not a and _ == "Vídeo 2"):
        trilhas = [t for t in trilhas if t[0] != "Vídeo 2"]
    if not any(c["audio"] and trilha[i] == 1 for i, c in enumerate(clipes)):
        trilhas = [t for t in trilhas if t[0] != "Áudio 2"]

    main = ET.Element("tractor", {"id": "maintractor", "global_feed": "1", "in": doc.clock(0), "out": doc.clock(doc.f(total) - 1)})
    _prop(main, "kdenlive:sequenceproperties.guides", json.dumps(guias, ensure_ascii=False))   # onde o Kdenlive 23.08+ lê as guias
    ET.SubElement(main, "track", {"producer": "black_track"})
    idx = {}
    for i, (nome, audio, itens) in enumerate(trilhas, start=1):
        sub = ET.Element("tractor", {"id": f"tractor{i}", "in": doc.clock(0), "out": doc.clock(doc.f(total) - 1)})
        _prop(sub, "kdenlive:track_name", nome); _prop(sub, "kdenlive:trackheight", 54)
        if audio: _prop(sub, "kdenlive:audio_track", "1")
        pl = ET.Element("playlist", {"id": f"playlist{2 * i}"}); pl2 = ET.Element("playlist", {"id": f"playlist{2 * i + 1}"})
        if audio: _prop(pl, "kdenlive:audio_track", "1"); _prop(pl2, "kdenlive:audio_track", "1")
        preencher_trilha(pl, itens)
        ET.SubElement(sub, "track", {"producer": pl.get("id"), "hide": "video" if audio else "audio"})
        ET.SubElement(sub, "track", {"producer": pl2.get("id"), "hide": "both"})
        doc.mlt.extend((pl, pl2, sub))
        ET.SubElement(main, "track", {"producer": sub.get("id")}); idx[nome] = i
    # composições internas (o Kdenlive soma os áudios e empilha os vídeos sobre a trilha 0)
    for nome, audio, _ in trilhas:
        tr = ET.SubElement(main, "transition")
        if audio:
            for k, v in {"a_track": 0, "b_track": idx[nome], "mlt_service": "mix", "kdenlive_id": "mix", "internal_added": 237,
                         "always_active": 1, "accepts_blanks": 1, "sum": 1}.items(): _prop(tr, k, v)
        else:
            for k, v in {"a_track": 0, "b_track": idx[nome], "mlt_service": "qtblend", "kdenlive_id": "qtblend", "internal_added": 237,
                         "always_active": 1, "compositing": 0}.items(): _prop(tr, k, v)
    # dissolver entre V1 e V2 durante cada sobreposição
    for i, c in enumerate(clipes[:-1]):
        if c["sobreposicao"] > 0 and "Vídeo 2" in idx:
            a = doc.f(clipes[i + 1]["na_linha"]); b = a + doc.f(c["sobreposicao"]) - 1
            tr = ET.SubElement(main, "transition", {"in": doc.clock(a), "out": doc.clock(b)})
            for k, v in {"a_track": idx["Vídeo 1"], "b_track": idx["Vídeo 2"], "mlt_service": "luma", "kdenlive_id": "dissolve",
                         "reverse": 1 if trilha[i] == 1 else 0}.items(): _prop(tr, k, v)
    saida = destino(pasta)
    dados = L.carregar(pasta)   # legendas: arquivo ASS ao lado + filtro de legendas na linha do tempo (como o Kdenlive grava)
    if d["legendas"]["ativo"] and dados and dados.get("segmentos"):
        dd = json.loads(json.dumps(d)); dd["legendas"]["estilo"] = "frases"   # uma frase por evento, editável no Kdenlive
        with open(saida + ".ass", "w", encoding="utf-8") as fh: fh.write(L.para_ass(dados, dd))
        fl = ET.SubElement(main, "filter")
        for k, v in {"mlt_service": "avfilter.subtitles", "internal_added": 237, "av.filename": saida + ".ass",
                     "av.alpha": 1, "kdenlive:locked": 0}.items():
            _prop(fl, k, v)
    doc.mlt.append(main)

    xml = minidom.parseString(ET.tostring(doc.mlt, encoding="unicode")).toprettyxml(indent=" ", encoding="utf-8")
    with open(saida, "wb") as fh: fh.write(xml)
    _registrar(pasta, saida)
    return saida


if __name__ == "__main__":
    try: print(exportar(os.path.abspath(sys.argv[1])))
    except P.ErroProjeto as e:
        print(f"erro: {e}", file=sys.stderr); sys.exit(1)
