"""Petalwake town kit, second layer: the things buildings are dressed with.

Everything here is written with kit primitives and can be read as examples for making new parts.
Positions on a wall are given the wall's natural way: metres from its left end on a flat Wall,
compass degrees on a round Ring (0 = front, 90 = right). Heights are metres above the wall's base.

Detail levels used here: 0 = structure (always drawn), 1 = things that shape the silhouette or
read at a few hundred metres (frames, shutters, railings, chimney pots), 2 = fine dressing.
"""
import math

from kit import C, M, PAL, lerp, mix, rad, shade, vadd, vmul, vsub
from kit import _Surface


def _cut(s, u, *a, **kw):
    """Cut an opening by metres along the wall, whatever kind of wall it is."""
    return _Surface.opening(s, u, *a, **kw)

FLOWERS = ["#e8497a", "#f2a0bd", "#f4f1e4", "#f5c842", "#b08ae6", "#e85d3a", "#ffffff", "#f07fa8"]


# ---------------------------------------------------------------------------------------- openings
def window(s, pos, z, w=0.85, h=1.25, arch=0.0, frame="ivory", bars=(1, 1), shutters=None, sill=True, lintel="stone", box=None,
           depth=None, glass=None, ajar=None):
    """A window: cuts the opening and dresses it. shutters = paint colour (or None); box = True for a flower box;
    lintel = 'stone', 'timber' or None; bars = (vertical, horizontal) glazing bars; arch = height of a curved head."""
    b = s.b
    u = s.U(pos)
    op = _cut(s, u, z, w, h, arch=arch, depth=depth, pane="glass", pane_col=glass)
    d = op["d"]
    rng = b.rng
    aj = rng.uniform(4, 22) if ajar is None else ajar
    boxcols = [rng.choice(FLOWERS) for _ in range(6)]

    def deco():
        with s.onu(u, z):
            fy = d * 0.62
            ft = 0.055
            hs = h - arch
            with b.detail(1):
                b.beam((-w / 2 + ft / 2, fy, 0), (-w / 2 + ft / 2, fy, hs), w=ft, h=0.07, mat="planks", col=frame, up=(0, 1, 0))
                b.beam((w / 2 - ft / 2, fy, 0), (w / 2 - ft / 2, fy, hs), w=ft, h=0.07, mat="planks", col=frame, up=(0, 1, 0))
                b.beam((-w / 2, fy, ft / 2), (w / 2, fy, ft / 2), w=0.07, h=ft, mat="planks", col=frame, up=(0, 0, 1))
                if arch > 1e-4:
                    n = 6
                    pts = [(-(w / 2 - ft / 2) * math.cos(math.pi * i / n), fy, hs + (arch - ft / 2) * math.sin(math.pi * i / n)) for i in range(n + 1)]
                    for i in range(n):
                        b.beam(pts[i], pts[i + 1], w=0.07, h=ft, mat="planks", col=frame, up=(0, 1, 0), caps=False)
                else:
                    b.beam((-w / 2, fy, h - ft / 2), (w / 2, fy, h - ft / 2), w=0.07, h=ft, mat="planks", col=frame, up=(0, 0, 1))
            with b.detail(2):
                nv, nh = bars
                for i in range(nv):
                    x = -w / 2 + w * (i + 1) / (nv + 1)
                    b.beam((x, fy + 0.01, ft), (x, fy + 0.01, h - (arch * 0.25 if arch else ft)), w=0.035, h=0.04, mat="planks", col=frame, up=(0, 1, 0), caps=False)
                for i in range(nh):
                    zz = hs * (i + 1) / (nh + 1)
                    b.beam((-w / 2 + ft, fy + 0.01, zz), (w / 2 - ft, fy + 0.01, zz), w=0.04, h=0.035, mat="planks", col=frame, up=(0, 0, 1), caps=False)
            if sill:
                with b.detail(1):
                    b.box(w + 0.18, 0.2, 0.07, "ashlar", col="stone", x=0, y=-0.02, z=-0.07, lod=1)
            if lintel == "stone" and arch < 1e-4:
                b.box(w + 0.3, 0.1, 0.2, "ashlar", col="stone", x=0, y=-0.012, z=h, lod=1)
            elif lintel == "timber" and arch < 1e-4:
                b.beam((-w / 2 - 0.2, -0.02, h + 0.09), (w / 2 + 0.2, -0.02, h + 0.09), w=0.1, h=0.18, mat="timber", col="darkoak", lod=1, up=(0, 0, 1))
            elif lintel == "stone" and arch > 1e-4:
                with b.detail(2):
                    n = 7
                    for i in range(n):
                        a = math.pi * (i + 0.5) / n
                        x, zz = -(w / 2 + 0.11) * math.cos(a), hs + (arch + 0.11) * math.sin(a)
                        with b.at(x, -0.03, zz, ry=-(90 - math.degrees(a))):
                            with b.at(rx=90):
                                b.stone(0.2, 0.24, 0.07, mat="ashlar", col="sand", jitter=0.08)
            if shutters is not None:
                sw = w / 2
                for sgn in (-1, 1):
                    with b.at(sgn * w / 2, -0.03, 0, rz=-sgn * aj):
                        x0, x1 = (-sw, 0) if sgn < 0 else (0, sw)
                        xm = (x0 + x1) / 2
                        b.box(sw - 0.02, 0.04, hs - 0.02, "planks", col=shutters, x=xm, y=-0.02, z=0.01, lod=1, bottom=True)
                        with b.detail(2):
                            for zz in (hs * 0.2, hs * 0.8):
                                b.beam((x0 + 0.03, -0.05, zz), (x1 - 0.03, -0.05, zz), w=0.025, h=0.07, mat="planks", col=shade(shutters, 0.8), up=(0, 0, 1))
            if box:
                with b.detail(2):
                    b.box(w + 0.1, 0.2, 0.17, "planks", col="darkoak", x=0, y=-0.14, z=-0.26, cap="ivy", capcol="#6b5a45")
                    for i, fc in enumerate(boxcols):
                        x = -w / 2 + (w) * (i + 0.5) / len(boxcols)
                        b.blob(0.09, 0.08, 0.07, mat="ivy", col="#8fc46a", x=x, y=-0.14, z=-0.07, seg=5, rings=2, wind=0.3, rough=0.3)
                        b.blob(0.055, 0.055, 0.05, mat="paint", col=fc, x=x + b.r(-0.03, 0.03), y=-0.17 + b.r(-0.03, 0.03), z=0.0 + b.r(0, 0.05), seg=5, rings=2, wind=0.5, rough=0.2)

    s.add(deco)
    return op


