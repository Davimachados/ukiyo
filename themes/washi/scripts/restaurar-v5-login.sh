#!/usr/bin/env bash
# Desfaz a V5b (login SDDM). Rodar COM sudo:  sudo ~/ukiyo/themes/washi/scripts/restaurar-v5-login.sh [BACKUP]
# Não reinicia o SDDM (vale no próximo logout/boot).
#
# EMERGÊNCIA — se a tela de login não aparecer ou não aceitar a senha:
#   1. Ctrl+Alt+F3  → login em modo texto com seu usuário
#   2. sudo rm /etc/sddm.conf.d/10-washi.conf      (volta ao tema padrão do Debian)
#   3. sudo systemctl restart sddm                 (ou reinicie o computador)
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Rode com sudo."; exit 1; }
U=${SUDO_USER:?rode com sudo a partir do seu usuário}
TEMA=$(cd "$(dirname "$0")/.." && pwd); PROJ=$(cd "$TEMA/../.." && pwd)
B="${1:-$(ls -d "$PROJ"/backups/*-washi-v5-login 2>/dev/null | sort | head -1)}"
[ -d "$B" ] || { echo "Backup não encontrado."; exit 1; }
SDDMH=$(getent passwd sddm | cut -d: -f6)
echo "Restaurando de: $B"

rm -f /etc/sddm.conf.d/10-washi.conf
if [ -e "$B/sddm.conf.d.ausente" ]; then rmdir /etc/sddm.conf.d 2>/dev/null || true
elif [ -d "$B/sddm.conf.d" ]; then cp -a "$B/sddm.conf.d"/. /etc/sddm.conf.d/; fi
rm -rf /usr/share/sddm/themes/washi
[ -d "$B/tema-washi" ] && cp -a "$B/tema-washi" /usr/share/sddm/themes/washi
[ -e "$B/cursor.ausente" ] && rm -rf /usr/share/icons/washi-cursor
if [ -e "$B/sddm-kdeglobals.ausente" ]; then rm -f "$SDDMH/.config/kdeglobals"
elif [ -e "$B/sddm-kdeglobals" ]; then install -o sddm -g sddm -m 644 "$B/sddm-kdeglobals" "$SDDMH/.config/kdeglobals"; fi
echo "Login restaurado (tema padrão do Debian no próximo logout/boot)."
