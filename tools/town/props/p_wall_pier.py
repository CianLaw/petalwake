# a stone pier to end or turn a garden wall: plinth, cap and ball (garden walls 1.7 m high butt against any side)
from kit import *
import parts as P
import parts_p as PP
import parts_m as PM

META = {"name": "Garden wall pier", "kind": "prop", "group": "walls", "clear": 0.6, "size": 0.62, "height": 2.0, "wobble": 0.0}


def build(b):
    S, H = 0.62, 2.0
    with b.detail(0):
        b.box(S, S, H + 1.2, "masonry", col="warm", z=-1.2)
    with b.detail(1):
        b.box(S + 0.1, S + 0.1, 0.3, "ashlar", col="sand", z=-0.04)
        b.box(S + 0.16, S + 0.16, 0.1, "ashlar", col="#f1e4cc", z=H, bottom=True)
        b.box(S + 0.04, S + 0.04, 0.16, "ashlar", col="#f1e4cc", z=H + 0.1, taper=0.45)
        PM.ball(b, 0, 0, H + 0.24, r=0.15, col="#f1e4cc")
    with b.detail(2):
        # corner stones, long and short alternately (drawn by hand: the pier is not a kit Body)
        for i in range(5):
            for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                lx, ly = (0.34, 0.2) if (i + (sx * sy > 0)) % 2 == 0 else (0.2, 0.34)
                with b.at(sx * (S / 2 - lx / 2 + 0.03), sy * (S / 2 - ly / 2 + 0.03), 0.3 + 0.34 * i):
                    b.stone(lx, ly, 0.32, mat="ashlar", col="sand", ch=0.12, jitter=0.05)
        PP.tuft(b, 0.4, -0.38, 0, r=0.1, h=0.2)
