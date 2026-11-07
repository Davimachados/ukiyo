#!/usr/bin/env bash
# Instala o widget "Tela Washi" (brilho + saturação) na barra superior, logo antes da bandeja do sistema.
# Idempotente. Desfazer: scripts/remover-widget-tela.sh
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd); PROJ=$(cd "$TEMA/../.." && pwd)
ID=org.ukiyo.tela
CFG="$HOME/.config"; APPLETS="$CFG/plasma-org.kde.plasma.desktop-appletsrc"
B="$PROJ/backups/$(date +%F_%H%M%S)-washi-tela-widget"; mkdir -p "$B"
cp -a "$APPLETS" "$CFG/plasmashellrc" "$CFG/kwinoutputconfig.json" "$B/"
(cd "$B" && find . -type f -exec sha256sum {} + > SHA256SUMS); echo "Backup: $B"

python3 -I "$TEMA/tools/gerar-widget-tela.py" "$TEMA/plasmoid" >/dev/null
if kpackagetool6 -t Plasma/Applet -s "$ID" >/dev/null 2>&1; then
  kpackagetool6 -t Plasma/Applet -u "$TEMA/plasmoid/$ID" >/dev/null
else
  kpackagetool6 -t Plasma/Applet -i "$TEMA/plasmoid/$ID" >/dev/null
fi

# adiciona à barra superior (se ainda não estiver)
NOVO=$(qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var p = panels().filter(function (x) { return x.location === 'top'; })[0];
var ja = p.widgets('$ID');
if (ja.length === 0) { var w = p.addWidget('$ID'); print(w.id); } else { print(ja[0].id); }")
NOVO=$(echo "$NOVO" | tr -dc '0-9'); [ -n "$NOVO" ] || { echo "Não consegui adicionar o widget."; exit 1; }

# posiciona antes da bandeja: edita AppletOrder com o plasmashell parado
kquitapp6 plasmashell >/dev/null 2>&1 || true
for i in $(seq 1 40); do pgrep -x plasmashell >/dev/null || break; timeout 0.5 tail -f /dev/null || true; done
python3 -I - "$APPLETS" "$NOVO" <<'EOF'
import re, sys
p, novo = sys.argv[1], sys.argv[2]
s = open(p, encoding="utf-8").read()
cont = None
for m in re.finditer(r"^\[Containments\]\[(\d+)\]\n(.*?)(?=^\[|\Z)", s, re.M | re.S):
    if "plugin=org.kde.panel" in m.group(2) and re.search(r"^location=3$", m.group(2), re.M): cont = m.group(1)
bandeja = None
for m in re.finditer(rf"^\[Containments\]\[{cont}\]\[Applets\]\[(\d+)\]\n(.*?)(?=^\[|\Z)", s, re.M | re.S):
    if re.search(r"^plugin=org.kde.plasma.systemtray$", m.group(2), re.M): bandeja = m.group(1)
g = re.search(rf"^(\[Containments\]\[{cont}\]\[General\]\n)(.*?)(?=^\[|\Z)", s, re.M | re.S)
ordem = re.search(r"^AppletOrder=(.*)$", g.group(2), re.M).group(1).split(";")
ordem = [x for x in ordem if x and x != novo]
ordem.insert(ordem.index(bandeja) if bandeja in ordem else len(ordem), novo)
corpo = re.sub(r"^AppletOrder=.*$", "AppletOrder=" + ";".join(ordem), g.group(2), flags=re.M)
s = s[:g.start(2)] + corpo + s[g.end(2):]
open(p, "w", encoding="utf-8").write(s)
print("AppletOrder=" + ";".join(ordem))
EOF
(setsid plasmashell >/dev/null 2>&1 &)
for i in $(seq 1 40); do qdbus6 org.kde.plasmashell /PlasmaShell >/dev/null 2>&1 && break; timeout 0.5 tail -f /dev/null || true; done
echo "Widget Tela Washi instalado (applet $NOVO). Desfazer: $TEMA/scripts/remover-widget-tela.sh"
