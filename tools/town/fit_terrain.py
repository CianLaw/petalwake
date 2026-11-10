#!/usr/bin/env python3
"""Fit the island to its towns.

    tools/.venv/bin/python tools/town/fit_terrain.py

The island itself comes from tools/terrain/bake.py. This takes that bake (kept untouched in
art/terrain_base/ the first time this runs) and, from assets/town/sites.json, reshapes it where
the towns stand, always starting again from the untouched copy, so it can be run as often as the
layout changes:
  - earthworks: the Crown's hill, the quay's made ground, the harbour basin, the mole;
  - streets graded along their length and level across, squares levelled, lots eased;
  - the meadow cleared from streets, squares and under buildings (splat map), boulders and trees
    in the way removed (props.json);
  - a ground mask per town (assets/town/<town>_mask.png: r cobbles, g flagstones, b bare earth,
    a nothing grows) for the terrain and meadow shaders;
  - sun shadow, ambient occlusion and shore distance re-baked around the changes, and simple
    shadows laid for the lone buildings out in the fields (the towns have real shadow maps);
  - the hidden places (assets/places/*.json): their clearings thinned in the meadow, and the
    shadows of their trees and stones laid on the ground.
"""
import json
import math
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TER = os.path.join(ROOT, "assets", "terrain")
BASE = os.path.join(ROOT, "art", "terrain_base")
TOWN = os.path.join(ROOT, "assets", "town")
sys.argv = sys.argv[:1]
sys.path.insert(0, os.path.join(ROOT, "tools", "terrain"))
import bake as B  # noqa: E402

FILES = ["height.u16", "splat.png", "light.png", "tint.png", "props.json", "meta.json"]
MASK_RES = 0.4          # metres per texel of a town's ground mask
SHADOWED = {"larkhaven", "cairnwick"}       # towns with their own shadow map in the game


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


class Grid:
    """A window onto an n x n field of square cells centred on the origin."""

    def __init__(self, n, half):
        self.n, self.half, self.cell = n, half, 2 * half / n

    def win(self, x0, z0, x1, z1):
        i0 = max(int((x0 + self.half) / self.cell), 0); i1 = min(int((x1 + self.half) / self.cell) + 1, self.n)
        j0 = max(int((z0 + self.half) / self.cell), 0); j1 = min(int((z1 + self.half) / self.cell) + 1, self.n)
        xs = (np.arange(i0, i1) + 0.5) * self.cell - self.half
        zs = (np.arange(j0, j1) + 0.5) * self.cell - self.half
        return (slice(j0, j1), slice(i0, i1)), np.meshgrid(xs, zs)

    def poly_sd(self, poly, margin):
        """Signed distance (metres, positive inside) to a polygon, over a window around it."""
        P = np.asarray(poly, float)
        sl, (X, Z) = self.win(P[:, 0].min() - margin, P[:, 1].min() - margin, P[:, 0].max() + margin, P[:, 1].max() + margin)
        hgt, wid = X.shape
        ss = 4
        im = Image.new("L", (wid * ss, hgt * ss), 0)
        x0, z0 = X[0, 0] - self.cell / 2, Z[0, 0] - self.cell / 2
        ImageDraw.Draw(im).polygon([((p[0] - x0) / self.cell * ss, (p[1] - z0) / self.cell * ss) for p in P], fill=255)
        hi = np.asarray(im) > 127
        sd = (ndimage.distance_transform_edt(hi) - ndimage.distance_transform_edt(~hi)) * self.cell / ss
        sd = sd.reshape(hgt, ss, wid, ss).mean((1, 3))
        return sl, X, Z, sd


