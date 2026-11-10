# The shot tower: molten lead is poured through a sieve at the top and falls the whole height into a water butt, cooling into round shot on the way; the lead goes up by the davit, and the hoist stage is where the rider lands.
# A slender tapering round brick shaft, a pale stone gallery flaring out of it lighthouse-fashion with a square timber stage standing out toward the street corner, a small lime-washed lantern drum and a ribbed copper dome.
# Warm red brick with iron tie bands, sand-coloured stone, cream drum, verdigris copper; accent green.
from kit import *
import parts as P
import parts_c as PC
import parts_k as K

META = {"name": "The Shot Tower", "kind": "tower", "lot": (5.0, 5.0)}

ZG = 19.0                       # the gallery floor
PROF = [(0.0, 2.0), (6.0, 1.78), (12.0, 1.6), (17.6, 1.45)]


def build(b):
    with b.at(0.0, 2.5):
        tower(b)


def tower(b):
    b.footprint(-2.35, -2.35, 2.35, 2.35, ZG)
    # ------------------------------------------------------------------ the shaft
    t = b.round(2.0, 17.6, profile=PROF, mat="brick", seg=20, depth=0.34)
    P.round_base(b, 2.0, h=1.0, out=0.26, ring=t, seg=20)
    P.door(t, 0, w=1.0, h=2.2, z=0.34, arch=0.5, col="green", steps=2, lamp=True)
    for deg, zz in ((300, 4.0), (60, 6.9), (180, 9.6), (300, 12.6), (60, 15.0)):
        P.window(t, deg, zz, w=0.55, h=1.1, arch=0.27, frame="ivory", bars=(1, 2))
    P.stones(t, n=34, size=(0.3, 0.5), proud=0.05, z0=1.1, z1=17.0)
    P.ivy(t, 205, 0.4, w=2.2, h=5.2, n=12)
    for zz in (6.0, 12.0, 17.36):
        P.ring_band(b, t.radius(zz), zz, h=0.2, out=0.07, col="sand", seg=20)
    with b.detail(2):
        for zz in (3.2, 9.0, 14.6):
            rr = t.radius(zz) + 0.02
            b.revolve([(rr, zz - 0.05), (rr, zz + 0.05)], "metal", col="iron", seg=20)

    # ------------------------------------------------------------------ the gallery and the hoist stage
    PC.stone_walk(b, 1.2, 2.2, ZG, seg=20, r_foot=1.45, drop=1.4, col="sand", floor_col="sand")
    zs = ZG + 0.02
    b.box(1.63, 1.63, 0.16, "planks", col="greyoak", x=-1.515, y=-1.515, z=zs - 0.16, bottom=True, lod=0)
    with b.detail(1):
        b.beam((-2.33, -2.28, zs - 0.11), (-0.7, -2.28, zs - 0.11), w=0.1, h=0.24, col="darkoak", up=(0, 0, 1))
        b.beam((-2.28, -2.33, zs - 0.11), (-2.28, -0.7, zs - 0.11), w=0.1, h=0.24, col="darkoak", up=(0, 0, 1))
        b.beam((-0.9, -0.9, zs - 0.25), (-2.26, -2.26, zs - 0.25), w=0.16, h=0.18, col="darkoak")
        for deg, end in ((298, (-2.2, -1.25)), (332, (-1.25, -2.2)), (315, (-2.13, -2.13))):
            p = PC.polar(t.radius(16.5) - 0.03, deg, 16.5)
            b.beam(p, (end[0], end[1], zs - 0.3), w=0.15, col="darkoak")
    PC.rail_arc(b, 2.12, -18.5, 288.5, z=ZG, h=1.05, style="iron", knobs="brass")
    P.railing(b, [(-0.72, -2.08, zs), (-0.72, -2.27, zs), (-1.15, -2.27, zs)], h=1.05, style="iron", posts_at=0.9)
    P.railing(b, [(-2.27, -1.15, zs), (-2.27, -0.72, zs), (-2.08, -0.72, zs)], h=1.05, style="iron", posts_at=0.9)
    with b.at(-1.5, -1.5, zs):
        P.landing_mark(b, 0.74)
    b.pad(-1.5, -1.5, zs, radius=0.78, face=315, name="Hoist stage")

    # ------------------------------------------------------------------ the lantern drum and its copper dome
    drum = b.round(1.2, 2.7, mat="plaster", col="cream", z=ZG, seg=16, depth=0.2, foot=False)
    P.door(drum, 315, w=0.72, h=1.85, z=0.03, col="green", frame="timber")
    for deg in (45, 135, 225):
        P.window(drum, deg, 0.95, w=0.45, h=0.9, arch=0.22, frame="ivory", bars=(1, 1))
    P.ring_band(b, 1.2, ZG, h=0.3, out=0.05, mat="brick", col=None, seg=16, lod=0)
    P.ring_band(b, 1.2, ZG + 2.5, h=0.2, out=0.1, col="sand", seg=16)
    sec = PC.dome_section(1.2, 1.4, n=6, eave=0.16, drop=0.06)
    b.cone_roof(1.2, 1.4, mat="metal", col="copper", z=ZG + 2.7, seg=16, section=sec, course=0, finial=True)
    with b.at(z=ZG + 2.7):
        PC.ribs(b, sec, n=8, w=0.09, proud=0.045)
    PC.doves(b, [PC.polar(2.12, 100, ZG + 1.07), PC.polar(2.12, 118, ZG + 1.07), PC.polar(2.12, 210, ZG + 1.07)])

    # ------------------------------------------------------------------ the davit that lifts the lead, and the yard
    px, py, _ = PC.polar(2.02, 25, 0)
    with b.detail(1):
        b.beam((px, py, ZG), (px, py, ZG + 2.25), w=0.09, mat="metal", col="iron")
    K.hoist(b, px, py, ZG + 2.1, out=0.62, face=25, rope=18.3, load="bucket", col="blackoak", back=0.12)
    K.ingots(b, -1.8, -2.02, 0, n=3, rows=3, rz=35)
    K.tub(b, 1.88, -1.95, 0, r=0.38, h=0.56, fill="water")
    P.crate(b, -2.0, 1.9, 0, s=0.55, rz=20)
    P.barrel(b, 1.95, 1.95, 0)
