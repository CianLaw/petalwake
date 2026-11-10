"""Larkhaven lanes (prefix l_): extra parts for the terraced houses, written with the kit primitives.

Same conventions as parts.py: positions on a wall are metres from its left end (seen from outside),
heights are above the wall's base; detail 0 = structure, 1 = silhouette, 2 = fine dressing.

What is here, roughly in the order a house is built:
  roofs      roof_face (any flat slope, coursed), pent, hip_roof (per-side eaves, hip rolls, a gap for a
             wall-dormer, a flat top), halfhip_roof, crow_roof / crow_gable, ridge_roll, saddle (a raised
             ridge capping), barge_boards (plumb-cut, for eaves that run to the edge of the lot)
  walls      outline_walls / Walls (ground plans that are not a rectangle), wall_top / cut_gable (windows
             in gables), timbers + knee + cross (framing that goes round the openings), band_on, anchors,
             arch_dress, shaped_wall (a parapet with a curved head)
  fronts     bay (box and canted bays, oriels), shopfront, hood, guard, porthole, hoist, sign, jetty
  roof life  deck, trapdoor, roof_ladder, parapet, pergola, telescope, beehive, roof_window, ball,
             bean_poles, straw_bird, cat, gull
  street     flowerpot, stall, logs, trough, pump, handcart, peel, column, downpipe, gutter, anchor,
             herbs, bunting
"""
import math

import kit
from kit import C, lerp, rad, shade, vadd, vcross, vdot, vlen, vlerp, vmul, vnorm, vsub
import parts as P


# ---------------------------------------------------------------------------------------- geometry helpers
def _clip(poly, k, lo, hi):
    """Clip a convex polygon (tuples of any length) to lo <= p[k] <= hi."""
    for sign, bound in ((1.0, lo), (-1.0, hi)):
        out = []
        n = len(poly)
        for i in range(n):
            a, c = poly[i], poly[(i + 1) % n]
            da, dc = sign * (a[k] - bound), sign * (c[k] - bound)
            if da >= -1e-7:
                out.append(a)
            if (da > 1e-7 and dc < -1e-7) or (da < -1e-7 and dc > 1e-7):
                t = da / (da - dc)
                out.append(tuple(a[j] + (c[j] - a[j]) * t for j in range(len(a))))
        poly = out
        if len(poly) < 3:
            return []
    return poly


def _normal(pts):
    nx = ny = nz = 0.0
    for i in range(len(pts)):
        a, c = pts[i], pts[(i + 1) % len(pts)]
        nx += (a[1] - c[1]) * (a[2] + c[2]); ny += (a[2] - c[2]) * (a[0] + c[0]); nz += (a[0] - c[0]) * (a[1] + c[1])
    return vnorm((nx, ny, nz))


def _minus(a, c, blocks, least=0.06):
    """The parts of the span a..c left after taking out the (lo, hi) blocks."""
    segs = [(a, c)]
    for lo, hi in blocks:
        nxt = []
        for s0, s1 in segs:
            if hi <= s0 or lo >= s1:
                nxt.append((s0, s1))
            else:
                if lo > s0:
                    nxt.append((s0, lo))
                if hi < s1:
                    nxt.append((hi, s1))
        segs = nxt
    return [(s0, s1) for s0, s1 in segs if s1 - s0 > least]


# ---------------------------------------------------------------------------------------- roofs
def roof_face(b, pts, mat="tiles", col=None, course=0.42, lip=0.045, lod=0, thick=0.0, rim=(), soffit="planks", soffit_col="darkoak", uvo=None):
    """One flat roof slope laid in overlapping courses that run level across it. pts = its outline, a convex
    polygon of (x, y, z) anticlockwise seen from outside. With thick > 0 it also gets an underside that far below
    and edge boards along the outline edges listed in rim (edge i runs from pts[i] to pts[i + 1]): give the eaves
    and verges, leave out ridges and hips. Hips, half-hips, pents and valleys are all made of these."""
    col = C(col)
    pts = [tuple(p) for p in pts]
    nrm = _normal(pts)
    u = vsub((0.0, 0.0, 1.0), vmul(nrm, nrm[2]))
    u = vnorm(u) if vlen(u) > 1e-4 else (0.0, 1.0, 0.0)
    t = vnorm(vcross(u, nrm))
    S = [vdot(p, u) for p in pts]
    s0, s1 = min(S), max(S)
    L = s1 - s0
    nc = max(1, round(L / course)) if course else 1
    uo, vo = uvo or b.uvo()
    P4 = [(p[0], p[1], p[2], s) for p, s in zip(pts, S)]
    for k in range(nc):
        sa, sb = s0 + L * k / nc, s0 + L * (k + 1) / nc
        band = _clip(P4, 3, sa, sb)
        if len(band) < 3:
            continue
        out = []
        for q in band:
            f = lip * (1.0 - (q[3] - sa) / max(sb - sa, 1e-9))
            out.append((q[0] + nrm[0] * f, q[1] + nrm[1] * f, q[2] + nrm[2] * f))
        b.face(out, mat, col=shade(col, b.r(0.88, 1.08)), lod=lod, uv=[(uo + vdot(q[:3], t), vo + q[3] - s0) for q in band])
        if k > 0 and lip > 0:      # the little riser where this course stands proud of the one below
            low = sorted([q for q in band if abs(q[3] - sa) < 1e-6], key=lambda q: vdot(q[:3], t))
            if len(low) >= 2:
                a, c = low[0][:3], low[-1][:3]
                b.face((a, c, vadd(c, vmul(nrm, lip)), vadd(a, vmul(nrm, lip))), mat, col=shade(col, 0.7), lod=lod)
    if thick > 0:
        dn = vmul(nrm, -thick)
        up = vmul(nrm, lip)
        b.face([vadd(p, dn) for p in reversed(pts)], soffit, col=soffit_col, lod=lod)
        for i in rim:
            a, c = pts[i], pts[(i + 1) % len(pts)]
            b.face((vadd(a, dn), vadd(c, dn), vadd(c, up), vadd(a, up)), soffit, col=soffit_col, lod=lod)
    return nrm


def ridge_roll(b, p0, p1, mat="tiles", col=None, w=0.26, h=0.14, step=0.42, lod=1):
    """Half-round ridge tiles laid from p0 to p1: along a ridge, or down a hip."""
    col = C(col)
    L = vlen(vsub(p1, p0))
    n = max(1, int(L / step))
    with b.detail(lod):
        for i in range(n):
            a, c = vlerp(p0, p1, i / n), vlerp(p0, p1, (i + 0.96) / n)
            b.beam((a[0], a[1], a[2] + 0.03), (c[0], c[1], c[2] + 0.05), w=w, h=h, mat=mat, col=shade(col, b.r(0.82, 1.0)), caps=True)


def pent(b, w, d, rise, mat="tiles", col=None, eave=0.25, verge=0.12, course=0.36, lip=0.04, thick=0.1, lod=0, top=0.0):
    """A lean-to roof in the current frame: over x in +-w/2, y in 0..d, low at y = 0 (height 0) and rising to
    `rise` at y = d, where it meets the wall it leans on (top = how far it carries on past y = d)."""
    k = rise / d
    y0, y1 = -eave, d + top
    pts = [(-w / 2 - verge, y0, y0 * k), (w / 2 + verge, y0, y0 * k), (w / 2 + verge, y1, y1 * k), (-w / 2 - verge, y1, y1 * k)]
    roof_face(b, pts, mat, col, course=course, lip=lip, lod=lod, thick=thick, rim=(0, 1, 3) if top <= 0 else (0, 1, 2, 3))


def halfhip_roof(bd, pitch=50.0, hip=0.42, ends="f", hip_pitch=None, mat="tiles", col=None, eave=0.25, verge=0.3, course=0.42, lip=0.045,
                 thick=0.16, roll=True, roll_mat=None, roll_col=None, roll_w=0.26, lod=0):
    """Roof a block with its ridge running front to back, the top `hip` (0..1) of the gable at the front ('f'),
    back ('b') or both ('fb') leaned back as a little hip: a half-hipped (jerkinhead) roof. Raises the end walls
    to suit; put windows in them first and they are cut round. Returns the rise of the ridge, and leaves the ends
    of the ridge on the body as bd.ridge_y = (front y, back y)."""
    b = bd.b
    a = bd.w / 2
    tp = math.tan(rad(pitch))
    th = math.tan(rad(hip_pitch if hip_pitch is not None else min(pitch + 6, 62)))
    R = a * tp
    ze = -eave * tp
    zh = R * (1.0 - hip)                    # where the little hip starts, on the wall plane
    zhe = zh - verge * th                   # ... and at its own eave, a verge out from the wall
    xh = a - zhe / tp                       # half-width of the hip's eave
    run = (R - zhe) / th                    # how far the hip leans in before it reaches the ridge
    y0, y1 = -bd.d / 2 - verge, bd.d / 2 + verge
    hf, hb = "f" in ends, "b" in ends
    yf = y0 + run if hf else y0
    yb = y1 - run if hb else y1
    with b.at(bd.x, bd.y, bd.z + bd.h):
        for sgn in (1, -1):
            poly = [(sgn * (a + eave), y0, ze)]
            if hb:
                poly += [(sgn * (a + eave), y1, ze), (sgn * xh, y1, zhe), (0.0, yb, R)]
            else:
                poly += [(sgn * (a + eave), y1, ze), (0.0, y1, R)]
            poly += [(0.0, yf, R), (sgn * xh, y0, zhe)] if hf else [(0.0, y0, R)]
            rim = [0, 1, len(poly) - 1]              # eave, back verge, front verge
            if sgn < 0:
                poly = list(reversed(poly))
                rim = [(len(poly) - 2 - i) % len(poly) for i in rim]
            roof_face(b, poly, mat, col, course=course, lip=lip, lod=lod, thick=thick, rim=rim)
        if hf:
            roof_face(b, [(-xh, y0, zhe), (xh, y0, zhe), (0.0, yf, R)], mat, col, course=course, lip=lip, lod=lod, thick=thick, rim=(0,))
        if hb:
            roof_face(b, [(xh, y1, zhe), (-xh, y1, zhe), (0.0, yb, R)], mat, col, course=course, lip=lip, lod=lod, thick=thick, rim=(0,))
        if roll:
            rm, rc = roll_mat or mat, roll_col if roll_col is not None else col
            ridge_roll(b, (0, yf, R), (0, yb, R), rm, rc, w=roll_w, h=roll_w * 0.54)
            for (flag, ye, yr) in ((hf, y0, yf), (hb, y1, yb)):
                if flag:
                    for sgn in (-1, 1):
                        ridge_roll(b, (sgn * xh, ye, zhe), (0, yr, R), rm, rc, w=roll_w * 0.85, h=roll_w * 0.46)
    bd.ridge_y = (bd.y + yf, bd.y + yb)
    for wl, flag in ((bd.front, hf), (bd.back, hb)):
        w, h = wl.w, wl.h
        if flag:
            k = hip
            wall_top(wl, [[(0.0, h), (w, h), (w / 2 + a * k, h + zh - 0.03), (w / 2 - a * k, h + zh - 0.03)]])
        else:
            wall_top(wl, [[(0.0, h), (w, h), (w / 2, h + R - 0.03)]])
    return R


