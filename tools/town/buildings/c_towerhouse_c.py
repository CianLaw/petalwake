# The Pilot's tower-house: built eight-sided by a river pilot who wanted a window toward every wind. His crow's nest is still the first place on the hill to see a sail, and the flag goes up when one is sighted.
# Massing: an eight-sided stone tower, tapering, under a jettied timber-framed top storey; a steep bell-cast pavilion roof cut off short for a railed crow's nest with a tall flagpole lashed to it; dormers in the roof, a porch at the door.
# Materials: grey-warm rubble, butter plaster in dark oak, silvered shingles. Accent: mustard.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Pilot's Tower-house", "kind": "tower", "lot": (7.0, 7.0), "lean": (0.0007, 0.001)}

CY = 3.5
R, ZS, TAPER = 3.3, 8.4, 0.93                     # the stone part
RT, HT = 3.42, 3.1                                # the timber storey
ZE = ZS + HT                                      # eaves
SEC = [(3.52, -0.2), (2.98, 0.78), (1.55, 6.3)]  # the roof: (corner radius, height above the eaves)
ZN = ZE + SEC[-1][1] + 0.07                       # the crow's nest floor
STONE = mix("warm", "grey", 0.3)


def build(b):
    with b.at(0, CY):
        stone(b)
        timber(b)
        roof(b)
        nest(b)
    P.bench(b, -1.9, 0.0, rz=18, w=1.2); P.barrel(b, 1.75, 0.05, r=0.27, h=0.72); P.crate(b, 2.3, 0.3, s=0.5, rz=24)


def stone(b):
    f = PC.poly_tower(b, 8, R, ZS, taper=TAPER, mat="masonry", col=STONE)
    w = f[0].w
    PC.poly_plinth(b, 8, R, h=0.9, out=0.12, col=STONE, doors=[(0, w / 2, 0.95), (4, w / 2, 0.8)])
    P.door(f[0], w / 2, w=0.95, h=2.05, arch=0.48, col="mustard", z=0.42, steps=2, lamp=True, porch="gable")
    P.window(f[7], w / 2, 2.0, w=0.7, h=1.2, arch=0.3, shutters="mustard", box=True)
    P.window(f[1], w / 2, 2.4, w=0.6, h=1.0, arch=0.26, bars=(1, 2))
    P.window(f[0], w / 2, 5.3, w=0.8, h=1.35, arch=0.36, shutters="mustard", box=True)
    P.window(f[6], w / 2, 5.0, w=0.7, h=1.25, arch=0.32, shutters="mustard")
    P.window(f[2], w / 2, 5.4, w=0.7, h=1.25, arch=0.32)
    P.window(f[3], w / 2, 2.2, w=0.6, h=1.0, arch=0.26)
    P.window(f[4], w / 2, 5.2, w=0.7, h=1.25, arch=0.32, shutters="mustard")
    P.window(f[5], w / 2, 2.6, w=0.6, h=1.0, arch=0.26, bars=(1, 2))
    P.door(f[4], w / 2, w=0.8, h=1.9, col="mustard", z=0.14, frame="timber")
    for k in (0, 2, 5, 7):
        P.stones(f[k], n=7, z0=1.0, z1=ZS - 0.6)
    P.exposed(f[6], "base", n=6, col="grey")
    P.ivy(f[3], w * 0.7, 0.5, w=1.6, h=4.8, n=10)
    P.ivy(f[5], w * 0.3, 0.5, w=1.3, h=3.0, n=5, lod=2)
    with b.at(rz=22.5):
        P.ring_band(b, R * (1 - (1 - TAPER) * 3.4 / ZS) - 0.03, 3.4, h=0.18, out=0.1, seg=8)


