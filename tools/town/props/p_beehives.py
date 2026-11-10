# the bee bench: three straw skeps on a plank stand under a little shingled lean-to, a few bees about
import math
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Beehive stand", "kind": "prop", "group": "green", "clear": 1.5, "wobble": 0.02}


def skep(b, x, y, z, s=1.0, col=PP.STRAW):
    with b.at(x, y, z, s=s):
        prof = [(0.21, 0.0)]
        for k in range(5):
            t0, t1 = k / 5, (k + 1) / 5
            r0, r1 = 0.23 * math.cos(t0 * 1.35), 0.23 * math.cos(t1 * 1.35)
            prof += [(r0 + 0.012, 0.42 * t0 + 0.02), (r0 + 0.012, 0.42 * t1 - 0.02), (r1 + 0.002, 0.42 * t1)]
        prof += [(0.0, 0.46)]
        b.revolve(prof, "thatch", col=col, seg=8)
        b.box(0.09, 0.02, 0.05, "paint", col="#1b1a1c", y=-0.235, z=0.01, bottom=True)


def build(b):
    with b.detail(1):
        PP.board(b, (-1.0, 0, 0.55), (1.0, 0, 0.55), w=0.55, t=0.05, col="greyoak")
        for sx in (-1, 1):
            b.beam((sx * 0.8, -0.22, -0.3), (sx * 0.8, -0.2, 0.53), w=0.07, mat="timber")
            b.beam((sx * 0.8, 0.22, -0.3), (sx * 0.8, 0.2, 1.72), w=0.07, mat="timber")
            b.beam((sx * 0.8, -0.3, 1.36), (sx * 0.8, -0.3, 0.55), w=0.05, mat="timber")
            b.beam((sx * 0.8, -0.34, 1.4), (sx * 0.8, 0.3, 1.66), w=0.05, mat="timber")
        b.gable_roof(2.2, 0.95, pitch=20, mat="shingle", x=0, y=0.42, z=1.38, ridge="x", half=True, eave=0.14, verge=0.1, course=0.24, thick=0.05, barge=False)
        skep(b, 0.02, 0.02, 0.575, s=1.08, col="!#dcc070")
    with b.detail(2):
        skep(b, -0.62, 0.0, 0.575)
        skep(b, 0.64, -0.01, 0.575, s=0.95)
        rng = b.rng
        for _ in range(9):                                    # bees
            x, y, z = rng.uniform(-0.95, 0.95), rng.uniform(-0.75, -0.25), rng.uniform(0.55, 1.25)
            b.blob(0.016, 0.022, 0.016, mat="paint", col="!#e8b020", x=x, y=y, z=z, seg=4, rings=2, rough=0.0, wind=0.7)
        PP.clump(b, -0.9, -0.6, 0, r=0.24, h=0.24, flowers=["#b08ae6", "#f2a0bd"])
        PP.clump(b, 0.75, -0.65, 0, r=0.22, h=0.22, flowers=["#f5c842", "#f4f1e4"])
        PP.clump(b, 0.0, -0.75, 0, r=0.18, h=0.18, flowers=["#e8497a"])
        PP.tuft(b, 1.15, 0.2, 0, r=0.12, h=0.24)
