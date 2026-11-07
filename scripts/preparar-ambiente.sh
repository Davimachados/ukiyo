#!/usr/bin/env bash
# Cria/atualiza o ambiente Python do projeto em .venv (Pillow + NumPy de requirements.txt).
# Requer o pacote Debian python3-venv (se faltar, o usuário instala: sudo apt install python3-venv).
# Idempotente: rodar de novo só confere/atualiza. Desfazer: rm -rf .venv
set -euo pipefail
PROJ=$(cd "$(dirname "$0")/.." && pwd)
if ! python3 -c 'import ensurepip' 2>/dev/null; then
  echo "Falta o python3-venv. Rode no seu terminal: sudo apt install python3-venv"; exit 1
fi
[ -x "$PROJ/.venv/bin/python" ] || python3 -m venv "$PROJ/.venv"
"$PROJ/.venv/bin/pip" install -q -r "$PROJ/requirements.txt"
"$PROJ/.venv/bin/python" -c 'import PIL, numpy; print("ok: Pillow", PIL.__version__, "| NumPy", numpy.__version__)'
