# Mill Row, the jettied one: a mill-hand's terrace cottage, the upper room pushed out over the street on its joists, a bench by the door where the old man sits to watch the lane.
# A terrace house, eaves to the street: rubble ground floor, a jettied timber-framed upper storey in sky-blue wash, a tiled roof with one gabled dormer and a stack on the party wall; blank side walls for the neighbours.
# Warm rubble, sky plaster in dark oak, tiles; accent blue.
from kit import *
import parts as P
import parts_c as PC
import parts_m as PM
import parts_k as K

META = {"name": "Mill Row (the jettied one)", "kind": "cottage", "lot": (5.5, 7.0), "terrace": True}

W, D = 5.2, 5.6


def build(b):
    b.footprint(-2.6, 0.0, 2.6, 6.8, 8.0)
    g = b.body(W, D, 2.6, mat="masonry", col="warm")
    P.plinth(g, h=0.45, out=0.04)
    for wl in (g.front, g.back):
        P.stones(wl, n=7, z0=0.5, z1=2.5)
    up = b.body(W, D + 0.3, 2.4, mat="plaster", col="sky", y=(D - 0.3) / 2, z=2.6, floor="planks")
    PM.joists(g.front, 2.6, out=0.3)
    P.door(g.front, 1.25, w=0.95, h=2.0, z=0.17, col="blue", steps=1, lamp=True)
    P.window(g.front, 3.65, 1.0, w=1.2, h=1.2, bars=(2, 1), shutters="blue")
    P.window(up.front, 1.3, 0.85, shutters="blue", box=True)
    P.window(up.front, 3.9, 0.85, shutters="blue")
    P.timber_frame(up.front, posts=[0.0, 0.75, 1.85, 3.35, 4.45, W], rails=[0.07, 0.72, 2.32],
                   braces=[(0.08, 0.12, 0.7, 0.68), (W - 0.08, 0.12, W - 0.7, 0.68), (1.9, 0.12, 2.6, 0.68), (3.3, 0.12, 2.6, 0.68)])
    P.door(g.back, 1.2, w=0.9, h=1.95, z=0.1, col="blue", frame="timber")
    P.window(g.back, 3.6, 1.0, w=1.0, h=1.2)
    P.window(up.back, 1.3, 0.85)
    P.window(up.back, 3.9, 0.85, shutters="blue")
    rise = up.gable(ridge="x", pitch=46, mat="tiles", sag=0.12, eave=0.38, verge=0.05, barge=False)
    P.dormer(b, 0.7, 0.8, 5.0 + 1.1 * math.tan(rad(46)) - 0.12, w=1.15, h=1.0, depth=1.6, face=0, roof="tiles", col="sky", frame="ivory")
    P.chimney(b, -2.2, (D - 0.3) / 2, 5.0 + rise - 1.0, 2.3, mat="brick", pots=2)
    P.bench(b, 0.9, -0.5, 0, w=1.3, rz=3)
    P.barrel(b, 2.2, -0.45)
    PC.pots(b, (0.2, -0.3, 0.0), (-0.4, -0.3, 0.0), n=3)
    P.ivy(g.back, 2.45, 0.3, w=0.7, h=2.2, n=6)
    fl = K.yard(b, -2.56, D, 2.56, 6.8, mat="flagstone", h=0.08)
    K.tub(b, 2.0, D + 0.6, fl, r=0.36, h=0.6, fill="water")
    with b.detail(1):
        b.beam((-2.3, 6.6, fl), (-2.3, 6.6, 2.7), w=0.1)
    P.laundry(b, (2.2, D + 0.05, 2.5), (-2.3, 6.6, 2.6), n=5)
    PC.cat(b, 0.9, -0.5, 0.48, rz=350)
