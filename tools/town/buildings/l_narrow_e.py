# The herbalist's: bunches drying under the thatch, and a bay window two storeys high to catch the morning for her seedlings.
# A low-browed house, gable to the street but with the gable's top leaned back in a half-hip; a canted bay up through two storeys; a fat brick stack through the ridge.
# Sage plaster on a rubble foot, deep straw thatch with a straw bird on the ridge; accent plum.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC

META = {"name": "The Herbalist's Thatch", "kind": "house", "lot": (5.4, 8.5), "terrace": True, "lean": (0.002, 0.001)}


def build(b):
    W, D, H, acc = 4.8, 7.7, 7.6, "plum"
    c = W / 2
    bd = b.body(W, D, H, mat="plaster", col="sage")
    P.plinth(bd, h=0.6)
    f = bd.front
    # --- the bay, from the ground up through two storeys
    L.bay(f, 1.62, 0.0, w=2.3, h=5.35, out=0.6, cant=0.5, base="ground", col="sage", rows=((0.95, 1.35), (3.7, 1.25)), rails=(2.6, 3.4),
          trim=acc, roof="shingle", roof_rise=0.55, lights=3)
    # --- door under a shingled hood, with a rose trained round it
    P.door(f, 3.9, w=0.9, h=2.0, z=0.17, col=acc, frame="timber", steps=1)
    L.hood(f, 3.9, 2.62, w=1.5, out=0.7, kind="pent", mat="shingle")
    P.lantern(f, 3.15, 2.0)
    PC.climber(b, (W - c - 0.28, -0.1, 0.2), (W - c - 0.22, -0.12, 2.5), n=6, r=0.2, bloom=["#f2a0bd", "#f4f1e4"])
    P.window(f, 3.9, 2.9 + 0.95, w=0.8, h=1.2, shutters=acc, box=True)
    for u in (1.3, 3.6):
        P.window(f, u, 6.05, w=0.75, h=0.9, shutters=acc)
    P.window(f, c, H + 0.3, w=0.6, h=0.75, lintel="timber", bars=(1, 0))
    L.sign(f, W - 0.28, 3.05, emblem="flower", col=acc, board="ivory", round_board=True)
    # --- sides, where they stand above the neighbours
    P.window(bd.left, 2.0, 6.15, w=0.55, h=0.75); P.window(bd.right, 5.4, 6.15, w=0.55, h=0.75)
    P.exposed(bd.left, "corners", n=8); P.exposed(bd.right, "corners", n=6)
    # --- back
    k = bd.back
    P.door(k, 1.3, w=0.9, h=2.0, z=0.17, col=acc, frame="timber", steps=1)
    P.window(k, 3.5, 1.15, w=0.9, h=1.2, shutters=acc)
    P.window(k, 1.35, 3.85, w=0.8, h=1.15); P.window(k, 3.55, 3.85, w=0.8, h=1.15, shutters=acc, box=True)
    P.window(k, c, H + 0.55, w=0.7, h=0.95, lintel="timber")
    P.ivy(k, c + 0.1, 0.5, w=1.0, h=2.2, n=6)
    # --- the thatch
    R = L.halfhip_roof(bd, pitch=52, hip=0.42, ends="f", mat="thatch", course=0.6, lip=0.03, thick=0.32, eave=0.15, verge=0.4, roll=False)
    yf, yb = bd.ridge_y
    L.saddle(b, (0, yf - 0.05, H + R), (0, yb, H + R), 52, w=0.62, lift=0.08, mat="thatch", col="#d8c08c", scallop=0.13)
    L.straw_bird(b, 0, yf + 0.25, H + R + 0.22)
    P.chimney(b, 0.0, 4.7, H + 1.9, 3.1, w=0.95, d=0.7, mat="brick", pots=2)
    with f.on(c, H + 1.62):
        L.herbs(b, (-1.15, -0.2, 0.0), (1.15, -0.2, 0.0), n=7)
    # --- the lane: pots and jars along the bay, a tub of lavender
    PC.pots(b, (-1.75, -0.82, 0), (-0.45, -0.85, 0), n=6)
    L.flowerpot(b, 0.75, -0.3, 0, r=0.2, h=0.3, plant="#8fa98a", flower="#b08ae6", tall=1.2)
    L.flowerpot(b, 2.2, -0.32, 0, flower="#f5c842")
    L.cat(b, 1.5, -0.28, 0.17, rz=-25, col="#8c8580")
    L.downpipe(b, -c + 0.3, D + 0.06, 0, H - 0.3, butt=True, face=180)
