#!/usr/bin/env python3
# The six hidden places in the east of the island: where every piece stands.
# Reads the baked heightfield, writes assets/places/east.json (schema: src/world/places.js).
# Usage: tools/.venv/bin/python tools/blender/place_east_layout.py [--check]
# Plain Python + numpy; place_east_flora.py and place_east_scene.py import it from Blender too.
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PLACES = os.path.join(ROOT, "assets", "places")
MODELS = os.path.join(PLACES, "models")


class Terrain:
    def __init__(self):
        d = os.path.join(ROOT, "assets", "terrain")
        self.meta = m = json.load(open(os.path.join(d, "meta.json")))
        self.n, self.cell, self.half = m["n"], m["cell"], m["world"] / 2
        q = np.fromfile(os.path.join(d, "height.u16"), dtype="<u2").reshape(self.n, self.n)
        self.H = m["hMin"] + q.astype(np.float32) * ((m["hMax"] - m["hMin"]) / 65535)

    def h(self, x, z):
        """Bilinear height, the same sample the game takes (terrain.js heightAt)."""
        n = self.n
        fx = np.clip((np.asarray(x, np.float64) + self.half) / self.cell - 0.5, 0, n - 1.001)
        fz = np.clip((np.asarray(z, np.float64) + self.half) / self.cell - 0.5, 0, n - 1.001)
        ix = fx.astype(int); iz = fz.astype(int); tx = fx - ix; tz = fz - iz
        H = self.H
        a = H[iz, ix]; b = H[iz, ix + 1]; c = H[iz + 1, ix]; d = H[iz + 1, ix + 1]
        v = (a + (b - a) * tx) * (1 - tz) + (c + (d - c) * tx) * tz
        return float(v) if np.ndim(v) == 0 else v

    def downhill(self, x, z, span=3.0):
        gx = self.h(x + span, z) - self.h(x - span, z); gz = self.h(x, z + span) - self.h(x, z - span)
        l = math.hypot(gx, gz) or 1.0
        return -gx / l, -gz / l, l / (2 * span)


T = Terrain()
WIND = (0.361, 0.933)                      # the prevailing wind blows toward the south-south-east


def sidecar(name):
    try:
        return json.load(open(os.path.join(MODELS, f"east_{name}.json")))
    except FileNotFoundError:
        return {}


def yaw_to(model_dir, world_dir):
    """Yaw (about +y, as places.js applies it) that turns a direction in the model's xz onto one in the world's."""
    return round(math.atan2(model_dir[1], model_dir[0]) - math.atan2(world_dir[1], world_dir[0]), 4)


def turn(v, yaw):
    """Model xz -> world xz offset under a yaw."""
    c, s = math.cos(yaw), math.sin(yaw)
    return v[0] * c + v[1] * s, -v[0] * s + v[1] * c


def r3(v): return [round(float(a), 2) for a in v]


class Place:
    def __init__(self, id, name, hint, x, z, radius):
        self.d = {"id": id, "name": name, "hint": hint, "pos": r3((x, T.h(x, z), z)), "radius": radius,
                  "models": {}, "items": [], "flora": [], "treasure": None, "clear": []}

    def model(self, key):
        self.d["models"].setdefault(key, f"models/east_{key}.glb")
        return key

    def item(self, key, x, z, yaw=0.0, scale=1.0, dy=0.0, y=None, **extra):
        it = {"model": self.model(key), "pos": r3((x, (T.h(x, z) + dy) if y is None else y, z)), "yaw": round(float(yaw), 4), "scale": scale}
        it.update(extra)
        self.d["items"].append(it)
        return it

    def flora(self, key, x, z, radius, count, seed, scale=(0.8, 1.2), **extra):
        f = {"model": self.model(key), "center": [round(x, 2), round(z, 2)], "radius": radius, "count": int(count), "seed": seed, "scale": list(scale)}
        f.update(extra)
        self.d["flora"].append(f)
        return f

    def treasure(self, id, name, lore, key, x, y, z, **extra):
        t = {"id": id, "name": name, "lore": lore, "model": self.model(key), "pos": r3((x, y, z))}
        t.update(extra)
        self.d["treasure"] = t

    def clear(self, x, z, r, grass, flowers):
        self.d["clear"].append({"x": round(x, 1), "z": round(z, 1), "r": r, "grass": grass, "flowers": flowers})

    def drift(self, **d):
        self.d.setdefault("drift", []).append(d)


