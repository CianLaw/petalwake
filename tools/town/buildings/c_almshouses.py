# The Four Widows' Almshouses: four doors, four hearths, one roof, endowed by a ship-owner whose four ships all came home. Each tenant whitens her own doorstep on Saturdays, and they share the pump and the bell.
# Massing: one long low range under a single sagging roof, the two end dwellings stepping forward under small gables; four doors, four tall brick stacks standing on the ridge, two little dormers, a bell-cote in the middle, washing behind.
# Materials: warm stone foot, cream limewash with the stones showing through, mossy tiles, brick stacks. Accent: blue.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Four Widows' Almshouses", "kind": "almshouses", "lot": (14.0, 6.0)}

W, Y0, Y1, H = 12.9, 0.95, 5.15, 3.1
D, CY = Y1 - Y0, (Y0 + Y1) / 2
PWD, PY0 = 2.9, 0.42                              # the end pavilions: width, front
PITCH = 48


def build(b):
    bd = b.body(W, D, H, mat="plaster", col="cream", x=0, y=CY)
    PC.plinth(bd, h=0.75, out=0.08, doors=[("front", 4.35, 0.85), ("front", 8.55, 0.85), ("back", 3.2, 0.8), ("back", 9.7, 0.8)])
    rise = bd.gable(ridge="x", pitch=PITCH, mat="tiles", col="#f2f0dc", eave=0.4, verge=0.15, sag=0.16)
    f, k = bd.front, bd.back
    # the two middle dwellings
    P.door(f, 4.35, w=0.85, h=1.9, col="blue", z=0.22, steps=1, frame="timber", lamp=True)
    P.window(f, 5.6, 1.0, w=0.75, h=1.05, shutters="blue", box=True)
    P.window(f, 7.3, 1.0, w=0.75, h=1.05, shutters="blue", box=True)
    P.door(f, 8.55, w=0.85, h=1.9, col="blue", z=0.22, steps=1, frame="timber", lamp=True)
    P.exposed(f, "base", n=10)
    for x in (-1.55, 1.55):
        P.dormer(b, x, Y0 + 0.7, H + 0.55, w=0.95, h=0.85, depth=1.3, face=0, col="cream", shutters=None)
    # the back: small windows, two back doors, the washing
    for u in (1.4, 5.0, 7.9, 11.5):
        P.window(k, u, 1.1, w=0.65, h=0.95, lintel="timber")
    P.door(k, 3.2, w=0.8, h=1.85, col="blue", z=0.15, frame="timber")
    P.door(k, 9.7, w=0.8, h=1.85, col="blue", z=0.15, frame="timber")
    P.exposed(k, "both", n=12)
    P.window(bd.left, D / 2, 1.1, w=0.65, h=0.95, lintel="timber")
    P.window(bd.right, D / 2, 1.1, w=0.65, h=0.95, lintel="timber")
    P.ivy(bd.right, 3.4, 0.3, w=1.4, h=2.6, n=6)
    for sx in (-1, 1):
        pavilion(b, sx)
    # four stacks on the ridge, one to each hearth, and the bell between
    for i, x in enumerate((-4.95, -1.75, 1.75, 4.95)):
        PC.stack(b, x, CY, H + rise - 0.75, 3.0 + 0.25 * (i % 2), w=0.72, d=0.56, flues=2, style="diagonal" if i in (0, 3) else "square")
    bellcote(b, 0.0, CY, H + rise - 0.2)
    garden(b)


