# Blender: import a GLB, print stats, render 6 orthographic views into a contact sheet dir.
# Usage: blender -b -P inspect_glb.py -- <in.glb> <out_dir>
import bpy, sys, math, os
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
src, out = argv[0], argv[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
print("OBJECTS", [(o.name, o.type, len(o.data.vertices), len(o.data.polygons)) for o in meshes])
pts = []
for o in meshes:
    m = o.matrix_world
    co = np.empty(len(o.data.vertices) * 3, np.float32)
    o.data.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    M = np.array(m)
    pts.append(co @ M[:3, :3].T + M[:3, 3])
    print("MATERIALS", [(s.material.name if s.material else None) for s in o.material_slots])
    for s in o.material_slots:
        if s.material and s.material.node_tree:
            for n in s.material.node_tree.nodes:
                if n.type == "TEX_IMAGE" and n.image:
                    print("  IMG", n.image.name, tuple(n.image.size))
pts = np.concatenate(pts)
mn, mx = pts.min(0), pts.max(0)
print("BOUNDS(blender xyz, z up)", mn.round(3), mx.round(3), "size", (mx - mn).round(3))
c = pts.mean(0)
cov = np.cov((pts - c).T)
w, v = np.linalg.eigh(cov)
print("PCA eigvals", w.round(4))
print("PCA axes (cols)", v.round(3))
ctr = (mn + mx) / 2
rad = float(np.linalg.norm(mx - mn)) / 2

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "TEXTURE"
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.film_transparent = False
world = bpy.data.worlds.new("w"); scene.world = world
cam_data = bpy.data.cameras.new("cam"); cam_data.type = "ORTHO"; cam_data.ortho_scale = rad * 2.1
cam = bpy.data.objects.new("cam", cam_data); scene.collection.objects.link(cam); scene.camera = cam
views = {"px": (1, 0, 0), "nx": (-1, 0, 0), "py": (0, 1, 0), "ny": (0, -1, 0), "pz": (0, 0.001, 1), "q": (0.6, -0.7, 0.45)}
for name, d in views.items():
    d = Vector(d).normalized()
    cam.location = Vector(ctr) + d * rad * 4
    cam.rotation_euler = (Vector(ctr) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(out, f"view_{name}.png")
    bpy.ops.render.render(write_still=True)
print("DONE")
