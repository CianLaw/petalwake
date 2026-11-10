# The Net-mender's House: she works on the gallery where the light is, and the nets hang across the yard to dry. The children are not allowed on the stair with wet feet.
# Massing: a broad house, eaves to the street, with two dormers; a timber gallery under its own pentice on the right of the front, reached by an open oak stair along the wall; the workshop doors underneath; a low-walled yard.
# Materials: warm stone below, sky-blue limewash above, dark oak gallery, tiles. Accent: teal.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Net-mender's House", "kind": "house", "lot": (7.0, 8.0)}

X0, X1, Y0, Y1 = -3.05, 3.05, 2.7, 7.5
W, D, CX, CY = X1 - X0, Y1 - Y0, 0.0, (Y0 + Y1) / 2
ZG, HU = 2.7, 2.6
GX0, GX1, GY = 0.25, 3.0, 1.45                    # the gallery deck


def build(b):
    g = b.body(W, D, ZG, mat="masonry", col="warm", x=CX, y=CY)
    PC.plinth(g, h=0.5, doors=[("front", 4.7, 1.4)])
    up = b.body(W, D, HU, mat="plaster", col="sky", x=CX, y=CY, z=ZG)
    P.band(g, ZG - 0.1, h=0.18, out=0.06)
    P.door(g.front, 4.7, w=1.4, h=2.0, col="teal", z=0.1, double=True, frame="timber")
    P.window(up.front, 1.0, 0.9, w=0.8, h=1.25, shutters="teal", box=True)
    P.window(up.front, 2.45, 0.9, w=0.8, h=1.25, shutters="teal")
    P.window(up.front, 4.05, 0.9, w=0.8, h=1.25)
    P.door(up.front, 5.3, w=0.85, h=1.9, col="teal", z=0.03, frame="timber", lamp=True)
    P.exposed(up.front, "corners", n=5)
    for wl, gl in ((up.left, g.left), (up.right, g.right)):
        P.window(wl, 1.5, 0.9, w=0.75, h=1.2, shutters="teal", ajar=5)
        P.window(wl, 3.4, 0.9, w=0.75, h=1.2, ajar=5)
        P.window(gl, 2.4, 1.1, w=0.65, h=0.9, bars=(1, 1))
    P.door(g.back, 1.3, w=0.85, h=1.9, col="teal", z=0.12, frame="timber")
    P.window(g.back, 4.4, 1.1, w=0.7, h=0.95)
    P.window(up.back, 1.6, 0.9, w=0.75, h=1.2, shutters="teal", ajar=5)
    P.window(up.back, 4.4, 0.9, w=0.75, h=1.2, ajar=5)
    P.exposed(up.back, "base", n=8)
    P.ivy(g.left, 0.8, 0.2, w=1.5, h=3.4, n=7)
    rise = up.gable(ridge="x", pitch=47, mat="tiles", eave=0.3, verge=0.12, sag=0.12)
    for x in (-1.6, 1.3):
        P.dormer(b, x, Y0 + 0.8, ZG + HU + 0.62, w=1.0, h=0.95, depth=1.4, face=0, col="sky", shutters="teal" if x < 0 else None)
    PC.stack(b, X0 + 0.5, CY, ZG + HU + rise - 0.8, 2.7, w=0.5, d=0.8, flues=2)
    gallery(b)
    yard(b)


def gallery(b):
    """The working gallery and the stair to it."""
    z = ZG
    b.box(GX1 - GX0, Y0 - GY, 0.12, "planks", col="greyoak", x=(GX0 + GX1) / 2, y=(GY + Y0) / 2, z=z - 0.12, bottom=True)
    with b.detail(1):
        for x in (GX0 + 0.1, GX1 - 0.1):
            b.beam((x, GY + 0.1, 0), (x, GY + 0.1, z + 2.22), w=0.15)
            b.beam((x, GY + 0.1, z - 0.9), (x + (0.6 if x < 1 else -0.6), GY + 0.1, z - 0.14), w=0.1)
            b.beam((x, Y0, z - 0.2), (x, GY, z - 0.2), w=0.13, h=0.16)
        b.beam((GX0, GY + 0.1, z - 0.2), (GX1, GY + 0.1, z - 0.2), w=0.13, h=0.16)
        b.beam((GX0 - 0.1, GY + 0.1, z + 2.28), (GX1 + 0.1, GY + 0.1, z + 2.28), w=0.13, h=0.14)
    P.railing(b, [(GX0 + 0.1, GY + 0.1, z), (GX1 - 0.1, GY + 0.1, z), (GX1 - 0.1, Y0 - 0.05, z)], h=0.95, style="balusters", col="darkoak")
    with b.at(0, 0, z + 2.35):
        PC.shed_roof(b, GX1 - GX0 + 0.3, Y0 - GY + 0.1, pitch=16, z=0.0, x=(GX0 + GX1) / 2, y=Y0 + 0.03, mat="tiles", eave=0.18, verge=0.1, course=0.34, thick=0.09, barge=False)
    with b.at(X0 + 0.05, 2.1, 0, rz=270):          # the open stair climbs along the wall toward the gallery
        P.stairs(b, w=1.0, rise=z / 14, run=(GX0 - X0 - 0.05) / 14, n=14, solid=False, rail="balusters", lod=0)
    P.sack(b, GX1 - 0.5, GY + 0.75, z, r=0.26)
    with b.detail(2):                               # a net over the rail, floats on the deck
        for i in range(5):
            x = GX0 + 0.5 + 0.38 * i
            b.quad((x, GY + 0.04, z + 0.25), (x + 0.36, GY + 0.04, z + 0.25), (x + 0.36, GY + 0.04, z + 0.97), (x, GY + 0.04, z + 0.97), "cloth", col="#7f9aa0" if i % 2 else "#93aaa2", wind=(0.3, 0.3, 0, 0))
        for (x, y) in ((GX0 + 0.5, Y0 - 0.3), (GX0 + 0.75, Y0 - 0.25), (GX0 + 0.6, Y0 - 0.5)):
            b.blob(0.11, 0.11, 0.11, mat="paint", col="!#d97b35", x=x, y=y, z=z + 0.11, seg=6, rings=3, rough=0.0)


def yard(b):
    PC.yard(b, -3.3, 3.3, Y0, h=1.15, gate=(-2.15, 1.0), piers=1.45, gate_col="teal")
    with b.detail(1):
        b.beam((-0.4, 0.75, 0), (-0.4, 0.75, 2.3), w=0.09, col="greyoak")
    P.laundry(b, (-0.4, 0.75, 2.25), (GX0 + 0.1, GY + 0.1, 2.35), n=2, sag=0.2, cols=["#7f9aa0", "#93aaa2"])
    P.laundry(b, (-0.4, 0.75, 2.2), (-3.0, 1.1, 2.0), n=4, sag=0.3, cols=["#7f9aa0", "#93aaa2", "#8aa58f"])
    with b.detail(1):
        b.beam((-3.0, 1.1, 0), (-3.0, 1.1, 2.1), w=0.09, col="greyoak")
    P.crate(b, 2.5, 0.9, s=0.5, rz=8); P.crate(b, 2.1, 0.85, s=0.5, rz=-14); P.crate(b, 2.35, 0.88, 0.5, s=0.45, rz=22)
    P.barrel(b, -1.3, 2.3, r=0.27, h=0.72)
    PC.flowers(b, 1.0, 0.65, 0, w=1.4, d=0.4, n=5)
    P.bench(b, 1.3, 1.1, rz=0, w=1.2)
