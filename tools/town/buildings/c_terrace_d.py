# The Physician's House: the doctor sees patients in the little tower room, so that nobody has to pass through the house; the herbs for his cupboard grow in the walled garden at the side.
# Massing: a hipped house with a square porch-tower stepping forward at its left corner under a steep pyramid roof; a stone stair along the front up to the tower's side door; a walled garden down the right flank with a tree.
# Materials: warm stone below, lilac limewash above, tiles, two round stacks. Accent: green.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Physician's House", "kind": "house", "lot": (8.0, 8.0)}

X0, X1, Y0, Y1 = -3.48, 1.6, 2.6, 7.5
W, D, CX, CY = X1 - X0, Y1 - Y0, (X0 + X1) / 2, (Y0 + Y1) / 2
ZG, HU = 2.7, 2.7
TX0, TX1, TY0, TY1 = -3.48, -1.5, 1.0, 2.9        # the porch-tower
TW, TD, TCX, TCY = TX1 - TX0, TY1 - TY0, (TX0 + TX1) / 2, (TY0 + TY1) / 2


def build(b):
    g = b.body(W, D, ZG, mat="masonry", col="warm", x=CX, y=CY)
    PC.plinth(g, h=0.5, doors=[("right", 3.4, 0.85)])
    up = b.body(W, D, HU, mat="plaster", col="lilac", x=CX, y=CY, z=ZG)
    P.band(g, ZG - 0.1, h=0.18, out=0.06)
    P.quoins(g, z0=0.5, corners="rb", size=(0.52, 0.3, 0.45))
    P.window(up.front, 3.0, 0.9, w=0.8, h=1.3, shutters="green", box=True)
    P.window(up.front, 4.45, 0.9, w=0.8, h=1.3, shutters="green")
    P.window(g.front, 4.5, 1.2, w=0.6, h=0.8, bars=(1, 1))
    P.door(g.right, 3.4, w=0.85, h=1.95, col="green", z=0.2, steps=1, frame="timber", lamp=True)
    P.window(g.right, 1.3, 1.05, w=0.75, h=1.1, bars=(2, 2))
    P.window(up.right, 1.3, 0.9, w=0.8, h=1.3, shutters="green", box=True)
    P.window(up.right, 3.5, 0.9, w=0.8, h=1.3, shutters="green")
    P.window(up.left, 1.5, 0.9, w=0.75, h=1.25, ajar=4)
    P.window(up.left, 3.5, 0.9, w=0.75, h=1.25, shutters="green", ajar=4)
    P.window(g.left, 2.4, 1.1, w=0.65, h=0.9)
    P.window(g.back, 1.3, 1.1, w=0.7, h=0.95)
    P.window(g.back, 3.9, 1.1, w=0.7, h=0.95)
    P.window(up.back, 1.4, 0.9, w=0.75, h=1.25, shutters="green", ajar=4)
    P.window(up.back, 3.8, 0.9, w=0.75, h=1.25, ajar=4)
    P.exposed(up.right, "corners", n=6)
    P.ivy(g.back, 4.7, 0.2, w=1.3, h=3.2, n=6)
    rise = up.hip(pitch=42, mat="tiles", eave=0.3)
    PC.stack(b, CX - 1.25, CY, ZG + HU + rise - 0.9, 2.8, w=0.8, d=0.55, flues=2, style="round")
    PC.stack(b, CX + 1.3, CY, ZG + HU + rise - 0.9, 2.4, w=0.5, d=0.5, flues=1, style="round")
    tower(b)
    with b.at(X1 - 0.05, Y0 - 0.58, 0, rz=90):      # the stair climbs along the front toward the tower door
        PC.outside_stair(b, n=13, w=1.1, rise=ZG / 13, run=(X1 - 0.05 - TX1) / 13, rail="iron", rail_sides="l")
    garden(b)


def tower(b):
    tg = b.body(TW, TD, ZG, mat="masonry", col="warm", x=TCX, y=TCY)
    PC.plinth(tg, h=0.5, doors=[("front", TW / 2, 0.9)])
    th = 3.9
    tu = b.body(TW, TD, th, mat="plaster", col="lilac", x=TCX, y=TCY, z=ZG)
    P.band(tg, ZG - 0.1, h=0.18, out=0.06)
    P.quoins(tg, z0=0.5, corners="fl", size=(0.5, 0.3, 0.45))
    P.door(tg.front, TW / 2, w=0.9, h=2.0, arch=0.42, col="green", z=0.22, steps=1, lamp=True)
    P.sign(tg.front, 0.3, 2.45, emblem="flower", col="green", out=0.6)
    P.door(tu.right, 1.02, w=0.8, h=1.85, col="green", z=0.03, frame="timber")
    P.window(tu.front, TW / 2, 0.9, w=0.8, h=1.3, arch=0.36, shutters="green", box=True)
    P.window(tu.front, TW / 2, 2.75, w=0.6, h=0.85, arch=0.28, lintel=None)
    P.window(tu.left, TD / 2, 1.0, w=0.6, h=1.1, ajar=4)
    P.window(tu.left, TD / 2, 2.75, w=0.5, h=0.8, lintel=None)
    P.window(tu.right, 1.0, 2.75, w=0.5, h=0.8, lintel=None)
    rise = tu.hip(pitch=57, mat="tiles", eave=0.3, course=0.36)
    PC.vane(b, TCX, TCY, ZG + th + rise - 0.1, h=1.5, shape="cock")


def garden(b):
    PC.yard(b, -3.78, 3.8, TY0, h=1.3, gate=(1.0, 1.0), piers=1.6, gate_col="green", right=False)
    PC.garden_wall(b, (3.8, 0.14), (3.8, Y1), h=1.6, t=0.32)
    PC.garden_wall(b, (3.8, Y1), (X1, Y1), h=1.6, t=0.32)
    P.tree(b, 2.7, 5.6, h=4.0, crown=0.85, col="#72b356")
    PC.flowers(b, 3.12, 2.6, 0, w=0.5, d=2.4, n=7, cols=["#b08ae6", "#f4f1e4", "#f5c842"])
    PC.flowers(b, 2.0, 6.9, 0, w=0.5, d=0.5, n=3, cols=["#b08ae6", "#f4f1e4"])
    P.bench(b, 2.2, 3.9, rz=90, w=1.2)
    with b.at(2.55, 1.2, 0):                         # a sundial
        with b.detail(2):
            b.revolve([(0.2, 0.0), (0.12, 0.12), (0.09, 0.85), (0.24, 0.95), (0.24, 1.0)], "ashlar", col="stone", seg=8, close_top=True)
            b.tri((0, -0.16, 1.0), (0, 0.14, 1.0), (0, 0.14, 1.2), "metal", col="brass")
            b.tri((0, 0.14, 1.0), (0, -0.16, 1.0), (0, 0.14, 1.2), "metal", col="brass")
    PC.flowers(b, -0.6, 0.7, 0, w=1.6, d=0.4, n=5)
