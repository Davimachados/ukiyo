#!/usr/bin/env bash
# Washi V1 — desktop: papel de parede, esquema de cores, barra superior + dock, áreas de trabalho, efeitos leves.
# Não toca em rede, áudio, drivers nem OBS. Idempotente.
# Desfazer: scripts/restaurar-v1-desktop.sh  (usa o backup *-washi-v1 mais antigo = estado anterior à 1ª aplicação)
set -euo pipefail
TEMA=$(cd "$(dirname "$0")/.." && pwd)
PROJ=$(cd "$TEMA/../.." && pwd)
CFG="$HOME/.config"; SHARE="$HOME/.local/share"
B="$PROJ/backups/$(date +%F_%H%M%S)-washi-v1"

fc-list : family | grep -i 'DotGothic16' >/dev/null || { echo "Fonte DotGothic16 ausente. Rode: sudo apt install fonts-dotgothic16"; exit 1; }
qdbus6 org.kde.plasmashell /PlasmaShell >/dev/null 2>&1 || { echo "plasmashell não está rodando."; exit 1; }

# ---------- backup do estado atual ----------
mkdir -p "$B"
for f in kdeglobals kwinrc plasmarc plasmashellrc plasma-org.kde.plasma.desktop-appletsrc; do
  if [ -e "$CFG/$f" ]; then cp -a "$CFG/$f" "$B/"; else touch "$B/$f.ausente"; fi
done
{
  echo "COLORSCHEME=$(kreadconfig6 --file kdeglobals --group General --key ColorScheme)"
  echo "DESKTOPTHEME=$(kreadconfig6 --file plasmarc --group Theme --key name --default default)"
  echo "BLUR=$(kreadconfig6 --file kwinrc --group Plugins --key blurEnabled)"
  echo "CONTRAST=$(kreadconfig6 --file kwinrc --group Plugins --key contrastEnabled)"
  echo "ANIM=$(kreadconfig6 --file kdeglobals --group KDE --key AnimationDurationFactor)"
} > "$B/estado.env"
qdbus6 --literal org.kde.KWin /VirtualDesktopManager org.freedesktop.DBus.Properties.Get \
  org.kde.KWin.VirtualDesktopManager desktops > "$B/desktops.txt"
echo "Backup: $B"

# ---------- instalar arquivos ----------
mkdir -p "$SHARE/color-schemes" "$SHARE/wallpapers/Washi/contents/images" "$SHARE/icons/hicolor/scalable/apps"
cp "$TEMA/color-schemes/Washi.colors" "$TEMA/color-schemes/Sumi.colors" "$SHARE/color-schemes/"
cp "$TEMA/wallpaper/entardecer-1920x1080.png" "$SHARE/wallpapers/Washi/contents/images/1920x1080.png"
cat > "$SHARE/wallpapers/Washi/metadata.json" <<'EOF'
{"KPlugin": {"Id": "Washi", "Name": "Washi — Entardecer", "Authors": [{"Name": "Davi"}], "License": "CC-BY-SA-4.0"}}
EOF
cp "$TEMA/icons-src/lancador.svg" "$SHARE/icons/hicolor/scalable/apps/washi-lancador.svg"
cp "$TEMA/icons-src/sakura.svg"   "$SHARE/icons/hicolor/scalable/apps/washi-sakura.svg"
touch "$SHARE/icons/hicolor"   # sinaliza mudança ao cache de ícones

# ---------- cores e estilo Plasma ----------
plasma-apply-colorscheme Washi
plasma-apply-desktoptheme default      # Breeze que segue o esquema de cores (painéis em washi)

# ---------- áreas de trabalho 一 二 三 四 ----------
NOMES=(一 二 三 四)
mapfile -t IDS < <(grep -oE '[0-9a-f]{8}-[0-9a-f-]{27}' "$B/desktops.txt")
qdbus6 org.kde.KWin /VirtualDesktopManager org.kde.KWin.VirtualDesktopManager.setDesktopName "${IDS[0]}" "${NOMES[0]}"
for i in 1 2 3; do
  if [ -n "${IDS[$i]:-}" ]; then
    qdbus6 org.kde.KWin /VirtualDesktopManager org.kde.KWin.VirtualDesktopManager.setDesktopName "${IDS[$i]}" "${NOMES[$i]}"
  else
    qdbus6 org.kde.KWin /VirtualDesktopManager org.kde.KWin.VirtualDesktopManager.createDesktop "$i" "${NOMES[$i]}"
  fi
done
qdbus6 org.kde.KWin /VirtualDesktopManager org.freedesktop.DBus.Properties.Set org.kde.KWin.VirtualDesktopManager rows 1 >/dev/null 2>&1 || true

# ---------- painéis ----------
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$(cat "$TEMA/plasma/layout-v1.js")"

# ---------- painéis opacos (cor washi fiel, sem tingir com o papel de parede) ----------
# plasmashellrc é regravado pelo plasmashell ao sair: escrever com ele parado e reiniciar
# (o reinício também faz os widgets relerem as opções gravadas pelo layout, ex.: fonte do relógio).
PAINEIS=$(awk -F'[][]' '/^\[Containments\]\[[0-9]+\]$/{id=$4} /^plugin=org.kde.panel$/{print id}' "$CFG/plasma-org.kde.plasma.desktop-appletsrc")
kquitapp6 plasmashell >/dev/null 2>&1 || true
for i in $(seq 1 40); do pgrep -x plasmashell >/dev/null || break; timeout 0.5 tail -f /dev/null || true; done
for p in $PAINEIS; do kwriteconfig6 --file plasmashellrc --group PlasmaViews --group "Panel $p" --key panelOpacity 1; done
(setsid plasmashell >/dev/null 2>&1 &)
for i in $(seq 1 40); do qdbus6 org.kde.plasmashell /PlasmaShell >/dev/null 2>&1 && break; timeout 0.5 tail -f /dev/null || true; done

# ---------- papel de parede ----------
plasma-apply-wallpaperimage "$SHARE/wallpapers/Washi"

# ---------- efeitos leves ----------
kwriteconfig6 --file kwinrc --group Plugins --key blurEnabled false
kwriteconfig6 --file kwinrc --group Plugins --key contrastEnabled false
kwriteconfig6 --file kdeglobals --group KDE --key AnimationDurationFactor 0.5
qdbus6 org.kde.KWin /KWin reconfigure

echo "Washi V1 aplicado. Para desfazer: $TEMA/scripts/restaurar-v1-desktop.sh"
