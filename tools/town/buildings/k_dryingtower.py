# The dyers' drying tower: new-dyed lengths are carried up and hung from its gallery to dry in the sea wind, and the dyers read the weather from the wind deck on top, which is where the rider lands (and the hatch is her way down).
# A battered rubble base with a timber stair wrapped round two sides, a louvred timber stage, a cloth-hung gallery, an open braced stage with cloth drying inside it, and a jettied deck under a small bell-cast roof on four posts.
# Warm rubble, dark oak frame with grey louvres, weathered shingles; accent navy (indigo) and every dye in the vat.
from kit import *
import parts as P
import parts_c as PC
import parts_k as K

META = {"name": "The Dyers' Drying Tower", "kind": "tower", "lot": (6.0, 6.0)}

Z1, Z2, Z3, ZP = 4.6, 8.6, 12.6, 15.5        # top of the stone, the gallery, the wind deck, the roof plates
OUT = 2.62                                    # half-width of the two decks


def half(z):
    """Half-width of the timber frame at height z (it tapers from 1.9 to 1.7)."""
    return 1.9 - 0.2 * (z - Z1) / (Z3 - Z1)


def deck(b, z, drop=1.15, t=0.14):
    """A jettied square deck: boards, edge beams, joist ends and struts down to the frame."""
    hin = half(z)
    b.box(2 * OUT, 2 * OUT, t, "planks", col="greyoak", z=z - t, bottom=True, lod=0)
    with b.detail(1):
        for k in range(4):
            with b.at(rz=90 * k):
                b.beam((-OUT, -OUT + 0.05, z - t / 2), (OUT, -OUT + 0.05, z - t / 2), w=0.1, h=t + 0.08, col="darkoak", up=(0, 0, 1))
                for xx in (-hin * 0.42, hin * 0.42):
                    b.beam((xx, -hin, z - t - 0.08), (xx, -OUT + 0.02, z - t - 0.08), w=0.12, h=0.15, col="darkoak")
                for xx in (-hin + 0.02, hin - 0.02):
                    b.beam((xx, -half(z - drop) - 0.05, z - drop), (xx, -OUT + 0.22, z - t - 0.1), w=0.12, col="darkoak", up=(1, 0, 0))


def build(b):
    with b.at(0.0, 3.0):
        tower(b)


