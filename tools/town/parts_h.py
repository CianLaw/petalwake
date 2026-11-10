"""Larkhaven harbour parts (district prefix h_): the working quay's vocabulary, on top of kit.py and parts.py.

Structure: GWall (a wall whose top can be a gable, a lean-to slope or crow steps and can still be cut anywhere),
lean-tos, tall stacks, roof ridges and hip rolls, dark linings for open doorways.
Dressing: tarred board-and-batten, loading doors, louvres, hoists, and the clutter of a quay: rope, nets, floats,
lobster pots, anchors, oars, buoys, boats, fish racks, signal flags, gulls and a cat.
Like parts.py everything is written in its own local frame; headings are the kit's (0 = front, 90 = right).
"""
import math
from contextlib import contextmanager

from kit import C, Wall, _grid, lerp, paint, rad, shade, vadd, vlerp, vmul, vnorm, vsub
import parts as P

# ---------------------------------------------------------------------------------------- colours of the quay
TAR = paint("#3f3a37")          # tarred boards
TAR_OLD = paint("#665f57")      # tar gone grey in the salt
OXIDE = paint("#a34a3b")        # red-oxide boat paint
ROPE = "#cdb686"
NET = "#5f8f86"
NET_BROWN = "#8f7350"
CORK = "#d7b98a"
SAIL_TAN = "#b8573c"            # bark-tanned sailcloth
SILVER = "#c3ced3"              # a fresh fish
SMOKED = "#c78a45"              # a kipper
GLASSY = ["!#3f9f8f", "!#4f86b8", "!#d9a431", "!#b5433a", "!#f2ead8"]      # net floats
SIGNALS = [("!#d8b02f", "!#2f4f8f"), ("!#b5433a", "!#f2ead8"), ("!#2f4f8f", "!#f2ead8"), ("!#d8b02f", "!#b5433a"),
           ("!#f2ead8", "!#2c2a2a"), ("!#b5433a", "!#b5433a"), ("!#3f8f5f", "!#f2ead8"), ("!#d8b02f", "!#d8b02f")]


def _cut(s, u, *a, **kw):
    """Cut an opening by metres along the wall, whatever kind of wall it is (as parts.py does)."""
    return Wall.opening(s, u, *a, **kw)


# ---------------------------------------------------------------------------------------- walls with shaped tops
def _clip_below(poly, u0, z0, u1, z1):
    """The part of a convex polygon [(u, z), ...] lying under the line through (u0, z0) and (u1, z1)."""
    f = lambda p: z0 + (z1 - z0) * (p[0] - u0) / (u1 - u0) - p[1]
    out = []
    for i in range(len(poly)):
        a, c = poly[i], poly[(i + 1) % len(poly)]
        fa, fc = f(a), f(c)
        if fa >= -1e-9:
            out.append(a)
        if (fa > 1e-9 and fc < -1e-9) or (fa < -1e-9 and fc > 1e-9):
            t = fa / (fa - fc)
            out.append((a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t))
    return out


class GWall(Wall):
    """A flat wall whose top edge is any outline: a gable, a lean-to slope, crow steps. Unlike the kit's Wall it
    can be cut anywhere under that outline (loft doors and windows in the gable). Make one with gwall(), or hand
    an existing wall of a Body to cuttable() / shape()."""
    tops = None          # [(u, z), ...] from the left end to the right: the top edge. None = the kit's gable.
    back_from = None     # with .back set: the wall stands free above this height (back face and top there)

    def outline(self):
        if self.tops:
            return self.tops
        if self.gable > 1e-6:
            half = self.w / 2
            if self.gable_section:
                sec = self.gable_section
                k = self.gable / sec[-1][1]
                left = [(0.0, self.h)] + [(min(r_, half), self.h + z_ * k) for r_, z_ in sec[1:]]
            else:
                left = [(0.0, self.h), (half, self.h + self.gable)]
            return left + [(self.w - u, z) for u, z in reversed(left[:-1])]
        return [(0.0, self.h), (self.w, self.h)]

    def top_at(self, u):
        out = self.outline()
        for (u0, z0), (u1, z1) in zip(out, out[1:]):
            if u1 - u0 > 1e-9 and u0 - 1e-9 <= u <= u1 + 1e-9:
                return z0 + (z1 - z0) * (u - u0) / (u1 - u0)
        return self.h

    def emit(self):
        b = self.b
        uo, vo = self.uvo
        out = self.outline()
        zmax = max(z for _, z in out)
        cu = lambda v: min(max(v, 0.0), self.w)
        cz = lambda v: min(max(v, 0.0), zmax)
        with b.frame(self.m):
            us = _grid({0.0, self.w} | {cu(u) for u, _ in out} | {cu(o[k]) for o in self.ops for k in ("u0", "u1")}, self.w, self.cell)
            zs = _grid({0.0, zmax} | {cz(z) for _, z in out} | {cz(o[k]) for o in self.ops for k in ("z0", "z1")}, zmax, self.cell)
            free = self.back_from if (self.back and self.back_from is not None) else None
            t = self.thick or 0.3
            for i in range(len(us) - 1):
                ua, ue = us[i], us[i + 1]
                if ue - ua < 1e-6:
                    continue
                um = (ua + ue) / 2
                seg = None
                for (u0, z0), (u1, z1) in zip(out, out[1:]):
                    if u1 - u0 > 1e-9 and u0 - 1e-9 <= um <= u1 + 1e-9:
                        seg = (u0, z0, u1, z1)
                        break
                if seg is None:
                    continue
                ta = seg[1] + (seg[3] - seg[1]) * (ua - seg[0]) / (seg[2] - seg[0])
                te = seg[1] + (seg[3] - seg[1]) * (ue - seg[0]) / (seg[2] - seg[0])
                for j in range(len(zs) - 1):
                    za, zb = zs[j], zs[j + 1]
                    if zb - za < 1e-6 or za >= max(ta, te) - 1e-6 or self._in_hole(um, (za + zb) / 2):
                        continue
                    poly = [(ua, za), (ue, za), (ue, zb), (ua, zb)]
                    if zb > min(ta, te) + 1e-6:
                        poly = _clip_below(poly, ua, ta, ue, te)
                    if len(poly) < 3:
                        continue
                    b.face([(p[0], 0.0, p[1]) for p in poly], self.mat, col=self.col, lod=self.lod, uv=[(uo + p[0], vo + p[1]) for p in poly])
                    if free is not None and zb > free + 1e-6:
                        q = [p for p in poly] if za >= free - 1e-6 else _clip_below([(p[0], -p[1]) for p in poly], ua, -free, ue, -free)
                        if za < free - 1e-6:
                            q = [(p[0], -p[1]) for p in q]
                        if len(q) >= 3:
                            b.face([(p[0], t, p[1]) for p in reversed(q)], self.back, col=self.backcol if self.backcol is not None else self.col, lod=self.lod,
                                   uv=[(uo + p[0], vo + p[1]) for p in reversed(q)])
            if free is not None:      # the top of the free-standing part, following the outline (risers too)
                for (u0, z0), (u1, z1) in zip(out, out[1:]):
                    if max(z0, z1) <= free + 1e-6 or (abs(u1 - u0) < 1e-9 and abs(z1 - z0) < 1e-9):
                        continue
                    b.quad((u0, 0, z0), (u1, 0, z1), (u1, t, z1), (u0, t, z0), self.back, col=shade(self.col, 0.94), lod=self.lod)
                for u, flip in ((0.0, False), (self.w, True)):
                    zt = out[0][1] if not flip else out[-1][1]
                    if zt > free + 1e-6:
                        q = [(u, t, free), (u, 0, free), (u, 0, zt), (u, t, zt)]
                        b.face(list(reversed(q)) if flip else q, self.back, col=self.col, lod=self.lod)
            self._emit_openings()
        self._finish()


