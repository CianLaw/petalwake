# a boat hauled out and turned keel-up on trestles for painting: paint pot and brush on a stool, oars leaning on it
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

META = {"name": "Upturned boat on trestles", "kind": "prop", "group": "harbour", "clear": 2.4, "length": 3.8, "axis": "x", "wobble": 0.012}


def build(b):
    H = PP.Hull(L=3.8, B=1.4, depth=0.54, draft=0.15, planks=5, stations=9, sheer_bow=0.2, sheer_stern=0.06)
    zt = 0.72
    base = zt + H.F + 0.06
    with b.detail(1):
        with b.at(0, 0, base, rx=180):
            H.build(b, cols=["#4f86b8", "#4f86b8", "#4f86b8", "#5a94c8", "ivory"], inner="#c9ab7e", gunwale="darkoak")
        for x in (-0.95, 0.95):                                 # the trestles
            b.beam((x, -0.85, zt - 0.05), (x, 0.85, zt - 0.05), w=0.09, h=0.1, mat="timber")
            for sy in (-1, 1):
                for dx in (-0.22, 0.22):
                    b.beam((x + dx, sy * 0.78, 0), (x, sy * 0.66, zt - 0.08), w=0.06, mat="timber")
    with b.detail(2):
        with b.at(0, 0, base, rx=180):
            H.thwart(b, -0.2, col="#b98f5e")
            H.thwart(b, 0.9, col="#b98f5e", w=0.2)
        b.box(0.34, 0.34, 0.04, "planks", col="greyoak", x=0.5, y=-1.25, z=0.4, bottom=True)        # a stool with the paint
        for (dx, dy) in ((-0.13, -0.13), (0.13, -0.13), (0.13, 0.13), (-0.13, 0.13)):
            b.beam((0.5 + dx * 1.2, -1.25 + dy * 1.2, 0), (0.5 + dx, -1.25 + dy, 0.4), w=0.035, mat="planks", col="greyoak", caps=False)
        with b.at(0.5, -1.25, 0.44):
            b.revolve([(0.085, 0.0), (0.095, 0.15), (0.085, 0.15), (0.08, 0.02)], "metal", col="lead", seg=7)
            b.disc(0.083, "paint", col="#4f86b8", seg=7, z=0.12)
            b.beam((0.02, 0.0, 0.12), (0.16, 0.06, 0.26), w=0.022, mat="planks", col="#c9a57a")
        PH.oars(b, -0.9, 0.86, 0, rz=180, n=2, L=2.5)
        PP.bucket(b, -0.6, -1.1, 0, r=0.14, h=0.24)
        PP.coil(b, 1.5, 0.9, 0, r=0.24, turns=2)
        for (x, y) in ((-1.4, -0.7), (1.3, -0.8), (0.2, 0.95)):
            PP.tuft(b, x, y, 0, r=0.11, h=0.2)
