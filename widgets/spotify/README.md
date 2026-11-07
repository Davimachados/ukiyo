# Spotify · Ukiyo

Widget Plasma 6 para a barra superior: miniatura da capa, título e anterior/tocar/pausar/próxima.
Clicar na capa ou no título abre os controles completos e o slider de volume.
A aparência usa o tema do KDE; DotGothic16 somente no título do popup.

## Instalação do aplicativo

O usuário executa no próprio terminal (o agente nunca executa sudo):

```bash
sudo bash ~/ukiyo/scripts/instalar-spotify.sh
```

Fonte verificada em 2026-11-07: https://www.spotify.com/us/download/linux/
Chave oficial: E1096BCBFF6D418796DE78515384CE82BA52C83A.
Chave vinculada somente a essa fonte por Signed-By em `/etc/apt/sources.list.d/spotify.sources`.
Backup automático em `backups/<data>-spotify-apt/` antes das alterações no APT.

## Ativação do widget (somente após aprovação visual)

```bash
~/ukiyo/widgets/spotify/instalar-widget.sh
```

A instalação é local, idempotente e não reinicia o painel. O widget é acrescentado à barra superior.
Se uma versão já estiver carregada e for atualizada, o Plasma pode exigir novo login para reler o QML.
Prévia funcional em `preview/widget-demo.png`, com faixa fictícia e wallpaper usado como capa ilustrativa.
O aplicativo real precisa estar aberto e autenticado para mostrar a música.

## Controles e volume

- Metadados e transporte: MPRIS do próprio KDE; seleciona exclusivamente a identidade Spotify.
- Volume: `pactl` sobre as saídas do Spotify. Não altera alto-falantes, volume geral ou microfone.
- O slider fica indisponível até existir uma saída de áudio do Spotify, normalmente após iniciar uma faixa.
- Nenhuma reprodução, alteração de volume ou abertura de aplicativo ocorre ao carregar o widget.
- Consulta volume a cada dois segundos apenas com o popup aberto; debounce de 120 ms no slider.
- Se a capa estiver ausente ou falhar, usa ícone de música.
- Sem API externa, credenciais, playerctl ou dependências Python adicionais.

## Validação

Três testes de seleção de streams/limites de volume passaram:

```bash
python3 -m unittest discover -s widgets/spotify/tests -v
```

O pacote carregou em `plasmawindowed` offscreen em sessão D-Bus isolada.
Um player MPRIS fictício confirmou metadados, capa, Next e PlayPause sem tocar áudio.
Sem validação de reprodução com a conta real do usuário até ele abrir o Spotify e escolher uma música.
Os arquivos `tests/mock-mpris.py` e `tests/preparar-previa.py` são exclusivamente para testes isolados.

## Reversão

Widget (sem desinstalar o Spotify e sem alterar volume):

```bash
~/ukiyo/widgets/spotify/remover-widget.sh
```

Spotify: o usuário pode executar `sudo apt-get remove spotify-client`.
Para desfazer a fonte APT, restaurar `spotify.sources` e `ukiyo-spotify.gpg` do backup `*-spotify-apt`
ou removê-los se o backup contiver os marcadores `.ausente`; restaurar também `spotify.list` caso existisse.
Não remover outros repositórios, chaves ou dados da conta.
