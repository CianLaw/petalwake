# The Tilted Tankard: the quay's inn since before the mole was built; pilots drink under the balcony and captains sleep above it.
# A tall gabled cross-wing (stone, plaster, a jettied timber-framed top) and a lower range set back beside it whose long first-floor
# balcony on oak posts shelters the benches; a great outside stack on the flank. Warm stone, butter plaster, terracotta; accent green.
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "The Tilted Tankard", "kind": "inn", "lot": (11.0, 10.0), "lean": (0.002, 0.0)}


def gable_frame(wl, h, rise, col="darkoak"):
    """Tie beam, collar and two struts for a framed gable."""
    b, w = wl.b, wl.w

    def deco():
        with b.detail(1):
            y = -0.035
            kw = dict(mat="timber", col=col, caps=False)
            b.beam((0.1, y, h), (w - 0.1, y, h), w=0.11, h=0.16, up=(0, 0, 1), **kw)
            zc = h + rise * 0.56
            xw = w / 2 * 0.44
            b.beam((w / 2 - xw, y, zc), (w / 2 + xw, y, zc), w=0.11, h=0.14, up=(0, 0, 1), **kw)
            for sgn in (-1, 1):
                x = w / 2 + sgn * w * 0.23
                b.beam((x, y, h), (x, y, h + rise * 0.5), w=0.13, h=0.11, up=(0, 1, 0), **kw)
                b.beam((w / 2 + sgn * 0.1, y, zc), (w / 2 + sgn * 0.1, y, h + rise - 0.25), w=0.11, h=0.11, up=(0, 1, 0), **kw)

    wl.add(deco)


