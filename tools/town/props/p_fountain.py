# the square's fountain: an eight-sided basin on a step, a stemmed upper bowl, and a carved fish that spouts
import math
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Fountain", "kind": "prop", "group": "square", "clear": 2.9, "wobble": 0.015}


def build(b):
    R, Ri, Rs = 1.95, 1.6, 2.45
    g, sd, st = C("grey"), C("sand"), C("stone")
    with b.detail(0):
        with b.at(rz=22.5):
            b.revolve([(Rs, -0.3), (Rs, 0.14), (R, 0.14), (R, 0.56), (R + 0.08, 0.6), (R + 0.08, 0.7), (Ri - 0.05, 0.7), (Ri - 0.05, 0.62), (Ri, 0.6), (Ri, 0.3)],
                      "ashlar", seg=8, smooth=False, cols=[g, sd, sd, st, st, st, sd, sd, g])
            b.disc(Ri, "water", seg=8, z=0.54)
        b.revolve([(0.5, 0.45), (0.5, 0.72), (0.36, 0.8), (0.23, 0.92), (0.19, 1.3), (0.27, 1.4), (0.21, 1.47), (0.5, 1.62), (0.9, 1.74), (0.95, 1.83), (0.86, 1.83), (0.83, 1.76)],
                  "ashlar", col="stone", seg=12)
        b.disc(0.84, "water", seg=12, z=1.78)
    with b.detail(1):
        b.revolve([(0.18, 1.74), (0.12, 2.0), (0.2, 2.06), (0.2, 2.13), (0.0, 2.15)], "ashlar", col="stone", seg=8)
        # the fish: tail curled on the stem, head raised
        pts = [(-0.22, 0, 2.32), (-0.1, 0, 2.2), (0.06, 0, 2.2), (0.17, 0, 2.34), (0.13, 0, 2.55), (0.0, 0, 2.71), (-0.09, 0, 2.9)]
        PP.sweep(b, pts, radii=[0.03, 0.06, 0.1, 0.125, 0.12, 0.1, 0.055], n=7, mat="ashlar", col="stone", caps=(True, True))
        PP.face2(b, [(-0.2, 0, 2.3), (-0.3, 0, 2.2), (-0.38, 0, 2.46)], "ashlar", col="stone")
        PP.face2(b, [(0.24, 0, 2.3), (0.36, 0, 2.5), (0.22, 0, 2.56)], "ashlar", col="stone")
        for k in range(4):      # spout lips on the upper bowl
            with b.at(rz=45 + 90 * k):
                b.box(0.14, 0.16, 0.06, "ashlar", col="stone", y=-0.98, z=1.74, bottom=True)
    with b.detail(2):
        PP.sweep(b, [(-0.1, 0, 2.93), (-0.22, 0, 3.12), (-0.36, 0, 3.14), (-0.5, 0, 2.95), (-0.6, 0, 2.5), (-0.64, 0, 1.79)], r=0.022, n=4, mat="water")
        for k in range(4):
            with b.at(rz=45 + 90 * k):
                PP.sweep(b, [(0, -0.98, 1.79), (0, -1.1, 1.76), (0, -1.2, 1.55), (0, -1.27, 1.15), (0, -1.31, 0.55)], r=0.024, n=4, mat="water")
        for (a, r) in ((30, 1.1), (155, 0.9), (200, 1.25), (300, 1.0)):       # water lilies
            with b.at(rz=a):
                with b.at(0, -r, 0.548, rz=b.r(0, 360)):
                    b.disc(0.15, "paint", col="#5f9a55", seg=6)
                    if b.chance(0.6):
                        b.blob(0.05, 0.05, 0.04, mat="paint", col=b.pick(["#f4f1e4", "#f2a0bd"]), x=0.06, z=0.03, seg=5, rings=2, rough=0.1)
        for a in (10, 95, 190, 260):
            with b.at(rz=a):
                PP.tuft(b, 0, -Rs - 0.05, 0, r=0.1, h=0.16, n=4)
