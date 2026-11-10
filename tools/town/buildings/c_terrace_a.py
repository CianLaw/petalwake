# The Chandler's House: candles and lamp-oil below, the family above. The cellar doors open straight onto the yard for the barrels; everyone else climbs the stair along the side.
# Massing: a narrow gable-fronted house on a stone undercroft; a stone stair up its left flank to a side door under a little canopy; a round window in the gable, one tall stack; a walled yard with a gate at the stair foot.
# Materials: warm stone below, peach limewash above, tiles. Accent: orange.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Chandler's House", "kind": "house", "lot": (6.0, 8.0)}

X0, X1, Y0, Y1 = -1.65, 2.65, 2.3, 7.55
W, D, CX, CY = X1 - X0, Y1 - Y0, (X0 + X1) / 2, (Y0 + Y1) / 2
ZG, HU = 2.6, 2.8


def build(b):
    g = b.body(W, D, ZG, mat="masonry", col="warm", x=CX, y=CY)
    PC.plinth(g, h=0.5, doors=[("front", 1.55, 1.5)])
    up = b.body(W, D, HU, mat="plaster", col="peach", x=CX, y=CY, z=ZG)
    P.band(g, ZG - 0.1, h=0.18, out=0.06)
    P.quoins(g, z0=0.5, corners="fr", size=(0.52, 0.3, 0.42))
    # the street front
    P.door(g.front, 1.55, w=1.5, h=2.0, arch=0.5, col="orange", z=0.12, double=True, lamp=True)
    P.window(g.front, 3.4, 1.15, w=0.6, h=0.8, bars=(1, 1))
    P.window(up.front, 1.15, 0.85, w=0.8, h=1.3, shutters="orange", box=True)
    P.window(up.front, 3.15, 0.85, w=0.8, h=1.3, shutters="orange", box=True)
    P.sign(up.front, 2.15, 0.6, emblem="anchor", col="orange", out=0.7)
    P.exposed(up.front, "corners", n=6)
    # the flanks and the back
    P.door(up.left, 0.72, w=0.85, h=1.9, col="orange", z=0.03, frame="timber", lamp=True, porch="gable")
    P.window(up.left, 3.3, 0.95, w=0.75, h=1.2, shutters="orange")
    P.window(up.right, 1.4, 0.9, w=0.75, h=1.25, shutters="orange", ajar=4)
    P.window(up.right, 3.9, 0.9, w=0.75, h=1.25, ajar=4)
    P.window(g.right, 2.6, 1.1, w=0.6, h=0.8, bars=(1, 1))
    P.window(up.back, 1.2, 0.9, w=0.75, h=1.25, shutters="orange", ajar=4)
    P.window(up.back, 3.2, 0.9, w=0.75, h=1.25, ajar=4)
    P.window(g.back, 2.2, 1.1, w=0.6, h=0.8)
    P.ivy(g.back, 3.6, 0.2, w=1.4, h=3.6, n=7)
    rise = up.gable(ridge="y", pitch=52, mat="tiles", eave=0.2, verge=0.12, sag=0.07)
    PC.oculus(up.front, W / 2, HU + rise * 0.42, r=0.3)
    P.chimney(b, X1 - 0.85, 5.7, ZG + HU + 0.4, 3.2, w=0.55, d=0.5, mat="brick", pots=2)
    # the stair up the left flank
    with b.at(X0 - 0.6, Y0 + 0.2, 0):
        PC.outside_stair(b, n=13, w=1.1, rise=ZG / 13, run=0.29, landing=1.2, rail="iron", rail_sides="l")
    # the yard
    PC.yard(b, -2.78, 2.78, Y0, h=1.25, gate=(-1.85, 0.95), piers=1.55, gate_col="orange", left=False)
    PC.garden_wall(b, (-2.78, Y0 + 0.2), (-2.78, 0.14), h=1.25, t=0.32)
    P.barrel(b, 1.2, 1.75, r=0.3, h=0.8); P.barrel(b, 1.85, 1.8, r=0.3, h=0.8); P.barrel(b, 1.5, 1.72, 0.8, r=0.27, h=0.7)
    P.crate(b, 2.1, 1.0, s=0.55, rz=12); P.crate(b, 2.15, 1.05, 0.55, s=0.42, rz=30)
    P.bench(b, -0.9, 0.75, rz=180, w=1.3)
    PC.flowers(b, 0.9, 0.62, 0, w=1.2, d=0.4, n=5)
    P.planter(b, -1.2, Y0 - 0.25, w=0.5, bush=True)
