# Blender: render a whole place from assets/places/east.json, to judge its composition offline.
# Builds the real ground around it from the baked heightfield, stands every item where the game will,
# scatters the plants with the same random stream src/world/places.js uses (so they land on the same
# spots), and lights it from the game's sun direction (-0.51, 0.56, -0.65).
# Usage: blender -b -P place_east_scene.py -- [place_id ...] [--views=150,40,eye,top] [--size=1280x720]
# Output: art/places_east/scenes/<id>_<view>.png
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector, Matrix, Euler, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import place_east_layout as L

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opts = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
want = [a for a in argv if not a.startswith("--")]
VIEWS = opts.get("views", "150,40,eye").split(",")
W, H = (int(v) for v in opts.get("size", "1280x720").split("x"))
OUT = os.path.join(ROOT, "art", "places_east", "scenes")
os.makedirs(OUT, exist_ok=True)
T = L.T
data = json.load(open(os.path.join(L.PLACES, "east.json")))
# camera bearings (compass, from the place to the eye) that show each place well
BEAR = {"wish_pine": 250, "kettle_pools": 135, "starfall": 250, "conch_garden": 330, "lantern_roots": 240, "whalebone_arbour": 300}

# game (x, y up, z south) -> Blender (x, y north, z up)
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
Ci = C.inverted()
def gl(p): return Vector((p[0], -p[2], p[1]))


# ---- the same generators places.js uses, so the scatter matches the game plant for plant
def imul(a, b): return ((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF)) & 0xFFFFFFFF
def rng(seed):
    s = [int(seed * 2654435761) & 0xFFFFFFFF or 1]
    def f():
        s[0] = (s[0] + 0x6D2B79F5) & 0xFFFFFFFF
        t = imul(s[0] ^ (s[0] >> 15), 1 | s[0])
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return f
def vnoise(x, z, seed):
    def h(ix, iz):
        n = (imul(ix, 374761393) + imul(iz, 668265263) + imul(int(seed), 2246822519)) & 0xFFFFFFFF
        n = imul(n ^ (n >> 13), 1274126177)
        return ((n ^ (n >> 16)) & 0xFFFFFFFF) / 4294967296
    ix, iz = math.floor(x), math.floor(z); fx, fz = x - ix, z - iz
    ux, uz = fx * fx * (3 - 2 * fx), fz * fz * (3 - 2 * fz)
    a, b, c, d = h(ix, iz), h(ix + 1, iz), h(ix, iz + 1), h(ix + 1, iz + 1)
    return (a + (b - a) * ux) * (1 - uz) + (c + (d - c) * ux) * uz
def sstep(x, a, b):
    t = min(max((x - a) / (b - a), 0), 1); return t * t * (3 - 2 * t)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    try: scene.render.engine = "BLENDER_EEVEE"
    except Exception: scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = W; scene.render.resolution_y = H
    scene.view_settings.view_transform = "Filmic" if "Filmic" in [i.identifier for i in type(scene.view_settings).bl_rna.properties["view_transform"].enum_items] else "AgX"
    world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
    bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.42, 0.62, 0.95, 1); bg.inputs[1].default_value = 1.1
    sd = bpy.data.lights.new("sun", "SUN"); sd.energy = 5.0; sd.color = (1.0, 0.94, 0.84); sd.angle = math.radians(1.5)
    sun = bpy.data.objects.new("sun", sd); scene.collection.objects.link(sun)
    sun.rotation_euler = Vector((-0.5104, 0.6533, 0.5592)).normalized().to_track_quat("Z", "Y").to_euler()
    return scene


