# a scarecrow: sack head under a battered hat, an old coat that flaps, straw at the cuffs, and a crow that is not scared
from kit import *
import parts as P
import parts_p as PP
import parts_m as PM

META = {"name": "Scarecrow", "kind": "prop", "group": "green", "clear": 1.1, "wobble": 0.02, "lean": (0.02, 0.01)}


def build(b):
    coat, patch = "#6f7f9a", "#b5564a"
    with b.detail(1):
        b.beam((0, 0, -0.3), (0, 0, 1.95), w=0.07, mat="timber")
        b.beam((-0.85, 0, 1.48), (0.85, 0, 1.52), w=0.055, mat="timber")
        b.blob(0.17, 0.16, 0.2, mat="cloth", col="#d9c9a3", z=1.84, seg=7, rings=4, rough=0.08)                 # the head
        b.revolve([(0.36, 2.0), (0.34, 1.97), (0.17, 2.0), (0.14, 2.22), (0.03, 2.3), (0.0, 2.3)], "thatch", col="!#c9a860", seg=9)      # straw hat
        b.disc(0.36, "thatch", col="!#b99850", seg=9, z=1.975, r_in=0.15, down=True)
        # the coat: front and back hang from the arms and flap
        for sy, cc in ((-1, coat), (1, shade(coat, 0.85))):
            y = sy * 0.1
            PP.face2(b, [(-0.3, y, 1.58), (-0.36, y * 1.4, 0.72), (0.36, y * 1.4, 0.72), (0.3, y, 1.58)], "cloth", col=cc, wind=(0.05, 0.5, 0.5, 0.05))
        for sx in (-1, 1):
            PP.sweep(b, [(sx * 0.26, 0, 1.55), (sx * 0.55, 0, 1.5), (sx * 0.8, 0, 1.44)], radii=[0.1, 0.085, 0.075], n=5, mat="cloth", col=coat, wind=[0.0, 0.15, 0.3])
            PP.face2(b, [(sx * 0.3, -0.1, 1.58), (sx * 0.36, -0.14, 0.72), (sx * 0.36, 0.14, 0.72), (sx * 0.3, 0.1, 1.58)], "cloth", col=shade(coat, 0.9), wind=(0.05, 0.5, 0.5, 0.05))
    with b.detail(2):
        for sx in (-1, 1):                                    # straw at the cuffs
            for k in range(4):
                PP.face2(b, [(sx * 0.78, -0.04 + 0.03 * k, 1.47), (sx * 0.78, 0.0 + 0.03 * k, 1.4), (sx * (0.98 + 0.04 * (k % 2)), -0.06 + 0.04 * k, 1.36 + 0.05 * k)], "thatch", col=PP.STRAW, wind=(0, 0, 0.5))
        for k in range(5):
            PP.face2(b, [(-0.1 + 0.05 * k, -0.11, 1.66), (-0.06 + 0.05 * k, -0.11, 1.66), (-0.12 + 0.06 * k, -0.2, 1.52)], "thatch", col=PP.STRAW, wind=(0, 0, 0.4))
        b.box(0.14, 0.012, 0.14, "cloth", col=patch, x=0.12, y=-0.142, z=0.95, bottom=True)
        for z in (1.1, 1.26, 1.42):
            b.box(0.035, 0.012, 0.035, "paint", col="#2c2a2a", x=0.0, y=-0.118 - 0.04 * (1.58 - z) / 0.86, z=z, bottom=True)
        b.box(0.045, 0.02, 0.03, "paint", col="#2c2a2a", x=-0.06, y=-0.16, z=1.86, bottom=True)                # eyes and a stitched grin
        b.box(0.045, 0.02, 0.03, "paint", col="#2c2a2a", x=0.06, y=-0.16, z=1.86, bottom=True)
        b.box(0.12, 0.02, 0.016, "paint", col="#7a3a30", x=0.0, y=-0.155, z=1.77, bottom=True)
        PP.face2(b, [(-0.12, -0.02, 1.68), (0.12, -0.02, 1.68), (0.2, -0.1, 1.2), (0.1, -0.12, 1.22)], "cloth", col="#b5433a", wind=(0, 0, 0.7, 0.7))      # a red scarf
        PM.pigeon(b, 0.62, 0.0, 1.55, rz=250, col="#2c2a2a")
        PP.tuft(b, 0.15, 0.12, 0, r=0.12, h=0.26)
        PP.tuft(b, -0.2, -0.1, 0, r=0.1, h=0.2, col="!#d9c060")
