"""Petalwake town kit, farm-district layer (prefix f_): what the lone buildings out in the flower
meadows are made of. Everything here is written with the kit primitives; conventions as in parts.py
(positions on a wall the wall's natural way, heights above the wall's base, detail levels 0 / 1 / 2).

Shapes:     loft, ribbon, pent / pent_roof (lean-tos), window / door (true to width on tapering round towers)
Thatch:     thatch_gable, thatch_ridge, soft_hip (round-shouldered hipped thatch), eyebrow
Mills:      sails
Doors:      half_door (stable door), barn_doors, slit
Timberwork: deck, fence, picket, gate, ladder_to, rope, net
Stone:      drystone, staddle, trough
Farm life:  hay, hive, wheel, cart, logs, tool, bucket, churn, stovepipe, fire_basket, candle, boat
Living:     bloom, flowers, meadow, spire_flower, sunflower, fruit_tree, veg_row, dove, cat
"""
import math

from kit import C, Ring, lerp, rad, shade, vadd, vcross, vlen, vmul, vnorm, vsub
import parts as P

STRAW = "#fff4d6"         # tint of fresh thatch (the thatch texture is already golden)
OLDSTRAW = "#d9d2bd"      # weathered thatch
HAY = "#fbeeb0"
DARKIN = "#2b241f"        # the dark inside of a barn seen through a door
BLOOMS = ["#e8497a", "#f2a0bd", "#f4f1e4", "#f5c842", "#b08ae6", "#e85d3a", "#ffffff", "#7fa8e8", "#f07fa8"]
HAZEL = "#8a6a48"


def _paint(c):
    """A flat paint colour from a palette name or '#rrggbb'."""
    c = C(c)
    return (c[0], c[1], c[2], 1.0)


# ---------------------------------------------------------------------------------------- shapes
def loft(b, rows, mat, col=None, lod=0, smooth=True, closed=False, flip=False, cols=None, wind=0.0, sm=None, uvo=None):
    """Skin a surface through rows of points (all rows the same length). Seen from outside, points run to the
    right along a row and the rows go upward (flip=True if yours go the other way). closed=True joins each row's
    last point to its first. cols = optional tint per span between rows."""
    if sm is None:
        sm = b.sm() if smooth else 0
    uo, vo = uvo or b.uvo()
    n = len(rows[0])
    m = n if closed else n - 1
    us = []
    for r in rows:
        acc = [0.0]
        for j in range(1, m + 1):
            acc.append(acc[-1] + math.dist(r[j - 1], r[j % n]))
        us.append(acc)
    vs = [0.0]
    k = n // 3
    for i in range(1, len(rows)):
        vs.append(vs[-1] + max(math.dist(rows[i][k], rows[i - 1][k]), math.dist(rows[i][0], rows[i - 1][0]), 1e-4))
    for i in range(len(rows) - 1):
        c = cols[i] if cols else col
        for j in range(m):
            j2 = (j + 1) % n
            p = [rows[i][j], rows[i][j2], rows[i + 1][j2], rows[i + 1][j]]
            uv = [(uo + us[i][j], vo + vs[i]), (uo + us[i][j + 1], vo + vs[i]), (uo + us[i + 1][j + 1], vo + vs[i + 1]), (uo + us[i + 1][j], vo + vs[i + 1])]
            if flip:
                p.reverse(); uv.reverse()
            b.face(p, mat, uv=uv, col=c, lod=lod, sm=sm, wind=wind)


def ribbon(b, p0, p1, w=0.03, mat="cloth", col=None, lod=2, up=(0, 0, 1), wind=0.0):
    """A flat two-sided strip from p0 to p1 (a cheap cord, lath or strap): w across, its faces looking along `up`."""
    a = vsub(p1, p0)
    s = vcross(a, up)
    if vlen(s) < 1e-6:
        s = vcross(a, (1, 0, 0))
    s = vmul(vnorm(s), w / 2)
    q = [vsub(p0, s), vsub(p1, s), vadd(p1, s), vadd(p0, s)]
    b.face(q, mat, col=col, lod=lod, wind=wind)
    b.face(list(reversed(q)), mat, col=shade(col, 0.85), lod=lod, wind=wind)


def _true(s, op):
    """Give an opening on a tapering round tower its real width (the kit measures widths where the wall has its
    mean radius, so high windows come out narrower than their frames). Harmless on other walls."""
    if isinstance(s, Ring):
        c = (op["u0"] + op["u1"]) / 2
        half = op["w"] / 2 * s.rref / max(s.radius(op["z"] + op["h"] / 2), 1e-6)
        op["u0"], op["u1"] = c - half, c + half
    return op


def window(s, pos, z, **kw):
    """parts.window, true to width on a tapering round tower."""
    return _true(s, P.window(s, pos, z, **kw))


def door(s, pos, **kw):
    """parts.door, true to width on a tapering round tower."""
    return _true(s, P.door(s, pos, **kw))


def _wall_top(wall, pts):
    """Add a piece of wall above a flat wall's top edge (pts in the wall's (u, z) plane), same stuff and colour."""
    def deco():
        b = wall.b
        uo, vo = wall.uvo
        b.face([(p[0], 0.0, p[1]) for p in pts], wall.mat, col=wall.col, lod=wall.lod, uv=[(uo + p[0], vo + p[1]) for p in pts])
    wall.add(deco)


def pent(body, rise, high="back"):
    """Shape a Body's walls for a single-slope (pent) roof that climbs `rise` toward its 'back', 'front', 'left' or
    'right' wall: that wall is made taller and the two walls beside it get sloping tops."""
    order = {"back": (body.back, body.right, body.left), "front": (body.front, body.left, body.right),
             "right": (body.right, body.front, body.back), "left": (body.left, body.back, body.front)}[high]
    tall, rising, falling = order           # `rising`: its right end (seen from outside) is the high one
    _wall_top(tall, [(0.0, tall.h), (tall.w, tall.h), (tall.w, tall.h + rise), (0.0, tall.h + rise)])
    _wall_top(rising, [(0.0, rising.h), (rising.w, rising.h), (rising.w, rising.h + rise)])
    _wall_top(falling, [(0.0, falling.h), (falling.w, falling.h), (0.0, falling.h + rise)])


def pent_roof(body, rise, high="back", z=None, over=0.25, **kw):
    """Roof a Body with one slope climbing `rise` toward the given wall (and shape its walls to suit); `over` =
    how far the slope carries on past the high wall. Other arguments as Building.gable_roof (mat, col, eave ...)."""
    b = body.b
    pent(body, rise, high)
    turn = {"back": 0.0, "front": 180.0, "right": 270.0, "left": 90.0}[high]
    w, d = (body.w, body.d) if high in ("back", "front") else (body.d, body.w)
    with b.at(body.x, body.y, body.top if z is None else z, rz=turn):
        # (kit: with half=True the slope ends on the given y instead of being centred on it, so give the high edge)
        b.gable_roof(w, d + over, math.degrees(math.atan2(rise, d)), ridge="x", half=True, x=0.0, y=d / 2 + over, z=0.0, **kw)


# ---------------------------------------------------------------------------------------- thatch
def _cushion(run, pitch, bulge):
    rise = run * math.tan(rad(pitch))
    return [(0.0, 0.0), (run * 0.3, rise * (0.3 + bulge * 0.9)), (run * 0.65, rise * (0.65 + bulge)), (run, rise)]


def thatch_ridge(b, length, pitch=45.0, drop=0.62, sag=0.0, col=None, off=0.07, step=0.44, lod=1, liggers=True):
    """The raised ridge cap of a thatched roof with its scalloped lower edge and hazel rods. Frame: origin on the
    middle of the ridge line, x along it. sag = how far the middle of the ridge dips (as given to the roof)."""
    col = C(col if col is not None else STRAW)
    p = rad(pitch)
    n = max(2, round(length / step))
    sg = (lambda x: -sag * (1 - (2 * x / length) ** 2)) if sag else (lambda x: 0.0)

    def pt(x, s, sgn, o=off):
        return (x, sgn * (s * math.cos(p) + o * math.sin(p)), -s * math.sin(p) + o * math.cos(p) + sg(x))

    for sgn in (-1, 1):
        for i in range(n):
            xa, xb = -length / 2 + length * i / n, -length / 2 + length * (i + 1) / n
            xm = (xa + xb) / 2
            ta, tb = (xa, 0.0, off / math.cos(p) + 0.04 + sg(xa)), (xb, 0.0, off / math.cos(p) + 0.04 + sg(xb))
            poly = [pt(xa, drop, sgn), pt(xm, drop + 0.15, sgn), pt(xb, drop, sgn), tb, ta]
            b.face(poly if sgn < 0 else list(reversed(poly)), "thatch", col=shade(col, b.r(0.9, 1.06)), lod=lod)
            for q in ([pt(xa, drop, sgn, 0.0), pt(xm, drop + 0.15, sgn, 0.0), pt(xm, drop + 0.15, sgn), pt(xa, drop, sgn)],
                      [pt(xm, drop + 0.15, sgn, 0.0), pt(xb, drop, sgn, 0.0), pt(xb, drop, sgn), pt(xm, drop + 0.15, sgn)]):
                b.face(q if sgn < 0 else list(reversed(q)), "thatch", col=shade(col, 0.58), lod=2)
        for xe, fl in ((-length / 2, False), (length / 2, True)):      # close the ends over the verges
            q = [pt(xe, drop, sgn, 0.0), pt(xe, drop, sgn), (xe, 0.0, off / math.cos(p) + 0.04 + sg(xe)), (xe, 0.0, sg(xe))]
            b.face(q if (sgn < 0) != fl else list(reversed(q)), "thatch", col=shade(col, 0.7), lod=lod)
        if liggers:
            m = 4 if sag else 1
            for s in (drop * 0.28, drop * 0.8):
                for i in range(m):
                    xa, xb = -length / 2 + 0.05 + (length - 0.1) * i / m, -length / 2 + 0.05 + (length - 0.1) * (i + 1) / m
                    b.beam(pt(xa, s, sgn, off + 0.015), pt(xb, s, sgn, off + 0.015), w=0.04, mat="planks", col=HAZEL, lod=2, caps=False)


