# Little Creaker: the old post mill of the east meadow; the whole buck is pushed round on its post by the tail pole to face the wind, and it complains at every turn.
# Massing: a tall tarred weatherboard box with a round boat-back roof, balanced on a single oak post over a trestle of crossed beams on four brick
#          piers; four lattice sails on the breast, a ladder and a long tail pole with a wheel behind.
# Materials: tarred boards with ivory corner boards and sail frames, grey shingles, oak trestle, brick piers; accent red.
from kit import *
import parts as P
import parts_k as PK
import parts_f as F

META = {"name": "Little Creaker", "kind": "windmill", "lot": (6.0, 6.0), "notes": "sails sweep 4.6 m about a hub 5.8 m up, over the front of the lot"}

CX, CY = 0.0, 3.05
BZ = 2.5                      # underside of the buck
BW, BD, BH = 2.5, 3.4, 4.3
TAR = "#93826f"


def build(b):
    # ---- the trestle: brick piers, crosstrees, quarter bars, the main post
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        px, py = CX + sx * 1.5, CY + sy * 1.5
        b.box(0.66, 0.66, 0.72, "brick", x=px, y=py, cap="ashlar", capcol="stone")
        b.box(0.66, 0.66, 3.0, "brick", col=shade("white", 0.85), x=px, y=py, z=-3.0, top=False)
        b.beam((CX + sx * 1.62, CY + sy * 1.62, 1.12), (CX + sx * 0.2, CY + sy * 0.2, BZ - 0.2), w=0.24, mat="timber", col="darkoak", lod=0)
    b.beam((CX - 1.8, CY - 1.8, 0.88), (CX + 1.8, CY + 1.8, 0.88), w=0.3, h=0.32, mat="timber", col="darkoak", lod=0, up=(0, 0, 1))
    b.beam((CX - 1.8, CY + 1.8, 0.9), (CX + 1.8, CY - 1.8, 0.9), w=0.3, h=0.32, mat="timber", col="darkoak", lod=0, up=(0, 0, 1))
    b.beam((CX, CY, 0.74), (CX, CY, BZ + 0.3), w=0.56, mat="timber", col="darkoak", lod=0)
    b.footprint(CX - 1.85, CY - 1.85, CX + 1.85, CY + 1.85, 1.0)

    # ---- the buck
    bd = b.body(BW, BD, BH, mat="planks", col=TAR, x=CX, y=CY, z=BZ, floor="planks", foot=False)
    P.door(bd.back, BW / 2 - 0.5, w=0.78, h=1.85, col="red", frame="timber", z=0.05, porch="flat")
    P.window(bd.left, 1.2, 1.1, w=0.5, h=0.6, lintel="timber")
    P.window(bd.left, 2.3, 2.9, w=0.5, h=0.6, lintel="timber", shutters="red")
    P.window(bd.right, 1.2, 2.9, w=0.5, h=0.6, lintel="timber", shutters="red")
    P.window(bd.right, 2.3, 1.1, w=0.5, h=0.6, lintel="timber")
    P.window(bd.front, BW / 2, 0.9, w=0.46, h=0.5, lintel="timber")
    P.band(bd, 0.0, h=0.2, out=0.05, mat="timber", col="darkoak")
    with b.detail(1):
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.beam((CX + sx * (BW / 2 + 0.01), CY + sy * (BD / 2 + 0.01), BZ + 0.2), (CX + sx * (BW / 2 + 0.01), CY + sy * (BD / 2 + 0.01), BZ + BH), w=0.14, mat="planks", col="ivory", caps=False)
    sec = [(0.0, 0.0), (0.36, 0.64), (0.82, 1.08), (BW / 2, 1.28)]
    rise = bd.gable(ridge="y", section=sec, mat="shingle", eave=0.14, verge=0.22, course=0.3, barge=False, thick=0.1)
    P.weathervane(b, CX, CY + 0.9, BZ + BH + rise - 0.05, h=1.0)

    # ---- the sails on the breast
    hy, hz = CY - BD / 2 - 0.5, BZ + 3.3
    with b.at(CX, hy, hz, rx=-5.0):
        with b.spin(speed=0.1):
            with b.at(ry=31.0):
                F.sails(b, n=4, length=4.5, width=1.1, lead=0.22, inner=0.85, bars=0.36, stock=0.15, hub=0.4, reef=0.32)
            b.tube((0, 0.15, 0), (0, 0.75, 0), r=0.16, mat="timber", col="darkoak", lod=0, n=7)

    # ---- behind: the ladder, the tail pole and its wheel
    with b.at(CX + 0.5, CY + BD / 2 + 1.06, 0.0, rz=180):
        P.stairs(b, w=0.8, rise=0.25, run=0.106, n=10, solid=False, rail="balusters")
    b.beam((CX - 0.4, CY + BD / 2 - 0.2, BZ + 0.2), (CX - 0.4, 5.52, 0.55), w=0.2, h=0.22, mat="timber", col="darkoak", lod=0)
    with b.at(CX - 0.4, 5.44, 0.36):
        F.wheel(b, r=0.36, w=0.08, spokes=6)

    # ---- under and around: sacks for the carter, a hand cart, the meadow
    PK.handcart(b, 2.0, 1.5, 0.0, rz=-25, load="sacks")
    P.sack(b, -0.5, 4.3, 0.0, r=0.3)
    P.sack(b, -0.9, 4.0, 0.0, r=0.27)
    F.cat(b, 1.64, 4.69, 1.05, rz=200, col="#3a3632")
    for (x, y) in ((-2.2, 1.2), (-2.35, 4.9), (2.3, 4.8), (-0.3, 0.9), (2.5, 2.9), (-2.5, 3.0)):
        F.flowers(b, x, y, 0.0, n=5, spread=0.32)
    F.spire_flower(b, -2.0, 1.55, 0.0, h=1.1, col="#e8497a")
    F.spire_flower(b, 2.1, 4.45, 0.0, h=1.3, col="#b08ae6")
