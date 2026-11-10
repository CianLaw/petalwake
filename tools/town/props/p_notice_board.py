# the town notice board: papers pinned under a little shingled roof (pictures and seals, no writing)
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Notice board", "kind": "prop", "group": "square", "clear": 1.3, "wobble": 0.02}


def build(b):
    with b.detail(1):
        for sx in (-1, 1):
            b.beam((sx * 0.8, 0, -0.3), (sx * 0.8, 0, 2.2), w=0.12, mat="timber")
        PP.board(b, (-0.74, 0.0, 1.42), (0.74, 0.0, 1.42), w=0.98, t=0.04, col="#b9a183", up=(0, 1, 0))
        for z in (0.93, 1.91):
            b.beam((-0.76, -0.01, z), (0.76, -0.01, z), w=0.07, h=0.06, mat="timber")
        b.gable_roof(2.05, 0.5, pitch=34, mat="shingle", z=2.2, ridge="x", eave=0.14, verge=0.1, course=0.24, thick=0.06, barge=False, ridge_roll=False)
    with b.detail(2):
        rng = b.rng
        papers = [(-0.5, 1.62, 0.3, 0.4, "#f4ecd6"), (-0.12, 1.55, 0.26, 0.34, "#f6e3a6"), (0.25, 1.64, 0.34, 0.3, "#efe6da"), (0.56, 1.5, 0.22, 0.3, "#f2c9c0"),
                  (-0.42, 1.14, 0.34, 0.26, "#e9e2cf"), (0.05, 1.12, 0.28, 0.3, "#f4ecd6"), (0.46, 1.1, 0.26, 0.22, "#dfe8d8")]
        for i, (x, z, w, h, c) in enumerate(papers):
            with b.at(x, -0.024 - 0.002 * i, z, ry=rng.uniform(-7, 7)):
                PP.face2(b, [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], "paint", col=c, wind=(0.25, 0.3, 0.0, 0.0))
                b.box(0.025, 0.012, 0.025, "metal", col="brass", y=-0.006, z=h / 2 - 0.04, bottom=True)
                if i == 0:
                    with b.at(0, -0.003, 0.02):
                        PP.emblem(b, "fish", s=0.45, col="!#3f6fb5", two=False)
                if i == 2:
                    with b.at(-0.05, -0.003, 0.0):
                        PP.emblem(b, "star", s=0.4, col="!#d9a431", two=False)
                    b.box(0.05, 0.008, 0.05, "paint", col="!#b5433a", x=0.1, y=-0.004, z=-0.12, bottom=True)
                if i == 5:
                    with b.at(0, -0.003, 0.0):
                        PP.emblem(b, "anchor", s=0.4, col="!#2c2a2a", two=False)
        for a, r, s in ((40, 0.2, 0.22), (200, 0.2, 0.26)):
            for sx in (-1, 1):
                with b.at(sx * 0.8, 0, 0, rz=a):
                    b.stone(s, s * 0.8, s * 0.5, col="warm", y=-r, jitter=0.2)
        PP.tuft(b, -0.55, 0.15, 0, r=0.12, h=0.24)
        PP.tuft(b, 0.3, -0.12, 0, r=0.1, h=0.2)
