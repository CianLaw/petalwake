# The Hatter's: twin gables, twin of nothing else in the street. Mistress Felt blocks hats in the window so the whole
# town can watch, and every one of the close-set timbers upstairs is said to be a ship's rib.
# Massing: three storeys, the upper two jettied and close-studded, an oriel over the shop, two steep gables side by
# side to the street with a valley between them and one stout chimney rising out of it.
# Materials: rubble ground floor, white lime plaster in black oak, terracotta tiles; red woodwork.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Hatter's", "kind": "house", "lot": (6.8, 9.0), "terrace": True}

A = "red"
W, D = 5.9, 7.0
Z1, Z2, ZE = 3.0, 5.8, 8.3
HATS = ["#2c2a2a", "#7a4672", "#b5433a", "#2f4470", "#d9c9a3", "#3f8f5f"]


def hats(b, w):
    with b.detail(2):
        for i in range(int(w / 0.34)):
            with b.at(-w / 2 + 0.17 + 0.34 * i, 0, 0):
                b.tube((0, 0, 0), (0, 0, 0.16), r=0.015, mat="planks", col="darkoak", n=4, lod=2)
                b.revolve([(0.12, 0.16), (0.125, 0.17), (0.065, 0.18), (0.06, 0.27), (0.0, 0.28)], "cloth", col=b.pick(HATS), seg=7)


def build(b):
    g = b.body(W, D, Z1, mat="masonry", col="warm")
    P.plinth(g, h=0.45)
    Q.shopfront(g.front, 1.9, 0.0, w=2.7, h=1.6, riser=0.62, col=A, lights=3, goods=hats)
    P.door(g.front, 4.85, w=0.95, h=2.1, z=0.15, col=A, frame="timber", steps=1, lamp=True)
    Q.sign(g.front, 3.85, 2.9, emblem="hat", shape="round", col="black", out=0.85)
    Q.joists(g.front, Z1, out=0.3)
    P.bench(b, -1.0, -0.45, 0, w=1.3)
    P.stones(g.front, n=5, z0=0.5, u0=3.4)
    # --- first floor: close studding and the oriel
    f1 = b.body(W, D + 0.3, Z2 - Z1, mat="plaster", col="white", z=Z1, y=(D - 0.3) / 2, floor="planks")
    h1 = Z2 - Z1
    studs = [0.0, 0.42, 1.18, 1.5, W - 1.5, W - 1.18, W - 0.42, W]
    P.timber_frame(f1.front, posts=studs, rails=[0.0, h1], braces=[], w=0.13, col="blackoak")
    P.timber_frame(f1.back, posts=[0.0, W / 2, W], rails=[0.0, h1], braces=[(0, 0, W / 2, h1), (W, 0, W / 2, h1)], col="blackoak")
    Q.bay(f1.front, W / 2, 0.45, w=2.3, h=1.5, out=0.45, cant=0.3, apron=0.4, col="ivory", apron_col=A, panes=(3, 2), side_panes=(1, 2), base="brackets", roof=None,
          head=0.25)
    for u in (0.8, W - 0.8):
        P.window(f1.front, u, 0.9, w=0.6, h=1.25, bars=(1, 2), lintel=None)
    for u in (1.4, W - 1.4):
        P.window(f1.back, u, 0.9, w=0.9, h=1.3, bars=(1, 2), lintel=None, shutters=A)
    Q.joists(f1.front, h1, out=0.25)
    # --- second floor and the roofs: two bays, each with its own gable
    y2 = (D - 0.55) / 2
    for sx in (-1, 1):
        f2 = b.body(W / 2, D + 0.55, ZE - Z2, mat="plaster", col="white", x=sx * W / 4, z=Z2, y=y2, floor="planks")
        h2 = ZE - Z2
        P.timber_frame(f2.front, posts=[0.0, 0.49, 0.95, 2.0, 2.46, W / 2], rails=[0.0, 0.8, h2], braces=[], w=0.13, col="blackoak")
        P.timber_frame(f2.back, posts=[0.0, W / 2], rails=[0.0, h2], braces=[(0, 0, W / 2, h2)], col="blackoak")
        P.timber_frame(f2.left if sx < 0 else f2.right, posts=[0.0, D + 0.55], rails=[0.0, h2], braces=[], col="blackoak")
        P.window(f2.front, W / 4, 0.85, w=0.9, h=1.2, bars=(1, 2), lintel=None, shutters=A, box=(sx > 0))
        P.window(f2.back, W / 4, 0.85, w=0.8, h=1.2, bars=(1, 2), lintel=None)
        P.window(f2.left if sx < 0 else f2.right, 3.6, 1.0, w=0.7, h=1.0, bars=(1, 1), lintel=None)
        f2.gable(ridge="y", pitch=56, mat="tiles", sag=0.06, eave=0.14, verge=0.2)
        Q.gable_holes(f2.front)
        P.window(f2.front, W / 4, h2 + 0.4, w=0.5, h=0.7, bars=(1, 1), lintel=None, sill=False)
        P.timber_frame(f2.front, z0=h2, z1=h2 + 2.0, posts=[], rails=[], braces=[(0.5, h2 + 0.1, 1.0, h2 + 1.2), (W / 2 - 0.5, h2 + 0.1, W / 2 - 1.0, h2 + 1.2), (0.95, h2 + 1.25, W / 2 - 0.95, h2 + 1.25)],
                       col="blackoak")
    P.chimney(b, 0.0, 4.4, ZE - 0.2, 4.4, w=0.8, d=0.6, mat="masonry", col="warm", pots=3)
    P.door(g.back, 4.6, w=0.9, h=2.0, z=0.15, col=A, frame="timber", steps=1)
    P.window(g.back, 1.6, 1.2, w=1.0, h=1.2, bars=(1, 1))
    P.barrel(b, 2.3, D + 0.45, 0)
    P.crate(b, 1.5, D + 0.5, 0, s=0.55, rz=15)
