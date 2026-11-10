# The fish market hall: the night's catch is cried here at first light; by noon the slabs are sluiced and the gulls own the ridge.
# An open arcade (stone piers at the corners and middles, oak posts on pad stones between) under one great sweeping hipped
# tile roof with a louvred lantern; the auctioneer's teal booth is tucked in the walled back corner. Warm rubble, oak, terracotta; accent teal.
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "Larkhaven Fish Market", "kind": "market", "lot": (14.0, 9.0)}

W, D, CY = 12.4, 7.4, 4.45          # the line of the piers, and its middle
HP, FZ = 3.3, 0.3                   # wall-plate height, floor height
SEC = [(0.0, 0.0), (1.3, 0.75), (3.7, 4.0)]
EAVE = 0.7
TEAL = paint("#3b8f8a")


def table(b, x, y, rz=0.0, w=2.3, d=0.85):
    """A stone fish slab on two stone legs; returns nothing, dress it at z = FZ + 0.9."""
    with b.at(x, y, FZ, rz=rz):
        with b.detail(1):
            for sx in (-1, 1):
                b.box(0.28, d * 0.8, 0.78, "masonry", col="grey", x=sx * (w / 2 - 0.3))
            b.box(w, d, 0.12, "ashlar", col="stone", z=0.78, bottom=True)


