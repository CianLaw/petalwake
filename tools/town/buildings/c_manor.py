# The Dower House: a small manor at the edge of the Crown, built by a sea-captain for his mother. The forecourt gate is never locked, and the pear tree in the court is older than the house.
# Massing: an L of two ranges round a walled forecourt: the hall range across the back with three dormers and tall stacks, a gabled wing running forward to the street on the right, an eight-sided stair turret with an ogee cap in the angle between them; gate piers with stone balls, a well in the court.
# Materials: warm stone below, peach limewash above, ashlar quoins, tiled roofs, lead-grey slate on the turret cap. Accent: mint.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Dower House", "kind": "manor", "lot": (13.0, 11.0)}

HX0, HX1, HY0, HY1 = -6.0, 2.1, 5.4, 10.35           # hall range
WX0, WX1, WY0, WY1 = 2.1, 6.0, 0.5, 10.35            # wing
ZG, ZH, ZW = 3.0, 5.8, 6.4                           # top of the stone storey, hall eaves, wing eaves
TX, TY, TR, TH = 1.25, 4.55, 1.5, 9.4                # stair turret


def build(b):
    wing(b)
    hall(b)
    turret(b)
    court(b)


def hall(b):
    w, d = HX1 - HX0, HY1 - HY0
    cx, cy = (HX0 + HX1) / 2, (HY0 + HY1) / 2
    g = b.body(w, d, ZG, mat="masonry", col="warm", x=cx, y=cy)
    PC.plinth(g, h=0.6, doors=[("front", 3.3, 1.0), ("back", 2.0, 0.85)])
    up = b.body(w, d, ZH - ZG, mat="plaster", col="peach", x=cx, y=cy, z=ZG)
    P.band(g, ZG - 0.1, h=0.18, out=0.06)
    P.quoins(g, z0=0.6, corners="l", size=(0.56, 0.32, 0.5)); P.quoins(g, z0=0.6, corners="f", size=(0.56, 0.32, 0.5))
    P.door(g.front, 3.3, w=1.0, h=2.1, arch=0.45, col="mint", z=0.3, steps=2, porch="gable", lamp=True)
    for u in (1.2, 5.3, 6.9):
        P.window(g.front, u, 1.05, w=0.85, h=1.25, bars=(2, 2))
    for u, bx in ((1.2, True), (3.3, False), (5.3, True), (6.9, False)):
        P.window(up.front, u, 0.75, w=0.85, h=1.3, shutters="mint", box=bx)
    P.window(g.left, 2.5, 1.05, w=0.85, h=1.25, bars=(2, 2))
    P.window(up.left, 2.5, 0.75, w=0.85, h=1.3, shutters="mint")
    P.door(g.back, 2.0, w=0.85, h=1.95, col="mint", z=0.2, frame="timber")
    for u in (5.4,):
        P.window(g.back, u, 1.1, w=0.8, h=1.2)
    for u in (2.6, 6.2):
        P.window(up.back, u, 0.8, w=0.8, h=1.25, shutters="mint", ajar=5)
    P.exposed(up.left, "corners", n=6); P.exposed(up.back, "base", n=7)
    # the roof runs on into the wing's roof, so only its left end is a gable
    pitch = 45
    rise = d / 2 * math.tan(rad(pitch))
    up.left.gable = rise - 0.03
    rw = 3.8 - HX0
    b.gable_roof(rw, d, pitch=pitch, mat="tiles", x=HX0 + rw / 2, y=cy, z=ZH, ridge="x", eave=0.38, verge=0.14, sag=0.1)
    for x in (-4.4, -1.2):
        P.dormer(b, x, HY0 + 0.75, ZH + 0.62, w=1.1, h=1.0, depth=1.5, face=0, col="peach", frame="ivory", shutters="mint" if x < -2 else None)
    PC.stack(b, -4.9, cy + 0.3, ZH + rise - 0.9, 3.0, w=0.8, d=0.6, flues=2, style="diagonal")
    PC.stack(b, -0.9, cy - 0.3, ZH + rise - 0.9, 3.3, w=0.8, d=0.6, flues=2, style="diagonal")
    P.ivy(g.left, 0.9, 0.4, w=1.8, h=3.6, n=8, lod=2)
    P.ivy(g.back, 7.4, 0.3, w=1.4, h=3.0, n=5, lod=2)