# =========================================================================================
# 1. The Thousand-Wish Pine: a shelf on the mountain's west shoulder, at the lip of the bluff
# =========================================================================================
PINE = dict(x=699.5, z=49.5, yaw=yaw_to((1, 0), WIND), dy=-0.35)    # the long low limb (model +x) streams downwind, along the lip
PINE_POLES = [(706.0, 41.0), (711.8, 45.6), (713.4, 52.6), (709.0, 60.6), (701.6, 62.4)]


def charms_spec():
    """The wish lines and paper strips, in the pine's own model space (x, y up, z) so that one item
    placed exactly like the pine carries them all. Used by place_east_flora.py."""
    y0 = T.h(PINE["x"], PINE["z"]) + PINE["dy"]
    yaw = PINE["yaw"]
    lines = []
    for wx, wz in PINE_POLES:
        mx, mz = turn((wx - PINE["x"], wz - PINE["z"]), -yaw)
        lines.append({"pole": [round(mx, 3), round(T.h(wx, wz) - y0, 3), round(mz, 3)]})
    # where strips can hang: the undersides of the limb and the needle pads, from the pine's own columns
    sc = sidecar("pine")
    cand = [(cx, y, cz) for cx, cz, r, y, y1 in sc.get("slabs", []) if 3.2 < y < 9.5 and math.hypot(cx, cz) > 2.4]
    picks = []
    if cand:
        picks = [max(cand, key=lambda c: math.hypot(c[0], c[2]))]
        while len(picks) < min(18, len(cand)):
            best = max(cand, key=lambda c: min((c[0] - q[0]) ** 2 + (c[1] - q[1]) ** 2 * 0.3 + (c[2] - q[2]) ** 2 for q in picks))
            picks.append(best)
    # where the trunk is at the height the lines are tied
    tie = 3.4
    near = [(cx, cz) for cx, cz, r, y, y1 in sc.get("slabs", []) if y <= tie <= y1 and math.hypot(cx, cz) < 2.2]
    trunk = [round(sum(c[0] for c in near) / len(near), 3), tie, round(sum(c[1] for c in near) / len(near), 3)] if near else [0.0, tie, 0.0]
    return {"lines": lines, "hang": [[round(v, 3) for v in q] for q in picks], "height": sc.get("height", 12.5), "trunk": trunk}


