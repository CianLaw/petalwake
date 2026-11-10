# Blender: look at the standing rider asset the way the game will get it.
#   turnaround.png     eight views of rider_stand.glb on its floor line (lit, with its PBR textures)
#   side_by_side.png   standing and seated rider at the same scale, hat bands level: front, side, back
#   placement.png      from in front and above, and from straight above: floor grid (0.25 units), origin,
#                      forward (-Z, blue) and +X (red) bars, markers for hand / broom top / broom base / lantern pivot
#   wind.png           the game's wind shader (src/player/rider.js) applied in numpy: rest, hover, two full-strength frames
#   wind_<part>.png    the same, close on cape, hat, lantern and bristles
# It reads the exported GLB and its JSON sidecar only, so it checks what actually ships.
# Usage: blender -b -P rider_stand_preview.py -- <rider_stand.glb> <out_dir> [<seated rider.glb>]
import bpy, sys, os, json, math, tempfile
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
src, out = argv[0], argv[1]
seated_path = argv[2] if len(argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(src)), "rider.glb")
info = json.load(open(os.path.splitext(src)[0] + ".json"))
os.makedirs(out, exist_ok=True)
tmp = tempfile.mkdtemp(prefix="rider_stand_preview_")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


# ---------------------------------------------------------------- scene helpers
def load(path):
    before = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in scene.objects if o not in before and o.type == "MESH"]
    assert len(new) == 1, f"{path}: expected one mesh, found {len(new)}"
    new[0].rotation_mode = "XYZ"                             # (the importer leaves objects in quaternion mode)
    return new[0]


def gl(p):   # glTF (x, y up, z) -> Blender (x, y, z up)
    return Vector((p[0], -p[2], p[1]))


def positions(me):
    co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    return np.stack([co[:, 0], co[:, 2], -co[:, 1]], -1).astype(np.float64)


def flat(name, rgb):
    m = bpy.data.materials.new(name); m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b: b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = 0.9
    return m


extras = []


def box(a, b, mat):
    """Axis-aligned box between two Blender-space corners."""
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(a + b) / 2)
    o = bpy.context.active_object
    o.scale = (max(abs(b.x - a.x), 1e-4), max(abs(b.y - a.y), 1e-4), max(abs(b.z - a.z), 1e-4))
    o.data.materials.append(mat)
    extras.append(o)
    return o


def clear():
    for o in extras: bpy.data.objects.remove(o)
    extras.clear()


def lights():
    """A soft key, a fill and a sky: enough to see form and the normal map without hiding anything in shadow."""
    w = bpy.data.worlds.new("w"); scene.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.22, 0.235, 0.26, 1); bg.inputs[1].default_value = 1.0
    for name, energy, rot in (("key", 3.2, (50, 0, 150)), ("fill", 1.2, (62, 0, -60)), ("rim", 1.0, (60, 0, 20))):
        d = bpy.data.lights.new(name, "SUN"); d.energy = energy; d.angle = math.radians(12)
        o = bpy.data.objects.new(name, d); scene.collection.objects.link(o)
        o.rotation_euler = tuple(math.radians(v) for v in rot)


def engine(lit):
    """lit: EEVEE with the model's own materials; otherwise Workbench with flat texture colour."""
    if lit:
        scene.render.engine = "BLENDER_EEVEE"
        scene.view_settings.view_transform = "Standard"
        scene.render.film_transparent = False
    else:
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.view_settings.view_transform = "Standard"
        sh = scene.display.shading
        sh.light = "STUDIO"; sh.color_type = "TEXTURE"; sh.show_cavity = False; sh.show_shadows = False
        sh.show_specular_highlight = False; sh.show_backface_culling = False


