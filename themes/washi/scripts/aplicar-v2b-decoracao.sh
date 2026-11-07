#!/usr/bin/env bash
# Washi V2b — decoração de janelas "Washi Pixel" (Aurorae, sem sombra, sem animação).
# Não toca nos painéis, OBS, áudio, login ou bloqueio. Idempotente.
# Desfazer: scripts/restaurar-v2b-decoracao.sh
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd)
PROJ=$(cd "$TEMA/../.." && pwd)
CFG="$HOME/.config"; AUR="$HOME/.local/share/aurorae/themes"
B="$PROJ/backups/$(date +%F_%H%M%S)-washi-v2b"

mkdir -p "$B"
for f in kwinrc gtk-3.0 gtk-4.0; do
  if [ -e "$CFG/$f" ]; then cp -a "$CFG/$f" "$B/"; else touch "$B/$f.ausente"; fi
done
[ -e "$HOME/.local/share/aurorae" ] || touch "$B/aurorae.ausente"
{
  echo "LIBRARY=$(kreadconfig6 --file kwinrc --group org.kde.kdecoration2 --key library --default org.kde.breeze)"
  echo "THEME=$(kreadconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme --default Breeze)"
} > "$B/estado.env"
(cd "$B" && find . -type f -exec sha256sum {} + > SHA256SUMS)
echo "Backup: $B"

python3 -I "$TEMA/tools/gerar-decoracao.py" "$TEMA/aurorae" >/dev/null
mkdir -p "$AUR"; rm -rf "$AUR/WashiPixel"; cp -a "$TEMA/aurorae/WashiPixel" "$AUR/"

# o KWin mantém o tema Aurorae em cache: passar pelo Breeze força a releitura do tema atualizado
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.breeze
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme Breeze
qdbus6 org.kde.KWin /KWin reconfigure
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__WashiPixel
qdbus6 org.kde.KWin /KWin reconfigure
# o Plasma redesenha os botões das janelas GTK a partir da decoração ativa
qdbus6 org.kde.kded6 /kded org.kde.kded6.unloadModule gtkconfig >/dev/null
qdbus6 org.kde.kded6 /kded org.kde.kded6.loadModule gtkconfig >/dev/null
echo "Washi Pixel aplicado. Desfazer: $TEMA/scripts/restaurar-v2b-decoracao.sh"
