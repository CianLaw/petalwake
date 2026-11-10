# a crooked timber lamp post: a bracket arm with a lantern hanging from it, the foot wedged with stones
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Timber lamp post", "kind": "prop", "group": "square", "clear": 0.8, "wobble": 0.02, "lean": (0.012, 0.006)}


def build(b):
    H = 3.3
    with b.detail(1):
        b.beam((0, 0, -0.3), (0, 0, H), w=0.17, mat="timber", lod=1)
        b.box(0.26, 0.26, 0.05, "planks", col="darkoak", z=H, bottom=True)                     # weather cap
        b.beam((0, 0, H - 0.3), (0, -0.92, H - 0.22), w=0.1, mat="timber")                       # the arm
        b.beam((0, 0, H - 1.05), (0, -0.66, H - 0.32), w=0.08, mat="timber")                     # its brace
        with b.at(0, -0.8, H - 0.3):
            PP.lantern(b, s=0.3, h=0.44, sides=4, hang=0.16)
    with b.detail(2):
        for a, r, s in ((20, 0.2, 0.26), (140, 0.19, 0.22), (250, 0.21, 0.3), (320, 0.17, 0.18)):
            with b.at(rz=a):
                b.stone(s, s * 0.8, s * 0.55, col="warm", y=-r, jitter=0.2)
        b.box(0.2, 0.2, 0.06, "metal", col="iron", z=1.55, top=False)                              # an old iron band
        PP.tuft(b, -0.2, 0.2, 0, r=0.12, h=0.24)
        PP.tuft(b, 0.24, -0.16, 0, r=0.1, h=0.18, n=4)
