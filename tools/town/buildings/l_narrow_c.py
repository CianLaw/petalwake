# The carrier's house: his cart goes in through the big green doors, and the parcels for the broom post go up to the deck he built across the valley of his roof.
# Three storeys under a double roof with its eaves to the street; an oriel over the cart doors; a railed deck high among three chimney stacks, reached by a hatch from the valley.
# Cream plaster over a rubble ground storey, terracotta tiles, grey oak deck; accent green.
from kit import *
import parts as P
import parts_l as L

META = {"name": "The Carrier's Deck", "kind": "house", "lot": (5.6, 8.5), "terrace": True, "lean": (0.002, 0.002)}


def build(b):
    W, D, acc = 5.1, 7.9, "green"
    H0, H = 3.1, 5.4
    hw, ym = W / 2, D / 2
    # --- rubble ground storey with the cart doors
    g = b.body(W, D, H0, mat="masonry", col="warm")
    P.plinth(g, h=0.3)
    P.door(g.front, 1.75, w=2.3, h=2.65, arch=0.62, col=acc, frame="stone", double=True, depth=0.3)
    P.window(g.front, W - 0.95, 1.2, w=0.75, h=1.05, bars=(1, 1), lintel="stone")
    L.guard(g.front, W - 0.95, 1.2, w=0.72, h=1.0, out=0.08)
    P.lantern(g.front, 3.25, 2.25)
    P.door(g.back, 1.3, w=0.9, h=2.0, z=0.17, col=acc, frame="stone", steps=1)
    P.window(g.back, 3.6, 1.1, w=0.9, h=1.2, shutters=acc)
    # --- two plastered storeys
    up = b.body(W, D, H, mat="plaster", col="cream", z=H0)
    L.bay(up.front, 1.75, 0.42, w=1.95, h=1.95, out=0.5, col="cream", rows=((0.5, 1.1),), lights=3, base="brackets", roof="tiles", trim=acc, frame="ivory", roof_rise=0.5)
    P.window(up.front, W - 1.05, 0.95, w=0.85, h=1.25, shutters=acc, box=True)
    P.window(up.front, 1.2, 2.8 + 0.85, w=0.8, h=1.15, shutters=acc)
    P.window(up.front, W - 1.4, 2.8 + 0.85, w=0.8, h=1.15, shutters=acc, box=True)
    P.exposed(up.front, "corners", n=6)
    for (u, z, bx) in ((1.3, 0.95, False), (W - 1.3, 0.95, True), (1.3, 3.65, False), (W - 1.3, 3.65, False)):
        P.window(up.back, u, z, w=0.8, h=1.15, shutters=acc, box=bx)
    P.window(up.left, 6.0, 3.6, w=0.6, h=0.9)
    P.window(up.right, 6.2, 3.7, w=0.6, h=0.9)
    P.exposed(up.right, "corners", n=8); P.exposed(up.left, "corners", n=6)
    # --- the double roof: two ridges along the street and a lead valley between them
    top, rise, e, v = H0 + H, 2.0, 0.42, 0.05
    for (ya, yb) in ((0.0, ym), (ym, D)):
        yr = (ya + yb) / 2
        k = rise / (yr - ya)
        fr = ya - e if ya == 0.0 else ya
        bk = yb + e if yb == D else yb
        zf, zb = top - (ya - fr) * k, top - (bk - yb) * k
        L.roof_face(b, [(-hw - v, fr, zf), (hw + v, fr, zf), (hw + v, yr, top + rise), (-hw - v, yr, top + rise)], "tiles", thick=0.15, rim=(0, 1, 3) if ya == 0.0 else (1, 3))
        L.roof_face(b, [(hw + v, bk, zb), (-hw - v, bk, zb), (-hw - v, yr, top + rise), (hw + v, yr, top + rise)], "tiles", thick=0.15, rim=(0, 1, 3) if yb == D else (1, 3))
        L.ridge_roll(b, (-hw - v, yr, top + rise), (hw + v, yr, top + rise))
    with b.detail(1):
        b.box(W + 0.08, 0.34, 0.05, "metal", col="lead", x=0, y=ym, z=top + 0.03)
    for wl in (up.left, up.right):
        L.wall_top(wl, [[(0.0, H), (ym, H), (ym / 2, H + rise - 0.03)], [(ym, H), (D, H), (ym * 1.5, H + rise - 0.03)]])
    P.window(up.left, ym * 1.5, H + 0.35, w=0.5, h=0.7, sill=True)
    P.window(up.left, ym * 0.5, H + 0.35, w=0.5, h=0.7, sill=True)
    # chimneys: one in the valley on the left wall, two on the right
    P.chimney(b, -hw + 0.36, ym, top - 0.3, 4.7, w=0.68, d=0.95, mat="brick", pots=2)
    P.chimney(b, hw - 0.35, ym * 1.5, top + 1.0, 3.2, w=0.66, d=0.7, mat="brick", pots=2)
    P.chimney(b, hw - 0.33, ym * 0.5 - 0.3, top + 1.1, 2.5, w=0.6, d=0.55, mat="masonry", col="warm", pots=1)
    # --- the deck across the valley
    dz = top + rise + 0.24
    dw, dy0, dy1 = 3.0, ym * 0.5 - 0.12, ym * 1.5 + 0.12
    dx = -0.05
    L.deck(b, dw, dy1 - dy0, z=dz, x=dx, y=ym)
    with b.detail(1):
        for x in (dx - 1.3, dx + 1.3):
            b.beam((x, dy0 + 0.1, dz - 0.3), (x, dy1 - 0.1, dz - 0.3), w=0.14, h=0.2)
            b.beam((x, ym, top + 0.05), (x, ym, dz - 0.38), w=0.14)
            for sgn in (-1, 1):
                b.beam((x, ym, top + 0.9), (x, ym + sgn * 1.15, dz - 0.4), w=0.1)
    x0, x1 = dx - dw / 2 + 0.07, dx + dw / 2 - 0.07
    P.railing(b, [(dx - 0.78, dy0 + 0.07, dz), (x0, dy0 + 0.07, dz), (x0, dy1 - 0.07, dz), (x1, dy1 - 0.07, dz), (x1, dy0 + 0.07, dz), (dx + 0.78, dy0 + 0.07, dz)], h=1.0, style="balusters", col="darkoak")
    with b.at(dx, ym - 0.45, dz):
        P.landing_mark(b, 1.0)
    b.pad(dx, ym - 0.45, dz, radius=1.1, face=0, name="Carrier's deck")
    L.trapdoor(b, dx - 0.95, dy1 - 0.65, dz, w=0.7, d=0.8)
    P.dormer(b, dx - 0.95, ym + 0.55, top + 0.45, w=0.85, h=1.0, depth=1.1, face=0, col="cream", frame=acc)
    L.roof_ladder(b, (dx - 0.95, ym + 0.4, top + 0.05), (dx - 0.95, ym + 1.0, dz - 0.12), w=0.4)
    P.crate(b, dx + 1.0, dy1 - 0.55, dz, s=0.5, rz=8); P.sack(b, dx + 0.4, dy1 - 0.45, dz, r=0.26); P.crate(b, dx + 1.05, dy1 - 0.6, dz + 0.5, s=0.34, rz=-15)
    L.flowerpot(b, x0 + 0.25, dy0 + 0.3, dz, flower="#f2a0bd"); L.flowerpot(b, x1 - 0.25, dy0 + 0.3, dz, r=0.13)
    with b.at(x1 - 0.02, dy1 - 0.1, dz):      # a lamp on a post at the back corner
        b.beam((0, 0, 0), (0, 0, 2.3), w=0.08, lod=1)
        P.lantern_at(b, 0, 0, 2.05, arm=0.3)
    P.laundry(b, (-hw + 0.5, ym + 0.3, top + 3.6), (x1, dy1 - 0.1, dz + 2.2), n=3, sag=0.3)
    # --- lane and yard
    P.barrel(b, 2.2, -0.4); L.flowerpot(b, 0.35, -0.3, 0, r=0.17, tall=1.3)
    P.bench(b, 1.2, D + 0.27, rz=180, w=1.2)
    P.ivy(up.back, W / 2 + 0.2, -1.6, w=1.3, h=3.6, n=9)
    L.downpipe(b, hw - 0.3, D + 0.06, 0, top - 0.2, face=180)
