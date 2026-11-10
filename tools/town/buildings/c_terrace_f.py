# The Potter's House: the kiln is in the lean-to and the pots dry on its roof, under the vine, where the potter's wife also keeps her chair. The stair to the roof is the one her cat uses.
# Massing: a white house, eaves to the street, with a flat-roofed workshop against its right side; a stone stair along the street up to the roof terrace, a pergola and rows of pots up there, and a bottle-necked brick kiln stack behind.
# Materials: whitewash over a stone foot, tiles, brick kiln, flagged terrace. Accent: red.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Potter's House", "kind": "house", "lot": (7.5, 8.0)}

X0, X1, Y0, Y1 = -3.4, 0.9, 2.4, 7.5
W, D, CX, CY = X1 - X0, Y1 - Y0, (X0 + X1) / 2, (Y0 + Y1) / 2
H = 5.3
SX0, SX1, SY0, SY1, SH = 0.9, 3.5, 1.62, 7.0, 2.7  # the workshop
ZT = SH + 0.15                                     # terrace floor


def build(b):
    bd = b.body(W, D, H, mat="plaster", col="white", x=CX, y=CY)
    PC.plinth(bd, h=0.8, out=0.08, doors=[("front", 1.0, 0.9)])
    f, r, k, l = bd.front, bd.right, bd.back, bd.left
    P.door(f, 1.0, w=0.9, h=2.0, col="red", z=0.25, steps=1, frame="timber", lamp=True)
    P.window(f, 2.95, 0.95, w=1.6, h=1.3, bars=(3, 1), lintel="timber")
    P.awning(f, 2.95, 2.75, w=2.0, out=0.9, drop=0.45, cols=("stripe_red", "linen"))
    P.sign(f, 0.3, 3.0, emblem="mug", col="red", out=0.6)
    P.window(f, 1.1, 3.45, w=0.8, h=1.25, shutters="red", box=True)
    P.window(f, 3.1, 3.45, w=0.8, h=1.25, shutters="red")
    P.exposed(f, "both", n=9)
    P.door(r, 1.6, w=0.85, h=1.9, col="red", z=ZT + 0.03, frame="timber")       # out onto the terrace
    P.window(r, 3.6, ZT + 0.85, w=0.75, h=1.15, shutters="red")
    P.window(l, 1.4, 1.1, w=0.7, h=1.0, ajar=4)
    P.window(l, 3.6, 3.45, w=0.75, h=1.2, shutters="red", ajar=4)
    P.window(l, 1.5, 3.45, w=0.75, h=1.2, ajar=4)
    P.window(k, 1.3, 1.1, w=0.7, h=1.0)
    P.door(k, 3.2, w=0.85, h=1.9, col="red", z=0.2, frame="timber")
    P.window(k, 1.2, 3.45, w=0.75, h=1.2, shutters="red", ajar=4)
    P.window(k, 3.2, 3.45, w=0.75, h=1.2, ajar=4)
    P.exposed(k, "base", n=8)
    P.ivy(l, 4.4, 0.3, w=1.2, h=3.2, n=6)
    rise = bd.gable(ridge="x", pitch=45, mat="tiles", eave=0.3, verge=0.1, sag=0.1, barge=False)
    PC.stack(b, X0 + 0.5, CY - 0.2, H + rise - 0.8, 2.6, w=0.5, d=0.8, flues=2)
    workshop(b)
    with b.at(0.08, 1.06, 0, rz=270):                # the stair along the street up to the terrace
        PC.outside_stair(b, n=14, w=1.05, rise=ZT / 14, run=(SX1 - 0.08 - 0.08) / 14, rail="iron", rail_sides="r")
    front(b)


def workshop(b):
    w, d = SX1 - SX0, SY1 - SY0
    cx, cy = (SX0 + SX1) / 2, (SY0 + SY1) / 2
    ws = b.body(w, d, SH, mat="plaster", col="white", x=cx, y=cy)
    PC.plinth(ws, h=0.8, out=0.08, doors=[("back", 1.3, 0.9)])
    P.window(ws.right, 1.5, 1.0, w=0.9, h=1.1, bars=(2, 1), lintel="timber", ajar=4)
    P.window(ws.right, 3.9, 1.0, w=0.9, h=1.1, bars=(2, 1), lintel="timber", ajar=4)
    P.door(ws.back, 1.3, w=0.9, h=1.95, col="red", z=0.2, frame="timber")
    P.exposed(ws.right, "base", n=7)
    with b.at(cx, cy, SH):
        b.box(w + 0.16, d + 0.16, 0.15, "flagstone", col="sand", bottom=True)
        z = 0.15
        # parapet on the right and the back, a rail to the street beside the stair head
        b.box(0.26, d - 0.2, 0.5, "plaster", col="white", x=w / 2 - 0.13, y=0.1, z=z)
        b.box(w, 0.26, 0.5, "plaster", col="white", x=0, y=d / 2 - 0.13, z=z)
        P.railing(b, [(-w / 2 + 0.06, -d / 2 + 0.06, z), (w / 2 - 1.25, -d / 2 + 0.06, z)], h=0.95, style="iron")
        PC.pots(b, (w / 2 - 0.13, -d / 2 + 0.9, z + 0.5), (w / 2 - 0.13, d / 2 - 1.6, z + 0.5), n=9)
        PC.pots(b, (-w / 2 + 0.3, d / 2 - 0.13, z + 0.5), (-0.1, d / 2 - 0.13, z + 0.5), n=4, r=(0.1, 0.2))
        with b.at(-0.15, 0.25, z):
            PC.pergola(b, 2.0, 2.4, h=2.15, nx=2, bloom=["#b08ae6", "#e3d8ee"])
        P.bench(b, -0.6, 0.9, z, rz=180, w=1.1)
        PC.pots(b, (-0.9, -1.9, z), (0.6, -2.2, z), n=5, r=(0.14, 0.24))
        # the kiln stack: bottle-necked brick, at the back
        with b.at(0.45, d / 2 - 0.85, z - 0.2):
            b.revolve([(0.62, 0.0), (0.6, 1.2), (0.42, 2.1), (0.36, 3.7), (0.42, 3.8), (0.42, 3.95), (0.3, 3.95)], "brick", seg=10)
            with b.detail(1):
                for zz in (0.6, 1.25):
                    b.revolve([(0.63, zz), (0.63, zz + 0.07)], "metal", col="iron", seg=10)
            b.smoke(0, 0, 4.3, strength=1.3)


def front(b):
    PC.yard(b, -3.6, 0.0, Y0, h=1.05, gate=(-2.4, 1.0), piers=1.4, gate_col="red", right=False)
    with b.at(-0.75, 1.75, 0):                       # the seconds table
        with b.detail(2):
            b.box(1.5, 0.5, 0.06, "planks", col="greyoak", z=0.7, bottom=True)
            for sx in (-1, 1):
                b.box(0.07, 0.42, 0.7, "planks", col="greyoak", x=sx * 0.65)
        PC.pots(b, (-0.6, 0, 0.76), (0.6, 0, 0.76), n=6, r=(0.08, 0.15))
    PC.pots(b, (-3.1, 2.1, 0), (-1.9, 2.15, 0), n=4, r=(0.16, 0.26))
    PC.flowers(b, -1.0, 0.72, 0, w=1.4, d=0.4, n=5)
    PC.cat(b, 1.62, 0.95, ZT * 6.5 / 14 + 0.02, rz=200, col="#e9e4da")
