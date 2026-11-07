# Ukiyo 浮世 — instruções para agentes (Codex, Claude Code e outros)

Fonte única de regras do projeto. `CLAUDE.md` só importa este arquivo. **Antes de qualquer tarefa, leia também
`docs/estado-atual.md`** (onde o trabalho parou, o que está pausado, o que o usuário já recusou).

Ambiente de produção de vídeo para TikTok neste notebook, com identidade visual japonesa em pixel art/8-bit.
Idioma de trabalho: **português brasileiro**. Perguntas ao usuário: **sempre múltipla escolha** (2–4 opções, a
recomendada primeiro, marcada "(Recomendado)").

## Máquina (detalhes em `docs/estado-inicial.md`)
- Dell Latitude 3540, i5-1335U (15 W, 2P+8E), 16 GB RAM, NVMe 512 GB.
- Intel UHD (Raptor Lake, driver `i915`), VA-API **iHD**: codifica H.264/HEVC/VP9 em hardware (low-power). Sem AV1.
- Debian 13 (trixie), KDE Plasma 6.3 em **Wayland**, SDDM, PipeWire + WirePlumber. Tela 1920×1080@60, escala 100%.

## Objetivos
- Ferramentas: OBS (central), Kdenlive, Audacity, FFmpeg. IA principalmente via serviços na nuvem.
- Visual próprio: painéis, ícones, janelas, papel de parede, login (SDDM) e bloqueio.
- **Legibilidade nos editores e desempenho durante gravações têm prioridade sobre a estética.**

## Regras (obrigatórias)
- Trabalhar como o usuário comum da máquina (nunca root). `sudo` só quando indispensável; **nunca pedir, exibir ou guardar a senha**. O agente
  não roda sudo: entrega o comando pronto e o usuário o executa no próprio terminal.
- **Backup antes de alterar qualquer configuração**, em `backups/<AAAA-MM-DD>-<etapa>/` (fora do git).
- Registrar toda mudança em `docs/mudancas.md`: o que mudou, onde está o backup, como desfazer.
- Edições em dotfiles: blocos com marcadores `# >>> ukiyo: <nome> >>>` / `# <<< … <<<`, idempotentes.
- Nunca gravar senhas, tokens, chaves de API ou PSK de Wi-Fi no repositório ou em docs.
- Não desativar proteções (sandbox, prompts de permissão, AppArmor, polkit). Nunca contornar a tela de bloqueio.
- **Rede:** o NetworkManager gerencia o Wi-Fi. Não mexer em `/etc/network/interfaces` nem em `/etc/network/interfaces.backup`.
- Codificação de vídeo sempre na GPU (VA-API); evitar x264/CPU em gravação.
- Seguir `docs/plano.md`, uma etapa por vez, e marcar o progresso nele.
- Não fazer commits sem o usuário pedir.
- **Ao terminar uma sessão de trabalho, atualizar `docs/estado-atual.md`** (o que foi feito, o que ficou pendente),
  para que o próximo agente continue sem perder contexto.

## Repositório público
- O projeto é publicado no GitHub. **Antes de qualquer commit**, conferir que nada pessoal entra: sem senhas/tokens,
  sem caminhos com o nome do usuário em código (use `$HOME`/caminho do próprio script), sem capturas com janelas ou
  notificações pessoais, sem retratos de configuração. Autor dos commits: e-mail *noreply* do GitHub.
- Identificadores: widgets `org.ukiyo.*`, estado `~/.local/state/ukiyo`, dados `~/.local/share/ukiyo`, marcadores
  `# >>> ukiyo: <nome> >>>`. O nome antigo (studio-linux) só existe como link de compatibilidade nesta máquina.

## Como o usuário quer que se trabalhe (aprendido nas sessões)
- **Fazer só o que foi pedido.** Nada de recursos extras não solicitados (ex.: uma "tela de carregamento" na troca de
  tema foi rejeitada com firmeza). Na dúvida, perguntar em múltipla escolha.
- Não repetir testes invasivos sem necessidade; não abrir ou focar janelas de teste enquanto o usuário usa a máquina
  (teclas digitadas podem cair nelas).
- Antes de **ativar** algo visível (papel de parede, tema, widget), gerar como arquivo novo, mostrar uma comparação
  e pedir aprovação. Versões anteriores são sempre preservadas.
- **OBS e áudio estão pausados** até o microfone definitivo chegar: nenhuma gravação e nenhum ajuste de áudio.
- **A troca de tema NÃO muda as cores dos apps** (fixas em Yoru); muda só papel de parede, ícones, decoração e bloqueio.
  Motivo: mudar o esquema de cores faz o KDE travar ~2 s.
- Capturas de tela podem ter conteúdo pessoal: ficam em `docs/visual/capturas/` (fora do git) e não são publicadas.

## Comandos principais
| Tarefa | Comando |
|---|---|
| Preparar o ambiente Python (Pillow/NumPy/faster-whisper em `.venv`) | `scripts/preparar-ambiente.sh` (precisa de `python3-venv`) |
| Ligar os comandos `tiktok`/`henshu`/`henshu-transcrever` e o atalho do Henshū | `scripts/instalar-comandos.sh [--remover]` |
| Trocar de tema | `modos/trocar-tema.sh <id>` ou `modos/modo-<id>.sh` (ids em `modos/temas.conf`) |
| Pré-carregar/instalar recursos de todos os temas | `modos/instalar-temas.sh` (roda sozinho no login com `--se-necessario`) |
| Redesenhar os papéis de parede | `scripts/gerar-papeis-de-parede.sh [id…]` (só gera PNGs; depois `modos/instalar-temas.sh`) |
| Esteira de pós-produção (pasta por vídeo, importar, cortar pausas, exportar −14 LUFS) | `tiktok <novo\|importar\|silencios\|exportar\|limpar\|onde>` (`producao/tiktok.sh`) |
| Editor com chat (Claude/Codex editam `projeto.json`, prévia ao vivo) | `henshu [pasta-do-vídeo]` (`editor/`) |
| Gerar/abrir o projeto no Kdenlive (ajuste fino) | botão "Abrir no Kdenlive" ou `python3 -m henshu.kdenlive <pasta>` (em `editor/`) |
| Transcrever falas e gerar legendas (local, faster-whisper) | `henshu-transcrever [pasta] [--so-legendas]` |
| Medir travamento do KDE durante um comando | `modos/medir-travamento.py "comando"` |
| Capacidades VA-API | `scripts/va-probe.py` |

