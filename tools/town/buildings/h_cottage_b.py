# Stair Cottage: the Pellow brothers live below and keep their nets above, where the damp cannot reach them; everyone sits on the forestair.
# A stone ground floor and a rose-washed net loft reached by a stone outside stair along the front, with a loading door and
# its little hoist; pantiled, a stack at each gable. Warm stone, rose plaster, terracotta; accent green.
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "Stair Cottage", "kind": "cottage", "lot": (6.0, 7.0)}


def build(b):
    g = b.body(5.4, 4.6, 2.4, mat="masonry", col="warm")                     # x +-2.7, y 0 .. 4.6
    up = b.body(5.4, 4.6, 2.2, mat="plaster", col="rose", z=2.4)
    H.cuttable(up.left, up.right)
    # ------------------------------------------------------------------ the forestair along the front, climbing to the right
    with b.at(-2.7, -0.55, 0, rz=-90):
        PC.outside_stair(b, n=12, w=1.0, rise=0.2, run=0.27, landing=1.05, rail="balusters", rail_sides="r")
    P.door(up.front, 3.75, w=0.9, h=1.9, z=0.03, col="green", frame="timber", lamp=True)
    P.door(g.front, 4.85, w=0.85, h=1.9, col="green", frame="stone", z=0.1)
    P.window(g.front, 0.75, 1.3, w=0.7, h=0.85, lintel="stone")
    H.loading_door(up.front, 1.25, 0.12, w=1.0, h=1.35, col="green", bar=False)
    P.window(up.front, 2.6, 0.85, w=0.6, h=0.85, shutters="green")
    H.hoist(b, -1.45, 0.0, 4.42, out=0.85, load="net", drop=1.35, brace=False, back=0.3)
    H.floats(up.front, 4.85, 1.75, n=4)
    # ------------------------------------------------------------------ gables and back
    P.window(g.right, 2.3, 1.05, w=0.8, h=1.0, lintel="stone")
    P.window(up.right, 2.3, 0.8, w=0.7, h=0.95, shutters="green")
    P.window(up.right, 2.3, 2.75, w=0.5, h=0.6, lintel=None)
    P.window(g.left, 2.3, 1.05, w=0.8, h=1.0, lintel="stone")
    P.window(up.left, 2.3, 0.8, w=0.7, h=0.95, shutters="green", box=True)
    P.door(g.back, 1.3, w=0.85, h=1.9, col="green", frame="timber", z=0.1)
    P.window(g.back, 3.9, 1.05, w=0.8, h=1.0, lintel="stone")
    P.window(up.back, 1.5, 0.8, w=0.7, h=0.95)
    P.window(up.back, 3.9, 0.8, w=0.7, h=0.95, shutters="green")
    P.plinth(g, h=0.4)
    P.quoins(g, corners="rb", z0=0.4, col="sand")
    P.exposed(up.front, "corners", n=8)
    up.gable(ridge="x", pitch=48, mat="tiles", eave=0.3, verge=0.14, sag=0.1)
    P.chimney(b, -2.3, 2.3, 5.0, 2.9, w=0.6, d=0.8, mat="masonry", col="warm", pots=2)
    P.chimney(b, 2.3, 2.3, 5.0, 2.5, w=0.6, d=0.8, mat="masonry", col="warm", pots=1)
    lt = H.leanto(b, -1.2, 4.6, 2.4, 1.2, 1.8, rz=180, pitch=28, mat="planks", col=H.TAR_OLD, roof="tiles", plinth=0.3)
    P.door(lt.front, 0.8, w=0.7, h=1.55, col="green", frame=None, z=0.05)
    H.battens(lt.front, col=H.TAR_OLD, z0=0.3)
    # ------------------------------------------------------------------ nets in the yard, pots under the stair
    with b.detail(1):
        for (x, y) in ((0.4, 5.3), (2.6, 6.5)):
            b.beam((x, y, 0), (x, y, 2.2), w=0.08, mat="timber", col="greyoak")
    H.net_drape(b, (0.4, 5.3, 2.15), (2.6, 6.5, 2.15), drop=1.6, sag=0.15, col=H.NET)
    H.fish_rack(b, -1.4, 6.3, w=1.8, h=1.6, rows=2, n=6)
    H.pots(b, 2.35, -0.75, rz=90, n=3)
    H.rope_coil(b, 1.95, -0.2, r=0.26)
    PC.cat(b, 0.9, -0.55, 2.4, rz=20, col="!#e8e2d4")
    H.gull(b, 2.3, 2.3, 7.95, rz=300)
