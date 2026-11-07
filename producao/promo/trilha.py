#!/usr/bin/env python3
"""Trilha original do vídeo promocional do Ukiyo — chiptune lo-fi na escala japonesa in-sen (Ré, Mi♭, Sol, Lá, Dó).
96 BPM, 55 s, 48 kHz estéreo, sintetizada do zero com NumPy (sem samples, sem rede).
Seções (compasso = 2,5 s): abertura 0–5 s · temas 5–30 · troca 30–35 · Henshū 35–47,5 · encerramento 47,5–55.
Uso: .venv/bin/python producao/promo/trilha.py saida.wav
"""
import sys, wave
import numpy as np

SR = 48000; BPM = 96; BEAT = 60 / BPM; BAR = 4 * BEAT; DUR = 55.0
N = int(SR * DUR)
rng = np.random.default_rng(21)
L = np.zeros(N); R = np.zeros(N)


def hz(nota):  # nota MIDI → Hz
    return 440.0 * 2 ** ((nota - 69) / 12)


def env(n, a=0.005, d=0.1, s=0.6, r=0.08, dur=None):
    t = np.arange(n) / SR; dur = dur or n / SR
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = np.clip((dur - t) / r, 0, 1); return e * rel


def por(sinal, t0, pan=0.0, ganho=1.0):
    i = int(t0 * SR); j = min(N, i + len(sinal))
    if i >= N or j <= i: return
    s = sinal[: j - i] * ganho
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))


def osc(tipo, f, dur, duty=0.5, vib=0.0):
    n = int(dur * SR); t = np.arange(n) / SR
    ff = f * (1 + vib * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.25, 0, 1))
    fase = np.cumsum(ff) / SR % 1.0
    if tipo == "quadrada": return np.where(fase < duty, 1.0, -1.0)
    if tipo == "triangulo": return 4 * np.abs(fase - 0.5) - 1
    if tipo == "serra": return 2 * fase - 1
    return np.sin(2 * np.pi * fase)


try:
    from scipy.signal import lfilter
    def passa_baixa(x, corte):   # filtro de um polo
        a = np.exp(-2 * np.pi * corte / SR); return lfilter([1 - a], [1, -a], x)
except ImportError:
    def passa_baixa(x, corte):   # mesma coisa, sem scipy (mais lento)
        a = np.exp(-2 * np.pi * corte / SR); y = np.empty_like(x); acc = 0.0
        for k in range(len(x)): acc = (1 - a) * x[k] + a * acc; y[k] = acc
        return y


# ---- harmonia: Rém(9) → Si♭maj7 → Solm9 → Lá7sus (um acorde por compasso)
ACORDES = [[50, 57, 62, 64, 65], [46, 53, 57, 62, 65], [43, 50, 55, 58, 62], [45, 52, 57, 60, 62]]
BAIXO = [38, 34, 31, 33]
INSEN = [62, 63, 67, 69, 72, 74, 75, 79, 81]          # Ré Mi♭ Sol Lá Dó (duas oitavas)

# pad (todo o vídeo): três serras desafinadas, filtradas, com volume por seção
for b in range(int(DUR / BAR) + 1):
    t0 = b * BAR; ac = ACORDES[b % 4]
    sec = 0.9 if t0 < 5 else (0.35 if t0 < 47.5 else 1.6)
    for nota in ac[1:]:
        s = sum(osc("serra", hz(nota) * (1 + d), BAR + 0.4) for d in (-0.004, 0, 0.0045)) / 3
        s = passa_baixa(s, 1400 if t0 < 5 else 2200) * env(len(s), a=0.35, d=1.5, s=0.75, r=0.5)
        por(s, t0, pan=(nota % 5 - 2) * 0.25, ganho=0.07 * sec)

# baixo (a partir de 5 s)
for b in range(2, 19):
    t0 = b * BAR; raiz = BAIXO[b % 4]
    for (bt, d, oit) in [(0, 0.55, 0), (1.5, 0.3, 0), (2, 0.55, 0), (3.5, 0.25, 12)]:
        s = osc("triangulo", hz(raiz + oit), d) * env(int(d * SR), a=0.004, d=0.12, s=0.7, r=0.04)
        por(s, t0 + bt * BEAT, ganho=0.30)

# bateria (5 s a 47,5 s), com leve swing
def bumbo():
    n = int(0.35 * SR); t = np.arange(n) / SR; f = 45 + 95 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
