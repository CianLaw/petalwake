# a cast-iron quay bollard on its stone pad
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Iron bollard", "kind": "prop", "group": "harbour", "clear": 0.6}


def build(b):
    with b.detail(1):
        b.box(0.62, 0.62, 0.09, "ashlar", col="grey", taper=0.94, z=-0.01)
        PP.bollard_iron(b, z=0.08, h=0.66, r=0.14)
    with b.detail(2):
        PP.rope_turns(b, z=0.34, r=0.135, turns=2, rr=0.024)
        PP.rope(b, [(0.14, -0.04, 0.38), (0.34, -0.2, 0.2), (0.6, -0.42, 0.06)], r=0.024)
