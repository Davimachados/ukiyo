#!/usr/bin/env bash
# Captura de verificação do Audacity com a V4 (tema dark + GTK escuro só nele).
# Abre um projeto VAZIO pelo lançador do menu/dock (não pede para salvar ao fechar), captura a janela
# ativa (inclui a janela "Bem-vindo", que testa a legibilidade do texto) e fecha o Audacity.
# Requer a tela desbloqueada. Uso: themes/washi/scripts/capturar-audacity-v4.sh
set -euo pipefail
PROJ=$(cd "$(dirname "$0")/../../.." && pwd)
OUT="$PROJ/docs/visual/capturas/washi-v4-audacity.png"
[ "$(qdbus6 org.freedesktop.ScreenSaver /ScreenSaver org.freedesktop.ScreenSaver.GetActive)" = false ] || { echo "Desbloqueie a tela primeiro."; exit 1; }
pgrep -x audacity >/dev/null && { echo "Feche o Audacity antes."; exit 1; }
kioclient exec "$HOME/.local/share/applications/audacity.desktop" >/dev/null 2>&1 &
for i in $(seq 1 20); do pgrep -x audacity >/dev/null && break; sleep 0.5; done
sleep 6
spectacle -b -n -a -o "$OUT" >/dev/null 2>&1 && echo "Captura: $OUT"
JS=$(mktemp --suffix=.js)
echo 'for (const w of workspace.windowList()) { if (w.resourceClass === "audacity") w.closeWindow(); }' > "$JS"
ID=$(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript "$JS" washi-fecha-audacity)
qdbus6 org.kde.KWin /Scripting/Script"$ID" org.kde.kwin.Script.run
sleep 2; qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript washi-fecha-audacity >/dev/null; rm -f "$JS"
pgrep -x audacity >/dev/null && echo "Audacity ainda aberto: feche manualmente." || echo "Audacity fechado."
