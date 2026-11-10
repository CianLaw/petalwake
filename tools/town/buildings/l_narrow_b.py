# The pilot's widow lets rooms by the week: four storeys, one room wide, the tallest front in the lane.
# A single lime-washed slab of a house with its eaves to the street, an iron balcony across the first floor, two cat-sized dormers, a chimney on each party wall and a scullery wing behind.
# Sky-blue plaster on a dressed-stone ground storey, pale bands, terracotta tiles; accent navy.
from kit import *
import parts as P
import parts_l as L

META = {"name": "The Tall House", "kind": "house", "lot": (4.5, 7.5), "terrace": True, "lean": (-0.002, 0.001)}


def build(b):
    W, D, acc = 4.0, 5.3, "navy"
    H0, H = 3.0, 7.9
    ul, ur = 1.05, W - 1.05
    # --- dressed-stone ground storey
    g = b.body(W, D, H0, mat="ashlar", col="warm")
    P.plinth(g, h=0.34, col="grey")
    P.door(g.front, 0.95, w=0.95, h=2.1, z=0.34, col=acc, frame="stone", lamp=True, steps=2)
    P.window(g.front, 0.95, 2.6, w=0.95, h=0.3, bars=(2, 0), sill=False, lintel=None)          # fanlight
    P.window(g.front, W - 1.2, 1.05, w=1.05, h=1.45, bars=(1, 2), shutters=acc)
    L.guard(g.front, W - 1.2, 1.05, w=1.0, h=0.5)
    P.window(g.back, 0.95, 1.1, w=0.8, h=1.2)
    # --- three plastered storeys
    up = b.body(W, D, H, mat="plaster", col="sky", z=H0)
    P.band(g, H0 - 0.02, h=0.2, out=0.07)
    for u in (ul, ur):
        P.window(up.front, u, 0.14, w=0.85, h=2.2, bars=(1, 3), sill=False)
        P.window(up.front, u, 2.8 + 0.85, w=0.82, h=1.3, shutters=acc, box=(u < 2))
        P.window(up.front, u, 5.5 + 0.7, w=0.76, h=0.95, shutters=acc)
    P.balcony(up.front, W / 2, 0.12, w=3.4, out=0.78, rail="iron", floor="flagstone", floor_col="grey", brackets=False)
    with up.front.on(W / 2, 0.0):
        with b.detail(1):
            for x in (-1.5, -0.5, 0.5, 1.5):      # scrolled iron brackets under the balcony
                b.beam((x, -0.02, -0.55), (x, -0.7, -0.03), w=0.05, mat="metal", col="iron")
                b.beam((x, -0.02, -0.04), (x, -0.74, -0.04), w=0.05, mat="metal", col="iron")
        L.flowerpot(b, -1.4, -0.55, 0.12, flower="#e8497a"); L.flowerpot(b, 1.35, -0.5, 0.12, r=0.13, flower="#f4f1e4")
        L.cat(b, 0.9, -0.5, 0.12, rz=-30, col="#c98a4b")
    L.band_on(up.front, 2.72, h=0.14); L.band_on(up.front, 5.42, h=0.14)
    L.band_on(up.front, H - 0.3, h=0.2, out=0.09)
    # sides above the neighbours: windows, and the plaster worn through
    P.window(up.left, 1.6, 5.5 + 0.7, w=0.7, h=0.95)
    P.window(up.left, 3.9, 5.5 + 0.75, w=0.55, h=0.8)
    P.window(up.right, 3.7, 5.5 + 0.75, w=0.6, h=0.85)
    P.window(up.left, D / 2, H + 0.7, w=0.55, h=0.8, arch=0.27)
    P.window(up.right, D / 2 - 0.9, H + 0.55, w=0.5, h=0.7)
    P.exposed(up.right, "corners", n=8)
    # back: one bay of windows beside the wing
    for z in (0.95, 2.8 + 0.9, 5.5 + 0.75):
        P.window(up.back, 0.9, z, w=0.78, h=1.15, shutters=acc if z > 3 else None)
    rise = up.gable(ridge="x", pitch=43, eave=0.45, verge=0.04, sag=0.09, col="#e9d8cf")
    L.cut_gable(up.left); L.cut_gable(up.right)
    top = H0 + H
    for x in (-0.95, 0.95):
        P.dormer(b, x, 0.72, top + 0.62, w=0.8, h=0.78, depth=1.25, col="sky", frame="ivory")
    P.chimney(b, -W / 2 + 0.36, D / 2 - 0.02, top + 1.9, 2.75, w=0.66, d=0.85, mat="brick", pots=2)
    P.chimney(b, W / 2 - 0.36, D / 2 + 1.4, top + 0.5, 3.6, w=0.64, d=0.6, mat="brick", pots=1)
    P.weathervane(b, -0.3, D / 2, top + rise + 0.05, h=1.1)
    # --- the scullery wing behind, under a lean-to
    ww, wd, wh = 2.3, 1.9, 5.3
    wx, wy0 = -W / 2 + ww / 2 + 0.02, D - 0.2
    wg = b.body(ww, wd, wh, mat="plaster", col="sky", x=wx, y=wy0 + wd / 2)
    P.plinth(wg, h=0.34, col="grey")
    P.door(wg.back, 1.4, w=0.85, h=2.0, z=0.17, col=acc, frame="timber", steps=1)
    P.window(wg.back, 1.15, 3.2, w=0.8, h=1.1, shutters=acc)
    P.window(wg.right, 1.1, 3.3, w=0.6, h=0.9)
    P.window(wg.right, 1.1, 1.1, w=0.6, h=0.9)
    L.wall_top(wg.right, [[(0.0, wh), (wd, wh), (0.0, wh + 0.95)]])
    L.wall_top(wg.left, [[(0.0, wh), (wd, wh), (wd, wh + 0.95)]])
    with b.at(wx, wy0 + wd, wh, rz=180):
        L.pent(b, ww, wd, 0.95, eave=0.25, verge=0.08, col="#e9d8cf")
    P.chimney(b, wx - 0.72, wy0 + wd - 0.35, wh - 0.3, 2.1, w=0.5, d=0.5, mat="brick", pots=1)
    # yard: a water butt, washing strung from the wing to a pole
    L.downpipe(b, W / 2 - 0.25, D + 0.06, 0, top - 0.15, butt=True, face=180)
    b.beam((W / 2 - 0.2, D + 1.75, 0), (W / 2 - 0.2, D + 1.75, 3.2), w=0.09, lod=1)
    P.laundry(b, (wx + ww / 2, D + 1.6, 3.0), (W / 2 - 0.2, D + 1.75, 3.1), n=3, sag=0.2)
    P.planter(b, 1.0, D + 1.0, 0, w=0.8)
