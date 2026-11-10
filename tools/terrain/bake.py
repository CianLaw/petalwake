#!/usr/bin/env python3
"""
Petalwake terrain bake.

Builds the island heightfield (meadow plateau + stratified sea cliffs + fjord + mountain +
lagoon), runs droplet erosion, carves the river, then bakes the lookup maps the game needs:

  assets/terrain/height.u16   uint16 heights, N x N, row-major (row = z, north first)
  assets/terrain/splat.png    R flower density, G species (ordinal, nearest-sampled), B wetness, A grass cover
  assets/terrain/tint.png     mean petal colour of the local flower drift (sRGB), for the far field
  assets/terrain/light.png    R sun shadow, G ambient occlusion, B shore distance (d / (|d| + 16)), A cliffness
  assets/terrain/meta.json    world size, height range, sun, river path, landmarks, spawn
  assets/terrain/preview.png  top-down shaded preview for eyeballing the layout

Usage: tools/.venv/bin/python tools/terrain/bake.py [N=2048] [--preview-only]
"""
import json
import math
import os
import sys
import time

import numpy as np
from numba import njit, prange
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "assets", "terrain")
os.makedirs(OUT, exist_ok=True)

N = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 2048
# --keep-props: leave the lighthouse, stones and trees exactly where props.json already has them
# (their scatter is one random stream, so any change to the terrain would otherwise reshuffle it)
KEEP_PROPS = "--keep-props" in sys.argv
WORLD = 6144.0
CELL = WORLD / N
HALF = WORLD / 2
SEED = 7

# Direction TO the sun (x east, y up, z south). Late-afternoon light from the north-west so the
# north- and west-facing sea cliffs are lit.
SUN_ELEV = math.radians(34.0)
SUN_AZ = math.radians(218.0)  # measured from +z (south) toward +x (east); 218deg -> north-west
SUN = np.array([math.sin(SUN_AZ) * math.cos(SUN_ELEV), math.sin(SUN_ELEV), math.cos(SUN_AZ) * math.cos(SUN_ELEV)])

TWO_PI = 6.283185307179586

# ----------------------------------------------------------------------------------------
# noise
# ----------------------------------------------------------------------------------------

@njit(inline="always")
def _hash(ix, iy, seed):
    h = (ix * 0x27D4EB2D) ^ (iy * 0x165667B1) ^ (seed * 0x9E3779B1)
    h &= 0xFFFFFFFF
    h ^= h >> 15
    h = (h * 0x2C1B3C6D) & 0xFFFFFFFF
    h ^= h >> 12
    h = (h * 0x297A2D39) & 0xFFFFFFFF
    h ^= h >> 15
    return h


@njit(inline="always")
def hash01(ix, iy, seed):
    return _hash(ix, iy, seed) / 4294967296.0


@njit(inline="always")
def gnoise(x, y, seed):
    """Gradient noise, roughly [-1, 1]."""
    x0 = math.floor(x)
    y0 = math.floor(y)
    ix = np.int64(x0)
    iy = np.int64(y0)
    fx = x - x0
    fy = y - y0
    u = fx * fx * fx * (fx * (fx * 6.0 - 15.0) + 10.0)
    v = fy * fy * fy * (fy * (fy * 6.0 - 15.0) + 10.0)
    k = TWO_PI / 4294967296.0
    a = _hash(ix, iy, seed) * k
    b = _hash(ix + 1, iy, seed) * k
    c = _hash(ix, iy + 1, seed) * k
    d = _hash(ix + 1, iy + 1, seed) * k
    n00 = math.cos(a) * fx + math.sin(a) * fy
    n10 = math.cos(b) * (fx - 1.0) + math.sin(b) * fy
    n01 = math.cos(c) * fx + math.sin(c) * (fy - 1.0)
    n11 = math.cos(d) * (fx - 1.0) + math.sin(d) * (fy - 1.0)
    nx0 = n00 + (n10 - n00) * u
    nx1 = n01 + (n11 - n01) * u
    return (nx0 + (nx1 - nx0) * v) * 1.4142


@njit(inline="always")
def fbm(x, y, octaves, seed):
    s = 0.0
    a = 0.5
    f = 1.0
    norm = 0.0
    for o in range(octaves):
        # rotate each octave to hide the lattice
        rx = x * 0.8 - y * 0.6
        ry = x * 0.6 + y * 0.8
        x = rx
        y = ry
        s += a * gnoise(x * f, y * f, seed + o * 17)
        norm += a
        a *= 0.5
        f *= 2.02
    return s / norm


@njit(inline="always")
def ridged(x, y, octaves, seed):
    s = 0.0
    a = 0.5
    f = 1.0
    w = 1.0
    norm = 0.0
    for o in range(octaves):
        rx = x * 0.8 - y * 0.6
        ry = x * 0.6 + y * 0.8
        x = rx
        y = ry
        n = 1.0 - abs(gnoise(x * f, y * f, seed + o * 31))
        n = n * n
        s += a * n * w
        norm += a
        w = min(1.0, max(0.0, n * 1.6))
        a *= 0.5
        f *= 2.07
    return s / norm


@njit(inline="always")
def smoothstep(a, b, x):
    t = (x - a) / (b - a)
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    return t * t * (3.0 - 2.0 * t)


@njit(inline="always")
def smin(a, b, k):
    h = max(k - abs(a - b), 0.0) / k
    return min(a, b) - h * h * k * 0.25


@njit(inline="always")
def mix(a, b, t):
    return a + (b - a) * t


@njit(inline="always")
def seg_dist(px, pz, ax, az, bx, bz):
    """Distance to segment and param t."""
    dx = bx - ax
    dz = bz - az
    l2 = dx * dx + dz * dz
    t = ((px - ax) * dx + (pz - az) * dz) / l2 if l2 > 0 else 0.0
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    qx = ax + dx * t - px
    qz = az + dz * t - pz
    return math.sqrt(qx * qx + qz * qz), t


# ----------------------------------------------------------------------------------------
# layout (all in metres; x east, z south, north = -z)
# ----------------------------------------------------------------------------------------

ELLIPSES = np.array([
    # cx,    cz,    rx,    rz,  rot(deg)
    [-150.0, -420.0, 1750.0, 760.0, -6.0],   # north plateau
    [350.0, 380.0, 1350.0, 900.0, 12.0],     # south body
    [-1450.0, -50.0, 620.0, 560.0, 0.0],     # west shoulder
    [1250.0, -250.0, 800.0, 760.0, 0.0],     # east highland
])

# capsule chains: x, z, radius
FJORD = np.array([
    [-600.0, -1420.0, 100.0],
    [-560.0, -1180.0, 88.0],
    [-470.0, -960.0, 72.0],
    [-350.0, -760.0, 60.0],
    [-270.0, -610.0, 48.0],
    [-235.0, -520.0, 40.0],
])
HEADLAND_W = np.array([
    [-1180.0, -760.0, 110.0],
    [-1420.0, -1060.0, 84.0],
    [-1600.0, -1300.0, 62.0],
    [-1690.0, -1450.0, 46.0],
])
HEADLAND_E = np.array([
    [1280.0, -640.0, 150.0],
    [1560.0, -930.0, 120.0],
    [1760.0, -1140.0, 92.0],
])
# sea stacks: x, z, radius, top height
STACKS = np.array([
    [-1800.0, -1590.0, 26.0, 64.0],
    [-1870.0, -1700.0, 15.0, 38.0],
    [-960.0, -1470.0, 36.0, 84.0],
    [-1060.0, -1590.0, 19.0, 46.0],
    [-760.0, -1560.0, 13.0, 30.0],
    [-330.0, -1500.0, 24.0, 58.0],
    [160.0, -1470.0, 42.0, 96.0],
    [300.0, -1600.0, 21.0, 52.0],
    [70.0, -1640.0, 12.0, 28.0],
    [800.0, -1420.0, 30.0, 74.0],
    [1180.0, -1400.0, 17.0, 40.0],
    [1950.0, -1290.0, 30.0, 70.0],
    [2060.0, -1400.0, 14.0, 34.0],
    [-2260.0, -420.0, 24.0, 46.0],
    [2260.0, -160.0, 26.0, 50.0],
])
LAGOON = np.array([250.0, 1760.0, 640.0])
ISLETS = np.array([
    # x, z, radius, top height (low sandy/grassy cays at the lagoon mouth)
    [-260.0, 1640.0, 70.0, 7.0],
    [560.0, 1700.0, 55.0, 6.0],
    [140.0, 1900.0, 38.0, 4.0],
])
MOUNTAIN = np.array([980.0, -90.0, 1150.0, 330.0])  # x, z, radius, extra height

