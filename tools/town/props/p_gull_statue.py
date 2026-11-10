# the gull: a bronze sea bird about to take wing, green with age, on a stepped stone plinth (and a live one perched on it)
import math
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

META = {"name": "Gull statue", "kind": "prop", "group": "square", "clear": 1.4, "wobble": 0.015}

BRONZE = "copper"


def wing(b, sgn):
    sh = (sgn * 0.14, 0.02, 0.62)
    el = (sgn * 0.62, 0.1, 1.12)
    tip = (sgn * 1.28, 0.3, 1.5)
    mid = (sgn * 0.78, 0.36, 0.98)
    back = (sgn * 0.16, 0.34, 0.52)
    PP.face2(b, [sh, el, mid, back], "metal", col=BRONZE)
    PP.face2(b, [el, tip, mid], "metal", col=shade(BRONZE, 0.9))


def build(b):
    with b.detail(1):
        b.box(1.4, 1.4, 0.4, "ashlar", col="grey", z=-0.22, taper=0.97)
        b.box(1.06, 1.06, 0.18, "ashlar", col="sand", z=0.18)
        b.box(0.76, 0.76, 1.12, "ashlar", col="stone", z=0.36, taper=0.94)
        b.box(0.94, 0.94, 0.07, "ashlar", col="sand", z=1.48, bottom=True)
        b.box(0.86, 0.86, 0.08, "ashlar", col="stone", z=1.55, taper=0.85)
        with b.at(0, 0, 1.63):
            b.blob(0.3, 0.26, 0.14, mat="ashlar", col="grey", z=0.06, seg=7, rings=3, rough=0.2, bottom=False)       # a rock for it to stand on
            for sx in (-1, 1):
                b.tube((sx * 0.08, 0.0, 0.12), (sx * 0.07, 0.03, 0.42), r=0.022, mat="metal", col=BRONZE, n=4)
            PP.sweep(b, [(0, 0.5, 0.5), (0, 0.3, 0.52), (0, 0.0, 0.6), (0, -0.24, 0.72), (0, -0.33, 0.86)], radii=[0.03, 0.16, 0.22, 0.17, 0.1], n=7, mat="metal", col=BRONZE, caps=(True, True))
            b.blob(0.115, 0.135, 0.11, mat="metal", col=BRONZE, x=0, y=-0.38, z=0.94, seg=7, rings=3, rough=0.03)
            PP.sweep(b, [(0, -0.48, 0.95), (0, -0.63, 0.92), (0, -0.7, 0.88)], radii=[0.042, 0.026, 0.006], n=4, mat="metal", col="brass")
            PP.face2(b, [(-0.14, 0.42, 0.5), (0.14, 0.42, 0.5), (0.2, 0.7, 0.46), (-0.2, 0.7, 0.46)], "metal", col=BRONZE)
            wing(b, -1)
            wing(b, 1)
    with b.detail(2):
        PH.gull(b, 0.0, -0.36, 1.63 + 1.05, rz=140, s=0.9)
        b.box(0.34, 0.02, 0.22, "metal", col="brass", y=-0.37, z=0.82, bottom=True)                    # a blank brass plate
        for a in (30, 150, 270):
            with b.at(rz=a):
                PP.tuft(b, 0, -0.78, 0, r=0.11, h=0.2)
