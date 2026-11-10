# The Chandler's House: candles, lamp oil and ships' lanterns below, the chandler's family on the two jettied floors
# above and the apprentices under the roof; its lamp is the last one out on the high street.
# Massing: three storeys and an attic with the gable to the street, each upper floor jettied; a lean-to wash-house.
# Materials: a rubble ground floor, cream lime plaster in dark oak framing, terracotta tiles; blue woodwork.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Chandler's House", "kind": "house", "lot": (6.2, 9.0), "terrace": True}

A = "blue"
W, D = 5.2, 6.6
Z1, Z2, ZE = 3.1, 5.9, 8.5


def candles(b, w):
    with b.detail(2):
        for i in range(int(w / 0.2)):
            x, h = -w / 2 + 0.1 + 0.2 * i, b.r(0.12, 0.3)
            b.tube((x, 0, 0), (x, 0, h), r=0.03, mat="paint", col=b.pick(["#f2ead8", "#f2ead8", "#b5433a", "#d9a431", "#8fcfae"]), n=5, caps=True, lod=2)


def build(b):
    g = b.body(W, D, Z1, mat="masonry", col="warm")
    P.plinth(g, h=0.45)
    Q.shopfront(g.front, 1.65, 0.0, w=2.3, h=1.65, riser=0.62, col=A, lights=3, goods=candles)
    P.door(g.front, 4.2, w=0.95, h=2.1, z=0.15, col=A, frame="timber", steps=1, lamp=True)
    Q.sign(g.front, 4.9, 2.95, emblem="candle", shape="arch", col="mustard", board=A, out=0.8)
    Q.joists(g.front, Z1, out=0.3)
    P.barrel(b, 2.25, -0.42, 0, r=0.25, h=0.62)
    # --- two jettied floors in close framing
    f1 = b.body(W, D + 0.3, Z2 - Z1, mat="plaster", col="cream", z=Z1, y=(D - 0.3) / 2, floor="planks")
    f2 = b.body(W, D + 0.55, ZE - Z2, mat="plaster", col="cream", z=Z2, y=(D - 0.55) / 2, floor="planks")
    posts = [0.0, 0.9, 2.1, 3.1, 4.3, W]
    for f in (f1, f2):
        h = f.h
        P.timber_frame(f.front, posts=posts, rails=[0.0, 0.85, h], braces=[(0, 0.85, 0.9, h), (W, 0.85, 4.3, h), (2.1, 0.0, 3.1, 0.85), (3.1, 0.0, 2.1, 0.85)])
        P.timber_frame(f.back, posts=[0.0, W / 2, W], rails=[0.0, h], braces=[(0, 0, W / 2, h)])
        for wl in (f.left, f.right):
            P.timber_frame(wl, posts=[0.0, wl.w], rails=[0.0, h], braces=[])
        for u in (1.5, 3.7):
            P.window(f.front, u, 0.9, w=0.95, h=1.3, shutters=A if f is f1 else None, box=(f is f2 and u < 2) or (f is f1 and u > 2), lintel=None, bars=(1, 2))
        P.window(f.back, 1.3, 0.9, w=0.9, h=1.3, bars=(1, 2), lintel=None, shutters=A)
    Q.joists(f1.front, Z2 - Z1, out=0.25)
    P.window(f2.right, 2.6, 0.95, w=0.7, h=1.1, bars=(1, 1), lintel=None)
    P.window(f2.left, 4.4, 0.95, w=0.7, h=1.1, bars=(1, 1), lintel=None)
    f2.gable(ridge="y", pitch=52, mat="tiles", sag=0.12, eave=0.25, verge=0.22)
    Q.gable_holes(f2.front)
    Q.gable_holes(f2.back)
    P.window(f2.front, W / 2, ZE - Z2 + 0.5, w=0.75, h=1.0, bars=(1, 1), lintel=None, shutters=A)
    P.timber_frame(f2.front, z0=ZE - Z2, z1=ZE - Z2 + 3.2, posts=[], rails=[], braces=[(0.8, 2.72, 1.75, 4.05), (W - 0.8, 2.72, W - 1.75, 4.05), (1.55, 4.3, W - 1.55, 4.3)])
    P.window(f2.back, W / 2, ZE - Z2 + 0.5, w=0.6, h=0.9, bars=(1, 1), lintel=None)
    P.chimney(b, -1.7, 4.4, ZE + 0.5, 3.9, mat="brick", pots=2)
    # --- the back: wash-house lean-to, the line
    wh = b.body(2.6, 1.6, 2.2, mat="masonry", col="warm", x=-W / 2 + 1.3, y=D + 0.8)
    Q.plinth(wh, h=0.3, walls="rbl")
    P.door(wh.right, 0.8, w=0.8, h=1.8, z=0.05, col=A, frame="timber")
    P.window(wh.back, 1.3, 1.0, w=0.8, h=0.8, bars=(1, 1), lintel="timber")
    rs = Q.lean_to(b, 2.6, 1.6, pitch=27, x=-W / 2 + 1.3, y=D, z=2.2, face=180, eave=0.18, verge=0.1)
    b.tri((-W / 2, D + 1.6, 2.2), (-W / 2, D, 2.2), (-W / 2, D, 2.2 + rs), "masonry", col="warm")
    b.tri((-W / 2 + 2.6, D, 2.2), (-W / 2 + 2.6, D + 1.6, 2.2), (-W / 2 + 2.6, D, 2.2 + rs), "masonry", col="warm")
    P.door(g.back, 1.2, w=0.9, h=2.0, z=0.15, col=A, frame="timber", steps=1)
    P.laundry(b, (2.4, D + 0.04, 4.6), (0.1, D + 1.7, 2.9), n=4)
