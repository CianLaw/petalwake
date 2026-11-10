# Blender: model the shore-life kit by hand (in code) and pack it for the game.
#
#   barnacle clusters, mussel beds, limpets, anemones, urchins, starfish, shells, cobbles,
#   shore boulders, driftwood, wrack, rockweed, floating kelp - and the crab.
#
# Everything is low-poly with vertex colours and baked occlusion; nothing is textured. Each vertex
# also carries a gloss, a shading kind and (for the weeds) how far along its frond it sits, so the
# game can sway them. The crab's vertices carry the joint they hang from, a gait phase and a weight,
# which is all its walk cycle needs in the vertex shader.
#
# Output (game space: x right, y up, z toward the viewer of a Blender front view, i.e. -Y):
#   <out>/shore.bin    packed vertex and index data
#   <out>/shore.json   the directory: byte offsets, per-mesh ranges, sizes, attachment points
#   <preview>          optional contact sheet
#
# Usage: blender -b -P tools/shore/build_shore.py -- <out_dir> [preview.png]
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "shore")
PREVIEW = argv[1] if len(argv) > 1 else None
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

# shading kinds (shore.js mirrors these)
PLAIN, ROCK, WEED, KELP, WOOD = 0, 1, 3, 4, 5
# crab parts
BODY, LEG, CLAW_R, CLAW_L, EYE, SHADOW = 0, 1, 2, 3, 4, 5

TAU = math.tau


