#!/usr/bin/env bash
# Executado pelo próprio usuário: sudo bash ~/ukiyo/scripts/instalar-spotify.sh
# Repositório oficial, chave restrita por Signed-By e backup antes de alterar apt.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo 'Execute no seu terminal: sudo bash ~/ukiyo/scripts/instalar-spotify.sh'; exit 1; }
[ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != root ] || { echo 'Use sudo a partir do seu usuário comum (não como root direto).'; exit 1; }
PROJ=$(cd "$(dirname "$0")/.." && pwd)
B="$PROJ/backups/$(date +%F_%H%M%S)-spotify-apt"
mkdir -p "$B"
for f in /etc/apt/sources.list.d/spotify.sources /etc/apt/sources.list.d/spotify.list /etc/apt/keyrings/ukiyo-spotify.gpg; do
  if [ -e "$f" ]; then cp -a "$f" "$B/$(basename "$f")"; else touch "$B/$(basename "$f").ausente"; fi
done
dpkg-query -W -f='${Package}\t${Version}\n' > "$B/pacotes-antes.txt"
for bin in curl gpg; do command -v "$bin" >/dev/null || { echo "Falta $bin; instale-o antes."; exit 1; }; done
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
curl -fLsS --proto '=https' --tlsv1.2 https://download.spotify.com/debian/pubkey_5384CE82BA52C83A.asc -o "$TMP/spotify.asc"
FINGERPRINT=$(gpg --batch --show-keys --with-colons "$TMP/spotify.asc" | awk -F: '$1=="fpr" {print $10; exit}')
[[ "$FINGERPRINT" = *5384CE82BA52C83A ]] || { echo 'A chave oficial mudou: revisar antes de continuar.'; exit 1; }
gpg --batch --dearmor --output "$TMP/spotify.gpg" "$TMP/spotify.asc"
install -d -m 755 /etc/apt/keyrings
install -m 644 "$TMP/spotify.gpg" /etc/apt/keyrings/ukiyo-spotify.gpg
# Uma fonte antiga do Spotify é substituída somente após backup.
if [ -e /etc/apt/sources.list.d/spotify.list ]; then mv /etc/apt/sources.list.d/spotify.list "$B/spotify.list.desativada"; fi
cat > /etc/apt/sources.list.d/spotify.sources <<'EOF'
# >>> ukiyo: spotify >>>
Types: deb
URIs: https://repository.spotify.com
Suites: stable
Components: non-free
Architectures: amd64
Signed-By: /etc/apt/keyrings/ukiyo-spotify.gpg
# <<< ukiyo: spotify <<<
EOF
apt-get update
apt-get install spotify-client
chown -R "$SUDO_USER:$(id -gn "$SUDO_USER")" "$B"
echo "Spotify instalado. Backup: $B"
echo 'Abra Spotify pelo menu e faça login na própria janela do aplicativo.'
