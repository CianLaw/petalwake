# the winter's firewood: a stacked rick of logs between stakes under a board roof, a chopping block with the axe in it
import math
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Wood pile", "kind": "prop", "group": "square", "clear": 1.7}


def build(b):
    with b.at(-0.45, 0, 0):          # (the rick and the chopping block together are centred on the origin)
        _build(b)


def _build(b):
    W, D, R = 1.9, 0.9, 0.1
    with b.detail(1):
        b.box(W - 0.1, D - 0.12, 1.02, "timber", col="#c9ad8c", x=0, y=0, z=0.04)                 # what is seen from far off
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.beam((sx * (W / 2 + 0.05), sy * (D / 2 - 0.1), 0), (sx * (W / 2 + 0.05), sy * (D / 2 - 0.1), 1.38 + (0.16 if sy > 0 else 0)), w=0.08, mat="timber")
        for i in range(5):                                    # the board roof
            y0 = -D / 2 - 0.16 + (D + 0.32) * i / 5
            y1 = y0 + (D + 0.32) / 5 + 0.03
            z0, z1 = 1.38 + 0.16 * i / 5, 1.38 + 0.16 * (i + 1) / 5
            PP.board(b, (-W / 2 - 0.2, (y0 + y1) / 2, (z0 + z1) / 2 + 0.03 + 0.012 * (i % 2)), (W / 2 + 0.2, (y0 + y1) / 2, (z0 + z1) / 2 + 0.03 + 0.012 * (i % 2)), w=y1 - y0, t=0.03,
                     col=shade("greyoak", b.r(0.85, 1.05)))
    with b.detail(2):
        rows = 5
        for r_ in range(rows):
            n = 9 if r_ % 2 == 0 else 8
            for i in range(n):
                x = -W / 2 + 0.12 + (W - 0.24) * (i + (0.5 if r_ % 2 else 0.0)) / 8.5
                rr = R * b.r(0.82, 1.08)
                z = 0.05 + R + r_ * R * 1.82
                c = shade(b.pick(["#d9b98f", "#c9a57a", "#e0c8a0"]), b.r(0.9, 1.08))
                y0, y1 = -D / 2 + b.r(-0.05, 0.03), D / 2 + b.r(-0.03, 0.05)
                b.tube((x, y0, z), (x, y1, z), r=rr, mat="timber", col="#c9ad8c", n=5)
                for (yy, flip) in ((y0, True), (y1, False)):
                    pts = [(x + rr * 0.95 * math.cos(2 * math.pi * k / 5), yy, z + rr * 0.95 * math.sin(2 * math.pi * k / 5)) for k in range(5)]
                    b.face(pts if flip else list(reversed(pts)), "paint", col=c)
        # chopping block, axe, kindling
        b.tube((1.75, -0.5, 0), (1.75, -0.5, 0.5), r=0.26, mat="timber", col="#c9ad8c", n=8)
        with b.at(1.75, -0.5, 0.5):
            b.disc(0.26, "paint", col="#dcc096", seg=8)
            b.beam((0.02, 0.0, 0.02), (0.36, 0.1, 0.62), w=0.035, mat="planks", col="#c9a57a")
            b.box(0.05, 0.16, 0.13, "metal", col="lead", x=0.03, y=0.0, z=-0.01)
        for (x, y, a) in ((1.35, -0.95, 20), (1.6, -1.05, -35), (1.9, -0.98, 60), (1.5, -0.8, 100)):
            with b.at(x, y, 0.035, rz=a):
                b.box(0.32, 0.07, 0.06, "paint", col="#dcc096", bottom=True)
        PP.tuft(b, -1.15, -0.5, 0, r=0.12, h=0.24)
        PP.tuft(b, 1.1, 0.55, 0, r=0.12, h=0.22)
