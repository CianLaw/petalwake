# The Merchants' Guildhall: where the wool, salt and herring guilds keep their charters and settle their quarrels;
# the crow-stepped gable was the tallest thing on the square until the town hall got its tower.
# Massing: a tall three-storey block with a crow-stepped gable to the square over a carved doorway and three tiers of
# mullioned windows, a steep tiled roof behind, a slim round stair turret at one corner and a great side chimney.
# Materials: pale dressed stone front, warm rubble flanks, ashlar copings, tiles, slate on the turret; green doors.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Merchants' Guildhall", "kind": "guildhall", "lot": (11.0, 10.0)}

A = "green"
BX, BW, BD = 0.7, 8.6, 9.3        # the main block: centre line, width, depth
Z1, Z2, ZE = 4.2, 8.2, 10.8       # first floor, second floor, eaves
PITCH = 55.0


def rosette(s, pos, z, r=0.42):
    """A carved boss over the door: a ring of petals round a knob."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            with b.at(rx=90):
                with b.detail(1):
                    b.revolve([(r + 0.12, 0.0), (r + 0.12, 0.07), (r, 0.07), (r - 0.04, 0.03), (0.0, 0.03)], "ashlar", col="stone", seg=12)
                with b.detail(2):
                    for k in range(8):
                        with b.at(rz=45 * k):
                            b.stone(0.15, 0.24, 0.07, mat="ashlar", col="sand", y=-r * 0.58, z=0.03, jitter=0.04)
                    b.revolve([(0.11, 0.03), (0.08, 0.1), (0.0, 0.12)], "ashlar", col="stone", seg=6)

    s.add(deco)


def anchor_iron(s, pos, z, k=0.26):
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            with b.detail(2):
                b.beam((-k, -0.02, -k), (k, -0.02, k), w=0.05, h=0.025, mat="metal", col="iron", up=(0, 1, 0), caps=False)
                b.beam((-k, -0.02, k), (k, -0.02, -k), w=0.05, h=0.025, mat="metal", col="iron", up=(0, 1, 0), caps=False)

    s.add(deco)


def build(b):
    x0 = BX - BW / 2
    bd = b.body(BW, BD, ZE, mat="masonry", col="warm", x=BX, y=BD / 2)
    f = bd.front
    f.mat, f.col = "ashlar", C("sand")
    P.plinth(bd, h=0.6, out=0.1, mat="ashlar", col="grey")
    # --- the carved doorway
    P.door(f, BW / 2, w=1.8, h=3.0, z=0.51, arch=0.9, col=A, frame=None, double=True)
    Q.surround(f, BW / 2, 0.51, 1.8, 3.0, arch=0.9, t=0.26, proud=0.09)
    Q.steps(f, BW / 2, w=2.7, n=3, z=0.51)
    rosette(f, BW / 2, 3.86)
    for sgn in (-1, 1):
        P.lantern(f, BW / 2 + sgn * 1.55, 2.5)

    def pilasters():
        with b.detail(1):
            for sgn in (-1, 1):
                with f.on(BW / 2 + sgn * 1.32, 0.6):
                    b.box(0.3, 0.14, 2.6, "ashlar", col="stone", y=-0.06, top=False)
                    b.box(0.42, 0.2, 0.16, "ashlar", col="stone", y=-0.08, z=2.6, bottom=True)

    f.add(pilasters)
    # --- three tiers of mullioned windows, string courses, iron anchors
    cols_u = (1.55, BW / 2, BW - 1.55)
    for u in (cols_u[0], cols_u[2]):
        Q.mullioned(f, u, 1.35, w=1.5, h=1.7, lights=3, transoms=1)
    for u in cols_u:
        Q.mullioned(f, u, Z1 + 0.6, w=1.7, h=3.0, lights=3, transoms=2)
        Q.mullioned(f, u, Z2 + 0.55, w=1.5, h=1.5, lights=3, transoms=0)
    for u in ((cols_u[0] + cols_u[1]) / 2, (cols_u[1] + cols_u[2]) / 2):
        anchor_iron(f, u, Z2 + 0.2)
        anchor_iron(f, u, ZE - 0.45)
    with b.detail(1):
        for z in (Z1, Z2, ZE - 0.1):
            b.box(BW + 0.16, 0.14, 0.2, "ashlar", col="stone", x=BX, y=-0.03, z=z - 0.1, bottom=True)
    Q.sign(f, BW - 0.45, 3.9, emblem="crown", shape="shield", col="mustard", board=A, out=0.8)
    with b.at(BX - 1.45, -0.05, Z1 + 0.25):
        P.flag(b, 0, 0, 0, pole=1.6, w=1.2, h=0.85, col="stripe_green", kind="banner", lean=36)
    # --- flanks and back
    for z in (1.4, Z1 + 0.9, Z2 + 0.7):
        for u in (3.4, 7.2):
            P.window(bd.right, u, z, w=0.9, h=1.5 if z > 2 and z < Z2 else 1.3, bars=(1, 2))
        for u in (2.2, 5.6):
            P.window(bd.left, u, z, w=0.9, h=1.5 if z > 2 and z < Z2 else 1.3, bars=(1, 2))
        for u in (2.0, 6.4):
            if z > 2:
                P.window(bd.back, u, z, w=1.0, h=1.5 if z < Z2 else 1.3, bars=(1, 2), shutters=A)
    P.door(bd.back, 6.4, w=1.0, h=2.1, z=0.17, col=A, frame="stone", steps=1)
    P.window(bd.back, 2.0, 1.4, w=1.0, h=1.3, bars=(1, 2), shutters=A)
    P.stones(bd.right, n=16, z0=0.7)
    P.stones(bd.left, n=12, z0=0.7)
    # --- the roof behind the gable (it starts just inside the gable wall)
    rise = (BW / 2) * math.tan(rad(PITCH))
    bd.back.gable = rise - 0.03
    b.gable_roof(BW, BD - 0.2 + 0.3, pitch=PITCH, mat="tiles", x=BX, y=0.2 + (BD + 0.1) / 2, z=ZE, ridge="y", eave=0.3, verge=0.0, sag=0.12)
    Q.gable_holes(bd.back)
    P.window(bd.back, BW / 2, ZE + 1.0, w=0.8, h=1.2, arch=0.3, bars=(1, 2))
    for y in (3.2, 6.4):
        P.dormer(b, BX + BW / 2 - 0.95, y, ZE + 0.95 * math.tan(rad(PITCH)), w=1.05, h=1.0, depth=1.2, face=90, col="sand", roof="tiles")
    # --- the crow-stepped gable: five tiers of free-standing wall, each coped, with windows in the lower ones
    tiers = [(BW, 1.43), (BW - 2.0, 1.43), (BW - 4.0, 1.43), (BW - 6.0, 1.43), (1.0, 1.25)]
    z = ZE
    for k, (w, h) in enumerate(tiers):
        with b.at(BX - w / 2, 0.0, z):
            wl = b.wall(w, h, mat="ashlar", col="sand", back="masonry", backcol="warm", thick=0.45)
            if k == 0:
                for u in (w / 2 - 1.5, w / 2 + 1.5):
                    Q.mullioned(wl, u, 0.2, w=1.1, h=0.95, lights=2, transoms=0, hood=False)
            elif k == 1:
                Q.mullioned(wl, w / 2, 0.2, w=1.3, h=1.0, lights=2, transoms=0, hood=False)
            elif k == 2:
                Q.round_window(wl, w / 2, 0.72, r=0.42, spokes=4, depth=0.2)
            with b.detail(1):
                nw = tiers[k + 1][0] if k + 1 < len(tiers) else 0.0
                for sgn in (-1, 1):
                    cw = (w - nw) / 2
                    b.box(cw + 0.1, 0.57, 0.1, "ashlar", col="stone", x=w / 2 + sgn * (w / 2 - cw / 2), y=0.225, z=h, bottom=True)
            if k in (0, 2):
                for sgn in (-1, 1):
                    Q.ball(b, w / 2 + sgn * (w / 2 - 0.3), 0.225, h + 0.1, r=0.14)
        z += h
    Q.ball(b, BX, 0.225, z + 0.1, r=0.2)
    Q.weathercock(b, BX, 0.225, z + 0.45, h=1.4, shape="pennon", size=0.9)
    # --- the great chimney on the right flank
    Q.stack(b, BX + BW / 2 + 0.02, 5.0, 0.0, 15.6, w=0.72, d=1.15, base=(0.72, 1.9, 9.0), pots=3)
    # --- the stair turret at the left corner
    tx, ty = x0 - 0.4, 1.3
    t = b.round(1.15, 12.8, r1=1.1, mat="masonry", col="warm", seg=12, x=tx, y=ty)
    P.round_base(b, 1.15, h=0.9, out=0.15, seg=12, ring=t)
    P.door(t, 353, w=0.75, h=1.9, z=0.2, arch=0.37, col=A, steps=1)
    for a, zz in ((300, 3.4), (255, 6.0), (330, 8.6), (275, 10.9), (200, 10.9)):
        t.opening(a, zz, 0.42, 1.0, arch=0.21, depth=0.22)
    P.ring_band(b, 1.1, 12.5, h=0.3, out=0.1, seg=12, x=tx, y=ty)
    b.cone_roof(1.1, 3.5, mat="slate", x=tx, y=ty, z=12.8, seg=12, eave=0.3, flare=0.4, course=0.55)
    P.ivy(t, 250, 0.4, w=1.3, h=3.6, n=6)
    P.bench(b, BX + 2.9, -0.45, 0, w=1.6)
    P.planter(b, BX - 2.1, -0.35, 0, w=0.6, bush=True)
