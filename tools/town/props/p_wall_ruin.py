# the old town wall, 8 m: thick, battered, its top broken down and grown over, a breach half way along; repeats along x
import math
from kit import *
import parts as P
import parts_p as PP

L, T = 8.0, 1.3
XS = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
HS = [3.6, 4.5, 5.3, 5.3, 4.4, 2.9, 2.3, 3.1, 3.6]
META = {"name": "Ruined town wall 8 m", "kind": "prop", "group": "walls", "clear": 4.2, "length": L, "axis": "x", "height": 5.3, "end_height": 3.6, "thick": T, "wobble": 0.0,
        "notes": "ends are 3.6 m high and 1.3 m thick (1.6 at the foot); turn alternate pieces round for variety"}
COL = "#f2e2c6"
BAT = 0.15


def top(x):
    x = min(max(x, -4.0), 4.0)
    i = min(int(x + 4), 7)
    return lerp(HS[i], HS[i + 1], x + 4 - i)


def yface(x, z):
    return T / 2 + BAT * (1 - z / top(x))


def build(b):
    rng = b.rng
    with b.detail(0):
        PP.wall_run(b, -L / 2, L / 2, 3.6, t=T, col=COL, batter=BAT, skirt=1.6, hfun=top)
        for x in (-2.75, -1.6):                               # what is left of the parapet
            b.box(0.8, 0.42, 0.95, "masonry", col=COL, x=x, y=-T / 2 + 0.21, z=top(x) - 0.05)
    with b.detail(1):
        for i in range(15):                                   # the broken head: loose courses, and grass
            x = -3.72 + 7.44 * i / 14
            for sy in (-1, 1):
                if (i + (sy > 0)) % 2 == 0:
                    b.stone(rng.uniform(0.45, 0.62), rng.uniform(0.4, 0.55), rng.uniform(0.18, 0.42), col=COL, x=x, y=sy * rng.uniform(0.28, 0.4), z=top(x) - 0.06, jitter=0.2)
        for (x, r) in ((-3.3, 0.4), (-0.4, 0.45), (1.2, 0.5), (2.2, 0.55), (3.2, 0.4)):
            b.blob(r, 0.5, 0.2, mat="ivy", col="!#9fc46a", x=x, y=rng.uniform(-0.15, 0.15), z=top(x) + 0.06, seg=6, rings=2, rough=0.3, wind=0.35, bottom=False)
        for (x, z, r) in ((1.5, 0.5, 0.6), (2.1, 1.3, 0.5), (1.0, 1.5, 0.45), (1.8, 2.1, 0.4), (2.6, 0.5, 0.45)):       # ivy in the breach
            b.blob(r, 0.3, r * 0.9, mat="ivy", col=shade(PP.LEAF, rng.uniform(0.85, 1.1)), x=x, y=-yface(x, z) - 0.05, z=z, seg=6, rings=3, wind=0.25, rough=0.3)
    with b.detail(2):
        for i in range(15):
            x = -3.72 + 7.44 * i / 14
            for sy in (-1, 1):
                if (i + (sy > 0)) % 2 == 1:
                    b.stone(rng.uniform(0.4, 0.6), rng.uniform(0.4, 0.55), rng.uniform(0.15, 0.36), col=COL, x=x, y=sy * rng.uniform(0.28, 0.4), z=top(x) - 0.06, jitter=0.2)
        PP.wall_stones(b, -L / 2, L / 2, 0.1, 5.2, T, n=14, col=COL, batter=BAT, h=4.0, hfun=top, size=(0.4, 0.75))
        x = -2.15                                             # an arrow loop, and putlog holes
        b.box(0.14, 0.04, 1.05, "paint", col="#1b1a1c", x=x, y=-yface(x, 2.9) - 0.012, z=2.4, bottom=True)
        b.stone(0.5, 0.2, 0.16, mat="ashlar", col="sand", x=x, y=-yface(x, 3.5) + 0.02, z=3.45, jitter=0.06)
        for (px, pz) in ((-3.3, 2.2), (-0.9, 2.2), (-3.3, 3.5), (-0.9, 3.6), (0.4, 2.1), (3.3, 1.9)):
            for sy in (-1, 1):
                b.box(0.17, 0.03, 0.17, "paint", col="#1b1a1c", x=px, y=sy * (yface(px, pz) + 0.008), z=pz, bottom=True)
        for (x, y, s) in ((1.6, -1.1, 0.5), (2.2, -1.3, 0.36), (1.1, -1.25, 0.3), (2.0, 1.15, 0.45), (1.3, 1.3, 0.3)):       # fallen stones
            b.stone(s, s * 0.8, s * 0.55, col=COL, x=x, y=y, jitter=0.25)
        for x in (-3.4, -1.8, 0.2, 3.1):
            PP.tuft(b, x, -T / 2 - BAT - 0.1, 0, r=0.14, h=0.3)
            PP.tuft(b, x + 0.6, T / 2 + BAT + 0.1, 0, r=0.14, h=0.28)
        PP.blooms(b, 2.2, 0.0, top(2.2) + 0.2, 0.4, n=6, cols=["#f5c842", "#f4f1e4"])
