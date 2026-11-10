"""Petalwake town kit, the Crown's parts: what the upper town of Larkhaven (prefix c_) needed beyond parts.py.

Everything here is written with kit primitives. Conventions as in parts.py: metres, compass degrees
(0 = front, 90 = right, 180 = back), detail levels 0 / 1 / 2.

  ring ............ b.round with its seam turned away from the front (works round a kit bug, see there)
  round_base, plinth ... the kit's base courses, left open in front of doors
  TaperWall, tbody, poly_tower ... battered square and many-sided towers whose faces are true trapezoids
  Shell, shell .... a roofless round wall with real thickness, a ragged skyline and through-openings
  rect_sides, poly_sides ... frames along the sides of a rectangle / polygon (for parapets, corbels, rails)
  corbels, corbel_row, battlements, round_battlements, lathe, stone_walk, deck_arc, rail_arc, shed_roof
  vault ........... the inside of an arched passage
  xprism .......... a convex section extruded sideways (buttresses, cheeks, kerbs)
  arch_stones, buttress, crow_steps, stack (tall chimneys), garden_wall, gate_piers, wood_gate, outside_stair
  yard (front-garden walls with a gate), oculus, well, pergola
  dome_section, ribs, armillary, vane, dove, banner, tuft, flowers, climber, lamp_post, hatch, slit
"""
import math

import kit
from kit import C, lerp, rad, shade, vadd, vmul, vsub

import parts as P

GRASS = "#8fc46a"
MOSS = "#7fa858"


# ---------------------------------------------------------------------------------------- small geometry helpers
def rect_sides(w, d, x=0.0, y=0.0):
    """The four sides of a w by d rectangle centred on (x, y) as [(ox, oy, rz, length), ...]: inside
    `with b.at(ox, oy, z, rz=rz)` x runs along the side from its left end (seen from outside) and -y points out.
    Order: front, right, back, left (as Body.walls)."""
    return [(x - w / 2, y - d / 2, 0.0, w), (x + w / 2, y - d / 2, 90.0, d), (x + w / 2, y + d / 2, 180.0, w), (x - w / 2, y + d / 2, 270.0, d)]


def poly_sides(n, r, rot=0.0, x=0.0, y=0.0):
    """As rect_sides for a regular n-gon of corner radius r. With rot = 0 side 0 squarely faces the front."""
    out = []
    side = 2 * r * math.sin(math.pi / n)
    for k in range(n):
        a = 360.0 * k / n + rot - 180.0 / n
        out.append((x + r * math.sin(rad(a)), y - r * math.cos(rad(a)), a + 180.0 / n, side))
    return out


def polar(r, deg, z=0.0):
    """The point at radius r and compass angle deg."""
    return (r * math.sin(rad(deg)), -r * math.cos(rad(deg)), z)


def xprism(b, prof, x0, x1, mat, col=None, lod=0, caps=True, uvo=None, skip=()):
    """Extrude a convex outline in the y-z plane [(y, z), ...] (anticlockwise seen from +x) along x from x0 to
    x1. skip = indices of outline edges to leave out (sides that are hidden)."""
    uo, vo = uvo or b.uvo()
    n = len(prof)
    acc = 0.0
    for i in range(n):
        (ya, za), (yb, zb) = prof[i], prof[(i + 1) % n]
        L = math.hypot(yb - ya, zb - za)
        if i not in skip and L > 1e-6:
            b.quad((x0, ya, za), (x0, yb, zb), (x1, yb, zb), (x1, ya, za), mat, col=col, lod=lod,
                   uv=[(uo, vo + acc), (uo, vo + acc + L), (uo + (x1 - x0), vo + acc + L), (uo + (x1 - x0), vo + acc)])
        acc += L
    if caps:
        b.face([(x1, y, z) for y, z in prof], mat, col=col, lod=lod, uv=[(uo + y, vo + z) for y, z in prof])
        b.face([(x0, y, z) for y, z in reversed(prof)], mat, col=col, lod=lod, uv=[(uo + y, vo + z) for y, z in reversed(prof)])


def lathe(b, prof, mat, col=None, lod=0, seg=24, a0=0.0, a1=360.0, cols=None):
    """b.revolve one span at a time, so every horizontal arris of the profile [(radius, z), ...] stays crisp
    while the surface is still smooth round the axis (mouldings, flares, drums)."""
    for j in range(len(prof) - 1):
        if math.hypot(prof[j + 1][0] - prof[j][0], prof[j + 1][1] - prof[j][1]) < 1e-6:
            continue
        b.revolve([prof[j], prof[j + 1]], mat, col=cols[j] if cols else col, lod=lod, seg=seg, a0=a0, a1=a1)


# ---------------------------------------------------------------------------------------- round walls
def ring(b, r0, h, r1=None, mat="masonry", col=None, x=0.0, y=0.0, z=0.0, seg=24, depth=0.3, lod=0, profile=None, foot=True, seam=180.0):
    """b.round, with the wall's seam turned to compass `seam` (default: the back).

    Works round two kit bugs:
      1. Ring.emit only cuts the half of an opening that lies after the seam, and b.round puts the seam at
         compass 0, so a street door at the front of a round tower came out half walled up.
      2. parts.window / parts.door turn the compass angle into metres (s.U) and then call Ring.opening, which
         takes it for degrees and converts again: the hole was cut somewhere near the front while its frame,
         shutters and lintel sat (holeless) in the right place.
    On the wall returned here parts.window / parts.door work as documented (true compass degrees), and
    `wall.cut(deg, z, w, h, ...)` makes a bare opening by compass angle. Keep openings clear of `seam`."""
    with b.at(x, y, z, rz=seam):
        rg = b.round(r0, h, r1=r1, mat=mat, col=col, seg=seg, depth=depth, lod=lod, profile=profile, foot=foot)
    _fix_ring(rg, seam)
    return rg


def _fix_ring(rg, seam):
    rg.seam = seam
    rg.u_of = lambda deg: rad((deg - seam) % 360.0) * rg.rref
    rg.opening = lambda u, z, w, h, **kw: kit._Surface.opening(rg, u, z, w, h, **kw)            # metres, as parts.py passes
    rg.cut = lambda deg, z, w, h, **kw: kit._Surface.opening(rg, rg.u_of(deg), z, w, h, **kw)     # compass degrees


def slit(s, deg, z, w=0.2, h=1.0, col="!#1b1a1c", lod=1):
    """A blind arrow-slit on a round wall: a dark slot with a lintel and a sill stone. It costs nothing at the
    far level (a real opening re-cuts the whole wall), so it suits slender turrets that have many."""
    b = s.b
    u = s.U(deg)

    def deco():
        with s.onu(u, z):
            b.quad((-w / 2, -0.012, 0), (w / 2, -0.012, 0), (w / 2, -0.012, h), (-w / 2, -0.012, h), "paint", col=col, lod=lod)
            with b.detail(2):
                b.box(w + 0.22, 0.1, 0.14, "ashlar", col="stone", x=0, y=-0.02, z=h)
                b.box(w + 0.14, 0.12, 0.08, "ashlar", col="stone", x=0, y=-0.03, z=-0.08)
                for sx in (-1, 1):
                    b.box(0.07, 0.07, h, "ashlar", col="sand", x=sx * (w / 2 + 0.035), y=-0.012, z=0, top=False)

    s.add(deco)


def foot_disc(b, r, top, x=0.0, y=0.0, z=0.0):
    """Tell the town about a round piece of ground this building stands on, `top` high (what b.round does by
    itself): for a tower built of several stacked rings, which should count as one."""
    t = b.tp((x, y, z))
    b.foot.append({"kind": "disc", "x": t[0], "y": t[1], "r": r, "top": t[2] + top})


def round_base(b, r, h=0.9, out=0.25, mat="masonry", col="warm", skirt=3.0, seg=24, x=0.0, y=0.0, z=0.0, door=None):
    """parts.round_base with a way in: door = (compass degrees, width in metres) leaves the battered foot open
    in front of a door, so the door and its steps are not half buried in it (the hidden foundation still goes
    all the way round)."""
    with b.at(x, y, z):
        b.revolve([(r + out, -skirt), (r + out, 0.0)], mat, col=shade(col, 0.85), seg=seg, lod=0)
        prof = [(r + out, 0.0), (r + out * 0.9, h * 0.5), (r + 0.02, h)]
        if not door:
            b.revolve(prof, mat, col=col, seg=seg, lod=0)
            return
        half = math.degrees(door[1] / 2 / (r + out))
        a0, a1 = door[0] + half, door[0] - half + 360.0
        b.revolve(prof, mat, col=col, seg=max(3, int(round(seg * (a1 - a0) / 360.0))), a0=a0, a1=a1, lod=0)
        for a, flip in ((a0, False), (a1, True)):
            with b.at(rz=a):
                q = [(0, -r, 0), (0, -(r + out), 0), (0, -(r + out * 0.9), h * 0.5), (0, -(r + 0.02), h), (0, -r, h)]
                b.face(list(reversed(q)) if flip else q, mat, col=shade(col, 0.9), lod=0)


def plinth(body, h=0.7, out=0.07, mat="masonry", col="warm", skirt=3.0, doors=(), lod=0):
    """parts.plinth with doorways: doors = [(wall, metres along it, door width), ...] (wall = 'front', 'right',
    'back' or 'left') leaves the base course open in front of each door, so the door and its steps are not
    half buried in it. Works on a kit Body and on a TBody."""
    b = body.b
    with b.at(body.x, body.y, body.z):
        b.box(body.w + 2 * out, body.d + 2 * out, skirt, mat, col=shade(col, 0.85), y=0, z=-skirt, top=False, lod=lod)
    for name, (ox, oy, rz, L) in zip(("front", "right", "back", "left"), rect_sides(body.w, body.d, body.x, body.y)):
        gs = sorted((u - w / 2 - 0.32, u + w / 2 + 0.32) for (wn, u, w) in doors if wn == name)
        with b.at(ox, oy, body.z, rz=rz):
            runs, x = [], -out
            for (g0, g1) in gs:
                if g0 - x > 0.02:
                    runs.append((x, g0))
                x = g1
            if L + out - x > 0.02:
                runs.append((x, L + out))
            for (x0, x1) in runs:
                b.box(x1 - x0, out + 0.03, h, mat, col=col, x=(x0 + x1) / 2, y=-out / 2 + 0.015, z=0, lod=lod, sides="frl")


