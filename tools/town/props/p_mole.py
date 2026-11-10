# mole / breakwater, 10 m: broad rubble mound with a paved walk on top, a sea wall along its outer (-y) edge, armour stones
import math
from kit import *
import parts as P
import parts_p as PP

L, TW = 10.0, 8.0
META = {"name": "Mole 10 m", "kind": "prop", "group": "harbour", "clear": 10.5, "length": L, "axis": "x", "wobble": 0.0, "top_width": TW,
        "deck": 0.0, "bottom": -PP.DEEP, "notes": "seat on the mole's crest; the sea wall is on the -y side, the harbour on +y; rubble slopes go 7.5 m down both sides"}

SLOPE = 0.72        # metres out per metre down


def build(b):
    hw, Z = TW / 2, PP.PAVE
    x0, x1 = -L / 2, L / 2
    rng = b.rng
    with b.detail(0):
        PP.quay_deck(b, x0, x1, y0=-hw, y1=hw, mat="masonry", col="grey", back=0, cell=2.5)
        b.quad((x0, -2.3, Z + 0.03), (x1, -2.3, Z + 0.03), (x1, 2.7, Z + 0.03), (x0, 2.7, Z + 0.03), "flagstone", col="sand")
        for sgn in (-1, 1):
            for (za, zb, m, k) in PP.QUAY_BANDS:
                ya, yb = hw + (Z - za) * SLOPE, hw + (Z - zb) * SLOPE
                c = shade(mix("grey", "#9aa888", m), k)
                for i in range(4):
                    xa, xb = lerp(x0, x1, i / 4), lerp(x0, x1, (i + 1) / 4)
                    q = [(xa, -ya, za), (xb, -ya, za), (xb, -yb, zb), (xa, -yb, zb)]
                    if sgn > 0:
                        q = [(p[0], -p[1], p[2]) for p in reversed(q)]
                    b.face(q, "masonry", col=c)
        for sx in (-1, 1):          # flat ends, hidden where segments meet
            x = sx * L / 2
            yb_ = hw + (Z + PP.DEEP) * SLOPE
            q = [(x, -yb_, -PP.DEEP), (x, yb_, -PP.DEEP), (x, hw, Z), (x, -hw, Z)]
            b.face(q if sx > 0 else list(reversed(q)), "masonry", col=shade("grey", 0.7))
        with b.at(0, -hw + 0.75, Z):
            PP.wall_run(b, x0, x1, 1.1, t=0.62, col="grey", skirt=0.25)
    with b.detail(1):
        with b.at(0, -hw + 0.75, Z):
            PP.cap_slabs(b, x0, x1, lambda _x: 1.1, 0.62, over=0.06, thick=0.13, col="stone", wmin=0.7, wmax=1.1)
        for xa, xb in PP.split(b, x0, x1, 0.9, 1.4):          # kerb along the harbour edge
            b.stone(xb - xa - 0.02, 0.6, 0.3, mat="ashlar", col="stone", x=(xa + xb) / 2, y=hw - 0.32, z=Z - 0.22, jitter=0.06, ch=0.18)
        PP.bollard_stone(b, -2.4, hw - 1.1, Z, h=0.7, r=0.19)
        PP.bollard_stone(b, 2.6, hw - 1.1, Z, h=0.7, r=0.19)
    for lod, n, s0, s1 in ((1, 9, 0.2, 2.4), (2, 14, 0.6, 5.2)):          # armour stones tumbled down both slopes
        with b.detail(lod):
            for sgn in (-1, 1):
                for i in range(n):
                    w = rng.uniform(0.8, 1.6)
                    d, h = w * rng.uniform(0.6, 0.9), w * rng.uniform(0.45, 0.7)
                    x = lerp(x0 + 1.5, x1 - 1.5, (i + rng.uniform(0.1, 0.9)) / n)
                    s = rng.uniform(s0, s1)
                    with b.at(x, sgn * (hw + s * SLOPE + 0.1), Z - s - h * 0.45, rz=rng.uniform(0, 90), rx=sgn * rng.uniform(-12, 28)):
                        b.stone(w, d, h, mat="masonry", col=shade("grey", 0.95 if s < 2.6 else 0.8), jitter=0.22, ch=0.3)
    with b.detail(2):
        with b.at(0, -hw + 0.75, Z):
            PP.wall_stones(b, x0, x1, 0.05, 1.05, 0.62, n=8, col="grey", size=(0.3, 0.55))
        for x in (-3.6, 0.4, 3.9):
            PP.tuft(b, x, -hw + 1.2, Z, r=0.1, h=0.18, n=4)
            PP.tuft(b, x + 0.8, hw - 0.8, Z, r=0.1, h=0.16, n=4)
        PP.rope_turns(b, -2.4, hw - 1.1, Z + 0.28, r=0.185, turns=2)
        PP.coil(b, 2.0, hw - 1.7, Z + 0.03, r=0.26, turns=2)