def gwall(b, w, h, tops=None, mat="plaster", col=None, depth=0.24, lod=0, back=None, thick=0.3, back_from=None, gable=0.0):
    """A flat wall like b.wall() (local x-z plane, facing -y, from the origin) whose top edge is `tops` =
    [(u, z), ...] (or a plain centred gable `gable` high) and which may be cut anywhere under it. With back =
    a material it stands free above back_from: it gets a back face and a top there, `thick` deep."""
    wl = GWall(b, w, h, mat, C(col), depth, gable, lod, b.uvo(), back, None, thick)
    wl.tops = tops
    wl.back_from = back_from
    b._walls.append(wl)
    return wl


def cuttable(*walls):
    """Let these walls of a Body (the gable ends, after or before body.gable()) take openings in their gables."""
    for wl in walls:
        wl.__class__ = GWall
    return walls[0]


def shape(wl, tops):
    """Give a Body's wall a shaped top edge: tops = [(u, z), ...] from its left end to its right."""
    wl.__class__ = GWall
    wl.tops = tops
    return wl


def steps_outline(w, h, rise, n, top_w=0.9):
    """The top edge of a crow-stepped gable w wide: eaves at h, n steps a side climbing `rise` to a flat top."""
    run = (w - top_w) / 2
    pts = [(0.0, h)]
    for i in range(n):
        pts.append((run * i / n, h + rise * (i + 1) / n))
        pts.append((run * (i + 1) / n, h + rise * (i + 1) / n))
    left = pts
    return left + [(w - u, z) for u, z in reversed(left)]


def leanto(b, x, y, w, d, h, rz=0.0, z=0.0, pitch=24.0, mat="masonry", col="warm", roof="tiles", roof_col=None, eave=0.28, verge=0.18,
           course=0.36, depth=0.2, thick=0.1, foot=True, back_wall=False, plinth=0.0, plinth_col="warm"):
    """A lean-to against a taller wall. (x, y, z) is the middle of the foot of its high side, on that wall; it is
    w long along the wall and stands d out from it toward compass rz (0 = toward the front, 90 = right, 180 =
    back, 270 = left). h = height of its low outer wall. Returns its Body (front = the low outer wall, left and
    right = the sloped ends as seen from outside facing it) with .rise set."""
    rise = d * math.tan(rad(pitch))
    with b.at(x, y, z, rz=rz):
        bd = b.body(w, d, h, mat=mat, col=col, x=0.0, y=-d / 2, depth=depth, foot=foot)
        shape(bd.right, [(0.0, h), (d, h + rise)])
        shape(bd.left, [(0.0, h + rise), (d, h)])
        if back_wall:
            shape(bd.back, [(0.0, h + rise), (w, h + rise)])
        else:
            bd.back.done = True
        b.gable_roof(w, d, pitch, mat=roof, col=roof_col, x=0.0, y=0.0, z=h, ridge="x", half=True, eave=eave, verge=verge,
                     course=course, thick=thick, barge=False)      # (a lean-to roof's high edge is on the line y)
        if plinth:
            b.box(w + 0.12, d + 0.06, plinth, "masonry", col=plinth_col, y=-d / 2 - 0.03, lod=0)
            b.box(w + 0.12, d + 0.06, 3.0, "masonry", col=shade(plinth_col, 0.85), y=-d / 2 - 0.03, z=-3.0, top=False, lod=0)
    bd.rise = rise
    return bd


def lining(b, w, d, h, x=0.0, y=0.0, z=0.0, col="#4a4038", mat="planks", floor="flagstone", floor_col="#8a8478", skip=""):
    """The inside of a room seen through an open doorway: a box of inward-facing boards (centred on x, y).
    skip = the sides to leave out, from 'frbl': leave out the side the doorway is in, or it hides the room."""
    hw, hd = w / 2, d / 2
    with b.at(x, y, z):
        c = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]
        for i in range(4):
            if "frbl"[i] in skip:
                continue
            a, e = c[i], c[(i + 1) % 4]
            b.quad((e[0], e[1], 0), (a[0], a[1], 0), (a[0], a[1], h), (e[0], e[1], h), mat, col=shade(col, 0.8 + 0.1 * (i % 2)), lod=0)
        b.quad((-hw, -hd, h), (hw, -hd, h), (hw, hd, h), (-hw, hd, h), mat, col=shade(col, 0.6), lod=0)
        if floor:
            b.quad((-hw, -hd, 0.02), (hw, -hd, 0.02), (hw, hd, 0.02), (-hw, hd, 0.02), floor, col=floor_col, lod=0)


def stack(b, x, y, z, h, w=0.85, d=None, top=0.62, mat="brick", col=None, bands=2, pots=1, smoke=1.0, cap_col="stone", pot_col="#c9764a"):
    """A tall tapering chimney stack rising h from z, with stone bands, an oversailing cap and pots."""
    d = w if d is None else d
    with b.at(x, y, z):
        b.box(w, d, h, mat, col=col, taper=top / w, lod=0)
        with b.detail(1):
            for i in range(bands):
                t = (i + 1) / (bands + 1) * 0.86
                k = 1 - (1 - top / w) * t
                b.box(w * k + 0.08, d * k + 0.08, 0.12, "ashlar", col=cap_col, z=h * t, bottom=True)
            k = top / w
            b.box(w * k + 0.06, d * k + 0.06, 0.2, mat, col=shade(col, 0.92), z=h, taper=1.22, bottom=True)
            b.box(w * k * 1.22 + 0.1, d * k * 1.22 + 0.1, 0.1, "ashlar", col=cap_col, z=h + 0.2, bottom=True)
            for i in range(pots):
                px = (i - (pots - 1) / 2) * 0.3
                with b.at(px, 0, h + 0.3):
                    b.revolve([(0.12, 0.0), (0.095, 0.34), (0.115, 0.38), (0.085, 0.4)], "paint", col=pot_col, seg=8)
        if smoke:
            b.smoke(0, 0, h + 0.75, strength=smoke)


def ridge_roll(b, p0, p1, mat="tiles", col=None, w=0.26, step=0.42, lod=1):
    """A line of ridge (or hip) tiles from p0 to p1."""
    L = math.dist(p0, p1)
    n = max(1, int(L / step))
    c = C(col)
    with b.detail(lod):
        for i in range(n):
            a, e = vlerp(p0, p1, i / n), vlerp(p0, p1, (i + 0.96) / n)
            b.beam((a[0], a[1], a[2] + 0.03), (e[0], e[1], e[2] + 0.05), w=w, h=0.14, mat=mat, col=shade(c, b.r(0.82, 1.0)), caps=True)