def poly_plinth(b, n, r, h=0.8, out=0.12, rot=0.0, mat="masonry", col="warm", skirt=3.0, doors=(), x=0.0, y=0.0, z=0.0, lod=0):
    """A base course and hidden foundation for a many-sided tower (corner radius r, as poly_tower), left open
    in front of doors: doors = [(face index, metres along that face, door width), ...]."""
    with b.at(x, y, z, rz=rot + 180.0 / n):
        b.revolve([((r + out) / math.cos(math.pi / n) * 1.0, -skirt), ((r + out) / math.cos(math.pi / n), 0.0)], mat, col=shade(col, 0.85), seg=n, smooth=False, lod=lod)
    ext = out * math.tan(math.pi / n) + 0.02
    for k, (ox, oy, rz, L) in enumerate(poly_sides(n, r, rot, x, y)):
        gs = sorted((u - w / 2 - 0.32, u + w / 2 + 0.32) for (fk, u, w) in doors if fk == k)
        with b.at(ox, oy, z, rz=rz):
            runs, xx = [], -ext
            for (g0, g1) in gs:
                if g0 - xx > 0.02:
                    runs.append((xx, g0))
                xx = g1
            if L + ext - xx > 0.02:
                runs.append((xx, L + ext))
            for (x0, x1) in runs:
                b.box(x1 - x0, out + 0.05, h, mat, col=col, x=(x0 + x1) / 2, y=-out / 2 + 0.025, z=0, lod=lod, sides="frl")


def cheeks(b, w, d, rise, mat="masonry", col=None, x=0.0, y=0.0, z=0.0, lod=0):
    """The two triangular wall-heads under the ends of a lean-to roof placed with shed_roof(w, d, ...) at the
    same (x, y, z): w = the width between the outer faces of the side walls."""
    for sx in (-1, 1):
        xx = x + sx * w / 2
        t = [(xx, y - d, z), (xx, y, z), (xx, y, z + rise)]
        b.face(t if sx > 0 else list(reversed(t)), mat, col=col, lod=lod)


class Shell(kit.Ring):
    """A roofless round wall with real thickness: outer face, inner face and the wall-head between. It can
    cover only an arc, its top can follow a ragged skyline, and openings made with pane=None go right through
    (you see sky). Make one with `shell(...)`; add openings exactly as on a kit Ring."""

    def setup(self, thick, span, skyline, head, head_col, core_col, inner_col, crumble, grass):
        self.thick, self.span, self.skyline = thick, span, skyline
        self.head, self.head_col, self.core_col, self.inner_col = head, head_col, core_col, inner_col
        self.crumble, self.grass = crumble, grass
        self.tops = []
        self.w = rad(span) * self.rref          # so parts that scatter along the wall stay on the arc

    def opening(self, u, z, w, h, **kw):
        """By metres along the wall (what parts.window / parts.door pass). Use `cut` for compass degrees."""
        return kit._Surface.opening(self, u, z, w, h, **kw)

    def cut(self, deg, z, w, h, **kw):
        """A bare opening by compass angle; pane=None goes right through the wall."""
        return kit._Surface.opening(self, self.u_of(deg), z, w, h, **kw)

    def top_at(self, deg):
        """Height of the wall-head (above the shell's base) at a true compass angle."""
        return min(self.h, self.skyline((deg - self.seam) % 360.0)) if self.skyline else self.h

    def emit(self):
        b = self.b
        uo, vo = self.uvo
        sm_o, sm_i = b.sm(), b.sm()
        rr = self.rref
        t = self.thick
        full = self.span >= 360.0 - 1e-6
        ub_end = rad(self.span) * rr
        nseg = max(1, int(round(self.seg * self.span / 360.0)))
        So = self._S

        def Si(u, z):
            a = u / rr
            r = self.radius(z) - t
            return (r * math.sin(a), -r * math.cos(a), z)

        through = [o for o in self.ops if not o["pane"]]

        def in_through(u, z):
            for op in through:
                if op["u0"] - 1e-6 < u < op["u1"] + 1e-6 and op["z0"] - 1e-6 < z < op["z1"] + 1e-6:
                    return True
            return False

        with b.frame(self.m):
            us = {ub_end * i / nseg for i in range(nseg + 1)}
            for o in self.ops:
                for k in ("u0", "u1"):
                    us.add(min(max(o[k], 0.0), ub_end))
            us = sorted(us)
            zs = kit._grid({z for z, _ in self.profile} | {min(max(o[k], 0.0), self.h) for o in self.ops for k in ("z0", "z1")}, self.h, self.cell)
            cols = []
            for i in range(len(us) - 1):
                ua, ub = us[i], us[i + 1]
                if ub - ua < 1e-6:
                    continue
                um = (ua + ub) / 2
                top = self.h
                if self.skyline:
                    top = min(self.h, max(0.0, self.skyline(math.degrees(um / rr))))
                    for op in self.ops:                      # never cut a column off inside one of its openings
                        if op["u0"] - 1e-6 < um < op["u1"] + 1e-6 and op["z0"] < top < op["z1"] + 0.25:
                            top = min(self.h, op["z1"] + 0.3)
                cols.append((ua, ub, top))
                if top < 1e-6:
                    continue
                rows = [z for z in zs if z < top - 1e-6] + [top]
                for j in range(len(rows) - 1):
                    za, zb = rows[j], rows[j + 1]
                    zm = (za + zb) / 2
                    if not self._in_hole(um, zm):
                        b.quad(So(ua, za), So(ub, za), So(ub, zb), So(ua, zb), self.mat, col=self.col, lod=self.lod, sm=sm_o,
                               uv=[(uo + ua, vo + za), (uo + ub, vo + za), (uo + ub, vo + zb), (uo + ua, vo + zb)])
                    if not in_through(um, zm):
                        b.quad(Si(ub, za), Si(ua, za), Si(ua, zb), Si(ub, zb), self.mat, col=self.inner_col, lod=self.lod, sm=sm_i,
                               uv=[(uo + 9 - ub, vo + za), (uo + 9 - ua, vo + za), (uo + 9 - ua, vo + zb), (uo + 9 - ub, vo + zb)])
                b.quad(So(ua, top), So(ub, top), Si(ub, top), Si(ua, top), self.head, col=shade(self.head_col, b.r(0.9, 1.08)), lod=self.lod)
            self.tops = cols
            # the broken faces where the wall-head steps, and the two ends of an arc
            n = len(cols)
            for i in range(n if full else n - 1):
                (_, u, ta), (_, _, tb) = cols[i], cols[(i + 1) % n]
                if abs(ta - tb) < 1e-6:
                    continue
                lo, hi = min(ta, tb), max(ta, tb)
                q = [So(u, lo), Si(u, lo), Si(u, hi), So(u, hi)]
                b.face(q if ta > tb else list(reversed(q)), self.mat, col=self.core_col, lod=self.lod)
            if not full and cols:
                u, top = cols[0][0], cols[0][2]
                if top > 1e-6:
                    b.quad(Si(u, 0), So(u, 0), So(u, top), Si(u, top), self.mat, col=self.core_col, lod=self.lod)
                u, top = cols[-1][1], cols[-1][2]
                if top > 1e-6:
                    b.quad(So(u, 0), Si(u, 0), Si(u, top), So(u, top), self.mat, col=self.core_col, lod=self.lod)
            # through-openings: reveals right through the wall, both faces cut
            rcol = shade(self.col, 0.84)
            for op in through:
                u0, u1, z0, z1, arch = op["u0"], op["u1"], op["z0"], op["z1"], op["arch"]
                zt = z1 - arch
                b.quad(So(u0, z0), Si(u0, z0), Si(u0, zt), So(u0, zt), self.mat, col=rcol, lod=self.lod)
                b.quad(Si(u1, z0), So(u1, z0), So(u1, zt), Si(u1, zt), self.mat, col=rcol, lod=self.lod)
                if z0 > 1e-6:
                    b.quad(So(u0, z0), So(u1, z0), Si(u1, z0), Si(u0, z0), self.mat, col=shade(rcol, 1.1), lod=self.lod)
                if arch > 1e-4:
                    na = 8
                    uc, hw = (u0 + u1) / 2, (u1 - u0) / 2
                    pts = [(uc - hw * math.cos(math.pi * i / na), zt + arch * math.sin(math.pi * i / na)) for i in range(na + 1)]
                    for i in range(na):
                        (ua, za), (ub, zb) = pts[i], pts[i + 1]
                        b.quad(Si(ua, za), Si(ub, zb), So(ub, zb), So(ua, za), self.mat, col=shade(rcol, 0.9), lod=self.lod)
                        corner = (u0, z1) if i < na // 2 else (u1, z1)
                        tri = [corner, pts[i], pts[i + 1]]
                        b.face([So(*p) for p in tri], self.mat, col=self.col, lod=self.lod, sm=sm_o, uv=[(uo + p[0], vo + p[1]) for p in tri])
                        b.face([Si(*p) for p in reversed(tri)], self.mat, col=self.inner_col, lod=self.lod, sm=sm_i)
                else:
                    b.quad(So(u1, z1), So(u0, z1), Si(u0, z1), Si(u1, z1), self.mat, col=shade(rcol, 0.8), lod=self.lod)
            allops, self.ops = self.ops, [o for o in self.ops if o["pane"]]
            self._emit_openings()
            self.ops = allops
            # loose stones and grass along the wall-head
            if self.crumble or self.grass:
                rng = b.rng
                for (ua, ub, top) in cols:
                    um, wd = (ua + ub) / 2, (ub - ua)
                    rmid = self.radius(top) - t / 2
                    with b.at(rz=math.degrees(um / rr)):
                        if self.crumble and rng.random() < self.crumble:
                            hh = rng.uniform(0.16, 0.42)
                            b.stone(wd * rng.uniform(0.55, 0.95), t * rng.uniform(0.6, 1.0), hh, mat=self.mat, col=self.col, lod=1 if rng.random() < 0.4 else 2,
                                    y=-(rmid + rng.uniform(-0.08, 0.08)), z=top, jitter=0.16)
                        elif self.grass and rng.random() < self.grass:
                            tuft(b, rng.uniform(-0.2, 0.2) * wd, -(rmid + rng.uniform(-0.25, 0.25) * t), top, r=rng.uniform(0.16, 0.3))
        self._finish()


