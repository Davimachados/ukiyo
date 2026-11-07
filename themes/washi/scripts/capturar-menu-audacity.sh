#!/usr/bin/env bash
# Captura cronometrada de um menu aberto do Audacity (para conferir o tema V4).
# Vai para a área de trabalho 二 (onde está só o Audacity de teste), espera e captura a tela inteira.
# Nesse intervalo, clique em um menu do Audacity (ex.: Efeitos) e deixe-o aberto.
# Uso: capturar-menu-audacity.sh [segundos]   (padrão 10)
set -euo pipefail
PROJ=$(cd "$(dirname "$0")/../../.." && pwd)
OUT="$PROJ/docs/visual/capturas/washi-v4b-audacity-menu.png"
ESPERA=${1:-10}
pgrep -x audacity >/dev/null || { echo "Abra o Audacity pelo menu/dock antes."; exit 1; }
ID2=$(qdbus6 --literal org.kde.KWin /VirtualDesktopManager org.freedesktop.DBus.Properties.Get \
      org.kde.KWin.VirtualDesktopManager desktops | grep -oE '[0-9a-f]{8}-[0-9a-f-]{27}' | sed -n 2p)
echo "Indo para a área 二. Abra um menu do Audacity e mantenha aberto: captura em $ESPERA s."
qdbus6 org.kde.KWin /VirtualDesktopManager org.freedesktop.DBus.Properties.Set org.kde.KWin.VirtualDesktopManager current "$ID2"
sleep "$ESPERA"
spectacle -b -n -f -o "$OUT" >/dev/null 2>&1 && echo "Captura: $OUT" || echo "Falhou a captura (tela bloqueada?)."
