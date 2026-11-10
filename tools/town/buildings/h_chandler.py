# The ship chandler's: rope by the fathom, lamp oil, charts and brass; the bow window was built by a shipwright and it shows.
# A stone shop floor with a curved many-paned bow and a painted fascia, a sage-plastered storey above and a gambrel gable to the quay
# with a loft door and hoist; a tarred store leans on the back. Warm stone, sage plaster, terracotta; accent plum.
from kit import *
import parts as P
import parts_h as H

META = {"name": "Larkhaven Ship Chandler", "kind": "shop", "lot": (7.5, 9.0), "lean": (-0.003, 0.002)}

SEC = [(0.0, 0.0), (0.85, 1.75), (3.2, 3.05)]      # the gambrel


def bow_window(b, x0, zs=0.8, zh=2.3, chord=2.6, out=0.85, col="plum", n=6):
    """A curved shop window standing on the wall line y = 0, centred on x0."""
    R = (chord * chord / 4 + out * out) / (2 * out)
    half = math.degrees(math.asin(chord / 2 / R))
    arc = dict(a0=-half, a1=half)
    with b.at(x0, R - out, 0):
        b.revolve([(R, 0.0), (R, zs)], "planks", col=col, seg=n, lod=0, **arc)
        b.revolve([(R - 0.04, zs), (R - 0.04, zh)], "glass", seg=n, lod=0, smooth=False, **arc)
        b.revolve([(R, zh), (R + 0.1, zh), (R + 0.14, zh + 0.34), (R, zh + 0.34)], "planks", col=col, seg=n, lod=0, **arc)
        b.revolve([(R + 0.18, zh + 0.34), (R * 0.45, zh + 0.8)], "metal", col="lead", seg=n, lod=0, **arc)
        with b.detail(1):
            b.revolve([(R, zs - 0.03), (R + 0.1, zs - 0.03), (R + 0.1, zs + 0.06), (R, zs + 0.06)], "planks", col="ivory", seg=n, **arc)
            for i in range(n + 1):
                with b.at(rz=-half + 2 * half * i / n):
                    b.beam((0, -R, zs), (0, -R, zh), w=0.09, h=0.08, mat="planks", col="ivory", caps=False)
        with b.detail(2):
            for zz in (zs + (zh - zs) / 3, zs + 2 * (zh - zs) / 3):
                pts = P.circle(R - 0.02, n, zz, -half, half)
                for a, e in zip(pts, pts[1:]):
                    b.beam(a, e, w=0.04, h=0.045, mat="planks", col="ivory", caps=False)
            for i in range(n):      # a middle glazing bar in every light, and panels on the stall board
                with b.at(rz=-half + 2 * half * (i + 0.5) / n):
                    b.beam((0, -R * math.cos(rad(half / n)) + 0.02, zs), (0, -R * math.cos(rad(half / n)) + 0.02, zh), w=0.035, h=0.04, mat="planks", col="ivory", caps=False)
                    b.box(R * rad(2 * half / n) * 0.62, 0.03, zs * 0.5, "planks", col=shade(col, 0.78), y=-R * math.cos(rad(half / n)) - 0.012, z=zs * 0.24, bottom=True)


def ships_wheel(s, pos, z, r=0.5, col="#b98a5a"):
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            with b.at(0, -0.07, 0, rx=90):
                with b.detail(2):
                    b.revolve([(r - 0.08, -0.03), (r, -0.03), (r, 0.035), (r - 0.08, 0.035), (r - 0.08, -0.03)], "planks", col=col, seg=12)
                    for k in range(8):
                        with b.at(rz=45 * k):
                            b.beam((0, 0.06, 0), (0, r + 0.17, 0), w=0.05, mat="planks", col=col)
                    b.revolve([(0.11, -0.04), (0.11, 0.05), (0.0, 0.07)], "metal", col="brass", seg=8)

    s.add(deco)