# river control points (source -> fjord head); refined into a polyline below
RIVER_CTRL = np.array([
    [640.0, -30.0],
    [470.0, -170.0],
    [280.0, -210.0],
    [110.0, -330.0],
    [-60.0, -370.0],
    [-170.0, -455.0],
    [-232.0, -512.0],
    [-262.0, -560.0],
])


def catmull(ctrl, per_seg=24):
    pts = []
    P = np.vstack([ctrl[0] * 2 - ctrl[1], ctrl, ctrl[-1] * 2 - ctrl[-2]])
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(per_seg):
            t = j / per_seg
            t2, t3 = t * t, t * t * t
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    pts.append(P[-2])
    return np.array(pts)


def meander(pts):
    """Give the spline the wandering of a real stream; both ends stay put."""
    d = np.hypot(*np.diff(pts, axis=0).T)
    s_ = np.concatenate([[0], np.cumsum(d)])
    total = s_[-1]
    t = np.gradient(pts, axis=0)
    t /= np.linalg.norm(t, axis=1, keepdims=True)
    nrm = np.stack([-t[:, 1], t[:, 0]], -1)
    taper = np.clip(s_ / 90.0, 0, 1) * np.clip((total - s_ - 210.0) / 160.0, 0, 1)
    off = (15.0 * np.sin(s_ / 38.0 + 1.1 * np.sin(s_ / 91.0)) + 6.0 * np.sin(s_ / 13.0 + 2.0)) * taper
    return pts + nrm * off[:, None]


RIVER = meander(catmull(RIVER_CTRL, per_seg=48))


@njit(inline="always")
def chain_sdf(px, pz, chain):
    d = 1e9
    for i in range(chain.shape[0] - 1):
        dd, t = seg_dist(px, pz, chain[i, 0], chain[i, 1], chain[i + 1, 0], chain[i + 1, 1])
        r = chain[i, 2] + (chain[i + 1, 2] - chain[i, 2]) * t
        d = min(d, dd - r)
    return d


@njit(inline="always")
def northness(x, z):
    """1 on the cliffy north / west / east coasts, 0 on the gentle southern shore."""
    w = fbm(x / 1300.0, z / 1300.0, 2, 91) * 260.0
    return smoothstep(620.0, -150.0, z + w)


@njit(parallel=True, fastmath=True, cache=True)
def land_field(n, cell, half, ell, fjord, hw, he, stacks, lagoon, islets, seed):
    """Implicit island: negative = land. Returns the field."""
    out = np.empty((n, n), np.float32)
    for iz in prange(n):
        z = (iz + 0.5) * cell - half
        for ix in range(n):
            x = (ix + 0.5) * cell - half
            nn = northness(x, z)
            # domain warp for organic coast
            wx = x + fbm(x / 900.0 + 3.1, z / 900.0, 3, seed + 1) * 190.0
            wz = z + fbm(x / 900.0, z / 900.0 + 7.7, 3, seed + 2) * 190.0
            d = 1e9
            for e in range(ell.shape[0]):
                c = math.cos(ell[e, 4] * 0.017453292)
                s = math.sin(ell[e, 4] * 0.017453292)
                qx = (wx - ell[e, 0]) * c + (wz - ell[e, 1]) * s
                qz = -(wx - ell[e, 0]) * s + (wz - ell[e, 1]) * c
                k = math.sqrt((qx / ell[e, 2]) ** 2 + (qz / ell[e, 3]) ** 2)
                de = (k - 1.0) * min(ell[e, 2], ell[e, 3])
                d = smin(d, de, 320.0)
            d = smin(d, chain_sdf(wx, wz, hw), 90.0)
            d = smin(d, chain_sdf(wx, wz, he), 120.0)
            # coastline roughness: bold headlands and coves in the north, smooth arcs in the south
            amp = 0.3 + 0.7 * nn
            d += amp * (fbm(x / 520.0, z / 520.0, 3, seed + 3) * 150.0
                        + fbm(x / 150.0, z / 150.0, 3, seed + 4) * 42.0 * nn
                        + fbm(x / 46.0, z / 46.0, 2, seed + 5) * 11.0 * nn)
            # lagoon bay (subtract) - not warped so the beach arc stays clean
            dl = math.sqrt((x - lagoon[0]) ** 2 + (z - lagoon[1]) ** 2) - lagoon[2]
            dl += fbm(x / 400.0, z / 400.0, 2, seed + 6) * 60.0
            d = -smin(-d, dl, 160.0)
            # fjord (subtract) with slightly noisy walls
            df = chain_sdf(x, z, fjord) + fbm(x / 90.0, z / 90.0, 3, seed + 8) * 16.0
            d = -smin(-d, df, 30.0)
            # sea stacks and cays (union)
            for s_i in range(stacks.shape[0]):
                r = stacks[s_i, 2]
                # each stack is a lopsided slab: stretched along its own axis, with bites out of it
                ca = math.cos(s_i * 2.4)
                sa = math.sin(s_i * 2.4)
                ux = (x - stacks[s_i, 0]) * ca + (z - stacks[s_i, 1]) * sa
                uz = -(x - stacks[s_i, 0]) * sa + (z - stacks[s_i, 1]) * ca
                uz *= 1.0 + 0.55 * hash01(s_i, 7, seed)
                ang = math.atan2(uz, ux)
                rr = r * (1.0 + 0.24 * math.sin(ang * 2.0 + s_i * 1.7) + 0.16 * math.sin(ang * 5.0 + s_i))
                ds = math.sqrt(ux * ux + uz * uz) - rr
                ds += fbm(x / 26.0, z / 26.0, 3, seed + 40 + s_i) * 9.0
                d = min(d, ds)
            for s_i in range(islets.shape[0]):
                ds = math.sqrt((x - islets[s_i, 0]) ** 2 + ((z - islets[s_i, 1]) * 1.5) ** 2) - islets[s_i, 2]
                ds += fbm(x / 60.0, z / 60.0, 2, seed + 70 + s_i) * 14.0
                d = min(d, ds)
            out[iz, ix] = d
    return out


@njit(inline="always")
def mountain_height(x, z, mt, seed):
    dx = x - mt[0]
    dz = z - mt[1]
    wx = dx + fbm(x / 700.0, z / 700.0, 2, seed + 20) * 220.0
    wz = dz + fbm(x / 700.0 + 9.0, z / 700.0, 2, seed + 21) * 220.0
    r = math.sqrt(wx * wx + (wz * 1.15) ** 2) / mt[2]
    if r >= 1.0:
        return 0.0
    f = 1.0 - r
    f = f * f * (3.0 - 2.0 * f)
    rd = ridged(x / 620.0 + 1.7, z / 620.0 - 0.6, 5, seed + 22)
    body = f ** 1.35
    return mt[3] * body * (0.42 + 0.9 * rd * (0.35 + 0.65 * f))


@njit(inline="always")
def plateau_height(x, z, mt, stacks, islets, seed):
    """Top surface of the island before the coast profile is applied."""
    nn = smoothstep(1000.0, -950.0, z + fbm(x / 1500.0, z / 1500.0, 2, seed + 10) * 300.0)
    p = 24.0 + 112.0 * nn
    # broad swells, rolling hills, hummocks
    p += fbm(x / 1250.0 + 0.3, z / 1250.0, 3, seed + 11) * 46.0
    p += fbm(x / 430.0, z / 430.0 + 2.2, 3, seed + 12) * 17.0 * (0.6 + 0.4 * nn)
    p += fbm(x / 140.0 + 5.0, z / 140.0, 3, seed + 13) * 4.5
    # the western shoulder dips into a wide flower bowl
    bowl = math.exp(-(((x + 1200.0) / 520.0) ** 2 + ((z + 60.0) / 430.0) ** 2))
    p -= 26.0 * bowl
    p += mountain_height(x, z, mt, seed)
    p = max(p, 5.0)
    for s_i in range(stacks.shape[0]):
        dd = math.sqrt((x - stacks[s_i, 0]) ** 2 + (z - stacks[s_i, 1]) ** 2)
        r = stacks[s_i, 2]
        t = smoothstep(r + 70.0, r + 18.0, dd)
        top = stacks[s_i, 3] * (0.9 + 0.1 * fbm(x / 18.0, z / 18.0, 2, seed + 50 + s_i)) + (x - stacks[s_i, 0]) * 0.12
        p = mix(p, top, t)
    for s_i in range(islets.shape[0]):
        dd = math.sqrt((x - islets[s_i, 0]) ** 2 + ((z - islets[s_i, 1]) * 1.5) ** 2)
        r = islets[s_i, 2]
        t = smoothstep(r + 120.0, r + 10.0, dd)
        p = mix(p, islets[s_i, 3], t)
    return p


