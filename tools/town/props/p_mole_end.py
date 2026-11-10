# mole head with the sea wall carried round its tip: for the outer end of a run of p_mole laid from that end inward
import parts_p as PP
import parts_x as PX

META = {"name": "Mole head (walled)", "kind": "prop", "group": "harbour", "clear": 9.5, "wobble": 0.0, "top_width": PX.MOLE_TW, "deck": 0.0, "bottom": -PP.DEEP,
        "notes": "joins a p_mole run on its own -x side, turned half round from the run's pieces: the wall it carries on is on its +y side"}


def build(b):
    PX.mole_head(b, wall="left")
