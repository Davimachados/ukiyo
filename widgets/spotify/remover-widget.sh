#!/usr/bin/env bash
# Remove apenas este widget. Não altera volume, aplicativo Spotify nem os outros widgets.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$D/../.." && pwd)
ID=org.ukiyo.spotify
B="$ROOT/backups/$(date +%F_%H%M%S)-remover-widget-spotify"
mkdir -p "$B"
cp -a "$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc" "$B/"
[ ! -d "$HOME/.local/share/plasma/plasmoids/$ID" ] || cp -a "$HOME/.local/share/plasma/plasmoids/$ID" "$B/"
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
panels().forEach(function(p) { p.widgets('$ID').forEach(function(w) { w.remove(); }); });"
kpackagetool6 --type Plasma/Applet --remove "$ID"
echo "Widget removido. Backup: $B"
