# a stack of crates and barrels waiting for the carter: a tarpaulin over one end, a cat asleep on top
from kit import *
import parts as P
import parts_p as PP
import parts_m as PM

META = {"name": "Crates and barrels", "kind": "prop", "group": "square", "clear": 1.8}


def build(b):
    with b.detail(1):
        PP.crate(b, -0.55, 0.15, 0, w=0.85, d=0.8, h=0.8, rz=4)
        PP.crate(b, -0.5, 0.2, 0.8, w=0.62, rz=-11, col="#cdb48e")
        PP.crate(b, 0.3, 0.35, 0, w=0.7, d=0.6, h=0.6, rz=-6, col="#e0cba6")
        PP.crate(b, 0.32, 0.36, 0.6, w=0.5, d=0.5, h=0.42, rz=14)
        PP.barrel(b, 1.0, 0.2, 0, r=0.32, h=0.85)
        PP.barrel(b, 0.75, -0.55, 0, r=0.28, h=0.72, col="#b9905e")
        PP.barrel(b, -0.3, -0.72, 0, r=0.27, h=0.74, lying=82, col="#c9a57a")
        PP.sack(b, 1.42, -0.45, 0, r=0.3)
    with b.detail(2):
        PP.sack(b, 1.2, -0.85, 0, r=0.26, col="#cdbb92")
        b.box(0.1, 0.16, 0.08, "planks", col="darkoak", x=-0.62, y=-0.92, z=0, taper=0.6)          # chocks under the lying barrel
        b.box(0.1, 0.16, 0.08, "planks", col="darkoak", x=0.02, y=-0.5, z=0, taper=0.6)
        # a tarpaulin thrown over the big case
        c = "#7f8f6a"
        PP.face2(b, [(-1.0, -0.27, 0.815), (-0.1, -0.2, 0.815), (-0.08, 0.57, 0.815), (-1.0, 0.56, 0.815)], "cloth", col=c)
        PP.face2(b, [(-1.0, -0.27, 0.815), (-1.0, 0.56, 0.815), (-1.02, 0.6, 0.3), (-1.03, -0.33, 0.22)], "cloth", col=c, wind=(0, 0, 0.3, 0.3))
        PP.face2(b, [(-1.0, 0.56, 0.815), (-0.08, 0.57, 0.815), (-0.05, 0.6, 0.36), (-1.02, 0.6, 0.3)], "cloth", col=shade(c, 0.9), wind=(0, 0, 0.3, 0.3))
        PM.cat(b, 0.32, 0.36, 1.02, rz=160, col="#d98a3d", sit=False)
        PP.coil(b, 0.05, -0.25, 0, r=0.24, turns=2, tail=False)
        PP.tuft(b, 1.5, 0.3, 0, r=0.11, h=0.2)
