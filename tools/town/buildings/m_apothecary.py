# The Green Lantern apothecary: three generations of herb-wives have dried, steeped and bottled here; a green lamp
# burns in the window all night so that anyone in need can find the door.
# Massing: tall and upright, three storeys each jettied a little over the last, a steep slate roof with its gable to
# the street, an oriel on a carved corbel at the first floor and a lean-to stillroom behind.
# Materials: a rubble ground floor, lilac lime plaster above with oak framing in the top storey, slate; teal woodwork.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Green Lantern apothecary", "kind": "shop", "lot": (7.5, 9.0)}

A = "teal"
W, D = 6.2, 7.0
Z1, Z2, ZE = 3.2, 6.1, 8.8
HERB = ["#8fc46a", "#6fa85a", "#a48fc9", "#9ab86a"]


def herbs(b, x0, x1, y, z, n=7):
    """Bunches of herbs hung up to dry on a line."""
    with b.detail(2):
        b.beam((x0, y, z), (x1, y, z), w=0.015, mat="cloth", col="#8a7a66", caps=False)
        for i in range(n):
            x = lerp(x0, x1, (i + 0.5) / n)
            b.blob(0.07, 0.07, 0.17, mat="ivy", col=b.pick(HERB), x=x, y=y, z=z - 0.2, seg=5, rings=2, wind=0.3, rough=0.25)


def build(b):
    g = b.body(W, D, Z1, mat="masonry", col="warm")
    P.plinth(g, h=0.5)
    Q.shopfront(g.front, 2.25, 0.0, w=2.6, h=1.7, riser=0.65, col=A, lights=3, goods="bottles", panes=2)
    P.door(g.front, 5.15, w=1.0, h=2.15, z=0.15, col=A, frame="stone", steps=1)
    Q.sign(g.front, 0.3, 3.02, emblem="mortar", shape="shield", col=A, out=0.9)
    Q.joists(g.front, Z1, out=0.3)
    with b.detail(2):                               # the green lantern by the door
        with g.front.on(4.3, 2.35):
            b.beam((0, 0.0, 0.2), (0, -0.3, 0.2), w=0.025, mat="metal", col="iron", caps=False)
            b.box(0.17, 0.17, 0.24, "glow", col="#9fe8a8", x=0, y=-0.3, z=-0.1, bottom=True)
            b.box(0.21, 0.21, 0.03, "metal", col="iron", x=0, y=-0.3, z=0.14)
    b.lamp(-W / 2 + 4.3, -0.3, 2.35)
    P.ivy(g.front, 5.95, 0.2, w=0.9, h=2.6, n=5)
    P.window(g.right, 4.6, 1.3, w=0.8, h=1.2, bars=(1, 1))
    P.window(g.left, 2.4, 1.3, w=0.8, h=1.2, bars=(1, 1))
    # --- first floor: the oriel between two herb-box windows
    f1 = b.body(W, D + 0.3, Z2 - Z1, mat="plaster", col="lilac", z=Z1, y=(D - 0.3) / 2, floor="planks")
    Q.bay(f1.front, W / 2, 0.55, w=2.1, h=1.45, out=0.5, cant=0.32, apron=0.4, col="ivory", apron_col=A, base="corbel", base_col=A, drop=0.75,
          roof="copper", roof_h=0.5, panes=(3, 2), side_panes=(1, 2))
    for u in (0.85, W - 0.85):
        P.window(f1.front, u, 0.95, w=0.7, h=1.25, box=True, bars=(1, 2))
    herbs(b, -W / 2 + 0.3, -1.25, -0.42, Z2 - 0.12, n=6)
    herbs(b, 1.25, W / 2 - 0.3, -0.42, Z2 - 0.12, n=6)
    Q.joists(f1.front, Z2 - Z1, out=0.25)
    P.window(f1.right, 2.6, 0.95, w=0.8, h=1.25, bars=(1, 2))
    P.window(f1.left, 4.6, 0.95, w=0.8, h=1.25, bars=(1, 2))
    for u in (1.6, 4.6):
        P.window(f1.back, u, 0.95, w=0.9, h=1.25, shutters=A, bars=(1, 2))
    # --- top storey: framed, shuttered; then the gable
    f2 = b.body(W, D + 0.55, ZE - Z2, mat="plaster", col="lilac", z=Z2, y=(D - 0.55) / 2, floor="planks")
    P.timber_frame(f2.front, posts=[0.0, 1.0, 2.4, 3.8, 5.2, W], rails=[0.0, 0.85, ZE - Z2], braces=[(0, 0.85, 1.0, 2.7), (W, 0.85, 5.2, 2.7), (2.4, 2.7, 3.8, 0.85)])
    for u in (1.7, 4.5):
        P.window(f2.front, u, 0.9, w=0.9, h=1.25, shutters=A, box=True, lintel=None, bars=(1, 2))
    P.window(f2.right, 4.4, 0.9, w=0.8, h=1.2, bars=(1, 2))
    P.window(f2.left, 3.0, 0.9, w=0.8, h=1.2, bars=(1, 2))
    P.window(f2.back, W / 2, 0.9, w=1.0, h=1.25, shutters=A, bars=(1, 2))
    f2.gable(ridge="y", pitch=54, mat="slate", sag=0.1, eave=0.3, verge=0.25)
    Q.gable_holes(f2.front)
    Q.gable_holes(f2.back)
    P.window(f2.front, W / 2, ZE - Z2 + 0.6, w=0.7, h=1.2, arch=0.35, bars=(1, 2))
    P.window(f2.back, W / 2, ZE - Z2 + 0.6, w=0.6, h=0.9, bars=(1, 1))
    P.chimney(b, -2.2, 4.8, ZE + 0.6, 4.0, w=0.55, d=0.5, mat="brick", pots=2)
    # --- the stillroom: a lean-to at the back with its own little flue
    st = b.body(3.4, 1.5, 2.3, mat="masonry", col="warm", x=-W / 2 + 1.7, y=D + 0.75)
    Q.plinth(st, h=0.3, walls="rbl")
    P.door(st.right, 0.75, w=0.8, h=1.85, z=0.06, col=A, frame="timber")
    P.window(st.back, 1.7, 1.0, w=1.2, h=0.9, bars=(2, 1), box=True)
    rs = Q.lean_to(b, 3.4, 1.5, pitch=28, x=-W / 2 + 1.7, y=D, z=2.3, face=180, mat="slate", eave=0.15, verge=0.12, course=0.35)
    b.tri((-W / 2, D + 1.5, 2.3), (-W / 2, D, 2.3), (-W / 2, D, 2.3 + rs), "masonry", col="warm")
    b.tri((-W / 2 + 3.4, D, 2.3), (-W / 2 + 3.4, D + 1.5, 2.3), (-W / 2 + 3.4, D, 2.3 + rs), "masonry", col="warm")
    P.chimney(b, -W / 2 + 0.5, D + 1.1, 2.2, 2.0, w=0.4, d=0.4, mat="brick", pots=1)
    P.door(g.back, 1.3, w=0.9, h=2.0, z=0.15, col=A, frame="timber", steps=1)
    # --- the street: herbs in troughs and pots
    P.planter(b, -0.85, -0.3, 0, w=1.1, flowers=["#b08ae6", "#f4f1e4", "#a48fc9"])
    P.planter(b, 2.95, -0.3, 0, w=0.45, d=0.4, h=0.38, bush=True)
    P.barrel(b, -2.85, -0.45, 0, r=0.26, h=0.65)
