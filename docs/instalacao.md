# Instalação do Ukiyo 浮世

Testado em **Debian 13 (trixie)** com **KDE Plasma 6.3 em Wayland** e GPU Intel (driver VA-API `iHD`).
Cada etapa é **independente, idempotente e reversível**: os scripts fazem backup em `backups/` antes de mudar
qualquer configuração e têm um par `restaurar-*`. Nenhum script roda `sudo` sozinho; os dois que precisam de root
avisam e você os executa.

> Recomendo ler cada script antes de rodar e aplicar uma etapa por vez, conferindo o resultado.

## 1. Pacotes do Debian

```bash
sudo apt install git curl ffmpeg mediainfo vainfo intel-media-va-driver \
  fonts-dotgothic16 fonts-noto-core fonts-noto-cjk \
  python3-venv python3-pyside6.qtwidgets python3-pyside6.qtmultimedia python3-pyside6.qtmultimediawidgets \
  kdenlive obs-studio audacity
```

- `fonts-dotgothic16` é a fonte pixel dos títulos e rótulos.
- `python3-pyside6.*` só é necessário para o editor Henshū; `kdenlive`, `obs-studio` e `audacity` são opcionais.
- Confira a codificação na GPU com `vainfo` (procure `VAEntrypointEncSliceLP` em H.264) ou com `scripts/va-probe.py`.

## 2. Clonar e preparar o ambiente Python

```bash
git clone https://github.com/Davimachados/ukiyo.git ~/ukiyo && cd ~/ukiyo
scripts/preparar-ambiente.sh   # cria .venv com Pillow, NumPy e faster-whisper (requirements.txt)
```

O repositório pode ficar em qualquer pasta: os scripts descobrem o próprio caminho.

## 3. Visual (tema Washi + os outros quatro)

| Ordem | Comando | O que faz | Desfazer |
|---|---|---|---|
| 1 | `themes/washi/scripts/aplicar-v1-desktop.sh` | papel de parede, esquema de cores, **barra superior + dock** (substitui o layout dos painéis), áreas de trabalho 一二三四, efeitos leves | `restaurar-v1-desktop.sh` |
| 2 | `themes/washi/scripts/aplicar-v2v3-janelas-icones.sh` | títulos de janela em DotGothic16, ícones pixel e cursor pixel | `restaurar-v2v3-janelas-icones.sh` |
| 3 | `themes/washi/scripts/aplicar-v2b-decoracao.sh` | decoração de janelas Washi Pixel (Aurorae) | `restaurar-v2b-decoracao.sh` |
| 4 | `modos/instalar-temas.sh` | pré-carrega os cinco temas e instala o autostart que os mantém atualizados no login | apagar `~/.config/autostart/ukiyo-temas.desktop` |
| 5 | `modos/modo-claro.sh` (ou `-escuro`, `-marys`, `-neontokyo`, `-touge`) | aplica um tema | trocar por outro |
| 6 | `themes/washi/scripts/aplicar-v4-producao.sh` | variante escura **Sumi** só no Konsole, no Kdenlive e no Audacity | `restaurar-v4-producao.sh` |
| 7 | `themes/washi/scripts/aplicar-v5-bloqueio.sh` | tela de bloqueio | `restaurar-v5-bloqueio.sh` |
| 8 | `sudo themes/washi/scripts/aplicar-v5-login.sh` | tela de login (SDDM); vale a partir do próximo logout | `sudo …/restaurar-v5-login.sh` |
| 9 | `themes/washi/scripts/instalar-widget-tela.sh` | widget **Tela** (brilho, saturação por perfil ICC, botões de tema); reinicia o painel | `remover-widget-tela.sh` |
| 10 | `widgets/spotify/instalar-widget.sh` | widget do Spotify (opcional; o app é instalado por `sudo bash scripts/instalar-spotify.sh`, com o repositório oficial) | `widgets/spotify/remover-widget.sh` |

A fonte nova dos títulos só aparece no KWin depois de um novo login. Para ver a tela de login antes de aplicá-la,
use `themes/washi/scripts/previa-login.sh`, que roda o modo de teste do SDDM sem mudar nada.

## 4. Produção de vídeo

```bash
scripts/instalar-comandos.sh   # liga tiktok, henshu e henshu-transcrever em ~/.local/bin + atalho do Henshū no menu
scripts/instalar-obs-base.sh   # (opcional) perfil e cenas verticais do OBS com VA-API
```

- `tiktok novo <nome>` cria `~/Vídeos/TikTok/<data>_<nome>/` (a pasta segue o diretório de vídeos do seu idioma).
- O Kdenlive pode usar proxies na GPU: em *Configurações → Configurar o Kdenlive → Projeto*, escolha o perfil de
  proxy **x264-vaapi-scale** e o perfil de projeto `vertical_hd_30`.

## 5. Henshū 編集 com IA (opcional)

O chat usa as ferramentas de linha de comando dos agentes, com o seu próprio login:

- **Claude Code**: instale pelo site oficial e faça login (`claude`).
- **Codex**: instale pelo site oficial e faça login (`codex login`).

Sem nenhum dos dois, o Henshū continua funcionando como editor (prévia, transcrição, legendas e exportação).
A primeira transcrição baixa o modelo `small` do faster-whisper (~460 MB, em `~/.cache/huggingface`).

## Desinstalar

Rode os scripts `restaurar-*`/`remover-*` na ordem inversa, `scripts/instalar-comandos.sh --remover` e apague a pasta
do repositório. Os backups de cada etapa ficam em `backups/` até você apagá-los.