@njit(inline="always")
def cliff_slope(y, x, z, seed, steep):
    """Vertical slope (dy/dd) of the cliff profile at height y: steep walls broken by strata ledges."""
    if y < 2.0:
        # wave-cut platform: a broad shelf in places, none at all in others
        return 0.26 + 3.2 * smoothstep(-0.05, 0.45, fbm(x / 70.0, z / 70.0, 2, seed + 35))
    s0 = (4.6 + 1.9 * fbm(x / 170.0, z / 170.0, 2, seed + 30)) * (1.0 + 2.6 * steep)
    # bedding planes dip gently to the east and undulate
    yb = y - x * 0.022 + fbm(x / 420.0, z / 420.0, 2, seed + 31) * 9.0
    ledge = 0.0
    # irregular strata: a repeating sequence of beds of different thickness
    seq = (0.0, 17.0, 29.0, 52.0, 66.0, 91.0, 118.0, 131.0)
    period = 150.0
    m = yb - math.floor(yb / period) * period
    for k in range(8):
        dy = m - seq[k]
        if dy > period * 0.5:
            dy -= period
        elif dy < -period * 0.5:
            dy += period
        ledge = max(ledge, math.exp(-(dy * dy) / (2.0 * 1.25 * 1.25)) * (0.55 + 0.45 * math.sin(k * 2.4)))
    # ledges pinch in and out along the coast
    pinch = smoothstep(0.02, 0.42, fbm(x / 95.0 + y * 0.013, z / 95.0, 3, seed + 32))
    ledge *= pinch
    return s0 / (1.0 + 20.0 * ledge * (1.0 - 0.7 * steep))


@njit(fastmath=True, cache=True)
def stack_steep(x, z, stacks, fall):
    """1 where the rock stands almost sheer: round the sea stacks and beside the waterfall."""
    stk = 0.0
    for s_i in range(stacks.shape[0]):
        sd = math.sqrt((x - stacks[s_i, 0]) ** 2 + (z - stacks[s_i, 1]) ** 2)
        stk = max(stk, smoothstep(stacks[s_i, 2] + 80.0, stacks[s_i, 2] + 25.0, sd))
    return max(stk, smoothstep(120.0, 50.0, math.sqrt((x - fall[0]) ** 2 + (z - fall[1]) ** 2)))


@njit(fastmath=True, cache=True)
def land_profile(x, z, di, P, cs, stk, seed):
    """Height of the ground di metres in from the coast, where the plateau behind stands at P.
    Zero at the coast, and close to linear across the first cell or two."""
    # --- gentle shore: beach, dune toe, then the land swells up to the plateau
    # (the swash face is steeper than the strand behind it)
    beach = min(di * 0.038 + 0.20 * (1.0 - math.exp(-di / 1.1)), 2.6)
    g = beach + (P - 2.6) * smoothstep(40.0, 560.0, di) ** 1.15
    if g < beach:
        g = beach
    # --- cliff shore: integrate the stratified profile up from the sea
    hc = P
    if cs > 0.001 and di < 150.0:
        dd = di - 1.5 + fbm(x / 26.0, z / 26.0, 2, seed + 33) * 3.5 + fbm(x / 9.0, z / 9.0, 2, seed + 34) * 1.2
        y = 0.0
        acc = 0.0
        if dd > 0.0:
            dy = 0.6
            while y < P:
                sl = cliff_slope(y, x, z, seed, stk)
                # The wall springs from a curved toe a couple of cells wide. A sheer face that
                # starts at full steepness has its foot snapped to the grid, and shows it as a
                # staircase wherever the coast runs diagonally.
                toe = 0.9 + 1.4 * math.sqrt(y)
                if sl > toe:
                    sl = toe
                step = dy / sl
                if acc + step >= dd:
                    y += (dd - acc) * sl
                    break
                acc += step
                y += dy
        # where the wall stands back from the sea, a cobble strand runs up to its foot
        strand = 0.14 * di + 0.08 * (1.0 - math.exp(-di / 1.1))
        if y < strand:
            y = strand
        # rounded lip where the wall meets the meadow
        hc = smin(y, P, 5.0)
        # fallen blocks along the foot of the cliff - but clear of the swash, where they would be
        # half-awash facets of the mesh
        if hc < 5.0:
            blk = fbm(x / 7.0, z / 7.0, 2, seed + 36)
            hc += max(blk - 0.12, 0.0) * 4.5 * smoothstep(5.0, 1.0, hc) * smoothstep(0.35, 1.1, hc)
    hh = mix(g, hc, cs)
    # a wall that stands in the sea leaves it at a slope the mesh can follow for the width of one
    # cell, and only then goes sheer
    cap = di * mix(1.0, 3.0, cs) + 40.0 * max(di - 1.6, 0.0)
    return min(hh, cap)


@njit(parallel=True, fastmath=True, cache=True)
def compose(n, cell, half, d_in, d_out, mt, stacks, islets, river_bed, fall, seed):
    """Height from coast distance + plateau surface. river_bed: per-cell (bed height or +inf).
    fall: xz of the waterfall; the cliff stands sheer around it.

    The waterline is where this surface meets the sea, so how it passes through zero decides how
    the shore looks. Three things make a waterline follow the mesh's triangles instead of the
    coast: ground that is nearly level there (the cut wanders with every centimetre of swell), a
    sheer step (its foot snaps to the grid), and a slope that changes abruptly at the shore (the
    cut snaps to the vertices on the gentler side). So within a few metres of the coast the sea
    floor is the mirror image of the land beside it: one smooth ramp through sea level."""
    h = np.empty((n, n), np.float32)
    cliff = np.empty((n, n), np.float32)
    for iz in prange(n):
        z = (iz + 0.5) * cell - half
        for ix in range(n):
            x = (ix + 0.5) * cell - half
            di = d_in[iz, ix]
            do = d_out[iz, ix]
            C = northness(x, z)
            cs = smoothstep(0.2, 0.7, C)
            if di <= 0.0:
                # sea floor: drops fast below cliffs, long shallow shelf off the beaches
                L = mix(190.0, 16.0, cs)
                dmax = mix(34.0, 46.0, cs)
                dep = -dmax * (1.0 - math.exp(-do / L)) - 0.04 * (1.0 - math.exp(-do / 0.9))
                # sand bars and reef mottling in the shallows
                dep += (1.0 - cs) * fbm(x / 120.0, z / 120.0, 3, seed + 60) * 2.2 * smoothstep(0.0, 120.0, do)
                dep += cs * fbm(x / 30.0, z / 30.0, 2, seed + 61) * 2.0 * smoothstep(2.0, 25.0, do)
                if do < 5.5:
                    # close in: the land's own profile, turned over
                    Pm = plateau_height(x, z, mt, stacks, islets, seed)
                    m = -land_profile(x, z, do, Pm, cs, stack_steep(x, z, stacks, fall), seed)
                    t = smoothstep(2.2, 5.5, do)
                    dep = m * (1.0 - t) + min(dep, m) * t
                lim = -0.1 * min(do, 4.0)          # (no bar or reef breaks surface right at the shore)
                if dep > lim:
                    dep = lim
                h[iz, ix] = dep
                cliff[iz, ix] = cs * math.exp(-do / 40.0)
                continue
            P = plateau_height(x, z, mt, stacks, islets, seed)
            rb = river_bed[iz, ix]
            if rb < P:
                P = rb
            h[iz, ix] = land_profile(x, z, di, P, cs, stack_steep(x, z, stacks, fall), seed)
            # 1 on the cliff face and its lip, fading to 0 inland
            cliff[iz, ix] = cs * smoothstep(75.0, 28.0, di)
    return h, cliff


# ----------------------------------------------------------------------------------------
# river
# ----------------------------------------------------------------------------------------

