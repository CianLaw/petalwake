# The chapel's bell tower: older than the chapel itself, a watch tower given bells when the town grew peaceful; the
# sexton keeps his tools in the lean-to and the ringers' ladder comes up through a hatch in the belfry floor.
# Massing: a square rubble shaft in three stages stepping in under chamfered bands, buttressed at the foot, about 24 m
# to the eaves of a low wide-eaved pyramid roof; the top stage is an open belfry (the landing place) with three bells.
# Materials: grey-warm rubble with pale ashlar bands, arch surrounds and quoins, slate roof, a tiled lean-to; teal door.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Chapel Bell Tower", "kind": "tower", "lot": (6.0, 6.0), "lean": (-0.003, 0.002)}

A = "teal"
TX, TY = -0.4, 2.95
ZB = 17.9                  # the belfry floor


def build(b):
    ST = mix("warm", "grey", 0.5)
    # --- stage one: the door between two buttresses
    s1 = b.body(4.4, 4.4, 7.0, mat="masonry", col=ST, x=TX, y=TY)
    P.plinth(s1, h=0.9, out=0.12, col=shade(ST, 0.9))
    P.door(s1.front, 2.2, w=1.0, h=2.2, z=0.34, arch=0.5, col=A, frame="stone", lamp=True)
    Q.steps(s1.front, 2.2, w=1.4, n=2, z=0.34)
    for sx in (-1, 1):
        with b.at(TX + sx * 1.8, TY - 2.2, 0):
            Q.buttress(b, w=0.8, d=0.6, h=6.4, steps=3, top_d=0.22, col=ST)
        with b.at(TX + sx * 1.8, TY + 2.2, 0, rz=180):
            Q.buttress(b, w=0.8, d=0.6, h=5.2, steps=2, top_d=0.3, col=ST)
    slit = dict(w=0.5, h=1.4, arch=0.25, lintel=None, sill=False, bars=(0, 2))
    P.window(s1.front, 2.2, 4.5, **slit)
    P.window(s1.left, 2.2, 3.0, **slit)
    P.window(s1.back, 2.2, 4.5, **slit)
    P.stones(s1.front, n=8, z0=1.0)
    P.stones(s1.left, n=10, z0=1.0)
    P.ivy(s1.left, 3.5, 0.3, w=1.6, h=4.6, n=7)
    b.box(4.52, 4.52, 0.28, "ashlar", col="stone", x=TX, y=TY, z=6.86, tx=4.16 / 4.52, ty=4.16 / 4.52)
    # --- stage two: a sundial to the square
    s2 = b.body(4.1, 4.1, 6.0, mat="masonry", col=ST, x=TX, y=TY, z=7.0)
    Q.quoins(s2, size=(0.56, 0.3, 0.46))
    Q.sundial(s2.front, 2.05, 2.5, r=0.66)
    P.window(s2.front, 2.05, 3.6, **slit)
    P.window(s2.right, 2.05, 1.8, **slit)
    P.window(s2.left, 2.05, 3.6, **slit)
    P.window(s2.back, 2.05, 1.8, **slit)
    P.stones(s2.front, n=7)
    P.stones(s2.right, n=8)
    for wl in s2.walls:
        Q.putlogs(wl, n=5, z0=0.8)
    b.box(4.22, 4.22, 0.28, "ashlar", col="stone", x=TX, y=TY, z=12.86, tx=3.86 / 4.22, ty=3.86 / 4.22)
    # --- stage three: paired lancets under the belfry floor
    s3 = b.body(3.8, 3.8, 4.6, mat="masonry", col=ST, x=TX, y=TY, z=13.0)
    Q.quoins(s3, size=(0.54, 0.3, 0.46))
    lancet = dict(w=0.5, h=1.9, arch=0.25, lintel=None, sill=False, bars=(0, 3))
    for wl in s3.walls:
        for u in (1.42, 2.38):
            P.window(wl, u, 1.3, **lancet)
            if wl is s3.front or wl is s3.right:
                Q.surround(wl, u, 1.3, 0.5, 1.9, arch=0.25, t=0.13, keystone=False)
    Q.corbel_table(b, 3.8, 3.8, 17.6, out=0.17, h=0.34, cw=0.24, spacing=0.55, x=TX, y=TY)
    b.box(4.14, 4.14, 0.3, "ashlar", col="stone", x=TX, y=TY, z=17.6, cap="planks", capcol="greyoak", bottom=True)
    # --- the open belfry: the arch to the square is the way in, the other three have a breast-high wall
    with b.at(TX, TY, ZB):
        W = 3.8
        for k in range(4):
            with b.at(rz=90 * k):
                with b.at(-W / 2, -W / 2, 0):
                    arch = (W / 2, 2.0, 3.5, 1.0) if k == 0 else (W / 2, 2.0, 2.5, 1.0, 1.0)
                    f, bk = Q.arcade(b, W, 4.5, thick=0.6, arches=[arch], mat="masonry", col=ST, ends="", top=False)
                    Q.surround(f, W / 2, arch[4] if k else 0.0, 2.0, arch[2], arch=1.0, t=0.2)
                    if k:
                        with b.detail(1):
                            b.box(2.12, 0.74, 0.08, "ashlar", col="stone", x=W / 2, y=0.3, z=1.0, bottom=True)
        b.box(4.1, 4.1, 0.25, "ashlar", col="stone", z=4.5, bottom=True)
        P.bell(b, 0, 0, 4.15, r=0.5, beam=2.7)
        with b.at(-1.0, 0, 0, rz=90):
            P.bell(b, 0, 0, 3.42, r=0.3, beam=2.7)
        with b.at(1.0, 0, 0, rz=90):
            P.bell(b, 0, 0, 3.5, r=0.34, beam=2.7)
        with b.detail(2):                         # the ringers' hatch and the head of their ladder
            b.box(0.7, 0.7, 0.04, "planks", col="darkoak", x=0.9, y=0.9, z=0.0)
            for dx in (-0.2, 0.2):
                b.beam((0.9 + dx, 1.2, 0.0), (0.9 + dx, 1.25, 0.95), w=0.05, mat="timber", col="greyoak")
            b.beam((0.7, 1.22, 0.5), (1.1, 1.22, 0.5), w=0.035, mat="timber", col="greyoak", caps=False)
        P.landing_mark(b, 0.95)
        b.pad(0, 0, 0.0, radius=1.0, face=0, name="Chapel bell tower belfry")
        rise = b.loop_roof(4.0, 4.0, pitch=33, mat="slate", z=4.75, eave=0.42, course=0.45)
        Q.ball(b, 0, 0, 4.75 + rise - 0.12, r=0.2, mat="metal", col="copper")
        Q.weathercock(b, 0, 0, 4.75 + rise + 0.2, h=1.8, shape="cock", size=1.25)
    # --- the sexton's lean-to on the flank
    sh = b.body(1.05, 3.2, 2.0, mat="masonry", col=ST, x=TX + 2.2 + 0.525, y=TY + 0.2)
    Q.plinth(sh, h=0.25, walls="frb", col=shade(ST, 0.9))
    P.door(sh.front, 0.525, w=0.72, h=1.72, z=0.05, col=A, frame="timber")
    P.window(sh.right, 1.6, 0.95, w=0.5, h=0.6, bars=(1, 0), lintel="timber", sill=False)
    x0, x1, y0, y1 = TX + 2.2, TX + 3.25, TY - 1.4, TY + 1.8
    rs = Q.lean_to(b, 3.2, 1.05, pitch=32, x=x0, y=TY + 0.2, z=2.0, face=90, eave=0.05, verge=0.12, course=0.3)
    b.tri((x0, y0, 2.0), (x1, y0, 2.0), (x0, y0, 2.0 + rs), "masonry", col=ST)
    b.tri((x1, y1, 2.0), (x0, y1, 2.0), (x0, y1, 2.0 + rs), "masonry", col=ST)
    P.barrel(b, 2.4, 1.0, 0)
