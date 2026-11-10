# Pippin Cote: the lost manor's dovecote, alone in the clover; the manor went, the doves stayed, and the post now comes to their front step.
# Massing: an eight-sided battered rubble shaft 8.4 m high, a stone alighting ledge round its head with a broad boarded landing on struts at
#          the front, a slim half-timbered lantern stage of pigeon-holes above, an eight-sided bell-cast tile roof and a dove vane.
# Materials: honey rubble with ashlar bands and ledge, cream plaster and oak in the lantern, terracotta tiles; accent mustard.
from kit import *
import parts as P
import parts_c as PC
import parts_m as PM
import parts_f as F

META = {"name": "Pippin Cote", "kind": "tower", "lot": (5.0, 5.0)}

AX, AY = 0.0, 2.85
R, HS, TAPER = 2.05, 8.4, 0.9       # shaft: corner radius, height, taper
LEDGE = 8.4                        # top of the stone ledge
DECK = 8.48                        # top of the boards the rider lands on
RD, HD = 1.1, 2.75                 # lantern stage


def build(b):
    side = 2 * R * math.sin(math.pi / 8)
    r_at = lambda z: R * (1 - (1 - TAPER) * z / HS)
    ap = lambda z: r_at(z) * math.cos(math.pi / 8)

    # ---- the shaft
    faces = PC.poly_tower(b, 8, R, HS, taper=TAPER, mat="masonry", col="stone", x=AX, y=AY, depth=0.3)
    PC.poly_plinth(b, 8, R, h=0.8, out=0.09, doors=[(0, side / 2, 1.0)], x=AX, y=AY)
    P.door(faces[0], side / 2, w=0.85, h=1.9, arch=0.42, col="mustard", z=0.3, steps=1, lamp=True)
    P.window(faces[2], side / 2, 3.4, w=0.5, h=1.1, arch=0.25)
    P.window(faces[6], side / 2, 3.4, w=0.5, h=1.1, arch=0.25, shutters="mustard")
    F.slit(faces[4], side / 2, 2.4, w=0.15, h=0.9)
    F.slit(faces[0], side / 2, 4.6, w=0.15, h=0.9)
    for k in (1, 3, 5, 7):
        PM.pigeonholes(faces[k], side / 2, 6.3, cols=3, rows=2, dx=0.4, dz=0.52, birds=1 if k != 5 else 2)
    for k in (0, 2, 4, 6):
        P.stones(faces[k], n=7, z0=1.0, z1=7.6, u0=0.2, u1=side - 0.2, proud=0.05, size=(0.26, 0.5))
    with b.at(AX, AY, 0.0, rz=22.5):
        P.ring_band(b, r_at(5.5), 5.5, h=0.18, out=0.07, seg=8)
    P.ivy(faces[6], side / 2 + 0.2, 0.8, w=1.2, h=2.3, n=7)

    # ---- the alighting ledge: stone all round on corbels, boards on struts at the front
    with b.at(AX, AY):
        PC.corbels(b, ap(HS) - 0.02, LEDGE - 0.2, n=16, out=0.4, drop=0.45, col="sand")
        Rl = r_at(HS) + 0.42
        b.prism([(Rl * math.sin(rad(22.5 + 45 * k)), -Rl * math.cos(rad(22.5 + 45 * k))) for k in range(8)], 0.2, "ashlar", col="sand", z=LEDGE - 0.2, bottom=True)
    yf = AY - RD * math.cos(math.pi / 8)          # the lantern's front face
    y0 = 0.16                                     # front edge of the boards
    F.deck(b, 2.7, yf - y0, x=AX, y=(yf + y0) / 2, z=DECK, thick=0.08, joists=0.66)
    with b.detail(1):
        for sx in (-1, 1):
            b.beam((sx * 0.62, AY - ap(6.3) + 0.05, 6.3), (sx * 1.05, y0 + 0.2, DECK - 0.3), w=0.16, mat="timber", col="darkoak")
            b.beam((sx * 0.62, AY - ap(6.3) + 0.02, 6.25), (sx * 0.62, AY - ap(6.3) + 0.02, 6.75), w=0.2, h=0.12, mat="timber", col="darkoak")
    P.railing(b, [(-1.29, yf - 0.3, DECK), (-1.29, y0 + 0.07, DECK), (-0.92, y0 + 0.07, DECK)], h=0.95, style="balusters")
    P.railing(b, [(0.92, y0 + 0.07, DECK), (1.29, y0 + 0.07, DECK), (1.29, yf - 0.3, DECK)], h=0.95, style="balusters")
    b.pad(AX, y0 + 0.78, DECK, radius=0.75, face=0, name="Alighting ledge")
    with b.at(AX, y0 + 0.78, DECK):
        P.landing_mark(b, 0.7)

    # ---- the lantern stage: plaster and oak, pigeon-holes, a hatch door onto the ledge
    lf = PC.poly_tower(b, 8, RD, HD, mat="plaster", col="cream", x=AX, y=AY, z=LEDGE, depth=0.14, foot=False)
    sd = 2 * RD * math.sin(math.pi / 8)
    P.door(lf[1], sd / 2, w=0.56, h=1.55, z=0.1, col="mustard", frame="timber")
    for k, wl in enumerate(lf):
        P.timber_frame(wl, posts=[0.0, sd], rails=[0.0, HD] if k in (0, 1) else [0.0, HD * 0.3, HD], braces=None, w=0.13)
        if k not in (0, 1):
            PM.pigeonholes(wl, sd / 2, 0.95, cols=2, rows=2, dx=0.36, dz=0.5, birds=1 if k % 2 == 0 else 0)
    with b.at(AX, AY, LEDGE + HD, rz=22.5):
        b.cone_roof(RD, 2.05, mat="tiles", seg=8, smooth=False, eave=0.32, flare=0.5, course=0.4, finial=False)
    PC.vane(b, AX, AY, LEDGE + HD + 1.95, h=1.5, shape="dove", size=1.3)

    # ---- doves on the ledge, and the foot of the tower
    PC.doves(b, [(AX + 2.05 * math.sin(rad(a)), AY - 2.05 * math.cos(rad(a)), LEDGE) for a in (62, 118, 151, 208, 246, 301)])
    F.dove(b, 1.29, y0 + 0.07, DECK + 1.0, rz=140)
    F.ladder_to(b, (2.25, 1.1, 0.0), (1.55, 1.6, 3.2), w=0.4)
    P.sack(b, -1.5, 0.5, 0.0, r=0.27)
    F.bucket(b, -1.05, 0.42, 0.0)
    for (x, y) in ((-2.0, 0.95), (-1.95, 4.45), (2.0, 4.4), (1.5, 0.5)):
        F.flowers(b, x, y, 0.0, n=5, spread=0.3, cols=["#f4f1e4", "#f2a0bd", "#f4f1e4", "#b08ae6"])
