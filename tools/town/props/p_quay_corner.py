# quay corner (outer): water on its -y and +x sides; quay runs join on its -x and +y sides
from kit import *
import parts as P
import parts_p as PP

D = PP.QUAY_D
META = {"name": "Quay corner (outer)", "kind": "prop", "group": "harbour", "clear": 2.8, "wobble": 0.0, "size": D, "deck": 0.0, "bottom": -PP.DEEP,
        "notes": "3.6 m square; faces toward -y and +x; a quay run along x joins its -x side, one along y its +y side"}


def build(b):
    h = D / 2
    with b.detail(0):
        PP.quay_face(b, -h, h, grow1=True)
        with b.at(rz=90):
            PP.quay_face(b, -h, h, grow0=True)
        PP.quay_deck(b, -h, h, back=0)
    with b.detail(1):
        PP.quay_coping(b, -h, h - 0.58)
        with b.at(rz=90):
            PP.quay_coping(b, -h, h)
        PP.bollard_stone(b, h - 0.95, -h + 0.95, PP.PAVE, h=0.78, r=0.21)
    with b.detail(2):
        PP.quay_stones(b, -h, h, n=6)
        with b.at(rz=90):
            PP.quay_stones(b, -h, h, n=6)
            with b.at(0.3, -h - PP.quay_out(-1.15), -1.15):
                PP.mooring_ring(b, r=0.15, rr=0.022)
        with b.at(-0.5, -h - PP.quay_out(-1.15), -1.15):
            PP.mooring_ring(b, r=0.15, rr=0.022)
        PP.rope_turns(b, h - 0.95, -h + 0.95, PP.PAVE + 0.3, r=0.2, turns=3)
        PP.coil(b, h - 1.75, -h + 1.5, PP.PAVE, r=0.26, turns=2)
