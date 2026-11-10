# Heron's Perch: the fisher's hut on tall stilts at the lagoon's edge; old Tam built a crow's nest on the roof from a wrecked lugger's mast to watch for the shoals.
# Massing: a boarded hut on a deck 3 m up on six leaning piles, a veranda in front and a walkway down one side, the mast coming up through the
#          shingle roof to a round railed crow's nest (the landing), a pennant above it, a skiff slung under the deck.
# Materials: silvered boards and piles, grey shingles, tarred rope and nets; accent teal.
from kit import *
import parts as P
import parts_h as PH
import parts_f as F

META = {"name": "Heron's Perch", "kind": "hut", "lot": (4.0, 5.0)}

DZ = 3.0                 # the deck
MX, MY = 0.15, 3.0      # the mast
NEST = 7.5               # the crow's nest floor
BOARD = "#cfc6b6"
PILE = "#a89c8c"


def build(b):
    # ---- piles and braces (they run on down for a sloping shore), the deck
    piles = [(-1.6, 0.45), (1.6, 0.45), (-1.6, 2.5), (1.6, 2.5), (-1.6, 4.55), (1.6, 4.55)]
    for i, (x, y) in enumerate(piles):
        b.tube((x * 1.08, y + (0.12 if i < 2 else 0.0) * -1, -3.0), (x, y, DZ - 0.1), r=0.14, r1=0.11, mat="planks", col=PILE, lod=0, n=7)
    with b.detail(1):
        for sx in (-1.6, 1.6):
            for (ya, yb) in ((0.45, 2.5), (2.5, 4.55)):
                b.beam((sx * 1.03, ya, 0.5), (sx, yb, DZ - 0.5), w=0.09, mat="planks", col=PILE, caps=False)
                b.beam((sx * 1.03, yb, 0.5), (sx, ya, DZ - 0.5), w=0.09, mat="planks", col=PILE, caps=False)
        for y in (0.45, 4.55):
            b.beam((-1.65, y, 0.6), (1.6, y, DZ - 0.5), w=0.09, mat="planks", col=PILE, caps=False)
            b.beam((1.65, y, 0.6), (-1.6, y, DZ - 0.5), w=0.09, mat="planks", col=PILE, caps=False)
    F.deck(b, 3.6, 4.6, x=0, y=2.5, z=DZ, thick=0.1, col="greyoak", edge="#8a7f72", joists=0.9)
    b.footprint(-1.8, 0.2, 1.8, 4.8, DZ)

    # ---- the hut
    bd = b.body(2.6, 2.9, 2.15, mat="planks", col=BOARD, x=-0.25, y=3.0, z=DZ, foot=False)
    P.door(bd.front, 0.75, w=0.8, h=1.85, col="teal", frame="timber", lamp=True)
    P.window(bd.front, 1.95, 0.9, w=0.62, h=0.75, shutters="teal", lintel="timber")
    P.window(bd.right, 1.45, 0.9, w=0.62, h=0.75, shutters="teal", lintel="timber")
    P.window(bd.back, 1.35, 0.9, w=0.62, h=0.75, lintel="timber")
    P.window(bd.left, 1.45, 0.9, w=0.62, h=0.75, lintel="timber")
    rise = bd.gable(ridge="x", pitch=40, mat="shingle", eave=0.34, verge=0.24, sag=0.06)
    F.stovepipe(b, -1.0, 3.7, DZ + 2.15 + rise - 0.9, h=1.5)

    # ---- the mast and the crow's nest: where the rider lands, in through the gap that looks over the lagoon
    b.tube((MX, MY, DZ), (MX, MY, NEST - 0.1), r=0.14, r1=0.11, mat="planks", col="#b8a890", lod=0, n=7)
    with b.at(MX, MY, NEST):
        b.disc(1.2, "planks", col="greyoak", seg=12, lod=0)
        b.disc(1.2, "planks", col="#8a7f72", seg=12, z=-0.1, down=True, lod=0)
        b.revolve([(1.2, -0.1), (1.2, 0.0)], "planks", col="#8a7f72", seg=12, lod=0)
        with b.detail(1):
            for k in range(4):
                a = rad(90 * k + 45)
                b.beam((0.1 * math.sin(a), -0.1 * math.cos(a), -0.95), (1.0 * math.sin(a), -1.0 * math.cos(a), -0.12), w=0.1, mat="planks", col="#8a7f72")
            b.revolve([(0.2, -0.22), (0.24, -0.1), (0.0, -0.1)], "planks", col="#8a7f72", seg=7)
        P.railing(b, P.circle(1.12, 9, 0.0, 48, 312), h=0.82, style="solid", col="teal", mat="planks", post=0.09)
        P.flag(b, 0.0, 1.1, 0.0, pole=2.6, w=1.05, h=0.5, col="#2f8f8f")
        P.lantern_at(b, 0.0, 1.1, 1.35, arm=0.24)
    b.pad(MX, MY - 0.2, NEST, radius=0.75, face=0, name="Crow's nest")
    with b.at(MX, MY - 0.2, NEST):
        P.landing_mark(b, 0.66)
    PH.gull(b, MX + 1.12 * math.sin(rad(235)), MY - 1.12 * math.cos(rad(235)), NEST + 0.86, rz=250)
    F.ladder_to(b, (1.5, 2.1, DZ), (MX + 1.12, MY - 0.2, NEST + 0.9), w=0.36, col=PILE)

    # ---- veranda and walkway: rails, the ladder up from the shore, nets, pots, the day's catch
    P.railing(b, [(-0.72, 0.28, DZ), (1.72, 0.28, DZ), (1.72, 4.72, DZ)], h=0.9, style="balusters", col="greyoak", mat="planks")
    P.railing(b, [(-1.72, 1.75, DZ), (-1.72, 0.28, DZ)], h=0.9, style="balusters", col="greyoak", mat="planks")
    F.ladder_to(b, (-1.22, -0.6, -0.4), (-1.22, 0.22, DZ + 0.95), w=0.5, col=PILE)
    PH.net_drape(b, (-0.6, 0.2, DZ + 0.93), (1.7, 0.2, DZ + 0.93), drop=1.05)
    PH.net_drape(b, (1.8, 2.9, DZ + 0.93), (1.8, 4.6, DZ + 0.93), drop=1.2)
    PH.pots(b, 1.38, 1.15, DZ, rz=90, n=3)
    PH.buoy(b, 1.42, 4.35, DZ)
    PH.fish_rack(b, -1.25, 1.0, DZ, rz=90, w=1.25, h=1.7, rows=2, n=4)
    P.barrel(b, 0.55, 1.2, DZ, r=0.24, h=0.66)
    F.bucket(b, -0.2, 0.75, DZ)
    with b.detail(2):
        b.beam((0.9, 0.5, DZ + 0.9), (1.5, -0.9, DZ + 2.7), w=0.03, mat="planks", col="#c9b089", caps=False)       # the rod left over the rail
        F.rope(b, (1.5, -0.9, DZ + 2.7), (1.52, -0.92, DZ + 0.6), r=0.008)

    # ---- the skiff slung under the deck
    with b.at(0.0, 2.1, 1.25, rz=90):
        PH.hull(b, L=3.1, beam=1.2, depth=0.5, col="!#2f8f8f", trim="!#f2ead8")
    with b.detail(2):
        for (x, y) in ((-0.42, 1.6), (0.42, 1.6), (-0.42, 3.9), (0.42, 3.9)):
            F.rope(b, (x, y, DZ - 0.2), (x * 0.9, y, 1.72), r=0.014)