def build(b):
    # ------------------------------------------------------------------ the cross-wing: gable to the quay
    cw = b.body(4.0, 8.0, 3.0, mat="masonry", col="warm", x=-3.1)                                     # x -5.1 .. -1.1
    cw1 = b.body(4.0, 8.0, 2.7, mat="plaster", col="butter", x=-3.1, z=3.0)
    cw2 = b.body(4.2, 8.3, 2.5, mat="plaster", col="cream", x=-3.1, y=3.9, z=5.7, floor="planks")     # y -0.25 .. 8.05
    H.cuttable(cw2.front, cw2.back)
    RC = 2.1 * math.tan(rad(52))
    with b.detail(1):
        for i in range(6):
            x = -5.0 + 3.8 * i / 5
            b.beam((x, 0.05, 5.6), (x, -0.3, 5.6), w=0.14, h=0.18, mat="timber", col="darkoak")
    P.window(cw.front, 2.0, 1.0, w=2.0, h=1.45, bars=(3, 1), lintel="timber", frame="ivory", box=True)
    P.window(cw1.front, 1.1, 0.9, shutters="green", box=True)
    P.window(cw1.front, 2.9, 0.9, shutters="green")
    P.window(cw2.front, 2.1, 0.85, w=1.2, h=1.2, bars=(2, 1), lintel=None)
    P.window(cw2.front, 2.1, 3.12, w=0.55, h=0.7, lintel=None)
    for wl in cw2.walls:
        P.timber_frame(wl, braces="auto")
    gable_frame(cw2.front, 2.5, RC)
    gable_frame(cw2.back, 2.5, RC)
    for u in (1.5, 6.5):
        P.window(cw.left, u, 1.1, w=0.8, h=1.1, lintel="timber")
        H.near_only(cw.left)
    P.window(cw1.left, 1.5, 0.9, shutters="green")
    P.window(cw1.left, 6.3, 0.9, shutters="green")
    for u in (2.2, 6.6):
        P.window(cw2.left, u, 0.85, w=0.8, h=1.1, lintel=None)
        H.near_only(cw2.left)
    P.door(cw.back, 2.0, w=1.0, h=2.0, col="green", frame="timber", z=0.1)
    P.window(cw1.back, 2.0, 0.9, shutters="green")
    P.window(cw2.back, 2.1, 0.85, w=0.9, h=1.1, lintel=None)
    P.window(cw2.right, 1.0, 0.85, w=0.7, h=1.0, lintel=None)
    P.plinth(cw, h=0.6)
    P.quoins(cw, corners="fl", z0=0.6, col="sand")
    P.exposed(cw1.front, "corners", n=8)
    P.ivy(cw.left, 7.3, 0.2, w=1.8, h=4.6, n=10)
    cw2.gable(ridge="y", pitch=52, mat="tiles", eave=0.25, verge=0.35, sag=0.12)
    P.sign(cw1.front, 3.7, 2.4, emblem="mug", col="mustard", board="green", out=1.05, w=0.8, h=0.7)
    H.stack(b, -5.16, 4.6, 0.0, 12.4, w=0.5, d=1.5, top=0.44, mat="masonry", col="warm", bands=2, pots=3)

    # ------------------------------------------------------------------ the lower range, set back behind its balcony
    mg = b.body(6.2, 6.0, 3.0, mat="masonry", col="warm", x=2.0, y=3.9)                               # x -1.1 .. 5.1, y 0.9 .. 6.9
    mu = b.body(6.2, 6.0, 4.6, mat="plaster", col="butter", x=2.0, y=3.9, z=3.0)
    mg.left.done = True
    mu.left.done = True
    P.door(mg.front, 1.4, w=1.2, h=2.25, arch=0.5, col="green", frame="stone", steps=1, z=0.15, lamp=True)
    for u in (3.4, 5.1):
        P.window(mg.front, u, 1.0, w=1.15, h=1.3, bars=(2, 1), lintel="timber")
    for u in (1.4, 4.9):
        P.door(mu.front, u, w=0.9, h=2.0, z=0.05, col="green", frame="timber")
    P.window(mu.front, 3.15, 0.9, shutters="green")
    for u in (1.4, 3.15, 4.9):
        P.window(mu.front, u, 3.3, w=0.75, h=0.9, shutters="green", lintel=None)
    P.window(mg.right, 1.6, 1.0, w=0.9, h=1.2, lintel="timber")
    P.door(mg.right, 4.6, w=0.9, h=2.0, col="green", frame="timber", z=0.1)
    for u in (1.6, 4.4):
        P.window(mu.right, u, 0.9, shutters="green")
    P.window(mu.right, 3.0, 3.3, w=0.75, h=0.9, lintel=None)
    mu.right.gable = 3.0 - 0.03
    H.cuttable(mu.right)
    P.window(mu.right, 3.0, 5.2, w=0.6, h=0.8, lintel=None)
    for u in (1.5, 4.6):
        P.window(mu.back, u, 0.95, shutters="green")
    P.window(mu.back, 3.0, 3.3, w=0.75, h=0.9, lintel=None)
    H.near_only(mu.back)
    P.plinth(mg, h=0.6)
    P.quoins(mg, corners="r", z0=0.6, col="sand")
    b.gable_roof(7.8, 6.0, pitch=45, mat="tiles", x=1.2, y=3.9, z=7.6, ridge="x", eave=0.45, verge=0.3, sag=0.1)
    P.dormer(b, 2.0, 1.6, 8.15, w=1.0, h=0.9, depth=1.5, face=0, col="butter", roof="tiles")
    P.chimney(b, 4.2, 4.2, 9.2, 2.9, w=0.7, d=0.6, mat="brick", pots=2)
    lt = H.leanto(b, 2.6, 6.9, 5.0, 1.7, 2.5, rz=180, pitch=24, mat="masonry", col="warm", roof="tiles", plinth=0.5)
    P.door(lt.front, 1.2, w=0.9, h=1.9, col="green", frame="timber", z=0.08)
    P.window(lt.front, 3.6, 1.0, w=0.8, h=0.9, lintel="timber")
    P.chimney(b, 4.55, 8.0, 2.3, 2.7, w=0.6, d=0.55, mat="brick", pots=1)
    P.laundry(b, (-1.0, 8.2, 4.9), (4.55, 8.0, 4.75), n=6, sag=0.3)

    # ------------------------------------------------------------------ the long balcony on its posts
    BZ, YO = 3.0, -0.17
    b.box(6.2, 1.15, 0.14, "planks", col="greyoak", x=2.0, y=0.325, z=BZ - 0.14, bottom=True, lod=0)
    for x in (-0.95, 1.0, 3.05, 4.98):
        b.beam((x, YO, 0.0), (x, YO, BZ + 1.1), w=0.17, mat="timber", col="darkoak", lod=0)
        with b.detail(1):
            b.stone(0.4, 0.4, 0.22, mat="ashlar", col="sand", lod=1, x=x, y=YO, jitter=0.05)
            for dx in (-0.62, 0.62):
                if -1.0 < x + dx < 5.05:
                    b.beam((x, YO, BZ - 0.95), (x + dx, YO, BZ - 0.2), w=0.11, mat="timber", col="darkoak")
            b.beam((x, 0.9, BZ - 0.24), (x, YO - 0.12, BZ - 0.24), w=0.13, h=0.18, mat="timber", col="darkoak")
    with b.detail(1):
        b.beam((-1.1, YO, BZ - 0.22), (5.1, YO, BZ - 0.22), w=0.13, h=0.2, mat="timber", col="darkoak")
    P.railing(b, [(-1.0, YO, BZ), (5.02, YO, BZ), (5.02, 0.86, BZ)], h=0.96, style="balusters", col="darkoak", posts_at=2.0)
    for x in (0.05, 2.02, 4.0):
        P.planter(b, x, YO - 0.2, BZ + 0.5, w=1.3, d=0.22, h=0.2)
    P.lantern_at(b, 1.0, YO - 0.1, 2.35)
    P.lantern_at(b, 3.05, YO - 0.1, 2.35)

    # ------------------------------------------------------------------ outside: benches, a barrel table, the cellar flap
    P.bench(b, 3.5, 0.52, w=1.6)
    P.bench(b, -3.35, -0.38, w=1.6)
    P.barrel(b, 2.2, 0.05, r=0.33, h=0.82)
    with b.detail(2):
        for (mx, my) in ((2.1, 0.0), (2.32, 0.12)):
            b.box(0.09, 0.09, 0.12, "metal", col="brass", x=mx, y=my, z=0.82)
    with b.at(-1.75, 0.0, 0.0):      # the cellar flap, one leaf thrown back
        with b.detail(1):
            b.box(1.2, 0.95, 0.16, "masonry", col="warm", y=-0.47)
            b.quad((-0.5, -0.9, 0.18), (0.0, -0.9, 0.18), (0.0, -0.03, 0.6), (-0.5, -0.03, 0.6), "planks", col="green")
            b.quad((0.0, -0.9, 0.17), (0.5, -0.9, 0.17), (0.5, -0.03, 0.17), (0.0, -0.03, 0.17), "planks", col="#3a332d")
            b.quad((0.52, -0.9, 0.2), (0.95, -0.9, 0.62), (0.95, -0.03, 0.62), (0.52, -0.03, 0.2), "planks", col=shade("green", 0.8))
    P.barrel(b, -0.75, -0.6, r=0.3, h=0.8)
    P.planter(b, -0.5, 0.55, w=0.45, d=0.45, h=0.4, bush=True)
    PC.lamp_post(b, 4.9, -0.95, h=2.8)