Os geradores de ícones, decoração e esquemas usam **só a biblioteca padrão** (`python3 -I`). Os papéis de parede
da série "Ma Pixel 間" usam `.venv/bin/python` (Pillow + NumPy) e a base `scripts/pixelarte.py`. São
determinísticos: rodar de novo produz o mesmo arquivo.

## Estrutura
- `README.md` (apresentação pública), `docs/instalacao.md` (guia), `CHANGELOG.md`, `SECURITY.md`, `LICENSE` + `LICENSES/`
- `docs/imagens/`: banner, capturas dos temas e do Henshū usadas no README (capturas feitas só em área de trabalho vazia)
- `docs/estado-atual.md`: **passagem de bastão**, com o estado atual e as pendências (ler primeiro)
- `docs/plano.md`: etapas e progresso · `docs/mudancas.md`: registro de mudanças, backups e reversão
- `docs/estado-inicial.md`: inventário técnico · `docs/obs-recomendacao.md`: configuração de gravação
- `docs/visual/`: direção artística (`direcao-artistica.md`), filosofia dos papéis de parede (`filosofia-papeis-de-parede.md`)
- `modos/temas.conf`: **registro único dos temas** (lido por `trocar-tema.sh`, `instalar-temas.sh` e `gerar-papeis-de-parede.sh`)
- `modos/`: troca de tema, pré-carregamento, atalhos `modo-*.sh` e o retrato salvo do modo claro (`modos/claro/`)
- `producao/`: esteira de vídeo (`tiktok.sh`, link em `~/.local/bin/tiktok`); vídeos em `~/Vídeos/TikTok/<data>_<nome>/`
- `editor/`: Henshū 編集 (PySide6 do Debian): `henshu/projeto.py` (formato), `render.py` (FFmpeg/VA-API), `agentes.py` (ponte `claude -p` / `codex exec --json`), `legendas.py` (ASS/SRT/capítulos), `kdenlive.py` (exporta `.kdenlive`), `transcrever.py` (faster-whisper, roda no `.venv`), `app.py` (janela)
- `scripts/`: utilitários (`pixelarte.py`, `va-probe.py`, preparação do ambiente, geração dos papéis de parede)
- `themes/washi/`: tema base (claro), com geradores (`tools/`), prévias (`preview/`), scripts de aplicar/restaurar
  (`scripts/`), widget "Tela" (`tools/gerar-widget-tela.py`) e tema SDDM
- `themes/yoru/` (escuro), `themes/marys/` (kawaii), `themes/neontokyo/` (cyberpunk), `themes/touge/` (drift):
  **cada tema é separado**; não alterar arquivos de um tema para outro (os geradores reaproveitam os do Washi por
  importação, sem modificá-los)
- `config/obs/`: perfis/cenas do OBS · `.venv/`: ambiente Python (fora do git) · `backups/`: cópias (fora do git)

## Adicionar um tema
1. Criar `themes/<pasta>/tools/` com `gerar-esquema-<pasta>.py`, `gerar-tema-icones-<pasta>.py`,
   `gerar-decoracao-<pasta>.py` (copiar o padrão de `themes/touge/tools/`) e um gerador de papel de parede que use
   `scripts/pixelarte.py`.
2. Acrescentar **uma linha** em `modos/temas.conf`.
3. Criar o atalho `modos/modo-<id>.sh` (mesmo conteúdo dos outros, trocando o id).
4. `scripts/gerar-papeis-de-parede.sh <id>` e depois `modos/instalar-temas.sh`.
5. (Opcional) Botão no widget: os botões ficam em `themes/washi/tools/gerar-widget-tela.py`. Reinstalar com
   `themes/washi/scripts/instalar-widget-tela.sh`, que reinicia o painel e por isso pede aprovação.
6. Backup, registro em `docs/mudancas.md`, marcação em `docs/plano.md`, atualização de `docs/estado-atual.md`.

## Particularidades técnicas do KDE (evitam retrabalho)
- Ícones: `kwriteconfig6 --notify --file kdeglobals --group Icons --key Theme <tema>` + sinal D-Bus
  `/KIconLoader iconChanged` (~35 ms). Não usar `plasma-changeicons` (~2 s). O `index.theme` precisa de
  `FollowsColorScheme=true`.
- Decoração Aurorae: o KWin guarda o tema em cache; para recarregar o mesmo tema alterado, alternar para Breeze e voltar.
- Papel de parede: usar **pacotes com nome novo** (ex.: `Yoru-v2`) em vez de sobrescrever a imagem de um pacote já
  aplicado (o Plasma guarda cache pelo caminho).
- Saturação da tela: perfis ICC gerados e aplicados com `kscreen-doctor output.eDP-1.iccprofile.<arquivo>` (capturas
  de tela não mostram o efeito).
- Fonte nova usada pelo KWin (títulos) só vale após novo login.
