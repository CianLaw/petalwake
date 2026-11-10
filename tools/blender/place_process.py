# Blender: turn a Meshy piece into a place asset (adapted from prop_process.py).
#  - decimates to a triangle budget, sets real-world size, puts the origin at the base
#  - describes its volume as discs [x, z, r, y0, y1] (glTF coords) for baked ground shadows and
#    flight collision: a stack of slices (round things) or a grid of small discs (arches, cups,
#    long things - anything the broom should be able to fly under, into or alongside)
#  - optional _WIND attribute: r leaf flutter + g sway (trees: leaves found by their colour),
#    b glow (lantern panes, glass: found by their colour)
#  - downsizes textures, exports GLB (WebP, tangents) + a JSON sidecar, renders a preview
# Usage: blender -b -P place_process.py -- <in.glb> <out.glb> <preview.png> key=value ...
#   size=<m>          real-world size, measured along `fit`
#   fit=h|w|max       h: height (default), w: longest horizontal extent, max: longest of all
#   tris=<n> tex=<px>
#   align=x           turn the piece so its long horizontal axis lies along x
#   yaw=<deg>         then turn it about the vertical (after align)
#   origin=base|box   base: under the lowest 8% of it (default); box: middle of its footprint
#   sink=<m>          bury the lowest <m> metres
#   discs=stack|grid[:cell]   how to describe the volume (default stack)
#   leaf=pink|green|purple|any   paint the wind attribute, finding the leaves by colour
#   swaymode=leaf     only the leaves sway (a vine on a wall), not the whole piece (a tree)
#   leaf_from=<0..1>  leaves start this far up the piece (default 0.25: a trunk below)
#   glow=amber|teal|gold|pale    paint the glow weight where the texture has that colour
#   back=1            also render the preview from behind (<preview>_b.png)
#   extra=<json>      merged into the sidecar (sway, glow, foliage, ...)
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
src, dst, preview = argv[0], argv[1], argv[2]
opt = dict(a.split("=", 1) for a in argv[3:])
name = os.path.splitext(os.path.basename(dst))[0]
size = float(opt.get("size", 1.0)); fit = opt.get("fit", "h")
tris, tex = int(opt.get("tris", 12000)), int(opt.get("tex", 1024))

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
# Smooth shading, split only along real creases: a decimated generated mesh otherwise exports nearly
# three vertices per triangle (every face on its own normals), which triples the file.
me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
if me.has_custom_normals:
    with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj]):
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
me.set_sharp_from_angle(angle=math.radians(float(opt.get("crease", 58))))
me.update()


def coords():
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("co", co)
    return co.reshape(-1, 3)


# ---- orientation
co = coords()
if opt.get("align") == "x":
    xy = co[:, :2] - co[:, :2].mean(0)
    w, v = np.linalg.eigh(np.cov(xy.T))
    ax = v[:, np.argmax(w)]
    me.transform(Matrix.Rotation(-math.atan2(ax[1], ax[0]), 4, "Z"))
if "yaw" in opt:
    me.transform(Matrix.Rotation(math.radians(float(opt["yaw"])), 4, "Z"))
me.update()

# ---- size and origin
co = coords()
mn, mx = co.min(0), co.max(0)
ext = mx - mn
s = size / {"h": ext[2], "w": max(ext[0], ext[1]), "max": ext.max()}[fit]
if opt.get("origin") == "box":
    cx, cy = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2
else:
    base = co[co[:, 2] < mn[2] + ext[2] * 0.08]
    cx, cy = base[:, 0].mean(), base[:, 1].mean()
sink = float(opt.get("sink", 0.0))
me.transform(Matrix.Translation((0, 0, -sink)) @ Matrix.Scale(s, 4) @ Matrix.Translation((-cx, -cy, -mn[2])))
me.update()
co = coords()
x, y, z = co[:, 0], co[:, 1], co[:, 2]
height = float(z.max())

