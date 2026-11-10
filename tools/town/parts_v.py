"""Cairnwick parts: what the cliff village (buildings v_*) is made of, on top of kit.py and parts.py.

The village is hard and low, hunkered against the wind, so its vocabulary differs from the harbour town's:

  BBody / BWall        battered (inward leaning) rubble walls with deep openings; gables and lean-to ends are
                       part of the wall, so they can carry loft doors and vents
  Roof                 what BBody.gable / .shed return: frames on the slopes, for weights, ropes, turf ...
  skews, crowsteps     gables that rise above the slates and are coped with stone, instead of oversailing verges
  weights, ropes       stones lying on the slates, ropes over the ridge with stones hanging at the eaves
  mound_roof           a rounded thatch or turf roof on a round-cornered eave line (blackhouse fashion)
  hull                 a clinker boat: upturned beside a house, cut in half as a porch, or as a bothy's roof
  drystone, gate       yard walls with upright cope stones
  trestle, deck        raking timber towers and their stages (wind pump, lookout)
  ... and the small things: peat stacks, creels, floats, fish racks, a fire basket, vanes, an anemometer.

Positions on walls follow the kit: metres from the wall's left end as seen from outside, heights above its base.
"""
import math
from contextlib import contextmanager

import kit
from kit import C, M, PAL, lerp, mix, rad, shade, vadd, vcross, vdot, vlen, vlerp, vmul, vnorm, vsub
import parts as P

ROPE = "#b89e70"
TURF = "!#83a550"
TURF_DRY = "!#a3ab5a"
PEAT = "!#40342c"
TAR = "!#343134"
HEATHER = "#b58ad6"
LICHEN = "#d9cf7a"


# ---------------------------------------------------------------------------------------- flat geometry helpers
def _clip(poly, a, c):
    """Clip a convex polygon [(u, z), ...] to the left of the directed line a -> c."""
    out = []
    n = len(poly)
    ex, ez = c[0] - a[0], c[1] - a[1]
    side = lambda p: ex * (p[1] - a[1]) - ez * (p[0] - a[0])
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        sp, sq = side(p), side(q)
        if sp >= -1e-9:
            out.append(p)
        if (sp > 1e-9 and sq < -1e-9) or (sp < -1e-9 and sq > 1e-9):
            t = sp / (sp - sq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def _inside(O, p, margin=0.0):
    """Is point p inside the convex anticlockwise outline O by at least `margin`?"""
    n = len(O)
    for i in range(n):
        a, c = O[i], O[(i + 1) % n]
        ex, ez = c[0] - a[0], c[1] - a[1]
        L = math.hypot(ex, ez) or 1.0
        if (ex * (p[1] - a[1]) - ez * (p[0] - a[0])) / L < margin:
            return False
    return True


def _area(poly):
    n = len(poly)
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))


def _tris(poly):
    """Index triples (anticlockwise) that fill a simple polygon [(x, y), ...]: ear clipping."""
    n = len(poly)
    idx = list(range(n)) if _area(poly) > 0 else list(range(n - 1, -1, -1))
    cr = lambda o, a, c: (a[0] - o[0]) * (c[1] - o[1]) - (a[1] - o[1]) * (c[0] - o[0])
    out = []
    guard = 0
    while len(idx) > 3 and guard < 400:
        guard += 1
        m = len(idx)
        for k in range(m):
            i0, i1, i2 = idx[(k - 1) % m], idx[k], idx[(k + 1) % m]
            a, c, e = poly[i0], poly[i1], poly[i2]
            if cr(a, c, e) <= 1e-12:
                continue
            if any(cr(a, c, poly[j]) > 1e-12 and cr(c, e, poly[j]) > 1e-12 and cr(e, a, poly[j]) > 1e-12 for j in idx if j not in (i0, i1, i2)):
                continue
            out.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            break
    if len(idx) == 3:
        out.append(tuple(idx))
    return out


def shape(b, pts, mat="metal", col="iron", lod=2, both=True, y=0.0, wind=0.0, t=0.012):
    """A flat cut-out standing in the local x-z plane (facing -y): pts = [(x, z), ...], any simple outline.
    wind = a weight, or a function of (x, z) giving one (so that a hanging thing can swing from its top)."""
    wf = wind if callable(wind) else (lambda x, z: wind)
    for (i, j, k) in _tris(pts):
        tri = [pts[i], pts[j], pts[k]]
        b.face([(p[0], y - (t / 2 if both else 0.0), p[1]) for p in tri], mat, col=col, lod=lod, wind=tuple(wf(*p) for p in tri))
        if both:
            tri.reverse()
            b.face([(p[0], y + t / 2, p[1]) for p in tri], mat, col=shade(col, 0.82), lod=lod, wind=tuple(wf(*p) for p in tri))


def skin(b, rings, mat, col=None, lod=0, smooth=True, closed=True, cols=None, flip=False, wind=0.0, uvs=None):
    """Stretch a surface over a stack of rings (each a list of points, all the same length). Seen from outside,
    each ring runs anticlockwise looking down on it and the rings climb; flip=True turns the faces over."""
    sm = b.sm() if smooth else 0
    uo, vo = b.uvo()
    n = len(rings[0])
    m = n if closed else n - 1
    us = [0.0]
    for i in range(1, n + 1):
        us.append(us[-1] + vlen(vsub(rings[0][i % n], rings[0][i - 1])))
    vs = [0.0]
    for j in range(1, len(rings)):
        vs.append(vs[-1] + max(vlen(vsub(rings[j][i], rings[j - 1][i])) for i in range(n)))
    for j in range(len(rings) - 1):
        c = cols[j] if cols else col
        for i in range(m):
            k = (i + 1) % n
            q = [rings[j][i], rings[j][k], rings[j + 1][k], rings[j + 1][i]]
            uv = [(uo + us[i], vo + vs[j]), (uo + us[i + 1], vo + vs[j]), (uo + us[i + 1], vo + vs[j + 1]), (uo + us[i], vo + vs[j + 1])]
            if flip:
                q.reverse(); uv.reverse()
            b.face(q, mat, col=c, lod=lod, sm=sm, uv=uv, wind=wind)


