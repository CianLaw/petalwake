# wide street steps rising 2 m: twelve shallow cobbled steps with stone nosings, stepped cheek walls, a handrail, pots
from kit import *
import parts as P
import parts_p as PP

N, RISE, GOING, TOP = 12, 2.0 / 12, 0.42, 0.9
RUN = (N - 1) * GOING + TOP
META = {"name": "Street steps rising 2 m", "kind": "prop", "group": "walls", "clear": 3.5, "width": 4.0, "rise": 2.0, "run": round(RUN, 3), "length": round(RUN, 3), "axis": "y", "wobble": 0.0,
        "notes": "climbs toward +y: foot at z = 0 on y = -run/2, head at z = 2 on y = +run/2; 3.32 m clear between the cheek walls"}


def build(b):
    s = PP.street_steps(b, w=4.0, n=N, rise=RISE, going=GOING, top=TOP)
    iw = s["clear"]
    with b.detail(2):
        for k, sx, fl in ((1, -1, ["#e8497a", "#f4f1e4"]), (4, 1, ["#f5c842", "#e85d3a"]), (7, -1, ["#b08ae6", "#f2a0bd"]), (10, 1, ["#e8497a"])):
            yk, d, z = s["treads"][k]
            PP.pot_plant(b, sx * (iw / 2 - 0.24), yk + d * 0.55, z, r=0.15, h=0.24, flowers=fl)
        for k, sx in ((0, 1), (3, -1), (6, 1), (9, -1)):
            yk, d, z = s["treads"][k]
            PP.tuft(b, sx * (iw / 2 - 0.08), yk + d * 0.8, z, r=0.09, h=0.16, n=4)
