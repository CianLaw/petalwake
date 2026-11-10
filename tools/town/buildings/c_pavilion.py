# The Belvedere: an eight-sided summer-house in the old physic garden, where the hill looks down on both coasts at once. Somebody always leaves a cushion there.
# Massing: eight slender posts on three stone steps, a low lattice balustrade between them (open to the front and to the view behind), a bell-cast ogee roof rising to a ball and spike; roses up the front posts, clipped box at the corners of the plot.
# Materials: ashlar steps and floor, ivory-painted posts and lattice, a verdigris copper roof with brass finial. Accent: ivory.
import math

from kit import *
import parts as P
import parts_c as PC

META = {"name": "The Belvedere", "kind": "pavilion", "lot": (5.0, 5.0)}

CY = 2.5
RP, ZF, ZP = 1.72, 0.51, 3.0                      # post circle, floor, wall-plate
SEC = [(2.22, -0.2), (1.92, 0.22), (1.5, 0.5), (1.08, 0.86), (0.8, 1.42), (0.56, 2.0), (0.22, 2.4), (0.0, 2.85)]


def build(b):
    with b.at(0, CY, 0, rz=22.5):
        base(b)
        frame(b)
        roof(b)
    garden(b)


def base(b):
    for i, r in enumerate((2.3, 2.1, 1.9)):
        b.revolve([(r, -3.0 if i == 0 else 0.17 * i), (r, 0.17 * (i + 1))], "ashlar", col="stone" if i < 2 else "sand", seg=8, smooth=False)
        b.disc(r, "flagstone" if i == 2 else "ashlar", col="sand" if i == 2 else "stone", seg=8, z=0.17 * (i + 1), r_in=0.0 if i == 2 else r - 0.3)
    PC.foot_disc(b, 2.3, ZF)


def frame(b):
    """Eight posts, a wall-plate, curved braces, and the lattice between (sides 0 and 4 are left open)."""
    P_ = lambda k, r=RP, z=0.0: PC.polar(r, 45 * k, z)
    with b.detail(0):
        for k in range(8):
            x, y, _ = P_(k)
            b.beam((x, y, ZF), (x, y, ZP), w=0.15, mat="planks", col="ivory", lod=0)
            b.beam(P_(k, RP, ZP + 0.07), P_(k + 1, RP, ZP + 0.07), w=0.16, h=0.16, mat="planks", col="ivory", lod=0)
    with b.detail(1):
        for k in range(8):
            a, c = P_(k), P_(k + 1)
            for (p, q) in ((a, c), (c, a)):                 # a brace from each post up to the plate
                m = (p[0] + (q[0] - p[0]) * 0.3, p[1] + (q[1] - p[1]) * 0.3)
                b.beam((p[0], p[1], ZP - 0.62), (m[0], m[1], ZP), w=0.07, mat="planks", col="ivory", caps=False)
            b.box(0.26, 0.26, 0.12, "planks", col="ivory", x=a[0], y=a[1], z=ZF)
    for k in range(8):
        if k in (7, 3):                                      # front and back bays stay open (frame is turned 22.5)
            continue
        a, c = P_(k, RP, ZF), P_(k + 1, RP, ZF)
        P.railing(b, [a, c], h=0.82, style="cross", col="ivory", mat="planks", post=0.07, posts_at=0.75)
    b.disc(RP + 0.05, "planks", col="ivory", seg=8, z=ZP + 0.14, down=True)        # the boarded ceiling
    # the seat round the back, and the cushion
    with b.detail(1):
        for k in (1, 2, 4, 5):
            a, c = P_(k, RP - 0.32), P_(k + 1, RP - 0.32)
            b.beam((a[0], a[1], ZF + 0.42), (c[0], c[1], ZF + 0.42), w=0.42, h=0.06, mat="planks", col="greyoak")
    with b.detail(2):
        for k in (1, 2, 3, 4, 5, 6):
            x, y, _ = P_(k, RP - 0.3)
            b.beam((x, y, ZF), (x, y, ZF + 0.4), w=0.07, mat="planks", col="greyoak", caps=False)
        x, y, _ = PC.polar(RP - 0.5, 112)
        b.blob(0.2, 0.2, 0.08, mat="cloth", col="#d9879a", x=x, y=y, z=ZF + 0.52, seg=6, rings=2, rough=0.1)
        x, y, _ = PC.polar(RP - 0.5, 196)
        b.blob(0.18, 0.2, 0.08, mat="cloth", col="#7fa8d6", x=x, y=y, z=ZF + 0.52, seg=6, rings=2, rough=0.1)


def roof(b):
    b.cone_roof(RP, SEC[-1][1], mat="metal", col="copper", z=ZP + 0.17, seg=8, smooth=False, section=SEC, course=0.36, lip=0.035, finial=False, soffit="planks", soffit_col="ivory")
    with b.at(z=ZP + 0.17):
        with b.detail(1):
            for k in range(8):
                with b.at(rz=45 * k):
                    for (ra, za), (rb, zb) in zip(SEC, SEC[1:]):
                        up = (0, -1, 0) if abs(zb - za) > abs(rb - ra) else (0, 0, 1)
                        b.beam((0, -ra, za + 0.03), (0, -max(rb, 0.03), zb + 0.03), w=0.09, h=0.07, mat="metal", col=shade("copper", 0.72), caps=False, up=up)
            zt = SEC[-1][1]
            b.revolve([(0.1, zt - 0.2), (0.07, zt + 0.1), (0.2, zt + 0.3), (0.2, zt + 0.46), (0.06, zt + 0.66), (0.035, zt + 1.3), (0.0, zt + 1.42)], "metal", col="brass", seg=8)
    PC.doves(b, [(PC.polar(1.6, 100)[0], PC.polar(1.6, 100)[1], ZP + 0.6)])


def garden(b):
    for (x, y) in ((-1.98, 0.5), (1.98, 0.5), (-1.98, 4.5), (1.98, 4.5)):
        with b.detail(1):
            b.blob(0.36, 0.36, 0.4, mat="ivy", col="#6fa552", x=x, y=y, z=0.36, seg=7, rings=4, rough=0.08, wind=0.1)
    for deg in (-22.5, 22.5):
        x, y, _ = PC.polar(RP + 0.02, deg)
        PC.climber(b, (x, CY + y, ZF + 0.1), (x, CY + y, ZP - 0.1), n=7, r=0.2, bloom=["#e8497a", "#f2a0bd", "#ffffff"])
    PC.flowers(b, -1.25, 0.55, 0, w=1.0, d=0.4, n=5); PC.flowers(b, 1.25, 0.55, 0, w=1.0, d=0.4, n=5)
    PC.flowers(b, -2.12, 2.5, 0, w=0.3, d=1.6, n=5); PC.flowers(b, 2.12, 2.5, 0, w=0.3, d=1.6, n=5)
    PC.flowers(b, 0.0, 4.6, 0, w=2.6, d=0.4, n=7)
    for sx in (-1, 1):                                  # urns either side of the steps, stepping stones to the street
        PC.urn(b, sx * 0.95, 0.3, 0, h=0.95, cols=["#f2a0bd", "#ffffff", "#b08ae6"])
    with b.detail(2):
        for i, (x, y) in enumerate(((0.05, 0.02), (-0.12, -0.42), (0.1, -0.86))):
            with b.at(x, y, 0, rz=20 * i - 15):
                b.stone(0.62, 0.42, 0.05, mat="flagstone", col="sand", jitter=0.2)