@njit(parallel=True, fastmath=True, cache=True)
def river_distance(n, cell, half, pts):
    """Per cell: distance to the river polyline and arc-length parameter (metres)."""
    dist = np.full((n, n), 1e9, np.float32)
    arc = np.zeros((n, n), np.float32)
    m = pts.shape[0]
    cum = np.zeros(m, np.float64)
    for i in range(1, m):
        cum[i] = cum[i - 1] + math.sqrt((pts[i, 0] - pts[i - 1, 0]) ** 2 + (pts[i, 1] - pts[i - 1, 1]) ** 2)
    minx = pts[:, 0].min() - 260.0
    maxx = pts[:, 0].max() + 260.0
    minz = pts[:, 1].min() - 260.0
    maxz = pts[:, 1].max() + 260.0
    for iz in prange(n):
        z = (iz + 0.5) * cell - half
        if z < minz or z > maxz:
            continue
        for ix in range(n):
            x = (ix + 0.5) * cell - half
            if x < minx or x > maxx:
                continue
            best = 1e9
            bs = 0.0
            for i in range(m - 1):
                dd, t = seg_dist(x, z, pts[i, 0], pts[i, 1], pts[i + 1, 0], pts[i + 1, 1])
                if dd < best:
                    best = dd
                    bs = cum[i] + (cum[i + 1] - cum[i]) * t
            dist[iz, ix] = best
            arc[iz, ix] = bs
    return dist, arc, cum


@njit(inline="always")
def bilerp(a, fx, fz):
    n = a.shape[0]
    if fx < 0.0:
        fx = 0.0
    if fz < 0.0:
        fz = 0.0
    if fx > n - 1.001:
        fx = n - 1.001
    if fz > n - 1.001:
        fz = n - 1.001
    ix = int(fx)
    iz = int(fz)
    tx = fx - ix
    tz = fz - iz
    return (a[iz, ix] * (1 - tx) + a[iz, ix + 1] * tx) * (1 - tz) + (a[iz + 1, ix] * (1 - tx) + a[iz + 1, ix + 1] * tx) * tz


# ----------------------------------------------------------------------------------------
# erosion
# ----------------------------------------------------------------------------------------

@njit(cache=True)
def erode(h, weight, n_drops, cell, seed, max_steps=90, inertia=0.06, capacity=5.0, min_slope=0.012,
          erode_speed=0.32, deposit_speed=0.28, evaporate=0.014, gravity=6.0, radius=3):
    n = h.shape[0]
    flow = np.zeros((n, n), np.float32)
    np.random.seed(seed)
    # brush
    offs = []
    ws = []
    wsum = 0.0
    for dz in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            d = math.sqrt(dx * dx + dz * dz)
            if d <= radius:
                w = 1.0 - d / radius
                offs.append((dz, dx))
                ws.append(w)
                wsum += w
    nb = len(offs)
    inv_cell = 1.0 / cell
    for drop in range(n_drops):
        px = np.random.random() * (n - 2 * radius - 3) + radius + 1
        pz = np.random.random() * (n - 2 * radius - 3) + radius + 1
        if np.random.random() > weight[int(pz), int(px)] + 0.02:
            continue
        dirx = 0.0
        dirz = 0.0
        speed = 1.0
        water = 1.0
        sed = 0.0
        for step in range(max_steps):
            ix = int(px)
            iz = int(pz)
            fx = px - ix
            fz = pz - iz
            h00 = h[iz, ix]
            h10 = h[iz, ix + 1]
            h01 = h[iz + 1, ix]
            h11 = h[iz + 1, ix + 1]
            gx = ((h10 - h00) * (1 - fz) + (h11 - h01) * fz) * inv_cell
            gz = ((h01 - h00) * (1 - fx) + (h11 - h10) * fx) * inv_cell
            hh = (h00 * (1 - fx) + h10 * fx) * (1 - fz) + (h01 * (1 - fx) + h11 * fx) * fz
            if hh < -0.3:
                break
            dirx = dirx * inertia - gx * (1 - inertia)
            dirz = dirz * inertia - gz * (1 - inertia)
            l = math.sqrt(dirx * dirx + dirz * dirz)
            if l < 1e-8:
                a = np.random.random() * TWO_PI
                dirx = math.cos(a)
                dirz = math.sin(a)
            else:
                dirx /= l
                dirz /= l
            npx = px + dirx
            npz = pz + dirz
            if npx < radius + 1 or npx > n - radius - 2 or npz < radius + 1 or npz > n - radius - 2:
                break
            jx = int(npx)
            jz = int(npz)
            tx = npx - jx
            tz = npz - jz
            nh = (h[jz, jx] * (1 - tx) + h[jz, jx + 1] * tx) * (1 - tz) + (h[jz + 1, jx] * (1 - tx) + h[jz + 1, jx + 1] * tx) * tz
            dh = (nh - hh) * inv_cell  # slope along the step (cell units)
            wloc = weight[iz, ix]
            cap = max(-dh, min_slope) * speed * water * capacity
            if sed > cap or dh > 0.0:
                dep = min(dh, sed) if dh > 0.0 else (sed - cap) * deposit_speed
                sed -= dep
                dm = dep * cell
                h[iz, ix] += dm * (1 - fx) * (1 - fz)
                h[iz, ix + 1] += dm * fx * (1 - fz)
                h[iz + 1, ix] += dm * (1 - fx) * fz
                h[iz + 1, ix + 1] += dm * fx * fz
            else:
                amt = min((cap - sed) * erode_speed, -dh) * wloc
                if amt > 0.0:
                    for b in range(nb):
                        oz = iz + offs[b][0]
                        ox = ix + offs[b][1]
                        h[oz, ox] -= amt * cell * ws[b] / wsum
                    sed += amt
            sp2 = speed * speed - dh * gravity
            speed = math.sqrt(sp2) if sp2 > 0.0 else 0.0
            water *= (1.0 - evaporate)
            flow[iz, ix] += water
            px = npx
            pz = npz
    return flow


@njit(parallel=True, cache=True)
def thermal(h, weight, cell, iters, talus):
    """Talus relaxation: steep loose slopes slump to the angle of repose."""
    n = h.shape[0]
    for it in range(iters):
        delta = np.zeros((n, n), np.float32)
        for iz in prange(1, n - 1):
            for ix in range(1, n - 1):
                w = weight[iz, ix]
                if w <= 0.0:
                    continue
                c = h[iz, ix]
                best = 0.0
                bz = 0
                bx = 0
                for k in range(4):
                    oz = (-1, 1, 0, 0)[k]
                    ox = (0, 0, -1, 1)[k]
                    d = c - h[iz + oz, ix + ox]
                    if d > best:
                        best = d
                        bz = oz
                        bx = ox
                lim = talus * cell
                if best > lim:
                    mv = (best - lim) * 0.25 * w
                    delta[iz, ix] -= mv
                    delta[iz + bz, ix + bx] += mv
        h += delta
    return h


@njit(parallel=True, fastmath=True, cache=True)
def relief(h, slope, river_dist, n, cell, half, seed):
    """Hummocks and tussocks on the meadows."""
    for iz in prange(n):
        z = (iz + 0.5) * cell - half
        for ix in range(n):
            y = h[iz, ix]
            if y < 3.0:
                continue
            x = (ix + 0.5) * cell - half
            k = smoothstep(3.0, 6.0, y) * smoothstep(0.6, 0.3, slope[iz, ix]) * smoothstep(6.0, 14.0, river_dist[iz, ix])
            if k <= 0.0:
                continue
            h[iz, ix] = y + k * (fbm(x / 11.0, z / 11.0, 2, seed + 95) * 0.42 + fbm(x / 34.0, z / 34.0, 2, seed + 96) * 0.9)


# ----------------------------------------------------------------------------------------
# light bakes
# ----------------------------------------------------------------------------------------

@njit(parallel=True, fastmath=True, cache=True)
def bake_shadow(h, cell, sx, sy, sz, max_dist, softness):
    """Soft sun shadow by marching the heightfield toward the sun. 1 = lit."""
    n = h.shape[0]
    out = np.empty((n, n), np.float32)
    hl = math.sqrt(sx * sx + sz * sz)
    dx = sx / hl
    dz = sz / hl
    rise = sy / hl  # metres up per metre travelled horizontally
    for iz in prange(n):
        for ix in range(n):
            y0 = max(h[iz, ix], 0.0) + 0.35
            res = 1.0
            t = cell * 1.2
            while t < max_dist:
                fx = ix + dx * t / cell
                fz = iz + dz * t / cell
                if fx < 0 or fz < 0 or fx > n - 1.01 or fz > n - 1.01:
                    break
                ry = y0 + rise * t
                th = bilerp(h, fx, fz)
                dlt = ry - th
                if dlt < 0.0:
                    res = 0.0
                    break
                pen = softness * dlt / t
                if pen < res:
                    res = pen
                if ry > 520.0:
                    break
                t += max(cell * 0.9, dlt * 0.55)
            out[iz, ix] = res
    return out


