# The star-gazer's tower: the old astronomer keeps Larkhaven's clock and calendar from up here. The copper dome came up the hill in pieces on a donkey, and his study had to be hung outside because the stair took all the room within.
# Massing: the tallest, slenderest shaft in town on a battered foot; a stair turret clings to its back-left, a timber study hangs on brackets half-way up, and a stone gallery flares out under a ribbed dome with the telescope poking from its slit. A small lodge leans on the foot.
# Materials: warm rubble with pale ashlar bands and drum, verdigris copper dome, brass telescope and armillary, slate caps, cream plaster in dark oak for the study and lodge. Accent: navy.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Star-gazer's Tower", "kind": "tower", "lot": (8.0, 8.0), "lean": (0.0016, -0.001)}

CX, CY = 0.0, 4.05
RS = [(0.0, 2.78), (6.0, 2.56), (12.0, 2.40), (18.0, 2.26), (23.4, 2.12)]      # the shaft: (height, radius)
ZG = 25.0                                                                     # gallery floor
SEG = 20


def build(b):
    with b.at(CX, CY):
        shaft(b)
        turret(b)
        gallery(b)
        dome(b)
    lodge(b)


def shaft(b):
    PC.round_base(b, 2.78, h=1.1, out=0.3, door=(0, 2.4), seg=SEG)
    rings = []
    for i in range(4):                       # four lifts of masonry, an ashlar band at every joint
        (z0, r0), (z1, r1) = RS[i], RS[i + 1]
        t = PC.ring(b, r0, z1 - z0, r1=r1, mat="masonry", col="warm", z=z0, seg=SEG, seam=150, foot=False)
        t.cell = 2.6
        rings.append(t)
        if i:
            P.ring_band(b, r0 - 0.02, z0 - 0.12, h=0.24, out=0.1, seg=SEG, col="sand")
    PC.foot_disc(b, 2.78, 23.4)
    a, c, d, e = rings
    P.door(a, 0, w=1.1, h=2.3, arch=0.55, col="navy", z=0.5, steps=3, lamp=True)
    P.window(a, 300, 3.9, w=0.6, h=1.25, arch=0.3, bars=(1, 2))
    P.window(a, 84, 3.9, w=0.5, h=1.25, arch=0.25, lintel=None)
    P.window(c, 40, 1.1, w=0.62, h=1.25, arch=0.3, shutters="navy", box=True)
    P.window(c, 286, 3.3, w=0.6, h=1.2, arch=0.3)
    P.window(c, 196, 3.3, w=0.55, h=1.2, arch=0.27, shutters="navy")
    P.window(d, 96, 2.0, w=0.62, h=1.25, arch=0.3, shutters="navy")
    P.window(d, 186, 2.0, w=0.6, h=1.25, arch=0.3, shutters="navy", box=True)
    P.window(e, 18, 1.2, w=0.62, h=1.3, arch=0.31, shutters="navy")
    P.window(e, 276, 2.5, w=0.55, h=1.15, arch=0.27)
    P.window(e, 118, 2.5, w=0.5, h=1.15, arch=0.25, lintel=None)
    for t, n in ((a, 16), (c, 13), (d, 12), (e, 10)):
        P.stones(t, n=n, z0=0.3 if t is not a else 1.2, z1=t.h - 0.4, u1=t.w)
    P.ivy(a, 200, 0.6, w=2.8, h=5.2, n=13)
    P.ivy(c, 172, 0.0, w=1.8, h=3.0, n=6, lod=2)
    P.ivy(a, 118, 0.4, w=1.6, h=3.4, n=7, lod=2)
    study(b, d)


