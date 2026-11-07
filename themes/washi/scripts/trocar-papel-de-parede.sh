#!/usr/bin/env bash
# Alterna o papel de parede Washi entre v1 e v2 sem sobrescrever nada:
# cada versão é um pacote próprio em ~/.local/share/wallpapers (Washi = v1, Washi-v2 = v2).
# Uso: trocar-papel-de-parede.sh v2   |   trocar-papel-de-parede.sh v1   (desfaz)
# Não toca nos painéis, no OBS, no áudio, no login nem no bloqueio.
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd)
PROJ=$(cd "$TEMA/../.." && pwd)
WP="$HOME/.local/share/wallpapers"
VER=${1:-}
case "$VER" in v1) PKG=Washi ;; v2) PKG=Washi-v2 ;; *) echo "Uso: $0 v1|v2"; exit 1 ;; esac

# backup do arquivo de configuração onde o Plasma guarda o papel de parede
B="$PROJ/backups/$(date +%F_%H%M%S)-papel-de-parede"
mkdir -p "$B"; cp -a "$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc" "$B/"
echo "Backup: $B"

if [ "$VER" = v2 ]; then
  mkdir -p "$WP/Washi-v2/contents/images"
  cp "$TEMA/wallpaper/entardecer-v2-1920x1080.png" "$WP/Washi-v2/contents/images/1920x1080.png"
  cat > "$WP/Washi-v2/metadata.json" <<'EOF'
{"KPlugin": {"Id": "Washi-v2", "Name": "Washi — Entardecer (v2)", "Authors": [{"Name": "Davi"}], "License": "CC-BY-SA-4.0"}}
EOF
fi
[ -d "$WP/$PKG" ] || { echo "Pacote $PKG ausente em $WP"; exit 1; }
plasma-apply-wallpaperimage "$WP/$PKG"
echo "Papel de parede: $PKG. Para voltar: $0 $([ "$VER" = v2 ] && echo v1 || echo v2)"