@njit(parallel=True, fastmath=True, cache=True)
def bake_ao(h, cell, dirs, steps, max_dist):
    """Sky visibility from the horizon angle in several directions. 1 = open sky."""
    n = h.shape[0]
    out = np.empty((n, n), np.float32)
    nd = dirs.shape[0]
    for iz in prange(n):
        for ix in range(n):
            y0 = max(h[iz, ix], 0.0)
            occ = 0.0
            for d in range(nd):
                mx = 0.0
                for s in range(1, steps + 1):
                    t = max_dist * (s / steps) ** 1.7
                    fx = ix + dirs[d, 0] * t / cell
                    fz = iz + dirs[d, 1] * t / cell
                    if fx < 0 or fz < 0 or fx > n - 1.01 or fz > n - 1.01:
                        break
                    th = bilerp(h, fx, fz)
                    if th < 0.0:
                        th = 0.0
                    a = (th - y0) / t
                    if a > mx:
                        mx = a
                # sin of horizon elevation
                occ += mx / math.sqrt(1.0 + mx * mx)
            out[iz, ix] = 1.0 - occ / nd
    return out


# ----------------------------------------------------------------------------------------
# splat
# ----------------------------------------------------------------------------------------

@njit(parallel=True, fastmath=True, cache=True)
def bake_splat(h, slope, flow, cliff, d_in, river_dist, river_hw, path_dist, n, cell, half, seed):
    out = np.zeros((n, n, 4), np.float32)
    for iz in prange(n):
        z = (iz + 0.5) * cell - half
        for ix in range(n):
            x = (ix + 0.5) * cell - half
            y = h[iz, ix]
            sl = slope[iz, ix]
            # grass cover: everywhere that is not rock wall, beach, scree or river
            alt_n = fbm(x / 160.0, z / 160.0, 2, seed + 80)
            cover = smoothstep(2.4, 4.4, y) * smoothstep(0.98, 0.62, sl) * (1.0 - 0.88 * smoothstep(232.0, 300.0, y + alt_n * 45.0))
            # grass leans right over the water's edge (and hides the mesh's stair-stepped waterline)
            cover *= smoothstep(-0.9, 0.5, river_dist[iz, ix] - 0.86 * river_hw[iz, ix])
            cover *= smoothstep(0.6, 2.2, path_dist[iz, ix])
            # where flowers can grow: gentler ground, off the cliff faces and their ledges
            meadow = smoothstep(3.2, 7.0, y) * smoothstep(0.70, 0.40, sl) * (0.12 + 0.88 * smoothstep(235.0, 150.0, y + alt_n * 40.0))
            meadow *= 1.0 - smoothstep(0.35, 0.9, cliff[iz, ix])
            # big drifts of flowers with ragged edges, thinner in between
            w1 = fbm(x / 520.0 + 11.0, z / 520.0, 3, seed + 81)
            w2 = fbm(x / 120.0, z / 120.0 + 4.0, 3, seed + 82)
            w3 = fbm(x / 26.0, z / 26.0, 2, seed + 83)
            drift = smoothstep(-0.16, 0.30, w1 + 0.46 * w2 + 0.18 * w3)
            dens = meadow * (0.20 + 0.80 * drift)
            # keep the river bank, paths, and wind-scoured cliff lips short-cropped
            dens *= smoothstep(5.0, 16.0, river_dist[iz, ix])
            dens *= smoothstep(1.2, 4.0, path_dist[iz, ix])
            # species: a patchwork of drifts. Each warped voronoi cell picks its own flower, so
            # neighbours are unrelated (no contour-line banding) and equal neighbours merge.
            sx = x + fbm(x / 520.0, z / 520.0 + 3.0, 3, seed + 84) * 170.0 + fbm(x / 60.0, z / 60.0, 2, seed + 87) * 16.0
            sz = z + fbm(x / 520.0 + 5.0, z / 520.0, 3, seed + 85) * 170.0 + fbm(x / 60.0 + 9.0, z / 60.0, 2, seed + 88) * 16.0
            cs_ = 330.0
            cxi = math.floor(sx / cs_)
            czi = math.floor(sz / cs_)
            best = 1e18
            bu = 0.0
            for oz in range(-1, 2):
                for ox in range(-1, 2):
                    gx = np.int64(cxi + ox)
                    gz = np.int64(czi + oz)
                    px = (gx + 0.15 + 0.7 * hash01(gx, gz, seed + 90)) * cs_
                    pz = (gz + 0.15 + 0.7 * hash01(gx, gz, seed + 91)) * cs_
                    dd = (sx - px) ** 2 + (sz - pz) ** 2
                    if dd < best:
                        best = dd
                        bu = hash01(gx, gz, seed + 92)
            # pink cosmos is the island's signature: skew the draw toward it
            # (the upper end is squeezed so gold and poppy stay accents)
            sp = bu ** 1.55
            if sp > 0.78:
                sp = 0.78 + (sp - 0.78) * 0.62 + (0.22 * 0.38 if bu > 0.985 else 0.0)
            # bare ground: paths, scree, beach
            bare = max(smoothstep(2.6, 0.8, path_dist[iz, ix]), smoothstep(0.55, 0.95, sl) * 0.0)
            # wetness / lushness: drainage lines, river margins, low hollows
            wet = min(1.0, math.log1p(flow[iz, ix]) / 6.5)
            wet = max(wet, smoothstep(26.0, 3.0, river_dist[iz, ix]))
            out[iz, ix, 0] = dens
            out[iz, ix, 1] = sp
            out[iz, ix, 2] = wet
            out[iz, ix, 3] = cover
    return out


# ----------------------------------------------------------------------------------------
# props: where the lighthouse, stones and trees stand, and the shadows they throw
# ----------------------------------------------------------------------------------------

MODELS = os.path.join(ROOT, "assets", "models")
WIND_DIR = np.array([0.361, 0.933])     # the prevailing wind blows toward the south-south-east


def prop_info(name):
    with open(os.path.join(MODELS, f"{name}.json")) as f:
        return json.load(f)


class Placer:
    """Rejection-samples prop sites against the terrain."""

    def __init__(self, h, slope, cliff, d_in, rdist, hw_at, seed):
        self.h, self.slope, self.cliff, self.d_in, self.rdist, self.hw = h, slope, cliff, d_in, rdist, hw_at
        self.rng = np.random.default_rng(seed)
        self.prom = h - ndimage.gaussian_filter(h, 45.0 / CELL)      # + on knolls, - in hollows
        self.items = {}                                               # name -> [[x, y, z, yaw, scale]]
        self.all = []                                                 # (x, z, clearance)

    def idx(self, x, z):
        ix = int(np.clip((x + HALF) / CELL - 0.5, 0, N - 1))
        iz = int(np.clip((z + HALF) / CELL - 0.5, 0, N - 1))
        return iz, ix

    def free(self, x, z, r):
        return all((x - a) ** 2 + (z - b) ** 2 > (r + c) ** 2 for a, b, c in self.all)

    def add(self, name, x, z, yaw, scale, clear, sink=0.0):
        y = float(self.h[self.idx(x, z)]) - sink
        self.items.setdefault(name, []).append([round(float(x), 2), round(y, 2), round(float(z), 2), round(float(yaw), 3), round(float(scale), 3)])
        self.all.append((x, z, clear))

    def scatter(self, name, count, test, scale, clear, sink, yaw=None, region=None, tries=40000):
        got = 0
        for _ in range(tries):
            if got >= count:
                break
            if region is None:
                x, z = self.rng.uniform(-HALF * 0.93, HALF * 0.93, 2)
            else:
                x = self.rng.uniform(region[0], region[1]); z = self.rng.uniform(region[2], region[3])
            i = self.idx(x, z)
            if self.h[i] < 0.6 or not test(i, x, z):
                continue
            sc = scale() if callable(scale) else scale
            if not self.free(x, z, clear * sc):
                continue
            self.add(name, x, z, yaw(x, z) if yaw else self.rng.uniform(0, TWO_PI), sc, clear * sc, sink * sc)
            got += 1
        return got


