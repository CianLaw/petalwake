# The water tower: the hilltop has no well, so the rain off every roof on the Crown runs to this cistern and a boy pumps it up to the tank each morning. The keeper's flat roof is the best seat in town on a summer evening.
# Massing: a battered square stone shaft; a boarded tank house wider than the shaft, carried on big oak brackets; a flat railed roof with a hatch, a fish for a weathervane and a bucket hoist; a lean-to pump shed and a stone trough at the foot.
# Materials: grey-warm rubble with ashlar quoins, weathered boards between dark oak posts with iron bands, a lead roof edge, slate on the lean-to. Accent: teal.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Cistern Tower", "kind": "tower", "lot": (7.0, 7.0), "lean": (0.001, 0.0012)}

CY = 3.5
SW, SH, INS = 3.7, 9.2, 0.22          # shaft: width at the foot, height, batter
TW, TH = 6.0, 3.0                     # tank house
ZR = SH + TH                          # the roof
STONE = mix("warm", "grey", 0.4)
BOARD = "#cdbda2"


def build(b):
    shaft(b)
    tank(b)
    roof(b)
    foot(b)


def shaft(b):
    tb = PC.tbody(b, SW, SW, SH, inset=INS, mat="masonry", col=STONE, x=0, y=CY)
    PC.plinth(tb, h=0.9, out=0.1, col=STONE, doors=[("front", SW / 2, 1.0)])
    PC.tquoins(tb, z0=0.9, size=(0.58, 0.34, 0.52))
    PC.tband(tb, 6.9, h=0.2, out=0.07)
    P.door(tb.front, SW / 2, w=1.0, h=2.1, arch=0.5, col="teal", z=0.45, steps=2, lamp=True)
    P.window(tb.front, SW / 2 + 0.2, 4.5, w=0.62, h=1.25, arch=0.3, shutters="teal", box=True)
    P.window(tb.left, 1.5, 3.3, w=0.55, h=1.1, arch=0.27)
    P.window(tb.left, 2.3, 5.5, w=0.5, h=1.0, arch=0.25, lintel=None)
    P.window(tb.right, 1.6, 5.2, w=0.62, h=1.25, arch=0.3, shutters="teal")
    P.window(tb.back, 1.7, 3.6, w=0.55, h=1.1, arch=0.27)
    P.window(tb.back, 2.2, 6.0, w=0.5, h=1.0, arch=0.25, lintel=None)
    P.exposed(tb.right, "base", n=8, col="grey")
    P.ivy(tb.back, 0.7, 0.6, w=1.6, h=4.6, n=9)
    P.ivy(tb.right, 3.1, 0.6, w=1.2, h=3.0, n=5, lod=2)
    b.tb = tb


def tank(b):
    """The boarded tank house on its brackets."""
    bd = b.body(TW, TW, TH, mat="planks", col=BOARD, x=0, y=CY, z=SH, depth=0.12, floor="planks", foot=False)
    for wl in bd.walls:
        P.timber_frame(wl, posts=[TW * i / 4 for i in range(5)], rails=[0.0, TH], braces=[], w=0.17)
    P.window(bd.front, 1.5, 1.0, w=0.7, h=0.9, lintel=None, shutters="teal", depth=0.1, bars=(0, 2))
    P.window(bd.front, 4.5, 1.0, w=0.7, h=0.9, lintel=None, shutters="teal", depth=0.1, bars=(0, 2))
    P.window(bd.left, 3.75, 1.0, w=0.7, h=0.9, lintel=None, shutters="teal", depth=0.1, bars=(0, 2))
    P.window(bd.right, 2.25, 1.0, w=0.7, h=0.9, lintel=None, shutters="teal", depth=0.1, bars=(0, 2))
    P.window(bd.back, 2.25, 1.0, w=0.7, h=0.9, lintel=None, shutters="teal", depth=0.1, bars=(0, 2))
    hs = SW / 2 - INS                                  # half-width of the shaft top
    for (ox, oy, rz, L) in PC.rect_sides(TW, TW, 0, CY):
        with b.at(ox, oy, SH, rz=rz):
            with b.detail(2):                           # iron bands round the boards
                for zz in (0.75, 2.25):
                    b.beam((0, -0.03, zz), (L, -0.03, zz), w=0.03, h=0.09, mat="metal", col="iron", caps=False, up=(0, 0, 1))
            for x in (L / 2 - 1.15, L / 2, L / 2 + 1.15):      # struts from the shaft (the middle one is always drawn)
                b.beam((x, TW / 2 - hs - 0.02, -2.5), (x, 0.14, -0.2), w=0.2, lod=0 if x == L / 2 else 1)
            with b.detail(1):                           # bearers under the floor
                for i in range(7):
                    x = 0.25 + (L - 0.5) * i / 6
                    b.beam((x, 1.0, -0.1), (x, -0.2, -0.1), w=0.15, h=0.18, lod=1 if i % 2 == 0 else 2)
    for sx in (-1, 1):                                  # a strut under each corner too
        for sy in (-1, 1):
            b.beam((sx * (hs + 0.02), CY + sy * (hs + 0.02), SH - 2.7), (sx * (TW / 2 - 0.12), CY + sy * (TW / 2 - 0.12), SH - 0.2), w=0.2, lod=0)
    b.footprint(-TW / 2, CY - TW / 2, TW / 2, CY + TW / 2, ZR)


