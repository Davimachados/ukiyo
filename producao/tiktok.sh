#!/usr/bin/env bash
# tiktok — esteira de pós-produção do ukiyo (Etapa 5a). Vídeo sempre na GPU (VA-API), nunca x264.
#
#   tiktok novo <nome>                     cria ~/Vídeos/TikTok/<AAAA-MM-DD>_<nome>/ a partir do modelo
#   tiktok importar <arquivo|pasta>...     copia mídia para brutos/ do vídeo atual, renomeando por data/hora
#   tiktok silencios <vídeo> [limiar_dB] [mín_s]   gera cópia sem as pausas (padrão −35 dB, 0,6 s)
#   tiktok exportar <vídeo> [saída]        1080×1920 H.264 VA-API + AAC, áudio normalizado em −14 LUFS
#   tiktok limpar [dias] [--apagar]        lista (ou apaga) proxies e cache do Kdenlive mais velhos que N dias (padrão 30)
#   tiktok onde                            mostra a pasta do vídeo atual
#
# "Vídeo atual": a pasta de vídeo em que você está (cd), senão a mais recente em ~/Vídeos/TikTok.
# Nunca apaga nem altera os originais; tudo que é gerado vai para arquivos novos.
set -euo pipefail
export LC_NUMERIC=C   # números com ponto decimal (o FFmpeg não entende vírgula)

RAIZ="${TIKTOK_RAIZ:-$(xdg-user-dir VIDEOS 2>/dev/null || echo "$HOME/Vídeos")/TikTok}"
GPU="${TIKTOK_GPU:-/dev/dri/renderD128}"
ALVO_LUFS=-14; ALVO_TP=-1.0; ALVO_LRA=11
EXT_MIDIA='mp4|mov|mkv|m4v|webm|avi|mts|m2ts|3gp|wav|flac|mp3|m4a|aac|ogg|opus|jpg|jpeg|png|heic|webp'

erro() { echo "tiktok: $*" >&2; exit 1; }
info() { echo "› $*"; }
precisa() { [ -e "$1" ] || erro "não encontrado: $1"; }

pasta_atual() {   # pasta de vídeo: a do diretório atual (ou acima), senão a mais recente
  local d=$PWD
  while [ "$d" != / ]; do
    [ -f "$d/notas.md" ] && [ -d "$d/brutos" ] && { echo "$d"; return; }
    d=$(dirname "$d")
  done
  local ult; ult=$(ls -1d "$RAIZ"/????-??-??_*/ 2>/dev/null | sort | tail -1)
  [ -n "$ult" ] || erro "nenhum vídeo ainda — crie com: tiktok novo <nome>"
  echo "${ult%/}"
}

