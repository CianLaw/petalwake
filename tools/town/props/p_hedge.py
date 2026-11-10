# a clipped hedge, 6 m: lumpy and leaning, flat at its ends so it repeats along x
from kit import *
import parts as P
import parts_p as PP

L = 6.0
META = {"name": "Hedge 6 m", "kind": "prop", "group": "green", "clear": 3.1, "length": L, "axis": "x", "height": 1.5, "thick": 0.9, "wobble": 0.0}


def build(b):
    with b.detail(0):
        PP.hedge(b, -L / 2, L / 2, h=1.5, t=0.9, col="#6fa857", wild=0.11)
    with b.detail(2):
        PP.blooms(b, -1.4, -0.42, 0.9, 0.5, n=7, cols=["#f4f1e4", "#f2a0bd"], lift=0.5)
        PP.blooms(b, 1.6, 0.42, 0.8, 0.5, n=6, cols=["#f4f1e4"], lift=0.5)
        for x in (-2.5, -0.2, 2.0):
            PP.tuft(b, x, -0.52, 0, r=0.12, h=0.22)
            PP.tuft(b, x + 0.6, 0.52, 0, r=0.12, h=0.2)
