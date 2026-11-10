# garden wall, 6 m: warm rubble with flat capping stones; repeats end to end along x
import math
from kit import *
import parts as P
import parts_p as PP

L, H, T = 6.0, 1.7, 0.45
META = {"name": "Garden wall 6 m", "kind": "prop", "group": "walls", "clear": 3.1, "length": L, "axis": "x", "height": H, "thick": T, "wobble": 0.0}


def top(x):
    return H + 0.05 * math.sin(2 * math.pi * x / L) + 0.025 * math.sin(4 * math.pi * x / L)


def build(b):
    with b.detail(0):
        PP.wall_run(b, -L / 2, L / 2, H, t=T, hfun=top)
    with b.detail(1):
        PP.cap_slabs(b, -L / 2, L / 2, top, T, over=0.07, thick=0.11, col="#f1e4cc")
        for (x, z, r) in ((1.45, 1.72, 0.42), (1.9, 1.5, 0.34), (1.2, 1.3, 0.3)):       # a creeper spilling over the top
            b.blob(r, 0.32, r * 0.8, mat="ivy", col=shade(PP.LEAF, b.r(0.85, 1.1)), x=x, y=-0.12, z=z, seg=6, rings=3, wind=0.25, rough=0.3)
        b.blob(0.36, 0.3, 0.26, mat="ivy", col=PP.LEAF, x=1.5, y=0.2, z=1.7, seg=6, rings=3, wind=0.25, rough=0.3)
    with b.detail(2):
        PP.wall_stones(b, -L / 2, L / 2, 0.05, H, T, n=11, hfun=top)
        PP.blooms(b, 1.5, -0.42, 1.55, 0.4, n=7, cols=["#f2a0bd", "#e8497a", "#f4f1e4"], lift=0.3)
        for x in (-2.4, -0.7, 0.4, 2.6):
            PP.tuft(b, x, -T / 2 - 0.08, 0, r=0.12, h=b.r(0.18, 0.3))
        PP.tuft(b, -1.6, T / 2 + 0.08, 0, r=0.12, h=0.25)
