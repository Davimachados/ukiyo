#!/usr/bin/env python3
"""Player fictício: somente para sessão D-Bus isolada, sem reprodução de áudio."""
from gi.repository import Gio,GLib
from pathlib import Path
import os
xml='''<node><interface name="org.mpris.MediaPlayer2">
<method name="Raise"/><method name="Quit"/>
<property name="Identity" type="s" access="read"/>
<property name="DesktopEntry" type="s" access="read"/>
<property name="CanRaise" type="b" access="read"/>
<property name="CanQuit" type="b" access="read"/>
<property name="HasTrackList" type="b" access="read"/>
<property name="SupportedUriSchemes" type="as" access="read"/>
<property name="SupportedMimeTypes" type="as" access="read"/>
</interface><interface name="org.mpris.MediaPlayer2.Player">
<method name="Next"/><method name="Previous"/><method name="PlayPause"/><method name="Play"/><method name="Pause"/><method name="Stop"/>
<property name="PlaybackStatus" type="s" access="read"/>
<property name="Metadata" type="a{sv}" access="read"/>
<property name="Volume" type="d" access="readwrite"/>
<property name="Position" type="x" access="read"/>
<property name="Rate" type="d" access="readwrite"/>
<property name="MinimumRate" type="d" access="read"/>
<property name="MaximumRate" type="d" access="read"/>
<property name="CanGoNext" type="b" access="read"/>
<property name="CanGoPrevious" type="b" access="read"/>
<property name="CanPlay" type="b" access="read"/>
<property name="CanPause" type="b" access="read"/>
<property name="CanSeek" type="b" access="read"/>
<property name="CanControl" type="b" access="read"/>
</interface></node>'''
props={'Identity':GLib.Variant('s','Spotify'),'DesktopEntry':GLib.Variant('s','spotify'),
'Metadata':GLib.Variant('a{sv}',{'mpris:trackid':GLib.Variant('o','/track/demo'),'xesam:title':GLib.Variant('s','Noite calma'),'xesam:artist':GLib.Variant('as',['Faixa de demonstração']),'mpris:artUrl':GLib.Variant('s',os.environ['STUDIO_TEST_COVER']),'mpris:length':GLib.Variant('x',180000000)}),
'PlaybackStatus':GLib.Variant('s','Playing'),'Volume':GLib.Variant('d',.65),'Position':GLib.Variant('x',0),'Rate':GLib.Variant('d',1.),'MinimumRate':GLib.Variant('d',1.),'MaximumRate':GLib.Variant('d',1.),'SupportedUriSchemes':GLib.Variant('as',[]),'SupportedMimeTypes':GLib.Variant('as',[])}
for k in ['CanRaise','CanQuit','HasTrackList','CanSeek']:props[k]=GLib.Variant('b',False)
for k in ['CanGoNext','CanGoPrevious','CanPlay','CanPause','CanControl']:props[k]=GLib.Variant('b',True)

def call(conn,sender,path,interface,method,parameters,invocation):
 with open(os.environ['STUDIO_TEST_LOG'],'a') as f:f.write(method+'\n')
 invocation.return_value(None)
def get(conn,sender,path,interface,name):return props.get(name)
def set_prop(conn,sender,path,interface,name,value):props[name]=value;return True
conn=Gio.bus_get_sync(Gio.BusType.SESSION,None)
info=Gio.DBusNodeInfo.new_for_xml(xml)
for iface in info.interfaces:conn.register_object('/org/mpris/MediaPlayer2',iface,call,get,set_prop)
Gio.bus_own_name_on_connection(conn,'org.mpris.MediaPlayer2.spotify',Gio.BusNameOwnerFlags.NONE,None,None)
GLib.MainLoop().run()
