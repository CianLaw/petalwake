"""Petalwake town kit, props layer (the "p" modeller): street furniture, harbour pieces, boats, green things.

Everything here is written with kit primitives and is used by tools/town/props/p_*.py.

Conventions for props: they stand on z = 0, centred on the origin, front toward -y; long pieces run along x
and say so in META ("length", "axis"). Pieces meant to repeat end to end are built without the kit's wobble
(META "wobble": 0) and with flat, matching ends.

Harbour structures (quay, quay stairs, mole, jetty) have their walking surface at z = 0 (seat them at the level
of the quay) and carry on DEEP below it, so the water can be anywhere from 2.5 to 5 m down. Bridges likewise:
the road meets the ground at z = 0 at both ends and the arch and abutments go down from there.
Boats and buoys float with their water line at z = 0; boats have the bow toward +x.
"""
import math

from kit import C, lerp, mix, rad, shade, vadd, vcross, vdot, vlen, vlerp, vmul, vnorm, vsub
import parts as P

DEEP = 7.5              # how far harbour structures carry on below their deck (z = 0)
QUAY_D = 3.6            # front to back of a quay strip
PAVE = 0.06             # made paving stands this much above z = 0, so the ground cannot show through it
BATTER = 0.04           # a quay face leans back this much per metre of height
QUAY_COL = "#f4e4da"     # dressed quay stone (the bake greens and darkens it toward the water)
HEMP = "#b99c6b"        # rope
TARRED = "#5d4b3c"      # tarred rope and nets
STRAW = "!#e6c766"      # fresh straw / hay (painted onto thatch)
SOIL = "!#6e5138"       # tilled earth (painted onto cobble or masonry)
LEAF = "#7db45e"
GRASS = "#8fc46a"
FLOWERS = P.FLOWERS

EMBLEMS = {
    "star": [(0, .22), (.06, .07), (.21, .07), (.09, -.03), (.13, -.18), (0, -.09), (-.13, -.18), (-.09, -.03), (-.21, .07), (-.06, .07)],
    "fish": [(-.22, 0), (-.08, .1), (.1, .08), (.16, 0), (.24, .1), (.24, -.1), (.16, 0), (.1, -.08), (-.08, -.1)],
    "loaf": [(-.2, -.1), (.2, -.1), (.22, .02), (.12, .12), (-.12, .12), (-.22, .02)],
    "anchor": [(-.03, .22), (.03, .22), (.03, -.08), (.16, -.02), (.2, -.1), (0, -.22), (-.2, -.1), (-.16, -.02), (-.03, -.08)],
    "mug": [(-.14, .16), (.1, .16), (.1, .08), (.2, .08), (.2, -.08), (.1, -.08), (.1, -.18), (-.14, -.18)],
    "moon": [(.02, .22), (-.14, .14), (-.2, 0), (-.14, -.14), (.02, -.22), (-.06, -.1), (-.08, 0), (-.06, .1)],
    "hat": [(0, .24), (.1, -.06), (.24, -.12), (.24, -.18), (-.24, -.18), (-.24, -.12), (-.1, -.06)],
    "bell": [(-.04, .2), (.04, .2), (.12, .06), (.14, -.1), (.2, -.16), (-.2, -.16), (-.14, -.1), (-.12, .06)],
}


