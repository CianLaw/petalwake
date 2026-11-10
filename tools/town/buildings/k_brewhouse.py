# The brewhouse: malt goes up by the hoist in the gable, the copper boils under the louvred vent on the ridge (which breathes steam all day), and the casks come out of the cellar wing to be stacked in the yard for the dray.
# A tall gable-fronted block (rubble below, warm brick above) with stacked loading doors and a ridge ventilator, a low cellar wing leaning on its right side, a round brick boiler stack behind, and a yard piled high with barrels.
# Warm rubble and red brick, terracotta tiles, slate on the vent; accent mustard.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_k as K

META = {"name": "The Brewhouse", "kind": "workshop", "lot": (11.0, 10.0)}

HX, HW, HD = -1.9, 6.2, 8.0             # the main block: x -5.0 .. 1.2
RX = HX + HW / 2


def build(b):
    b.footprint(-5.3, 0.0, 5.36, 9.75, 9.0)
    # ------------------------------------------------------------------ the brewhouse
    g = b.body(HW, HD, 3.0, mat="masonry", col="warm", x=HX)
    P.plinth(g, h=0.7, out=0.08)
    P.quoins(g, z0=0.7, col="sand")
    for wl in g.walls:
        P.stones(wl, n=8, z0=0.75, z1=2.8)
    up = b.body(HW, HD, 2.8, mat="brick", x=HX, z=3.0)
    P.band(g, 2.9, h=0.2, out=0.07, col="sand")
    P.door(g.front, HW / 2, w=2.0, h=2.6, arch=0.75, col="mustard", double=True, lamp=True)
    for u in (0.95, HW - 0.95):
        P.window(g.front, u, 1.15, w=0.85, h=1.25, shutters="mustard")
        P.window(up.front, u, 0.9, w=0.85, h=1.25, arch=0.22)
    PH.loading_door(up.front, HW / 2, 0.15, w=1.3, h=1.8, col="mustard")
    K.sign(g.front, 1.7, 2.75, emblem="mug", col="mustard", shape="round")
    for u in (1.5, 4.0, 6.5):
        P.window(g.left, u, 1.15, w=0.85, h=1.25)
        PH.louvre(up.left, u, 1.0, w=0.9, h=1.0)
    P.window(g.right, 1.6, 1.15, w=0.85, h=1.25, shutters="mustard")
    for u in (1.2, 3.4, 5.6):
        PH.louvre(up.right, u, 1.55, w=0.9, h=0.9)
    P.door(g.back, 1.6, w=1.0, h=2.05, z=0.18, col="mustard", steps=1)
    P.window(g.back, 4.4, 1.15, w=0.85, h=1.25)
    for u in (1.6, 4.4):
        P.window(up.back, u, 0.9, w=0.85, h=1.25, arch=0.22)
    rise = up.gable(ridge="y", pitch=45, mat="tiles", sag=0.12, eave=0.28, verge=0.3)
    PH.cuttable(up.front, up.back)
    PH.loading_door(up.front, HW / 2, 2.95, w=1.05, h=1.45, col="mustard", sill=False)
    P.window(up.back, HW / 2, 3.1, w=0.8, h=1.2, arch=0.3)
    K.hoist(b, HX, 0.0, 5.8 + rise - 0.75, out=1.05, face=0, rope=4.9, load="barrel", brace=False, back=0.25)
    K.ridge_vent(b, HX, 4.7, 5.8 + rise - 0.12, L=3.2, w=1.35, h=1.0, drop=0.7, ridge="y", roof="slate")
    b.smoke(HX, 4.7, 5.8 + rise + 1.9, 1.0)

    # ------------------------------------------------------------------ the cellar wing
    lt = PH.leanto(b, RX, 5.6, 4.8, 3.7, 2.6, rz=90, pitch=23, mat="masonry", col="warm", roof="tiles", plinth=0.6)
    P.door(lt.left, 2.0, w=1.7, h=2.2, arch=0.5, col="mustard", double=True)
    P.window(lt.front, 1.3, 1.1, w=0.85, h=1.1)
    P.window(lt.front, 3.5, 1.1, w=0.85, h=1.1)
    P.ivy(lt.front, 2.4, 0.3, w=1.4, h=2.2, n=7)

    # ------------------------------------------------------------------ the boiler stack behind
    b.box(1.7, 1.5, 1.3, "masonry", col="warm", x=3.2, y=8.95)
    b.box(1.7, 1.5, 3.0, "masonry", col=shade("warm", 0.85), x=3.2, y=8.95, z=-3.0, top=False)
    K.round_stack(b, 3.2, 8.95, 1.3, h=9.6, r0=0.68, r1=0.42, seg=12, bands=(0.3, 0.6, 0.86), strength=1.4)
    K.firewood(b, 0.6, 8.05, 0, w=1.9, h=1.2, rz=180)
    K.coal_heap(b, 1.7, 9.0, 0, r=0.6, h=0.4)

    # ------------------------------------------------------------------ the barrel yard
    fl = K.yard(b, RX, 0.1, 5.36, 3.2, mat="cobble")
    K.barrel_stack(b, n=4, x=RX + 1.05, y=1.72, z=fl, rz=0, deep=2, r=0.34, h=0.9)
    K.barrel(b, 3.55, 2.75, fl, r=0.33, h=0.85)
    K.barrel(b, 4.25, 2.8, fl, r=0.33, h=0.85)
    K.barrel(b, 3.9, 2.72, fl + 0.85, r=0.3, h=0.78)
    K.barrel(b, 3.4, 0.55, fl, r=0.34, h=0.9, lying=True, rz=70)
    K.handcart(b, 4.4, 1.35, fl, rz=165, load="barrels")
    K.low_wall(b, (5.14, 0.25), (5.14, 3.2), h=1.1, t=0.3)
    PC.cat(b, 5.14, 2.4, 1.2, rz=260)
