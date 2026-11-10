# The whale-watchers' lookout: when the grey whales pass in spring someone sits up here all day with the glass,
# and rings the bell so the whole village comes to the cliff to see. A boarded stage on four raking larch legs
# straddling an old turf-roofed stone hut; a bench under a little pent roof, the bell, the telescope. Moss, oak, navy.
import math

from kit import *
import parts as P
import parts_v as V
import parts_h as PH
import parts_l as PL

META = {"name": "Whale-watchers' Lookout", "kind": "tower", "lot": (5.0, 5.0), "wobble": 0.03, "lean": (0.0, 0.002)}

CX, CY = 0.0, 2.5


def build(b):
    b.footprint(-2.4, 0.1, 2.4, 4.9, 3.0)
    # ------------------------------------------------------------------ the hut
    h = V.BBody(b, 3.3, 3.2, 1.85, col="moss", x=CX, y=CY, batter=0.08, depth=0.4)
    V.footing(h, h=0.4, boulders="frl")
    V.door(h.front, 1.2, w=0.8, h=1.5, col="navy")
    V.window(h.front, 2.5, 0.75, w=0.45, h=0.5, col="navy", shut="one")
    V.window(h.right, 1.6, 0.8, w=0.45, h=0.5)
    V.rubble(h.left, n=8); V.rubble(h.right, n=6); V.rubble(h.back, n=8); V.rubble(h.front, n=4)
    h.hip(pitch=30, mat="thatch", col=V.TURF, eave=0.3, thick=0.24, course=0.7, lip=0.035)
    with b.at(CX, CY, 1.85):
        with b.detail(2):
            for k in range(20):
                a, rr = b.r(0, 6.28), b.r(0.2, 1.5)
                x, y = rr * math.cos(a), rr * math.sin(a)
                with b.at(x, y, max((1.45 - max(abs(x), abs(y))) * 0.577 + 0.04, 0.05)):
                    V.tuft(b, b.r(0.09, 0.14), b.r(0.16, 0.28), shade("#8fb556", b.r(0.85, 1.2)))
    V.chimney(b, CX + 0.95, CY + 0.9, 1.6, 1.5, w=0.55, d=0.5, col="moss", cap="slab", strength=0.7)
    # ------------------------------------------------------------------ the stage on its four legs
    PZ = 9.6
    V.trestle(b, (2.05, 2.05), (1.4, 1.4), 0.0, PZ - 0.3, tiers=3, leg=0.3, round_legs=True, brace=0.12, girt=0.15, x=CX, y=CY, cross="z",
              skip_brace={(0, 0)}, foot=(0.56, 0.34), foot_col="moss")
    DW = 3.5
    V.deck(b, DW, DW, PZ, x=CX, y=CY, joists=0.7)
    for sx in (-1, 1):
        for sy in (-1, 1):
            V.knee(b, (CX + sx * 1.52, CY + sy * 1.52, PZ - 1.35), (CX + sx * (DW / 2 - 0.15), CY + sy * (DW / 2 - 0.15), PZ - 0.3), w=0.12, strut=False)
    e = DW / 2 - 0.09
    V.rails(b, [(CX + 1.1, CY - e, PZ), (CX + e, CY - e, PZ), (CX + e, CY + 0.5, PZ)], h=1.0, col="darkoak", posts_at=1.2)
    V.rails(b, [(CX + e, CY + 1.3, PZ), (CX + e, CY + e, PZ), (CX - e, CY + e, PZ), (CX - e, CY - e, PZ), (CX - 0.8, CY - e, PZ)], h=1.0, col="darkoak", posts_at=1.2)
    with b.at(CX + 0.15, CY - 0.75, PZ):
        P.landing_mark(b, 0.74)
    b.pad(CX + 0.15, CY - 0.75, PZ, radius=0.8, face=0, name="Lookout stage")
    # the long ladder up the right side to the gap in the rail
    V.ladder(b, (CX + 2.33, CY + 0.9, 0.0), (CX + e + 0.07, CY + 0.9, PZ + 0.8), w=0.5, rail=0.065)
    # the shelter at the back: a pent roof over the bench, open toward the sea
    sx0, sx1, sy0 = CX - 1.45, CX + 0.95, CY + 0.45
    for sx in (sx0, sx1):
        V.beam(b, (sx, sy0, PZ), (sx, sy0, PZ + 2.42), w=0.12, mat="timber", col="darkoak", lod=0)
        V.beam(b, (sx, CY + e - 0.03, PZ + 0.9), (sx, CY + e - 0.03, PZ + 1.86), w=0.11, mat="timber", col="darkoak", lod=1)
        V.beam(b, (sx, sy0, PZ + 2.3), (sx, CY + e, PZ + 1.78), w=0.09, h=0.13, mat="timber", col="darkoak", lod=1)
        V.knee(b, (sx, sy0, PZ + 1.7), (sx + (0.5 if sx < CX else -0.5), sy0, PZ + 2.28), w=0.08, strut=False)
    V.beam(b, (sx0 - 0.1, sy0, PZ + 2.34), (sx1 + 0.1, sy0, PZ + 2.34), w=0.11, h=0.15, mat="timber", col="darkoak", lod=1)
    V.shed_roof(b, sx1 - sx0 + 0.1, e - 0.45 + 0.12, 23, x=(sx0 + sx1) / 2, y=sy0 - 0.05, z=PZ + 2.5, face=180, mat="shingle", eave=0.14, verge=0.14, course=0.3, thick=0.07)
    P.bench(b, (sx0 + sx1) / 2, CY + e - 0.42, PZ, w=1.8)
    with b.at(sx1 - 0.45, sy0, PZ + 2.27):
        P.bell(b, 0, 0, 0, r=0.19, beam=0.34)
    with b.detail(2):
        V.beam(b, (sx1 - 0.45, sy0 + 0.02, PZ + 1.9), (sx1 - 0.45, sy0 + 0.02, PZ + 1.2), w=0.02, mat="cloth", col=V.ROPE, caps=False)
    PL.telescope(b, CX + 1.28, CY - e + 0.42, PZ, rz=-25)
    P.flag(b, CX - e + 0.02, CY - e + 0.02, PZ + 1.0, pole=2.4, w=1.1, h=0.5, col="stripe_blue")
    V.vane(b, (sx0 + sx1) / 2, sy0 + 0.05, PZ + 2.5, h=1.3, kind="whale", s=0.9, arms=False)
    PH.gull(b, CX - e, CY + 0.2, PZ + 1.06, rz=260)
    # things at the foot
    V.creel(b, CX - 0.8, CY + 2.0, rz=12); V.creel(b, CX - 0.1, CY + 2.02, rz=-8); V.creel(b, CX - 0.45, CY + 2.0, z=0.25, rz=3)
    # the whale board on the rail
    with b.detail(1):
        b.box(0.86, 0.04, 0.44, "planks", col="navy", x=CX - 1.22, y=CY - e - 0.04, z=PZ + 0.3, bottom=True)
    with b.at(CX - 1.2, CY - e - 0.07, PZ + 0.5):
        V.shape(b, [(p[0] * 0.52, p[1] * 0.52) for p in V.VANES["whale"]], mat="paint", col="ivory", lod=2, both=False)
    P.barrel(b, CX - 1.15, 0.6, 0.0, r=0.26, h=0.7)
