# Registro de mudanças e como desfazer

Cada alteração no sistema entra aqui: o que mudou, onde está o backup e como reverter.
Backups ficam em `backups/<data>-<etapa>/` (ignorado pelo git).

## 2026-11-06 — Etapa 1: PATH

**O que mudou:** bloco anexado ao fim de `~/.bashrc`, entre os marcadores
`# >>> ukiyo: PATH >>>` e `# <<< ukiyo: PATH <<<`. Ele só adiciona
`~/.local/bin` ao PATH se a pasta existir e se ela ainda não estiver no PATH; carregar várias vezes não duplica nada.

**Backup:** `backups/2026-11-06-etapa1/bashrc.orig` e `profile.orig` (`~/.profile` não foi alterado).

**Verificação:** `bash -n ~/.bashrc` OK; `command -v claude` → `~/.local/bin/claude`; uma única ocorrência no PATH em shell interativo e de login.

**Desfazer (qualquer opção):**

```bash
# 1) restaurar o backup
cp ~/ukiyo/backups/2026-11-06-etapa1/bashrc.orig ~/.bashrc
# 2) ou remover só o bloco
sed -i '/# >>> ukiyo: PATH >>>/,/# <<< ukiyo: PATH <<</d' ~/.bashrc
```

Observação: após o próximo logout/login, o `~/.profile` padrão também adiciona `~/.local/bin`; o bloco do `.bashrc` não duplica.

## 2026-11-06 — Etapa 2: pacotes

**O que mudou:** instalados via apt (comando executado pelo usuário com sudo):
`obs-studio kdenlive audacity ffmpeg vainfo v4l-utils intel-gpu-tools` + 170 dependências. Nada removido.

**Backup:** `backups/2026-11-06-etapa2/dpkg-selections.antes.txt`, `apt-manual.antes.txt`, `dpkg-selections.depois.txt`.

**Desfazer:**
```bash
sudo apt remove obs-studio kdenlive audacity ffmpeg vainfo v4l-utils intel-gpu-tools
sudo apt autoremove   # revise a lista antes de confirmar
```

## 2026-11-06 — Etapa 2: OBS base "TikTok Vertical"

**O que mudou:** criado `~/.config/obs-studio/` (não existia) por `scripts/instalar-obs-base.sh` a partir de `config/obs/`:
perfil `TikTok_Vertical` (1080×1920, 30 fps, H.264 VAAPI CQP 20, MKV + remux MP4, AAC 192k, gravações em
`~/Vídeos/TikTok/brutos`) e coleção de cenas `TikTok_Vertical` (3 cenas). Webcam com `auto_reset=false`
(backup da cena anterior à correção: `backups/2026-11-06-etapa2/TikTok_Vertical.json.antes-autoreset`).
Criadas as pastas `~/Vídeos/TikTok/{brutos,projetos,exports,testes}`.

**Backup:** não havia configuração anterior. O script faz backup completo em `backups/<data>-obs/` sempre que roda
sobre uma configuração existente.

**Desfazer:**
```bash
# restaurar um backup específico
rm -rf ~/.config/obs-studio && cp -a ~/ukiyo/backups/<data>-obs/obs-studio ~/.config/
# ou voltar ao OBS "de fábrica"
rm -rf ~/.config/obs-studio
```

## 2026-11-06 — Etapa 2: ganho do microfone

**O que mudou:** volume da fonte `alsa_input…HiFi__Mic1__source` (microfone digital) de 100% para 46%
(= Base Volume, ganho nominal 0 dB). Persistido pelo WirePlumber em `~/.local/state/wireplumber/default-routes`.

**Motivo:** em 100% o sinal saturava (centenas de amostras cortadas por segundo de fala).

**Backup:** `backups/2026-11-06-etapa2/mic-volume.antes.txt`, `backups/2026-11-06-etapa2/wireplumber-state.antes/`.

**Desfazer:**
```bash
pactl set-source-volume alsa_input.pci-0000_00_1f.3-platform-skl_hda_dsp_generic.HiFi__Mic1__source 100%
```

## 2026-11-06 — Etapa 3 (visual): Washi V1 — desktop

**Pacote:** `fonts-dotgothic16` (instalado pelo usuário com sudo). Desfazer: `sudo apt remove fonts-dotgothic16`.

**O que mudou** (`themes/washi/scripts/aplicar-v1-desktop.sh`):
- Esquema de cores **Washi** (antes: BreezeLight); estilo Plasma `default` (antes: `breeze-dark`, via padrão do look-and-feel Debian).
- Painéis: o painel inferior original foi substituído por **barra superior** (30 px, opaca: lançador com ícone torii e rótulo スタジオ,
  menu global, áreas de trabalho, bandeja, relógio DotGothic16) e **dock** inferior centralizada (flutuante, opaca, "esquivar janelas").
- Áreas de trabalho: 1 → 4, nomeadas 一 二 三 四.
- Papel de parede **Washi — Entardecer**.
- Efeitos: `blurEnabled=false`, `contrastEnabled=false` (kwinrc), `AnimationDurationFactor=0.5` (kdeglobals).
- Arquivos novos: `~/.local/share/color-schemes/{Washi,Sumi}.colors`, `~/.local/share/wallpapers/Washi/`,
  `~/.local/share/icons/hicolor/scalable/apps/washi-{lancador,sakura}.svg`, `~/.config/plasmarc`.

**Backup:** `backups/2026-11-06_204919-washi-v1/` (estado imediatamente anterior, com `SHA256SUMS`) e o backup geral
`backups/2026-11-06-etapa3-visual/`.

**Desfazer:**
```bash
~/ukiyo/themes/washi/scripts/restaurar-v1-desktop.sh            # volta ao estado anterior
~/ukiyo/themes/washi/scripts/restaurar-v1-desktop.sh --limpar   # idem + remove os arquivos instalados
```

## 2026-11-06 — Etapa 3 (visual): Washi V2 + V3 — janelas, ícones e cursor

**O que mudou** (`themes/washi/scripts/aplicar-v2v3-janelas-icones.sh`; layout dos painéis intacto, checksum conferido):
- **Janelas (V2):** decoração continua Breeze, recolorida pelo esquema Washi. `breezerc [Common]`: `ShadowSize=ShadowSmall`,
  `OutlineIntensity=OutlineHigh` (arquivo novo). Título: `kdeglobals [WM] activeFont=DotGothic16 12 pt`.
  ⚠ O KWin foi iniciado antes da instalação da fonte; os títulos só passam a usar DotGothic16 **após o próximo login**.
- **Ícones (V3):** tema `washi-pixel` (`~/.local/share/icons/washi-pixel`, herda `breeze,hicolor`): Dolphin, Firefox, Konsole,
  OBS, Kdenlive, Audacity, Configurações, lançador, sakura e pastas (início, área de trabalho, documentos, downloads,
  música, imagens, vídeos, público, modelos, lixeira). Demais ícones: Breeze.
- **Cursor (V3):** tema `washi-cursor` em `~/.icons/washi-cursor` (a libXcursor do Debian não procura em `~/.local/share/icons`;
  `~/.icons` não existia). Tamanho 24 → **32** (2× a grade de 16 px; mais visível em gravações de tela). Fallback: breeze_cursors.
- GTK/Firefox sincronizados pelo módulo `gtkconfig` do kded (tema e tamanho do cursor, ícones).

**Backups:** `backups/2026-11-06_210010-washi-v2v3/` (estado **original**, usado pela restauração) e
`backups/2026-11-06_210050-washi-v2v3/` (intermediário: ícones já trocados, criado na reexecução).

