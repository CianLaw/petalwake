# a fish-drying frame: split fish hung in rows on poles between four posts, a salt cask, a cat keeping watch
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

META = {"name": "Fish-drying frame", "kind": "prop", "group": "harbour", "clear": 2.3, "length": 3.2, "axis": "x", "wobble": 0.02}


def build(b):
    W, Dp, H = 3.0, 1.1, 2.15
    PH.fish_rack(b, 0, 0, 0, w=W, h=H, rows=3, n=9, deep=Dp)
    with b.detail(1):
        for sy in (-1, 1):
            b.beam((-W / 2, sy * Dp / 2, 0.25), (-W / 2 + 0.85, sy * Dp / 2, H - 0.1), w=0.06, mat="timber", col="greyoak")
            b.beam((W / 2, sy * Dp / 2, 0.25), (W / 2 - 0.85, sy * Dp / 2, H - 0.1), w=0.06, mat="timber", col="greyoak")
    PH.fish_line(b, (-W / 2, 0.0, H + 0.02), (W / 2, 0.0, H + 0.02), n=10, col=PH.SMOKED, size=0.34, sag=0.0)
    PH.basket(b, 1.95, -0.5, 0, r=0.3, h=0.32)
    PH.cat(b, -1.95, -0.6, 0, rz=70, col="!#3b3532")
    PH.gull(b, W / 2, Dp / 2, H + 0.14, rz=220)
    with b.detail(2):
        PP.barrel(b, 2.0, 0.45, 0, r=0.28, h=0.7)
        with b.at(2.0, 0.45, 0.66):
            b.disc(0.24, "paint", col="#f2f0ea", seg=9)
        for (x, y) in ((-1.7, 0.7), (0.4, -0.8), (1.5, 0.9)):
            PP.tuft(b, x, y, 0, r=0.12, h=0.22)
