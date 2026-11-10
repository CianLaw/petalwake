# Blender: the hand-modelled plants and dressing of the six eastern places.
# Every model is built from code: vertex colours (COLOR_0, linear), no textures, and the _WIND
# attribute src/world/places.js reads (r = leaf flutter / translucency, g = how much of the wind's
# lean this vertex takes, b = glow weight, a = 1 - cloth weight). A few hundred triangles each.
# Writes assets/places/models/east_<name>.glb + .json and a contact sheet in art/places_east/preview.
# Usage: blender -b -P place_east_flora.py -- [name ...]        (no names = all)
import bpy, sys, os, json, math, random
import numpy as np
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
OUT = os.path.join(ROOT, "assets", "places", "models")
PREVIEW = os.path.join(ROOT, "art", "places_east", "preview")
os.makedirs(OUT, exist_ok=True); os.makedirs(PREVIEW, exist_ok=True)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
TAU = math.tau


# ------------------------------------------------------------------------------------ toolkit
def lerp(a, b, t): return a + (b - a) * t
def mix3(a, b, t): return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t))
def smooth01(t): t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)


class Geo:
    """Triangles/quads with per-vertex colour and wind weights (flutter, sway, glow, cloth)."""

    def __init__(self):
        self.v, self.c, self.w, self.f, self.sm = [], [], [], [], []

    def add(self, verts, faces, cols, winds, smooth=True):
        o = len(self.v)
        self.v += [tuple(map(float, p)) for p in verts]
        self.c += [tuple(c) for c in cols]
        self.w += [tuple(w) + (0.0,) * (4 - len(w)) for w in winds]
        self.f += [tuple(o + i for i in f) for f in faces]
        self.sm += [smooth] * len(faces)
        return o

    def merge(self, other, M=None):
        vs = other.v if M is None else [tuple(M @ Vector(p)) for p in other.v]
        self.add(vs, other.f, other.c, other.w)
        self.sm[-len(other.f):] = other.sm

    def tris(self):
        return sum(len(f) - 2 for f in self.f)


def frame(d):
    """Two unit vectors perpendicular to d."""
    d = Vector(d).normalized()
    a = Vector((0, 0, 1)) if abs(d.z) < 0.92 else Vector((1, 0, 0))
    u = d.cross(a).normalized()
    return u, d.cross(u).normalized()


def tube(g, path, radii, sides, cols, winds, cap=True, smooth=True, twist=0.0):
    """A generalised cylinder along a polyline. radii/cols/winds: one per path point. Radius 0 closes to a point."""
    path = [Vector(p) for p in path]
    n = len(path)
    rings = []
    verts, vc, vw, faces = [], [], [], []
    prev_u = None
    for i, p in enumerate(path):
        d = (path[min(i + 1, n - 1)] - path[max(i - 1, 0)])
        if d.length < 1e-9: d = Vector((0, 0, 1))
        d.normalize()
        if prev_u is None:
            u, v = frame(d)
        else:
            u = (prev_u - d * prev_u.dot(d))
            u = u.normalized() if u.length > 1e-6 else frame(d)[0]
            v = d.cross(u).normalized()
        prev_u = u
        r = radii[i]
        if r <= 1e-6:
            rings.append([len(verts)]); verts.append(p); vc.append(cols[i]); vw.append(winds[i])
        else:
            ring = []
            for k in range(sides):
                a = TAU * k / sides + twist * i
                ring.append(len(verts)); verts.append(p + (u * math.cos(a) + v * math.sin(a)) * r); vc.append(cols[i]); vw.append(winds[i])
            rings.append(ring)
    for i in range(n - 1):
        a, b = rings[i], rings[i + 1]
        if len(a) == 1 and len(b) == 1: continue
        for k in range(sides):
            k2 = (k + 1) % sides
            if len(a) == 1: faces.append((a[0], b[k], b[k2]))
            elif len(b) == 1: faces.append((a[k], a[k2], b[0]))
            else: faces.append((a[k], a[k2], b[k2], b[k]))
    if cap:
        if len(rings[0]) > 1: faces.append(tuple(reversed(rings[0])))
        if len(rings[-1]) > 1: faces.append(tuple(rings[-1]))
    g.add(verts, faces, vc, vw, smooth)


def lathe(g, profile, sides, cols, winds, center=(0, 0, 0), M=None, smooth=True, wobble=0.0, seed=0, squash=(1, 1)):
    """Surface of revolution about z. profile: [(r, z)], cols/winds one per profile point. wobble jitters the radius."""
    rnd = random.Random(seed)
    jit = [[1 + wobble * (rnd.random() * 2 - 1) for _ in range(sides)] for _ in profile]
    verts, vc, vw, faces, rings = [], [], [], [], []
    for i, (r, z) in enumerate(profile):
        if r <= 1e-6:
            rings.append([len(verts)]); verts.append(Vector((0, 0, z))); vc.append(cols[i]); vw.append(winds[i])
        else:
            ring = []
            for k in range(sides):
                a = TAU * k / sides
                rr = r * jit[i][k]
                ring.append(len(verts)); verts.append(Vector((math.cos(a) * rr * squash[0], math.sin(a) * rr * squash[1], z))); vc.append(cols[i]); vw.append(winds[i])
            rings.append(ring)
    for i in range(len(profile) - 1):
        a, b = rings[i], rings[i + 1]
        if len(a) == 1 and len(b) == 1: continue
        for k in range(sides):
            k2 = (k + 1) % sides
            if len(a) == 1: faces.append((a[0], b[k], b[k2]))
            elif len(b) == 1: faces.append((a[k], a[k2], b[0]))
            else: faces.append((a[k], a[k2], b[k2], b[k]))
    c = Vector(center)
    verts = [(M @ p if M else p) + c for p in verts]
    g.add(verts, faces, vc, vw, smooth)


def blade(g, root, yaw, length, width, lean, curl, col0, col1, wind0, wind1, segs=3):
    """A leaf blade: a tapering strip that leaves the root at `lean` from vertical and curls over by `curl`."""
    root = Vector(root)
    out = Vector((math.cos(yaw), math.sin(yaw), 0)); side = Vector((-math.sin(yaw), math.cos(yaw), 0)); up = Vector((0, 0, 1))
    verts, vc, vw, faces = [], [], [], []
    p = root.copy(); ang = lean
    step = length / segs
    for i in range(segs + 1):
        t = i / segs
        w = width * (1 - t ** 1.5) * (0.55 + 0.45 * min(t * 4, 1))
        col = mix3(col0, col1, t); wd = tuple(lerp(a_, b_, t ** 1.3) for a_, b_ in zip(wind0, wind1))
        if i == segs:
            verts.append(p.copy()); vc.append(col); vw.append(wd)
        else:
            verts.append(p - side * w * 0.5); vc.append(col); vw.append(wd)
            verts.append(p + side * w * 0.5); vc.append(col); vw.append(wd)
        p = p + (out * math.sin(ang) + up * math.cos(ang)) * step
        ang += curl / segs
    for i in range(segs):
        a_ = i * 2
        if i == segs - 1: faces.append((a_, a_ + 1, a_ + 2))
        else: faces.append((a_, a_ + 1, a_ + 3, a_ + 2))
    g.add(verts, faces, vc, vw)


def petal(g, base, direction, up, length, width, col0, col1, wind0, wind1, cup=0.0, mid=0.45, pointed=True):
    """A flat leaf or petal: base, widest at `mid`, to a tip. `cup` lifts the edges."""
    base = Vector(base); d = Vector(direction).normalized(); up = Vector(up).normalized()
    side = d.cross(up).normalized()
    m = base + d * length * mid
    tip = base + d * length
    verts = [base, m - side * width * 0.5 + up * cup * width, m + side * width * 0.5 + up * cup * width, tip]
    cm = mix3(col0, col1, mid); wm = tuple(lerp(a, b, mid) for a, b in zip(wind0, wind1))
    faces = [(0, 2, 1), (1, 2, 3)]
    if not pointed:
        t2 = tip - side * width * 0.3; t3 = tip + side * width * 0.3
        verts = verts[:3] + [t2, t3]; faces = [(0, 2, 1), (1, 2, 4, 3)]
        g.add(verts, faces, [col0, cm, cm, col1, col1], [wind0, wm, wm, wind1, wind1]); return
    g.add(verts, faces, [col0, cm, cm, col1], [wind0, wm, wm, wind1])


def blob(g, center, radii, sides, rings, col_top, col_bot, wind_top, wind_bot, wobble=0.0, seed=0, flat_base=False, smooth=True, M=None):
    """An ellipsoid (or a dome when flat_base) with a colour running bottom to top."""
    rx, ry, rz = radii
    prof, cols, winds = [], [], []
    lo = 0.0 if flat_base else -1.0
    for i in range(rings + 1):
        t = i / rings
        zz = lerp(lo, 1.0, t)
        r = math.sqrt(max(1 - zz * zz, 0.0))
        prof.append((r, zz * rz)); cols.append(mix3(col_bot, col_top, smooth01(t))); winds.append(tuple(lerp(a, b, t) for a, b in zip(wind_bot, wind_top)))
    lathe(g, prof, sides, cols, winds, center=center, M=M, smooth=smooth, wobble=wobble, seed=seed, squash=(rx, ry))


