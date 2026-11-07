#!/usr/bin/env python3
"""Gera o widget Plasma 6 "Tela Washi" (brilho + saturação) como pacote Plasma/Applet.

- Brilho: luz de fundo via org.kde.ScreenBrightness (mesma interface do controle de brilho do Plasma).
- Saturação: perfil ICC gerado na hora (tools/gerar-icc-saturacao.py) aplicado à tela pelo KWin
  (kscreen-doctor output.<saída>.iccprofile). 100% = sem perfil (sRGB, custo zero).
  A correção é feita na saída para o painel: capturas de tela não são afetadas.
Uso: gerar-widget-tela.py PASTA_DESTINO   (cria PASTA_DESTINO/org.ukiyo.tela)
"""
import json, os, shutil, stat, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ID = "org.ukiyo.tela"

AUX = r'''#!/usr/bin/env bash
# washi-tela — auxiliar do widget "Tela Washi".
#   washi-tela ler            -> imprime "BRILHO=<0-100> SATURACAO=<pct>"
#   washi-tela brilho <5-100>
#   washi-tela saturacao <30-150>   (100 = normal, sem perfil ICC)
set -euo pipefail
AQUI=$(cd "$(dirname "$0")" && pwd)
EST="${XDG_STATE_HOME:-$HOME/.local/state}/ukiyo"; mkdir -p "$EST"
ICC="${XDG_DATA_HOME:-$HOME/.local/share}/ukiyo/icc"; mkdir -p "$ICC"
SAIDA=$(kscreen-doctor -j 2>/dev/null | python3 -I -c '
import json,sys
d=json.load(sys.stdin); outs=[o for o in d.get("outputs",[]) if o.get("enabled") and o.get("connected")]
interna=[o for o in outs if str(o.get("name","")).startswith(("eDP","LVDS","DSI"))]
print((interna or outs)[0]["name"] if outs else "")')
[ -n "$SAIDA" ] || { echo "ERRO=sem-tela"; exit 1; }
DISP=$(qdbus6 org.kde.ScreenBrightness /org/kde/ScreenBrightness org.freedesktop.DBus.Properties.Get \
       org.kde.ScreenBrightness DisplaysDBusNames 2>/dev/null | head -1)
DISP=${DISP:-display0}
prop() { qdbus6 org.kde.ScreenBrightness "/org/kde/ScreenBrightness/$DISP" org.freedesktop.DBus.Properties.Get org.kde.ScreenBrightness.Display "$1"; }
sat_atual() { [ -f "$EST/saturacao" ] && cat "$EST/saturacao" || echo 100; }

case "${1:-ler}" in
  ler)
    b=$(prop Brightness); m=$(prop MaxBrightness)
    modo=$(cat "$EST/modo" 2>/dev/null || echo claro)
    echo "BRILHO=$(( (b * 100 + m / 2) / m )) SATURACAO=$(sat_atual) MODO=$modo" ;;
  tema)
    # troca claro/escuro usando os scripts do projeto (fazem backup e são reversíveis)
    alvo=${2:?}; case "$alvo" in claro|escuro|marys|neontokyo|touge) ;; *) echo "ERRO=tema-invalido"; exit 2 ;; esac
    script="__PROJ__/modos/modo-$alvo.sh"
    [ -x "$script" ] || { echo "ERRO=sem-script"; exit 1; }
    if "$script" > "$EST/ultima-troca-de-tema.log" 2>&1; then echo "MODO=$alvo"
    else echo "ERRO=troca-falhou MODO=$(cat "$EST/modo" 2>/dev/null || echo claro)"; fi ;;
  brilho)
    p=${2:?}; [ "$p" -lt 5 ] && p=5; [ "$p" -gt 100 ] && p=100
    m=$(prop MaxBrightness)
    qdbus6 org.kde.ScreenBrightness "/org/kde/ScreenBrightness/$DISP" org.kde.ScreenBrightness.Display.SetBrightness $(( p * m / 100 )) 0
    echo "BRILHO=$p" ;;
  saturacao)
    p=${2:?}; [ "$p" -lt 30 ] && p=30; [ "$p" -gt 150 ] && p=150
    if [ "$p" = 100 ]; then
      kscreen-doctor "output.$SAIDA.iccprofile." >/dev/null 2>&1
    else
      f="$ICC/washi-sat-$p.icc"
      [ -f "$f" ] || python3 -I "$AQUI/gerar-icc-saturacao.py" "$p" "$f" >/dev/null
      kscreen-doctor "output.$SAIDA.iccprofile.$f" >/dev/null 2>&1
    fi
    echo "$p" > "$EST/saturacao"; echo "SATURACAO=$p" ;;
  *) echo "uso: washi-tela ler | brilho N | saturacao N | tema claro|escuro|marys|neontokyo|touge"; exit 2 ;;
esac
'''

