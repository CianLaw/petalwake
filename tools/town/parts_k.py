"""Petalwake town kit, craft-quarter parts (district prefix k_): what Larkhaven's workshops are dressed with.

Written with kit primitives only, in the manner of parts.py: cloth on lines and rails, louvres, an open
(boarded-under) roof for shelters, a mill wheel, casks in every state, pots and racks, chimneys of several
shapes, a ridge ventilator, a hoist, a bell cupola, domes, an arcade, yard walls and paving, timber stacks,
the smith's and the carpenter's and the chandler's gear, and hanging signs with craft emblems.

Compass angles: 0 = toward local -y (the front), 90 = +x. Things stand at the origin of the current frame
unless x, y, z are given. Detail levels as in parts.py (0 structure, 1 silhouette, 2 fine dressing).
"""
import math

from kit import C, lerp, rad, shade

import parts as P

# dyers' colours: madder, indigo, weld, green, plum, saffron, woad, rose, undyed
DYES = ["#b8433a", "#2f4f8f", "#e0b23a", "#5a9a68", "#7a4672", "#d9803a", "#6fa3c8", "#c8587c", "#f3ecd9"]
ROPE = "#8a7a66"
SOOT = "#2b2724"


# ---------------------------------------------------------------------------------------- cloth
def cloth(b, w, h, col, x=0.0, y=0.0, z=0.0, face=0.0, rows=4, sway=1.0, belly=0.0, hem=None, lod=1, taper=0.0):
    """A length of cloth hanging from its top edge (the middle of which is at (x, y, z)): w wide, h long, turned to
    face compass `face`. Fixed along the top, free at the bottom (sway = how much it flies in the wind).
    belly bows it out; hem = colour of a border along the bottom; taper narrows it toward the bottom."""
    col = C(col)
    with b.at(x, y, z, rz=face):
        with b.detail(lod):
            for j in range(rows):
                t0, t1 = j / rows, (j + 1) / rows
                z0, z1 = -h * t0, -h * t1
                y0, y1 = -belly * math.sin(math.pi * t0), -belly * math.sin(math.pi * t1)
                w0, w1 = w * (1 - taper * t0), w * (1 - taper * t1)
                c = C(hem) if (hem is not None and j == rows - 1) else col
                p = [(-w1 / 2, y1, z1), (w1 / 2, y1, z1), (w0 / 2, y0, z0), (-w0 / 2, y0, z0)]
                k0, k1 = sway * t0 ** 1.3, sway * t1 ** 1.3
                b.face(p, "cloth", col=c, wind=(k1, k1, k0, k0))
                b.face(list(reversed(p)), "cloth", col=shade(c, 0.86), wind=(k0, k0, k1, k1))


def cloth_line(b, p0, p1, n=4, cols=None, drop=(1.2, 2.0), width=(0.7, 1.1), sag=0.25, lod=1, rope=True, sway=1.0, rows=3):
    """A drying line from p0 to p1 hung with n lengths of dyed cloth (longer and bolder than washing)."""
    rng = b.rng
    order = list(cols or DYES)
    if cols is None:
        rng.shuffle(order)
    N = 6
    pt = lambda t: (lerp(p0[0], p1[0], t), lerp(p0[1], p1[1], t), lerp(p0[2], p1[2], t) - sag * 4 * t * (1 - t))
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    if rope:
        with b.detail(lod):
            for i in range(N):
                b.beam(pt(i / N), pt((i + 1) / N), w=0.022, mat="cloth", col=ROPE, caps=False)
    for k in range(n):
        t = (k + 0.5) / n + rng.uniform(-0.12, 0.12) / n
        c = pt(t)
        ww = min(rng.uniform(*width), L / n * 0.92)
        hh = rng.uniform(*drop)
        cloth(b, ww, hh, order[k % len(order)], x=c[0], y=c[1], z=c[2] + 0.01, face=ang, rows=rows, sway=sway, lod=lod)


def draped(b, p0, p1, n=3, cols=None, drop=(1.8, 2.6), width=(0.55, 0.85), inside=0.28, off=0.075, lod=1, sway=0.8, rows=4):
    """Lengths of cloth thrown over a rail whose top runs from p0 to p1, hanging down its outer side (the outside
    is on the right going from p0 to p1: list a gallery's rails anticlockwise as seen from above)."""
    rng = b.rng
    order = list(cols or DYES)
    if cols is None:
        rng.shuffle(order)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    ox, oy = dy / L, -dx / L
    face = math.degrees(math.atan2(ox, -oy))
    for k in range(n):
        t = (k + 0.5) / n + rng.uniform(-0.15, 0.15) / n
        ww = min(rng.uniform(*width), L / n * 0.9)
        hh = rng.uniform(*drop)
        col = C(order[k % len(order)])
        with b.at(p0[0] + dx * t, p0[1] + dy * t, lerp(p0[2], p1[2], t), rz=face):
            with b.detail(lod):
                b.face([(-ww / 2, -off, 0.02), (ww / 2, -off, 0.02), (ww / 2, off, 0.02), (-ww / 2, off, 0.02)], "cloth", col=col)
            cloth(b, ww, hh, col, y=-off, z=0.02, face=0, rows=rows, sway=sway, lod=lod)
            cloth(b, ww, inside, col, y=off, z=0.02, face=180, rows=1, sway=0.15, lod=lod)


def bolt(b, x=0.0, y=0.0, z=0.0, L=0.9, r=0.11, col="#b8433a", rz=0.0, lod=2):
    """A rolled bolt of cloth lying along the local x axis."""
    with b.at(x, y, z + r, rz=rz):
        with b.at(-L / 2, 0, 0, ry=90):
            with b.detail(lod):
                b.revolve([(r, 0.0), (r, L)], "cloth", col=col, seg=6)
                b.disc(r, "cloth", col=shade(col, 0.8), seg=6, z=L)
                b.disc(r, "cloth", col=shade(col, 0.8), seg=6, z=0.0, down=True)


# ---------------------------------------------------------------------------------------- timber work
def slats(b, w, h, x=0.0, y=0.0, z=0.0, face=0.0, pitch=0.3, board=0.22, tilt=30.0, t=0.03, mat="planks", col="greyoak", lod=1):
    """Horizontal louvre boards filling a panel w wide and h high that stands with the middle of its foot at
    (x, y, z), looking toward compass `face`. Each board leans out at its lower edge. Put something dark behind."""
    n = max(1, int(h / pitch + 0.5))
    up = (0.0, math.sin(rad(tilt)), math.cos(rad(tilt)))
    with b.at(x, y, z, rz=face):
        for i in range(n):
            zz = (i + 0.5) * h / n
            b.beam((-w / 2, 0.0, zz), (w / 2, 0.0, zz), w=t, h=board, mat=mat, col=shade(col, b.r(0.86, 1.06)), lod=lod, up=up, caps=False)


def open_roof(b, w, d, section=None, pitch=40.0, mat="shingle", col=None, x=0.0, y=0.0, z=0.0, eave=0.45, thick=0.14, course=0.4,
              under="planks", under_col="darkoak", rafters=True, lod=0, flyunder=None):
    """A hipped roof (a pyramid when w == d) for an open shelter standing on posts: Building.loop_roof plus a boarded
    underside and hip rafters, so it can be looked at from below. z = the height of the plates it sits on.

    flyunder = a colour: for a roof the rider flies in under to land. The game's collision grid (assemble.py) takes
    the top of every always-drawn hard face as the floor, and the landing autopilot will not go beneath it, so such
    a roof is drawn from the mid level (detail 1) and only a plain stand-in of that colour in the 'paint' material
    (which the grid ignores), tucked just beneath the tiles, is left at the far level. Returns the rise."""
    run = min(w, d) / 2
    if section is None:
        section = [(0.0, 0.0), (run, run * math.tan(rad(pitch)))]
    hw, hd = w / 2, d / 2

    def loop(inset, zz):
        a, c = max(hw - inset, 0.0), max(hd - inset, 0.0)
        return [(-a, -c, zz), (a, -c, zz), (a, c, zz), (-a, c, zz)]

    lv = 1 if flyunder is not None else lod
    with b.detail(lv):
        b.loop_roof(w, d, mat=mat, col=col, x=x, y=y, z=z, eave=eave, thick=thick, course=course, section=section)
    with b.at(x, y, z):
        with b.detail(lv):
            for k in range(len(section) - 1):
                A, B = loop(section[k][0], section[k][1] - thick), loop(section[k + 1][0], section[k + 1][1] - thick)
                for i in range(4):
                    j = (i + 1) % 4
                    b.face((A[j], A[i], B[i], B[j]), under, col=under_col)
        if flyunder is not None:
            s0 = (section[1][1] - section[0][1]) / max(section[1][0] - section[0][0], 1e-6)
            prof = [(-eave, -eave * s0)] + list(section[1:])
            for k in range(len(prof) - 1):
                A, B = loop(prof[k][0], prof[k][1] - 0.09), loop(prof[k + 1][0], prof[k + 1][1] - 0.09)
                for i in range(4):
                    j = (i + 1) % 4
                    b.face((A[i], A[j], B[j], B[i]), "paint", col=shade(flyunder, 0.92 + 0.06 * (i % 2)), lod=0)
        if rafters:
            top = (0.0, 0.0, section[-1][1] - thick - 0.06)
            with b.detail(2):
                for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    q = (sx * (hw - section[1][0]), sy * (hd - section[1][0]), section[1][1] - thick - 0.06) if len(section) > 2 else None
                    p = (sx * hw, sy * hd, -thick - 0.06)
                    if q:
                        b.beam(p, q, w=0.09, h=0.12, mat="timber", col=under_col, caps=False)
                        b.beam(q, top, w=0.09, h=0.12, mat="timber", col=under_col, caps=False)
                    else:
                        b.beam(p, top, w=0.09, h=0.12, mat="timber", col=under_col, caps=False)
    return section[-1][1]