def crystal(g, base, axis, length, radius, sides, col0, col1, tip=0.28, glow=(0.0, 0.0), seed=0):
    """A faceted prism with a point."""
    rnd = random.Random(seed)
    base = Vector(base); axis = Vector(axis).normalized()
    u, v = frame(axis)
    ring0, ring1 = [], []
    for k in range(sides):
        a = TAU * k / sides + rnd.random() * 0.3
        r = radius * (0.85 + 0.3 * rnd.random())
        o = u * math.cos(a) + v * math.sin(a)
        ring0.append(base + o * r * 1.08)
        ring1.append(base + axis * length * (1 - tip) + o * r * 0.86)
    apex = base + axis * length + (u * (rnd.random() - 0.5) + v * (rnd.random() - 0.5)) * radius * 0.5
    verts = ring0 + ring1 + [apex]
    cols = [col0] * sides + [mix3(col0, col1, 0.7)] * sides + [col1]
    winds = [(0, 0, glow[0], 0)] * sides + [(0, 0, lerp(glow[0], glow[1], 0.7), 0)] * sides + [(0, 0, glow[1], 0)]
    faces = []
    for k in range(sides):
        k2 = (k + 1) % sides
        faces.append((k, k2, sides + k2, sides + k))
        faces.append((sides + k, sides + k2, 2 * sides))
    g.add(verts, faces, cols, winds, smooth=False)


def rock(g, center, radii, seed, col_top, col_bot, detail=1, smooth=False, rough=0.22, flat=0.0):
    """A low stone: a jittered subdivided octahedron, optionally flattened underneath."""
    rnd = random.Random(seed)
    vs = [Vector(p) for p in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]
    fs = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
    for _ in range(detail):
        cache, nf = {}, []
        def midp(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache:
                cache[k] = len(vs); vs.append(((vs[a] + vs[b]) / 2).normalized())
            return cache[k]
        for a, b, c in fs:
            ab, bc, ca = midp(a, b), midp(b, c), midp(c, a)
            nf += [(a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)]
        fs = nf
    c = Vector(center)
    out, cols = [], []
    for p in vs:
        k = 1 + rough * (rnd.random() * 2 - 1)
        q = Vector((p.x * radii[0] * k, p.y * radii[1] * k, p.z * radii[2] * k))
        if flat and q.z < -radii[2] * flat: q.z = -radii[2] * flat
        out.append(c + q)
        cols.append(mix3(col_bot, col_top, smooth01(p.z * 0.5 + 0.5)))
    g.add(out, fs, cols, [(0, 0, 0, 0)] * len(out), smooth)


def rot_z(a): return Matrix.Rotation(a, 4, "Z")
def rot_axis(a, axis): return Matrix.Rotation(a, 4, Vector(axis))
def move(v): return Matrix.Translation(Vector(v))


# ------------------------------------------------------------------------------------ export
REGISTRY = {}


def model(name, **info):
    def deco(fn):
        REGISTRY[name] = (fn, info)
        return fn
    return deco


def make_object(name, g):
    me = bpy.data.meshes.new(name)
    me.from_pydata(g.v, [], g.f)
    me.polygons.foreach_set("use_smooth", g.sm)
    n = len(g.v)
    col = me.color_attributes.new(name="Color", type="FLOAT_COLOR", domain="POINT")
    c4 = np.ones((n, 4), np.float32); c4[:, :3] = np.clip(np.array(g.c, np.float32), 0, 1)
    col.data.foreach_set("color", c4.reshape(-1))
    w = np.array(g.w, np.float32).reshape(n, 4).copy()
    w[:, 3] = 1.0 - w[:, 3]                                    # stored as 1 - cloth
    wa = me.attributes.new(name="_WIND", type="FLOAT_COLOR", domain="POINT")
    wa.data.foreach_set("color", np.clip(w, 0, 1).reshape(-1))
    me.color_attributes.active_color = me.color_attributes["Color"]
    me.color_attributes.render_color_index = 0
    me.update()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    mat = bpy.data.materials.get("vcol")
    if mat is None:
        mat = bpy.data.materials.new("vcol"); mat.use_nodes = True
        nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
        ca = nt.nodes.new("ShaderNodeVertexColor"); ca.layer_name = "Color"
        nt.links.new(ca.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.85
        mat.use_backface_culling = False
    me.materials.append(mat)
    return obj


def export(name, g, info):
    for o in list(bpy.context.scene.objects): bpy.data.objects.remove(o)
    obj = make_object(name, g)
    P = np.array(g.v, np.float32)
    height = float(P[:, 2].max())
    rad = float(np.hypot(P[:, 0], P[:, 1]).max())
    low = P[P[:, 2] < max(height * 0.12, 0.05)]
    side = {"name": name, "height": round(height, 3), "tris": g.tris(), "radius": round(rad, 3),
            "baseRadius": round(float(np.percentile(np.hypot(low[:, 0], low[:, 1]), 90)), 3) if len(low) > 2 else round(rad * 0.3, 3),
            "slabs": []}
    side.update(info)
    side.pop("bespoke", None)
    fn_slabs = getattr(REGISTRY[name][0], "slabs", None)
    if fn_slabs is not None: side["slabs"] = fn_slabs
    dst = os.path.join(OUT, f"{name}.glb")
    bpy.ops.object.select_all(action="DESELECT"); obj.select_set(True); bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_attributes=True,
                              export_vertex_color="ACTIVE", export_all_vertex_colors=False, export_active_vertex_color_when_no_material=True,
                              export_tangents=False, export_yup=True, export_apply=True, export_texcoords=False, export_materials="EXPORT")
    json.dump(side, open(os.path.join(OUT, f"{name}.json"), "w"), indent=1)
    return obj, side, os.path.getsize(dst)


def render_sheet(names, path, cell=420, cols=5):
    """All the models side by side, lit from the game's sun."""
    scene = bpy.context.scene
    for o in list(scene.objects): bpy.data.objects.remove(o)
    try: scene.render.engine = "BLENDER_EEVEE"
    except Exception: scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.74, 0.92, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    sd = bpy.data.lights.new("sun", "SUN"); sd.energy = 3.6; sd.color = (1.0, 0.95, 0.86); sd.angle = math.radians(3)
    sun = bpy.data.objects.new("sun", sd); scene.collection.objects.link(sun)
    sun.rotation_euler = Vector((-0.5104, 0.6533, 0.5592)).normalized().to_track_quat("Z", "Y").to_euler()
    gm = bpy.data.meshes.new("ground"); R = 400
    gm.from_pydata([(-R, -R, 0), (R, -R, 0), (R, R, 0), (-R, R, 0)], [], [(0, 1, 2, 3)])
    ground = bpy.data.objects.new("ground", gm); scene.collection.objects.link(ground)
    gmat = bpy.data.materials.new("g"); gmat.use_nodes = True
    gmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.30, 0.36, 0.22, 1)
    gmat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
    gm.materials.append(gmat)
    cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"
    cam = bpy.data.objects.new("c", cd); scene.collection.objects.link(cam); scene.camera = cam
    scene.render.resolution_x = cell; scene.render.resolution_y = cell
    tiles = []
    for nm in names:
        fn, info = REGISTRY[nm]
        g = fn()
        obj = make_object(nm, g)
        P = np.array(g.v, np.float32)
        h = float(P[:, 2].max()); r = float(np.hypot(P[:, 0], P[:, 1]).max())
        ext = max(h, r * 2) * 1.25
        d = Vector((0.62, -0.7, 0.42)).normalized()
        cd.ortho_scale = ext
        cam.location = Vector((0, 0, h * 0.45)) + d * ext * 8
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler(); cd.clip_end = ext * 40
        fp = os.path.join(PREVIEW, f"_tile_{nm}.png"); scene.render.filepath = fp
        bpy.ops.render.render(write_still=True)
        tiles.append(fp)
        bpy.data.objects.remove(obj)
    rows = (len(tiles) + cols - 1) // cols
    sheet = np.zeros((rows * cell, cols * cell, 4), np.float32); sheet[..., 3] = 1
    for i, fp in enumerate(tiles):
        im = bpy.data.images.load(fp)
        buf = np.empty(cell * cell * 4, np.float32); im.pixels.foreach_get(buf)
        r_, c_ = rows - 1 - i // cols, i % cols
        sheet[r_ * cell:(r_ + 1) * cell, c_ * cell:(c_ + 1) * cell] = buf.reshape(cell, cell, 4)
        bpy.data.images.remove(im); os.remove(fp)
    out = bpy.data.images.new("sheet", cols * cell, rows * cell)
    out.pixels.foreach_set(sheet.reshape(-1)); out.filepath_raw = path; out.file_format = "PNG"; out.save()


# ====================================================================================
# 1. The Thousand-Wish Pine: alpine plants of the high scree
# ====================================================================================
@model("east_cushion", sway=0.25, lod0=90, thin=True)
def cushion():
    """Silver-green cushion plant starred with tiny pale flowers."""
    g = Geo(); rnd = random.Random(11)
    blob(g, (0, 0, 0), (0.46, 0.42, 0.26), 10, 4, (0.50, 0.64, 0.46), (0.15, 0.27, 0.15), (0.1, 0.12), (0, 0), wobble=0.10, seed=3, flat_base=True)
    blob(g, (0.30, 0.16, 0), (0.24, 0.22, 0.15), 8, 3, (0.46, 0.60, 0.42), (0.15, 0.27, 0.15), (0.1, 0.12), (0, 0), wobble=0.12, seed=5, flat_base=True)
    for i in range(15):
        a = rnd.random() * TAU; rr = math.sqrt(rnd.random()) * 0.36
        x, y = math.cos(a) * rr, math.sin(a) * rr * 0.92
        z = 0.26 * math.sqrt(max(1 - (x / 0.46) ** 2 - (y / 0.42) ** 2, 0)) + 0.012
        col = (0.99, 0.84, 0.90) if rnd.random() < 0.7 else (0.98, 0.96, 0.92)
        s = 0.035 + 0.02 * rnd.random(); a0 = rnd.random() * TAU
        ctr = Vector((x, y, z + 0.012))
        vs = [ctr] + [ctr + Vector((math.cos(a0 + TAU * k / 5) * s, math.sin(a0 + TAU * k / 5) * s, -0.008)) for k in range(5)]
        g.add(vs, [(0, 1 + k, 1 + (k + 1) % 5) for k in range(5)], [(1.0, 0.86, 0.30)] + [col] * 5, [(0.4, 0.15)] * 6)
    return g


