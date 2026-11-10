# the end of the jetty, 3 m: tall mooring posts, a lantern, a ladder down to the boats, pots and a gull
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

L = 3.0
META = {"name": "Jetty end 3 m", "kind": "prop", "group": "harbour", "clear": 2.2, "length": L, "axis": "x", "wobble": 0.0, "width": 2.4,
        "deck": 0.0, "bottom": -PP.DEEP, "notes": "joins a p_jetty on its -x side; the open end is at +x"}


def build(b):
    Z = PP.PAVE
    PP.jetty(b, -L / 2, L / 2, bents=(-0.3, 1.2), tall=(1.2,), post_h=1.05)
    with b.detail(1):
        b.beam((1.2, -1.04, Z + 1.0), (1.2, -1.04, Z + 2.5), w=0.07, mat="timber")          # a lamp staff lashed to the corner post
        b.beam((1.2, -1.04, Z + 2.44), (1.2, -0.6, Z + 2.5), w=0.05, mat="timber")
        with b.at(1.2, -0.62, Z + 2.47):
            PP.lantern(b, s=0.26, h=0.38, sides=4, hang=0.12)
        with b.at(L / 2 + 0.03, 0.45, Z + 0.05, rz=90):
            PP.iron_ladder(b, z0=-5.6, z1=0.0, w=0.4, hoops=0.9)
    with b.detail(2):
        for sy in (-1, 1):
            PP.rope_turns(b, 1.2, sy * 1.02, Z + 0.45, r=0.15, turns=3, rr=0.02)
        PH.gull(b, 1.2, 1.02, Z + 1.07, rz=70)
        PH.pots(b, -0.5, 0.55, Z, rz=20, n=3)
        PH.rope_coil(b, 0.5, -0.6, Z, r=0.26)
        PH.fish_box(b, -1.0, -0.6, Z, rz=-12)
        PH.net_heap(b, 0.55, 0.35, Z, r=0.42)
