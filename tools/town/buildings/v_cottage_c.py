# The Peat House: Davie Rosie cuts for half the village, and his stack along the gable is rebuilt every June
# as carefully as any wall. A low thatched cottage, its straw tucked between raised gables and roped down with
# stones, set to one side of its lot to leave room for the stack. Dark rubble, a lime-washed front, red paint.
from kit import *
import parts as P
import parts_v as V
import parts_h as PH
import parts_f as PF
import parts_l as PL

META = {"name": "The Peat House", "kind": "house", "lot": (6.0, 7.0), "wobble": 0.05}


def build(b):
    ac = "red"
    b.footprint(-2.9, 0.0, 2.9, 6.9, 2.0)
    X0 = -0.45
    c = V.BBody(b, 4.6, 4.5, 2.0, col="dark", x=X0, batter=0.07, depth=0.48, faces={"front": ("plaster", "white")})
    V.footing(c, h=0.42, boulders="f")
    V.quoins(c, corners="r", col="grey")
    V.door(c.front, 1.65, w=0.9, h=1.56, col=ac, lintel="timber")
    V.window(c.front, 3.45, 0.82, w=0.64, h=0.78, col=ac, shut="open")
    V.window(c.front, 0.62, 0.82, w=0.45, h=0.55, col=ac, shut="one")
    V.harl(c.front, n=10, where="both", col="dark")
    V.window(c.left, 2.25, 0.85, w=0.5, h=0.62)
    V.window(c.back, 1.2, 0.85, w=0.5, h=0.62); V.window(c.back, 3.3, 0.85, w=0.5, h=0.62)
    V.rubble(c.left, n=8); V.rubble(c.back, n=10); V.rubble(c.right, n=5, z0=1.6)
    rf = c.gable(ridge="x", pitch=48, skew=True, mat="thatch", col="#d2c8b6", thick=0.3, course=0.6, lip=0.05, eave=0.34, ridge_roll=False, soffit_col="greyoak")
    V.ropes(rf, every=0.92, rows=(0.42, 0.74), drop=0.24)
    V.tufts(rf, n=0, ridge=True, col="#9aa860")
    RZ = 2.0 + rf.rise
    V.chimney(b, X0 - 1.75, 2.25, RZ - 0.9, 2.2, w=0.85, d=0.68, col="dark")
    V.chimney(b, X0 + 1.8, 2.25, RZ - 0.8, 1.7, w=0.7, d=0.6, col="dark", cap="pots")
    PL.straw_bird(b, X0 + 0.3, 2.25, RZ + 0.12, rz=90)
    # ------------------------------------------------------------------ the stack along the gable, and the cutter's gear
    V.peat_stack(b, 2.24, 2.3, w=3.4, d=0.72, h=1.5, rz=90, loose=0)
    PH.basket(b, 2.3, -0.25, 0, r=0.28, h=0.32, fill=V.PEAT)
    PH.basket(b, 2.25, 0.35, 0, r=0.26, h=0.3, fill=V.PEAT)
    PF.tool(b, -2.35, -0.12, 0, kind="spade")
    P.bench(b, 0.75, -0.48, w=1.2)
    # behind: a rowan, a line of washing, a wall
    V.drystone(b, [(-2.6, 4.75), (-2.6, 6.6), (2.6, 6.6)], h=0.9, t=0.45, col="dark")
    P.tree(b, 1.55, 5.55, h=3.3, crown=0.95, col="#7da053")
    P.laundry(b, (-2.3, 4.6, 1.85), (0.9, 5.6, 2.0), n=4, sag=0.25)