def knee(b, x, y, z, dx=0.0, dy=0.0, drop=0.7, w=0.1, col="darkoak", lod=1):
    """A knee brace from a post at (x, y, z - drop) up to a beam at (x + dx, y + dy, z)."""
    b.beam((x, y, z - drop), (x + dx, y + dy, z), w=w, mat="timber", col=col, lod=lod)


def plank_stack(b, x=0.0, y=0.0, z=0.0, L=3.0, w=0.9, layers=5, rz=0.0, col="#e0c79c", t=0.07, lod=1):
    """Sawn boards stacked with sticks between the layers to season, lying along the local y axis."""
    with b.at(x, y, z, rz=rz):
        with b.detail(2):
            for yy in (-L * 0.32, L * 0.32):
                b.beam((-w / 2 - 0.05, yy, 0.06), (w / 2 + 0.05, yy, 0.06), w=0.12, mat="timber", col="darkoak")
        zz = 0.12
        for i in range(layers):
            ln = L * b.r(0.9, 1.0)
            b.box(w * b.r(0.92, 1.0), ln, t, "planks", col=shade(col, b.r(0.88, 1.08)), x=b.r(-0.03, 0.03), y=b.r(-0.08, 0.08), z=zz, lod=lod, bottom=True)
            zz += t
            if i < layers - 1:
                with b.detail(2):
                    for yy in (-L * 0.33, 0.0, L * 0.33):
                        b.beam((-w / 2, yy, zz + 0.015), (w / 2, yy, zz + 0.015), w=0.05, h=0.03, mat="planks", col=shade(col, 0.8), caps=False)
                zz += 0.03
    return zz


def log(b, L, r=0.15, col="#9a7a5a", end="#e6cfa4", seg=6, lod=1):
    """One round log lying along the local +y axis from the origin (its centre line)."""
    with b.at(rx=-90):
        with b.detail(lod):
            b.revolve([(r, 0.0), (r * 0.94, L)], "timber", col=col, seg=seg)
            b.disc(r * 0.94, "planks", col=end, seg=seg, z=L)
            b.disc(r, "planks", col=end, seg=seg, z=0.0, down=True)


def log_pile(b, x=0.0, y=0.0, z=0.0, L=2.4, n=4, rows=None, rz=0.0, r=0.15, col="#9a7a5a", lod=1):
    """Round logs piled n wide at the bottom and one fewer in each row above, lying along the local y axis."""
    with b.at(x, y, z, rz=rz):
        for row in range(rows or n):
            m = n - row
            if m <= 0:
                break
            for i in range(m):
                rr = r * b.r(0.88, 1.04)
                with b.at((i - (m - 1) / 2) * 2 * r, -L / 2 + b.r(-0.12, 0.12), row * r * 1.73 + r):
                    log(b, L * b.r(0.92, 1.0), rr, col=shade(col, b.r(0.85, 1.1)), lod=lod)


def firewood(b, x=0.0, y=0.0, z=0.0, w=1.6, h=1.0, d=0.45, rz=0.0, col="#a58462", lod=2):
    """A stack of split firewood against a wall: w long (x), h high, d deep; its back on the local x axis."""
    with b.at(x, y, z, rz=rz):
        b.box(w, d * 0.8, h * 0.94, "planks", col=shade(col, 0.62), y=-d * 0.42, lod=1)
        with b.detail(lod):
            n, m = max(2, int(w / 0.2)), max(2, int(h / 0.19))
            for j in range(m):
                for i in range(n):
                    if b.chance(0.12) and j == m - 1:
                        continue
                    xx = -w / 2 + w * (i + 0.5 + 0.5 * (j % 2)) / (n + 0.5)
                    b.box(w / n * 0.86, 0.06, h / m * 0.84, "planks", col=shade("#e6cfa4", b.r(0.75, 1.05)), x=xx, y=-d + 0.02 - b.r(0, 0.05), z=h * j / m + 0.01, bottom=True)


def leaning_planks(b, x=0.0, y=0.0, z=0.0, n=4, h=2.6, rz=0.0, col="#e0c79c", lean=0.5, lod=2):
    """Boards stood on end leaning back against a wall that lies along the local x axis (they lean toward +y)."""
    with b.at(x, y, z, rz=rz):
        with b.detail(lod):
            for i in range(n):
                hh = h * b.r(0.8, 1.0)
                xx = (i - (n - 1) / 2) * 0.24 + b.r(-0.03, 0.03)
                ln = lean * b.r(0.8, 1.1)
                b.beam((xx, -ln, 0.0), (xx, -0.03, hh), w=0.2, h=0.035, mat="planks", col=shade(col, b.r(0.85, 1.08)), up=(0, 1, 0.2))


def sawhorse(b, x=0.0, y=0.0, z=0.0, rz=0.0, L=1.5, h=0.75, log_on=True, col="greyoak", lod=2):
    """A saw-horse lying along the local x axis: two crossed trestles joined by a rail, a log in its crutch and a
    saw left in the cut."""
    with b.at(x, y, z, rz=rz):
        with b.detail(lod):
            for sx in (-1, 1):
                xx = sx * L * 0.36
                b.beam((xx, -0.38, 0), (xx, 0.3, h + 0.2), w=0.08, mat="timber", col=col)
                b.beam((xx + 0.085, 0.38, 0), (xx + 0.085, -0.3, h + 0.2), w=0.08, mat="timber", col=col)
            b.beam((-L * 0.36, 0.0, h * 0.4), (L * 0.36 + 0.08, 0.0, h * 0.4), w=0.07, mat="timber", col=col)
        if log_on:
            zc = 0.56 * (h + 0.2) + 0.2
            with b.at(-L * 0.62, 0.02, zc, rz=-90):
                log(b, L * 1.25, 0.15, lod=lod)
            with b.detail(lod):
                p = [(0.18, -0.02, zc - 0.1), (0.2, -0.02, zc + 0.52), (0.2, 0.5, zc + 0.62), (0.18, 0.62, zc + 0.5), (0.18, 0.62, zc + 0.3)]
                b.face(p, "metal", col="lead")
                b.face(list(reversed(p)), "metal", col="lead")
                b.box(0.05, 0.16, 0.12, "planks", col="darkoak", x=0.19, y=0.68, z=zc + 0.36, bottom=True)


