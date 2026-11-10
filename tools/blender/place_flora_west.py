# Blender: the plants and simple dressing of the western places, modelled in code.
# Every model is a few hundred triangles, coloured by vertex (linear RGB, the meadow's own palette)
# and carries a _WIND attribute the game's place shader reads:
#   r leaf flutter / translucency, g sway with height (0 at the foot), b glow, a 1 - cloth weight.
# Writes <out>/<name>.glb + <name>.json (sidecar) and a preview to <previews>/<name>.png.
# Usage: blender -b -P place_flora_west.py -- <out_dir> <preview_dir> [name ...]
import bpy, sys, os, json, math, random
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, PREV = argv[0], argv[1]
WANT = argv[2:]
os.makedirs(OUT, exist_ok=True); os.makedirs(PREV, exist_ok=True)
TAU = math.tau


def V(*a): return np.array(a, dtype=np.float64)
def norm(v):
    l = np.linalg.norm(v)
    return v / l if l > 1e-9 else v
def mixc(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
def shade(c, k): return tuple(min(max(v * k, 0.0), 1.0) for v in c)
def bez(p0, p1, p2, t): return p0 * (1 - t) ** 2 + p1 * 2 * (1 - t) * t + p2 * t * t


class Model:
    def __init__(self, name, seed=1):
        self.name = name
        self.v, self.f, self.c, self.w = [], [], [], []
        self.rnd = random.Random(seed)

    def r(self, a=1.0, b=None):
        return self.rnd.uniform(0, a) if b is None else self.rnd.uniform(a, b)

    def add(self, verts, faces, cols, winds):
        o = len(self.v)
        n = len(verts)
        if not isinstance(cols, list): cols = [cols] * n
        if not isinstance(winds, list): winds = [winds] * n
        for i in range(n):
            self.v.append(tuple(float(x) for x in verts[i]))
            self.c.append(tuple(cols[i])[:3])
            w = tuple(winds[i]); self.w.append((w + (0.0, 0.0, 0.0, 1.0)[len(w):])[:4])
        for f in faces: self.f.append(tuple(o + i for i in f))

    # ---- primitives -------------------------------------------------------------------
    def tube(self, path, radii, sides, col, wind, cap=False):
        """A tube along a polyline. col/wind: one value, or a function of t (0..1 along it)."""
        path = [np.asarray(p, float) for p in path]
        n = len(path)
        if not isinstance(radii, (list, tuple)): radii = [radii] * n
        verts, cols, winds, faces = [], [], [], []
        up = V(0, 0, 1)
        for i, p in enumerate(path):
            t = i / (n - 1)
            d = norm(path[min(i + 1, n - 1)] - path[max(i - 1, 0)])
            a = np.cross(d, up if abs(d[2]) < 0.95 else V(1, 0, 0)); a = norm(a); b = np.cross(d, a)
            for k in range(sides):
                ang = TAU * k / sides
                verts.append(p + (a * math.cos(ang) + b * math.sin(ang)) * radii[i])
                cols.append(col(t) if callable(col) else col); winds.append(wind(t, p) if callable(wind) else wind)
        for i in range(n - 1):
            for k in range(sides):
                a0, a1 = i * sides + k, i * sides + (k + 1) % sides
                faces.append((a0, a1, a1 + sides, a0 + sides))
        if cap:
            verts.append(path[-1]); cols.append(col(1.0) if callable(col) else col); winds.append(wind(1.0, path[-1]) if callable(wind) else wind)
            for k in range(sides): faces.append(((n - 1) * sides + k, (n - 1) * sides + (k + 1) % sides, len(verts) - 1))
        self.add(verts, faces, cols, winds)

    def strip(self, path, widths, side, col, wind, cup=0.0):
        """A ribbon (leaf, petal, blade) along a polyline; `side` is the across direction (or a list)."""
        path = [np.asarray(p, float) for p in path]
        n = len(path)
        if not isinstance(widths, (list, tuple)): widths = [widths] * n
        verts, cols, winds, faces = [], [], [], []
        for i, p in enumerate(path):
            t = i / (n - 1)
            s = norm(np.asarray(side[i] if isinstance(side, list) else side, float))
            d = norm(path[min(i + 1, n - 1)] - path[max(i - 1, 0)])
            nrm = norm(np.cross(s, d))
            c = col(t) if callable(col) else col
            w = wind(t, p) if callable(wind) else wind
            if cup:
                verts += [p - s * widths[i] + nrm * cup * widths[i], p, p + s * widths[i] + nrm * cup * widths[i]]
                cols += [shade(c, 1.06), shade(c, 0.9), shade(c, 1.06)]; winds += [w, w, w]
            else:
                verts += [p - s * widths[i], p + s * widths[i]]
                cols += [c, c]; winds += [w, w]
        k = 3 if cup else 2
        for i in range(n - 1):
            for j in range(k - 1):
                a = i * k + j
                faces.append((a, a + 1, a + k + 1, a + k))
        self.add(verts, faces, cols, winds)

    def blob(self, center, radius, lon, lat, col, wind, squash=(1, 1, 1), top=None, axis=None):
        """A low-poly ellipsoid. `top` lightens the colour toward +z; `axis` re-orients the pole."""
        center = np.asarray(center, float)
        verts, cols, winds, faces = [], [], [], []
        az = norm(np.asarray(axis, float)) if axis is not None else V(0, 0, 1)
        ax = norm(np.cross(az, V(1, 0, 0) if abs(az[0]) < 0.9 else V(0, 1, 0))); ay = np.cross(az, ax)
        def put(x, y, z):
            p = center + (ax * x * squash[0] + ay * y * squash[1] + az * z * squash[2]) * radius
            c = col if top is None else mixc(col, top, 0.5 + 0.5 * z)
            verts.append(p); cols.append(c); winds.append(wind(0, p) if callable(wind) else wind)
        put(0, 0, 1)
        for j in range(1, lat):
            ph = math.pi * j / lat
            for i in range(lon):
                th = TAU * i / lon
                put(math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph))
        put(0, 0, -1)
        last = len(verts) - 1
        for i in range(lon):
            faces.append((0, 1 + i, 1 + (i + 1) % lon))
            faces.append((last, 1 + (lat - 2) * lon + (i + 1) % lon, 1 + (lat - 2) * lon + i))
        for j in range(lat - 2):
            for i in range(lon):
                a = 1 + j * lon + i; b = 1 + j * lon + (i + 1) % lon
                faces.append((a, a + lon, b + lon, b))
        self.add(verts, faces, cols, winds)

    def fan(self, center, normal, radius, sides, col_c, col_e, wind, cone=0.0, ruffle=0.0, notch=None):
        """A disc: flat, a shallow cone (cone > 0 lifts the centre) or ruffled at the rim."""
        center = np.asarray(center, float); nz = norm(np.asarray(normal, float))
        ax = norm(np.cross(nz, V(1, 0, 0) if abs(nz[0]) < 0.9 else V(0, 1, 0))); ay = np.cross(nz, ax)
        wf = (lambda q: wind(0, q)) if callable(wind) else (lambda q: wind)
        verts = [center + nz * cone * radius]; cols = [col_c]; winds = [wf(verts[0])]
        ph = self.r(TAU)
        for i in range(sides):
            a = ph + TAU * i / sides
            rr = radius * (0.35 if (notch is not None and i == notch) else 1.0)
            verts.append(center + (ax * math.cos(a) + ay * math.sin(a)) * rr + nz * (ruffle * radius * (1 if i % 2 else -1)))
            cols.append(col_e); winds.append(wf(verts[-1]))
        faces = [(0, 1 + i, 1 + (i + 1) % sides) for i in range(sides)]
        self.add(verts, faces, cols, winds)

    # ---- output -----------------------------------------------------------------------
    def stats(self):
        v = np.array(self.v)
        tris = sum(len(f) - 2 for f in self.f)
        return v, tris

    def export(self, info=None):
        v, tris = self.stats()
        me = bpy.data.meshes.new(self.name)
        me.from_pydata([tuple(p) for p in self.v], [], self.f)
        me.update()
        for p in me.polygons: p.use_smooth = True
        col = me.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="POINT")
        col.data.foreach_set("color", np.array([c + (1.0,) for c in self.c], np.float32).reshape(-1))
        me.color_attributes.active_color = col
        me.color_attributes.render_color_index = 0
        wind = me.attributes.new(name="_WIND", type="FLOAT_COLOR", domain="POINT")
        wind.data.foreach_set("color", np.array(self.w, np.float32).reshape(-1))
        obj = bpy.data.objects.new(self.name, me)
        bpy.context.scene.collection.objects.link(obj)
        mat = bpy.data.materials.new(self.name)
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"][0]
        ca = nt.nodes.new("ShaderNodeVertexColor"); ca.layer_name = "Col"
        nt.links.new(ca.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.8
        mat.use_backface_culling = False
        me.materials.append(mat)
        height = float(v[:, 2].max())
        rad = float(np.hypot(v[:, 0], v[:, 1]).max())
        base = v[v[:, 2] < max(height * 0.1, 0.02)]
        meta = {"name": self.name, "height": round(height, 3), "tris": tris, "radius": round(rad, 3),
                "baseRadius": round(float(np.percentile(np.hypot(base[:, 0], base[:, 1]), 90)) if len(base) else rad, 3),
                "slabs": [], "thin": True}
        meta.update(info or {})
        render_preview(obj, height, rad, os.path.join(PREV, self.name + ".png"), float(v[:, 2].min()))
        for o in bpy.context.scene.objects: o.select_set(o == obj)
        bpy.context.view_layer.objects.active = obj
        dst = os.path.join(OUT, self.name + ".glb")
        bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", use_selection=True, export_attributes=True,
                                  export_vertex_color="ACTIVE", export_all_vertex_colors=False, export_normals=True,
                                  export_tangents=False, export_yup=True, export_apply=True, export_materials="EXPORT")
        json.dump(meta, open(os.path.join(OUT, self.name + ".json"), "w"), indent=1)
        print(f"EXPORTED {self.name}: {tris} tris, h {height:.2f}, r {rad:.2f}, {os.path.getsize(dst) / 1024:.1f} KB")
        bpy.data.objects.remove(obj)


