# washing day: a line of laundry between two posts, propped in the middle, the basket waiting underneath
from kit import *
import parts as P
import parts_p as PP

L = 5.4
META = {"name": "Washing line", "kind": "prop", "group": "green", "clear": 2.9, "length": L, "axis": "x", "wobble": 0.02}


def build(b):
    with b.detail(1):
        for sx in (-1, 1):
            b.beam((sx * 2.6, 0, -0.3), (sx * 2.66, 0, 2.3), w=0.09, mat="timber", col="greyoak")
            b.beam((sx * 2.66 - 0.25, 0, 2.2), (sx * 2.66 + 0.25, 0, 2.2), w=0.05, mat="timber", col="greyoak")
        b.beam((0.3, 0.5, 0.0), (0.0, 0.0, 2.02), w=0.045, mat="planks", col="#c9a57a")              # the prop
    P.laundry(b, (-2.64, 0, 2.22), (0.0, 0.0, 2.0), n=4, sag=0.12)
    P.laundry(b, (0.0, 0.0, 2.0), (2.64, 0, 2.22), n=4, sag=0.14, cols=["linen", "#bcd4ea", "#f2c4cf", "#f6d9a8", "stripe_red"])
    with b.detail(2):
        PP.basket(b, 0.9, -0.5, 0, r=0.3, h=0.26, fill="#f3ecd9", heap=0.12)
        for (x, y) in ((-2.4, 0.3), (2.45, -0.3), (0.3, 0.7)):
            PP.tuft(b, x, y, 0, r=0.12, h=0.24)
