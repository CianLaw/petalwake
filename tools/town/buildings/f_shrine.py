# The Candle Stump: the roofless stump of a tower older than the towns; a wild cherry has grown up through it, and travellers leave candles at its foot.
# Massing: a round rubble shell 5.2 m across with a ragged skyline from 5.8 m to 10.8 m, a breach at the front where a bough leans out, the last
#          wedge of the top floor still in place on the seaward side (the landing), and the tree's crown riding above the wall-head.
# Materials: weathered warm rubble, turf and wildflowers on the wall-head, old flags on the surviving floor, blossom; accent: candle-light and plum ribbons.
from kit import *
import parts as P
import parts_c as PC
import parts_m as PM
import parts_f as F

META = {"name": "The Candle Stump", "kind": "ruin", "lot": (6.0, 6.0)}

AX, AY = 0.0, 3.0
R0, R1, HMAX, T = 2.6, 2.3, 10.8, 0.8
FLOOR = 9.0
PINK = "#f4b6c8"


def rad_at(z):
    return R0 + (R1 - R0) * z / HMAX


def polar(r, deg, z=0.0):
    return (r * math.sin(rad(deg)), -r * math.cos(rad(deg)), z)


def arch_ring(b, w, h, arch, n=9, col="sand"):
    """Voussoirs round an arched hole: frame on the wall face at the middle of the hole's foot, -y out."""
    hs = h - arch
    with b.detail(2):
        for i in range(n):
            a = math.pi * (i + 0.5) / n
            x, zz = -(w / 2 + 0.13) * math.cos(a), hs + (arch + 0.13) * math.sin(a)
            with b.at(x, -0.035, zz, ry=-(90 - math.degrees(a))):
                with b.at(rx=90):
                    b.stone(0.24, 0.3, 0.08, mat="ashlar", col=col, jitter=0.07)


def cherry(b):
    """The wild cherry growing up through the stump. Frame: the tower's axis."""
    bark = "#8f735c"
    p0, p1, p2 = (-0.55, -0.5, 0.15), (-0.62, -0.75, 4.6), (-0.7, -1.0, 8.2)
    b.tube(p0, p1, r=0.4, r1=0.3, mat="planks", col=bark, lod=0, n=7)
    b.tube(p1, p2, r=0.3, r1=0.22, mat="planks", col=bark, lod=0, n=7)
    lumps = [(-1.45, -1.9, 11.0, 1.35), (-0.05, -1.5, 11.5, 1.3), (-1.6, -0.4, 10.5, 1.15), (-0.9, -1.15, 12.4, 1.3), (0.95, -2.6, 6.9, 0.85),
             (-0.9, -2.5, 10.3, 0.95), (-1.95, -1.2, 11.6, 0.8), (-0.2, -1.05, 10.9, 0.72), (-1.5, -0.2, 12.0, 0.85)]
    with b.detail(1):
        for q in lumps[:4]:
            b.tube(p2, (q[0], q[1], q[2] - 0.5), r=0.2, r1=0.08, mat="planks", col=bark, n=5)
        b.tube((-0.6, -0.68, 3.9), (0.7, -2.25, 6.5), r=0.17, r1=0.09, mat="planks", col=bark, n=5)      # the bough that leans out through the breach
        for (x, y, z, r) in lumps:
            b.blob(r, r, r * 0.8, mat="ivy", col=shade("#7fb760", b.r(0.86, 1.12)), x=x, y=y, z=z, seg=8, rings=4, wind=0.45, rough=0.24)
        for _ in range(16):                                # drifts of blossom lying on the crown
            k = b.pick(lumps)
            a, e = b.r(0, 6.283), b.r(0.0, 1.3)
            r = b.r(0.34, 0.5)
            b.blob(r, r, r * 0.6, mat="paint", col=F._paint(b.pick([PINK, "#f7cfd8", PINK])), x=k[0] + k[3] * 0.82 * math.cos(e) * math.cos(a),
                   y=k[1] + k[3] * 0.82 * math.cos(e) * math.sin(a), z=k[2] + k[3] * 0.66 * math.sin(e), seg=7, rings=4, wind=0.5, rough=0.2)
    for _ in range(30):
        k = b.pick(lumps)
        a, e = b.r(0, 6.283), b.r(-0.3, 1.2)
        F.bloom(b, k[0] + k[3] * math.cos(e) * math.cos(a), k[1] + k[3] * math.cos(e) * math.sin(a), k[2] + k[3] * 0.8 * math.sin(e), r=0.09, col=b.pick([PINK, "#ffffff", "#f7cfd8"]))