# ---- volume as discs (glTF coords: x, y up, z = -blender y)
slabs = []
mode = opt.get("discs", "stack")
if mode.startswith("grid"):
    cell = float(mode.split(":")[1]) if ":" in mode else 1.1
    # sample the surface, not just its corners, so big flat faces are not missed
    nl = len(me.loops)
    me.calc_loop_triangles()
    tri = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get("vertices", tri); tri = tri.reshape(-1, 3)
    a, b, c = co[tri[:, 0]], co[tri[:, 1]], co[tri[:, 2]]
    pts = np.concatenate([co, (a + b + c) / 3, (a + b) / 2, (b + c) / 2, (a + c) / 2])
    pts = pts[pts[:, 2] >= 0.0]
    NS = max(2, int(math.ceil(height / max(cell * 0.9, 0.5))))
    zs = np.linspace(0, height, NS + 1)
    for i in range(NS):
        m = (pts[:, 2] >= zs[i]) & (pts[:, 2] <= zs[i + 1])
        if m.sum() < 3: continue
        p = pts[m]
        key = np.floor(p[:, 0] / cell).astype(np.int64) * 100003 + np.floor(p[:, 1] / cell).astype(np.int64)
        for k in np.unique(key):
            q = p[key == k]
            if len(q) < 2: continue
            slabs.append([round(float(q[:, 0].mean()), 3), round(float(-q[:, 1].mean()), 3), round(cell * 0.62, 3), round(float(zs[i]), 3), round(float(zs[i + 1]), 3)])
else:
    NS = 10
    for i in range(NS):
        z0, z1 = height * i / NS, height * (i + 1) / NS
        m = (z >= z0) & (z <= z1)
        if m.sum() < 6: continue
        px, py = x[m], y[m]
        ccx, ccy = float(px.mean()), float(py.mean())
        r = float(np.percentile(np.hypot(px - ccx, py - ccy), 88))
        slabs.append([round(ccx, 3), round(-ccy, 3), round(r, 3), round(z0, 3), round(z1, 3)])

low = z < max(height * 0.1, 0.05)
info = {"name": name, "height": round(height, 3), "tris": len(me.polygons), "slabs": slabs,
        "radius": round(float(np.hypot(x, y).max()), 3),
        "baseRadius": round(float(np.percentile(np.hypot(x[low], y[low]), 90)) if low.sum() > 3 else 0.5, 3),
        "bounds": [round(float(v), 3) for v in (x.min(), x.max(), -y.max(), -y.min())]}