def thatch_gable(body, pitch=50.0, ridge="x", col=None, eave=0.5, verge=0.38, thick=0.32, sag=0.0, bulge=0.07, course=0.55, lip=0.07,
                 cap=True, cap_col=None, lod=0):
    """Thatch a Body with a gabled roof: thick, slightly cushion-shaped, with a raised scalloped ridge.
    Returns the rise of the ridge."""
    b = body.b
    col = C(col if col is not None else STRAW)
    span = body.d if ridge == "x" else body.w
    sec = _cushion(span / 2, pitch, bulge)
    rise = body.gable(ridge=ridge, section=sec, mat="thatch", col=col, eave=eave, verge=verge, thick=thick, course=course, lip=lip, sag=sag,
                      soffit="thatch", soffit_col=shade(col, 0.6), barge=False, ridge_roll=False, lod=lod)
    if cap:
        length = (body.w if ridge == "x" else body.d) + 2 * verge
        top = math.degrees(math.atan2(sec[-1][1] - sec[-2][1], sec[-1][0] - sec[-2][0]))
        with b.at(body.x, body.y, body.top + rise, rz=0.0 if ridge == "x" else 90.0):
            thatch_ridge(b, length + 0.06, top, sag=sag, col=cap_col if cap_col is not None else shade(col, 0.84))
    return rise


def eave_pitch(pitch, bulge=0.07):
    """The slope (degrees) of a cushion-shaped thatch roof just above its eave, for seating eyebrows on it."""
    return math.degrees(math.atan(math.tan(rad(pitch)) * (0.3 + bulge * 0.9) / 0.3))


def hip_lift(pitch=50.0, eave=0.5, corner=0.35, shoulder=0.75, bulge=0.07):
    """How far a soft_hip roof has to sit above the wall tops so that the square corners of the walls stay inside its
    rounded ones (what soft_hip uses when lift is not given; add it to z for anything you stand on that roof's eave)."""
    i = -0.4142 * (corner + shoulder * eave) / (1.4142 + 0.4142 * shoulder)
    return -i * math.tan(rad(pitch)) * (0.3 + bulge * 0.9) / 0.3 + 0.06


def soft_hip(b, w, d, pitch=50.0, mat="thatch", col=None, x=0.0, y=0.0, z=0.0, eave=0.5, thick=0.32, course=0.52, lip=0.07, corner=0.35,
             shoulder=0.75, bulge=0.07, nc=3, section=None, lift=None, lod=0, cap=0.6, cap_col=None, soffit_col=None, under=False):
    """A hipped roof with rounded shoulders over a w by d block whose wall tops are at z (centred on x, y): the
    soft loaf shape of thatch. corner = how round the eave corners are, shoulder = how much rounder the hips get
    per metre climbed inward; cap = width of the raised ridge cap (0 for none). under=True gives it an inside
    (for an open barn on posts, which is looked at from below). Returns the rise."""
    col = C(col if col is not None else STRAW)
    run = min(w, d) / 2
    if section is None:
        section = _cushion(run, pitch, bulge)
    if lift is None:
        lift = hip_lift(pitch, eave, corner, shoulder, bulge)
    rise = section[-1][1]
    s0 = (section[1][1] - section[0][1]) / max(section[1][0] - section[0][0], 1e-6)
    prof = [(-eave, -eave * s0)] + list(section[1:])
    stepped, _ = b._courses(prof, course, lip)
    hw, hd = w / 2, d / 2

    def loop(inset, zz, cr=None):
        a, bq = max(hw - inset, 0.0), max(hd - inset, 0.0)
        if cr is None:                     # (never quite round: a straight run that dies out leaves odd slivers)
            cr = min(corner + shoulder * (inset + eave), 0.85 * a, 0.85 * bq)
        cr = min(cr, a, bq)
        arcs = []
        for (sx, sy, a0) in ((-1, -1, 180.0), (1, -1, 270.0), (1, 1, 0.0), (-1, 1, 90.0)):
            cx, cy = sx * (a - cr), sy * (bq - cr)
            arcs.append([(cx + cr * math.cos(rad(a0 + 90.0 * i / nc)), cy + cr * math.sin(rad(a0 + 90.0 * i / nc)), zz) for i in range(nc + 1)])
        pts = []
        for k in range(4):                      # each corner's arc, then two stations along the straight run to the next
            pts += arcs[k]                      # (the stations keep their place along the side from loop to loop, so the quads do not skew)
            p, q = arcs[k][-1], arcs[(k + 1) % 4][0]
            L = math.dist(p, q)
            s_ = min((a if k % 2 == 0 else bq) / 3.0, L / 2) / L if L > 1e-6 else 0.0
            pts += [(lerp(p[0], q[0], t), lerp(p[1], q[1], t), zz) for t in (0.5 - s_, 0.5 + s_)]
        return pts

    def sec_z(inset):
        for (ra, za), (rb, zb) in zip(section, section[1:]):
            if inset <= rb + 1e-9:
                return za + (zb - za) * (inset - ra) / max(rb - ra, 1e-9)
        return rise

    uo, vo = b.uvo()
    with b.at(x, y, z + lift):
        acc = 0.0
        for k in range(len(stepped) - 1):
            (ra, za), (rb, zb) = stepped[k], stepped[k + 1]
            loft(b, [loop(ra, za), loop(rb, zb)], mat, col=shade(col, b.r(0.88, 1.07)), lod=lod, closed=True, uvo=(uo, vo + acc))
            acc += math.hypot(rb - ra, zb - za)
        # the cut edge of the eave (undercut) and the flat underside back to the wall
        (r0_, z0_) = prof[0]
        sc = soffit_col if soffit_col is not None else shade(col, 0.58)
        bot = loop(r0_ + 0.14, z0_ - thick)
        loft(b, [bot, loop(stepped[0][0], stepped[0][1])], mat, col=sc, lod=lod, closed=True)
        loft(b, [loop(0.0, z0_ - thick, cr=0.0), bot], mat, col=shade(sc, 0.8), lod=lod, closed=True, smooth=False)
        if under:
            zb, zi = z0_ - thick + 0.03, rise - 0.4
            c0, c1, c2, c3 = (-hw, -hd, zb), (hw, -hd, zb), (hw, hd, zb), (-hw, hd, zb)
            if hw >= hd:
                rl, rr_ = (-(hw - hd), 0.0, zi), (hw - hd, 0.0, zi)
                inner = [(c0, rl, rr_, c1), (c1, rr_, c2), (c2, rr_, rl, c3), (c3, rl, c0)]
            else:
                rf, rb = (0.0, -(hd - hw), zi), (0.0, hd - hw, zi)
                inner = [(c0, rf, c1), (c1, rf, rb, c2), (c2, rb, c3), (c3, rb, rf, c0)]
            for q in inner:
                b.face(q, mat, col=shade(col, 0.42), lod=lod)
        if cap and cap > 0:
            cc = C(cap_col if cap_col is not None else shade(col, 0.84))
            i0 = max(run - cap, 0.0)
            o = 0.075
            rows = [loop(i0, sec_z(i0) + 0.0), loop(i0, sec_z(i0) + o), loop((i0 + run) / 2, sec_z((i0 + run) / 2) + o + 0.05), loop(run, rise + o + 0.2)]
            loft(b, rows, mat, cols=[shade(cc, 0.62), cc, shade(cc, 1.04)], lod=1, closed=True)
            lg = loop(i0 + cap * 0.3, sec_z(i0 + cap * 0.3) + o + 0.03)
            for i in range(len(lg)):
                p0, p1 = lg[i], lg[(i + 1) % len(lg)]
                if math.dist(p0, p1) > 0.05:
                    b.beam(p0, p1, w=0.04, mat="planks", col=HAZEL, lod=2, caps=False)
    return rise + lift


