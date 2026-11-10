"""Larkhaven market-district parts (the m_ buildings): what the kit's parts.py does not have.

  roofs      lean_to, pent, cone_part
  walls      arcade (a two-sided wall with open arches), gable_holes (windows in a gable), plinth (a base course
             on chosen sides only), quoins (cheap), buttress, corbel, corbel_ring, corbel_table, joists (jetty),
             parapet, steps, putlogs, sundial
  openings   round_window, mullioned, surround, louvres, shopfront, bay (bay windows and oriels), half_door, counter
  roofscape  stack (a big shouldered chimney), weathercock
  street     sign (shaped boards, more emblems), bunting, hoist, pigeonholes
  life       cat, pigeon, table, chair, parasol, produce, display (loaves, bottles, books, fruit ...), stall

Conventions as in parts.py: `s` is a wall (a flat Wall, or a round Ring where it says so) and positions on it are
metres from its left end (degrees on a Ring); `b` is the Building and the part is drawn in the current frame.
Kit facts behind some of these parts: a Wall(back=...) is not see-through (use arcade); openings cannot be cut
in a gable (use gable_holes); P.door(steps=n) stacks its slabs upside down for n > 1 (use steps). lean_to and
plinth here are conveniences over b.gable_roof(half=True) and P.plinth (a compass direction; chosen sides only).
"""
import math

from kit import C, M, PAL, lerp, mix, rad, shade, vadd, vcross, vmul, vnorm, vsub
import parts as P

FRUIT = ["#d8432e", "#e88a2a", "#f0c53a", "#7fae3f", "#b3202e", "#e9d9a0", "#8d5ba8"]
BREAD = ["#c98b4a", "#dba55c", "#b9763a", "#e2b877"]
BOOKS = ["#8a3b34", "#2f4f6f", "#3f6b4a", "#c9a24a", "#6a4a6f", "#d9c9a3", "#274a4a"]
BOTTLES = ["#2f8f8f", "#c9862e", "#7a4672", "#5a9a68", "#b5433a", "#3f6fb5"]
DARK = "!#26211e"          # the inside of an open door or hatch


# ---------------------------------------------------------------------------------------- roofs
def lean_to(b, w, run, pitch=28.0, x=0.0, y=0.0, z=0.0, face=0.0, mat="tiles", col=None, eave=0.3, verge=0.25, **kw):
    """A single-slope roof, w long. Its HIGH edge runs along a wall through (x, y); its low eave is `run` away toward
    compass `face` (0 = toward the front, 90 = +x, 180 = the back, 270 = -x). z = the height of the low edge (the top of
    the outer wall it rests on). Returns the rise: the top edge meets the wall at z + rise. Other arguments as
    b.gable_roof (course, thick, sag, barge ...)."""
    with b.at(x, y, z, rz=face):
        return b.gable_roof(w, run, pitch=pitch, mat=mat, col=col, ridge="x", half=True, eave=eave, verge=verge, **kw)


def pent(s, pos, z, w=3.0, out=0.9, pitch=26.0, mat="tiles", col=None, brackets=True, lod=1, course=0.3, bracket_col="darkoak"):
    """A pentice: a little tiled canopy on a flat wall, over a shop front or a door. z = where its top edge meets the
    wall; it slopes out and down `out` from there, carried on two timber brackets."""
    b = s.b
    u = s.U(pos)
    rise = out * math.tan(rad(pitch))

    def deco():
        with s.onu(u, z - rise):
            with b.detail(lod):
                lean_to(b, w, out, pitch, mat=mat, col=col, eave=0.1, verge=0.06, course=course, thick=0.07, barge=False, lod=lod)
                if brackets:
                    for sgn in (-1, 1):
                        x = sgn * (w / 2 - 0.12)
                        b.beam((x, -0.02, -0.55), (x, -out + 0.08, -0.06), w=0.08, mat="timber", col=bracket_col)
                        b.beam((x, -0.02, -0.07), (x, -out + 0.04, -0.07), w=0.08, mat="timber", col=bracket_col)

    s.add(deco)


def cone_part(b, r, h, a0=90.0, a1=270.0, mat="slate", col=None, x=0.0, y=0.0, z=0.0, seg=10, eave=0.3, flare=0.3, course=0.5, lip=0.05,
              smooth=True, soffit="planks", soffit_col="darkoak", lod=0, section=None):
    """Part of a conical roof (over an apse, a half-round bay or stair turret against a wall): as b.cone_roof, but only
    from compass a0 round to a1 (90..270 = the back half), with `seg` sides in that arc. No finial."""
    col = C(col)
    with b.at(x, y, z):
        if section is None:
            re = r + eave
            k = 0.22
            section = [(re, -eave * (h / r) * (1.0 - flare) * 0.9), (r * (1 - k), h * k * (1.0 - flare * 0.55)), (0.0, h)]
        sec = [(section[0][0] - p[0], p[1]) for p in section]
        stepped, _ = b._courses(sec, course, lip)
        prof = [(max(section[0][0] - run, 0.0), zz) for run, zz in stepped]
        cols = [shade(col, b.r(0.86, 1.08)) for _ in range(len(prof) - 1)]
        b.revolve(prof, mat, col=col, lod=lod, seg=seg, a0=a0, a1=a1, smooth=smooth, rref=section[0][0], cols=cols)
        re, ze, ri = section[0][0], section[0][1] - 0.02, max(r - 0.05, 0.0)
        pt = lambda rr, a: (rr * math.sin(rad(a)), -rr * math.cos(rad(a)), ze)
        for i in range(seg):
            a, c = a0 + (a1 - a0) * i / seg, a0 + (a1 - a0) * (i + 1) / seg
            b.face([pt(ri, c), pt(re, c), pt(re, a), pt(ri, a)], soffit, col=soffit_col, lod=lod)
    return h


# ---------------------------------------------------------------------------------------- walls
def arcade(b, w, h, thick=0.5, arches=(), mat="ashlar", col="stone", lod=0, top=True, ends="lr", back_mat=None, back_col=None):
    """A free-standing wall with open arches you can see (and fly) through: w long, h high, `thick` deep, standing in
    the current frame like b.wall (front face in the x-z plane facing -y, the thickness behind it toward +y).
    arches = [(u, width, height, arch_rise[, z0]), ...]: u = centre in metres from the left end, height in all,
    arch_rise = how much of it is the curved head, z0 = sill height (default 0). Returns (front, back): both are real
    Walls, so windows, stones and so on can be added to either (positions on the back run from ITS left end:
    u_back = w - u_front)."""
    f = b.wall(w, h, mat, col, depth=thick / 2, lod=lod)
    with b.at(w, thick, 0, rz=180):
        k = b.wall(w, h, back_mat or mat, col if back_col is None else back_col, depth=thick / 2, lod=lod)
    for a in arches:
        u, aw, ah, ar = a[:4]
        z0 = a[4] if len(a) > 4 else 0.0
        f.opening(u, z0, aw, ah, arch=ar, pane=None)
        k.opening(w - u, z0, aw, ah, arch=ar, pane=None)
    if top:
        b.quad((0, 0, h), (w, 0, h), (w, thick, h), (0, thick, h), mat, col=col, lod=lod)
    if "l" in ends:
        b.quad((0, thick, 0), (0, 0, 0), (0, 0, h), (0, thick, h), mat, col=col, lod=lod)
    if "r" in ends:
        b.quad((w, 0, 0), (w, thick, 0), (w, thick, h), (w, 0, h), mat, col=col, lod=lod)
    return f, k


def gable_holes(wl):
    """Let windows be cut in the triangular gable of a wall. Call it once after body.gable(...); then openings whose
    z lies above the wall's height (P.window, round_window, mullioned ...) really pierce the gable. Keep each opening
    inside the triangle. (Straight gables only, not gambrel sections.)"""
    rise = wl.gable
    if rise <= 1e-6:
        return
    wl.gable = 0.0
    b = wl.b

    def deco():
        w, h = wl.w, wl.h
        uo, vo = wl.uvo
        xl = lambda z: (z - h) / rise * (w / 2)
        holes = [o for o in wl.ops if o["z1"] > h + 1e-6]
        zc = sorted({h, h + rise} | {min(max(o[k], h), h + rise) for o in holes for k in ("z0", "z1")})
        for za, zb in zip(zc, zc[1:]):
            if zb - za < 1e-6:
                continue
            zm = (za + zb) / 2
            cur, spans = None, []
            for c0, c1 in sorted((o["u0"], o["u1"]) for o in holes if o["z0"] < zm < o["z1"]):
                spans.append((cur, c0))
                cur = c1
            spans.append((cur, None))
            for sa, sb in spans:
                a0, a1 = (xl(za), xl(zb)) if sa is None else (sa, sa)
                b0, b1 = (w - xl(za), w - xl(zb)) if sb is None else (sb, sb)
                pts = [(a0, 0.0, za), (b0, 0.0, za), (b1, 0.0, zb), (a1, 0.0, zb)]
                b.face(pts, wl.mat, col=wl.col, lod=wl.lod, uv=[(uo + p[0], vo + p[2]) for p in pts])

    wl.add(deco)


