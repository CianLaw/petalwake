#!/usr/bin/env python3
"""Pack the modelled buildings into what the game loads.

    tools/.venv/bin/python tools/town/assemble.py [layout.json]

Reads assets/town/layout.json (which building stands where: tools/town/layout.py writes it) and
the built models in art/town/build/*.npz, seats every building on the terrain, and writes, per
town:
    assets/town/<town>.bin    chunked, quantised geometry + the collision height grids
    assets/town/<town>.json   chunk table, landing pads, chimneys, lamps, turning parts, bounds
and assets/town/index.json listing the towns.

World frame: +x east, +y up, +z south. A building's `yaw` is the compass direction its front
faces, in degrees (0 = north, 90 = east), the same convention as the broom's heading.
"""
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILD = os.path.join(ROOT, "art", "town", "build")
OUT = os.path.join(ROOT, "assets", "town")
CHUNK = 56.0            # metres: buildings are grouped on a grid of this size
MAXV = 65000            # vertices per chunk (16-bit indices)
SOLID_CELL = 0.5
SOLID_STEP = 0.05       # metres per unit of the collision grid
NO_SOLID = {"cloth", "ivy", "glow", "paint", "glass", "water"}

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MATS = ["masonry", "ashlar", "plaster", "timber", "planks", "slate", "tiles", "thatch", "shingle",
        "brick", "cobble", "flagstone", "ivy", "metal", "glass", "cloth", "paint", "glow", "water"]


class Terrain:
    def __init__(self):
        m = json.load(open(os.path.join(ROOT, "assets", "terrain", "meta.json")))
        self.n, self.cell, self.half = m["n"], m["cell"], m["world"] / 2
        h = np.fromfile(os.path.join(ROOT, "assets", "terrain", "height.u16"), dtype="<u2").reshape(self.n, self.n).astype(np.float32)
        self.h = m["hMin"] + (m["hMax"] - m["hMin"]) * h / 65535.0

    def at(self, x, z):
        fx = (np.asarray(x, np.float64) + self.half) / self.cell - 0.5
        fz = (np.asarray(z, np.float64) + self.half) / self.cell - 0.5
        ix = np.clip(np.floor(fx).astype(int), 0, self.n - 2); iz = np.clip(np.floor(fz).astype(int), 0, self.n - 2)
        tx = np.clip(fx - ix, 0, 1); tz = np.clip(fz - iz, 0, 1)
        h = self.h
        return (h[iz, ix] * (1 - tx) + h[iz, ix + 1] * tx) * (1 - tz) + (h[iz + 1, ix] * (1 - tx) + h[iz + 1, ix + 1] * tx) * tz


_cache = {}


def load(bid):
    if bid not in _cache:
        a = dict(np.load(os.path.join(BUILD, bid + ".npz")))
        info = json.load(open(os.path.join(BUILD, bid + ".json")))
        _cache[bid] = (a, info)
    return _cache[bid]


def xform(p, x, y, z, yaw, s=1.0):
    """Building frame (x right, y back, z up) -> world. yaw in degrees."""
    c, sn = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    out = np.empty_like(p, dtype=np.float64)
    out[:, 0] = x + s * (-p[:, 0] * c - p[:, 1] * sn)
    out[:, 2] = z + s * (-p[:, 0] * sn + p[:, 1] * c)
    out[:, 1] = y + s * p[:, 2]
    return out


def xdir(n, yaw):
    c, sn = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    out = np.empty_like(n, dtype=np.float64)
    out[:, 0] = -n[:, 0] * c - n[:, 1] * sn
    out[:, 2] = -n[:, 0] * sn + n[:, 1] * c
    out[:, 1] = n[:, 2]
    return out


