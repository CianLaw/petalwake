# Larkhaven Town Hall: the wool merchants built it round an older watch tower; the butter market was held under its
# arcade, proclamations are read from the balcony, and the whole town sets its day by the four-faced clock.
# Massing: an arcaded hall under a steep tiled roof with dormers; at its right hand a staged 32 m clock tower with a
# corbelled, railed gallery (the landing place), an open belfry and a bell-cast spire; a clerks' wing and a stair turret behind.
# Materials: warm rubble tower with pale ashlar quoins, bands and arcade, cream plaster hall, tiles and slate; navy doors.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "Larkhaven Town Hall", "kind": "townhall", "lot": (16.0, 14.0), "landmark": True}

A = "navy"
TX, TY = 4.7, 3.1                    # centre of the clock tower
X0, HW, GH = -7.7, 9.4, 4.4          # the hall: its left edge, its width, the height of the arcaded ground storey
HX = X0 + HW / 2
PW = (HW - 4 * 1.7) / 5              # width of an arcade pier
ARCH = [PW + 0.85 + (1.7 + PW) * i for i in range(4)]


def clock_face(s, pos, z, r=1.2, hour=9, minute=41):
    b = s.b
    u = s.U(pos)
    P.clock(s, pos, z, r=r, hour=hour, minute=minute)

    def deco():
        with s.onu(u, z):
            with b.at(rx=90):
                with b.detail(1):
                    b.revolve([(r + 0.38, 0.0), (r + 0.38, 0.06), (r + 0.08, 0.06)], "ashlar", col="stone", seg=20)
                with b.detail(2):
                    for k in range(4):
                        with b.at(rz=90 * k):
                            b.box(0.26, 0.36, 0.1, "ashlar", col="stone", y=-(r + 0.24), z=0.0)

    s.add(deco)


