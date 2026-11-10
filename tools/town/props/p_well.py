# a well: rubble well head with a coping, a windlass with crank and bucket, a little shingled roof
import math
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Well", "kind": "prop", "group": "square", "clear": 1.8, "wobble": 0.02}


def build(b):
    Ro, Ri, H = 0.98, 0.64, 0.82
    with b.detail(0):
        b.revolve([(Ro + 0.07, -0.5), (Ro + 0.07, 0.0), (Ro, 0.1), (Ro - 0.03, H - 0.1)], "masonry", col="warm", seg=12)
        b.revolve([(Ro - 0.03, H - 0.1), (Ro + 0.05, H - 0.08), (Ro + 0.05, H), (Ri - 0.04, H), (Ri - 0.04, H - 0.1)], "ashlar", col="#f1e4cc", seg=12)
        b.revolve([(Ri, H - 0.1), (Ri, 0.3)], "masonry", col="dark", seg=12)
        b.disc(Ri, "water", seg=12, z=0.4)
        b.gable_roof(2.6, 1.5, pitch=40, mat="shingle", z=2.3, ridge="x", eave=0.22, verge=0.18, course=0.3, thick=0.08, barge=False)
    with b.detail(1):
        for sx in (-1, 1):
            b.beam((sx * 1.06, 0, -0.2), (sx * 1.06, 0, 2.3), w=0.15, mat="timber")
            b.beam((sx * 1.06, -0.78, 2.26), (sx * 1.06, 0.78, 2.26), w=0.11, mat="timber")
            b.beam((sx * 1.06, -0.55, 2.2), (sx * 1.06, 0, 2.2 + 0.55 * math.tan(rad(40))), w=0.08, mat="timber")
            b.beam((sx * 1.06, 0.55, 2.2), (sx * 1.06, 0, 2.2 + 0.55 * math.tan(rad(40))), w=0.08, mat="timber")
            b.beam((sx * 1.06, 0, 1.7), (sx * 0.62, 0, 2.2), w=0.08, mat="timber")
        b.beam((-1.06, 0, 2.24), (1.06, 0, 2.24), w=0.12, mat="timber")
        b.tube((-0.99, 0, 1.42), (1.3, 0, 1.42), r=0.085, mat="planks", col="darkoak", n=8, caps=True)        # the windlass
        PP.sweep(b, [(1.3, 0, 1.42), (1.3, 0, 1.1), (1.56, 0, 1.1)], r=0.022, n=4, mat="metal", col="iron")       # crank
    with b.detail(2):
        with b.at(0, 0, 1.42, ry=90):
            PP.rope_turns(b, z=-0.22, r=0.085, turns=7, rr=0.018)
        PP.rope(b, [(0.06, -0.1, 1.4), (0.06, -0.1, 1.18)], r=0.016)
        PP.bucket(b, 0.06, -0.1, 0.76, r=0.15, h=0.28, water=True)
        PP.bucket(b, -1.25, -0.75, 0, r=0.15, h=0.28)
        for (a, s) in ((30, 0.3), (140, 0.24), (250, 0.34)):
            with b.at(rz=a):
                b.stone(s, s * 0.8, s * 0.5, col="warm", y=-(Ro + 0.2), jitter=0.2)
        for a in (80, 200, 300):
            with b.at(rz=a):
                PP.tuft(b, 0, -(Ro + 0.14), 0, r=0.12, h=0.24)
        PP.clump(b, 0.7, 1.0, 0, r=0.22, h=0.2, flowers=["#f4f1e4", "#f5c842"])
        b.blob(0.3, 0.14, 0.4, mat="ivy", col=PP.LEAF, x=-0.7, y=0.72, z=0.42, seg=6, rings=3, wind=0.25, rough=0.3)
