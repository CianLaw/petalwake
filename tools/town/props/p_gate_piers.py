# a gateway: two stone piers with ball finials, a pair of wrought-iron gates (one standing open), a lantern on an iron overthrow
import math
from kit import *
import parts as P
import parts_p as PP
import parts_c as PC

W = 3.0
META = {"name": "Gate piers and iron gate", "kind": "prop", "group": "square", "clear": 2.4, "opening": W, "wobble": 0.015,
        "notes": "the gateway is 3 m wide along x and looks toward -y; the leaves swing inward (+y)"}


def build(b):
    PC.gate_piers(b, w=W, h=2.3, size=0.6, mat="ashlar", col="sand", ball=True)
    with b.detail(1):
        with b.at(-W / 2 + 0.03, 0, 0):
            PP.iron_gate(b, w=W / 2 - 0.05, h=1.95, bars=8, ajar=38, hinge=-1)
        with b.at(W / 2 - 0.03, 0, 0):
            PP.iron_gate(b, w=W / 2 - 0.05, h=1.95, bars=8, ajar=6, hinge=1)
        n = 10
        arc = [(-W / 2 - 0.1 + (W + 0.2) * i / n, 0, 2.42 + 0.75 * math.sin(math.pi * i / n)) for i in range(n + 1)]
        PP.sweep(b, arc, r=0.024, n=4, mat="metal", col="iron")
        with b.at(0, 0, 3.17 - 0.02):
            PP.lantern(b, s=0.28, h=0.42, sides=4, hang=0.14)
    with b.detail(2):
        for sx in (-1, 1):                                    # scrolls springing from the piers
            PP.sweep(b, [(sx * (W / 2 + 0.1), 0, 2.42), (sx * 1.2, 0, 2.5), (sx * 1.05, 0, 2.7), (sx * 1.25, 0, 2.78), (sx * 1.35, 0, 2.66)], r=0.014, n=3, mat="metal", col="iron")
        for (x, y) in ((-2.2, -0.3), (2.25, 0.3), (-1.9, 0.45), (1.9, -0.4)):
            PP.tuft(b, x, y, 0, r=0.12, h=0.24)
        PC.climber(b, (W / 2 + 0.62, 0.2, 0.2), (W / 2 + 0.5, 0.15, 2.0), n=5, r=0.22, bloom=["#f4f1e4"])