@model("east_skybell", sway=0.7, lod0=80, thin=True)
def skybell():
    """A tuft of deep blue trumpet flowers, wide open to the sky."""
    g = Geo(); rnd = random.Random(21)
    for k in range(7):                                                  # rosette
        a = TAU * k / 7 + rnd.random() * 0.4
        petal(g, (0, 0, 0.01), (math.cos(a), math.sin(a), 0.32), (0, 0, 1), 0.17 + 0.05 * rnd.random(), 0.075,
              (0.07, 0.20, 0.08), (0.16, 0.36, 0.14), (0, 0), (0.3, 0.15), cup=0.25)
    deep, mid, pale = (0.05, 0.11, 0.72), (0.12, 0.26, 0.92), (0.72, 0.86, 1.0)
    for k in range(5):
        a = TAU * k / 5 + rnd.random() * 0.5; rr = 0.05 + 0.10 * rnd.random()
        h = 0.20 + 0.16 * rnd.random()
        root = Vector((math.cos(a) * rr * 0.4, math.sin(a) * rr * 0.4, 0))
        top = Vector((math.cos(a) * rr * 1.6, math.sin(a) * rr * 1.6, h))
        tube(g, [root, (root + top) / 2 + Vector((0, 0, 0.02)), top], [0.011, 0.010, 0.012], 3, [(0.10, 0.26, 0.10)] * 3, [(0, 0), (0.1, 0.5), (0.2, 1.0)], cap=False)
        tilt = rot_axis(0.35 * rnd.random(), (math.sin(a), -math.cos(a), 0))
        R = 0.085 + 0.02 * rnd.random()
        # the trumpet: a narrow tube opening to a five-pointed star
        prof = [(0.014, 0.0), (0.022, 0.05), (0.048, 0.085)]
        lathe(g, prof, 5, [(0.20, 0.36, 0.20), deep, mid], [(0.3, 1.0)] * 3, center=top, M=tilt)
        ring = [tilt @ Vector((math.cos(TAU * j / 5) * 0.048, math.sin(TAU * j / 5) * 0.048, 0.085)) + top for j in range(5)]
        tips = [tilt @ Vector((math.cos(TAU * (j + 0.5) / 5) * R, math.sin(TAU * (j + 0.5) / 5) * R, 0.098)) + top for j in range(5)]
        eye = tilt @ Vector((0, 0, 0.062)) + top
        vs = ring + tips + [eye]
        fs = [(j, (j + 1) % 5, 5 + j) for j in range(5)] + [(10, (j + 1) % 5, j) for j in range(5)]
        g.add(vs, fs, [mid] * 5 + [deep] * 5 + [pale], [(0.8, 1.0)] * 11)
    return g


# ====================================================================================
# 2. The Kettle Pools: what grows on warm mineral ground
# ====================================================================================
@model("east_plume", sway=1.0, lod0=120, thin=True)
def plume():
    """Pale plume reed: arching sage blades and tall cream feathers."""
    g = Geo(); rnd = random.Random(31)
    for k in range(12):
        a = TAU * k / 12 + rnd.random() * 0.5
        L = 1.0 + 0.7 * rnd.random()
        blade(g, (math.cos(a) * 0.06, math.sin(a) * 0.06, 0), a, L, 0.13, 0.10 + 0.2 * rnd.random(), 1.2 + 0.7 * rnd.random(),
              (0.12, 0.26, 0.11), (0.66, 0.70, 0.36), (0.1, 0.0), (0.7, 0.9), segs=4)
    cream, gold = (0.80, 0.75, 0.60), (0.66, 0.52, 0.26)
    for k in range(5):
        a = TAU * k / 5 + rnd.random(); lean = 0.08 + 0.14 * rnd.random()
        H = 1.5 + 0.8 * rnd.random()
        d = Vector((math.cos(a) * math.sin(lean), math.sin(a) * math.sin(lean), math.cos(lean)))
        root = Vector((math.cos(a) * 0.06, math.sin(a) * 0.06, 0))
        p1 = root + d * H * 0.5; p2 = root + d * H + Vector((math.cos(a), math.sin(a), 0)) * 0.05
        tube(g, [root, p1, p2], [0.022, 0.016, 0.012], 3, [(0.30, 0.40, 0.18), (0.56, 0.58, 0.30), (0.74, 0.68, 0.42)], [(0, 0), (0.1, 0.55), (0.3, 0.95)], cap=False)
        # the feather: a fat drooping spindle
        droop = Vector((math.cos(a + 0.6), math.sin(a + 0.6), 0))
        n = 5; path, rad, cols, winds = [], [], [], []
        Lp = 0.75 + 0.25 * rnd.random()
        for i in range(n + 1):
            t = i / n
            path.append(p2 + d * Lp * t * (1 - 0.25 * t) + droop * Lp * 0.42 * t * t)
            rad.append(0.17 * math.sin(math.pi * (0.10 + 0.90 * t) ** 0.75) * (1 - 0.30 * t) + 0.006)
            cols.append(mix3(gold, cream, min(t * 2.4, 1))); winds.append((1.0, 1.0))
        rad[-1] = 0.0
        tube(g, path, rad, 6, cols, winds, cap=True)
    return g


@model("east_embermoss", sway=0.2, lod0=90)
def embermoss():
    """Ember moss: rust-red cushions that like warm ground, with little yellow spore clubs."""
    g = Geo(); rnd = random.Random(41)
    for (x, y, r, s) in ((0, 0, 0.36, 1), (0.30, 0.12, 0.24, 2), (-0.22, 0.24, 0.20, 3), (-0.10, -0.28, 0.22, 4)):
        blob(g, (x, y, 0), (r, r * 0.92, r * 0.42), 8, 3, (0.95, 0.34, 0.08), (0.42, 0.06, 0.03), (0.2, 0.1), (0, 0), wobble=0.14, seed=s, flat_base=True)
    for i in range(16):
        a = rnd.random() * TAU; rr = math.sqrt(rnd.random()) * 0.40
        x, y = math.cos(a) * rr, math.sin(a) * rr
        h = 0.10 + 0.07 * rnd.random()
        z0 = 0.06
        tube(g, [(x, y, z0), (x + 0.01, y, z0 + h * 0.7), (x + 0.012, y, z0 + h)], [0.006, 0.006, 0.014], 3,
             [(0.80, 0.30, 0.06), (0.98, 0.70, 0.12), (1.0, 0.90, 0.30)], [(0.1, 0.2), (0.5, 0.7), (0.8, 1.0)], cap=True)
    return g


# ====================================================================================
# 3. Starfall: what the fallen star left growing
# ====================================================================================
@model("east_glasslily", sway=0.8, lod0=110, glow=[0.62, 0.90, 1.0, 1.2], thin=True)
def glasslily():
    """Glass lily: nodding bells as clear and pale as ice, on a silver stem, tall enough to clear the meadow."""
    g = Geo(); rnd = random.Random(51)
    silver = (0.42, 0.54, 0.60)
    for k in range(5):
        a = TAU * k / 5 + 0.4
        blade(g, (0, 0, 0), a, 0.62 + 0.16 * rnd.random(), 0.085, 0.35, 0.8, (0.14, 0.28, 0.32), (0.46, 0.66, 0.74), (0, 0), (0.6, 0.6), segs=3)
    for s_ in range(3):
        a = TAU * s_ / 3 + rnd.random() * 0.6
        H = 0.95 + 0.35 * rnd.random()
        out = Vector((math.cos(a), math.sin(a), 0))
        p0 = Vector((0, 0, 0)); p1 = out * 0.05 + Vector((0, 0, H * 0.6)); p2 = out * 0.17 + Vector((0, 0, H)); p3 = out * 0.30 + Vector((0, 0, H - 0.07))
        tube(g, [p0, p1, p2, p3], [0.016, 0.013, 0.010, 0.008], 3, [silver] * 4, [(0, 0), (0.1, 0.5), (0.3, 0.9), (0.4, 1.0)], cap=False)
        # the bell hangs mouth down: faceted, six sides
        top = p3; L = 0.24 + 0.06 * rnd.random(); R = 0.12 + 0.03 * rnd.random()
        ice, white, core = (0.46, 0.76, 0.96), (0.80, 0.93, 1.0), (0.20, 0.56, 0.92)
        rings = [(0.016, 0.0, core, 0.9), (R * 0.72, -L * 0.42, ice, 0.6), (R, -L * 0.86, white, 0.5)]
        vs, cs, ws, fs = [], [], [], []
        for (r, z, c, gl) in rings:
            for j in range(6):
                an = TAU * j / 6
                vs.append(top + Vector((math.cos(an) * r, math.sin(an) * r, z))); cs.append(c); ws.append((0.9, 1.0, gl))
        for i in range(2):
            for j in range(6):
                j2 = (j + 1) % 6
                fs.append((i * 6 + j, i * 6 + j2, (i + 1) * 6 + j2, (i + 1) * 6 + j))
        for j in range(6):                                              # six pointed lips
            an = TAU * (j + 0.5) / 6
            vs.append(top + Vector((math.cos(an) * R * 1.22, math.sin(an) * R * 1.22, -L * 1.08))); cs.append(white); ws.append((1.0, 1.0, 0.7))
            fs.append((12 + j, 12 + (j + 1) % 6, 18 + j))
        g.add(vs, fs, cs, ws, smooth=False)
    return g


