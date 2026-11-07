#!/usr/bin/env bash
# Liga os comandos do Ukiyo em ~/.local/bin (tiktok, henshu, henshu-transcrever) e cria o atalho do Henshū no menu.
# Idempotente: rodar de novo só atualiza os links. Funciona de qualquer pasta onde o repositório foi clonado.
# Desfazer: scripts/instalar-comandos.sh --remover
set -euo pipefail
PROJ=$(cd "$(dirname "$0")/.." && pwd)
BIN="$HOME/.local/bin"; APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
CMDS=("tiktok:producao/tiktok.sh" "henshu:editor/henshu.sh" "henshu-transcrever:editor/henshu-transcrever.sh")

if [ "${1:-}" = "--remover" ]; then
  for c in "${CMDS[@]}"; do
    l="$BIN/${c%%:*}"; [ -L "$l" ] && [ "$(readlink -f "$l")" = "$PROJ/${c#*:}" ] && rm "$l" && echo "removido: $l"
  done
  rm -f "$APPS/henshu.desktop"; echo "Atalho do menu removido."; exit 0
fi

mkdir -p "$BIN" "$APPS"
for c in "${CMDS[@]}"; do
  ln -sfn "$PROJ/${c#*:}" "$BIN/${c%%:*}"; echo "  $BIN/${c%%:*} → ${c#*:}"
done
cat > "$APPS/henshu.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Henshū 編集
GenericName=Editor de vídeo com IA
Comment=Edite vídeos conversando com o Claude ou o Codex
Exec=$PROJ/editor/henshu.sh
Icon=kdenlive
Categories=AudioVideo;Video;AudioVideoEditing;
Terminal=false
StartupWMClass=henshu
EOF
command -v update-desktop-database >/dev/null && update-desktop-database "$APPS" 2>/dev/null || true
case ":$PATH:" in *":$BIN:"*) ;; *) echo "Aviso: $BIN não está no PATH. Faça logout/login (o ~/.profile padrão do Debian o adiciona)." ;; esac
echo "Comandos prontos."
