"""Renderização do projeto com FFmpeg: filtros na CPU (cortes, velocidade, enquadramento, transições, textos,
legendas, mistura) e codificação na GPU (VA-API).
- prévia: metade da resolução, rápida (usada a cada mudança)
- final:  resolução do preset, áudio normalizado em −14 LUFS (2 passadas), capítulos embutidos se houver
Uso direto: python3 -m henshu.render <pasta-do-video> [--final]
"""
import json, os, subprocess, sys
from . import projeto as P, legendas as L

GPU = os.environ.get("TIKTOK_GPU", "/dev/dri/renderD128")
FONTES = {"padrao": "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
          "pixel": "/usr/share/fonts/truetype/dotgothic16/DotGothic16-Regular.ttf"}
if not os.path.exists(FONTES["padrao"]):
    FONTES["padrao"] = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ALVO_LUFS, ALVO_TP, ALVO_LRA = -14, -1.0, 11


def _n(x):
    return f"{x:.3f}"


def _esc(s):   # caminho dentro de um filtro do FFmpeg
    return s.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def _atempo(v):
    """atempo aceita 0.5–2 por instância; encadeia para 0.25–4."""
    out = []
    while v > 2.0: out.append("atempo=2.0"); v /= 2.0
    while v < 0.5: out.append("atempo=0.5"); v /= 0.5
    if abs(v - 1.0) > 1e-3: out.append(f"atempo={v:.4f}")
    return out


