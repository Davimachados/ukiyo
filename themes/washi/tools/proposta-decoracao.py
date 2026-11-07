#!/usr/bin/env python3
"""Gera a PROPOSTA (conceito) da decoração de janelas 'Washi Pixel' para o motor Aurorae.

Os botões são grades 12x12 (desenhadas a 2x = 24 px). As mesmas funções poderão gerar os SVGs
reais do tema Aurorae numa etapa seguinte, se aprovado.
Uso: proposta-decoracao.py SAIDA.html
"""
import sys

C = {"k": "#2B2A28", "w": "#F2EBDD", "p": "#E4D9C4", "q": "#EBE3D2", "r": "#C8102E",
     "d": "#8E0B22", "m": "#8C857A", "s": "#5B5650", "x": "#24221F"}

def vazio(fundo): return [["k"] * 12] + [["k"] + [fundo] * 10 + ["k"] for _ in range(10)] + [["k"] * 12]

def glifo(nome, fundo, tinta):
    g = vazio(fundo)
    def p(x, y): g[y][x] = tinta
    if nome == "min":
        for x in range(3, 9): p(x, 7); p(x, 8)
    elif nome == "max":
        for x in range(3, 9): p(x, 3); p(x, 4); p(x, 8)
        for y in range(3, 9): p(3, y); p(8, y)
    elif nome == "restore":
        for x in range(5, 9): p(x, 2); p(x, 3)
        for y in range(2, 7): p(8, y)
        for x in range(3, 7): p(x, 5); p(x, 6); p(x, 9)
        for y in range(5, 10): p(3, y); p(6, y)
    elif nome == "close":
        for i in range(6):
            p(3 + i, 3 + i); p(8 - i, 3 + i)
            if i < 5: p(4 + i, 3 + i); p(7 - i, 3 + i)
    elif nome == "pin":        # manter acima / fixar
        for x in range(4, 8): p(x, 2)
        for y in range(3, 6): p(4, y); p(7, y)
        for x in range(3, 9): p(x, 6)
        for y in range(7, 10): p(5, y); p(6, y)
    return g

ESTADOS = {   # (fundo, tinta, cor da moldura)
    "normal":      ("p", "k", "k"),
    "foco":        ("w", "r", "k"),
    "pressionado": ("k", "w", "k"),
    "inativo":     ("q", "m", "m"),
}
def estado_close(e):
    return {"normal": ("r", "w", "k"), "foco": ("d", "w", "k"), "pressionado": ("k", "r", "k"),
            "inativo": ("q", "m", "m")}[e]

def svg(g, borda, tam=24):
    rects = []
    for y, linha in enumerate(g):
        for x, c in enumerate(linha):
            cor = C[borda] if c == "k" and (x in (0, 11) or y in (0, 11)) else C[c]
            rects.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{cor}"/>')
    return (f'<svg viewBox="0 0 12 12" width="{tam}" height="{tam}" shape-rendering="crispEdges">'
            + "".join(rects) + "</svg>")

def botao(nome, estado, tam=24):
    fundo, tinta, borda = estado_close(estado) if nome == "close" else ESTADOS[estado]
    return svg(glifo(nome, fundo, tinta), borda, tam)

def janela(titulo, ativa=True, zoom=1):
    st = "normal" if ativa else "inativo"
    botoes = "".join(f'<span class="b">{botao(n, st, 24 * zoom)}</span>' for n in ("pin", "min", "max", "close"))
    cls = "jan" + ("" if ativa else " inat")
    return f'''<div class="sombra{' inat' if not ativa else ''}" style="--z:{zoom}"><div class="{cls}" style="--z:{zoom}">
  <div class="tb"><span class="ic"><img src="../icons/washi-pixel/apps/scalable/utilities-terminal.svg" width="{16*zoom}" height="{16*zoom}" alt=""></span>
  <span class="t">{titulo}</span><span class="bs">{botoes}</span></div>
  <div class="corpo"><div class="barra">Nova aba · Dividir a exibição</div><pre>ukiyo@ukiyo:~/ukiyo$ ▌</pre></div></div></div>'''

