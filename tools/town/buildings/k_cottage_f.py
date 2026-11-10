# Turret Cottage: the shot-tower keeper's house; he could not live without a stair that winds, so he built his own little round tower on the corner, and climbs it every night to look at the big one.
# A two-storey gable-fronted cottage with a round stair turret engaged at its front right corner, capped by a slate cone with a weathercock that stands well above the tiled roof; the street door is in the foot of the turret.
# Warm rubble, rose lime-wash, tiles on the house and slate on the turret; accent plum.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_k as K

META = {"name": "Turret Cottage", "kind": "cottage", "lot": (5.5, 7.0)}

HX, HW, D = -0.7, 3.5, 6.0               # the house: x -2.45 .. 1.05
TX, TY, TR, TH = 1.45, 1.22, 1.0, 6.8    # the turret


def build(b):
    b.footprint(-2.55, 0.0, 2.58, 6.2, 7.0)
    g = b.body(HW, D, 2.5, mat="masonry", col="warm", x=HX)
    P.plinth(g, h=0.5, out=0.05)
    for wl in g.walls:
        P.stones(wl, n=5, z0=0.55, z1=2.4)
    up = b.body(HW, D, 2.2, mat="plaster", col="rose", x=HX, z=2.5)
    P.window(g.front, 1.25, 1.0, w=1.0, h=1.15, shutters="plum", box=True)
    P.window(up.front, 1.25, 0.8, shutters="plum")
    P.exposed(up.front, "corners")
    P.window(g.left, 1.5, 1.0, w=0.8, h=1.1)
    P.window(g.left, 4.3, 1.0, w=0.8, h=1.1)
    P.window(up.left, 2.9, 0.8, w=0.8, h=1.1)
    P.window(g.right, 4.3, 1.0, w=0.8, h=1.1, shutters="plum")
    P.window(up.right, 4.3, 0.8, w=0.8, h=1.1, shutters="plum")
    P.door(g.back, 1.1, w=0.9, h=1.9, z=0.12, col="plum", frame="timber")
    P.window(g.back, 2.6, 1.0, w=0.8, h=1.1)
    P.window(up.back, 1.75, 0.8, shutters="plum")
    rise = up.gable(ridge="y", pitch=48, mat="tiles", sag=0.08, eave=0.08, verge=0.3)
    PH.cuttable(up.front, up.back)
    P.window(up.front, HW / 2, 2.2 + 0.4, w=0.6, h=0.8, arch=0.25)
    P.chimney(b, HX - 1.2, 4.6, 4.9, 2.7, mat="brick", pots=2)

    # ------------------------------------------------------------------ the stair turret
    t = b.round(TR, TH, r1=0.92, mat="masonry", col="warm", x=TX, y=TY, seg=14, depth=0.26)
    P.round_base(b, TR, h=0.6, out=0.1, ring=t, seg=14)
    P.door(t, 0, w=0.8, h=1.95, z=0.17, arch=0.4, col="plum", steps=1, lamp=True)
    P.window(t, 0, 3.4, w=0.45, h=0.9, arch=0.22)
    P.window(t, 75, 5.0, w=0.45, h=0.9, arch=0.22)
    PC.slit(t, 50, 1.9)
    PC.slit(t, 110, 3.2)
    P.stones(t, n=14, z0=0.7, z1=6.2)
    P.ivy(t, 185, 0.3, w=0.9, h=3.6, n=8)
    P.ring_band(b, 0.93, TH - 0.5, h=0.18, out=0.07, col="sand", seg=14, x=TX, y=TY)
    b.cone_roof(0.92, 2.3, mat="slate", x=TX, y=TY, z=TH, seg=14, eave=0.2, flare=0.4, finial=False)
    PC.vane(b, TX, TY, TH + 2.25, h=1.3, shape="cock")
    P.bench(b, HX - 0.2, -0.5, 0, w=1.2)
    PC.cat(b, HX + 0.9, -0.42, 0.0, rz=30)
    P.barrel(b, 2.2, 2.9, 0)
