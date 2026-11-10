# The bookseller's: two fat storeys and a slate mansard full of unsold atlases, with the best shop window in the lane.
# The widest and lowest of the row: a full-width shop front under an awning, three tall windows above, and a double-pitched mansard with hipped dormers between tall end stacks.
# Lilac plaster, grey slate, mustard paintwork with cream frames; accent mustard.
from kit import *
import parts as P
import parts_l as L
import parts_m as PM

META = {"name": "The Atlas Bookshop", "kind": "shop", "lot": (6.0, 8.0), "terrace": True, "lean": (0.001, 0.002)}


def build(b):
    W, D, H, acc = 5.5, 7.3, 6.2, "mustard"
    c = W / 2
    bd = b.body(W, D, H, mat="plaster", col="lilac")
    P.plinth(bd, h=0.2, mat="ashlar", col="grey")
    f = bd.front
    # --- the shop front: two windows of books either side of the door
    L.shopfront(f, 0.22, W - 0.22, h=2.9, z=0.2, col=acc, door=c, door_w=1.0, lights=3, riser=0.5, fascia=0.4)
    P.awning(f, 1.27, 2.62, w=2.0, out=1.0, drop=0.5, cols=("stripe_yellow", "linen"))
    P.lantern(f, W - 0.1, 2.35)
    for u in (1.27, W - 1.27):
        with f.on(u, 0.2 + 0.5 + 0.02):
            with b.at(0, 0.06, 0):
                PM.display(b, 1.5, kind="books", depth=0.1)
    # --- first floor: three tall windows
    for u in (1.0, W - 1.0):
        P.window(f, u, 3.95, w=0.85, h=1.6, bars=(1, 2), shutters=acc, box=True)
    P.window(f, c, 3.95, w=0.85, h=1.6, bars=(1, 2))
    L.guard(f, c, 3.95, w=0.9, h=0.55)
    L.band_on(f, 3.22, h=0.14); L.band_on(f, H - 0.42, h=0.16, out=0.08)
    P.sign(f, W - 0.3, 3.5, emblem="book", col="brown", board="ivory")
    # --- back
    k = bd.back
    P.door(k, 1.4, w=0.9, h=2.0, z=0.17, col=acc, frame="stone", steps=1)
    P.window(k, 4.0, 1.1, w=1.0, h=1.3); P.window(k, 1.4, 3.95, w=0.85, h=1.3, shutters=acc); P.window(k, 4.0, 3.95, w=0.85, h=1.3, shutters=acc)
    # --- the mansard: steep slate skirts, a low slate cap, lead rolls at the break
    P.window(bd.left, D / 2, H + 0.85, w=0.7, h=1.0); P.window(bd.right, D / 2, H + 0.85, w=0.7, h=1.0)
    sec = [(0.0, 0.0), (0.72, 2.25), (D / 2, 3.55)]
    rise = bd.gable(ridge="x", section=sec, mat="slate", eave=0.12, verge=0.04, course=0.4)
    L.cut_gable(bd.left); L.cut_gable(bd.right)
    with b.detail(1):
        for y in (0.72, D - 0.72):
            b.beam((-c - 0.04, y, H + 2.25 + 0.05), (c + 0.04, y, H + 2.25 + 0.05), w=0.17, h=0.1, mat="metal", col="lead")
    for x in (-1.75, 0.0, 1.75):
        P.dormer(b, x, 0.15, H + 0.34, w=0.95, h=1.25, depth=1.05, face=0, kind="hip", roof="slate", col="lilac", frame="ivory", pitch=34)
    for x in (-1.3, 1.3):
        P.dormer(b, x, D - 0.15, H + 0.34, w=0.95, h=1.25, depth=1.05, face=180, kind="hip", roof="slate", col="lilac", frame="ivory", pitch=34)
    P.chimney(b, -c + 0.36, D / 2 - 1.3, H + 2.3, 3.0, w=0.66, d=0.9, mat="brick", pots=2)
    P.chimney(b, c - 0.36, D / 2 + 1.1, H + 2.3, 2.8, w=0.66, d=0.9, mat="brick", pots=2)
    # --- the lane: a bench of penny books, the shop cat
    P.bench(b, 1.75, -0.48, w=1.4)
    with b.at(1.55, -0.5, 0.48):
        PM.display(b, 0.8, kind="books", depth=0.2)
    L.cat(b, 2.25, -0.5, 0.48, rz=10, col="#d98a3d")
    P.planter(b, -2.3, -0.32, 0, w=0.7, d=0.3)
    L.downpipe(b, c - 0.3, D + 0.06, 0, H - 0.2, butt=True, face=180)
