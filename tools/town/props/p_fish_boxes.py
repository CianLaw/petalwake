# the morning's catch landed on the quay: stacked fish boxes, baskets, a cask of brine, and gulls after their share
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

META = {"name": "Fish boxes", "kind": "prop", "group": "harbour", "clear": 1.5}


def build(b):
    PH.fish_box(b, -0.4, 0.1, 0, rz=6)
    PH.fish_box(b, -0.38, 0.12, 0.2, rz=-4, fill=PH.SMOKED)
    PH.fish_box(b, -0.42, 0.08, 0.4, rz=10)
    PH.fish_box(b, 0.45, 0.25, 0, rz=-12, fill="#b8c4cc")
    PH.fish_box(b, 0.48, 0.22, 0.2, rz=-2)
    PH.fish_box(b, 0.3, -0.5, 0, rz=24, fill="!#d9603a")
    PH.basket(b, -1.0, -0.4, 0, r=0.3, h=0.32)
    PH.basket(b, 1.15, -0.25, 0, r=0.26, h=0.28, fill="#3f4a5a")
    PH.gull(b, -0.42, 0.08, 0.62, rz=160)
    PH.gull(b, 0.95, 0.7, 0, rz=250)
    with b.detail(2):
        PP.barrel(b, -1.1, 0.5, 0, r=0.27, h=0.68)
        with b.at(-1.1, 0.5, 0.64):
            b.disc(0.22, "water", seg=9)
        PP.coil(b, 0.1, 1.0, 0, r=0.24, turns=2)
