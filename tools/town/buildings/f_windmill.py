# Whitecap Mill: the island's tower mill, grinding the meadow barley since before the charts were drawn; the miller's cat owns the stage.
# Massing: a slender tower tapering 6.2 m -> 4.1 m over 15 m, a timber stage on raking struts a third of the way up, an upturned-boat cap
#          with a striped fantail behind and four 8.6 m lattice sails (cloth half spread) turning in front.
# Materials: white lime-wash over warm rubble that shows at the foot, tarred clinker boards on the cap, ivory sail frames, linen cloth; accent blue.
from kit import *
import parts as P
import parts_f as F

META = {"name": "Whitecap Mill", "kind": "windmill", "lot": (9.0, 9.0), "notes": "sails sweep 8.7 m about a hub 16.3 m up, 3.75 m in front of the axis"}

AX = (0.0, 4.5)        # the tower's axis
CURB = 15.0            # top of the masonry
STAGE = 5.4


def cap(b):
    """The boat-shaped cap, an upturned clinker hull. Frame: origin on the middle of the curb, +y to the back."""
    L, W, H, yc = 7.0, 2.3, 2.75, 0.45
    T = [-1.0, -0.9, -0.72, -0.48, -0.2, 0.1, 0.4, 0.66, 0.87, 1.0]
    hw = lambda t: W * max(1 - abs(t) ** 1.8, 0.0) ** 0.78
    hh = lambda t: H * (1 - 0.42 * abs(t) ** 3)
    f = lambda s: 1 - s ** 1.35
    g = lambda s: 0.7 * (1 - (1 - s) ** 2) + 0.3 * s

    def loop(s, o=0.0, dz=0.0):
        side = []
        for t in T:
            w_, h_ = hw(t), hh(t)
            x, z = w_ * f(s), h_ * g(s)
            if o and w_ > 1e-6:
                nx, nz = h_ * (1.4 * (1 - s) + 0.3), w_ * 1.35 * s ** 0.35
                k = math.hypot(nx, nz) or 1.0
                x, z = x + o * nx / k, z + o * nz / k
            side.append((x, yc + t * L / 2, z + dz))
        return side + [(-p[0], p[1], p[2]) for p in reversed(side[1:-1])]

    n = 7
    rows, cols = [], []
    tar = C("#8f7d6c")
    for k in range(n):
        rows += [loop(k / n, 0.05), loop((k + 1) / n)]
        cols += [shade(tar, b.r(0.86, 1.06)), shade(tar, 0.55)]
    F.loft(b, rows, "planks", closed=True, cols=cols)
    # the petticoat that hangs over the curb, its painted band, and the underside
    F.loft(b, [loop(0, 0.05, -0.6), loop(0, 0.05, 0.0)], "planks", col="ivory", closed=True)
    F.loft(b, [loop(0, 0.08, -0.6), loop(0, 0.08, -0.4)], "planks", col="blue", closed=True, lod=1)
    b.face(list(reversed(loop(0, 0.05, -0.6))), "planks", col="darkoak")
    # keel, stem and stern posts, finial
    ridge = [(0.0, yc + t * L / 2, hh(t) + 0.05) for t in T]
    with b.detail(1):
        for p0, p1 in zip(ridge, ridge[1:]):
            b.beam(p0, p1, w=0.2, h=0.2, mat="planks", col="ivory", caps=False)
        for p in (ridge[0], ridge[-1]):
            b.beam((0, p[1], -0.62), (0, p[1], p[2] + 0.06), w=0.22, h=0.2, mat="planks", col="ivory")
        with b.at(0, yc, H + 0.02):
            b.revolve([(0.06, 0.0), (0.05, 0.4), (0.17, 0.5), (0.21, 0.66), (0.12, 0.8), (0.0, 0.84)], "metal", col="brass", seg=8)


def fantail(b):
    """The fantail on its frame behind the cap: eight striped vanes that turn. Frame as `cap`."""
    yb = 0.45 + 7.0 / 2
    ya, za = yb + 2.05, 2.6
    with b.detail(1):
        for sx in (-0.72, 0.72):
            b.beam((sx, yb - 1.9, 0.22), (sx, ya + 0.12, 0.22), w=0.14, h=0.18, mat="timber", col="darkoak", up=(0, 0, 1))
            b.beam((sx, ya, 0.22), (sx, ya, za + 0.22), w=0.13, mat="timber", col="darkoak")
            b.beam((sx, yb - 1.2, 1.5), (sx, ya, za - 0.1), w=0.11, mat="timber", col="darkoak")
            b.beam((sx, ya - 1.45, 0.3), (sx, ya, 1.45), w=0.1, mat="timber", col="darkoak")
        b.beam((-0.8, ya + 0.1, 0.22), (0.8, ya + 0.1, 0.22), w=0.13, mat="timber", col="darkoak")
        b.beam((-0.86, ya, za), (0.86, ya, za), w=0.08, mat="metal", col="iron")
    with b.at(0, ya, za):
        with b.spin(speed=0.4, axis=(1, 0, 0)):
            n = 8
            tx, ty = 0.2 * math.sin(rad(40)), 0.2 * math.cos(rad(40))
            for k in range(n):
                with b.at(rx=360.0 * k / n + 11):
                    b.beam((0, 0, 0.1), (0, 0, 1.46), w=0.05, mat="planks", col="ivory", lod=1, caps=False)
                    c = "blue" if k % 2 == 0 else "ivory"
                    q = [(-tx, -ty, 0.5), (tx, ty, 0.5), (tx * 1.3, ty * 1.3, 1.46), (-tx * 1.3, -ty * 1.3, 1.46)]
                    b.face(q, "planks", col=c)
                    b.face(list(reversed(q)), "planks", col=shade(c, 0.85))
            b.box(0.3, 0.26, 0.26, "metal", col="iron", z=-0.13, bottom=True, lod=1)