def timber(b):
    """The jettied top storey: a window toward every wind."""
    f = PC.poly_tower(b, 8, RT, HT, mat="plaster", col="butter", z=ZS, depth=0.14)
    w = f[0].w
    for k, wl in enumerate(f):
        P.timber_frame(wl, z1=HT - 0.08, posts=[0, 0.62, w - 0.62, w], rails=[0, 0.92, HT - 0.08], braces=[(0, 0.92, 0.62, 0), (w, 0.92, w - 0.62, 0)] if k % 2 else [(0.62, 0, w - 0.62, 0.92), (0.62, 0.92, w - 0.62, 0)], w=0.15)
        P.window(wl, w / 2, 1.05, w=0.95, h=1.25, lintel=None, depth=0.11, shutters="mustard" if k in (0, 3, 6) else None, box=k in (1, 7))
    rs = R * TAPER
    with b.at(z=ZS, rz=22.5):
        b.disc(RT, "planks", col="darkoak", seg=8, r_in=rs - 0.1, down=True)
        with b.detail(1):
            for k in range(8):
                with b.at(rz=45 * k):                # a bracket under every corner, joist ends between
                    b.beam((0, -(rs - 0.02), -1.0), (0, -(RT - 0.06), -0.06), w=0.16)
        with b.detail(2):
            for k in range(8):
                with b.at(rz=45 * k + 22.5):
                    ap = RT * math.cos(math.pi / 8)
                    for x in (-0.8, -0.4, 0.0, 0.4, 0.8):
                        b.beam((x, -(ap - 0.5), -0.09), (x, -(ap + 0.05), -0.09), w=0.11, h=0.14)


def roof(b):
    with b.at(z=ZE, rz=22.5):
        b.cone_roof(RT, SEC[-1][1], mat="shingle", seg=8, smooth=False, section=SEC, course=0.46, lip=0.05, finial=False)
        with b.detail(1):                             # hip rolls down the eight arrises
            for k in range(8):
                with b.at(rz=45 * k):
                    for (ra, za), (rb, zb) in zip(SEC, SEC[1:]):
                        b.beam((0, -ra, za + 0.05), (0, -rb, zb + 0.05), w=0.16, h=0.1, mat="shingle", col="#b8b3a8", caps=False, up=(0, -1, 0))
    for deg, zz in ((315, 2.0), (90, 2.3), (180, 2.0)):
        rr = (SEC[1][0] - (SEC[1][0] - SEC[2][0]) * (zz - SEC[1][1]) / (SEC[2][1] - SEC[1][1])) * math.cos(math.pi / 8)
        x, y, _ = PC.polar(rr + 0.42, deg)
        P.dormer(b, x, y, ZE + zz - 0.25, w=1.0, h=1.0, depth=1.2, face=deg, roof="shingle", col="butter", shutters="mustard" if deg == 315 else None, pitch=50)
    x, y, _ = PC.polar(2.42, 135)
    with b.at(x, y, ZE + 1.0, rz=135):
        P.chimney(b, 0, 0, 0, 3.6, w=0.6, d=0.55, mat="brick", pots=2)


def nest(b):
    """The crow's nest: an eight-sided deck on the cut-off roof, railed, open to the front; flagpole, hatch."""
    rn = 1.85
    with b.at(z=ZN, rz=22.5):
        b.disc(rn, "planks", col="greyoak", seg=8)
        b.disc(rn, "planks", col=shade("darkoak", 0.8), seg=8, z=-0.13, down=True, r_in=1.3)
        b.revolve([(rn, -0.13), (rn, 0.0)], "planks", col="darkoak", seg=8, smooth=False)
        P.railing(b, P.circle(rn - 0.1, 7, 0.0, 0, 315), h=1.0, style="balusters", col="darkoak", posts_at=2.0)
        with b.detail(1):
            for k in range(8):
                with b.at(rz=45 * k):
                    b.beam((0, -1.45, -0.75), (0, -(rn - 0.08), -0.14), w=0.12)
        fx, fy, _ = PC.polar(rn - 0.12, 180)
        P.flag(b, fx, fy, -0.4, pole=5.6, w=2.1, h=0.85, col="stripe_yellow", kind="pennant")
        with b.detail(2):
            for zz in (0.25, 0.85):
                b.box(0.16, 0.16, 0.06, "metal", col="iron", x=fx, y=fy, z=zz)
    with b.at(z=ZN):
        with b.at(0, -0.42):
            P.landing_mark(b, 0.74)
        b.pad(0, -0.42, 0.0, radius=0.8, face=0, name="Crow's nest")
        PC.hatch(b, 0.78, 0.92, 0.0, w=0.66, d=0.66, rz=-45)
        P.lantern_at(b, -1.2, 0.95, 1.2, arm=0.0)
