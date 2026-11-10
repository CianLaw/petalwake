# a kitchen garden, 4 x 3 m: boarded bed, ridged rows of cabbages, carrots and lettuce, a row of bean poles, pumpkins
import math
from kit import *
import parts as P
import parts_p as PP
import parts_c as PC

META = {"name": "Vegetable patch 4 x 3 m", "kind": "prop", "group": "green", "clear": 2.6, "size": (4.0, 3.0)}


def build(b):
    W, D = 4.0, 3.0
    with b.detail(1):
        b.box(W - 0.1, D - 0.1, 0.5, "cobble", col=PP.SOIL, z=-0.38)                       # the bed
        for (p0, p1) in (((-W / 2, -D / 2, 0.08), (W / 2, -D / 2, 0.08)), ((-W / 2, D / 2, 0.08), (W / 2, D / 2, 0.08)),
                         ((-W / 2, -D / 2, 0.08), (-W / 2, D / 2, 0.08)), ((W / 2, -D / 2, 0.08), (W / 2, D / 2, 0.08))):
            PP.board(b, p0, p1, w=0.2, t=0.04, col="greyoak", up=(1, 0, 0) if p0[0] != p1[0] else (0, 1, 0))
        ys = [-1.12, -0.56, 0.0, 0.56, 1.12]
        for y in ys:                                          # the ridges
            b.blob(1.85, 0.2, 0.09, mat="cobble", col=shade(PP.SOIL, 1.12), x=0, y=y, z=0.12, seg=6, rings=2, rough=0.08, bottom=False)
        # the bean row: crossed poles under a ridge pole, the vines well up
        yb = ys[3]
        b.beam((-1.75, yb, 1.72), (1.75, yb, 1.72), w=0.035, mat="planks", col="#c9a57a")
        for i in range(5):
            x = -1.6 + 0.8 * i
            b.beam((x, yb - 0.3, 0.1), (x + 0.04, yb + 0.07, 1.95), w=0.03, mat="planks", col="#c9a57a", caps=False)
            b.beam((x + 0.06, yb + 0.3, 0.1), (x + 0.02, yb - 0.07, 1.95), w=0.03, mat="planks", col="#c9a57a", caps=False)
            PC.climber(b, (x, yb - 0.22, 0.3), (x + 0.03, yb, 1.6), n=3, r=0.17, col="#86c25e", bloom=["#e8497a", "#f4f1e4"] if i % 2 else None)
            PC.climber(b, (x + 0.05, yb + 0.22, 0.3), (x + 0.03, yb, 1.5), n=2, r=0.16, col="#7db45e")
    with b.detail(2):
        for i in range(8):                                    # cabbages
            x = -1.7 + 3.4 * i / 7
            b.blob(0.17, 0.17, 0.13, mat="ivy", col="!#a9cf8c" if i % 3 else "!#8fbf9a", x=x, y=ys[0], z=0.26, seg=6, rings=3, rough=0.15, bottom=False)
            b.blob(0.24, 0.24, 0.05, mat="ivy", col="#8fc46a", x=x, y=ys[0], z=0.2, seg=6, rings=2, rough=0.25, bottom=False)
        for i in range(11):                                   # carrot tops
            PP.tuft(b, -1.75 + 3.5 * i / 10, ys[1], 0.17, r=0.1, h=0.24, n=4, col="!#7fbf55")
        for i in range(9):                                    # lettuces
            x = -1.7 + 3.4 * i / 8
            b.blob(0.15, 0.15, 0.08, mat="ivy", col="!#b9dc7a" if i % 2 else "!#a05a6a", x=x, y=ys[2], z=0.2, seg=6, rings=2, rough=0.25, bottom=False)
        for (x, r) in ((-1.3, 0.2), (-0.2, 0.26), (1.0, 0.18)):          # pumpkins among their leaves
            b.blob(r, r, r * 0.72, mat="paint", col="!#e8892e", x=x, y=ys[4], z=0.16 + r * 0.6, seg=7, rings=3, rough=0.06)
            b.tube((x, ys[4], 0.16 + r * 1.2), (x + 0.03, ys[4], 0.16 + r * 1.2 + 0.07), r=0.02, mat="paint", col="#6f8f4a", n=4)
        for x in (-1.75, -0.75, 0.35, 0.6, 1.55):
            b.blob(0.22, 0.2, 0.05, mat="ivy", col="#7db45e", x=x, y=ys[4] + b.r(-0.1, 0.1), z=0.2, seg=5, rings=2, rough=0.3, bottom=False, wind=0.2)
        # a spade left standing, a basket of the day's picking
        b.beam((1.72, -0.3, 0.05), (1.78, -0.26, 1.05), w=0.035, mat="planks", col="#c9a57a")
        b.box(0.19, 0.02, 0.26, "metal", col="lead", x=1.715, y=-0.305, z=-0.12)
        b.beam((1.72, -0.26, 1.05), (1.84, -0.26, 1.05), w=0.03, mat="planks", col="#c9a57a")
        PP.basket(b, -2.3, -0.9, 0, r=0.24, h=0.22, fill="!#8fbf5a")
        for (x, y) in ((-2.15, 1.3), (2.12, -1.4), (2.15, 0.9), (-0.6, -1.65), (1.0, 1.66)):
            PP.tuft(b, x, y, 0, r=0.12, h=0.22)