def crow_gable(wall, rise, n=5, up=0.45, t=0.3, mat=None, col=None, cope=0.1, cope_mat="ashlar", cope_col="stone"):
    """A crow-stepped gable standing on a wall top: n steps a side, climbing clear of a roof whose ridge is `rise`
    above the wall top, `up` higher than the tiles at every step. t = its thickness (it has a back, and dressed
    copings). Windows put in the wall above its top (P.window ...) are cut through it."""
    b = wall.b
    w, h = wall.w, wall.h
    c = w / 2
    tiers, zprev = [], h
    for k in range(n):
        zk = h + rise * (k + 1) / n + up
        tiers.append((c * (1 - k / n), zprev, zk))
        zprev = zk
    rects = [[(c - hk, za), (c + hk, za), (c + hk, zb), (c - hk, zb)] for hk, za, zb in tiers]

    def deco():
        _region(wall, rects, mat, col)
        _region(wall, rects, mat, col, y=t, back=True, holes=False)
        m, cl = mat or wall.mat, wall.col if col is None else col
        for i, (hk, za, zb) in enumerate(tiers):
            hn = tiers[i + 1][0] if i + 1 < n else 0.0
            for sgn in (-1, 1):
                x = c + sgn * hk
                if sgn < 0:
                    b.quad((x, t, za), (x, 0, za), (x, 0, zb), (x, t, zb), m, col=cl, lod=wall.lod)
                else:
                    b.quad((x, 0, za), (x, t, za), (x, t, zb), (x, 0, zb), m, col=cl, lod=wall.lod)
                if hn <= 0 and sgn > 0:
                    continue
                x0, x1 = (c - hk, c - hn) if sgn < 0 else (c + hn, c + hk)
                if hn <= 0:
                    x0, x1 = c - hk, c + hk
                b.quad((x0, 0, zb), (x1, 0, zb), (x1, t, zb), (x0, t, zb), m, col=cl, lod=wall.lod)
                if cope:
                    b.box(x1 - x0 + 0.1, t + 0.12, cope, cope_mat, col=cope_col, x=(x0 + x1) / 2, y=t / 2, z=zb, lod=1, bottom=True)

    wall.add(deco)
    return tiers[-1][2]


def crow_roof(bd, pitch=52.0, steps=5, up=0.45, t=0.3, ends="f", verge=0.3, **kw):
    """Roof a block with its ridge running front to back between crow-stepped gables (ends = 'f', 'b' or 'fb';
    the other end gets a plain gable and a verge). Returns (rise, height of the top step above the wall base)."""
    b = bd.b
    rise = bd.w / 2 * math.tan(rad(pitch))
    y0 = bd.y - bd.d / 2 + (t * 0.5 if "f" in ends else -verge)
    y1 = bd.y + bd.d / 2 - (t * 0.5 if "b" in ends else -verge)
    b.gable_roof(bd.w, (y1 - y0) - 2 * verge, pitch, x=bd.x, y=(y0 + y1) / 2, z=bd.z + bd.h, ridge="y", verge=verge, **kw)
    top = 0.0
    for wl, key in ((bd.front, "f"), (bd.back, "b")):
        if key in ends:
            top = crow_gable(wl, rise, n=steps, up=up, t=t)
        else:
            wl.gable = rise - 0.03
    return rise, top


# ---------------------------------------------------------------------------------------- walls
def _region(wall, polys, mat=None, col=None, y=0.0, back=False, holes=True, lod=None):
    """Emit flat pieces of wall (convex outlines in (u, z)) in the wall's plane, cut round its openings.
    Runs in the wall's own frame."""
    b = wall.b
    uo, vo = wall.uvo
    mat = mat or wall.mat
    col = wall.col if col is None else col
    lod = wall.lod if lod is None else lod
    for poly in polys:
        us, zs = [p[0] for p in poly], [p[1] for p in poly]
        u0, u1, z0, z1 = min(us), max(us), min(zs), max(zs)
        ucut, zcut = {u0, u1}, {z0, z1}
        if holes:
            for o in wall.ops:
                if o["u1"] > u0 and o["u0"] < u1 and o["z1"] > z0 and o["z0"] < z1:
                    ucut |= {min(max(o["u0"], u0), u1), min(max(o["u1"], u0), u1)}
                    zcut |= {min(max(o["z0"], z0), z1), min(max(o["z1"], z0), z1)}
        ug, zg = kit._grid(ucut, 0, wall.cell), kit._grid(zcut, 0, wall.cell)
        for j in range(len(zg) - 1):
            for i in range(len(ug) - 1):
                ua, ub, za, zb = ug[i], ug[i + 1], zg[j], zg[j + 1]
                if ub - ua < 1e-6 or zb - za < 1e-6 or (holes and wall._in_hole((ua + ub) / 2, (za + zb) / 2)):
                    continue
                piece = _clip(poly, 0, ua, ub)
                piece = _clip(piece, 1, za, zb) if piece else piece
                if len(piece) < 3:
                    continue
                pts = [(p[0], y, p[1]) for p in piece]
                uv = [(uo + p[0], vo + p[1]) for p in piece]
                if back:
                    pts.reverse(); uv.reverse()
                b.face(pts, mat, col=col, lod=lod, uv=uv)


def wall_top(wall, polys, mat=None, col=None):
    """Carry a flat wall on above its top (or anywhere outside its rectangle) with convex outline pieces
    [(u, z), ...], z measured from the wall's base, anticlockwise. Openings added to the wall cut through them too:
    this is how a window gets into a gable, a half-hip, an M-shaped party wall."""
    wall.add(lambda: _region(wall, polys, mat, col))


def cut_gable(wall):
    """Call after Body.gable(...): the gable the roof gave this wall is rebuilt round the wall's openings, so a
    P.window(wall, u, z ...) with z above the wall top gives a real attic window."""
    g, sec = wall.gable, wall.gable_section
    if g <= 1e-6:
        return
    w, h = wall.w, wall.h
    half = w / 2
    if sec:
        k = g / sec[-1][1]
        side = [(min(r_, half), h + z_ * k) for r_, z_ in sec[1:]]
    else:
        side = [(half, h + g)]
    ring = [(w, h)] + [(w - u, z) for u, z in side]
    ring += [(u, z) for u, z in reversed(side) if abs(u - half) > 1e-6] + [(0.0, h)]
    c = (half, h)
    wall.gable = 0.0
    wall_top(wall, [[c, ring[i], ring[i + 1]] for i in range(len(ring) - 1)])


def roofline(wall, rise, u):
    """Height (above the wall's base) of a plain gable of the given rise at u along the wall."""
    c = wall.w / 2
    return wall.h + rise * max(0.0, 1.0 - abs(u - c) / c)


def timbers(wall, posts=(), rails=(), braces=(), u0=0.0, u1=None, z0=0.0, z1=None, gable=0.0, col="darkoak", w=0.15, proud=0.035, lod=1,
            frames=True):
    """Half-timbering that goes round the openings (the kit's P.timber_frame runs straight across them).
    posts = positions along the wall (or (u, za, zb)); rails = heights (or (z, ua, ub)); braces = straight pieces
    (ua, za, ub, zb), see knee() and cross(). gable = the rise of the wall's gable: posts and rails given above the
    wall top are then trimmed to the roof line. frames=True boxes every opening in the framed area with a head and
    a sill timber."""
    b = wall.b
    u1 = wall.w if u1 is None else u1
    z1 = (wall.h + gable) if z1 is None else z1
    y = -proud
    th = proud * 2 + 0.04

    def top_at(u):
        return roofline(wall, gable, u) - 0.1 if gable > 0 else 1e9

    def deco():
        ops = wall.ops
        with b.detail(lod):
            for p in posts:
                u, za, zb = (p, z0, z1) if not isinstance(p, (tuple, list)) else p
                x = min(max(u, u0 + w / 2), u1 - w / 2)
                zb = min(zb, top_at(x))
                blocks = [(o["z0"] - 0.02, o["z1"] + 0.02) for o in ops if o["u0"] - w / 2 < x < o["u1"] + w / 2]
                for sa, sb in _minus(za, zb, blocks):
                    b.beam((x, y, sa), (x, y, sb), w=w, h=th, mat="timber", col=col, up=(0, 1, 0), caps=False)
            for r in rails:
                z, ua, ub = (r, u0, u1) if not isinstance(r, (tuple, list)) else r
                zz = min(max(z, z0 + w / 2), z1 - w / 2)
                if gable > 0 and zz > wall.h:
                    k = (wall.w / 2) * (1.0 - (zz + 0.1 - wall.h) / gable)
                    ua, ub = max(ua, wall.w / 2 - k), min(ub, wall.w / 2 + k)
                blocks = [(o["u0"] - 0.02, o["u1"] + 0.02) for o in ops if o["z0"] - w / 2 < zz < o["z1"] + w / 2]
                for sa, sb in _minus(ua, ub, blocks):
                    b.beam((sa, y - 0.004, zz), (sb, y - 0.004, zz), w=th, h=w, mat="timber", col=col, up=(0, 0, 1), caps=False)
            for (ua, za, ub, zb) in braces:
                if any(wall._in_hole(lerp(ua, ub, f), lerp(za, zb, f)) for f in (0.25, 0.5, 0.75)):
                    continue
                b.beam((ua, y + 0.006, za), (ub, y + 0.006, zb), w=w * 0.8, h=th - 0.01, mat="timber", col=col, up=(0, 1, 0), caps=False)
            if frames:
                for o in ops:
                    if o["u0"] < u0 - 0.01 or o["u1"] > u1 + 0.01 or o["z0"] < z0 - 0.01 or o["z1"] > z1 + 0.01:
                        continue
                    for zz in ((o["z0"] - w * 0.4, o["z1"] + w * 0.4) if o["z0"] > z0 + 0.3 else (o["z1"] + w * 0.4,)):
                        b.beam((o["u0"] - 0.14, y - 0.008, zz), (o["u1"] + 0.14, y - 0.008, zz), w=th, h=w * 0.8, mat="timber", col=col, up=(0, 0, 1), caps=False)
                    for uu in (o["u0"] - w * 0.4, o["u1"] + w * 0.4):
                        b.beam((uu, y - 0.006, o["z0"] - w * 0.4), (uu, y - 0.006, o["z1"] + w * 0.4), w=w * 0.8, h=th, mat="timber", col=col, up=(0, 1, 0), caps=False)

    wall.add(deco)


