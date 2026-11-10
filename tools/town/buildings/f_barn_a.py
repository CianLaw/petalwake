# The Tithe Barn: the great barn of the middle meadows, so old its ridge sags like a hammock; at harvest every cart on the island queues at its porch.
# Massing: a long low range under one huge tiled roof with a swaybacked ridge, a gabled wagon porch with double doors tall enough for a loaded
#          cart, buttressed stone walls with boarded upper parts, a hoist door in one gable.
# Materials: warm rubble below tarred weatherboard, mossy terracotta tiles, oak; accent teal.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_f as F

META = {"name": "The Tithe Barn", "kind": "barn", "lot": (14.0, 9.0)}

X0, X1, Y0, Y1 = -6.3, 6.3, 2.4, 8.25
G, U = 1.5, 2.5
TAR = "#8a7a6a"
PX, PW, PY = -1.0, 4.2, 1.1               # the porch: centre, width, front


def build(b):
    w, d, cx, cy = X1 - X0, Y1 - Y0, 0.0, (Y0 + Y1) / 2
    g = b.body(w, d, G, mat="masonry", col="warm", x=cx, y=cy)
    P.plinth(g, h=0.4, out=0.08)
    u = b.body(w, d, U, mat="planks", col=TAR, x=cx, y=cy, z=G)
    P.band(u, 0.0, h=0.16, out=0.06, mat="timber", col="darkoak")
    # slits in the boarding, in rows that share their cuts
    for uu in (1.2, 2.4, 9.6, 10.8, 12.0):
        F.slit(u.front, uu, 0.6, w=0.13, h=1.2)
    for uu in (1.2, 2.6, 4.0, 8.6, 10.0, 11.4):
        F.slit(u.back, uu, 0.6, w=0.13, h=1.2)
    for uu in (3.3, 9.3):
        P.window(g.back, uu, 0.5, w=0.7, h=0.7, lintel="timber")
    PH.cuttable(u.left, u.right)
    rise = u.gable(ridge="x", pitch=50, mat="tiles", col="#f2ead8", sag=0.42, eave=0.42, verge=0.4)
    PH.loading_door(u.left, d / 2, U + 0.35, w=1.1, h=1.5, col="teal", bar=False)
    PM.hoist(b, X0, cy, G + U + 2.45, face=270, out=0.5, rope=3.2, load="sack")
    P.window(u.right, d / 2, U + 0.6, w=0.7, h=1.0, lintel="timber", shutters="teal")
    PC.oculus(u.right, d / 2, U + rise * 0.72, r=0.22)
    P.window(g.right, 1.5, 0.45, w=0.6, h=0.7, lintel="timber")
    P.window(g.left, d - 1.5, 0.45, w=0.6, h=0.7, lintel="timber")
    PM.weathercock(b, 3.2, cy, G + U + rise - 0.3, h=1.5, shape="cock")

    # ---- the wagon porch
    pb = b.body(PW, Y0 - PY, G + U, mat="planks", col=TAR, x=PX, y=(PY + Y0) / 2)
    P.plinth(pb, h=G, out=0.07)
    F.barn_doors(pb.front, PW / 2, w=3.2, h=3.6, col="teal", swing=(8.0, 40.0))
    prise = pb.gable(ridge="y", pitch=50, mat="tiles", col="#f2ead8", eave=0.3, verge=0.3)
    b.gable_roof(PW, 2.6, 50, mat="tiles", col="#f2ead8", x=PX, y=Y0 + 1.3, z=G + U, ridge="y", eave=0.3, verge=0.0, barge=False)      # carry its ridge back into the big roof
    PC.oculus(pb.front, PW / 2, G + U + prise * 0.45, r=0.26)
    P.lantern(pb.right, 0.5, 2.2)

    # ---- buttresses
    for x in (X0 + 0.9, -4.2, 2.6, 4.6, X1 - 0.9):
        with b.at(x, Y0, 0.0):
            PC.buttress(b, w=0.6, d=0.6, h=2.9)
    for x in (X0 + 0.9, -3.0, 0.4, 3.4, X1 - 0.9):
        with b.at(x, Y1, 0.0, rz=180):
            PC.buttress(b, w=0.6, d=0.5, h=2.9)

    # ---- harvest: a cart at the porch, hay, a ladder to the hoist door, the barn cat
    F.cart(b, 4.0, 0.95, 0.0, rz=-90, L=2.2, W=1.15, load="hay", paint="teal")
    F.hay(b, 1.6, 1.9, 0.0, rx=0.7, ry=0.55, h=0.7, lod=2)
    F.tool(b, 1.9, 2.3, 0.0, kind="fork", lean=0.06)
    F.ladder_to(b, (X0 - 0.42, cy + 1.25, 0.0), (X0 - 0.06, cy + 0.95, G + U + 0.3), w=0.42)
    for (x, y) in ((-4.6, 1.75), (-5.2, 1.6), (-4.9, 2.05)):
        P.sack(b, x, y, 0.0, r=0.28)
    P.barrel(b, -5.75, 2.0, 0.0, r=0.3, h=0.85)
    F.cat(b, 1.15, 1.5, 0.0, rz=250)
    F.meadow(b, -6.2, 0.6, -3.6, 1.2, n=5, spread=(0.3, 0.45))
    F.meadow(b, 5.2, 0.5, 6.3, 2.0, n=3, spread=(0.3, 0.42))
