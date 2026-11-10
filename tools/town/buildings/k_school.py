# The schoolhouse: one tall light room where the quarter's children learn their letters between errands; the bell in the cupola calls them in, and the flags of the little yard are chalked for hopscotch.
# A gable-fronted hall with tall many-paned windows, a timber porch on the street gable, a bell cupola astride the ridge, the teacher's room leaning on the right side and a small walled yard with a tree in front of it.
# Butter lime-wash on a rubble footing with pale quoins, slate roofs, a white boarded cupola; accent red.
from kit import *
import parts as P
import parts_c as PC
import parts_h as PH
import parts_k as K

META = {"name": "The Schoolhouse", "kind": "school", "lot": (8.0, 9.0)}

HX, HW = -1.0, 5.2                    # the schoolroom: x -3.6 .. 1.6
Y0, Y1, H = 1.5, 8.5, 3.9
PF = 0.34                             # the porch floor


def build(b):
    b.footprint(-3.9, 0.0, 3.88, 8.8, 7.0)
    # ------------------------------------------------------------------ the schoolroom
    room = b.body(HW, Y1 - Y0, H, mat="plaster", col="butter", x=HX, y=(Y0 + Y1) / 2)
    P.plinth(room, h=0.9, out=0.08)
    P.quoins(room, z0=0.9, col="sand")
    P.door(room.front, HW / 2, w=1.2, h=2.15, z=PF, arch=0.5, col="red", double=True)
    for u in (0.72, HW - 0.72):
        P.window(room.front, u, 1.3, w=0.6, h=1.5, bars=(1, 3))
    for u in (1.3, 3.5, 5.7):
        P.window(room.left, u, 1.2, w=1.0, h=2.0, bars=(2, 3))
    P.window(room.right, 0.9, 1.2, w=1.0, h=2.0, bars=(2, 3))
    for u in (1.4, 3.8):
        P.window(room.back, u, 1.2, w=1.0, h=2.0, bars=(2, 3))
    P.ivy(room.back, 0.35, 0.5, w=1.2, h=3.2, n=8)
    rise = room.gable(ridge="y", pitch=48, mat="slate", sag=0.06, eave=0.24, verge=0.3)
    PH.cuttable(room.front, room.back)
    P.window(room.front, HW / 2, H + 0.3, w=1.0, h=1.5, arch=0.5, bars=(1, 2))
    PC.oculus(room.back, HW / 2, H + 1.2, r=0.42)
    K.sign(room.front, HW - 0.42, 3.35, emblem="book", col="red")
    K.cupola(b, HX, 3.0, H + rise, w=1.25, base=0.7, stage=1.2, roof_h=1.55, drop=0.85, roof="shingle", col="ivory")
    P.chimney(b, HX + 1.25, 7.5, 4.9, 3.0, mat="brick", pots=1)

    # ------------------------------------------------------------------ the porch
    b.box(2.7, Y0 - 0.1, PF + 3.0, "ashlar", col="sand", x=HX, y=(Y0 + 0.1) / 2, z=-3.0, cap="flagstone", capcol="sand")
    with b.at(HX, -0.46, 0):
        P.stairs(b, w=1.7, rise=0.17, run=0.28, n=2)
    for sx in (-1, 1):
        b.beam((HX + sx * 1.15, 0.28, PF), (HX + sx * 1.15, 0.28, 2.6), w=0.18, lod=0)
        b.beam((HX + sx * 1.15, 0.12, 2.52), (HX + sx * 1.15, Y0, 2.52), w=0.16, h=0.18, lod=0)
        with b.detail(1):
            b.beam((HX + sx * 1.15, Y0 - 0.1, PF), (HX + sx * 1.15, Y0 - 0.1, 2.6), w=0.16)
            b.beam((HX + sx * 1.15, 0.28, 1.95), (HX + sx * 0.6, 0.28, 2.46), w=0.1, caps=False)
            b.beam((HX + sx * 1.15, 0.36, 1.95), (HX + sx * 1.15, 0.9, 2.46), w=0.1, caps=False)
        P.railing(b, [(HX + sx * 1.15, 0.42, PF), (HX + sx * 1.15, Y0 - 0.14, PF)], h=0.85, style="solid", col="red", mat="planks", post=0.09)
    b.beam((HX - 1.3, 0.28, 2.52), (HX + 1.3, 0.28, 2.52), w=0.16, h=0.18, lod=0)
    prise = b.gable_roof(2.6, Y0 - 0.1, pitch=45, mat="slate", x=HX, y=(Y0 + 0.1) / 2, z=2.6, ridge="y", eave=0.2, verge=0.2)
    with b.detail(1):
        b.beam((HX, 0.28, 2.6), (HX, 0.28, 2.6 + prise - 0.2), w=0.13)
        for sx in (-1, 1):
            b.beam((HX + sx * 1.2, 0.28, 2.56), (HX, 0.28, 2.5 + prise - 0.1), w=0.11, h=0.14, up=(0, 1, 0), caps=False)
    P.lantern_at(b, HX + 0.95, Y0 - 0.03, 2.05)

    # ------------------------------------------------------------------ the teacher's room
    lt = PH.leanto(b, HX + HW / 2, 5.6, 4.6, 2.0, 2.3, rz=90, pitch=24, mat="plaster", col="butter", roof="slate", plinth=0.9, eave=0.22)
    P.door(lt.left, 1.0, w=0.85, h=1.95, z=0.18, col="red", steps=1)
    P.window(lt.front, 1.3, 1.05, w=0.8, h=0.95)
    P.window(lt.front, 3.3, 1.05, w=0.8, h=0.95)

    # ------------------------------------------------------------------ the yard: a tree, a bench, hopscotch
    fl = K.yard(b, HX + HW / 2, 0.1, 3.85, 3.3, mat="flagstone")
    K.gate(b, (1.78, 0.25), (2.9, 0.25), col="red", h=1.05)
    K.low_wall(b, (3.07, 0.25), (3.84, 0.25), h=1.0, t=0.28)
    K.low_wall(b, (3.7, 0.25), (3.7, 3.3), h=1.0, t=0.28)
    P.tree(b, 2.85, 1.8, fl, h=3.7, crown=0.8)
    P.bench(b, 3.1, 3.05, fl, w=0.95)
    with b.detail(2):
        for i, n in enumerate((1, 1, 2, 1, 2, 1)):
            for k in range(n):
                cx, cy = 2.12 + (k - (n - 1) / 2) * 0.36, 0.75 + 0.36 * i
                b.quad((cx - 0.16, cy - 0.16, fl + 0.006), (cx + 0.16, cy - 0.16, fl + 0.006), (cx + 0.16, cy + 0.16, fl + 0.006), (cx - 0.16, cy + 0.16, fl + 0.006), "paint", col="!#f4e9c8")
    PC.cat(b, 3.7, 2.3, 1.1, rz=280)
