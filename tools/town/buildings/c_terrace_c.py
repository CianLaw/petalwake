# The Thatched House: the last thatch on the hill, and its owner will not hear of tiles. You go in by the garden door in the wall, past the apple tree, and up the stair at the side.
# Massing: a stone ground floor under a jettied timber-framed storey and a deep thatched roof with one small dormer; a great stone chimney up the left gable; a stone stair up the right flank; a tall garden wall to the street with an arched doorway.
# Materials: warm stone, sage plaster in dark oak, thatch. Accent: pink.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Thatched House", "kind": "house", "lot": (6.5, 8.0)}

X0, X1, Y0, Y1 = -2.72, 1.75, 2.2, 7.4
W, D, CX, CY = X1 - X0, Y1 - Y0, (X0 + X1) / 2, (Y0 + Y1) / 2
ZG, HU, JET = 2.5, 2.5, 0.35


def build(b):
    g = b.body(W, D, ZG, mat="masonry", col="warm", x=CX, y=CY)
    PC.plinth(g, h=0.5, doors=[("front", 1.25, 0.9)])
    uw, ud = W + 0.1, D + JET
    up = b.body(uw, ud, HU, mat="plaster", col="sage", x=CX, y=Y1 - ud / 2, z=ZG, floor="planks", depth=0.16)
    for wl in (up.front, up.back):
        P.timber_frame(wl, braces="auto", z1=HU - 0.1)        # (a top rail right at the eaves pokes through the roof)
    P.timber_frame(up.left, braces="x", posts=[0, ud * 0.36, ud * 0.64, ud])
    P.timber_frame(up.right, braces="auto", posts=[0, 1.3, 2.6, 4.05, ud])
    with b.detail(1):                               # the jetty: joist ends and two brackets
        for sx in (-1, 1):
            b.beam((CX + sx * (W / 2 - 0.12), Y0 + 0.03, ZG - 0.75), (CX + sx * (W / 2 - 0.12), Y0 - JET + 0.05, ZG - 0.05), w=0.13)
    with b.detail(2):
        for i in range(8):
            x = X0 + 0.25 + (W - 0.5) * i / 7
            b.beam((x, Y0 + 0.1, ZG - 0.09), (x, Y0 - JET - 0.03, ZG - 0.09), w=0.11, h=0.14)
    # ground floor
    P.door(g.front, 1.25, w=0.9, h=1.95, col="pink", z=0.2, steps=1, frame="timber", lamp=True)
    P.window(g.front, 3.15, 1.0, w=1.1, h=1.15, bars=(2, 2), box=True, lintel="timber")
    P.window(g.back, 1.4, 1.1, w=0.7, h=0.95, lintel="timber")
    P.window(g.back, 3.3, 1.1, w=0.7, h=0.95, lintel="timber")
    P.window(g.left, 1.2, 1.1, w=0.65, h=0.9, lintel="timber")
    # upper floor
    P.window(up.front, 1.25, 0.95, w=0.85, h=1.1, lintel=None, shutters="pink", depth=0.12)
    P.window(up.front, 3.3, 0.95, w=0.85, h=1.1, lintel=None, shutters="pink", depth=0.12, box=True)
    P.door(up.right, 4.8, w=0.85, h=1.85, col="pink", z=0.03, frame="timber", lamp=True)
    P.window(up.right, 1.95, 0.95, w=0.75, h=1.05, lintel=None, depth=0.12)
    P.window(up.back, 1.3, 0.95, w=0.8, h=1.05, lintel=None, depth=0.12)
    P.window(up.back, 3.3, 0.95, w=0.8, h=1.05, lintel=None, depth=0.12)
    # the thatch
    rise = up.gable(ridge="x", pitch=50, mat="thatch", eave=0.42, verge=0.22, thick=0.34, course=0.62, lip=0.07, sag=0.14, barge=False)
    P.dormer(b, CX + 0.2, Y1 - ud + 0.75, ZG + HU + 0.55, w=1.05, h=0.85, depth=1.5, face=0, roof="thatch", col="sage", pitch=46)
    PC.doves(b, [(CX - 1.2, CY - 0.4, ZG + HU + rise + 0.08), (CX + 1.3, CY - 0.3, ZG + HU + rise + 0.02)])
    # the great chimney on the left gable
    cy = CY + 0.3
    b.box(0.36, 1.5, 4.7, "masonry", col="warm", x=X0 - 0.17, y=cy, z=0.0, sides="fbl", top=False)
    b.box(0.36, 1.5, 3.0, "masonry", col=shade("warm", 0.85), x=X0 - 0.17, y=cy, z=-3.0, sides="fbl", top=False)
    b.box(0.36, 1.5, 0.9, "masonry", col="warm", x=X0 - 0.17, y=cy, z=4.7, ty=0.46, sides="fbl", top=False)
    P.chimney(b, X0 - 0.1, cy, 5.5, 4.2, w=0.46, d=0.68, mat="masonry", col="warm", pots=2)
    # the stair up the right flank
    with b.at(X1 + 0.68, Y0 + 0.25, 0):
        PC.outside_stair(b, n=12, w=1.1, rise=ZG / 12, run=0.29, landing=1.3, rail="balusters", rail_sides="r")
    # the garden: a tall wall to the street with a door in it
    PC.yard(b, -3.02, 3.02, Y0 + 0.25, h=1.95, gate=(0.55, 1.05), gate_h=1.8, arch=0.5, gate_col="pink", pickets=False, left=False, cope_lod=2)
    PC.garden_wall(b, (-3.02, Y0 - 0.2), (-3.02, 0.14), h=1.95, t=0.32, cope_lod=2)
    P.tree(b, -1.75, 1.05, h=3.6, crown=0.82, col="#7cba5c")
    PC.climber(b, (1.3, 0.32, 1.9), (2.9, 0.32, 2.05), n=6, r=0.22, bloom=["#f2a0bd", "#e8497a", "#ffffff"])
    PC.flowers(b, -0.4, 0.75, 0, w=1.0, d=0.5, n=5)
    P.bench(b, 1.75, 1.55, rz=180, w=1.2)
    P.barrel(b, -2.4, 1.95, r=0.26, h=0.7)