def render_preview(obj, height, rad, path, zmin=0.0):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light = "STUDIO"; sh.color_type = "VERTEX"; sh.show_backface_culling = False
    sh.show_shadows = False; sh.show_cavity = True
    scene.display.render_aa = "8"
    scene.render.resolution_x = scene.render.resolution_y = 420
    scene.render.film_transparent = False
    if scene.world is None: scene.world = bpy.data.worlds.new("w")
    scene.world.color = (0.16, 0.22, 0.14)
    span = max(height - zmin, rad * 2)
    cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = span * 1.25
    cam = bpy.data.objects.new("c", cd); scene.collection.objects.link(cam); scene.camera = cam
    d = Vector((0.7, -0.75, 0.38)).normalized()
    ctr = Vector((0, 0, (height + zmin) * 0.5))
    cam.location = ctr + d * span * 6
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def sway(height, power=1.5):
    """Wind weights for an upright plant part: flutter f, bend rising with height."""
    return lambda flutter: (lambda t, p: (flutter, min(max(p[2] / height, 0.0), 1.0) ** power, 0.0, 1.0))


def fib(n):
    """n directions spread evenly over a sphere."""
    out = []
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(max(1 - z * z, 0)); a = i * 2.39996323
        out.append(V(r * math.cos(a), r * math.sin(a), z))
    return out


# =====================================================================================
# palette (linear; the meadow's own greens and flower colours, see src/shaders/common.js)
# =====================================================================================
LUSH = (0.085, 0.235, 0.050); FRESH = (0.190, 0.315, 0.068); DEEP = (0.045, 0.150, 0.040)
STEM = (0.10, 0.22, 0.045); STRAW = (0.50, 0.46, 0.20)
PINK = (0.90, 0.16, 0.46); ROSE = (0.97, 0.42, 0.66); BLUSH = (0.97, 0.76, 0.87); WHITE = (0.97, 0.96, 0.90)
GOLD = (0.99, 0.72, 0.05); LEMON = (0.98, 0.90, 0.30); ORANGE = (0.98, 0.36, 0.05); RED = (0.90, 0.07, 0.035)
LILAC = (0.66, 0.50, 0.93); VIOLET = (0.42, 0.26, 0.82); BLUE = (0.16, 0.36, 0.92)


# ------------------------------------------------------------------------------------- stack
def gentian():
    """Sister's gentian: a tight green cushion crowded with deep blue trumpets that open straight up."""
    m = Model("gentian", 11); H = 0.22
    W = lambda fl: (lambda t, p: (fl, min(max(p[2] / H, 0.0), 1.0) ** 1.5 * 0.6, 0.0, 1.0))
    deep, mid, throat = (0.03, 0.07, 0.72), (0.08, 0.20, 0.95), (0.62, 0.78, 1.0)
    m.blob((0, 0, 0.02), 0.22, 6, 3, DEEP, (0.1, 0.0), squash=(1, 1, 0.45), top=FRESH)
    for i in range(8):
        a = TAU * i / 8 + m.r(0.3); d = V(math.cos(a), math.sin(a), 0); L = m.r(0.10, 0.16)
        m.strip([d * 0.15 + V(0, 0, 0.05), d * (0.15 + L * 0.6) + V(0, 0, 0.08), d * (0.15 + L) + V(0, 0, 0.02)], [0.016, 0.014, 0.002],
                np.cross(d, V(0, 0, 1)), lambda t: mixc(LUSH, FRESH, t), W(0.5))
    for i in range(7):
        a = TAU * i / 7 * 1.9 + m.r(0.5); rr = 0.03 + 0.17 * math.sqrt((i + 0.5) / 7)
        c = V(math.cos(a) * rr, math.sin(a) * rr, 0.085 - 0.03 * (rr / 0.2) ** 2)
        ax = norm(V(math.cos(a) * rr * 1.6, math.sin(a) * rr * 1.6, 1.0))
        e1 = norm(np.cross(ax, V(0, 0, 1) if abs(ax[2]) < 0.95 else V(1, 0, 0))); e2 = np.cross(ax, e1)
        L = m.r(0.07, 0.10); rm = m.r(0.030, 0.040)
        verts, cols, winds = [], [], []
        for (zz, rad, col) in ((0.0, 0.34, deep), (1.0, 1.0, mid)):
            for j in range(5):
                an = TAU * j / 5
                verts.append(c + ax * L * zz + (e1 * math.cos(an) + e2 * math.sin(an)) * rm * rad); cols.append(col); winds.append((1.0, 0.5, 0.0, 1.0))
        faces = [(j, (j + 1) % 5, 5 + (j + 1) % 5, 5 + j) for j in range(5)]
        # five pointed lobes flaring flat from the rim, and the pale throat between them
        for j in range(5):
            an = TAU * (j + 0.5) / 5
            verts.append(c + ax * L * 1.02 + (e1 * math.cos(an) + e2 * math.sin(an)) * rm * 2.1); cols.append(shade(mid, 1.15)); winds.append((1.0, 0.6, 0.0, 1.0))
            faces.append((5 + j, 5 + (j + 1) % 5, 10 + j))
        verts.append(c + ax * L * 0.5); cols.append(throat); winds.append((1.0, 0.5, 0.0, 1.0))
        for j in range(5): faces.append((5 + (j + 1) % 5, 5 + j, 15))
        m.add(verts, faces, cols, winds)
    m.export({"sway": 0.6, "lod0": 45})