@model("east_shard", sway=0.0, lod0=140, glow=[0.55, 0.85, 1.0, 1.6], foliage=0.35)
def shard():
    """A spray of star-glass: pale blue crystals pushed up out of the ground."""
    g = Geo(); rnd = random.Random(61)
    deep, pale = (0.10, 0.42, 0.62), (0.86, 0.97, 1.0)
    specs = [(0.0, 0.0, 0.10, 1.05, 0.15), (2.2, 0.50, 0.16, 0.70, 0.11), (4.3, 0.62, 0.20, 0.58, 0.10), (0.9, 0.85, 0.26, 0.40, 0.08), (3.3, 0.32, 0.18, 0.46, 0.085), (5.4, 0.9, 0.20, 0.30, 0.07)]
    for i, (a, tilt, off, L, R) in enumerate(specs):
        axis = Vector((math.cos(a) * math.sin(tilt), math.sin(a) * math.sin(tilt), math.cos(tilt)))
        base = Vector((math.cos(a) * off, math.sin(a) * off, -0.04))
        crystal(g, base, axis, L, R, 5 if i else 6, deep, pale, tip=0.30, glow=(0.15, 1.0), seed=i + 3)
    return g


@model("east_scorchgrass", sway=1.0, lod0=110, thin=True)
def scorchgrass():
    """Cinder grass: soot-dark blades with ash-pale tips, the only thing that took to the burnt ring."""
    g = Geo(); rnd = random.Random(71)
    for k in range(13):
        a = TAU * k / 13 + rnd.random() * 0.5
        L = 0.75 + 0.55 * rnd.random()
        r0 = 0.07 * rnd.random()
        blade(g, (math.cos(a) * r0, math.sin(a) * r0, 0), a, L, 0.15, 0.10 + 0.35 * rnd.random(), 0.7 + 0.8 * rnd.random(),
              (0.016, 0.013, 0.024), (0.105, 0.085, 0.17), (0.02, 0.0), (0.30, 1.0), segs=4)
    return g


@model("east_cinder", sway=0.0, lod0=120, glow=[0.55, 0.85, 1.0, 1.5], foliage=0.0)
def cinder():
    """A fragment that broke off on the way in: black iron with a seam of star-glass."""
    g = Geo()
    rock(g, (0, 0, 0.16), (0.34, 0.27, 0.24), 5, (0.10, 0.085, 0.08), (0.05, 0.04, 0.04), detail=1, rough=0.26, flat=0.6)
    crystal(g, (0.05, 0.02, 0.22), (0.3, 0.2, 1.0), 0.34, 0.07, 5, (0.16, 0.50, 0.70), (0.88, 0.98, 1.0), glow=(0.3, 1.0), seed=9)
    crystal(g, (-0.08, 0.06, 0.20), (-0.5, 0.3, 0.9), 0.22, 0.05, 5, (0.16, 0.50, 0.70), (0.88, 0.98, 1.0), glow=(0.3, 1.0), seed=10)
    return g


# ====================================================================================
# 4. The Conch Garden: things of the reef that learned to live in the air
# ====================================================================================
def branch(g, p, d, L, r, depth, rnd, col0, col1, wind, sides=4, spread=0.75, kids=2, taper=0.68, hmax=1.0):
    """Recursive coral / fan branching: a tapering limb that forks."""
    d = Vector(d).normalized()
    q = p + d * L
    t0 = min(p.z / hmax, 1.0); t1 = min(q.z / hmax, 1.0)
    w0 = (wind[0] * t0, wind[1] * t0 ** 1.3); w1 = (wind[0] * t1, wind[1] * t1 ** 1.3)
    if depth == 0:
        tube(g, [p, q, q + d * r * 1.2], [r, r * 0.8, 0.0], sides, [mix3(col0, col1, 0.55), col1, col1], [w0, w1, w1], cap=False)
        return
    tube(g, [p, q], [r, r * taper], sides, [mix3(col0, col1, 0.25 * (3 - depth)), mix3(col0, col1, 0.25 * (4 - depth))], [w0, w1], cap=False)
    u, v = frame(d)
    a0 = rnd.random() * TAU
    for k in range(kids):
        a = a0 + TAU * k / kids + (rnd.random() - 0.5) * 0.8
        nd = (d + (u * math.cos(a) + v * math.sin(a)) * spread * (0.7 + 0.6 * rnd.random()) + Vector((0, 0, 0.25))).normalized()
        branch(g, q, nd, L * (0.62 + 0.25 * rnd.random()), r * taper, depth - 1, rnd, col0, col1, wind, sides, spread, kids, taper, hmax)


@model("east_coralbush", sway=0.15, lod0=130, foliage=0.4)
def coralbush():
    """Air coral: a knee-high bush of smooth antlers, red at the root and pale at the tips."""
    g = Geo(); rnd = random.Random(81)
    red, tip = (0.80, 0.08, 0.06), (0.98, 0.42, 0.30)
    for k in range(5):
        a = TAU * k / 5 + rnd.random()
        d = Vector((math.cos(a) * 0.55, math.sin(a) * 0.55, 1.0))
        branch(g, Vector((math.cos(a) * 0.07, math.sin(a) * 0.07, 0.0)), d, 0.28 + 0.10 * rnd.random(), 0.075, 2, rnd, red, tip, (0.3, 1.0), sides=4, taper=0.72, hmax=0.95)
    return g


@model("east_seafan", sway=0.5, lod0=130, foliage=0.8, thin=True)
def seafan():
    """Sea fan: a flat violet lace that turns its face across the wind."""
    g = Geo(); rnd = random.Random(91)
    violet, rose = (0.36, 0.10, 0.60), (0.98, 0.50, 0.82)
    H = 1.0
    def rib(p, ang, L, w, depth):
        d = Vector((math.sin(ang), 0, math.cos(ang)))
        q = p + d * L
        t0, t1 = min(p.z / H, 1), min(q.z / H, 1)
        side = Vector((math.cos(ang), 0, -math.sin(ang)))
        w1 = w * 0.66
        vs = [p - side * w, p + side * w, q + side * w1, q - side * w1]
        cs = [mix3(violet, rose, t0 ** 1.3)] * 2 + [mix3(violet, rose, t1 ** 1.3)] * 2
        ws = [(0.5 * t0, t0 ** 1.2)] * 2 + [(0.5 * t1, t1 ** 1.2)] * 2
        g.add(vs, [(0, 1, 2, 3)], cs, ws)
        if depth > 0:
            n = 3 if depth >= 3 else 2
            for k in range(n):
                na = ang + (k - (n - 1) / 2) * (0.50 + 0.16 * rnd.random()) + (rnd.random() - 0.5) * 0.16
                na = max(min(na, 1.35), -1.35)
                rib(q, na, L * (0.70 + 0.16 * rnd.random()), w1, depth - 1)
    tube(g, [(0, 0, 0), (0, 0, 0.14)], [0.045, 0.034], 4, [violet, violet], [(0, 0), (0, 0.02)], cap=False)
    rib(Vector((0, 0, 0.12)), 0.0, 0.24, 0.040, 4)
    return g


@model("east_anemone", sway=1.0, lod0=100, thin=True)
def anemone():
    """Sand anemone: a stout mint stalk crowned with slow pink-tipped fingers."""
    g = Geo(); rnd = random.Random(101)
    mint, pink = (0.50, 0.90, 0.62), (0.98, 0.36, 0.62)
    lathe(g, [(0.10, 0.0), (0.085, 0.10), (0.095, 0.22), (0.12, 0.28), (0.0, 0.26)], 8,
          [(0.80, 0.62, 0.44), (0.92, 0.74, 0.56), (0.70, 0.88, 0.62), mint, (0.95, 0.80, 0.50)], [(0, 0), (0, 0.1), (0.1, 0.3), (0.2, 0.4), (0.2, 0.4)])
    for ring, (n, R, L, up) in enumerate(((10, 0.10, 0.34, 0.75), (8, 0.06, 0.28, 1.15))):
        for k in range(n):
            a = TAU * (k + 0.5 * ring) / n + rnd.random() * 0.2
            out = Vector((math.cos(a), math.sin(a), 0))
            p0 = out * R + Vector((0, 0, 0.27))
            pts, rad, cols, winds = [], [], [], []
            ang = up
            p = p0.copy()
            for i in range(4):
                t = i / 3
                pts.append(p.copy()); rad.append(0.020 * (1 - 0.55 * t)); cols.append(mix3(mint, pink, smooth01(t * 1.15))); winds.append((0.7 * t, 0.4 + 0.6 * t))
                p = p + (out * math.cos(ang) + Vector((0, 0, 1)) * math.sin(ang)) * (L / 3)
                ang += 0.35 + 0.2 * rnd.random()
            rad[-1] = 0.0
            tube(g, pts, rad, 3, cols, winds, cap=False)
    return g


