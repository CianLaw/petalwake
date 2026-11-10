# the market cross: a tall tapering shaft with a wheel head on three worn eight-sided steps
import math
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Market cross", "kind": "prop", "group": "square", "clear": 2.6, "wobble": 0.02, "lean": (0.006, -0.004)}


def build(b):
    g, sd, st, ms = C("grey"), C("sand"), C("stone"), C("moss")
    with b.detail(0):
        with b.at(rz=22.5):
            b.revolve([(2.3, -0.3), (2.3, 0.2), (1.85, 0.2), (1.85, 0.42), (1.4, 0.42), (1.4, 0.64), (0.95, 0.64), (0.95, 0.86), (0.0, 0.86)],
                      "ashlar", seg=8, smooth=False, cols=[ms, sd, g, sd, g, st, g, st])
        b.box(0.8, 0.8, 0.46, "ashlar", col="stone", z=0.86, taper=0.84)
        with b.at(z=1.32, rz=22.5):
            b.revolve([(0.25, 0.0), (0.2, 0.22), (0.135, 2.9), (0.2, 2.98), (0.25, 3.1), (0.25, 3.2), (0.1, 3.27)], "ashlar", col="sand", seg=8, smooth=False)
    with b.detail(1):
        with b.at(z=4.98):
            with b.at(rx=90):
                PP.torus(b, 0.34, 0.065, mat="ashlar", col="stone", seg=10, n=4)
            b.box(0.14, 0.14, 0.96, "ashlar", col="stone", z=-0.42)
            b.box(0.9, 0.14, 0.14, "ashlar", col="stone", z=-0.07, bottom=True)
    with b.detail(2):
        for (a, r, z) in ((15, 2.2, 0.0), (100, 2.25, 0.0), (205, 2.2, 0.0), (290, 2.22, 0.0), (60, 1.75, 0.2), (240, 1.3, 0.42)):
            with b.at(rz=a):
                b.stone(0.5, 0.3, 0.16, mat="ashlar", col="grey", y=-r, z=z, jitter=0.2)
        for a in (40, 130, 215, 330):
            with b.at(rz=a):
                PP.tuft(b, 0, -2.1, 0.0, r=0.12, h=0.2)
                PP.tuft(b, 0.2, -1.68, 0.2, r=0.08, h=0.14, n=4)
        PP.basket(b, -1.0, -1.25, 0.42, r=0.2, h=0.2, fill="!#d9382e")
        PP.jar(b, -0.6, -1.5, 0.2, s=1.1, kind="jug", col="#c9764a")
        b.blob(0.3, 0.2, 0.05, mat="ivy", col="#9fb86a", x=1.2, y=1.0, z=0.43, seg=6, rings=2, bottom=False)       # moss
        b.blob(0.25, 0.3, 0.05, mat="ivy", col="#9fb86a", x=-1.5, y=0.6, z=0.21, seg=6, rings=2, bottom=False)
