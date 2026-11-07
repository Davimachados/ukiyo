# Plano de implementação

Cada etapa termina com: verificação, registro em `docs/mudancas.md` (backup + como desfazer) e atualização deste plano.

## Etapa 1 — Inventário e organização ✅ (2026-11-06)
- [x] Inventário de hardware/software → `docs/estado-inicial.md`
- [x] PATH idempotente para `~/.local/bin`
- [x] `CLAUDE.md`, `.gitignore`, plano, registro de mudanças
- [x] Recomendação inicial de OBS → `docs/obs-recomendacao.md`

## ⏸ Pendências
- ~~Fazer logout/login para os títulos em DotGothic16~~ — feito e conferido em 2026-11-06 (21:11).
- **Áudio/OBS pausados (2026-11-06):** o microfone definitivo ainda não está conectado. Quando estiver:
  conferir o novo dispositivo/Base Volume, gravar amostra crua (`scripts/gravar-amostra-voz.sh`), avaliar
  ruído e dinâmica, testar filtros em A/B e só então configurar os filtros no OBS e fazer a gravação final.
  O mic interno está em 46% (nominal) — ver `docs/mudancas.md`. Nenhuma gravação ou ajuste de áudio até lá.

## Etapa 2 — Ferramentas de produção (concluída exceto áudio — ver pendências)
- Decidir origem dos pacotes: repositório Debian (OBS 30.2, Kdenlive 24.12) vs. Flatpak/Flathub (versões mais novas, sandbox). Recomendação inicial: Debian para FFmpeg/Audacity; avaliar OBS e Kdenlive caso a caso.
- Instalar: `obs-studio`, `kdenlive`, `audacity`, `ffmpeg`, `vainfo`, `v4l-utils`, `intel-gpu-tools` (monitorar a GPU com `intel_gpu_top`).
- Validar: `vainfo`, codificação de teste `ffmpeg -vaapi_device /dev/dri/renderD128 … -c:v h264_vaapi`, formatos da webcam (`v4l2-ctl --list-formats-ext`).
- Configurar `git user.name/email` (perguntar ao usuário).

## Etapa 3 — OBS
- Perfil "TikTok vertical" (1080×1920, 30 fps, H.264 VAAPI) e perfil "Horizontal" opcional.
- Cenas: tela (PipeWire), webcam, tela+webcam, cena de "intervalo".
- Áudio: filtros de supressão de ruído (RNNoise), noise gate, compressor, limitador; teste de níveis.
- Gravação teste de 10 min observando quedas de quadro, temperatura e uso de CPU/GPU.

## Etapa 4 — Desempenho para gravação: **Modo Gravação** (escolhido em 2026-11-07)
Um comando liga e outro desliga; o estado anterior é salvo e restaurado exatamente.
- [ ] `modos/gravacao.sh liga|desliga|estado` + botão no widget (opcional, com aprovação)
- [ ] Ao ligar: perfil de energia "performance", pausar Baloo, "não perturbe", suspender efeitos pesados do KWin
- [ ] Verificações antes de gravar: espaço livre na pasta de gravação, VA-API respondendo, temperatura
- [ ] Abrir o OBS no perfil vertical (só depois que OBS/áudio forem liberados)
- [ ] Ao desligar: restaurar tudo; registrar a sessão em `~/.local/state/ukiyo/`
- [ ] Medir: gravação de teste com e sem o modo (quedas de quadro, CPU/GPU, temperatura) — depende da liberação do OBS

