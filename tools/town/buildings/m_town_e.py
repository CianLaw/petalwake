# The Wheelwright's: carts go in through the big arched door and come out with new wheels; the master lives over the
# shop, his journeymen above him, and the little glazed lantern on the roof lights the stair all the way down.
# Massing: four storeys, flat-fronted, a cart arch and a house door below, an oriel on a carved corbel at the second
# floor, a hipped roof with a glazed lantern on its ridge and one very tall chimney.
# Materials: rubble ground floor with a dressed arch, peach lime plaster above with stone bands, tiles; mint woodwork.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Wheelwright's", "kind": "house", "lot": (6.4, 9.0), "terrace": True}

A = "mint"
W, D = 5.5, 7.2
ZS = [0.0, 3.4, 6.2, 9.0, 11.4]


def cart_wheel(b, x, y, r=0.55, lean=14.0, turn=0.0):
    """A cart wheel leaning against a wall that lies just behind (x, y)."""
    with b.at(x, y, r * math.cos(rad(lean)), rx=90 - lean):
        with b.at(rz=turn):
            with b.detail(2):
                b.revolve([(r - 0.07, -0.035), (r, -0.035), (r, 0.035), (r - 0.07, 0.035), (r - 0.07, -0.035)], "planks", col="greyoak", seg=12)
                b.revolve([(0.0, -0.07), (0.1, -0.07), (0.1, 0.07), (0.0, 0.07)], "planks", col="darkoak", seg=6)
                for k in range(8):
                    a = math.pi * k / 4
                    b.beam((0.08 * math.sin(a), -0.08 * math.cos(a), 0), ((r - 0.05) * math.sin(a), -(r - 0.05) * math.cos(a), 0), w=0.04, mat="planks", col="greyoak", caps=False)


def build(b):
    g = b.body(W, D, ZS[1], mat="masonry", col="warm")
    P.plinth(g, h=0.5)
    P.door(g.front, 1.7, w=2.3, h=2.9, z=0.04, arch=0.85, col=A, frame=None, double=True, knob=False)
    Q.surround(g.front, 1.7, 0.04, 2.3, 2.9, arch=0.85, t=0.24, proud=0.07)
    P.door(g.front, 4.5, w=0.9, h=2.1, z=0.3, col=A, frame="stone", lamp=True)
    Q.steps(g.front, 4.5, w=1.3, n=2, z=0.3, rise=0.15)
    Q.sign(g.front, 3.35, 3.2, emblem="wheel", shape="round", col="brown", out=0.9)
    P.stones(g.front, n=6, z0=0.5, u0=3.0)
    cart_wheel(b, -W / 2 + 3.35, -0.16, r=0.6)
    cart_wheel(b, W / 2 - 0.35, -0.5, r=0.45, lean=8, turn=20)
    P.barrel(b, -W / 2 + 0.2, -0.4, 0, r=0.24, h=0.6)
    up = b.body(W, D, ZS[4] - ZS[1], mat="plaster", col="peach", z=ZS[1])
    for k in (1, 2, 3):
        P.band(up, ZS[k] - ZS[1], h=0.18, out=0.06)
    P.band(up, ZS[4] - ZS[1] - 0.22, h=0.22, out=0.09)
    Q.quoins(up, corners="fr", size=(0.48, 0.27, 0.42))
    # --- first floor: three shuttered windows
    for i, u in enumerate((0.95, W / 2, W - 0.95)):
        P.window(up.front, u, 0.95, w=0.85, h=1.4, shutters=A, bars=(1, 2), box=(i == 0))
    # --- second floor: the oriel between two small windows
    z2 = ZS[2] - ZS[1]
    Q.bay(up.front, W / 2, z2 + 0.6, w=2.0, h=1.4, out=0.5, cant=0.32, apron=0.4, col="ivory", apron_col=A, panes=(3, 2), side_panes=(1, 2), base="corbel", base_mat="ashlar",
          base_col="stone", drop=0.8, roof="copper", roof_h=0.5)
    for u in (0.8, W - 0.8):
        P.window(up.front, u, z2 + 0.95, w=0.65, h=1.3, bars=(1, 2))
    # --- third floor: low windows under the eaves
    z3 = ZS[3] - ZS[1]
    for i, u in enumerate((0.95, W / 2, W - 0.95)):
        P.window(up.front, u, z3 + 0.75, w=0.8, h=1.0, bars=(1, 1), shutters=A if i == 1 else None, box=(i == 2))
    for z in (0.95, z2 + 0.95, z3 + 0.75):
        for u in (1.3, W - 1.3):
            P.window(up.back, u, z, w=0.9, h=1.3 if z < z3 else 1.0, bars=(1, 2), shutters=A if z < z3 else None)
    for wl, u in ((up.right, 2.2), (up.left, 5.0)):
        P.window(wl, u, z2 + 0.95, w=0.7, h=1.2, bars=(1, 1))
        P.window(wl, u, z3 + 0.75, w=0.7, h=1.0, bars=(1, 1))
    # --- the hipped roof, the glazed lantern, the tall stack
    rise = up.hip(pitch=42, mat="tiles", eave=0.3)
    zl = ZS[4] + rise - 0.35
    b.box(0.9, 0.9, 0.95, "glass", x=0, y=D / 2, z=zl, top=False)
    with b.detail(1):
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.beam((sx * 0.45, D / 2 + sy * 0.45, zl), (sx * 0.45, D / 2 + sy * 0.45, zl + 0.95), w=0.08, mat="planks", col="ivory", caps=False)
        b.box(1.0, 1.0, 0.08, "planks", col="ivory", x=0, y=D / 2, z=zl + 0.95, bottom=True)
    lr = b.loop_roof(1.0, 1.0, pitch=48, mat="tiles", x=0, y=D / 2, z=zl + 1.03, eave=0.16, course=0.25, thick=0.07)
    Q.ball(b, 0, D / 2, zl + 1.03 + lr - 0.08, r=0.1, mat="metal", col="copper")
    Q.stack(b, W / 2 - 0.45, D - 2.0, ZS[4] - 0.4, 5.4, w=0.7, d=0.7, mat="brick", col=None, pots=2)
    # --- behind
    P.door(g.back, 1.3, w=0.9, h=2.0, z=0.15, col=A, frame="timber", steps=1)
    P.window(g.back, 3.7, 1.3, w=1.2, h=1.2, bars=(2, 1))
    P.crate(b, -1.2, D + 0.45, 0, s=0.55)
    P.laundry(b, (-2.6, D + 0.04, 5.6), (2.6, D + 0.04, 5.2), n=5, sag=0.4)
