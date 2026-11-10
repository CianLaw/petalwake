# the meeting tree: a broad lime with an eight-sided stone seat built round its foot
import math
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Stone bench round a tree", "kind": "prop", "group": "square", "clear": 3.6, "wobble": 0.03}


def build(b):
    bark = "#b59a80"
    g, sd, st = C("grey"), C("sand"), C("stone")
    fork = (0.05, 0.0, 2.7)
    with b.detail(0):
        with b.at(rz=22.5):
            b.revolve([(1.6, -0.3), (1.6, 0.4), (1.68, 0.42), (1.68, 0.49), (0.95, 0.49), (0.95, 0.4)], "ashlar", seg=8, smooth=False, cols=[g, sd, st, st, sd])
            b.disc(0.95, "cobble", col=PP.SOIL, seg=8, z=0.42)
        PP.sweep(b, [(0, 0, 0.3), (0.0, 0.0, 1.2), (0.04, 0.0, 2.0), fork], radii=[0.4, 0.3, 0.27, 0.26], n=8, mat="timber", col=bark)
        for (ex, ey, ez) in ((-1.5, 0.6, 4.4), (1.6, -0.4, 4.5), (0.4, 1.6, 4.6), (-0.2, -1.5, 4.3), (0.1, 0.1, 5.2)):
            PP.sweep(b, [fork, (fork[0] + (ex - fork[0]) * 0.5, fork[1] + (ey - fork[1]) * 0.5, (fork[2] + ez) / 2 + 0.1), (ex, ey, ez)], radii=[0.17, 0.12, 0.07], n=5, mat="timber", col=bark)
        PP.crown(b, [(0.1, 0.0, 5.3, 2.5, 2.5, 1.7), (-1.9, 0.7, 4.6, 1.5), (1.9, -0.5, 4.7, 1.6), (0.5, 2.0, 4.8, 1.5), (-0.3, -1.9, 4.5, 1.45), (0.2, 0.2, 6.5, 1.6), (-1.2, -1.0, 5.6, 1.2), (1.3, 1.1, 5.7, 1.25)],
                 col="#72b052", wind=0.45)
    with b.detail(2):
        for a in (20, 110, 200, 290):
            with b.at(rz=a):
                PP.tuft(b, 0, -0.75, 0.42, r=0.12, h=0.2)
                PP.tuft(b, 0.3, -1.72, 0, r=0.12, h=0.22)
        PP.blooms(b, 0.3, 0.6, 0.48, 0.25, n=5, cols=["#f4f1e4", "#f5c842"])
        PP.basket(b, 1.1, -0.75, 0.49, r=0.18, h=0.18, fill="!#f2d03c")
        PP.jar(b, -1.25, 0.2, 0.49, s=0.9, kind="jug", col="#4f7fae")
