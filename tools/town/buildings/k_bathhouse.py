# The bathhouse: the quarter washes off its soot, dye and clay here; bathers undress in the cool hall under the big dome and sweat in the two little hot rooms behind, whose vents steam above the lane all evening.
# A low lime-washed hall with a flat parapeted roof and a saucer dome pierced with glass eyes, an arcaded porch with a tiled floor and roof in front, two small domes over the hot rooms behind, the boiler house leaning on one side.
# White and sky-blue lime-wash, glazed tile bands, terracotta tiles, brass finials; accent mint.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_m as PM
import parts_k as K

META = {"name": "The Bathhouse", "kind": "bathhouse", "lot": (8.0, 9.0)}

HX, HW = -0.7, 6.0                    # the hall: x -3.7 .. 2.3, y 2.0 .. 7.0
Y0, Y1, H = 2.0, 7.0, 3.7
PF = 0.3                              # the porch floor


def build(b):
    b.footprint(-3.8, 0.1, 3.8, 8.65, 5.9)
    # ------------------------------------------------------------------ the hall and its dome
    hall = b.body(HW, Y1 - Y0, H, mat="plaster", col="white", x=HX, y=(Y0 + Y1) / 2)
    P.plinth(hall, h=0.6, col="grey")
    P.door(hall.front, 3.0, w=1.3, h=2.3, z=PF, arch=0.55, col="mint", double=True, lamp=True)
    for u in (0.95, 5.05):
        P.window(hall.front, u, 1.5, w=0.6, h=1.1, arch=0.3, glass="#9fd0d8", lintel=None)
    K.frieze(hall.front, 2.95, h=0.3)
    for wl in (hall.left, hall.right):
        K.frieze(wl, 2.95, h=0.3)
        for u in (1.3, 3.7):
            P.window(wl, u, 1.6, w=0.6, h=1.1, arch=0.3, glass="#9fd0d8")
    P.exposed(hall.left, "base", n=8)
    b.box(HW, Y1 - Y0, 0.1, "flagstone", col="sand", x=HX, y=(Y0 + Y1) / 2, z=H - 0.1)
    for (px, py, pw, pd) in ((HX, Y0 + 0.14, HW + 0.1, 0.28), (HX, Y1 - 0.14, HW + 0.1, 0.28), (HX - HW / 2 + 0.14, (Y0 + Y1) / 2, 0.28, Y1 - Y0), (HX + HW / 2 - 0.14, (Y0 + Y1) / 2, 0.28, Y1 - Y0)):
        b.box(pw, pd, 0.42, "plaster", col="white", x=px, y=py, z=H, cap="ashlar", capcol="sand")
    K.dome(b, 2.05, 1.5, x=HX, y=(Y0 + Y1) / 2, z=H, drum=0.75, eyes=10, col="white", seg=18, steps=6)
    K.steam_vent(b, HX - 2.3, Y0 + 0.9, H, h=1.0)
    K.steam_vent(b, HX + 2.35, Y1 - 0.9, H, h=0.8, smoke=False)
    with b.detail(1):
        for xx in (HX + 1.0, HX + 2.5):
            b.beam((xx, Y0 + 0.6, H), (xx, Y0 + 0.6, H + 1.9), w=0.07)
    P.laundry(b, (HX + 1.0, Y0 + 0.6, H + 1.8), (HX + 2.5, Y0 + 0.6, H + 1.8), n=4, sag=0.15, cols=["linen", "#bfe3d0", "linen", "#bcd4ea"])

    # ------------------------------------------------------------------ the hot rooms behind
    hot = b.body(HW, 1.6, 2.9, mat="plaster", col="sky", x=HX, y=Y1 + 0.8)
    hot.front.done = True                      # (it stands against the hall)
    P.plinth(hot, h=0.6, col="grey")
    P.window(hot.back, 1.5, 1.5, w=0.5, h=0.9, arch=0.25, glass="#9fd0d8")
    P.window(hot.back, 4.5, 1.5, w=0.5, h=0.9, arch=0.25, glass="#9fd0d8")
    P.door(hot.back, 3.0, w=0.8, h=1.9, z=0.1, col="mint")
    P.window(hot.left, 0.9, 1.5, w=0.5, h=0.9, arch=0.25, glass="#9fd0d8")
    b.box(HW + 0.12, 1.72, 0.12, "plaster", col="white", x=HX, y=Y1 + 0.8, z=2.9, cap="flagstone", capcol="sand")
    for xx in (HX - 1.55, HX + 1.55):
        K.dome(b, 0.74, 0.6, x=xx, y=Y1 + 0.8, z=3.02, drum=0.3, eyes=5, eye_r=0.08, col="white", seg=12, steps=4)
    K.steam_vent(b, HX, Y1 + 0.82, 3.02, h=0.95, strength=0.8)

    # ------------------------------------------------------------------ the boiler house
    lt = PH.leanto(b, HX + HW / 2, 5.0, 4.0, 1.25, 2.1, rz=90, pitch=24, mat="masonry", col="warm", roof="tiles", plinth=0.5)
    P.door(lt.left, 0.62, w=0.7, h=1.75, z=0.1, col="mint", frame="timber")
    P.window(lt.front, 2.0, 1.0, w=0.7, h=0.8)
    P.chimney(b, HX + HW / 2 + 0.62, 6.4, 1.9, 4.6, w=0.7, d=0.6, mat="brick", pots=1)
    K.firewood(b, HX + HW / 2 + 0.03, 2.5, 0, w=0.9, h=1.1, rz=90)

    # ------------------------------------------------------------------ the tiled porch
    x0, x1 = -3.3, 1.9
    b.box(x1 - x0 + 0.3, Y0 - 0.2, PF + 3.0, "ashlar", col="sand", x=(x0 + x1) / 2, y=(Y0 + 0.2) / 2, z=-3.0, cap="flagstone", capcol="sand")
    K.chequer(b, x0 + 0.1, 0.55, x1 - 0.1, Y0 - 0.02, z=PF + 0.01, n=10)
    K.arcade(b, x1 - x0, 2.75, n=3, t=0.3, pier=0.42, top=0.45, x=x0, y=0.25, z=PF + 0.01, mat="plaster", col="white")
    K.arcade(b, Y0 - 0.55, 2.75, n=1, t=0.3, pier=0.3, top=0.45, x=x0, y=Y0, z=PF + 0.01, face=270, mat="plaster", col="white")
    K.arcade(b, Y0 - 0.55, 2.75, n=1, t=0.3, pier=0.3, top=0.45, x=x1, y=0.55, z=PF + 0.01, face=90, mat="plaster", col="white")
    PM.lean_to(b, x1 - x0 + 0.1, Y0 - 0.25, pitch=17, x=(x0 + x1) / 2, y=Y0, z=PF + 2.75, face=0, mat="tiles", eave=0.25, verge=0.12)
    with b.at(-0.7, -0.36, 0):
        P.stairs(b, w=1.9, rise=0.15, run=0.28, n=2)
    P.bench(b, -2.3, 1.6, PF, w=1.2, col="#d9d2c7")
    P.planter(b, 1.35, 0.85, PF, bush=True)
    P.planter(b, -2.85, 0.85, PF, bush=True)
    K.hanging_sign(b, -1.5, 0.21, PF + 2.72, emblem="drop", col="teal", w=0.5, h=0.44, drop=0.04)
