# Blender: turn a Meshy prop into a game asset.
#  - decimates to a triangle budget, sets real-world size, puts the origin at the base
#  - describes its volume as a stack of discs (for baked ground shadows and flight collision)
#  - trees: paints a wind attribute (_WIND r = leaf flutter, g = sway with height) and measures the lean
#  - downsizes textures, exports GLB (WebP, tangents) + a JSON sidecar + a preview render
# Usage: blender -b -P prop_process.py -- <in.glb> <out.glb> <name> <height_m> <tris> <tex_px>
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
src, dst, name = argv[0], argv[1], argv[2]
height, tris, tex = float(argv[3]), int(argv[4]), int(argv[5])
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

co = coords()
mn, mx = co.min(0), co.max(0)
s = height / (mx[2] - mn[2])
base = co[co[:, 2] < mn[2] + (mx[2] - mn[2]) * 0.08]
cx, cy = base[:, 0].mean(), base[:, 1].mean()
me.transform(Matrix.Scale(s, 4) @ Matrix.Translation((-cx, -cy, -mn[2])))
me.update()
co = coords()
x, y, z = co[:, 0], co[:, 1], co[:, 2]

# ---- volume as a stack of discs (glTF coords: x, y up, z = -blender y)
slabs = []
NS = 10
for i in range(NS):
    z0, z1 = height * i / NS, height * (i + 1) / NS
    m = (z >= z0) & (z <= z1)
    if m.sum() < 6: continue
    px, py = x[m], y[m]
    ccx, ccy = float(px.mean()), float(py.mean())
    r = float(np.percentile(np.hypot(px - ccx, py - ccy), 88))
    slabs.append([round(ccx, 3), round(-ccy, 3), round(r, 3), round(z0, 3), round(z1, 3)])

info = {"name": name, "height": height, "tris": len(me.polygons), "slabs": slabs,
        "radius": round(float(np.hypot(x, y).max()), 3), "baseRadius": round(float(np.percentile(np.hypot(x[z < height * 0.1], y[z < height * 0.1]), 90)), 3)}

# ---- colour lookup (for the tree's leaves)
if name == "tree":
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
    leaf = ((col[:, 1] > col[:, 0] * 1.08) & (col[:, 1] > col[:, 2] * 1.08)) | (col.min(1) > 0.75)   # green, or white blossom
    leaf = leaf.astype(np.float32) * np.clip((z - height * 0.25) / (height * 0.2), 0, 1)
    sway = np.clip(z / height, 0, 1) ** 1.6
    wind = np.stack([leaf, sway, np.zeros_like(z), np.ones_like(z)], -1).astype(np.float32)
    ne = len(me.edges)
    ev = np.empty(ne * 2, np.int32); me.edges.foreach_get("vertices", ev); ev = ev.reshape(-1, 2)
    deg = np.zeros(len(z), np.float32); np.add.at(deg, ev[:, 0], 1); np.add.at(deg, ev[:, 1], 1)
    for it in range(3):
        acc = np.zeros_like(wind); np.add.at(acc, ev[:, 0], wind[ev[:, 1]]); np.add.at(acc, ev[:, 1], wind[ev[:, 0]])
        wind = wind * 0.5 + acc / np.maximum(deg, 1)[:, None] * 0.5
    attr = me.attributes.new(name="_WIND", type="FLOAT_COLOR", domain="POINT")
    attr.data.foreach_set("color", wind.reshape(-1))
    top = z > height * 0.55
    lx, ly = float(x[top].mean()), float(y[top].mean())
    # direction the canopy streams toward, as (x, z) in glTF space
    info["lean"] = [round(lx, 3), round(-ly, 3)]
    info["leaf"] = round(float((leaf > 0.5).mean()), 3)

# ---- preview
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "TEXTURE"
scene.render.resolution_x = 560; scene.render.resolution_y = 560
cam_data = bpy.data.cameras.new("c"); cam_data.type = "ORTHO"; cam_data.ortho_scale = max(height, info["radius"] * 2) * 1.25
cam = bpy.data.objects.new("c", cam_data); scene.collection.objects.link(cam); scene.camera = cam
d = Vector((0.7, -0.75, 0.32)).normalized()
ctr = Vector((0, 0, height * 0.5))
cam.location = ctr + d * height * 6
cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = os.path.splitext(dst)[0] + "_preview.png"
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam)

for im in bpy.data.images:
    if im.size[0] > tex:
        im.scale(tex, tex)
bpy.ops.export_scene.gltf(
    filepath=dst, export_format="GLB", use_selection=False,
    export_image_format="WEBP", export_image_quality=88,
    export_attributes=True, export_vertex_color="NONE",
    export_tangents=True, export_yup=True, export_apply=True,
)
json.dump(info, open(os.path.splitext(dst)[0] + ".json", "w"), indent=1)
print("EXPORTED", name, round(os.path.getsize(dst) / 1e6, 2), "MB", n0, "->", info["tris"], "tris", "radius", info["radius"], info.get("lean"))
