# a channel buoy riding at its mooring: red and white, a caged lantern and a ball on top, a gull that will not leave
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

META = {"name": "Harbour buoy", "kind": "prop", "group": "harbour", "clear": 1.2, "float": True, "draft": 0.6, "wobble": 0.0, "lean": (0.05, 0.02)}


def build(b):
    red, white = C("!#b5433a"), C("!#f2ead8")
    with b.detail(1):
        b.revolve([(0.0, -0.6), (0.3, -0.45), (0.56, -0.08), (0.62, 0.12), (0.56, 0.3), (0.42, 0.62), (0.3, 0.98), (0.16, 1.3), (0.12, 1.36)], "paint", seg=10,
                  cols=[red, red, red, red, white, white, red, red])
        b.disc(0.12, "paint", col=red, seg=10, z=1.36)
        for k in range(4):                                    # the cage
            with b.at(rz=90 * k + 45):
                PP.sweep(b, [(0, -0.12, 1.34), (0, -0.2, 1.55), (0, -0.16, 1.85), (0, 0.0, 2.0)], r=0.014, n=3, mat="metal", col="iron")
        with b.at(z=1.4):
            PP.lantern(b, s=0.22, h=0.36, sides=6, lamp=False)
        PP.ball(b, 0.11, "paint", red, z=2.12, seg=7, rings=4)
        b.tube((0, 0, 1.98), (0, 0, 2.05), r=0.02, mat="metal", col="iron", n=4)
    with b.detail(2):
        b.revolve([(0.63, 0.08), (0.66, 0.12), (0.63, 0.17)], "cloth", col=PP.HEMP, seg=10)              # a rope fender round its waist
        PP.rope(b, [(0.3, 0.0, -0.4), (0.5, 0.1, -1.2), (0.8, 0.2, -2.6)], r=0.03, col="#4a4848")
        PH.gull(b, 0.0, 0.0, 2.23, rz=30)