def line_dist(X, Z, pts):
    """Distance from every cell to a polyline, and how far along it the nearest point is (as an index)."""
    P = np.asarray(pts, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    dense = [P[0]]
    for a, b, L in zip(P[:-1], P[1:], seg):
        n = max(1, int(L / 0.75))
        for k in range(1, n + 1):
            dense.append(a + (b - a) * k / n)
    D = np.array(dense)
    d, i = cKDTree(D).query(np.stack([X.ravel(), Z.ravel()], 1))
    return d.reshape(X.shape), i.reshape(X.shape), D


def sample(h, G, x, z):
    fx = (np.asarray(x) + G.half) / G.cell - 0.5; fz = (np.asarray(z) + G.half) / G.cell - 0.5
    ix = np.clip(np.floor(fx).astype(int), 0, G.n - 2); iz = np.clip(np.floor(fz).astype(int), 0, G.n - 2)
    tx = fx - ix; tz = fz - iz
    return (h[iz, ix] * (1 - tx) + h[iz, ix + 1] * tx) * (1 - tz) + (h[iz + 1, ix] * (1 - tx) + h[iz + 1, ix + 1] * tx) * tz


def main():
    os.makedirs(BASE, exist_ok=True)
    if not os.path.exists(os.path.join(BASE, "meta.json")) and json.load(open(os.path.join(TER, "meta.json"))).get("towns"):
        # (a fresh clone: art/ is not in the repository, and the terrain in assets/ is the fitted one. Taking
        # that as the untouched bake would pile the earthworks on a second time.)
        raise SystemExit("assets/terrain already has the towns fitted into it and there is no untouched bake in art/terrain_base.\n"
                         "Bake the island first:  tools/.venv/bin/python tools/terrain/bake.py 4096 --keep-props   then run this again.")
    for f in FILES:
        if not os.path.exists(os.path.join(BASE, f)):
            shutil.copy2(os.path.join(TER, f), os.path.join(BASE, f))
            print("kept the untouched bake:", f)
    meta = json.load(open(os.path.join(BASE, "meta.json")))
    N, HALF = meta["n"], meta["world"] / 2
    G = Grid(N, HALF)
    q = np.fromfile(os.path.join(BASE, "height.u16"), dtype="<u2").reshape(N, N)
    h0 = (meta["hMin"] + q.astype(np.float32) * ((meta["hMax"] - meta["hMin"]) / 65535.0)).astype(np.float32)
    h = h0.copy()
    splat = np.asarray(Image.open(os.path.join(BASE, "splat.png"))).astype(np.float32) / 255.0
    light = np.asarray(Image.open(os.path.join(BASE, "light.png"))).astype(np.float32) / 255.0
    props = json.load(open(os.path.join(BASE, "props.json")))
    sites = json.load(open(os.path.join(TOWN, "sites.json")))["towns"]
    GS = Grid(splat.shape[0], HALF)
    masks, towns_meta = {}, []
    calm, rocky = [], []        # sheltered water (no surf), and made stonework that should read as rock
    sown = []                   # windows of the splat that were sown with meadow

    for site in sites:
        tid = site["id"]
        # ---------------------------------------------------------------- earthworks
        dredge = []
        for e in site.get("earth", []):
            if e["kind"] == "hill":
                sl, (X, Z) = G.win(e["x"] - e["r"], e["z"] - e["r"], e["x"] + e["r"], e["z"] + e["r"])
                t = np.clip(np.hypot(X - e["x"], Z - e["z"]) / e["r"], 0, 1)
                h[sl] += (e["h"] * (1 - t * t) ** 2).astype(np.float32)
            elif e["kind"] == "raise":
                sl, X, Z, sd = G.poly_sd(e["poly"], e["edge"] + 3)
                w = smooth(-e["edge"], 0.0, sd)
                h[sl] = np.maximum(h[sl], h[sl] * (1 - w) + e["level"] * w)
            elif e["kind"] == "flat":
                sl, X, Z, sd = G.poly_sd(e["poly"], e["edge"] + 3)
                w = smooth(-e["edge"], 0.0, sd)
                h[sl] = h[sl] * (1 - w) + e["level"] * w
            elif e["kind"] == "basin":
                sl, X, Z, sd = G.poly_sd(e["poly"], 6)
                w = smooth(0.0, e["edge"], sd)
                h[sl] = np.minimum(h[sl], h[sl] * (1 - w) + e["level"] * w)
                dredge.append((sl, w, e["level"]))
                rocky.append((sl, smooth(-3.0, 0.5, sd) * (1 - smooth(1.0, 4.0, sd)), True))
                csl, _, _, csd = G.poly_sd(e.get("calm", e["poly"]), 6)
                calm.append((csl, smooth(-2.5, 0.0, csd)))
            elif e["kind"] == "ridge":
                P = np.asarray(e["pts"])
                reach = e["width"] / 2 + (e["top"] + 25) * e["side"]
                sl, (X, Z) = G.win(P[:, 0].min() - reach, P[:, 1].min() - reach, P[:, 0].max() + reach, P[:, 1].max() + reach)
                d, _, _ = line_dist(X, Z, P)
                bump = (ndimage.gaussian_filter(np.random.default_rng(5).random(X.shape), 1.2) - 0.5) * 1.6
                target = e["top"] - np.maximum(d - e["width"] / 2, 0) / e["side"] + bump * smooth(0.0, 3.0, d - e["width"] / 2)
                rocky.append((sl, (target > h[sl] - 0.5).astype(np.float32) * smooth(reach, e["width"] / 2 + 2.0, d), False))
                h[sl] = np.maximum(h[sl], target)

        # ---------------------------------------------------------------- meadow on made ground
        # (ground raised out of the beach has no grass cover in the bake: sow it, in drifts like its neighbours)
        for e in site.get("earth", []):
            if e["kind"] != "raise":
                continue
            sl, X, Z, sd = GS.poly_sd(e["poly"], e["edge"] + 3)
            ho, hn = sample(h0, G, X, Z), sample(h, G, X, Z)
            gain = ((1 - smooth(3.0, 4.6, ho)) * smooth(3.5, 4.1, hn)).astype(np.float32)
            S4 = splat[sl]
            ok = S4[..., 3] > 0.5
            if ok.any():        # each new patch flowers like the nearest old meadow
                idx = ndimage.distance_transform_edt(~ok, return_distances=False, return_indices=True)
                S4[..., 1] = np.where(gain > 0.25, S4[..., 1][idx[0], idx[1]], S4[..., 1])
            rng = np.random.default_rng(17)
            n1 = ndimage.gaussian_filter(rng.random(X.shape), 7.0); n1 = (n1 - n1.min()) / max(np.ptp(n1), 1e-6)
            n2 = ndimage.gaussian_filter(rng.random(X.shape), 2.5); n2 = (n2 - n2.min()) / max(np.ptp(n2), 1e-6)
            drift = smooth(0.42, 0.7, n1 * 0.7 + n2 * 0.3) * 0.6
            S4[..., 3] = np.maximum(S4[..., 3], gain * (0.82 + 0.18 * n2))
            S4[..., 0] = np.maximum(S4[..., 0], gain * drift)
            sown.append(sl)

        # ---------------------------------------------------------------- streets, squares, lots
        for st in site["streets"]:
            if not st.get("grade", True) or st["kind"] == "edge":
                continue
            P = np.asarray(st["pts"])
            hw, sh = st["width"] / 2, 4.5
            sl, (X, Z) = G.win(P[:, 0].min() - hw - sh, P[:, 1].min() - hw - sh, P[:, 0].max() + hw + sh, P[:, 1].max() + hw + sh)
            d, idx, D = line_dist(X, Z, P)
            hs = ndimage.gaussian_filter1d(sample(h, G, D[:, 0], D[:, 1]), 12.0, mode="nearest")
            w = 1 - smooth(hw + 0.3, hw + sh, d)
            h[sl] = h[sl] * (1 - w) + hs[idx] * w
        for pz in site["plazas"]:
            sl, X, Z, sd = G.poly_sd(pz["poly"], 9)
            inside = sd > 0
            level = pz["level"] if pz.get("level") is not None else float(h[sl][inside].mean())
            w = smooth(-6.0, 0.0, sd) * (0.55 if pz["kind"] == "grass" else 1.0)
            h[sl] = h[sl] * (1 - w) + level * w
        for lot in site["lots"]:
            P = np.asarray(lot["pts"])
            front = (P[0] + P[1]) / 2
            sl, X, Z, sd = G.poly_sd(P, 5)
            level = float(sample(h, G, front[0], front[1]))
            w = smooth(-3.5, 0.5, sd) * 0.75
            h[sl] = h[sl] * (1 - w) + level * w

        # (a street's shoulders must not fill a basin's edge back in: the quay wall stands in deep water)
        for sl, w, level in dredge:
            h[sl] = np.minimum(h[sl], h[sl] * (1 - w) + level * w)

        # ---------------------------------------------------------------- the ground mask
        allp = np.concatenate([np.asarray(s["pts"]) for s in site["streets"]] + [np.asarray(p["poly"]) for p in site["plazas"]] + [np.asarray(l["pts"]) for l in site["lots"]])
        x0, z0 = math.floor(allp[:, 0].min() - 14), math.floor(allp[:, 1].min() - 14)
        x1, z1 = math.ceil(allp[:, 0].max() + 14), math.ceil(allp[:, 1].max() + 14)
        res = MASK_RES if tid in SHADOWED else 1.5
        W, Hh = int((x1 - x0) / res), int((z1 - z0) / res)
        ch = [Image.new("L", (W, Hh), 0) for _ in range(4)]
        dr = [ImageDraw.Draw(c) for c in ch]
        T = lambda p: ((p[0] - x0) / res, (p[1] - z0) / res)
        kinds = {"cobble": 0, "flagstone": 1, "dirt": 2}
        for lot in site["lots"]:
            P = np.asarray(lot["pts"]); c = P.mean(0)
            big = [T(c + (p - c) * (1 + 1.3 / max(np.linalg.norm(p - c), 1e-3))) for p in P]
            dr[2].polygon(big, fill=150)
            dr[3].polygon(big, fill=255)
        for e in site.get("earth", []):
            if e["kind"] == "flat" and e.get("pave", True):
                dr[1].polygon([T(p) for p in e["poly"]], fill=255); dr[3].polygon([T(p) for p in e["poly"]], fill=255)
        for pz in site["plazas"]:
            if pz["kind"] == "grass":          # a village green is mown: the meadow stops at its edge
                dr[3].polygon([T(p) for p in pz["poly"]], fill=215)
                continue
            dr[kinds.get(pz["kind"], 1)].polygon([T(p) for p in pz["poly"]], fill=255)
            dr[3].polygon([T(p) for p in pz["poly"]], fill=255)
        for st in site["streets"]:
            if st["kind"] == "edge":
                continue
            pts = [T(p) for p in st["pts"]]
            k = kinds.get(st["kind"], 0)
            for c2, wd in ((k, st["width"]), (3, st["width"] + 0.8)):
                dr[c2].line(pts, fill=255, width=max(1, int(round(wd / res))), joint="curve")
                r = wd / res / 2
                for p in (pts[0], pts[-1]):
                    dr[c2].ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=255)
        arr = np.stack([ndimage.gaussian_filter(np.asarray(c).astype(np.float32) / 255.0, 0.9 if tid in SHADOWED else 0.5) for c in ch], -1)
        # cobbles and flags win over bare earth where they overlap
        arr[..., 2] *= 1 - np.clip(arr[..., 0] + arr[..., 1], 0, 1)
        masks[tid] = {"x0": x0, "z0": z0, "w": W * res, "h": Hh * res, "res": res, "arr": arr}
        if tid in SHADOWED:
            Image.fromarray(B.to_u8(arr), "RGBA").save(os.path.join(TOWN, f"{tid}_mask.png"), optimize=True)
        c = allp.mean(0)
        towns_meta.append({"id": tid, "name": site["name"], "x": round(float(c[0]), 1), "z": round(float(c[1]), 1),
                           "r": round(float(np.linalg.norm(allp - c, axis=1).max()), 1)})

        # ---------------------------------------------------------------- nothing grows on paving
        sl, (X, Z) = GS.win(x0, z0, x1, z1)
        u = np.clip(((X - x0) / res).astype(int), 0, W - 1); v = np.clip(((Z - z0) / res).astype(int), 0, Hh - 1)
        k = max(1, int(round(GS.cell / res)))
        a = ndimage.uniform_filter(arr[..., 3], k)[v, u]
        near = np.clip(ndimage.gaussian_filter(a, 1.6) * 1.6, 0, 1)
        splat[sl][..., 3] *= 1 - a
        splat[sl][..., 0] *= (1 - a) * (1 - 0.75 * near)

    # -------------------------------------------------------------------- boulders and trees in the way
    def in_town(x, z):
        for m in masks.values():
            u, v = int((x - m["x0"]) / m["res"]), int((z - m["z0"]) / m["res"])
            if 0 <= u < m["arr"].shape[1] and 0 <= v < m["arr"].shape[0] and ndimage.maximum_filter(m["arr"][max(v - 8, 0):v + 9, max(u - 8, 0):u + 9, 3], 3).max() > 0.2:
                return True
        return False
    removed = 0
    for name in list(props):
        if name == "lighthouse":
            continue
        keep = [p for p in props[name] if not in_town(p[0], p[2])]
        removed += len(props[name]) - len(keep)
        props[name] = keep
    # carry the rest up or down with any ground that moved
    for name, items in props.items():
        for it in items:
            dh = float(sample(h, G, it[0], it[2]) - sample(h0, G, it[0], it[2]))
            if abs(dh) > 0.01:
                it[1] = round(it[1] + dh, 2)

    # -------------------------------------------------------------------- light: shadow, occlusion, shore
    changed = np.abs(h - h0) > 0.02
    if changed.any():
        jj, ii = np.nonzero(changed)
        pad = int(160 / G.cell)
        j0, j1, i0, i1 = max(jj.min() - pad, 0), min(jj.max() + pad, N), max(ii.min() - pad, 0), min(ii.max() + pad, N)
        # (one window round everything that moved would span the island: do it town by town)
        lab, nlab = ndimage.label(ndimage.binary_dilation(changed, iterations=40))
        for k in range(1, nlab + 1):
            jj, ii = np.nonzero(lab == k)
            j0, j1, i0, i1 = max(jj.min() - pad, 0), min(jj.max() + pad, N), max(ii.min() - pad, 0), min(ii.max() + pad, N)
            # square it up (the bake's kernels expect square fields)
            side = max(j1 - j0, i1 - i0)
            j1, i1 = min(j0 + side, N), min(i0 + side, N); j0, i0 = j1 - side, i1 - side
            sub = np.ascontiguousarray(h[j0:j1, i0:i1])
            sh = ndimage.gaussian_filter(B.bake_shadow(sub, G.cell, B.SUN[0], B.SUN[1], B.SUN[2], 700.0, 9.0), 1.0)
            ang = np.arange(16) / 16.0 * B.TWO_PI
            dirs = np.stack([np.cos(ang), np.sin(ang)], -1)
            ao = np.clip(B.bake_ao(sub, G.cell, dirs, 10, 60.0) * 0.55 + B.bake_ao(sub, G.cell, dirs, 10, 420.0) * 0.45, 0, 1)
            # feather into the untouched bake at the window's rim
            f = np.minimum.outer(np.minimum(np.arange(side), np.arange(side)[::-1]), np.minimum(np.arange(side), np.arange(side)[::-1]))
            f = smooth(4.0, 40.0, f.astype(np.float32))
            L = light[j0:j1, i0:i1]
            L[..., 0] = L[..., 0] * (1 - f) + sh * f
            L[..., 1] = L[..., 1] * (1 - f) + ao * f
            # the shore: metres offshore (+) or inland (-), from the new coast, where the coast moved
            sea = sub <= 0.0
            sd = (ndimage.distance_transform_edt(sea) - ndimage.distance_transform_edt(~sea)) * G.cell
            gy, gx = np.gradient(sub, G.cell)
            fine = np.clip(-sub / np.maximum(np.hypot(gx, gy), 0.08), -4, 4)
            kf = smooth(4.0, 1.5, np.abs(sd))
            sd = sd * (1 - kf) + fine * kf
            moved = ndimage.gaussian_filter(ndimage.binary_dilation(changed[j0:j1, i0:i1], iterations=14).astype(np.float32), 5.0) * f
            enc = np.clip(0.5 + 0.5 * sd / (np.abs(sd) + 16.0), 0, 1)
            L[..., 2] = L[..., 2] * (1 - moved) + enc * moved
            print(f"re-lit {side * G.cell:.0f} m round ({(i0 + side / 2) * G.cell - HALF:.0f}, {(j0 + side / 2) * G.cell - HALF:.0f})")
    # a harbour basin is sheltered: read as well offshore, so no surf breaks on its walls; and the
    # mole, the pier and the quay wall are stone, not beach
    for sl, k in calm:
        L = light[sl]
        L[..., 2] = np.where(h[sl] < 0.4, np.maximum(L[..., 2], 0.5 + 0.5 * (30.0 / 46.0) * k), L[..., 2])
    for sl, k, wall in rocky:
        L = light[sl]
        if wall:        # a basin's edge is stone only where ground stands behind it, not across open water
            k = k * ndimage.maximum_filter(smooth(-1.0, 1.5, h[sl]), 5)
        L[..., 3] = np.maximum(L[..., 3], k)
    # simple cast shadows for the lone buildings (no shadow map out there)
    sx, sz = B.SUN[0], B.SUN[2]
    hl = math.hypot(sx, sz)
    for site in sites:
        if site["id"] in SHADOWED:
            continue
        for lot in site["lots"]:
            P = np.asarray(lot["pts"])
            ht = lot["top"] * 0.8
            off = np.array([-sx, -sz]) / hl * ht / (B.SUN[1] / hl)
            hull = np.concatenate([P, P + off])
            sl, (X, Z) = G.win(hull[:, 0].min() - 6, hull[:, 1].min() - 6, hull[:, 0].max() + 6, hull[:, 1].max() + 6)
            ss = 3
            im = Image.new("L", (X.shape[1] * ss, X.shape[0] * ss), 0)
            d = ImageDraw.Draw(im)
            tx = lambda p: ((p[0] - (X[0, 0] - G.cell / 2)) / G.cell * ss, (p[1] - (Z[0, 0] - G.cell / 2)) / G.cell * ss)
            for a in range(4):
                b = (a + 1) % 4
                d.polygon([tx(P[a]), tx(P[b]), tx(P[b] + off), tx(P[a] + off)], fill=255)
            d.polygon([tx(p) for p in P + off], fill=255)
            m = ndimage.gaussian_filter(np.asarray(im).astype(np.float32) / 255.0, 2.2).reshape(X.shape[0], ss, X.shape[1], ss).mean((1, 3))
            light[sl][..., 0] *= 1 - 0.82 * m

    # -------------------------------------------------------------------- the hidden places
    B.N, B.CELL = N, B.WORLD / N
    infos, items, nclear = {}, {}, 0
    pdir = os.path.join(ROOT, "assets", "places")
    for fn in ("west.json", "east.json"):
        try:
            places = json.load(open(os.path.join(pdir, fn)))["places"]
        except (OSError, ValueError, KeyError):
            continue
        for pl in places:
            for it in pl.get("items", []):
                try:
                    key = fn + ":" + it["model"]
                    if key not in infos:
                        info = json.load(open(os.path.join(pdir, os.path.splitext(pl["models"][it["model"]])[0] + ".json")))
                        if not info.get("slabs"):
                            continue
                        info.setdefault("height", max(s[4] for s in info["slabs"]))
                        info.setdefault("radius", max(math.hypot(s[0], s[1]) + s[2] for s in info["slabs"]))
                        info.setdefault("baseRadius", info["radius"] * 0.5)
                        infos[key] = info
                    x, y, z = it["pos"]
                    items.setdefault(key, []).append([x, y, z, it.get("yaw", 0.0), it.get("scale", 1.0)])
                except (OSError, ValueError, KeyError, TypeError):
                    continue
            for c in pl.get("clear", []):
                try:
                    r = float(c["r"])
                    sl, (X, Z) = GS.win(c["x"] - r - 6, c["z"] - r - 6, c["x"] + r + 6, c["z"] + r + 6)
                    k = 1 - smooth(r * 0.75, r + 2.0, np.hypot(X - c["x"], Z - c["z"]))
                    splat[sl][..., 3] *= 1 - k * (1 - float(c.get("grass", 1.0)))
                    splat[sl][..., 0] *= 1 - k * (1 - float(c.get("flowers", 1.0)))
                    nclear += 1
                except (KeyError, TypeError, ValueError):
                    continue
    if items:
        B.prop_info = lambda name: infos[name]
        sh, ao = np.ascontiguousarray(light[..., 0]), np.ascontiguousarray(light[..., 1])
        B.stamp_shadows(sh, ao, h, items, N)
        light[..., 0], light[..., 1] = sh, ao
    print(f"places: shadows of {sum(len(v) for v in items.values())} pieces, {nclear} clearings")

    # -------------------------------------------------------------------- write
    lo, hi = meta["hMin"], meta["hMax"]
    if h.min() < lo or h.max() > hi:
        raise SystemExit("heights left the bake's range")
    np.clip((h - lo) / (hi - lo) * 65535.0 + 0.5, 0, 65535).astype("<u2").tofile(os.path.join(TER, "height.u16"))
    Image.fromarray(B.to_u8(splat), "RGBA").save(os.path.join(TER, "splat.png"), optimize=True)
    # the far-field flower colour follows the species sown on made ground (as the bake derives it)
    tint = np.asarray(Image.open(os.path.join(BASE, "tint.png")).convert("RGB")).astype(np.float32) / 255.0
    pal = np.array([[0.94, 0.36, 0.60], [0.96, 0.92, 0.72], [0.52, 0.38, 0.86], [0.96, 0.82, 0.30], [0.90, 0.26, 0.14]], np.float32)
    sig = 9.0 / GS.cell
    for sl in sown:
        m = int(sig * 4)
        j0, j1 = max(sl[0].start - m, 0), min(sl[0].stop + m, splat.shape[0]); i0, i1 = max(sl[1].start - m, 0), min(sl[1].stop + m, splat.shape[1])
        t = pal[np.digitize(splat[j0:j1, i0:i1, 1], [0.42, 0.60, 0.78, 0.90])]
        t = np.stack([ndimage.gaussian_filter(t[..., c], sig) for c in range(3)], -1)
        srgb = np.where(t <= 0.0031308, t * 12.92, 1.055 * np.power(np.clip(t, 1e-6, 1), 1 / 2.4) - 0.055)
        a, b2 = sl[0].start - j0, sl[1].start - i0
        tint[sl] = srgb[a:a + (sl[0].stop - sl[0].start), b2:b2 + (sl[1].stop - sl[1].start)]
    Image.fromarray(B.to_u8(tint), "RGB").save(os.path.join(TER, "tint.png"), optimize=True)
    Image.fromarray(B.to_u8(light), "RGBA").save(os.path.join(TER, "light.png"), optimize=True)
    json.dump(props, open(os.path.join(TER, "props.json"), "w"))
    meta["towns"] = towns_meta
    json.dump(meta, open(os.path.join(TER, "meta.json"), "w"), indent=1)
    json.dump({t: {"file": f"{t}_mask.png", "x0": m["x0"], "z0": m["z0"], "w": m["w"], "h": m["h"]} for t, m in masks.items() if t in SHADOWED},
              open(os.path.join(TOWN, "masks.json"), "w"), indent=1)
    # the terrain's own material set gains the two pavings
    tm = os.path.join(ROOT, "assets", "textures", "materials.json")
    mats = json.load(open(tm))
    town_m = json.load(open(os.path.join(TOWN, "tex", "materials.json")))
    for name in ("cobble", "flagstone"):
        for suf in ("_c.webp", "_n.webp"):
            shutil.copy2(os.path.join(TOWN, "tex", name + suf), os.path.join(ROOT, "assets", "textures", name + suf))
        if name not in mats["order"]:
            mats["order"].append(name)
        mats["mean"][name] = town_m["mean"][name]
    json.dump(mats, open(tm, "w"), indent=1)
    print(f"ground moved under {int(changed.sum() * G.cell ** 2)} m2; {removed} boulders and trees cleared; masks: {', '.join(m for m in masks if m in SHADOWED)}")


if __name__ == "__main__":
    main()