def knee(ua, za, ub, zb, bulge=0.18, n=3):
    """A curved brace from (ua, za) to (ub, zb) as n straight pieces, bowed toward the corner it braces."""
    out = []
    dx, dz = ub - ua, zb - za
    L = math.hypot(dx, dz) or 1.0
    nx, nz = dz / L, -dx / L
    pts = []
    for i in range(n + 1):
        t = i / n
        k = bulge * L * 4 * t * (1 - t)
        pts.append((ua + dx * t + nx * k, za + dz * t + nz * k))
    for i in range(n):
        out.append((pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]))
    return out


def cross(ua, za, ub, zb):
    """A St Andrew's cross filling the panel between two corners."""
    return [(ua, za, ub, zb), (ua, zb, ub, za)]


def band_on(wall, z, h=0.16, out=0.05, u0=0.0, u1=None, mat="ashlar", col="stone", lod=1):
    """A string course along one wall at height z (P.band goes right round a block)."""
    b = wall.b
    u1 = wall.w if u1 is None else u1
    wall.add(lambda: b.box(u1 - u0, out + 0.02, h, mat, col=col, x=(u0 + u1) / 2, y=-(out - 0.02) / 2 - 0.0, z=z, lod=lod, bottom=True))


def anchors(wall, spots, s=0.26, col="iron", kind="x"):
    """Wrought-iron wall ties at the given (u, z) spots: 'x' crosses or 's' bars."""
    b = wall.b

    def deco():
        with b.detail(2):
            for (u, z) in spots:
                if kind == "x":
                    b.beam((u - s / 2, -0.025, z - s / 2), (u + s / 2, -0.025, z + s / 2), w=0.035, h=0.03, mat="metal", col=col, up=(0, 1, 0))
                    b.beam((u - s / 2, -0.03, z + s / 2), (u + s / 2, -0.03, z - s / 2), w=0.035, h=0.03, mat="metal", col=col, up=(0, 1, 0))
                else:
                    b.beam((u, -0.025, z - s * 0.7), (u, -0.025, z + s * 0.7), w=0.04, h=0.03, mat="metal", col=col, up=(0, 1, 0))
                    b.beam((u, -0.03, z + s * 0.7), (u + s * 0.3, -0.03, z + s * 0.45), w=0.035, h=0.03, mat="metal", col=col, up=(0, 1, 0))
                    b.beam((u, -0.03, z - s * 0.7), (u - s * 0.3, -0.03, z - s * 0.45), w=0.035, h=0.03, mat="metal", col=col, up=(0, 1, 0))

    wall.add(deco)


def arch_dress(wall, pos, z, w, h, arch, mat="ashlar", col="sand", proud=0.07, key=True, jambs=True, lod=2):
    """Dressed stones round an opening made with wall.opening(...): long-and-short jambs and a ring of voussoirs
    (with a bigger keystone). Use it for open archways; P.door dresses its own."""
    b = wall.b
    u = wall.U(pos)

    def deco():
        with wall.onu(u, z):
            hs = h - arch
            with b.detail(lod):
                if jambs:
                    n = max(3, int(hs / 0.36))
                    for i in range(n):
                        for sgn in (-1, 1):
                            ww = 0.38 if i % 2 == 0 else 0.24
                            with b.at(sgn * (w / 2 + ww / 2 - 0.02), -proud / 2, hs * i / n, rx=90):
                                b.stone(ww, hs / n * 0.94, proud, mat=mat, col=col, y=-(hs / n) * 0.47, jitter=0.05, lod=lod)
                if arch > 1e-4:
                    n = max(7, int(math.pi * w / 2 / 0.3) | 1)
                    for i in range(n):
                        a = math.pi * (i + 0.5) / n
                        big = key and i == n // 2
                        d = 0.19 if big else 0.14
                        x, zz = -(w / 2 + d) * math.cos(a), hs + (arch + d) * math.sin(a)
                        with b.at(x, -proud / 2, zz, ry=-(90 - math.degrees(a))):
                            with b.at(rx=90):
                                b.stone(math.pi * w / 2 / n * 0.92, 0.42 if big else 0.3, proud + (0.03 if big else 0.0), mat=mat, col=col, jitter=0.06, lod=lod)
                else:
                    b.box(w + 0.5, 0.14, 0.26, mat, col=col, x=0, y=-0.03, z=h, lod=1)

    wall.add(deco)


# ---------------------------------------------------------------------------------------- fronts
def bay(wall, pos, z, w=1.9, h=1.7, out=0.5, cant=0.0, mat="plaster", col="cream", frame="ivory", rows=((0.5, 1.0),), lights=3, side_lights=True,
        roof="tiles", roof_col=None, roof_rise=0.45, eave=0.12, base="brackets", base_col="darkoak", base_mat=None, drop=0.6, trim=None,
        rails=(), posts=True, shutters=None, box=False, lod=0, lintel=None, glass=None):
    """A bay or oriel window standing out from a wall: centred on pos, its floor at z, w wide where it joins the
    wall, h high, standing `out` proud. cant = how far each side is splayed in (0 = a box bay). rows = (sill, height)
    of each tier of windows, measured from its floor; lights = panes across the front. base = 'brackets' (timber
    struts), 'corbel' (a moulded foot dying into the wall), 'ground' (stands on the ground with a stone foot) or
    None. roof = material of its little hipped roof, or None when it runs up under a jetty or an eave. trim = paint
    for its corner posts and rails (rails = heights of moulded rails right round it)."""
    b = wall.b
    u = wall.U(pos)
    trim = frame if trim is None else trim
    with wall.onu(u, z):
        pts = [(-w / 2, 0.0), (-w / 2 + cant, -out), (w / 2 - cant, -out), (w / 2, 0.0)]
        faces = []
        for (a, c) in zip(pts, pts[1:]):
            L = math.hypot(c[0] - a[0], c[1] - a[1])
            with b.at(a[0], a[1], 0, rz=math.degrees(math.atan2(c[1] - a[1], c[0] - a[0]))):
                faces.append(b.wall(L, h, mat, col, depth=0.09, lod=lod))
        fl = faces[1].w
        for (sz, wh) in rows:
            P.window(faces[1], fl / 2, sz, w=fl - 0.3, h=wh, frame=frame, bars=(max(lights - 1, 0), 1), sill=False, lintel=lintel, depth=0.09,
                     shutters=shutters, box=box, glass=glass)
            if side_lights:
                for s in (faces[0], faces[2]):
                    if s.w > 0.52:
                        P.window(s, s.w / 2, sz, w=s.w - 0.26, h=wh, frame=frame, bars=(0, 1), sill=False, lintel=None, depth=0.09, glass=glass)
        for s in faces:
            s.emit()
        # floor and lid
        b.face([(p[0], p[1], 0.0) for p in reversed(pts)], "planks", col=base_col, lod=lod)
        if posts:
            with b.detail(1):
                for p in pts[1:3]:
                    b.beam((p[0], p[1], 0.0), (p[0], p[1], h), w=0.1, mat="planks", col=trim, caps=False)
                for rz in tuple(rails) + (0.05, h - 0.05):
                    for (a, c) in zip(pts, pts[1:]):
                        b.beam((a[0], a[1] - 0.0, rz), (c[0], c[1] - 0.0, rz), w=0.1, h=0.1, mat="planks", col=trim, caps=False)
        if roof:
            n1 = vnorm((pts[1][1] - pts[0][1], -(pts[1][0] - pts[0][0]), 0.0))      # outward normal of the left side
            n2 = (0.0, -1.0, 0.0)
            kk = eave / (1.0 + vdot(n1, n2))
            E1 = (pts[1][0] + (n1[0] + n2[0]) * kk, pts[1][1] + (n1[1] + n2[1]) * kk)
            d1 = vnorm((pts[1][0] - pts[0][0], pts[1][1] - pts[0][1], 0.0))
            sft = -eave * n1[1] / d1[1] if abs(d1[1]) > 1e-6 else 0.0
            E0 = (pts[0][0] + n1[0] * eave + d1[0] * sft, 0.0)
            ze = h - eave * roof_rise / max(out, 0.1)
            zt = h + roof_rise
            kin = min(w / 2 - 0.02, cant + out * 0.75)
            Ls = [(E0[0], E0[1], ze), (E1[0], E1[1], ze), (-E1[0], E1[1], ze), (-E0[0], E0[1], ze)]
            R1, R2 = (-w / 2 + kin, 0.0, zt), (w / 2 - kin, 0.0, zt)
            rc = roof_col
            roof_face(b, [Ls[0], Ls[1], R1], roof, rc, course=0.3, lip=0.035, lod=lod, thick=0.06, rim=(0,))
            roof_face(b, [Ls[1], Ls[2], R2, R1] if kin < w / 2 - 0.03 else [Ls[1], Ls[2], R1], roof, rc, course=0.3, lip=0.035, lod=lod, thick=0.06, rim=(0,))
            roof_face(b, [Ls[2], Ls[3], R2], roof, rc, course=0.3, lip=0.035, lod=lod, thick=0.06, rim=(0,))
        else:
            b.face([(p[0], p[1], h) for p in pts], "planks", col=base_col, lod=lod)
        if base == "brackets":
            with b.detail(1):
                for sgn in (-1, 1):
                    x = sgn * (w / 2 - 0.14)
                    xo = sgn * (w / 2 - cant - 0.1) if cant else x
                    b.beam((x, 0.0, -drop), (xo, -out + 0.07, -0.03), w=0.11, mat="timber", col=base_col)
                    b.beam((x, 0.0, -0.07), (xo, -out + 0.02, -0.07), w=0.1, h=0.13, mat="timber", col=base_col)
        elif base == "corbel":
            k1, k2 = 0.55, 0.22
            mid = [(p[0] * k1, p[1] * k1, -drop * 0.55) for p in pts]
            low = [(p[0] * k2, p[1] * k2 * 0.6, -drop) for p in pts]
            bm = base_mat or mat
            for A, Bq, sh in (([(p[0], p[1], 0.0) for p in pts], mid, 0.94), (mid, low, 0.82)):
                for i in range(3):
                    b.face((Bq[i], Bq[i + 1], A[i + 1], A[i]), bm, col=shade(base_col if base_mat else col, sh), lod=lod)
            b.face(list(reversed(low)), bm, col=shade(base_col if base_mat else col, 0.7), lod=lod)
        elif base == "ground":
            foot = [(p[0] * 1.0 + (0.06 if p[0] > 0 else -0.06), p[1] - (0.06 if p[1] < 0 else 0.0)) for p in pts]
            b.prism(foot, 0.5, base_mat or "masonry", col=base_col if base_mat else "warm", z=0.0, lod=lod)
            b.prism(foot, 3.0, base_mat or "masonry", col=shade(base_col if base_mat else "warm", 0.85), z=-3.0, top=False, lod=lod)
    return faces


