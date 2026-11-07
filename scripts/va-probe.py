#!/usr/bin/env python3
# Lista perfis/entrypoints VA-API sem precisar do vainfo. Uso: python3 scripts/va-probe.py [iHD|i965]
import ctypes, os, sys
P = {-1:"None(VPP)",0:"MPEG2Simple",1:"MPEG2Main",2:"MPEG4Simple",3:"MPEG4AdvSimple",4:"MPEG4Main",5:"H264Baseline",6:"H264Main",7:"H264High",8:"VC1Simple",9:"VC1Main",10:"VC1Advanced",11:"H263Baseline",12:"JPEGBaseline",13:"H264ConstrainedBaseline",14:"VP8",15:"H264MultiviewHigh",16:"H264StereoHigh",17:"HEVCMain",18:"HEVCMain10",19:"VP9P0",20:"VP9P1",21:"VP9P2",22:"VP9P3",23:"HEVCMain12",24:"HEVCMain422_10",25:"HEVCMain422_12",26:"HEVCMain444",27:"HEVCMain444_10",28:"HEVCMain444_12",29:"HEVCSccMain",30:"HEVCSccMain10",31:"HEVCSccMain444",32:"AV1P0",33:"AV1P1",34:"HEVCSccMain444_10"}
E = {1:"VLD(decode)",6:"EncSlice",7:"EncPicture",8:"EncSliceLP",10:"VideoProc",11:"FEI",12:"Stats"}
drv = sys.argv[1] if len(sys.argv) > 1 else None
if drv: os.environ["LIBVA_DRIVER_NAME"] = drv
va = ctypes.CDLL("libva.so.2"); vadrm = ctypes.CDLL("libva-drm.so.2")
vadrm.vaGetDisplayDRM.restype = ctypes.c_void_p
va.vaQueryVendorString.restype = ctypes.c_char_p
fd = os.open("/dev/dri/renderD128", os.O_RDWR)
dpy = ctypes.c_void_p(vadrm.vaGetDisplayDRM(fd))
ma, mi = ctypes.c_int(), ctypes.c_int()
if va.vaInitialize(dpy, ctypes.byref(ma), ctypes.byref(mi)) != 0:
    print("vaInitialize falhou"); sys.exit(1)
print(f"VA-API {ma.value}.{mi.value} | driver: {va.vaQueryVendorString(dpy).decode()}")
n = va.vaMaxNumProfiles(dpy); profs = (ctypes.c_int*n)(); cnt = ctypes.c_int()
va.vaQueryConfigProfiles(dpy, profs, ctypes.byref(cnt))
m = va.vaMaxNumEntrypoints(dpy)
for i in range(cnt.value):
    p = profs[i]; eps = (ctypes.c_int*m)(); ne = ctypes.c_int()
    va.vaQueryConfigEntrypoints(dpy, p, eps, ctypes.byref(ne))
    print(f"  {str(P.get(p, p)):26s} " + ", ".join(E.get(eps[j], str(eps[j])) for j in range(ne.value)))
va.vaTerminate(dpy)
