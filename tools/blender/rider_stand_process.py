# Blender: turn the Meshy standing rider into the game asset (the standing sister of rider_process.py).
#  - measures hat and head on the seated asset and scales the standing mesh so they match
#  - turns her to face glTF -Z, puts the floor at y = 0 and the origin between her feet
#  - paints the same per-vertex wind attribute as rider.glb (_WIND rgba = cape, bristles, hat, lantern)
#  - downsizes textures, exports GLB (WebP, tangents) and a JSON sidecar for lining it up in the game
# Usage: blender -b -P rider_stand_process.py -- <in.glb> <out.glb> <debug_dir> [<seated rider.glb>]
#
# Everything is measured on the mesh (colour from the base-colour texture + position), nothing is a
# hand-typed coordinate, so a re-generated mesh goes through the same script. All analysis is done in
# glTF coordinates (x, y up, z); "final" means after scaling and turning, the frame the game sees.
import bpy, sys, os, json, math
import numpy as np
from mathutils import Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
src, dst, dbg = argv[0], argv[1], argv[2]
seated_path = argv[3] if len(argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(dst)), "rider.glb")
os.makedirs(dbg, exist_ok=True)

MAX_BYTES = 8_000_000        # budget for the exported GLB
TEX = 2048                   # like the seated rider: 2K is plenty for a hero seen from a chase camera


# ---------------------------------------------------------------- mesh -> numpy
def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    assert len(meshes) == 1, f"{path}: expected one mesh, found {len(meshes)}"
    obj = meshes[0]
    bpy.context.view_layer.objects.active = obj; obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj


def positions(me):
    co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    return np.stack([co[:, 0], co[:, 2], -co[:, 1]], -1).astype(np.float64)      # Blender (x, y, z up) -> glTF (x, y up, z)


