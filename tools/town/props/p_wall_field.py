# a drystone field wall, 8 m: battered grey rubble with upright cock-and-hen coping and a step stile; repeats along x
import math
from kit import *
import parts as P
import parts_p as PP

L, H, T = 8.0, 1.15, 0.5
META = {"name": "Drystone field wall 8 m", "kind": "prop", "group": "walls", "clear": 4.1, "length": L, "axis": "x", "height": H, "thick": T, "wobble": 0.0}
BAT = 0.11


def top(x):
    return H + 0.06 * math.sin(2 * math.pi * x / L) + 0.04 * math.sin(6 * math.pi * x / L)


def build(b):
    with b.detail(0):
        PP.wall_run(b, -L / 2, L / 2, H, t=T, col="grey", batter=BAT, skirt=1.2, hfun=top)
    with b.detail(1):
        PP.cap_ridge(b, -L / 2, L / 2, top, T, h=0.16, col="dark")
        for (z, sy) in ((0.34, -1), (0.68, -1), (0.34, 1), (0.68, 1)):          # the stile: through-stones for steps
            b.stone(0.5, 0.52, 0.09, mat="ashlar", col="grey", x=1.55 + (0.18 if z > 0.5 else -0.18) * 1, y=sy * (T / 2 + BAT * (1 - z / H) + 0.2), z=z, jitter=0.08, bottom=True)
    with b.detail(2):
        PP.cap_cocks(b, -L / 2, L / 2, top, T, col="grey")
        PP.wall_stones(b, -L / 2, L / 2, 0.05, H, T, n=17, col="grey", batter=BAT, h=H, hfun=top, size=(0.26, 0.55), proud=0.06)
        PP.wall_stones(b, -L / 2, L / 2, 0.05, H, T, n=6, col="dark", batter=BAT, h=H, hfun=top, size=(0.24, 0.4), proud=0.05)
        for (x, sy) in ((-2.6, -1), (0.2, 1), (2.9, -1)):                       # lichen and moss
            b.blob(0.3, 0.12, 0.22, mat="ivy", col="!#c9cf7a", x=x, y=sy * (T / 2 + 0.05), z=0.7, seg=6, rings=2, rough=0.3)
        for x in (-3.6, -2.4, -1.0, 0.4, 2.0, 3.2):
            PP.tuft(b, x, -T / 2 - BAT - 0.08, 0, r=0.14, h=b.r(0.22, 0.36))
            PP.tuft(b, x + 0.5, T / 2 + BAT + 0.08, 0, r=0.14, h=b.r(0.22, 0.36))
        PP.blooms(b, -1.5, -0.55, 0.12, 0.35, n=6, cols=["#f5c842", "#ffffff"], lift=0.1)