def study(b, t):
    """The study: a timber box on brackets, 13 m up the sunny side, with the moon dial in its gable."""
    w, dp, h = 2.2, 1.5, 2.65
    with t.on(325, 1.0):
        bd = b.body(w, dp, h, mat="plaster", col="cream", x=0, y=0.25 - dp / 2, z=0, depth=0.14, floor="planks", foot=False)
        P.timber_frame(bd.front, posts=[0, 0.42, 1.78, w], rails=[0, 0.86, h], braces=[(0, 0.86, 0.42, 0), (w, 0.86, 1.78, 0)], w=0.14)
        P.timber_frame(bd.right, u1=1.25, z1=h - 0.1, posts=[0, 1.25], rails=[0, 0.86, h - 0.1], braces=[(0, h - 0.1, 1.25, 0.86)], w=0.14)
        P.timber_frame(bd.left, u0=0.25, z1=h - 0.1, posts=[0.25, dp], rails=[0, 0.86, h - 0.1], braces=[(dp, h - 0.1, 0.25, 0.86)], w=0.14)
        P.window(bd.front, w / 2, 0.98, w=1.2, h=1.3, bars=(2, 1), lintel=None, box=True, depth=0.12)
        P.window(bd.left, 0.9, 1.05, w=0.5, h=0.9, lintel=None, sill=False, depth=0.12)
        rise = bd.gable(ridge="y", pitch=52, mat="slate", eave=0.16, verge=0.2, course=0.32, thick=0.1)
        P.clock(bd.front, w / 2, h + rise * 0.4, r=0.4, face="navy", hands="ivory", rim="brass", hour=8, minute=22)
        with b.detail(1):
            for sx in (-1, 1):
                b.beam((sx * 0.86, 0.04, -1.55), (sx * 0.86, -1.16, -0.06), w=0.17)
                b.beam((sx * 0.86, 0.04, -0.1), (sx * 0.86, -1.3, -0.1), w=0.15, h=0.17)
            b.beam((-w / 2 - 0.06, -1.2, -0.1), (w / 2 + 0.06, -1.2, -0.1), w=0.15, h=0.17)
        with b.detail(2):
            for i in range(5):
                x = -0.8 + 0.4 * i
                b.beam((x, -0.9, -0.09), (x, -1.34, -0.09), w=0.09, h=0.12)


def turret(b):
    """The stair turret clinging to the back-left of the shaft, stopping short of the gallery."""
    tx, ty, _ = PC.polar(2.72, 240)
    PC.round_base(b, 1.02, h=0.8, out=0.2, seg=12, x=tx, y=ty)
    tr = PC.ring(b, 1.02, 19.0, r1=0.94, col=mix("warm", "grey", 0.45), x=tx, y=ty, seg=12, seam=60, depth=0.22)
    tr.cell = 4.2
    for deg, z in ((240, 3.2), (268, 8.1), (216, 12.6), (244, 16.6)):
        PC.slit(tr, deg, z, w=0.2, h=1.05)
    for z in (6.0, 12.0, 18.0):
        P.ring_band(b, tr.radius(z) - 0.02, z - 0.1, h=0.2, out=0.07, seg=12, x=tx, y=ty)
    b.cone_roof(0.94, 2.5, mat="slate", x=tx, y=ty, z=19.0, seg=12, eave=0.3, flare=0.42, course=0.72)
    P.ivy(tr, 300, 0.4, w=1.2, h=3.6, n=6, lod=2)


def gallery(b):
    """The dome gallery: a stone walk on a corbelled flare, iron rail with brass knobs, open at the front."""
    with b.at(z=ZG):
        b.disc(3.8, "flagstone", col="sand", seg=SEG, r_in=2.05)
        PC.lathe(b, [(2.12, -1.6), (2.3, -1.45), (2.3, -1.25), (2.75, -0.55), (2.75, -0.42), (3.66, -0.24), (3.66, -0.2), (3.8, -0.2), (3.8, 0.0)],
                 "ashlar", col="sand", seg=SEG)
        PC.corbels(b, 2.3, -0.26, n=16, out=1.3, drop=0.85, w=0.3, steps=3, col="sand")
        PC.rail_arc(b, 3.68, 24, 352, h=1.05, style="iron", knobs="brass")
        px, py, _ = PC.polar(2.98, 8)
        with b.at(px, py):
            P.landing_mark(b, 0.72)
        b.pad(px, py, 0.0, radius=0.78, face=8, name="Dome gallery")
        cx, cy, _ = PC.polar(2.85, 158)
        P.crate(b, cx, cy, 0, s=0.5, rz=25)
        sx, sy, _ = PC.polar(2.9, 182)
        P.barrel(b, sx, sy, 0, r=0.22, h=0.55)
        with b.at(rz=138):                   # the hoist: how the instruments (and the coal) come up
            with b.detail(1):
                b.beam((0, -3.45, 0), (0, -3.45, 2.5), w=0.16)
                b.beam((0, -2.7, 2.3), (0, -4.62, 2.3), w=0.14, h=0.16)
                b.beam((0, -3.45, 1.2), (0, -4.3, 2.22), w=0.11)
                b.beam((0, -3.45, 1.5), (0, -2.75, 2.24), w=0.1)
                b.beam((0, -4.55, 2.24), (0, -4.55, -11.6), w=0.035, mat="cloth", col="#8a7a66", caps=False)
            with b.at(0, -4.55, -12.2):
                P.crate(b, 0, 0, 0, s=0.58, rz=20)
                with b.detail(2):
                    for sx2 in (-1, 1):
                        b.beam((sx2 * 0.27, 0, 0.56), (0, 0, 0.95), w=0.025, mat="cloth", col="#8a7a66", caps=False)
                        b.beam((0, sx2 * 0.27, 0.56), (0, 0, 0.95), w=0.025, mat="cloth", col="#8a7a66", caps=False)


