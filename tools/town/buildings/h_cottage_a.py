# Samphire Cottage: old Mother Garrow mends nets at the door and sells samphire by the bunch; the thatch is older than anyone can say.
# A low whitewashed rubble cottage, one room and a loft, under a thick sagging thatch with an eyebrow dormer and a stone gable
# stack; a wash-house and a walled drying yard behind. Whitewash, golden thatch, warm stone; accent blue.
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "Samphire Cottage", "kind": "cottage", "lot": (6.0, 7.0), "lean": (0.003, -0.002)}


def build(b):
    bd = b.body(5.2, 4.4, 2.5, mat="plaster", col="white")                   # x +-2.6, y 0 .. 4.4
    H.cuttable(bd.left, bd.right)
    RISE = 2.2 * math.tan(rad(52))
    P.door(bd.front, 1.75, w=0.95, h=1.95, col="blue", frame="timber", z=0.17, steps=1, lamp=True)
    P.window(bd.front, 0.6, 1.15, w=0.6, h=0.8, shutters="blue", lintel="timber")
    P.window(bd.front, 3.85, 1.0, w=1.0, h=1.05, bars=(2, 1), shutters="blue", box=True, lintel="timber")
    P.window(bd.right, 2.2, 1.0, w=0.8, h=1.0, shutters="blue", lintel="timber")
    P.window(bd.right, 2.2, 3.05, w=0.6, h=0.75, arch=0.3, lintel=None)
    P.window(bd.left, 3.3, 3.05, w=0.6, h=0.75, arch=0.3, lintel=None)
    P.window(bd.left, 3.4, 1.0, w=0.7, h=0.9, lintel="timber")
    P.door(bd.back, 1.2, w=0.85, h=1.85, col="blue", frame="timber", z=0.1)
    P.window(bd.back, 3.9, 1.05, w=0.8, h=0.9, lintel="timber")
    P.plinth(bd, h=0.5)
    P.exposed(bd.front, "corners", n=10)
    P.exposed(bd.right, "both", n=10)
    P.stones(bd.left, n=8, mat="masonry", col="warm", z1=1.6)
    P.ivy(bd.front, 4.95, 0.2, w=1.0, h=2.2, n=5, col="#86b866")
    bd.gable(ridge="x", pitch=52, mat="thatch", eave=0.5, verge=0.38, thick=0.34, course=0.62, lip=0.08, sag=0.16, barge=False)
    with b.detail(1):      # the block ridge, pegged down
        for i in range(8):
            xa = -2.95 + 5.9 * i / 8
            dz = -0.16 * (1 - ((xa + 0.37) / 2.95) ** 2)
            b.beam((xa, 2.2, 2.5 + RISE + 0.1 + dz), (xa + 0.72, 2.2, 2.5 + RISE + 0.1 + dz), w=0.8, h=0.2, mat="thatch", col=shade("#d9c49a", 0.9 + 0.1 * (i % 2)))
    P.dormer(b, 1.25, 0.55, 3.0, w=1.15, h=0.75, depth=1.4, face=0, kind="shed", roof="thatch", col="white")
    P.chimney(b, -2.15, 2.2, 3.4, 2.9, w=0.75, d=0.95, mat="masonry", col="warm", pots=2)
    lt = H.leanto(b, 1.25, 4.4, 2.5, 1.3, 1.8, rz=180, pitch=30, mat="masonry", col="warm", roof="shingle")
    P.door(lt.front, 0.85, w=0.75, h=1.6, col="blue", frame=None, z=0.05)
    P.window(lt.front, 1.9, 0.9, w=0.5, h=0.55, lintel="timber")
    # ------------------------------------------------------------------ the drying yard
    PC.garden_wall(b, (-2.85, 6.85), (-2.85, 4.4), h=1.0)
    PC.garden_wall(b, (2.85, 6.85), (-2.85, 6.85), h=1.0)
    PC.garden_wall(b, (2.85, 4.4), (2.85, 6.85), h=1.0)
    with b.detail(1):
        for (x, y) in ((-2.3, 5.0), (-0.3, 6.25)):
            b.beam((x, y, 0), (x, y, 2.15), w=0.08, mat="timber", col="greyoak")
    H.net_drape(b, (-2.3, 5.0, 2.1), (-0.3, 6.25, 2.1), drop=1.6, sag=0.15, col=H.NET_BROWN)
    H.pots(b, 2.2, 6.1, rz=0, n=3)
    P.barrel(b, 2.35, 4.9, r=0.28, h=0.8)
    # ------------------------------------------------------------------ the front
    P.bench(b, 1.35, -0.42, w=1.3)
    PC.flowers(b, -2.0, -0.4, w=1.0, d=0.45, n=6)
    H.net_heap(b, 0.15, -0.75, r=0.4, col=H.NET)
    H.basket(b, 2.35, -0.5, r=0.27, fill="#6fa86a")
    H.gull(b, -2.15, 2.2, 6.75, rz=40)
