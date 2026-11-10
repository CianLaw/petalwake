# The Couriers' Guild: every delivery in Larkhaven starts here. Riders step off onto the broad timber gallery, parcels
# go up and down on the hoist, the carrier pigeons roost under the eaves and the clerk keeps the counting-house below.
# Massing: a stout round rubble tower, battered at the foot; at 13.6 m a great round gallery hung off-centre so that it
# is widest to the square; above it an eight-sided timber-framed lantern storey under a tall bell-cast slate spire.
# Materials: warm rubble, cream plaster in dark oak framing, slate above and tiles on the counting-house; courier red.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Couriers' Guild", "kind": "tower", "lot": (10.0, 10.0), "lean": (0.002, -0.002)}

A = "red"
CX, CY = 0.0, 6.0          # the tower's centre
GY, GR = 5.0, 4.9          # the gallery is a circle about (0, GY): 3 m wide to the front, a ledge behind
ZG = 13.6                  # the gallery floor
PADY = 1.75


def shaft(b):
    t = b.round(3.6, 13.2, mat="masonry", col="warm", seg=20, x=CX, y=CY, profile=[(0.0, 3.6), (3.0, 3.36), (13.2, 3.1)])
    P.round_base(b, 3.6, h=1.0, out=0.3, seg=20, ring=t)
    P.door(t, 20, w=1.0, h=2.2, z=0.34, arch=0.5, col=A, lamp=True)
    Q.steps(t, 20, w=1.5, n=2, z=0.34)
    for a, z, kw in ((62, 3.4, dict(shutters=A)), (318, 3.4, dict(box=True)), (200, 3.4, {}), (105, 6.4, dict(shutters=A, box=True)), (342, 6.4, {}),
                     (248, 6.4, dict(shutters=A)), (28, 9.4, dict(shutters=A)), (150, 9.4, {}), (292, 9.4, dict(box=True))):
        P.window(t, a, z, w=0.62, h=1.2, arch=0.3, bars=(1, 2), lintel=None, **kw)
    P.stones(t, n=30, z0=1.0, z1=12.3)
    P.ivy(t, 255, 0.5, w=2.0, h=4.6, n=8, lod=2)
    Q.bay(t, 222, 6.0, w=1.7, h=1.3, out=0.55, cant=0.32, tuck=0.3, base="corbel", base_mat="ashlar", base_col="stone", roof="slate", col="ivory")
    P.ring_band(b, 3.23, 8.2, h=0.18, out=0.08, seg=20, x=CX, y=CY)
    P.ring_band(b, 3.1, 12.9, h=0.54, out=0.16, seg=20, x=CX, y=CY, lod=0)
    Q.corbel_ring(b, 3.12, 12.9, n=16, out=0.42, h=0.55, x=CX, y=CY, lod=2)


def gallery(b):
    with b.at(0, GY, ZG):
        b.disc(GR, "planks", col="greyoak", seg=24)
        b.disc(GR, "planks", col=shade("darkoak", 0.8), seg=24, z=-0.16, down=True)
        b.revolve([(GR, -0.16), (GR, 0.0)], "planks", col="darkoak", seg=24)
        P.railing(b, P.circle(GR - 0.1, 14, 0.0, 22, 338), h=1.05, style="balusters", col="darkoak")
        for a in (22, 338):                       # gate posts either side of the landing gap, with lanterns
            px, py = (GR - 0.1) * math.sin(rad(a)), -(GR - 0.1) * math.cos(rad(a))
            b.beam((px, py, 0), (px, py, 2.5), w=0.15, mat="timber", col="darkoak", lod=1)
            Q.post_lantern(b, px, py, 2.5, s=0.22)
        for a in (118, 200, 262):
            Q.pigeon(b, (GR - 0.1) * math.sin(rad(a)), -(GR - 0.1) * math.cos(rad(a)), 1.1, rz=a + 20)
        for a, c in ((62, "stripe_yellow"), (298, "stripe_red")):      # pennants on the rail, flying inward over the deck
            with b.at((GR - 0.1) * math.sin(rad(a)), -(GR - 0.1) * math.cos(rad(a)), 0, rz=180 if a < 180 else 0):
                P.flag(b, 0, 0, 0, pole=3.1, w=1.1, h=0.45, col=c)
        with b.at(0, PADY - GY, 0):
            P.landing_mark(b, 1.45)
    b.pad(0, PADY, ZG, radius=1.5, face=0, name="Couriers' Guild gallery")
    # the struts that carry it: long ones under the wide front, short ones behind
    n = 14
    for i in range(n):
        a = rad(360.0 * (i + 0.5) / n)
        px, py = 4.5 * math.sin(a), GY - 4.5 * math.cos(a)
        L = math.hypot(px - CX, py - CY)
        ux, uy = (px - CX) / L, (py - CY) / L
        drop = 0.5 + 0.85 * (L - 3.1)
        b.beam((CX + ux * 3.12, CY + uy * 3.12, ZG - 0.2 - drop), (px, py, ZG - 0.24), w=0.16, mat="timber", col="darkoak", lod=0 if i % 2 == 0 else 1)
        b.beam((CX + ux * 3.0, CY + uy * 3.0, ZG - 0.25), (px + ux * 0.3, py + uy * 0.3, ZG - 0.25), w=0.13, h=0.16, mat="timber", col="darkoak", lod=2)
    # parcels waiting on the gallery (well clear of the landing ring)
    P.crate(b, 3.25, 5.5, ZG, s=0.6)
    P.crate(b, 3.3, 6.25, ZG, s=0.5, rz=20)
    P.crate(b, 3.28, 5.55, ZG + 0.6, s=0.42, rz=35)
    P.sack(b, -3.2, 5.9, ZG)
    P.barrel(b, -3.3, 5.05, ZG, r=0.27, h=0.7)


