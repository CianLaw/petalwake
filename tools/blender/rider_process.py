# Blender: turn the Meshy rider into the game asset.
#  - paints a per-vertex wind attribute (_WIND rgba = cape, bristles, hat, lantern)
#  - re-orients so the broom points down glTF -Z, pivot on the seat
#  - downsizes textures and exports GLB (WebP)
# Usage: blender -b -P rider_process.py -- <in.glb> <out.glb> <debug_dir>
import bpy, sys, os, json, math, numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
src, dst, dbg = argv[0], argv[1], argv[2]
os.makedirs(dbg, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
for o in list(bpy.context.scene.objects):
    if o != obj and o.type != "MESH":
        pass
bpy.context.view_layer.objects.active = obj; obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = obj.data
nv = len(me.vertices)
co = np.empty(nv * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
x, y, z = co[:, 0], co[:, 1], co[:, 2]

# ---- colour lookup
nl = len(me.loops)
luv = np.empty(nl * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", luv); luv = luv.reshape(-1, 2)
lvi = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", lvi)
vuv = np.zeros((nv, 2), np.float32); vuv[lvi] = luv
mat = obj.material_slots[0].material
nodes = mat.node_tree.nodes
bsdf = [n for n in nodes if n.type == "BSDF_PRINCIPLED"][0]
img = bsdf.inputs["Base Color"].links[0].from_node.image
w, h = img.size
px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
ix = np.clip((vuv[:, 0] % 1.0) * w, 0, w - 1).astype(int); iy = np.clip((vuv[:, 1] % 1.0) * h, 0, h - 1).astype(int)
col = px[iy, ix, :3]
del px
mx = col.max(1); mn = col.min(1)
sat = np.where(mx > 1e-5, (mx - mn) / np.maximum(mx, 1e-5), 0)
d = np.maximum(mx - mn, 1e-6)
hue = np.where(mx == col[:, 0], ((col[:, 1] - col[:, 2]) / d) % 6, np.where(mx == col[:, 1], (col[:, 2] - col[:, 0]) / d + 2, (col[:, 0] - col[:, 1]) / d + 4)) / 6.0

def ss(a, b, v):
    t = np.clip((v - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)

# ---- weights
HANDLE_Z = -0.22
# cape: saturated marigold around the shoulders; hem moves most, the back more than the front
cape_m = (hue > 0.08) & (hue < 0.16) & (sat > 0.68) & (mx > 0.5) & (z > 0.015) & (z < 0.30) & (y > -0.42) & (y < 0.30)
cape = cape_m * (0.12 + 0.88 * ss(0.27, 0.03, z)) * (0.55 + 0.45 * ss(-0.25, 0.2, y))
# bristles: everything behind the binding
bris = np.clip((y - 0.50) / 0.45, 0, 1) ** 1.4
# hat: the tip whips, the brim flexes a little at its rim
hat_c = np.array([0.0, -0.22])
r = np.hypot(x - hat_c[0], y - hat_c[1])
plum = ((hue > 0.72) | (hue < 0.03)) & (z > 0.2)
tip = ss(0.40, 0.66, z) * (z > 0.36)
brim = ss(0.13, 0.30, r) * (z > 0.2) * (z < 0.46) * plum * 0.45
hat = np.maximum(tip, brim)
# lantern: rigid pendulum under the front of the handle
lant_m = (y < -0.60) & (z < HANDLE_Z - 0.03)
lant = lant_m * ss(HANDLE_Z - 0.03, HANDLE_Z - 0.075, z)
lp = co[lant_m]
pivot = [float(lp[:, 0].mean()), float(lp[:, 1].mean()), float(HANDLE_Z - 0.035)] if lant_m.sum() else [0, -0.8, HANDLE_Z]
print("CAPE verts", int(cape_m.sum()), "BRISTLE", int((bris > 0).sum()), "HAT", int((hat > 0).sum()), "LANTERN", int(lant_m.sum()), "pivot", np.round(pivot, 3))
if lant_m.sum():
    print("LANTERN bounds y", lp[:, 1].min().round(3), lp[:, 1].max().round(3), "z", lp[:, 2].min().round(3), lp[:, 2].max().round(3))

wind = np.stack([cape, bris, hat, lant], -1).astype(np.float32)
# smooth the weights over the surface a few times so there are no hard seams
ne = len(me.edges)
ev = np.empty(ne * 2, np.int32); me.edges.foreach_get("vertices", ev); ev = ev.reshape(-1, 2)
deg = np.zeros(nv, np.float32); np.add.at(deg, ev[:, 0], 1); np.add.at(deg, ev[:, 1], 1)
for it in range(6):
    acc = np.zeros_like(wind)
    np.add.at(acc, ev[:, 0], wind[ev[:, 1]]); np.add.at(acc, ev[:, 1], wind[ev[:, 0]])
    sm = acc / np.maximum(deg, 1)[:, None]
    keep = wind[:, 3].copy()
    wind = wind * 0.4 + sm * 0.6
    wind[:, 3] = keep * 0.8 + wind[:, 3] * 0.2   # keep the lantern rigid
attr = me.attributes.new(name="_WIND", type="FLOAT_COLOR", domain="POINT")
attr.data.foreach_set("color", wind.reshape(-1))

# ---- debug render of the weights
def render(path, emission_attr):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "VERTEX"
    scene.render.resolution_x = 900; scene.render.resolution_y = 700
    cam_data = bpy.data.cameras.new("c"); cam_data.type = "ORTHO"; cam_data.ortho_scale = 2.4
    cam = bpy.data.objects.new("c", cam_data); scene.collection.objects.link(cam); scene.camera = cam
    dvec = Vector((0.75, 0.55, 0.38)).normalized()
    cam.location = dvec * 6
    cam.rotation_euler = (-dvec).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)

vc = me.color_attributes.new(name="dbg", type="FLOAT_COLOR", domain="POINT")
dbgcol = np.stack([wind[:, 0] + wind[:, 3], wind[:, 1] + wind[:, 3], wind[:, 2], np.ones(nv)], -1).astype(np.float32)
vc.data.foreach_set("color", dbgcol.reshape(-1))
me.color_attributes.active_color = vc
render(os.path.join(dbg, "wind_weights.png"), "dbg")
me.color_attributes.remove(me.color_attributes["dbg"])

# ---- orient: Blender -Y is the model's forward. Rotate 180deg about Z so forward = +Y (glTF -Z).
# pivot on the seat (centre of the figure on the handle).
seat = Vector((0.0, 0.02, HANDLE_Z))
M = Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-seat)
me.transform(M)
me.update()
pv = M @ Vector(pivot)
info = {
    "lanternPivot": [pv.x, pv.z, -pv.y],            # glTF coords (x, y up, z)
    "handleY": 0.0,
    "bounds": {"min": [float(v) for v in (M @ Vector(co.min(0)))], "max": [float(v) for v in (M @ Vector(co.max(0)))]},
    "tris": len(me.polygons),
}

# ---- textures: 2K is plenty for a chase-cam hero
for im in bpy.data.images:
    if im.size[0] > 2048:
        im.scale(2048, 2048)
bpy.ops.export_scene.gltf(
    filepath=dst, export_format="GLB", use_selection=False,
    export_image_format="WEBP", export_image_quality=90,
    export_attributes=True, export_vertex_color="NONE",
    export_tangents=True, export_yup=True, export_apply=True,
)
json.dump(info, open(os.path.splitext(dst)[0] + ".json", "w"), indent=1)
print("EXPORTED", dst, os.path.getsize(dst) / 1e6, "MB", info)
