# The glassblower's: the furnace never goes out, and its tall brick cone draws the heat up through the middle of the house; bottles, flasks and the fishermen's glass floats cool in the window and by the door.
# A square rubble house under a hipped tile roof, with a great tapering brick cone rising through the roof to twice the height of the house; a shop window and a pent-roofed door on the street, bull's-eye windows down the sides.
# Warm rubble with pale quoins, tiles, red furnace brick banded with iron; accent blue.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_k as K

META = {"name": "The Glassblower's", "kind": "workshop", "lot": (6.0, 7.0)}

W, D, H = 5.0, 6.0, 3.0
CX, CY = 0.0, 3.3
CONE = [(1.8, 2.4), (1.5, 4.4), (1.18, 6.4), (0.9, 8.4), (0.66, 10.4), (0.6, 11.0)]


def cone_r(z):
    for (r0, z0), (r1, z1) in zip(CONE, CONE[1:]):
        if z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return CONE[-1][0]


def build(b):
    b.footprint(-2.8, 0.0, 2.8, 6.4, 5.2)
    bd = b.body(W, D, H, mat="masonry", col="warm")
    P.plinth(bd, h=0.55)
    P.quoins(bd, z0=0.55, col="sand")
    for wl in bd.walls:
        P.stones(wl, n=7, z0=0.6, z1=2.8)
    PM.shopfront(bd.front, 1.5, z=0.0, w=2.0, h=1.4, riser=0.7, col="blue", lights=3, goods="bottles", glass="#ffcf8a")
    P.door(bd.front, 3.8, w=0.95, h=2.05, z=0.17, col="blue", steps=1, lamp=True)
    PM.pent(bd.front, 3.8, 2.78, w=1.7, out=0.7)
    K.sign(bd.front, 2.85, 2.9, emblem="bottle", col="blue", shape="round")
    PH.floats(bd.front, 4.62, 1.95, n=5)
    for wl in (bd.left, bd.right):
        PM.round_window(wl, 1.6, 1.9, r=0.5, spokes=6)
        PM.round_window(wl, 4.4, 1.9, r=0.5, spokes=6)
    P.door(bd.back, 1.3, w=0.9, h=1.95, z=0.12, col="blue", frame="timber")
    P.window(bd.back, 3.6, 1.1, w=1.0, h=1.2, bars=(2, 1))
    P.ivy(bd.right, 5.5, 0.3, w=1.2, h=2.4, n=7)
    sec = [(0.0, 0.0), (W / 2, W / 2 * math.tan(rad(40.0)))]
    b.loop_roof(W, D, mat="tiles", x=0.0, y=D / 2, z=H, eave=0.25, section=sec)
    PH.hip_rolls(b, W, D, sec, z=H, x=0.0, y=D / 2, mat="tiles", eave=0.25)
    P.dormer(b, -1.45, 0.85, 3.62, w=0.9, h=0.8, depth=1.2, face=0, roof="tiles", col="cream", frame="ivory")

    # ------------------------------------------------------------------ the cone
    with b.at(CX, CY):
        b.revolve(CONE, "brick", seg=16, lod=0)
        with b.detail(1):
            b.revolve([(0.6, 10.96), (0.71, 11.04), (0.71, 11.2), (0.48, 11.2)], "brick", seg=16)
            b.disc(0.48, "paint", col=K.SOOT, seg=16, z=11.17)
            for zz in (5.4, 7.4, 9.4):
                rr = cone_r(zz) + 0.02
                b.revolve([(rr, zz - 0.06), (rr, zz + 0.06)], "metal", col="iron", seg=16)
        b.smoke(0, 0, 11.6, 1.5)

    # ------------------------------------------------------------------ glass at the door, fuel behind
    P.crate(b, -2.05, -0.5, 0, s=0.55, rz=12)
    P.crate(b, -1.4, -0.45, 0, s=0.45, rz=-8)
    for i, (kind, col) in enumerate((("flask", "#2f8f8f"), ("globe", "#3f6fb5"), ("bottle", "#5a9a68"), ("globe", "#d9a431"))):
        K.pot(b, -2.2 + 0.2 * i, -0.5 + 0.06 * (i % 2), 0.55, kind=kind, r=0.09, h=0.24, col=col, mat="glass", mouth=False)
    K.firewood(b, 1.1, D + 0.03, 0, w=1.9, h=1.2, rz=180)
    with b.detail(2):
        for i in range(4):                       # blow-pipes stood against the back wall
            b.beam((-1.6 + 0.12 * i, D + 0.3, 0), (-1.62 + 0.12 * i, D + 0.06, 1.7), w=0.025, mat="metal", col="iron")
    PC.cat(b, 1.3, -0.5, 0.0, rz=20)