def door(s, pos, w=1.0, h=2.05, z=0.0, arch=0.0, col="green", frame="stone", steps=0, lamp=False, porch=None, porch_col=None, depth=None,
         knob=True, double=False):
    """A door: cuts the opening (bottom at z) and dresses it. frame = 'stone', 'timber' or None; steps = how many
    steps lead up to it from the street side; porch = 'gable' or 'flat' canopy; double = two leaves."""
    b = s.b
    u = s.U(pos)
    op = _cut(s, u, z, w, h, arch=arch, depth=depth, pane="planks", pane_col=col)
    d = op["d"]

    def deco():
        with s.onu(u, z):
            hs = h - arch
            with b.detail(2):
                leaf_y = d - 0.012
                for zz in (hs * 0.22, hs * 0.78):      # strap hinges
                    b.beam((-w / 2 + 0.03, leaf_y, zz), (w / 2 - 0.2 if not double else -0.06, leaf_y, zz), w=0.02, h=0.06, mat="metal", col="iron", up=(0, 0, 1), caps=False)
                    if double:
                        b.beam((w / 2 - 0.03, leaf_y, zz), (0.06, leaf_y, zz), w=0.02, h=0.06, mat="metal", col="iron", up=(0, 0, 1), caps=False)
                if double:
                    b.beam((0, leaf_y, 0.02), (0, leaf_y, hs), w=0.03, h=0.02, mat="planks", col=shade(col, 0.6), up=(0, 1, 0), caps=False)
                if knob:
                    kx = w / 2 - 0.14 if not double else 0.09
                    b.box(0.05, 0.05, 0.05, "metal", col="brass", x=kx, y=leaf_y - 0.03, z=hs * 0.48, bottom=True)
            if frame == "stone":
                with b.detail(1):
                    if arch < 1e-4:
                        b.box(w + 0.5, 0.16, 0.24, "ashlar", col="stone", x=0, y=-0.02, z=h)
                with b.detail(2):
                    n = max(3, int(hs / 0.34))
                    for i in range(n):
                        zz = hs * i / n
                        for sgn in (-1, 1):
                            ww = 0.34 if i % 2 == 0 else 0.22
                            with b.at(sgn * (w / 2 + ww / 2 - 0.02), -0.035, zz, rx=90):
                                b.stone(ww, hs / n * 0.94, 0.07, mat="ashlar", col="sand", y=-(hs / n) * 0.47, jitter=0.05)
                    if arch > 1e-4:
                        n = 9
                        for i in range(n):
                            a = math.pi * (i + 0.5) / n
                            x, zz = -(w / 2 + 0.13) * math.cos(a), hs + (arch + 0.13) * math.sin(a)
                            with b.at(x, -0.035, zz, ry=-(90 - math.degrees(a))):
                                with b.at(rx=90):
                                    b.stone(0.24, 0.3, 0.08, mat="ashlar", col="sand", jitter=0.06)
            elif frame == "timber":
                with b.detail(1):
                    for sgn in (-1, 1):
                        b.beam((sgn * (w / 2 + 0.07), -0.02, 0), (sgn * (w / 2 + 0.07), -0.02, h + 0.14), w=0.14, h=0.1, mat="timber", col="darkoak", up=(0, 1, 0))
                    b.beam((-w / 2 - 0.2, -0.02, h + 0.08), (w / 2 + 0.2, -0.02, h + 0.08), w=0.1, h=0.16, mat="timber", col="darkoak", up=(0, 0, 1))
            if steps:
                with b.detail(1):
                    for i in range(steps):          # the top step is the smallest, each one below it wider and deeper
                        k = i + 1
                        b.box(w + 0.5 + 0.12 * k, 0.3 * k + 0.1, 0.17, "ashlar", col="stone", x=0, y=-(0.3 * k + 0.1) / 2 + 0.05, z=-0.17 * (i + 1) - 0.0)
            if porch:
                pc = porch_col if porch_col is not None else "tiles"
                with b.detail(1):
                    pw, pd = w + 0.9, 0.9
                    if porch == "gable":
                        with b.at(0, -pd / 2, h + 0.28):
                            b.gable_roof(pw, pd, pitch=38, mat="tiles", ridge="y", eave=0.12, verge=0.05, course=0.3, thick=0.08, barge=False, ridge_roll=False, lod=1)
                    else:
                        with b.at(0, 0, h + 0.3):
                            b.gable_roof(pw, pd, pitch=16, mat="slate", ridge="x", half=True, eave=0.1, verge=0.06, course=0.3, thick=0.07, barge=False, lod=1)
                    for sgn in (-1, 1):
                        b.beam((sgn * (pw / 2 - 0.1), -0.02, h - 0.35), (sgn * (pw / 2 - 0.1), -pd + 0.08, h + 0.22), w=0.08, mat="timber", col="darkoak")
                        b.beam((sgn * (pw / 2 - 0.1), -0.02, h + 0.24), (sgn * (pw / 2 - 0.1), -pd + 0.05, h + 0.24), w=0.08, mat="timber", col="darkoak")
            if lamp:
                lantern_at(b, w / 2 + 0.35, -0.02, hs * 0.86)

    s.add(deco)
    return op


def lantern_at(b, x, y, z, arm=0.32):
    """A small wall lantern on an iron arm, hanging at (x, y - arm, z) in the current frame."""
    with b.detail(2):
        b.beam((x, y, z + 0.2), (x, y - arm, z + 0.2), w=0.025, mat="metal", col="iron", caps=False)
        b.beam((x, y - arm, z + 0.2), (x, y - arm, z + 0.1), w=0.02, mat="metal", col="iron", caps=False)
        b.box(0.15, 0.15, 0.2, "glow", col="#ffd88a", x=x, y=y - arm, z=z - 0.1, bottom=True)
        b.box(0.19, 0.19, 0.03, "metal", col="iron", x=x, y=y - arm, z=z + 0.1)
        b.box(0.17, 0.17, 0.025, "metal", col="iron", x=x, y=y - arm, z=z - 0.12, bottom=True)
    b.lamp(x, y - arm, z)


def lantern(s, pos, z, arm=0.32):
    u = s.U(pos)
    s.add(lambda: _on(s, u, 0, lambda b: lantern_at(b, 0, -0.01, z, arm)))


def _on(s, u, z, fn):
    with s.onu(u, z):
        fn(s.b)


