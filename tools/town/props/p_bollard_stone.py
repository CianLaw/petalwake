# a granite mooring post with a hawser made fast and its tail coiled beside it
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Stone bollard", "kind": "prop", "group": "harbour", "clear": 0.8}


def build(b):
    with b.detail(1):
        PP.bollard_stone(b, h=0.8, r=0.2, col="grey")
    with b.detail(2):
        PP.rope_turns(b, z=0.3, r=0.2, turns=3)
        PP.rope(b, [(0.2, 0.05, 0.34), (0.3, 0.16, 0.12), (0.42, 0.24, 0.05), (0.5, 0.26, 0.05)], r=0.022)
        PP.coil(b, 0.52, 0.3, 0, r=0.2, turns=2, tail=False)
        PP.tuft(b, -0.22, 0.14, 0, r=0.1, h=0.2, n=4)