def workbench(b, x=0.0, y=0.0, z=0.0, rz=0.0, w=1.8, d=0.7, h=0.85, col="#c9ad82", lod=2):
    """A joiner's bench along the local x axis, with a vice, a mallet and a board in progress."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            b.box(w, d, 0.1, "planks", col=col, z=h - 0.1, bottom=True)
        with b.detail(lod):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    b.beam((sx * (w / 2 - 0.12), sy * (d / 2 - 0.1), 0), (sx * (w / 2 - 0.12), sy * (d / 2 - 0.1), h - 0.1), w=0.1, mat="timber", col="darkoak", caps=False)
            b.beam((-w / 2 + 0.12, 0, 0.22), (w / 2 - 0.12, 0, 0.22), w=0.07, mat="timber", col="darkoak", caps=False)
            b.box(0.12, 0.3, 0.2, "planks", col="darkoak", x=-w / 2 - 0.06, y=-d / 2 + 0.2, z=h - 0.22, bottom=True)        # vice
            b.box(0.9, 0.24, 0.035, "planks", col="#ecd7ae", x=0.15, y=0.05, z=h + 0.002)                                    # a board
            b.box(0.12, 0.2, 0.1, "planks", col="darkoak", x=w / 2 - 0.3, y=-0.12, z=h)                                      # a mallet
            b.beam((w / 2 - 0.3, -0.12, h + 0.05), (w / 2 - 0.3, 0.2, h + 0.05), w=0.035, mat="planks", col="greyoak")
            b.blob(0.3, 0.26, 0.09, mat="planks", col="#f0dcb4", x=0.4, y=-d / 2 - 0.3, z=0.06, seg=6, rings=2, rough=0.3, bottom=False)   # shavings


def cart_wheel(b, r=0.55, t=0.08, spokes=8, col="darkoak", tyre="iron", lod=2, seg=12):
    """A cart wheel standing in the local x-z plane, its hub at the origin (turn or tilt the frame to lean it)."""
    with b.at(rx=90):
        with b.detail(lod):
            b.revolve([(r - 0.1, -t / 2), (r, -t / 2), (r, t / 2), (r - 0.1, t / 2), (r - 0.1, -t / 2)], "timber", col=col, seg=seg, smooth=False)
            if tyre:
                b.revolve([(r + 0.012, -t / 2), (r + 0.012, t / 2)], "metal", col=tyre, seg=seg, smooth=False)
            b.revolve([(0.09, -t * 0.9), (0.09, t * 0.9), (0.0, t * 0.9)], "timber", col=col, seg=6, smooth=False)
            b.disc(0.09, "timber", col=col, seg=6, z=-t * 0.9, down=True)
            for i in range(spokes):
                a = 2 * math.pi * i / spokes
                b.beam((0.08 * math.cos(a), 0.08 * math.sin(a), 0), ((r - 0.09) * math.cos(a), (r - 0.09) * math.sin(a), 0), w=0.05, h=0.05, mat="timber", col=col, up=(0, 0, 1), caps=False)


def handcart(b, x=0.0, y=0.0, z=0.0, rz=0.0, col="greyoak", load=None, lod=2):
    """A two-wheeled hand cart standing along the local y axis (shafts toward -y, resting on their prop).
    load = 'sacks', 'barrels', 'crates' or None."""
    with b.at(x, y, z, rz=rz):
        with b.detail(lod):
            b.box(0.95, 1.5, 0.07, "planks", col=col, y=0.1, z=0.62, bottom=True)
            for sx in (-1, 1):
                b.box(0.05, 1.5, 0.3, "planks", col=shade(col, 0.9), x=sx * 0.47, y=0.1, z=0.66, bottom=True)
                b.beam((sx * 0.4, 0.85, 0.6), (sx * 0.4, -1.5, 0.74), w=0.06, mat="timber", col="darkoak")
                with b.at(sx * 0.58, 0.2, 0.5, rz=90):
                    cart_wheel(b, r=0.5, t=0.07, lod=lod, seg=10)
            b.box(0.05, 0.05, 0.6, "timber", col="darkoak", x=0, y=-0.62, z=0.0)
            b.beam((-0.5, 0.2, 0.5), (0.5, 0.2, 0.5), w=0.06, mat="timber", col="darkoak", caps=False)
        if load == "sacks":
            for (sx, sy, sz) in ((-0.2, -0.2, 0.0), (0.22, 0.0, 0.0), (-0.15, 0.45, 0.0), (0.05, 0.1, 0.3)):
                with b.detail(lod):
                    b.blob(0.3, 0.26, 0.2, mat="cloth", col=shade("#e2d6b6", b.r(0.9, 1.05)), x=sx, y=sy + 0.1, z=0.86 + sz, seg=6, rings=3, rough=0.12)
        elif load == "barrels":
            for (sx, sy) in ((-0.22, -0.3), (0.22, -0.3), (-0.22, 0.42), (0.22, 0.42)):
                barrel(b, sx, sy + 0.1, 0.69, r=0.21, h=0.6, lod=lod)
        elif load == "crates":
            P.crate(b, -0.18, -0.2, 0.69, s=0.5, rz=8)
            P.crate(b, 0.2, 0.45, 0.69, s=0.45, rz=-12)


# ---------------------------------------------------------------------------------------- the mill wheel
def waterwheel(b, r=2.3, w=0.9, spokes=8, floats=20, col="darkoak", rim=0.26, axle=(0.6, 0.9), seg=16):
    """A mill wheel with its axle along the local x axis through the origin (the wheel centred on x = 0).
    Call it inside `with b.spin(speed, axis=(1, 0, 0), wind=False):`. axle = how far the shaft runs beyond the
    wheel on the -x and +x sides."""
    hw = w / 2
    rs = r - rim
    with b.at(ry=90):                               # local z now runs along the axle (+x of the caller)
        for z0 in (-hw, hw - 0.1):
            b.revolve([(rs, z0), (r, z0), (r, z0 + 0.1), (rs, z0 + 0.1), (rs, z0)], "timber", col=col, seg=seg, smooth=False, lod=0)
        b.revolve([(rs + 0.04, -hw + 0.1), (rs + 0.04, hw - 0.1)], "planks", col=shade("greyoak", 0.8), seg=seg, smooth=False, lod=0)
        b.revolve([(rs + 0.01, hw - 0.1), (rs + 0.01, -hw + 0.1)], "planks", col=shade("greyoak", 0.55), seg=seg, smooth=False, lod=0)
        for i in range(floats):
            a = 2 * math.pi * (i + 0.5) / floats
            ca, sa = math.cos(a), math.sin(a)
            rc = r - rim / 2 + 0.09
            b.beam((rc * ca, rc * sa, -hw - 0.03), (rc * ca, rc * sa, hw + 0.03), w=0.045, h=rim + 0.2, mat="planks",
                   col=shade("greyoak", b.r(0.7, 0.95)), lod=0, up=(ca, sa, 0))
        for zz in (-hw + 0.05, hw - 0.05):
            for i in range(spokes):
                a = 2 * math.pi * i / spokes
                ca, sa = math.cos(a), math.sin(a)
                b.beam((0.2 * ca, 0.2 * sa, zz), ((rs + 0.02) * ca, (rs + 0.02) * sa, zz), w=0.14, h=0.1, mat="timber", col=col, lod=0, up=(0, 0, 1), caps=False)
        b.revolve([(0.3, -hw - 0.05), (0.3, hw + 0.05)], "timber", col=col, seg=8, smooth=False, lod=0)
        b.disc(0.3, "timber", col=col, seg=8, z=hw + 0.05, lod=0)
        b.disc(0.3, "timber", col=col, seg=8, z=-hw - 0.05, down=True, lod=0)
        b.revolve([(0.15, -hw - axle[0]), (0.15, hw + axle[1])], "timber", col=shade(col, 0.85), seg=8, smooth=False, lod=0)
        b.disc(0.15, "timber", col=col, seg=8, z=hw + axle[1], lod=0)
        b.disc(0.15, "timber", col=col, seg=8, z=-hw - axle[0], down=True, lod=0)


def millstone(b, r=0.6, t=0.18, col="grey", lod=2):
    """A millstone lying flat at the origin (tilt the frame to lean it against a wall)."""
    with b.detail(lod):
        b.revolve([(0.1, 0.0), (r, 0.0), (r, t), (0.1, t), (0.1, 0.0)], "ashlar", col=col, seg=12)
        for k in range(6):
            with b.at(rz=60 * k):
                b.box(0.03, r - 0.2, 0.012, "ashlar", col=shade(col, 0.7), y=-(r + 0.12) / 2, z=t)


# ---------------------------------------------------------------------------------------- casks
def barrel(b, x=0.0, y=0.0, z=0.0, r=0.3, h=0.8, col="#c9a57a", lod=1, lying=False, rz=0.0, seg=8, hoops=True, tilt=0.0, open_top=False):
    """A cask standing on (x, y, z), or with lying=True on its side (its length along the local x axis after turning
    rz) resting on z. Like parts.barrel, but it can be had at the mid level, lying, tilted or open."""
    def body():
        prof = [(r * 0.80, 0.0), (r * 0.96, h * 0.25), (r, h * 0.5), (r * 0.96, h * 0.75), (r * 0.80, h)]
        b.revolve(prof, "planks", col=col, seg=seg, lod=lod, close_top=not open_top, close_bottom=lying or tilt != 0.0)
        if open_top:
            b.disc(r * 0.76, "planks", col=shade(col, 0.45), seg=seg, z=h * 0.3, lod=lod)
            b.revolve([(r * 0.76, h), (r * 0.9, h * 0.75), (r * 0.76, h * 0.3)], "planks", col=shade(col, 0.6), seg=seg, lod=lod)
        if hoops:
            with b.detail(2):
                for t in (0.1, 0.34, 0.66, 0.9):
                    rr = r * (0.80 + 0.16 * min(t, 1 - t) / 0.25) if min(t, 1 - t) < 0.25 else r * (0.96 + 0.04 * (min(t, 1 - t) - 0.25) / 0.25)
                    b.revolve([(rr + 0.012, h * t - 0.022), (rr + 0.012, h * t + 0.022)], "metal", col="iron", seg=seg)
    if lying:
        with b.at(x, y, z + r, rz=rz):
            with b.at(-h / 2, 0, 0, ry=90):
                body()
    else:
        with b.at(x, y, z, rz=rz):
            with b.at(rx=tilt):
                body()


def barrel_stack(b, n=3, rows=None, x=0.0, y=0.0, z=0.0, r=0.34, h=0.9, rz=0.0, col="#c9a57a", lod=1, deep=1):
    """Casks piled on their sides: n in the bottom row (side by side along the local y axis), one fewer in each row
    above; deep = how many such piles stand end to end along the local x axis."""
    with b.at(x, y, z, rz=rz):
        for k in range(deep):
            xx = (k - (deep - 1) / 2) * (h + 0.04)
            for row in range(rows or n):
                m = n - row
                if m <= 0:
                    break
                for i in range(m):
                    barrel(b, xx, (i - (m - 1) / 2) * 2 * r * 1.01, 0.05 + row * r * 1.74, r=r, h=h, lying=True, lod=lod, col=shade(col, b.r(0.86, 1.1)))
            with b.detail(2):
                for sy in (-1, 1):
                    b.box(h * 0.8, 0.16, 0.14, "timber", col="darkoak", x=xx, y=sy * (n * r * 1.01 + 0.02), tx=1.0, ty=0.3)
                b.box(h * 0.9, n * 2 * r * 1.02, 0.05, "timber", col="darkoak", x=xx, z=0.0)


def staves(b, x=0.0, y=0.0, z=0.0, r=0.3, h=0.85, n=11, splay=0.2, col="#e3cba0", lod=2, hoop=True):
    """A cask being raised: the staves stand in one hoop and splay apart at the top like a tulip."""
    with b.at(x, y, z):
        with b.detail(lod):
            for i in range(n):
                a = 2 * math.pi * i / n
                ca, sa = math.cos(a), math.sin(a)
                sp = splay * b.r(0.7, 1.15)
                b.beam((r * 0.8 * ca, r * 0.8 * sa, 0.0), ((r + sp) * ca, (r + sp) * sa, h), w=2 * math.pi * r * 0.8 / n * 0.92, h=0.03, mat="planks",
                       col=shade(col, b.r(0.88, 1.08)), up=(ca, sa, 0))
            if hoop:
                b.revolve([(r * 0.86, h * 0.13), (r * 0.9, h * 0.2)], "metal", col="iron", seg=n)
                b.revolve([(r * 0.88, h * 0.2), (r * 0.84, h * 0.13)], "metal", col="iron", seg=n)


def hoop(b, r=0.3, col="iron", lod=2, seg=10, w=0.04):
    """An iron hoop standing in the local x-z plane (hang it on a wall or lean it)."""
    with b.at(rx=90):
        with b.detail(lod):
            b.revolve([(r, -w / 2), (r, w / 2)], "metal", col=col, seg=seg)
            b.revolve([(r - 0.012, w / 2), (r - 0.012, -w / 2)], "metal", col=shade(col, 0.8), seg=seg)


def tub(b, x=0.0, y=0.0, z=0.0, r=0.5, h=0.55, col="#b79a72", fill=None, lod=1, seg=10):
    """A coopered tub or vat. fill = colour of the liquor in it (drawn glossy), or 'water', or None for empty."""
    with b.at(x, y, z):
        with b.detail(lod):
            b.revolve([(r * 0.9, 0.0), (r, h), (r - 0.05, h), (r - 0.08, h * 0.25)], "planks", col=col, seg=seg)
            if fill == "water":
                b.disc(r - 0.05, "water", seg=seg, z=h * 0.86)
            elif fill is not None:
                b.disc(r - 0.05, "glass", col=fill, seg=seg, z=h * 0.86)
            else:
                b.disc(r - 0.07, "planks", col=shade(col, 0.5), seg=seg, z=h * 0.25)
        with b.detail(2):
            for t in (0.2, 0.8):
                rr = r * (0.9 + 0.1 * t) + 0.012
                b.revolve([(rr, h * t - 0.025), (rr, h * t + 0.025)], "metal", col="iron", seg=seg)


def bucket(b, x=0.0, y=0.0, z=0.0, r=0.15, h=0.26, col="#b79a72", lod=2):
    with b.at(x, y, z):
        with b.detail(lod):
            b.revolve([(r * 0.8, 0.0), (r, h), (r - 0.025, h), (r * 0.72, 0.04)], "planks", col=col, seg=6)
            b.disc(r * 0.74, "planks", col=shade(col, 0.5), seg=6, z=0.04)
            b.beam((-r, 0, h), (-r * 0.5, 0, h + 0.16), w=0.015, mat="metal", col="iron", caps=False)
            b.beam((-r * 0.5, 0, h + 0.16), (r * 0.5, 0, h + 0.16), w=0.015, mat="metal", col="iron", caps=False)
            b.beam((r * 0.5, 0, h + 0.16), (r, 0, h), w=0.015, mat="metal", col="iron", caps=False)


# ---------------------------------------------------------------------------------------- pots
POTS = {
    "jug": [(0.50, 0.00), (0.92, 0.22), (1.00, 0.45), (0.80, 0.70), (0.48, 0.86), (0.62, 1.00)],
    "crock": [(0.72, 0.00), (0.98, 0.20), (1.00, 0.75), (0.82, 0.92), (0.90, 1.00)],
    "bowl": [(0.45, 0.00), (0.85, 0.45), (1.00, 1.00)],
    "urn": [(0.42, 0.00), (0.36, 0.08), (0.80, 0.35), (1.00, 0.60), (0.78, 0.86), (0.60, 0.94), (0.74, 1.00)],
    "bottle": [(0.80, 0.00), (1.00, 0.10), (1.00, 0.50), (0.45, 0.72), (0.34, 1.00)],
    "vase": [(0.50, 0.00), (0.80, 0.30), (0.62, 0.62), (0.42, 0.85), (0.70, 1.00)],
    "flask": [(0.55, 0.00), (1.00, 0.18), (1.00, 0.42), (0.30, 0.62), (0.22, 0.92), (0.34, 1.00)],
    "globe": [(0.30, 0.00), (0.80, 0.14), (1.00, 0.42), (0.80, 0.70), (0.32, 0.86), (0.26, 1.00)],
}
POT_COLS = ["#c9764a", "#b8643c", "#d9925c", "#e8d9b8", "#3f8f8f", "#c9764a", "#8a5a3a", "#d9a55a", "#a59a8c"]


def pot(b, x=0.0, y=0.0, z=0.0, kind="jug", r=0.16, h=0.32, col="#c9764a", seg=6, lod=2, mat="paint", mouth=True):
    """A turned pot standing on (x, y, z). kind = a key of POTS."""
    prof = [(r * a, h * t) for a, t in POTS[kind]]
    with b.at(x, y, z):
        with b.detail(lod):
            b.revolve(prof, mat, col=col, seg=seg)
            if mouth:
                b.disc(prof[-1][0] * 0.9, mat, col=shade(col, 0.4), seg=seg, z=h * 0.98)


def pot_rack(b, w=1.8, shelves=3, h=1.7, d=0.36, x=0.0, y=0.0, z=0.0, rz=0.0, cols=None, kinds=None, fill=0.9, lod=2, mat="paint", size=1.0):
    """Drying shelves full of pots: stands on (x, y, z), the shelves running along the local x axis, open to -y."""
    cols = cols or POT_COLS
    kinds = kinds or ["jug", "crock", "bowl", "urn", "vase", "bottle"]
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    b.beam((sx * (w / 2 - 0.04), sy * (d / 2 - 0.04), 0), (sx * (w / 2 - 0.04), sy * (d / 2 - 0.04), h), w=0.07, mat="timber", col="darkoak", caps=False)
            for k in range(shelves):
                zz = 0.22 + (h - 0.3) * k / max(shelves - 1, 1)
                b.box(w, d, 0.04, "planks", col="greyoak", z=zz, bottom=True)
        for k in range(shelves):
            zz = 0.26 + (h - 0.3) * k / max(shelves - 1, 1)
            gap = (h - 0.3) / max(shelves - 1, 1) - 0.08
            xx = -w / 2 + 0.16
            while xx < w / 2 - 0.12:
                kind = b.pick(kinds)
                rr = b.r(0.09, 0.15) * size
                hh = min(rr * b.r(1.6, 2.6), gap) if kind != "bowl" else rr * 0.8
                if b.chance(fill):
                    pot(b, xx, b.r(-0.05, 0.05), zz, kind=kind, r=rr, h=hh, col=b.pick(cols), lod=lod, mat=mat)
                xx += rr * 2 + b.r(0.03, 0.09)


# ---------------------------------------------------------------------------------------- chimneys and vents
def round_stack(b, x=0.0, y=0.0, z=0.0, h=5.0, r0=0.5, r1=0.36, seg=10, mat="brick", col=None, bands=(0.4, 0.75), head=True, smoke=True,
                strength=1.0, lod=0):
    """A round, tapering chimney rising h from (x, y, z), with a corbelled head and iron bands."""
    with b.at(x, y, z):
        b.revolve([(r0, 0.0), (r1, h)], mat, col=col, seg=seg, lod=lod)
        if head:
            b.revolve([(r1 - 0.01, h - 0.46), (r1 + 0.07, h - 0.4), (r1 + 0.07, h - 0.28), (r1 + 0.13, h - 0.2), (r1 + 0.13, h), (r1 - 0.1, h)], mat,
                      col=shade(col, 0.9), seg=seg, lod=1)
        b.disc(max(r1 - 0.1, 0.05), "paint", col=SOOT, seg=seg, z=h - 0.03, lod=1)
        with b.detail(2):
            for t in bands:
                rr = lerp(r0, r1, t) + 0.015
                b.revolve([(rr, h * t - 0.04), (rr, h * t + 0.04)], "metal", col="iron", seg=seg)
        if smoke:
            b.smoke(0, 0, h + 0.3, strength)


def great_chimney(b, x=0.0, y=0.0, z=0.0, h=6.0, w=1.3, d=1.1, shoulder=2.2, neck=0.62, mat="brick", col=None, pots=2, smoke=True,
                  strength=1.3, pot_col="#c9764a", weather="ashlar", weather_col="stone"):
    """A massive stack rising h from (x, y, z): a broad base that steps in at a weathered shoulder to a tall,
    slightly tapering shaft with a corbelled head and pots."""
    wn, dn = w * neck, d * neck
    with b.at(x, y, z):
        b.box(w, d, shoulder, mat, col=col, lod=0, top=False)
        b.box(w, d, 0.55, mat, col=col, z=shoulder, tx=neck, ty=neck, lod=0, top=False)
        with b.detail(1):
            b.box(w + 0.1, d + 0.1, 0.09, weather, col=weather_col, z=shoulder - 0.045, bottom=True)
        hs = h - shoulder - 0.55 - 0.4
        b.box(wn, dn, hs, mat, col=col, z=shoulder + 0.55, taper=0.93, lod=0, top=False)
        zt = shoulder + 0.55 + hs
        wt, dt = wn * 0.93, dn * 0.93
        b.box(wt + 0.12, dt + 0.12, 0.13, mat, col=shade(col, 0.92), z=zt, lod=0, bottom=True)
        b.box(wt + 0.26, dt + 0.26, 0.13, mat, col=shade(col, 0.86), z=zt + 0.13, lod=0, bottom=True)
        b.box(wt + 0.1, dt + 0.1, 0.14, mat, col=col, z=zt + 0.26, lod=0, cap="paint", capcol=SOOT)
        top = zt + 0.4
        with b.detail(1):
            for i in range(pots):
                px = (i - (pots - 1) / 2) * min(0.34, wt / max(pots, 1))
                with b.at(px, 0, top):
                    b.revolve([(0.12, 0.0), (0.095, 0.34), (0.115, 0.39), (0.085, 0.41)], "paint", col=pot_col, seg=8)
        if smoke:
            b.smoke(0, 0, top + 0.5, strength)
    return top


def steam_vent(b, x=0.0, y=0.0, z=0.0, h=0.9, r=0.2, col="white", hat="copper", smoke=True, strength=0.6, mat="plaster", lod=1):
    """A short round vent with a little conical hat on three stays: for steam (it breathes like a chimney)."""
    with b.at(x, y, z):
        b.revolve([(r * 1.1, 0.0), (r, h), (r - 0.05, h)], mat, col=col, seg=8, lod=0)
        with b.detail(lod):
            b.disc(r - 0.05, "paint", col=SOOT, seg=8, z=h - 0.02)
            for k in range(3):
                a = 2 * math.pi * k / 3
                b.beam((r * 0.8 * math.sin(a), r * 0.8 * math.cos(a), h), (r * 0.8 * math.sin(a), r * 0.8 * math.cos(a), h + 0.2), w=0.025, mat="metal", col="iron", caps=False)
            b.revolve([(r * 1.6, h + 0.18), (0.0, h + 0.42)], "metal", col=hat, seg=8)
            b.disc(r * 1.6, "metal", col=shade(hat, 0.7), seg=8, z=h + 0.18, down=True)
        if smoke:
            b.smoke(0, 0, h + 0.5, strength)


def ridge_vent(b, x=0.0, y=0.0, z=0.0, L=2.6, w=1.2, h=0.95, drop=0.6, ridge="x", roof="slate", roof_col=None, pitch=38.0, col="greyoak",
               frame="darkoak", core="#4a4038", lod=0):
    """A louvred ventilator astride a roof ridge at (x, y, z = the height of the ridge): L long along the ridge, w
    across it, its louvred walls h high above the ridge and running `drop` down the slopes on either side."""
    with b.at(x, y, z, rz=0 if ridge == "x" else 90):
        b.box(L - 0.08, w - 0.08, h + drop, "planks", col=core, z=-drop, lod=lod)
        with b.detail(1):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    b.beam((sx * (L / 2 - 0.05), sy * (w / 2 - 0.05), -drop), (sx * (L / 2 - 0.05), sy * (w / 2 - 0.05), h), w=0.12, mat="timber", col=frame, caps=False)
            for sy in (-1, 1):
                b.beam((-L / 2, sy * (w / 2 - 0.04), h - 0.05), (L / 2, sy * (w / 2 - 0.04), h - 0.05), w=0.1, mat="timber", col=frame, caps=False)
            slats(b, L - 0.22, h + drop - 0.2, y=-w / 2 + 0.02, z=-drop + 0.12, face=0, col=col, pitch=0.24, board=0.2)
            slats(b, L - 0.22, h + drop - 0.2, y=w / 2 - 0.02, z=-drop + 0.12, face=180, col=col, pitch=0.24, board=0.2)
            slats(b, w - 0.22, h - 0.1, x=L / 2 - 0.02, z=0.04, face=90, col=col, pitch=0.24, board=0.2)
            slats(b, w - 0.22, h - 0.1, x=-L / 2 + 0.02, z=0.04, face=270, col=col, pitch=0.24, board=0.2)
        rise = (w / 2) * math.tan(rad(pitch))
        b.gable_roof(L, w, pitch=pitch, mat=roof, col=roof_col, z=h, ridge="x", eave=0.2, verge=0.22, course=0.3, thick=0.08, lod=lod, barge_col=frame)
        for sx in (-1, 1):
            t = [(sx * (L / 2 - 0.04), -w / 2 * sx, h), (sx * (L / 2 - 0.04), w / 2 * sx, h), (sx * (L / 2 - 0.04), 0, h + rise)]
            b.face(t, "planks", col=core, lod=lod)


# ---------------------------------------------------------------------------------------- hoists and lifting
def hoist(b, x=0.0, y=0.0, z=0.0, out=1.2, face=0.0, rope=2.6, load="sack", brace=True, col="darkoak", lod=1, back=0.3):
    """A hoist: a beam jutting `out` from a wall at (x, y, z) toward compass `face`, a pulley at its end and a rope
    hanging `rope` metres from it with a load: 'sack', 'barrel', 'crate', 'bale', 'bucket', 'hook' or None."""
    with b.at(x, y, z, rz=face):
        with b.detail(lod):
            b.beam((0, back, 0), (0, -out, 0), w=0.16, h=0.2, mat="timber", col=col)
            if brace:
                b.beam((0, 0.0, -0.8), (0, -out * 0.7, -0.1), w=0.1, mat="timber", col=col)
        py = -out + 0.14
        with b.detail(2):
            with b.at(0, py, -0.25, ry=90):
                b.revolve([(0.0, -0.03), (0.13, -0.03), (0.13, 0.03), (0.0, 0.03)], "metal", col="iron", seg=8)
            b.beam((0, py, -0.1), (0, py, -0.25), w=0.03, mat="metal", col="iron", caps=False)
        if rope > 0:
            with b.detail(lod):
                b.tube((0, py, -0.3), (0, py, -rope), r=0.02, mat="cloth", col=ROPE, n=4)
            zz = -rope
            if load == "sack":
                with b.detail(lod):
                    b.blob(0.3, 0.26, 0.4, mat="cloth", col="#e2d6b6", x=0, y=py, z=zz - 0.34, seg=6, rings=3, rough=0.1)
            elif load == "barrel":
                barrel(b, 0, py, zz - 0.72, r=0.27, h=0.72, lod=lod)
            elif load == "bale":
                with b.detail(lod):
                    b.box(0.6, 0.45, 0.45, "cloth", col="#d9c9a3", x=0, y=py, z=zz - 0.45, bottom=True)
                    b.beam((0, py - 0.24, zz - 0.22), (0, py + 0.24, zz - 0.22), w=0.63, h=0.03, mat="cloth", col=ROPE, caps=False)
            elif load == "crate":
                with b.detail(lod):
                    b.box(0.55, 0.55, 0.5, "planks", col="#d8c3a0", x=0, y=py, z=zz - 0.5, bottom=True)
            elif load == "bucket":
                bucket(b, 0, py, zz - 0.42, lod=lod)
            elif load == "hook":
                with b.detail(2):
                    b.beam((0, py, zz), (0, py, zz - 0.14), w=0.03, mat="metal", col="iron", caps=False)
                    b.beam((0, py, zz - 0.14), (0.07, py, zz - 0.2), w=0.03, mat="metal", col="iron", caps=False)


# ---------------------------------------------------------------------------------------- roof-top things
def cupola(b, x=0.0, y=0.0, z=0.0, w=1.3, base=0.8, stage=1.25, roof_h=1.5, drop=0.7, roof="shingle", roof_col=None, col="ivory", post="darkoak",
           base_mat="planks", bell=True, vane=True, cap="ogee", rail=True):
    """A square bell cupola astride a ridge at (x, y, z = the height of the ridge): a boarded base (running `drop`
    down the slopes), an open stage on four posts with the bell hung in it, and a little roof with a weathervane."""
    hw = w / 2
    with b.at(x, y, z):
        b.box(w, w, base + drop, base_mat, col=col, z=-drop, lod=0, cap="planks", capcol="greyoak")
        with b.detail(1):
            b.box(w + 0.16, w + 0.16, 0.08, "planks", col=shade(col, 0.9), z=base - 0.04, bottom=True)
        zs = base + 0.04
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.beam((sx * (hw - 0.08), sy * (hw - 0.08), zs), (sx * (hw - 0.08), sy * (hw - 0.08), zs + stage), w=0.13, mat="timber", col=post, lod=0, caps=False)
        with b.detail(1):
            for sx in (-1, 1):
                b.beam((sx * (hw - 0.08), -hw, zs + stage - 0.06), (sx * (hw - 0.08), hw, zs + stage - 0.06), w=0.12, mat="timber", col=post)
                b.beam((-hw, sx * (hw - 0.08), zs + stage - 0.06), (hw, sx * (hw - 0.08), zs + stage - 0.06), w=0.12, mat="timber", col=post)
        with b.detail(2):
            for k in range(4):
                with b.at(rz=90 * k):
                    for sx in (-1, 1):
                        b.beam((sx * (hw - 0.1), -hw + 0.08, zs + stage - 0.5), (sx * (hw - 0.42), -hw + 0.08, zs + stage - 0.1), w=0.07, mat="timber", col=post, caps=False)
                    if rail:
                        b.beam((-hw + 0.1, -hw + 0.08, zs + 0.34), (hw - 0.1, -hw + 0.08, zs + 0.34), w=0.06, mat="timber", col=post, caps=False)
        b.quad((-hw, hw, zs + stage), (hw, hw, zs + stage), (hw, -hw, zs + stage), (-hw, -hw, zs + stage), "planks", col="darkoak", lod=1)
        if bell:
            P.bell(b, 0, 0, zs + stage - 0.12, r=min(0.3, w * 0.24), beam=w - 0.2)
        rr = hw * math.sqrt(2)
        with b.at(z=zs + stage, rz=45):
            if cap == "ogee":
                sec = [(rr + 0.24, -0.06), (rr * 0.78, 0.2), (rr * 0.42, 0.52), (rr * 0.26, roof_h * 0.7), (0.0, roof_h)]
                b.cone_roof(rr, roof_h, mat=roof, col=roof_col, seg=4, smooth=False, section=sec, course=0.28, finial=not vane)
            else:
                b.cone_roof(rr, roof_h, mat=roof, col=roof_col, seg=4, smooth=False, eave=0.24, flare=0.5, course=0.28, finial=not vane)
        if vane:
            P.weathervane(b, 0, 0, zs + stage + roof_h - 0.1, h=1.1)
    return zs + stage + roof_h


def dome(b, r, h, x=0.0, y=0.0, z=0.0, mat="plaster", col="white", seg=16, steps=5, drum=0.0, drum_out=0.06, lod=0, finial="brass",
         eyes=0, eye_r=0.11, eye_at=0.55, eye_col="#9fd0d8"):
    """A low dome of radius r rising h from the top of a drum `drum` high standing on (x, y, z). eyes = how many
    little round glass lights are set in a ring part-way up (as a bath-house has); finial = metal of the knob."""
    with b.at(x, y, z):
        if drum > 0:
            b.revolve([(r + drum_out, 0.0), (r + drum_out, drum), (r, drum)], mat, col=shade(col, 0.96), seg=seg, lod=lod, smooth=False)
        pts = [(r * math.cos(math.pi / 2 * i / steps), drum + h * math.sin(math.pi / 2 * i / steps)) for i in range(steps + 1)]
        pts[-1] = (0.0, drum + h)
        b.revolve(pts, mat, col=col, seg=seg, lod=lod)
        if eyes:
            t = eye_at * math.pi / 2
            rr, zz = r * math.cos(t), drum + h * math.sin(t)
            phi = math.degrees(math.atan2(math.sin(t) / h, math.cos(t) / r))
            with b.detail(2):
                for k in range(eyes):
                    with b.at(rz=360.0 * (k + 0.5) / eyes):
                        with b.at(0, -rr, zz, rx=90 - phi):
                            b.disc(eye_r, "glass", col=eye_col, seg=8, z=0.035)
                            b.revolve([(eye_r + 0.035, 0.0), (eye_r + 0.035, 0.05), (eye_r, 0.05)], mat, col=shade(col, 0.9), seg=8)
        if finial:
            with b.detail(1):
                zt = drum + h
                b.revolve([(0.1, zt - 0.06), (0.06, zt + 0.08), (0.13, zt + 0.2), (0.13, zt + 0.3), (0.04, zt + 0.42), (0.03, zt + 0.8), (0.0, zt + 0.92)], "metal", col=finial, seg=8)


# ---------------------------------------------------------------------------------------- masonry
def arcade(b, w, h, n=3, t=0.32, pier=0.4, arch=None, top=0.5, mat="plaster", col="white", x=0.0, y=0.0, z=0.0, face=0.0, lod=0, sill=0.0,
           caps="ashlar", cap_col="stone"):
    """A free-standing arcaded wall you can see through: w long, h high, t thick, with n round-headed arches between
    piers. Its left end (seen from outside) stands at (x, y, z) and its front looks toward compass `face`.
    arch = height of the curved heads (default: half-round); top = wall left above the crown of the arches."""
    bay = (w - pier) / n
    ow = bay - pier
    arch = ow / 2 if arch is None else arch
    oh = h - top - sill
    with b.at(x, y, z, rz=face):
        f = b.wall(w, h, mat, col, depth=t / 2, lod=lod)
        with b.at(w, t, 0, rz=180):
            k = b.wall(w, h, mat, col, depth=t / 2, lod=lod)
        for i in range(n):
            u = pier + ow / 2 + i * bay
            f.opening(u, sill, ow, oh, arch=arch, pane=None)
            k.opening(w - u, sill, ow, oh, arch=arch, pane=None)
        f.emit()
        k.emit()
        b.quad((0, 0, h), (w, 0, h), (w, t, h), (0, t, h), mat, col=col, lod=lod)
        b.quad((0, t, 0), (0, 0, 0), (0, 0, h), (0, t, h), mat, col=col, lod=lod)
        b.quad((w, 0, 0), (w, t, 0), (w, t, h), (w, 0, h), mat, col=col, lod=lod)
        if caps:
            with b.detail(2):
                for i in range(n + 1):
                    u = pier / 2 + i * bay
                    b.box(pier + 0.1, t + 0.1, 0.1, caps, col=cap_col, x=u, y=t / 2, z=sill + oh - arch - 0.1, bottom=True)
                    b.box(pier + 0.12, t + 0.12, 0.16, caps, col=cap_col, x=u, y=t / 2, z=sill)
    return ow


def low_wall(b, p0, p1, h=1.0, t=0.34, mat="masonry", col="warm", coping="ashlar", coping_col="stone", skirt=3.0, lod=0, rough=True):
    """A free-standing yard wall from p0 to p1 ((x, y) pairs: its centre line), h high and t thick, with coping
    stones and the hidden foundation that keeps it grounded on a slope."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    with b.at(p0[0], p0[1], 0, rz=ang):
        b.box(L, t, h + skirt, mat, col=col, x=L / 2, z=-skirt, lod=lod)
        if coping:
            n = max(1, int(L / 0.55))
            if rough:
                with b.detail(2):
                    for i in range(n):
                        b.stone(L / n * 0.96, t + 0.1, 0.12, mat=coping, col=coping_col, x=L * (i + 0.5) / n, z=h - 0.01, jitter=0.08, lod=2)
            with b.detail(1):
                b.box(L, t + 0.06, 0.05, coping, col=coping_col, x=L / 2, z=h - 0.01, bottom=True)


