"""Henshū 編集 — editor de vídeo com chat (Claude ou Codex editam enquanto você assiste).

Janela: prévia 9:16 + linha do tempo à esquerda, chat à direita. O agente edita `projeto.json` na pasta do vídeo;
o Henshū percebe a mudança, refaz a prévia na GPU e recarrega o player.
Uso: henshu [pasta-do-vídeo]
"""
import html, json, os, shutil, subprocess, sys, time
from PySide6.QtCore import Qt, QTimer, QUrl, QProcess, QFileSystemWatcher, QRectF, Signal, QSize
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QKeySequence, QShortcut, QAction, QIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QSlider, QTextBrowser, QPlainTextEdit, QComboBox, QFileDialog,
                               QInputDialog, QMessageBox, QToolBar, QStatusBar, QSizePolicy, QCheckBox, QDialog,
                               QTableWidget, QTableWidgetItem, QDialogButtonBox, QHeaderView)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from . import projeto as P, render as R, agentes as A, legendas as L, kdenlive as K

RAIZ = os.path.join(os.path.expanduser("~"), "Vídeos", "TikTok")
PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TIKTOK = os.path.join(PROJ, "producao", "tiktok.sh")
PY_VENV = os.path.join(PROJ, ".venv", "bin", "python")
EDITOR = os.path.join(PROJ, "editor")
COR = {"clipe": "#c8343b", "clipe2": "#8e2335", "texto": "#d9a441", "musica": "#4f6b3a", "cabeca": "#f2ebdd", "legenda": "#5a7aa8",
       "fundo": "#1b1a22", "faixa": "#24222b", "rotulo": "#a9a3b5"}


def mmss(s):
    s = max(0, s); return f"{int(s // 60)}:{s % 60:04.1f}"


# ---------------------------------------------------------------------------------------------------------------
class LinhaDoTempo(QWidget):
    """Quatro faixas (vídeo, textos, legendas, música) em proporção à duração; clique para posicionar."""
    pedirPosicao = Signal(float)
    FAIXAS = [("vídeo", 8), ("textos", 40), ("legendas", 72), ("música", 104)]

    def __init__(self):
        super().__init__(); self.setMinimumHeight(138); self.clipes, self.textos, self.legendas, self.musica = [], [], [], None
        self.caps, self.total, self.pos = [], 0.0, 0.0
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def definir(self, clipes, textos, legendas, musica, caps, total):
        self.clipes, self.textos, self.legendas, self.musica, self.caps, self.total = clipes, textos, legendas, musica, caps, total
        self.update()

    def posicao(self, s):
        self.pos = s; self.update()

    def _x(self, s, w0, w):
        return w0 + (s / self.total * w if self.total else 0)

    def mousePressEvent(self, e):
        w0, w = 70, self.width() - 80
        if self.total and e.position().x() >= w0:
            self.pedirPosicao.emit(min(self.total, max(0, (e.position().x() - w0) / w * self.total)))

    mouseMoveEvent = mousePressEvent

    def _bloco(self, p, x, y, larg, cor, texto, cor_txt="#ffffff"):
        r = QRectF(x, y, max(2, larg), 26); p.fillRect(r, QColor(cor)); p.setPen(QColor(cor_txt))
        p.drawText(r.adjusted(4, 0, -2, 0), Qt.AlignVCenter, texto); return r

    def paintEvent(self, _):
        p = QPainter(self); p.fillRect(self.rect(), QColor(COR["fundo"]))
        f = QFont(self.font()); f.setPointSize(8); p.setFont(f)
        w0, w = 70, self.width() - 80
        for nome, y in self.FAIXAS:
            p.fillRect(QRectF(w0, y, w, 26), QColor(COR["faixa"]))
            p.setPen(QColor(COR["rotulo"])); p.drawText(QRectF(6, y, 60, 26), Qt.AlignVCenter, nome)
        if not self.total:
            p.setPen(QColor(COR["rotulo"])); p.drawText(QRectF(w0, 8, w, 120), Qt.AlignCenter, "projeto vazio — peça no chat")
            return
        k = w / self.total
        for i, c in enumerate(self.clipes):
            rot = os.path.basename(c["arquivo"]) + (f"  {c['velocidade']:g}×" if c["velocidade"] != 1 else "") \
                  + ("  ⤢" if c["enquadrar"] == "preencher" else "")
            r = self._bloco(p, self._x(c["na_linha"], w0, w), 8, c["duracao"] * k - 1, COR["clipe"] if i % 2 == 0 else COR["clipe2"], rot)
            if c["sobreposicao"]:   # dissolver: faixa listrada na sobreposição
                p.fillRect(QRectF(r.right() - c["sobreposicao"] * k, 8, c["sobreposicao"] * k, 26), QBrush(QColor("#f2ebdd"), Qt.BDiagPattern))
            if c["transicao"]["tipo"] == "fade" and i < len(self.clipes) - 1:
                p.fillRect(QRectF(r.right() - 4, 8, 6, 26), QColor("#000000"))
        for t in self.textos:
            self._bloco(p, self._x(t["inicio"], w0, w), 40, (min(t["fim"], self.total) - t["inicio"]) * k, COR["texto"],
                        t["texto"].replace("\n", " "), "#1b1a22")
        for sg in self.legendas:
            self._bloco(p, self._x(sg["inicio"], w0, w), 72, (sg["fim"] - sg["inicio"]) * k - 1, COR["legenda"], sg["texto"])
        if self.musica:
            self._bloco(p, w0, 104, w, COR["musica"], f"{os.path.basename(self.musica['arquivo'])}  ·  volume {self.musica['volume']}")
        p.setPen(QPen(QColor("#f2ebdd"), 1, Qt.DotLine))
        for c in self.caps:   # capítulos: linhas pontilhadas
            x = self._x(c["inicio"], w0, w); p.drawLine(int(x), 2, int(x), self.height() - 2)
        x = self._x(self.pos, w0, w); p.setPen(QPen(QColor(COR["cabeca"]), 2)); p.drawLine(int(x), 2, int(x), self.height() - 2)


