# The bakehouse and wash-house of the lanes: the oven is fired twice a week and every household brings its dough; on the other days the washing is done at the trough, in the warmth of the oven wall.
# A low lime-washed room under a tiled roof; the oven bulges out of one gable as a half-round of bare stone with a big brick stack over it; along the front a pent roof on posts shelters the stone trough and the pump.
# Whitewash over rubble, warm stone, brick and terracotta; accent teal.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC
import parts_m as PM

META = {"name": "The Bakehouse", "kind": "bakehouse", "lot": (7.0, 6.0), "terrace": False}


def build(b):
    acc = "teal"
    x0, x1, y0, y1 = -3.05, 1.2, 1.5, 5.35
    W, D, cx, cy = x1 - x0, y1 - y0, (x0 + x1) / 2, (y0 + y1) / 2
    H = 2.6
    bd = b.body(W, D, H, mat="plaster", col="white", x=cx, y=cy)
    P.plinth(bd, h=0.6)
    f = bd.front
    # --- the front: the stable door, a window under the pent
    PM.half_door(f, 3.45, w=1.05, h=2.0, col=acc, frame="timber")
    P.window(f, 1.5, 1.0, w=0.9, h=1.0, bars=(1, 1), lintel="timber")
    P.sign(f, 4.05, 2.45, emblem="loaf", col="brown", board="ivory", out=0.6)
    for wl in bd.walls:
        P.exposed(wl, "both", n=7)
    # --- the other walls
    P.window(bd.left, 1.2, 1.05, w=0.7, h=0.9); P.window(bd.left, 2.9, 1.05, w=0.7, h=0.9, shutters=acc)
    P.door(bd.back, 1.1, w=0.9, h=1.95, z=0.1, col=acc, frame="timber")
    P.window(bd.back, 2.9, 1.0, w=0.9, h=1.0, shutters=acc)
    P.window(bd.left, D / 2, H + 0.55, w=0.5, h=0.7)
    rise = bd.gable(ridge="x", pitch=45, eave=0.33, verge=0.25, sag=0.1)
    L.cut_gable(bd.left)
    # --- the oven: a half-round of bare stone against the gable, and its stack
    ox, oy, orad = x1, cy, 1.45
    ov = b.round(orad, 1.9, mat="masonry", col="warm", x=ox, y=oy, seg=16)
    P.round_base(b, orad, h=0.5, out=0.12, seg=16, x=ox, y=oy)
    ov.opening(90, 0.55, 0.5, 0.45, arch=0.2, pane="paint", pane_col="#2a2622", depth=0.16)
    P.stones(ov, n=14, z0=0.5, z1=1.8, u0=ov.u_of(5), u1=ov.u_of(175))
    with b.at(ox, oy, 0):
        b.revolve([(orad + 0.12, 1.86), (orad + 0.1, 1.98), (orad - 0.25, 2.5), (0.85, 2.95), (0.3, 3.15)], "flagstone", col="sand", seg=8, a0=0, a1=180)
    PM.stack(b, ox + 0.12, oy, 0.0, 8.7, w=0.95, d=0.95, base=(1.45, 1.6, 3.5), mat="brick", pots=3)
    L.cat(b, ox + 0.95, oy - 0.75, 2.33, rz=110, col="#3b3632")
    # --- the wash-house: a pent on posts over the trough
    px0, px1, py0 = x0 + 0.02, -0.15, 0.2
    pw, pm = px1 - px0, (px0 + px1) / 2
    with b.at(pm, py0, 1.95):
        L.pent(b, pw, y0 - py0, 0.42, eave=0.12, verge=0.1, course=0.34)
    with b.detail(1):
        for x in (px0 + 0.1, pm, px1 - 0.1):
            b.beam((x, py0 + 0.08, 0), (x, py0 + 0.08, 1.95), w=0.14)
            b.beam((x, py0 + 0.08, 1.5), (x + (0.38 if x < px1 - 0.2 else -0.38), py0 + 0.08, 1.9), w=0.08, caps=False)
        b.beam((px0, py0 + 0.08, 1.9), (px1, py0 + 0.08, 1.9), w=0.13, h=0.15)
    b.box(pw, y0 - py0, 0.06, "flagstone", col="sand", x=pm, y=(py0 + y0) / 2, lod=1)
    L.trough(b, pm + 0.35, (py0 + y0) / 2 + 0.1, 0.06, w=1.9, d=0.72, h=0.6)
    L.pump(b, px0 + 0.38, (py0 + y0) / 2 + 0.1, 0.06, rz=90)
    with b.detail(2):                        # a tub of washing and a board
        with b.at(px1 - 0.45, py0 + 0.55, 0.06):
            b.revolve([(0.26, 0.0), (0.32, 0.32), (0.3, 0.32)], "planks", col="#c9a57a", seg=9)
            b.blob(0.26, 0.26, 0.14, mat="cloth", col="linen", z=0.34, seg=6, rings=2, rough=0.2)
        b.beam((pm + 1.2, y0 - 0.06, 0.06), (pm + 1.2, y0 - 0.28, 0.85), w=0.3, h=0.03, mat="planks", col="greyoak", up=(0, 1, 0))
    # --- the yard: firewood, flour, the peel and the cart
    L.logs(b, 2.95, 1.25, 0, w=1.9, h=1.0, d=0.5, rz=270)
    with b.detail(2):
        for y in (0.28, 2.22):
            b.beam((2.95, y, 0), (2.95, y, 1.15), w=0.07, caps=False)
    P.sack(b, 0.95, y0 - 0.32, 0, r=0.3); P.sack(b, 0.5, y0 - 0.42, 0, r=0.26); P.sack(b, 0.8, y0 - 0.36, 0.36, r=0.24)
    L.peel(b, 1.05, y0 - 0.03, 0, h=2.2)
    L.handcart(b, 1.15, 0.2, 0, rz=205, load=("#d9a86a", "#c9955a", "#e0b87a"))
    P.laundry(b, (x0 + 0.12, y1 + 0.1, 2.0), (x0 + 2.9, y1 + 0.38, 1.95), n=4, sag=0.2)
    b.beam((x0 + 2.9, y1 + 0.38, 0), (x0 + 2.9, y1 + 0.38, 2.05), w=0.08, lod=1)
    P.bench(b, cx + 0.3, y1 + 0.24, 0, rz=180, w=1.3)
