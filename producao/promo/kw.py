#!/usr/bin/env python3
"""Ferramenta de janelas via script do KWin. Uso:
  kw.py desk N                 -> troca para a área N (0-3)
  kw.py arranjar '<json>'      -> {pid: [area, x, y, w, h]} ; imprime geometria final das janelas desses pids
"""
import json, subprocess, sys, time, os
S = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
def run(js):
    p = f"{S}/ukiyo-promo-kw.js"; open(p, "w").write(js)
    i = subprocess.run(["qdbus6", "org.kde.KWin", "/Scripting", "org.kde.kwin.Scripting.loadScript", p, "ukiyo-promo"], capture_output=True, text=True).stdout.strip()
    t0 = time.time(); subprocess.run(["qdbus6", "org.kde.KWin", f"/Scripting/Script{i}", "org.kde.kwin.Script.run"], capture_output=True)
    time.sleep(0.7); subprocess.run(["qdbus6", "org.kde.KWin", "/Scripting", "org.kde.kwin.Scripting.unloadScript", "ukiyo-promo"], capture_output=True)
    out = subprocess.run(["journalctl", "--user", "--since", "-6 s", "-o", "cat"], capture_output=True, text=True).stdout
    return [l.split("PROMO|", 1)[1] for l in out.splitlines() if "PROMO|" in l]
if sys.argv[1] == "desk":
    run(f"workspace.currentDesktop = workspace.desktops[{int(sys.argv[2])}];")
else:
    spec = json.loads(sys.argv[2])
    js = "var spec = " + json.dumps(spec) + ";\nworkspace.windowList().forEach(function (w) {\n  var s = spec[String(w.pid)]; if (!s || !w.normalWindow) return;\n  w.minimized = false; w.desktops = [workspace.desktops[s[0]]];\n  if (s.length > 1) w.frameGeometry = {x: s[1], y: s[2], width: s[3], height: s[4]};\n  var g = w.frameGeometry; print('PROMO|' + w.pid + '|' + w.resourceClass + '|' + Math.round(g.x) + ',' + Math.round(g.y) + ',' + Math.round(g.width) + ',' + Math.round(g.height));\n});"
    for l in run(js): print(l)
