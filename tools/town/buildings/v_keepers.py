# Keepers' Row: built by the harbour board for the three keepers of the signal fire, who have painted their
# doors different colours ever since so that nobody comes home to the wrong one in a fog. Three cottages under
# one long weighted slate roof, sculleries behind. Lime-washed front on grey rubble; red, mustard and navy doors.
from kit import *
import parts as P
import parts_v as V
import parts_h as PH

META = {"name": "Keepers' Row", "kind": "house", "lot": (15.0, 6.0), "wobble": 0.045}


def build(b):
    W, D, H, BT = 14.2, 4.6, 2.25, 0.055
    r = V.BBody(b, W, D, H, col="grey", batter=BT, depth=0.42, faces={"front": ("plaster", "white")})
    b.footprint(-7.4, 0.0, 7.4, 5.9, H)
    V.footing(r, boulders="f")
    V.quoins(r, corners="fr")
    # ------------------------------------------------------------------ three doors, three colours
    homes = ((2.3, 0.95, 3.7, "red"), (7.1, 5.7, 8.5, "mustard"), (11.9, 10.5, 13.25, "navy"))
    for i, (ud, ua, ub, c) in enumerate(homes):
        V.door(r.front, ud, w=0.9, h=1.74, col=c, half=(i == 0), lamp=(i == 2))
        V.window(r.front, ua, 0.85, w=0.66, h=0.85, col=c, shut=("open", "half", "one")[i])
        V.window(r.front, ub, 0.85, w=0.66, h=0.85, col=c, shut=("one", "open", "open")[i])
    V.harl(r.front, n=16, where="both")
    V.window(r.left, 2.3, 0.9, w=0.55, h=0.75); V.window(r.right, 2.3, 0.9, w=0.55, h=0.75)
    V.rubble(r.left, n=8); V.rubble(r.right, n=8)
    V.door(r.back, 11.9, w=0.85, h=1.75, col="red", step=False)
    V.window(r.back, 13.2, 0.9, w=0.55, h=0.75)
    V.rubble(r.back, n=10, u0=9.0)
    rf = r.gable(ridge="x", pitch=43, skew=True, mat="slate", eave=0.3)
    V.weights(rf, rows=(0.35, 1.45), every=0.9)
    RZ = H + rf.rise
    V.chimney(b, -6.2, D / 2, RZ - 1.0, 2.35, w=0.85, d=0.66, cap="slab")
    V.chimney(b, -2.35, D / 2, RZ - 0.8, 2.1, w=0.95, d=0.66, cap="pots", pots=2)
    V.chimney(b, 2.4, D / 2, RZ - 0.8, 2.2, w=0.95, d=0.66, cap="pots", pots=2)
    PH.gull(b, 6.3, D / 2, RZ + 0.16, rz=120)
    # ------------------------------------------------------------------ the sculleries behind two of them, a drying green behind the third
    s = V.BBody(b, 6.4, 1.2, 1.85, col="dark", x=3.75, y=D + 0.44, batter=0.04, depth=0.32)
    V.footing(s, h=0.3, boulders="")
    V.door(s.back, 1.6, w=0.8, h=1.5, col="navy", step=False, lintel="timber")
    V.door(s.back, 4.8, w=0.8, h=1.5, col="mustard", step=False, half=True, lintel="timber")
    V.slit(s.back, 3.2, 0.9, h=0.5)
    r2 = s.shed(pitch=24, high="front", mat="slate", eave=0.2, verge=0.16)
    V.weights(r2, rows=(0.3,), verges=False, every=1.0)
    for x in (-6.9, 0.35):
        V.beam(b, (x, 5.45, 0), (x, 5.45, 2.25), w=0.09, mat="timber", col="greyoak", lod=1)
    P.laundry(b, (-6.9, 5.45, 2.15), (0.35, 5.45, 2.15), n=6, sag=0.3)
    V.peat_stack(b, -2.9, 5.2, w=1.7, d=0.7, h=1.0)
    V.rain_barrel(b, 0.15, 4.95, r=0.3, h=0.85)
    # ------------------------------------------------------------------ before the doors
    P.bench(b, -5.45, -0.45, w=1.2)
    PH.basket(b, -4.15, -0.4, 0, r=0.26, h=0.3, fill=V.PEAT)
    PH.cat(b, 0.55, -0.5, 0.0, rz=200)
    P.bench(b, 2.75, -0.45, w=1.1, rz=3)
    V.creel(b, 5.6, -0.45, rz=10); V.creel(b, 6.25, -0.5, rz=-14); V.creel(b, 5.95, -0.45, z=0.25, rz=4)
    PH.floats(r.front, 12.6, 1.95, n=4)
    V.oars(b, 6.5, 0.0, 0, h=2.45, lean=0.5, top=-0.38)