QML = r'''import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents3
import org.kde.plasma.extras as PlasmaExtras
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami

// Tela Washi — brilho (luz de fundo) e saturação (perfil ICC aplicado pelo KWin).
PlasmoidItem {
    id: root

    property int brilho: 100
    property int saturacao: 100
    readonly property string aux: decodeURIComponent(Qt.resolvedUrl("../code/washi-tela").toString().replace("file://", ""))

    toolTipMainText: "Tela"
    toolTipSubText: "Brilho " + brilho + "% · Saturação " + saturacao + "%\nRoda do mouse: brilho"

    function rodar(args) { exec.connectSource("'" + aux + "' " + args) }

    P5Support.DataSource {
        id: exec
        engine: "executable"
        connectedSources: []
        onNewData: function (fonte, dados) {
            const saida = (dados["stdout"] || "").trim()
            const b = saida.match(/BRILHO=(\d+)/); if (b) root.brilho = parseInt(b[1])
            const s = saida.match(/SATURACAO=(\d+)/); if (s) root.saturacao = parseInt(s[1])
            const m = saida.match(/MODO=(claro|escuro|marys|neontokyo|touge)/); if (m) root.modo = m[1]
            root.erroTema = saida.indexOf("ERRO=") >= 0 && fonte.indexOf(" tema ") >= 0
            if (fonte.indexOf(" tema ") >= 0) root.trocando = false
            disconnectSource(fonte)
        }
    }

    Timer { id: atrasoBrilho; interval: 120; onTriggered: root.rodar("brilho " + sliderBrilhoValor) }
    Timer { id: atrasoSat; interval: 200; onTriggered: root.rodar("saturacao " + sliderSatValor) }
    property int sliderBrilhoValor: 100
    property int sliderSatValor: 100
    property string modo: "claro"
    property bool trocando: false
    property bool erroTema: false
    function trocarTema(alvo) { if (trocando || modo === alvo) return; trocando = true; erroTema = false; rodar("tema " + alvo) }

    Component.onCompleted: rodar("ler")
    onExpandedChanged: function () { if (root.expanded) root.rodar("ler") }

    compactRepresentation: MouseArea {
        id: compacto
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton
        onClicked: root.expanded = !root.expanded
        onWheel: function (ev) {
            const passo = ev.angleDelta.y > 0 ? 5 : -5
            root.brilho = Math.max(5, Math.min(100, root.brilho + passo))
            root.rodar("brilho " + root.brilho)
        }
        Kirigami.Icon {
            anchors.centerIn: parent
            width: 16; height: 16
            // no painel escuro (modo Yoru) usa os raios claros; no claro, o ícone original
            source: Qt.resolvedUrl(Kirigami.Theme.backgroundColor.hslLightness < 0.5 ? "../icons/tela-escuro.svg" : "../icons/tela.svg")
            smooth: false
        }
    }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 18
        Layout.minimumWidth: Kirigami.Units.gridUnit * 16
        spacing: Kirigami.Units.smallSpacing

        PlasmaExtras.Heading {
            level: 4
            text: "Tela"
            font.family: "DotGothic16"
            Layout.fillWidth: true
        }

        RowLayout {
            Layout.fillWidth: true
            PlasmaComponents3.Label { text: "Brilho"; Layout.fillWidth: true }
            PlasmaComponents3.Label { text: sliderB.value + "%"; font.family: "DotGothic16" }
        }
        PlasmaComponents3.Slider {
            id: sliderB
            Layout.fillWidth: true
            from: 5; to: 100; stepSize: 5
            value: root.brilho
            onMoved: { root.sliderBrilhoValor = value; atrasoBrilho.restart() }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: Kirigami.Units.smallSpacing
            PlasmaComponents3.Label { text: "Saturação"; Layout.fillWidth: true }
            PlasmaComponents3.Label { text: sliderS.value + "%"; font.family: "DotGothic16" }
        }
        PlasmaComponents3.Slider {
            id: sliderS
            Layout.fillWidth: true
            from: 30; to: 150; stepSize: 5
            value: root.saturacao
            onMoved: { root.sliderSatValor = value; atrasoSat.restart() }
        }
        Item {   // marcas da escala: "normal" fica exatamente sobre 100% (escala 30–150)
            Layout.fillWidth: true
            implicitHeight: rotCinza.implicitHeight
            PlasmaComponents3.Label { id: rotCinza; text: "cinza"; opacity: 0.7; font.pointSize: Kirigami.Theme.smallFont.pointSize; anchors.left: parent.left }
            PlasmaComponents3.Label {
                text: "▲ normal"; opacity: 0.7; font.pointSize: Kirigami.Theme.smallFont.pointSize
                x: Math.round(sliderS.leftPadding + (sliderS.availableWidth - sliderS.handle.width) * (100 - sliderS.from) / (sliderS.to - sliderS.from) + sliderS.handle.width / 2 - width / 2 + 6)
            }
            PlasmaComponents3.Label { text: "vivo"; opacity: 0.7; font.pointSize: Kirigami.Theme.smallFont.pointSize; anchors.right: parent.right }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: Kirigami.Units.smallSpacing
            PlasmaComponents3.Button {
                text: "Saturação normal"
                icon.name: "edit-undo"
                enabled: root.saturacao !== 100
                onClicked: { root.saturacao = 100; root.rodar("saturacao 100") }
            }
            PlasmaComponents3.Button {
                text: "Brilho 100%"
                icon.name: "brightness-high"
                enabled: root.brilho !== 100
                onClicked: { root.brilho = 100; root.rodar("brilho 100") }
            }
        }

        Kirigami.Separator { Layout.fillWidth: true; Layout.topMargin: Kirigami.Units.smallSpacing }

        RowLayout {
            Layout.fillWidth: true
            PlasmaComponents3.Label { text: "Tema"; Layout.fillWidth: true }
            PlasmaComponents3.BusyIndicator { visible: root.trocando; running: root.trocando; implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth }
            PlasmaComponents3.Label {
                text: root.trocando ? "aplicando…" : (root.modo === "escuro" ? "Escuro · Yoru" : root.modo === "marys" ? "Mary's · gatinhos" : root.modo === "neontokyo" ? "Neon Tokyo" : root.modo === "touge" ? "Touge 峠" : "Claro · Washi")
                font.family: "DotGothic16"
            }
        }
        RowLayout {
            Layout.fillWidth: true
            PlasmaComponents3.Button {
                Layout.fillWidth: true
                text: "Claro (Washi)"
                icon.name: "weather-clear"
                checkable: true
                checked: root.modo === "claro"
                enabled: !root.trocando
                onClicked: { checked = Qt.binding(function () { return root.modo === "claro" }); root.trocarTema("claro") }
            }
            PlasmaComponents3.Button {
                Layout.fillWidth: true
                text: "Escuro (Yoru)"
                icon.name: "weather-clear-night"
                checkable: true
                checked: root.modo === "escuro"
                enabled: !root.trocando
                onClicked: { checked = Qt.binding(function () { return root.modo === "escuro" }); root.trocarTema("escuro") }
            }
        }
        RowLayout {   // segunda linha da grade 2x2 de temas
            Layout.fillWidth: true
        PlasmaComponents3.Button {
            Layout.fillWidth: true
            text: "Mary's (gatinhos)"
            icon.source: Qt.resolvedUrl("../icons/gatinho.svg")
            checkable: true
            checked: root.modo === "marys"
            enabled: !root.trocando
            onClicked: { checked = Qt.binding(function () { return root.modo === "marys" }); root.trocarTema("marys") }
        }
        PlasmaComponents3.Button {
            Layout.fillWidth: true
            text: "Neon Tokyo (cyberpunk)"
            icon.source: Qt.resolvedUrl("../icons/neon.svg")
            checkable: true
            checked: root.modo === "neontokyo"
            enabled: !root.trocando
            onClicked: { checked = Qt.binding(function () { return root.modo === "neontokyo" }); root.trocarTema("neontokyo") }
        }
        }
        RowLayout {   // terceira linha: Touge
            Layout.fillWidth: true
            PlasmaComponents3.Button {
                Layout.fillWidth: true
                text: "Touge 峠 (drift)"
                icon.source: Qt.resolvedUrl("../icons/volante.svg")
                checkable: true
                checked: root.modo === "touge"
                enabled: !root.trocando
                onClicked: { checked = Qt.binding(function () { return root.modo === "touge" }); root.trocarTema("touge") }
            }
        }
        PlasmaComponents3.Label {
            Layout.fillWidth: true
            visible: root.erroTema
            wrapMode: Text.WordWrap
            color: Kirigami.Theme.negativeTextColor
            text: "A troca de tema falhou. Detalhes em ~/.local/state/ukiyo/ultima-troca-de-tema.log"
        }

        PlasmaComponents3.Label {
            Layout.fillWidth: true
            Layout.topMargin: Kirigami.Units.smallSpacing
            wrapMode: Text.WordWrap
            opacity: 0.75
            font.pointSize: Kirigami.Theme.smallFont.pointSize
            text: "A saturação muda só o que você vê no painel: capturas de tela não são afetadas. Para avaliar cores de vídeo, use 100%."
        }
    }
}
'''

