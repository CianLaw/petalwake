# The Terrace Tea House: two sisters turned the flat roof over their tea room into the best view in the high street;
# riders with a parcel of leaf tea set down among the chimney stacks and are given a cup before they go.
# Massing: a two-storey front range with a flat, railed roof terrace 7.8 m up between two brick chimney stacks; behind
# it a taller range under a tiled roof whose door and dormer look out over the terrace.
# Materials: sage-green lime plaster on a stone base, brick stacks, tiles, white-painted rails; pink woodwork and awning.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Terrace Tea House", "kind": "shop", "lot": (7.5, 9.0)}

A = "pink"
ROSE = "#e58fa6"            # the awning and parasol stripe
W, D, FD, ZT = 6.9, 8.5, 5.2, 7.8   # width, depth, depth of the terrace range, terrace floor


def cakes(b, w):
    Q.display(b, w, "pots", cols=["#f2a0bd", "#f4f1e4", "#8fcfae", "#f5c842", "#e9d9a0"], depth=0.1)


def build(b):
    # --- ground floor: the tea room window under its awning, the door, the sign
    g = b.body(W, D, 3.5, mat="plaster", col="sage")
    P.plinth(g, h=0.5)
    Q.shopfront(g.front, 2.35, 0.0, w=3.2, h=1.9, riser=0.6, col=A, lights=4, goods=cakes)
    P.awning(g.front, 2.35, 3.32, w=3.9, out=1.2, drop=0.55, cols=(ROSE, "linen"))
    P.door(g.front, 5.45, w=1.0, h=2.15, z=0.12, col=A, frame="timber", steps=1, lamp=True)
    Q.sign(g.front, 6.6, 3.3, emblem="teapot", shape="round", col=A, w=0.62, out=0.85)
    P.window(g.right, 6.6, 1.2, w=0.9, h=1.3)
    P.window(g.left, 2.2, 1.2, w=0.9, h=1.3)
    P.door(g.back, 1.6, w=0.95, h=2.05, z=0.12, col=A, frame="timber", steps=1)
    P.window(g.back, 4.6, 1.2, w=1.2, h=1.3, bars=(2, 1), shutters=A)
    P.exposed(g.right, "base", n=6)
    # --- first floor: three shuttered windows over a string course, a cornice under the terrace
    f1 = b.body(W, D, ZT - 3.5, mat="plaster", col="sage", z=3.5)
    P.band(f1, 0.0, h=0.2, out=0.06)
    P.band(f1, ZT - 3.5 - 0.5, h=0.22, out=0.09)
    for i, u in enumerate((1.3, 3.5, 5.7)):
        P.window(f1.front, u, 1.0, w=0.95, h=1.45, shutters=A, box=(i != 1), bars=(1, 2))
    P.window(f1.right, 6.6, 1.0, w=0.9, h=1.45)
    P.window(f1.left, 2.2, 1.0, w=0.9, h=1.45)
    for u in (1.6, 4.6):
        P.window(f1.back, u, 1.0, w=0.95, h=1.45, shutters=A, box=(u < 2))
    # --- the roof terrace: flags, a kerb with a white rail, a gap to the street between two lamp piers
    b.box(W - 0.04, FD - 0.02, 0.12, "flagstone", col="stone", x=0, y=FD / 2 + 0.01, z=ZT - 0.12)
    hw = W / 2
    left = [(-hw, FD, ZT), (-hw, 0.0, ZT), (-0.9, 0.0, ZT)]
    right = [(0.9, 0.0, ZT), (hw, 0.0, ZT), (hw, FD, ZT)]
    for line in (left, right):
        Q.parapet(b, line, h=0.4, t=0.22, mat="plaster", col="sage")
        P.railing(b, [(x * (1 - 0.11 / abs(x)) if abs(x) > 1 else x, max(y, 0.11), ZT + 0.48) for x, y, _ in line], h=0.62, style="balusters", col="ivory", mat="planks",
                  post=0.09, gap=0.18)
    for sx in (-1, 1):
        with b.detail(1):
            b.box(0.26, 0.26, 1.16, "ashlar", col="stone", x=sx * 0.9, y=0.13, z=ZT)
        Q.post_lantern(b, sx * 0.9, 0.13, ZT + 1.16)
        P.planter(b, sx * 3.0, 0.62, ZT, w=0.5, d=0.5, h=0.4, bush=True)
    with b.at(0, 2.3, ZT):
        P.landing_mark(b, 1.25)
    b.pad(0, 2.3, ZT, radius=1.3, face=0, name="Tea house roof terrace")
    Q.table(b, -2.3, 3.95, ZT, cloth="linen")
    Q.chair(b, -2.3, 3.3, ZT, rz=180)
    Q.chair(b, -1.65, 4.1, ZT, rz=280)
    Q.parasol(b, -2.5, 4.2, ZT, r=1.05, h=2.25, cols=(ROSE, "linen"))
    Q.table(b, 2.35, 3.5, ZT, col="ivory")
    Q.chair(b, 2.35, 2.85, ZT, rz=180)
    Q.chair(b, 2.95, 3.7, ZT, rz=250)
    with b.at(2.35, 3.5, ZT + 0.72):
        with b.detail(2):
            b.revolve([(0.07, 0.0), (0.1, 0.06), (0.07, 0.13), (0.03, 0.15), (0.0, 0.17)], "paint", col=ROSE, seg=6)
            b.beam((0.09, 0, 0.08), (0.17, 0, 0.13), w=0.025, mat="paint", col=ROSE, caps=False)
    Q.cat(b, 2.2, 0.11, ZT + 0.48, rz=-15, col="#efe9df")
    # --- the two stacks the terrace sits between
    Q.stack(b, -3.25, 1.6, 0.0, 10.6, w=0.64, d=0.95, mat="brick", col=None, pots=2)
    Q.stack(b, 3.25, 4.3, 0.0, 11.3, w=0.64, d=0.95, mat="brick", col=None, pots=3)
    # --- the back range: the door onto the terrace, a dormer, the roof
    rb = b.body(W, D - FD, 2.6, mat="plaster", col="sage", x=0, y=(D + FD) / 2, z=ZT)
    P.door(rb.front, 2.2, w=0.9, h=2.0, z=0.02, col=A, frame="timber")
    Q.pent(rb.front, 2.2, 2.62, w=1.7, out=0.6)
    P.window(rb.front, 4.9, 0.9, w=1.3, h=1.2, bars=(2, 1), shutters=A, box=True)
    P.window(rb.left, 1.7, 0.9, w=0.8, h=1.2)
    P.window(rb.right, 1.7, 0.9, w=0.8, h=1.2)
    for u in (1.6, 4.6):
        P.window(rb.back, u, 0.9, w=0.95, h=1.2, shutters=A)
    rb.gable(ridge="x", pitch=48, mat="tiles", sag=0.1, eave=0.32, verge=0.1)
    Q.gable_holes(rb.left)
    P.window(rb.left, 1.7, 2.6 + 0.4, w=0.55, h=0.75, bars=(1, 1))
    tz = math.tan(rad(48))
    P.dormer(b, 1.5, FD + 0.75, ZT + 2.6 + 0.75 * tz, w=1.1, h=1.0, depth=1.5, col="sage")
    P.chimney(b, -1.9, 7.5, ZT + 2.6 + 1.1 * tz - 0.5, 2.4, mat="brick", pots=2)
    Q.bunting(b, (-3.3, FD - 0.1, ZT + 2.42), (3.3, FD - 0.1, ZT + 2.42), sag=0.28, cols=(ROSE, "linen", "stripe_yellow", "mint"))
    # --- the street: a table under the awning
    Q.table(b, -2.2, -0.72, 0, r=0.36, cloth=ROSE)
    Q.chair(b, -2.85, -0.7, 0, rz=90)
    Q.chair(b, -1.55, -0.7, 0, rz=270)
    P.planter(b, 0.55, -0.28, 0, w=0.8)
    P.planter(b, 3.1, -0.28, 0, w=0.5, d=0.42, h=0.4, bush=True)
