"""Petalwake town kit: the modelling vocabulary every building is made from.

A building script gets a `Building` and adds to it with plain calls: walls with real recessed
openings, round and many-sided towers, stepped-course roofs, beams, stones, lathe-turned shapes.
`parts.py` builds the finer vocabulary on top (windows, doors, galleries, chimneys, dormers ...).

Frame: x to the right, y away from the street, z up, metres. A building's front faces -y and its
footprint is centred on x = 0 with the front wall near y = 0 (so y runs 0 .. depth).
Everything is emitted through a transform stack (`with b.at(...)`), so parts are written once in
their own local frame.

Every face carries: a material (name from MATS), a tint (r, g, b[, paint]) in sRGB 0..1, a detail
level (0 = always drawn, 1 = dropped beyond a few hundred metres, 2 = dropped beyond ~120 m), UVs in
metres, an optional smoothing group and a wind weight (cloth, flags, leaves).
"""
import math
import random
from contextlib import contextmanager

import numpy as np

# material ids: the first 13 are layers of the game's texture array (tools/town/pack_textures.py),
# the rest are shaded procedurally in src/world/town.js
MATS = ["masonry", "ashlar", "plaster", "timber", "planks", "slate", "tiles", "thatch", "shingle",
        "brick", "cobble", "flagstone", "ivy", "metal", "glass", "cloth", "paint", "glow", "water"]
M = {n: i for i, n in enumerate(MATS)}

WHITE = (1.0, 1.0, 1.0, 0.0)


def hexcol(h, paint=0.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, paint)


def paint(h):
    """A painted surface: the texture gives only light and dark, the colour is this."""
    return hexcol(h, 1.0)


# The village palette. Walls are tints (multiplied into the material); woodwork and cloth are paints.
PAL = {
    # plaster washes
    "cream": hexcol("#fff6e2"), "white": hexcol("#ffffff"), "butter": hexcol("#ffeeb8"), "ochre": hexcol("#f3cf8e"),
    "rose": hexcol("#f6cdbd"), "peach": hexcol("#fad9b4"), "sage": hexcol("#d9e3c4"), "sky": hexcol("#d5e6ee"),
    "lilac": hexcol("#e3d8ee"), "sand": hexcol("#ead9bb"),
    # stone tones
    "stone": hexcol("#ffffff"), "warm": hexcol("#ffe9c9"), "grey": hexcol("#d6d6d2"), "dark": hexcol("#a9a59c"),
    "moss": hexcol("#c9d6a2"),
    # timber
    "oak": hexcol("#ffffff"), "darkoak": hexcol("#b79f8c"), "blackoak": hexcol("#7c6c62"), "greyoak": hexcol("#d9d2c7"),
    # paints (doors, shutters, frames, boats)
    "green": paint("#3f8f5f"), "teal": paint("#2f8f8f"), "blue": paint("#3f6fb5"), "navy": paint("#2f4470"),
    "red": paint("#b5433a"), "mustard": paint("#d9a431"), "plum": paint("#7a4672"), "pink": paint("#d9879a"),
    "ivory": paint("#f2ead8"), "black": paint("#2c2a2a"), "brown": paint("#6b4a35"), "mint": paint("#8fcfae"),
    "orange": paint("#d97b35"),
    # metals (material "metal")
    "iron": hexcol("#3a3a3e"), "copper": hexcol("#5fa58c"), "brass": hexcol("#c9a24a"), "lead": hexcol("#7f868c"),
    # cloth
    "linen": hexcol("#f3ecd9"), "stripe_red": hexcol("#c8493f"), "stripe_blue": hexcol("#4a78b8"),
    "stripe_yellow": hexcol("#e5b84a"), "stripe_green": hexcol("#5a9a68"),
}


def C(c):
    """Colour argument: a palette name, '#rrggbb', '!#rrggbb' (painted), or an (r, g, b[, paint]) tuple."""
    if c is None:
        return WHITE
    if isinstance(c, str):
        if c in PAL:
            return PAL[c]
        if c.startswith("!"):
            return paint(c[1:])
        return hexcol(c)
    return tuple(c) if len(c) == 4 else (c[0], c[1], c[2], 0.0)


def shade(c, k):
    """The same colour, k times as bright."""
    c = C(c)
    return (min(c[0] * k, 1.0), min(c[1] * k, 1.0), min(c[2] * k, 1.0), c[3])


def mix(a, b, t):
    a, b = C(a), C(b)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))


def rad(d):
    return d * math.pi / 180.0


def _mat4(x=0.0, y=0.0, z=0.0, rz=0.0, rx=0.0, ry=0.0, s=1.0):
    cz, sz, cx, sx, cy, sy = math.cos(rad(rz)), math.sin(rad(rz)), math.cos(rad(rx)), math.sin(rad(rx)), math.cos(rad(ry)), math.sin(rad(ry))
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    T = np.eye(4)
    sc = np.diag(s if isinstance(s, (tuple, list)) else (s, s, s))
    T[:3, :3] = Rz @ Ry @ Rx @ sc
    T[:3, 3] = (x, y, z)
    return T


def vsub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def vadd(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def vmul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def vlen(a): return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
def vcross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def vdot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vnorm(a):
    l = vlen(a) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)


def lerp(a, b, t): return a + (b - a) * t
def vlerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


class Geo:
    """Faces with attributes. Vertices that land on the same spot are shared."""

    def __init__(self):
        self.v = []
        self._vi = {}
        self.f = []      # (indices, uvs, mat, col, lod, smooth group, wind per corner, spinner id)

    def vert(self, p):
        k = (round(p[0], 4), round(p[1], 4), round(p[2], 4))
        i = self._vi.get(k)
        if i is None:
            i = len(self.v)
            self.v.append(k)
            self._vi[k] = i
        return i

    def face(self, pts, uvs, mat, col, lod, sm, wind, spin=0):
        idx, uv2, w2 = [], [], []
        for k, p in enumerate(pts):
            i = self.vert(p)
            if idx and (i == idx[-1]):
                continue
            idx.append(i); uv2.append(uvs[k]); w2.append(wind[k])
        if len(idx) > 1 and idx[0] == idx[-1]:
            idx.pop(); uv2.pop(); w2.pop()
        if len(idx) < 3:
            return
        self.f.append((tuple(idx), tuple(uv2), mat, col, lod, sm, tuple(w2), spin))


