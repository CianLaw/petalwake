#!/usr/bin/env python3
"""Lay out the six western places and write assets/places/west.json.

    tools/.venv/bin/python tools/places/west_layout.py

Everything is placed from the baked heightfield (assets/terrain/height.u16), so run it again after
a terrain bake that moves the ground. The models come from tools/places/west_models.py (generated
pieces) and tools/blender/place_flora_west.py (plants, cloth).
World: +x east, +z south, y up, metres. A piece's yaw turns its local +x toward (cos yaw, -sin yaw).
"""
import json, math, os, random
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
META = json.load(open(os.path.join(ROOT, "assets", "terrain", "meta.json")))
N, CELL, HALF = META["n"], META["cell"], META["world"] / 2
_q = np.fromfile(os.path.join(ROOT, "assets", "terrain", "height.u16"), dtype="<u2").reshape(N, N)
HMAP = META["hMin"] + _q.astype(np.float32) * (META["hMax"] - META["hMin"]) / 65535
WIND = (0.361, 0.933)                       # the prevailing wind blows toward the south-south-east
DOWNWIND = math.atan2(-WIND[1], WIND[0])    # yaw that points a piece's +x downwind


def gy(x, z):
    fx = min(max((x + HALF) / CELL - 0.5, 0), N - 1.001); fz = min(max((z + HALF) / CELL - 0.5, 0), N - 1.001)
    ix, iz = int(fx), int(fz); tx, tz = fx - ix, fz - iz
    a, b, c, d = HMAP[iz, ix], HMAP[iz, ix + 1], HMAP[iz + 1, ix], HMAP[iz + 1, ix + 1]
    return float((a + (b - a) * tx) * (1 - tz) + (c + (d - c) * tx) * tz)


def yaw_to(dx, dz):
    return math.atan2(-dz, dx)


def rot(yaw, lx, lz):
    """A local offset turned by yaw (three.js rotation about +y)."""
    c, s = math.cos(yaw), math.sin(yaw)
    return lx * c + lz * s, -lx * s + lz * c


def info(model):
    path = MODELS[model]
    return json.load(open(os.path.join(ROOT, "assets", "places", os.path.splitext(path)[0] + ".json")))


MODELS = {k: f"west/{k}.glb" for k in (
    "blossom_tree teacup gentian petalfall moss "
    "wisteria_bridge stone_lamp thimble wisteria wisteria_fall fern flagiris rimlily "
    "ship_mast anchor whistle pennant_red pennant_gold pennant_white bunting cottongrass heather "
    "flower_boat glass_floats tide_knot marigold seapoppy marram driftwood groyne_post oar_flag "
    "sundial hourglass dandelion_clock dandelion_half dandelion_bloom "
    "stone_hand storm_marble spiderlily").split()}
MODELS["menhir"] = "../models/menhir.glb"          # the island's own standing stones and boulders:
MODELS["boulders"] = "../models/boulders.glb"      # already loaded by the game, so they cost nothing more


class Place:
    def __init__(self, id, name, hint, x, z, radius):
        self.d = {"id": id, "name": name, "hint": hint, "pos": [x, round(gy(x, z), 2), z], "radius": radius,
                  "models": {}, "items": [], "flora": [], "treasure": None, "clear": []}
        self.rnd = random.Random(sum(map(ord, id)))

    def use(self, model):
        self.d["models"][model] = MODELS[model]

    def item(self, model, x, z, yaw=0.0, scale=1.0, dy=0.0, y=None, **extra):
        self.use(model)
        it = {"model": model, "pos": [round(x, 2), round((gy(x, z) if y is None else y) + dy, 2), round(z, 2)], "yaw": round(yaw, 4),
              "scale": [round(s, 3) for s in scale] if isinstance(scale, (list, tuple)) else round(scale, 3)}
        it.update(extra)
        self.d["items"].append(it)
        return it

    def flora(self, model, x, z, radius, count, seed, scale, **extra):
        self.use(model)
        f = {"model": model, "center": [round(x, 2), round(z, 2)], "radius": radius, "count": count, "seed": seed, "scale": list(scale)}
        f.update(extra)
        self.d["flora"].append(f)

    def treasure(self, id, name, lore, model, x, y, z, **extra):
        self.use(model)
        self.d["treasure"] = {"id": id, "name": name, "lore": lore, "model": model, "pos": [round(x, 2), round(y, 2), round(z, 2)], **extra}

    def clear(self, x, z, r, grass, flowers):
        self.d["clear"].append({"x": round(x, 1), "z": round(z, 1), "r": r, "grass": grass, "flowers": flowers})

    def drift(self, x, y, z, radius, rate, color, kind="petal", **extra):
        self.d.setdefault("drift", []).append({"from": [round(x, 2), round(y, 2), round(z, 2)], "radius": radius, "rate": rate, "color": color, "kind": kind, **extra})