def pack_mesh(pos, nrm, uv, col, mat, wind, ao, tris_by_lod, blob, seed=0):
    """Quantise one mesh and append it to the binary. tris_by_lod = [far, mid, near] index arrays."""
    lo, hi = pos.min(0), pos.max(0)
    ctr = (lo + hi) / 2
    ext = np.maximum((hi - lo) / 2, 1e-3)
    q = np.round((pos - ctr) / ext * 32767).astype(np.int16)
    w = (mat.astype(np.int32) + 32 * np.round(wind.astype(np.float32) / 255 * 31).astype(np.int32)).astype(np.int16)
    P = np.concatenate([q, w[:, None]], 1).astype("<i2")
    N = np.concatenate([np.round(np.clip(nrm, -1, 1) * 127).astype(np.int8), np.round(ao.astype(np.float32) / 255 * 127).astype(np.int8)[:, None]], 1)
    if np.abs(uv).max() * 256 > 32760:
        uv = uv - np.floor(uv.mean(0) / 16) * 16
    T = np.round(np.clip(uv * 256, -32767, 32767)).astype("<i2")
    Cc = col.astype(np.uint8)
    idx = np.concatenate(tris_by_lod).astype("<u2" if len(pos) <= 65535 else "<u4")
    counts = np.cumsum([len(t) for t in tris_by_lod]).tolist()

    def put(arr):
        off = len(blob)
        b = arr.tobytes()
        blob.extend(b)
        while len(blob) % 4:
            blob.append(0)
        return off

    return {"center": [round(float(v), 4) for v in ctr], "extent": [round(float(v), 5) for v in ext],
            "aabb": [round(float(v), 3) for v in lo] + [round(float(v), 3) for v in hi],
            "verts": int(len(pos)), "index": counts, "index32": bool(len(pos) > 65535),
            "pos": put(P), "nrm": put(N), "uv": put(T), "col": put(Cc), "idx": put(idx)}


def tri_samples(P, step):
    """Points sprinkled over triangles (n, 3, 3) about `step` apart."""
    e = np.maximum(np.linalg.norm(P[:, 1] - P[:, 0], axis=1), np.linalg.norm(P[:, 2] - P[:, 0], axis=1))
    out = []
    ns = np.clip(np.ceil(e / step).astype(int), 1, 80)
    for n in np.unique(ns):
        sel = P[ns == n]
        i, j = np.meshgrid(np.arange(n + 1), np.arange(n + 1), indexing="ij")
        ok = (i + j) <= n
        u = (i[ok] / n)[None, :, None]; v = (j[ok] / n)[None, :, None]
        pts = sel[:, None, 0] * (1 - u - v) + sel[:, None, 1] * u + sel[:, None, 2] * v
        out.append(pts.reshape(-1, 3))
    return np.concatenate(out) if out else np.zeros((0, 3))


