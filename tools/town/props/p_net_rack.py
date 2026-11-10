# a net-drying rack: three posts and two rails hung with fishing nets, a heap of net and floats at its foot, a gull
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

L = 4.6
META = {"name": "Net-drying rack", "kind": "prop", "group": "harbour", "clear": 2.6, "length": L, "axis": "x", "wobble": 0.02}


def build(b):
    xs = (-2.2, 0.0, 2.2)
    with b.detail(1):
        for x in xs:
            b.beam((x, 0, -0.3), (x, 0, 2.7), w=0.11, mat="timber", col="greyoak")
            for sy in (-1, 1):
                b.beam((x, sy * 0.75, 0.0), (x, 0, 1.25), w=0.07, mat="timber", col="greyoak")
        b.beam((-2.4, 0, 2.6), (2.4, 0, 2.6), w=0.09, mat="timber", col="greyoak")
        b.beam((-2.3, -0.06, 1.55), (2.3, -0.06, 1.55), w=0.07, mat="timber", col="greyoak")
    PH.net_drape(b, (-2.15, 0.02, 2.62), (-0.05, 0.02, 2.62), drop=1.9, sag=0.12, col=PH.NET, lod=1)
    PH.net_drape(b, (0.05, 0.02, 2.62), (2.15, 0.02, 2.62), drop=1.5, sag=0.18, col=PH.NET_BROWN, lod=2)
    PH.net_drape(b, (-1.2, -0.12, 1.56), (1.9, -0.12, 1.56), drop=1.2, sag=0.1, col=PH.NET, lod=2, mesh=0.3)
    PH.net_heap(b, 1.3, -0.9, 0, r=0.6)
    PH.rope_coil(b, -1.6, -0.8, 0, r=0.28)
    PH.basket(b, -0.6, -1.0, 0, r=0.28, h=0.3, fill=None)
    PH.gull(b, 2.2, 0, 2.72, rz=300)
    with b.detail(2):
        for (x, y) in ((-2.4, 0.5), (0.3, 0.6), (2.5, -0.4)):
            PP.tuft(b, x, y, 0, r=0.12, h=0.24)