# =====================================================================================
def blossom_sister():
    """A sea stack north of the shale coast, and the old cherry that has it (nearly) to itself."""
    x, z = -955.0, -1463.0
    p = Place("blossom_sister", "The Blossom Sister", "One of the Sisters, north of the shale coast, wears pink in every season.", x, z, 34)
    t = info("blossom_tree")
    S = 1.6
    # turn the tree so its crown streams downwind, like the island's hawthorns
    yaw = math.atan2(t["lean"][1], t["lean"][0]) - math.atan2(WIND[1], WIND[0])
    p.item("blossom_tree", x, z, yaw, S, dy=-0.5)
    cx, cz = rot(yaw, t["lean"][0] * S, t["lean"][1] * S)
    cx, cz = x + cx, z + cz                                        # under the middle of the crown
    p.flora("petalfall", cx, cz, 12.5, 700, 3, (0.9, 1.9))
    p.flora("gentian", x + 1, z - 1, 17, 230, 11, (1.5, 2.6), clump=0.45)
    p.flora("moss", x, z, 9.0, 30, 5, (0.8, 1.6), inner=2.6)
    for bx, bz, s, a in ((-963.5, -1458.5, 0.42, 0.7), (-945.5, -1455.0, 0.5, 2.9), (-950.0, -1473.5, 0.34, 4.4), (-958.5, -1451.5, 0.26, 1.9)):
        p.item("boulders", bx, bz, a, s, dy=-0.25)
    # one seedling of the old tree has taken, at the windward end of the top
    sx, sz = -962.5, -1474.0
    p.item("blossom_tree", sx, sz, yaw + 0.9, 0.36, dy=-0.12)
    p.flora("petalfall", sx - 0.4, sz + 0.6, 3.2, 70, 4, (0.8, 1.5))
    p.flora("gentian", sx + 1.5, sz + 2.5, 5.0, 30, 12, (1.4, 2.3), inner=1.2)
    p.drift(cx, gy(x, z) + 7.4 * S, cz, 6.5, 14, [0.97, 0.66, 0.80], spread=2.2)
    tx, tz = -944.5, -1451.5                                       # the far end of the top (a wind seed already hangs over the near one)
    p.treasure("unspilled_cup", "The Unspilled Cup", "However the gale howls around the Sister, the tea in this cup has never so much as rippled.",
               "teacup", tx, gy(tx, tz) + 3.6, tz, color=[1.0, 0.72, 0.84], petals=[[0.97, 0.76, 0.87], [0.97, 0.42, 0.66], [0.97, 0.96, 0.90]])
    p.clear(x, z, 17, 0.45, 0.0)
    return p


