#!/usr/bin/env bash
# Remove o widget "Tela Washi": volta a saturação para 100% (sem perfil ICC), tira o widget da barra
# e desinstala o pacote. O brilho fica como estiver (ajuste pela bandeja ou teclas de brilho).
set -euo pipefail
ID=org.ukiyo.tela
AUX="$HOME/.local/share/plasma/plasmoids/$ID/contents/code/washi-tela"
[ -x "$AUX" ] && "$AUX" saturacao 100 >/dev/null || true
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
panels().forEach(function (p) { p.widgets('$ID').forEach(function (w) { w.remove(); }); });" >/dev/null
kpackagetool6 -t Plasma/Applet -r "$ID" >/dev/null 2>&1 || true
rm -rf "${XDG_DATA_HOME:-$HOME/.local/share}/ukiyo/icc" "${XDG_STATE_HOME:-$HOME/.local/state}/ukiyo/saturacao"
echo "Widget removido; saturação em 100% (sRGB)."