def gate(b, p0, p1, h=1.15, col="green", ajar=18.0, posts="ashlar", post_col="stone", post_h=None, lod=1):
    """A boarded yard gate hung between p0 and p1 ((x, y) pairs), a little open, with gate posts."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    ph = post_h or h + 0.35
    with b.at(p0[0], p0[1], 0, rz=ang):
        if posts:
            for xx in (0.0, L):
                b.box(0.34, 0.34, ph + 3.0, posts, col=post_col, x=xx, z=-3.0, lod=0, top=False)
                with b.detail(1):
                    b.box(0.44, 0.44, 0.1, posts, col=post_col, x=xx, z=ph, bottom=True)
                    b.box(0.34, 0.34, 0.16, posts, col=post_col, x=xx, z=ph + 0.1, taper=0.3)
        with b.at(0.2, 0, 0.08, rz=-ajar):
            with b.detail(lod):
                gw = L - 0.4
                b.box(gw, 0.05, h, "planks", col=col, x=gw / 2, y=0, bottom=True)
            with b.detail(2):
                for zz in (h * 0.2, h * 0.8):
                    for sy in (-1, 1):
                        b.beam((0.02, sy * 0.035, zz), (gw - 0.02, sy * 0.035, zz), w=0.02, h=0.08, mat="planks", col=shade(col, 0.75), up=(0, 0, 1), caps=False)
                b.beam((0.02, -0.035, h * 0.2), (gw - 0.02, -0.035, h * 0.8), w=0.02, h=0.07, mat="planks", col=shade(col, 0.75), up=(0, 0, 1), caps=False)


def yard(b, x0, y0, x1, y1, mat="cobble", col=None, h=0.1, skirt=3.0, edge="masonry", edge_col="warm", lod=0):
    """A paved yard: a low terrace of setts or flags from (x0, y0) to (x1, y1), with the hidden foundation that
    keeps it grounded on a slope. Stand the yard's things on z = h."""
    b.box(x1 - x0, y1 - y0, h + skirt, edge, col=edge_col, x=(x0 + x1) / 2, y=(y0 + y1) / 2, z=-skirt, cap=mat, capcol=C(col), lod=lod)
    return h


