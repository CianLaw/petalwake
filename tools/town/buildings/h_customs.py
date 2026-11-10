# The customs house: every cask landed at Larkhaven is counted here; the collector watches for sails from the walk on the roof.
# A tall dressed-stone block of four bays with a columned doorcase off-centre, a hipped slate roof cut flat for a railed widow's walk
# between two stacks, and a lean-to seizure store with a cart arch on its side. Pale ashlar, slate, white rail; accent blue.
from kit import *
import parts as P
import parts_c as PC
import parts_h as H

META = {"name": "Larkhaven Customs House", "kind": "civic", "lot": (11.0, 9.0)}

MX, W, D, HT = -1.15, 7.8, 7.6, 7.5        # the main block: centre x, width, depth, wall height
RUN, RISE = 1.9, 1.72                     # the roof slope up to the walk
DZ = HT + RISE                            # the walk
UD = 2.95                                 # the door's bay on the front wall


def doorcase(s, u, z, w, h):
    """Two stone columns, an entablature and a little pediment with a brass seal."""
    b = s.b

    def deco():
        with s.onu(u, z):
            hw, zt, ph, yo = (w + 1.3) / 2, h + 0.5, 0.62, -0.5
            with b.detail(1):
                for sgn in (-1, 1):
                    x = sgn * (w / 2 + 0.3)
                    b.box(0.36, 0.32, 0.5, "ashlar", col="stone", x=x, y=-0.22)
                    b.tube((x, -0.22, 0.5), (x, -0.22, h + 0.08), r=0.13, r1=0.11, mat="ashlar", col="stone", n=8)
                    b.box(0.34, 0.34, 0.12, "ashlar", col="stone", x=x, y=-0.22, z=h + 0.08, bottom=True)
                b.box(w + 1.2, 0.5, 0.3, "ashlar", col="stone", y=-0.22, z=h + 0.2, bottom=True)
                b.tri((-hw, yo, zt), (hw, yo, zt), (0, yo, zt + ph), "ashlar", col="stone")
                b.quad((-hw, yo, zt), (0, yo, zt + ph), (0, 0, zt + ph), (-hw, 0, zt), "slate")
                b.quad((0, yo, zt + ph), (hw, yo, zt), (hw, 0, zt), (0, 0, zt + ph), "slate")
                b.quad((-hw, 0, zt), (hw, 0, zt), (hw, yo, zt), (-hw, yo, zt), "ashlar", col=shade("stone", 0.8))
            with b.detail(2):
                with b.at(0, yo - 0.01, zt + 0.22, rx=90):
                    b.disc(0.15, "metal", col="brass", seg=8)

    s.add(deco)