# =====================================================================================
def river_rows():
    """The river as the game draws it (src/world/river.js): centre line, half width, water level."""
    path = META["river"]
    rows, s0, nxt = [], 0.0, 0.0
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        dx, dz = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dz)
        while nxt <= s0 + ln:
            t = (nxt - s0) / ln
            rows.append({"x": a[0] + dx * t, "z": a[1] + dz * t, "hw": a[2] + (b[2] - a[2]) * t, "tx": dx / ln, "tz": dz / ln, "s": nxt})
            nxt += 1.5
        s0 += ln
    level, end = math.inf, len(rows)
    for i, r in enumerate(rows):
        bed = gy(r["x"], r["z"])
        if level < math.inf and bed < level - 0.55 - 3.0: end = i; break
        level = min(level, bed + 0.55)
        r["y"] = level
        if bed < 0.3: end = i; break
    rows = rows[:end]
    for _ in range(3):
        for i in range(1, len(rows) - 1):
            rows[i]["y"] = min(rows[i]["y"], (rows[i - 1]["y"] + rows[i]["y"] * 2 + rows[i + 1]["y"]) / 4 + 0.02)
    return rows


def farewell_bridge():
    """The river's last pool before it falls into the fjord: a humpback bridge under wisteria."""
    rows = river_rows()
    lip = rows[-1]
    back = lambda m: rows[len(rows) - 1 - int(round(m / 1.5))]          # the row m metres upstream of the brink
    b = back(25.0)
    p = Place("farewell_bridge", "Farewell Bridge", "Where the river takes its last step before the fall, something purple hangs over the water.", round(b["x"], 1), round(b["z"], 1), 46)
    nx, nz = -b["tz"], b["tx"]                                         # across the river
    S = 1.25
    yaw = yaw_to(nx, nz)
    by = gy(b["x"], b["z"]) - 0.2
    p.item("wisteria_bridge", b["x"], b["z"], yaw, S, y=by)
    # ---- wisteria hung along both parapets (the generated bridge only flowers on one side)
    prof = [(-6.75, 2.9), (-5.5, 3.2), (-4.5, 3.4), (-3.5, 4.2), (-2.5, 4.6), (-1.5, 5.0), (0.0, 5.0), (1.5, 4.8), (2.5, 4.65), (3.5, 4.0), (4.5, 3.8), (5.5, 3.2), (6.75, 2.9)]
    top = lambda lx: float(np.interp(lx, [q[0] for q in prof], [q[1] for q in prof]))
    R = p.rnd
    for side in (-1, 1):
        lx = -6.1 + R.uniform(0, 0.4)
        while lx < 6.2:
            ox, oz = rot(yaw, lx * S, side * 2.98 * S)
            s = R.uniform(1.15, 1.9) * (1.0 if abs(lx) > 2.6 else 0.9)
            p.item("wisteria", b["x"] + ox, b["z"] + oz, yaw + R.uniform(-0.25, 0.25) + (math.pi if side < 0 else 0), s, y=by + (top(lx) - 0.38) * S)
            lx += R.uniform(0.75, 1.15)
    # ---- lamps at the four corners
    for sx in (-1, 1):
        for sz in (-1, 1):
            ox, oz = rot(yaw, sx * 7.55 * S, sz * 2.75 * S)
            p.item("stone_lamp", b["x"] + ox, b["z"] + oz, yaw + (0 if sx > 0 else math.pi) + R.uniform(-0.2, 0.2), R.uniform(0.95, 1.1), dy=-0.12)
    # ---- lotus on the pool, above and below the bridge
    placed = []
    for k in range(60):
        m = R.uniform(3.0, 62.0)
        r = back(m)
        u = R.uniform(-0.6, 0.6) * r["hw"]
        x, z = r["x"] - r["tz"] * u, r["z"] + r["tx"] * u
        if abs(m - 25.0) < 6.0 and abs(u) > 2.2 * S: continue          # the bridge's feet
        if gy(x, z) > r["y"] - 0.2: continue                            # not enough water
        if any((x - q[0]) ** 2 + (z - q[1]) ** 2 < 4.4 ** 2 for q in placed): continue
        placed.append((x, z))
        p.item("rimlily", x, z, R.uniform(0, 6.28), R.uniform(0.7, 1.15), y=r["y"] + 0.012)
        if len(placed) >= 14: break
    # ---- the banks: giant ferns by the bridge and the brink, goldflag iris in drifts along the water
    for m, lat, rad, n in ((25, 16.0, 7.5, 19), (25, -16.0, 7.5, 19), (40, 13.0, 5.5, 10), (9, 12.5, 5.5, 11), (7, -13.0, 5.5, 11), (52, -12.5, 6.0, 10)):
        r = back(m)
        p.flora("fern", r["x"] - r["tz"] * lat, r["z"] + r["tx"] * lat, rad, n, 40 + int(m) + (1 if lat > 0 else 0), (1.0, 1.7), clump=0.3)
    for i, (m, lat, rad, n) in enumerate(((32, 13.0, 6.0, 44), (17, 12.0, 6.0, 48), (5, 11.5, 5.0, 36), (34, -13.0, 6.0, 44), (16, -12.0, 6.5, 48), (3, -11.0, 5.0, 36), (47, 12.0, 5.5, 28), (58, -12.5, 5.5, 28))):
        r = back(m)
        p.flora("flagiris", r["x"] - r["tz"] * lat, r["z"] + r["tx"] * lat, rad, n, 60 + i, (0.9, 1.45), clump=0.55)
        p.clear(r["x"] - r["tz"] * lat, r["z"] + r["tx"] * lat, rad + 3, 0.75, 0.1)
    # fallen blossom riding the pool down to the brink
    for i, m in enumerate((35, 29, 21, 15, 9, 4)):
        r = back(m)
        p.flora("wisteria_fall", r["x"], r["z"], 4.7, 70 if 12 < m < 32 else 45, 120 + i, (0.9, 1.8), lift=round(r["y"] - gy(r["x"], r["z"]) + 0.02, 3))
    p.drift(b["x"], by + 4.2 * S, b["z"], 6.5, 5, [0.70, 0.55, 0.95], spread=1.0)
    # ---- the treasure hangs just past the brink, where the ground goes: low enough to be seen through
    # the arch from upstream, and to be taken by a broom that has just skimmed under it
    tx, tz = lip["x"] + lip["tx"] * 3.0, lip["z"] + lip["tz"] * 3.0
    p.treasure("rain_thimble", "Thimble of the First Rain", "Still brimming with the first rain that ever fell on the island. It has been trying to reach the sea ever since.",
               "thimble", tx, lip["y"] + 1.6, tz, color=[0.62, 0.86, 1.0], petals=[[0.66, 0.50, 0.93], [0.42, 0.26, 0.82], [0.97, 0.96, 0.90]])
    return p


