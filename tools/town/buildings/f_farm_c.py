# Longgallery Farm: stone below, timber and butter-yellow plaster above, and the whole household lives on the gallery from May to October.
# Massing: a two-storey range whose roof sweeps on down over an open timber gallery along the front at first-floor height; five oak posts
#          from the ground to the eaves plate, a stone outside stair up the left gable to the gallery's end.
# Materials: warm rubble ground floor, half-timbered butter plaster above, oak posts and balusters, terracotta tiles; accent red.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_k as PK
import parts_f as F

META = {"name": "Longgallery Farm", "kind": "farm", "lot": (10.0, 8.0)}

X0, X1, Y0, Y1 = -3.7, 4.3, 1.6, 6.8       # the walls
GY = 0.45                                   # front edge of the gallery (and of the roof block)
G, U = 2.7, 2.5                             # storey heights
PITCH = 40.0


def build(b):
    w, d, cx, cy = X1 - X0, Y1 - Y0, (X0 + X1) / 2, (Y0 + Y1) / 2
    t = math.tan(rad(PITCH))
    span = Y1 - GY
    rise = span / 2 * t
    yr = GY + span / 2                      # the ridge

    # ---- ground floor
    g = b.body(w, d, G, mat="masonry", col="warm", x=cx, y=cy)
    P.plinth(g, h=0.5)
    P.door(g.front, 4.0, w=1.0, h=2.0, col="red", frame="timber", z=0.15, lamp=True)
    P.window(g.front, 1.5, 0.95, w=0.85, h=1.1, shutters="red", lintel="timber")
    P.window(g.front, 6.5, 0.95, w=0.85, h=1.1, shutters="red", lintel="timber")
    F.half_door(g.back, 2.0, w=1.0, h=1.95, z=0.15, col="red")
    P.window(g.back, 4.6, 0.95, w=0.85, h=1.1, lintel="timber")
    P.window(g.back, 6.6, 0.95, w=0.85, h=1.1, lintel="timber")
    P.window(g.right, 2.6, 0.95, w=0.85, h=1.1, lintel="timber", shutters="red")

    # ---- upper floor: timber and plaster, gables shaped to the long front slope
    up = b.body(w, d, U, mat="plaster", col="butter", x=cx, y=cy, z=G)
    zf, zr = U + (Y0 - GY) * t - 0.03, U + rise - 0.03
    PH.shape(up.right, [(0.0, zf), (yr - Y0, zr), (d, U)])
    PH.shape(up.left, [(0.0, U), (Y1 - yr, zr), (d, zf)])
    P.door(up.front, 1.1, w=0.85, h=1.9, col="red", frame="timber", z=0.04)
    P.door(up.front, 6.9, w=0.85, h=1.9, col="red", frame="timber", z=0.04)
    P.window(up.front, 3.0, 0.9, w=0.8, h=1.1, shutters="red", box=True, lintel=None)
    P.window(up.front, 5.0, 0.9, w=0.8, h=1.1, shutters="red", lintel=None)
    for u in (1.5, 4.0, 6.5):
        P.window(up.back, u, 0.9, w=0.8, h=1.1, lintel=None, shutters="red" if u != 4.0 else None)
    P.window(up.right, 2.6, 0.9, w=0.8, h=1.1, lintel=None)
    P.window(up.left, 1.2, 0.9, w=0.8, h=1.1, lintel=None)
    P.timber_frame(up.front, posts=[0.0, 0.55, 1.65, 2.5, 3.5, 4.5, 5.5, 6.35, 7.45, w], rails=[0.0, U], braces=None, z1=U)
    P.timber_frame(up.back, posts=[0.0, 0.9, 2.1, 3.4, 4.6, 5.9, 7.1, w], rails=[0.0, 0.8, U], braces=[(0.0, U, 0.9, 0.8), (w, U, 7.1, 0.8)], z1=U)
    P.timber_frame(up.right, posts=[0.0, 1.3, 2.0, 3.2, 3.9, d], rails=[0.0, 0.8, U], braces=[(0.0, U, 1.3, 0.8), (d, U, 3.9, 0.8)], z1=U)
    P.timber_frame(up.left, posts=[0.0, 0.7, 1.7, 3.0, 4.2, d], rails=[0.0, 0.8, U], braces=[(d, U, 4.2, 0.8)], z1=U)

    def gable_timbers(wl, ur, flip):
        def deco():
            with b.detail(1):
                b.beam((ur, -0.04, U), (ur, -0.04, zr - 0.25), w=0.15, h=0.1, mat="timber", col="darkoak", up=(0, 1, 0), caps=False)
                u0, u1 = (0.0, d - 0.95 / t) if not flip else (0.95 / t, d)
                b.beam((u0, -0.045, U + 0.9), (u1, -0.045, U + 0.9), w=0.1, h=0.14, mat="timber", col="darkoak", up=(0, 0, 1), caps=False)
        wl.add(deco)

    gable_timbers(up.right, yr - Y0, False)
    gable_timbers(up.left, Y1 - yr, True)

    # ---- the roof, sweeping on over the gallery
    b.gable_roof(w, span, PITCH, mat="tiles", x=cx, y=yr, z=G + U, ridge="x", eave=0.34, verge=0.35, sag=0.1)
    PC.stack(b, 2.8, 5.35, G + U + 0.75, 2.9, w=0.8, d=0.6, mat="masonry", col="warm", flues=2)
    for xe, sgn in ((X0, -1), (X1, 1)):                     # boarded spandrels closing the roof's ends over the gallery
        q = [(xe, GY + 0.05, G + U), (xe, Y0, G + U), (xe, Y0, G + zf)]
        b.face(q if sgn < 0 else list(reversed(q)), "planks", col="darkoak")
        b.face(list(reversed(q)) if sgn < 0 else q, "planks", col="darkoak")

    # ---- the gallery: deck, posts from the ground to the plate, balustrade, washing
    F.deck(b, w, Y0 - GY, x=cx, y=(Y0 + GY) / 2, z=G, thick=0.1, joists=1.0)
    posts = [X0 + 0.1, -1.65, 0.3, 2.25, X1 - 0.1]
    for x in posts:
        b.beam((x, GY + 0.1, -2.0), (x, GY + 0.1, G + U), w=0.18, mat="timber", col="darkoak", lod=0)
        with b.detail(1):
            for sx in (-1, 1):
                if X0 < x + sx * 0.6 < X1:
                    b.beam((x, GY + 0.1, G + U - 0.7), (x + sx * 0.6, GY + 0.1, G + U - 0.12), w=0.1, mat="timber", col="darkoak", caps=False)
    b.beam((X0, GY + 0.1, G + U - 0.08), (X1, GY + 0.1, G + U - 0.08), w=0.18, h=0.2, mat="timber", col="darkoak", lod=0, up=(0, 0, 1))
    for xa, xb in zip(posts, posts[1:]):
        P.railing(b, [(xa, GY + 0.1, G), (xb, GY + 0.1, G)], h=0.95, style="balusters", posts_at=3.0)
    P.railing(b, [(X1 - 0.1, GY + 0.1, G), (X1 - 0.1, Y0 - 0.05, G)], h=0.95, style="balusters", posts_at=3.0)
    P.laundry(b, (-1.55, GY + 0.22, G + U - 0.45), (2.15, GY + 0.22, G + U - 0.5), n=5, sag=0.3)
    P.bench(b, 2.9, Y0 - 0.3, G, w=1.3)
    P.planter(b, -0.9, Y0 - 0.25, G, w=0.9)
    PC.climber(b, (X1 - 0.1, GY + 0.02, 0.1), (X1 - 0.1, GY + 0.02, G + 0.9), bloom=["#e8497a", "#f2a0bd"])

    # ---- the stone stair up the left gable to the gallery's end
    with b.at(X0 - 0.55, 5.4, 0.0, rz=180):
        PC.outside_stair(b, n=14, w=1.0, rise=G / 14, run=0.27, landing=1.1, rail="balusters", rail_sides="r")

    # ---- under the gallery and round the back
    PK.firewood(b, 2.6, Y0 - 0.03, 0.0, w=2.0, h=1.15, d=0.42)
    P.bench(b, -1.6, Y0 - 0.3, 0.0, w=1.4)
    P.barrel(b, -2.9, Y0 - 0.4, 0.0, r=0.3, h=0.85)
    F.tool(b, -2.45, Y0 - 0.12, 0.0, kind="fork", lean=0.08)
    F.veg_row(b, (-1.8, 7.35), (1.4, 7.35), "cabbage")
    F.veg_row(b, (2.0, 7.4), (4.0, 7.4), "leek")
    for x in (-3.1, -2.6, 4.2):
        F.sunflower(b, x, 7.45, 0.0, h=b.r(1.4, 1.8), face=180)
    F.meadow(b, -3.3, 7.6, 4.2, 7.72, n=4, spread=(0.2, 0.28))
