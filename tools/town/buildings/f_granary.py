# The Mushroom Granary: the seed corn of three farms sits up here on nine stone mushrooms where no rat can climb; the cat is kept on anyway.
# Massing: a square timber-framed box with brick filling, lifted a yard off the ground on nine staddle stones, under a steep half-hipped tile
#          roof; a flight of stone steps stops a stride short of the door.
# Materials: oak frame and soft red brick nogging, terracotta tiles, grey staddle stones; accent brown.
from kit import *
import parts as P
import parts_h as PH
import parts_l as PL
import parts_m as PM
import parts_f as F

META = {"name": "The Mushroom Granary", "kind": "barn", "lot": (5.0, 6.0)}

W, D, H = 4.0, 4.2, 2.5
CX, CY = 0.0, 3.2
FLOOR = 1.06


def build(b):
    # ---- nine staddle stones and the sill frame
    for x in (-1.75, 0.0, 1.75):
        for y in (CY - 1.85, CY, CY + 1.85):
            F.staddle(b, x, y, 0.0, h=0.8, r=0.4)
        b.beam((x, CY - D / 2 - 0.08, 0.92), (x, CY + D / 2 + 0.08, 0.92), w=0.24, h=0.24, mat="timber", col="darkoak", lod=0, up=(0, 0, 1))
    for y in (CY - D / 2 + 0.1, CY + D / 2 - 0.1):
        b.beam((-W / 2 - 0.08, y, 0.94), (W / 2 + 0.08, y, 0.94), w=0.24, h=0.24, mat="timber", col="darkoak", lod=0, up=(0, 0, 1))
    b.footprint(-W / 2, CY - D / 2, W / 2, CY + D / 2, FLOOR)

    # ---- the box: oak frame, brick nogging, half-hipped roof
    bd = b.body(W, D, H, mat="brick", col="#ffe9d8", x=CX, y=CY, z=FLOOR, floor="planks", foot=False)
    P.door(bd.front, W / 2, w=0.9, h=1.9, col="brown", frame="timber", z=0.05, lamp=True)
    PH.hatch(bd.front, W / 2, H + 0.35, w=0.62, h=0.72, col="brown")
    PH.louvre(bd.left, D / 2, 1.2, w=0.6, h=0.7, col="brown")
    PH.louvre(bd.right, D / 2, 1.2, w=0.6, h=0.7, col="brown")
    PH.louvre(bd.back, W / 2, 1.2, w=0.6, h=0.7, col="brown")
    P.timber_frame(bd.front, posts=[0.0, 0.75, 1.4, 2.6, 3.25, W], rails=[0.0, H], braces=[(0.0, H, 0.75, 0.0), (W, H, 3.25, 0.0)])
    P.timber_frame(bd.back, posts=[0.0, 0.85, 1.55, 2.45, 3.15, W], rails=[0.0, H], braces=[(0.0, H, 0.85, 0.0), (W, H, 3.15, 0.0)])
    for wl in (bd.left, bd.right):
        P.timber_frame(wl, posts=[0.0, 0.9, 1.65, 2.55, 3.3, D], rails=[0.0, H], braces=[(0.0, H, 0.9, 0.0), (D, H, 3.3, 0.0)])
    rise = PL.halfhip_roof(bd, pitch=52, hip=0.45, ends="fb", mat="tiles", eave=0.3, verge=0.28)
    PM.weathercock(b, CX, CY, FLOOR + H + rise - 0.1, h=1.2, shape="lark", size=0.9)
    PM.pigeon(b, 0.5, CY + 0.6, FLOOR + H + rise + 0.02, rz=60)
    PM.pigeon(b, -0.7, CY - 0.3, FLOOR + H + rise + 0.02, rz=200)

    # ---- the steps, a stride short of the door (so nothing can climb in)
    with b.at(0.0, -0.45, 0.0):
        P.stairs(b, w=1.15, rise=0.2, run=0.26, n=5, mat="ashlar", col="grey", lod=0)
        b.box(1.15, 1.3, 1.5, "masonry", col="warm", y=0.65, z=-1.5, top=False)
    with b.detail(2):
        b.quad((0.2, CY - D / 2 - 0.015, FLOOR + 0.06), (0.38, CY - D / 2 - 0.015, FLOOR + 0.06), (0.38, CY - D / 2 - 0.015, FLOOR + 0.24), (0.2, CY - D / 2 - 0.015, FLOOR + 0.24), "paint", col="black")
    P.sack(b, -0.3, 0.55, 0.8, r=0.26)
    P.sack(b, 0.25, 0.3, 0.6, r=0.25)
    F.cat(b, 0.36, 0.7, 1.0, rz=330, col="#d98a3d")
    F.ladder_to(b, (W / 2 + 0.22, CY + 1.2, 0.0), (W / 2 + 0.05, CY + 1.0, FLOOR + 1.95), w=0.4)
    P.barrel(b, -1.75, 0.75, 0.0, r=0.27, h=0.75)
    F.tool(b, -2.12, CY - 0.4, 0.0, kind="spade", rz=-90, lean=0.02, h=1.1)
    for (x, y) in ((-2.05, 0.6), (2.05, 0.7), (-2.1, 5.55), (2.05, 5.5), (1.3, 0.35)):
        F.flowers(b, x, y, 0.0, n=5, spread=0.28)
