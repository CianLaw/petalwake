# a white picket fence, 4 m: pointed pales on two rails, half a post at each end so that segments make whole posts
from kit import *
import parts as P
import parts_p as PP

L = 4.0
META = {"name": "Picket fence 4 m", "kind": "prop", "group": "walls", "clear": 2.1, "length": L, "axis": "x", "height": 1.0, "wobble": 0.0}
WHITE = "ivory"


def pale(b, x, h, w=0.085, t=0.022, lean=0.0):
    with b.at(x, -0.035, 0.06, ry=lean):
        for sy in (-1, 1):
            q = [(-w / 2, sy * t / 2, 0), (w / 2, sy * t / 2, 0), (w / 2, sy * t / 2, h - 0.07), (0, sy * t / 2, h), (-w / 2, sy * t / 2, h - 0.07)]
            b.face(q if sy < 0 else list(reversed(q)), "planks", col=WHITE)
        b.quad((w / 2, -t / 2, 0), (w / 2, t / 2, 0), (w / 2, t / 2, h - 0.07), (w / 2, -t / 2, h - 0.07), "planks", col=shade(WHITE, 0.85))
        b.quad((-w / 2, t / 2, 0), (-w / 2, -t / 2, 0), (-w / 2, -t / 2, h - 0.07), (-w / 2, t / 2, h - 0.07), "planks", col=shade(WHITE, 0.85))


def build(b):
    n = 28
    pitch = (L - 0.12) / n
    with b.detail(1):
        for sx in (-1, 1):                                    # half posts
            b.box(0.06, 0.11, 1.35, "planks", col=WHITE, x=sx * (L / 2 - 0.03), y=0.02, z=-0.3)
            b.box(0.06, 0.15, 0.05, "planks", col=WHITE, x=sx * (L / 2 - 0.03), y=0.02, z=1.05, ty=0.4)
        for z in (0.32, 0.78):
            PP.board(b, (-L / 2 + 0.06, 0.0, z), (L / 2 - 0.06, 0.0, z), w=0.07, t=0.035, col=WHITE, up=(0, 1, 0), caps=False)
        for i in range(0, n, 2):
            pale(b, -L / 2 + 0.06 + pitch * (i + 0.5), 0.9 + b.r(-0.02, 0.03), lean=b.r(-1.2, 1.2))
    with b.detail(2):
        for i in range(1, n, 2):
            pale(b, -L / 2 + 0.06 + pitch * (i + 0.5), 0.9 + b.r(-0.02, 0.03), lean=b.r(-1.2, 1.2))
        PP.clump(b, -1.2, -0.3, 0, r=0.22, h=0.22, flowers=["#e8497a", "#f2a0bd"])
        PP.clump(b, 0.9, -0.28, 0, r=0.2, h=0.2, flowers=["#f5c842", "#f4f1e4"])
        PP.clump(b, 1.5, 0.3, 0, r=0.22, h=0.26, flowers=["#b08ae6"])
        for x in (-1.8, -0.3, 0.3, 1.9):
            PP.tuft(b, x, -0.12, 0, r=0.1, h=0.2)
