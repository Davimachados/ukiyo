#!/usr/bin/env bash
# Desfaz a V5a (bloqueio) usando o backup *-washi-v5-bloqueio mais antigo (ou o indicado).
set -euo pipefail
PROJ=$(cd "$(dirname "$0")/../../.." && pwd)
B="${1:-$(ls -d "$PROJ"/backups/*-washi-v5-bloqueio 2>/dev/null | sort | head -1)}"
[ -d "$B" ] || { echo "Backup não encontrado."; exit 1; }
if [ -e "$B/kscreenlockerrc.ausente" ]; then rm -f "$HOME/.config/kscreenlockerrc"; else cp -a "$B/kscreenlockerrc" "$HOME/.config/"; fi
echo "Bloqueio restaurado de $B."