# =====================================================================================
def shipless_mast():
    """The plateau of the north-west headland comes to a point like a bow. Somebody stepped a mast there
    and lined the rails with pennants, and the headland has been under sail ever since."""
    mx, mz = -1474.0, -1117.0
    p = Place("shipless_mast", "The Shipless Mast", "On the spine of Lantern Head a mast still flies its colours, with no ship beneath it.", -1466.0, -1090.0, 60)
    R = p.rnd
    yaw = yaw_to(0.973, -0.23)                                          # the yard lies across the "deck"
    base = gy(mx, mz) - 0.25
    p.item("ship_mast", mx, mz, yaw, 1.0, y=base)
    hx, hz = rot(yaw, -1.4, 0.1)                                        # the masthead leans a little
    hx, hz = mx + hx, mz + hz
    # stays strung with flags, down to pegs on the deck
    for dx, dz in ((-0.30, 0.95), (0.42, 0.91), (0.86, 0.50)):
        l = math.hypot(dx, dz); dx, dz = dx / l, dz / l
        peg = gy(hx + dx * 11.5, hz + dz * 11.5)
        p.item("bunting", hx, hz, yaw_to(dx, dz), [1.0, (base + 14.2 - peg) / 14.2, 1.0], y=peg)
    # pennant poles down both rails, bow to stern
    cols = ["pennant_red", "pennant_gold", "pennant_white"]
    rails = [[(-1479.0, -1103.0 + 15.0 * i) for i in range(5)], [(-1462.0 + 6.2 * i, -1105.0 + 15.5 * i) for i in range(5)]]
    k = 0
    for rail in rails:
        for (x, z) in rail:
            p.item(cols[k % 3], x, z, DOWNWIND + R.uniform(-0.08, 0.08), R.uniform(0.88, 1.08), dy=-0.1)
            k += 1
    for (x, z, c) in ((-1470.0, -1030.0, "pennant_gold"), (-1452.0, -1029.0, "pennant_red")):      # the stern
        p.item(c, x, z, DOWNWIND, 1.0, dy=-0.1)
    ax, az = mx + 4.6, mz + 3.4
    p.item("anchor", ax, az, 2.2, 1.35, dy=-0.1)
    # cotton grass down the deck, heather about the mast and under the poles
    for i, (x, z, rad, n) in enumerate(((-1468.0, -1098.0, 10, 100), (-1462.0, -1078.0, 11, 105), (-1458.0, -1058.0, 11, 100), (-1470.0, -1045.0, 9, 72), (-1448.0, -1040.0, 9, 63))):
        p.flora("cottongrass", x, z, rad, n, 20 + i, (1.0, 1.7), clump=0.5)
        p.clear(x, z, rad + 2, 0.85, 0.25)
    for i, (x, z, rad, n) in enumerate(((mx + 2, mz + 8, 8.5, 60), (-1478.0, -1080.0, 7, 44), (-1452.0, -1072.0, 7, 44), (-1462.0, -1040.0, 8, 44))):
        p.flora("heather", x, z, rad, n, 30 + i, (1.2, 2.2), clump=0.45)
    p.treasure("gale_whistle", "The Gale-Whistle", "Blow it once and the wind remembers your name. Blow it twice and it comes looking for you.",
               "whistle", hx, base + 15.0 + 2.0, hz, color=[1.0, 0.80, 0.50], petals=[[0.97, 0.96, 0.90], [0.80, 0.07, 0.05], [0.98, 0.66, 0.08]])
    return p


