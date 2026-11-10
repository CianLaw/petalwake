# Penny Gate: the eight-sided toll house on the meadow road; old Mistress Fenn can see both ways along it from her windows and misses nothing.
# Massing: a two-storey octagon under a broad eight-sided slate roof with one chimney at its point, a little gabled porch on posts at the
#          front, a white bar gate and a strip of fence to one side.
# Materials: cream stucco over a rubble base with an ashlar band, blue-grey slate, a brick chimney; accent pink.
from kit import *
import parts as P
import parts_c as PC
import parts_f as F

META = {"name": "Penny Gate", "kind": "house", "lot": (6.0, 6.0)}

AX, AY = -0.28, 3.25
R, H, G = 2.4, 5.3, 2.75


def build(b):
    side = 2 * R * math.sin(math.pi / 8)
    ap = R * math.cos(math.pi / 8)
    m = side / 2
    faces = PC.poly_tower(b, 8, R, H, mat="plaster", col="cream", x=AX, y=AY, depth=0.24)
    PC.poly_plinth(b, 8, R, h=0.7, out=0.1, doors=[(0, m, 1.1), (4, m, 1.0)], x=AX, y=AY)
    P.door(faces[0], m, w=0.95, h=2.0, col="pink", frame="stone", z=0.22, steps=1, lamp=True)
    P.door(faces[4], m, w=0.85, h=1.95, col="pink", frame="stone", z=0.22, steps=1)
    for k in (1, 7, 3, 5):
        P.window(faces[k], m, 1.05, w=0.8, h=1.25, shutters="pink" if k in (1, 7) else None, box=k == 1)
    for k in (0, 1, 7, 2, 6, 4):
        P.window(faces[k], m, G + 0.85, w=0.75, h=1.15, shutters="pink" if k in (1, 7) else None)
    with b.at(AX, AY, 0.0, rz=22.5):
        P.ring_band(b, R, G, h=0.16, out=0.06, seg=8)
        P.ring_band(b, R, H - 0.2, h=0.2, out=0.1, seg=8)
        b.cone_roof(R, 2.5, mat="slate", z=H, seg=8, smooth=False, eave=0.42, flare=0.42, course=0.42, finial=False)
    P.chimney(b, AX, AY, H + 1.5, 1.9, w=0.72, d=0.72, mat="brick", pots=2)
    P.exposed(faces[2], "base", n=6)
    P.exposed(faces[5], "base", n=6)
    P.ivy(faces[6], m, 0.7, w=1.4, h=3.0, n=8)

    # ---- the porch: two posts, a little slate gable, the tariff board beside the door
    yf = AY - ap
    b.gable_roof(1.9, 0.75, 40, mat="slate", x=AX, y=yf - 0.375, z=2.42, ridge="y", eave=0.14, verge=0.1, course=0.3, thick=0.08, lod=1)
    with b.detail(1):
        for sx in (-1, 1):
            b.beam((AX + sx * 0.85, yf - 0.62, 0.0), (AX + sx * 0.85, yf - 0.62, 2.42), w=0.13, mat="planks", col="ivory")
            b.beam((AX + sx * 0.85, yf - 0.7, 2.36), (AX + sx * 0.85, yf, 2.36), w=0.1, h=0.12, mat="planks", col="ivory", up=(0, 0, 1))
        b.beam((AX - 0.92, yf - 0.62, 2.36), (AX + 0.92, yf - 0.62, 2.36), w=0.1, h=0.12, mat="planks", col="ivory", up=(0, 0, 1))
        b.box(1.9, 0.75, 0.2, "flagstone", col="sand", x=AX, y=yf - 0.36, z=0.0)

    with b.at(2.45, 0.62, 0.0, rz=-12):                     # the tariff board on its post (lines, no letters)
        with b.detail(2):
            b.beam((0, 0.04, -0.4), (0, 0.04, 1.75), w=0.09, mat="planks", col="ivory")
            b.box(0.56, 0.05, 0.8, "planks", col="ivory", y=-0.02, z=0.95, bottom=True)
            for i in range(5):
                b.box(0.4 - 0.06 * (i % 2), 0.012, 0.035, "paint", col="black", y=-0.052, z=1.06 + 0.13 * i)
            b.beam((-0.31, -0.02, 1.79), (0.31, -0.02, 1.79), w=0.07, h=0.06, mat="planks", col="pink", caps=True)

    # ---- the little bar gate and its fence, on the right
    gx0, gy = AX + ap + 0.12, 1.25
    with b.detail(1):
        b.box(0.2, 0.2, 1.75, "planks", col="ivory", x=gx0, y=gy, z=-0.5)
        b.box(0.16, 0.16, 1.5, "planks", col="ivory", x=2.82, y=gy, z=-0.5)
    with b.at(gx0, gy, 0.0, rz=-8):
        F.gate(b, w=2.82 - gx0 - 0.06, h=1.05, col="ivory", bars=5, kind="field")
    F.picket(b, [(2.82, gy), (2.82, 5.6)], h=0.85, col="ivory")
    F.picket(b, [(-2.86, 5.8), (-2.86, 0.9)], h=0.85, col="ivory")

    # ---- a bench in the sun, flowers under the windows
    P.bench(b, AX + 1.82, AY - 1.82, 0.0, w=1.1, rz=45)
    for (x, y, c_) in ((-2.6, 1.2, "#e8497a"), (-2.3, 0.85, "#f2a0bd"), (2.3, 2.0, "#b08ae6"), (2.4, 4.9, "#e8497a")):
        F.spire_flower(b, x, y, 0.0, h=b.r(1.0, 1.4), col=c_)
    for (x, y) in ((-2.5, 1.6), (-2.55, 5.3), (2.35, 5.3), (2.3, 2.5), (-1.9, 0.6)):
        F.flowers(b, x, y, 0.0, n=5, spread=0.28)