def plinth(body, h=0.55, out=0.07, mat="masonry", col="warm", skirt=3.0, lod=0, walls="frbl"):
    """P.plinth on chosen sides only: walls = which of the front, right, back, left walls get the base course (for
    blocks that stand against other volumes or inside a loggia). Like P.plinth it leaves doorways clear and adds the
    hidden foundation under the whole block."""
    b = body.b
    with b.at(body.x, body.y, body.z):
        b.box(body.w + 2 * out, body.d + 2 * out, skirt, mat, col=shade(col, 0.85), y=0, z=-skirt, top=False, lod=0)
    for key, wl in zip("frbl", body.walls):
        if key not in walls:
            continue

        def strip(wl=wl):
            u, segs = -out, []
            for g0, g1 in sorted((o["u0"] - 0.02, o["u1"] + 0.02) for o in wl.ops if o["z0"] < h - 0.03):
                if g0 > u + 0.05:
                    segs.append((u, g0))
                u = max(u, g1)
            if wl.w + out > u + 0.05:
                segs.append((u, wl.w + out))
            for ua, ub in segs:
                b.box(ub - ua, out + 0.04, h, mat, col=col, x=(ua + ub) / 2, y=-out / 2 + 0.02, z=0, lod=lod, sides="frl")

        wl.add(strip)


def quoins(body, corners="frbl", z0=0.0, z1=None, size=(0.5, 0.28, 0.4), proud=0.03, mat="ashlar", col="stone", lod=2):
    """Dressed corner stones, long and short alternately, like P.quoins but 8 triangles a stone instead of 18.
    corners: 'f' = front-left, 'r' = front-right, 'b' = back-right, 'l' = back-left."""
    b = body.b
    z1 = body.h if z1 is None else z1
    L, S, H = size
    n = max(1, int((z1 - z0) / H))
    hh = (z1 - z0) / n
    cs = {"f": (-1, -1), "r": (1, -1), "b": (1, 1), "l": (-1, 1)}
    with b.detail(lod):
        for key in corners:
            sx, sy = cs[key]
            cx, cy = body.x + sx * body.w / 2, body.y + sy * body.d / 2
            for i in range(n):
                lx, ly = (L, S) if i % 2 == 0 else (S, L)
                lx *= b.r(0.9, 1.08)
                ly *= b.r(0.9, 1.08)
                b.box(lx, ly, hh * 0.93, mat, col=shade(col, b.r(0.9, 1.06)), x=cx - sx * (lx / 2 - proud), y=cy - sy * (ly / 2 - proud),
                      z=body.z + z0 + hh * (i + 0.035), top=False)


def buttress(b, w=0.7, d=1.0, h=5.0, steps=2, top_d=0.3, mat="masonry", col="warm", cap="ashlar", cap_col="stone", lod=0, slope=1.1):
    """A stepped buttress in the current frame: it stands against a wall lying in the x-z plane and projects toward
    -y, centred on x = 0, rising h from z = 0. `steps` stages shrinking from depth d to top_d, each with a sloping
    stone weathering; the top one dies into the wall. Put it with `with b.at(x, y_wall, 0, rz=...)`."""
    ds = [lerp(d, top_d, i / max(steps - 1, 1)) for i in range(steps)] + [0.0]
    sl = [(ds[i] - ds[i + 1]) * slope for i in range(steps)]
    wts = [steps - i + 1.0 for i in range(steps)]
    body_h = max(h - sum(sl), 0.2)
    z = 0.0
    hw = w / 2
    for i in range(steps):
        hi = body_h * wts[i] / sum(wts)
        b.box(w, ds[i], hi + (sl[i - 1] if i else 0.0), mat, col=col, x=0, y=-ds[i] / 2, z=z - (sl[i - 1] if i else 0.0), lod=lod, sides="frl", top=False)
        z += hi
        ya, yb, zt = -ds[i], -ds[i + 1], z + sl[i]
        b.quad((-hw, ya, z), (hw, ya, z), (hw, yb, zt), (-hw, yb, zt), cap, col=cap_col, lod=lod)
        b.tri((-hw, ya, z), (-hw, yb, zt), (-hw, yb, z), mat, col=col, lod=lod)
        b.tri((hw, ya, z), (hw, yb, z), (hw, yb, zt), mat, col=col, lod=lod)
        z = zt if i == steps - 1 else z + sl[i]
    return z


def corbel(b, w=0.3, out=0.4, h=0.45, mat="ashlar", col="stone", lod=1, nose=0.4):
    """One stone bracket in the current frame: against a wall in the x-z plane, projecting `out` toward -y, centred on
    x = 0, its top at z = 0 and its sloping underside reaching down h. nose = how much of h is the square front."""
    hw = w / 2
    pr = [(0.0, 0.0), (-out, 0.0), (-out, -h * nose), (0.0, -h)]
    L = [(-hw, y, z) for y, z in pr]
    R = [(hw, y, z) for y, z in pr]
    b.quad(L[2], R[2], R[1], L[1], mat, col=col, lod=lod)
    b.quad(L[3], R[3], R[2], L[2], mat, col=shade(col, 0.82), lod=lod)
    b.quad(L[3], L[2], L[1], L[0], mat, col=shade(col, 0.92), lod=lod)
    b.quad(R[0], R[1], R[2], R[3], mat, col=shade(col, 0.92), lod=lod)


def corbel_ring(b, r, z, n=16, out=0.4, h=0.45, w=0.3, x=0.0, y=0.0, a0=0.0, a1=360.0, **kw):
    """n corbels round a tower of radius r, their tops at height z (under a gallery or an oversailing parapet)."""
    with b.at(x, y, z):
        for k in range(n):
            with b.at(rz=a0 + (a1 - a0) * (k + 0.5) / n):
                with b.at(0, -r + 0.02, 0):
                    corbel(b, w, out, h, **kw)


def corbel_table(b, w, d, z, out=0.4, h=0.45, cw=0.3, spacing=0.75, x=0.0, y=0.0, sides="frbl", **kw):
    """Corbels along the sides of a w by d block centred on (x, y), their tops at height z."""
    for key, (ox, oy, rz, L) in zip("frbl", ((0, -d / 2, 0, w), (w / 2, 0, 90, d), (0, d / 2, 180, w), (-w / 2, 0, 270, d))):
        if key not in sides:
            continue
        n = max(2, round(L / spacing))
        with b.at(x + ox, y + oy, z, rz=rz):
            for i in range(n):
                with b.at(-L / 2 + L * (i + 0.5) / n, 0.02, 0):
                    corbel(b, cw, out, h, **kw)


def joists(s, z, out=0.4, n=None, u0=0.0, u1=None, w=0.13, h=0.17, col="darkoak", lod=1, inset=0.12):
    """The joist ends that carry a jettied (overhanging) storey: beams poking `out` from a flat wall, their tops at
    height z, from u0 to u1. Use on the wall below the overhang."""
    b = s.b
    u1 = s.w if u1 is None else u1
    n = n or max(2, round((u1 - u0) / 0.62))

    def deco():
        with b.detail(lod):
            for i in range(n + 1):
                u = lerp(u0 + inset, u1 - inset, i / n)
                b.beam((u, 0.05, z - h / 2), (u, -out, z - h / 2), w=w, h=h, mat="timber", col=col, caps=True)

    s.add(deco)


def parapet(b, pts, h=0.5, t=0.24, mat="masonry", col="warm", cope="ashlar", cope_col="stone", lod=0, closed=False):
    """A low wall with a coping along the points [(x, y, z), ...] (current frame), its outer face on the line; the
    thickness lies to the LEFT of the direction of travel. For terraces: put a P.railing on top or leave gaps."""
    Pp = list(pts) + ([pts[0]] if closed else [])
    for i in range(len(Pp) - 1):
        a, c = Pp[i], Pp[i + 1]
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        if L < 1e-4:
            continue
        ang = math.degrees(math.atan2(c[1] - a[1], c[0] - a[0]))
        with b.at(a[0], a[1], a[2], rz=ang):
            b.box(L, t, h, mat, col=col, x=L / 2, y=t / 2, lod=lod, top=False)
            b.box(L + 0.08, t + 0.1, 0.08, cope, col=cope_col, x=L / 2, y=t / 2, z=h, lod=lod, bottom=True)


# ---------------------------------------------------------------------------------------- openings
def round_window(s, pos, z, r=0.8, spokes=8, frame="ivory", trim="ashlar", trim_col="stone", trim_w=0.16, depth=None, glass=None, hub=True):
    """A round window centred at (pos, z) on a flat wall (or, with gable_holes, in its gable): a true round recess with
    a stone ring round it and wheel tracery of `spokes` spokes (0 for none)."""
    b = s.b
    u = s.U(pos)
    op = s.opening(u, z - r, 2 * r, 2 * r, arch=r, depth=depth, pane="glass", pane_col=glass)
    d = op["d"]

    def deco():
        uo, vo = s.uvo
        n = 8
        S_ = s._S
        inw = s._inward(u)
        In = lambda uu, zz: vadd(S_(uu, zz), vmul(inw, d))
        pts = [(u - r * math.cos(math.pi * i / n), z - r * math.sin(math.pi * i / n)) for i in range(n + 1)]
        rcol = shade(s.col, 0.9)
        for i in range(n):        # the lower half: fill the square corners of the kit's opening back in, line the curve
            (ua, za), (ub, zb) = pts[i], pts[i + 1]
            corner = (u - r, z - r) if i < n // 2 else (u + r, z - r)
            t = [corner, pts[i + 1], pts[i]]
            b.face([S_(*q) for q in t], s.mat, col=s.col, lod=s.lod, uv=[(uo + q[0], vo + q[1]) for q in t])
            b.quad(S_(ua, za), S_(ub, zb), In(ub, zb), In(ua, za), s.mat, col=rcol, lod=s.lod)
        with s.onu(u, z):
            with b.at(rx=90):                  # local z now points out of the wall, y up the wall
                with b.detail(1):
                    if trim:
                        b.revolve([(r + trim_w, 0.0), (r + trim_w, 0.05), (r, 0.05), (r, 0.0)], trim, col=trim_col, seg=16)
                    b.revolve([(r, -d * 0.6 + 0.05), (r - 0.07, -d * 0.6 + 0.05), (r - 0.07, -d * 0.6)], "planks", col=frame, seg=16)
                with b.detail(2):
                    for k in range(spokes):
                        a = 2 * math.pi * k / spokes
                        b.beam((0, 0, -d * 0.6), (r * math.sin(a), r * math.cos(a), -d * 0.6), w=0.05, h=0.05, mat="planks", col=frame, up=(0, 0, 1), caps=False)
                    if hub and spokes:
                        b.revolve([(r * 0.24, -d * 0.6), (r * 0.24, -d * 0.6 + 0.04), (0.0, -d * 0.6 + 0.04)], "planks", col=frame, seg=8)

    s.add(deco)
    return op