def petalfall(name="petalfall", pale=BLUSH, strong=ROSE, seed=5):
    """Blossom lying where it fell: a scatter of pale petals on the ground (or afloat)."""
    m = Model(name, seed)
    for i in range(9):
        a = m.r(TAU); rr = math.sqrt(m.r()) * 0.5; c = V(math.cos(a) * rr, math.sin(a) * rr, m.r(0.02, 0.05))
        d = V(math.cos(m.r(TAU)), math.sin(m.r(TAU)), m.r(-0.3, 0.3)); d = norm(d)
        s = norm(np.cross(d, V(0, 0, 1))); L = m.r(0.035, 0.055)
        col = mixc(pale, strong, m.r(0.0, 0.55))
        m.add([c - d * L, c - s * L * 0.6, c + d * L, c + s * L * 0.6], [(0, 1, 2, 3)], [shade(col, 0.9), col, shade(col, 1.06), col], (1.0, 0.0, 0.0, 1.0))
    m.export({"sway": 0.0, "lod0": 45})


# ------------------------------------------------------------------------------------- bridge
def fern():
    """A big shuttlecock fern: arching fronds of paired leaflets."""
    m = Model("fern", 3); H = 1.25; W = sway(H, 1.2)
    for i in range(9):
        a = TAU * i / 9 + m.r(-0.2, 0.2); d = V(math.cos(a), math.sin(a), 0); L = m.r(1.0, 1.35)
        p0, p1, p2 = V(0, 0, 0.03), d * L * 0.22 + V(0, 0, L * 1.30), d * L * 0.95 + V(0, 0, L * m.r(0.38, 0.60))
        side = np.cross(d, V(0, 0, 1))
        n = 9
        pts = [bez(p0, p1, p2, t) for t in np.linspace(0, 1, n)]
        m.strip(pts, [0.014 * (1 - 0.8 * t) for t in np.linspace(0, 1, n)], side, lambda t: mixc(shade(STEM, 0.9), LUSH, t), W(0.3))
        for k in range(1, n):
            t = k / (n - 1); p = pts[k]; tan = norm(pts[k] - pts[k - 1])
            ll = L * 0.34 * math.sin(math.pi * min(t * 1.06, 1.0) ** 0.7) + 0.03
            for sg in (-1, 1):
                # leaflets sweep forward along the frond and droop a little at the tip
                out = norm(side * sg + tan * 0.55 + V(0, 0, -0.10))
                tip = p + out * ll + V(0, 0, -0.06 * ll)
                wd = norm(np.cross(out, V(0, 0, 1))) * ll * 0.30
                c = mixc(DEEP, LUSH, 0.15 + 0.85 * t)
                m.add([p - tan * 0.02, p + out * ll * 0.42 - wd, tip, p + out * ll * 0.42 + wd], [(0, 1, 2, 3)],
                      [shade(c, 0.7), c, mixc(c, FRESH, 0.6), shade(c, 1.1)], [W(0.9)(0, q) for q in (p, p, tip, p)])
    m.export({"sway": 0.55, "foliage": 0.7})


def flagiris():
    """Goldflag: a water iris with sword leaves and three-tongued yellow flowers, for the river's edge."""
    m = Model("flagiris", 8); H = 0.98; W = sway(H, 1.4)
    blue, tip = (0.07, 0.24, 0.12), (0.26, 0.44, 0.14)
    for i in range(7):
        a = TAU * i / 7 + m.r(0.5); d = V(math.cos(a), math.sin(a), 0); L = m.r(0.62, 0.92); out = m.r(0.10, 0.34)
        pts = [bez(d * 0.02, d * L * out * 0.4 + V(0, 0, L * 0.7), d * L * out + V(0, 0, L), t) for t in np.linspace(0, 1, 4)]
        m.strip(pts, [0.026, 0.030, 0.022, 0.002], np.cross(d, V(0, 0, 1)), lambda t: mixc(blue, tip, t), W(0.6))
    gold, deep = (0.99, 0.74, 0.03), (0.92, 0.42, 0.02)
    for s_ in range(2):
        a = m.r(TAU); d = V(math.cos(a), math.sin(a), 0); h = H * (0.98 if s_ == 0 else 0.74)
        top = d * 0.08 + V(0, 0, h - 0.06)
        m.tube([V(0, 0, 0), d * 0.03 + V(0, 0, h * 0.5), top], [0.010, 0.009, 0.007], 3, lambda t: mixc(blue, tip, t), W(0.3))
        for k in range(3):
            an = TAU * k / 3 + s_ * 1.0; o = V(math.cos(an), math.sin(an), 0)
            # the falls: broad tongues that arch out and hang
            pts = [top, top + o * 0.06 + V(0, 0, 0.035), top + o * 0.125 + V(0, 0, 0.005), top + o * 0.15 + V(0, 0, -0.06)]
            m.strip(pts, [0.012, 0.038, 0.042, 0.006], np.cross(o, V(0, 0, 1)), lambda t: mixc(deep, gold, min(t * 2.2, 1.0)), W(1.0))
            # the standards: narrow, upright, between the falls
            an2 = an + TAU / 6; o2 = V(math.cos(an2), math.sin(an2), 0)
            pts = [top, top + o2 * 0.03 + V(0, 0, 0.06), top + o2 * 0.035 + V(0, 0, 0.115)]
            m.strip(pts, [0.008, 0.02, 0.003], np.cross(o2, V(0, 0, 1)), lambda t: mixc(gold, LEMON, t), W(1.0))
    b0 = V(-0.03, 0.02, 0.0)
    m.tube([b0, b0 + V(-0.03, 0.02, H * 0.6)], [0.008, 0.006], 3, blue, W(0.3))
    m.blob(b0 + V(-0.03, 0.02, H * 0.6 + 0.04), 0.022, 4, 3, mixc(tip, gold, 0.5), W(0.8), squash=(1, 1, 2.2), top=gold)
    m.export({"sway": 0.7, "lod0": 45})


