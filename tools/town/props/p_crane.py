# a harbour hand-crane: stone drum, timber post and jib, an iron crank winch, a cask swinging in its sling
import math
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Harbour hand-crane", "kind": "prop", "group": "harbour", "clear": 2.2, "wobble": 0.015, "reach": 3.3,
        "notes": "the jib reaches 3.3 m toward -y (set it at the quay edge with -y over the water)"}


def build(b):
    tip = (0.0, -3.3, 4.5)
    head = (0.0, 0.0, 3.7)
    with b.detail(1):
        b.revolve([(1.0, -0.3), (1.0, 0.36), (0.94, 0.5), (0.0, 0.5)], "masonry", col="grey", seg=12)
        b.beam((0, 0, 0.4), head, w=0.3, mat="timber")
        b.beam((0, -0.1, 1.5), tip, w=0.2, h=0.22, mat="timber")                                   # the jib
        b.beam(head, tip, w=0.07, mat="metal", col="iron")                                         # the stay
        b.beam((0, 0.14, 3.5), (0, 0.95, 0.55), w=0.07, mat="metal", col="iron")                   # back stay
        for sx in (-1, 1):                                                                         # winch cheeks and crank wheels
            b.box(0.07, 0.5, 0.75, "planks", col="darkoak", x=sx * 0.34, y=0.42, z=0.85, bottom=True)
            with b.at(sx * 0.46, 0.42, 1.25, ry=90):
                PP.torus(b, 0.36, 0.02, col="iron", seg=10, n=3)
                for k in range(4):
                    a = math.pi * k / 4
                    b.beam((0.36 * math.cos(a), 0.36 * math.sin(a), 0), (-0.36 * math.cos(a), -0.36 * math.sin(a), 0), w=0.022, mat="metal", col="iron", caps=False)
                b.tube((0.3, 0.0, 0.0), (0.3, 0.0, sx * 0.16), r=0.018, mat="planks", col="#c9a57a", n=4)
        b.tube((-0.36, 0.42, 1.25), (0.36, 0.42, 1.25), r=0.11, mat="planks", col="#c9a57a", n=7, caps=True)
        PP.barrel(b, 0.0, -3.3, 1.2, r=0.3, h=0.78)
    with b.detail(2):
        for z in (1.0, 2.2, 3.4):
            b.box(0.34, 0.34, 0.06, "metal", col="iron", z=z, top=False)
        with b.at(0, 0.42, 1.25, ry=90):
            PP.rope_turns(b, z=-0.18, r=0.11, turns=6, rr=0.02)
        PP.rope(b, [(0.0, 0.32, 1.33), (0.0, 0.05, 3.72), tip, (0.0, -3.3, 2.5)], r=0.016)
        b.box(0.12, 0.12, 0.16, "metal", col="iron", x=tip[0], y=tip[1], z=tip[2] - 0.2)           # sheave
        b.box(0.1, 0.1, 0.18, "metal", col="iron", x=0, y=-3.3, z=2.34)                            # hook block
        for sx in (-1, 1):
            PP.rope(b, [(0, -3.3, 2.36), (sx * 0.3, -3.3, 1.95), (sx * 0.31, -3.3, 1.25)], r=0.014)
            PP.rope(b, [(0, -3.3, 2.36), (0, -3.3 + sx * 0.3, 1.95), (0, -3.3 + sx * 0.31, 1.25)], r=0.014)
        b.revolve([(0.31, 1.24), (0.33, 1.3)], "cloth", col=PP.HEMP, seg=9)
        with b.at(0, -3.3, 0):
            b.revolve([(0.31, 1.24), (0.33, 1.3)], "cloth", col=PP.HEMP, seg=9)
        PP.crate(b, 1.25, -0.6, 0, w=0.6, rz=12)
        PP.coil(b, -1.3, -0.4, 0, r=0.28, turns=2)
        PP.tuft(b, 0.9, 0.7, 0, r=0.11, h=0.2)