def mullioned(s, pos, z, w=2.0, h=2.0, lights=3, transoms=1, mat="ashlar", col="stone", hood=True, sill=True, arch=0.0, bars=1, depth=None,
              glass=None, frame=None):
    """A stone-mullioned window: one wide opening divided into `lights` by stone mullions, with `transoms` cross-bars,
    a projecting hood mould over the head and a sill. bars = leaded glazing bars per light (near level only)."""
    b = s.b
    u = s.U(pos)
    op = s.opening(u, z, w, h, arch=arch, depth=depth, pane="glass", pane_col=glass)
    d = op["d"]

    def deco():
        with s.onu(u, z):
            hs = h - arch
            my = d * 0.45
            with b.detail(1):
                for i in range(1, lights):
                    x = -w / 2 + w * i / lights
                    top = hs + (arch * math.sin(math.acos(min(abs(x) / (w / 2), 1.0))) if arch > 0 else 0.0)
                    b.beam((x, my, 0), (x, my, top), w=0.11, h=d * 0.8, mat=mat, col=col, up=(0, 1, 0), caps=False)
                for j in range(1, transoms + 1):
                    zz = hs * j / (transoms + 1)
                    b.beam((-w / 2, my, zz), (w / 2, my, zz), w=d * 0.8, h=0.1, mat=mat, col=col, up=(0, 0, 1), caps=False)
                if sill:
                    b.box(w + 0.24, 0.2, 0.09, mat, col=col, x=0, y=-0.03, z=-0.09, bottom=True)
                if hood and arch < 1e-4:
                    b.box(w + 0.4, 0.13, 0.09, mat, col=col, x=0, y=-0.045, z=h + 0.08, bottom=True)
                    for sgn in (-1, 1):
                        b.box(0.1, 0.11, 0.3, mat, col=col, x=sgn * (w / 2 + 0.15), y=-0.04, z=h - 0.2, bottom=True)
            with b.detail(2):
                fc = frame if frame is not None else "#3a3a3e"
                lw = w / lights
                for i in range(lights):
                    x0 = -w / 2 + lw * i
                    for k in range(bars):
                        x = x0 + lw * (k + 1) / (bars + 1)
                        b.beam((x, d - 0.03, 0.02), (x, d - 0.03, hs), w=0.025, h=0.02, mat="metal", col=fc, up=(0, 1, 0), caps=False)
                nz = max(2, int(hs / 0.5))
                for j in range(1, nz):
                    zz = hs * j / nz
                    b.beam((-w / 2, d - 0.03, zz), (w / 2, d - 0.03, zz), w=0.02, h=0.025, mat="metal", col=fc, up=(0, 0, 1), caps=False)

    s.add(deco)
    return op


