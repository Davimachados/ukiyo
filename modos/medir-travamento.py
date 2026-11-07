#!/usr/bin/env python3
"""Mede congelamentos do painel (plasmashell) e do compositor (KWin) enquanto um comando roda.
Sonda os dois por D-Bus a cada 50 ms e registra quanto tempo cada um ficou sem responder.
Uso: medir-travamento.py "comando a medir"   [duração da observação em s, padrão 5]
"""
import subprocess, sys, threading, time

CMD = sys.argv[1]; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
SONDAS = {"painel": ["qdbus6", "org.kde.plasmashell", "/PlasmaShell", "org.freedesktop.DBus.Peer.Ping"],
          "KWin":   ["qdbus6", "org.kde.KWin", "/KWin", "org.freedesktop.DBus.Peer.Ping"]}
res = {k: [] for k in SONDAS}

def sondar(nome, cmd, fim):
    while time.time() < fim:
        t0 = time.time()
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        res[nome].append((t0, time.time() - t0))
        time.sleep(0.05)

fim = time.time() + DUR
ths = [threading.Thread(target=sondar, args=(n, c, fim)) for n, c in SONDAS.items()]
for t in ths: t.start()
time.sleep(0.3)
t0 = time.time(); subprocess.run(CMD, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); tcmd = time.time() - t0
for t in ths: t.join()
base = {}
for n, v in res.items():
    lat = sorted(d for _, d in v); base[n] = lat[len(lat) // 4] if lat else 0
    pior = max(d for _, d in v); total = sum(max(0, d - 0.1) for _, d in v)
    print(f"  {n:7s} maior congelamento {pior*1000:6.0f} ms | tempo total travado (>100 ms) {total*1000:6.0f} ms")
print(f"  comando terminou em {tcmd*1000:.0f} ms")