@model("east_scallop", sway=0.0, lod0=80, foliage=0.0, thin=True)
def scallop():
    """A scallop shell, ribbed in cream and coral, half sunk in the sand."""
    g = Geo()
    n = 9; R = 0.24
    lift = rot_axis(-0.9, (1, 0, 0))                           # stands leaning back
    vs, cs = [Vector((0, 0, 0))], [(0.92, 0.80, 0.70)]
    for k in range(n * 2 + 1):
        a = lerp(-1.15, 1.15, k / (n * 2))
        ridge = (k % 2 == 0)
        rr = R * (1.0 if ridge else 0.93) * (0.93 + 0.07 * math.cos(a * 1.4))
        vs.append(Vector((math.sin(a) * rr, 0.035 if ridge else 0.006, math.cos(a) * rr)))
        cs.append((0.99, 0.93, 0.84) if ridge else (0.96, 0.52, 0.42))
    fs = [(0, k + 1, k + 2) for k in range(n * 2)]
    # the two ears at the hinge
    vs += [Vector((-0.09, 0.0, 0.0)), Vector((0.09, 0.0, 0.0)), Vector((-0.07, 0.0, 0.07)), Vector((0.07, 0.0, 0.07))]
    cs += [(0.90, 0.76, 0.66)] * 4
    b = len(vs) - 4
    fs += [(0, b, b + 2), (0, b + 3, b + 1)]
    vs = [lift @ p + Vector((0, 0, 0.02)) for p in vs]
    g.add(vs, fs, cs, [(0, 0, 0, 0)] * len(vs), smooth=False)
    return g


@model("east_starfish", sway=0.0, lod0=80, foliage=0.0, thin=True)
def starfish():
    """A fat orange starfish, one arm curled."""
    g = Geo()
    orange, pale = (0.98, 0.42, 0.10), (1.0, 0.76, 0.48)
    vs, cs, fs = [Vector((0, 0, 0.055))], [pale], []
    for k in range(5):
        a = TAU * k / 5
        tip = Vector((math.cos(a) * 0.24, math.sin(a) * 0.24, 0.012 + (0.07 if k == 2 else 0)))
        for da in (-0.63, 0.63):
            vs.append(Vector((math.cos(a + da) * 0.075, math.sin(a + da) * 0.075, 0.0))); cs.append(orange)
        vs.append(tip); cs.append(orange)
        ridge = Vector((math.cos(a) * 0.12, math.sin(a) * 0.12, 0.045)); vs.append(ridge); cs.append(pale)
        b = 1 + k * 4
        fs += [(0, b, b + 3), (0, b + 3, b + 1), (b, b + 2, b + 3), (b + 3, b + 2, b + 1)]
        nb = 1 + ((k + 1) % 5) * 4
        fs.append((0, b + 1, nb))
    g.add(vs, fs, cs, [(0, 0, 0, 0)] * len(vs), smooth=True)
    return g


# ====================================================================================
# 5. Lantern Roots: the lagoon's edge
# ====================================================================================
@model("east_lotus", sway=0.6, lod0=110, thin=True)
def lotus():
    """Lagoon lotus: it roots on the seabed and holds its leaves and one peach bloom clear of the water."""
    g = Geo(); rnd = random.Random(111)
    stem = (0.22, 0.40, 0.24)
    # three leaves on long stalks: shallow bowls
    for k, (a, rr, h, R) in enumerate(((0.3, 0.42, 1.30, 0.44), (2.5, 0.50, 1.12, 0.36), (4.4, 0.34, 1.45, 0.30))):
        top = Vector((math.cos(a) * rr, math.sin(a) * rr, h))
        tube(g, [(0, 0, 0), top * 0.5 + Vector((0, 0, 0.05)), top], [0.022, 0.018, 0.016], 3, [stem] * 3, [(0, 0), (0, 0.5), (0.1, 1.0)], cap=False)
        tilt = rot_axis(0.25, (math.sin(a), -math.cos(a), 0))
        n = 10; vs = [tilt @ Vector((0, 0, -0.03)) + top]; cs = [(0.20, 0.50, 0.34)]; ws = [(0.3, 1.0)]
        for j in range(n):
            an = TAU * j / n
            notch = 0.62 if j == 0 else 1.0
            wav = 1 + 0.07 * math.sin(an * 5 + k)
            vs.append(tilt @ Vector((math.cos(an) * R * notch * wav, math.sin(an) * R * notch * wav, 0.05 * wav)) + top)
            cs.append((0.07, 0.36, 0.26) if j % 2 else (0.12, 0.46, 0.32)); ws.append((0.9, 1.0))
        g.add(vs, [(0, 1 + j, 1 + (j + 1) % n) for j in range(n)], cs, ws)
    # the bloom
    H = 1.62
    tube(g, [(0, 0, 0), (0.03, 0.02, H * 0.55), (0.0, 0.0, H)], [0.022, 0.018, 0.016], 3, [stem] * 3, [(0, 0), (0, 0.5), (0.1, 1.0)], cap=False)
    c = Vector((0, 0, H))
    peach, cream, rose = (1.0, 0.56, 0.50), (1.0, 0.94, 0.84), (0.98, 0.36, 0.48)
    for ring, (n, L, tilt, w) in enumerate(((8, 0.30, 0.35, 0.15), (7, 0.25, 0.85, 0.13), (5, 0.19, 1.25, 0.10))):
        for j in range(n):
            a = TAU * (j + 0.5 * ring) / n
            d = Vector((math.cos(a) * math.cos(tilt), math.sin(a) * math.cos(tilt), math.sin(tilt)))
            up = Vector((-math.cos(a) * math.sin(tilt), -math.sin(a) * math.sin(tilt), math.cos(tilt)))
            petal(g, c + Vector((math.cos(a), math.sin(a), 0)) * 0.03, d, up, L, w, rose if ring == 0 else peach, cream, (0.6, 1.0), (1.0, 1.0), cup=0.35, mid=0.5)
    blob(g, c + Vector((0, 0, 0.06)), (0.055, 0.055, 0.05), 6, 2, (1.0, 0.86, 0.22), (0.86, 0.62, 0.12), (0.3, 1.0), (0.3, 1.0))
    return g


@model("east_lanternberry", sway=0.8, lod0=100, glow=[1.0, 0.62, 0.22, 0.9], thin=True)
def lanternberry():
    """Lantern-berry: a low shore bush that hangs out its seed pods like paper lamps."""
    g = Geo(); rnd = random.Random(121)
    leaf0, leaf1 = (0.10, 0.28, 0.12), (0.30, 0.52, 0.18)
    orange, deep = (1.0, 0.46, 0.08), (0.80, 0.20, 0.04)
    for k in range(6):
        a = TAU * k / 6 + rnd.random() * 0.5
        out = Vector((math.cos(a), math.sin(a), 0))
        L = 0.42 + 0.2 * rnd.random()
        p0 = Vector((0, 0, 0)); p1 = out * L * 0.45 + Vector((0, 0, L * 0.75)); p2 = out * L + Vector((0, 0, L * 0.95))
        tube(g, [p0, p1, p2], [0.016, 0.011, 0.007], 3, [(0.20, 0.22, 0.10), (0.24, 0.32, 0.12), (0.30, 0.42, 0.14)], [(0, 0), (0.1, 0.6), (0.3, 1.0)], cap=False)
        for j, t in enumerate((0.35, 0.6, 0.85, 1.0)):
            q = p0.lerp(p1, t / 0.5) if t < 0.5 else p1.lerp(p2, (t - 0.5) / 0.5)
            sgn = 1 if j % 2 else -1
            d = (out * 0.5 + Vector((-out.y, out.x, 0)) * sgn * 0.9 + Vector((0, 0, 0.25))).normalized()
            petal(g, q, d, (0, 0, 1), 0.17, 0.10, leaf0, leaf1, (0.4, t), (0.9, t), cup=0.2)
        # a pod hanging from the arch of the stem
        for t in ((0.7,) if k % 2 else (0.55, 0.95)):
            q = p1.lerp(p2, (t - 0.5) / 0.5) if t >= 0.5 else p0.lerp(p1, t / 0.5)
            top = q + Vector((0, 0, -0.03)); Lp = 0.20 + 0.04 * rnd.random()
            prof = [(0.0, 0.0), (0.060, -Lp * 0.30), (0.078, -Lp * 0.58), (0.0, -Lp)]
            lathe(g, prof, 5, [deep, orange, orange, (1.0, 0.70, 0.20)], [(0.5, 1.0, 0.3), (0.6, 1.0, 0.9), (0.6, 1.0, 1.0), (0.6, 1.0, 0.6)], center=top, smooth=False)
    return g


