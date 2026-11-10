# a haystack: round and domed, roped down with stones, its pole poking through, a ladder and a fork left against it
import math
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Haystack", "kind": "prop", "group": "green", "clear": 2.6, "wobble": 0.03}


def build(b):
    hay = PP.STRAW
    with b.detail(0):
        b.revolve([(1.75, -0.2), (1.9, 0.5), (2.0, 1.4), (1.72, 2.0), (1.15, 2.85), (0.45, 3.45), (0.0, 3.6)], "thatch", seg=12,
                  cols=[shade(hay, 0.86), shade(hay, 0.95), shade(hay, 0.8), hay, shade(hay, 1.06), shade(hay, 1.1)], wind=0.04)
    with b.detail(1):
        b.tube((0, 0, 3.3), (0.04, 0.02, 4.15), r=0.05, r1=0.035, mat="planks", col="#c9a57a", n=5)
        b.revolve([(2.02, 1.86), (2.1, 1.74), (2.03, 1.6)], "thatch", col=shade(hay, 0.72), seg=12)             # the eaves' shadow line
        with b.at(1.22, -1.02, 0, rz=50):
            P.ladder(b, 2.5, w=0.42)
    with b.detail(2):
        for k in range(4):                                    # ropes over the top, weighted with stones
            with b.at(rz=45 + 90 * k):
                PP.rope(b, [(0, 0, 3.62), (0, -0.5, 3.44), (0, -1.2, 2.86), (0, -1.76, 2.0), (0, -2.05, 1.45), (0, -2.06, 0.95)], r=0.016)
                b.stone(0.22, 0.2, 0.2, col="grey", x=0, y=-2.1, z=0.75, jitter=0.2, bottom=True)
        b.beam((-1.55, -1.6, 0.0), (-1.2, -1.25, 1.75), w=0.035, mat="planks", col="#c9a57a")                  # the fork
        for d in (-0.06, 0.0, 0.06):
            b.beam((-1.2 + d, -1.25 - d, 1.75), (-1.14 + d, -1.19 - d, 2.02), w=0.014, mat="metal", col="iron", caps=False)
        rng = b.rng
        for _ in range(7):
            a, r = rng.uniform(0, 6.28), rng.uniform(1.9, 2.6)
            b.blob(0.3, 0.26, 0.07, mat="thatch", col=hay, x=r * math.cos(a), y=r * math.sin(a), z=0.03, seg=6, rings=2, rough=0.3, bottom=False)
        for a in (10, 130, 250):
            with b.at(rz=a):
                PP.tuft(b, 0, -2.2, 0, r=0.14, h=0.3)