def vcol_material(name="vcol", rough=0.9):
    mat = bpy.data.materials.get(name)
    if mat: return mat
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
    ca = nt.nodes.new("ShaderNodeVertexColor"); ca.layer_name = "Color"
    nt.links.new(ca.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    mat.use_backface_culling = False
    return mat


def ground_object(cx, cz, half):
    n = int(half * 2 / T.cell) + 1
    xs = cx - half + np.arange(n) * T.cell; zs = cz - half + np.arange(n) * T.cell
    X, Z = np.meshgrid(xs, zs)
    Y = np.asarray(T.h(X, Z), np.float32)
    verts = np.stack([X, -Z, Y], -1).reshape(-1, 3)
    idx = np.arange(n * n).reshape(n, n)
    faces = np.stack([idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]], -1).reshape(-1, 4)
    me = bpy.data.meshes.new("ground")
    me.from_pydata(verts.tolist(), [], faces.tolist())
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    col = terrain_colours(X, Z, Y).reshape(-1, 3)
    ca = me.color_attributes.new(name="Color", type="FLOAT_COLOR", domain="POINT")
    c4 = np.ones((len(verts), 4), np.float32); c4[:, :3] = col
    ca.data.foreach_set("color", c4.reshape(-1))
    me.materials.append(vcol_material("ground", 1.0))
    ob = bpy.data.objects.new("ground", me); bpy.context.scene.collection.objects.link(ob)
    # the sea
    sm = bpy.data.meshes.new("sea"); R = half * 6
    sm.from_pydata([(cx - R, -cz - R, 0), (cx + R, -cz - R, 0), (cx + R, -cz + R, 0), (cx - R, -cz + R, 0)], [], [(0, 1, 2, 3)])
    mat = bpy.data.materials.new("sea"); mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.03, 0.30, 0.36, 1); b.inputs["Roughness"].default_value = 0.12
    if "Alpha" in b.inputs: b.inputs["Alpha"].default_value = 0.78
    try: mat.surface_render_method = "BLENDED"
    except Exception:
        try: mat.blend_method = "BLEND"
        except Exception: pass
    sm.materials.append(mat)
    so = bpy.data.objects.new("sea", sm); bpy.context.scene.collection.objects.link(so)
    return ob


_maps = {}
def terrain_colours(X, Z, Y):
    """Grass / flowers / sand / scree, from the baked splat and tint maps (read with Blender's own image loader)."""
    def load(name):
        if name not in _maps:
            im = bpy.data.images.load(os.path.join(ROOT, "assets", "terrain", name))
            w, h = im.size
            px = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(px)
            _maps[name] = px.reshape(h, w, 4)[::-1]                    # top row first
            bpy.data.images.remove(im)
        return _maps[name]
    def samp(a, x, z):
        S = a.shape[0]
        ix = np.clip(((x + T.half) / (2 * T.half) * S).astype(int), 0, S - 1)
        iz = np.clip(((z + T.half) / (2 * T.half) * S).astype(int), 0, S - 1)
        return a[iz, ix]
    sp = samp(load("splat.png"), X, Z); tint = samp(load("tint.png"), X, Z)[..., :3]
    cover = sp[..., 3:4]; dens = sp[..., 0:1]
    gy, gx = np.gradient(Y, T.cell)
    slope = np.hypot(gx, gy)[..., None]
    grass = np.array([0.16, 0.30, 0.07]); scree = np.array([0.42, 0.41, 0.38]); sand = np.array([0.78, 0.70, 0.50]); rockc = np.array([0.20, 0.19, 0.19])
    base = np.where(Y[..., None] < 3.4, sand, scree)
    base = np.where(slope > 0.95, rockc, base)
    col = base * (1 - cover) + grass * cover
    f = np.clip(dens * cover * 0.7, 0, 1)
    col = col * (1 - f) + tint * f
    sea = np.clip(-Y[..., None] / 5.0, 0, 1)
    col = col * (1 - 0.5 * sea)
    return np.clip(col, 0, 1).astype(np.float32)