def eyebrow(b, w=2.1, h=0.62, pitch=58.0, mat="thatch", col=None, wall="plaster", wall_col="cream", frame="ivory", over=0.34, thick=0.2,
            n=10, lod=1, win=(0.62, 0.4), droop=0.1):
    """An eyebrow dormer: a soft hump in a thatched roof over a little window. Frame: the origin on the wall line
    (where the roof meets the wall top) under the middle of the dormer, x along the eave, +y into the roof, z up;
    the roof climbs toward +y at `pitch` degrees there (see eave_pitch)."""
    col = C(col if col is not None else STRAW)
    tp = math.tan(rad(pitch))
    xs = [-w / 2 + w * i / n for i in range(n + 1)]
    hh = [h * min(1.0, 1.2 * math.cos(math.pi * xx / w) ** 1.6) for xx in xs]
    k = [min(1.0, (v / h) ** 0.6) for v in hh]
    F = [(xx, -over, -over * tp + v + (over * tp - droop) * kk) for xx, v, kk in zip(xs, hh, k)]
    Mi = [(xx, 0.0, v + 0.02) for xx, v in zip(xs, hh)]
    Bk = [(xx, (v + 0.12) / tp, v) for xx, v in zip(xs, hh)]
    Fb = [(p[0], p[1] + 0.05, p[2] - thick * (0.25 + 0.75 * kk)) for p, kk in zip(F, k)]
    Sb = [(p[0], 0.0, max(p[2] + 0.03, -0.02)) for p in Fb]
    with b.detail(lod):
        loft(b, [F, Mi, Bk], mat, col=shade(col, 0.97))
        loft(b, [Fb, F], mat, col=shade(col, 0.6))
        loft(b, [Sb, Fb], mat, col=shade(col, 0.5), smooth=False)
        uo, vo = b.uvo()
        for i in range(n):
            if max(Sb[i][2], Sb[i + 1][2]) < 0.03:
                continue
            q = [(xs[i], 0.0, 0.0), (xs[i + 1], 0.0, 0.0), (xs[i + 1], 0.0, max(Sb[i + 1][2], 0.0)), (xs[i], 0.0, max(Sb[i][2], 0.0))]
            b.face(q, wall, col=wall_col, uv=[(uo + p[0], vo + p[2]) for p in q])
        ww, wh = win
        b.quad((-ww / 2, -0.02, 0.07), (ww / 2, -0.02, 0.07), (ww / 2, -0.02, 0.07 + wh), (-ww / 2, -0.02, 0.07 + wh), "glass")
    with b.detail(2):
        for (p0, p1) in (((-ww / 2, -0.035, 0.07), (-ww / 2, -0.035, 0.07 + wh)), ((ww / 2, -0.035, 0.07), (ww / 2, -0.035, 0.07 + wh)),
                         ((-ww / 2, -0.035, 0.07), (ww / 2, -0.035, 0.07)), ((-ww / 2, -0.035, 0.07 + wh), (ww / 2, -0.035, 0.07 + wh)),
                         ((0, -0.035, 0.07), (0, -0.035, 0.07 + wh))):
            b.beam(p0, p1, w=0.05, h=0.04, mat="planks", col=frame, caps=False, up=(0, 1, 0))


# ---------------------------------------------------------------------------------------- mills
def sails(b, n=4, length=8.0, width=1.8, lead=0.34, inner=1.3, bars=0.42, col="ivory", stock_col="darkoak", cloth="linen", reef=0.3,
          weather=(20.0, 5.0), stock=0.2, hub=0.55):
    """A set of lattice windmill sails round the origin, to be made inside `with b.spin(...)`: they lie in the local
    x-z plane and turn about local -y (which points out of the front of the mill; seen from the front they go
    anticlockwise). Each sail has a stock along its length, a lattice frame `width` wide on its trailing side from
    `inner` out to the tip, a leading board on the other side, a twist (weather: degrees at the heel and the tip)
    and cloth spread over the outer part (reef = the fraction left bare at the heel; cloth=None for bare frames)."""
    N = max(3, round((length - 0.12 - inner) / bars))
    zs = [inner + (length - 0.12 - inner) * i / N for i in range(N + 1)]
    yb = -(stock / 2 + 0.03)

    def pt(s, z, yo=0.0):
        t = (z - inner) / max(length - inner, 1e-6)
        th = rad(lerp(weather[0], weather[1], min(max(t, 0.0), 1.0)))
        return (s * math.cos(th), yb + s * math.sin(th) + yo, z)

    for k in range(n):
        with b.at(ry=360.0 * k / n):
            b.beam((0, 0, 0), (0, 0, length * 0.52), w=stock, h=stock, mat="timber", col=stock_col, lod=0, up=(1, 0, 0), caps=False)
            b.beam((0, 0, length * 0.52), (0, 0, length), w=stock * 0.7, h=stock * 0.7, mat="timber", col=stock_col, lod=0, up=(1, 0, 0))
            for i, z in enumerate(zs):
                b.beam(pt(-lead, z), pt(width, z), w=0.05, h=0.045, mat="planks", col=col, lod=2 if i not in (0, N) else 1, caps=False, up=(0, 0, 1))
            for s, ld in ((width, 1), (width * 0.5, 2), (-lead, 1)):
                for i in range(0, N, 2):
                    j = min(i + 2, N)
                    b.beam(pt(s, zs[i]), pt(s, zs[j]), w=0.05, h=0.05, mat="planks", col=col, lod=ld, caps=False, up=(0, 1, 0))
            for i in range(0, N, 4):                       # the leading board
                j = min(i + 4, N)
                q = [pt(-lead, zs[i], -0.03), pt(-0.04, zs[i], -0.03), pt(-0.04, zs[j], -0.03), pt(-lead, zs[j], -0.03)]
                b.face(q, "planks", col=col, lod=1)
                b.face(list(reversed(q)), "planks", col=shade(col, 0.85), lod=1)
            if cloth:
                j0 = min(max(round(reef * N), 1), N - 1)
                cc = C(cloth)
                seq = list(range(j0, N, 3)) + [N]
                for a, c in zip(seq, seq[1:]):
                    q = [pt(0.07, zs[a]), pt(width - 0.04, zs[a]), pt(width - 0.04, zs[c]), pt(0.07, zs[c])]
                    b.face(q, "cloth", col=cc, lod=0)
                    b.face(list(reversed(q)), "cloth", col=shade(cc, 0.86), lod=0)
                jp = max(j0 - 3, 0)                        # the sword point: the heel corner pulled back along the stock
                q = [pt(0.07, zs[jp]), pt(width - 0.04, zs[j0]), pt(0.07, zs[j0])]
                b.face(q, "cloth", col=cc, lod=0)
                b.face(list(reversed(q)), "cloth", col=shade(cc, 0.86), lod=0)
    b.box(hub, hub * 0.8, hub, "metal", col="iron", x=0, y=0, z=-hub / 2, bottom=True, lod=0)       # the poll end
    with b.at(rx=90):
        b.revolve([(0.09, hub * 0.4), (0.13, hub * 0.4 + 0.1), (0.0, hub * 0.4 + 0.2)], "metal", col="iron", seg=6, lod=1)


