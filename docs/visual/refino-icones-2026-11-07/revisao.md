# Refino dos ícones dos aplicativos — proposta

Escopo aprovado pelo usuário: dock inferior, inicialmente com os sete
aplicativos fixados e Spotify. Não altera lançadores fixados, ordem, painel ou bandeja de rede/som/bateria.
O Spotify ganha somente o recurso visual: não é fixado automaticamente na dock.

## Revisão

Os ícones anteriores usam 16×16 com corpos majoritariamente retangulares e pouca margem em alguns desenhos.
A borda extra dos temas escuros pode ocupar o limite da grade. O tamanho percebido varia entre ícones e o
Spotify usa o ícone original, fora da família. O Audacity e o Kdenlive se parecem com outros cartões claros.

## Proposta

Grade 24×24, margem transparente e contorno fino. Paleta curta, luz discreta, silhuetas reconhecíveis:
pasta aberta, globo, terminal, câmera de gravação, claquete inclinada, fones com onda, engrenagem e Spotify pixel.
Os cinco temas mantêm variações próprias, com cores menos estridentes. SVGs nítidos, sem bitmap gerado por IA.

Saídas separadas em `themes/<tema>/icons-refino/<tema>-pixel-refino/`, com aliases dos aplicativos.
Os temas propostos herdam os atuais: pastas, lixeira e ícones simbólicos permanecem disponíveis pelo fallback.
Não foram gerados ícones Henshū separados: seu lançador atual usa `Icon=kdenlive`.

## Prévia

- `comparacao.html`: antes/depois de cada tema, em 96 e 48 px.
- `cinco-temas.png`: conjunto proposto nos cinco temas.
- `yoru-comparacao.png`: comparação do tema escuro atual.

As imagens mostram os próprios SVGs gerados, e não uma reconstrução ilustrativa.
As versões antigas do Spotify nas comparações usam o PNG oficial instalado localmente.

## Reprodução

```bash
python3 -I scripts/gerar-icones-refinados.py
.venv/bin/python scripts/previa-icones-refinados.py
```

O gerador usa somente a biblioteca padrão. Pillow é usado apenas para as pranchas de revisão.
Nenhuma dependência nova, instalação, troca de tema ou janela de teste foi necessária.
Aprovação recebida: conjuntos instalados e integrados ao pré-carregamento; Yoru refinado aplicado.
As pranchas preservam a comparação produzida antes da ativação.
