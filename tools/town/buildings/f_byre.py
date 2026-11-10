# Buttercup Byre: the cowshed of the low pasture; five half-doors, five names chalked up in the cowman's head, and Daisy always looking out of the second.
# Massing: one long low shed under a single pent roof that is high over the row of half-doors and falls to the back; oak posts between the
#          doors, a trough and churns in front.
# Materials: warm rubble, oak, grey shingles; accent mint.
from kit import *
import parts as P
import parts_k as PK
import parts_f as F

META = {"name": "Buttercup Byre", "kind": "barn", "lot": (10.0, 5.0)}

X0, X1, Y0, Y1 = -4.5, 4.5, 1.15, 4.35
LOW, RISE = 2.1, 0.85


def cow(b):
    """A cow's head looking out over a half-door. Frame: the middle of the door's ledge, -y out."""
    hide, white = F._paint("#8a5a3c"), F._paint("#f2ead8")
    with b.detail(2):
        with b.at(0.05, -0.1, 0.12, rx=14, rz=12):
            b.box(0.3, 0.5, 0.3, "paint", col=hide, y=-0.05, z=0.0, bottom=True)
            b.box(0.24, 0.24, 0.22, "paint", col=white, y=-0.38, z=0.0, bottom=True)
            b.box(0.25, 0.06, 0.1, "paint", col=F._paint("#e8a9a0"), y=-0.52, z=0.02, bottom=True)
            b.box(0.1, 0.3, 0.012, "paint", col=white, y=-0.1, z=0.3)
            for sx in (-1, 1):
                b.beam((sx * 0.13, 0.12, 0.28), (sx * 0.27, 0.16, 0.36), w=0.07, h=0.03, mat="paint", col=hide, caps=False)
                b.beam((sx * 0.11, 0.1, 0.3), (sx * 0.2, 0.08, 0.46), w=0.035, mat="paint", col=white, caps=False)
                b.box(0.045, 0.02, 0.045, "paint", col="black", x=sx * 0.152, y=-0.1, z=0.17)


def build(b):
    w, d, cx, cy = X1 - X0, Y1 - Y0, 0.0, (Y0 + Y1) / 2
    bd = b.body(w, d, LOW, mat="masonry", col="warm", x=cx, y=cy)
    P.plinth(bd, h=0.4, out=0.06)
    doors = (1.0, 2.75, 4.5, 6.25, 8.0)
    tops = (100, 104, "shut", 96, "shut")
    for u, tp in zip(doors, tops):
        F.half_door(bd.front, u, w=1.1, h=1.95, z=0.08, col="mint", top=tp)
    for u in (1.4, 4.5, 7.6):
        P.window(bd.back, u, 1.05, w=0.7, h=0.6, lintel="timber", bars=(1, 0))
    P.window(bd.left, d / 2, 0.95, w=0.7, h=0.7, lintel="timber")
    P.window(bd.right, d / 2, 0.95, w=0.7, h=0.7, lintel="timber")
    F.pent_roof(bd, RISE, high="front", over=0.42, mat="shingle", eave=0.34, verge=0.28, course=0.38, thick=0.12)
    with b.detail(1):                                  # oak posts and the long beam over the doors
        for u in (0.1, 1.87, 3.62, 5.37, 7.12, 8.9):
            b.beam((X0 + u, Y0 - 0.03, 0.4), (X0 + u, Y0 - 0.03, LOW + RISE - 0.05), w=0.16, h=0.1, mat="timber", col="darkoak", up=(0, 1, 0))
        b.beam((X0, Y0 - 0.03, LOW + 0.1), (X1, Y0 - 0.03, LOW + 0.1), w=0.1, h=0.18, mat="timber", col="darkoak", up=(0, 0, 1))
    with b.at(X0 + doors[1], Y0 + 0.1, 0.08 + 1.95 * 0.52):
        cow(b)
    P.exposed(bd.back, "base", n=8, col="grey")

    # ---- the yard side: trough, churns, stool and tools, a wheel that never got mended
    PK.trough(b, 2.35, Y0 - 0.4, 0.0, w=1.3, d=0.5, h=0.48)
    for i, x in enumerate((-0.55, -0.2, 0.18)):
        F.churn(b, x, Y0 - 0.34 + 0.06 * (i % 2), 0.0, s=1.0 + 0.1 * (i == 1))
    F.bucket(b, 1.5, Y0 - 0.33, 0.0)
    with b.detail(2):
        b.box(0.34, 0.3, 0.05, "planks", col="greyoak", x=-1.25, y=Y0 - 0.5, z=0.3, bottom=True)
        for (dx, dy) in ((-0.12, -0.1), (0.12, -0.1), (0.0, 0.11)):
            b.beam((-1.25 + dx * 1.3, Y0 - 0.5 + dy * 1.3, 0.0), (-1.25 + dx, Y0 - 0.5 + dy, 0.3), w=0.04, mat="planks", col="greyoak", caps=False)
    F.tool(b, 0.76, Y0 - 0.11, 0.0, kind="fork", lean=0.05)
    F.tool(b, 0.98, Y0 - 0.11, 0.0, kind="broom", lean=0.05)
    P.ivy(bd.back, 8.3, 0.3, w=1.5, h=1.7, n=6)
    F.hay(b, 3.6, Y1 + 0.22, 0.0, rx=0.5, ry=0.2, h=0.45, lod=2)
    F.tool(b, 3.0, Y1 + 0.07, 0.0, kind="rake", rz=180, lean=0.06)
    F.meadow(b, -4.3, Y1 + 0.2, 2.6, Y1 + 0.26, n=5, spread=(0.18, 0.22))
