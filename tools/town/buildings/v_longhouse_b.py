# Hallan longhouse: rebuilt in slate after the great gale took the thatch; the house end was given a second
# hearth and a coat of lime, the byre end left as it was, lower and darker. Two roofs stepping down, people to
# the right and beasts to the left. Grey and dark rubble, weighted slates, teal paint.
from kit import *
import parts as P
import parts_v as V
import parts_h as PH
import parts_f as PF

META = {"name": "Hallan Longhouse", "kind": "house", "lot": (14.0, 6.0), "wobble": 0.045}


def build(b):
    b.footprint(-6.9, 0.0, 6.9, 5.9, 2.45)
    ac = "teal"
    # ------------------------------------------------------------------ the house end
    hs = V.BBody(b, 7.0, 5.2, 2.45, col="grey", x=3.1, batter=0.05, depth=0.44, faces={"front": ("plaster", "white")})
    V.footing(hs, boulders="f")
    V.quoins(hs, corners="r")
    V.door(hs.front, 2.3, w=0.92, h=1.85, col=ac, lamp=True)
    for u, sh in ((0.95, "one"), (4.25, "open"), (5.85, "half")):
        V.window(hs.front, u, 0.9, w=0.7, h=0.9, col=ac, shut=sh)
    V.harl(hs.front, n=12, where="both")
    V.window(hs.right, 1.3, 0.95, w=0.6, h=0.8); V.window(hs.right, 2.6, 3.0, w=0.5, h=0.6)
    V.window(hs.back, 1.6, 0.95, w=0.6, h=0.8); V.window(hs.back, 4.9, 0.95, w=0.6, h=0.8)
    V.rubble(hs.right, n=10); V.rubble(hs.back, n=12)
    rf = hs.gable(ridge="x", pitch=44, skew=True, mat="slate", apex=None, eave=0.3)
    V.weights(rf, rows=(0.35, 1.6), every=0.9)
    RZ = 2.45 + rf.rise
    V.chimney(b, 6.05, 2.6, RZ - 0.9, 2.3, w=0.85, d=0.66, cap="pots", pots=2)
    V.chimney(b, 0.2, 2.6, RZ - 0.9, 2.1, w=0.85, d=0.66, cap="slab")
    # ------------------------------------------------------------------ the byre end: lower, darker, a step back
    by = V.BBody(b, 6.5, 4.8, 1.95, col="dark", x=-3.35, y=0.25 + 2.4, batter=0.06, depth=0.44)
    V.footing(by, boulders="f")
    V.quoins(by, corners="f", col="grey")
    V.door(by.front, 3.3, w=1.5, h=1.6, col=ac, double=True, lintel="timber")
    V.slit(by.front, 1.3, 0.8, h=0.55); V.slit(by.front, 5.3, 0.8, h=0.55)
    V.door(by.left, 2.4, w=0.8, h=1.15, z=1.55, col=ac, step=False, jambs=False, lintel="timber")       # the hay door in the gable
    V.slit(by.back, 1.6, 0.8, h=0.55); V.slit(by.back, 4.6, 0.8, h=0.55)
    V.rubble(by.front, n=10); V.rubble(by.back, n=12); V.rubble(by.left, n=8)
    r2 = by.gable(ridge="x", pitch=42, skew=True, mat="slate", col="#dfe6da", eave=0.3)
    V.weights(r2, rows=(0.35,), every=0.8, ridge=True)
    PH.cat(b, -3.0, 0.25 + 2.4, 1.95 + r2.rise + 0.14, rz=20)
    # ------------------------------------------------------------------ life
    with b.at(-5.9, -0.45, 0):
        V.trough(b, w=1.3, d=0.58, h=0.48, col="dark")
    V.churn(b, -1.95, -0.05); V.churn(b, -1.6, -0.3, h=0.55)
    PF.tool(b, -4.75, 0.12, 0, kind="fork")
    PF.hay(b, -1.15, 0.0, 0, rx=0.55, h=0.6)
    P.bench(b, 5.2, -0.48, w=1.4)
    PH.floats(hs.front, 3.35, 1.9, n=4)
    V.peat_stack(b, 3.6, 5.5, w=2.2, d=0.6, h=0.95, loose=0)
    V.rain_barrel(b, -0.45, 5.35, r=0.3, h=0.85)
