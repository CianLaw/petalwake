# Thimble & Shears: the tailor works at the long window upstairs where the light lasts longest; half the town's
# Sunday coats were cut on the table behind it.
# Massing: two storeys and a roof room; the whole first-floor front is one long shallow oriel of glass under a deep
# hipped roof with a dormer; a shop window and door below; a dyer's line of cloth across the back yard.
# Materials: rose lime plaster on a stone base, terracotta tiles, a brick stack; plum woodwork.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "Thimble & Shears, tailors", "kind": "shop", "lot": (5.5, 8.0)}

A = "plum"
W, D = 4.6, 6.6
Z1, ZE = 3.1, 6.0
DYES = ["#b5433a", "#3f6fb5", "#d9a431", "#7a4672", "#5a9a68", "#f3ecd9"]


def dress_form(b, x, y, z=0.0, col="#e9dcc3"):
    with b.at(x, y, z):
        with b.detail(2):
            b.tube((0, 0, 0.05), (0, 0, 0.95), r=0.025, mat="planks", col="darkoak", n=5)
            b.revolve([(0.0, 0.0), (0.18, 0.0), (0.18, 0.05), (0.0, 0.05)], "planks", col="darkoak", seg=6)
            b.revolve([(0.15, 0.92), (0.2, 1.08), (0.14, 1.24), (0.19, 1.44), (0.1, 1.56), (0.05, 1.62), (0.0, 1.64)], "cloth", col=col, seg=8)


def build(b):
    g = b.body(W, D, Z1, mat="plaster", col="rose")
    P.plinth(g, h=0.55)
    Q.quoins(g, corners="fr", z0=0.55)
    Q.shopfront(g.front, 1.6, 0.0, w=2.1, h=1.65, riser=0.62, col=A, lights=2, goods="cloth")
    P.door(g.front, 3.75, w=0.95, h=2.1, z=0.15, col=A, frame="timber", steps=1, lamp=True)
    Q.sign(g.front, 4.3, 2.95, emblem="scissors", shape="shield", col=A, out=0.8)
    Q.joists(g.front, Z1, out=0.3)
    P.window(g.right, 4.6, 1.3, w=0.7, h=1.1, bars=(1, 1))
    P.exposed(g.right, "base", n=5)
    # --- the workroom: one long oriel across the whole front
    f1 = b.body(W, D + 0.3, ZE - Z1, mat="plaster", col="rose", z=Z1, y=(D - 0.3) / 2, floor="planks")
    Q.bay(f1.front, W / 2, 0.6, w=4.1, h=1.55, out=0.38, cant=0.3, apron=0.3, col="ivory", apron_col=A, panes=(9, 2), side_panes=(1, 2), base="brackets", drop=0.55,
          roof="lead", roof_h=0.28)
    P.window(f1.right, 2.6, 0.95, w=0.8, h=1.3, bars=(1, 2))
    P.window(f1.left, 4.4, 0.95, w=0.8, h=1.3, bars=(1, 2))
    for u in (1.2, W - 1.2):
        P.window(f1.back, u, 0.95, w=0.9, h=1.3, shutters=A, bars=(1, 2), box=True)
    P.band(f1, ZE - Z1 - 0.22, h=0.2, out=0.06)
    Q.quoins(f1, corners="fr", z1=ZE - Z1 - 0.25)
    # --- the hipped roof, its dormer and the stack
    f1.hip(pitch=50, mat="tiles", eave=0.3)
    P.dormer(b, 0.0, -0.3 + 0.6, ZE + 0.6 * math.tan(rad(50)), w=2.1, h=1.2, depth=1.7, col="rose", shutters=A)
    P.chimney(b, 1.45, 4.6, ZE + 0.4, 3.4, w=0.55, d=0.5, mat="brick", pots=2)
    # --- behind: the back door, and the dyer's line out to a post
    P.door(g.back, 1.1, w=0.9, h=2.0, z=0.15, col=A, frame="timber", steps=1)
    P.window(g.back, 3.3, 1.3, w=0.9, h=1.2, bars=(1, 1))
    with b.detail(1):
        b.beam((1.9, D + 1.05, 0), (1.9, D + 1.05, 3.3), w=0.12, mat="timber", col="darkoak")
    P.laundry(b, (-1.9, D + 0.02, 5.0), (1.9, D + 1.05, 3.2), n=5, cols=DYES)
    # --- the street
    dress_form(b, -1.95, -0.55)
    with b.at(1.95, -0.45, 0):
        with b.detail(2):
            b.box(0.5, 0.5, 0.45, "planks", col="#d8c3a0")
            for i, c in enumerate(("#3f6fb5", "#b5433a", "#d9a431")):
                b.tube((-0.14 + 0.14 * i, 0.0, 0.2), (-0.16 + 0.16 * i, 0.03 * i, 1.2), r=0.07, mat="cloth", col=c, n=6, caps=True)