def dome(b):
    dr = PC.ring(b, 2.12, 2.6, mat="ashlar", col="sand", z=ZG, seg=SEG, seam=195, foot=False)
    P.door(dr, 55, w=0.85, h=1.95, z=0.03, arch=0.4, col="navy", frame="stone")
    for a in (150, 300):
        P.window(dr, a, 0.95, w=0.5, h=1.1, arch=0.25, lintel=None)
    P.lantern(dr, 80, 1.75)
    P.ring_band(b, 2.1, ZG + 2.42, h=0.2, out=0.15, seg=SEG)
    zd = ZG + 2.6
    sec = PC.dome_section(2.2, 2.75, n=7, eave=0.2, drop=0.1, power=0.9)
    b.cone_roof(2.12, 2.75, mat="metal", col="copper", z=zd, seg=SEG, section=sec, course=0.5, lip=0.035, finial=False)
    with b.at(z=zd):
        PC.ribs(b, sec, n=10, w=0.11, proud=0.05, col=shade("copper", 0.7), phase=0.5)
        with b.at(rz=297):                   # the slit, and the telescope looking out of it
            hw = 0.3
            for i in range(1, 5):
                (ra, za), (rb, zb) = sec[i], sec[i + 1]
                b.quad((-hw, -ra * 1.025, za + 0.05), (hw, -ra * 1.025, za + 0.05), (hw, -rb * 1.025, zb + 0.05), (-hw, -rb * 1.025, zb + 0.05), "paint", col="!#15171b", lod=1)
                for sx in (-1, 1):
                    b.beam((sx * hw, -ra * 1.03, za + 0.07), (sx * hw, -rb * 1.03, zb + 0.07), w=0.07, h=0.07, mat="metal", col="brass", lod=2, caps=False, up=(0, -1, 0))
            el = rad(40)
            dv = (0.0, -math.cos(el), math.sin(el))
            p0 = (0.0, -0.3, 0.75)
            at = lambda s: vadd(p0, vmul(dv, s))
            b.tube(at(0.0), at(3.6), r=0.17, r1=0.23, mat="metal", col="brass", lod=0, n=8)
            b.tube(at(3.0), at(3.66), r=0.285, mat="metal", col="brass", lod=1, n=8, caps=True)
            for s in (1.9, 2.45):
                b.tube(at(s), at(s + 0.08), r=0.245, mat="metal", col=shade("brass", 0.75), lod=2, n=8)
            nrm = (0.0, math.sin(el), math.cos(el))                     # upward normal of the tube
            fa, fb = vadd(at(1.8), vmul(nrm, 0.32)), vadd(at(2.9), vmul(nrm, 0.32))
            b.tube(fa, fb, r=0.055, mat="metal", col="brass", lod=2, n=5, caps=True)
            c = at(3.67)
            ring_pts = [vadd(c, vadd(vmul((1, 0, 0), 0.24 * math.cos(2 * math.pi * i / 8)), vmul(nrm, 0.24 * math.sin(2 * math.pi * i / 8)))) for i in range(8)]
            b.face(list(reversed(ring_pts)), "glass", lod=1)
    PC.armillary(b, 0, 0, zd + 2.68, r=0.4, pole=0.7)


def lodge(b):
    """The lodge at the foot: one room and a hearth, its roof running into the tower."""
    bd = b.body(2.05, 2.75, 2.45, mat="plaster", col="cream", x=2.53, y=1.75)
    PC.plinth(bd, h=0.55, doors=[("left", 2.1, 0.75)])
    P.exposed(bd.front, "corners", n=6)
    P.window(bd.front, 1.05, 1.0, w=0.8, h=1.1, shutters="navy", box=True)
    P.window(bd.right, 1.3, 1.1, w=0.6, h=0.9, lintel="timber")
    P.door(bd.left, 2.1, w=0.75, h=1.85, col="navy", z=0.18, frame="timber", steps=1)
    bd.gable(ridge="y", pitch=50, mat="tiles", eave=0.25, verge=0.3, sag=0.05)
    P.chimney(b, 3.2, 2.5, 2.3, 2.7, w=0.5, d=0.45, mat="brick", pots=1)
    P.barrel(b, 1.95, -0.05, r=0.26, h=0.7)
    P.planter(b, 3.0, 0.1, w=0.8)
    P.bench(b, -2.2, 0.75, rz=-28, w=1.2)