**Desfazer:**
```bash
~/ukiyo/themes/washi/scripts/restaurar-v2v3-janelas-icones.sh            # volta Breeze/breeze_cursors 24/fonte padrão
~/ukiyo/themes/washi/scripts/restaurar-v2v3-janelas-icones.sh --limpar   # idem + remove os temas instalados
```

## 2026-11-06 — Refinamento visual: verificação dos títulos, papel de parede v2 (proposto), proposta de decoração

**Sistema:** nenhuma configuração alterada nesta rodada.
- Títulos de janela em DotGothic16 **conferidos** após novo login (KWin reporta `font: DotGothic16,12…`; captura em
  `docs/visual/capturas/titulo-breeze-atual.png`). Menus e textos longos seguem em Noto Sans.

**Papel de parede v2 — aplicado em seguida, a pedido (ver abaixo):**
- v1 preservada: `themes/washi/tools/gerar-papel-de-parede-v1.py`, `themes/washi/wallpaper/entardecer-v1-*.png`
  (idêntica ao papel de parede instalado; SHA-256 1920×1080 `23ab38b7…`).
- v2: `themes/washi/tools/gerar-papel-de-parede.py` → `themes/washi/wallpaper/entardecer-v2-*.png`.
  Céu com faixas lisas (−66% de trocas de cor entre pixels vizinhos), água calma (−58%), reflexo do sol em faixas
  interrompidas; sakura, Fuji, torii e margem idênticos à v1 (0 pixels diferentes).
- Comparação: `themes/washi/preview/comparacao-papel-de-parede.html`.
- Para aplicar: `themes/washi/scripts/trocar-papel-de-parede.sh v2` (instala o pacote separado `Washi-v2`, com backup
  do appletsrc). **Desfazer:** `themes/washi/scripts/trocar-papel-de-parede.sh v1`.

**Proposta de decoração "Washi Pixel" (Aurorae) — só proposta:** `themes/washi/preview/proposta-decoracao.html`
(gerada por `themes/washi/tools/proposta-decoracao.py`).

## 2026-11-06 — Papel de parede v2 aplicado

**O que mudou:** novo pacote `~/.local/share/wallpapers/Washi-v2/` e papel de parede de todas as áreas de trabalho → `Washi-v2`
(`plasma-org.kde.plasma.desktop-appletsrc`, chave `Image=`). O pacote `Washi` (v1) continua instalado. Painéis inalterados.

**Backup:** `backups/2026-11-06_212804-papel-de-parede/` (appletsrc anterior).

**Desfazer:** `~/ukiyo/themes/washi/scripts/trocar-papel-de-parede.sh v1`

## 2026-11-06 — Washi V2b: decoração de janelas "Washi Pixel" (Aurorae, sem sombra)

**O que mudou** (`themes/washi/scripts/aplicar-v2b-decoracao.sh`):
- Tema instalado em `~/.local/share/aurorae/themes/WashiPixel/` (gerado por `themes/washi/tools/gerar-decoracao.py`; a pasta
  `~/.local/share/aurorae` não existia).
- `kwinrc [org.kde.kdecoration2]`: `library=org.kde.kwin.aurorae`, `theme=__aurorae__svg__WashiPixel` (antes: `org.kde.breeze` / `Breeze`).
- Moldura 2 px sumi + 2 px washi2, cantos em degrau, linha sob o título, botões pixel 24 px (12×12 a 2×), ícone do app 16 px,
  sem sombra e sem animação; maximizada sem bordas laterais. Títulos continuam em DotGothic16.
- Botões GTK (`~/.config/gtk-3.0|4.0/assets`) regenerados pelo Plasma.

**Verificado:** janela ativa e inativa, maximizada, ícone nítido (após `ButtonWidthMenu=16`), painéis inalterados.
CPU do KWin em repouso: 0,9% (Breeze) → ~0% (Aurorae). Memória do KWin: ~249 MB → ~370 MB (motor QML do Aurorae).
Limitação: janelas GTK com barra própria continuam com o desenho de botão do Breeze (em sumi); o Firefox desenha a própria barra.

**Backup:** `backups/2026-11-06_213101-washi-v2b/` (kwinrc, gtk-3.0, gtk-4.0, estado anterior).

**Desfazer:**
```bash
~/ukiyo/themes/washi/scripts/restaurar-v2b-decoracao.sh            # volta ao Breeze recolorido
~/ukiyo/themes/washi/scripts/restaurar-v2b-decoracao.sh --limpar   # idem + remove o tema WashiPixel
```

## 2026-11-06 — Washi V4: variante Sumi nos apps de produção

Esquema global (Washi), painéis, Dolphin e decoração **inalterados** (checksums de `kdeglobals`, `kwinrc` e appletsrc conferidos).
OBS e áudio não foram tocados.

**O que mudou** (`themes/washi/scripts/aplicar-v4-producao.sh`):
- **Konsole:** `~/.local/share/konsole/Sumi.profile` + `Sumi.colorscheme` (fundo carvão `#24221F`, texto marfim `#EDE6D6`,
  16 cores ≥ 4,5:1 — ver `themes/washi/konsole/contraste-terminal.txt`; fonte DejaVu Sans Mono 11; cursor âmbar).
  `konsolerc`: `DefaultProfile=Sumi.profile`, `[UiSettings] ColorScheme=Sumi` (barra de ferramentas/abas escuras).
- **Kdenlive:** `kdenliverc [UiSettings] ColorSchemePath=~/.local/share/color-schemes/Sumi.colors` (tema do próprio Kdenlive;
  cores conferidas na captura: fundo `#1E1C1A`, seleção `#B3263B`).
- **Audacity:** `audacity.cfg [GUI] Theme=dark` (tema embutido). Lançador `~/.local/bin/audacity-sumi` + atalho local
  `~/.local/share/applications/audacity.desktop` (prioridade sobre o do sistema; usado pela dock/menu): roda o Audacity com
  `XDG_CONFIG_HOME` "sombra" (`~/.local/share/ukiyo/audacity-xdg`, links para todo o `~/.config`, inclusive
  `audacity`, `pulse`, `dconf`) e `gtk-3.0` escuro (Breeze-Dark), sem alterar `~/.config`.

**Limitações registradas:**
- Audacity 3.7.3 não oferece paleta personalizada utilizável (o tema "custom" depende de um ImageCache gerado por editor de
  temas ausente nas versões de distribuição) → tema **dark** nativo; a parte GTK usa **Breeze-Dark** (cinza-azulado), não a Sumi.
- Sem o lançador, o Audacity misturava tema escuro com GTK claro, deixando o título da janela "Bem-vindo" ilegível
  (texto claro sobre fundo claro) — motivo do lançador.
- Abrir o Audacity por fora do menu/dock (ex.: `audacity` no terminal) não usa o GTK escuro; use `audacity-sumi`.

**Verificação:** capturas `docs/visual/capturas/washi-v4-konsole.png` e `washi-v4-kdenlive.png`; contraste dos papéis Sumi
(menus, campos, seleção, erro, aviso, links) em `themes/washi/preview/contraste-sumi-apps.txt` (todos ≥ 4,5:1).
Captura do Audacity com o lançador **pendente**: a tela bloqueou por inatividade durante o teste →
`themes/washi/scripts/capturar-audacity-v4.sh` (com a tela desbloqueada).
Testes do Audacity usaram um tom sintético; as sessões temporárias não salvas criadas pelos testes foram removidas de
`/var/tmp/audacity-davi/`.

**Backups:** `backups/2026-11-06_213944-washi-v4/` (estado **original**, usado na restauração) e
`backups/2026-11-06_214408-washi-v4/` (intermediário).

**Desfazer** (reverte só as chaves alteradas; demais ajustes dos apps são preservados):
```bash
~/ukiyo/themes/washi/scripts/restaurar-v4-producao.sh
```