duracao() { ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$1"; }
tem_audio() { [ -n "$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$1")" ]; }

# ---------------------------------------------------------------------------------------------------------------
cmd_novo() {
  local nome=${1:?uso: tiktok novo <nome>}
  nome=$(echo "$nome" | tr ' /' '-_' | tr -cd '[:alnum:]_.-' | tr '[:upper:]' '[:lower:]')
  [ -n "$nome" ] || erro "nome inválido"
  local d="$RAIZ/$(date +%F)_$nome"
  [ -e "$d" ] && erro "já existe: $d"
  mkdir -p "$d"/{brutos,audio,legendas,proxies,export}
  cat > "$d/notas.md" <<EOF
# $nome — $(date +%F)

## Gancho (primeiros 2 s)


## Roteiro / tópicos
-

## Legenda e hashtags


## Checklist
- [ ] brutos importados (\`tiktok importar …\`)
- [ ] pausas cortadas (\`tiktok silencios …\`)
- [ ] montagem no Kdenlive (perfil vertical 1080×1920)
- [ ] legendas revisadas
- [ ] export final (\`tiktok exportar …\`) conferido no celular
- [ ] publicado em:
EOF
  info "criado: $d"
}

# ---------------------------------------------------------------------------------------------------------------
data_de() {   # data de gravação: metadado creation_time → data de modificação
  local f=$1 c
  c=$(ffprobe -v error -show_entries format_tags=creation_time -of default=nw=1:nk=1 "$f" 2>/dev/null | head -1 || true)
  if [ -n "$c" ] && date -d "$c" >/dev/null 2>&1; then date -d "$c" +%F_%H-%M-%S; else date -r "$f" +%F_%H-%M-%S; fi
}
cmd_importar() {
  [ $# -gt 0 ] || erro "uso: tiktok importar <arquivo|pasta>..."
  local d; d=$(pasta_atual); local n=0 p=0
  while IFS= read -r -d '' f; do
    local base ext dest
    base=$(basename "$f"); ext=${base##*.}; ext=${ext,,}
    if [[ $base =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2} ]]; then dest="$d/brutos/${base%.*}.$ext"   # já tem data no nome
    else dest="$d/brutos/$(data_de "$f")_${base%.*}.$ext"; fi
    if [ -e "$dest" ]; then p=$((p + 1)); continue; fi
    cp --preserve=timestamps "$f" "$dest"; n=$((n + 1)); info "$(basename "$dest")"
  done < <(find "$@" -maxdepth 3 -type f -regextype posix-extended -iregex ".*\.($EXT_MIDIA)$" -print0 | sort -z)
  info "$n arquivo(s) copiado(s) para $d/brutos ($p já existiam). Originais intactos."
}

# ---------------------------------------------------------------------------------------------------------------
cmd_silencios() {
  local ent=${1:?uso: tiktok silencios <vídeo> [limiar_dB] [mín_s]} lim=${2:--35} min=${3:-0.6}
  precisa "$ent"; tem_audio "$ent" || erro "o arquivo não tem áudio"
  local margem=0.15 dur saida lista
  dur=$(duracao "$ent")
  saida="${ent%.*}_sem-pausas.mp4"; lista="${ent%.*}_sem-pausas.cortes.txt"
  info "procurando pausas (< ${lim} dB por ≥ ${min} s)…"
  # trechos a manter = complemento dos silêncios, com margem para não comer o começo/fim das falas
  local trechos
  trechos=$(ffmpeg -hide_banner -nostats -i "$ent" -map 0:a:0 -af "silencedetect=noise=${lim}dB:d=${min}" -f null - 2>&1 |
    awk -v dur="$dur" -v m="$margem" '
      /silence_start/ { s=$NF; if (s < 0) s = 0 }
      /silence_end/   { split($0, a, "silence_end: "); split(a[2], b, " "); e=b[1]; ini[++n]=s; fim[n]=e }
      END {
        pos = 0
        for (i = 1; i <= n; i++) {
          a1 = ini[i] + m; b1 = fim[i] - m
          if (b1 - a1 <= 0) continue
          if (a1 - pos > 0.05) printf "%.3f %.3f\n", pos, a1
          pos = b1
        }
        if (dur - pos > 0.05) printf "%.3f %.3f\n", pos, dur
      }')
  [ -n "$trechos" ] || erro "não sobrou nenhum trecho com som (limiar alto demais?)"
  local qtd total expr=""
  qtd=$(echo "$trechos" | wc -l)
  total=$(echo "$trechos" | awk '{t += $2 - $1} END {printf "%.1f", t}')
  if [ "$qtd" -le 1 ] && awk -v t="$total" -v d="$dur" 'BEGIN{exit !(t > d - 0.3)}'; then
    info "nenhuma pausa encontrada — nada a cortar"; return 0
  fi
  while read -r a b; do expr+="between(t,$a,$b)+"; done <<< "$trechos"; expr=${expr%+}
  { echo "# trechos mantidos (s) de $(basename "$ent") — limiar ${lim} dB, mínimo ${min} s, margem ${margem} s"; echo "$trechos"; } > "$lista"
  info "$qtd trechos, $(printf '%.1f' "$dur") s → ${total} s; codificando na GPU…"
  ffmpeg -hide_banner -loglevel error -stats -y -vaapi_device "$GPU" -i "$ent" \
    -vf "select='$expr',setpts=N/FRAME_RATE/TB,format=nv12,hwupload" \
    -af "aselect='$expr',asetpts=N/SR/TB" \
    -c:v h264_vaapi -qp 20 -c:a aac -b:a 192k -movflags +faststart "$saida"
  info "pronto: $saida (lista de cortes: $(basename "$lista"))"
}

# ---------------------------------------------------------------------------------------------------------------
cmd_exportar() {
  local ent=${1:?uso: tiktok exportar <vídeo> [saída]} saida=${2:-}
  precisa "$ent"
  if [ -z "$saida" ]; then   # dentro de uma pasta de vídeo → export/ dela; senão, ao lado do arquivo
    local d; d=$(dirname "$(readlink -f "$ent")")
    while [ "$d" != / ] && ! { [ -f "$d/notas.md" ] && [ -d "$d/export" ]; }; do d=$(dirname "$d"); done
    if [ "$d" != / ]; then saida="$d/export/$(basename "${ent%.*}")_tiktok.mp4"
    else saida="${ent%.*}_tiktok.mp4"; fi
  fi
  local af="anull"
  if tem_audio "$ent"; then
    info "medindo o áudio (passada 1/2)…"
    local j il itp ilra ith off
    j=$(ffmpeg -hide_banner -nostats -i "$ent" -map 0:a:0 \
      -af "loudnorm=I=$ALVO_LUFS:TP=$ALVO_TP:LRA=$ALVO_LRA:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
    val() { echo "$j" | sed -n "s/.*\"$1\" : \"\([^\"]*\)\".*/\1/p"; }
    il=$(val input_i); itp=$(val input_tp); ilra=$(val input_lra); ith=$(val input_thresh); off=$(val target_offset)
    [ -n "$il" ] || erro "não consegui medir o áudio"
    info "entrada: ${il} LUFS, pico ${itp} dBTP → alvo ${ALVO_LUFS} LUFS"
    af="loudnorm=I=$ALVO_LUFS:TP=$ALVO_TP:LRA=$ALVO_LRA:measured_I=$il:measured_TP=$itp:measured_LRA=$ilra:measured_thresh=$ith:offset=$off:linear=true,aresample=48000"
  fi
  info "codificando 1080×1920 na GPU (passada 2/2)…"
  local amap=(); tem_audio "$ent" && amap=(-map 0:a:0 -af "$af" -c:a aac -b:a 192k -ar 48000)
  ffmpeg -hide_banner -loglevel error -stats -y \
    -hwaccel vaapi -hwaccel_device "$GPU" -hwaccel_output_format vaapi -i "$ent" \
    -map 0:v:0 -vf "scale_vaapi=w=1080:h=1920:force_original_aspect_ratio=decrease:force_divisible_by=2:format=nv12,pad_vaapi=w=1080:h=1920:x=-1:y=-1" \
    -c:v h264_vaapi -profile:v high -rc_mode VBR -b:v 12M -maxrate 16M -g 60 \
    "${amap[@]}" -movflags +faststart "$saida"
  # conferência final
  local v a l
  v=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate -of csv=p=0 "$saida")
  info "vídeo: $v"
  if tem_audio "$saida"; then
    l=$(ffmpeg -hide_banner -nostats -i "$saida" -map 0:a:0 -af ebur128=peak=true -f null - 2>&1 | awk '/Integrated loudness/{f=1} f&&/I:/{print $2; exit}')
    info "áudio final: ${l} LUFS (alvo ${ALVO_LUFS})"
  fi
  info "pronto: $saida ($(du -h "$saida" | cut -f1))"
}

# ---------------------------------------------------------------------------------------------------------------
cmd_limpar() {
  local dias=30 apagar=0
  for a in "$@"; do case "$a" in --apagar) apagar=1 ;; *[!0-9]*) erro "uso: tiktok limpar [dias] [--apagar]" ;; *) dias=$a ;; esac; done
  local alvos=()
  while IFS= read -r -d '' p; do alvos+=("$p"); done < <(find "$RAIZ" -mindepth 2 -maxdepth 2 -type d -name proxies -mtime +"$dias" -print0 2>/dev/null)
  for c in "$HOME/.cache/kdenlive" "$HOME/.cache/kdenlive-thumbs"; do
    [ -d "$c" ] && while IFS= read -r -d '' p; do alvos+=("$p"); done < <(find "$c" -mindepth 1 -maxdepth 1 -mtime +"$dias" -print0)
  done
  [ ${#alvos[@]} -gt 0 ] || { info "nada com mais de $dias dias para limpar"; return; }
  du -sch "${alvos[@]}" | sed 's/^/  /'
  if [ "$apagar" = 1 ]; then
    for p in "${alvos[@]}"; do
      if [ "$(basename "$p")" = proxies ]; then find "$p" -mindepth 1 -delete; else rm -rf -- "$p"; fi
    done
    info "apagado (só proxies e cache; brutos, projetos e exports não são tocados)"
  else
    info "isso é só a lista. Para apagar: tiktok limpar $dias --apagar"
  fi
}

case "${1:-}" in
  novo) shift; cmd_novo "$@" ;;
  importar) shift; cmd_importar "$@" ;;
  silencios|silêncios) shift; cmd_silencios "$@" ;;
  exportar) shift; cmd_exportar "$@" ;;
  limpar) shift; cmd_limpar "$@" ;;
  onde) pasta_atual ;;
  *) sed -n '2,12p' "$(readlink -f "$0")" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
