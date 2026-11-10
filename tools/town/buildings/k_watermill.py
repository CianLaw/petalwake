# The watermill on the mill stream: the leat runs down its left side through a sluice and turns a breast-shot wheel against the gable; sacks go up by the hoist in the lucam, and the miller's kitchen leans on the other gable.
# A tall two-storey rubble mill house with a deep tiled roof, a boarded lucam jutting from the front slope over stacked loading doors, the big wheel in a stone race on the left, a low lean-to with a tall brick stack on the right.
# Warm rubble with pale quoins, weathered boards, terracotta tiles; accent blue.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_k as K

META = {"name": "The Watermill", "kind": "mill", "lot": (11.0, 9.0)}

WX, WY, WZ = -4.5, 3.8, 2.7          # the wheel's centre


def build(b):
    b.footprint(-5.38, 0.0, 5.35, 8.85, 9.0)
    # ------------------------------------------------------------------ the mill house
    bd = b.body(6.4, 7.6, 5.4, mat="masonry", col="warm", x=-0.75)
    P.plinth(bd, h=0.7, out=0.08)
    P.quoins(bd, z0=0.7, col="sand")
    for wl in bd.walls:
        P.stones(wl, n=10, z0=0.8, z1=5.0)
    P.door(bd.front, 1.75, w=1.9, h=2.6, arch=0.7, col="blue", double=True, lamp=True)
    PH.loading_door(bd.front, 1.75, 2.95, w=1.2, h=1.7, col="blue")
    for u in (4.2, 5.6):
        P.window(bd.front, u, 1.1, shutters="blue", box=(u > 5))
        P.window(bd.front, u, 3.2, shutters="blue")
    K.sign(bd.front, 3.25, 3.0, emblem="wheel", col="blue", shape="round")
    bd.left.opening(3.8, WZ - 0.3, 0.6, 0.6, pane="paint", pane_col=K.SOOT, depth=0.3)       # where the shaft goes in
    P.window(bd.left, 1.1, 3.3, w=0.8, h=1.1)
    P.window(bd.left, 6.7, 3.3, w=0.8, h=1.1)
    for u in (2.2, 5.3):
        P.window(bd.right, u, 4.05, w=0.8, h=1.1, shutters="blue")
    P.door(bd.back, 1.2, w=0.95, h=2.0, z=0.18, col="blue", steps=1)
    for u in (3.3, 5.3):
        P.window(bd.back, u, 1.1, shutters="blue")
        P.window(bd.back, u, 3.2)
    P.ivy(bd.back, 0.5, 2.4, w=1.4, h=3.0, n=8)
    rise = bd.gable(ridge="x", pitch=46, mat="tiles", sag=0.14, eave=0.4, verge=0.3)
    PH.cuttable(bd.left, bd.right)
    P.window(bd.left, 3.8, 6.2, w=0.8, h=1.2, arch=0.3, shutters="blue")
    P.window(bd.right, 3.8, 6.3, w=0.8, h=1.2, arch=0.3)
    P.dormer(b, 0.5, 6.5, 6.5, w=1.0, h=0.9, depth=1.4, face=180, roof="tiles", col="cream", frame="ivory")
    P.weathervane(b, 1.7, 3.8, 5.4 + rise - 0.12, h=1.4)

    # ------------------------------------------------------------------ the lucam: the hoist dormer over the loading doors
    lu = b.body(2.0, 2.85, 1.9, mat="planks", col="#9a8468", x=-2.2, y=0.975, z=5.25, floor="planks", foot=False)
    PH.loading_door(lu.front, 1.0, 0.1, w=1.05, h=1.45, col="blue", sill=False)
    PH.battens(lu.left)
    PH.battens(lu.right)
    lu.gable(ridge="y", pitch=42, mat="tiles", eave=0.22, verge=0.45, course=0.36, thick=0.1)
    with b.detail(1):
        for xx in (-3.05, -1.35):
            b.beam((xx, 0.02, 4.45), (xx, -0.4, 5.2), w=0.13)
            b.beam((xx, 0.02, 5.18), (xx, -0.45, 5.18), w=0.12, h=0.14)
    K.hoist(b, -2.2, -0.45, 7.52, out=0.6, face=0, rope=4.7, load="sack", brace=False, back=0.2)

    # ------------------------------------------------------------------ the miller's kitchen on the right gable
    lt = PH.leanto(b, 2.45, 3.9, 5.6, 2.6, 2.5, rz=90, pitch=26, mat="masonry", col="warm", roof="tiles", plinth=0.5)
    P.door(lt.left, 1.3, w=0.9, h=1.95, z=0.18, col="blue", steps=1)
    P.window(lt.front, 1.4, 1.0, w=0.8, h=1.1, shutters="blue", box=True)
    P.window(lt.front, 4.2, 1.0, w=0.8, h=1.1, shutters="blue")
    PM.stack(b, 3.7, 6.25, 2.3, 5.5, w=0.85, d=0.7, mat="brick", col=None, pots=2)

    # ------------------------------------------------------------------ the race: head water, sluice, wheel, tail water
    K.low_wall(b, (-5.17, 0.1), (-5.17, 6.3), h=0.9, t=0.3)
    K.low_wall(b, (-5.17, 6.3), (-5.17, 8.85), h=1.95, t=0.3)
    b.box(0.3, 1.25, 4.95, "masonry", col="warm", x=-3.8, y=8.225, z=-3.0)
    b.box(1.07, 0.3, 3.9, "masonry", col="warm", x=-4.485, y=0.25, z=-3.0)
    b.box(1.07, 0.3, 4.95, "masonry", col="warm", x=-4.485, y=8.7, z=-3.0)
    b.box(1.07, 0.3, 4.35, "masonry", col="grey", x=-4.485, y=6.45, z=-3.0)                 # the weir under the gate
    b.quad((-5.02, 0.4, 0.42), (-3.95, 0.4, 0.42), (-3.95, 6.3, 0.42), (-5.02, 6.3, 0.42), "water")
    b.quad((-5.02, 6.6, 1.62), (-3.95, 6.6, 1.62), (-3.95, 8.55, 1.62), (-5.02, 8.55, 1.62), "water")
    b.quad((-4.95, 5.2, 0.44), (-4.05, 5.2, 0.44), (-4.05, 6.3, 1.36), (-4.95, 6.3, 1.36), "water")      # the chute on to the wheel
    b.quad((-4.9, 0.405, 0.42), (-4.9, 0.405, 0.78), (-4.1, 0.405, 0.78), (-4.1, 0.405, 0.42), "paint", col=K.SOOT)
    b.quad((-4.1, 8.545, 1.62), (-4.1, 8.545, 1.88), (-4.9, 8.545, 1.88), (-4.9, 8.545, 1.62), "paint", col=K.SOOT)
    b.box(0.38, 1.0, 5.5, "masonry", col="warm", x=-5.17, y=WY, z=-3.0)                      # the pier of the outer bearing
    with b.detail(1):
        b.box(0.3, 0.55, 0.2, "timber", col="darkoak", x=-5.17, y=WY, z=2.5)
        for xx in (-4.95, -4.02):                                                          # the sluice gate
            b.beam((xx, 6.3, 1.3), (xx, 6.3, 3.25), w=0.14)
        b.beam((-5.12, 6.3, 3.2), (-3.9, 6.3, 3.2), w=0.16)
        b.box(0.8, 0.06, 1.0, "planks", col="greyoak", x=-4.485, y=6.3, z=1.55, bottom=True)
    with b.detail(2):
        b.beam((-4.485, 6.24, 2.5), (-4.485, 6.24, 3.75), w=0.05, mat="metal", col="iron")
        with b.at(-4.485, 6.18, 3.5):
            K.cart_wheel(b, r=0.24, t=0.04, spokes=4, tyre=None, seg=8)
    with b.at(WX, WY, WZ):
        with b.spin(0.07, axis=(-1, 0, 0), wind=False):
            K.waterwheel(b, r=2.3, w=0.8, axle=(0.4, 0.8))

    # ------------------------------------------------------------------ flour at the door
    with b.at(-0.55, -0.16, 0.62, rx=78):
        K.millstone(b, r=0.6)
    P.sack(b, 0.35, -0.42)
    P.sack(b, 0.85, -0.5)
    P.sack(b, 0.6, -0.42, 0.36)
    K.handcart(b, 1.75, -0.6, 0, rz=80, load="sacks")
    PC.cat(b, -5.17, 1.2, 0.93, rz=60)
