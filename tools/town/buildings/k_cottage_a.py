# Stair Cottage: two households under one thatch, the dyer's man below and the mill-hand above, whose only way in is the worn stone stair up the side (where the pots of herbs and the cat live).
# A narrow two-storey cottage with its eaves to the street under a steep thatched roof with a little shed dormer, and a solid outside stair climbing its right flank to a landing and the upper door.
# Warm rubble below, cream lime-wash above, golden thatch; accent green.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_k as K

META = {"name": "Stair Cottage", "kind": "cottage", "lot": (5.5, 7.0)}

HX, HW, HD = -0.55, 3.8, 5.8            # x -2.45 .. 1.35


def build(b):
    b.footprint(-2.6, 0.0, 2.5, 6.6, 7.8)
    g = b.body(HW, HD, 2.5, mat="masonry", col="warm", x=HX)
    P.plinth(g, h=0.45, out=0.05)
    for wl in (g.front, g.left, g.back):
        P.stones(wl, n=5, z0=0.5, z1=2.4)
    up = b.body(HW, HD, 2.1, mat="plaster", col="cream", x=HX, z=2.5)
    P.door(g.front, 1.05, w=0.9, h=1.95, z=0.17, col="green", steps=1, lamp=True)
    P.window(g.front, 2.75, 1.0, w=0.9, h=1.1, shutters="green", box=True)
    P.window(up.front, 1.05, 0.66, h=1.1, shutters="green")
    P.window(up.front, 2.75, 0.66, h=1.1, shutters="green")
    P.exposed(up.front, "corners")
    P.window(g.left, 2.9, 1.0, w=0.8, h=1.1)
    P.window(up.left, 2.9, 0.75, w=0.8, h=1.1)
    P.door(g.back, 1.1, w=0.9, h=1.9, z=0.12, col="green", frame="timber")
    P.window(g.back, 2.8, 1.0, w=0.9, h=1.1)
    P.window(up.back, 1.9, 0.66, h=1.1, shutters="green")
    with b.at(HX + HW / 2 + 0.55, 0.45, 0):
        PC.outside_stair(b, n=13, w=1.08, rise=2.5 / 13, run=0.27, landing=1.0, rail="balusters", rail_sides="r")
    P.door(up.right, 4.45, w=0.85, h=1.85, z=0.02, col="green", frame="timber")
    P.window(up.right, 1.6, 0.75, w=0.8, h=1.1, shutters="green")
    rise = up.gable(ridge="x", pitch=48, mat="thatch", eave=0.4, verge=0.1, thick=0.3, course=0.55, lip=0.07, sag=0.1)
    PH.cuttable(up.left, up.right)
    P.window(up.right, HD / 2, 2.1 + 0.6, w=0.65, h=0.85)
    P.dormer(b, HX + 0.2, 0.95, 5.45, w=1.1, h=0.75, depth=1.3, face=0, kind="shed", roof="thatch", col="cream", frame="ivory")
    P.chimney(b, HX - HW / 2 + 0.5, HD / 2, 6.5, 2.3, mat="masonry", col="warm", pots=1)
    PC.pots(b, (HX + HW / 2 + 0.2, 1.3, 0.62), (HX + HW / 2 + 0.2, 2.5, 1.5), n=4)
    PC.cat(b, HX + HW / 2 + 0.8, 4.6, 2.5, rz=120)
    with b.detail(1):
        b.beam((2.2, 6.4, 0), (2.2, 6.4, 3.4), w=0.1)
    P.laundry(b, (HX - 1.2, HD + 0.05, 3.9), (2.2, 6.4, 3.3), n=4)
    P.barrel(b, HX - 1.3, -0.45)