def icone_svg(raio="#2B2A28"):
    # sol pixel 16x16: raios sumi, disco meio ouro (brilho) / meio torii (saturação)
    g = [["."] * 16 for _ in range(16)]
    cor = {"k": raio, "y": "#D9A441", "r": "#C8102E", "w": "#F2EBDD"}
    for (x, y) in [(7, 0), (8, 0), (7, 1), (8, 1), (7, 14), (8, 14), (7, 15), (8, 15),
                   (0, 7), (0, 8), (1, 7), (1, 8), (14, 7), (14, 8), (15, 7), (15, 8),
                   (2, 2), (3, 3), (13, 2), (12, 3), (2, 13), (3, 12), (13, 13), (12, 12)]:
        g[y][x] = "k"
    for y in range(4, 12):
        for x in range(4, 12):
            dx, dy = x - 7.5, y - 7.5
            d = (dx * dx + dy * dy) ** 0.5
            if d <= 3.2: g[y][x] = "y" if x < 8 else "r"
            elif d <= 4.3: g[y][x] = "k"
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{cor[c]}"/>'
                    for y in range(16) for x in range(16) if (c := g[y][x]) != ".")
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" '
            'shape-rendering="crispEdges">' + rects + "</svg>\n")

META = {
    "KPackageStructure": "Plasma/Applet",
    "X-Plasma-API-Minimum-Version": "6.0",
    "KPlugin": {"Id": ID, "Name": "Tela Washi", "Description": "Brilho, saturação e temas (claro, escuro, Mary's)",
                "Icon": "video-display-brightness", "Category": "System Information",
                "Authors": [{"Name": "Davi"}], "License": "GPL-2.0-or-later", "Version": "1.0"}
}

