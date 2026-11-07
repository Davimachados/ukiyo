#!/usr/bin/env bash
# Transcreve as falas do vídeo (local, faster-whisper) e gera legendas/legendas.json.
# Uso: henshu-transcrever [pasta-do-vídeo] [--so-legendas]   (sem pasta = pasta atual)
DIR=$(dirname "$(readlink -f "$0")"); PROJ=$(dirname "$DIR")
ALVO=$PWD; [ $# -gt 0 ] && [ "${1#--}" = "$1" ] && { ALVO=$(readlink -f "$1"); shift; }
cd "$DIR" && exec "$PROJ/.venv/bin/python" -m henshu.transcrever "$ALVO" "$@"
