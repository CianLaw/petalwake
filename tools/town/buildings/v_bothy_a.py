# The Shieling: a one-room bothy older than the village, where the herd-lasses once slept at the summer grazing;
# now it is let to whoever needs a roof. Low round-shouldered walls with turf on the wall-head and a green
# mound of a roof you could mistake for a hillock, a stovepipe poking out. Moss stone, turf, teal paint.
from kit import *
import parts as P
import parts_v as V
import parts_f as PF

META = {"name": "The Shieling", "kind": "house", "lot": (4.0, 5.0), "wobble": 0.055}


def build(b):
    b.footprint(-1.9, 0.0, 1.9, 4.9, 1.5)
    c = V.BBody(b, 3.3, 4.2, 1.5, col="moss", batter=0.1, depth=0.5)
    V.footing(c, h=0.36, boulders="flr", size=(0.5, 0.9))
    V.door(c.front, 1.65, w=0.8, h=1.3, col="teal")
    V.window(c.left, 2.6, 0.62, w=0.42, h=0.45, col="teal", shut="one")
    V.window(c.right, 1.5, 0.62, w=0.42, h=0.45)
    V.rubble(c.front, n=5, size=(0.3, 0.6)); V.rubble(c.left, n=8, size=(0.3, 0.6)); V.rubble(c.right, n=8, size=(0.3, 0.6)); V.rubble(c.back, n=7, size=(0.3, 0.6))
    V.wallhead(c, width=0.5, tufts=12)
    MZ = 1.5 + 0.16
    with b.at(0, 2.1, MZ, rz=90):
        m = V.mound_roof(b, c.td - 0.5, c.tw - 0.5, 1.55, rc=1.25, mat="thatch", col=V.TURF, thick=0.26, courses=3, lip=0.02, bulge=1.8, soffit_col="greyoak")
        V.mound_tufts(m, n=34, flowers=0.35)
    PF.stovepipe(b, 0.45, 3.1, MZ + 1.1, h=1.2)
    # outside
    with b.detail(1):
        for sx in (-0.45, 0.45):
            b.stone(0.3, 0.32, 0.4, mat="masonry", col="moss", lod=1, x=1.15 + sx, y=-0.42, z=0)
        b.box(1.25, 0.34, 0.06, "planks", col="greyoak", x=1.15, y=-0.42, z=0.4, bottom=True)
    V.peat_stack(b, -1.15, -0.45, w=1.0, d=0.55, h=0.7, turf=False, loose=4)
    PF.tool(b, -0.75, -0.1, 0, kind="spade")
