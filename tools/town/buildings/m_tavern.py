# The Blue Anchor: the old coaching inn on the square; carts still rattle through its arch to the galleried yard,
# and the taproom fire has not gone out, they say, since the great storm.
# Massing: a rubble ground floor split by a carriage arch you can see through to the yard; a jettied timber-framed
# storey over it, a second jetty in the cross-gable; a steep sagging tiled roof with dormers; a huge outside chimney.
# Materials: warm rubble below, butter plaster in dark oak above, tiles; in the yard an oak gallery and stair; blue doors.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Blue Anchor", "kind": "tavern", "lot": (11.0, 10.0)}

A = "blue"
YG, YF, YC = 1.0, 0.6, 0.2    # front of the ground floor, of the jettied first floor, of the cross-gable
YB = 7.0                      # back of the ground floor; the yard lies behind
ZG, ZF = 3.3, 6.2             # first floor, eaves
PX0, PX1 = 1.9, 4.5           # the carriage way
T50 = math.tan(rad(50))


def build(b):
    # --- ground floor: two rubble blocks either side of the carriage way, an arch at each end of it
    gl = b.body(PX0 + 5.0, YB - YG, ZG, mat="masonry", col="warm", x=(PX0 - 5.0) / 2, y=(YG + YB) / 2)
    gr = b.body(5.0 - PX1, YB - YG, ZG, mat="masonry", col="warm", x=(PX1 + 5.0) / 2, y=(YG + YB) / 2)
    Q.plinth(gl, h=0.5, walls="fbl")
    Q.plinth(gr, h=0.5, walls="frb")
    pw = PX1 - PX0
    b.box(pw - 0.04, YB - YG - 0.04, 3.04, "cobble", x=(PX0 + PX1) / 2, y=(YG + YB) / 2, z=-3.0)
    for y in (YG, YB - 0.5):
        with b.at(PX0, y, 0):
            af, ab = Q.arcade(b, pw, ZG, thick=0.5, arches=[(pw / 2, 2.3, 3.0, 0.95)], mat="masonry", col="warm", ends="", top=False)
            Q.surround(af if y == YG else ab, pw / 2, 0.0, 2.3, 3.0, arch=0.95, t=0.24)
            if y == YG:
                Q.joists(af, ZG, out=0.4, n=3)
                P.lantern(af, 0.14, 2.5)
    with b.detail(1):
        for y in (2.0, 3.2, 4.4, 5.6):
            b.beam((PX0, y, ZG - 0.11), (PX1, y, ZG - 0.11), w=0.16, h=0.2, mat="timber", col="darkoak", caps=False)
    P.door(gl.right, 3.2, w=0.9, h=2.0, z=0.06, col=A, frame="timber")
    # --- the taproom front: a bay of small panes, the door, the sign
    Q.bay(gl.front, 2.0, 0.0, w=2.6, h=1.5, out=0.55, cant=0.35, apron=0.85, apron_mat="masonry", apron_col="warm", base=None, roof="tiles", col="ivory",
          panes=(4, 3), side_panes=(1, 3))
    P.door(gl.front, 6.0, w=1.05, h=2.1, z=0.15, col=A, frame="timber", steps=1, lamp=True)
    Q.sign(gl.front, 6.72, 3.08, emblem="anchor", shape="arch", col=A, out=0.85)
    Q.joists(gl.front, ZG, out=0.4)
    Q.joists(gr.front, ZG, out=0.4, n=1, inset=0.1)
    P.window(gl.back, 2.2, 1.2, w=0.9, h=1.2, bars=(1, 1))
    P.door(gl.back, 5.2, w=0.95, h=2.0, z=0.06, col=A, frame="timber")
    P.stones(gl.front, n=10, z0=0.6)
    # --- the first floor: jettied, close-framed, a row of casements
    f1 = b.body(10.0, YB + 0.2 - YF, ZF - ZG, mat="plaster", col="butter", x=0, y=(YF + YB + 0.2) / 2, z=ZG, floor="planks")
    posts = [1.25 * i for i in range(9)]
    P.timber_frame(f1.front, posts=posts, rails=[0.0, 0.9, 2.9],
                   braces=[(0, 0.9, 1.25, 2.9), (2.5, 2.9, 3.75, 0.9), (5.0, 0.9, 6.25, 2.9), (7.5, 2.9, 8.75, 0.9), (0, 0.9, 1.25, 0), (10, 0.9, 8.75, 0)])
    for i, u in enumerate((1.875, 4.375, 6.875, 9.375)):
        P.window(f1.front, u, 0.95, w=0.9, h=1.25, bars=(1, 2), lintel=None, box=(i in (1, 2)))
    P.timber_frame(f1.back, posts=posts, rails=[0.0, 2.9], braces=[(0, 0, 1.25, 2.9), (10, 0, 8.75, 2.9)])
    for u in (2.6, 7.6):
        P.door(f1.back, u, w=0.85, h=1.95, z=0.03, col=A, frame=None)
    for u in (0.65, 4.4, 5.65, 9.35):
        P.window(f1.back, u, 0.95, w=0.8, h=1.2, bars=(1, 1), lintel=None)
    P.timber_frame(f1.left, posts=[0, 1.7, 5.0, 6.8], rails=[0.0, 2.9], braces=[(5.0, 2.9, 6.8, 0)])
    P.timber_frame(f1.right, posts=[0, 2.6, 4.2, 6.8], rails=[0.0, 0.9, 2.9], braces=[(0, 0.9, 2.6, 2.9), (6.8, 0.9, 4.2, 2.9)])
    P.window(f1.right, 3.4, 0.95, w=0.9, h=1.25, bars=(1, 2), lintel=None)
    Q.joists(f1.front, ZF - ZG, out=0.4, u0=0.5, u1=5.1)
    f1.gable(ridge="x", pitch=50, mat="tiles", sag=0.18, eave=0.38, verge=0.3)
    # --- the cross-gable: one more jetty, a wide casement, a little window in the peak
    cg = b.body(4.6, 4.2, 1.8, mat="plaster", col="butter", x=-2.2, y=YC + 2.1, z=ZF, floor="planks")
    P.timber_frame(cg.front, posts=[0, 1.2, 3.4, 4.6], rails=[0.0, 0.5, 1.8], braces=[(0, 0.5, 1.2, 1.8), (4.6, 0.5, 3.4, 1.8)])
    P.window(cg.front, 2.3, 0.55, w=1.7, h=1.05, bars=(3, 1), lintel=None, box=True)
    P.timber_frame(cg.left, posts=[2.6, 4.2], rails=[1.8], braces=[])
    cg.gable(ridge="y", pitch=50, mat="tiles", sag=0.06, eave=0.35, verge=0.2)
    Q.gable_holes(cg.front)
    P.window(cg.front, 2.3, 2.3, w=0.6, h=0.8, bars=(1, 1), lintel=None, sill=False)
    P.timber_frame(cg.front, z0=1.8, z1=4.4, posts=[], rails=[], braces=[(0.9, 1.9, 1.7, 3.45), (3.7, 1.9, 2.9, 3.45), (1.5, 3.42, 3.1, 3.42)])
    # --- roofscape: dormers, the great chimney, a brick stack
    for x in (1.9, 4.0):
        P.dormer(b, x, YF + 0.8, ZF + 0.8 * T50, w=1.05, h=1.0, depth=1.5, col="butter")
    P.dormer(b, -1.6, YB + 0.2 - 0.8, ZF + 0.8 * T50, w=1.05, h=1.0, depth=1.5, face=180, col="butter")
    Q.stack(b, -4.9, 4.0, 0.0, 13.4, w=0.9, d=1.25, base=(0.9, 2.6, 4.4), pots=3)
    P.chimney(b, 3.1, 4.7, 8.4, 3.2, mat="brick", pots=2)
    # --- the yard: cobbles, a wall round it, the gallery along the back of the house and the stair up to it
    b.box(10.0, 2.84, 3.03, "cobble", x=0, y=8.44, z=-3.0)
    Q.parapet(b, [(5.0, YB, 0), (5.0, 9.86, 0), (-5.0, 9.86, 0), (-5.0, YB, 0)], h=1.7, t=0.3)
    yg = YB + 0.2
    b.box(9.8, 1.1, 0.12, "planks", col="greyoak", x=0, y=yg + 0.55, z=ZG - 0.12, bottom=True)
    b.box(1.0, 1.05, 0.12, "planks", col="greyoak", x=-4.4, y=yg + 1.1 + 0.52, z=ZG - 0.12, bottom=True)
    for x in (-4.82, -3.9, -1.3, 1.75, 4.65):
        b.beam((x, yg + 1.02, 0.03), (x, yg + 1.02, ZG + 1.0), w=0.16, mat="timber", col="darkoak", lod=0)
        with b.detail(1):
            b.beam((x, yg + 1.02, ZG - 0.9), (x + (0.6 if x < 4 else -0.6), yg + 1.02, ZG - 0.14), w=0.11, mat="timber", col="darkoak", caps=False)
    b.beam((-4.82, yg + 2.1, 0.03), (-4.82, yg + 2.1, ZG + 1.0), w=0.16, mat="timber", col="darkoak", lod=0)
    P.railing(b, [(-3.9, yg + 1.02, ZG), (4.82, yg + 1.02, ZG), (4.82, yg + 0.06, ZG)], h=0.95, style="balusters")
    P.railing(b, [(-4.82, yg + 0.06, ZG), (-4.82, yg + 2.1, ZG), (-3.95, yg + 2.1, ZG)], h=0.95, style="balusters")
    with b.at(-0.3, yg + 1.62, 0.03, rz=90):
        P.stairs(b, w=0.85, rise=(ZG - 0.03) / 14, run=0.257, n=14, solid=False, rail="balusters")
    with b.detail(1):
        b.box(1.7, 0.62, 0.5, "ashlar", col="grey", x=3.2, y=9.3, z=0.03, cap="water")
    P.barrel(b, 0.75, 9.3, 0.03)
    P.barrel(b, 1.45, 9.35, 0.03)
    P.barrel(b, 1.1, 9.3, 0.83, r=0.26, h=0.7)
    P.crate(b, -4.3, 7.75, 0.03, s=0.6, rz=10)
    P.sack(b, -3.5, 7.7, 0.03)
    # --- the street
    P.bench(b, -0.65, YG - 0.22, 0, w=1.6)
    P.barrel(b, 0.3, 0.45, 0)
    with b.at(-4.72, 0.62, 0):
        b.stone(0.62, 0.5, 0.46, mat="ashlar", col="grey", lod=1)
    Q.cat(b, -0.2, YG - 0.24, 0.48, rz=15, col="#2f2c2a")
