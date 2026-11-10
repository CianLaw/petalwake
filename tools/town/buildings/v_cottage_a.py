# Sod Cottage: the oldest roof in Cairnwick, and old Ishbel will tell you the sheep have been mowing it since
# before the signal tower was built. Low battered walls of mossy rubble, a turf roof held by eave logs and
# stitched with daisies, a byre-end lean-to and a kale yard behind. Moss stone, green turf, mustard paint.
from kit import *
import parts as P
import parts_v as V
import parts_c as PC
import parts_f as PF

META = {"name": "Sod Cottage", "kind": "house", "lot": (6.0, 7.0), "wobble": 0.055}


def build(b):
    ac = "mustard"
    b.footprint(-2.9, 0.0, 2.9, 6.9, 1.9)
    c = V.BBody(b, 5.4, 4.3, 1.9, col="moss", batter=0.085, depth=0.5)
    V.footing(c, h=0.42, boulders="f", size=(0.6, 1.0))
    V.door(c.front, 1.95, w=0.88, h=1.52, col=ac, lintel="timber")
    V.window(c.front, 3.95, 0.8, w=0.6, h=0.68, col=ac, shut="open")
    V.window(c.front, 0.72, 0.8, w=0.45, h=0.52, col=ac, shut="one")
    V.window(c.left, 2.15, 0.85, w=0.5, h=0.6)
    V.window(c.right, 2.15, 2.25, w=0.42, h=0.48, lintel="timber")
    V.window(c.back, 4.4, 0.85, w=0.5, h=0.6)
    V.rubble(c.front, n=10, size=(0.34, 0.7)); V.rubble(c.back, n=10, size=(0.34, 0.7)); V.rubble(c.left, n=8); V.rubble(c.right, n=8)
    rf = c.gable(ridge="x", pitch=34, mat="thatch", col=V.TURF, thick=0.3, course=0.9, lip=0.03, eave=0.36, verge=0.2, ridge_roll=False,
                 barge_col="darkoak", soffit_col="greyoak")
    V.eave_logs(rf)
    V.tufts(rf, n=30, flowers=0.3)
    V.chimney(b, -2.05, 2.15, 2.3, 2.35, w=0.9, d=0.72, col="moss")
    PC.cat(b, 0.9, 2.15, 1.9 + rf.rise + 0.06, rz=160, col="#3d3632")
    # the lean-to at the byre end, turfed too
    ln = V.BBody(b, 2.9, 1.7, 1.45, col="moss", x=-1.15, y=4.3 + 0.75, batter=0.07, depth=0.36)
    V.footing(ln, h=0.3, boulders="")
    V.door(ln.back, 1.0, w=0.8, h=1.2, col=ac, half=True, step=False, lintel="timber")
    r2 = ln.shed(pitch=20, high="front", mat="thatch", col=V.TURF_DRY, thick=0.26, course=0.9, lip=0.03, eave=0.26, verge=0.2, soffit_col="greyoak")
    V.tufts(r2, n=10, ridge=False)
    # the kale yard
    V.drystone(b, [(0.75, 6.55), (2.55, 6.55), (2.55, 4.5)], h=0.9, t=0.45, col="moss")
    PF.veg_row(b, (1.0, 5.0), (2.1, 5.0), kind="cabbage")
    PF.veg_row(b, (1.0, 5.7), (2.1, 5.7), kind="cabbage")
    # by the door
    P.bench(b, 1.25, -0.48, w=1.3)
    PF.tool(b, -1.6, -0.12, 0, kind="scythe")
    V.bucket(b, -0.05, -0.45, 0, water=True)
    V.peat_stack(b, -2.0, -0.5, w=1.0, d=0.6, h=0.75, turf=False, loose=3)
