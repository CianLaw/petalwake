# The Red Door net loft: three generations of drift-net men have hauled wet nets up its face to dry in the dark of the top floor.
# A stone store with two tarred board storeys, each jettied a little further over the quay, under a steep sagging tiled gable
# with a hooded hoist; it leans. Black tar over warm rubble, terracotta; accent red.
from kit import *
import parts as P
import parts_h as H

META = {"name": "The Red Door Net Loft", "kind": "netloft", "lot": (4.8, 6.5), "lean": (0.007, -0.004)}


def build(b):
    # ------------------------------------------------------------------ stone store, two jettied tarred storeys
    g = b.body(3.7, 5.2, 2.5, mat="masonry", col="warm", y=2.85)                      # y 0.25 .. 5.45
    f1 = b.body(3.9, 5.45, 2.3, mat="planks", col=H.TAR, y=2.725, z=2.5, floor="planks", depth=0.14)      # y 0.0 .. 5.45
    f2 = b.body(4.0, 5.6, 2.2, mat="planks", col=H.TAR, y=2.65, z=4.8, floor="planks", depth=0.14)        # y -0.15 .. 5.45
    H.cuttable(f2.front, f2.back)
    RISE = 2.0 * math.tan(rad(54))
    with b.detail(1):      # joist ends under each jetty
        for i in range(6):
            x = -1.7 + 3.4 * i / 5
            b.beam((x, 0.3, 2.4), (x, -0.06, 2.4), w=0.13, h=0.17, mat="timber", col="darkoak")
            b.beam((x * 1.04, 0.05, 4.7), (x * 1.04, -0.2, 4.7), w=0.13, h=0.17, mat="timber", col="darkoak")

    # ------------------------------------------------------------------ the front: a door at every floor, the hoist above
    P.door(g.front, 1.25, w=1.5, h=2.0, col="red", frame="timber", double=True, z=0.08, lamp=True)
    P.window(g.front, 3.05, 1.15, w=0.6, h=0.75, frame="ivory", lintel="timber")
    H.loading_door(f1.front, 1.95, 0.25, w=1.25, h=1.7, col="red")
    H.loading_door(f2.front, 2.0, 0.22, w=1.25, h=1.65, col="red")
    H.loading_door(f2.front, 2.0, 2.5, w=0.9, h=1.1, col="red", sill=False, bar=False)
    H.floats(f1.front, 0.62, 1.7, n=5)
    H.rope_hank(f1.front, 3.3, 1.75)
    H.hoist(b, 0.0, -0.1, 4.8 + 3.92, out=1.0, load="net", drop=3.3, hood="tiles")
    # ------------------------------------------------------------------ sides and back
    H.hatch(g.right, 1.6, 1.2, w=0.7, h=0.7, col="red")
    P.window(g.right, 3.9, 1.1, w=0.7, h=0.8, frame="ivory", lintel="timber")
    H.hatch(g.left, 2.6, 1.2, w=0.7, h=0.7, col="red")
    P.door(g.back, 1.2, w=0.9, h=1.9, col="red", frame="timber", z=0.08)
    P.plinth(g, h=0.35)
    P.quoins(g, corners="fr", z0=0.35, col="sand")
    P.window(f1.right, 1.5, 0.85, w=0.65, h=0.9, frame="ivory", lintel=None)
    H.hatch(f1.right, 4.1, 0.9, w=0.6, h=0.7, col="red")
    P.window(f1.left, 3.9, 0.85, w=0.65, h=0.9, frame="ivory", lintel=None)
    P.window(f1.back, 1.95, 0.8, w=0.7, h=0.95, frame="ivory", lintel=None)
    P.window(f2.right, 3.9, 0.75, w=0.65, h=0.9, frame="ivory", lintel=None)
    P.window(f2.left, 1.6, 0.75, w=0.65, h=0.9, frame="ivory", lintel=None)
    H.life_ring(f2.left, 4.3, 1.2)
    H.loading_door(f2.back, 2.0, 0.25, w=1.1, h=1.5, col="red", bar=False)
    H.louvre(f2.back, 2.0, 2.65, w=0.7, h=0.9)
    for wl in f1.walls:
        H.battens(wl, col=H.TAR, rails=(0.07,))
    for wl in (f2.left, f2.right):
        H.battens(wl, col=H.TAR, rails=(0.07,))
    for wl in (f2.front, f2.back):
        H.battens(wl, col=H.TAR, z1=2.2 + RISE, rails=(0.07, 2.2))

    # ------------------------------------------------------------------ the roof, the stove pipe
    f2.gable(ridge="y", pitch=54, mat="tiles", eave=0.2, verge=0.32, sag=0.14, course=0.4)
    zr = 7.0 + (2.0 - 1.05) * math.tan(rad(54))
    with b.at(-1.05, 4.1, zr):
        with b.detail(1):
            b.tube((0, 0, -0.2), (0, 0, 1.5), r=0.09, mat="metal", col="iron", n=6)
            b.revolve([(0.2, 1.5), (0.0, 1.72)], "metal", col="iron", seg=6)
        b.smoke(0, 0, 1.9, strength=0.6)
    H.gull(b, 0.0, -0.3, 7.0 + RISE + 0.12, rz=20)

    # ------------------------------------------------------------------ the quay in front: a net on its rack, pots, a barrel
    with b.detail(1):
        for x in (0.45, 2.25):
            b.beam((x, -0.95, 0), (x, -0.95, 2.25), w=0.09, mat="timber", col="greyoak")
    H.net_drape(b, (0.45, -0.95, 2.2), (2.25, -0.95, 2.2), drop=1.75, sag=0.12, col=H.NET)
    H.pots(b, -1.9, -0.55, rz=90, n=3)
    P.barrel(b, -1.2, -0.9, r=0.27, h=0.72)
    H.rope_coil(b, 1.2, -0.45, r=0.28)
    H.net_heap(b, 1.75, -0.3, r=0.45, col=H.NET_BROWN)
