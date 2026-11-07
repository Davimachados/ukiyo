#!/usr/bin/env python3
"""Gera um perfil ICC v4 (matriz/TRC) de "tela sRGB com saturação S%".

Ideia: o KWin converte o conteúdo (sRGB) para o espaço da tela usando as primárias do perfil.
Se o perfil declara primárias P' = P_sRGB · M_s⁻¹, a cor enviada ao painel vira M_s · c, onde
M_s = s·I + (1−s)·L (L = pesos de luminância): s<1 dessatura, s>1 satura. O branco é preservado.
Curva de transferência: sRGB (paramétrica). Sem dependências.

Uso: gerar-icc-saturacao.py PORCENTAGEM SAIDA.icc     (ex.: 60 /tmp/sat60.icc)
"""
import struct, sys

# primárias sRGB adaptadas a D50 (colunas R, G, B) e matriz de adaptação Bradford D65→D50
P50 = [[0.4360747, 0.3850649, 0.1430804],
       [0.2225045, 0.7168786, 0.0606169],
       [0.0139322, 0.0971045, 0.7141733]]
CHAD = [[1.0478112, 0.0228866, -0.0501270],
        [0.0295424, 0.9904844, -0.0170491],
        [-0.0092345, 0.0150436, 0.7521316]]
D50 = (0.9642, 1.0, 0.8249)

def mul(a, b): return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def inv(m):
    a, b, c = m[0]; d, e, f = m[1]; g, h, i = m[2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    return [[(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
            [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
            [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det]]

def s15(v): return struct.pack(">i", int(round(v * 65536)))
def xyz(v): return b"XYZ " + b"\0" * 4 + b"".join(s15(x) for x in v)
def mluc(txt):
    t = txt.encode("utf-16-be")
    return b"mluc" + b"\0" * 4 + struct.pack(">II", 1, 12) + b"enUS" + struct.pack(">II", len(t), 28) + t
def para_srgb():
    return (b"para" + b"\0" * 4 + struct.pack(">HH", 3, 0) +
            s15(2.4) + s15(1 / 1.055) + s15(0.055 / 1.055) + s15(1 / 12.92) + s15(0.04045))
def sf32(m): return b"sf32" + b"\0" * 4 + b"".join(s15(m[i][j]) for i in range(3) for j in range(3))

def perfil(pct):
    s = pct / 100.0
    lum = P50[1]                                          # linha Y = pesos de luminância (soma 1)
    Ms = [[s * (i == j) + (1 - s) * lum[j] for j in range(3)] for i in range(3)]
    P = mul(P50, inv(Ms))                                 # primárias declaradas
    col = lambda j: [P[i][j] for i in range(3)]
    trc = para_srgb()
    tags = [(b"desc", mluc(f"Washi sRGB saturacao {pct}%")), (b"cprt", mluc("ukiyo")),
            (b"wtpt", xyz(D50)), (b"chad", sf32(CHAD)),
            (b"rXYZ", xyz(col(0))), (b"gXYZ", xyz(col(1))), (b"bXYZ", xyz(col(2))),
            (b"rTRC", trc), (b"gTRC", trc), (b"bTRC", trc)]
    n = len(tags); off = 128 + 4 + 12 * n; dados = b""; tabela = b""; vistos = {}
    for sig, d in tags:
        if d in vistos: o, l = vistos[d]
        else:
            while (off + len(dados)) % 4: dados += b"\0"
            o, l = off + len(dados), len(d); dados += d; vistos[d] = (o, l)
        tabela += sig + struct.pack(">II", o, l)
    corpo = struct.pack(">I", n) + tabela + dados
    while len(corpo) % 4: corpo += b"\0"
    tam = 128 + len(corpo)
    cab = (struct.pack(">I", tam) + b"\0" * 4 + struct.pack(">I", 0x04300000) + b"mntr" + b"RGB " + b"XYZ " +
           struct.pack(">6H", 2026, 11, 6, 0, 0, 0) + b"acsp" + b"\0" * 4 + struct.pack(">I", 0) +
           b"\0" * 8 + b"\0" * 8 + struct.pack(">I", 0) + b"".join(s15(x) for x in D50) + b"\0" * 4 +
           b"\0" * 16 + b"\0" * 28)
    assert len(cab) == 128
    return cab + corpo

if __name__ == "__main__":
    pct = int(sys.argv[1]); assert 0 < pct <= 200
    open(sys.argv[2], "wb").write(perfil(pct)); print(sys.argv[2])
