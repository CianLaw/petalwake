# The old longhouse: the Gunns and their two cows have wintered under this one thatch for longer than the parish
# has kept books, a single door for both. Thick double drystone walls with turf growing on the wall-head, a
# rounded thatch netted with rope and hung with stones, a tarred barrel for a chimney. Dark stone, old straw, red.
from kit import *
import parts as P
import parts_v as V
import parts_h as PH
import parts_f as PF
import parts_l as PL

META = {"name": "The Old Longhouse", "kind": "house", "lot": (14.0, 6.0), "wobble": 0.055}


def build(b):
    W, D, H, BT = 13.2, 5.2, 1.75, 0.1
    h = V.BBody(b, W, D, H, col="dark", batter=BT, depth=0.62)
    b.footprint(-6.9, 0.0, 6.9, 5.9, H)
    V.footing(h, h=0.4, out=0.1, boulders="fb", size=(0.6, 1.1))
    # one door: the people turn right at the hallan, the beasts left
    V.door(h.front, 6.1, w=0.95, h=1.5, col="red")
    V.window(h.front, 8.7, 0.72, w=0.5, h=0.55, col="red", shut="one")
    V.window(h.front, 11.3, 0.72, w=0.5, h=0.55, col="red", shut="open")
    V.slit(h.front, 1.9, 0.75, h=0.5); V.slit(h.front, 3.9, 0.75, h=0.5)
    V.door(h.left, D / 2, w=1.1, h=1.42, col="red", half=True, step=False)
    V.window(h.right, D / 2, 0.72, w=0.5, h=0.55)
    V.window(h.back, 2.2, 0.72, w=0.5, h=0.55); V.slit(h.back, 9.5, 0.75, h=0.5); V.slit(h.back, 11.4, 0.75, h=0.5)
    V.rubble(h.front, n=20, size=(0.34, 0.75)); V.rubble(h.back, n=20, size=(0.34, 0.75)); V.rubble(h.left, n=6); V.rubble(h.right, n=7)
    # the turfed wall-head and the thatch that sits inside it
    V.wallhead(h, width=0.66, tufts=30)
    MZ = H + 0.2
    m = V.mound_roof(b, h.tw - 0.95, h.td - 0.95, 2.4, rc=1.5, x=0, y=D / 2, z=MZ, col="#cfc7b8", thick=0.3, courses=5, sag=0.14, bulge=1.9)
    V.mound_ropes(m, every=0.85, rows=(0.3, 0.62), rest=H - MZ + 0.03, stone_col="grey")
    V.barrel_lum(b, 3.3, D / 2 + 0.05, MZ + 2.4 - 0.42)
    PL.straw_bird(b, -2.9, D / 2, MZ + 2.4 - 0.12, rz=90)
    V.ladder(b, (-0.9, 0.16, H + 0.02), (-0.9, 2.32, MZ + 2.62), w=0.44)
    # round the door
    V.peat_stack(b, -3.3, -0.52, w=2.3, d=0.72, h=1.1)
    V.churn(b, 0.55, -0.4); V.churn(b, 0.95, -0.55, h=0.55)
    P.bench(b, 3.45, -0.48, w=1.4)
    PF.tool(b, -1.25, -0.12, 0, kind="fork")
    PF.hay(b, -5.6, -0.4, 0, rx=0.6, h=0.75)
    PH.cat(b, 5.75, -0.05 + 0.0, H + 0.02, rz=170)