def shopfront(wall, u0, u1, h=2.8, col="green", door=None, door_w=0.95, riser=0.55, lights=3, fascia=0.36, frame="ivory", z=0.0, pil=0.16,
              glass=None, transom=True, lamp=False):
    """A timber shop front between u0 and u1 along a wall: a display window over a panelled stall riser, an
    optional half-glazed door (door = its centre; keep it inside u0..u1), pilasters, and a fascia board with a
    cornice, all painted col. It stands on z and is h high to the top of the cornice."""
    b = wall.b
    top = h - fascia - 0.08                      # head of the window and door, above z
    spans = [(u0 + pil, u1 - pil)]
    dop = None
    if door is not None:
        d0, d1 = door - door_w / 2 - pil * 0.6, door + door_w / 2 + pil * 0.6
        spans = [s for s in ((u0 + pil, d0), (d1, u1 - pil)) if s[1] - s[0] > 0.45]
        dop = wall.opening(door, z, door_w, top, pane="planks", pane_col=col, depth=0.2)
    wins = [(a, c, wall.opening((a + c) / 2, z + riser, c - a, top - riser, pane="glass", pane_col=glass, depth=0.14)) for a, c in spans]

    def deco():
        dk = shade(col, 0.72)
        ups = [u0 + pil / 2, u1 - pil / 2] + ([door - door_w / 2 - pil * 0.3, door + door_w / 2 + pil * 0.3] if door is not None else [])
        with b.detail(1):
            for i, uu in enumerate(ups):
                ww = pil if i < 2 else pil * 0.6
                b.box(ww, 0.09, top + 0.04, "planks", col=col, x=uu, y=-0.035, z=z)
                b.box(ww + 0.07, 0.12, 0.09, "planks", col=dk, x=uu, y=-0.04, z=z)
            b.box(u1 - u0 + 0.06, 0.12, fascia, "planks", col=col, x=(u0 + u1) / 2, y=-0.05, z=z + top, bottom=True)
            b.box(u1 - u0 + 0.22, 0.24, 0.08, "planks", col=dk, x=(u0 + u1) / 2, y=-0.09, z=z + top + fascia, bottom=True)
        for (a, c, op) in wins:
            ww = c - a
            with b.detail(1):      # stall riser
                b.box(ww, 0.07, riser - 0.04, "planks", col=col, x=(a + c) / 2, y=-0.02, z=z + 0.02)
                b.box(ww + 0.08, 0.2, 0.06, "planks", col=dk, x=(a + c) / 2, y=-0.06, z=z + riser - 0.05, bottom=True)
            fy = op["d"] * 0.6
            n = max(1, min(lights, int(ww / 0.5)))
            with b.detail(1):
                for uu in (a + 0.03, c - 0.03):
                    b.beam((uu, fy, z + riser), (uu, fy, z + top), w=0.06, h=0.07, mat="planks", col=frame, up=(0, 1, 0), caps=False)
                for zz in (z + riser + 0.03, z + top - 0.03):
                    b.beam((a, fy, zz), (c, fy, zz), w=0.07, h=0.06, mat="planks", col=frame, up=(0, 0, 1), caps=False)
            with b.detail(2):
                for i in range(1, n):
                    uu = a + ww * i / n
                    b.beam((uu, fy + 0.005, z + riser), (uu, fy + 0.005, z + top), w=0.045, h=0.05, mat="planks", col=frame, up=(0, 1, 0), caps=False)
                if transom:
                    zz = z + top - 0.42
                    b.beam((a, fy + 0.005, zz), (c, fy + 0.005, zz), w=0.05, h=0.045, mat="planks", col=frame, up=(0, 0, 1), caps=False)
                m = max(1, int(ww / 0.6))
                for i in range(m):      # raised panels on the riser
                    b.box(ww / m - 0.12, 0.02, riser - 0.24, "planks", col=dk, x=a + ww * (i + 0.5) / m, y=-0.062, z=z + 0.1)
        if dop is not None:
            d = dop["d"]
            with b.detail(2):
                gh = top * 0.42
                b.box(door_w - 0.26, 0.02, gh, "glass", x=door, y=d - 0.016, z=z + top * 0.5)
                for zz in (z + top * 0.5, z + top * 0.5 + gh):
                    b.beam((door - door_w / 2 + 0.1, d - 0.03, zz), (door + door_w / 2 - 0.1, d - 0.03, zz), w=0.03, h=0.05, mat="planks", col=dk, up=(0, 0, 1), caps=False)
                b.box(door_w - 0.26, 0.02, top * 0.3, "planks", col=dk, x=door, y=d - 0.016, z=z + 0.14)
                b.box(0.05, 0.05, 0.05, "metal", col="brass", x=door + door_w / 2 - 0.12, y=d - 0.05, z=z + top * 0.46, bottom=True)
            if z > 0.05:      # a threshold slab when the shop stands on a plinth
                with b.detail(1):
                    b.box(door_w + 0.5, 0.42, z, "ashlar", col="stone", x=door, y=-0.19, z=0.0)
        if lamp:
            P.lantern_at(b, u0 - 0.05, -0.02, z + top - 0.25)

    wall.add(deco)


def hood(wall, pos, z, w=1.5, out=0.75, kind="pent", mat="tiles", col=None, rise=0.32, brackets=True, wood="darkoak", lod=1):
    """A little canopy over a door: its back edge on the wall at height z. kind = 'pent' (one slope, falling to
    the street), 'gable' or 'flat' (a lead-covered board)."""
    b = wall.b
    u = wall.U(pos)

    def deco():
        with wall.onu(u, z):
            if kind == "pent":
                with b.at(0, -out, -rise):
                    pent(b, w, out, rise, mat, col, eave=0.06, verge=0.04, course=0.26, lip=0.03, thick=0.07, lod=lod)
            elif kind == "gable":
                for sgn in (1, -1):
                    pts = [(sgn * (w / 2 + 0.05), -out - 0.06, -rise), (sgn * (w / 2 + 0.05), 0.0, -rise), (0.0, 0.0, 0.0), (0.0, -out - 0.06, 0.0)]
                    roof_face(b, pts if sgn > 0 else list(reversed(pts)), mat, col, course=0.26, lip=0.03, lod=lod, thick=0.07, rim=(0, 3) if sgn > 0 else (2, 3))
                with b.detail(lod):
                    b.face([(-w / 2, -out, -rise - 0.07), (w / 2, -out, -rise - 0.07), (0.0, -out, -0.07)], "planks", col=wood)
            else:
                with b.detail(lod):
                    b.box(w, out, 0.08, "planks", col=wood, x=0, y=-out / 2, z=-0.08, bottom=True, cap="metal", capcol="lead")
            if brackets:
                with b.detail(lod):
                    zz = -rise if kind != "flat" else -0.08
                    for sgn in (-1, 1):
                        x = sgn * (w / 2 - 0.09)
                        b.beam((x, -0.02, zz - 0.55), (x, -out + 0.1, zz - 0.02), w=0.08, mat="timber", col=wood)
                        b.beam((x, -0.02, zz - 0.04), (x, -out + 0.04, zz - 0.04), w=0.08, mat="timber", col=wood)

    wall.add(deco)


def guard(wall, pos, z, w=1.0, h=0.45, out=0.16, col="iron"):
    """A wrought-iron window guard (a balconette) in front of a window: bottom rail at height z."""
    b = wall.b
    u = wall.U(pos)

    def deco():
        with wall.onu(u, z):
            with b.detail(2):
                for zz in (0.0, h):
                    b.beam((-w / 2, -out, zz), (w / 2, -out, zz), w=0.03, mat="metal", col=col, caps=False)
                    for sgn in (-1, 1):
                        b.beam((sgn * w / 2, 0.0, zz), (sgn * w / 2, -out, zz), w=0.03, mat="metal", col=col, caps=False)
                n = max(3, int(w / 0.14))
                for i in range(n + 1):
                    x = -w / 2 + w * i / n
                    b.beam((x, -out, 0.0), (x, -out - (0.05 if i % 2 else 0.0), h), w=0.018, mat="metal", col=col, caps=False)

    wall.add(deco)


def porthole(wall, pos, z, r=0.32, rim="brass", seg=12, glass=None):
    """A round window: a glazed disc in a metal ring, centred at (pos, z). (It sits on the wall face; the kit's
    openings cannot be round.)"""
    b = wall.b
    u = wall.U(pos)

    def deco():
        with wall.onu(u, z):
            with b.at(rx=90):
                b.disc(r, "glass", col=glass, seg=seg, z=0.03, lod=0)
                with b.detail(1):
                    b.revolve([(r - 0.02, 0.03), (r - 0.02, 0.07), (r + 0.07, 0.07), (r + 0.09, 0.0)], "metal", col=rim, seg=seg)
                with b.detail(2):
                    b.box(0.03, 2 * r, 0.012, "metal", col=rim, z=0.035)
                    b.box(2 * r, 0.03, 0.012, "metal", col=rim, z=0.035)

    wall.add(deco)


def hoist(wall, pos, z, out=1.15, drop=1.6, load="sack", col="darkoak"):
    """A hoist beam sticking out of a gable at (pos, z), with a pulley, a rope and something on the hook
    (load = 'sack', 'crate', 'hook' or None)."""
    b = wall.b
    u = wall.U(pos)

    def deco():
        with wall.onu(u, z):
            with b.detail(1):
                b.beam((0, 0.3, 0), (0, -out, 0), w=0.16, h=0.18, mat="timber", col=col)
                b.beam((0, -0.02, -0.55), (0, -out * 0.55, -0.06), w=0.1, mat="timber", col=col)
            with b.detail(2):
                y = -out + 0.14
                b.tube((-0.05, y, -0.2), (0.05, y, -0.2), r=0.11, mat="metal", col="iron", n=8, caps=True)
                b.beam((0, y, -0.02), (0, y, -0.2), w=0.03, mat="metal", col="iron", caps=False)
                b.beam((0, y, -0.3), (0, y, -drop), w=0.022, mat="cloth", col="#8a7a66", caps=False, wind=0.12)
                if load == "sack":
                    b.blob(0.2, 0.2, 0.3, mat="cloth", col="#d9c9a3", x=0, y=y, z=-drop - 0.28, seg=6, rings=3, rough=0.12, wind=0.25)
                elif load == "crate":
                    with b.at(0, y, -drop - 0.45, rz=18):
                        b.box(0.45, 0.45, 0.45, "planks", col="#d8c3a0", bottom=True)
                elif load == "hook":
                    b.beam((0, y, -drop), (0.06, y, -drop - 0.12), w=0.025, mat="metal", col="iron", caps=False)

    wall.add(deco)