# ====================================================================================
# 6. The Whalebone Arbour: what the salt wind lets grow on the long beach
# ====================================================================================
@model("east_thrift", sway=0.8, lod0=90, thin=True)
def thrift():
    """Sea-thrift: a tight green cushion holding up a crowd of pink pompoms."""
    g = Geo(); rnd = random.Random(131)
    blob(g, (0, 0, 0), (0.24, 0.22, 0.13), 8, 3, (0.20, 0.42, 0.16), (0.07, 0.18, 0.07), (0.3, 0.2), (0, 0), wobble=0.12, seed=7, flat_base=True)
    for k in range(18):                                                  # a ruff of grassy leaves
        a = TAU * k / 18 + rnd.random() * 0.3
        blade(g, (math.cos(a) * 0.12, math.sin(a) * 0.12, 0.02), a, 0.16 + 0.06 * rnd.random(), 0.028, 0.7, 0.8, (0.08, 0.22, 0.08), (0.26, 0.48, 0.18), (0.1, 0.1), (0.6, 0.5), segs=2)
    pinks = [(0.96, 0.34, 0.60), (1.0, 0.56, 0.76), (0.90, 0.22, 0.52), (1.0, 0.76, 0.88)]
    for k in range(10):
        a = TAU * k / 10 + rnd.random() * 0.6; rr = 0.04 + 0.13 * rnd.random()
        h = 0.26 + 0.16 * rnd.random()
        root = Vector((math.cos(a) * rr, math.sin(a) * rr, 0.08))
        top = Vector((math.cos(a) * rr * 1.7, math.sin(a) * rr * 1.7, h))
        tube(g, [root, top], [0.007, 0.006], 3, [(0.20, 0.36, 0.14), (0.40, 0.44, 0.22)], [(0.1, 0.25), (0.3, 1.0)], cap=False)
        c = pinks[k % len(pinks)]
        blob(g, top + Vector((0, 0, 0.03)), (0.052, 0.052, 0.042), 5, 2, mix3(c, (1, 1, 1), 0.25), mix3(c, (0.5, 0.1, 0.3), 0.35), (0.9, 1.0), (0.9, 1.0), wobble=0.12, seed=k)
    return g


@model("east_seaholly", sway=0.55, lod0=100, thin=True)
def seaholly():
    """Sea-holly: steel-blue thistle heads on silver ruffs."""
    g = Geo(); rnd = random.Random(141)
    silver, steel, blue = (0.56, 0.68, 0.74), (0.34, 0.48, 0.70), (0.20, 0.32, 0.78)
    for k in range(7):                                                   # spiny basal leaves
        a = TAU * k / 7 + rnd.random() * 0.4
        d = Vector((math.cos(a), math.sin(a), 0.35)).normalized()
        base = Vector((math.cos(a) * 0.03, math.sin(a) * 0.03, 0.02))
        side = Vector((-math.sin(a), math.cos(a), 0))
        L = 0.26 + 0.08 * rnd.random()
        vs = [base, base + d * L * 0.35 + side * 0.07, base + d * L * 0.5 + side * 0.03, base + d * L * 0.75 + side * 0.06, base + d * L,
              base + d * L * 0.75 - side * 0.06, base + d * L * 0.5 - side * 0.03, base + d * L * 0.35 - side * 0.07]
        g.add(vs, [(0, 1, 2), (0, 2, 6), (0, 6, 7), (2, 3, 4), (2, 4, 6), (6, 4, 5)], [(0.30, 0.44, 0.40)] + [(0.50, 0.64, 0.60)] * 7, [(0, 0)] + [(0.4, 0.3)] * 7)
    def head(top, d, s):
        u, v = frame(d)
        for j in range(8):                                               # the ruff
            an = TAU * j / 8
            o = (u * math.cos(an) + v * math.sin(an))
            dd = (o + d * 0.30).normalized()
            petal(g, top, dd, d, 0.15 * s, 0.05 * s, steel, silver, (0.5, 1.0), (0.9, 1.0), cup=0.1, mid=0.35)
        prof = [(0.036 * s, 0.0), (0.048 * s, 0.035 * s), (0.036 * s, 0.085 * s), (0.0, 0.115 * s)]
        M = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
        lathe(g, prof, 6, [steel, blue, blue, (0.42, 0.56, 0.94)], [(0.4, 1.0)] * 4, center=top, M=M, smooth=False)
    stems = [((0.0, 0.0), 0.66, 0.05, 1.0), ((0.9, 0.5), 0.46, 0.5, 0.8), ((3.0, 0.5), 0.52, 0.42, 0.85), ((4.6, 0.4), 0.40, 0.6, 0.72), ((2.0, 0.3), 0.34, 0.7, 0.66)]
    for (a, _), H, lean, s in stems:
        d = Vector((math.cos(a) * math.sin(lean), math.sin(a) * math.sin(lean), math.cos(lean)))
        top = d * H
        tube(g, [(0, 0, 0), top * 0.5, top], [0.016, 0.012, 0.010], 3, [(0.34, 0.46, 0.42), silver, silver], [(0, 0), (0.1, 0.5), (0.3, 1.0)], cap=False)
        head(top, d, s)
    return g


# ====================================================================================
# Dressing: stones, posts, lamps
# ====================================================================================
GREY = [(0.40, 0.40, 0.38), (0.48, 0.47, 0.44), (0.34, 0.35, 0.34), (0.52, 0.50, 0.46)]


@model("east_cairnlet", sway=0.0, foliage=0.0, slabs=[[0, 0, 0.42, 0, 0.55], [0, 0, 0.26, 0.55, 1.15]])
def cairnlet():
    """A wayfarer's cairn: six flat stones, each a little smaller than the one beneath."""
    g = Geo(); rnd = random.Random(151)
    z = 0.0
    for i in range(6):
        t = i / 5
        rx = lerp(0.44, 0.13, t) * (0.9 + 0.2 * rnd.random()); ry = rx * (0.72 + 0.25 * rnd.random()); rz = lerp(0.13, 0.07, t)
        c = GREY[i % len(GREY)]
        lich = mix3(c, (0.80, 0.50, 0.14), 0.35) if i in (1, 4) else mix3(c, (0.60, 0.70, 0.52), 0.25)
        sub = Geo()
        rock(sub, (0, 0, 0), (rx, ry, rz), 200 + i, lich, mix3(c, (0, 0, 0), 0.35), detail=1, rough=0.16)
        g.merge(sub, move(((rnd.random() - 0.5) * 0.07, (rnd.random() - 0.5) * 0.07, z + rz * 0.9)) @ rot_z(rnd.random() * TAU))
        z += rz * 1.72
    return g


@model("east_stepstone", sway=0.0, foliage=0.0, collide=False)
def stepstone():
    """A stepping stone of the same pale mineral the pools are made of."""
    g = Geo()
    rock(g, (0, 0, 0.03), (0.62, 0.48, 0.13), 301, (0.80, 0.76, 0.64), (0.50, 0.46, 0.38), detail=1, rough=0.14, flat=0.3)
    return g


@model("east_bucket", sway=0.0, foliage=0.0, collide=False)
def bucket():
    """A cedar bathing pail and its dipper, left on the rim for whoever comes next."""
    g = Geo()
    wood, dark, hoop = (0.50, 0.33, 0.18), (0.30, 0.19, 0.10), (0.16, 0.13, 0.10)
    prof = [(0.26, 0.0), (0.27, 0.04), (0.27, 0.10), (0.29, 0.10), (0.29, 0.14), (0.285, 0.14), (0.30, 0.34), (0.32, 0.34), (0.32, 0.38), (0.305, 0.38), (0.31, 0.46), (0.285, 0.46), (0.275, 0.20), (0.0, 0.20)]
    cols = [dark, wood, wood, hoop, hoop, wood, wood, hoop, hoop, wood, wood, wood, dark, (0.30, 0.66, 0.68)]
    lathe(g, prof, 10, cols, [(0, 0)] * len(prof), smooth=False)
    prof2 = [(0.275, 0.40), (0.0, 0.40)]                                 # the water
    lathe(g, prof2, 10, [(0.36, 0.78, 0.78), (0.50, 0.88, 0.86)], [(0, 0)] * 2)
    # the dipper: a cup on a long handle, leaning on the rim
    M = move((0.20, 0.05, 0.47)) @ rot_z(0.5) @ rot_axis(-0.42, (0, 1, 0))
    sub = Geo()
    lathe(sub, [(0.0, -0.07), (0.075, -0.06), (0.09, 0.03), (0.075, 0.03), (0.065, -0.04), (0.0, -0.045)], 7, [wood] * 4 + [dark] * 2, [(0, 0)] * 6)
    tube(sub, [(0.08, 0, 0.0), (0.55, 0, 0.02)], [0.016, 0.014], 4, [wood, wood], [(0, 0)] * 2)
    g.merge(sub, M)
    return g


def paper_lantern(g, top, R=0.20, H=0.34, glow=1.0, sway=0.2, col=(1.0, 0.50, 0.14), pale=(1.0, 0.82, 0.50)):
    """A round paper lantern hanging from `top` (the cord's upper end)."""
    top = Vector(top)
    tube(g, [top, top - Vector((0, 0, 0.14))], [0.008, 0.008], 3, [(0.12, 0.10, 0.08)] * 2, [(0, sway * 0.5), (0, sway)], cap=False)
    c = top - Vector((0, 0, 0.14 + H * 0.5))
    prof, cols, winds = [], [], []
    n = 6
    for i in range(n + 1):
        t = i / n
        zz = lerp(H * 0.5, -H * 0.5, t)
        r = R * math.sin(math.pi * lerp(0.16, 0.84, t)) ** 0.8
        prof.append((r, zz)); cols.append(mix3(col, pale, math.sin(math.pi * t) ** 2 * 0.75)); winds.append((0.0, sway, glow * (0.5 + 0.5 * math.sin(math.pi * t))))
    lathe(g, [(R * 0.34, H * 0.5 + 0.03)] + prof + [(R * 0.34, -H * 0.5 - 0.03)], 8,
          [(0.10, 0.08, 0.07)] + cols + [(0.10, 0.08, 0.07)], [(0, sway, 0)] + winds + [(0, sway, 0)], center=c)
    # a tassel
    tube(g, [c - Vector((0, 0, H * 0.5 + 0.03)), c - Vector((0, 0, H * 0.5 + 0.22))], [0.012, 0.0], 3, [(0.80, 0.16, 0.10)] * 2, [(0.5, sway), (1.0, sway * 1.5)], cap=False)


