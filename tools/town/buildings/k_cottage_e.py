# Ginnel Cottage: the terrace's way through to the dye-yards runs under its upper floor, so everybody's errands pass its kitchen window, and its lamp in the passage is the lane's only light after dark.
# A terrace house, eaves to the street, with an arched passage through the ground floor at its right end; butter lime-wash over a rubble footing, three upper windows in a row, a sagging tiled roof with a dormer and two stacks.
# Butter plaster, pale stone band and arch, terracotta tiles; accent red.
from kit import *
import parts as P
import parts_c as PC
import parts_k as K

META = {"name": "Ginnel Cottage", "kind": "cottage", "lot": (5.5, 7.0), "terrace": True}

W, D = 5.2, 5.6
GX, GW, GH, GA = 1.5, 1.3, 2.35, 0.55            # the passage: its middle, width, height and arch


def build(b):
    b.footprint(-2.6, 0.0, 2.6, 6.8, 7.8)
    g = b.body(W, D, 2.7, mat="plaster", col="butter")
    P.plinth(g, h=0.6, out=0.04)
    up = b.body(W, D, 2.3, mat="plaster", col="butter", z=2.7)
    P.band(g, 2.6, h=0.16, out=0.04, col="sand")
    g.front.opening(GX + W / 2, 0.0, GW, GH, arch=GA, pane=None, depth=0.02)
    g.back.opening(W / 2 - GX, 0.0, GW, GH, arch=GA, pane=None, depth=0.02)
    with b.at(GX, 0.0, 0.0):
        PC.vault(b, GW, GH, GA, D)
    PC.arch_stones(g.front, GX + W / 2, 0.0, GW, GH, GA, size=(0.36, 0.42))
    P.lantern_at(b, GX - 0.2, 0.9, 1.85, arm=0.0)
    P.door(g.front, 0.95, w=0.9, h=2.0, z=0.17, col="red", steps=1)
    P.window(g.front, 2.4, 1.05, w=0.9, h=1.2, shutters="red", box=True)
    for i, u in enumerate((0.95, 2.6, 4.25)):
        P.window(up.front, u, 0.8, shutters="red", box=(i == 2))
    P.exposed(up.front, "corners")
    P.door(g.back, 3.1, w=0.9, h=1.95, z=0.1, col="red", frame="timber")
    P.window(g.back, 4.45, 1.05, w=0.8, h=1.2)
    P.window(up.back, 1.4, 0.8)
    P.window(up.back, 3.8, 0.8, shutters="red")
    rise = up.gable(ridge="x", pitch=45, mat="tiles", sag=0.16, eave=0.38, verge=0.05, barge=False)
    P.dormer(b, -0.9, 0.85, 5.0 + 1.1 - 0.12, w=1.15, h=0.95, depth=1.6, face=0, roof="tiles", col="butter", frame="ivory", shutters=None)
    P.chimney(b, -2.2, D / 2, 5.0 + rise - 1.0, 2.2, mat="brick", pots=2)
    P.chimney(b, 2.2, D / 2 + 0.6, 5.0 + rise - 1.5, 2.4, mat="masonry", col="warm", pots=1)
    P.bench(b, -1.0, -0.5, 0, w=1.2)
    PC.pots(b, (0.75, -0.3, 0.0), (0.2, -0.3, 0.0), n=3)
    P.ivy(g.back, 2.2, 0.3, w=0.6, h=2.3, n=6)
    P.exposed(g.front, "base", n=8)
    fl = K.yard(b, -2.56, D, 2.56, 6.8, mat="cobble", h=0.06)
    with b.detail(1):
        b.beam((-2.3, 6.6, fl), (-2.3, 6.6, 2.7), w=0.1)
    P.laundry(b, (0.6, D + 0.05, 2.6), (-2.3, 6.6, 2.6), n=4)
    K.tub(b, -0.4, D + 0.65, fl, r=0.34, h=0.55, fill="water")
    PC.cat(b, 0.55, -0.4, 0.0, rz=300)