SHAPES = {
    "apple": [(0, .13), (.09, .19), (.2, .12), (.22, -.04), (.13, -.19), (0, -.15), (-.13, -.19), (-.22, -.04), (-.2, .12), (-.09, .19)],
    "bottle": [(-.04, .24), (.04, .24), (.04, .08), (.11, 0), (.11, -.22), (-.11, -.22), (-.11, 0), (-.04, .08)],
    "candle": [(0, .25), (.05, .15), (.03, .08), (.07, .08), (.07, -.16), (.2, -.16), (.2, -.22), (-.2, -.22), (-.2, -.16), (-.07, -.16), (-.07, .08), (-.03, .08), (-.05, .15)],
    "cheese": [(-.22, -.12), (.22, -.12), (.22, .02), (-.1, .14), (-.22, .02)],
    "teapot": [(-.06, .18), (.06, .18), (.14, .08), (.24, .12), (.17, -.02), (.14, -.16), (-.14, -.16), (-.17, -.06), (-.25, -.02), (-.23, .08), (-.16, .06), (-.14, .08)],
    "scissors": [(0, .03), (.2, .2), (.23, .16), (.05, 0), (.23, -.16), (.2, -.2), (0, -.03), (-.12, -.2), (-.22, -.14), (-.22, -.06), (-.08, 0), (-.22, .06), (-.22, .14), (-.12, .2)],
    "pretzel": [(0, .06), (.1, .2), (.22, .12), (.2, -.06), (.08, -.2), (0, -.1), (-.08, -.2), (-.2, -.06), (-.22, .12), (-.1, .2)],
    "bee": [(0, .1), (.1, .22), (.2, .14), (.12, .04), (.2, -.04), (.12, -.2), (0, -.24), (-.12, -.2), (-.2, -.04), (-.12, .04), (-.2, .14), (-.1, .22)],
    "barrel": [(-.12, .22), (.12, .22), (.19, .08), (.19, -.08), (.12, -.22), (-.12, -.22), (-.19, -.08), (-.19, .08)],
    "ship": [(-.03, .24), (.14, .02), (.02, .02), (.02, -.06), (.24, -.06), (.14, -.2), (-.16, -.2), (-.24, -.06), (-.03, -.06)],
    "feather": [(.2, .24), (.22, .1), (.06, -.1), (-.16, -.24), (-.22, -.22), (-.08, -.04), (.02, .14)],
    "shell": [(0, -.2), (.1, -.14), (.22, .02), (.16, .16), (.06, .22), (0, .16), (-.06, .22), (-.16, .16), (-.22, .02), (-.1, -.14)],
}


def sign(wall, pos, z, emblem="apple", col="mustard", board="ivory", out=0.75, w=0.62, h=0.5, round_board=False):
    """A hanging shop sign like P.sign, with more emblems (see SHAPES; or give your own outline, a list of (x, z)
    points that can be seen whole from its middle) and an optional round board."""
    b = wall.b
    u = wall.U(pos)
    poly = SHAPES.get(emblem) if isinstance(emblem, str) else emblem
    if poly is None:
        return P.sign(wall, pos, z, emblem=emblem, col=col, board=board, out=out, w=w, h=h)

    def deco():
        with wall.onu(u, z):
            with b.detail(1):
                b.beam((0, -0.01, 0.06), (0, -out - 0.05, 0.06), w=0.03, mat="metal", col="iron", caps=False)
                b.beam((0, -0.01, -0.3), (0, -out * 0.6, 0.04), w=0.025, mat="metal", col="iron", caps=False)
                with b.at(0, -out * 0.55, -h / 2 - 0.08):
                    if round_board:
                        with b.at(0, 0, h / 2, ry=90):
                            b.revolve([(w / 2, -0.022), (w / 2, 0.022)], "paint", col=shade(board, 0.8), seg=12)
                            b.disc(w / 2, "paint", col=board, seg=12, z=0.022)
                            b.disc(w / 2, "paint", col=board, seg=12, z=-0.022, down=True)
                    else:
                        b.box(0.045, w, h, "paint", col=board, bottom=True)
            with b.detail(2):
                with b.at(0, -out * 0.55, -0.08):
                    for sx in (-1, 1):
                        cen = (sx * 0.03, 0, 0)
                        ring = [(sx * 0.03, -px * sx, pz) for px, pz in poly]
                        for i in range(len(ring)):
                            b.tri(cen, ring[i], ring[(i + 1) % len(ring)], "paint", col=col)
                for yy in (-out * 0.55 - w * 0.35, -out * 0.55 + w * 0.35):
                    b.beam((0, yy, 0.05), (0, yy, -0.08), w=0.015, mat="metal", col="iron", caps=False)

    wall.add(deco)


# ---------------------------------------------------------------------------------------- roof life
def deck(b, w, d, z=0.0, x=0.0, y=0.0, col="greyoak", thick=0.1, joists=0.8, joist_col="darkoak", lod=0):
    """A boarded platform w by d, centred on (x, y), its top at z."""
    with b.at(x, y, z):
        b.box(w, d, thick, "planks", col=col, z=-thick, bottom=True, lod=lod)
        if joists:
            with b.detail(1):
                n = max(2, int(d / joists) + 1)
                for i in range(n):
                    yy = -d / 2 + 0.08 + (d - 0.16) * i / (n - 1)
                    b.beam((-w / 2, yy, -thick - 0.08), (w / 2, yy, -thick - 0.08), w=0.1, h=0.16, mat="timber", col=joist_col)


def trapdoor(b, x=0.0, y=0.0, z=0.0, w=0.75, d=0.8, col="darkoak", rz=0.0):
    """A hatch lying shut in a floor: the way down from a landing place."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            b.box(w, d, 0.035, "planks", col=col, z=0.0)
            for yy in (-d * 0.3, d * 0.3):
                b.box(w * 0.9, 0.05, 0.012, "metal", col="iron", y=yy, z=0.035)
            b.box(0.12, 0.03, 0.03, "metal", col="iron", x=w * 0.3, z=0.047)


def roof_ladder(b, p0, p1, w=0.42, col="greyoak", lift=0.06, lod=2):
    """A ladder lying on a roof (or standing against anything) from p0 up to p1."""
    a = vsub(p1, p0)
    L = vlen(a)
    side = vnorm(vcross(a, (0, 0, 1))) if abs(a[0]) + abs(a[1]) > 1e-6 else (1.0, 0.0, 0.0)
    nrm = vnorm(vcross(side, a))
    off = vmul(nrm, lift)
    with b.detail(lod):
        for sgn in (-1, 1):
            s = vadd(vmul(side, sgn * w / 2), off)
            b.beam(vadd(p0, s), vadd(p1, s), w=0.05, mat="timber", col=col)
        n = max(2, int(L / 0.3))
        for i in range(1, n):
            c = vadd(vlerp(p0, p1, i / n), off)
            b.beam(vadd(c, vmul(side, -w / 2)), vadd(c, vmul(side, w / 2)), w=0.035, mat="timber", col=col, caps=False)


def parapet(b, pts, h=0.8, t=0.25, mat="plaster", col="cream", cope="ashlar", cope_col="stone", closed=False, lod=0, skip=()):
    """A low solid wall along a line of points [(x, y), ...] (its outer face on the line, its thickness to the left of
    travel) at the current height, with a coping. skip = indices of the segments to leave open."""
    P_ = list(pts) + ([pts[0]] if closed else [])
    for i in range(len(P_) - 1):
        if i in skip:
            continue
        a, c = P_[i], P_[i + 1]
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        if L < 1e-4:
            continue
        with b.at(a[0], a[1], 0, rz=math.degrees(math.atan2(c[1] - a[1], c[0] - a[0]))):
            b.box(L, t, h, mat, col=col, x=L / 2, y=t / 2, lod=lod)
            if cope:
                b.box(L + 0.06, t + 0.1, 0.08, cope, col=cope_col, x=L / 2, y=t / 2, z=h, lod=1, bottom=True)


def pergola(b, w, d, h=2.2, x=0.0, y=0.0, z=0.0, col="darkoak", n=5, vines=0.6, vine_col="#7fb760", posts="all", flowers=None):
    """A timber pergola w by d standing on (x, y, z): four posts (or 'front' two, when it leans on a wall behind),
    two beams and n cross pieces, with vines over part of it."""
    rng = b.rng
    with b.at(x, y, z):
        with b.detail(1):
            for sx in (-1, 1):
                for sy in ((-1, 1) if posts == "all" else (-1,)):
                    b.beam((sx * (w / 2 - 0.06), sy * (d / 2 - 0.06), 0), (sx * (w / 2 - 0.06), sy * (d / 2 - 0.06), h), w=0.11, mat="timber", col=col)
                b.beam((sx * (w / 2 - 0.06), -d / 2 - 0.2, h + 0.06), (sx * (w / 2 - 0.06), d / 2 + 0.2, h + 0.06), w=0.1, h=0.14, mat="timber", col=col)
        with b.detail(2):
            for i in range(n):
                yy = -d / 2 + d * (i + 0.5) / n
                b.beam((-w / 2 - 0.2, yy, h + 0.17), (w / 2 + 0.2, yy, h + 0.17), w=0.07, h=0.1, mat="timber", col=col)
        if vines:
            m = max(2, int(w * d * vines * 1.6))
            for _ in range(m):
                r = rng.uniform(0.28, 0.46)
                px, py = rng.uniform(-w / 2, w / 2), rng.uniform(-d / 2, d / 2)
                b.blob(r, r, r * 0.5, mat="ivy", col=shade(vine_col, rng.uniform(0.85, 1.15)), x=px, y=py, z=h + 0.26, lod=1, seg=6, rings=3, wind=0.3, rough=0.3)
                if flowers:
                    with b.detail(2):
                        b.blob(0.07, 0.07, 0.06, mat="paint", col=rng.choice(flowers), x=px + rng.uniform(-0.2, 0.2), y=py + rng.uniform(-0.2, 0.2), z=h + 0.26 + r * 0.45, seg=5, rings=2, wind=0.4)


def telescope(b, x=0.0, y=0.0, z=0.0, rz=0.0, tilt=12.0, h=1.15):
    """A brass telescope on a tripod, looking toward local -y."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            for k in range(3):
                a = rad(120 * k + 30)
                b.beam((0.3 * math.cos(a), 0.3 * math.sin(a), 0), (0, 0, h), w=0.035, mat="timber", col="darkoak", caps=False)
            with b.at(0, 0, h + 0.03, rx=-tilt):
                b.tube((0, 0.32, 0), (0, -0.1, 0), r=0.04, r1=0.05, mat="metal", col="brass", n=6, caps=True)
                b.tube((0, -0.1, 0), (0, -0.48, 0), r=0.055, r1=0.065, mat="metal", col="brass", n=6, caps=True)


