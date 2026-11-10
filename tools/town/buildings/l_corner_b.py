# The tea house on the round corner: built that way, they say, so that the gossip could see both streets at once from the bow windows.
# Corner house, streets to the front and the right: its corner swept round in a quarter circle from the pavement to the eaves, the door in the curve; a slate hipped roof that turns the corner as part of a cone.
# Peach plaster on a dressed-stone shop storey, grey slate with lead rolls; accent teal.
from kit import *
import parts as P
import parts_l as L
import parts_m as PM

META = {"name": "The Round Corner", "kind": "shop", "lot": (7.5, 8.0), "terrace": True, "fronts": ["front", "right"]}


def build(b):
    acc = "teal"
    x0, x1, D = -3.45, 3.25, 7.7           # the side street runs down the right
    W, cx = x1 - x0, (x0 + x1) / 2
    H0, H = 3.3, 5.6
    top = H0 + H
    # the roof first: the corner radius is chosen so that the slate courses run on round the cone
    pitch, eS, eP = 40.0, 0.38, 0.12       # eaves to the streets, to the neighbours
    tp = math.tan(rad(pitch))
    run = W / 2 + eS
    hs = run / max(1, round(run / math.cos(rad(pitch)) / 0.42))
    R = 7 * hs - eS
    Cx, Cy = x1 - R, R

    def storey(z, h, mat, col):
        with b.at(x0, 0, z):
            fw = b.wall(Cx - x0, h, mat, col)
        with b.at(x1, Cy, z, rz=90):
            rw = b.wall(D - Cy, h, mat, col)
        with b.at(x1, D, z, rz=180):
            bw = b.wall(W, h, mat, col)
        with b.at(x0, D, z, rz=270):
            lw = b.wall(D, h, mat, col)
        return fw, rw, bw, lw, b.round(R, h, mat=mat, col=col, x=Cx, y=Cy, z=z, seg=20, foot=False)

    b.footprint(x0, 0, x1, D, top)
    # --- the shop storey
    fw, rw, bw, lw, rg = storey(0.0, H0, "ashlar", "warm")
    P.plinth(L.Walls(b, [fw, rw, bw, lw]), h=0.3, mat="ashlar", col="grey")
    P.door(rg, 45, w=1.1, h=2.25, arch=0.5, z=0.17, col=acc, frame="stone", steps=1)
    P.lantern(rg, 17, 2.3)
    P.round_base(b, R, h=0.3, out=0.07, mat="ashlar", col="grey", seg=20, ring=rg)
    L.shopfront(fw, 0.4, fw.w - 0.35, h=2.7, z=0.3, col=acc, lights=4, riser=0.45)
    L.shopfront(rw, 0.35, 3.0, h=2.7, z=0.3, col=acc, lights=3, riser=0.45)
    P.door(rw, 4.55, w=0.9, h=2.05, z=0.17, col=acc, frame="stone", steps=1)
    P.awning(fw, fw.w / 2 + 0.03, 2.6, w=3.7, out=1.05, drop=0.5, cols=("#3a9a96", "linen"))
    with b.detail(1):
        P.ring_band(b, R, H0 - 0.16, h=0.24, out=0.08, x=Cx, y=Cy, seg=20)
    L.band_on(fw, H0 - 0.16, h=0.24, out=0.08); L.band_on(rw, H0 - 0.16, h=0.24, out=0.08)
    # --- two plastered storeys
    fu, ru, bu, lu, ru_ = storey(H0, H, "plaster", "peach")
    for z, hh in ((0.9, 1.3), (3.75, 1.1)):
        for a in (22, 68):
            P.window(ru_, a, z, w=0.7, h=hh, bars=(1, 2))
        for u, bx in ((1.15, True), (3.3, False)):
            P.window(fu, u, z, w=0.85, h=hh, shutters=acc, box=bx and z < 2)
        for u, bx in ((1.2, False), (3.1, True), (4.9, False)):
            P.window(ru, u, z, w=0.8, h=hh, shutters=acc, box=bx and z < 2)
    P.window(lu, 3.0, 3.8, w=0.6, h=0.9); P.window(bu, 2.4, 3.8, w=0.6, h=0.9); P.window(bu, 5.0, 3.8, w=0.6, h=0.9)
    P.exposed(lu, "corners", n=8)
    L.sign(fu, 0.3, 0.8, emblem="teapot", col=acc, board="ivory")
    # --- the roof
    zt = W / 2 * tp
    zs, zp = -eS * tp, -eP * tp
    T0, T1, Cc = (cx, W / 2, zt), (cx, D - W / 2, zt), (Cx, Cy, R * tp)
    with b.at(0, 0, top):
        kw = dict(mat="slate", thick=0.14)
        L.roof_face(b, [(x0 - eP, -eS, zs), (Cx, -eS, zs), Cc, T0, (x0 - eP, -eP, zp)], rim=(0, 4), **kw)
        L.roof_face(b, [(x1 + eS, Cy, zs), (x1 + eS, D + eP, zs), (x1 + eP, D + eP, zp), T1, T0, Cc], rim=(0, 1), **kw)
        L.roof_face(b, [(x1 + eP, D + eP, zp), (x0 - eP, D + eP, zp), T1], rim=(0,), **kw)
        L.roof_face(b, [(x0 - eP, D + eP, zp), (x0 - eP, -eP, zp), T0, T1], rim=(0,), **kw)
        PM.cone_part(b, R, R * tp, a0=0, a1=90, mat="slate", x=Cx, y=Cy, seg=7, eave=eS, section=[(R + eS, zs), (0.0, R * tp)], course=0.42, lip=0.045)
        for p0, p1 in ((Cc, T0), ((x0 - eP, -eP, zp), T0), ((x0 - eP, D + eP, zp), T1), ((x1 + eP, D + eP, zp), T1), (T0, T1)):
            L.ridge_roll(b, vlerp(p0, p1, 0.04), p1, "metal", "lead", w=0.17, h=0.1)
        L.ball(b, Cc[0], Cc[1], Cc[2] - 0.02, r=0.16, mat="metal", col="lead")
    P.dormer(b, -1.7, 1.25, top + 1.25 * tp - 0.1, w=1.0, h=0.95, depth=1.4, face=0, roof="slate", col="peach", frame="ivory")
    P.dormer(b, x1 - 1.25, 4.9, top + 1.25 * tp - 0.1, w=1.0, h=0.95, depth=1.4, face=90, roof="slate", col="peach", frame="ivory")
    P.chimney(b, x0 + 0.42, 3.0, top + 0.05, 3.4, w=0.66, d=0.9, mat="brick", pots=2)
    P.chimney(b, cx - 0.9, D - 0.42, top + 0.05, 3.2, w=0.9, d=0.66, mat="brick", pots=2)
    # --- the pavement: a table for two under the awning, bay trees by the door
    PM.table(b, -1.2, -0.72, 0, cloth="linen")
    PM.chair(b, -1.85, -0.72, 0, rz=90); PM.chair(b, -0.55, -0.72, 0, rz=270)
    P.planter(b, Cx + (R + 0.33) * math.sin(rad(15)), Cy - (R + 0.33) * math.cos(rad(15)), 0, w=0.4, d=0.4, bush=True)
    L.cat(b, -2.9, -0.4, 0, rz=30, col="#8c8580")
