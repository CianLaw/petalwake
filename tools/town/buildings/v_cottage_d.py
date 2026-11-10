# The Boatwright's: when the Maggie Ann was too rotten to mend, Tam cut her in two and hung her bow over his
# own door, ribs and all. A gable-fronted cottage with half an upturned clinker boat for a porch, a slipway's
# worth of gear about it. Grey rubble, weighted slates, teal paint, tarred planking.
from kit import *
import parts as P
import parts_v as V
import parts_h as PH

META = {"name": "The Boatwright's", "kind": "house", "lot": (6.0, 7.0), "wobble": 0.045}


def build(b):
    ac = "teal"
    b.footprint(-2.9, 0.0, 2.9, 6.9, 2.3)
    c = V.BBody(b, 4.8, 5.6, 2.3, col="grey", batter=0.05, depth=0.45)
    V.footing(c, h=0.45, boulders="f")
    V.quoins(c, corners="fr")
    V.door(c.front, 2.4, w=0.9, h=1.8, col=ac)
    V.window(c.front, 0.85, 0.9, w=0.55, h=0.7, col=ac, shut="one")
    V.window(c.front, 3.95, 0.9, w=0.55, h=0.7, col=ac, shut="open")
    V.window(c.front, 2.4, 3.35, w=0.5, h=0.62, col=ac, shut="open")
    V.rubble(c.front, n=8, z0=2.2)
    for wl in (c.left, c.right):
        V.window(wl, 1.6, 0.9, w=0.6, h=0.8, col=ac, shut="open"); V.window(wl, 4.0, 0.9, w=0.6, h=0.8, col=ac, shut="half")
        V.rubble(wl, n=10)
    V.window(c.back, 3.5, 0.9, w=0.55, h=0.75); V.window(c.back, 2.4, 3.35, w=0.45, h=0.55)
    V.rubble(c.back, n=8)
    rf = c.gable(ridge="y", pitch=46, skew=True, mat="slate", eave=0.3, apex="stone")
    V.weights(rf, rows=(0.35,), every=0.85)
    RZ = 2.3 + rf.rise
    V.chimney(b, 0.0, 5.6 - 0.62, RZ - 0.9, 2.3, w=0.7, d=0.85, cap="pots", pots=2)
    # ------------------------------------------------------------------ the porch: half a boat, keel up, bow to the street
    L, S0 = 2.25, 0.42
    with b.at(0.0, 0.16, 2.68, rz=180):
        with b.at(ry=180):
            with b.at(0, -L * S0, 0):
                V.hull(b, L=L, width=1.95, depth=0.72, n=5, strakes=4, s0=S0, s1=1.0, col="#8d7663", incol="#c4ab84", rail=ac, ribs=3, cap0=False, lod=1)
    for sx in (-1, 1):
        V.beam(b, (sx * 0.62, -0.92, 0.0), (sx * 0.6, -0.92, 2.0), w=0.09, mat="timber", col="greyoak", lod=1)
        V.knee(b, (sx * 0.95, 0.08, 1.45), (sx * 0.9, -0.42, 1.98), w=0.07, strut=False)
    # ------------------------------------------------------------------ the trade
    PH.anchor(b, -1.75, -0.12, 0, rz=0, h=1.25)
    V.floats(b, 1.5, -0.02, 2.0, n=4)
    PH.net_heap(b, 1.75, -0.6, 0, r=0.45)
    V.oars(b, 2.0, -0.05, 0.0, h=2.4, lean=0.3, blade=ac)
    with b.at(0.4, 6.28, 0.56, rz=90):
        with b.at(ry=180):
            V.hull(b, L=3.0, width=1.2, depth=0.5, n=6, strakes=3, col="#7a5f4a", rail=ac, inside=False, lod=1)
    V.drystone(b, [(-2.6, 5.75), (-2.6, 6.6), (-1.6, 6.6)], h=0.85, t=0.45)
    V.rain_barrel(b, 2.15, 5.95, r=0.3, h=0.85)