def rimlily():
    """Rimlily: great round pads with turned-up rims, bronze underneath, and a white star of a flower. Floats (z = 0 is the water)."""
    m = Model("rimlily", 21)
    top_c, top_e, under = (0.10, 0.36, 0.10), (0.20, 0.46, 0.12), (0.42, 0.10, 0.07)
    N = 14
    for (x, y, r, rim) in ((0.0, 0.0, 1.0, 0.11), (1.55, 0.55, 0.66, 0.08), (-0.6, 1.5, 0.42, 0.055)):
        ph = m.r(TAU); notch = int(m.r(N))
        ring = [V(x + math.cos(ph + TAU * i / N) * r, y + math.sin(ph + TAU * i / N) * r, 0.02) for i in range(N)]
        lip = [V(x + math.cos(ph + TAU * i / N) * r * 1.03, y + math.sin(ph + TAU * i / N) * r * 1.03, 0.02 + rim * (0.25 if i == notch else 1.0)) for i in range(N)]
        verts = [V(x, y, 0.035)] + ring + lip
        cols = [top_c] + [top_e if i % 2 else shade(top_c, 1.15) for i in range(N)] + [under] * N
        faces = [(0, 1 + i, 1 + (i + 1) % N) for i in range(N)] + [(1 + i, 1 + N + i, 1 + N + (i + 1) % N, 1 + (i + 1) % N) for i in range(N)]
        m.add(verts, faces, cols, (0.1, 0.0, 0.0, 1.0))
    fc = V(0.95, -0.85, 0.07)
    white, cream = (0.97, 0.97, 0.93), (0.99, 0.88, 0.55)
    for ring, (n, L, lift) in enumerate(((10, 0.36, 0.22), (8, 0.28, 0.75), (5, 0.18, 1.5))):
        for i in range(n):
            a = TAU * (i + 0.5 * ring) / n; d = V(math.cos(a), math.sin(a), 0)
            pts = [fc, fc + d * L * 0.5 + V(0, 0, L * lift * 0.45), fc + d * L + V(0, 0, L * lift)]
            m.strip(pts, [0.02, L * 0.20, 0.004], np.cross(d, V(0, 0, 1)), lambda t: mixc(cream, white, min(t * 2, 1)), (0.8, 0.4, 0.0, 1.0))
    m.blob(fc + V(0, 0, 0.06), 0.065, 6, 3, GOLD, (0.3, 0.4, 0.0, 1.0), squash=(1, 1, 0.6), top=LEMON)
    bc = V(-0.95, -0.7, 0.0)
    m.tube([bc, bc + V(0.02, 0.0, 0.26)], [0.018, 0.014], 4, STEM, (0.2, 0.5, 0.0, 1.0))
    m.blob(bc + V(0.02, 0, 0.34), 0.08, 5, 4, cream, (0.6, 0.7, 0.0, 1.0), squash=(0.7, 0.7, 1.4), top=white)
    m.export({"sway": 0.25, "lod0": 90, "foliage": 0.35, "collide": False})


def wisteria():
    """A hanging spray of wisteria: racemes of pale-to-deep violet on a short woody stem. Hangs from its origin."""
    m = Model("wisteria", 4)
    wood = (0.20, 0.14, 0.09)
    m.tube([V(-0.55, 0, 0.0), V(-0.2, 0.03, 0.03), V(0.2, -0.03, 0.02), V(0.55, 0, 0.0)], [0.03, 0.035, 0.03, 0.022], 4, wood, (0.0, 0.0))
    hi, lo = (0.60, 0.40, 0.95), (0.30, 0.14, 0.72)
    for i, (x, L) in enumerate(((-0.45, 1.0), (-0.18, 1.55), (0.1, 1.25), (0.38, 0.85), (0.0, 0.7))):
        y = m.r(-0.08, 0.08)
        n = int(5 + L * 7)
        def wnd(t, p, L=L): return (0.6, min(max(-p[2] / 1.55, 0.0), 1.0) ** 1.15, 0.0, 1.0)
        m.strip([V(x, y, 0), V(x, y, -L * 0.5), V(x + m.r(-0.03, 0.03), y, -L)], 0.005, V(1, 0, 0), shade(FRESH, 0.8), wnd)
        for k in range(n):
            t = k / (n - 1); z = -0.08 - t * (L - 0.1)
            rr = 0.125 * (1 - t) ** 0.8 + 0.02
            a = k * 2.39996; p = V(x + math.cos(a) * rr * 0.75, y + math.sin(a) * rr * 0.75, z)
            col = mixc(hi, lo, t ** 0.8)
            s = 0.074 * (1 - 0.5 * t)
            m.blob(p, s, 4, 2, shade(col, 0.78), wnd, squash=(1, 1, 1.25), top=shade(col, 1.15))
    # leaves at the top: a few drooping leaflets
    for i in range(6):
        a = m.r(TAU); d = V(math.cos(a), math.sin(a), 0); x = m.r(-0.5, 0.5)
        pts = [V(x, 0, 0.02), V(x, 0, 0.0) + d * 0.2 + V(0, 0, 0.03), V(x, 0, 0.0) + d * 0.36 + V(0, 0, -0.12)]
        m.strip(pts, [0.02, 0.05, 0.004], np.cross(d, V(0, 0, 1)), lambda t: mixc(LUSH, FRESH, t), lambda t, p: (0.9, 0.25 * t, 0.0, 1.0))
    v = np.array(m.v)
    m.export({"sway": 1.6, "foliage": 0.3, "height": 0.05, "radius": 0.6, "baseRadius": 0.6, "collide": False, "hang": round(float(-v[:, 2].min()), 3)})


# ------------------------------------------------------------------------------------- mast
def cottongrass():
    """Cotton grass: white tufts streaming from thin stems."""
    m = Model("cottongrass", 14); H = 0.62; W = sway(H)
    for i in range(6):
        a = TAU * i / 6 + m.r(0.4); d = V(math.cos(a), math.sin(a), 0); L = m.r(0.22, 0.36)
        pts = [d * 0.02, d * 0.07 + V(0, 0, L * 0.7), d * (0.07 + L * 0.5) + V(0, 0, L * 0.9)]
        m.strip(pts, [0.010, 0.008, 0.001], np.cross(d, V(0, 0, 1)), lambda t: mixc(LUSH, (0.30, 0.36, 0.12), t), W(0.7))
    for i in range(5):
        a = TAU * i / 5 + m.r(0.5); rr = m.r(0.01, 0.07); d = V(math.cos(a), math.sin(a), 0)
        h = m.r(0.40, H - 0.05); top = d * (rr + 0.05) + V(0.03, 0, h)
        m.tube([d * rr, d * (rr + 0.02) + V(0, 0, h * 0.55), top], [0.005, 0.004, 0.003], 3, (0.24, 0.30, 0.10), W(0.3))
        # the tuft hangs a little downwind (+x)
        m.blob(top + V(0.03, 0, 0.0), m.r(0.040, 0.056), 4, 3, (0.80, 0.80, 0.74), W(1.0), squash=(1.5, 0.9, 0.95), top=(1.0, 1.0, 0.97), axis=(0.25, 0, 1))
    m.export({"sway": 1.1, "lod0": 45})


