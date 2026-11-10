# The smithy: the forge burns in the open under the deep front of the roof, where the street can watch; the smith lives behind it, and the great stack over the hearth is the tallest thing in the lane.
# A low rubble house whose slate roof runs on forward over an open bay on oak posts, an open king-post truss to the street, the brick hearth and hood on the left with a massive shouldered chimney breaking through the slope.
# Warm rubble, sooty slate, dark oak, red brick; accent orange.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_k as K

META = {"name": "The Smithy", "kind": "workshop", "lot": (7.5, 9.0)}

W, Y0, Y1, H, PITCH = 6.5, 3.4, 8.45, 2.9, 40.0
FL = 0.08                                   # the flagged floor of the forge


def roof_z(x):
    """Underside of the roof at x."""
    return H + (W / 2 - abs(x)) * math.tan(rad(PITCH)) - 0.16


def build(b):
    b.footprint(-3.6, 0.0, 3.6, 8.8, 5.7)
    # ------------------------------------------------------------------ the house behind
    bd = b.body(W, Y1 - Y0, H, mat="masonry", col="warm", y=(Y0 + Y1) / 2)
    P.plinth(bd, h=0.55)
    for wl in (bd.left, bd.right, bd.back):
        P.stones(wl, n=7, z0=0.6, z1=2.7)
    rise = b.gable_roof(W, Y1 - 0.25, pitch=PITCH, mat="slate", x=0, y=(Y1 + 0.25) / 2, z=H, ridge="y", eave=0.3, verge=0.28, sag=0.1)
    bd.front.gable = rise - 0.03
    bd.back.gable = rise - 0.03
    PH.cuttable(bd.front, bd.back)
    P.door(bd.front, 4.0, w=1.3, h=2.1, z=FL, col="orange", double=True, frame="timber")
    K.tool_rack(bd.front, 2.55, 1.95, w=1.1)
    K.horseshoes(bd.front, 5.6, 2.05, n=5)
    for u in (1.3, 3.7):
        P.window(bd.right, u, 1.05, w=0.8, h=1.1)
        P.window(bd.left, u, 1.05, w=0.8, h=1.1)
    P.door(bd.back, 1.6, w=0.9, h=1.95, z=0.17, col="orange", steps=1)
    P.window(bd.back, 4.6, 1.05, w=0.9, h=1.1, shutters="orange", box=True)
    P.exposed(bd.back, "corners", mat="masonry")
    P.ivy(bd.right, 4.6, 0.3, w=1.4, h=2.6, n=7)
    P.chimney(b, 2.0, 7.5, 3.5, 2.7, mat="masonry", col="warm", pots=1)

    # ------------------------------------------------------------------ the open forge bay: posts, plates and the truss
    K.yard(b, -3.37, 0.2, 3.37, Y0, mat="flagstone", h=FL)
    for sx in (-1, 1):
        for yy in (0.45, 1.95):
            b.beam((sx * 3.05, yy, 0), (sx * 3.05, yy, H), w=0.26, lod=0)
        b.beam((sx * 3.05, 0.3, H - 0.11), (sx * 3.05, Y0, H - 0.11), w=0.2, h=0.22, lod=0)
    b.beam((-3.25, 0.45, H - 0.13), (3.25, 0.45, H - 0.13), w=0.22, h=0.26, lod=0)
    b.beam((0, 0.45, H), (0, 0.45, H + rise - 0.3), w=0.2, lod=0)
    with b.detail(1):
        for sx in (-1, 1):
            b.beam((sx * 3.1, 0.45, H - 0.14), (0, 0.45, H + rise - 0.44), w=0.16, h=0.2, up=(0, 1, 0), caps=False)
            b.beam((sx * 0.1, 0.45, H + 0.2), (sx * 1.62, 0.45, roof_z(1.62) - 0.12), w=0.13, caps=False)
            b.beam((sx * 3.05, 0.45, H - 1.0), (sx * 2.25, 0.45, H - 0.2), w=0.12, caps=False)
            b.beam((sx * 3.05, 0.5, H - 0.95), (sx * 3.05, 1.2, H - 0.2), w=0.12, caps=False)
            b.beam((sx * 3.05, 1.95, H - 0.95), (sx * 3.05, 2.65, H - 0.2), w=0.12, caps=False)
    K.low_wall(b, (3.07, 0.62), (3.07, Y0), h=0.85, t=0.28)
    K.low_wall(b, (-3.07, 0.62), (-3.07, 1.95), h=0.85, t=0.28)
    K.hanging_sign(b, 1.85, 0.3, H - 0.26, emblem="horseshoe", col="black")

    # ------------------------------------------------------------------ hearth, hood and the great chimney
    K.hearth(b, -2.25, 2.75, FL, w=1.5, d=1.2, h=0.85, hood_h=1.45, hood_top=(0.95, 0.75))
    K.great_chimney(b, -2.25, 2.95, 3.25, h=5.4, w=1.2, d=0.95, shoulder=1.55, neck=0.66, pots=2)
    K.bellows(b, -2.3, 1.15, FL, rz=90)
    K.coal_heap(b, -1.05, 3.0, FL, r=0.42, h=0.3)

    # ------------------------------------------------------------------ the smith's floor
    K.anvil(b, 0.15, 1.75, FL, rz=20)
    K.trough(b, 2.15, 3.05, FL, w=1.3)
    K.bucket(b, 1.15, 3.0, FL)
    K.grindstone(b, 2.35, 1.2, FL, rz=90)
    with b.at(2.69, 2.35, FL + 0.56, rz=90):
        with b.at(rx=12):
            K.cart_wheel(b, r=0.55)
    with b.detail(2):
        for i in range(4):                      # bar iron stood in the corner
            b.beam((-2.85 + 0.07 * i, 2.02, FL), (-2.95 + 0.05 * i, 2.1, 2.0 + 0.1 * i), w=0.03, mat="metal", col="iron")
    PC.cat(b, 3.07, 1.5, 0.95, rz=250)
