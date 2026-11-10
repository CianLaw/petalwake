# The honey-seller's: she keeps her hives up on the leads among beans and marigolds, and sells the comb through a hatch by her door.
# A flat-roofed house with a shaped parapet to the street; on the roof a tiny garden: a pergola, tubs, two hives and the tiled head of the stair.
# Peach plaster with dressed-stone quoins and copings; accent mint.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC
import parts_m as PM

META = {"name": "The Honey Roof", "kind": "house", "lot": (5.0, 7.0), "terrace": True, "lean": (-0.002, 0.0)}


def build(b):
    W, D, H, acc = 4.5, 6.3, 8.3, "mint"
    c = W / 2
    bd = b.body(W, D, H, mat="plaster", col="peach")
    P.plinth(bd, h=0.4, mat="ashlar", col="warm")
    P.quoins(bd, corners="fr", z0=0.4, col="warm")
    f = bd.front
    # --- the front: door under a lead hood, the honey hatch, a balcony on the top floor
    P.door(f, 1.0, w=0.95, h=2.1, z=0.17, col=acc, frame="stone", steps=1)
    L.hood(f, 1.0, 2.78, w=1.5, out=0.7, kind="flat")
    PM.counter(f, W - 1.35, 1.05, w=1.4, h=1.15, col=acc, goods="pots")
    for u in (1.1, W - 1.1):
        P.window(f, u, 3.0 + 0.9, w=0.85, h=1.25, shutters=acc, box=True)
    P.window(f, 1.2, 5.7 + 0.12, w=0.85, h=2.0, bars=(1, 3), sill=False)
    P.balcony(f, 1.2, 5.7 + 0.1, w=1.7, out=0.7, rail="iron")
    P.window(f, W - 1.1, 5.7 + 0.85, w=0.8, h=1.15, shutters=acc)
    L.band_on(f, H - 0.26, h=0.22, out=0.1)
    L.sign(f, W - 0.28, 3.3, emblem="bee", col="mustard", board="ivory")
    # --- sides above the neighbours, and the back
    P.window(bd.left, 2.0, 6.6, w=0.6, h=0.9); P.window(bd.right, 2.3, 6.6, w=0.6, h=0.9)
    P.exposed(bd.left, "corners", n=8); P.exposed(bd.right, "corners", n=6)
    k = bd.back
    P.door(k, 1.2, w=0.9, h=2.0, z=0.17, col=acc, frame="stone", steps=1)
    P.window(k, W - 1.2, 1.1, w=0.9, h=1.2)
    for z in (3.9, 6.55):
        P.window(k, 1.2, z, w=0.8, h=1.15, shutters=acc); P.window(k, W - 1.2, z, w=0.8, h=1.15)
    L.downpipe(b, c - 0.3, D + 0.06, 0, H - 0.2, butt=True, face=180)
    # --- the roof garden
    with b.at(0, 0, H):
        b.box(W - 0.06, D - 0.06, 0.12, "flagstone", col="sand", x=0, y=D / 2, z=-0.12)
        arc = [(1.35 * math.cos(rad(a)), 0.75 + 0.62 * math.sin(rad(a))) for a in (0, 30, 60, 90, 120, 150, 180)]
        L.shaped_wall(b, [(-c, 0.0), (c, 0.0), (c, 0.75), (-c, 0.75)], t=0.26, col="peach", cope="ashlar")
        L.shaped_wall(b, arc, t=0.26, col="peach", cope="ashlar")
        for sx in (-1, 1):
            L.ball(b, sx * (c - 0.18), 0.13, 0.83, r=0.15)
        L.parapet(b, [(c, 0.26), (c, D), (-c, D), (-c, 0.26)], h=0.75, t=0.24, col="peach")
        # the head of the stair, at the back
        sw, sd, sh = 2.0, 2.1, 2.05
        sx_, sy_ = c - 0.24 - sw / 2, D - 0.24 - sd / 2
        st = b.body(sw, sd, sh, mat="plaster", col="peach", x=sx_, y=sy_, foot=False)
        P.door(st.front, 0.75, w=0.8, h=1.85, z=0.05, col=acc, frame="timber")
        P.window(st.left, 1.05, 0.9, w=0.55, h=0.7)
        L.wall_top(st.front, [[(0.0, sh), (sw, sh), (sw, sh + 0.7), (0.0, sh + 0.7)]])
        L.wall_top(st.right, [[(0.0, sh), (sd, sh), (0.0, sh + 0.7)]])
        L.wall_top(st.left, [[(0.0, sh), (sd, sh), (sd, sh + 0.7)]])
        with b.at(sx_, sy_ + sd / 2, sh, rz=180):
            L.pent(b, sw, sd, 0.7, eave=0.05, verge=0.1, top=0.12)
        # pergola and bench, hives, tubs, beans
        L.pergola(b, 2.0, 1.9, h=2.1, x=-c + 1.3, y=1.5, vines=0.7, flowers=["#f5c842", "#f4f1e4", "#e85d3a"])
        P.bench(b, -c + 1.3, 2.05, 0, w=1.2)
        L.beehive(b, -c + 0.75, D - 1.0, 0, rz=90); L.beehive(b, -c + 0.75, D - 1.95, 0, rz=90)
        P.planter(b, 1.1, 0.5, 0, w=1.4, d=0.36, flowers=["#f5c842", "#e85d3a", "#f5c842"])
        P.planter(b, c - 0.55, 1.5, 0, w=0.5, d=0.5, bush=True)
        L.bean_poles(b, 0.35, 3.3, 0)
        L.flowerpot(b, -c + 0.5, 3.4, 0, flower="#f2a0bd"); L.flowerpot(b, 0.9, 2.2, 0, r=0.18, plant="#8fa98a", flower="#b08ae6")
        L.cat(b, c - 1.2, 0.13, 0.83, rz=-20, col="#d9b98a")
        PC.climber(b, (-c + 0.3, -0.05, 0.7), (-c + 2.0, -0.05, 0.25), n=6, r=0.22, bloom=["#f5c842", "#f4f1e4"])
    P.chimney(b, -c + 0.36, 3.6, H - 0.3, 2.7, w=0.6, d=0.7, mat="brick", pots=2)
    # --- the lane
    L.flowerpot(b, -c + 0.3, -0.35, 0, flower="#f5c842"); P.barrel(b, c - 0.35, -0.4, r=0.26, h=0.65, col="#e3c98f")