def heather():
    """Bell heather: a springy dark mound, every sprig tipped with a spike of magenta bells."""
    m = Model("heather", 9); H = 0.46; W = sway(H)
    dark, bell0, bell1 = (0.04, 0.12, 0.05), (0.50, 0.06, 0.36), (0.86, 0.34, 0.72)
    m.blob((0, 0, 0.0), 0.30, 7, 3, dark, (0.2, 0.1), squash=(1, 1, 0.62), top=(0.10, 0.22, 0.08))
    for i in range(9):
        a = TAU * i * 0.618 + m.r(0.4); rr = 0.05 + 0.24 * math.sqrt((i + 0.5) / 9); d = V(math.cos(a), math.sin(a), 0)
        base = d * rr * 0.8 + V(0, 0, 0.14 * (1 - (rr / 0.3) ** 2) + 0.03)
        ax = norm(d * (0.35 + rr * 1.6) + V(0, 0, 1))
        L = m.r(0.16, 0.26)
        tip = base + ax * L
        m.strip([base, tip], [0.006, 0.004], np.cross(ax, d + V(0, 0, 0.01)), (0.10, 0.20, 0.07), W(0.5))
        m.blob(tip + ax * 0.02, m.r(0.028, 0.036), 4, 3, bell0, W(1.0), squash=(1, 1, 2.3), top=mixc(bell0, bell1, m.r(0.5, 1.0)), axis=ax)
    m.export({"sway": 0.45, "lod0": 45})


# ------------------------------------------------------------------------------------- boat
def marigold(name="marigold", seed=6):
    """Marigold: a bushy plant crowned with ruffled orange and gold pompoms."""
    m = Model(name, seed); H = 0.52; W = sway(H)
    leaf = (0.06, 0.20, 0.05)
    deep, hot, warm = (0.80, 0.10, 0.01), (0.96, 0.24, 0.015), (0.98, 0.46, 0.02)
    for i in range(6):
        a = TAU * i / 6 + m.r(0.4); d = V(math.cos(a), math.sin(a), 0); L = m.r(0.16, 0.26); z = m.r(0.05, 0.3)
        pts = [d * 0.03 + V(0, 0, z), d * (0.03 + L * 0.6) + V(0, 0, z + 0.07), d * (0.03 + L) + V(0, 0, z + 0.01)]
        m.strip(pts, [0.02, 0.06, 0.004], np.cross(d, V(0, 0, 1)), lambda t: mixc(leaf, LUSH, t), W(0.7))
    for i in range(5):
        a = TAU * i / 5 + m.r(0.6); rr = 0.0 if i == 0 else m.r(0.05, 0.13); d = V(math.cos(a), math.sin(a), 0)
        h = H - 0.07 if i == 0 else m.r(0.30, H - 0.09)
        top = d * (rr + h * 0.16) + V(0, 0, h)
        m.tube([d * rr * 0.4, top], [0.009, 0.007], 3, STEM, W(0.3))
        nrm = norm(d * 0.25 + V(0, 0, 1)); big = m.r(0.066, 0.09)
        c0 = mixc(hot, warm, m.r(0.0, 1.0))
        m.fan(top - nrm * 0.02, -nrm, big * 0.5, 4, STEM, FRESH, W(0.4), cone=0.9)                       # calyx
        for k, (rs, zz) in enumerate(((1.0, 0.0), (0.62, 0.034))):
            m.fan(top + nrm * zz, nrm, big * rs, 8, mixc(c0, deep, 0.55 - 0.3 * k), mixc(c0, GOLD, 0.22 * k), W(1.0), cone=0.2, ruffle=0.12)
    m.export({"sway": 0.6, "lod0": 45})


def seapoppy():
    """Horned sea-poppy: lemon cups over a rosette of blue-grey leaves, with one long curved pod."""
    m = Model("seapoppy", 12); H = 0.42; W = sway(H)
    glauc, glauc2 = (0.20, 0.33, 0.28), (0.36, 0.48, 0.40)
    for i in range(6):
        a = TAU * i / 6 + m.r(0.3); d = V(math.cos(a), math.sin(a), 0); L = m.r(0.2, 0.3)
        pts = [d * 0.02 + V(0, 0, 0.02), d * L * 0.45 + V(0, 0, 0.11), d * L + V(0, 0, 0.04)]
        m.strip(pts, [0.02, 0.06, 0.004], np.cross(d, V(0, 0, 1)), lambda t: mixc(glauc, glauc2, t), W(0.6), cup=-0.25)
    for i in range(3):
        a = TAU * i / 3 + m.r(0.8); d = V(math.cos(a), math.sin(a), 0); h = m.r(0.26, H - 0.06); rr = m.r(0.02, 0.08)
        top = d * (rr + 0.06) + V(0, 0, h)
        m.tube([d * rr, top], [0.007, 0.005], 3, glauc, W(0.3))
        for k in range(4):
            an = TAU * k / 4 + i; o = V(math.cos(an), math.sin(an), 0)
            pts = [top, top + o * 0.045 + V(0, 0, 0.035), top + o * 0.085 + V(0, 0, 0.060)]
            m.strip(pts, [0.012, 0.05, 0.03], np.cross(o, V(0, 0, 1)), lambda t: mixc(GOLD, LEMON, t), W(1.0))
        m.blob(top + V(0, 0, 0.022), 0.016, 4, 2, ORANGE, W(0.6))
    d = V(0.6, -0.5, 0)
    m.tube([V(0, 0, 0.12), d * 0.12 + V(0, 0, 0.26), d * 0.30 + V(0, 0, 0.30), d * 0.46 + V(0, 0, 0.24)], [0.008, 0.007, 0.006, 0.002], 3, glauc2, W(0.5))
    m.export({"sway": 0.6, "lod0": 45})


def marram():
    """Marram: a tussock of long pale dune grass."""
    m = Model("marram", 2); H = 0.95; W = sway(H, 1.3)
    for i in range(18):
        a = TAU * i / 18 + m.r(0.3); d = V(math.cos(a), math.sin(a), 0); L = m.r(0.6, 1.0); out = m.r(0.25, 0.7)
        ctrl = (d * 0.03, d * L * out * 0.35 + V(0, 0, L * 0.85), d * L * out + V(0.08, 0, L * m.r(0.45, 0.8)))
        pts = [bez(*ctrl, t) for t in np.linspace(0, 1, 5)]
        m.strip(pts, [0.012, 0.012, 0.010, 0.007, 0.001], np.cross(d, V(0, 0, 1)), lambda t: mixc((0.20, 0.30, 0.10), (0.62, 0.60, 0.30), t ** 0.8), W(0.8))
    m.export({"sway": 1.0, "lod0": 50})


