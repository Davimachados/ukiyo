#!/usr/bin/env bash
# Captura os insumos do vídeo promocional (telas dos temas e janelas de demonstração) — tudo na área de trabalho 4.
# Privacidade: só as janelas abertas por este script (identificadas pelo PID) vão para a área 4; as do usuário não
# são movidas. Antes de rodar, deixe a área 4 VAZIA e feche notificações. No fim, volta ao tema e à área 1.
# Uso: producao/promo/capturar.sh <pasta-de-saida> <pasta-de-um-video-do-henshu>
#   (o vídeo do Henshū deve ter projeto.json e um export vertical em export/*_vertical.mp4)
set -euo pipefail
PROJ=$(cd "$(dirname "$0")/../.." && pwd); KW="$PROJ/producao/promo/kw.py"
OUT=${1:?pasta de saída}; DEMO=${2:?pasta de um vídeo do Henshū}; mkdir -p "$OUT"
EST="${XDG_STATE_HOME:-$HOME/.local/state}/ukiyo"; ORIG=$(cat "$EST/modo" 2>/dev/null || echo claro)
RC=$(mktemp); trap 'rm -f "$RC"' EXIT
printf 'PS1="\\[\\e[38;5;179m\\]ukiyo\\[\\e[0m\\] \\w \\$ "\nPATH="$HOME/.local/bin:$PATH"\ncd %q\nclear\ntiktok | head -8\necho\nls --color=always\n' "$PROJ" > "$RC"

# 1) telas limpas dos cinco temas
"$KW" desk 3; sleep 1.5
for t in claro escuro marys neontokyo touge; do
  "$PROJ/modos/trocar-tema.sh" "$t" --esperar >/dev/null; sleep 4; spectacle -b -n -f -o "$OUT/desk-$t.png"; sleep 1.3
done
"$KW" desk 0

# 2) janelas de demonstração (estacionadas na área 3 até a vez delas)
(setsid "$PROJ/editor/henshu.sh" "$DEMO" >/dev/null 2>&1 &)
(setsid dolphin --new-window "$PROJ/themes" >/dev/null 2>&1 &)
(setsid konsole --separate --workdir "$PROJ" -e bash --rcfile "$RC" -i >/dev/null 2>&1 &)
(setsid plasmawindowed org.ukiyo.tela >/dev/null 2>&1 &)
KDEN=$(ls "$DEMO"/*.kdenlive 2>/dev/null | head -1 || true)
[ -n "$KDEN" ] && (setsid kdenlive "$KDEN" >/dev/null 2>&1 &)
for i in $(seq 1 40); do sleep 1; [ "$i" -lt 6 ] && continue; [ -e /tmp/kdenlivelock ] || break; done; sleep 4
H=$(pgrep -nf "henshu.app $DEMO"); D=$(pgrep -nf "dolphin --new-window"); K=$(pgrep -of "konsole --separate")
T=$(pgrep -nx plasmawindowed); KD=$(pgrep -nx kdenlive || true)
"$KW" arranjar "{\"$H\":[2],\"$D\":[2],\"$K\":[2],\"$T\":[2]${KD:+,\"$KD\":[2]}}" >/dev/null

conj() {   # nome tema json-ida json-volta
  "$PROJ/modos/trocar-tema.sh" "$2" --esperar >/dev/null; "$KW" arranjar "$3" >/dev/null
  "$KW" desk 3; sleep 3.5; spectacle -b -n -f -o "$OUT/$1-$2.png"; sleep 1.3; "$KW" desk 0; "$KW" arranjar "$4" >/dev/null
}
J="{\"$D\":[3,40,60,780,470],\"$K\":[3,40,560,780,440],\"$H\":[3,860,60,1030,940]}"; V="{\"$D\":[2],\"$K\":[2],\"$H\":[2]}"
for t in claro marys neontokyo; do conj janelas "$t" "$J" "$V"; done
[ -n "$KD" ] && conj kdenlive escuro "{\"$KD\":[3,0,30,1920,1010]}" "{\"$KD\":[2]}"
for t in touge claro; do conj tela "$t" "{\"$T\":[3,730,200,460,660]}" "{\"$T\":[2]}"; done

# 3) fecha só o que abriu, copia o vídeo vertical e restaura o tema
kill "$H" "$D" "$K" "$T" 2>/dev/null || true
[ -n "$KD" ] && { kill -9 "$KD" 2>/dev/null || true; rm -f /tmp/kdenlivelock; }
cp "$(ls "$DEMO"/export/*_vertical.mp4 | head -1)" "$OUT/henshu-vertical.mp4"
"$PROJ/modos/trocar-tema.sh" "$ORIG" >/dev/null
echo "Insumos em $OUT — confira as imagens antes de usar."