def shell(b, r0, h, r1=None, thick=0.9, mat="masonry", col=None, x=0.0, y=0.0, z=0.0, seg=24, depth=0.3, lod=0, profile=None,
          arc=(0.0, 360.0), skyline=None, head="ivy", head_col=GRASS, core_col=None, inner_col=None, crumble=0.5, grass=0.6):
    """A Shell (see the class) on (x, y) from z up: outer radius r0 at the bottom to r1 at the top, `thick`
    through. arc = (a0, a1) true compass degrees it covers, a0 < a1 (a1 may pass 360). skyline = a list of
    (compass degrees, height) points the wall-head follows (heights above z, stepped per wall segment), or a
    function of the angle. head = the material of the wall-head ('ivy' = turf). crumble / grass = how likely
    a wall segment is to carry a loose stone / a tuft. Openings: parts.window / parts.door by compass degrees,
    or shell.cut(deg, z, w, h, pane=None) for a bare hole right through."""
    r1 = r0 if r1 is None else r1
    profile = profile or [(0.0, r0), (h, r1)]
    a0, a1 = arc
    col = C(col)
    with b.at(x, y, z, rz=a0):
        sh = Shell(b, profile, mat, col, depth, lod, seg, b.uvo())
    sh.seam = a0
    sh.u_of = lambda deg: rad((deg - a0) % 360.0) * sh.rref
    sky = None
    if skyline is not None:
        if callable(skyline):
            sky = lambda loc, f=skyline, a0=a0: f((loc + a0) % 360.0)
        else:
            pts = sorted(((d - a0) % 360.0, hh) for d, hh in skyline)

            def sky(loc, pts=pts):
                if loc <= pts[0][0]:
                    return pts[0][1]
                for i in range(len(pts) - 1):
                    if loc <= pts[i + 1][0]:
                        k = (loc - pts[i][0]) / max(pts[i + 1][0] - pts[i][0], 1e-9)
                        return pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k
                return pts[-1][1]
    sh.setup(thick, min(a1 - a0, 360.0), sky, head, C(head_col), C(core_col) if core_col is not None else shade(col, 0.8),
             C(inner_col) if inner_col is not None else shade(col, 0.9), crumble, grass)
    b._walls.append(sh)
    return sh


# ---------------------------------------------------------------------------------------- battered flat-sided towers
class TaperWall(kit.Wall):
    """A flat wall that narrows evenly toward its top (a trapezoid), so that the faces of a battered square or
    many-sided tower meet exactly at the corners. Positions along it are metres at its base; openings and the
    parts that dress them slide in with the taper. (Half-timbering does not: keep that for straight walls.)"""

    def __init__(self, b, w, h, top_w, mat, col, depth, lod, uvo):
        kit.Wall.__init__(self, b, w, h, mat, C(col), depth, 0.0, lod, uvo, None, None, 0.0)
        self.top_w = top_w
        self.k = (1.0 - top_w / w) / h

    def _sq(self, u, z):
        return self.w / 2 + (u - self.w / 2) * (1.0 - self.k * z)

    def _S(self, u, z):
        return (self._sq(u, z), 0.0, z)

    def _local(self, u, z):
        return kit._mat4(self._sq(u, z), 0.0, z)

    def width(self, z):
        return self.w * (1.0 - self.k * z)

    def emit(self):
        b = self.b
        uo, vo = self.uvo
        S = self._S
        with b.frame(self.m):
            us = kit._grid({0.0, self.w} | {min(max(o[k], 0.0), self.w) for o in self.ops for k in ("u0", "u1")}, self.w, self.cell)
            zs = kit._grid({0.0, self.h} | {min(max(o[k], 0.0), self.h) for o in self.ops for k in ("z0", "z1")}, self.h, self.cell)
            for j in range(len(zs) - 1):
                za, zb = zs[j], zs[j + 1]
                if zb - za < 1e-6:
                    continue
                for i in range(len(us) - 1):
                    ua, ue = us[i], us[i + 1]
                    if ue - ua < 1e-6 or self._in_hole((ua + ue) / 2, (za + zb) / 2):
                        continue
                    b.quad(S(ua, za), S(ue, za), S(ue, zb), S(ua, zb), self.mat, col=self.col, lod=self.lod,
                           uv=[(uo + ua, vo + za), (uo + ue, vo + za), (uo + ue, vo + zb), (uo + ua, vo + zb)])
            self._emit_openings()
        self._finish()


class TBody:
    """What tbody returns: .front .right .back .left (TaperWalls), .w .d at the base, .h, and half(z)."""

    def __init__(self, b, w, d, h, inset, x, y, z, walls):
        self.b, self.w, self.d, self.h, self.inset, self.x, self.y, self.z = b, w, d, h, inset, x, y, z
        self.front, self.right, self.back, self.left = walls
        self.walls = walls

    def half(self, zz):
        """Half-width and half-depth of the block at height zz above its base."""
        k = self.inset * zz / self.h
        return self.w / 2 - k, self.d / 2 - k

    @property
    def top(self):
        return self.z + self.h


def tbody(b, w, d, h, inset=0.2, mat="masonry", col=None, x=0.0, y=None, z=0.0, depth=0.26, lod=0, foot=True):
    """As b.body, but battered: every wall leans in so the block is `inset` narrower on each side at the top.
    Centred on x, front wall at y = 0 unless y (the centre) is given."""
    y = d / 2 if y is None else y
    uo, vo = b.uvo()
    lean = math.degrees(math.atan2(inset, h))
    H = math.hypot(h, inset)
    walls = []
    for (ox, oy, rz, ww), off in zip(rect_sides(w, d, x, y), (0.0, w, w + d, 2 * w + d)):
        with b.at(ox, oy, z, rz=rz):
            with b.at(rx=-lean):
                wl = TaperWall(b, ww, H, ww - 2 * inset, mat, col, depth, lod, (uo + off, vo + z))
        b._walls.append(wl)
        walls.append(wl)
    if foot:
        b.footprint(x - w / 2, y - d / 2, x + w / 2, y + d / 2, z + h)
    return TBody(b, w, d, h, inset, x, y, z, walls)


def poly_tower(b, n, r, h, taper=1.0, mat="masonry", col=None, x=0.0, y=0.0, z=0.0, depth=0.26, lod=0, rot=0.0, foot=True):
    """As b.polygon (an n-sided shaft, r to the corners), but with taper < 1 the faces are true trapezoids
    that meet at the corners, and by default (rot = 0) face 0 squarely faces the front. Returns the n walls,
    going round to the right; wall k looks toward compass 360 k / n + rot."""
    uo, vo = b.uvo()
    ap = r * math.cos(math.pi / n)
    lean = math.degrees(math.atan2(ap * (1 - taper), h))
    H = math.hypot(h, ap * (1 - taper))
    walls = []
    for k, (ox, oy, rz, side) in enumerate(poly_sides(n, r, rot, x, y)):
        with b.at(ox, oy, z, rz=rz):
            with b.at(rx=-lean):
                wl = TaperWall(b, side, H, side * taper, mat, col, depth, lod, (uo + side * k, vo + z))
        b._walls.append(wl)
        walls.append(wl)
    if foot:
        t = b.tp((x, y, z))
        b.foot.append({"kind": "disc", "x": t[0], "y": t[1], "r": r, "top": t[2] + h})
    return walls


def tquoins(tb, mat="ashlar", col="stone", size=(0.56, 0.32, 0.46), z0=0.0, z1=None, proud=0.035, corners="frbl", lod=2):
    """parts.quoins for a battered block (TBody): the stones step in with the corner."""
    b = tb.b
    z1 = tb.h if z1 is None else z1
    L, S, H = size
    n = max(1, int((z1 - z0) / H))
    hh = (z1 - z0) / n
    cs = {"f": (-1, -1), "r": (1, -1), "b": (1, 1), "l": (-1, 1)}
    for key in corners:
        sx, sy = cs[key]
        for i in range(n):
            zz = z0 + hh * i
            hw, hd = tb.half(zz + hh / 2)
            lx, ly = (L, S) if i % 2 == 0 else (S, L)
            with b.at(tb.x + sx * (hw - lx / 2 + proud), tb.y + sy * (hd - ly / 2 + proud), tb.z + zz):
                b.stone(lx, ly, hh * 0.96, mat=mat, col=col, lod=lod, ch=0.12, jitter=0.05)


def tband(tb, zz, h=0.18, out=0.06, mat="ashlar", col="stone", lod=1):
    """parts.band for a battered block: a string course at height zz."""
    hw, hd = tb.half(zz)
    tb.b.box(2 * (hw + out), 2 * (hd + out), h, mat, col=col, x=tb.x, y=tb.y, z=tb.z + zz, lod=lod, bottom=True)


# ---------------------------------------------------------------------------------------- corbels, parapets, walks
def corbels(b, r, z, n=16, out=0.5, drop=0.6, w=0.26, steps=2, mat="ashlar", col="stone", lod=1, a0=0.0, a1=360.0):
    """A ring of stepped stone corbels under an overhang: their tops at height z, reaching from the wall at
    radius r out to r + out, `drop` deep. a0, a1 = the arc to cover."""
    for i in range(n):
        a = a0 + (a1 - a0) * (i + 0.5) / n
        with b.at(rz=a):
            _corbel(b, r, z, out, drop, w, steps, mat, col, lod)