# ---------------------------------------------------------------------------------------------------------------
class Chat(QWidget):
    enviar = Signal(str, str)      # agente, mensagem
    parar = Signal()
    novaConversa = Signal(str)

    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self); lay.setContentsMargins(6, 6, 6, 6)
        topo = QHBoxLayout()
        topo.addWidget(QLabel("Quem edita:"))
        self.agente = QComboBox()
        for k, nome in A.AGENTES.items():
            self.agente.addItem(nome + ("" if A.disponivel(k) else " (não instalado)"), k)
        topo.addWidget(self.agente, 1)
        self.btn_nova = QPushButton("Nova conversa"); topo.addWidget(self.btn_nova)
        lay.addLayout(topo)
        self.log = QTextBrowser(); self.log.setOpenExternalLinks(False); lay.addWidget(self.log, 1)
        self.estado = QLabel(""); self.estado.setStyleSheet("color:#a9a3b5"); lay.addWidget(self.estado)
        self.caixa = QPlainTextEdit(); self.caixa.setPlaceholderText("Diga o que fazer no vídeo… (Enter envia, Shift+Enter quebra linha)")
        self.caixa.setFixedHeight(84); self.caixa.installEventFilter(self); lay.addWidget(self.caixa)
        baixo = QHBoxLayout(); baixo.addStretch(1)
        self.btn_parar = QPushButton("Parar"); self.btn_parar.setEnabled(False); baixo.addWidget(self.btn_parar)
        self.btn_enviar = QPushButton("Enviar"); self.btn_enviar.setDefault(True); baixo.addWidget(self.btn_enviar)
        lay.addLayout(baixo)
        self.btn_enviar.clicked.connect(self._enviar); self.btn_parar.clicked.connect(self.parar)
        self.btn_nova.clicked.connect(lambda: self.novaConversa.emit(self.agente.currentData()))

    def eventFilter(self, obj, ev):
        if obj is self.caixa and ev.type() == ev.Type.KeyPress and ev.key() in (Qt.Key_Return, Qt.Key_Enter) \
                and not ev.modifiers() & Qt.ShiftModifier:
            self._enviar(); return True
        return super().eventFilter(obj, ev)

    def _enviar(self):
        msg = self.caixa.toPlainText().strip()
        if msg and self.btn_enviar.isEnabled():
            self.caixa.clear(); self.enviar.emit(self.agente.currentData(), msg)

    def ocupado(self, sim, texto=""):
        self.btn_enviar.setEnabled(not sim); self.btn_parar.setEnabled(sim); self.agente.setEnabled(not sim)
        self.estado.setText(texto)

    def adicionar(self, quem, texto, tipo="texto"):
        t = html.escape(texto).replace("\n", "<br>")
        if tipo == "voce":
            self.log.append(f'<p style="margin:8px 0 2px 0"><b style="color:#d9a441">você</b><br>{t}</p>')
        elif tipo == "acao":
            self.log.append(f'<p style="margin:0;color:#8f89a0;font-size:small">↳ {t}</p>')
        elif tipo == "erro":
            self.log.append(f'<p style="margin:4px 0;color:#e8694a">⚠ {t}</p>')
        elif tipo == "sistema":
            self.log.append(f'<p style="margin:4px 0;color:#8f89a0;font-style:italic">{t}</p>')
        else:
            self.log.append(f'<p style="margin:6px 0 2px 0"><b style="color:#c8a2f0">{html.escape(quem)}</b><br>{t}</p>')
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())


