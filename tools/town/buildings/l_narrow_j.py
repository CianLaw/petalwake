# The midwife's: you go up to her door, so that her patients' husbands can pace the landing; the cellar underneath is let to a wine merchant.
# A house on a tall basement: a flight of steps runs up along the front to a railed landing and the door, with the cellar hatch under it. Three storeys over that, a hipped roof and one fat dormer gable breaking the eaves.
# Rose plaster on a rubble basement, terracotta tiles; accent pink, ivory frames.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC

META = {"name": "The Pink House", "kind": "house", "lot": (4.8, 7.5), "terrace": True, "lean": (-0.001, -0.002)}


def build(b):
    W, D, acc = 4.2, 6.5, "pink"
    HB, H = 1.5, 9.3
    c = W / 2
    cel = b.body(W, D, HB, mat="masonry", col="warm")
    P.plinth(cel, h=0.25, out=0.08)
    up = b.body(W, D, H - HB, mat="plaster", col="rose", z=HB)
    P.band(cel, HB - 0.1, h=0.18, out=0.06)
    f = up.front
    Ht = H - HB
    # --- the front: door on the landing, tall windows, a dormer gable breaking the eaves
    du = 3.15
    P.door(f, du, w=0.95, h=2.1, z=0.03, col=acc, frame="stone", lamp=True)
    L.hood(f, du, 2.68, w=1.5, out=0.7, kind="gable", mat="tiles", rise=0.36)
    P.window(f, 1.1, 0.8, w=0.9, h=1.5, shutters=acc, bars=(1, 2))
    for u, bx in ((1.1, True), (3.1, False)):
        P.window(f, u, 2.7 + 0.9, w=0.8, h=1.2, shutters=acc, box=bx)
        P.window(f, u, 5.3 + 0.78, w=0.75, h=1.0, shutters=acc, box=not bx)
    gw, g1, g2 = 2.3, 0.75, 1.15
    L.wall_top(f, [[(c - gw / 2, Ht), (c + gw / 2, Ht), (c + gw / 2, Ht + g1), (c, Ht + g1 + g2 - 0.03), (c - gw / 2, Ht + g1)]])
    P.window(f, c, Ht + 0.12, w=0.8, h=1.1, arch=0.32, bars=(1, 1))
    L.band_on(f, Ht - 0.22, h=0.18, out=0.08, u1=c - gw / 2); L.band_on(f, Ht - 0.22, h=0.18, out=0.08, u0=c + gw / 2)
    P.window(cel.front, 3.3, 0.5, w=0.7, h=0.55, bars=(2, 0), sill=False)
    # --- the steps up along the front, and the cellar hatch under the landing
    lx0, lx1 = 0.35, 1.9
    n, run = 8, 0.28
    with b.at(lx0 - n * run, -0.54, 0, rz=-90):
        PC.outside_stair(b, n=n, w=1.04, rise=HB / n, run=run, landing=lx1 - lx0, rail="iron", rail_sides="r")
    P.railing(b, [(lx1 - 0.06, -1.0, HB), (lx1 - 0.06, -0.06, HB)], h=0.95, style="iron")
    with b.at(lx0, -1.085, 0):
        fw = b.wall(lx1 - lx0, HB - 0.08, mat="masonry", col="warm", depth=0.02)
        P.door(fw, (lx1 - lx0) / 2, w=0.9, h=1.2, arch=0.4, col=acc, frame="stone", depth=0.022, knob=False)
    L.flowerpot(b, lx0 - 0.5 * run, -0.9, HB - HB / n, r=0.12, flower="#f2a0bd")
    L.flowerpot(b, lx0 - 3.5 * run, -0.9, HB - 4 * HB / n, r=0.12, flower="#f4f1e4")
    L.flowerpot(b, lx0 - 6.5 * run, -0.9, HB - 7 * HB / n, r=0.12, flower="#e8497a")
    L.cat(b, lx0 + 0.3, -0.75, HB + 0.03, rz=-40, col="#f1ede4")
    # --- sides above the neighbours, and the back
    P.window(up.left, 2.0, 5.3 + 0.8, w=0.6, h=0.9); P.window(up.right, 4.3, 5.3 + 0.8, w=0.6, h=0.9)
    P.exposed(up.left, "corners", n=6)
    P.door(cel.back, 1.1, w=0.9, h=1.36, col=acc, frame="timber")
    P.window(cel.back, 3.1, 0.55, w=0.7, h=0.6, sill=False)
    for z, sh in ((0.85, acc), (2.7 + 0.9, None), (5.3 + 0.8, acc)):
        P.window(up.back, 1.15, z, w=0.8, h=1.15, shutters=sh); P.window(up.back, W - 1.15, z, w=0.8, h=1.15, shutters=None if sh else acc)
    # --- the roof: hipped, open at the front for the dormer gable
    R, ridge = L.hip_roof(b, W, D, pitch=48, x=0, y=D / 2, z=H, eave=0.15, gap=(-gw / 2, gw / 2, 0.62))
    b.gable_roof(gw, 2.3, pitch=45, x=0, y=1.15, z=H + g1, ridge="y", eave=0.12, verge=0.28, course=0.34)
    y1 = g1 / math.tan(rad(48))
    for sx in (-1, 1):
        ck = [(sx * gw / 2, 0.0, H), (sx * gw / 2, y1, H + g1), (sx * gw / 2, 0.0, H + g1)]
        b.face(ck if sx > 0 else list(reversed(ck)), "plaster", col="rose")
    L.ball(b, ridge[0][0], ridge[0][1], ridge[0][2] + 0.08, r=0.13, mat="metal", col="lead")
    P.weathervane(b, ridge[1][0], ridge[1][1], ridge[1][2] + 0.05, h=1.2)
    P.chimney(b, c - 0.52, D / 2 + 0.7, H + 0.2, 3.5, w=0.6, d=0.75, mat="brick", pots=2)
    L.downpipe(b, -c + 0.3, D + 0.06, 0, H - 0.2, butt=True, face=180)
