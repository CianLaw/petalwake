# The Clockmender's House: tall, thin and exact, like its owner. The clock in the gable is the only one on the hill that agrees with the star-gazer's, and he will tell you so.
# Massing: a narrow three-storey house, gable to the street, under a gambrel roof with a dormer on each flank; the front door stands half a storey up at the head of a straight flight with iron rails; an oriel on brackets beside it, a clock in the gable.
# Materials: warm stone basement, ochre limewash, tiles, a tall brick stack. Accent: mustard.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Clockmender's House", "kind": "house", "lot": (6.0, 8.0)}

X0, X1, Y0, Y1 = -2.3, 2.3, 2.9, 7.5
W, D, CX, CY = X1 - X0, Y1 - Y0, 0.0, (Y0 + Y1) / 2
ZG, HU = 1.5, 5.4
SEC = [(0.0, 0.0), (0.95, 1.95), (2.3, 2.8)]       # the gambrel


def build(b):
    g = b.body(W, D, ZG, mat="masonry", col="warm", x=CX, y=CY)
    P.plinth(g, h=0.35)
    up = b.body(W, D, HU, mat="plaster", col="ochre", x=CX, y=CY, z=ZG)
    P.band(g, ZG - 0.1, h=0.18, out=0.06)
    P.quoins(up, z0=0.1, corners="fr", size=(0.5, 0.3, 0.48), mat="ashlar")
    # street front: the raised door, the cellar hatch, the oriel
    P.door(up.front, 1.4, w=0.95, h=2.05, arch=0.45, col="mustard", z=0.03, lamp=True)
    P.door(g.front, 3.55, w=0.9, h=1.15, arch=0.35, col="mustard", z=0.1, frame="stone", knob=False)
    P.window(up.front, 3.45, 0.85, w=0.85, h=1.3, shutters="mustard", box=True)
    P.window(up.front, 1.3, 3.45, w=0.8, h=1.3, shutters="mustard")
    oriel(b, up)
    rise = up.gable(ridge="y", section=SEC, mat="tiles", eave=0.22, verge=0.18, course=0.4)
    P.clock(up.front, W / 2, HU + 1.15, r=0.56, face="ivory", hands="black", rim="brass", hour=4, minute=38)
    # flanks and back
    for wl in (up.left, up.right):
        P.window(wl, 1.3, 0.9, w=0.75, h=1.25, ajar=4)
        P.window(wl, 3.2, 0.9, w=0.75, h=1.25, shutters="mustard", ajar=4)
        P.window(wl, 2.2, 3.45, w=0.75, h=1.25, shutters="mustard", ajar=4)
    P.window(g.right, 2.3, 0.45, w=0.7, h=0.6, lintel="stone", sill=False)
    P.door(up.back, 1.2, w=0.85, h=1.9, col="mustard", z=0.03, frame="timber")
    P.window(up.back, 3.3, 0.9, w=0.75, h=1.25)
    P.window(up.back, 1.3, 3.45, w=0.75, h=1.25, shutters="mustard", ajar=4)
    P.window(up.back, 3.3, 3.45, w=0.75, h=1.25, ajar=4)
    P.exposed(up.back, "both", n=8)
    P.balcony(up.back, 1.2, 0.0, w=1.5, out=0.34, rail="iron", brackets=True)
    P.ivy(g.left, 1.0, 0.1, w=1.3, h=3.0, n=6)
    for sx, face in ((-1, 270), (1, 90)):
        P.dormer(b, sx * (W / 2 - 0.45), CY + 0.3 * sx, ZG + HU + 0.55, w=1.0, h=0.95, depth=1.1, face=face, col="ochre", shutters=None, pitch=40)
    PC.stack(b, -0.75, Y1 - 1.1, ZG + HU + 1.6, 3.5, w=0.55, d=0.75, flues=2)
    # the flight to the door
    with b.at(X0 + 1.4, 0.62, 0):
        PC.outside_stair(b, n=8, w=1.3, rise=ZG / 8, run=0.27, landing=Y0 - 0.62 - 8 * 0.27, rail="iron", rail_sides="lr")
    garden(b)


def oriel(b, up):
    w, dp, h = 1.5, 0.7, 1.9
    with up.front.on(3.4, 3.25):
        bd = b.body(w, dp, h, mat="plaster", col="cream", x=0, y=0.15 - dp / 2, z=0, depth=0.1, floor="planks", foot=False)
        P.timber_frame(bd.front, posts=[0, w], rails=[0, 0.55, h], braces=[], w=0.12)
        P.window(bd.front, w / 2, 0.62, w=1.05, h=1.05, bars=(2, 1), lintel=None, sill=False, depth=0.08)
        PC.shed_roof(b, w + 0.24, dp + 0.08, pitch=40, z=h, x=0, y=0.17, mat="tiles", eave=0.1, verge=0.08, course=0.28, thick=0.07, barge=False)
        PC.cheeks(b, w, dp - 0.15, (dp - 0.15) * math.tan(rad(40)), mat="plaster", col="cream", x=0, y=0.15, z=h)
        with b.detail(1):
            for sx in (-1, 1):
                b.beam((sx * 0.6, 0.03, -0.85), (sx * 0.6, -0.5, -0.04), w=0.12)


def garden(b):
    PC.yard(b, -2.8, 2.8, Y0, h=1.0, gate=(X0 + 1.4, 1.2), piers=1.35, gate_col="mustard", coping="slab")
    PC.lamp_post(b, X0 + 2.4, 0.5, 0, h=2.5)
    P.planter(b, 1.6, 2.5, w=1.0)
    P.planter(b, -2.2, 2.45, w=0.5, bush=True)
    PC.flowers(b, 1.7, 0.75, 0, w=1.4, d=0.45, n=5)
    PC.flowers(b, -2.3, 1.2, 0, w=0.5, d=1.2, n=4)
