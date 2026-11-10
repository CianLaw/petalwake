# The Halfway Mug: the roadside inn between the two towns; carts rattle in under the arch at dusk and nobody leaves before the second pie.
# Massing: a long two-storey range on the road with a carriage arch through its right end into a cobbled stable yard; a stable wing with
#          half-doors and a hay loft down the yard's left side, a high wall round the rest; dormers, two stacks, a sign beam over the road.
# Materials: warm rubble ground floor, peach plaster and oak above, terracotta tiles, cobbles; accent navy.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_k as PK
import parts_l as PL
import parts_m as PM
import parts_f as F

META = {"name": "The Halfway Mug", "kind": "inn", "lot": (13.0, 11.0)}

X0, X1, FY, RY = -6.0, 6.0, 0.3, 5.3        # the road range
G, U = 3.4, 2.6
AX, AW, AH, AA = 3.4, 3.0, 3.2, 1.0          # the arch: centre, width, height, curve
SX1, SY1 = -2.4, 10.5                        # the stable wing's yard face and back end


def build(b):
    w, d, cy = X1 - X0, RY - FY, (FY + RY) / 2
    # ---- ground floor of the range, with the arch right through it
    g = b.body(w, d, G, mat="masonry", col="warm", x=0, y=cy)
    P.plinth(g, h=0.5)
    g.front.opening(AX - X0, 0.0, AW, AH, arch=AA, pane=None)
    g.back.opening(X1 - AX, 0.0, AW, AH, arch=AA, pane=None)
    PC.arch_stones(g.front, AX - X0, 0.0, AW, AH, AA, jambs=True)
    PC.arch_stones(g.back, X1 - AX, 0.0, AW, AH, AA)
    with b.at(AX, FY, 0.0):
        PC.vault(b, AW, AH, AA, d, floor="cobble")
    P.door(g.front, 4.4, w=1.1, h=2.25, arch=0.4, col="navy", z=0.25, steps=1, lamp=True)
    for u in (1.4, 2.9, 6.3):
        P.window(g.front, u, 1.1, w=0.95, h=1.4, shutters="navy", box=u == 2.9)
    P.window(g.front, 11.45, 1.1, w=0.5, h=1.4)
    P.door(g.back, 5.6, w=0.95, h=2.1, col="navy", frame="timber", z=0.1)
    P.window(g.back, 7.4, 1.1, w=0.95, h=1.4)
    P.window(g.left, 2.5, 1.1, w=0.95, h=1.4)
    P.window(g.right, 2.5, 1.1, w=0.8, h=1.4)
    P.lantern(g.front, AX - X0 - AW / 2 - 0.4, 2.5)

    # ---- upper floor: plaster and oak
    up = b.body(w, d, U, mat="plaster", col="peach", x=0, y=cy, z=G)
    fcols = (1.4, 2.9, 4.4, 6.3, 8.7, 10.1)
    for u in fcols:
        P.window(up.front, u, 0.9, w=0.85, h=1.2, shutters="navy" if u not in (4.4, 8.7) else None, lintel=None)
    for u in (1.9, 3.3, 5.6, 7.4):
        P.window(up.back, u, 0.9, w=0.85, h=1.2, lintel=None)
    P.window(up.left, 2.5, 0.9, w=0.85, h=1.2, lintel=None)
    P.window(up.right, 2.5, 0.9, w=0.85, h=1.2, lintel=None)
    P.timber_frame(up.front, posts=[0.0, 0.7, 2.15, 3.65, 5.35, 7.2, 8.0, 9.4, 10.8, w], rails=[0.0, 0.75, U],
                   braces=[(0.0, U, 0.7, 0.75), (w, U, 10.8, 0.75), (7.2, U, 8.0, 0.75)])
    P.timber_frame(up.back, posts=[0.0, 1.2, 2.6, 4.0, 4.9, 6.5, 8.1, w], rails=[0.0, 0.75, U], braces=[(0.0, U, 1.2, 0.75), (4.0, 0.75, 4.9, U)])
    for wl in (up.left, up.right):
        P.timber_frame(wl, posts=[0.0, 1.0, 1.9, 3.1, 4.0, d], rails=[0.0, 0.75, U], braces=[(0.0, U, 1.0, 0.75), (d, U, 4.0, 0.75)])
    PM.joists(g.front, G + 0.02, out=0.16, u0=0.2, u1=w - 0.2, n=16)
    rise = up.gable(ridge="x", pitch=45, mat="tiles", sag=0.16, eave=0.3, verge=0.27)
    for x in (-3.9, 0.4):
        P.dormer(b, x, FY + 1.05, G + U + 0.8, w=1.15, h=1.0, depth=1.5, col="peach", shutters=None)
    PC.stack(b, X0 + 0.75, cy, G + U + rise - 1.1, 2.5, w=0.8, d=0.62, mat="masonry", col="warm", flues=2)
    PM.stack(b, 1.5, cy + 1.3, G + U + 0.6, 3.3, w=0.9, d=0.7, mat="brick", pots=3)

    # ---- the sign beam over the road, the mounting block, benches and a trough at the door
    su = 7.6
    P.sign(up.front, su, 1.72, emblem="mug", col="navy", board="ivory", out=1.2, w=0.92, h=0.78)
    xs = X0 + su
    with b.detail(1):
        b.beam((xs, FY + 0.05, G + 1.92), (xs, FY - 1.25, G + 1.92), w=0.2, h=0.22, mat="timber", col="darkoak", up=(0, 0, 1))
        b.beam((xs, FY, G + 1.1), (xs, FY - 0.7, G + 1.8), w=0.12, mat="timber", col="darkoak", caps=False)
        b.beam((xs, FY, G + 2.5), (xs, FY - 1.1, G + 2.04), w=0.035, mat="metal", col="iron", caps=False)
    with b.detail(1):
        for i in range(3):
            b.box(0.42, 0.72, 0.28 * (i + 1), "ashlar", col="stone", x=0.2 + 0.42 * i, y=FY - 0.4, z=0.0)
        b.box(0.5, 0.72, 0.84, "ashlar", col="stone", x=1.5, y=FY - 0.4, z=0.0)
    P.bench(b, -3.55, FY - 0.3, 0.0, w=1.5)
    PK.trough(b, -4.95, FY - 0.36, 0.0, w=1.3, d=0.5, h=0.48)
    P.barrel(b, -0.35, FY - 0.36, 0.0, r=0.28, h=0.8)

    # ---- the stable wing down the left of the yard
    sw = b.body(SX1 - X0, SY1 - RY, 2.6, mat="masonry", col="warm", x=(X0 + SX1) / 2, y=(RY + SY1) / 2)
    P.plinth(sw, h=0.4, out=0.06)
    for u, tp in ((1.0, "open"), (2.65, "ajar"), (4.3, "shut")):
        F.half_door(sw.right, u, w=1.05, h=2.0, z=0.06, col="navy", top=tp)
    P.window(sw.left, 1.3, 1.5, w=0.6, h=0.5, lintel="timber")
    P.window(sw.left, 4.0, 1.5, w=0.6, h=0.5, lintel="timber")
    PH.cuttable(sw.back)
    srise = sw.gable(ridge="y", pitch=45, mat="tiles", eave=0.26, verge=0.2, sag=0.06)
    PH.loading_door(sw.back, (SX1 - X0) / 2, 2.65, w=0.75, h=1.15, col="navy", sill=False, bar=False)
    PM.hoist(b, (X0 + SX1) / 2, SY1, 2.6 + srise - 0.25, face=180, out=0.22, rope=0.9, load=None)
    P.window(sw.back, (SX1 - X0) / 2, 1.0, w=0.7, h=0.9, lintel="timber")

    # ---- the yard: cobbles, the wall round it, a trough and pump, a cart, casks by the back door
    PK.yard(b, SX1, RY, X1, SY1, mat="cobble")
    PC.garden_wall(b, (X1, SY1), (SX1, SY1), h=2.1)
    PC.garden_wall(b, (X1, RY), (X1, SY1), h=2.1)
    PK.trough(b, 5.25, 8.3, 0.06, rz=90, w=1.4, d=0.55, h=0.5)
    PL.pump(b, 5.3, 9.6, 0.06, rz=270)
    F.cart(b, 1.9, 9.25, 0.06, rz=90, L=2.0, W=1.1, load="hay", paint="navy")
    F.hay(b, -1.75, 9.9, 0.06, rx=0.7, ry=0.6, h=0.8, lod=2)
    F.tool(b, -2.3, 9.2, 0.06, kind="fork", rz=90, lean=0.05)
    for (x, y, r_) in ((-0.5, 5.75, 0.3), (-1.1, 5.7, 0.28), (-0.8, 6.25, 0.27)):
        P.barrel(b, x, y, 0.06, r=r_, h=0.82)
    P.lantern(sw.right, 1.85, 2.2)
    F.cat(b, 4.2, SY1 - 0.16, 2.24, rz=160, col="#d98a3d")
