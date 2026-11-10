# The house over Pudding Lane: the lane was there first, so the house was built across it, and the locksmith who lives there has had carts under his bedroom ever since.
# A long house with its eaves to the street; at its right-hand end an archway runs clean through from front to back, with a timber-framed room jettied and gabled over it; rubble below, plaster above.
# Sand plaster and dark oak over warm rubble, terracotta tiles; accent navy.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC
import parts_m as PM

META = {"name": "The Arch House", "kind": "house", "lot": (8.0, 7.0), "terrace": True, "arch": {"x0": 0.5, "x1": 3.5, "height": 3.6}}


def build(b):
    acc = "navy"
    x0, x1, D = -3.75, 3.75, 6.5
    W = x1 - x0
    ax0, ax1 = 0.5, 3.5                      # the lane under the house
    H0, H = 3.95, 2.75
    top = H0 + H
    th = 0.5
    aw = x1 - ax0
    # --- the ground storey: the house on the left, the archway on the right
    with b.at(ax0, 0, 0):
        fa, _ = PM.arcade(b, aw, H0, thick=th, arches=[((ax1 - ax0) / 2, ax1 - ax0, 3.6, 1.25)], mat="masonry", col="warm", top=False, ends="")
    with b.at(x1, D, 0, rz=180):
        ba, _ = PM.arcade(b, aw, H0, thick=th, arches=[(x1 - (ax0 + ax1) / 2, ax1 - ax0, 3.6, 1.25)], mat="masonry", col="warm", top=False, ends="")
    with b.at(x0, 0, 0):
        fw = b.wall(ax0 - x0, H0, "masonry", "warm")
    with b.at(ax0, D, 0, rz=180):
        bw = b.wall(ax0 - x0, H0, "masonry", "warm")
    with b.at(x0, D, 0, rz=270):
        lw = b.wall(D, H0, "masonry", "warm")
    with b.at(x1, 0, 0, rz=90):
        rw = b.wall(D, H0, "masonry", "warm")
    with b.at(ax0, th, 0, rz=90):
        pl = b.wall(D - 2 * th, H0, "masonry", "warm")          # the house's wall inside the passage
    with b.at(ax1, D - th, 0, rz=270):
        pr = b.wall(D - 2 * th, H0, "masonry", "warm")          # the pier's
    P.plinth(L.Walls(b, [fw, fa, rw, ba, bw, lw, pl, pr], front=fw), h=0.35, col="grey")
    b.footprint(x0, 0, ax0, D, top); b.footprint(ax1, 0, x1, D, top)
    L.arch_dress(fa, (ax1 - ax0) / 2, 0, ax1 - ax0, 3.6, 1.25, col="stone")
    L.arch_dress(ba, x1 - (ax0 + ax1) / 2, 0, ax1 - ax0, 3.6, 1.25, col="stone", jambs=False)
    P.door(fw, 1.2, w=0.95, h=2.1, z=0.17, col=acc, frame="stone", steps=1)
    L.shopfront(fw, 2.05, fw.w - 0.3, h=2.75, z=0.35, col=acc, lights=3, riser=0.5)
    P.sign(fw, 0.3, 3.3, emblem="key", col="mustard", board=acc)
    P.door(pl, 1.6, w=0.85, h=2.0, z=0.1, col=acc, frame="timber")
    P.window(pl, 3.6, 1.2, w=0.7, h=0.9, bars=(1, 1))
    P.lantern(pl, 0.6, 2.5)
    P.window(bw, 1.3, 1.2, w=0.9, h=1.2, shutters=acc); P.door(bw, 3.2, w=0.9, h=2.0, z=0.17, col=acc, frame="stone", steps=1)
    with b.detail(1):                        # the beams of the room over the lane
        for i in range(6):
            y = th + 0.35 + (D - 2 * th - 0.7) * i / 5
            b.beam((ax0, y, H0 - 0.11), (ax1, y, H0 - 0.11), w=0.16, h=0.2)
    L.bunting(b, (ax0 + 0.12, -0.03, 3.05), (ax1 - 0.12, -0.03, 3.05), n=9, sag=0.28)
    # --- the upper storey, right across
    up = b.body(W, D, H, mat="plaster", col="sand", z=H0, floor="planks", foot=False)
    f = up.front
    for u, bx in ((1.15, True), (3.1, False)):
        P.window(f, u, 0.85, w=0.85, h=1.25, shutters=acc, box=bx)
    L.band_on(f, -0.14, h=0.2, out=0.06, u1=ax0 - x0)
    k = up.back
    for u, bx in ((1.4, False), (3.3, True), (5.4, False), (6.6, False)):
        P.window(k, u, 0.85, w=0.8, h=1.2, shutters=acc if u > 4 or bx else None, box=bx)
    P.window(up.left, D / 2, H + 0.75, w=0.6, h=0.85, sill=False); P.window(up.right, D / 2, H + 0.75, w=0.6, h=0.85, sill=False)
    rise = up.gable(ridge="x", pitch=42, eave=0.3, verge=0.04, sag=0.1, col="#f2dccc")
    L.cut_gable(up.left); L.cut_gable(up.right)
    # --- the room over the arch: framed, jettied, gabled to the street
    bx0, bw_ = ax0 - 0.1, 3.0
    bay = b.body(bw_, 1.2, H, mat="plaster", col="sand", x=bx0 + bw_ / 2, y=0.2, z=H0, floor="planks", foot=False)
    L.jetty(b, bx0, bx0 + bw_, 0.0, 0.4, H0)
    bf = bay.front
    P.window(bf, bw_ / 2, 0.85, w=2.0, h=1.25, bars=(3, 1), lintel=None, sill=False, box=True)
    P.window(bf, bw_ / 2, H + 0.4, w=0.65, h=0.85, lintel=None, sill=False)
    rb = bw_ / 2 * math.tan(rad(50))
    b.gable_roof(bw_, 3.6, pitch=50, x=bay.x, y=1.4, z=top, ridge="y", eave=0.2, verge=0.35, barge=False, col="#f2dccc")
    bf.gable = rb - 0.03
    L.cut_gable(bf)
    L.barge_boards(bay, rb, eave=0.2, verge=0.35, ends="f")
    L.timbers(bf, posts=(0.08, 0.5, bw_ - 0.5, bw_ - 0.08), rails=(0.08, H - 0.1), braces=L.knee(0.14, 1.5, 0.46, 2.6, bulge=0.1) + L.knee(bw_ - 0.14, 1.5, bw_ - 0.46, 2.6, bulge=0.1))
    L.timbers(bf, posts=(bw_ / 2 - 0.65, bw_ / 2 + 0.65), rails=(H + 1.38,), z0=H, gable=rb)
    L.timbers(bay.left, posts=(0.72, 1.12), rails=(0.08, H - 0.1), frames=False, u0=0.7)
    # --- roof life
    P.dormer(b, -2.35, 1.2, top + 1.2 * math.tan(rad(42)) - 0.1, w=0.95, h=0.9, depth=1.4, face=0, col="sand", frame="ivory")
    P.dormer(b, -0.6, 1.2, top + 1.2 * math.tan(rad(42)) - 0.1, w=0.95, h=0.9, depth=1.4, face=0, col="sand", frame="ivory")
    P.chimney(b, x0 + 0.42, D / 2, top + 1.7, 3.0, w=0.66, d=0.9, mat="brick", pots=2)
    P.chimney(b, ax0 - 0.35, D / 2 + 1.2, top + 0.9, 3.2, w=0.7, d=0.7, mat="brick", pots=2)
    PC.vane(b, 1.4, D / 2, top + rise + 0.02, h=1.4, shape="pennon")
    # --- the street
    P.bench(b, -1.2, -0.42, w=1.3); P.barrel(b, ax0 - 0.35, -0.42, r=0.27, h=0.7)
    PC.climber(b, (ax0 - 0.1, -0.1, 0.3), (ax0 - 0.05, -0.12, 3.5), n=8, r=0.22, bloom=["#f4f1e4", "#f2a0bd"])
    L.cat(b, (ax0 + ax1) / 2 + 0.4, 1.8, 0.0, rz=160, col="#d98a3d")
    L.flowerpot(b, x0 + 0.3, -0.32, 0, flower="#f5c842")