def tower(b):
    b.footprint(-2.9, -2.9, 2.9, 2.9, Z3)
    # ------------------------------------------------------------------ the stone base
    base = PC.tbody(b, 4.6, 4.6, Z1, inset=0.3, mat="masonry", col="warm", y=0.0, depth=0.34)
    PC.plinth(base, h=0.6, out=0.1, doors=[("front", 1.9, 1.0)])
    PC.tquoins(base, z0=0.6, col="sand")
    PC.tband(base, Z1 - 0.2, h=0.2, out=0.09, col="sand")
    P.door(base.front, 1.9, w=1.0, h=2.15, z=0.34, arch=0.5, col="navy", steps=2, lamp=True)
    P.window(base.front, 3.4, 2.9, w=0.6, h=1.0, arch=0.3, shutters="navy")
    P.window(base.right, 1.5, 1.4, w=0.6, h=1.0, arch=0.3)
    P.window(base.right, 3.1, 2.9, w=0.6, h=1.0, arch=0.3, shutters="navy", box=True)
    P.window(base.back, 0.95, 2.9, w=0.6, h=1.0, arch=0.3)
    P.window(base.left, 0.9, 2.9, w=0.6, h=1.0, arch=0.3)
    for wl in base.walls:
        P.stones(wl, n=9, z0=0.7, z1=4.2, u0=0.5, u1=4.1)
    P.ivy(base.right, 3.9, 0.3, w=1.5, h=3.6, n=9)

    # ------------------------------------------------------------------ the louvred stage
    core = PC.tbody(b, 3.8, 3.8, Z2 - Z1, inset=0.1, mat="planks", col="#6e5a4a", y=0.0, z=Z1, depth=0.16, foot=False)
    P.door(core.left, 3.05, w=0.8, h=1.9, z=0.04, col="navy", frame="timber")
    P.window(core.front, 1.0, 0.75, w=0.7, h=0.95, shutters="navy", lintel="timber", sill=False, frame="ivory")
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.beam((sx * 1.9, sy * 1.9, Z1 - 0.1), (sx * 1.7, sy * 1.7, Z3), w=0.26, lod=0, up=(0, 1, 0))
    with b.detail(1):
        for k in range(4):
            with b.at(rz=90 * k):
                for zz in (Z1 + 0.1, 6.6, Z2 - 0.24):
                    hh = half(zz) + 0.03
                    b.beam((-hh, -hh, zz), (hh, -hh, zz), w=0.14, h=0.18, up=(0, 0, 1), caps=False)
                b.beam((0, -half(Z1) - 0.03, Z1), (0, -half(Z2) - 0.03, Z2), w=0.16, h=0.14, up=(0, 1, 0), caps=False)
                for (z0, z1) in ((Z1 + 0.22, 6.5), (6.72, Z2 - 0.34)):
                    for sx in (-1, 1):
                        if z0 < 6.0 and ((k == 0 and sx < 0) or (k == 3 and sx > 0)):
                            continue                    # the shuttered window, and the door from the stair
                        K.slats(b, 1.5, z1 - z0, x=sx * 0.92, y=-half((z0 + z1) / 2) - 0.07, z=z0, pitch=0.26, board=0.2)

    # ------------------------------------------------------------------ the gallery, hung with cloth
    deck(b, Z2)
    r = OUT - 0.08
    ring = [(-r, -r, Z2), (r, -r, Z2), (r, r, Z2), (-r, r, Z2)]
    P.railing(b, ring, h=1.0, style="cross", closed=True)
    for i in range(4):
        p0, p1 = ring[i], ring[(i + 1) % 4]
        K.draped(b, (p0[0], p0[1], Z2 + 1.02), (p1[0], p1[1], Z2 + 1.02), n=3, drop=(2.3, 3.2), width=(0.8, 1.05), lod=0)

    # ------------------------------------------------------------------ the open stage: braces, cloth drying inside
    with b.detail(1):
        for k in range(4):
            with b.at(rz=90 * k):
                hh = half(10.6) + 0.02
                b.beam((-hh, -hh, 10.6), (hh, -hh, 10.6), w=0.14, h=0.16, up=(0, 0, 1), caps=False)
        for yy in (-0.6, 0.55):
            b.beam((-1.62, yy, 12.2), (1.62, yy, 12.2), w=0.07, caps=False)
    for k in range(4):                                  # the great cross-braces read from afar: always drawn
        with b.at(rz=90 * k):
            b.beam((-half(8.8) + 0.1, -half(8.8), 8.8), (half(12.3) - 0.1, -half(12.3), 12.3), w=0.13, h=0.1, up=(0, 1, 0), caps=False, lod=0)
            b.beam((half(8.8) - 0.1, -half(8.8) - 0.02, 8.8), (-half(12.3) + 0.1, -half(12.3) - 0.02, 12.3), w=0.13, h=0.1, up=(0, 1, 0), caps=False, lod=0)
    inner = ["#2f4f8f", "#e0b23a", "#b8433a", "#5a9a68"]
    for i, (xx, yy) in enumerate(((-0.75, -0.6), (0.6, -0.6), (-0.5, 0.55), (0.25, 0.55))):
        K.cloth(b, 0.85, 2.5 + 0.3 * (i % 2), inner[i], x=xx, y=yy, z=12.16, rows=4, sway=0.45, hem=shade(inner[i], 0.8), lod=0)
    with b.at(0.95, 1.5, Z2):
        P.ladder(b, 5.0)

    # ------------------------------------------------------------------ the wind deck: where the rider lands
    deck(b, Z3)
    r = OUT - 0.08
    P.railing(b, [(-1.75, -r, Z3), (-r, -r, Z3), (-r, r, Z3), (r, r, Z3), (r, -r, Z3), (1.75, -r, Z3)], h=1.0, style="balusters")
    K.draped(b, (r, -r, Z3 + 1.02), (r, r, Z3 + 1.02), n=2, drop=(1.5, 2.1), width=(0.8, 1.0), lod=0)
    K.draped(b, (r, r, Z3 + 1.02), (-r, r, Z3 + 1.02), n=3, drop=(1.5, 2.2), width=(0.8, 1.0), lod=0)
    K.draped(b, (-r, r, Z3 + 1.02), (-r, -r, Z3 + 1.02), n=2, drop=(1.5, 2.1), width=(0.8, 1.0), lod=0)
    PC.hatch(b, 0.95, 1.2, Z3, w=0.8, d=0.8)
    with b.at(0.0, -1.15, Z3):
        P.landing_mark(b, 0.95)
    b.pad(0.0, -1.15, Z3, radius=1.0, face=0, name="Wind deck")
    with b.detail(2):
        b.blob(0.3, 0.26, 0.2, mat="cloth", col="#c8587c", x=-1.1, y=1.25, z=Z3 + 0.14, seg=6, rings=3, rough=0.2)      # a heap of wet cloth
        K.bucket(b, -0.5, 1.4, Z3)

    # ------------------------------------------------------------------ four posts and the little roof
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.beam((sx * 1.7, sy * 1.7, Z3), (sx * 1.7, sy * 1.7, ZP), w=0.2, lod=0)
    with b.detail(1):
        for k in range(4):
            with b.at(rz=90 * k):
                b.beam((-1.95, -1.7, ZP - 0.09), (1.95, -1.7, ZP - 0.09), w=0.16, h=0.18, up=(0, 0, 1))
                for sx in (-1, 1):
                    b.beam((sx * 1.7, -1.7, ZP - 0.85), (sx * 1.02, -1.7, ZP - 0.16), w=0.1, caps=False)
    rise = K.open_roof(b, 3.6, 3.6, section=[(0.0, 0.0), (0.55, 0.2), (1.8, 1.85)], z=ZP, eave=0.5, mat="shingle", flyunder="#9a978f")
    P.weathervane(b, 0, 0, ZP + rise - 0.05, h=1.3)
    with b.detail(2):
        b.beam((0, 0, ZP + rise - 0.3), (0, 0, ZP + 0.5), w=0.02, mat="metal", col="iron", caps=False)
        b.box(0.2, 0.2, 0.26, "glow", col="#ffd88a", z=ZP + 0.24, bottom=True)
        b.box(0.25, 0.25, 0.03, "metal", col="iron", z=ZP + 0.5)
        b.box(0.22, 0.22, 0.025, "metal", col="iron", z=ZP + 0.215, bottom=True)
    b.lamp(0, 0, ZP + 0.37)

    # ------------------------------------------------------------------ the stair round the back and the left side
    with b.at(0.62, 2.52, 0, rz=90):
        P.stairs(b, w=0.56, rise=0.23, run=0.27, n=10, solid=False)
        P.railing(b, [(0.25, 0.0, 0.1), (0.25, 2.7, 2.4)], h=0.9, style="plain", posts_at=1.4)
    with b.at(-2.52, 2.08, 2.3, rz=180):
        P.stairs(b, w=0.56, rise=0.23, run=0.27, n=10, solid=False)
        P.railing(b, [(0.25, 0.0, 0.1), (0.25, 2.7, 2.4)], h=0.9, style="plain", posts_at=1.4)
    with b.detail(1):
        b.box(0.78, 0.78, 0.08, "planks", col="greyoak", x=-2.41, y=2.41, z=2.22, bottom=True)
        b.box(0.9, 1.0, 0.08, "planks", col="greyoak", x=-2.35, y=-1.12, z=Z1 - 0.08, bottom=True)
        b.beam((-2.72, 2.72, 0), (-2.72, 2.72, 2.22), w=0.12)
        b.beam((-2.72, -1.55, 0), (-2.72, -1.55, Z1 - 0.08), w=0.12)
        b.beam((-2.2, -0.7, 3.7), (-2.72, -0.7, Z1 - 0.1), w=0.1)
        b.box(0.72, 0.5, 1.7, "ashlar", col="stone", x=0.78, y=2.52, z=-1.5)
    P.railing(b, [(-2.05, 2.75, 2.3), (-2.75, 2.75, 2.3), (-2.75, 2.05, 2.3)], h=0.9, style="plain")
    P.railing(b, [(-2.75, -0.64, Z1), (-2.75, -1.58, Z1), (-1.95, -1.58, Z1)], h=0.9, style="plain")

    # ------------------------------------------------------------------ the hoist and the dye-yard at the door
    K.hoist(b, 1.72, -1.72, 11.2, out=1.45, face=0, rope=9.2, load="bale")
    K.tub(b, 1.1, -2.74, 0, r=0.4, h=0.5, fill="#2f4f8f")
    K.tub(b, 1.95, -2.66, 0, r=0.34, h=0.46, fill="#b8433a")
    K.bolt(b, -1.7, -2.72, 0.0, col="#e0b23a", rz=8)
    K.bolt(b, -1.45, -2.66, 0.0, col="#5a9a68", rz=-6)
    K.bolt(b, -1.58, -2.7, 0.2, col="#b8433a", rz=3)
