# kit exemplar 1: a round courier tower with a timber gallery, and the house grown onto its side
from kit import *
import parts as P

META = {"name": "Gallery Tower (kit example)", "kind": "tower", "lean": (0.004, -0.003)}

def build(b):
    R = 3.1
    # --- the shaft: battered foot, slight taper, a string course under the gallery
    t = b.round(R, 15.5, r1=2.75, mat="masonry", col="warm", seg=24)
    P.round_base(b, R, h=1.0, out=0.32, ring=t)          # ring=t keeps the doorway clear of the stone foot
    P.door(t, 0, w=1.05, h=2.2, arch=0.5, col="teal", steps=2, z=0.36, lamp=True)
    P.window(t, 300, 4.2, w=0.6, h=1.2, arch=0.3, frame="ivory", bars=(1, 2))
    P.window(t, 70, 6.6, w=0.6, h=1.2, arch=0.3, shutters="teal", box=True)
    P.window(t, 200, 8.8, w=0.55, h=1.0, arch=0.27)
    P.window(t, 330, 10.4, w=0.6, h=1.2, arch=0.3, shutters="teal")
    P.stones(t, n=46, z0=0.8, z1=12.5, u1=t.w)
    P.ivy(t, 250, 0.3, w=2.2, h=4.5, n=11)
    P.ring_band(b, 2.83, 12.6, h=0.22, out=0.12)
    # --- the gallery: where the rider lands
    P.gallery(b, 2.78, 4.35, 13.0, seg=24, rail="balusters", gap=(-28, 28), bracket_drop=1.5)
    with b.at(z=13.0):
        P.landing_mark(b, 0.62, z=0.015)
    b.pad(0, -3.6, 13.0, radius=0.75, face=0, name="Gallery")
    with b.at(0, -3.55, 13.0):
        P.landing_mark(b, 0.6)
    P.door(t, 0, w=0.85, h=1.9, z=13.02, col="teal", frame="timber")
    # --- cap: a tall bell-cast slate cone with a dormer and a pennant
    b.cone_roof(2.75, 6.4, mat="slate", z=15.5, seg=24, eave=0.75, flare=0.45, course=0.52)
    P.dormer(b, 0, -1.55, 16.9, w=1.0, h=0.9, depth=1.6, roof="slate", col="cream", frame="ivory")
    P.flag(b, 0, 0, 22.9, pole=1.8, w=1.5, h=0.6, col="stripe_yellow")
    # --- the house on its flank
    bd = b.body(5.6, 6.2, 5.0, mat="plaster", col="cream", x=5.3, y=3.3)
    P.plinth(bd, h=0.8)
    P.quoins(bd, corners="rb", z0=0.8)
    P.door(bd.front, 1.3, col="teal", steps=1, z=0.2, porch="gable")
    P.window(bd.front, 3.9, 1.25, shutters="teal", box=True)
    P.window(bd.front, 1.5, 3.3, shutters="teal")
    P.window(bd.front, 3.9, 3.3, shutters="teal")
    P.window(bd.right, 2.0, 1.25, shutters="teal")
    P.window(bd.right, 4.4, 3.3, w=0.7)
    P.sign(bd.front, 2.7, 3.1, emblem="hat", col="plum")
    bd.gable(ridge="x", pitch=47, mat="tiles", sag=0.14, eave=0.5)
    P.chimney(b, 6.9, 4.4, 5.2, 3.4, mat="brick", pots=2)
    P.laundry(b, (2.4, -0.2, 9.0), (7.4, 0.1, 6.3), n=5)
    P.barrel(b, 2.6, -0.5); P.crate(b, 3.4, -0.6, rz=20); P.planter(b, 6.9, -0.35)