def beehive(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="ivory"):
    """A little white hive on legs."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    b.beam((sx * 0.2, sy * 0.2, 0), (sx * 0.2, sy * 0.2, 0.22), w=0.05, mat="timber", col="darkoak", caps=False)
            for i in range(3):
                b.box(0.5 - i * 0.03, 0.5 - i * 0.03, 0.2, "planks", col=shade(col, 1.0 - 0.05 * (i % 2)), z=0.22 + 0.2 * i)
            for sgn in (1, -1):
                pts = [(sgn * 0.31, -0.31, 0.8), (sgn * 0.31, 0.31, 0.8), (0, 0.31, 0.98), (0, -0.31, 0.98)]
                b.face(pts if sgn > 0 else list(reversed(pts)), "planks", col=shade(col, 0.82))
            b.tri((-0.31, -0.31, 0.8), (0.31, -0.31, 0.8), (0, -0.31, 0.98), "planks", col=shade(col, 0.9))
            b.tri((0.31, 0.31, 0.8), (-0.31, 0.31, 0.8), (0, 0.31, 0.98), "planks", col=shade(col, 0.9))
            b.box(0.16, 0.02, 0.03, "paint", col="black", y=-0.25, z=0.24)


def roof_window(b, x, y, z, pitch, face=0.0, w=0.7, h=0.9, frame="lead"):
    """A small glazed light lying in a roof slope: (x, y, z) = the middle of its lower edge on the tiles,
    face = the compass direction the slope looks toward, pitch = the slope in degrees."""
    with b.at(x, y, z, rz=face):
        with b.at(rx=pitch):
            with b.detail(1):
                b.box(w, h, 0.09, "metal", col=frame, y=h / 2, z=0.0)
                b.box(w - 0.12, h - 0.12, 0.012, "glass", y=h / 2, z=0.09)
            with b.detail(2):
                b.beam((0, 0.06, 0.1), (0, h - 0.06, 0.1), w=0.03, h=0.02, mat="metal", col=frame, caps=False)


def cat(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="#3b3632", s=1.0, bib=None):
    """A cat sitting, looking toward local -y."""
    with b.at(x, y, z, rz=rz, s=s):
        with b.detail(2):
            b.blob(0.105, 0.13, 0.15, mat="paint", col=col, z=0.14, seg=6, rings=3, rough=0.06)
            b.blob(0.078, 0.078, 0.07, mat="paint", col=col, y=-0.085, z=0.33, seg=6, rings=3, rough=0.04)
            if bib:
                b.blob(0.05, 0.03, 0.07, mat="paint", col=bib, y=-0.115, z=0.2, seg=5, rings=2, rough=0.05)
            for sx in (-1, 1):
                e = [(sx * 0.07, -0.08, 0.37), (sx * 0.02, -0.08, 0.39), (sx * 0.055, -0.075, 0.455)]
                b.face(e, "paint", col=col); b.face(list(reversed(e)), "paint", col=col)
            b.beam((0.06, 0.1, 0.03), (0.17, 0.02, 0.03), w=0.035, mat="paint", col=col, caps=False)
            b.beam((0.17, 0.02, 0.03), (0.16, -0.1, 0.035), w=0.03, mat="paint", col=col, caps=True)


def gull(b, x=0.0, y=0.0, z=0.0, rz=0.0):
    """A gull standing, looking toward local -y."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            b.blob(0.075, 0.15, 0.075, mat="paint", col="#f6f5ef", z=0.16, seg=6, rings=3, rough=0.05)
            b.blob(0.05, 0.055, 0.05, mat="paint", col="#f6f5ef", y=-0.13, z=0.26, seg=5, rings=2, rough=0.04)
            for sx in (-1, 1):
                wg = [(sx * 0.078, -0.06, 0.2), (sx * 0.078, 0.2, 0.15), (sx * 0.072, 0.02, 0.11)]
                b.face(wg if sx > 0 else list(reversed(wg)), "paint", col="#9aa3ab")
                b.beam((sx * 0.03, 0.0, 0.0), (sx * 0.03, 0.0, 0.1), w=0.012, mat="paint", col="#e8a23a", caps=False)
            bk = [(-0.015, -0.17, 0.26), (0.015, -0.17, 0.26), (0.0, -0.24, 0.245)]
            b.face(bk, "paint", col="#e8a23a"); b.face(list(reversed(bk)), "paint", col="#e8a23a")


# ---------------------------------------------------------------------------------------- the street
def flowerpot(b, x=0.0, y=0.0, z=0.0, r=0.15, h=0.24, plant="#7db45e", flower=None, tall=1.0):
    """A terracotta pot with a plant in it (flower = colour of its blooms, or None for a green shrub)."""
    rng = b.rng
    with b.at(x, y, z):
        with b.detail(2):
            b.revolve([(r * 0.68, 0.0), (r, h), (r * 1.1, h), (r * 1.1, h + 0.035), (r * 0.9, h + 0.035)], "paint", col="#c9764a", seg=7)
            b.blob(r * 1.15, r * 1.15, r * 1.2 * tall, mat="ivy", col=plant, z=h + r * 0.9 * tall, seg=5, rings=3, wind=0.3, rough=0.25)
            if flower:
                for k in range(4):
                    a = rng.uniform(0, 6.28)
                    b.blob(0.05, 0.05, 0.045, mat="paint", col=flower, x=math.cos(a) * r * 0.8, y=math.sin(a) * r * 0.8, z=h + r * (1.0 + 0.9 * rng.random()) * tall, seg=5, rings=2, wind=0.45)


def stall(b, x=0.0, y=0.0, z=0.0, w=1.8, d=0.6, rz=0.0, goods=("#d9432f", "#e8a23a", "#7fb04a", "#f0d24a"), cloth=None):
    """A trestle table of crates heaped with goods, standing in front of a shop."""
    rng = b.rng
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            b.box(w, d, 0.05, "planks", col="greyoak", z=0.62, bottom=True)
            for sx in (-1, 1):
                b.beam((sx * (w / 2 - 0.15), -d / 2 + 0.04, 0), (sx * (w / 2 - 0.15), 0, 0.62), w=0.05, mat="timber", col="darkoak", caps=False)
                b.beam((sx * (w / 2 - 0.15), d / 2 - 0.04, 0), (sx * (w / 2 - 0.15), 0, 0.62), w=0.05, mat="timber", col="darkoak", caps=False)
            if cloth:
                b.box(w + 0.04, d + 0.04, 0.02, "cloth", col=cloth, z=0.67)
            n = max(1, int(w / 0.55))
            for i in range(n):
                cx = -w / 2 + w * (i + 0.5) / n
                gc = goods[i % len(goods)]
                with b.at(cx, 0, 0.69, rx=12):
                    b.box(0.46, d - 0.12, 0.16, "planks", col="#d8c3a0", cap="planks", capcol="#8a7358")
                    for k in range(5):
                        b.blob(0.075, 0.075, 0.065, mat="paint", col=shade(gc, rng.uniform(0.85, 1.1)), x=rng.uniform(-0.15, 0.15), y=rng.uniform(-0.14, 0.14), z=0.19 + 0.03 * (k % 2), seg=5, rings=2, rough=0.1)


def logs(b, x=0.0, y=0.0, z=0.0, w=1.6, h=0.9, d=0.5, r=0.085, rz=0.0, col="#b08a62"):
    """A stack of firewood w wide and h high against a wall behind it (the logs point at the street, local -y)."""
    rng = b.rng
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            rows = max(1, int(h / (r * 1.8)))
            for j in range(rows):
                n = max(1, int(w / (r * 2.05)))
                for i in range(n):
                    if j == rows - 1 and rng.random() < 0.35:
                        continue
                    cx = -w / 2 + r + (w - 2 * r) * (i + 0.5 * (j % 2)) / max(n, 1)
                    if cx > w / 2 - r:
                        continue
                    rr = r * rng.uniform(0.8, 1.05)
                    cz = r + j * r * 1.8
                    yo = rng.uniform(-0.04, 0.04)
                    b.tube((cx, d / 2 + yo, cz), (cx, -d / 2 + yo, cz), r=rr, mat="timber", col=shade("#c9b08e", rng.uniform(0.8, 1.1)), n=5, smooth=False)
                    ang = [2 * math.pi * k / 5 for k in range(5)]
                    b.face([(cx + rr * math.cos(a), -d / 2 + yo, cz + rr * math.sin(a)) for a in ang], "planks", col=shade(col, rng.uniform(0.9, 1.25)))


def trough(b, x=0.0, y=0.0, z=0.0, w=2.6, d=0.8, h=0.62, t=0.12, rz=0.0, mat="ashlar", col="grey", water=0.1):
    """A stone trough full of water, centred on (x, y)."""
    with b.at(x, y, z, rz=rz):
        b.box(w, d, h, mat, col=col, top=False, lod=1)
        hw, hd = w / 2, d / 2
        O = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]
        I = [(-hw + t, -hd + t), (hw - t, -hd + t), (hw - t, hd - t), (-hw + t, hd - t)]
        with b.detail(1):
            for i in range(4):
                j = (i + 1) % 4
                b.quad((O[i][0], O[i][1], h), (O[j][0], O[j][1], h), (I[j][0], I[j][1], h), (I[i][0], I[i][1], h), mat, col=shade(col, 1.08))
                b.quad((I[j][0], I[j][1], h - water - 0.3), (I[i][0], I[i][1], h - water - 0.3), (I[i][0], I[i][1], h), (I[j][0], I[j][1], h), mat, col=shade(col, 0.8))
            b.quad((I[0][0], I[0][1], h - water), (I[1][0], I[1][1], h - water), (I[2][0], I[2][1], h - water), (I[3][0], I[3][1], h - water), "water", col="#9fd6dc")


