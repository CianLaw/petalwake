# The Huer's Lookout: the tallest net loft on the quay; from the crow's nest on its ridge the huer watches for the shoals and hoists the ball.
# A slim stone store, two flush tarred storeys and a jettied grey-boarded lookout room under a shingled gable; on trestles
# astride the ridge a railed plank deck with a signal mast. Black and salt-grey boards, grey rubble, shingle; accent mustard.
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "The Huer's Lookout", "kind": "netloft", "lot": (4.8, 6.5), "lean": (-0.004, 0.003)}

PITCH = 50.0
RISE = 1.95 * math.tan(rad(PITCH))
RZ = 9.5 + RISE             # the ridge
DZ = 12.25                  # the crow's nest deck


def build(b):
    # ------------------------------------------------------------------ the stack of storeys
    g = b.body(3.5, 5.0, 2.6, mat="masonry", col="grey", y=2.7)                                           # y 0.2 .. 5.2
    mid = b.body(3.5, 5.0, 4.6, mat="planks", col=H.TAR, y=2.7, z=2.6, depth=0.14)
    top = b.body(3.9, 5.4, 2.3, mat="planks", col=H.TAR_OLD, y=2.7, z=7.2, floor="planks", depth=0.14)    # y 0.0 .. 5.4
    H.cuttable(top.front, top.back)
    P.band(mid, 0.0, h=0.14, out=0.05, mat="timber", col="darkoak")
    with b.detail(1):
        for i in range(6):
            x = -1.6 + 3.2 * i / 5
            if abs(x + 0.45) > 0.3:
                b.beam((x, 0.25, 7.1), (x, -0.05, 7.1), w=0.13, h=0.17, mat="timber", col="darkoak")

    # ------------------------------------------------------------------ front: doors one above another under the jetty hoist
    P.door(g.front, 1.3, w=1.3, h=2.05, col="mustard", frame="timber", double=True, z=0.08, lamp=True)
    P.window(g.front, 2.8, 1.2, w=0.55, h=0.7, frame="ivory", lintel="timber")
    H.loading_door(mid.front, 1.3, 0.3, w=1.2, h=1.7, col="mustard")
    H.loading_door(mid.front, 1.3, 2.6, w=1.2, h=1.65, col="mustard")
    P.window(mid.front, 2.8, 0.8, w=0.55, h=0.85, frame="ivory", lintel=None)
    P.window(mid.front, 2.8, 3.05, w=0.55, h=0.85, frame="ivory", lintel=None)
    H.hoist(b, -0.45, 0.2, 7.02, out=1.25, load="crate", drop=2.3, brace=False, back=0.6)
    P.window(top.front, 0.85, 0.85, w=0.62, h=0.95, frame="ivory", lintel=None, shutters="mustard")
    P.window(top.front, 1.95, 0.85, w=0.62, h=0.95, frame="ivory", lintel=None)
    P.window(top.front, 3.05, 0.85, w=0.62, h=0.95, frame="ivory", lintel=None, shutters="mustard")
    H.louvre(top.front, 1.95, 2.85, w=0.6, h=0.75)
    H.floats(mid.front, 0.35, 4.3, n=4)
    H.life_ring(mid.front, 2.8, 2.25)
    # ------------------------------------------------------------------ sides and back
    H.hatch(g.right, 1.5, 1.2, w=0.7, h=0.7, col="mustard")
    P.window(g.right, 3.7, 1.1, w=0.65, h=0.8, frame="ivory", lintel="timber")
    H.hatch(g.left, 2.4, 1.2, w=0.7, h=0.7, col="mustard")
    P.door(g.back, 1.2, w=0.9, h=1.9, col="mustard", frame="timber", z=0.08)
    P.plinth(g, h=0.3, col="grey")
    P.window(mid.right, 1.4, 0.8, w=0.6, h=0.85, frame="ivory", lintel=None)
    P.window(mid.right, 3.7, 3.05, w=0.6, h=0.85, frame="ivory", lintel=None)
    P.window(mid.left, 1.3, 3.05, w=0.6, h=0.85, frame="ivory", lintel=None)
    H.hatch(mid.left, 3.6, 0.9, w=0.6, h=0.7, col="mustard")
    P.window(mid.back, 1.75, 0.8, w=0.65, h=0.9, frame="ivory", lintel=None)
    H.loading_door(mid.back, 1.75, 2.6, w=1.1, h=1.55, col="mustard", bar=False)
    P.window(top.right, 2.7, 0.85, w=0.62, h=0.95, frame="ivory", lintel=None, shutters="mustard")
    P.window(top.left, 1.7, 0.85, w=0.62, h=0.95, frame="ivory", lintel=None)
    P.window(top.back, 1.95, 0.85, w=0.62, h=0.95, frame="ivory", lintel=None)
    H.louvre(top.back, 1.95, 2.85, w=0.6, h=0.75)
    for wl in mid.walls:
        H.battens(wl, col=H.TAR, rails=(2.3,))
    for wl in (top.left, top.right):
        H.battens(wl, col=H.TAR_OLD, rails=(0.07,))
    for wl in (top.front, top.back):
        H.battens(wl, col=H.TAR_OLD, z1=2.3 + RISE, rails=(0.07, 2.3))
    top.gable(ridge="y", pitch=PITCH, mat="shingle", eave=0.2, verge=0.3, course=0.4)

    # ------------------------------------------------------------------ the crow's nest on the ridge: where the rider lands
    zr = RZ - 1.05 * math.tan(rad(PITCH))          # the roof under the posts
    ys = (0.45, 1.8, 3.15)
    for sx in (-1, 1):
        for y in ys:
            b.beam((sx * 1.05, y, zr - 0.15), (sx * 1.05, y, DZ + 1.1), w=0.14, mat="timber", col="darkoak", lod=0)
    b.box(2.36, 3.0, 0.1, "planks", col="greyoak", y=1.8, z=DZ - 0.1, bottom=True, lod=0)
    with b.detail(1):
        for sx in (-1, 1):
            b.beam((sx * 1.05, 0.25, DZ - 0.2), (sx * 1.05, 3.35, DZ - 0.2), w=0.12, h=0.18, mat="timber", col="darkoak")
            for ya, yb in zip(ys, ys[1:]):
                b.beam((sx * 1.05, ya, zr + 0.1), (sx * 1.05, yb, DZ - 0.32), w=0.09, mat="timber", col="darkoak", caps=False)
                b.beam((sx * 1.05, yb, zr + 0.1), (sx * 1.05, ya, DZ - 0.32), w=0.09, mat="timber", col="darkoak", caps=False)
        for y in ys:
            b.beam((-1.2, y, DZ - 0.36), (1.2, y, DZ - 0.36), w=0.12, h=0.16, mat="timber", col="darkoak")
            for sx in (-1, 1):
                b.beam((sx * 1.05, y, zr + 0.25), (sx * 0.12, y, DZ - 0.42), w=0.09, mat="timber", col="darkoak", caps=False)
    P.railing(b, [(-1.05, 0.45, DZ), (-1.05, 3.15, DZ), (1.05, 3.15, DZ), (1.05, 0.45, DZ)], h=1.0, style="cross", col="darkoak", posts_at=1.35)
    with b.at(0, 1.45, DZ):
        P.landing_mark(b, 0.9)
    b.pad(0, 1.45, DZ, radius=0.95, face=0, name="The Huer's Lookout")
    PC.hatch(b, 0.52, 2.8, DZ, w=0.6, d=0.6, open_deg=62)
    with b.detail(2):      # the ladder under the hatch, down to the roof
        zl = RZ - 0.52 * math.tan(rad(PITCH))
        for dy in (-0.2, 0.2):
            b.beam((0.52, 2.8 + dy, zl - 0.1), (0.52, 2.8 + dy, DZ - 0.1), w=0.05, mat="timber", col="greyoak", caps=False)
        for k in range(3):
            zz = zl + 0.2 + 0.3 * k
            b.beam((0.52, 2.6, zz), (0.52, 3.0, zz), w=0.035, mat="timber", col="greyoak", caps=False)
    # the signal mast: lantern, pennant and the huer's ball
    MXm, MYm = -0.72, 3.15
    P.flag(b, MXm, MYm, DZ, pole=3.5, w=1.3, h=0.5, col="stripe_yellow", pole_col="greyoak")
    with b.detail(1):
        b.beam((MXm - 0.1, MYm, DZ + 2.5), (MXm + 1.0, MYm, DZ + 2.5), w=0.05, mat="planks", col="greyoak")
        b.beam((MXm + 0.9, MYm, DZ + 2.5), (MXm + 0.9, MYm, DZ + 1.95), w=0.02, mat="cloth", col=H.ROPE, caps=False)
        b.blob(0.2, mat="thatch", col="#b5653f", x=MXm + 0.9, y=MYm, z=DZ + 1.75, seg=6, rings=3, rough=0.05)
    P.lantern_at(b, MXm, MYm - 0.02, DZ + 1.75, arm=0.3)
    H.gull(b, 1.05, 3.15, DZ + 1.12, rz=140)

    # ------------------------------------------------------------------ the quay at its foot
    H.net_drape(b, (1.86, 0.7, 2.5), (1.86, 3.5, 2.5), drop=1.7, sag=0.1, col=H.NET_BROWN)
    with b.at(1.2, 0.2, 0):
        P.ladder(b, 2.75)
    H.pots(b, -1.45, -0.55, rz=85, n=3)
    P.barrel(b, 1.95, -0.55, r=0.28, h=0.75)
    H.rope_coil(b, 0.85, -0.55, r=0.3)
    H.buoy(b, 0.0, -0.9, col="!#d9a431", stripe="!#2c2a2a", s=0.9)
