# a flower bed, 3 x 1.5 m: a low mound edged with stones, drifts of colour, hollyhocks at the back, a clipped ball
import math
from kit import *
import parts as P
import parts_p as PP
import parts_c as PC

META = {"name": "Flower bed 3 x 1.5 m", "kind": "prop", "group": "green", "clear": 1.9, "size": (3.0, 1.5)}


def build(b):
    W, D = 3.0, 1.5
    with b.detail(1):
        b.blob(W / 2, D / 2, 0.16, mat="cobble", col=PP.SOIL, z=0.02, seg=10, rings=2, rough=0.04, bottom=False)
        n = 16
        for i in range(n):                                    # the stone edging
            a = 2 * math.pi * i / n
            with b.at(W / 2 * math.cos(a), D / 2 * math.sin(a), -0.03, rz=math.degrees(math.atan2(D / 2 * math.cos(a), -W / 2 * math.sin(a)))):
                b.stone(b.r(0.36, 0.5), 0.2, b.r(0.13, 0.19), col="warm", jitter=0.2, ch=0.3)
        for (x, y, r, c) in ((-0.9, 0.1, 0.34, "#7db45e"), (0.1, -0.15, 0.3, "#86c25e"), (0.95, 0.1, 0.3, "#7db45e"), (-0.2, 0.35, 0.26, "#6fa857")):
            b.blob(r, r * 0.8, 0.2, mat="ivy", col=c, x=x, y=y, z=0.22, seg=6, rings=3, rough=0.3, wind=0.3, bottom=False)
        b.blob(0.27, 0.27, 0.26, mat="ivy", col="#5f9f55", x=1.15, y=-0.1, z=0.42, seg=8, rings=4, rough=0.05, wind=0.15)        # the clipped ball
    with b.detail(2):
        PP.blooms(b, -0.9, 0.05, 0.4, 0.34, n=9, cols=["#e8497a", "#f2a0bd", "#f07fa8"], lift=0.08)
        PP.blooms(b, 0.1, -0.2, 0.38, 0.3, n=8, cols=["#f5c842", "#f4f1e4"], lift=0.08)
        PP.blooms(b, 0.9, 0.3, 0.36, 0.26, n=6, cols=["#b08ae6", "#f4f1e4"], lift=0.08)
        PP.blooms(b, -0.25, 0.4, 0.36, 0.26, n=6, cols=["#e85d3a", "#f5c842"], lift=0.08)
        PP.blooms(b, -0.3, -0.45, 0.2, 0.3, n=7, cols=["#ffffff", "#b08ae6"], lift=0.06)
        for i, (x, c) in enumerate(((-1.05, "#e8497a"), (-0.7, "#f4f1e4"), (-0.38, "#b08ae6"), (0.45, "#f2a0bd"), (0.72, "#e85d3a"))):      # hollyhocks
            y = 0.42 + 0.06 * (i % 2)
            h = b.r(1.1, 1.55)
            b.tube((x, y, 0.1), (x + b.r(-0.04, 0.04), y, h), r=0.014, mat="paint", col="#6f9f4a", n=3)
            for j in range(5):
                zz = h * (0.45 + 0.13 * j)
                b.blob(0.065 - 0.006 * j, 0.065 - 0.006 * j, 0.05, mat="paint", col=c, x=x + (0.045 if j % 2 else -0.045), y=y - 0.02, z=zz, seg=5, rings=2, rough=0.1, wind=0.4 + 0.1 * j)
            b.blob(0.13, 0.13, 0.1, mat="ivy", col="#7db45e", x=x, y=y, z=0.24, seg=5, rings=2, rough=0.3, bottom=False)
        for (x, y) in ((-1.7, -0.5), (1.72, 0.3), (0.4, -0.92)):
            PP.tuft(b, x, y, 0, r=0.11, h=0.2)
