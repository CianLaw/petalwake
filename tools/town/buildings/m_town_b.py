# The Locksmith's: the narrowest and tallest house in the row. Old Master Ward makes locks on the ground floor and
# keeps the town's spare keys on the fourth, hauling his iron up the front on the hoist.
# Massing: four flat-fronted storeys, eaves to the street, a tall gabled wall-dormer with a hoist breaking the slate
# roof, a brick stack on each party wall, a two-storey outshot behind.
# Materials: dressed stone ground floor, ochre lime plaster with stone window surrounds, bands and quoins; teal woodwork.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Locksmith's", "kind": "house", "lot": (5.6, 9.0), "terrace": True}

A = "teal"
W, D = 4.8, 6.4
ZS = [0.0, 3.3, 6.1, 8.9, 11.3]
T48 = math.tan(rad(48))


def build(b):
    g = b.body(W, D, ZS[1], mat="ashlar", col="sand")
    P.plinth(g, h=0.5, mat="ashlar", col="grey")
    P.window(g.front, 1.45, 1.0, w=1.5, h=1.7, arch=0.6, bars=(2, 2), lintel=None, sill=False)
    Q.surround(g.front, 1.45, 1.0, 1.5, 1.7, arch=0.6, sill=True)
    P.door(g.front, 3.65, w=0.95, h=2.3, z=0.34, arch=0.47, col=A, frame=None, lamp=True)
    Q.surround(g.front, 3.65, 0.34, 0.95, 2.3, arch=0.47)
    Q.steps(g.front, 3.65, w=1.4, n=2, z=0.34)
    Q.sign(g.front, 0.3, 3.05, emblem="key", shape="arch", col="mustard", board="black", out=0.85)
    up = b.body(W, D, ZS[4] - ZS[1], mat="plaster", col="ochre", z=ZS[1])
    Q.quoins(up, corners="fr", size=(0.5, 0.28, 0.42))
    for k in (1, 2, 3):
        z = ZS[k] - ZS[1]
        P.band(up, z, h=0.18, out=0.06)
        for u in (1.25, W - 1.25):
            hh = 1.5 if k < 3 else 1.15
            P.window(up.front, u, z + 0.95, w=0.95, h=hh, bars=(1, 2), lintel=None, sill=False, shutters=A if k == 2 else None, box=(k == 1 and u < 2))
            Q.surround(up.front, u, z + 0.95, 0.95, hh, t=0.13, sill=True, keystone=(k == 1))
        P.window(up.back, 3.6, z + 0.95, w=0.9, h=1.3, bars=(1, 2), shutters=A)
    for wl, u in ((up.right, 4.6), (up.left, 1.8)):
        P.window(wl, u, ZS[3] - ZS[1] + 0.95, w=0.7, h=1.1, bars=(1, 1))
    P.band(up, ZS[4] - ZS[1] - 0.24, h=0.22, out=0.09)
    up.gable(ridge="x", pitch=48, mat="slate", sag=0.08, eave=0.35, verge=0.1)
    # --- the wall-dormer and its hoist
    wd = b.body(1.9, 2.0, 1.7, mat="plaster", col="ochre", x=0, y=1.0, z=ZS[4], foot=False)
    P.door(wd.front, 0.95, w=0.85, h=1.35, z=0.05, col=A, frame="timber", knob=False)
    wd.gable(ridge="y", pitch=52, mat="slate", eave=0.2, verge=0.28)
    Q.hoist(b, 0, 0.0, ZS[4] + 1.7 + 0.7, face=0, out=0.95, rope=3.4, load="crate")
    for sx, top in ((-1, 16.6), (1, 16.0)):
        Q.stack(b, sx * (W / 2 - 0.33), D / 2 + 0.6 * sx, ZS[4] - 0.3, top - ZS[4] + 0.3, w=0.6, d=0.8, mat="brick", col=None, pots=2, band=False)
    # --- the outshot behind
    o = b.body(2.8, 1.9, 5.4, mat="plaster", col="ochre", x=W / 2 - 1.4, y=D + 0.95)
    Q.plinth(o, h=0.4, walls="rbl")
    P.door(o.left, 0.95, w=0.85, h=1.95, z=0.1, col=A, frame="timber")
    for z in (1.2, 3.6):
        P.window(o.back, 1.4, z, w=0.9, h=1.2, bars=(1, 2))
    rs = Q.lean_to(b, 2.8, 1.9, pitch=30, x=W / 2 - 1.4, y=D, z=5.4, face=180, mat="slate", eave=0.18, verge=0.1)
    b.tri((W / 2 - 2.8, D + 1.9, 5.4), (W / 2 - 2.8, D, 5.4), (W / 2 - 2.8, D, 5.4 + rs), "plaster", col="ochre")
    b.tri((W / 2, D, 5.4), (W / 2, D + 1.9, 5.4), (W / 2, D, 5.4 + rs), "plaster", col="ochre")
    P.window(g.back, 3.6, 1.3, w=0.9, h=1.3, bars=(1, 2))
    P.planter(b, -0.2, -0.28, 0, w=0.5, d=0.4, h=0.36, bush=True)
