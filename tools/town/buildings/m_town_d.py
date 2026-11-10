# The Flower House: Widow Marrow sells cut flowers, seed and gossip from the ground floor; the balcony above is so
# full of pots that the postman waters them in passing.
# Massing: three storeys under a tiled mansard with two dormers; a flat front with a first-floor balcony on stone
# corbels; an outside stair up the back to the upper lodging.
# Materials: sage-green lime plaster on a stone base, terracotta tiles, a brick stack, iron rails; mustard woodwork.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Flower House", "kind": "house", "lot": (6.0, 9.0), "terrace": True}

A = "mustard"
W, D = 5.2, 6.6
Z1, Z2, ZE = 3.2, 6.0, 8.4
SEC = [(0.0, 0.0), (0.8, 2.0), (D / 2, 3.2)]


def blooms(b, w):
    Q.display(b, w, "fruit", cols=P.FLOWERS, depth=0.1)


def bucket(b, x, y, col):
    with b.at(x, y, 0):
        with b.detail(2):
            b.revolve([(0.13, 0.0), (0.17, 0.3)], "metal", col="lead", seg=7)
            b.blob(0.17, 0.17, 0.14, mat="ivy", col="#7db45e", z=0.36, seg=6, rings=2, wind=0.3, rough=0.3)
            for k in range(4):
                b.blob(0.07, 0.07, 0.06, mat="paint", col=col, x=b.r(-0.1, 0.1), y=b.r(-0.1, 0.1), z=0.47 + b.r(0, 0.06), seg=5, rings=2, wind=0.5)


def build(b):
    g = b.body(W, D, Z1, mat="plaster", col="sage")
    P.plinth(g, h=0.55)
    Q.shopfront(g.front, 1.7, 0.0, w=2.4, h=1.7, riser=0.62, col=A, lights=3, goods=blooms)
    P.door(g.front, 4.25, w=0.95, h=2.15, z=0.15, col=A, frame="timber", steps=1, lamp=True)
    Q.sign(g.front, 4.9, 3.05, emblem="flower", shape="round", col="pink", out=0.8)
    P.exposed(g.front, "corners", n=6)
    # --- first floor: the balcony and its pots
    f1 = b.body(W, D, Z2 - Z1, mat="plaster", col="sage", z=Z1)
    P.band(f1, 0.0, h=0.18, out=0.06)
    P.door(f1.front, W / 2, w=1.0, h=2.05, z=0.1, col=A, frame="timber", knob=False)
    P.balcony(f1.front, W / 2, 0.1, w=2.6, out=0.85, rail="iron", floor="ashlar", floor_col="stone", brackets=False, thick=0.13)

    def corbels():
        for sgn in (-1, 1):
            with f1.front.on(W / 2 + sgn * 0.95, -0.03):
                Q.corbel(b, 0.24, 0.7, 0.6)
        for sgn in (-1, 1):
            with f1.front.on(W / 2 + sgn * 0.95, 0.1):
                P.planter(b, 0, -0.62, 0, w=0.6, d=0.22, h=0.2)

    f1.front.add(corbels)
    for u in (0.85, W - 0.85):
        P.window(f1.front, u, 0.95, w=0.75, h=1.3, shutters=A, bars=(1, 2))
    P.window(f1.back, 1.3, 0.95, w=0.9, h=1.3, bars=(1, 2))
    # --- second floor and the mansard
    f2 = b.body(W, D, ZE - Z2, mat="plaster", col="sage", z=Z2)
    P.band(f2, 0.0, h=0.16, out=0.05)
    for i, u in enumerate((0.95, W / 2, W - 0.95)):
        P.window(f2.front, u, 0.8, w=0.8, h=1.15, bars=(1, 2), box=(i == 1), shutters=A if i != 1 else None)
    for u in (1.3, W - 1.3):
        P.window(f2.back, u, 0.8, w=0.85, h=1.15, bars=(1, 2), shutters=A)
    P.window(f2.right, 2.2, 0.85, w=0.7, h=1.1, bars=(1, 1))
    P.window(f2.left, 4.4, 0.85, w=0.7, h=1.1, bars=(1, 1))
    f2.gable(ridge="x", mat="tiles", section=SEC, sag=0.1, eave=0.32, verge=0.1)
    zd = ZE + 0.35 * 2.0 / 0.8
    for x in (-1.3, 1.3):
        P.dormer(b, x, 0.35, zd, w=1.05, h=1.05, depth=1.3, col="sage", frame="ivory")
    P.dormer(b, 0.4, D - 0.35, zd, w=1.05, h=1.05, depth=1.3, face=180, col="sage")
    P.chimney(b, 2.0, D / 2 + 0.4, ZE + 2.5, 2.9, mat="brick", pots=2)
    # --- the back: an outside stair to the lodging door
    P.door(f1.back, W - 1.0, w=0.85, h=1.95, z=0.05, col=A, frame="timber")
    lx = -W / 2 + 1.0
    with b.detail(1):
        b.box(1.1, 1.0, 0.1, "planks", col="greyoak", x=lx, y=D + 0.5, z=Z1 - 0.05, bottom=True)
        for dx in (-0.48, 0.48):
            b.beam((lx + dx, D + 0.93, 0), (lx + dx, D + 0.93, Z1 + 1.0), w=0.12, mat="timber", col="darkoak")
    P.railing(b, [(lx - 0.5, D + 0.05, Z1 + 0.05), (lx - 0.5, D + 0.95, Z1 + 0.05), (lx + 0.5, D + 0.95, Z1 + 0.05)], h=0.9, style="balusters")
    with b.at(lx + 0.55 + 14 * 0.25, D + 0.5, 0, rz=90):
        P.stairs(b, w=0.85, rise=(Z1 + 0.05) / 14, run=0.25, n=14, solid=False, rail="balusters")
    P.door(g.back, 1.4, w=0.9, h=2.0, z=0.15, col=A, frame="timber", steps=1)
    # --- the pavement: buckets and troughs of flowers
    for i, (x, y) in enumerate(((-2.35, -0.4), (-1.95, -0.75), (-1.5, -0.42), (0.55, -0.4), (0.95, -0.72))):
        bucket(b, x, y, P.FLOWERS[(i * 3) % len(P.FLOWERS)])
    P.planter(b, -0.4, -0.3, 0, w=1.0)
    P.planter(b, 2.4, -0.3, 0, w=0.5, d=0.42, h=0.4, bush=True)
