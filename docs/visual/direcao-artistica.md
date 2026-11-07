# Direção artística — tema "Washi" (decidida em 2026-11-06)

| Decisão | Escolha |
|---|---|
| Cenário | Japão tradicional: montanha nevada, torii no lago, sakura, lanternas de pedra, pagode |
| Momento | Entardecer dourado, papel de parede estático |
| Paleta do sistema | **Washi**: #F2EBDD fundo · #E4D9C4 superfícies · #2B2A28 texto · #C8102E seleção · #4F6B3A links · #D9A441 só decoração |
| Paleta de produção | **Sumi** (OBS, Kdenlive, Audacity, Konsole): #24221F · #302D29 · #EDE6D6 texto · #B3263B seleção · #8FB36F foco · #E3B65A avisos |
| Layout | Barra fina no topo (lançador, menu global, áreas de trabalho 一二三四, bandeja, relógio) + dock inferior centralizada |
| Fonte pixel | DotGothic16 (`fonts-dotgothic16`) só em relógio, rótulos e títulos de janela |
| Fontes legíveis | Noto Sans / Noto Sans CJK JP (interface), DejaVu Sans Mono (terminal) |

Contraste (WCAG): texto principal ≥ 12:1; seleção e links ≥ 4,5:1 — ver `themes/washi/preview/contraste.txt`.

Prévia (conceito): `themes/washi/preview/proposta.html` e `maquete-desktop.png`.
A prévia carrega a DotGothic16 do Google Fonts só para exibir a maquete; o tema real usará o pacote Debian.

Ativos finais gerados por código (reprodutíveis):
- `themes/washi/tools/gerar-papel-de-parede.py` → `themes/washi/wallpaper/`
- `themes/washi/tools/gerar-icones.py` → `themes/washi/icons-src/` (ícones originais 16×16, metáforas genéricas, sem logos de marcas)
