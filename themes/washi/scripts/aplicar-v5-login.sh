#!/usr/bin/env bash
# Washi V5b — tela de LOGIN (SDDM). Rodar COM sudo:  sudo ~/ukiyo/themes/washi/scripts/aplicar-v5-login.sh
# NÃO reinicia o SDDM: o tema vale a partir do próximo logout/boot.
#   1) instala o tema /usr/share/sddm/themes/washi (gerado de themes/washi/sddm/washi)
#   2) cria /etc/sddm.conf.d/10-washi.conf  ->  [Theme] Current=washi, cursor pixel
#   3) instala o cursor washi-cursor em /usr/share/icons (o SDDM não lê ~/.icons)
#   4) cores do greeter = esquema Washi (/var/lib/sddm/.config/kdeglobals), como o botão
#      "Aplicar configurações do Plasma" da página Tela de login faria
# Desfazer: sudo ~/ukiyo/themes/washi/scripts/restaurar-v5-login.sh
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Rode com sudo."; exit 1; }
U=${SUDO_USER:?rode com sudo a partir do seu usuário}
UH=$(getent passwd "$U" | cut -d: -f6)
TEMA=$(cd "$(dirname "$0")/.." && pwd); PROJ=$(cd "$TEMA/../.." && pwd)
SRC="$TEMA/sddm/washi"
B="$PROJ/backups/$(date +%F_%H%M%S)-washi-v5-login"
SDDMH=$(getent passwd sddm | cut -d: -f6)

# ---------- verificações ----------
for f in Main.qml WashiClock.qml theme.conf metadata.desktop fundo.png torii.svg; do
  [ -f "$SRC/$f" ] || { echo "Falta $SRC/$f (rode tools/gerar-sddm.py)."; exit 1; }
done
fc-list : family | grep -i DotGothic16 >/dev/null || { echo "Fonte DotGothic16 ausente no sistema."; exit 1; }
[ -d "$UH/.icons/washi-cursor" ] || { echo "Cursor washi-cursor ausente em $UH/.icons."; exit 1; }

# ---------- backup ----------
mkdir -p "$B"
[ -d /etc/sddm.conf.d ] && cp -a /etc/sddm.conf.d "$B/" || touch "$B/sddm.conf.d.ausente"
[ -e /etc/sddm.conf ] && cp -a /etc/sddm.conf "$B/" || touch "$B/sddm.conf.ausente"
[ -e /usr/share/sddm/themes/washi ] && cp -a /usr/share/sddm/themes/washi "$B/tema-washi" || touch "$B/tema-washi.ausente"
[ -e /usr/share/icons/washi-cursor ] && touch "$B/cursor.existia" || touch "$B/cursor.ausente"
if [ -e "$SDDMH/.config/kdeglobals" ]; then cp -a "$SDDMH/.config/kdeglobals" "$B/sddm-kdeglobals"; else touch "$B/sddm-kdeglobals.ausente"; fi
readlink -f /usr/share/sddm/themes/debian-theme > "$B/tema-debian-ativo.txt" || true
(cd "$B" && find . -type f -exec sha256sum {} + > SHA256SUMS)
chown -R "$U:$U" "$B"
echo "Backup: $B"

# ---------- instalação ----------
rm -rf /usr/share/sddm/themes/washi
install -d -m 755 /usr/share/sddm/themes/washi
cp -r "$SRC"/. /usr/share/sddm/themes/washi/
chown -R root:root /usr/share/sddm/themes/washi; chmod -R u=rwX,go=rX /usr/share/sddm/themes/washi

rm -rf /usr/share/icons/washi-cursor
cp -a "$UH/.icons/washi-cursor" /usr/share/icons/
chown -R root:root /usr/share/icons/washi-cursor; chmod -R u=rwX,go=rX /usr/share/icons/washi-cursor

install -d -m 755 /etc/sddm.conf.d
cat > /etc/sddm.conf.d/10-washi.conf <<'EOF'
# ukiyo: tema de login Washi. Remover este arquivo volta ao tema padrão do Debian.
[Theme]
Current=washi
CursorTheme=washi-cursor
CursorSize=32
EOF
chmod 644 /etc/sddm.conf.d/10-washi.conf

install -d -o sddm -g sddm -m 755 "$SDDMH/.config"
install -o sddm -g sddm -m 644 "$UH/.local/share/color-schemes/Washi.colors" "$SDDMH/.config/kdeglobals"

echo "Tema de login Washi instalado. Vale no próximo logout/boot (o SDDM NÃO foi reiniciado)."
echo "Desfazer: sudo $TEMA/scripts/restaurar-v5-login.sh"
