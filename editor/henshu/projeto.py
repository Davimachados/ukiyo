"""Projeto do Henshū 編集: um arquivo `projeto.json` na pasta do vídeo, simples o bastante para os agentes editarem.

Formato (versão 2; projetos da versão 1 continuam válidos):
{
  "versao": 2,
  "formato": {"preset": "vertical", "largura": 1080, "altura": 1920, "fps": 30},
  "clipes": [                                   # em sequência, um após o outro
    {"arquivo": "brutos/fala.mp4", "inicio": 2.0, "fim": 7.5, "volume": 1.0,
     "velocidade": 1.0,                          # 0.25 a 4 (o áudio acompanha, sem mudar o tom)
     "enquadrar": "ajustar",                     # ajustar (faixas pretas) | preencher (corta para ocupar a tela)
     "foco_x": 0.5, "foco_y": 0.5,               # ao preencher: ponto da imagem que fica no centro (0 a 1)
     "transicao": {"tipo": "corte", "duracao": 0.5}}   # para o PRÓXIMO clipe: corte | fade | dissolver
  ],
  "textos": [ {"texto": "…", "inicio": 0.0, "fim": 2.5, "posicao": "topo", "tamanho": 84, "cor": "#ffffff", "fonte": "padrao"} ],
  "legendas": {"ativo": false, "estilo": "frases", "posicao": "base", "tamanho": 0},  # frases | karaoke | pixel
  "capitulos": [ {"inicio": 0.0, "titulo": "Introdução"} ],
  "musica": {"arquivo": "audio/fundo.mp3", "volume": 0.15},   # ou null
  "observacoes": ""
}
- As falas das legendas ficam em `legendas/legendas.json` (gerado pela transcrição e revisável).
- Tempos de textos, legendas e capítulos são da linha do tempo final.
"""
import json, os, subprocess

NOME = "projeto.json"
PRESETS = {
    "vertical":   {"nome": "Vertical 9:16", "largura": 1080, "altura": 1920, "fps": 30},
    "horizontal": {"nome": "Horizontal 16:9", "largura": 1920, "altura": 1080, "fps": 30},
}
ESTILOS_LEGENDA = {"frases": "Frases curtas", "karaoke": "Palavra destacada (karaokê)", "pixel": "Pixel (identidade)"}
TRANSICOES = ("corte", "fade", "dissolver")
VAZIO = {"versao": 2, "formato": {"preset": "vertical", "largura": 1080, "altura": 1920, "fps": 30},
         "clipes": [], "textos": [], "legendas": {"ativo": False, "estilo": "frases", "posicao": "base", "tamanho": 0},
         "capitulos": [], "musica": None, "observacoes": ""}


class ErroProjeto(Exception):
    pass


def caminho(pasta):
    return os.path.join(pasta, NOME)


def novo(preset="vertical"):
    d = json.loads(json.dumps(VAZIO)); aplicar_preset(d, preset); return d


def aplicar_preset(d, preset):
    p = PRESETS[preset]
    d["formato"] = {"preset": preset, "largura": p["largura"], "altura": p["altura"], "fps": p["fps"]}
    return d


def carregar(pasta):
    p = caminho(pasta)
    if not os.path.exists(p):
        return novo()
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except json.JSONDecodeError as e:
        raise ErroProjeto(f"projeto.json inválido (linha {e.lineno}): {e.msg}")
    return normalizar(d)


def ler_cru(pasta):
    with open(caminho(pasta), encoding="utf-8") as f:
        return json.load(f)


def salvar(pasta, d):
    tmp = caminho(pasta) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2); f.write("\n")
    os.replace(tmp, caminho(pasta))


