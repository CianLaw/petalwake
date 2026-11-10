# The apothecary under the arches: the corner of the house stands open on stone piers, the shop is in the shelter behind them, and a lamp burns in the lantern on the roof for anyone who needs him at night.
# Corner house, streets to the front and the right: a dressed-stone ground storey with an arched porch cut out of the corner; two plastered storeys over; a steep pavilion roof cut off flat and crowned with a glazed lantern.
# Ochre plaster over pale ashlar, terracotta tiles, a lead flat; accent blue.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC
import parts_m as PM

META = {"name": "The Apothecary's Arches", "kind": "shop", "lot": (7.5, 8.0), "terrace": True, "fronts": ["front", "right"]}


def build(b):
    acc = "blue"
    x0, x1, D = -3.45, 3.25, 7.7           # the side street runs down the right
    W, cx = x1 - x0, (x0 + x1) / 2
    H0, H = 3.4, 5.2
    top = H0 + H
    a, th = 2.8, 0.42                       # the porch: one arched bay to each street
    arch = [(a / 2 + 0.02, 2.0, 2.85, 1.0)]
    b.footprint(x0, 0, x1, D, top)
    # --- the ground storey: arcades at the corner, plain walls elsewhere
    with b.at(x1 - a, 0, 0):
        fa, _ = PM.arcade(b, a, H0, thick=th, arches=arch, mat="ashlar", col="warm", top=False, ends="")
    with b.at(x1, 0, 0, rz=90):
        ra, _ = PM.arcade(b, a, H0, thick=th, arches=[(a / 2 - 0.02, 2.0, 2.85, 1.0)], mat="ashlar", col="warm", top=False, ends="")
    with b.at(x0, 0, 0):
        fw = b.wall(x1 - a - x0, H0, "ashlar", "warm")
    with b.at(x1, a, 0, rz=90):
        rw = b.wall(D - a, H0, "ashlar", "warm")
    with b.at(x1, D, 0, rz=180):
        bw = b.wall(W, H0, "ashlar", "warm")
    with b.at(x0, D, 0, rz=270):
        lw = b.wall(D, H0, "ashlar", "warm")
    with b.at(x1 - a, a, 0):
        pw = b.wall(a - th, H0, "plaster", "cream")          # back of the porch
    with b.at(x1 - a, th, 0, rz=90):
        ps = b.wall(a - th, H0, "plaster", "cream")          # its inner side
    P.plinth(L.Walls(b, [fw, fa, ra, rw, bw, lw], front=fw), h=0.34, mat="ashlar", col="grey")
    L.arch_dress(fa, a / 2 + 0.02, 0, 2.0, 2.85, 1.0, col="stone")
    L.arch_dress(ra, a / 2 - 0.02, 0, 2.0, 2.85, 1.0, col="stone")
    pcx, pcy = x1 - th - (a - th) / 2, th + (a - th) / 2
    b.box(a - th, a - th, 0.07, "flagstone", col="sand", x=pcx, y=pcy, z=0.0)
    L.shopfront(pw, 0.12, pw.w - 0.1, h=2.75, z=0.07, col=acc, door=0.72, door_w=0.9, lights=2, riser=0.5)
    P.window(ps, ps.w / 2 + 0.05, 1.0, w=1.3, h=1.45, bars=(2, 2), lintel="timber")
    with ps.on(ps.w / 2 + 0.05, 1.02):
        with b.at(0, 0.08, 0):
            PM.display(b, 1.05, kind="bottles", depth=0.12)
    P.lantern_at(b, pcx + 0.1, pcy + 0.32, H0 - 0.55, arm=0.3)
    with b.detail(1):
        for yy in (th + 0.5, th + 1.2, th + 1.9):
            b.beam((x1 - a, yy, H0 - 0.1), (x1 - th, yy, H0 - 0.1), w=0.14, h=0.18)
    L.shopfront(fw, 0.4, 3.3, h=2.75, z=0.34, col=acc, lights=3, riser=0.5)
    with fw.on(1.85, 0.34 + 0.52):
        with b.at(0, 0.06, 0):
            PM.display(b, 2.2, kind="bottles", depth=0.1)
    P.window(rw, 1.3, 1.1, w=0.9, h=1.3, shutters=acc)
    P.door(rw, 3.6, w=0.9, h=2.05, z=0.17, col=acc, frame="stone", steps=1)
    # --- two plastered storeys
    up = b.body(W, D, H, mat="plaster", col="ochre", x=cx, z=H0, floor="planks")
    P.band(up, -0.14, h=0.22, out=0.07)
    P.quoins(up, corners="r", col="stone")
    for u, bx in ((1.2, False), (3.35, True), (5.5, False)):
        P.window(up.front, u, 0.9, w=0.85, h=1.3, shutters=acc, box=bx)
        P.window(up.front, u, 3.5, w=0.8, h=1.1, shutters=acc)
    for u, bx in ((1.4, True), (3.85, False), (6.3, True)):
        P.window(up.right, u, 0.9, w=0.85, h=1.3, shutters=acc, box=bx)
        P.window(up.right, u, 3.5, w=0.8, h=1.1, shutters=acc)
    P.window(up.left, 3.2, 3.55, w=0.6, h=0.9); P.window(up.back, 2.2, 3.55, w=0.6, h=0.9); P.window(up.back, 4.8, 3.55, w=0.6, h=0.9)
    P.exposed(up.left, "corners", n=8); P.exposed(up.back, "corners", n=6)
    L.sign(up.front, W - 0.22, 0.85, emblem="bottle", col=acc, board="ivory")
    # --- the roof: a steep pavilion cut off flat, with the night lantern on top
    tp = math.tan(rad(54))
    cut, flat = L.hip_roof(b, W, D, pitch=54, x=cx, y=D / 2, z=top, eave=(0.38, 0.38, 0.12, 0.12), cut=2.7)
    lz = top + cut
    with b.at(cx, D / 2, lz):
        b.box(1.5, 1.5, 0.28, "planks", col=acc, lod=0)
        b.box(0.95, 0.95, 1.15, "glow", col="#ffd88a", z=0.28, top=False)
        with b.detail(1):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    b.beam((sx * 0.6, sy * 0.6, 0.28), (sx * 0.6, sy * 0.6, 1.5), w=0.13, mat="planks", col="ivory", caps=False)
            for (p0, p1) in (((-0.6, -0.6), (0.6, -0.6)), ((0.6, -0.6), (0.6, 0.6)), ((0.6, 0.6), (-0.6, 0.6)), ((-0.6, 0.6), (-0.6, -0.6))):
                b.beam((p0[0], p0[1], 0.9), (p1[0], p1[1], 0.9), w=0.05, mat="planks", col="ivory", caps=False)
                mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
                b.beam((mx, my, 0.28), (mx, my, 1.5), w=0.05, mat="planks", col="ivory", caps=False)
        b.box(1.56, 1.56, 0.12, "planks", col="ivory", z=1.5, bottom=True)
        b.loop_roof(1.5, 1.5, pitch=50, mat="slate", z=1.62, eave=0.16, course=0.3, thick=0.08)
        L.ball(b, 0, 0, 1.62 + 0.75 * math.tan(rad(50)) - 0.05, r=0.13, mat="metal", col="lead")
        PC.vane(b, 0, 0, 1.62 + 0.75 * math.tan(rad(50)) + 0.3, h=1.2, shape="moon", cardinals=False)
    b.lamp(cx, D / 2, lz + 0.9, strength=1.4)
    for x in (cx - 1.35, cx + 1.35):
        P.dormer(b, x, 0.82, top + 0.82 * tp - 0.12, w=0.9, h=1.0, depth=1.2, face=0, col="ochre", frame="ivory")
    for y in (D / 2 - 1.5, D / 2 + 1.5):
        P.dormer(b, x1 - 0.82, y, top + 0.82 * tp - 0.12, w=0.9, h=1.0, depth=1.2, face=90, col="ochre", frame="ivory")
    P.chimney(b, x0 + 0.42, 2.8, top + 0.1, 4.4, w=0.66, d=0.9, mat="brick", pots=2)
    P.chimney(b, cx + 0.3, D - 0.42, top + 0.1, 4.2, w=0.9, d=0.66, mat="brick", pots=2)
    # --- the pavement
    P.bench(b, x1 - a + 0.3, th + 1.2, 0.07, rz=-90, w=1.3)
    L.cat(b, x1 - a + 0.3, th + 0.95, 0.55, rz=-90, col="#e9e4d8")
    P.planter(b, x1 - a - 0.45, -0.38, 0, w=0.42, d=0.42, bush=True)
    L.flowerpot(b, x1 + 0.18, a + 0.5, 0, r=0.15, h=0.3, tall=1.4)
    P.crate(b, x0 + 0.45, -0.45, s=0.5, rz=8); P.crate(b, x0 + 0.5, -0.45, z=0.5, s=0.36, rz=-12)
