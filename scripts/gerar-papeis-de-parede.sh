#!/usr/bin/env bash
# Redesenha os papéis de parede atuais de todos os temas (coluna "gerador" de modos/temas.conf).
# Uso: scripts/gerar-papeis-de-parede.sh [id...]   (sem argumentos = todos)
# Só gera os PNGs em themes/<pasta>/wallpaper/; para instalar: modos/instalar-temas.sh
set -euo pipefail
PROJ=$(cd "$(dirname "$0")/.." && pwd); PY="$PROJ/.venv/bin/python"
[ -x "$PY" ] || { echo "Ambiente ausente: rode scripts/preparar-ambiente.sh"; exit 1; }
while IFS='|' read -r ID _ _ _ _ _ _ _ _ GERADOR; do
  case "$ID" in ''|\#*) continue ;; esac
  if [ $# -gt 0 ] && [[ " $* " != *" $ID "* ]]; then continue; fi
  [ "$GERADOR" != "-" ] || { echo "== $ID: bitmap aprovado preservado (sem gerador)"; continue; }
  echo "== $ID"; "$PY" "$PROJ/$GERADOR" </dev/null
done < "$PROJ/modos/temas.conf"