def grafo(pasta, d, escala=1.0, com_video=True):
    """Monta (entradas, filter_complex, rótulo_vídeo, rótulo_áudio, duração)."""
    clipes, total = P.clipes_resolvidos(pasta, d)
    if not clipes:
        raise P.ErroProjeto("o projeto ainda não tem clipes")
    W = int(d["formato"]["largura"] * escala) // 2 * 2; H = int(d["formato"]["altura"] * escala) // 2 * 2
    fps = d["formato"]["fps"]
    entradas, fc = [], []
    for c in clipes:   # uma entrada por clipe (cada rótulo de entrada só pode ser usado uma vez)
        entradas += ["-i", c["caminho"]]
    for i, c in enumerate(clipes):
        anterior = clipes[i - 1]["transicao"] if i > 0 else None
        fade_in = anterior["duracao"] if anterior and anterior["tipo"] == "fade" else 0
        fade_out = c["transicao"]["duracao"] if c["transicao"]["tipo"] == "fade" and i < len(clipes) - 1 else 0
        fade_in, fade_out = min(fade_in, c["duracao"] / 2), min(fade_out, c["duracao"] / 2)
        v = c["velocidade"]
        if com_video:
            if c["enquadrar"] == "preencher":
                enq = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                       f"crop={W}:{H}:x='(iw-{W})*{c['foco_x']:.3f}':y='(ih-{H})*{c['foco_y']:.3f}'")
            else:
                enq = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black"
            cad = [f"trim=start={_n(c['inicio'])}:end={_n(c['fim_real'])}", f"setpts=(PTS-STARTPTS)/{v:.4f}", f"fps={fps}",
                   enq, "setsar=1", "format=yuv420p", "settb=AVTB"]
            if fade_in: cad.append(f"fade=t=in:st=0:d={_n(fade_in)}")
            if fade_out: cad.append(f"fade=t=out:st={_n(c['duracao'] - fade_out)}:d={_n(fade_out)}")
            fc.append(f"[{i}:v]" + ",".join(cad) + f"[v{i}]")
        if c["audio"]:
            cad = [f"atrim=start={_n(c['inicio'])}:end={_n(c['fim_real'])}", "asetpts=PTS-STARTPTS", *_atempo(v),
                   "aresample=48000", "aformat=sample_fmts=fltp:channel_layouts=stereo", f"volume={c['volume']}"]
        else:
            cad = [f"anullsrc=r=48000:cl=stereo", f"atrim=duration={_n(c['duracao'])}", "aformat=sample_fmts=fltp:channel_layouts=stereo"]
        if fade_in: cad.append(f"afade=t=in:st=0:d={_n(fade_in)}")
        if fade_out: cad.append(f"afade=t=out:st={_n(c['duracao'] - fade_out)}:d={_n(fade_out)}")
        fc.append((f"[{i}:a]" if c["audio"] else "") + ",".join(cad) + f"[a{i}]")
    # junta os clipes em sequência: concat (corte/fade) ou xfade+acrossfade (dissolver)
    av, aa, dur = "[v0]", "[a0]", clipes[0]["duracao"]
    for i in range(1, len(clipes)):
        sob = clipes[i - 1]["sobreposicao"]
        nv, na = f"[vj{i}]", f"[aj{i}]"
        if sob > 0:
            if com_video: fc.append(f"{av}[v{i}]xfade=transition=fade:duration={_n(sob)}:offset={_n(dur - sob)}{nv}")
            fc.append(f"{aa}[a{i}]acrossfade=d={_n(sob)}{na}")
            dur += clipes[i]["duracao"] - sob
        else:
            if com_video: fc.append(f"{av}{aa}[v{i}][a{i}]concat=n=2:v=1:a=1{nv}{na}")
            else: fc.append(f"{aa}[a{i}]concat=n=2:v=0:a=1{na}")
            dur += clipes[i]["duracao"]
        av, aa = (nv if com_video else av), na
    rot_v, rot_a = av, aa
    if com_video:
        cadeia = []
        if d["textos"]:   # textos (arquivo de texto evita problemas de escape)
            tdir = os.path.join(pasta, ".henshu", "textos"); os.makedirs(tdir, exist_ok=True)
            for j, t in enumerate(d["textos"]):
                tf = os.path.join(tdir, f"{j}.txt")
                with open(tf, "w", encoding="utf-8") as f: f.write(t["texto"])
                tam = max(8, int(t["tamanho"] * H / d["formato"]["altura"]))   # tamanho em pixels do vídeo final
                y = {"topo": f"{int(H * 0.12)}", "centro": "(h-text_h)/2", "base": f"h-text_h-{int(H * 0.2)}"}[t["posicao"]]
                cadeia.append(f"drawtext=fontfile='{_esc(FONTES[t['fonte']])}':textfile='{_esc(tf)}':fontsize={tam}:"
                              f"fontcolor={t['cor']}:borderw={max(2, tam // 14)}:bordercolor=black@0.85:line_spacing={tam // 6}:"
                              f"x=(w-text_w)/2:y={y}:enable='between(t,{_n(t['inicio'])},{_n(t['fim'])})'")
        if d["legendas"]["ativo"]:
            dados = L.carregar(pasta)
            if dados and dados.get("segmentos"):
                ass = os.path.join(pasta, ".henshu", "legendas.ass")
                with open(ass, "w", encoding="utf-8") as f: f.write(L.para_ass(dados, d))
                cadeia.append(f"subtitles=filename='{_esc(ass)}':fontsdir='/usr/share/fonts/truetype'")
        if cadeia:
            fc.append(f"{rot_v}{','.join(cadeia)}[vt]"); rot_v = "[vt]"
    m = d.get("musica")
    if m:   # música de fundo
        mp = os.path.normpath(os.path.join(pasta, m["arquivo"]))
        if not os.path.exists(mp): raise P.ErroProjeto(f"música não encontrada: {m['arquivo']}")
        k = len(clipes); entradas += ["-stream_loop", "-1", "-i", mp]
        fc.append(f"[{k}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={m['volume']},"
                  f"atrim=duration={_n(total)},afade=t=out:st={_n(max(0, total - 1.5))}:d=1.5[mus]")
        fc.append(f"{rot_a}[mus]amix=inputs=2:duration=first:normalize=0[am]"); rot_a = "[am]"
    return entradas, ";".join(fc), rot_v, rot_a, total


def comando_previa(pasta, d, saida):
    ent, fc, v, a, total = grafo(pasta, d, escala=0.5)
    return ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-vaapi_device", GPU, *ent,
            "-filter_complex", fc + f";{v}format=nv12,hwupload[vo]", "-map", "[vo]", "-map", a,
            "-c:v", "h264_vaapi", "-qp", "28", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            "-progress", "pipe:1", "-nostats", saida], total


