#!/usr/bin/env bash
# Grava uma amostra de voz CRUA (sem filtros) do microfone padrão, para avaliar
# ruído, ganho e filtros antes de configurá-los no OBS.
# Uso: scripts/gravar-amostra-voz.sh [segundos]   (padrão 30)
set -euo pipefail
DUR=${1:-30}
DEST="$(xdg-user-dir VIDEOS 2>/dev/null || echo "$HOME/Videos")/TikTok/testes"
mkdir -p "$DEST"
OUT="$DEST/amostra-voz-$(date +%F_%H%M%S).wav"
SRC=$(pactl get-default-source)

cat <<'EOF'
=== Amostra de voz ===
Fique na posição em que você costuma gravar e fale no volume normal.
Deixe o ambiente como fica nas gravações reais (ar-condicionado/ventilador como de costume).

Roteiro:
  0–5 s   : SILÊNCIO total (mede o ruído de fundo)
  depois  : leia em voz normal, com pausas naturais:

  "Oi, pessoal! Hoje eu vou mostrar como montei meu estúdio no Linux.
   Três, dois, um... Sim, sapo, chuva, pressa, xícara, trinta e três tigres.
   Agora uma frase mais baixa... e uma mais animada: BORA COMEÇAR!"

  no fim  : mais 3 s de silêncio
EOF
for i in 3 2 1; do echo "Começando em $i..."; sleep 1; done
echo ">>> GRAVANDO ($DUR s) — fique em SILÊNCIO nos primeiros 5 s"
ffmpeg -hide_banner -loglevel error -nostdin -y -f pulse -i "$SRC" -t "$DUR" -c:a pcm_s24le "$OUT"
echo ">>> Fim. Arquivo: $OUT"