# ---------------------------------------------------------------------------------------------------------------
class Janela(QMainWindow):
    def __init__(self, pasta=None):
        super().__init__()
        self.setWindowTitle("Henshū 編集"); self.resize(1500, 900)
        self.pasta = None; self.sessoes = {}; self.proc_agente = None; self.agente_atual = None; self.buffer = ""
        self.proc_render = None; self.render_pendente = False; self.retomar_em = 0

        self.proc_transc = None; self.proc_export = None
        tb = QToolBar(); tb.setMovable(False); self.addToolBar(tb)
        for rot, fn in [("Novo vídeo", self.novo), ("Abrir vídeo", self.abrir), ("Importar mídia", self.importar)]:
            a = QAction(rot, self); a.triggered.connect(fn); tb.addAction(a)
        tb.addSeparator()
        self.cb_preset = QComboBox()
        for k, v in P.PRESETS.items(): self.cb_preset.addItem(v["nome"], k)
        self.cb_preset.setToolTip("Vertical 9:16: TikTok, Reels, Shorts (1080×1920) · Horizontal 16:9: YouTube (1920×1080)")
        self.cb_preset.activated.connect(self.mudar_preset); tb.addWidget(self.cb_preset)
        tb.addSeparator()
        a = QAction("Transcrever", self); a.setToolTip("Transcreve as falas (local) e gera as legendas"); a.triggered.connect(self.transcrever); tb.addAction(a)
        self.ck_leg = QCheckBox("Legendas"); self.ck_leg.toggled.connect(self.mudar_legendas); tb.addWidget(self.ck_leg)
        self.cb_estilo = QComboBox()
        for k, v in P.ESTILOS_LEGENDA.items(): self.cb_estilo.addItem(v, k)
        self.cb_estilo.activated.connect(self.mudar_legendas); tb.addWidget(self.cb_estilo)
        a = QAction("Revisar legendas", self); a.triggered.connect(self.revisar_legendas); tb.addAction(a)
        tb.addSeparator()
        for rot, fn in [("Exportar final", self.exportar), ("SRT e capítulos", self.exportar_textos), ("Abrir no Kdenlive", self.abrir_kdenlive)]:
            a = QAction(rot, self); a.triggered.connect(fn); tb.addAction(a)
        self.lbl_video = QLabel(""); self.lbl_video.setContentsMargins(16, 0, 0, 0); tb.addWidget(self.lbl_video)

        # esquerda: player + transporte + linha do tempo
        esq = QWidget(); le = QVBoxLayout(esq); le.setContentsMargins(6, 6, 6, 6)
        self.video = QVideoWidget(); self.video.setMinimumSize(QSize(300, 420)); self.video.setStyleSheet("background:#000")
        le.addWidget(self.video, 1)
        tr = QHBoxLayout()
        self.btn_play = QPushButton("▶"); self.btn_play.setFixedWidth(44); tr.addWidget(self.btn_play)
        self.slider = QSlider(Qt.Horizontal); tr.addWidget(self.slider, 1)
        self.lbl_tempo = QLabel("0:00.0 / 0:00.0"); tr.addWidget(self.lbl_tempo)
        le.addLayout(tr)
        self.tl = LinhaDoTempo(); le.addWidget(self.tl)
        self.chat = Chat()
        sp = QSplitter(); sp.addWidget(esq); sp.addWidget(self.chat); sp.setStretchFactor(0, 3); sp.setStretchFactor(1, 2)
        sp.setSizes([900, 600]); self.setCentralWidget(sp)
        self.setStatusBar(QStatusBar())

        self.player = QMediaPlayer(); self.audio = QAudioOutput(); self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video)
        self.btn_play.clicked.connect(self.alternar_play); QShortcut(QKeySequence("Ctrl+Space"), self, self.alternar_play)
        self.player.positionChanged.connect(self._pos); self.player.durationChanged.connect(lambda d: (self.slider.setRange(0, d), self._pos(self.player.position())))
        self.player.playbackStateChanged.connect(lambda s: self.btn_play.setText("⏸" if s == QMediaPlayer.PlayingState else "▶"))
        self.player.mediaStatusChanged.connect(self._status_midia)
        self.slider.sliderMoved.connect(self.player.setPosition)
        self.tl.pedirPosicao.connect(lambda s: self.player.setPosition(int(s * 1000)))

        self.chat.enviar.connect(self.enviar); self.chat.parar.connect(self.parar_agente)
        self.chat.novaConversa.connect(self.nova_conversa)

        self.vigia = QFileSystemWatcher(); self.vigia.fileChanged.connect(self._mudou); self.vigia.directoryChanged.connect(self._mudou)
        self.atraso = QTimer(singleShot=True, interval=450); self.atraso.timeout.connect(self.atualizar)

        if pasta: self.carregar(pasta)
        else: QTimer.singleShot(0, self.abrir)

    # ---- pasta / projeto --------------------------------------------------------------------------------------
    def carregar(self, pasta):
        pasta = os.path.abspath(pasta)
        if not os.path.isdir(os.path.join(pasta, "brutos")):
            QMessageBox.warning(self, "Henshū", "Essa pasta não é um vídeo (falta brutos/). Use “Novo vídeo”."); return
        self.pasta = pasta; os.makedirs(os.path.join(pasta, ".henshu"), exist_ok=True)
        A.preparar_pasta(pasta)
        if not os.path.exists(P.caminho(pasta)): P.salvar(pasta, P.novo())
        try: self.sessoes = json.load(open(os.path.join(pasta, ".henshu", "sessoes.json")))
        except (OSError, ValueError): self.sessoes = {}
        if self.vigia.files(): self.vigia.removePaths(self.vigia.files())
        if self.vigia.directories(): self.vigia.removePaths(self.vigia.directories())
        os.makedirs(os.path.join(pasta, "legendas"), exist_ok=True)
        self.vigia.addPath(P.caminho(pasta)); self.vigia.addPath(pasta); self.vigia.addPath(os.path.join(pasta, "legendas"))
        if os.path.exists(os.path.join(pasta, L.ARQ)): self.vigia.addPath(os.path.join(pasta, L.ARQ))
        self.lbl_video.setText(f"<b>{os.path.basename(pasta)}</b>")
        self.chat.log.clear(); self._reler_chat()
        self.chat.adicionar("", f"Vídeo aberto: {pasta}. Brutos: {', '.join(sorted(os.listdir(os.path.join(pasta, 'brutos')))) or 'nenhum ainda'}", "sistema")
        self.atualizar()

    def _mudou(self, *_):
        if self.pasta:
            for f in (P.caminho(self.pasta), os.path.join(self.pasta, L.ARQ)):
                if f not in self.vigia.files() and os.path.exists(f): self.vigia.addPath(f)   # substituído: volta a vigiar
        self.atraso.start()

    def atualizar(self):
        """Relê o projeto, redesenha a linha do tempo e refaz a prévia (se nada estiver renderizando)."""
        if not self.pasta: return
        try:
            d = P.carregar(self.pasta); clipes, total = P.clipes_resolvidos(self.pasta, d)
        except (P.ErroProjeto, ValueError, KeyError, TypeError) as e:
            self.statusBar().showMessage(f"⚠ projeto: {e}"); return
        leg = L.carregar(self.pasta) if d["legendas"]["ativo"] else None
        self.tl.definir(clipes, d["textos"], (leg or {}).get("segmentos", []), d.get("musica"), d["capitulos"], total)
        for w, f in ((self.cb_preset, lambda: self.cb_preset.setCurrentIndex(self.cb_preset.findData(d["formato"]["preset"]))),
                     (self.ck_leg, lambda: self.ck_leg.setChecked(d["legendas"]["ativo"])),
                     (self.cb_estilo, lambda: self.cb_estilo.setCurrentIndex(self.cb_estilo.findData(d["legendas"]["estilo"])))):
            w.blockSignals(True); f(); w.blockSignals(False)
        if not clipes:
            self.player.setSource(QUrl()); self.statusBar().showMessage("Projeto vazio — peça no chat para montar o vídeo."); return
        if self.proc_render and self.proc_render.state() != QProcess.NotRunning:
            self.render_pendente = True; return
        self.retomar_em = self.player.position()
        tmp = os.path.join(self.pasta, ".henshu", "previa-nova.mp4")
        try: cmd, _ = R.comando_previa(self.pasta, d, tmp)
        except P.ErroProjeto as e:
            self.statusBar().showMessage(f"⚠ {e}"); return
        self.statusBar().showMessage("renderizando a prévia na GPU…"); self.t0 = time.time()
        pr = QProcess(self); pr.setProgram(cmd[0]); pr.setArguments(cmd[1:]); pr.setProcessChannelMode(QProcess.SeparateChannels)
        pr.finished.connect(lambda code, _s: self._render_fim(pr, code, tmp)); self.proc_render = pr; pr.start()

    def _render_fim(self, pr, code, tmp):
        if code == 0 and os.path.exists(tmp):
            final = R.caminho_previa(self.pasta)
            self.player.setSource(QUrl()); os.replace(tmp, final)
            self.player.setSource(QUrl.fromLocalFile(final))
            self.statusBar().showMessage(f"prévia atualizada em {time.time() - self.t0:.1f} s", 6000)
        else:
            err = bytes(pr.readAllStandardError()).decode(errors="replace").strip().splitlines()
            self.statusBar().showMessage("⚠ falha na prévia: " + (err[-1] if err else f"código {code}"))
        if self.render_pendente:
            self.render_pendente = False; self.atualizar()

    def _status_midia(self, st):
        if st == QMediaPlayer.LoadedMedia:      # mostra o quadro já (parado, o Qt não desenha nada)
            self.player.setPosition(self.retomar_em); self.retomar_em = 0
            if self.player.playbackState() != QMediaPlayer.PlayingState: self.player.pause()

    def _pos(self, ms):
        if not self.slider.isSliderDown(): self.slider.setValue(ms)
        self.lbl_tempo.setText(f"{mmss(ms / 1000)} / {mmss(self.player.duration() / 1000)}"); self.tl.posicao(ms / 1000)

    def alternar_play(self):
        self.player.pause() if self.player.playbackState() == QMediaPlayer.PlayingState else self.player.play()

    # ---- barra de ferramentas -----------------------------------------------------------------------------------
    def novo(self):
        nome, ok = QInputDialog.getText(self, "Novo vídeo", "Nome do vídeo (ex.: receita-de-bolo):")
        if not ok or not nome.strip(): return
        r = subprocess.run([TIKTOK, "novo", nome.strip()], capture_output=True, text=True)
        if r.returncode != 0:
            QMessageBox.warning(self, "Henshū", r.stderr.strip() or r.stdout.strip()); return
        self.carregar(r.stdout.strip().split("criado: ", 1)[-1])

    def abrir(self):
        os.makedirs(RAIZ, exist_ok=True)
        d = QFileDialog.getExistingDirectory(self, "Abrir vídeo (pasta em Vídeos/TikTok)", RAIZ)
        if d: self.carregar(d)

    def importar(self):
        if not self.pasta: return
        arqs, _ = QFileDialog.getOpenFileNames(self, "Importar mídia para brutos/", os.path.expanduser("~"),
                                               "Mídia (*.mp4 *.mov *.mkv *.webm *.m4v *.wav *.mp3 *.m4a *.flac *.ogg *.png *.jpg)")
        if not arqs: return
        r = subprocess.run([TIKTOK, "importar", *arqs], cwd=self.pasta, capture_output=True, text=True)
        self.chat.adicionar("", (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "importado", "sistema")

    def _editar_projeto(self, fn):
        """Altera o projeto.json preservando o resto (o vigia refaz a prévia)."""
        if not self.pasta: return
        try: d = P.ler_cru(self.pasta)
        except (OSError, ValueError) as e:
            self.statusBar().showMessage(f"⚠ não consegui ler o projeto: {e}"); return
        fn(d); P.salvar(self.pasta, d)

    def mudar_preset(self, *_):
        preset = self.cb_preset.currentData()
        self._editar_projeto(lambda d: d.update(formato=P.aplicar_preset({}, preset)["formato"]))
        self.chat.adicionar("", f"Formato: {P.PRESETS[preset]['nome']}. Clipes em outra orientação ficam com faixas — "
                                "peça “preencher a tela” no chat para reenquadrar.", "sistema")

    def mudar_legendas(self, *_):
        ativo, estilo = self.ck_leg.isChecked(), self.cb_estilo.currentData()
        if ativo and not L.carregar(self.pasta or "."):
            self.chat.adicionar("", "Ainda não há legendas: use “Transcrever” primeiro.", "sistema")
        self._editar_projeto(lambda d: d.update(legendas={**(d.get("legendas") or {}), "ativo": ativo, "estilo": estilo}))

    def transcrever(self):
        if not self.pasta or (self.proc_transc and self.proc_transc.state() != QProcess.NotRunning): return
        if not os.path.exists(PY_VENV):
            QMessageBox.warning(self, "Henshū", "Falta o ambiente Python do projeto: rode scripts/preparar-ambiente.sh"); return
        pr = QProcess(self); pr.setProgram(PY_VENV); pr.setArguments(["-m", "henshu.transcrever", self.pasta])
        pr.setWorkingDirectory(EDITOR); pr.setProcessChannelMode(QProcess.MergedChannels)
        def ler():
            for l in bytes(pr.readAllStandardOutput()).decode(errors="replace").splitlines():
                if l.startswith("PROGRESSO "):
                    _, pct, *resto = l.split(" ", 2); self.statusBar().showMessage(f"transcrevendo… {pct}% {' '.join(resto)}")
                elif l.startswith(("OK ", "ERRO ", "INFO ")):
                    self.chat.adicionar("", "Transcrição: " + l.split(" ", 1)[1], "erro" if l.startswith("ERRO") else "sistema")
        pr.readyReadStandardOutput.connect(ler)
        def fim(code, _s):
            ler(); self.statusBar().showMessage("transcrição concluída" if code == 0 else "⚠ a transcrição falhou", 8000)
            if code == 0 and not self.ck_leg.isChecked(): self.ck_leg.setChecked(True)   # liga as legendas na primeira vez
            self.atraso.start()
        pr.finished.connect(fim); self.proc_transc = pr
        self.statusBar().showMessage("transcrevendo (local, faster-whisper)…"); pr.start(); pr.closeWriteChannel()

    def revisar_legendas(self):
        if not self.pasta: return
        dados = L.carregar(self.pasta)
        if not dados or not dados.get("segmentos"):
            QMessageBox.information(self, "Henshū", "Ainda não há legendas. Use “Transcrever” primeiro."); return
        dlg = QDialog(self); dlg.setWindowTitle("Revisar legendas"); dlg.resize(760, 560); lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Corrija o texto de cada frase (os tempos vêm da transcrição). Clique duplo para editar."))
        tab = QTableWidget(len(dados["segmentos"]), 3); tab.setHorizontalHeaderLabels(["início", "fim", "texto"])
        tab.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        for r, sg in enumerate(dados["segmentos"]):
            for c, v in enumerate((mmss(sg["inicio"]), mmss(sg["fim"]))):
                it = QTableWidgetItem(v); it.setFlags(it.flags() & ~Qt.ItemIsEditable); tab.setItem(r, c, it)
            tab.setItem(r, 2, QTableWidgetItem(sg["texto"]))
        tab.cellClicked.connect(lambda r, _c: self.player.setPosition(int(dados["segmentos"][r]["inicio"] * 1000)))
        lay.addWidget(tab)
        bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); lay.addWidget(bb)
        bb.rejected.connect(dlg.reject); bb.accepted.connect(dlg.accept)
        if dlg.exec() == QDialog.Accepted:
            for r, sg in enumerate(dados["segmentos"]):
                novo = tab.item(r, 2).text().strip()
                if novo: sg["texto"] = novo
            L.salvar(self.pasta, dados); self.chat.adicionar("", "Legendas revisadas e salvas.", "sistema"); self.atraso.start()

    def exportar(self):
        if not self.pasta or (self.proc_export and self.proc_export.state() != QProcess.NotRunning): return
        pr = QProcess(self); pr.setProgram(sys.executable); pr.setArguments(["-m", "henshu.render", self.pasta, "--final"])
        pr.setWorkingDirectory(EDITOR); pr.setProcessChannelMode(QProcess.SeparateChannels)
        def fim(code, _s):
            out = bytes(pr.readAllStandardOutput()).decode(errors="replace").strip()
            err = bytes(pr.readAllStandardError()).decode(errors="replace").strip()
            msg = ("pronto:\n" + out) if code == 0 else ("falhou: " + err[-300:])
            self.statusBar().showMessage(msg.splitlines()[-1], 15000); self.chat.adicionar("", f"Exportação final {msg}", "sistema")
        pr.finished.connect(fim); self.proc_export = pr
        self.statusBar().showMessage("exportando a versão final (resolução cheia, −14 LUFS)…"); pr.start()

    def abrir_kdenlive(self):
        """Gera o projeto do Kdenlive a partir do projeto atual e o abre (para ajuste fino)."""
        if not self.pasta: return
        if not shutil.which("kdenlive"):
            QMessageBox.warning(self, "Henshū", "O Kdenlive não está instalado (sudo apt install kdenlive)."); return
        try: arq = K.exportar(self.pasta, P.carregar(self.pasta))
        except P.ErroProjeto as e:
            self.chat.adicionar("", str(e), "erro"); return
        QProcess.startDetached("kdenlive", [arq])
        extra = " (o .kdenlive anterior tinha ajustes seus e foi preservado)" if not arq.endswith(os.path.basename(self.pasta) + ".kdenlive") else ""
        self.chat.adicionar("", f"Abrindo no Kdenlive: {os.path.relpath(arq, self.pasta)}{extra}. "
                                "Mudanças feitas lá ficam só no Kdenlive; o projeto do Henshū continua como está.", "sistema")

    def exportar_textos(self):
        if not self.pasta: return
        try: feitos = R.exportar_textos(self.pasta, P.carregar(self.pasta))
        except P.ErroProjeto as e:
            self.chat.adicionar("", str(e), "erro"); return
        if feitos: self.chat.adicionar("", "Gerado: " + ", ".join(os.path.relpath(f, self.pasta) for f in feitos), "sistema")
        else: self.chat.adicionar("", "Nada para exportar: transcreva para ter o SRT; peça capítulos no chat (ex.: “crie capítulos”).", "sistema")

    # ---- chat / agentes ----------------------------------------------------------------------------------------
    def _salvar_chat(self, quem, texto, tipo):
        with open(os.path.join(self.pasta, ".henshu", "chat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"quem": quem, "texto": texto, "tipo": tipo}, ensure_ascii=False) + "\n")

    def _reler_chat(self):
        try:
            for l in open(os.path.join(self.pasta, ".henshu", "chat.jsonl"), encoding="utf-8"):
                e = json.loads(l); self.chat.adicionar(e["quem"], e["texto"], e["tipo"])
        except OSError:
            pass

    def _dizer(self, quem, texto, tipo="texto"):
        self.chat.adicionar(quem, texto, tipo); self._salvar_chat(quem, texto, tipo)

    def enviar(self, agente, msg):
        if not self.pasta: return
        if not A.disponivel(agente):
            self._dizer("", f"{A.AGENTES[agente]} não está instalado.", "erro"); return
        self._dizer("você", msg, "voce")
        cmd = A.comando(agente, msg, self.sessoes.get(agente))
        pr = QProcess(self); pr.setWorkingDirectory(self.pasta); pr.setProgram(cmd[0]); pr.setArguments(cmd[1:])
        pr.setProcessChannelMode(QProcess.SeparateChannels)
        pr.readyReadStandardOutput.connect(lambda: self._saida(pr, agente))
        pr.finished.connect(lambda code, _s: self._agente_fim(pr, agente, code))
        self.proc_agente, self.agente_atual, self.buffer = pr, agente, ""
        self.chat.ocupado(True, f"{A.AGENTES[agente]} está trabalhando… (a prévia se atualiza a cada mudança)")
        pr.start(); pr.closeWriteChannel()   # o Codex espera o fim da entrada padrão antes de começar

    def _saida(self, pr, agente):
        self.buffer += bytes(pr.readAllStandardOutput()).decode(errors="replace")
        *linhas, self.buffer = self.buffer.split("\n")
        for l in linhas:
            for e in A.eventos(agente, l):
                if e["tipo"] == "sessao" and e["texto"]:
                    self.sessoes[agente] = e["texto"]
                    json.dump(self.sessoes, open(os.path.join(self.pasta, ".henshu", "sessoes.json"), "w"))
                elif e["tipo"] in ("texto", "acao", "erro"):
                    self._dizer(A.AGENTES[agente], e["texto"], e["tipo"])

    def _agente_fim(self, pr, agente, code):
        self._saida(pr, agente)
        if code != 0:
            err = bytes(pr.readAllStandardError()).decode(errors="replace").strip()
            if err: self._dizer("", f"{A.AGENTES[agente]} terminou com erro: {err.splitlines()[-1][:300]}", "erro")
            if "login" in err.lower() or "auth" in err.lower():
                self._dizer("", f"Faça login no terminal: {agente} login", "sistema")
        self.chat.ocupado(False); self.proc_agente = None; self.atraso.start()

    def parar_agente(self):
        if self.proc_agente: self.proc_agente.kill(); self._dizer("", "interrompido por você", "sistema")

    def nova_conversa(self, agente):
        self.sessoes.pop(agente, None)
        if self.pasta: json.dump(self.sessoes, open(os.path.join(self.pasta, ".henshu", "sessoes.json"), "w"))
        self._dizer("", f"Nova conversa com {A.AGENTES[agente]} (o vídeo continua como está).", "sistema")

    def closeEvent(self, e):
        for pr in (self.proc_agente, self.proc_render, self.proc_transc, self.proc_export):
            if pr and pr.state() != QProcess.NotRunning: pr.kill(); pr.waitForFinished(2000)
        super().closeEvent(e)


def main():
    app = QApplication(sys.argv); app.setApplicationName("Henshū"); app.setDesktopFileName("henshu")
    w = Janela(sys.argv[1] if len(sys.argv) > 1 else None); w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
