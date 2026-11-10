# The Hill Gate: the old town gate at the top of the hill road. The portcullis has not come down in living memory, the guard rooms are a cobbler's and a lamplighter's store, and the wall-walk between the turrets is where the post-riders wait for the wind.
# Massing: a deep gate block pierced by a round-arched passage; two round turrets flank the arch on the outer face, the left one tall under a conical cap, the right one cut short and battlemented with a beacon basket; a stone gallery on corbels over the arch, a timber gate-chamber on the town side.
# Materials: grey-warm rubble, ashlar arch stones, slate cap, dark oak and cream plaster toward the town. Accent: red.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Hill Gate", "kind": "gatehouse", "lot": (11.0, 6.0)}

BW, Y0, Y1, BH = 10.2, 0.9, 5.5, 9.05
BD, BY = Y1 - Y0, (Y0 + Y1) / 2
ZW = BH + 0.15                                    # the wall-walk
TXC, TYC, TR = 3.55, 1.9, 1.65                    # turret centres (+-x), radius
STONE = mix("warm", "grey", 0.45)
PW, PH, PA = 4.0, 4.5, 2.0                        # the passage: width, height, height of its round head


def build(b):
    block(b)
    passage(b)
    left_turret(b)
    right_turret(b)
    walk(b)
    town_side(b)


def block(b):
    bd = b.body(BW, BD, BH, mat="masonry", col=STONE, x=0, y=BY, foot=False)
    b.footprint(-BW / 2, Y0, -PW / 2, Y1, ZW)     # the two flanks stand on the ground; the passage is free
    b.footprint(PW / 2, Y0, BW / 2, Y1, ZW)
    PC.plinth(bd, h=0.7, out=0.08, col=STONE, doors=[("front", BW / 2, PW), ("back", BW / 2, PW), ("back", 1.55, 0.85), ("back", BW - 1.55, 0.85)])
    for wl in (bd.front, bd.back):
        wl.opening(BW / 2, -0.5, PW, PH + 0.5, arch=PA, depth=0.02, pane=None)
        PC.arch_stones(wl, BW / 2, -0.5, PW, PH + 0.5, PA, n=13)
    P.window(bd.left, 2.4, 5.6, w=0.7, h=1.2, arch=0.3, shutters="red")
    P.window(bd.left, 3.2, 1.4, w=0.5, h=0.9, bars=(2, 1))
    P.window(bd.right, 2.3, 5.6, w=0.7, h=1.2, arch=0.3, shutters="red")
    P.window(bd.right, 1.5, 1.4, w=0.5, h=0.9, bars=(2, 1))
    # the town side of the flanks: the cobbler's door and the lamplighter's
    P.door(bd.back, 1.55, w=0.85, h=1.95, arch=0.4, col="red", z=0.2, steps=0)
    P.lantern(bd.back, 2.2, 2.0, arm=0.16)
    P.window(bd.back, 2.55, 1.2, w=0.55, h=0.9)
    P.sign(bd.back, 0.6, 2.9, emblem="boot", col="brown", out=0.26, w=0.4, h=0.36)
    P.door(bd.back, BW - 1.55, w=0.85, h=1.95, arch=0.4, col="red", z=0.2, steps=0)
    P.window(bd.back, BW - 2.55, 1.2, w=0.55, h=0.9)
    P.window(bd.back, 1.6, 6.2, w=0.7, h=1.15, arch=0.3)
    P.window(bd.back, BW - 1.6, 6.2, w=0.7, h=1.15, arch=0.3)
    P.stones(bd.front, n=10, u0=3.2, u1=7.0, z0=5.2, z1=8.0)
    P.stones(bd.left, n=10, z0=0.8); P.stones(bd.right, n=10, z0=0.8)
    P.ivy(bd.right, 3.9, 0.5, w=1.6, h=5.2, n=10)
    P.ivy(bd.left, 0.8, 0.5, w=1.4, h=3.4, n=6, lod=2)
    b.bd = bd


