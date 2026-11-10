# The harbour light on the roundhead of the mole: lit every dusk for three hundred years; its lens turns all day because the keeper likes to watch it.
# A lime-washed tower flaring to its foot, one red daymark band, a coved stone cornice carrying an iron-railed walkway round an open
# glazed lantern with a turning lens, a ribbed copper cap; an oil store leans on its side. White, red and verdigris; accent red.
from kit import *
import parts as P
import parts_h as H

META = {"name": "The Harbour Light", "kind": "lighthouse", "lot": (7.0, 7.0), "lean": (-0.002, 0.002)}

CY = 3.5                    # the tower's centre is (0, CY)
BZ = 0.85                   # top of the roundhead it stands on
PROF = [(0.0, 2.22), (1.2, 2.0), (4.6, 1.72), (11.15, 1.42)]      # (height above the roundhead, radius)
DZ = BZ + 11.15             # the walkway
RED = "#c4473b"
DECK = paint("#8a9096")


def rr(z):
    for (z0, r0), (z1, r1) in zip(PROF, PROF[1:]):
        if z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return PROF[-1][1]


def cut(z0, z1):
    return [(0.0, rr(z0))] + [(z - z0, r) for z, r in PROF if z0 < z < z1] + [(z1 - z0, rr(z1))]


