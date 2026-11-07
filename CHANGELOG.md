# Mudanças

O diário detalhado de cada alteração (com backup e como desfazer) está em [`docs/mudancas.md`](docs/mudancas.md).

## 1.0.0 — 2026-11-07 · primeira versão pública

- **Identidade:** o projeto passa a se chamar **Ukiyo 浮世** (antes "studio-linux"), com widgets `org.ukiyo.*`,
  estado em `~/.local/state/ukiyo` e dados em `~/.local/share/ukiyo`.
- **Cinco temas** trocáveis em menos de 1 s: Washi (claro), Yoru (escuro), Mary's (kawaii), Neon Tokyo (cyberpunk)
  e Touge (montanha), com registro único `modos/temas.conf`.
- **Pixel art por código:** papéis de parede da série *Ma Pixel 間*, ícones, cursor, decorações Aurorae, esquemas de
  cores, perfis ICC de saturação e tema de login; refinos dos papéis de parede com geração de imagem por IA.
- **Widgets:** Tela (brilho, saturação e troca de tema) e Spotify (capa, controles e volume próprio).
- **Produção:** esteira `tiktok` (novo, importar, cortar pausas, exportar −14 LUFS), Kdenlive com proxies na GPU e
  OBS com perfil vertical VA-API.
- **Henshū 編集:** editor com prévia ao vivo e chat com Claude ou Codex; formatos vertical e horizontal, reenquadrar,
  velocidade, fade e dissolver, transcrição local (faster-whisper), legendas em três estilos, SRT e capítulos.
- **Compartilhamento:** README, guia de instalação, licenças (GPL-3.0-or-later, CC BY-SA 4.0, LGPL-2.0-or-later no
  tema de login derivado do Breeze), `SECURITY.md` e `scripts/instalar-comandos.sh`.
