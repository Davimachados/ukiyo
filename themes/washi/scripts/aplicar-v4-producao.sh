#!/usr/bin/env bash
# Washi V4 — variante Sumi (escura) só nos apps de produção, por configuração de cada app.
#   Konsole : perfil + esquema de terminal "Sumi" e esquema de cores da janela = Sumi
#   Kdenlive: tema de cores do próprio Kdenlive = Sumi.colors
#   Audacity: tema embutido "dark" (não há paleta personalizada utilizável na versão 3.7.3)
# O esquema global (Washi), painéis, Dolphin e decoração não são alterados. OBS e áudio não são tocados.
# Desfazer: scripts/restaurar-v4-producao.sh
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd)
PROJ=$(cd "$TEMA/../.." && pwd)
CFG="$HOME/.config"; KS="$HOME/.local/share/konsole"
SUMI="$HOME/.local/share/color-schemes/Sumi.colors"
B="$PROJ/backups/$(date +%F_%H%M%S)-washi-v4"

[ -f "$SUMI" ] || { echo "Sumi.colors não instalado (rode a V1)."; exit 1; }
for app in kdenlive audacity; do pgrep -x "$app" >/dev/null && { echo "Feche o $app antes."; exit 1; }; done

# ---------- backup ----------
mkdir -p "$B"
for f in konsolerc kdenliverc audacity; do
  if [ -e "$CFG/$f" ]; then cp -a "$CFG/$f" "$B/"; else touch "$B/$f.ausente"; fi
done
if [ -n "$(ls -A "$KS" 2>/dev/null)" ]; then cp -a "$KS" "$B/konsole-share"; else touch "$B/konsole-share.ausente"; fi
(cd "$B" && find . -type f -exec sha256sum {} + > SHA256SUMS)
echo "Backup: $B"

# ---------- Konsole ----------
mkdir -p "$KS"
cp "$TEMA/konsole/Sumi.colorscheme" "$TEMA/konsole/Sumi.profile" "$KS/"
kwriteconfig6 --file konsolerc --group "Desktop Entry" --key DefaultProfile Sumi.profile
kwriteconfig6 --file konsolerc --group UiSettings --key ColorScheme Sumi

# ---------- Kdenlive ----------
kwriteconfig6 --file kdenliverc --group UiSettings --key ColorSchemePath "$SUMI"

# ---------- Audacity ----------
mkdir -p "$CFG/audacity"
python3 -I - "$CFG/audacity/audacity.cfg" <<'EOF'
import sys, os, re
p = sys.argv[1]
s = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
def setkey(s, grupo, chave, valor):
    m = re.search(rf"^\[{grupo}\]\n(.*?)(?=^\[|\Z)", s, re.M | re.S)
    if not m: return s.rstrip("\n") + ("\n\n" if s.strip() else "") + f"[{grupo}]\n{chave}={valor}\n"
    corpo = m.group(1)
    if re.search(rf"^{chave}=", corpo, re.M): corpo = re.sub(rf"^{chave}=.*$", f"{chave}={valor}", corpo, flags=re.M)
    else: corpo = f"{chave}={valor}\n" + corpo
    return s[:m.start(1)] + corpo + s[m.end(1):]
s = setkey(s, "GUI", "Theme", "dark")
open(p, "w", encoding="utf-8").write(s)
EOF
# Audacity: parte GTK escura só nele, via lançador próprio (o esquema global continua Washi)
APPS="$HOME/.local/share/applications"
[ -e "$HOME/.local/bin/audacity-sumi" ] || touch "$B/audacity-sumi.ausente"
[ -e "$APPS/audacity.desktop" ] && cp -a "$APPS/audacity.desktop" "$B/audacity.desktop.local" || touch "$B/audacity.desktop.ausente"
mkdir -p "$HOME/.local/bin" "$APPS"
cp "$TEMA/scripts/audacity-sumi" "$HOME/.local/bin/audacity-sumi"
sed "s|^Exec=.*|Exec=$HOME/.local/bin/audacity-sumi %F|" /usr/share/applications/audacity.desktop > "$APPS/audacity.desktop"
kbuildsycoca6 >/dev/null 2>&1 || true
echo "Washi V4 aplicado. Abra novas janelas do Konsole/Kdenlive/Audacity para ver. Desfazer: $TEMA/scripts/restaurar-v4-producao.sh"
