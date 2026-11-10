# a clipped hedge ball (two, one on the other) in a green tub with flowers round its foot
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Topiary in a tub", "kind": "prop", "group": "green", "clear": 0.7, "wobble": 0.015}


def build(b):
    with b.detail(1):
        b.revolve([(0.3, 0.0), (0.36, 0.44), (0.39, 0.44), (0.39, 0.48), (0.3, 0.48), (0.3, 0.42)], "planks", col="green", seg=9)
        b.disc(0.3, "cobble", col=PP.SOIL, seg=9, z=0.43)
        b.tube((0, 0, 0.42), (0.02, 0.0, 1.0), r=0.035, mat="timber", n=5)
        b.blob(0.44, 0.44, 0.42, mat="ivy", col="#5f9f55", z=1.12, seg=9, rings=5, rough=0.04, wind=0.12)
        b.blob(0.27, 0.27, 0.26, mat="ivy", col="#66a85a", x=0.02, z=1.74, seg=8, rings=4, rough=0.04, wind=0.18)
    with b.detail(2):
        for z in (0.1, 0.34):
            b.revolve([(0.315 + 0.06 * z / 0.44, z - 0.025), (0.325 + 0.06 * z / 0.44, z + 0.025)], "metal", col="iron", seg=9)
        PP.blooms(b, 0, 0, 0.5, 0.26, n=8, cols=["#f4f1e4", "#f2a0bd", "#b08ae6"], lift=0.05)
        for a in (20, 140, 260):
            with b.at(rz=a):
                b.blob(0.1, 0.1, 0.07, mat="ivy", col=PP.LEAF, y=-0.22, z=0.47, seg=5, rings=2, rough=0.3, bottom=False)