_dur_cache = {}
def sondar(path):
    """(duração, largura, altura, tem_áudio) do arquivo, com cache."""
    try:
        k = (path, os.path.getmtime(path))
    except OSError:
        raise ErroProjeto(f"arquivo não encontrado: {os.path.basename(path)}")
    if k not in _dur_cache:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
                            "-of", "json", path], capture_output=True, text=True)
        try:
            j = json.loads(r.stdout); dur = float(j["format"]["duration"])
        except (ValueError, KeyError):
            raise ErroProjeto(f"não consegui ler {os.path.basename(path)}")
        v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
        a = any(s.get("codec_type") == "audio" for s in j.get("streams", []))
        _dur_cache[k] = (dur, v.get("width", 0), v.get("height", 0), a)
    return _dur_cache[k]


def duracao_arquivo(path):
    return sondar(path)[0]


def tem_audio(path):
    return sondar(path)[3]


def _num(v, nome, minimo=None, maximo=None):
    try: v = float(v)
    except (TypeError, ValueError): raise ErroProjeto(f"{nome} precisa ser um número")
    if (minimo is not None and v < minimo) or (maximo is not None and v > maximo):
        raise ErroProjeto(f"{nome} fora do intervalo ({minimo} a {maximo})")
    return v


def normalizar(d):
    """Completa campos ausentes e confere tipos; erros viram mensagens claras (que aparecem no chat)."""
    out = json.loads(json.dumps(VAZIO))
    fo = d.get("formato") or {}
    preset = fo.get("preset") if fo.get("preset") in PRESETS else None
    if preset is None:   # versão 1 ou formato manual: deduz pela orientação
        preset = "horizontal" if fo.get("largura", 1080) > fo.get("altura", 1920) else "vertical"
    out["formato"] = {"preset": preset, "largura": int(fo.get("largura") or PRESETS[preset]["largura"]),
                      "altura": int(fo.get("altura") or PRESETS[preset]["altura"]), "fps": fo.get("fps") or 30}
    for k in ("largura", "altura", "fps"):
        if not isinstance(out["formato"][k], (int, float)) or out["formato"][k] <= 0: raise ErroProjeto(f"formato.{k} inválido")
    clipes = []
    for i, c in enumerate(d.get("clipes") or []):
        if not isinstance(c, dict) or not c.get("arquivo"): raise ErroProjeto(f"clipes[{i}] precisa de \"arquivo\"")
        ini = _num(c.get("inicio") or 0, f"clipes[{i}].inicio", 0); fim = c.get("fim")
        fim = None if fim is None else _num(fim, f"clipes[{i}].fim", 0)
        if fim is not None and fim <= ini: raise ErroProjeto(f"clipes[{i}]: fim precisa ser maior que inicio")
        tr = c.get("transicao") or {}
        if isinstance(tr, str): tr = {"tipo": tr}
        tipo = tr.get("tipo", "corte")
        if tipo not in TRANSICOES: raise ErroProjeto(f"clipes[{i}].transicao.tipo: use {', '.join(TRANSICOES)}")
        enq = c.get("enquadrar", "ajustar")
        if enq not in ("ajustar", "preencher"): raise ErroProjeto(f"clipes[{i}].enquadrar: use ajustar ou preencher")
        clipes.append({"arquivo": c["arquivo"], "inicio": ini, "fim": fim,
                       "volume": _num(c.get("volume", 1.0), f"clipes[{i}].volume", 0, 4),
                       "velocidade": _num(c.get("velocidade", 1.0), f"clipes[{i}].velocidade", 0.25, 4),
                       "enquadrar": enq,
                       "foco_x": _num(c.get("foco_x", 0.5), f"clipes[{i}].foco_x", 0, 1),
                       "foco_y": _num(c.get("foco_y", 0.5), f"clipes[{i}].foco_y", 0, 1),
                       "transicao": {"tipo": tipo, "duracao": _num(tr.get("duracao", 0.5), f"clipes[{i}].transicao.duracao", 0.1, 3)}})
    out["clipes"] = clipes
    textos = []
    for i, t in enumerate(d.get("textos") or []):
        if not isinstance(t, dict) or not str(t.get("texto", "")).strip(): raise ErroProjeto(f"textos[{i}] precisa de \"texto\"")
        ini, fim = _num(t.get("inicio", 0), f"textos[{i}].inicio", 0), _num(t.get("fim", 0), f"textos[{i}].fim", 0)
        if fim <= ini: raise ErroProjeto(f"textos[{i}]: fim precisa ser maior que inicio")
        pos = t.get("posicao", "base")
        if pos not in ("topo", "centro", "base"): raise ErroProjeto(f"textos[{i}].posicao: use topo, centro ou base")
        textos.append({"texto": str(t["texto"]), "inicio": ini, "fim": fim, "posicao": pos,
                       "tamanho": int(t.get("tamanho", 72)), "cor": str(t.get("cor", "#ffffff")),
                       "fonte": t.get("fonte", "padrao") if t.get("fonte") in ("padrao", "pixel") else "padrao"})
    out["textos"] = textos
    lg = {**VAZIO["legendas"], **(d.get("legendas") or {})}
    if lg["estilo"] not in ESTILOS_LEGENDA: raise ErroProjeto(f"legendas.estilo: use {', '.join(ESTILOS_LEGENDA)}")
    if lg["posicao"] not in ("topo", "centro", "base"): raise ErroProjeto("legendas.posicao: use topo, centro ou base")
    out["legendas"] = {"ativo": bool(lg["ativo"]), "estilo": lg["estilo"], "posicao": lg["posicao"], "tamanho": int(lg.get("tamanho") or 0)}
    caps = []
    for i, c in enumerate(d.get("capitulos") or []):
        if not isinstance(c, dict) or not str(c.get("titulo", "")).strip(): raise ErroProjeto(f"capitulos[{i}] precisa de \"titulo\"")
        caps.append({"inicio": _num(c.get("inicio", 0), f"capitulos[{i}].inicio", 0), "titulo": str(c["titulo"]).strip()})
    out["capitulos"] = sorted(caps, key=lambda c: c["inicio"])
    m = d.get("musica")
    out["musica"] = None if not m else {"arquivo": m["arquivo"], "volume": _num(m.get("volume", 0.15), "musica.volume", 0, 2)}
    out["observacoes"] = str(d.get("observacoes") or "")
    return out


