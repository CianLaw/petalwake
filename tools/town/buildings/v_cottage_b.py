# The Stair House: the Tullochs keep their nets and creels dry on the ground floor and live above them, up an
# outside stair worn hollow by four generations of sea boots. A tall narrow two-storey cottage, the forestair
# along its front to a door at the first floor, weighted slates. Grey rubble, navy paint, an iron handrail.
from kit import *
import parts as P
import parts_v as V
import parts_h as PH

META = {"name": "The Stair House", "kind": "house", "lot": (6.0, 7.0), "wobble": 0.04}


def build(b):
    ac = "navy"
    b.footprint(-2.9, 0.0, 2.9, 6.9, 3.9)
    c = V.BBody(b, 5.2, 4.6, 3.9, col="grey", batter=0.04, depth=0.45)
    V.footing(c, h=0.45, boulders="lb")
    V.quoins(c, corners="fr", size=(0.66, 0.36, 0.5))
    # the upper door at the head of the stair, the net store's half-door below
    V.door(c.front, 3.45, w=0.85, h=1.75, z=2.0, col=ac, step=False, lamp=True)
    V.door(c.front, 4.52, w=0.8, h=1.5, col=ac, half=True)
    V.window(c.front, 1.2, 2.45, w=0.62, h=0.82, col=ac, shut="open")
    V.slit(c.front, 0.75, 0.9, h=0.5)
    V.window(c.left, 2.3, 0.95, w=0.55, h=0.75, col=ac, shut="one"); V.window(c.left, 2.3, 2.45, w=0.55, h=0.75, col=ac, shut="open")
    V.window(c.right, 2.3, 2.45, w=0.5, h=0.7); V.window(c.right, 2.3, 4.75, w=0.4, h=0.5)
    V.window(c.back, 1.4, 2.45, w=0.55, h=0.75); V.window(c.back, 3.8, 2.45, w=0.55, h=0.75); V.window(c.back, 3.8, 0.95, w=0.55, h=0.75)
    V.rubble(c.front, n=10, z0=2.2); V.rubble(c.left, n=12); V.rubble(c.right, n=12); V.rubble(c.back, n=12)
    rf = c.gable(ridge="x", pitch=45, skew=True, mat="slate", apex=None, eave=0.3)
    V.weights(rf, rows=(0.35,), every=0.8)
    RZ = 3.9 + rf.rise
    V.chimney(b, 2.05, 2.3, RZ - 0.9, 2.3, w=0.85, d=0.66, cap="pots", pots=2)
    V.chimney(b, -2.1, 2.3, RZ - 0.8, 1.8, w=0.7, d=0.6, cap="slab")
    # ------------------------------------------------------------------ the forestair
    with b.at(-2.5, -0.52, 0):
        top = V.forestair(b, n=10, w=1.0, rise=0.2, run=0.27, landing=1.25, col="grey", niche=True)
        P.railing(b, [(0.0, -0.44, 0.2), (2.7, -0.44, top), (3.9, -0.44, top), (3.9, 0.42, top)], h=0.95, style="iron")
    PH.net_drape(b, (-2.5 + 2.75, -1.0, 2.0 + 0.95), (-2.5 + 3.9, -1.0, 2.0 + 0.95), drop=1.15, sag=0.12)
    PH.cat(b, -2.5 + 3.5, -0.75, 2.0, rz=200, col="!#8a8f96")
    # the net store's clutter
    V.creel(b, 2.35, -0.45, rz=80); V.creel(b, 2.4, -0.42, z=0.25, rz=95)
    PH.buoy(b, -2.5, -1.0 + 0.05, 0, s=0.9)
    PH.floats(c.front, 0.35, 1.9, n=4)
    V.rain_barrel(b, 2.3, 4.95, r=0.3, h=0.85)
    V.peat_stack(b, -1.0, 5.2, w=1.8, d=0.7, h=1.0)
