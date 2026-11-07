#!/usr/bin/env bash
# Prévia do tema de login Washi no modo de teste do SDDM (não aplica nada, não reinicia o SDDM).
# Abre o greeter de teste numa janela, na área de trabalho 三, e captura a tela após N segundos.
# Nesse intervalo, MEXA O MOUSE sobre a janela (o Breeze esconde o formulário sem interação).
# Não digite sua senha real: no modo de teste ela não serve para nada.
# Feche a janela pelo × depois. Uso: previa-login.sh [segundos]  (padrão 12)
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd)
OUT="$TEMA/preview/v5-login-preview-interativa.png"
ESPERA=${1:-12}
python3 -I "$TEMA/tools/gerar-sddm.py" "$TEMA/sddm" >/dev/null
ID3=$(qdbus6 --literal org.kde.KWin /VirtualDesktopManager org.freedesktop.DBus.Properties.Get \
      org.kde.KWin.VirtualDesktopManager desktops | grep -oE '[0-9a-f]{8}-[0-9a-f-]{27}' | sed -n 3p)
qdbus6 org.kde.KWin /VirtualDesktopManager org.freedesktop.DBus.Properties.Set org.kde.KWin.VirtualDesktopManager current "$ID3"
(cd ~ && setsid sddm-greeter-qt6 --test-mode --theme "$TEMA/sddm/washi" >/dev/null 2>&1 &)
echo "Prévia aberta na área 三. Mexa o mouse sobre ela; captura em $ESPERA s."
sleep "$ESPERA"
spectacle -b -n -f -o "$OUT" >/dev/null 2>&1 && echo "Captura: $OUT" || echo "Falhou a captura."
echo "Feche a janela de teste pelo × quando terminar."
