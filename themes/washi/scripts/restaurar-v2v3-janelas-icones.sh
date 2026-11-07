#!/usr/bin/env bash
# Desfaz a Washi V2+V3 a partir do backup *-washi-v2v3 mais antigo (ou do indicado).
# Uso: restaurar-v2v3-janelas-icones.sh [PASTA_BACKUP] [--limpar]
#   --limpar: também remove ~/.local/share/icons/washi-pixel e ~/.icons/washi-cursor
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd)
PROJ=$(cd "$TEMA/../.." && pwd)
CFG="$HOME/.config"; ICONS="$HOME/.local/share/icons"
LIMPAR=0; B=""
for a in "$@"; do case "$a" in --limpar) LIMPAR=1 ;; *) B="$a" ;; esac; done
[ -n "$B" ] || B=$(ls -d "$PROJ"/backups/*-washi-v2v3 2>/dev/null | sort | head -1)
[ -d "$B" ] && [ -f "$B/estado.env" ] || { echo "Backup não encontrado."; exit 1; }
echo "Restaurando de: $B"
# shellcheck disable=SC1091
source "$B/estado.env"
rk() { if [ -n "$4" ]; then kwriteconfig6 --file "$1" --group "$2" --key "$3" "$4"; else kwriteconfig6 --file "$1" --group "$2" --key "$3" --delete; fi; }

/usr/lib/x86_64-linux-gnu/libexec/plasma-changeicons "${ICONES:-breeze}"
if [ -n "${CURSOR_TAM:-}" ]; then plasma-apply-cursortheme --size "$CURSOR_TAM" "${CURSOR:-breeze_cursors}"
else plasma-apply-cursortheme --size 24 "${CURSOR:-breeze_cursors}"; kwriteconfig6 --file kcminputrc --group Mouse --key cursorSize --delete; fi
[ -e "$B/kcminputrc.ausente" ] && rm -f "$CFG/kcminputrc"

rk kdeglobals WM activeFont "${FONTE_TITULO:-}"
dbus-send --session --type=signal /KDEPlatformTheme org.kde.KDEPlatformTheme.refreshFonts   # KWin/apps releem as fontes
if [ -e "$B/breezerc.ausente" ]; then rm -f "$CFG/breezerc"
else rk breezerc Common ShadowSize "${SOMBRA:-}"; rk breezerc Common OutlineIntensity "${CONTORNO:-}"; fi
# arquivos GTK regenerados pelo Plasma: volta às cópias do backup
for f in gtk-3.0 gtk-4.0 gtkrc gtkrc-2.0 xsettingsd; do
  if [ -e "$B/$f" ]; then rm -rf "${CFG:?}/$f"; cp -a "$B/$f" "$CFG/"; fi
done
qdbus6 org.kde.KWin /KWin reconfigure
# reaplica tudo no GTK (o gtkconfig só propaga o tamanho do cursor ao ser recarregado)
qdbus6 org.kde.kded6 /kded org.kde.kded6.unloadModule gtkconfig >/dev/null
qdbus6 org.kde.kded6 /kded org.kde.kded6.loadModule gtkconfig >/dev/null

if [ "$LIMPAR" = 1 ]; then
  rm -rf "$ICONS/washi-pixel" "$ICONS/washi-cursor" "$HOME/.icons/washi-cursor"
  [ -e "$B/dot-icons.ausente" ] && rmdir "$HOME/.icons" 2>/dev/null || true
fi
echo "Restaurado. (O cursor pode exigir reabrir os apps já abertos.)"