# ------------------------------------------------------------------------------------- clock meadow
def leaves_rosette(m, n, L0, L1, W, col0=LUSH, col1=FRESH):
    """A dandelion's toothed leaves, flat on the ground and lifting at the tips."""
    for i in range(n):
        a = TAU * i / n + m.r(0.3); d = V(math.cos(a), math.sin(a), 0); L = m.r(L0, L1); side = np.cross(d, V(0, 0, 1))
        ts = np.linspace(0, 1, 7)
        pts = [d * (0.05 + L * t) + V(0, 0, 0.04 + 0.22 * L * math.sin(t * math.pi * 0.9) + 0.10 * L * t * t) for t in ts]
        wid = [L * w for w in (0.03, 0.10, 0.06, 0.15, 0.09, 0.17, 0.01)]        # the teeth
        m.strip(pts, wid, side, lambda t: mixc(col0, col1, t), W(0.5), cup=-0.18)


def dandelion_clock(name="dandelion_clock", seed=31, bare=0.0):
    """A dandelion gone to seed, grown taller than a rider: a globe of parasols on a hollow stalk."""
    m = Model(name, seed); H = 3.0; W = sway(H, 1.6)
    stalk0, stalk1 = (0.30, 0.34, 0.14), (0.40, 0.50, 0.20)
    lean = V(m.r(-0.25, 0.25), m.r(-0.25, 0.25), 0)
    head = V(lean[0], lean[1], H - 0.62)
    pts = [bez(V(0, 0, 0), V(-lean[0] * 0.6, -lean[1] * 0.6, H * 0.5), head, t) for t in np.linspace(0, 1, 7)]
    m.tube(pts, [0.075, 0.07, 0.064, 0.058, 0.052, 0.046, 0.042], 6, lambda t: mixc((0.36, 0.26, 0.20), stalk1, min(t * 2.5, 1.0)), W(0.0))
    m.blob(head, 0.10, 6, 4, (0.70, 0.72, 0.52), W(0.2), top=(0.86, 0.86, 0.70))
    R = 0.56
    for dv in fib(78):
        if dv[2] < -0.86: continue                               # where the stalk comes in
        if bare > 0 and (dv[0] * 0.8 + dv[2] * 0.3 + m.r(-0.25, 0.25)) > 1.0 - 1.6 * bare: continue      # the wind has had these
        d = norm(dv + V(m.r(-0.07, 0.07), m.r(-0.07, 0.07), m.r(-0.07, 0.07)))
        tip = head + d * R * m.r(0.94, 1.04)
        e1 = norm(np.cross(d, V(0, 0, 1) if abs(d[2]) < 0.9 else V(1, 0, 0)))
        wnd = W(1.0)(0, tip)
        m.add([head + d * 0.09 - e1 * 0.004, head + d * 0.09 + e1 * 0.004, tip + e1 * 0.003, tip - e1 * 0.003], [(0, 1, 2, 3)], [(0.60, 0.55, 0.42)] * 2 + [(0.90, 0.90, 0.84)] * 2, [W(0.5)(0, head), W(0.5)(0, head), wnd, wnd])
        # the parasol: a shallow cone opening outward
        m.fan(tip - d * 0.035, d, 0.135, 6, (0.62, 0.62, 0.56), shade((0.93, 0.93, 0.89), m.r(0.86, 1.0)), wnd, cone=-0.42)
    leaves_rosette(m, 8, 0.8, 1.25, W)
    m.export({"sway": 0.30, "foliage": 0.9, "lod0": 120})


def dandelion_bloom():
    """The same giant dandelion in flower: a golden head as wide as a cartwheel."""
    m = Model("dandelion_bloom", 44); H = 2.2; W = sway(H, 1.6)
    lean = V(0.18, -0.12, 0)
    head = V(lean[0], lean[1], H - 0.16)
    pts = [bez(V(0, 0, 0), V(-lean[0], -lean[1], H * 0.5), head, t) for t in np.linspace(0, 1, 6)]
    m.tube(pts, [0.07, 0.064, 0.058, 0.052, 0.047, 0.044], 6, lambda t: mixc((0.36, 0.26, 0.20), (0.40, 0.50, 0.20), min(t * 2.5, 1.0)), W(0.0))
    nrm = norm(V(lean[0] * 0.6, lean[1] * 0.6, 1))
    e1 = norm(np.cross(nrm, V(1, 0, 0))); e2 = np.cross(nrm, e1)
    for k in range(12):                                             # bracts curling back under the head
        an = TAU * k / 12; o = e1 * math.cos(an) + e2 * math.sin(an)
        m.add([head - nrm * 0.02 + np.cross(nrm, o) * 0.03, head - nrm * 0.02 - np.cross(nrm, o) * 0.03, head + o * 0.2 - nrm * 0.13], [(0, 1, 2)], [LUSH, LUSH, FRESH], [W(0.5)(0, head)] * 3)
    for ring, (n, L, up, col) in enumerate(((22, 0.46, 0.06, GOLD), (18, 0.36, 0.30, mixc(GOLD, LEMON, 0.25)), (13, 0.24, 0.75, mixc(GOLD, ORANGE, 0.25)), (8, 0.12, 1.6, mixc(GOLD, ORANGE, 0.45)))):
        for k in range(n):
            an = TAU * (k + 0.5 * ring) / n + m.r(-0.05, 0.05); o = e1 * math.cos(an) + e2 * math.sin(an); t2 = np.cross(nrm, o)
            LL = L * m.r(0.88, 1.08)
            tip = head + o * LL + nrm * (LL * up + 0.02)
            mid = head + o * LL * 0.5 + nrm * (LL * up * 0.42 + 0.03)
            wd = LL * 0.085 + 0.012
            m.add([head + nrm * 0.02, mid - t2 * wd, tip - t2 * wd * 0.7, tip + t2 * wd * 0.7, mid + t2 * wd], [(0, 1, 4), (1, 2, 3, 4)],
                  [shade(col, 0.72), col, mixc(col, LEMON, 0.35), mixc(col, LEMON, 0.35), col], [W(1.0)(0, tip)] * 5)
    leaves_rosette(m, 8, 0.8, 1.2, W)
    m.export({"sway": 0.30, "foliage": 0.9, "lod0": 120})