# ---------------------------------------------------------------------------------------- doors and slits
def half_door(s, pos, w=1.1, h=2.0, z=0.0, col="green", top="open", frame="timber", depth=None, inside=DARKIN, split=0.52):
    """A stable door in two leaves: the lower one shut, the upper 'open' (swung back against the wall), 'ajar',
    'shut', or a number of degrees it stands open. Cuts the opening (bottom at z)."""
    b = s.b
    u = s.U(pos)
    op = _true(s, P._cut(s, u, z, w, h, depth=depth, pane="planks", pane_col=inside))
    d = op["d"]

    def leaf(lw, lh, face=-1.0):
        b.box(lw, 0.05, lh, "planks", col=col, x=lw / 2, y=0.0, z=0.0, lod=1, bottom=True)
        with b.detail(2):
            yy = face * 0.035
            for zz in (lh * 0.16, lh * 0.84):
                b.beam((0.02, yy, zz), (lw - 0.02, yy, zz), w=0.03, h=0.09, mat="planks", col=shade(col, 0.78), up=(0, 0, 1), caps=False)
                b.beam((0.0, yy * 1.5, zz), (lw * 0.45, yy * 1.5, zz), w=0.015, h=0.05, mat="metal", col="iron", up=(0, 0, 1), caps=False)
            b.beam((0.04, yy, lh * 0.16), (lw - 0.04, yy, lh * 0.84), w=0.03, h=0.08, mat="planks", col=shade(col, 0.78), up=(0, 1, 0), caps=False)

    def deco():
        with s.onu(u, z):
            hl = h * split
            with b.at(-w / 2 + 0.02, min(d * 0.4, 0.1), 0.02):
                leaf(w - 0.04, hl - 0.03)
            if top == "shut":
                with b.at(-w / 2 + 0.02, min(d * 0.4, 0.1), hl + 0.02):
                    leaf(w - 0.04, h - hl - 0.04)
            else:
                swing = -float(top) if isinstance(top, (int, float)) else (-158.0 if top == "open" else -62.0)
                with b.at(-w / 2 - 0.02, -0.03, hl + 0.02, rz=swing):
                    leaf(w - 0.04, h - hl - 0.04, face=1.0)
            if frame == "timber":
                with b.detail(1):
                    for sgn in (-1, 1):
                        b.beam((sgn * (w / 2 + 0.07), -0.02, 0), (sgn * (w / 2 + 0.07), -0.02, h + 0.14), w=0.14, h=0.1, mat="timber", col="darkoak", up=(0, 1, 0))
                    b.beam((-w / 2 - 0.2, -0.02, h + 0.08), (w / 2 + 0.2, -0.02, h + 0.08), w=0.1, h=0.16, mat="timber", col="darkoak", up=(0, 0, 1))
            elif frame == "stone":
                b.box(w + 0.5, 0.14, 0.24, "ashlar", col="stone", x=0, y=-0.02, z=h, lod=1)

    s.add(deco)
    return op


def barn_doors(s, pos, w=3.2, h=3.6, z=0.0, col="green", swing=(12.0, 74.0), arch=0.0, frame="timber", depth=None, inside=DARKIN):
    """Great double doors: cuts the opening and hangs two ledged-and-braced leaves, each swung outward by the
    given angle (degrees; left leaf, right leaf)."""
    b = s.b
    u = s.U(pos)
    op = _true(s, P._cut(s, u, z, w, h, arch=arch, depth=depth, pane="planks", pane_col=inside))
    hs = h - arch

    def leaf(lw, face):
        b.box(lw, 0.07, hs - 0.06, "planks", col=col, x=lw / 2, y=0.0, z=0.03, lod=1, bottom=True)
        with b.detail(2):
            yy = face * 0.05
            for zz in (hs * 0.1, hs * 0.5, hs * 0.9):
                b.beam((0.02, yy, zz), (lw - 0.02, yy, zz), w=0.04, h=0.14, mat="planks", col=shade(col, 0.78), up=(0, 0, 1), caps=False)
                b.beam((0.0, yy * 1.4, zz), (lw * 0.5, yy * 1.4, zz), w=0.02, h=0.07, mat="metal", col="iron", up=(0, 0, 1), caps=False)
            for (za, zb) in ((hs * 0.1, hs * 0.5), (hs * 0.5, hs * 0.9)):
                b.beam((0.06, yy, za), (lw - 0.06, yy, zb), w=0.04, h=0.12, mat="planks", col=shade(col, 0.78), up=(0, 1, 0), caps=False)

    def deco():
        with s.onu(u, z):
            with b.at(-w / 2, -0.04, 0.0, rz=-swing[0]):
                leaf(w / 2 - 0.02, -1.0)
            with b.at(w / 2, -0.04, 0.0, rz=180.0 + swing[1]):
                leaf(w / 2 - 0.02, 1.0)
            if frame == "timber":
                with b.detail(1):
                    for sgn in (-1, 1):
                        b.beam((sgn * (w / 2 + 0.11), -0.03, 0), (sgn * (w / 2 + 0.11), -0.03, hs + 0.2), w=0.22, h=0.14, mat="timber", col="darkoak", up=(0, 1, 0))
                    if arch < 1e-4:
                        b.beam((-w / 2 - 0.36, -0.03, h + 0.13), (w / 2 + 0.36, -0.03, h + 0.13), w=0.14, h=0.26, mat="timber", col="darkoak", up=(0, 0, 1))

    s.add(deco)
    return op


def slit(s, pos, z, w=0.14, h=0.9, depth=None, col=DARKIN):
    """A narrow ventilation slit (barns) or arrow loop (towers)."""
    return _true(s, P._cut(s, s.U(pos), z, w, h, depth=depth, pane="planks", pane_col=col))


# ---------------------------------------------------------------------------------------- timberwork
def deck(b, w, d, x=0.0, y=0.0, z=0.0, thick=0.1, col="greyoak", edge="darkoak", joists=0.8, lod=0):
    """A boarded platform w by d centred on (x, y) with its walking surface at z: boards, edge beams and joists."""
    with b.at(x, y, z):
        b.box(w, d, thick, "planks", col=col, z=-thick, bottom=True, lod=lod)
        with b.detail(1):
            for sy in (-1, 1):
                b.beam((-w / 2, sy * (d / 2 - 0.07), -thick - 0.09), (w / 2, sy * (d / 2 - 0.07), -thick - 0.09), w=0.14, h=0.18, mat="timber", col=edge, up=(0, 0, 1))
            if joists:
                n = max(1, round(w / joists))
                for i in range(n + 1):
                    xx = -w / 2 + 0.07 + (w - 0.14) * i / n
                    b.beam((xx, -d / 2 + 0.02, -thick - 0.26), (xx, d / 2 - 0.02, -thick - 0.26), w=0.12, h=0.16, mat="timber", col=edge, up=(0, 0, 1))


def _p3(p):
    return (p[0], p[1], p[2] if len(p) > 2 else 0.0)


def fence(b, pts, h=1.05, rails=(0.42, 0.88), col="greyoak", post=0.11, every=1.8, lod=1, skirt=0.8, mat="planks"):
    """A post-and-rail field fence along ground points [(x, y[, z]), ...]."""
    pts = [_p3(p) for p in pts]
    for i, (a, c) in enumerate(zip(pts, pts[1:])):
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        n = max(1, round(L / every))
        for k in range(0 if i == 0 else 1, n + 1):
            p = (lerp(a[0], c[0], k / n), lerp(a[1], c[1], k / n), lerp(a[2], c[2], k / n))
            b.beam((p[0], p[1], p[2] - skirt), (p[0] + b.r(-0.03, 0.03), p[1] + b.r(-0.03, 0.03), p[2] + h + b.r(0.02, 0.1)), w=post, mat=mat, col=col, lod=lod)
        for rz_ in rails:
            b.beam((a[0], a[1], a[2] + rz_), (c[0], c[1], c[2] + rz_), w=0.04, h=0.1, mat=mat, col=col, lod=lod if rz_ == rails[-1] else 2, caps=False)


def picket(b, pts, h=0.95, col="ivory", every=0.17, post=0.09, lod=1, skirt=0.6):
    """A painted picket fence along ground points [(x, y[, z]), ...]."""
    pts = [_p3(p) for p in pts]
    for i, (a, c) in enumerate(zip(pts, pts[1:])):
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        ang = math.degrees(math.atan2(c[1] - a[1], c[0] - a[0]))
        with b.at(a[0], a[1], a[2], rz=ang):
            for xx in ([0.0, L] if i == 0 else [L]):
                b.box(post, post, h + 0.12 + skirt, "planks", col=col, x=xx, z=-skirt, lod=lod)
            for zz in (h * 0.28, h * 0.78):
                b.beam((0, 0, zz), (L, 0, zz), w=0.03, h=0.07, mat="planks", col=col, lod=lod, caps=False)
            n = max(2, int(L / every))
            for k in range(1, n):
                b.box(0.075, 0.02, h * b.r(0.94, 1.0), "planks", col=col, x=L * k / n, y=-0.025, z=0.06, lod=2, sides="fb")


def gate(b, w=1.4, h=1.05, col="greyoak", bars=5, kind="field", lod=1):
    """A gate hung at the origin of the current frame and lying along +x (turn it with b.at(rz=...) to open it).
    kind = 'field' (bars and a brace) or 'picket'."""
    with b.detail(lod):
        for xx in (0.04, w - 0.04):
            b.beam((xx, 0, 0.08), (xx, 0, h + (0.12 if xx < 0.1 else 0.0)), w=0.07, h=0.09, mat="planks", col=col)
        if kind == "field":
            for i in range(bars):
                zz = 0.16 + (h - 0.22) * (i / (bars - 1)) ** 0.85
                b.beam((0.04, 0, zz), (w - 0.04, 0, zz), w=0.03, h=0.075, mat="planks", col=col, caps=False)
            b.beam((0.06, 0.02, 0.18), (w - 0.06, 0.02, h - 0.08), w=0.03, h=0.07, mat="planks", col=col, caps=False, up=(0, 1, 0))
        else:
            for zz in (h * 0.28, h * 0.78):
                b.beam((0.04, 0, zz), (w - 0.04, 0, zz), w=0.03, h=0.07, mat="planks", col=col, caps=False)
            n = max(2, int(w / 0.17))
            for k in range(1, n):
                t = k / n
                b.box(0.075, 0.02, h * (0.9 + 0.12 * math.sin(math.pi * t)), "planks", col=col, x=w * t, y=-0.025, z=0.08, sides="fb")


