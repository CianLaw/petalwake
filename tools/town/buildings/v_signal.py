# Cairnwick's signal tower: a fire is lit in the iron basket on its cap when the fleet is out in fog or dark, and
# has been for three hundred years. A slender round rubble shaft with a white day-mark band, a stone walk with an
# iron rail under the watch room, the keeper's low house hunched against its foot. Grey stone, lime-wash, red paint.
from kit import *
import parts as P
import parts_v as V
import parts_c as PC
import parts_h as PH

META = {"name": "Cairnwick Signal Tower", "kind": "tower", "lot": (8.0, 8.0), "lean": (0.0012, -0.0008)}

TX, TY = -0.45, 4.5


def build(b):
    red = "red"
    b.footprint(-3.9, 0.0, 3.9, 7.9, 8.0)
    # ------------------------------------------------------------------ the shaft, in three stages
    s1 = b.round(2.5, 7.0, r1=2.2, mat="masonry", col="grey", x=TX, y=TY, z=0.0, seg=20, depth=0.5)
    s2 = b.round(2.2, 7.0, r1=1.95, mat="masonry", col="grey", x=TX, y=TY, z=7.0, seg=20, depth=0.45, foot=False)
    s3 = b.round(1.95, 7.0, r1=1.72, mat="masonry", col="grey", x=TX, y=TY, z=14.0, seg=20, depth=0.42, foot=False)
    P.round_base(b, 2.5, h=1.1, out=0.34, col=shade("grey", 0.92), seg=20, ring=s1)
    V.door(s1, 0, w=1.0, h=2.0, z=0.6, col=red, steps=3, step=False, lamp=True)
    V.window(s1, 62, 3.9, w=0.5, h=0.9, col=red, shut="one")
    V.window(s1, 300, 5.2, w=0.5, h=0.9, col=red, shut="closed")
    V.window(s2, 205, 0.9, w=0.5, h=0.9, col=red, shut="half")
    V.window(s2, 80, 6.0, w=0.5, h=0.85, col=red, shut="one")
    V.window(s3, 330, 1.9, w=0.48, h=0.85, col=red, shut="closed")
    V.window(s3, 150, 3.6, w=0.48, h=0.85, col=red, shut="open")
    V.rubble(s1, n=34, size=(0.32, 0.7), z0=1.2); V.rubble(s2, n=16, z1=2.3); V.rubble(s2, n=6, z0=5.7); V.rubble(s3, n=22, z1=5.4)
    P.ring_band(b, 2.2, 6.9, h=0.24, out=0.1, mat="masonry", col=shade("grey", 1.1), seg=20, x=TX, y=TY)
    P.ring_band(b, 1.95, 13.9, h=0.22, out=0.09, mat="masonry", col=shade("grey", 1.1), seg=20, x=TX, y=TY)
    # the day-mark: a broad lime-washed band that shipping can pick out against the moor
    with b.at(TX, TY, 7.0):
        ra, rb = s2.radius(2.5), s2.radius(5.5)
        b.revolve([(ra - 0.03, 2.44), (ra + 0.035, 2.5), (rb + 0.035, 5.5), (rb - 0.03, 5.56)], "plaster", col="white", seg=20, lod=0)
    # ------------------------------------------------------------------ the stone walk: where the rider lands
    GZ = 21.0
    PC.stone_walk(b, 1.72, 3.35, GZ, seg=20, floor="flagstone", floor_col="grey", mat="masonry", col=shade("grey", 1.04), thick=0.22, drop=1.7, x=TX, y=TY)
    with b.at(TX, TY):
        PC.corbels(b, 1.9, GZ - 0.5, n=14, out=0.75, drop=0.8, w=0.3, steps=2, mat="masonry", col=shade("grey", 0.95), lod=1)
        PC.rail_arc(b, 3.25, 27, 333, z=GZ, h=1.05, style="iron", knobs="brass")
    with b.at(TX, TY - 2.55, GZ):
        P.landing_mark(b, 0.72)
    b.pad(TX, TY - 2.55, GZ, radius=0.78, face=0, name="Signal gallery")
    # ------------------------------------------------------------------ the watch room and its cap
    w = b.round(1.72, 3.25, r1=1.66, mat="plaster", col="white", x=TX, y=TY, z=GZ, seg=20, depth=0.4, foot=False)
    V.rubble(w, n=14, size=(0.26, 0.5), proud=0.03, z0=0.0, z1=1.0, mat="masonry", col="grey")
    V.door(w, 100, w=0.78, h=1.85, z=0.04, col=red, step=False, jambs=False)
    V.window(w, 0, 0.95, w=0.52, h=0.85, col=red, shut="open")
    V.window(w, 180, 0.95, w=0.52, h=0.85, col=red, shut="closed")
    V.window(w, 270, 0.95, w=0.52, h=0.85, col=red, shut="half")
    P.ring_band(b, 1.66, GZ + 3.2, h=0.26, out=0.2, mat="masonry", col=shade("grey", 1.1), seg=20, x=TX, y=TY)
    CZ = GZ + 3.46
    b.cone_roof(1.68, 1.9, mat="slate", x=TX, y=TY, z=CZ, seg=20, eave=0.55, flare=0.42, course=0.4, finial=False)
    with b.at(TX, TY, CZ):          # a fascia under the slates' edge (the kit leaves a slit there)
        b.revolve([(2.225, -0.35), (2.25, -0.26)], "planks", col="darkoak", seg=20, lod=0)
    with b.at(TX, TY, CZ):
        with b.detail(1):
            b.tube((0, 0, 1.2), (0, 0, 3.1), r=0.07, mat="metal", col="iron", n=6)
            for k in range(4):
                with b.at(rz=90 * k + 45):
                    V.beam(b, (0, -0.8, 0.82), (0, -0.42, 3.06), w=0.05, mat="metal", col="iron", caps=False)
                    V.beam(b, (0, -0.62, 1.95), (0, 0, 2.0), w=0.035, mat="metal", col="iron", caps=False)
        with b.at(0, 0, 3.12):
            V.fire_basket(b, r=0.62, h=0.6, fire_lod=0)
    # the keeper's way up to feed the fire: an iron ladder up the wall and over the slates
    V.ladder(b, V.polar(2.5, 215, GZ, TX, TY), V.polar(2.26, 215, CZ - 0.2, TX, TY), w=0.4, col="iron", mat="metal", rail=0.04, lod=1)
    V.ladder(b, V.polar(2.2, 215, CZ - 0.16, TX, TY), V.polar(0.5, 215, CZ + 1.5, TX, TY), w=0.4, col="iron", mat="metal", rail=0.04)
    # a davit and a peat basket on its rope, half way up
    d0, d1 = V.polar(3.25, 318, GZ + 1.0, TX, TY), V.polar(3.95, 318, GZ + 1.75, TX, TY)
    with b.detail(1):
        V.beam(b, V.polar(3.25, 318, GZ, TX, TY), d0, w=0.07, mat="metal", col="iron")
        V.beam(b, d0, d1, w=0.07, mat="metal", col="iron")
        V.beam(b, V.polar(3.25, 318, GZ + 0.3, TX, TY), vlerp(d0, d1, 0.7), w=0.045, mat="metal", col="iron", caps=False)
    V.rope(b, d1, (d1[0], d1[1], 9.3), w=0.035, lod=1)
    PH.basket(b, d1[0], d1[1], 8.95, r=0.3, h=0.36, fill=V.PEAT)
    # signal flags from the cap down to the rail, gulls on the rail
    PH.signal_flags(b, (TX + 0.25, TY + 0.1, CZ + 2.2), V.polar(3.25, 78, GZ + 1.08, TX, TY), n=5, sag=0.35, size=0.4)
    PH.gull(b, *V.polar(3.25, 152, GZ + 1.09, TX, TY), rz=130)
    # the keeper's things on the walk: the fuel box and a creel of peats by the door, a bench in the lee, the fog bell
    with b.at(TX, TY, GZ):
        with b.at(rz=132):
            P.crate(b, 0.0, -2.25, 0.0, s=0.62, col="#b9a888", rz=8)
            PH.basket(b, 0.75, -2.35, 0.0, r=0.27, h=0.32, fill=V.PEAT)
        with b.at(rz=228):
            P.bench(b, 0.0, -2.12, 0.0, w=1.2, rz=180)
        with b.at(rz=52):
            with b.detail(1):
                V.beam(b, (0, -1.7, 2.35), (0, -2.45, 2.35), w=0.05, mat="metal", col="iron")
                V.beam(b, (0, -1.7, 1.85), (0, -2.3, 2.33), w=0.035, mat="metal", col="iron", caps=False)
            with b.at(0, -2.35, 2.33, rz=90):
                P.bell(b, 0, 0, 0, r=0.2, beam=0.16)
            V.rope(b, (0, -2.35, 1.95), (0, -2.3, 1.2), w=0.022)
    P.lantern(w, 122, 1.75)
    PH.gull(b, *V.polar(3.25, 232, GZ + 1.09, TX, TY), rz=250, s=0.9)
    # ------------------------------------------------------------------ the keeper's house, hunched at the foot
    h = V.BBody(b, 3.5, 4.2, 2.1, col="dark", x=1.95, batter=0.055, faces={"front": ("plaster", "white"), "left": ("plaster", "white")})
    V.footing(h, boulders="f")
    V.quoins(h, corners="r", col="grey")
    V.door(h.front, 1.25, w=0.9, h=1.6, col=red)
    V.window(h.front, 2.6, 0.85, col=red)
    V.window(h.left, 3.25, 0.85, w=0.55, h=0.75, col=red, shut="one")
    V.window(h.right, 2.1, 0.9, w=0.5, h=0.7)
    V.harl(h.front, n=9, where="both"); V.harl(h.left, n=5, where="base"); V.rubble(h.right, n=12, col=shade("dark", 1.1))
    rf = h.gable(ridge="x", pitch=42, skew=True, mat="slate", apex=None, eave=0.28)
    V.weights(rf, rows=(0.3,), every=0.8)
    V.chimney(b, 3.2, 2.1, 2.9, 2.5, w=0.82, d=0.66, col="dark")
    PH.gull(b, 1.6, 2.1, 2.1 + rf.rise + 0.16, rz=200)
    # the yard before the tower door: drystone, a gate, peat, a barrel under the spout
    V.drystone(b, [(-3.6, 0.3), (-1.12, 0.3)], h=1.0, t=0.5)
    V.drystone(b, [(-3.6, 0.3), (-3.6, 3.1), (-2.55, 3.3)], h=1.0, t=0.5)
    V.gatepost(b, -1.02, 0.3); V.gatepost(b, 0.08, 0.3)
    V.gate(b, (-0.95, 0.3), (0.0, 0.3), ajar=-38)
    V.peat_stack(b, -2.75, 1.25, w=1.5, d=0.8, h=1.05, rz=4)
    V.rain_barrel(b, -0.0, 0.95, r=0.3, h=0.8)
    P.bench(b, 2.6, -0.45, w=1.1)
