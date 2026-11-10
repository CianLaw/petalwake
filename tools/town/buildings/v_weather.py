# The weather house: three generations of the Marrans have read the sky from its roof and chalked the forecast on
# the door for the boats. A square, battered, lime-washed tower-house; a boarded roof walk jettied out on brackets
# round a little slated cap-house, bristling with vanes, cups, a storm cone and a windsock. Cream harl, mustard paint.
import math

from kit import *
import parts as P
import parts_v as V
import parts_h as PH
import parts_m as PM

META = {"name": "The Weather House", "kind": "tower", "lot": (7.0, 7.0), "wobble": 0.03}


def build(b):
    ac = "mustard"
    W, D, H, BT = 5.4, 5.4, 12.3, 0.028
    cy = D / 2
    t = V.BBody(b, W, D, H, mat="plaster", col="cream", batter=BT, depth=0.45)
    b.footprint(-3.2, 0.0, 3.2, 6.85, H)
    V.footing(t, h=0.7, out=0.1, col="grey", boulders="frl")
    V.quoins(t, corners="fr", size=(0.74, 0.4, 0.56), col="grey")
    V.quoins(t, corners="bl", size=(0.74, 0.4, 0.56), z1=5.6, col="grey")
    # front: the door and two columns of small windows (the stair climbs behind the left one)
    V.door(t.front, 1.5, w=1.0, h=1.95, z=0.36, col=ac, steps=2, step=False, lamp=True)
    V.window(t.front, 3.8, 1.3, w=0.62, h=0.9, col=ac, shut="half")
    for z in (4.2, 7.2, 10.1):
        V.window(t.front, 3.8, z, w=0.62, h=0.9, col=ac)
    V.window(t.front, 1.5, 5.6, w=0.5, h=0.75, col=ac, shut="one")
    V.window(t.front, 1.5, 8.7, w=0.5, h=0.75, col=ac, shut="one")
    PM.sundial(t.front, 2.7, 3.55, r=0.55, col="brass")
    V.harl(t.front, n=12, where="base")
    # right: two windows and the observer's little boarded bay
    V.window(t.right, 2.7, 4.2, w=0.62, h=0.9, col=ac)
    V.window(t.right, 2.7, 10.1, w=0.62, h=0.9, col=ac, shut="half")
    V.harl(t.right, n=10, where="base")
    xr = W / 2 - BT * 6.6
    with b.at(xr, cy - 0.3, 6.6, rz=90):
        o = b.body(1.5, 0.66, 1.55, mat="planks", col="greyoak", x=0, y=-0.27, foot=False, floor="planks", depth=0.08)
        P.window(o.front, 0.75, 0.42, w=1.0, h=0.85, frame=ac, bars=(2, 1), sill=False, lintel=None, depth=0.07)
        V.shed_roof(b, 1.62, 0.78, 32, x=0, y=0.09, z=1.55 + 0.49, face=0, eave=0.12, verge=0.1, course=0.24, thick=0.07)
        for sx in (-0.6, 0.6):
            V.knee(b, (sx, 0.0, -0.8), (sx, -0.55, -0.02), w=0.11)
    # left and back
    V.window(t.left, 2.7, 1.4, w=0.62, h=0.9, col=ac)
    V.window(t.left, 2.7, 7.2, w=0.62, h=0.9, col=ac)
    V.harl(t.left, n=10, where="base")
    for z in (4.2, 7.2, 10.1):
        V.window(t.back, 1.6, z, w=0.55, h=0.8, col=ac, shut="one")
    V.harl(t.back, n=10, where="base")
    # ------------------------------------------------------------------ the roof walk
    DZ = H + 0.32
    hw = W / 2 - BT * H
    DW, DD = 6.3, 6.2
    dy = cy + 0.05
    b.box(2 * hw + 0.16, 2 * hw + 0.16, 0.32, "timber", col="darkoak", x=0, y=cy, z=H - 0.04, top=False, lod=0)
    V.deck(b, DW, DD, DZ, x=0, y=dy, thick=0.1, joists=0.8)
    zb = DZ - 1.8
    for k in range(4):
        s = -1.85 + 3.7 * k / 3
        V.knee(b, (s, BT * zb, zb), (s, dy - DD / 2 + 0.18, DZ - 0.3))
        V.knee(b, (s, D - BT * zb, zb), (s, dy + DD / 2 - 0.18, DZ - 0.3))
        V.knee(b, (-(W / 2 - BT * zb), cy + s, zb), (-DW / 2 + 0.18, cy + s, DZ - 0.3))
        V.knee(b, (W / 2 - BT * zb, cy + s, zb), (DW / 2 - 0.18, cy + s, DZ - 0.3))
    x0, x1, y0, y1 = -DW / 2 + 0.09, DW / 2 - 0.09, dy - DD / 2 + 0.09, dy + DD / 2 - 0.09
    P.railing(b, [(1.75, y0, DZ), (x1, y0, DZ), (x1, y1, DZ), (x0, y1, DZ), (x0, y0, DZ), (-1.35, y0, DZ)], h=1.0, style="cross", col="darkoak")
    with b.at(0.2, 0.95, DZ):
        P.landing_mark(b, 1.05)
    b.pad(0.2, 0.95, DZ, radius=1.1, face=0, name="Roof walk")
    # the cap-house at the head of the stair, and the chimney
    c = V.BBody(b, 2.5, 2.3, 2.0, mat="plaster", col="cream", x=-1.0, y=3.8, z=DZ, batter=0.0, depth=0.3, foot=False)
    V.door(c.front, 1.55, w=0.8, h=1.7, z=0.03, col=ac, step=False, jambs=False)
    V.window(c.right, 1.15, 0.85, w=0.5, h=0.6, lintel="timber")
    c.hip(pitch=54, mat="slate", eave=0.28, course=0.36)
    apex = DZ + 2.0 + (2.3 / 2) * math.tan(rad(54))
    V.vane(b, -1.0, 3.8, apex - 0.15, h=2.4, kind="arrow", s=1.25, rz=-78)
    V.chimney(b, 1.7, 4.55, H - 1.0, 4.5, w=0.95, d=0.75, col="grey")
    PH.gull(b, 1.7, 4.55, H + 3.86, rz=300)
    # the instruments
    V.anemometer(b, x1 - 0.02, y0 + 0.02, DZ, h=2.9, arm=0.4, cup=0.12)
    V.storm_mast(b, -2.42, 3.05, DZ, h=4.3, rz=90, yard=1.2)
    V.windsock(b, x0 + 0.02, y0 + 0.02, DZ, h=2.75, rz=98)
    V.vane(b, x1, cy - 0.2, DZ + 1.0, h=1.5, kind="whale", s=0.8, rz=-78, arms=False)
    V.vane(b, x0, cy + 0.3, DZ + 1.0, h=1.3, kind="gull", s=0.7, rz=-78, arms=False)
    V.vane(b, x0, y1 - 0.4, DZ + 1.0, h=1.9, kind="fish", s=0.85, rz=-78, arms=False)
    V.vane(b, x1, y1 - 0.5, DZ + 1.0, h=2.3, kind="boat", s=0.8, rz=-78, arms=False)
    V.weather_screen(b, 2.3, 2.75, DZ, rz=90)
    V.rain_barrel(b, 0.62, 2.35, DZ, r=0.3, h=0.8)
    with b.detail(2):
        V.beam(b, (0.3, 2.62, DZ + 1.95), (0.6, 2.4, DZ + 1.0), w=0.06, mat="metal", col="lead", caps=False)
    # ------------------------------------------------------------------ the store at the back, and the yard things
    ln = V.BBody(b, 3.2, 1.35, 1.9, col="grey", x=-0.9, y=D + 0.55, batter=0.04, depth=0.34)
    V.footing(ln, h=0.35, boulders="")
    V.door(ln.back, 1.1, w=0.85, h=1.5, col=ac, half=True, step=False, lintel="timber")
    V.slit(ln.back, 2.5, 0.9, h=0.6)
    r2 = ln.shed(pitch=27, high="front", mat="slate", eave=0.25, verge=0.18)
    V.weights(r2, rows=(0.3,), verges=False)
    V.rain_barrel(b, 1.3, D + 0.5, r=0.34, h=0.9)
    V.peat_stack(b, 2.15, D + 0.52, w=0.9, d=0.7, h=0.95, rz=90, turf=False, loose=4)
    P.bench(b, 1.15, -0.5, w=1.3, rz=-3)
