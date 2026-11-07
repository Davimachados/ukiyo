// Layout Washi V1 — executado pelo plasmashell (evaluateScript).
// Remove os painéis existentes e cria: barra superior fina + dock inferior centralizada.
// O estado anterior fica no backup feito por aplicar-v1-desktop.sh.

panels().forEach(function (p) { p.remove(); });

// ---------- barra superior ----------
var topo = new Panel("org.kde.panel");
topo.location = "top";
topo.height = 30;
topo.lengthMode = "fill";
topo.alignment = "center";
topo.hiding = "none";
topo.floating = false;

var k = topo.addWidget("org.kde.plasma.kickoff");
k.currentConfigGroup = ["General"];
k.writeConfig("icon", "washi-lancador");
k.writeConfig("menuLabel", "スタジオ");

topo.addWidget("org.kde.plasma.appmenu");
topo.addWidget("org.kde.plasma.panelspacer");

var pager = topo.addWidget("org.kde.plasma.pager");
pager.currentConfigGroup = ["General"];
pager.writeConfig("displayedText", 1);        // 1 = Name (一 二 三 四)
pager.writeConfig("showWindowIcons", false);

topo.addWidget("org.kde.plasma.panelspacer");
topo.addWidget("org.kde.plasma.systemtray");

var rel = topo.addWidget("org.kde.plasma.digitalclock");
rel.currentConfigGroup = ["Appearance"];
rel.writeConfig("autoFontAndSize", false);
rel.writeConfig("fontFamily", "DotGothic16");
rel.writeConfig("fontSize", 12);
rel.writeConfig("fontWeight", 400);
rel.writeConfig("showDate", true);
rel.writeConfig("dateDisplayFormat", 1);       // 1 = ao lado da hora
rel.writeConfig("dateFormat", "custom");
rel.writeConfig("customDateFormat", "ddd dd/MM");

// ---------- dock inferior ----------
var dock = new Panel("org.kde.panel");
dock.location = "bottom";
dock.height = 60;
dock.lengthMode = "fit";
dock.alignment = "center";
dock.hiding = "dodgewindows";   // some quando uma janela (ex.: editor maximizado) a cobre
dock.floating = true;

var t = dock.addWidget("org.kde.plasma.icontasks");
t.currentConfigGroup = ["General"];
t.writeConfig("launchers", [
  "applications:org.kde.dolphin.desktop",
  "applications:firefox-esr.desktop",
  "applications:org.kde.konsole.desktop",
  "applications:com.obsproject.Studio.desktop",
  "applications:org.kde.kdenlive.desktop",
  "applications:audacity.desktop",
  "applications:systemsettings.desktop"
]);
t.writeConfig("maxStripes", 1);
t.writeConfig("showOnlyCurrentDesktop", false);

dock.addWidget("org.kde.plasma.marginsseparator");
var sd = dock.addWidget("org.kde.plasma.showdesktop");
sd.currentConfigGroup = ["General"];
sd.writeConfig("icon", "washi-sakura");