def lerp(a, b, t): return a + (b - a) * t
def lerp3(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)
def mul3(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def clamp01(x): return 0.0 if x < 0 else 1.0 if x > 1 else x
def smooth(a, b, x):
    t = clamp01((x - a) / (b - a))
    return t * t * (3 - 2 * t)


class Part:
    """Vertices with their paint, and faces. Faces are wound to agree with a hint, so the
    occlusion bake always knows which side is out."""

    def __init__(self):
        self.v, self.c, self.g, self.k, self.t, self.p, self.f = [], [], [], [], [], [], []
        self.piv, self.leg = [], []      # crab only: joint position; (phase, weight, part)

    def vert(self, co, col, gloss=0.2, kind=PLAIN, t=0.0, ph=0.0, piv=(0, 0, 0), leg=(0, 0, BODY)):
        self.v.append(Vector(co)); self.c.append(tuple(col)); self.g.append(gloss); self.k.append(kind)
        self.t.append(t); self.p.append(ph); self.piv.append(Vector(piv)); self.leg.append(tuple(leg))
        return len(self.v) - 1

    def face(self, idx, out=None, frm=None):
        """out: direction the face should look; frm: a point the face should look away from."""
        idx = list(idx)
        if out is not None or frm is not None:
            n = Vector((0, 0, 0))
            for i in range(len(idx)):                       # Newell
                a, b = self.v[idx[i]], self.v[idx[(i + 1) % len(idx)]]
                n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
            if frm is not None:
                c = sum((self.v[i] for i in idx), Vector((0, 0, 0))) / len(idx)
                out = c - Vector(frm)
            if n.dot(Vector(out)) < 0: idx.reverse()
        self.f.append(idx)

    def strip(self, a, b, closed=True, frm=None, out=None):
        n = len(a)
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            self.face([a[i], a[j], b[j], b[i]], out=out, frm=frm)

    def fan(self, ring, apex, closed=True, frm=None, out=None):
        n = len(ring)
        for i in range(n if closed else n - 1):
            self.face([ring[i], ring[(i + 1) % n], apex], out=out, frm=frm)

    def add(self, o, M=None):
        """Merge another part, optionally transformed."""
        off = len(self.v)
        M = M or Matrix.Identity(4)
        for i in range(len(o.v)):
            self.v.append(M @ o.v[i]); self.c.append(o.c[i]); self.g.append(o.g[i]); self.k.append(o.k[i])
            self.t.append(o.t[i]); self.p.append(o.p[i]); self.piv.append(M @ o.piv[i]); self.leg.append(o.leg[i])
        flip = M.determinant() < 0
        for f in o.f:
            g = [i + off for i in f]
            self.f.append(g[::-1] if flip else g)
        return off

    def paint(self, fn):
        for i in range(len(self.v)): self.c[i] = fn(self.v[i], self.c[i])


def from_bmesh(bm, col_fn, gloss=0.2, kind=PLAIN):
    p = Part()
    bm.verts.ensure_lookup_table(); bm.verts.index_update()
    for v in bm.verts: p.vert(v.co, col_fn(v.co, v.normal), gloss, kind)
    for f in bm.faces: p.f.append([v.index for v in f.verts])
    return p


# ------------------------------------------------------------------------------------ finishing
_HEMI = []
def _hemi():
    if not _HEMI:
        rng = np.random.default_rng(7)
        for i in range(56):
            u, v = (i + 0.5) / 56, rng.random()
            r, a = math.sqrt(u), TAU * ((i * 0.61803398875 + v * 0.15) % 1.0)
            _HEMI.append((r * math.cos(a), r * math.sin(a), math.sqrt(max(1 - u, 0))))
    return _HEMI


MESHES = {}      # name -> dict of numpy arrays
ORDER = []


def finalize(part, name, sharp=40.0, ao_dist=None, ao_k=1.0, ground=0.55, ground_z=0.0, crab=False, meta=None):
    """Triangulate, split normals at sharp edges, bake occlusion into the vertices."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in part.v], [], part.f)
    me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free()
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(sharp))
    nl = len(me.loops)
    cn = np.empty(nl * 3, np.float32); me.corner_normals.foreach_get("vector", cn); cn = cn.reshape(-1, 3)
    lv = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", lv)
    key, src, nrm, tris = {}, [], [], []
    for poly in me.polygons:
        t = []
        for li in poly.loop_indices:
            n = cn[li]
            k = (int(lv[li]), int(round(n[0] * 60)), int(round(n[1] * 60)), int(round(n[2] * 60)))
            i = key.get(k)
            if i is None:
                i = key[k] = len(src); src.append(int(lv[li])); nrm.append(n.copy())
            t.append(i)
        if len(t) == 3 and len(set(t)) == 3: tris.append(t)
    co = np.array([tuple(part.v[i]) for i in src], np.float32)
    nrm = np.array(nrm, np.float32)
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-6)

    # ---- occlusion: cosine-weighted rays against the mesh itself and the ground it sits on
    size = float(np.linalg.norm(co.max(0) - co.min(0)))
    D = ao_dist or size * 0.45
    solid = [t for t in tris if not (crab and part.leg[src[t[0]]][2] == SHADOW)]
    polys = [tuple(t) for t in solid]
    verts = [tuple(v) for v in co]
    gi = len(polys)
    if ground > 0:
        b = len(verts); L = size * 20
        verts += [(-L, -L, ground_z), (L, -L, ground_z), (L, L, ground_z), (-L, L, ground_z)]
        polys += [(b, b + 1, b + 2), (b, b + 2, b + 3)]
    bvh = BVHTree.FromPolygons(verts, polys, all_triangles=True)
    ao = np.ones(len(co), np.float32)
    for i in range(len(co)):
        n = Vector(nrm[i])
        t = n.orthogonal().normalized(); bt = n.cross(t)
        o = Vector(co[i]) + n * (size * 0.004 + 0.0008)
        acc = 0.0
        for hx, hy, hz in _hemi():
            d = t * hx + bt * hy + n * hz
            hit = bvh.ray_cast(o, d, D)
            if hit[0] is not None:
                w = 1.0 - hit[3] / D
                acc += w * (ground if hit[2] >= gi else 1.0)
        ao[i] = 1.0 - ao_k * acc / len(_HEMI)
    ao = np.clip(ao, 0.0, 1.0)

    # ---- pack (game space: y up)
    def g(v): return (v[0], v[2], -v[1])
    out = {
        "pos": np.array([g(c) for c in co], np.float32),
        "nrm": np.array([g(n) for n in nrm], np.float32),
        "ao": ao,
        "col": np.array([part.c[i] for i in src], np.float32),
        "gloss": np.array([part.g[i] for i in src], np.float32),
        "kind": np.array([part.k[i] for i in src], np.uint8),
        "t": np.array([part.t[i] for i in src], np.float32),
        "ph": np.array([part.p[i] for i in src], np.float32),
        "idx": np.array(tris, np.uint32).reshape(-1),
        "meta": dict(meta or {}),
        "crab": crab,
    }
    if crab:
        out["piv"] = np.array([g(part.piv[i]) for i in src], np.float32)
        out["leg"] = np.array([part.leg[i] for i in src], np.float32)
    p = out["pos"]
    out["meta"].update({"radius": round(float(np.hypot(p[:, 0], p[:, 2]).max()), 4), "height": round(float(p[:, 1].max()), 4), "low": round(float(p[:, 1].min()), 4)})
    MESHES[name] = out
    ORDER.append(name)
    print(f"  {name:18s} {len(co):4d} verts {len(tris):4d} tris  r {out['meta']['radius']:.3f} h {out['meta']['height']:.3f}")
    # keep a Blender object for the contact sheet
    pv = bpy.data.meshes.new(name + "_pv")
    pv.from_pydata([tuple(c) for c in co], [], [tuple(t) for t in tris]); pv.update()
    ca = pv.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="POINT")
    lit = np.clip(out["col"], 0, 1) ** 2.2 * (0.35 + 0.65 * ao[:, None])
    if crab:   # masks -> a stand-in orange
        m = out["col"]
        lit = (np.outer(m[:, 0], (0.80, 0.19, 0.045)) + np.outer(m[:, 1], (0.80, 0.70, 0.52)) + np.outer(m[:, 2], (0.02, 0.02, 0.025))) * (0.35 + 0.65 * ao[:, None])
    ca.data.foreach_set("color", np.concatenate([lit, np.ones((len(co), 1))], 1).astype(np.float32).reshape(-1))
    pv.shade_smooth(); pv.set_sharp_from_angle(angle=math.radians(sharp))
    ob = bpy.data.objects.new(name, pv)
    bpy.context.scene.collection.objects.link(ob)
    return out


# ====================================================================================== barnacles
def barnacle(P, cx, cy, r, h, n, rng, lean=(0.0, 0.0), tone=1.0):
    a0 = rng.uniform(0, TAU)
    base, rim = [], []
    for i in range(n):
        a = a0 + i * TAU / n
        rr = r * rng.uniform(0.9, 1.12)
        plate = 0.86 if i % 2 else 1.04
        base.append(P.vert((cx + math.cos(a) * rr, cy + math.sin(a) * rr, -0.006), mul3((0.50, 0.47, 0.39), tone * plate * rng.uniform(0.92, 1.06)), 0.18))
    for i in range(n):
        a = a0 + (i + 0.2) * TAU / n
        rr = r * rng.uniform(0.44, 0.56)
        hh = h * rng.uniform(0.86, 1.12)
        rim.append(P.vert((cx + lean[0] * hh + math.cos(a) * rr, cy + lean[1] * hh + math.sin(a) * rr, hh), mul3((0.80, 0.78, 0.69), tone * rng.uniform(0.94, 1.05)), 0.28))
    ctr = P.vert((cx + lean[0] * h * 0.5, cy + lean[1] * h * 0.5, h * 0.40), (0.10, 0.085, 0.075), 0.5)
    c = (cx, cy, h * 0.3)
    P.strip(base, rim, frm=c)
    P.fan(rim, ctr, out=(0, 0, 1))


def barnacle_cluster(seed, k, spread, rmax, rmin, big=6):
    rng = np.random.default_rng(seed)
    P = Part()
    placed = []
    for i in range(k):
        r = lerp(rmax, rmin, (i / max(k - 1, 1)) ** 0.75) * rng.uniform(0.92, 1.08)
        for _ in range(300):
            a, d = rng.uniform(0, TAU), spread * math.sqrt(rng.random()) * (0.25 if i == 0 else 1.0)
            x, y = math.cos(a) * d, math.sin(a) * d
            if all(math.hypot(x - px, y - py) > (r + pr) * 0.80 for px, py, pr in placed): break
        placed.append((x, y, r))
    cx = sum(p[0] for p in placed) / k; cy = sum(p[1] for p in placed) / k
    for x, y, r in placed:
        dx, dy = x - cx, y - cy
        dl = math.hypot(dx, dy) or 1.0
        lean = (dx / dl * 0.22 * min(dl / spread, 1), dy / dl * 0.22 * min(dl / spread, 1))
        barnacle(P, x - cx, y - cy, r, r * rng.uniform(0.80, 1.25), big if r > rmax * 0.72 else 5, rng, lean, rng.uniform(0.86, 1.06))
    return P


# ====================================================================================== mussels
def mussel(L, rng):
    P = Part()
    navy = (0.075, 0.085, 0.14); blue = (0.17, 0.20, 0.31); worn = (0.33, 0.30, 0.29)
    w = rng.uniform(0.92, 1.1)
    A = P.vert((0, 0.5 * L, 0.01 * L), worn, 0.5)
    B = P.vert((0.17 * L * w, 0.18 * L, 0), navy, 0.8)
    C = P.vert((0.25 * L * w, -0.22 * L, 0), navy, 0.8)
    D = P.vert((0, -0.5 * L, 0.02 * L), mul3(navy, 1.3), 0.8)
    E = P.vert((-0.25 * L * w, -0.22 * L, 0), navy, 0.8)
    F = P.vert((-0.17 * L * w, 0.18 * L, 0), navy, 0.8)
    R1 = P.vert((0.01 * L, 0.2 * L, 0.25 * L), mul3(blue, rng.uniform(0.85, 1.1)), 0.85)
    R2 = P.vert((-0.01 * L, -0.2 * L, 0.29 * L), mul3(blue, rng.uniform(0.8, 1.15)), 0.85)
    c = (0, 0, -0.3 * L)
    for f in ([A, B, R1], [B, C, R2, R1], [C, D, R2], [D, E, R2], [E, F, R1, R2], [F, A, R1]): P.face(f, frm=c)
    return P


def mussel_bed(seed, k, lx, ly):
    rng = np.random.default_rng(seed)
    P = Part()
    pts = []
    bed = rng.uniform(0, TAU)
    for i in range(k):
        for _ in range(200):
            x, y = rng.uniform(-lx, lx), rng.uniform(-ly, ly)
            if (x / lx) ** 2 + (y / ly) ** 2 > 1: continue
            if all(math.hypot(x - px, y - py) > 0.05 for px, py in pts): break
        pts.append((x, y))
        L = rng.uniform(0.08, 0.125)
        pitch = rng.uniform(0.20, 0.55)
        yaw = bed + rng.uniform(-0.6, 0.6) + (math.pi if rng.random() < 0.25 else 0)
        M = Matrix.Translation((x, y, math.sin(pitch) * L * 0.42 - 0.008)) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(-pitch, 4, "X")
        P.add(mussel(L, rng), M)
    return P


# ====================================================================================== limpets
def limpet(P, cx, cy, r, rng, tint):
    n = 8
    a0 = rng.uniform(0, TAU)
    ring = []
    for i in range(n):
        a = a0 + i * TAU / n
        rr = r * (1.0 if i % 2 else 0.84) * rng.uniform(0.95, 1.05)
        col = mul3(tint, 1.18 if i % 2 else 0.62)
        ring.append(P.vert((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.9, -0.004), col, 0.22))
    apex = P.vert((cx + math.cos(a0) * r * 0.16, cy + math.sin(a0) * r * 0.16, r * 0.46), mul3(tint, 1.45), 0.3)
    P.fan(ring, apex, frm=(cx, cy, -r))


def limpets(seed, k):
    rng = np.random.default_rng(seed)
    P = Part(); pts = []
    for i in range(k):
        r = rng.uniform(0.034, 0.058) * (1.0 - 0.12 * i)
        for _ in range(200):
            x, y = rng.uniform(-0.11, 0.11), rng.uniform(-0.11, 0.11)
            if all(math.hypot(x - px, y - py) > r + pr + 0.012 for px, py, pr in pts): break
        pts.append((x, y, r))
        limpet(P, x, y, r, rng, lerp3((0.56, 0.50, 0.40), (0.44, 0.46, 0.36), rng.random()))
    return P


# ====================================================================================== anemones
def anemone_closed(P, cx, cy, r, rng):
    n = 6
    red = (0.62, 0.065, 0.06)
    rings = []
    a0 = rng.uniform(0, TAU)
    for rr, z, cm in ((1.0, -0.004, 0.50), (1.07, 0.40, 0.95), (0.60, 0.84, 1.25)):
        rings.append([P.vert((cx + math.cos(a0 + i * TAU / n) * rr * r, cy + math.sin(a0 + i * TAU / n) * rr * r, z * r), mul3(red, cm * rng.uniform(0.9, 1.1)), 0.9) for i in range(n)])
    top = P.vert((cx, cy, 0.72 * r), mul3(red, 0.55), 0.9)
    c = (cx, cy, 0.3 * r)
    P.strip(rings[0], rings[1], frm=c); P.strip(rings[1], rings[2], frm=c); P.fan(rings[2], top, out=(0, 0, 1))


def anemone_open(seed):
    rng = np.random.default_rng(seed)
    P = Part(); n = 7; r = 0.055
    col = (0.44, 0.20, 0.27)
    a0 = rng.uniform(0, TAU)
    base = [P.vert((math.cos(a0 + i * TAU / n) * r * 0.82, math.sin(a0 + i * TAU / n) * r * 0.82, -0.004), mul3(col, 0.6), 0.7) for i in range(n)]
    lip = [P.vert((math.cos(a0 + i * TAU / n) * r * 0.9, math.sin(a0 + i * TAU / n) * r * 0.9, r * 0.75), col, 0.7) for i in range(n)]
    mouth = P.vert((0, 0, r * 0.62), (0.30, 0.07, 0.12), 0.8)
    P.strip(base, lip, frm=(0, 0, r * 0.3)); P.fan(lip, mouth, out=(0, 0, 1))
    m = 15
    for i in range(m):
        a = a0 + (i + rng.uniform(-0.2, 0.2)) * TAU / m
        w = 0.26
        b0 = P.vert((math.cos(a - w) * r * 0.84, math.sin(a - w) * r * 0.84, r * 0.76), (0.72, 0.40, 0.48), 0.6)
        b1 = P.vert((math.cos(a + w) * r * 0.84, math.sin(a + w) * r * 0.84, r * 0.76), (0.72, 0.40, 0.48), 0.6)
        L = r * rng.uniform(1.75, 2.35)
        tip = P.vert((math.cos(a) * L, math.sin(a) * L, r * rng.uniform(0.75, 1.5)), (0.93, 0.80, 0.80), 0.6)
        P.face([b0, b1, tip], out=(0, 0, 1))
    return P


def anemones(seed):
    rng = np.random.default_rng(seed)
    P = Part()
    anemone_closed(P, 0.0, 0.0, 0.062, rng)
    anemone_closed(P, 0.105, 0.03, 0.044, rng)
    return P


# ====================================================================================== urchin
def urchin(seed):
    rng = np.random.default_rng(seed)
    P = Part(); n = 6
    body = (0.20, 0.075, 0.27)
    rings = []
    for rr, z, cm in ((0.92, -0.01, 0.6), (1.0, 0.36, 1.0), (0.55, 0.70, 1.15)):
        rings.append([P.vert((math.cos(i * TAU / n) * rr, math.sin(i * TAU / n) * rr, z), mul3(body, cm), 0.35) for i in range(n)])
    top = P.vert((0, 0, 0.78), mul3(body, 1.2), 0.35)
    c = (0, 0, 0.2)
    P.strip(rings[0], rings[1], frm=c); P.strip(rings[1], rings[2], frm=c); P.fan(rings[2], top, out=(0, 0, 1))
    m = 19
    for i in range(m):
        el = math.radians(lerp(4, 82, ((i + 0.5) / m) ** 0.9))
        az = i * 2.39996 + rng.uniform(-0.25, 0.25)
        d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
        o = Vector((d.x * 0.88, d.y * 0.88, 0.12 + d.z * 0.62))
        t = d.orthogonal().normalized(); bt = d.cross(t)
        L = rng.uniform(0.75, 1.25)
        w = 0.085
        b = [P.vert(o + (t * math.cos(j * TAU / 3) + bt * math.sin(j * TAU / 3)) * w, (0.36, 0.17, 0.50), 0.3) for j in range(3)]
        tip = P.vert(o + d * L, (0.86, 0.68, 0.92), 0.3)
        P.fan(b, tip, frm=o)
    return P


# ====================================================================================== starfish
def starfish(seed, curl=0.0, lift=0):
    rng = np.random.default_rng(seed)
    P = Part()
    g = 0.5
    hc = 0.16
    C = P.vert((0, 0, hc * 1.05), (0.96, 0.96, 0.96), g)
    th = [i * TAU / 5 + rng.uniform(-0.10, 0.10) for i in range(5)]
    pits = []
    for i in range(5):
        a = (th[i] + th[(i - 1) % 5]) / 2 if i else (th[0] + th[4] - TAU) / 2
        pits.append(P.vert((math.cos(a) * 0.27, math.sin(a) * 0.27, 0.012), (0.50, 0.50, 0.50), g))
    for i in range(5):
        u = Vector((math.cos(th[i]), math.sin(th[i]), 0)); p = Vector((-u.y, u.x, 0))
        La = rng.uniform(0.88, 1.08)
        bend = rng.uniform(-1, 1) * (0.5 + curl)
        up = 0.16 if (lift and i == 1) else 0.0
        B = P.vert(u * 0.29 + Vector((0, 0, hc)), (1.0, 1.0, 1.0), g)
        st = []
        for s, hw, hz, lat, cm in ((0.60, 0.125, 0.105, 0.06, 0.92), (0.86, 0.072, 0.062, 0.20, 0.84)):
            c = u * (s * La) + p * (lat * bend * La) + Vector((0, 0, up * (s - 0.3)))
            st.append((P.vert(c - p * hw + Vector((0, 0, 0.010)), (0.58, 0.58, 0.58), g),
                       P.vert(c + Vector((0, 0, hz)), (cm, cm, cm), g),
                       P.vert(c + p * hw + Vector((0, 0, 0.010)), (0.58, 0.58, 0.58), g)))
        T = P.vert(u * La + p * (0.34 * bend * La) + Vector((0, 0, 0.018 + up * 0.9)), (0.74, 0.74, 0.74), g)
        pl, pr = pits[i], pits[(i + 1) % 5]
        up3 = (0, 0, 1)
        P.face([C, pl, B], out=up3); P.face([C, B, pr], out=up3)
        P.face([pl, st[0][0], st[0][1], B], out=up3); P.face([B, st[0][1], st[0][2], pr], out=up3)
        P.face([st[0][0], st[1][0], st[1][1], st[0][1]], out=up3); P.face([st[0][1], st[1][1], st[1][2], st[0][2]], out=up3)
        P.face([st[1][0], T, st[1][1]], out=up3); P.face([st[1][1], T, st[1][2]], out=up3)
    return P


# ====================================================================================== shells
def scallop(seed):
    rng = np.random.default_rng(seed)
    P = Part(); m = 7
    g = 0.38
    rim, mid = [], []
    for j in range(2 * m + 1):
        a = math.radians(18 + j * (144 / (2 * m)))
        ridge = j % 2 == 1
        rr = 1.0 if ridge else 0.93
        edge = 1.0 - 0.10 * abs(j - m) / m            # the fan is a little shorter toward the ears
        rim.append(P.vert((math.cos(a) * rr * edge, math.sin(a) * rr * edge, 0.075 if ridge else 0.022), ((1.0, 1.0, 1.0) if ridge else (0.74, 0.74, 0.74)), g))
        mid.append(P.vert((math.cos(a) * 0.55 * edge, math.sin(a) * 0.55 * edge, 0.205 if ridge else 0.165), ((0.80, 0.80, 0.80) if ridge else (0.60, 0.60, 0.60)), g))
    A = P.vert((0, 0.03, 0.10), (0.97, 0.97, 0.97), g)
    E1 = P.vert((-0.34, 0.0, 0.012), (0.9, 0.9, 0.9), g); E2 = P.vert((0.34, 0.0, 0.012), (0.9, 0.9, 0.9), g)
    Bk = P.vert((0, -0.07, 0.012), (0.85, 0.85, 0.85), g)
    up = (0, 0, 1)
    P.fan(mid, A, closed=False, out=up)
    P.strip(mid, rim, closed=False, out=up)
    P.face([A, mid[0], E2], out=up); P.face([A, E1, mid[-1]], out=up); P.face([A, E2, Bk], out=up); P.face([A, Bk, E1], out=up)
    return P


def whelk(seed):
    """A turret shell lying on its side: whorls stepping down to the point, banded cream and brown."""
    rng = np.random.default_rng(seed)
    P = Part(); n = 6
    cream = (0.90, 0.83, 0.68); brown = (0.56, 0.34, 0.18)
    prof = [(0.00, 0.20, 1), (0.08, 0.33, 0), (0.28, 0.335, 0), (0.37, 0.235, 1), (0.54, 0.235, 0), (0.62, 0.14, 1), (0.80, 0.125, 0)]
    rings = []
    for x, R, dark in prof:
        ring = []
        for i in range(n):
            a = i * TAU / n + x * 0.9
            rr = R * (1 + 0.05 * math.sin(a * 2 + x * 7))
            col = mul3(brown if dark else cream, rng.uniform(0.9, 1.08))
            ring.append(P.vert((x, math.cos(a) * rr, math.sin(a) * rr), col, 0.45))
        rings.append(ring)
    tip = P.vert((1.0, 0, 0), mul3(cream, 0.92), 0.45)
    mouth = P.vert((0.10, 0.02, -0.03), (0.30, 0.15, 0.10), 0.6)
    for k in range(len(rings) - 1): P.strip(rings[k], rings[k + 1], frm=(0.45, 0, 0))
    P.fan(rings[-1], tip, frm=(0.45, 0, 0))
    P.fan(rings[0], mouth, out=(-1, 0, 0))
    # lie it down: the body whorl and the tip of the spire both touch the ground
    M = Matrix.Translation((-0.45, 0, 0.325)) @ Matrix.Rotation(math.radians(16), 4, "Y")
    Q = Part(); Q.add(P, M)
    return Q


def cockle(seed):
    rng = np.random.default_rng(seed)
    P = Part(); n = 10; g = 0.32
    rim = [P.vert((math.cos(i * TAU / n), math.sin(i * TAU / n) * 0.88, -0.004), ((1.0, 1.0, 1.0) if i % 2 else (0.70, 0.70, 0.70)), g) for i in range(n)]
    mid = [P.vert((math.cos(i * TAU / n) * 0.62, math.sin(i * TAU / n) * 0.55 - 0.08, 0.30), ((0.90, 0.90, 0.90) if i % 2 else (0.66, 0.66, 0.66)), g) for i in range(n)]
    top = P.vert((0, -0.26, 0.42), (0.97, 0.97, 0.97), g)
    c = (0, 0, -0.2)
    P.strip(rim, mid, frm=c); P.fan(mid, top, frm=c)
    return P


# ====================================================================================== stones
PEBBLE = [(0.42, 0.40, 0.38), (0.36, 0.35, 0.34), (0.50, 0.45, 0.38), (0.48, 0.37, 0.30), (0.56, 0.54, 0.50), (0.40, 0.39, 0.36)]


def stone(P, x, y, rx, ry, rz, yaw, col, rng, sink=0.3):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    for v in bm.verts:
        k = 1.0 + 0.10 * noise.noise(v.co * 1.7 + Vector((x * 9.1, y * 7.3, rx * 31)))
        v.co = Vector((v.co.x * rx * k, v.co.y * ry * k, v.co.z * rz * k))
    M = Matrix.Translation((x, y, rz * (1 - sink))) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(rng.uniform(-0.25, 0.25), 4, "X")
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts[:])
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(v.co.z < 0.0 for v in f.verts)], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.normal_update()
    tone = rng.uniform(0.85, 1.1)
    q = from_bmesh(bm, lambda co, n: mul3(col, tone * (0.86 + 0.20 * clamp01(n.z * 0.5 + 0.5)) * (1 + 0.08 * noise.noise(co * 14))), 0.16)
    bm.free()
    P.add(q)


def cobbles(seed, k, spread, r0, r1):
    rng = np.random.default_rng(seed)
    P = Part(); pts = []
    for i in range(k):
        r = lerp(r1, r0, i / max(k - 1, 1)) * rng.uniform(0.9, 1.1)
        for _ in range(300):
            a, d = rng.uniform(0, TAU), spread * math.sqrt(rng.random())
            x, y = math.cos(a) * d, math.sin(a) * d
            if all(math.hypot(x - px, y - py) > (r + pr) * 0.9 for px, py, pr in pts): break
        pts.append((x, y, r))
        stone(P, x, y, r, r * rng.uniform(0.66, 0.9), r * rng.uniform(0.42, 0.62), rng.uniform(0, TAU), PEBBLE[int(rng.integers(len(PEBBLE)))], rng)
    return P


def rock(seed, npts, sx, sy, sz, bevel, cut, box=False, spike=0.0):
    """A boulder: the hull of a handful of points, edges chamfered, the underside cut away."""
    rng = np.random.default_rng(seed)
    bm = bmesh.new()
    if box:
        for ix in (-1, 1):
            for iy in (-1, 1):
                for iz in (-1, 1):
                    bm.verts.new((ix * sx * rng.uniform(0.52, 1.0) + rng.uniform(-0.12, 0.12), iy * sy * rng.uniform(0.52, 1.0) + rng.uniform(-0.12, 0.12), iz * sz * rng.uniform(0.6, 1.0)))
        for _ in range(npts - 8):
            d = Vector((rng.normal(), rng.normal(), rng.normal())).normalized()
            bm.verts.new((d.x * sx * 0.98, d.y * sy * 0.98, d.z * sz * 0.98))
    else:
        for i in range(npts):
            u = (i + 0.5) / npts
            el = math.asin(1 - 2 * u); az = i * 2.39996 + rng.uniform(-0.5, 0.5)
            d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
            k = rng.uniform(0.70, 1.0) * (1.0 + spike * max(d.z, 0) ** 3)
            bm.verts.new((d.x * sx * k, d.y * sy * k, d.z * sz * k))
    r = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    junk = list({e for e in r["geom_interior"] + r["geom_unused"] if isinstance(e, bmesh.types.BMVert)})
    if junk: bmesh.ops.delete(bm, geom=junk, context="VERTS")
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, offset_type="OFFSET", segments=1, profile=0.5, affect="EDGES", clamp_overlap=True)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, cut), plane_no=(0, 0, -1), clear_outer=True)
    bmesh.ops.translate(bm, vec=(0, 0, -cut - 0.10), verts=bm.verts[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.dissolve_degenerate(bm, dist=0.012, edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    base = (0.505, 0.51, 0.52)
    def col(co, n):
        k = 0.90 + 0.16 * noise.noise(co * 1.3 + Vector((seed, 0, 0))) + 0.08 * noise.noise(co * 4.1)
        k *= 0.90 + 0.14 * clamp01(n.z)
        warm = clamp01(0.5 + 0.9 * noise.noise(co * 0.9 + Vector((0, seed * 3.1, 0))))
        return mul3(lerp3(base, (0.54, 0.50, 0.45), warm * 0.6), k)
    P = from_bmesh(bm, col, 0.14, ROCK)
    # attachment points for barnacles and weed: spots on the faces, with the way they look
    anchors = []
    tris = [f for f in bm.faces]
    areas = np.array([f.calc_area() for f in tris]); areas /= areas.sum()
    for i in rng.choice(len(tris), size=34, p=areas):
        f = tris[int(i)]
        a, b = rng.random(), rng.random()
        if a + b > 1: a, b = 1 - a, 1 - b
        v = f.verts
        c = v[0].co * (1 - a - b) + v[1].co * a + v[2].co * b
        if c.z < 0.04: continue
        n = f.normal
        anchors.append([round(c.x, 4), round(c.z, 4), round(-c.y, 4), round(n.x, 3), round(n.z, 3), round(-n.y, 3)])
    bm.free()
    return P, anchors


# ====================================================================================== driftwood
def tube(P, pts, radii, n, col_fn, cap0=None, cap1=None, lumps=0.0, rng=None, gloss=0.12, twist=0.0, kind=WOOD):
    """Rings swept along a polyline. col_fn(station 0..1, side index, around 0..1) -> colour.
    Each vertex remembers how far round the trunk it is (t), which is what the grain follows."""
    rings = []
    m = len(pts)
    up0 = Vector((0, 0, 1))
    for k in range(m):
        a = Vector(pts[max(k - 1, 0)]); b = Vector(pts[min(k + 1, m - 1)])
        tg = (b - a).normalized()
        e1 = tg.cross(up0)
        if e1.length < 1e-3: e1 = tg.cross(Vector((0, 1, 0)))
        e1.normalize(); e2 = e1.cross(tg)
        ring = []
        for i in range(n):
            ang = i * TAU / n + twist * k
            rr = radii[k] * (1 + (lumps * rng.uniform(-1, 1) if lumps else 0))
            ring.append(P.vert(Vector(pts[k]) + (e1 * math.cos(ang) + e2 * math.sin(ang)) * rr, col_fn(k / (m - 1), i, i / n), gloss, kind, i / n))
        rings.append(ring)
    axis = lambda k: Vector(pts[k])
    for k in range(m - 1): P.strip(rings[k], rings[k + 1], frm=(axis(k) + axis(k + 1)) / 2)
    for cap, k, sgn in ((cap0, 0, -1), (cap1, m - 1, 1)):
        if cap is None: continue
        tg = (Vector(pts[min(k + 1, m - 1)]) - Vector(pts[max(k - 1, 0)])).normalized() * sgn
        c = P.vert(Vector(pts[k]) + tg * cap[0], cap[1], gloss, kind, 0.5)
        P.fan(rings[k], c, out=tg)
    return rings


WOODC = (0.84, 0.80, 0.72)


def wood_col(rng, n):
    tones = [rng.uniform(0.78, 1.06) for _ in range(n)]
    dark = int(rng.integers(n))
    def f(s, i, a):
        k = tones[i] * (0.66 if i == dark else 1.0) * (0.92 + 0.12 * math.sin(s * 9.0 + i))
        under = 0.80 + 0.20 * clamp01(math.sin(a * TAU) * 0.8 + 0.6)
        return mul3(WOODC, k * under)
    return f


def log(seed, L=3.0, r0=0.135, r1=0.08, nseg=6, n=7, stubs=2):
    rng = np.random.default_rng(seed)
    P = Part()
    bend = rng.uniform(-1, 1)
    pts, rad = [], []
    for k in range(nseg + 1):
        s = k / nseg
        x = (s - 0.5) * L
        r = lerp(r0, r1, s) * (1.32 if k == 0 else 1.0)
        pts.append((x, bend * 0.16 * (1 - (2 * s - 1) ** 2) * L * 0.25, r * 0.74 + 0.02 * math.sin(s * 7 + seed)))
        rad.append(r)
    end = mul3(WOODC, 0.60)
    tube(P, pts, rad, n, wood_col(rng, n), cap0=(-0.03, mul3(WOODC, 0.42)), cap1=(0.02, end), lumps=0.035, rng=rng)
    for j in range(stubs):
        s = rng.uniform(0.25, 0.8)
        k = s * nseg; k0 = int(k); f = k - k0
        c = Vector(pts[k0]).lerp(Vector(pts[min(k0 + 1, nseg)]), f)
        r = lerp(rad[k0], rad[min(k0 + 1, nseg)], f)
        a = rng.uniform(0.5, 2.6)                      # around the trunk, in the upper half
        d = Vector((rng.uniform(-0.5, 0.5), math.cos(a), math.sin(a))).normalized()
        Ls = rng.uniform(0.16, 0.34)
        tube(P, [c + d * r * 0.5, c + d * (r + Ls * 0.6), c + d * (r + Ls)], [r * 0.42, r * 0.33, r * 0.25], 5, wood_col(rng, 5), cap1=(0.012, mul3(WOODC, 0.5)))
    return P


def branch(seed):
    rng = np.random.default_rng(seed)
    P = Part()
    main = [(-0.8, 0.0, 0.035), (-0.3, 0.06, 0.05), (0.2, -0.04, 0.085), (0.75, 0.05, 0.20)]
    tube(P, main, [0.052, 0.045, 0.036, 0.020], 5, wood_col(rng, 5), cap0=(-0.02, mul3(WOODC, 0.5)), cap1=(0.05, mul3(WOODC, 0.9)), lumps=0.04, rng=rng)
    tube(P, [main[2], (0.50, 0.30, 0.10), (0.70, 0.52, 0.17)], [0.030, 0.024, 0.012], 5, wood_col(rng, 5), cap1=(0.04, mul3(WOODC, 0.9)))
    tube(P, [main[1], (-0.12, -0.26, 0.045), (0.02, -0.46, 0.03)], [0.034, 0.026, 0.013], 5, wood_col(rng, 5), cap1=(0.04, mul3(WOODC, 0.9)))
    return P


def stick(seed):
    rng = np.random.default_rng(seed)
    P = Part()
    tube(P, [(-0.3, 0.0, 0.014), (0.02, 0.035, 0.02), (0.3, -0.01, 0.016)], [0.019, 0.017, 0.011], 4, wood_col(rng, 4), cap0=(-0.01, mul3(WOODC, 0.5)), cap1=(0.02, mul3(WOODC, 0.8)))
    return P


# ====================================================================================== weeds
def ribbon(P, centre, widths, cols, gloss, kind=PLAIN, ts=None, ph=0.0, bank=None, ruffle=0.0):
    """A flat strap along a polyline, lying face up."""
    m = len(centre)
    L, R = [], []
    for k in range(m):
        a = Vector(centre[max(k - 1, 0)]); b = Vector(centre[min(k + 1, m - 1)])
        tg = (b - a); tg.z = 0
        tg = tg.normalized() if tg.length > 1e-6 else Vector((1, 0, 0))
        p = Vector((-tg.y, tg.x, 0))
        bz = (bank[k] if bank else 0.0) * widths[k]
        rz = ruffle * math.sin(k * 2.4 + ph * 9.0)
        t = ts[k] if ts else 0.0
        L.append(P.vert(Vector(centre[k]) + p * widths[k] + Vector((0, 0, bz + rz)), cols[k], gloss, kind, t, ph))
        R.append(P.vert(Vector(centre[k]) - p * widths[k] + Vector((0, 0, -bz - rz)), mul3(cols[k], 0.9), gloss, kind, t, ph))
    for k in range(m - 1): P.face([L[k], R[k], R[k + 1], L[k + 1]], out=(0, 0, 1))
    return L, R


def wrack(seed, nrib, stipe=False):
    rng = np.random.default_rng(seed)
    P = Part()
    dry = [(0.26, 0.20, 0.13), (0.20, 0.17, 0.11), (0.30, 0.23, 0.13), (0.30, 0.18, 0.14), (0.46, 0.41, 0.27)]
    for i in range(nrib):
        col = dry[int(rng.integers(len(dry)))] if i else dry[0]
        x, y = rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2)
        a = rng.uniform(0, TAU)
        pts, wid, cols, bank = [], [], [], []
        for k in range(5):
            pile = math.exp(-(x * x + y * y) / 0.06)
            pts.append((x, y, 0.012 + 0.07 * pile * rng.uniform(0.3, 1.0)))
            wid.append(rng.uniform(0.028, 0.055) * (0.6 if k in (0, 4) else 1.0))
            cols.append(mul3(col, rng.uniform(0.7, 1.25)))
            bank.append(rng.uniform(-0.5, 0.5))
            x += math.cos(a) * 0.14; y += math.sin(a) * 0.14
            a += rng.uniform(-1.0, 1.0)
            if math.hypot(x, y) > 0.42: a = math.atan2(-y, -x) + rng.uniform(-0.5, 0.5)
        ribbon(P, pts, wid, cols, 0.10, bank=bank)
    for i in range(2):       # air bladders
        x, y = rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25)
        r = rng.uniform(0.018, 0.03)
        ring = [P.vert((x + math.cos(j * TAU / 4) * r, y + math.sin(j * TAU / 4) * r, 0.02), (0.30, 0.25, 0.12), 0.3) for j in range(4)]
        P.fan(ring, P.vert((x, y, 0.02 + r * 1.2), (0.46, 0.40, 0.20), 0.3), out=(0, 0, 1))
    if stipe:                # a bull-kelp whip thrown up the beach
        pts, wid, cols = [], [], []
        a = rng.uniform(0, TAU); x, y = -math.cos(a) * 0.5, -math.sin(a) * 0.5
        for k in range(6):
            pts.append((x, y, 0.014)); wid.append(lerp(0.012, 0.022, k / 5)); cols.append(mul3((0.34, 0.27, 0.14), rng.uniform(0.8, 1.2)))
            x += math.cos(a) * 0.21; y += math.sin(a) * 0.21; a += rng.uniform(-0.5, 0.5)
        ribbon(P, pts, wid, cols, 0.2)
        r = 0.05
        ring = [P.vert((x + math.cos(j * TAU / 5) * r, y + math.sin(j * TAU / 5) * r, 0.03), (0.38, 0.31, 0.15), 0.4) for j in range(5)]
        P.fan(ring, P.vert((x, y, 0.03 + r * 1.3), (0.52, 0.44, 0.22), 0.4), out=(0, 0, 1))
        base = [P.vert((x + math.cos(j * TAU / 5) * r * 0.6, y + math.sin(j * TAU / 5) * r * 0.6, 0.0), (0.26, 0.21, 0.10), 0.4) for j in range(5)]
        P.strip(base, ring, frm=(x, y, 0.02))
    return P


def kelp(seed, nfr, nseg, spread=0.62, len0=2.3, len1=4.2):
    """Fronds streaming from a holdfast along +x. They are modelled flat: the game floats every
    vertex on the swell."""
    rng = np.random.default_rng(seed)
    P = Part()
    base = (0.42, 0.30, 0.10); midc = (0.66, 0.52, 0.16); tipc = (0.80, 0.68, 0.26)
    for i in range(nfr):
        a = lerp(-spread, spread, (i + 0.5) / nfr) + rng.uniform(-0.12, 0.12)
        L = rng.uniform(len0, len1)
        wmax = rng.uniform(0.12, 0.19)
        amp, c, ph = rng.uniform(0.10, 0.26), rng.uniform(0.9, 1.7), rng.uniform(0, TAU)
        tone = rng.uniform(0.8, 1.15)
        u = Vector((math.cos(a), math.sin(a), 0)); p = Vector((-u.y, u.x, 0))
        pts, wid, cols, ts = [], [], [], []
        for k in range(nseg + 1):
            t = k / nseg
            lat = amp * math.sin(math.pi * t * c + ph) * t * L * 0.3
            pts.append(u * (t * L) + p * lat)
            wid.append(max(wmax * (smooth(0, 0.3, t) ** 0.7) * (1 - 0.86 * smooth(0.72, 1.0, t)), 0.014))
            cols.append(mul3(lerp3(lerp3(base, midc, smooth(0.0, 0.4, t)), tipc, smooth(0.5, 1.0, t)), tone))
            ts.append(t)
        ribbon(P, pts, wid, cols, 0.8, KELP, ts, rng.random(), ruffle=0.022)
    return P


def rockweed(seed, nfr, arc=TAU, len0=0.24, len1=0.40):
    """A tuft of broad forked straps, long ones lying out over short ones. arc < tau hangs them
    all to one side (-y), for walls."""
    rng = np.random.default_rng(seed)
    P = Part()
    base = (0.25, 0.23, 0.09); midc = (0.36, 0.33, 0.11); tipc = (0.56, 0.49, 0.17)
    for i in range(nfr):
        inner = i % 2 == 1
        a = (i + rng.uniform(0.15, 0.85)) / nfr * arc + (-math.pi / 2 - arc / 2 if arc < TAU else 0)
        L = rng.uniform(len0, len1) * (0.60 if inner else 1.0)
        lift = 0.030 if inner else 0.0
        u = Vector((math.cos(a), math.sin(a), 0)); p = Vector((-u.y, u.x, 0))
        ph = rng.random(); tone = rng.uniform(0.82, 1.15) * (1.12 if inner else 1.0)
        w0, w1 = rng.uniform(0.030, 0.040), rng.uniform(0.052, 0.072)
        st = []
        for t, w, z in ((0.0, w0, 0.045), (0.36, (w0 + w1) / 2, 0.062 + lift), (0.66, w1, 0.030 + lift)):
            c = u * (0.015 + t * L) + Vector((0, 0, z))
            col = mul3(lerp3(base, midc, t / 0.66), tone)
            st.append((P.vert(c + p * w, col, 0.62, WEED, t, ph), P.vert(c - p * w, mul3(col, 0.9), 0.62, WEED, t, ph), c))
        up = (0, 0, 1)
        P.face([st[0][0], st[0][1], st[1][1], st[1][0]], out=up); P.face([st[1][0], st[1][1], st[2][1], st[2][0]], out=up)
        cm = P.vert(st[2][2], mul3(midc, tone), 0.62, WEED, 0.66, ph)
        for sgn, edge in ((1, st[2][0]), (-1, st[2][1])):
            d = (u + p * sgn * rng.uniform(0.34, 0.58)).normalized()
            tip = st[2][2] + d * (L * 0.40) + Vector((0, 0, -0.022 - lift * 0.4))
            q = Vector((-d.y, d.x, 0))
            t0 = P.vert(tip + q * 0.022, mul3(tipc, tone), 0.62, WEED, 1.0, ph)
            t1 = P.vert(tip - q * 0.022, mul3(tipc, tone * 0.92), 0.62, WEED, 1.0, ph)
            P.face([edge, cm, t1, t0] if sgn > 0 else [cm, edge, t1, t0], out=up)
    return P


# ====================================================================================== the crab
def prism(P, a, b, ra, rb, col_a, col_b, piv, leg_a, leg_b, n=3, cap=False, rot=0.0):
    """A tapering strut from a to b (crab limbs). leg_* = (phase, weight, part)."""
    a, b = Vector(a), Vector(b)
    tg = (b - a).normalized()
    side = tg.cross(Vector((0, 0, 1)))
    if side.length < 1e-3: side = Vector((1, 0, 0))
    side.normalize(); upv = side.cross(tg)
    ra_ring, rb_ring = [], []
    for i in range(n):
        ang = math.pi / 2 + i * TAU / n + rot
        d = side * math.cos(ang) + upv * math.sin(ang)
        ra_ring.append(P.vert(a + d * ra, col_a, 0.55, PLAIN, piv=piv, leg=leg_a))
        if rb > 0: rb_ring.append(P.vert(b + d * rb, col_b, 0.55, PLAIN, piv=piv, leg=leg_b))
    if rb > 0:
        P.strip(ra_ring, rb_ring, frm=(a + b) / 2)
        if cap: P.fan(rb_ring, P.vert(b + tg * rb * 0.6, col_b, 0.55, PLAIN, piv=piv, leg=leg_b), out=tg)
    else:
        P.fan(ra_ring, P.vert(b, col_b, 0.55, PLAIN, piv=piv, leg=leg_b), frm=a)
    return ra_ring, rb_ring


SHELL, CREAM, DARK = (1, 0, 0), (0, 1, 0), (0, 0, 1)
def mix_m(s, c, d): return (s, c, d)       # crab paint is three masks: shell colour, cream, dark


def crab(lod=0):
    rng = np.random.default_rng(11)
    P = Part()
    FWD = -1.0                                  # the crab looks down -Y here, which is +z in the game
    # ---- carapace (top view, x right, y back)
    out = [(-0.30, -0.34), (-0.11, -0.365), (0.11, -0.365), (0.30, -0.34), (0.52, -0.215), (0.46, 0.06), (0.33, 0.28), (0.12, 0.35), (-0.12, 0.35), (-0.33, 0.28), (-0.46, 0.06), (-0.52, -0.215)]
    if lod: out = [out[i] for i in (0, 3, 4, 5, 6, 7, 8, 9, 10, 11)]
    bl = (0, 0, BODY)
    rim = [P.vert((x, y, 0.245 + (0.012 if abs(x) > 0.5 else 0)), mix_m(0.92 + rng.uniform(-0.05, 0.05), 0.16, 0.0), 0.55, leg=bl) for x, y in out]
    if lod == 0:
        upper = [P.vert((x * 0.66, y * 0.66 + 0.01, 0.345), mix_m(0.98 + rng.uniform(-0.08, 0.04), 0.0, 0.03), 0.6, leg=bl) for x, y in out]
        top = P.vert((0, 0.02, 0.372), mix_m(0.80, 0.0, 0.16), 0.6, leg=bl)
        P.strip(rim, upper, frm=(0, 0, 0.2)); P.fan(upper, top, out=(0, 0, 1))
    else:
        top = P.vert((0, 0.02, 0.37), mix_m(0.90, 0.0, 0.08), 0.6, leg=bl)
        P.fan(rim, top, out=(0, 0, 1))
    belly = P.vert((0, 0.02, 0.105), mix_m(0.25, 0.75, 0.0), 0.3, leg=bl)
    P.fan(rim, belly, out=(0, 0, -1))

    # ---- eyes on stalks
    for s in (-1, 1):
        b0 = (s * 0.165, -0.335, 0.30); b1 = (s * 0.205, -0.375, 0.50)
        el = (0, 0, EYE)
        if lod == 0:
            prism(P, b0, b1, 0.024, 0.02, mix_m(0.85, 0.15, 0), mix_m(0.5, 0.3, 0.1), b0, el, el)
            c = Vector(b1) + Vector((0, 0, 0.03))
            r = 0.05
            ring = [P.vert(c + Vector((math.cos(i * TAU / 4) * r, math.sin(i * TAU / 4) * r, 0)), mix_m(0, 0.0, 1.0), 0.95, piv=b0, leg=el) for i in range(4)]
            P.fan(ring, P.vert(c + Vector((0, 0, r * 1.1)), mix_m(0, 0.12, 0.9), 0.95, piv=b0, leg=el), out=(0, 0, 1))
            P.fan(ring, P.vert(c + Vector((0, 0, -r * 0.8)), mix_m(0, 0, 1), 0.95, piv=b0, leg=el), out=(0, 0, -1))
        else:
            prism(P, b0, (b1[0], b1[1], b1[2] + 0.07), 0.04, 0.0, mix_m(0.5, 0.2, 0.2), mix_m(0, 0, 1), b0, el, el)

    # ---- claws: the right one is the big one
    def claw(s, k, part):
        S = Vector((s * 0.36, -0.30, 0.20))
        def at(x, y, z): return S + Vector(((x - 0.36) * s * k, (y + 0.30) * k, (z - 0.20) * k))
        E = at(0.60, -0.50, 0.25); M = at(0.50, -0.66, 0.245); W = at(0.37, -0.79, 0.23)
        F1 = at(0.17, -0.93, 0.155); F2 = at(0.16, -0.95, 0.305)
        cl = (0, 0, part)
        shell, palm, cream = mix_m(0.95, 0.05, 0), mix_m(0.84, 0.22, 0), mix_m(0.08, 0.92, 0)
        if lod:
            a = [P.vert(S + Vector((0, 0, dz)), shell, 0.55, piv=S, leg=cl) for dz in (0.05 * k, -0.05 * k)]
            m = [P.vert(M + Vector((0, 0, dz)), palm, 0.55, piv=S, leg=cl) for dz in (0.10 * k, -0.08 * k)]
            m2 = P.vert(M + Vector((s * 0.09 * k, -0.02 * k, 0)), palm, 0.55, piv=S, leg=cl)
            tip = P.vert((F1 + F2) / 2, cream, 0.6, piv=S, leg=cl)
            P.face([a[0], a[1], m[1], m[0]], frm=M + Vector((-s * 0.2, 0, 0))); P.face([a[0], m[0], m2], out=(0, 0, 1)); P.face([a[1], m2, m[1]], out=(0, 0, -1)); P.face([a[0], m2, a[1]], frm=M + Vector((-s * 0.2, 0, 0)))
            P.face([m[0], m[1], tip], frm=M + Vector((s * 0.2, 0, 0))); P.face([m[0], tip, m2], out=(0, 0, 1)); P.face([m[1], m2, tip], out=(0, 0, -1))
            return
        prism(P, S, E, 0.052 * k, 0.060 * k, shell, shell, S, cl, cl)
        # palm: a flattened bulb from the elbow to the wrist
        ax = (W - E).normalized(); sd = ax.cross(Vector((0, 0, 1))).normalized()
        def ring(c, hv, hs, col):
            return [P.vert(c + Vector((0, 0, hv)), col, 0.6, piv=S, leg=cl), P.vert(c + sd * hs, col, 0.6, piv=S, leg=cl),
                    P.vert(c + Vector((0, 0, -hv * 0.8)), mix_m(0.6, 0.45, 0), 0.6, piv=S, leg=cl), P.vert(c - sd * hs, col, 0.6, piv=S, leg=cl)]
        r0 = ring(E, 0.070 * k, 0.055 * k, shell); r1 = ring(M, 0.118 * k, 0.078 * k, palm); r2 = ring(W, 0.088 * k, 0.058 * k, palm)
        P.strip(r0, r1, frm=(E + M) / 2); P.strip(r1, r2, frm=(M + W) / 2)
        back = P.vert(E - ax * 0.03 * k, shell, 0.6, piv=S, leg=cl)
        P.fan(r0, back, out=-ax)
        # fingers: the fixed one below, the dactyl above, a gap between them
        mid = P.vert(W + ax * 0.02 * k, mix_m(0.3, 0.3, 0.35), 0.6, piv=S, leg=cl)
        tip1 = P.vert(F1, cream, 0.7, piv=S, leg=cl); tip2 = P.vert(F2, cream, 0.7, piv=S, leg=cl)
        P.face([r2[1], r2[2], tip1], frm=W); P.face([r2[2], r2[3], tip1], frm=W); P.face([r2[3], mid, tip1], out=(0, 0, 1)); P.face([mid, r2[1], tip1], out=(0, 0, 1))
        P.face([r2[0], r2[1], tip2], frm=W); P.face([r2[3], r2[0], tip2], frm=W); P.face([r2[1], mid, tip2], out=(0, 0, -1)); P.face([mid, r2[3], tip2], out=(0, 0, -1))
    claw(1, 1.32, CLAW_R)
    claw(-1, 0.84, CLAW_L)

    # ---- eight walking legs
    ys = [-0.14, 0.02, 0.17, 0.29]
    betas = [math.radians(b) for b in (-34, -11, 15, 40)]
    for s in (-1, 1):
        for i in range(4):
            ph = ((i % 2) * 0.5 + (0.0 if s < 0 else 0.5) + rng.uniform(-0.05, 0.05)) % 1.0
            H = Vector((s * 0.40, ys[i], 0.205))
            d = Vector((s * math.cos(betas[i]), math.sin(betas[i]), 0))
            k = 1.0 if i < 3 else 0.9
            K = H + d * 0.30 * k + Vector((0, 0, 0.215)); A = H + d * 0.64 * k + Vector((0, 0, -0.045)); T = H + d * 0.83 * k + Vector((0, 0, -0.205))
            shell, joint, dark = mix_m(0.92, 0.06, 0.0), mix_m(0.62, 0.10, 0.22), mix_m(0.10, 0.05, 0.80)
            if lod:
                # two flat blades, edge up
                w = Vector((-d.y, d.x, 0)) * 0.034
                v = [P.vert(p + q, c, 0.5, piv=H, leg=(ph, wt, LEG)) for p, c, wt in ((H, shell, 0.0), (K, shell, 0.3), (A, joint, 0.8)) for q in (w, -w)]
                tip = P.vert(T, dark, 0.5, piv=H, leg=(ph, 1.0, LEG))
                P.face([v[0], v[1], v[3], v[2]], out=(0, 0, 1)); P.face([v[2], v[3], v[5], v[4]], out=(0, 0, 1)); P.face([v[4], v[5], tip], out=(0, 0, 1))
                continue
            prism(P, H, K, 0.050, 0.043, shell, shell, H, (ph, 0.0, LEG), (ph, 0.3, LEG))
            prism(P, K, A, 0.043, 0.030, shell, joint, H, (ph, 0.3, LEG), (ph, 0.8, LEG))
            prism(P, A, T, 0.030, 0.0, joint, dark, H, (ph, 0.8, LEG), (ph, 1.0, LEG))

    # ---- a soft blob of shade on the ground under it (weight = opacity)
    n = 8 if lod == 0 else 6
    sl = lambda w: (0, w, SHADOW)
    c = P.vert((0, 0, 0.008), (0, 0, 0), 0, leg=sl(1.0))
    ring = [P.vert((math.cos(i * TAU / n) * 1.02, math.sin(i * TAU / n) * 0.80, 0.008), (0, 0, 0), 0, leg=sl(0.0)) for i in range(n)]
    P.fan(ring, c, out=(0, 0, 1))
    return P


# ====================================================================================== build
print("building shore kit")
finalize(barnacle_cluster(1, 7, 0.15, 0.060, 0.028), "barnacles_a", 80)
finalize(barnacle_cluster(2, 5, 0.12, 0.056, 0.030), "barnacles_b", 80)
finalize(barnacle_cluster(3, 3, 0.07, 0.050, 0.032), "barnacles_c", 80)
finalize(mussel_bed(4, 10, 0.15, 0.10), "mussels_a", 72, ao_k=0.9)
finalize(mussel_bed(5, 6, 0.11, 0.08), "mussels_b", 72, ao_k=0.9)
finalize(limpets(6, 3), "limpets", 35)
finalize(anemones(7), "anemones", 70)
finalize(anemone_open(8), "anemone_open", 60)
finalize(urchin(9), "urchin", 80, meta={"unit": True})
finalize(starfish(10), "starfish_a", 60, meta={"unit": True})
finalize(starfish(11, curl=0.9, lift=1), "starfish_b", 60, meta={"unit": True})
finalize(scallop(12), "scallop", 50, meta={"unit": True})
finalize(whelk(13), "whelk", 60, meta={"unit": True})
finalize(cockle(14), "cockle", 60, meta={"unit": True})
finalize(cobbles(15, 3, 0.20, 0.08, 0.135), "cobbles_a", 75)
finalize(cobbles(16, 2, 0.20, 0.14, 0.21), "cobbles_b", 75)
ROCKS = [("rock_a", dict(seed=21, npts=17, sx=1.0, sy=0.86, sz=0.78, bevel=0.10, cut=-0.30)),
         ("rock_b", dict(seed=22, npts=15, sx=1.0, sy=0.72, sz=0.46, bevel=0.07, cut=-0.16)),
         ("rock_c", dict(seed=23, npts=15, sx=0.80, sy=0.74, sz=1.05, bevel=0.09, cut=-0.42, spike=0.5)),
         ("rock_d", dict(seed=27, npts=13, sx=0.90, sy=0.72, sz=0.58, bevel=0.10, cut=-0.24, box=True))]
for name, kw in ROCKS:
    P, anchors = rock(**kw)
    finalize(P, name, 44, ao_k=0.8, meta={"unit": True, "anchors": anchors})
    lo = dict(kw); lo["bevel"] = 0.0; lo["npts"] = min(kw["npts"], 12)
    P1, _ = rock(**lo)
    finalize(P1, name + "_far", 32, ao_k=0.8, meta={"unit": True})
finalize(log(31), "log_a", 62, ao_k=0.8)
finalize(log(32, L=2.2, r0=0.10, r1=0.07, stubs=1), "log_b", 62, ao_k=0.8)
finalize(log(31, nseg=3, n=5, stubs=0), "log_a_far", 62, ao_k=0.8)
finalize(log(32, L=2.2, r0=0.10, r1=0.07, nseg=3, n=5, stubs=0), "log_b_far", 62, ao_k=0.8)
finalize(branch(33), "branch", 62, ao_k=0.8)
finalize(stick(34), "stick", 45, ao_k=0.6)
finalize(wrack(35, 5), "wrack_a", 50, ao_k=0.7, ground=0.3)
finalize(wrack(36, 3, stipe=True), "wrack_b", 50, ao_k=0.7, ground=0.3)
finalize(kelp(37, 6, 8), "kelp_a", 60, ao_k=0.0, ground=0)
finalize(kelp(38, 4, 8, spread=0.95, len0=1.8, len1=3.2), "kelp_b", 60, ao_k=0.0, ground=0)
finalize(kelp(37, 3, 4), "kelp_a_far", 60, ao_k=0.0, ground=0)
finalize(kelp(38, 3, 4, spread=0.95, len0=1.8, len1=3.2), "kelp_b_far", 60, ao_k=0.0, ground=0)
finalize(rockweed(39, 12), "rockweed_a", 60, ao_k=0.6, ground=0.35)
finalize(rockweed(40, 8, arc=math.radians(170), len0=0.30, len1=0.50), "rockweed_b", 60, ao_k=0.6, ground=0.35)
finalize(crab(0), "crab", 46, ao_k=0.85, ground=0.6, crab=True)
finalize(crab(1), "crab_far", 46, ao_k=0.85, ground=0.6, crab=True)

# ------------------------------------------------------------------------------------ pack
def q8(a, lo=0.0, hi=1.0): return np.clip(np.round((a - lo) / (hi - lo) * 255), 0, 255).astype(np.uint8)

sections, blob, off = {}, [], 0
def put(name, arr):
    global off
    b = arr.tobytes()
    pad = (-len(b)) % 4
    sections[name] = [off, len(b)]
    blob.append(b + b"\0" * pad)
    off += len(b) + pad

directory = {}
for kind in ("static", "crab"):
    names = [n for n in ORDER if MESHES[n]["crab"] == (kind == "crab")]
    v0 = i0 = 0
    pos, nrm, col, aux, idx, piv, leg = [], [], [], [], [], [], []
    for n in names:
        m = MESHES[n]
        nv, ni = len(m["pos"]), len(m["idx"])
        assert nv < 65536
        directory[n] = {"set": kind, "v0": v0, "nv": nv, "i0": i0, "ni": ni, **m["meta"]}
        pos.append(m["pos"])
        nrm.append(np.concatenate([np.clip(np.round(m["nrm"] * 127), -127, 127), np.round(m["ao"][:, None] * 127)], 1).astype(np.int8))
        col.append(np.concatenate([q8(m["col"]), q8(m["gloss"])[:, None]], 1))
        if kind == "static":
            aux.append(np.stack([m["kind"], q8(m["t"]), q8(m["ph"]), np.zeros(nv, np.uint8)], 1))
        else:
            piv.append(m["piv"])
            aux.append(np.stack([q8(m["leg"][:, 0]), q8(m["leg"][:, 1]), m["leg"][:, 2].astype(np.uint8), np.zeros(nv, np.uint8)], 1))
        idx.append(m["idx"].astype(np.uint16))
        v0 += nv; i0 += ni
    put(kind + ".pos", np.concatenate(pos).astype(np.float32))
    if kind == "crab": put(kind + ".piv", np.concatenate(piv).astype(np.float32))
    put(kind + ".nrm", np.concatenate(nrm))
    put(kind + ".col", np.concatenate(col))
    put(kind + ".aux", np.concatenate(aux))
    put(kind + ".idx", np.concatenate(idx))
    print(f"{kind}: {v0} verts, {i0 // 3} tris in {len(names)} meshes")

with open(os.path.join(OUT, "shore.bin"), "wb") as f:
    for b in blob: f.write(b)
json.dump({"version": 1, "kinds": {"plain": PLAIN, "rock": ROCK, "weed": WEED, "kelp": KELP, "wood": WOOD},
           "parts": {"body": BODY, "leg": LEG, "clawR": CLAW_R, "clawL": CLAW_L, "eye": EYE, "shadow": SHADOW},
           "sections": sections, "meshes": directory}, open(os.path.join(OUT, "shore.json"), "w"), separators=(",", ":"))
print("wrote", os.path.join(OUT, "shore.bin"), off, "bytes;", os.path.getsize(os.path.join(OUT, "shore.json")), "bytes of json")

# ------------------------------------------------------------------------------------ contact sheet
if PREVIEW:
    scene = bpy.context.scene
    try: scene.render.engine = "BLENDER_WORKBENCH"
    except Exception as e: print("workbench unavailable:", e)
    sh = scene.display.shading
    sh.light = "STUDIO"; sh.color_type = "VERTEX"; sh.show_shadows = False; sh.show_cavity = False
    scene.display.render_aa = "8"
    scene.view_settings.view_transform = "Standard"
    cols = 8
    obs = [o for o in scene.objects if o.type == "MESH"]
    cellw = 1.0
    for i, o in enumerate(obs):
        m = MESHES[o.name]["meta"]
        size = max(m["radius"] * 2, m["height"], 0.05)
        s = 0.78 * cellw / size
        o.scale = (s, s, s)
        o.location = ((i % cols) * cellw, -(i // cols) * cellw * 1.0, 0)
    rows = (len(obs) + cols - 1) // cols
    for tag, d in (("", Vector((0.55, -0.9, 0.62))), ("_top", Vector((0.0, -0.02, 1.0)))):
        cam_data = bpy.data.cameras.new("c"); cam_data.type = "ORTHO"; cam_data.ortho_scale = cols * cellw * 1.04
        cam = bpy.data.objects.new("c", cam_data); scene.collection.objects.link(cam); scene.camera = cam
        d = d.normalized()
        ctr = Vector(((cols - 1) * cellw / 2, -(rows - 1) * cellw / 2, 0.1))
        cam.location = ctr + d * 30
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        scene.render.resolution_x = 2000; scene.render.resolution_y = int(2000 * (rows + 0.6) / cols * (1.0 if tag else 0.82))
        if scene.world is None: scene.world = bpy.data.worlds.new("w")
        scene.world.color = (0.33, 0.36, 0.40)
        scene.render.film_transparent = False
        scene.render.filepath = os.path.splitext(PREVIEW)[0] + tag + ".png"
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(cam)
    print("preview", PREVIEW)