@model("east_moorpost", sway=1.0, foliage=0.0, glow=[1.0, 0.62, 0.30, 5.0], slabs=[[0, 0, 0.2, 0, 3.2]], solid=[[0, 0, 0.16, 0, 3.2]])
def moorpost():
    """A mooring post with a lamp on its arm. The post stands a metre deep in the lagoon."""
    g = Geo()
    wood, wet, rope = (0.34, 0.25, 0.17), (0.16, 0.14, 0.11), (0.62, 0.52, 0.34)
    lathe(g, [(0.15, 0.0), (0.14, 1.3), (0.125, 2.2), (0.12, 3.05), (0.09, 3.15), (0.0, 3.17)], 7,
          [wet, wet, wood, wood, (0.44, 0.34, 0.24), (0.44, 0.34, 0.24)], [(0, 0)] * 6, wobble=0.05, seed=4, smooth=True)
    for z0 in (1.55, 1.63, 1.71):                                         # a few turns of mooring rope
        lathe(g, [(0.150, z0 - 0.035), (0.175, z0), (0.150, z0 + 0.035)], 7, [rope] * 3, [(0, 0)] * 3)
    tube(g, [(0.0, 0, 2.86), (0.34, 0, 2.94), (0.62, 0, 2.90)], [0.035, 0.03, 0.022], 4, [wood] * 3, [(0, 0), (0, 0.02), (0, 0.05)])
    paper_lantern(g, (0.58, 0, 2.88), R=0.21, H=0.36, glow=1.0, sway=0.16)
    return g


@model("east_pearl", sway=0.0, foliage=0.0, collide=False, glow=[0.95, 0.90, 1.0, 1.1])
def pearl():
    """The Moon Pearl."""
    g = Geo()
    n, m = 14, 9
    prof, cols, winds = [], [], []
    for i in range(m + 1):
        t = i / m
        zz = math.cos(math.pi * t)
        r = math.sin(math.pi * t)
        # a soft sheen that runs from rose at the foot through white to a cool blue cap
        c = mix3((0.98, 0.80, 0.86), (0.98, 0.97, 0.94), smooth01(t * 1.6)) if t > 0.5 else mix3((0.80, 0.90, 1.0), (0.98, 0.97, 0.94), smooth01((1 - t) * 0 + t * 2))
        prof.append((r * 0.34, zz * 0.34 + 0.34)); cols.append(c); winds.append((0, 0, 0.7 + 0.3 * math.sin(math.pi * t)))
    lathe(g, prof, n, cols, winds)
    return g


@model("east_starglass", sway=0.0, foliage=0.25, glow=[0.55, 0.85, 1.0, 1.8],
       slabs=[[0, 0, 0.75, 0, 0.9], [0.05, 0, 0.5, 0.9, 1.8], [0.1, 0, 0.3, 1.8, 2.7]])
def starglass():
    """Star-glass: where the star's skin splashed and froze, in blades taller than a rider."""
    g = Geo()
    deep, pale = (0.07, 0.34, 0.56), (0.80, 0.96, 1.0)
    specs = [(0.0, 0.10, 0.0, 2.75, 0.34), (1.9, 0.42, 0.42, 1.75, 0.26), (4.0, 0.55, 0.46, 1.45, 0.22), (0.7, 0.80, 0.60, 1.0, 0.17), (3.0, 0.72, 0.52, 1.15, 0.19), (5.2, 0.95, 0.55, 0.75, 0.15), (2.6, 1.15, 0.70, 0.55, 0.12)]
    for i, (a, tilt, off, L, R) in enumerate(specs):
        axis = Vector((math.cos(a) * math.sin(tilt), math.sin(a) * math.sin(tilt), math.cos(tilt)))
        base = Vector((math.cos(a) * off, math.sin(a) * off, -0.12))
        crystal(g, base, axis, L, R, 6 if i < 2 else 5, deep, pale, tip=0.26, glow=(0.10, 1.0), seed=i + 31)
    return g


@model("east_ribarch", sway=0.0, foliage=0.0, collide=False, baseRadius=0.5,
       slabs=[[-2.55, 0, 0.32, 0, 2.6], [2.55, 0, 0.32, 0, 2.6], [-2.2, 0, 0.3, 2.6, 4.6], [2.2, 0, 0.3, 2.6, 4.6],
              [-1.25, 0, 0.3, 4.6, 6.0], [1.25, 0, 0.3, 4.6, 6.0], [0, 0, 0.45, 5.9, 6.9]])
def ribarch():
    """Two great ribs set in the sand and lashed at the top: one arch of the walk that leads to the old singer."""
    g = Geo(); rnd = random.Random(191)
    ivory, pale, moss, stain = (0.80, 0.74, 0.60), (0.90, 0.86, 0.74), (0.34, 0.42, 0.20), (0.62, 0.50, 0.30)
    for sgn in (-1, 1):
        n = 10; path, rad, cols = [], [], []
        lean = 0.10 * rnd.random()
        for i in range(n + 1):
            t = i / n
            x = sgn * (2.62 * (1 - t ** 2.3) + 0.42 * math.sin(math.pi * t) - 0.30 * t)   # the tips cross a little
            y = (rnd.random() - 0.5) * 0.05 + sgn * 0.16 * t + lean * math.sin(math.pi * t)
            z = -0.45 + 7.25 * math.sin(t * math.pi / 2) ** 0.92
            path.append((x, y, z))
            rad.append(lerp(0.33, 0.20, t ** 0.7) * (1 - 0.55 * t ** 3))
            c = mix3(moss, ivory, smooth01((z - 0.2) / 1.6))
            c = mix3(c, stain, 0.35 * (0.5 + 0.5 * math.sin(t * 9.0 + sgn)))
            cols.append(mix3(c, pale, smooth01((t - 0.55) / 0.45) * 0.7))
        rad[-1] = 0.10
        tube(g, path, rad, 6, cols, [(0, 0)] * (n + 1), cap=True)
    # the lashing where they cross: a fat knot of old rope and its two loose ends
    rope = (0.50, 0.40, 0.24)
    blob(g, (0.0, 0.0, 6.76), (0.24, 0.36, 0.22), 7, 4, rope, mix3(rope, (0, 0, 0), 0.35), (0, 0), (0, 0), wobble=0.10, seed=5)
    for sx_, L_ in ((0.10, 0.9), (-0.08, 0.6)):
        tube(g, [(sx_, 0.20, 6.66), (sx_ * 1.4, 0.26, 6.66 - L_ * 0.5), (sx_ * 1.2, 0.24, 6.66 - L_)], [0.035, 0.03, 0.02], 4, [rope] * 3, [(0, 0)] * 3)
    return g


# ====================================================================================
# Made to measure: pieces fitted to the ground and the trees they belong to
# ====================================================================================
def gl(p):
    """A point given in game/model axes (x, y up, z) -> Blender (x, -z, y)."""
    return Vector((p[0], -p[2], p[1]))


PAPER = [(0.93, 0.91, 0.84), (0.80, 0.15, 0.11), (0.93, 0.91, 0.84), (0.95, 0.93, 0.86), (0.84, 0.20, 0.13), (0.92, 0.74, 0.34)]


def paper_strip(g, top, face, length, width, col, sway, forked=False):
    """A strip of paper hanging from `top`: tied at the top (cloth 0), free at the bottom (cloth 1)."""
    top = Vector(top); face = Vector(face); face.z = 0
    face = face.normalized() if face.length > 1e-6 else Vector((1, 0, 0))
    side = Vector((-face.y, face.x, 0))
    rows = 4
    vs, cs, ws, fs = [], [], [], []
    for i in range(rows):
        t = i / (rows - 1)
        zc = top.z - length * t
        for sgn in (-1, 1):
            notch = 0.035 if (forked and i == rows - 1) else 0.0
            vs.append(Vector((top.x, top.y, zc + notch * 0)) + side * sgn * width * 0.5 + face * 0.012 * math.sin(t * 5.0))
            cs.append(mix3(col, (1, 1, 1), 0.10 * t)); ws.append((0.5 * t, sway, 0.0, t))
    for i in range(rows - 1):
        a_ = i * 2
        fs.append((a_, a_ + 1, a_ + 3, a_ + 2))
    if forked:                                                          # a swallow-tail
        b_ = len(vs)
        vs.append(Vector((top.x, top.y, top.z - length * 0.86))); cs.append(col); ws.append((0.5, sway, 0.0, 0.86))
        fs[-1] = (b_ - 4, b_ - 3, b_)
        fs += [(b_ - 4, b_, b_ - 2), (b_ - 3, b_ - 1, b_)]
    g.add(vs, fs, cs, ws)