class Building:
    def __init__(self, bid, seed=None):
        self.id = bid
        self.rng = random.Random(seed if seed is not None else sum(ord(c) * (i + 7) for i, c in enumerate(bid)))
        self.g = Geo()
        self._stack = [np.eye(4)]
        self._m = self._stack[-1]
        self._lod = None
        self._spin = 0
        self._sm = 0
        self._walls = []
        self.pads, self.smokes, self.lamps, self.foot, self.spinners = [], [], [], [], []
        self.meta = {"name": bid, "kind": "house", "notes": ""}

    # ------------------------------------------------------------------ transforms and state
    @contextmanager
    def at(self, x=0.0, y=0.0, z=0.0, rz=0.0, rx=0.0, ry=0.0, s=1.0):
        """Work in a moved / turned / scaled frame. Angles in degrees; rz turns anticlockwise seen from above."""
        self._stack.append(self._stack[-1] @ _mat4(x, y, z, rz, rx, ry, s))
        self._m = self._stack[-1]
        try:
            yield self
        finally:
            self._stack.pop()
            self._m = self._stack[-1]

    @contextmanager
    def frame(self, m):
        self._stack.append(m)
        self._m = m
        try:
            yield self
        finally:
            self._stack.pop()
            self._m = self._stack[-1]

    @contextmanager
    def detail(self, lod):
        """Everything emitted inside is given this detail level (0 always, 1 mid, 2 near only)."""
        old, self._lod = self._lod, lod
        try:
            yield self
        finally:
            self._lod = old

    @contextmanager
    def spin(self, speed=0.5, axis=(0, -1, 0), wind=True):
        """Everything emitted inside turns in the game about `axis` through the origin of the current frame
        (windmill sails, a weathercock). speed in turns per second at full wind; wind=True scales it with the wind."""
        o = self.tp((0, 0, 0)); q = self.tp(axis)
        ax = vnorm(vsub(q, o))
        self.spinners.append({"pivot": [round(v, 4) for v in o], "axis": [round(v, 4) for v in ax], "speed": speed, "wind": bool(wind)})
        old, self._spin = self._spin, len(self.spinners)
        try:
            yield self
        finally:
            self._spin = old

    def tp(self, p):
        m = self._m
        x, y, z = p
        return (m[0, 0] * x + m[0, 1] * y + m[0, 2] * z + m[0, 3], m[1, 0] * x + m[1, 1] * y + m[1, 2] * z + m[1, 3], m[2, 0] * x + m[2, 1] * y + m[2, 2] * z + m[2, 3])

    def world(self, p=(0, 0, 0)):
        """Where a local point is in the building's own frame (for pads, smoke and so on)."""
        return self.tp(p)

    def heading(self, local_deg=0.0):
        """Building-frame compass angle (degrees, 0 = facing the front -y, 90 = +x) of a local direction that
        makes `local_deg` with the local -y axis."""
        a = rad(local_deg)
        o = self.tp((0, 0, 0)); q = self.tp((math.sin(a), -math.cos(a), 0))
        return math.degrees(math.atan2(q[0] - o[0], -(q[1] - o[1])))

    def r(self, a=0.0, b=1.0):
        return self.rng.uniform(a, b)

    def chance(self, p):
        return self.rng.random() < p

    def pick(self, seq):
        return seq[self.rng.randrange(len(seq))]

    def sm(self):
        self._sm += 1
        return self._sm

    def uvo(self):
        return (self.rng.uniform(0, 8), self.rng.uniform(0, 8))

    # ------------------------------------------------------------------ faces
    def face(self, pts, mat, uv=None, col=None, lod=0, sm=0, wind=0.0):
        """One convex polygon, anticlockwise seen from outside. uv in metres (default: laid flat on the face)."""
        n = len(pts)
        if uv is None:
            e1 = vsub(pts[1], pts[0])
            nrm = vcross(e1, vsub(pts[-1], pts[0]))
            a = vnorm(e1)
            bax = vnorm(vcross(nrm, a)) if vlen(nrm) > 1e-9 else (0, 0, 1)
            uv = [(vdot(vsub(p, pts[0]), a), vdot(vsub(p, pts[0]), bax)) for p in pts]
        if not isinstance(wind, (tuple, list)):
            wind = (wind,) * n
        lod = self._lod if self._lod is not None else lod
        self.g.face([self.tp(p) for p in pts], uv, mat if isinstance(mat, int) else M[mat], C(col), lod, sm, wind, self._spin)

    def quad(self, p0, p1, p2, p3, mat, **kw):
        self.face((p0, p1, p2, p3), mat, **kw)

    def tri(self, p0, p1, p2, mat, **kw):
        self.face((p0, p1, p2), mat, **kw)

    # ------------------------------------------------------------------ solids
    def box(self, w, d, h, mat, col=None, lod=0, x=0.0, y=0.0, z=0.0, top=True, bottom=False, taper=1.0, tx=None, ty=None,
            cap=None, capcol=None, uvo=None, sides="frbl"):
        """A block centred on (x, y) standing on z. taper (or tx, ty) narrows the top. cap = material of the top."""
        tx = taper if tx is None else tx
        ty = taper if ty is None else ty
        uo, vo = uvo or self.uvo()
        hw, hd = w / 2, d / 2
        B = [(x - hw, y - hd, z), (x + hw, y - hd, z), (x + hw, y + hd, z), (x - hw, y + hd, z)]
        T = [(x - hw * tx, y - hd * ty, z + h), (x + hw * tx, y - hd * ty, z + h), (x + hw * tx, y + hd * ty, z + h), (x - hw * tx, y + hd * ty, z + h)]
        u = [0, w, w + d, 2 * w + d, 2 * w + 2 * d]
        for i, s in enumerate("frbl"):
            if s not in sides:
                continue
            j = (i + 1) % 4
            self.quad(B[i], B[j], T[j], T[i], mat, col=col, lod=lod, uv=[(u[i] + uo, vo), (u[i + 1] + uo, vo), (u[i + 1] + uo, vo + h), (u[i] + uo, vo + h)])
        if top:
            self.quad(T[0], T[1], T[2], T[3], cap or mat, col=capcol if capcol is not None else col, lod=lod,
                      uv=[(uo, vo), (uo + w * tx, vo), (uo + w * tx, vo + d * ty), (uo, vo + d * ty)])
        if bottom:
            self.quad(B[3], B[2], B[1], B[0], mat, col=shade(col, 0.8), lod=lod, uv=[(uo, vo), (uo + w, vo), (uo + w, vo + d), (uo, vo + d)])

    def beam(self, p0, p1, w=0.14, h=None, mat="timber", col=None, lod=1, up=(0, 0, 1), caps=True, uvo=None, wind=0.0):
        """A squared timber (or bar, or rope) from p0 to p1; w across, h in the `up` direction."""
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
        uo, vo = uvo or self.uvo()
        c0 = [vadd(p0, vadd(vmul(s, sx * w / 2), vmul(u2, sz * h / 2))) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        c1 = [vadd(p, vmul(a, L)) for p in c0]
        acc = 0.0
        for i in range(4):
            j = (i + 1) % 4
            e = w if i % 2 == 0 else h
            self.quad(c0[i], c1[i], c1[j], c0[j], mat, col=col, lod=lod, wind=wind,
                      uv=[(uo, vo + acc), (uo + L, vo + acc), (uo + L, vo + acc + e), (uo, vo + acc + e)])
            acc += e
        if caps:        # (wound to face out of the ends)
            self.quad(c0[0], c0[1], c0[2], c0[3], mat, col=shade(col, 0.85), lod=lod, wind=wind)
            self.quad(c1[3], c1[2], c1[1], c1[0], mat, col=shade(col, 0.85), lod=lod, wind=wind)

    def tube(self, p0, p1, r=0.06, mat="metal", col=None, lod=1, n=6, r1=None, caps=False, smooth=True):
        """A round bar or post from p0 to p1."""
        r1 = r if r1 is None else r1
        a = vsub(p1, p0)
        L = vlen(a)
        if L < 1e-6:
            return
        a = vmul(a, 1 / L)
        s = vcross(a, (0, 0, 1))
        if vlen(s) < 1e-4:
            s = (1, 0, 0)
        s = vnorm(s)
        t = vnorm(vcross(a, s))
        sm = self.sm() if smooth else 0
        uo, vo = self.uvo()
        ring = lambda p, rr: [vadd(p, vadd(vmul(s, rr * math.cos(2 * math.pi * i / n)), vmul(t, rr * math.sin(2 * math.pi * i / n)))) for i in range(n)]
        A, Bq = ring(p0, r), ring(p1, r1)
        for i in range(n):
            j = (i + 1) % n
            u0, u1 = 2 * math.pi * r * i / n, 2 * math.pi * r * (i + 1) / n
            self.quad(A[i], A[j], Bq[j], Bq[i], mat, col=col, lod=lod, sm=sm, uv=[(uo + u0, vo), (uo + u1, vo), (uo + u1, vo + L), (uo + u0, vo + L)])
        if caps:
            self.face(list(reversed(A)), mat, col=col, lod=lod)
            self.face(Bq, mat, col=col, lod=lod)

    def revolve(self, profile, mat, col=None, lod=0, seg=20, a0=0.0, a1=360.0, smooth=True, flat_rings=False, rref=None, uvo=None,
                close_top=False, close_bottom=False, wind=0.0, cols=None):
        """Lathe: spin a profile [(radius, z), ...] (bottom to top for an outward-facing surface) about the z axis.
        seg sides; smooth=False gives a faceted (many-sided) shape. cols = optional tint per profile span."""
        sm = self.sm() if smooth else 0
        full = abs((a1 - a0) - 360.0) < 1e-6
        rref = rref or max(r for r, _ in profile) or 1.0
        uo, vo = uvo or self.uvo()
        vs = [0.0]
        for i in range(1, len(profile)):
            vs.append(vs[-1] + math.hypot(profile[i][0] - profile[i - 1][0], profile[i][1] - profile[i - 1][1]))
        ang = [rad(a0 + (a1 - a0) * i / seg) for i in range(seg + 1)]
        P = lambda r, z, a: (r * math.sin(a), -r * math.cos(a), z)
        for j in range(len(profile) - 1):
            (ra, za), (rb, zb) = profile[j], profile[j + 1]
            c = cols[j] if cols else col
            s = 0 if (flat_rings and abs(ra - rb) < 1e-6 and False) else sm
            for i in range(seg):
                ua, ub = ang[i] * rref, ang[i + 1] * rref
                self.quad(P(ra, za, ang[i]), P(ra, za, ang[i + 1]), P(rb, zb, ang[i + 1]), P(rb, zb, ang[i]), mat, col=c, lod=lod, sm=s, wind=wind,
                          uv=[(uo + ua, vo + vs[j]), (uo + ub, vo + vs[j]), (uo + ub, vo + vs[j + 1]), (uo + ua, vo + vs[j + 1])])
        if close_top and profile[-1][0] > 1e-6:
            r, z = profile[-1]
            self.face([P(r, z, ang[i]) for i in range(seg)], mat, col=col, lod=lod)
        if close_bottom and profile[0][0] > 1e-6:
            r, z = profile[0]
            self.face([P(r, z, ang[i]) for i in reversed(range(seg))], mat, col=shade(col, 0.8), lod=lod)
        return full

    def disc(self, r, mat, col=None, lod=0, seg=20, z=0.0, r_in=0.0, down=False, uvo=None):
        """A flat round floor (or a ring if r_in > 0) at height z, facing up (or down)."""
        uo, vo = uvo or self.uvo()
        ang = [2 * math.pi * i / seg for i in range(seg + 1)]
        P = lambda rr, a: (rr * math.sin(a), -rr * math.cos(a), z)
        U = lambda p: (uo + p[0], vo + p[1])
        for i in range(seg):
            a, b = ang[i], ang[i + 1]
            pts = [P(r_in, a), P(r, a), P(r, b), P(r_in, b)] if r_in > 1e-6 else [(0, 0, z), P(r, a), P(r, b)]
            if down:
                pts = list(reversed(pts))
            self.face(pts, mat, col=col, lod=lod, uv=[U(p) for p in pts])

    def prism(self, poly, h, mat, col=None, lod=0, z=0.0, top=True, bottom=False, cap=None, capcol=None, uvo=None, smooth=False):
        """Extrude a convex outline [(x, y), ...] (anticlockwise seen from above) upward by h."""
        uo, vo = uvo or self.uvo()
        n = len(poly)
        sm = self.sm() if smooth else 0
        acc = 0.0
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            self.quad((a[0], a[1], z), (b[0], b[1], z), (b[0], b[1], z + h), (a[0], a[1], z + h), mat, col=col, lod=lod, sm=sm,
                      uv=[(uo + acc, vo), (uo + acc + L, vo), (uo + acc + L, vo + h), (uo + acc, vo + h)])
            acc += L
        if top:
            self.face([(p[0], p[1], z + h) for p in poly], cap or mat, col=capcol if capcol is not None else col, lod=lod, uv=[(uo + p[0], vo + p[1]) for p in poly])
        if bottom:
            self.face([(p[0], p[1], z) for p in reversed(poly)], mat, col=shade(col, 0.8), lod=lod, uv=[(uo + p[0], vo + p[1]) for p in reversed(poly)])

    def stone(self, w, d, h, mat="masonry", col=None, lod=2, x=0.0, y=0.0, z=0.0, ch=0.22, jitter=0.12, bottom=False):
        """One chunky, slightly crooked block with softened top edges, centred on (x, y) and standing on z."""
        r = self.rng
        col = shade(col, r.uniform(0.86, 1.10))
        c = min(w, d, h) * ch
        hw, hd = w / 2, d / 2
        j = lambda: r.uniform(-jitter, jitter) * min(w, d, h) * 0.5
        B = [(x - hw + j(), y - hd + j(), z), (x + hw + j(), y - hd + j(), z), (x + hw + j(), y + hd + j(), z), (x - hw + j(), y + hd + j(), z)]
        Mid = [(p[0], p[1], z + h - c + j() * 0.5) for p in B]
        cx, cy = sum(p[0] for p in B) / 4, sum(p[1] for p in B) / 4
        T = [(p[0] + (cx - p[0]) * (c / max(hw, 1e-3)) * 0.9, p[1] + (cy - p[1]) * (c / max(hd, 1e-3)) * 0.9, z + h + j() * 0.3) for p in B]
        uo, vo = self.uvo()
        acc = 0.0
        for i in range(4):
            k = (i + 1) % 4
            L = math.hypot(B[k][0] - B[i][0], B[k][1] - B[i][1])
            self.quad(B[i], B[k], Mid[k], Mid[i], mat, col=col, lod=lod, uv=[(uo + acc, vo), (uo + acc + L, vo), (uo + acc + L, vo + h - c), (uo + acc, vo + h - c)])
            self.quad(Mid[i], Mid[k], T[k], T[i], mat, col=shade(col, 1.06), lod=lod, uv=[(uo + acc, vo + h - c), (uo + acc + L, vo + h - c), (uo + acc + L, vo + h), (uo + acc, vo + h)])
            acc += L
        self.quad(T[0], T[1], T[2], T[3], mat, col=shade(col, 1.1), lod=lod, uv=[(uo, vo), (uo + w, vo), (uo + w, vo + d), (uo, vo + d)])
        if bottom:
            self.quad(B[3], B[2], B[1], B[0], mat, col=shade(col, 0.7), lod=lod)

    def blob(self, rx, ry=None, rz=None, mat="ivy", col=None, lod=1, x=0.0, y=0.0, z=0.0, rough=0.22, seg=7, rings=4, wind=0.0, bottom=True):
        """A lumpy rounded mass (shrub, tree crown, boulder, sack): centred on (x, y), z = its middle height."""
        ry = rx if ry is None else ry
        rz = rx if rz is None else rz
        r = self.rng
        sm = self.sm()
        uo, vo = self.uvo()
        rows = []
        for j in range(rings + 1):
            ph = -math.pi / 2 + math.pi * j / rings
            row = []
            for i in range(seg):
                th = 2 * math.pi * (i + 0.5 * (j % 2)) / seg
                k = 1.0 + r.uniform(-rough, rough) if 0 < j < rings else 1.0
                row.append((x + rx * k * math.cos(ph) * math.cos(th), y + ry * k * math.cos(ph) * math.sin(th), z + rz * k * math.sin(ph)))
            rows.append(row)
        for j in range(rings):
            if j == 0 and not bottom:
                continue
            for i in range(seg):
                k = (i + 1) % seg
                a, bq, c, d = rows[j][i], rows[j][k], rows[j + 1][k], rows[j + 1][i]
                shade_k = 0.78 + 0.34 * (j + 0.5) / rings
                w0 = wind * (0.4 + 0.6 * j / rings)
                self.face((a, bq, c, d), mat, col=shade(col, shade_k), lod=lod, sm=sm, wind=w0,
                          uv=[(uo + i * 0.5, vo + j * 0.5), (uo + i * 0.5 + 0.5, vo + j * 0.5), (uo + i * 0.5 + 0.5, vo + j * 0.5 + 0.5), (uo + i * 0.5, vo + j * 0.5 + 0.5)])

    # ------------------------------------------------------------------ walls
    def wall(self, w, h, mat="plaster", col=None, depth=0.24, gable=0.0, lod=0, uvo=None, back=None, backcol=None, thick=0.0):
        """A flat wall in the local x-z plane, facing -y, from (0, 0, 0) to (w, 0, h). Add openings to the returned
        Wall before the building is finished. gable = height of a centred triangular top."""
        wl = Wall(self, w, h, mat, C(col), depth, gable, lod, uvo or self.uvo(), back, backcol, thick)
        self._walls.append(wl)
        return wl

    def body(self, w, d, h, mat="plaster", col=None, x=0.0, y=None, z=0.0, depth=0.24, lod=0, floor=None, foot=True):
        """Four walls of a rectangular block w wide (x), d deep (y), h high, standing on z. Centred on x, and with
        its front wall at y = 0 unless y (the centre) is given. Returns a Body (front, right, back, left walls)."""
        y = d / 2 if y is None else y
        uo, vo = self.uvo()
        walls = []
        for k, (ox, oy, rz, ww, off) in enumerate(((x - w / 2, y - d / 2, 0, w, 0.0), (x + w / 2, y - d / 2, 90, d, w), (x + w / 2, y + d / 2, 180, w, w + d), (x - w / 2, y + d / 2, 270, d, 2 * w + d))):
            with self.at(ox, oy, z, rz=rz):
                walls.append(self.wall(ww, h, mat, col, depth=depth, lod=lod, uvo=(uo + off, vo + z)))
        if floor is not None:      # underside, for a storey that overhangs
            with self.at(x, y, z):
                self.quad((-w / 2, d / 2, 0), (w / 2, d / 2, 0), (w / 2, -d / 2, 0), (-w / 2, -d / 2, 0), floor, col="darkoak")
        bd = Body(self, w, d, h, x, y, z, walls)
        if foot:
            self.footprint(x - w / 2, y - d / 2, x + w / 2, y + d / 2, z + h)
        return bd

    def round(self, r0, h, r1=None, mat="masonry", col=None, x=0.0, y=0.0, z=0.0, seg=24, depth=0.3, lod=0, profile=None, foot=True):
        """A round tower shaft: radius r0 at the bottom, r1 at the top (or profile = [(z, r), ...]), centred on
        (x, y). Returns a Ring wall: add openings by compass angle (0 = front, 90 = right, 180 = back)."""
        r1 = r0 if r1 is None else r1
        profile = profile or [(0.0, r0), (h, r1)]
        with self.at(x, y, z):
            rg = Ring(self, profile, mat, C(col), depth, lod, seg, self.uvo())
        self._walls.append(rg)
        if foot:
            t = self.tp((x, y, z))
            self.foot.append({"kind": "disc", "x": t[0], "y": t[1], "r": max(r for _, r in profile), "top": t[2] + h})
        return rg

    def polygon(self, n, r, h, mat="masonry", col=None, x=0.0, y=0.0, z=0.0, depth=0.26, lod=0, rot=None, foot=True, taper=1.0):
        """A many-sided tower shaft (n flat faces), 'r' to the corners. Returns a list of n Walls going round to
        the right. By default a CORNER points at the front; pass rot=0 to put face 0 squarely at the front.
        With taper < 1 the faces lean in and cross at the corners: for a tapered tower use parts_c.poly_tower."""
        rot = 180.0 / n if rot is None else rot
        walls = []
        uo, vo = self.uvo()
        side = 2 * r * math.sin(math.pi / n)
        ap = r * math.cos(math.pi / n)
        lean = math.degrees(math.atan2(ap * (1 - taper), h))
        for k in range(n):
            a = 360.0 * k / n + rot - 180.0 / n
            # face k spans corner angles a .. a + 360/n (compass, 0 = front); its left end as seen from outside:
            ca = rad(a)
            ox, oy = x + r * math.sin(ca), y - r * math.cos(ca)
            with self.at(ox, oy, z, rz=a + 180.0 / n):
                with self.at(rx=-lean):
                    walls.append(self.wall(side, h / math.cos(rad(lean)), mat, col, depth=depth, lod=lod, uvo=(uo + side * k, vo)))
        if foot:
            t = self.tp((x, y, z))
            self.foot.append({"kind": "disc", "x": t[0], "y": t[1], "r": r, "top": t[2] + h})
        return walls

    # ------------------------------------------------------------------ roofs
    def _courses(self, prof, course, lip):
        """Turn a roof section [(run, rise), ...] (eave to ridge) into overlapping tile courses: each course
        starts `lip` proud of the plane and dies into the start of the next, which gives real shadow lines."""
        if not course or course <= 0:
            return [(p[0], p[1]) for p in prof], [0.0] + [math.hypot(prof[i][0] - prof[i - 1][0], prof[i][1] - prof[i - 1][1]) for i in range(1, len(prof))]
        out = []
        for i in range(len(prof) - 1):
            a, b = prof[i], prof[i + 1]
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if L < 1e-6:
                continue
            n = max(1, round(L / course))
            dx, dz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            nx, nz = -dz, dx                       # outward normal of a section that climbs toward +run
            if nz < 0:
                nx, nz = -nx, -nz
            for k in range(n):
                t0, t1 = k / n, (k + 1) / n
                out.append((a[0] + (b[0] - a[0]) * t0 + nx * lip, a[1] + (b[1] - a[1]) * t0 + nz * lip))
                out.append((a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1))
        return out, None

    def gable_roof(self, w, d, pitch=45.0, mat="tiles", col=None, x=0.0, y=0.0, z=0.0, ridge="x", eave=0.45, verge=0.35, thick=0.16,
                   course=0.42, lip=0.045, sag=0.0, half=False, section=None, soffit="planks", soffit_col="darkoak", barge=True,
                   barge_col=None, ridge_roll=True, hip=0.0, lod=0):
        """A pitched roof over a w (x) by d (y) block whose wall tops are at z, centred on (x, y).
        ridge = 'x' (ridge runs left-right, slopes face front and back) or 'y'. pitch in degrees, or give
        section = [(run, rise), ...] from the wall line to the ridge for gambrels and bell-cast eaves.
        half=True makes a single slope (a lean-to): with ridge 'x' its HIGH edge runs along the line y (from
        x - w/2 to x + w/2) and it falls toward -y over the depth d, so z is the height of its low edge.
        sag lowers the middle of the ridge. Returns the rise of the ridge above z."""
        col = C(col)
        span, length = (d, w) if ridge == "x" else (w, d)
        run = span if half else span / 2
        if section is None:
            section = [(0.0, 0.0), (run, run * math.tan(rad(pitch)))]
        rise = section[-1][1]
        # extend down past the wall line for the eave
        s0 = (section[1][1] - section[0][1]) / max(section[1][0] - section[0][0], 1e-6)
        prof = [(-eave, -eave * s0)] + list(section[1:])
        prof = [(p[0] if i else p[0], p[1]) for i, p in enumerate(prof)]
        stepped, _ = self._courses(prof, course, lip)
        nseg = 4 if sag > 0 else 1
        xs = [-length / 2 - verge + (length + 2 * verge) * i / nseg for i in range(nseg + 1)]
        sagz = lambda xx, rz: -sag * (1 - (2 * xx / (length + 2 * verge)) ** 2) * (rz / max(rise, 1e-6)) if sag > 0 else 0.0
        uo, vo = self.uvo()
        rot = 0.0 if ridge == "x" else 90.0
        with self.at(x, y, z, rz=rot):
            sides = (1,) if half else (1, -1)
            for sgn in sides:
                # local: ridge along x; this slope's wall line at yy = -sgn*span/2 (or -run for half)
                y_wall = -run if half else -sgn * span / 2
                yy = lambda r_: y_wall + sgn * r_ if not half else y_wall + r_
                acc = 0.0
                for k in range(len(stepped) - 1):
                    (ra, za), (rb, zb) = stepped[k], stepped[k + 1]
                    L = math.hypot(rb - ra, zb - za)
                    ck = shade(col, self.r(0.88, 1.08))
                    for i in range(nseg):
                        xa, xb = xs[i], xs[i + 1]
                        p = [(xa, yy(ra), za + sagz(xa, max(za, 0))), (xb, yy(ra), za + sagz(xb, max(za, 0))), (xb, yy(rb), zb + sagz(xb, max(zb, 0))), (xa, yy(rb), zb + sagz(xa, max(zb, 0)))]
                        if sgn < 0 and not half:
                            p = [p[1], p[0], p[3], p[2]]
                        uvq = [(uo + xa, vo + acc), (uo + xb, vo + acc), (uo + xb, vo + acc + L), (uo + xa, vo + acc + L)]
                        if sgn < 0 and not half:
                            uvq = [uvq[1], uvq[0], uvq[3], uvq[2]]
                        self.quad(*p, mat, col=ck, lod=lod, uv=uvq)
                    acc += L
                # underside and edge thickness
                (r0_, z0_), (r1_, z1_) = prof[0], prof[-1]
                dn = thick
                for i in range(nseg):
                    xa, xb = xs[i], xs[i + 1]
                    q = [(xa, yy(r0_), z0_ - dn + sagz(xa, 0)), (xb, yy(r0_), z0_ - dn + sagz(xb, 0)), (xb, yy(r1_), z1_ - dn + sagz(xb, z1_)), (xa, yy(r1_), z1_ - dn + sagz(xa, z1_))]
                    if not (sgn < 0 and not half):
                        q = [q[1], q[0], q[3], q[2]]
                    self.quad(*q, soffit, col=soffit_col, lod=lod)
                    # eave fascia
                    e = [(xa, yy(r0_), z0_ - dn + sagz(xa, 0)), (xb, yy(r0_), z0_ - dn + sagz(xb, 0)), (xb, yy(stepped[0][0]), stepped[0][1] + sagz(xb, 0)), (xa, yy(stepped[0][0]), stepped[0][1] + sagz(xa, 0))]
                    if sgn < 0 and not half:
                        e = [e[1], e[0], e[3], e[2]]
                    self.quad(*e, soffit, col=soffit_col, lod=lod)
                # verges (the edges over the gable ends) and their barge boards
                for xe, flip in ((xs[0], False), (xs[-1], True)):
                    v = [(xe, yy(r0_), z0_ - dn), (xe, yy(r1_), z1_ - dn + sagz(xe, z1_)), (xe, yy(r1_), z1_ + sagz(xe, z1_) + lip), (xe, yy(r0_), z0_ + lip)]
                    if flip == (sgn < 0 and not half):          # (so that they face out over the gable)
                        v = list(reversed(v))
                    self.quad(*v, soffit, col=soffit_col, lod=lod)
                    if barge:
                        off = -0.04 if not flip else 0.04
                        self.beam((xe + off, yy(r0_), z0_ - dn * 0.4), (xe + off, yy(r1_), z1_ - dn * 0.4 + sagz(xe, z1_)), w=thick + 0.14, h=0.07, mat="planks",
                                  col=barge_col if barge_col is not None else "darkoak", lod=1, up=(1, 0, 0))
            if half:        # the tall back edge of a lean-to
                (r1_, z1_) = prof[-1]
                self.quad((xs[-1], -run + r1_, z1_ - thick), (xs[0], -run + r1_, z1_ - thick), (xs[0], -run + r1_, z1_ + lip), (xs[-1], -run + r1_, z1_ + lip), soffit, col=soffit_col, lod=lod)
            elif ridge_roll:
                with self.detail(1):
                    n = max(2, int((length + 2 * verge) / 0.42))
                    for i in range(n):
                        xa = -length / 2 - verge + (length + 2 * verge) * i / n
                        xb = xa + (length + 2 * verge) / n * 0.96
                        xm = (xa + xb) / 2
                        zz = rise + sagz(xm, rise)
                        self.beam((xa, 0, zz + 0.03), (xb, 0, zz + 0.05), w=0.26, h=0.14, mat=mat, col=shade(col, self.r(0.82, 1.0)), lod=1, caps=True)
        return rise

    def loop_roof(self, w, d, pitch=45.0, mat="tiles", col=None, x=0.0, y=0.0, z=0.0, eave=0.4, thick=0.14, course=0.42, lip=0.045,
                  section=None, soffit="planks", soffit_col="darkoak", lod=0, top=None):
        """A hipped roof (or a pyramid when w == d) over a w by d block whose wall tops are at z: every side
        slopes. section = [(run, rise), ...] overrides the straight pitch (for bell-cast or mansard shapes).
        Returns the rise."""
        col = C(col)
        run = min(w, d) / 2
        if section is None:
            section = [(0.0, 0.0), (run, run * math.tan(rad(pitch)))]
        s0 = (section[1][1] - section[0][1]) / max(section[1][0] - section[0][0], 1e-6)
        prof = [(-eave, -eave * s0)] + list(section[1:])
        stepped, _ = self._courses(prof, course, lip)
        uo, vo = self.uvo()
        hw, hd = w / 2, d / 2

        def loop(inset, zz):
            a, b = max(hw - inset, 0.0), max(hd - inset, 0.0)
            return [(-a, -b, zz), (a, -b, zz), (a, b, zz), (-a, b, zz)]

        with self.at(x, y, z):
            acc = 0.0
            for k in range(len(stepped) - 1):
                (ra, za), (rb, zb) = stepped[k], stepped[k + 1]
                A, Bq = loop(ra, za), loop(rb, zb)
                L = math.hypot(rb - ra, zb - za)
                per = 0.0
                ck = shade(col, self.r(0.88, 1.08))
                for i in range(4):
                    j = (i + 1) % 4
                    side = math.hypot(A[j][0] - A[i][0], A[j][1] - A[i][1])
                    sideb = math.hypot(Bq[j][0] - Bq[i][0], Bq[j][1] - Bq[i][1])
                    off = (side - sideb) / 2
                    self.face((A[i], A[j], Bq[j], Bq[i]), mat, col=ck, lod=lod,
                              uv=[(uo + per, vo + acc), (uo + per + side, vo + acc), (uo + per + side - off, vo + acc + L), (uo + per + off, vo + acc + L)])
                    per += 2.3 + side
                acc += L
            # soffit ring under the eaves
            (r0_, z0_) = prof[0]
            A, Bq = loop(r0_, z0_ - thick), loop(0.0, -thick + 0.0)
            E = loop(stepped[0][0], stepped[0][1])
            for i in range(4):
                j = (i + 1) % 4
                self.face((A[j], A[i], Bq[i], Bq[j]), soffit, col=soffit_col, lod=lod)
                self.face((A[i], A[j], E[j], E[i]), soffit, col=soffit_col, lod=lod)
            if top is not None and section[-1][0] < run - 1e-6:      # flat or capped top for a truncated section
                T = loop(section[-1][0], section[-1][1])
                self.face(T, top, col=col, lod=lod)
        return section[-1][1]

    def cone_roof(self, r, h, mat="slate", col=None, x=0.0, y=0.0, z=0.0, seg=20, eave=0.4, flare=0.35, course=0.5, lip=0.05,
                  smooth=True, soffit="planks", soffit_col="darkoak", lod=0, section=None, finial=True):
        """A conical (or with smooth=False and seg = n, an n-sided) spire roof over a round shaft of radius r whose
        wall top is at z. flare = how far the eave kicks out flatter than the cone (bell-cast). h = its height.
        section = [(radius, z), ...] from the eave up overrides the shape (onion and ogee caps)."""
        col = C(col)
        with self.at(x, y, z):
            if section is None:
                re = r + eave
                k = 0.22
                section = [(re, -eave * (h / r) * (1.0 - flare) * 0.9), (r * (1 - k) + 0.0, h * k * (1.0 - flare * 0.55) + 0.0), (0.0, h)]
            # convert (radius, z) from the eave up into a climbing section for the course stepper
            sec = [(section[0][0] - p[0], p[1]) for p in section]
            stepped, _ = self._courses(sec, course, lip)
            prof = [(max(section[0][0] - run, 0.0), zz) for run, zz in stepped]
            cols = [shade(col, self.r(0.86, 1.08)) for _ in range(len(prof) - 1)]
            self.revolve(prof, mat, col=col, lod=lod, seg=seg, smooth=smooth, rref=section[0][0], cols=cols)
            # underside of the eave
            self.disc(section[0][0], soffit, col=soffit_col, lod=lod, seg=seg, z=section[0][1] - 0.02, r_in=max(r - 0.05, 0.0), down=True)
            if prof[0][1] > section[0][1] - 0.02 + 1e-4:        # a fascia closes the gap under the lowest course
                self.revolve([(section[0][0], section[0][1] - 0.02), (prof[0][0], prof[0][1])], soffit, col=soffit_col, lod=lod, seg=seg, smooth=smooth, rref=section[0][0])
            if finial:
                with self.detail(1):
                    self.revolve([(0.10, h - 0.25), (0.07, h + 0.05), (0.16, h + 0.22), (0.16, h + 0.34), (0.05, h + 0.5), (0.035, h + 1.3), (0.0, h + 1.45)], "metal", col="copper", seg=8)
        return h

    # ------------------------------------------------------------------ markers
    def footprint(self, x0, y0, x1, y1, top):
        """Tell the town what ground this building stands on (local rectangle, and the height of its top)."""
        c = [self.tp((x0, y0, 0)), self.tp((x1, y0, 0)), self.tp((x1, y1, 0)), self.tp((x0, y1, 0))]
        self.foot.append({"kind": "rect", "pts": [[round(p[0], 3), round(p[1], 3)] for p in c], "top": round(self.tp((0, 0, top))[2], 3)})

    def pad(self, x=0.0, y=0.0, z=0.0, radius=1.6, face=0.0, approach=None, name=None):
        """A place the rider can land: the centre of a clear, level floor (local point), `radius` of clear floor,
        `face` = the compass direction (degrees in the local frame: 0 = toward local -y) she looks once landed,
        approach = the direction she arrives from the air travelling toward (defaults to opposite of face)."""
        p = self.tp((x, y, z))
        f = self.heading(face)
        self.pads.append({"pos": [round(v, 3) for v in p], "radius": radius, "face": round(f, 1),
                          "approach": round(self.heading(approach) if approach is not None else (f + 180.0) % 360.0, 1), "name": name})

    def smoke(self, x=0.0, y=0.0, z=0.0, strength=1.0):
        """Where a chimney breathes."""
        self.smokes.append({"pos": [round(v, 3) for v in self.tp((x, y, z))], "strength": strength})

    def lamp(self, x=0.0, y=0.0, z=0.0, strength=1.0):
        self.lamps.append({"pos": [round(v, 3) for v in self.tp((x, y, z))], "strength": strength})

    # ------------------------------------------------------------------ finishing
    def finish(self):
        for wl in self._walls:
            if not wl.done:
                wl.emit()


class Body:
    def __init__(self, b, w, d, h, x, y, z, walls):
        self.b, self.w, self.d, self.h, self.x, self.y, self.z = b, w, d, h, x, y, z
        self.front, self.right, self.back, self.left = walls
        self.walls = walls

    def gable(self, ridge="x", pitch=45.0, **kw):
        """Roof this block with a gable roof (see Building.gable_roof); raises the two end walls into gables."""
        span = self.d if ridge == "x" else self.w
        if kw.get("section"):
            rise = kw["section"][-1][1]
        else:
            rise = (span if kw.get("half") else span / 2) * math.tan(rad(pitch))
        if not kw.get("half"):
            for wl in ((self.left, self.right) if ridge == "x" else (self.front, self.back)):
                wl.gable = rise - 0.03
                wl.gable_section = kw.get("section")
        x0, y0 = self.x, self.y
        if kw.get("half"):          # a lean-to over the whole block: its high edge along the back (or the left) wall
            if ridge == "x":
                y0 = self.y + self.d / 2
            else:
                x0 = self.x - self.w / 2
        return self.b.gable_roof(self.w, self.d, pitch, x=x0, y=y0, z=self.z + self.h, ridge=ridge, **kw)

    def hip(self, pitch=40.0, **kw):
        return self.b.loop_roof(self.w, self.d, pitch, x=self.x, y=self.y, z=self.z + self.h, **kw)

    @property
    def top(self):
        return self.z + self.h


def _grid(cuts, length, cell):
    """Cut positions plus enough evenly spaced extra ones that no span is much longer than `cell`."""
    cuts = sorted(cuts)
    out = []
    for a, b in zip(cuts, cuts[1:]):
        out.append(a)
        n = int((b - a) / cell + 0.35)
        for k in range(1, n):
            out.append(a + (b - a) * k / n)
    out.append(cuts[-1])
    return out


class _Surface:
    """Shared machinery of flat and round walls: a grid over (u, z) with holes, reveals and panes."""

    def _init(self, b, mat, col, depth, lod, uvo):
        self.b, self.mat, self.col, self.depth, self.lod, self.uvo = b, mat, col, depth, lod, uvo
        self.m = b._m.copy()
        self.ops = []
        self.deco = []
        self.done = False
        self.cell = 1.5

    def opening(self, u, z, w, h, arch=0.0, depth=None, pane="glass", pane_col=None, reveal=None, reveal_col=None):
        """Cut a hole centred on u (metres along the wall), bottom at z, w wide and h high in all; arch = how much
        of that height is a curved top. pane = material of what closes it at the back (None leaves it open)."""
        op = {"u0": u - w / 2, "u1": u + w / 2, "z0": z, "z1": z + h, "arch": min(arch, h * 0.8), "d": self.depth if depth is None else depth,
              "pane": pane, "pane_col": pane_col, "reveal": reveal, "reveal_col": reveal_col, "u": u, "w": w, "h": h, "z": z}
        self.ops.append(op)
        return op

    def add(self, fn):
        """Run fn() later, after the wall is cut, in the wall's own frame."""
        self.deco.append(fn)

    @contextmanager
    def on(self, u, z=0.0):
        """Work in a frame sitting on the wall at (u, z): x along the wall, -y out of it, z up."""
        with self.b.frame(self.m @ self._local(u, z)):
            yield self.b

    @contextmanager
    def onu(self, u, z=0.0):
        """As `on`, but always by metres along the wall (round walls: metres of arc at the mean radius)."""
        with self.b.frame(self.m @ self._local(u, z)):
            yield self.b

    def U(self, pos):
        """Metres along the wall for a position given the natural way (metres on a flat wall, degrees on a round one)."""
        return pos

    def _in_hole(self, u, z):
        for op in self.ops:
            if op["u0"] - 1e-6 < u < op["u1"] + 1e-6 and op["z0"] - 1e-6 < z < op["z1"] + 1e-6:
                return True
        return False

    def _emit_openings(self):
        b = self.b
        for op in self.ops:
            u0, u1, z0, z1, d, arch = op["u0"], op["u1"], op["z0"], op["z1"], op["d"], op["arch"]
            zs = z1 - arch
            uc = (u0 + u1) / 2
            inw = self._inward(uc)
            S = self._S
            In = lambda u, z: vadd(S(u, z), vmul(inw, d))
            rmat = op["reveal"] or self.mat
            rcol = op["reveal_col"] if op["reveal_col"] is not None else shade(self.col, 0.86)
            # jambs, sill
            b.quad(S(u0, z0), In(u0, z0), In(u0, zs), S(u0, zs), rmat, col=rcol, lod=self.lod)
            b.quad(In(u1, z0), S(u1, z0), S(u1, zs), In(u1, zs), rmat, col=rcol, lod=self.lod)
            b.quad(S(u0, z0), S(u1, z0), In(u1, z0), In(u0, z0), rmat, col=shade(rcol, 1.1), lod=self.lod)
            if arch > 1e-4:
                n = 8
                pts = [(uc - (u1 - u0) / 2 * math.cos(math.pi * i / n), zs + arch * math.sin(math.pi * i / n)) for i in range(n + 1)]
                for i in range(n):
                    (ua, za), (ub, zb) = pts[i], pts[i + 1]
                    b.quad(In(ua, za), In(ub, zb), S(ub, zb), S(ua, za), rmat, col=shade(rcol, 0.92), lod=self.lod)
                    corner = (u0, z1) if i < n // 2 else (u1, z1)
                    uo, vo = self.uvo
                    tri = [corner, pts[i], pts[i + 1]]
                    b.face([S(*t) for t in tri], self.mat, col=self.col, lod=self.lod, uv=[(uo + t[0], vo + t[1]) for t in tri])
            else:
                b.quad(In(u0, z1), In(u1, z1), S(u1, z1), S(u0, z1), rmat, col=shade(rcol, 0.8), lod=self.lod)
            if op["pane"]:
                pc = op["pane_col"]
                b.quad(In(u0, z0), In(u1, z0), In(u1, z1), In(u0, z1), op["pane"], col=pc, lod=self.lod,
                       uv=[(0, 0), (u1 - u0, 0), (u1 - u0, z1 - z0), (0, z1 - z0)])

    def _finish(self):
        self.done = True
        for fn in self.deco:
            with self.b.frame(self.m):
                fn()


class Wall(_Surface):
    def __init__(self, b, w, h, mat, col, depth, gable, lod, uvo, back, backcol, thick):
        self._init(b, mat, col, depth, lod, uvo)
        self.w, self.h, self.gable, self.back, self.backcol, self.thick = w, h, gable, back, backcol, thick
        self.gable_section = None

    def _S(self, u, z):
        return (u, 0.0, z)

    def _inward(self, u):
        return (0.0, 1.0, 0.0)

    def _local(self, u, z):
        return _mat4(u, 0.0, z)

    def emit(self):
        b = self.b
        uo, vo = self.uvo
        with b.frame(self.m):
            us = _grid({0.0, self.w} | {min(max(o[k], 0.0), self.w) for o in self.ops for k in ("u0", "u1")}, self.w, self.cell)
            zs = _grid({0.0, self.h} | {min(max(o[k], 0.0), self.h) for o in self.ops for k in ("z0", "z1")}, self.h, self.cell)
            for j in range(len(zs) - 1):
                za, zb = zs[j], zs[j + 1]
                if zb - za < 1e-6:
                    continue
                for i in range(len(us) - 1):
                    ua, ue = us[i], us[i + 1]
                    if ue - ua < 1e-6 or self._in_hole((ua + ue) / 2, (za + zb) / 2):
                        continue
                    b.quad((ua, 0, za), (ue, 0, za), (ue, 0, zb), (ua, 0, zb), self.mat, col=self.col, lod=self.lod,
                           uv=[(uo + ua, vo + za), (uo + ue, vo + za), (uo + ue, vo + zb), (uo + ua, vo + zb)])
            if self.gable > 1e-6:
                if self.gable_section:
                    sec = self.gable_section
                    half = self.w / 2
                    pts = [(0.0, self.h)] + [(min(r_, half), self.h + z_ * (self.gable / sec[-1][1])) for r_, z_ in sec[1:]]
                    pts = pts + [(self.w - p[0], p[1]) for p in reversed(pts[:-1] if abs(pts[-1][0] - half) < 1e-6 else pts)]
                    poly = [(p[0], 0.0, p[1]) for p in pts]
                    # fan from the bottom-middle keeps it convex enough for gambrels
                    c = (half, 0.0, self.h)
                    ring = [(self.w, 0.0, self.h)] + list(reversed(poly[1:-1])) + [(0.0, 0.0, self.h)]
                    for i in range(len(ring) - 1):
                        t = [c, ring[i], ring[i + 1]]
                        b.face(t, self.mat, col=self.col, lod=self.lod, uv=[(uo + p[0], vo + p[2]) for p in t])
                else:
                    rows = max(1, int(self.gable / 1.2 + 0.5))
                    for j in range(rows):
                        ta, tb = j / rows, (j + 1) / rows
                        za, zb = self.h + self.gable * ta, self.h + self.gable * tb
                        la, ra = self.w / 2 * ta, self.w - self.w / 2 * ta
                        lb, rb = self.w / 2 * tb, self.w - self.w / 2 * tb
                        cols = max(1, int((ra - la) / 1.5 + 0.5))
                        for c in range(cols):
                            q = [(la + (ra - la) * c / cols, 0.0, za), (la + (ra - la) * (c + 1) / cols, 0.0, za),
                                 (lb + (rb - lb) * (c + 1) / cols, 0.0, zb), (lb + (rb - lb) * c / cols, 0.0, zb)]
                            b.face(q, self.mat, col=self.col, lod=self.lod, uv=[(uo + p[0], vo + p[2]) for p in q])
            if self.back:      # a free-standing wall: its other face and its top
                t = self.thick or 0.3
                b.quad((self.w, t, 0), (0, t, 0), (0, t, self.h), (self.w, t, self.h), self.back, col=self.backcol if self.backcol is not None else self.col, lod=self.lod)
                b.quad((0, 0, self.h), (self.w, 0, self.h), (self.w, t, self.h), (0, t, self.h), self.back, col=self.col, lod=self.lod)
                b.quad((0, t, 0), (0, 0, 0), (0, 0, self.h), (0, t, self.h), self.back, col=self.col, lod=self.lod)
                b.quad((self.w, 0, 0), (self.w, t, 0), (self.w, t, self.h), (self.w, 0, self.h), self.back, col=self.col, lod=self.lod)
            self._emit_openings()
        self._finish()


class Ring(_Surface):
    def __init__(self, b, profile, mat, col, depth, lod, seg, uvo):
        self._init(b, mat, col, depth, lod, uvo)
        self.profile = profile
        self.h = profile[-1][0]
        self.seg = seg
        self.rref = sum(r for _, r in profile) / len(profile)
        self.w = 2 * math.pi * self.rref

    def radius(self, z):
        p = self.profile
        if z <= p[0][0]:
            return p[0][1]
        for i in range(len(p) - 1):
            if z <= p[i + 1][0]:
                t = (z - p[i][0]) / max(p[i + 1][0] - p[i][0], 1e-9)
                return p[i][1] + (p[i + 1][1] - p[i][1]) * t
        return p[-1][1]

    def U(self, pos):
        return self.u_of(pos)

    def _in_hole(self, u, z):
        # (the wall closes on itself: an opening may straddle the seam at compass 0)
        return _Surface._in_hole(self, u, z) or _Surface._in_hole(self, u - self.w, z) or _Surface._in_hole(self, u + self.w, z)

    def u_of(self, deg):
        """Metres along the wall for a compass angle (0 = front, 90 = right ...)."""
        return rad(deg % 360.0) * self.rref

    def _S(self, u, z):
        a = u / self.rref
        r = self.radius(z)
        return (r * math.sin(a), -r * math.cos(a), z)

    def _inward(self, u):
        a = u / self.rref
        return (-math.sin(a), math.cos(a), 0.0)

    def _local(self, u, z):
        a = math.degrees(u / self.rref)
        return _mat4(rz=a) @ _mat4(0.0, -self.radius(z), z)

    def opening(self, deg, z, w, h, **kw):
        """As Wall.opening, but placed by compass angle in degrees."""
        return _Surface.opening(self, self.u_of(deg), z, w, h, **kw)

    @contextmanager
    def on(self, deg, z=0.0):
        with self.b.frame(self.m @ self._local(self.u_of(deg), z)):
            yield self.b

    def emit(self):
        b = self.b
        uo, vo = self.uvo
        sm = b.sm()
        with b.frame(self.m):
            us = {self.w * i / self.seg for i in range(self.seg + 1)}
            for o in self.ops:
                for k in ("u0", "u1"):
                    us.add(o[k] % self.w)
            us = sorted(us)
            zs = _grid({z for z, _ in self.profile} | {min(max(o[k], 0.0), self.h) for o in self.ops for k in ("z0", "z1")}, self.h, self.cell)
            S = self._S
            for j in range(len(zs) - 1):
                za, zb = zs[j], zs[j + 1]
                if zb - za < 1e-6:
                    continue
                for i in range(len(us) - 1):
                    ua, ub = us[i], us[i + 1]
                    if ub - ua < 1e-6 or self._in_hole((ua + ub) / 2, (za + zb) / 2):
                        continue
                    b.quad(S(ua, za), S(ub, za), S(ub, zb), S(ua, zb), self.mat, col=self.col, lod=self.lod, sm=sm,
                           uv=[(uo + ua, vo + za), (uo + ub, vo + za), (uo + ub, vo + zb), (uo + ua, vo + zb)])
            self._emit_openings()
        self._finish()