def pagina():
    linhas = ""
    for e in ESTADOS:
        cel = "".join(f"<td>{botao(n, e, 48)}</td>" for n in ("pin", "min", "max", "restore", "close"))
        linhas += f"<tr><th>{e}</th>{cel}</tr>"
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Proposta — decoração Washi Pixel</title>
<style>
:root{{--washi:#F2EBDD;--washi2:#E4D9C4;--q:#EBE3D2;--sumi:#2B2A28;--torii:#C8102E;--sec:#5B5650;--m:#8C857A}}
body{{margin:0;background:var(--washi);color:var(--sumi);font:15px/1.55 "Noto Sans",sans-serif}}
main{{max-width:1180px;margin:0 auto;padding:24px 18px 60px}}
h1,h2,h3{{font-family:"DotGothic16",monospace;font-weight:normal}} h1{{font-size:30px;margin:0 0 4px}}
h2{{font-size:21px;margin:34px 0 10px;border-bottom:2px solid var(--sumi);padding-bottom:3px}}
.sub{{color:var(--sec)}} .aviso{{border:2px solid var(--sumi);background:#fff8ec;padding:10px 14px;box-shadow:4px 4px 0 rgba(43,42,40,.25)}}
.duas{{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}} @media(max-width:900px){{.duas{{grid-template-columns:1fr}}}}
figure{{margin:0}} figcaption{{font-family:"DotGothic16",monospace;margin:0 0 8px}}
.real{{width:100%;border:2px dashed var(--m)}}
.zoomwrap{{overflow-x:auto}}
.jan{{--z:1;width:calc(410px*var(--z));border:calc(2px*var(--z)) solid var(--sumi);background:#24221F;
      margin:0;
      clip-path:polygon(0 calc(4px*var(--z)),calc(2px*var(--z)) calc(4px*var(--z)),calc(2px*var(--z)) calc(2px*var(--z)),calc(4px*var(--z)) calc(2px*var(--z)),calc(4px*var(--z)) 0,calc(100% - 4px*var(--z)) 0,calc(100% - 4px*var(--z)) calc(2px*var(--z)),calc(100% - 2px*var(--z)) calc(2px*var(--z)),calc(100% - 2px*var(--z)) calc(4px*var(--z)),100% calc(4px*var(--z)),100% 100%,0 100%);
      overflow:visible}}
.jan .tb{{height:calc(30px*var(--z));background:var(--washi2);border-bottom:calc(2px*var(--z)) solid var(--sumi);display:flex;align-items:center;gap:calc(6px*var(--z));padding:0 calc(4px*var(--z)) 0 calc(8px*var(--z))}}
.jan .tb .t{{flex:1;text-align:center;font:calc(16px*var(--z))/1 "DotGothic16",monospace}}
.jan .tb .bs{{display:flex;gap:calc(3px*var(--z))}} .jan .b svg,.jan img{{display:block;image-rendering:pixelated}}
.jan .corpo{{background:#24221F;color:#EDE6D6}} .jan .barra{{background:var(--washi2);color:var(--sumi);font-size:calc(13px*var(--z));padding:calc(5px*var(--z)) calc(10px*var(--z));border-bottom:1px solid #d6c8ae}}
.jan pre{{margin:0;padding:calc(8px*var(--z)) calc(10px*var(--z));font:calc(13px*var(--z)) "DejaVu Sans Mono",monospace;height:calc(70px*var(--z))}}
.sombra{{--z:1;width:max-content;margin:0 0 calc(20px*var(--z));filter:drop-shadow(calc(5px*var(--z)) calc(5px*var(--z)) 0 rgba(43,42,40,.38))}}
.sombra.inat{{filter:drop-shadow(calc(3px*var(--z)) calc(3px*var(--z)) 0 rgba(43,42,40,.18))}}
.jan.inat{{border-color:var(--m)}}
.jan.inat .tb{{background:var(--q);border-bottom-color:var(--m);color:var(--sec)}}
table{{border-collapse:collapse;background:#fffaf1;font-size:14px}} th,td{{border:2px solid var(--sumi);padding:7px 9px;vertical-align:top;text-align:left}}
th{{background:var(--washi2);font-family:"DotGothic16",monospace;font-weight:normal}}
.bt td{{text-align:center}} .bt svg{{image-rendering:pixelated}}
.tag{{display:inline-block;font:13px "DotGothic16",monospace;padding:1px 7px;border:2px solid var(--sumi);white-space:nowrap}}
.ok{{background:#dfe8d3}} .au{{background:#f6e6bf}} .no{{background:#f3d3d6}}
.tabela{{overflow-x:auto}} code{{background:var(--washi2);padding:1px 5px}} li{{margin-bottom:5px}}
</style></head><body><main>
<h1>Decoração de janelas — Washi Pixel</h1>
<p class="sub">Proposta para decidir. Nada foi aplicado; a decoração atual (Breeze recolorido) continua ativa.</p>
<div class="aviso"><b>Real × conceito.</b> À esquerda, uma captura real da janela de agora. À direita, uma maquete HTML do tema
proposto: os botões já são as grades de pixels finais, e moldura, cantos e sombra mostram a intenção.
O resultado exato no KWin só se confirma instalando o tema, que é reversível.</div>

<h2>Atual × proposta</h2>
<div class="duas">
<figure><figcaption>REAL · Breeze recolorido (hoje)</figcaption><img class="real" src="../../../docs/visual/capturas/titulo-breeze-atual.png" alt="captura real"></figure>
<figure><figcaption>CONCEITO · Aurorae "Washi Pixel"</figcaption>{janela("ukiyo : bash — Konsole")}{janela("TikTok — Dolphin", ativa=False)}</figure>
</div>

<h2>Ampliação 2× do conceito (pixels nítidos)</h2>
<div class="zoomwrap">{janela("ukiyo : bash — Konsole", zoom=2)}</div>

<h2>Botões — grade 12×12 desenhada a 2× (24 px)</h2>
<div class="tabela"><table class="bt"><tr><th>estado</th><th>manter acima</th><th>minimizar</th><th>maximizar</th><th>restaurar</th><th>fechar</th></tr>{linhas}</table></div>
<p>Fechar é o único botão vermelho, para ser achado rápido. No foco, o desenho fica vermelho-torii; pressionado, as cores se invertem.
Janela inativa: cinza-pedra, para ficar claro qual janela está com o foco. Nenhum estado é animado.</p>

<h2>O que o Breeze recolorido já permite (sem tema próprio)</h2>
<div class="tabela"><table>
<tr><th>Ajuste</th><th>Onde</th><th>Efeito</th></tr>
<tr><td>Cores da barra e do texto (ativa e inativa)</td><td>esquema Washi (já aplicado)</td><td>washi2 / sumi</td></tr>
<tr><td>Fonte do título</td><td><code>kdeglobals [WM] activeFont</code> (já aplicado)</td><td>DotGothic16</td></tr>
<tr><td>Contorno e sombra</td><td><code>breezerc</code> (já aplicado: contorno alto, sombra pequena)</td><td>sombra sempre suave, com desfoque; não fica dura nem deslocada</td></tr>
<tr><td>Espessura da borda</td><td><code>kwinrc BorderSize</code>: Nenhuma … Enorme</td><td>borda lisa; sem moldura de 2 px desenhada</td></tr>
<tr><td>Tamanho dos botões, alinhamento do título, ordem dos botões</td><td>Configurações → Decoração</td><td>os botões continuam com o desenho Breeze</td></tr>
</table></div>

<h2>O que exige um tema próprio (Aurorae)</h2>
<div class="tabela"><table>
<tr><th>Elemento</th><th>Breeze</th><th>Aurorae Washi Pixel</th></tr>
<tr><td>Desenho dos botões (pixel, × vermelho, estados próprios)</td><td><span class="tag no">não</span> desenho fixo do Breeze</td><td><span class="tag ok">sim</span> um SVG por botão, com estados normal, foco, pressionado e inativo</td></tr>
<tr><td>Cantos em degrau (pixel)</td><td><span class="tag no">não</span> cantos arredondados fixos</td><td><span class="tag ok">sim</span> cantos desenhados no SVG da moldura</td></tr>
<tr><td>Moldura sumi de 2 px e linha sob a barra de título</td><td><span class="tag no">não</span> há só o contorno fino</td><td><span class="tag ok">sim</span></td></tr>
<tr><td>Sombra dura deslocada (como na maquete)</td><td><span class="tag no">não</span></td><td><span class="tag au">a validar</span> o Aurorae desenha a sombra dentro de margens extras da moldura; é preciso conferir se elas atrapalham o clique na borda e o encaixe das janelas lado a lado</td></tr>
<tr><td>Janela maximizada sem moldura</td><td><span class="tag ok">sim</span></td><td><span class="tag ok">sim</span> com margens separadas para janela maximizada</td></tr>
<tr><td>Fonte do título DotGothic16</td><td><span class="tag ok">sim</span></td><td><span class="tag ok">sim</span> usa a mesma configuração</td></tr>
<tr><td>Apps GTK com barra própria (ex.: diálogos)</td><td>imitam o Breeze</td><td><span class="tag au">a validar</span> o Plasma também desenha os botões GTK a partir de temas Aurorae; conferir na prática</td></tr>
<tr><td>Firefox</td><td colspan="2">desenha a própria barra (abas no lugar do título); não é afetado por nenhuma das duas</td></tr>
</table></div>

<h2>Compatibilidade com o Plasma instalado</h2>
<ul>
<li>KWin 6.3.6 com o motor <code>org.kde.kwin.aurorae</code> já instalado (pacote <code>kwin-common</code>); hoje não há nenhum tema Aurorae instalado.</li>
<li>O tema fica em <code>~/.local/share/aurorae/themes/WashiPixel/</code>: <code>metadata.json</code>, <code>decoration.svg</code> (moldura em 9 partes, ativa e inativa),
um SVG por botão (<code>close</code>, <code>minimize</code>, <code>maximize</code>, <code>restore</code>, <code>keepabove</code>, <code>alldesktops</code>…) e <code>WashiPixelrc</code> (margens, tamanho dos botões, cores do título, animação 0).</li>
<li>Ativação: <code>kwinrc [org.kde.kdecoration2] library=org.kde.kwin.aurorae</code> e <code>theme=__aurorae__svg__WashiPixel</code>, seguido de <code>reconfigure</code> (não precisa de novo login).</li>
<li>Para desfazer: voltar a <code>library=org.kde.breeze</code> e <code>theme=Breeze</code>. Não usa sudo e não toca nos painéis, no OBS nem no áudio.</li>
<li>Escala: a tela está em 100%. Os botões de 24 px (grade de 12 a 2×) e a moldura de 2 px saem nítidos. Se um dia a escala mudar para 125% ou 150%, os pixels deixam de ser exatos.</li>
</ul>

<h2>Custos e riscos</h2>
<ul>
<li><b>Desempenho:</b> o Breeze é escrito em C++; o Aurorae monta cada barra de título em QML e desenha a partir de SVG. Gasta um pouco mais de memória por janela
e redesenha ao passar o mouse e ao trocar o foco. Com janelas paradas durante uma gravação, a diferença esperada é desprezível. Plano: medir a CPU do KWin com o OBS gravando, antes e depois.</li>
<li><b>Manutenção:</b> o Aurorae é estável há anos, mas recebe menos atenção que o Breeze. O tema fica isolado em uma pasta e volta ao Breeze com 2 linhas.</li>
<li><b>O que se perde em relação ao Breeze:</b> o contorno de contraste automático e alguns ajustes finos das Configurações. Os botões têm tamanho fixo, definido no tema.</li>
<li><b>Fora do escopo:</b> decoração própria em C++ (KDecoration3) dá controle total, mas exige compilar e manter um plugin a cada atualização do Plasma. Não recomendo.</li>
</ul>

<h2>Etapas sugeridas se aprovado (V2b)</h2>
<ol>
<li>Gerar os SVGs do tema a partir destas grades (<code>tools/gerar-decoracao.py</code>), primeiro <b>sem</b> sombra dura.</li>
<li>Backup de <code>kwinrc</code>, aplicar, conferir janela ativa e inativa, maximizada, diálogos e GTK; medir a CPU.</li>
<li>Testar a sombra dura numa segunda versão; manter só se não atrapalhar o redimensionamento nem o encaixe das janelas.</li>
<li>Scripts de aplicar e restaurar, com o registro em <code>docs/mudancas.md</code>.</li>
</ol>
</main></body></html>'''

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "proposta-decoracao.html"
    open(out, "w").write(pagina()); print(out)
