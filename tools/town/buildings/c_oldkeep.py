# The old round keep, turned hostel: the oldest thing on the hill. A storm took one side of its top two hundred years ago; nobody rebuilt it, they put a little hall in the gap and hung a veranda where the wall had been. Riders are welcome: the beds are cheap and the stew is good.
# Massing: a broad battered drum, 4.5 m in radius; its upper storey a roofless shell broken away at the front-left, with one tall tooth of old wall and empty windows. In the break a timber hall with a steep roof and a veranda deck on struts over the edge.
# Materials: old grey-warm rubble, turf on the wall-head, dark oak and cream plaster, red tiles on the hall. Accent: red.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Old Keep Hostel", "kind": "tower", "lot": (11.0, 11.0), "lean": (-0.0012, 0.0008)}

CX, CY = 0.0, 5.5
R0, R1 = 4.85, 4.5
ZT = 13.6                     # the top floor, where the hall and the veranda are
STONE = mix("warm", "grey", 0.5)
BRK = 327.0                   # compass middle of the break (front-left, into the sun)


def rk(z):
    return R0 + (R1 - R0) * z / ZT


def build(b):
    with b.at(CX, CY):
        drum(b)
        top(b)
        with b.at(z=ZT, rz=BRK):
            hall(b)
        veranda(b)


def drum(b):
    PC.round_base(b, R0, h=1.2, out=0.3, door=(0, 2.7), col=STONE)
    lifts = []
    for z0, z1 in ((0.0, 4.6), (4.6, 9.2), (9.2, ZT)):
        t = PC.ring(b, rk(z0), z1 - z0, r1=rk(z1), mat="masonry", col=STONE, z=z0, seam=165, foot=False, depth=0.36)
        t.cell = 2.6
        lifts.append(t)
    PC.foot_disc(b, R0, ZT)
    a, c, d = lifts
    P.door(a, 0, w=1.3, h=2.5, arch=0.65, col="red", z=0.55, steps=3, lamp=True, double=True)
    P.sign(a, 17, 3.75, emblem="moon", col="mustard", board="red")
    for deg in (315, 62, 250):
        P.window(a, deg, 2.3, w=0.7, h=1.2, arch=0.32, bars=(1, 2))
    P.door(a, 205, w=0.85, h=1.9, col="red", z=0.3, steps=1, frame="timber")
    P.window(c, 336, 1.25, w=0.8, h=1.4, arch=0.36, shutters="red", box=True)
    P.window(c, 38, 1.25, w=0.8, h=1.4, arch=0.36, shutters="red")
    P.window(c, 262, 1.25, w=0.8, h=1.4, arch=0.36, shutters="red", box=True)
    P.window(c, 205, 1.25, w=0.8, h=1.4, arch=0.36, shutters="red")
    P.balcony(c, 128, 1.05, w=2.0, out=1.0, rail="balusters")
    P.door(c, 128, w=0.9, h=2.0, z=1.07, col="red", frame="timber")
    P.window(d, 2, 1.2, w=0.9, h=1.5, arch=0.4, shutters="red", box=True)
    P.window(d, 78, 1.2, w=0.75, h=1.35, arch=0.34, shutters="red")
    P.window(d, 222, 1.2, w=0.75, h=1.35, arch=0.34)
    P.window(d, 296, 1.2, w=0.75, h=1.35, arch=0.34, shutters="red", box=True)
    P.ring_band(b, rk(4.6) - 0.02, 4.5, h=0.2, out=0.09, col="grey")
    P.ring_band(b, rk(10.7) - 0.02, 10.6, h=0.18, out=0.08, col="grey")
    for t, n in ((a, 26), (c, 24), (d, 20)):
        P.stones(t, n=n, z0=0.3 if t is not a else 1.3, z1=t.h - 0.3, u1=t.w, size=(0.34, 0.7))
    P.ivy(a, 150, 0.4, w=3.2, h=4.0, n=12)
    P.ivy(c, 160, 0.0, w=2.6, h=4.4, n=9, lod=2)
    P.ivy(d, 172, 0.0, w=2.2, h=4.2, n=8, lod=2)
    P.ivy(a, 285, 0.4, w=2.0, h=3.2, n=7, lod=2)
    P.laundry(b, PC.polar(5.5, 120, 6.7), PC.polar(4.74, 92, 7.6), n=4, sag=0.3)
    P.barrel(b, *PC.polar(5.45, 20)[:2]); P.crate(b, *PC.polar(5.5, 31)[:2], rz=20); P.bench(b, *PC.polar(5.65, 338)[:2], rz=-22, w=1.4)


def top(b):
    """The roofless upper storey: floor, the broken shell, turf and rubble."""
    b.disc(R1 - 0.02, "flagstone", col="grey", z=ZT, seg=24)
    sky = [(44, 0.5), (60, 1.6), (76, 2.7), (96, 3.1), (118, 2.8), (131, 3.3), (139, 5.2), (171, 5.4), (179, 3.5), (200, 3.0), (222, 2.6), (237, 1.5), (252, 0.6)]
    sh = PC.shell(b, R1, 5.4, thick=0.95, mat="masonry", col=STONE, z=ZT, seg=30, arc=(44, 252), skyline=sky, crumble=0.55, grass=0.7)
    sh.cut(155, 1.7, 1.0, 2.7, arch=0.5, pane=None)
    sh.cut(102, 1.0, 0.8, 1.5, arch=0.4, pane=None)
    sh.cut(207, 1.0, 0.8, 1.5, arch=0.4, pane=None)
    P.stones(sh, n=16, z0=0.2, z1=2.4, size=(0.34, 0.7))
    P.ivy(sh, 164, 0.0, w=1.6, h=3.6, n=6)
    with b.at(z=ZT):
        for deg, r in ((48, 3.9), (246, 4.0), (64, 3.1), (232, 3.2)):          # rubble where the wall gave way
            x, y, _ = PC.polar(r, deg)
            with b.at(x, y, 0.0, rz=deg + b.r(-30, 30)):
                b.stone(b.r(0.4, 0.7), b.r(0.3, 0.5), b.r(0.2, 0.35), mat="masonry", col=STONE, lod=2)
        for deg, r in ((80, 2.9), (120, 3.2), (200, 3.1), (225, 2.6), (95, 2.2)):
            x, y, _ = PC.polar(r, deg)
            PC.tuft(b, x, y, 0.0, r=b.r(0.2, 0.34))
    b.pad(*PC.polar(4.25, BRK, ZT + 0.12), radius=0.95, face=BRK, name="Hostel veranda")