def prop_slabs(name, inst):
    """World-space discs [cx, cz, r, y0, y1] approximating one placed prop."""
    x, y, z, yaw, sc = inst
    c, s_ = math.cos(yaw), math.sin(yaw)
    out = []
    for lx, lz, r, y0, y1 in prop_info(name)["slabs"]:
        # three.js rotation about +Y
        wx = (lx * c + lz * s_) * sc + x
        wz = (-lx * s_ + lz * c) * sc + z
        out.append([wx, wz, r * sc, y + y0 * sc, y + y1 * sc])
    return out


def stamp_shadows(shadow, ao, h, items, M):
    """Multiply prop shadows and contact occlusion into the light map (M x M)."""
    cell = WORLD / M
    sx, sz = SUN[0], SUN[2]
    hl = math.hypot(sx, sz)
    ux, uz = sx / hl, sz / hl                     # horizontal direction toward the sun
    tan_e = SUN[1] / hl
    SS = 3                                        # supersampling per texel
    for name, insts in items.items():
        info = prop_info(name)
        for inst in insts:
            slabs = prop_slabs(name, inst)
            x, y, z, yaw, sc = inst
            H = info["height"] * sc
            R = info["radius"] * sc
            reach = H / tan_e + R + 6.0
            # window: the prop and the ground its shadow can reach (away from the sun)
            x0, x1 = min(x, x - ux * reach) - R - 4, max(x, x - ux * reach) + R + 4
            z0, z1 = min(z, z - uz * reach) - R - 4, max(z, z - uz * reach) + R + 4
            ix0, ix1 = int((x0 + HALF) / cell), int((x1 + HALF) / cell) + 1
            iz0, iz1 = int((z0 + HALF) / cell), int((z1 + HALF) / cell) + 1
            ix0, iz0, ix1, iz1 = max(ix0, 0), max(iz0, 0), min(ix1, M), min(iz1, M)
            if ix1 <= ix0 or iz1 <= iz0:
                continue
            w, hgt = ix1 - ix0, iz1 - iz0
            sub = (np.arange(SS) + 0.5) / SS
            px = ((ix0 + np.arange(w)[:, None] + sub[None, :]).reshape(-1)) * cell - HALF       # w*SS
            pz = ((iz0 + np.arange(hgt)[:, None] + sub[None, :]).reshape(-1)) * cell - HALF     # h*SS
            PX, PZ = np.meshgrid(px, pz)
            # ground height under each sample, from the full-res heightfield
            gy = ndimage.map_coordinates(h, [(PZ + HALF) / CELL - 0.5, (PX + HALF) / CELL - 0.5], order=1, mode="nearest")
            occ = np.zeros_like(PX)
            for cx, cz, r, y0, y1 in slabs:
                vx, vz = cx - PX, cz - PZ
                t0 = vx * ux + vz * uz
                perp = np.abs(vx * uz - vz * ux)
                yr = gy + 0.15 + np.maximum(t0, 0.0) * tan_e
                pen = 0.25 + np.maximum(t0, 0.0) * 0.012
                a = np.clip((r + pen - perp) / (2 * pen), 0, 1)
                a *= np.clip((t0 + r) / (0.5 + r * 0.5), 0, 1)
                a *= np.clip((y1 - yr) / (0.6 + pen), 0, 1) * np.clip((yr - y0 + 0.8) / 0.8, 0, 1)
                occ = np.maximum(occ, a)
            occ = occ.reshape(hgt, SS, w, SS).mean((1, 3))
            shadow[iz0:iz1, ix0:ix1] *= (1.0 - 0.94 * occ).astype(np.float32)
            # contact occlusion around the foot
            br = info["baseRadius"] * sc
            cxs = (ix0 + np.arange(w) + 0.5) * cell - HALF
            czs = (iz0 + np.arange(hgt) + 0.5) * cell - HALF
            d2 = (cxs[None, :] - x) ** 2 + (czs[:, None] - z) ** 2
            ao[iz0:iz1, ix0:ix1] *= (1.0 - 0.45 * np.exp(-d2 / (2 * (br * 0.9 + 0.8) ** 2))).astype(np.float32)


# ----------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------

def to_u8(a):
    return np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8)


def resize_f(a, m):
    """Area-ish resample of a float field to m x m."""
    if a.shape[0] == m:
        return a.astype(np.float32)
    img = Image.fromarray(a.astype(np.float32), mode="F")
    return np.asarray(img.resize((m, m), Image.BILINEAR if m > a.shape[0] else Image.BOX), dtype=np.float32)