## 2026-11-06 — V4 fechada (captura do Audacity) e V5 preparada (NÃO aplicada)

- Captura do Audacity pelo atalho `audacity-sumi`: `docs/visual/capturas/washi-v4-audacity.png` (janela "Bem-vindo"
  escura e legível). Uma captura de tela inteira gerada pelo script continha conteúdo pessoal e foi apagada; o script
  passou a capturar só a janela.
- **V5 preparada, sem aplicar e sem reiniciar o SDDM:**
  - Tema de login `themes/washi/sddm/washi/` (gerado por `themes/washi/tools/gerar-sddm.py` a partir do Breeze; muda só relógio
    DotGothic16, fundo v2 e logo torii). Pré-visualização real: `themes/washi/preview/v5-login-preview.png`.
  - Bloqueio: papel de parede v2. Pré-visualização real (configuração temporária, nada gravado em `~/.config`):
    `themes/washi/preview/v5-bloqueio-preview.png`.
  - Proposta: `themes/washi/preview/proposta-v5.html`.
  - Scripts: `aplicar-v5-bloqueio.sh` / `restaurar-v5-bloqueio.sh` (usuário) e `aplicar-v5-login.sh` /
    `restaurar-v5-login.sh` (sudo; backup automático de `/etc/sddm.conf.d`, `/etc/sddm.conf`, tema, cursor e
    `/var/lib/sddm/.config/kdeglobals`). Emergência documentada nos scripts e na proposta.

## 2026-11-06 — Correções antes da V5 (ícones, Sumi, Audacity, prévia do login)

**Ícones escuros no Konsole/Kdenlive (corrigido):** o tema `washi-pixel` não declarava `FollowsColorScheme=true` (o Breeze
declara), então os ícones herdados do Breeze não eram recoloridos e ficavam `#232629` sobre carvão (1,14:1).
Adicionado em `themes/washi/tools/gerar-tema-icones.py` e em `~/.local/share/icons/washi-pixel/index.theme`.
Medido depois: ícones habilitados 12,8–14:1.

**Desabilitados na Sumi:** `[ColorEffects:Disabled]` da Sumi (`ContrastAmount` 0.65→0.6, `IntensityEffect` 2→0) em
`themes/washi/color-schemes/Sumi.colors` e `~/.local/share/color-schemes/Sumi.colors`. Texto desabilitado 2,65→3,32:1.
Ícones desabilitados (1,74:1 Konsole, 2,53:1 Kdenlive) são desenhados pelo estilo Breeze (cinza + esmaecido) e não são
configuráveis no KF6 (testados `[DisabledIcons]` e `*Icons/DisabledEffect`: sem efeito; chaves removidas).

**Backup:** `backups/2026-11-06_222758-washi-icones-fix/` (`index.theme`, `Sumi.colors.antes`, `konsolerc.antes`, `kdenliverc.antes`).
**Desfazer:** `cp backups/2026-11-06_222758-washi-icones-fix/index.theme ~/.local/share/icons/washi-pixel/` e
`cp backups/2026-11-06_222758-washi-icones-fix/Sumi.colors.antes ~/.local/share/color-schemes/Sumi.colors`.

**Audacity:** interface principal capturada pelo atalho (`docs/visual/capturas/washi-v4b-audacity-principal.png`).
Menu aberto depende de clique: `themes/washi/scripts/capturar-menu-audacity.sh` (captura cronometrada). Sem alterações de áudio.

**Login (prévia b, NÃO aplicada):** `themes/washi/tools/gerar-sddm.py` agora gera `WashiFader.qml` (sem desfoque/ajuste de cor)
e um painel sumi com borda washi atrás do formulário no `Main.qml`; `Login.qml` permanece idêntico ao Breeze.
Prévia: `themes/washi/preview/v5-login-preview-b.png` (capturada sem foco: formulário em fade — não validar contraste por ela).
Prévia interativa: `themes/washi/scripts/previa-login.sh`. SDDM não reiniciado; nada instalado no sistema.

## 2026-11-06 — V5a aplicada: bloqueio de tela com papel de parede v2

**O que mudou:** `~/.config/kscreenlockerrc` (não existia): `[Greeter][Wallpaper][org.kde.image][General] Image/PreviewImage =
~/.local/share/wallpapers/Washi-v2`. Cores do bloqueio já seguem a Washi; relógio na fonte do sistema (limitação registrada).
**Backup:** `backups/2026-11-06_223914-washi-v5-bloqueio/` (marca `kscreenlockerrc.ausente`).
**Desfazer:** `~/ukiyo/themes/washi/scripts/restaurar-v5-bloqueio.sh`

## 2026-11-06 — V5b preparada para aplicar: login com desfoque original do Breeze

Escolha do usuário: variante "a" (desfoque do Breeze, sem painel). `themes/washi/tools/gerar-sddm.py` gera essa variante por
padrão; a variante sem desfoque + painel continua disponível com `--painel`. Tema em `themes/washi/sddm/washi/`:
`Main.qml` = Breeze + só o relógio pixel; `Login.qml` idêntico ao Breeze; fundo v2 e logo torii. Carregamento conferido no
modo de teste (sem erros novos). Instalação pendente de sudo: `sudo ~/ukiyo/themes/washi/scripts/aplicar-v5-login.sh`.

## 2026-11-06 — Widget "Tela Washi" (brilho + saturação) na barra superior

**O que é:** plasmoide `org.ukiyo.tela` (gerado por `themes/washi/tools/gerar-widget-tela.py`, instalado com
`kpackagetool6` em `~/.local/share/plasma/plasmoids/`), na barra superior entre as áreas de trabalho e a bandeja
(`AppletOrder=26;27;28;29;30;52;31;43`). Clique abre o painel; roda do mouse sobre o ícone ajusta o brilho em passos de 5%.
- **Brilho (5–100%):** luz de fundo via `org.kde.ScreenBrightness` (mesma interface do controle de brilho do Plasma).
- **Saturação (30–150%, padrão 100%):** perfil ICC gerado por `themes/washi/tools/gerar-icc-saturacao.py` (matriz sRGB com
  primárias ajustadas; branco preservado) e aplicado pelo KWin com `kscreen-doctor output.eDP-1.iccprofile`. Em 100% o
  perfil é removido (sRGB, sem custo). Perfis em `~/.local/share/ukiyo/icc/`; estado em `~/.local/state/ukiyo/saturacao`.
  O KWin guarda a escolha em `~/.config/kwinoutputconfig.json` (persiste após reiniciar).
- **Verificado:** KWin aceita o perfil (origem ICC) e volta a sRGB; capturas de tela têm pixels idênticos com 60% e 100%
  (a correção vale só para o painel). **Efeito visual no painel: a confirmar pelo usuário.**

**Backups:** `backups/2026-11-06_224156-washi-tela-widget/` (kwinoutputconfig.json antes do teste) e
`backups/2026-11-06_224427-washi-tela-widget/` (appletsrc, plasmashellrc, kwinoutputconfig.json antes de instalar).

**Desfazer:** `~/ukiyo/themes/washi/scripts/remover-widget-tela.sh` (volta saturação a 100%, remove o widget e o pacote).

## 2026-11-06 — Modo claro salvo + modo escuro "Yoru" (separado)

**Modo claro (Washi) salvo:** `modos/claro/retrato-2026-11-06_225218/` (cópia das configurações + `estado.env` com os valores-chave:
esquema Washi, ícones washi-pixel, decoração WashiPixel, DotGothic16 nos títulos, cursor 32 px, papel de parede e bloqueio Washi-v2,
Konsole/Kdenlive em Sumi). Nenhum arquivo do tema Washi foi alterado para criar o modo escuro.

