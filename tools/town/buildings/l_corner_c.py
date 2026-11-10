# The tailor's at the sign of the shears: the little turret on the corner was the fitting room, so that a customer could be seen in his new coat from both streets.
# Corner house, streets to the front and the left: a rubble shop storey; two timber-framed storeys with a gabled bay jettied over the shop; the long gable of the main roof to the side street; a round stone turret corbelled out of the corner, capped with a slate candle-snuffer.
# Cream plaster in dark oak, warm rubble and pale stone, terracotta tiles and slate; accent mustard.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC

META = {"name": "The Shears", "kind": "shop", "lot": (7.5, 8.0), "terrace": True, "fronts": ["front", "left"]}


def build(b):
    acc = "mustard"
    x0, x1, D = -3.0, 3.25, 7.5            # the side street runs down the left
    W, cx = x1 - x0, (x0 + x1) / 2
    H0, H = 3.2, 5.3
    top = H0 + H
    F1 = 2.72                               # the upper floor line, above H0
    # --- the shop storey
    g = b.body(W, D, H0, mat="masonry", col="warm", x=cx)
    P.plinth(g, h=0.3)
    L.shopfront(g.front, 3.2, 6.1, h=2.75, z=0.3, col=acc, door=5.45, door_w=0.9, lights=3, riser=0.45)
    P.door(g.front, 2.35, w=0.9, h=2.05, z=0.17, col=acc, frame="stone", steps=1)
    P.window(g.front, 1.05, 1.0, w=0.75, h=1.1, bars=(1, 1))
    for u in (1.5, 4.0):
        P.window(g.left, u, 1.1, w=0.9, h=1.25, shutters=acc)
    P.door(g.left, 5.75, w=0.85, h=2.0, z=0.17, col=acc, frame="timber", steps=1)
    # --- two framed storeys
    up = b.body(W, D, H, mat="plaster", col="cream", x=cx, z=H0)
    f = up.front
    for z, hh in ((0.9, 1.25), (F1 + 0.8, 1.05)):
        P.window(f, 2.3, z, w=0.8, h=hh, lintel=None, sill=False, box=(z < 2))
    L.timbers(f, posts=(1.62, 3.0), rails=(0.08, F1, H - 0.1), braces=L.knee(1.7, F1 - 0.75, 2.9, F1 - 0.08, bulge=0.1), u0=1.55, u1=3.05)
    lf = up.left
    for u in (1.4, 3.6, 5.5):
        P.window(lf, u, 0.9, w=0.85, h=1.25, lintel=None, sill=False, box=(u > 3 and u < 5))
        P.window(lf, u, F1 + 0.8, w=0.8, h=1.05, lintel=None, sill=False)
    for u in (2.9, 4.6):
        P.window(lf, u, H + 0.55, w=0.7, h=0.95, lintel=None, sill=False)
    P.window(up.right, D / 2, H + 0.7, w=0.6, h=0.85)
    P.window(up.back, 1.6, F1 + 0.9, w=0.6, h=0.9); P.window(up.back, 4.4, F1 + 0.9, w=0.6, h=0.9)
    rise = up.gable(ridge="x", pitch=40, eave=0.3, verge=0.3, sag=0.08)
    L.cut_gable(lf); L.cut_gable(up.right)
    ps = [0.08, 0.72, 2.5, 4.55, 6.2, D - 0.08]
    br = L.knee(0.16, 0.2, 0.66, F1 - 0.1) + L.knee(0.16, F1 + 0.15, 0.66, H - 0.2) + L.cross(2.58, F1 + 0.15, 2.95, H - 0.2) + L.cross(4.1, F1 + 0.15, 4.47, H - 0.2)
    L.timbers(lf, posts=ps, rails=(0.08, F1, H - 0.1), braces=br)
    L.timbers(lf, posts=(2.0, D / 2, D - 2.0), rails=(H + 1.75,), z0=H, gable=rise)
    # --- the gabled bay, jettied over the shop
    bw_, bx0 = 2.95, 0.05
    bay = b.body(bw_, 1.2, H, mat="plaster", col="cream", x=bx0 + bw_ / 2, y=0.15, z=H0, floor="planks", foot=False)
    L.jetty(b, bx0, bx0 + bw_, 0.0, 0.45, H0)
    bf = bay.front
    P.window(bf, bw_ / 2, 0.9, w=2.1, h=1.25, bars=(3, 1), lintel=None, sill=False, box=True)
    P.window(bf, bw_ / 2, F1 + 0.8, w=1.7, h=1.05, bars=(2, 1), lintel=None, sill=False)
    P.window(bf, bw_ / 2, H + 0.35, w=0.6, h=0.8, lintel=None, sill=False)
    rb = bw_ / 2 * math.tan(rad(50))
    b.gable_roof(bw_, 3.7, pitch=50, x=bay.x, y=1.4, z=top, ridge="y", eave=0.2, verge=0.35, barge=False)
    bf.gable = rb - 0.03
    L.cut_gable(bf)
    L.barge_boards(bay, rb, eave=0.2, verge=0.35, ends="f")
    L.timbers(bf, posts=(0.08, bw_ - 0.08), rails=(0.08, F1, H - 0.1), braces=L.cross(0.14, F1 + 0.12, 0.6, H - 0.18) + L.cross(bw_ - 0.6, F1 + 0.12, bw_ - 0.14, H - 0.18))
    L.timbers(bf, posts=(bw_ / 2 - 0.62, bw_ / 2 + 0.62), rails=(H + 1.3,), z0=H, gable=rb)
    L.sign(bf, 0.1, 0.55, emblem="scissors", col="black", board=acc, round_board=True)
    # --- the corner turret
    tx, ty, tr, th = -2.42, 0.45, 1.05, 6.5
    with b.at(tx, ty, 0):
        b.revolve([(0.1, 1.8), (0.26, 2.05), (0.5, 2.5), (0.92, 2.98), (tr + 0.06, 3.1), (tr + 0.06, H0)], "ashlar", col="stone", seg=16)
    t = b.round(tr, th, mat="ashlar", col="warm", x=tx, y=ty, z=H0, seg=16, foot=False)
    for a in (270, 315, 0):
        P.window(t, a, 0.95, w=0.5, h=1.2, arch=0.25, bars=(0, 1), sill=(a != 270))
    for a in (302, 346):
        P.window(t, a, F1 + 0.85, w=0.5, h=1.05, arch=0.25, bars=(0, 1), sill=False)
    for a in (250, 315, 20):
        P.window(t, a, H + 0.25, w=0.42, h=0.7, arch=0.21, bars=(0, 0), sill=False)
    with b.detail(1):
        P.ring_band(b, tr, H0 + F1 - 0.08, h=0.16, out=0.06, x=tx, y=ty, seg=16)
        P.ring_band(b, tr, H0 + th - 0.2, h=0.2, out=0.07, x=tx, y=ty, seg=16)
    b.cone_roof(tr, 3.6, mat="slate", x=tx, y=ty, z=H0 + th, seg=16, eave=0.08, flare=0.5, course=0.45)
    # --- roof life
    P.chimney(b, x1 - 0.42, D / 2, top + 1.9, 3.1, w=0.66, d=0.9, mat="brick", pots=2)
    P.chimney(b, cx - 0.6, D - 1.3, top + 0.6, 2.9, w=0.6, d=0.6, mat="brick", pots=1)
    L.gull(b, cx + 1.2, D / 2, top + rise + 0.08, rz=120)
    # --- the pavement
    P.bench(b, -0.9, -0.42, w=1.2); L.cat(b, -0.6, -0.42, 0.48, rz=-10, col="#2f2b29")
    P.barrel(b, 3.0, -0.4, r=0.26, h=0.65); L.flowerpot(b, 0.25, -0.3, 0, flower="#f5c842"); L.flowerpot(b, x0 - 0.22, 3.0, 0, r=0.14, flower="#e8497a")
