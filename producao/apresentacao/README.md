# Apresentação do Ukiyo

Filme de 48 segundos, 1920×1080, 30 fps, H.264 VA-API + AAC.
Saída: `renders/apresentacao-2026-11-07/Ukiyo-apresentacao-48s.mp4` (fora do Git).

## Direção

Uma apresentação tranquila da distro pessoal: origem e refino dos cinco wallpapers,
seguidos de capturas reais do KDE, com enquadramentos em movimento. Tipografia pixel
nos títulos; texto de apoio legível. Sem gravação de microfone, áudio do sistema ou OBS.
A trilha instrumental foi composta e sintetizada offline pelo próprio script, sem samples externos.

## Roteiro

- 0–5 s: identidade Ukiyo e Debian/KDE.
- 5–30 s: Washi, Yoru, Mary's, Neon Tokyo e Touge; passagem da arte antiga à nova.
- 30–42,5 s: os cinco desktops reais, com painel, dock e ícones, em cartões animados.
- 42,5–48 s: encerramento.

## Reprodução

As capturas pessoais ficam em `docs/visual/capturas/apresentacao-2026-11-07/`, ignoradas pelo Git.
O vídeo utiliza somente as tomadas limpas conferidas, sem janelas com conversas.

Para renderizar novamente, com as capturas locais disponíveis:

```bash
.venv/bin/python producao/apresentacao/renderizar.py
```

Requer Pillow/NumPy do ambiente existente e acesso à GPU Intel em `/dev/dri/renderD128`.
O processamento dos frames ocorre na CPU; a escala final e a codificação H.264 usam VA-API.
`capturar-desktop.py` muda de área de trabalho e alterna os temas: executar apenas com autorização.
Ao terminar, restaura o tema, a área de trabalho e o estado Mostrar desktop anteriores.
Não altera as cores dos aplicativos nem instala software.
