# The Pilot's Cottage: the harbour pilot must see the bar from his bed, so his grandfather built the stair into a turret with windows at the top.
# A narrow two-storey house, gable to the quay (stone below, peach plaster above), with a round stair turret on its corner rising
# past the eaves to a candle-snuffer slate cone and the pilot's flag; a tarred store behind. Warm stone, peach, tiles and slate; accent mustard.
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "The Pilot's Cottage", "kind": "cottage", "lot": (6.0, 7.0), "lean": (0.002, 0.002)}

TX, TY = 1.5, 1.35


def build(b):
    g = b.body(3.7, 5.0, 2.5, mat="masonry", col="warm", x=-0.75, y=2.8)                 # x -2.6 .. 1.1, y 0.3 .. 5.3
    up = b.body(3.7, 5.0, 2.3, mat="plaster", col="peach", x=-0.75, y=2.8, z=2.5)
    H.cuttable(up.front, up.back)
    P.window(g.front, 1.25, 1.0, w=1.0, h=1.1, bars=(2, 1), shutters="mustard", box=True, lintel="stone")
    P.window(up.front, 0.85, 0.85, w=0.7, h=1.0, shutters="mustard")
    P.window(up.front, 2.25, 0.85, w=0.7, h=1.0, shutters="mustard")
    P.window(up.front, 1.85, 2.85, w=0.55, h=0.7, lintel=None, arch=0.27)
    P.window(g.left, 1.4, 1.0, w=0.8, h=1.0, lintel="stone")
    P.window(g.left, 3.7, 1.0, w=0.8, h=1.0, lintel="stone")
    P.window(up.left, 1.4, 0.85, w=0.7, h=1.0, shutters="mustard")
    P.window(up.left, 3.7, 0.85, w=0.7, h=1.0, shutters="mustard", box=True)
    P.door(g.back, 1.2, w=0.85, h=1.9, col="mustard", frame="timber", z=0.1)
    P.window(g.back, 2.9, 1.05, w=0.7, h=0.9, lintel="stone")
    P.window(up.back, 1.85, 0.85, w=0.7, h=1.0, shutters="mustard")
    P.window(up.right, 3.9, 0.85, w=0.7, h=1.0)
    P.plinth(g, h=0.45)
    P.quoins(g, corners="fl", z0=0.45, col="sand")
    P.exposed(up.left, "corners", n=8)
    up.gable(ridge="y", pitch=50, mat="tiles", eave=0.28, verge=0.3, sag=0.1)
    P.chimney(b, -1.95, 4.0, 4.4, 3.4, w=0.65, d=0.6, mat="brick", pots=2)
    # ------------------------------------------------------------------ the stair turret
    t = b.round(1.05, 6.6, r1=0.98, mat="masonry", col="warm", x=TX, y=TY, seg=14)
    P.door(t, 0, w=0.85, h=1.95, arch=0.42, col="mustard", z=0.17, steps=1, lamp=True)
    P.round_base(b, 1.05, h=0.55, out=0.16, ring=t, seg=14)
    P.window(t, 62, 2.4, w=0.4, h=0.9, arch=0.2, lintel=None)
    P.window(t, 300, 3.6, w=0.4, h=0.9, arch=0.2, lintel=None)
    for a in (0, 90, 250):
        P.window(t, a, 5.3, w=0.5, h=0.75, lintel=None, sill=True)
    P.stones(t, n=14, z0=0.6, z1=5.0, u1=t.w)
    P.ring_band(b, 0.99, 6.25, h=0.16, out=0.1, x=TX, y=TY, seg=14)
    b.cone_roof(0.98, 2.9, mat="slate", x=TX, y=TY, z=6.6, seg=14, eave=0.32, flare=0.5, course=0.42, finial=False)
    P.flag(b, TX, TY, 9.4, pole=1.9, w=1.2, h=0.6, col="stripe_red", kind="banner", pole_col="ivory")
    # ------------------------------------------------------------------ the tarred store behind, the pilot's gear
    lt = H.leanto(b, 1.1, 4.0, 2.4, 1.5, 1.9, rz=90, pitch=26, mat="planks", col=H.TAR_OLD, roof="tiles", plinth=0.3)
    P.door(lt.left, 0.8, w=0.7, h=1.65, col="mustard", frame=None, z=0.06)
    H.hatch(lt.front, 1.3, 0.95, w=0.6, h=0.6, col="mustard")
    H.battens(lt.front, col=H.TAR_OLD, z0=0.3)
    H.anchor(b, -2.15, 0.26, h=1.3)
    H.rope_coil(b, 0.35, -0.35, r=0.3)
    P.barrel(b, 2.7, 2.6, r=0.26, h=0.72)
    P.bench(b, -0.9, -0.2, w=1.3)
    H.buoy(b, 2.5, -0.3, col="!#d9a431", stripe="!#2c2a2a", s=0.85, flag="stripe_red")
    PC.lamp_post(b, -2.5, -0.85, h=2.6)
    H.pots(b, -1.9, 6.1, rz=10, n=3)
    H.fish_rack(b, 0.9, 6.3, w=1.8, h=1.6, rows=2, n=6)
