# The treadwheel crane: two men walking inside its wheels can lift a ton of salt cod; the children are let in to tread it on feast days.
# A round stone base, an eight-sided boarded wheelhouse that tapers to a shingled cap, both great wheels showing through its open
# sides, and a long braced jib slung from a king post through the roof. Weathered boards, rubble, shingle; accent red.
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "The Old Crane", "kind": "crane", "lot": (6.0, 6.0)}

CX, CY = -0.3, 3.3
BZ = 1.5                    # top of the stone base
HH = 4.4                    # wheelhouse height
BOARD = "#b9a48e"
TIP = (2.5, -0.85, 12.6)    # the jib's head
TAIL = (-1.45, 5.3, 6.3)
PALE = paint("#eadcbc")      # the scrubbed wood of the wheels


def wheel(b, x, r=1.4, wd=0.66):
    """One treadwheel, its axle along x, centred on the current frame."""
    with b.at(x, 0, 0, ry=90):
        with b.detail(1):
            for zz in (-wd / 2, wd / 2):
                with b.at(z=zz):
                    b.revolve([(r - 0.22, -0.05), (r, -0.05), (r, 0.05), (r - 0.22, 0.05), (r - 0.22, -0.05)], "planks", col=PALE, seg=12)
                    for k in range(2):
                        with b.at(rz=90 * k + 20):
                            b.beam((0, -r + 0.1, 0), (0, r - 0.1, 0), w=0.13, mat="planks", col=PALE, caps=False)
            for k in range(12):
                with b.at(rz=30 * k + 15):
                    b.box(0.36, 0.05, wd, "planks", col=shade(PALE, 0.86), y=-(r - 0.16), z=-wd / 2, bottom=True)
        with b.detail(2):
            for zz in (-wd / 2 - 0.06, wd / 2 + 0.06):
                with b.at(z=zz):
                    b.revolve([(0.0, -0.03), (0.24, -0.03), (0.24, 0.03), (0.0, 0.03)], "paint", col="red", seg=8)


