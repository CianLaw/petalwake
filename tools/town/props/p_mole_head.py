# mole head, bare: the rounded end of a mole with a kerb all round it, for a light to stand on
import parts_p as PP
import parts_x as PX

META = {"name": "Mole head (bare)", "kind": "prop", "group": "harbour", "clear": 9.5, "wobble": 0.0, "top_width": PX.MOLE_TW, "deck": 0.0, "bottom": -PP.DEEP,
        "notes": "joins the +x end of a p_mole run on its own -x side; the round bulges toward +x; no wall"}


def build(b):
    PX.mole_head(b, wall=None)