def hip_rolls(b, w, d, section, z=0.0, x=0.0, y=0.0, mat="tiles", col=None, eave=0.4, ridge=True):
    """Hip and ridge tiles for a b.loop_roof(w, d, section=...) at the same place: section = [(run, rise), ...]."""
    hw, hd = w / 2, d / 2
    s0 = (section[1][1] - section[0][1]) / max(section[1][0] - section[0][0], 1e-6)
    sec = [(-eave, -eave * s0)] + list(section[1:])
    with b.at(x, y, z):
        for sx in (-1, 1):
            for sy in (-1, 1):
                for (ra, za), (rb, zb) in zip(sec, sec[1:]):
                    pa = (sx * max(hw - ra, 0.0), sy * max(hd - ra, 0.0), za)
                    pb = (sx * max(hw - rb, 0.0), sy * max(hd - rb, 0.0), zb)
                    ridge_roll(b, pa, pb, mat=mat, col=col, w=0.24, step=0.5)
        run, rise = section[-1]
        if ridge and abs(hw - hd) > 0.3 and run >= min(hw, hd) - 1e-6:
            if hw > hd:
                ridge_roll(b, (-(hw - hd) - 0.1, 0, rise), (hw - hd + 0.1, 0, rise), mat=mat, col=col)
            else:
                ridge_roll(b, (0, -(hd - hw) - 0.1, rise), (0, hd - hw + 0.1, rise), mat=mat, col=col)


def near_only(s, n=1):
    """Demote the dressing of the last n parts added to this wall (frames, sills, shutters, lintels) to the near
    level; their openings and panes stay. For windows that matter little from afar: keeps the mid level in budget."""
    b = s.b
    fns = [s.deco.pop() for _ in range(n)][::-1]

    def deco():
        real = b.detail

        @contextmanager
        def forced(lod):
            with real(2):
                yield b

        b.detail = forced
        try:
            with real(2):
                for fn in fns:
                    fn()
        finally:
            del b.detail

    s.add(deco)


def small_bell(b, x=0.0, y=0.0, z=0.0, r=0.16, col="brass", lod=2):
    """A hand-sized bell hanging at (x, y, z) (its crown)."""
    with b.at(x, y, z):
        with b.detail(lod):
            b.revolve([(r * 1.05, -r * 1.7), (r * 0.9, -r * 1.5), (r * 0.55, -r * 0.7), (r * 0.3, -r * 0.15), (0.03, 0.0)], "metal", col=col, seg=7)


# ---------------------------------------------------------------------------------------- boarding, doors, vents
def battens(s, z0=0.0, z1=None, u0=0.0, u1=None, step=0.44, col=None, w=0.07, proud=0.03, lod=2, rails=()):
    """Board-and-batten relief on a boarded wall: thin vertical cover strips every `step`, cut by the openings,
    and horizontal rails at the given heights."""
    b = s.b
    z1 = s.h if z1 is None else z1
    u1 = s.w if u1 is None else u1
    col = s.col if col is None else col
    n = max(1, round((u1 - u0) / step))
    top = getattr(s, "top_at", None)

    def deco():
        with b.detail(lod):
            for i in range(n + 1):
                u = u0 + (u1 - u0) * i / n
                u = min(max(u, u0 + w / 2), u1 - w / 2)
                zt = min(z1, top(u) - 0.02) if (top and z1 > s.h) else z1
                cuts = sorted((o["z0"], o["z1"]) for o in s.ops if o["u0"] - w / 2 < u < o["u1"] + w / 2 and o["z1"] > z0 and o["z0"] < zt)
                za = z0
                for (ca, cb) in cuts + [(zt, zt)]:
                    if ca - za > 0.12:
                        b.beam((u, -proud / 2, za), (u, -proud / 2, ca), w=w, h=proud, mat="planks", col=shade(col, 0.9), up=(0, 1, 0), caps=False)
                    za = max(za, cb)
            for rz_ in rails:
                b.beam((u0, -proud / 2 - 0.004, rz_), (u1, -proud / 2 - 0.004, rz_), w=proud + 0.01, h=0.11, mat="planks", col=shade(col, 0.82), up=(0, 0, 1), caps=False)

    s.add(deco)


def loading_door(s, pos, z, w=1.3, h=1.8, col="red", frame="darkoak", sill=True, bar=True, depth=None, arch=0.0, lod=2):
    """A pair of boarded loading doors high in a wall: braced leaves, strap hinges, a landing sill on brackets
    and a guard bar across."""
    b = s.b
    u = s.U(pos)
    op = _cut(s, u, z, w, h, arch=arch, depth=depth if depth is not None else min(s.depth, 0.16), pane="planks", pane_col=col)
    d = op["d"]

    def deco():
        with s.onu(u, z):
            hs = h - arch
            with b.detail(1):
                for sgn in (-1, 1):
                    b.beam((sgn * (w / 2 + 0.06), -0.02, -0.05), (sgn * (w / 2 + 0.06), -0.02, hs + 0.1), w=0.12, h=0.09, mat="timber", col=frame, up=(0, 1, 0))
                if arch < 1e-4:
                    b.beam((-w / 2 - 0.2, -0.02, h + 0.07), (w / 2 + 0.2, -0.02, h + 0.07), w=0.1, h=0.15, mat="timber", col=frame, up=(0, 0, 1))
                if sill:
                    b.box(w + 0.5, 0.42, 0.07, "planks", col="greyoak", y=-0.19, z=-0.08, bottom=True)
            with b.detail(lod):
                y = d - 0.014
                dk = shade(col, 0.66)
                b.beam((0, y, 0.02), (0, y, hs - 0.02), w=0.035, h=0.02, mat="planks", col=dk, up=(0, 1, 0), caps=False)
                for sgn in (-1, 1):
                    xa, xb = sgn * 0.05, sgn * (w / 2 - 0.04)
                    for zz in (hs * 0.16, hs * 0.84):
                        b.beam((xa, y, zz), (xb, y, zz), w=0.025, h=0.1, mat="planks", col=dk, up=(0, 0, 1), caps=False)
                    b.beam((xa, y, hs * 0.2), (xb, y, hs * 0.8), w=0.09, h=0.025, mat="planks", col=dk, up=(0, 1, 0), caps=False)
                    for zz in (hs * 0.16, hs * 0.84):
                        b.beam((xb + sgn * 0.04, y - 0.014, zz), (xb - sgn * 0.3, y - 0.014, zz), w=0.02, h=0.05, mat="metal", col="iron", up=(0, 0, 1), caps=False)
                if sill:
                    for sgn in (-1, 1):
                        b.beam((sgn * (w / 2 + 0.1), 0.0, -0.42), (sgn * (w / 2 + 0.1), -0.34, -0.1), w=0.07, mat="timber", col=frame)
                if bar:
                    b.beam((-w / 2 - 0.02, d * 0.3, hs * 0.45), (w / 2 + 0.02, d * 0.3, hs * 0.45), w=0.05, h=0.07, mat="timber", col=frame, caps=False)

    s.add(deco)
    return op