def beam(b, p0, p1, w=0.14, h=None, mat="timber", col=None, lod=1, up=(0, 0, 1), caps=True, wind=0.0):
    """kit.Building.beam with end caps that face outward (the kit's own are wound inside out, so in the game,
    which culls back faces, a kit beam's ends are open)."""
    b.beam(p0, p1, w=w, h=h, mat=mat, col=col, lod=lod, up=up, caps=False, wind=wind)
    if not caps:
        return
    h = w if h is None else h
    a = vsub(p1, p0)
    L = vlen(a)
    if L < 1e-6:
        return
    a = vmul(a, 1 / L)
    s = vcross(a, up)
    if vlen(s) < 1e-4:
        s = vcross(a, (1, 0, 0))
    s = vnorm(s)
    u2 = vnorm(vcross(s, a))
    c0 = [vadd(p0, vadd(vmul(s, sx * w / 2), vmul(u2, sz * h / 2))) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    c1 = [vadd(q, vmul(a, L)) for q in c0]
    b.quad(c0[0], c0[1], c0[2], c0[3], mat, col=shade(col, 0.85), lod=lod, wind=wind)
    b.quad(c1[3], c1[2], c1[1], c1[0], mat, col=shade(col, 0.85), lod=lod, wind=wind)


def verge_faces(b, length, span, pitch, eave=0.3, verge=0.2, thick=0.16, lip=0.045, half=False, mat="planks", col="darkoak", lod=0):
    """The edge of a pitched roof's thickness over its gable ends, facing outward (the kit winds these inside out).
    Call in the frame the roof was built in: for a gable roof the frame gable_roof uses (ridge along x through the
    origin at height rise); for a lean-to the high edge on the x axis at z = rise."""
    t = math.tan(rad(pitch))
    run = span if half else span / 2
    rise = run * t
    for sx in (-1, 1):
        xe = sx * (length / 2 + verge + 0.003)
        for sgn in ((1,) if half else (1, -1)):
            ye = -sgn * (run + eave)
            q = [(xe, ye, -eave * t - thick), (xe, 0.0, rise - thick), (xe, 0.0, rise + lip), (xe, ye, -eave * t + lip)]
            if (sx < 0) == (sgn > 0):
                q.reverse()
            b.face(q, mat, col=col, lod=lod)


# ---------------------------------------------------------------------------------------- battered walls
class BWall(kit.Wall):
    """A flat wall with any convex outline [(u, z), ...] (anticlockwise seen from outside): a trapezoid for a
    battered wall, with a gable or a lean-to top as part of it. Openings may be cut anywhere inside the outline."""

    def __init__(self, b, w, h, mat="masonry", col=None, depth=0.42, lod=0, uvo=None, outline=None):
        kit.Wall.__init__(self, b, w, h, mat, C(col), depth, 0.0, lod, uvo or b.uvo(), None, None, 0.0)
        self.outline = outline or [(0.0, 0.0), (w, 0.0), (w, h), (0.0, h)]
        self.ucuts = set()
        self.halo = 0.3 if mat == "plaster" else 0.0      # smooth walls: keep the shade of sills and shutters close to them
        b._walls.append(self)

    def top_at(self, u):
        """Height of the wall's top edge above position u."""
        O = self.outline
        best = 0.0
        for i in range(len(O)):
            a, c = O[i], O[(i + 1) % len(O)]
            if abs(c[0] - a[0]) > 1e-9 and min(a[0], c[0]) - 1e-9 <= u <= max(a[0], c[0]) + 1e-9:
                best = max(best, a[1] + (c[1] - a[1]) * (u - a[0]) / (c[0] - a[0]))
        return best

    def emit(self):
        b = self.b
        uo, vo = self.uvo
        O = self.outline
        u0, u1 = min(p[0] for p in O), max(p[0] for p in O)
        z0, z1 = min(p[1] for p in O), max(p[1] for p in O)
        cl = lambda v, lo, hi: min(max(v, lo), hi)
        with b.frame(self.m):
            hu = {cl(o[k] + d, u0, u1) for o in self.ops for k, d in (("u0", -self.halo), ("u1", self.halo))} if self.halo else set()
            hz = {cl(o[k] + d, z0, z1) for o in self.ops for k, d in (("z0", -self.halo), ("z1", self.halo))} if self.halo else set()
            us = kit._grid({p[0] for p in O} | {cl(o[k], u0, u1) for o in self.ops for k in ("u0", "u1")} | {cl(c, u0, u1) for c in self.ucuts} | hu, u1 - u0, self.cell)
            zs = kit._grid({p[1] for p in O} | {cl(o[k], z0, z1) for o in self.ops for k in ("z0", "z1")} | hz, z1 - z0, self.cell)
            for j in range(len(zs) - 1):
                za, zb = zs[j], zs[j + 1]
                if zb - za < 1e-6:
                    continue
                for i in range(len(us) - 1):
                    ua, ue = us[i], us[i + 1]
                    if ue - ua < 1e-6 or self._in_hole((ua + ue) / 2, (za + zb) / 2):
                        continue
                    poly = [(ua, za), (ue, za), (ue, zb), (ua, zb)]
                    if not all(_inside(O, p, -1e-7) for p in poly):
                        for k in range(len(O)):
                            poly = _clip(poly, O[k], O[(k + 1) % len(O)])
                            if len(poly) < 3:
                                break
                        if len(poly) < 3 or abs(_area(poly)) < 1e-6:
                            continue
                    b.face([(p[0], 0.0, p[1]) for p in poly], self.mat, col=self.col, lod=self.lod, uv=[(uo + p[0], vo + p[1]) for p in poly])
            self._emit_openings()
        self._finish()


class Roof:
    """Where a pitched roof's slopes are, so that things can be laid on them. `faces` = the compass directions
    its slopes look (0 front, 90 right, 180 back, 270 left)."""

    def __init__(self, b, x, y, z, length, span, pitch, faces, eave=0.3, verge=0.0, lip=0.05, half=False):
        self.b, self.x, self.y, self.z, self.length, self.span, self.pitch = b, x, y, z, length, span, pitch
        self.faces, self.eave, self.verge, self.lip, self.half = faces, eave, verge, lip, half
        self.run = span if half else span / 2
        self.rise = self.run * math.tan(rad(pitch))
        self.L = self.run / math.cos(rad(pitch))          # slope length, wall line to ridge
        self.Le = eave / math.cos(rad(pitch))             # and from the wall line down to the eave's edge

    @contextmanager
    def on(self, face=None):
        """A frame lying on the slope that looks toward `face`: origin on the wall line at mid length, x along the
        eave (to the right, seen from outside), y up the slope, z out of the roof."""
        b = self.b
        face = self.faces[0] if face is None else face
        off = self.span / 2 if not self.half else self.span / 2
        with b.at(self.x, self.y, self.z, rz=face):
            with b.at(0, -off, 0, rx=self.pitch):
                yield b

    @property
    def top(self):
        return self.z + self.rise


class BBody:
    """Four battered walls of a block w by d at the foot, h high, standing on z, centred on x with the front wall
    on y = 0 unless y (the centre) is given. batter = how far the walls lean in per metre of height.
    faces = {"front": ("plaster", "white"), ...} gives single walls another material (lime-washed fronts)."""

    def __init__(self, b, w, d, h, mat="masonry", col="grey", x=0.0, y=None, z=0.0, batter=0.05, depth=0.42, lod=0, foot=True, faces=None):
        y = d / 2 if y is None else y
        self.b, self.w, self.d, self.h, self.x, self.y, self.z, self.batter = b, w, d, h, x, y, z, batter
        self.mat, self.col = mat, C(col)
        self.k = math.sqrt(1 + batter * batter)
        self.e = batter * h
        self.tw, self.td = w - 2 * self.e, d - 2 * self.e
        self.lean = math.degrees(math.atan(batter))
        faces = faces or {}
        uo, vo = b.uvo()
        self.walls = []
        H = h * self.k
        for name, (ox, oy, rz, ww, off) in zip(("front", "right", "back", "left"),
                                               ((x - w / 2, y - d / 2, 0, w, 0.0), (x + w / 2, y - d / 2, 90, d, w), (x + w / 2, y + d / 2, 180, w, w + d), (x - w / 2, y + d / 2, 270, d, 2 * w + d))):
            m_, c_ = faces.get(name, (mat, col))
            with b.at(ox, oy, z, rz=rz):
                with b.at(rx=-self.lean):
                    wl = BWall(b, ww, H, m_, c_, depth=depth, lod=lod, uvo=(uo + off, vo + z),
                               outline=[(0.0, 0.0), (ww, 0.0), (ww - self.e, H), (self.e, H)])
            wl.name = name
            self.walls.append(wl)
        self.front, self.right, self.back, self.left = self.walls
        if foot:
            b.footprint(x - w / 2, y - d / 2, x + w / 2, y + d / 2, z + h)

    @property
    def top(self):
        return self.z + self.h

    def corner(self, sx, sy, zz):
        """Where the corner (sx, sy = -1 or 1) is at height zz above the base."""
        return (self.x + sx * (self.w / 2 - self.batter * zz), self.y + sy * (self.d / 2 - self.batter * zz), self.z + zz)

    def gable(self, ridge="x", pitch=45.0, skew=False, skew_col=None, apex="stone", **kw):
        """Roof the block with a gable roof; the two end walls grow into gables (and keep leaning).
        skew=True tucks the slates between raised, stone-coped gables. Returns a Roof."""
        b = self.b
        span = self.td if ridge == "x" else self.tw
        length = self.tw if ridge == "x" else self.td
        rise = span / 2 * math.tan(rad(pitch))
        H = self.h * self.k
        ends = (self.left, self.right) if ridge == "x" else (self.front, self.back)
        for wl in ends:
            wl.outline = [(0.0, 0.0), (wl.w, 0.0), (wl.w - self.e, H), (wl.w / 2, H + (rise - 0.03) * self.k), (self.e, H)]
        if skew:
            kw.setdefault("verge", -(self.batter * rise + 0.1))
            kw.setdefault("barge", False)
        kw.setdefault("eave", 0.3)
        kw.setdefault("verge", 0.22)
        kw.setdefault("sag", 0.02)          # (a whisper of sag makes the kit cut the slopes in four along their length,
        b.gable_roof(self.tw, self.td, pitch, x=self.x, y=self.y, z=self.z + self.h, ridge=ridge, **kw)      # so they follow the walls' wobble)
        if True:                    # (also between skews: a thick thatch shows its end at the eaves)
            with b.at(self.x, self.y, self.z + self.h, rz=0 if ridge == "x" else 90):
                verge_faces(b, length, span, pitch, eave=kw["eave"], verge=kw["verge"], thick=kw.get("thick", 0.16), lip=kw.get("lip", 0.045),
                            col=kw.get("soffit_col", "darkoak"))
        rf = Roof(b, self.x, self.y, self.z + self.h, length, span, pitch, (0, 180) if ridge == "x" else (90, 270), eave=kw["eave"], verge=kw["verge"], lip=kw.get("lip", 0.045))
        rf.ends = ends
        if skew:
            skews(self, rf, col=skew_col, apex=apex)
        return rf

    def shed(self, pitch=22.0, high="back", **kw):
        """Roof the block with a single slope rising toward the `high` wall ('back', 'front', 'left', 'right').
        The side walls get sloping tops. Returns a Roof."""
        b = self.b
        order = ["front", "right", "back", "left"]
        hi = order.index(high)
        lo = (hi + 2) % 4
        t = math.tan(rad(pitch))
        span0 = self.td if high in ("back", "front") else self.tw
        rise = span0 * t / (1 + self.batter * t)
        H0, H1 = self.h * self.k, (self.h + rise) * self.k
        e0, e1 = self.e, self.batter * (self.h + rise)
        hw = self.walls[hi]
        hw.outline = [(0.0, 0.0), (hw.w, 0.0), (hw.w - e1, H1), (e1, H1)]
        a = self.walls[(lo + 1) % 4]          # runs from the low wall to the high wall
        a.outline = [(0.0, 0.0), (a.w, 0.0), (a.w - e1, H1), (e0, H0)]
        c = self.walls[(hi + 1) % 4]          # runs from the high wall to the low wall
        c.outline = [(0.0, 0.0), (c.w, 0.0), (c.w - e0, H0), (e1, H1)]
        span = span0 - (e1 - e0)
        length = (self.tw if high in ("back", "front") else self.td)
        face = {"back": 0, "front": 180, "left": 90, "right": 270}[high]     # the way the slope looks
        kw.setdefault("eave", 0.3)
        kw.setdefault("verge", 0.2)
        cx = self.x + (0 if high in ("back", "front") else (1 if high == "right" else -1) * (self.tw / 2 - (e1 - e0)))
        cy = self.y + (0 if high in ("left", "right") else (1 if high == "back" else -1) * (self.td / 2 - (e1 - e0)))
        shed_roof(b, length, span, pitch, x=cx, y=cy, z=self.z + self.h + rise, face=face, **kw)
        # a Roof whose frame origin sits on the low wall line
        rf = Roof(b, 0, 0, 0, length, span, pitch, (face,), eave=kw["eave"], verge=kw["verge"], lip=kw.get("lip", 0.045), half=True)
        ax = math.sin(rad(face)); ay = -math.cos(rad(face))        # outward direction of the slope's fall
        rf.x, rf.y, rf.z = cx + ax * span / 2, cy + ay * span / 2, self.z + self.h
        rf.span = span
        return rf

    def hip(self, pitch=40.0, **kw):
        kw.setdefault("eave", 0.3)
        return self.b.loop_roof(self.tw, self.td, pitch, x=self.x, y=self.y, z=self.z + self.h, **kw)


def shed_roof(b, length, span, pitch, x=0.0, y=0.0, z=0.0, face=0.0, mat="slate", col=None, **kw):
    """A single slope (lean-to roof). (x, y, z) is the middle of its HIGH edge; it falls toward compass `face`
    over a horizontal distance `span`, and is `length` long. (Wraps the kit's half roof, whose own placing is off
    by half a span.)"""
    kw.setdefault("barge", False)
    kw.setdefault("eave", 0.3)
    kw.setdefault("verge", 0.2)
    if length > 3.0:
        kw.setdefault("sag", 0.012)
    with b.at(x, y, z - span * math.tan(rad(pitch)), rz=face):
        b.gable_roof(length, span, pitch, mat=mat, col=col, x=0, y=0, z=0, ridge="x", half=True, **kw)
        verge_faces(b, length, span, pitch, eave=kw["eave"], verge=kw["verge"], thick=kw.get("thick", 0.16), lip=kw.get("lip", 0.045), half=True,
                    col=kw.get("soffit_col", "darkoak"))
        xe, rise = length / 2 + kw["verge"], span * math.tan(rad(pitch))
        b.quad((xe, 0.004, rise - kw.get("thick", 0.16)), (-xe, 0.004, rise - kw.get("thick", 0.16)), (-xe, 0.004, rise + kw.get("lip", 0.045)), (xe, 0.004, rise + kw.get("lip", 0.045)),
               "planks", col=kw.get("soffit_col", "darkoak"), lod=kw.get("lod", 0))


def skews(body, rf, t=None, col=None, apex="stone", lod=0, copes=True):
    """Raised gable copings (skews) on both ends of a gabled BBody: the slates stop against them."""
    b = body.b
    col = shade(body.col, 1.08) if col is None else C(col)
    t = t or max(0.34, body.batter * rf.rise + 0.26)
    H = body.h * body.k
    g = (rf.rise - 0.03) * body.k
    for wl in rf.ends:
        with b.frame(wl.m):
            A = (wl.w / 2, H + g + 0.1)
            yc = t / 2 - 0.05
            for sgn, foot in ((1, (body.e - 0.06, H - 0.04)), (-1, (wl.w - body.e + 0.06, H - 0.04))):
                ax, az = A[0] - foot[0], A[1] - foot[1]
                L = math.hypot(ax, az)
                nx, nz = (-az / L, ax / L) if sgn > 0 else (az / L, -ax / L)        # in-plane normal pointing up and out
                o = 0.07
                p0 = (foot[0] + nx * o, yc, foot[1] + nz * o)
                p1 = (A[0] + nx * o, yc, A[1] + nz * o)
                beam(b, p0, p1, w=0.3, h=t, mat="masonry", col=col, lod=lod, up=(0, 1, 0))
                if copes:
                    n = max(2, int(L / 0.6))
                    for i in range(n):
                        q0 = vlerp(p0, p1, i / n); q1 = vlerp(p0, p1, (i + 0.94) / n)
                        q0 = (q0[0] + nx * 0.17, yc, q0[2] + nz * 0.17); q1 = (q1[0] + nx * 0.19, yc, q1[2] + nz * 0.19)
                        beam(b, q0, q1, w=0.06, h=t + 0.07, mat="flagstone", col=shade("grey", b.r(0.86, 1.06)), lod=2, up=(0, 1, 0))
                # the skewputt: a big stone carrying the foot of the coping
                b.stone(0.44, t + 0.1, 0.34, mat="masonry", col=shade(col, 1.05), lod=1, x=foot[0] + sgn * 0.02, y=yc, z=foot[1] - 0.18, ch=0.18, jitter=0.08)
            if apex == "stone":
                b.stone(0.4, t + 0.1, 0.36, mat="masonry", col=shade(col, 1.05), lod=1, x=A[0], y=yc, z=A[1] - 0.12, ch=0.2, jitter=0.08)
            elif apex == "knob":
                b.stone(0.4, t + 0.1, 0.3, mat="masonry", col=shade(col, 1.05), lod=1, x=A[0], y=yc, z=A[1] - 0.12, ch=0.2, jitter=0.06)
                with b.at(A[0], yc, A[1] + 0.16):
                    b.revolve([(0.07, 0.0), (0.06, 0.12), (0.15, 0.24), (0.15, 0.34), (0.0, 0.46)], "masonry", col=shade(col, 1.1), seg=7, lod=1)


def crowsteps(body, rf, n=6, t=None, col=None, lod=1):
    """Crow-stepped gables: the gable climbs above the slates in stone steps (use with gable(verge=-0.2, barge=False))."""
    b = body.b
    col = shade(body.col, 1.06) if col is None else C(col)
    t = t or max(0.36, body.batter * rf.rise + 0.28)
    H = body.h * body.k
    g = rf.rise * body.k
    for wl in rf.ends:
        with b.frame(wl.m):
            yc = t / 2 - 0.05
            half = wl.w / 2 - body.e
            for sgn in (1, -1):
                for i in range(n):
                    f0, f1 = i / n, (i + 1) / n
                    uc = wl.w / 2 - sgn * half * (1 - (f0 + f1) / 2)
                    zb = H + g * f0 - 0.14
                    hh = g * (f1 - f0) + 0.34
                    b.stone(half / n + 0.03, t, hh, mat="masonry", col=col, lod=lod, x=uc, y=yc, z=zb, ch=0.1, jitter=0.05)
                    with b.detail(2):
                        b.box(half / n + 0.12, t + 0.1, 0.06, "flagstone", col=shade("grey", b.r(0.88, 1.05)), x=uc, y=yc, z=zb + hh, bottom=True)
            b.stone(0.5, t, 0.5, mat="masonry", col=col, lod=lod, x=wl.w / 2, y=yc, z=H + g - 0.05, ch=0.12, jitter=0.05)
            with b.detail(2):
                b.box(0.6, t + 0.1, 0.06, "flagstone", col="grey", x=wl.w / 2, y=yc, z=H + g + 0.45, bottom=True)


def footing(body, h=0.45, out=0.09, col=None, skirt=3.0, boulders="f", size=(0.55, 0.95), mat="masonry"):
    """The base of a battered block: a spreading course (with boulders on the sides named in `boulders`, 'frbl')
    and the hidden foundation that keeps it grounded on a slope. Doorways are left clear."""
    b = body.b
    col = shade(body.col if body.mat == "masonry" else "grey", 0.94) if col is None else C(col)
    m0 = b._m.copy()

    def deco():
        rng = b.rng
        for key, wl in zip("frbl", body.walls):
            cuts = sorted((max(o["u0"] - 0.05, -out), min(o["u1"] + 0.05, wl.w + out)) for o in wl.ops if o["z0"] < h - 0.05)
            spans, a = [], -out
            for c0, c1 in cuts:
                if c0 > a + 0.02:
                    spans.append((a, c0))
                a = max(a, c1)
            if wl.w + out > a + 0.02:
                spans.append((a, wl.w + out))
            with b.frame(wl.m):
                for ua, ub in spans:
                    b.box(ub - ua, out + 0.05, h, mat, col=col, x=(ua + ub) / 2, y=(0.05 - out) / 2, z=0, lod=0, tx=1.0, ty=0.62)
                    if key in boulders:
                        u = ua + 0.05
                        while u < ub - 0.3:
                            sw = min(rng.uniform(*size), ub - u)
                            b.stone(sw * 0.94, 0.3, rng.uniform(0.3, 0.52), mat=mat, col=shade(col, rng.uniform(0.95, 1.12)), lod=2, x=u + sw / 2, y=-out + 0.04, z=0.0, ch=0.26, jitter=0.16)
                            u += sw
        with b.frame(m0):
            with b.at(body.x, body.y, body.z):
                b.box(body.w + 2 * out, body.d + 2 * out, skirt, mat, col=shade(col, 0.85), z=-skirt, top=False, lod=0)

    if body.front.done:
        deco()
    else:
        body.front.add(deco)


def quoins(body, corners="fr", size=(0.62, 0.34, 0.42), z0=0.0, z1=None, proud=0.045, col=None, lod=2, mat="masonry"):
    """Big corner stones, long and short alternately, following the batter. corners: f = front-left, r = front-right,
    b = back-right, l = back-left (the kit's order)."""
    b = body.b
    col = shade(body.col if body.mat == "masonry" else "grey", 1.1) if col is None else C(col)
    z1 = body.h if z1 is None else z1
    Lq, Sq, Hq = size
    n = max(1, int((z1 - z0) / Hq))
    hh = (z1 - z0) / n
    cs = {"f": (-1, -1), "r": (1, -1), "b": (1, 1), "l": (-1, 1)}
    ends = {"f": ((body.front, 0), (body.left, 1)), "r": ((body.front, 1), (body.right, 0)), "b": ((body.right, 1), (body.back, 0)), "l": ((body.back, 1), (body.left, 0))}
    for key in corners:
        for wl, end in ends[key]:          # keep the corner's shade at the corner
            if wl.w > 2.6 and not wl.done:
                wl.ucuts.add(wl.w - Lq - 0.05 if end else Lq + 0.05)
        sx, sy = cs[key]
        for i in range(n):
            lx, ly = (Lq, Sq) if i % 2 == 0 else (Sq, Lq)
            cx, cy, cz = body.corner(sx, sy, z0 + hh * (i + 0.5))
            with b.at(cx - sx * (lx / 2 - proud), cy - sy * (ly / 2 - proud), body.z + z0 + hh * i):
                b.stone(lx, ly, hh * 0.95, mat=mat, col=shade(col, b.r(0.92, 1.08)), lod=lod, ch=0.14, jitter=0.07)


def rubble(s, n=18, size=(0.3, 0.6), proud=0.06, z0=0.05, z1=None, u0=None, u1=None, mat=None, col=None, lod=2):
    """Single stones standing a little proud of a wall, kept inside its outline (gables too) and clear of openings."""
    b = s.b
    O = getattr(s, "outline", None) or [(0.0, 0.0), (s.w, 0.0), (s.w, s.h), (0.0, s.h)]
    zt = max(p[1] for p in O) if z1 is None else z1
    ua = min(p[0] for p in O) if u0 is None else u0
    ub = max(p[0] for p in O) if u1 is None else u1
    rng = b.rng
    spots = []
    for _ in range(n * 6):
        if len(spots) >= n:
            break
        w = rng.uniform(*size)
        h = w * rng.uniform(0.45, 0.72)
        u, z = rng.uniform(ua + w / 2, ub - w / 2), rng.uniform(z0, max(zt - h, z0 + 0.01))
        if not all(_inside(O, q, 0.04) for q in ((u - w / 2, z), (u + w / 2, z), (u + w / 2, z + h), (u - w / 2, z + h))):
            continue
        if any(s._in_hole(uu, zz) for uu in (u - w / 2 - 0.08, u, u + w / 2 + 0.08) for zz in (z - 0.08, z + h / 2, z + h + 0.08)):
            continue
        spots.append((u, z, w, h, rng.uniform(-4, 4)))

    def deco():
        for (u, z, w, h, tilt) in spots:
            with s.onu(u, z):
                with b.at(0, 0.02, h / 2, ry=tilt):
                    with b.at(rx=90):
                        b.stone(w, h, proud + 0.02, mat=mat or s.mat, col=col if col is not None else s.col, lod=lod, jitter=0.16)

    s.add(deco)


def harl(s, n=10, where="base", col="grey", size=(0.3, 0.55)):
    """Bare rubble showing through a lime-washed wall: along its 'base', at its 'ends', or 'both'."""
    O = getattr(s, "outline", None)
    w = max(p[0] for p in O) if O else s.w
    if where in ("base", "both"):
        rubble(s, n=n, size=size, proud=0.03, z0=0.0, z1=0.9, mat="masonry", col=col)
    if where in ("ends", "both"):
        rubble(s, n=n // 2 + 1, size=size, proud=0.03, z0=0.1, z1=1.9, u0=0.0, u1=min(1.2, w * 0.25), mat="masonry", col=col)
        rubble(s, n=n // 2 + 1, size=size, proud=0.03, z0=0.1, z1=1.6, u0=max(w - 1.2, w * 0.75), u1=w, mat="masonry", col=col)


# ---------------------------------------------------------------------------------------- openings
def _cut(s, u, z, w, h, **kw):
    """Cut an opening by metres along the wall, whatever kind of wall it is. On a round, tapering wall the kit
    measures widths at the wall's mean radius: correct for that, so the hole is really w wide where it is."""
    if hasattr(s, "radius"):
        w = w * s.rref / max(s.radius(z + h / 2), 1e-6)
    return kit._Surface.opening(s, u, z, w, h, **kw)


def _leaf(b, x0, x1, hs, col, lod=1):
    """One ledged-and-braced plank leaf (a storm shutter or a door half) in the hinge frame."""
    b.box(x1 - x0 - 0.02, 0.045, hs - 0.02, "planks", col=col, x=(x0 + x1) / 2, y=-0.022, z=0.01, lod=lod, bottom=True)
    with b.detail(2):
        for zz in (hs * 0.18, hs * 0.82):
            beam(b, (x0 + 0.03, -0.055, zz), (x1 - 0.03, -0.055, zz), w=0.022, h=0.075, mat="planks", col=shade(col, 0.76), up=(0, 0, 1), caps=False)
        beam(b, (x0 + 0.04, -0.055, hs * 0.2), (x1 - 0.04, -0.055, hs * 0.8), w=0.02, h=0.06, mat="planks", col=shade(col, 0.76), up=(0, 1, 0), caps=False)


def window(s, pos, z, w=0.62, h=0.82, col=None, shut="open", lintel="slab", sill=True, bars=(1, 1), frame="ivory", depth=None, glass=None, arch=0.0):
    """A small deep-set window. col = paint of its storm shutters (None: no shutters); shut = 'open' (a pair folded
    back), 'one' (a single leaf folded back), 'half' (one leaf closed) or 'closed'. lintel = 'slab', 'timber', None."""
    b = s.b
    u = s.U(pos)
    op = _cut(s, u, z, w, h, depth=depth, pane="glass", pane_col=glass, arch=arch)
    d = op["d"]
    rng = b.rng
    aj = rng.uniform(5, 18)
    aj2 = rng.uniform(5, 18)
    side = rng.choice((-1, 1))
    lc = shade(mix(s.col if s.mat == "masonry" else C("grey"), "stone", 0.35), rng.uniform(1.0, 1.14))

    def deco():
        with s.onu(u, z):
            fy = d * 0.72
            ft = 0.05
            hs = h - arch
            with b.detail(1):
                for sx in (-1, 1):
                    beam(b, (sx * (w / 2 - ft / 2), fy, 0), (sx * (w / 2 - ft / 2), fy, hs), w=ft, h=0.06, mat="planks", col=frame, up=(0, 1, 0), caps=False)
                beam(b, (-w / 2, fy, ft / 2), (w / 2, fy, ft / 2), w=0.06, h=ft, mat="planks", col=frame, up=(0, 0, 1), caps=False)
                if arch < 1e-4:
                    beam(b, (-w / 2, fy, h - ft / 2), (w / 2, fy, h - ft / 2), w=0.06, h=ft, mat="planks", col=frame, up=(0, 0, 1), caps=False)
            with b.detail(2):
                nv, nh = bars
                for i in range(nv):
                    x = -w / 2 + w * (i + 1) / (nv + 1)
                    beam(b, (x, fy + 0.01, ft), (x, fy + 0.01, h - ft), w=0.03, h=0.035, mat="planks", col=frame, up=(0, 1, 0), caps=False)
                for i in range(nh):
                    zz = hs * (i + 1) / (nh + 1)
                    beam(b, (-w / 2 + ft, fy + 0.01, zz), (w / 2 - ft, fy + 0.01, zz), w=0.035, h=0.03, mat="planks", col=frame, up=(0, 0, 1), caps=False)
            if sill:
                b.box(w + 0.2, 0.2, 0.08, "flagstone", col=shade("grey", 1.02), x=0, y=-0.03, z=-0.08, lod=1, bottom=True)
            if lintel == "slab" and arch < 1e-4:
                with b.at(0, 0.03, h + 0.125):
                    with b.at(rx=90):
                        b.stone(w + 0.42, 0.25, 0.09, mat="masonry", col=lc, lod=1, jitter=0.07, ch=0.16)
            elif lintel == "timber" and arch < 1e-4:
                beam(b, (-w / 2 - 0.2, -0.015, h + 0.09), (w / 2 + 0.2, -0.015, h + 0.09), w=0.1, h=0.18, mat="timber", col="darkoak", lod=1, up=(0, 0, 1))
            elif arch > 1e-4 and lintel:
                with b.detail(2):
                    n = 5
                    for i in range(n):
                        a = math.pi * (i + 0.5) / n
                        x, zz = -(w / 2 + 0.1) * math.cos(a), hs + (arch + 0.1) * math.sin(a)
                        with b.at(x, -0.03, zz, ry=-(90 - math.degrees(a))):
                            with b.at(rx=90):
                                b.stone(0.2, 0.26, 0.07, mat="masonry", col=lc, jitter=0.08)
            if col is not None:
                if shut == "open":
                    for sgn, a_ in ((-1, aj), (1, aj2)):
                        with b.at(sgn * w / 2, -0.03, 0, rz=-sgn * a_):
                            _leaf(b, *((-w / 2, 0) if sgn < 0 else (0, w / 2)), hs, col)
                elif shut == "one":
                    with b.at(side * w / 2, -0.03, 0, rz=-side * aj):
                        _leaf(b, *((-w, 0) if side < 0 else (0, w)), hs, col)
                elif shut == "half":
                    with b.at(side * w / 2, -0.03, 0, rz=-side * aj):
                        _leaf(b, *((-w / 2, 0) if side < 0 else (0, w / 2)), hs, col)
                    with b.at(-side * w / 2, -0.035, 0, rz=-side * rng.uniform(2, 7)):
                        _leaf(b, *((0, w / 2) if side > 0 else (-w / 2, 0)), hs, col)
                elif shut == "closed":
                    with b.at(-side * w / 2, -0.035, 0, rz=-side * rng.uniform(1, 5)):
                        _leaf(b, *((0, w) if side > 0 else (-w, 0)), hs, col)

    s.add(deco)
    return op


def slit(s, pos, z, w=0.16, h=0.75, depth=None):
    """A ventilation slit (byres, barns): a narrow dark opening."""
    return _cut(s, s.U(pos), z, w, h, depth=depth, pane="paint", pane_col="#1d1b1c")


def door(s, pos, w=0.95, h=1.9, z=0.0, col="navy", lintel="slab", step=True, half=False, lamp=False, depth=None, jambs=True, double=False,
         latch=True, dark="#1f1c1c", steps=0, arch=0.0):
    """A low plank door in a thick wall. half=True is a stable door with its top leaf folded back outside;
    double=True two leaves (barn); lintel = 'slab', 'timber' or None; steps = stone steps up to a raised sill."""
    b = s.b
    u = s.U(pos)
    op = _cut(s, u, z, w, h, depth=depth, pane="planks" if not half else "paint", pane_col=col if not half else dark, arch=arch)
    d = op["d"]
    rng = b.rng
    lc = shade(mix(s.col if s.mat == "masonry" else C("grey"), "stone", 0.35), rng.uniform(1.0, 1.12))
    aj = rng.uniform(6, 16)

    def deco():
        with s.onu(u, z):
            leaf_y = d - 0.012
            if half:
                hb = h * 0.52
                b.box(w - 0.02, 0.05, hb, "planks", col=col, x=0, y=d * 0.55, z=0.0, lod=0, bottom=False)
                with b.detail(2):
                    beam(b, (-w / 2 + 0.03, d * 0.55 - 0.035, hb * 0.5), (w / 2 - 0.03, d * 0.55 - 0.035, hb * 0.5), w=0.02, h=0.08, mat="planks", col=shade(col, 0.76), up=(0, 0, 1), caps=False)
                with b.at(-w / 2, -0.03, hb + 0.02, rz=aj):
                    _leaf(b, -w, 0, h - hb - 0.04, col)
            else:
                with b.detail(2):
                    for zz in (h * 0.2, h * 0.78):
                        beam(b, (-w / 2 + 0.03, leaf_y, zz), ((w / 2 - 0.22) if not double else -0.06, leaf_y, zz), w=0.02, h=0.07, mat="metal", col="iron", up=(0, 0, 1), caps=False)
                        if double:
                            beam(b, (w / 2 - 0.03, leaf_y, zz), (0.06, leaf_y, zz), w=0.02, h=0.07, mat="metal", col="iron", up=(0, 0, 1), caps=False)
                    if double:
                        beam(b, (0, leaf_y, 0.02), (0, leaf_y, h), w=0.035, h=0.02, mat="planks", col=shade(col, 0.6), up=(0, 1, 0), caps=False)
                    if latch:
                        kx = w / 2 - 0.15 if not double else 0.1
                        b.box(0.06, 0.04, 0.12, "metal", col="iron", x=kx, y=leaf_y - 0.02, z=h * 0.47, bottom=True)
            if arch > 1e-4:
                with b.detail(2):
                    nv = 7
                    for i in range(nv):
                        a = math.pi * (i + 0.5) / nv
                        x, zz = -(w / 2 + 0.13) * math.cos(a), (h - arch) + (arch + 0.13) * math.sin(a)
                        with b.at(x, -0.03, zz, ry=-(90 - math.degrees(a))):
                            with b.at(rx=90):
                                b.stone(0.26, 0.32, 0.08, mat="masonry", col=shade(lc, rng.uniform(0.94, 1.06)), jitter=0.07)
            elif lintel == "slab":
                with b.at(0, 0.03, h + 0.17):
                    with b.at(rx=90):
                        b.stone(w + 0.62, 0.34, 0.11, mat="masonry", col=lc, lod=1, jitter=0.07, ch=0.16)
            elif lintel == "timber":
                beam(b, (-w / 2 - 0.28, -0.02, h + 0.11), (w / 2 + 0.28, -0.02, h + 0.11), w=0.12, h=0.22, mat="timber", col="darkoak", lod=1, up=(0, 0, 1))
            if jambs:
                with b.detail(2):
                    hj = h - arch
                    n = max(3, int(hj / 0.5))
                    for i in range(n):
                        for sgn in (-1, 1):
                            ww = 0.4 if (i + (sgn > 0)) % 2 == 0 else 0.26
                            with b.at(sgn * (w / 2 + ww / 2 - 0.01), 0.03, hj * (i + 0.5) / n):
                                with b.at(rx=90):
                                    b.stone(ww, hj / n * 0.93, 0.085, mat="masonry", col=shade(lc, rng.uniform(0.92, 1.05)), jitter=0.08)
            if step:
                with b.detail(1):
                    b.box(w + 0.5, 0.55, 0.1, "flagstone", col="grey", x=0, y=-0.2, z=-0.1 if z > 0.09 else -0.06)
            if steps:
                with b.detail(1):
                    for i in range(steps):
                        k = steps - i
                        b.box(w + 0.5 + 0.1 * k, 0.3 * k + 0.1, z / steps + 0.0, "flagstone", col=shade("grey", rng.uniform(0.92, 1.05)), x=0, y=-(0.3 * k + 0.1) / 2 + 0.05,
                              z=-(z / steps) * (i + 1))
            if lamp:
                P.lantern_at(b, w / 2 + 0.42, -0.02, h * 0.84)

    s.add(deco)
    return op


# ---------------------------------------------------------------------------------------- chimneys
def chimney(b, x, y, z, h, w=0.8, d=0.62, mat="masonry", col="grey", cap="slab", taper=0.86, smoke=True, pots=1, strength=1.0, along="x"):
    """A stout, battered stack rising h from z (start it below the roof so it passes through).
    cap = 'slab' (a wind slab raised on four stones), 'pots' (squat pots) or 'plain'."""
    with b.at(x, y, z):
        b.box(w, d, h, mat, col=col, taper=taper, lod=0)
        k = lerp(1.0, taper, 0.74)
        b.box(w * k + 0.14, d * k + 0.14, 0.1, "flagstone", col=shade("grey", 0.98), z=h * 0.74, lod=1, bottom=True)
        tw_, td_ = w * taper, d * taper
        b.box(tw_ + 0.18, td_ + 0.18, 0.09, "flagstone", col=shade("grey", 1.04), z=h, lod=1, bottom=True)
        top = h + 0.09
        if cap == "slab":
            with b.detail(2):
                for sx in (-1, 1):
                    for sy in (-1, 1):
                        b.stone(0.15, 0.15, 0.17, mat="masonry", col=col, x=sx * (tw_ / 2 - 0.07), y=sy * (td_ / 2 - 0.07), z=top)
            b.box(tw_ + 0.1, td_ + 0.1, 0.07, "flagstone", col=shade("grey", 0.9), z=top + 0.17, lod=1, bottom=True)
            top += 0.1
        elif cap == "pots":
            with b.detail(1):
                for i in range(pots):
                    px = (i - (pots - 1) / 2) * 0.36
                    with b.at(px if along == "x" else 0, 0 if along == "x" else px, top):
                        b.revolve([(0.14, 0.0), (0.12, 0.26), (0.14, 0.3), (0.1, 0.33)], "paint", col="#b7694a", seg=8)
            top += 0.33
        if smoke:
            b.smoke(0, 0, top + 0.35, strength=strength)


# ---------------------------------------------------------------------------------------- things on roofs
def weights(rf, rows=(0.35,), every=0.85, size=(0.26, 0.42), verges=True, faces=None, lod=2, col="grey", ridge=False):
    """Stones lying on the slates to hold them in a gale: rows near the eaves (distances up the slope from the wall
    line) and up the verges."""
    b = rf.b
    rng = b.rng
    for face in (faces or rf.faces):
        with rf.on(face):
            half = rf.length / 2 + min(rf.verge, 0.0) - 0.22
            for yy in rows:
                n = max(2, int(2 * half / every))
                for i in range(n + 1):
                    xx = -half + 2 * half * i / n + rng.uniform(-0.12, 0.12)
                    w = rng.uniform(*size)
                    with b.at(xx, yy + rng.uniform(-0.08, 0.08), rf.lip, rz=rng.uniform(-25, 25)):
                        b.stone(w, w * rng.uniform(0.6, 0.85), rng.uniform(0.09, 0.15), mat="masonry", col=shade(col, rng.uniform(0.9, 1.12)), lod=lod, ch=0.3, jitter=0.2)
            if verges:
                m = max(1, int((rf.L - 0.9) / 0.95))
                for sx in (-1, 1):
                    for i in range(m):
                        yy = 0.95 + (rf.L - 1.3) * (i + 0.5) / m
                        w = rng.uniform(*size)
                        with b.at(sx * (half + 0.02), yy, rf.lip, rz=rng.uniform(-20, 20)):
                            b.stone(w * 0.8, w, rng.uniform(0.09, 0.14), mat="masonry", col=shade(col, rng.uniform(0.9, 1.12)), lod=lod, ch=0.3, jitter=0.2)
            if ridge:
                n = max(2, int(2 * half / 1.1))
                for i in range(n + 1):
                    xx = -half + 2 * half * i / n + rng.uniform(-0.15, 0.15)
                    w = rng.uniform(*size)
                    with b.at(xx, rf.L - 0.28, rf.lip, rz=rng.uniform(-20, 20)):
                        b.stone(w, w * 0.7, 0.12, mat="masonry", col=shade(col, rng.uniform(0.9, 1.12)), lod=lod, ch=0.3, jitter=0.2)


def ropes(rf, every=0.95, rows=(0.45,), drop=0.42, faces=None, col=ROPE, lod=2, stone_col="grey", inset=0.3):
    """Ropes over the roof from eave to ridge, each ending in a stone that hangs below the eave, and ropes along
    the slope (`rows` = fractions of the slope's length) tying them together."""
    b = rf.b
    rng = b.rng
    p = rad(rf.pitch)
    half = rf.length / 2 + rf.verge - inset
    n = max(2, round(2 * half / every))
    for face in (faces or rf.faces):
        with rf.on(face):
            for i in range(n + 1):
                xx = -half + 2 * half * i / n
                y0 = -rf.Le - 0.02
                with b.detail(lod):
                    beam(b, (xx, y0, rf.lip + 0.03), (xx, rf.L + 0.03, rf.lip + 0.03), w=0.05, h=0.04, mat="cloth", col=col, up=(0, 0, 1), caps=False)
                    dr = drop * rng.uniform(0.75, 1.2)
                    q0 = (xx, y0, rf.lip + 0.03)
                    q1 = (xx, y0 - math.sin(p) * dr, rf.lip + 0.03 - math.cos(p) * dr)
                    beam(b, q0, q1, w=0.04, h=0.04, mat="cloth", col=col, caps=False)
                    with b.at(*q1):
                        with b.at(rx=-rf.pitch):
                            b.stone(rng.uniform(0.17, 0.24), rng.uniform(0.15, 0.2), rng.uniform(0.2, 0.28), mat="masonry", col=shade(stone_col, rng.uniform(0.88, 1.1)),
                                    lod=lod, z=-0.24, ch=0.3, jitter=0.22, bottom=True)
            with b.detail(lod):
                for f in rows:
                    beam(b, (-half - 0.12, rf.L * f, rf.lip + 0.05), (half + 0.12, rf.L * f, rf.lip + 0.05), w=0.045, h=0.04, mat="cloth", col=col, up=(0, 0, 1), caps=False)


def tuft(b, r=0.12, h=0.24, col="#8fb556", wind=0.5, n=4):
    """One tuft of grass at the origin: a little spike that bends from its root in the wind."""
    base = [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), -0.03) for k in range(n)]
    for k in range(n):
        b.face([base[k], base[(k + 1) % n], (0.0, 0.0, h)], "ivy", col=shade(col, 0.82 + 0.1 * (k % 2)), wind=(0.0, 0.0, wind))


def tufts(rf, n=26, faces=None, flowers=0.25, col="#8fb556", lod=2, ridge=True, zone=(0.05, 0.95)):
    """Grass tufts (and a few flowers) growing on a turf roof."""
    b = rf.b
    rng = b.rng
    for face in (faces or rf.faces):
        with rf.on(face):
            half = rf.length / 2 + rf.verge - 0.15
            with b.detail(lod):
                for _ in range(n):
                    xx, yy = rng.uniform(-half, half), rng.uniform(rf.L * zone[0] - rf.Le * 0.6, rf.L * zone[1])
                    hgt = rng.uniform(0.16, 0.3)
                    with b.at(xx, yy, rf.lip, rx=-rf.pitch * 0.7):
                        tuft(b, rng.uniform(0.09, 0.15), hgt, shade(col, rng.uniform(0.85, 1.2)))
                        if rng.random() < flowers:
                            b.blob(0.05, 0.05, 0.045, mat="paint", col=rng.choice(["#f4f1e4", "#f5c842", HEATHER, "#f2a0bd"]), x=rng.uniform(-0.1, 0.1), y=rng.uniform(-0.1, 0.1), z=hgt * 0.5,
                                   seg=4, rings=2, wind=0.2, rough=0.1)
            if ridge:
                with b.detail(1):
                    m = max(2, int(2 * half / 0.9))
                    for i in range(m):
                        xx = -half + 2 * half * (i + rng.uniform(0.2, 0.8)) / m
                        b.blob(rng.uniform(0.22, 0.34), 0.2, 0.14, mat="ivy", col=shade(col, rng.uniform(0.9, 1.15)), x=xx, y=rf.L - 0.1, z=rf.lip + 0.08, seg=5, rings=2, wind=0.35, rough=0.3)


def eave_logs(rf, r=0.085, col="greyoak", faces=None, pegs=True):
    """The logs that hold the turf at the eaves of a turf roof, with their wooden hooks."""
    b = rf.b
    for face in (faces or rf.faces):
        with rf.on(face):
            half = rf.length / 2 + rf.verge
            yy = -rf.Le + 0.05
            b.tube((-half - 0.04, yy, rf.lip + r * 0.9), (half + 0.04, yy, rf.lip + r * 0.9), r=r, mat="timber", col=col, lod=1, n=6, caps=True)
            if pegs:
                with b.detail(2):
                    n = max(2, int(2 * half / 1.3))
                    for i in range(n + 1):
                        xx = -half + 0.2 + (2 * half - 0.4) * i / n
                        beam(b, (xx, yy - r - 0.03, rf.lip - 0.1), (xx, yy - r - 0.03, rf.lip + r * 2 + 0.05), w=0.06, mat="timber", col=col, caps=True)
                        beam(b, (xx, yy - r - 0.03, rf.lip - 0.02), (xx, yy + 0.3, rf.lip - 0.02), w=0.06, mat="timber", col=col, caps=False)


# ---------------------------------------------------------------------------------------- rounded roofs (thatch, turf)
class Mound:
    """A rounded roof made by mound_roof: remembers its shape so ropes and tufts can follow it."""

    def __init__(self, b, x, y, z, loop, targets, h, bulge, sag, hw, lip):
        self.b, self.x, self.y, self.z, self.loop, self.targets, self.h, self.bulge, self.sag, self.hw, self.lip = b, x, y, z, loop, targets, h, bulge, sag, hw, lip
        self.n = len(loop)

    def at(self, s, f, lift=0.0):
        """The point at perimeter position s (0 .. n, fractions allowed) and height fraction f (0 eave .. 1 ridge),
        `lift` off the surface. In the mound's own frame (use inside `with m.frame():`)."""
        i = int(math.floor(s)) % self.n
        t = s - math.floor(s)
        k = (i + 1) % self.n
        p = (lerp(self.loop[i][0], self.loop[k][0], t), lerp(self.loop[i][1], self.loop[k][1], t))
        q = (lerp(self.targets[i][0], self.targets[k][0], t), lerp(self.targets[i][1], self.targets[k][1], t))
        D = math.hypot(p[0] - q[0], p[1] - q[1]) or 1e-6
        hh = self.h - self.sag * (1 - (q[0] / self.hw) ** 2)
        zz = hh * (1 - (1 - f) ** self.bulge)
        slope = hh * self.bulge * (1 - f) ** (self.bulge - 1) / D
        ox, oy = (p[0] - q[0]) / D, (p[1] - q[1]) / D
        nl = math.sqrt(slope * slope + 1)
        return (p[0] + (q[0] - p[0]) * f + ox * slope / nl * lift, p[1] + (q[1] - p[1]) * f + oy * slope / nl * lift, zz + lift / nl)

    @contextmanager
    def frame(self):
        with self.b.at(self.x, self.y, self.z):
            yield self.b


def mound_roof(b, w, d, h, rc=None, mat="thatch", col=None, x=0.0, y=0.0, z=0.0, ridge=None, thick=0.26, courses=4, lip=0.05, bulge=1.9, soffit=0.5,
               corner=3, lod=0, sag=0.0, span_max=1.7, soffit_col="darkoak"):
    """A rounded roof (thatch or turf) over a round-cornered eave line w (x) by d (y), corner radius rc, rising h
    above z to a ridge along x (`ridge` = its length; default: as long as a stadium's). Its eave is `thick` deep.
    w must be >= d (turn the frame for a ridge along y). Returns a Mound."""
    col = C(col)
    hw, hd = w / 2, d / 2
    rc = min(hw, hd) if rc is None else min(rc, hw, hd)
    rl = max((hw - hd) if ridge is None else ridge / 2, 0.0)
    loop = []

    def straight(p, q):
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        if L < 1e-6:
            return
        n = max(1, math.ceil(L / span_max))
        for k in range(n):
            loop.append((lerp(p[0], q[0], k / n), lerp(p[1], q[1], k / n)))

    def arc(cx, cy, a0):
        for k in range(corner):
            a = rad(a0 + 90.0 * k / corner)
            loop.append((cx + rc * math.cos(a), cy + rc * math.sin(a)))

    straight((-(hw - rc), -hd), (hw - rc, -hd)); arc(hw - rc, -(hd - rc), -90)
    straight((hw, -(hd - rc)), (hw, hd - rc)); arc(hw - rc, hd - rc, 0)
    straight((hw - rc, hd), (-(hw - rc), hd)); arc(-(hw - rc), hd - rc, 90)
    straight((-hw, hd - rc), (-hw, -(hd - rc))); arc(-(hw - rc), -(hd - rc), 180)
    targets = [(min(max(p[0], -rl), rl), 0.0) for p in loop]
    m = Mound(b, x, y, z, loop, targets, h, bulge, sag, hw, lip)
    n = len(loop)
    rng = b.rng
    with b.at(x, y, z):
        # the eave: its underside and its cut butt end
        inner = []
        for i in range(n):
            p, q = loop[i], targets[i]
            D = math.hypot(p[0] - q[0], p[1] - q[1]) or 1e-6
            f = min(soffit / D, 0.7)
            inner.append((p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f, -thick))
        bottom = [(p[0], p[1], -thick) for p in loop]
        top0 = [m.at(i, 0.0, lip) for i in range(n)]
        skin(b, [inner, bottom], "planks", col=soffit_col, lod=lod, smooth=False)
        skin(b, [bottom, top0], mat, col=shade(col, 0.8), lod=lod, smooth=True)
        rings, cols = [top0], []
        for k in range(courses):
            f1 = (k + 1) / courses
            rings.append([m.at(i, f1, 0.0) for i in range(n)])
            cols.append(shade(col, rng.uniform(0.9, 1.08)))
            if k + 1 < courses:
                rings.append([m.at(i, f1, lip) for i in range(n)])
                cols.append(cols[-1])
        skin(b, rings, mat, cols=cols, lod=lod, smooth=True)
    return m


def mound_ropes(m, every=0.95, rows=(0.34, 0.66), drop=0.4, col=ROPE, lod=2, stone_col="grey", steps=4, rest=None):
    """Rope a rounded thatch down: ropes from the eave over to the ridge, each with a hanging stone, tied
    together by ropes running round the roof at the given height fractions."""
    b = m.b
    rng = b.rng
    with m.frame():
        with b.detail(lod):
            for i in range(m.n):
                k = (i + 1) % m.n
                L = math.hypot(m.loop[k][0] - m.loop[i][0], m.loop[k][1] - m.loop[i][1])
                nn = max(1, round(L / every))
                for j in range(nn):
                    s = i + j / nn
                    pts = [m.at(s, f / steps, 0.045) for f in range(steps + 1)]
                    for a, c in zip(pts, pts[1:]):
                        beam(b, a, c, w=0.05, h=0.04, mat="cloth", col=col, caps=False)
                    e = m.at(s, 0.0, 0.05)
                    if rest is not None:        # the rope runs out to an anchor stone lying on the wall-head (at height `rest`)
                        e2 = m.at(s, 0.12, 0.0)
                        dx, dy = e[0] - e2[0], e[1] - e2[1]
                        dl = math.hypot(dx, dy) or 1.0
                        q = (e[0] + dx / dl * rng.uniform(0.2, 0.34), e[1] + dy / dl * rng.uniform(0.2, 0.34), rest)
                        beam(b, e, (q[0], q[1], rest + 0.12), w=0.04, mat="cloth", col=col, caps=False)
                        b.stone(rng.uniform(0.24, 0.34), rng.uniform(0.2, 0.28), rng.uniform(0.16, 0.24), mat="masonry", col=shade(stone_col, rng.uniform(0.9, 1.15)), lod=lod,
                                x=q[0], y=q[1], z=rest, ch=0.3, jitter=0.22)
                        continue
                    dr = drop * rng.uniform(0.7, 1.2)
                    beam(b, e, (e[0], e[1], e[2] - dr), w=0.04, mat="cloth", col=col, caps=False)
                    b.stone(rng.uniform(0.17, 0.24), rng.uniform(0.15, 0.2), rng.uniform(0.2, 0.28), mat="masonry", col=shade(stone_col, rng.uniform(0.88, 1.1)), lod=lod,
                            x=e[0], y=e[1], z=e[2] - dr - 0.22, ch=0.3, jitter=0.22, bottom=True)
            for f in rows:
                for i in range(m.n):
                    beam(b, m.at(i, f, 0.06), m.at(i + 1, f, 0.06), w=0.045, h=0.04, mat="cloth", col=col, caps=False)


def mound_tufts(m, n=40, flowers=0.2, col="#8fb556", lod=2, fmin=0.05, fmax=1.0):
    """Grass and flowers on a turf mound."""
    b = m.b
    rng = b.rng
    with m.frame():
        with b.detail(lod):
            for _ in range(n):
                p = m.at(rng.uniform(0, m.n), rng.uniform(fmin, fmax), 0.0)
                hgt = rng.uniform(0.16, 0.32)
                with b.at(*p):
                    tuft(b, rng.uniform(0.09, 0.15), hgt, shade(col, rng.uniform(0.85, 1.2)))
                    if rng.random() < flowers:
                        b.blob(0.05, 0.05, 0.045, mat="paint", col=rng.choice(["#f4f1e4", "#f5c842", HEATHER, "#f2a0bd"]), x=rng.uniform(-0.1, 0.1), y=rng.uniform(-0.1, 0.1), z=hgt * 0.5,
                               seg=4, rings=2, wind=0.2, rough=0.1)


def wallhead(body, width=0.6, mat="thatch", col=TURF, lod=0, z=0.0, tufts=0):
    """The flat top of a thick wall (a blackhouse's turfed wall-head), from its outer edge `width` inward."""
    b = body.b
    hw, hd = body.tw / 2, body.td / 2
    iw, idp = hw - width, hd - width
    rng = b.rng
    with b.at(body.x, body.y, body.top + z):
        O = [(-hw, -hd, 0), (hw, -hd, 0), (hw, hd, 0), (-hw, hd, 0)]
        I = [(-iw, -idp, 0.04), (iw, -idp, 0.04), (iw, idp, 0.04), (-iw, idp, 0.04)]
        for i in range(4):
            j = (i + 1) % 4
            b.face([O[i], O[j], I[j], I[i]], mat, col=col, lod=lod)
        with b.detail(2):
            for _ in range(tufts):
                side = rng.randrange(4)
                t = rng.random()
                p = vlerp(vlerp(O[side], O[(side + 1) % 4], t), vlerp(I[side], I[(side + 1) % 4], t), rng.uniform(0.2, 0.8))
                with b.at(*p):
                    tuft(b, rng.uniform(0.09, 0.14), rng.uniform(0.16, 0.28), shade("#8fb556", rng.uniform(0.85, 1.2)))


# ---------------------------------------------------------------------------------------- boats
def _hull_section(s, beam, depth, strakes, sheer=1.0):
    if s < 0.42:
        hb = 1 - 0.34 * ((0.42 - s) / 0.42) ** 2
    else:
        hb = max(1 - ((s - 0.42) / 0.58) ** 2.2, 0.0) ** 0.7
    hb *= beam / 2
    zs = depth * (1 + sheer * (0.22 * (2 * s - 1) ** 2 + 0.32 * max(s - 0.5, 0.0)))
    zk = depth * 0.5 * max((s - 0.78) / 0.22, 0.0) ** 2 + depth * 0.06 * (2 * s - 1) ** 2
    pts = []
    for j in range(strakes + 1):
        q = j / strakes
        pts.append((hb * math.sin(q * math.pi / 2) ** 0.75, zk + (zs - zk) * (1 - math.cos(q * math.pi / 2)) ** 0.85))
    return pts


def hull(b, L=4.2, width=1.5, depth=0.6, n=7, strakes=4, col="#8a6f55", incol=None, inside=True, s0=0.0, s1=1.0, keel=True, rail=None, ribs=0, thwarts=(),
         lod=1, cap0=True, cap1=False, mat="planks", sheer=1.0):
    """A clinker boat lying along +y: stern at y = L*s0 (a flat transom when s0 = 0), bow at y = L. z = 0 is the keel
    amidships; the gunwale is about `depth` up. Build stations s0 .. s1 only for a boat cut in half.
    Turn it over with `with b.at(..., ry=180)`. rail = colour of the gunwale strake."""
    col = C(col)
    incol = shade(col, 0.72) if incol is None else C(incol)
    S = [s0 + (s1 - s0) * i / n for i in range(n + 1)]
    secs = [_hull_section(s, width, depth, strakes, sheer) for s in S]
    ys = [L * s for s in S]
    R = lambda i, j: (secs[i][j][0], ys[i], secs[i][j][1])
    Lf = lambda i, j: (-secs[i][j][0], ys[i], secs[i][j][1])
    th = 0.035
    Ri = lambda i, j: (max(secs[i][j][0] - th * (0.3 + 0.7 * j / strakes), 0.0), ys[i], secs[i][j][1] + th * (1 - j / strakes))
    Li = lambda i, j: (-Ri(i, j)[0], ys[i], Ri(i, j)[2])
    with b.detail(lod):
        for a in range(n):
            for j in range(strakes):
                c = shade(col, 0.92 + 0.14 * ((j + 1) % 2)) if not (rail is not None and j == strakes - 1) else C(rail)
                qr = [R(a, j), R(a + 1, j), R(a + 1, j + 1), R(a, j + 1)]
                ql = [Lf(a, j + 1), Lf(a + 1, j + 1), Lf(a + 1, j), Lf(a, j)]
                b.face(qr, mat, col=c)
                b.face(ql, mat, col=c)
                if inside and min(secs[a][-1][0], secs[a + 1][-1][0]) > 4 * th:
                    b.face([Ri(a, j + 1), Ri(a + 1, j + 1), Ri(a + 1, j), Ri(a, j)], mat, col=incol)
                    b.face([Li(a, j), Li(a + 1, j), Li(a + 1, j + 1), Li(a, j + 1)], mat, col=incol)
                elif inside:                    # toward the stem the two skins would cross: one skin, seen from both sides
                    b.face(list(reversed(qr)), mat, col=incol)
                    b.face(list(reversed(ql)), mat, col=incol)
        for end, i, on in ((0, 0, cap0), (1, n, cap1)):
            if not on or secs[i][-1][0] < 1e-4:
                continue
            poly = [R(i, j) for j in range(strakes + 1)] + [Lf(i, j) for j in range(strakes, 0, -1)]
            b.face(poly if end == 0 else list(reversed(poly)), mat, col=shade(col, 0.95))
            if inside:
                pin = [(q[0], q[1] + (th if end == 0 else -th), q[2]) for q in poly]
                b.face(list(reversed(pin)) if end == 0 else pin, mat, col=incol)
        if keel:
            for a in range(n):
                beam(b, (0, ys[a], secs[a][0][1] - 0.02), (0, ys[a + 1], secs[a + 1][0][1] - 0.02), w=0.07, h=0.11, mat="timber", col=shade(col, 0.7), caps=(a in (0, n - 1)))
            if s1 > 0.999:
                beam(b, (0, ys[n] + 0.02, secs[n][0][1] - 0.05), (0, ys[n] + 0.05, secs[n][-1][1] + 0.12), w=0.07, h=0.1, mat="timber", col=shade(col, 0.7), up=(0, 1, 0))
    with b.detail(2):
        for k in range(ribs):
            a = round((k + 0.5) * n / ribs)
            a = min(max(a, 0), n)
            cz = secs[a][-1][1]
            for sgn in (-1, 1):
                pts = [(sgn * p[0] * 0.95, ys[a], p[1] + (cz - p[1]) * 0.05) for p in secs[a]]
                for p0, p1 in zip(pts, pts[1:]):
                    beam(b, p0, p1, w=0.05, h=0.05, mat="timber", col=shade(incol, 0.8), caps=False)
        for sq in thwarts:
            a = min(max(round((sq - s0) / (s1 - s0) * n), 0), n)
            zt = secs[a][0][1] + (secs[a][-1][1] - secs[a][0][1]) * 0.62
            xw = secs[a][-1][0] * 0.9
            b.box(2 * xw, 0.22, 0.04, "planks", col="greyoak", x=0, y=ys[a], z=zt, bottom=True)


# ---------------------------------------------------------------------------------------- yard walls
def drystone(b, pts, h=1.0, t=0.5, col="grey", cope=True, lod=0, skirt=1.2, piece=1.25):
    """A drystone wall along a line of points [(x, y), ...] on the ground: battered, of uneven height, topped
    with stones set on edge."""
    rng = b.rng
    for i in range(len(pts) - 1):
        a, c = pts[i], pts[i + 1]
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        if L < 0.05:
            continue
        with b.at(a[0], a[1], 0, rz=math.degrees(math.atan2(c[1] - a[1], c[0] - a[0]))):
            n = max(1, round(L / piece))
            for k in range(n):
                x0, x1 = L * k / n, L * (k + 1) / n
                hh = h * rng.uniform(0.93, 1.06)
                b.box(x1 - x0 + 0.02, t, hh, "masonry", col=shade(col, rng.uniform(0.9, 1.06)), x=(x0 + x1) / 2, y=0, z=0, tx=1.0, ty=0.7, lod=lod)
                if cope:
                    with b.detail(2):
                        m = max(2, int((x1 - x0) / 0.3))
                        for j in range(m):
                            xx = x0 + (x1 - x0) * (j + 0.5) / m
                            with b.at(xx, rng.uniform(-0.03, 0.03), hh - 0.03, ry=rng.uniform(-16, 16), rz=rng.uniform(-8, 8)):
                                b.box(rng.uniform(0.1, 0.17), t * 0.76, rng.uniform(0.2, 0.32), "masonry", col=shade(col, rng.uniform(0.86, 1.12)), taper=0.85)
            b.box(L, t, skirt, "masonry", col=shade(col, 0.8), x=L / 2, y=0, z=-skirt, top=False, lod=lod, sides="fb")


def gatepost(b, x, y, h=1.3, col="grey"):
    b.stone(0.3, 0.28, h, mat="masonry", col=shade(col, 1.08), lod=1, x=x, y=y, z=0, ch=0.1, jitter=0.1)


def gate(b, p0, p1, h=1.0, col="greyoak", bars=4, ajar=0.0):
    """A timber field gate hung at p0 and closing on p1 (ajar = degrees it stands open)."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    with b.at(p0[0], p0[1], 0, rz=math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0])) + ajar):
        with b.detail(1):
            for x in (0.05, L - 0.05):
                beam(b, (x, 0, 0.06), (x, 0, h + 0.08), w=0.08, mat="timber", col=col)
            beam(b, (0.05, 0, h), (L - 0.05, 0, h), w=0.05, h=0.08, mat="timber", col=col, up=(0, 0, 1), caps=False)
            beam(b, (0.05, 0, 0.16), (L - 0.05, 0, 0.16), w=0.05, h=0.08, mat="timber", col=col, up=(0, 0, 1), caps=False)
        with b.detail(2):
            for i in range(1, bars - 1):
                zz = 0.16 + (h - 0.16) * i / (bars - 1)
                beam(b, (0.05, 0, zz), (L - 0.05, 0, zz), w=0.04, h=0.07, mat="timber", col=col, up=(0, 0, 1), caps=False)
            beam(b, (0.07, 0, 0.18), (L - 0.07, 0, h - 0.03), w=0.04, h=0.07, mat="timber", col=col, up=(0, 1, 0), caps=False)


# ---------------------------------------------------------------------------------------- timber towers
def trestle(b, base, top, z0, z1, tiers=3, leg=0.2, col="darkoak", brace=0.1, girt=0.13, x=0.0, y=0.0, round_legs=False, cross="x", lod_brace=1,
            lod_girt=0, skip_brace=(), foot=None, foot_col="grey"):
    """An open timber tower: four raking legs from a rectangle `base` = (half x, half y) at z0 to `top` at z1,
    tied by girts at each tier and braced with crosses ('x') or single diagonals ('z') on every side.
    skip_brace = set of (side, tier) to leave open, sides 0 front, 1 right, 2 back, 3 left.
    foot = (size, height): a stone pad (with its hidden foundation) under each leg. Returns the tier heights."""
    bx, by = base if isinstance(base, (tuple, list)) else (base, base)
    tx, ty = top if isinstance(top, (tuple, list)) else (top, top)
    cs = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    P0 = lambda c, t: (x + c[0] * lerp(bx, tx, t), y + c[1] * lerp(by, ty, t), lerp(z0, z1, t))
    zs = [k / tiers for k in range(tiers + 1)]
    for c in cs:
        a, e = P0(c, 0.0), P0(c, 1.0)
        if round_legs:
            b.tube(a, e, r=leg / 2, r1=leg * 0.4, mat="timber", col=col, lod=0, n=6, caps=True)
        else:
            beam(b, a, e, w=leg, h=leg, mat="timber", col=col, lod=0, up=(-c[0], -c[1], 0))
        if foot:
            fs, fh = foot
            b.box(fs, fs, fh, "masonry", col=foot_col, x=a[0], y=a[1], z=z0 - fh + 0.04, lod=0, taper=0.88)
            b.box(fs, fs, 3.0, "masonry", col=shade(foot_col, 0.85), x=a[0], y=a[1], z=z0 - fh + 0.04 - 3.0, top=False, lod=0)
    for k in range(1, tiers + 1):
        for s in range(4):
            a, e = P0(cs[s], zs[k]), P0(cs[(s + 1) % 4], zs[k])
            beam(b, a, e, w=girt, h=girt, mat="timber", col=col, lod=lod_girt, caps=False)
    for k in range(tiers):
        for s in range(4):
            if (s, k) in skip_brace:
                continue
            a0, e0 = P0(cs[s], zs[k]), P0(cs[(s + 1) % 4], zs[k])
            a1, e1 = P0(cs[s], zs[k + 1]), P0(cs[(s + 1) % 4], zs[k + 1])
            nrm = (cs[s][0] + cs[(s + 1) % 4][0], cs[s][1] + cs[(s + 1) % 4][1], 0)
            if cross == "x" or (k + s) % 2 == 0:
                beam(b, a0, e1, w=brace, h=brace * 0.7, mat="timber", col=col, lod=lod_brace, up=nrm, caps=False)
            if cross == "x" or (k + s) % 2 == 1:
                beam(b, e0, a1, w=brace, h=brace * 0.7, mat="timber", col=col, lod=lod_brace, up=nrm, caps=False)
    return [lerp(z0, z1, t) for t in zs]


def deck(b, w, d, z, x=0.0, y=0.0, thick=0.09, col="greyoak", joists=0.75, jcol="darkoak", lod=0, hatch=None, edge=True):
    """A plank stage w by d with its top at z, on joists. hatch = (x, y, w, d) draws a trapdoor."""
    with b.at(x, y, z):
        b.box(w, d, thick, "planks", col=col, z=-thick, bottom=True, top=False, lod=lod)
        nx, ny = max(1, round(w / 0.9)), max(1, round(d / 0.9))
        uo, vo = b.uvo()
        for i in range(nx):
            for j in range(ny):
                xa, xb, ya, yb = -w / 2 + w * i / nx, -w / 2 + w * (i + 1) / nx, -d / 2 + d * j / ny, -d / 2 + d * (j + 1) / ny
                b.quad((xa, ya, 0), (xb, ya, 0), (xb, yb, 0), (xa, yb, 0), "planks", col=col, lod=lod, uv=[(uo + xa, vo + ya), (uo + xb, vo + ya), (uo + xb, vo + yb), (uo + xa, vo + yb)])
        if joists:
            with b.detail(1):
                n = max(2, round(d / joists))
                for i in range(n + 1):
                    yy = -d / 2 + 0.08 + (d - 0.16) * i / n
                    beam(b, (-w / 2 + 0.02, yy, -thick - 0.09), (w / 2 - 0.02, yy, -thick - 0.09), w=0.1, h=0.18, mat="timber", col=jcol, up=(0, 0, 1))
        if edge:
            with b.detail(1):
                for sx in (-1, 1):
                    beam(b, (sx * (w / 2 - 0.05), -d / 2, -thick - 0.05), (sx * (w / 2 - 0.05), d / 2, -thick - 0.05), w=0.1, h=0.26, mat="timber", col=jcol, up=(0, 0, 1))
        if hatch:
            hx, hy, hw, hd = hatch
            with b.detail(2):
                b.box(hw, hd, 0.035, "planks", col=shade(col, 0.74), x=hx, y=hy, z=0.0)
                beam(b, (hx - hw / 2 + 0.06, hy - hd / 2 + 0.1, 0.045), (hx + hw / 2 - 0.06, hy - hd / 2 + 0.1, 0.045), w=0.05, h=0.02, mat="metal", col="iron", up=(0, 0, 1))
                beam(b, (hx - hw / 2 + 0.06, hy + hd / 2 - 0.1, 0.045), (hx + hw / 2 - 0.06, hy + hd / 2 - 0.1, 0.045), w=0.05, h=0.02, mat="metal", col="iron", up=(0, 0, 1))
                b.box(0.1, 0.1, 0.03, "metal", col="iron", x=hx + hw / 2 - 0.12, y=hy, z=0.035)


def rails(b, pts, h=1.0, col="darkoak", post=0.1, mid=True, closed=False, lod=1, posts_at=1.5):
    """A plain post-and-rail fence along points [(x, y, z), ...]: posts, a top rail, a middle rail."""
    Pp = list(pts) + ([pts[0]] if closed else [])
    with b.detail(lod):
        for i in range(len(Pp) - 1):
            a, c = Pp[i], Pp[i + 1]
            L = math.hypot(c[0] - a[0], c[1] - a[1])
            if L < 1e-4:
                continue
            n = max(1, round(L / posts_at))
            for k in range(n + (0 if (closed or i < len(Pp) - 2) else 1)):
                p = vlerp(a, c, k / n)
                beam(b, p, (p[0], p[1], p[2] + h + 0.05), w=post, mat="timber", col=col)
            beam(b, (a[0], a[1], a[2] + h), (c[0], c[1], c[2] + h), w=post * 0.9, h=post * 0.7, mat="timber", col=col, caps=False)
            if mid:
                beam(b, (a[0], a[1], a[2] + h * 0.5), (c[0], c[1], c[2] + h * 0.5), w=post * 0.6, h=post * 0.6, mat="timber", col=col, caps=False)


def ladder(b, p0, p1, w=0.46, col="greyoak", rung=0.3, lod=2, side=None, mat="timber", rail=0.055):
    """A ladder from p0 up to p1 (points on its centre line)."""
    a = vsub(p1, p0)
    L = vlen(a)
    s = vnorm(vcross(a, (0, 0, 1))) if side is None else vnorm(side)
    if vlen(vcross(a, (0, 0, 1))) < 1e-4 and side is None:
        s = (1, 0, 0)
    with b.detail(lod):
        for sgn in (-1, 1):
            o = vmul(s, sgn * w / 2)
            beam(b, vadd(p0, o), vadd(p1, o), w=rail, mat=mat, col=col)
        n = max(2, int(L / rung))
        for i in range(1, n):
            c = vlerp(p0, p1, i / n)
            beam(b, vadd(c, vmul(s, -w / 2)), vadd(c, vmul(s, w / 2)), w=rail * 0.65, mat=mat, col=col, caps=False)


def forestair(b, n=9, w=1.0, rise=0.2, run=0.3, landing=1.1, mat="masonry", col="grey", treads=True, skirt=3.0, niche=False, wall="+y"):
    """A solid stone outside stair: from the origin it climbs toward +x for n steps, then a landing `landing` long
    at height n*rise. It is w wide, centred on y = 0; wall = the side that stands against the building
    ('+y' or '-y': turn the frame half round and say '-y' for a stair that climbs toward -x)."""
    rng = b.rng
    sd = "f" if wall == "+y" else "b"
    oy = -1 if wall == "+y" else 1
    for i in range(n):
        b.box(run, w, rise * (i + 1), mat, col=shade(col, rng.uniform(0.94, 1.05)), x=run * (i + 0.5), y=0, z=0, lod=0, sides=sd + "l")
    top = rise * n
    b.box(landing, w, top, mat, col=col, x=run * n + landing / 2, y=0, z=0, lod=0, sides=sd + "lr")
    b.box(run * n + landing, w, skirt, mat, col=shade(col, 0.85), x=(run * n + landing) / 2, y=0, z=-skirt, top=False, lod=0)
    if treads:
        with b.detail(2):
            for i in range(n):
                b.box(run + 0.05, w + 0.06, 0.06, "flagstone", col=shade("grey", rng.uniform(0.9, 1.08)), x=run * (i + 0.5) - 0.02, y=oy * 0.02, z=rise * (i + 1) - 0.01, bottom=True)
            b.box(landing + 0.05, w + 0.06, 0.06, "flagstone", col="grey", x=run * n + landing / 2, y=oy * 0.02, z=top - 0.01, bottom=True)
    if niche:
        with b.detail(1):
            nx = run * n + landing * 0.5
            yy = oy * (w / 2 + 0.004)
            q = [(nx - 0.3, yy, 0.0), (nx + 0.3, yy, 0.0), (nx + 0.3, yy, min(0.75, top - 0.4)), (nx - 0.3, yy, min(0.75, top - 0.4))]
            b.face(q if wall == "+y" else list(reversed(q)), "paint", col="#1d1b1c")
    return top


# ---------------------------------------------------------------------------------------- the small things of the place
def peat_stack(b, x=0.0, y=0.0, w=1.8, d=0.9, h=1.1, rz=0.0, turf=True, loose=10):
    """A stack of cut peats drying against the weather: dark bricks of turf, ridged on top."""
    rng = b.rng
    with b.at(x, y, 0, rz=rz):
        b.box(w, d, h * 0.72, "cobble", col=PEAT, tx=0.93, ty=0.8, lod=1)
        b.box(w * 0.93, d * 0.8, h * 0.28, "cobble", col=shade(PEAT, 0.9), z=h * 0.72, tx=0.82, ty=0.25, lod=1)
        with b.detail(2):
            for _ in range(loose):
                px, py = rng.uniform(-w / 2, w / 2), rng.choice((-1, 1)) * rng.uniform(d / 2, d / 2 + 0.25)
                with b.at(px, py, 0, rz=rng.uniform(0, 180), rx=rng.uniform(-10, 10)):
                    b.box(0.3, 0.12, 0.09, "brick", col=shade(PEAT, rng.uniform(0.8, 1.3)), z=rng.uniform(0, 0.08))
            for i in range(int(w / 0.33)):
                with b.at(-w / 2 + 0.2 + i * 0.33, 0, h * 0.97, rz=rng.uniform(60, 120), ry=rng.uniform(-8, 8)):
                    b.box(0.3, 0.12, 0.09, "brick", col=shade(PEAT, rng.uniform(0.8, 1.3)))
            if turf:
                for i in range(2):
                    with b.at(rng.uniform(-w / 3, w / 3), 0, h + 0.04, rz=rng.uniform(-20, 20)):
                        b.box(0.5, 0.36, 0.07, "thatch", col=TURF, bottom=True)


def creel(b, x=0.0, y=0.0, z=0.0, rz=0.0, L=0.62, r=0.24, col="#a08e6c"):
    """A lobster creel: a half-barrel of netting on hoops."""
    n = 5
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            pts = [(r * math.cos(math.pi * i / n), r * math.sin(math.pi * i / n)) for i in range(n + 1)]
            for i in range(n):
                (y0, z0), (y1, z1) = pts[i], pts[i + 1]
                b.quad((L / 2, y0, z0), (-L / 2, y0, z0), (-L / 2, y1, z1), (L / 2, y1, z1), "cloth", col=col)
                for hx in (-L / 2 + 0.03, 0.0, L / 2 - 0.03):
                    k = 1.06
                    b.quad((hx + 0.025, y0 * k, z0 * k), (hx - 0.025, y0 * k, z0 * k), (hx - 0.025, y1 * k, z1 * k), (hx + 0.025, y1 * k, z1 * k), "planks", col="darkoak")
            b.face([(-L / 2, p[0], p[1]) for p in reversed(pts)], "cloth", col=shade(col, 0.8))
            b.face([(L / 2, p[0], p[1]) for p in pts], "cloth", col=shade(col, 0.8))


def floats(b, x=0.0, y=0.0, z=0.0, n=4, cols=("red", "mustard", "teal", "ivory"), r=0.11, drop=0.22):
    """A string of painted net floats hanging from a peg at (x, y, z)."""
    rng = b.rng
    with b.detail(2):
        beam(b, (x, y, z), (x, y, z - drop * (n + 0.2)), w=0.02, mat="cloth", col=ROPE, caps=False)
        for i in range(n):
            b.blob(r, r, r * 1.1, mat="paint", col=cols[(i + rng.randrange(4)) % len(cols)], x=x + rng.uniform(-0.04, 0.04), y=y - 0.03, z=z - drop * (i + 0.8), seg=5, rings=3, rough=0.05)


FISH = [(0.0, 0.0), (0.06, -0.09), (0.05, -0.27), (0.02, -0.34), (0.07, -0.44), (-0.07, -0.44), (-0.02, -0.34), (-0.05, -0.27), (-0.06, -0.09)]


def fish_rack(b, x=0.0, y=0.0, z=0.0, w=1.7, h=1.75, n=8, rz=0.0, col="greyoak", fishcol="#d9c49a"):
    """Split fish drying on a pole between two posts."""
    rng = b.rng
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            for sx in (-1, 1):
                beam(b, (sx * w / 2, 0, 0), (sx * w / 2 * 0.96, 0, h + 0.12), w=0.08, mat="timber", col=col)
            b.tube((-w / 2 - 0.12, 0, h), (w / 2 + 0.12, 0, h), r=0.03, mat="timber", col=col, n=5)
        with b.detail(2):
            for i in range(n):
                xx = -w / 2 + 0.16 + (w - 0.32) * i / max(n - 1, 1)
                with b.at(xx, 0, h - 0.03, rz=rng.uniform(-25, 25)):
                    k = rng.uniform(0.85, 1.25)
                    shape(b, [(p[0] * k, p[1] * k) for p in FISH], mat="paint", col=shade(fishcol, rng.uniform(0.85, 1.1)), lod=2, wind=lambda x, z: min(-z * 0.5, 0.3))


def oars(b, x=0.0, y=0.0, z=0.0, h=2.6, lean=0.35, col="greyoak", blade="ivory", n=2, rz=0.0, top=0.0):
    """Oars leaning against a wall (the wall is on the +y side). top = how far out from the wall their upper ends
    are (negative = out: give the eave's overhang to lean them on the eave instead of poking through it)."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            for i in range(n):
                xx = (i - (n - 1) / 2) * 0.22
                f = top - lean
                beam(b, (xx, f, 0.0), (xx + 0.05 * i, f + lean * 0.72, h * 0.72), w=0.045, mat="timber", col=col, caps=False)
                beam(b, (xx + 0.05 * i, f + lean * 0.72, h * 0.72), (xx + 0.07 * i, top, h), w=0.14, h=0.03, mat="planks", col=blade, up=(0, 1, 0))


def trough(b, x=0.0, y=0.0, z=0.0, w=1.5, d=0.6, h=0.5, rz=0.0, col="grey", water=True):
    """A stone water trough."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            b.box(w, d, h, "masonry", col=col, taper=0.94, top=False)
            t = 0.1
            ww, dd = w * 0.94, d * 0.94
            for (cx, cy, bw, bd) in ((0, -dd / 2 + t / 2, ww, t), (0, dd / 2 - t / 2, ww, t), (-ww / 2 + t / 2, 0, t, dd - 2 * t), (ww / 2 - t / 2, 0, t, dd - 2 * t)):
                b.quad((cx - bw / 2, cy - bd / 2, h), (cx + bw / 2, cy - bd / 2, h), (cx + bw / 2, cy + bd / 2, h), (cx - bw / 2, cy + bd / 2, h), "masonry", col=shade(col, 1.08))
            if water:
                b.quad((-ww / 2 + t, -dd / 2 + t, h - 0.07), (ww / 2 - t, -dd / 2 + t, h - 0.07), (ww / 2 - t, dd / 2 - t, h - 0.07), (-ww / 2 + t, dd / 2 - t, h - 0.07), "water", col="#7fb6c4")
            # inner sides down to the water
            iw, idp = ww / 2 - t, dd / 2 - t
            I = [(-iw, -idp), (iw, -idp), (iw, idp), (-iw, idp)]
            for i in range(4):
                j = (i + 1) % 4
                b.quad((I[j][0], I[j][1], h - 0.07), (I[i][0], I[i][1], h - 0.07), (I[i][0], I[i][1], h), (I[j][0], I[j][1], h), "masonry", col=shade(col, 0.7))


def churn(b, x=0.0, y=0.0, z=0.0, h=0.62, r=0.17, col="lead"):
    """A milk churn."""
    with b.at(x, y, z):
        with b.detail(2):
            b.revolve([(r, 0.0), (r, h * 0.62), (r * 0.62, h * 0.82), (r * 0.62, h * 0.95), (r * 0.78, h)], "metal", col=col, seg=8, close_top=True)


def bucket(b, x=0.0, y=0.0, z=0.0, r=0.16, h=0.3, col="#b99c78", water=False):
    with b.at(x, y, z):
        with b.detail(2):
            b.revolve([(r * 0.8, 0.0), (r, h)], "planks", col=col, seg=8)
            b.revolve([(r * 0.96, h), (r * 0.76, 0.03)], "planks", col=shade(col, 0.6), seg=8)
            b.disc(r * 0.95, "water" if water else "planks", col="#7fb6c4" if water else shade(col, 0.5), seg=8, z=h * (0.8 if water else 0.1))
            b.revolve([(r * 0.92, h * 0.25), (r * 0.95, h * 0.32)], "metal", col="iron", seg=8)


def hay(b, x=0.0, y=0.0, z=0.0, r=0.9, h=0.9, col="#e2c56f"):
    """A heap of hay."""
    with b.detail(1):
        b.blob(r, r * 0.9, h, mat="thatch", col=col, x=x, y=y, z=z + h * 0.45, seg=7, rings=3, rough=0.18, bottom=False)


def rain_barrel(b, x=0.0, y=0.0, z=0.0, r=0.36, h=0.95, col="#b99c78", lod=1):
    """An open barrel standing under a spout, full of water."""
    with b.at(x, y, z):
        with b.detail(lod):
            b.revolve([(r * 0.84, 0.0), (r, h * 0.35), (r, h * 0.65), (r * 0.86, h)], "planks", col=col, seg=10)
            b.revolve([(r * 0.86, h), (r * 0.8, h)], "planks", col=shade(col, 0.7), seg=10)
            b.revolve([(r * 0.8, h), (r * 0.9, h * 0.6)], "planks", col=shade(col, 0.55), seg=10)
            b.disc(r * 0.88, "water", col="#7fb6c4", seg=10, z=h - 0.09)
        with b.detail(2):
            for zz in (h * 0.16, h * 0.84):
                b.revolve([(r * 0.93, zz - 0.03), (r * 0.95, zz + 0.03)], "metal", col="iron", seg=10)


# ---------------------------------------------------------------------------------------- beacons, lanterns, instruments
def fire_basket(b, r=0.5, h=0.5, lamp=2.5, smoke=1.4, flames=6, fire_lod=1):
    """An iron fire basket (a cresset) with a fire burning in it; the origin is the middle of its floor."""
    rng = b.rng
    with b.detail(1):
        b.disc(r * 0.72, "metal", col="iron", seg=8, z=0.0)
        b.disc(r * 0.72, "metal", col="iron", seg=8, z=-0.04, down=True)
        for (zz, rr) in ((0.0, r * 0.72), (h * 0.52, r * 0.9), (h, r)):
            b.revolve([(rr - 0.02, zz - 0.04), (rr + 0.02, zz - 0.04), (rr + 0.02, zz + 0.04), (rr - 0.02, zz + 0.04)], "metal", col="iron", seg=8)
            b.revolve([(rr - 0.02, zz + 0.04), (rr - 0.02, zz - 0.04)], "metal", col=shade("iron", 0.7), seg=8)
        for k in range(8):
            with b.at(rz=45 * k + 22.5):
                beam(b, (0, -r * 0.72, 0.0), (0, -r, h + 0.1), w=0.035, mat="metal", col="iron", caps=False)
    with b.detail(fire_lod):
        b.revolve([(r * 0.66, 0.04), (r * 0.82, h * 0.62), (r * 0.5, h * 0.95), (0.0, h * 1.08)], "glow", col="#ff8a2e", seg=7)
        for k in range(flames):
            a = 2 * math.pi * k / flames + rng.uniform(-0.3, 0.3)
            rr = r * rng.uniform(0.0, 0.5) if k else 0.0
            cx, cy = rr * math.cos(a), rr * math.sin(a)
            fh = h * rng.uniform(1.3, 2.3) if k else h * 2.7
            fw = r * rng.uniform(0.22, 0.34)
            base = [(cx + fw * math.cos(a + 2.094 * j), cy + fw * math.sin(a + 2.094 * j), h * 0.7) for j in range(3)]
            tip = (cx + rng.uniform(-0.08, 0.08), cy + rng.uniform(-0.08, 0.08), h * 0.7 + fh)
            for j in range(3):
                b.face([base[j], base[(j + 1) % 3], tip], "glow", col="#ffcf5a" if k % 2 else "#ffb03a", wind=(0.0, 0.0, 0.9))
    if lamp:
        b.lamp(0, 0, h + 0.4, strength=lamp)
    if smoke:
        b.smoke(0, 0, h * 2.6, strength=smoke)


def big_lantern(b, s=0.5, col="iron", lamp=2.0, glow="#ffd88a"):
    """A big storm lantern; the origin is the point it hangs from."""
    hh = s * 1.15
    with b.detail(1):
        beam(b, (0, 0, 0), (0, 0, -0.16), w=0.03, mat="metal", col=col, caps=False)
        with b.at(0, 0, -0.16 - s * 0.36, rz=45):
            b.revolve([(s * 0.78, 0.0), (s * 0.1, s * 0.36)], "metal", col=col, seg=4, smooth=False)
            b.disc(s * 0.78, "metal", col=shade(col, 0.7), seg=4, down=True)
        zb = -0.16 - s * 0.36 - hh
        b.box(s * 0.82, s * 0.82, hh, "glow", col=glow, z=zb, bottom=True, top=False)
        b.box(s * 0.96, s * 0.96, 0.06, "metal", col=col, z=zb - 0.06, bottom=True)
    with b.detail(2):
        for sx in (-1, 1):
            for sy in (-1, 1):
                beam(b, (sx * s * 0.42, sy * s * 0.42, zb), (sx * s * 0.42, sy * s * 0.42, zb + hh), w=0.04, mat="metal", col=col, caps=False)
    if lamp:
        b.lamp(0, 0, zb + hh / 2, strength=lamp)


VANES = {
    "arrow": [(0.62, 0), (0.4, 0.1), (0.4, 0.02), (-0.3, 0.02), (-0.4, 0.14), (-0.62, 0.14), (-0.5, 0.0), (-0.62, -0.14), (-0.4, -0.14), (-0.3, -0.02), (0.4, -0.02), (0.4, -0.1)],
    "whale": [(0.5, 0.02), (0.42, 0.13), (0.2, 0.19), (-0.1, 0.17), (-0.32, 0.09), (-0.5, 0.03), (-0.62, 0.15), (-0.74, 0.17), (-0.65, 0.02), (-0.72, -0.11), (-0.56, -0.04),
              (-0.3, -0.1), (0.0, -0.14), (0.3, -0.13), (0.46, -0.07)],
    "fish": [(0.45, 0), (0.3, 0.1), (0.05, 0.13), (-0.2, 0.07), (-0.32, 0.02), (-0.5, 0.14), (-0.46, 0.0), (-0.5, -0.14), (-0.32, -0.02), (-0.2, -0.07), (0.05, -0.13), (0.3, -0.1)],
    "gull": [(0, 0.03), (0.2, 0.14), (0.42, 0.1), (0.6, 0.0), (0.4, 0.04), (0.2, 0.05), (0.04, -0.06), (0, -0.1), (-0.04, -0.06), (-0.2, 0.05), (-0.4, 0.04), (-0.6, 0.0), (-0.42, 0.1), (-0.2, 0.14)],
    "boat": [(-0.5, 0.0), (0.5, 0.0), (0.38, -0.14), (-0.4, -0.14), (-0.44, -0.04), (-0.05, -0.02), (-0.05, 0.36), (0.3, 0.04), (0.0, 0.04), (0.0, 0.0)],
}


def vane(b, x=0.0, y=0.0, z=0.0, h=1.5, kind="arrow", col="iron", fig="brass", s=1.0, rz=None, arms=True, lod=1):
    """A wind vane on a pole rising from (x, y, z): 'arrow', 'whale', 'fish', 'gull' or 'boat'."""
    with b.at(x, y, z):
        with b.detail(lod):
            b.tube((0, 0, 0), (0, 0, h), r=0.025, mat="metal", col=col, n=5)
            with b.at(z=h * 0.9 if arms else h * 0.96, rz=b.r(0, 360) if rz is None else rz):
                shape(b, [(p[0] * s, p[1] * s + 0.02) for p in VANES[kind]], mat="metal", col=fig, lod=lod)
        if arms:
            with b.detail(2):
                beam(b, (-0.3, 0, h * 0.6), (0.3, 0, h * 0.6), w=0.02, mat="metal", col=col, caps=False)
                beam(b, (0, -0.3, h * 0.6), (0, 0.3, h * 0.6), w=0.02, mat="metal", col=col, caps=False)
                b.box(0.08, 0.08, 0.08, "metal", col=fig, z=h * 0.6 - 0.04, bottom=True)


def anemometer(b, x=0.0, y=0.0, z=0.0, h=1.8, arm=0.36, cup=0.11, speed=0.9, n=4, col="iron", cupcol="copper"):
    """A cup anemometer on a pole: its cups turn in the wind."""
    with b.at(x, y, z):
        with b.detail(1):
            b.tube((0, 0, 0), (0, 0, h), r=0.03, mat="metal", col=col, n=5)
        with b.at(0, 0, h):
            with b.spin(speed=speed, axis=(0, 0, 1)):
                with b.detail(1):
                    b.box(0.09, 0.09, 0.1, "metal", col=col, z=-0.02, bottom=True)
                    for k in range(n):
                        with b.at(rz=360.0 * k / n):
                            beam(b, (0, 0, 0.03), (arm, 0, 0.03), w=0.022, mat="metal", col=col, caps=False)
                            with b.at(arm, 0, 0.03, rx=90):
                                b.revolve([(0.0, -cup), (cup * 0.72, -cup * 0.68), (cup, 0.0)], "metal", col=cupcol, seg=6)
                                b.revolve([(cup * 0.94, 0.0), (cup * 0.66, -cup * 0.62), (0.0, -cup * 0.9)], "metal", col=shade(cupcol, 0.6), seg=6)


def windsock(b, x=0.0, y=0.0, z=0.0, h=2.4, L=1.3, r=0.17, cols=("red", "ivory"), rz=0.0):
    """A striped windsock on a pole: it streams in the game's wind."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            b.tube((0, 0, 0), (0, 0, h), r=0.03, mat="metal", col="iron", n=5)
            n, seg = 5, 6
            for i in range(n):
                t0, t1 = i / n, (i + 1) / n
                r0, r1 = r * (1 - 0.55 * t0), r * (1 - 0.55 * t1)
                c = cols[i % len(cols)]
                for k in range(seg):
                    a0, a1 = 2 * math.pi * k / seg, 2 * math.pi * (k + 1) / seg
                    q = [(0.05 + L * t0, r0 * math.cos(a0), h - 0.2 + r0 * math.sin(a0)), (0.05 + L * t1, r1 * math.cos(a0), h - 0.2 + r1 * math.sin(a0) - 0.25 * t1 * t1),
                         (0.05 + L * t1, r1 * math.cos(a1), h - 0.2 + r1 * math.sin(a1) - 0.25 * t1 * t1), (0.05 + L * t0, r0 * math.cos(a1), h - 0.2 + r0 * math.sin(a1))]
                    wd = (t0, t1, t1, t0)
                    b.face(list(reversed(q)), "cloth", col=c, wind=tuple(reversed(wd)))
                    b.face(q, "cloth", col=shade(c, 0.8), wind=wd)


def sign(s, pos, z, pts, col="mustard", board="ivory", out=0.8, w=0.66, h=0.58):
    """A hanging sign on an iron bracket with a cut-out emblem pts = [(x, z), ...] (within about +-0.24)."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            with b.detail(1):
                beam(b, (0, -0.01, 0.06), (0, -out - 0.05, 0.06), w=0.035, mat="metal", col="iron", caps=False)
                beam(b, (0, -0.01, -0.34), (0, -out * 0.6, 0.04), w=0.03, mat="metal", col="iron", caps=False)
                with b.at(0, -out * 0.55, -h - 0.1):
                    b.box(0.05, w, h, "paint", col=board, bottom=True)
            with b.detail(2):
                for sx, rz in ((1, 90), (-1, 270)):
                    with b.at(sx * 0.031, -out * 0.55, -h / 2 - 0.1, rz=rz):
                        shape(b, pts, mat="paint", col=col, lod=2, both=False)
                for yy in (-out * 0.55 - w * 0.35, -out * 0.55 + w * 0.35):
                    beam(b, (0, yy, 0.05), (0, yy, -0.1), w=0.015, mat="metal", col="iron", caps=False)

    s.add(deco)


LANTERN = [(-0.03, 0.24), (0.03, 0.24), (0.03, 0.18), (0.14, 0.1), (0.1, 0.1), (0.13, -0.14), (0.16, -0.14), (0.16, -0.2), (-0.16, -0.2), (-0.16, -0.14), (-0.13, -0.14), (-0.1, 0.1), (-0.14, 0.1), (-0.03, 0.18)]


def polar(r, deg, z=0.0, cx=0.0, cy=0.0):
    """The point at radius r and compass angle deg (0 = front, 90 = right) round (cx, cy)."""
    return (cx + r * math.sin(rad(deg)), cy - r * math.cos(rad(deg)), z)


def rope(b, p0, p1, sag=0.0, w=0.03, col=ROPE, n=5, lod=2, wind=0.0):
    """A rope from p0 to p1, hanging `sag` low in the middle."""
    pts = [(lerp(p0[0], p1[0], i / n), lerp(p0[1], p1[1], i / n), lerp(p0[2], p1[2], i / n) - sag * 4 * (i / n) * (1 - i / n)) for i in range(n + 1)] if sag else [p0, p1]
    with b.detail(lod):
        for a, c in zip(pts, pts[1:]):
            beam(b, a, c, w=w, mat="cloth", col=col, caps=False, wind=wind)


def rotor(b, r=1.35, n=8, r0=0.3, cols=("teal", "ivory"), hoop=0.7, twist=0.07, w0=0.18, w1=0.46, lod=0):
    """A wind pump's wheel of painted plank vanes. Make it inside `with b.spin(...)`: it lies in the local x-z
    plane round the origin and faces local -y (the spin axis)."""
    with b.detail(lod):
        for k in range(n):
            a = 2 * math.pi * k / n
            u, t = (math.cos(a), 0.0, math.sin(a)), (-math.sin(a), 0.0, math.cos(a))
            pt = lambda rr, s, wd, yy: (u[0] * rr + t[0] * s, yy + twist * s / (wd / 2), u[2] * rr + t[2] * s)
            c = cols[k % len(cols)]
            q = [pt(r0, -w0 / 2, w0, -0.003), pt(r, -w1 / 2, w1, -0.003), pt(r, w1 / 2, w1, -0.003), pt(r0, w0 / 2, w0, -0.003)]
            b.face(q, "planks", col=c)
            q2 = [pt(r0, w0 / 2, w0, 0.003), pt(r, w1 / 2, w1, 0.003), pt(r, -w1 / 2, w1, 0.003), pt(r0, -w0 / 2, w0, 0.003)]
            b.face(q2, "planks", col=shade(c, 0.75))
            beam(b, (0, 0.03, 0), (u[0] * r * 0.97, 0.03, u[2] * r * 0.97), w=0.045, mat="timber", col="darkoak", caps=False)
        with b.at(rx=90):
            b.revolve([(0.13, -0.1), (0.13, 0.08), (0.05, 0.16)], "metal", col="iron", seg=8, close_top=True)
    with b.detail(max(lod, 1)):
        m = n * 2
        for k in range(m):
            a0, a1 = 2 * math.pi * k / m, 2 * math.pi * (k + 1) / m
            beam(b, (math.cos(a0) * r * hoop, 0.04, math.sin(a0) * r * hoop), (math.cos(a1) * r * hoop, 0.04, math.sin(a1) * r * hoop), w=0.03, mat="metal", col="iron", caps=False)


def weather_screen(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="ivory", h=1.15):
    """The weather-watcher's instrument screen: a white louvred box on legs."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    beam(b, (sx * 0.3, sy * 0.21, 0), (sx * 0.27, sy * 0.19, h + 0.05), w=0.05, mat="planks", col=col)
            b.box(0.66, 0.5, 0.56, "planks", col=col, z=h, bottom=True)
            b.box(0.84, 0.68, 0.05, "planks", col=shade(col, 0.86), z=h + 0.6, bottom=True)
            b.box(0.7, 0.54, 0.05, "planks", col=shade(col, 0.8), z=h + 0.56, bottom=False, top=False)
        with b.detail(2):
            for i in range(5):
                zz = h + 0.07 + 0.095 * i
                for (cx, cy, w_, d_) in ((0, -0.26, 0.62, 0.035), (0, 0.26, 0.62, 0.035), (-0.34, 0, 0.035, 0.46), (0.34, 0, 0.035, 0.46)):
                    b.box(w_, d_, 0.03, "planks", col=shade(col, 0.72), x=cx, y=cy, z=zz, bottom=True)


def storm_mast(b, x=0.0, y=0.0, z=0.0, h=3.4, yard=1.3, rz=0.0, cone=True, col="darkoak"):
    """A signal mast with a yard: a tarred canvas storm cone hoisted on one arm, a pennant at the truck."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            b.tube((0, 0, 0), (0, 0, h), r=0.055, r1=0.035, mat="planks", col=col, n=6)
            beam(b, (-yard / 2, 0, h * 0.74), (yard / 2, 0, h * 0.74), w=0.05, mat="planks", col=col)
            b.box(0.09, 0.09, 0.09, "metal", col="brass", z=h, bottom=True)
            if cone:
                with b.at(yard / 2 - 0.12, 0, h * 0.74 - 0.72):
                    b.revolve([(0.24, 0.0), (0.0, 0.52)], "cloth", col="#2f2d30", seg=7)
                    b.disc(0.24, "cloth", col="#262427", seg=7, down=True)
        with b.detail(2):
            if cone:
                beam(b, (yard / 2 - 0.12, 0, h * 0.74), (yard / 2 - 0.12, 0, h * 0.74 - 0.2), w=0.015, mat="cloth", col=ROPE, caps=False)
            beam(b, (-yard / 2 + 0.1, 0, h * 0.74), (-0.05, 0, 0.5), w=0.015, mat="cloth", col=ROPE, caps=False)
        P.flag(b, 0, 0, h * 0.82, pole=h * 0.2, w=0.8, h=0.3, col="stripe_red", pole_col=col)


def knee(b, p0, p1, w=0.14, col="darkoak", lod=1, strut=True):
    """A timber bracket: a raking brace from p0 (low, on the wall) up to p1 (out under what it carries), with a
    short level strut at the top back to the wall line."""
    with b.detail(lod):
        beam(b, p0, p1, w=w, mat="timber", col=col)
        if strut:
            beam(b, (p0[0], p0[1], p1[2] - w * 0.6), (p1[0], p1[1], p1[2] - w * 0.6), w=w * 0.9, h=w, mat="timber", col=col, up=(0, 0, 1))


def convex(pts):
    """The convex hull of 2-D points, anticlockwise (so that any outline can safely be given to a BWall)."""
    P_ = sorted(set((round(p[0], 5), round(p[1], 5)) for p in pts))
    if len(P_) < 3:
        return P_
    cr = lambda o, a, c: (a[0] - o[0]) * (c[1] - o[1]) - (a[1] - o[1]) * (c[0] - o[0])
    lo, hi = [], []
    for p in P_:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 1e-9:
            lo.pop()
        lo.append(p)
    for p in reversed(P_):
        while len(hi) >= 2 and cr(hi[-2], hi[-1], p) <= 1e-9:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def bellcote(b, w=1.5, t=0.5, h=1.5, col="grey", bell=0.25, cap="flagstone", lod=0):
    """A bell-cote to stand on a gable's apex: two stone piers and a little gabled cap, the bell hanging between.
    Origin = the middle of its foot; it is w wide along local x and t thick."""
    pw = w * 0.26
    for sx in (-1, 1):
        b.box(pw, t, h, "masonry", col=col, x=sx * (w / 2 - pw / 2), y=0, z=0, lod=lod, taper=0.94)
    b.box(w + 0.1, t + 0.08, 0.14, "flagstone", col=shade("grey", 1.02), z=h, lod=lod, bottom=True)
    prof = [(-(w / 2 + 0.12), h + 0.14), (w / 2 + 0.12, h + 0.14), (0.0, h + 0.14 + w * 0.48)]
    for sy, flip in ((-1, False), (1, True)):
        q = [(p[0], sy * (t / 2 + 0.06), p[1]) for p in prof]
        b.face(list(reversed(q)) if flip else q, "masonry", col=col, lod=lod)
    for sx in (-1, 1):
        a = (sx * (w / 2 + 0.12), 0.0, h + 0.14)
        q = [(a[0], -(t / 2 + 0.06), a[2]), (a[0], t / 2 + 0.06, a[2]), (0.0, t / 2 + 0.06, prof[2][1]), (0.0, -(t / 2 + 0.06), prof[2][1])]
        b.face(q if sx > 0 else list(reversed(q)), cap, col=shade("grey", 0.95), lod=lod)
    with b.at(0, 0, h - 0.02):
        P.bell(b, 0, 0, 0, r=bell, beam=w - 2 * pw + 0.1)
    return h + 0.14 + w * 0.48


def barrel_lum(b, x=0.0, y=0.0, z=0.0, r=0.3, h=0.75, col="#5b4a3c", strength=0.9):
    """A blackhouse's chimney: an old tarred barrel with both ends knocked out, set in the thatch."""
    with b.at(x, y, z):
        with b.detail(1):
            b.revolve([(r * 0.86, 0.0), (r, h * 0.35), (r, h * 0.65), (r * 0.86, h)], "planks", col=col, seg=9)
            b.revolve([(r * 0.86, h), (r * 0.78, h)], "planks", col=shade(col, 0.6), seg=9)
            b.revolve([(r * 0.78, h), (r * 0.9, h * 0.5)], "paint", col="#1d1b1c", seg=9)
        with b.detail(2):
            for zz in (h * 0.18, h * 0.82):
                b.revolve([(r * 0.93, zz - 0.03), (r * 0.95, zz + 0.03)], "metal", col="iron", seg=9)
        b.smoke(0, 0, h + 0.3, strength=strength)


def headstone(b, x=0.0, y=0.0, h=0.8, w=0.5, rz=0.0, lean=6.0, col="grey"):
    """An old leaning slab of a gravestone, lichened."""
    with b.at(x, y, -0.1, rz=rz, rx=lean):
        b.stone(w, 0.12, h + 0.1, mat="flagstone", col=shade(col, b.r(0.85, 1.05)), lod=1, ch=0.3, jitter=0.1)
