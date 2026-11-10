# The chandler's: candles are dipped and soap is boiled in the open shed behind (well away from the thatch next door), and sold over the counter on the street, where the day's dipping hangs out to harden.
# A jettied two-storey shop-house with its eaves to the street and a dormer over the counter, an open tiled boiling shed on posts across the back with the copper in its brick furnace and a thin iron-banded flue.
# Cream lime-wash below, rose above, terracotta tiles; accent pink.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_k as K

META = {"name": "The Chandler's", "kind": "shop", "lot": (5.5, 7.0)}

W, D = 4.8, 5.2


def build(b):
    b.footprint(-2.62, 0.0, 2.62, 6.8, 8.0)
    g = b.body(W, D, 2.7, mat="plaster", col="cream")
    P.plinth(g, h=0.6, out=0.05)
    up = b.body(W, D + 0.3, 2.2, mat="plaster", col="rose", y=(D - 0.3) / 2, z=2.7, floor="planks")
    PM.joists(g.front, 2.7, out=0.3)
    PM.counter(g.front, 1.45, 0.95, w=1.7, h=1.15, col="pink", goods="parcels")
    P.door(g.front, 3.75, w=0.9, h=2.0, z=0.17, col="pink", steps=1, lamp=True)
    P.exposed(g.front, "base", n=7)
    P.window(up.front, 1.2, 0.7, shutters="pink", box=True)
    P.window(up.front, 3.6, 0.7, shutters="pink")
    K.sign(up.front, 2.4, 1.85, emblem="candle", col="pink")
    for wl in (g.left, g.right):
        P.window(wl, 2.6, 1.1, w=0.8, h=1.1)
    P.door(g.back, 1.2, w=0.9, h=1.95, z=0.1, col="pink", frame="timber")
    P.window(g.back, 3.4, 1.1, w=0.9, h=1.1)
    P.window(up.back, 1.3, 0.7)
    P.window(up.back, 3.5, 0.7)
    rise = up.gable(ridge="x", pitch=48, mat="tiles", sag=0.1, eave=0.35, verge=0.15)
    PH.cuttable(up.left, up.right)
    PC.oculus(up.left, (D + 0.3) / 2, 2.2 + 1.2, r=0.34)
    PC.oculus(up.right, (D + 0.3) / 2, 2.2 + 1.2, r=0.34)
    P.dormer(b, -0.95, 0.75, 4.9 + 1.0 * math.tan(rad(48)) - 0.1, w=1.1, h=0.95, depth=1.5, face=0, roof="tiles", col="rose", frame="ivory")
    P.chimney(b, 1.55, 4.3, 5.4, 3.4, mat="brick", pots=2)

    # ------------------------------------------------------------------ the day's dipping and the soap, on the street
    K.candle_rack(b, 0.35, -0.5, 0, w=0.9, h=1.55, rods=3, per=5)
    K.soap_table(b, -2.0, -0.55, 0, w=0.75, d=0.45)

    # ------------------------------------------------------------------ the boiling shed behind
    fl = K.yard(b, -2.6, D, 2.6, 6.8, mat="flagstone", h=0.08)
    PM.lean_to(b, 4.5, 1.3, pitch=18, x=0.0, y=D, z=2.05, face=180, mat="tiles", eave=0.15, verge=0.1)
    for sx in (-1, 1):
        b.beam((sx * 2.05, D + 1.2, fl), (sx * 2.05, D + 1.2, 2.02), w=0.16, lod=0)
    b.beam((-2.2, D + 1.2, 1.98), (2.2, D + 1.2, 1.98), w=0.14, h=0.16, lod=0)
    K.cauldron(b, 1.05, D + 0.72, fl, r=0.42)
    K.round_stack(b, 1.9, D + 0.38, fl, h=4.7, r0=0.24, r1=0.19, seg=8, bands=(0.45, 0.8), head=False, strength=0.8)
    K.candle_rack(b, -1.05, D + 0.75, fl, w=1.4, h=1.6, rods=3, per=7)
    K.firewood(b, -0.2, D + 0.03, fl, w=1.0, h=0.9, rz=180)
    K.bucket(b, 0.2, D + 1.0, fl)
    PC.cat(b, -2.0, -0.55, 0.92, rz=340)
