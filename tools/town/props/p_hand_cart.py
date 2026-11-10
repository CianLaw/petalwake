# a hand cart at rest on its legs: flat bed with low rails, long shafts, a load of sacks and a cask
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Hand cart", "kind": "prop", "group": "square", "clear": 1.7, "wobble": 0.015}


def build(b):
    with b.at(-0.5, 0, 0):           # (cart and shafts together are centred on the origin)
        _build(b)


def _build(b):
    zb = 0.66
    with b.detail(1):
        PP.planking(b, -0.9, 0.8, -0.44, 0.44, zb, along="x", pw=0.22, t=0.04, col="#c9b08a")
        for sy in (-1, 1):
            b.beam((-0.95, sy * 0.44, zb - 0.07), (2.0, sy * 0.4, zb + 0.06), w=0.07, h=0.08, mat="timber")       # the shafts run right through
            PP.board(b, (-0.9, sy * 0.46, zb + 0.13), (0.8, sy * 0.46, zb + 0.13), w=0.14, t=0.025, col="greyoak", up=(0, 1, 0))
            for x in (-0.85, 0.0, 0.75):
                b.beam((x, sy * 0.46, zb), (x, sy * 0.46, zb + 0.24), w=0.04, mat="timber", caps=False)
            with b.at(-0.1, sy * 0.56, 0.5):
                PP.wheel(b, r=0.5, w=0.065, spokes=10, col="darkoak")
            b.beam((0.78, sy * 0.4, zb - 0.06), (0.86, sy * 0.44, 0.0), w=0.055, mat="timber")
        b.beam((-0.1, -0.6, 0.5), (-0.1, 0.6, 0.5), w=0.07, mat="timber")
        b.beam((2.0, -0.44, zb + 0.06), (2.0, 0.44, zb + 0.06), w=0.05, mat="planks", col="#c9a57a")
        PP.board(b, (-0.9, -0.44, zb + 0.13), (-0.9, 0.44, zb + 0.13), w=0.14, t=0.025, col="greyoak", up=(1, 0, 0))
        PP.sack(b, -0.5, 0.1, zb, r=0.3)
        PP.barrel(b, 0.4, -0.08, zb, r=0.24, h=0.58)
    with b.detail(2):
        PP.sack(b, -0.42, -0.14, zb + 0.34, r=0.26, col="#cdbb92")
        PP.sack(b, -0.05, 0.2, zb, r=0.24, col="#e0d2ae")
        PP.rope(b, [(0.7, -0.47, zb + 0.2), (0.4, -0.3, zb + 0.5), (0.4, 0.14, zb + 0.5), (0.7, 0.47, zb + 0.2)], r=0.012)
        PP.tuft(b, 1.2, 0.6, 0, r=0.11, h=0.2)
