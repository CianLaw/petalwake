"""Minimal GLB reader: vertex positions (and indices) of the first mesh, in glTF space (y up)."""
import json, struct
import numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def read(path):
    b = open(path, "rb").read()
    jl = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + jl])
    bin0 = 20 + jl + 8
    def acc(i):
        a = j["accessors"][i]; v = j["bufferViews"][a["bufferView"]]
        off = bin0 + v.get("byteOffset", 0) + a.get("byteOffset", 0)
        n = NC[a["type"]]; dt = np.dtype(CT[a["componentType"]])
        stride = v.get("byteStride", 0)
        if stride and stride != dt.itemsize * n:
            raw = np.frombuffer(b, np.uint8, count=stride * a["count"], offset=off).reshape(a["count"], stride)
            return raw[:, :dt.itemsize * n].copy().view(dt).reshape(a["count"], n)
        return np.frombuffer(b, dt, count=a["count"] * n, offset=off).reshape(a["count"], n)
    out = []
    for m in j["meshes"]:
        for p in m["primitives"]:
            out.append((acc(p["attributes"]["POSITION"]).astype(np.float64), acc(p["indices"]).reshape(-1, 3) if "indices" in p else None))
    pos = np.concatenate([o[0] for o in out])
    return pos, j
