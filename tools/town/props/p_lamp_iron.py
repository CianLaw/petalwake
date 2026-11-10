# a cast-iron street lamp: fluted column on a stone foot, a ladder bar, a six-sided lantern
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Iron street lamp", "kind": "prop", "group": "square", "clear": 0.5, "wobble": 0.02}


def build(b):
    with b.detail(1):
        b.box(0.52, 0.52, 0.54, "ashlar", col="grey", z=-0.4, taper=0.94)
        b.revolve([(0.17, 0.14), (0.17, 0.3), (0.115, 0.38), (0.1, 0.92), (0.075, 1.0), (0.09, 1.06), (0.06, 1.13), (0.045, 2.86), (0.075, 2.93), (0.075, 2.99), (0.04, 3.06)],
                  "metal", col="iron", seg=8)
        b.tube((-0.34, 0, 2.74), (0.34, 0, 2.74), r=0.018, mat="metal", col="iron", n=4, caps=True)
        with b.at(z=3.2):
            PP.lantern(b, s=0.4, h=0.6, sides=6, strength=1.2)
    with b.detail(2):
        for k in range(3):      # the cradle the lantern sits in
            with b.at(z=3.02, rz=120 * k + 30):
                PP.sweep(b, [(0, -0.03, 0.0), (0, -0.15, 0.03), (0, -0.2, 0.12), (0, -0.16, 0.2)], r=0.012, n=3, mat="metal", col="iron")
        for sx in (-1, 1):
            PP.ball(b, 0.03, "metal", "iron", x=sx * 0.34, z=2.74, seg=5, rings=2)
        PP.tuft(b, 0.24, 0.2, 0, r=0.1, h=0.18, n=4)