def build(b):
    # ------------------------------------------------------------------ the main block
    m = b.body(W, D, HT, mat="ashlar", col="sand", x=MX)
    P.plinth(m, h=0.7, out=0.1, mat="masonry", col="grey")
    P.quoins(m, z0=0.7, col="stone")
    P.band(m, 4.28, h=0.2, out=0.08)
    P.band(m, HT - 0.24, h=0.24, out=0.2)
    gf = dict(w=1.0, h=2.3, arch=0.5, frame="ivory", bars=(1, 3))
    ff = dict(w=0.95, h=1.75, frame="ivory", bars=(1, 2))
    # front: window, door, window, window
    for u in (1.05, 4.85, 6.75):
        P.window(m.front, u, 1.6, **gf)
    P.door(m.front, UD, w=1.25, h=2.5, col="blue", frame=None, steps=4, z=0.72, double=True)
    doorcase(m.front, UD, 0.72, 1.25, 2.5)
    P.lantern(m.front, UD - 1.45, 2.5)
    P.lantern(m.front, UD + 1.45, 2.5)
    for u in (1.05, 4.85, 6.75):
        P.window(m.front, u, 5.0, **ff)
    P.window(m.front, UD, 4.84, w=1.1, h=2.05, frame="ivory", bars=(1, 3), sill=False)
    P.balcony(m.front, UD, 4.8, w=2.2, out=0.85, rail="iron", floor="ashlar", floor_col="stone", brackets=False, thick=0.16)

    def consoles():
        with m.front.on(UD, 4.8):
            with b.detail(1):
                for sgn in (-1, 1):
                    b.box(0.2, 0.6, 0.34, "ashlar", col="stone", x=sgn * 0.85, y=-0.3, z=-0.5, taper=1.0, ty=0.45, bottom=True)
    m.front.add(consoles)
    # sides and back
    for u in (2.0, 5.6):
        P.window(m.left, u, 1.6, **gf)
        P.window(m.left, u, 5.0, **ff)
    for u in (2.1, 5.5):
        P.window(m.right, u, 5.0, **ff)
    P.door(m.back, 3.9, w=1.0, h=2.2, col="blue", frame="stone", steps=3, z=0.55)
    for u in (1.3, 6.5):
        P.window(m.back, u, 1.6, **gf)
    for u in (1.3, 3.9, 6.5):
        P.window(m.back, u, 5.0, **ff)
    P.exposed(m.left, "base", n=8, mat="masonry", col="grey")

    # ------------------------------------------------------------------ the roof and the widow's walk: where the rider lands
    SEC = [(0.0, 0.0), (RUN, RISE)]
    m.hip(section=SEC, mat="slate", eave=0.36, course=0.4, top="planks")
    H.hip_rolls(b, W, D, SEC, z=HT, x=MX, y=D / 2, mat="slate", col="#9aa2a8", eave=0.36, ridge=False)
    dw, dd = W - 2 * RUN, D - 2 * RUN
    with b.at(MX, D / 2, DZ):
        b.box(dw + 0.16, dd + 0.16, 0.1, "planks", col="greyoak", z=-0.02, lod=0, bottom=True)
        hw, hd = dw / 2 - 0.04, dd / 2 - 0.04
        gap = 0.95
        rail = dict(h=0.98, style="balusters", col="ivory", mat="planks", posts_at=1.3)
        P.railing(b, [(-gap, -hd, 0.08), (-hw, -hd, 0.08), (-hw, hd, 0.08), (hw, hd, 0.08), (hw, -hd, 0.08), (gap, -hd, 0.08)], **rail)
        with b.detail(1):
            for (px, py) in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd), (-gap, -hd), (gap, -hd)):
                b.beam((px, py, 0.08), (px, py, 1.22), w=0.14, mat="planks", col="ivory")
                b.blob(0.11, mat="paint", col="ivory", x=px, y=py, z=1.33, seg=6, rings=3, rough=0.0)
        with b.at(0, -0.42, 0.08):
            P.landing_mark(b, 1.15)
        b.pad(0, -0.42, 0.08, radius=1.2, face=0, name="Customs House walk")
        # the hatch she goes down by, propped open, and the collector's glass
        with b.at(hw - 0.48, hd - 0.48, 0.08):
            with b.detail(1):
                b.box(0.8, 0.8, 0.22, "planks", col="darkoak", cap="planks", capcol="#3a332d")
                with b.at(0, 0.4, 0.22, rx=62):
                    b.box(0.8, 0.8, 0.05, "planks", col="greyoak", y=-0.4, bottom=True)
            with b.detail(2):
                b.beam((0.3, -0.3, 0.2), (0.3, -0.05, 0.62), w=0.03, mat="metal", col="iron", caps=False)
        with b.at(-hw + 0.5, hd - 0.5, 0.08):
            with b.detail(2):
                for k in range(3):
                    with b.at(rz=120 * k + 20):
                        b.beam((0, -0.26, 0), (0, 0, 1.1), w=0.035, mat="timber", col="darkoak", caps=False)
                with b.at(rz=-20):
                    b.tube((0, 0.34, 1.08), (0, -0.5, 1.3), r=0.05, r1=0.075, mat="metal", col="brass", n=7, caps=True)
        P.flag(b, -hw, hd, 1.2, pole=3.4, w=1.6, h=0.95, col="stripe_blue", kind="banner", pole_col="ivory")
    P.chimney(b, MX - W / 2 + 0.95, D / 2 + 0.3, HT - 0.2, 4.0, w=0.75, d=1.3, mat="ashlar", col="sand", pots=3)
    P.chimney(b, MX + W / 2 - 0.95, D / 2 - 0.5, HT - 0.2, 4.3, w=0.75, d=1.3, mat="ashlar", col="sand", pots=2)
    P.dormer(b, MX + 0.2, D - 1.15, HT + 0.5, w=0.95, h=0.85, depth=1.2, face=180, roof="slate", col="sand", wall="ashlar", frame="ivory", pitch=38)
    H.gull(b, MX + W / 2 - 0.95, D / 2 - 0.5 + 0.3, HT + 4.52, rz=250)

    # ------------------------------------------------------------------ the seizure store: a lean-to with a cart arch
    wing = H.leanto(b, MX + W / 2, 3.7, 5.4, 2.5, 3.6, rz=90, pitch=25, mat="ashlar", col="sand", roof="slate", eave=0.28, verge=0.2,
                    plinth=0.7, plinth_col="grey")
    P.door(wing.left, 1.32, w=1.5, h=2.8, arch=0.75, col="blue", frame="stone", double=True, z=0.06)
    P.lantern(wing.left, 0.3, 2.3)
    for u in (1.5, 3.9):
        P.window(wing.front, u, 1.9, w=0.8, h=0.95, frame="ivory", bars=(2, 1))
    P.door(wing.right, 1.2, w=0.85, h=1.95, col="blue", frame="timber", z=0.1)
    P.ivy(wing.front, 4.9, 0.3, w=1.4, h=3.0, n=7)

    # ------------------------------------------------------------------ the quay in front
    fx = MX - W / 2 + UD
    for sgn in (-1, 1):
        P.planter(b, fx + sgn * 1.75, -0.55, w=0.5, d=0.5, h=0.45, bush=True)
    P.bench(b, MX - W / 2 + 5.8, -0.5, w=1.5, rz=180)
    wx = MX + W / 2 + 1.3
    P.crate(b, wx + 0.75, 0.45, s=0.7, rz=8)
    P.crate(b, wx + 0.8, 0.5, z=0.7, s=0.5, rz=-14)
    P.barrel(b, wx - 0.75, 0.55, r=0.32, h=0.85)
    P.barrel(b, wx - 0.2, 0.05, r=0.3, h=0.8)
    P.sack(b, wx + 0.1, 0.7)
    H.bollard(b, MX - W / 2 + 0.5, -0.9)
    H.bollard(b, 4.6, -0.9)
    PC.lamp_post(b, 5.0, 0.35, h=2.9)
    P.sign(m.front, 0.25, 3.6, emblem="key", col="mustard", board="navy")