@model("east_charms", sway=1.0, foliage=0.55, thin=True, cloth=[0.30, 0.11], collide=False, baseRadius=0.3, bespoke=True)
def charms():
    """The wish lines of the pine: ropes strung from its trunk to poles on the shelf, hung with paper, and
    strips tied under its limbs. Built in the pine's own model space and placed exactly like the pine."""
    import place_east_layout as L
    spec = L.charms_spec()
    g = Geo(); rnd = random.Random(171)
    H = spec["height"]
    wood, straw = (0.34, 0.24, 0.16), (0.62, 0.50, 0.30)
    trunk = Vector(gl(spec["trunk"]))
    slabs = []
    k = 0
    for ln in spec["lines"]:
        px, py, pz = ln["pole"]
        base = gl((px, py - 0.35, pz)); u = Vector((px, -pz, 0)).normalized()
        topp = gl((px, py + 2.55, pz)) + u * 0.22                       # the pole leans a little away from the tree
        tube(g, [base, base.lerp(topp, 0.5), topp], [0.085, 0.07, 0.055], 6, [mix3(wood, (0, 0, 0), 0.3), wood, mix3(wood, (1, 1, 1), 0.12)], [(0, 0)] * 3)
        lathe(g, [(0.075, -0.03), (0.09, 0.02), (0.0, 0.10)], 6, [straw] * 3, [(0, 0)] * 3, center=topp)
        slabs.append([round(px, 3), round(pz, 3), 0.12, round(py, 3), round(py + 2.6, 3)])
        A = trunk + u * 0.55
        Bp = topp - Vector((0, 0, 0.08))
        Lr = (Bp - A).length; sag = 0.055 * Lr
        n = 12; path = []
        for i in range(n + 1):
            t = i / n
            path.append(A.lerp(Bp, t) - Vector((0, 0, sag * 4 * t * (1 - t))))
        gA = (spec["trunk"][1] / H) ** 1.6
        tube(g, path, [0.018] * (n + 1), 3, [straw] * (n + 1), [(0, gA * (1 - i / n)) for i in range(n + 1)], cap=False)
        m = max(int(Lr / 0.68), 3)
        for j in range(m):
            t = (j + 0.6) / (m + 0.2)
            q = A.lerp(Bp, t) - Vector((0, 0, sag * 4 * t * (1 - t) + 0.015))
            face = (Bp - A).cross(Vector((0, 0, 1)))
            face = rot_z((rnd.random() - 0.5) * 1.2) @ face
            paper_strip(g, q, face, 0.48 + 0.22 * rnd.random(), 0.13 + 0.03 * rnd.random(), PAPER[k % len(PAPER)], gA * (1 - t), forked=(k % 4 == 1))
            k += 1
        # two ribbons at the pole's head
        for a_ in (0.6, 2.4):
            paper_strip(g, topp + Vector((0, 0, -0.04)), Vector((math.cos(a_), math.sin(a_), 0)), 0.62, 0.10, PAPER[1], 0.0)
    # strips tied under the limb and the needle pads: they ride the tree's own sway
    for hx, hy, hz in spec["hang"]:
        sway = min(max(hy / H, 0), 1) ** 1.6
        top = gl((hx, hy + 0.10, hz))
        tube(g, [top + Vector((0, 0, 0.30)), top], [0.006, 0.006], 3, [straw] * 2, [(0, sway)] * 2, cap=False)
        paper_strip(g, top, Vector((rnd.random() - 0.5, rnd.random() - 0.5, 0)), 0.60 + 0.35 * rnd.random(), 0.15 + 0.04 * rnd.random(), PAPER[k % len(PAPER)], sway, forked=(k % 3 == 0))
        k += 1
    charms.slabs = slabs
    return g


@model("east_jetty", sway=1.0, foliage=0.0, glow=[1.0, 0.62, 0.30, 5.0], baseRadius=0.3, bespoke=True)
def jetty():
    """The lamplighter's boardwalk: from the sand, past the roots, to a landing over the water.
    Built as offsets from its corner, with the sea at y = 0."""
    import place_east_layout as L
    spec = L.jetty_spec()
    g = Geo(); rnd = random.Random(181)
    pts = spec["pts"]; deck = spec["deck"]
    woods = [(0.44, 0.36, 0.27), (0.38, 0.31, 0.24), (0.48, 0.41, 0.31), (0.34, 0.28, 0.22)]
    wet = (0.15, 0.13, 0.11)
    slabs = []

    def plank(c, along, length, width, thick, col):
        along = Vector(along).normalized(); across = Vector((-along.y, along.x, 0))
        a = along * width * 0.5; b = across * length * 0.5; c = Vector(c)
        top = [c - a - b, c + a - b, c + a + b, c - a + b]
        bot = [q - Vector((0, 0, thick)) for q in top]
        dark = mix3(col, (0, 0, 0), 0.4)
        g.add(top + bot, [(0, 1, 2, 3), (4, 5, 1, 0), (5, 6, 2, 1), (6, 7, 3, 2), (7, 4, 0, 3)], [col] * 4 + [dark] * 4, [(0, 0)] * 8, smooth=False)

    def post(x, z, h_ground, top_y, r=0.095, lamp=None):
        b = gl((x, min(h_ground, 0.0) - 0.5, z)); t = gl((x, top_y, z))
        lathe(g, [(r * 1.1, 0.0), (r, (t.z - b.z) * 0.5), (r * 0.92, t.z - b.z), (0.0, t.z - b.z + 0.03)], 6,
              [wet, mix3(wet, woods[0], 0.6), woods[0], woods[2]], [(0, 0)] * 4, center=b)
        slabs.append([round(x, 3), round(z, 3), 0.14, 0.0, round(top_y, 3)])
        if lamp is not None:
            d = Vector((lamp[0], -lamp[1], 0)).normalized()
            arm0 = t - Vector((0, 0, 0.22)); arm1 = arm0 + d * 0.55 + Vector((0, 0, 0.06))
            tube(g, [arm0, arm1], [0.03, 0.022], 4, [woods[3]] * 2, [(0, 0), (0, 0.04)])
            paper_lantern(g, arm1 - d * 0.05, R=0.22, H=0.38, glow=1.0, sway=0.15)

    n = len(pts)
    for i, (x, z, h) in enumerate(pts):
        j0, j1 = max(i - 1, 0), min(i + 1, n - 1)
        along = Vector((pts[j1][0] - pts[j0][0], -(pts[j1][1] - pts[j0][1]), 0))
        c = gl((x, deck + (rnd.random() - 0.5) * 0.025, z))
        along = rot_z((rnd.random() - 0.5) * 0.10) @ along
        plank(c, along, 1.28 + (rnd.random() - 0.5) * 0.14, 0.37, 0.06, woods[i % len(woods)])
        if i % 2 == 0: slabs.append([round(x, 3), round(z, 3), 0.72, 0.0, round(deck + 0.05, 3)])
        if i % 5 == 2:
            across = Vector((-along.y, along.x, 0)).normalized()
            for sgn in (-1, 1):
                q = c + across * sgn * 0.58
                post(q.x, -q.y, h, deck + 0.28)
    # stringers under the planks
    for sgn in (-0.42, 0.42):
        path = []
        for i in range(0, n, 3):
            j0, j1 = max(i - 1, 0), min(i + 1, n - 1)
            along = Vector((pts[j1][0] - pts[j0][0], -(pts[j1][1] - pts[j0][1]), 0)).normalized()
            across = Vector((-along.y, along.x, 0))
            path.append(gl((pts[i][0], deck - 0.12, pts[i][1])) + across * sgn)
        tube(g, path, [0.055] * len(path), 4, [woods[3]] * len(path), [(0, 0)] * len(path))
    # the landing at the end, and its lamps
    ex, ez, eh = pts[-1]
    j = n - 4
    along = Vector((pts[-1][0] - pts[j][0], -(pts[-1][1] - pts[j][1]), 0)).normalized(); across = Vector((-along.y, along.x, 0))
    c0 = gl((ex, deck, ez)) + along * 0.4
    for k in range(6):
        c = c0 + along * (k * 0.43) + Vector((0, 0, (rnd.random() - 0.5) * 0.02))
        plank(c, along, 2.9, 0.39, 0.06, woods[(k + 1) % len(woods)])
        slabs.append([round(c.x, 3), round(-c.y, 3), 1.3, 0.0, round(deck + 0.05, 3)])
    far = c0 + along * 2.3
    for sgn, lamp in ((-1, True), (1, True)):
        q = far + across * sgn * 1.32
        post(q.x, -q.y, eh, deck + 2.5 if lamp else deck + 0.3, r=0.11, lamp=(across.x * sgn * 0.3 + along.x, -(across.y * sgn * 0.3 + along.y)) if lamp else None)
        q2 = c0 + across * sgn * 1.32
        post(q2.x, -q2.y, eh, deck + 0.3)
    # a lamp where the walk turns
    bx, bz = 0.0, 0.0
    q = gl((bx, deck, bz)) + Vector((0.75, 0.25, 0))
    post(q.x, -q.y, 0.0, deck + 2.45, r=0.105, lamp=(-0.6, 0.8))
    jetty.slabs = slabs
    return g


# ------------------------------------------------------------------------------------ main
if __name__ == "__main__":
    names = [a for a in argv if not a.startswith("--")] or list(REGISTRY)
    total = 0
    for nm in names:
        fn, info = REGISTRY[nm]
        g = fn()
        obj, side, size = export(nm, g, dict(info))
        total += size
        print(f"FLORA {nm:22s} {side['tris']:5d} tris  h {side['height']:.2f}  r {side['radius']:.2f}  {size / 1024:.1f} KB")
    print(f"FLORA total {total / 1024:.0f} KB")
    if "--nosheet" not in argv:
        render_sheet(names, os.path.join(PREVIEW, "east_flora_sheet.png"))
        print("SHEET", os.path.join(PREVIEW, "east_flora_sheet.png"))
