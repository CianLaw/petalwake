# The Scholars' Library: three hundred years of the town's books under one steep roof, and a reading tower built so that old eyes could have the light all day. Riders bring back the books that were borrowed down the coast and hand them in at the balcony.
# Massing: a tall hall, gable to the street, buttressed between tall windows; a round reading tower at its front-left corner, set back behind a small forecourt, with a ring of windows under a conical roof and a half-round stone balcony on a moulded corbel.
# Materials: pale ashlar hall with rubble buttresses and tower, slate roofs, ivory frames. Accent: navy (the librarian and the star-gazer share a paint pot).
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Scholars' Library", "kind": "library", "lot": (10.0, 9.0), "lean": (0.0004, -0.0003)}

HX0, HX1, HY0, HY1, HH = -1.5, 4.4, 0.45, 8.6, 6.2      # the hall
HW, HD, HCX, HCY = HX1 - HX0, HY1 - HY0, (HX0 + HX1) / 2, (HY0 + HY1) / 2
TX, TY = -2.48, 4.15                                    # the reading tower
ZJ, ZE = 11.6, 16.4                                     # tower: foot of the reading room, eaves
ZB = 12.6                                               # balcony floor


def rt(z):
    return 2.1 - 0.15 * z / ZE


def build(b):
    hall(b)
    with b.at(TX, TY):
        tower(b)
    court(b)


def hall(b):
    bd = b.body(HW, HD, HH, mat="ashlar", col="sand", x=HCX, y=HCY)
    PC.plinth(bd, h=0.8, out=0.1, doors=[("front", HW / 2, 1.5)])
    f, r, k, l = bd.front, bd.right, bd.back, bd.left
    P.door(f, HW / 2, w=1.5, h=2.4, arch=0.6, col="navy", z=0.34, steps=2, double=True, lamp=True)
    P.window(f, HW / 2, 2.95, w=1.9, h=3.15, arch=0.95, bars=(3, 3), depth=0.3)
    P.sign(f, HW / 2 + 1.75, 2.75, emblem="book", col="navy")
    P.window(f, 0.95, 1.5, w=0.5, h=1.3, arch=0.25, lintel=None)
    for u in (1.3, 3.25, 5.2, 7.05):                    # the long side: tall windows between buttresses
        P.window(r, u, 1.7, w=0.9, h=3.5, arch=0.45, bars=(1, 4))
    for u in (0.28, 2.28, 4.22, 6.12, 7.87):
        with b.at(HX1, HY0 + u, 0, rz=90):
            PC.buttress(b, w=0.56, d=0.44, h=5.4)
    for u in (1.3, 3.25):
        P.window(l, u, 1.7, w=0.9, h=3.5, arch=0.45, bars=(1, 4))
    with b.at(HX0, HY1 - 2.28, 0, rz=270):
        PC.buttress(b, w=0.56, d=0.5, h=5.4)
    with b.at(HX0, HY1 - 0.28, 0, rz=270):
        PC.buttress(b, w=0.56, d=0.5, h=5.4)
    P.window(k, HW / 2, 2.2, w=1.7, h=3.7, arch=0.85, bars=(3, 3), depth=0.3)
    P.door(k, 0.85, w=0.8, h=1.9, col="navy", z=0.25, frame="timber")
    P.band(bd, HH - 0.2, h=0.2, out=0.08)
    rise = bd.gable(ridge="y", pitch=55, mat="slate", eave=0.3, verge=0.14, barge=False)
    for wl in (f, k):                                   # stone copings up the two gables, a finial block on each
        with wl.on(0.0, HH):
            for sx in (0, 1):
                x0, x1 = (0.0, HW / 2) if sx == 0 else (HW, HW / 2)
                b.beam((x0, 0.1, 0.02), (x1, 0.1, rise + 0.1), w=0.34, h=0.16, mat="ashlar", col="stone", lod=1, up=(0, 1, 0))
            b.box(0.34, 0.34, 0.5, "ashlar", col="stone", x=HW / 2, y=0.12, z=rise - 0.05, lod=1)
            b.box(0.2, 0.2, 0.3, "ashlar", col="stone", x=HW / 2, y=0.12, z=rise + 0.45, lod=2, taper=0.3)
    # the ridge turret: a louvred vent for the lamp smoke
    with b.at(HCX, HCY + 0.6, HH + rise - 0.35):
        fl = b.polygon(8, 0.55, 1.5, mat="planks", col="#cdbfa8", foot=False)
        for i, wl in enumerate(fl):                     # louvres: dark slots with slats
            with wl.on(wl.w / 2, 0.5):
                b.quad((-0.13, -0.012, 0), (0.13, -0.012, 0), (0.13, -0.012, 0.75), (-0.13, -0.012, 0.75), "paint", col="!#1c1a1a", lod=1)
                for j in range(4):
                    b.box(0.3, 0.05, 0.03, "planks", col="darkoak", x=0, y=-0.03, z=0.08 + 0.19 * j, lod=2)
        b.cone_roof(0.55, 1.9, mat="slate", z=1.5, seg=8, smooth=False, eave=0.2, flare=0.5, course=0.62)
    PC.stack(b, HX0 + 0.75, HY1 - 0.9, HH + 0.5, 4.6, w=0.7, d=0.6, flues=2, mat="masonry", col="warm", style="round")
    P.ivy(k, HW - 0.9, 0.4, w=1.6, h=4.4, n=9, lod=2)
    P.ivy(r, 7.6, 0.3, w=0.8, h=2.6, n=4, lod=2)
    PC.doves(b, [(HCX + 0.9, HY0 + 2.0, HH + rise * 0.72), (HCX - 0.2, HCY - 1.3, HH + rise + 0.12)])