def surround(s, pos, z, w, h, arch=0.0, t=0.16, proud=0.045, mat="ashlar", col="stone", keystone=True, sill=False, lod=1):
    """A dressed-stone architrave round an opening w wide and h high whose bottom is at z (the same numbers you gave
    P.window or P.door; give those lintel=None / frame=None): bands up the jambs and over the head, following an
    arched head, with a keystone; sill=True adds a moulded sill on two little brackets."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            hs = h - arch
            y = -proud / 2 + 0.01
            with b.detail(lod):
                for sgn in (-1, 1):
                    b.box(t, proud + 0.02, hs, mat, col=col, x=sgn * (w / 2 + t / 2), y=y, z=0, top=False)
                if arch > 1e-4:
                    n = 6
                    rr = w / 2 + t / 2
                    pts = [(-rr * math.cos(math.pi * i / n), y, hs + (arch + t / 2) * math.sin(math.pi * i / n)) for i in range(n + 1)]
                    for i in range(n):
                        b.beam(pts[i], pts[i + 1], w=t, h=proud + 0.02, mat=mat, col=col, up=(0, 1, 0), caps=False)
                else:
                    b.box(w + 2 * t, proud + 0.02, t, mat, col=col, x=0, y=y, z=h, bottom=True)
                if keystone:
                    b.box(0.2, proud + 0.06, t + 0.14, mat, col=shade(col, 1.04), x=0, y=y - 0.02, z=h - 0.04, tx=1.3, bottom=True)
                if sill:
                    b.box(w + 2 * t + 0.1, 0.22, 0.1, mat, col=col, x=0, y=-0.06, z=-0.1, bottom=True)
                    for sgn in (-1, 1):
                        b.box(0.12, 0.14, 0.18, mat, col=col, x=sgn * (w / 2 + t / 2), y=-0.04, z=-0.28, bottom=True)

    s.add(deco)


def louvres(s, pos, z, w, h, col="darkoak", n=None, inset=0.35):
    """Sloping louvre boards across an opening w by h whose bottom is at z (belfries, lanterns, lofts). Cut the
    opening first with pane="paint", pane_col=DARK (or pane=None)."""
    b = s.b
    u = s.U(pos)
    n = n or max(3, int(h / 0.24))

    def deco():
        with s.onu(u, z):
            with b.detail(1):
                for i in range(n):
                    zz = h * (i + 0.5) / n
                    b.beam((-w / 2, s.depth * inset, zz), (w / 2, s.depth * inset, zz), w=0.19, h=0.03, mat="planks", col=col, up=(0, -0.5, 0.87), caps=False)

    s.add(deco)


def display(b, w, kind="loaves", n=None, cols=None, depth=0.14):
    """A row of small goods standing on z = 0 along x (centred), about `depth` deep: for shop-window sills, counters,
    shelves and stalls. kind = 'loaves', 'bottles', 'books', 'fruit', 'pots', 'parcels' or 'cloth'."""
    rng = b.rng
    with b.detail(2):
        if kind == "loaves":
            n = n or max(2, int(w / 0.3))
            for i in range(n):
                x = -w / 2 + w * (i + 0.5) / n
                b.blob(0.12, depth * 0.45, 0.06, mat="cloth", col=rng.choice(cols or BREAD), x=x, z=0.055, seg=5, rings=2, rough=0.1)
        elif kind == "fruit":
            n = n or max(3, int(w / 0.15))
            for i in range(n):
                x = -w / 2 + w * (i + 0.5) / n
                b.blob(0.06, 0.06, 0.055, mat="paint", col=rng.choice(cols or FRUIT), x=x, y=rng.uniform(-0.02, 0.02), z=0.05, seg=5, rings=2, rough=0.1)
        elif kind == "bottles":
            n = n or max(3, int(w / 0.17))
            for i in range(n):
                x = -w / 2 + w * (i + 0.5) / n
                k = rng.uniform(0.8, 1.3)
                with b.at(x, 0, 0):
                    b.revolve([(0.045, 0.0), (0.045, 0.11 * k), (0.017, 0.15 * k), (0.017, 0.2 * k)], "paint", col=rng.choice(cols or BOTTLES), seg=5, close_top=True)
        elif kind == "books":
            n = n or max(3, int(w / 0.09))
            x = -w / 2
            for i in range(n):
                t = rng.uniform(0.04, 0.08)
                hh = rng.uniform(0.17, 0.26)
                b.box(t, depth * 0.8, hh, "paint", col=rng.choice(cols or BOOKS), x=x + t / 2, z=0)
                x += t + 0.004
                if x > w / 2 - 0.08:
                    break
        elif kind == "pots":
            n = n or max(2, int(w / 0.26))
            for i in range(n):
                x = -w / 2 + w * (i + 0.5) / n
                k = rng.uniform(0.8, 1.2)
                with b.at(x, 0, 0):
                    b.revolve([(0.05, 0.0), (0.085 * k, 0.07), (0.07 * k, 0.15 * k), (0.05, 0.17 * k)], "paint", col=rng.choice(cols or ["#c9764a", "#b56a48", "#d9b08a", "#7d94a8"]), seg=6, close_top=True)
        elif kind == "parcels":
            n = n or max(2, int(w / 0.3))
            for i in range(n):
                x = -w / 2 + w * (i + 0.5) / n
                sz = rng.uniform(0.14, 0.24)
                with b.at(x, 0, 0, rz=rng.uniform(-20, 20)):
                    b.box(sz * 1.2, min(sz, depth), sz * 0.8, "paint", col=rng.choice(cols or ["#c9a57a", "#d8c3a0", "#b89468", "#e3d2b0"]))
                    b.beam((-sz * 0.6, 0, sz * 0.8 + 0.004), (sz * 0.6, 0, sz * 0.8 + 0.004), w=0.02, h=0.006, mat="paint", col="#b5433a", caps=False)
        elif kind == "cloth":
            n = n or max(2, int(w / 0.22))
            for i in range(n):
                x = -w / 2 + w * (i + 0.5) / n
                b.tube((x, -depth * 0.4, 0.07), (x, depth * 0.4, 0.07), r=0.07, mat="cloth", col=rng.choice(cols or ["#b5433a", "#3f6fb5", "#d9a431", "#7a4672", "#f3ecd9", "#5a9a68"]), n=6, caps=True, lod=2)


def shopfront(s, pos, z=0.0, w=2.6, h=1.9, riser=0.6, col="green", lights=3, transom=0.42, fascia=0.32, pilasters=True, depth=0.2,
              goods=None, riser_mat="planks", riser_col=None, glass=None, panes=1):
    """A timber shop window on a flat wall: a panelled stall-riser `riser` high standing at z, the glass above it
    (w wide, h high) divided by mullions into `lights` with a row of small top-lights above a transom (transom = their
    height, 0 for none), flat pilasters at the sides and a fascia board with a cornice over it (fascia = its height,
    0 for none; no lettering). Everything painted `col`. goods = what is on show on the sill inside (a `display`
    kind such as 'loaves', 'bottles', 'books', 'fruit', 'pots', 'cloth', or a function(b, w) drawing in a frame
    on the sill). The whole thing is w + 0.6 wide and riser + h + fascia + 0.1 high. Keep riser >= the plinth."""
    b = s.b
    u = s.U(pos)
    op = s.opening(u, z + riser, w, h, depth=depth, pane="glass", pane_col=glass)
    d = op["d"]

    def deco():
        with s.onu(u, z):
            rc = col if riser_col is None else riser_col
            fy = d * 0.32
            top = riser + h
            with b.detail(1):
                b.box(w + 0.12, 0.1, riser, riser_mat, col=rc, x=0, y=-0.045, z=0, top=False)
                b.box(w + 0.32, 0.22, 0.07, "planks", col=shade(col, 1.15), x=0, y=-0.06, z=riser - 0.045, bottom=True)
                for i in range(lights + 1):
                    x = min(max(-w / 2 + w * i / lights, -w / 2 + 0.04), w / 2 - 0.04)
                    b.beam((x, fy, riser), (x, fy, top), w=0.08, h=0.1, mat="planks", col=col, up=(0, 1, 0), caps=False)
                if transom:
                    b.beam((-w / 2, fy, top - transom), (w / 2, fy, top - transom), w=0.1, h=0.07, mat="planks", col=col, up=(0, 0, 1), caps=False)
                b.beam((-w / 2, fy, top - 0.04), (w / 2, fy, top - 0.04), w=0.1, h=0.08, mat="planks", col=col, up=(0, 0, 1), caps=False)
                if pilasters:
                    for sgn in (-1, 1):
                        b.box(0.18, 0.09, top + 0.03, "planks", col=shade(col, 0.84), x=sgn * (w / 2 + 0.12), y=-0.045, z=0, top=False)
                if fascia:
                    b.box(w + 0.52, 0.11, fascia, "planks", col=shade(col, 0.72), x=0, y=-0.055, z=top + 0.03, bottom=True)
                    b.box(w + 0.66, 0.22, 0.06, "planks", col=shade(col, 1.15), x=0, y=-0.09, z=top + 0.03 + fascia, bottom=True)
            with b.detail(2):
                lw = w / lights
                for i in range(lights):       # sunk panels on the riser, glazing bars in the top-lights
                    x = -w / 2 + lw * (i + 0.5)
                    b.box(lw - 0.2, 0.02, riser - 0.24, riser_mat, col=shade(rc, 0.86), x=x, y=-0.105, z=0.11, top=False)
                    if transom:
                        for k in range(panes):
                            xx = -w / 2 + lw * i + lw * (k + 1) / (panes + 1)
                            b.beam((xx, fy + 0.01, top - transom), (xx, fy + 0.01, top), w=0.035, h=0.04, mat="planks", col=col, up=(0, 1, 0), caps=False)
                if pilasters:
                    for sgn in (-1, 1):
                        b.box(0.24, 0.12, 0.09, "planks", col=shade(col, 1.0), x=sgn * (w / 2 + 0.12), y=-0.05, z=top - 0.1, bottom=True)
                if goods:
                    with b.at(0, d - 0.055, riser):
                        if callable(goods):
                            goods(b, w - 0.2)
                        else:
                            display(b, w - 0.24, goods, depth=0.1)

    s.add(deco)
    return op


def bay(s, pos, z, w=2.2, h=1.6, out=0.6, cant=0.3, apron=0.45, head=0.14, col="ivory", apron_mat="planks", apron_col=None, panes=(3, 2),
        side_panes=(1, 2), base="brackets", drop=0.7, base_mat="planks", base_col=None, roof="slate", roof_col=None, roof_h=0.45, tuck=0.0,
        glass=None, lod=0):
    """A bay window standing out from a wall (an oriel when it hangs on brackets): its floor at height z, w wide at the
    wall, projecting `out`; cant = how far the front corners are cut back (0 = a square bay). From the floor up: a
    solid apron, glass h high, a head rail. panes = (upright, level) glazing bars on the front, side_panes on the
    cheeks; col = the paint of its woodwork (apron_col for the panels).
    base = 'brackets' (two timber brackets `drop` long), 'corbel' (a moulded tapering underside `drop` deep, of
    base_mat / base_col), or None (it stands on the ground or on something: then give apron the height you need).
    roof = 'slate', 'tiles', 'shingle', 'lead' or 'copper' for a little hipped roof roof_h high, or None for a flat
    top (under a jetty or eaves). tuck = how far the cheeks reach back past the wall plane (use ~0.2 on a round
    tower). It needs no opening behind it. Total height apron + h + head (+ roof_h)."""
    b = s.b
    u = s.U(pos)
    acol = shade(col, 0.94) if apron_col is None else apron_col

    def deco():
        with s.onu(u, z):
            pts = [(-w / 2, tuck), (-w / 2 + cant, -out), (w / 2 - cant, -out), (w / 2, tuck)]
            H = apron + h + head
            g0, g1 = apron, apron + h
            for i in range(3):
                p, q = pts[i], pts[i + 1]
                L = math.hypot(q[0] - p[0], q[1] - p[1])
                nx, ny = (q[1] - p[1]) / L, -(q[0] - p[0]) / L        # outward normal of this face
                V = lambda t, zz, o=0.0: (p[0] + (q[0] - p[0]) * t + nx * o, p[1] + (q[1] - p[1]) * t + ny * o, zz)
                if apron > 1e-3:
                    b.quad(V(0, 0), V(1, 0), V(1, g0), V(0, g0), apron_mat, col=acol, lod=lod)
                b.quad(V(0, g0), V(1, g0), V(1, g1), V(0, g1), "glass", col=glass, lod=lod, uv=[(0, 0), (L, 0), (L, h), (0, h)])
                b.quad(V(0, g1), V(1, g1), V(1, H), V(0, H), apron_mat, col=acol, lod=lod)
                with b.detail(1):
                    b.beam(V(0, g0, 0.02), V(1, g0, 0.02), w=0.07, h=0.08, mat="planks", col=col, up=(0, 0, 1), caps=False)
                    b.beam(V(0, g1, 0.02), V(1, g1, 0.02), w=0.07, h=0.08, mat="planks", col=col, up=(0, 0, 1), caps=False)
                with b.detail(2):
                    nv, nh = panes if i == 1 else side_panes
                    for k in range(nv):
                        t = (k + 1) / (nv + 1)
                        b.beam(V(t, g0, 0.012), V(t, g1, 0.012), w=0.035, h=0.03, mat="planks", col=col, up=(nx, ny, 0), caps=False)
                    for k in range(nh):
                        zz = g0 + h * (k + 1) / (nh + 1)
                        b.beam(V(0, zz, 0.012), V(1, zz, 0.012), w=0.03, h=0.035, mat="planks", col=col, up=(0, 0, 1), caps=False)
            with b.detail(1):
                for (px, py) in pts[1:3] if tuck <= 0 else pts:
                    b.beam((px, py, 0), (px, py, H), w=0.09, mat="planks", col=col, caps=False)
            b.face([(p[0], p[1], 0) for p in reversed(pts)], base_mat if base else apron_mat, col=shade(acol if base_col is None else base_col, 0.8), lod=lod)
            if base == "brackets":
                with b.detail(1):
                    for sgn in (-1, 1):
                        x = sgn * (w / 2 - cant - 0.06) if cant > 0.05 else sgn * (w / 2 - 0.1)
                        b.beam((x, 0.0, -drop), (x, -out + 0.08, -0.05), w=0.1, mat="timber", col="darkoak")
                        b.beam((x, 0.0, -0.06), (x, -out + 0.02, -0.06), w=0.1, h=0.1, mat="timber", col="darkoak")
            elif base == "corbel":
                bc = acol if base_col is None else base_col
                tiers = [(1.0, 0.0), (0.72, -drop * 0.42), (0.3, -drop)]
                for (k0, z0), (k1, z1) in zip(tiers, tiers[1:]):
                    up_ = [(p[0] * k0, tuck if p[1] > 0 else p[1] * k0, z0) for p in pts]
                    lo_ = [(p[0] * k1, tuck if p[1] > 0 else p[1] * k1, z1) for p in pts]
                    for i in range(3):
                        b.quad(lo_[i], lo_[i + 1], up_[i + 1], up_[i], base_mat, col=shade(bc, 0.9 if z0 == 0.0 else 0.78), lod=lod)
                b.face([(p[0] * 0.3, tuck if p[1] > 0 else p[1] * 0.3, -drop) for p in reversed(pts)], base_mat, col=shade(bc, 0.7), lod=lod)
            if roof:
                rmat, rc = {"lead": ("metal", "lead"), "copper": ("metal", "copper")}.get(roof, (roof, None))
                rc = rc if roof_col is None else roof_col
                e = 0.07
                ex = [(-w / 2 - e, tuck), (-w / 2 + cant - e * 0.6, -out - e), (w / 2 - cant + e * 0.6, -out - e), (w / 2 + e, tuck)]
                ins = min(max(cant, out * 0.45) + 0.05, w / 2 - 0.04)
                Rl, Rr = (-w / 2 + ins, 0.0, H + roof_h), (w / 2 - ins, 0.0, H + roof_h)
                E = [(q[0], q[1], H) for q in ex]
                b.face([E[0], E[1], Rl], rmat, col=shade(rc, 0.92), lod=lod)
                b.face([E[1], E[2], Rr, Rl], rmat, col=rc, lod=lod)
                b.face([E[2], E[3], Rr], rmat, col=shade(rc, 0.92), lod=lod)
                for i in range(3):
                    a_, c_ = ex[i], ex[i + 1]
                    b.quad((a_[0], a_[1], H - 0.06), (c_[0], c_[1], H - 0.06), (c_[0], c_[1], H), (a_[0], a_[1], H), "planks", col="darkoak", lod=lod)
                    b.quad((pts[i][0], pts[i][1], H - 0.06), (pts[i + 1][0], pts[i + 1][1], H - 0.06), (c_[0], c_[1], H - 0.06), (a_[0], a_[1], H - 0.06), "planks", col="darkoak", lod=lod)
            else:
                b.face([(p[0], p[1], H) for p in pts], apron_mat, col=acol, lod=lod)

    s.add(deco)


def half_door(s, pos, w=1.0, h=2.0, z=0.0, col="green", frame="timber", open_deg=150.0, depth=None, shelf=True):
    """A stable door on a flat wall: the lower leaf shut (with a little ledge on top), the upper leaf swung open
    against the wall, the dark of the shop inside."""
    b = s.b
    u = s.U(pos)
    op = s.opening(u, z, w, h, depth=depth, pane="paint", pane_col=DARK)
    d = op["d"]

    def deco():
        with s.onu(u, z):
            hl = h * 0.52
            with b.detail(1):
                b.box(w - 0.03, 0.05, hl, "planks", col=col, x=0, y=d * 0.45, z=0.0, bottom=False)
                if shelf:
                    b.box(w - 0.02, 0.16, 0.04, "planks", col=shade(col, 1.15), x=0, y=d * 0.45 - 0.03, z=hl, bottom=True)
                with b.at(-w / 2, 0.0, hl + 0.03, rz=-open_deg):       # the upper leaf, hinged on the left jamb
                    b.box(w - 0.03, 0.05, h - hl - 0.05, "planks", col=col, x=(w - 0.03) / 2, y=-0.035, z=0, bottom=True)
                if frame == "timber":
                    for sgn in (-1, 1):
                        b.beam((sgn * (w / 2 + 0.07), -0.02, 0), (sgn * (w / 2 + 0.07), -0.02, h + 0.14), w=0.14, h=0.1, mat="timber", col="darkoak", up=(0, 1, 0))
                    b.beam((-w / 2 - 0.2, -0.02, h + 0.08), (w / 2 + 0.2, -0.02, h + 0.08), w=0.1, h=0.16, mat="timber", col="darkoak", up=(0, 0, 1))
                elif frame == "stone":
                    b.box(w + 0.5, 0.16, 0.24, "ashlar", col="stone", x=0, y=-0.02, z=h)
            with b.detail(2):
                for zz in (hl * 0.25, hl * 0.8):
                    b.beam((-w / 2 + 0.03, d * 0.45 - 0.03, zz), (w / 2 - 0.15, d * 0.45 - 0.03, zz), w=0.02, h=0.06, mat="metal", col="iron", up=(0, 0, 1), caps=False)

    s.add(deco)
    return op


def counter(s, pos, z, w=1.5, h=1.1, col="green", shelf=0.38, flap=True, goods=None, depth=None, frame=True):
    """A serving hatch on a flat wall: an open window (dark inside) whose sill at height z is a projecting shelf on
    brackets, with a drop-shutter propped open above it like a little awning. goods = a `display` kind laid out on
    the shelf ('loaves', 'parcels', 'fruit' ...) or a function(b, w)."""
    b = s.b
    u = s.U(pos)
    op = s.opening(u, z, w, h, depth=depth, pane="paint", pane_col=DARK)
    d = op["d"]

    def deco():
        with s.onu(u, z):
            with b.detail(1):
                b.box(w + 0.24, shelf + d * 0.6, 0.06, "planks", col="greyoak", x=0, y=(d * 0.6 - shelf) / 2, z=-0.06, bottom=True)
                for sgn in (-1, 1):
                    b.beam((sgn * (w / 2 - 0.08), 0.0, -0.5), (sgn * (w / 2 - 0.08), -shelf + 0.06, -0.08), w=0.07, mat="timber", col="darkoak")
                if frame:
                    for sgn in (-1, 1):
                        b.beam((sgn * (w / 2 + 0.05), -0.02, 0), (sgn * (w / 2 + 0.05), -0.02, h + 0.1), w=0.1, h=0.08, mat="planks", col=col, up=(0, 1, 0))
                    b.beam((-w / 2 - 0.1, -0.02, h + 0.05), (w / 2 + 0.1, -0.02, h + 0.05), w=0.08, h=0.1, mat="planks", col=col, up=(0, 0, 1))
                if flap:
                    with b.at(0, -0.04, h + 0.02, rx=-58):          # hinged at the head, swung up and out
                        b.box(w, 0.04, h * 0.92, "planks", col=col, x=0, y=0, z=-h * 0.92, bottom=True)
            with b.detail(2):
                if flap:
                    fz, fy = h + 0.02 - h * 0.92 * math.cos(rad(58)), -0.04 - h * 0.92 * math.sin(rad(58))
                    for sgn in (-1, 1):
                        b.beam((sgn * (w / 2 - 0.05), -0.02, h * 0.45), (sgn * (w / 2 - 0.05), fy + 0.05, fz + 0.04), w=0.025, mat="metal", col="iron", caps=False)
                if goods:
                    with b.at(0, -shelf * 0.45, 0):
                        if callable(goods):
                            goods(b, w)
                        else:
                            display(b, w - 0.1, goods, depth=min(shelf * 0.7, 0.2))

    s.add(deco)
    return op


# ---------------------------------------------------------------------------------------- roofscape
def stack(b, x, y, z, h, w=0.9, d=0.7, base=None, mat="masonry", col="warm", pots=2, pot_col="#c9764a", smoke=True, taper=0.9, band=True, lod=0):
    """A big chimney rising h from (x, y, z): an optional breast base = (width, depth, height) that shoulders in to
    the w by d stack, a string band, two oversailing cap courses and a row of pots; smoke from the top. Start it below
    the roof surface (or on the ground against a wall, for an outside chimney)."""
    with b.at(x, y, z):
        zz = 0.0
        if base:
            bw, bdp, bh = base
            sh = min(max(bw - w, bdp - d) * 0.7 + 0.15, h * 0.25)
            b.box(bw, bdp, bh, mat, col=col, lod=lod, top=False)
            b.box(bw, bdp, sh, mat, col=shade(col, 1.05), z=bh, tx=w / bw, ty=d / bdp, lod=lod, top=False)
            zz = bh + sh
        hs = h - zz - 0.24
        b.box(w, d, hs, mat, col=col, z=zz, lod=lod, taper=taper, top=False)
        tw, td = w * taper, d * taper
        with b.detail(1):
            if band:
                b.box(tw + 0.1, td + 0.1, 0.1, "ashlar", col="stone", z=zz + hs * 0.72, bottom=True)
            b.box(tw + 0.14, td + 0.14, 0.12, "ashlar", col="stone", z=h - 0.24, bottom=True)
            b.box(tw + 0.28, td + 0.28, 0.12, "ashlar", col="stone", z=h - 0.12, bottom=True)
            for i in range(pots):
                px = (i - (pots - 1) / 2) * min(0.32, (tw - 0.1) / max(pots, 1))
                with b.at(px, 0, h):
                    b.revolve([(0.12, 0.0), (0.095, 0.34), (0.11, 0.38), (0.085, 0.4)], "paint", col=shade(pot_col, b.r(0.9, 1.08)), seg=8)
        if smoke:
            b.smoke(0, 0, h + 0.5)


VANES = {
    "cock": [(-.44, -.04), (-.42, .12), (-.3, .34), (-.2, .14), (0, .1), (.13, .2), (.17, .36), (.24, .3), (.28, .34), (.4, .24), (.29, .2),
             (.26, .02), (.12, -.14), (.02, -.17), (-.12, -.1), (-.28, .0)],
    "lark": [(-.46, .1), (-.2, .1), (-.06, .3), (.02, .12), (.2, .14), (.3, .2), (.44, .14), (.3, .08), (.2, -.04), (.02, -.1), (-.14, -.06),
             (-.44, .0)],
    "fish": [(-.44, .16), (-.3, .02), (-.1, .13), (.16, .14), (.36, .04), (.44, 0), (.36, -.05), (.16, -.14), (-.1, -.13), (-.3, -.02), (-.44, -.16), (-.38, 0)],
    "arrow": [(-.46, .12), (-.3, .02), (.22, .02), (.22, .12), (.46, 0), (.22, -.12), (.22, -.02), (-.3, -.02), (-.46, -.12), (-.38, 0)],
    "pennon": [(-.1, .14), (.46, .1), (.3, 0), (.46, -.1), (-.1, -.14)],
}


def weathercock(b, x=0.0, y=0.0, z=0.0, h=1.6, shape="cock", col="brass", size=1.0, turn=None, arms=True):
    """A weathervane with a cut-out figure ('cock', 'lark', 'fish', 'arrow', 'pennon', or your own clockwise outline
    [(x, z), ...] within about +-0.45) on a pole rising h from (x, y, z). size scales the figure."""
    poly = VANES.get(shape, shape) if isinstance(shape, str) else shape
    with b.at(x, y, z):
        with b.detail(1):
            b.tube((0, 0, 0), (0, 0, h), r=0.028, mat="metal", col="iron", n=5)
            b.revolve([(0.0, h * 0.5 - 0.07), (0.075, h * 0.5), (0.0, h * 0.5 + 0.07)], "metal", col=col, seg=6)
        with b.detail(2):
            if arms:
                b.beam((-0.34, 0, h * 0.66), (0.34, 0, h * 0.66), w=0.02, mat="metal", col="iron", caps=False)
                b.beam((0, -0.34, h * 0.66), (0, 0.34, h * 0.66), w=0.02, mat="metal", col="iron", caps=False)
        with b.detail(1):
            with b.at(z=h + 0.02, rz=b.r(0, 360) if turn is None else turn, s=size):
                cz = sum(p[1] for p in poly) / len(poly)
                c = (0.0, 0.0, cz - min(p[1] for p in poly) + 0.02)
                ring = [(p[0], 0.0, p[1] - min(q[1] for q in poly) + 0.02) for p in poly]
                for i in range(len(ring)):
                    j = (i + 1) % len(ring)
                    b.tri(c, ring[i], ring[j], "metal", col=col)
                    b.tri(c, ring[j], ring[i], "metal", col=shade(col, 0.85))


# ---------------------------------------------------------------------------------------- street furniture
EMBLEMS = {      # clockwise outlines (x to the right, z up) within about +-0.24, star-shaped about the origin
    "teapot": [(-.24, .09), (-.2, .12), (-.13, .03), (-.08, .09), (-.03, .12), (-.03, .17), (.03, .17), (.03, .12), (.08, .09), (.13, .04), (.22, .05),
               (.24, -.03), (.2, -.11), (.12, -.11), (.08, -.16), (-.07, -.16), (-.11, -.12), (-.14, -.06)],
    "scissors": [(0, .03), (.2, .22), (.23, .2), (.05, -.02), (.2, -.12), (.22, -.2), (.14, -.24), (.08, -.16), (0, -.06), (-.08, -.16), (-.14, -.24),
                 (-.22, -.2), (-.2, -.12), (-.05, -.02), (-.23, .2), (-.2, .22)],
    "mortar": [(-.2, .04), (.02, .04), (.16, .24), (.21, .2), (.1, .04), (.2, .04), (.13, -.13), (.15, -.2), (-.15, -.2), (-.13, -.13)],
    "apple": [(0, .12), (.03, .22), (.07, .21), (.05, .13), (.14, .15), (.21, .06), (.2, -.08), (.12, -.2), (0, -.17), (-.12, -.2), (-.2, -.08),
              (-.21, .06), (-.14, .15)],
    "candle": [(-.05, .08), (-.02, .08), (-.045, .15), (0, .24), (.045, .15), (.02, .08), (.05, .08), (.05, -.16), (.14, -.16), (.14, -.21),
               (-.14, -.21), (-.14, -.16), (-.05, -.16)],
    "letter": [(-.23, .15), (0, -.02), (.23, .15), (.23, -.15), (-.23, -.15)],
    "hammer": [(-.04, -.22), (-.04, .08), (-.18, .08), (-.22, .14), (-.18, .2), (.18, .2), (.18, .08), (.04, .08), (.04, -.22)],
    "crown": [(-.2, -.12), (-.22, .14), (-.1, .02), (0, .2), (.1, .02), (.22, .14), (.2, -.12)],
    "bird": [(-.24, .02), (-.1, .08), (0, .16), (.1, .14), (.16, .18), (.24, .12), (.18, .08), (.14, -.02), (.02, -.1), (-.08, -.08), (-.2, -.14),
             (-.14, -.04)],
    "sun": [(0.24 * math.sin(math.pi * i / 8) * (1.0 if i % 2 == 0 else 0.55), 0.24 * math.cos(math.pi * i / 8) * (1.0 if i % 2 == 0 else 0.55)) for i in range(16)],
    "wheel": [(0.22 * math.sin(math.pi * i / 6), 0.22 * math.cos(math.pi * i / 6)) for i in range(12)],
    "pretzel": [(0, .08), (.1, .2), (.22, .12), (.2, -.06), (.08, -.2), (0, -.1), (-.08, -.2), (-.2, -.06), (-.22, .12), (-.1, .2)],
    "bottle": [(-.04, .24), (.04, .24), (.04, .1), (.11, .0), (.11, -.22), (-.11, -.22), (-.11, .0), (-.04, .1)],
    "boot": [(-.1, .2), (.04, .2), (.04, -.04), (.2, -.1), (.2, -.2), (-.1, -.2)],
    "book": [(-.2, .14), (0, .1), (.2, .14), (.2, -.14), (0, -.18), (-.2, -.14)],
    "loaf": [(-.2, -.1), (-.22, .02), (-.12, .12), (.12, .12), (.22, .02), (.2, -.1)],
    "key": [(-.22, .03), (.06, .03), (.1, .11), (.2, .11), (.24, 0), (.2, -.11), (.1, -.11), (.06, -.03), (-.1, -.03), (-.1, -.1), (-.15, -.1), (-.15, -.03), (-.22, -.03)],
    "fish": [(-.22, 0), (-.08, .1), (.1, .08), (.16, 0), (.24, .1), (.24, -.1), (.16, 0), (.1, -.08), (-.08, -.1)],
    "mug": [(-.14, .16), (.1, .16), (.1, .08), (.2, .08), (.2, -.08), (.1, -.08), (.1, -.18), (-.14, -.18)],
    "star": [(0, .22), (.06, .07), (.21, .07), (.09, -.03), (.13, -.18), (0, -.09), (-.13, -.18), (-.09, -.03), (-.21, .07), (-.06, .07)],
    "flower": [(0, .22), (.08, .08), (.22, .06), (.12, -.05), (.14, -.2), (0, -.12), (-.14, -.2), (-.12, -.05), (-.22, .06), (-.08, .08)],
    "hat": [(0, .24), (.1, -.06), (.24, -.12), (.24, -.18), (-.24, -.18), (-.24, -.12), (-.1, -.06)],
    "needle": [(-.22, -.2), (.16, .2), (.22, .22), (.2, .16), (-.18, -.22)],
    "anchor": [(-.03, .22), (.03, .22), (.03, -.08), (.16, -.02), (.2, -.1), (0, -.22), (-.2, -.1), (-.16, -.02), (-.03, -.08)],
    "moon": [(.02, .22), (-.06, .1), (-.08, 0), (-.06, -.1), (.02, -.22), (-.14, -.14), (-.2, 0), (-.14, .14)],
    "bell": [(-.04, .2), (.04, .2), (.12, .06), (.14, -.1), (.2, -.16), (-.2, -.16), (-.14, -.1), (-.12, .06)],
}


def sign(s, pos, z, emblem="teapot", col="mustard", board="ivory", shape="rect", out=0.85, w=0.64, h=0.54, scroll=True, rim=None):
    """A hanging shop sign on a wrought-iron bracket with a scroll, standing out from the wall at (pos, z) so that it
    reads along the street. shape of the board: 'rect', 'round', 'shield' or 'arch'; emblem = a name from EMBLEMS or
    your own clockwise outline [(x, z), ...]; col = the emblem's paint, rim = a painted border colour. No lettering.
    Works on flat and round walls."""
    b = s.b
    u = s.U(pos)
    poly = EMBLEMS.get(emblem, EMBLEMS["star"]) if isinstance(emblem, str) else emblem
    if shape == "round":
        bd_ = [(w / 2 * math.sin(2 * math.pi * i / 12), w / 2 * math.cos(2 * math.pi * i / 12)) for i in range(12)]
        hh = w
    elif shape == "shield":
        bd_ = [(-w / 2, h / 2), (w / 2, h / 2), (w / 2, -h * 0.1), (0, -h / 2 - 0.06), (-w / 2, -h * 0.1)]
        hh = h + 0.06
    elif shape == "arch":
        bd_ = [(-w / 2, -h / 2), (-w / 2, h * 0.2), (-w * 0.3, h * 0.45), (0, h / 2 + 0.04), (w * 0.3, h * 0.45), (w / 2, h * 0.2), (w / 2, -h / 2)]
        hh = h + 0.04
    else:
        bd_ = [(-w / 2, h / 2), (w / 2, h / 2), (w / 2, -h / 2), (-w / 2, -h / 2)]
        hh = h
    k = min(w, hh) / 0.6

    def deco():
        with s.onu(u, z):
            cy, cz = -out * 0.58, -hh / 2 - 0.1
            with b.detail(1):
                b.beam((0, 0.0, 0.06), (0, -out - 0.06, 0.06), w=0.035, mat="metal", col="iron", caps=False)
                b.beam((0, 0.0, -0.38), (0, -out * 0.5, 0.04), w=0.028, mat="metal", col="iron", caps=False)
                for sx in (-1, 1):                # the board: two faces and (near) an edge
                    ring = [(sx * 0.022, cy - sx * px, cz + pz) for px, pz in bd_]
                    for i in range(1, len(ring) - 1):
                        b.tri(ring[0], ring[i], ring[i + 1], "paint", col=board)
            with b.detail(2):
                for i in range(len(bd_)):
                    (pa, za), (pb, zb) = bd_[i], bd_[(i + 1) % len(bd_)]
                    b.quad((0.022, cy - pa, cz + za), (-0.022, cy - pa, cz + za), (-0.022, cy - pb, cz + zb), (0.022, cy - pb, cz + zb), "paint", col=shade(rim or board, 0.8))
                for sx in (-1, 1):
                    cen = (sx * 0.03, cy, cz)
                    ring = [(sx * 0.03, cy - sx * px * k, cz + pz * k) for px, pz in poly]
                    for i in range(len(ring)):
                        b.tri(cen, ring[i], ring[(i + 1) % len(ring)], "paint", col=col)
                for yy in (cy - w * 0.32, cy + w * 0.32):
                    b.beam((0, yy, 0.05), (0, yy, cz + (hh / 2 if shape != "round" else w * 0.38)), w=0.016, mat="metal", col="iron", caps=False)
                if scroll:
                    pts = [(0, -out - 0.06 + 0.1 * math.sin(a), 0.16 - 0.1 * math.cos(a)) for a in [math.pi * 1.5 * i / 5 for i in range(6)]]
                    for i in range(5):
                        b.beam(pts[i], pts[i + 1], w=0.022, mat="metal", col="iron", caps=False)

    s.add(deco)


def bunting(b, p0, p1, n=None, sag=0.35, cols=("stripe_red", "stripe_yellow", "linen", "stripe_blue"), size=0.3, lod=1):
    """A string of little three-cornered flags from p0 to p1 (current frame); they flutter in the wind."""
    L = math.dist(p0, p1)
    n = n or max(3, int(L / 0.45))
    pt = lambda t: (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t) - sag * 4 * t * (1 - t))
    with b.detail(2):
        N = 6
        for i in range(N):
            b.beam(pt(i / N), pt((i + 1) / N), w=0.016, mat="cloth", col="#8a7a66", caps=False)
    with b.detail(lod):
        for k in range(n):
            t = (k + 0.5) / n
            a, c = pt(t - 0.32 / n), pt(t + 0.32 / n)
            m = pt(t)
            tip = (m[0], m[1], m[2] - size)
            col = cols[k % len(cols)]
            b.face([a, tip, c], "cloth", col=col, wind=(0.0, 0.8, 0.0))
            b.face([c, tip, a], "cloth", col=shade(col, 0.85), wind=(0.0, 0.8, 0.0))


def hoist(b, x=0.0, y=0.0, z=0.0, face=0.0, out=1.4, rope=4.0, load="crate", col="darkoak", strut=True, wheel=True):
    """A hoist: a beam poking `out` from a wall at (x, y, z) toward compass `face`, with a strut down to the wall, a
    pulley wheel at its end and a rope hanging `rope` metres with a hook and a load ('crate', 'sack', 'parcel', None)."""
    with b.at(x, y, z, rz=face):
        with b.detail(1):
            b.beam((0, 0.15, 0), (0, -out, 0), w=0.16, h=0.18, mat="timber", col=col)
            if strut:
                b.beam((0, 0.0, -0.8), (0, -out * 0.72, -0.1), w=0.1, mat="timber", col=col)
            if wheel:
                with b.at(0, -out + 0.14, -0.2, ry=90):
                    b.revolve([(0.0, -0.035), (0.13, -0.035), (0.13, 0.035), (0.0, 0.035)], "metal", col="iron", seg=8)
            b.beam((0, -out + 0.14, -0.2), (0, -out + 0.14, -rope), w=0.025, mat="cloth", col="#8a7a66", caps=False)
        with b.detail(2):
            with b.at(0, -out + 0.14, -rope):
                b.beam((0, 0, 0), (0, 0, -0.12), w=0.03, mat="metal", col="iron", caps=False)
                if load == "crate":
                    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                        b.beam((0, 0, -0.1), (sx * 0.24, sy * 0.24, -0.5), w=0.016, mat="cloth", col="#8a7a66", caps=False)
                    with b.at(0, 0, -1.0, rz=b.r(0, 40)):
                        b.box(0.52, 0.52, 0.5, "planks", col="#d8c3a0", bottom=True)
                elif load == "sack":
                    b.blob(0.26, 0.24, 0.34, mat="cloth", col="#d9c9a3", z=-0.45, seg=6, rings=3, rough=0.12)
                elif load == "parcel":
                    with b.at(0, 0, -0.5, rz=b.r(0, 40)):
                        b.box(0.44, 0.34, 0.3, "paint", col="#c9a57a", bottom=True)
                        b.beam((-0.225, 0, 0.305), (0.225, 0, 0.305), w=0.03, h=0.012, mat="paint", col="#b5433a", caps=False)
                        b.beam((0, -0.175, 0.305), (0, 0.175, 0.305), w=0.03, h=0.012, mat="paint", col="#b5433a", caps=False)
                    b.beam((0, 0, -0.1), (0, 0, -0.2), w=0.016, mat="cloth", col="#8a7a66", caps=False)


def pigeonholes(s, pos, z, cols=4, rows=2, dx=0.44, dz=0.5, hw=0.22, hh=0.28, ledge=True, birds=1, trim="ivory"):
    """A dovecote front on a wall (flat or round): cols x rows little arched pigeon-holes, each with a landing ledge,
    centred on pos with the bottom row at height z; `birds` pigeons sit on ledges."""
    b = s.b
    u = s.U(pos)
    rng = b.rng
    spots = [(i, j) for i in range(cols) for j in range(rows)]
    sit = set(rng.sample(spots, min(birds, len(spots))))

    def deco():
        for (i, j) in spots:
            with s.onu(u + (i - (cols - 1) / 2) * dx, z + j * dz):
                with b.detail(1):
                    pts = [(-hw / 2, 0), (hw / 2, 0), (hw / 2, hh * 0.6), (hw * 0.3, hh * 0.92), (0, hh), (-hw * 0.3, hh * 0.92), (-hw / 2, hh * 0.6)]
                    b.face([(p[0], -0.015, p[1]) for p in pts], "paint", col=DARK)
                with b.detail(2):
                    if trim:
                        for k in range(2, 6):
                            pa, pb = pts[k], pts[k + 1] if k + 1 < len(pts) else pts[0]
                            b.beam((pa[0], -0.02, pa[1]), (pb[0], -0.02, pb[1]), w=0.04, h=0.03, mat="planks", col=trim, up=(0, 1, 0), caps=False)
                    if ledge:
                        b.box(hw + 0.12, 0.16, 0.035, "planks", col="greyoak", x=0, y=-0.07, z=-0.035, bottom=True)
                    if (i, j) in sit:
                        pigeon(b, 0.0, -0.09, 0.0, rz=rng.uniform(-60, 60))

    s.add(deco)


# ---------------------------------------------------------------------------------------- life
def cat(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="#3b3532", sit=True, s=1.0):
    """A cat (sitting upright, or lying if sit=False) facing local -y. About 35 cm."""
    with b.at(x, y, z, rz=rz, s=s):
        with b.detail(2):
            if sit:
                b.blob(0.1, 0.12, 0.16, mat="cloth", col=col, z=0.15, seg=6, rings=3, rough=0.08)
                hz, hy = 0.36, -0.05
            else:
                b.blob(0.11, 0.2, 0.09, mat="cloth", col=col, z=0.085, seg=6, rings=3, rough=0.08)
                hz, hy = 0.17, -0.2
            b.blob(0.075, 0.075, 0.07, mat="cloth", col=col, y=hy, z=hz, seg=6, rings=3, rough=0.05)
            for sx in (-1, 1):
                b.tri((sx * 0.065, hy, hz + 0.035), (sx * 0.015, hy, hz + 0.06), (sx * 0.045, hy, hz + 0.13), "cloth", col=col)
                b.tri((sx * 0.015, hy, hz + 0.06), (sx * 0.065, hy, hz + 0.035), (sx * 0.045, hy, hz + 0.13), "cloth", col=shade(col, 0.8))
            b.beam((0, 0.1, 0.05), (0.14, 0.16, 0.04), w=0.035, mat="cloth", col=col, caps=False)
            b.beam((0.14, 0.16, 0.04), (0.2, 0.08, 0.06), w=0.03, mat="cloth", col=col, caps=False)


def pigeon(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="#e9e6df"):
    """A pigeon standing on z, facing local -y."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            b.blob(0.065, 0.1, 0.065, mat="cloth", col=col, z=0.085, seg=5, rings=3, rough=0.06)
            b.blob(0.04, 0.04, 0.04, mat="cloth", col=shade(col, 0.92), y=-0.08, z=0.16, seg=5, rings=2, rough=0.04)
            b.tri((-0.04, 0.07, 0.09), (0.04, 0.07, 0.09), (0, 0.2, 0.06), "cloth", col=shade(col, 0.8))
            b.tri((0.04, 0.07, 0.09), (-0.04, 0.07, 0.09), (0, 0.2, 0.06), "cloth", col=shade(col, 0.7))


