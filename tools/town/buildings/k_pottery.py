# The pottery: pots are thrown in the house, dried on the racks in the yard and fired in the bottle kiln, whose brick shoulders stand over the wall like a great jug; the shop window on the street shows the best of each firing.
# A narrow jettied shop-house with its gable to the street, a lean-to clay store behind, and a walled cobbled yard on the right filled by the tall bottle-shaped kiln, with racks of pots along the walls.
# Warm rubble below peach plaster, tiles, red kiln brick banded with iron; accent teal (the glaze).
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_k as K

META = {"name": "The Pottery", "kind": "workshop", "lot": (9.0, 9.0)}

HX = -1.8                      # the house's middle
KX, KY = 2.2, 5.8               # the kiln
KILN = [(0.0, 1.6), (2.3, 1.56), (3.1, 1.46), (3.9, 1.28), (4.7, 1.05), (5.5, 0.88), (6.3, 0.8), (8.0, 0.76), (8.4, 0.84)]


def build(b):
    b.footprint(-4.3, 0.0, 4.38, 8.85, 8.6)
    # ------------------------------------------------------------------ the shop-house
    g = b.body(4.3, 6.4, 2.7, mat="masonry", col="warm", x=HX)
    P.plinth(g, h=0.5)
    for wl in g.walls:
        P.stones(wl, n=6, z0=0.55, z1=2.5)
    up = b.body(4.3, 6.7, 2.3, mat="plaster", col="peach", x=HX, y=3.05, z=2.7, floor="planks")
    PM.joists(g.front, 2.7, out=0.3)
    PM.shopfront(g.front, 1.5, z=0.0, w=2.0, h=1.45, riser=0.65, col="teal", lights=3, goods="pots")
    P.door(g.front, 3.45, w=0.95, h=2.0, z=0.17, col="teal", steps=1, lamp=True)
    P.window(up.front, 1.2, 0.8, shutters="teal", box=True)
    P.window(up.front, 3.1, 0.8, shutters="teal")
    K.sign(up.front, 4.05, 1.9, emblem="jug", col="teal", shape="shield")
    P.window(g.right, 2.0, 1.0, w=0.9, h=1.2)
    P.door(g.right, 4.7, w=0.9, h=1.95, z=0.12, col="teal", frame="timber")
    P.window(up.right, 2.3, 0.8, shutters="teal")
    P.window(up.right, 5.0, 0.8, shutters="teal")
    P.window(g.left, 3.2, 1.0, w=0.8, h=1.2)
    P.window(up.left, 3.3, 0.8, w=0.8)
    P.exposed(up.right, "corners")
    up.gable(ridge="y", pitch=48, mat="tiles", sag=0.1, eave=0.3, verge=0.35)
    PH.cuttable(up.front, up.back)
    PC.oculus(up.front, 2.15, 3.2, r=0.4)
    PC.oculus(up.back, 2.15, 3.2, r=0.4)
    P.chimney(b, HX - 1.35, 4.6, 5.3, 2.9, mat="brick", pots=2)
    lt = PH.leanto(b, HX, 6.4, 4.0, 2.2, 2.0, rz=180, pitch=24, mat="masonry", col="warm", roof="tiles", plinth=0.4)
    P.door(lt.left, 1.1, w=0.85, h=1.85, z=0.12, col="teal", frame="timber")
    P.window(lt.front, 2.0, 0.9, w=0.9, h=0.8)

    # ------------------------------------------------------------------ the yard and its walls
    fl = K.yard(b, 0.35, 0.1, 4.38, 8.85, mat="cobble")
    K.gate(b, (0.55, 0.24), (1.75, 0.24), col="teal", h=1.2)
    K.low_wall(b, (1.92, 0.24), (4.32, 0.24), h=1.0)
    K.low_wall(b, (4.15, 0.24), (4.15, 8.8), h=1.5)
    K.low_wall(b, (0.35, 8.62), (4.32, 8.62), h=1.5)

    # ------------------------------------------------------------------ the bottle kiln
    kiln = b.round(1.6, 8.4, profile=KILN, mat="brick", x=KX, y=KY, z=fl - 0.02, seg=18, depth=0.3)
    P.round_base(b, 1.6, h=0.45, out=0.1, ring=kiln, seg=18)
    P.door(kiln, 232, w=0.6, h=1.8, z=0.1, arch=0.3, col="brown", frame="stone")
    for i, deg in enumerate((20, 92, 164, 300)):
        hot = i in (0, 3)
        kiln.opening(deg, 0.3, 0.43, 0.66, arch=0.2, pane="glow" if hot else "paint", pane_col="#ffb060" if hot else K.SOOT, depth=0.3)
    P.stones(kiln, n=22, size=(0.28, 0.46), proud=0.05, z0=0.8, z1=6.0)
    with b.at(KX, KY, fl):
        with b.detail(1):
            for zz in (1.25, 2.3, 3.5, 4.7, 5.9, 7.3):
                rr = kiln.radius(zz) + 0.02
                b.revolve([(rr, zz - 0.05), (rr, zz + 0.05)], "metal", col="iron", seg=18)
            b.revolve([(0.84, 8.36), (0.93, 8.44), (0.93, 8.6), (0.7, 8.6)], "brick", seg=18)
            b.disc(0.7, "paint", col=K.SOOT, seg=18, z=8.57)
        b.smoke(0, 0, 9.0, 1.4)
    px, py, _ = PC.polar(1.9, 20, 0)
    b.lamp(KX + px, KY + py, 0.7, 0.8)

    # ------------------------------------------------------------------ racks of pots, and the potter's corner
    K.pot_rack(b, w=2.7, shelves=3, h=1.7, x=3.76, y=2.2, z=fl, rz=270)
    K.pot_rack(b, w=2.0, shelves=4, h=1.95, x=0.57, y=2.15, z=fl, rz=90, size=0.9)
    K.pot(b, 1.95, 1.15, fl, kind="urn", r=0.3, h=0.78, col="#c9764a", lod=1, seg=8)
    K.pot(b, 2.65, 0.95, fl, kind="crock", r=0.27, h=0.55, col="#3f8f8f", lod=1, seg=8)
    K.pot(b, 3.2, 1.2, fl, kind="vase", r=0.22, h=0.7, col="#e8d9b8", lod=1, seg=8)
    K.firewood(b, 1.2, 8.42, fl, w=1.5, h=1.05)
    with b.at(0.95, 3.9, fl):                       # the kick-wheel by the yard door
        with b.detail(2):
            b.revolve([(0.34, 0.1), (0.34, 0.18), (0.0, 0.18)], "ashlar", col="grey", seg=10)
            b.beam((0, 0, 0.0), (0, 0, 0.74), w=0.06, mat="metal", col="iron", caps=False)
            b.revolve([(0.2, 0.74), (0.2, 0.78), (0.0, 0.78)], "planks", col="greyoak", seg=10)
            b.box(0.3, 0.3, 0.42, "planks", col="darkoak", x=0.0, y=0.6)
        K.pot(b, 0, 0, 0.78, kind="bowl", r=0.14, h=0.13, col="#a59a8c")
    with b.detail(2):
        b.blob(0.42, 0.36, 0.24, mat="paint", col="#a59a8c", x=3.75, y=4.0, z=fl + 0.1, seg=7, rings=3, rough=0.25, bottom=False)      # wedged clay
    PC.cat(b, 3.0, 0.24, 1.1, rz=200)
