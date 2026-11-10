# The seamen's chapel of St Brine: every boat lost from Larkhaven has a candle here, and the bell is rung in fog to bring the rest home.
# A lime-washed buttressed nave with coloured lancets, a lower chancel and vestry, a timber porch on the quay; astride the west end
# of the ridge an open bell turret under a slender shingled spire, and a little stone bell-cote over the chancel arch. White, slate, silver shingle; accent blue.
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "Seamen's Chapel", "kind": "chapel", "lot": (8.0, 12.0)}

NY0, NW, ND, NH = 1.3, 5.8, 7.6, 4.0           # nave: front wall y, width, depth, wall height
PITCH = 52.0
BLUE, AMBER = "#5f9fe0", "#e0a94a"


def build(b):
    # ------------------------------------------------------------------ nave
    nave = b.body(NW, ND, NH, mat="plaster", col="white", y=NY0 + ND / 2)
    H.cuttable(nave.front, nave.back)
    rise = NW / 2 * math.tan(rad(PITCH))
    P.door(nave.front, NW / 2, w=1.2, h=2.35, arch=0.6, col="blue", frame="stone", z=0.12, double=True)
    P.window(nave.front, NW / 2, 4.35, w=0.75, h=1.5, arch=0.37, glass=BLUE, bars=(1, 2))
    for i, u in enumerate((1.45, 3.95, 6.3)):
        P.window(nave.right, u, 1.35, w=0.62, h=1.95, arch=0.31, glass=(BLUE, AMBER, BLUE)[i], bars=(1, 3))
        P.window(nave.left, ND - u, 1.35, w=0.62, h=1.95, arch=0.31, glass=(AMBER, BLUE, AMBER)[i], bars=(1, 3))
    P.plinth(nave, h=0.55, col="grey")
    P.exposed(nave.right, "base", n=10, col="grey")
    P.exposed(nave.left, "both", n=10, col="grey")
    P.exposed(nave.front, "corners", n=8, col="grey")
    for y in (NY0 + 0.25, NY0 + 2.7, NY0 + 5.1, NY0 + ND - 0.3):
        for sx, rz in ((1, 90), (-1, 270)):
            with b.at(sx * NW / 2, y, 0, rz=rz):
                PC.buttress(b, w=0.6, d=0.85, h=3.3, mat="masonry", col="grey")
    nave.gable(ridge="y", pitch=PITCH, mat="slate", eave=0.3, verge=0.25, sag=0.1)
    RZ = NH + rise
    # ------------------------------------------------------------------ chancel and vestry
    ch = b.body(4.2, 2.6, 3.2, mat="plaster", col="white", y=NY0 + ND + 1.3)
    P.window(ch.right, 1.3, 1.3, w=0.5, h=1.5, arch=0.25, glass=AMBER)
    P.window(ch.left, 1.3, 1.3, w=0.5, h=1.5, arch=0.25, glass=BLUE)
    for u, hh, gl in ((1.35, 1.5, BLUE), (2.1, 1.9, AMBER), (2.85, 1.5, BLUE)):
        P.window(ch.back, u, 1.2, w=0.44, h=hh, arch=0.22, glass=gl, sill=False)
    P.plinth(ch, h=0.55, col="grey")
    ch.gable(ridge="y", pitch=PITCH, mat="slate", eave=0.28, verge=0.22)
    vs = H.leanto(b, 2.1, NY0 + ND + 1.35, 2.2, 1.3, 2.0, rz=90, pitch=30, mat="plaster", col="white", roof="slate", plinth=0.45, plinth_col="grey")
    P.door(vs.left, 0.7, w=0.7, h=1.75, col="blue", frame="timber", z=0.08)
    P.window(vs.front, 1.1, 1.0, w=0.6, h=0.7, lintel="timber")
    P.chimney(b, 2.5, NY0 + ND + 2.2, 2.0, 2.6, w=0.5, d=0.5, mat="masonry", col="grey", pots=1)
    with b.at(0, NY0 + ND - 0.2, RZ - 0.25):      # the stone bell-cote over the chancel arch
        with b.detail(1):
            for sx in (-1, 1):
                b.box(0.24, 0.4, 0.95, "ashlar", col="stone", x=sx * 0.42)
            b.box(1.2, 0.46, 0.16, "ashlar", col="stone", z=0.95, bottom=True)
            b.box(0.9, 0.42, 0.3, "ashlar", col="stone", z=1.11, taper=1.0, tx=0.25)
        H.small_bell(b, 0, 0, 0.9, r=0.2, lod=1)
    # ------------------------------------------------------------------ the bell turret and its slender spire
    TY, TZ, TH = NY0 + 1.15, RZ - 1.25, 3.5
    tw = b.body(1.6, 1.6, TH, mat="shingle", col="#e9e4da", x=0, y=TY, z=TZ, foot=False, depth=0.14)
    for wl in tw.walls:
        wl.opening(0.8, 1.75, 0.8, 1.3, arch=0.4, pane=None, depth=0.14)
    with b.detail(1):
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.beam((sx * 0.8, TY + sy * 0.8, TZ + 0.9), (sx * 0.8, TY + sy * 0.8, TZ + TH), w=0.16, mat="timber", col="darkoak")
        b.box(1.5, 1.5, 0.06, "planks", col="#3a332d", x=0, y=TY, z=TZ + 1.7)
    P.bell(b, 0, TY, TZ + 3.0, r=0.3, beam=1.5)
    SZ = TZ + TH
    with b.at(0, TY, SZ, rz=45):
        b.cone_roof(1.13, 6.0, mat="shingle", seg=4, smooth=False, course=0.42, finial=False, section=[(1.52, -0.22), (0.92, 0.5), (0.5, 2.5), (0.0, 6.0)])
    PC.vane(b, 0, TY, SZ + 5.9, h=1.5, shape="cock")
    # ------------------------------------------------------------------ the porch on the quay
    with b.at(0, 0.0, 0):
        for sx in (-1, 1):
            b.box(0.3, 1.3, 0.95, "masonry", col="grey", x=sx * 1.15, y=0.65, lod=0)
            for yy in (0.12, 1.15):
                b.beam((sx * 1.15, yy, 0.95), (sx * 1.15, yy, 2.5), w=0.16, mat="timber", col="darkoak", lod=0)
            with b.detail(1):
                b.beam((sx * 1.15, 0.0, 2.5), (sx * 1.15, 1.3, 2.5), w=0.14, h=0.16, mat="timber", col="darkoak")
        b.gable_roof(2.6, 1.3, pitch=48, mat="slate", x=0, y=0.65, z=2.56, ridge="y", eave=0.16, verge=0.12, course=0.34, thick=0.1)
        with b.detail(1):
            b.beam((-1.2, 0.08, 2.52), (1.2, 0.08, 2.52), w=0.12, h=0.16, mat="timber", col="darkoak")
            b.beam((0, 0.08, 2.52), (0, 0.08, 3.85), w=0.12, mat="timber", col="darkoak")
        b.box(2.5, 1.3, 0.12, "flagstone", col="sand", y=0.65, lod=0)
    H.anchor(b, 0.0, 0.02, 2.75, rz=0, h=1.0, lean=0.0)
    P.lantern_at(b, 1.15, 0.05, 2.05, arm=0.2)
    # ------------------------------------------------------------------ the garth
    with b.detail(1):
        for (x, y, rz_, hh) in ((2.9, 0.45, 8, 0.85), (3.4, 0.75, -6, 0.7)):
            with b.at(x, y, 0, rz=rz_, rx=-7):
                b.stone(0.5, 0.14, hh, mat="ashlar", col="grey", lod=1, ch=0.3, jitter=0.1)
        with b.at(-3.2, 0.6, 0):      # a mariner's cross
            b.box(0.5, 0.5, 0.3, "ashlar", col="stone")
            b.beam((0, 0, 0.3), (0, 0, 1.7), w=0.16, mat="ashlar", col="stone")
            b.beam((-0.38, 0, 1.3), (0.38, 0, 1.3), w=0.14, mat="ashlar", col="stone")
    PC.flowers(b, 2.1, 0.75, w=1.1, d=0.5, n=6)
    PC.flowers(b, -2.3, 0.75, w=1.0, d=0.5, n=5)
    P.tree(b, -2.75, 10.7, h=4.0, crown=1.0)
    H.gull(b, 0.0, NY0 + 4.6, RZ - 0.06, rz=100)