# =====================================================================================
def marigold_wreck():
    """A rowing boat wrecked on the south-west strand, long since become a flower bed."""
    x, z = -1478.0, 460.0
    p = Place("marigold_wreck", "The Wreck of the Marigold", "A little blue boat came ashore on the Longstrand long ago, and has been in flower ever since.", x, z, 40)
    R = p.rnd
    S, yaw = 1.6, 0.5
    by = gy(x, z)
    p.item("flower_boat", x, z, yaw, S, y=by, rot=[0.0, 0.0, 0.13])
    orange = [0.98, 0.42, 0.04]
    # marigolds: in the boat (its hold is full of earth), spilled around it, and seeded off downwind
    for i, lx in enumerate((-1.75, -0.55, 0.95)):
        ox, oz = rot(yaw, lx * S, 0.05)
        p.flora("marigold", x + ox, z + oz, 0.9, 11, 70 + i, (1.3, 1.9), lift=0.9 * S)
    p.flora("marigold", x, z, 8.5, 130, 73, (1.3, 2.3), inner=3.6, clump=0.3)
    # ...and a long drift of them trailing off downwind, where the seed has blown
    p.flora("marigold", x + WIND[0] * 12, z + WIND[1] * 12, 10.0, 160, 74, (1.2, 2.2), clump=0.5)
    p.flora("marigold", x + WIND[0] * 26 + 2, z + WIND[1] * 26, 8.0, 80, 76, (1.1, 1.9), clump=0.6)
    fx, fz = rot(yaw, -1.05 * S, 0.1)
    p.item("oar_flag", x + fx, z + fz, DOWNWIND, 1.0, y=by + 0.55 * S)
    p.flora("seapoppy", x - 2, z - 3, 21, 130, 75, (1.1, 1.9), clump=0.5)
    for i, (fx, fz, rad, n) in enumerate(((-1488.0, 441.0, 13, 55), (-1462.0, 444.0, 12, 45), (-1500.0, 455.0, 8, 22))):
        p.flora("marram", fx, fz, rad, n, 80 + i, (0.95, 1.6), clump=0.4)
    for (fx, fz, a, s) in ((x - 6.4, z + 3.4, 0.4, 1.35), (x + 7.4, z + 4.2, 2.3, 1.15), (x + 1.6, z - 6.2, 4.0, 1.5), (x + 17.0, z + 15.0, 5.2, 1.05)):
        p.item("glass_floats", fx, fz, a, s, dy=-0.12)
    for (fx, fz, a, s) in ((x - 9.5, z - 3.0, 0.9, 1.3), (x + 10.5, z + 8.5, 2.6, 1.1), (x - 2.0, z + 12.0, 0.2, 1.5), (x + 14.0, z - 6.0, 1.7, 0.9), (x - 18.0, z + 9.0, 3.9, 1.2)):
        p.item("driftwood", fx, fz, a, s, dy=-0.05)
    # what is left of the groyne she was moored to: a line of posts walking down into the sea
    for i in range(10):
        gx, gz = x + 12.0 + i * 0.9 + R.uniform(-0.3, 0.3), z + 6.0 + i * 3.6
        p.item("groyne_post", gx, gz, R.uniform(0, 6.28), R.uniform(0.9, 1.35), y=max(gy(gx, gz), -0.6) - R.uniform(0.15, 0.5))
    p.drift(x, by + 1.6, z, 3.5, 3.5, orange, spread=0.5)
    bx, bz = rot(yaw, 3.1 * S, 0.0)
    p.treasure("tide_knot", "The Seven-Tide Knot", "Seven tides were tied into this rope by someone who wanted the sea to stay. Nobody has dared to undo it.",
               "tide_knot", x + bx, by + 4.4, z + bz, color=[0.55, 0.85, 1.0], petals=[orange, [0.99, 0.72, 0.05], [0.97, 0.96, 0.90]])
    p.clear(x, z, 15, 0.0, 0.0)
    return p


