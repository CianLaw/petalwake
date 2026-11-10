# The notary's: his stair climbs a stone tower of its own at the corner of the house, and he lets the broom post use the leads on top.
# A broad three-storey house with its eaves to the street and cart doors below; at its right-hand corner a square stair tower in dressed stone, its little windows stepping up with the stair, flat-topped inside a parapet.
# Sand plaster, pale ashlar tower, terracotta tiles; accent orange.
from kit import *
import parts as P
import parts_l as L
import parts_c as PC
import parts_m as PM

META = {"name": "The Notary's Stair", "kind": "house", "lot": (5.8, 9.0), "terrace": True, "lean": (0.001, 0.001)}


def build(b):
    W, D, acc = 5.3, 8.1, "orange"
    H0, top = 3.2, 8.7
    c = W / 2
    g = b.body(W, D, top, mat="plaster", col="sand")
    P.plinth(g, h=0.5)
    f = g.front
    # --- the house front: cart doors, a stone-mullioned window, two little ones under the eaves
    P.door(f, 1.4, w=2.1, h=2.55, arch=0.55, col=acc, frame="stone", double=True, depth=0.3)
    PM.mullioned(f, 1.4, H0 + 0.75, w=1.9, h=1.5, lights=3, transoms=1)
    for u in (0.8, 2.0):
        P.window(f, u, 6.1 + 0.75, w=0.65, h=0.95, shutters=acc)
    L.band_on(f, H0 - 0.05, h=0.16, u1=2.8)
    L.sign(f, 0.26, H0 + 2.75, emblem="feather", col="navy", board="ivory", round_board=True)
    # --- sides and back
    P.window(g.left, 2.2, 6.9, w=0.6, h=0.9); P.window(g.right, 5.6, 6.9, w=0.6, h=0.9)
    P.window(g.left, D / 2, top + 0.8, w=0.6, h=0.9, arch=0.3); P.window(g.right, D / 2, top + 0.7, w=0.55, h=0.8)
    P.exposed(g.left, "corners", n=8)
    k = g.back
    P.door(k, 1.3, w=0.9, h=2.0, z=0.17, col=acc, frame="stone", steps=1)
    P.window(k, 3.9, 1.1, w=1.0, h=1.3)
    for z in (H0 + 0.9, 6.1 + 0.8):
        P.window(k, 1.35, z, w=0.8, h=1.15, shutters=acc); P.window(k, 3.9, z, w=0.8, h=1.15, shutters=acc, box=(z < 5))
    PC.climber(b, (c - 0.5, D + 0.12, 0.2), (c - 0.45, D + 0.12, 4.6), n=9, r=0.26, bloom=["#f4f1e4"])
    # --- the stair tower
    tw_w, tw_d, tw_h = 2.5, 2.6, 13.3
    tx, ty = c - tw_w / 2, tw_d / 2 - 0.3
    tw = PC.tbody(b, tw_w, tw_d, tw_h, inset=0.12, mat="ashlar", col="warm", x=tx, y=ty)
    P.plinth(tw, h=0.7, col="grey")
    P.door(tw.front, 1.25, w=0.9, h=2.1, arch=0.45, z=0.34, col=acc, frame="stone", steps=2, lamp=True)
    for i, z in enumerate((3.3, 5.35, 7.4, 9.45, 11.3)):
        P.window(tw.front, 0.78 if i % 2 == 0 else 1.72, z, w=0.5, h=0.95, arch=0.25, bars=(0, 1))
    P.window(tw.right, 1.3, 7.0, w=0.5, h=0.9, arch=0.25); P.window(tw.right, 1.3, 10.6, w=0.5, h=0.9, arch=0.25)
    P.window(tw.left, 1.3, 11.3, w=0.5, h=0.9, arch=0.25)
    P.window(tw.back, 1.25, 11.6, w=0.5, h=0.9, arch=0.25)
    PC.tquoins(tw, corners="fr", z0=0.7, col="stone")
    PC.tband(tw, 8.6)
    hw, hd = tw.half(tw_h)
    out = 0.2
    pw, pd = 2 * (hw + out), 2 * (hd + out)
    fz = tw_h + 0.22
    with b.at(tx, ty, tw_h):
        PM.corbel_table(b, 2 * hw, 2 * hd, 0.0, out=out + 0.02, h=0.42, cw=0.24, spacing=0.6)
        b.box(pw, pd, 0.22, "ashlar", col="stone", bottom=True, cap="flagstone", capcol="sand")
        with b.at(z=0.22):
            L.parapet(b, [(-pw / 2, -pd / 2), (-0.62, -pd / 2)], h=0.8, t=0.24, mat="ashlar", col="stone")
            L.parapet(b, [(0.62, -pd / 2), (pw / 2, -pd / 2), (pw / 2, pd / 2), (-pw / 2, pd / 2), (-pw / 2, -pd / 2)], h=0.8, t=0.24, mat="ashlar", col="stone")
            for sx in (-1, 1):
                for sy in (-1, 1):
                    L.ball(b, sx * (pw / 2 - 0.12), sy * (pd / 2 - 0.12), 0.88, r=0.14)
            P.landing_mark(b, 0.8)
            L.trapdoor(b, pw / 2 - 0.62, pd / 2 - 0.66, 0.0, w=0.62, d=0.66)
            PC.vane(b, -pw / 2 + 0.12, pd / 2 - 0.12, 1.1, h=1.5, shape="quill", cardinals=False)
    b.pad(tx, ty, fz, radius=0.85, face=0, name="Notary's leads")
    # --- the roof: built round the tower (its front slope stops against the tower's flank)
    e, v, tp = 0.45, 0.04, math.tan(rad(40))
    yr = D / 2
    rise = yr * tp
    n = max(1, round((yr + e) / math.cos(rad(40)) / 0.42))
    hs = (yr + e) / n
    ys = -e + math.ceil((tw_d - 0.3 - 0.25 + e) / hs) * hs          # a course line just inside the tower's back wall
    xt = tx - tw_w / 2 + 0.1
    zr = top + rise
    L.roof_face(b, [(-c - v, -e, top - e * tp), (xt, -e, top - e * tp), (xt, yr, zr), (-c - v, yr, zr)], "tiles", "#ead9cd", thick=0.16, rim=(0, 3))
    L.roof_face(b, [(xt, ys, top + ys * tp), (c + v, ys, top + ys * tp), (c + v, yr, zr), (xt, yr, zr)], "tiles", "#ead9cd", thick=0.16, rim=(1,))
    L.roof_face(b, [(c + v, D + e, top - e * tp), (-c - v, D + e, top - e * tp), (-c - v, yr, zr), (c + v, yr, zr)], "tiles", "#ead9cd", thick=0.16, rim=(0, 1, 3))
    L.ridge_roll(b, (-c - v, yr, zr), (c + v, yr, zr), col="#ead9cd")
    for wl in (g.left, g.right):
        L.wall_top(wl, [[(0.0, top), (D, top), (D / 2, top + rise - 0.03)]])
    PC.stack(b, -c + 0.42, yr, top + 2.2, 2.9, w=0.72, d=0.6, flues=2, style="diagonal")
    P.dormer(b, -1.45, 1.2, top + 1.02, w=0.9, h=0.85, depth=1.3, face=0, col="sand", frame="ivory")
    P.dormer(b, 0.9, D - 1.2, top + 1.02, w=0.9, h=0.85, depth=1.3, face=180, col="sand", frame="ivory")
    # --- the lane
    for sx in (-0.85, 0.85):
        P.planter(b, tx + sx, -0.3 - 0.42, 0, w=0.42, d=0.42, bush=True)
    P.barrel(b, -c + 0.35, -0.4)
    L.cat(b, tx + 0.2, -0.75, 0.34, rz=30, col="#3b3632")
