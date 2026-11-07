# Estado inicial do sistema — 2026-11-06

Inventário coletado com o usuário comum (sem sudo). Nenhum segredo registrado.

## Máquina

| Item | Valor |
|---|---|
| Modelo | Dell Latitude 3540 |
| CPU | Intel Core i5-1335U (13ª ger., Raptor Lake-U, 15 W) — 10 núcleos (2 P + 8 E), 12 threads, até 4,6 GHz |
| Escalonamento de CPU | `intel_pstate`, governor `powersave`, perfil de energia `balanced` |
| RAM | 16 GB (≈15 GiB utilizáveis) |
| Swap | partição de ≈15 GiB (`/dev/nvme0n1p3`), `vm.swappiness=60` |
| Disco | SK hynix BC901 NVMe 512 GB — `/` em `nvme0n1p2`, 452 GB, ≈6 GB usados |
| Webcam | Integrated_Webcam_FHD (`/dev/video0`, `/dev/video1`, V4L2) |
| Rede | Wi-Fi Intel CNVi (Raptor Lake PCH) `wlp0s20f3` — conectado via NetworkManager; Ethernet Realtek RTL8111 `enp2s0` (sem cabo) |

## Sistema

| Item | Valor |
|---|---|
| Distribuição | Debian 13.7 (trixie) |
| Kernel | 6.12.115+deb13.1-amd64 |
| Desktop | KDE Plasma 6.3.6 |
| Sessão gráfica | **Wayland** (`kwin_wayland`), XWayland em `:1` |
| Login | SDDM 0.21 (tema Breeze/Debian Breeze) |
| Portais | `xdg-desktop-portal` 1.20.3 + `-kde` 6.3.5 + `-gtk` (captura de tela via PipeWire disponível) |
| Repositórios | `trixie main non-free-firmware`, `trixie-security`, `trixie-updates` (sem `contrib`/`non-free`) |

## Tela

- Painel interno `eDP-1`: **1920×1080 @ 60 Hz**, escala 1 (100%), sem VRR/HDR, perfil sRGB.

## GPU e vídeo

- Intel UHD Graphics (Raptor Lake-P, Xe-LP), PCI `8086:a721`, driver de kernel **`i915`** (módulo `xe` também disponível, não em uso).
- Firmware: `firmware-intel-graphics` 20250410 (GuC/HuC/DMC adlp presentes).
- Mesa 25.0.7; VA-API 1.22 (`libva2` 2.22).
- Driver VA-API ativo: **iHD** (`intel-media-va-driver` 25.2.3, versão livre do Debian). `i965-va-driver` também instalado (legado, não usar).

### Codificação/decodificação por hardware (consulta real via `scripts/va-probe.py`)

| Codec | Decodificar | Codificar |
|---|---|---|
| H.264 (Constrained Baseline/Main/High) | sim | **sim** (`EncSliceLP` = VDEnc low-power) |
| HEVC Main / Main10 | sim | **sim** (low-power) |
| HEVC 4:4:4 / SCC | sim | sim (low-power) |
| VP9 perfis 0–3 | sim | sim (low-power) |
| JPEG | sim | sim |
| MPEG-2, VP8 | sim | não |
| AV1 | **não listado** pelo driver livre atual | não (hardware não tem) |
| Pós-processamento (VPP: escala/conversão de cor) | sim | — |

Conclusão: OBS/FFmpeg podem codificar H.264 e HEVC na GPU via VA-API, sem pesar na CPU de 15 W.

## Áudio

- Controlador Intel cAVS (Raptor Lake-P), driver **SOF** (`sof-audio-pci-intel-tgl`), placa `sof-hda-dsp`; `firmware-sof-signed` 2025.01.
- Servidor: **PipeWire 1.4.2** + WirePlumber 0.5.8 + `pipewire-pulse` + `pipewire-alsa`; 48 kHz float32 estéreo.
- Saída padrão: alto-falante interno. Também há 3 saídas HDMI/DP.
- Entrada padrão: **microfone digital** (array interno). Alternativa: microfone de headset (mono, P2).

## Ferramentas

| Ferramenta | Estado | Candidato no repositório |
|---|---|---|
| OBS Studio | não instalado | 30.2.3 |
| Kdenlive | não instalado | 24.12.3 |
| Audacity | não instalado | 3.7.3 |
| FFmpeg | não instalado | 7.1.5 |
| vainfo / v4l-utils | não instalados (diagnóstico) | — |
| Flatpak | não instalado | — |
| Git | 2.47.3 (sem `user.name`/`user.email` configurados) | — |
| Python | 3.13.5 | — |
| Claude Code | 2.1.319 em `~/.local/bin/claude` | — |

## Rede (preservar)

- NetworkManager gerencia o Wi-Fi. `/etc/network/interfaces` (root, 0600, 31 bytes — só o loopback, presumivelmente) e backup do instalador em `/etc/network/interfaces.backup` (0600). Não lidos nesta etapa (exigiriam sudo e o backup pode conter credencial do Wi-Fi). **Não alterar.**

## PATH (antes da correção)

- `PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games` — sem `~/.local/bin`.
- `~/.bashrc` e `~/.profile` idênticos aos de `/etc/skel`: as tentativas anteriores com aspas erradas não chegaram a gravar nada.
- O `~/.profile` padrão já adiciona `~/.local/bin` se a pasta existir, mas ela foi criada depois do login. Correção aplicada: ver `docs/mudancas.md`.
