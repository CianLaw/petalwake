# The Lambing Hut: the shepherd's hut, towed up to the high meadow every spring; a stove, a bunk, a bottle-fed lamb by the steps.
# Massing: a narrow boarded van with a bowed roof riding high on four iron wheels, a stable door and steps at the front end, a stovepipe
#          through the roof, the drawbar folded up behind.
# Materials: sage-painted boards with ivory trim, a tarred bowed roof, black iron wheels; accent ivory.
from kit import *
import parts as P
import parts_f as F

META = {"name": "The Lambing Hut", "kind": "hut", "lot": (3.0, 5.0)}

W, L, H = 1.9, 3.5, 1.9
CY = 2.75
FLOOR = 0.82
SAGE = "#b9c9a6"


def lamb(b, x, y, rz):
    wool, dark = F._paint("#f4f0e4"), F._paint("#3a3632")
    with b.at(x, y, 0.0, rz=rz):
        with b.detail(2):
            b.blob(0.13, 0.22, 0.13, mat="paint", col=wool, z=0.34, seg=6, rings=3, rough=0.14)
            b.blob(0.075, 0.09, 0.075, mat="paint", col=wool, y=-0.24, z=0.47, seg=5, rings=2, rough=0.08)
            b.box(0.07, 0.09, 0.06, "paint", col=dark, y=-0.33, z=0.42, bottom=True)
            for (dx, dy) in ((-0.07, -0.13), (0.07, -0.13), (-0.07, 0.13), (0.07, 0.13)):
                b.beam((dx, dy, 0.0), (dx, dy, 0.26), w=0.035, mat="paint", col=dark, caps=False)
            for sx in (-1, 1):
                b.tri((sx * 0.05, -0.2, 0.52), (sx * 0.13, -0.19, 0.5), (sx * 0.06, -0.17, 0.48), "paint", col=wool)
                b.tri((sx * 0.13, -0.19, 0.5), (sx * 0.05, -0.2, 0.52), (sx * 0.06, -0.17, 0.48), "paint", col=wool)


def build(b):
    y0, y1 = CY - L / 2, CY + L / 2
    # ---- running gear: iron wheels (small in front, larger behind), axles, the frame
    for (y, r) in ((y0 + 0.75, 0.4), (y1 - 0.7, 0.5)):
        for sx in (-1, 1):
            with b.at(sx * (W / 2 + 0.12), y, r):
                F.wheel(b, r=r, w=0.1, spokes=8, mat="metal", col="iron", tyre=None, hub=0.09)
        b.beam((-W / 2 - 0.16, y, r), (W / 2 + 0.16, y, r), w=0.09, mat="metal", col="iron", lod=1)
        b.box(1.3, 0.2, FLOOR - 0.14 - r, "timber", col="darkoak", x=0, y=y, z=r, lod=1)
    for sx in (-0.6, 0.6):
        b.beam((sx, y0 + 0.05, FLOOR - 0.1), (sx, y1 - 0.05, FLOOR - 0.1), w=0.14, h=0.16, mat="timber", col="darkoak", lod=0, up=(0, 0, 1))
    for (y, r) in ((y0 + 0.75, 0.4), (y1 - 0.7, 0.5)):                # chocks
        with b.detail(2):
            b.box(0.16, 0.2, 0.12, "planks", col="greyoak", x=W / 2 + 0.12, y=y - r * 0.75, z=0.0, ty=0.4)
    b.footprint(-W / 2, y0, W / 2, y1, FLOOR)

    # ---- the van
    bd = b.body(W, L, H, mat="planks", col=SAGE, x=0, y=CY, z=FLOOR, floor="planks", foot=False)
    F.half_door(bd.front, W / 2, w=0.78, h=1.75, z=0.04, col="ivory", top="open")
    P.window(bd.left, 1.2, 0.8, w=0.6, h=0.6, frame="ivory", lintel=None, bars=(1, 1))
    P.window(bd.right, 2.2, 0.8, w=0.6, h=0.6, frame="ivory", lintel=None, bars=(1, 1))
    P.window(bd.back, W / 2, 0.85, w=0.5, h=0.5, frame="ivory", lintel=None, bars=(1, 1))
    with b.detail(1):
        for sx in (-1, 1):
            for y in (y0, y1):
                b.beam((sx * (W / 2 + 0.01), y + (0.01 if y > CY else -0.01), FLOOR), (sx * (W / 2 + 0.01), y + (0.01 if y > CY else -0.01), FLOOR + H), w=0.09, mat="planks", col="ivory", caps=False)
        b.box(W + 0.06, L + 0.06, 0.1, "planks", col="ivory", x=0, y=CY, z=FLOOR - 0.04, bottom=True)
    sec = [(0.0, 0.0), (0.28, 0.3), (0.62, 0.48), (W / 2, 0.55)]
    rise = bd.gable(ridge="y", section=sec, mat="slate", col="#c9c4c0", eave=0.12, verge=0.2, course=0.0, barge=False, thick=0.06, ridge_roll=False)
    F.stovepipe(b, -0.5, y1 - 0.75, FLOOR + H + 0.25, h=1.0, r=0.07)
    P.lantern_at(b, 0.62, y0 - 0.02, FLOOR + 1.45, arm=0.22)

    # ---- the steps up to the door, the drawbar folded up behind
    with b.at(0.0, y0 - 0.66, 0.0):
        P.stairs(b, w=0.8, rise=FLOOR / 3, run=0.22, n=3, solid=False)
    with b.detail(1):
        for sx in (-0.22, 0.22):
            b.beam((sx, y1 + 0.04, 0.45), (sx * 0.4, y1 + 0.14, 2.05), w=0.07, mat="timber", col="darkoak")
        b.beam((-0.2, y1 + 0.13, 2.0), (0.2, y1 + 0.13, 2.0), w=0.06, mat="metal", col="iron")

    # ---- the shepherd's things
    F.tool(b, 0.72, y0 - 0.06, 0.0, kind="crook", h=1.7, lean=0.04)
    lamb(b, -0.85, y0 - 0.45, 70)
    F.bucket(b, 0.7, y0 - 0.5, 0.0)
    with b.detail(2):                                   # a wattle hurdle leaning on the side
        with b.at(W / 2 + 0.3, CY + 0.2, 0.0, rz=90):
            for i in range(6):
                b.beam((-0.75 + 0.3 * i, 0.0, 0.0), (-0.75 + 0.3 * i, 0.12, 1.05), w=0.035, mat="planks", col="#a58c6c", caps=False)
            for j in range(5):
                zz = 0.15 + 0.2 * j
                F.ribbon(b, (-0.8, 0.02 * (j + 1), zz), (0.8, 0.02 * (j + 1), zz), w=0.09, mat="planks", col="#b89c78", up=(0, 1, 0))
    for (x, y) in ((-1.15, 0.5), (1.1, 4.55), (-1.1, 4.5)):
        F.flowers(b, x, y, 0.0, n=4, spread=0.22)
