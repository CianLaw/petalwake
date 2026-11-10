# the big bridge: a high hump-backed arch of 10 m, a cart's width between parapets, lanterns on the crown
from kit import *
import parts as P
import parts_p as PP
import parts_m as PM

SPAN, WIDTH, APP = 10.0, 4.6, 3.6
META = {"name": "Stone bridge, 10 m arch", "kind": "prop", "group": "walls", "clear": 9.0, "length": SPAN + 2 * APP, "axis": "x", "span": SPAN, "width": WIDTH, "road_width": 3.8,
        "hump": 2.01, "spring": -1.6, "bottom": -4.5, "wobble": 0.02,
        "notes": "road ends at z = 0 at x = +-8.6; the stream runs along y under the arch, which springs 1.6 m below the road ends and crowns 1.4 m above them"}


def build(b):
    br = PP.arch_bridge(b, span=SPAN, width=WIDTH, rise=3.0, spring=-1.6, approach=APP, ring=0.45, fill=0.16, parapet=0.9, pt=0.4, deep=4.5, nseg=16, nv=17, stones=16)
    hw, road = br["hw"], br["road"]
    with b.detail(1):
        for sy in (-1, 1):                                    # a pier and a lantern either side of the crown
            b.box(0.56, 0.56, 1.25, "ashlar", col="sand", x=0, y=sy * (hw - 0.2), z=road(0) - 0.05)
            b.box(0.66, 0.66, 0.1, "ashlar", col="stone", x=0, y=sy * (hw - 0.2), z=road(0) + 1.2, bottom=True)
            with b.at(0, sy * (hw - 0.2), road(0) + 1.3):
                PP.lantern(b, s=0.3, h=0.46, sides=4)
        for (x, z, r) in ((6.3, 0.6, 0.55), (7.0, 0.1, 0.5), (5.7, 1.2, 0.4), (6.6, 1.4, 0.34)):
            b.blob(r, 0.28, r * 0.9, mat="ivy", col=shade(PP.LEAF, b.r(0.85, 1.1)), x=x, y=-hw - 0.08, z=z, seg=6, rings=3, wind=0.25, rough=0.3)
    with b.detail(2):
        for (x, sy) in ((-8.2, -1), (8.1, 1), (8.3, -1), (-8.0, 1)):
            PP.tuft(b, x, sy * (hw + 0.12), 0, r=0.13, h=0.26)
        for x in (-3.4, 1.2, 4.6):
            PP.tuft(b, x, (hw - 0.5) * (1 if x > 0 else -1), road(x), r=0.07, h=0.12, n=4)