def wish_pine():
    p = Place("wish_pine", "The Thousand-Wish Pine",
              "High on the mountain's western shoulder, something flutters that is not leaves.", 704.0, 50.0, 38)
    px, pz, yaw = PINE["x"], PINE["z"], PINE["yaw"]
    p.item("pine", px, pz, yaw, 1.0, dy=PINE["dy"])
    p.item("charms", px, pz, yaw, 1.0, dy=PINE["dy"])
    p.item("cairn", 710.2, 55.6, yaw_to((0, 1), (-1, -0.45)), 1.0, dy=-0.14)
    # wayfarers' cairns along the rim of the shelf
    for i, (x, z, sc) in enumerate(((703.5, 35.4, 1.7), (695.6, 42.6, 1.0), (713.0, 40.6, 1.25), (719.5, 48.5, 0.9), (717.0, 59.0, 1.35),
                                    (705.0, 66.0, 1.0), (694.6, 57.4, 0.85), (724.5, 42.5, 1.1), (690.5, 34.5, 0.8))):
        p.item("cairnlet", x, z, 0.7 + i * 1.9, sc, dy=-0.06)
    p.treasure("windwrights_bell", "The Windwright's Bell",
               "A thumb-worn bronze bell with no clapper. The pine rings it anyway, on nights when the wind changes its mind.",
               "bell", 692.4, T.h(694.6, 52.0) + 3.4, 52.6, color=[1.0, 0.84, 0.48], scale=1.4,
               petals=[[0.97, 0.96, 0.90], [0.86, 0.22, 0.16], [1.0, 0.84, 0.48]])
    p.flora("cushion", 708.0, 50.0, 17, 120, 1, (0.6, 1.6), clump=0.3)
    p.flora("skybell", 708.0, 50.0, 18, 560, 2, (0.9, 1.7), clump=0.45)
    p.flora("skybell", 727.0, 44.0, 9, 110, 22, (0.9, 1.6), clump=0.5)
    # thinner and wider, so the shelf reads as a garden and not a bare ledge
    p.flora("cushion", 714.0, 50.0, 31, 80, 23, (0.7, 1.9), inner=16, clump=0.5)
    p.flora("skybell", 714.0, 50.0, 33, 300, 24, (0.9, 1.7), inner=17, clump=0.6)
    # waymarks on the way up from the green
    for i, (x, z, sc) in enumerate(((729.5, 52.0, 0.8), (737.0, 47.0, 0.7), (746.5, 43.0, 0.9), (757.5, 40.0, 0.75))):
        p.item("cairnlet", x, z, 2.2 + i * 1.3, sc, dy=-0.08)
    return p


