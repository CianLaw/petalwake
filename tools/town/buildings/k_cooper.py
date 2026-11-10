# The cooper's: casks for the brewhouse, the fish-yards and the dyers, made under the pent roof on the street where passers-by can see every state of one, from splayed staves over the cresset to the finished cask.
# A thatched gable-fronted house set back behind an open tiled working shed on two oak posts that runs right across its front; rubble below, ochre plaster in a timber frame above.
# Warm rubble, ochre plaster, dark oak, golden thatch; accent brown.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_k as K

META = {"name": "The Cooper's", "kind": "workshop", "lot": (5.5, 7.0)}

W, Y0, D = 4.6, 1.6, 4.8


def build(b):
    b.footprint(-2.5, 0.1, 2.5, 6.65, 7.6)
    g = b.body(W, D, 2.6, mat="masonry", col="warm", y=Y0 + D / 2)
    P.plinth(g, h=0.45, out=0.05)
    for wl in g.walls:
        P.stones(wl, n=5, z0=0.5, z1=2.5)
    up = b.body(W, D, 2.2, mat="plaster", col="ochre", y=Y0 + D / 2, z=2.6)
    P.door(g.front, 1.5, w=1.5, h=2.1, z=0.08, col="brown", double=True, frame="timber")
    P.window(g.front, 3.65, 1.0, w=1.0, h=1.1)
    P.window(up.front, 1.2, 0.8, shutters="brown", box=True)
    P.window(up.front, 3.6, 0.8, shutters="brown")
    P.timber_frame(up.front, posts=[0.0, 0.65, 1.75, 3.05, 4.15, W], rails=[0.07, 0.68, 2.12],
                   braces=[(0.08, 0.12, 0.6, 0.64), (W - 0.08, 0.12, W - 0.42, 0.64), (1.8, 0.12, 2.4, 0.64), (3.0, 0.12, 2.4, 0.64)])
    K.sign(up.front, W / 2, 1.85, emblem="barrel", col="brown", shape="round")
    for wl in (g.left, g.right):
        P.window(wl, 2.5, 1.0, w=0.8, h=1.1)
    P.timber_frame(up.left, posts=[0.0, 1.2, 2.4, 3.6, D], rails=[0.07, 1.1, 2.12], braces="k")
    P.timber_frame(up.right, posts=[0.0, 1.2, 2.4, 3.6, D], rails=[0.07, 1.1, 2.12], braces="k")
    P.door(g.back, 1.3, w=0.9, h=1.95, z=0.12, col="brown", frame="timber")
    P.window(g.back, 3.4, 1.0, w=0.9, h=1.1)
    P.window(up.back, W / 2, 0.8, shutters="brown")
    up.gable(ridge="y", pitch=50, mat="thatch", eave=0.18, verge=0.3, thick=0.3, course=0.55, lip=0.07, sag=0.08)
    PH.cuttable(up.front, up.back)
    P.window(up.front, W / 2, 2.2 + 0.5, w=0.7, h=0.9, shutters="brown")
    P.chimney(b, 1.15, 4.8, 5.4, 3.0, mat="brick", pots=1)

    # ------------------------------------------------------------------ the working shed across the front
    fl = K.yard(b, -2.5, 0.1, 2.5, Y0, mat="flagstone", h=0.08)
    PM.lean_to(b, W + 0.1, Y0 - 0.25, pitch=20, x=0.0, y=Y0, z=2.25, face=0, mat="tiles", eave=0.2, verge=0.1)
    for sx in (-1, 1):
        b.beam((sx * 2.12, 0.35, fl), (sx * 2.12, 0.35, 2.22), w=0.2, lod=0)
        with b.detail(1):
            b.beam((sx * 2.12, 0.35, 1.5), (sx * 1.45, 0.35, 2.12), w=0.1, caps=False)
            b.beam((sx * 2.12, 0.35, 2.14), (sx * 2.12, Y0, 2.6), w=0.12, h=0.14, caps=False)
    b.beam((-2.3, 0.35, 2.16), (2.3, 0.35, 2.16), w=0.18, h=0.2, lod=0)
    K.staves(b, -1.55, 0.8, fl, r=0.3, h=0.85)                      # raising a cask over the cresset
    with b.detail(2):
        b.blob(0.14, 0.14, 0.1, mat="glow", col="#ffb060", x=-1.55, y=0.8, z=fl + 0.12, seg=6, rings=2, rough=0.3, bottom=False)
    b.lamp(-1.55, 0.8, fl + 0.4, 0.7)
    K.barrel(b, -0.45, 0.62, fl, r=0.3, h=0.82, open_top=True)       # hooped, the head not yet in
    K.barrel(b, 1.7, 1.05, fl, r=0.31, h=0.85)
    with b.at(1.7, 1.05, fl + 0.9):                                 # a hoop waiting to be driven
        with b.at(rx=-82):
            K.hoop(b, r=0.3)
    K.barrel(b, 0.7, 0.55, fl, r=0.27, h=0.75, lying=True, rz=25)
    for i in range(3):                                               # hoops hung on the wall
        with b.at(1.05 + 0.02 * i, Y0 - 0.07 - 0.05 * i, 2.02 - 0.03 * i):
            K.hoop(b, r=0.3 - 0.04 * i)
    with b.detail(2):                                                # staves stacked crosswise to season
        for k in range(5):
            with b.at(-0.6, 1.25, fl + 0.06 * k, rz=90 * (k % 2)):
                for i in range(4):
                    b.box(0.1, 0.8, 0.05, "planks", col=shade("#e3cba0", b.r(0.85, 1.08)), x=(i - 1.5) * 0.2, bottom=True)
    K.barrel_stack(b, n=2, rows=2, x=1.7, y=-0.48, z=0.0, rz=90, r=0.3, h=0.8)
    K.bucket(b, -2.1, 1.3, fl)
    PC.cat(b, 0.7, 0.55, fl + 0.56, rz=10)
