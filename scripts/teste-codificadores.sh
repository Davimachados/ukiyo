#!/usr/bin/env bash
# Testa codificadores de vídeo (hardware e CPU) com 10 s sintéticos em 1080x1920@30.
# Para cada um: codifica, decodifica de volta e conta quadros/erros.
# Uso: scripts/teste-codificadores.sh [pasta_saida]
set -u
T=${1:-$(mktemp -d)}; mkdir -p "$T"
DUR=10; FPS=30; ESPERADO=$((DUR*FPS))
SRC=(-f lavfi -i "testsrc2=size=1080x1920:rate=$FPS:duration=$DUR")
VA=(-vaapi_device /dev/dri/renderD128)

run() {
  local name=$1; shift; local out="$T/$name.mkv"
  if ffmpeg -hide_banner -nostdin -benchmark -y "$@" "$out" >"$T/$name.log" 2>&1 && [ -s "$out" ]; then
    local bench frames dec
    bench=$(grep -o 'bench: utime=.*' "$T/$name.log" | tail -1 | sed 's/bench: //')
    frames=$(ffprobe -v error -count_frames -select_streams v:0 \
      -show_entries stream=codec_name,profile,nb_read_frames -of csv=p=0 "$out")
    dec=$(ffmpeg -v error -nostdin -i "$out" -f null - 2>&1 | wc -l)
    printf '%-15s OK     %-28s quadros/esperado=%s/%s  %s  %sKB  erros_decodificacao=%s\n' \
      "$name" "${frames%,*}" "${frames##*,}" "$ESPERADO" "$bench" $(( $(stat -c%s "$out")/1024 )) "$dec"
  else
    printf '%-15s FALHA  %s\n' "$name" "$(grep -iE 'error|failed|not supported|unsupported' "$T/$name.log" | head -2 | tr '\n' ' ' | cut -c1-220)"
  fi
}

run h264_vaapi     "${VA[@]}" "${SRC[@]}" -vf format=nv12,hwupload -c:v h264_vaapi -profile:v high -qp 20
run hevc_vaapi     "${VA[@]}" "${SRC[@]}" -vf format=nv12,hwupload -c:v hevc_vaapi -qp 22
run hevc10_vaapi   "${VA[@]}" "${SRC[@]}" -vf format=p010,hwupload -c:v hevc_vaapi -profile:v main10 -qp 22
run vp9_vaapi      "${VA[@]}" "${SRC[@]}" -vf format=nv12,hwupload -c:v vp9_vaapi -global_quality 80
run av1_vaapi      "${VA[@]}" "${SRC[@]}" -vf format=nv12,hwupload -c:v av1_vaapi
run h264_qsv       -init_hw_device qsv=hw -filter_hw_device hw "${SRC[@]}" -vf format=nv12,hwupload=extra_hw_frames=64 -c:v h264_qsv -global_quality 22
run x264_veryfast  "${SRC[@]}" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p
run x264_ultrafast "${SRC[@]}" -c:v libx264 -preset ultrafast -crf 20 -pix_fmt yuv420p
echo "Arquivos em: $T"