def table(b, x=0.0, y=0.0, z=0.0, r=0.42, h=0.72, col="ivory", cloth=None):
    """A little round table (cloth = a colour for a table-cloth)."""
    with b.at(x, y, z):
        with b.detail(2):
            b.tube((0, 0, 0.03), (0, 0, h - 0.03), r=0.035, mat="metal", col="iron", n=5)
            b.revolve([(0.0, 0.0), (0.2, 0.0), (0.2, 0.03), (0.0, 0.03)], "metal", col="iron", seg=6)
            if cloth:
                b.revolve([(r + 0.03, h - 0.2), (r, h), (0.0, h + 0.004)], "cloth", col=cloth, seg=10, wind=0.1)
            else:
                b.revolve([(0.0, h - 0.04), (r, h - 0.04), (r, h), (0.0, h)], "planks", col=col, seg=10)


def chair(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="ivory"):
    """A cafe chair, its back toward local +y (so it faces -y)."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            b.box(0.38, 0.38, 0.035, "planks", col=col, z=0.43, bottom=True)
            for sx in (-1, 1):
                b.beam((sx * 0.16, -0.16, 0), (sx * 0.16, -0.16, 0.43), w=0.035, mat="planks", col=col, caps=False)
                b.beam((sx * 0.16, 0.17, 0), (sx * 0.16, 0.2, 0.88), w=0.035, mat="planks", col=col, caps=False)
            b.box(0.36, 0.025, 0.2, "planks", col=col, y=0.2, z=0.66, bottom=True)


def parasol(b, x=0.0, y=0.0, z=0.0, r=1.1, h=2.3, cols=("stripe_red", "linen"), n=8):
    """A striped cloth parasol on a pole."""
    with b.at(x, y, z):
        with b.detail(1):
            b.tube((0, 0, 0), (0, 0, h + 0.12), r=0.03, mat="planks", col="darkoak", n=5)
            for i in range(n):
                a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
                p = [(r * math.sin(a0), -r * math.cos(a0), h - r * 0.32), (r * math.sin(a1), -r * math.cos(a1), h - r * 0.32), (0, 0, h)]
                c = cols[i % len(cols)]
                b.face(p, "cloth", col=c, wind=(0.3, 0.3, 0.0))
                b.face(list(reversed(p)), "cloth", col=shade(c, 0.8), wind=(0.0, 0.3, 0.3))


def produce(b, x=0.0, y=0.0, z=0.0, s=0.56, rz=0.0, cols=None, tilt=14.0, h=0.26, n=3, crate_col="#d8c3a0"):
    """A shallow crate heaped with fruit or vegetables (cols = their colours), tipped up a little toward local -y."""
    rng = b.rng
    one = rng.choice(cols or FRUIT) if cols is None or len(cols) > 3 else None
    with b.at(x, y, z, rz=rz):
        with b.at(0, 0, 0.02 + (s / 2) * math.sin(rad(tilt)), rx=tilt):
            with b.detail(2):
                b.box(s, s, h, "planks", col=crate_col, top=False, bottom=True)
                b.quad((-s / 2, -s / 2, h * 0.55), (s / 2, -s / 2, h * 0.55), (s / 2, s / 2, h * 0.55), (-s / 2, s / 2, h * 0.55), "planks", col=shade(crate_col, 0.6))
                for i in range(n):
                    for j in range(n):
                        c = one if one else rng.choice(cols)
                        rr = s / n * 0.46
                        b.blob(rr, rr, rr * 0.9, mat="paint", col=shade(c, rng.uniform(0.88, 1.1)), x=-s / 2 + s * (i + 0.5) / n, y=-s / 2 + s * (j + 0.5) / n,
                               z=h * 0.55 + rr * 0.7, seg=5, rings=2, rough=0.12)


def stall(b, x=0.0, y=0.0, z=0.0, w=1.9, d=0.9, rz=0.0, cols=("stripe_red", "linen"), goods="fruit", canopy=True, h=2.05):
    """A market stall, its front toward local -y: a trestle table with goods on it and a striped canopy on four poles."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            b.box(w, d, 0.05, "planks", col="greyoak", z=0.78, bottom=True)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    b.beam((sx * (w / 2 - 0.12), sy * (d / 2 - 0.05), 0), (sx * (w / 2 - 0.3), sy * 0.04, 0.78), w=0.06, mat="timber", col="darkoak", caps=False)
            if canopy:
                for sx in (-1, 1):
                    for sy, top in ((-1, h - 0.3), (1, h + 0.15)):
                        b.beam((sx * (w / 2 + 0.03), sy * (d / 2 + 0.03), 0), (sx * (w / 2 + 0.03), sy * (d / 2 + 0.03), top), w=0.05, mat="timber", col="darkoak", caps=False)
                n = max(4, int(w / 0.3))
                y0, y1, z0, z1 = -d / 2 - 0.3, d / 2 + 0.1, h - 0.42, h + 0.18
                for i in range(n):
                    x0, x1 = -w / 2 - 0.1 + (w + 0.2) * i / n, -w / 2 - 0.1 + (w + 0.2) * (i + 1) / n
                    c = cols[i % len(cols)]
                    p = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z1), (x0, y1, z1)]
                    b.face(p, "cloth", col=c, wind=(0.3, 0.3, 0.05, 0.05))
                    b.face(list(reversed(p)), "cloth", col=shade(c, 0.78), wind=(0.05, 0.05, 0.3, 0.3))
                    v = [(x0, y0, z0 - 0.14), (x1, y0, z0 - 0.14), (x1, y0, z0), (x0, y0, z0)]
                    b.face(v, "cloth", col=c, wind=(0.6, 0.6, 0.3, 0.3))
                    b.face(list(reversed(v)), "cloth", col=shade(c, 0.78), wind=(0.3, 0.3, 0.6, 0.6))
        if goods:
            with b.at(0, -d * 0.2, 0.83):
                if callable(goods):
                    goods(b, w)
                else:
                    display(b, w - 0.2, goods, depth=0.2)
            with b.at(0, d * 0.18, 0.83):
                if not callable(goods):
                    display(b, w - 0.3, goods, depth=0.2)


