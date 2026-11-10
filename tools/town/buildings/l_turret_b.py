# The lamp house: the lamplighter keeps a light of his own burning at the top of his stair, in a glazed lantern like a lighthouse's, and the brooms set down on the walk round it.
# A low house across the front of the lot; rising from behind its ridge a lime-washed round turret with a painted band, flaring out to a stone walk with an iron rail, a little lantern room and a copper cap.
# Sage plaster house, white turret on a rubble foot, copper and tiles; accent red.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC

META = {"name": "The Lamp House", "kind": "tower-house", "lot": (6.0, 7.0), "terrace": True}


def build(b):
    acc = "red"
    W, D, top = 5.5, 3.4, 5.4
    g = b.body(W, D, top, mat="plaster", col="sage")
    P.plinth(g, h=0.5)
    f = g.front
    # --- the house front
    P.door(f, 1.3, w=0.9, h=2.05, z=0.17, col=acc, frame="stone", steps=1, lamp=True)
    L.hood(f, 1.3, 2.7, w=1.45, out=0.6, kind="gable", rise=0.34)
    P.window(f, 3.95, 1.0, w=1.5, h=1.35, bars=(2, 1), box=True)
    for u, bx in ((1.1, False), (2.75, True), (4.4, False)):
        P.window(f, u, 2.8 + 0.8, w=0.75, h=1.15, shutters=acc, box=bx)
    PC.oculus(g.left, D / 2, top + 0.62, r=0.24); PC.oculus(g.right, D / 2, top + 0.62, r=0.24)
    P.window(g.back, 0.9, 1.1, w=0.7, h=1.1); P.window(g.back, 4.75, 2.8 + 0.85, w=0.7, h=1.0, shutters=acc)
    P.door(g.back, 4.6, w=0.85, h=2.0, z=0.17, col=acc, frame="timber", steps=1)
    rise = g.gable(ridge="x", pitch=42, eave=0.3, verge=0.04, sag=0.06)
    P.chimney(b, -W / 2 + 0.42, D / 2, top + 0.8, 2.5, w=0.66, d=0.85, mat="brick", pots=2)
    # --- the turret behind
    tx, ty, zf = 0.3, 4.3, 11.0
    r0, r1 = 1.55, 1.3
    t = b.round(r0, zf, r1=r1, mat="plaster", col="white", x=tx, y=ty, seg=20)
    P.door(t, 180, w=0.85, h=2.0, arch=0.42, z=0.17, col=acc, frame="stone", steps=1)
    P.round_base(b, r0, h=1.6, out=0.18, seg=20, ring=t)
    for a, z in ((270, 3.3), (90, 5.0), (205, 6.3), (335, 8.9), (70, 9.4)):
        P.window(t, a, z, w=0.5, h=1.0, arch=0.25, bars=(0, 1))
    zb = 7.3
    P.ring_band(b, r0 + (r1 - r0) * zb / zf - 0.004, zb, h=0.85, out=0.016, mat="plaster", col="!#b5433a", x=tx, y=ty, seg=20, lod=0)
    PC.stone_walk(b, 0.95, 2.5, zf, seg=20, drop=1.15, r_foot=r1, x=tx, y=ty)
    with b.at(tx, ty, 0):
        PC.rail_arc(b, 2.42, 26, 334, z=zf, h=1.0, style="iron", col="iron", knobs="brass")
        with b.at(0, -1.75, zf):
            P.landing_mark(b, 0.7)
    b.pad(tx, ty - 1.75, zf, radius=0.75, face=0, name="The lamp walk")
    # the lantern room and its cap
    lr = b.round(0.95, 2.6, mat="plaster", col="white", x=tx, y=ty, z=zf, seg=14, foot=False)
    P.door(lr, 0, w=0.7, h=1.85, z=0.03, col=acc, frame=None)
    for a in (60, 120, 180, 240, 300):
        lr.opening(a, 0.8, 0.55, 1.35, pane="glow", pane_col="#ffd88a", depth=0.1)
    with b.detail(1):
        P.ring_band(b, 0.95, zf + 0.5, h=0.14, out=0.05, x=tx, y=ty, seg=14)
        P.ring_band(b, 0.95, zf + 2.3, h=0.3, out=0.06, mat="planks", col=acc, x=tx, y=ty, seg=14)
    b.lamp(tx, ty, zf + 1.5, strength=1.6)
    b.cone_roof(0.95, 1.95, mat="metal", col="copper", x=tx, y=ty, z=zf + 2.6, seg=14, course=0, lip=0.0,
                section=[(1.25, -0.08), (1.02, 0.22), (0.8, 0.5), (0.62, 0.9), (0.34, 1.4), (0.0, 1.95)])
    # --- the yard round the turret's foot
    y1, xs = 6.8, W / 2
    PC.garden_wall(b, (xs, y1), (-xs, y1), h=1.6, t=0.28, gate=(xs - tx, 0.95))
    PC.garden_wall(b, (-xs, y1), (-xs, D + 0.02), h=1.6, t=0.28)
    PC.garden_wall(b, (xs, D + 0.02), (xs, y1), h=1.6, t=0.28)
    with b.at(tx, y1 - 0.14, 0, rz=180):
        PC.wood_gate(b, w=0.95, h=1.4, col=acc)
    b.beam((-2.3, y1 - 0.5, 0), (-2.3, y1 - 0.5, 2.4), w=0.08, lod=1)
    P.laundry(b, (-2.3, y1 - 0.5, 2.3), (-1.75, D + 0.1, 2.5), n=3, sag=0.2)
    L.logs(b, -2.0, D + 0.3, 0, w=1.2, h=0.7, d=0.45, rz=180)
    PC.climber(b, (tx + 1.5, ty + 0.75, 0.3), (tx + 1.42, ty + 0.7, 3.8), n=8, r=0.22, bloom=["#e8497a", "#f2a0bd"])
    # --- the pavement
    P.bench(b, 1.65, -0.42, w=1.3); L.cat(b, 2.0, -0.42, 0.48, rz=20, col="#f1ede4")
    L.flowerpot(b, -0.05, -0.32, 0, flower="#e85d3a"); L.flowerpot(b, -2.45, -0.32, 0, r=0.17, h=0.28, flower="#f4f1e4")
    with f.on(2.75, 1.75):                   # a ship's lifebuoy on the wall
        with b.at(rx=90):
            with b.detail(2):
                b.revolve([(0.2, 0.02), (0.2, 0.09), (0.34, 0.09), (0.34, 0.02)], "paint", col="#f4f1e4", seg=12)
                for q in range(4):
                    b.revolve([(0.195, 0.015), (0.195, 0.095), (0.345, 0.095), (0.345, 0.015)], "paint", col="#b5433a", seg=2, a0=90 * q + 30, a1=90 * q + 60)