def snap(center, width, height, ppu, direction=(0, 1, 0)):
    """Orthographic shot of a (width x height) window around center looking along direction -> (h, w, 3) array."""
    cam_data = bpy.data.cameras.new("c"); cam_data.type = "ORTHO"; cam_data.clip_end = 100
    scene.render.resolution_x = int(round(width * ppu)); scene.render.resolution_y = int(round(height * ppu))
    scene.render.resolution_percentage = 100
    cam_data.ortho_scale = max(width, height)
    cam = bpy.data.objects.new("c", cam_data); scene.collection.objects.link(cam); scene.camera = cam
    d = Vector(direction).normalized()
    cam.location = Vector(center) - d * 20
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    path = os.path.join(tmp, "snap.png")
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    im = bpy.data.images.load(path)
    w, h = im.size
    px = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(px)
    bpy.data.images.remove(im)
    return px.reshape(h, w, 4)[::-1, :, :3].copy()


def sheet(path, cells, cols, gap=6):
    rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    ch = max(c.shape[0] for c in cells); cw = max(c.shape[1] for c in cells)
    H_, W_ = len(rows) * ch + (len(rows) - 1) * gap, cols * cw + (cols - 1) * gap
    canvas = np.full((H_, W_, 3), 0.07, np.float32)
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            y0, x0 = r * (ch + gap), c * (cw + gap)
            canvas[y0:y0 + cell.shape[0], x0:x0 + cell.shape[1]] = cell
    rgba = np.concatenate([canvas[::-1], np.ones((H_, W_, 1), np.float32)], -1)
    im = bpy.data.images.new("sheet", W_, H_, alpha=False)
    im.pixels.foreach_set(rgba.reshape(-1))
    im.filepath_raw = path; im.file_format = "PNG"; im.save()
    bpy.data.images.remove(im)
    print("WROTE", path, f"{W_}x{H_}")


def turn(o, angle_deg, at=(0, 0, 0)):
    """Turn a model about the vertical. The camera looks along +Y and she faces +Y: 180 = front, 0 = back, 90 = her left."""
    o.rotation_euler = (0, 0, math.radians(angle_deg)); o.location = at


# ---------------------------------------------------------------- the two models
stand = load(src)
seated = load(seated_path)
sp_ = positions(stand.data); rp_ = positions(seated.data)
H = info["height"]
print("STANDING bounds (glTF)", sp_.min(0).round(4), sp_.max(0).round(4), "tris", len(stand.data.polygons), "verts", len(sp_))
print("SEATED   bounds (glTF)", rp_.min(0).round(4), rp_.max(0).round(4), "tris", len(seated.data.polygons))
assert abs(sp_[:, 1].min()) < 2e-3, "the floor is not at y = 0"
assert abs(sp_[:, 1].max() - H) < 2e-3, "sidecar height does not match the mesh"

WHITE, GREY, DARK = flat("white", (0.85, 0.85, 0.85)), flat("grey", (0.36, 0.36, 0.38)), flat("dark", (0.12, 0.12, 0.13))
RED, GREEN, BLUE, YELLOW = flat("red", (0.95, 0.15, 0.1)), flat("green", (0.1, 0.8, 0.25)), flat("blue", (0.15, 0.4, 1.0)), flat("yellow", (1.0, 0.85, 0.1))
lights()

# ---------------------------------------------------------------- 1. turnaround (lit)
try:
    engine(True)
    seated.hide_render = True
    floor = box((-0.6, -0.6, -0.012), (0.6, 0.6, 0), DARK)
    cells = []
    for a in (180, 135, 90, 45, 0, -45, -90, -135):
        turn(stand, a)
        cells.append(snap((0, 0, H / 2 + 0.02), 1.25, 1.9, 420))
    sheet(os.path.join(out, "turnaround.png"), cells, 4)
except Exception as e:                                       # no GPU in this session: flat texture colour instead
    print("EEVEE failed (%s): Workbench turnaround" % e)
    engine(False)
    cells = []
    for a in (180, 135, 90, 45, 0, -45, -90, -135):
        turn(stand, a)
        cells.append(snap((0, 0, H / 2 + 0.02), 1.25, 1.9, 420))
    sheet(os.path.join(out, "turnaround.png"), cells, 4)
