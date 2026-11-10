# Blender: turn a Meshy model into a game asset for the hidden places in the east of the island.
# Adapted from prop_process.py (same output: GLB with WebP textures and tangents, JSON sidecar with a
# `slabs` disc list for collisions and baked shadows), with a few things the places need:
#  - size by height or by length, turns before sizing, a sink depth (ground level is y = 0)
#  - slabs either as the usual stack of discs, or as columns of small discs on a grid so that hollow
#    and long things (a rib cage, stilt roots) keep their gaps; optionally a separate `solid` list
#    (what the broom bumps into) that leaves the thin parts out
#  - the _WIND attribute src/world/places.js reads: r = leaf flutter, g = sway, b = glow, a = 1 - cloth,
#    painted from the texture colours by named rules
#  - a lit preview from the game's sun direction
# Usage: blender -b -P place_east_process.py -- <in.glb> <out.glb> <name> <size_m> <tris> <tex_px> [key=value ...]
#   fit=height|length     what <size_m> measures (default height)
#   pre=<axis><deg>,...   turns applied first, in Blender axes (z up), e.g. pre=y65,z20
#   align=1               then turn the longest horizontal axis onto x
#   turn=<deg>            then rotate about the vertical (positive = counter-clockwise seen from above)
#   sink=<m>              bury the base this deep (after scaling)
#   center=base|bbox      origin under the base centroid (default) or under the bounding box centre
#   slabs=stack|columns|none   shadow / collision description (default stack)
#   cell=<m>              grid size for slabs=columns (default 0.9)
#   solid=bulk|slabs|none what the broom collides with: only the bulky columns, a copy of the slabs
#                         (full size, no leafy shrink), or nothing. Default: left to the engine (slabs).
#   bulk=<0..8>           for solid=bulk: how many of a column's 8 neighbours must be filled (default 6)
#   wind=<rule>           none | pine | ember | mangrove
#   glow=<rule>           none | all | amber | ice | ember | lantern   (+ glowcol=r,g,b,strength)
#                         (the light given off is albedo x tint x strength x weight, so `all` makes
#                         the bright parts of the texture shine and leaves the dark parts dark)
#   glowkey=amber|teal    let the texture pick what glows (places.js glowKey), with or without a glow rule
#   cloth=<rule>          none | paper                              (+ clothdim=length,amplitude)
#   foliage=<0..1>        leaf translucency written to the sidecar (default: engine decides)
#   baser=<m>             baseRadius to write (plants keep off the foot of a piece by this much; default measured)
#   ntex=<px>             size of the normal and roughness maps when smaller than <tex_px>
#   q=<1..100>            WebP quality (default 86)
#   preview=<dir>         where the preview PNG goes (default: art/places_east/preview)
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
src, dst, name = argv[0], argv[1], argv[2]
size, tris, tex = float(argv[3]), int(argv[4]), int(argv[5])
opt = dict(a.split("=", 1) for a in argv[6:])
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PREVIEW = opt.get("preview", os.path.join(ROOT, "art", "places_east", "preview"))
os.makedirs(PREVIEW, exist_ok=True)
os.makedirs(os.path.dirname(dst), exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1: bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = obj.data
n0 = len(me.polygons)
if n0 > tris * 1.1:
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = tris / n0
    bpy.ops.object.modifier_apply(modifier=mod.name)
me = obj.data


def coords():
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("co", co)
    return co.reshape(-1, 3)


# ---- orientation
for part in [p for p in opt.get("pre", "").split(",") if p]:
    me.transform(Matrix.Rotation(math.radians(float(part[1:])), 4, part[0].upper()))
if opt.get("align") == "1":
    co = coords()
    xy = co[:, :2] - co[:, :2].mean(0)
    w, v = np.linalg.eigh(np.cov(xy.T))
    ax = v[:, 1]
    me.transform(Matrix.Rotation(-math.atan2(ax[1], ax[0]), 4, "Z"))
if "turn" in opt:
    me.transform(Matrix.Rotation(math.radians(float(opt["turn"])), 4, "Z"))
me.update()

# ---- size, origin at the base, optional sink
co = coords()
mn, mx = co.min(0), co.max(0)
if opt.get("fit", "height") == "length":
    s = size / max(mx[0] - mn[0], mx[1] - mn[1])
else:
    s = size / (mx[2] - mn[2])
if opt.get("center", "base") == "bbox":
    cx, cy = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2
else:
    base = co[co[:, 2] < mn[2] + (mx[2] - mn[2]) * 0.08]
    cx, cy = base[:, 0].mean(), base[:, 1].mean()
sink = float(opt.get("sink", 0))
me.transform(Matrix.Translation((0, 0, -sink)) @ Matrix.Scale(s, 4) @ Matrix.Translation((-cx, -cy, -mn[2])))
me.update()
co = coords()
x, y, z = co[:, 0], co[:, 1], co[:, 2]
height = float(z.max())
above = z > -0.05

# ---- volume (glTF coords: x, y up, z = -blender y)
slabs, solid = [], None
mode = opt.get("slabs", "stack")
if mode == "columns":
    # surface samples: vertices plus points spread over the triangles, so big faces are not missed
    me.calc_loop_triangles()
    nt = len(me.loop_triangles)
    tv = np.empty(nt * 3, np.int32); me.loop_triangles.foreach_get("vertices", tv); tv = tv.reshape(-1, 3)
    rng = np.random.default_rng(1)
    pts = [co]
    for _ in range(6):
        b = rng.random((nt, 2)); f = b.sum(1) > 1; b[f] = 1 - b[f]
        pts.append(co[tv[:, 0]] + (co[tv[:, 1]] - co[tv[:, 0]]) * b[:, :1] + (co[tv[:, 2]] - co[tv[:, 0]]) * b[:, 1:])
    P = np.concatenate(pts); P = P[P[:, 2] > 0.0]
    g = float(opt.get("cell", 0.9))
    gv = g * 0.8                                           # vertical resolution
    ix = np.floor(P[:, 0] / g).astype(int); iy = np.floor(P[:, 1] / g).astype(int); iz = np.floor(P[:, 2] / gv).astype(int)
    occ = set(zip(ix.tolist(), iy.tolist(), iz.tolist()))
    cols = {}
    for a, b, c in occ:
        cols.setdefault((a, b), []).append(c)
    bulk = []
    for (a, b), zs in sorted(cols.items()):
        zs.sort()
        run = [zs[0], zs[0]]
        runs = []
        for c in zs[1:]:
            if c <= run[1] + 1: run[1] = c
            else: runs.append(run); run = [c, c]
        runs.append(run)
        m = (ix == a) & (iy == b)
        ccx, ccy = float(P[m, 0].mean()), float(P[m, 1].mean())
        for z0, z1 in runs:
            d = [round(ccx, 3), round(-ccy, 3), round(g * 0.62, 3), round(max(z0 * gv, 0.0), 3), round((z1 + 1) * gv, 3)]
            slabs.append(d)
            # bulky = most of the 8 neighbouring cells are filled over the same heights
            zm = (z0 + z1) // 2
            nb = sum(1 for da in (-1, 0, 1) for db in (-1, 0, 1) if (da or db) and any((a + da, b + db, zz) in occ for zz in (zm - 1, zm, zm + 1)))
            if nb >= int(opt.get("bulk", 6)): bulk.append(d)
    if opt.get("solid") == "bulk": solid = bulk
elif mode == "stack":
    NS = 10
    for i in range(NS):
        z0, z1 = height * i / NS, height * (i + 1) / NS
        m = (z >= z0) & (z <= z1)
        if m.sum() < 6: continue
        px, py = x[m], y[m]
        ccx, ccy = float(px.mean()), float(py.mean())
        r = float(np.percentile(np.hypot(px - ccx, py - ccy), 88))
        slabs.append([round(ccx, 3), round(-ccy, 3), round(r, 3), round(z0, 3), round(z1, 3)])
if opt.get("solid") == "slabs": solid = [list(d) for d in slabs]

low = above & (z < max(height * 0.1, 0.3))
info = {"name": name, "height": round(height, 3), "tris": len(me.polygons), "slabs": slabs,
        "radius": round(float(np.hypot(x[above], y[above]).max()), 3),
        "baseRadius": round(float(np.percentile(np.hypot(x[low], y[low]), 90)), 3) if low.sum() > 3 else 0.5,
        "bounds": [round(float(v), 3) for v in (x.min(), -y.max(), x.max(), -y.min())]}   # x0, z0, x1, z1 in glTF space
if sink: info["sink"] = sink
if solid is not None: info["solid"] = solid
if opt.get("solid") == "none": info["collide"] = False
if "foliage" in opt: info["foliage"] = float(opt["foliage"])
if "baser" in opt: info["baseRadius"] = float(opt["baser"])
if "glowkey" in opt:
    info["glowKey"] = opt["glowkey"]
    info["glow"] = [float(v) for v in opt.get("glowcol", "1,0.75,0.45,4").split(",")]

# ---- wind / glow / cloth weights, from the texture colours
wrule, grule, crule = opt.get("wind", "none"), opt.get("glow", "none"), opt.get("cloth", "none")
if (wrule, grule, crule) != ("none", "none", "none"):
    nl = len(me.loops)
    luv = np.empty(nl * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", luv); luv = luv.reshape(-1, 2)
    lvi = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", lvi)
    vuv = np.zeros((len(me.vertices), 2), np.float32); vuv[lvi] = luv
    mat = obj.material_slots[0].material
    bsdf = [n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
    img = bsdf.inputs["Base Color"].links[0].from_node.image
    w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    ixp = np.clip((vuv[:, 0] % 1.0) * w, 0, w - 1).astype(int); iyp = np.clip((vuv[:, 1] % 1.0) * h, 0, h - 1).astype(int)
    col = px[iyp, ixp, :3]; del px
    r_, g_, b_ = col[:, 0], col[:, 1], col[:, 2]
    lo_, hi_ = col.min(1), col.max(1)
    zn = np.clip(z / height, 0, 1)
    nv = len(z)
    leaf = np.zeros(nv, np.float32); sway = np.zeros(nv, np.float32); glow = np.zeros(nv, np.float32); cloth = np.zeros(nv, np.float32)
    ne = len(me.edges)
    ev = np.empty(ne * 2, np.int32); me.edges.foreach_get("vertices", ev); ev = ev.reshape(-1, 2)
    deg = np.zeros(nv, np.float32); np.add.at(deg, ev[:, 0], 1); np.add.at(deg, ev[:, 1], 1)

    def smooth(a, it=3):
        for _ in range(it):
            acc = np.zeros_like(a); np.add.at(acc, ev[:, 0], a[ev[:, 1]]); np.add.at(acc, ev[:, 1], a[ev[:, 0]])
            a = a * 0.5 + acc / np.maximum(deg, 1) * 0.5
        return a

    paper = np.zeros(nv, bool)
    if wrule == "pine":
        # blue-green needle pads
        needle = (g_ > r_ * 1.10) & (b_ > r_ * 0.95)
        leaf = needle.astype(np.float32) * np.clip((zn - 0.30) / 0.15, 0, 1)
        sway = zn ** 1.6
        paper = ((lo_ > 0.60) | ((r_ > g_ * 1.9) & (r_ > 0.35))) & (zn > 0.18) & (zn < 0.75)
    elif wrule == "ember":
        # crimson / orange canopy
        leaf = ((r_ > g_ * 1.5) & (r_ > 0.20)).astype(np.float32) * np.clip((zn - 0.30) / 0.15, 0, 1)
        sway = zn ** 1.6
    elif wrule == "mangrove":
        # glossy green crown with pale blossoms
        green = ((g_ > r_ * 1.08) & (g_ > b_ * 1.08)) | ((lo_ > 0.55) & (r_ > b_ * 1.15))
        leaf = green.astype(np.float32) * np.clip((zn - 0.42) / 0.12, 0, 1)
        sway = zn ** 1.6
    elif wrule != "none":
        raise SystemExit(f"unknown wind rule {wrule}")

    if grule == "all":
        glow = np.ones(nv, np.float32)
    elif grule == "amber":     # lit glass, warm paper
        glow = (((r_ > 0.55) & (g_ > 0.28) & (b_ < r_ * 0.62) & (r_ - b_ > 0.28)).astype(np.float32)) * np.clip((hi_ - 0.5) / 0.3, 0.3, 1)
    elif grule == "ice":       # pale blue-white crystal
        glow = ((b_ > 0.50) & (b_ >= r_ * 1.02) & (lo_ > 0.36)).astype(np.float32) * np.clip((lo_ - 0.36) / 0.3, 0.25, 1)
    elif grule == "ember":     # molten cracks in dark stone
        glow = ((r_ > 0.42) & (g_ > 0.14) & (b_ < 0.30) & (r_ > b_ * 2.2)).astype(np.float32)
    elif grule == "lantern":   # paper lanterns hung low in a tree
        lant = (((r_ > b_ * 1.7) & (r_ > 0.45)) | ((r_ > 0.72) & (g_ > 0.58) & (b_ > 0.35) & (b_ < g_ * 0.92))) & (zn < 0.42)
        glow = lant.astype(np.float32)
        sway = np.maximum(sway, lant.astype(np.float32) * 0.22)       # they swing a little
        if lant.sum(): info["lanternY"] = [round(float(v), 2) for v in (z[lant].min(), z[lant].mean(), z[lant].max())]
    elif grule != "none":
        raise SystemExit(f"unknown glow rule {grule}")

    if crule == "paper":
        # strips of paper: free end streams, tied end stays. Per connected patch of paper-coloured
        # vertices, the weight runs from 0 at its top to 1 at its bottom.
        if not paper.any():
            paper = (lo_ > 0.60) & (hi_ - lo_ < 0.25)
        lab = np.arange(nv)
        pe = ev[paper[ev[:, 0]] & paper[ev[:, 1]]]
        for _ in range(60):
            m_ = np.minimum(lab[pe[:, 0]], lab[pe[:, 1]])
            old = lab.copy()
            np.minimum.at(lab, pe[:, 0], m_); np.minimum.at(lab, pe[:, 1], m_)
            if (old == lab).all(): break
        ids = np.unique(lab[paper])
        for i in ids:
            m_ = paper & (lab == i)
            if m_.sum() < 4: continue
            z0, z1 = z[m_].min(), z[m_].max()
            if z1 - z0 < 0.05: continue
            cloth[m_] = np.clip((z1 - z[m_]) / (z1 - z0), 0, 1)
        info["cloth"] = [float(v) for v in opt.get("clothdim", "0.5,0.10").split(",")]
    elif crule != "none":
        raise SystemExit(f"unknown cloth rule {crule}")

    leaf = np.clip(smooth(leaf), 0, 1); sway = np.clip(smooth(sway), 0, 1); glow = np.clip(smooth(glow, 1), 0, 1); cloth = np.clip(smooth(cloth, 1), 0, 1)
    wind = np.stack([leaf, sway, glow, 1.0 - cloth], -1).astype(np.float32)
    # 8-bit weights are plenty (the exporter writes them as normalized integers: half the bytes of floats)
    attr = me.attributes.new(name="_WIND", type="BYTE_COLOR", domain="POINT")
    attr.data.foreach_set("color", wind.reshape(-1))
    if wrule != "none":
        top = z > height * 0.55
        info["lean"] = [round(float(x[top].mean()), 3), round(float(-y[top].mean()), 3)]   # where the crown hangs, (x, z) in glTF space
        info["leaf"] = round(float((leaf > 0.5).mean()), 3)
    else:
        info.setdefault("foliage", 0)
    if grule != "none":
        info["glow"] = [float(v) for v in opt.get("glowcol", "1,0.75,0.45,4").split(",")]
        info["glowShare"] = round(float((glow > 0.5).mean()), 3)
    if crule != "none":
        info["clothShare"] = round(float((cloth > 0.3).mean()), 3)

# ---- preview: lit from the game's sun (game x east, y up, z south -> Blender x, z, -y), two sides and a top view
scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_EEVEE"
except Exception:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 760; scene.render.resolution_y = 760
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
world = bpy.data.worlds.new("w"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.74, 0.92, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
sun_d = bpy.data.lights.new("sun", "SUN"); sun_d.energy = 4.2; sun_d.color = (1.0, 0.95, 0.86); sun_d.angle = math.radians(2)
sun = bpy.data.objects.new("sun", sun_d); scene.collection.objects.link(sun)
to_sun = Vector((-0.5104, 0.6533, 0.5592)).normalized()
sun.rotation_euler = to_sun.to_track_quat("Z", "Y").to_euler()
gm = bpy.data.meshes.new("ground")
R = max(info["radius"], height) * 6
gm.from_pydata([(-R, -R, 0), (R, -R, 0), (R, R, 0), (-R, R, 0)], [], [(0, 1, 2, 3)])
ground = bpy.data.objects.new("ground", gm); scene.collection.objects.link(ground)
gmat = bpy.data.materials.new("g"); gmat.use_nodes = True
gmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.42, 0.50, 0.28, 1)
gmat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
gm.materials.append(gmat)
cam_data = bpy.data.cameras.new("c"); cam_data.type = "ORTHO"
cam = bpy.data.objects.new("c", cam_data); scene.collection.objects.link(cam); scene.camera = cam
ext = max(height, info["radius"] * 2)
ctr = Vector(((x.min() + x.max()) / 2, (y.min() + y.max()) / 2, height * 0.45))
views = {"a": ((0.7, -0.75, 0.38), 1.25), "b": ((-0.75, 0.6, 0.38), 1.25), "top": ((0.0, -0.02, 1.0), 1.15)}
shots = []
for vn, (d, k) in views.items():
    d = Vector(d).normalized()
    cam_data.ortho_scale = ext * k
    cam.location = ctr + d * ext * 6
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam_data.clip_end = ext * 20
    fp = os.path.join(PREVIEW, f"{name}_{vn}.png")
    scene.render.filepath = fp
    bpy.ops.render.render(write_still=True)
    shots.append(fp)
for o in (cam, sun, ground): bpy.data.objects.remove(o)
# one sheet
try:
    ims = [bpy.data.images.load(fp) for fp in shots]
    wI, hI = ims[0].size
    sheet = np.zeros((hI, wI * len(ims), 4), np.float32)
    for i, im in enumerate(ims):
        buf = np.empty(wI * hI * 4, np.float32); im.pixels.foreach_get(buf)
        sheet[:, i * wI:(i + 1) * wI] = buf.reshape(hI, wI, 4)
    out = bpy.data.images.new("sheet", wI * len(ims), hI)
    out.pixels.foreach_set(sheet.reshape(-1))
    out.filepath_raw = os.path.join(PREVIEW, f"{name}.png"); out.file_format = "PNG"; out.save()
    for im in ims: bpy.data.images.remove(im)
    bpy.data.images.remove(out)
    for fp in shots: os.remove(fp)
except Exception as e:
    print("sheet failed", e)

ntex = int(opt.get("ntex", tex))
base_img = None
try:
    bs = [n for n in obj.material_slots[0].material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
    base_img = bs.inputs["Base Color"].links[0].from_node.image
except Exception:
    pass
for im in bpy.data.images:
    want = tex if im == base_img else ntex
    if im.size[0] > want:
        im.scale(want, want)
bpy.ops.export_scene.gltf(
    filepath=dst, export_format="GLB", use_selection=False,
    export_image_format="WEBP", export_image_quality=int(opt.get("q", 86)),
    export_attributes=True, export_vertex_color="NONE",
    export_tangents=True, export_yup=True, export_apply=True,
)
json.dump(info, open(os.path.splitext(dst)[0] + ".json", "w"), indent=1)
print("EXPORTED", name, round(os.path.getsize(dst) / 1e6, 2), "MB", n0, "->", info["tris"], "tris", "h", info["height"],
      "radius", info["radius"], "slabs", len(slabs), "solid", None if solid is None else len(solid),
      {k: info[k] for k in ("lean", "leaf", "glowShare", "clothShare", "lanternY") if k in info})
