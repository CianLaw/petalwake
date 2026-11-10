# a stone bench: a worn slab on two carved blocks, moss in the joints
from kit import *
import parts as P
import parts_p as PP

META = {"name": "Stone bench", "kind": "prop", "group": "square", "clear": 1.1}


def build(b):
    with b.detail(1):
        for sx in (-1, 1):
            b.stone(0.3, 0.46, 0.38, mat="ashlar", col="grey", x=sx * 0.68, z=-0.02, jitter=0.06, ch=0.15)
        b.stone(1.9, 0.54, 0.12, mat="ashlar", col="stone", z=0.36, jitter=0.03, ch=0.2, bottom=True)
    with b.detail(2):
        b.blob(0.22, 0.1, 0.03, mat="ivy", col="#9fb86a", x=-0.7, y=0.2, z=0.47, seg=6, rings=2, bottom=False)
        for (x, y) in ((-0.9, -0.3), (0.95, 0.3), (0.2, 0.34)):
            PP.tuft(b, x, y, 0, r=0.11, h=0.2)
        PP.blooms(b, 0.95, 0.35, 0.1, 0.15, n=4, cols=["#f4f1e4", "#f5c842"])