clear(); turn(stand, 0)

# ---------------------------------------------------------------- 2. side by side with the seated rider, same scale
engine(False)
seated.hide_render = False
lift = info["hatBandCenter"][1] - info["seated"]["hatBandCenter"][1]     # hat bands level
print("side by side: seated rider lifted by %.4f so the hat bands are level" % lift)
cells = []
for a, (xs, xr) in ((180, (0.62, -0.62)), (90, (1.12, -0.42)), (0, (0.62, -0.62))):
    turn(stand, a, (xs, 0, 0)); turn(seated, a, (xr, 0, lift))
    for yy in np.arange(0, 1.76, 0.25):                      # rulers every 0.25 model units, behind the figures
        strong = abs(yy / 0.5 - round(yy / 0.5)) < 1e-6
        t = 0.006 if strong else 0.003
        box((-1.55, 2.0, yy - t), (1.55, 2.1, yy + t), WHITE if yy == 0 else (GREY if strong else DARK))
    cells.append(snap((0, 0, 0.84), 3.1, 1.95, 400))
    clear()
sheet(os.path.join(out, "side_by_side.png"), cells, 1)
turn(stand, 0); turn(seated, 0)
seated.hide_render = True

# ---------------------------------------------------------------- 3. placement: origin, forward, markers
box((-1, -1, -0.02), (1, 1, -0.006), DARK)
for g in np.arange(-1.0, 1.01, 0.25):
    box((g - 0.003, -1, -0.006), (g + 0.003, 1, 0), GREY)
    box((-1, g - 0.003, -0.006), (1, g + 0.003, 0), GREY)
box((-0.012, 0, 0), (0.012, 0.7, 0.008), BLUE); box((-0.05, 0.7, 0), (0.05, 0.76, 0.008), BLUE)   # forward: glTF -Z = Blender +Y
box((0, -0.012, 0), (0.35, 0.012, 0.008), RED)                                                      # glTF +X: her right
box((-0.03, -0.03, 0), (0.03, 0.03, 0.014), WHITE)                                                  # origin
for key, mat in (("hand", GREEN), ("broomTop", YELLOW), ("broomBase", YELLOW), ("lanternPivot", RED), ("hatTip", WHITE)):
    p = gl(info[key]); r = 0.02
    box(p - Vector((r, r, r)), p + Vector((r, r, r)), mat)
for f_ in info["feet"].values():
    p = gl(f_); box(p - Vector((0.02, 0.02, 0)), p + Vector((0.02, 0.02, 0.012)), GREEN)
cells = [snap((0, 0, 0.72), 2.3, 2.3, 480, direction=(-0.45, -0.75, -0.48)), snap((0, 0, 0), 2.3, 2.3, 480, direction=(0, 0.001, -1))]
sheet(os.path.join(out, "placement.png"), cells, 2)
clear()

# ---------------------------------------------------------------- 4. the wind shader, in numpy
me = stand.data
W = np.empty(len(me.vertices) * 4, np.float32); me.attributes["_WIND"].data.foreach_get("color", W); W = W.reshape(-1, 4).astype(np.float64)
print("_WIND max per channel", W.max(0).round(3), "verts with weight > 0.02", (W > 0.02).sum(0))
rest = positions(me)
piv = np.array(info["lanternPivot"])