def build(b):
    with b.at(AX, AY):
        P.round_base(b, R0, h=0.85, out=0.2)
        sky = [(142, 9.5), (165, 10.3), (200, 10.8), (250, 10.6), (285, 9.6), (310, 8.8), (335, 7.9), (358, 7.4), (372, 5.8), (388, 6.2), (402, 8.2), (413, 8.8)]
        main = PC.shell(b, R0, HMAX, R1, thick=T, mat="masonry", col="warm", seg=24, arc=(140, 415), skyline=sky, crumble=0.55, grass=0.55)
        land = PC.shell(b, R0, FLOOR, rad_at(FLOOR), thick=T, mat="masonry", col="warm", seg=24, arc=(55, 140), head="flagstone", head_col="sand", crumble=0.0, grass=0.0)
        main.cut(0, 0.95, 0.9, 1.45, arch=0.45, pane="masonry", pane_col="#6a5d50", depth=0.42)        # the shrine niche
        main.cut(215, 0.85, 1.0, 2.2, arch=0.5, pane=None)                                              # the old doorway
        main.cut(305, 4.4, 0.6, 1.3, arch=0.3, pane=None)
        main.cut(262, 6.4, 0.6, 1.3, arch=0.3, pane=None)
        land.cut(97, 5.0, 0.56, 1.2, arch=0.28, pane=None)
        P.stones(main, n=26, z0=1.0, z1=5.4, proud=0.06)
        P.ivy(main, 318, 0.5, w=2.6, h=6.4, n=14)
        P.ivy(main, 172, 0.5, w=2.0, h=4.0, n=9)

        # ---- the last wedge of the top floor: where the rider lands, coming in over the low seaward wall
        wedge = [(0.0, 0.0)] + [polar(1.6, a)[:2] for a in range(38, 159, 15)]
        b.prism(wedge, 0.34, "masonry", col="warm", z=FLOOR - 0.33, cap="flagstone", capcol="sand", bottom=True)
        for a, r in ((36, 1.25), (37, 0.55), (160, 1.2), (159, 0.5)):
            p = polar(r, a, FLOOR - 0.2)
            b.stone(0.42, 0.34, 0.22, mat="masonry", col="warm", lod=2, x=p[0], y=p[1], z=p[2], jitter=0.25)
        pp = polar(1.45, 97, FLOOR + 0.01)
        b.pad(pp[0], pp[1], pp[2], radius=0.75, face=97, name="Wall-head")
        with b.at(*pp):
            P.landing_mark(b, 0.7)
        with b.detail(2):                                  # what is left of the stair that wound down inside the wall
            for k in range(9):
                zz = FLOOR - 0.26 * (k + 1)
                with b.at(rz=163 + 15 * k):
                    b.box(0.38, 0.8, 0.15, "ashlar", col="grey", x=0, y=-(rad_at(zz) - T - 0.36), z=zz, bottom=True)

        # ---- the cherry, the turf and rubble inside, flowers along the wall-head
        cherry(b)
        b.disc(1.95, "ivy", col="#8fc46a", seg=12, z=0.3, lod=0)
        for (x, y, s_) in ((0.7, 0.6, 0.5), (1.1, -0.2, 0.36), (0.2, 1.1, 0.42), (-1.0, 0.9, 0.34)):
            b.stone(s_, s_ * 0.8, s_ * 0.6, mat="masonry", col="warm", lod=2, x=x, y=y, z=0.28, jitter=0.3)
        F.flowers(b, 0.9, 1.0, 0.3, n=5)
        F.flowers(b, -0.2, 1.4, 0.3, n=4)
        for a in (150, 176, 190, 222, 262, 291, 322, 348):
            top = main.top_at(a)
            p = polar(rad_at(top) - T / 2 + b.r(-0.15, 0.15), a, top)
            F.flowers(b, p[0], p[1], p[2], n=5, spread=0.32, h=0.3)
        for a in (236, 276, 337):
            top = main.top_at(a)
            p = polar(rad_at(top) - T / 2, a, top)
            F.spire_flower(b, p[0], p[1], p[2], h=b.r(0.8, 1.2), col=b.pick(["#b08ae6", "#e8497a"]))

        # ---- the shrine niche at the foot: guardian stone, candles, ribbons, a kneeling step
        yw = -rad_at(1.0)
        with b.at(0.0, yw, 0.95):
            arch_ring(b, 0.9, 1.45, 0.45)
            with b.detail(1):
                b.box(1.3, 0.44, 0.1, "ashlar", col="stone", x=0, y=-0.1, z=-0.1, bottom=True)
                for sgn in (-1, 1):
                    b.beam((sgn * 0.82, -0.16, 1.4), (0.0, -0.16, 2.02), w=0.5, h=0.08, mat="slate", col=None)
                b.stone(0.32, 0.2, 0.66, mat="ashlar", col="stone", lod=1, x=0, y=0.26, z=0.0, ch=0.3, jitter=0.1)
            with b.detail(2):
                with b.at(0.0, 0.15, 0.44, rx=90):
                    b.disc(0.085, "paint", col="mustard", seg=8)
                    for k in range(8):
                        with b.at(rz=45 * k):
                            b.tri((0.025, -0.1, 0), (-0.025, -0.1, 0), (0, -0.17, 0), "paint", col="mustard")
                PM.bunting(b, (-0.72, -0.13, 1.5), (0.72, -0.13, 1.5), n=7, sag=0.2, cols=["#7a4672", "#e8497a", "#f5c842", "#f4f1e4"])
            for (x, y, h_) in ((-0.5, -0.14, 0.2), (-0.36, -0.22, 0.13), (-0.2, -0.05, 0.24), (0.3, -0.2, 0.16), (0.47, -0.1, 0.22), (0.2, 0.05, 0.1)):
                F.candle(b, x, y, 0.0, h=h_)
            with b.detail(2):
                with b.at(0.56, 0.05, 0.0):
                    b.revolve([(0.05, 0.0), (0.085, 0.1), (0.06, 0.17)], "paint", col="!#c9764a", seg=6)
                    for (dx, dy, dz, c_) in ((0.0, 0.0, 0.3, "#e8497a"), (0.06, -0.03, 0.26, "#f5c842"), (-0.05, 0.02, 0.27, "#b08ae6")):
                        F.bloom(b, dx, dy, dz, r=0.05, col=c_)
            b.lamp(0.0, -0.2, 0.35, strength=0.6)
            with b.detail(1):
                b.box(1.6, 0.62, 0.15, "flagstone", col="sand", x=0, y=-0.64, z=-0.95)
            for (x, h_) in ((-0.62, 0.15), (0.55, 0.19), (0.68, 0.11)):
                F.candle(b, x, -0.62, -0.8, h=h_)
        with b.at(rz=215):                                  # stones fallen across the old doorway
            b.stone(0.6, 0.42, 0.4, mat="masonry", col="warm", lod=1, x=-0.25, y=-R0 - 0.16, z=0.0, jitter=0.25)
            b.stone(0.46, 0.38, 0.3, mat="masonry", col="warm", lod=2, x=0.45, y=-R0 - 0.14, z=0.0, jitter=0.3)
            with b.at(0.0, -rad_at(0.85), 0.85):
                arch_ring(b, 1.0, 2.2, 0.5, col="warm")
        for a, n_ in ((32, 5), (52, 4), (124, 5), (140, 4), (220, 4), (232, 5), (310, 5), (326, 4)):
            p = polar(R0 + 0.45, a)
            F.flowers(b, p[0], p[1], 0.0, n=n_, spread=b.r(0.26, 0.34))
