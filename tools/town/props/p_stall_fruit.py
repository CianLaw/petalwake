# market stall: fruit under a red-striped ridge awning, slanted trays, baskets round its feet
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Fruit stall", "kind": "prop", "group": "square", "clear": 2.1}

FRUIT = ["!#d9382e", "!#f08c2e", "!#f2d03c", "!#9cc43f", "!#7a2f6a", "!#e8556a", "!#c9d94a", "!#b5281e"]


def build(b):
    s = PP.stall(b, w=2.7, d=1.7, roof="gable", cols=("stripe_red", "linen"), apron="boards")
    top, y0, y1, hw = s["top"], s["y0"], s["y1"], s["hw"]
    with b.detail(2):
        k = 0
        for row, (yy, zz, tilt) in enumerate(((y0 + 0.06, top, 14), (y0 + 0.5, top + 0.16, 22))):
            for i in range(4):
                x = -hw + 0.32 + (2 * hw - 0.64) * i / 3
                PP.tray(b, x, yy, zz, w=0.56, d=0.42, h=0.1, tilt=tilt, fill=FRUIT[k % len(FRUIT)], loose=3)
                k += 1
        b.box(2 * hw - 0.1, 0.4, 0.16, "planks", col="greyoak", y=y0 + 0.72, z=top)               # the step the back row sits on
        PP.basket(b, -hw - 0.1, -1.15, 0, r=0.26, h=0.26, fill=FRUIT[1])
        PP.basket(b, -hw + 0.45, -1.3, 0, r=0.22, h=0.22, fill=FRUIT[3])
        PP.basket(b, hw + 0.05, -1.1, 0, r=0.24, h=0.3, fill=FRUIT[0])
        P.crate(b, hw - 0.3, 0.45, 0, s=0.5, rz=12)
        P.crate(b, hw - 0.36, 0.42, 0.5, s=0.42, rz=-8)
        P.sack(b, -hw + 0.3, 0.5, 0, r=0.3)
        # strings of onions hanging from the front rail
        for x in (-0.9, 0.2, 0.75):
            zr = s["post_h"] - 0.1
            PP.rope(b, [(x, -s["py"], zr), (x, -s["py"], zr - 0.5)], r=0.008)
            for j in range(4):
                b.blob(0.05, 0.05, 0.045, mat="paint", col=b.pick(["#d9a45a", "#c98a4a", "#b5524a"]), x=x + b.r(-0.03, 0.03), y=-s["py"] + b.r(-0.03, 0.03), z=zr - 0.16 - 0.1 * j, seg=5, rings=2, rough=0.1)
