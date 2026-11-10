# market stall: the draper. A pointed tent in yellow stripes, bolts of cloth stacked, lengths hung out to show
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Cloth stall", "kind": "prop", "group": "square", "clear": 2.2}

DYES = ["#b5433a", "#3f6fb5", "#d9a431", "#7a4672", "#3f8f5f", "#d9879a", "#2f8f8f", "#f2ead8", "#d97b35", "#8fcfae"]


def build(b):
    s = PP.stall(b, w=2.8, d=1.9, roof="hip", cols=("stripe_yellow", "linen"), apron="cloth", apron_col=("#7a4672", "#8a5682"), rise=0.8, counter=0.82)
    top, y0, y1, hw, py, px = s["top"], s["y0"], s["y1"], s["hw"], s["py"], s["px"]
    ph = s["post_h"]
    with b.detail(1):
        # lengths of cloth hung along the back and one side
        for i, x in enumerate((-1.05, -0.35, 0.35, 1.05)):
            PP.drape(b, (x + 0.3, py - 0.02, ph - 0.1), (x - 0.3, py - 0.02, ph - 0.1), drop=b.r(1.2, 1.55), col=DYES[i], wind=0.45, sway=0.06)
        for i, y in enumerate((-0.2, 0.45)):
            PP.drape(b, (px - 0.02, y - 0.28, ph - 0.1), (px - 0.02, y + 0.28, ph - 0.1), drop=b.r(1.1, 1.4), col=DYES[4 + i], wind=0.45)
    with b.detail(2):
        k = 0
        for row, n in enumerate((4, 3, 2)):          # a pyramid of bolts along the back of the counter
            for i in range(n):
                x0 = -1.15 + 0.17 * row + i * 0.2
                yy = y1 - 0.2
                PP.bolt(b, (x0 - 0.4, yy, top + 0.085 + row * 0.145), (x0 + 0.5, yy, top + 0.085 + row * 0.145), r=0.085, col=DYES[(k * 3 + 1) % len(DYES)])
                k += 1
        for i, (x, n) in enumerate(((0.55, 4), (0.95, 3), (-0.9, 2))):
            for j in range(n):
                b.box(0.34, 0.26, 0.05, "cloth", col=DYES[(i * 4 + j * 3) % len(DYES)], x=x + b.r(-0.02, 0.02), y=y0 + 0.26 + b.r(-0.02, 0.02), z=top + 0.05 * j)
        for i in range(4):
            PP.bolt(b, (-0.5 + 0.24 * i, y0 + 0.1, top + 0.07), (-0.5 + 0.24 * i + 0.05, y0 + 0.62, top + 0.07), r=0.07, col=DYES[(i * 2 + 5) % len(DYES)])
        # a basket of ribbon rolls, standing bolts in a tub, ribbons from the pole
        PP.basket(b, -hw - 0.15, -1.2, 0, r=0.24, h=0.22, fill="!#d9879a")
        P.barrel(b, hw + 0.05, -1.05, 0, r=0.26, h=0.5)
        for i, (dx, dy) in enumerate(((-0.08, 0.05), (0.09, 0.02), (0.0, -0.09))):
            PP.bolt(b, (hw + 0.05 + dx, -1.05 + dy, 0.2), (hw + 0.05 + dx * 2.2, -1.05 + dy * 2.2, 1.15 + 0.1 * i), r=0.065, col=DYES[(i * 3) % len(DYES)])
        for i, a in enumerate((20, 140, 260)):
            with b.at(0, 0, ph + 0.8 + 0.22, rz=a):
                PP.face2(b, [(0, 0, 0), (0, -0.5, -0.1), (0, -0.52, -0.16), (0, 0, -0.06)], "cloth", col=DYES[i], wind=(0, 0.8, 0.8, 0))
