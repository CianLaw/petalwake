# The weavers' house: the looms stand on the top floor, where the long windows on both sides give them light all day; yarn comes in by the taking-in door in the gable, and the finished cloth is dyed and dried in the yard.
# A tall narrow three-storey house (rubble, then lilac plaster, then a jettied timber-framed loom shop under a steep roof) with an L-shaped walled dye-yard beside and behind it, strung with lines of coloured cloth.
# Warm rubble, lilac and cream plaster, dark oak, tiles; accent plum.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_k as K

META = {"name": "The Weavers' House", "kind": "workshop", "lot": (7.5, 9.0)}

HX, HW = -0.95, 4.8                 # the house: middle and width (x -3.35 .. 1.45)


def loom_windows(wl):
    """The long weavers' window and the framing round it, on a front or back wall of the loom shop."""
    PM.mullioned(wl, HW / 2, 0.72, w=3.9, h=1.15, lights=6, transoms=0, mat="planks", col="darkoak", hood=False)
    P.timber_frame(wl, z0=0.0, z1=0.7, posts=[0.0, 0.8, 1.6, 2.4, 3.2, 4.0, HW], rails=[0.07, 0.63], braces=None)
    P.timber_frame(wl, z0=1.9, z1=2.2, posts=[0.0, HW], rails=[2.12], braces=None)
    P.timber_frame(wl, posts=[0.0, HW], rails=[], braces=None)


def build(b):
    b.footprint(-3.6, 0.0, 3.6, 8.85, 10.4)
    # ------------------------------------------------------------------ the house
    g = b.body(HW, 6.0, 2.6, mat="masonry", col="warm", x=HX)
    P.plinth(g, h=0.5)
    for wl in g.walls:
        P.stones(wl, n=6, z0=0.55, z1=2.45)
    f1 = b.body(HW, 6.0, 2.4, mat="plaster", col="lilac", x=HX, z=2.6)
    up = b.body(HW, 6.6, 2.2, mat="plaster", col="cream", x=HX, y=3.0, z=5.0, floor="planks")
    P.door(g.front, 1.0, w=0.95, h=2.0, z=0.17, col="plum", steps=1, lamp=True)
    P.window(g.front, 3.2, 1.0, w=1.3, h=1.2, bars=(2, 1), shutters="plum")
    K.sign(g.front, 2.05, 2.45, emblem="shuttle", col="plum")
    P.window(f1.front, 1.2, 0.75, shutters="plum", box=True)
    P.window(f1.front, 3.5, 0.75, shutters="plum")
    P.exposed(f1.front, "corners")
    PM.joists(f1.front, 2.4, out=0.3)
    PM.joists(f1.back, 2.4, out=0.3)
    loom_windows(up.front)
    loom_windows(up.back)
    P.door(g.back, 1.2, w=0.9, h=1.95, z=0.12, col="plum", frame="timber")
    P.window(g.back, 3.4, 1.0)
    P.window(f1.back, 1.3, 0.75)
    P.window(f1.back, 3.5, 0.75, shutters="plum")
    P.window(g.right, 1.6, 1.0, shutters="plum")
    P.door(g.right, 4.4, w=0.9, h=1.95, z=0.12, col="plum", frame="timber")
    P.window(f1.right, 1.9, 0.75, shutters="plum")
    P.window(f1.right, 4.3, 0.75, shutters="plum")
    PH.loading_door(up.right, 3.3, 0.1, w=1.1, h=1.7, col="plum")
    P.timber_frame(up.right, posts=[0.0, 1.5, 2.55, 4.05, 5.1, 6.6], rails=[0.07, 2.12], braces=[(0.1, 0.1, 1.45, 2.1), (6.5, 0.1, 5.15, 2.1)])
    P.window(f1.left, 3.0, 0.75, w=0.8)
    P.window(g.left, 3.0, 1.0, w=0.8)
    P.timber_frame(up.left, posts=[0.0, 2.2, 4.4, 6.6], rails=[0.07, 1.1, 2.12], braces="auto")
    rise = up.gable(ridge="x", pitch=44, mat="tiles", sag=0.12, eave=0.4, verge=0.2)
    PH.cuttable(up.left, up.right)
    PC.oculus(up.left, 3.3, 3.3, r=0.36)
    K.hoist(b, HX + HW / 2, 3.0, 7.2 + 1.05, out=1.2, face=90, rope=4.9, load="bale")
    P.chimney(b, -2.5, 5.0, 8.0, 3.3, mat="brick", pots=2)

    # ------------------------------------------------------------------ the dye-yard
    fl = K.yard(b, 1.45, 0.1, 3.6, 8.85, mat="flagstone")
    K.yard(b, -3.6, 6.0, 1.45, 8.85, mat="flagstone")
    K.gate(b, (1.65, 0.24), (3.25, 0.24), col="plum", h=1.3)
    K.low_wall(b, (3.38, 0.24), (3.38, 8.8), h=1.6, t=0.3)
    K.low_wall(b, (-3.53, 8.62), (3.53, 8.62), h=1.6, t=0.3)
    K.low_wall(b, (-3.38, 6.0), (-3.38, 8.62), h=1.6, t=0.3)
    with b.detail(1):
        for (px, py, ph) in ((2.95, 0.95, 3.75), (2.95, 8.25, 3.75), (-3.0, 7.55, 3.45), (2.25, 7.55, 3.45)):
            b.beam((px, py, fl), (px, py, ph), w=0.12)
            b.beam((px - 0.3, py, ph - 0.12), (px + 0.3, py, ph - 0.12), w=0.07, caps=False)
    K.cloth_line(b, (2.95, 0.95, 3.6), (2.95, 8.25, 3.6), n=5, drop=(1.5, 2.3), width=(0.95, 1.2), sag=0.3)
    K.cloth_line(b, (-3.0, 7.55, 3.3), (2.25, 7.55, 3.3), n=4, drop=(1.4, 2.1), width=(0.9, 1.15), sag=0.25)
    K.tub(b, 2.1, 1.7, fl, r=0.48, h=0.6, fill="#2f4f8f")
    K.tub(b, 2.05, 2.85, fl, r=0.42, h=0.55, fill="#b8433a")
    K.tub(b, -2.5, 6.75, fl, r=0.48, h=0.6, fill="#e0b23a")
    K.trough(b, 0.3, 6.45, fl, w=1.4)
    K.bucket(b, 1.15, 6.5, fl)
    P.bench(b, 1.8, 5.3, fl, w=1.3, rz=90)
    K.bolt(b, 1.8, 5.0, fl + 0.48, col="#7a4672", rz=90, L=0.8)
    K.bolt(b, 1.8, 5.45, fl + 0.48, col="#5a9a68", rz=90, L=0.8)
    K.bolt(b, 1.82, 5.22, fl + 0.68, col="#e0b23a", rz=90, L=0.8)
    PC.cat(b, 0.4, 8.62, 1.7, rz=180)
