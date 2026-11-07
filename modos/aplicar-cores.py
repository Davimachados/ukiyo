#!/usr/bin/env python3
"""Aplica um esquema de cores KDE de forma leve: grava os grupos de cor no kdeglobals e emite só os sinais
que os apps KDE/Qt escutam (KConfigWatcher + KGlobalSettings). Não reescreve arquivos de X11/GTK aqui.
Uso: aplicar-cores.py /caminho/Esquema.colors [tema-de-icones]
(com o tema de ícones, grava cores e ícones juntos e avisa os programas uma única vez)
"""
import os, re, subprocess, sys

esq = sys.argv[1]; icones = sys.argv[2] if len(sys.argv) > 2 else None; kg = os.path.expanduser("~/.config/kdeglobals")
def grupos(texto):
    out, atual = {}, None
    for l in texto.splitlines():
        m = re.match(r"^\[(.+)\]\s*$", l)
        if m: atual = m.group(1); out.setdefault(atual, {}); continue
        if atual and "=" in l and not l.startswith("#"):
            k, v = l.split("=", 1); out[atual][k.strip()] = v.strip()
    return out
novo = grupos(open(esq, encoding="utf-8").read())
alvos = {g: kv for g, kv in novo.items() if g.startswith(("Colors:", "ColorEffects:", "WM"))}
if icones: alvos["Icons"] = {"Theme": icones}
alvos.setdefault("General", {})["ColorScheme"] = novo.get("General", {}).get("ColorScheme", os.path.basename(esq)[:-7])

linhas = open(kg, encoding="utf-8").read().splitlines() if os.path.exists(kg) else []
saida, atual, vistos = [], None, set()
for l in linhas:
    m = re.match(r"^\[(.+)\]\s*$", l)
    if m:
        atual = m.group(1)
        if atual in alvos and atual not in ("General",):       # grupos de cor: substituídos inteiros
            vistos.add(atual); saida.append(l); saida += [f"{k}={v}" for k, v in alvos[atual].items()]; continue
        saida.append(l); continue
    if atual in alvos and atual != "General": continue
    if atual == "General" and l.split("=", 1)[0] == "ColorScheme": continue
    saida.append(l)
    if atual == "General" and "General" not in vistos: pass
# ColorScheme dentro de [General]
if "[General]" in saida:
    i = saida.index("[General]"); saida.insert(i + 1, "ColorScheme=" + alvos["General"]["ColorScheme"])
else:
    saida += ["", "[General]", "ColorScheme=" + alvos["General"]["ColorScheme"]]
for g, kv in alvos.items():
    if g == "General" or g in vistos: continue
    saida += ["", f"[{g}]"] + [f"{k}={v}" for k, v in kv.items()]
tmp = kg + ".tmp"; open(tmp, "w", encoding="utf-8").write("\n".join(saida) + "\n"); os.replace(tmp, kg)

# sinais: KConfigWatcher (apps KF6) e KGlobalSettings PaletteChanged (tema de plataforma Qt)
mapa = "{" + ", ".join(f"'{g}': [b'{k}' {''.join('' for _ in [])}" .replace(" ", "") + "]" for g, kv in alvos.items() for k in list(kv)[:1]) + "}"
mapa = "{" + ", ".join("'%s': [%s]" % (g, ", ".join("b'%s'" % k for k in kv)) for g, kv in alvos.items()) + "}"
subprocess.run(["gdbus", "emit", "--session", "--object-path", "/kdeglobals", "--signal",
                "org.kde.kconfig.notify.ConfigChanged", mapa], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if icones:
    subprocess.run(["dbus-send", "--session", "--type=signal", "/KIconLoader", "org.kde.KIconLoader.iconChanged", "int32:0"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["dbus-send", "--session", "--type=signal", "/KGlobalSettings", "org.kde.KGlobalSettings.notifyChange",
                "int32:0", "int32:0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