_models = {}
def load_model(path):
    """Import a GLB once; returns (mesh datablocks with their local matrices, sidecar)."""
    if path in _models: return _models[path]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(L.PLACES, path))
    new = [o for o in bpy.data.objects if o not in before]
    prims = []
    for o in new:
        if o.type == "MESH":
            if o.data.color_attributes and not any(n.type == "TEX_IMAGE" for m in o.data.materials if m and m.node_tree for n in m.node_tree.nodes):
                o.data.materials.clear(); o.data.materials.append(vcol_material())
                o.data.color_attributes.active_color = o.data.color_attributes[0]
                if o.data.color_attributes[0].name != "Color": o.data.color_attributes[0].name = "Color"
            prims.append((o.data, o.matrix_world.copy()))
    for o in new: bpy.data.objects.remove(o)
    try: info = json.load(open(os.path.join(L.PLACES, path[:-4] + ".json")))
    except Exception: info = {}
    _models[path] = (prims, info)
    return _models[path]


def game_matrix(pos, yaw=0.0, scale=1.0, rot=None, tilt=None):
    """places.js' item transform, expressed in Blender axes."""
    q = Quaternion((0, 1, 0), yaw)
    # (three's Euler order 'YXZ' is Ry.Rx.Rz, which mathutils calls 'ZXY')
    if rot: q = q @ Euler((rot[0], rot[1], rot[2]), "ZXY").to_quaternion()
    if tilt: q = Euler(tilt, "ZXY").to_quaternion()
    s = scale if isinstance(scale, (list, tuple)) else (scale, scale, scale)
    Mg = Matrix.Translation(Vector(pos)) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((s[0], s[1], s[2], 1))
    return C @ Mg @ Ci


def build_place(pl):
    scene = reset()
    px, py, pz = pl["pos"]
    half = max(pl["radius"] * 2.2, 90)
    ground_object(px, pz, half)
    loaded = {k: load_model(p) for k, p in pl["models"].items()}
    keepout = []
    coll = bpy.context.scene.collection
    for it in pl["items"]:
        prims, info = loaded[it["model"]]
        x, y, z = it["pos"]
        if "agl" in it: y = T.h(x, z) + it["agl"]
        M = game_matrix((x, y, z), it.get("yaw", 0), it.get("scale", 1), it.get("rot"))
        for me, local in prims:
            ob = bpy.data.objects.new(it["model"], me); coll.objects.link(ob); ob.matrix_world = M @ local
        s = it.get("scale", 1); su = max(s) if isinstance(s, (list, tuple)) else s
        keepout.append((x, z, (info.get("baseRadius", min(info.get("radius", 1.5), 1.5))) * su * 0.9))
    nplants = 0
    for f in pl["flora"]:
        prims, info = loaded[f["model"]]
        R = rng(f.get("seed", 1))
        cx, cz = f["center"]; rad = f.get("radius", 8); inner = f.get("inner", 0); clump = f.get("clump", 0)
        s0, s1 = f["scale"] if isinstance(f.get("scale"), list) else (f.get("scale", 1),) * 2
        n = min(int(f["count"]), 4000)
        mats = []
        tries = 0
        while len(mats) < n and tries < n * 12:
            tries += 1
            a = R() * 6.2831853; rr = math.sqrt(inner * inner + (rad * rad - inner * inner) * R())
            x, z = cx + math.cos(a) * rr, cz + math.sin(a) * rr
            r1, r2, r3, r4 = R(), R(), R(), R()
            if clump > 0 and r1 > 1 - clump + clump * sstep(vnoise(x * 0.42, z * 0.42, int(f.get("seed", 0))), 0.34, 0.62): continue
            h = T.h(x, z)
            if h < 0.25 and not f.get("lift"): continue
            if not f.get("steep"):                                      # nor on a cliff face
                e_ = 1.5
                nx_, nz_ = T.h(x - e_, z) - T.h(x + e_, z), T.h(x, z - e_) - T.h(x, z + e_)
                if 2 * e_ / math.sqrt(nx_ * nx_ + 4 * e_ * e_ + nz_ * nz_) < 0.74: continue
            if any((x - k[0]) ** 2 + (z - k[1]) ** 2 < k[2] * k[2] for k in keepout): continue
            s = s0 + (s1 - s0) * r2 ** 1.35
            ry = R() * 6.2831853
            mats.append(game_matrix((x, h + f.get("lift", 0), z), scale=s, tilt=((r3 - 0.5) * 0.24, ry, (r4 - 0.5) * 0.24)))
            R(); R(); R()                                               # the tint draws
        if not mats: continue
        nplants += len(mats)
        for me, local in prims:
            nv = len(me.vertices)
            co = np.empty(nv * 3, np.float32); me.vertices.foreach_get("co", co); co = np.c_[co.reshape(-1, 3), np.ones(nv, np.float32)]
            polys = [tuple(p.vertices) for p in me.polygons]
            col = np.ones((nv, 4), np.float32)
            if me.color_attributes:
                ca = me.color_attributes[0]
                if ca.domain == "POINT": ca.data.foreach_get("color", col.reshape(-1))
                else:
                    nl = len(me.loops); lc = np.empty(nl * 4, np.float32); ca.data.foreach_get("color", lc)
                    lvi = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", lvi); col[lvi] = lc.reshape(-1, 4)
            V, F, Cc = [], [], []
            rv = np.random.default_rng(f.get("seed", 1))
            for i, M in enumerate(mats):
                Mn = np.array(M @ local, np.float32)
                V.append((co @ Mn.T)[:, :3])
                F += [tuple(v + i * nv for v in p) for p in polys]
                Cc.append(col * np.array([*(0.86 + 0.28 * rv.random(1)).repeat(3), 1], np.float32))
            big = bpy.data.meshes.new(f["model"] + "_field")
            big.from_pydata(np.concatenate(V).tolist(), [], F)
            big.polygons.foreach_set("use_smooth", [True] * len(big.polygons))
            c2 = big.color_attributes.new(name="Color", type="FLOAT_COLOR", domain="POINT")
            c2.data.foreach_set("color", np.concatenate(Cc).reshape(-1))
            big.materials.append(vcol_material())
            ob = bpy.data.objects.new(f["model"] + "_field", big); coll.objects.link(ob)
    t = pl.get("treasure")
    if t and t.get("model") in loaded:
        prims, info = loaded[t["model"]]
        s = t.get("scale", 1)
        M = game_matrix((t["pos"][0], t["pos"][1] - info.get("height", 0) * 0.5 * s, t["pos"][2]), 0.6, s)
        for me, local in prims:
            ob = bpy.data.objects.new("treasure", me); coll.objects.link(ob); ob.matrix_world = M @ local
    return scene, nplants


