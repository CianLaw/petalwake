# The Butter Cross: Larkhaven's covered market, standing free in the middle of the square since before the town hall.
# Farmers set out under it at dawn; the market clerk weighs, tolls and gossips from his booth at the east end.
# Massing: twelve stout oak posts on stone feet under one great hipped roof whose eaves kick out and come low, a
# louvred lantern with a fish vane on the ridge; open on every side but for the clerk's little boxed-in booth.
# Materials: dark oak, pale stone feet, a flagged floor one step up, terracotta tiles; mustard paint on the booth.
from kit import *
import parts as P
import parts_m as Q

META = {"name": "The Butter Cross market hall", "kind": "market", "lot": (12.0, 8.0)}

A = "mustard"
CY = 4.0                    # centre line (the hall is centred on x = 0)
XS = [-5.0 + 2.0 * i for i in range(6)]
YR = (CY - 3.0, CY + 3.0)  # the two rows of posts
ZF, ZP = 0.22, 3.42          # floor, top of the posts
SEC = [(0.0, 0.0), (1.0, 0.5), (3.2, 3.25)]   # roof section: a flat kick at the eaves, then steep


def underside(b, w, d, z, thick=0.14):
    """The boarded underside of the hipped roof (the kit's roof is only skinned on top)."""
    hw, hd = w / 2, d / 2
    loop = lambda ins, zz: [(-max(hw - ins, 0), -max(hd - ins, 0), zz), (max(hw - ins, 0), -max(hd - ins, 0), zz), (max(hw - ins, 0), max(hd - ins, 0), zz),
                            (-max(hw - ins, 0), max(hd - ins, 0), zz)]
    with b.at(0, CY, z - thick):
        for (ra, za), (rb, zb) in zip(SEC, SEC[1:]):
            A_, B_ = loop(ra, za), loop(rb, zb)
            for i in range(4):
                j = (i + 1) % 4
                b.face((A_[j], A_[i], B_[i], B_[j]), "planks", col="darkoak")


def scales(b, x, y, z):
    with b.at(x, y, z):
        with b.detail(2):
            b.beam((0, 0, 0), (0, 0, -0.9), w=0.02, mat="metal", col="iron", caps=False)
            b.beam((-0.5, 0, -0.9), (0.5, 0, -0.9), w=0.03, mat="metal", col="brass", caps=False)
            for sx in (-1, 1):
                b.beam((sx * 0.5, 0, -0.9), (sx * 0.5, 0, -1.4), w=0.012, mat="metal", col="iron", caps=False)
                with b.at(sx * 0.5, 0, -1.45):
                    b.revolve([(0.0, 0.0), (0.2, 0.05), (0.22, 0.06), (0.0, 0.02)], "metal", col="brass", seg=8)