def main():
    t0 = time.time()

    def tick(msg):
        print(f"[{time.time() - t0:6.1f}s] {msg}", flush=True)

    tick(f"N={N} cell={CELL:.2f}m")
    F = land_field(N, CELL, HALF, ELLIPSES, FJORD, HEADLAND_W, HEADLAND_E, STACKS, LAGOON, ISLETS, SEED)
    land = F < 0
    # drop tiny specks
    lab, cnt = ndimage.label(land)
    sizes = ndimage.sum(land, lab, range(1, cnt + 1))
    min_cells = (9.0 / CELL) ** 2 * 3.14
    kill = np.isin(lab, np.nonzero(sizes < min_cells)[0] + 1)
    land &= ~kill
    d_in = (ndimage.distance_transform_edt(land) * CELL).astype(np.float32)
    d_out = (ndimage.distance_transform_edt(~land) * CELL).astype(np.float32)
    # The mask is binary, so its edge is a staircase. Near the coast take the distance from the
    # smooth implicit field instead, which places the waterline with sub-cell accuracy.
    gz_, gx_ = np.gradient(F, CELL)
    sd = np.clip(-F / np.maximum(np.hypot(gx_, gz_), 0.3), -12.0, 12.0)       # + inside the land
    sd = np.where(kill, -CELL, sd)
    wfar = np.clip((np.maximum(d_in, d_out) - 3.0) / 4.0, 0, 1)
    d_in = np.where(land, np.maximum(sd, 0.02) * (1 - wfar) + d_in * wfar, 0).astype(np.float32)
    d_out = np.where(~land, np.maximum(-sd, 0.02) * (1 - wfar) + d_out * wfar, 0).astype(np.float32)
    tick(f"land mask + distance fields ({land.mean() * 100:.1f}% land, {cnt} bodies)")

    # ---- river: a graded bed from the mountain to a hanging valley that plunges into the fjord
    rdist, rarc, rcum = river_distance(N, CELL, HALF, RIVER)
    fx = (RIVER[:, 0] + HALF) / CELL - 0.5
    fz = (RIVER[:, 1] + HALF) / CELL - 0.5
    d_path = ndimage.map_coordinates(d_in, [fz, fx], order=1)
    lip_i = int(np.nonzero(d_path > 32.0)[0].max())     # last point still back from the cliff edge
    brink = np.nonzero(d_path <= 0.5)[0]
    fall = RIVER[int(brink.min()) if len(brink) else -1].astype(np.float64)
    big = np.full((N, N), 1e9, np.float32)
    h0, _ = compose(N, CELL, HALF, d_in, d_out, MOUNTAIN, STACKS, ISLETS, big, fall, SEED)
    path_h = ndimage.map_coordinates(h0, [fz, fx], order=1)
    bed = path_h.copy() - 1.6
    lip = float(path_h[lip_i] - 7.0)
    src = bed[0]
    # blend toward a smooth graded profile so it reads as a river, not a ditch
    s_norm = np.clip(rcum / rcum[lip_i], 0, 1)
    graded = src + (lip - src) * s_norm ** 0.85
    bed = np.minimum(bed, graded)
    bed = np.minimum.accumulate(bed)
    bed[lip_i:] = bed[lip_i]                              # level run-out to the brink
    # widens downstream; pools and narrows along the way
    half_w = (2.4 + 2.2 * s_norm) * (1.0 + 0.28 * np.sin(rcum / 21.0 + 0.9) * np.sin(rcum / 57.0))
    # per-cell bed target (cells past the lip keep the lip's level: the notch runs out through the cliff)
    seg_s = np.clip(rarc, 0, rcum[lip_i])
    bed_at = np.interp(seg_s, rcum, bed).astype(np.float32)
    hw_at = np.interp(seg_s, rcum, half_w).astype(np.float32)
    # valley cross-section applied to the plateau: channel, then banks that open out
    rise = np.clip(rdist - hw_at, 0, None)
    # a soft-floored dale: nearly level beside the stream, steepening toward the shoulders
    river_bed = np.where(rdist < 400.0, bed_at + rise * 0.10 + rise * rise * 0.0075, 1e9).astype(np.float32)
    river_bed = np.where(rise <= 0.0, bed_at - 0.75 * (1.0 - (rdist / np.maximum(hw_at, 1e-3)) ** 2), river_bed).astype(np.float32)
    h, cliff = compose(N, CELL, HALF, d_in, d_out, MOUNTAIN, STACKS, ISLETS, river_bed, fall, SEED)
    tick(f"composed (max {h.max():.0f}m, river source {src:.0f}m -> lip {lip:.0f}m)")

    # ---- erosion
    slope0 = np.hypot(*np.gradient(h, CELL))
    mt = np.exp(-(((np.arange(N)[None, :] + 0.5) * CELL - HALF - MOUNTAIN[0]) ** 2 + ((np.arange(N)[:, None] + 0.5) * CELL - HALF - MOUNTAIN[1]) ** 2) / (2 * 620.0 ** 2))
    weight = (0.22 + 0.78 * mt).astype(np.float32)
    weight *= np.clip((h - 1.5) / 6.0, 0, 1)
    weight *= (1.0 - 0.88 * cliff)
    weight *= np.clip((rdist - 4.0) / 30.0, 0.15, 1)
    weight = ndimage.gaussian_filter(weight.astype(np.float32), 2.0 / CELL * 1.5)
    weight[~land] = 0.0
    drops = int(1.5e6 * (N / 2048) ** 2)
    hb = h.copy()
    flow = erode(h, weight, drops, CELL, SEED)
    tick(f"erosion ({drops} drops, mean change {np.abs(h - hb).mean():.3f}m)")
    tw = (mt * np.clip((h - 150.0) / 80.0, 0, 1)).astype(np.float32)
    thermal(h, tw, CELL, 28, 0.95)
    # a light blur where water ran keeps gully floors smooth
    hs = ndimage.gaussian_filter(h, 1.2)
    k = np.clip(np.log1p(flow) / 7.0, 0, 1) * 0.5 * (weight > 0.01)
    h = (h * (1 - k) + hs * k).astype(np.float32)
    # restore river bed and sea floor exactly
    in_bed = rdist < hw_at
    h = np.where(in_bed & land, np.minimum(h, river_bed), h)
    h[~land] = hb[~land]
    tick("thermal + cleanup")

    # ---- micro relief: meadow hummocks so the ground is never dead flat at grass height
    xs = (np.arange(N) + 0.5) * CELL - HALF
    slope = np.hypot(*np.gradient(h, CELL)).astype(np.float32)
    relief(h, slope, rdist, N, CELL, HALF, SEED)
    slope = np.hypot(*np.gradient(h, CELL)).astype(np.float32)

    # ---- the lighthouse stands on a levelled pad on the western head
    best, site = -1e9, None
    props_path = os.path.join(OUT, "props.json")
    kept = None
    h_prev = None
    if KEEP_PROPS and os.path.exists(props_path):
        with open(props_path) as f:
            kept = json.load(f)
        # the heights those props were placed on
        try:
            with open(os.path.join(OUT, "meta.json")) as f:
                pm = json.load(f)
            if pm["n"] == N:
                q_prev = np.fromfile(os.path.join(OUT, "height.u16"), dtype="<u2").reshape(N, N)
                h_prev = pm["hMin"] + q_prev.astype(np.float32) * ((pm["hMax"] - pm["hMin"]) / 65535.0)
        except (OSError, ValueError, KeyError):
            h_prev = None
        if kept.get("lighthouse"):
            lx, ly, lz = kept["lighthouse"][0][:3]
            site = (lx, lz, ly + 0.25)        # (it is sunk a quarter of a metre into its pad)
    for iz in range(0, N if site is None else 0, 3):
        z = xs[iz]
        if abs(z + 1290) > 240:
            continue
        for ix in range(0, N, 3):
            x = xs[ix]
            if abs(x + 1580) > 240 or not (26.0 < d_in[iz, ix] < 60.0) or slope[iz, ix] > 0.22:
                continue
            score = h[iz, ix] - 0.25 * math.hypot(x + 1640, z + 1380)
            if score > best:
                best, site = score, (x, z, float(h[iz, ix]))
    XX, ZZ = np.meshgrid(xs, xs)
    if site:
        dd = np.hypot(XX - site[0], ZZ - site[1])
        k = np.clip((19.0 - dd) / 8.0, 0, 1)
        k = k * k * (3 - 2 * k)
        h = (h * (1 - k) + site[2] * k).astype(np.float32)
        slope = np.hypot(*np.gradient(h, CELL)).astype(np.float32)
    tick(f"lighthouse site {site}")

    # ---- prop sites
    P = Placer(h, slope, cliff, d_in, rdist, hw_at, SEED + 500)
    rng = P.rng
    if kept:
        # same places; but the ground under a few of them will have moved a little (the strand is
        # reshaped, and erosion never lands quite the same way twice), so carry each one up or
        # down with it
        P.items = kept
        if h_prev is not None:
            moved = 0
            for items in kept.values():
                for it in items:
                    i = P.idx(it[0], it[2])
                    dh = float(h[i]) - float(h_prev[i])
                    if abs(dh) > 0.01:
                        it[1] = round(it[1] + dh, 2)
                        moved += 1
            print(f"         re-seated {moved} kept props on the new ground", flush=True)
    else:
        cx, cz = -1200.0, -60.0
        if site:
            # door toward the island
            P.add("lighthouse", site[0], site[1], math.atan2(-(0 - site[1]), 0 - site[0]) + 0.6, 1.0, 10.0, 0.25)
        # a stone circle in the western bowl, and lone stones on the knolls
        for k_ in range(11):
            a = k_ / 11 * TWO_PI + 0.2
            P.add("menhir", cx + math.cos(a) * 13.5, cz + math.sin(a) * 13.5, a + rng.uniform(-0.4, 0.4), rng.uniform(0.75, 1.15), 1.2, 0.35)
        P.add("menhir", cx + 1.5, cz - 1.0, 0.7, 1.45, 1.6, 0.4)
        P.scatter("menhir", 9, lambda i, x, z: P.prom[i] > 2.2 and slope[i] < 0.16 and 25 < h[i] < 210 and cliff[i] < 0.2 and rdist[i] > 40,
                  lambda: rng.uniform(0.9, 1.5), 180.0, 0.35)
        # boulders: scree at the mountain's foot, erratics on the downs, the strand, the river, the cliff tops
        small = lambda: 0.45 + 1.7 * rng.random() ** 2.2
        P.scatter("boulders", 30, lambda i, x, z: 175 < h[i] < 285 and 0.22 < slope[i] < 0.75, small, 3.2, 0.5)
        P.scatter("boulders", 18, lambda i, x, z: h[i] > 8 and slope[i] < 0.28 and cliff[i] < 0.3 and rdist[i] > 20, small, 3.2, 0.45)
        P.scatter("boulders", 12, lambda i, x, z: 0.9 < h[i] < 3.2 and cliff[i] < 0.2, small, 3.2, 0.6)
        P.scatter("boulders", 18, lambda i, x, z: P.hw[i] + 0.5 < rdist[i] < P.hw[i] + 7.0 and d_in[i] > 45, lambda: 0.35 + 0.9 * rng.random() ** 2, 2.6, 0.5)
        P.scatter("boulders", 12, lambda i, x, z: 0.3 < cliff[i] < 0.9 and slope[i] < 0.3 and h[i] > 30, small, 3.2, 0.45)
        # wind-bent trees: down the dale, and in clumps where the downs give some shelter
        lean = prop_info("tree")["lean"]
        lean_a = math.atan2(-lean[1], lean[0])
        wind_a = math.atan2(-WIND_DIR[1], WIND_DIR[0])
        tree_yaw = lambda x, z: wind_a - lean_a + rng.uniform(-0.3, 0.3)
        tree_sc = lambda: rng.uniform(0.75, 1.4)
        P.scatter("tree", 26, lambda i, x, z: 7.0 < rdist[i] - P.hw[i] < 48.0 and slope[i] < 0.5 and h[i] < 215 and d_in[i] > 60, tree_sc, 4.5, 0.25, tree_yaw)
        clumps = []
        P_before = len(P.items.get("tree", []))
        for _ in range(4000):
            if len(clumps) >= 7:
                break
            x, z = rng.uniform(-HALF * 0.8, HALF * 0.8, 2)
            i = P.idx(x, z)
            if not (P.prom[i] < -1.2 and 15 < h[i] < 160 and slope[i] < 0.3 and cliff[i] < 0.1 and rdist[i] > 120):
                continue
            if any((x - a) ** 2 + (z - b) ** 2 < 420 ** 2 for a, b in clumps):
                continue
            clumps.append((x, z))
            P.scatter("tree", int(rng.integers(3, 6)), lambda i, x_, z_: slope[i] < 0.4 and h[i] > 6, tree_sc, 4.0, 0.25, tree_yaw,
                      region=(x - 26, x + 26, z - 26, z + 26), tries=400)
        P.add("tree", cx + 24.0, cz + 9.0, tree_yaw(0, 0), 1.25, 4.0, 0.3)
    tick("props: " + ", ".join(f"{k_} {len(v)}" for k_, v in P.items.items()))

    # ---- paths (none yet; placeholder distance field)
    path_dist = np.full((N, N), 1e9, np.float32)

    # ---- maps
    M = min(N, 2048)
    splat = bake_splat(h, slope, flow, cliff, d_in, rdist, hw_at, path_dist, N, CELL, HALF, SEED)
    if M != N:
        k = N // M
        species = splat[::k, ::k, 1]            # an ordinal: never average it
        splat = np.stack([resize_f(splat[..., c], M) for c in range(4)], -1)
        splat[..., 1] = species
    # nothing grows under a prop's foot
    cellS = WORLD / M
    for name, insts in P.items.items():
        info = prop_info(name)
        for x, y, z, yaw, sc in insts:
            r = info["baseRadius"] * sc * (1.0 if name != "tree" else 0.35)
            i0, i1 = int((x - r - 3 + HALF) / cellS), int((x + r + 3 + HALF) / cellS) + 1
            j0, j1 = int((z - r - 3 + HALF) / cellS), int((z + r + 3 + HALF) / cellS) + 1
            gx = (np.arange(i0, i1) + 0.5) * cellS - HALF
            gz = (np.arange(j0, j1) + 0.5) * cellS - HALF
            d = np.hypot(gx[None, :] - x, gz[:, None] - z)
            keep = np.clip((d - r * 0.8) / 1.6, 0, 1).astype(np.float32)
            splat[j0:j1, i0:i1, 3] *= keep
            splat[j0:j1, i0:i1, 0] *= keep
    Image.fromarray(to_u8(splat), "RGBA").save(os.path.join(OUT, "splat.png"), optimize=True)
    # far-field flower colour: the mean petal colour of each drift, softened so borders intermix
    sp = splat[..., 1]
    pal = np.array([[0.94, 0.36, 0.60], [0.96, 0.92, 0.72], [0.52, 0.38, 0.86], [0.96, 0.82, 0.30], [0.90, 0.26, 0.14]], np.float32)
    idx = np.digitize(sp, [0.42, 0.60, 0.78, 0.90])
    tint = pal[idx]
    sig = 9.0 / (WORLD / M)
    tint = np.stack([ndimage.gaussian_filter(tint[..., c], sig) for c in range(3)], -1)
    srgb = np.where(tint <= 0.0031308, tint * 12.92, 1.055 * np.power(np.clip(tint, 1e-6, 1), 1 / 2.4) - 0.055)
    Image.fromarray(to_u8(srgb), "RGB").save(os.path.join(OUT, "tint.png"), optimize=True)
    tick("splat + tint")

    ML = N                                   # the light map keeps full resolution: crisp cliff and prop shadows
    hL = resize_f(h, ML)
    cellL = WORLD / ML
    shadow = bake_shadow(hL, cellL, SUN[0], SUN[1], SUN[2], 2600.0, 9.0)
    shadow = ndimage.gaussian_filter(shadow, 1.0)
    tick("sun shadow")
    ang = np.arange(16) / 16.0 * TWO_PI
    dirs = np.stack([np.cos(ang), np.sin(ang)], -1)
    ao_near = bake_ao(hL, cellL, dirs, 10, 60.0)
    ao_far = bake_ao(hL, cellL, dirs, 10, 420.0)
    ao = np.clip(ao_near * 0.55 + ao_far * 0.45, 0, 1)
    tick("ambient occlusion")
    stamp_shadows(shadow, ao, h, P.items, ML)
    tick("prop shadows")
    # Shore distance, signed: metres offshore (+) / inland (-). Taken from the same sub-cell field
    # the coast was shaped with - measured from the land/sea mask it would be a staircase, and so
    # would every foam line drawn from it. Stored as d / (|d| + 16): steps of about 12 cm at the
    # waterline, coarser far out where nothing needs it.
    sd_shore = resize_f(d_out - d_in, ML)
    shore = np.clip(0.5 + 0.5 * sd_shore / (np.abs(sd_shore) + 16.0), 0, 1)
    light = np.stack([shadow, ao, shore, resize_f(cliff, ML)], -1)
    Image.fromarray(to_u8(light), "RGBA").save(os.path.join(OUT, "light.png"), optimize=True)
    tick("light")

    # ---- height
    h_min = float(math.floor(h.min() - 1.0))
    h_max = float(math.ceil(h.max() + 1.0))
    q = np.clip((h - h_min) / (h_max - h_min) * 65535.0 + 0.5, 0, 65535).astype("<u2")
    q.tofile(os.path.join(OUT, "height.u16"))

    # ---- river export: the path and its half-width; the game reads levels off the terrain itself
    riv = [[round(float(RIVER[i, 0]), 2), round(float(RIVER[i, 1]), 2), round(float(half_w[i]), 2)] for i in range(len(RIVER))]
    meta = {
        "world": WORLD, "n": N, "cell": CELL, "mapN": M,
        "hMin": h_min, "hMax": h_max, "sea": 0.0,
        "sun": [float(SUN[0]), float(SUN[1]), float(SUN[2])],
        "river": riv,
        "riverLip": lip_i,
        "lighthouse": list(site) if site else None,
        "stacks": STACKS.tolist(),
        "fjord": FJORD.tolist(),
        "mountain": MOUNTAIN.tolist(),
        "lagoon": LAGOON.tolist(),
        "peak": None,
    }
    pk = np.unravel_index(np.argmax(h), h.shape)
    meta["peak"] = [float(xs[pk[1]]), float(h.max()), float(xs[pk[0]])]
    with open(os.path.join(OUT, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    with open(os.path.join(OUT, "props.json"), "w") as f:
        json.dump(P.items, f)
    tick(f"height [{h_min:.0f}, {h_max:.0f}] + meta")

    preview(h, splat, shadow, ao, M)
    tick("preview")


def preview(h, splat, shadow, ao, M):
    """Top-down shaded preview, roughly the palette the game uses."""
    P = 2048
    hp = resize_f(h, P)
    cell = WORLD / P
    gz, gx = np.gradient(hp, cell)
    nrm = np.stack([-gx, np.ones_like(hp), -gz], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    ndl = np.clip(nrm @ SUN, 0, 1)
    slope = np.hypot(gx, gz)
    sp = np.stack([resize_f(splat[..., c], P) for c in range(4)], -1)
    grass = np.array([0.36, 0.52, 0.16])
    rock = np.array([0.42, 0.38, 0.34])
    sand = np.array([0.86, 0.8, 0.62])
    col = np.broadcast_to(grass, (P, P, 3)).copy()
    pal = np.array([[0.95, 0.55, 0.75], [0.97, 0.95, 0.9], [0.62, 0.48, 0.9], [0.9, 0.2, 0.16], [0.98, 0.82, 0.2]])
    idx = np.clip((sp[..., 1] * 5).astype(int), 0, 4)
    fl = pal[idx]
    col = col * (1 - sp[..., 0:1] * 0.75) + fl * sp[..., 0:1] * 0.75
    rk = np.clip((slope - 0.75) / 0.5, 0, 1)[..., None]
    col = col * (1 - rk) + rock * rk
    bs = np.clip((4.0 - hp) / 2.0, 0, 1)[..., None]
    col = col * (1 - bs) + sand * bs
    lit = (0.32 + 0.9 * ndl * resize_f(shadow, P)) * (0.5 + 0.5 * resize_f(ao, P))
    col = col * lit[..., None]
    depth = np.clip(-hp / 30.0, 0, 1)[..., None]
    water = np.array([0.25, 0.75, 0.72]) * (1 - depth) + np.array([0.03, 0.2, 0.36]) * depth
    sea = (hp <= 0)[..., None]
    col = np.where(sea, water, col)
    Image.fromarray(to_u8(np.clip(col, 0, 1) ** (1 / 2.2)), "RGB").save(os.path.join(OUT, "preview.png"))


if __name__ == "__main__":
    main()