# ---- colour lookup, for leaves and for things that glow
if "leaf" in opt or "glow" in opt:
    nl = len(me.loops)
    luv = np.empty(nl * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", luv); luv = luv.reshape(-1, 2)
    lvi = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", lvi)
    vuv = np.zeros((len(me.vertices), 2), np.float32); vuv[lvi] = luv
    mat = obj.material_slots[0].material
    bsdf = [n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
    img = bsdf.inputs["Base Color"].links[0].from_node.image
    w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    ix = np.clip((vuv[:, 0] % 1.0) * w, 0, w - 1).astype(int); iy = np.clip((vuv[:, 1] % 1.0) * h, 0, h - 1).astype(int)
    col = px[iy, ix, :3]; del px
    R, G, B = col[:, 0], col[:, 1], col[:, 2]
    lum = col.mean(1)
    leaf = np.zeros_like(z); glow = np.zeros_like(z)
    key = opt.get("leaf")
    if key:
        green = (G > R * 1.08) & (G > B * 1.08)
        pink = (R > G * 1.12) & (R > 0.42) & (B > G * 0.9)
        purple = (B > G * 1.12) & (R > G * 1.0) & (lum > 0.25)
        pale = col.min(1) > 0.75
        vivid = (G > R * 1.3) & (G > B * 1.3) & (G > 0.3)                 # leaves, not mossy stone
        leaf = {"pink": pink | green | pale, "green": green | pale, "purple": purple | vivid, "any": green | pink | purple | pale}[key].astype(np.float32)
        leaf *= np.clip((z - height * float(opt.get("leaf_from", 0.25))) / (height * 0.2), 0, 1)
    key = opt.get("glow")
    if key:
        glow = {"amber": (R > 0.72) & (G > 0.42) & (R - B > 0.32),
                "teal": (G > R * 1.2) & (B > R * 1.1) & (lum > 0.3),
                "gold": (R > 0.7) & (G > 0.5) & (B < 0.45),
                "pale": lum > 0.8}[key].astype(np.float32)
    # trees bend as a whole, more toward the top; on a stone thing only the growth on it moves
    sway = np.zeros_like(z)
    if "leaf" in opt: sway = leaf * 0.5 if opt.get("swaymode") == "leaf" else np.clip(z / height, 0, 1) ** 1.6
    wind = np.stack([leaf, sway, glow, np.ones_like(z)], -1).astype(np.float32)
    ne = len(me.edges)
    ev = np.empty(ne * 2, np.int32); me.edges.foreach_get("vertices", ev); ev = ev.reshape(-1, 2)
    deg = np.zeros(len(z), np.float32); np.add.at(deg, ev[:, 0], 1); np.add.at(deg, ev[:, 1], 1)
    for it in range(3 if "leaf" in opt else 1):
        acc = np.zeros_like(wind); np.add.at(acc, ev[:, 0], wind[ev[:, 1]]); np.add.at(acc, ev[:, 1], wind[ev[:, 0]])
        wind = wind * 0.5 + acc / np.maximum(deg, 1)[:, None] * 0.5
    wind[:, 3] = 1.0
    attr = me.attributes.new(name="_WIND", type="FLOAT_COLOR", domain="POINT")
    attr.data.foreach_set("color", wind.reshape(-1))
    if "leaf" in opt:
        top = z > height * 0.55
        info["lean"] = [round(float(x[top].mean()), 3), round(float(-y[top].mean()), 3)]
        info["leaf"] = round(float((leaf > 0.5).mean()), 3)
    if "glow" in opt:
        info["glowShare"] = round(float((glow > 0.5).mean()), 3)
if "extra" in opt:
    info.update(json.loads(opt["extra"]))

# ---- preview (a red bar on the ground points along +x, a blue one along glTF +z)
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "TEXTURE"
scene.render.resolution_x = 560; scene.render.resolution_y = 560
span = max(height, info["radius"] * 2)
marks = []
for axis, colr in (((1, 0, 0), (1, 0, 0, 1)), ((0, -1, 0), (0, 0.2, 1, 1))):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(axis[0] * span * 0.5, axis[1] * span * 0.5, 0.0))
    b = bpy.context.active_object
    b.scale = (span * 0.5 if axis[0] else span * 0.012, span * 0.5 if axis[1] else span * 0.012, span * 0.012)
    m2 = bpy.data.materials.new("mark"); m2.diffuse_color = colr; b.data.materials.append(m2); b.color = colr
    marks.append(b)
scene.display.shading.color_type = "TEXTURE"
cam_data = bpy.data.cameras.new("c"); cam_data.type = "ORTHO"; cam_data.ortho_scale = span * 1.45
cam = bpy.data.objects.new("c", cam_data); scene.collection.objects.link(cam); scene.camera = cam
d = Vector((0.7, -0.75, 0.42)).normalized()
ctr = Vector((0, 0, height * 0.5))
cam.location = ctr + d * span * 6
cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
os.makedirs(os.path.dirname(preview), exist_ok=True)
scene.render.filepath = preview
bpy.ops.render.render(write_still=True)
if opt.get("back"):                                   # and from the other side
    d = Vector((-0.7, 0.75, 0.42)).normalized()
    cam.location = ctr + d * span * 6
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = preview.replace(".png", "_b.png")
    bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam)
for b in marks: bpy.data.objects.remove(b)

for im in bpy.data.images:
    if im.size[0] > tex:
        im.scale(tex, tex)
for o in bpy.context.scene.objects: o.select_set(o == obj)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.gltf(
    filepath=dst, export_format="GLB", use_selection=True,
    export_image_format="WEBP", export_image_quality=int(opt.get("q", 86)),
    export_attributes=True, export_vertex_color="NONE",
    export_tangents=True, export_yup=True, export_apply=True,
)
json.dump(info, open(os.path.splitext(dst)[0] + ".json", "w"), indent=1)
print("EXPORTED", name, round(os.path.getsize(dst) / 1e6, 2), "MB", n0, "->", info["tris"], "tris", "h", info["height"], "radius", info["radius"], "bounds", info["bounds"], "discs", len(slabs), info.get("lean"), info.get("leaf"), info.get("glowShare"))