def _corbel(b, r, z, out, drop, w, steps, mat, col, lod):
    hh = drop / steps
    for s in range(steps):
        o = out * (s + 1) / steps
        b.box(w, o + 0.06, hh, mat, col=shade(col, 0.92 + 0.08 * s), lod=lod, x=0.0, y=-(r + o / 2 - 0.03), z=z - drop + hh * s, sides="frl", top=s < steps - 1, bottom=True)


def corbel_row(b, length, z=0.0, n=None, out=0.4, drop=0.5, w=0.26, steps=2, mat="ashlar", col="stone", lod=1, x0=0.0):
    """A row of corbels along a flat wall: in the current frame the wall face is y = 0 from x0 to x0 + length
    and -y points out (use rect_sides / poly_sides frames). Tops at height z."""
    n = n or max(2, int(round(length / 0.7)))
    for i in range(n):
        with b.at(x0 + length * (i + 0.5) / n, 0, 0):
            _corbel(b, 0.0, z, out, drop, w, steps, mat, col, lod)


def battlements(b, sides, z=0.0, t=0.34, wall=0.55, h=0.65, merlon=0.75, gap=0.5, mat="masonry", col="warm", cap=True, gaps=None, lod=0, kerb=0.12):
    """Battlements along straight runs. sides = [(ox, oy, rz, length), ...] from rect_sides / poly_sides: the
    parapet's outer face stands on the side line and it is t thick inward. gaps = {side index: [(x0, x1), ...]}
    stretches left open (a landing approach, a stair head): only a low kerb there."""
    for si, (ox, oy, rz, L) in enumerate(sides):
        gs = sorted((gaps or {}).get(si, []))
        with b.at(ox, oy, z, rz=rz):
            runs, x = [], 0.0
            for (g0, g1) in gs:
                if g0 - x > 0.05:
                    runs.append((x, g0))
                x = g1
                if kerb:
                    b.box(g1 - g0, t, kerb, mat, col=col, x=(g0 + g1) / 2, y=t / 2, lod=lod)
            if L - x > 0.05:
                runs.append((x, L))
            for (x0, x1) in runs:
                run = x1 - x0
                b.box(run, t, wall, mat, col=col, x=(x0 + x1) / 2, y=t / 2, lod=lod)
                m = max(1, int(round((run + gap) / (merlon + gap))))
                mw = (run - gap * (m - 1)) / m
                if mw < 0.35:
                    m, mw = 1, run
                for i in range(m):
                    cx = x0 + mw / 2 + i * (mw + gap)
                    b.stone(mw, t, h, mat=mat, col=col, lod=1, x=cx, y=t / 2, z=wall, ch=0.1, jitter=0.06)
                    if cap:
                        b.box(mw + 0.07, t + 0.07, 0.07, "ashlar", col="stone", x=cx, y=t / 2, z=wall + h - 0.01, lod=2, bottom=True)


def round_battlements(b, r, z=0.0, n=None, t=0.34, wall=0.55, h=0.65, mat="masonry", col="warm", seg=24, gap=None, fill=0.56, cap=True, kerb=0.12):
    """parts.crenels for a round top, with an optional open stretch: gap = (a0, a1) compass degrees."""
    a0, a1 = (gap[1], gap[0] + 360.0) if gap else (0.0, 360.0)
    with b.at(z=z):
        nseg = max(3, int(round(seg * (a1 - a0) / 360.0)))
        b.revolve([(r, 0.0), (r, wall), (r - t, wall), (r - t, 0.0)], mat, col=col, seg=nseg, a0=a0, a1=a1, lod=0)
        if gap:
            for a, flip in ((a0, True), (a1, False)):
                with b.at(rz=a):
                    q = [(0, -r, 0), (0, -r + t, 0), (0, -r + t, wall), (0, -r, wall)]
                    b.face(list(reversed(q)) if flip else q, mat, col=col, lod=0)
            if kerb:
                b.revolve([(r, 0.0), (r, kerb), (r - t, kerb), (r - t, 0.0)], mat, col=col, seg=max(2, seg - nseg), a0=gap[0], a1=gap[1], lod=0)
        n = n or max(6, int(2 * math.pi * r / 1.25))
        m = max(2, int(round(n * (a1 - a0) / 360.0)))
        for i in range(m):
            a = a0 + (a1 - a0) * (i + 0.5) / m
            with b.at(rz=a):
                mw = 2 * math.pi * r / n * fill
                b.stone(mw, t, h, mat=mat, col=col, lod=1, y=-(r - t / 2), z=wall, ch=0.1, jitter=0.06)
                if cap:
                    b.box(mw + 0.07, t + 0.07, 0.07, "ashlar", col="stone", y=-(r - t / 2), z=wall + h - 0.01, lod=2, bottom=True)


def stone_walk(b, r_in, r_out, z, seg=24, floor="flagstone", floor_col="sand", mat="ashlar", col="stone", thick=0.2, drop=0.9, r_foot=None, x=0.0, y=0.0, a0=0.0, a1=360.0):
    """A stone walk round a tower, lighthouse fashion: a ring floor at height z from r_in out to r_out, on a
    moulded stone flare growing out of the shaft (radius r_foot, `drop` below the floor). No railing: add
    rail_arc / parts.railing. This is a landing place when it is wide enough: put a b.pad on it."""
    r_foot = r_in if r_foot is None else r_foot
    with b.at(x, y, z):
        nseg = max(3, int(round(seg * (a1 - a0) / 360.0)))
        ang = [a0 + (a1 - a0) * i / nseg for i in range(nseg + 1)]
        uo, vo = b.uvo()
        for i in range(nseg):
            q = [polar(r_in - 0.05, ang[i]), polar(r_out, ang[i]), polar(r_out, ang[i + 1]), polar(r_in - 0.05, ang[i + 1])]
            b.face(q, floor, col=floor_col, lod=0, uv=[(uo + p[0], vo + p[1]) for p in q])
        k = r_out - r_foot
        lathe(b, [(r_foot, -drop), (r_foot + k * 0.16, -drop * 0.86), (r_foot + k * 0.16, -drop * 0.72), (r_foot + k * 0.62, -thick - 0.16),
                  (r_out - 0.12, -thick - 0.03), (r_out - 0.12, -thick), (r_out, -thick), (r_out, 0.0)], mat, col=col, seg=nseg, a0=a0, a1=a1, lod=0)


def deck_arc(b, r_in, r_out, a0, a1, z=0.0, thick=0.14, seg=None, mat="planks", col="greyoak", edge_col="darkoak", lod=0):
    """A boarded deck in the shape of a ring sector (compass a0 to a1, a1 > a0) with its top at height z: for a
    veranda hung round part of a tower."""
    seg = seg or max(3, int(round((a1 - a0) / 12.0)))
    with b.at(z=z):
        b.revolve([(r_out, 0.0), (r_in, 0.0)], mat, col=col, seg=seg, a0=a0, a1=a1, lod=lod, smooth=False)
        b.revolve([(r_in, -thick), (r_out, -thick)], mat, col=shade(edge_col, 0.8), seg=seg, a0=a0, a1=a1, lod=lod, smooth=False)
        b.revolve([(r_out, -thick), (r_out, 0.0)], mat, col=edge_col, seg=seg, a0=a0, a1=a1, lod=lod)
        b.revolve([(r_in, 0.0), (r_in, -thick)], mat, col=edge_col, seg=seg, a0=a0, a1=a1, lod=lod)
        for a, flip in ((a0, True), (a1, False)):
            with b.at(rz=a):
                q = [(0, -r_out, -thick), (0, -r_in, -thick), (0, -r_in, 0), (0, -r_out, 0)]
                b.face(list(reversed(q)) if flip else q, mat, col=edge_col, lod=lod)


def shed_roof(b, w, d, pitch=20.0, z=0.0, x=0.0, y=0.0, **kw):
    """A lean-to roof against a wall, pinned down the plain way: in the current frame its high edge runs along
    the wall line `y` (from x - w/2 to x + w/2) and it slopes down toward -y over a depth d, reaching height z
    at its low edge (the wall-plate of the lean-to). Turn the frame (b.at(rz=...)) for other sides. Returns
    the rise. (kit gable_roof(half=True) is not centred on (x, y) as documented; this is what it does.)"""
    return b.gable_roof(w, d, pitch, x=x, y=y, z=z, ridge="x", half=True, **kw)


def rail_arc(b, r, a0, a1, z=0.0, h=1.0, style="iron", col="darkoak", n=None, knobs=None, posts_at=1.3, lod=1, mat="timber"):
    """A railing round an arc of radius r from compass a0 to a1 (a1 > a0; the rest is left open for the rider).
    knobs = a colour for a ball finial on each post (brass on an iron rail looks right). For a painted rail
    give mat="planks": the timber texture is too dark to take a pale paint."""
    n = n or max(3, int(round(2 * math.pi * r * (a1 - a0) / 360.0 / posts_at)))
    pts = [polar(r, a0 + (a1 - a0) * i / n, z) for i in range(n + 1)]
    closed = (a1 - a0) >= 360.0 - 1e-6
    P.railing(b, pts[:-1] if closed else pts, h=h, style=style, col=col, mat=mat, closed=closed, posts_at=posts_at * 1.4, lod=lod)
    if knobs:
        with b.detail(2):
            for p in (pts[:-1] if closed else pts):
                b.blob(0.055, 0.055, 0.055, mat="metal", col=knobs, x=p[0], y=p[1], z=p[2] + h + 0.09, seg=5, rings=2, rough=0.0)


