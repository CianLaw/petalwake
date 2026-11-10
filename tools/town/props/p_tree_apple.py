# a round old apple tree heavy with fruit: forked trunk, a ladder left in it, windfalls and a basket underneath
import math
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Apple tree", "kind": "prop", "group": "green", "clear": 2.6, "wobble": 0.03}


def build(b):
    bark = "#b59a80"
    fork = (0.14, 0.04, 1.45)
    with b.detail(0):
        PP.sweep(b, [(0, 0, -0.4), (0.03, 0.0, 0.5), (0.1, 0.02, 1.05), fork], radii=[0.27, 0.18, 0.155, 0.15], n=7, mat="timber", col=bark)
        for (ex, ey, ez) in ((-0.9, 0.35, 2.5), (1.0, -0.25, 2.55), (0.25, 0.9, 2.6), (0.05, -0.85, 2.45)):
            PP.sweep(b, [fork, (fork[0] + (ex - fork[0]) * 0.5, fork[1] + (ey - fork[1]) * 0.5, 2.0), (ex, ey, ez)], radii=[0.11, 0.08, 0.05], n=5, mat="timber", col=bark)
        PP.crown(b, [(0.1, 0.0, 3.05, 1.55, 1.55, 1.2), (-0.95, 0.4, 2.75, 1.0), (1.05, -0.3, 2.8, 1.05), (0.25, 1.0, 2.85, 0.95), (0.0, -0.95, 2.65, 0.9), (0.3, 0.1, 3.75, 0.95)], col="#77b556")
    with b.detail(2):
        rng = b.rng
        for _ in range(26):                                   # the apples, mostly round the skirts of the crown
            a, ph = rng.uniform(0, 6.283), rng.uniform(-0.75, 0.5)
            r = 1.95 + rng.uniform(-0.08, 0.12)
            x, y, z = 0.1 + r * math.cos(ph) * math.cos(a), r * math.cos(ph) * math.sin(a), 2.95 + 1.45 * math.sin(ph)
            b.blob(0.075, 0.075, 0.07, mat="paint", col=rng.choice(["!#d9382e", "!#c8302a", "!#e8a03a", "!#d9382e"]), x=x, y=y, z=z, seg=5, rings=2, rough=0.08, wind=0.3)
        for (x, y) in ((0.9, 0.6), (-0.7, -0.9), (1.3, -0.4), (-1.2, 0.3), (0.2, 1.4)):
            b.blob(0.07, 0.07, 0.06, mat="paint", col="!#c8302a", x=x, y=y, z=0.05, seg=5, rings=2, rough=0.08)
        with b.at(0.2, -1.55, 0):
            P.ladder(b, 2.5, w=0.42, col="greyoak")
        PP.basket(b, -0.85, -1.3, 0, r=0.24, h=0.22, fill="!#d9382e")
        for (x, y) in ((0.5, 0.45), (-0.45, 0.2), (0.3, -0.5)):
            PP.tuft(b, x, y, 0, r=0.13, h=0.26)