def passage(b):
    """The road through: vault, the raised portcullis, the gate leaves folded back, the guard-room doors."""
    with b.at(0, Y0, 0):
        PC.vault(b, PW, PH, PA, BD, n=5, col=STONE)
        with b.detail(1):                           # portcullis: its lower bars hang below the arch
            for i in range(9):
                x = -1.76 + 0.44 * i
                top = PH - PA + math.sqrt(max(PA * PA - x * x, 0.0)) - 0.03
                b.beam((x, 0.5, 3.15), (x, 0.5, top), w=0.09, h=0.07, mat="timber", col="blackoak")
            for zz in (3.45, 4.0):
                hx = math.sqrt(max(PA * PA - (zz - (PH - PA)) ** 2, 0.0)) - 0.03
                b.beam((-hx, 0.5, zz), (hx, 0.5, zz), w=0.07, h=0.09, mat="timber", col="blackoak")
        with b.detail(2):
            for i in range(9):
                x = -1.76 + 0.44 * i
                b.box(0.07, 0.06, 0.16, "metal", col="iron", x=x, y=0.5, z=2.99, taper=0.2, bottom=True)
        for sx in (-1, 1):                          # the great leaves, open against the walls
            with b.at(sx * (PW / 2 - 0.07), 1.95, 0.08):
                b.box(0.09, 1.9, 3.5, "planks", col="red", lod=1, bottom=True)
                with b.detail(2):
                    for zz in (0.6, 1.75, 2.9):
                        b.beam((-sx * 0.055, -0.9, zz), (-sx * 0.055, 0.9, zz), w=0.02, h=0.1, mat="metal", col="iron", up=(0, 0, 1), caps=False)
            with b.at(sx * (PW / 2 - 0.02), 3.85, 0.0):     # guard-room door in the passage wall
                b.box(0.05, 0.8, 1.85, "planks", col="red", z=0.12, lod=1)
                with b.detail(2):
                    b.box(0.1, 1.06, 0.2, "ashlar", col="sand", z=1.97)
                    for yy in (-0.46, 0.46):
                        b.box(0.09, 0.14, 1.9, "ashlar", col="sand", y=yy, z=0.07)
        P.lantern_at(b, -PW / 2 + 0.04, 3.1, 2.3, arm=0.0)
        with b.at(PW / 2 - 0.5, 4.3, 0):
            P.barrel(b, 0, 0, 0, r=0.26, h=0.7)
        with b.detail(1):                           # a lamp hung in the mouth
            b.beam((0, 0.2, PH - 0.02), (0, 0.2, PH - 0.55), w=0.025, mat="metal", col="iron", caps=False)
        P.lantern_at(b, 0, 0.2, PH - 0.85, arm=0.0)


def left_turret(b):
    """The tall one: lookout room above the walk, conical slate cap, the town's banner."""
    with b.at(-TXC, TYC):
        PC.round_base(b, TR, h=0.8, out=0.1, col=STONE, seg=18)
        t = PC.ring(b, TR, 13.4, r1=1.5, mat="masonry", col=STONE, seg=18, seam=200, depth=0.26)
        t.cell = 3.2
        for deg, z in ((330, 2.6), (20, 5.4), (300, 7.4)):
            PC.slit(t, deg, z, w=0.2, h=1.1)
        P.door(t, 92, w=0.75, h=1.85, z=ZW + 0.03, col="red", frame="timber", lamp=True)
        for deg in (330, 250, 30):
            P.window(t, deg, ZW + 1.6, w=0.55, h=1.1, arch=0.27, shutters="red" if deg == 330 else None)
        P.ring_band(b, t.radius(ZW + 0.9) - 0.02, ZW + 0.9, h=0.18, out=0.08, seg=18, col="grey")
        P.stones(t, n=18, z0=1.0, z1=12.6, u1=t.w * 0.62)
        PC.corbels(b, 1.5, 13.4, n=12, out=0.22, drop=0.4, w=0.2, steps=2, col="grey")
        b.cone_roof(1.5, 3.9, mat="slate", z=13.4, seg=18, eave=0.3, flare=0.5, course=0.5)
        P.flag(b, 0, 0, 13.4 + 3.9 + 1.2, pole=1.4, w=1.3, h=0.55, col="stripe_red")
        PC.banner(b, *PC.polar(TR + 0.03, 350, 8.4), w=0.7, h=3.0, col="stripe_red", stripe="linen", rz=350)


def right_turret(b):
    """The short one: battlements and the beacon basket that is lit when a rider is expected after dark."""
    with b.at(TXC, TYC):
        PC.round_base(b, TR, h=0.8, out=0.1, col=STONE, seg=18)
        zt = 11.3
        t = PC.ring(b, TR, zt, r1=1.55, mat="masonry", col=STONE, seg=18, seam=160, depth=0.26)
        t.cell = 3.2
        for deg, z in ((30, 2.6), (340, 5.6), (60, 7.6)):
            PC.slit(t, deg, z, w=0.2, h=1.1)
        P.door(t, 268, w=0.75, h=1.85, z=ZW + 0.03, col="red", frame="timber")
        P.stones(t, n=16, z0=1.0, z1=10.6, u0=t.w * 0.4)
        PC.corbels(b, 1.55, zt, n=12, out=0.2, drop=0.4, w=0.2, steps=2, col="grey")
        with b.at(z=zt):
            b.disc(1.76, "flagstone", col="grey", seg=18)
            b.revolve([(1.55, -0.02), (1.76, -0.02), (1.76, 0.0)], "masonry", col=STONE, seg=18)
            PC.round_battlements(b, 1.76, z=0.0, n=8, t=0.3, wall=0.5, h=0.6, col=STONE, seg=18)
            with b.detail(1):                       # the beacon: an iron basket on three legs
                for k in range(3):
                    with b.at(rz=120 * k + 30):
                        b.beam((0, -0.55, 0.0), (0, -0.2, 1.5), w=0.05, mat="metal", col="iron", caps=False)
                b.revolve([(0.2, 1.45), (0.36, 1.95)], "metal", col="iron", seg=8)
                b.revolve([(0.34, 1.95), (0.18, 1.47)], "metal", col=shade("iron", 0.7), seg=8)
                b.blob(0.27, 0.27, 0.2, mat="glow", col="#ffb060", z=1.92, seg=6, rings=3, rough=0.3)
            b.lamp(0, 0, 2.0, strength=1.6)
        PC.banner(b, *PC.polar(TR + 0.03, 10, 8.4), w=0.7, h=3.0, col="stripe_red", stripe="linen", rz=10)
        P.ivy(t, 60, 0.4, w=1.6, h=4.4, n=8, lod=2)


