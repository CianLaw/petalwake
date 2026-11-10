# The Stair Barn: hay and nets go in at the top, up the outside stair, and the cart and the plough below; the
# owl that lives in the peak has its own hole. A tall stone barn, gable to the street, with a forestair to the
# loft door, a hoist beam, and a cart passage down its side. Grey rubble, weighted slates, ox-red doors.
from kit import *
import parts as P
import parts_v as V
import parts_c as PC
import parts_h as PH
import parts_f as PF

META = {"name": "The Stair Barn", "kind": "barn", "lot": (8.0, 10.0), "wobble": 0.045}


def build(b):
    ac = "red"
    b.footprint(-3.9, 0.0, 3.9, 9.9, 3.0)
    BT, X0, W, D, H = 0.05, -0.55, 6.2, 9.0, 3.0
    c = V.BBody(b, W, D, H, col="grey", x=X0, batter=BT, depth=0.5)
    xl = X0 - W / 2
    V.footing(c, h=0.5, boulders="l")
    V.quoins(c, corners="fr", size=(0.72, 0.4, 0.5))
    # the gable to the street: cart doors, the loft door at the head of the stair, the owl's hole
    V.door(c.front, 1.5, w=1.9, h=2.4, col=ac, double=True, lintel="timber")
    V.door(c.front, 3.3, w=0.9, h=1.55, z=2.5, col=ac, step=False, lintel="timber", jambs=False)
    V.slit(c.front, W / 2, 5.25, w=0.3, h=0.34)
    V.slit(c.front, 5.3, 1.0, h=0.6)
    V.rubble(c.front, n=12, z0=2.6)
    for wl in (c.left, c.right):
        for u in (1.5, 3.5, 5.5, 7.5):
            V.slit(wl, u, 1.1, h=0.7)
        V.rubble(wl, n=16)
    V.door(c.right, 4.5, w=0.9, h=1.7, col=ac, half=True, lintel="timber")
    V.window(c.back, W / 2, 3.4, w=0.6, h=0.75, lintel="timber")
    V.slit(c.back, 1.6, 1.1, h=0.7); V.slit(c.back, 4.6, 1.1, h=0.7)
    V.rubble(c.back, n=12)
    rf = c.gable(ridge="y", pitch=45, skew=True, mat="slate", eave=0.3, apex="stone")
    V.weights(rf, rows=(0.4, 2.0), every=1.0)
    RZ = H + rf.rise
    PC.doves(b, [(X0 + 0.1, 2.2, RZ + 0.14), (X0 - 0.05, 2.7, RZ + 0.14), (X0, 6.4, RZ + 0.14)])
    # ------------------------------------------------------------------ the forestair, climbing right to left along the gable
    SX = xl + W - 0.12
    with b.at(SX, -0.53, 0, rz=180):
        top = V.forestair(b, n=10, w=1.0, rise=0.25, run=0.24, landing=0.95, col="grey", niche=True, wall="-y")
        V.rails(b, [(0.0, 0.44, 0.25), (2.4, 0.44, top), (3.35, 0.44, top), (3.35, -0.44, top)], h=0.95, col="darkoak", post=0.08, posts_at=1.2)
    PH.hoist(b, xl + 3.3, BT * 4.4, 4.45, out=0.9, rz=0, drop=1.0, load="sack")
    PC.cat(b, SX - 2.9, -0.6, 2.5, rz=190, col="#b98a5a")
    P.sack(b, xl + 0.35, -0.4); P.sack(b, xl + 0.85, -0.55, r=0.26)
    PF.tool(b, xl + 2.75, -0.1, 0, kind="fork")
    # ------------------------------------------------------------------ the cart passage and the yard wall
    PF.cart(b, 3.2, 3.4, 0, rz=0, W=0.9, load="hay")
    V.drystone(b, [(2.75, 9.55), (3.65, 9.55), (3.65, 5.6)], h=1.0, t=0.45)
    PF.hay(b, 3.15, 6.9, 0, rx=0.55, h=0.75)
    V.trough(b, 3.1, 0.6, 0, w=1.2, d=0.55, h=0.45, rz=90)
