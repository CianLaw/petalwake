# a tall dark cypress: a narrow flame of foliage that nods in the wind
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Cypress", "kind": "prop", "group": "green", "clear": 1.3, "wobble": 0.04, "lean": (0.008, 0.004)}


def build(b):
    with b.detail(0):
        b.tube((0, 0, -0.4), (0, 0, 1.3), r=0.17, r1=0.12, mat="timber", col="#b59a80", n=6)
        PP.crown(b, [(0.0, 0.0, 3.5, 0.98, 0.98, 3.0), (0.14, -0.1, 5.6, 0.74, 0.74, 2.6), (-0.12, 0.14, 2.5, 0.92, 0.92, 1.8), (0.03, 0.0, 7.3, 0.44, 0.44, 1.5)],
                 col="#4f8a55", wind=0.3, seg=7, rings=5, rough=0.14, vary=0.08)
    with b.detail(1):
        PP.crown(b, [(0.5, 0.3, 2.0, 0.45, 0.45, 0.8), (-0.45, -0.35, 3.2, 0.42, 0.42, 0.9), (0.3, -0.4, 4.6, 0.36, 0.36, 0.8)], col="#457d4c", wind=0.3, seg=6, rings=3, rough=0.2)
    with b.detail(2):
        for (x, y) in ((0.4, 0.3), (-0.35, -0.3)):
            PP.tuft(b, x, y, 0, r=0.12, h=0.22)
