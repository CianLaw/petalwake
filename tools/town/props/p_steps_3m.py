# wide street steps rising 3 m: two flights of nine with a deep landing between, cheek walls, a handrail, pots and a cat
from kit import *
import parts as P
import parts_p as PP
import parts_h as PH

N, RISE, GOING, LAND, TOP = 18, 3.0 / 18, 0.42, 1.3, 0.9
RUN = (N - 2) * GOING + LAND + TOP
META = {"name": "Street steps rising 3 m", "kind": "prop", "group": "walls", "clear": 4.9, "width": 4.0, "rise": 3.0, "run": round(RUN, 3), "length": round(RUN, 3), "axis": "y", "wobble": 0.0,
        "notes": "climbs toward +y: foot at z = 0 on y = -run/2, head at z = 3 on y = +run/2; a landing half way; 3.32 m clear between the cheek walls"}


def build(b):
    s = PP.street_steps(b, w=4.0, n=N, rise=RISE, going=GOING, landings=(9,), landing=LAND, top=TOP)
    iw = s["clear"]
    with b.detail(2):
        for k, sx, fl in ((2, 1, ["#e8497a", "#f4f1e4"]), (5, -1, ["#f5c842"]), (8, 1, ["#b08ae6", "#f2a0bd"]), (8, -1, ["#e85d3a", "#f4f1e4"]), (12, -1, ["#e8497a"]), (15, 1, ["#f5c842", "#f2a0bd"])):
            yk, d, z = s["treads"][k]
            PP.pot_plant(b, sx * (iw / 2 - 0.24), yk + d * 0.5, z, r=0.15, h=0.24, flowers=fl)
        yk, d, z = s["treads"][8]
        PH.cat(b, -0.9, yk + 0.8, z, rz=200)
        for k, sx in ((0, -1), (4, 1), (10, 1), (13, -1), (16, 1)):
            yk, d, z = s["treads"][k]
            PP.tuft(b, sx * (iw / 2 - 0.08), yk + d * 0.8, z, r=0.09, h=0.16, n=4)
