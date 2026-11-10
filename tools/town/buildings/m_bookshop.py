# Quire & Quill, booksellers: four leaning storeys of books, charts and almanacs; the top floor is all the unsold
# poetry, and the shop cat is said to have read most of it.
# Massing: very narrow and tall, each floor jettied a hand's breadth beyond the one below, a steep slate roof with its
# gable to the street, a square bay of small panes beside the door.
# Materials: a rubble ground floor, sky-blue lime plaster with oak corner posts above, slate; navy woodwork.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "Quire & Quill, booksellers", "kind": "shop", "lot": (5.5, 8.0), "lean": (0.006, -0.004)}

A = "navy"
W, D = 4.4, 6.9
ZS = [0.0, 3.0, 5.7, 8.3, 10.7]        # floor levels and the eaves
JET = [0.0, 0.25, 0.5, 0.7]            # how far each storey stands forward


def build(b):
    g = b.body(W, D, ZS[1], mat="masonry", col="warm")
    P.plinth(g, h=0.45)
    # --- the bay of small panes, the door, the reading lamp, the sign
    Q.bay(g.front, 1.45, 0.0, w=2.2, h=1.6, out=0.5, cant=0.0, apron=0.75, col=A, apron_col=A, panes=(5, 4), side_panes=(1, 4), base=None, roof="lead", roof_h=0.3)
    P.door(g.front, 3.55, w=0.95, h=2.1, z=0.15, col=A, frame="timber", steps=1, lamp=True)
    Q.sign(g.front, 4.15, 2.85, emblem="book", shape="rect", col=A, out=0.8, w=0.6, h=0.5)
    Q.joists(g.front, ZS[1], out=JET[1])
    Q.cat(b, -W / 2 + 1.45, -0.3, 2.52, rz=20, col="#2d2a2a", sit=False)
    P.window(g.right, 4.8, 1.2, w=0.7, h=1.1, bars=(1, 1))
    P.stones(g.front, n=5, z0=0.5, u0=2.7)
    # --- three jettied storeys
    bodies = []
    for k in (1, 2, 3):
        f = b.body(W, D + JET[k], ZS[k + 1] - ZS[k], mat="plaster", col="sky", z=ZS[k], y=(D - JET[k]) / 2, floor="planks")
        h = ZS[k + 1] - ZS[k]
        for wl in f.walls:
            P.timber_frame(wl, posts=[0.0, wl.w], rails=[0.0, h], braces=[])
        if k < 3:
            Q.joists(f.front, h, out=JET[k + 1] - JET[k])
        bodies.append(f)
    f1, f2, f3 = bodies
    P.window(f1.front, 1.45, 0.85, w=1.7, h=1.3, bars=(3, 2), lintel="timber", box=True)
    P.window(f1.front, 3.55, 0.85, w=0.75, h=1.3, bars=(1, 2), lintel="timber")
    for u in (1.2, 3.2):
        P.window(f2.front, u, 0.85, w=0.9, h=1.25, shutters=A, bars=(1, 2), lintel="timber")
    P.window(f3.front, W / 2, 0.7, w=1.5, h=1.15, bars=(3, 1), lintel="timber", box=True)
    for f, u in ((f1, 2.4), (f2, 4.9), (f3, 3.0)):
        P.window(f.right, u, 0.85, w=0.7, h=1.15, bars=(1, 2), lintel="timber")
        P.window(f.left, D - u + 1.0, 0.85, w=0.7, h=1.15, bars=(1, 2), lintel="timber")
    for f in (f1, f2):
        P.window(f.back, W / 2, 0.85, w=1.0, h=1.25, bars=(1, 2), shutters=A)
    f3.gable(ridge="y", pitch=57, mat="slate", sag=0.08, eave=0.25, verge=0.22)
    Q.gable_holes(f3.front)
    Q.gable_holes(f3.back)
    P.window(f3.front, W / 2, ZS[4] - ZS[3] + 0.55, w=0.55, h=0.9, arch=0.27, bars=(1, 1))
    P.window(f3.back, W / 2, ZS[4] - ZS[3] + 0.5, w=0.6, h=0.9, bars=(1, 1))
    P.chimney(b, -1.5, 5.2, ZS[4] + 0.3, 3.6, w=0.5, d=0.5, mat="brick", pots=1)
    Q.weathercock(b, 0, -JET[3] + 0.1, ZS[4] + 2.2 * math.tan(rad(57)), h=1.1, shape="pennon", size=0.7)
    # --- a lean-to scullery behind and the back door
    P.door(g.back, 1.0, w=0.9, h=2.0, z=0.15, col=A, frame="timber", steps=1)
    P.window(g.back, 3.1, 1.2, w=0.9, h=1.2, bars=(1, 1))
    # --- the pavement: the penny table
    with b.at(-0.35, -0.95, 0):
        with b.detail(2):
            b.box(1.5, 0.55, 0.05, "planks", col="greyoak", z=0.72, bottom=True)
            for sx in (-1, 1):
                b.box(0.06, 0.5, 0.72, "planks", col="darkoak", x=sx * 0.62)
        with b.at(0, -0.1, 0.77):
            Q.display(b, 1.3, "books", depth=0.2)
        with b.at(0, 0.14, 0.77):
            Q.display(b, 1.2, "books", depth=0.2)
    P.planter(b, 1.85, -0.28, 0, w=0.45, d=0.4, h=0.36, bush=True)
