# Built by a Low Country merchant who missed home: a crow-stepped gable to the street, and iron ties to hold it all together.
# One tall plastered block, three storeys and a loft; the front gable climbs in six steps to a seat for the weathercock, and a chimney rides the back gable.
# Ochre plaster with pale dressed-stone copings and bands, terracotta tiles; accent teal.
from kit import *
import parts as P
import parts_l as L
import parts_m as PM

META = {"name": "The Stepped Gable", "kind": "house", "lot": (5.2, 8.0), "terrace": True, "lean": (-0.001, -0.002)}


def build(b):
    W, D, H, acc = 4.6, 7.0, 8.4, "teal"
    c = W / 2
    bd = b.body(W, D, H, mat="plaster", col="ochre")
    P.plinth(bd, h=0.34, mat="ashlar", col="grey")
    f = bd.front
    # --- ground floor: an arched door up two steps and an arched window behind a grille
    P.door(f, 1.15, w=1.0, h=2.3, arch=0.5, z=0.34, col=acc, frame="stone", lamp=True, steps=2)
    P.window(f, W - 1.35, 1.0, w=1.05, h=1.6, arch=0.52, bars=(1, 2))
    L.guard(f, W - 1.35, 1.0, w=1.0, h=0.55)
    # --- first floor: two tall arched windows
    for u in (1.22, W - 1.22):
        P.window(f, u, 3.1 + 0.75, w=0.85, h=1.65, arch=0.42, shutters=acc, bars=(1, 2))
    # --- second floor: three small ones
    for u, bx in ((0.95, True), (c, False), (W - 0.95, True)):
        P.window(f, u, 5.9 + 0.8, w=0.62, h=0.95, bars=(1, 1), box=bx)
    L.band_on(f, 3.0, h=0.16); L.band_on(f, 5.85, h=0.16); L.band_on(f, H - 0.1, h=0.16)
    L.anchors(f, [(0.4, 3.45), (c, 3.45), (W - 0.4, 3.45), (0.4, 6.28), (W - 0.4, 6.28)])
    # --- the loft: an arched light and a pigeon-hole under the weathercock
    P.window(f, c, H + 0.55, w=0.8, h=1.25, arch=0.4, bars=(1, 1))
    L.porthole(f, c, H + 2.55, r=0.2, rim="lead")
    L.anchors(f, [(c - 1.35, H + 0.75), (c + 1.35, H + 0.75)], kind="s")
    rise, top = L.crow_roof(bd, pitch=54, steps=6, up=0.4, ends="f", verge=0.3, eave=0.15, sag=0.08, barge=False, col="#f7e3d3")
    L.barge_boards(bd, rise, eave=0.15, verge=0.3, ends="b")
    PM.weathercock(b, 0, 0.15, top + 0.1, h=1.3, shape="cock")
    # --- sides above the neighbours
    P.window(bd.left, 2.2, 6.7, w=0.6, h=0.85); P.window(bd.right, 4.8, 6.75, w=0.6, h=0.85)
    L.anchors(bd.left, [(4.6, 6.3), (6.5, 6.3)]); L.anchors(bd.right, [(0.6, 6.3), (2.6, 6.3)])
    P.exposed(bd.left, "corners", n=8)
    # --- back: a plain gable with the chimney riding it, a little balcony
    k = bd.back
    P.door(k, 1.2, w=0.9, h=2.0, z=0.17, col=acc, frame="stone", steps=1)
    P.window(k, W - 1.3, 1.1, w=0.9, h=1.2)
    P.door(k, W - 1.45, w=0.85, h=1.95, z=3.1 + 0.12, col=acc, frame=None)
    P.balcony(k, W - 1.45, 3.1 + 0.1, w=1.9, out=0.8, rail="balusters")
    P.window(k, 1.2, 3.1 + 0.9, w=0.8, h=1.2, shutters=acc)
    P.window(k, 1.3, 5.9 + 0.8, w=0.7, h=1.0); P.window(k, W - 1.3, 5.9 + 0.8, w=0.7, h=1.0, shutters=acc)
    P.window(k, c - 1.0, H + 0.5, w=0.55, h=0.8)
    L.cut_gable(k)
    P.chimney(b, 0.0, D - 0.36, H + 1.9, 3.3, w=0.75, d=0.62, mat="brick", pots=2)
    P.laundry(b, (-1.4, D + 0.72, 3.1 + 1.0), (-2.05, D + 0.1, 5.6), n=3, sag=0.2)
    # --- the lane: the merchant's sign, a bench under the window, pots on the steps
    L.sign(f, W - 0.3, 3.1, emblem="ship", col="navy", board="ivory", round_board=True)
    P.bench(b, 1.0, -0.42, w=1.3)
    L.flowerpot(b, -1.95, -0.4, 0.0, flower="#e85d3a"); L.flowerpot(b, -0.4, -0.35, 0.0, r=0.13, flower="#f5c842")
    L.cat(b, 1.2, -0.42, 0.48, rz=15, col="#2f2b29", bib="#f1ede4")