# ---------------------------------------------------------------------------------------- added later
def steps(s, pos, w=1.6, n=3, rise=0.17, tread=0.3, mat="ashlar", col="stone", lod=1, z=None, spread=0.12):
    """A flight of n stone steps up to a door on a flat or round wall, centred on pos. The top one is level with z
    (default n * rise: give the door the same z); each lower step is one tread deeper and a little wider.
    (P.door(steps=n) stacks its slabs upside down when n > 1, so use this for more than one step.)"""
    b = s.b
    u = s.U(pos)
    top = n * rise if z is None else z

    def deco():
        with s.onu(u, 0.0):
            with b.detail(lod):
                for i in range(n):                      # i = 0 is the lowest, deepest slab
                    k = n - i
                    b.box(w + 2 * spread * (k - 1), tread * k + 0.06, rise, mat, col=shade(col, 1.0 - 0.03 * (i % 2)), x=0, y=-(tread * k) / 2 + 0.03,
                          z=top - rise * k)

    s.add(deco)


def putlogs(s, n=10, z0=1.5, z1=None, size=0.16, u0=0.3, u1=None):
    """Putlog holes: small dark square sockets scattered in rows over an old tower wall (near level only)."""
    b = s.b
    z1 = s.h - 0.5 if z1 is None else z1
    u1 = s.w - 0.3 if u1 is None else u1
    rng = b.rng
    rows = max(1, int((z1 - z0) / 1.6))
    spots = []
    for _ in range(n):
        u, z = rng.uniform(u0, u1), z0 + (z1 - z0) * rng.randrange(rows + 1) / max(rows, 1) + rng.uniform(-0.05, 0.05)
        if not (s._in_hole(u, z) or s._in_hole(u - 0.3, z) or s._in_hole(u + 0.3, z) or s._in_hole(u, z + 0.3) or s._in_hole(u, z - 0.3)):
            spots.append((u, z))

    def deco():
        with b.detail(2):
            for u, z in spots:
                with s.onu(u, z):
                    h = size / 2
                    b.quad((-h, -0.012, -h), (h, -0.012, -h), (h, -0.012, h), (-h, -0.012, h), "paint", col=DARK)

    s.add(deco)