def lantern_storey(b):
    R8 = 2.6 / math.cos(rad(22.5))
    faces = b.polygon(8, R8, 4.0, mat="plaster", col="cream", x=CX, y=CY, z=ZG, foot=False, rot=0.0)
    fw = faces[0].w
    for k, wl in enumerate(faces):
        P.timber_frame(wl, posts=[0.0, fw], rails=[0.0, 2.72, 4.0], braces="auto", w=0.16)
        if k in (0, 3):
            P.door(wl, fw / 2, w=0.95, h=2.0, z=0.02, col=A, frame="timber")
        else:
            P.window(wl, fw / 2, 1.1, w=0.85, h=1.3, shutters=A, lintel="timber", box=(k in (2, 6)))
        if k in (1, 2, 6, 7):
            Q.pigeonholes(wl, fw / 2, 2.98, cols=3, rows=2, dx=0.46, dz=0.47, birds=1)
    with b.at(CX, CY, ZG + 4.0, rz=22.5):
        b.cone_roof(R8, 6.2, mat="slate", seg=8, smooth=False, eave=0.75, flare=0.5, course=0.55)
    P.dormer(b, CX, CY - 2.15, ZG + 4.8, w=1.0, h=0.95, depth=1.5, roof="slate", col="cream", frame="ivory")
    P.flag(b, CX, CY, ZG + 10.5, pole=2.1, w=1.7, h=0.6, col="stripe_red")
    # the parcel hoist over the loading door at the back, its rope dropping outside the gallery rail
    Q.hoist(b, CX + 2.62 * math.sin(rad(135)), CY - 2.62 * math.cos(rad(135)), ZG + 3.1, face=135, out=2.35, rope=10.2, load="crate")
    # pennants from the gate posts up to the eaves and on round to the rail
    for sgn in (-1, 1):
        ex, ey, ez = sgn * 3.25, CY - 1.4, ZG + 3.25
        Q.bunting(b, (sgn * 1.8, GY - 4.45, ZG + 2.45), (ex, ey, ez), sag=0.3)
        Q.bunting(b, (ex, ey, ez), (sgn * 4.7, GY + 1.3, ZG + 1.1), sag=0.25, cols=("stripe_yellow", "linen", "stripe_red"))


def counting_house(b):
    ch = b.body(4.0, 4.4, 3.0, mat="plaster", col="cream", x=-2.6, y=2.2)
    Q.plinth(ch, h=0.7, walls="frl")
    P.timber_frame(ch.front, z0=0.7, posts=[0.0, 1.75, 4.0], rails=[0.7, 3.0], braces=[])
    P.timber_frame(ch.left, z0=0.7, posts=[0.0, 2.2, 4.4], rails=[0.7, 3.0], braces=[])
    P.door(ch.front, 0.95, w=0.95, h=2.0, z=0.18, col=A, frame="timber", steps=1, lamp=True)
    Q.counter(ch.front, 2.85, 1.05, w=1.5, h=1.15, col=A, goods="parcels")
    P.window(ch.left, 1.2, 1.2, w=0.8, h=1.2, shutters=A)
    P.window(ch.left, 3.3, 1.2, w=0.8, h=1.2, shutters=A, box=True)
    P.window(ch.right, 1.3, 1.2, w=0.8, h=1.2)
    ch.gable(ridge="y", pitch=50, mat="tiles", sag=0.08, eave=0.24, verge=0.15)
    Q.gable_holes(ch.front)
    P.window(ch.front, 2.0, 3.45, w=0.7, h=0.95, shutters=A, lintel="timber")
    Q.sign(ch.front, 3.72, 2.95, emblem="letter", shape="shield", col=A, out=0.8)
    P.chimney(b, -3.75, 3.0, 3.4, 2.7, mat="brick", pots=1)
    # the yard in front: parcels in and out
    P.crate(b, -0.05, 0.6, 0, s=0.6, rz=12)
    P.crate(b, -0.02, 0.62, 0.6, s=0.45, rz=40)
    P.sack(b, 0.75, 0.5, 0)
    P.barrel(b, 2.9, 1.7, 0)
    P.crate(b, 3.6, 1.9, 0, s=0.55, rz=25)
    P.bench(b, 3.6, 1.0, 0, w=1.3)
    Q.cat(b, 3.9, 1.0, 0.48, rz=-20, col="#d98b3a")


def build(b):
    shaft(b)
    gallery(b)
    lantern_storey(b)
    counting_house(b)