# ------------------------------------------------------------------------------------- hand
def spiderlily():
    """Red spider lily: a bare stalk, a burst of curled-back petals and long whiskers."""
    m = Model("spiderlily", 17); H = 0.62; W = sway(H)
    red, red2, whisk = (0.42, 0.004, 0.012), (0.66, 0.012, 0.018), (0.74, 0.04, 0.03)
    top = V(0.02, 0.0, H - 0.14)
    m.tube([V(0, 0, 0), V(0.0, 0.01, H * 0.5), top], [0.010, 0.009, 0.008], 3, lambda t: mixc((0.16, 0.22, 0.08), (0.30, 0.20, 0.10), t), W(0.2))
    for i in range(5):
        a = TAU * i / 5 + m.r(0.3); o = V(math.cos(a), math.sin(a), 0); c = top + o * 0.035 + V(0, 0, 0.01)
        ax = norm(o + V(0, 0, 0.55))
        e1 = norm(np.cross(ax, V(0, 0, 1))); e2 = np.cross(ax, e1)
        for k in range(4):
            an = TAU * k / 4 + i; q = e1 * math.cos(an) + e2 * math.sin(an)
            # each petal runs out along the floret's axis, then curls right back on itself
            pts = [c, c + ax * 0.08 + q * 0.04, c + ax * 0.105 + q * 0.10, c + ax * 0.06 + q * 0.14]
            m.strip(pts, [0.007, 0.016, 0.013, 0.002], np.cross(ax, q), lambda t: mixc(red, red2, t), W(1.0))
        for k in range(2):
            an = TAU * k / 2 + i * 1.7; q = e1 * math.cos(an) + e2 * math.sin(an)
            pts = [c, c + ax * 0.15 + q * 0.03, c + ax * 0.25 + q * 0.035 + V(0, 0, 0.09)]
            m.strip(pts, [0.004, 0.0035, 0.005], np.cross(ax, q), lambda t: mixc(red2, whisk if t < 0.9 else (0.95, 0.55, 0.10), t), W(1.0))
    m.export({"sway": 0.8, "lod0": 45})


def moss():
    """A cushion of emerald moss."""
    m = Model("moss", 23)
    for (x, y, r, h) in ((0, 0, 0.42, 0.55), (0.34, 0.16, 0.26, 0.6), (-0.26, 0.22, 0.22, 0.6), (0.08, -0.33, 0.24, 0.5)):
        m.blob((x, y, 0.0), r, 6, 3, (0.03, 0.13, 0.03), (0.0, 0.0), squash=(1, 1, h), top=(0.16, 0.40, 0.07))
    v = np.array(m.v); keep = v[:, 2] >= -0.02
    m.export({"sway": 0.0, "thin": False, "lod0": 55})


# ------------------------------------------------------------------------------------- dressing
def pennant(name, col, col2, seed):
    """A tall crooked pole flying one long swallow-tailed pennant. The cloth streams along +x: turn
    the piece so +x points downwind."""
    m = Model(name, seed); H = 9.6
    wood0, wood1 = (0.20, 0.13, 0.07), (0.36, 0.27, 0.16)
    bend = V(m.r(-0.14, 0.14), m.r(-0.14, 0.14), 0)
    pts = [bez(V(0, 0, -0.5), V(bend[0] * 2, bend[1] * 2, H * 0.5), V(0, 0, H), t) for t in np.linspace(0, 1, 7)]
    def polew(t, p): return (0.0, 0.25 * max(p[2] / H, 0) ** 2, 0.0, 1.0)
    m.tube(pts, [0.12, 0.112, 0.104, 0.094, 0.082, 0.07, 0.058], 6, lambda t: mixc(wood0, wood1, 0.3 + 0.7 * t), polew, cap=True)
    for z in (H * 0.33, H * 0.62, H - 0.3):                         # rope lashings
        m.tube([V(0, 0, z - 0.06), V(0, 0, z + 0.06)], 0.125 - 0.055 * z / H, 6, (0.50, 0.42, 0.26), polew)
    m.blob(V(0, 0, H + 0.1), 0.12, 6, 3, (0.80, 0.58, 0.16), polew, top=(1.0, 0.82, 0.36))
    # the cloth: hoisted near the top, long and tapering, split into two tails
    L, W0 = 8.2, 0.95
    nx, ny = 18, 4
    top = H - 0.4
    verts, cols, winds, faces = [], [], [], []
    for i in range(nx + 1):
        t = i / nx; x = 0.07 + L * t
        half = W0 * 0.5 * (1 - 0.5 * t)
        for j in range(ny + 1):
            u = j / ny * 2 - 1
            z = top - W0 * 0.5 + u * half
            # swallow tail: the middle of the free end is cut back
            xx = x - (max(t - 0.72, 0) / 0.28) * L * 0.16 * (1 - abs(u)) if t > 0.72 else x
            verts.append(V(xx, 0, z))
            c = col2 if abs(u) > 0.62 else col
            cols.append(shade(c, 0.86 + 0.2 * (1 - t)))
            winds.append((0.5 * t, 0.25 * (z / H) ** 2, 0.0, 1.0 - t))
    for i in range(nx):
        for j in range(ny):
            a = i * (ny + 1) + j
            faces.append((a, a + ny + 1, a + ny + 2, a + 1))
    m.add(verts, faces, cols, winds)
    m.export({"sway": 0.5, "cloth": [L, 0.62], "foliage": 0.45, "height": H, "radius": 0.5, "baseRadius": 0.2,
              "slabs": [[0, 0, 0.16, 0.0, H]], "solid": [[0, 0, 0.16, 0.0, H]]})


def bunting():
    """A stay rope strung with little flags, from a masthead down to a peg in the turf. Origin under
    the masthead; the rope leaves it 14.2 m up and meets the ground 11.5 m out along +x."""
    m = Model("bunting", 77)
    top, peg = V(0.1, 0, 14.2), V(11.5, 0, 0.05)
    n = 30
    cols_ = [(0.80, 0.07, 0.05), WHITE, GOLD, (0.10, 0.30, 0.62), WHITE, ORANGE]
    pts = []
    for i in range(n + 1):
        t = i / n
        p = top + (peg - top) * t
        p[2] -= math.sin(t * math.pi) * 1.0                             # sag
        pts.append(p)
    def ropew(t, p): return (0.0, 0.5 * math.sin(t * math.pi), 0.0, 1.0)
    m.tube(pts, 0.02, 4, (0.46, 0.38, 0.22), ropew)
    m.tube([peg + V(0, 0, 0.4), peg + V(0.14, 0, -0.3)], [0.055, 0.03], 5, (0.26, 0.18, 0.10), (0, 0))
    for i in range(2, n - 1):
        t = (i + 0.5) / n; a, b = pts[i], pts[i + 1]
        c = cols_[i % len(cols_)]
        mid = (a + b) * 0.5 + V(0, 0, -0.72)
        sw = 0.5 * math.sin(t * math.pi)
        m.add([a, b, mid], [(0, 1, 2)], [shade(c, 0.9), shade(c, 0.9), c],
              [(0.2, sw, 0.0, 1.0), (0.2, sw, 0.0, 1.0), (1.0, sw, 0.0, 0.0)])
    m.export({"sway": 0.8, "cloth": [0.72, 0.2], "foliage": 0.45, "height": 14.2, "radius": 11.6, "baseRadius": 0.3, "slabs": [], "collide": False})


