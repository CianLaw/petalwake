# The smokehouse: herring go in silver and come out gold; the two crooked stacks have never once both drawn at the same time.
# A squat stone curing floor under a tarred, louvred smoke loft with a steep sooty gable and a vented ridge; two tall brick stacks
# of different heights, a pent rack of kippers along the front and a log store behind. Grey rubble, tar, brick; accent brown and kipper-gold.
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "Larkhaven Smokehouse", "kind": "workshop", "lot": (6.0, 7.0), "lean": (0.004, 0.002)}

SOOT = "#c9b6a8"


def build(b):
    g = b.body(4.6, 5.4, 2.4, mat="masonry", col="grey")                                           # x +-2.3, y 0 .. 5.4
    up = b.body(4.7, 5.5, 2.2, mat="planks", col=H.TAR, y=2.7, z=2.4, floor="planks", depth=0.14)
    H.cuttable(up.front, up.back)
    RISE = 2.35 * math.tan(rad(50))
    # ------------------------------------------------------------------ openings: a low door, vents everywhere
    P.door(g.front, 1.1, w=1.0, h=1.95, col="brown", frame="timber", z=0.08, lamp=True)
    P.window(g.front, 3.4, 1.15, w=0.8, h=0.8, lintel="timber")
    H.louvre(up.front, 2.35, 0.45, w=1.3, h=1.25, n=6)
    H.hatch(up.front, 2.35, 2.75, w=0.7, h=0.8, col="brown")
    H.hatch(g.right, 3.7, 1.2, w=0.7, h=0.7, col="brown")
    for u in (3.3, 4.7):
        H.louvre(up.right, u, 0.6, w=0.8, h=1.0, n=5)
    P.window(g.left, 3.9, 1.15, w=0.7, h=0.8, lintel="timber")
    for u in (3.0, 4.4):
        H.louvre(up.left, u, 0.6, w=0.8, h=1.0, n=5)
    P.door(g.back, 4.0, w=0.85, h=1.85, col="brown", frame="timber", z=0.08)
    H.louvre(up.back, 2.35, 0.45, w=1.3, h=1.25, n=6)
    H.hatch(up.back, 2.35, 2.75, w=0.7, h=0.8, col="brown")
    P.plinth(g, h=0.4, col="grey")
    for wl in (up.left, up.right):
        H.battens(wl, col=H.TAR, rails=(0.07,))
    for wl in (up.front, up.back):
        H.battens(wl, col=H.TAR, z1=2.2 + RISE, rails=(0.07, 2.2))
    # ------------------------------------------------------------------ the roof and its vented ridge
    up.gable(ridge="y", pitch=50, mat="tiles", col=SOOT, eave=0.25, verge=0.3, sag=0.08)
    RZ = 4.6 + RISE
    vb = b.body(0.8, 3.0, 0.55, mat="planks", col="greyoak", x=0, y=2.9, z=RZ - 0.3, foot=False, depth=0.08)
    H.louvre(vb.left, 1.5, 0.12, w=2.5, h=0.34, n=3, depth=0.06)
    H.louvre(vb.right, 1.5, 0.12, w=2.5, h=0.34, n=3, depth=0.06)
    b.gable_roof(0.8, 3.0, pitch=36, mat="tiles", col=SOOT, x=0, y=2.9, z=RZ + 0.25, ridge="y", eave=0.2, verge=0.16, course=0.3, thick=0.08, barge=False)
    vb.front.gable = vb.back.gable = 0.4 * math.tan(rad(36)) - 0.02
    b.smoke(0, 2.9, RZ + 0.9, strength=0.8)
    # ------------------------------------------------------------------ the two stacks
    H.stack(b, -1.95, 4.15, 0.0, 10.6, w=0.95, top=0.6, mat="brick", bands=2, pots=1, smoke=1.4)
    H.stack(b, 1.95, 1.55, 0.0, 8.8, w=0.9, top=0.62, mat="brick", col="#f0e2d8", bands=1, pots=1, smoke=1.1)
    # ------------------------------------------------------------------ the kipper rack along the front
    b.gable_roof(2.9, 1.1, pitch=24, mat="shingle", x=1.0, y=0.0, z=2.02, ridge="x", half=True, eave=0.1, verge=0.08, course=0.3, thick=0.06, barge=False)
    for x in (-0.3, 2.3):
        b.beam((x, -1.0, 0.0), (x, -1.0, 2.02), w=0.11, mat="timber", col="greyoak", lod=0)
    with b.detail(1):
        b.beam((-0.45, -1.0, 1.98), (2.45, -1.0, 1.98), w=0.1, h=0.12, mat="timber", col="greyoak")
        for x in (-0.3, 2.3):
            b.beam((x, 0.0, 2.3), (x, -1.0, 1.96), w=0.08, mat="timber", col="greyoak")
    for (yy, n) in ((-0.3, 9), (-0.62, 8), (-0.92, 9)):
        H.fish_line(b, (-0.3, yy, 1.9), (2.3, yy, 1.9), n=n, col=H.SMOKED, size=0.34)
    H.fish_line(b, (2.42, 2.6, 2.05), (2.42, 5.2, 2.05), n=9, col=H.SMOKED, size=0.32)
    # ------------------------------------------------------------------ the log store and the yard
    lt = H.leanto(b, 0.55, 5.4, 3.3, 1.15, 1.7, rz=180, pitch=25, mat="planks", col=H.TAR_OLD, roof="shingle", plinth=0.3, plinth_col="grey")
    P.door(lt.front, 0.9, w=0.8, h=1.5, col="brown", frame=None, z=0.05)
    H.battens(lt.front, col=H.TAR_OLD, z0=0.3)
    H.logs(b, 1.35, 6.35, rz=90, n=3, L=1.0)
    H.logs(b, -1.75, 6.0, rz=0, n=3, L=0.9)
    P.barrel(b, -1.95, -0.55, r=0.3, h=0.82)
    P.barrel(b, -1.35, -0.95, r=0.27, h=0.74, col="#b99870")
    H.basket(b, -0.75, -0.75, r=0.3, fill=H.SMOKED)
    P.sack(b, -2.55, 1.4, r=0.3)
    P.sack(b, -2.6, 2.05, r=0.26, col="#cdbb92")
    PC.cat(b, 0.05, -0.55, 0.0, rz=60, col="!#2c2a2a")
