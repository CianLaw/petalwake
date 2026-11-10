# Garden Cottage: nothing is supposed to grow on this cliff, so Mairi built a wall as high as her shoulder and
# grows kale, leeks and a thorn tree behind it out of pure stubbornness, and keeps bees in the lee of it. A
# lime-washed cottage set back behind a drystone-walled garden. White harl, slate, mustard paint.
from kit import *
import parts as P
import parts_v as V
import parts_f as PF

META = {"name": "Garden Cottage", "kind": "house", "lot": (6.0, 7.0), "wobble": 0.045}


def build(b):
    ac = "mustard"
    b.footprint(-2.9, 0.0, 2.9, 6.9, 2.15)
    GY = 2.35
    c = V.BBody(b, 5.2, 4.3, 2.15, mat="plaster", col="white", x=0, y=GY + 2.15, batter=0.05, depth=0.45)
    V.footing(c, h=0.42, col="grey", boulders="f")
    V.quoins(c, corners="fr", col="grey")
    V.door(c.front, 2.0, w=0.9, h=1.66, col=ac, lamp=True)
    V.window(c.front, 0.8, 0.85, w=0.62, h=0.8, col=ac, shut="open")
    V.window(c.front, 3.85, 0.85, w=0.7, h=0.85, col=ac, shut="open")
    V.harl(c.front, n=8, where="base")
    V.window(c.left, 2.15, 0.9, w=0.55, h=0.75, col=ac, shut="one"); V.window(c.left, 2.15, 2.75, w=0.42, h=0.5)
    V.window(c.right, 2.15, 0.9, w=0.55, h=0.75)
    V.window(c.back, 1.3, 0.9, w=0.55, h=0.75); V.window(c.back, 3.9, 0.9, w=0.55, h=0.75)
    V.harl(c.left, n=7); V.harl(c.right, n=7); V.harl(c.back, n=8)
    rf = c.gable(ridge="x", pitch=45, skew=True, mat="slate", apex=None, eave=0.3, skew_col="grey")
    V.weights(rf, rows=(0.35,), every=0.85)
    RZ = 2.15 + rf.rise
    V.chimney(b, -2.05, GY + 2.15, RZ - 0.9, 2.2, w=0.85, d=0.66, cap="pots", pots=2)
    V.chimney(b, 2.05, GY + 2.15, RZ - 0.9, 2.0, w=0.8, d=0.66, cap="slab")
    # ------------------------------------------------------------------ the garden behind its wall
    V.drystone(b, [(-2.6, GY - 0.15), (-2.6, 0.3), (-1.2, 0.3)], h=1.25, t=0.5)
    V.drystone(b, [(-0.05, 0.3), (2.6, 0.3), (2.6, GY - 0.15)], h=1.25, t=0.5)
    V.gatepost(b, -1.12, 0.3, h=1.45); V.gatepost(b, -0.12, 0.3, h=1.45)
    V.gate(b, (-1.05, 0.3), (-0.2, 0.3), h=1.0, col="greyoak", ajar=28)
    with b.detail(2):
        for i in range(4):
            b.box(0.62, 0.42, 0.05, "flagstone", col=shade("grey", b.r(0.9, 1.08)), x=-0.62 + b.r(-0.05, 0.05), y=0.75 + 0.47 * i, z=0.0)
    PF.veg_row(b, (0.35, 0.95), (2.15, 0.95), kind="cabbage")
    PF.veg_row(b, (0.35, 1.5), (2.15, 1.5), kind="leek")
    PF.veg_row(b, (0.35, 2.0), (1.6, 2.0), kind="cabbage")
    P.tree(b, -1.95, 1.0, h=2.9, crown=0.72, col="#6f9a52")
    with b.detail(1):
        b.box(1.15, 0.42, 0.42, "masonry", col="grey", x=-1.85, y=1.98, z=0.0, taper=0.92)
    PF.hive(b, -2.12, 1.98, 0.42, face=0); PF.hive(b, -1.58, 1.98, 0.42, face=10, col="#ecd596")
    PF.flowers(b, -1.25, 0.75, 0.0, n=5); PF.flowers(b, 2.2, 2.05, 0.0, n=4)
    P.bench(b, 1.25, GY - 0.45, w=1.3)
    V.rain_barrel(b, -2.35, GY - 0.38, r=0.28, h=0.8)