def hatch(s, pos, z, w=0.7, h=0.8, col="red", depth=0.1, hinges=True):
    """A small boarded shutter closed over an opening: a store-room window that is never opened."""
    b = s.b
    u = s.U(pos)
    op = _cut(s, u, z, w, h, depth=depth, pane="planks", pane_col=col)

    def deco():
        with s.onu(u, z):
            with b.detail(2):
                y = op["d"] - 0.012
                dk = shade(col, 0.66)
                for zz in (h * 0.22, h * 0.78):
                    b.beam((-w / 2 + 0.03, y, zz), (w / 2 - 0.03, y, zz), w=0.022, h=0.07, mat="planks", col=dk, up=(0, 0, 1), caps=False)
                    if hinges:
                        b.beam((-w / 2, y - 0.012, zz), (-w / 2 + 0.28, y - 0.012, zz), w=0.02, h=0.04, mat="metal", col="iron", up=(0, 0, 1), caps=False)
            with b.detail(1):
                b.box(w + 0.16, 0.14, 0.06, "planks", col="greyoak", y=-0.03, z=-0.06, bottom=True)

    s.add(deco)
    return op


def shutter(s, pos, z, w=0.7, h=0.95, col="red", lod=1):
    """A closed boarded shutter planted on the wall (nothing is cut): cheap rows of store windows on a long wall."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            with b.detail(lod):
                b.box(w, 0.05, h, "planks", col=col, y=-0.025, bottom=True)
                b.box(w + 0.16, 0.12, 0.06, "ashlar", col="stone", y=-0.04, z=-0.06, bottom=True)
            with b.detail(2):
                dk = shade(col, 0.66)
                for zz in (h * 0.22, h * 0.78):
                    b.beam((-w / 2 + 0.03, -0.06, zz), (w / 2 - 0.03, -0.06, zz), w=0.022, h=0.07, mat="planks", col=dk, up=(0, 0, 1), caps=False)
                    b.beam((-w / 2, -0.07, zz), (-w / 2 + 0.26, -0.07, zz), w=0.02, h=0.04, mat="metal", col="iron", up=(0, 0, 1), caps=False)
                b.box(w + 0.2, 0.08, 0.14, "ashlar", col="stone", y=-0.03, z=h, bottom=True)

    s.add(deco)


def louvre(s, pos, z, w=0.9, h=1.0, n=6, col="greyoak", frame="darkoak", depth=0.14, arch=0.0):
    """A louvred vent in a wall: sloping slats in a frame."""
    b = s.b
    u = s.U(pos)
    op = _cut(s, u, z, w, h, arch=arch, depth=depth, pane="planks", pane_col="#3a332d")

    def deco():
        with s.onu(u, z):
            hs = h - arch
            with b.detail(1):
                for i in range(n):
                    zz = hs * (i + 0.5) / n
                    b.beam((-w / 2, depth * 0.45, zz), (w / 2, depth * 0.45, zz), w=0.03, h=hs / n * 1.15, mat="planks", col=col, up=(0, -0.55, 0.83), caps=False)
            with b.detail(2):
                for sgn in (-1, 1):
                    b.beam((sgn * (w / 2 + 0.04), -0.015, -0.04), (sgn * (w / 2 + 0.04), -0.015, hs + 0.04), w=0.09, h=0.06, mat="timber", col=frame, up=(0, 1, 0))
                b.beam((-w / 2 - 0.09, -0.015, -0.04), (w / 2 + 0.09, -0.015, -0.04), w=0.06, h=0.08, mat="timber", col=frame, up=(0, 0, 1))
                if arch < 1e-4:
                    b.beam((-w / 2 - 0.09, -0.015, h + 0.04), (w / 2 + 0.09, -0.015, h + 0.04), w=0.06, h=0.08, mat="timber", col=frame, up=(0, 0, 1))

    s.add(deco)
    return op


def hoist(b, x, y, z, out=1.25, rz=0.0, drop=3.0, load="crate", col="darkoak", brace=True, hood=None, hood_col=None, back=0.5):
    """A hoist beam (cathead) sticking `out` from a wall at (x, y, z) toward compass rz, with its brace, a block,
    a rope hanging `drop` and a load on the hook: 'crate', 'barrel', 'sack', 'net', 'bale' or None.
    hood = a roofing material for a little pent hood over it."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            b.beam((0, back, 0), (0, -out, 0), w=0.17, h=0.22, mat="timber", col=col)
            if brace:
                b.beam((0, 0.0, -0.85), (0, -out * 0.72, -0.1), w=0.11, mat="timber", col=col)
            if hood:
                for sgn in (-1, 1):
                    q = [(0, 0.02, 0.62), (sgn * 0.55, 0.02, 0.24), (sgn * 0.6, -out - 0.12, 0.2), (0, -out - 0.12, 0.58)]
                    b.face(q if sgn > 0 else list(reversed(q)), hood, col=hood_col)
                    b.face(list(reversed(q)) if sgn > 0 else q, "planks", col="darkoak")
                b.tri((-0.6, -out - 0.12, 0.2), (0.6, -out - 0.12, 0.2), (0, -out - 0.12, 0.58), "planks", col="darkoak")
        yb = -out + 0.16
        with b.detail(2):
            with b.at(0, yb, -0.26, ry=90):
                b.revolve([(0.0, -0.035), (0.11, -0.035), (0.11, 0.035), (0.0, 0.035)], "timber", col="greyoak", seg=8)
            b.beam((0, yb, -0.11), (0, yb, -0.2), w=0.03, mat="metal", col="iron", caps=False)
        if drop:
            with b.detail(1):
                b.beam((0, yb, -0.3), (0, yb, -drop), w=0.03, mat="cloth", col=ROPE, caps=False)
            with b.detail(2):
                b.beam((0, yb, -drop), (0, yb, -drop - 0.14), w=0.035, mat="metal", col="iron", caps=False)
            zl = -drop - 0.14
            if load == "crate":
                with b.detail(1):
                    with b.at(0, yb, zl - 0.62, rz=b.r(-25, 25)):
                        b.box(0.62, 0.62, 0.55, "planks", col="#d8c3a0", bottom=True)
                with b.detail(2):
                    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                        b.beam((0, yb, zl), (sx * 0.3, yb + sy * 0.3, zl - 0.08), w=0.02, mat="cloth", col=ROPE, caps=False)
            elif load == "barrel":
                with b.at(0, yb, zl - 0.48, rx=90):
                    with b.detail(1):
                        b.revolve([(0.22, -0.36), (0.3, -0.12), (0.3, 0.12), (0.22, 0.36)], "planks", col="#c9a57a", seg=10, close_top=True, close_bottom=True)
                with b.detail(2):
                    for sy in (-1, 1):
                        b.beam((0, yb, zl), (0, yb + sy * 0.26, zl - 0.2), w=0.02, mat="cloth", col=ROPE, caps=False)
            elif load == "sack":
                with b.detail(1):
                    b.blob(0.27, 0.24, 0.36, mat="cloth", col="#d9c9a3", x=0, y=yb, z=zl - 0.36, seg=6, rings=3, rough=0.12)
            elif load == "bale":
                with b.detail(1):
                    with b.at(0, yb, zl - 0.6, rz=b.r(-20, 20)):
                        b.box(0.75, 0.5, 0.5, "cloth", col="#e6dcc2", bottom=True)
                with b.detail(2):
                    with b.at(0, yb, zl - 0.6):
                        for xx in (-0.2, 0.2):
                            b.box(0.04, 0.54, 0.54, "cloth", col=ROPE, x=xx, z=-0.02, bottom=True)
            elif load == "net":
                with b.detail(1):
                    b.blob(0.34, 0.3, 0.42, mat="cloth", col=NET, x=0, y=yb, z=zl - 0.4, seg=6, rings=3, rough=0.2)
                with b.detail(2):
                    for i in range(4):
                        a = b.r(0, 6.28)
                        b.blob(0.065, mat="paint", col=b.pick(GLASSY), x=0.3 * math.cos(a), y=yb + 0.26 * math.sin(a), z=zl - 0.4 + b.r(-0.25, 0.2), seg=5, rings=2, rough=0.05)