def pump(b, x=0.0, y=0.0, z=0.0, rz=0.0, h=1.25, col="iron"):
    """A cast-iron hand pump, its spout toward local -y."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            b.revolve([(0.13, 0.0), (0.11, 0.1), (0.075, 0.16), (0.075, h - 0.12), (0.1, h - 0.08), (0.1, h), (0.04, h + 0.1), (0.0, h + 0.12)], "metal", col=col, seg=8)
        with b.detail(2):
            b.beam((0, -0.05, h - 0.3), (0, -0.34, h - 0.36), w=0.07, mat="metal", col=col)
            b.beam((0, -0.34, h - 0.36), (0, -0.34, h - 0.46), w=0.06, mat="metal", col=col)
            b.beam((0, 0.05, h - 0.05), (0, 0.5, h - 0.45), w=0.04, mat="metal", col=col)
            b.box(0.07, 0.07, 0.07, "metal", col="brass", y=0.5, z=h - 0.5, bottom=True)


def handcart(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="greyoak", load=None):
    """A two-wheeled handcart, its shafts toward local -y. load = colours of what is heaped on it."""
    rng = b.rng
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            b.box(0.8, 1.2, 0.06, "planks", col=col, z=0.5, bottom=True)
            for sx in (-1, 1):
                b.box(0.04, 1.2, 0.26, "planks", col=col, x=sx * 0.4, z=0.56, bottom=True)
                b.tube((sx * 0.46, 0.1, 0.36), (sx * 0.5, 0.1, 0.36), r=0.36, mat="planks", col="darkoak", n=10, caps=True)
                b.beam((sx * 0.38, -0.6, 0.55), (sx * 0.33, -1.35, 0.72), w=0.05, mat="timber", col="darkoak")
            b.box(0.8, 0.04, 0.26, "planks", col=col, y=0.6, z=0.56, bottom=True)
            b.beam((0, -0.5, 0.5), (0, -0.55, 0.0), w=0.05, mat="timber", col="darkoak")
            for k, c in enumerate(load or ()):
                b.blob(0.2, 0.2, 0.15, mat="cloth", col=c, x=rng.uniform(-0.18, 0.18), y=-0.4 + 0.33 * k, z=0.68, seg=6, rings=3, rough=0.12)


def peel(b, x=0.0, y=0.0, z=0.0, rz=0.0, h=2.3, lean=0.35):
    """A baker's peel leaning against the wall behind it (at local +y)."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            b.beam((0, -lean, 0), (0, 0, h - 0.4), w=0.04, mat="planks", col="#d8c3a0", caps=False)
            with b.at(0, 0.0, h - 0.42, rx=-8):
                b.box(0.34, 0.03, 0.46, "planks", col="#d8c3a0", bottom=True)


def column(b, x=0.0, y=0.0, z=0.0, r=0.2, h=2.6, mat="ashlar", col="stone", seg=10, lod=0, square=0.0):
    """A stout stone column standing on (x, y, z) and carrying something h above it: base, swelling shaft, capital."""
    with b.at(x, y, z):
        b.box(r * 2.7, r * 2.7, 0.14, mat, col=col, lod=lod)
        b.revolve([(r * 1.3, 0.14), (r * 1.3, 0.2), (r * 1.05, 0.3), (r * 1.06, h * 0.4), (r * 0.92, h - 0.32), (r * 1.08, h - 0.28), (r * 1.3, h - 0.14)], mat, col=col, seg=seg, lod=lod)
        b.box(r * 2.9, r * 2.9, 0.14, mat, col=col, z=h - 0.14, lod=lod, bottom=True)


def downpipe(b, x, y, z0, z1, r=0.05, col="lead", butt=False, face=0.0):
    """A rainwater pipe down a wall from z1 to z0 at (x, y): give the point 6 cm off the wall, and face = the compass
    direction the wall looks (0 front, 90 right, 180 back, 270 left). butt=True ends it in a water butt."""
    ox, oy = math.sin(rad(face)), -math.cos(rad(face))
    with b.detail(2):
        b.tube((x, y, z1), (x, y, z0 + (0.8 if butt else 0.14)), r=r, mat="metal", col=col, n=5)
        if not butt:
            b.tube((x, y, z0 + 0.14), (x + ox * 0.18, y + oy * 0.18, z0 + 0.03), r=r, mat="metal", col=col, n=5)
        b.box(r * 3.4, r * 3.4, 0.16, "metal", col=col, x=x, y=y, z=z1 - 0.04, bottom=True)
    if butt:
        P.barrel(b, x + ox * 0.2, y + oy * 0.2, z0, r=0.25, h=0.78, col="#a9c0c4")


def gutter(b, p0, p1, r=0.07, col="lead"):
    """A half-round gutter from p0 to p1 (under an eave)."""
    with b.detail(2):
        b.tube(p0, p1, r=r, mat="metal", col=col, n=5, caps=True)


def bunting(b, p0, p1, n=9, sag=0.3, cols=("stripe_red", "stripe_yellow", "stripe_blue", "linen", "stripe_green"), s=0.26):
    """A string of little flags from p0 to p1."""
    N = 8
    pt = lambda t: (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t) - sag * 4 * t * (1 - t))
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1.0
    dx, dy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    with b.detail(2):
        for i in range(N):
            b.beam(pt(i / N), pt((i + 1) / N), w=0.015, mat="cloth", col="#8a7a66", caps=False)
        for k in range(n):
            c = pt((k + 0.5) / n)
            col = C(cols[k % len(cols)])
            p = [(c[0] - dx * s / 2, c[1] - dy * s / 2, c[2]), (c[0], c[1], c[2] - s * 1.2), (c[0] + dx * s / 2, c[1] + dy * s / 2, c[2])]
            b.face(p, "cloth", col=col, wind=(0.1, 0.8, 0.1))
            b.face(list(reversed(p)), "cloth", col=shade(col, 0.88), wind=(0.1, 0.8, 0.1))


def jetty(b, x0, x1, y, out, z, n=None, col="darkoak", brackets=True, beam=True, face=0.0):
    """The timbers under an overhanging storey: joist ends, a bressummer along the foot of the wall above, and a
    curved bracket at each end. y = the face of the wall below, out = how far the storey above sails over it,
    z = its underside. (Front walls by default; for a side that oversails, wrap it in b.at(..., rz=...).)"""
    n = n or max(3, int((x1 - x0) / 0.55))
    with b.detail(1):
        if beam:
            b.beam((x0, y - out - 0.025, z + 0.1), (x1, y - out - 0.025, z + 0.1), w=0.13, h=0.22, mat="timber", col=col)
        if brackets:
            for x in (x0 + 0.09, x1 - 0.09):
                b.beam((x, y - 0.02, z - 0.62), (x, y - out * 0.55, z - 0.3), w=0.12, mat="timber", col=col, caps=False)
                b.beam((x, y - out * 0.55, z - 0.3), (x, y - out + 0.02, z - 0.1), w=0.12, mat="timber", col=col, caps=False)
    with b.detail(2):
        for i in range(n):
            x = x0 + (x1 - x0) * (i + 0.5) / n
            b.beam((x, y + 0.02, z - 0.09), (x, y - out - 0.07, z - 0.09), w=0.12, h=0.16, mat="timber", col=col)


def ball(b, x=0.0, y=0.0, z=0.0, r=0.16, mat="ashlar", col="stone", lod=1, neck=True):
    """A stone ball finial standing on (x, y, z)."""
    with b.at(x, y, z):
        with b.detail(lod):
            prof = [(r * 0.55, 0.0), (r * 0.4, r * 0.35)] if neck else []
            k = r * 0.35 if neck else 0.0
            prof += [(r * math.sin(rad(a)), k + r - r * math.cos(rad(a))) for a in (35, 65, 90, 115, 145)] + [(0.0, k + 2 * r)]
            b.revolve(prof, mat, col=col, seg=7)


def shaped_wall(b, outline, t=0.26, mat="plaster", col="cream", lod=0, cope=None, cope_col="stone"):
    """A free-standing shaped piece of wall (a parapet with a curved or stepped head): outline = convex [(x, z), ...]
    anticlockwise seen from the front, standing in the current frame with its face on y = 0 and its back at y = t.
    cope = material for a thin capping laid along its upper edges."""
    with b.at(0, t, 0, rx=90):
        b.prism(outline, t, mat, col=col, lod=lod, top=True, bottom=True)
    if cope:
        with b.detail(1):
            n = len(outline)
            for i in range(n):
                a, c = outline[i], outline[(i + 1) % n]
                if abs(a[1]) < 1e-6 and abs(c[1]) < 1e-6:
                    continue
                if abs(a[0] - c[0]) < 1e-6:
                    continue
                b.beam((a[0], t / 2, a[1] + 0.03), (c[0], t / 2, c[1] + 0.03), w=t + 0.1, h=0.08, mat=cope, col=cope_col, up=(0, 0, 1))


def herbs(b, p0, p1, n=7, drop=0.12, cols=("#8fae6a", "#a99bc9", "#c9b86a", "#7d9a5a")):
    """Bunches of herbs hung to dry along a line from p0 to p1 (under an eave, across a window)."""
    rng = b.rng
    with b.detail(2):
        b.beam(p0, p1, w=0.015, mat="cloth", col="#8a7a66", caps=False)
        for i in range(n):
            c = vlerp(p0, p1, (i + 0.5) / n)
            hh = rng.uniform(0.26, 0.4)
            b.blob(0.07, 0.07, hh / 2, mat="ivy", col=rng.choice(cols), x=c[0], y=c[1], z=c[2] - drop - hh / 2, seg=5, rings=2, rough=0.25, wind=0.3)


