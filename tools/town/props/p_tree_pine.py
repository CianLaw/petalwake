# a pine bent by the sea wind: the trunk leans toward +x and the flat pads of needles all stream that way
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Wind-leaned pine", "kind": "prop", "group": "green", "clear": 3.0, "wobble": 0.02, "leans": "+x",
        "notes": "the trunk stands on the origin; the crown reaches about 4.6 m toward +x (turn it so +x is downwind)"}


def build(b):
    bark = "#c2a288"
    trunk = [(0, 0, -0.4), (0.05, 0, 0.8), (0.3, 0.02, 1.9), (0.8, 0.05, 3.0), (1.5, 0.1, 3.85), (2.3, 0.1, 4.45)]
    with b.detail(0):
        PP.sweep(b, trunk, radii=[0.32, 0.25, 0.2, 0.16, 0.12, 0.07], n=7, mat="timber", col=bark)
        PP.sweep(b, [trunk[3], (1.2, -0.5, 3.6), (1.7, -0.75, 4.0)], radii=[0.09, 0.06, 0.04], n=5, mat="timber", col=bark)
        PP.sweep(b, [trunk[3], (1.1, 0.55, 3.75), (1.55, 0.9, 4.2)], radii=[0.09, 0.06, 0.04], n=5, mat="timber", col=bark)
        PP.sweep(b, [trunk[4], (2.6, 0.25, 4.2), (3.4, 0.3, 4.3)], radii=[0.07, 0.05, 0.03], n=5, mat="timber", col=bark)
        PP.crown(b, [(2.7, 0.1, 4.75, 1.75, 1.3, 0.5), (1.75, -0.8, 4.2, 1.25, 0.9, 0.42), (1.65, 0.95, 4.4, 1.15, 0.85, 0.4), (3.5, 0.3, 4.45, 1.05, 0.8, 0.36), (0.95, 0.15, 3.8, 0.8, 0.7, 0.34)],
                 col="#4f8f62", wind=0.4, seg=8, rings=3, rough=0.24)
    with b.detail(1):
        PP.sweep(b, [trunk[2], (-0.25, 0.1, 2.3), (-0.7, 0.16, 2.45), (-0.95, 0.2, 2.75)], radii=[0.07, 0.05, 0.035, 0.015], n=4, mat="timber", col="#d9c7b0")       # a dead limb to windward
        PP.sweep(b, [trunk[1], (-0.2, -0.25, 1.1), (-0.42, -0.42, 1.2)], radii=[0.06, 0.04, 0.015], n=4, mat="timber", col="#d9c7b0")
    with b.detail(2):
        for (x, y, s) in ((0.45, 0.3, 0.3), (-0.4, -0.2, 0.24)):
            b.stone(s, s * 0.8, s * 0.5, col="grey", x=x, y=y, jitter=0.2)
        for (x, y) in ((0.2, -0.45), (-0.3, 0.4), (0.7, 0.1)):
            PP.tuft(b, x, y, 0, r=0.14, h=0.3, col="#a8c47a")
