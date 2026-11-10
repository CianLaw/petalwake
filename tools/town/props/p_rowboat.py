# a clinker rowing boat: three thwarts, bottom boards, oars shipped, the painter coiled in the bow
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Rowing boat", "kind": "prop", "group": "harbour", "clear": 2.3, "length": 4.0, "axis": "x", "bow": "+x",
        "float": True, "draft": 0.23, "wobble": 0.01}


def build(b):
    H = PP.Hull(L=4.0, B=1.45, depth=0.58, draft=0.16, planks=5, stations=9)
    with b.detail(1):
        H.build(b, cols=["ivory", "ivory", "ivory", "ivory", "red"], inner="#d9bd8a", gunwale="darkoak")
        H.sole(b, -1.93, 1.6, 0.05, n=8)
        H.thwart(b, -0.2, col="#b98f5e")
        H.thwart(b, 0.95, w=0.2, col="#b98f5e")
        H.thwart(b, -1.62, w=0.5, z=0.22, col="#b98f5e")
    with b.detail(2):
        H.ribs(b, [-1.25, -0.75, 0.3, 0.6, 1.3])
        PP.oar(b, (-1.45, 0.2, 0.3), (1.45, 0.3, 0.29))
        PP.oar(b, (-1.4, -0.28, 0.3), (1.5, -0.2, 0.29))
        for sy in (-1, 1):                                  # rowlocks
            y = sy * (H.hb(H.u_at(-0.55)) + 0.0)
            z = H.zs(H.u_at(-0.55))
            b.box(0.2, 0.06, 0.035, "planks", col="darkoak", x=-0.55, y=y - sy * 0.02, z=z)
            for dx in (-0.035, 0.035):
                b.tube((-0.55 + dx, y - sy * 0.02, z + 0.03), (-0.55 + dx * 1.5, y - sy * 0.02, z + 0.12), r=0.01, mat="metal", col="iron", n=3)
        PP.coil(b, 1.2, 0.0, 0.05, r=0.14, turns=2, rr=0.02, tail=False)
        PP.rope(b, [(1.34, 0.02, 0.08), (1.6, 0.0, 0.32), (1.84, 0.0, H.zs(0.92) - 0.02)], r=0.014)
        PP.bucket(b, -1.05, 0.2, 0.05, r=0.1, h=0.2)
