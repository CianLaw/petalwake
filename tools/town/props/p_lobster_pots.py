# lobster pots stacked on the quay with their marker buoys, a coil of line, and a gull that knows what is in them
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

META = {"name": "Lobster pots", "kind": "prop", "group": "harbour", "clear": 1.7}


def build(b):
    PH.pots(b, -0.35, 0.1, 0, rz=8, n=5)
    PH.pots(b, 0.75, -0.35, 0, rz=-64, n=3)
    PH.pot(b, 0.2, -0.95, 0, rz=30)
    PH.buoy(b, -1.15, -0.55, 0, col="!#b5433a", flag="stripe_yellow")
    PH.buoy(b, 1.35, 0.55, 0, col="!#d9a431", stripe="!#2f4470", s=0.9)
    PH.rope_coil(b, -0.9, -1.15, 0, r=0.26)
    PH.gull(b, -0.35, 0.1, 0.62, rz=200)
    with b.detail(2):
        PP.rope(b, [(-1.15, -0.55, 0.3), (-1.05, -0.9, 0.05), (-0.9, -1.1, 0.12)], r=0.014)
        PP.tuft(b, 1.2, -1.0, 0, r=0.11, h=0.2)