def arrays(obj):
    """Per-vertex position (glTF coords), base colour (sRGB values, as rider_process.py reads them) and triangles."""
    me = obj.data
    nv, nl = len(me.vertices), len(me.loops)
    luv = np.empty(nl * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", luv); luv = luv.reshape(-1, 2)
    lvi = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", lvi)
    vuv = np.zeros((nv, 2), np.float32); vuv[lvi] = luv
    bsdf = [n for n in obj.material_slots[0].material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
    img = bsdf.inputs["Base Color"].links[0].from_node.image
    w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
    ix = np.clip((vuv[:, 0] % 1.0) * w, 0, w - 1).astype(int); iy = np.clip((vuv[:, 1] % 1.0) * h, 0, h - 1).astype(int)
    col = px[iy, ix, :3].astype(np.float64); del px
    me.calc_loop_triangles()
    tri = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get("vertices", tri)
    return positions(me), col, tri.reshape(-1, 3)


# ---------------------------------------------------------------- small numpy toolkit
def ss(a, b, v):
    t = np.clip((v - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def hsv(col):
    mx = col.max(1); mn = col.min(1)
    sat = np.where(mx > 1e-5, (mx - mn) / np.maximum(mx, 1e-5), 0)
    d = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == col[:, 0], ((col[:, 1] - col[:, 2]) / d) % 6,
                   np.where(mx == col[:, 1], (col[:, 2] - col[:, 0]) / d + 2, (col[:, 0] - col[:, 1]) / d + 4)) / 6.0
    return hue, sat, mx


def weld(pos, tri, col, tol=2e-5):
    """Meshy splits vertices along UV seams. Weld by position so that neighbourhoods cross the seams."""
    key = np.round(pos / tol).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    wt = inv[tri]
    e = np.concatenate([wt[:, [0, 1]], wt[:, [1, 2]], wt[:, [2, 0]]])
    e = np.unique(np.sort(e[e[:, 0] != e[:, 1]], 1), axis=0)
    return pos[first], col[first], e, inv


def components(n, e, mask):
    """Connected components of the vertices in mask (label = smallest vertex id, -1 outside)."""
    e = e[mask[e[:, 0]] & mask[e[:, 1]]]
    lab = np.arange(n)
    while True:
        m = np.minimum(lab[e[:, 0]], lab[e[:, 1]])
        new = lab.copy()
        np.minimum.at(new, e[:, 0], m); np.minimum.at(new, e[:, 1], m)
        while True:
            nn = new[new]
            if (nn == new).all(): break
            new = nn
        if (new == lab).all(): break
        lab = new
    lab = lab.copy(); lab[~mask] = -1
    return lab


def comp_list(lab, minsize=1):
    ids, counts = np.unique(lab[lab >= 0], return_counts=True)
    order = np.argsort(-counts)
    return [(int(ids[i]), int(counts[i])) for i in order if counts[i] >= minsize]


def pca(p):
    c = p.mean(0); w, v = np.linalg.eigh(np.cov((p - c).T))
    return c, w[::-1], v[:, ::-1]


def circle_fit(u, v):
    A = np.stack([2 * u, 2 * v, np.ones_like(u)], 1); b = u * u + v * v
    (cx, cy, k), *_ = np.linalg.lstsq(A, b, rcond=None)
    return cx, cy, float(np.sqrt(k + cx * cx + cy * cy))


def nearest_dist(a, b, chunk=128):
    """Distance from every point of a to the nearest point of b (brute force, a few thousand each)."""
    out = np.empty(len(a))
    for i in range(0, len(a), chunk):
        out[i:i + chunk] = np.sqrt(((a[i:i + chunk, None, :] - b[None, :, :]) ** 2).sum(-1).min(1))
    return out


def colour_classes(C):
    """The palette of both riders, loose enough for the texture differences between two generations."""
    h, s, v = hsv(C)
    return dict(
        h=h, s=s, v=v,
        plum=((h > 0.80) | (h < 0.02)) & (s > 0.3) & (v < 0.6),                     # hat, gloves, lantern loop, cord
        cream=(s < 0.27) & (v > 0.7),                                               # hat band, blouse, flowers
        skin=(h > 0.0) & (h < 0.075) & (s > 0.18) & (s < 0.5) & (v > 0.72),
        gold=(h > 0.07) & (h < 0.125) & (s > 0.5) & (v > 0.6),                      # marigold cape and straw
        green=(h > 0.14) & (h < 0.30) & (s > 0.18) & (v > 0.22) & (v < 0.6),        # bedroll
        brown=((h < 0.085) | (h > 0.97)) & (s > 0.45) & (v > 0.15) & (v < 0.62),    # hair, boots, belt, straps
        wood=(h > 0.05) & (h < 0.13) & (s > 0.10) & (s < 0.36) & (v > 0.55),        # broom handle
        brass=(h > 0.08) & (h < 0.12) & (s > 0.3) & (s < 0.5) & (v > 0.35),         # lantern
    )


# ---------------------------------------------------------------- what both riders have in common
def head_hat(P, C, E, say=lambda *a: None):
    """Hat band ring, brim, face and cape of either rider (P: welded vertices)."""
    n = len(P); k = colour_classes(C)
    # hat: the big plum pieces at the top (the cream band splits the crown from the brim)
    lab = components(n, E, k["plum"])
    comps = comp_list(lab, 30)
    cents = {i: P[lab == i].mean(0) for i, c in comps}
    top = max([i for i, c in comps if c > 0.25 * comps[0][1]], key=lambda i: cents[i][1])
    reach = 0.55 * np.ptp(P[lab == top], axis=0).max() + 0.12
    hat = np.isin(lab, [i for i, c in comps if np.linalg.norm(cents[i] - cents[top]) < reach])
    # band: the big cream component that touches the hat
    labc = components(n, E, k["cream"])
    a, b = E[:, 0], E[:, 1]
    t = np.unique(np.concatenate([labc[b[hat[a] & k["cream"][b]]], labc[a[hat[b] & k["cream"][a]]]]))
    band = labc == max(t, key=lambda i: (labc == i).sum())
    B = P[band]
    bc, _, bv = pca(B)
    axis = bv[:, 2] * np.sign(bv[:, 2][1])           # ring normal, pointing up through the crown
    e1 = bv[:, 0]; e2 = np.cross(axis, e1)
    for it in range(4):                                # circle fit in the ring plane, trimming strays (flowers)
        u = (B - bc) @ e1; w = (B - bc) @ e2
        cx, cy, r = circle_fit(u, w)
        res = np.abs(np.hypot(u - cx, w - cy) - r)
        keep = res < max(0.25 * r, 3 * np.median(res))
        if keep.all(): break
        B = B[keep]
    cen = bc + e1 * cx + e2 * cy
    cen = cen + axis * float(np.median((B - cen) @ axis))
    # brim: rim radius about the hat axis, averaged around the hat (the brim is floppy, not round)
    H = P[hat] - cen
    ax = H @ axis
    rad = np.linalg.norm(H - np.outer(ax, axis), axis=1)
    ang = np.arctan2(H @ e2, H @ e1)
    bins = np.floor((ang + np.pi) / (2 * np.pi) * 36).astype(int) % 36
    rim = np.array([rad[bins == i].max() if (bins == i).any() else np.nan for i in range(36)])
    # face: skin in a ball under the band
    hc = cen - axis * 1.1 * r
    ball = np.linalg.norm(P - hc, axis=1) < 2.0 * r
    face = k["skin"] & ball
    fx = P[face][:, 0]
    lat = np.array([1.0, 0, 0]); lat -= axis * (lat @ axis); lat /= np.linalg.norm(lat)
    fwd = np.cross(lat, axis); fwd *= np.sign((P[face].mean(0) - cen) @ fwd)
    q = P[face] - cen
    front = (q @ fwd) > np.percentile(q @ fwd, 99.8) - 0.7 * r
    chin = -float(np.percentile((q @ axis)[front], 0.5))
    # cape: marigold around the shoulders (the straw has the same hue but is far from the head in both poses)
    capec = k["gold"] & (np.linalg.norm(P - hc, axis=1) < 4.6 * r) & (((P - cen) @ axis) < -0.6 * r) & (k["s"] > 0.56) & (k["v"] > 0.62)
    labk = components(n, E, capec)
    kc = comp_list(labk, 20)
    cape = np.isin(labk, [i for i, c in kc if c > 0.04 * kc[0][1]])
    cx_ = P[cape][:, 0]
    out = dict(
        band_radius=r, band_center=cen, hat_axis=axis, face_forward=fwd,
        brim_radius=float(np.nanmean(rim)), brim_radius_max=float(np.nanmax(rim)),
        hat_tip_axial=float(ax.max()), hat_top=P[hat][np.argmax(P[hat][:, 1])],
        face_width=float(np.percentile(fx, 99.5) - np.percentile(fx, 0.5)), face_center=P[face].mean(0),
        chin_below_band=chin, cape_x=(float(np.percentile(cx_, 0.3)), float(np.percentile(cx_, 99.7))),
        masks=dict(hat=hat, band=band, face=face, cape=cape), classes=k,
    )
    say("hat band r %.4f | brim r %.4f | face width %.4f | chin %.4f below the band | cape x %+.3f..%+.3f" % (
        r, out["brim_radius"], out["face_width"], chin, out["cape_x"][0], out["cape_x"][1]))
    return out


def straw_head(P, C, E, cape):
    """The bristle head: the biggest connected piece of straw-coloured surface that is not the cape."""
    k = colour_classes(C)
    lab = components(len(P), E, k["gold"] & ~cape)
    return lab == comp_list(lab, 40)[0][0]


# ================================================================ 1. the seated rider: the size to match
ref_obj = load(seated_path)
rp, rc, rt = arrays(ref_obj)
RP, RC, RE, _ = weld(rp, rt, rc)
print("SEATED", os.path.basename(seated_path), "verts", len(rp), "tris", len(rt))
ref = head_hat(RP, RC, RE, say=lambda *a: print("  seated  :", *a))
def head_size(p):
    """Length and thickness of a bristle head along its own long axis."""
    c, _, v = pca(p)
    t = (p - c) @ v[:, 0]
    return v[:, 0], float(np.ptp(t)), float(2 * np.percentile(np.linalg.norm((p - c) - np.outer(t, v[:, 0]), axis=1), 98))


rb = straw_head(RP, RC, RE, ref["masks"]["cape"])
r_axis, r_bl, r_bd = head_size(RP[rb])
ref_broom = dict(length=float(np.ptp(RP @ r_axis)),      # the seated broom is the longest thing along its own axis
                 bristle_length=r_bl, bristle_diameter=r_bd)
ref_bounds = (RP.min(0), RP.max(0))
print("  seated  : broom %.3f long, bristle head %.3f long x %.3f across | bounds y %.3f..%.3f" % (
    ref_broom["length"], ref_broom["bristle_length"], ref_broom["bristle_diameter"], ref_bounds[0][1], ref_bounds[1][1]))

# ================================================================ 2. the standing mesh, as Meshy made it
obj = load(src)
me = obj.data
pos, col, tri = arrays(obj)
nv = len(pos)
P, C, E, inv = weld(pos, tri, col)
n = len(P)
print("STANDING", os.path.basename(src), "verts", nv, "welded", n, "tris", len(tri))
raw = head_hat(P, C, E, say=lambda *a: print("  raw     :", *a))

# ---- scale: hat and head are what the eye compares between the two models
ratios = {
    "hatBrimRadius": ref["brim_radius"] / raw["brim_radius"],
    "hatBandRadius": ref["band_radius"] / raw["band_radius"],
    "faceWidth": ref["face_width"] / raw["face_width"],
    "bandToChin": ref["chin_below_band"] / raw["chin_below_band"],
}
scale = float(np.mean(list(ratios.values())))
print("  scale ratios (seated / standing raw):", {k_: round(v_, 4) for k_, v_ in ratios.items()}, "-> scale", round(scale, 4))

# ---- boots: the two lowest big brown pieces. Their soles are the floor, their middle is the origin.
k0 = raw["classes"]
labb = components(n, E, k0["brown"])
boots = sorted(comp_list(labb, 100), key=lambda ic: P[labb == ic[0]][:, 1].mean())[:2]
bb = [(P[labb == i].min(0), P[labb == i].max(0)) for i, c in boots]
bcen = np.array([(lo + hi) / 2 for lo, hi in bb])
floor_y = min(lo[1] for lo, hi in bb)
origin = np.array([bcen[:, 0].mean(), floor_y, bcen[:, 2].mean()])
# ---- facing: the face looks along +Z in Meshy's frame; the game wants -Z. Any small yaw of the feet is taken out too.
across = bcen[1] - bcen[0] if bcen[1][0] > bcen[0][0] else bcen[0] - bcen[1]
foot_yaw = math.atan2(across[2], across[0])                # 0 when the feet are side by side along X
fwd = raw["face_forward"]
theta = (math.pi if fwd[2] > 0 else 0.0) + (foot_yaw if abs(foot_yaw) > math.radians(1.5) else 0.0)
print("  floor y %.4f, origin %s, face forward %s, foot yaw %.2f deg -> turn %.1f deg" % (
    floor_y, origin.round(4), fwd.round(3), math.degrees(foot_yaw), math.degrees(theta)))
cth, sth = math.cos(theta), math.sin(theta)
Rg = np.array([[cth, 0, sth], [0, 1, 0], [-sth, 0, cth]])   # rotation about glTF +Y


def to_final(p):
    return (p - origin) @ Rg.T * scale


# the same transform on the Blender mesh (Blender Z up: glTF (x, y, z) = Blender (x, z, -y))
M = Matrix.Scale(scale, 4) @ Matrix.Rotation(theta, 4, "Z") @ Matrix.Translation((-origin[0], origin[2], -origin[1]))
me.transform(M)
me.update()
pos = positions(me)                                        # final frame, split vertices
P = to_final(P)                                            # final frame, welded vertices
assert np.abs(pos - P[inv]).max() < 1e-4, "mesh and analysis frames disagree"
x, y, z = P.T

# ================================================================ 3. landmarks in the final frame
F = head_hat(P, C, E, say=lambda *a: print("  final   :", *a))
k = F["classes"]; h_, s_, v_ = k["h"], k["s"], k["v"]
cen, axis, rb_, Rb = F["band_center"], F["hat_axis"], F["band_radius"], F["brim_radius"]
assert F["face_forward"][2] < -0.5, "she should face -Z now"
q = P - cen
ha = q @ axis                                              # height above the hat band, along the hat's own axis
hr = np.linalg.norm(q - np.outer(ha, axis), axis=1)        # distance from the hat axis

# ---- broom: bristle head, then the handle as a line fit through the pale wood above it
bristle_core = straw_head(P, C, E, F["masks"]["cape"])
_, s_bl, s_bd = head_size(P[bristle_core])
bc0 = P[bristle_core].mean(0)
cand = k["wood"] & (np.hypot(x - bc0[0], z - bc0[2]) < 0.12) & (y > P[bristle_core][:, 1].max() + 0.08)
pc, _, pv = pca(P[cand]); paxis = pv[:, 0] * np.sign(pv[:, 0][1])
for it in range(4):
    qq = P - pc; pt = qq @ paxis; prad = np.linalg.norm(qq - np.outer(pt, paxis), axis=1)
    pole = k["wood"] & (prad < 0.05) & (y > P[bristle_core][:, 1].max() * 0.9)
    pc, _, pv = pca(P[pole]); paxis = pv[:, 0] * np.sign(pv[:, 0][1])
qq = P - pc; pt = qq @ paxis; prad = np.linalg.norm(qq - np.outer(pt, paxis), axis=1)
pole_r = float(np.median(prad[pole]))
top_sel = pole & (pt > pt[pole].max() - 0.02)
broom_top = P[top_sel].mean(0); broom_top[1] = P[pole][:, 1].max()
on_broom = prad < 0.30                                     # the column around the broom: straw, cord, handle, lantern
tips = on_broom & k["gold"] & (y < 0.03)
broom_base = np.array([P[tips][:, 0].mean(), 0.0, P[tips][:, 2].mean()])
broom_len = float(np.linalg.norm(broom_top - broom_base))
broom_dir = (broom_top - broom_base) / broom_len
# the cord that binds the straw: dark, hugging the broom axis, just above the bristle head
cord = on_broom & (prad < 0.12) & (v_ < 0.45) & (y > 0.15) & (y < 0.75) & ~k["skin"]
labd = components(n, E, cord)
cord = labd == comp_list(labd, 10)[0][0]
cord_lo, cord_hi = float(P[cord][:, 1].min()), float(P[cord][:, 1].max())
straw = on_broom & k["gold"] & (y < cord_hi + 0.16)        # the bristle head and its stubby collar above the cord
# her hand on the handle: the piece of skin and glove wrapped round it, between the straw and the lantern
grip = (k["skin"] | k["plum"]) & (prad < 0.075) & (y > cord_hi + 0.1) & (y < broom_top[1] - 0.25)
labh = components(n, E, grip)
hand = labh == comp_list(labh, 5)[0][0]
hand_t = float(np.median(pt[hand]))
hand_pt = pc + paxis * hand_t
hand_span = (float(P[hand][:, 1].min()), float(P[hand][:, 1].max()))
print("  broom   : base %s top %s length %.3f, handle radius %.4f, lean %.1f deg, cord y %.3f..%.3f, hand at %s (y %.3f..%.3f)" % (
    broom_base.round(3), broom_top.round(3), broom_len, pole_r, math.degrees(math.acos(broom_dir[1])), cord_lo, cord_hi, hand_pt.round(3), *hand_span))

# ---- lantern: everything that hangs off the top of the handle and is not handle
box = (prad < 0.24) & (y > broom_top[1] - 0.50) & (y < broom_top[1] + 0.02)
handle_like = (prad < 0.045) & (k["wood"] | ((s_ < 0.36) & (v_ > 0.45) & ~k["brass"]))   # the handle's surface, whatever its exact tint
labl = components(n, E, box & ~handle_like)
lid = max(comp_list(labl, 20), key=lambda ic: int(((labl == ic[0]) & k["brass"]).sum()))[0]
hang = labl == lid                                         # leather loop + ring + lantern
loop = hang & ((h_ > 0.8) | (h_ < 0.04)) & (v_ < 0.55) & (s_ > 0.2)    # the leather loop round the handle
loop_low = loop & (y < P[loop][:, 1].min() + 0.012)       # ... and its lowest point, where the ring hangs
pivot = P[loop_low].mean(0)
lamp = hang & ~loop & (y < pivot[1] - 0.03)
lamp_c = P[lamp].mean(0); lamp_bottom = float(P[lamp][:, 1].min())
print("  lantern : %d verts (loop %d), pivot %s, body centre %s, bottom y %.3f, radius %.3f" % (
    int(hang.sum()), int(loop.sum()), pivot.round(3), lamp_c.round(3), lamp_bottom, float(np.percentile(np.hypot(x[lamp] - lamp_c[0], z[lamp] - lamp_c[2]), 98))))

# ================================================================ 4. wind weights (the shader in src/player/rider.js)
# r cape: pushed back (+z) and lifted, rippling. Hem most, shoulders hardly; the back more than the front
#   (the front would be pushed into her chest); nothing where a strap, the braid or the bedroll holds it down.
# Meshy's two textures differ a little, so the cape is grown from its saturated core over neighbours of cape hue.
cape = F["masks"]["cape"].copy()
torso = (np.linalg.norm(P - (cen - axis * 1.1 * rb_), axis=1) < 4.8 * rb_) & (ha < -0.6 * rb_)
cape_hue = torso & (h_ > 0.083) & (h_ < 0.125) & (s_ > 0.40) & (v_ > 0.45)
ea, eb = E[:, 0], E[:, 1]
deg = np.zeros(n); np.add.at(deg, ea, 1); np.add.at(deg, eb, 1)       # edges per vertex
core_hem = float(np.percentile(P[cape][:, 1], 1))
for it in range(12):
    grow = np.zeros(n, bool)
    grow[eb[cape[ea]]] = True; grow[ea[cape[eb]]] = True
    add = grow & cape_hue & ~cape & (y > core_hem - 0.02)   # (the strap runs on down to the satchel: stop at the hem)
    if not add.any(): break
    cape |= add
for it in range(2):                                        # close pinholes (a dark crease, a speck of another hue)
    near_cape = np.zeros(n); np.add.at(near_cape, ea, cape[eb]); np.add.at(near_cape, eb, cape[ea])
    cape |= torso & (near_cape >= 0.6 * np.maximum(deg, 1))
cy = P[cape][:, 1]
hem_y, top_y = float(np.percentile(cy, 2)), float(np.percentile(cy, 99.5))
shoulder_y = hem_y + 0.68 * (top_y - hem_y)
cz = float(np.median(P[cape][:, 2]))
# pins: leather (straps, satchel, braid, hair), the bedroll and the brooch, wherever they lie against the cape
turq = (h_ > 0.42) & (h_ < 0.58) & (s_ > 0.45) & (v_ > 0.4)
pin = ~cape & torso & (k["brown"] | k["green"] | turq | ((h_ > 0.05) & (h_ < 0.083) & (s_ > 0.4) & (v_ > 0.3) & (v_ < 0.75)))
# joins: the generated mesh is one skin, so where the cape rests on her arms and neck it runs straight into the
# blouse. A hem that lifted there would drag the sleeve's texture out with it, so those joins hold the cape as well.
join = np.zeros(n, bool)
join[eb[cape[ea] & ~cape[eb]]] = True; join[ea[cape[eb] & ~cape[ea]]] = True
join &= ~pin
pin_d = np.full(n, 1.0); join_d = np.full(n, 1.0)
pin_d[cape] = nearest_dist(P[cape], P[pin])
join_d[cape] = nearest_dist(P[cape], P[join])
w_cape = (cape * (0.10 + 0.90 * ss(shoulder_y, hem_y, y)) * (0.25 + 0.75 * ss(cz - 0.05, cz + 0.07, z))
          * ss(0.008, 0.06, pin_d) * ss(0.006, 0.07, join_d))
print("  cape    : %d verts, hem y %.3f, shoulders y %.3f, top y %.3f, %d pin and %d join verts, mean weight %.3f, max %.3f" % (
    int(cape.sum()), hem_y, shoulder_y, top_y, int(pin.sum()), int(join.sum()), float(w_cape[cape].mean()), float(w_cape.max())))

# g bristles: the straw stands on the floor here, so the tips are pinned and the cord holds the top. In between
#   the bundle only shivers; the loose strands that stick out of it flutter (the shader moves straw in x and y,
#   and y is along the straw now, so anything touching the floor has to stay out of it).
edges_y = np.linspace(0.0, cord_lo, 9)
ctr_y = (edges_y[:-1] + edges_y[1:]) / 2
slabs = [straw & (y >= a_) & (y < b_) for a_, b_ in zip(edges_y[:-1], edges_y[1:])]
mid_x = np.interp(y, ctr_y, [x[m_].mean() for m_ in slabs]); mid_z = np.interp(y, ctr_y, [z[m_].mean() for m_ in slabs])
brad = np.hypot(x - mid_x, z - mid_z)                      # distance from the middle of the bundle at that height
bundle = np.array([np.percentile(brad[m_], 90) for m_ in slabs])
rel = brad / np.interp(y, ctr_y, bundle)
w_bris = straw * ss(cord_lo, cord_lo - 0.14, y) * ss(0.004, 0.075, y) * (0.30 + 0.60 * ss(0.85, 1.2, rel))
print("  bristles: %d verts, bundle radius %.3f (floor) .. %.3f (under the cord), mean weight %.3f, max %.3f" % (
    int(straw.sum()), bundle[0], bundle[-1], float(w_bris[straw].mean()), float(w_bris.max())))

# b hat: the crown is pushed back and its tip whips; the brim flexes towards its rim
crown = (ha > -0.3 * rb_) & (hr < 1.9 * rb_)              # crown, band and the flowers tucked into it
tip_w = crown * ss(-0.4 * rb_, F["hat_tip_axial"], ha)
brim_w = F["masks"]["hat"] * 0.45 * ss(1.04 * rb_, Rb, hr) * (ha < 0.3 * rb_)
w_hat = np.maximum(tip_w, brim_w)
print("  hat     : crown %d verts, brim %d verts" % (int(crown.sum()), int((brim_w > 0).sum())))

# a lantern: a rigid pendulum under the leather loop. The ring between loop and lantern takes up the bend.
w_lant = (hang & ~loop) * ss(pivot[1] + 0.010, pivot[1] - 0.022, y)

wind = np.stack([w_cape, w_bris, w_hat, w_lant], -1)
# smooth over the surface a few times so there are no hard seams (the lantern stays rigid)
for it in range(6):
    acc = np.zeros_like(wind)
    np.add.at(acc, ea, wind[eb]); np.add.at(acc, eb, wind[ea])
    sm = acc / np.maximum(deg, 1)[:, None]
    keep = wind[:, 3].copy()
    wind = wind * 0.4 + sm * 0.6
    wind[:, 3] = keep * 0.8 + wind[:, 3] * 0.2
# what must not move at all: straw tips on the floor, the handle, and everything the lantern does not own
wind[:, 1] *= ss(0.0, 0.03, y) * on_broom
wind[:, 3] *= hang & ~loop
wind[pole & ~hang] = 0
wind = np.clip(wind, 0, 1)
vw = wind[inv].astype(np.float32)                          # back onto the split vertices
# Meshy fused the lantern to the handle where its roof and its ring touch it. A triangle with one corner on the
# swinging lantern and another on the handle would be pulled out like gum, so those few triangles are removed.
tw = wind[:, 3][inv[tri]]
out_of_hang = ~hang[inv[tri]]
bridge = (tw.max(1) > 0.5) & ((tw < 0.01) & out_of_hang).any(1)
if bridge.any():
    import bmesh
    pidx = np.empty(len(me.loop_triangles), np.int32); me.loop_triangles.foreach_get("polygon_index", pidx)
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in np.unique(pidx[bridge])], context="FACES_ONLY")   # vertices stay, so indices do
    bm.to_mesh(me); bm.free(); me.update()
    assert len(me.vertices) == nv
    me.calc_loop_triangles()
print("  lantern : %d triangles between lantern and handle removed (at y %s)" % (
    int(bridge.sum()), np.round(np.sort(P[inv[tri[bridge]]][:, :, 1].mean(1)), 3).tolist()))
attr = me.attributes.new(name="_WIND", type="FLOAT_COLOR", domain="POINT")
attr.data.foreach_set("color", vw.reshape(-1))
print("  wind    : weighted verts cape %d, bristles %d, hat %d, lantern %d (of %d welded)" % (*[int((wind[:, i] > 0.02).sum()) for i in range(4)], n))


# ================================================================ 5. debug renders of the weights
def snap(colours, angle_deg, focus, size, px=640):
    """The model with flat per-vertex colours, turned about the vertical, in a square window around focus."""
    scene = bpy.context.scene
    vc = me.color_attributes.new(name="dbg", type="FLOAT_COLOR", domain="POINT")
    rgba = np.concatenate([np.clip(colours, 0, 1) ** 2.2, np.ones((len(colours), 1))], 1).astype(np.float32)   # vertex colours are linear light
    vc.data.foreach_set("color", rgba[inv].reshape(-1))
    me.color_attributes.active_color = vc
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "VERTEX"
    scene.view_settings.view_transform = "Standard"         # the colours are data: no filmic roll-off
    scene.render.resolution_x = scene.render.resolution_y = px
    scene.render.image_settings.file_format = "PNG"
    if scene.world is None: scene.world = bpy.data.worlds.new("w")
    scene.world.color = (0.02, 0.02, 0.025)
    fb = (focus[0], -focus[2], focus[1])                    # focus in Blender coords
    a_ = math.radians(angle_deg)
    obj.rotation_mode = "XYZ"                               # (the glTF importer leaves objects in quaternion mode)
    obj.rotation_euler = (0, 0, a_)
    obj.location = (-(fb[0] * math.cos(a_) - fb[1] * math.sin(a_)), 0, 0)   # keep the focus in the middle
    cam_data = bpy.data.cameras.new("c"); cam_data.type = "ORTHO"; cam_data.ortho_scale = size
    cam = bpy.data.objects.new("c", cam_data); scene.collection.objects.link(cam); scene.camera = cam
    cam.location = (0, -8, fb[2]); cam.rotation_euler = (math.radians(90), 0, 0)   # looks along +Y
    path = os.path.join(dbg, "_snap.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    obj.rotation_euler = (0, 0, 0); obj.location = (0, 0, 0)
    me.color_attributes.remove(me.color_attributes["dbg"])
    im = bpy.data.images.load(path)
    w_, h_ = im.size
    pix = np.empty(w_ * h_ * 4, np.float32); im.pixels.foreach_get(pix)
    bpy.data.images.remove(im); os.remove(path)
    return pix.reshape(h_, w_, 4)[::-1, :, :3].copy()


def sheet(path, cells, cols, gap=4):
    rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    ch, cw = cells[0].shape[:2]
    canvas = np.full((len(rows) * ch + (len(rows) - 1) * gap, cols * cw + (cols - 1) * gap, 3), 0.1, np.float32)
    for r_, row in enumerate(rows):
        for c_, cell in enumerate(row):
            canvas[r_ * (ch + gap):r_ * (ch + gap) + ch, c_ * (cw + gap):c_ * (cw + gap) + cw] = cell
    rgba = np.concatenate([canvas[::-1], np.ones((*canvas.shape[:2], 1), np.float32)], -1)
    im = bpy.data.images.new("sheet", canvas.shape[1], canvas.shape[0], alpha=False)
    im.pixels.foreach_set(rgba.reshape(-1))
    im.filepath_raw = path; im.file_format = "PNG"; im.save()
    bpy.data.images.remove(im)


grey = np.repeat((C.mean(1) * 0.30 + 0.05)[:, None], 3, 1)   # the model as a dim grey photo
def heat(w):                                                  # 0 grey .. 0.45 red .. 0.85 yellow .. 1 white, over the grey
    c = np.stack([np.clip(w * 2.2, 0, 1), np.clip(w * 2.2 - 0.9, 0, 1), np.clip(w * 3 - 2.2, 0, 1)], -1)
    m = np.clip(w * 8, 0, 1)[:, None]
    return grey * (1 - m) + c * m
# the camera looks along +Y and she faces +Y in Blender: 180 shows her front, 0 her back, 90 her left side
VIEWS = (180, 135, 90, 0, -90, -135)
WHOLE = ((float(pos[:, 0].min() + pos[:, 0].max()) / 2, float(pos[:, 1].max()) / 2 + 0.02, 0.0), float(pos[:, 1].max()) + 0.2)
ZOOM = {"cape": ((0.0, 1.02, 0.03), 0.66), "bristles": (tuple(broom_base + [0, 0.26, 0]), 0.66),
        "hat": (tuple(cen + axis * 0.04), 0.84), "lantern": (tuple((pivot + lamp_c) / 2), 0.40)}
for i, nm in enumerate(("cape", "bristles", "hat", "lantern")):
    sheet(os.path.join(dbg, f"wind_{nm}.png"), [snap(heat(wind[:, i]), a_, *ZOOM[nm]) for a_ in VIEWS], 3)
# all four on the whole figure, in the seated script's colours (cape red, bristles green, hat blue, lantern yellow)
allc = np.maximum(grey * 0.6, np.stack([wind[:, 0] + wind[:, 3], wind[:, 1] + wind[:, 3], wind[:, 2]], -1))
sheet(os.path.join(dbg, "wind_weights.png"), [snap(allc, a_, *WHOLE) for a_ in VIEWS], 6)
# what the script took each part to be
seg = grey * 0.6
for m_, c_ in ((cape, (1, 0.8, 0)), (pin, (0.1, 0.9, 1)), (F["masks"]["hat"], (0.6, 0.1, 0.9)), (crown & ~F["masks"]["hat"], (1, 1, 1)),
               (straw, (0.9, 0.5, 0.1)), (cord, (1, 0, 0)), (pole, (0.3, 0.4, 1)), (hand, (1, 0.5, 0.6)), (hang, (0, 1, 0.3)), (loop, (1, 0, 1))):
    seg[m_] = c_
sheet(os.path.join(dbg, "segments.png"), [snap(seg, a_, *WHOLE) for a_ in VIEWS], 6)

# ================================================================ 6. export
bounds = (pos.min(0), pos.max(0))
info = {
    "name": "rider_stand",
    "units": "model units of rider.glb (the game draws the rider at SCALE 1.28)",
    "up": [0, 1, 0], "forward": [0, 0, -1],
    "origin": "on the floor, midway between the boots",
    "height": round(float(bounds[1][1]), 4),
    "bounds": {"min": [round(float(v), 4) for v in bounds[0]], "max": [round(float(v), 4) for v in bounds[1]]},
    "tris": len(me.polygons),
    "broomHand": "left" if hand_pt[0] < 0 else "right",
    "hand": [round(float(v), 4) for v in hand_pt],
    "handSpanY": [round(v, 4) for v in hand_span],
    "broomTop": [round(float(v), 4) for v in broom_top],
    "broomBase": [round(float(v), 4) for v in broom_base],
    "broomAxis": [round(float(v), 4) for v in broom_dir],
    "broomLength": round(broom_len, 4),
    "handleRadius": round(pole_r, 4),
    "bristleTopY": round(cord_hi, 4),
    "lanternPivot": [round(float(v), 4) for v in pivot],
    "lanternCenter": [round(float(v), 4) for v in lamp_c],
    "lanternBottomY": round(lamp_bottom, 4),
    "hatTip": [round(float(v), 4) for v in F["hat_top"]],
    "hatBandCenter": [round(float(v), 4) for v in cen],
    "hatAxis": [round(float(v), 4) for v in axis],
    "hatBrimRadius": round(Rb, 4),
    "faceCenter": [round(float(v), 4) for v in F["face_center"]],
    "feet": {("left" if f_[0] < 0 else "right"): [round(float(f_[0]), 4), 0.0, round(float(f_[2]), 4)] for f_ in to_final(bcen)},
    "wind": {"attribute": "_WIND", "channels": ["cape", "bristles", "hat", "lantern"],
             "note": "same layout and shader as rider.glb; the straw tips on the floor and the handle carry no weight"},
    "scale": {
        "factor": round(scale, 5),
        "seatedOverStandingRaw": {k_: round(v_, 4) for k_, v_ in ratios.items()},
        "standingOverSeatedAfterScaling": {k_: round(scale / v_, 4) for k_, v_ in ratios.items()},
        # not used for the scale: the cape drapes wider over arms that hang than over arms that reach for the
        # handle, and the standing concept was drawn with a hat-high broom, shorter than the one she flies
        "otherStandingOverSeated": {
            "capeWidth": round((F["cape_x"][1] - F["cape_x"][0]) / (ref["cape_x"][1] - ref["cape_x"][0]), 4),
            "capeWidthFreeArmSideTwice": round(2 * min(abs(F["cape_x"][0]), abs(F["cape_x"][1])) / (ref["cape_x"][1] - ref["cape_x"][0]), 4),
            "broomLength": round(broom_len / ref_broom["length"], 4),
            "bristleHeadLength": round(s_bl / ref_broom["bristle_length"], 4),
            "bristleHeadDiameter": round(s_bd / ref_broom["bristle_diameter"], 4),
        },
    },
    "seated": {
        "file": os.path.basename(seated_path),
        "boundsY": [round(float(ref_bounds[0][1]), 4), round(float(ref_bounds[1][1]), 4)],
        "broomLength": round(ref_broom["length"], 4),
        "bristleHeadLength": round(ref_broom["bristle_length"], 4), "bristleHeadDiameter": round(ref_broom["bristle_diameter"], 4),
        "hatBrimRadius": round(ref["brim_radius"], 4), "hatBandRadius": round(ref["band_radius"], 4), "faceWidth": round(ref["face_width"], 4),
        "hatBandCenter": [round(float(v), 4) for v in ref["band_center"]], "hatTip": [round(float(v), 4) for v in ref["hat_top"]],
    },
}

for im in bpy.data.images:
    if im.size[0] > TEX:
        im.scale(TEX, TEX)


def export(quality):
    bpy.ops.export_scene.gltf(
        filepath=dst, export_format="GLB", use_selection=False,
        export_image_format="WEBP", export_image_quality=quality,
        export_attributes=True, export_vertex_color="NONE",
        export_tangents=True, export_yup=True, export_apply=True,
    )
    return os.path.getsize(dst)


for quality in (90, 88, 86, 84, 82, 78, 74):             # the best WebP quality that fits the budget
    size = export(quality)
    if size <= MAX_BYTES: break
info["bytes"] = size
info["webpQuality"] = quality
json.dump(info, open(os.path.splitext(dst)[0] + ".json", "w"), indent=1)
print("EXPORTED", dst, "%.2f MB" % (size / 1e6), "webp quality", quality, "tris", len(me.polygons))
print(json.dumps(info, indent=1))
