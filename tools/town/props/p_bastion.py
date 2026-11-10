# the stump of a round corner bastion: battered drum of rubble, a broken parapet, the top gone to grass and a thorn bush
import math
from kit import *
import parts as P
import parts_p as PP

R = 3.4
META = {"name": "Bastion stump", "kind": "prop", "group": "walls", "clear": 4.4, "radius": R, "foot_radius": 4.0, "height": 3.7, "wobble": 0.02,
        "notes": "ruined town-wall segments (3.6 m high at their ends) butt into it from any side"}
COL = "#f2e2c6"


def build(b):
    rng = b.rng
    with b.detail(0):
        b.revolve([(4.0, -1.6), (4.0, 0.0), (3.62, 1.3), (R, 3.7)], "masonry", col=COL, seg=20)
        b.disc(R, "ivy", col="!#9fc46a", seg=20, z=3.62)
    P.ruin_top(b, R, 3.62, hmin=0.15, hmax=1.3, t=0.6, col=COL, arc=(205, 420))
    P.ruin_top(b, R, 3.62, hmin=0.1, hmax=0.5, t=0.6, col=COL, arc=(70, 190), grass=False)
    with b.detail(1):
        P.ring_band(b, 3.6, 1.3, h=0.2, out=0.1, mat="masonry", col=shade(COL, 0.92), seg=20)
        PP.crown(b, [(0.8, 0.6, 4.5, 0.95, 0.9, 0.75), (0.2, 0.9, 4.2, 0.7), (1.3, 0.2, 4.2, 0.6)], col="#6f9f4e", wind=0.4, seg=7, rings=3)
        b.tube((0.7, 0.6, 3.6), (0.8, 0.6, 4.3), r=0.08, r1=0.05, mat="timber", n=5)
        for (a, z, r) in ((140, 0.6, 0.7), (150, 1.5, 0.6), (128, 2.3, 0.55), (146, 3.1, 0.5), (118, 1.2, 0.5), (160, 2.5, 0.45)):       # ivy up one side
            rr = 3.95 - 0.6 * z / 3.7
            with b.at(rz=a):
                b.blob(r, 0.3, r * 0.9, mat="ivy", col=shade(PP.LEAF, rng.uniform(0.85, 1.1)), x=0, y=-rr - 0.05, z=z, seg=6, rings=3, wind=0.25, rough=0.3)
    with b.detail(2):
        for _ in range(26):                                   # stones proud of the drum
            a, z = rng.uniform(0, 360), rng.uniform(0.2, 3.2)
            w = rng.uniform(0.4, 0.75)
            hh = w * rng.uniform(0.45, 0.7)
            rr = 4.0 - 0.38 * min(z / 1.3, 1.0) - 0.22 * max(z - 1.3, 0.0) / 2.4
            with b.at(rz=a):
                with b.at(0, -rr + 0.03, z + hh / 2, ry=rng.uniform(-4, 4)):
                    with b.at(rx=90 - 9):
                        b.stone(w, hh, 0.08, col=COL, jitter=0.16)
        for (a, d, s) in ((30, 4.5, 0.5), (48, 4.8, 0.34), (300, 4.4, 0.4), (200, 4.5, 0.3)):
            with b.at(rz=a):
                b.stone(s, s * 0.8, s * 0.55, col=COL, y=-d, jitter=0.25)
        for a in range(0, 360, 45):
            with b.at(rz=a + 10):
                PP.tuft(b, 0, -4.15, 0, r=0.14, h=0.3)
        for (x, y) in ((-1.5, -0.8), (-0.6, 1.6), (1.6, -1.5), (-2.0, 0.9)):
            PP.tuft(b, x, y, 3.62, r=0.16, h=0.34)
        PP.blooms(b, -1.0, -1.2, 3.72, 0.6, n=8, cols=["#f5c842", "#f4f1e4", "#e8497a"])
