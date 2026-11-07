#!/usr/bin/env python3
"""Gera o tema de login SDDM 'washi' a partir do tema Breeze instalado (/usr/share/sddm/themes/breeze).

Mudanças mínimas (o resto é o Breeze original, para preservar legibilidade e funções):
  - relógio e data em DotGothic16 (WashiClock.qml, tamanhos múltiplos de 16 px: 64 e 32)
  - papel de parede Washi v2 (fundo.png) e torii pixel como logo (torii.svg)
  - [só com --painel] fundo sem desfoque e sem alteração de cor (WashiFader.qml)
  - [só com --painel] painel compacto sumi com borda washi atrás do formulário, no Main.qml, fora do layout (legibilidade sem desfoque)
  - campos de senha, lista de usuários, seleção de sessão, mensagens de erro e botões de energia: inalterados
Uso: gerar-sddm.py PASTA_DESTINO [--painel]   (cria PASTA_DESTINO/washi)
  padrão (V5): desfoque original do Breeze, sem painel; --painel: variante sem desfoque + painel
"""
import os, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TEMA = os.path.dirname(AQUI)
BREEZE = "/usr/share/sddm/themes/breeze"
CLOCK = "/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/breeze/components/Clock.qml"
FADER = "/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/breeze/components/WallpaperFader.qml"

