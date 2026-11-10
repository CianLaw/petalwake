# Thrushes: the long thatched farmhouse of the west meadow; three sleepy eyebrow windows, a porch deep enough to sit out the rain in, hollyhocks to the eaves.
# Massing: one long low range under a thick sagging thatch with three eyebrow dormers, a thatched open porch on oak posts, a stone chimney breast up
#          the left gable and a brick stack on the ridge, a lean-to dairy on the right end; a picket fence round the front garden.
# Materials: cream lime-wash over rubble (showing at the foot), golden thatch with a scalloped ridge, oak; accent green.
from kit import *
import parts as P
import parts_c as PC
import parts_l as PL
import parts_m as PM
import parts_f as F

META = {"name": "Thrushes Farm", "kind": "farm", "lot": (13.0, 7.0)}

HX0, HX1 = -5.7, 3.7          # the house
FY, BY = 1.55, 6.35
WH = 2.6
PX = -1.6                     # the porch


def porch(b):
    dark = shade(F.STRAW, 0.6)
    b.gable_roof(2.6, 1.88, mat="thatch", col=F.STRAW, x=PX, y=0.42 + 0.94, z=2.2, ridge="y", section=F._cushion(1.3, 46, 0.06), eave=0.28, verge=0.2,
                 thick=0.22, course=0.42, lip=0.06, soffit="thatch", soffit_col=dark, barge=False, ridge_roll=False)
    with b.at(PX, 0.8, 2.2 + 1.3 * math.tan(rad(46)), rz=90):
        F.thatch_ridge(b, 1.3, 34, drop=0.42, col=shade(F.STRAW, 0.84), step=0.36)
    for sx in (-1, 1):
        x = PX + sx * 1.15
        b.beam((x, 0.55, -0.6), (x, 0.55, 2.2), w=0.17, mat="timber", col="darkoak", lod=0)
        with b.detail(1):
            b.beam((x, 0.45, 2.12), (x, FY, 2.12), w=0.15, h=0.16, mat="timber", col="darkoak", up=(0, 0, 1))
            b.beam((x, 0.55, 1.45), (x - sx * 0.6, 0.55, 2.08), w=0.1, mat="timber", col="darkoak", caps=False)
            b.box(0.07, 1.0, 0.9, "planks", col="greyoak", x=x, y=1.05, bottom=False)
    with b.detail(1):
        b.beam((PX - 1.25, 0.55, 2.12), (PX + 1.25, 0.55, 2.12), w=0.15, h=0.16, mat="timber", col="darkoak", up=(0, 0, 1))
        b.beam((PX, 0.55, 2.2), (PX, 0.55, 3.3), w=0.12, mat="timber", col="darkoak")
        b.box(2.5, 1.25, 0.1, "flagstone", col="sand", x=PX, y=0.98, z=0.0)
        b.box(2.5, 1.25, 1.5, "masonry", col="warm", x=PX, y=0.98, z=-1.5, top=False)
    P.bench(b, PX - 0.88, 1.05, 0.1, w=0.95, rz=90)
    P.bench(b, PX + 0.88, 1.05, 0.1, w=0.95, rz=-90)
    P.lantern_at(b, PX, 0.55, 1.95, arm=0.0)
    PC.climber(b, (PX - 1.2, 0.5, 0.1), (PX - 1.2, 0.5, 2.3), bloom=["#e8497a", "#f2a0bd"])
    F.cat(b, PX + 0.85, 1.0, 0.56, rz=120, pose="curl")


