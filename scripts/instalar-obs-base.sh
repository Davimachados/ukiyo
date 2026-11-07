#!/usr/bin/env bash
# Instala a base do OBS (perfil + cenas "TikTok Vertical") a partir de config/obs/.
# Idempotente. Faz backup completo de ~/.config/obs-studio antes de mexer, se existir.
# Desfazer: ver docs/mudancas.md (restaurar o backup ou apagar ~/.config/obs-studio).
set -euo pipefail
PROJ=$(cd "$(dirname "$0")/.." && pwd)
OBS="$HOME/.config/obs-studio"
VIDEOS=$(xdg-user-dir VIDEOS 2>/dev/null || echo "$HOME/Videos")

if pgrep -x obs >/dev/null; then echo "Feche o OBS antes de rodar este script."; exit 1; fi

if [ -d "$OBS" ]; then
  B="$PROJ/backups/$(date +%F_%H%M%S)-obs"; mkdir -p "$B"
  cp -a "$OBS" "$B/"; echo "Backup: $B/obs-studio"
fi

mkdir -p "$OBS/basic/profiles/TikTok_Vertical" "$OBS/basic/scenes" "$VIDEOS/TikTok/brutos"
sed "s|@VIDEOS@|$VIDEOS|" "$PROJ/config/obs/profile/basic.ini" > "$OBS/basic/profiles/TikTok_Vertical/basic.ini"
cp "$PROJ/config/obs/profile/recordEncoder.json" "$PROJ/config/obs/profile/streamEncoder.json" \
   "$OBS/basic/profiles/TikTok_Vertical/"
# Não sobrescreve cenas já editadas no OBS (a menos que FORCAR_CENAS=1)
if [ ! -f "$OBS/basic/scenes/TikTok_Vertical.json" ] || [ "${FORCAR_CENAS:-0}" = 1 ]; then
  cp "$PROJ/config/obs/scenes/TikTok_Vertical.json" "$OBS/basic/scenes/"
fi

if [ ! -f "$OBS/global.ini" ]; then
  cat > "$OBS/global.ini" <<EOF
[General]
FirstRun=true
Language=pt-BR

[Basic]
Profile=TikTok Vertical
ProfileDir=TikTok_Vertical
SceneCollection=TikTok Vertical
SceneCollectionFile=TikTok_Vertical
EOF
else
  echo "global.ini já existe: selecione no OBS Perfil → 'TikTok Vertical' e Coleção de cenas → 'TikTok Vertical'."
fi
echo "OBS base instalada. Gravações em: $VIDEOS/TikTok/brutos"