## Etapa 5 — Esteira de pós-produção e legendas (escolhidas em 2026-11-07)
Scripts em `producao/` (FFmpeg com VA-API; nada de x264), comando `tiktok`. Pastas em `~/Vídeos/TikTok/`.
**5a · Esteira**
- [x] `tiktok novo <nome>` (2026-11-07): pasta por vídeo a partir de modelo (`brutos/ audio/ legendas/ proxies/ export/ notas.md`)
- [x] `tiktok importar` (2026-11-07): copia clipes (celular/cartão/pasta) para `brutos/`, renomeando por data/hora, sem apagar a origem
- [x] Proxies na GPU no próprio Kdenlive + perfil padrão vertical 1080×1920/30 (2026-11-07) — conferir na primeira edição real
- [x] `tiktok silencios` (2026-11-07): remove pausas (FFmpeg silencedetect), gerando cópia + lista de cortes
- [x] `tiktok exportar` (2026-11-07): 1080×1920, H.264 VA-API, AAC, loudness −14 LUFS (2 passadas), checagem final do arquivo
- [x] `tiktok limpar [dias] [--apagar]` (2026-11-07)
**5c · Henshū 編集 — editor com chat (Claude/Codex)** (2026-11-07)
- [x] Formato `projeto.json`, prévia automática na GPU, linha do tempo, chat com escolha de agente, exportação final
- [x] Abrir o projeto no Kdenlive para ajuste fino (2026-11-07) — verificado no Kdenlive 24.12.3; guias dos capítulos não aparecem (limitação)
- [ ] Fonte pixel sem "ū" (DotGothic16 não tem o caractere): trocar por fonte com cobertura ou avisar
**5b · Legendas automáticas** (2026-11-07, dentro do Henshū)
- [x] Transcrição local (faster-whisper small, sem internet) — `henshu-transcrever` / botão Transcrever
- [x] Legendas estilo TikTok (frases, karaokê, pixel), revisão manual na janela, queimadas no export
- [x] Exportar `.srt` e capítulos do YouTube (capítulos também embutidos no MP4)
**5d · Henshū v2** (2026-11-07)
- [x] Predefinições vertical 9:16 e horizontal 16:9; reenquadrar (preencher + foco); velocidade; transições fade/dissolver

## Etapa 6 — Identidade visual japonesa pixel art/8-bit (em andamento)
- [x] **Backup antes do refino** (2026-11-07): projeto e recursos/configurações visuais, arquivos conferidos e SHA-256.
- [x] **Refino dos cinco wallpapers** (2026-11-07): propostas image_gen e comparação em `docs/visual/refino-2026-11-07/`; cinco aprovados, instalados e disponíveis na troca de temas.
Direção: `docs/visual/direcao-artistica.md`. Tema em `themes/washi/`.
- [x] Estado visual inicial + backup; direção artística; prévia (`themes/washi/preview/proposta.html`)
- [x] **V1 · Desktop** (2026-11-06): Washi, barra superior + dock, 一二三四, papel de parede, efeitos leves — validado por captura
- [x] **V2 · Janelas** (2026-11-06): Breeze recolorido, sombra curta, contorno nítido; títulos DotGothic16 — conferidos após novo login
- [x] **Papel de parede v2** (2026-11-06): céu e água mais calmos, reflexo em faixas — aplicado (v1 preservada)
- [x] **V2b · Decoração Washi Pixel** (2026-11-06): Aurorae próprio, sem sombra — aplicado e conferido
- [ ] V2c · (opcional) testar sombra dura deslocada; manter só se não atrapalhar redimensionar/encaixar
- [x] **V3 · Ícones e cursor** (2026-11-06): `washi-pixel` (fallback Breeze) e `washi-cursor` 32 px — validados em Dolphin, Konsole, menu e dock
- [x] **V4 · Produção em Sumi** (2026-11-06): Konsole e Kdenlive com a Sumi exata; Audacity com tema dark + GTK Breeze-Dark via lançador próprio (limitação registrada) — capturas dos três apps feitas
- [ ] OBS em Sumi — só com autorização (OBS pausado)
- [ ] Troca suave: cortina removida a pedido; o redesenho do KDE (~2 s) continua — sem solução nativa para fade instantâneo
- [x] **Troca de temas otimizada** (2026-11-07): pré-carregamento no login (`modos/instalar-temas.sh`) e `modos/trocar-tema.sh` (~0,8 s, antes ~8 s)
- [x] **Papéis de parede "Ma Pixel 間"** (2026-11-07): os 5 temas revisitados (filosofia em `docs/visual/filosofia-papeis-de-parede.md`, geradores com Pillow/NumPy em `.venv`) — ativados; login SDDM não alterado
- [x] **Tema Touge 峠** (2026-11-07): drift na montanha, racing claro em `themes/touge/`; `modos/modo-touge.sh` e botão no widget
- [x] **Tema Neon Tokyo** (2026-11-07): cyberpunk magenta/ciano em `themes/neontokyo/`; `modos/modo-neontokyo.sh` e botão no widget
- [x] **Tema Mary's** (2026-11-07): kawaii rosa/creme com gatinhos em `themes/marys/`; `modos/modo-marys.sh` e botão no widget — capturas reais feitas
- [x] **Modo escuro Yoru** (2026-11-06): tema separado em `themes/yoru/`, troca por `modos/modo-escuro.sh` / `modos/modo-claro.sh`; modo claro salvo em `modos/claro/`
- [x] **Widget Tela Washi** (2026-11-06): brilho + saturação na barra superior — instalado; efeito da saturação a confirmar visualmente
- [x] **V5a · Bloqueio** (2026-11-06): papel de parede v2 — aplicado
- [ ] V5b · Login (SDDM) com desfoque do Breeze — pronto; instalar com sudo e **validar num logout real**
Itens originais:
- Paleta e tipografia (fonte pixel apenas em títulos/painel; fonte legível na interface e nos editores).
- Esquema de cores Plasma, decoração de janelas, ícones, cursor, papel de parede.
- Tela de bloqueio e tema SDDM (login) — exige sudo; backup de `/etc/sddm.conf.d`.
- Manter Kdenlive/OBS com tema escuro neutro para não distorcer a percepção de cor.
- Tudo empacotado em `themes/` com script de instalação e de reversão.