def pavilion(b, sx):
    """An end dwelling: steps forward under its own gable."""
    cx = sx * (W / 2 - PWD / 2)
    d = Y0 + 1.2 - PY0
    pv = b.body(PWD, d, H, mat="plaster", col="cream", x=cx, y=PY0 + d / 2)
    PC.plinth(pv, h=0.75, out=0.08, doors=[("front", 0.85 if sx < 0 else PWD - 0.85, 0.85)])
    du, wu = (0.85, 2.05) if sx < 0 else (PWD - 0.85, PWD - 2.05)
    P.door(pv.front, du, w=0.85, h=1.9, col="blue", z=0.22, steps=1, frame="timber", lamp=True)
    P.window(pv.front, wu, 1.0, w=0.75, h=1.05, shutters="blue", box=sx < 0)
    PC.oculus(pv.front, PWD / 2, H + 0.75, r=0.27)
    P.exposed(pv.front, "corners", n=6)
    side = pv.left if sx < 0 else pv.right
    P.window(side, d / 2, 1.1, w=0.5, h=0.9, lintel="timber")
    pv.gable(ridge="y", pitch=50, mat="tiles", col="#f2f0dc", eave=0.3, verge=0.1, barge=False, sag=0.0)
    with pv.front.on(0, H):                           # plain barge boards, tight to the gable (the lot is close)
        rz = PWD / 2 * math.tan(rad(50))
        for (xa, xb) in ((-0.06, PWD / 2), (PWD + 0.06, PWD / 2)):
            b.beam((xa, -0.13, -0.1), (xb, -0.13, rz + 0.02), w=0.05, h=0.2, mat="planks", col="darkoak", lod=1, up=(0, 1, 0))


def bellcote(b, x, y, z):
    with b.at(x, y, z):
        with b.detail(1):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    b.beam((sx * 0.3, sy * 0.3, 0), (sx * 0.3, sy * 0.3, 1.25), w=0.1)
            b.box(0.86, 0.86, 0.1, "timber", col="darkoak", z=1.2, bottom=True)
        b.loop_roof(0.8, 0.8, pitch=58, mat="tiles", col="#f2f0dc", z=1.3, eave=0.16, course=0.3, thick=0.07, lod=1)
        P.bell(b, 0, 0, 1.12, r=0.2, beam=0.7)
        PC.dove(b, 0.34, 0.1, 1.31, rz=120)


def garden(b):
    """Front: beds, benches, the shared pump. Back: the drying ground."""
    with b.at(0, 0.35, 0):                             # the pump and its trough
        with b.detail(1):
            b.beam((0, 0, 0), (0, 0, 1.35), w=0.16, col="greyoak")
            b.beam((0, 0, 1.15), (0.5, 0, 0.95), w=0.05, mat="metal", col="iron")
            b.beam((0, -0.06, 1.05), (0, -0.4, 0.9), w=0.07, mat="metal", col="iron")
            b.box(1.0, 0.5, 0.42, "ashlar", col="grey", x=0, y=-0.42, z=0, top=False)
            b.box(0.8, 0.3, 0.02, "water", col="#9fd3d6", x=0, y=-0.42, z=0.34)
        b.box(1.0, 0.5, 3.0, "ashlar", col=shade("grey", 0.8), x=0, y=-0.42, z=-3.0, top=False)
    P.bench(b, -2.3, 0.55, w=1.3); P.bench(b, 2.3, 0.55, w=1.3)
    PC.cat(b, 2.55, 0.52, 0.48, rz=-20)
    with b.detail(2):                                 # the founder's tablet between the middle doors
        b.box(0.7, 0.07, 0.5, "ashlar", col="stone", x=0, y=Y0 - 0.03, z=2.05, bottom=True)
        b.box(0.86, 0.1, 0.08, "ashlar", col="sand", x=0, y=Y0 - 0.04, z=2.55, bottom=True)
    for x in (-3.3, -1.1, 1.1, 3.3):
        PC.flowers(b, x, 0.72, 0, w=0.7, d=0.3, n=3)
    P.planter(b, -5.9, 0.1, w=0.5, bush=True); P.planter(b, 4.15, 0.1, w=0.5, bush=True)
    P.barrel(b, -3.9, 0.75, r=0.25, h=0.7)
    with b.detail(1):
        for x in (-4.4, 0.0, 4.4):
            b.beam((x, 5.72, 0), (x, 5.72, 2.1), w=0.09, col="greyoak")
            b.beam((x - 0.3, 5.72, 2.0), (x + 0.3, 5.72, 2.0), w=0.06, col="greyoak")
    P.laundry(b, (-4.4, 5.72, 2.02), (0.0, 5.72, 2.02), n=6, sag=0.25)
    P.laundry(b, (0.0, 5.72, 2.02), (4.4, 5.72, 2.02), n=5, sag=0.25)
    P.crate(b, 5.6, 5.55, s=0.5, rz=10); P.sack(b, 6.05, 5.5, r=0.24); P.barrel(b, -5.9, 5.6, r=0.26, h=0.7)