# =====================================================================================
def clock_meadow():
    """A green nose of land in the western meadows where the dandelions have grown into giants
    around an old sundial, inside a ring of hour stones."""
    x, z = -1243.0, -372.0
    p = Place("clock_meadow", "The Clock Meadow", "In the Westbowl the dandelions have grown taller than a rider, and they still keep the time.", x, z, 46)
    R = p.rnd
    yaw = yaw_to(0.0, -1.0)                                             # the gnomon rises toward the north
    S = 1.3
    base = gy(x, z) - 0.55
    p.item("sundial", x, z, yaw, S, y=base)
    for hr in range(12):
        a = hr / 12 * math.tau
        sx, sz = x + math.sin(a) * 16.0, z - math.cos(a) * 16.0
        p.item("menhir", sx, sz, R.uniform(0, 6.28), (0.9 if hr == 0 else 0.72 if hr % 3 == 0 else R.uniform(0.5, 0.6)), dy=-0.2)
    white = [1.0, 1.0, 0.96]
    shed = {"color": white, "kind": "fluff", "height": 2.4, "reach": 3.4}
    p.flora("dandelion_clock", x, z, 34, 60, 90, (0.85, 1.85), inner=6.5, clump=0.25, shed=shed)
    p.flora("dandelion_half", x + 3, z + 2, 31, 18, 91, (0.85, 1.6), inner=7.0, shed=shed)
    p.flora("dandelion_bloom", x - 2, z + 1, 31, 28, 92, (0.8, 1.5), inner=6.0, clump=0.25)
    p.drift(x, base + 4.4, z, 20, 7, white, kind="fluff", spread=2.2)
    gx, gz = rot(yaw, 1.0 * S, -0.18 * S)
    p.treasure("lost_hour", "The Hour That Got Away", "A brass hourglass whose sand runs upward, very slowly. Nobody has ever seen it finish.",
               "hourglass", x + gx, base + 5.5 * S + 2.3, z + gz, color=[1.0, 0.84, 0.45], petals=[[0.99, 0.72, 0.05], white, [0.98, 0.90, 0.30]])
    p.clear(x, z, 7, 0.5, 0.3)
    return p


