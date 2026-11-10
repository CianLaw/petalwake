# kit exemplar 2: a jettied shop-house, a flat-topped watch tower with a roof terrace, an eight-sided bell turret.
# (Also exercises every part once.)
from kit import *
import parts as P

META = {"name": "Parts test (kit example)", "kind": "test"}

def build(b):
    # ---------------- jettied timber shop-house (left)
    with b.at(-9, 0):
        g = b.body(6.4, 7.0, 3.1, mat="masonry", col="warm")
        P.plinth(g, h=0.5)
        P.door(g.front, 1.5, w=1.1, h=2.15, col="red", frame="timber", steps=1, z=0.18, double=True, lamp=True)
        P.window(g.front, 4.4, 0.9, w=2.0, h=1.6, bars=(3, 1), lintel="timber", box=True)
        P.awning(g.front, 4.4, 2.75, w=2.5, cols=("stripe_red", "linen"))
        P.sign(g.front, 0.5, 2.9, emblem="loaf", col="brown")
        up = b.body(7.0, 7.6, 2.9, mat="plaster", col="butter", z=3.1, y=3.5 - 0.0, floor="planks")
        for wl in up.walls:
            P.timber_frame(wl, braces="auto")
        P.window(up.front, 1.9, 0.95, shutters="red"); P.window(up.front, 5.1, 0.95, shutters="red", box=True)
        P.window(up.right, 3.8, 0.95, w=0.75)
        P.balcony(up.left, 3.8, 0.1, w=2.0, out=1.0, rail="cross")
        P.door(up.left, 3.8, w=0.9, h=2.0, z=0.12, col="red", frame="timber")
        with b.detail(1):
            for i in range(6):
                x = -3.3 + 6.6 * i / 5
                b.beam((x, 0.05, 2.55), (x, -0.32, 3.05), w=0.13)
        up.gable(ridge="y", pitch=52, mat="tiles", sag=0.1, eave=0.45, verge=0.4)
        P.dormer(b, -2.55, 3.6, 7.6, w=1.1, h=0.95, depth=1.6, face=270, shutters="red")
        P.chimney(b, 2.2, 5.6, 6.2, 4.0, mat="masonry", col="warm", pots=1)
        P.weathervane(b, 0, 3.5, 10.9)
        P.bench(b, 4.6, -0.6, rz=10); P.sack(b, -4.2, -0.5); P.tree(b, 5.3, 6.5, h=4.6)
    # ---------------- flat-topped watch tower with a roof terrace (middle)
    with b.at(1.5, 3.5):
        sq = b.body(5.2, 5.2, 13.0, mat="ashlar", col="sand", y=0)
        P.plinth(sq, h=1.1, out=0.14, col="grey")
        P.quoins(sq, z0=1.1)
        P.band(sq, 9.2)
        P.door(sq.front, 2.6, w=1.0, h=2.1, arch=0.5, col="navy", steps=3, z=0.55)
        P.window(sq.front, 2.6, 5.0, w=0.7, h=1.4, arch=0.35, shutters="navy")
        P.window(sq.right, 2.6, 7.2, w=0.7, h=1.4, arch=0.35)
        P.clock(sq.front, 2.6, 10.9, r=0.95)
        P.exposed(sq.left, "base")
        with b.at(z=13.0):
            b.box(5.2, 5.2, 0.12, "flagstone", col="sand", z=-0.12)
            P.crenels(b, w=5.6, d=5.6, z=0.0, h=0.6, wall=0.55, mat="ashlar", col="sand")
            P.landing_mark(b, 1.5)
            b.pad(0, 0, 0.0, radius=1.9, face=0, name="Watch roof")
            P.flag(b, 2.2, 2.2, 0.0, pole=3.2, kind="banner", col="stripe_blue", w=1.4, h=0.9)
            P.ladder(b, 0); P.barrel(b, -1.8, 1.8); P.crate(b, 1.6, -1.7, rz=30)
        with b.at(3.4, -2.2, 0):
            P.stairs(b, w=1.0, n=3)
    # ---------------- eight-sided bell turret with an open belfry (right)
    with b.at(10.5, 3.5):
        P.round_base(b, 2.5, h=0.8, out=0.25, seg=8)
        faces = b.polygon(8, 2.5, 9.0, mat="masonry", col="grey", taper=0.94)
        P.door(faces[0], faces[0].w / 2, w=0.9, h=2.0, arch=0.45, col="plum", z=0.3, steps=1)
        P.window(faces[2], faces[2].w / 2, 4.0, w=0.5, h=1.2, arch=0.25)
        P.window(faces[5], faces[5].w / 2, 6.0, w=0.5, h=1.2, arch=0.25)
        P.ring_band(b, 2.35, 9.0, h=0.25, out=0.2, seg=8)
        with b.at(z=9.25):
            b.disc(2.5, "planks", col="greyoak", seg=8)
            for k in range(8):
                with b.at(rz=45 * k + 22.5):
                    b.beam((0, -2.2, 0), (0, -2.2, 2.6), w=0.2)
            P.railing(b, P.circle(2.25, 8, 0.0, 22.5, 382.5)[:-1], h=0.9, closed=True, style="solid", col="darkoak")
            P.bell(b, 0, 0, 2.3, r=0.45, beam=4.2)
            P.ruin_top(b, 2.3, 0.0, arc=(200, 330), hmax=1.0, t=0.4)
        b.cone_roof(2.3, 4.6, mat="shingle", z=11.85, seg=8, smooth=False, eave=0.6, flare=0.5)
        P.lantern(faces[0], faces[0].w / 2 + 0.8, 2.4)
        P.ivy(faces[7], 0.9, 0.2, w=1.6, h=3.4)