def chequer(b, x0, y0, x1, y1, z=0.0, n=6, cols=("!#8fcfae", "!#f2ead8"), lod=2):
    """Glazed floor tiles laid chequerwise over (x0, y0)..(x1, y1) at height z (lay them on a floor: they are thin)."""
    w, d = x1 - x0, y1 - y0
    m = max(1, round(n * d / w))
    b.quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), "paint", col=cols[1], lod=1)
    with b.detail(lod):
        for i in range(n):
            for j in range(m):
                if (i + j) % 2:
                    continue
                xa, xb = x0 + w * i / n, x0 + w * (i + 1) / n
                ya, yb = y0 + d * j / m, y0 + d * (j + 1) / m
                b.quad((xa, ya, z + 0.006), (xb, ya, z + 0.006), (xb, yb, z + 0.006), (xa, yb, z + 0.006), "paint", col=cols[0])


def frieze(s, z, h=0.28, u0=0.0, u1=None, size=0.28, cols=("!#2f8f8f", "!#f2ead8", "!#8fcfae"), proud=0.012, lod=2, border="!#f2ead8"):
    """A band of glazed tiles along a flat wall between u0 and u1 at height z: squares of alternating colours."""
    b = s.b
    u1 = s.w if u1 is None else u1
    n = max(1, round((u1 - u0) / size))

    def deco():
        b.quad((u0, -proud * 0.6, z - 0.03), (u1, -proud * 0.6, z - 0.03), (u1, -proud * 0.6, z + h + 0.03), (u0, -proud * 0.6, z + h + 0.03), "paint", col=border, lod=1)
        with b.detail(lod):
            for i in range(n):
                ua, ub = u0 + (u1 - u0) * i / n + 0.015, u0 + (u1 - u0) * (i + 1) / n - 0.015
                c = cols[i % len(cols)]
                if i % 2 == 0:
                    b.quad((ua, -proud, z), (ub, -proud, z), (ub, -proud, z + h), (ua, -proud, z + h), "paint", col=c)
                else:
                    um = (ua + ub) / 2
                    b.quad((um, -proud, z), (ub, -proud, z + h / 2), (um, -proud, z + h), (ua, -proud, z + h / 2), "paint", col=c)

    s.add(deco)