# =========================================================================================
# 2. The Kettle Pools: a hot spring spilling down a fold of the eastern foothills
# =========================================================================================
def kettle_pools():
    p = Place("kettle_pools", "The Kettle Pools",
              "In a green fold of the eastern foothills the hillside keeps a staircase of warm blue water.", 1489.0, -113.0, 42)
    cx, cz = 1484.0, -120.0
    dx, dz, slope = T.downhill(cx, cz, 6.0)
    yaw = yaw_to((0, 1), (dx, dz))           # the cascade (model +z) runs downhill
    front = (cx + dx * 6.5, cz + dz * 6.5)
    y = T.h(*front) - 0.2
    p.item("pools", cx, cz, yaw, 1.0, y=y)
    tx, tz = 1497.2, -122.4
    p.item("emberleaf", tx, tz, yaw_to((1, 0), WIND), 1.0, dy=-0.12)
    # stepping stones up from the low side to the rim of the first pool, and the pail left there
    a = (1503.5, -102.5); b = (front[0] + 3.2, front[1] + 2.6)
    n = 9
    for i in range(n):
        t = i / (n - 1)
        bend = math.sin(t * math.pi) * 2.2
        x = a[0] + (b[0] - a[0]) * t + dz * bend; z = a[1] + (b[1] - a[1]) * t - dx * bend
        p.item("stepstone", x, z, 0.9 * i + 0.3, 0.95 + 0.25 * ((i * 7) % 3) / 2, dy=0.02)
    p.item("bucket", b[0] - 1.3, b[1] + 0.9, 2.1, 1.35, dy=0.0)
    top = (cx - dx * 4.4, cz - dz * 4.4)
    hmod = sidecar("pools").get("height", 6.3)
    p.treasure("ember_egg", "The Ember Egg",
               "A river stone that has never once gone cold. Shepherds carried it in their coats through seven winters and argued over whose turn it was.",
               "emberstone", top[0], y + hmod + 2.0, top[1], color=[1.0, 0.58, 0.26], scale=1.5,
               petals=[[0.90, 0.12, 0.06], [0.98, 0.42, 0.08], [1.0, 0.80, 0.40]])
    p.flora("plume", cx + dx * 1.5, cz + dz * 1.5, 17.5, 150, 3, (0.8, 1.3), inner=10.8, clump=0.25, shed={"color": [1.0, 0.96, 0.85], "kind": "fluff"})
    p.flora("embermoss", cx + dx * 2.5, cz + dz * 2.5, 15.5, 190, 4, (0.8, 1.9), inner=9.2, clump=0.3)
    # warm air lifting specks of mineral off the water; the tree letting go of a leaf now and then
    p.drift(**{"from": r3((cx - dx * 1.5, y + hmod * 0.75, cz - dz * 1.5)), "radius": 4.5, "rate": 5, "color": [0.92, 0.97, 1.0], "kind": "fluff", "spread": 1.5})
    p.drift(**{"from": r3((tx + WIND[0] * 1.5, T.h(tx, tz) + 6.6, tz + WIND[1] * 1.5)), "radius": 4.2, "rate": 2.2, "color": [0.86, 0.13, 0.05], "kind": "petal"})
    p.clear(cx + dx * 1.0, cz + dz * 1.0, 13, 0.3, 0)
    p.clear((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 5, 0.5, 0.2)
    return p


# =========================================================================================
# 3. Starfall: where a star clipped the cliff's edge and came to rest in the cosmos field
# =========================================================================================
def starfall():
    p = Place("starfall", "Starfall",
              "Something fell on the north-east meadow long ago. It took a bite out of the cliff on the way in.", 1322.0, -1048.0, 46)
    mx, mz = 1316.0, -1046.0
    p.item("meteor", mx, mz, 0.6, 1.0)
    # a crown of star-glass thrown up around it, every blade leaning away from the blow
    n = 9
    for i in range(n):
        phi = math.tau * i / n + 0.35 * math.sin(i * 2.3)
        r = 5.6 + 1.3 * math.sin(i * 1.7 + 1.0)
        x, z = mx + math.cos(phi) * r, mz + math.sin(phi) * r
        p.item("starglass", x, z, -phi, round(0.72 + 0.5 * (0.5 + 0.5 * math.sin(i * 3.1)), 2), dy=-0.1, rot=[0.0, 0.0, round(-(0.32 + 0.22 * math.sin(i * 1.3) ** 2), 3)])
    # the furrow it ploughed from the bite in the cliff
    nx0, nz0 = 1351.0, -1055.6
    L = math.hypot(nx0 - mx, nz0 - mz); ux, uz = (nx0 - mx) / L, (nz0 - mz) / L
    k = 0
    d = 9.0
    while d < L - 1.0:
        x, z = mx + ux * d, mz + uz * d
        p.flora("scorchgrass", x, z, 2.7, 46, 30 + k, (0.7, 1.4))
        if k % 2 == 0: p.flora("shard", x, z, 2.4, 3, 60 + k, (0.6, 1.3))
        if k % 3 == 1:
            phi = math.atan2(uz, ux)
            p.item("starglass", x - uz * 1.4, z + ux * 1.4, -phi, 0.5 + 0.1 * (k % 4), dy=-0.25, rot=[0.0, 0.0, -0.75])
        p.clear(x, z, 3.2, 0.3, 0)
        d += 4.4; k += 1
    p.flora("scorchgrass", mx, mz, 13.5, 950, 5, (0.8, 1.6), inner=4.6)
    p.flora("shard", mx, mz, 9.0, 40, 6, (0.6, 1.5), inner=4.4)
    p.flora("glasslily", mx, mz, 25.0, 760, 7, (0.8, 1.35), inner=10.5, clump=0.35)
    p.flora("cinder", mx, mz, 26, 20, 8, (0.6, 1.7), inner=6)
    nx, nz = 1361.0, -1057.5                  # down in the notch the star cut
    p.treasure("sky_splinter", "The Sky Splinter",
               "A sliver of the star that fell here. Hold it to your ear and it is still humming the note it made coming down.",
               "splinter", nx, T.h(nx, nz) + 3.2, nz, color=[0.62, 0.90, 1.0], scale=1.5,
               petals=[[0.72, 0.92, 1.0], [0.97, 0.97, 1.0], [0.30, 0.62, 0.95]])
    p.drift(**{"from": r3((mx, T.h(mx, mz) + 3.6, mz)), "radius": 2.6, "rate": 3, "color": [0.62, 0.90, 1.0], "kind": "fluff", "spread": 1.6})
    p.clear(mx, mz, 14.5, 0.22, 0)
    return p


# =========================================================================================
# 4. The Conch Garden: the eastern sand cay, planted in a spiral like the shell at its heart
# =========================================================================================
def conch_garden():
    p = Place("conch_garden", "The Conch Garden",
              "The smallest island keeps the largest shell, and somebody has been gardening around it.", 562.0, 1699.0, 48)
    cx, cz = 560.5, 1698.0
    p.item("conch", cx, cz, 3.3, 1.0)
    # the spiral: beds of air coral, anemone and sea fan, opening out from the shell
    th0, turns = 0.9, 2.15
    th1 = th0 + turns * math.tau
    def spiral(th):
        t = (th - th0) / (th1 - th0)
        a = 8.0 + 27.0 * t ** 0.92
        return cx + 1.5 + a * math.cos(th), cz + 0.5 + 0.60 * a * math.sin(th), a
    kinds = ["coralbush", "anemone", "seafan"]
    th = th0; k = 0; heroes = 0
    while th < th1:
        x, z, a = spiral(th)
        if T.h(x, z) > 0.55:
            kind = kinds[k % 3]
            if k % 9 == 4 and heroes < 6:
                p.item("coral", x, z, 0.9 * k, round(0.62 + 0.09 * (k % 5), 2), dy=-0.12); heroes += 1
            else:
                n, sc = {"coralbush": (11, (1.2, 2.4)), "anemone": (13, (1.1, 2.0)), "seafan": (8, (1.1, 2.0))}[kind]
                p.flora(kind, x, z, 2.3, n, 100 + k, sc)
            if k % 3 == 0: p.flora("scallop", x, z, 3.8, 10, 200 + k, (0.8, 1.7), inner=2.2)
        th += 3.7 / max(a * 0.8, 4.0)
        k += 1
    # the old clam at the spiral's far end keeps the pearl
    ex, ez, _ = spiral(th1 + 0.12)
    while T.h(ex, ez) < 0.9:
        ex, ez = ex + (cx - ex) * 0.06, ez + (cz - ez) * 0.06
    p.item("clam", ex, ez, yaw_to((0, 1), (cx - ex, cz - ez)), 1.0)
    p.flora("starfish", 562.0, 1699.0, 31, 70, 13, (0.9, 1.8))
    p.flora("scallop", 562.0, 1699.0, 33, 90, 12, (0.7, 1.5), inner=20)
    p.treasure("moon_pearl", "The Moon Pearl",
               "Grown over a hundred years of tides around one grain of sand that the full moon happened to be shining on.",
               "pearl", ex, T.h(ex, ez) + 2.9, ez, color=[0.92, 0.90, 1.0], scale=1.2,
               petals=[[0.98, 0.62, 0.56], [0.97, 0.96, 0.92], [0.70, 0.86, 1.0]])
    return p


# =========================================================================================
# 5. Lantern Roots: the tree that went wading into the lagoon
# =========================================================================================
MANGROVE = dict(x=702.0, z=1247.5, y=-1.2)
JETTY = [(714.4, 1240.6), (709.9, 1247.0), (707.4, 1255.6)]        # from the sand, past the roots, to the landing


def jetty_spec():
    """The boardwalk, as offsets from its corner (x east, y above the sea, z south). Used by place_east_flora.py."""
    bx, bz = JETTY[1]
    pts = []
    for (x0, z0), (x1, z1) in zip(JETTY[:-1], JETTY[1:]):
        L = math.hypot(x1 - x0, z1 - z0); n = max(int(round(L / 0.42)), 1)
        for i in range(n + (1 if (x1, z1) == JETTY[-1] else 0)):
            t = i / n
            x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
            pts.append([round(x - bx, 3), round(z - bz, 3), round(T.h(x, z), 3)])
    return {"anchor": [bx, bz], "pts": pts, "deck": 0.85}


def lantern_roots():
    p = Place("lantern_roots", "Lantern Roots",
              "One tree went wading into the lagoon and never came back. Somebody still lights its lamps.", 703.0, 1246.5, 42)
    mx, mz = MANGROVE["x"], MANGROVE["z"]
    p.item("mangrove", mx, mz, 0.9, 1.0, y=MANGROVE["y"])
    p.item("jetty", JETTY[1][0], JETTY[1][1], 0.0, 1.0, y=0.0)
    p.item("skiff", 717.6, 1238.4, yaw_to((1, 0), (0.42, -0.9)), 1.0, dy=-0.14, rot=[0.0, 0.0, 0.11])
    # lamp posts wading out along the shore either side of the tree
    for i, (x, z, yw) in enumerate(((689.6, 1240.6, 0.4), (693.6, 1245.6, 1.2), (716.6, 1255.4, 2.6), (721.4, 1258.8, 3.5), (684.6, 1237.0, 5.2))):
        p.item("moorpost", x, z, yw, 1.0, y=round(min(T.h(x, z), 0.0) - 0.75, 2))
    # the lagoon's seaward normal here
    sx, sz = -0.406, 0.914
    tx, tz = mx + sx * 8.0, mz + sz * 8.0
    p.treasure("ferrylight", "The Ferrylight",
               "The lamp of a ferry that ran before there was a town to run to. It has only ever needed lighting once.",
               "ferrylight", tx, 2.1, tz, color=[1.0, 0.76, 0.40], scale=1.35,
               petals=[[1.0, 0.55, 0.12], [1.0, 0.90, 0.66], [0.98, 0.80, 0.30]])
    # lotus stands in the shallows either side of the roots: walk the waterline and keep each bed wet
    dxs, dzs = 0.914, 0.406                   # along the shore
    i = 0
    for srun in (-25.0, -20.5, -16.0, -11.5, 14.0, 18.5, 23.0, 27.5):
        bx, bz = mx + dxs * srun, mz + dzs * srun
        t = -14.0
        while t < 14.0 and T.h(bx + sx * t, bz + sz * t) > 0.0: t += 0.25
        for off, r, n in ((3.3, 2.3, 6), (7.0, 1.9, 3)):
            lx, lz = bx + sx * (t + off), bz + sz * (t + off)
            hs = [T.h(lx + math.cos(a) * r, lz + math.sin(a) * r) for a in (0, 1.05, 2.1, 3.14, 4.2, 5.2)]
            if max(hs) < -0.08 and min(hs) > -1.75:
                p.flora("lotus", round(lx, 2), round(lz, 2), r, n, 14 + i, (1.0, 1.3), lift=0.001)
                i += 1
    p.flora("lanternberry", 705.0, 1235.5, 11, 70, 18, (0.9, 1.7), clump=0.35)
    p.drift(**{"from": r3((mx, 11.0, mz)), "radius": 6.0, "rate": 1.4, "color": [1.0, 0.93, 0.62], "kind": "petal"})
    return p


# =========================================================================================
# 6. The Whalebone Arbour: the long south-east beach
# =========================================================================================
def whalebone_arbour():
    p = Place("whalebone_arbour", "The Whalebone Arbour",
              "On the long south-east beach a great traveller rests, and thrift grows where it sang.", 1479.0, 800.0, 52)
    wx, wz = 1487.0, 791.0
    head = (-0.655, 0.756)                    # the skull (model -x) points down the beach, south-west
    yaw = yaw_to((-1, 0), head)
    p.item("whale", wx, wz, yaw, 1.0)
    p.item("driftwood", 1505.0, 794.5, 1.1, 1.0)
    p.item("driftwood", 1462.5, 806.5, 4.0, 0.7)
    # the arbour: a walk of old ribs set up as arches, leading in to the skull. Nothing here stops
    # the broom, so the line is through the arches, over the head and down the spine.
    ayaw = yaw_to((0, 1), head)
    arches = []
    for i, d in enumerate((25.0, 33.5, 42.0, 50.5)):
        ax, az = wx + head[0] * d, wz + head[1] * d
        p.item("ribarch", ax, az, round(ayaw + 0.06 * math.sin(i * 2.1), 4), round(1.0 - 0.05 * i, 2), dy=-0.05)
        arches.append((ax, az))
    # the treasure hangs inside the rib cage, under the spine: the ribs do not stop the broom (the
    # sidecar's `solid` list leaves them out), so it is taken by threading the cage from the side
    ox, oz = turn((1.6, 0.0), yaw)
    jx, jz = wx + ox, wz + oz
    p.treasure("song_bone", "The Song Bone",
               "A whale's ear-bone, sanded smooth by the tides. On a still evening it gives back the songs it heard, very slowly.",
               "songbone", jx, T.h(jx, jz) + 2.9, jz, color=[0.70, 0.90, 1.0], scale=1.5,
               petals=[[0.95, 0.40, 0.62], [1.0, 0.70, 0.82], [0.97, 0.96, 0.90]])
    # a mat of thrift under the bones, thinning into the sand, and sea-holly where it is driest
    shed = {"color": [0.96, 0.42, 0.64], "kind": "petal"}
    for i, t in enumerate((-13.5, -7.5, -1.5, 4.5, 9.5)):
        ax, az = turn((t, 0.0), yaw)
        p.flora("thrift", wx + ax, wz + az, 7.5, 230, 40 + i, (1.0, 2.0), clump=0.2, shed=shed)
    p.flora("thrift", wx, wz, 25, 420, 19, (0.8, 1.7), clump=0.5, inner=6, shed=shed)
    p.flora("seaholly", wx, wz, 26, 150, 20, (0.9, 1.7), clump=0.3)
    for i, (ax, az) in enumerate(arches):
        p.flora("thrift", ax, az, 5.2, 70, 50 + i, (0.9, 1.8), clump=0.25, shed=shed)
    p.flora("seaholly", arches[1][0], arches[1][1], 17, 60, 21, (0.9, 1.6), clump=0.35)
    return p


PLACES_FN = [wish_pine, kettle_pools, starfall, conch_garden, lantern_roots, whalebone_arbour]


def build():
    out = []
    for fn in PLACES_FN:
        p = fn().d
        if p["treasure"] is None: del p["treasure"]
        out.append(p)
    return {"places": out}


def check(data):
    """Sanity: spacing, the excluded areas, model files, and how much each place weighs."""
    ps = data["places"]
    ok = True
    for i, a in enumerate(ps):
        x, _, z = a["pos"]
        if x <= 250: print(f"!! {a['id']} is not in the east"); ok = False
        if -420 <= x <= 320 and 640 <= z <= 1180: print(f"!! {a['id']} is inside the main town"); ok = False
        if -100 <= x <= 420 and -1180 <= z <= -880: print(f"!! {a['id']} is inside the cliff village"); ok = False
        for b in ps[i + 1:]:
            d = math.hypot(x - b["pos"][0], z - b["pos"][2])
            if d < 200: print(f"!! {a['id']} and {b['id']} are only {d:.0f} m apart"); ok = False
        size = 0
        for k, path in a["models"].items():
            f = os.path.join(PLACES, path)
            if not os.path.exists(f): print(f"!! {a['id']}: missing {path}"); ok = False; continue
            size += os.path.getsize(f)
            j = f[:-4] + ".json"
            if not os.path.exists(j): print(f"!! {a['id']}: no sidecar for {path}"); ok = False
            else: size += os.path.getsize(j)
        flag = "" if size <= 3e6 else "   !! over 3 MB"
        if size > 3e6: ok = False
        print(f"{a['id']:18s} {a['name']:26s} pos {a['pos']}  {len(a['items'])} items, {len(a['flora'])} flora, {len(a['models'])} models, {size / 1e6:.2f} MB{flag}")
    return ok


if __name__ == "__main__":
    data = build()
    good = check(data)
    if "--check" not in sys.argv:
        os.makedirs(PLACES, exist_ok=True)
        with open(os.path.join(PLACES, "east.json"), "w") as f:
            json.dump(data, f, indent=1)
        print("wrote assets/places/east.json")
    sys.exit(0 if good else 1)
