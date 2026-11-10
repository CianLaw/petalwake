# Harrow Beacon: an old watch tower on the hill, kept alight for the fishing boats; the keeper's girl stacks driftwood at its foot and feeds the basket at dusk.
# Massing: a battered square rubble tower 4.6 m -> 3.8 m, an outside stair to a raised door, a corbelled flat top inside a broken parapet,
#          a little cap-house over the stair head in the back corner, and an iron gibbet holding the fire basket over the front corner.
# Materials: warm rubble with pale quoins and corbels, a flagged roof, slate on the cap-house, wrought iron; accent red.
from kit import *
import parts as P
import parts_c as PC
import parts_f as F

META = {"name": "Harrow Beacon", "kind": "tower", "lot": (6.0, 6.0)}

CX, CY = 0.0, 3.05      # the tower's centre
W0, INSET = 4.6, 0.38
H = 12.4                # top of the shaft (and of the corbels)
TOP = 12.7              # the roof flags


def build(b):
    # ---- the shaft and its battered foot
    tb = PC.tbody(b, W0, W0, H, inset=INSET, mat="masonry", col="warm", x=CX, y=CY, depth=0.36)
    b.box(W0 + 0.56, W0 + 0.56, 1.0, "masonry", col="warm", x=CX, y=CY, taper=(W0 + 0.08) / (W0 + 0.56))
    b.box(W0 + 0.56, W0 + 0.56, 3.0, "masonry", col=shade("warm", 0.85), x=CX, y=CY, z=-3.0, top=False)
    c = W0 / 2
    P.door(tb.front, c + 0.6, w=0.95, h=2.0, z=1.8, arch=0.45, col="red", lamp=True)
    P.window(tb.front, c, 6.6, w=0.6, h=1.3, arch=0.3, shutters="red")
    F.slit(tb.front, c, 10.0, w=0.17, h=1.0)
    P.window(tb.right, c, 4.4, w=0.6, h=1.3, arch=0.3)
    F.slit(tb.right, c, 9.2, w=0.17, h=1.0)
    F.slit(tb.back, c, 2.6, w=0.17, h=1.0)
    P.window(tb.back, c, 6.6, w=0.6, h=1.3, arch=0.3)
    F.slit(tb.back, c, 10.0, w=0.17, h=1.0)
    F.slit(tb.left, c, 4.0, w=0.17, h=1.0)
    P.window(tb.left, c, 8.4, w=0.6, h=1.3, arch=0.3, shutters="red")
    PC.tquoins(tb, z0=1.0)
    PC.tband(tb, 8.9)
    for wl in tb.walls:
        P.stones(wl, n=9, z0=1.2, z1=11.6, u0=0.5, u1=W0 - 0.5, proud=0.05)
    P.ivy(tb.left, 1.2, 0.9, w=2.2, h=5.6, n=12)
    P.ivy(tb.back, 3.6, 0.9, w=1.6, h=3.2, n=7)

    # ---- the outside stair along the front, up to the raised door
    with b.at(-2.72, 0.32, 0.0, rz=-90):
        PC.outside_stair(b, n=9, w=1.1, rise=0.2, run=0.29, landing=1.55, rail="iron", rail_sides="r")

    # ---- the head: corbel table, flagged roof, broken parapet
    wt = W0 - 2 * INSET
    for (ox, oy, rz, ln) in PC.rect_sides(wt, wt, CX, CY):
        with b.at(ox, oy, 0.0, rz=rz):
            PC.corbel_row(b, ln, z=H, n=6, out=0.4, drop=0.6)
    S = wt + 0.8
    b.box(S, S, TOP - H, "masonry", col="warm", x=CX, y=CY, z=H, cap="flagstone", capcol="sand", bottom=True)
    PC.battlements(b, PC.rect_sides(S, S, CX, CY), z=TOP, t=0.34, wall=0.6, h=0.6, merlon=0.72, gap=0.5, mat="masonry", col="warm",
                   gaps={0: [(0.95, 3.3)], 1: [(1.15, 2.0)], 3: [(0.45, 1.75)]})
    hs = S / 2
    for (x, y, w_, h_) in ((-hs + 0.75, CY - hs + 0.17, 0.42, 0.5), (-hs + 0.98, CY - hs + 0.19, 0.3, 0.24), (hs - 1.1, CY - hs + 0.17, 0.5, 0.42),
                           (hs - 1.36, CY - hs + 0.2, 0.3, 0.2), (-hs + 0.17, CY + hs - 0.32, 0.4, 0.34), (-0.9, CY - hs - 0.02, 0.36, 0.16)):
        b.stone(w_, 0.34, h_, mat="masonry", col="warm", lod=1, x=x, y=y, z=TOP + 0.02, jitter=0.2)
    with b.detail(2):
        b.blob(0.2, 0.18, 0.14, mat="ivy", col="#8fc46a", x=-hs + 1.2, y=CY - hs + 0.2, z=TOP + 0.1, seg=5, rings=2, wind=0.4)
        b.blob(0.2, 0.18, 0.14, mat="ivy", col="#8fc46a", x=-hs + 0.2, y=CY + hs - 1.0, z=TOP + 0.12, seg=5, rings=2, wind=0.4)

    # ---- where the rider lands: the middle of the flags, in through the broken front
    b.pad(-0.25, CY - 0.55, TOP, radius=0.9, face=0, name="Beacon top")
    with b.at(-0.25, CY - 0.55, TOP):
        P.landing_mark(b, 0.85)

    # ---- the cap-house over the stair head (the way down)
    ch = b.body(1.5, 1.5, 1.9, mat="masonry", col="warm", x=CX + 1.2, y=CY + 1.2, z=TOP, foot=False)
    P.door(ch.front, 0.75, w=0.68, h=1.6, col="red", frame="timber", knob=True)
    F.slit(ch.right, 0.75, 0.7, w=0.14, h=0.7)
    F.slit(ch.back, 0.75, 0.7, w=0.14, h=0.7)
    rise = ch.hip(pitch=52, mat="slate", eave=0.2, course=0.3, thick=0.08)
    P.flag(b, CX + 1.2, CY + 1.2, TOP + 1.9 + rise - 0.1, pole=1.5, w=1.15, h=0.5, col="stripe_red")
    F.logs(b, CX + 1.25, CY - 1.3, TOP, n=3, L=0.8, rows=2, rz=90)
    F.bucket(b, CX + 0.2, CY + 1.55, TOP)

    # ---- the gibbet and its fire basket over the front-left corner
    px, py = CX - 1.72, CY - 1.72
    ex, ey = CX - 2.44, CY - 2.44
    with b.detail(1):
        b.tube((px, py, TOP), (px, py, TOP + 3.3), r=0.06, mat="metal", col="iron", n=6)
        b.beam((px, py, TOP + 3.2), (ex, ey, TOP + 3.45), w=0.07, mat="metal", col="iron")
        b.beam((px, py, TOP + 2.0), ((px + ex) / 2, (py + ey) / 2, TOP + 3.3), w=0.05, mat="metal", col="iron", caps=False)
        b.beam((px, py, TOP + 3.3), (px + 0.5, py + 0.5, TOP + 2.5), w=0.04, mat="metal", col="iron", caps=False)
    with b.detail(2):
        for k in range(3):
            a = rad(120 * k + 40)
            b.beam((ex, ey, TOP + 3.42), (ex + 0.43 * math.sin(a), ey - 0.43 * math.cos(a), TOP + 2.2), w=0.022, mat="metal", col="iron", caps=False)
    F.fire_basket(b, ex, ey, TOP + 1.6, r=0.42, h=0.58)

    # ---- at the foot: driftwood for the fire, a barrel, the meadow coming up to the walls
    F.logs(b, 2.1, 0.08, 0.0, n=3, L=1.3, rows=3)
    F.tool(b, 2.45, 0.44, 0.0, kind="fork", rz=0, lean=0.05)
    for (x, y) in ((-2.68, 1.7), (-2.68, 3.5), (-2.68, 4.9), (2.68, 2.0), (2.68, 4.2), (-1.2, 5.72), (0.9, 5.72)):
        F.flowers(b, x, y, 0.0, n=4, spread=0.2, h=0.26)