def tower(b):
    # --- three rubble stages, each stepping in under a chamfered ashlar band
    s1 = b.body(6.0, 6.0, 8.6, mat="masonry", col="warm", x=TX, y=TY)
    Q.plinth(s1, h=1.0, out=0.14, col=shade("warm", 0.9), walls="frb")
    Q.quoins(s1, corners="frb", z0=1.0, size=(0.62, 0.34, 0.48))
    P.door(s1.front, 3.0, w=1.7, h=3.3, z=0.5, arch=0.85, col=A, frame="stone", double=True, lamp=True)
    Q.steps(s1.front, 3.0, w=2.5, n=3, z=0.5, rise=0.167)
    P.window(s1.front, 3.0, 5.5, w=0.9, h=1.9, arch=0.45, bars=(1, 3), lintel=None, sill=False)
    Q.surround(s1.front, 3.0, 5.5, 0.9, 1.9, arch=0.45, sill=True)
    P.window(s1.right, 3.0, 2.3, w=0.8, h=1.5, arch=0.4, bars=(1, 2))
    P.window(s1.right, 3.0, 5.5, w=0.8, h=1.9, arch=0.4, bars=(1, 3))
    P.door(s1.left, 4.4, w=1.0, h=2.3, z=0.2, arch=0.5, col=A, frame=None)
    P.stones(s1.front, n=12, z0=1.1)
    P.stones(s1.right, n=12, z0=1.1)
    Q.putlogs(s1.right, n=6, z0=2.0)
    b.box(6.12, 6.12, 0.3, "ashlar", col="stone", x=TX, y=TY, z=8.45, tx=5.66 / 6.12, ty=5.66 / 6.12)
    s2 = b.body(5.6, 5.6, 6.6, mat="masonry", col="warm", x=TX, y=TY, z=8.6)
    Q.quoins(s2, corners="frb", size=(0.6, 0.32, 0.47))
    P.window(s2.front, 2.8, 2.6, w=0.75, h=1.8, arch=0.37, bars=(1, 3))
    P.window(s2.right, 2.8, 2.6, w=0.75, h=1.8, arch=0.37, bars=(1, 3))
    P.window(s2.back, 2.8, 3.4, w=0.7, h=1.5, arch=0.35)
    P.stones(s2.front, n=9)
    P.stones(s2.right, n=9)
    Q.putlogs(s2.front, n=6, z0=0.8)
    Q.putlogs(s2.right, n=5, z0=0.8)
    b.box(5.72, 5.72, 0.3, "ashlar", col="stone", x=TX, y=TY, z=15.05, tx=5.26 / 5.72, ty=5.26 / 5.72)
    s3 = b.body(5.2, 5.2, 5.2, mat="masonry", col="warm", x=TX, y=TY, z=15.2)
    Q.quoins(s3, size=(0.56, 0.3, 0.46))
    for wl in s3.walls:
        clock_face(wl, 2.6, 2.7, r=1.25)
    # --- the gallery: a flagged floor oversailing on a corbel table, a stone balustrade open to the square
    Q.corbel_table(b, 5.2, 5.2, 20.4, out=0.5, h=0.65, cw=0.34, spacing=0.75, x=TX, y=TY)
    b.box(6.2, 6.2, 0.2, "ashlar", col="stone", x=TX, y=TY, z=20.4, cap="flagstone", capcol="sand", bottom=True)
    with b.at(TX, TY, 20.6):
        G = 2.98
        rail = [(0.9, -G, 0), (G, -G, 0), (G, G, 0), (-G, G, 0), (-G, -G, 0), (-0.9, -G, 0)]
        P.railing(b, rail, h=1.0, style="balusters", col="stone", mat="ashlar", post=0.13, gap=0.27)
        for i, (px, py, _) in enumerate(rail):
            with b.detail(1):
                b.box(0.3, 0.3, 1.18, "ashlar", col="stone", x=px, y=py)
            if i in (0, 5):
                Q.post_lantern(b, px, py, 1.18)
            else:
                Q.ball(b, px, py, 1.18, r=0.15)
        with b.at(0, -2.15, 0):
            P.landing_mark(b, 0.72)
        b.pad(0, -2.15, 0.0, radius=0.75, face=0, name="Town hall belfry gallery")
        Q.pigeon(b, G, -1.2, 1.06, rz=80)
        Q.pigeon(b, -G, 0.6, 1.06, rz=-70)
        Q.pigeon(b, 1.9, G, 1.06, rz=170)
        # --- the open belfry: four arches, the great bell, the hatch down to the clock room
        for k in range(4):
            with b.at(rz=90 * k):
                with b.at(-1.35, -1.35, 0):
                    Q.arcade(b, 2.7, 3.7, thick=0.5, arches=[(1.35, 1.5, 3.0, 0.75)], mat="ashlar", col="stone", ends="", top=False)
        b.box(3.0, 3.0, 0.22, "ashlar", col="stone", z=3.7, bottom=True)
        P.bell(b, 0, 0, 3.1, r=0.52, beam=1.8)
        with b.detail(2):
            b.box(0.8, 0.8, 0.04, "planks", col="darkoak", x=0.35, y=0.35, z=0.0)
            b.box(0.12, 0.12, 0.03, "metal", col="iron", x=0.35, y=0.1, z=0.04)
        # --- the spire: bell-cast slate, four lucarnes, a copper ball and the lark
        b.loop_roof(3.1, 3.1, z=3.92, section=[(0, 0), (0.5, 0.45), (1.0, 2.0), (1.55, 7.4)], mat="slate", eave=0.5, course=0.5)
        for k in range(4):
            a = rad(90 * k)
            P.dormer(b, 1.0 * math.sin(a), -1.0 * math.cos(a), 4.42, w=0.62, h=0.72, depth=0.6, face=90 * k, wall="ashlar", col="stone", roof="slate",
                     pitch=50, lod=2)
        T = 3.92 + 7.4
        with b.detail(1):
            b.revolve([(0.1, T - 0.5), (0.07, T - 0.05), (0.19, T + 0.12), (0.19, T + 0.26), (0.05, T + 0.45)], "metal", col="copper", seg=8)
        Q.weathercock(b, 0, 0, T + 0.4, h=1.9, shape="lark", size=1.5)