# ---------------------------------------------------------------------------------------- rope, nets, floats
def rope_coil(b, x=0.0, y=0.0, z=0.0, r=0.3, col=ROPE):
    """A coil of rope lying on the ground (or on a deck)."""
    with b.at(x, y, z):
        with b.detail(2):
            b.revolve([(r, 0.0), (r * 1.04, 0.05), (r * 0.96, 0.1), (r * 1.02, 0.15), (r * 0.9, 0.2), (r * 0.5, 0.2), (r * 0.5, 0.02)], "cloth",
                      col=col, seg=8, cols=[shade(col, k) for k in (0.95, 1.05, 0.92, 1.04, 1.0, 0.7)])


def rope_hank(s, pos, z, r=0.2, col=ROPE):
    """A hank of rope hung on a peg on a wall."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            with b.detail(2):
                b.beam((0, 0.0, 0), (0, -0.12, 0.02), w=0.035, mat="timber", col="darkoak")
                with b.at(0, -0.07, -r * 1.25, rx=90):
                    b.revolve([(r * 0.62, -0.035), (r, -0.04), (r, 0.04), (r * 0.62, 0.035)], "cloth", col=col, seg=7, cols=[shade(col, 0.8), col, shade(col, 0.9)])

    s.add(deco)


def net_drape(b, p0, p1, drop=1.3, sag=0.25, col=NET, mesh=0.36, floats=True, ragged=0.25, lod=2, strand=0.04, n=6):
    """A fishing net hung to dry from a line or pole between p0 and p1: a chunky diamond mesh under a head rope
    with cork floats. It stirs in the wind."""
    rng = b.rng
    Lh = math.dist(p0, p1) or 1.0
    top = lambda s_: (lerp(p0[0], p1[0], s_), lerp(p0[1], p1[1], s_), lerp(p0[2], p1[2], s_) - sag * 4 * s_ * (1 - s_))
    knots = [drop * (1 - ragged * rng.random()) for _ in range(n + 1)]

    def dropat(s_):
        x = min(max(s_, 0.0), 1.0) * n
        i = min(int(x), n - 1)
        return lerp(knots[i], knots[i + 1], x - i)

    def at(s_, t):
        p = top(s_)
        return (p[0], p[1], p[2] - dropat(s_) * t)

    hx, hy = (p1[0] - p0[0]) / Lh, (p1[1] - p0[1]) / Lh
    nrm = (hy, -hx, 0.0)
    q = drop / Lh
    dc = mesh * 1.414 / Lh
    c = C(col)
    with b.detail(1):
        N = 5
        for i in range(N):
            b.beam(top(i / N), top((i + 1) / N), w=0.035, mat="cloth", col=ROPE, caps=False)
    with b.detail(lod):
        for sgn in (1, -1):
            cc = -q + dc * rng.random() if sgn > 0 else dc * rng.random()
            end = 1.0 if sgn > 0 else 1.0 + q
            while cc < end:
                ts = [(0.0 - cc) / (sgn * q), (1.0 - cc) / (sgn * q)]
                t0, t1 = max(0.0, min(ts)), min(1.0, max(ts))
                if t1 - t0 > 0.08:
                    ck = shade(c, rng.uniform(0.82, 1.1))
                    for k in range(2):
                        ta, tb = lerp(t0, t1, k / 2), lerp(t0, t1, (k + 1) / 2)
                        A, B = at(cc + sgn * q * ta, ta), at(cc + sgn * q * tb, tb)
                        d = vnorm(vsub(B, A))
                        w = (d[1] * nrm[2] - d[2] * nrm[1], d[2] * nrm[0] - d[0] * nrm[2], d[0] * nrm[1] - d[1] * nrm[0])
                        w = vmul(vnorm(w), strand / 2)
                        qd = [vsub(A, w), vsub(B, w), vadd(B, w), vadd(A, w)]
                        wd = (0.35 * ta, 0.35 * tb, 0.35 * tb, 0.35 * ta)
                        b.face(qd, "cloth", col=ck, wind=wd)
                        b.face(list(reversed(qd)), "cloth", col=shade(ck, 0.85), wind=tuple(reversed(wd)))
                cc += dc
    if floats:
        with b.detail(2):
            m = max(3, int(Lh / 0.5))
            for i in range(m + 1):
                a_ = top(i / m)
                b.blob(0.065, 0.065, 0.05, mat="paint", col=CORK if i % 3 else rng.choice(GLASSY), x=a_[0], y=a_[1], z=a_[2] - 0.02, seg=5, rings=2, rough=0.05)


def net_heap(b, x=0.0, y=0.0, z=0.0, r=0.55, col=NET, floats=4):
    """A heap of net on the ground with a few floats in it."""
    with b.detail(2):
        b.blob(r, r * 0.8, r * 0.38, mat="cloth", col=col, x=x, y=y, z=z + r * 0.3, seg=7, rings=3, rough=0.3)
        for _ in range(floats):
            a, k = b.r(0, 6.28), b.r(0.3, 0.85)
            b.blob(0.065, mat="paint", col=b.pick(GLASSY + [CORK]), x=x + r * k * math.cos(a), y=y + r * 0.8 * k * math.sin(a), z=z + r * 0.42 * (1.2 - k) + 0.1, seg=5, rings=2, rough=0.05)


def floats(s, pos, z, n=5, cols=None, drop=0.9):
    """A bunch of coloured net floats hung on a wall from a peg."""
    b = s.b
    u = s.U(pos)
    rng = b.rng
    cols = cols or GLASSY
    items = [(rng.uniform(-0.16, 0.16), rng.uniform(0.25, drop), rng.uniform(0.09, 0.13), rng.choice(cols)) for _ in range(n)]

    def deco():
        with s.onu(u, z):
            with b.detail(2):
                b.beam((0, 0.0, 0), (0, -0.12, 0.02), w=0.035, mat="timber", col="darkoak")
                for (dx, dz, r, c) in items:
                    b.beam((0, -0.1, 0), (dx, -0.1 - r * 0.4, -dz + r), w=0.012, mat="cloth", col=ROPE, caps=False)
                    b.blob(r, mat="paint", col=c, x=dx, y=-0.1 - r * 0.5, z=-dz, seg=6, rings=3, rough=0.04)

    s.add(deco)


def buoy(b, x=0.0, y=0.0, z=0.0, col="!#b5433a", stripe="!#f2ead8", s=1.0, flag=None):
    """A marker buoy stood on the quay, optionally with its little flag stick."""
    with b.at(x, y, z, s=s):
        with b.detail(2):
            b.revolve([(0.05, 0.0), (0.24, 0.16), (0.3, 0.36), (0.26, 0.5), (0.1, 0.72), (0.05, 0.76)], "paint", col=col, seg=8, close_top=True,
                      cols=[col, col, stripe, col, col])
            if flag:
                b.beam((0, 0, 0.74), (0, 0, 1.7), w=0.025, mat="planks", col="greyoak", caps=False)
                q = [(0, 0, 1.4), (0.3, 0, 1.47), (0.3, 0, 1.63), (0, 0, 1.7)]
                b.face(q, "cloth", col=flag, wind=(0, 0.5, 0.5, 0))
                b.face(list(reversed(q)), "cloth", col=shade(flag, 0.85), wind=(0, 0.5, 0.5, 0))


def pot(b, x=0.0, y=0.0, z=0.0, rz=0.0, L=0.72, r=0.27, col="#c9a36f"):
    """A lobster pot (creel): a wicker half-barrel on a slatted base."""
    n = 5
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            arc = [(-r * math.cos(math.pi * i / n), r * math.sin(math.pi * i / n) + 0.03) for i in range(n + 1)]
            for i in range(n):
                (ya, za), (yb, zb) = arc[i], arc[i + 1]
                b.quad((L / 2, ya, za), (-L / 2, ya, za), (-L / 2, yb, zb), (L / 2, yb, zb), "thatch", col=shade(col, 0.85 + 0.08 * (i % 2)))
            for sx in (-1, 1):
                pts = [(sx * L / 2, y_, z_) for y_, z_ in arc]
                b.face(pts if sx < 0 else list(reversed(pts)), "thatch", col=shade(col, 0.72))
            b.box(L + 0.04, 2 * r + 0.04, 0.03, "planks", col="greyoak", bottom=True)


def pots(b, x=0.0, y=0.0, z=0.0, rz=0.0, n=3, **kw):
    """A stack of n lobster pots: a row with more piled on top."""
    row = max(1, (n + 1) // 2)
    with b.at(x, y, z, rz=rz):
        k = 0
        for lvl, cnt in ((0, row), (1, n - row)):
            for i in range(cnt):
                pot(b, 0.0 + b.r(-0.05, 0.05), (i - (cnt - 1) / 2) * 0.6, lvl * 0.32, rz=b.r(-8, 8), **kw)
                k += 1


def bollard(b, x=0.0, y=0.0, z=0.0, h=0.62, r=0.15, col="iron", mat="metal"):
    """A mooring bollard."""
    with b.at(x, y, z):
        with b.detail(2):
            b.revolve([(r * 1.2, 0.0), (r * 0.9, h * 0.12), (r * 0.8, h * 0.62), (r * 1.35, h * 0.78), (r * 1.35, h * 0.9), (r * 0.6, h)], mat, col=col, seg=8, close_top=True)


def mooring_post(b, x=0.0, y=0.0, z=0.0, h=1.5, r=0.13, gull_on=False, rope=True):
    """A weathered timber mooring post with a rope turn round it (a gull's favourite perch)."""
    with b.at(x, y, z):
        with b.detail(1):
            b.tube((0, 0, -0.3), (0, 0, h), r=r, r1=r * 0.86, mat="timber", col="greyoak", n=7, caps=True)
        with b.detail(2):
            b.revolve([(r * 0.9, h - 0.07), (r * 1.08, h - 0.05), (r * 1.08, h + 0.0), (r * 0.5, h + 0.03)], "metal", col="iron", seg=7, close_top=True)
            if rope:
                b.revolve([(r * 1.0, h * 0.5), (r * 1.3, h * 0.52), (r * 1.3, h * 0.62), (r * 1.0, h * 0.64)], "cloth", col=ROPE, seg=7)
        if gull_on:
            gull(b, 0, 0, h + 0.03, rz=b.r(0, 360))


def life_ring(s, pos, z, r=0.33, cols=("!#c8443a", "!#f4eee0")):
    """A life ring hung on a wall."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            with b.detail(2):
                with b.at(0, -0.075, 0, rx=90):
                    t = r * 0.24
                    prof = [(r - t, 0.0), (r, -t * 0.8), (r + t, 0.0), (r, t * 0.8), (r - t, 0.0)]
                    for k in range(4):
                        b.revolve(prof, "paint", col=cols[k % 2], seg=3, a0=90 * k + 45, a1=90 * k + 135)

    s.add(deco)


def anchor(b, x=0.0, y=0.0, z=0.0, rz=0.0, h=1.35, lean=12.0, col="iron"):
    """An old anchor leaning against a wall (it leans back toward local +y)."""
    with b.at(x, y, z, rz=rz):
        with b.at(rx=-lean):
            with b.detail(2):
                b.beam((0, 0, 0.06), (0, 0, h), w=0.07, mat="metal", col=col)
                b.beam((-0.34, 0, h * 0.86), (0.34, 0, h * 0.86), w=0.06, mat="metal", col=col)
                for sgn in (-1, 1):
                    pts = [(0, 0, 0.06), (sgn * 0.24, 0, 0.1), (sgn * 0.42, 0, 0.26), (sgn * 0.5, 0, 0.5)]
                    for a, e in zip(pts, pts[1:]):
                        b.beam(a, e, w=0.06, mat="metal", col=col, caps=False)
                    q = [(sgn * 0.5, 0, 0.5), (sgn * 0.36, 0, 0.42), (sgn * 0.47, 0, 0.66)]
                    b.face(q, "metal", col=col)
                    b.face(list(reversed(q)), "metal", col=col)
                with b.at(0, 0, h + 0.07, rx=90):
                    b.revolve([(0.05, -0.02), (0.09, -0.02), (0.09, 0.02), (0.05, 0.02)], "metal", col=col, seg=6)


def oars(b, x=0.0, y=0.0, z=0.0, rz=0.0, n=2, L=2.7, col="#d9c7a3", blade="!#f2ead8"):
    """Oars stood against a wall, blades up (they lean back toward local +y)."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            for i in range(n):
                dx = (i - (n - 1) / 2) * 0.2
                tip = (dx + b.r(-0.05, 0.05), 0.0, L)
                foot = (dx, -0.3 - 0.06 * i, 0.0)
                b.tube(foot, vlerp(foot, tip, 0.8), r=0.026, mat="planks", col=col, n=4)
                a, e = vlerp(foot, tip, 0.78), tip
                b.beam(a, e, w=0.12, h=0.025, mat="paint", col=blade, up=(0, 1, 0.1))


def fish_line(b, p0, p1, n=8, col=SILVER, size=0.3, sag=0.08, pole=True):
    """A row of fish hung by their tails from a pole or line between p0 and p1."""
    rng = b.rng
    pt = lambda t: (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t) - sag * 4 * t * (1 - t))
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1.0
    dx, dy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    if pole:
        with b.detail(1):
            b.beam(p0, p1, w=0.05, mat="timber", col="greyoak", caps=False)
    with b.detail(2):
        for i in range(n):
            c = pt((i + 0.5) / n)
            s_ = size * rng.uniform(0.8, 1.15)
            wv = s_ * 0.22
            q = [(c[0], c[1], c[2]), (c[0] - dx * wv, c[1] - dy * wv, c[2] - s_ * 0.45), (c[0], c[1], c[2] - s_), (c[0] + dx * wv, c[1] + dy * wv, c[2] - s_ * 0.45)]
            ck = shade(col, rng.uniform(0.85, 1.1))
            b.face(q, "paint", col=ck)
            b.face(list(reversed(q)), "paint", col=shade(ck, 0.9))