# ---------------------------------------------------------------------------------------- the smith's gear
def anvil(b, x=0.0, y=0.0, z=0.0, rz=0.0, lod=1):
    """An anvil on its oak stump (the horn toward local +x)."""
    with b.at(x, y, z, rz=rz):
        with b.detail(lod):
            b.revolve([(0.3, 0.0), (0.27, 0.55)], "timber", col="#b59a80", seg=8)
            b.disc(0.27, "planks", col="#cbb089", seg=8, z=0.55)
            b.box(0.34, 0.24, 0.1, "metal", col="iron", z=0.55)
            b.box(0.2, 0.16, 0.14, "metal", col="iron", z=0.65)
            b.box(0.52, 0.2, 0.11, "metal", col="iron", x=-0.02, z=0.79)
            b.tube((0.24, 0, 0.845), (0.52, 0, 0.87), r=0.055, r1=0.012, mat="metal", col="iron", n=6)
        with b.detail(2):
            b.beam((-0.12, -0.02, 0.92), (0.2, -0.3, 0.93), w=0.03, mat="planks", col="greyoak")
            b.box(0.09, 0.14, 0.08, "metal", col="iron", x=-0.12, y=-0.02, z=0.9, bottom=True)
            b.revolve([(0.31, 0.2), (0.31, 0.26)], "metal", col="iron", seg=8)


def trough(b, x=0.0, y=0.0, z=0.0, rz=0.0, w=1.3, d=0.55, h=0.5, mat="masonry", col="grey", lod=1):
    """A stone quenching (or drinking) trough full of water, lying along the local x axis."""
    with b.at(x, y, z, rz=rz):
        with b.detail(lod):
            b.box(w, d, h, mat, col=col, taper=0.96)
            b.quad((-w / 2 + 0.1, -d / 2 + 0.1, h + 0.008), (w / 2 - 0.1, -d / 2 + 0.1, h + 0.008), (w / 2 - 0.1, d / 2 - 0.1, h + 0.008), (-w / 2 + 0.1, d / 2 - 0.1, h + 0.008), "water")


