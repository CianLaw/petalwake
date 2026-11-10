# The chandler's: rope, lamp oil and candles below, the family above, and a hoist in the gable for the stock kept in the loft.
# A rubble shop storey, then two timber-framed storeys each jettied a step further over the lane, under a steep gable to the street.
# Warm rubble, butter plaster in dark oak framing, terracotta tiles; accent red.
from kit import *
import parts as P
import parts_l as L

META = {"name": "The Chandler's Loft", "kind": "house", "lot": (5.0, 8.0), "terrace": True, "lean": (0.001, -0.003)}


def build(b):
    W, D, acc = 4.4, 7.3, "red"
    c = W / 2
    # --- the shop: rubble, with a painted shop front right across it
    g = b.body(W, D, 3.0, mat="masonry", col="warm")
    P.plinth(g, h=0.3)
    L.shopfront(g.front, 0.2, W - 0.2, h=2.55, z=0.3, col=acc, door=W - 0.86, door_w=0.9, lights=3, riser=0.4)
    P.lantern(g.front, 0.12, 2.3)
    P.door(g.back, 1.2, w=0.9, h=2.0, z=0.17, col=acc, frame="timber", steps=1)
    P.window(g.back, 3.25, 1.1, w=0.8, h=1.1, lintel="timber")
    # --- first floor: close-studded, a step out over the lane
    j1, j2 = 0.26, 0.24
    f1 = b.body(W, D + j1, 2.7, mat="plaster", col="butter", z=3.0, y=(D - j1) / 2, floor="planks")
    L.jetty(b, -c, c, 0.0, j1, 3.0)
    for u in (1.2, W - 1.2):
        P.window(f1.front, u, 0.95, w=0.95, h=1.25, lintel=None, sill=False, box=True, bars=(1, 2))
    L.timbers(f1.front, posts=[0.08 + (W - 0.16) * i / 8 for i in range(9)], rails=(0.08, 2.62))
    P.window(f1.back, c, 0.95, w=0.9, h=1.2, shutters=acc, lintel="timber")
    for wl in (f1.left, f1.right):
        L.timbers(wl, posts=[0.08 + (wl.w - 0.16) * i / 5 for i in range(6)], rails=(0.08, 2.62), frames=False)
    L.timbers(f1.back, posts=(0.08, 1.5, W - 1.5, W - 0.08), rails=(0.08, 2.62))
    L.sign(f1.front, 0.42, 1.0, emblem="candle", col="mustard", board=acc)
    # --- second floor: square panels and crosses, another step out
    f2 = b.body(W, D + j1 + j2, 2.5, mat="plaster", col="butter", z=5.7, y=(D - j1 - j2) / 2, floor="planks")
    L.jetty(b, -c, c, -j1, j2, 5.7)
    P.window(f2.front, c, 0.85, w=2.0, h=1.15, bars=(3, 1), lintel=None, sill=False, box=True)
    L.timbers(f2.front, posts=(0.08, 0.98, W - 0.98, W - 0.08), rails=(0.08, 2.42), braces=L.cross(0.16, 0.16, 0.9, 2.34) + L.cross(W - 0.9, 0.16, W - 0.16, 2.34))
    d2 = f2.left.w
    P.window(f2.left, d2 - 1.3, 0.9, w=0.6, h=0.9, lintel=None, sill=False)
    P.window(f2.right, 1.5, 0.9, w=0.6, h=0.9, lintel=None, sill=False)
    for wl in (f2.left, f2.right):
        ps = [0.08 + (d2 - 0.16) * i / 5 for i in range(6)]
        br = L.knee(ps[0] + 0.08, 0.2, ps[1] - 0.1, 2.3) + L.knee(ps[5] - 0.08, 0.2, ps[4] + 0.1, 2.3) + L.cross(ps[2] + 0.08, 1.33, ps[3] - 0.08, 2.36)
        L.timbers(wl, posts=ps, rails=(0.08, 1.25, 2.42), braces=br)
    P.window(f2.back, 1.3, 0.8, w=0.8, h=1.1, lintel=None, sill=False)
    L.timbers(f2.back, posts=(0.08, c, W - 0.08), rails=(0.08, 2.42), braces=L.knee(W - 0.16, 0.2, W - 0.9, 2.3))
    # --- the gable: a loft door under the hoist beam
    P.door(f2.front, c, w=0.9, h=1.5, z=2.5 + 0.3, col=acc, frame=None, knob=False)
    P.window(f2.back, c, 2.5 + 0.55, w=0.7, h=0.9, lintel=None, sill=False)
    rise = f2.gable(ridge="y", pitch=56, eave=0.15, verge=0.42, sag=0.1, barge=False)
    L.barge_boards(f2, rise, eave=0.15, verge=0.42)
    L.cut_gable(f2.front); L.cut_gable(f2.back)
    L.timbers(f2.front, posts=(c - 0.88, c + 0.88), rails=(2.5 + 2.05,), z0=2.5, gable=rise)
    L.timbers(f2.back, posts=(c - 0.8, c + 0.8), rails=(2.5 + 1.75,), z0=2.5, gable=rise)
    L.hoist(f2.front, c, 2.5 + 2.5, out=0.66, drop=1.5, load="crate")
    top = 5.7 + 2.5
    L.cat(b, 0, -j1 - j2 - 0.3, top + 2.5 + 0.09, rz=20, col="#e9e4d8")
    # --- roof life
    P.chimney(b, 1.2, 4.5, top + 0.5, 4.0, w=0.62, d=0.8, mat="brick", pots=2)
    P.dormer(b, -1.52, 2.6, top + 0.95, w=0.9, h=0.8, depth=1.3, face=270, col="butter", frame="ivory")
    L.gull(b, 0.05, 6.3, top + rise + 0.12, rz=200)
    # --- the lane
    P.barrel(b, -1.8, -0.45); P.crate(b, -1.2, -0.5, s=0.5, rz=12); P.crate(b, -1.25, -0.48, z=0.5, s=0.36, rz=-20)
    L.flowerpot(b, 2.05, -0.3, 0, flower="#f5c842")
    # --- the back: washing on a line held off the wall, a water butt
    for x in (-1.85, 1.85):
        b.beam((x, D, 5.35), (x, D + 0.45, 5.35), w=0.06, lod=2)
    P.laundry(b, (-1.85, D + 0.42, 5.33), (1.85, D + 0.42, 5.33), n=5, sag=0.25)
    L.downpipe(b, -1.95, D + 0.06, 0, top - 0.1, butt=True, face=180)
