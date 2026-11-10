# market stall: the fishmonger. A lean-to awning in blue stripes, a slanted slab of fish, barrels and a catch hung up
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Fish stall", "kind": "prop", "group": "square", "clear": 2.1}

SILVER = ["#9fb3c2", "#b8c4cc", "#8aa3b8", "#c7ced2", "#e0a090", "#7f97aa"]


def build(b):
    s = PP.stall(b, w=2.5, d=1.6, roof="lean", cols=("stripe_blue", "linen"), apron="boards", apron_col="#b9c4c9", rise=0.5)
    top, y0, y1, hw, py = s["top"], s["y0"], s["y1"], s["hw"], s["py"]
    with b.detail(1):
        with b.at(0, y0 - 0.02, top, rx=14):
            PP.board(b, (-hw + 0.04, 0.42, 0.03), (hw - 0.04, 0.42, 0.03), w=0.84, t=0.05, col="#dfe6e8")
            with b.detail(2):
                for row in range(2):
                    for i in range(6):
                        x = -hw + 0.3 + (2 * hw - 0.6) * i / 5 + b.r(-0.04, 0.04)
                        PP.fish(b, x, 0.2 + 0.4 * row + b.r(-0.03, 0.03), 0.056, L=b.r(0.3, 0.4), col=b.pick(SILVER), rz=90 + b.r(-18, 18))
                PP.fish(b, 0.2, 0.42, 0.06, L=0.62, col="#6f8fa6", rz=4)
                b.box(2 * hw - 0.08, 0.04, 0.07, "planks", col="darkoak", y=0.02, z=0.03)
    with b.detail(2):
        P.barrel(b, -hw - 0.05, -1.0, 0, r=0.3, h=0.74)
        with b.at(-hw - 0.05, -1.0, 0.74):
            b.disc(0.24, "water", seg=10, z=-0.05)
        P.barrel(b, hw - 0.2, 0.5, 0, r=0.28, h=0.7)
        PP.basket(b, hw + 0.1, -1.05, 0, r=0.27, h=0.24, fill="#3f4a5a", heap=0.08)
        PP.tray(b, -0.3, -1.25, 0, w=0.6, d=0.42, h=0.16, fill="!#d9603a", loose=4)
        # the day's best hung from the front rail, and a string of small ones
        zr = s["post_h"] - 0.1
        with b.at(0.75, -py, zr):
            PP.rope(b, [(0, 0, 0), (0, 0, -0.14)], r=0.008)
            PP.sweep(b, [(0, 0, -0.14), (0, 0, -0.26), (0, 0, -0.5), (0, 0, -0.74), (0, 0, -0.86)], radii=[0.015, 0.05, 0.085, 0.06, 0.02], n=6, mat="paint", col="#8aa3b8", squash=0.55)
            PP.face2(b, [(0, 0, -0.16), (-0.09, 0, -0.06), (0.09, 0, -0.06)], "paint", col="#7f97aa")
        for i in range(5):
            x = -0.95 + 0.17 * i
            PP.face2(b, [(x, -py, zr), (x - 0.045, -py, zr - 0.2), (x, -py, zr - 0.3), (x + 0.045, -py, zr - 0.2)], "paint", col=b.pick(SILVER), wind=(0, 0.2, 0.3, 0.2))
        PP.coil(b, hw - 0.5, -1.2, 0, r=0.22, turns=2, rr=0.03)
