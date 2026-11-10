# a small hump-backed stone bridge: one arch of 6 m, cobbled road between parapets, clear water way beneath
from kit import *
import parts as P
import parts_p as PP

SPAN, WIDTH, APP = 6.0, 3.4, 3.0
META = {"name": "Stone bridge, 6 m arch", "kind": "prop", "group": "walls", "clear": 6.3, "length": SPAN + 2 * APP, "axis": "x", "span": SPAN, "width": WIDTH, "road_width": 2.72,
        "hump": 1.3, "spring": -1.2, "bottom": -4.0, "wobble": 0.02,
        "notes": "road ends at z = 0 at x = +-6; the stream runs along y under the arch, which springs 1.2 m below the road ends and crowns 0.8 m above them"}


def build(b):
    br = PP.arch_bridge(b, span=SPAN, width=WIDTH, rise=2.0, spring=-1.2, approach=APP, ring=0.36, parapet=0.85, pt=0.34, deep=4.0, nseg=12, nv=13)
    hw, road = br["hw"], br["road"]
    with b.detail(1):
        for (x, z, r) in ((-4.3, 0.5, 0.5), (-4.8, 0.05, 0.42), (-3.9, 0.95, 0.36)):          # ivy over one shoulder
            b.blob(r, 0.26, r * 0.9, mat="ivy", col=shade(PP.LEAF, b.r(0.85, 1.1)), x=x, y=-hw - 0.08, z=z, seg=6, rings=3, wind=0.25, rough=0.3)
    with b.detail(2):
        for (x, sy) in ((-5.6, -1), (5.5, 1), (5.7, -1), (-5.4, 1)):
            PP.tuft(b, x, sy * (hw + 0.12), 0, r=0.13, h=0.26)
        for x in (-2.2, 0.4, 2.9):
            PP.tuft(b, x, (hw - 0.42) * (1 if x > 0 else -1), road(x), r=0.07, h=0.12, n=4)
