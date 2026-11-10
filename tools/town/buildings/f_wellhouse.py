# Sweetwater Well: the well at the meeting of the meadow paths; the water is cold enough to make your teeth ache and everyone stops here.
# Massing: a round stone well-head on a flagged step, four oak posts and a little pyramid roof of tiles over it, a windlass with its rope and
#          bucket between the posts.
# Materials: grey rubble well-head with a worn ashlar rim, oak, terracotta tiles; accent red (the bucket's band).
from kit import *
import parts as P
import parts_k as PK
import parts_m as PM
import parts_f as F

META = {"name": "Sweetwater Well", "kind": "well", "lot": (3.0, 3.0)}

CX, CY = 0.0, 1.5
STEP = 0.18
PLATE = 2.3


def build(b):
    with b.at(CX, CY):
        # ---- the flagged step and its hidden footing
        b.box(2.3, 2.3, STEP, "flagstone", col="sand", z=0.0)
        b.box(2.3, 2.3, 3.0, "masonry", col=shade("warm", 0.85), z=-3.0, top=False)
        b.footprint(-1.15, -1.15, 1.15, 1.15, STEP)

        # ---- the well-head: outside, worn rim, the dark shaft and the water
        with b.at(z=STEP):
            b.revolve([(0.78, 0.0), (0.74, 0.72), (0.76, 0.74), (0.76, 0.86)], "masonry", col="grey", seg=14, lod=0)
            b.revolve([(0.76, 0.86), (0.5, 0.86)], "ashlar", col="stone", seg=14, lod=0)
            b.revolve([(0.5, 0.86), (0.5, -0.3)], "masonry", col="#8a8478", seg=14, lod=0)
            b.disc(0.5, "water", col="#4f7f8a", seg=14, z=-0.25, lod=0)
            for k in range(7):
                with b.at(rz=51.4 * k + 12):
                    b.stone(0.42, 0.16, 0.24, mat="masonry", col="grey", lod=2, y=-0.74, z=b.r(0.12, 0.5), jitter=0.2)

        # ---- four posts, plates, the roof
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.beam((sx * 0.95, sy * 0.95, STEP), (sx * 0.95, sy * 0.95, PLATE), w=0.16, mat="timber", col="darkoak", lod=0)
                with b.detail(1):
                    b.beam((sx * 0.95, sy * 0.95, PLATE - 0.55), (sx * 0.5, sy * 0.95, PLATE - 0.06), w=0.09, mat="timber", col="darkoak", caps=False)
                    b.beam((sx * 0.95, sy * 0.95, PLATE - 0.55), (sx * 0.95, sy * 0.5, PLATE - 0.06), w=0.09, mat="timber", col="darkoak", caps=False)
            b.beam((sx * 0.95, -1.08, PLATE), (sx * 0.95, 1.08, PLATE), w=0.16, h=0.16, mat="timber", col="darkoak", lod=0, up=(0, 0, 1))
            b.beam((-1.08, sx * 0.95, PLATE + 0.02), (1.08, sx * 0.95, PLATE + 0.02), w=0.16, h=0.16, mat="timber", col="darkoak", lod=0, up=(0, 0, 1))
        rise = PK.open_roof(b, 2.14, 2.14, pitch=46, mat="tiles", z=PLATE + 0.1, eave=0.24, course=0.34)
        PM.ball(b, 0.0, 0.0, PLATE + 0.1 + rise - 0.06, r=0.11, mat="metal", col="brass")
        F.dove(b, 0.45, -0.35, PLATE + 0.1 + rise * 0.62, rz=40)

        # ---- the windlass: side rails, the drum on its axle, crank, rope and bucket
        zw = STEP + 1.5
        with b.detail(1):
            for sx in (-1, 1):
                b.beam((sx * 0.95, -0.95, zw), (sx * 0.95, 0.95, zw), w=0.09, h=0.12, mat="timber", col="darkoak", up=(0, 0, 1), caps=False)
            b.tube((-1.0, 0.0, zw), (1.0, 0.0, zw), r=0.04, mat="metal", col="iron", n=6)
            b.tube((-0.52, 0.0, zw), (0.52, 0.0, zw), r=0.13, mat="planks", col="#b08f6e", n=8, caps=True)
            b.beam((1.05, 0.0, zw), (1.05, 0.0, zw - 0.3), w=0.035, mat="metal", col="iron")
            b.beam((1.05, 0.0, zw - 0.3), (1.2, 0.0, zw - 0.3), w=0.035, mat="metal", col="iron")
        with b.detail(2):
            for x in (-0.2, -0.1, 0.0, 0.1):
                with b.at(x, 0.0, zw, ry=90):
                    b.revolve([(0.135, -0.04), (0.155, 0.0), (0.135, 0.04)], "cloth", col="#b8a57f", seg=8)
            F.rope(b, (0.1, -0.13, zw), (0.1, -0.13, STEP + 1.08), r=0.012, col="#b8a57f")
        with b.at(0.1, -0.13, STEP + 0.8):
            F.bucket(b, 0, 0, 0, r=0.15, h=0.28, handle=True)
            with b.detail(2):
                b.revolve([(0.153, 0.19), (0.158, 0.25)], "paint", col="red", seg=8)
        F.bucket(b, -0.85, -0.55, STEP, r=0.14, h=0.26)
        with b.detail(2):                                 # the tin cup on its chain
            F.rope(b, (0.95, -0.87, zw - 0.3), (0.86, -0.72, STEP + 0.92), r=0.006, col="#3a3a3e")
            with b.at(0.84, -0.7, STEP + 0.86):
                b.revolve([(0.04, 0.0), (0.05, 0.08)], "metal", col="lead", seg=6)
        # ---- moss, ferns and flowers round the step
        for (x, y) in ((-1.22, -0.7), (1.2, 0.6), (-0.5, 1.25), (0.8, -1.24)):
            F.flowers(b, x, y, 0.0, n=4, spread=0.2, h=0.26)
        with b.detail(2):
            b.blob(0.3, 0.2, 0.1, mat="ivy", col="#7fa85a", x=-0.9, y=0.95, z=STEP, seg=5, rings=2, bottom=False)
            b.blob(0.24, 0.3, 0.09, mat="ivy", col="#8fb86a", x=0.98, y=-0.2, z=STEP, seg=5, rings=2, bottom=False)