def build(b):
    # ------------------------------------------------------------------ the floor
    b.box(W + 0.9, D + 0.9, FZ, "masonry", col="warm", y=CY, cap="flagstone", capcol="sand", lod=0)
    b.box(W + 0.9, D + 0.9, 3.0, "masonry", col=shade("warm", 0.85), y=CY, z=-3.0, top=False, lod=0)
    b.footprint(-W / 2 - 0.45, CY - D / 2 - 0.45, W / 2 + 0.45, CY + D / 2 + 0.45, HP + 4.0)
    b.box(6.8, 0.42, 0.15, "ashlar", col="stone", y=CY - D / 2 - 0.45 - 0.2, lod=1)
    y0, y1 = CY - D / 2, CY + D / 2

    # ------------------------------------------------------------------ piers, posts, plates
    piers = {}
    for (px, py) in ((-6.2, y0), (0.0, y0), (6.2, y0), (-6.2, y1), (0.0, y1), (6.2, y1)):
        pr = b.body(0.8, 0.8, HP - FZ - 0.8, mat="masonry", col="warm", x=px, y=py, z=FZ, foot=False)
        piers[(px, py)] = pr
        b.box(0.94, 0.94, 0.28, "ashlar", col="stone", x=px, y=py, z=HP - 0.8, lod=0, bottom=True)
        b.box(0.5, 0.5, 0.28, "timber", col="darkoak", x=px, y=py, z=HP - 0.52, lod=0)
        P.stones(pr.front, n=3, size=(0.26, 0.4))

    def post(px, py, top, braces):
        with b.at(px, py, FZ):
            b.stone(0.52, 0.52, 0.42, mat="ashlar", col="sand", lod=0, ch=0.2, jitter=0.06)
            b.beam((0, 0, 0.4), (0, 0, top - FZ), w=0.26, mat="timber", col="darkoak", lod=0)
            with b.detail(1):
                for (dx, dy) in braces:
                    b.beam((0, 0, HP - FZ - 1.2), (dx * 0.98, dy * 0.98, HP - FZ - 0.3), w=0.14, mat="timber", col="darkoak")

    for px in (-3.1, 3.1):
        post(px, y0, HP - 0.26, ((-1, 0), (1, 0)))
        post(px, y1, HP - 0.26, ((-1, 0), (1, 0)))
    for px in (-6.2, 6.2):
        post(px, CY, HP - 0.26, ((0, -1), (0, 1)))
    post(-3.1, CY, 6.35, ((-1, 0), (1, 0), (0, -1), (0, 1)))
    post(3.1, CY, 6.35, ((-1, 0), (1, 0), (0, -1), (0, 1)))
    post(0.0, CY, 6.4, ((-1, 0), (1, 0), (0, -1), (0, 1)))
    zp = HP - 0.13
    for (a, e) in (((-6.2, y0), (6.2, y0)), ((6.2, y0), (6.2, y1)), ((6.2, y1), (-6.2, y1)), ((-6.2, y1), (-6.2, y0))):
        b.beam((a[0], a[1], zp), (e[0], e[1], zp), w=0.26, h=0.26, mat="timber", col="darkoak", lod=0)
    with b.detail(1):
        for px in (-3.1, 0.0, 3.1):
            b.beam((px, y0, zp), (px, y1, zp), w=0.22, h=0.24, mat="timber", col="darkoak")
        b.beam((-6.2, CY, zp), (6.2, CY, zp), w=0.22, h=0.24, mat="timber", col="darkoak")

    # ------------------------------------------------------------------ the great roof, boarded underneath
    b.loop_roof(W, D, section=SEC, mat="tiles", x=0, y=CY, z=HP, eave=EAVE, course=0.44, thick=0.16)
    H.hip_rolls(b, W, D, SEC, z=HP, x=0, y=CY, mat="tiles", eave=EAVE)

    def loop(inset, zz):
        a, c = max(W / 2 - inset, 0.0), max(D / 2 - inset, 0.0)
        return [(-a, -c, zz), (a, -c, zz), (a, c, zz), (-a, c, zz)]

    with b.at(0, CY, HP - 0.15):
        for (ra, za), (rb, zb) in zip(SEC, SEC[1:]):
            A, B = loop(ra, za), loop(rb, zb)
            for i in range(4):
                j = (i + 1) % 4
                b.face((A[j], A[i], B[i], B[j]), "planks", col=shade("darkoak", 0.9 + 0.1 * (i % 2)), lod=0)

    # ------------------------------------------------------------------ the louvred lantern on the ridge
    cb = b.body(1.9, 1.9, 2.0, mat="planks", col="greyoak", x=0, y=CY, z=6.5, foot=False, depth=0.14)
    H.louvre(cb.front, 0.95, 0.5, w=1.3, h=1.25, n=7)
    H.louvre(cb.back, 0.95, 0.5, w=1.3, h=1.25, n=7)
    H.louvre(cb.left, 0.95, 0.95, w=1.3, h=0.8, n=5)
    H.louvre(cb.right, 0.95, 0.95, w=1.3, h=0.8, n=5)
    with b.detail(1):
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.beam((sx * 0.95, CY + sy * 0.95, 6.5), (sx * 0.95, CY + sy * 0.95, 8.5), w=0.16, mat="timber", col="darkoak")
    CSEC = [(0.0, 0.0), (0.4, 0.22), (0.95, 1.3)]
    b.loop_roof(1.9, 1.9, section=CSEC, mat="tiles", x=0, y=CY, z=8.5, eave=0.42, course=0.3, thick=0.1)
    H.hip_rolls(b, 1.9, 1.9, CSEC, z=8.5, x=0, y=CY, mat="tiles", eave=0.42, ridge=False)
    PC.vane(b, 0, CY, 9.7, h=1.6, shape="fish", size=1.2)
    H.gull(b, -2.3, CY, 7.42, rz=70)
    H.gull(b, 2.0, CY, 7.42, rz=200)
    H.gull(b, 0.6, CY - 0.5, 9.4, rz=330, s=0.95)

    # ------------------------------------------------------------------ the walled back corner and the auctioneer's booth
    hw = HP - FZ - 0.26
    with b.at(5.8, y1 + 0.2, FZ, rz=180):
        bw = b.wall(5.4, hw, mat="masonry", col="warm", back="masonry", thick=0.4)
    P.window(bw, 1.4, 1.15, w=0.7, h=0.8, frame="ivory", lintel="timber")
    P.window(bw, 3.9, 1.15, w=0.7, h=0.8, frame="ivory", lintel="timber")
    P.ivy(bw, 4.8, 0.0, w=1.6, h=2.6, n=7)
    with b.at(6.4, CY + 0.3, FZ, rz=90):
        rw = b.wall(3.0, hw, mat="masonry", col="warm", back="masonry", thick=0.4)
    P.window(rw, 1.5, 1.15, w=0.7, h=0.8, frame="ivory", lintel="timber")
    ob = b.body(2.8, 2.2, 2.45, mat="planks", col=TEAL, x=4.5, y=6.75, z=FZ, foot=False, depth=0.12)
    P.door(ob.front, 0.7, w=0.8, h=1.9, col="ivory", frame="timber", z=0.03)
    P.window(ob.front, 1.95, 1.0, w=0.9, h=0.8, frame="ivory", lintel=None)
    P.window(ob.left, 1.1, 1.0, w=0.7, h=0.8, frame="ivory", lintel=None)
    H.battens(ob.front, col=TEAL)
    H.battens(ob.left, col=TEAL)
    b.box(3.0, 2.4, 0.08, "planks", col="darkoak", x=4.5, y=6.75, z=FZ + 2.45, lod=0, bottom=True)
    P.crate(b, 4.0, 6.9, FZ + 2.53, s=0.55, rz=15)
    P.crate(b, 5.0, 6.6, FZ + 2.53, s=0.45, rz=-20)
    H.basket(b, 4.55, 7.3, FZ + 2.53, r=0.26, fill=None)
    with b.detail(2):      # the counter under the hatch, and the hand bell on it
        b.box(1.0, 0.3, 0.05, "planks", col="darkoak", x=3.1 + 1.95, y=5.5, z=FZ + 0.95, bottom=True)
    H.small_bell(b, 3.1 + 2.2, 5.5, FZ + 1.3, r=0.1)

    # ------------------------------------------------------------------ the slabs and the catch
    for (tx, fill) in ((-4.6, H.SILVER), (-1.55, "#d98f7a"), (1.55, H.SILVER)):
        table(b, tx, y0 + 1.25)
        H.fish_box(b, tx - 0.6, y0 + 1.25, FZ + 0.9, rz=4, fill=fill)
        H.fish_box(b, tx + 0.45, y0 + 1.2, FZ + 0.9, rz=-6, fill=H.SILVER)
    table(b, -5.0, CY + 1.3, rz=90)
    H.basket(b, -5.0, CY + 0.7, FZ + 0.9, r=0.26)
    H.basket(b, -5.05, CY + 1.75, FZ + 0.9, r=0.28, fill="#3d4a55")
    H.fish_line(b, (-5.75, y0, 2.72), (-3.3, y0, 2.72), n=9, size=0.34)
    H.fish_line(b, (-6.2, y0 + 0.5, 2.72), (-6.2, CY - 0.3, 2.72), n=8, size=0.3, col="#d9b08a")
    with b.at(0.9, y0 + 1.1, zp - 0.12):      # the market scales
        with b.detail(2):
            b.beam((0, 0, 0), (0, 0, -0.5), w=0.03, mat="metal", col="iron", caps=False)
            b.beam((-0.55, 0, -0.5), (0.55, 0, -0.5), w=0.04, mat="metal", col="brass")
            for sx in (-1, 1):
                for dx in (-0.16, 0.16):
                    b.beam((sx * 0.52, 0, -0.5), (sx * 0.52 + dx, 0, -1.1), w=0.015, mat="metal", col="iron", caps=False)
                with b.at(sx * 0.52, 0, -1.12):
                    b.revolve([(0.0, -0.03), (0.2, 0.0), (0.22, 0.04)], "metal", col="brass", seg=8)
    P.barrel(b, 5.5, y0 + 0.9, FZ, r=0.3, h=0.8)
    P.barrel(b, 4.85, y0 + 1.5, FZ, r=0.28, h=0.75)
    H.basket(b, 3.75, y0 + 0.7, FZ, r=0.3, fill="#3d4a55")
    P.crate(b, -5.5, y1 - 0.9, FZ, s=0.65, rz=10)
    P.crate(b, -5.45, y1 - 0.95, FZ + 0.65, s=0.5, rz=-12)
    H.fish_box(b, -4.6, y1 - 0.8, FZ, rz=80)
    H.cat(b, -0.7, y0 + 0.45, FZ, rz=140, col="!#d98a3d")
    H.net_heap(b, -2.6, y1 - 0.7, FZ, r=0.5)
    P.sign(piers[(-6.2, y0)].front, 0.4, 2.3, emblem="fish", col="teal", board="ivory", out=0.8)
    P.lantern_at(b, -3.1, y0 - 0.14, 2.55)
    P.lantern_at(b, 3.1, y0 - 0.14, 2.55)
    P.lantern_at(b, 0.0, CY - 0.14, 2.7)
