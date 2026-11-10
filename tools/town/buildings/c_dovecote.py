# The dovecote: the Crown's doves have carried the town's small messages for longer than anyone remembers. The birds live in the wall, the keeper in the lantern on top, and the walk round it is where a rider leaves the post.
# Massing: a short stout round tower on a battered stone foot, lime-washed above a rat-ledge; three rows of flight holes over perch ledges; a corbelled stone walk round a small boarded lantern under a flared conical cap with a dove for a vane.
# Materials: warm rubble foot, cream limewash with the stones showing through, pale ashlar ledges, ivory rail, grey-blue slate cap. Accent: blue.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Dovecote", "kind": "tower", "lot": (6.0, 6.0), "lean": (0.0015, 0.001)}

CX, CY = 0.0, 2.96
ZA, ZW = 3.4, 9.4             # rat-ledge, lantern walk
SEG = 20


def build(b):
    with b.at(CX, CY):
        shaft(b)
        walk(b)
        lantern(b)
    yard(b)


def shaft(b):
    PC.round_base(b, 2.42, h=0.9, out=0.28, door=(0, 2.1), seg=SEG)
    a = PC.ring(b, 2.42, ZA, r1=2.33, mat="masonry", col="warm", seg=SEG, seam=200, foot=False)
    PC.foot_disc(b, 2.42, ZW)
    P.door(a, 0, w=0.95, h=2.0, arch=0.45, col="blue", z=0.42, steps=2, lamp=True)
    P.window(a, 262, 1.5, w=0.55, h=0.95, arch=0.25, bars=(1, 1))
    P.stones(a, n=16, z0=1.0, z1=3.0, u1=a.w)
    P.ring_band(b, 2.31, ZA - 0.1, h=0.2, out=0.2, seg=SEG)                  # the rat-ledge
    c = PC.ring(b, 2.33, ZW - ZA, r1=2.15, mat="plaster", col="cream", z=ZA, seg=SEG, seam=200, foot=False, depth=0.24)
    c.cell = 3.0
    spots = []
    for k, zr in enumerate((1.75, 3.05, 4.35)):                              # three rows of flight holes, each over its perch ledge
        P.ring_band(b, c.radius(zr) - 0.02, ZA + zr - 0.11, h=0.07, out=0.19, seg=SEG, lod=1)
        for i in range(9):
            deg = 10 + 40 * i + 20 * (k % 2)
            c.cut(deg, zr, 0.3, 0.38, pane="paint", pane_col="!#1b1816", depth=0.2)
            if b.chance(0.3):
                spots.append((deg + b.r(8, 30), ZA + zr - 0.04, c.radius(zr) + 0.1))
    P.window(c, 304, 0.45, w=0.6, h=0.95, shutters="blue", box=True)
    P.window(c, 120, 0.45, w=0.6, h=0.95, shutters="blue")
    P.stones(c, n=18, proud=0.035, mat="masonry", col="warm", z0=0.0, z1=1.5, size=(0.26, 0.5))
    P.stones(c, n=8, proud=0.035, mat="masonry", col="warm", z0=3.6, z1=5.6, size=(0.26, 0.46))
    P.ivy(a, 150, 0.5, w=2.2, h=3.4, n=9)
    P.ivy(c, 164, 0.0, w=1.5, h=2.4, n=5, lod=2)
    for deg, z, r in spots:
        x, y, _ = PC.polar(r, deg)
        PC.dove(b, x, y, z, rz=deg + b.r(-40, 40))


def walk(b):
    """The lantern walk: stone, corbelled out, with an ivory rail left open at the front for the rider."""
    PC.stone_walk(b, 1.25, 2.84, ZW, seg=SEG, r_foot=2.15, drop=1.05)
    PC.corbels(b, 2.18, ZW - 0.24, n=12, out=0.62, drop=0.62, w=0.26, steps=2)
    with b.at(z=ZW):
        PC.rail_arc(b, 2.74, 21, 339, h=0.95, style="balusters", col="ivory", mat="planks")
        x, y, _ = PC.polar(2.03, 0)
        with b.at(x, y):
            P.landing_mark(b, 0.7)
        b.pad(x, y, 0.0, radius=0.75, face=0, name="Lantern walk")
        P.sack(b, *PC.polar(2.25, 205)[:2], 0, r=0.26)
        P.crate(b, *PC.polar(2.3, 232)[:2], 0, s=0.42, rz=20)
        for deg in (64, 118, 171, 262, 301):
            x, y, _ = PC.polar(2.74, deg)
            PC.dove(b, x, y, 1.0, rz=deg + b.r(-60, 60))


def lantern(b):
    lt = PC.ring(b, 1.25, 3.0, r1=1.2, mat="planks", col="#d9cdb6", z=ZW, seg=16, seam=250, foot=False, depth=0.16)
    P.door(lt, 52, w=0.75, h=1.85, z=0.03, col="blue", frame="timber")
    P.lantern(lt, 20, 1.75)
    for deg in (140, 200, 300, 345):
        lt.cut(deg, 2.0, 0.28, 0.42, arch=0.14, pane="paint", pane_col="!#1b1816", depth=0.14)
        with lt.on(deg, 1.93):
            b.box(0.5, 0.2, 0.05, "planks", col="darkoak", x=0, y=-0.08, z=0, lod=2, bottom=True)
    with b.at(z=ZW):
        with b.detail(1):
            for i in range(8):                                               # cover strips: it is a boarded drum
                with b.at(rz=22.5 + 45 * i):
                    b.beam((0, -1.26, 0.0), (0, -1.21, 2.98), w=0.1, h=0.05, col="darkoak", caps=False, up=(0, -1, 0))
        P.ring_band(b, 1.2, 2.86, h=0.14, out=0.08, mat="timber", col="darkoak", seg=16)
    zc = ZW + 3.0
    b.cone_roof(1.2, 2.8, mat="slate", z=zc, seg=SEG, eave=0.47, flare=0.6, course=0.45, finial=False)
    PC.vane(b, 0, 0, zc + 2.72, h=1.5, shape="dove", size=1.1)
    with b.at(z=zc):
        for deg, r, z in ((30, 1.25, 0.42), (200, 0.9, 0.98), (290, 1.45, 0.12)):
            x, y, _ = PC.polar(r, deg)
            PC.dove(b, x, y, z, rz=deg + 90)


def yard(b):
    P.sack(b, 1.35, 0.0, r=0.3); P.sack(b, 1.85, 0.2, r=0.26); P.barrel(b, -1.45, 0.05, r=0.28, h=0.75)
    with b.at(-2.2, 1.35, 0, rz=-52):
        P.ladder(b, 3.6)
    PC.doves(b, [(0.9, -0.5, 0), (1.25, -0.75, 0), (-0.7, -0.6, 0)])
