#!/usr/bin/env bash
# Troca rápida de tema: só APLICA valores (os recursos já estão pré-carregados por instalar-temas.sh).
# Troca papel de parede, ícones, decoração e fundo do bloqueio. As CORES DOS APPS ficam fixas.
# Uso: trocar-tema.sh <id> [--esperar]   (ids em modos/temas.conf)
#   - ordem sem fila: papel de parede → ícones → decoração → fundo do bloqueio; chamadas ao painel e ao KWin
#     não bloqueiam (o KDE conclui o redesenho em segundo plano, ≈1–2 s)
#   - ícones por chave com notificação (≈35 ms; o plasma-changeicons levava ≈2 s)
#   - decoração recarregada uma única vez; nenhum arquivo de tema é regenerado ou recopiado
#   - registra o estado anterior em ~/.local/state/ukiyo/historico-temas.log
set -euo pipefail
PROJ=$(cd "$(dirname "$0")/.." && pwd); SH="$HOME/.local/share"; EST="$HOME/.local/state/ukiyo"; mkdir -p "$EST"
LISTA=$(grep -v '^#' "$PROJ/modos/temas.conf" | grep -v '^$' | cut -d'|' -f1 | paste -sd'|')
ALVO=${1:?uso: trocar-tema.sh $LISTA}
ESPERAR=0; [ "${2:-}" = "--esperar" ] && ESPERAR=1   # --esperar: só retorna quando o KDE aceitou tudo

# valores do tema vêm do registro único modos/temas.conf
LINHA=$(grep -v '^#' "$PROJ/modos/temas.conf" | awk -F'|' -v id="$ALVO" '$1 == id' | head -1)
[ -n "$LINHA" ] || { echo "tema desconhecido: $ALVO (disponíveis: $LISTA)"; exit 2; }
IFS='|' read -r _ _ ESQ ICO DECO_NOME PACOTE _ _ _ <<< "$LINHA"
FUNDO=$SH/wallpapers/$PACOTE; DECO=__aurorae__svg__$DECO_NOME; BLOQ=$FUNDO

# recursos ausentes? pré-carrega (só na primeira vez)
if [ ! -d "$SH/icons/$ICO" ] || [ ! -d "$FUNDO" ] || [ ! -d "$SH/aurorae/themes/${DECO#__aurorae__svg__}" ]; then
  "$PROJ/modos/instalar-temas.sh" >/dev/null
fi

# histórico leve (uma linha) em vez de backup completo a cada troca
echo "$(date '+%F %T') $(cat "$EST/modo" 2>/dev/null || echo ?) -> $ALVO | esquema=$(kreadconfig6 --file kdeglobals --group General --key ColorScheme) icones=$(kreadconfig6 --file kdeglobals --group Icons --key Theme) deco=$(kreadconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme)" >> "$EST/historico-temas.log"

# aplicar — ordem pensada para não enfileirar:
# 1) papel de parede enquanto o painel está ocioso (o esquema de cores faz o painel redesenhar tudo)
plasma-apply-wallpaperimage "$FUNDO" >/dev/null 2>&1 < /dev/null &             # em paralelo
# 2) ícones por chave com notificação (≈35 ms)
kwriteconfig6 --notify --file kdeglobals --group Icons --key Theme "$ICO"
dbus-send --session --type=signal /KIconLoader org.kde.KIconLoader.iconChanged int32:0
# 3) decoração: grava e pede a recarga SEM esperar resposta (o KWin processa em segundo plano)
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme "$DECO"
dbus-send --session --type=method_call --dest=org.kde.KWin /KWin org.kde.KWin.reconfigure
# 4) fundo do bloqueio (só grava; vale no próximo bloqueio)
kwriteconfig6 --file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General --key Image "$BLOQ"
kwriteconfig6 --file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General --key PreviewImage "$BLOQ"
# cores dos apps NÃO são trocadas (pedido do usuário: evita o redesenho geral do KDE, que trava ~2 s)
[ "$ESPERAR" = 1 ] && wait || disown -a
echo "$ALVO" > "$EST/modo"
echo "Tema aplicado: $ALVO"
