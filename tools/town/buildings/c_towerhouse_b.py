# The Notary's tower-house: a narrow harled tower with crow-stepped gables. The notary had the corner turret built so he could see who was coming up the hill; his grand-daughter keeps its little gallery for the post.
# Massing: a tall narrow block set back behind a walled court and a lean-to porch; a round turret corbelled out of the front-left corner near the top, with a pulpit of a gallery on oak struts and a candle-snuffer roof well above the main ridge.
# Materials: stone ground storey, rose-washed harling above, ashlar corbelling and crow-steps, slate roofs. Accent: plum.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Notary's Tower-house", "kind": "tower", "lot": (7.0, 7.0), "lean": (0.0008, -0.0006)}

X0, X1, Y0, Y1 = -1.45, 3.2, 3.2, 6.64             # the main block
BW, BD = X1 - X0, Y1 - Y0
BX, BY = (X0 + X1) / 2, (Y0 + Y1) / 2
ZG, ZE = 3.2, 12.6                                # top of the stone storey, eaves
TX, TY, TR = -1.6, 3.05, 1.1                      # the turret
ZC, ZGAL, ZTT = 9.0, 14.3, 17.1                   # turret: foot of the drum, gallery, eaves
DX, DY, DR = TX, TY - 0.95, 1.8                   # the gallery: an off-centre round deck


def build(b):
    block(b)
    turret(b)
    gallery(b)
    porch(b)
    court(b)


def block(b):
    g = b.body(BW, BD, ZG, mat="masonry", col="warm", x=BX, y=BY)
    P.plinth(g, h=0.6)
    up = b.body(BW, BD, ZE - ZG, mat="plaster", col="rose", x=BX, y=BY, z=ZG)
    P.band(g, ZG - 0.1, h=0.2, out=0.07)
    P.quoins(up, z0=0.2, corners="rb", size=(0.5, 0.3, 0.5))
    P.quoins(g, z0=0.6, corners="frbl", size=(0.56, 0.32, 0.5))
    P.window(g.front, 0.9, 1.1, w=0.7, h=1.1, bars=(2, 1))
    P.window(g.left, 1.8, 1.2, w=0.7, h=1.1, bars=(2, 1))
    P.door(g.left, 2.9, w=0.85, h=1.95, col="plum", z=0.25, frame="timber", steps=1)
    P.window(g.back, 2.4, 1.2, w=0.7, h=1.1)
    # the harled floors: three storeys of windows, none quite above another
    for wl, spec in ((up.front, ((1.6, 1.0, True), (3.6, 1.0, False), (2.6, 3.9, True), (1.5, 6.7, False), (3.5, 6.7, True))),
                     (up.left, ((1.5, 1.2, False), (2.3, 4.0, True))),
                     (up.right, ((1.9, 1.1, True), (1.6, 4.6, False))),
                     (up.back, ((1.4, 1.1, False), (3.4, 1.1, True), (2.4, 4.0, False), (1.5, 6.8, True), (3.4, 6.8, False)))):
        for (u, z, bx) in spec:
            edge = wl in (up.back, up.right)              # the lot line is close behind these walls: no flower boxes there
            P.window(wl, u, z, w=0.78, h=1.3, shutters="plum" if (bx or (z > 6 and not edge)) else None, box=bx and not edge, ajar=6 if edge else None)
    P.exposed(up.front, "corners", n=6)
    P.exposed(up.back, "both", n=8)
    rise = up.gable(ridge="x", pitch=56, mat="slate", eave=0.2, verge=0.0, barge=False, sag=0.06)
    with b.at(X0, Y1, ZE, rz=270):
        PC.crow_steps(b, BD, rise, t=0.36, n=5, mat="plaster", col="rose")
    with b.at(X1, Y0, ZE, rz=90):
        PC.crow_steps(b, BD, rise, t=0.36, n=5, mat="plaster", col="rose")
    PC.stack(b, X0 + 0.2, BY, ZE + rise - 0.6, 2.7, w=0.4, d=0.8, flues=2, style="square")
    PC.stack(b, X1 - 0.2, BY, ZE + rise - 0.6, 2.2, w=0.4, d=0.8, flues=1, style="square")
    P.dormer(b, 2.0, Y0 + 0.55, ZE + 0.55, w=1.0, h=0.95, depth=1.3, face=0, roof="slate", col="rose", shutters="plum")
    P.ivy(g.back, 3.9, 0.3, w=1.6, h=2.6, n=6, lod=2)


