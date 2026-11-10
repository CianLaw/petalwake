# The lookout: a retired courier built a stair turret on to his cottage just to have somewhere to watch the brooms come in, and left the front bay of its rail open for them.
# A small two-storey house set back behind a scrap of walled court; at its front a round rubble stair turret climbing to twice its height, to an open timber lookout under a slate cone.
# Rose plaster and warm rubble, slate cap, terracotta tiles on the house; accent plum.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC

META = {"name": "The Lookout", "kind": "tower-house", "lot": (6.0, 7.0), "terrace": True}


def build(b):
    acc = "plum"
    # --- the house, set back
    W, D, cy = 5.5, 3.8, 4.5
    H0, H = 2.9, 2.7
    top = H0 + H
    g = b.body(W, D, H0, mat="masonry", col="warm", y=cy)
    P.plinth(g, h=0.3)
    up = b.body(W, D, H, mat="plaster", col="rose", y=cy, z=H0)
    P.door(g.front, 4.75, w=0.9, h=2.0, z=0.17, col=acc, frame="stone", steps=1)
    L.hood(g.front, 4.75, 2.62, w=1.4, out=0.6, kind="pent")
    P.window(g.front, 3.78, 1.1, w=0.6, h=1.0, bars=(1, 1))
    P.window(up.front, 4.5, 0.85, w=0.85, h=1.2, shutters=acc, box=True)
    k = g.back
    P.door(k, 1.3, w=0.9, h=2.0, z=0.17, col=acc, frame="timber", steps=1)
    P.window(k, 3.9, 1.1, w=1.0, h=1.2, shutters=acc)
    P.window(up.back, 1.3, 0.85, w=0.8, h=1.15, shutters=acc); P.window(up.back, 3.9, 0.85, w=0.8, h=1.15, shutters=acc, box=True)
    P.window(up.left, D / 2, H + 0.45, w=0.5, h=0.7); P.window(up.right, D / 2, H + 0.45, w=0.5, h=0.7)
    rise = up.gable(ridge="x", pitch=45, eave=0.3, verge=0.04, sag=0.06)
    L.cut_gable(up.left); L.cut_gable(up.right)
    P.chimney(b, W / 2 - 0.42, cy, top + 1.0, 2.5, w=0.66, d=0.85, mat="brick", pots=2)
    # --- the stair turret
    tx, ty, zf = -0.8, 1.95, 10.2
    t = b.round(1.45, zf, r1=1.28, mat="masonry", col="warm", x=tx, y=ty, seg=18)
    P.door(t, 0, w=0.9, h=2.05, arch=0.45, z=0.34, col=acc, frame="stone", steps=2, lamp=True)
    P.round_base(b, 1.45, h=0.9, out=0.2, seg=18, ring=t)
    for a, z in ((300, 3.0), (40, 4.7), (320, 6.4), (90, 6.9), (30, 8.1)):
        P.window(t, a, z, w=0.45, h=1.0, arch=0.22, bars=(0, 1))
    P.stones(t, n=30, z0=0.9, z1=9.4)
    P.ivy(t, 252, 0.4, w=1.5, h=4.2, n=9)
    with b.at(tx, ty, 0):
        PC.corbels(b, 1.29, zf - 0.16, n=12, out=0.5, drop=0.55)
        b.revolve([(1.3, zf - 0.16), (1.85, zf - 0.16), (1.85, zf)], "ashlar", col="stone", seg=18)
        b.disc(1.85, "flagstone", col="sand", seg=18, z=zf)
        for i in range(6):
            a = rad(30 + 60 * i)
            px, py = 1.68 * math.sin(a), -1.68 * math.cos(a)
            b.beam((px, py, zf), (px, py, zf + 2.78), w=0.15, lod=0)
            with b.detail(1):
                for da in (-0.32, 0.32):
                    qx, qy = 1.68 * math.sin(a + da), -1.68 * math.cos(a + da)
                    b.beam((px, py, zf + 2.15), (qx, qy, zf + 2.68), w=0.08, caps=False)
        PC.rail_arc(b, 1.68, 30, 330, z=zf, h=1.0, style="balusters", col="darkoak")
        b.revolve([(1.58, zf + 2.62), (1.8, zf + 2.62), (1.8, zf + 2.78), (1.58, zf + 2.78)], "timber", col="darkoak", seg=18)
        b.disc(1.75, "planks", col="darkoak", seg=18, z=zf + 2.77, down=True)
        with b.at(0, -0.15, zf):
            P.landing_mark(b, 0.85)
        L.trapdoor(b, 0.0, 1.1, zf, w=0.65, d=0.6)
        P.lantern_at(b, 1.0, 1.25, zf + 2.3, arm=0.3)
    b.cone_roof(1.72, 2.45, mat="slate", x=tx, y=ty, z=zf + 2.78, seg=18, eave=0.3, flare=0.45, course=0.45)
    b.pad(tx, ty - 0.15, zf, radius=0.9, face=0, name="The lookout")
    # --- the court in the angle, and the pavement
    PC.yard(b, tx + 1.38, W / 2, 2.6, h=1.05, y0=0.9, gate=(1.85, 0.9), left=False, right=True, gate_col=acc, pickets=True)
    P.tree(b, 1.75, 1.9, 0, h=2.9, crown=0.6)
    PC.flowers(b, 2.25, 2.3, 0, w=0.7, d=0.4)
    P.bench(b, 1.0, 0.45, 0, w=1.1)
    L.flowerpot(b, 2.35, 0.55, 0, r=0.17, h=0.3, flower="#b08ae6")
    L.cat(b, 2.55, 0.92, 1.2, rz=-70, col="#8c8580")
    L.downpipe(b, -W / 2 + 0.3, cy + D / 2 + 0.06, 0, top - 0.2, face=180)