def wing(b):
    w, d = WX1 - WX0, WY1 - WY0
    cx, cy = (WX0 + WX1) / 2, (WY0 + WY1) / 2
    g = b.body(w, d, ZG, mat="masonry", col="warm", x=cx, y=cy)
    PC.plinth(g, h=0.6, doors=[("front", 1.0, 0.95)])
    up = b.body(w, d, ZW - ZG, mat="plaster", col="peach", x=cx, y=cy, z=ZG)
    P.band(g, ZG - 0.1, h=0.18, out=0.06)
    P.quoins(g, z0=0.6, corners="frb", size=(0.56, 0.32, 0.5))
    P.quoins(up, z0=0.2, corners="fr", size=(0.5, 0.3, 0.5), mat="ashlar")
    P.door(g.front, 1.0, w=0.95, h=2.05, col="mint", z=0.25, steps=1, lamp=True)
    P.window(g.front, 2.65, 1.0, w=1.3, h=1.4, bars=(3, 2), box=True)
    P.window(up.front, w / 2, 0.8, w=1.5, h=1.6, bars=(3, 2), shutters="mint")
    PC.oculus(up.front, w / 2, ZW - ZG + 1.05, r=0.36)
    for u, z in ((2.6, 1.0), (7.3, 1.0)):
        P.window(g.right, u, z, w=0.85, h=1.25, bars=(2, 2))
    for u in (2.6, 7.3):
        P.window(up.right, u, 0.9, w=0.85, h=1.4, shutters="mint", ajar=5)
    P.window(up.left, 7.6, 0.9, w=0.85, h=1.4, shutters="mint")       # looks over the court
    P.window(g.left, 7.6, 1.0, w=0.85, h=1.25, bars=(2, 2))
    P.window(g.back, w / 2, 1.1, w=0.8, h=1.2)
    P.window(up.back, w / 2, 0.9, w=0.85, h=1.4)
    P.exposed(up.right, "base", n=8)
    rise = up.gable(ridge="y", pitch=50, mat="tiles", eave=0.3, verge=0.18, sag=0.08)
    PC.stack(b, WX1 - 0.75, 6.4, ZW + 0.3, 3.7, w=0.7, d=0.6, flues=2, style="square")
    P.ivy(g.right, 9.2, 0.3, w=1.2, h=3.4, n=6, lod=2)


def turret(b):
    """The stair turret in the angle: eight-sided, an ogee cap, its door to the court."""
    with b.at(TX, TY):
        f = PC.poly_tower(b, 8, TR, TH, taper=0.95, mat="masonry", col="warm")
        w = f[0].w
        PC.poly_plinth(b, 8, TR, h=0.6, out=0.07, doors=[(7, w / 2, 0.8)])
        P.door(f[7], w / 2, w=0.8, h=1.95, arch=0.4, col="mint", z=0.3, steps=1)
        P.window(f[0], w / 2, 3.0, w=0.45, h=1.1, arch=0.22)
        P.window(f[6], w / 2, 4.6, w=0.45, h=1.1, arch=0.22)
        P.window(f[7], w / 2, 6.6, w=0.45, h=1.1, arch=0.22)
        P.window(f[0], w / 2, 7.6, w=0.45, h=1.0, arch=0.22)
        with b.at(rz=22.5):
            rt = TR * 0.95
            P.ring_band(b, rt - 0.02, TH - 0.2, h=0.2, out=0.12, seg=8)
            sec = [(rt + 0.3, -0.12), (rt + 0.05, 0.32), (rt * 0.82, 0.62), (rt * 0.62, 1.15), (rt * 0.5, 1.95), (rt * 0.34, 2.65), (0.14, 3.1), (0.0, 3.5)]
            b.cone_roof(rt, 3.5, mat="slate", z=TH, seg=8, smooth=False, section=sec, course=0.4, lip=0.04)


def court(b):
    """The forecourt: wall and gate to the street, the pear tree, the well, beds along the walls."""
    PC.yard(b, -6.26, WX0, HY0, h=1.9, gate=(-2.3, 1.7), piers=2.35, gate_col="mint", pickets=False, right=False, cope_lod=2)
    P.tree(b, -4.4, 2.5, h=4.6, crown=1.25, col="#7ab65a")
    PC.well(b, -0.9, 2.1)
    P.bench(b, -5.5, 4.6, rz=0, w=1.5)
    PC.flowers(b, -5.2, 0.8, 0, w=1.6, d=0.5, n=6)
    PC.flowers(b, -0.2, 0.8, 0, w=1.8, d=0.5, n=6)
    PC.flowers(b, -3.2, 4.9, 0, w=1.6, d=0.5, n=5)
    P.planter(b, -1.55, 5.0, w=0.6, bush=True); P.planter(b, -0.2, 5.0, w=0.6, bush=True)
    P.barrel(b, 4.9, 0.1, r=0.27, h=0.72)
