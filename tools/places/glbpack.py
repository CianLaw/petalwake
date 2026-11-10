#!/usr/bin/env python3
"""Shrink a GLB's geometry in place (KHR_mesh_quantization; three's GLTFLoader reads it natively).

A generated mesh comes with a badly fragmented UV layout, so nearly every triangle has its own three
vertices and the vertex data is most of the file. This rewrites each primitive with
  positions  int16, normalized (the mesh node gets a uniform scale to restore metres; no offset, so
             the origin stays at the foot of the piece)
  normals    int8, normalized
  uvs        uint16, normalized (when they lie in 0..1)
  _WIND      uint8, normalized
  tangents   dropped (the game derives the tangent frame in the fragment shader)
and welds vertices that end up identical. Textures are carried over untouched.

    python3 glbpack.py file.glb [file.glb ...]            (needs numpy)
"""
import json, struct, sys
import numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def pack(path):
    raw = open(path, "rb").read()
    jl = struct.unpack("<I", raw[12:16])[0]
    j = json.loads(raw[20:20 + jl])
    b0 = 20 + jl + 8
    if "KHR_mesh_quantization" in j.get("extensionsUsed", []):
        return None

    def acc(i):
        a = j["accessors"][i]; v = j["bufferViews"][a["bufferView"]]
        off = b0 + v.get("byteOffset", 0) + a.get("byteOffset", 0)
        n = NC[a["type"]]; dt = np.dtype(CT[a["componentType"]]); stride = v.get("byteStride", 0)
        if stride and stride != dt.itemsize * n:
            r = np.frombuffer(raw, np.uint8, count=stride * a["count"], offset=off).reshape(a["count"], stride)
            return r[:, :dt.itemsize * n].copy().view(dt).reshape(a["count"], n)
        return np.frombuffer(raw, dt, count=a["count"] * n, offset=off).reshape(a["count"], n)

    out = bytearray()
    views, accs = [], []

    def view(data, target=None, stride=None):
        while len(out) % 4: out.append(0)
        v = {"buffer": 0, "byteOffset": len(out), "byteLength": len(data)}
        if target: v["target"] = target
        if stride: v["byteStride"] = stride
        out.extend(data)
        views.append(v)
        return len(views) - 1

    def accessor(arr, ctype, typ, normalized=False, pad=0, minmax=False, target=34962):
        n = arr.shape[0]
        a = np.ascontiguousarray(arr)
        if pad:
            a = np.concatenate([a, np.zeros((n, pad), a.dtype)], 1)
        item = a.dtype.itemsize * a.shape[1] if a.ndim > 1 else a.dtype.itemsize
        bv = view(a.tobytes(), target, item if (pad and target == 34962) else None)
        d = {"bufferView": bv, "componentType": ctype, "count": n, "type": typ}
        if normalized: d["normalized"] = True
        if minmax: d["min"] = [int(v) for v in arr.min(0)]; d["max"] = [int(v) for v in arr.max(0)]
        accs.append(d)
        return len(accs) - 1

    mesh_scale = {}
    stats = [0, 0]
    for mi, m in enumerate(j["meshes"]):
        # one scale for the whole mesh so its node can carry it
        ext = max(float(np.abs(acc(p["attributes"]["POSITION"])).max()) for p in m["primitives"])
        mesh_scale[mi] = ext
        for p in m["primitives"]:
            at = p["attributes"]
            pos = np.round(acc(at["POSITION"]).astype(np.float64) / ext * 32767).astype(np.int16)
            cols = [pos]
            nrm = acc(at["NORMAL"]).astype(np.float64)
            nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
            cols.append(np.round(nrm * 127).astype(np.int16))
            uv = acc(at["TEXCOORD_0"]).astype(np.float64) if "TEXCOORD_0" in at else None
            uv_q = uv is not None and uv.min() >= 0.0 and uv.max() <= 1.0
            if uv is not None: cols.append(np.round(uv * 65535).astype(np.int64) if uv_q else uv.astype(np.float32).view(np.int32).astype(np.int64))
            wind = np.round(np.clip(acc(at["_WIND"]).astype(np.float64), 0, 1) * 255).astype(np.int16) if "_WIND" in at else None
            if wind is not None: cols.append(wind)
            col = None
            if "COLOR_0" in at:
                c = acc(at["COLOR_0"]).astype(np.float64)
                if j["accessors"][at["COLOR_0"]]["componentType"] != 5126: c = c / np.iinfo(CT[j["accessors"][at["COLOR_0"]]["componentType"]]).max
                col = np.round(np.clip(c, 0, 1) * 65535).astype(np.int64)
                cols.append(col)
            rows = np.concatenate([c.astype(np.int64) for c in cols], 1)
            idx = acc(p["indices"]).reshape(-1).astype(np.int64) if "indices" in p else np.arange(len(pos))
            uniq, first, inv = np.unique(rows, axis=0, return_index=True, return_inverse=True)
            order = np.argsort(first)                       # keep the original vertex order (cache friendly)
            rank = np.empty_like(order); rank[order] = np.arange(len(order))
            keep = first[order]
            idx = rank[inv.reshape(-1)[idx]]
            stats[0] += len(pos); stats[1] += len(keep)
            new = {"POSITION": accessor(pos[keep], 5122, "VEC3", True, pad=1, minmax=True),
                   "NORMAL": accessor(np.round(nrm[keep] * 127).astype(np.int8), 5120, "VEC3", True, pad=1)}
            if uv is not None:
                new["TEXCOORD_0"] = accessor(np.round(uv[keep] * 65535).astype(np.uint16), 5123, "VEC2", True) if uv_q else accessor(uv[keep].astype(np.float32), 5126, "VEC2")
            if wind is not None: new["_WIND"] = accessor(wind[keep].astype(np.uint8), 5121, "VEC4", True)
            if col is not None: new["COLOR_0"] = accessor(col[keep].astype(np.uint16), 5123, "VEC4" if col.shape[1] == 4 else "VEC3", True, pad=0 if col.shape[1] == 4 else 1)
            p["attributes"] = new
            big = len(keep) > 65535
            p["indices"] = accessor(idx.astype(np.uint32 if big else np.uint16).reshape(-1, 1), 5125 if big else 5123, "SCALAR", target=34963)
    for n in j["nodes"]:
        if "mesh" in n:
            if "matrix" in n: raise SystemExit(f"{path}: mesh node has a matrix; export with transforms applied")
            s = mesh_scale[n["mesh"]]                           # a normalized int16 decodes to c / 32767
            old = n.get("scale", [1, 1, 1])
            n["scale"] = [old[0] * s, old[1] * s, old[2] * s]
    for im in j.get("images", []):
        if "bufferView" in im:
            v = j["bufferViews"][im["bufferView"]]
            o = b0 + v.get("byteOffset", 0)
            im["bufferView"] = view(raw[o:o + v["byteLength"]])
    while len(out) % 4: out.append(0)
    j["bufferViews"], j["accessors"] = views, accs
    j["buffers"] = [{"byteLength": len(out)}]
    for k in ("extensionsUsed", "extensionsRequired"):
        j[k] = sorted(set(j.get(k, []) + ["KHR_mesh_quantization"]))
    js = json.dumps(j, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(out)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack("<II", len(out), 0x004E4942)); f.write(out)
    return len(raw), total, stats


if __name__ == "__main__":
    for path in sys.argv[1:]:
        r = pack(path)
        print(f"{path.split('/')[-1]}: already packed" if r is None else f"{path.split('/')[-1]}: {r[0] / 1e6:.2f} -> {r[1] / 1e6:.2f} MB, {r[2][0]} -> {r[2][1]} vertices")