def build(b):
    # ------------------------------------------------------------------ the roundhead of the mole
    with b.at(0, CY, 0):
        b.revolve([(3.34, -3.0), (3.34, 0.0), (3.3, BZ - 0.16), (3.36, BZ - 0.16), (3.36, BZ), (3.2, BZ)], "masonry", col="warm", seg=20, lod=0,
                  cols=[shade("warm", 0.85), "warm", "stone", "stone", "stone"])
        b.disc(3.22, "flagstone", col="sand", seg=20, z=BZ)
        b.foot.append({"kind": "disc", "x": 0.0, "y": CY, "r": 3.36, "top": BZ})
        n = 9
        for i in range(n):      # stone posts and a slack chain round the seaward edge
            a = 62 + (298 - 62) * i / (n - 1)
            with b.at(rz=a):
                b.stone(0.3, 0.3, 0.72, mat="ashlar", col="sand", lod=1, y=-3.0, z=BZ, ch=0.3, jitter=0.08)
        with b.detail(2):
            pts = P.circle(3.0, (n - 1) * 2, BZ, 62, 298)
            for k in range(len(pts) - 1):
                za, zb = (0.62, 0.42) if k % 2 == 0 else (0.42, 0.62)
                b.beam((pts[k][0], pts[k][1], BZ + za), (pts[k + 1][0], pts[k + 1][1], BZ + zb), w=0.035, mat="metal", col="iron", caps=False)
    with b.at(0, -1.2, 0):
        P.stairs(b, w=1.7, rise=0.17, run=0.28, n=5, mat="ashlar", col="sand")

    # ------------------------------------------------------------------ the tower: white, a red band, white
    zs = (0.0, 5.3, 7.5, 11.15)
    lower = b.round(0, zs[1], mat="plaster", col="white", x=0, y=CY, z=BZ, seg=20, profile=cut(zs[0], zs[1]))
    band = b.round(0, zs[2] - zs[1], mat="plaster", col=RED, x=0, y=CY, z=BZ + zs[1], seg=20, profile=cut(zs[1], zs[2]), foot=False)
    upper = b.round(0, zs[3] - zs[2], mat="plaster", col="white", x=0, y=CY, z=BZ + zs[2], seg=20, profile=cut(zs[2], zs[3]), foot=False)
    P.door(lower, 0, w=0.95, h=2.15, arch=0.47, col="red", steps=1, z=0.2, lamp=True)
    win = dict(w=0.52, h=1.05, arch=0.26, frame="red", bars=(1, 1), lintel=None)
    P.window(lower, 0, 3.55, **win)
    P.window(lower, 205, 2.3, **win); H.near_only(lower)
    P.window(band, 118, 0.55, **win)
    P.window(band, 262, 0.55, **win)
    P.window(upper, 0, 1.2, **win)
    P.window(upper, 180, 1.2, **win); H.near_only(upper)
    P.exposed(lower, "base", n=16)
    H.life_ring(lower, 28, 1.5)

    def hood():      # a little copper hood over the door, and the fog bell beside it
        with lower.on(0, 0.2):
            with b.detail(1):
                for sgn in (-1, 1):
                    q = [(0, 0.05, 2.75), (sgn * 0.75, 0.05, 2.42), (sgn * 0.8, -0.5, 2.34), (0, -0.5, 2.66)]
                    b.face(q if sgn > 0 else list(reversed(q)), "metal", col="copper")
                    b.face(list(reversed(q)) if sgn > 0 else q, "metal", col=shade("copper", 0.6))
        with lower.on(-27, 0.0):
            with b.detail(2):
                b.beam((0, 0, 2.1), (0, -0.4, 2.1), w=0.04, mat="metal", col="iron")
                b.beam((0, 0, 1.75), (0, -0.36, 2.08), w=0.03, mat="metal", col="iron", caps=False)
            H.small_bell(b, 0, -0.36, 2.06, r=0.15)
    lower.add(hood)

    # ------------------------------------------------------------------ cornice, walkway and railing: where the rider lands
    with b.at(0, CY, DZ):
        b.revolve([(1.42, -0.95), (1.46, -0.62), (1.62, -0.32), (1.98, -0.1), (2.02, -0.1), (2.02, 0.0)], "ashlar", col="stone", seg=20, lod=0)
        b.disc(3.0, "planks", col=DECK, seg=20, lod=0)
        b.disc(3.0, "planks", col=shade(DECK, 0.6), seg=20, r_in=1.98, z=-0.1, down=True, lod=0)
        b.revolve([(3.0, -0.1), (3.04, -0.1), (3.04, 0.03), (3.0, 0.03)], "metal", col="iron", seg=20, lod=0)
        n = 10
        with b.detail(1):
            for i in range(n):
                with b.at(rz=360.0 * (i + 0.5) / n):      # cranked iron brackets
                    b.beam((0, -1.5, -0.92), (0, -2.3, -0.46), w=0.07, h=0.11, mat="metal", col="iron", caps=False)
                    b.beam((0, -2.28, -0.48), (0, -2.94, -0.15), w=0.07, h=0.11, mat="metal", col="iron", caps=False)
            b.revolve([(2.5, -0.2), (2.58, -0.2), (2.58, -0.1), (2.5, -0.1)], "metal", col="iron", seg=20)
        P.railing(b, P.circle(2.94, 18, 0.0, 25, 335), h=1.12, style="iron", posts_at=1.1)
        with b.detail(1):
            for a in (-25, 25):
                with b.at(rz=a):
                    b.tube((0, -2.94, 0), (0, -2.94, 1.3), r=0.045, mat="metal", col="iron", n=6)
                    b.blob(0.085, mat="paint", col="red", y=-2.94, z=1.36, seg=5, rings=2, rough=0.0)
        with b.at(0, -2.14, 0):
            P.landing_mark(b, 0.76)
        b.pad(0, -2.14, 0, radius=0.8, face=0, name="The Harbour Light")
        with b.at(rz=118):
            H.gull(b, 0, -2.94, 1.14, rz=150)
        with b.at(rz=200):
            H.rope_coil(b, 0, -2.3, 0, r=0.26)

        # -------------------------------------------------------------- the lantern
        mur = b.round(1.2, 0.92, mat="plaster", col=RED, seg=16, depth=0.12, foot=False)
        b.revolve([(1.08, 0.92), (1.08, 0.03)], "plaster", col=shade(RED, 0.7), seg=16, lod=0)
        b.disc(1.2, "plaster", col=shade(RED, 1.1), seg=16, r_in=1.08, z=0.92, lod=0)
        b.disc(1.1, "planks", col=shade(DECK, 0.8), seg=16, z=0.03, lod=0)
        P.door(mur, 180, w=0.6, h=0.8, z=0.04, col="black", frame=None, knob=False, depth=0.06)
        TOP = 2.78
        for i in range(12):
            with b.at(rz=30 * i + 15):
                b.beam((0, -1.16, 0.9), (0, -1.16, TOP), w=0.055, mat="metal", col="iron", caps=False, lod=0)
        b.revolve([(1.13, TOP - 0.14), (1.24, TOP - 0.14), (1.24, TOP + 0.02), (1.13, TOP + 0.02)], "metal", col="iron", seg=12, lod=0, smooth=False)
        b.revolve([(1.14, 1.78), (1.19, 1.78), (1.19, 1.84), (1.14, 1.84)], "metal", col="iron", seg=12, lod=2, smooth=False)
        with b.detail(1):      # the lamp's brass pedestal
            b.revolve([(0.34, 0.03), (0.2, 0.3), (0.2, 0.95), (0.34, 1.04)], "metal", col="brass", seg=8)
        with b.spin(speed=0.07, axis=(0, 0, 1), wind=False):
            b.revolve([(0.3, 1.04), (0.52, 1.22), (0.66, 1.5), (0.66, 2.02), (0.52, 2.3), (0.3, 2.48), (0.0, 2.52)], "glass", col="#8fd6c6", seg=8, smooth=False, lod=0,
                      cols=["#8fd6c6", "#a6e0d2", "#c8efe6", "#a6e0d2", "#8fd6c6", "#8fd6c6"])
            for k in range(2):
                with b.at(rz=180 * k + 22.5):
                    with b.at(0, -0.625, 1.76, rx=90):
                        b.disc(0.2, "glow", col="#ffd88a", seg=8, lod=0)
                        b.revolve([(0.2, 0.0), (0.25, 0.0), (0.25, 0.03), (0.2, 0.03)], "metal", col="brass", seg=8, lod=1)
        b.lamp(0, 0, 1.76, strength=2.0)

        # -------------------------------------------------------------- the copper cap
        CAP = [(1.52, -0.08), (1.3, 0.12), (1.12, 0.6), (0.72, 1.14), (0.32, 1.5), (0.17, 1.74)]
        b.cone_roof(1.2, 1.74, mat="metal", col="copper", z=TOP, seg=12, course=0, smooth=False, section=CAP, soffit="metal",
                    soffit_col=shade("copper", 0.6), finial=False)
        with b.at(z=TOP):
            with b.detail(1):
                b.revolve([(1.5, -0.14), (1.58, -0.14), (1.58, -0.02), (1.5, -0.02)], "metal", col=shade("copper", 0.8), seg=12, smooth=False)
                b.revolve([(0.17, 1.72), (0.21, 1.84), (0.31, 1.98), (0.31, 2.12), (0.17, 2.28), (0.06, 2.36), (0.03, 3.25)], "metal", col="copper", seg=8)
            with b.detail(2):
                for i in range(12):
                    with b.at(rz=30 * i):
                        for (ra, za), (rb, zb) in zip(CAP[1:], CAP[2:]):
                            b.beam((0, -ra - 0.01, za + 0.02), (0, -rb - 0.01, zb + 0.02), w=0.05, h=0.04, mat="metal", col=shade("copper", 0.8), caps=False)
            P.weathervane(b, 0, 0, 2.3, h=1.25)
            H.gull(b, 0.0, -0.31, 2.02, rz=40)

    # ------------------------------------------------------------------ the oil store
    st = H.leanto(b, 1.42, CY + 0.15, 1.95, 1.3, 1.75, rz=90, z=BZ, pitch=30, mat="masonry", col="warm", roof="slate", eave=0.2, verge=0.14, foot=False)
    P.door(st.left, 0.78, w=0.68, h=1.62, z=0.04, col="red", frame="timber")
    P.window(st.front, 0.98, 0.75, w=0.55, h=0.6, frame="red", bars=(1, 0), lintel="timber")
    H.hatch(st.right, 0.6, 0.7, w=0.45, h=0.5, col="red")

    # ------------------------------------------------------------------ what the keeper leaves about
    with b.at(0, CY, BZ):
        with b.at(rz=-52):
            P.bench(b, 0, -2.45, w=1.3, rz=0)
        with b.at(rz=148):
            H.pots(b, 0, -2.6, 0, rz=0, n=3)
        with b.at(rz=228):
            P.barrel(b, 0, -2.5, r=0.27, h=0.72)
            P.crate(b, 0.6, -2.45, s=0.5, rz=20)
        with b.at(rz=40):
            H.rope_coil(b, 0, -2.75, 0, r=0.3)
            H.bollard(b, 0.55, -2.95)
        with b.at(rz=-22):
            H.bollard(b, 0, -3.02)
        with b.at(rz=190):
            H.buoy(b, 0, -2.65, col="!#c4473b", flag="stripe_yellow")