def build(b):
    # --- the floor: flags one step up, on the hidden foundation
    b.box(10.8, 6.8, 3.0 + ZF, "masonry", col="warm", x=0, y=CY, z=-3.0, cap="flagstone", capcol="sand")
    with b.detail(1):
        b.box(11.4, 7.4, 0.1, "ashlar", col="stone", x=0, y=CY, z=0.0)
    # --- the frame: posts on stone feet, wall plates, tie beams, braces, king posts and principal rafters
    zr = ZP + 0.4                                   # the roof's wall line
    HW, HD = 5.2, 3.2                               # its half extents there
    sec = lambda t: 0.5 * t if t <= 1.0 else 0.5 + (t - 1.0) * 2.75 / 2.2
    under = lambda t: zr + sec(t) - 0.3             # just under the boarding, t = distance in from the wall line
    oak = dict(mat="timber", col="darkoak", caps=False)
    for x in XS:
        for y in YR:
            b.box(0.64, 0.64, 0.56, "ashlar", col="stone", x=x, y=y, z=ZF, taper=0.72)
            b.beam((x, y, ZF + 0.56), (x, y, ZP), w=0.3, mat="timber", col="darkoak", lod=0)
        b.beam((x, YR[0] - 0.15, ZP + 0.13), (x, YR[1] + 0.15, ZP + 0.13), w=0.24, h=0.26, mat="timber", col="darkoak", lod=0)
        rx = min(HD, HW - abs(x))                   # how far up this frame goes before it meets the hip
        with b.detail(1):
            for sy in (-1, 1):
                yy = CY + sy * 3.0
                b.beam((x, yy, ZP - 0.95), (x, yy - sy * 0.85, ZP + 0.02), w=0.16, **oak)
                if rx > 1.2:                        # principal rafters follow the kick of the roof
                    pts = [(x, CY + sy * (HD - t), under(t)) for t in (0.2, 1.0, rx)]
                    b.beam(pts[0], pts[1], w=0.17, h=0.2, **oak)
                    b.beam(pts[1], pts[2], w=0.17, h=0.2, **oak)
            if rx > 1.2:
                b.beam((x, CY, ZP + 0.24), (x, CY, under(rx) + 0.05), w=0.2, **oak)
                if rx < HD:
                    b.beam((x, CY - (HD - rx), under(rx)), (x, CY + (HD - rx), under(rx)), w=0.17, h=0.2, **oak)
        if rx > 1.8:
            with b.detail(2):
                for sy in (-1, 1):
                    b.beam((x, CY + sy * 0.12, ZP + 0.26), (x, CY + sy * 1.5, under(1.7)), w=0.13, **oak)
    for y in YR:
        b.beam((XS[0] - 0.25, y, ZP + 0.14), (XS[-1] + 0.25, y, ZP + 0.14), w=0.26, h=0.28, mat="timber", col="darkoak", lod=0)
        with b.detail(1):
            for i, x in enumerate(XS):
                for sx in (-1, 1):
                    if 0 <= i + sx < len(XS):
                        b.beam((x, y, ZP - 0.95), (x + sx * 0.8, y, ZP + 0.02), w=0.15, **oak)
    with b.detail(1):                               # hip rafters from the corners to the ends of the ridge
        for sx in (-1, 1):
            for sy in (-1, 1):
                pts = [(sx * (HW - t), CY + sy * (HD - t), under(t)) for t in (0.2, 1.0, HD)]
                b.beam(pts[0], pts[1], w=0.17, h=0.2, **oak)
                b.beam(pts[1], pts[2], w=0.17, h=0.2, **oak)
    with b.detail(2):                               # purlins
        for sy in (-1, 1):
            b.beam((-(HW - 2.0), CY + sy * (HD - 1.9), under(1.9)), (HW - 2.0, CY + sy * (HD - 1.9), under(1.9)), w=0.14, **oak)
    # --- the roof, boarded underneath, and the lantern on its ridge
    rise = b.loop_roof(10.4, 6.4, x=0, y=CY, z=zr, section=SEC, mat="tiles", eave=0.72, course=0.42)
    underside(b, 10.4, 6.4, zr)
    lan = b.body(1.5, 1.1, 1.5, mat="planks", col="darkoak", x=0, y=CY, z=zr + rise - 0.75, foot=False)
    for wl in lan.walls:
        wl.opening(wl.w / 2, 0.85, wl.w - 0.4, 0.5, pane="paint", pane_col=Q.DARK, depth=0.1)
        Q.louvres(wl, wl.w / 2, 0.85, wl.w - 0.4, 0.5, col=A, n=3)
    lt = b.loop_roof(1.5, 1.1, x=0, y=CY, z=zr + rise + 0.75, section=[(0, 0), (0.25, 0.14), (0.55, 0.95)], mat="tiles", eave=0.32, course=0.3, thick=0.08)
    Q.ball(b, 0, CY, zr + rise + 0.75 + lt - 0.1, r=0.12, mat="metal", col="copper")
    Q.weathercock(b, 0, CY, zr + rise + 0.75 + lt + 0.05, h=1.3, shape="fish", size=1.0)
    # --- the clerk's booth, boxed in under the east end
    bo = b.body(1.9, 2.6, 2.95, mat="plaster", col="cream", x=3.95, y=CY + 1.55, z=ZF, foot=False)
    for wl in bo.walls:
        P.timber_frame(wl, braces="auto", w=0.13)
    P.door(bo.front, 0.65, w=0.8, h=1.9, z=0.02, col=A, frame="timber")
    P.lantern(bo.front, 1.45, 2.0)
    Q.counter(bo.left, 1.3, 1.0, w=1.2, h=1.0, col=A, goods="parcels", shelf=0.3)
    P.window(bo.right, 1.3, 1.0, w=0.7, h=1.0, lintel="timber")
    P.window(bo.back, 1.0, 1.0, w=0.7, h=1.0, lintel="timber", box=True)
    b.box(2.04, 2.74, 0.1, "planks", col="darkoak", x=3.95, y=CY + 1.55, z=ZF + 2.95, bottom=True)
    # --- market day
    Q.stall(b, -3.7, CY - 1.7, ZF, cols=("stripe_red", "linen"), goods="fruit")
    Q.stall(b, -1.0, CY - 1.6, ZF, cols=("stripe_blue", "linen"), goods="loaves")
    Q.stall(b, -2.6, CY + 1.9, ZF, rz=180, cols=("stripe_green", "linen"), goods="pots")
    Q.stall(b, 0.6, CY + 1.9, ZF, rz=180, cols=("stripe_yellow", "linen"), goods="cloth", canopy=False)
    Q.produce(b, 1.5, CY - 2.0, ZF, cols=["#7fae3f"])
    Q.produce(b, 2.2, CY - 2.0, ZF, cols=["#e88a2a"])
    Q.produce(b, 1.85, CY - 1.35, ZF, cols=["#d8432e", "#f0c53a"])
    P.barrel(b, -4.55, CY + 2.3, ZF)
    P.barrel(b, -4.45, CY + 1.65, ZF, r=0.26, h=0.7)
    P.sack(b, 2.6, CY + 0.2, ZF)
    P.sack(b, 2.9, CY - 0.35, ZF, r=0.26)
    P.crate(b, 3.5, CY - 2.3, ZF, s=0.55, rz=15)
    P.crate(b, 4.15, CY - 2.2, ZF, s=0.6, rz=-10)
    scales(b, XS[3], CY - 0.9, ZP + 0.02)
    for x in (XS[1], XS[4]):
        with b.detail(2):
            b.beam((x, CY + 0.9, ZP + 0.02), (x, CY + 0.9, ZP - 0.25), w=0.02, mat="metal", col="iron", caps=False)
            b.box(0.18, 0.18, 0.24, "glow", col="#ffd88a", x=x, y=CY + 0.9, z=ZP - 0.5, bottom=True)
        b.lamp(x, CY + 0.9, ZP - 0.4)
    Q.bunting(b, (XS[0], YR[0] - 0.16, ZP - 0.1), (XS[2], YR[0] - 0.16, ZP - 0.1), sag=0.3, cols=(A, "linen", "stripe_red"))
    Q.bunting(b, (XS[3], YR[0] - 0.16, ZP - 0.1), (XS[5], YR[0] - 0.16, ZP - 0.1), sag=0.3, cols=("stripe_blue", "linen", A))
    Q.cat(b, -4.55, CY + 2.3, ZF + 0.8, rz=200, col="#5a5754")
    Q.pigeon(b, 2.0, CY + 0.1, zr + rise + 0.02, rz=40)
    Q.pigeon(b, -1.6, CY - 0.05, zr + rise + 0.02, rz=-110)
