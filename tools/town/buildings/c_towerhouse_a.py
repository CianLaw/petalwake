# The Warden's tower-house: five rooms one above another and a roof to watch the road from. The warden's widow lets the upper floors to students of the library and grows beans on the terrace.
# Massing: a battered square tower of five storeys; the parapet corbelled out all round, battlements with one wide embrasure left for the rider; on the terrace a gabled cap-house over the stair head and a tall chimney; a timber oriel on brackets at the third floor.
# Materials: warm rubble with ashlar quoins and bands, slate on the cap-house, dark oak oriel with cream panels. Accent: green.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Warden's Tower-house", "kind": "tower", "lot": (7.0, 7.0), "lean": (-0.001, 0.0006)}

CY = 3.2
W, H, INS = 5.7, 15.0, 0.28
ZT = H + 0.16                 # terrace floor


def build(b):
    tb = PC.tbody(b, W, W, H, inset=INS, mat="masonry", col="warm", x=0, y=CY)
    walls(b, tb)
    oriel(b, tb)
    with b.at(0, CY, H):
        terrace(b)


def walls(b, tb):
    PC.plinth(tb, h=0.95, out=0.12, doors=[("front", 3.65, 1.1)])
    PC.tquoins(tb, z0=0.95, z1=H - 0.6, size=(0.6, 0.34, 0.56))
    PC.tband(tb, 3.25, h=0.2, out=0.07)
    PC.tband(tb, 11.95, h=0.18, out=0.06)
    f, r, k, l = tb.front, tb.right, tb.back, tb.left
    P.door(f, 3.65, w=1.1, h=2.2, arch=0.55, col="green", z=0.5, steps=3, lamp=True)
    P.window(f, 1.45, 1.35, w=0.6, h=0.85, lintel="stone", bars=(2, 1))
    P.window(f, 1.5, 4.15, w=0.85, h=1.4, shutters="green", box=True)
    P.window(f, 4.15, 4.15, w=0.85, h=1.4, shutters="green")
    P.window(f, 4.2, 7.1, w=0.8, h=1.35, arch=0.36, shutters="green")
    P.window(f, 1.5, 10.0, w=0.75, h=1.3, arch=0.34)
    P.window(f, 4.05, 10.0, w=0.75, h=1.3, arch=0.34, shutters="green", box=True)
    P.window(f, 2.85, 12.75, w=0.6, h=1.0, arch=0.28, lintel=None)
    P.window(l, 3.8, 1.6, w=0.6, h=0.9, bars=(2, 1))
    P.window(l, 2.0, 4.3, w=0.8, h=1.35, shutters="green")
    P.window(l, 3.8, 7.2, w=0.8, h=1.35, arch=0.36, shutters="green", box=True)
    P.window(l, 2.1, 10.1, w=0.75, h=1.3, arch=0.34)
    P.window(l, 3.6, 12.75, w=0.6, h=1.0, arch=0.28, lintel=None)
    P.window(r, 2.2, 4.3, w=0.8, h=1.35)
    P.window(r, 3.6, 7.2, w=0.8, h=1.35, arch=0.36, shutters="green")
    P.window(r, 2.0, 10.1, w=0.75, h=1.3, arch=0.34, shutters="green")
    P.window(k, 1.6, 4.3, w=0.8, h=1.35, shutters="green")
    P.window(k, 4.0, 7.2, w=0.8, h=1.35, arch=0.36)
    P.window(k, 1.8, 10.1, w=0.75, h=1.3, arch=0.34, shutters="green", box=True)
    P.door(k, 4.3, w=0.85, h=1.9, col="green", z=0.3, frame="timber", steps=1)
    P.exposed(l, "base", n=8, col="grey")
    P.ivy(k, 3.2, 0.7, w=2.2, h=6.0, n=13)
    P.ivy(r, 4.8, 0.7, w=1.4, h=3.6, n=6, lod=2)
    P.laundry(b, (-W / 2 - 0.05, CY - 1.0, 9.2), (-W / 2 - 0.15, CY + 1.9, 8.6), n=4, sag=0.25)
    P.barrel(b, 0.6, CY - W / 2 - 0.45); P.bench(b, -1.3, CY - W / 2 - 0.5, w=1.4); P.planter(b, 2.2, CY - W / 2 - 0.3, w=0.7, bush=True)