def shader(p, w, t, sp, lantern):
    """transformed = f(position), line for line what Rider._patch adds to the vertex shader."""
    x, y, z = p.T
    o = p.copy()
    ph = z * 10.0 + x * 6.0 - t * 15.0                       # cape
    o += np.stack([np.sin(ph * 0.83 + 1.3) * 0.022, np.sin(ph) * 0.034 + 0.030, 0.030 + 0.020 * np.sin(ph * 0.5)], -1) * (w[:, 0] * sp)[:, None]
    bp = x * 43.0 + y * 37.0 - t * 33.0                      # bristles
    o[:, 0] += np.sin(bp) * 0.011 * w[:, 1] * sp
    o[:, 1] += np.cos(bp * 1.31) * 0.011 * w[:, 1] * sp
    o[:, 1] += np.sin(t * 8.3 + z * 5.0) * 0.016 * w[:, 1] * sp
    o[:, 0] += np.sin(t * 6.1 + z * 4.0) * 0.012 * w[:, 1] * sp
    o[:, 2] += (0.040 + np.sin(t * 11.0 + x * 9.0) * 0.012) * w[:, 2] * sp     # hat
    o[:, 0] += np.sin(t * 7.3 + y * 6.0) * 0.018 * w[:, 2] * sp
    o[:, 1] += np.sin(t * 13.0 + x * 14.0 + z * 9.0) * 0.010 * w[:, 2] * sp
    lp = o - piv                                             # lantern pendulum
    cx, sx, cz, sz = math.cos(lantern[0]), math.sin(lantern[0]), math.cos(lantern[1]), math.sin(lantern[1])
    lp = np.stack([lp[:, 0] * cz - lp[:, 1] * sz, lp[:, 0] * sz + lp[:, 1] * cz, lp[:, 2]], -1)
    lp = np.stack([lp[:, 0], lp[:, 1] * cx - lp[:, 2] * sx, lp[:, 1] * sx + lp[:, 2] * cx], -1)
    return o + (piv + lp - o) * w[:, 3:4]


def pose(p):
    b = np.stack([p[:, 0], -p[:, 2], p[:, 1]], -1).astype(np.float32)
    me.vertices.foreach_set("co", b.reshape(-1)); me.update()


# time, wind strength (uRiderWind: 0.35 hovering, 1 at cruise) and lantern swing (uLantern, radians)
states = [("rest", 0.0, 0.0, (0.0, 0.0)), ("hover", 0.7, 0.35, (0.12, -0.10)), ("full a", 1.9, 1.0, (-0.30, 0.22)), ("full b", 3.3, 1.0, (0.35, -0.25))]
cells = []
for label, t, sp, lan in states:
    p = shader(rest, W, t, sp, lan)
    print("wind %-7s sp %.2f: largest move %.4f, lowest point y %+.4f, straw on the floor moves up to %.4f" % (
        label, sp, np.linalg.norm(p - rest, axis=1).max(), p[:, 1].min(), np.linalg.norm(p - rest, axis=1)[rest[:, 1] < 0.01].max()))
    pose(p)
    for a in (180, 90, 0, -90):
        turn(stand, a)
        cells.append(snap((0, 0, H / 2 + 0.02), 1.3, 1.9, 380))
sheet(os.path.join(out, "wind.png"), cells, 4)
# close on the parts that move: rest above, the two full-strength frames below
focus = {"cape": ((0.0, 1.02, 0.03), 0.66), "hat": ((0.0, 1.43, 0.08), 0.84),
         "lantern": (tuple((piv + np.array(info["lanternCenter"])) / 2), 0.42), "bristles": ((info["broomBase"][0], 0.24, info["broomBase"][2]), 0.64)}
for name, (f, size) in focus.items():
    fb = gl(f)
    cells = []
    for label, t, sp, lan in (states[0], states[2], states[3]):
        pose(shader(rest, W, t, sp, lan))
        for a in (180, 90, 0, -90):
            ar = math.radians(a)
            turn(stand, a, (-(fb.x * math.cos(ar) - fb.y * math.sin(ar)), 0, 0))     # keep the part in the middle
            cells.append(snap((0, 0, fb.z), size, size, 520 / size))
    sheet(os.path.join(out, f"wind_{name}.png"), cells, 4)
pose(rest); turn(stand, 0)
print("PREVIEW DONE", out)
