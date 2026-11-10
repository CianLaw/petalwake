# a moored trading ketch, 11 m: navy clinker hull, decked, a little cabin aft, two masts with furled sails, a bowsprit
import math
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

META = {"name": "Ketch", "kind": "prop", "group": "harbour", "clear": 8.0, "length": 11.0, "axis": "x", "bow": "+x",
        "float": True, "draft": 1.15, "wobble": 0.012}

SAIL = "#efe6cf"


def build(b):
    H = PP.Hull(L=11.0, B=3.3, depth=1.9, draft=1.0, sheer_bow=0.6, sheer_stern=0.28, transom=0.52, rake_bow=1.3, rake_stern=0.3,
                planks=9, stations=12, lap=0.05, th=0.06, vee=0.9, flare=10.0)
    ox = PH.OXIDE
    drop = 0.34
    zd = lambda x: H.zs(H.u_at(x)) - drop + 0.03
    with b.detail(0):
        H.build(b, cols=[ox] * 6 + ["navy", "navy", "ivory"], inner="#d9bd8a", inside=7 / 9, gunwale="darkoak", head=0.28, keel_w=0.13, keel_d=0.15)
        H.deck(b, -1.0, 1.0, drop=drop, camber=0.06, col="#d9c7a3")
        # the cabin trunk
        cx0, cx1, cw, ch = -3.3, -0.7, 1.9, 0.66
        zc = zd(-2.0) - 0.06
        b.box(cx1 - cx0, cw, ch, "planks", col="ivory", x=(cx0 + cx1) / 2, z=zc)
        b.box(cx1 - cx0 + 0.16, cw + 0.16, 0.07, "planks", col="#b9a183", x=(cx0 + cx1) / 2, z=zc + ch, bottom=True, ty=0.92)
        main = PP.mast(b, 1.7, 0, zd(1.7) - 0.1, h=9.4, r=0.13, rake=2.0)
        miz = PP.mast(b, -3.85, 0, zd(-3.85) - 0.1, h=6.4, r=0.1, rake=3.0)
        PP.furled(b, (1.5, 0, 1.95), (-3.1, 0, 2.05), r=0.2, col=SAIL, ties=7, spar=0.07, above=True, gaff=0.045, tie_col="#8a6a4a")
        PP.furled(b, (-4.05, 0, 1.75), (-6.3, 0, 1.9), r=0.14, col=SAIL, ties=4, spar=0.055, above=True, gaff=0.035, tie_col="#8a6a4a")
        stem = H.pt(1.0, 1.0)
        PP.sweep(b, [(stem[0] - 1.0, 0, stem[2] + 0.02), (stem[0] + 0.3, 0, stem[2] + 0.2), (stem[0] + 2.4, 0, stem[2] + 0.55)], r=0.1, r1=0.06, n=6, mat="planks", col="#c9a57a", caps=(True, True))
    sprit = (stem[0] + 2.35, 0, stem[2] + 0.55)
    with b.detail(1):
        PP.furled(b, (stem[0] + 0.5, 0, stem[2] + 0.36), (stem[0] + 2.1, 0, stem[2] + 0.64), r=0.09, col=SAIL, ties=3, spar=0, above=True, tie_col="#8a6a4a")
        PP.rudder(b, H.xof(-1.0, 0.6) - 0.02, -1.0, zd(-5.4) + 0.42, w=0.46, col="navy", tiller=1.5, tiller_z=zd(-5.0) + 0.6)
        mt = (main[0], 0, main[2] - 1.0)
        hb1, hb2 = H.hb(H.u_at(1.3)), H.hb(H.u_at(2.2))
        PP.shrouds(b, mt, [(1.3, hb1, H.zs(H.u_at(1.3))), (2.2, hb2, H.zs(H.u_at(2.2))), (1.3, -hb1, H.zs(H.u_at(1.3))), (2.2, -hb2, H.zs(H.u_at(2.2))), sprit], r=0.016)
        zt = (miz[0], 0, miz[2] - 0.6)
        hb3 = H.hb(H.u_at(-3.6))
        PP.shrouds(b, zt, [(-3.6, hb3, H.zs(H.u_at(-3.6))), (-3.6, -hb3, H.zs(H.u_at(-3.6))), (-6.4, 0, 1.98)], r=0.014)
        PP.shrouds(b, (main[0], 0, main[2] - 0.2), [(miz[0], 0, miz[2] - 0.15), (-3.2, 0, 2.2)], r=0.012)
        PP.shrouds(b, sprit, [(stem[0] - 0.15, 0, 0.25)], r=0.016)
        PH.signal_flags(b, (main[0] - 0.3, 0, main[2] - 0.5), (miz[0] + 0.3, 0, miz[2] - 0.3), n=6, sag=0.5, size=0.4, line=False)
        PP.pennant(b, (main[0], 0, main[2] + 0.16), L=1.2, h=0.3, col="stripe_red")
        # cabin details
        b.box(0.9, 0.8, 0.12, "planks", col="darkoak", x=cx0 + 0.75, z=zc + ch + 0.07)                  # the sliding hatch
        for (dy, cc) in ((-0.21, "teal"), (0.21, "teal")):
            b.box(0.04, 0.4, 0.52, "planks", col=cc, x=cx0 - 0.02, y=dy, z=zc + 0.08, bottom=True)        # companion doors
        b.box(1.5, 1.3, 0.22, "planks", col="darkoak", x=3.0, z=zd(3.0) - 0.04)                          # the cargo hatch
        b.box(1.56, 1.36, 0.03, "cloth", col="#8a9a6a", x=3.0, z=zd(3.0) + 0.18)
    with b.detail(2):
        for sy in (-1, 1):
            for x in (-2.7, -2.0, -1.3):
                with b.at(x, sy * (cw / 2 + 0.006), zc + ch * 0.58, rx=sy * 90):
                    b.disc(0.1, "glass", seg=8)
                    b.disc(0.145, "metal", col="brass", seg=8, r_in=0.1, z=0.004)
        with b.at(cx0 - 0.1, 0, zc + ch + 0.42):
            PP.lantern(b, s=0.2, h=0.3, sides=4, hang=0.0, lamp=False)
        b.beam((cx0 - 0.1, 0, zc + ch + 0.05), (cx0 - 0.1, 0, zc + ch + 0.42), w=0.03, mat="metal", col="iron")
        PH.anchor(b, 4.3, 0.55, zd(4.3), rz=-25, h=1.1, lean=62)
        PH.rope_coil(b, 4.0, -0.5, zd(4.0), r=0.3)
        PH.rope_coil(b, -4.6, 0.6, zd(-4.6), r=0.24)
        P.barrel(b, 0.3, 0.95, zd(0.3), r=0.26, h=0.6)
        P.crate(b, 0.35, -0.9, zd(0.3), s=0.5, rz=10)
        P.crate(b, 3.1, 0.1, zd(3.0) + 0.21, s=0.45, rz=-20)
        for x in (-2.2, 0.8, 3.0):                                # fenders
            y = H.hb(H.u_at(x)) + 0.11
            z = H.zs(H.u_at(x))
            PP.rope(b, [(x, y - 0.1, z + 0.02), (x, y, z - 0.3)], r=0.014)
            b.blob(0.13, 0.11, 0.2, mat="cloth", col=PP.HEMP, x=x, y=y + 0.02, z=z - 0.5, seg=6, rings=3, rough=0.08)
        PH.gull(b, main[0] + 0.0, 0.0, main[2] + 0.12, rz=120, s=1.2)