def hall(b):
    # --- the loggia: its floor one step up on the hidden foundation, four arches to the square and one at the end
    b.box(HW - 0.04, 2.88, 3.2, "masonry", col="warm", x=HX, y=1.46, z=-3.0, cap="flagstone", capcol="sand")
    with b.at(X0, 0, 0):
        Q.arcade(b, HW, GH, thick=0.55, arches=[(u, 1.7, 3.35, 0.85, 0.2) for u in ARCH], mat="ashlar", col="stone", ends="l", top=False)
    with b.at(X0, 2.9, 0, rz=270):
        Q.arcade(b, 2.35, GH, thick=0.5, arches=[(1.175, 1.4, 3.2, 0.7, 0.2)], mat="ashlar", col="stone", ends="", top=False)
    with b.detail(1):
        for i in range(5):
            b.box(PW + 0.1, 0.67, 0.15, "ashlar", col="stone", x=X0 + PW / 2 + (1.7 + PW) * i, y=0.275, z=2.56, bottom=True)
        b.box(HW - 0.4, 0.42, 0.1, "ashlar", col="stone", x=HX, y=-0.2, z=0.0)
    with b.detail(2):
        for u in ARCH:
            b.box(0.24, 0.12, 0.44, "ashlar", col="stone", x=X0 + u, y=-0.03, z=3.48, tx=1.35)
    # --- the rooms behind the loggia
    g = b.body(HW, 6.1, GH, mat="plaster", col="cream", x=HX, y=5.95)
    Q.plinth(g, h=0.55, walls="lb")
    P.door(g.front, HW / 2, w=1.5, h=2.8, z=0.2, arch=0.6, col=A, frame="stone", double=True)
    for u in (1.9, HW - 1.9):
        P.window(g.front, u, 1.3, w=1.0, h=1.7, arch=0.4, bars=(1, 2))
    P.lantern(g.front, HW / 2 - 1.35, 2.5)

    def board():
        with g.front.on(HW / 2 + 1.75, 1.45):
            with b.detail(2):
                b.box(0.95, 0.05, 0.72, "planks", col="darkoak", x=0, y=-0.03, z=0)
                for (px, pz, pw, ph) in ((-0.24, 0.36, 0.3, 0.26), (0.2, 0.3, 0.34, 0.34), (-0.2, 0.06, 0.36, 0.22), (0.24, 0.05, 0.24, 0.2)):
                    b.quad((px - pw / 2, -0.062, pz), (px + pw / 2, -0.062, pz), (px + pw / 2, -0.062, pz + ph), (px - pw / 2, -0.062, pz + ph), "paint", col="ivory")

    g.front.add(board)
    for u in (2.0, 4.4):
        P.window(g.left, u, 1.3, w=1.0, h=1.7, arch=0.4, bars=(1, 2), box=(u < 3))
    P.door(g.back, 1.3, w=1.0, h=2.1, z=0.2, col=A, frame="stone", steps=1)
    P.window(g.back, 2.75, 1.3, w=0.9, h=1.4, bars=(1, 2))
    P.exposed(g.left, "base", n=8)
    # --- the council chamber over it: tall windows in stone surrounds, the proclamation balcony, two banners
    up = b.body(HW, 9.0, 4.7, mat="plaster", col="cream", x=HX, y=4.5, z=GH, floor="planks")
    P.band(up, 0.0, h=0.24, out=0.08)
    P.band(up, 4.44, h=0.22, out=0.07)
    for i, u in enumerate(ARCH):
        P.window(up.front, u, 0.9, w=1.15, h=2.9, arch=0.57, bars=(1, 3), lintel=None, sill=False, box=(i in (0, 3)))
        Q.surround(up.front, u, 0.9, 1.15, 2.9, arch=0.57, sill=(i != 1))
    P.balcony(up.front, ARCH[1], 0.86, w=2.0, out=0.9, rail="iron", floor="ashlar", floor_col="stone", brackets=False, thick=0.14)

    def corbels():
        for sgn in (-1, 1):
            with up.front.on(ARCH[1] + sgn * 0.7, 0.72):
                Q.corbel(b, 0.26, 0.75, 0.7)

    up.front.add(corbels)
    for u in ((ARCH[0] + ARCH[1]) / 2, (ARCH[2] + ARCH[3]) / 2):
        P.flag(b, X0 + u, -0.05, GH + 2.5, pole=1.7, w=1.2, h=0.8, col="stripe_blue", kind="banner", lean=38)
    for u in (2.6, 6.4):
        P.window(up.left, u, 0.9, w=1.0, h=2.4, arch=0.5, bars=(1, 3))
    for u in (1.6, 4.2):
        P.window(up.back, u, 1.2, w=1.0, h=1.9, arch=0.45, bars=(1, 2))
    up.gable(ridge="x", pitch=52, mat="tiles", sag=0.14, eave=0.5, verge=0.06)
    Q.gable_holes(up.left)
    Q.round_window(up.left, 4.5, 4.7 + 2.0, r=0.7, glass="#8fb0d8")
    zr = lambda yy: GH + 4.7 + yy * math.tan(rad(52))            # the roof surface, yy in from the eaves wall
    for x in (-6.2, -3.4, -0.6):
        P.dormer(b, x, 0.95, zr(0.95), w=1.15, h=1.15, depth=1.7, col="cream", frame="ivory")
    P.dormer(b, -1.8, 9.0 - 0.95, zr(0.95), w=1.15, h=1.15, depth=1.7, face=180, col="cream")
    Q.stack(b, -5.0, 6.4, zr(2.6) - 0.6, 4.6, w=0.95, d=0.75, pots=3)
    P.chimney(b, -0.4, 6.9, zr(2.1) - 0.5, 3.6, mat="masonry", col="warm", pots=2)
    # --- a lean-to store in the yard behind
    lt = b.body(2.5, 1.8, 2.2, mat="masonry", col="warm", x=-3.15, y=9.9)
    Q.plinth(lt, h=0.3, walls="rbl")
    P.door(lt.back, 0.8, w=0.8, h=1.8, z=0.05, col=A, frame="timber")
    P.window(lt.back, 1.9, 1.0, w=0.5, h=0.6, bars=(1, 0), lintel="timber")
    rs = Q.lean_to(b, 2.5, 1.8, pitch=25, x=-3.15, y=9.0, z=2.2, face=180, eave=0.25, verge=0.2)
    b.tri((-4.4, 10.8, 2.2), (-4.4, 9.0, 2.2), (-4.4, 9.0, 2.2 + rs), "masonry", col="warm")
    b.tri((-1.9, 9.0, 2.2), (-1.9, 10.8, 2.2), (-1.9, 9.0, 2.2 + rs), "masonry", col="warm")
    # --- life under the arcade
    P.bench(b, X0 + 2.2, 2.55, 0.2, w=1.7)
    P.barrel(b, 1.2, 2.3, 0.2)
    Q.bunting(b, (X0 + 0.2, -0.12, 4.32), (1.6, -0.12, 4.32), sag=0.45)