def ladder_to(b, p0, p1, w=0.42, col="greyoak", rung=0.3, lod=2):
    """A ladder from the ground point p0 to the top point p1 (any direction)."""
    a = vsub(p1, p0)
    L = vlen(a)
    side = vcross(a, (0, 0, 1))
    side = vmul(vnorm(side) if vlen(side) > 1e-6 else (1, 0, 0), w / 2)
    with b.detail(lod):
        for sgn in (-1, 1):
            b.beam(vadd(p0, vmul(side, sgn)), vadd(p1, vmul(side, sgn)), w=0.055, mat="planks", col=col)
        n = max(2, int(L / rung))
        for i in range(1, n):
            q = vadd(p0, vmul(a, i / n))
            b.beam(vsub(q, side), vadd(q, side), w=0.035, mat="planks", col=col, caps=False)


def rope(b, p0, p1, sag=0.0, r=0.018, col="#8a7a66", n=6, lod=2, wind=0.0):
    """A rope from p0 to p1, hanging `sag` low in the middle."""
    pt = lambda t: (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t) - sag * 4 * t * (1 - t))
    m = n if sag else 1
    for i in range(m):
        b.beam(pt(i / m), pt((i + 1) / m), w=r * 2, mat="cloth", col=col, lod=lod, caps=False, wind=wind)


def net(b, p0, p1, drop=1.4, sag=0.22, col="#5f8279", nx=7, nz=3, floats="#e08a3c", lod=2, belly=0.18):
    """A fishing net hung to dry between two points: a head rope, a lattice of cords and cork floats."""
    head = lambda t: (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t) - sag * 4 * t * (1 - t))
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    nxv, nyv = -dy / L, dx / L
    rng = b.rng
    G = []
    for i in range(nx + 1):
        hp = head(i / nx)
        col_ = []
        for j in range(nz + 1):
            t = j / nz
            bl = belly * math.sin(math.pi * t) * math.sin(math.pi * i / nx)
            col_.append((hp[0] + nxv * bl, hp[1] + nyv * bl, hp[2] - drop * t * (0.86 + 0.14 * math.sin(i * 1.7))))
        G.append(col_)
    for i in range(nx):
        b.beam(head(i / nx), head((i + 1) / nx), w=0.03, mat="cloth", col="#8a7a66", lod=1, caps=False)
        for j in range(nz):
            ribbon(b, G[i][j], G[i + 1][j + 1], w=0.022, col=col, lod=lod, up=(nxv, nyv, 0), wind=0.15 * (j + 1) / nz)
            ribbon(b, G[i + 1][j], G[i][j + 1], w=0.022, col=col, lod=lod, up=(nxv, nyv, 0), wind=0.15 * (j + 1) / nz)
        ribbon(b, G[i][nz], G[i + 1][nz], w=0.03, col=shade(col, 0.8), lod=lod, up=(nxv, nyv, 0), wind=0.15)
    if floats:
        for i in range(1, nx):
            hp = head(i / nx)
            bloom(b, hp[0], hp[1], hp[2] - 0.03, r=0.06, col=floats if i % 3 else "#f2ead8", lod=lod, wind=0.0)


# ---------------------------------------------------------------------------------------- stone
def drystone(b, pts, h=1.1, t=0.42, mat="masonry", col="warm", cope=True, skirt=2.0, lod=0, batter=0.8):
    """A free-standing field wall along ground points [(x, y), ...]: battered rubble with a row of cope stones
    (and a hidden foundation, as it may stand on a slope)."""
    rng = b.rng
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        ang = math.degrees(math.atan2(by - ay, bx - ax))
        with b.at(ax, ay, 0, rz=ang):
            b.box(L + t * batter, t, h, mat, col=col, x=L / 2, y=0, ty=batter, lod=lod)
            b.box(L + t, t, skirt, mat, col=shade(col, 0.85), x=L / 2, y=0, z=-skirt, top=False, lod=lod)
            if cope:
                n = max(2, int(L / 0.36))
                for i in range(n):
                    b.stone(L / n * 0.9, t * batter * 1.04, 0.2 * rng.uniform(0.75, 1.3), mat=mat, col=shade(col, 0.95), lod=1 if i % 2 == 0 else 2,
                            x=L * (i + 0.5) / n, y=0, z=h - 0.02, jitter=0.22)


def staddle(b, x=0.0, y=0.0, z=0.0, h=0.78, r=0.38, col="grey", seg=7, lod=0):
    """A staddle stone: the mushroom-shaped stone that keeps rats out of a granary. Its top is at z + h."""
    with b.at(x, y, z, rz=b.r(0, 50)):
        b.revolve([(r * 0.7, -0.6), (r * 0.66, 0.0), (r * 0.42, h * 0.7), (r * 0.42, h * 0.72)], "ashlar", col=col, seg=seg, lod=lod, smooth=False)
        b.revolve([(r * 0.4, h * 0.72), (r, h * 0.74), (r * 0.94, h * 0.86), (r * 0.5, h), (0.0, h)], "ashlar", col=shade(col, 1.06), seg=seg, lod=lod)


def trough(b, x=0.0, y=0.0, z=0.0, w=1.6, d=0.55, h=0.5, rz=0.0, mat="ashlar", col="grey", water=True, lod=1):
    """A stone (or with mat='planks' a wooden) drinking trough, w long."""
    t = 0.09
    with b.at(x, y, z, rz=rz):
        with b.detail(lod):
            b.box(w, d, h, mat, col=col, top=False)
            O = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
            I = [(-w / 2 + t, -d / 2 + t), (w / 2 - t, -d / 2 + t), (w / 2 - t, d / 2 - t), (-w / 2 + t, d / 2 - t)]
            for i in range(4):
                j = (i + 1) % 4
                b.quad((O[i][0], O[i][1], h), (O[j][0], O[j][1], h), (I[j][0], I[j][1], h), (I[i][0], I[i][1], h), mat, col=shade(col, 1.05))
                b.quad((I[i][0], I[i][1], h), (I[j][0], I[j][1], h), (I[j][0], I[j][1], h - 0.2), (I[i][0], I[i][1], h - 0.2), mat, col=shade(col, 0.7))
            b.quad((I[0][0], I[0][1], h - 0.1), (I[1][0], I[1][1], h - 0.1), (I[2][0], I[2][1], h - 0.1), (I[3][0], I[3][1], h - 0.1),
                   "water" if water else mat, col="#7fb6c2" if water else shade(col, 0.6))


# ---------------------------------------------------------------------------------------- farm life
def hay(b, x=0.0, y=0.0, z=0.0, rx=1.2, ry=None, h=1.0, col=HAY, lod=1, seg=8, rough=0.24):
    """A heap of loose hay about 2 rx across and h high, sitting on z."""
    ry = rx if ry is None else ry
    b.blob(rx, ry, h * 0.74, mat="thatch", col=col, x=x, y=y, z=z + h * 0.28, lod=lod, seg=seg, rings=4, rough=rough, bottom=False)


def hive(b, x=0.0, y=0.0, z=0.0, r=0.26, h=0.48, col="#f6e3b0", face=0.0, hackle=False, lod=2):
    """A straw skep beehive standing on z, its flight hole toward local -y (turned by `face`)."""
    with b.at(x, y, z, rz=face):
        k = 4
        prof = [(r * 0.9, 0.0)]
        for i in range(k):
            a0, a1 = rad(84.0 * i / k), rad(84.0 * (i + 1) / k)
            prof.append((r * math.cos((a0 + a1) / 2) * 1.05, h * math.sin((a0 + a1) / 2)))
            prof.append((r * math.cos(a1) * 0.95, h * math.sin(a1)))
        prof.append((0.0, h * 1.0))
        b.revolve(prof, "thatch", col=col, seg=7, lod=lod, cols=[shade(col, 0.86 + 0.14 * (i % 2)) for i in range(len(prof) - 1)])
        b.quad((-0.045, -r * 0.93, 0.0), (0.045, -r * 0.93, 0.0), (0.045, -r * 0.96, 0.07), (-0.045, -r * 0.96, 0.07), "paint", col="black", lod=lod)
        if hackle:
            b.revolve([(r * 1.18, h * 0.5), (r * 0.5, h * 1.05), (0.04, h * 1.5)], "thatch", col=shade(col, 0.8), seg=7, lod=lod)


