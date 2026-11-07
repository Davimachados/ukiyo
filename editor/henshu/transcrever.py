"""Transcrição local com faster-whisper (roda com .venv/bin/python do projeto).

Uso: .venv/bin/python -m henshu.transcrever <pasta-do-vídeo> [--modelo small] [--idioma pt] [--so-legendas]
- Transcreve cada arquivo usado no projeto que ainda não tem cache (com tempo de cada palavra).
- Depois monta legendas/legendas.json a partir do corte atual (a versão anterior vira legendas.json.anterior).
- Imprime linhas "PROGRESSO <0-100> <arquivo>" para a janela acompanhar.
"""
import argparse, json, os, sys, time
from . import projeto as P, legendas as L


def audio_16k(path):
    """Áudio mono 16 kHz em float32 via FFmpeg do sistema (evita a decodificação do PyAV)."""
    import numpy as np, subprocess
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", "16000",
                        "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)


def transcrever_arquivo(modelo, path, idioma, base_pct, peso):
    dur = P.duracao_arquivo(path)
    segs, info = modelo.transcribe(audio_16k(path), language=idioma, word_timestamps=True, vad_filter=True,
                                   vad_parameters={"min_silence_duration_ms": 400}, beam_size=5,
                                   condition_on_previous_text=False)
    palavras, frases = [], []
    for s in segs:
        frases.append({"i": round(s.start, 3), "f": round(s.end, 3), "texto": s.text.strip()})
        for w in s.words or []:
            if w.word.strip():
                palavras.append({"p": w.word.strip(), "i": round(w.start, 3), "f": round(w.end, 3), "conf": round(w.probability, 2)})
        print(f"PROGRESSO {int(base_pct + peso * min(1, s.end / max(dur, 0.1)))} {os.path.basename(path)}", flush=True)
    return {"arquivo": os.path.abspath(path), "idioma": info.language, "duracao": dur, "palavras": palavras, "frases": frases}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("pasta"); ap.add_argument("--modelo", default="small")
    ap.add_argument("--idioma", default="pt"); ap.add_argument("--so-legendas", action="store_true")
    a = ap.parse_args(); pasta = os.path.abspath(a.pasta)
    d = P.carregar(pasta); clipes, _ = P.clipes_resolvidos(pasta, d)
    falta = [] if a.so_legendas else L.faltando(pasta, clipes)
    if falta:
        print(f"PROGRESSO 0 carregando o modelo {a.modelo} (a primeira vez baixa ~460 MB)…", flush=True)
        from faster_whisper import WhisperModel
        opts = dict(device="cpu", compute_type="int8", cpu_threads=max(2, (os.cpu_count() or 4) - 2))
        try:   # usa o modelo já baixado sem tocar na rede (funciona dentro da sandbox do Codex)
            modelo = WhisperModel(a.modelo, local_files_only=True, **opts)
        except Exception:
            modelo = WhisperModel(a.modelo, **opts)
        t0 = time.time()
        for n, path in enumerate(falta):
            tr = transcrever_arquivo(modelo, path, a.idioma, 100 * n / len(falta), 100 / len(falta))
            with open(L.cache_de(pasta, path), "w", encoding="utf-8") as f: json.dump(tr, f, ensure_ascii=False)
        print(f"INFO transcrição em {time.time() - t0:.0f} s", flush=True)
    dados = L.gerar(pasta, d, clipes)
    L.salvar(pasta, dados)
    print(f"OK {len(dados['segmentos'])} frases em {L.ARQ}", flush=True)


if __name__ == "__main__":
    try: main()
    except P.ErroProjeto as e:
        print(f"ERRO {e}", flush=True); sys.exit(1)
