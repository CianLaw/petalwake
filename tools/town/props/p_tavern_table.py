# a tavern table set out of doors: trestle top and two benches, mugs and a jug, a loaf, a lantern for the evening
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Tavern table and benches", "kind": "prop", "group": "square", "clear": 1.6, "wobble": 0.015}


def build(b):
    with b.detail(1):
        PP.planking(b, -0.95, 0.95, -0.38, 0.38, 0.77, along="x", pw=0.19, t=0.045, col="#c9b08a")
        for sx in (-1, 1):
            b.beam((sx * 0.7, -0.34, 0), (sx * 0.62, 0.0, 0.73), w=0.06, mat="timber")
            b.beam((sx * 0.7, 0.34, 0), (sx * 0.62, 0.0, 0.73), w=0.06, mat="timber")
        b.beam((-0.62, 0, 0.36), (0.62, 0, 0.36), w=0.05, mat="timber")
        for sy in (-1, 1):                                    # the benches
            PP.board(b, (-0.9, sy * 0.72, 0.45), (0.9, sy * 0.72, 0.45), w=0.28, t=0.045, col="greyoak")
            for sx in (-1, 1):
                b.box(0.06, 0.26, 0.43, "planks", col="darkoak", x=sx * 0.7, y=sy * 0.72)
        with b.at(0.1, 0.05, 0.77):
            PP.lantern(b, s=0.17, h=0.28, sides=4, strength=0.6)
    with b.detail(2):
        for (x, y) in ((-0.6, -0.2), (-0.25, 0.22), (0.55, -0.18), (0.7, 0.2)):
            with b.at(x, y, 0.77):
                b.revolve([(0.045, 0.0), (0.055, 0.13), (0.045, 0.13), (0.04, 0.02)], "planks", col="#b9905e", seg=6)
                b.disc(0.045, "paint", col="#f4ecd0", seg=6, z=0.11)
        PP.jar(b, -0.2, -0.12, 0.77, s=0.85, kind="jug", col="#4f7fae")
        PP.jar(b, 0.38, 0.05, 0.77, s=1.0, kind="plate", col="#efe2c4")
        b.blob(0.11, 0.07, 0.05, mat="paint", col="#c98a4a", x=0.38, y=0.05, z=0.83, seg=6, rings=2, rough=0.08)
        PP.barrel(b, 1.35, -0.3, 0, r=0.24, h=0.5)
        PP.tuft(b, -1.1, 0.5, 0, r=0.1, h=0.2)