def hall(b):
    """The little hall in the break (frame: its front looks out through the break)."""
    w, dp, h = 4.3, 2.7, 2.9
    bd = b.body(w, dp, h, mat="plaster", col="cream", x=0.3, y=0.4 + dp / 2, z=0.0, depth=0.16)
    P.timber_frame(bd.front, z1=h - 0.1, posts=[0, 0.95, 2.05, 3.05, w], rails=[0, 1.0, h - 0.1], braces=[(0, 1.0, 0.95, 0), (w, 1.0, 3.05, 0)])
    P.timber_frame(bd.left, braces="x", posts=[0, dp / 2, dp])
    P.timber_frame(bd.right, braces="x", posts=[0, dp / 2, dp])
    P.door(bd.front, 2.55, w=0.9, h=1.95, col="red", z=0.05, frame="timber", lamp=True)
    P.window(bd.front, 1.5, 1.1, w=0.8, h=1.0, lintel=None, shutters="red", depth=0.12)
    P.window(bd.front, 3.68, 1.1, w=0.7, h=1.0, lintel=None, shutters="red", depth=0.12)
    rise = bd.gable(ridge="x", pitch=52, mat="tiles", eave=0.25, verge=0.3, sag=0.08)
    P.chimney(b, -1.0, 2.55, 2.4, 3.4, w=0.6, d=0.5, mat="masonry", col=STONE, pots=2)
    # the pentice over the door, on three posts
    with b.detail(1):
        for x in (-1.65, 0.45, 2.3):
            b.beam((x, -1.0, 0.0), (x, -1.0, 2.06), w=0.14)
            b.beam((x, -1.0, 1.6), (x + (0.4 if x < 2 else -0.4), -1.0, 2.05), w=0.09)
        b.beam((-1.8, -1.0, 2.12), (2.45, -1.0, 2.12), w=0.14, h=0.14)
    PC.shed_roof(b, 4.5, 1.6, pitch=13, z=2.19, x=0.3, y=0.46, mat="tiles", eave=0.16, verge=0.1, course=0.36, thick=0.1, barge=False)
    P.bench(b, -0.9, 0.05, 0.0, rz=0, w=1.3)
    P.planter(b, 1.55, -0.05, 0.0, w=0.7)


def veranda(b):
    """The deck hung where the wall had been: boards on oak struts, a rail open at the middle of the break."""
    a0, a1 = BRK - 71, BRK + 71
    zd = ZT + 0.12
    PC.deck_arc(b, 2.3, 5.3, a0, a1, z=zd, thick=0.16, seg=14)
    with b.at(z=zd):
        n = 9
        with b.detail(1):
            for i in range(n):
                a = a0 + 4 + (a1 - a0 - 8) * i / (n - 1)
                with b.at(rz=a):
                    b.beam((0, -(R1 + 0.02), -2.5), (0, -5.18, -0.18), w=0.17)
                    b.beam((0, -(R1 - 0.3), -0.25), (0, -5.3, -0.25), w=0.15, h=0.16)
            b.revolve([(5.24, -0.36), (5.24, -0.17)], "timber", col="darkoak", seg=14, a0=a0, a1=a1)
        PC.rail_arc(b, 5.2, a0 + 1, BRK - 13, style="balusters", col="darkoak", h=1.0)
        PC.rail_arc(b, 5.2, BRK + 13, a1 - 1, style="balusters", col="darkoak", h=1.0)
        for da in (-13, 13):                 # two lantern posts mark the way in
            x, y, _ = PC.polar(5.2, BRK + da)
            with b.detail(1):
                b.beam((x, y, 0), (x, y, 2.35), w=0.13)
            P.lantern_at(b, x, y, 2.0, arm=0.28)
        x, y, _ = PC.polar(4.25, BRK)
        with b.at(x, y):
            P.landing_mark(b, 0.88)
        PC.banner(b, *PC.polar(5.36, BRK + 47, -0.42), w=0.85, h=2.5, col="stripe_red", stripe="linen", rz=BRK + 47)
        PC.banner(b, *PC.polar(5.36, BRK - 44, -0.42), w=0.85, h=2.5, col="stripe_red", stripe="linen", rz=BRK - 44)
        P.barrel(b, *PC.polar(4.7, BRK - 58)[:2], 0); P.crate(b, *PC.polar(4.4, BRK - 47)[:2], 0, rz=15, s=0.5)
        P.sack(b, *PC.polar(4.6, BRK + 56)[:2], 0); P.planter(b, *PC.polar(4.75, BRK + 44)[:2], 0, w=0.8, bush=True)
        PC.cat(b, *PC.polar(4.55, BRK - 40)[:2], 0, rz=BRK - 100, col="#2f2b2a")