def build(b):
    w, cx, d, cy = HX1 - HX0, (HX0 + HX1) / 2, BY - FY, (FY + BY) / 2
    bd = b.body(w, d, WH, mat="plaster", col="cream", x=cx, y=cy)
    P.plinth(bd, h=0.55)
    U = lambda x: x - HX0
    P.door(bd.front, U(PX), w=0.95, h=1.95, col="green", frame="timber", z=0.12)
    for x, box in ((-4.4, True), (0.75, False), (2.75, True)):
        P.window(bd.front, U(x), 0.95, w=0.8, h=1.0, shutters="green", box=box, lintel="timber")
    F.half_door(bd.back, HX1 + 0.5, w=1.0, h=1.95, z=0.12, col="green")
    P.window(bd.back, HX1 + 4.2, 0.95, w=0.8, h=1.0, lintel="timber")
    P.window(bd.back, HX1 - 2.2, 0.95, w=0.8, h=1.0, shutters="green", lintel="timber")
    P.window(bd.left, BY - 2.45, 0.95, w=0.6, h=0.9, lintel="timber")
    P.exposed(bd.front, "base", n=9)
    P.exposed(bd.back, "both", n=8)
    rise = F.thatch_gable(bd, pitch=50, ridge="x", sag=0.14, eave=0.46, verge=0.38)
    ep = F.eave_pitch(50)
    for x, ww in ((-4.4, 2.1), (0.75, 1.9), (2.75, 1.9)):
        with b.at(x, FY, WH):
            F.eyebrow(b, w=ww, h=0.62, pitch=ep)
    porch(b)

    # ---- chimneys: a stone breast up the left gable, a brick stack on the ridge
    with b.at(HX0 - 0.02, cy, 0.0, rz=90):
        PM.stack(b, 0, 0, 0, h=WH + rise + 1.35, w=0.85, d=0.62, base=(1.6, 0.62, 2.6), mat="masonry", col="warm", pots=1)
    P.chimney(b, 1.6, cy + 0.25, WH + rise - 1.3, 2.4, w=0.7, d=0.55, mat="brick", pots=2)

    # ---- the dairy: a thatched lean-to on the right end
    o = b.body(2.2, 3.6, 1.9, mat="plaster", col="cream", x=HX1 + 1.1, y=cy + 0.3)
    P.plinth(o, h=0.45)
    P.door(o.front, 1.1, w=0.8, h=1.75, col="green", frame="timber", z=0.1)
    P.window(o.right, 1.8, 0.8, w=0.6, h=0.7, lintel="timber")
    P.window(o.back, 1.1, 0.8, w=0.6, h=0.7, lintel="timber")
    F.pent_roof(o, 1.3, high="left", over=0.0, mat="thatch", col=F.STRAW, eave=0.38, verge=0.3, thick=0.24, course=0.45, lip=0.06,
                soffit="thatch", soffit_col=shade(F.STRAW, 0.6), barge=False)
    for i, (x, y) in enumerate(((4.3, 2.15), (4.62, 2.05), (5.45, 2.2))):
        F.churn(b, x, y, 0.0, s=1.0 if i else 1.15)

    # ---- the front garden: picket fence and gate, hollyhocks and sunflowers
    F.picket(b, [(-6.3, 1.45), (-6.3, 0.18), (-2.3, 0.18)], col="ivory")
    F.picket(b, [(-0.9, 0.18), (6.3, 0.18), (6.3, 2.35)], col="ivory")
    with b.at(-2.3, 0.18, 0.0, rz=42):
        F.gate(b, w=1.38, h=0.9, col="ivory", kind="picket")
    for x, c_ in ((-5.3, "#e8497a"), (-3.55, "#f2a0bd"), (-0.2, "#b08ae6"), (1.75, "#e8497a"), (3.6, "#f4f1e4")):
        F.spire_flower(b, x, 1.3, 0.0, h=b.r(1.2, 1.7), col=c_)
        F.spire_flower(b, x + 0.3, 1.15, 0.0, h=b.r(0.9, 1.3), col=c_)
    F.sunflower(b, 4.9, 1.2, 0.0, h=1.7, face=350)
    F.sunflower(b, 5.4, 1.0, 0.0, h=1.5, face=20)
    F.meadow(b, -5.8, 0.6, -3.2, 1.1, n=5, spread=(0.25, 0.4))
    F.meadow(b, -0.3, 0.6, 5.8, 1.1, n=8, spread=(0.25, 0.4))
    P.tree(b, 5.3, 1.55, 0.0, h=1.7, crown=0.7, kind="bush")

    # ---- the back: logs under the eaves, the water butt, a rake
    PL.logs(b, 1.8, BY + 0.05, 0.0, w=1.8, h=0.85, d=0.42, rz=180)
    P.barrel(b, -3.3, BY + 0.28, 0.0, r=0.24, h=0.9)
    F.tool(b, -1.9, BY + 0.14, 0.0, kind="rake", rz=180, lean=0.08)
    F.meadow(b, -5.4, BY + 0.2, 5.6, BY + 0.26, n=5, spread=(0.2, 0.28))
