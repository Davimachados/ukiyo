#!/usr/bin/env bash
# Restaura o estado anterior à Washi V1 a partir de um backup criado por aplicar-v1-desktop.sh.
# Uso: restaurar-v1-desktop.sh [PASTA_BACKUP] [--limpar]
#   sem PASTA_BACKUP: usa o backup *-washi-v1 mais ANTIGO (= estado anterior à primeira aplicação)
#   --limpar: também remove os arquivos instalados (esquemas, papel de parede, ícones)
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd)
PROJ=$(cd "$TEMA/../.." && pwd)
CFG="$HOME/.config"; SHARE="$HOME/.local/share"
LIMPAR=0; B=""
for a in "$@"; do case "$a" in --limpar) LIMPAR=1 ;; *) B="$a" ;; esac; done
[ -n "$B" ] || B=$(ls -d "$PROJ"/backups/*-washi-v1 2>/dev/null | sort | head -1)
[ -d "$B" ] && [ -f "$B/estado.env" ] || { echo "Backup não encontrado."; exit 1; }
echo "Restaurando de: $B"
# shellcheck disable=SC1091
source "$B/estado.env"

# cores e estilo Plasma
plasma-apply-colorscheme "${COLORSCHEME:-BreezeLight}"
plasma-apply-desktoptheme "${DESKTOPTHEME:-default}"
[ -e "$B/plasmarc.ausente" ] && rm -f "$CFG/plasmarc"

# efeitos
rk() { if [ -n "$4" ]; then kwriteconfig6 --file "$1" --group "$2" --key "$3" "$4"; else kwriteconfig6 --file "$1" --group "$2" --key "$3" --delete; fi; }
rk kwinrc Plugins blurEnabled "$BLUR"
rk kwinrc Plugins contrastEnabled "$CONTRAST"
rk kdeglobals KDE AnimationDurationFactor "$ANIM"

# painéis + papel de parede (precisam do plasmashell parado)
kquitapp6 plasmashell >/dev/null 2>&1 || true
for i in $(seq 1 20); do pgrep -x plasmashell >/dev/null || break; sleep 0.5; done
for f in plasmashellrc plasma-org.kde.plasma.desktop-appletsrc; do
  if [ -e "$B/$f" ]; then cp -a "$B/$f" "$CFG/$f"; elif [ -e "$B/$f.ausente" ]; then rm -f "$CFG/$f"; fi
done
(setsid plasmashell >/dev/null 2>&1 &)

# áreas de trabalho: remove as que não existiam e restaura nomes
mapfile -t ANTES < <(grep -oE '\(uss\) [0-9]+, "[^"]+", "[^"]*"' "$B/desktops.txt" | sed -E 's/.*"([^"]+)", "([^"]*)"/\1|\2/')
ATUAL=$(qdbus6 --literal org.kde.KWin /VirtualDesktopManager org.freedesktop.DBus.Properties.Get org.kde.KWin.VirtualDesktopManager desktops)
for id in $(grep -oE '[0-9a-f]{8}-[0-9a-f-]{27}' <<<"$ATUAL"); do
  printf '%s\n' "${ANTES[@]}" | grep -q "^$id|" || qdbus6 org.kde.KWin /VirtualDesktopManager org.kde.KWin.VirtualDesktopManager.removeDesktop "$id"
done
for par in "${ANTES[@]}"; do
  qdbus6 org.kde.KWin /VirtualDesktopManager org.kde.KWin.VirtualDesktopManager.setDesktopName "${par%%|*}" "${par#*|}"
done
qdbus6 org.kde.KWin /KWin reconfigure

if [ "$LIMPAR" = 1 ]; then
  rm -f "$SHARE/color-schemes/Washi.colors" "$SHARE/color-schemes/Sumi.colors" \
        "$SHARE/icons/hicolor/scalable/apps/washi-lancador.svg" "$SHARE/icons/hicolor/scalable/apps/washi-sakura.svg"
  rm -rf "$SHARE/wallpapers/Washi"
fi
echo "Restaurado."
