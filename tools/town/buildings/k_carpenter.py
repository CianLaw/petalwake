# The carpenter's shop: he shows his trade on his own house (boarded below, close-framed above, a shingled roof he split himself) and works in the open lean-to beside it among his seasoning boards.
# A narrow jettied gable-fronted house, an open lean-to on oak posts along its right side with the saw-horse, bench and stacked timber under it, and a yard of logs behind.
# Honey-coloured boards on a rubble footing, sage plaster in dark oak framing, grey shingles; accent green.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_k as K

META = {"name": "The Carpenter's Shop", "kind": "workshop", "lot": (7.5, 9.0)}

HX, HW, HD = -1.2, 4.2, 6.6             # the house: x -3.3 .. 0.9
RX = HX + HW / 2                         # its right wall, which the lean-to leans on


def build(b):
    b.footprint(-3.55, 0.0, 3.6, 8.85, 7.4)
    # ------------------------------------------------------------------ the house
    g = b.body(HW, HD, 2.6, mat="planks", col="#c9a77a", x=HX)
    P.plinth(g, h=0.5)
    for wl in (g.front, g.left, g.back):
        PH.battens(wl, z0=0.5)
    up = b.body(HW, HD + 0.35, 2.3, mat="plaster", col="sage", x=HX, y=(HD - 0.35) / 2, z=2.6, floor="planks")
    PM.joists(g.front, 2.6, out=0.35)
    PM.half_door(g.front, 3.25, w=1.0, h=2.0, z=0.17, col="green")
    P.window(g.front, 1.35, 0.95, w=1.6, h=1.25, bars=(3, 1), frame="green", lintel="timber")
    P.window(up.front, 1.1, 0.85, shutters="green", box=True)
    P.window(up.front, 3.1, 0.85, shutters="green")
    P.timber_frame(up.front, posts=[0.0, 0.55, 1.65, 2.55, 3.65, HW], rails=[0.07, 0.72, 2.22],
                   braces=[(0.08, 0.12, 0.5, 0.68), (HW - 0.08, 0.12, HW - 0.5, 0.68), (1.7, 0.12, 2.1, 0.68), (2.5, 0.12, 2.1, 0.68)])
    K.sign(up.front, 2.1, 1.75, emblem="saw", col="green")
    P.door(g.right, 3.0, w=1.3, h=2.1, z=0.1, col="green", double=True, frame="timber")
    P.window(up.right, 2.4, 1.0, w=0.8, h=1.05)
    P.window(up.right, 5.1, 1.0, w=0.8, h=1.05)
    P.timber_frame(up.right, posts=[0.0, 1.85, 2.95, 4.55, 5.65, HD + 0.35], rails=[0.07, 0.86, 2.22], braces=None)
    P.window(g.left, 2.2, 0.95, w=0.8, h=1.2, frame="green")
    P.window(g.left, 4.6, 0.95, w=0.8, h=1.2, frame="green")
    P.timber_frame(up.left, posts=[0.0, 1.4, 2.8, 4.15, 5.55, HD + 0.35], rails=[0.07, 1.15, 2.22], braces="k")
    P.door(g.back, 1.2, w=0.9, h=1.95, z=0.12, col="green", frame="timber")
    P.window(g.back, 3.1, 0.95, w=0.8, h=1.2, frame="green")
    P.window(up.back, 2.1, 0.85, shutters="green")
    P.timber_frame(up.back, posts=[0.0, 1.5, 2.7, HW], rails=[0.07, 0.72, 2.22], braces=None)
    up.gable(ridge="y", pitch=50, mat="shingle", sag=0.08, eave=0.2, verge=0.35)
    PH.cuttable(up.front, up.back)
    P.window(up.front, HW / 2, 2.75, w=0.7, h=0.95, arch=0.3, frame="green")
    P.chimney(b, HX - 1.2, 4.7, 5.2, 2.9, mat="masonry", col="warm", pots=1)
    P.bench(b, -2.2, -0.5, 0, w=1.3, rz=4, col="#e0c79c")

    # ------------------------------------------------------------------ the open lean-to
    fl = K.yard(b, RX, 0.3, 3.6, 8.85, mat="cobble")
    K.yard(b, -3.6, HD, RX, 8.85, mat="cobble")
    rise = PM.lean_to(b, 5.6, 2.4, pitch=16, x=RX, y=3.6, z=2.45, face=90, mat="shingle", eave=0.16, verge=0.2)
    for yy in (1.0, 3.6, 6.2):
        b.beam((3.2, yy, fl), (3.2, yy, 2.42), w=0.2, lod=0)
    b.beam((3.2, 0.8, 2.36), (3.2, 6.4, 2.36), w=0.18, h=0.2, lod=0)
    with b.detail(1):
        for yy in (1.0, 3.6, 6.2):
            b.beam((3.2, yy, 2.3), (RX, yy, 2.3 + rise * 0.95), w=0.12, h=0.14, caps=False)
            for sy in (-1, 1):
                if 0.9 < yy + sy * 0.7 < 6.3:
                    b.beam((3.2, yy, 1.65), (3.2, yy + sy * 0.7, 2.3), w=0.1, caps=False)
    K.sawhorse(b, 2.05, 1.85, fl, rz=0)
    K.workbench(b, RX + 0.42, 5.3, fl, rz=90, w=1.6)
    K.plank_stack(b, 2.62, 4.75, fl, L=2.8, w=0.95, layers=7)
    K.leaning_planks(b, RX + 0.05, 1.35, fl, n=4, h=2.2, rz=90)
    with b.at(2.95, 0.62, fl + 0.56, rz=0):
        with b.at(rx=-10):
            K.cart_wheel(b, r=0.55, tyre=None, col="#c9ad82")

    # ------------------------------------------------------------------ the log yard behind
    K.log_pile(b, -1.5, 7.75, fl, L=3.0, n=5, rz=90)
    K.log_pile(b, 2.3, 7.9, fl, L=1.8, n=3, rz=90, r=0.2)
    with b.at(0.15, HD + 0.02, fl, rz=180):
        P.ladder(b, 3.4)
    PC.cat(b, -1.0, 7.75, fl + 1.4, rz=170)
