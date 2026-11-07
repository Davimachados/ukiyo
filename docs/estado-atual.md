# Estado atual (passagem de bastão)

> Documento para continuar o trabalho com qualquer agente (Claude Code, Codex…). **Atualize ao fim de cada sessão.**
> Detalhes de cada mudança: `docs/mudancas.md`. Etapas: `docs/plano.md`.

## Identidade e publicação — 2026-11-07 (Claude Code)
- Projeto renomeado para **Ukiyo 浮世**; pasta `~/ukiyo` (link `~/studio-linux`), widgets `org.ukiyo.*`. Ver `docs/mudancas.md`.
- Repositório público preparado (README, instalação, licenças, imagens). Publicação no GitHub: ver a última entrada de `docs/mudancas.md`.

**Última atualização:** 2026-11-07 (Codex; ícones v2 ativados).

## O que está ativo agora
- **Tema atual:** consultar `~/.local/state/ukiyo/modo` (usuário alternando após ativação). O estado fica em `~/.local/state/ukiyo/modo`, e o histórico de trocas em
  `~/.local/state/ukiyo/historico-temas.log`.
- **Cores dos apps:** fixas no esquema Yoru. A troca de tema não as altera (decisão do usuário).
- **Temas:** claro (Washi), escuro (Yoru), Mary's, Neon Tokyo e Touge, todos registrados em `modos/temas.conf`.
  A troca é feita pelo widget "Tela" na barra superior ou por `modos/modo-<id>.sh`.
- **Papéis de parede:** refinos aprovados (cinco pacotes com sufixo `-Refino-20261107`). Os pacotes
  antigos continuam instalados.
- **Widget Tela** (`org.ukiyo.tela`): brilho, saturação (via ICC) e 5 botões de tema.
- **Pré-carregamento no login:** `~/.config/autostart/ukiyo-temas.desktop` executa `modos/instalar-temas.sh --se-necessario`.
- **Esteira de pós (`tiktok`)** pronta: novo/importar/silencios/exportar/limpar. Kdenlive com proxies na GPU e projeto
  vertical por padrão (ainda não usado num projeto real).
- **Henshū 編集** (`henshu`, menu do KDE): editor com prévia + chat Claude/Codex; v2 com formatos vertical/horizontal,
  transcrição local (`henshu-transcrever`), legendas (frases/karaokê/pixel) revisáveis, reenquadrar, velocidade,
  fade/dissolver, SRT e capítulos. Falta abrir no Kdenlive. Demo em `~/Vídeos/TikTok/2026-11-07_demo-henshu/`.
- **Ambiente Python:** `.venv/` com Pillow 13 e NumPy 2.5 (`scripts/preparar-ambiente.sh` recria).

## Pausado / aguardando o usuário
- **OBS e áudio:** pausados até o microfone definitivo ser conectado. Nada de gravações nem ajustes de áudio. O
  roteiro para quando o mic chegar está em `docs/plano.md` → Pendências.
- **Login (SDDM) V5b:** está pronto, mas a instalação exige sudo pelo usuário:
  `sudo ~/ukiyo/themes/washi/scripts/aplicar-v5-login.sh`. Depois, validar num logout real. Ainda usa o
  papel de parede Washi v2 com o desfoque do Breeze (o usuário escolheu assim).
- **OBS em Sumi:** só com autorização.

## Decisões e recusas do usuário (não repetir)
- **Sem tela de carregamento/cortina** na troca de tema. O usuário queria um fade quase instantâneo, que o KDE não
  oferece nativamente. O redesenho de ~2 s ao trocar cores foi resolvido deixando as cores dos apps fixas.
- Fazer só o que foi pedido; perguntas sempre em múltipla escolha; nenhum commit sem pedido.
- Ícones: usuário considerou o refino v1 conservador demais, como apenas acrescentar contorno.
  Quer mudanças perceptíveis de desenho e beleza; evitar outra rodada baseada só em borda/recoloração.

## Próximos passos (escolhidos pelo usuário em 2026-11-07, um de cada vez, com aprovação)
- ~~Esteira de pós-produção~~ (feita em 2026-11-07). ~~Legendas automáticas~~ (feitas no Henshū v2, transcrição local).
- **Modo Gravação** — Etapa 4 (a parte do OBS e a medição dependem da liberação do áudio/OBS).
- Depois: Etapa 3 (OBS), quando o microfone chegar; Etapa 7 (backup/checklist).

## Para começar uma sessão nova
1. Ler `AGENTS.md` e este arquivo.
2. Conferir o estado com `git status` e `tail -40 docs/mudancas.md`.
3. Se for mexer em papéis de parede: `scripts/preparar-ambiente.sh`.

