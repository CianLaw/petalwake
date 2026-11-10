# The Oven Door: the square's bakery. The oven has been alight for three generations and its chimney is how sailors
# find the square from the bay; loaves go out through the hatch before the shop door is even unbolted.
# Massing: low and broad, a stone ground floor under a plastered knee wall and one great steep tiled roof, a gabled
# flour loft breaking the eaves, a massive outside chimney on the gable and the round back of the oven behind.
# Materials: warm rubble, peach plaster in oak framing, sagging terracotta tiles; orange paintwork.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Oven Door bakery", "kind": "shop", "lot": (7.5, 9.0)}

A = "orange"
W, D = 6.6, 7.2


def build(b):
    g = b.body(W, D, 3.0, mat="masonry", col="warm")
    P.plinth(g, h=0.45)
    k = b.body(W, D, 1.2, mat="plaster", col="peach", z=3.0)
    # --- the shop: door, window full of loaves, the bread hatch, a pentice over both
    P.door(g.front, 0.95, w=1.0, h=2.1, z=0.15, col=A, frame="timber", steps=1, lamp=True)
    Q.shopfront(g.front, 3.15, 0.0, w=2.3, h=1.55, riser=0.7, col=A, lights=3, goods="loaves", fascia=0.0)
    Q.counter(g.front, 5.55, 1.0, w=1.2, h=1.15, col=A, goods="loaves")
    Q.pent(g.front, 4.25, 2.98, w=4.7, out=0.85)
    P.stones(g.front, n=6, z0=0.5, u1=1.9)
    P.timber_frame(k.front, rails=[0.0, 1.2], braces=[])
    Q.sign(k.front, 0.32, 0.55, emblem="pretzel", shape="round", col="brown", out=0.85)
    P.window(k.front, 1.35, 0.3, w=0.8, h=0.75, shutters=A, lintel=None, bars=(1, 1))
    P.window(k.front, 6.0, 0.3, w=0.6, h=0.75, lintel=None, bars=(1, 1))
    # --- the flour loft: a gabled wall-dormer with its door and hoist
    ld = b.body(2.3, 2.0, 1.55, mat="plaster", col="peach", x=-W / 2 + 4.2, y=1.0, z=4.2, foot=False)
    P.timber_frame(ld.front, posts=[0.0, 2.3], rails=[0.0, 1.55], braces=[])
    P.door(ld.front, 1.15, w=0.9, h=1.3, z=0.04, col=A, frame="timber", knob=False)
    ld.gable(ridge="y", pitch=50, mat="tiles", eave=0.22, verge=0.3)
    Q.hoist(b, -W / 2 + 4.2, 0.0, 4.2 + 1.55 + 0.75, face=0, out=0.95, rope=2.9, load="sack")
    # --- the big roof and the gable ends
    k.gable(ridge="x", pitch=52, mat="tiles", sag=0.2, eave=0.4, verge=0.12)
    Q.gable_holes(k.left)
    P.window(k.left, D / 2, 2.1, w=0.8, h=1.1, bars=(1, 2))
    P.window(g.left, 2.0, 1.2, w=0.8, h=1.2, bars=(1, 1))
    P.window(g.right, 1.6, 1.2, w=0.8, h=1.2, bars=(1, 1))
    # --- the great oven chimney on the right gable, the oven's round back behind
    Q.stack(b, 3.1, 4.6, 0.0, 11.2, w=0.95, d=1.15, base=(0.95, 2.3, 4.4), pots=2)
    ox = 1.6
    P.round_base(b, 1.3, h=0.5, out=0.15, seg=10, x=ox, y=D)
    b.round(1.3, 2.0, mat="masonry", col="warm", seg=10, x=ox, y=D)
    Q.cone_part(b, 1.3, 1.3, a0=90, a1=270, mat="tiles", x=ox, y=D, z=2.0, seg=6, eave=0.2, flare=0.2, course=0.35)
    P.door(g.back, 4.7, w=0.95, h=2.0, z=0.15, col=A, frame="timber", steps=1)
    P.window(g.back, 6.0, 1.2, w=0.7, h=1.1, bars=(1, 1))
    for u in (1.3, 5.3):
        P.window(k.back, u, 0.3, w=0.7, h=0.75, lintel=None, bars=(1, 1))
    P.dormer(b, -1.4, D - 1.0, 4.2 + 1.0 * math.tan(rad(52)), w=1.0, h=0.95, depth=1.3, face=180, col="peach")
    # --- the street
    P.sack(b, -3.0, -0.45, 0)
    P.sack(b, -2.55, -0.75, 0, r=0.26)
    P.barrel(b, -1.6, -0.5, 0, r=0.27, h=0.7)
    Q.cat(b, 1.75, -0.22, 1.0, rz=-10, col="#e9e4d8", sit=False)
    P.planter(b, 0.95, -0.3, 0, w=0.7)
