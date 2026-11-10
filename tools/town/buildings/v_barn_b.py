# The Kiln Barn: every sheaf grown on the cliff farms is threshed on its floor and dried in the round kiln at
# its back before the damp can get at it. A low stone threshing barn with great doors under a roped stone-slab
# roof, a bottle-shaped kiln with a turf cap, an open cart hovel in its lee. Dark rubble, stone slates, teal doors.
import math

from kit import *
import parts as P
import parts_v as V
import parts_c as PC
import parts_f as PF

META = {"name": "The Kiln Barn", "kind": "barn", "lot": (8.0, 10.0), "wobble": 0.045}

SLAB = "#c2c5c4"


def build(b):
    ac = "teal"
    b.footprint(-3.9, 0.0, 3.9, 9.9, 2.9)
    W, D, H, BT = 7.4, 5.4, 2.9, 0.055
    c = V.BBody(b, W, D, H, col="dark", batter=BT, depth=0.5)
    V.footing(c, h=0.5, boulders="f")
    V.quoins(c, corners="fr", col="grey", size=(0.72, 0.4, 0.5))
    V.door(c.front, W / 2, w=2.3, h=2.35, col=ac, double=True, lintel="timber")
    for u in (0.9, 1.9, 5.5, 6.5):
        V.slit(c.front, u, 1.1, h=0.7)
    V.rubble(c.front, n=14)
    V.slit(c.left, 1.4, 1.1, h=0.7); V.window(c.left, D / 2, 3.3, w=0.5, h=0.6, lintel="timber")
    V.slit(c.right, 4.0, 1.1, h=0.7); V.door(c.right, D / 2, w=0.8, h=1.1, z=2.6, col=ac, step=False, jambs=False, lintel="timber")
    V.rubble(c.left, n=10); V.rubble(c.right, n=10)
    V.door(c.back, 2.4, w=1.0, h=1.9, col=ac, half=True, lintel="timber", step=False)
    V.rubble(c.back, n=10)
    rf = c.gable(ridge="x", pitch=42, skew=True, mat="flagstone", col=SLAB, eave=0.3, course=0.55, ridge_roll=False)
    V.ropes(rf, every=1.05, rows=(0.5,), drop=0.45)
    RZ = H + rf.rise
    with b.detail(1):
        V.beam(b, (-W / 2 + 0.5, D / 2, RZ + 0.05), (W / 2 - 0.5, D / 2, RZ + 0.05), w=0.3, h=0.12, mat="flagstone", col=shade(SLAB, 0.9), up=(0, 0, 1))
    PC.doves(b, [(-1.6, D / 2, RZ + 0.13), (-1.2, D / 2, RZ + 0.13), (2.3, D / 2, RZ + 0.13)])
    # ------------------------------------------------------------------ the kiln
    KX, KY, KR, KH = -1.84, D + 1.55, 1.75, 4.3
    k = b.round(KR, KH, r1=1.36, mat="masonry", col="dark", x=KX, y=KY, seg=16, depth=0.45)
    P.round_base(b, KR, h=0.6, out=0.2, col=shade("dark", 0.9), seg=16, ring=k)
    V.door(k, 95, w=0.75, h=1.4, z=0.15, col=ac, jambs=True)
    V.slit(k, 215, 2.4, w=0.16, h=0.6); V.slit(k, 300, 1.2, w=0.16, h=0.6)
    V.rubble(k, n=22, size=(0.3, 0.6), z0=0.7)
    b.cone_roof(1.36, 1.75, mat="thatch", col="!#789248", x=KX, y=KY, z=KH, seg=16, finial=False, course=0.5, lip=0.03,
                section=[(1.52, -0.06), (1.42, 0.5), (1.08, 1.15), (0.5, 1.62), (0.0, 1.75)])
    with b.at(KX, KY, KH):
        b.revolve([(1.5, -0.13), (1.53, -0.02)], "planks", col="greyoak", seg=16, lod=0)
        b.stone(0.5, 0.45, 0.14, mat="flagstone", col="grey", lod=1, z=1.72)
        with b.detail(2):
            for kk in range(14):
                a, rr = b.r(0, 6.28), b.r(0.3, 1.2)
                zz = 1.72 - 1.2 * (rr / 1.4) ** 2
                with b.at(rr * math.cos(a), rr * math.sin(a), zz):
                    V.tuft(b, b.r(0.09, 0.14), b.r(0.16, 0.26))
    b.smoke(KX, KY, KH + 2.1, strength=0.8)
    V.ladder(b, (KX + 2.05, KY + 1.0, 0.0), (KX + 1.25, KY + 0.75, KH + 0.2), w=0.42)
    # ------------------------------------------------------------------ the cart hovel in the lee of the barn
    hx0, hx1, hy1 = 0.45, 3.38, 8.5
    for (x, y) in ((hx0, hy1), (hx1, hy1), ((hx0 + hx1) / 2, hy1)):
        V.beam(b, (x, y, 0), (x, y, 1.8), w=0.16, mat="timber", col="darkoak", lod=0)
        b.stone(0.36, 0.36, 0.22, mat="masonry", col="grey", lod=1, x=x, y=y, z=0)
    V.beam(b, (hx0 - 0.15, hy1, 1.86), (hx1 + 0.15, hy1, 1.86), w=0.14, h=0.18, mat="timber", col="darkoak", lod=1, up=(0, 0, 1))
    V.shed_roof(b, hx1 - hx0 + 0.3, hy1 - D + 0.25, 13, x=(hx0 + hx1) / 2, y=D - BT * 2.8, z=2.86, face=180, mat="flagstone", col=SLAB, eave=0.3, verge=0.2,
                course=0.55, soffit_col="darkoak")
    for x in (hx0, hx1):
        V.beam(b, (x, D - 0.1, 2.6), (x, hy1 + 0.3, 1.8), w=0.1, h=0.14, mat="timber", col="darkoak", lod=1, up=(0, 0, 1))
    PF.cart(b, 1.92, 6.75, 0, rz=180, load="sacks")
    # ------------------------------------------------------------------ before the doors
    for x in (2.0, 2.75, 3.4):
        PF.staddle(b, x, -0.55, 0, h=0.7, r=0.34)
    P.sack(b, -2.9, -0.45); P.sack(b, -2.45, -0.6, r=0.27); P.sack(b, -2.7, -0.5, z=0.38, r=0.25)
    PF.tool(b, -1.75, -0.1, 0, kind="rake")
