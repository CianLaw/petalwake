# The harbourmaster's tower: an old sea-watch tower where every arrival is logged; the wind dial on its face is driven from the vane.
# Round battered rubble shaft, a lime-washed lookout drum ringed with windows above a broad timber gallery, a witch-hat slate cone;
# the office house (stone below, a jettied painted-board storey above) leans on its flank. Warm rubble, white, slate; accent navy and brass.
from kit import *
import parts as P
import parts_h as H

META = {"name": "Harbourmaster's Tower", "kind": "tower", "lot": (9.0, 9.0), "lean": (0.003, 0.002)}

TX, TY = -0.8, 3.8          # the tower's centre
GZ = 14.4                   # gallery floor
BOARD = paint("#b9cbd3")    # the office's painted boards


def wind_dial(s, deg, z, r=0.92):
    """The wind dial: a painted compass with one hand, in a stone ring."""
    b = s.b

    def deco():
        with s.on(deg, z):
            with b.at(rx=90):
                with b.detail(1):
                    b.revolve([(r + 0.14, -0.34), (r + 0.14, 0.03)], "ashlar", col="stone", seg=16, close_top=True)
                    b.disc(r, "paint", col="ivory", seg=16, z=0.05)
                    b.revolve([(r, 0.03), (r + 0.07, 0.04), (r + 0.07, 0.1), (r, 0.11)], "metal", col="brass", seg=16)
                with b.detail(2):
                    for k in range(8):
                        with b.at(rz=45 * k):
                            ln, wd = (r * 0.86, 0.13) if k % 2 == 0 else (r * 0.55, 0.1)
                            b.tri((-wd, 0.1, 0.056), (wd, 0.1, 0.056), (0, ln, 0.056), "paint", col="navy" if k % 2 == 0 else "red")
                    with b.at(rz=-62):
                        b.box(0.07, r * 0.8, 0.02, "paint", col="black", y=r * 0.26, z=0.07)
                        b.tri((-0.12, r * 0.62, 0.08), (0.12, r * 0.62, 0.08), (0, r * 0.86, 0.08), "paint", col="black")
                    b.box(0.12, 0.12, 0.04, "metal", col="brass", z=0.08)

    s.add(deco)