def wheel(b, r=0.6, w=0.09, spokes=10, mat="planks", col="darkoak", tyre="iron", lod=1, hub=0.11):
    """A spoked cart wheel centred on the origin of the current frame, its axle along local x."""
    with b.at(ry=90):
        with b.detail(lod):
            b.revolve([(r - 0.09, -w / 2), (r, -w / 2), (r, w / 2), (r - 0.09, w / 2), (r - 0.09, -w / 2)], mat, col=col, seg=12, smooth=False,
                      cols=[col, tyre, col, shade(col, 0.8)] if tyre else None)
            b.revolve([(hub, -w * 0.8), (hub * 0.8, w * 0.9), (0.0, w * 1.0)], mat, col=col, seg=6)
            b.revolve([(0.0, -w * 0.9), (hub, -w * 0.8)], mat, col=col, seg=6)
        with b.detail(2):
            for k in range(spokes):
                a = 2 * math.pi * k / spokes
                b.beam((hub * 0.8 * math.sin(a), -hub * 0.8 * math.cos(a), 0), ((r - 0.07) * math.sin(a), -(r - 0.07) * math.cos(a), 0), w=0.05, h=0.045,
                       mat=mat, col=col, caps=False, up=(0, 0, 1))


def cart(b, x=0.0, y=0.0, z=0.0, rz=0.0, L=2.3, W=1.15, r=0.62, col="greyoak", wheel_col="darkoak", load=None, paint=None):
    """A two-wheeled farm cart, its shafts resting on the ground toward local -y. load = 'hay', 'sacks' or None;
    paint = colour of the side boards (default: bare wood)."""
    side = paint or col
    shaft = 1.7
    tip = math.degrees(math.asin(min((r - 0.02) / (L * 0.45 + shaft), 0.9)))
    with b.at(x, y, z, rz=rz):
        for sx in (-1, 1):
            with b.at(sx * (W / 2 + 0.1), 0, r):
                wheel(b, r, col=wheel_col)
        with b.detail(1):
            b.beam((-W / 2 - 0.12, 0, r), (W / 2 + 0.12, 0, r), w=0.09, mat="timber", col="darkoak")
        with b.at(0, 0, r, rx=tip):
            with b.detail(1):
                b.box(W, L, 0.07, "planks", col=col, y=L * 0.05, z=0.1, bottom=True)
                for sx in (-1, 1):
                    b.box(0.05, L, 0.4, "planks", col=side, x=sx * (W / 2 - 0.02), y=L * 0.05, z=0.17, bottom=True)
                    b.beam((sx * (W / 2 - 0.08), -L * 0.45, 0.13), (sx * (W / 2 - 0.2), -L * 0.45 - shaft, 0.13), w=0.07, mat="planks", col=col)
                b.box(W, 0.05, 0.4, "planks", col=side, y=L * 0.55, z=0.17, bottom=True)
            with b.detail(2):
                for yy, lean in ((-L * 0.45, -0.3), (L * 0.55, 0.3)):
                    for sx in (-1, 1):
                        b.beam((sx * (W / 2 - 0.06), yy, 0.17), (sx * (W / 2 - 0.02), yy + lean, 1.05), w=0.05, mat="planks", col=col)
                    for zz in (0.62, 1.0):
                        t = (zz - 0.17) / 0.88
                        b.beam((-W / 2 + 0.04, yy + lean * t, zz), (W / 2 - 0.04, yy + lean * t, zz), w=0.04, mat="planks", col=col, caps=False)
            if load == "hay":
                hay(b, 0, L * 0.05, 0.2, rx=W * 0.62, ry=L * 0.6, h=1.0, lod=1)
            elif load == "sacks":
                for (sx_, sy_) in ((-0.25, -0.5), (0.25, -0.3), (-0.2, 0.3), (0.22, 0.6)):
                    P.sack(b, sx_, L * 0.05 + sy_, 0.17, r=0.27)


def logs(b, x=0.0, y=0.0, z=0.0, n=4, L=0.9, r=0.11, rz=0.0, rows=3, col="#b08f6e", lod=2):
    """A stack of firewood: logs lying along local x, n wide at the bottom, `rows` high."""
    with b.at(x, y, z, rz=rz):
        for j in range(rows):
            m = n - j
            for i in range(max(m, 0)):
                yy = (i - (m - 1) / 2) * 2 * r * 1.02
                x0 = b.r(-0.06, 0.06)
                b.tube((-L / 2 + x0, yy, r + j * r * 1.75), (L / 2 + x0, yy, r + j * r * 1.75), r=r * b.r(0.85, 1.08), mat="planks", col=shade(col, b.r(0.8, 1.1)), lod=lod, n=6, caps=True)


def tool(b, x=0.0, y=0.0, z=0.0, kind="fork", h=1.55, lean=0.22, rz=0.0, col="#c9b089", lod=2):
    """A long-handled tool standing at (x, y, z) and leaning toward local +y (against a wall behind it).
    kind = 'fork', 'rake', 'spade', 'broom', 'crook' or 'scythe'."""
    with b.at(x, y, z, rz=rz):
        with b.detail(lod):
            top = (0.0, h * lean, h * math.sqrt(max(1 - lean * lean, 0.1)))
            d = vnorm(top)
            if kind in ("fork", "rake", "broom", "spade"):       # head on the ground, handle up
                b.beam((0, 0, 0.22), top, w=0.035, mat="planks", col=col, caps=False)
                if kind == "fork":
                    for sx in (-0.07, 0.0, 0.07):
                        b.beam((sx, -0.03, 0.0), (sx * 0.6, 0.0, 0.24), w=0.016, mat="metal", col="iron", caps=False)
                elif kind == "rake":
                    b.beam((-0.28, 0, 0.2), (0.28, 0, 0.2), w=0.04, mat="planks", col=col)
                    for i in range(6):
                        b.beam((-0.25 + 0.1 * i, 0, 0.2), (-0.25 + 0.1 * i, -0.02, 0.07), w=0.016, mat="planks", col=col, caps=False)
                elif kind == "spade":
                    b.box(0.17, 0.02, 0.26, "metal", col="iron", z=0.0, bottom=True)
                else:
                    b.revolve([(0.13, 0.0), (0.05, 0.32), (0.0, 0.34)], "thatch", col="#d9b56a", seg=5, smooth=False)
            else:
                b.beam((0, 0, 0), top, w=0.035, mat="planks", col=col, caps=False)
                if kind == "crook":
                    p1 = vadd(top, (0.0, -0.1, 0.1)); p2 = vadd(top, (0.0, -0.2, 0.02))
                    b.beam(top, p1, w=0.03, mat="planks", col=col, caps=False)
                    b.beam(p1, p2, w=0.03, mat="planks", col=col, caps=False)
                else:
                    b.beam(top, vadd(top, (0.5, -0.12, -0.14)), w=0.012, h=0.07, mat="metal", col="lead", caps=False, up=d)


def bucket(b, x=0.0, y=0.0, z=0.0, r=0.14, h=0.27, col="#c9a57a", lod=2, handle=True):
    """A wooden pail."""
    with b.at(x, y, z):
        with b.detail(lod):
            b.revolve([(r * 0.78, 0.0), (r, h)], "planks", col=col, seg=8)
            b.revolve([(r * 0.92, h), (r * 0.72, 0.03)], "planks", col=shade(col, 0.6), seg=8)
            b.disc(r * 0.74, "planks", col=shade(col, 0.5), seg=8, z=0.03)
            b.revolve([(r * 0.84, h * 0.22), (r * 0.87, h * 0.32)], "metal", col="iron", seg=8)
            if handle:
                pts = [(-r, 0, h), (-r * 0.7, 0, h + r * 0.75), (r * 0.7, 0, h + r * 0.75), (r, 0, h)]
                for a, c in zip(pts, pts[1:]):
                    b.beam(a, c, w=0.014, mat="metal", col="iron", caps=False)


def churn(b, x=0.0, y=0.0, z=0.0, s=1.0, lod=2):
    """A milk churn."""
    with b.at(x, y, z, s=s):
        with b.detail(lod):
            b.revolve([(0.15, 0.0), (0.17, 0.05), (0.17, 0.4), (0.1, 0.52), (0.11, 0.6), (0.13, 0.62), (0.0, 0.64)], "metal", col="lead", seg=8)