**Modo escuro Yoru (夜):** tudo em `themes/yoru/` (geradores em `tools/`):
- Esquema `Yoru.colors` (índigo `#1C1E2E`, texto `#E6E4EC` 13:1, seleção torii; contraste em `themes/yoru/preview/contraste-yoru.txt`).
- Papel de parede "Rua do templo" (pixel art noturna: lanternas chōchin, shoji acesos, torii, templo, lua crescente).
- Ícones `yoru-pixel` (mesmas grades do Washi + borda externa clara de 1 px; herda breeze-dark).
- Decoração Aurorae `YoruPixel` (gerador do Washi carregado sem alteração, paleta trocada em memória).
- Mantém: layout, cursor, fontes, Konsole/Kdenlive (Sumi), Audacity, OBS, áudio e login.

**Alternar:**
```bash
~/ukiyo/modos/modo-escuro.sh    # Yoru
~/ukiyo/modos/modo-claro.sh     # Washi (valores do retrato salvo)
```
Cada troca faz backup em `backups/<data>-antes-modo-{escuro,claro}/`. Volta ao claro verificada item a item contra o retrato
(painéis: arquivo idêntico). Estado atual em `~/.local/state/ukiyo/modo`.

**Widget Tela:** passou a usar `tela-escuro.svg` (raios claros) quando o fundo do painel é escuro; no modo claro o ícone é o mesmo.

## 2026-11-06 — Botões de tema no widget Tela

**O que mudou:** o widget `org.ukiyo.tela` ganhou a seção **Tema** com os botões "Claro (Washi)" e "Escuro (Yoru)"
(o atual fica marcado; os botões ficam bloqueados durante a troca, com indicador "aplicando…"). O auxiliar `washi-tela`
ganhou `tema claro|escuro` (chama `modos/modo-claro.sh` / `modos/modo-escuro.sh`, que fazem backup) e informa `MODO=` em `ler`.
Saída da última troca: `~/.local/state/ukiyo/ultima-troca-de-tema.log`; em caso de falha o widget mostra um aviso.
Verificado: troca em 1–2 s nos dois sentidos; tema inválido recusado; o widget não troca o tema ao carregar (8 s sem cliques).

**Backup:** `backups/2026-11-06_225926-widget-tela-tema/` (pacote instalado e gerador anteriores).
**Desfazer:** `kpackagetool6 -t Plasma/Applet -u backups/2026-11-06_225926-widget-tela-tema/org.ukiyo.tela`
(ou remover tudo com `themes/washi/scripts/remover-widget-tela.sh`).

## 2026-11-06 — Tema "Mary's" (primeira parte)

Separado do Washi e do Yoru, em `themes/marys/`: esquema `Marys.colors` (rosa/creme, texto ameixa 10:1; contraste em
`themes/marys/preview/contraste-marys.txt`), papel de parede de gatinhos (`wallpaper/gatinhos-1920x1080.png`) e ícones
`marys-pixel` (lançador = carinha de gato, mostrar área de trabalho = patinha). Script `modos/modo-marys.sh` escrito (sintaxe
conferida), ainda não executado. Pendente: decoração própria (usa WashiPixel provisoriamente), botão no widget Tela, teste real.

## 2026-11-07 — Tema "Mary's" concluído + botão no widget

- Decoração Aurorae `MarysPixel` (gerador do Washi carregado sem alteração, paleta rosa/creme/ameixa em memória):
  `themes/marys/tools/gerar-decoracao-marys.py` → instalada em `~/.local/share/aurorae/themes/MarysPixel` pelo script do modo.
- `modos/modo-marys.sh`: aplica esquema Marys, ícones marys-pixel, decoração MarysPixel, papel de parede e bloqueio "gatinhos"
  (backup em `backups/<data>-antes-modo-marys/`). Mantém layout, cursor, fontes, Konsole/Kdenlive (Sumi), Audacity, OBS, áudio e login.
- Widget Tela: terceiro botão **Mary's (gatinhos)** (ícone carinha de gato); auxiliar aceita `tema marys`.
  Backup do widget anterior: `backups/2026-11-07_010231-widget-tela-marys/`.
- **Verificado:** troca escuro → Mary's → escuro pelo auxiliar do widget, chaves conferidas (esquema, ícones, decoração,
  papel de parede, bloqueio). Sistema devolvido ao modo **escuro** (escolha do usuário).
- **Pendente:** captura do sistema real em Mary's (a tela bloqueou por inatividade durante o teste). Prévia montada com os
  arquivos do tema: `themes/marys/preview/previa-marys.png` (não é captura do sistema).

**Desfazer/voltar:** botões Claro/Escuro do widget, ou `modos/modo-claro.sh` / `modos/modo-escuro.sh`.

## 2026-11-07 — Tema "Neon Tokyo" (cyberpunk) + Mary's conferido

**Neon Tokyo**, separado dos outros temas, em `themes/neontokyo/` (geradores em `tools/`):
- Esquema `NeonTokyo.colors`: fundo `#0B0D17`, texto `#E6F1FF` 17:1, seleção magenta `#FF2E88` com texto escuro 5,5:1,
  links/foco ciano `#00E5FF`, avisos `#FFE600` (contraste em `themes/neontokyo/preview/contraste-neontokyo.txt`).
- Papel de parede "Rua na chuva" (letreiros neon com caracteres pixel, skyline em 3 profundidades, carros voadores,
  asfalto molhado com reflexos, chuva).
- Ícones `neontokyo-pixel` (grades do Washi recoloridas + borda ciano de 1 px) e decoração `NeonTokyoPixel`
  (moldura ciano, barra azul-noite, fechar magenta) — geradores dos outros temas carregados sem alteração.
- `modos/modo-neontokyo.sh` (backup em `backups/<data>-antes-modo-neontokyo/`).
- Widget Tela: quarto botão **Neon Tokyo (cyberpunk)**; botões de tema em grade 2×2.
  Backup do widget anterior: `backups/2026-11-07_012604-widget-tela-neontokyo/`.