def build(b):
    with b.at(*AX):
        # ---- the tower: battered foot, lime-washed shaft, windows in four files up it (each file shares its cuts)
        t = b.round(3.1, CURB, mat="plaster", col="white", seg=20, profile=[(0.0, 3.1), (2.6, 2.9), (CURB, 2.05)])
        P.round_base(b, 3.1, h=1.1, out=0.3, ring=t)

        def win(deg, z, h, arch=0.28, **kw):
            F.window(t, deg, z, w=rad(12.5) * t.radius(z + h / 2), h=h, arch=arch, frame="blue", **kw)

        F.door(t, 0, w=1.1, h=2.24, arch=0.5, col="blue", steps=2, z=0.36, lamp=True)
        F.door(t, 180, w=1.0, h=2.24, col="blue", frame="timber", steps=2, z=0.36)
        win(100, 1.6, 1.0)
        win(262, 1.6, 1.0, box=True)
        F.door(t, 58, w=0.82, h=1.87, z=STAGE + 0.03, col="blue", frame="timber")
        win(0, 6.2, 1.1, arch=0.3, bars=(1, 2), shutters="blue")
        win(180, 6.2, 1.1, arch=0.3, bars=(1, 2))
        win(100, 9.3, 1.0, arch=0.26)
        win(262, 9.3, 1.0, arch=0.26, shutters="blue")
        win(0, 11.6, 0.95, arch=0.25)
        win(180, 11.6, 0.95, arch=0.25)
        win(100, 13.2, 0.8, arch=0.0, lintel="timber", bars=(1, 0))
        win(262, 13.2, 0.8, arch=0.0, lintel="timber", bars=(1, 0))
        P.stones(t, n=38, z0=0.25, z1=3.0, mat="masonry", col="warm", proud=0.03, size=(0.26, 0.52))
        P.stones(t, n=14, z0=3.0, z1=5.0, mat="masonry", col="warm", proud=0.03, size=(0.25, 0.46))
        P.stones(t, n=10, z0=6.6, z1=13.5, mat="masonry", col="warm", proud=0.025, size=(0.24, 0.42))
        P.ring_band(b, 2.72, STAGE - 0.5, h=0.2, out=0.1, seg=20)
        P.ring_band(b, 2.07, CURB - 0.42, h=0.34, out=0.14, mat="timber", col="darkoak", seg=20)

        # ---- the stage: where the miller reaches the sails, and where the rider lands (clear of their sweep, round the right-hand side)
        P.gallery(b, 2.69, 4.4, STAGE, seg=20, rail="cross", gap=(81, 119), brackets=10, bracket_drop=2.6)
        px, py = 3.6 * math.sin(rad(100)), -3.6 * math.cos(rad(100))
        b.pad(px, py, STAGE, radius=0.75, face=100, name="Mill stage")
        with b.at(px, py, STAGE):
            P.landing_mark(b, 0.7)
        with b.at(z=STAGE):
            for a, r_ in ((38, 3.2), (47, 3.75), (52, 3.15)):
                P.sack(b, r_ * math.sin(rad(a)), -r_ * math.cos(rad(a)), 0.0, r=0.3)
            P.barrel(b, 3.5 * math.sin(rad(322)), -3.5 * math.cos(rad(322)), 0.0, r=0.27, h=0.7)
            with b.at(rz=232):
                F.cat(b, 0.2, -3.85, 0.0, rz=70, pose="curl")
                F.tool(b, -0.9, -2.83, 0.0, kind="broom", rz=180, lean=0.12)
            with b.at(rz=180):
                P.sack(b, 0.5, -3.3, 0.0, r=0.28)

        # ---- the cap, its fantail and the sails
        with b.at(z=CURB):
            cap(b)
            fantail(b)
            with b.at(0, -3.75, 1.3, rx=-8.0):
                with b.spin(speed=0.08):
                    with b.at(ry=17.0):
                        F.sails(b, n=4, length=8.6, width=1.85, inner=1.5, bars=0.44, col="ivory", cloth="linen", reef=0.36)
                    b.tube((0, 0.2, 0), (0, 2.0, 0), r=0.2, mat="timber", col="darkoak", lod=0, n=8)

        # ---- round the foot: an old millstone, sacks for the carter, a bench in the sun, flowers
        with b.at(rz=40):
            with b.at(0, -3.52, 0.56, rx=62):
                with b.detail(1):
                    b.revolve([(0.11, -0.09), (0.62, -0.09), (0.62, 0.09), (0.11, 0.09), (0.11, -0.09)], "ashlar", col="grey", seg=12, smooth=False)
        with b.at(rz=18):
            P.sack(b, -0.25, -3.72, 0.0); P.sack(b, 0.3, -3.8, 0.0, r=0.27); P.sack(b, 0.05, -3.7, 0.42, r=0.26)
        with b.at(rz=322):
            P.bench(b, 0, -3.78, 0, w=1.3)
        for a, n_ in ((62, 5), (88, 4), (140, 6), (158, 4), (215, 5), (240, 6), (285, 5), (300, 4), (344, 4)):
            with b.at(rz=a):
                F.flowers(b, b.r(-0.2, 0.2), -3.85 + b.r(-0.1, 0.12), 0.0, n=n_, spread=b.r(0.32, 0.5))
        for a in (150, 228, 293):
            with b.at(rz=a):
                F.spire_flower(b, 0, -3.62, 0, h=b.r(1.0, 1.5), col=b.pick(["#b08ae6", "#e8497a", "#f2a0bd"]))