def turret(b):
    """The corner turret: corbelled out of the corner in ashlar rings, harled drum, candle-snuffer."""
    with b.at(TX, TY):
        PC.lathe(b, [(0.14, 7.25), (0.4, 7.45), (0.4, 7.62), (0.64, 7.9), (0.64, 8.07), (0.88, 8.35), (0.88, 8.52), (TR + 0.04, 8.83), (TR + 0.04, ZC)],
                 "ashlar", col="stone", seg=16)
        with b.detail(1):
            b.blob(0.2, 0.2, 0.24, mat="ashlar", col="stone", z=7.12, seg=6, rings=4, rough=0.0)
        tr = PC.ring(b, TR, ZTT - ZC, mat="plaster", col="rose", z=ZC, seg=16, seam=120, foot=False, depth=0.22)
        tr.cell = 3.0
        P.window(tr, 292, 1.6, w=0.5, h=1.05, arch=0.25)
        P.window(tr, 15, 3.1, w=0.5, h=1.05, arch=0.25, shutters="plum")
        P.door(tr, 0, w=0.7, h=1.8, z=ZGAL - ZC + 0.03, col="plum", frame="timber")
        for deg in (255, 62):
            P.window(tr, deg, ZGAL - ZC + 1.0, w=0.45, h=0.9, arch=0.22, lintel=None)
        P.lantern(tr, 318, ZGAL - ZC + 1.75)
        P.ring_band(b, TR - 0.02, ZTT - 0.22, h=0.16, out=0.08, seg=16)
        b.cone_roof(TR, 4.3, mat="slate", z=ZTT, seg=16, eave=0.25, flare=0.75, course=0.5)
        P.flag(b, 0, 0, ZTT + 4.3 + 1.2, pole=1.3, w=1.1, h=0.45, col="stripe_red")
    PC.doves(b, [(TX + 0.5, TY - 0.2, ZTT + 0.42), (X0 + 1.4, BY, ZE + 2.52)])


def gallery(b):
    """The gallery: a round deck hung off-centre on the front of the turret, open toward the street."""
    with b.at(DX, DY, ZGAL):
        b.disc(DR, "planks", col="greyoak", seg=18)
        b.disc(DR, "planks", col=shade("darkoak", 0.8), seg=18, z=-0.14, down=True)
        b.revolve([(DR, -0.14), (DR, 0.0)], "planks", col="darkoak", seg=18)
        PC.rail_arc(b, DR - 0.08, 24, 142, style="balusters", col="darkoak", h=0.98, posts_at=1.25)
        PC.rail_arc(b, DR - 0.08, 218, 336, style="balusters", col="darkoak", h=0.98, posts_at=1.25)
        for a in (-84, -42, 0, 42, 84):               # oak struts from the drum (three are always drawn)
            ex, ey, _ = PC.polar(DR - 0.1, a)
            sx, sy, _ = PC.polar(TR, a * 0.62)
            b.beam((sx, sy + 0.95, -1.7), (ex, ey, -0.16), w=0.14, lod=0 if a in (-84, 0, 84) else 1)
            b.beam((sx * 0.6, sy * 0.6 + 0.95, -0.21), (ex, ey, -0.21), w=0.12, h=0.13, lod=2)
        with b.at(0, -0.93):
            P.landing_mark(b, 0.7)
        b.pad(0, -0.93, 0.0, radius=0.75, face=0, name="Turret gallery")
        x, y, _ = PC.polar(DR - 0.36, 96)
        P.planter(b, x, y, 0, w=0.5, d=0.26, h=0.24)


def porch(b):
    """The lean-to porch in front of the tower: the street door."""
    fb = b.body(2.85, 3.1, 2.7, mat="masonry", col="warm", x=1.72, y=1.65)
    PC.plinth(fb, h=0.5, doors=[("front", 1.05, 1.0)])
    P.door(fb.front, 1.05, w=1.0, h=2.05, arch=0.4, col="plum", z=0.2, steps=1, lamp=True)
    P.window(fb.front, 2.3, 1.05, w=0.7, h=1.0, shutters="plum", box=True)
    P.window(fb.left, 1.5, 1.1, w=0.7, h=1.0)
    P.sign(fb.front, 0.28, 2.5, emblem="key", col="mustard", board="plum")
    rise = PC.shed_roof(b, 2.85, 3.16, pitch=30, z=2.7, x=1.72, y=Y0 + 0.04, mat="slate", eave=0.06, verge=0.1, course=0.4, barge=False)
    PC.cheeks(b, 2.85, 3.1, 3.1 * math.tan(rad(30)), mat="masonry", col="warm", x=1.72, y=Y0, z=2.7)
    P.chimney(b, 2.7, 2.6, 3.3, 2.6, w=0.5, d=0.45, mat="brick", pots=1)


def court(b):
    """The walled court under the turret: a gate, a pear tree, a seat."""
    PC.garden_wall(b, (-3.3, 0.14), (0.3, 0.14), h=1.45, gate=(1.65, 1.1))
    with b.at(-1.65, 0.31):
        PC.gate_piers(b, w=1.1, h=1.75, size=0.42)
        PC.wood_gate(b, w=1.1, h=1.25, col="plum", pickets=True, arch=1)
    wl = PC.garden_wall(b, (-3.3, 6.8), (-3.3, 0.14), h=1.7)
    PC.garden_wall(b, (X0, 6.8), (-3.3, 6.8), h=1.7)
    P.tree(b, -2.25, 5.3, h=3.9, crown=0.8, col="#79b85c")
    P.bench(b, -2.55, 2.3, rz=90, w=1.3)
    PC.flowers(b, -0.5, 0.75, 0, w=1.3, d=0.5, n=5)
    PC.flowers(b, -2.75, 0.8, 0, w=0.8, d=0.6, n=4)
    P.barrel(b, -1.95, 3.5, r=0.26, h=0.7)
