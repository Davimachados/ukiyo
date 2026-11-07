#!/usr/bin/env bash
# Desfaz a Washi V4 revertendo SÓ as chaves que ela alterou (preserva outros ajustes feitos depois nos apps).
#   Konsole : DefaultProfile e [UiSettings] ColorScheme voltam ao valor anterior; remove Sumi.profile/.colorscheme
#   Kdenlive: remove [UiSettings] ColorSchemePath (volta ao padrão do Kdenlive, Breeze escuro)
#   Audacity: [GUI] Theme volta ao valor anterior; remove o lançador audacity-sumi e o atalho local
# Valores anteriores lidos do backup *-washi-v4 mais antigo (ou do indicado). Cópia integral dos arquivos
# originais fica no próprio backup, para restauração manual completa.
# Uso: restaurar-v4-producao.sh [PASTA_BACKUP]
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd)
PROJ=$(cd "$TEMA/../.." && pwd)
CFG="$HOME/.config"; KS="$HOME/.local/share/konsole"; APPS="$HOME/.local/share/applications"
B="${1:-$(ls -d "$PROJ"/backups/*-washi-v4 2>/dev/null | sort | head -1)}"
[ -d "$B" ] || { echo "Backup não encontrado."; exit 1; }
echo "Restaurando de: $B"
for app in kdenlive audacity; do pgrep -x "$app" >/dev/null && { echo "Feche o $app antes."; exit 1; }; done

ant() { [ -f "$B/$1" ] && kreadconfig6 --file "$B/$1" --group "$2" --key "$3" || true; }
rk() { if [ -n "$4" ]; then kwriteconfig6 --file "$1" --group "$2" --key "$3" "$4"; else kwriteconfig6 --file "$1" --group "$2" --key "$3" --delete; fi; }

# Konsole
rk konsolerc "Desktop Entry" DefaultProfile "$(ant konsolerc 'Desktop Entry' DefaultProfile)"
rk konsolerc UiSettings ColorScheme "$(ant konsolerc UiSettings ColorScheme)"
if [ -e "$B/konsole-share.ausente" ]; then rm -f "$KS/Sumi.colorscheme" "$KS/Sumi.profile"
elif [ -d "$B/konsole-share" ]; then rm -rf "$KS"; cp -a "$B/konsole-share" "$KS"; fi

# Kdenlive
rk kdenliverc UiSettings ColorSchemePath "$(ant kdenliverc UiSettings ColorSchemePath)"

# Audacity
TEMA_ANT=""; [ -f "$B/audacity/audacity.cfg" ] && TEMA_ANT=$(python3 -I -c '
import re,sys; s=open(sys.argv[1],encoding="utf-8").read()
m=re.search(r"^\[GUI\]\n(.*?)(?=^\[|\Z)",s,re.M|re.S); t=re.search(r"^Theme=(.*)$",m.group(1),re.M) if m else None
print(t.group(1) if t else "")' "$B/audacity/audacity.cfg")
if [ -f "$CFG/audacity/audacity.cfg" ]; then
  python3 -I - "$CFG/audacity/audacity.cfg" "$TEMA_ANT" <<'EOF'
import re, sys
p, ant = sys.argv[1], sys.argv[2]
s = open(p, encoding="utf-8").read()
m = re.search(r"^\[GUI\]\n(.*?)(?=^\[|\Z)", s, re.M | re.S)
if m:
    corpo = m.group(1)
    corpo = re.sub(r"^Theme=.*$\n?", (f"Theme={ant}\n" if ant else ""), corpo, flags=re.M)
    s = s[:m.start(1)] + corpo + s[m.end(1):]
open(p, "w", encoding="utf-8").write(s)
EOF
fi
[ -e "$B/audacity-sumi.ausente" ] && rm -f "$HOME/.local/bin/audacity-sumi"
if [ -e "$B/audacity.desktop.ausente" ]; then rm -f "$APPS/audacity.desktop"
elif [ -e "$B/audacity.desktop.local" ]; then cp -a "$B/audacity.desktop.local" "$APPS/audacity.desktop"; fi
rm -rf "$HOME/.local/share/ukiyo/audacity-xdg"
kbuildsycoca6 >/dev/null 2>&1 || true
echo "Restaurado. Janelas do Konsole já abertas mantêm o perfil até serem reabertas."