**Verificado no sistema real:** troca escuro → Neon Tokyo → Mary's → escuro pelo widget; capturas
`docs/visual/capturas/neontokyo-{desktop-limpo,janelas}.png` e `marys-{desktop-limpo,janelas}.png` (a captura real do
Mary's, antes pendente, foi feita). Sistema devolvido ao modo **escuro**.

## 2026-11-07 — Tema "Touge 峠" (drift na montanha)

Separado dos outros temas, em `themes/touge/` (geradores em `tools/`):
- Esquema `Touge.colors` (racing claro): branco gelo `#F2F2F0`, texto preto 17:1, seleção vermelha `#D7141E` com texto branco 5,2:1,
  links azuis, avisos âmbar (contraste em `themes/touge/preview/contraste-touge.txt`).
- Papel de parede "Curva da montanha": touge noturno com grampo, guard-rail com refletores, dois carros esportivos genéricos
  (sem marcas) em drift com fumaça, faróis e lanternas, cidade no vale, placa de curva, "TOUGE" com faixa quadriculada.
- Ícones `touge-pixel` (lançador = volante esportivo, mostrar área de trabalho = bandeira quadriculada) e decoração
  `TougePixel` (barra preta, título branco, foco amarelo, fechar vermelho) — geradores dos outros temas carregados sem alteração.
- `modos/modo-touge.sh` (backup em `backups/<data>-antes-modo-touge/`).
- Widget Tela: quinto botão **Touge 峠 (drift)** (terceira linha). Backup do widget anterior: `backups/2026-11-07_013934-widget-tela-touge/`.

**Verificado no sistema real:** escuro → Touge → escuro pelo widget; capturas `docs/visual/capturas/touge-{desktop-limpo,janelas}.png`.
Sistema devolvido ao modo **escuro**.

## 2026-11-07 — Troca de temas otimizada + pré-carregamento padrão

**Diagnóstico (medido):** a troca levava ~8 s porque cada script regenerava e recopiava todos os recursos (apagar/recopiar
a pasta de ícones invalidava o cache de ícones de todos os apps abertos), usava `plasma-changeicons` (~2,2 s), recarregava a
decoração duas vezes (passagem pelo Breeze), esperava o `KWin reconfigure` (1,2–1,6 s) e o painel (até 3,9 s na fila),
e copiava pastas GTK inteiras a cada troca (23 backups, 23 MB).

**O que mudou:**
- `modos/instalar-temas.sh` — **pré-carrega** os recursos dos temas (Yoru, Mary's, Neon Tokyo, Touge; Washi só conferido)
  em `~/.local/share`. Copia só o que mudou. Com `--se-necessario`, só refaz se algum gerador/papel de parede mudou (13 ms).
- `~/.config/autostart/ukiyo-temas.desktop` — roda `instalar-temas.sh --se-necessario` no login (**padrão**).
- `modos/trocar-tema.sh <tema>` — só aplica: papel de parede → ícones (chave com notificação, ~35 ms) → decoração (uma
  recarga, sem esperar o KWin) → bloqueio → esquema de cores; chamadas ao painel em segundo plano. Histórico leve em
  `~/.local/state/ukiyo/historico-temas.log` em vez de backup completo a cada troca.
- `modos/modo-{claro,escuro,marys,neontokyo,touge}.sh` viraram atalhos para `trocar-tema.sh` (o widget continua igual).

**Resultado medido (sistema ocioso):** script ~150 ms; tudo aplicado em ~0,8 s (2,8 s na primeira volta ao claro). Antes: ~8 s.
Os cinco temas conferidos (esquema, ícones, decoração, papel de parede; GTK acompanha).

**Backup dos scripts anteriores:** `backups/2026-11-07_014833-modos-antes-otimizacao/`.
**Desfazer:** copiar os scripts desse backup de volta para `modos/` e apagar `~/.config/autostart/ukiyo-temas.desktop`.

## 2026-11-07 — Troca de temas suave (cortina de transição no widget)

**Medição do engasgo** (`modos/medir-travamento.py`: sonda painel e KWin a cada 50 ms): ao mudar o esquema de cores o próprio
KDE redesenha compositor, painel e apps — KWin ~1,7–2,9 s e painel ~2 s sem responder, ~5–6 s de travamento somado numa troca
completa. Testado: não é a decoração Aurorae (com Breeze é igual); aplicar cores de forma "leve" reduz pouco e quebra as
cores dos apps GTK (não adotado; script de teste `modos/aplicar-cores.py` mantido só para diagnóstico).

**O que mudou:** o widget Tela passou a cobrir a tela com uma **cortina** na cor do tema de destino (nome em DotGothic16):
fade de entrada 0,18 s → aplica o tema (`trocar-tema.sh <tema> --esperar`) → espera o KDE terminar (+1,1 s) → fade de saída
0,32 s. O redesenho/engasgo acontece por baixo da cortina. Trava de segurança: a cortina sai sozinha em 8 s.
Verificado por capturas durante a transição (tela inteira coberta, inclusive barra/dock; tema aplicado por baixo).
Trocas pelo terminal (`modos/modo-*.sh`) continuam sem cortina.

**Backup do widget anterior:** `backups/2026-11-07_020004-widget-tela-cortina/`.

## 2026-11-07 — Cortina de transição removida (pedido do usuário)

Widget Tela restaurado para a versão anterior à cortina, a partir de `backups/2026-11-07_020004-widget-tela-cortina/`
(gerador e pacote). A troca volta a ser aplicada diretamente, sem tela de carregamento.

## 2026-11-07 — Troca de tema sem mudar as cores dos apps

`modos/trocar-tema.sh` deixou de aplicar o esquema de cores: troca só papel de parede, ícones, decoração das janelas e fundo
do bloqueio. As cores dos apps ficam fixas no esquema atual (Yoru). Motivo: a mudança de cores é o que faz o KDE travar ~2 s.
Backup do script anterior: `backups/trocar-tema.sh.antes-sem-cores-*`. Para escolher as cores fixas: Configurações do sistema →
Cores (ou `plasma-apply-colorscheme <Esquema>`).

## 2026-11-07 — Papéis de parede revisitados ("Ma Pixel 間") — gerados, ainda não ativados

Filosofia visual da série: `docs/visual/filosofia-papeis-de-parede.md`. Comparação: `docs/visual/papeis-de-parede-antes-depois.png`.

- **Ferramentas:** pacote `python3-venv` (instalado pelo usuário via apt) + ambiente do projeto `.venv/` (fora do git) com
  Pillow e NumPy do PyPI. Base comum: `scripts/pixelarte.py` (tela 480×270, paleta curta, dithering Bayer, ampliação ×4 nítida,
  fonte pixel DotGothic16). Desfazer: `rm -rf .venv` e `sudo apt remove python3-venv`.
- **Novos geradores e imagens** (os anteriores continuam intactos):
  - Washi: `themes/washi/tools/gerar-papel-de-parede-v3.py` → `wallpaper/diamante-*.png` (Fuji de diamante, 夕凪)
  - Yoru: `themes/yoru/tools/gerar-papel-de-parede-v2.py` → `wallpaper/senbon-*.png` (túnel de torii, 夜詣)
  - Mary's: `themes/marys/tools/gerar-papel-de-parede-v2.py` → `wallpaper/movel-*.png` (gatinha na lua-móbile, おやすみ)
  - Neon Tokyo: `themes/neontokyo/tools/gerar-papel-de-parede-v2.py` → `wallpaper/sinal-*.png` (letreiro 深夜営業 na chuva, 雨夜)
  - Touge: `themes/touge/tools/gerar-papel-de-parede-v2.py` → `wallpaper/rastro-*.png` (rastro de luz nos grampos, 峠道)
  - Rodar: `.venv/bin/python <gerador>`.
- Nenhuma configuração do sistema foi alterada nesta etapa.

### Ativação (mesmo dia, aprovada pelo usuário)
- Novos pacotes de papel de parede em `~/.local/share/wallpapers/`: `Washi-v3`, `Yoru-v2`, `Marys-v2`, `NeonTokyo-v2`,
  `Touge-v2` (instalados por `modos/instalar-temas.sh`). Os pacotes antigos continuam lá.
- `modos/trocar-tema.sh` aponta cada tema para o pacote novo (o claro usa `Washi-v3` no lugar do `Washi-v2` do retrato).
- Tema atual (escuro) reaplicado: área de trabalho e bloqueio com `Yoru-v2`.
- O fundo do login (SDDM) **não** foi alterado (continua o Washi v2 com desfoque; exige sudo).
- **Backup:** `backups/2026-11-07-papeis-ma-pixel/` (scripts `trocar-tema.sh` e `instalar-temas.sh`, pasta `wallpapers`,
  `kscreenlockerrc`, `plasma-org.kde.plasma.desktop-appletsrc`).
- **Desfazer:** copiar `trocar-tema.sh` e `instalar-temas.sh` do backup para `modos/`, rodar `modos/modo-escuro.sh`
  (ou o tema desejado) e, se quiser, apagar os pacotes `*-v2`/`Washi-v3` novos.

## 2026-11-07 — Projeto preparado para vários agentes (Codex/Claude) e escalável

- **`AGENTS.md`** (novo) passa a ser a fonte única de regras, lida pelo Codex. Inclui as preferências aprendidas, os
  comandos e o passo a passo para adicionar um tema. `CLAUDE.md` virou um arquivo curto que importa o `AGENTS.md` e o
  `docs/estado-atual.md`.
- **`docs/estado-atual.md`** (novo): passagem de bastão com o que está ativo, o que está pausado e as recusas do usuário.
- **`modos/temas.conf`** (novo): registro único dos temas. `modos/trocar-tema.sh` e `modos/instalar-temas.sh` passaram a
  lê-lo (antes havia valores fixos repetidos em cada script). Os valores resolvidos foram conferidos e são idênticos
  aos anteriores. Para adicionar um tema, basta uma linha no registro, mais a pasta do tema e o atalho.
- **`requirements.txt`** + **`scripts/preparar-ambiente.sh`** recriam o `.venv`. **`scripts/gerar-papeis-de-parede.sh`**
  redesenha os papéis de parede pelo registro (resultado determinístico, conferido por hash).
- **Backup:** `backups/2026-11-07-escalavel/` (`CLAUDE.md`, `trocar-tema.sh`, `instalar-temas.sh` anteriores).
- **Desfazer:** copiar os três arquivos do backup de volta; apagar `AGENTS.md`, `docs/estado-atual.md`,
  `modos/temas.conf`, `requirements.txt`, `scripts/preparar-ambiente.sh` e `scripts/gerar-papeis-de-parede.sh`.

## 2026-11-07 — Etapa 5a: esteira de pós-produção (`tiktok`)

- **`producao/tiktok.sh`** (novo), instalado como comando `tiktok` (link em `~/.local/bin/tiktok`):
  - `novo <nome>`: cria `~/Vídeos/TikTok/<data>_<nome>/` com `brutos/ audio/ legendas/ proxies/ export/ notas.md`.
  - `importar`: copia a mídia para `brutos/`, renomeando por data (metadado ou data do arquivo), sem tocar na origem.
  - `silencios`: gera `<vídeo>_sem-pausas.mp4` e a lista de cortes (silencedetect, margem de 0,15 s, H.264 VA-API).
  - `exportar`: 1080×1920 com escala/margem **na GPU** (`scale_vaapi` + `pad_vaapi`), H.264 VA-API high, VBR 12 Mb/s,
    AAC 192k/48 kHz e loudnorm em 2 passadas para −14 LUFS / −1 dBTP. No fim confere a resolução e o volume.
  - `limpar`: lista proxies e cache do Kdenlive com mais de N dias; só apaga com `--apagar`.
  - Testado com vídeo sintético (20 s → 15,6 s sem as pausas; horizontal → vertical com margem) e com um bruto de 30 s
    (exportado em 5,5 s; −9,2 → −14,0 LUFS). Arquivos de teste apagados.
- **Kdenlive** (`~/.config/kdenliverc`): proxies ligados e gerados automaticamente **na GPU** (perfil VA-API do
  próprio Kdenlive, 640 px, `.mov`; testado: 30 s em 1,3 s), perfil padrão de projeto `vertical_hd_30` e pasta de
  projetos `~/Vídeos/TikTok`. Pastas antigas (`brutos/`, `exports/`, `projetos/`, `testes/`) mantidas.
- **Backup:** `backups/2026-11-07-esteira-pos/kdenliverc`.
- **Desfazer:** `cp backups/2026-11-07-esteira-pos/kdenliverc ~/.config/` (com o Kdenlive fechado) e `rm ~/.local/bin/tiktok`.

## 2026-11-07 — Henshū 編集: editor de vídeo com chat (Claude ou Codex)

O Kdenlive não aceita plugins/painéis de terceiros nem controle externo, então foi criado um editor próprio.
- **Código:** `editor/henshu/` (`projeto.py`: formato `projeto.json`; `render.py`: FFmpeg, filtros na CPU e
  codificação VA-API; `agentes.py`: ponte com `claude -p` e `codex exec --json`; `app.py`: janela Qt/PySide6).
  Lançador `editor/henshu.sh`, link `~/.local/bin/henshu`, entrada no menu `~/.local/share/applications/henshu.desktop`.
- **Como funciona:** o agente edita `projeto.json` na pasta do vídeo; a janela percebe a mudança, refaz a prévia
  (540×960, ~2 s para 10 s de vídeo) e recarrega o player. "Exportar final" gera 1080×1920 com −14 LUFS em `export/`.
- **Segurança:** Claude só com edição de arquivos da pasta + Bash restrito (`ffprobe`, `ls`, `tiktok silencios`); Codex
  com sandbox `workspace-write` (só escreve na pasta, sem rede). Instruções para os agentes geradas em cada pasta de
  vídeo (`AGENTS.md` + `CLAUDE.md`). Conversa e sessões em `<vídeo>/.henshu/`.
- **Pacotes instalados pelo usuário:** `python3-pyside6.qtwidgets`, `python3-pyside6.qtmultimedia`,
  `python3-pyside6.qtmultimediawidgets` (+ dependências). Codex logado pelo usuário.
- **Testado:** prévia/export com projeto sintético; Claude e Codex editando via ponte (incluindo continuar a conversa);
  janela atualizando sozinha após edição do Claude (demo em `~/Vídeos/TikTok/2026-11-07_demo-henshu/`).
- **Desfazer:** `rm ~/.local/bin/henshu ~/.local/share/applications/henshu.desktop`; `sudo apt remove` dos pacotes
  acima; apagar `editor/`.

## 2026-11-07 — Leitura e visão do projeto (Codex)

**O que mudou:** registrada em `docs/estado-atual.md` a definição do usuário: sua distro pessoal baseada em
Debian, totalmente ao seu gosto. Inventário e inspeção do projeto, sem alterações de configuração do sistema,
ativação visual ou execução de gravações. Código e plano de implementação preservados.

**Backup:** `backups/2026-11-07-leitura-visao-projeto/` (`estado-atual.md` e `mudancas.md` anteriores).
**Desfazer:** remover a seção "Visão do projeto" acrescentada ao estado atual e esta entrada do registro, ou
restaurar os dois documentos desse backup caso não tenham recebido outras mudanças posteriores.

## 2026-11-07 — Backup anterior ao refino visual e cinco propostas de wallpaper

**Backup:** `backups/2026-11-07_052038-antes-refino-wallpapers/`. Arquivos `projeto.tar.gz` e `desktop.tar.gz`
reabertos para verificar integridade; somas SHA-256 em `SHA256SUMS`; escopo em `LEIA-ME.txt`. Documentos
anteriores também copiados individualmente. Nenhuma alteração ativa no desktop ou nos aplicativos.

**O que mudou:** cinco novos arquivos PNG em `themes/<tema>/wallpaper/`, sufixo `-refino-2026-11-07.png`;
comparação local e prompts em `docs/visual/refino-2026-11-07/`. Edição pela ferramenta integrada image_gen,
sem API/CLI externa. Washi, Yoru, Mary's e Neon Tokyo conservam os motivos centrais; Touge passa a um pequeno
cupê numa curva de montanha ao anoitecer. Registro no plano e no estado atual. Propostas pendentes de aprovação.

**Desfazer:** remover apenas os novos arquivos dessa proposta e suas entradas documentais. Os arquivos originais,
os geradores e `modos/temas.conf` não foram substituídos. Para recuperação mais ampla, extrair os arquivos de backup
num diretório de revisão e restaurar seletivamente com os aplicativos fechados; não extrair por cima da sessão ativa.

## 2026-11-07 — Cinco refinos aprovados e ativados

**Mudanças:** `modos/temas.conf` aponta aos pacotes novos `*-Refino-20261107`, com PNGs nativos 1672×941.
Instalador inclui todos os PNGs na assinatura; gerador ignora entradas `-`, preservando bitmaps aprovados.
Cinco arquivos instalados conferidos contra as fontes. Washi reaplicado ao desktop e bloqueio; consulta D-Bus
confirmou Washi refinado. Usuário alternando temas durante a verificação, sem forçar nova seleção.
Originais e pacotes anteriores preservados. SDDM, OBS e áudio sem alterações.

**Backup:** `backups/2026-11-07_052859-ativar-refinos/`.
**Desfazer:** restaurar os três scripts/registro de `projeto/` do backup para seus caminhos originais;
executar `modos/trocar-tema.sh <tema-desejado> --esperar`. Os pacotes antigos continuam instalados.

## 2026-11-07 — Filme de apresentação da distro (48 s)

**Pedido:** apresentação de 30–60 s usando wallpapers antigos/novos e liberdade para capturas e trocas de temas.
**Arquivos:** `producao/apresentacao/` (captura, montagem, trilha original sintetizada e instruções);
saída local `renders/apresentacao-2026-11-07/Ukiyo-apresentacao-48s.mp4`.
Capturas limpas dos cinco temas em `docs/visual/capturas/apresentacao-2026-11-07/` (fora do Git).
Montagem com wipes, movimentos suaves, títulos e encerramento; 1920×1080/30 fps, H.264 VA-API + AAC.
Trilha gerada em arquivo, sem samples externos, microfone ou áudio do sistema. OBS e ajustes de áudio seguem pausados.

**Backup anterior às capturas:** `backups/2026-11-07_053335-video-apresentacao/` (documentos, cores, KWin, bloqueio, configuração do Plasma e modo).
As capturas finais foram feitas na área 四 e conferidas visualmente; tema e área anteriores restaurados.
**Desfazer:** remover apenas os arquivos novos em `producao/apresentacao/`, `renders/apresentacao-2026-11-07/`
e as capturas dessa apresentação. Não houve alteração permanente planejada no desktop; backup disponível para
restauração seletiva caso necessário. Nenhum commit nem publicação.

**Validação do filme:** 48,000 s; H.264 High/VA-API, 1920×1080/30 fps; AAC estéreo 48 kHz;
decodificação integral sem erros antes da conversão final do áudio para 48 kHz, quadros do MP4 final conferidos.
Trilha sem saturação (pico medido antes da conversão: −5,5 dBFS). Hash do arquivo final em `renders/apresentacao-2026-11-07/SHA256SUMS`.

## 2026-11-07 — Spotify instalado e widget preparado

**O que mudou:** `scripts/instalar-spotify.sh` prepara repositório oficial com chave restrita por Signed-By,
confere identificador da chave e salva fontes anteriores/pacotes. Executado pelo usuário; instalado
`spotify-client 1:1.2.95.453.g0eeebbed`. Backup APT: `backups/2026-11-07_055151-spotify-apt/`.
Widget novo em `widgets/spotify/`: capa, metadados e transporte MPRIS exclusivo do Spotify; volume por
saída do aplicativo com pactl, sem alterar volume geral ou microfone. Scripts locais de instalar/remover
com backup e sem reinício do painel. Ainda não ativado: pendente de aprovação visual.

**Backup documental/painel:** `backups/2026-11-07_054921-spotify-widget/`.
**Validação:** pacote carregado em Plasma offscreen; player fictício confirmou Next/PlayPause,
metadados e capa; três testes de filtragem/volume passaram. Prévia `widgets/spotify/preview/widget-demo.png`.
Falta validar reprodução/volume na conta real após login e faixa escolhida pelo usuário.
**Desfazer:** instruções completas em `widgets/spotify/README.md`; remover widget com seu script local
se ativado; Spotify pode ser removido pelo usuário com `sudo apt-get remove spotify-client`; restaurar
fontes/chave anteriores do backup APT ou remover somente os arquivos novos marcados como antes ausentes.

## 2026-11-07 — Widget Spotify ativado após aprovação

**O que mudou:** pacote `org.ukiyo.spotify` instalado no perfil do usuário; widget 55 adicionado
à barra superior via API do Plasma, sem reiniciar painel. Identificador/localização confirmados por D-Bus
e metadados conferidos por kpackagetool6. Não foi iniciada música nem alterado volume.

**Backup:** `backups/2026-11-07_055837-ativar-widget-spotify/` (painel, plasmashellrc e documentos anteriores).
**Desfazer:** `widgets/spotify/remover-widget.sh` remove apenas este widget/pacote, sem afetar o Spotify.
**Pendente:** validação com música real escolhida pelo usuário, após abrir/autenticar o Spotify.

## 2026-11-07 — Henshū v2: predefinições, transcrição local, legendas, reenquadrar, velocidade, transições, SRT/capítulos

- **Formato do projeto v2** (`editor/henshu/projeto.py`; projetos v1 continuam abrindo): `formato.preset` vertical
  (1080×1920) ou horizontal (1920×1080); por clipe `velocidade` (0,25–4, áudio sem mudar o tom), `enquadrar`
  ajustar/preencher com `foco_x`/`foco_y` (reenquadrar horizontal↔vertical), `transicao` corte/fade/dissolver;
  `legendas` (ativo, estilo frases/karaoke/pixel, posição, tamanho) e `capitulos`.
- **Transcrição local** (`editor/henshu/transcrever.py`, comando `henshu-transcrever` → `~/.local/bin`): faster-whisper
  modelo small (int8, CPU) no `.venv`; o áudio é decodificado pelo FFmpeg do sistema (o PyAV 19 é incompatível com o
  faster-whisper 1.2.1). Cache por arquivo em `<vídeo>/.henshu/transcricoes/`; frases revisáveis em
  `<vídeo>/legendas/legendas.json` (a anterior vira `.anterior`). Teste: 22 s de fala em 5 s.
- **Legendas** (`editor/henshu/legendas.py`): frases curtas (vertical ≤4 palavras; horizontal ≤9), karaokê com a palavra
  falada em amarelo, estilo pixel (DotGothic16 em caixa escura); queimadas via libass. Exporta `.srt` e capítulos do
  YouTube (`export/<nome>_capitulos.txt`); capítulos também embutidos no MP4 final.
- **Janela:** seletor de formato, Transcrever (com progresso), Legendas + estilo, Revisar legendas (tabela editável que
  posiciona o player), Exportar final (sem travar a janela), SRT e capítulos; linha do tempo com faixa de legendas,
  marcas de velocidade/enquadramento, dissolver (listrado), fade e capítulos.
- **Agentes:** instruções v2 em cada pasta de vídeo; Claude pode rodar `henshu-transcrever`; testado o Codex
  transcrevendo dentro da sandbox (modelo carregado só do disco) e criando capítulos pelos assuntos falados.
- **Testado:** velocidade 2×/0,5×, preencher com foco, dissolver (duração 13,2 s exata), fade, capítulos embutidos,
  três estilos de legenda (vertical e horizontal), janela abrindo sem erros. Cópias de teste com gravação pessoal apagadas.
- **Backup:** `backups/2026-11-07-henshu-v2/` (editor anterior e `requirements.txt`).
- **Desfazer:** restaurar `editor/` do backup; `rm ~/.local/bin/henshu-transcrever`; `.venv/bin/pip uninstall faster-whisper
  ctranslate2 onnxruntime av tokenizers huggingface-hub`; apagar `~/.cache/huggingface/hub/models--Systran--faster-whisper-small`.

## 2026-11-07 — Proposta de refino dos ícones dos aplicativos

**Mudanças:** novos SVGs separados em `themes/<tema>/icons-refino/`, com oito desenhos em grade 24×24
para Dolphin, Firefox, Konsole, OBS, Kdenlive, Audacity, Configurações e Spotify; 120 arquivos/aliases em cinco temas.
Gerador padrão `scripts/gerar-icones-refinados.py`; pranchas reais em `docs/visual/refino-icones-2026-11-07/`
geradas por `scripts/previa-icones-refinados.py`. Escopo assumido: dock inferior; clarificação pendente.
Sem instalação, ativação, alterações nos originais ou no registro/instalador de temas.

**Backup:** `backups/2026-11-07_061644-refino-icones/icones-originais.tar.gz`, com hash e verificação de leitura.
**Validação:** 120 SVGs XML válidos, dentro da grade, reprodução idêntica por hash; arquivos anteriores
conferidos contra o backup. **Desfazer:** remover somente as novas pastas `icons-refino`, os dois scripts
novos e as pranchas desta proposta; o sistema ativo não foi alterado.

## 2026-11-07 — Ícones refinados aprovados e ativados

**O que mudou:** cinco temas `*-pixel-refino` instalados em `~/.local/share/icons/`, com os oito desenhos
aprovados e aliases. Yoru refinado aplicado ao tema ativo via `kwriteconfig6 --notify` e sinal KIconLoader,
sem reiniciar painel. `modos/temas.conf` aponta aos refinos; `modos/instalar-temas.sh` gera/instala os
novos conjuntos e preserva/instala os temas-base, utilizados como fallback. A assinatura inclui o gerador
e os recursos novos, mantendo os ícones nas trocas de tema e no login. Cores dos apps e wallpapers intactos.

**Backup:** `backups/2026-11-07_062029-ativar-icones-refinados/` (registro/instalador/documentos e arquivo `usuario.tar.gz`
com kdeglobals, autostart, estado e ícones anteriores).
**Validação:** 125 arquivos instalados idênticos às fontes, herança/FollowsColorScheme conferidos,
pré-carregamento `--se-necessario` sem alterações adicionais; chave ativa `yoru-pixel-refino`.
**Desfazer:** restaurar `modos/temas.conf` e `modos/instalar-temas.sh` de `projeto/` nesse backup;
para o Yoru, executar `kwriteconfig6 --notify --file kdeglobals --group Icons --key Theme yoru-pixel`
e `dbus-send --session --type=signal /KIconLoader org.kde.KIconLoader.iconChanged int32:0`.
Os conjuntos anteriores permanecem instalados, e não é necessário remover os novos para reverter.

## 2026-11-07 — Redesenho dos ícones v2 após crítica ao refino v1

**Motivo:** usuário considerou o resultado v1 conservador e semelhante a apenas acrescentar contorno.
**Mudanças:** nova família em SVG 48×48, com objetos redesenhados e identidades reconhecíveis,
cores próprias por aplicativo e luz em planos. Fontes novas `scripts/gerar-icones-v2.py` e
`scripts/previa-icones-v2.py`; recursos em `themes/<tema>/icons-v2/`; pranchas e direção em
`docs/visual/icones-v2-2026-11-07/`. Cinco temas, oito desenhos e 24 aliases por tema.
**Backup:** `backups/2026-11-07_062347-redesenho-icones-v2/refino-v1.tar.gz`, mais documentos anteriores.
**Validação:** 120 SVGs XML válidos, limites de grade e determinismo conferidos; v1, registro e instalador
idênticos ao backup. Nada instalado ou ativado.
**Desfazer:** remover apenas os novos scripts, diretórios `icons-v2` e pranchas v2. Sistema ativo preservado.

## 2026-11-07 — Redesenho dos ícones v2 aprovado e ativado

**Mudanças:** `modos/temas.conf` seleciona `*-pixel-art-v2` nos cinco temas. Instalador gera a família v2,
instala recursos de `icons-v2/` e mantém os temas-base para herança. Assinatura inclui gerador e SVGs v2.
Washi era o tema ativo na aplicação: aplicada chave `washi-pixel-art-v2` com notificação e sinal KIconLoader.
Sem reiniciar painel nem trocar wallpaper. Versões anteriores preservadas.
**Backup:** `backups/2026-11-07_062743-ativar-icones-v2/` (registro, instalador, documentos e configurações do usuário).
**Validação:** 125 arquivos instalados idênticos às fontes; herança/FollowsColorScheme conferidos;
pré-carregamento reconhece estado atualizado.
**Desfazer:** restaurar registro e instalador de `projeto/modos/` do backup; aplicar ícones da versão anterior
com `kwriteconfig6 --notify --file kdeglobals --group Icons --key Theme washi-pixel-refino` e sinal
`dbus-send --session --type=signal /KIconLoader org.kde.KIconLoader.iconChanged int32:0` (Washi).

## 2026-11-07 — Nova identidade: Ukiyo 浮世, e preparação para o GitHub

- **Nome:** studio-linux → **Ukiyo 浮世** ("mundo flutuante", do ukiyo-e). Pasta `~/ukiyo` (com o link de
  compatibilidade `~/studio-linux → ~/ukiyo`); estado `~/.local/state/ukiyo` e dados `~/.local/share/ukiyo` (os nomes
  antigos viraram links); marcador do `~/.bashrc` `# >>> ukiyo: PATH >>>`; autostart `ukiyo-temas.desktop`.
- **Widgets renomeados** `org.studiolinux.washi.tela` → `org.ukiyo.tela` e `org.studiolinux.spotify` → `org.ukiyo.spotify`:
  pacotes novos instalados, IDs trocados no `appletsrc` com o plasmashell parado (mesmos applets 52 e 55, com as
  configurações mantidas) e pacotes antigos removidos. O perfil ICC foi reaplicado pelo caminho novo.
- **Portabilidade:** nenhum caminho `/home/<usuário>` no código; `scripts/instalar-spotify.sh` aceita qualquer usuário;
  novo `scripts/instalar-comandos.sh` (links em `~/.local/bin` + atalho do Henshū).
- **Público:** `README.md`, `docs/instalacao.md`, `CHANGELOG.md`, `SECURITY.md`, `LICENSE` (GPL-3.0-or-later),
  `LICENSES/` (CC BY-SA 4.0 para a arte e LGPL-2.0-or-later para o login derivado do Breeze), imagens em `docs/imagens/`
  (capturas novas na área 四 vazia; demo do Henshū feita a partir dos papéis de parede, sem conteúdo pessoal).
- **Fora do git:** retrato pessoal `modos/claro/retrato-*`, widget gerado `themes/washi/plasmoid/`, prévias do login
  `v5-login-preview*.png` (mostravam o campo de senha preenchido), `renders/`, `.henshu/`.
- **Incidente corrigido na hora:** uma captura com janelas pegou a área 一 com uma janela pessoal (sessão do Codex) e
  foi apagada antes de qualquer uso; as capturas finais foram refeitas movendo só as janelas de demonstração.
- **Backup:** `backups/2026-11-07-ukiyo-rebrand/` (`projeto.tar.gz` com o `.git` antigo, `externos.tar.gz`,
  `externos-share.tar.gz`, `SHA256SUMS`).
- **Desfazer:** extrair os tarballs do backup (projeto em `~`, externos em `~`), reinstalar os widgets antigos a partir
  de `externos.tar.gz` (`.local/share/plasma/plasmoids`) e restaurar o `appletsrc` com o plasmashell parado.

## 2026-11-07 — Publicado no GitHub: github.com/Davimachados/ukiyo (v1.0.0)

- Repositório **público** criado com `gh` (login do usuário). Histórico novo e limpo (7 commits por área + este),
  autor `Davi <143721445+Davimachados@users.noreply.github.com>` (o e-mail pessoal não aparece). Tag e release `v1.0.0`,
  tópicos, e *private vulnerability reporting* ativado.
- Antes do envio: varredura de tokens, chaves, e-mail pessoal e caminhos `/home/<usuário>` em todo o histórico (0 achados).
- O histórico git antigo (com o e-mail pessoal) ficou só no backup: `backups/2026-11-07-ukiyo-rebrand/git-antigo`.
- Fluxo daqui em diante: commits só quando o usuário pedir; `git push` envia para `origin/main`.