def tower(b):
    """The reading tower (frame: its own axis)."""
    PC.round_base(b, 2.1, h=1.0, out=0.24, door=(318, 1.9), seg=20)
    lo = PC.ring(b, 2.1, ZJ, r1=rt(ZJ), mat="masonry", col="warm", seam=110, foot=False, seg=20)
    lo.cell = 3.0
    PC.foot_disc(b, 2.1, ZE)
    P.door(lo, 318, w=0.85, h=1.95, arch=0.42, col="navy", z=0.45, steps=2)
    P.window(lo, 268, 2.6, w=0.55, h=1.5, arch=0.27, bars=(1, 3))
    P.window(lo, 222, 5.3, w=0.55, h=1.5, arch=0.27, bars=(1, 3))
    P.window(lo, 318, 5.3, w=0.55, h=1.5, arch=0.27, bars=(1, 3))
    P.window(lo, 268, 8.2, w=0.55, h=1.5, arch=0.27, bars=(1, 3))
    P.window(lo, 2, 8.2, w=0.55, h=1.5, arch=0.27, bars=(1, 3))
    P.stones(lo, n=40, z0=1.2, z1=ZJ - 0.4, u1=lo.w, size=(0.3, 0.6))
    P.ivy(lo, 236, 0.5, w=2.4, h=4.6, n=11, lod=2)
    P.ring_band(b, rt(ZJ) - 0.02, ZJ - 0.12, h=0.24, out=0.11, seg=20)
    up = PC.ring(b, rt(ZJ), ZE - ZJ, r1=rt(ZE), mat="ashlar", col="sand", z=ZJ, seam=150, foot=False, seg=20)
    P.door(up, 0, w=0.9, h=2.05, arch=0.45, col="navy", z=ZB - ZJ + 0.03, frame="stone")
    P.lantern(up, 24, ZB - ZJ + 1.8)
    for deg in (60, 120, 180, 240, 300):                # the reading room: light from every side
        P.window(up, deg, ZB - ZJ + 0.55, w=0.75, h=2.0, arch=0.37, bars=(1, 3))
    PC.corbels(b, rt(ZE) - 0.03, ZE, n=16, out=0.28, drop=0.4, w=0.2, steps=2, lod=2)
    b.cone_roof(rt(ZE), 5.7, mat="slate", z=ZE, seg=20, eave=0.42, flare=0.45, course=0.64, finial=False)
    PC.vane(b, 0, 0, ZE + 5.6, h=1.7, shape="quill", size=1.2)
    P.dormer(b, *PC.polar(1.5, 300)[:2], ZE + 1.25, w=0.8, h=0.8, depth=1.1, face=300, roof="slate", col="sand")
    balcony(b, up)


def balcony(b, up):
    """The balcony: a half-round of flagstone on a moulded stone corbel, iron rail, open at the front."""
    hw, dp = 1.85, 1.9
    with up.on(0, ZB - ZJ):
        ell = lambda th, k=1.0: (hw * k * math.cos(rad(th)), dp * k * math.sin(rad(th)))
        outline = [(-hw, 0.3), (-hw, 0.0)] + [ell(th) for th in range(195, 346, 15)] + [(hw, 0.0), (hw, 0.3)]
        b.prism(outline, 0.2, "flagstone", col="sand", z=-0.2, bottom=True, cap="flagstone")
        PC.lathe(b, [(0.2, -2.1), (0.55, -1.75), (0.55, -1.58), (1.05, -1.0), (1.05, -0.84), (1.72, -0.24), (1.72, -0.2)], "ashlar", col="stone", seg=12, a0=-96, a1=96)
        with b.detail(1):
            b.blob(0.24, 0.24, 0.26, mat="ashlar", col="stone", z=-2.2, seg=6, rings=4, rough=0.0)
        left = [(-hw + 0.08, 0.02, 0)] + [(ell(th, 0.955)[0], ell(th, 0.955)[1], 0) for th in range(195, 246, 10)]
        right = [(ell(th, 0.955)[0], ell(th, 0.955)[1], 0) for th in range(295, 346, 10)] + [(hw - 0.08, 0.02, 0)]
        for pts in (left, right):
            P.railing(b, pts, h=1.0, style="iron", posts_at=3.0)
            with b.detail(2):
                for p in pts:
                    b.blob(0.055, 0.055, 0.055, mat="metal", col="brass", x=p[0], y=p[1], z=1.09, seg=5, rings=2, rough=0.0)
        with b.at(0, -0.92):
            P.landing_mark(b, 0.72)
        b.pad(0, -0.92, 0.0, radius=0.78, face=0, name="Library balcony")
        P.crate(b, -1.3, -0.42, 0, s=0.4, rz=14)       # the returns box


def court(b):
    """The forecourt under the tower: a low wall, a lamp, a seat for readers waiting for the door to open."""
    PC.garden_wall(b, (-4.84, 0.1), (-2.2, 0.1), h=0.75, t=0.3, coping="slab", mat="ashlar", col="sand")
    PC.garden_wall(b, (-4.84, 2.2), (-4.84, 0.1), h=0.75, t=0.3, coping="slab", mat="ashlar", col="sand")
    PC.lamp_post(b, -1.95, 0.3, 0, h=2.7)
    P.bench(b, -4.2, 1.2, rz=90, w=1.4)
    PC.cat(b, -4.15, 0.75, 0.48, rz=70, col="#d9a05a")
    P.planter(b, -3.2, 0.62, w=1.2)
    P.planter(b, 3.95, 0.05, w=0.6, bush=True)
    P.planter(b, -0.95, 0.05, w=0.6, bush=True)