# =====================================================================================
def open_hand():
    """On the western cliffs, all that is left of a giant: one hand, held out to the sea, in a drift of red lilies."""
    x, z = -2082.0, -236.0
    p = Place("open_hand", "The Open Hand", "On the western cliffs a hand of stone is still held out to the sea.", x, z, 40)
    R = p.rnd
    yaw, S = 3.0, 1.6
    base = gy(x, z) - 0.6
    p.item("stone_hand", x, z, yaw, S, y=base)
    p.flora("spiderlily", x, z, 14.0, 240, 100, (1.0, 1.8), inner=5.2, clump=0.3)
    p.flora("spiderlily", x + 20, z + 14, 10.5, 125, 101, (1.0, 1.7), clump=0.6)
    p.flora("spiderlily", x + 7, z + 27, 9.0, 85, 102, (1.0, 1.7), clump=0.6)
    p.flora("spiderlily", x + 30, z + 30, 8.0, 55, 104, (0.95, 1.6), clump=0.7)
    p.flora("moss", x, z, 10.0, 46, 103, (0.8, 1.8), inner=4.2)
    for (bx, bz, a, s) in ((x + 7.5, z + 5.0, 1.1, 0.42), (x + 10.0, z - 5.5, 5.0, 0.36)):
        p.item("boulders", bx, bz, a, s, dy=-0.2)
    # what else is left of the giant: stumps of the same grey stone, leaning, sunk to the shoulder in the turf
    for (bx, bz, a, s, lean, dy) in ((x + 12.5, z + 9.5, 0.6, 0.9, 0.34, -1.9), (x + 4.0, z + 14.5, 2.4, 0.7, 0.46, -1.7), (x + 16.5, z - 1.0, 4.1, 0.6, 0.30, -1.5), (x + 9.5, z + 18.0, 1.3, 0.75, 0.40, -2.0), (x - 6.5, z + 12.0, 5.2, 0.55, 0.50, -1.3)):
        p.item("menhir", bx, bz, a, s, dy=dy, rot=[lean, 0.0, 0.0])
    cx, cz = rot(yaw, -0.1 * S, -1.9 * S)
    p.treasure("storm_marble", "The Storm Marble", "A glass marble with a thunderstorm the size of a thumbnail inside. The giant lost the game and kept the prize.",
               "storm_marble", x + cx, base + 6.4 * S, z + cz, color=[0.72, 0.62, 1.0], petals=[[0.90, 0.07, 0.035], [0.98, 0.20, 0.08], [0.72, 0.62, 1.0]])
    p.clear(x, z, 16, 0.6, 0.0)
    p.clear(x + 20, z + 14, 12, 0.7, 0.0)
    p.clear(x + 7, z + 27, 11, 0.7, 0.0)
    p.clear(x + 30, z + 30, 10, 0.7, 0.0)
    return p


if __name__ == "__main__":
    places = [f().d for f in (blossom_sister, farewell_bridge, shipless_mast, marigold_wreck, clock_meadow, open_hand)]
    out = os.path.join(ROOT, "assets", "places", "west.json")
    with open(out, "w") as f:
        json.dump({"places": places}, f, indent=1)
    for d in places:
        n_items = len(d["items"]); n_fl = sum(f["count"] for f in d["flora"])
        size = sum(os.path.getsize(os.path.join(ROOT, "assets", "places", v)) for v in d["models"].values() if not v.startswith(".."))
        tris = lambda m: json.load(open(os.path.join(ROOT, "assets", "places", os.path.splitext(d["models"][m])[0] + ".json")))["tris"]
        t_items = sum(tris(i["model"]) for i in d["items"]) + tris(d["treasure"]["model"])
        t_flora = sum(tris(f["model"]) * f["count"] for f in d["flora"])
        print(f'{d["id"]:16s} pos {d["pos"]} items {n_items:3d} plants {n_fl:4d} models {len(d["models"]):2d} assets {size / 1e6:.2f} MB  triangles: pieces {t_items / 1000:.0f}k + plants (all, close up) {t_flora / 1000:.0f}k')
    print("wrote", out)