def oriel(b, tb):
    """The oriel: a timber bay on brackets on the third floor, looking down the street."""
    w, dp, h = 1.9, 1.0, 2.3
    with tb.front.on(1.55, 6.95):
        bd = b.body(w, dp, h, mat="plaster", col="cream", x=0, y=0.2 - dp / 2, z=0, depth=0.12, floor="planks", foot=False)
        P.timber_frame(bd.front, posts=[0, 0.3, w - 0.3, w], rails=[0, 0.8, h], braces=[], w=0.13)
        P.timber_frame(bd.left, u0=0.2, posts=[0.2, dp], rails=[0, 0.8, h], braces=[(dp, 0.8, 0.2, 0)], w=0.13)
        P.timber_frame(bd.right, u1=0.8, posts=[0, 0.8], rails=[0, 0.8, h], braces=[(0, 0.8, 0.8, 0)], w=0.13)
        P.window(bd.front, w / 2, 0.9, w=1.2, h=1.2, bars=(2, 1), lintel=None, depth=0.1, box=True)
        PC.shed_roof(b, w + 0.3, dp + 0.1, pitch=38, z=h, x=0, y=0.22, mat="slate", eave=0.12, verge=0.1, course=0.3, thick=0.08)
        PC.cheeks(b, w, dp - 0.2, (dp - 0.2) * math.tan(rad(38)), mat="plaster", col="cream", x=0, y=0.2, z=h)
        with b.detail(1):
            for sx in (-1, 1):
                b.beam((sx * 0.75, 0.04, -1.25), (sx * 0.75, -0.72, -0.05), w=0.15)
            b.beam((-w / 2 - 0.04, -0.74, -0.09), (w / 2 + 0.04, -0.74, -0.09), w=0.14, h=0.16)


def terrace(b):
    """The roof: corbelled parapet, battlements open at the front-left, cap-house, chimney, beans."""
    hw = W / 2 - INS
    out = 0.42
    for (ox, oy, rz, L) in PC.rect_sides(2 * hw, 2 * hw):
        with b.at(ox, oy, 0, rz=rz):
            PC.corbel_row(b, L, z=0.0, n=8, out=out, drop=0.62, w=0.28, steps=2)
    e = 2 * (hw + out)
    b.box(e, e, 0.16, "flagstone", col="sand", z=0.0, bottom=True)
    z = 0.16
    PC.battlements(b, PC.rect_sides(e, e), z=z, t=0.34, wall=0.6, h=0.7, merlon=0.8, gap=0.52, gaps={0: [(0.75, 2.75)]})
    px, py = -1.05, -1.0
    with b.at(px, py, z):
        P.landing_mark(b, 1.2)
    b.pad(px, py, z, radius=1.3, face=0, name="Warden's terrace")
    # cap-house over the stair, back-right
    ch = b.body(2.3, 2.5, 2.0, mat="masonry", col="warm", x=1.42, y=1.38, z=z, foot=False)
    P.door(ch.front, 1.0, w=0.8, h=1.75, col="green", z=0.04, frame="timber", lamp=True)
    P.window(ch.left, 1.3, 0.8, w=0.55, h=0.8, lintel="timber")
    rise = ch.gable(ridge="y", pitch=50, mat="slate", eave=0.2, verge=0.22, course=0.36, thick=0.1)
    b.footprint(0.27, 0.13, 2.57, 2.63, z + 2.0)
    P.flag(b, 1.42, 0.1, z + 2.0 + rise - 0.05, pole=1.7, w=1.1, h=0.5, col="stripe_green")
    PC.stack(b, -1.95, 2.05, z, 3.1, w=0.75, d=0.6, flues=2, style="diagonal")
    # the widow's beans, a seat in the sun, washing
    P.planter(b, -2.2, 0.55, z, w=0.42, d=1.5 * 0.3 + 0.2, col="#b58a66")
    with b.detail(2):
        for i in range(3):
            y0 = 0.25 + 0.3 * i
            for dx, dy in ((-0.14, -0.1), (0.14, -0.1), (0.0, 0.14)):
                b.beam((-2.2 + dx, y0 + dy, z + 0.3), (-2.2, y0, z + 1.9), w=0.025, mat="planks", col="#c9b48a", caps=False)
            PC.climber(b, (-2.2, y0, z + 0.4), (-2.2, y0, z + 1.6), n=4, r=0.16, bloom=["#e8497a", "#ffffff"], lod=2)
    P.bench(b, 0.95, -0.1, z, rz=180, w=1.2)
    P.laundry(b, (0.3, 0.2, z + 1.85), (-1.75, 2.0, z + 1.9), n=3, sag=0.22)
    P.planter(b, 2.2, -2.2, z, w=0.6, bush=True)
