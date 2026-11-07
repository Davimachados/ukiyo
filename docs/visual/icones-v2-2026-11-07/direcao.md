# Redesenho dos ícones — v2

O usuário considerou o primeiro refino conservador demais, percebido como contorno acrescentado.
A nova proposta redesenha cada objeto e trabalha proporções, cores próprias e planos de luz.

- Dolphin: pasta azul aberta, folhas sobrepostas e dobra frontal.
- Firefox: raposa em tons de brasa envolvendo um globo azul.
- Konsole: terminal de bancada, vidro índigo e pequenos controles de cobre.
- OBS: disco fosco com três pás curvas em marfim.
- Kdenlive: claquete aberta, reprodução e duas faixas de timeline.
- Audacity: fones dourados, almofadas azuis e onda quente no centro.
- Configurações: engrenagem chanfrada, metal em três planos e cubo âmbar.
- Spotify: disco verde, luz lateral contida e três ondas separadas.

Grade 48×48; SVGs gerados com biblioteca padrão por `scripts/gerar-icones-v2.py`.
Cores dos aplicativos permanecem reconhecíveis entre temas; os cinco temas variam pequenos reflexos.
Não há aplicação automática de contorno externo. Cada desenho controla suas bordas e seus planos.
SVGs em `themes/<tema>/icons-v2/<tema>-pixel-art-v2/`, com 24 aliases por tema e fallback ao tema-base.

Pranchas geradas dos arquivos reais por `scripts/previa-icones-v2.py` (Pillow apenas para documentação).
`comparacao.html` mostra ativo/v2 nos cinco temas; `dock-48px.png` mostra a nova proposta em tamanho real.
As versões atuais e os geradores anteriores são preservados. V2 aprovado e instalado em 2026-11-07. As comparações preservam o registro anterior à ativação.
