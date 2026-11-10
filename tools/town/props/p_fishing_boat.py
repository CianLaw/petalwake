# a double-ended clinker fishing boat: half-decked, one mast, the red sail furled on its boom, nets and pots aboard
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

META = {"name": "Fishing boat", "kind": "prop", "group": "harbour", "clear": 3.8, "length": 6.4, "axis": "x", "bow": "+x",
        "float": True, "draft": 0.5, "wobble": 0.012}


def build(b):
    H = PP.Hull(L=6.4, B=2.3, depth=1.05, draft=0.42, sheer_bow=0.42, sheer_stern=0.3, transom=None, rake_bow=0.7, rake_stern=0.18,
                planks=6, stations=11, lap=0.042, th=0.045, vee=0.8)
    ox = PH.OXIDE
    with b.detail(0):
        H.build(b, cols=[ox, ox, ox, "teal", "teal", "mustard"], inner="#c9ab7e", gunwale="darkoak", head=0.2, keel_w=0.09, keel_d=0.1)
        H.sole(b, -2.4, 1.4, 0.1, n=8, col="#bfae93")
        fd = H.deck(b, 0.42, 1.0, drop=0.1, camber=0.05, col="#cdb894")
        H.deck(b, -1.0, -0.74, drop=0.12, camber=0.04, col="#cdb894")
        H.bulkhead(b, 0.42, z0=0.1, drop=0.1, col="#c9ab7e", face=-1)
        H.bulkhead(b, -0.74, z0=0.1, drop=0.12, col="#c9ab7e", face=1)
        top = PP.mast(b, 1.6, 0, 0.1, h=5.7, r=0.085, rake=3.0)
        PP.furled(b, (1.42, 0, 1.6), (-2.3, 0, 1.46), r=0.15, col="stripe_red", ties=6, spar=0.05, above=True, gaff=0.035)
    with b.detail(1):
        H.thwart(b, -0.35, col="#b98f5e", w=0.26)
        H.thwart(b, -1.5, col="#b98f5e", w=0.24)
        PP.rudder(b, -3.21, -0.5, 0.86, w=0.36, col="teal", tiller=1.15, tiller_z=1.0)
        for sy in (-1, 1):                                   # the boom crutch
            b.beam((-2.3, sy * 0.5, H.zs(-0.72) - 0.1), (-2.3, -sy * 0.14, 1.52), w=0.06, mat="planks", col="darkoak")
        hbm = H.hb(H.u_at(1.6))
        PP.shrouds(b, (top[0], 0, top[2] - 0.7), [(1.3, hbm, H.zs(0.4)), (1.95, hbm - 0.08, H.zs(0.6)), (1.3, -hbm, H.zs(0.4)), (1.95, -hbm + 0.08, H.zs(0.6)),
                                                  (3.2, 0, H.zs(1.0) + 0.18), (-2.5, 0, 1.56)])
        PP.pennant(b, (top[0], 0, top[2] + 0.1), L=0.8, h=0.2, col="stripe_yellow")
    with b.detail(2):
        H.ribs(b, [-1.9, -1.0, 0.1, 0.9], col="#b98f5e", w=0.05)
        PH.net_heap(b, 0.55, 0.1, 0.1, r=0.6)
        PH.fish_box(b, -0.95, 0.35, 0.1, rz=8)
        PH.fish_box(b, -0.9, -0.4, 0.1, rz=-10, fill=PH.SMOKED)
        PH.pot(b, -2.0, 0.0, 0.1, rz=90, L=0.6, r=0.24)
        PH.rope_coil(b, 2.25, 0.0, fd[len(fd) // 2][1][2] + 0.0, r=0.22)
        PP.oar(b, (-2.2, 0.62, 0.52), (0.9, 0.74, 0.5))
        with b.at(top[0] + 0.12, -0.12, 2.3):
            PP.lantern(b, s=0.2, h=0.3, sides=4, hang=0.1, lamp=False)
        for x in (-0.9, 0.7):                                # fenders over the side
            y = -H.hb(H.u_at(x)) - 0.09
            z = H.zs(H.u_at(x))
            PP.rope(b, [(x, y + 0.08, z + 0.02), (x, y, z - 0.18)], r=0.012)
            b.blob(0.1, 0.09, 0.16, mat="cloth", col=PP.HEMP, x=x, y=y - 0.02, z=z - 0.32, seg=6, rings=3, rough=0.08)
        PH.gull(b, -3.05, 0.0, H.zs(-1.0) + 0.22, rz=250)
