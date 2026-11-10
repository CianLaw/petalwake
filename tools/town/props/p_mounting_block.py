# a mounting block: three worn stone steps for getting on a horse, an iron tethering ring in its end
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Mounting block", "kind": "prop", "group": "square", "clear": 1.0}


def build(b):
    with b.detail(1):
        b.stone(1.08, 0.66, 0.3, mat="ashlar", col="grey", x=0.0, z=-0.02, jitter=0.06, ch=0.14)
        b.stone(0.72, 0.62, 0.29, mat="ashlar", col="stone", x=0.18, z=0.27, jitter=0.06, ch=0.14)
        b.stone(0.38, 0.6, 0.29, mat="ashlar", col="grey", x=0.35, z=0.55, jitter=0.06, ch=0.14)
    with b.detail(2):
        with b.at(0.55, 0.0, 0.62, rz=90):
            PP.mooring_ring(b, r=0.085, rr=0.014)
        b.blob(0.2, 0.12, 0.04, mat="ivy", col="#9fb86a", x=-0.3, y=0.25, z=0.28, seg=6, rings=2, bottom=False)
        for (x, y) in ((-0.6, -0.3), (0.5, 0.4), (-0.2, 0.42)):
            PP.tuft(b, x, y, 0, r=0.11, h=0.2)
