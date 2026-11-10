"""Build town buildings in Blender.

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/town/make.py -- <id> [<id> ...] [--render] [--blend] [--quiet]

Each <id> is a module tools/town/buildings/<id>.py (or tools/town/props/<id>.py) with a `build(b)`
function and an optional META dict. For every one this:
  - runs build(b) on a fresh kit.Building, finishes its walls, gives the whole thing a slight
    hand-made wobble, works out normals and per-corner ambient occlusion;
  - writes art/town/build/<id>.npz + .json  (what the town assembler packs for the game);
  - with --render, renders two views side by side to art/town/preview/<id>.jpg;
  - with --blend, saves the model as art/town/blend/<id>.blend to open in Blender.
"""
import importlib
import json
import math
import os
import sys
import time
import zlib

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for p in (HERE, os.path.join(HERE, "buildings"), os.path.join(HERE, "props")):
    if p not in sys.path:
        sys.path.insert(0, p)
import kit  # noqa: E402

OUT = os.path.join(ROOT, "art", "town")
TEX = os.path.join(ROOT, "assets", "town", "tex")


# ---------------------------------------------------------------------------- geometry -> arrays
def _hemisphere(n, seed=3):
    rng = np.random.default_rng(seed)
    u, v = rng.random(n), rng.random(n)
    r, th = np.sqrt(u), 2 * np.pi * v
    return np.stack([r * np.cos(th), r * np.sin(th), np.sqrt(1 - u)], 1)


