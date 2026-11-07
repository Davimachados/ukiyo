# Estado visual inicial — 2026-11-06

Backup completo: `backups/2026-11-06-etapa3-visual/` (configs + `SHA256SUMS` + captura `antes-desktop.png`,
mantida fora do git por conter conteúdo pessoal).

| Elemento | Valor atual |
|---|---|
| Look-and-feel global | `org.debian.desktop` (Breeze, edição Debian) |
| Esquema de cores | BreezeLight (apps) + tema Plasma `breeze-dark` (painel) |
| Estilo de widgets | Breeze |
| Decoração de janelas | `org.kde.breeze` / Breeze, botões padrão à direita |
| Ícones | breeze |
| Cursor | breeze_cursors, tamanho padrão |
| Fontes | padrão: Noto Sans (interface), DejaVu Sans Mono (monoespaçada) |
| Fontes pixel instaladas | nenhuma |
| Fontes japonesas | Noto Sans CJK (instalada) |
| Painel | 1 painel inferior, flutuante, 44 px: Kickoff, pager, gerenciador de tarefas (icontasks), bandeja, relógio digital, mostrar área de trabalho |
| Área de trabalho | Folder View, papel de parede padrão Debian |
| Splash | `org.debian.desktop` |
| Bloqueio de tela | padrão (sem `kscreenlockerrc`) |
| Konsole | perfil padrão, sem perfis em `~/.local/share/konsole` |
| GTK | arquivos `gtk-3.0`, `gtk-4.0`, `gtkrc*` gerados pelo Plasma |
| Telas | 1920×1080 @ 60 Hz, escala 100% |

Arquivos **inexistentes** antes da etapa visual (desfazer = apagar se forem criados):
`~/.config/plasmarc`, `kcminputrc`, `ksplashrc`, `kscreenlockerrc`, `breezerc`,
`~/.local/share/{color-schemes,plasma,icons}`, `~/.icons`.
