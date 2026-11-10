# The Last & Awl: the cobbler's is the smallest shop on the square and the oldest; he works at the half-door so as
# not to miss anything, and the big red boot has hung over it longer than anyone remembers.
# Massing: a storey and a half; a stone ground floor, an oak-framed knee wall, a steep shingle roof that runs down
# at the back in a catslide over the workshop, one cat-sized dormer and a chimney that leans.
# Materials: warm rubble, sand plaster in dark oak, silvered shingles; red door, shutters and boot.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Last & Awl, cobbler", "kind": "shop", "lot": (5.5, 7.0), "lean": (-0.004, 0.003)}

A = "red"
W, D, DB = 4.6, 3.9, 2.2      # width, depth of the house, depth of the catslide workshop behind
ZG, ZK = 2.5, 3.4


def boot(b, s=1.0, col=A):
    """A boot, toe toward local -y, hanging point at the origin (top of the leg)."""
    with b.at(s=s):
        b.box(0.2, 0.24, 0.42, "paint", col=col, y=0.05, z=-0.42, bottom=True)
        b.box(0.2, 0.5, 0.17, "paint", col=col, y=-0.08, z=-0.59, bottom=True, ty=0.85)
        b.box(0.22, 0.54, 0.04, "paint", col=shade(col, 0.5), y=-0.08, z=-0.63, bottom=True)
        b.box(0.22, 0.14, 0.06, "paint", col=shade(col, 0.5), y=0.11, z=-0.69, bottom=True)
        b.box(0.22, 0.26, 0.05, "paint", col=shade(col, 1.25), y=0.05, z=-0.02, bottom=True)


def boots_on_show(b, w):
    for i in range(3):
        with b.at(-w / 2 + w * (i + 0.5) / 3, 0.0, 0.2, rz=90):
            with b.detail(2):
                boot(b, s=0.3, col=("brown", "black", A)[i])


def build(b):
    g = b.body(W, D + DB, ZG, mat="masonry", col="warm")
    P.plinth(g, h=0.4)
    # --- the half-door, the little shop window, the boot
    Q.half_door(g.front, 3.45, w=0.95, h=1.95, z=0.1, col=A, frame="timber")
    Q.shopfront(g.front, 1.45, 0.0, w=1.6, h=1.15, riser=0.8, col=A, lights=2, transom=0.0, fascia=0.0, goods=boots_on_show)
    P.lantern(g.front, 4.25, 1.95)

    def hang():
        with g.front.on(2.5, 2.42):
            with b.detail(1):
                b.beam((0, 0.0, 0.0), (0, -0.95, 0.0), w=0.035, mat="metal", col="iron", caps=False)
                b.beam((0, 0.0, -0.45), (0, -0.6, -0.03), w=0.028, mat="metal", col="iron", caps=False)
                b.beam((0, -0.78, 0.0), (0, -0.78, -0.16), w=0.02, mat="metal", col="iron", caps=False)
                with b.at(0, -0.78, -0.16, rz=90):
                    boot(b, s=1.0)

    g.front.add(hang)
    P.stones(g.front, n=6, z0=0.4, u0=2.3, u1=3.0)
    P.window(g.right, 1.5, 1.1, w=0.7, h=1.0, bars=(1, 1))
    # --- the knee wall and the roof: steep in front, a catslide behind
    k = b.body(W, D, ZK - ZG, mat="plaster", col="sand", z=ZG, y=D / 2)
    for wl in (k.front, k.back):
        P.timber_frame(wl, rails=[0.0, ZK - ZG], braces=[])
    P.window(k.front, 1.3, 0.12, w=0.7, h=0.62, shutters=A, lintel=None, sill=False, bars=(1, 0))
    k.gable(ridge="x", pitch=51, mat="shingle", sag=0.12, eave=0.32, verge=0.14)
    for wl in (k.left, k.right):
        Q.gable_holes(wl)
        P.timber_frame(wl, rails=[0.0, ZK - ZG], braces=[])
    P.window(k.right, D / 2, ZK - ZG + 0.35, w=0.65, h=0.9, bars=(1, 1), lintel="timber")
    P.window(k.left, D / 2, ZK - ZG + 0.35, w=0.65, h=0.9, bars=(1, 1), lintel="timber")
    P.dormer(b, 0.9, 0.55, ZK + 0.55 * math.tan(rad(51)), w=0.85, h=0.75, depth=1.0, col="sand", roof="shingle", shutters=A)
    rs = Q.lean_to(b, W, DB, pitch=24, x=0, y=D, z=ZG, face=180, mat="shingle", eave=0.3, verge=0.14, sag=0.08)
    for sx in (-1, 1):
        pts = [(sx * W / 2, D, ZG), (sx * W / 2, D + DB, ZG), (sx * W / 2, D, ZG + rs)]
        b.face(pts if sx > 0 else [pts[1], pts[0], pts[2]], "masonry", col="warm")
    P.door(g.back, 1.2, w=0.85, h=1.85, z=0.1, col=A, frame="timber")
    P.window(g.back, 3.2, 1.0, w=1.1, h=0.85, bars=(2, 1), lintel="timber")
    # --- the chimney that leans
    with b.at(-1.55, 2.75, 3.6, ry=-4, rx=3):
        Q.stack(b, 0, 0, 0, 3.6, w=0.6, d=0.6, pots=1, band=False)
    # --- the street: the bench, a pair of boots, a barrel
    P.bench(b, -0.95, -0.42, 0, w=1.4)
    with b.at(-0.6, -0.5, 0.48):
        with b.detail(2):
            for dx in (-0.14, 0.12):
                with b.at(dx, 0, 0.21, rz=180 + dx * 80):
                    boot(b, s=0.3, col="brown")
    P.barrel(b, 2.0, -0.45, 0, r=0.27, h=0.7)
    Q.cat(b, -1.4, -0.42, 0.48, rz=-25, col="#c98b4a")