def clipes_resolvidos(pasta, d):
    """Clipes com caminho absoluto, duração real (já com a velocidade) e posição na linha do tempo.
    Uma transição "dissolver" sobrepõe o fim de um clipe ao começo do próximo (a linha do tempo encurta)."""
    t = 0.0; res = []
    for i, c in enumerate(d["clipes"]):
        p = os.path.normpath(os.path.join(pasta, c["arquivo"]))
        dur_arq, w, h, aud = sondar(p)
        fim = min(c["fim"], dur_arq) if c["fim"] is not None else dur_arq
        if fim <= c["inicio"]: raise ErroProjeto(f"{c['arquivo']}: o trecho começa depois do fim do arquivo ({dur_arq:.1f} s)")
        dur = (fim - c["inicio"]) / c["velocidade"]
        if i > 0 and res[-1]["transicao"]["tipo"] == "dissolver":
            sob = min(res[-1]["transicao"]["duracao"], res[-1]["duracao"] / 2, dur / 2)
            res[-1]["sobreposicao"] = sob; t -= sob
        res.append({**c, "caminho": p, "fim_real": fim, "duracao": dur, "na_linha": t, "audio": aud,
                    "largura_orig": w, "altura_orig": h, "sobreposicao": 0.0})
        t += dur
    return res, t


def linha_para_fonte(clipes, t):
    """Converte um instante da linha do tempo em (clipe, instante no arquivo). Útil para depuração e agentes."""
    for c in clipes:
        if c["na_linha"] <= t < c["na_linha"] + c["duracao"]:
            return c, c["inicio"] + (t - c["na_linha"]) * c["velocidade"]
    return None, None
