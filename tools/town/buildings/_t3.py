# kit example 3: a turning part (windmill sails)
from kit import *
import parts as P
META = {"name": "Spin test", "kind": "test"}
def build(b):
    P.round_base(b, 2.6, h=0.8)
    t = b.round(2.6, 9.0, r1=2.0, mat="plaster", col="white")
    P.door(t, 0, col="blue", z=0.3, steps=1)
    b.cone_roof(2.0, 2.6, mat="shingle", z=9.0, eave=0.3)
    with b.at(0, -2.5, 8.2):
        with b.spin(speed=0.12):
            for k in range(4):
                with b.at(ry=90 * k):
                    b.beam((0, 0, 0), (0, 0, 5.2), w=0.14, lod=0)
                    b.quad((0.1, 0, 1.0), (1.2, 0, 1.0), (1.2, 0, 5.0), (0.1, 0, 5.0), "cloth", col="linen")
                    b.quad((0.1, 0, 5.0), (1.2, 0, 5.0), (1.2, 0, 1.0), (0.1, 0, 1.0), "cloth", col="linen")
