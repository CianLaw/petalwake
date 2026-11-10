# the hay wagon home from the meadow: four wheels, flaring ladder sides, a towering load, the pitchfork left in it
import math
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Hay wagon", "kind": "prop", "group": "square", "clear": 3.4, "length": 5.0, "axis": "x", "wobble": 0.02}


def build(b):
    zb = 0.98
    with b.detail(1):
        PP.planking(b, -1.6, 1.6, -0.58, 0.58, zb, along="x", pw=0.24, t=0.05, col="#c9b08a")
        for sy in (-1, 1):
            b.beam((-1.6, sy * 0.5, zb - 0.12), (1.6, sy * 0.5, zb - 0.12), w=0.09, h=0.14, mat="timber")
            # the flaring hay ladders
            b.beam((-1.75, sy * 0.62, zb + 0.02), (1.75, sy * 0.62, zb + 0.02), w=0.06, mat="timber")
            b.beam((-1.9, sy * 1.02, zb + 0.78), (1.9, sy * 1.02, zb + 0.78), w=0.06, mat="timber")
            with b.at(1.12, sy * 0.78, 0.44):
                PP.wheel(b, r=0.44, w=0.07, spokes=8, col="darkoak")
            with b.at(-1.05, sy * 0.8, 0.58):
                PP.wheel(b, r=0.58, w=0.075, spokes=10, col="darkoak")
        b.beam((1.12, -0.82, 0.44), (1.12, 0.82, 0.44), w=0.09, mat="timber")
        b.beam((-1.05, -0.84, 0.58), (-1.05, 0.84, 0.58), w=0.09, mat="timber")
        b.beam((1.12, 0, 0.5), (1.12, 0, zb - 0.1), w=0.16, mat="timber")
        b.beam((-1.05, -0.4, 0.62), (-1.05, -0.4, zb - 0.1), w=0.1, mat="timber")
        b.beam((-1.05, 0.4, 0.62), (-1.05, 0.4, zb - 0.1), w=0.1, mat="timber")
        b.beam((1.2, 0, 0.5), (3.35, 0, 0.12), w=0.08, mat="timber")                                  # the pole, dropped
        b.beam((3.2, -0.45, 0.14), (3.2, 0.45, 0.14), w=0.06, mat="timber")
        # the load
        hay = PP.STRAW
        b.blob(1.85, 0.98, 0.95, mat="thatch", col=hay, x=0.0, y=0, z=zb + 0.62, seg=9, rings=4, rough=0.14, wind=0.12)
        b.blob(1.3, 0.8, 0.7, mat="thatch", col=shade(hay, 1.06), x=-0.2, y=0.05, z=zb + 1.25, seg=8, rings=4, rough=0.16, wind=0.2)
    with b.detail(2):
        for sy in (-1, 1):
            for i in range(9):
                x = -1.6 + 3.2 * i / 8
                b.beam((x, sy * 0.62, zb + 0.02), (x * 1.09, sy * 1.02, zb + 0.78), w=0.035, mat="planks", col="#c9a57a", caps=False)
        for sx in (-1, 1):                                    # end gates
            for y in (-0.5, 0.0, 0.5):
                b.beam((sx * 1.62, y, zb), (sx * 1.85, y * 1.5, zb + 1.0), w=0.04, mat="planks", col="#c9a57a", caps=False)
            b.beam((sx * 1.83, -0.8, zb + 0.9), (sx * 1.83, 0.8, zb + 0.9), w=0.04, mat="planks", col="#c9a57a")
        rng = b.rng
        for _ in range(12):                                   # wisps hanging over the rails
            x, sy = rng.uniform(-1.6, 1.6), rng.choice((-1, 1))
            PP.face2(b, [(x - 0.1, sy * 0.98, zb + 0.8), (x + 0.1, sy * 0.98, zb + 0.8), (x + rng.uniform(-0.06, 0.06), sy * 1.1, zb + 0.8 - rng.uniform(0.25, 0.5))], "thatch", col=PP.STRAW, wind=(0.1, 0.1, 0.6))
        b.beam((0.5, 0.2, zb + 1.5), (0.95, 0.5, zb + 2.5), w=0.035, mat="planks", col="#c9a57a")       # pitchfork
        for d in (-0.07, 0.0, 0.07):
            b.beam((0.5 + d, 0.2 - d, zb + 1.5), (0.42 + d, 0.14 - d, zb + 1.28), w=0.015, mat="metal", col="iron", caps=False)
        for (x, y) in ((2.2, 0.7), (-2.2, -0.9), (0.3, 1.35)):
            b.blob(0.3, 0.24, 0.07, mat="thatch", col=PP.STRAW, x=x, y=y, z=0.03, seg=6, rings=2, rough=0.3, bottom=False)
