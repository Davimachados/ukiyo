#!/usr/bin/env bash
# Washi V5a — tela de BLOQUEIO: papel de parede Washi v2 (usuário comum, sem sudo).
# As cores do bloqueio já seguem o esquema Washi; o relógio usa a fonte do sistema (o QML do bloqueio
# pertence ao shell do Plasma e não é personalizado aqui, para não arriscar o desbloqueio).
# Desfazer: scripts/restaurar-v5-bloqueio.sh
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd)
PROJ=$(cd "$TEMA/../.." && pwd)
WP="$HOME/.local/share/wallpapers/Washi-v2"
[ -d "$WP" ] || { echo "Pacote $WP ausente (rode trocar-papel-de-parede.sh v2)."; exit 1; }
B="$PROJ/backups/$(date +%F_%H%M%S)-washi-v5-bloqueio"; mkdir -p "$B"
if [ -e "$HOME/.config/kscreenlockerrc" ]; then cp -a "$HOME/.config/kscreenlockerrc" "$B/"; else touch "$B/kscreenlockerrc.ausente"; fi
echo "Backup: $B"
kwriteconfig6 --file kscreenlockerrc --group Greeter --key WallpaperPlugin org.kde.image
kwriteconfig6 --file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General --key Image "$WP"
kwriteconfig6 --file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General --key PreviewImage "$WP"
echo "Bloqueio: papel de parede Washi v2. Teste: bloqueie com Meta+L. Desfazer: $TEMA/scripts/restaurar-v5-bloqueio.sh"
