# Vídeo promocional do Ukiyo 浮世

Filme de 55 s em 1920×1080/30 fps, todo gerado por código: motion graphics em camadas sobre capturas reais do
sistema, com trilha chiptune original. A saída fica em `renders/promo/` (fora do git).

| Arquivo | O que faz |
|---|---|
| `trilha.py` | trilha original (96 BPM, escala japonesa *in-sen*), sintetizada com NumPy, sem samples |
| `capturar.sh` | captura telas dos cinco temas e janelas de demonstração na área de trabalho 4 (só janelas próprias) |
| `kw.py` | utilitário de janelas via script do KWin (trocar de área, posicionar janelas por PID) |
| `renderizar.py` | renderiza o vídeo: papel de parede em 2,5D, partículas, kanji em pixel, cartões 3D, tipografia e transições |

## Roteiro (compasso = 2,5 s)

| Tempo | Cena |
|---|---|
| 0–5 s | abertura: 浮世 em dissolve de pixels (Bayer), UKIYO, "Debian + KDE Plasma, redesenhado em pixel art" |
| 5–30 s | os cinco temas: paralaxe 2,5D do papel de parede, partículas do tema e o desktop real em cartão 3D |
| 30–35 s | troca de tema em menos de 1 s: widget Tela e desktops alternando |
| 35–42,5 s | Henshū: a janela real, aproximação no chat e um celular tocando o vídeo exportado (legenda karaokê) |
| 42,5–47,5 s | estúdio na GPU: Kdenlive e a esteira `tiktok` |
| 47,5–55 s | encerramento: leque 3D dos desktops, licenças e o endereço do repositório |

## Como refazer

```bash
.venv/bin/python producao/promo/trilha.py renders/promo/trilha.wav
producao/promo/capturar.sh renders/promo/insumos <pasta-de-um-vídeo-do-henshu>   # área 4 vazia!
.venv/bin/python producao/promo/renderizar.py renders/promo/insumos renders/promo/ukiyo-promo.mp4 --trilha renders/promo/trilha.wav
.venv/bin/python producao/promo/renderizar.py renders/promo/insumos renders/promo/q --quadros 3,12.5,40   # só conferir quadros
```

A codificação é feita na GPU (`h264_vaapi`). Os textos são públicos e neutros (sem primeira pessoa), para uso no
repositório. Fontes: DotGothic16 e Noto Sans CJK (pacotes Debian), Outfit, Instrument Sans e DM Mono (OFL).
