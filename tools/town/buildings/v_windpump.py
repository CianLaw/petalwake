# The wind pump: it lifts the village's water from the spring under the moor into a round stone tank, and the
# trough at its foot never runs dry. An open oak trestle standing on the tank's rim, a railed service stage under
# a wheel of painted vanes and its tail. Mossy rubble, weathered oak, teal and ivory paint.
import math

from kit import *
import parts as P
import parts_v as V
import parts_c as PC
import parts_h as PH

META = {"name": "Cairnwick Wind Pump", "kind": "works", "lot": (6.0, 6.0), "wobble": 0.025, "lean": (0.002, 0.0)}

CX, CY = 0.0, 3.0


def build(b):
    R, TH, WALL = 2.3, 2.5, 0.48
    b.footprint(-2.9, 0.1, 2.9, 5.9, TH)
    # ------------------------------------------------------------------ the tank
    tank = b.round(R, TH, r1=R - 0.1, mat="masonry", col="moss", x=CX, y=CY, seg=20, depth=0.4)
    P.round_base(b, R, h=0.8, out=0.3, col=shade("moss", 0.92), seg=20, ring=tank)
    V.door(tank, 0, w=0.75, h=1.25, z=0.25, col="teal", step=True, jambs=True)
    V.rubble(tank, n=30, size=(0.32, 0.7), z0=0.9)
    with b.at(CX, CY, TH):
        ro, ri = R - 0.1, R - 0.1 - WALL
        b.disc(ro + 0.06, "flagstone", col="grey", seg=20, r_in=ri - 0.04, lod=0)
        b.revolve([(ro + 0.06, -0.12), (ro + 0.06, 0.0)], "flagstone", col=shade("grey", 0.9), seg=20, lod=0)
        b.revolve([(ri - 0.04, 0.0), (ri, -0.5)], "masonry", col=shade("moss", 0.7), seg=20, lod=0)
        b.disc(ri + 0.02, "water", col="#7fb6c4", seg=20, z=-0.42, lod=0)
    # ------------------------------------------------------------------ the trestle, standing on the rim
    PZ = 9.6
    leg0, leg1 = 1.42, 0.98
    tiers = V.trestle(b, leg0, leg1, TH, PZ - 0.3, tiers=3, leg=0.22, brace=0.11, girt=0.14, x=CX, y=CY)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.stone(0.5, 0.5, 0.2, mat="flagstone", col="grey", lod=1, x=CX + sx * leg0, y=CY + sy * leg0, z=TH - 0.02)
    # the stage
    DW = 3.7
    V.deck(b, DW, DW, PZ, x=CX, y=CY, joists=0.7, hatch=(1.3, 0.8, 0.7, 0.8))
    for sx in (-1, 1):
        for sy in (-1, 1):
            V.knee(b, (CX + sx * (leg1 + 0.12), CY + sy * (leg1 + 0.12), PZ - 1.5), (CX + sx * (DW / 2 - 0.2), CY + sy * (DW / 2 - 0.2), PZ - 0.3), w=0.12, strut=False)
    e = DW / 2 - 0.09
    V.rails(b, [(CX + 1.25, CY - e, PZ), (CX + e, CY - e, PZ), (CX + e, CY + e, PZ), (CX - e, CY + e, PZ), (CX - e, CY - e, PZ), (CX - 0.75, CY - e, PZ)], h=1.0, col="darkoak", posts_at=1.3)
    with b.at(CX + 0.25, CY - 0.85, PZ):
        P.landing_mark(b, 0.74)
    b.pad(CX + 0.25, CY - 0.85, PZ, radius=0.8, face=0, name="Pump stage")
    # ladders: the tank's side, then inside the trestle up to the hatch
    V.ladder(b, (CX + 2.75, CY + 0.9, 0.0), (CX + 2.22, CY + 0.9, TH + 0.4), w=0.44)
    MZ = tiers[2] + 0.1
    with b.detail(1):
        b.box(0.95, 1.6, 0.07, "planks", col="greyoak", x=CX + 1.58, y=CY + 0.45, z=MZ - 0.07, bottom=True)
        for yy in (-0.25, 1.15):
            V.beam(b, (CX + 0.9, CY + yy, MZ - 0.14), (CX + 2.05, CY + yy, MZ - 0.14), w=0.1, h=0.14, mat="timber", col="darkoak", up=(0, 0, 1))
            V.knee(b, (CX + 1.2, CY + yy, MZ - 0.95), (CX + 1.98, CY + yy, MZ - 0.2), w=0.09, strut=False)
    V.rails(b, [(CX + 2.0, CY - 0.3, MZ), (CX + 2.0, CY + 0.55, MZ)], h=0.9, col="darkoak", post=0.08, lod=2)
    V.rails(b, [(CX + 1.15, CY - 0.3, MZ), (CX + 2.0, CY - 0.3, MZ)], h=0.9, col="darkoak", post=0.08, lod=2)
    V.ladder(b, (CX + 2.02, CY + 0.9, TH), (CX + 2.07, CY + 0.9, MZ + 0.85), w=0.44)
    V.ladder(b, (CX + 1.5, CY + 0.05, MZ), (CX + 1.26, CY + 0.6, PZ + 0.1), w=0.44)
    P.lantern_at(b, CX + 1.2, CY - 0.32, MZ + 1.2, arm=0.3)
    PH.rope_coil(b, CX - 0.2, CY + 1.25, PZ, r=0.3)
    # ------------------------------------------------------------------ the head: mast, wheel, tail
    MX, MY, HZ = CX - 1.15, CY + 0.45, PZ + 3.1
    with b.detail(0):
        V.beam(b, (MX, MY, PZ - 0.2), (MX, MY, HZ + 0.25), w=0.2, mat="timber", col="darkoak", lod=0)
    for (dx, dy) in ((0.75, 0), (0, -0.7), (0, 0.7)):
        V.knee(b, (MX + dx, MY + dy, PZ), (MX, MY, PZ + 1.25), w=0.1, strut=False)
    with b.detail(1):
        b.box(0.5, 0.36, 0.34, "planks", col="teal", x=MX, y=MY, z=HZ - 0.17, bottom=True)
        b.tube((MX + 0.2, MY, HZ), (MX - 1.02, MY, HZ), r=0.055, mat="metal", col="iron", n=6)
        V.beam(b, (MX + 0.2, MY, HZ + 0.05), (MX + 2.5, MY, HZ + 0.12), w=0.07, h=0.1, mat="timber", col="darkoak")
        with b.at(MX + 1.75, MY, HZ + 0.1):
            V.shape(b, [(0.0, 0.06), (0.25, 0.42), (0.95, 0.5), (1.1, 0.1), (1.1, -0.1), (0.95, -0.5), (0.25, -0.42), (0.0, -0.06)], mat="planks", col="teal", lod=1, t=0.008)
            V.shape(b, [(0.72, 0.36), (0.95, 0.42), (1.04, 0.1), (1.04, -0.1), (0.95, -0.42), (0.72, -0.36)], mat="planks", col="ivory", lod=1, t=0.02)
        # the pump rod down to the tank
        b.tube((MX - 0.05, MY - 0.24, HZ - 0.1), (MX - 0.05, MY - 0.24, TH - 0.3), r=0.025, mat="metal", col="iron", n=5)
    with b.at(MX - 1.0, MY, HZ, rz=270):
        with b.spin(speed=0.42):
            V.rotor(b, r=1.36, n=8, cols=("teal", "ivory"))
    # ------------------------------------------------------------------ the trough, and life round the foot
    with b.at(CX - 1.25, CY - R - 0.42, 0):
        V.trough(b, w=1.5, d=0.62, h=0.5, col="moss")
        with b.detail(2):
            V.beam(b, (0.45, 0.5, 0.95), (0.45, 0.05, 0.86), w=0.07, mat="metal", col="lead")
            b.quad((0.42, 0.04, 0.84), (0.48, 0.04, 0.84), (0.48, 0.04, 0.44), (0.42, 0.04, 0.44), "water", col="#7fb6c4")
    V.bucket(b, CX - 2.25, CY - R - 0.2, 0.0, water=True)
    V.bucket(b, CX + 0.2, CY - R - 0.45, 0.0)
    V.churn(b, CX + 1.2, CY - R + 0.25, 0.0)
    P.ivy(tank, 250, 0.2, w=1.8, h=2.2, n=8, col="#8aa65a")
    PH.gull(b, CX + e, CY + e, PZ + 1.06, rz=140)