# ---------------------------------------------------------------------------------------- passages, masses
def vault(b, w, h, arch, length, n=5, mat="masonry", col="warm", floor="cobble", floor_col=None, z0=0.0, lod=0, skirt=3.0, seg=8):
    """The inside of an arched passage: in the current frame its mouth is the opening centred on x = 0 in the
    wall plane y = 0 (w wide, h high in all, the top `arch` of that curved, exactly as a kit opening) and it
    runs to y = length. n slices, so the middle is properly dark. floor = paving material (with a hidden
    foundation under it), or None."""
    hw, zt = w / 2, h - arch
    sm = b.sm()
    uo, vo = b.uvo()
    ys = [length * i / n for i in range(n + 1)]
    pts = [(-hw * math.cos(math.pi * i / seg), zt + arch * math.sin(math.pi * i / seg)) for i in range(seg + 1)]
    nz = max(1, int(round((zt - z0) / 1.6)))
    zs = [z0 + (zt - z0) * j / nz for j in range(nz + 1)]
    for k in range(n):
        ya, yb = ys[k], ys[k + 1]
        ck = shade(col, 0.9 - 0.12 * math.sin(math.pi * (k + 0.5) / n))
        for j in range(nz):
            za, zb = zs[j], zs[j + 1]
            b.quad((-hw, ya, za), (-hw, yb, za), (-hw, yb, zb), (-hw, ya, zb), mat, col=ck, lod=lod, uv=[(uo + ya, vo + za), (uo + yb, vo + za), (uo + yb, vo + zb), (uo + ya, vo + zb)])
            b.quad((hw, yb, za), (hw, ya, za), (hw, ya, zb), (hw, yb, zb), mat, col=ck, lod=lod, uv=[(uo + 7 - yb, vo + za), (uo + 7 - ya, vo + za), (uo + 7 - ya, vo + zb), (uo + 7 - yb, vo + zb)])
        acc = zt
        for i in range(seg):
            (xa, za), (xb, zb) = pts[i], pts[i + 1]
            L = math.hypot(xb - xa, zb - za)
            b.quad((xa, ya, za), (xa, yb, za), (xb, yb, zb), (xb, ya, zb), mat, col=shade(ck, 0.94), lod=lod, sm=sm,
                   uv=[(uo + ya, vo + acc), (uo + yb, vo + acc), (uo + yb, vo + acc + L), (uo + ya, vo + acc + L)])
            acc += L
    if floor:
        for k in range(n):
            ya, yb = ys[k], ys[k + 1]
            b.quad((-hw, ya, z0 + 0.03), (hw, ya, z0 + 0.03), (hw, yb, z0 + 0.03), (-hw, yb, z0 + 0.03), floor, col=floor_col, lod=lod,
                   uv=[(-hw, ya), (hw, ya), (hw, yb), (-hw, yb)])
        b.box(w, 0.3, skirt, mat, col=shade(col, 0.8), x=0, y=0.15, z=z0 - skirt, top=False, lod=lod, sides="f")
        b.box(w, 0.3, skirt, mat, col=shade(col, 0.8), x=0, y=length - 0.15, z=z0 - skirt, top=False, lod=lod, sides="b")