def bake(b, meta):
    g = b.g
    V = np.array(g.v, np.float64)
    # --- hand-made wobble: a slow drift of every vertex (not the foundations)
    amp = meta.get("wobble", 0.035)
    lean = meta.get("lean", (0.0, 0.0))
    if len(V):
        rng = np.random.default_rng(zlib.crc32(b.id.encode()))       # (the same wobble every run)
        ph = rng.random(6) * 6.28
        z = np.maximum(V[:, 2], 0.0)
        k = np.clip(z / 1.5, 0, 1)
        V[:, 0] += k * amp * (np.sin(0.83 * V[:, 1] + 0.71 * V[:, 2] + ph[0]) + 0.6 * np.sin(1.9 * V[:, 2] + 1.3 * V[:, 0] + ph[1])) + lean[0] * z
        V[:, 1] += k * amp * (np.sin(0.77 * V[:, 0] + 0.66 * V[:, 2] + ph[2]) + 0.6 * np.sin(2.1 * V[:, 2] + 1.1 * V[:, 1] + ph[3])) + lean[1] * z
        V[:, 2] += k * amp * 0.45 * np.sin(0.9 * V[:, 0] + 0.8 * V[:, 1] + ph[4])

    # --- triangles (fans) with per-corner data
    tri_v, tri_uv, tri_mat, tri_col, tri_lod, tri_sm, tri_wind, tri_face, tri_spin = [], [], [], [], [], [], [], [], []
    for fi, (idx, uvs, mat, col, lod, sm, wind, spin) in enumerate(g.f):
        for k in range(1, len(idx) - 1):
            tri_v.append((idx[0], idx[k], idx[k + 1]))
            tri_uv.append((uvs[0], uvs[k], uvs[k + 1]))
            tri_wind.append((wind[0], wind[k], wind[k + 1]))
            tri_mat.append(mat); tri_col.append(col); tri_lod.append(lod); tri_sm.append(sm); tri_face.append(fi); tri_spin.append(spin)
    T = np.array(tri_v, np.int64).reshape(-1, 3)
    if len(T) == 0:
        raise RuntimeError(f"{b.id}: no geometry")
    P = V[T]                                             # (nt, 3, 3)
    fn = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])   # area-weighted face normals
    area = np.linalg.norm(fn, axis=1)
    keep = area > 1e-10
    T, P, fn, area = T[keep], P[keep], fn[keep], area[keep]
    tri_uv = np.array(tri_uv, np.float32)[keep]
    tri_wind = np.array(tri_wind, np.float32)[keep]
    tri_mat = np.array(tri_mat, np.int32)[keep]
    tri_col = np.array(tri_col, np.float32)[keep]
    tri_lod = np.array(tri_lod, np.int32)[keep]
    tri_sm = np.array(tri_sm, np.int64)[keep]
    tri_spin = np.array(tri_spin, np.int32)[keep]
    nt = len(T)
    unit = fn / area[:, None]
    # smooth groups: average the normals of faces of the same group around each vertex
    cn = np.repeat(unit[:, None, :], 3, 1).copy()
    smt = np.nonzero(tri_sm > 0)[0]
    if len(smt):
        key = tri_sm[smt, None] * (len(V) + 1) + T[smt]            # (ns, 3)
        flat = key.reshape(-1)
        uniq, inv = np.unique(flat, return_inverse=True)
        acc = np.zeros((len(uniq), 3))
        np.add.at(acc, inv, np.repeat(fn[smt], 3, 0))
        acc /= np.maximum(np.linalg.norm(acc, axis=1, keepdims=True), 1e-12)
        cn[smt] = acc[inv].reshape(-1, 3, 3)

    # --- ambient occlusion per corner
    ao = np.ones((nt, 3), np.float32)
    if not meta.get("no_ao"):
        zmin = float(V[:, 2].min())
        gz = min(0.0, zmin) if zmin > -0.5 else 0.0
        gv = [(-80, -80, gz), (80, -80, gz), (80, 80, gz), (-80, 80, gz)]
        bvh = BVHTree.FromPolygons([tuple(v) for v in V] + gv, [tuple(int(i) for i in t) for t in T] + [(len(V), len(V) + 1, len(V) + 2, len(V) + 3)])
        H = _hemisphere(18)
        cache = {}
        maxd = 3.2
        for t in range(nt):
            for c in range(3):
                n = cn[t, c]
                k = (int(T[t, c]), int(round(n[0] * 6)), int(round(n[1] * 6)), int(round(n[2] * 6)))
                a = cache.get(k)
                if a is None:
                    up = np.array((0.0, 0.0, 1.0)) if abs(n[2]) < 0.95 else np.array((1.0, 0.0, 0.0))
                    tx = np.cross(up, n); tx /= np.linalg.norm(tx)
                    ty = np.cross(n, tx)
                    o = Vector(P[t, c] + n * 0.03)
                    occ = 0.0
                    for h in H:
                        d = tx * h[0] + ty * h[1] + n * h[2]
                        hit = bvh.ray_cast(o, Vector(d), maxd)
                        if hit[0] is not None:
                            occ += 1.0 - 0.55 * (hit[3] / maxd)
                    a = 1.0 - occ / len(H)
                    cache[k] = a
                ao[t, c] = a
        ao = np.clip(0.22 + 0.78 * ao ** 0.85, 0, 1)

    # --- grounding: masonry, plaster and wood darken (and stone greens a little) toward the ground
    zc = P[:, :, 2]
    wallish = np.isin(tri_mat, [kit.M[n] for n in ("masonry", "ashlar", "plaster", "brick", "planks", "timber", "shingle")])
    k = np.clip(zc / 1.8, 0, 1)
    k = (k * k * (3 - 2 * k))[..., None]
    g = np.where(np.isin(tri_mat, [kit.M["masonry"], kit.M["ashlar"]])[:, None, None], np.array([0.80, 0.86, 0.72]), np.array([0.84, 0.84, 0.82]))
    ccol = np.repeat(tri_col[:, None, :], 3, 1).copy()
    ccol[..., :3] = np.where(wallish[:, None, None], ccol[..., :3] * (g + (1 - g) * k), ccol[..., :3])

    # --- weld corners into an indexed mesh, triangles ordered by detail level
    out = {}
    for sp in sorted(set(tri_spin.tolist())):
        sel = np.nonzero(tri_spin == sp)[0]
        part = _pack(sel[np.argsort(tri_lod[sel], kind="stable")], P, cn, tri_uv, ccol, tri_mat, tri_wind, ao, tri_lod)
        for k, v in part.items():
            out[k if sp == 0 else f"spin{sp}_{k}"] = v
    if "pos" not in out:
        raise RuntimeError(f"{b.id}: everything is inside a spin() block")
    return out


