# The chapel of Cairnwick: one bell, rung for fog as often as for prayers; the fishermen's wives whitewash the
# porch door every spring. A narrow buttressed nave under a steep stone-slabbed roof, a bell-cote on the west
# gable, a low porch, a vestry tucked behind. Grey lichened rubble, stone slates, a navy door.
import math

from kit import *
import parts as P
import parts_v as V
import parts_c as PC
import parts_h as PH

META = {"name": "Cairnwick Chapel", "kind": "chapel", "lot": (7.0, 12.0), "wobble": 0.04}

SLAB = "#c6c9cc"


def build(b):
    b.footprint(-3.4, 0.0, 3.4, 11.8, 3.3)
    NW, ND, NH, NY, BT = 5.4, 7.8, 3.3, 1.75, 0.045
    nave = V.BBody(b, NW, ND, NH, col="grey", x=0, y=NY + ND / 2, batter=BT, depth=0.5)
    V.footing(nave, h=0.5, boulders="lr", col=shade("moss", 0.9))
    V.quoins(nave, corners="frbl", size=(0.68, 0.36, 0.5))
    for wl in (nave.left, nave.right):
        for u in (1.5, 3.9, 6.3):
            V.window(wl, u, 1.15, w=0.46, h=1.55, arch=0.23, bars=(0, 2))
        V.rubble(wl, n=12)
    for du in (-0.6, 0.6):
        V.window(nave.front, NW / 2 + du, 3.55, w=0.4, h=1.25, arch=0.2, bars=(0, 1))
    for du, hh in ((-0.8, 1.5), (0.0, 2.0), (0.8, 1.5)):
        V.window(nave.back, NW / 2 + du, 2.35, w=0.42, h=hh, arch=0.21, bars=(0, 2))
    V.rubble(nave.front, n=10, z0=2.6); V.rubble(nave.back, n=8, z0=3.0)
    rf = nave.gable(ridge="y", pitch=54, skew=True, mat="flagstone", col=SLAB, apex=None, eave=0.26, course=0.5)
    V.weights(rf, rows=(0.4,), every=1.1, verges=False)
    RZ = NH + rf.rise
    # the bell-cote on the west gable, its rope down to the porch
    by = NY + BT * RZ + 0.2
    with b.at(0, by, RZ - 0.06):
        top = V.bellcote(b, w=1.5, t=0.52, h=1.45, col=shade("grey", 1.05), bell=0.26)
    V.vane(b, 0, by, RZ - 0.06 + top - 0.08, h=1.05, kind="fish", s=0.62, arms=False)
    V.rope(b, (0.22, by - 0.3, RZ + 1.0), (0.3, NY + BT * 3.6 - 0.06, 3.5), w=0.025)
    with b.at(0, NY + ND - BT * RZ - 0.2, RZ - 0.1):
        b.stone(0.42, 0.5, 0.4, mat="masonry", col=shade("grey", 1.1), lod=1, ch=0.2)
    # buttresses between the windows
    for u in (2.7, 5.1):
        with b.at(NW / 2 - 0.02, NY + u, 0, rz=90):
            PC.buttress(b, w=0.62, d=0.62, h=2.7, mat="masonry", col="grey", cap="flagstone", cap_col="grey")
        with b.at(-NW / 2 + 0.02, NY + u, 0, rz=270):
            PC.buttress(b, w=0.62, d=0.62, h=2.7, mat="masonry", col="grey", cap="flagstone", cap_col="grey")
    # ------------------------------------------------------------------ the porch
    porch = V.BBody(b, 2.5, 1.95, 2.0, col="grey", x=0, y=0.975, batter=0.04, depth=0.42)
    V.footing(porch, h=0.4, boulders="f")
    V.door(porch.front, 1.25, w=1.05, h=1.9, col="navy", arch=0.5, lamp=True)
    V.slit(porch.left, 1.0, 0.9, w=0.15, h=0.6); V.slit(porch.right, 0.95, 0.9, w=0.15, h=0.6)
    pr = porch.gable(ridge="y", pitch=50, skew=True, mat="flagstone", col=SLAB, apex="knob", eave=0.2, course=0.45)
    # ------------------------------------------------------------------ the vestry behind
    v = V.BBody(b, 3.3, 1.75, 2.0, col="dark", x=-0.85, y=NY + ND + 0.72, batter=0.04, depth=0.36)
    V.footing(v, h=0.35, boulders="")
    V.door(v.right, 0.9, w=0.8, h=1.6, col="navy", step=False)
    V.window(v.back, 1.65, 0.9, w=0.5, h=0.7)
    V.rubble(v.back, n=6); V.rubble(v.left, n=4)
    vr = v.shed(pitch=30, high="front", mat="flagstone", col=SLAB, eave=0.22, verge=0.16, course=0.45)
    V.chimney(b, -2.05, NY + ND + 0.35, 1.9, 2.5, w=0.62, d=0.52, col="dark")
    # ------------------------------------------------------------------ the yard: low walls, old stones, a thorn
    V.drystone(b, [(-3.15, 1.75), (-3.15, 0.3), (-1.5, 0.3)], h=0.85, t=0.45)
    V.drystone(b, [(1.5, 0.3), (3.15, 0.3), (3.15, 1.75)], h=0.85, t=0.45)
    V.headstone(b, -2.35, 1.15, h=0.8, rz=6, lean=7); V.headstone(b, -1.75, 1.3, h=0.6, w=0.42, rz=-8, lean=-5)
    V.headstone(b, 2.2, 1.2, h=0.72, rz=-4, lean=9)
    with b.detail(2):
        for (x, y) in ((-2.6, 0.9), (-1.9, 0.85), (2.5, 0.85), (1.85, 1.3), (-2.7, 1.5)):
            with b.at(x, y, 0.0):
                V.tuft(b, 0.14, 0.3)
    P.tree(b, 1.95, 10.45, h=3.1, crown=0.95, col="#6f9a52")
    P.bench(b, 1.9, 9.95 + 0.25 - 0.2, w=1.2, rz=180)