def build(b):
    g = b.body(6.4, 7.2, 3.0, mat="masonry", col="warm")
    up = b.body(6.4, 7.2, 2.6, mat="plaster", col="sage", z=3.0)
    H.cuttable(up.front, up.back)
    # ------------------------------------------------------------------ the shopfront
    bow_window(b, -1.25)
    P.door(g.front, 4.95, w=1.0, h=2.1, col="plum", frame="timber", steps=1, z=0.15)
    with b.detail(1):      # the fascia, no words on it
        b.box(6.1, 0.12, 0.34, "planks", col="plum", y=-0.07, z=3.0, bottom=True)
    with b.detail(2):
        b.box(5.7, 0.02, 0.2, "paint", col="ivory", y=-0.14, z=3.07, bottom=True)
        for x in (-2.9, 2.9):
            b.beam((x, -0.02, 2.6), (x, -0.14, 3.0), w=0.08, mat="planks", col="plum")
    P.lantern_at(b, 0.75, -0.05, 2.45, arm=0.4)
    P.lantern_at(b, 2.85, -0.05, 2.45, arm=0.4)
    H.rope_hank(g.front, 5.85, 2.1)
    H.life_ring(g.front, 0.42, 2.45)
    P.window(up.front, 1.6, 0.9, shutters="plum", box=True)
    P.window(up.front, 4.8, 0.9, shutters="plum")
    ships_wheel(up.front, 3.2, 1.5)
    H.loading_door(up.front, 3.2, 2.85, w=0.95, h=1.25, col="plum", bar=False)
    H.hoist(b, 0.0, 0.0, 5.6 + 2.62, out=1.0, load="sack", drop=1.7)
    P.sign(up.front, 6.05, 2.0, emblem="anchor", col="navy", board="ivory")
    # ------------------------------------------------------------------ sides and back
    P.window(g.right, 2.0, 1.1, w=0.9, h=1.2, lintel="timber")
    H.hatch(g.right, 5.3, 1.3, w=0.7, h=0.8, col="plum")
    P.window(up.right, 1.8, 0.9, shutters="plum")
    P.window(up.right, 5.2, 0.9, shutters="plum")
    P.window(g.left, 5.4, 1.1, w=0.9, h=1.2, lintel="timber")
    P.window(up.left, 2.0, 0.9, shutters="plum")
    P.window(up.left, 5.4, 0.9, shutters="plum", box=True)
    P.door(g.back, 5.6, w=0.9, h=1.95, col="plum", frame="timber", z=0.1)
    P.window(up.back, 1.7, 0.9, shutters="plum")
    P.window(up.back, 4.7, 0.9)
    H.louvre(up.back, 3.2, 3.0, w=0.7, h=0.85)
    P.plinth(g, h=0.5)
    P.quoins(g, corners="frbl", z0=0.5, col="sand")
    P.exposed(up.right, "corners", n=8)
    P.ivy(g.right, 6.6, 0.2, w=1.5, h=3.6, n=8)
    lt = H.leanto(b, 0.7, 7.2, 3.6, 1.25, 2.2, rz=180, pitch=26, mat="planks", col=H.TAR_OLD, roof="tiles", plinth=0.35)
    P.door(lt.front, 1.0, w=0.8, h=1.8, col="plum", frame=None, z=0.06)
    H.hatch(lt.front, 2.6, 1.0, w=0.6, h=0.6, col="plum")
    H.battens(lt.front, col=H.TAR_OLD, z0=0.35)
    # ------------------------------------------------------------------ the gambrel roof
    up.gable(ridge="y", section=SEC, mat="tiles", eave=0.3, verge=0.3)
    P.chimney(b, 2.2, 5.4, 6.4, 3.5, w=0.7, d=0.6, mat="brick", pots=2)
    H.gull(b, 0.0, 0.4, 8.75, rz=340)
    # ------------------------------------------------------------------ the stock that lives outside
    H.oars(b, 0.75, -0.02, n=3, L=2.6)
    H.anchor(b, 2.85, -0.04, h=1.45)
    H.rope_coil(b, 2.55, -0.75, r=0.34)
    H.rope_coil(b, 2.5, -0.72, z=0.2, r=0.27, col="#b89a6a")
    H.buoy(b, -3.3, -0.55, col="!#c4473b")
    H.buoy(b, -3.25, -0.98, col="!#3f8f5f", s=0.85, flag="stripe_yellow")
    P.barrel(b, 0.45, -0.8, r=0.28, h=0.75)
    P.crate(b, 3.0, -0.92, s=0.5, rz=12)
    with b.detail(2):
        for i in range(4):
            b.blob(0.1, mat="paint", col=H.GLASSY[i], x=2.9 + 0.2 * (i % 2), y=-1.02 + 0.2 * (i // 2), z=0.56, seg=5, rings=3, rough=0.03)