def walk(b):
    """The wall-walk: flagged, battlemented at the sides and back, a corbelled gallery over the arch open in the middle."""
    b.box(BW, BD, 0.15, "flagstone", col="grey", x=0, y=BY, z=BH)
    sides = PC.rect_sides(BW, BD, 0, BY)
    PC.battlements(b, sides, z=ZW, t=0.34, wall=0.55, h=0.65, col=STONE, gaps={0: [(0.0, BW)]}, kerb=0)
    gx, gd = 4.6, 0.55                              # the gallery over the gate
    with b.at(-gx / 2, Y0, BH):
        PC.corbel_row(b, gx, z=0.0, n=6, out=gd, drop=0.85, w=0.34, steps=3, col="grey")
    b.box(gx, gd + 0.1, 0.15, "flagstone", col="grey", x=0, y=Y0 - gd / 2 + 0.05, z=BH, bottom=True)
    PC.battlements(b, [(-gx / 2, Y0 - gd, 0.0, gx)], z=ZW, t=0.32, wall=0.55, h=0.65, col=STONE, gaps={0: [(gx / 2 - 0.95, gx / 2 + 0.95)]})
    with b.at(0, 2.75, ZW):
        P.landing_mark(b, 1.4)
    b.pad(0, 2.75, ZW, radius=1.5, face=0, name="Gate wall-walk")
    P.bench(b, -1.4, Y1 - 0.62, ZW, rz=180, w=1.5)
    P.barrel(b, 4.45, 4.9, ZW, r=0.27, h=0.75); P.crate(b, 4.4, 4.2, ZW, s=0.5, rz=12)
    PC.stack(b, -4.45, Y1 - 0.7, ZW - 0.3, 2.9, w=0.6, d=0.5, flues=2, mat="masonry", col=STONE)
    with b.detail(2):                               # a few old pikes
        for i in range(4):                          # (leaning on the town-side parapet, well clear of the landing)
            x = 1.9 + 0.17 * i
            b.beam((x, Y1 - 0.95, ZW), (x + 0.05, Y1 - 0.36, ZW + 2.45), w=0.04, mat="planks", col="greyoak", caps=False)
    PC.doves(b, [(2.9, Y1 - 0.17, ZW + 1.2), (3.3, Y1 - 0.17, ZW + 1.2), (-0.3, Y0 - 0.37, ZW + 1.2)])


def town_side(b):
    """Toward the town the gate-chamber is a timber-framed face, jettied a hand's breadth, with a little pentice."""
    w, h, z0 = 6.2, 3.5, 5.15
    yf = Y1 + 0.13
    with b.at(w / 2, yf, z0, rz=180):
        wl = b.wall(w, h, mat="plaster", col="cream", depth=0.11)
        P.timber_frame(wl, posts=[0, 1.0, 2.0, 2.6, 3.6, 4.2, 5.2, w], rails=[0, 1.05, 2.45, h], braces=[(0, 1.05, 1.0, 0), (w, 1.05, 5.2, 0), (2.0, 0, 2.6, 1.05), (4.2, 0, 3.6, 1.05)])
        P.window(wl, 1.5, 1.15, w=0.85, h=1.2, lintel=None, depth=0.1, sill=False)
        P.window(wl, 3.1, 1.15, w=0.85, h=1.2, lintel=None, depth=0.1, sill=False)
        P.window(wl, 4.7, 1.15, w=0.85, h=1.2, lintel=None, depth=0.1, sill=False)
        with b.detail(1):
            for x in (0.07, w - 0.07):
                b.box(0.14, 0.15, h, "timber", col="darkoak", x=x, y=0.07, z=0)
            for i in range(7):
                x = 0.15 + (w - 0.3) * i / 6
                b.beam((x, 0.16, -0.5), (x, -0.02, -0.02), w=0.13, lod=1 if i % 2 == 0 else 2)
            b.beam((0, 0.04, -0.08), (w, 0.04, -0.08), w=0.16, h=0.16)
        PC.shed_roof(b, w + 0.3, 0.34, pitch=40, z=h, x=w / 2, y=0.16, mat="slate", eave=0.04, verge=0.02, course=0.2, thick=0.07, barge=False)