def straw_bird(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="#f2d9a0"):
    """The thatcher's signature: a straw bird on the ridge, looking toward local -y."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            b.blob(0.1, 0.2, 0.1, mat="thatch", col=col, z=0.16, seg=6, rings=3, rough=0.08)
            b.blob(0.065, 0.07, 0.065, mat="thatch", col=col, y=-0.2, z=0.3, seg=5, rings=2, rough=0.05)
            for sx in (-1, 1):
                tl = [(0.0, 0.14, 0.2), (sx * 0.1, 0.42, 0.34), (0.0, 0.4, 0.22)]
                b.face(tl if sx > 0 else list(reversed(tl)), "thatch", col=col)
                b.face(list(reversed(tl)) if sx > 0 else tl, "thatch", col=shade(col, 0.8))
            b.beam((0, 0, 0.0), (0, 0, 0.1), w=0.03, mat="thatch", col=col, caps=False)


def bean_poles(b, x=0.0, y=0.0, z=0.0, r=0.3, h=1.9, n=4, leaf="#7db45e", bloom="#e85d3a"):
    """A wigwam of canes with beans climbing it, in a tub."""
    rng = b.rng
    with b.at(x, y, z):
        with b.detail(2):
            b.revolve([(r * 0.95, 0.0), (r * 1.1, 0.34), (r * 0.95, 0.34)], "planks", col="#b58a66", seg=8)
            b.disc(r * 0.95, "ivy", col="#6b5a45", seg=8, z=0.3)
            for k in range(n):
                a = 2 * math.pi * k / n + 0.4
                b.beam((r * 0.8 * math.cos(a), r * 0.8 * math.sin(a), 0.3), (0.03 * math.cos(a), 0.03 * math.sin(a), h), w=0.025, mat="timber", col="greyoak", caps=False)
            for k in range(5):
                t = (k + 0.6) / 5.5
                rr = r * (1.0 - t * 0.75) * 0.8
                b.blob(rr + 0.08, rr + 0.08, 0.16, mat="ivy", col=shade(leaf, rng.uniform(0.85, 1.15)), z=0.34 + (h - 0.5) * t, seg=6, rings=2, rough=0.3, wind=0.3)
                a = rng.uniform(0, 6.28)
                b.blob(0.045, 0.045, 0.04, mat="paint", col=bloom, x=(rr + 0.1) * math.cos(a), y=(rr + 0.1) * math.sin(a), z=0.36 + (h - 0.5) * t, seg=5, rings=2, wind=0.4)


def anchor(b, x=0.0, y=0.0, z=0.0, rz=0.0, h=1.25, lean=14.0, col="iron"):
    """An old iron anchor leaning against the wall behind it (at local +y)."""
    with b.at(x, y, z, rz=rz):
        with b.at(rx=lean):
            with b.detail(2):
                b.beam((0, 0, 0.12), (0, 0, h), w=0.07, mat="metal", col=col)
                b.beam((-h * 0.3, 0, h - 0.14), (h * 0.3, 0, h - 0.14), w=0.06, mat="planks", col="darkoak")
                for sx in (-1, 1):
                    b.beam((0, 0, 0.12), (sx * h * 0.22, 0, 0.16), w=0.07, mat="metal", col=col, caps=False)
                    b.beam((sx * h * 0.22, 0, 0.16), (sx * h * 0.34, 0, 0.42), w=0.07, mat="metal", col=col)
                b.revolve([(0.05, h), (0.08, h + 0.04), (0.08, h + 0.1), (0.05, h + 0.14)], "metal", col=col, seg=6)


def barge_boards(bd, rise, eave=0.15, verge=0.3, ends="fb", depth=0.27, t=0.06, col="darkoak", lift=0.05, lod=1):
    """Upright barge boards with plumb-cut feet for a roof whose ridge runs front to back over a body (give that
    roof barge=False). The kit's own boards end square and their corner pokes 12 cm past the eave, which matters
    when the eaves run to the edge of the lot; these stop on the eave line."""
    b = bd.b
    a = bd.w / 2
    k = rise / a
    ze = -eave * k
    dv = depth * math.hypot(1.0, k)
    for key, y in (("f", bd.y - bd.d / 2 - verge), ("b", bd.y + bd.d / 2 + verge + t)):
        if key not in ends:
            continue
        with b.at(0, y, bd.z + bd.h, rx=90):
            with b.detail(lod):
                for sgn in (1, -1):
                    o = [(bd.x + sgn * (a + eave), ze + lift - dv), (bd.x + sgn * (a + eave), ze + lift), (bd.x, rise + lift), (bd.x, rise + lift - dv)]
                    b.prism(o if sgn > 0 else list(reversed(o)), t, "planks", col=col, top=True, bottom=True)


def saddle(b, p0, p1, pitch, w=0.5, lift=0.07, mat="thatch", col=None, lod=0, scallop=0.0, step=0.45):
    """A raised capping along a level ridge from p0 to p1 (a thatcher's block ridge, a lead saddle): a strip w wide
    lying down the slope on either side, standing lift proud of the roof. scallop = how deep its lower edge is
    cut into points."""
    col = C(col)
    a = vsub(p1, p0)
    L = vlen(a)
    d = vnorm(a)
    s = (d[1], -d[0], 0.0)
    cp, sp = math.cos(rad(pitch)), math.sin(rad(pitch))
    n = max(2, int(L / step))
    for sgn in (1, -1):
        hi = [vadd(vlerp(p0, p1, i / n), (0, 0, lift)) for i in range(n + 1)]
        lo = []
        for i in range(n + 1):
            ww = w - (scallop if i % 2 else 0.0)
            q = vlerp(p0, p1, i / n)
            lo.append((q[0] + sgn * s[0] * ww * cp, q[1] + sgn * s[1] * ww * cp, q[2] - ww * sp + lift))
        for i in range(n):
            ck = shade(col, b.r(0.9, 1.06))
            q = (lo[i], lo[i + 1], hi[i + 1], hi[i])
            e = (vsub(lo[i], (0, 0, lift)), vsub(lo[i + 1], (0, 0, lift)), lo[i + 1], lo[i])
            if sgn < 0:
                q, e = tuple(reversed(q)), tuple(reversed(e))
            b.face(q, mat, col=ck, lod=lod)
            b.face(e, mat, col=shade(ck, 0.75), lod=lod)


def hip_roof(b, w, d, pitch=45.0, x=0.0, y=0.0, z=0.0, eave=0.3, mat="tiles", col=None, course=0.42, lip=0.045, thick=0.14, rolls=True,
             gap=None, cut=None, top="metal", top_col="lead", roll_mat=None, roll_col=None, lod=0):
    """A hipped roof over a w by d block (wall tops at z, centred on (x, y)): four coursed faces, with ridge tiles
    down the hips and along the ridge (the kit's loop_roof has neither).
    eave = one overhang, or four (front, right, back, left): a corner house wants deep eaves to its streets and
    tight ones to its neighbours. gap = (x0, x1, depth) leaves the front slope open between x0 and x1 (measured
    from the block's middle) for `depth` back from the wall line: for a gabled wall-dormer that breaks the eaves.
    cut = a height above z at which the roof is cut off flat (a pavilion roof with a lead flat).
    Returns (rise above z, ends): the two ends of the ridge as (x, y, z) in the caller's frame, or with cut the
    front-left and back-right corners of the flat."""
    tp = math.tan(rad(pitch))
    eF, eR, eB, eL = (eave,) * 4 if not isinstance(eave, (tuple, list)) else eave
    em = max(eF, eR, eB, eL)
    a, c = w / 2 + em, d / 2 + em
    ze, zt = -em * tp, min(w, d) / 2 * tp
    if w <= d:
        T0, T1 = (0.0, -(d - w) / 2, zt), (0.0, (d - w) / 2, zt)
        faces = [[(-a, -c, ze), (a, -c, ze), T0], [(a, -c, ze), (a, c, ze), T1, T0], [(a, c, ze), (-a, c, ze), T1], [(-a, c, ze), (-a, -c, ze), T0, T1]]
    else:
        T0, T1 = (-(w - d) / 2, 0.0, zt), ((w - d) / 2, 0.0, zt)
        faces = [[(-a, -c, ze), (a, -c, ze), T1, T0], [(a, -c, ze), (a, c, ze), T1], [(a, c, ze), (-a, c, ze), T0, T1], [(-a, c, ze), (-a, -c, ze), T0]]
    box = (-w / 2 - eL, w / 2 + eR, -d / 2 - eF, d / 2 + eB)

    def trim(f):
        f = _clip(f, 0, box[0], box[1])
        f = _clip(f, 1, box[2], box[3]) if f else f
        if f and cut is not None:
            f = _clip(f, 2, -1e9, cut)
        return f

    faces = [trim(f) for f in faces]
    if gap and faces[0]:
        x0, x1, depth = gap
        run = min(w, d) / 2 + eF
        n = max(1, round(run / math.cos(rad(pitch)) / course))
        hs = run / n
        ys = box[2] + math.ceil((depth + eF) / hs - 1e-6) * hs
        f = faces[0]
        mid = _clip(f, 0, x0, x1)
        mid = _clip(mid, 1, ys, 1e9) if mid else mid
        faces = [_clip(f, 0, -1e9, x0), _clip(f, 0, x1, 1e9), mid] + faces[1:]

    def edge(p, q):
        return any(abs(p[k] - v) < 1e-6 and abs(q[k] - v) < 1e-6 for k, v in ((0, box[0]), (0, box[1]), (1, box[2]), (1, box[3])))

    rm, rc = roll_mat or mat, col if roll_col is None else roll_col
    with b.at(x, y, z):
        for f in faces:
            if len(f) < 3:
                continue
            rim = [i for i in range(len(f)) if edge(f[i], f[(i + 1) % len(f)])]
            roof_face(b, f, mat, col, course=course, lip=lip, lod=lod, thick=thick, rim=rim)
        zc = zt if cut is None else min(cut, zt)
        if cut is not None and cut < zt:
            hx, hy = w / 2 - cut / tp, d / 2 - cut / tp
            b.face([(-hx, -hy, cut), (hx, -hy, cut), (hx, hy, cut), (-hx, hy, cut)], top, col=top_col, lod=lod)
        if rolls:
            for (sx, sy, T) in ((-1, -1, T0), (1, -1, T0 if w <= d else T1), (1, 1, T1), (-1, 1, T1 if w <= d else T0)):
                e = min(eL if sx < 0 else eR, eF if sy < 0 else eB)
                p0 = (sx * (w / 2 + e), sy * (d / 2 + e), -e * tp)
                p1 = T if zc >= zt else (sx * (w / 2 - zc / tp), sy * (d / 2 - zc / tp), zc)
                ridge_roll(b, vlerp(p0, p1, 0.07), p1, rm, rc, w=0.22, h=0.12)
            if zc >= zt and vlen(vsub(T1, T0)) > 0.2:
                ridge_roll(b, T0, T1, rm, rc)
    if cut is not None and cut < zt:
        hx, hy = w / 2 - cut / tp, d / 2 - cut / tp
        return cut, [(x - hx, y - hy, z + cut), (x + hx, y + hy, z + cut)]
    return zt, [(x + T0[0], y + T0[1], z + zt), (x + T1[0], y + T1[1], z + zt)]


class Walls:
    """A group of flat walls standing in for a kit Body, for parts that only need its walls (P.plinth ...)."""

    def __init__(self, b, walls, front=None):
        self.b, self.walls = b, list(walls)
        self.front = front or self.walls[0]


def outline_walls(b, pts, h, mat="plaster", col=None, z=0.0, depth=0.24, lod=0, closed=True):
    """Walls along an outline of (x, y) points given anticlockwise seen from above (so that each wall faces out):
    for ground plans that are not a rectangle - a chamfered corner, a recess. Returns the list of Walls, one per
    side, in order; positions along each run from the first of its two points."""
    P_ = list(pts) + ([pts[0]] if closed else [])
    out = []
    for a, c in zip(P_, P_[1:]):
        with b.at(a[0], a[1], z, rz=math.degrees(math.atan2(c[1] - a[1], c[0] - a[0]))):
            out.append(b.wall(math.hypot(c[0] - a[0], c[1] - a[1]), h, mat, col, depth=depth, lod=lod))
    return out
