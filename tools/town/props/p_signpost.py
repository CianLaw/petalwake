# a fingerpost where the lanes meet: three painted arms with picture signs, the foot wedged with stones, a gull on top
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

META = {"name": "Signpost", "kind": "prop", "group": "square", "clear": 1.2, "wobble": 0.02, "lean": (0.01, -0.006)}


def arm(b, z, heading, L=0.95, name="fish", tip="red", em="navy"):
    with b.at(0, 0, z, rz=heading):
        PP.board(b, (0.06, 0, 0), (L - 0.16, 0, 0), w=0.19, t=0.035, col="ivory", up=(0, 1, 0))
        for sy in (-1, 1):
            q = [(L - 0.16, sy * 0.0175, -0.095), (L, sy * 0.0175, 0.0), (L - 0.16, sy * 0.0175, 0.095)]
            b.face(q if sy < 0 else list(reversed(q)), "planks", col=tip)
        b.quad((L - 0.16, -0.0175, 0.095), (L, -0.0175, 0), (L, 0.0175, 0), (L - 0.16, 0.0175, 0.095), "planks", col=tip)
        b.quad((L, -0.0175, 0), (L - 0.16, -0.0175, -0.095), (L - 0.16, 0.0175, -0.095), (L, 0.0175, 0), "planks", col=tip)
        with b.detail(2):
            with b.at(0.42, -0.021, 0):
                PP.emblem(b, name, s=0.33, col=em, two=False)
            with b.at(0.42, 0.021, 0, rz=180):
                PP.emblem(b, name, s=0.33, col=em, two=False)


def build(b):
    H = 2.95
    with b.detail(1):
        b.beam((0, 0, -0.3), (0, 0, H), w=0.14, mat="timber")
        b.box(0.2, 0.2, 0.16, "planks", col="darkoak", z=H, taper=0.2)
        arm(b, 2.62, 20, L=1.0, name="fish", tip="blue", em="navy")
        arm(b, 2.34, 165, L=0.9, name="loaf", tip="red", em="brown")
        arm(b, 2.06, 262, L=0.95, name="anchor", tip="green", em="black")
    with b.detail(2):
        for a, r, s in ((30, 0.2, 0.26), (150, 0.19, 0.22), (255, 0.21, 0.3), (330, 0.17, 0.18)):
            with b.at(rz=a):
                b.stone(s, s * 0.8, s * 0.55, col="warm", y=-r, jitter=0.2)
        PH.gull(b, 0, 0, H + 0.15, rz=200)
        PP.tuft(b, -0.22, 0.2, 0, r=0.12, h=0.24)
        PP.tuft(b, 0.25, -0.2, 0, r=0.1, h=0.18, n=4)
