# The Sailors' Chapel: raised by the fishing families for those the sea kept; its wheel window is said to be a ship's
# wheel in stone, and the bells that answer it hang in the old tower next door.
# Massing: a tall narrow nave with a steep slate roof and its gable to the square (door, wheel window, a little
# bellcote), stepped buttresses down both flanks, a round apse at the east end and a lean-to vestry on one side.
# Materials: warm rubble with pale ashlar buttress caps, surrounds and wheel, slate roofs, tinted glass; plum doors.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Sailors' Chapel", "kind": "chapel", "lot": (9.0, 15.0)}

A = "plum"
NX, NW = -0.3, 6.4            # the nave: centre line and width
Y0, NL, NH = 0.65, 10.55, 5.6  # its front wall, length and wall height
GLASS = "#86a8d6"


def bellcote(b, x, y, z):
    """A little stone bell-gable riding the ridge at the west end."""
    with b.at(x, y, z):
        b.box(1.2, 0.5, 0.45, "ashlar", col="stone", z=-0.25)
        for sx in (-1, 1):
            b.box(0.26, 0.46, 1.0, "ashlar", col="stone", x=sx * 0.44, z=0.2)
        b.box(1.2, 0.5, 0.18, "ashlar", col="stone", z=1.2, bottom=True)
        b.gable_roof(1.2, 0.5, pitch=48, mat="slate", x=0, y=0, z=1.38, ridge="y", eave=0.1, verge=0.08, course=0.3, thick=0.06, barge=False, ridge_roll=False)
        b.tri((-0.6, -0.25, 1.38), (0.6, -0.25, 1.38), (0, -0.25, 2.04), "ashlar", col="stone")
        b.tri((0.6, 0.25, 1.38), (-0.6, 0.25, 1.38), (0, 0.25, 2.04), "ashlar", col="stone")
        P.bell(b, 0, 0, 1.12, r=0.2, beam=0.7)
        Q.ball(b, 0, 0, 2.02, r=0.09, mat="metal", col="copper")


