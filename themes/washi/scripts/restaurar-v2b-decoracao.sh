#!/usr/bin/env bash
# Volta à decoração anterior à V2b (Breeze recolorido) a partir do backup *-washi-v2b mais antigo (ou do indicado).
# Uso: restaurar-v2b-decoracao.sh [PASTA_BACKUP] [--limpar]   (--limpar remove o tema WashiPixel instalado)
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd)
PROJ=$(cd "$TEMA/../.." && pwd)
CFG="$HOME/.config"; AUR="$HOME/.local/share/aurorae/themes"
LIMPAR=0; B=""
for a in "$@"; do case "$a" in --limpar) LIMPAR=1 ;; *) B="$a" ;; esac; done
[ -n "$B" ] || B=$(ls -d "$PROJ"/backups/*-washi-v2b 2>/dev/null | sort | head -1)
[ -d "$B" ] && [ -f "$B/estado.env" ] || { echo "Backup não encontrado."; exit 1; }
echo "Restaurando de: $B"
# shellcheck disable=SC1091
source "$B/estado.env"
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library "${LIBRARY:-org.kde.breeze}"
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme "${THEME:-Breeze}"
qdbus6 org.kde.KWin /KWin reconfigure
for f in gtk-3.0 gtk-4.0; do
  if [ -e "$B/$f" ]; then rm -rf "${CFG:?}/$f"; cp -a "$B/$f" "$CFG/"; fi
done
qdbus6 org.kde.kded6 /kded org.kde.kded6.unloadModule gtkconfig >/dev/null
qdbus6 org.kde.kded6 /kded org.kde.kded6.loadModule gtkconfig >/dev/null
if [ "$LIMPAR" = 1 ]; then
  rm -rf "$AUR/WashiPixel"
  [ -e "$B/aurorae.ausente" ] && rm -rf "$HOME/.local/share/aurorae" || true
fi
echo "Decoração restaurada: ${LIBRARY:-org.kde.breeze} / ${THEME:-Breeze}"
