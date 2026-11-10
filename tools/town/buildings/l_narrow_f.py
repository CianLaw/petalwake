# A retired mate could not give up the masthead: he built a crow's nest on his ridge, and now the broom post lands there.
# The thinnest house in the lane: four storeys, an oriel two storeys high, a steep gable to the street and a boarded tub of a lookout perched on the ridge, reached by a ladder from a roof hatch.
# White lime-wash over a tarred foot, terracotta tiles, tarred timber for the nest; accent blue.
from kit import *
import parts as P
import parts_l as L

META = {"name": "The Crow's Nest", "kind": "house", "lot": (4.6, 7.0), "terrace": True, "lean": (0.0, -0.003)}


def build(b):
    W, D, H, acc = 4.0, 6.4, 10.7, "blue"
    c = W / 2
    bd = b.body(W, D, H, mat="plaster", col="white")
    P.plinth(bd, h=0.7, col="dark")
    f = bd.front
    # --- the front: arched door, a two-storey oriel, the mate's porthole in the gable
    P.door(f, 0.95, w=0.9, h=2.1, arch=0.45, z=0.34, col=acc, frame="stone", steps=2, lamp=True)
    P.window(f, W - 1.15, 1.15, w=0.9, h=1.2, shutters=acc)
    L.bay(f, W - 1.2, 3.0 + 0.35, w=1.8, h=4.95, out=0.5, col="white", rows=((0.55, 1.2), (3.2, 1.15)), rails=(2.15, 2.85), trim=acc,
          base="brackets", roof="slate", lights=3, drop=0.75)
    for z in (3.0 + 0.9, 5.7 + 0.85):
        P.window(f, 0.9, z, w=0.7, h=1.2, shutters=acc)
    for u, bx in ((1.0, True), (W - 1.0, False)):
        P.window(f, u, 8.3 + 0.78, w=0.75, h=1.0, shutters=acc, box=bx)
    L.porthole(f, c, H + 1.2, r=0.36)
    L.band_on(f, 2.92, h=0.14, u1=W - 2.2); L.band_on(f, H - 0.12, h=0.14)
    # --- sides above the neighbours
    P.window(bd.left, 1.5, 6.6, w=0.6, h=0.9); P.window(bd.left, 4.6, 9.1, w=0.6, h=0.9); P.window(bd.left, 2.2, 9.1, w=0.6, h=0.9)
    P.window(bd.right, 2.0, 9.1, w=0.6, h=0.9); P.window(bd.right, 4.7, 6.7, w=0.6, h=0.9)
    P.exposed(bd.left, "corners", n=8)
    # --- back
    k = bd.back
    P.door(k, 1.1, w=0.9, h=2.0, z=0.17, col=acc, frame="stone", steps=1)
    P.window(k, W - 1.1, 1.2, w=0.8, h=1.1)
    for z, sh in ((3.9, acc), (6.55, None), (9.05, acc)):
        P.window(k, 1.15, z, w=0.75, h=1.1, shutters=sh); P.window(k, W - 1.15, z, w=0.75, h=1.1, shutters=acc if sh is None else None)
    P.window(k, c, H + 0.7, w=0.6, h=0.9, arch=0.3)
    rise = bd.gable(ridge="y", pitch=58, eave=0.15, verge=0.34, barge=False, col="#f6dccb")
    L.barge_boards(bd, rise, eave=0.15, verge=0.34)
    L.cut_gable(k)
    top = H + rise
    tp = math.tan(rad(58))
    # --- the crow's nest: a boarded tub on a king post, strutted off the roof
    ny, nz, nr = 4.15, top + 0.34, 1.2
    b.beam((0, ny, top - 0.6), (0, ny, nz - 0.1), w=0.2, lod=1)
    P.gallery(b, 0.1, nr, nz, seg=14, rail="solid", rail_col="blackoak", gap=(-40, 40), brackets=6, bracket_drop=1.2, floor_col="greyoak",
              edge_col="blackoak", x=0, y=ny)
    with b.at(0, ny, nz):
        P.landing_mark(b, 0.72)
        b.disc(0.14, "planks", col="greyoak", seg=8, z=0.002)
        L.trapdoor(b, 0.48, 0.55, 0.0, w=0.6, d=0.6)
        with b.at(rz=300):                      # the glass, shipped on the rail
            with b.detail(2):
                b.beam((0, -nr + 0.1, 1.0), (0, -nr + 0.1, 1.18), w=0.04, mat="metal", col="brass", caps=False)
                b.tube((0, -nr + 0.42, 1.2), (0, -nr - 0.4, 1.36), r=0.04, r1=0.06, mat="metal", col="brass", n=6, caps=True)
    b.pad(0, ny, nz, radius=0.85, face=0, name="Crow's nest")
    P.flag(b, 0, ny + nr - 0.1, nz, pole=3.5, w=1.4, h=0.55, col="stripe_blue", kind="pennant")
    P.lantern_at(b, 0, ny + nr - 0.1, nz + 2.75, arm=0.28)
    # the way down: a hatch in the tiles and a ladder up under the tub
    hx = 1.3
    L.roof_window(b, hx, ny + 0.55, top - hx * tp + 0.02, 58, face=90, w=0.7, h=0.85)
    L.roof_ladder(b, (0.86, ny + 0.55, top - 0.86 * tp + 0.1), (0.5, ny + 0.55, nz - 0.16), w=0.4)
    # --- roof life
    P.chimney(b, -1.33, 5.6, H - 0.4, 4.6, w=0.6, d=0.7, mat="brick", pots=2)
    P.dormer(b, 1.38, 1.5, H + 0.98, w=0.85, h=0.8, depth=1.2, face=90, col="white", frame=acc)
    L.gull(b, 0.0, 1.2, top + 0.1, rz=-60)
    # --- the lane
    L.anchor(b, -c + 0.4 + 1.45, -0.12, 0, lean=12)
    P.barrel(b, c - 0.4, -0.4, r=0.27, h=0.7)
    L.flowerpot(b, -c + 0.25, -0.75, 0.0, flower="#3f6fb5", r=0.14)
    P.laundry(b, (-1.2, D + 0.3, 6.3), (1.6, D + 0.3, 6.5), n=4, sag=0.2)
    for x, z in ((-1.2, 6.3), (1.6, 6.5)):
        b.beam((x, D, z + 0.02), (x, D + 0.33, z + 0.02), w=0.05, lod=2)
