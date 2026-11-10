# Humble Cottage: the beekeeper's, where the whole meadow ends up in jars; a row of straw skeps hums on the shelf along the warm wall.
# Massing: a small square cottage under a tall round-shouldered thatch like a tea cosy, one eyebrow over the door, a stone chimney, and
#          along the left wall a long hive shelf under its own little pent roof, facing a garden of bee flowers.
# Materials: honey-butter lime-wash on rubble, golden thatch, oak, straw skeps; accent plum.
from kit import *
import parts as P
import parts_m as PM
import parts_f as F

META = {"name": "Humble Cottage", "kind": "house", "lot": (6.0, 7.0)}

X0, X1, Y0, Y1 = -1.6, 2.3, 1.5, 5.5
WH = 2.5


def build(b):
    w, d, cx, cy = X1 - X0, Y1 - Y0, (X0 + X1) / 2, (Y0 + Y1) / 2
    bd = b.body(w, d, WH, mat="plaster", col="butter", x=cx, y=cy)
    P.plinth(bd, h=0.5)
    P.door(bd.front, 1.5, w=0.9, h=1.9, col="plum", frame="timber", z=0.12, lamp=True)
    P.window(bd.front, 3.15, 0.95, w=0.8, h=1.0, shutters="plum", box=True, lintel="timber")
    P.window(bd.right, 1.3, 0.95, w=0.8, h=1.0, shutters="plum", lintel="timber")
    P.window(bd.right, 2.9, 0.95, w=0.8, h=1.0, lintel="timber")
    P.window(bd.back, 1.2, 0.95, w=0.8, h=1.0, shutters="plum", lintel="timber")
    P.door(bd.back, 3.0, w=0.85, h=1.85, col="plum", frame="timber", z=0.12)
    P.exposed(bd.front, "corners", n=8)
    P.exposed(bd.right, "base", n=7)
    P.sign(bd.front, 0.45, 2.25, emblem="flower", col="mustard", out=0.7)
    lf = F.hip_lift(54, eave=0.48, corner=0.45, shoulder=0.85)
    rise = F.soft_hip(b, w, d, pitch=54, x=cx, y=cy, z=WH, eave=0.48, corner=0.45, shoulder=0.85, cap=0.55, lift=lf)
    with b.at(X0 + 1.5, Y0, WH + lf):
        F.eyebrow(b, w=1.8, h=0.6, pitch=F.eave_pitch(54), wall_col="butter")
    PM.stack(b, X1 - 0.35, cy + 0.2, WH - 0.2, rise + 1.5, w=0.75, d=0.6, mat="masonry", col="warm", pots=1)

    # ---- the hive shelf along the left wall, under its own pent roof
    sx0, sx1 = X0 - 0.72, X0 - 0.06
    sy0, sy1 = Y0 + 0.25, Y1 - 0.25
    with b.detail(1):
        b.box(sx1 - sx0, sy1 - sy0, 0.07, "planks", col="greyoak", x=(sx0 + sx1) / 2, y=(sy0 + sy1) / 2, z=0.62, bottom=True)
        for y in (sy0 + 0.15, (sy0 + sy1) / 2, sy1 - 0.15):
            b.beam((sx0 + 0.1, y, -0.5), (sx0 + 0.1, y, 0.62), w=0.1, mat="timber", col="darkoak")
            b.beam((sx0 + 0.1, y, 0.56), (X0, y, 0.56), w=0.09, mat="timber", col="darkoak", caps=False)
            b.beam((X0, y, 1.62), (sx0 - 0.1, y, 1.42), w=0.08, mat="timber", col="darkoak", caps=False)
            b.beam((X0, y, 1.15), (sx0 + 0.15, y, 1.44), w=0.06, mat="timber", col="darkoak", caps=False)
    with b.at(X0, (sy0 + sy1) / 2, 1.72, rz=-90):
        b.gable_roof(sy1 - sy0 + 0.3, 0.95, 16, mat="shingle", ridge="x", half=True, x=0.0, y=0.0, z=0.0, eave=0.1, verge=0.06, course=0.3, thick=0.06, barge=False, lod=1)
    n = 6
    for i in range(n):
        y = sy0 + 0.3 + (sy1 - sy0 - 0.6) * i / (n - 1)
        F.hive(b, (sx0 + sx1) / 2, y, 0.69, r=0.25, h=0.46 + 0.05 * (i % 2), face=270, hackle=i in (1, 4), lod=1)
    for _ in range(14):                               # bees
        F.bloom(b, sx0 - b.r(0.0, 0.42), b.r(sy0, sy1), b.r(0.75, 1.6), r=0.022, col="#f5c842", wind=1.0)

    # ---- the bee garden: lavender, foxgloves, sunflowers, a low fence; honey for sale by the door
    for i in range(7):
        F.spire_flower(b, -2.62 + 0.1 * (i % 2), Y0 + 0.5 + 0.52 * i, 0.0, h=0.62, col="#b08ae6", n=5)
    for (x, y, c_) in ((-2.6, 0.75, "#e8497a"), (-1.9, 0.6, "#f2a0bd"), (-2.3, 5.75, "#e8497a"), (-1.2, 6.05, "#f4f1e4")):
        F.spire_flower(b, x, y, 0.0, h=b.r(1.1, 1.5), col=c_)
    for (x, y, f_) in ((-0.3, 6.1, 200), (0.5, 6.2, 170), (1.4, 6.05, 190)):
        F.sunflower(b, x, y, 0.0, h=b.r(1.5, 1.9), face=f_)
    F.meadow(b, -2.6, 1.3, -2.5, 5.4, n=5, spread=(0.18, 0.24), cols=["#f5c842", "#f4f1e4", "#b08ae6"])
    F.picket(b, [(-2.85, 6.4), (-2.85, 0.2), (-0.6, 0.2)], h=0.8, col="ivory")
    with b.detail(2):
        b.box(0.9, 0.42, 0.05, "planks", col="greyoak", x=1.75, y=1.15, z=0.72, bottom=True)
        for sx in (-0.38, 0.38):
            b.beam((1.75 + sx, 1.0, 0.0), (1.75 + sx, 1.3, 0.72), w=0.05, mat="planks", col="greyoak", caps=False)
            b.beam((1.75 + sx, 1.3, 0.0), (1.75 + sx, 1.0, 0.72), w=0.05, mat="planks", col="greyoak", caps=False)
        for i, c_ in enumerate(("#e0a030", "#f0c050", "#d98a2c", "#e8b040")):
            with b.at(1.42 + 0.22 * i, 1.15 + 0.05 * (i % 2), 0.77):
                b.revolve([(0.06, 0.0), (0.07, 0.11), (0.05, 0.13), (0.055, 0.16), (0.0, 0.165)], "paint", col=F._paint(c_), seg=6)
    P.barrel(b, X1 + 0.02, Y1 + 0.3, 0.0, r=0.26, h=0.85)
    F.tool(b, 2.2, Y1 + 0.12, 0.0, kind="spade", rz=180, lean=0.06, h=1.15)
    F.meadow(b, 0.0, Y1 + 0.45, 2.4, Y1 + 0.55, n=3, spread=(0.2, 0.28))