## Visão do projeto — esclarecida pelo usuário em 2026-11-07
- O usuário define o Ukiyo como **sua distro pessoal baseada em Debian, totalmente ao seu gosto**.
  Essa visão abrange a experiência do computador: aparência, comportamento, ferramentas e fluxos próprios.
  A produção de vídeo/TikTok é uma parte importante desse ambiente, sem limitar a identidade do projeto.
- Implementação atual: personalização do Debian/KDE instalado neste notebook, com recursos visuais gerados por
  código, scripts de aplicação/restauração, widget Tela, esteira `tiktok` e editor Henshū. Não foi encontrada
  estrutura de geração de ISO, repositório de pacotes próprio ou instalador completo do ambiente. Esses itens
  não foram solicitados; a definição de distro pessoal não autoriza implementá-los por iniciativa do agente.
- Sessão de leitura (Codex): inventário de 618 arquivos fora de `.git`, `.venv`, backups, caches Python e
  capturas pessoais; leitura da documentação e inspeção de código, configurações e recursos gerados, incluindo
  a comparação visual dos cinco temas. Não equivale a auditoria linha a linha de todos os arquivos.
  Nenhum script de aplicação, gravação ou teste gráfico foi executado. Pendências anteriores preservadas.

## Backup e propostas de refino visual — 2026-11-07 (Codex)
- Pedido: backup do estado atual antes do refino dos cinco wallpapers; Touge com liberdade para nova composição;
  suavidade e personalidade, evitando excesso de brilho e acabamento genérico de IA.
- Backup verificado em `backups/2026-11-07_052038-antes-refino-wallpapers/`: `projeto.tar.gz` (inclui Git e trabalho não commitado),
  `desktop.tar.gz` (configurações e recursos visuais do usuário), hashes em `SHA256SUMS`. Não é imagem de disco;
  vídeos pessoais, dependências Python, backups anteriores e credenciais conhecidas ficam fora desse retrato.
- Novas propostas em `themes/<tema>/wallpaper/*-refino-2026-11-07.png`, geradas pela ferramenta image_gen
  a partir dos wallpapers atuais. Comparação: `docs/visual/refino-2026-11-07/comparacao.html`.
  Prompts completos: `docs/visual/refino-2026-11-07/prompts.md`.
- **Aprovadas e ativadas pelo usuário em 2026-11-07.** Registro atualizado; pacotes anteriores e
  geradores originais preservados. Os novos bitmaps não são reproduzidos pelos geradores determinísticos.

### Ativação dos refinos — 2026-11-07
- Cinco pacotes instalados e conteúdo conferido. Washi encontrado ativo e reaplicado com refino; confirmação via D-Bus do Plasma.
- Observadas trocas de tema durante a verificação; evitar forçar um tema após a escolha do usuário. Último estado lido: `claro`.
- Registro aponta aos novos bitmaps; gerador `-` significa preservar a imagem, sem geração por código.
- Backup: `backups/2026-11-07_052859-ativar-refinos/`. SDDM, OBS e áudio sem alterações.

## Vídeo de apresentação — 2026-11-07
- Filme de 48 s solicitado pelo usuário, com artes antigas/novas, capturas reais limpas dos cinco temas, motion
  e trilha original sintetizada offline. `producao/apresentacao/` contém scripts e roteiro.
- Saída: `renders/apresentacao-2026-11-07/Ukiyo-apresentacao-48s.mp4` (fora do Git).
- Capturas autorizadas nesta sessão; feitas na área 四 após conferir privacidade. Tema claro e área 一 restaurados.
- Backup anterior: `backups/2026-11-07_053335-video-apresentacao/`. OBS/microfone/configurações de áudio não usados.

## Spotify e widget — 2026-11-07
- Usuário pediu instalar Spotify e criar widget com capa, troca de faixas e volume. Spotify confirmado instalado:
  `spotify-client 1:1.2.95.453.g0eeebbed`, via script oficial `scripts/instalar-spotify.sh` executado pelo usuário com sudo.
- Repositório oficial com Signed-By; backup APT em `backups/2026-11-07_055151-spotify-apt/`.
- Widget em `widgets/spotify/`, id `org.ukiyo.spotify`: capa/título/controles na barra, popup com volume
  exclusivo do Spotify. **Ativado na barra superior após aprovação do usuário.**