# ---------------------------------------------------------------------------------------- wall dressing
def timber_frame(s, u0=0.0, u1=None, z0=0.0, z1=None, posts=None, rails=None, braces="auto", w=0.15, col="darkoak", proud=0.035, lod=1):
    """Half-timbering on a flat wall between (u0, z0) and (u1, z1): posts at the given positions (default: both
    ends and about every 1.3 m), rails at the given heights (default: bottom, top and one in between), and
    diagonal braces: 'auto' (in the end panels), 'x' (crosses in every panel), 'k', or a list of (ua, za, ub, zb)."""
    b = s.b
    u1 = s.w if u1 is None else u1
    z1 = s.h - 0.1 if z1 is None else z1
    if posts is None:
        n = max(1, round((u1 - u0) / 1.3))
        posts = [u0 + (u1 - u0) * i / n for i in range(n + 1)]
    if rails is None:
        rails = [z0, (z0 + z1) / 2, z1]
    y = -proud

    def deco():
        with b.detail(lod):
            for i, pu in enumerate(posts):
                x = min(max(pu, u0 + w / 2), u1 - w / 2)
                b.beam((x, y, z0), (x, y, z1), w=w, h=proud * 2 + 0.04, mat="timber", col=col, up=(0, 1, 0), caps=False)
            for rz in rails:
                zz = min(max(rz, z0 + w / 2), z1 - w / 2)
                b.beam((u0, y - 0.004, zz), (u1, y - 0.004, zz), w=proud * 2 + 0.04, h=w, mat="timber", col=col, up=(0, 0, 1), caps=False)
            br = braces
            if br in ("auto", "x", "k"):
                out = []
                rs = sorted(rails)
                ps = sorted(posts)
                for j in range(len(rs) - 1):
                    for i in range(len(ps) - 1):
                        end = i == 0 or i == len(ps) - 2
                        if br == "x":
                            out += [(ps[i], rs[j], ps[i + 1], rs[j + 1]), (ps[i], rs[j + 1], ps[i + 1], rs[j])]
                        elif br == "k" and i % 2 == j % 2:
                            out += [(ps[i], rs[j], ps[i + 1], rs[j + 1])]
                        elif br == "auto" and end and j == 0:
                            out += [(ps[i], rs[j + 1], ps[i + 1], rs[j])] if i == 0 else [(ps[i], rs[j], ps[i + 1], rs[j + 1])]
                br = out
            for (ua, za, ub, zb) in br or []:
                if s._in_hole((ua + ub) / 2, (za + zb) / 2):
                    continue
                b.beam((ua, y + 0.006, za), (ub, y + 0.006, zb), w=w * 0.8, h=proud * 2 + 0.03, mat="timber", col=col, up=(0, 1, 0), caps=False)

    s.add(deco)


def stones(s, n=30, size=(0.3, 0.62), proud=0.07, z0=0.0, z1=None, u0=0.0, u1=None, mat=None, col=None, lod=2):
    """Individual stones standing a little proud of a wall, scattered between the given bounds (metres along the
    wall, or the whole way round a tower): the chunky hand-laid look, and a broken silhouette."""
    b = s.b
    z1 = s.h if z1 is None else z1
    u1 = s.w if u1 is None else u1
    rng = b.rng
    spots = []
    for _ in range(n * 4):
        if len(spots) >= n:
            break
        w = rng.uniform(*size)
        h = w * rng.uniform(0.45, 0.75)
        u, z = rng.uniform(u0 + w / 2, u1 - w / 2), rng.uniform(z0 + 0.05, max(z1 - h - 0.05, z0 + 0.06))
        if s._in_hole(u, z + h / 2) or s._in_hole(u - w / 2, z) or s._in_hole(u + w / 2, z + h):
            continue
        spots.append((u, z, w, h, rng.uniform(-4, 4)))

    def deco():
        for (u, z, w, h, tilt) in spots:
            with s.onu(u, z):
                with b.at(0, 0.02, h / 2, ry=tilt):
                    with b.at(rx=90):
                        b.stone(w, h, proud + 0.02, mat=mat or s.mat, col=col if col is not None else s.col, lod=lod, jitter=0.16)

    s.add(deco)


