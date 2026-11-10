# Pippin & Daughters, grocers: everything that grows within a day's cart ride ends up tipped in crates under the two
# green awnings; the loft still smells of last autumn's apples.
# Massing: broad and low, two storeys of butter-yellow plaster under a tiled gambrel roof with two dormers (one is
# the loft hoist), twin shop windows either side of the door, a store lean-to behind.
# Materials: butter lime plaster on a stone base, terracotta tiles, a brick chimney; green paint and striped canvas.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "Pippin & Daughters, grocers", "kind": "shop", "lot": (7.5, 9.0)}

A = "green"
W, D = 6.6, 6.6
Z1, ZE = 3.2, 6.0
SEC = [(0.0, 0.0), (0.95, 2.3), (D / 2, 3.7)]        # gambrel: steep below, easy above


def trestle(b, x, y, w=1.9, cols=None):
    """A plank trestle with tipped-up crates of produce."""
    with b.at(x, y, 0):
        with b.detail(2):
            b.box(w, 0.6, 0.05, "planks", col="greyoak", z=0.4, bottom=True)
            for sx in (-1, 1):
                b.box(0.07, 0.5, 0.4, "planks", col="darkoak", x=sx * (w / 2 - 0.15))
        n = int(w / 0.62)
        for i in range(n):
            Q.produce(b, -w / 2 + w * (i + 0.5) / n, 0.0, 0.45, s=0.54, cols=cols[i % len(cols)] if cols else None)


def build(b):
    g = b.body(W, D, Z1, mat="plaster", col="butter")
    P.plinth(g, h=0.5)
    # --- twin shop windows under twin awnings, the door between, the apple sign over it
    for u, goods in ((1.5, "fruit"), (W - 1.5, "pots")):
        Q.shopfront(g.front, u, 0.0, w=2.0, h=1.6, riser=0.62, col=A, lights=2, goods=goods, fascia=0.26)
        P.awning(g.front, u, 3.02, w=2.5, out=1.15, drop=0.5, cols=("stripe_green", "linen"))
    P.door(g.front, W / 2, w=1.0, h=2.15, z=0.15, col=A, frame="timber", steps=1, lamp=True)
    Q.sign(g.front, W / 2 + 0.75, 3.12, emblem="apple", shape="round", col="red", out=0.95)
    P.window(g.right, 4.6, 1.3, w=0.8, h=1.2, bars=(1, 1))
    P.window(g.left, 2.0, 1.3, w=0.8, h=1.2, bars=(1, 1))
    P.exposed(g.left, "base", n=6)
    # --- upstairs: three shuttered windows over a string course
    f1 = b.body(W, D, ZE - Z1, mat="plaster", col="butter", z=Z1)
    P.band(f1, 0.0, h=0.18, out=0.06)
    for i, u in enumerate((1.2, W / 2, W - 1.2)):
        P.window(f1.front, u, 0.95, w=0.95, h=1.35, shutters=A, box=(i != 1), bars=(1, 2))
    for u in (1.6, W - 1.6):
        P.window(f1.back, u, 0.95, w=0.95, h=1.35, shutters=A, bars=(1, 2))
    P.window(f1.right, 2.0, 0.95, w=0.8, h=1.3, bars=(1, 2))
    P.window(f1.left, 4.6, 0.95, w=0.8, h=1.3, bars=(1, 2))
    # --- the gambrel roof, its dormers, the loft hoist
    f1.gable(ridge="x", mat="tiles", section=SEC, sag=0.14, eave=0.35, verge=0.12)
    zd = ZE + 0.38 * 2.3 / 0.95
    for x in (-1.75, 1.75):
        P.dormer(b, x, 0.38, zd, w=1.15, h=1.15, depth=1.5, col="butter", shutters=None if x > 0 else A)
    Q.hoist(b, 1.75, 0.3, zd + 1.15 + 0.5, face=0, out=0.9, rope=2.2, load="sack")
    P.dormer(b, 0.0, D - 0.38, zd, w=1.15, h=1.15, depth=1.5, face=180, col="butter")
    P.chimney(b, -2.4, D / 2 + 0.5, ZE + 3.0, 2.6, mat="brick", pots=2)
    # --- the store behind: a lean-to with a wide door for the cart
    st = b.body(4.2, 1.7, 2.4, mat="plaster", col="butter", x=W / 2 - 2.1, y=D + 0.85)
    Q.plinth(st, h=0.35, walls="rbl")
    P.door(st.back, 2.1, w=1.7, h=1.95, z=0.05, col=A, frame="timber", double=True)
    rs = Q.lean_to(b, 4.2, 1.7, pitch=26, x=W / 2 - 2.1, y=D, z=2.4, face=180, eave=0.2, verge=0.1)
    b.tri((W / 2 - 4.2, D + 1.7, 2.4), (W / 2 - 4.2, D, 2.4), (W / 2 - 4.2, D, 2.4 + rs), "plaster", col="butter")
    b.tri((W / 2, D, 2.4), (W / 2, D + 1.7, 2.4), (W / 2, D, 2.4 + rs), "plaster", col="butter")
    P.door(g.back, W - 1.0, w=0.9, h=2.0, z=0.15, col=A, frame="timber", steps=1)
    # --- the pavement: crates on trestles, sacks, a barrel of brooms
    trestle(b, -1.8, -0.72, cols=[["#d8432e"], ["#7fae3f"], ["#e88a2a"]])
    trestle(b, 1.85, -0.72, w=1.3, cols=[["#f0c53a"], ["#8d5ba8", "#b3202e"]])
    P.sack(b, 3.0, -0.4, 0)
    P.sack(b, 2.95, -0.85, 0, r=0.25)
    P.barrel(b, -3.05, -0.45, 0, r=0.28, h=0.75)
    Q.cat(b, 0.62, -0.35, 0.17, rz=30, col="#b9763a")
