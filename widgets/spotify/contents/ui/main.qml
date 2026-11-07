import QtQuick
import QtQuick.Layouts
import QtQml.Models
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PC
import org.kde.plasma.plasma5support as P5
import org.kde.plasma.private.mpris as Mpris
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    switchWidth: Kirigami.Units.gridUnit * 24
    switchHeight: Kirigami.Units.gridUnit * 16
    readonly property var player: {
        const p = players.currentPlayer;
        return p && p.identity.toLowerCase().indexOf("spotify") >= 0 ? p : null;
    }
    readonly property bool playing: player?.playbackStatus === Mpris.PlaybackStatus.Playing
    readonly property string track: player?.track || "Spotify"
    readonly property string artist: player?.artist || "Escolha uma música no aplicativo"
    readonly property string art: player?.artUrl || ""
    property int volume: 0
    property bool volumeAvailable: false
    property string volumeError: ""
    property int pendingVolume: 0
    readonly property string helper: decodeURIComponent(Qt.resolvedUrl("../code/volume-spotify").toString().replace("file://", ""))
    Plasmoid.icon: "multimedia-audio-player"
    toolTipMainText: track
    toolTipSubText: player ? artist + "\nClique para abrir os controles" : "Abra o Spotify para ouvir"
    toolTipTextFormat: Text.PlainText

    function selectSpotify() {
        for (let i = 0; i < entries.count; i++) {
            const entry = entries.objectAt(i);
            if (entry && !entry.isMultiplexer && entry.identity.toLowerCase().indexOf("spotify") >= 0) {
                players.currentIndex = entry.index;
                return;
            }
        }
    }
    function readVolume() { exec.connectSource("'" + helper + "' ler"); }
    function setVolume(value) {
        pendingVolume = Math.round(value);
        volumeDelay.restart();
    }
    Mpris.Mpris2Model { id: players }
    Instantiator {
        id: entries
        model: players
        delegate: QtObject {
            required property int index
            required property string identity
            required property bool isMultiplexer
            onIdentityChanged: Qt.callLater(root.selectSpotify)
        }
        onObjectAdded: Qt.callLater(root.selectSpotify)
        onObjectRemoved: Qt.callLater(root.selectSpotify)
    }
    P5.DataSource {
        id: exec
        engine: "executable"
        connectedSources: []
        onNewData: function(source, data) {
            try {
                const state = JSON.parse(data.stdout || "{}");
                root.volumeAvailable = state.disponivel === true;
                root.volume = state.volume || 0;
                root.volumeError = state.erro || "";
            } catch (e) {
                root.volumeAvailable = false;
                root.volumeError = "Não foi possível ler o volume.";
            }
            disconnectSource(source);
        }
    }
    Timer {
        id: volumeDelay
        interval: 120
        onTriggered: exec.connectSource("'" + root.helper + "' definir " + root.pendingVolume)
    }
    Timer {
        interval: 2000
        repeat: true
        running: root.expanded
        onTriggered: root.readVolume()
    }
    onExpandedChanged: function () { if (root.expanded) root.readVolume(); }

    compactRepresentation: RowLayout {
        spacing: 5
        Layout.minimumWidth: 190
        Layout.preferredWidth: 240
        Item {
            Layout.preferredWidth: 24
            Layout.preferredHeight: 24
            Image { id: tinyArt; anchors.fill: parent; source: root.art; fillMode: Image.PreserveAspectCrop; asynchronous: true }
            Kirigami.Icon { anchors.fill: parent; source: "audio-x-generic"; visible: tinyArt.status !== Image.Ready }
            MouseArea { anchors.fill: parent; onClicked: root.expanded = !root.expanded; Accessible.name: "Abrir controles do Spotify" }
        }
        PC.Label {
            color: Kirigami.Theme.textColor;
            Layout.fillWidth: true
            Layout.maximumWidth: 150
            text: root.track
            textFormat: Text.PlainText
            elide: Text.ElideRight
            font.pixelSize: 12
            MouseArea { anchors.fill: parent; onClicked: root.expanded = !root.expanded }
        }
        PC.ToolButton {
            icon.color: Kirigami.Theme.textColor;
            implicitWidth: 24; implicitHeight: 26
            icon.name: "media-skip-backward"
            text: "Anterior"; display: PC.AbstractButton.IconOnly
            enabled: root.player?.canGoPrevious ?? false
            onClicked: root.player.Previous()
        }
        PC.ToolButton {
            icon.color: Kirigami.Theme.textColor;
            implicitWidth: 24; implicitHeight: 26
            icon.name: root.playing ? "media-playback-pause" : "media-playback-start"
            text: root.playing ? "Pausar" : "Tocar"; display: PC.AbstractButton.IconOnly
            enabled: root.playing ? (root.player?.canPause ?? false) : (root.player?.canPlay ?? false)
            onClicked: root.player.PlayPause()
        }
        PC.ToolButton {
            icon.color: Kirigami.Theme.textColor;
            implicitWidth: 24; implicitHeight: 26
            icon.name: "media-skip-forward"
            text: "Próxima"; display: PC.AbstractButton.IconOnly
            enabled: root.player?.canGoNext ?? false
            onClicked: root.player.Next()
        }
    }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: 340
        Layout.minimumWidth: 300
        spacing: 12
        PC.Label {
            color: Kirigami.Theme.textColor; text: "Spotify"; font.family: "DotGothic16"; font.pixelSize: 20 }
        RowLayout {
            spacing: 14
            Item {
                Layout.preferredWidth: 88; Layout.preferredHeight: 88
                Image { id: albumArt; anchors.fill: parent; source: root.art; fillMode: Image.PreserveAspectCrop; asynchronous: true }
                Kirigami.Icon { anchors.fill: parent; source: "audio-x-generic"; visible: albumArt.status !== Image.Ready }
            }
            ColumnLayout {
                Layout.fillWidth: true
                PC.Label {
            color: Kirigami.Theme.textColor; text: root.track; textFormat: Text.PlainText; font.bold: true; wrapMode: Text.Wrap; maximumLineCount: 2; elide: Text.ElideRight; Layout.fillWidth: true }
                PC.Label {
            color: Kirigami.Theme.textColor; text: root.artist; textFormat: Text.PlainText; opacity: 0.7; wrapMode: Text.Wrap; maximumLineCount: 2; elide: Text.ElideRight; Layout.fillWidth: true }
            }
        }
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            PC.ToolButton {
            icon.color: Kirigami.Theme.textColor; text: "Anterior"; icon.name: "media-skip-backward"; display: PC.AbstractButton.IconOnly; enabled: root.player?.canGoPrevious ?? false; onClicked: root.player.Previous() }
            PC.ToolButton {
            icon.color: Kirigami.Theme.textColor; text: root.playing ? "Pausar" : "Tocar"; icon.name: root.playing ? "media-playback-pause" : "media-playback-start"; display: PC.AbstractButton.IconOnly; enabled: root.playing ? (root.player?.canPause ?? false) : (root.player?.canPlay ?? false); onClicked: root.player.PlayPause() }
            PC.ToolButton {
            icon.color: Kirigami.Theme.textColor; text: "Próxima"; icon.name: "media-skip-forward"; display: PC.AbstractButton.IconOnly; enabled: root.player?.canGoNext ?? false; onClicked: root.player.Next() }
        }
        Kirigami.Separator { Layout.fillWidth: true }
        RowLayout {
            PC.Label {
            color: Kirigami.Theme.textColor; text: "Volume do Spotify"; Layout.fillWidth: true }
            PC.Label {
            color: Kirigami.Theme.textColor; text: root.volumeAvailable ? volumeSlider.value + "%" : "—" }
        }
        PC.Slider {
            id: volumeSlider
            Layout.fillWidth: true
            from: 0; to: 100; stepSize: 1
            value: root.volume
            enabled: root.volumeAvailable
            Accessible.name: "Volume do Spotify"
            onMoved: root.setVolume(value)
        }
        PC.Label {
            color: Kirigami.Theme.textColor;
            Layout.fillWidth: true
            text: root.volumeError || (!root.volumeAvailable ? "Inicie uma música para liberar o volume." : "Ajusta só o Spotify.")
            wrapMode: Text.Wrap; opacity: 0.65; font.pixelSize: 12
        }
    }
}
