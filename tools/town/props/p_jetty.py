# timber jetty, 6 m: plank deck on stringers, two bents of raking piles with cross braces; repeats end to end along x
from kit import *
import parts as P
import parts_p as PP

L = 6.0
META = {"name": "Timber jetty 6 m", "kind": "prop", "group": "harbour", "clear": 3.3, "length": L, "axis": "x", "wobble": 0.0, "width": 2.4,
        "deck": 0.0, "bottom": -PP.DEEP, "notes": "deck level with the quay it leaves; piles go 7.5 m down; chain along x and finish with p_jetty_end"}


def build(b):
    PP.jetty(b, -L / 2, L / 2, bents=(-1.5, 1.5))
    with b.detail(2):
        PP.coil(b, -2.2, 0.75, PP.PAVE, r=0.24, turns=2)
