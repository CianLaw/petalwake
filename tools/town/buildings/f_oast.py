# Twin Cowls: the hop kilns of the upper meadows; when the cowls swing round together the whole valley knows which way the weather is coming.
# Massing: two round brick kilns with tall tiled cones and white turning cowls, a boarded stowage barn wedged between them with its gable to
#          the front, and a railed loading platform at loft level between the two kiln fronts (the landing) under a hoist.
# Materials: red brick, terracotta cones, white weatherboard on the barn's upper floor, white cowls; accent green.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_f as F

META = {"name": "Twin Cowls Oast", "kind": "kiln", "lot": (11.0, 8.0)}

KX, KY, KR, KH = 3.05, 2.95, 2.0, 5.5        # kiln axes at (+-KX, KY), radius, wall height
CONE = 5.0
PLAT = 3.2                                   # the loading platform
BY0, BY1, BW = 2.0, 6.9, 4.4                 # the barn: front wall, back wall, width


def cowl(b):
    """A turning cowl: a boarded hood open on one side with a wind vane behind. Frame: the middle of its foot; it opens toward local -y."""
    hood = [(0.53, 0.08), (0.5, 0.55), (0.37, 1.5), (0.17, 2.12), (0.0, 2.3)]
    b.revolve(hood, "planks", col="ivory", seg=10, a0=38, a1=322, lod=0)
    b.revolve([(max(r - 0.03, 0.0), z) for r, z in reversed(hood)], "planks", col="#4a4038", seg=10, a0=38, a1=322, lod=0)
    with b.detail(1):
        b.beam((0, 0.3, 1.72), (0, 1.95, 1.98), w=0.05, h=0.2, mat="planks", col="ivory", up=(0, 0, 1))
        b.box(0.06, 0.5, 0.34, "planks", col="green", x=0, y=2.05, z=1.82, bottom=True)
        b.revolve([(0.07, 2.26), (0.1, 2.4), (0.0, 2.5)], "planks", col="green", seg=6)


def kiln(b, sx):
    with b.at(sx * KX, KY):
        t = b.round(KR, KH, r1=KR - 0.06, mat="brick", seg=16)
        P.round_base(b, KR, h=0.7, out=0.16, mat="brick", col="#d8c2b0", seg=16, ring=t)
        F.door(t, 335 if sx < 0 else 25, w=0.8, h=1.55, arch=0.4, col="green", z=0.12)
        F.window(t, 270 if sx < 0 else 90, 3.0, w=0.55, h=0.9, arch=0.27)
        F.window(t, 200 if sx < 0 else 160, 3.0, w=0.55, h=0.9, arch=0.27)
        P.ring_band(b, KR - 0.04, KH - 0.42, h=0.22, out=0.07, mat="brick", col="#f2d6bc", seg=16)
        b.cone_roof(KR - 0.06, CONE, mat="tiles", z=KH, seg=16, eave=0.3, course=0.62, finial=False,
                    section=[(KR + 0.26, -0.32), (KR - 0.55, 0.95), (0.5, CONE)])
        with b.at(z=KH + CONE):
            with b.detail(1):
                b.revolve([(0.52, -0.16), (0.6, -0.1), (0.6, 0.08), (0.5, 0.14)], "timber", col="darkoak", seg=10)
            with b.at(rz=228 if sx < 0 else 236):
                with b.spin(speed=0.02, axis=(0, 0, 1)):
                    cowl(b)
            b.smoke(0, 0, 1.6, strength=0.7)
    return t