def build(b):
    # ------------------------------------------------------------------ the stone base
    base = b.round(2.5, BZ, r1=2.42, mat="masonry", col="warm", x=CX, y=CY, seg=20)
    P.door(base, 320, w=0.8, h=1.25, arch=0.4, col="red", frame="stone", z=0.05, knob=False)
    with b.at(CX, CY, 0):
        b.revolve([(2.56, -3.0), (2.56, 0.02)], "masonry", col=shade("warm", 0.85), seg=20, lod=0)
        b.revolve([(2.4, BZ - 0.18), (2.52, BZ - 0.18), (2.52, BZ), (2.3, BZ)], "ashlar", col="stone", seg=20, lod=0)
        b.disc(2.32, "flagstone", col="sand", seg=20, z=BZ, lod=0)
    P.stones(base, n=16, z0=0.1, z1=1.2)
    # ------------------------------------------------------------------ the wheelhouse
    faces = PC.poly_tower(b, 8, 2.32, HH, taper=0.88, mat="planks", col=BOARD, x=CX, y=CY, z=BZ, depth=0.14, foot=False)
    for k in (2, 6):
        faces[k].opening(faces[k].w / 2, 0.4, 1.5, 3.1, arch=0.75, pane=None, depth=0.14)
    P.door(faces[4], faces[4].w / 2, w=0.8, h=1.8, z=0.04, col="red", frame="timber")
    P.window(faces[0], faces[0].w / 2, 2.3, w=0.6, h=0.8, lintel=None)
    P.window(faces[3], faces[3].w / 2, 1.9, w=0.55, h=0.75, lintel=None)
    P.window(faces[7], faces[7].w / 2, 1.9, w=0.55, h=0.75, lintel=None)
    H.life_ring(faces[1], faces[1].w / 2, 1.7)
    P.lantern(faces[0], faces[0].w / 2 + 0.55, 1.5)
    ap0, ap1 = 2.32 * math.cos(math.pi / 8), 2.32 * 0.88 * math.cos(math.pi / 8)
    with b.at(CX, CY, BZ):
        n = 8      # the dark inside, a floor, and oak posts down the corners
        ring = lambda r, z: [(r * math.sin(rad(45 * i + 22.5)), -r * math.cos(rad(45 * i + 22.5)), z) for i in range(n)]
        A, B = ring(2.15, 0.02), ring(2.15 * 0.88, HH)
        for i in range(n):
            j = (i + 1) % n
            if i in (1, 5):      # (behind the two open sides)
                continue
            b.quad(A[j], A[i], B[i], B[j], "planks", col=shade("#3d342d", 0.8 + 0.12 * (i % 2)), lod=0)
        b.face(A, "planks", col="#6a5d50", lod=0)
        with b.detail(1):
            C0, C1 = ring(2.34, 0.0), ring(2.34 * 0.88, HH)
            for i in range(n):
                b.beam(C0[i], C1[i], w=0.17, mat="timber", col="darkoak", caps=False)
        # the two wheels on their axle, and the windlass between them
        with b.at(0, 0.1, 2.12):
            wheel(b, -0.86)
            wheel(b, 0.86)
            with b.detail(1):
                b.tube((-1.6, 0, 0), (1.6, 0, 0), r=0.13, mat="timber", col="darkoak", n=7)
                b.tube((-0.36, 0, 0), (0.36, 0, 0), r=0.3, mat="cloth", col=H.ROPE, n=8, caps=True)
        # ------------------------------------------------------------------ the cap, the king post and the jib
        with b.at(0, 0, HH, rz=22.5):
            b.cone_roof(2.32 * 0.88, 2.5, mat="shingle", seg=8, smooth=False, eave=0.42, flare=0.5, course=0.4, finial=False)
        KZ = 10.9 - BZ
        b.beam((0, 0, HH - 0.6), (0, 0, KZ), w=0.3, mat="timber", col="darkoak", lod=0)
        tip = (TIP[0] - CX, TIP[1] - CY, TIP[2] - BZ)
        tail = (TAIL[0] - CX, TAIL[1] - CY, TAIL[2] - BZ)
        b.beam(tail, tip, w=0.28, h=0.34, mat="timber", col="darkoak", lod=0)
        mid = vlerp(tail, tip, 0.62)
        with b.detail(1):
            b.beam((0.05, -0.05, KZ - 0.25), vlerp(tail, tip, 0.97), w=0.09, mat="timber", col="darkoak")
            b.beam((0.05, -0.05, KZ - 0.25), vlerp(tail, tip, 0.04), w=0.09, mat="timber", col="darkoak")
            b.beam((1.5, -1.3, HH + 0.4), mid, w=0.16, mat="timber", col="darkoak")
            b.beam((-0.1, 0.1, KZ - 0.5), (-0.3, 0.3, HH + 1.5), w=0.03, mat="cloth", col=H.ROPE, caps=False)
            b.box(0.36, 0.36, 0.14, "metal", col="iron", z=KZ, bottom=True)
        P.flag(b, 0, 0, KZ + 0.1, pole=1.5, w=1.2, h=0.5, col="stripe_red", pole_col="darkoak")
        H.gull(b, *vlerp(tail, tip, 0.8)[:2], vlerp(tail, tip, 0.8)[2] + 0.2, rz=120)
    # ------------------------------------------------------------------ the fall: sheave, rope, hook and a cask in its sling
    with b.at(*TIP):
        with b.detail(1):
            with b.at(0, 0, -0.32, ry=90, rz=0):
                b.revolve([(0.0, -0.05), (0.2, -0.05), (0.2, 0.05), (0.0, 0.05)], "timber", col="greyoak", seg=8)
            b.beam((0, 0, -0.5), (0, 0, -8.3), w=0.04, mat="cloth", col=H.ROPE, caps=False)
            b.beam((0, 0, -8.3), (0, 0, -8.5), w=0.05, mat="metal", col="iron", caps=False)
            with b.at(0, 0, -9.0, rx=90, rz=25):
                b.revolve([(0.26, -0.42), (0.35, -0.14), (0.35, 0.14), (0.26, 0.42)], "planks", col="#c9a57a", seg=10, close_top=True, close_bottom=True)
        with b.detail(2):
            for d in (-0.3, 0.3):
                b.beam((0, 0, -8.5), (d * math.cos(rad(25)), d * math.sin(rad(25)), -8.72), w=0.025, mat="cloth", col=H.ROPE, caps=False)
    # ------------------------------------------------------------------ round its foot
    with b.at(CX - 1.2, CY + 2.35, 0, rz=205):
        P.ladder(b, BZ + 0.1, w=0.5)
    P.barrel(b, 2.3, 0.4, r=0.3, h=0.82)
    P.barrel(b, 1.75, -0.2, r=0.28, h=0.76, col="#b99870")
    P.crate(b, 2.5, 1.35, s=0.65, rz=14)
    P.sack(b, -2.55, 0.5, r=0.3)
    P.sack(b, -2.2, 0.15, r=0.27, col="#cdbb92")
    H.rope_coil(b, -1.3, -0.5, r=0.32)
    H.bollard(b, 0.4, -0.9)
