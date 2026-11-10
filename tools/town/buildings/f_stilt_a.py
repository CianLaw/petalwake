# The Net Loft: Heron's Perch's little neighbour, where young Merrin mends the nets and dries them on the frame beside her door.
# Massing: one tarred room under a steep reed-thatch gable (door in the gable end) on a low deck on four piles, a tall net-drying frame along
#          one side, a ladder up from the shore.
# Materials: tarred boards, silvery reed thatch, bleached piles and poles, green-grey nets; accent orange.
from kit import *
import parts as P
import parts_h as PH
import parts_f as F

META = {"name": "The Net Loft", "kind": "hut", "lot": (4.0, 5.0)}

DZ = 2.2
PILE = "#a89c8c"
TAR = "#8f7f70"


def build(b):
    # ---- piles, braces, deck
    for (x, y) in ((-1.45, 0.6), (1.45, 0.6), (-1.45, 4.1), (1.45, 4.1)):
        b.tube((x * 1.1, y, -3.0), (x, y, DZ - 0.1), r=0.14, r1=0.11, mat="planks", col=PILE, lod=0, n=7)
    with b.detail(1):
        for sx in (-1.45, 1.45):
            b.beam((sx * 1.05, 0.6, 0.4), (sx, 4.1, DZ - 0.45), w=0.09, mat="planks", col=PILE, caps=False)
            b.beam((sx * 1.05, 4.1, 0.4), (sx, 0.6, DZ - 0.45), w=0.09, mat="planks", col=PILE, caps=False)
        for y in (0.6, 4.1):
            b.beam((-1.52, y, 0.5), (1.45, y, DZ - 0.45), w=0.09, mat="planks", col=PILE, caps=False)
    F.deck(b, 3.3, 4.0, x=0, y=2.35, z=DZ, thick=0.1, col="greyoak", edge="#8a7f72", joists=0.85)
    b.footprint(-1.65, 0.35, 1.65, 4.35, DZ)

    # ---- the hut: door in the gable end, reed thatch
    bd = b.body(2.3, 2.5, 1.85, mat="planks", col=TAR, x=-0.4, y=3.0, z=DZ, foot=False)
    P.door(bd.front, 1.1, w=0.75, h=1.7, col="orange", frame="timber", lamp=True)
    P.window(bd.right, 1.25, 0.8, w=0.56, h=0.66, shutters="orange", lintel="timber")
    P.window(bd.back, 1.15, 0.8, w=0.5, h=0.6, lintel="timber")
    P.window(bd.left, 1.25, 0.8, w=0.5, h=0.6, lintel="timber")
    rise = F.thatch_gable(bd, pitch=52, ridge="y", col=F.OLDSTRAW, eave=0.29, verge=0.3, thick=0.26, course=0.45)
    F.stovepipe(b, -1.0, 3.7, DZ + 1.85 + rise * 0.3, h=1.5)
    PH.floats(bd.front, 1.92, 1.4)

    # ---- the drying frame and its nets
    for y in (0.62, 4.08):
        b.tube((1.5, y, DZ), (1.52, y, DZ + 2.75), r=0.06, mat="planks", col=PILE, lod=1, n=6)
    with b.detail(1):
        b.beam((1.5, 0.5, DZ + 2.62), (1.5, 4.2, DZ + 2.62), w=0.07, mat="planks", col=PILE)
        b.beam((0.75, 2.2, DZ + 1.75), (1.5, 2.2, DZ + 2.6), w=0.06, mat="planks", col=PILE, caps=False)
    PH.net_drape(b, (1.5, 0.7, DZ + 2.58), (1.5, 2.3, DZ + 2.58), drop=1.9)
    PH.net_drape(b, (1.5, 2.45, DZ + 2.58), (1.5, 4.05, DZ + 2.58), drop=1.5, col=PH.NET_BROWN)

    # ---- the veranda: rail, ladder, the things of the trade
    P.railing(b, [(-1.57, 1.7, DZ), (-1.57, 0.43, DZ), (-0.45, 0.43, DZ)], h=0.85, style="cross", col="greyoak", mat="planks")
    F.ladder_to(b, (0.2, -0.5, -0.4), (0.2, 0.38, DZ + 0.9), w=0.5, col=PILE)
    PH.pots(b, -1.0, 1.05, DZ, rz=0, n=3)
    PH.oars(b, 0.84, 2.6, DZ, rz=90)
    PH.basket(b, 0.75, 1.25, DZ, r=0.26)
    PH.cat(b, -0.15, 0.75, DZ, rz=160)
    P.barrel(b, 1.05, 4.05, DZ, r=0.22, h=0.6)