## Etapa 7 — Manutenção
- [x] **Identidade Ukiyo 浮世 + repositório público** (2026-11-07): renomeação completa, README/instalação/licenças/segurança, capturas limpas
- [x] **Projeto multiagente** (2026-11-07): `AGENTS.md` (regras únicas, Codex/Claude), `docs/estado-atual.md` (passagem de bastão), registro de temas `modos/temas.conf`, `scripts/preparar-ambiente.sh`
- Script de backup das configurações (OBS, Kdenlive, Plasma).
- Checklist pós-atualização do Debian.

## Apresentação da distro — pedido pontual (2026-11-07)
- [x] Capturas limpas dos cinco desktops e montagem de 48 s, comparando wallpapers antigos e refinados.
- [x] Renderizador reproduzível com trilha original em `producao/apresentacao/`; saída H.264 VA-API Full HD.

## Spotify e controle de música — pedido pontual (2026-11-07)
- [x] Spotify oficial instalado pelo usuário; script e backup APT documentados.
- [x] Widget com capa, anterior/tocar/pausar/próxima e volume exclusivo; prévia e testes isolados.
- [x] Aprovação visual e ativação na barra superior, sem reiniciar painel (widget 55).
- [ ] Validar com Spotify aberto/autenticado e música escolhida pelo usuário.

## Refino dos ícones dos aplicativos — pedido pontual (2026-11-07)
- [x] Revisão, backup, SVGs em separado e comparação antes/depois nos cinco temas.
- [x] Escopo dock inferior aprovado; cinco conjuntos instalados e integrados ao pré-carregamento; Yoru aplicado.

## Redesenho dos ícones v2 — correção solicitada (2026-11-07)
- [x] Nova proposta com redesenho dos objetos, cores e volumes; comparação com o conjunto ativo.
- [x] V2 aprovado e ativado nos cinco temas; Washi ativo aplicado, versões anteriores preservadas.