def gerar(dest):
    raiz = os.path.join(dest, ID)
    if os.path.exists(raiz): shutil.rmtree(raiz)
    for d in ("contents/ui", "contents/code", "contents/icons"): os.makedirs(os.path.join(raiz, d))
    json.dump(META, open(os.path.join(raiz, "metadata.json"), "w"), ensure_ascii=False, indent=2)
    open(os.path.join(raiz, "contents/ui/main.qml"), "w").write(QML)
    open(os.path.join(raiz, "contents/icons/tela.svg"), "w").write(icone_svg())
    open(os.path.join(raiz, "contents/icons/tela-escuro.svg"), "w").write(icone_svg("#E6E4EC"))
    gato = os.path.abspath(os.path.join(AQUI, "..", "..", "marys", "icons", "marys-pixel", "apps", "scalable", "washi-lancador.svg"))
    if os.path.exists(gato): shutil.copy(gato, os.path.join(raiz, "contents/icons/gatinho.svg"))
    neon = os.path.abspath(os.path.join(AQUI, "..", "..", "neontokyo", "icons", "neontokyo-pixel", "apps", "scalable", "washi-lancador.svg"))
    if os.path.exists(neon): shutil.copy(neon, os.path.join(raiz, "contents/icons/neon.svg"))
    vol = os.path.abspath(os.path.join(AQUI, "..", "..", "touge", "icons", "touge-pixel", "apps", "scalable", "washi-lancador.svg"))
    if os.path.exists(vol): shutil.copy(vol, os.path.join(raiz, "contents/icons/volante.svg"))
    proj = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
    aux = os.path.join(raiz, "contents/code/washi-tela"); open(aux, "w").write(AUX.replace("__PROJ__", proj))
    shutil.copy(os.path.join(AQUI, "gerar-icc-saturacao.py"), os.path.join(raiz, "contents/code/"))
    for f in (aux, os.path.join(raiz, "contents/code/gerar-icc-saturacao.py")):
        os.chmod(f, os.stat(f).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return raiz

if __name__ == "__main__":
    print(gerar(sys.argv[1] if len(sys.argv) > 1 else "."))
