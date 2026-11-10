# quay edge, 8 m: battered dressed-stone wall with coping, fenders, iron rings, a bollard and a ladder
from kit import *
import parts as P
import parts_p as PP

L = 8.0
META = {"name": "Quay edge 8 m (with ladder)", "kind": "prop", "group": "harbour", "clear": 4.4, "length": L, "axis": "x", "wobble": 0.0,
        "deck": 0.0, "depth": PP.QUAY_D, "face_y": -PP.QUAY_D / 2, "bottom": -PP.DEEP,
        "notes": "seat at quay level; the wall goes 7.5 m down; the face (water side) is at y = -1.8, looking toward -y"}


def build(b):
    PP.quay_segment(b, L, ladder=2.5)