def grindstone(b, x=0.0, y=0.0, z=0.0, rz=0.0, r=0.34, lod=2):
    """A grindstone in its wooden frame with a crank (the stone turning about the local x axis)."""
    with b.at(x, y, z, rz=rz):
        with b.detail(lod):
            for sx in (-1, 1):
                b.beam((sx * 0.16, -0.36, 0), (sx * 0.16, -0.1, 0.62), w=0.06, mat="timber", col="greyoak")
                b.beam((sx * 0.16, 0.36, 0), (sx * 0.16, 0.1, 0.62), w=0.06, mat="timber", col="greyoak")
                b.beam((sx * 0.16, -0.16, 0.6), (sx * 0.16, 0.16, 0.6), w=0.06, mat="timber", col="greyoak")
            with b.at(-0.06, 0, 0.62, ry=90):
                b.revolve([(0.0, 0.0), (r, 0.0), (r, 0.12), (0.0, 0.12)], "ashlar", col="grey", seg=10)
            b.beam((-0.24, 0, 0.62), (0.3, 0, 0.62), w=0.03, mat="metal", col="iron", caps=False)
            b.beam((0.3, 0, 0.62), (0.3, 0.1, 0.78), w=0.03, mat="metal", col="iron", caps=False)


def bellows(b, x=0.0, y=0.0, z=0.0, rz=0.0, L=1.3, lod=2):
    """Forge bellows on a trestle, the nozzle toward local +x."""
    with b.at(x, y, z, rz=rz):
        with b.detail(lod):
            for sx in (-0.4, 0.25):
                b.beam((sx, -0.25, 0), (sx, 0, 0.75), w=0.06, mat="timber", col="darkoak")
                b.beam((sx, 0.25, 0), (sx, 0, 0.75), w=0.06, mat="timber", col="darkoak")
            pts = lambda zz, k: [(-L / 2, -0.3 * k, zz), (L * 0.2, -0.3 * k, zz), (L / 2, -0.03, zz), (L / 2, 0.03, zz), (L * 0.2, 0.3 * k, zz), (-L / 2, 0.3 * k, zz)]
            lo, hi = pts(0.78, 1.0), [(p[0], p[1], 0.78 + 0.34 * (1 - (p[0] + L / 2) / L)) for p in pts(0.0, 1.0)]
            b.face(hi, "planks", col="#9a6a48")
            b.face(list(reversed(lo)), "planks", col="#8a5c3e")
            for i in range(6):
                j = (i + 1) % 6
                b.face([lo[i], lo[j], hi[j], hi[i]], "cloth", col="#6b4a35")
            b.tube((L / 2, 0, 0.8), (L / 2 + 0.35, 0, 0.74), r=0.04, r1=0.025, mat="metal", col="iron", n=5)
            b.beam((-L / 2, 0, 1.12), (-L / 2 - 0.45, 0, 1.3), w=0.04, mat="timber", col="greyoak")


def horseshoes(s, pos, z, n=5, gap=0.2, r=0.07, lod=2):
    """A row of horseshoes nailed along a wall."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            with b.detail(lod):
                for i in range(n):
                    with b.at((i - (n - 1) / 2) * gap, -0.015, 0, rx=90):
                        b.revolve([(r, 0.0), (r + 0.03, 0.0), (r + 0.03, 0.02), (r, 0.02)], "metal", col="iron", seg=8, a0=-140, a1=140)

    s.add(deco)


def ingots(b, x=0.0, y=0.0, z=0.0, n=3, rows=3, rz=0.0, col="lead", lod=2):
    """Pigs of metal stacked crosswise."""
    with b.at(x, y, z, rz=rz):
        with b.detail(lod):
            for k in range(rows):
                with b.at(z=0.1 * k, rz=90 * (k % 2)):
                    for i in range(n - (k // 2)):
                        b.box(0.14, 0.5, 0.1, "metal", col=shade(col, b.r(0.85, 1.1)), x=(i - (n - (k // 2) - 1) / 2) * 0.17, taper=0.85, bottom=True)


def coal_heap(b, x=0.0, y=0.0, z=0.0, r=0.6, h=0.4, lod=2):
    with b.detail(lod):
        b.blob(r, r * 0.8, h, mat="paint", col="#2a2826", x=x, y=y, z=z + h * 0.35, seg=7, rings=3, rough=0.3, bottom=False)


def hearth(b, x=0.0, y=0.0, z=0.0, rz=0.0, w=1.6, d=1.2, h=0.85, mat="brick", col=None, hood=True, hood_h=1.5, hood_top=(0.9, 0.7), lod=0):
    """A raised forge hearth with glowing coals, and over it a brick hood that gathers to the flue."""
    with b.at(x, y, z, rz=rz):
        b.box(w, d, h, mat, col=col, lod=lod, cap="masonry", capcol="dark")
        with b.detail(1):
            b.blob(w * 0.26, d * 0.26, 0.1, mat="paint", col="#2a2826", z=h + 0.03, seg=7, rings=2, rough=0.3, bottom=False)
            b.blob(w * 0.17, d * 0.17, 0.09, mat="glow", col="#ffb060", z=h + 0.07, seg=6, rings=2, rough=0.3, bottom=False)
        b.lamp(0, 0, h + 0.3, 1.2)
        if hood:
            z0 = h + 0.95
            tw, td = hood_top
            hw, hd = w / 2, d / 2
            B = [(-hw, -hd, z0), (hw, -hd, z0), (hw, hd, z0), (-hw, hd, z0)]
            T = [(-tw / 2, hd - td, z0 + hood_h), (tw / 2, hd - td, z0 + hood_h), (tw / 2, hd, z0 + hood_h), (-tw / 2, hd, z0 + hood_h)]
            for i in range(4):
                j = (i + 1) % 4
                b.quad(B[i], B[j], T[j], T[i], mat, col=col, lod=lod)
            b.quad(B[3], B[2], B[1], B[0], "paint", col=SOOT, lod=lod)
            with b.detail(1):
                b.beam((-hw - 0.03, -hd - 0.02, z0 + 0.06), (hw + 0.03, -hd - 0.02, z0 + 0.06), w=0.1, h=0.16, mat="timber", col="blackoak")
                for sx in (-1, 1):
                    b.beam((sx * (hw - 0.05), -hd + 0.05, h), (sx * (hw - 0.05), -hd + 0.05, z0), w=0.1, mat="metal", col="iron", caps=False)


def tool_rack(s, pos, z, w=1.4, n=6, lod=2):
    """A rail of smith's tools (tongs, hammers) hung on a wall."""
    b = s.b
    u = s.U(pos)

    def deco():
        with s.onu(u, z):
            with b.detail(lod):
                b.beam((-w / 2, -0.04, 0), (w / 2, -0.04, 0), w=0.05, h=0.08, mat="timber", col="darkoak", up=(0, 0, 1))
                for i in range(n):
                    xx = -w / 2 + w * (i + 0.5) / n
                    L = b.r(0.4, 0.7)
                    if i % 2:
                        b.beam((xx - 0.02, -0.07, 0), (xx - 0.05, -0.07, -L), w=0.02, mat="metal", col="iron", caps=False)
                        b.beam((xx + 0.02, -0.07, 0), (xx + 0.05, -0.07, -L), w=0.02, mat="metal", col="iron", caps=False)
                    else:
                        b.beam((xx, -0.07, 0.02), (xx, -0.07, -L), w=0.03, mat="planks", col="greyoak", caps=False)
                        b.box(0.14, 0.07, 0.08, "metal", col="iron", x=xx, y=-0.07, z=-L - 0.04, bottom=True)

    s.add(deco)


