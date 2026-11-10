# The boathouse: the pilot gig lives here on her cradle, always half out of the doors, ready to be run down the slip at a shout.
# A red-oxide boarded shed on a stone base, gable to the water, white doors thrown wide above a stone slip with timber skids that
# runs down into the lagoon; an oar store leans on its side. Red boards, white trim, grey shingles; accent ivory.
from kit import *
import parts as P
import parts_h as H

META = {"name": "The Gig House", "kind": "boathouse", "lot": (9.0, 10.0)}

CX, Y0 = -0.2, 3.1          # the shed's middle, and its front wall
FZ = 0.9                    # the floor: the top of the stone base
SLOPE = 0.95 / 4.35         # the slip falls from the floor at the doors to the quay at its toe


def zs(y):
    return FZ - (Y0 - y) * SLOPE


def build(b):
    bd = b.body(6.6, 6.5, 4.2, mat="planks", col=H.OXIDE, x=CX, y=Y0 + 3.25, depth=0.16)       # x -3.5 .. 3.1, y 3.1 .. 9.6
    H.cuttable(bd.front, bd.back)
    RISE = 3.3
    # ------------------------------------------------------------------ the doorway, its dark inside and the two white leaves
    DW, DH = 4.2, 2.95
    bd.front.opening(3.3, FZ, DW, DH, pane=None, depth=0.16)
    H.lining(b, 6.3, 6.2, 3.2, x=CX, y=Y0 + 3.25, z=FZ - 0.02, floor="planks", floor_col="#8a7a66", skip="f")
    with b.detail(1):
        b.beam((CX - DW / 2 - 0.3, Y0 - 0.03, FZ + DH + 0.12), (CX + DW / 2 + 0.3, Y0 - 0.03, FZ + DH + 0.12), w=0.14, h=0.24, mat="planks", col="ivory")
        for sx in (-1, 1):
            b.beam((CX + sx * (DW / 2 + 0.09), Y0 - 0.03, FZ), (CX + sx * (DW / 2 + 0.09), Y0 - 0.03, FZ + DH), w=0.16, h=0.12, mat="planks", col="ivory", up=(0, 1, 0))
    for sx, ang in ((-1, 97), (1, 105)):
        with b.at(CX + sx * DW / 2, Y0 - 0.05, FZ + 0.03, rz=-sx * ang):
            xm = sx * DW / 4
            b.box(DW / 2 - 0.03, 0.07, DH - 0.06, "planks", col="ivory", x=xm, y=0.0, lod=0, bottom=True)
            with b.detail(2):
                for yy in (-0.045, 0.045):
                    for zz in (0.35, DH - 0.45):
                        b.beam((xm - DW / 4 + 0.06, yy, zz), (xm + DW / 4 - 0.06, yy, zz), w=0.02, h=0.14, mat="planks", col="#d9cfb8", up=(0, 0, 1), caps=False)
                    b.beam((xm - DW / 4 + 0.08, yy, 0.42), (xm + DW / 4 - 0.08, yy, DH - 0.52), w=0.14, h=0.02, mat="planks", col="#d9cfb8", up=(0, 1, 0), caps=False)
    # ------------------------------------------------------------------ gable, sides and back
    P.window(bd.front, 3.3, 4.2 + 0.75, w=0.95, h=1.05, lintel=None, bars=(1, 1))
    H.life_ring(bd.front, 0.55, 2.5)
    P.lantern(bd.front, 6.05, 2.7)
    for u in (1.7, 4.6):
        P.window(bd.left, u, 2.0, w=0.85, h=1.0, lintel=None)
    P.window(bd.back, 1.7, 2.0, w=0.85, h=1.0, lintel=None)
    P.door(bd.back, 4.9, w=0.9, h=1.95, col="ivory", frame="timber", z=0.1)
    H.louvre(bd.back, 3.3, 4.2 + 0.9, w=0.8, h=0.9)
    P.plinth(bd, h=0.9, out=0.1, col="grey")
    for wl in (bd.left, bd.right):
        H.battens(wl, col=H.OXIDE, z0=0.9, step=0.5)
    for wl in (bd.front, bd.back):
        H.battens(wl, col=H.OXIDE, z0=0.9, z1=4.2 + RISE, step=0.5, rails=(4.2,))
    with b.detail(1):      # white corner boards
        for sx in (-1, 1):
            for yy in (Y0 - 0.02, Y0 + 6.52):
                b.beam((CX + sx * 3.31, yy, 0.9), (CX + sx * 3.31, yy, 4.2), w=0.16, h=0.16, mat="planks", col="ivory")
    bd.gable(ridge="y", pitch=45, mat="shingle", eave=0.3, verge=0.25, sag=0.1, barge_col="ivory")
    P.flag(b, CX, Y0 + 0.1, 4.2 + RISE - 0.1, pole=2.3, w=1.3, h=0.55, col="stripe_red", pole_col="ivory")
    H.gull(b, CX, Y0 + 3.4, 4.2 + RISE - 0.02, rz=250)
    # ------------------------------------------------------------------ the oar store
    lt = H.leanto(b, 3.1, Y0 + 3.4, 5.0, 1.1, 1.9, rz=90, pitch=27, mat="planks", col=H.OXIDE, roof="shingle", eave=0.2, verge=0.15, plinth=0.5, plinth_col="grey")
    P.door(lt.left, 0.56, w=0.7, h=1.7, col="ivory", frame=None, z=0.36, steps=2)
    P.window(lt.front, 2.5, 1.0, w=0.8, h=0.6, lintel=None)
    H.battens(lt.front, col=H.OXIDE, z0=0.5, step=0.5)
    # ------------------------------------------------------------------ the slip
    x0, x1, yb = CX - 2.25, CX + 2.25, -1.25
    ym = 0.55
    b.quad((x0, yb, zs(yb)), (x1, yb, zs(yb)), (x1, ym, zs(ym)), (x0, ym, zs(ym)), "flagstone", col="moss", lod=0)
    b.quad((x0, ym, zs(ym)), (x1, ym, zs(ym)), (x1, Y0 + 0.3, zs(Y0 + 0.3)), (x0, Y0 + 0.3, zs(Y0 + 0.3)), "flagstone", col="sand", lod=0)
    b.quad((x0, yb, -3.0), (x1, yb, -3.0), (x1, yb, zs(yb)), (x0, yb, zs(yb)), "masonry", col="moss", lod=0)
    for sx in (-1, 1):
        xi, xo = (x0, x0 - 0.45) if sx < 0 else (x1, x1 + 0.45)
        zt0, zt1 = zs(Y0) + 0.38, zs(yb) + 0.38
        fo = [(xo, Y0, -3.0), (xo, yb, -3.0), (xo, yb, zt1), (xo, Y0, zt0)]
        fi = [(xi, yb, -3.0), (xi, Y0, -3.0), (xi, Y0, zt0), (xi, yb, zt1)]
        tp = [(xo, yb, zt1), (xi, yb, zt1), (xi, Y0, zt0), (xo, Y0, zt0)]
        en = [(xo, yb, -3.0), (xi, yb, -3.0), (xi, yb, zt1), (xo, yb, zt1)]
        for q in (fo, fi, tp, en):
            b.face(q if sx < 0 else list(reversed(q)), "masonry", col="grey" if q is not tp else "stone", lod=0)
    b.footprint(x0 - 0.45, yb, x1 + 0.45, Y0, 1.3)
    with b.detail(1):      # timber skids
        for dx in (-0.75, 0.75):
            b.beam((CX + dx, yb + 0.1, zs(yb + 0.1) + 0.06), (CX + dx, Y0 + 0.25, zs(Y0 + 0.25) + 0.06), w=0.16, h=0.12, mat="timber", col="greyoak")
    # ------------------------------------------------------------------ the gig on her cradle
    yc = 1.85
    ang = math.degrees(math.atan(SLOPE))
    with b.at(CX, yc, zs(yc) + 0.3, rz=-90, ry=ang):
        H.hull(b, L=5.4, beam=1.7, depth=0.72, col="!#f4eee0", trim="!#2f4f8f", stations=8, strakes=4, thwarts=3)
        with b.detail(1):
            for xx in (-1.5, 1.2):
                b.beam((xx, -0.8, -0.14), (xx, 0.8, -0.14), w=0.16, h=0.18, mat="timber", col="greyoak")
                for sy in (-1, 1):
                    b.beam((xx, sy * 0.72, -0.1), (xx, sy * 0.5, 0.22), w=0.1, mat="timber", col="greyoak")
        with b.detail(2):
            for sy in (-0.28, 0.25):
                b.tube((-1.9, sy, 0.5), (1.5, sy * 0.8, 0.56), r=0.028, mat="planks", col="#d9c7a3", n=4)
    # ------------------------------------------------------------------ either side of the slip
    H.net_drape(b, (-3.72, 3.9, 2.9), (-3.72, 8.3, 2.9), drop=1.8, sag=0.12, col=H.NET)
    H.pots(b, -3.85, 2.3, rz=10, n=5)
    H.mooring_post(b, x0 - 0.22, -0.9, zs(-0.9) + 0.3, h=1.3, gull_on=True)
    H.mooring_post(b, x1 + 0.22, -0.6, zs(-0.6) + 0.3, h=1.2)
    H.rope_coil(b, x1 + 0.9, 1.0, r=0.32)
    P.bench(b, 3.55, 2.75, w=1.4)
    H.buoy(b, 3.9, 0.4, col="!#d9a431", stripe="!#2c2a2a")
    P.barrel(b, -3.3, 0.9, r=0.27, h=0.72)