- Prévia real QML com dados fictícios: `widgets/spotify/preview/widget-demo.png`. Testes MPRIS isolados confirmaram
  metadados, capa, Next/PlayPause; três testes garantem seleção exclusiva do Spotify e limites de volume.
- Ativação realizada com `widgets/spotify/instalar-widget.sh` (sem sudo, sem reiniciar painel).
  Falta validar com a conta real após abrir o aplicativo e iniciar uma faixa; não iniciar música por conta própria.
- Backup documental/painel: `backups/2026-11-07_054921-spotify-widget/`. Controles de saída do Spotify explicitamente solicitados;
  OBS, microfone e demais ajustes de áudio continuam pausados.

### Widget Spotify ativado — 2026-11-07
- Aprovação recebida; pacote instalado em `~/.local/share/plasma/plasmoids/org.ukiyo.spotify/`.
- Widget **55** confirmado via D-Bus na barra superior; sem reinício do Plasma, sem iniciar reprodução
  e sem alterar volume. Metadados de pacote conferidos; sem erros do widget no journal consultado.
- Backup: `backups/2026-11-07_055837-ativar-widget-spotify/`. Remover: `widgets/spotify/remover-widget.sh`.
- Validação com música real ainda depende de o usuário abrir/autenticar o Spotify e escolher uma faixa.

## Proposta de refino dos ícones — 2026-11-07
- Pedido: revisão/refino dos ícones da "bandeja de apps". Clarificação enviada; sem resposta até a preparação:
  assumida dock inferior (sete apps fixados + cobertura visual do Spotify), sem alterar rede/som/bateria.
- Propostas em `themes/<tema>/icons-refino/<tema>-pixel-refino/`; oito desenhos e aliases nos cinco temas,
  SVG 24×24, gerador padrão em `scripts/gerar-icones-refinados.py`; versões atuais preservadas.
- Prévia: `docs/visual/refino-icones-2026-11-07/comparacao.html` e `cinco-temas.png`.
- **Aprovados e ativados no escopo da dock inferior.** Registro atualizado para `*-pixel-refino`;
  instalador integra a geração/instalação dos novos conjuntos e preserva os temas-base herdados.
- Backup: `backups/2026-11-07_061644-refino-icones/`. 120 SVGs validados por XML/limites, geração determinística por hash;
  originais, geradores existentes, registro e instalador conferidos idênticos ao backup.

### Ativação dos ícones refinados — 2026-11-07
- Cinco temas `*-pixel-refino` instalados; Yoru refinado aplicado via chave Icons/Theme e sinal KIconLoader.
- `modos/temas.conf` passa a selecionar os refinos; instalador gera a família nova e instala também os temas-base.
  Assinatura inclui o gerador e os SVGs novos. Pré-carregamento com `--se-necessario` reconhece o estado atualizado.
- 125 arquivos instalados conferidos com as fontes e herança existente validada. Sem troca de wallpaper,
  mudança das cores dos apps, reinício do painel ou alteração dos aplicativos fixados.
- Backup anterior à ativação: `backups/2026-11-07_062029-ativar-icones-refinados/`. Reversão descrita no registro de mudanças.

## Redesenho de ícones v2 — 2026-11-07 (aprovado)
- Após a crítica ao refino v1, criada família nova em grade 48×48, com formas e planos de luz próprios por app:
  pasta aberta com folhas, raposa/globo, terminal de bancada, obturador, claquete/timeline, fones/onda, engrenagem e Spotify.
- SVGs separados em `themes/<tema>/icons-v2/<tema>-pixel-art-v2/`; gerador `scripts/gerar-icones-v2.py`.
- Comparação: `docs/visual/icones-v2-2026-11-07/comparacao.html`; faixa em tamanho real `dock-48px.png`.
- **Aprovado e ativado.** V1 preservado; registro/instalador integrados ao v2. Backup da preparação: `backups/2026-11-07_062347-redesenho-icones-v2/`.
- 120 SVGs XML válidos e dentro da grade; geração idêntica por hash, v1 conferido contra o backup.

### Ativação do redesenho v2 — 2026-11-07
- Cinco conjuntos `*-pixel-art-v2` instalados e registrados. Washi encontrado ativo na aplicação;
  chave confirmada `washi-pixel-art-v2`. Sem mudança de tema ou reinício do painel.
- Pré-carregamento inclui gerador/SVGs v2 na assinatura, instala a família nova e mantém os temas-base.
  `--se-necessario` conferido sem reinstalação. 125 arquivos instalados comparados com as fontes.
- Backup anterior: `backups/2026-11-07_062743-ativar-icones-v2/`. V1 e ícones originais continuam preservados.
