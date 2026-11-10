# Greystones: the square stone farmhouse behind its walled kitchen garden; cabbages in rows, beans on canes, and a scarecrow in the farmer's old hat.
# Massing: a two-storey stone block under a slate roof with a stack at each gable, a lean-to scullery on the right end, and in front a garden
#          enclosed by a rubble wall with gate piers, a flagged path to the porch.
# Materials: grey rubble with ashlar quoins and string course, blue-grey slate, a white picket gate; accent blue.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_f as F

META = {"name": "Greystones", "kind": "farm", "lot": (10.0, 9.0)}

HX0, HX1, HY0, HY1 = -4.55, 2.45, 3.55, 8.5
G, WALL = 2.75, 5.35


def scarecrow(b, x, y):
    with b.at(x, y, 0.0, rz=-20):
        with b.detail(2):
            b.beam((0, 0, -0.3), (0.03, 0, 1.75), w=0.06, mat="planks", col="#c9b089")
            b.beam((-0.75, 0, 1.3), (0.75, 0, 1.32), w=0.05, mat="planks", col="#c9b089")
            b.blob(0.16, 0.15, 0.18, mat="cloth", col="#d9c9a3", z=1.72, seg=6, rings=3, rough=0.1)
            b.revolve([(0.3, 1.84), (0.17, 1.86), (0.14, 2.02), (0.0, 2.06)], "cloth", col="#6b5a45", seg=7)
            b.disc(0.3, "cloth", col="#5a4a3a", seg=7, z=1.84, down=True)
            for sgn in (-1, 1):
                q = [(-0.68, sgn * 0.02, 0.7), (0.68, sgn * 0.02, 0.7), (0.7, sgn * 0.02, 1.36), (-0.7, sgn * 0.02, 1.36)]
                b.face(q if sgn < 0 else list(reversed(q)), "cloth", col="#7a4672", wind=(0.5, 0.5, 0.0, 0.0) if sgn < 0 else (0.0, 0.0, 0.5, 0.5))


def build(b):
    w, d, cx, cy = HX1 - HX0, HY1 - HY0, (HX0 + HX1) / 2, (HY0 + HY1) / 2
    bd = b.body(w, d, WALL, mat="masonry", col="grey", x=cx, y=cy)
    P.plinth(bd, h=0.5, out=0.08, col="dark")
    P.quoins(bd, z0=0.5)
    P.band(bd, G, h=0.16)
    cols = (1.3, 3.5, 5.7)
    P.door(bd.front, cols[1], w=1.0, h=2.1, col="blue", frame="stone", z=0.2, steps=1, porch="gable", lamp=True)
    P.window(bd.front, cols[0], 1.05, w=0.9, h=1.3, shutters="blue", box=True)
    P.window(bd.front, cols[2], 1.05, w=0.9, h=1.3, shutters="blue")
    for u in cols:
        P.window(bd.front, u, G + 0.85, w=0.85, h=1.2, shutters="blue" if u != cols[1] else None)
        P.window(bd.back, u, G + 0.85, w=0.85, h=1.2)
    P.window(bd.back, cols[0], 1.05, w=0.9, h=1.3)
    P.window(bd.back, cols[2], 1.05, w=0.9, h=1.3)
    P.door(bd.back, cols[1], w=0.9, h=2.0, col="blue", frame="stone", z=0.2, steps=1)
    P.window(bd.left, d / 2, 1.05, w=0.85, h=1.3)
    P.window(bd.left, d / 2, G + 0.85, w=0.85, h=1.2)
    P.window(bd.right, 1.0, G + 0.85, w=0.75, h=1.2)
    rise = bd.gable(ridge="x", pitch=42, mat="slate", eave=0.27, verge=0.27, sag=0.05)
    PC.stack(b, HX0 + 0.5, cy, WALL + rise - 1.0, 2.3, w=0.75, d=0.6, mat="masonry", col="grey", flues=2)
    PC.stack(b, HX1 - 0.5, cy, WALL + rise - 1.0, 2.1, w=0.7, d=0.6, mat="masonry", col="grey", flues=1)
    P.ivy(bd.left, 0.9, 0.5, w=1.6, h=3.6, n=9)

    # ---- the scullery: a lean-to on the right end, its door toward the garden
    lt = PH.leanto(b, HX1, 6.6, w=3.4, d=2.0, h=2.0, rz=90, pitch=26, mat="masonry", col="grey", roof="slate")
    P.door(lt.left, 1.0, w=0.8, h=1.8, col="blue", frame="timber", z=0.08)
    P.window(lt.front, 1.7, 0.9, w=0.7, h=0.8)
    P.barrel(b, 4.05, 4.55, 0.0, r=0.3, h=0.95)

    # ---- the walled kitchen garden
    PC.yard(b, -4.8, 4.8, HY0, h=1.2, y0=0.14, gate=(cx, 1.1), piers=1.55, gate_col="ivory")
    PC.garden_wall(b, (4.8, HY0), (4.8, 4.95), h=1.2)
    with b.detail(1):
        b.box(0.9, HY0 - 0.5, 0.05, "flagstone", col="sand", x=cx, y=(HY0 + 0.5) / 2 - 0.05)
        for (x0, x1) in ((-4.35, cx - 0.7), (cx + 0.7, 3.2)):
            b.box(x1 - x0, 2.7, 0.05, "masonry", col="#6b5a48", x=(x0 + x1) / 2, y=1.95)
    F.veg_row(b, (-4.2, 0.95), (-1.95, 0.95), "cabbage")
    F.veg_row(b, (-4.2, 1.55), (-1.95, 1.55), "leek")
    F.veg_row(b, (-4.2, 2.15), (-1.95, 2.15), "cabbage")
    F.veg_row(b, (-4.2, 2.9), (-2.9, 2.9), "pumpkin")
    F.veg_row(b, (0.0, 1.0), (3.0, 1.0), "bean")
    F.veg_row(b, (-0.1, 1.9), (2.3, 1.9), "cabbage")
    F.veg_row(b, (-0.1, 2.6), (2.3, 2.6), "leek")
    scarecrow(b, -2.2, 2.85)
    F.fruit_tree(b, 3.45, 2.5, 0.0, h=3.0, crown=0.9, fruit="#d8402f")
    P.bench(b, -3.0, HY0 - 0.32, 0.0, w=1.4)
    F.spire_flower(b, 0.2, HY0 - 0.3, 0.0, h=1.4, col="#e8497a")
    F.spire_flower(b, 1.9, HY0 - 0.28, 0.0, h=1.2, col="#b08ae6")
    F.flowers(b, 1.0, HY0 - 0.35, 0.0, n=5, spread=0.35)
    F.cat(b, 2.6, 0.3, 1.24, rz=30, col="#3a3632")
    F.bucket(b, -0.2, 3.1, 0.0)