def _pack(order, P, cn, tri_uv, ccol, tri_mat, tri_wind, ao, tri_lod):
    pos = P[order].reshape(-1, 3).astype(np.float32)
    nrm = cn[order].reshape(-1, 3).astype(np.float32)
    uv = tri_uv[order].reshape(-1, 2)
    col = (np.clip(ccol[order], 0, 1) * 255).round().astype(np.uint8).reshape(-1, 4)
    mat = np.repeat(tri_mat[order].astype(np.uint8), 3)
    wind = (np.clip(tri_wind[order].reshape(-1), 0, 1) * 255).round().astype(np.uint8)
    aob = (ao[order].reshape(-1) * 255).round().astype(np.uint8)
    rec = np.concatenate([np.round(pos * 2000).astype(np.int64), np.round(nrm * 40).astype(np.int64), np.round(uv * 500).astype(np.int64),
                          col.astype(np.int64), mat[:, None].astype(np.int64), wind[:, None].astype(np.int64), (aob[:, None] // 6).astype(np.int64)], 1)
    _, first, inv = np.unique(rec, axis=0, return_index=True, return_inverse=True)
    idx = inv.reshape(-1).astype(np.uint32)
    lods = tri_lod[order]
    counts = [int((lods <= k).sum()) for k in (0, 1, 2)]
    out = dict(pos=pos[first], nrm=nrm[first], uv=uv[first].astype(np.float32), col=col[first], mat=mat[first], wind=wind[first], ao=aob[first], idx=idx,
               lod=np.array(counts, np.int32))
    return out


# ---------------------------------------------------------------------------- Blender scene
def _material(name, mid, tiles, lum=0.55):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tint = nt.nodes.new("ShaderNodeVertexColor"); tint.layer_name = "tint"
    aon = nt.nodes.new("ShaderNodeAttribute"); aon.attribute_name = "ao"
    mul = nt.nodes.new("ShaderNodeMixRGB"); mul.blend_type = "MULTIPLY"; mul.inputs["Fac"].default_value = 1.0
    cpath = os.path.join(TEX, f"{name}_c.webp")
    if os.path.exists(cpath):
        uvn = nt.nodes.new("ShaderNodeUVMap")
        mp = nt.nodes.new("ShaderNodeMapping")
        s = 1.0 / tiles.get(name, 2.5)
        mp.inputs["Scale"].default_value = (s, s, s)
        nt.links.new(uvn.outputs["UV"], mp.inputs["Vector"])
        ct = nt.nodes.new("ShaderNodeTexImage"); ct.image = bpy.data.images.load(cpath, check_existing=True)
        ct.image.alpha_mode = "CHANNEL_PACKED"
        nt.links.new(mp.outputs["Vector"], ct.inputs["Vector"])
        # painted surfaces: the texture's light and dark only, times the paint colour
        bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(ct.outputs["Color"], bw.inputs["Color"])
        gain = nt.nodes.new("ShaderNodeMath"); gain.operation = "MULTIPLY"; gain.inputs[1].default_value = 0.92 / max(lum, 0.02)
        nt.links.new(bw.outputs["Val"], gain.inputs[0])
        pm = nt.nodes.new("ShaderNodeMixRGB"); pm.blend_type = "MIX"
        nt.links.new(tint.outputs["Alpha"], pm.inputs["Fac"]); nt.links.new(ct.outputs["Color"], pm.inputs["Color1"]); nt.links.new(gain.outputs["Value"], pm.inputs["Color2"])
        nt.links.new(pm.outputs["Color"], mul.inputs["Color1"])
        npath = os.path.join(TEX, f"{name}_n.webp")
        if os.path.exists(npath):
            ntx = nt.nodes.new("ShaderNodeTexImage"); ntx.image = bpy.data.images.load(npath, check_existing=True); ntx.image.colorspace_settings.name = "Non-Color"
            nt.links.new(mp.outputs["Vector"], ntx.inputs["Vector"])
            sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(ntx.outputs["Color"], sep.inputs["Color"])
            comb = nt.nodes.new("ShaderNodeCombineColor"); comb.inputs["Blue"].default_value = 1.0
            nt.links.new(sep.outputs["Red"], comb.inputs["Red"]); nt.links.new(sep.outputs["Green"], comb.inputs["Green"])
            nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 1.0
            nt.links.new(comb.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
            rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.55; rr.inputs["To Max"].default_value = 0.98
            nt.links.new(sep.outputs["Blue"], rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], bsdf.inputs["Roughness"])
    else:
        base = {"metal": (1, 1, 1, 1), "glass": (0.10, 0.16, 0.20, 1), "cloth": (1, 1, 1, 1), "paint": (1, 1, 1, 1), "glow": (1, 0.8, 0.5, 1), "water": (0.2, 0.55, 0.6, 1)}.get(name, (1, 1, 1, 1))
        mul.inputs["Color1"].default_value = base
        bsdf.inputs["Roughness"].default_value = {"metal": 0.42, "glass": 0.06, "water": 0.08}.get(name, 0.85)
        bsdf.inputs["Metallic"].default_value = 1.0 if name == "metal" else 0.0
        if name == "glow":
            bsdf.inputs["Emission Color"].default_value = (1.0, 0.75, 0.4, 1)
            bsdf.inputs["Emission Strength"].default_value = 3.0
    nt.links.new(tint.outputs["Color"], mul.inputs["Color2"])
    mul2 = nt.nodes.new("ShaderNodeMixRGB"); mul2.blend_type = "MULTIPLY"; mul2.inputs["Fac"].default_value = 0.85
    nt.links.new(mul.outputs["Color"], mul2.inputs["Color1"]); nt.links.new(aon.outputs["Fac"], mul2.inputs["Color2"])
    nt.links.new(mul2.outputs["Color"], bsdf.inputs["Base Color"])
    return m


_MATS = None


def materials():
    global _MATS
    if _MATS is None:
        try:
            mj = json.load(open(os.path.join(TEX, "materials.json")))
            tiles, means = mj["tile"], mj["mean"]
        except Exception:
            tiles, means = {}, {}
        lum = lambda n: 0.2126 * means[n][0] + 0.7152 * means[n][1] + 0.0722 * means[n][2] if n in means else 0.55
        _MATS = [_material(n, i, tiles, lum(n)) for i, n in enumerate(kit.MATS)]
    return _MATS


def to_object(bid, a):
    me = bpy.data.meshes.new(bid)
    nt = len(a["idx"]) // 3
    me.from_pydata(a["pos"].tolist(), [], a["idx"].reshape(-1, 3).tolist())
    me.update()
    loops = np.array([l.vertex_index for l in me.loops], np.int64) if False else a["idx"].astype(np.int64)
    uvl = me.uv_layers.new(name="UVMap")
    uvl.data.foreach_set("uv", a["uv"][loops].reshape(-1).astype(np.float32))
    ca = me.color_attributes.new("tint", "FLOAT_COLOR", "CORNER")
    c = a["col"][loops].astype(np.float32) / 255.0
    lin = np.where(c[:, :3] <= 0.04045, c[:, :3] / 12.92, ((c[:, :3] + 0.055) / 1.055) ** 2.4)
    ca.data.foreach_set("color", np.concatenate([lin, c[:, 3:4]], 1).reshape(-1))
    fa = me.attributes.new("ao", "FLOAT", "POINT"); fa.data.foreach_set("value", (a["ao"].astype(np.float32) / 255.0))
    wa = me.attributes.new("wind", "FLOAT", "POINT"); wa.data.foreach_set("value", (a["wind"].astype(np.float32) / 255.0))
    la = me.attributes.new("detail", "INT", "FACE")
    lods = np.zeros(nt, np.int32); lods[a["lod"][0]:a["lod"][1]] = 1; lods[a["lod"][1]:] = 2
    la.data.foreach_set("value", lods)
    mats = materials()
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", a["mat"][a["idx"][0::3]].astype(np.int32))
    me.polygons.foreach_set("use_smooth", np.ones(nt, bool))
    me.normals_split_custom_set_from_vertices(a["nrm"].tolist())
    ob = bpy.data.objects.new(bid, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def merged(a):
    """The static mesh and any turning parts as one (for looking at in Blender)."""
    keys = sorted({k.split("_")[0] for k in a if k.startswith("spin")})
    if not keys:
        return a
    parts = [a] + [{f: a[f"{k}_{f}"] for f in ("pos", "nrm", "uv", "col", "mat", "wind", "ao", "idx", "lod")} for k in keys]
    out, off, idx = {}, 0, []
    for f in ("pos", "nrm", "uv", "col", "mat", "wind", "ao"):
        out[f] = np.concatenate([p[f] for p in parts])
    for p in parts:
        idx.append(p["idx"] + off)
        off += len(p["pos"])
    # (detail levels of the turning parts are folded into the last level here)
    out["idx"] = np.concatenate(idx)
    n = len(out["idx"]) // 3
    out["lod"] = np.array([a["lod"][0], a["lod"][1], n], np.int32)
    return out


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    global _MATS
    _MATS = None
    s = bpy.context.scene
    s.render.engine = "BLENDER_EEVEE"
    try:
        s.view_settings.view_transform = "Standard"
        s.view_settings.look = "None"
    except Exception:
        pass
    w = bpy.data.worlds.new("sky"); s.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.42, 0.62, 0.95, 1); bg.inputs["Strength"].default_value = 0.85
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 4.2; sun.data.color = (1.0, 0.95, 0.86); sun.data.angle = 0.02
    s.collection.objects.link(sun)
    d = Vector((0.55, 0.62, -0.56)).normalized()      # light travels toward +x, +y, down: lights the front and left
    sun.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    gm = bpy.data.meshes.new("ground"); gm.from_pydata([(-120, -120, 0), (120, -120, 0), (120, 120, 0), (-120, 120, 0)], [], [(0, 1, 2, 3)])
    go = bpy.data.objects.new("ground", gm); s.collection.objects.link(go)
    mat = bpy.data.materials.new("grass"); mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.20, 0.33, 0.09, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
    gm.materials.append(mat)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); s.collection.objects.link(cam); s.camera = cam
    cam.data.lens = 42
    return s, cam, go


def render_views(s, cam, a, path, size=720, views=((-38, 16), (142, 22)), ground=None):
    lo, hi = a["pos"].min(0), a["pos"].max(0)
    lo[2] = max(lo[2], -0.3)
    c = (lo + hi) / 2
    rad = float(np.linalg.norm((hi - lo) / 2))
    s.render.resolution_x = size; s.render.resolution_y = size; s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    tiles = []
    for k, (az, el) in enumerate(views):
        fov = 2 * math.atan(18 / cam.data.lens)
        dist = rad / math.sin(fov / 2) * 0.93
        azr, elr = math.radians(az), math.radians(el)
        dirv = Vector((math.sin(azr) * math.cos(elr), -math.cos(azr) * math.cos(elr), math.sin(elr)))
        cam.location = Vector(c) + dirv * dist
        cam.rotation_euler = (-dirv).to_track_quat("-Z", "Y").to_euler()
        cam.data.clip_end = dist * 4 + 500
        fp = path + f".v{k}.png"
        s.render.filepath = fp
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(fp)
        px = np.array(img.pixels[:], np.float32).reshape(size, size, 4)
        tiles.append(px)
        bpy.data.images.remove(img)
        os.remove(fp)
    sheet = np.concatenate(tiles, 1)
    out = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0], alpha=False)
    out.pixels.foreach_set(sheet.reshape(-1))
    out.filepath_raw = path
    out.file_format = "JPEG"
    s.render.image_settings.file_format = "JPEG"; s.render.image_settings.quality = 88
    out.save_render(path, scene=s)
    bpy.data.images.remove(out)