def medir_volume(pasta, d):
    ent, fc, _, a, _ = grafo(pasta, d, com_video=False)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *ent, "-filter_complex", fc + f";{a}loudnorm=I={ALVO_LUFS}:TP={ALVO_TP}:"
                        f"LRA={ALVO_LRA}:print_format=json[med]", "-map", "[med]", "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1]
    try: return json.loads(txt)
    except ValueError: raise P.ErroProjeto("não consegui medir o volume do áudio: " + r.stderr.strip()[-200:])


def comando_final(pasta, d, saida, medida):
    ent, fc, v, a, total = grafo(pasta, d, escala=1.0)
    ln = (f"loudnorm=I={ALVO_LUFS}:TP={ALVO_TP}:LRA={ALVO_LRA}:measured_I={medida['input_i']}:measured_TP={medida['input_tp']}:"
          f"measured_LRA={medida['input_lra']}:measured_thresh={medida['input_thresh']}:offset={medida['target_offset']}:linear=true,aresample=48000")
    extra = []
    if d["capitulos"]:
        meta = os.path.join(pasta, ".henshu", "capitulos.ffmeta")
        with open(meta, "w", encoding="utf-8") as f: f.write(L.ffmetadata(d["capitulos"], total))
        n = sum(1 for x in ent if x == "-i"); ent = ent + ["-f", "ffmetadata", "-i", meta]; extra = ["-map_chapters", str(n)]
    taxa = ("12M", "16M") if d["formato"]["preset"] == "vertical" else ("10M", "14M")
    return ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-vaapi_device", GPU, *ent,
            "-filter_complex", fc + f";{v}format=nv12,hwupload[vo];{a}{ln}[ao]", "-map", "[vo]", "-map", "[ao]", *extra,
            "-c:v", "h264_vaapi", "-profile:v", "high", "-rc_mode", "VBR", "-b:v", taxa[0], "-maxrate", taxa[1], "-g", "60",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
            "-progress", "pipe:1", "-nostats", saida], total


def caminho_previa(pasta):
    os.makedirs(os.path.join(pasta, ".henshu"), exist_ok=True)
    return os.path.join(pasta, ".henshu", "previa.mp4")


def nome_final(pasta, d):
    os.makedirs(os.path.join(pasta, "export"), exist_ok=True)
    return os.path.join(pasta, "export", f"{os.path.basename(pasta)}_{d['formato']['preset']}.mp4")


def exportar_textos(pasta, d):
    """SRT (para subir na plataforma) e capítulos do YouTube; devolve a lista de arquivos gerados."""
    _, total = P.clipes_resolvidos(pasta, d); base = os.path.join(pasta, "export", os.path.basename(pasta))
    os.makedirs(os.path.dirname(base), exist_ok=True); feitos = []
    dados = L.carregar(pasta)
    if dados and dados.get("segmentos"):
        with open(base + ".srt", "w", encoding="utf-8") as f: f.write(L.para_srt(dados))
        feitos.append(base + ".srt")
    if d["capitulos"]:
        with open(base + "_capitulos.txt", "w", encoding="utf-8") as f: f.write(L.capitulos_youtube(d["capitulos"], total))
        feitos.append(base + "_capitulos.txt")
    return feitos


if __name__ == "__main__":
    pasta = os.path.abspath(sys.argv[1]); final = "--final" in sys.argv
    try:
        d = P.carregar(pasta)
        if final:
            saida = nome_final(pasta, d); cmd, total = comando_final(pasta, d, saida, medir_volume(pasta, d))
        else:
            saida = caminho_previa(pasta); cmd, total = comando_previa(pasta, d, saida)
    except P.ErroProjeto as e:
        print(f"erro: {e}", file=sys.stderr); sys.exit(1)
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL)
    if r.returncode == 0 and final:
        for f in exportar_textos(pasta, d): print(f)
    print(saida if r.returncode == 0 else "falhou"); sys.exit(r.returncode)