def fish_rack(b, x=0.0, y=0.0, z=0.0, rz=0.0, w=2.2, h=1.9, rows=2, n=7, col=SILVER, deep=0.0):
    """A drying rack: two posts (four with deep > 0), rails, and rows of fish."""
    with b.at(x, y, z, rz=rz):
        ys = (0.0,) if deep <= 0 else (-deep / 2, deep / 2)
        with b.detail(1):
            for yy in ys:
                for sx in (-1, 1):
                    b.beam((sx * w / 2, yy, -0.2), (sx * w / 2, yy, h + 0.12), w=0.09, mat="timber", col="greyoak")
            if deep > 0:
                for sx in (-1, 1):
                    b.beam((sx * w / 2, -deep / 2, h), (sx * w / 2, deep / 2, h), w=0.07, mat="timber", col="greyoak")
        for yy in ys:
            for r in range(rows):
                zz = h - r * (h * 0.42)
                fish_line(b, (-w / 2, yy, zz), (w / 2, yy, zz), n=n, col=col, sag=0.0)


def basket(b, x=0.0, y=0.0, z=0.0, r=0.3, h=0.34, fill=SILVER, col="#c9a36f"):
    """A wicker basket, full of fish (or whatever colour `fill` is; None = empty)."""
    with b.at(x, y, z):
        with b.detail(2):
            b.revolve([(r * 0.72, 0.0), (r, h), (r * 1.06, h + 0.03), (r * 0.94, h + 0.03)], "thatch", col=col, seg=8)
            if fill:
                b.disc(r * 0.95, "paint", col=fill, seg=8, z=h - 0.03)
                for _ in range(3):
                    a = b.r(0, 6.28)
                    b.blob(r * 0.4, r * 0.16, 0.05, mat="paint", col=shade(fill, b.r(0.8, 1.1)), x=r * 0.4 * math.cos(a), y=r * 0.4 * math.sin(a), z=h, seg=5, rings=2, rough=0.1)