def stovepipe(b, x=0.0, y=0.0, z=0.0, h=1.5, r=0.085, col="iron", hat=True, lean=0.0, smoke=True, lod=1):
    """An iron stovepipe rising h from (x, y, z) with a collar and a little conical hat; breathes smoke."""
    with b.at(x, y, z, rx=lean):
        with b.detail(lod):
            b.tube((0, 0, 0), (0, 0, h), r=r, mat="metal", col=col, n=7)
            b.revolve([(r * 2.2, 0.0), (r * 1.1, 0.14)], "metal", col=col, seg=7)
            b.revolve([(r * 1.25, h * 0.6), (r * 1.25, h * 0.6 + 0.05)], "metal", col=shade(col, 1.3), seg=7)
            if hat:
                b.revolve([(r * 2.3, h + 0.07), (0.0, h + 0.22)], "metal", col=col, seg=7)
                b.disc(r * 2.3, "metal", col=shade(col, 0.7), seg=7, z=h + 0.07, down=True)
                for k in range(3):
                    a = rad(120 * k + 30)
                    b.beam((r * math.sin(a), -r * math.cos(a), h - 0.02), (r * 1.6 * math.sin(a), -r * 1.6 * math.cos(a), h + 0.08), w=0.015, mat="metal", col=col, caps=False)
        if smoke:
            b.smoke(0, 0, h + 0.35, strength=0.6)


def fire_basket(b, x=0.0, y=0.0, z=0.0, r=0.42, h=0.55, lit=True, lod=1):
    """An iron cresset: a basket of hoops and bars full of glowing embers. (x, y, z) = the middle of its bottom."""
    with b.at(x, y, z):
        with b.detail(lod):
            for (rr, zz) in ((r * 0.62, 0.0), (r * 0.9, h * 0.5), (r, h)):
                b.revolve([(rr - 0.025, zz - 0.03), (rr + 0.025, zz - 0.03), (rr + 0.025, zz + 0.03), (rr - 0.025, zz + 0.03), (rr - 0.025, zz - 0.03)],
                          "metal", col="iron", seg=8, smooth=False)
            b.disc(r * 0.62, "metal", col="iron", seg=8, z=0.0)
            b.disc(r * 0.62, "metal", col="iron", seg=8, z=-0.02, down=True)
            if lit:
                b.blob(r * 0.74, r * 0.74, h * 0.45, mat="glow", col="#ff8a2c", z=h * 0.58, seg=6, rings=3, rough=0.3)
                for k in range(4):
                    a = rad(90 * k + 20)
                    fx, fy = r * 0.3 * math.sin(a), -r * 0.3 * math.cos(a)
                    tip = (fx * 0.3, fy * 0.3, h + r * b.r(1.0, 1.7))
                    ring = [(fx + 0.13, fy, h * 0.8), (fx, fy + 0.13, h * 0.8), (fx - 0.13, fy, h * 0.8), (fx, fy - 0.13, h * 0.8)]
                    for i in range(4):
                        b.face((ring[i], ring[(i + 1) % 4], tip), "glow", col="#ffd070", wind=(0.0, 0.0, 0.7))
        with b.detail(2):
            for k in range(8):
                a = rad(45 * k + 22.5)
                b.beam((r * 0.62 * math.sin(a), -r * 0.62 * math.cos(a), 0), (r * 1.02 * math.sin(a), -r * 1.02 * math.cos(a), h + 0.1), w=0.03, mat="metal", col="iron", caps=False)
        if lit:
            b.lamp(0, 0, h + 0.3, strength=2.0)
            b.smoke(0, 0, h + 0.9, strength=0.8)


def candle(b, x=0.0, y=0.0, z=0.0, h=0.16, r=0.024, lit=True, lod=2):
    """A candle; its flame glows."""
    b.tube((x, y, z), (x, y, z + h), r=r, mat="paint", col="!#f4ecd6", lod=lod, n=5, caps=True)
    if lit:
        fz = z + h + 0.012
        ring = [(x + 0.018, y, fz + 0.02), (x, y + 0.018, fz + 0.02), (x - 0.018, y, fz + 0.02), (x, y - 0.018, fz + 0.02)]
        for i in range(4):
            b.face((ring[i], ring[(i + 1) % 4], (x, y, fz + 0.09)), "glow", col="#ffd070", lod=lod)
            b.face((ring[(i + 1) % 4], ring[i], (x, y, fz)), "glow", col="#ff9a3c", lod=lod)


def boat(b, x=0.0, y=0.0, z=0.0, rz=0.0, rx=0.0, ry=0.0, L=3.1, W=1.25, D=0.46, col="teal", inside="#cdb892", lod=1, oars=True):
    """A small clinker rowing boat, bow toward local -y, keel on z (turn it over with ry=180)."""
    ys = [-0.5, -0.37, -0.2, 0.0, 0.2, 0.37, 0.5]
    hw = [0.0, 0.5, 0.84, 1.0, 0.97, 0.86, 0.68]
    zk = [0.5, 0.13, 0.03, 0.0, 0.02, 0.1, 0.24]
    zg = [1.36, 1.17, 1.05, 1.0, 1.0, 1.06, 1.14]
    S = [(ys[i] * L, hw[i] * W / 2, zk[i] * D, zg[i] * D) for i in range(7)]

    def rows(sgn, inset=0.0):
        k = max(1.0 - inset / (W / 2), 0.0)
        r0 = [(0.0, yy, zkk + inset) for (yy, h_, zkk, zgg) in S]
        r1 = [(sgn * h_ * 0.78 * k, yy, zkk + (zgg - zkk) * 0.3 + inset * 0.5) for (yy, h_, zkk, zgg) in S]
        r2 = [(sgn * h_ * k, yy, zgg) for (yy, h_, zkk, zgg) in S]
        return [r0, r1, r2] if sgn > 0 else [list(reversed(r)) for r in (r0, r1, r2)]

    with b.at(x, y, z, rz=rz, rx=rx, ry=ry):
        with b.detail(lod):
            for sgn in (1, -1):
                loft(b, rows(sgn), "planks", cols=[shade(col, 0.9), col])
                loft(b, rows(sgn, 0.03), "planks", col=inside, flip=True)
            (yy, h_, zkk, zgg) = S[-1]
            tr = [(0.0, yy, zkk), (-h_ * 0.78, yy, zkk + (zgg - zkk) * 0.3), (-h_, yy, zgg), (h_, yy, zgg), (h_ * 0.78, yy, zkk + (zgg - zkk) * 0.3)]
            b.face(tr, "planks", col=shade(col, 0.92))
            b.face([(p[0] * 0.97, p[1] - 0.03, p[2]) for p in reversed(tr)], "planks", col=inside)
            for i in (1, 3):
                b.beam((0, S[i][0], S[i][2] - 0.02), (0, S[i + 2][0], S[i + 2][2] - 0.02), w=0.05, h=0.07, mat="planks", col=shade(col, 0.7), up=(0, 0, 1))
        with b.detail(2):
            for sgn in (1, -1):
                for i in range(6):
                    b.beam((sgn * S[i][1], S[i][0], S[i][3]), (sgn * S[i + 1][1], S[i + 1][0], S[i + 1][3]), w=0.05, h=0.04, mat="planks", col="ivory", caps=False)
            for i in (2, 4):
                b.box(S[i][1] * 1.9, 0.2, 0.03, "planks", col=inside, y=S[i][0], z=S[i][3] - 0.14, bottom=True)
            if oars:
                for sgn in (-1, 1):
                    b.beam((sgn * 0.12, -L * 0.3, D * 0.5), (sgn * 0.2, L * 0.42, D * 0.95), w=0.035, mat="planks", col="#c9b089", caps=False)
                    b.box(0.11, 0.42, 0.02, "planks", col="#c9b089", x=sgn * 0.11, y=-L * 0.36, z=D * 0.43, bottom=True)


# ---------------------------------------------------------------------------------------- living things
def bloom(b, x, y, z, r=0.05, col="#e8497a", lod=2, wind=0.5):
    """One blossom (or berry, fruit, cork float): a tiny double pyramid of flat colour."""
    c = _paint(col)
    top, bot = (x, y, z + r), (x, y, z - r * 0.7)
    ring = [(x + r, y, z), (x, y + r, z), (x - r, y, z), (x, y - r, z)]
    for i in range(4):
        a, c2 = ring[i], ring[(i + 1) % 4]
        b.tri(a, c2, top, "paint", col=c, lod=lod, wind=wind)
        b.tri(c2, a, bot, "paint", col=shade(c, 0.78), lod=lod, wind=wind)


def flowers(b, x=0.0, y=0.0, z=0.0, n=5, spread=0.45, h=0.3, cols=None, leaf="#8fc46a", lod=2):
    """A clump of meadow flowers on the ground (or on a wall-head) at (x, y, z)."""
    rng = b.rng
    cols = cols or BLOOMS
    b.blob(spread * 0.8, spread * 0.62, h * 0.8, mat="ivy", col=leaf, x=x, y=y, z=z, lod=lod, seg=5, rings=2, wind=0.35, rough=0.3, bottom=False)
    for _ in range(n):
        a, rr = rng.uniform(0, 6.283), spread * rng.uniform(0.1, 0.85)
        bloom(b, x + rr * math.cos(a), y + rr * 0.8 * math.sin(a), z + h * rng.uniform(0.7, 1.15), r=rng.uniform(0.04, 0.065), col=rng.choice(cols), lod=lod)


