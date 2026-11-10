# The Last Lantern: the last roof before the cliff road ends, and the lantern on its mast is lit every dusk for
# anyone still out on the moor. Long and low under one great slate roof, a white-railed gallery along the ridge
# between two great chimneys, a kitchen outshot behind. Lime-washed front on warm rubble, navy paint, a brass lamp.
import math

from kit import *
import parts as P
import parts_v as V
import parts_c as PC
import parts_h as PH
import parts_k as PK
import parts_l as PL

META = {"name": "The Last Lantern", "kind": "inn", "lot": (13.0, 9.0), "wobble": 0.04}


def build(b):
    ac = "navy"
    W, D, H, BT = 12.0, 6.2, 5.0, 0.034
    m = V.BBody(b, W, D, H, col="warm", batter=BT, depth=0.45, faces={"front": ("plaster", "white")})
    b.footprint(-6.4, 0.0, 6.4, 8.8, H)
    V.footing(m, h=0.55, col=shade("warm", 0.9), boulders="f")
    V.quoins(m, corners="fr", col=shade("warm", 1.05), size=(0.7, 0.38, 0.5))
    # ------------------------------------------------------------------ the front
    cols = (1.3, 2.9, 7.0, 8.8, 10.6)
    V.door(m.front, 4.75, w=1.15, h=2.0, z=0.12, col=ac, lamp=True)
    for i, u in enumerate(cols):
        V.window(m.front, u, 1.0, w=0.8, h=1.05, col=ac, shut="half" if i == 3 else "open", bars=(1, 2))
        V.window(m.front, u, 3.35, w=0.62, h=0.8, col=ac, shut="one" if i in (0, 4) else "open")
    V.window(m.front, 4.75, 3.35, w=0.62, h=0.8, col=ac)
    V.harl(m.front, n=16, where="both", col="warm")
    V.sign(m.front, 5.95, 3.75, V.LANTERN, col="mustard", board="navy", out=0.9)
    # a slated hood over the door on two brackets
    with b.at(-6.0 + 4.75, BT * 2.5, 2.52):
        V.shed_roof(b, 1.9, 0.85, 30, x=0, y=0.0, z=0.55, face=0, eave=0.1, verge=0.08, course=0.28, thick=0.08)
        for sx in (-0.8, 0.8):
            V.knee(b, (sx, 0.0, -0.65), (sx, -0.72, -0.02), w=0.1)
    # ------------------------------------------------------------------ gables: small windows either side of the breasts
    for wl in (m.left, m.right):
        V.window(wl, 1.0, 1.1, w=0.6, h=0.85, col=ac if wl is m.left else None, shut="one")
        V.window(wl, D - 1.0, 3.3, w=0.55, h=0.75)
        V.rubble(wl, n=14, col=shade("warm", 1.08))
    for u in (2.2, 9.6):
        V.window(m.back, u, 3.35, w=0.62, h=0.8)
    V.rubble(m.back, n=14, z0=3.0, col=shade("warm", 1.08))
    # ------------------------------------------------------------------ the roof, the two great chimneys
    rf = m.gable(ridge="x", pitch=51.5, skew=True, mat="slate", apex=None, eave=0.32)
    V.weights(rf, rows=(0.35, 1.7), every=0.95)
    RZ = H + rf.rise
    for sx in (-1, 1):
        xg = W / 2 - BT * RZ
        b.box(0.72, 2.3, 6.4, "masonry", col="grey", x=sx * (W / 2 - 0.02), y=D / 2, z=0, tx=0.55, ty=0.74, lod=0)
        b.box(0.8, 2.4, 3.0, "masonry", col=shade("grey", 0.85), x=sx * (W / 2 - 0.02), y=D / 2, z=-3.0, top=False, lod=0)
        V.chimney(b, sx * (xg - 0.42), D / 2, 5.9, RZ + 2.95 - 5.9, w=1.12, d=1.7, col="grey", cap="pots" if sx < 0 else "slab", pots=3, along="y", strength=1.3)
    PH.gull(b, W / 2 - BT * RZ - 0.42, D / 2 + 0.4, RZ + 3.3, rz=250)
    for x in (-3.3, 3.5):
        P.dormer(b, x, 1.1, H + 1.0, w=1.15, h=1.0, depth=1.5, face=0, kind="gable", wall="plaster", col="white", roof="slate", pitch=44, frame="ivory")
    # ------------------------------------------------------------------ the roof gallery along the ridge: where the rider lands
    GZ = RZ + 0.17
    GL, GW, gy = 9.3, 1.8, D / 2
    V.deck(b, GL, GW, GZ, x=0, y=gy, joists=0, edge=False)
    with b.detail(1):
        for sy in (-1, 1):
            V.beam(b, (-GL / 2, gy + sy * (GW / 2 - 0.06), GZ - 0.2), (GL / 2, gy + sy * (GW / 2 - 0.06), GZ - 0.2), w=0.12, h=0.22, mat="timber", col="darkoak", up=(0, 0, 1))
            for k in range(7):
                x = -GL / 2 + 0.3 + (GL - 0.6) * k / 6
                zr = RZ - (GW / 2 - 0.06) * math.tan(rad(51.5))
                V.beam(b, (x, gy + sy * (GW / 2 - 0.06), zr - 0.1), (x, gy + sy * (GW / 2 - 0.06), GZ - 0.3), w=0.11, mat="timber", col="darkoak", caps=False)
    y0, y1 = gy - GW / 2 + 0.08, gy + GW / 2 - 0.08
    P.railing(b, [(-GL / 2 + 0.05, y1, GZ), (GL / 2 - 0.05, y1, GZ)], h=1.0, style="balusters", col="ivory", mat="planks")
    P.railing(b, [(-GL / 2 + 0.05, y0, GZ), (-0.55, y0, GZ)], h=1.0, style="balusters", col="ivory", mat="planks")
    P.railing(b, [(1.9, y0, GZ), (GL / 2 - 0.05, y0, GZ)], h=1.0, style="balusters", col="ivory", mat="planks")
    with b.at(0.65, gy, GZ):
        P.landing_mark(b, 0.74)
    b.pad(0.65, gy, GZ, radius=0.8, face=0, name="Roof gallery")
    PC.hatch(b, 3.55, gy + 0.05, GZ, w=0.7, d=0.75, open_deg=62)
    # the lantern on its mast
    MX = -3.75
    with b.detail(1):
        b.tube((MX, gy, GZ), (MX, gy, GZ + 4.5), r=0.075, r1=0.045, mat="planks", col="darkoak", n=6)
        V.beam(b, (MX, gy, GZ + 3.95), (MX + 1.0, gy, GZ + 4.15), w=0.07, mat="timber", col="darkoak")
        V.beam(b, (MX, gy, GZ + 3.3), (MX + 0.7, gy, GZ + 4.05), w=0.05, mat="timber", col="darkoak", caps=False)
        b.box(0.1, 0.1, 0.1, "metal", col="brass", x=MX, y=gy, z=GZ + 4.5, bottom=True)
    with b.at(MX + 0.88, gy, GZ + 4.06):
        V.big_lantern(b, s=0.56, lamp=3.0)
    V.rope(b, (MX, gy, GZ + 4.3), (-GL / 2 - 0.3, gy, RZ + 2.6), sag=0.12, lod=1)
    V.rope(b, (MX, gy, GZ + 4.3), (MX + 2.6, y1, GZ + 1.0), sag=0.1, lod=1)
    # ------------------------------------------------------------------ the kitchen outshot under a catslide
    o = V.BBody(b, 8.2, 2.15, 2.3, col="grey", x=-1.7, y=D + 0.95, batter=0.04, depth=0.38)
    V.footing(o, h=0.4, boulders="")
    V.door(o.back, 2.0, w=0.9, h=1.75, col=ac, half=True)
    V.window(o.back, 4.6, 0.95, w=0.62, h=0.75)
    V.window(o.back, 6.6, 0.95, w=0.62, h=0.75)
    V.window(o.right, 1.2, 0.95, w=0.55, h=0.7)
    V.rubble(o.back, n=10); V.rubble(o.left, n=5); V.rubble(o.right, n=5)
    r2 = o.shed(pitch=31, high="front", mat="slate", eave=0.28, verge=0.2)
    V.weights(r2, rows=(0.35,), verges=False)
    V.chimney(b, -5.2, D + 0.55, 2.2, 3.4, w=0.8, d=0.7, col="grey", cap="slab")
    # the yard corner behind: casks, firewood, a drystone wall
    V.drystone(b, [(2.5, 8.4), (6.1, 8.4), (6.1, 6.35)], h=1.1, t=0.5)
    PK.barrel(b, 3.3, 7.0, 0, r=0.34, h=0.9)
    PK.barrel(b, 4.05, 7.25, 0, r=0.34, h=0.9)
    PK.barrel(b, 3.7, 6.75, 0.0, r=0.3, h=0.8, lying=True, rz=20)
    PH.logs(b, 5.2, 7.9, 0, rz=0, n=4)
    # ------------------------------------------------------------------ before the door
    P.bench(b, -4.15, -0.5, w=1.9)
    P.bench(b, 2.0, -0.5, w=1.9, rz=2)
    PK.barrel(b, 0.35, -0.55, 0, r=0.36, h=0.92)
    with b.at(5.05, -0.55, 0):
        V.trough(b, w=1.4, d=0.6, h=0.5)
    PL.pump(b, 5.95, -0.42, 0, rz=90)