def build(b):
    kl, kr = kiln(b, -1), kiln(b, 1)
    P.ivy(kl, 212, 0.6, w=2.0, h=3.4, n=9)

    # ---- the stowage barn between them: brick below, white boards above, gable to the front
    yc = (BY0 + BY1) / 2
    g = b.body(BW, BY1 - BY0, 2.7, mat="brick", x=0, y=yc)
    P.plinth(g, h=0.45, out=0.06, mat="brick", col="#d8c2b0")
    u = b.body(BW, BY1 - BY0, 2.3, mat="planks", col="ivory", x=0, y=yc, z=2.7)
    P.door(g.front, 1.25, w=1.0, h=2.0, col="green", frame="timber", z=0.1, lamp=True)
    P.window(g.front, 3.25, 1.0, w=0.7, h=1.0, lintel="timber")
    PH.loading_door(u.front, BW / 2 - 0.65, PLAT - 2.7 + 0.03, w=1.15, h=1.75, col="green", sill=False, bar=False)
    F.barn_doors(g.back, BW / 2, w=2.3, h=2.3, col="green", swing=(8, 50))
    P.window(u.back, 1.1, 0.75, w=0.7, h=1.0, shutters="green", lintel="timber")
    P.window(u.back, 3.3, 0.75, w=0.7, h=1.0, shutters="green", lintel="timber")
    P.window(u.right, 4.0, 0.75, w=0.7, h=1.0, lintel="timber")
    P.window(u.left, 0.9, 0.75, w=0.7, h=1.0, lintel="timber")
    P.window(g.right, 4.0, 1.0, w=0.7, h=1.0, lintel="timber")
    P.band(u, 0.0, h=0.14, out=0.05, mat="timber", col="darkoak")
    rise = u.gable(ridge="y", pitch=48, mat="tiles", eave=0.3, verge=0.34, sag=0.08)
    PC.oculus(u.front, BW / 2, 2.3 + rise * 0.42, r=0.3)
    PC.oculus(u.back, BW / 2, 2.3 + rise * 0.42, r=0.3)
    P.weathervane(b, 0, yc, 5.0 + rise - 0.1, h=1.2)

    # ---- the loading platform between the kiln fronts: where the rider lands, in through the gap in the rail
    y0 = 0.15
    F.deck(b, 3.8, BY0 - y0, x=0, y=(BY0 + y0) / 2, z=PLAT, thick=0.1, joists=0.75)
    for sx in (-1, 1):
        b.beam((sx * 1.72, y0 + 0.14, -2.0), (sx * 1.72, y0 + 0.14, PLAT - 0.1), w=0.2, mat="timber", col="darkoak", lod=0)
        with b.detail(1):
            b.beam((sx * 1.72, y0 + 0.14, PLAT - 1.0), (sx * 0.9, y0 + 0.14, PLAT - 0.2), w=0.13, mat="timber", col="darkoak")
            b.beam((sx * 1.72, y0 + 0.14, PLAT - 1.0), (sx * 1.72, y0 + 0.95, PLAT - 0.2), w=0.13, mat="timber", col="darkoak")
    P.railing(b, [(0.3, y0 + 0.08, PLAT), (1.82, y0 + 0.08, PLAT), (1.82, 1.15, PLAT)], h=0.95, style="cross")
    P.railing(b, [(-1.82, 1.15, PLAT), (-1.82, y0 + 0.08, PLAT), (-1.5, y0 + 0.08, PLAT)], h=0.95, style="cross")
    b.pad(-0.62, 1.0, PLAT, radius=0.75, face=0, name="Loading platform")
    with b.at(-0.62, 1.0, PLAT):
        P.landing_mark(b, 0.7)
    PM.hoist(b, 1.05, BY0, 5.55, face=0, out=1.88, rope=1.7, load="sack")
    for (x, y, r_) in ((1.2, 1.55, 0.3), (1.5, 1.05, 0.27), (0.85, 1.25, 0.26)):
        P.sack(b, x, y, PLAT, r=r_, col="#d6c69a")
    P.sack(b, 1.25, 1.2, PLAT + 0.42, r=0.25, col="#d6c69a")

    # ---- yard clutter: casks under the platform, hop poles against a kiln, the meadow at the back
    P.barrel(b, 0.3, 1.45, 0.0, r=0.3, h=0.85)
    P.barrel(b, 0.95, 1.6, 0.0, r=0.28, h=0.8)
    P.barrel(b, 0.6, 0.95, 0.0, r=0.27, h=0.78)
    P.sack(b, -1.2, 1.5, 0.0)
    with b.detail(2):
        for k in range(6):
            a = rad(196 + 5 * k)
            fx, fy = KX + (KR + 0.7) * math.sin(a), KY - (KR + 0.7) * math.cos(a)
            tx, ty = KX + (KR + 0.02) * math.sin(a), KY - (KR + 0.02) * math.cos(a)
            b.beam((fx, fy, 0.0), (tx, ty, 4.6 + 0.15 * k), w=0.05, mat="planks", col="#c9b089", caps=False)
    P.crate(b, -1.75, 7.25, 0.0, s=0.55, rz=12)
    P.sack(b, -2.6, 6.4, 0.0, r=0.3, col="#d6c69a")
    P.sack(b, -2.95, 6.9, 0.0, r=0.28, col="#d6c69a")
    F.ladder_to(b, (-4.3, 5.9, 0.0), (-3.75, 4.95, 4.3), w=0.42)
    F.meadow(b, -4.9, 5.7, -3.6, 7.5, n=4, spread=(0.28, 0.42))
    F.meadow(b, 2.8, 5.7, 4.9, 7.5, n=5, spread=(0.28, 0.42))
    for (x, y) in ((-4.85, 0.75), (4.85, 0.75), (-4.95, 5.2), (4.95, 5.2)):
        F.flowers(b, x, y, 0.0, n=5, spread=0.34)
