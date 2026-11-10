# quay edge, 8 m, the plain one: no ladder, three rings, a gull on the bollard (alternate it with p_quay)
from kit import *
import parts as P
import parts_p as PP

L = 8.0
META = {"name": "Quay edge 8 m (plain)", "kind": "prop", "group": "harbour", "clear": 4.4, "length": L, "axis": "x", "wobble": 0.0,
        "deck": 0.0, "depth": PP.QUAY_D, "face_y": -PP.QUAY_D / 2, "bottom": -PP.DEEP,
        "notes": "seat at quay level; the wall goes 7.5 m down; the face (water side) is at y = -1.8, looking toward -y"}


def build(b):
    PP.quay_segment(b, L, ladder=None, rings=(-3.1, -0.2, 2.7), fenders=(-1.9, 1.3), bollard=2.2, gull=True)
