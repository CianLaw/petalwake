#!/usr/bin/env python3
# Shrink a GLB written by place_east_process.py without touching how it looks: normals and tangents
# become normalized bytes, texture coordinates normalized 16-bit, the _WIND weights normalized bytes
# (KHR_mesh_quantization, which three's GLTFLoader reads natively). Positions stay floats because the
# game takes them as they are. Typically halves the geometry: 56 -> 28 bytes a vertex.
# Usage: python3 place_east_pack.py <file.glb> [...]        (rewrites each file in place; plain Python + numpy)
import json, struct, sys, os
import numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def pack(path):
    raw = open(path, "rb").read()
    magic, ver, total = struct.unpack_from("<III", raw, 0)
    assert magic == 0x46546C67, "not a GLB"
    jl, jt = struct.unpack_from("<II", raw, 12)
    js = json.loads(raw[20:20 + jl])
    bl, bt = struct.unpack_from("<II", raw, 20 + jl)
    bin_ = raw[28 + jl:28 + jl + bl]
    views, accs = js["bufferViews"], js["accessors"]

    def read(ai):
        a = accs[ai]; v = views[a["bufferView"]]
        dt = np.dtype(CT[a["componentType"]]); n = NC[a["type"]]
        off = v.get("byteOffset", 0) + a.get("byteOffset", 0)
        stride = v.get("byteStride") or dt.itemsize * n
        if stride == dt.itemsize * n:
            arr = np.frombuffer(bin_, dt, a["count"] * n, off).reshape(a["count"], n)
        else:
            arr = np.stack([np.frombuffer(bin_, dt, n, off + i * stride) for i in range(a["count"])])
        if a.get("normalized"):
            arr = arr.astype(np.float32) / np.iinfo(dt).max
        return arr.astype(np.float32)

    new = {}                                   # accessor index -> (bytes, componentType, type, stride, normalized)
    for mesh in js["meshes"]:
        for pr in mesh["primitives"]:
            at = pr["attributes"]
            for key in ("NORMAL", "TANGENT", "TEXCOORD_0", "_WIND"):
                ai = at.get(key)
                if ai is None or ai in new: continue
                a = accs[ai]
                d = read(ai)
                if key == "NORMAL":
                    if a["componentType"] != 5126: continue
                    d = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
                    q = np.zeros((len(d), 4), np.int8); q[:, :3] = np.round(d * 127)
                    new[ai] = (q.tobytes(), 5120, "VEC3", 4, True)
                elif key == "TANGENT":
                    if a["componentType"] != 5126: continue
                    t = d[:, :3] / np.maximum(np.linalg.norm(d[:, :3], axis=1, keepdims=True), 1e-9)
                    q = np.zeros((len(d), 4), np.int8); q[:, :3] = np.round(t * 127); q[:, 3] = np.where(d[:, 3] < 0, -127, 127)
                    new[ai] = (q.tobytes(), 5120, "VEC4", 4, True)
                elif key == "TEXCOORD_0":
                    if a["componentType"] != 5126 or d.min() < 0 or d.max() > 1: continue
                    new[ai] = (np.round(d * 65535).astype(np.uint16).tobytes(), 5123, "VEC2", 4, True)
                else:
                    if a["componentType"] == 5121: continue
                    new[ai] = (np.round(np.clip(d, 0, 1) * 255).astype(np.uint8).tobytes(), 5121, "VEC4", 4, True)
    if not new:
        return None

    # rebuild the binary: keep every view that is still referenced, append the packed ones
    used = set()
    for i, a in enumerate(accs):
        if i not in new and "bufferView" in a: used.add(a["bufferView"])
    for im in js.get("images", []):
        if "bufferView" in im: used.add(im["bufferView"])
    out = bytearray(); remap = {}; nviews = []
    for i, v in enumerate(views):
        if i not in used: continue
        while len(out) % 4: out.append(0)
        nv = dict(v); o = v.get("byteOffset", 0)
        nv["byteOffset"] = len(out); out += bin_[o:o + v["byteLength"]]
        remap[i] = len(nviews); nviews.append(nv)
    for ai, (data, ct, typ, stride, norm) in new.items():
        while len(out) % 4: out.append(0)
        nviews.append({"buffer": 0, "byteOffset": len(out), "byteLength": len(data), "byteStride": stride, "target": 34962})
        out += data
        a = accs[ai]
        a["bufferView"] = len(nviews) - 1; a["componentType"] = ct; a["type"] = typ; a["normalized"] = norm
        a.pop("byteOffset", None); a.pop("min", None); a.pop("max", None)
    for i, a in enumerate(accs):
        if i not in new and "bufferView" in a: a["bufferView"] = remap[a["bufferView"]]
    for im in js.get("images", []):
        if "bufferView" in im: im["bufferView"] = remap[im["bufferView"]]
    while len(out) % 4: out.append(0)
    js["bufferViews"] = nviews
    js["buffers"] = [{"byteLength": len(out)}]
    for k in ("extensionsUsed", "extensionsRequired"):
        ex = js.setdefault(k, [])
        if "KHR_mesh_quantization" not in ex: ex.append("KHR_mesh_quantization")
    jb = json.dumps(js, separators=(",", ":")).encode()
    while len(jb) % 4: jb += b" "
    glb = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(jb) + 8 + len(out)) + struct.pack("<II", len(jb), 0x4E4F534A) + jb + struct.pack("<II", len(out), 0x004E4942) + bytes(out)
    open(path, "wb").write(glb)
    return len(raw), len(glb)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        r = pack(p)
        print(os.path.basename(p), "already packed" if r is None else f"{r[0] / 1e6:.2f} -> {r[1] / 1e6:.2f} MB")