def shoot(scene, pl, view):
    px, py, pz = pl["pos"]
    bear = math.radians(BEAR.get(pl["id"], 220))
    cd = bpy.data.cameras.new("cam"); cd.lens_unit = "FOV"; cd.sensor_fit = "VERTICAL"; cd.angle = math.radians(64); cd.clip_start = 0.3; cd.clip_end = 4000
    cam = bpy.data.objects.new("cam", cd); scene.collection.objects.link(cam); scene.camera = cam
    spec = {"150": (150, 28, 0, 2.0), "40": (40, 16, 0, 2.0), "eye": (24, 4, 40, 2.5), "top": (95, 88, 0, 0.0)}[view]
    dist, elev, daz, lift = spec
    a = bear + math.radians(daz); e = math.radians(elev)
    ty = max(T.h(px, pz), 0) + lift
    ex, ez, ey = px + math.sin(a) * math.cos(e) * dist, pz - math.cos(a) * math.cos(e) * dist, ty + math.sin(e) * dist
    cam.location = gl((ex, ey, ez))
    look = gl((px, ty, pz)) - cam.location
    cam.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(OUT, f"{pl['id']}_{view}.png")
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    return scene.render.filepath


for pl in data["places"]:
    if want and pl["id"] not in want: continue
    scene, n = build_place(pl)
    for v in VIEWS:
        print("SCENE", pl["id"], v, n, "plants ->", shoot(scene, pl, v))