def groyne_post():
    """A weathered timber post from an old groyne: tide-dark at the foot, bleached above, a turn of rope."""
    m = Model("groyne_post", 19); H = 2.3
    def col(t):
        wet = (0.10, 0.09, 0.07); dry = (0.50, 0.42, 0.32)
        return mixc(wet, dry, min(max((t - 0.18) / 0.25, 0), 1)) if t < 0.9 else (0.60, 0.53, 0.42)
    lean = V(0.10, 0.05, 0)
    pts = [V(0, 0, -0.5) + lean * 0.0, V(0, 0, 0.4) + lean * 0.4, V(0, 0, 1.3) + lean * 1.3, V(0, 0, 2.05) + lean * 2.05, V(0, 0, H) + lean * H]
    m.tube(pts, [0.17, 0.165, 0.15, 0.14, 0.10], 7, col, (0, 0), cap=True)
    m.tube([V(0, 0, 1.55) + lean * 1.55, V(0, 0, 1.72) + lean * 1.72], 0.168, 7, (0.62, 0.52, 0.30), (0, 0))
    # a few barnacles at the tide line
    for i in range(7):
        a = m.r(TAU); z = m.r(0.05, 0.5)
        m.blob(V(math.cos(a) * 0.165, math.sin(a) * 0.165, z) + lean * z, m.r(0.025, 0.04), 4, 2, (0.62, 0.60, 0.52), (0, 0), top=(0.86, 0.84, 0.76))
    m.export({"sway": 0.0, "thin": False, "height": H, "radius": 0.3, "baseRadius": 0.2, "slabs": [[0.1, -0.05, 0.2, 0.0, H]]})


def oar_flag():
    """An oar stood on end in the wreck with a rag of sailcloth knotted under its blade: the Marigold's
    last ensign. The rag streams along +x: turn the piece so +x points downwind."""
    m = Model("oar_flag", 23); H = 4.4
    wood0, wood1 = (0.28, 0.20, 0.12), (0.52, 0.42, 0.28)
    lean = V(0.30, 0.12, 0)
    def polew(t, p): return (0.0, 0.2 * max(p[2] / H, 0) ** 2, 0.0, 1.0)
    at = lambda f: V(0, 0, H * f) + lean * f
    m.tube([at(-0.08), at(0.3), at(0.6), at(0.8)], [0.05, 0.047, 0.044, 0.04], 6, lambda t: mixc(wood0, wood1, t), polew)
    m.strip([at(0.8), at(0.9), at(1.0)], [0.05, 0.12, 0.10], V(0, 1, 0), lambda t: mixc(wood1, (0.62, 0.54, 0.40), t), polew)
    m.tube([at(0.755), at(0.775)], 0.052, 6, (0.56, 0.47, 0.30), polew)                # the knot
    orange, cream = (0.96, 0.34, 0.03), (0.93, 0.88, 0.74)
    L, W0 = 2.7, 0.78
    nx, ny = 11, 3
    o = at(0.765)
    verts, cols, winds, faces = [], [], [], []
    for i in range(nx + 1):
        t = i / nx
        half = W0 * 0.5 * (1 - 0.30 * t)
        for j in range(ny + 1):
            u = j / ny * 2 - 1
            fray = m.r(-0.10, 0.04) * L if i == nx else 0.0                             # the torn free edge
            verts.append(V(o[0] + 0.05 + L * t + fray, o[1], o[2] - W0 * 0.5 + u * half))
            c = orange if (j % 2 == 0) else cream
            cols.append(shade(c, 0.82 + 0.22 * (1 - t)))
            winds.append((0.5 * t, 0.2 * (o[2] / H) ** 2, 0.0, 1.0 - t))
    for i in range(nx):
        for j in range(ny):
            a = i * (ny + 1) + j
            faces.append((a, a + ny + 1, a + ny + 2, a + 1))
    m.add(verts, faces, cols, winds)
    m.export({"sway": 0.4, "cloth": [L, 0.34], "foliage": 0.45, "height": H, "radius": 0.4, "baseRadius": 0.1,
              "slabs": [[0.15, -0.06, 0.12, 0.0, H]], "collide": False})


def driftwood():
    """A sea-silvered branch: a crooked bough with two broken limbs."""
    m = Model("driftwood", 13)
    g0, g1 = (0.42, 0.38, 0.32), (0.72, 0.68, 0.60)
    def bark(t): return mixc(g0, g1, 0.45 + 0.4 * math.sin(t * 13) + 0.15 * math.sin(t * 41))
    pts = [V(-1.3, 0.12, 0.10), V(-0.8, -0.02, 0.15), V(-0.2, 0.05, 0.13), V(0.4, -0.04, 0.17), V(0.95, 0.14, 0.13), V(1.4, 0.34, 0.20), V(1.75, 0.42, 0.34)]
    m.tube(pts, [0.085, 0.11, 0.105, 0.095, 0.075, 0.05, 0.016], 6, bark, (0, 0), cap=True)
    m.fan(pts[0], pts[0] - pts[1], 0.085, 6, (0.56, 0.48, 0.36), (0.46, 0.40, 0.32), (0, 0))
    m.tube([V(0.2, 0.0, 0.2), V(0.36, -0.26, 0.42), V(0.34, -0.5, 0.72), V(0.44, -0.62, 0.98)], [0.055, 0.045, 0.03, 0.01], 5, bark, (0, 0), cap=True)
    m.tube([V(-0.55, 0.0, 0.2), V(-0.72, 0.24, 0.40), V(-0.70, 0.36, 0.62)], [0.05, 0.035, 0.012], 5, bark, (0, 0), cap=True)
    m.tube([V(0.9, 0.1, 0.16), V(1.05, -0.16, 0.30)], [0.04, 0.012], 4, bark, (0, 0), cap=True)
    m.export({"sway": 0.0, "thin": False, "height": 0.98, "slabs": [[0, 0, 0.9, 0.0, 0.3]], "collide": False})


ALL = {
    "gentian": gentian, "petalfall": petalfall, "wisteria_fall": lambda: petalfall("wisteria_fall", (0.78, 0.66, 0.96), (0.50, 0.30, 0.88), 7), "fern": fern, "flagiris": flagiris, "rimlily": rimlily, "wisteria": wisteria,
    "cottongrass": cottongrass, "heather": heather, "marigold": marigold, "seapoppy": seapoppy, "marram": marram,
    "dandelion_clock": dandelion_clock, "dandelion_half": lambda: dandelion_clock("dandelion_half", 57, 0.55),
    "dandelion_bloom": dandelion_bloom, "spiderlily": spiderlily, "moss": moss,
    "pennant_red": lambda: pennant("pennant_red", (0.80, 0.07, 0.05), (0.98, 0.80, 0.30), 1),
    "pennant_gold": lambda: pennant("pennant_gold", (0.98, 0.66, 0.08), (0.95, 0.94, 0.88), 2),
    "pennant_white": lambda: pennant("pennant_white", (0.95, 0.94, 0.88), (0.10, 0.30, 0.62), 3),
    "bunting": bunting, "driftwood": driftwood, "groyne_post": groyne_post, "oar_flag": oar_flag,
}

bpy.ops.wm.read_factory_settings(use_empty=True)
for name in (WANT or ALL.keys()):
    ALL[name]()
print("FLORA DONE")
