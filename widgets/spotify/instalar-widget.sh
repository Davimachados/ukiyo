#!/usr/bin/env bash
# Ativa o widget apenas depois de o usuário aprovar a prévia. Sem sudo e sem reiniciar o painel.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$D/../.." && pwd)
ID=org.ukiyo.spotify
B="$ROOT/backups/$(date +%F_%H%M%S)-ativar-widget-spotify"
mkdir -p "$B"
for name in plasma-org.kde.plasma.desktop-appletsrc plasmashellrc; do
  [ ! -f "$HOME/.config/$name" ] || cp -a "$HOME/.config/$name" "$B/"
done
if [ -d "$HOME/.local/share/plasma/plasmoids/$ID" ]; then
  cp -a "$HOME/.local/share/plasma/plasmoids/$ID" "$B/"
  kpackagetool6 --type Plasma/Applet --upgrade "$D"
else
  kpackagetool6 --type Plasma/Applet --install "$D"
fi
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var p = panels().filter(function(p) { return p.location === 'top'; })[0];
if (!p) { throw new Error('Barra superior não encontrada.'); }
var existing = p.widgets('$ID');
if (existing.length === 0) { var w = p.addWidget('$ID'); print(w.id); }
else { print(existing[0].id); }
"
echo "Widget ativado. Backup: $B"
