#!/usr/bin/env bash
# Washi V2 + V3 — janelas (Breeze recolorido + títulos DotGothic16), ícones pixel (fallback Breeze) e cursor pixel.
# Preserva o layout (não toca nos painéis). Não toca em OBS, áudio, login ou bloqueio. Idempotente.
# Desfazer: scripts/restaurar-v2v3-janelas-icones.sh
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd)
PROJ=$(cd "$TEMA/../.." && pwd)
CFG="$HOME/.config"; ICONS="$HOME/.local/share/icons"
XCUR="$HOME/.icons"   # libXcursor do Debian procura em ~/.icons, não em ~/.local/share/icons
B="$PROJ/backups/$(date +%F_%H%M%S)-washi-v2v3"
FONTE_TITULO="DotGothic16,12,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"   # 12 pt = 16 px: tamanho nativo da fonte
CURSOR_TAM=32                                                   # 2x a grade de 16 px (nítido)

fc-list : family | grep -i 'DotGothic16' >/dev/null || { echo "Fonte DotGothic16 ausente."; exit 1; }

# ---------- backup ----------
mkdir -p "$B"
for f in kdeglobals kwinrc kcminputrc breezerc gtk-3.0 gtk-4.0 gtkrc gtkrc-2.0 xsettingsd; do
  if [ -e "$CFG/$f" ]; then cp -a "$CFG/$f" "$B/"; else touch "$B/$f.ausente"; fi
done
[ -e "$XCUR" ] || touch "$B/dot-icons.ausente"
{
  echo "ICONES=$(kreadconfig6 --file kdeglobals --group Icons --key Theme --default breeze)"
  echo "CURSOR=$(kreadconfig6 --file kcminputrc --group Mouse --key cursorTheme --default breeze_cursors)"
  echo "CURSOR_TAM=$(kreadconfig6 --file kcminputrc --group Mouse --key cursorSize)"
  echo "FONTE_TITULO='$(kreadconfig6 --file kdeglobals --group WM --key activeFont)'"
  echo "SOMBRA=$(kreadconfig6 --file breezerc --group Common --key ShadowSize)"
  echo "CONTORNO=$(kreadconfig6 --file breezerc --group Common --key OutlineIntensity)"
} > "$B/estado.env"
(cd "$B" && find . -type f -exec sha256sum {} + > SHA256SUMS)
echo "Backup: $B"

# ---------- gerar e instalar temas ----------
python3 -I "$TEMA/tools/gerar-tema-icones.py" "$TEMA/icons" >/dev/null
python3 -I "$TEMA/tools/gerar-cursores.py" "$TEMA/cursors" >/dev/null
mkdir -p "$ICONS" "$XCUR"
rm -rf "$ICONS/washi-pixel" "$ICONS/washi-cursor" "$XCUR/washi-cursor"
cp -a "$TEMA/icons/washi-pixel" "$ICONS/"
cp -a "$TEMA/cursors/washi-cursor" "$XCUR/"

# ---------- V3: ícones e cursor ----------
/usr/lib/x86_64-linux-gnu/libexec/plasma-changeicons washi-pixel
kwriteconfig6 --file kcminputrc --group Mouse --key cursorSize "$CURSOR_TAM"
plasma-apply-cursortheme --size "$CURSOR_TAM" breeze_cursors >/dev/null   # força a propagação do tamanho
plasma-apply-cursortheme --size "$CURSOR_TAM" washi-cursor
# reaplica tudo no GTK (o gtkconfig só propaga o tamanho do cursor ao ser recarregado)
qdbus6 org.kde.kded6 /kded org.kde.kded6.unloadModule gtkconfig >/dev/null
qdbus6 org.kde.kded6 /kded org.kde.kded6.loadModule gtkconfig >/dev/null

# ---------- V2: janelas ----------
# Breeze continua como decoração; as cores já vêm do esquema Washi ([WM] e [Colors:Header]).
kwriteconfig6 --file kdeglobals --group WM --key activeFont "$FONTE_TITULO"
dbus-send --session --type=signal /KDEPlatformTheme org.kde.KDEPlatformTheme.refreshFonts   # KWin/apps releem as fontes
kwriteconfig6 --file breezerc --group Common --key ShadowSize ShadowSmall        # sombra curta: mais leve e mais "pixel"
kwriteconfig6 --file breezerc --group Common --key OutlineIntensity OutlineHigh  # contorno nítido de 1 px
qdbus6 org.kde.KWin /KWin reconfigure

echo "Washi V2+V3 aplicado. Desfazer: $TEMA/scripts/restaurar-v2v3-janelas-icones.sh"