def fish_box(b, x=0.0, y=0.0, z=0.0, rz=0.0, w=0.75, d=0.48, h=0.2, fill=SILVER):
    """A shallow fish box, full to the brim."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            b.box(w, d, h, "planks", col="#d8c3a0", cap="paint", capcol=shade(fill, 0.9))
            for i in range(4):
                b.blob(w * 0.2, d * 0.14, 0.04, mat="paint", col=shade(fill, b.r(0.85, 1.12)), x=b.r(-w * 0.25, w * 0.25), y=b.r(-d * 0.25, d * 0.25), z=h + 0.01, seg=5, rings=2, rough=0.1)


def logs(b, x=0.0, y=0.0, z=0.0, rz=0.0, n=3, L=0.9, r=0.11, col="#b08f6a"):
    """A stack of cut logs, n along the bottom row."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            for lvl in range(n):
                for i in range(n - lvl):
                    xx = (i - (n - lvl - 1) / 2) * r * 2.05
                    b.tube((xx, -L / 2 + b.r(-0.05, 0.05), r + lvl * r * 1.75), (xx, L / 2 + b.r(-0.05, 0.05), r + lvl * r * 1.75), r=r, mat="timber", col=shade(col, b.r(0.85, 1.1)), n=6, caps=True)


def signal_flags(b, p0, p1, n=7, sag=0.5, size=0.42, cols=None, line=True):
    """A hoist of signal flags on a halyard from p0 to p1: bright two-colour flags that fly in the wind."""
    rng = b.rng
    cols = cols or SIGNALS
    pt = lambda t: (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t) - sag * 4 * t * (1 - t))
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1.0
    dx, dy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    with b.detail(1):
        if line:
            N = 6
            for i in range(N):
                b.beam(pt(i / N), pt((i + 1) / N), w=0.018, mat="cloth", col="#8a7a66", caps=False)
        k0 = rng.randrange(len(cols))
        for i in range(n):
            c = pt((i + 0.5) / n)
            ca, cb = cols[(k0 + i) % len(cols)]
            hw = size * 0.5
            for half, cc in ((0, ca), (1, cb)):
                x0, x1 = -hw + hw * half, -hw + hw * (half + 1)
                q = [(c[0] + dx * x0, c[1] + dy * x0, c[2] - size * 0.82), (c[0] + dx * x1, c[1] + dy * x1, c[2] - size * 0.82),
                     (c[0] + dx * x1, c[1] + dy * x1, c[2] - 0.02), (c[0] + dx * x0, c[1] + dy * x0, c[2] - 0.02)]
                b.face(q, "cloth", col=cc, wind=(0.55, 0.55, 0.05, 0.05))
                b.face(list(reversed(q)), "cloth", col=shade(cc, 0.88), wind=(0.05, 0.05, 0.55, 0.55))


def sail(b, pts, col=SAIL_TAN, rows=4, wind=0.35):
    """A sail (or awning) hung out: pts = its corners in order, 3 or 4 of them, the first two along the yard or
    line it hangs from. Drawn both sides in cloth strips so the seams show; it stirs in the wind."""
    c = C(col)
    a, e = pts[0], pts[1]
    lo = pts[2:] if len(pts) == 4 else [pts[2], pts[2]]
    with b.detail(1):
        for j in range(rows):
            t0, t1 = j / rows, (j + 1) / rows
            q = [vlerp(a, lo[-1], t1), vlerp(e, lo[0], t1), vlerp(e, lo[0], t0), vlerp(a, lo[-1], t0)]
            ck = shade(c, 0.9 + 0.14 * ((j * 7) % 3) / 2)
            b.face(q, "cloth", col=ck, wind=(wind * t1, wind * t1, wind * t0, wind * t0))
            b.face(list(reversed(q)), "cloth", col=shade(ck, 0.86), wind=(wind * t0, wind * t0, wind * t1, wind * t1))


