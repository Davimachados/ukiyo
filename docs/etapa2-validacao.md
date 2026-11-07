# Etapa 2 — Validação de ferramentas, aceleração e captura (2026-11-06)

Pacotes instalados do Debian (177 novos, 0 removidos — comparação em `backups/2026-11-06-etapa2/`):
OBS 30.2.3, Kdenlive 24.12.3, Audacity 3.7.3, FFmpeg 7.1.5, vainfo 2.22, v4l-utils 1.30.1, intel-gpu-tools 2.0.

## 1. Aceleração de vídeo: anunciado × funcionando

"Anunciado" = `vainfo` (`docs/testes/vainfo.txt`). "Testado" = `scripts/teste-codificadores.sh`:
10 s sintéticos 1080×1920@30 → codificar → decodificar de volta, contar quadros e erros
(`docs/testes/codificadores.txt`).

| Codificador | Driver anuncia | Teste real | Observação |
|---|---|---|---|
| **H.264 VAAPI** (High) | sim (EncSliceLP) | **OK** — 300/300 quadros, 0 erros, 1,07 s p/ 10 s (~9× tempo real) | **Escolhido** |
| HEVC VAAPI (Main) | sim | OK — 300/300, 0 erros, 0,95 s | arquivos ~28% menores que H.264 no mesmo QP |
| HEVC VAAPI (Main10) | sim | OK — 300/300, 0 erros, 1,87 s | |
| VP9 VAAPI | sim | OK — 300/300, 0 erros | controle de qualidade pouco previsível (arquivo minúsculo com `global_quality 80`); não usar |
| AV1 VAAPI | **não** | FALHA ("Function not implemented") | hardware não tem codificador AV1 |
| H.264 QSV | (via oneVPL) | FALHA ("Error creating a MFX session: -9") | falta o runtime GPU do oneVPL (`libmfx-gen`); desnecessário — VAAPI cobre o mesmo hardware |
| x264 veryfast (CPU) | — | OK — 10,5 s de CPU p/ 10 s de vídeo (~1 núcleo inteiro), 1,43 s real | **viável como alternativa**, mais calor/consumo |
| x264 ultrafast (CPU) | — | OK — 4,7 s de CPU, arquivo 2,3× maior | |

Decodificação por hardware (VAAPI) de H.264 e HEVC: OK, ~0,2 s de CPU para 10 s de vídeo.

Linha de base: só gerar o vídeo sintético + converter RGB→NV12 na CPU custa ~2,5 s de CPU. Isso significa que
**o codificador por hardware em si praticamente não usa CPU**; o custo restante do teste é da fonte sintética.
No OBS a conversão de cor acontece na GPU.

## 2. OBS

Log de carregamento confirma: `FFmpeg VAAPI H264 encoding supported`, `HEVC supported`, `AV1 not supported`;
codificadores `ffmpeg_vaapi_tex` (H.264) e `hevc_ffmpeg_vaapi_tex` (zero-cópia, lê textura da GPU).
Plugins presentes: PipeWire (tela/janela), V4L2, PulseAudio, filtros incluindo **RNNoise**, Speex, noise gate,
compressor, limitador, expansor, EQ.

### Captura de tela (PipeWire, Wayland)
- Portal KDE pediu a tela uma vez; o OBS guardou o `RestoreToken` e nas execuções seguintes restaurou sem diálogo.
- Formato negociado: BGRA 1920×1080 com modificador DMA-BUF (`0x100000000000008`) → **sem cópia pela CPU**.

### Webcam (Integrated_Webcam_FHD)
| Formato | 1920×1080 | 1280×720 | 640×480 |
|---|---|---|---|
| MJPG | **30 fps** | 30 fps | 30 fps |
| YUYV | 5 fps | 10 fps | 30 fps |

- **Usar MJPG** para 1080p30. `exposure_dynamic_framerate=1`: em pouca luz a câmera pode baixar o fps — iluminar bem o rosto.
- `power_line_frequency=60 Hz` (correto para o Brasil, evita cintilação de lâmpadas).
- **Problema encontrado e corrigido:** com `auto_reset=true` o OBS reiniciava a câmera a cada 166 ms (5 quadros sem imagem),
  mas ela leva ~1 s para entregar o 1º quadro → laço infinito (287 reinícios em 78 s). Com `auto_reset=false` (padrão do OBS) inicia normalmente.

### Gravação de teste no OBS (cena "Vertical — Tela + Webcam", 20 s)
| Métrica | Resultado |
|---|---|
| Saída | H.264 High 1080×1920 30/1, AAC 48 kHz estéreo 192 kbps, MKV → remux automático para MP4 |
| Quadros | 905 gravados / 909 desenhados (diferença de 4–5 só no início/fim, igual em todos os testes; nenhum "lagged/skipped") |
| CPU do sistema | **~10%** dos 12 threads (processo OBS ≈ 63% de 1 núcleo, incluindo decodificação MJPEG da webcam) |
| GPU | até 800 MHz de 1250 MHz |
| Temperatura máx. | 59 °C (54 °C em repouso) |

`intel_gpu_top` exige CAP_PERFMON/root — não foi alterado; usar `sudo intel_gpu_top` quando quiser ver a ocupação dos motores.

## 3. Áudio

| Medida | Resultado |
|---|---|
| Áudio do sistema (monitor do alto-falante) | captura OK (silencioso no teste, nenhum app tocando) |
| Microfone digital, volume 100% | **saturando**: picos 0,0 dBFS, 750–860 amostras cortadas em 6 s, −9,4 LUFS |
| Causa | `Base Volume` do microfone = 46% (−20 dB) = ganho nominal; 100% somava ~+20 dB digitais |
| Ação | volume do microfone ajustado para **46%** (nominal) → pico −16 dBFS, RMS −33 dB, sem cortes |
| Ruído de fundo | energia concentrada em 40–200 Hz; há um ar-condicionado no ambiente (visível na webcam) — hipótese a confirmar com a amostra de voz |

**Filtros ainda não aplicados.** Próximo passo: amostra de voz crua (`scripts/gravar-amostra-voz.sh`),
análise de ruído/dinâmica e comparação A/B de filtros antes de configurá-los no OBS.

## Arquivos de teste preservados (`~/Vídeos/TikTok/testes/`)
- `teste-ffmpeg-webcam-h264vaapi-1080p30.mkv` — 8 s webcam MJPEG + mic, codificado com h264_vaapi (mic ainda em 100%).
- `teste-obs-tela+webcam-ANTES-ajuste-mic.mkv` — gravação do OBS na cena vertical (áudio saturado, para comparação).
