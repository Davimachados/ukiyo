"""Copia isolada do widget para teste e captura do QML real com dados fictícios."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[3];tmp=Path('/tmp/ukiyo-spotify-preview');pkg=tmp/'share/plasma/plasmoids/org.ukiyo.spotify'
shutil.copytree(root/'widgets/spotify',pkg,dirs_exist_ok=True)
p=pkg/'contents/ui/main.qml';s=p.read_text().replace('fullRepresentation: ColumnLayout {','fullRepresentation: ColumnLayout {\n        id: previewView\n        Timer {\n            interval: 3500; running: true\n            onTriggered: {\n                root.player?.Next(); root.player?.PlayPause();\n                previewView.grabToImage(function(result) { result.saveToFile("/tmp/ukiyo-spotify-preview/widget.png"); Qt.quit(); });\n            }\n        }')
s=s.replace('    onExpandedChanged:', '    Component.onCompleted: { root.expanded = true; root.readVolume(); }\n    onExpandedChanged:')
s=s.replace('    id: root','    id: root\n    Kirigami.Theme.inherit: false\n    Kirigami.Theme.textColor: \"#e6e4ec\"\n    Kirigami.Theme.backgroundColor: \"#1c1e2e\"')
p.write_text(s)
helper=pkg/'contents/code/volume-spotify';helper.write_text('#!/bin/sh\nprintf \'{"disponivel":true,"volume":65}\\n\'\n');helper.chmod(0o755)
print(tmp)
