# bunting for a feast day: a long string of flags between two painted poles (it flaps in the wind), 8 m along x
import math
from kit import *
import parts as P
import parts_p as PP
import parts_m as PM

L = 8.0
META = {"name": "Bunting between two poles", "kind": "prop", "group": "square", "clear": 4.4, "length": L, "axis": "x", "wobble": 0.02,
        "notes": "poles at x = +-4, 4.3 m tall; the string sags to about 3.3 m in the middle"}


def build(b):
    H = 4.3
    with b.detail(1):
        for sx in (-1, 1):
            x = sx * L / 2
            b.tube((x, 0, -0.3), (x + sx * 0.06, 0, H), r=0.06, r1=0.04, mat="planks", col="ivory", n=6)
            for k in range(4):
                z0 = 0.5 + 0.9 * k
                b.tube((x + sx * 0.06 * z0 / H, 0, z0), (x + sx * 0.06 * (z0 + 0.3) / H, 0, z0 + 0.3), r=0.063 - 0.004 * k, mat="planks", col="red" if k % 2 == 0 else "blue", n=6)
            PP.ball(b, 0.07, "metal", "brass", x=x + sx * 0.06, z=H + 0.05, seg=6, rings=3)
            b.box(0.5, 0.5, 0.62, "ashlar", col="grey", x=x, z=-0.4, taper=0.84)
        PM.bunting(b, (-L / 2 - 0.05, 0, H - 0.08), (L / 2 + 0.05, 0, H - 0.08), n=18, sag=0.9, size=0.36)
        PM.bunting(b, (-L / 2 - 0.05, 0, H - 0.9), (L / 2 + 0.05, 0, H - 0.9), n=15, sag=0.7, size=0.3, cols=("stripe_green", "linen", "#f2a0bd", "stripe_yellow"))
    with b.detail(2):
        for sx in (-1, 1):
            for sy in (-1, 1):
                PP.rope(b, [(sx * (L / 2 + 0.05), 0, H - 0.5), (sx * (L / 2 + 0.25), sy * 1.3, 0.02)], r=0.012)
                b.beam((sx * (L / 2 + 0.25), sy * 1.3, -0.05), (sx * (L / 2 + 0.29), sy * 1.36, 0.16), w=0.04, mat="planks", col="darkoak")
            PP.tuft(b, sx * (L / 2) + 0.35, 0.3, 0, r=0.11, h=0.2)