def build(b):
    # ------------------------------------------------------------------ the shaft
    t = b.round(2.45, GZ, mat="masonry", col="warm", x=TX, y=TY, seg=20, profile=[(0.0, 2.45), (5.0, 2.27), (GZ, 2.02)])
    P.door(t, 0, w=1.1, h=2.3, arch=0.55, col="navy", steps=3, z=0.52, lamp=True)
    P.round_base(b, 2.45, h=1.1, out=0.34, ring=t, seg=20)
    win = dict(w=0.6, h=1.25, arch=0.3, frame="ivory", bars=(1, 2))      # the stair windows climb round the shaft
    P.window(t, 318, 3.6, shutters="navy", **win)
    P.window(t, 205, 3.6, **win); H.near_only(t)
    P.window(t, 52, 6.2, **win)
    P.window(t, 262, 6.2, shutters="navy", box=True, **win)
    P.window(t, 150, 8.75, **win); H.near_only(t)
    P.window(t, 300, 11.1, shutters="navy", **win)
    P.window(t, 78, 11.1, **win)
    wind_dial(t, 0, 9.3)
    P.stones(t, n=54, z0=0.9, z1=12.3, u1=t.w)
    P.ivy(t, 232, 0.4, w=2.4, h=5.2, n=9)
    P.ring_band(b, 2.3, 5.0, h=0.2, out=0.1, x=TX, y=TY, seg=20)
    P.ring_band(b, 2.06, 12.55, h=0.24, out=0.16, x=TX, y=TY, seg=20)

    # ------------------------------------------------------------------ the gallery: where the rider lands
    R_IN, R_OUT = 1.9, 3.72
    with b.at(TX, TY, GZ):
        b.disc(R_OUT, "planks", col="greyoak", seg=20, r_in=R_IN)
        b.disc(R_OUT, "planks", col=shade("darkoak", 0.8), seg=20, r_in=2.0, z=-0.16, down=True)
        b.revolve([(R_OUT, -0.2), (R_OUT + 0.03, -0.02), (R_OUT, 0.02)], "planks", col="darkoak", seg=20)
        n = 9
        for i in range(n):
            with b.at(rz=360.0 * (i + 0.5) / n):
                with b.detail(1):      # a stone corbel, a cranked oak brace and the joist it carries
                    b.stone(0.42, 0.46, 0.3, mat="ashlar", col="sand", lod=1, y=-2.2, z=-2.25, jitter=0.06)
                    b.beam((0, -2.12, -1.95), (0, -2.75, -1.0), w=0.17, mat="timber", col="darkoak")
                    b.beam((0, -2.7, -1.08), (0, -3.5, -0.3), w=0.17, mat="timber", col="darkoak")
                    b.beam((0, -1.98, -0.27), (0, -R_OUT - 0.14, -0.27), w=0.15, h=0.2, mat="timber", col="darkoak")
        with b.detail(2):
            for i in range(n * 2):
                if i % 2 == 0:
                    with b.at(rz=360.0 * (i / 2) / n):
                        b.beam((0, -2.0, -0.25), (0, -R_OUT - 0.06, -0.25), w=0.09, h=0.16, mat="timber", col="darkoak")
        P.railing(b, P.circle(R_OUT - 0.1, 20, 0.0, 26, 334), h=1.05, style="balusters", col="darkoak", posts_at=1.25)
        for a in (-26, 26):      # stout newels either side of the open landing side, each with a lantern
            with b.at(rz=a):
                with b.detail(1):
                    b.beam((0, -R_OUT + 0.1, 0), (0, -R_OUT + 0.1, 1.5), w=0.15, mat="timber", col="darkoak")
                P.lantern_at(b, 0, -R_OUT + 0.1, 1.72, arm=0.0)
        with b.at(0, -2.9, 0):
            P.landing_mark(b, 0.76)
        b.pad(0, -2.9, 0, radius=0.8, face=0, name="Harbourmaster's gallery")
        with b.at(rz=104):      # the signal gaff and the day's hoist
            with b.detail(1):
                b.beam((0, -3.5, 0.15), (0, -5.0, 3.5), w=0.075, mat="planks", col="ivory")
                b.beam((0, -3.62, 1.02), (0, -4.25, 1.9), w=0.05, mat="planks", col="ivory")
            H.signal_flags(b, (0, -4.96, 3.42), (0, -3.72, 0.95), n=4, sag=0.0, size=0.46)
        # a brass telescope on its stand, a rope coil, a fog bell by the door
        with b.at(rz=58):
            with b.at(0, -3.15, 0):
                with b.detail(2):
                    for k in range(3):
                        with b.at(rz=120 * k):
                            b.beam((0, -0.26, 0), (0, 0, 1.12), w=0.035, mat="timber", col="darkoak", caps=False)
                    b.tube((0, 0.36, 1.1), (0, -0.5, 1.34), r=0.05, r1=0.075, mat="metal", col="brass", n=7, caps=True)
        with b.at(rz=118):
            H.rope_coil(b, 0, -2.9, 0, r=0.3)
        with b.at(rz=-64):
            P.crate(b, 0, -2.75, 0, s=0.5, rz=12)
            H.gull(b, 0, -R_OUT + 0.1, 1.09, rz=200)

    # ------------------------------------------------------------------ the lookout drum and its cone
    drum = b.round(1.92, 3.1, r1=1.9, mat="plaster", col="white", x=TX, y=TY, z=GZ, seg=16, depth=0.2, foot=False)
    P.door(drum, 0, w=0.82, h=1.95, z=0.03, col="navy", frame="timber")
    for k in range(1, 8):
        P.window(drum, 45 * k, 0.95, w=0.74, h=1.0, frame="ivory", bars=(1, 1), lintel=None, sill=True, depth=0.16)
        H.near_only(drum)

    def posts():
        with b.detail(1):
            for k in range(8):
                with drum.on(45 * k + 22.5, 0.0):
                    b.beam((0, -0.03, 0.0), (0, -0.03, 3.1), w=0.17, h=0.1, mat="timber", col="darkoak", up=(0, 1, 0), caps=False)
    drum.add(posts)
    P.ring_band(b, 1.92, GZ + 0.72, h=0.14, out=0.06, mat="timber", col="darkoak", x=TX, y=TY, seg=16)
    P.ring_band(b, 1.9, GZ + 2.9, h=0.2, out=0.08, mat="timber", col="darkoak", x=TX, y=TY, seg=16, lod=2)
    with b.at(TX, TY, GZ):
        with b.at(rz=22.5):
            with b.detail(2):      # the fog bell on its bracket
                b.beam((0, -1.9, 2.25), (0, -2.45, 2.25), w=0.06, mat="metal", col="iron")
            H.small_bell(b, 0, -2.4, 2.2, r=0.17)
    CZ = GZ + 3.1
    b.cone_roof(1.9, 5.9, mat="slate", x=TX, y=TY, z=CZ, seg=16, course=0.58, finial=False,
                section=[(2.62, -0.26), (2.12, 0.24), (1.46, 1.42), (0.76, 3.38), (0.0, 5.9)])
    with b.at(TX, TY, CZ + 5.9):
        with b.detail(1):      # copper ball, mast, compass arms, vane and a whirling cup anemometer
            b.revolve([(0.12, -0.3), (0.08, 0.0), (0.2, 0.2), (0.2, 0.34), (0.06, 0.52), (0.04, 2.3)], "metal", col="copper", seg=8)
            for k in range(2):
                with b.at(rz=90 * k):
                    b.beam((-0.45, 0, 1.0), (0.45, 0, 1.0), w=0.03, mat="metal", col="iron", caps=False)
            with b.at(z=1.55, rz=35):
                b.beam((-0.55, 0, 0), (0.5, 0, 0), w=0.03, mat="metal", col="iron", caps=False)
                for q in ([(0.5, 0, -0.12), (0.78, 0, 0), (0.5, 0, 0.12)], [(-0.55, 0, -0.17), (-0.3, 0, 0), (-0.55, 0, 0.17), (-0.74, 0, 0.0)]):
                    b.face(q, "metal", col="brass")
                    b.face(list(reversed(q)), "metal", col="brass")
        with b.at(z=2.3):
            with b.spin(speed=0.7, axis=(0, 0, 1)):
                for k in range(3):
                    with b.at(rz=120 * k):
                        b.beam((0, 0, 0), (0.42, 0, 0), w=0.025, mat="metal", col="iron", caps=False, lod=1)
                        b.blob(0.09, 0.09, 0.09, mat="metal", col="brass", x=0.46, lod=1, seg=5, rings=2, rough=0.0)

    # ------------------------------------------------------------------ the office house on the tower's flank
    HX, HY = 1.82, 4.6
    g = b.body(4.2, 5.6, 2.8, mat="masonry", col="warm", x=HX, y=HY)
    P.plinth(g, h=0.55)
    P.quoins(g, corners="rb", z0=0.55)
    P.door(g.front, 2.75, w=1.0, h=2.05, col="navy", frame="stone", steps=1, z=0.2, lamp=True)
    P.window(g.front, 1.35, 1.1, w=0.8, h=1.15, frame="ivory", shutters="navy")
    P.window(g.right, 1.6, 1.1, w=0.9, h=1.2, frame="ivory", shutters="navy", box=True)
    P.window(g.right, 4.2, 1.1, w=0.9, h=1.2, frame="ivory", shutters="navy")
    P.door(g.back, 1.2, w=0.9, h=1.95, col="navy", frame="timber", z=0.1)
    P.window(g.back, 3.0, 1.2, w=0.8, h=1.0, frame="ivory"); H.near_only(g.back)
    P.window(g.left, 0.9, 1.2, w=0.7, h=1.0, frame="ivory"); H.near_only(g.left)
    up = b.body(4.5, 5.9, 2.5, mat="planks", col=BOARD, x=HX, y=HY - 0.05, z=2.8, floor="planks", depth=0.16)
    H.cuttable(up.front, up.back)
    for wl in up.walls:
        H.battens(wl, step=0.5, col=BOARD, rails=(0.06,))
    with b.detail(1):      # the joist ends that carry the jetty
        for i in range(7):
            x = HX - 2.1 + 4.2 * i / 6
            b.beam((x, HY - 2.75, 2.68), (x, HY - 3.12, 2.68), w=0.14, h=0.18, mat="timber", col="darkoak")
    P.window(up.front, 1.5, 0.85, w=0.85, h=1.2, frame="ivory", shutters="navy")
    P.window(up.front, 3.3, 0.85, w=0.85, h=1.2, frame="ivory", shutters="navy", box=True)
    P.window(up.front, 2.25, 3.0, w=0.6, h=0.8, frame="ivory", sill=True, lintel=None, arch=0.3)
    P.window(up.right, 1.5, 0.85, w=0.85, h=1.2, frame="ivory", shutters="navy")
    P.window(up.right, 4.3, 0.85, w=0.85, h=1.2, frame="ivory", shutters="navy")
    P.window(up.back, 2.25, 0.85, w=0.85, h=1.2, frame="ivory", shutters="navy")
    P.window(up.back, 2.25, 3.05, w=0.55, h=0.7, frame="ivory", lintel=None); H.near_only(up.back)
    P.window(up.left, 1.2, 0.9, w=0.7, h=1.1, frame="ivory"); H.near_only(up.left)
    up.gable(ridge="y", pitch=50, mat="tiles", sag=0.1, eave=0.3, verge=0.3)
    P.chimney(b, HX + 1.2, HY + 1.4, 5.3, 4.0, w=0.7, d=0.6, mat="masonry", col="warm", pots=2)
    # a blank notice board, a bench, the day's clutter
    with b.at(HX - 0.75, HY - 2.8, 0):
        P.bench(b, 0.05, -0.38, w=1.3, rz=180)
    with b.detail(2):
        with b.at(HX + 1.72, HY - 2.86, 1.25):
            b.box(0.62, 0.05, 0.8, "planks", col="darkoak", bottom=True)
            b.box(0.5, 0.02, 0.66, "paint", col="ivory", y=-0.03, z=0.07, bottom=True)
    P.barrel(b, 4.0, 1.3, r=0.28, h=0.75)
    H.rope_coil(b, 3.5, 1.25, r=0.32)
    H.bollard(b, 1.3, -0.75)
    H.bollard(b, 3.6, -0.8)
    H.buoy(b, -3.75, 1.2, col="!#b5433a")
    H.buoy(b, -3.2, 0.75, col="!#3f8f5f", stripe="!#f2ead8", s=0.85)
    H.anchor(b, -3.35, 3.4, rz=285, h=1.5)

    # ------------------------------------------------------------------ the signal mast and the gig in the yard
    MX, MY = -3.75, 8.2
    with b.at(MX, MY, 0):
        b.box(0.7, 0.7, 0.45, "masonry", col="warm", lod=1)
        b.tube((0, 0, 0), (0, 0, 9.6), r=0.11, r1=0.055, mat="planks", col="ivory", n=7, lod=0)
        with b.detail(1):
            b.beam((-0.7, 0, 7.1), (1.5, 0, 7.1), w=0.07, mat="planks", col="ivory")
            b.beam((0, 0, 6.2), (1.3, 0, 8.3), w=0.06, mat="planks", col="ivory")
            b.box(0.12, 0.12, 0.12, "metal", col="brass", z=9.6, bottom=True)
            for (ex, ey) in ((1.6, -2.4), (-0.6, 0.6), (1.8, 0.5)):
                b.beam((0, 0, 7.0), (ex, ey, 0.0), w=0.02, mat="cloth", col="#8a7a66", caps=False)
        with b.at(1.38, 0, 7.1):      # the storm cone, hoisted when the glass is falling
            with b.detail(1):
                b.beam((0, 0, 0), (0, 0, -0.3), w=0.02, mat="cloth", col=H.ROPE, caps=False)
                b.revolve([(0.0, -1.0), (0.34, -0.36), (0.0, -0.3)], "paint", col="black", seg=7)
        H.signal_flags(b, (0.0, 0, 9.3), (-0.62, 0, 7.15), n=4, sag=0.05, size=0.4)
    P.flag(b, MX, MY, 9.55, pole=0.9, w=1.3, h=0.55, col="stripe_blue", pole_col="ivory")
    with b.at(-1.7, 8.25, 0):
        with b.detail(1):
            for xx in (-1.0, 0.9):
                b.beam((xx, -0.6, 0), (xx, -0.25, 0.62), w=0.08, mat="timber", col="greyoak")
                b.beam((xx, 0.6, 0), (xx, 0.25, 0.62), w=0.08, mat="timber", col="greyoak")
                b.beam((xx, -0.5, 0.56), (xx, 0.5, 0.56), w=0.09, mat="timber", col="greyoak")
        with b.at(0, 0, 1.3, rx=180):
            H.hull(b, L=3.5, beam=1.25, depth=0.6, col="!#f2ead8", trim="!#2f4470", inner=False, stations=6)