def exposed(s, where="corners", n=10, mat="masonry", col="warm", size=(0.28, 0.5)):
    """Patches of bare stonework where the plaster has fallen away: at the wall's 'corners', along its 'base',
    or 'both'. (On a plastered wall this is what makes it look old and loved.)"""
    w, h = s.w, s.h
    if where in ("corners", "both"):
        stones(s, n=n // 2 + 1, size=size, proud=0.03, z0=0.1, z1=h * 0.75, u0=0.0, u1=min(1.1, w * 0.25), mat=mat, col=col)
        stones(s, n=n // 2 + 1, size=size, proud=0.03, z0=0.1, z1=h * 0.6, u0=max(w - 1.1, w * 0.75), u1=w, mat=mat, col=col)
    if where in ("base", "both"):
        stones(s, n=n, size=size, proud=0.03, z0=0.0, z1=min(1.2, h * 0.3), mat=mat, col=col)


def ivy(s, pos, z, w=1.6, h=2.4, n=9, col="#7fb760", lod=1):
    """A patch of climbing ivy on a wall, about w wide and h tall, its foot at (pos, z)."""
    b = s.b
    u = s.U(pos)
    rng = b.rng
    lumps = [(rng.uniform(-w / 2, w / 2) * (1 - 0.5 * t), t * h, rng.uniform(0.28, 0.5) * (1.1 - 0.4 * t)) for t in [rng.random() ** 0.8 for _ in range(n)]]

    def deco():
        with s.onu(u, z):
            for (x, zz, r) in lumps:
                b.blob(r, r * 0.3, r * 0.85, mat="ivy", col=shade(col, rng.uniform(0.8, 1.15)), x=x, y=-0.04, z=zz, lod=lod, seg=6, rings=3, wind=0.25, rough=0.3)

    s.add(deco)


def plinth(body, h=0.7, out=0.07, mat="masonry", col="warm", skirt=3.0):
    """A stone base course round a block, plus the hidden foundation that keeps it grounded on a slope.
    Doorways (any opening that starts below the top of the plinth) are left clear."""
    b = body.b

    def deco():
        for wl in body.walls:
            cuts = sorted((max(o["u0"] - 0.04, -out), min(o["u1"] + 0.04, wl.w + out)) for o in wl.ops if o["z0"] < h - 0.05)
            spans, a = [], -out
            for c0, c1 in cuts:
                if c0 > a + 0.02:
                    spans.append((a, c0))
                a = max(a, c1)
            if wl.w + out > a + 0.02:
                spans.append((a, wl.w + out))
            with b.frame(wl.m):
                for ua, ub in spans:
                    b.box(ub - ua, out + 0.05, h, mat, col=col, x=(ua + ub) / 2, y=(0.05 - out) / 2, z=0, lod=0)
                b.box(wl.w + 2 * out, out + 0.05, skirt, mat, col=shade(col, 0.85), x=wl.w / 2, y=(0.05 - out) / 2, z=-skirt, top=False, lod=0)

    if body.front.done:
        deco()
    else:
        body.front.add(deco)


def round_base(b, r, h=0.9, out=0.25, mat="masonry", col="warm", skirt=3.0, seg=24, x=0.0, y=0.0, z=0.0, ring=None):
    """A battered (spreading) stone foot for a round tower, plus its hidden foundation. Pass ring=<the tower's
    wall> and its doorways are left clear (otherwise the foot runs right round and buries a door's threshold)."""
    prof = [(r + out, 0.0), (r + out * 0.9, h * 0.5), (r + 0.02, h)]
    if ring is None:
        with b.at(x, y, z):
            b.revolve([(r + out, -skirt)] + prof, mat, col=col, seg=seg, lod=0)
        return

    def deco():
        doors = sorted(((math.degrees(o["u0"] / ring.rref) - 3.0) % 360.0, math.degrees((o["u1"] - o["u0"]) / ring.rref) + 6.0) for o in ring.ops if o["z0"] < h - 0.05)
        with b.frame(ring.m):
            b.revolve([(r + out, -skirt), (r + out, 0.0)], mat, col=col, seg=seg, lod=0)
            if not doors:
                b.revolve(prof, mat, col=col, seg=seg, lod=0)
                return
            for i, (a0, wd) in enumerate(doors):
                start = a0 + wd
                end = doors[(i + 1) % len(doors)][0] + (360.0 if i == len(doors) - 1 else 0.0)
                if end - start > 1.0:
                    n = max(2, int(seg * (end - start) / 360.0))
                    b.revolve(prof, mat, col=col, seg=n, a0=start, a1=end, lod=0)
                    for ang in (start, end):          # close the cut ends
                        with b.at(rz=ang):
                            pts = [(0, -(r - 0.05), 0.0), (0, -(r + out), 0.0), (0, -(r + out * 0.9), h * 0.5), (0, -(r + 0.02), h), (0, -(r - 0.05), h)]
                            b.face(pts if ang == end else list(reversed(pts)), mat, col=col, lod=0)

    if ring.done:
        deco()
    else:
        ring.add(deco)


def band(body, z, h=0.18, out=0.06, mat="ashlar", col="stone", lod=1):
    """A string course (a thin projecting band) round a block at height z."""
    b = body.b
    with b.at(body.x, body.y, body.z + z):
        b.box(body.w + 2 * out, body.d + 2 * out, h, mat, col=col, y=0, lod=lod, bottom=True)


def ring_band(b, r, z, h=0.2, out=0.08, mat="ashlar", col="stone", seg=24, lod=1, x=0.0, y=0.0):
    """A projecting band round a tower of radius r at height z."""
    with b.at(x, y, z):
        b.revolve([(r - 0.02, 0.0), (r + out, 0.0), (r + out, h), (r - 0.02, h)], mat, col=col, seg=seg, lod=lod)


def quoins(body, mat="ashlar", col="stone", size=(0.52, 0.3, 0.36), z0=0.0, z1=None, proud=0.035, corners="frbl", lod=2):
    """Dressed corner stones, long and short alternately, up the corners of a block."""
    b = body.b
    z1 = body.h if z1 is None else z1
    L, S, H = size
    n = max(1, int((z1 - z0) / H))
    hh = (z1 - z0) / n
    cs = {"f": (-1, -1), "r": (1, -1), "b": (1, 1), "l": (-1, 1)}
    for key in corners:
        sx, sy = cs[key]
        cx, cy = body.x + sx * body.w / 2, body.y + sy * body.d / 2
        for i in range(n):
            lx, ly = (L, S) if i % 2 == 0 else (S, L)
            with b.at(cx - sx * (lx / 2 - proud), cy - sy * (ly / 2 - proud), body.z + z0 + hh * i):
                b.stone(lx, ly, hh * 0.96, mat=mat, col=col, lod=lod, ch=0.12, jitter=0.05)


def crenels(b, r=None, w=None, d=None, z=0.0, n=None, h=0.7, t=0.35, mat="masonry", col="warm", wall=0.5, x=0.0, y=0.0, seg=24):
    """Battlements: a low parapet and merlons round a tower top of radius r, or a rectangle w by d, at height z."""
    with b.at(x, y, z):
        if r is not None:
            b.revolve([(r, 0.0), (r, wall), (r - t, wall), (r - t, 0.0)], mat, col=col, seg=seg, lod=0)
            n = n or max(6, int(2 * math.pi * r / 1.3))
            with b.detail(1):
                for i in range(n):
                    a = 360.0 * i / n
                    with b.at(rz=a):
                        b.stone(2 * math.pi * r / n * 0.55, t, h, mat=mat, col=col, lod=1, y=-(r - t / 2), z=wall, ch=0.1, jitter=0.06)
        else:
            hw, hd = w / 2, d / 2
            for (ax, ay, bx, by) in ((-hw, -hd, hw, -hd), (hw, -hd, hw, hd), (hw, hd, -hw, hd), (-hw, hd, -hw, -hd)):
                L = math.hypot(bx - ax, by - ay)
                ang = math.degrees(math.atan2(by - ay, bx - ax))
                with b.at(ax, ay, 0, rz=ang):
                    b.box(L, t, wall, mat, col=col, x=L / 2, y=t / 2, lod=0)
                    m = n or max(2, int(L / 1.3))
                    with b.detail(1):
                        for i in range(m):
                            b.stone(L / m * 0.55, t, h, mat=mat, col=col, lod=1, x=L * (i + 0.5) / m, y=t / 2, z=wall, ch=0.1, jitter=0.06)


def ruin_top(b, r, z, n=None, hmin=0.15, hmax=1.5, t=0.5, mat="masonry", col="warm", grass=True, x=0.0, y=0.0, arc=(0.0, 360.0)):
    """A broken, weathered wall top round a tower of radius r at height z: stones of uneven height over the given
    arc (degrees), highest in the middle of it, with tufts of grass."""
    rng = b.rng
    a0, a1 = arc
    n = n or max(8, int(2 * math.pi * r * (a1 - a0) / 360.0 / 0.62))
    with b.at(x, y, z):
        for i in range(n):
            t0 = (i + 0.5) / n
            a = a0 + (a1 - a0) * t0
            k = math.sin(math.pi * t0) ** 0.7 if (a1 - a0) < 359 else 0.5 + 0.5 * math.sin(t0 * 2 * math.pi * 2 + 1.0)
            hh = lerp(hmin, hmax, k) * rng.uniform(0.7, 1.15)
            rows = max(1, int(hh / 0.42))
            for j in range(rows):
                with b.at(rz=a + rng.uniform(-2, 2)):
                    wd = 2 * math.pi * r * (a1 - a0) / 360.0 / n * rng.uniform(0.86, 1.08)
                    b.stone(wd, t * rng.uniform(0.85, 1.05), hh / rows, mat=mat, col=col, lod=1 if j == 0 else 2, y=-(r - t / 2 + rng.uniform(-0.03, 0.05)), z=hh / rows * j, jitter=0.14)
            if grass and rng.random() < 0.4:
                with b.at(rz=a):
                    b.blob(0.22, 0.2, 0.16, mat="ivy", col="#8fc46a", y=-(r - t / 2), z=hh + 0.08, lod=2, seg=5, rings=2, wind=0.4, rough=0.35)


# ---------------------------------------------------------------------------------------- railings, galleries, stairs
def railing(b, pts, h=1.0, style="balusters", col="darkoak", mat="timber", closed=False, post=0.11, gap=0.2, lod=1, posts_at=1.7):
    """A railing along a line of points [(x, y, z), ...] (in the current frame). style = 'balusters' (uprights),
    'cross' (X braces), 'iron' (thin metal bars) or 'solid' (boarded)."""
    if style == "iron":
        mat, col, post = "metal", "iron", 0.05
    P = list(pts) + ([pts[0]] if closed else [])
    for i in range(len(P) - 1):
        a, c = P[i], P[i + 1]
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        if L < 1e-4:
            continue
        n = max(1, round(L / posts_at))
        up = lambda p, dz: (p[0], p[1], p[2] + dz)
        for k in range(n + (0 if (closed or i < len(P) - 2) else 1)):
            p = (a[0] + (c[0] - a[0]) * k / n, a[1] + (c[1] - a[1]) * k / n, a[2] + (c[2] - a[2]) * k / n)
            with b.detail(lod):
                b.beam(p, up(p, h + 0.04), w=post, mat=mat, col=col, caps=True)
        with b.detail(lod):
            b.beam(up(a, h), up(c, h), w=post * 0.9, h=post * 0.7, mat=mat, col=col, caps=False)
            if style != "solid":
                b.beam(up(a, 0.12), up(c, 0.12), w=post * 0.6, h=post * 0.6, mat=mat, col=col, caps=False)
        if style in ("balusters", "iron"):
            m = max(1, int(L / gap))
            with b.detail(2):
                for k in range(1, m):
                    p = (a[0] + (c[0] - a[0]) * k / m, a[1] + (c[1] - a[1]) * k / m, a[2] + (c[2] - a[2]) * k / m)
                    b.beam(up(p, 0.12), up(p, h), w=post * (0.38 if style == "balusters" else 0.3), mat=mat, col=col, caps=False)
        elif style == "cross":
            with b.detail(2):
                for k in range(n):
                    p0 = (a[0] + (c[0] - a[0]) * k / n, a[1] + (c[1] - a[1]) * k / n, a[2] + (c[2] - a[2]) * k / n)
                    p1 = (a[0] + (c[0] - a[0]) * (k + 1) / n, a[1] + (c[1] - a[1]) * (k + 1) / n, a[2] + (c[2] - a[2]) * (k + 1) / n)
                    b.beam(up(p0, 0.12), up(p1, h), w=post * 0.5, mat=mat, col=col, caps=False)
                    b.beam(up(p0, h), up(p1, 0.12), w=post * 0.5, mat=mat, col=col, caps=False)
        elif style == "solid":
            with b.detail(lod):
                b.quad(up(a, 0.05), up(c, 0.05), up(c, h), up(a, h), "planks", col=col)
                b.quad(up(c, 0.05), up(a, 0.05), up(a, h), up(c, h), "planks", col=shade(col, 0.85))


def circle(r, n, z=0.0, a0=0.0, a1=360.0):
    """n+1 points round an arc of radius r (compass degrees), for railings and the like."""
    return [(r * math.sin(rad(a0 + (a1 - a0) * i / n)), -r * math.cos(rad(a0 + (a1 - a0) * i / n)), z) for i in range(n + 1)]


def gallery(b, r_in, r_out, z, seg=20, floor="planks", floor_col="greyoak", rail="balusters", rail_col="darkoak", rail_h=1.0, brackets=None,
            bracket_drop=1.2, gap=None, thick=0.14, edge_col="darkoak", x=0.0, y=0.0):
    """A walkway round a tower: a ring floor from r_in to r_out at height z, carried on brackets, with a railing.
    brackets = how many (default: one every ~1.4 m); gap = (a0, a1) compass degrees of railing left open (where
    the rider steps on). This is the classic landing place: put a `b.pad(...)` on it."""
    with b.at(x, y, z):
        b.disc(r_out, floor, col=floor_col, seg=seg, r_in=r_in, lod=0)
        b.disc(r_out, "planks", col=shade(edge_col, 0.8), seg=seg, r_in=r_in, z=-thick, down=True, lod=0)
        b.revolve([(r_out, -thick), (r_out, 0.0)], "planks", col=edge_col, seg=seg, lod=0)
        n = brackets or max(6, int(2 * math.pi * r_out / 1.4))
        with b.detail(1):
            for i in range(n):
                with b.at(rz=360.0 * (i + 0.5) / n):
                    b.beam((0, -r_in + 0.02, -bracket_drop), (0, -r_out + 0.12, -thick - 0.02), w=0.13, mat="timber", col=edge_col)
                    b.beam((0, -r_in + 0.05, -thick - 0.08), (0, -r_out + 0.05, -thick - 0.08), w=0.12, h=0.14, mat="timber", col=edge_col)
        if rail:
            rr = r_out - 0.08
            if gap:
                a0, a1 = gap
                nn = max(4, int(seg * (360 - (a1 - a0)) / 360))
                railing(b, circle(rr, nn, 0.0, a1, a0 + 360.0), h=rail_h, style=rail, col=rail_col)
            else:
                railing(b, circle(rr, seg, 0.0)[:-1], h=rail_h, style=rail, col=rail_col, closed=True)


def balcony(s, pos, z, w=2.2, out=1.1, rail="balusters", rail_col="darkoak", floor="planks", floor_col="greyoak", brackets=True, rail_h=0.95, thick=0.12):
    """A small balcony projecting from a wall, centred on pos at height z (give it a door or a tall window)."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            b.box(w, out, thick, floor, col=floor_col, x=0, y=-out / 2, z=-thick, bottom=True, lod=0)
            if brackets:
                with b.detail(1):
                    for sgn in (-1, 1):
                        b.beam((sgn * (w / 2 - 0.12), 0.0, -thick - 0.85), (sgn * (w / 2 - 0.12), -out + 0.1, -thick - 0.02), w=0.11, mat="timber", col=rail_col)
            railing(b, [(-w / 2 + 0.06, -0.02, 0), (-w / 2 + 0.06, -out + 0.06, 0), (w / 2 - 0.06, -out + 0.06, 0), (w / 2 - 0.06, -0.02, 0)], h=rail_h, style=rail, col=rail_col)

    s.add(deco)


def stairs(b, w=1.1, rise=0.18, run=0.28, n=8, mat="ashlar", col="stone", lod=1, solid=True, rail=None):
    """A straight flight climbing toward +y from the origin of the current frame: n steps, each `rise` high."""
    with b.detail(lod):
        for i in range(n):
            if solid:
                b.box(w, run * (n - i), rise, mat, col=col, x=0, y=run * i + run * (n - i) / 2, z=rise * i)
            else:
                b.box(w, run + 0.04, 0.06, "planks", col="greyoak", x=0, y=run * (i + 0.5), z=rise * (i + 1) - 0.06, bottom=True)
        if not solid:
            for sgn in (-1, 1):
                b.beam((sgn * (w / 2 - 0.04), 0, 0), (sgn * (w / 2 - 0.04), run * n, rise * n), w=0.07, h=0.22, mat="timber", col="darkoak")
    if rail:
        for sgn in (-1, 1):
            railing(b, [(sgn * (w / 2 - 0.05), 0, rise * 0.5), (sgn * (w / 2 - 0.05), run * n, rise * n)], h=0.95, style=rail, posts_at=1.4)


def ladder(b, h, w=0.45, col="greyoak"):
    """A ladder standing against the wall at the origin of the current frame (leaning back toward +y)."""
    with b.detail(2):
        lean = 0.12 * h
        for sgn in (-1, 1):
            b.beam((sgn * w / 2, -lean, 0), (sgn * w / 2, 0, h), w=0.05, mat="timber", col=col)
        n = int(h / 0.3)
        for i in range(1, n):
            t = i / n
            b.beam((-w / 2, -lean * (1 - t), h * t), (w / 2, -lean * (1 - t), h * t), w=0.035, mat="timber", col=col, caps=False)


def landing_mark(b, r=1.4, z=0.012, col="!#f4e9c8", n=24):
    """A painted ring and compass points on a platform floor: marks a landing place."""
    with b.detail(2):
        with b.at(z=z):
            b.disc(r, "paint", col=col, seg=n, r_in=r - 0.09)
            for k in range(4):
                with b.at(rz=90 * k):
                    b.tri((-0.1, -r + 0.12, 0), (0.1, -r + 0.12, 0), (0, -r + 0.48, 0), "paint", col=col)


# ---------------------------------------------------------------------------------------- roof furniture
def chimney(b, x, y, z, h, w=0.6, d=0.5, mat="brick", col=None, pots=1, cap=True, smoke=True, pot_col="#c9764a"):
    """A chimney stack rising h from z (start it below the roof surface so it passes through). Adds smoke."""
    with b.at(x, y, z):
        b.box(w, d, h, mat, col=col, lod=0)
        if cap:
            b.box(w + 0.14, d + 0.14, 0.1, "ashlar", col="stone", z=h, lod=1, bottom=True)
        top = h + (0.1 if cap else 0.0)
        with b.detail(1):
            for i in range(pots):
                px = (i - (pots - 1) / 2) * 0.3
                with b.at(px, 0, top):
                    b.revolve([(0.11, 0.0), (0.09, 0.3), (0.105, 0.34), (0.08, 0.36)], "paint", col=pot_col, seg=8)
        if smoke:
            b.smoke(0, 0, top + 0.4)


def dormer(b, x, y, z, w=1.2, h=1.0, depth=1.5, face=0.0, kind="gable", wall="plaster", col="cream", roof="tiles", roof_col=None, pitch=42,
           frame="ivory", shutters=None, lod=1):
    """A dormer window standing on a roof: its front face centred at (x, y, z) looking toward compass `face`
    (0 = the building's front), running back `depth` into the roof. kind = 'gable', 'shed' or 'hip'."""
    with b.at(x, y, z, rz=face):
        with b.detail(lod):
            bd = b.body(w, depth, h, mat=wall, col=col, x=0, y=depth / 2, foot=False, lod=lod)
            window(bd.front, w / 2, 0.12, w=w * 0.55, h=h * 0.72, frame=frame, bars=(1, 1), shutters=shutters, sill=False, lintel=None, depth=0.12)
            if kind == "gable":
                bd.gable(ridge="y", pitch=pitch, mat=roof, col=roof_col, eave=0.14, verge=0.14, course=0.3, thick=0.08, lod=lod, barge=True)
            elif kind == "hip":
                bd.hip(pitch=pitch, mat=roof, col=roof_col, eave=0.14, course=0.3, thick=0.08, lod=lod)
            else:
                b.gable_roof(w, depth, pitch=14, mat=roof, col=roof_col, x=0, y=depth, z=h, ridge="x", half=True, eave=0.16, verge=0.12, course=0.3, thick=0.07, lod=lod, barge=False)
            for wl in bd.walls:
                wl.lod = lod
                wl.emit()


def weathervane(b, x=0.0, y=0.0, z=0.0, h=1.5, col="iron", shape="arrow"):
    """A weathervane on a pole rising from (x, y, z)."""
    with b.at(x, y, z):
        with b.detail(1):
            b.tube((0, 0, 0), (0, 0, h), r=0.025, mat="metal", col=col, n=5)
        with b.detail(2):
            b.beam((-0.35, 0, h * 0.62), (0.35, 0, h * 0.62), w=0.02, mat="metal", col=col, caps=False)
            b.beam((0, -0.35, h * 0.62), (0, 0.35, h * 0.62), w=0.02, mat="metal", col=col, caps=False)
            with b.at(z=h * 0.88, rz=b.r(0, 360)):
                b.beam((-0.45, 0, 0), (0.4, 0, 0), w=0.02, mat="metal", col=col, caps=False)
                for sgn in (1, -1):
                    pts = [(0.4, 0, -0.1), (0.62, 0, 0), (0.4, 0, 0.1)] if shape != "x" else [(0.4, 0, -0.1), (0.62, 0, 0), (0.4, 0, 0.1)]
                    b.face(pts if sgn > 0 else list(reversed(pts)), "metal", col="brass")
                    tail = [(-0.45, 0, -0.14), (-0.22, 0, 0), (-0.45, 0, 0.14), (-0.6, 0, 0.0)]
                    b.face(tail if sgn > 0 else list(reversed(tail)), "metal", col="brass")
            b.box(0.09, 0.09, 0.09, "metal", col="brass", z=h, bottom=True)


def flag(b, x=0.0, y=0.0, z=0.0, pole=2.2, w=1.3, h=0.7, col="stripe_red", kind="pennant", pole_col="darkoak", lean=0.0):
    """A flag on a pole rising from (x, y, z); it flies in the game's wind. kind = 'pennant' (tapering) or 'banner'."""
    with b.at(x, y, z, rx=lean):
        with b.detail(1):
            b.tube((0, 0, 0), (0, 0, pole), r=0.035, mat="planks", col=pole_col, n=5)
            b.box(0.09, 0.09, 0.09, "metal", col="brass", z=pole, bottom=True)
            nx = 5
            for i in range(nx):
                t0, t1 = i / nx, (i + 1) / nx
                h0 = h * (1 - 0.85 * t0) if kind == "pennant" else h
                h1 = h * (1 - 0.85 * t1) if kind == "pennant" else h
                zt = pole - 0.06
                p = [(w * t0 + 0.03, 0, zt - h / 2 - h0 / 2), (w * t1 + 0.03, 0, zt - h / 2 - h1 / 2), (w * t1 + 0.03, 0, zt - h / 2 + h1 / 2), (w * t0 + 0.03, 0, zt - h / 2 + h0 / 2)]
                wd = (t0, t1, t1, t0)
                b.face(p, "cloth", col=col, wind=wd)
                b.face(list(reversed(p)), "cloth", col=shade(col, 0.9), wind=tuple(reversed(wd)))


def laundry(b, p0, p1, n=5, sag=0.35, cols=None):
    """A washing line from p0 to p1 with n pieces of laundry that flap in the wind."""
    rng = b.rng
    cols = cols or ["linen", "#f2c4cf", "#bcd4ea", "#fff3d6", "#e8e2f2", "linen", "#f6d9a8"]
    N = 8
    pt = lambda t: (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t) - sag * 4 * t * (1 - t))
    with b.detail(1):
        for i in range(N):
            b.beam(pt(i / N), pt((i + 1) / N), w=0.018, mat="cloth", col="#8a7a66", caps=False)
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        dx, dy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
        for k in range(n):
            t = (k + 0.5 + rng.uniform(-0.2, 0.2)) / n
            c = pt(t)
            ww, hh = rng.uniform(0.35, 0.75), rng.uniform(0.45, 0.9)
            col = C(rng.choice(cols))
            rows = 3
            for j in range(rows):
                z0, z1 = c[2] - hh * j / rows, c[2] - hh * (j + 1) / rows
                w0, w1 = j / rows, (j + 1) / rows
                p = [(c[0] - dx * ww / 2, c[1] - dy * ww / 2, z1), (c[0] + dx * ww / 2, c[1] + dy * ww / 2, z1), (c[0] + dx * ww / 2, c[1] + dy * ww / 2, z0), (c[0] - dx * ww / 2, c[1] - dy * ww / 2, z0)]
                b.face(p, "cloth", col=col, wind=(w1, w1, w0, w0))
                b.face(list(reversed(p)), "cloth", col=shade(col, 0.88), wind=(w0, w0, w1, w1))


def sign(s, pos, z, emblem="star", col="mustard", board="ivory", out=0.75, w=0.62, h=0.5):
    """A hanging shop sign on an iron bracket. emblem = 'star', 'fish', 'boot', 'loaf', 'key', 'mug', 'anchor',
    'needle', 'book', 'flower', 'moon', 'bell', 'hat'."""
    b = s.b
    u = s.U(pos)
    shapes = {
        "star": [(0, .22), (.06, .07), (.21, .07), (.09, -.03), (.13, -.18), (0, -.09), (-.13, -.18), (-.09, -.03), (-.21, .07), (-.06, .07)],
        "fish": [(-.22, 0), (-.08, .1), (.1, .08), (.16, 0), (.24, .1), (.24, -.1), (.16, 0), (.1, -.08), (-.08, -.1)],
        "boot": [(-.1, .2), (.04, .2), (.04, -.04), (.2, -.1), (.2, -.2), (-.1, -.2)],
        "loaf": [(-.2, -.1), (.2, -.1), (.22, .02), (.12, .12), (-.12, .12), (-.22, .02)],
        "key": [(-.22, .03), (.06, .03), (.1, .11), (.2, .11), (.24, 0), (.2, -.11), (.1, -.11), (.06, -.03), (-.1, -.03), (-.1, -.1), (-.15, -.1), (-.15, -.03), (-.22, -.03)],
        "mug": [(-.14, .16), (.1, .16), (.1, .08), (.2, .08), (.2, -.08), (.1, -.08), (.1, -.18), (-.14, -.18)],
        "anchor": [(-.03, .22), (.03, .22), (.03, -.08), (.16, -.02), (.2, -.1), (0, -.22), (-.2, -.1), (-.16, -.02), (-.03, -.08)],
        "needle": [(-.22, -.2), (-.18, -.22), (.2, .16), (.22, .22), (.16, .2)],
        "book": [(-.2, .14), (0, .1), (.2, .14), (.2, -.14), (0, -.18), (-.2, -.14)],
        "flower": [(0, .22), (.08, .08), (.22, .06), (.12, -.05), (.14, -.2), (0, -.12), (-.14, -.2), (-.12, -.05), (-.22, .06), (-.08, .08)],
        "moon": [(.02, .22), (-.14, .14), (-.2, 0), (-.14, -.14), (.02, -.22), (-.06, -.1), (-.08, 0), (-.06, .1)],
        "bell": [(-.04, .2), (.04, .2), (.12, .06), (.14, -.1), (.2, -.16), (-.2, -.16), (-.14, -.1), (-.12, .06)],
        "hat": [(0, .24), (.1, -.06), (.24, -.12), (.24, -.18), (-.24, -.18), (-.24, -.12), (-.1, -.06)],
    }
    poly = shapes.get(emblem, shapes["star"])

    def deco():
        with s.onu(u, z):
            with b.detail(1):
                b.beam((0, -0.01, 0.06), (0, -out - 0.05, 0.06), w=0.03, mat="metal", col="iron", caps=False)
                b.beam((0, -0.01, -0.3), (0, -out * 0.6, 0.04), w=0.025, mat="metal", col="iron", caps=False)
                with b.at(0, -out * 0.55, -h / 2 - 0.08):
                    b.box(0.045, w, h, "paint", col=board, bottom=True)
            with b.detail(2):
                with b.at(0, -out * 0.55, -h / 2 - 0.08 + h / 2):
                    for sx in (-1, 1):
                        cen = (sx * 0.03, 0, 0)
                        ring = [(sx * 0.03, -px * sx, pz) for px, pz in poly]
                        for i in range(len(ring)):
                            b.tri(cen, ring[i], ring[(i + 1) % len(ring)], "paint", col=col)
                for yy in (-out * 0.55 - w * 0.35, -out * 0.55 + w * 0.35):
                    b.beam((0, yy, 0.05), (0, yy, -0.08), w=0.015, mat="metal", col="iron", caps=False)

    s.add(deco)


def awning(s, pos, z, w=2.4, out=1.2, drop=0.55, cols=("stripe_red", "linen"), stripes=None, poles=True):
    """A striped cloth awning over a shop front: top edge on the wall at height z, sloping out and down."""
    b = s.b
    u = s.U(pos)
    n = stripes or max(4, int(w / 0.3))

    def deco():
        with s.onu(u, z):
            with b.detail(1):
                for i in range(n):
                    x0, x1 = -w / 2 + w * i / n, -w / 2 + w * (i + 1) / n
                    c = cols[i % len(cols)]
                    p = [(x0, -out, -drop), (x1, -out, -drop), (x1, 0, 0), (x0, 0, 0)]
                    b.face(p, "cloth", col=c, wind=(0.25, 0.25, 0, 0))
                    b.face(list(reversed(p)), "cloth", col=shade(c, 0.8), wind=(0, 0, 0.25, 0.25))
                    v = [(x0, -out, -drop - 0.16), (x1, -out, -drop - 0.16), (x1, -out, -drop), (x0, -out, -drop)]
                    b.face(v, "cloth", col=c, wind=(0.6, 0.6, 0.25, 0.25))
                    b.face(list(reversed(v)), "cloth", col=shade(c, 0.8), wind=(0.25, 0.25, 0.6, 0.6))
                if poles:
                    for sgn in (-1, 1):
                        b.beam((sgn * (w / 2 - 0.03), -0.02, -drop - 0.5), (sgn * (w / 2 - 0.03), -out, -drop), w=0.03, mat="metal", col="iron", caps=False)

    s.add(deco)


def clock(s, pos, z, r=0.75, face="ivory", hands="black", rim="brass", hour=10, minute=10):
    """A clock face on a wall, centred at (pos, z)."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            with b.at(rx=90):                      # now local z points out of the wall, y points up it
                with b.detail(1):
                    b.disc(r, "paint", col=face, seg=20, z=0.05)
                    b.revolve([(r, 0.0), (r + 0.09, 0.02), (r + 0.09, 0.09), (r, 0.11)], "metal", col=rim, seg=20)
                with b.detail(2):
                    for k in range(12):
                        with b.at(rz=30 * k):
                            b.box(0.05 if k % 3 else 0.08, r * 0.16, 0.012, "paint", col=hands, y=-r * 0.82, z=0.052)
                    for ang, ln, wd in ((hour * 30 + minute * 0.5, r * 0.5, 0.07), (minute * 6, r * 0.78, 0.045)):
                        with b.at(rz=-ang + 180):
                            b.box(wd, ln, 0.02, "paint", col=hands, y=-ln / 2, z=0.07)
                    b.box(0.09, 0.09, 0.03, "metal", col=rim, z=0.08)

    s.add(deco)


def bell(b, x=0.0, y=0.0, z=0.0, r=0.38, col="brass", beam=1.6):
    """A bell hanging from a headstock beam; (x, y, z) is the middle of the beam."""
    with b.at(x, y, z):
        with b.detail(1):
            b.beam((-beam / 2, 0, 0), (beam / 2, 0, 0), w=0.16, mat="timber", col="darkoak")
            b.revolve([(r * 1.05, -r * 1.75), (r * 0.95, -r * 1.6), (r * 0.62, -r * 0.9), (r * 0.5, -r * 0.45), (r * 0.3, -r * 0.2), (0.05, -r * 0.1), (0.05, -0.08)], "metal", col=col, seg=12)


# ---------------------------------------------------------------------------------------- things that stand on the ground
def barrel(b, x=0.0, y=0.0, z=0.0, r=0.3, h=0.8, col="#c9a57a"):
    with b.at(x, y, z):
        with b.detail(2):
            b.revolve([(r * 0.82, 0.0), (r, h * 0.3), (r, h * 0.7), (r * 0.82, h)], "planks", col=col, seg=10, close_top=True)
            for zz in (h * 0.16, h * 0.84):
                b.revolve([(r * 0.92, zz - 0.025), (r * 0.94, zz + 0.025)], "metal", col="iron", seg=10)


def crate(b, x=0.0, y=0.0, z=0.0, s=0.6, col="#d8c3a0", rz=0.0):
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            b.box(s, s, s, "planks", col=col)
            for sx in (-1, 1):
                b.beam((sx * s / 2, -s / 2 - 0.005, 0.03), (sx * s / 2, -s / 2 - 0.005, s - 0.03), w=0.07, h=0.03, mat="planks", col=shade(col, 0.8), up=(0, 1, 0), caps=False)


def sack(b, x=0.0, y=0.0, z=0.0, r=0.3, col="#d9c9a3"):
    with b.detail(2):
        b.blob(r, r * 0.85, r * 0.7, mat="cloth", col=col, x=x, y=y, z=z + r * 0.6, seg=6, rings=3, rough=0.12)


def planter(b, x=0.0, y=0.0, z=0.0, w=0.9, d=0.35, h=0.32, col="#b58a66", flowers=None, bush=False):
    """A plant trough (or with bush=True a clipped shrub in a pot) with flowers."""
    rng = b.rng
    with b.at(x, y, z):
        with b.detail(2):
            b.box(w, d, h, "planks" if not bush else "paint", col=col if not bush else "#c9764a", cap="ivy", capcol="#6b5a45", taper=1.0 if not bush else 1.15)
            if bush:
                b.blob(w * 0.55, d * 0.9, h * 1.1, mat="ivy", col="#7db45e", z=h + h * 0.9, seg=6, rings=3, wind=0.2)
            else:
                n = max(3, int(w / 0.16))
                for i in range(n):
                    px = -w / 2 + w * (i + 0.5) / n
                    b.blob(0.1, 0.1, 0.09, mat="ivy", col="#8fc46a", x=px, z=h + 0.05, seg=5, rings=2, wind=0.3, rough=0.3)
                    b.blob(0.06, 0.06, 0.055, mat="paint", col=rng.choice(flowers or FLOWERS), x=px + rng.uniform(-0.03, 0.03), y=rng.uniform(-0.05, 0.05), z=h + 0.15, seg=5, rings=2, wind=0.5, rough=0.2)


def bench(b, x=0.0, y=0.0, z=0.0, w=1.5, rz=0.0, col="greyoak"):
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            b.box(w, 0.36, 0.06, "planks", col=col, z=0.42, bottom=True)
            b.box(w, 0.05, 0.4, "planks", col=col, y=0.2, z=0.5, bottom=True)
            for sx in (-1, 1):
                b.box(0.08, 0.34, 0.42, "planks", col=shade(col, 0.85), x=sx * (w / 2 - 0.12))
                b.beam((sx * (w / 2 - 0.12), 0.2, 0.4), (sx * (w / 2 - 0.12), 0.24, 0.92), w=0.06, mat="planks", col=shade(col, 0.85))


def tree(b, x=0.0, y=0.0, z=0.0, h=5.0, crown=1.9, trunk=0.22, col="#6fae52", kind="round"):
    """A small garden tree: trunk and a lumpy crown that sways. kind = 'round', 'tall' (poplar-like) or 'bush'."""
    rng = b.rng
    with b.at(x, y, z):
        with b.detail(1):
            th = h - crown * (1.3 if kind != "tall" else 2.2)
            if kind != "bush":
                b.revolve([(trunk * 1.5, -0.3), (trunk, 0.4), (trunk * 0.7, max(th, 0.6) + crown * 0.5)], "timber", col="#b59a80", seg=7)
            if kind == "tall":
                b.blob(crown * 0.55, crown * 0.55, crown * 1.7, mat="ivy", col=col, z=th + crown * 1.5, seg=8, rings=5, wind=0.5, rough=0.2)
            else:
                base = max(th, 0.5) + crown * 0.7 if kind != "bush" else crown * 0.6
                b.blob(crown, crown, crown * 0.85, mat="ivy", col=col, z=base, seg=8, rings=4, wind=0.45, rough=0.22)
                for _ in range(3):
                    a = rng.uniform(0, 6.28)
                    r2 = crown * rng.uniform(0.45, 0.65)
                    b.blob(r2, r2, r2 * 0.85, mat="ivy", col=shade(col, rng.uniform(0.85, 1.15)), x=math.cos(a) * crown * 0.6, y=math.sin(a) * crown * 0.6,
                           z=base + rng.uniform(-0.3, 0.5) * crown, seg=7, rings=3, wind=0.5, rough=0.25)
