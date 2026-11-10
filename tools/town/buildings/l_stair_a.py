# The cellarman's, on the stair-street: wine goes in at the bottom through the big cellar doors, the family goes in at the top, by the back door off the yard, a full storey higher.
# A tall rubble cellar storey with two plastered storeys over it, gable to the street; a stone stair climbs the right-hand side to a little raised yard behind, walled and gated to the upper lane.
# Sky-blue plaster over warm rubble, terracotta tiles; accent mustard.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC

META = {"name": "The Cellarman's Steps", "kind": "house", "lot": (6.0, 8.0), "terrace": True, "stair": "right", "lean": (0.001, -0.002)}


def build(b):
    acc = "mustard"
    x0, x1, D = -2.65, 1.25, 5.4            # the house; the stair runs up its right flank
    W, cx = x1 - x0, (x0 + x1) / 2
    L0, H = 3.2, 5.2
    top = L0 + H
    sx1, y1 = 2.75, 7.8                    # outer edge of the stair, back of the yard
    # --- the cellar storey
    g = b.body(W, D, L0, mat="masonry", col="warm", x=cx)
    P.plinth(g, h=0.3, col="grey")
    P.door(g.front, 1.55, w=1.9, h=2.4, arch=0.6, col=acc, frame="stone", double=True, depth=0.3)
    P.window(g.front, 3.3, 1.55, w=0.6, h=0.7, bars=(1, 0), sill=False)
    L.guard(g.front, 3.3, 1.55, w=0.6, h=0.7, out=0.07)
    P.lantern(g.front, 2.78, 2.35)
    # --- two plastered storeys
    up = b.body(W, D, H, mat="plaster", col="sky", x=cx, z=L0)
    P.band(g, L0 - 0.1, h=0.2, out=0.06)
    f = up.front
    P.window(f, 1.2, 0.12, w=0.85, h=2.0, bars=(1, 3), sill=False)
    P.balcony(f, 1.2, 0.1, w=1.7, out=0.7, rail="balusters")
    P.window(f, 2.95, 0.95, w=0.8, h=1.25, shutters=acc)
    for u, bx in ((1.05, True), (2.85, False)):
        P.window(f, u, 2.75 + 0.8, w=0.78, h=1.1, shutters=acc, box=bx)
    P.window(f, W / 2, H + 0.45, w=0.6, h=0.85, arch=0.3)
    r = up.right
    P.window(r, 1.5, 0.95, w=0.8, h=1.2, shutters=acc); P.window(r, 3.9, 1.0, w=0.7, h=1.1)
    P.window(r, 2.7, 2.75 + 0.8, w=0.75, h=1.05, shutters=acc, box=True)
    k = up.back
    P.door(k, 1.15, w=0.9, h=2.0, z=0.03, col=acc, frame="stone", lamp=True)
    P.window(k, 2.95, 0.95, w=0.8, h=1.2, shutters=acc)
    P.window(k, 1.1, 2.75 + 0.8, w=0.75, h=1.05); P.window(k, 2.85, 2.75 + 0.8, w=0.75, h=1.05, shutters=acc)
    P.window(k, W / 2, H + 0.45, w=0.55, h=0.8)
    P.window(up.left, 2.2, 2.75 + 0.9, w=0.55, h=0.85)
    P.exposed(up.left, "corners", n=8)
    rise = up.gable(ridge="y", pitch=50, eave=0.15, verge=0.35, sag=0.06, barge=False, col="#e8d6cb")
    L.cut_gable(f); L.cut_gable(k)
    L.barge_boards(up, rise, eave=0.15, verge=0.35)
    P.chimney(b, x0 + 0.5, 3.5, top - 0.2, 3.6, w=0.6, d=0.8, mat="brick", pots=2)
    L.gull(b, cx, 1.3, top + rise + 0.1, rz=140)
    # --- the stair up the flank
    n = 17
    with b.at((x1 + sx1) / 2, 0.45, 0):
        PC.outside_stair(b, n=n, w=sx1 - x1, rise=L0 / n, run=0.28, landing=0.3, rail="balusters", rail_sides="r")
    for i, fc in ((3, "#e8497a"), (8, "#f5c842"), (13, "#f4f1e4")):
        L.flowerpot(b, x1 + 0.22, 0.45 + 0.28 * (i + 0.5), L0 / n * (i + 1), r=0.12, flower=fc)
    # --- the raised yard behind
    yw, yc = y1 - D, (D + y1) / 2
    b.box(5.5, yw, L0, "masonry", col="warm", x=0, y=yc, cap="flagstone", capcol="sand")
    b.box(5.5, yw, 3.0, "masonry", col=shade("warm", 0.85), x=0, y=yc, z=-3.0, top=False)
    b.footprint(-2.75, D, 2.75, y1, L0)
    with b.at(0, 0, L0):
        PC.garden_wall(b, (2.75, D + 0.35), (2.75, y1), h=1.0, t=0.28, skirt=0.3)
        PC.garden_wall(b, (-2.75, y1), (-2.75, D + 0.02), h=1.0, t=0.28, skirt=0.3)
        PC.garden_wall(b, (2.75, y1), (-2.75, y1), h=1.0, t=0.28, skirt=0.3, gate=(1.55, 1.0))
        with b.at(1.2, y1 - 0.14, 0, rz=180):
            PC.wood_gate(b, w=1.0, h=0.95, col=acc, pickets=True)
        P.tree(b, -1.6, y1 - 1.15, 0, h=3.1, crown=0.82)
        b.beam((-0.55, y1 - 0.55, 0), (-0.55, y1 - 0.55, 2.3), w=0.08, lod=1)
        P.laundry(b, (x0 + 0.35, D + 0.1, 2.25), (-0.55, y1 - 0.55, 2.25), n=4, sag=0.22)
        P.bench(b, 2.2, yc + 0.2, 0, rz=270, w=1.2)
        PC.pots(b, (-0.3, D + 0.3, 0), (-1.2, D + 0.3, 0), n=4)
        L.cat(b, 2.61, D + 1.0, 1.14, rz=250, col="#d98a3d")
        L.downpipe(b, x0 + 0.3, D + 0.06, 0, H - 0.2, butt=True, face=180)
    # --- the street: barrels by the cellar doors, the handcart
    P.barrel(b, x0 + 0.38, -0.42); P.barrel(b, x0 + 1.02, -0.45, r=0.27, h=0.72)
    L.handcart(b, 0.35, -0.72, 0, rz=90, load=("#d9c9a3", "#cdb98f"))
