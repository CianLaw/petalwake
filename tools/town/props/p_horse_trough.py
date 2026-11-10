# a stone horse trough with an iron hand pump at its end and a hitching rail behind
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Horse trough and pump", "kind": "prop", "group": "square", "clear": 2.0, "wobble": 0.02}


def build(b):
    W, D = 2.0, 0.72
    with b.detail(1):
        for x in (-0.65, 0.65):
            b.stone(0.36, D + 0.06, 0.16, mat="ashlar", col="grey", x=x, jitter=0.08)
        b.box(W, D, 0.44, "ashlar", col="grey", z=0.14, top=False, bottom=True)
        for sy in (-1, 1):
            b.box(W, 0.11, 0.08, "ashlar", col="stone", y=sy * (D / 2 - 0.055), z=0.58)
        for sx in (-1, 1):
            b.box(0.11, D - 0.22, 0.08, "ashlar", col="stone", x=sx * (W / 2 - 0.055), z=0.58)
        b.quad((-W / 2 + 0.1, -D / 2 + 0.1, 0.6), (W / 2 - 0.1, -D / 2 + 0.1, 0.6), (W / 2 - 0.1, D / 2 - 0.1, 0.6), (-W / 2 + 0.1, D / 2 - 0.1, 0.6), "water")
        # the pump
        with b.at(-W / 2 - 0.3, 0, 0):
            b.box(0.5, 0.5, 0.12, "ashlar", col="grey", taper=0.9)
            b.revolve([(0.11, 0.12), (0.11, 0.3), (0.075, 0.36), (0.07, 1.15), (0.1, 1.2), (0.1, 1.32), (0.05, 1.4), (0.0, 1.46)], "metal", col="iron", seg=7)
            PP.sweep(b, [(0.06, 0, 0.98), (0.26, 0, 1.04), (0.4, 0, 0.98), (0.44, 0, 0.84)], r=0.04, r1=0.032, n=5, mat="metal", col="iron")
            PP.sweep(b, [(0.0, 0, 1.3), (-0.2, 0, 1.38), (-0.5, 0, 1.2), (-0.62, 0, 0.92)], r=0.02, n=4, mat="metal", col="iron")
        # the hitching rail
        for sx in (-1, 1):
            b.beam((sx * 1.15, 0.85, -0.2), (sx * 1.15, 0.85, 1.12), w=0.12, mat="timber")
        b.beam((-1.35, 0.85, 1.02), (1.35, 0.85, 1.02), w=0.1, mat="timber")
    with b.detail(2):
        PP.sweep(b, [(-0.86, 0, 0.84), (-0.86, 0, 0.61)], r=0.014, n=3, mat="water")
        with b.at(0.4, 0.85 - 0.06, 0.98):
            PP.mooring_ring(b, r=0.08, rr=0.013)
        PP.bucket(b, 0.75, -0.75, 0, r=0.15, h=0.27)
        for (x, y) in ((-1.0, -0.5), (1.1, -0.45), (0.2, 0.5), (-1.5, 0.7)):
            PP.tuft(b, x, y, 0, r=0.12, h=0.24)
        b.blob(0.3, 0.12, 0.05, mat="ivy", col="#9fb86a", x=0.3, y=-D / 2 - 0.02, z=0.3, seg=6, rings=2)