def roof(b):
    """The keeper's roof: boards inside a cross-braced rail, open at the front; hatch, vane, hoist, a seat."""
    with b.at(0, CY, ZR):
        b.box(TW + 0.34, TW + 0.34, 0.16, "metal", col="lead", z=0.0, bottom=True)
        b.box(TW + 0.2, TW + 0.2, 0.16, "timber", col="darkoak", z=-0.16, top=False, lod=1)
        b.box(TW - 0.1, TW - 0.1, 0.05, "planks", col="greyoak", z=0.16)
        z = 0.21
        e = TW / 2 - 0.06
        P.railing(b, [(-1.05, -e, z), (-e, -e, z), (-e, e, z), (e, e, z), (e, -e, z), (1.05, -e, z)], h=1.0, style="cross", col="darkoak")
        with b.at(0, -0.95, z):
            P.landing_mark(b, 1.35)
        b.pad(0, -0.95, z, radius=1.5, face=0, name="Cistern roof")
        PC.hatch(b, 1.75, 1.75, z, w=0.9, d=0.9, rz=0)
        PC.vane(b, -2.45, 2.45, z, h=2.4, shape="fish", size=1.25)
        P.bench(b, -0.9, 2.45, z, rz=180, w=1.5)
        P.barrel(b, -2.4, 0.9, z, r=0.3, h=0.8)
        P.planter(b, 0.9, 2.55, z, w=0.9)
        P.planter(b, -2.5, -0.4, z, w=0.5, bush=True)
        with b.detail(1):                               # the bucket hoist over the right-hand edge
            b.beam((2.55, 0.2, z), (2.55, 0.2, z + 2.0), w=0.14)
            b.beam((1.9, 0.2, z + 1.9), (3.22, 0.2, z + 1.9), w=0.12, h=0.14)
            b.beam((2.55, 0.2, z + 1.0), (3.1, 0.2, z + 1.84), w=0.09)
            b.beam((3.16, 0.2, z + 1.84), (3.16, 0.2, z - 4.4), w=0.03, mat="cloth", col="#8a7a66", caps=False)
            with b.at(3.16, 0.2, z - 4.8):
                b.revolve([(0.12, 0.0), (0.16, 0.4)], "planks", col="#c9a57a", seg=8, close_bottom=True)
                b.revolve([(0.14, 0.4), (0.1, 0.02)], "planks", col="#8a6f52", seg=8)


def foot(b):
    """The pump shed leaning on the shaft, the pipe and the trough."""
    hw = SW / 2
    sh = b.body(1.3, 2.6, 1.9, mat="masonry", col=STONE, x=-hw - 0.6, y=CY + 0.2)
    PC.plinth(sh, h=0.4, out=0.06, col=STONE, doors=[("front", 0.65, 0.7)])
    P.door(sh.front, 0.65, w=0.7, h=1.6, col="teal", z=0.12, frame="timber")
    P.window(sh.left, 1.3, 0.8, w=0.6, h=0.7, lintel="timber")
    with b.at(-hw + 0.08, CY + 0.2, 1.9, rz=270):
        PC.shed_roof(b, 2.9, 1.42, pitch=26, z=0.0, mat="slate", eave=0.14, verge=0.12, course=0.34, thick=0.1)
    with b.detail(1):                                   # the rising main and the overflow down to the trough
        b.tube((hw - 0.5, CY - hw + 0.02, SH + 0.1), (hw - 0.38, CY - hw - 0.06, 1.25), r=0.07, mat="metal", col="lead", n=6)
        b.tube((hw - 0.38, CY - hw - 0.06, 1.25), (hw - 0.38, CY - hw - 0.42, 1.05), r=0.06, mat="metal", col="lead", n=6)
    with b.at(hw - 0.35, CY - hw - 0.62, 0):
        b.box(1.5, 0.75, 0.62, "ashlar", col="grey", top=False)
        b.box(1.5, 0.75, 3.0, "ashlar", col=shade("grey", 0.8), z=-3.0, top=False)
        b.box(1.26, 0.51, 0.02, "water", col="#9fd3d6", z=0.5)
        with b.detail(1):
            for (x, y, w, d) in ((0, -0.31, 1.5, 0.13), (0, 0.31, 1.5, 0.13), (-0.69, 0, 0.13, 0.75), (0.69, 0, 0.13, 0.75)):
                b.box(w, d, 0.05, "ashlar", col="stone", x=x, y=y, z=0.6)
    P.barrel(b, -0.95, CY - hw - 0.45, r=0.27, h=0.72)
    PC.flowers(b, -1.9, CY - hw - 0.2, 0, w=0.9, d=0.4, n=4)
    PC.tuft(b, 2.1, CY + hw + 0.3, 0, r=0.3); PC.tuft(b, -0.6, CY + hw + 0.25, 0, r=0.26)
