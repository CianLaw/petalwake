# the gardener's wheelbarrow: one wheel, a boarded tray of earth with a spade and a pot of seedlings
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Wheelbarrow", "kind": "prop", "group": "green", "clear": 1.0, "wobble": 0.015}


def build(b):
    with b.detail(1):
        with b.at(0.62, 0, 0.24):
            PP.wheel(b, r=0.24, w=0.06, spokes=6, col="darkoak")
        for sy in (-1, 1):
            b.beam((0.62, sy * 0.07, 0.24), (-0.95, sy * 0.32, 0.56), w=0.05, mat="planks", col="darkoak")      # frame and handle in one
            b.beam((-0.38, sy * 0.24, 0.42), (-0.42, sy * 0.27, 0.0), w=0.045, mat="planks", col="darkoak")
        b.box(0.8, 0.5, 0.05, "planks", col="#b9a183", x=-0.05, z=0.44, bottom=True)
        for sy in (-1, 1):
            PP.board(b, (-0.45, sy * 0.27, 0.6), (0.38, sy * 0.24, 0.6), w=0.28, t=0.025, col="#c9b08a", up=(0, 1, 0.25 * sy))
        PP.board(b, (0.37, -0.25, 0.6), (0.37, 0.25, 0.6), w=0.28, t=0.025, col="#c9b08a", up=(1, 0, 0))
        PP.board(b, (-0.45, -0.28, 0.58), (-0.45, 0.28, 0.58), w=0.22, t=0.025, col="#c9b08a", up=(1, 0, 0))
        b.blob(0.38, 0.24, 0.14, mat="cobble", col=PP.SOIL, x=-0.05, z=0.62, seg=7, rings=2, rough=0.12, bottom=False)
    with b.detail(2):
        b.beam((0.1, 0.05, 0.62), (-0.55, -0.1, 1.2), w=0.03, mat="planks", col="#c9a57a")                    # the spade
        b.box(0.16, 0.02, 0.2, "metal", col="lead", x=0.14, y=0.06, z=0.5)
        PP.pot_plant(b, -0.25, 0.1, 0.66, r=0.1, h=0.14, flowers=["#f4f1e4"], n=3)
        PP.pot_plant(b, -0.9, -0.55, 0, r=0.13, h=0.2, flowers=["#e8497a", "#f5c842"])
        PP.tuft(b, 0.5, 0.4, 0, r=0.1, h=0.2)