def smooth01(a, c, x):
    t = min(max((x - a) / (c - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def split(b, x0, x1, wmin, wmax):
    """Random lengths between wmin and wmax that exactly fill x0 .. x1: [(xa, xb), ...]."""
    L = x1 - x0
    n = max(1, round(L / ((wmin + wmax) / 2)))
    ws = [b.r(wmin, wmax) for _ in range(n)]
    k = L / sum(ws)
    out, x = [], x0
    for w in ws:
        out.append((x, x + w * k))
        x += w * k
    return out


# ---------------------------------------------------------------------------------------- surfaces
def face2(b, pts, mat="cloth", col=None, back=None, wind=0.0, uv=None):
    """A polygon seen from both sides (cloth, paper, leaves)."""
    n = len(pts)
    w = tuple(wind) if isinstance(wind, (tuple, list)) else (wind,) * n
    col = C(col)
    b.face(pts, mat, col=col, wind=w, uv=uv)
    b.face(list(reversed(pts)), mat, col=back if back is not None else shade(col, 0.82), wind=tuple(reversed(w)), uv=list(reversed(uv)) if uv else None)


def face_away(b, pts, away, mat, col=None, **kw):
    """A convex polygon wound so that it faces away from the point `away`."""
    nrm = vcross(vsub(pts[1], pts[0]), vsub(pts[-1], pts[0]))
    c = vmul((sum(p[0] for p in pts), sum(p[1] for p in pts), sum(p[2] for p in pts)), 1.0 / len(pts))
    if vdot(nrm, vsub(c, away)) < 0:
        pts = list(reversed(pts))
    b.face(pts, mat, col=col, **kw)


def loft(b, rows, mat, col=None, cols=None, flip=False, sms=None, smooth=True, wind=None, uvo=None, close=False, swap=False, uvf=None, two=False):
    """A skin over rows of points (every row the same length): one face between each pair of neighbouring rows
    and neighbouring points. Seen from outside the rows advance to the right and the points upward; flip=True if
    it is the other way round. cols = a tint per span between points, or f(i, j); sms = smoothing group per span;
    wind = f(i, j) -> weight; close joins each row's last point to its first; swap lays the texture's v along the
    rows (for planks: the grain runs along v); uvf(i, j) -> (u, v) overrides the texture coordinates."""
    nr, npt = len(rows), len(rows[0])
    us = [0.0]
    for i in range(1, nr):
        us.append(us[-1] + sum(vlen(vsub(rows[i][j], rows[i - 1][j])) for j in range(npt)) / npt)
    uo, vo = uvo or b.uvo()
    spans = npt if close else npt - 1
    if sms is None:
        s0 = b.sm() if smooth else 0
        sms = [s0] * spans
    vs = []
    for i in range(nr):
        v = [0.0]
        for j in range(1, spans + 1):
            v.append(v[-1] + vlen(vsub(rows[i][j % npt], rows[i][j - 1])))
        vs.append(v)

    def uvat(i, j, jj):
        if uvf:
            return uvf(i, jj)
        return (uo + vs[i][jj], vo + us[i]) if swap else (uo + us[i], vo + vs[i][jj])

    for i in range(nr - 1):
        for j in range(spans):
            k = (j + 1) % npt
            q = [rows[i][j], rows[i + 1][j], rows[i + 1][k], rows[i][k]]
            uv = [uvat(i, j, j), uvat(i + 1, j, j), uvat(i + 1, k, j + 1), uvat(i, k, j + 1)]
            w = [wind(i, j), wind(i + 1, j), wind(i + 1, k), wind(i, k)] if wind else [0.0] * 4
            c = cols(i, j) if callable(cols) else (cols[j] if cols else col)
            if flip:
                q.reverse(); uv.reverse(); w.reverse()
            b.face(q, mat, col=c, sm=sms[j], wind=tuple(w), uv=uv)
            if two:
                b.face(list(reversed(q)), mat, col=shade(c, 0.82), sm=sms[j], wind=tuple(reversed(w)), uv=list(reversed(uv)))


def sweep(b, pts, r=0.05, n=6, mat="timber", col=None, r1=None, radii=None, caps=(False, False), smooth=True, wind=0.0, squash=1.0, up=None):
    """A round bar bent along a line of points (trunks, ropes, hoops, handles). r tapers to r1, or radii gives
    one per point. squash flattens it across its second axis. up = a direction the first axis should lean to."""
    m = len(pts)
    if m < 2:
        return
    d = [0.0]
    for i in range(1, m):
        d.append(d[-1] + vlen(vsub(pts[i], pts[i - 1])))
    tot = d[-1] or 1.0
    if radii is None:
        r1 = r if r1 is None else r1
        radii = [lerp(r, r1, di / tot) for di in d]
    tang = [vnorm(vsub(pts[min(i + 1, m - 1)], pts[max(i - 1, 0)])) for i in range(m)]
    nrm = vcross(tang[0], up or (0, 0, 1))
    if vlen(nrm) < 1e-3:
        nrm = vcross(tang[0], (1, 0, 0))
    nrm = vnorm(nrm)
    rings = []
    for i in range(m):
        t = tang[i]
        nn = vsub(nrm, vmul(t, vdot(nrm, t)))
        if vlen(nn) > 1e-6:
            nrm = vnorm(nn)
        bn = vcross(t, nrm)
        rings.append([vadd(pts[i], vadd(vmul(nrm, radii[i] * math.cos(2 * math.pi * k / n)), vmul(bn, radii[i] * squash * math.sin(2 * math.pi * k / n)))) for k in range(n)])
    sm = b.sm() if smooth else 0
    uo, vo = b.uvo()
    wv = list(wind) if isinstance(wind, (list, tuple)) else [wind] * m
    for i in range(m - 1):
        A, Bq = rings[i], rings[i + 1]
        for k in range(n):
            j = (k + 1) % n
            u0, u1 = 2 * math.pi * radii[i] * k / n, 2 * math.pi * radii[i] * (k + 1) / n
            b.face((A[k], A[j], Bq[j], Bq[k]), mat, col=col, sm=sm, wind=(wv[i], wv[i], wv[i + 1], wv[i + 1]),
                   uv=[(uo + u0, vo + d[i]), (uo + u1, vo + d[i]), (uo + u1, vo + d[i + 1]), (uo + u0, vo + d[i + 1])])
    if caps[0]:
        b.face(list(reversed(rings[0])), mat, col=col, wind=wv[0])
    if caps[1]:
        b.face(rings[-1], mat, col=col, wind=wv[-1])


def board(b, p0, p1, w=0.2, t=0.04, mat="planks", col=None, up=(0, 0, 1), caps=True, wind=0.0):
    """A plank from p0 to p1, w wide and t thick (in the `up` direction), with the grain running along it
    (kit beams lay the planks texture across themselves)."""
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
    uo, vo = b.uvo()
    c0 = [vadd(p0, vadd(vmul(s, sx * w / 2), vmul(u2, sz * t / 2))) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    c1 = [vadd(p, vmul(a, L)) for p in c0]
    acc = 0.0
    for i in range(4):
        j = (i + 1) % 4
        e = w if i % 2 == 0 else t
        b.quad(c0[i], c1[i], c1[j], c0[j], mat, col=col, wind=wind, uv=[(uo + acc, vo), (uo + acc, vo + L), (uo + acc + e, vo + L), (uo + acc + e, vo)])
        acc += e
    if caps:
        b.quad(c0[3], c0[2], c0[1], c0[0], mat, col=shade(col, 0.85), wind=wind)
        b.quad(c1[0], c1[1], c1[2], c1[3], mat, col=shade(col, 0.85), wind=wind)


def planking(b, x0, x1, y0, y1, z, along="y", pw=0.2, t=0.045, col="greyoak", gap=0.012, vary=0.12, jit=0.0, underside=False):
    """A floor of separate planks filling x0..x1 by y0..y1 with their tops at z. along = the direction the
    planks run. jit = how unevenly their ends finish (never past the rectangle on the side that must stay clean)."""
    if along == "y":
        n = max(1, round((x1 - x0) / pw))
        for i in range(n):
            xa, xb = x0 + (x1 - x0) * i / n, x0 + (x1 - x0) * (i + 1) / n
            c = shade(col, b.r(1 - vary, 1 + vary * 0.6))
            ja, jb = b.r(0, jit), b.r(0, jit)
            board(b, ((xa + xb) / 2, y0 + ja, z - t / 2), ((xa + xb) / 2, y1 - jb, z - t / 2), w=xb - xa - gap, t=t, col=c)
    else:
        n = max(1, round((y1 - y0) / pw))
        for i in range(n):
            ya, yb = y0 + (y1 - y0) * i / n, y0 + (y1 - y0) * (i + 1) / n
            c = shade(col, b.r(1 - vary, 1 + vary * 0.6))
            board(b, (x0, (ya + yb) / 2, z - t / 2), (x1, (ya + yb) / 2, z - t / 2), w=yb - ya - gap, t=t, col=c)


def rope(b, pts, r=0.016, col=HEMP, n=3, wind=0.0):
    """A rope or line through the points."""
    sweep(b, pts, r=r, n=n, mat="cloth", col=col, wind=wind)


def sag(p0, p1, drop=0.3, n=6):
    """Points along a line hanging between p0 and p1."""
    return [(lerp(p0[0], p1[0], i / n), lerp(p0[1], p1[1], i / n), lerp(p0[2], p1[2], i / n) - drop * 4 * (i / n) * (1 - i / n)) for i in range(n + 1)]


def arc(cx, cz, r, a0, a1, n, y=0.0, plane="xz"):
    """n + 1 points round an arc in a vertical plane: angle 0 = +x (or +y for plane 'yz'), 90 = up."""
    out = []
    for i in range(n + 1):
        a = rad(a0 + (a1 - a0) * i / n)
        if plane == "xz":
            out.append((cx + r * math.cos(a), y, cz + r * math.sin(a)))
        else:
            out.append((y, cx + r * math.cos(a), cz + r * math.sin(a)))
    return out


def torus(b, R, r, mat="metal", col="iron", seg=10, n=4, a0=0.0, a1=360.0):
    """A ring of radius R (to the middle of the bar) and bar radius r lying flat round the frame's z axis."""
    prof = [(R + r * math.cos(-math.pi + 2 * math.pi * k / n), r * math.sin(-math.pi + 2 * math.pi * k / n)) for k in range(n + 1)]
    b.revolve(prof, mat, col=col, seg=seg, a0=a0, a1=a1)


def ball(b, r, mat="ashlar", col=None, x=0.0, y=0.0, z=0.0, seg=8, rings=4, squash=1.0):
    """A smooth ball centred on (x, y, z)."""
    with b.at(x, y, z):
        prof = [(r * math.sin(math.pi * k / rings), -r * squash * math.cos(math.pi * k / rings)) for k in range(rings + 1)]
        prof[0] = (0.0, prof[0][1]); prof[-1] = (0.0, prof[-1][1])
        b.revolve(prof, mat, col=col, seg=seg)


# ---------------------------------------------------------------------------------------- small living things
def tuft(b, x=0.0, y=0.0, z=0.0, r=0.14, h=0.3, n=5, col=GRASS, wind=0.5):
    """A tuft of grass: a few leaning blades."""
    rng = b.rng
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.5, 0.5)
        ca, sa = math.cos(a), math.sin(a)
        lean = rng.uniform(0.35, 1.0) * r
        hh = h * rng.uniform(0.65, 1.15)
        w2 = r * 0.24
        p0 = (x + ca * 0.02 - sa * w2, y + sa * 0.02 + ca * w2, z)
        p1 = (x + ca * 0.02 + sa * w2, y + sa * 0.02 - ca * w2, z)
        tip = (x + ca * lean, y + sa * lean, z + hh)
        face2(b, (p0, p1, tip), "ivy", col=shade(col, rng.uniform(0.85, 1.2)), wind=(0.0, 0.0, wind))


def blooms(b, x=0.0, y=0.0, z=0.0, r=0.3, n=6, cols=None, size=0.055, lift=0.0, wind=0.5):
    """Flower heads scattered over a patch of radius r at height z (+ up to lift)."""
    rng = b.rng
    cols = cols or FLOWERS
    for _ in range(n):
        a, rr = rng.uniform(0, 6.283), r * math.sqrt(rng.random())
        s = size * rng.uniform(0.8, 1.25)
        b.blob(s, s, s * 0.8, mat="paint", col=rng.choice(cols), x=x + math.cos(a) * rr, y=y + math.sin(a) * rr, z=z + rng.uniform(0, lift), seg=5, rings=2, wind=wind, rough=0.15)


def clump(b, x=0.0, y=0.0, z=0.0, r=0.25, h=0.25, col=GRASS, flowers=None, n=5, seg=6, wind=0.35):
    """A low mound of leaves, with flowers on it if `flowers` (a list of colours) is given."""
    b.blob(r, r, h, mat="ivy", col=col, x=x, y=y, z=z + h * 0.35, seg=seg, rings=3, wind=wind, rough=0.28, bottom=False)
    if flowers:
        blooms(b, x, y, z + h * 1.15, r * 0.75, n=n, cols=flowers, lift=h * 0.25)


def pot_plant(b, x=0.0, y=0.0, z=0.0, r=0.16, h=0.26, col="#c9764a", leaf=LEAF, flowers=None, n=5, bush=1.0):
    """A terracotta pot with a plant (and flowers) in it."""
    with b.at(x, y, z):
        b.revolve([(r * 0.68, 0.0), (r, h), (r * 1.08, h), (r * 1.08, h + 0.03), (r * 0.9, h + 0.03)], "paint", col=col, seg=7)
        clump(b, 0, 0, h, r=r * 1.25 * bush, h=r * 1.5 * bush, col=leaf, flowers=flowers, n=n, seg=6)


# ---------------------------------------------------------------------------------------- turned and wrought things
def wheel(b, r=0.5, w=0.07, spokes=8, col="darkoak", tyre="#4a4848", hub=None, felloe=None, lod_spokes=2):
    """A spoked cart wheel centred on the origin of the current frame, its axle along the local y axis."""
    hub = hub or r * 0.17
    t = felloe or r * 0.16
    with b.at(rx=90):      # local z is now the axle
        b.revolve([(r - t, -w / 2), (r, -w / 2), (r, w / 2), (r - t, w / 2), (r - t, -w / 2)], "planks", seg=12,
                  cols=[C(col), C(tyre), C(col), shade(col, 0.8)])
        b.revolve([(0.0, -w * 1.15), (hub, -w * 0.8), (hub, w * 0.8), (0.0, w * 1.15)], "planks", col=shade(col, 0.9), seg=7)
        with b.detail(lod_spokes):
            for k in range(spokes):
                a = 2 * math.pi * (k + 0.5) / spokes
                b.tube((hub * 0.8 * math.cos(a), hub * 0.8 * math.sin(a), 0.0), ((r - t * 0.6) * math.cos(a), (r - t * 0.6) * math.sin(a), 0.0),
                       r=r * 0.045, r1=r * 0.035, mat="planks", col=col, n=4)


def lantern(b, s=0.3, h=0.46, sides=4, col="iron", glow="#ffd88a", lamp=True, strength=1.0, hang=0.0):
    """A street lantern standing on the origin of the current frame (or with hang > 0 hanging from a ring that
    high above its cap): glowing glass, an iron frame and a little roof. s = width across, h = height."""
    rb, rt = s * 0.36, s * 0.52
    if sides == 4:
        rb, rt = rb * 1.25, rt * 1.25
    hg = h * 0.66
    z0 = -(h + hang) if hang else 0.0
    with b.at(z=z0, rz=180.0 / sides):
        b.revolve([(rb, 0.035), (rt, hg)], "glow", col=glow, seg=sides, smooth=False)
        b.revolve([(0.0, 0.0), (rb + 0.02, 0.0), (rb + 0.02, 0.04), (0.0, 0.04)], "metal", col=col, seg=sides, smooth=False)
        b.revolve([(0.0, hg - 0.012), (rt + 0.05, hg - 0.012), (rt + 0.055, hg + 0.014), (rt * 0.42, hg + (h - hg) * 0.62), (0.035, h - 0.02), (0.045, h + 0.03), (0.0, h + 0.07)],
                  "metal", col=col, seg=sides, smooth=False)
        for k in range(sides):
            a = 2 * math.pi * k / sides
            b.beam((rb * math.sin(a), -rb * math.cos(a), 0.03), (rt * math.sin(a), -rt * math.cos(a), hg), w=0.022, mat="metal", col=col, caps=False)
        if hang:
            b.tube((0, 0, h + 0.05), (0, 0, h + hang), r=0.012, mat="metal", col=col, n=3)
    if lamp:
        b.lamp(0, 0, z0 + hg * 0.5, strength)


def emblem(b, name, s=1.0, col="mustard", two=True):
    """A flat painted emblem in the local x-z plane facing -y (and +y if two), about 0.45 * s across."""
    poly = EMBLEMS.get(name, EMBLEMS["star"])
    ring = [(px * s, 0.0, pz * s) for px, pz in poly]
    for i in range(len(ring)):
        a, c = ring[i], ring[(i + 1) % len(ring)]
        b.tri((0, 0, 0), c, a, "paint", col=col)       # the outlines run clockwise seen from the front
        if two:
            b.tri((0, 0, 0), a, c, "paint", col=col)


def coil(b, x=0.0, y=0.0, z=0.0, r=0.3, turns=3, rr=0.035, col=HEMP, tail=True, seg=8):
    """A flat coil of rope lying on the ground: `turns` rings of rope out to radius r."""
    with b.at(x, y, z):
        for k in range(turns):
            ro = r - 2 * rr * k
            if ro - 2 * rr < 0.0:
                break
            b.revolve([(ro, 0.0), (ro, rr * 1.1), (ro - rr, rr * 1.8), (ro - 2 * rr, rr * 1.1)], "cloth", col=shade(col, 1.0 - 0.06 * (k % 2)), seg=seg)
        ri = max(r - 2 * rr * turns, 0.0)
        if ri > 0.01:
            b.disc(ri, "cloth", col=shade(col, 0.6), seg=seg, z=0.01)
        if tail:
            a = b.r(0, 6.283)
            ca, sa = math.cos(a), math.sin(a)
            rope(b, [(ca * r, sa * r, rr), (ca * (r + 0.22) - sa * 0.1, sa * (r + 0.22) + ca * 0.1, rr * 0.9), (ca * (r + 0.4) + sa * 0.08, sa * (r + 0.4) - ca * 0.08, rr * 0.8)], r=rr * 0.8, col=col)


def bucket(b, x=0.0, y=0.0, z=0.0, r=0.15, h=0.28, col="#c9a57a", water=False, handle=True):
    with b.at(x, y, z):
        b.revolve([(r * 0.78, 0.0), (r, h), (r * 0.9, h), (r * 0.72, 0.05)], "planks", col=col, seg=8)
        b.disc(r * 0.9, "water" if water else "planks", col=None if water else shade(col, 0.7), seg=8, z=h * (0.8 if water else 0.2))
        b.revolve([(r * 0.86, h * 0.2), (r * 0.88, h * 0.28)], "metal", col="iron", seg=8)
        b.revolve([(r * 0.98, h * 0.78), (r * 1.0, h * 0.86)], "metal", col="iron", seg=8)
        if handle:
            sweep(b, arc(0, h, r * 0.98, 0, 180, 5), r=0.008, n=3, mat="metal", col="iron")


def basket(b, x=0.0, y=0.0, z=0.0, r=0.22, h=0.22, col="#c9a064", fill=None, heap=0.1):
    """A woven basket; fill = colour of what is heaped in it."""
    with b.at(x, y, z):
        b.revolve([(r * 0.7, 0.0), (r * 0.95, h * 0.5), (r, h), (r * 0.9, h), (r * 0.66, 0.04)], "thatch", col=col, seg=8)
        b.revolve([(r * 1.0, h - 0.02), (r * 1.06, h + 0.01), (r * 0.9, h + 0.02)], "thatch", col=shade(col, 0.8), seg=8)
        if fill is not None:
            b.blob(r * 0.86, r * 0.86, heap, mat="paint", col=fill, z=h - 0.02, seg=7, rings=3, rough=0.2, bottom=False, lod=2)
        else:
            b.disc(r * 0.7, "thatch", col=shade(col, 0.6), seg=8, z=0.05)


def jar(b, x=0.0, y=0.0, z=0.0, s=1.0, kind="jug", col="#c9764a", seg=7):
    """Pottery: kind = 'jug', 'bowl', 'urn', 'amphora', 'vase', 'plate'. s = scale (1 = about 0.3 m tall)."""
    prof = {
        "jug": [(0.07, 0.0), (0.12, 0.08), (0.12, 0.17), (0.06, 0.25), (0.075, 0.3), (0.05, 0.3)],
        "bowl": [(0.06, 0.0), (0.13, 0.05), (0.16, 0.11), (0.14, 0.11), (0.05, 0.03)],
        "urn": [(0.09, 0.0), (0.17, 0.12), (0.17, 0.26), (0.1, 0.36), (0.12, 0.4), (0.08, 0.4)],
        "amphora": [(0.04, 0.0), (0.13, 0.16), (0.14, 0.32), (0.06, 0.46), (0.08, 0.52), (0.05, 0.52)],
        "vase": [(0.06, 0.0), (0.09, 0.1), (0.05, 0.22), (0.08, 0.3), (0.05, 0.3)],
        "plate": [(0.05, 0.0), (0.15, 0.025), (0.13, 0.03), (0.0, 0.012)],
    }[kind]
    with b.at(x, y, z, s=s):
        b.revolve(prof, "paint", col=col, seg=seg)
        if kind != "plate":      # the dark inside, a little below the lip
            b.disc(prof[-1][0], "paint", col=shade(col, 0.35), seg=seg, z=prof[-1][1] - (0.015 if kind != "bowl" else 0.0))
        if kind in ("jug",):
            sweep(b, [(0.115, 0, 0.16), (0.17, 0, 0.2), (0.15, 0, 0.27), (0.07, 0, 0.28)], r=0.014, n=3, mat="paint", col=col)
        if kind in ("amphora",):
            for sx in (-1, 1):
                sweep(b, [(sx * 0.13, 0, 0.33), (sx * 0.16, 0, 0.44), (sx * 0.07, 0, 0.49)], r=0.014, n=3, mat="paint", col=col)


def stripes(b, p00, p10, p11, p01, n, cols, wind=(0.0, 0.0, 0.0, 0.0), two=True, back=0.8):
    """A striped cloth panel with corners p00, p10, p11, p01 (anticlockwise seen from its good side): n stripes
    side by side from the p00-p01 edge to the p10-p11 edge. wind = weight at each corner."""
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        q = (vlerp(p00, p10, t0), vlerp(p00, p10, t1), vlerp(p01, p11, t1), vlerp(p01, p11, t0))
        w = (lerp(wind[0], wind[1], t0), lerp(wind[0], wind[1], t1), lerp(wind[3], wind[2], t1), lerp(wind[3], wind[2], t0))
        c = C(cols[i % len(cols)])
        b.face(q, "cloth", col=c, wind=w)
        if two:
            b.face((q[3], q[2], q[1], q[0]), "cloth", col=shade(c, back), wind=(w[3], w[2], w[1], w[0]))


def valance(b, p0, p1, drop=0.16, n=8, cols=("stripe_red", "linen"), wind=(0.2, 0.6), scallop=True):
    """A scalloped strip of cloth hanging from the edge p0 -> p1 (p0 on the left seen from outside)."""
    for i in range(n):
        a, c = vlerp(p0, p1, i / n), vlerp(p0, p1, (i + 1) / n)
        m = vlerp(a, c, 0.5)
        col = cols[i % len(cols)]
        if scallop:
            pts = [a, (a[0], a[1], a[2] - drop * 0.5), (m[0], m[1], m[2] - drop), (c[0], c[1], c[2] - drop * 0.5), c]
            w = (wind[0], wind[1] * 0.8, wind[1], wind[1] * 0.8, wind[0])
        else:
            pts = [a, (a[0], a[1], a[2] - drop), (c[0], c[1], c[2] - drop), c]
            w = (wind[0], wind[1], wind[1], wind[0])
        face2(b, pts, "cloth", col=col, wind=w)


# ---------------------------------------------------------------------------------------- walls
def wall_run(b, x0, x1, h, t=0.45, mat="masonry", col="warm", batter=0.0, skirt=1.2, hfun=None, cell=1.0, ends="lr", uvo=None):
    """The plain body of a free-standing wall along x from x0 to x1, centred on y = 0, t thick at the top and
    spreading by `batter` each side at the ground. hfun(x) = height of its top (default h everywhere).
    ends = which ends get an end face ('l', 'r'). It carries on `skirt` below the ground for slopes."""
    n = max(1, round((x1 - x0) / cell))
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    H = [hfun(x) if hfun else h for x in xs]
    tb, tt = t / 2 + batter, t / 2
    uo, vo = uvo or b.uvo()
    col = C(col)
    for i in range(n):
        xa, xb, ha, hb = xs[i], xs[i + 1], H[i], H[i + 1]
        zm = min(0.9, min(ha, hb) * 0.5)
        ym = tb + (tt - tb) * (zm / max(min(ha, hb), 1e-6))
        for (ya0, za0, zb0, ya1, za1, zb1, k) in ((tb, -skirt, -skirt, tb, 0.0, 0.0, 0.85), (tb, 0.0, 0.0, ym, zm, zm, 1.0), (ym, zm, zm, tt, ha, hb, 1.0)):
            c = shade(col, k)
            b.quad((xa, -ya0, za0), (xb, -ya0, zb0), (xb, -ya1, zb1), (xa, -ya1, za1), mat, col=c,
                   uv=[(uo + xa, vo + za0), (uo + xb, vo + zb0), (uo + xb, vo + zb1), (uo + xa, vo + za1)])
            b.quad((xb, ya0, zb0), (xa, ya0, za0), (xa, ya1, za1), (xb, ya1, zb1), mat, col=c,
                   uv=[(uo + 31 - xb, vo + zb0), (uo + 31 - xa, vo + za0), (uo + 31 - xa, vo + za1), (uo + 31 - xb, vo + zb1)])
        b.quad((xa, -tt, ha), (xb, -tt, hb), (xb, tt, hb), (xa, tt, ha), mat, col=shade(col, 1.05), uv=[(uo + xa, vo + 17), (uo + xb, vo + 17), (uo + xb, vo + 17 + t), (uo + xa, vo + 17 + t)])
    if "l" in ends:
        b.face([(x0, tb, -skirt), (x0, -tb, -skirt), (x0, -tb, 0), (x0, -tt, H[0]), (x0, tt, H[0]), (x0, tb, 0)], mat, col=col)
    if "r" in ends:
        b.face([(x1, -tb, -skirt), (x1, tb, -skirt), (x1, tb, 0), (x1, tt, H[-1]), (x1, -tt, H[-1]), (x1, -tb, 0)], mat, col=col)


def wall_stones(b, x0, x1, z0, z1, t, n=10, size=(0.3, 0.6), proud=0.05, mat="masonry", col="warm", sides=(-1, 1), batter=0.0, h=None, hfun=None):
    """Stones standing proud of both faces (sides: -1 = front, 1 = back) of a wall made with wall_run."""
    rng = b.rng
    for sgn in sides:
        for _ in range(n):
            w = rng.uniform(*size)
            hh = w * rng.uniform(0.45, 0.75)
            x = rng.uniform(x0 + w / 2 + 0.03, x1 - w / 2 - 0.03)
            top = (hfun(x) if hfun else z1)
            top = min(top, z1) - hh - 0.04
            if top <= z0:
                continue
            z = rng.uniform(z0, top)
            yf = t / 2 + (batter * (1 - (z + hh / 2) / h) if (batter and h) else 0.0)
            with b.at(x, sgn * (yf - 0.02), z + hh / 2, rz=0 if sgn < 0 else 180):
                with b.at(ry=rng.uniform(-4, 4)):
                    with b.at(rx=90):
                        b.stone(w, hh, proud + 0.02, mat=mat, col=col, jitter=0.16)


def cap_slabs(b, x0, x1, zfun, t, over=0.06, thick=0.1, mat="ashlar", col="stone", wmin=0.45, wmax=0.8, jitter=0.07):
    """Flat capping stones along a wall top, exactly filling x0 .. x1."""
    for xa, xb in split(b, x0, x1, wmin, wmax):
        xm = (xa + xb) / 2
        b.stone(xb - xa - 0.012, t + 2 * over, thick * b.r(0.9, 1.12), mat=mat, col=col, x=xm, y=b.r(-0.012, 0.012), z=zfun(xm), jitter=jitter, ch=0.3)


def cap_cocks(b, x0, x1, zfun, t, mat="masonry", col="grey", wmin=0.2, wmax=0.34, hmin=0.2, hmax=0.36):
    """Upright 'cock and hen' capping stones along a drystone wall top, exactly filling x0 .. x1."""
    for k, (xa, xb) in enumerate(split(b, x0, x1, wmin, wmax)):
        xm = (xa + xb) / 2
        hh = b.r(hmin, hmax) * (1.0 if k % 2 else 0.8)
        with b.at(xm, 0, zfun(xm) - 0.02):
            b.box(xb - xa - 0.015, t * b.r(0.92, 1.05), hh, mat, col=shade(col, b.r(0.85, 1.12)), tx=b.r(0.7, 0.95), ty=b.r(0.55, 0.8), y=b.r(-0.02, 0.02))


def cap_ridge(b, x0, x1, zfun, t, h=0.18, mat="masonry", col="grey", cell=1.0):
    """A plain ridged (triangular) wall top: the far-off stand-in for cock-and-hen stones."""
    n = max(1, round((x1 - x0) / cell))
    for i in range(n):
        xa, xb = x0 + (x1 - x0) * i / n, x0 + (x1 - x0) * (i + 1) / n
        za, zb = zfun(xa), zfun(xb)
        b.quad((xa, -t / 2, za), (xb, -t / 2, zb), (xb, 0, zb + h), (xa, 0, za + h), mat, col=col)
        b.quad((xb, t / 2, zb), (xa, t / 2, za), (xa, 0, za + h), (xb, 0, zb + h), mat, col=col)


# ---------------------------------------------------------------------------------------- harbour bits
def pile(b, x=0.0, y=0.0, z0=-3.0, z1=3.0, r=0.14, col="darkoak", band=True, n=7, lean=(0.0, 0.0)):
    """A round timber pile from z0 up to z1."""
    with b.at(x, y, 0):
        dx, dy = lean[0] * (z1 - z0), lean[1] * (z1 - z0)
        b.tube((0, 0, z0), (dx, dy, z1 - 0.06), r=r * 1.04, r1=r, mat="timber", col=col, n=n)
        with b.at(dx, dy, z1 - 0.06):
            b.revolve([(r, 0.0), (r * 0.78, 0.06)], "timber", col=shade(col, 1.15), seg=n, close_top=True)
            if band:
                b.revolve([(r * 1.03, -0.14), (r * 1.05, -0.06)], "metal", col="iron", seg=n)


def mooring_ring(b, r=0.13, rr=0.02, col="iron", flat=False):
    """An iron ring hanging from an eye on a wall. In a frame on the wall: x along it, -y out of it, the eye at
    the origin."""
    b.box(0.1, 0.035, 0.1, "metal", col=col, y=-0.017, z=-0.05, bottom=True)
    with b.at(0, -0.045, -r - 0.01, rx=90 if not flat else 20):
        torus(b, r, rr, col=col, seg=8, n=3)


def bollard_stone(b, x=0.0, y=0.0, z=0.0, h=0.78, r=0.2, col="grey", seg=8):
    """A squat granite mooring post with a mushroom head."""
    with b.at(x, y, z):
        b.revolve([(r * 1.25, -0.2), (r * 1.25, 0.0), (r * 1.1, 0.07), (r * 0.9, h * 0.62), (r * 1.22, h * 0.74), (r * 1.25, h * 0.86), (r * 0.8, h), (0.0, h + 0.02)],
                  "ashlar", col=col, seg=seg)


def bollard_iron(b, x=0.0, y=0.0, z=0.0, h=0.7, r=0.15, col="iron", seg=8):
    """A cast-iron bollard: flange, waisted stem, a cap and two horns."""
    with b.at(x, y, z):
        b.revolve([(r * 1.7, 0.0), (r * 1.7, 0.05), (r * 1.1, 0.09), (r * 0.85, h * 0.5), (r * 1.0, h * 0.78), (r * 1.35, h * 0.86), (r * 1.3, h * 0.94), (0.0, h)],
                  "metal", col=col, seg=seg)
        b.tube((-r * 1.9, 0, h * 0.7), (r * 1.9, 0, h * 0.7), r=r * 0.3, mat="metal", col=col, n=5, caps=True)


def rope_turns(b, x=0.0, y=0.0, z=0.4, r=0.2, turns=3, rr=0.022, col=HEMP, seg=8):
    """A few turns of rope round a post of radius r, the lowest at height z."""
    with b.at(x, y, z):
        for k in range(turns):
            z0 = rr * 2.05 * k
            b.revolve([(r - 0.012, z0), (r + rr * 1.3, z0 + rr * 0.45), (r + rr * 1.3, z0 + rr * 1.55), (r - 0.012, z0 + rr * 2)], "cloth", col=shade(col, 1.0 - 0.08 * (k % 2)), seg=seg)


def iron_ladder(b, z0, z1, w=0.42, out=0.09, col="iron", hoops=0.9):
    """An iron ladder on a wall face. In a frame on the wall (x along it, -y out of it): rails from z0 up to z1
    and then curving back over the top as hand hoops (hoops = how far they rise above z1)."""
    for sx in (-1, 1):
        x = sx * w / 2
        pts = [(x, -out, z0), (x, -out, z1 + hoops * 0.6), (x, -out + 0.12, z1 + hoops), (x, 0.3, z1 + hoops), (x, 0.42, z1 + hoops * 0.7), (x, 0.42, z1)]
        sweep(b, pts, r=0.022, n=4, mat="metal", col=col)
    with b.detail(2):
        n = int((z1 - z0) / 0.3)
        for i in range(n + 1):
            zz = z0 + 0.1 + (z1 - z0 - 0.2) * i / max(n, 1)
            b.beam((-w / 2, -out, zz), (w / 2, -out, zz), w=0.025, mat="metal", col=col, caps=False)
            if i % 4 == 1:
                for sx in (-1, 1):
                    b.beam((sx * w / 2, -out, zz), (sx * w / 2, 0.02, zz), w=0.02, mat="metal", col=col, caps=False)


# ---------------------------------------------------------------------------------------- market stalls
def stall(b, w=2.6, d=1.6, post_h=2.05, roof="gable", cols=("stripe_red", "linen"), rise=0.55, over=0.3, nstripes=None,
          counter=0.86, cdepth=None, apron="boards", apron_col="greyoak", post_col=None, drop=0.17, top_col="#d8c3a0"):
    """The carcass of a market stall centred on the origin, the customers' side toward -y: four posts, a counter
    along the front and a striped awning. roof = 'gable' (ridge left to right), 'lean' (one slope down to the
    front), 'hip' (a pointed tent) or 'barrel' (a hooped vault). Returns the places goods can go."""
    hw, hd = w / 2, d / 2
    px, py = hw - 0.05, hd - 0.05
    n = nstripes or max(5, round(w / 0.3))
    cd = cdepth or d * 0.58
    back_h = post_h + (rise if roof == "lean" else 0.0)
    with b.detail(1):
        for sx in (-1, 1):
            b.beam((sx * px, -py, -0.3), (sx * px, -py, post_h - 0.04), w=0.075, mat="timber", col=post_col)
            b.beam((sx * px, py, -0.3), (sx * px, py, back_h - 0.04), w=0.075, mat="timber", col=post_col)
            b.beam((sx * px, -py, post_h - 0.1), (sx * px, py, back_h - 0.1), w=0.055, h=0.08, mat="timber", col=post_col)
        b.beam((-px, -py, post_h - 0.1), (px, -py, post_h - 0.1), w=0.055, h=0.08, mat="timber", col=post_col)
        b.beam((-px, py, back_h - 0.1), (px, py, back_h - 0.1), w=0.055, h=0.08, mat="timber", col=post_col)
    ex, ey = hw + over * 0.45, hd + over
    if roof == "gable":
        zr = post_h + rise
        ze = post_h - over * rise / hd * 0.7
        with b.detail(0):
            stripes(b, (-ex, -ey, ze), (ex, -ey, ze), (ex, 0, zr), (-ex, 0, zr), n, cols, wind=(0.3, 0.3, 0.05, 0.05))
            stripes(b, (ex, ey, ze), (-ex, ey, ze), (-ex, 0, zr), (ex, 0, zr), n, cols, wind=(0.3, 0.3, 0.05, 0.05))
        with b.detail(1):
            b.beam((-ex + 0.02, 0, zr - 0.03), (ex - 0.02, 0, zr - 0.03), w=0.05, mat="timber", col=post_col)
            for sx in (-1, 1):
                b.beam((sx * px, 0, post_h - 0.08), (sx * px, 0, zr - 0.04), w=0.05, mat="timber", col=post_col)
                face2(b, [(sx * (ex - 0.03), -hd, post_h + 0.02), (sx * (ex - 0.03), hd, post_h + 0.02), (sx * (ex - 0.03), 0, zr - 0.02)], "cloth", col=cols[0], wind=(0.1, 0.1, 0.0))
            valance(b, (-ex, -ey, ze), (ex, -ey, ze), drop, n, cols)
            valance(b, (ex, ey, ze), (-ex, ey, ze), drop, n, cols)
        top_z = zr
    elif roof == "lean":
        yf, yb = -(hd + over * 1.5), hd + 0.12
        sl = rise / (2 * py)
        zf, zb = post_h + 0.02 + (yf + py) * sl, post_h + 0.02 + (yb + py) * sl
        with b.detail(0):
            stripes(b, (-ex, yf, zf), (ex, yf, zf), (ex, yb, zb), (-ex, yb, zb), n, cols, wind=(0.35, 0.35, 0.0, 0.0))
        with b.detail(1):
            valance(b, (-ex, yf, zf), (ex, yf, zf), drop, n, cols)
            for sx in (-1, 1):
                b.beam((sx * px, -py, post_h - 0.02), (sx * px, yf + 0.04, zf - 0.01), w=0.04, mat="timber", col=post_col)
                valance(b, (sx * ex, yb if sx < 0 else yf, zb if sx < 0 else zf), (sx * ex, yf if sx < 0 else yb, zf if sx < 0 else zb), drop * 0.8, max(3, int(n * 0.6)), cols)
        top_z = zb
    elif roof == "hip":
        apex = (0.0, 0.0, post_h + rise)
        ze = post_h - 0.03
        with b.detail(0):
            for (pa, pb) in (((-ex, -ey, ze), (ex, -ey, ze)), ((ex, -ey, ze), (ex, ey, ze)), ((ex, ey, ze), (-ex, ey, ze)), ((-ex, ey, ze), (-ex, -ey, ze))):
                m = max(4, round(vlen(vsub(pb, pa)) / 0.3))
                stripes(b, pa, pb, apex, apex, m, cols, wind=(0.3, 0.3, 0.0, 0.0))
        with b.detail(1):
            for (pa, pb) in (((-ex, -ey, ze), (ex, -ey, ze)), ((ex, -ey, ze), (ex, ey, ze)), ((ex, ey, ze), (-ex, ey, ze)), ((-ex, ey, ze), (-ex, -ey, ze))):
                m = max(4, round(vlen(vsub(pb, pa)) / 0.3))
                valance(b, pa, pb, drop, m, cols)
            b.beam((0, 0, post_h - 0.1), (0, 0, post_h + rise + 0.28), w=0.05, mat="timber", col=post_col)
            b.beam((-px, 0, post_h - 0.1), (px, 0, post_h - 0.1), w=0.05, mat="timber", col=post_col)
            ball(b, 0.06, "metal", "brass", z=post_h + rise + 0.3, seg=6, rings=3)
        top_z = post_h + rise
    else:        # barrel
        seg = 6
        ze = post_h - 0.08
        prof = [(-ey * math.cos(math.pi * k / seg), ze + rise * math.sin(math.pi * k / seg)) for k in range(seg + 1)]
        with b.detail(0):
            for k in range(seg):
                (ya, za), (yb, zb) = prof[k], prof[k + 1]
                stripes(b, (-ex, ya, za), (ex, ya, za), (ex, yb, zb), (-ex, yb, zb), n, cols, wind=(0.2, 0.2, 0.2, 0.2) if 0 < k < seg - 1 else ((0.3, 0.3, 0.2, 0.2) if k == 0 else (0.2, 0.2, 0.3, 0.3)))
        with b.detail(1):
            valance(b, (-ex, -ey, ze), (ex, -ey, ze), drop, n, cols)
            valance(b, (ex, ey, ze), (-ex, ey, ze), drop, n, cols)
            for sx in (-1, 1):
                sweep(b, [(sx * (ex - 0.03), yy, zz - 0.02) for yy, zz in prof], r=0.02, n=4, mat="timber", col=post_col)
        top_z = post_h + rise
    y0 = -hd + 0.03
    y1 = y0 + cd
    with b.detail(1):
        board(b, (-hw + 0.06, (y0 + y1) / 2, counter - 0.025), (hw - 0.06, (y0 + y1) / 2, counter - 0.025), w=cd, t=0.05, col=top_col)
        for sx in (-1, 1):
            b.beam((sx * (hw - 0.22), y1 - 0.07, -0.3), (sx * (hw - 0.22), y1 - 0.07, counter - 0.05), w=0.06, mat="timber", col=post_col)
        if apron == "boards":
            board(b, (-hw + 0.1, y0 + 0.04, 0.06 + (counter - 0.12) / 2), (hw - 0.1, y0 + 0.04, 0.06 + (counter - 0.12) / 2), w=counter - 0.12, t=0.03, col=apron_col, up=(0, 1, 0))
        elif apron == "cloth":
            valance(b, (-hw + 0.08, y0 - 0.01, counter - 0.01), (hw - 0.08, y0 - 0.01, counter - 0.01), counter - 0.2, n, (apron_col,) if isinstance(apron_col, str) else apron_col, wind=(0.0, 0.25), scallop=False)
    return {"top": counter, "y0": y0, "y1": y1, "hw": hw - 0.08, "hd": hd, "post_h": post_h, "back_h": back_h, "px": px, "py": py, "roof_z": top_z}


def tray(b, x, y, z, w=0.5, d=0.4, h=0.1, tilt=0.0, col="#d8c3a0", fill=None, heap=0.09, rz=0.0, loose=0):
    """A shallow wooden crate of produce on a counter; tilt (degrees) raises its back edge. fill = colour heaped
    in it, loose = how many separate pieces of it sit on top."""
    with b.at(x, y, z, rz=rz):
        with b.at(0, -d / 2, 0, rx=tilt):
            b.box(w, d, h, "planks", col=col, y=d / 2, cap="paint" if fill is not None else None, capcol=shade(fill, 0.8) if fill is not None else None)
            if fill is not None:
                b.blob(w * 0.44, d * 0.42, heap, mat="paint", col=fill, y=d / 2, z=h - 0.01, seg=6, rings=3, rough=0.22, bottom=False)
                for _ in range(loose):
                    s = min(w, d) * b.r(0.08, 0.11)
                    b.blob(s, s, s, mat="paint", col=shade(fill, b.r(0.9, 1.15)), x=b.r(-w * 0.3, w * 0.3), y=d / 2 + b.r(-d * 0.3, d * 0.3), z=h + heap * 0.8, seg=5, rings=2, rough=0.1)


# ---------------------------------------------------------------------------------------- boats
class Hull:
    """A round-bilged clinker-built boat hull: bow toward +x, water line at z = 0, centred on the origin.

    L, B = length and beam; depth = keel to sheer amidships; draft = how much of that is under water.
    sheer_bow / sheer_stern = how much the sheer rises toward the ends. transom = breadth of the transom as a
    share of the beam (None = a pointed, double-ended stern). rake_bow = how far the foot of the stem is cut
    back. planks = strakes per side, stations = sections along the length, lap = how proud each strake's lower
    edge stands (the clinker steps), th = thickness of the planking.
    """

    def __init__(self, L=4.0, B=1.45, depth=0.58, draft=0.16, sheer_bow=0.24, sheer_stern=0.08, transom=0.62, rake_bow=0.42, rake_stern=0.1,
                 flare=12.0, vee=0.9, vee_aft=0.2, bilge=0.85, bow_pow=0.85, bow_a=2.2, rise_fwd=None, rise_aft=None, planks=5, stations=9,
                 lap=0.034, th=0.035):
        self.L, self.B, self.depth, self.draft = L, B, depth, draft
        self.F = depth - draft
        self.sheer_bow, self.sheer_stern, self.transom = sheer_bow, sheer_stern, transom
        self.rake_bow, self.rake_stern = rake_bow, rake_stern
        self.tm = rad(90.0 - flare)
        self.vee, self.vee_aft, self.bilge, self.bow_pow, self.bow_a = vee, vee_aft, bilge, bow_pow, bow_a
        self.rise_fwd = draft * 0.9 if rise_fwd is None else rise_fwd
        self.rise_aft = draft * (0.5 if transom is not None else 0.9) if rise_aft is None else rise_aft
        self.planks, self.lap, self.th = planks, lap, th
        n = stations
        self.us = [(-math.cos(math.pi * i / n)) * 0.5 + (2 * i / n - 1) * 0.5 for i in range(n + 1)]
        self.us[0], self.us[-1] = -1.0, 1.0

    # --- the shape
    def hb(self, u):
        B2 = self.B / 2
        if u >= 0 or self.transom is None:
            return B2 * max(1 - abs(u) ** self.bow_a, 0.0) ** self.bow_pow
        return B2 * (1 - (1 - self.transom) * (-u) ** 2.4)

    def zs(self, u):
        return self.F + self.sheer_bow * max(u, 0.0) ** 2.2 + self.sheer_stern * max(-u, 0.0) ** 2.0

    def zk(self, u):
        aft = max(-u, 0.0) ** (2.5 if self.transom is not None else 3.0)
        return -self.draft + self.rise_fwd * max(u, 0.0) ** 3 + self.rise_aft * aft

    def xof(self, u, g):
        x = u * self.L / 2 - self.rake_bow * (1 - g) ** 1.5 * smooth01(0.45, 1.0, u)
        if self.transom is not None:
            x += self.rake_stern * (1 - g) * smooth01(0.6, 1.0, -u)
        else:
            x += self.rake_stern * (1 - g) ** 1.5 * smooth01(0.45, 1.0, -u)
        return x

    def _yz(self, u, t):
        a = t * self.tm
        p = (1.0 + self.vee * max(u, 0.0) ** 2 + (self.vee_aft if self.transom is not None else self.vee) * max(-u, 0.0) ** 2) * self.bilge
        s = (math.sin(a) / math.sin(self.tm)) ** p if t > 1e-9 else 0.0
        g = (1 - math.cos(a)) / (1 - math.cos(self.tm))
        return self.hb(u) * s, self.zk(u) + (self.zs(u) - self.zk(u)) * g, g

    def pt(self, u, t, off=0.0):
        """A point on the starboard (+y) side at station u (-1 stern .. 1 bow) and girth t (0 keel .. 1 sheer),
        `off` metres outside the planking (negative = inside)."""
        y, z, g = self._yz(u, t)
        if off:
            ya, za, _ = self._yz(u, max(t - 0.02, 0.0))
            yb, zb, _ = self._yz(u, min(t + 0.02, 1.0))
            dy, dz = yb - ya, zb - za
            l = math.hypot(dy, dz) or 1.0
            y += dz / l * off
            z += -dy / l * off
        return (self.xof(u, g), max(y, 0.0), z)

    def u_at(self, x):
        return max(min(x / (self.L / 2), 1.0), -1.0)

    def half_in(self, x, z):
        """Half the inside width of the hull at position x and height z."""
        u = self.u_at(x)
        zk, zs = self.zk(u), self.zs(u)
        g = min(max((z - zk) / max(zs - zk, 1e-6), 0.0), 1.0)
        c = 1 - g * (1 - math.cos(self.tm))
        t = math.acos(max(min(c, 1.0), -1.0)) / self.tm
        return max(self._yz(u, t)[0] - self.th, 0.0)

    # --- the planking
    def build(self, b, cols=None, inner="#d9bd8a", gunwale="darkoak", keel="darkoak", transom_col=None, inside=True, head=0.12, keel_w=0.07, keel_d=0.07):
        """Emit the hull: outer planking (cols = one paint per strake, keel upward), the inner skin, gunwales,
        the transom, keel and stem."""
        n = self.planks
        cols = [C(c) for c in (cols or ["ivory"] * n)]
        ts = [k / n for k in range(n + 1)]
        mir = lambda p: (p[0], -p[1], p[2])
        outer = []
        for u in self.us:
            lap = self.lap * (1 - smooth01(0.72, 1.0, u))
            if self.transom is None:
                lap *= 1 - smooth01(0.72, 1.0, -u)
            row = [self.pt(u, 0.0)]
            for k in range(1, n):
                row.append(self.pt(u, ts[k]))
                row.append(self.pt(u, ts[k], off=lap) if lap > 1e-5 else self.pt(u, ts[k]))
            row.append(self.pt(u, 1.0))
            outer.append(row)
        scol = [cols[j // 2] if j % 2 == 0 else shade(cols[(j + 1) // 2], 0.5) for j in range(2 * n - 1)]
        U0 = (0.35, 0.68, 1.10, 1.42, 0.60, 1.30)
        xs_ = [r_[n][0] for r_ in outer]

        def uvf_for(side):
            def f(i, jj):
                k = jj // 2 + (jj % 2)      # strake this point belongs to (its lower edge)
                return (U0[(jj // 2 + side) % len(U0)] + 0.03 * (jj % 2), xs_[i] * 1.0 + 3.0 * side)
            return f

        for side, rows, flip in ((0, outer, True), (1, [[mir(p) for p in r_] for r_ in outer], False)):
            sms = [b.sm() if j % 2 == 0 else 0 for j in range(2 * n - 1)]
            loft(b, rows, "planks", cols=scol, sms=sms, flip=flip, uvf=uvf_for(side))
        # inner skin (inside = True for all of it, or the girth it starts at: a decked boat only shows its bulwarks)
        tin = ts if inside is True else [t for t in ts if t >= float(inside) - 1e-9]
        if inside:
            innr = []
            for i, u in enumerate(self.us):
                row = [self.pt(u, t, off=-self.th) for t in tin]
                if tin[0] < 1e-9:
                    row[0] = (row[0][0], 0.0, row[0][2])
                if i == len(self.us) - 1:
                    row = [(p[0] - 2 * self.th, 0.0, p[2]) for p in row]
                if i == 0 and self.transom is None:
                    row = [(p[0] + 2 * self.th, 0.0, p[2]) for p in row]
                innr.append(row)
            loft(b, innr, "planks", col=inner, flip=False, swap=True)
            loft(b, [[mir(p) for p in r_] for r_ in innr], "planks", col=inner, flip=True, swap=True)
        # gunwales
        go, gi, gh = 0.03, 0.03, 0.075
        gun = []
        for u in self.us:
            o = self.pt(u, 1.0, off=go)
            i_ = self.pt(u, 1.0, off=-(self.th + gi))
            zz = self.zs(u)
            gun.append([(o[0], o[1], zz - gh), (o[0], o[1], zz + 0.014), (i_[0], i_[1], zz + 0.014), (i_[0], i_[1], zz - gh * 0.8)])
        loft(b, gun, "planks", col=gunwale, flip=True, smooth=False, swap=True)
        loft(b, [[mir(p) for p in r_] for r_ in gun], "planks", col=gunwale, flip=False, smooth=False, swap=True)
        # transom
        if self.transom is not None:
            tc = transom_col if transom_col is not None else cols[-1]
            row = outer[0]
            c0 = (self.xof(-1.0, 1.0), 0.0, self.zs(-1.0))
            for j in range(len(row) - 1):
                b.tri(c0, row[j + 1], row[j], "planks", col=tc)
                b.tri(c0, mir(row[j]), mir(row[j + 1]), "planks", col=tc)
            if inside:
                ir = innr[0]
                sh = lambda p: (p[0] + self.th, p[1], p[2])
                for j in range(len(ir) - 1):
                    b.quad(mir(sh(ir[j])), sh(ir[j]), sh(ir[j + 1]), mir(sh(ir[j + 1])), "planks", col=inner)
                top = row[-1]
                b.quad(mir(top), (top[0] + self.th, -top[1], top[2]), (top[0] + self.th, top[1], top[2]), top, "planks", col=gunwale)
        # keel and stem
        line = [self.pt(u, 0.0) for u in self.us] + [self.pt(1.0, t) for t in (0.14, 0.3, 0.48, 0.66, 0.84, 1.0)]
        d = vnorm(vsub(line[-1], line[-2]))
        line.append(vadd(line[-1], vmul(d, head)))
        if self.transom is None:
            aft = [self.pt(-1.0, t) for t in (1.0, 0.84, 0.66, 0.48, 0.3, 0.14)]
            d = vnorm(vsub(aft[0], aft[1]))
            line = [vadd(aft[0], vmul(d, head))] + aft + line
        rows = []
        m = len(line)
        for i in range(m):
            a, c = line[max(i - 1, 0)], line[min(i + 1, m - 1)]
            tx, tz = c[0] - a[0], c[2] - a[2]
            l = math.hypot(tx, tz) or 1.0
            nx, nz = tz / l, -tx / l
            p = line[i]
            rows.append([(p[0] - nx * 0.02, -keel_w / 2, p[2] - nz * 0.02), (p[0] + nx * keel_d, -keel_w / 2, p[2] + nz * keel_d),
                         (p[0] + nx * keel_d, keel_w / 2, p[2] + nz * keel_d), (p[0] - nx * 0.02, keel_w / 2, p[2] - nz * 0.02)])
        loft(b, rows, "planks", col=keel, flip=True, smooth=False, swap=True)
        b.face(rows[-1], "planks", col=keel)
        b.face(list(reversed(rows[0])), "planks", col=keel)
        return self

    # --- fittings
    def thwart(self, b, x, z=None, w=0.22, t=0.035, col="#c9a57a", lip=0.02):
        """A seat plank across the boat at x, its top at z (default: a hand below the sheer)."""
        z = self.zs(self.u_at(x)) - 0.17 if z is None else z
        ya, yb = self.half_in(x - w / 2, z) + lip, self.half_in(x + w / 2, z) + lip
        b.prism([(x - w / 2, -ya), (x + w / 2, -yb), (x + w / 2, yb), (x - w / 2, ya)], t, "planks", col=col, z=z - t, bottom=True)
        return z

    def sole(self, b, x0, x1, z, col="greyoak", n=6, mat="planks"):
        """Bottom boards: a floor at height z from x0 to x1, as wide as the hull is there."""
        rows = []
        for i in range(n + 1):
            x = lerp(x0, x1, i / n)
            y = self.half_in(x, z) + 0.01
            rows.append([(x, -y, z), (x, y, z)])
        uo, vo = b.uvo()
        loft(b, rows, mat, col=col, smooth=False, uvf=lambda i, jj: (uo + rows[i][jj][1], vo + rows[i][jj][0]))

    def ribs(self, b, xs, w=0.035, proud=0.014, col="#c9a57a", t1=1.0):
        """Bent frames inside the planking at the given x positions."""
        for x in xs:
            u = self.u_at(x)
            pts = [self.pt(u, t, off=-(self.th + proud)) for t in (0.0, 0.2, 0.4, 0.6, 0.8, t1)]
            for sgn in (1, -1):
                rows = [[(p[0] - w / 2, sgn * p[1], p[2]) for p in pts], [(p[0] + w / 2, sgn * p[1], p[2]) for p in pts]]
                loft(b, rows, "planks", col=col, flip=(sgn < 0), swap=False)

    def deck(self, b, u0, u1, drop=0.0, camber=0.04, col="greyoak", mat="planks"):
        """A deck between stations u0 and u1 (-1 stern .. 1 bow), `drop` below the sheer, cambered."""
        us = sorted({u0, u1} | {u for u in self.us if u0 < u < u1})
        rows = []
        for u in us:
            x = u * self.L / 2
            z = self.zs(u) - drop
            y = self.half_in(x, z) + self.th * 0.5
            rows.append([(x, -y, z), (x, 0.0, z + camber * (y / (self.B / 2))), (x, y, z)])
        uo, vo = b.uvo()
        loft(b, rows, mat, col=col, smooth=True, uvf=lambda i, jj: (uo + rows[i][jj][1], vo + rows[i][jj][0]))
        return rows

    def bulkhead(self, b, u, z0=None, drop=0.0, col="#d9bd8a", face=1):
        """A boarded wall across the boat at station u from z0 (default the bottom) up to `drop` below the sheer,
        seen from the +x side (face = 1) or the -x side (-1)."""
        x = u * self.L / 2
        zt = self.zs(u) - drop
        zb = self.zk(u) + self.th if z0 is None else z0
        pts = []
        for k in range(6):
            z = lerp(zb, zt, k / 5)
            pts.append((x, self.half_in(x, z) + 0.01, z))
        poly = [(p[0], -p[1], p[2]) for p in pts] + list(reversed(pts))       # up the port side, down the starboard: clockwise seen from +x
        c = (x, 0.0, (zb + zt) / 2)
        for i in range(len(poly)):
            a, d = poly[i], poly[(i + 1) % len(poly)]
            if face > 0:
                b.tri(c, d, a, "planks", col=col)
            else:
                b.tri(c, a, d, "planks", col=col)


def oar(b, p0, p1, col="#d8c3a0", blade=0.62, bw=0.13):
    """An oar from the grip p0 to the tip of the blade p1."""
    L = vlen(vsub(p1, p0))
    q = vlerp(p0, p1, 1 - blade / L)
    b.tube(p0, q, r=0.022, mat="planks", col=col, n=5)
    board(b, q, p1, w=bw, t=0.022, col=col)


def mast(b, x=0.0, y=0.0, z=0.0, h=5.0, r=0.07, rake=2.0, col="#c9a57a", truck=True, n=7):
    """A mast stepped at (x, y, z), raking aft (toward -x) by `rake` degrees. Returns its top point."""
    dx = -math.tan(rad(rake)) * h
    b.tube((x, y, z), (x + dx, y, z + h), r=r, r1=r * 0.55, mat="planks", col=col, n=n)
    if truck:
        ball(b, r * 0.8, "paint", "!#f2ead8", x=x + dx, y=y, z=z + h + r * 0.3, seg=6, rings=3, squash=0.7)
    return (x + dx, y, z + h)


def furled(b, p0, p1, r=0.11, col="stripe_red", ties=5, tie_col=HEMP, spar=0.04, spar_col="#c9a57a", sag_=0.0, n=7, over=0.2, above=False, gaff=0.0):
    """A sail furled along a spar from p0 to p1: the spar (sticking out `over` at each end) with a lumpy roll of
    cloth lashed under it (or on top of it: above=True, as on a boom). gaff = radius of a second spar lying on
    the roll."""
    d = vnorm(vsub(p1, p0))
    if spar:
        b.tube(vsub(p0, vmul(d, over)), vadd(p1, vmul(d, over)), r=spar, r1=spar * 0.8, mat="planks", col=spar_col, n=6, caps=True)
    sg = 1.0 if above else -1.0
    m = 8
    pts, radii = [], []
    for i in range(m + 1):
        t = i / m
        p = vlerp(p0, p1, t)
        rr = r * (0.82 + 0.3 * b.rng.random()) if 0 < i < m else r * 0.4
        pts.append((p[0], p[1], p[2] + sg * (spar + rr * 0.75) - sag_ * 4 * t * (1 - t)))
        radii.append(rr)
    sweep(b, pts, radii=radii, n=n, mat="cloth", col=col, wind=0.06, caps=(True, True))
    if gaff:
        b.tube((pts[0][0], pts[0][1], pts[0][2] + r * 0.9), (pts[-2][0], pts[-2][1], pts[-2][2] + r * 1.0), r=gaff, r1=gaff * 0.8, mat="planks", col=spar_col, n=5, caps=True)
    for k in range(ties):
        t = (k + 0.5) / ties
        i = min(int(t * m), m - 1)
        f = t * m - i
        c = vlerp(pts[i], pts[i + 1], f)
        rr = lerp(radii[i], radii[i + 1], f) * 1.04 + 0.006
        b.tube(vsub(c, vmul(d, 0.025)), vadd(c, vmul(d, 0.025)), r=rr, mat="cloth", col=tie_col, n=n)


def pennant(b, p, L=0.9, h=0.22, col="stripe_red"):
    """A little masthead pennant flying from the point p."""
    face2(b, [(p[0], p[1], p[2]), (p[0], p[1], p[2] - h), (p[0] - L, p[1], p[2] - h * 0.5)], "cloth", col=col, wind=(0.0, 0.0, 1.0))


# ---------------------------------------------------------------------------------------- goods
def fish(b, x=0.0, y=0.0, z=0.0, L=0.34, col="#9fb3c2", rz=0.0, belly=None):
    """A fish lying on its side on a slab."""
    w = L * 0.3
    with b.at(x, y, z, rz=rz):
        out = [(L * 0.5, 0), (L * 0.22, w * 0.5), (-L * 0.12, w * 0.42), (-L * 0.34, w * 0.1), (-L * 0.34, -w * 0.1), (-L * 0.12, -w * 0.42), (L * 0.22, -w * 0.5)]
        top = (L * 0.05, 0, w * 0.32)
        for i in range(len(out)):
            a, c = out[i], out[(i + 1) % len(out)]
            b.tri(top, (a[0], a[1], 0), (c[0], c[1], 0), "paint", col=col if a[1] + c[1] >= 0 else (belly or shade(col, 1.25)))
        b.tri((-L * 0.34, 0, 0.012), (-L * 0.5, w * 0.4, 0.012), (-L * 0.5, -w * 0.4, 0.012), "paint", col=shade(col, 0.8))


def bolt(b, p0, p1, r=0.07, col="#b5433a", n=6):
    """A bolt (roll) of cloth from p0 to p1."""
    b.tube(p0, p1, r=r, mat="cloth", col=col, n=n, caps=True)


def drape(b, p0, p1, drop=1.0, col="#b5433a", wind=0.5, rows=2, sway=0.0):
    """A length of cloth hanging from the rail p0 -> p1 (p0 on the left seen from its good side)."""
    for j in range(rows):
        t0, t1 = j / rows, (j + 1) / rows
        o0, o1 = sway * t0 * t0, sway * t1 * t1
        pts = [(p0[0], p0[1] - o0, p0[2] - drop * t0), (p0[0], p0[1] - o1, p0[2] - drop * t1), (p1[0], p1[1] - o1, p1[2] - drop * t1), (p1[0], p1[1] - o0, p1[2] - drop * t0)]
        face2(b, pts, "cloth", col=col, wind=(wind * t0, wind * t1, wind * t1, wind * t0))


# ---------------------------------------------------------------------------------------- quays
def quay_out(z):
    """How far a battered quay face stands out at height z (nothing at the top)."""
    return BATTER * (PAVE - z)


QUAY_BANDS = [(-DEEP, -5.4, 0.9, 0.5), (-5.4, -4.0, 0.8, 0.62), (-4.0, -2.7, 0.55, 0.78), (-2.7, -1.4, 0.2, 0.92), (-1.4, PAVE, 0.0, 1.0)]


def quay_tone(z, col=QUAY_COL, moss="#a9b58c"):
    """The colour of quay stonework at height z (matching quay_face's bands)."""
    for (za, zb, m, k) in QUAY_BANDS:
        if z <= zb:
            return shade(mix(col, moss, m), k)
    return C(col)


def quay_face(b, x0, x1, yf=-QUAY_D / 2, col=QUAY_COL, mat="ashlar", moss="#a9b58c", cell=2.0, grow0=False, grow1=False, top=PAVE):
    """The battered front of a quay from x0 to x1, facing -y, from `top` down to DEEP: weedier and darker
    toward the water. grow0 / grow1 let that end spread with the batter (at an outer corner)."""
    n = max(1, round((x1 - x0) / cell))
    uo, vo = b.uvo()
    for (za, zb, m, k) in QUAY_BANDS:
        zb = min(zb, top)
        if zb <= za + 1e-6:
            continue
        c = shade(mix(col, moss, m), k)
        oa, ob = quay_out(za), quay_out(zb)
        X = lambda t, o: lerp(x0 - (o if grow0 else 0.0), x1 + (o if grow1 else 0.0), t)
        for i in range(n):
            ta, tb = i / n, (i + 1) / n
            q = [(X(ta, oa), yf - oa, za), (X(tb, oa), yf - oa, za), (X(tb, ob), yf - ob, zb), (X(ta, ob), yf - ob, zb)]
            b.quad(*q, mat, col=c, uv=[(uo + v[0], vo + v[2]) for v in q])


def quay_deck(b, x0, x1, y0=-QUAY_D / 2, y1=QUAY_D / 2, mat="flagstone", col="sand", cell=2.0, back=0.7, z=PAVE):
    """Paving from x0 to x1 and y0 to y1 at the level of the quay, with a kerb face `back` deep down its landward
    (+y) edge."""
    n = max(1, round((x1 - x0) / cell))
    uo, vo = b.uvo()
    for i in range(n):
        xa, xb = lerp(x0, x1, i / n), lerp(x0, x1, (i + 1) / n)
        b.quad((xa, y0, z), (xb, y0, z), (xb, y1, z), (xa, y1, z), mat, col=col, uv=[(uo + xa, vo + y0), (uo + xb, vo + y0), (uo + xb, vo + y1), (uo + xa, vo + y1)])
        if back:
            b.quad((xb, y1, z - back), (xa, y1, z - back), (xa, y1, z), (xb, y1, z), "ashlar", col=shade(col, 0.9))


def quay_coping(b, x0, x1, yf=-QUAY_D / 2, depth=0.62, thick=0.34, col="stone", mat="ashlar", wmin=0.8, wmax=1.25):
    """Big coping stones along the edge of a quay from x0 to x1, standing a finger proud of the paving."""
    for xa, xb in split(b, x0, x1, wmin, wmax):
        b.stone(xb - xa - 0.015, depth, thick, mat=mat, col=col, x=(xa + xb) / 2, y=yf - 0.05 + depth / 2, z=PAVE + 0.045 - thick, jitter=0.05, ch=0.16)


def quay_end(b, x, side, yf=-QUAY_D / 2, yb=QUAY_D / 2, mat="ashlar", col=QUAY_COL, wall=1.2):
    """Close the end of a quay run at x: side = -1 (the end faces -x) or 1."""
    lo = quay_out(-DEEP)
    for poly in ([(yf - lo, -DEEP), (yf + wall, -DEEP), (yf + wall, PAVE), (yf, PAVE)], [(yf + wall, -0.7), (yb, -0.7), (yb, PAVE), (yf + wall, PAVE)]):
        pts = [(x, y, z) for y, z in poly]
        b.face(pts if side > 0 else list(reversed(pts)), mat, col=shade(col, 0.8))


def quay_stones(b, x0, x1, n=12, z0=-4.4, z1=-0.5, yf=-QUAY_D / 2, col=QUAY_COL, mat="ashlar", size=(0.5, 0.95)):
    """Dressed blocks standing a little proud of a quay face."""
    rng = b.rng
    lean = math.degrees(math.atan(BATTER))
    for _ in range(n):
        w = rng.uniform(*size)
        hh = w * rng.uniform(0.42, 0.6)
        x, z = rng.uniform(x0 + w / 2 + 0.05, x1 - w / 2 - 0.05), rng.uniform(z0, z1 - hh)
        tone = shade(quay_tone(z + hh / 2, col=col), 1.07)          # (weathered like the face round it, a shade lighter)
        with b.at(x, yf - quay_out(z + hh / 2) + 0.02, z + hh / 2, rx=-lean):
            with b.at(rx=90):
                b.stone(w, hh, 0.06, mat=mat, col=tone, jitter=0.1, ch=0.2)


def quay_segment(b, L=8.0, ladder=None, rings=(-2.9, 0.4), fenders=(-1.4, 3.4), bollard=-0.6, gull=False, ends=""):
    """A straight run of quay edge along x, centred on the origin, its face toward -y: battered dressed-stone
    wall from the deck (z = 0) down to DEEP, coping, a strip of paving QUAY_D deep, timber fenders, iron rings,
    a bollard, and (ladder = x) an iron ladder."""
    import parts_h as PH
    x0, x1 = -L / 2, L / 2
    yf = -QUAY_D / 2
    lean = math.degrees(math.atan(BATTER))
    with b.detail(0):
        quay_face(b, x0, x1)
        quay_deck(b, x0, x1)
        if "l" in ends:
            quay_end(b, x0, -1)
        if "r" in ends:
            quay_end(b, x1, 1)
    with b.detail(1):
        quay_coping(b, x0, x1)
        for x in fenders:
            za, zb = -0.4, -5.8
            b.beam((x, yf - quay_out(za) - 0.11, za), (x, yf - quay_out(zb) - 0.11, zb), w=0.24, h=0.22, mat="timber", up=(0, 1, 0))
        if bollard is not None:
            bollard_stone(b, bollard, yf + 0.78, PAVE, h=0.72, r=0.19)
        if ladder is not None:
            with b.at(ladder, yf, PAVE + 0.045, rx=-lean):
                iron_ladder(b, z0=-5.8, z1=0.0, hoops=0.95)
    with b.detail(2):
        quay_stones(b, x0, x1, n=int(L * 1.6))
        for x in rings:
            with b.at(x, yf - quay_out(-1.15), -1.15):
                mooring_ring(b, r=0.15, rr=0.022)
        for x in fenders:
            for z in (-0.9, -3.0, -5.0):
                b.box(0.3, 0.05, 0.07, "metal", col="iron", x=x, y=yf - quay_out(z) - 0.235, z=z, bottom=True)
        if bollard is not None:
            rope_turns(b, bollard, yf + 0.78, PAVE + 0.28, r=0.185, turns=2)
            if gull:
                PH.gull(b, bollard, yf + 0.78, PAVE + 0.74, rz=b.r(0, 360))
        for x in (x0 + 1.1, x0 + 3.7, x1 - 1.6):
            tuft(b, x + b.r(-0.3, 0.3), QUAY_D / 2 - b.r(0.1, 0.5), PAVE, r=0.09, h=0.14, n=4)


def jetty(b, x0, x1, bents, w=2.4, col="greyoak", tall=(), post_h=1.0):
    """A timber jetty deck along x from x0 to x1, its top at the level of the quay (z = PAVE): piles in pairs at
    the x positions `bents` (those in `tall` rise post_h above the deck as mooring posts), cap beams, cross
    braces, stringers and a deck of planks with a kerb rail."""
    hw = w / 2
    zt = PAVE
    with b.detail(0):
        b.box(x1 - x0, w - 0.08, 0.05, "planks", col=shade(col, 0.7), x=(x0 + x1) / 2, z=zt - 0.09, bottom=True)
        for y in (-hw + 0.22, 0.0, hw - 0.22):
            b.beam((x0, y, zt - 0.2), (x1, y, zt - 0.2), w=0.16, h=0.22, mat="timber")
        for xb in bents:
            top = zt + post_h if xb in tall else zt - 0.3
            H = top + DEEP
            for sy in (-1, 1):
                pile(b, xb, sy * (hw - 0.16) + sy * 0.014 * H, z0=-DEEP, z1=top, r=0.15, lean=(0.0, -sy * 0.014), band=xb in tall)
            b.beam((xb, -hw - 0.12, zt - 0.42), (xb, hw + 0.12, zt - 0.42), w=0.2, h=0.2, mat="timber")
    with b.detail(1):
        planking(b, x0, x1, -hw, hw, zt, along="y", pw=0.2, t=0.045, col=col, jit=0.05)
        for sy in (-1, 1):
            b.beam((x0, sy * (hw - 0.08), zt + 0.075), (x1, sy * (hw - 0.08), zt + 0.075), w=0.1, h=0.09, mat="timber")
        for xb in bents:
            b.beam((xb, -hw + 0.1, zt - 0.75), (xb, hw - 0.02, zt - 2.55), w=0.07, h=0.16, mat="timber", up=(1, 0, 0))
            b.beam((xb, hw - 0.1, zt - 0.75), (xb, -hw + 0.02, zt - 2.55), w=0.07, h=0.16, mat="timber", up=(1, 0, 0))
            b.beam((xb, -hw - 0.1, zt - 2.7), (xb, hw + 0.1, zt - 2.7), w=0.08, h=0.16, mat="timber", up=(1, 0, 0))


# ---------------------------------------------------------------------------------------- steps and bridges
def street_steps(b, w=4.0, n=12, rise=1 / 6, going=0.42, landings=(), landing=1.3, top=0.9, mat="ashlar", col="sand", tread="cobble", tread_col="warm",
                 cheek=0.34, cheek_h=0.5, skirt=1.6, rail=True):
    """A flight of wide street steps climbing toward +y, centred on the origin: n risers, the foot at z = 0 on
    the front edge, the head a short landing at z = n * rise on the back edge. landings = which treads (1 ..
    n - 1) are deep ones. Low stepped cheek walls down both sides, an iron handrail down the middle.
    Returns {"run", "rise", "treads": [(y of its riser, depth, height), ...], "clear": width between the walls}."""
    depths = [landing if k in landings else going for k in range(1, n)] + [top]
    run = sum(depths)
    y = -run / 2
    info = []
    for k in range(1, n + 1):
        info.append((y, depths[k - 1], k * rise))
        y += depths[k - 1]
    iw = w - 2 * cheek
    with b.detail(0):
        for k, (yk, d, z) in enumerate(info):
            b.box(iw, d, rise + skirt, mat, col=col, y=yk + d / 2, z=z - rise - skirt, sides="f" if k < n - 1 else "fb", cap=tread, capcol=tread_col)
        g = 0
        while g < n:
            e = min(g + 2, n - 1)
            ya, yb = info[g][0], info[e][0] + info[e][1]
            zt = info[e][2] + cheek_h
            zb = info[g][2] - rise - skirt
            for sx in (-1, 1):
                b.box(cheek, yb - ya, zt - zb, "masonry", col="warm", x=sx * (w / 2 - cheek / 2), y=(ya + yb) / 2, z=zb, sides="frl" if e < n - 1 else "frbl")
            g = e + 1
    with b.detail(1):
        g = 0
        while g < n:
            e = min(g + 2, n - 1)
            ya, yb = info[g][0], info[e][0] + info[e][1]
            zt = info[e][2] + cheek_h
            for sx in (-1, 1):
                with b.at(sx * (w / 2 - cheek / 2), (ya + yb) / 2, 0, rz=90):
                    cap_slabs(b, -(yb - ya) / 2, (yb - ya) / 2, lambda _x: zt, cheek, over=0.04, thick=0.09, col="#f1e4cc", wmin=0.5, wmax=0.8)
            g = e + 1
        for (yk, d, z) in info:
            for xa, xb in split(b, -iw / 2, iw / 2, 0.7, 1.3):
                b.box(xb - xa - 0.012, 0.3, rise + 0.014, mat, col=shade(col, b.r(0.9, 1.08)), x=(xa + xb) / 2, y=yk + 0.15 - 0.014, z=z - rise, sides="f")
        if rail:
            tops = []
            for k in range(0, n, 3):
                yk, d, z = info[k]
                p = (0.0, yk + d * 0.5, z)
                b.tube(p, (p[0], p[1], p[2] + 0.95), r=0.022, mat="metal", col="iron", n=5)
                tops.append((p[0], p[1], p[2] + 0.95))
            sweep(b, tops, r=0.024, n=4, mat="metal", col="iron", caps=(True, True))
    return {"run": run, "rise": n * rise, "treads": info, "clear": iw}


def arch_bridge(b, span=6.0, width=3.4, rise=2.0, spring=-1.2, approach=3.0, ring=0.36, fill=0.14, parapet=0.85, pt=0.34, deep=4.0, nseg=12,
                mat="masonry", col="warm", stone="ashlar", stone_col="sand", road="cobble", road_col="warm", nv=13, cope=True, stones=10):
    """A hump-backed stone bridge along x, centred on the origin: one segmental arch of the given span springing
    at height `spring` (below the road ends, which are at z = 0 at x = +-(span / 2 + approach)), rising `rise`.
    width = over the parapets (pt thick, `parapet` high). The stream runs along y underneath; abutments go `deep`
    down. Returns {"half", "hump", "road": f(x), "crown"}."""
    R = (rise * rise + (span / 2) ** 2) / (2 * rise)
    cz = spring + rise - R
    alpha = math.asin(min((span / 2) / R, 1.0))
    crown = spring + rise
    hump = crown + ring + fill
    half = span / 2 + approach
    hw = width / 2
    road_z = lambda x: hump * 0.5 * (1 + math.cos(math.pi * min(abs(x) / half, 1.0)))
    A = lambda ph, r: (r * math.sin(ph), cz + r * math.cos(ph))
    arch = [A(-alpha + 2 * alpha * i / nseg, R) for i in range(nseg + 1)]
    arch[0], arch[-1] = (-span / 2, spring), (span / 2, spring)
    na = max(2, round(approach / 1.2))
    cols_ = [(-half + approach * i / na, -half + approach * (i + 1) / na, -deep, -deep) for i in range(na)]
    cols_ += [(arch[i][0], arch[i + 1][0], arch[i][1], arch[i + 1][1]) for i in range(nseg)]
    cols_ += [(span / 2 + approach * i / na, span / 2 + approach * (i + 1) / na, -deep, -deep) for i in range(na)]
    uo, vo = b.uvo()
    col = C(col)
    with b.detail(0):
        for (xa, xb, za, zb) in cols_:
            ra, rb = road_z(xa), road_z(xb)
            pa, pb = ra + parapet, rb + parapet
            for sgn in (-1, 1):
                y, yi = sgn * hw, sgn * (hw - pt)
                q = [(xa, y, za), (xb, y, zb), (xb, y, pb), (xa, y, pa)]
                uv = [(uo + v[0] + 20 * (sgn > 0), vo + v[2]) for v in q]
                if sgn > 0:
                    q.reverse(); uv.reverse()
                b.face(q, mat, col=col, uv=uv)
                q = [(xb, yi, rb), (xa, yi, ra), (xa, yi, pa), (xb, yi, pb)]
                if sgn > 0:
                    q.reverse()
                b.face(q, mat, col=shade(col, 0.95))
                q = [(xa, y, pa), (xb, y, pb), (xb, yi, pb), (xa, yi, pa)]
                if sgn > 0:
                    q.reverse()
                b.face(q, stone, col=stone_col)
            b.quad((xa, -hw + pt, ra), (xb, -hw + pt, rb), (xb, hw - pt, rb), (xa, hw - pt, ra), road, col=road_col,
                   uv=[(uo + xa, vo - hw), (uo + xb, vo - hw), (uo + xb, vo + hw), (uo + xa, vo + hw)])
        acc = 0.0
        for i in range(nseg):          # the barrel
            (xa, za), (xb, zb) = arch[i], arch[i + 1]
            Ls = math.hypot(xb - xa, zb - za)
            b.quad((xa, -hw, za), (xa, hw, za), (xb, hw, zb), (xb, -hw, zb), mat, col=shade(col, 0.8),
                   uv=[(uo - hw, vo + 9 + acc), (uo + hw, vo + 9 + acc), (uo + hw, vo + 9 + acc + Ls), (uo - hw, vo + 9 + acc + Ls)])
            acc += Ls
        x = -span / 2
        b.quad((x, -hw, -deep), (x, hw, -deep), (x, hw, spring), (x, -hw, spring), mat, col=shade(col, 0.8))
        b.quad((-x, hw, -deep), (-x, -hw, -deep), (-x, -hw, spring), (-x, hw, spring), mat, col=shade(col, 0.8))
        for sx in (-1, 1):             # the ends
            x = sx * half
            for (ya, yb) in ((-hw + pt, -hw), (hw, hw - pt)):
                q = [(x, ya, 0), (x, yb, 0), (x, yb, parapet), (x, ya, parapet)]
                b.face(q if sx < 0 else list(reversed(q)), mat, col=col)
            q = [(x, hw, -deep), (x, -hw, -deep), (x, -hw, 0), (x, hw, 0)]
            b.face(q if sx < 0 else list(reversed(q)), mat, col=shade(col, 0.8))
    with b.detail(1):
        proud = 0.045
        for k in range(nv):            # the arch ring, both faces
            pa, pb = -alpha + 2 * alpha * k / nv, -alpha + 2 * alpha * (k + 1) / nv
            key = k == nv // 2
            ro = R + ring * (1.28 if key else 1.0)
            pr = proud * (1.8 if key else 1.0)
            c = shade(stone_col, 1.06 if key else (0.92 if k % 2 else 1.02))
            (ax, az), (bx, bz) = A(pa, R), A(pb, R)
            (cx, cz_), (dx, dz) = A(pb, ro), A(pa, ro)
            for sgn in (-1, 1):
                yo, yw = sgn * (hw + pr), sgn * hw
                f = [(ax, yo, az), (bx, yo, bz), (cx, yo, cz_), (dx, yo, dz)]
                t = [(dx, yo, dz), (cx, yo, cz_), (cx, yw, cz_), (dx, yw, dz)]
                u = [(bx, yo, bz), (ax, yo, az), (ax, yw, az), (bx, yw, bz)]
                for q in (f, t, u):
                    b.face(q if sgn < 0 else list(reversed(q)), stone, col=c)
        for sx in (-1, 1):             # end piers
            for sy in (-1, 1):
                with b.at(sx * (half - 0.28), sy * (hw - pt / 2), 0):
                    b.box(pt + 0.2, pt + 0.2, parapet + 0.55, stone, col=stone_col, z=-0.3)
                    b.box(pt + 0.3, pt + 0.3, 0.16, stone, col=stone_col, z=parapet + 0.25, taper=0.35, bottom=True)
    with b.detail(2):
        if cope:
            m = max(4, round(2 * half / 0.62))
            for i in range(m):
                xa, xb = -half + 0.5 + (2 * half - 1.0) * i / m, -half + 0.5 + (2 * half - 1.0) * (i + 1) / m
                xm = (xa + xb) / 2
                za, zb = road_z(xa) + parapet, road_z(xb) + parapet
                ang = math.degrees(math.atan2(zb - za, xb - xa))
                Ls = math.hypot(xb - xa, zb - za)
                for sy in (-1, 1):
                    with b.at(xm, sy * (hw - pt / 2), (za + zb) / 2, ry=-ang):
                        b.box(Ls - 0.012, pt + 0.09, 0.1, stone, col=shade(stone_col, b.r(0.9, 1.08)), z=-0.015, ty=0.9)
        rng = b.rng
        for sgn in (-1, 1):
            for _ in range(stones):
                w = rng.uniform(0.35, 0.7)
                hh = w * rng.uniform(0.45, 0.7)
                x = rng.uniform(-half + 0.6, half - 0.6)
                lo = -0.3
                if abs(x) < span / 2:
                    lo = max(lo, cz + math.sqrt(max((R + ring) ** 2 - x * x, 0.0)) + 0.08)
                hi = road_z(x) + parapet - hh - 0.12
                if hi <= lo:
                    continue
                z = rng.uniform(lo, hi)
                with b.at(x, sgn * (hw - 0.02), z + hh / 2, rz=0 if sgn < 0 else 180):
                    with b.at(ry=rng.uniform(-4, 4)):
                        with b.at(rx=90):
                            b.stone(w, hh, 0.07, mat=mat, col=col, jitter=0.16)
    return {"half": half, "hump": hump, "road": road_z, "crown": crown, "hw": hw}


# ---------------------------------------------------------------------------------------- green things
def hedge(b, x0, x1, h=1.5, t=0.9, col="#6fa857", wild=0.1, ends="lr", skirt=0.3, cell=0.75):
    """A clipped hedge along x from x0 to x1, centred on y = 0: lumpy in between, flat and matching at its ends."""
    n = max(2, round((x1 - x0) / cell))
    base = [(-t / 2, -skirt), (-t / 2, h * 0.5), (-t * 0.42, h * 0.9), (-t * 0.2, h), (t * 0.2, h), (t * 0.42, h * 0.9), (t / 2, h * 0.5), (t / 2, -skirt)]
    rng = b.rng
    rows = []
    for i in range(n + 1):
        x = lerp(x0, x1, i / n)
        a = wild if 0 < i < n else 0.0
        rows.append([(x + (rng.uniform(-a, a) if 0 < j < 7 else 0.0), y + (rng.uniform(-a, a) if j in (1, 2, 5, 6) else 0.0), z + (rng.uniform(-a, a) if 1 < j < 6 else 0.0))
                     for j, (y, z) in enumerate(base)])
    cols = lambda i, j: shade(col, (0.8, 0.95, 1.06, 1.12, 1.06, 0.95, 0.8)[j] * (0.94 + 0.12 * ((i * 7 + j * 3) % 5) / 4))
    loft(b, rows, "ivy", cols=cols, wind=lambda i, j: (0.0, 0.05, 0.14, 0.2, 0.2, 0.14, 0.05, 0.0)[j])
    if "l" in ends:
        b.face(rows[0], "ivy", col=shade(col, 0.85))
    if "r" in ends:
        b.face(list(reversed(rows[-1])), "ivy", col=shade(col, 0.85))


def crown(b, lumps, col="#6fae52", wind=0.45, seg=8, rings=4, rough=0.22, vary=0.12):
    """A tree crown from lumps [(x, y, z, rx[, ry, rz]), ...]."""
    rng = b.rng
    for l in lumps:
        x, y, z, rx = l[:4]
        ry = l[4] if len(l) > 4 else rx
        rz = l[5] if len(l) > 5 else rx * 0.85
        b.blob(rx, ry, rz, mat="ivy", col=shade(col, rng.uniform(1 - vary, 1 + vary)), x=x, y=y, z=z, seg=seg, rings=rings, wind=wind, rough=rough)


# ---------------------------------------------------------------------------------------- more for boats
def shrouds(b, top, feet, r=0.012, col=TARRED):
    """Standing rigging: a line from the point `top` to each of the points in `feet`."""
    for f in feet:
        b.tube(f, top, r=r, mat="cloth", col=col, n=3)


def rudder(b, x, z0, z1, w=0.4, t=0.045, col="darkoak", tiller=1.1, tiller_z=None):
    """A rudder hung on the stern at x (its leading edge), from z0 up to z1, with a tiller reaching forward."""
    b.prism([(x - w, -t / 2), (x, -t / 2), (x, t / 2), (x - w, t / 2)], z1 - z0, "planks", col=col, z=z0, bottom=True)
    if tiller:
        tz = z1 if tiller_z is None else tiller_z
        sweep(b, [(x - 0.04, 0, z1 - 0.03), (x + tiller * 0.5, 0.03, tz + 0.06), (x + tiller, 0.06, tz + 0.02)], r=0.028, r1=0.02, n=4, mat="planks", col="#c9a57a")


def iron_gate(b, w=1.4, h=1.9, bars=8, col="iron", ajar=0.0, hinge=-1, arch=0.25, lod_bars=2):
    """One leaf of a wrought-iron gate w wide, hinged at the origin of the current frame on its left (hinge = -1)
    or right (1) edge and lying along x, opened by `ajar` degrees (inward, toward +y)."""
    with b.at(rz=-hinge * ajar):
        sx = -hinge
        X = lambda t: sx * w * t
        top = lambda t: h - arch + arch * math.sin(math.pi * t)
        b.beam((X(0.0), 0, 0.05), (X(0.0), 0, top(0.0) + 0.12), w=0.05, mat="metal", col=col)
        b.beam((X(1.0), 0, 0.05), (X(1.0), 0, top(1.0) + 0.02), w=0.045, mat="metal", col=col)
        b.beam((X(0.0), 0, 0.14), (X(1.0), 0, 0.14), w=0.03, h=0.05, mat="metal", col=col, caps=False)
        b.beam((X(0.0), 0, h * 0.55), (X(1.0), 0, h * 0.55), w=0.03, h=0.04, mat="metal", col=col, caps=False)
        n = 6
        for i in range(n):
            b.beam((X(i / n), 0, top(i / n)), (X((i + 1) / n), 0, top((i + 1) / n)), w=0.03, h=0.045, mat="metal", col=col, caps=False)
        with b.detail(lod_bars):
            for i in range(1, bars):
                t = i / bars
                b.beam((X(t), 0, 0.14), (X(t), 0, top(t) + 0.16), w=0.022, mat="metal", col=col, caps=False)
                b.tri((X(t) - 0.035, 0, top(t) + 0.14), (X(t) + 0.035, 0, top(t) + 0.14), (X(t), 0, top(t) + 0.3), "metal", col=col)
                b.tri((X(t) + 0.035, 0, top(t) + 0.14), (X(t) - 0.035, 0, top(t) + 0.14), (X(t), 0, top(t) + 0.3), "metal", col=col)


# ---------------------------------------------------------------------------------------- casks, cases, sacks
def barrel(b, x=0.0, y=0.0, z=0.0, r=0.3, h=0.8, col="#c9a57a", lying=None, seg=9, hoops=True):
    """A barrel standing on (x, y, z); or with lying = a heading in degrees, on its side along that heading.
    (Unlike parts.barrel it takes the detail level you are in.)"""
    def body():
        b.revolve([(r * 0.8, 0.0), (r, h * 0.3), (r, h * 0.7), (r * 0.8, h)], "planks", col=col, seg=seg, close_top=True, close_bottom=lying is not None)
        if hoops:
            for zz in (h * 0.14, h * 0.86):
                b.revolve([(r * 0.9, zz - 0.03), (r * 0.925, zz + 0.03)], "metal", col="iron", seg=seg)
    with b.at(x, y, z):
        if lying is None:
            body()
        else:
            with b.at(0, 0, r * 0.98, rz=lying):
                with b.at(0, h / 2, 0, rx=90):
                    body()


def crate(b, x=0.0, y=0.0, z=0.0, w=0.6, d=None, h=None, col="#d8c3a0", rz=0.0, slats=True):
    """A packing case w by d by h (a cube by default) standing on (x, y, z), with corner battens and a brace."""
    d = w if d is None else d
    h = w if h is None else h
    with b.at(x, y, z, rz=rz):
        b.box(w, d, h, "planks", col=col)
        if slats:
            with b.detail(2):
                c = shade(col, 0.78)
                for sx in (-1, 1):
                    for sy in (-1, 1):
                        b.box(0.07, 0.07, h + 0.012, "planks", col=c, x=sx * (w / 2 - 0.02), y=sy * (d / 2 - 0.02))
                for sy in (-1, 1):
                    b.beam((-w / 2 + 0.06, sy * (d / 2 + 0.008), 0.05), (w / 2 - 0.06, sy * (d / 2 + 0.008), h - 0.05), w=0.02, h=0.07, mat="planks", col=c, up=(0, 1, 0), caps=False)


def sack(b, x=0.0, y=0.0, z=0.0, r=0.3, col="#d9c9a3", flat=0.7, tie=True):
    """A full sack sitting on (x, y, z)."""
    b.blob(r, r * 0.85, r * flat, mat="cloth", col=col, x=x, y=y, z=z + r * flat * 0.85, seg=6, rings=3, rough=0.12)
    if tie:
        b.blob(r * 0.22, r * 0.22, r * 0.2, mat="cloth", col=shade(col, 0.85), x=x, y=y, z=z + r * flat * 1.75, seg=5, rings=2, rough=0.1)
