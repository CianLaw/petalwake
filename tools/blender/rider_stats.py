# Blender: classify rider vertices by texture colour + position; print stats to calibrate wind weights.
import bpy, sys, numpy as np, colorsys
argv = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=argv[0])
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
bpy.context.view_layer.objects.active = obj; obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = obj.data
nv = len(me.vertices)
co = np.empty(nv * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
nl = len(me.loops)
luv = np.empty(nl * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", luv); luv = luv.reshape(-1, 2)
lvi = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", lvi)
vuv = np.zeros((nv, 2), np.float32); vuv[lvi] = luv
mat = obj.material_slots[0].material
bsdf = [n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
img = bsdf.inputs["Base Color"].links[0].from_node.image
w, h = img.size
px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
ix = np.clip((vuv[:, 0] % 1.0) * w, 0, w - 1).astype(int); iy = np.clip((vuv[:, 1] % 1.0) * h, 0, h - 1).astype(int)
col = px[iy, ix, :3]
mx = col.max(1); mn = col.min(1); v = mx; s = np.where(mx > 1e-5, (mx - mn) / np.maximum(mx, 1e-5), 0)
d = np.maximum(mx - mn, 1e-6)
hh = np.where(mx == col[:, 0], ((col[:, 1] - col[:, 2]) / d) % 6, np.where(mx == col[:, 1], (col[:, 2] - col[:, 0]) / d + 2, (col[:, 0] - col[:, 1]) / d + 4)) / 6.0
print("img", img.name, w, h, "colorspace", img.colorspace_settings.name)
def rep(name, m):
    if m.sum() == 0: print(name, "none"); return
    p = co[m]
    print(f"{name:10s} n={m.sum():6d} x[{p[:,0].min():+.2f},{p[:,0].max():+.2f}] y[{p[:,1].min():+.2f},{p[:,1].max():+.2f}] z[{p[:,2].min():+.2f},{p[:,2].max():+.2f}] meancol {col[m].mean(0).round(2)}")
rep("all", np.ones(nv, bool))
yellow = (hh > 0.07) & (hh < 0.17) & (s > 0.45) & (v > 0.35)
rep("yellow", yellow)
rep("yel_rear", yellow & (co[:, 1] > 0.35))
rep("yel_body", yellow & (co[:, 1] < 0.35) & (co[:, 2] > -0.15))
plum = ((hh > 0.75) | (hh < 0.02)) & (s > 0.25) & (v < 0.55) & (co[:, 2] > 0.2)
rep("plum", plum)
green = (hh > 0.2) & (hh < 0.4) & (s > 0.2)
rep("green", green)
teal = (hh > 0.42) & (hh < 0.6) & (s > 0.3)
rep("teal", teal)
front = co[:, 1] < -0.55
rep("front", front)
rep("front_low", front & (co[:, 2] < -0.12))
# height histogram of handle-ish pale wood at the front
for y0 in (-0.9, -0.7, -0.5, -0.3, 0.3, 0.5, 0.7, 0.9):
    m = np.abs(co[:, 1] - y0) < 0.03
    if m.sum(): print(f"slice y={y0:+.1f}: z[{co[m,2].min():+.2f},{co[m,2].max():+.2f}] x[{co[m,0].min():+.2f},{co[m,0].max():+.2f}] n={m.sum()}")
for z0 in (0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.5):
    m = np.abs(co[:, 2] - z0) < 0.02
    if m.sum(): print(f"slice z={z0:+.1f}: y[{co[m,1].min():+.2f},{co[m,1].max():+.2f}] x[{co[m,0].min():+.2f},{co[m,0].max():+.2f}] n={m.sum()}")
