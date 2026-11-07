#!/usr/bin/env bash
# Henshū 編集 — editor de vídeo com chat (Claude/Codex). Uso: henshu [pasta-do-vídeo]
DIR=$(dirname "$(readlink -f "$0")")
PYTHONPATH="$DIR${PYTHONPATH:+:$PYTHONPATH}" exec python3 -m henshu.app "$@"