def caixa():
    n = int(0.22 * SR); t = np.arange(n) / SR
    ruido = passa_baixa(rng.standard_normal(n), 5000) * np.exp(-t * 22)
    return 0.7 * ruido + 0.35 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 30)
def chimbal(aberto=False):
    n = int((0.12 if aberto else 0.04) * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); x = x - passa_baixa(x, 7000)
    return x * np.exp(-t * (18 if aberto else 70))
BU, CX = bumbo(), caixa()
for b in range(2, 19):
    t0 = b * BAR
    for bt in (0, 2.5) + ((1.75,) if b % 2 else ()): por(BU, t0 + bt * BEAT, ganho=0.55)
    for bt in (1, 3): por(CX, t0 + bt * BEAT, pan=0.1, ganho=0.30)
    for k in range(8):
        sw = 0.06 * BEAT if k % 2 else 0
        por(chimbal(k == 7), t0 + k * BEAT / 2 + sw, pan=-0.3, ganho=0.10 if k % 2 else 0.14)

# melodia (quadrada 25%, com vibrato e "bitcrush"), frases de 8 compassos
FRASE = [(0, 4, 1), (1, 3, 0.5), (1.5, 2, 0.5), (2, 1, 1), (3, 3, 1),
         (4, 5, 1.5), (5.5, 4, 0.5), (6, 3, 1), (7, 1, 1),
         (8, 2, 1), (9, 3, 0.5), (9.5, 4, 0.5), (10, 6, 1.5), (11.5, 5, 0.5),
         (12, 4, 1), (13, 3, 1), (14, 1, 1.5), (15.5, 0, 0.5)]
def melodia(t_ini, rep, transp=0, ganho=0.11):
    for r in range(rep):
        for (bt, grau, d) in FRASE:
            t0 = t_ini + r * 16 * BEAT + bt * BEAT; dd = d * BEAT * 0.92
            s = osc("quadrada", hz(INSEN[grau] + transp), dd, duty=0.25, vib=0.006)
            s = np.round(s * env(len(s), a=0.006, d=0.25, s=0.55, r=0.05) * 12) / 12   # 8-bit
            por(s, t0, pan=0.15, ganho=ganho)
            eco = s * 0.35; por(eco, t0 + 0.75 * BEAT, pan=-0.35, ganho=ganho)            # eco pingue-pongue
melodia(5.0, 3)                       # temas (5–35 s)
melodia(35.0, 1, transp=12, ganho=0.07)  # Henshū: oitava acima, mais suave (35–45 s)

# arpejo (Henshū): pulso 12,5% em semicolcheias
for b in range(14, 19):
    ac = ACORDES[b % 4]
    for k in range(16):
        nota = ac[1 + (k % 4)] + 12; t0 = b * BAR + k * BEAT / 4
        s = osc("quadrada", hz(nota), BEAT / 4 * 0.8, duty=0.125) * env(int(BEAT / 4 * 0.8 * SR), a=0.002, d=0.05, s=0.3, r=0.02)
        por(s, t0, pan=0.5 if k % 2 else -0.5, ganho=0.045)

# sinos (abertura e encerramento) e efeitos de transição
def sino(f, dur=2.5):
    n = int(dur * SR); t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * dcy) for m, a, dcy in ((1, 1, 1.6), (2.76, 0.4, 3), (5.4, 0.2, 5)))
for (t0, nota) in [(0.8, 74), (1.4, 79), (2.0, 81), (48.2, 74), (48.8, 81), (49.4, 86)]:
    por(sino(hz(nota)), t0, pan=0.2, ganho=0.12)
def subida(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); x = x - passa_baixa(x, 2500); return x * (t / dur) ** 2.5
def impacto():
    n = int(1.6 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (38 + 40 * np.exp(-t * 6)) * t) * np.exp(-t * 2.6)
for tc in (5.0, 30.0, 35.0, 47.5):
    por(subida(1.2), tc - 1.2, ganho=0.10); por(impacto(), tc, ganho=0.5)
# chiado de vinil, bem baixo
v = passa_baixa(rng.standard_normal(N), 3000) * 0.006
L += v; R += v * 0.9

# mixagem final: limitador suave + fade de saída
mix = np.stack([L, R], 1)
mix *= np.clip((DUR - np.arange(N) / SR) / 2.5, 0, 1)[:, None]
mix = np.tanh(mix * 1.6) / np.tanh(1.6)
mix /= max(1e-9, np.abs(mix).max()) / 0.89
with wave.open(sys.argv[1] if len(sys.argv) > 1 else "trilha.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("trilha pronta:", DUR, "s")