def meadow(b, x0, y0, x1, y1, n=6, cols=None, spread=(0.3, 0.55), z=0.0, lod=2):
    """Scatter n clumps of wildflowers over a patch of ground (a rectangle, or a line if it has no width)."""
    rng = b.rng
    for _ in range(n):
        flowers(b, rng.uniform(x0, x1), rng.uniform(y0, y1), z, n=rng.randrange(3, 7), spread=rng.uniform(*spread), h=rng.uniform(0.22, 0.38),
                cols=cols or [rng.choice(BLOOMS), rng.choice(BLOOMS)], lod=lod)


def spire_flower(b, x=0.0, y=0.0, z=0.0, h=1.1, col="#b08ae6", n=6, lod=2):
    """A tall flowering spike (hollyhock, foxglove, lupin)."""
    rng = b.rng
    top = (x + rng.uniform(-0.06, 0.06), y + rng.uniform(-0.06, 0.06), z + h)
    b.beam((x, y, z), top, w=0.022, mat="ivy", col="#6fa34f", lod=lod, caps=False, wind=0.3)
    b.blob(0.16, 0.14, 0.14, mat="ivy", col="#7db45e", x=x, y=y, z=z, lod=lod, seg=5, rings=2, wind=0.3, rough=0.3, bottom=False)
    for i in range(n):
        t = 0.38 + 0.62 * i / max(n - 1, 1)
        a = i * 2.4
        rr = 0.05 * (1.2 - t * 0.6)
        bloom(b, lerp(x, top[0], t) + rr * math.cos(a), lerp(y, top[1], t) + rr * math.sin(a), z + h * t, r=0.055 * (1.25 - 0.55 * t), col=col, lod=lod, wind=0.3 + 0.4 * t)


def sunflower(b, x=0.0, y=0.0, z=0.0, h=1.6, face=0.0, lod=2):
    """A sunflower looking toward compass `face`."""
    b.beam((x, y, z), (x, y, z + h), w=0.03, mat="ivy", col="#6fa34f", lod=lod, caps=False, wind=0.25)
    with b.at(x, y, z + h, rz=face):
        with b.at(0, -0.04, 0.0, rx=65):
            b.disc(0.17, "paint", col=_paint("#f5c842"), seg=8, lod=lod)
            b.disc(0.17, "paint", col=_paint("#c99a2a"), seg=8, lod=lod, down=True)
            b.disc(0.075, "paint", col=_paint("#5a3b22"), seg=6, lod=lod, z=0.012)
    b.blob(0.14, 0.12, 0.08, mat="ivy", col="#7db45e", x=x, y=y, z=z + h * 0.45, lod=lod, seg=5, rings=2, wind=0.3, rough=0.3)


def fruit_tree(b, x=0.0, y=0.0, z=0.0, h=3.6, crown=1.5, col="#6fae52", fruit="#d8402f", n=12, kind="round", trunk=0.16):
    """An orchard tree: P.tree with fruit (or with a pale colour, blossom) dotted over its crown."""
    P.tree(b, x, y, z, h=h, crown=crown, trunk=trunk, col=col, kind=kind)
    rng = b.rng
    th = h - crown * 1.3
    base = max(th, 0.5) + crown * 0.7
    for _ in range(n):
        a, e = rng.uniform(0, 6.283), rng.uniform(-0.35, 0.9)
        rr = crown * 1.0 * math.cos(e)
        bloom(b, x + rr * math.cos(a), y + rr * math.sin(a), z + base + crown * 0.85 * math.sin(e), r=0.07, col=fruit, lod=2, wind=0.45)


def veg_row(b, p0, p1, kind="cabbage", n=None, lod=2):
    """A row of vegetables between two ground points. kind = 'cabbage', 'leek', 'pumpkin' or 'bean' (canes)."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    step = {"cabbage": 0.42, "leek": 0.24, "pumpkin": 0.8, "bean": 0.5}[kind]
    n = n or max(2, int(L / step))
    rng = b.rng
    for i in range(n):
        t = (i + 0.5) / n
        x, y, z = lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), (p0[2] if len(p0) > 2 else 0.0)
        if kind == "cabbage":
            b.blob(0.16, 0.16, 0.13, mat="ivy", col=shade("#9ccf9a", rng.uniform(0.85, 1.1)), x=x, y=y, z=z + 0.07, lod=lod, seg=5, rings=2, rough=0.25, bottom=False)
        elif kind == "leek":
            b.beam((x, y, z), (x + rng.uniform(-0.05, 0.05), y + rng.uniform(-0.05, 0.05), z + 0.34), w=0.035, mat="ivy", col="#7fb760", lod=lod, caps=False, wind=0.3)
        elif kind == "pumpkin":
            b.blob(0.2, 0.2, 0.15, mat="paint", col=_paint("#e08a2c"), x=x + rng.uniform(-0.1, 0.1), y=y, z=z + 0.12, lod=lod, seg=6, rings=3, rough=0.1)
            b.blob(0.3, 0.26, 0.07, mat="ivy", col="#7db45e", x=x + 0.2, y=y + 0.1, z=z + 0.02, lod=lod, seg=5, rings=2, rough=0.4, bottom=False)
        else:
            dx, dy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
            for sgn in (-1, 1):
                b.beam((x - dy * 0.22 * sgn, y + dx * 0.22 * sgn, z), (x, y, z + 1.75), w=0.025, mat="planks", col="#c9b089", lod=lod, caps=False)
            b.blob(0.2, 0.2, 0.55, mat="ivy", col=shade("#7fb760", rng.uniform(0.85, 1.1)), x=x, y=y, z=z + 0.75, lod=lod, seg=5, rings=3, rough=0.3, wind=0.2)
            bloom(b, x + 0.1, y - 0.12, z + rng.uniform(0.7, 1.2), r=0.045, col="#e85d3a", lod=lod)
    if kind == "bean":
        b.beam((p0[0], p0[1], 1.68), (p1[0], p1[1], 1.68), w=0.025, mat="planks", col="#c9b089", lod=lod, caps=False)


def dove(b, x=0.0, y=0.0, z=0.0, rz=0.0, s=1.0, col="#f7f4ec", lod=2):
    """A dove standing at (x, y, z), looking toward local -y."""
    c = _paint(col)
    with b.at(x, y, z, rz=rz, s=s):
        with b.detail(lod):
            b.blob(0.065, 0.125, 0.07, mat="paint", col=c, y=0.0, z=0.115, seg=5, rings=3, rough=0.05)
            b.blob(0.04, 0.045, 0.042, mat="paint", col=c, y=-0.105, z=0.2, seg=5, rings=2, rough=0.05)
            t = [(-0.055, 0.09, 0.13), (0.055, 0.09, 0.13), (0.0, 0.27, 0.085)]
            b.face(t, "paint", col=c)
            b.face(list(reversed(t)), "paint", col=shade(c, 0.85))
            b.tri((-0.012, -0.14, 0.2), (0.012, -0.14, 0.2), (0.0, -0.18, 0.19), "paint", col=_paint("#e0a04a"))
            b.tri((0.012, -0.14, 0.2), (-0.012, -0.14, 0.2), (0.0, -0.18, 0.19), "paint", col=_paint("#e0a04a"))


def cat(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="#d98a3d", lod=2, pose="sit"):
    """A cat at (x, y, z) looking toward local -y. pose = 'sit' or 'curl' (asleep)."""
    c = _paint(col)
    with b.at(x, y, z, rz=rz):
        with b.detail(lod):
            if pose == "curl":
                b.blob(0.17, 0.2, 0.09, mat="paint", col=c, z=0.08, seg=6, rings=3, rough=0.08)
                b.blob(0.07, 0.075, 0.06, mat="paint", col=c, x=0.08, y=-0.14, z=0.09, seg=5, rings=2, rough=0.05)
                hx, hy, hz = 0.08, -0.14, 0.14
            else:
                b.blob(0.1, 0.13, 0.17, mat="paint", col=c, z=0.16, seg=6, rings=3, rough=0.06)
                b.blob(0.075, 0.08, 0.07, mat="paint", col=c, y=-0.07, z=0.37, seg=5, rings=2, rough=0.05)
                b.beam((0.06, 0.1, 0.03), (0.2, 0.0, 0.03), w=0.035, mat="paint", col=c, caps=False)
                hx, hy, hz = 0.0, -0.07, 0.42
            for sx in (-1, 1):
                e = [(hx + sx * 0.06, hy, hz - 0.0), (hx + sx * 0.02, hy, hz + 0.0), (hx + sx * 0.05, hy, hz + 0.075)]
                b.face(e, "paint", col=c)
                b.face(list(reversed(e)), "paint", col=c)
