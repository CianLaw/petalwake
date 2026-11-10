# Keel Cottage: when the lugger Petrel was past mending Jory Tamblyn sawed her in two and turned her over; half of her is his shed.
# A small sky-washed cottage, gable to the quay under slate, and beside it a tarred half-boat standing keel-up with a door in the sawn
# end and a stove pipe through her planks; washing and a fish rack behind. Sky plaster, slate, tar; accent red.
from kit import *
import parts as P
import parts_h as H

META = {"name": "Keel Cottage", "kind": "cottage", "lot": (6.0, 7.0), "lean": (-0.003, 0.0)}


def build(b):
    bd = b.body(3.2, 4.6, 2.4, mat="plaster", col="sky", x=-1.1)             # x -2.7 .. 0.5, y 0 .. 4.6
    H.cuttable(bd.front, bd.back)
    P.door(bd.front, 0.95, w=0.9, h=1.9, col="red", frame="timber", z=0.17, steps=1, lamp=True)
    P.window(bd.front, 2.35, 1.0, w=0.75, h=1.0, shutters="red", box=True)
    P.window(bd.front, 1.6, 2.95, w=0.55, h=0.7, lintel=None)
    P.window(bd.left, 2.4, 1.0, w=0.8, h=1.0)
    P.window(bd.right, 3.3, 1.1, w=0.6, h=0.8)
    P.door(bd.back, 0.9, w=0.8, h=1.85, col="red", frame="timber", z=0.1)
    P.window(bd.back, 2.4, 1.05, w=0.7, h=0.9)
    P.window(bd.back, 1.6, 2.95, w=0.5, h=0.6, lintel=None)
    P.plinth(bd, h=0.5)
    P.exposed(bd.front, "base", n=8)
    P.exposed(bd.left, "corners", n=8)
    bd.gable(ridge="y", pitch=48, mat="slate", eave=0.2, verge=0.3, sag=0.08)
    P.chimney(b, -1.1, 4.05, 3.4, 2.5, w=0.65, d=0.55, mat="brick", pots=1)
    H.oars(b, 0.38, -0.02, n=2, L=2.4)
    # ------------------------------------------------------------------ half the Petrel, keel-up
    SX, SY, SH = 1.86, 1.05, 2.3
    with b.at(SX, SY, SH, rz=90, rx=180):
        H.hull(b, L=7.0, beam=2.1, depth=SH, col=H.TAR_OLD, trim=H.TAR, cut=0.42, stations=7, strakes=5, inner=False, sheer=0.0, lod=0)
    b.footprint(0.95, 0.45, 2.9, 4.7, SH)
    yf = SY - 0.56 - 0.02
    with b.at(SX, yf, 0):
        with b.detail(1):
            b.box(0.78, 0.06, 1.72, "planks", col="red", y=-0.03, bottom=True)
            for sx in (-1, 1):
                b.beam((sx * 0.45, -0.03, 0), (sx * 0.45, -0.03, 1.8), w=0.1, h=0.08, mat="timber", col="darkoak", up=(0, 1, 0))
            b.beam((-0.52, -0.03, 1.8), (0.52, -0.03, 1.8), w=0.08, h=0.1, mat="timber", col="darkoak", up=(0, 0, 1))
        with b.detail(2):
            for zz in (0.4, 1.3):
                b.beam((-0.36, -0.07, zz), (0.2, -0.07, zz), w=0.02, h=0.06, mat="metal", col="iron", up=(0, 0, 1), caps=False)
            b.box(0.05, 0.05, 0.05, "metal", col="brass", x=0.27, y=-0.08, z=0.85, bottom=True)
        P.lantern_at(b, 0.62, -0.02, 1.55, arm=0.25)
    with b.at(SX + 0.35, SY + 1.6, SH - 0.25):
        with b.detail(1):
            b.tube((0, 0, 0), (0, 0, 1.05), r=0.07, mat="metal", col="iron", n=6)
            b.revolve([(0.16, 1.05), (0.0, 1.22)], "metal", col="iron", seg=6)
        b.smoke(0, 0, 1.4, strength=0.5)
    H.net_drape(b, (SX - 0.7, SY + 0.2, 1.95), (SX - 0.95, SY + 2.4, 1.35), drop=1.0, sag=0.05, col=H.NET, floats=True)
    H.pots(b, 2.3, -0.4, rz=80, n=3)
    H.buoy(b, 0.95, -0.7, col="!#c4473b", s=0.9)
    # ------------------------------------------------------------------ behind
    with b.detail(1):
        b.beam((2.6, 6.6, 0), (2.6, 6.6, 2.4), w=0.08, mat="timber", col="greyoak")
    P.laundry(b, (-0.8, 4.65, 2.3), (2.6, 6.6, 2.3), n=5, sag=0.3)
    H.fish_rack(b, -1.5, 6.2, w=1.9, h=1.6, rows=2, n=6)
    P.barrel(b, 0.2, 5.0, r=0.28, h=0.8)
    H.gull(b, SX, SY + 0.6, SH + 0.1, rz=200)