def assemble_town(town, terrain):
    tid = town["id"]
    blob = bytearray()
    placed = []
    missing = []
    pads, smokes, lamps, spinners, buildings, floaters = [], [], [], [], [], []
    for k, it in enumerate(town["items"]):
        bid = it["id"]
        try:
            a, info = load(bid)
        except FileNotFoundError:
            # STANDIN=1: while the modellers are still at work, fill missing lots with models that exist
            pool = sorted(os.path.splitext(os.path.basename(f))[0] for f in os.listdir(BUILD) if f.endswith(".npz") and not f.startswith(("_", "p_")))
            if not os.environ.get("STANDIN") or not pool or bid.startswith("p_"):
                missing.append(bid)
                continue
            a, info = load(pool[(k * 7 + len(bid)) % len(pool)])
        x, z, yaw, s = it["x"], it["z"], it.get("yaw", 0.0), it.get("scale", 1.0)
        if it.get("float") or info.get("float"):
            # a boat: its own little mesh about its waterline, for the game to rock on the swell
            lod = a["lod"]
            idx = a["idx"].astype(np.int64)
            m = pack_mesh(xform(a["pos"], 0, 0, 0, yaw, s), xdir(a["nrm"], yaw), a["uv"] * s, a["col"], a["mat"], a["wind"], a["ao"],
                          [idx[:lod[0] * 3], idx[lod[0] * 3:lod[1] * 3], idx[lod[1] * 3:lod[2] * 3]], blob)
            m.update({"x": x, "z": z, "draft": it.get("sink", 0.0), "id": bid})          # (models float with their water line at z = 0)
            floaters.append(m)
            continue
        y = it["y"] if "y" in it else float(terrain.at(x, z)) + it.get("lift", 0.0)
        pos = xform(a["pos"], x, y, z, yaw, s)
        nrm = xdir(a["nrm"], yaw)
        lod = a["lod"]
        idx = a["idx"].astype(np.int64)
        placed.append(dict(pos=pos, nrm=nrm, uv=a["uv"] * s, col=a["col"], mat=a["mat"], wind=a["wind"], ao=a["ao"],
                           tris=[idx[:lod[0] * 3], idx[lod[0] * 3:lod[1] * 3], idx[lod[1] * 3:lod[2] * 3]], cx=x, cz=z, id=bid))
        name = it.get("name") or info.get("name") or bid
        buildings.append({"id": bid, "name": name, "pos": [round(x, 2), round(y, 2), round(z, 2)], "yaw": yaw, "kind": info.get("kind", "house"),
                          "top": round(float(pos[:, 1].max()), 2)})
        for j, p in enumerate(info.get("pads", [])):
            wp = xform(np.array([p["pos"]]), x, y, z, yaw, s)[0]
            pname = p.get("name")
            pads.append({"id": f"{tid}:{bid}:{k}:{j}", "name": name if not pname else f"{name}", "spot": pname or "", "town": tid, "building": bid,
                         "pos": [round(float(v), 3) for v in wp], "radius": round(p["radius"] * s, 2),
                         "yaw": round(math.radians((yaw - p["face"]) % 360.0), 4), "approach": round(math.radians((yaw - p["approach"]) % 360.0), 4),
                         "ground": round(y, 2)})
        for key, lst in (("smokes", smokes), ("lamps", lamps)):
            for p in info.get(key, []):
                wp = xform(np.array([p["pos"]]), x, y, z, yaw, s)[0]
                lst.append({"pos": [round(float(v), 2) for v in wp], "strength": p.get("strength", 1.0)})
        for j, sp in enumerate(info.get("spinners", [])):
            pre = f"spin{j + 1}_"
            if pre + "pos" not in a:
                continue
            piv = xform(np.array([sp["pivot"]]), x, y, z, yaw, s)[0]
            ax = xdir(np.array([sp["axis"]]), yaw)[0]
            spos = xform(a[pre + "pos"], x, y, z, yaw, s) - piv
            slod = a[pre + "lod"]
            sidx = a[pre + "idx"].astype(np.int64)
            m = pack_mesh(spos, xdir(a[pre + "nrm"], yaw), a[pre + "uv"] * s, a[pre + "col"], a[pre + "mat"], a[pre + "wind"], a[pre + "ao"],
                          [sidx[:slod[0] * 3], sidx[slod[0] * 3:slod[1] * 3], sidx[slod[1] * 3:slod[2] * 3]], blob)
            m.update({"pivot": [round(float(v), 3) for v in piv], "axis": [round(float(v), 4) for v in ax], "speed": sp["speed"], "wind": sp.get("wind", True)})
            spinners.append(m)
    if missing:
        print(f"  {tid}: {len(missing)} not built yet")
    if not placed:
        return None

    # ---- chunks: buildings grouped on a grid, split so each stays under the 16-bit vertex limit
    groups = {}
    for p in placed:
        groups.setdefault((int(math.floor(p["cx"] / CHUNK)), int(math.floor(p["cz"] / CHUNK))), []).append(p)
    chunks = []
    for key in sorted(groups):
        bucket, nv = [], 0
        packs = []
        for p in sorted(groups[key], key=lambda q: -len(q["pos"])):
            if bucket and nv + len(p["pos"]) > MAXV:
                packs.append(bucket); bucket, nv = [], 0
            bucket.append(p); nv += len(p["pos"])
        if bucket:
            packs.append(bucket)
        for bucket in packs:
            off = 0
            tr = [[], [], []]
            for p in bucket:
                for l in range(3):
                    tr[l].append(p["tris"][l] + off)
                off += len(p["pos"])
            cat = lambda k: np.concatenate([p[k] for p in bucket])
            m = pack_mesh(cat("pos"), cat("nrm"), cat("uv"), cat("col"), cat("mat"), cat("wind"), cat("ao"), [np.concatenate(t) for t in tr], blob)
            m["buildings"] = [p["id"] for p in bucket]
            chunks.append(m)

    # ---- collision: top-down height grids of the structure (detail level 0, hard materials only),
    # one per group of neighbours so that lone farms do not cost a grid the size of the island
    allp = np.concatenate([p["pos"] for p in placed])
    hard = np.array([m not in NO_SOLID for m in MATS])
    solids = []
    clusters = {}
    for p in placed:
        clusters.setdefault((int(math.floor(p["cx"] / 112.0)), int(math.floor(p["cz"] / 112.0))), []).append(p)
    for key in sorted(clusters):
        grp = clusters[key]
        gp = np.concatenate([p["pos"] for p in grp])
        x0, z0 = math.floor(gp[:, 0].min() - 2), math.floor(gp[:, 2].min() - 2)
        x1, z1 = math.ceil(gp[:, 0].max() + 2), math.ceil(gp[:, 2].max() + 2)
        nx, nz = int((x1 - x0) / SOLID_CELL), int((z1 - z0) / SOLID_CELL)
        grid = np.full(nz * nx, -1e9, np.float32)
        for p in grp:
            t = p["tris"][0].reshape(-1, 3)
            if not len(t):
                continue
            t = t[hard[p["mat"][t[:, 0]]]]
            pts = tri_samples(p["pos"][t], SOLID_CELL * 0.45)
            # a landing place, and the last few metres of the way in to it, are open to the broom: whatever
            # hangs over them (an eave, a roof on posts) is not solid
            for pd in pads:
                c = np.array(pd["pos"])
                if abs(c[0] - p["cx"]) > 40 or abs(c[2] - p["cz"]) > 40:
                    continue
                d = np.array([math.sin(pd["approach"]), -math.cos(pd["approach"])])      # the way she travels on the final approach
                rel = pts[:, [0, 2]] - c[[0, 2]]
                along = np.clip(-(rel @ d), 0.0, 3.5)                                       # back along the way she came
                dist = np.linalg.norm(rel + along[:, None] * d, axis=1)
                over = (dist < pd["radius"] + 0.9) & (pts[:, 1] > c[1] + 0.45)
                if over.any():
                    pts = pts[~over]
            ix = ((pts[:, 0] - x0) / SOLID_CELL).astype(int); iz = ((pts[:, 2] - z0) / SOLID_CELL).astype(int)
            ok = (ix >= 0) & (iz >= 0) & (ix < nx) & (iz < nz)
            np.maximum.at(grid, iz[ok] * nx + ix[ok], pts[ok, 1].astype(np.float32))
        ybase = float(np.floor(gp[:, 1].min() - 4))
        g16 = np.where(grid < -1e8, 0, np.clip(np.round((grid - ybase) / SOLID_STEP), 1, 65535)).astype("<u2")
        off = len(blob)
        blob.extend(g16.tobytes())
        while len(blob) % 4:
            blob.append(0)
        solids.append({"x0": x0, "z0": z0, "nx": nx, "nz": nz, "cell": SOLID_CELL, "y0": ybase, "step": SOLID_STEP, "offset": off})

    lo, hi = allp.min(0), allp.max(0)
    meta = {"id": tid, "name": town.get("name", tid), "aabb": [round(float(v), 2) for v in lo] + [round(float(v), 2) for v in hi],
            "shadow": town.get("shadow", 2048), "chunks": chunks, "spinners": spinners, "floaters": floaters, "pads": pads, "smokes": smokes, "lamps": lamps,
            "buildings": buildings, "solids": solids, "bytes": len(blob)}
    with open(os.path.join(OUT, tid + ".bin"), "wb") as f:
        f.write(blob)
    json.dump(meta, open(os.path.join(OUT, tid + ".json"), "w"))
    tris = sum(c["index"][2] for c in chunks) // 3
    print(f"  {tid}: {len(buildings)} buildings, {len(chunks)} chunks, {tris} tris ({sum(c['index'][0] for c in chunks) // 3} far), "
          f"{sum(c['verts'] for c in chunks)} verts, {len(pads)} pads, {len(blob) / 1e6:.1f} MB")
    return {"id": tid, "name": meta["name"], "aabb": meta["aabb"], "bytes": len(blob), "lazy": bool(town.get("lazy", False))}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT, "layout.json")
    layout = json.load(open(path))
    terrain = Terrain()
    os.makedirs(OUT, exist_ok=True)
    index = []
    for town in layout["towns"]:
        r = assemble_town(town, terrain)
        if r:
            index.append(r)
    json.dump({"towns": index}, open(os.path.join(OUT, "index.json"), "w"), indent=1)
    print("towns:", ", ".join(t["id"] for t in index))


if __name__ == "__main__":
    main()