def build(b):
    nave = b.body(NW, NL, NH, mat="masonry", col="warm", x=NX, y=Y0 + NL / 2)
    P.plinth(nave, h=0.8, out=0.1, col=shade("warm", 0.92))
    x0, x1, y1 = NX - NW / 2, NX + NW / 2, Y0 + NL
    # --- the west front: door, two little lancets, the wheel window in the gable
    P.door(nave.front, NW / 2, w=1.6, h=3.0, z=0.34, arch=0.8, col=A, frame="stone", double=True, lamp=True)
    Q.steps(nave.front, NW / 2, w=2.3, n=2, z=0.34)
    for u in (1.4, NW - 1.4):
        P.window(nave.front, u, 2.0, w=0.45, h=1.6, arch=0.22, bars=(0, 3), lintel=None, sill=False, glass=GLASS)
    for sx in (-1, 1):
        with b.at(NX + sx * (NW / 2 - 0.4), Y0, 0):
            Q.buttress(b, w=0.7, d=0.6, h=5.3, steps=3, top_d=0.2)
    # --- the flanks: buttresses and lancets between them
    lanc = dict(w=0.7, h=2.6, arch=0.35, bars=(1, 4), lintel=None, sill=False, glass=GLASS)
    for yb in (Y0 + 0.4, 4.15, 7.65, y1 - 0.4):
        with b.at(x0, yb, 0, rz=270):
            Q.buttress(b, w=0.7, d=0.7, h=4.7, steps=2)
    for yb in (Y0 + 0.4, 4.15, y1 - 0.4):
        with b.at(x1, yb, 0, rz=90):
            Q.buttress(b, w=0.7, d=0.7, h=4.7, steps=2)
    for yw in (2.45, 5.9, 9.35):
        P.window(nave.left, y1 - yw, 1.9, **lanc)
        Q.surround(nave.left, y1 - yw, 1.9, 0.7, 2.6, arch=0.35, t=0.14, keystone=False)
    for yw in (2.45, 5.9):
        P.window(nave.right, yw - Y0, 1.9, **lanc)
        Q.surround(nave.right, yw - Y0, 1.9, 0.7, 2.6, arch=0.35, t=0.14, keystone=False)
    P.stones(nave.left, n=14, z0=0.9)
    P.stones(nave.front, n=8, z0=3.6)
    P.ivy(nave.left, y1 - 7.4, 0.3, w=1.8, h=3.6, n=7)
    # --- the roof, the wheel window, the bellcote
    rise = nave.gable(ridge="y", pitch=56, mat="slate", sag=0.1, eave=0.35, verge=0.22)
    Q.gable_holes(nave.front)
    Q.gable_holes(nave.back)
    Q.round_window(nave.front, NW / 2, NH + 1.55, r=0.95, spokes=8, glass=GLASS)
    Q.round_window(nave.back, NW / 2, NH + 2.75, r=0.45, spokes=4, glass=GLASS)
    bellcote(b, NX, Y0 + 0.15, NH + rise)
    # --- the apse: three lancets, two small buttresses, a half-cone of slate against the east gable
    ax, ay = NX, y1
    P.round_base(b, 2.5, h=0.8, out=0.2, seg=14, x=ax, y=ay)
    ap = b.round(2.5, 4.6, mat="masonry", col="warm", seg=14, x=ax, y=ay)
    for a in (128, 180, 232):
        P.window(ap, a, 1.7, w=0.55, h=1.9, arch=0.27, bars=(0, 3), lintel=None, sill=False, glass=GLASS)
    for a in (154, 206):
        with b.at(ax, ay, 0, rz=a):
            with b.at(0, -2.5, 0):
                Q.buttress(b, w=0.5, d=0.5, h=3.7, steps=2, top_d=0.25)
    Q.cone_part(b, 2.5, 2.7, a0=90, a1=270, mat="slate", x=ax, y=ay, z=4.6, seg=8, eave=0.3, flare=0.3, course=0.5)
    P.ring_band(b, 2.5, 4.3, h=0.3, out=0.1, seg=14, x=ax, y=ay)
    # --- the vestry: a lean-to with its own door and chimney
    v = b.body(1.4, 3.6, 2.5, mat="masonry", col="warm", x=x1 + 0.7, y=8.8)
    Q.plinth(v, h=0.4, walls="frb")
    P.door(v.front, 0.7, w=0.8, h=1.9, z=0.1, col=A, frame="timber")
    P.window(v.right, 1.8, 1.0, w=0.6, h=0.9, arch=0.2, bars=(1, 1))
    rs = Q.lean_to(b, 3.6, 1.4, pitch=35, x=x1, y=8.8, z=2.5, face=90, mat="slate", eave=0.1, verge=0.15, course=0.35)
    b.tri((x1, 7.0, 2.5), (x1 + 1.4, 7.0, 2.5), (x1, 7.0, 2.5 + rs), "masonry", col="warm")
    b.tri((x1 + 1.4, 10.6, 2.5), (x1, 10.6, 2.5), (x1, 10.6, 2.5 + rs), "masonry", col="warm")
    P.chimney(b, x1 + 1.0, 10.25, 2.3, 2.5, w=0.45, d=0.45, mat="masonry", col="warm", pots=1)
    # --- the chapel yard
    P.bench(b, x1 + 0.3, 2.45, 0, w=1.5, rz=90)
    P.planter(b, NX + 1.75, 0.3, 0, w=0.6, bush=True)
    P.tree(b, 3.2, 12.9, 0, h=4.8, crown=1.25, kind="tall", col="#4f8a52")
    for gx, gy, rz in ((-3.5, 12.6, 12), (-2.9, 13.7, -8), (-3.9, 13.9, 20)):
        with b.at(gx, gy, 0, rz=rz):
            b.stone(0.5, 0.15, 0.85, mat="ashlar", col="grey", lod=1, jitter=0.2)
