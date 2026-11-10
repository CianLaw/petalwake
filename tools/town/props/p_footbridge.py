# a wooden footbridge over the stream: cambered plank deck on two bowed stringers, cross-braced handrails, stone footings
import math
from kit import *
import parts as P
import parts_p as PP

SPAN, L, W = 5.0, 6.0, 1.5
META = {"name": "Wooden footbridge, 5 m span", "kind": "prop", "group": "walls", "clear": 3.6, "length": L, "axis": "x", "span": SPAN, "width": W, "wobble": 0.015,
        "notes": "deck ends at z = 0 at x = +-3; the stream runs along y under it; stone footings go 3 m down"}


def zc(x):
    return 0.05 + 0.3 * (1 - (x / (L / 2)) ** 2)


def build(b):
    n = 12
    xs = [-L / 2 + L * i / n for i in range(n + 1)]
    with b.detail(0):
        for sx in (-1, 1):                                    # footings in the banks
            b.box(0.7, W + 0.5, 3.0, "masonry", col="warm", x=sx * (SPAN / 2 + 0.36), z=-3.02, cap="ashlar", capcol="sand")
        for sy in (-1, 1):
            PP.sweep(b, [(x, sy * (W / 2 - 0.16), zc(x) - 0.17) for x in xs], r=0.12, n=4, mat="timber", squash=1.25, caps=(True, True))
        rows = [[(x, -W / 2, zc(x) - 0.03), (x, W / 2, zc(x) - 0.03)] for x in xs]
        PP.loft(b, rows, "planks", col=shade("greyoak", 0.75), smooth=False, two=True)
    with b.detail(1):
        m = 27
        for i in range(m):                                    # the deck planks
            x = -L / 2 + 0.05 + (L - 0.1) * (i + 0.5) / m
            PP.board(b, (x, -W / 2 - b.r(0.0, 0.05), zc(x)), (x, W / 2 + b.r(0.0, 0.05), zc(x)), w=(L - 0.1) / m - 0.012, t=0.045, col=shade("greyoak", b.r(0.86, 1.06)))
        px = [-2.75, -1.4, 0.0, 1.4, 2.75]
        for sy in (-1, 1):
            y = sy * (W / 2 - 0.05)
            for x in px:
                b.beam((x, y, zc(x) - 0.25), (x, y + sy * 0.04, zc(x) + 1.0), w=0.09, mat="timber")
                b.beam((x, y + sy * 0.36, zc(x) - 0.2), (x, y + sy * 0.03, zc(x) + 0.5), w=0.06, mat="timber")      # outriggers
                b.beam((x, y - sy * 0.1, zc(x) - 0.2), (x, y + sy * 0.38, zc(x) - 0.2), w=0.07, mat="timber")
            PP.sweep(b, [(x, y + sy * 0.04, zc(x) + 1.0) for x in px], r=0.05, n=4, mat="timber", caps=(True, True))
    with b.detail(2):
        for sy in (-1, 1):
            y = sy * (W / 2 - 0.03)
            for i in range(len(px) - 1):
                xa, xb = px[i], px[i + 1]
                b.beam((xa, y, zc(xa) + 0.14), (xb, y, zc(xb) + 0.92), w=0.045, mat="timber", caps=False)
                b.beam((xa, y, zc(xa) + 0.92), (xb, y, zc(xb) + 0.14), w=0.045, mat="timber", caps=False)
        for (x, sy) in ((-3.1, -1), (3.15, 1), (-3.2, 1), (3.1, -1)):
            PP.tuft(b, x, sy * (W / 2 + 0.25), 0, r=0.14, h=0.3)
        PP.clump(b, -3.3, -1.0, 0, r=0.24, h=0.2, flowers=["#f5c842", "#f4f1e4"])
        PP.clump(b, 3.3, 0.95, 0, r=0.22, h=0.2, flowers=["#b08ae6"])