# ---------------------------------------------------------------------------------------- the chandler's gear
def candle_rack(b, x=0.0, y=0.0, z=0.0, rz=0.0, w=1.3, h=1.6, rods=3, per=7, col="#f2e6c4", lod=2):
    """A dipping rack: rods of candles hanging by their wicks between two posts, along the local x axis."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            for sx in (-1, 1):
                b.beam((sx * w / 2, 0, 0), (sx * w / 2, 0, h), w=0.07, mat="timber", col="darkoak")
                b.beam((sx * w / 2, -0.3, 0.03), (sx * w / 2, 0.3, 0.03), w=0.07, mat="timber", col="darkoak")
            b.beam((-w / 2, 0, h - 0.04), (w / 2, 0, h - 0.04), w=0.06, mat="timber", col="darkoak", caps=False)
        with b.detail(lod):
            for k in range(rods):
                zz = h - 0.16 - k * (h - 0.75) / max(rods, 1)
                yy = (k - (rods - 1) / 2) * 0.17
                b.beam((-w / 2, yy, zz), (w / 2, yy, zz), w=0.028, mat="timber", col="greyoak", caps=False)
                c = shade(col, b.r(0.9, 1.05)) if k % 2 == 0 else C(b.pick(["#f2e6c4", "#e9c46a", "#f0d9a0"]))
                for i in range(per):
                    xx = -w / 2 + w * (i + 0.5) / per
                    L = b.r(0.24, 0.3)
                    b.tube((xx, yy, zz - 0.05), (xx, yy, zz - 0.05 - L), r=0.016, r1=0.024, mat="paint", col=c, n=4)


def soap_table(b, x=0.0, y=0.0, z=0.0, rz=0.0, w=1.2, d=0.5, h=0.75, cols=("#f0e2c0", "#d9c99a", "#c9d6b0", "#e8c4c4"), lod=2):
    """A trestle table stacked with cakes of soap."""
    with b.at(x, y, z, rz=rz):
        with b.detail(1):
            b.box(w, d, 0.05, "planks", col="greyoak", z=h - 0.05, bottom=True)
        with b.detail(lod):
            for sx in (-1, 1):
                b.beam((sx * (w / 2 - 0.15), -d / 2 + 0.04, 0), (sx * (w / 2 - 0.15), 0, h - 0.05), w=0.05, mat="timber", col="darkoak", caps=False)
                b.beam((sx * (w / 2 - 0.15), d / 2 - 0.04, 0), (sx * (w / 2 - 0.15), 0, h - 0.05), w=0.05, mat="timber", col="darkoak", caps=False)
            n = int(w / 0.3)
            for i in range(n):
                c = cols[i % len(cols)]
                xx = -w / 2 + w * (i + 0.5) / n
                for k in range(b.rng.randint(1, 3)):
                    b.box(0.2, 0.3, 0.09, "paint", col=shade(c, b.r(0.9, 1.05)), x=xx + b.r(-0.02, 0.02), y=b.r(-0.03, 0.03), z=h + 0.09 * k, bottom=True)


def cauldron(b, x=0.0, y=0.0, z=0.0, r=0.45, mat="brick", col=None, fill="#d9c99a", lod=1):
    """A boiling copper set in a round brick furnace with a stoke hole (toward local -y)."""
    with b.at(x, y, z):
        b.revolve([(r + 0.18, 0.0), (r + 0.14, 0.7), (r + 0.02, 0.7)], mat, col=col, seg=10, lod=0)
        with b.detail(lod):
            b.revolve([(r + 0.04, 0.68), (r + 0.06, 0.8), (r, 0.8), (r - 0.04, 0.6)], "metal", col="copper", seg=10)
            b.disc(r - 0.02, "glass", col=fill, seg=10, z=0.72)
        with b.detail(2):
            b.box(0.34, 0.06, 0.3, "glow", col="#ffb060", y=-(r + 0.17), z=0.08)
            b.box(0.44, 0.05, 0.4, "metal", col="iron", y=-(r + 0.15), z=0.03)


# ---------------------------------------------------------------------------------------- signs
def _arc(r0, r1, a0, a1, n):
    out = []
    for k in range(n):
        t0, t1 = math.radians(a0 + (a1 - a0) * k / n), math.radians(a0 + (a1 - a0) * (k + 1) / n)
        out.append([(r0 * math.cos(t0), r0 * math.sin(t0)), (r1 * math.cos(t0), r1 * math.sin(t0)), (r1 * math.cos(t1), r1 * math.sin(t1)), (r0 * math.cos(t1), r0 * math.sin(t1))])
    return out


# each emblem is a list of convex outlines, clockwise, in a box about +-0.24
EMBLEMS = {
    "candle": [[(-.05, .06), (.0, .1), (.05, .06), (.05, -.18), (-.05, -.18)], [(0, .25), (.05, .16), (0, .1), (-.05, .16)], [(-.14, -.18), (.14, -.18), (.14, -.23), (-.14, -.23)]],
    "barrel": [[(-.12, .2), (.12, .2), (.19, .07), (.19, -.07), (.12, -.2), (-.12, -.2), (-.19, -.07), (-.19, .07)]],
    "jug": [[(-.07, .2), (.07, .2), (.05, .1), (.15, -.02), (.14, -.14), (.08, -.22), (-.08, -.22), (-.14, -.14), (-.15, -.02), (-.05, .1)],
            [(.12, .1), (.24, .1), (.24, .05), (.12, .05)], [(.19, .05), (.24, .05), (.24, -.08), (.19, -.08)], [(.12, -.08), (.24, -.08), (.24, -.13), (.12, -.13)]],
    "horseshoe": _arc(0.12, 0.21, 235, -55, 8),
    "hammer": [[(-.22, -.17), (.03, .1), (.1, .04), (-.15, -.23)], [(-.1, .17), (.14, -.06), (.25, .06), (.01, .29)]],
    "shuttle": [[(-.25, 0), (-.1, .075), (.1, .075), (.25, 0), (.1, -.075), (-.1, -.075)]],
    "saw": [[(-.25, .03), (.1, .1), (.1, -.08), (-.25, -.03)], [(.1, .13), (.24, .13), (.24, -.12), (.1, -.12)]],
    "bottle": [[(-.04, .25), (.04, .25), (.04, .1), (.11, 0), (.11, -.23), (-.11, -.23), (-.11, 0), (-.04, .1)]],
    "drop": [[(0, .25), (.1, .02), (.14, -.1), (.08, -.2), (-.08, -.2), (-.14, -.1), (-.1, .02)]],
    "anvil": [[(-.22, .15), (.2, .15), (.25, .09), (.06, .03), (-.06, .03), (-.14, .06)], [(-.06, .03), (.06, .03), (.06, -.1), (-.06, -.1)],
              [(-.06, -.1), (.06, -.1), (.16, -.2), (-.16, -.2)]],
    "wheel": _arc(0.15, 0.22, 360, 0, 10) + [[(-.15, .02), (.15, .02), (.15, -.02), (-.15, -.02)], [(-.02, .15), (.02, .15), (.02, -.15), (-.02, -.15)]],
    "mug": [[(-.14, .16), (.1, .16), (.1, -.18), (-.14, -.18)], [(.1, .1), (.21, .1), (.21, .05), (.1, .05)], [(.16, .05), (.21, .05), (.21, -.07), (.16, -.07)],
            [(.1, -.07), (.21, -.07), (.21, -.12), (.1, -.12)]],
    "book": [[(-.2, .14), (0, .1), (0, -.18), (-.2, -.14)], [(0, .1), (.2, .14), (.2, -.14), (0, -.18)]],
    "bell": [[(-.04, .2), (.04, .2), (.12, .06), (.14, -.1), (.2, -.16), (-.2, -.16), (-.14, -.1), (-.12, .06)]],
}


def sign(s, pos, z, emblem="barrel", col="mustard", board="ivory", out=0.75, w=0.62, h=0.5, shape="board"):
    """A hanging craft sign on an iron bracket, like parts.sign but with the craft quarter's emblems: 'candle',
    'barrel', 'jug', 'horseshoe', 'hammer', 'shuttle', 'saw', 'bottle', 'drop', 'anvil', 'wheel', 'mug', 'book',
    'bell' (or pass your own list of convex clockwise outlines). shape = 'board', 'round' or 'shield'."""
    b = s.b
    u = s.U(pos)
    polys = EMBLEMS.get(emblem, EMBLEMS["barrel"]) if isinstance(emblem, str) else emblem

    def deco():
        with s.onu(u, z):
            cy, cz = -out * 0.55, -h / 2 - 0.08
            with b.detail(1):
                b.beam((0, -0.01, 0.06), (0, -out - 0.05, 0.06), w=0.03, mat="metal", col="iron", caps=False)
                b.beam((0, -0.01, -0.3), (0, -out * 0.6, 0.04), w=0.025, mat="metal", col="iron", caps=False)
                if shape == "round":
                    with b.at(-0.0225, cy, cz, ry=90):
                        rr = min(w, h) / 2
                        b.revolve([(rr, 0.0), (rr, 0.045)], "paint", col=shade(board, 0.8), seg=12)
                        b.disc(rr, "paint", col=board, seg=12, z=0.045)
                        b.disc(rr, "paint", col=board, seg=12, z=0.0, down=True)
                elif shape == "shield":
                    for sx in (-1, 1):
                        pts = [(sx * 0.0225, -w / 2, h / 2), (sx * 0.0225, w / 2, h / 2), (sx * 0.0225, w / 2, -h * 0.1), (sx * 0.0225, 0, -h / 2), (sx * 0.0225, -w / 2, -h * 0.1)]
                        pts = [(p[0], cy + p[1], cz + p[2]) for p in pts]
                        b.face(pts if sx < 0 else list(reversed(pts)), "paint", col=board)
                else:
                    with b.at(0, cy, cz - h / 2):
                        b.box(0.045, w, h, "paint", col=board, bottom=True)
            with b.detail(2):
                for sx in (-1, 1):
                    for poly in polys:
                        mx, mz = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
                        cen = (sx * 0.03, cy - mx * sx, cz + mz)
                        ring = [(sx * 0.03, cy - px * sx, cz + pz) for px, pz in poly]
                        for i in range(len(ring)):
                            b.tri(cen, ring[i], ring[(i + 1) % len(ring)], "paint", col=col)
                for yy in (cy - w * 0.35, cy + w * 0.35):
                    b.beam((0, yy, 0.05), (0, yy, cz + h / 2 - 0.02), w=0.015, mat="metal", col="iron", caps=False)

    s.add(deco)


def hanging_sign(b, x=0.0, y=0.0, z=0.0, emblem="horseshoe", col="black", board="ivory", face=0.0, w=0.62, h=0.52, drop=0.22):
    """A sign board hung by two chains under a beam: its top edge `drop` below (x, y, z), facing compass `face`
    (and painted on the back as well). emblem as for sign()."""
    polys = EMBLEMS.get(emblem, EMBLEMS["barrel"]) if isinstance(emblem, str) else emblem
    with b.at(x, y, z, rz=face):
        cz = -drop - h / 2
        with b.detail(1):
            b.box(w, 0.045, h, "paint", col=board, z=cz - h / 2, bottom=True)
        with b.detail(2):
            for sx in (-1, 1):
                b.beam((sx * w * 0.36, 0, 0), (sx * w * 0.36, 0, -drop), w=0.015, mat="metal", col="iron", caps=False)
            for sy in (-1, 1):
                for poly in polys:
                    pts = [(-sy * px, sy * 0.03, cz + pz) for px, pz in poly]
                    cen = (sum(p[0] for p in pts) / len(pts), sy * 0.03, sum(p[2] for p in pts) / len(pts))
                    for i in range(len(pts)):
                        b.tri(cen, pts[(i + 1) % len(pts)], pts[i], "paint", col=col)
