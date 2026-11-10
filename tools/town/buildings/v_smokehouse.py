# The smokehouse: herring go in silver on Monday and come out gold on Thursday, and the whole north end of the
# village smells of oak smoke and is glad of it. A tall narrow shed of tarred boards on a rubble base, slatted
# vents in both gables and a louvred ridge that breathes smoke. Tar black, dark stone, mustard paint.
from kit import *
import parts as P
import parts_v as V
import parts_h as PH
import parts_k as PK

META = {"name": "Cairnwick Smokehouse", "kind": "works", "lot": (5.0, 6.0), "wobble": 0.035}


def build(b):
    ac = "mustard"
    b.footprint(-2.4, 0.0, 2.4, 5.9, 3.6)
    W, D, H = 4.1, 4.9, 3.6
    c = V.BBody(b, W, D, H, mat="planks", col=V.TAR, batter=0.018, depth=0.16)
    V.footing(c, h=1.4, out=0.13, col="dark", boulders="f", size=(0.5, 0.9))
    V.door(c.front, 1.55, w=1.5, h=2.1, col=ac, double=True, lintel="timber", jambs=False)
    PH.louvre(c.front, W / 2, 4.05, w=0.95, h=1.1, n=7, col=ac)
    PH.louvre(c.back, W / 2, 4.05, w=0.95, h=1.1, n=7, col=ac)
    for wl in (c.left, c.right):
        PH.louvre(wl, 1.45, 2.55, w=1.1, h=0.55, n=4, col=ac)
        PH.louvre(wl, 3.45, 2.55, w=1.1, h=0.55, n=4, col=ac)
    V.door(c.back, 1.3, w=0.85, h=1.8, col=ac, lintel="timber", jambs=False, step=False)
    with b.detail(2):                    # cover strips on the boards
        for wl in c.walls:
            with b.frame(wl.m):
                n = int(wl.w / 0.5)
                for i in range(1, n):
                    u = wl.w * i / n
                    if any(o["u0"] - 0.05 < u < o["u1"] + 0.05 for o in wl.ops):
                        continue
                    V.beam(b, (u, -0.012, 1.42), (u, -0.012, H * 1.0), w=0.06, h=0.025, mat="planks", col=shade(V.TAR, 0.8), up=(0, 1, 0), caps=False)
    rf = c.gable(ridge="y", pitch=50, mat="slate", eave=0.2, verge=0.24, barge_col="blackoak")
    RZ = H + rf.rise
    PK.ridge_vent(b, 0.0, D / 2, RZ, L=2.4, w=0.95, h=0.6, drop=0.5, ridge="y", roof="slate", pitch=40, col=ac)
    b.smoke(0.0, D / 2 - 0.6, RZ + 1.0, strength=1.2); b.smoke(0.0, D / 2 + 0.7, RZ + 1.0, strength=1.0)
    b.smoke(0.0, -0.1, 4.9, strength=0.6)
    # ------------------------------------------------------------------ the day's work round the door
    V.fish_rack(b, 1.45, -0.62, 0, w=1.25, h=1.7, n=7)
    PK.barrel(b, -1.75, -0.45, 0, r=0.33, h=0.88)
    PK.barrel(b, -1.2, -0.75, 0, r=0.3, h=0.8)
    PH.fish_box(b, -0.1, -0.7, 0, rz=8)
    PH.fish_box(b, 0.05, -0.68, 0.2, rz=-6)
    PH.cat(b, 0.75, -0.95, 0, rz=150)
    PK.firewood(b, 1.0, D + 0.02, 0, w=1.9, h=1.1, d=0.5, rz=180)
    PK.barrel(b, -1.5, D + 0.45, 0, r=0.32, h=0.85)