def wing(b):
    wg = b.body(5.8, 6.4, 6.4, mat="plaster", col="cream", x=4.6, y=9.3)
    Q.plinth(wg, h=0.6, walls="rbl")
    Q.quoins(wg, corners="bl", z0=0.6)
    for z in (1.3, 4.0):
        for u in (1.6, 4.6):
            P.window(wg.right, u, z, w=0.9, h=1.4, box=(z > 2 and u < 2))
        P.window(wg.back, 4.1, z, w=0.9, h=1.4, shutters=A)
        P.window(wg.left, 1.7, z, w=0.9, h=1.4)
    P.window(wg.back, 1.6, 4.0, w=0.9, h=1.4, shutters=A)
    P.door(wg.back, 1.6, w=0.95, h=2.05, z=0.2, col=A, frame="timber", steps=1, porch="gable", lamp=True)
    wg.gable(ridge="y", pitch=48, mat="tiles", sag=0.08, eave=0.4, verge=0.3)
    Q.gable_holes(wg.back)
    P.window(wg.back, 2.9, 6.4 + 0.7, w=0.7, h=1.0, arch=0.3)
    P.chimney(b, 6.3, 10.6, 7.0, 3.7, mat="brick", pots=2)
    P.laundry(b, (1.75, 12.3, 3.4), (-5.3, 10.95, 3.6), n=5)


def turret(b):
    x, y = -6.2, 9.9
    t = b.round(1.45, 13.2, r1=1.35, mat="masonry", col="warm", seg=14, x=x, y=y)
    P.round_base(b, 1.45, h=0.8, out=0.2, seg=14, ring=t)
    P.door(t, 180, w=0.85, h=1.95, z=0.15, arch=0.42, col=A, steps=1)
    for a, z in ((235, 3.2), (275, 6.0), (205, 8.6), (255, 11.0), (120, 11.0)):
        t.opening(a, z, 0.45, 1.0, arch=0.22, depth=0.24)
    P.ivy(t, 245, 0.4, w=1.5, h=4.2, n=7)
    b.cone_roof(1.35, 3.8, mat="slate", x=x, y=y, z=13.2, seg=14, eave=0.38, flare=0.4, course=0.6)


def build(b):
    hall(b)
    tower(b)
    wing(b)
    turret(b)
    P.planter(b, TX - 2.0, -0.42, 0, bush=True)
    P.planter(b, TX + 2.0, -0.42, 0, bush=True)