def gerar(dest, painel=False):
    out = os.path.join(dest, "washi")
    if os.path.exists(out): shutil.rmtree(out)
    shutil.copytree(BREEZE, out, ignore=shutil.ignore_patterns("preview.png", "theme.conf.user"))

    # 1) Main.qml: usa o relógio pixel no lugar do Clock padrão
    p = os.path.join(out, "Main.qml"); s = open(p, encoding="utf-8").read()
    alvo = "        Clock {\n            id: clock\n"
    assert s.count(alvo) == 1, "estrutura do Main.qml do Breeze mudou; revisar o gerador"
    s = s.replace(alvo, "        WashiClock {\n            id: clock\n")
    open(p, "w", encoding="utf-8").write(s)

    if painel:   # variante "b": sem desfoque + painel (a V5 usa o padrão: desfoque original do Breeze)
        # 1b) WashiFader.qml: cópia do WallpaperFader sem desfoque nem ajuste de cor (estados de opacidade preservados)
        f = open(FADER, encoding="utf-8").read()
        trocas = [("radius: 50 * wallpaperFader.factor", "radius: 0"),
                  ("readonly property real contrast: 0.65 * wallpaperFader.factor + (1 - wallpaperFader.factor)", "readonly property real contrast: 1.0"),
                  ("readonly property real saturation: 1.6 * wallpaperFader.factor + (1 - wallpaperFader.factor)", "readonly property real saturation: 1.0"),
                  ("readonly property real intensity: (wallpaperFader.lightColorScheme ? 1.7 : 0.6) * wallpaperFader.factor + (1 - wallpaperFader.factor)", "readonly property real intensity: 1.0")]
        for a, b in trocas:
            assert a in f, "estrutura do WallpaperFader.qml mudou; revisar o gerador: " + a[:40]
            f = f.replace(a, b)
        open(os.path.join(out, "WashiFader.qml"), "w", encoding="utf-8").write("// Washi: WallpaperFader do Breeze sem desfoque/ajuste de cor\n" + f)
        p = os.path.join(out, "Main.qml"); s = open(p, encoding="utf-8").read()
        assert s.count("        WallpaperFader {\n") == 1
        s = s.replace("        WallpaperFader {\n", "        WashiFader {\n")
        open(p, "w", encoding="utf-8").write(s)

        # 1c) Main.qml: painel compacto ATRÁS da pilha do formulário (fora do layout do Breeze; componentes intactos)
        p = os.path.join(out, "Main.qml"); s = open(p, encoding="utf-8").read()
        alvo = "        QQC2.StackView {\n            id: mainStack\n"
        assert s.count(alvo) == 1, "estrutura do Main.qml mudou; revisar o gerador"
        painel = """        // Washi: painel sumi com borda washi de 2 px e sombra dura atrás de usuário, senha, sessão e energia.
            // Acompanha a tela atual da pilha (lista de usuários ou "Outros...") e a opacidade do formulário.
            Rectangle {
                id: washiPainel
                readonly property Item alvo: mainStack.currentItem
                readonly property bool ok: !!alvo && !!alvo.mainPasswordBox && !!alvo.userList
                readonly property real topo: ok ? mainStack.y + alvo.userList.y + alvo.userList.height / 2 - 110 + 0 * (alvo.height + mainStack.height) : 0
                readonly property real base: ok ? parent.mapFromItem(alvo.mainPasswordBox, 0, alvo.mainPasswordBox.height).y + 205 + 0 * (alvo.height + mainStack.height + alvo.mainPasswordBox.y) : 0
                visible: ok
                opacity: mainStack.opacity
                x: (parent.width - width) / 2
                y: topo
                width: Math.min(parent.width - 32, 640)
                height: Math.max(0, base - topo)
                color: Qt.rgba(0x24 / 255, 0x22 / 255, 0x1F / 255, 0.92)
                border.color: "#E4D9C4"
                border.width: 2
                radius: 0
                Rectangle { z: -1; x: 6; y: 6; width: parent.width; height: parent.height; color: Qt.rgba(0, 0, 0, 0.35) }
            }

    """
        s = s.replace(alvo, painel + alvo)
        open(p, "w", encoding="utf-8").write(s)

    # 2) WashiClock.qml: cópia do Clock do Breeze com DotGothic16 em tamanhos inteiros (nítidos)
    c = open(CLOCK, encoding="utf-8").read()
    a1 = "font.pointSize: Math.round(Kirigami.Theme.defaultFont.pointSize * 4.8)"
    a2 = "font.pointSize: Math.round(Kirigami.Theme.defaultFont.pointSize * 2.4)"
    assert a1 in c and a2 in c, "estrutura do Clock.qml mudou; revisar o gerador"
    c = c.replace(a1, 'font.family: "DotGothic16"\n        font.pixelSize: 64')
    c = c.replace(a2, 'font.family: "DotGothic16"\n        font.pixelSize: 32')
    c = c.replace("ColumnLayout {", "// Washi: relógio do Breeze com fonte pixel DotGothic16\nColumnLayout {", 1)
    open(os.path.join(out, "WashiClock.qml"), "w", encoding="utf-8").write(c)

    # 3) papel de parede e logo
    shutil.copy(os.path.join(TEMA, "wallpaper", "entardecer-v2-1920x1080.png"), os.path.join(out, "fundo.png"))
    shutil.copy(os.path.join(TEMA, "icons-src", "lancador.svg"), os.path.join(out, "torii.svg"))

    # 4) configuração e metadados
    open(os.path.join(out, "theme.conf"), "w").write("""[General]
type=image
background=fundo.png
color=#24221F
fontSize=10
showClock=true
showlogo=shown
logo=torii.svg
needsFullUserModel=false
""")
    m = os.path.join(out, "metadata.desktop"); linhas = []
    for l in open(m, encoding="utf-8"):
        if l.startswith(("Name[", "Description[")): continue
        if l.startswith("Name="): l = "Name=Washi\n"
        elif l.startswith("Description="): l = "Description=Washi (pixel, Japão tradicional) — baseado no Breeze\n"
        elif l.startswith("Theme-Id="): l = "Theme-Id=washi\n"
        elif l.startswith("Screenshot="): l = "Screenshot=preview.png\n"
        linhas.append(l)
    open(m, "w", encoding="utf-8").write("".join(linhas))
    return out

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    print(gerar(args[0] if args else ".", painel="--painel" in sys.argv))
