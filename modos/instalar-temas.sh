#!/usr/bin/env bash
# Pré-carrega (gera e instala) os recursos de TODOS os temas de modos/temas.conf, para que a troca não precise gerar nada.
#   esquemas de cores -> ~/.local/share/color-schemes
#   ícones            -> ~/.local/share/icons/<tema>-pixel
#   decorações        -> ~/.local/share/aurorae/themes/<Tema>Pixel
#   papéis de parede  -> ~/.local/share/wallpapers/<Tema>
# Uso: instalar-temas.sh [--se-necessario]   (com a opção, só refaz se algum gerador mudou desde a última vez)
# Roda no login por ~/.config/autostart/ukiyo-temas.desktop (instalado por este script).
set -euo pipefail
PROJ=$(cd "$(dirname "$0")/.." && pwd); T="$PROJ/themes"; SH="$HOME/.local/share"
EST="$HOME/.local/state/ukiyo"; mkdir -p "$EST"
CARIMBO="$EST/temas-instalados.sha256"

assinatura() { cat "$PROJ/modos/temas.conf" "$T"/*/tools/*.py "$T"/*/wallpaper/*.png "$PROJ/scripts/gerar-icones-refinados.py" "$T"/*/icons-refino/*/index.theme "$T"/*/icons-refino/*/apps/scalable/*.svg "$PROJ/scripts/gerar-icones-v2.py" "$T"/*/icons-v2/*/index.theme "$T"/*/icons-v2/*/apps/scalable/*.svg 2>/dev/null | sha256sum | cut -d' ' -f1; }
falta_algo() {   # algum recurso de algum tema do registro não está instalado?
  while IFS='|' read -r ID _ _ ICO DECO PACOTE _; do
    case "$ID" in ''|\#*) continue ;; esac
    [ -d "$SH/icons/$ICO" ] && [ -d "$SH/aurorae/themes/$DECO" ] && [ -d "$SH/wallpapers/$PACOTE" ] || return 0
  done < "$PROJ/modos/temas.conf"
  return 1
}
if [ "${1:-}" = "--se-necessario" ] && [ -f "$CARIMBO" ] && [ "$(cat "$CARIMBO")" = "$(assinatura)" ] && ! falta_algo; then
  exit 0
fi

mkdir -p "$SH/color-schemes" "$SH/icons" "$SH/aurorae/themes" "$SH/wallpapers"
atualizar_dir() {   # copia só se mudou (não invalida o cache de ícones à toa)
  local orig=$1 dest=$2
  if [ -d "$dest" ] && diff -rq "$orig" "$dest" >/dev/null 2>&1; then return 0; fi
  rm -rf "$dest"; cp -a "$orig" "$dest"; echo "  atualizado: $dest"
}
papel() {   # pacote de papel de parede
  local id=$1 nome=$2 png=$3 d="$SH/wallpapers/$1/contents/images"
  mkdir -p "$d"; cmp -s "$png" "$d/1920x1080.png" || cp "$png" "$d/1920x1080.png"
  printf '{"KPlugin": {"Id": "%s", "Name": "%s", "Authors": [{"Name": "Davi"}], "License": "CC-BY-SA-4.0"}}\n' "$id" "$nome" > "$SH/wallpapers/$id/metadata.json"
}

# Refino aprovado: gera somente a família nova, preservando os temas-base herdados.
if awk -F'|' '!/^#/ && $4 ~ /-refino$/ {found=1} END {exit !found}' "$PROJ/modos/temas.conf"; then
  python3 -I "$PROJ/scripts/gerar-icones-refinados.py" >/dev/null
fi

# Redesenho v2 aprovado, mantido em diretórios separados das versões anteriores.
if awk -F'|' '!/^#/ && $4 ~ /-art-v2$/ {found=1} END {exit !found}' "$PROJ/modos/temas.conf"; then
  python3 -I "$PROJ/scripts/gerar-icones-v2.py" >/dev/null
fi

# todos os temas do registro único modos/temas.conf
while IFS='|' read -r ID PASTA ESQ ICO DECO PACOTE IMAGEM TITULO GERAR _; do
  case "$ID" in ''|\#*) continue ;; esac
  D="$T/$PASTA"
  BASE_ICO=${ICO%-refino}
  BASE_ICO=${BASE_ICO%-art-v2}
  if [ "$GERAR" = sim ]; then
    python3 -I "$D/tools/gerar-esquema-$PASTA.py" "$D/color-schemes/$ESQ.colors" </dev/null >/dev/null
    python3 -I "$D/tools/gerar-tema-icones-$PASTA.py" "$D/icons" </dev/null >/dev/null
    python3 -I "$D/tools/gerar-decoracao-$PASTA.py" "$D/aurorae" </dev/null >/dev/null
    cmp -s "$D/color-schemes/$ESQ.colors" "$SH/color-schemes/$ESQ.colors" || cp "$D/color-schemes/$ESQ.colors" "$SH/color-schemes/"
    atualizar_dir "$D/icons/$BASE_ICO" "$SH/icons/$BASE_ICO"
    atualizar_dir "$D/aurorae/$DECO" "$SH/aurorae/themes/$DECO"
  else   # instalação própria (Washi): aqui só confere
    for f in "$SH/color-schemes/$ESQ.colors" "$SH/icons/$BASE_ICO" "$SH/aurorae/themes/$DECO"; do
      [ -e "$f" ] || echo "  AVISO: falta $f (instale o tema $ID pelos scripts em themes/$PASTA/scripts/)"
    done
  fi
  # Os ícones novos herdam pastas/simbólicos do tema-base, que continua instalado.
  case "$ICO" in
    *-art-v2) atualizar_dir "$D/icons-v2/$ICO" "$SH/icons/$ICO" ;;
    *-refino) atualizar_dir "$D/icons-refino/$ICO" "$SH/icons/$ICO" ;;
  esac
  papel "$PACOTE" "$TITULO" "$PROJ/$IMAGEM"
done < "$PROJ/modos/temas.conf"

# pré-carregamento padrão no login
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/ukiyo-temas.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=ukiyo: pré-carregar temas
Comment=Mantém os recursos dos temas instalados (só refaz se algum gerador mudou)
Exec=$PROJ/modos/instalar-temas.sh --se-necessario
NoDisplay=true
X-KDE-autostart-phase=2
EOF
assinatura > "$CARIMBO"
echo "Temas pré-carregados."