def arch_stones(s, pos, z, w, h, arch, n=13, size=(0.44, 0.5), proud=0.07, jambs=True, mat="ashlar", col="sand", lod=1):
    """Voussoirs round the head of a big arched opening in a flat wall (a gateway: the kit dresses only doors
    and windows), and with jambs=True long-and-short stones down both sides. Same pos, z, w, h, arch as the
    opening itself."""
    b = s.b
    u = s.U(pos)
    zt = z + h - arch

    def deco():
        with s.onu(u, 0.0):
            for i in range(n):
                a = math.pi * (i + 0.5) / n
                x, zz = -(w / 2 + size[1] / 2 - 0.03) * math.cos(a), zt + (arch + size[1] / 2 - 0.03) * math.sin(a) * (1.0)
                with b.at(x, -0.02, zz, ry=-(90 - math.degrees(a))):
                    with b.at(rx=90):
                        b.stone(size[0] * (1.12 if i == n // 2 else 1.0), size[1] * (1.25 if i == n // 2 else 1.0), proud, mat=mat, col=col, lod=lod, jitter=0.06)
            if jambs:
                m = max(2, int((zt - max(z, 0.0)) / 0.42))
                hh = (zt - max(z, 0.0)) / m
                for i in range(m):
                    ww = 0.52 if i % 2 == 0 else 0.34
                    for sx in (-1, 1):
                        with b.at(sx * (w / 2 + ww / 2 - 0.02), -0.02, max(z, 0.0) + hh * i, rx=90):
                            b.stone(ww, hh * 0.95, proud, mat=mat, col=col, y=-hh * 0.475, lod=2, jitter=0.05)

    s.add(deco)


def buttress(b, w=0.62, d=0.9, h=4.2, mat="masonry", col="warm", cap="ashlar", cap_col="stone", lod=0, skirt=3.0):
    """A stepped buttress standing against a wall: in the current frame the wall face is y = 0 and the buttress
    projects toward -y, centred on x = 0, with two sloped offsets and a hidden foundation."""
    d2 = d * 0.6
    h1, s1, s2 = h * 0.5, d * 0.42, d * 0.5
    xprism(b, [(0, -skirt), (0, h1 + s1), (-d2, h1 + s1), (-d, h1), (-d, -skirt)], -w / 2, w / 2, mat, col=col, lod=lod, skip=(0,))
    xprism(b, [(0, h1 + s1), (0, h), (-d2, h - s2), (-d2, h1 + s1)], -w / 2, w / 2, mat, col=col, lod=lod, skip=(0, 3))
    with b.detail(1):      # weathering slabs on the two slopes
        for (ya, za, yb, zb) in ((-d - 0.03, h1 - 0.02, -d2 + 0.02, h1 + s1 + 0.03), (-d2 - 0.03, h - s2 - 0.02, 0.0, h + 0.03)):
            b.beam((0, ya, za + 0.03), (0, yb, zb + 0.03), w=w + 0.08, h=0.07, mat=cap, col=cap_col, up=(0, 0, 1))


def crow_steps(b, span, rise, t=0.36, n=5, step_h=None, mat="masonry", col="warm", cap="ashlar", cap_col="stone", lod=0, top=0.5):
    """Crow-stepped coping for a gable: in the current frame the gable wall runs from x = 0 to x = span along
    y = 0 (facing -y, t thick toward +y), its eaves at z = 0 and its apex `rise` above the middle. n steps up
    each side and a flat-topped block (`top` wide) at the apex."""
    half = span / 2
    sw = (half - top / 2) / n
    sh = step_h or rise / n
    for sgn in (-1, 1):
        for i in range(n):
            xa = half + sgn * (half - sw * i)
            xb = half + sgn * (half - sw * (i + 1))
            x0, x1 = min(xa, xb), max(xa, xb)
            z_roof = rise * (i) / n
            zt = rise * (i + 1) / n + 0.12
            b.box(x1 - x0 + 0.02, t, zt - z_roof + 0.25, mat, col=col, x=(x0 + x1) / 2, y=t / 2, z=z_roof - 0.25, lod=lod)
            b.box(x1 - x0 + 0.1, t + 0.1, 0.08, cap, col=cap_col, x=(x0 + x1) / 2, y=t / 2, z=zt, lod=2, bottom=True)
    b.box(top + 0.02, t, 0.75, mat, col=col, x=half, y=t / 2, z=rise - 0.3, lod=lod)
    b.box(top + 0.12, t + 0.1, 0.08, cap, col=cap_col, x=half, y=t / 2, z=rise + 0.45, lod=1, bottom=True)


def stack(b, x, y, z, h, w=0.7, d=0.55, mat="brick", col=None, flues=2, style="square", smoke=True, pot_col="#c9764a", band=True):
    """A tall chimney stack rising h from z (start below the roof surface): a plinth block, then one slender
    shaft per flue (style 'square', 'diagonal' = set cornerwise, or 'round'), an oversailing cap and pots."""
    hb = min(h * 0.38, 1.3)
    with b.at(x, y, z):
        b.box(w, d, hb, mat, col=col, lod=0)
        b.box(w + 0.1, d + 0.1, 0.09, "ashlar", col="stone", z=hb, lod=1, bottom=True)
        fw = min(d * 0.72, (w - 0.08) / flues * 0.86)
        hs = h - hb - 0.3
        for i in range(flues):
            fx = (i - (flues - 1) / 2) * (w - 0.04) / flues
            with b.at(fx, 0, hb + 0.09):
                if style == "round":
                    b.revolve([(fw / 2, 0.0), (fw / 2 * 0.92, hs)], mat, col=shade(col, b.r(0.9, 1.06)), seg=8, lod=0)
                else:
                    with b.at(rz=45 if style == "diagonal" else 0):
                        b.box(fw * (0.8 if style == "diagonal" else 1.0), fw * (0.8 if style == "diagonal" else 1.0), hs, mat, col=shade(col, b.r(0.9, 1.06)), lod=0, top=False)
        zc = hb + 0.09 + hs
        b.box(w + 0.06, d + 0.06, 0.1, mat, col=shade(col, 0.9), z=zc, lod=0, bottom=True)
        if band:
            b.box(w + 0.2, d + 0.2, 0.1, mat, col=col, z=zc + 0.1, lod=1, bottom=True)
        with b.detail(1):
            for i in range(flues):
                fx = (i - (flues - 1) / 2) * (w - 0.04) / flues
                with b.at(fx, 0, zc + (0.2 if band else 0.1)):
                    b.revolve([(0.11, 0.0), (0.09, 0.32), (0.105, 0.36), (0.08, 0.38)], "paint", col=pot_col, seg=8)
        if smoke:
            b.smoke(0, 0, zc + 0.7)


# ---------------------------------------------------------------------------------------- gardens: walls, gates, stairs
def garden_wall(b, p0, p1, h=1.5, t=0.34, mat="masonry", col="warm", coping="stones", cope_col=None, skirt=3.0, lod=0, gate=None, gate_h=None, arch=0.0, cope_lod=1):
    """A free-standing wall from p0 to p1 = (x, y): walk from p0 to p1 and its outer face is on your right, its
    thickness t on your left. A hidden foundation keeps it grounded on a slope.
    coping = 'stones' (hand-laid, uneven), 'slab' or None. gate = (metres along the wall, width) leaves a
    gateway (gate_h high with an optional arched head when the wall is taller, else right through the top).
    Returns the kit Wall (add openings, ivy...) or a pair of them when a gateway splits it."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    out = []
    with b.at(p0[0], p0[1], 0, rz=ang):
        spans = [(0.0, L)]
        through = gate and (gate_h is None or gate_h >= h - 0.05)
        if through:
            g0, g1 = gate[0] - gate[1] / 2, gate[0] + gate[1] / 2
            spans = [(0.0, g0), (g1, L)]
        for (x0, x1) in spans:
            if x1 - x0 < 0.05:
                continue
            with b.at(x0, 0, 0):
                wl = b.wall(x1 - x0, h, mat, col, depth=t, back=mat, thick=t, lod=lod)
                out.append(wl)
                b.box(x1 - x0, t, skirt, mat, col=shade(col, 0.85), x=(x1 - x0) / 2, y=t / 2, z=-skirt, top=False, lod=lod)
                _coping(b, x1 - x0, h, t, coping, cope_col if cope_col is not None else col, mat, cope_lod)
        if gate and not through:
            out[0].opening(gate[0], 0.0, gate[1], gate_h, arch=arch, depth=t, pane=None)
    return out[0] if len(out) == 1 else out


def _coping(b, L, h, t, coping, col, mat, cope_lod=1):
    if coping == "stones":
        n = max(1, int(round(L / 0.5)))
        for i in range(n):
            b.stone(L / n * 0.97, t + 0.1, b.r(0.11, 0.2), mat=mat, col=col, lod=cope_lod if i % 3 == 0 else 2, x=L * (i + 0.5) / n, y=t / 2, z=h, jitter=0.14)
    elif coping == "slab":
        b.box(L + 0.06, t + 0.12, 0.09, "ashlar", col="stone", x=L / 2, y=t / 2, z=h, lod=1, bottom=True)


def gate_piers(b, w=1.4, h=2.1, size=0.5, mat="ashlar", col="stone", ball=True, lod=0, skirt=3.0):
    """Two stone gate piers either side of a gateway w wide, centred on the origin of the current frame (the
    gateway looks toward -y), with caps and ball finials."""
    for sgn in (-1, 1):
        with b.at(sgn * (w / 2 + size / 2), 0, 0):
            b.box(size, size, h, mat, col=col, lod=lod)
            b.box(size, size, skirt, mat, col=shade(col, 0.85), z=-skirt, top=False, lod=lod)
            b.box(size + 0.14, size + 0.14, 0.1, mat, col=col, z=h, lod=1, bottom=True)
            b.box(size + 0.02, size + 0.02, 0.16, mat, col=col, z=h + 0.1, lod=1, taper=0.5)
            if ball:
                with b.detail(1):
                    b.blob(0.17, 0.17, 0.17, mat=mat, col=col, z=h + 0.4, seg=6, rings=4, rough=0.0)


def wood_gate(b, w=1.4, h=1.5, col="green", leaves=2, ajar=18.0, pickets=False, arch=0.0):
    """A boarded (or picket) garden gate hung in a gateway w wide centred on the origin, looking toward -y.
    ajar = how far (degrees) the leaves stand open, inward."""
    lw = w / leaves
    with b.detail(1):
        for k in range(leaves):
            sgn = -1 if k == 0 else 1
            with b.at(sgn * w / 2, 0.06, 0.06, rz=-sgn * ajar if leaves == 2 else -ajar * sgn):
                x0, x1 = (0.0, lw) if sgn < 0 else (-lw, 0.0)
                if pickets:
                    n = max(2, int(lw / 0.16))
                    for i in range(n):
                        xx = x0 + (x1 - x0) * (i + 0.5) / n
                        hh = h - 0.1 + 0.16 * math.sin(math.pi * (i + 0.5) / n) if arch else h
                        b.beam((xx, 0, 0), (xx, 0, hh), w=0.09, h=0.03, mat="planks", col=col, up=(0, 1, 0), lod=1 if i % 2 == 0 else 2)
                    for zz in (0.25, h - 0.3):
                        b.beam((x0, 0.03, zz), (x1, 0.03, zz), w=0.03, h=0.08, mat="planks", col=shade(col, 0.8), up=(0, 0, 1), lod=2)
                else:
                    b.box(abs(x1 - x0) - 0.02, 0.05, h, "planks", col=col, x=(x0 + x1) / 2, y=0, z=0, bottom=True)
                    with b.detail(2):
                        for zz in (h * 0.22, h * 0.78):
                            b.beam((x0 + 0.03, -0.035, zz), (x1 - 0.03, -0.035, zz), w=0.02, h=0.07, mat="metal", col="iron", up=(0, 0, 1), caps=False)


def yard(b, x0, x1, y1, h=1.4, y0=0.14, t=0.32, mat="masonry", col="warm", gate=None, left=True, right=True, coping="stones", gate_h=None, arch=0.0, piers=None,
         gate_col="green", pickets=True, lod=0, cope_lod=1):
    """The walls of a front garden: a wall along the street (y0) from x0 to x1 and returns down one or both
    sides back to y1. gate = (x of its middle, width) in the street wall; piers = height of stone gate piers
    (None for none); the gate itself is hung when gate_col is given. Returns [street wall(s), left, right]."""
    kw = dict(h=h, t=t, mat=mat, col=col, coping=coping, lod=lod, cope_lod=cope_lod)
    out = [garden_wall(b, (x0, y0), (x1, y0), gate=(gate[0] - x0, gate[1]) if gate else None, gate_h=gate_h, arch=arch, **kw)]
    out.append(garden_wall(b, (x0, y1), (x0, y0), **kw) if left else None)
    out.append(garden_wall(b, (x1, y0), (x1, y1), **kw) if right else None)
    if gate:
        with b.at(gate[0], y0 + t / 2, 0):
            if piers:
                gate_piers(b, w=gate[1], h=piers, size=0.44, lod=lod)
            if gate_col:
                wood_gate(b, w=gate[1], h=min((gate_h or h) - 0.15, 1.5), col=gate_col, pickets=pickets, arch=1 if pickets else 0)
    return out


def oculus(s, pos, z, r=0.34, rim="ashlar", rim_col="stone", glass="glass", lod=1):
    """A small round window drawn on a wall, centred at (pos, z): a stone ring round dark glass. It is dressing,
    not a cut, so it also works in a gable (where the kit cannot cut an opening)."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            with b.at(rx=90):
                with b.detail(lod):
                    b.disc(r, glass, seg=12, z=0.02)
                    b.revolve([(r, 0.0), (r + 0.12, 0.0), (r + 0.12, 0.07), (r, 0.09)], rim, col=rim_col, seg=12)
                with b.detail(2):
                    b.box(0.035, 2 * r, 0.02, "planks", col="ivory", z=0.03)
                    b.box(2 * r, 0.035, 0.02, "planks", col="ivory", z=0.03)

    s.add(deco)


def well(b, x=0.0, y=0.0, z=0.0, r=0.62, col="warm", roof="tiles"):
    """A garden well: stone ring, two posts, a little roof, windlass and bucket (with a hidden foundation)."""
    with b.at(x, y, z):
        lathe(b, [(r, -3.0), (r, 0.0), (r, 0.78), (r - 0.2, 0.78), (r - 0.2, 0.3)], "masonry", col=col, seg=10, lod=0)
        b.disc(r - 0.2, "water", col="#5f8f96", seg=10, z=0.32, lod=1)
        with b.detail(2):
            for i in range(10):
                with b.at(rz=36 * i + 18):
                    b.stone(0.36, 0.26, 0.09, mat="ashlar", col="sand", y=-(r - 0.1), z=0.78, jitter=0.1)
        with b.detail(1):
            for sx in (-1, 1):
                b.beam((sx * (r - 0.06), 0, 0.7), (sx * (r - 0.06), 0, 2.15), w=0.11)
            b.tube((-r + 0.06, 0, 1.55), (r - 0.06, 0, 1.55), r=0.06, mat="timber", col="darkoak", n=6)
            b.gable_roof(2 * r + 0.3, 0.9, pitch=40, mat=roof, x=0, y=0, z=2.1, ridge="x", eave=0.12, verge=0.08, course=0.3, thick=0.07, barge=False, ridge_roll=False, lod=1)
        with b.detail(2):
            b.beam((0.1, 0, 1.5), (0.1, 0, 1.0), w=0.02, mat="cloth", col="#8a7a66", caps=False)
            with b.at(0.1, 0, 0.72):
                b.revolve([(0.1, 0.0), (0.14, 0.28)], "planks", col="#c9a57a", seg=7, close_bottom=True)


def pergola(b, w, d, h=2.2, nx=3, col="darkoak", vines=True, bloom=None, lod=1):
    """An open timber pergola over a w by d patch centred on the origin of the current frame: posts at the
    corners (and along the long sides), beams, rafters, and a vine over it."""
    xs = [-w / 2 + w * i / (nx - 1) for i in range(nx)]
    with b.detail(lod):
        for x in xs:
            for y in (-d / 2, d / 2):
                b.beam((x, y, 0), (x, y, h), w=0.11, col=col)
        for y in (-d / 2, d / 2):
            b.beam((-w / 2 - 0.2, y, h + 0.06), (w / 2 + 0.2, y, h + 0.06), w=0.1, h=0.13, col=col)
    with b.detail(2):
        n = max(3, int(w / 0.45))
        for i in range(n + 1):
            x = -w / 2 + w * i / n
            b.beam((x, -d / 2 - 0.22, h + 0.17), (x, d / 2 + 0.22, h + 0.17), w=0.06, h=0.1, col=col)
    if vines:
        climber(b, (xs[0], -d / 2, 0.2), (xs[0], -d / 2, h), n=5, r=0.2, bloom=bloom, lod=2)
        climber(b, (-w / 2, 0, h + 0.3), (w / 2, 0, h + 0.3), n=max(5, int(w * 2.2)), r=0.3, bloom=bloom, lod=lod)
        climber(b, (xs[-1], d / 2, 0.2), (xs[-1], d / 2, h), n=4, r=0.2, bloom=bloom, lod=2)


def outside_stair(b, n=10, w=1.1, rise=0.19, run=0.3, mat="masonry", col="warm", tread="ashlar", tread_col="stone", landing=0.0, rail=None, rail_sides="lr",
                  rail_col="darkoak", skirt=3.0, lod=0, rail_h=0.95):
    """A solid stone stair climbing toward +y from the origin of the current frame (as parts.stairs), built to
    be seen from afar: a rubble mass with a hidden foundation (always drawn), real steps and proud treads
    nearer by, an optional top landing `landing` long and a rail on the left / right ('l', 'r', 'lr').
    Returns (y, z) of the far end of the top (landing) floor."""
    Lr, H = n * run, n * rise
    Lt = Lr + landing
    xprism(b, [(0.0, -skirt), (Lt, -skirt), (Lt, H), (Lr, H), (0.0, 0.0)], -w / 2, w / 2, mat, col=col, lod=lod)
    with b.detail(1):
        for i in range(n):
            b.box(w, run, rise, mat, col=col, x=0, y=run * (i + 0.5), z=rise * i, sides="frl", top=False)
            b.box(w + 0.06, run + 0.04, 0.06, tread, col=shade(tread_col, b.r(0.92, 1.06)), x=0, y=run * (i + 0.5) - 0.02, z=rise * (i + 1) - 0.03, bottom=True)
        if landing:
            b.box(w + 0.06, landing + 0.02, 0.06, tread, col=tread_col, x=0, y=Lr + landing / 2 + 0.02, z=H - 0.03, bottom=True)
    if rail:
        for s in rail_sides:
            sx = -1 if s == "l" else 1
            pts = [(sx * (w / 2 - 0.06), 0.05, rise * 0.6), (sx * (w / 2 - 0.06), Lr, H)]
            if landing:
                pts.append((sx * (w / 2 - 0.06), Lt - 0.06, H))
            P.railing(b, pts, h=rail_h, style=rail, col=rail_col, posts_at=1.3)
    return Lt, H


# ---------------------------------------------------------------------------------------- domes, vanes, creatures
def dome_section(r, h, n=7, eave=0.14, drop=0.07, power=1.0):
    """A (radius, z) section for kit cone_roof: a dome of radius r and height h springing from a wall top.
    power < 1 swells it (bulbous), > 1 makes it more pointed."""
    out = [(r + eave, -drop)]
    for i in range(1, n + 1):
        th = math.pi / 2 * i / n
        out.append((r * math.cos(th) ** power if i < n else 0.0, h * math.sin(th)))
    return out


def ribs(b, section, n=12, w=0.1, proud=0.05, mat="metal", col="copper", lod=1, phase=0.0):
    """Ribs standing on a domed / conical roof with the given (radius, z) section, n of them round the axis."""
    for k in range(n):
        with b.at(rz=360.0 * (k + phase) / n):
            for i in range(len(section) - 1):
                (ra, za), (rb, zb) = section[i], section[i + 1]
                up = (0, -1, 0) if abs(zb - za) > abs(rb - ra) else (0, 0, 1)
                b.beam((0, -ra, za + proud * 0.5), (0, -max(rb, 0.03), zb + proud * 0.5), w=w, h=proud * 2, mat=mat, col=col, lod=lod, caps=False, up=up)


def armillary(b, x=0.0, y=0.0, z=0.0, r=0.42, pole=0.9, col="brass"):
    """A brass armillary sphere on a short pole: the star-gazer's finial."""
    with b.at(x, y, z):
        with b.detail(1):
            b.tube((0, 0, 0), (0, 0, pole + 2 * r + 0.5), r=0.025, mat="metal", col=col, n=5)
            b.blob(r * 0.26, r * 0.26, r * 0.26, mat="metal", col=col, z=pole + r, seg=6, rings=4, rough=0.0)
            with b.at(z=pole + r):
                for (rx, ry) in ((0, 0), (90, 0), (90, 90), (62, 35)):
                    with b.at(rx=rx, rz=ry):
                        b.revolve([(r, -0.03), (r, 0.03)], "metal", col=col, seg=14)
                        b.revolve([(r - 0.012, 0.03), (r - 0.012, -0.03)], "metal", col=shade(col, 0.7), seg=14)
            b.box(0.07, 0.07, 0.07, "metal", col=col, z=pole + 2 * r + 0.5, bottom=True)


VANES = {
    "dove": [(-.5, .02), (-.3, .1), (-.08, .12), (.1, .3), (.2, .16), (.34, .16), (.46, .1), (.34, .04), (.2, -.08), (-.1, -.1), (-.3, -.04), (-.52, -.1)],
    "fish": [(-.5, .16), (-.36, 0), (-.2, .1), (.1, .15), (.36, .08), (.5, 0), (.36, -.08), (.1, -.14), (-.2, -.1), (-.36, 0), (-.5, -.16), (-.42, 0)],
    "quill": [(-.5, -.2), (-.44, -.24), (-.1, -.02), (.2, .06), (.42, .22), (.5, .34), (.36, .34), (.1, .26), (-.14, .1)],
    "cock": [(-.44, .3), (-.3, .1), (-.12, .04), (.1, .1), (.2, .3), (.3, .36), (.34, .26), (.44, .22), (.34, .16), (.3, -.02), (.1, -.16), (-.14, -.14), (-.34, .0), (-.5, .12)],
    "moon": [(.06, .34), (-.18, .22), (-.28, 0), (-.18, -.22), (.06, -.34), (-.06, -.16), (-.1, 0), (-.06, .16)],
    "pennon": [(-.5, .14), (.1, .14), (.5, .22), (.3, 0), (.5, -.22), (.1, -.14), (-.5, -.14)],
    "comet": [(-.55, .04), (-.1, .08), (.12, .24), (.2, .1), (.4, .1), (.24, 0), (.4, -.1), (.2, -.1), (.12, -.24), (-.1, -.08), (-.55, -.04)],
}


def vane(b, x=0.0, y=0.0, z=0.0, h=1.6, shape="dove", size=1.0, col="brass", pole="iron", rz=None, cardinals=True):
    """A weathervane with a cut-out figure ('dove', 'fish', 'quill', 'cock', 'moon', 'pennon', 'comet') on a
    pole rising from (x, y, z)."""
    poly = VANES[shape]
    with b.at(x, y, z):
        with b.detail(1):
            b.tube((0, 0, 0), (0, 0, h), r=0.025, mat="metal", col=pole, n=5)
            with b.at(z=h * 0.86, rz=b.r(0, 360) if rz is None else rz):
                area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
                if area > 0:                       # make it clockwise seen from -y
                    poly = list(reversed(poly))
                ring = [(px * size, 0.0, pz * size + 0.02) for px, pz in poly]
                cx = sum(p[0] for p in ring) / len(ring)
                cz = sum(p[2] for p in ring) / len(ring)
                for i in range(len(ring)):
                    p, q = ring[i], ring[(i + 1) % len(ring)]
                    b.tri((cx, -0.006, cz), q, p, "metal", col=col)
                    b.tri((cx, 0.006, cz), p, q, "metal", col=shade(col, 0.85))
        with b.detail(2):
            if cardinals:
                b.beam((-0.32, 0, h * 0.58), (0.32, 0, h * 0.58), w=0.02, mat="metal", col=pole, caps=False)
                b.beam((0, -0.32, h * 0.58), (0, 0.32, h * 0.58), w=0.02, mat="metal", col=pole, caps=False)
            b.blob(0.06, 0.06, 0.06, mat="metal", col=col, z=h + 0.03, seg=5, rings=2, rough=0.0)


def dove(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="#f6f3ea", s=1.0):
    """A dove sitting at (x, y, z), looking toward local -y turned by rz. (The Crown is full of them.)"""
    with b.at(x, y, z, rz=rz, s=s):
        with b.detail(2):
            b.blob(0.075, 0.13, 0.075, mat="cloth", col=col, y=0.0, z=0.085, seg=5, rings=3, rough=0.06)
            b.blob(0.045, 0.05, 0.045, mat="cloth", col=col, y=-0.12, z=0.17, seg=4, rings=2, rough=0.0)
            t = [(-0.045, 0.09, 0.1), (0.045, 0.09, 0.1), (0.03, 0.27, 0.07), (-0.03, 0.27, 0.07)]
            b.face(t, "cloth", col=shade(col, 0.92))
            b.face(list(reversed(t)), "cloth", col=shade(col, 0.8))
            b.tri((-0.012, -0.16, 0.17), (0.012, -0.16, 0.17), (0, -0.2, 0.16), "paint", col="!#e39a3c")


def cat(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="#4a4038", s=1.0):
    """A cat sitting at (x, y, z), looking toward local -y turned by rz."""
    with b.at(x, y, z, rz=rz, s=s):
        with b.detail(2):
            b.blob(0.1, 0.13, 0.14, mat="cloth", col=col, y=0.03, z=0.13, seg=5, rings=3, rough=0.05)
            b.blob(0.075, 0.075, 0.07, mat="cloth", col=col, y=-0.07, z=0.31, seg=5, rings=3, rough=0.0)
            for sx in (-1, 1):
                t = [(sx * 0.065, -0.07, 0.35), (sx * 0.015, -0.07, 0.365), (sx * 0.05, -0.07, 0.43)]
                b.face(t, "cloth", col=col)
                b.face(list(reversed(t)), "cloth", col=col)
            b.beam((0.07, 0.12, 0.03), (0.17, -0.02, 0.03), w=0.035, mat="cloth", col=col, caps=False)
            b.beam((0.17, -0.02, 0.03), (0.13, -0.12, 0.03), w=0.03, mat="cloth", col=col, caps=False)


def urn(b, x=0.0, y=0.0, z=0.0, h=1.0, col="stone", plant=True, cols=None):
    """A stone urn on a pedestal, with flowers: for gate-sides and garden steps."""
    with b.at(x, y, z):
        with b.detail(1):
            b.box(0.36, 0.36, h * 0.5, "ashlar", col=col)
            b.revolve([(0.08, h * 0.5), (0.1, h * 0.58), (0.22, h * 0.8), (0.24, h * 0.95), (0.19, h)], "ashlar", col=col, seg=8)
        b.box(0.36, 0.36, 1.5, "ashlar", col=shade(col, 0.85), z=-1.5, top=False, lod=1)
        if plant:
            flowers(b, 0, 0, h - 0.12, w=0.26, d=0.26, n=3, cols=cols, h=0.34)


def doves(b, spots, col="#f6f3ea"):
    """Several doves: spots = [(x, y, z), ...]; each looks a random way."""
    for (x, y, z) in spots:
        dove(b, x, y, z, rz=b.r(0, 360), col=shade(col, b.r(0.86, 1.0)), s=b.r(0.9, 1.15))


def banner(b, x, y, z, w=0.7, h=2.4, col="stripe_red", rz=0.0, tail="swallow", rod=True, stripe=None):
    """A long cloth banner hanging from (x, y, z) (the middle of its top edge), facing local -y; it stirs in the
    wind. tail = 'swallow', 'point' or 'square'. stripe = a second colour for a middle band."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            if rod:
                b.beam((-w / 2 - 0.08, 0, 0.02), (w / 2 + 0.08, 0, 0.02), w=0.04, mat="timber", col="darkoak", caps=True)
            n = 4
            for i in range(n):
                z0, z1 = -h * i / n, -h * (i + 1) / n
                w0, w1 = i / n * 0.6, (i + 1) / n * 0.6
                for (xa, xb, cc) in ((-w / 2, -w / 6, col), (-w / 6, w / 6, stripe or col), (w / 6, w / 2, col)):
                    p = [(xa, 0, z1), (xb, 0, z1), (xb, 0, z0), (xa, 0, z0)]
                    b.face(p, "cloth", col=cc, wind=(w1, w1, w0, w0))
                    b.face(list(reversed(p)), "cloth", col=shade(cc, 0.82), wind=(w0, w0, w1, w1))
            if tail in ("swallow", "point"):
                d = 0.35
                tris = [((-w / 2, 0, -h), (0, 0, -h), (-w / 2, 0, -h - d)), ((0, 0, -h), (w / 2, 0, -h), (w / 2, 0, -h - d))] if tail == "swallow" else [((-w / 2, 0, -h), (w / 2, 0, -h), (0, 0, -h - d))]
                for t in tris:
                    wd = (0.6, 0.6, 0.75)
                    b.face([t[0], t[2], t[1]] if tail == "swallow" else [t[2], t[1], t[0]], "cloth", col=col, wind=(wd[0], wd[2], wd[1]) if tail == "swallow" else (wd[2], wd[1], wd[0]))
                    b.face([t[0], t[1], t[2]], "cloth", col=shade(col, 0.82), wind=wd)


# ---------------------------------------------------------------------------------------- green things, small furniture
def tuft(b, x=0.0, y=0.0, z=0.0, r=0.22, col=GRASS, lod=2):
    """A tuft of grass or moss."""
    b.blob(r, r * 0.9, r * 0.6, mat="ivy", col=shade(col, b.r(0.85, 1.12)), x=x, y=y, z=z + r * 0.3, lod=lod, seg=5, rings=2, wind=0.4, rough=0.35)


def flowers(b, x=0.0, y=0.0, z=0.0, w=0.8, d=0.4, n=5, cols=None, leaf="#7db45e", h=0.3, lod=2):
    """A clump of flowering plants on the ground (or in a bed) about w by d."""
    rng = b.rng
    with b.detail(lod):
        for i in range(n):
            px, py = x + rng.uniform(-w / 2, w / 2), y + rng.uniform(-d / 2, d / 2)
            r = rng.uniform(0.12, 0.2)
            b.blob(r, r, h * rng.uniform(0.5, 0.8), mat="ivy", col=shade(leaf, rng.uniform(0.85, 1.1)), x=px, y=py, z=z + h * 0.35, seg=5, rings=2, wind=0.35, rough=0.3)
            b.blob(0.07, 0.07, 0.06, mat="paint", col=rng.choice(cols or P.FLOWERS), x=px + rng.uniform(-0.05, 0.05), y=py + rng.uniform(-0.05, 0.05), z=z + h * rng.uniform(0.75, 1.0), seg=5, rings=2, wind=0.5, rough=0.2)


def climber(b, p0, p1, n=7, r=0.24, col="#7fb760", bloom=None, lod=1):
    """A climbing plant along a line from p0 to p1 (up a post, along a beam): leafy lumps, and with bloom = a
    list of flower colours, blossoms among them."""
    rng = b.rng
    for i in range(n):
        t = (i + rng.uniform(0.2, 0.8)) / n
        p = (lerp(p0[0], p1[0], t) + rng.uniform(-0.08, 0.08), lerp(p0[1], p1[1], t) + rng.uniform(-0.08, 0.08), lerp(p0[2], p1[2], t))
        rr = r * rng.uniform(0.7, 1.2)
        b.blob(rr, rr, rr * 0.9, mat="ivy", col=shade(col, rng.uniform(0.82, 1.15)), x=p[0], y=p[1], z=p[2], lod=lod, seg=5, rings=3, wind=0.3, rough=0.3)
        if bloom:
            with b.detail(2):
                for _ in range(2):
                    b.blob(0.06, 0.06, 0.055, mat="paint", col=rng.choice(bloom), x=p[0] + rng.uniform(-rr, rr) * 0.8, y=p[1] + rng.uniform(-rr, rr) * 0.8, z=p[2] + rng.uniform(-rr, rr) * 0.7,
                           seg=4, rings=2, wind=0.5, rough=0.2)


def pots(b, p0, p1, n=6, r=(0.09, 0.17), cols=("#c9764a", "#b5653f", "#d9a37a", "#8fb0a8", "#e8dcc0"), lod=2):
    """A row of pots and jars standing between p0 and p1 = (x, y, z): the potter's drying shelf, a doorstep."""
    rng = b.rng
    with b.detail(lod):
        for i in range(n):
            t = (i + 0.5) / n
            rr = rng.uniform(*r)
            hh = rr * rng.uniform(1.4, 2.6)
            with b.at(lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t)):
                b.revolve([(rr * 0.6, 0.0), (rr, hh * 0.45), (rr * 0.85, hh * 0.8), (rr * 0.5, hh * 0.92), (rr * 0.62, hh)], "paint", col=rng.choice(cols), seg=6)


def lamp_post(b, x=0.0, y=0.0, z=0.0, h=2.6, col="iron"):
    """A lantern on an iron post."""
    with b.at(x, y, z):
        with b.detail(1):
            b.tube((0, 0, 0), (0, 0, h), r=0.045, mat="metal", col=col, n=6)
            b.box(0.2, 0.2, 0.1, "metal", col=col, z=0.0)
        with b.detail(2):
            b.box(0.2, 0.2, 0.26, "glow", col="#ffd88a", z=h, bottom=True)
            b.box(0.26, 0.26, 0.04, "metal", col=col, z=h + 0.26)
            b.box(0.24, 0.24, 0.03, "metal", col=col, z=h - 0.03, bottom=True)
            b.box(0.12, 0.12, 0.1, "metal", col=col, z=h + 0.3, taper=0.3)
        b.lamp(0, 0, h + 0.1)


def hatch(b, x=0.0, y=0.0, z=0.0, w=0.9, d=0.9, open_deg=55.0, col="greyoak", rz=0.0, frame="darkoak"):
    """A trap door in a floor or flat roof at (x, y, z): a kerb, the dark well and a boarded lid propped open
    (hinged along its far, +y, edge). The believable way down from a roof."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            for (bx, by, bw, bd) in ((0, -d / 2, w + 0.16, 0.08), (0, d / 2, w + 0.16, 0.08), (-w / 2, 0, 0.08, d), (w / 2, 0, 0.08, d)):
                b.box(bw, bd, 0.14, "timber", col=frame, x=bx, y=by, z=0)
            b.quad((-w / 2, -d / 2, 0.02), (w / 2, -d / 2, 0.02), (w / 2, d / 2, 0.02), (-w / 2, d / 2, 0.02), "paint", col="!#1e1a18")
            with b.at(0, d / 2, 0.14, rx=-open_deg):
                b.box(w + 0.1, d + 0.06, 0.05, "planks", col=col, x=0, y=-(d + 0.06) / 2, z=0, bottom=True)
                with b.detail(2):
                    for xx in (-w * 0.3, w * 0.3):
                        b.beam((xx, -0.05, 0.06), (xx, -d, 0.06), w=0.08, h=0.03, mat="planks", col=shade(col, 0.8), up=(0, 0, 1))
        with b.detail(2):
            if open_deg > 12:
                L = d * 0.8
                b.beam((w * 0.36, -d / 2 + 0.02, 0.14), (w * 0.36, d / 2 - L * math.cos(rad(open_deg)) * 0.98, 0.14 + L * math.sin(rad(open_deg)) * 0.98), w=0.035, mat="timber", col=frame, caps=False)
            for i in range(2):      # the top of the ladder showing
                xx = (-0.2, 0.2)[i]
                b.beam((xx, -d / 2 + 0.1, -0.3), (xx, -d / 2 + 0.06, 0.5), w=0.045, mat="timber", col="greyoak")
            b.beam((-0.2, -d / 2 + 0.07, 0.3), (0.2, -d / 2 + 0.07, 0.3), w=0.035, mat="timber", col="greyoak", caps=False)
