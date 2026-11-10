# The sail loft: on its one long floor a mainsail can be laid out whole; a tanned sail is always airing on the front and a bale on the hoist.
# A long stone ground floor with a cart arch, a bleached boarded loft storey with a band of windows, a gabled hoist lucam breaking
# the eaves, and a stone outside stair up the gable end. Warm rubble, pale boards, slate; accent orange (and bark-red canvas).
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "Larkhaven Sail Loft", "kind": "workshop", "lot": (12.0, 8.0)}

BOARD = paint("#d6d0c0")
CX = -0.5


def build(b):
    g = b.body(10.2, 6.4, 3.0, mat="masonry", col="warm", x=CX)                                       # x -5.7 .. 4.5, y 0 .. 6.4
    up = b.body(10.4, 6.6, 2.6, mat="planks", col=BOARD, x=CX, y=3.2, z=3.0, floor="planks", depth=0.14)      # x -5.8 .. 4.6
    H.cuttable(up.left, up.right)
    RISE = 3.3 * math.tan(rad(42))
    # ------------------------------------------------------------------ the front
    P.window(g.front, 1.1, 1.1, w=0.9, h=1.1, lintel="stone")
    P.door(g.front, 3.4, w=2.4, h=2.75, arch=0.8, col="orange", frame="stone", double=True, z=0.05)
    for u in (6.3, 7.9):
        P.window(g.front, u, 1.1, w=1.0, h=1.15, bars=(2, 1), lintel="stone")
    P.door(g.front, 9.3, w=0.95, h=2.05, col="orange", frame="timber", steps=1, z=0.15, lamp=True)
    H.loading_door(up.front, 3.5, 0.05, w=2.0, h=1.95, col="orange")
    for u in (0.9, 1.85, 5.3, 9.5):
        P.window(up.front, u, 1.0, w=0.8, h=1.05, lintel=None)
    for u in (6.4, 7.6, 8.5):
        P.window(up.front, u, 1.0, w=0.8, h=1.05, lintel=None)
        H.near_only(up.front)
    # ------------------------------------------------------------------ the hoist lucam
    LX = CX - 1.7
    lb = b.body(2.5, 0.8, 1.5, mat="planks", col=BOARD, x=LX, y=-0.5, z=5.05, floor="planks", foot=False, depth=0.12)    # y -0.9 .. -0.1
    lb.back.done = True
    lr = 1.25 * math.tan(rad(42))
    lb.front.gable = lr - 0.03
    H.cuttable(lb.front)
    H.loading_door(lb.front, 1.25, 0.12, w=1.1, h=1.2, col="orange", sill=False, bar=False)
    H.battens(lb.front, col=BOARD, z1=1.5 + lr)
    b.gable_roof(2.5, 3.3, pitch=42, mat="slate", x=LX, y=0.75, z=6.55, ridge="y", eave=0.18, verge=0.16, course=0.36, thick=0.1)
    with b.detail(1):
        for sx in (-1, 1):
            b.beam((LX + sx * 1.1, -0.1, 4.15), (LX + sx * 1.1, -0.86, 5.0), w=0.12, mat="timber", col="darkoak")
    H.hoist(b, LX, -0.9, 7.2, out=0.3, load="bale", drop=3.0, brace=False, back=0.5)
    # ------------------------------------------------------------------ ends and back
    P.door(g.left, 3.2, w=1.0, h=2.0, col="orange", frame="timber", z=0.08)
    P.window(g.left, 5.3, 1.1, w=0.8, h=1.0, lintel="stone")
    for u in (1.9, 4.7):
        P.window(up.left, u, 1.0, w=0.8, h=1.05, lintel=None)
    P.window(up.left, 3.3, 2.6 + 0.8, w=0.65, h=0.9, lintel=None, arch=0.3)
    P.window(g.right, 1.3, 1.7, w=0.7, h=0.8, lintel="stone")
    P.door(up.right, 5.9, w=0.85, h=1.95, z=0.04, col="orange", frame="timber", porch="flat")
    P.window(up.right, 2.4, 1.0, w=0.8, h=1.05, lintel=None)
    P.window(up.right, 3.3, 2.6 + 0.8, w=0.65, h=0.9, lintel=None, arch=0.3)
    P.door(g.back, 2.2, w=1.0, h=2.0, col="orange", frame="timber", z=0.08)
    for u in (4.6, 7.4):
        H.hatch(g.back, u, 1.3, w=0.8, h=0.8, col="orange")
    for u in (1.4, 3.9, 6.5, 9.0):
        P.window(up.back, u, 1.0, w=0.8, h=1.05, lintel=None)
    P.plinth(g, h=0.45)
    P.quoins(g, corners="fl", z0=0.45, col="sand")
    for wl in (up.front, up.back):
        H.battens(wl, col=BOARD, step=0.5, rails=(0.07,))
    for wl in (up.left, up.right):
        H.battens(wl, col=BOARD, step=0.5, z1=2.6 + RISE, rails=(0.07, 2.6))
    P.ivy(g.left, 0.9, 0.2, w=1.6, h=2.6, n=7)
    # ------------------------------------------------------------------ the roof
    up.gable(ridge="x", pitch=42, mat="slate", eave=0.4, verge=0.2, sag=0.18)
    P.chimney(b, CX - 4.3, 3.3, 7.4, 2.6, w=0.7, d=0.6, mat="masonry", col="warm", pots=2)
    H.gull(b, 0.4, 3.2, 5.6 + RISE - 0.02, rz=300)
    H.gull(b, 1.1, 3.2, 5.6 + RISE - 0.02, rz=80, s=0.9)
    # ------------------------------------------------------------------ the outside stair up the gable end
    with b.at(CX + 5.72, 0.35, 0):
        PC.outside_stair(b, n=16, w=1.0, rise=0.19, run=0.3, landing=1.3, rail="balusters", rail_sides="r")
    # ------------------------------------------------------------------ a tanned sail airing, spars on trestles, canvas
    with b.detail(1):
        b.beam((0.1, -0.46, 5.0), (3.3, -0.46, 4.94), w=0.08, mat="timber", col="greyoak")
        for x in (0.5, 2.9):
            b.beam((x, -0.46, 5.0), (x, -0.3, 5.3), w=0.02, mat="cloth", col=H.ROPE, caps=False)
    H.sail(b, [(0.35, -0.46, 4.97), (3.05, -0.46, 4.92), (2.85, -0.72, 3.3), (0.7, -0.68, 3.36)], rows=5)
    with b.detail(1):
        for x in (0.0, 3.4):
            b.beam((x, -1.05, 0), (x, -0.8, 0.62), w=0.08, mat="timber", col="greyoak")
            b.beam((x, -0.45, 0), (x, -0.7, 0.62), w=0.08, mat="timber", col="greyoak")
            b.beam((x, -0.95, 0.58), (x, -0.55, 0.58), w=0.09, mat="timber", col="greyoak")
        for i, (yy, zz, r_) in enumerate(((-0.86, 0.7, 0.085), (-0.68, 0.7, 0.075), (-0.77, 0.84, 0.065))):
            b.tube((-0.6 + 0.2 * i, yy, zz), (4.1 - 0.3 * i, yy, zz + 0.02), r=r_, r1=r_ * 0.7, mat="planks", col="#d9c7a3", n=6, caps=True)
    with b.detail(2):
        for i, (x, y) in enumerate(((-4.3, -0.5), (-4.05, -0.72), (-4.5, -0.8))):
            b.tube((x, y, 0.0), (x + 0.03 * i, y, 1.25 - 0.12 * i), r=0.17, mat="cloth", col=("#e6dcc2", H.SAIL_TAN, "#d9cfb4")[i], n=7, caps=True)
    P.barrel(b, 4.0, -0.55, r=0.28, h=0.75)
    H.rope_coil(b, -0.75, -0.6, r=0.3)