def sundial(s, pos, z, r=0.6, face="ivory", col="brass"):
    """A painted sundial on a flat wall, centred at (pos, z): a half-round dial with hour lines and a gnomon."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            n = 10
            pts = [(-r * math.cos(math.pi * i / n), -0.03, -r * math.sin(math.pi * i / n)) for i in range(n + 1)]
            with b.detail(1):
                for i in range(n):
                    b.tri((0, -0.03, 0.0), pts[i + 1], pts[i], "paint", col=face)
                b.box(2 * r + 0.16, 0.07, 0.1, "ashlar", col="stone", x=0, y=-0.035, z=0.0, bottom=True)
            with b.detail(2):
                for i in range(1, n):
                    a = math.pi * i / n
                    b.beam((-r * 0.55 * math.cos(a), -0.036, -r * 0.55 * math.sin(a)), (-r * 0.92 * math.cos(a), -0.036, -r * 0.92 * math.sin(a)), w=0.025, h=0.008,
                           mat="paint", col="black", up=(0, 1, 0), caps=False)
                b.tri((0, -0.03, 0.0), (0, -0.03, -r * 0.5), (0, -0.03 - r * 0.45, -r * 0.5), "metal", col=col)
                b.tri((0, -0.03, 0.0), (0, -0.03 - r * 0.45, -r * 0.5), (0, -0.03, -r * 0.5), "metal", col=col)

    s.add(deco)


def ball(b, x=0.0, y=0.0, z=0.0, r=0.16, mat="ashlar", col="stone", lod=1, seg=6):
    """A stone (or metal) ball finial sitting on (x, y, z)."""
    with b.at(x, y, z):
        b.revolve([(r * 0.45, 0.0), (r * 0.9, r * 0.45), (r, r), (r * 0.8, r * 1.6), (0.0, r * 2.0)], mat, col=col, seg=seg, lod=lod)


def post_lantern(b, x=0.0, y=0.0, z=0.0, s=0.2, strength=1.0):
    """A lantern standing on top of a post or pier at (x, y, z); lights up at dusk."""
    with b.at(x, y, z):
        with b.detail(2):
            b.box(s, s, s * 1.3, "glow", col="#ffd88a", z=0.03)
            b.box(s * 1.25, s * 1.25, 0.03, "metal", col="iron", bottom=True)
            b.box(s * 1.35, s * 1.35, 0.04, "metal", col="iron", z=s * 1.3 + 0.03, taper=0.3, bottom=True)
        b.lamp(0, 0, s * 0.7 + 0.03, strength)
