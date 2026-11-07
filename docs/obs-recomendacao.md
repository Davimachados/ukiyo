# Configuração inicial recomendada do OBS

Baseada no inventário de `docs/estado-inicial.md`: i5-1335U (15 W), Intel UHD (Xe-LP) com
VA-API iHD codificando H.264/HEVC em low-power, sessão Wayland, tela 1920×1080@60, PipeWire.
A validar na Etapa 3 com gravações de teste.

## Princípio
A CPU de 15 W não deve codificar vídeo (x264 causaria quedas de quadro e aquecimento).
Toda a codificação vai para a GPU via VA-API.

## Vídeo
| Ajuste | Valor |
|---|---|
| Resolução base (canvas) | **1080×1920** (vertical, TikTok) |
| Resolução de saída | 1080×1920 (sem reescala) |
| FPS | **30** (60 só para jogo/movimento rápido, após teste) |
| Filtro de escala | Bilinear ou Bicúbico (Lanczos gasta mais GPU) |

A tela é 16:9; na cena vertical, recorte a região de interesse da captura ou combine tela + webcam empilhadas.

## Gravação (Saída → Avançado → Gravação)
| Ajuste | Valor |
|---|---|
| Codificador | **FFmpeg VAAPI H.264** (ou "H.264 VAAPI" nativo), dispositivo `/dev/dri/renderD128` |
| Perfil | High |
| Controle de taxa | **CQP 20** (qualidade constante) — alternativa: CBR 20–25 Mbps |
| Intervalo de keyframe | 2 s |
| Formato | **MKV** (sobrevive a travamentos) → remuxar para MP4 no OBS antes de editar |
| Pasta | SSD local, ex.: `~/Videos/TikTok/brutos` |

HEVC VAAPI também funciona e gera arquivos menores, mas H.264 é mais leve para editar no Kdenlive; comece com H.264.

## Captura no Wayland
- Tela/janela: **Captura de tela (PipeWire)** — via portal `xdg-desktop-portal-kde`.
- Webcam: fonte **Dispositivo de captura de vídeo (V4L2)**, `Integrated_Webcam_FHD` em 1920×1080, preferindo formato MJPEG se oferecido (confirmar com `v4l2-ctl` na Etapa 2).

## Áudio
| Ajuste | Valor |
|---|---|
| Taxa | 48 kHz, estéreo |
| Codificador | AAC 192–320 kbps |
| Microfone | Digital Microphone (interno); headset P2 como alternativa melhor |
| Filtros do mic | Supressão de ruído (RNNoise) → Noise gate → Compressor → Limitador (−1 dB) |

## Desempenho
- Mudar o perfil de energia para **Desempenho** enquanto grava (hoje: `balanced`); manter na tomada.
- Fechar navegador/abas pesadas durante a gravação.
- Em Configurações → Avançado: prioridade do processo "Acima do normal".
- Conferir no OBS: Estatísticas → quadros perdidos por codificação/renderização devem ficar em 0%.