def build_one(bid, render=False, blend=False, quiet=False, scene=None):
    t0 = time.time()
    mod = importlib.import_module(bid)
    importlib.reload(mod)
    meta = dict(getattr(mod, "META", {}))
    b = kit.Building(bid, seed=meta.get("seed"))
    b.meta.update(meta)
    mod.build(b)
    b.finish()
    a = bake(b, b.meta)
    os.makedirs(os.path.join(OUT, "build"), exist_ok=True)
    np.savez_compressed(os.path.join(OUT, "build", bid + ".npz"), **a)
    lo, hi = a["pos"].min(0), a["pos"].max(0)
    info = {"id": bid, **{k: v for k, v in b.meta.items() if k not in ("seed",)}, "bounds": [[round(float(v), 3) for v in lo], [round(float(v), 3) for v in hi]],
            "tris": [int(c) for c in a["lod"]], "verts": int(len(a["pos"])), "pads": b.pads, "smokes": b.smokes, "lamps": b.lamps, "foot": b.foot, "spinners": b.spinners}
    json.dump(info, open(os.path.join(OUT, "build", bid + ".json"), "w"), indent=1)
    if render or blend:
        s, cam, ground = scene or setup_scene()
        for o in [o for o in s.collection.objects if o.type == "MESH" and o.name != "ground"]:
            bpy.data.objects.remove(o, do_unlink=True)
        ob = to_object(bid, merged(a))
        if render:
            os.makedirs(os.path.join(OUT, "preview"), exist_ok=True)
            render_views(s, cam, merged(a), os.path.join(OUT, "preview", bid + ".jpg"))
        if blend:
            os.makedirs(os.path.join(OUT, "blend"), exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "blend", bid + ".blend"), check_existing=False)
    if not quiet:
        size = hi - lo
        print(f"BUILT {bid}: {info['tris'][2]} tris (far {info['tris'][0]}, mid {info['tris'][1]}), {info['verts']} verts, "
              f"{size[0]:.1f} x {size[1]:.1f} x {hi[2]:.1f} m, pads {len(b.pads)}, {time.time() - t0:.1f}s")
    return info


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ids = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    scene = setup_scene() if ("--render" in flags or "--blend" in flags) else None
    failed = []
    for bid in ids:
        try:
            build_one(bid, "--render" in flags, "--blend" in flags, "--quiet" in flags, scene)
        except Exception as e:
            import traceback
            traceback.print_exc()
            failed.append(bid)
            print(f"FAILED {bid}: {e}")
    if failed:
        print("FAILED:", " ".join(failed))
        sys.exit(1)
