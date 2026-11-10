# The Skipper's: three Sinclairs have skippered the Cairnwick yole from this house, and the loft under its crow
# steps still smells of barked nets and tar. A tall gable-fronted house of warm rubble with crow-stepped gables,
# a loft door and hoist beam in the peak, the net hung out to dry. Warm stone, a cream harled front, red paint.
import math

from kit import *
import parts as P
import parts_v as V
import parts_h as PH

META = {"name": "The Skipper's", "kind": "house", "lot": (6.0, 7.0), "wobble": 0.04}


def build(b):
    ac = "red"
    b.footprint(-2.9, 0.0, 2.9, 6.9, 3.5)
    BT = 0.04
    c = V.BBody(b, 4.6, 5.7, 3.5, col="warm", batter=BT, depth=0.45, faces={"front": ("plaster", "cream")})
    V.footing(c, h=0.45, boulders="f", col=shade("warm", 0.88))
    V.quoins(c, corners="fr", col=shade("warm", 1.06))
    V.door(c.front, 1.25, w=0.92, h=1.85, col=ac, lamp=True)
    V.window(c.front, 3.3, 0.9, w=0.7, h=0.9, col=ac, shut="open")
    V.window(c.front, 1.25, 2.35, w=0.62, h=0.8, col=ac, shut="open"); V.window(c.front, 3.3, 2.35, w=0.62, h=0.8, col=ac, shut="half")
    V.door(c.front, 2.3, w=0.8, h=1.15, z=4.0, col=ac, step=False, jambs=False, lintel="timber")       # the net loft
    V.harl(c.front, n=10, where="both", col="warm")
    for wl in (c.left, c.right):
        V.window(wl, 1.5, 0.9, w=0.6, h=0.8, col=ac if wl is c.left else None, shut="one"); V.window(wl, 1.5, 2.35, w=0.55, h=0.75)
        V.window(wl, 4.2, 2.35, w=0.55, h=0.75)
        V.rubble(wl, n=12, col=shade("warm", 1.06))
    V.window(c.back, 1.2, 0.9, w=0.55, h=0.75); V.window(c.back, 3.4, 2.35, w=0.55, h=0.75)
    V.door(c.back, 3.4, w=0.85, h=1.75, col=ac, step=False)
    V.rubble(c.back, n=8, z0=2.0, col=shade("warm", 1.06))
    rise = (c.tw / 2) * math.tan(rad(52))
    rf = c.gable(ridge="y", pitch=52, mat="slate", eave=0.3, verge=-(BT * rise + 0.14), barge=False)
    V.crowsteps(c, rf, n=6, col=shade("warm", 1.04))
    V.weights(rf, rows=(0.4,), every=0.9, verges=False)
    RZ = 3.5 + rf.rise
    V.chimney(b, 0.0, 5.7 - 0.62, RZ - 0.6, 2.2, w=0.75, d=0.85, col="warm", cap="pots", pots=2)
    # the hoist in the peak, and the net out to dry
    PH.hoist(b, 0.0, BT * 5.4, 5.45, out=0.95, rz=0, drop=1.1, load="net")
    PH.net_drape(b, (-2.72, 0.55, 2.3), (-2.72, 4.6, 2.3), drop=1.5, sag=0.2)
    for y in (0.55, 4.6):
        V.beam(b, (-2.72, y, 0), (-2.72, y, 2.4), w=0.09, mat="timber", col="greyoak", lod=1)
    PH.pots(b, 1.6, 6.25, 0, rz=0, n=3)
    PH.buoy(b, -1.2, 6.3, 0, flag="red")
    P.bench(b, 0.75 + 1.25, -0.47, w=1.2)
    V.floats(b, -1.72, -0.02, 2.0, n=4)
    PH.gull(b, 0.0, 5.7 - 0.62, RZ + 2.05, rz=30)
