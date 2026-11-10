# garden wall, 6 m, with a boarded door in a raised arched doorway under a little tiled coping; repeats with p_wall_garden
import math
from kit import *
import parts as P
import parts_p as PP
import parts_c as PC
import parts_m as PM

L, H, T = 6.0, 1.7, 0.45
META = {"name": "Garden wall 6 m with a door", "kind": "prop", "group": "walls", "clear": 3.1, "length": L, "axis": "x", "height": H, "thick": T, "wobble": 0.0,
        "door": {"x": 0.0, "width": 1.0}}
DW, BW, BH = 1.0, 1.9, 2.55


def top(x):
    return H + 0.05 * math.sin(2 * math.pi * x / L) + 0.025 * math.sin(4 * math.pi * x / L)


def build(b):
    with b.detail(0):
        PP.wall_run(b, -L / 2, -BW / 2, H, t=T, hfun=top, ends="l")
        PP.wall_run(b, BW / 2, L / 2, H, t=T, hfun=top, ends="r")
        with b.at(-BW / 2, -T / 2, 0):
            f, k = PM.arcade(b, BW, BH, thick=T, arches=[(BW / 2, DW, 2.15, 0.5)], mat="masonry", col="warm")
        b.box(BW, T, 1.2, "masonry", col=shade("warm", 0.85), z=-1.2, top=False)
        b.gable_roof(BW, T, pitch=36, mat="tiles", z=BH, ridge="x", eave=0.14, verge=0.1, course=0.2, thick=0.06, barge=False, ridge_roll=False)
    PC.arch_stones(f, BW / 2, 0.0, DW, 2.15, 0.5, n=9, size=(0.22, 0.26), proud=0.055)
    PC.arch_stones(k, BW / 2, 0.0, DW, 2.15, 0.5, n=9, size=(0.22, 0.26), proud=0.055, jambs=False)
    P.lantern(f, BW / 2 + 0.72, 1.72)
    PC.wood_gate(b, w=DW, h=2.1, col="teal", leaves=1, ajar=0.0)
    with b.detail(1):
        PP.cap_slabs(b, -L / 2, -BW / 2, top, T, over=0.07, thick=0.11, col="#f1e4cc")
        PP.cap_slabs(b, BW / 2, L / 2, top, T, over=0.07, thick=0.11, col="#f1e4cc")
        PC.climber(b, (-0.85, -T / 2 - 0.1, 0.5), (-0.6, -T / 2 - 0.1, 2.5), n=5, r=0.22, bloom=["#f2a0bd", "#e8497a", "#f4f1e4"])
        PC.climber(b, (-0.5, -T / 2 - 0.08, 2.6), (0.5, -T / 2 - 0.08, 2.72), n=3, r=0.2, bloom=["#f2a0bd", "#e8497a"])
    with b.detail(2):
        PP.wall_stones(b, -L / 2, -BW / 2, 0.05, H, T, n=5, hfun=top)
        PP.wall_stones(b, BW / 2, L / 2, 0.05, H, T, n=5, hfun=top)
        b.box(DW + 0.3, 0.42, 0.1, "ashlar", col="sand", y=-T / 2 - 0.16, z=-0.04)                 # the doorstep
        with b.at(0.3, 0.03, 1.05, rx=90):
            PP.torus(b, 0.06, 0.012, col="iron", seg=7, n=3)
        PP.pot_plant(b, 0.78, -T / 2 - 0.25, 0, r=0.15, h=0.24, flowers=["#f5c842", "#f4f1e4"])
        for x in (-2.5, -1.3, 2.3):
            PP.tuft(b, x, -T / 2 - 0.08, 0, r=0.12, h=b.r(0.18, 0.3))
