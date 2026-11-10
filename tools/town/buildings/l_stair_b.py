# The cooper's, on the stair-street: the workshop is in the tall bottom storey, the house door is up the covered steps, and the new barrels season in the yard at the top.
# A rubble workshop storey under two plastered storeys with their eaves to the street and one fat dormer; a stone stair up the left-hand side, roofed over at its head; a raised yard behind with a vine arbour and a hen-house.
# Butter plaster over warm rubble, terracotta tiles; accent green.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC
import parts_m as PM

META = {"name": "The Cooper's Yard", "kind": "house", "lot": (6.0, 8.0), "terrace": True, "stair": "left", "lean": (-0.001, 0.001)}


def build(b):
    acc = "green"
    x0, x1, D = -1.3, 2.55, 5.2             # the house; the stair runs up its left flank
    W, cx = x1 - x0, (x0 + x1) / 2
    L0, H = 3.2, 5.1
    top = L0 + H
    sx0, y1 = -2.75, 7.8
    # --- the workshop storey
    g = b.body(W, D, L0, mat="masonry", col="warm", x=cx)
    P.plinth(g, h=0.3, col="grey")
    PM.half_door(g.front, 1.0, w=1.2, h=2.1, col=acc, frame="timber")
    P.window(g.front, 2.8, 1.0, w=1.3, h=1.3, bars=(2, 1), lintel="timber")
    L.sign(g.front, W - 0.2, 2.95, emblem="barrel", col="brown", board="ivory")
    # --- two plastered storeys
    up = b.body(W, D, H, mat="plaster", col="butter", x=cx, z=L0)
    P.band(g, L0 - 0.1, h=0.2, out=0.06)
    f = up.front
    for u, bx in ((1.0, False), (2.85, True)):
        P.window(f, u, 0.95, w=0.82, h=1.25, shutters=acc, box=bx)
        P.window(f, u, 2.7 + 0.75, w=0.76, h=1.05, shutters=acc, box=not bx)
    lf = up.left                             # the side over the stair
    P.door(lf, 0.72, w=0.85, h=1.95, z=0.03, col=acc, frame="timber")
    P.window(lf, 2.6, 0.95, w=0.75, h=1.15); P.window(lf, 4.25, 0.95, w=0.75, h=1.15, shutters=acc)
    P.window(lf, 1.5, 2.7 + 0.8, w=0.7, h=1.0, shutters=acc); P.window(lf, 3.75, 2.7 + 0.8, w=0.7, h=1.0)
    P.window(lf, D / 2, H + 0.6, w=0.6, h=0.85, arch=0.3)
    P.window(up.right, D / 2, H + 0.6, w=0.5, h=0.7); P.window(up.right, 3.6, 2.7 + 0.85, w=0.55, h=0.85)
    k = up.back
    P.door(k, 1.0, w=0.9, h=2.0, z=0.03, col=acc, frame="stone")
    P.window(k, 2.8, 0.95, w=0.8, h=1.2, shutters=acc)
    P.window(k, 1.0, 2.7 + 0.8, w=0.75, h=1.05, shutters=acc); P.window(k, 2.85, 2.7 + 0.8, w=0.75, h=1.05)
    rise = up.gable(ridge="x", pitch=45, eave=0.35, verge=0.2, sag=0.08)
    L.cut_gable(lf); L.cut_gable(up.right)
    P.dormer(b, cx, 0.95, top + 0.85, w=1.35, h=1.1, depth=1.55, face=0, col="butter", frame="ivory", shutters=acc)
    P.chimney(b, x1 - 0.42, D / 2, top + 1.5, 2.8, w=0.66, d=0.85, mat="brick", pots=2)
    # --- the stair up the flank, roofed over at its head
    n, run = 16, 0.26
    sw = x0 - sx0
    with b.at((sx0 + x0) / 2, 0.3, 0):
        PC.outside_stair(b, n=n, w=sw, rise=L0 / n, run=run, landing=0.95, rail="balusters", rail_sides="l")
    py0, py1, pz = 2.45, 5.3, 5.25
    with b.at(sx0 + 0.06, (py0 + py1) / 2, pz, rz=-90):
        L.pent(b, py1 - py0, sw - 0.06, 0.62, eave=0.08, verge=0.1, course=0.34)
    with b.detail(1):
        for y in (py0 + 0.12, (py0 + py1) / 2, py1 - 0.12):
            zs = min(L0, max(0.0, (y - 0.3) / run * L0 / n))
            b.beam((sx0 + 0.12, y, zs), (sx0 + 0.12, y, pz - 0.02), w=0.12)
            b.beam((sx0 + 0.12, y, pz - 0.5), (sx0 + 0.55, y, pz + 0.12), w=0.08)
        b.beam((sx0 + 0.12, py0, pz - 0.06), (sx0 + 0.12, py1, pz - 0.06), w=0.12, h=0.14)
    P.lantern(lf, 1.5, 2.2)
    # --- the raised yard behind
    yw, yc = y1 - D, (D + y1) / 2
    b.box(5.5, yw, L0, "masonry", col="warm", x=0, y=yc, cap="flagstone", capcol="sand")
    b.box(5.5, yw, 3.0, "masonry", col=shade("warm", 0.85), x=0, y=yc, z=-3.0, top=False)
    b.footprint(-2.75, D, 2.75, y1, L0)
    with b.at(0, 0, L0):
        PC.garden_wall(b, (2.75, D + 0.02), (2.75, y1), h=1.0, t=0.28, skirt=0.3)
        PC.garden_wall(b, (-2.75, y1), (-2.75, D + 0.35), h=1.0, t=0.28, skirt=0.3)
        PC.garden_wall(b, (2.75, y1), (-2.75, y1), h=1.0, t=0.28, skirt=0.3, gate=(4.1, 1.0))
        with b.at(2.75 - 4.1, y1 - 0.14, 0, rz=180):
            PC.wood_gate(b, w=1.0, h=0.95, col=acc, pickets=False)
        # the hen-house in the corner
        hx, hy = 1.75, y1 - 0.9
        hen = b.body(1.3, 1.0, 1.25, mat="planks", col="greyoak", x=hx, y=hy, z=0.35, foot=False, floor="planks")
        hen.front.opening(0.4, 0.0, 0.34, 0.42, arch=0.17, pane="paint", pane_col="#2a2622", depth=0.05)
        P.window(hen.front, 0.95, 0.45, w=0.4, h=0.4, bars=(1, 1), sill=False, lintel=None, depth=0.05)
        with b.at(hx, hy - 0.5, 1.6):
            L.pent(b, 1.3, 1.0, 0.3, mat="shingle", eave=0.15, verge=0.1, course=0.3, thick=0.06)
        L.wall_top(hen.left, [[(0.0, 1.25), (1.0, 1.25), (0.0, 1.55)]]); L.wall_top(hen.right, [[(0.0, 1.25), (1.0, 1.25), (1.0, 1.55)]])
        L.wall_top(hen.back, [[(0.0, 1.25), (1.3, 1.25), (1.3, 1.55), (0.0, 1.55)]])
        with b.detail(2):
            for sx in (-0.55, 0.55):
                for sy in (-0.4, 0.4):
                    b.beam((hx + sx, hy + sy, 0), (hx + sx, hy + sy, 0.36), w=0.08, caps=False)
            b.beam((hx - 0.25, hy - 0.52, 0.36), (hx - 0.25, hy - 1.25, 0.0), w=0.2, h=0.03, mat="planks", col="greyoak")
        PC.dove(b, hx - 0.25, hy - 1.0, 0.16, rz=20, col="#c98a4b"); PC.dove(b, hx - 0.95, hy - 0.7, 0.0, rz=-60, col="#f6f3ea")
        # the vine arbour, barrels seasoning
        L.pergola(b, 2.0, 1.6, h=2.1, x=-0.55, y=D + 1.15, vines=0.8, vine_col="#86b85c", flowers=["#7a4672", "#8a4fa0"])
        PM.table(b, -0.55, D + 1.2, 0, r=0.4, col="greyoak")
        P.barrel(b, -2.2, y1 - 0.75, r=0.3, h=0.8); P.barrel(b, -2.25, y1 - 1.45, r=0.27, h=0.72); P.barrel(b, -2.2, y1 - 0.78, z=0.8, r=0.24, h=0.6)
        L.downpipe(b, x1 - 0.3, D + 0.06, 0, H - 0.2, butt=True, face=180)
    # --- the street: the cooper's stock
    P.barrel(b, x1 - 0.42, -0.42, r=0.32, h=0.85); P.barrel(b, x1 - 1.08, -0.45, r=0.3, h=0.8); P.barrel(b, x1 - 0.75, -0.44, z=0.85, r=0.26, h=0.66)
    L.logs(b, x0 + 2.05, -0.3, 0, w=0.7, h=0.36, d=0.5, r=0.045, col="#d8c3a0")
    with b.detail(2):
        for k_, rr in ((0, 0.36), (1, 0.3)):
            with b.at(x0 + 2.1 + 0.5 * k_, -0.12 - 0.04 * k_, 0.02, rx=-72):
                b.revolve([(rr, 0.0), (rr + 0.03, 0.02), (rr, 0.05)], "metal", col="iron", seg=12)
                b.revolve([(rr, 0.05), (rr - 0.03, 0.02), (rr, 0.0)], "metal", col="iron", seg=12)
    L.cat(b, sx0 + 0.75, 0.3 + run * 5.5, L0 / n * 6, rz=10, col="#3b3632", bib="#f1ede4")