# ---------------------------------------------------------------------------------------- boats
def hull(b, L=4.2, beam=1.5, depth=0.62, col="!#f2ead8", trim="!#2f4470", inside="#b89a72", cut=0.0, stations=7, strakes=3, inner=True,
         thwarts=2, keel=True, lod=1, sheer=0.3, skin=0.05, transom=0.7):
    """A clinker boat lying along local x, bow toward +x, keel on z = 0. col = hull paint, trim = the top strake.
    cut = 0..0.6 saws the stern off at that fraction of the length (a flat end: half a boat for a shed).
    inner=False leaves out the inside (for a boat turned keel-up: wrap it in `with b.at(z=..., rx=180)`).
    Returns the stations: lists of (x, half-breadth, z) from keel to sheer."""
    th = [k / strakes * math.pi / 2 for k in range(strakes + 1)]
    f = [math.sin(a_) ** 0.8 for a_ in th]            # half-breadth of each strake edge, keel to sheer
    g = [1 - math.cos(a_) ** 1.3 for a_ in th]        # and its height
    ts = [cut + (1.0 - cut) * i / (stations - 1) for i in range(stations)]

    def sec(t, ins=0.0):
        x = -L / 2 + L * t
        bw = beam / 2 * (1 - t ** 2.2) ** 0.55 * (transom + (1 - transom) * min(1.0, t / 0.35))
        zk = depth * 0.5 * max(0.0, (t - 0.75) / 0.25) ** 2
        zs = depth * (1.0 + sheer * (2 * t - 0.9) ** 2)
        rake = 0.2 * depth if t > 0.999 else 0.0
        out = []
        for k in range(strakes + 1):
            yy = bw * f[k]
            yy = max(yy - ins, 0.0) if k else 0.0
            zz = zk + (zs - zk) * g[k] + ins * (1 - g[k])
            out.append((x + rake * g[k], yy, zz))
        return out

    S = [sec(t) for t in ts]
    Si = [sec(t, skin) for t in ts]
    cols = [shade(col, 0.9 if k % 2 == 0 else 1.0) for k in range(strakes - 1)] + [trim]
    P3 = lambda p, sgn: (p[0], sgn * p[1], p[2])
    with b.detail(lod):
        for i in range(len(S) - 1):
            for sgn in (1, -1):
                for k in range(strakes):
                    p = [P3(S[i][k], sgn), P3(S[i + 1][k], sgn), P3(S[i + 1][k + 1], sgn), P3(S[i][k + 1], sgn)]
                    b.face(list(reversed(p)) if sgn > 0 else p, "paint", col=cols[k])
                    if inner:
                        p = [P3(Si[i][k], sgn), P3(Si[i + 1][k], sgn), P3(Si[i + 1][k + 1], sgn), P3(Si[i][k + 1], sgn)]
                        b.face(p if sgn > 0 else list(reversed(p)), "planks", col=shade(inside, 0.72 + 0.2 * k / strakes))
                if inner:      # the gunwale
                    p = [P3(S[i][-1], sgn), P3(S[i + 1][-1], sgn), P3(Si[i + 1][-1], sgn), P3(Si[i][-1], sgn)]
                    b.face(list(reversed(p)) if sgn > 0 else p, "paint", col=shade(trim, 1.15))
        # the stern (transom, or the sawn end)
        ring = lambda st, dx: [(st[k][0] + dx, st[k][1], st[k][2]) for k in range(strakes + 1)] + [(st[k][0] + dx, -st[k][1], st[k][2]) for k in range(strakes, 0, -1)]
        b.face(list(reversed(ring(S[0], 0.0))), "paint", col=shade(col, 0.82))
        if inner:
            b.face(ring(Si[0], skin), "planks", col=shade(inside, 0.8))
            a_, e_ = S[0][-1], Si[0][-1]
            b.quad((a_[0], -a_[1], a_[2]), (a_[0] + skin, -e_[1], e_[2]), (a_[0] + skin, e_[1], e_[2]), (a_[0], a_[1], a_[2]), "paint", col=shade(trim, 1.15))
            for i in range(thwarts):
                t = cut + (1.0 - cut) * ((0.22 + 0.5 * i / (thwarts - 1)) if thwarts > 1 else 0.42)
                s_ = sec(t, skin)
                k = max(1, strakes - 1)
                b.box(0.24, s_[k][1] * 2 + 0.02, 0.04, "planks", col=inside, x=s_[0][0], z=s_[k][2] + (s_[-1][2] - s_[k][2]) * 0.3, bottom=True)
        if keel:
            b.beam((S[0][0][0], 0, -0.02), (S[-2][0][0], 0, -0.02 + S[-2][0][2]), w=0.07, h=0.1, mat="timber", col="darkoak")
            b.beam((S[-2][0][0], 0, S[-2][0][2] - 0.02), (S[-1][-1][0] + 0.03, 0, S[-1][-1][2] + 0.08), w=0.07, h=0.1, mat="timber", col="darkoak", up=(1, 0, 0))
    return S


# ---------------------------------------------------------------------------------------- creatures
def gull(b, x=0.0, y=0.0, z=0.0, rz=0.0, s=1.0):
    """A herring gull standing on whatever is at (x, y, z), looking toward compass rz."""
    with b.at(x, y, z, rz=rz, s=s):
        with b.detail(2):
            b.blob(0.085, 0.17, 0.085, mat="paint", col="!#f6f4ee", x=0, y=0.0, z=0.19, seg=5, rings=3, rough=0.06)
            b.blob(0.058, 0.062, 0.058, mat="paint", col="!#f6f4ee", x=0, y=-0.15, z=0.3, seg=5, rings=2, rough=0.04)
            b.beam((0, -0.2, 0.3), (0, -0.29, 0.275), w=0.03, mat="paint", col="!#e8a531", caps=False)
            for sx in (-1, 1):
                b.box(0.025, 0.26, 0.085, "paint", col="!#9aa3ab", x=sx * 0.082, y=0.05, z=0.17, bottom=True)
                b.beam((sx * 0.035, 0.0, 0.0), (sx * 0.035, 0.0, 0.12), w=0.015, mat="paint", col="!#e8a531", caps=False)
            b.box(0.09, 0.1, 0.03, "paint", col="!#3a3a3e", y=0.2, z=0.185, bottom=True)


def cat(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="!#d98a3d", s=1.0):
    """A cat sitting and watching the fish, looking toward compass rz."""
    with b.at(x, y, z, rz=rz, s=s):
        with b.detail(2):
            b.blob(0.105, 0.135, 0.17, mat="paint", col=col, x=0, y=0.03, z=0.17, seg=6, rings=3, rough=0.05)
            b.blob(0.082, 0.08, 0.075, mat="paint", col=col, x=0, y=-0.07, z=0.39, seg=6, rings=3, rough=0.04)
            for sx in (-1, 1):
                q = [(sx * 0.075, -0.07, 0.43), (sx * 0.02, -0.07, 0.45), (sx * 0.055, -0.065, 0.52)]
                b.face(q if sx > 0 else list(reversed(q)), "paint", col=shade(col, 0.85))
                b.face(list(reversed(q)) if sx > 0 else q, "paint", col=shade(col, 0.85))
            pts = [(0.06, 0.14, 0.03), (0.2, 0.12, 0.03), (0.27, 0.0, 0.03), (0.24, -0.1, 0.05)]
            for a, e in zip(pts, pts[1:]):
                b.beam(a, e, w=0.04, mat="paint", col=col, caps=False)
