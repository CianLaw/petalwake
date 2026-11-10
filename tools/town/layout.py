#!/usr/bin/env python3
"""Where everything stands: the towns' streets, squares and lots.

    tools/.venv/bin/python tools/town/layout.py

A town is described below as hand-drawn streets (centre lines through a few points), squares,
a handful of landmarks put exactly where they belong, and for each side of each street the
buildings that line it, in order. The script walks the streets and seats each building on its
lot, front to the street, shoulder to shoulder, skipping where a cross street, a square or an
earlier building is in the way. It writes:
    assets/town/layout.json   every building's place and facing   (-> tools/town/assemble.py)
    assets/town/sites.json    streets, squares, lots, earthworks   (-> tools/town/fit_terrain.py)
    art/town/plan_<town>.png  a plan to look at

World frame: +x east, +z south. A building's yaw is the compass bearing its front faces.
"""
import glob
import json
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from assemble import Terrain  # noqa: E402

BUILD = os.path.join(ROOT, "art", "town", "build")
OUT = os.path.join(ROOT, "assets", "town")


# ---------------------------------------------------------------------------- the catalogue
def catalogue():
    cat = {}
    for f in sorted(glob.glob(os.path.join(BUILD, "*.json"))):
        d = json.load(open(f))
        x0 = y0 = 1e9; x1 = y1 = -1e9
        for ft in d.get("foot", []):
            if ft["kind"] == "rect":
                for px, py in ft["pts"]:
                    x0, x1, y0, y1 = min(x0, px), max(x1, px), min(y0, py), max(y1, py)
            else:
                x0, x1, y0, y1 = min(x0, ft["x"] - ft["r"]), max(x1, ft["x"] + ft["r"]), min(y0, ft["y"] - ft["r"]), max(y1, ft["y"] + ft["r"])
        if x0 > x1:
            (bx0, by0, _), (bx1, by1, _) = d["bounds"]
            x0, x1, y0, y1 = bx0, bx1, by0, by1
        cat[d["id"]] = {"id": d["id"], "name": d.get("name", d["id"]), "kind": d.get("kind", "house"), "rect": (x0, y0, x1, y1),
                        "top": d["bounds"][1][2], "pads": len(d.get("pads", [])), "terrace": bool(d.get("terrace")), "bounds": d["bounds"]}
    return cat


# ---------------------------------------------------------------------------- geometry
def catmull(ctrl, step=2.0):
    P = [np.array(p, float) for p in ctrl]
    P = [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = max(2, int(np.linalg.norm(p2 - p1) / step))
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return np.array(out)


class Line:
    def __init__(self, pts):
        self.p = np.asarray(pts, float)
        d = np.linalg.norm(np.diff(self.p, axis=0), axis=1)
        self.s = np.concatenate([[0], np.cumsum(d)])
        self.length = float(self.s[-1])

    def at(self, s):
        s = min(max(s, 0.0), self.length)
        i = min(int(np.searchsorted(self.s, s, side="right")) - 1, len(self.p) - 2)
        t = (s - self.s[i]) / max(self.s[i + 1] - self.s[i], 1e-9)
        p = self.p[i] + (self.p[i + 1] - self.p[i]) * t
        tg = self.p[i + 1] - self.p[i]
        return p, tg / (np.linalg.norm(tg) or 1.0)

    def dist(self, q):
        q = np.asarray(q, float)
        a, b = self.p[:-1], self.p[1:]
        ab = b - a
        t = np.clip(((q - a) * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-12), 0, 1)
        return float(np.min(np.linalg.norm(a + ab * t[:, None] - q, axis=1)))


def rect_pts(o, r, b, x0, y0, x1, y1):
    return [o + r * x0 + b * y0, o + r * x1 + b * y0, o + r * x1 + b * y1, o + r * x0 + b * y1]


def sat(A, B, margin=0.0):
    """Do two convex polygons overlap by more than `margin`?"""
    for P in (A, B):
        for i in range(len(P)):
            e = P[(i + 1) % len(P)] - P[i]
            ax = np.array([-e[1], e[0]])
            ax /= (np.linalg.norm(ax) or 1.0)
            a = [float(np.dot(p, ax)) for p in A]
            b = [float(np.dot(p, ax)) for p in B]
            if min(a) >= max(b) - margin or min(b) >= max(a) - margin:
                return False
    return True


def in_poly(q, poly):
    x, y = q
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            inside = not inside
    return inside


def samples(R):
    out = list(R)
    for i in range(4):
        out.append((R[i] + R[(i + 1) % 4]) / 2)
    out.append(sum(R) / 4)
    return out


# ---------------------------------------------------------------------------- a town being laid out
class Site:
    def __init__(self, tid, name, cat, terrain, seed=1, shadow=2048):
        self.id, self.name, self.cat, self.T = tid, name, cat, terrain
        self.rng = random.Random(seed)
        self.shadow = shadow
        self.streets, self.plazas, self.items, self.lots, self.earth, self.missing = [], [], [], [], [], []
        self.deco = []
        self.used = set()

    def street(self, key, ctrl, width=5.0, kind="cobble", grade=True):
        ln = Line(catmull(ctrl))
        self.streets.append({"key": key, "line": ln, "width": width, "kind": kind, "grade": grade})
        return ln

    def plaza(self, key, poly, kind="flagstone", level=None):
        self.plazas.append({"key": key, "poly": [np.array(p, float) for p in poly], "kind": kind, "level": level})

    def hill(self, x, z, r, h):
        self.earth.append({"kind": "hill", "x": x, "z": z, "r": r, "h": h})

    def flat(self, poly, level, edge=6.0, pave=True):
        self.earth.append({"kind": "flat", "poly": [list(map(float, p)) for p in poly], "level": level, "edge": edge, "pave": pave})

    def ridge(self, ctrl, width, top, side=1.2):
        self.earth.append({"kind": "ridge", "pts": catmull(ctrl, 3.0).round(2).tolist(), "width": width, "top": top, "side": side})

    def _rect(self, bid, x, z, yaw):
        c = self.cat[bid]
        psi = math.radians(yaw)
        r = np.array([-math.cos(psi), -math.sin(psi)]); b = np.array([-math.sin(psi), math.cos(psi)])
        x0, y0, x1, y1 = c["rect"]
        return rect_pts(np.array([x, z]), r, b, x0, y0, x1, y1)

    def free(self, R, ignore_street=None, margin=0.12):
        for lot in self.lots:
            if sat(R, lot["pts"], margin):
                return False
        pts = samples(R)
        for st in self.streets:
            if st["key"] == ignore_street:
                continue
            for q in pts:
                if st["line"].dist(q) < st["width"] / 2 + 0.25:
                    return False
        for pz in self.plazas:
            for q in pts:
                if in_poly(q, pz["poly"]):
                    return False
        return True

    def put(self, bid, x, z, yaw, name=None, force=False, **extra):
        if bid not in self.cat:
            self.missing.append(bid)
            return False
        R = self._rect(bid, x, z, yaw)
        if not force and not self.free(R):
            return False
        self.items.append({"id": bid, "x": round(float(x), 2), "z": round(float(z), 2), "yaw": round(float(yaw) % 360, 1), **({"name": name} if name else {}), **extra})
        self.lots.append({"id": bid, "pts": R, "top": self.cat[bid]["top"]})
        self.used.add(bid)
        return True

    def prop(self, bid, x, z, yaw=0.0, y=None, clear="lots", **extra):
        """Stand a prop (street furniture, a boat, a tree): no lot of its own, no change to the ground.
        clear = 'lots' (keep off buildings), 'yard' (also off other props), 'all' (also off streets and
        squares) or None."""
        if bid not in self.cat or self.cat[bid].get("pending"):
            self.missing.append(bid)
            return False
        R = self._rect(bid, x, z, yaw)
        if clear and any(sat(R, l["pts"], 0.05) for l in self.lots):
            return False
        if clear == "all" and not self.free(R):
            return False
        if clear in ("all", "yard") and any(sat(R, d, 0.0) for d in self.deco):
            return False
        it = {"id": bid, "x": round(float(x), 2), "z": round(float(z), 2), "yaw": round(float(yaw) % 360, 1), **extra}
        if y is not None:
            it["y"] = y
        self.items.append(it)
        self.deco.append(R)
        return True

    def along(self, ctrl, step, ids, y=None, flip=False, clear=None, start=None):
        """Lay repeating pieces end to end along a line (their x axis along it, +y to the left of travel).
        Returns where the run stops: the point, and the direction of travel there."""
        ln = Line(catmull(ctrl, 1.0))
        s = step / 2 if start is None else start
        k = 0
        while s < ln.length - step * 0.3:
            p, tg = ln.at(s)
            if flip:
                tg = -tg
            self.prop(ids[k % len(ids)], p[0], p[1], math.degrees(math.atan2(-tg[1], -tg[0])), y=y, clear=clear)
            s += step
            k += 1
        return ln.at(min(s - step / 2, ln.length))

    def walled(self, x0, z0, x1, z1, wall="p_wall_garden", step=6.0, door=None, pier="p_wall_pier", skip=""):
        """A walled enclosure: pieces `step` long round a rectangle whose sides are multiples of step, their
        good face outward. door = (side, index) puts a doorway there (sides 'n', 's', 'w', 'e'); skip = sides left open."""
        nx, nz = max(1, round((x1 - x0) / step)), max(1, round((z1 - z0) / step))
        for side, n in (("n", nx), ("s", nx), ("w", nz), ("e", nz)):
            if side in skip:
                continue
            for i in range(n):
                t = (i + 0.5) * step
                x, z, yaw = {"n": (x0 + t, z0, 0), "s": (x0 + t, z1, 180), "w": (x0, z0 + t, 270), "e": (x1, z0 + t, 90)}[side]
                self.prop("p_wall_door" if door == (side, i) else wall, x, z, yaw, clear="lots")
        if pier:
            for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
                self.prop(pier, x, z, 0, clear="lots")

    def rows(self, bid, x0, z0, nx, nz, dx, dz, jitter=0.6, seed=3, skew=0.0):
        """An orchard: nx by nz trees on a grid, a little out of line."""
        rng = random.Random(seed)
        for j in range(nz):
            for i in range(nx):
                self.prop(bid, x0 + i * dx + j * skew + rng.uniform(-jitter, jitter), z0 + j * dz + rng.uniform(-jitter, jitter), rng.uniform(0, 360), clear="all")

    def scatter(self, ids, x0, z0, x1, z1, n, seed=1, mind=3.0):
        """Scatter props over a patch of ground, keeping off buildings, streets and each other."""
        rng = random.Random(seed)
        got, tries, pts = 0, 0, []
        while got < n and tries < n * 40:
            tries += 1
            x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
            if any((x - a) ** 2 + (z - b) ** 2 < mind * mind for a, b in pts):
                continue
            if self.prop(ids[got % len(ids)], x, z, rng.uniform(0, 360), clear="all"):
                pts.append((x, z))
                got += 1
        return got

    def line_up(self, key, side, ids, start=0.0, end=None, setback=0.5, gap=(0.0, 0.5), jitter=2.5, repeat=False):
        """Seat buildings along one side of a street (side = +1 left of the direction of travel, -1 right)."""
        st = next(s for s in self.streets if s["key"] == key)
        ln = st["line"]
        end = ln.length if end is None else end
        s = start
        queue = list(ids)
        while queue and s < end:
            bid = queue[0]
            if bid not in self.cat:
                self.missing.append(queue.pop(0))
                continue
            if bid in self.used and not repeat:
                queue.pop(0)
                continue
            x0, y0, x1, y1 = self.cat[bid]["rect"]
            w = x1 - x0
            placed = False
            tries = 0
            while s + w <= end + 0.5 and tries < 60:
                p, tg = ln.at(s + w / 2)
                n = np.array([tg[1], -tg[0]]) * side          # away from the street on this side
                f = -n
                yaw = math.degrees(math.atan2(f[0], -f[1])) + self.rng.uniform(-jitter, jitter)
                psi = math.radians(yaw)
                r = np.array([-math.cos(psi), -math.sin(psi)])
                sb = setback + self.rng.uniform(0, 0.5) + (self.rng.uniform(0.3, 1.1) if self.rng.random() < 0.22 else 0.0)
                o = p + n * (st["width"] / 2 + sb - y0) - r * ((x0 + x1) / 2)
                if self.put(bid, o[0], o[1], yaw):
                    s += w + self.rng.uniform(*gap)
                    placed = True
                    break
                s += 1.0
                tries += 1
            queue.pop(0)
            if not placed:
                self.missing.append(bid + "(no room on " + key + ")")
        return s

    # ---- output
    def layout(self):
        return {"id": self.id, "name": self.name, "shadow": self.shadow, "items": self.items}

    def site(self):
        return {"id": self.id, "name": self.name,
                "streets": [{"key": s["key"], "pts": s["line"].p.round(2).tolist(), "width": s["width"], "kind": s["kind"], "grade": s["grade"]} for s in self.streets],
                "plazas": [{"key": p["key"], "poly": [q.round(2).tolist() for q in p["poly"]], "kind": p["kind"], "level": p["level"]} for p in self.plazas],
                "lots": [{"id": l["id"], "pts": [q.round(2).tolist() for q in l["pts"]], "top": l["top"]} for l in self.lots],
                "earth": self.earth}

    def plan(self, path, scale=3.0, pad=30):
        allp = np.concatenate([np.array(l["pts"]) for l in self.lots] + [s["line"].p for s in self.streets] + [np.array(p["poly"]) for p in self.plazas] or [np.zeros((1, 2))])
        lo, hi = allp.min(0) - pad, allp.max(0) + pad
        W, H = int((hi[0] - lo[0]) * scale), int((hi[1] - lo[1]) * scale)
        im = Image.new("RGB", (W, H), (176, 196, 140))
        # terrain shading
        xs = np.linspace(lo[0], hi[0], W // 4); zs = np.linspace(lo[1], hi[1], H // 4)
        hh = self.T.at(xs[None, :].repeat(len(zs), 0), zs[:, None].repeat(len(xs), 1))
        g = np.clip((hh - hh.min()) / max(hh.max() - hh.min(), 1e-3), 0, 1)
        base = np.stack([150 + 60 * g, 180 + 40 * g, 120 + 50 * g], -1)
        base[hh < 0.2] = (120, 170, 200)
        im = Image.fromarray(base.astype(np.uint8), "RGB").resize((W, H), Image.BILINEAR)
        d = ImageDraw.Draw(im)
        T = lambda q: ((q[0] - lo[0]) * scale, (q[1] - lo[1]) * scale)
        for p in self.plazas:
            d.polygon([T(q) for q in p["poly"]], fill=(226, 214, 186))
        for s in self.streets:
            d.line([T(q) for q in s["line"].p], fill=(214, 200, 172), width=max(2, int(s["width"] * scale)))
        colors = {"h": (90, 140, 190), "m": (200, 110, 90), "c": (150, 110, 180), "k": (190, 150, 80), "l": (120, 160, 110), "v": (110, 120, 140), "f": (190, 170, 110), "p": (120, 120, 120)}
        for l in self.lots:
            c = colors.get(l["id"][0], (90, 90, 90))
            d.polygon([T(q) for q in l["pts"]], fill=c, outline=(40, 40, 40))
            if self.cat[l["id"]]["pads"]:
                cx, cy = T(sum(l["pts"]) / 4)
                d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 235, 60), outline=(0, 0, 0))
            f0, f1 = T(l["pts"][0]), T(l["pts"][1])
            d.line([f0, f1], fill=(255, 255, 255), width=2)
        for R in self.deco:
            d.polygon([T(q) for q in R], outline=(60, 90, 50))
        im.save(path)


# ============================================================================ the towns themselves
# Lots as briefed to the modellers (frontage, depth, landing places): stand-ins until a model is built.
BRIEF = {}
def _brief(ids, f, d, pads=0):
    for i in ids.split():
        BRIEF[i] = (f, d, pads)
_brief("h_harbourmaster", 9, 9, 1); _brief("h_light", 7, 7, 1); _brief("h_customs", 11, 9, 1); _brief("h_netloft_a", 4.8, 6.5); _brief("h_netloft_b", 4.8, 6.5, 1)
_brief("h_fishmarket", 14, 9); _brief("h_inn", 11, 10); _brief("h_sailloft", 12, 8); _brief("h_chandler", 7.5, 9); _brief("h_smokehouse", 6, 7); _brief("h_boathouse", 9, 10)
_brief("h_warehouse", 10, 11); _brief("h_crane", 6, 6); _brief("h_chapel", 8, 12); _brief("h_cottage_a h_cottage_b h_cottage_c h_cottage_d h_cottage_e", 6, 7)
_brief("m_townhall", 16, 14, 1); _brief("m_couriers", 10, 10, 1); _brief("m_belltower", 6, 6, 1); _brief("m_chapel", 9, 15); _brief("m_markethall", 12, 8); _brief("m_guildhall", 11, 10)
_brief("m_tavern", 11, 10); _brief("m_teahouse", 7.5, 9, 1); _brief("m_bakery m_apothecary m_grocer", 7.5, 9); _brief("m_bookshop m_tailor", 5.5, 8); _brief("m_cobbler", 5.5, 7)
_brief("m_town_a m_town_b m_town_c m_town_d m_town_e", 6.2, 9)
_brief("c_observatory", 8, 8, 1); _brief("c_oldkeep", 11, 11, 1); _brief("c_dovecote", 6, 6, 1); _brief("c_cistern", 7, 7, 1); _brief("c_towerhouse_a c_towerhouse_b c_towerhouse_c", 7, 7, 1)
_brief("c_gatehouse", 11, 6, 1); _brief("c_library", 10, 9, 1); _brief("c_manor", 13, 11); _brief("c_almshouses", 14, 6); _brief("c_pavilion", 5, 5)
_brief("c_terrace_a c_terrace_b c_terrace_c c_terrace_d c_terrace_e c_terrace_f", 7, 8)
_brief("k_dryingtower", 6, 6, 1); _brief("k_shot", 5, 5, 1); _brief("k_watermill", 11, 9); _brief("k_smithy k_weaver k_carpenter", 7.5, 9); _brief("k_pottery", 9, 9); _brief("k_brewhouse", 11, 10)
_brief("k_bathhouse k_school", 8, 9); _brief("k_glassworks", 6, 7); _brief("k_cooper k_candlemaker", 5.5, 7); _brief("k_cottage_a k_cottage_b k_cottage_c k_cottage_d k_cottage_e k_cottage_f", 5.5, 7)
_brief("l_narrow_a l_narrow_b l_narrow_d l_narrow_e l_narrow_g l_narrow_h l_narrow_j", 5.2, 8); _brief("l_narrow_c l_narrow_f l_narrow_i", 5.2, 8, 1)
_brief("l_corner_a l_corner_b l_corner_c l_corner_d", 7.5, 8); _brief("l_stair_a l_stair_b", 6, 8); _brief("l_turret_a l_turret_b", 6, 7, 1); _brief("l_arch", 8, 7); _brief("l_bakehouse", 7, 6)
_brief("v_signal", 8, 8, 1); _brief("v_weather", 7, 7, 1); _brief("v_windpump", 6, 6, 1); _brief("v_lookout", 5, 5, 1); _brief("v_inn", 13, 9, 1); _brief("v_chapel", 7, 12); _brief("v_keepers", 15, 6)
_brief("v_longhouse_a v_longhouse_b", 14, 6); _brief("v_cottage_a v_cottage_b v_cottage_c v_cottage_d v_cottage_e v_cottage_f", 6, 7); _brief("v_bothy_a v_bothy_b", 4, 5)
_brief("v_smokehouse", 5, 6); _brief("v_barn_a v_barn_b", 8, 10)
_brief("f_windmill", 9, 9, 1); _brief("f_beacon", 6, 6, 1); _brief("f_oast", 11, 8, 1); _brief("f_dovecote", 5, 5, 1); _brief("f_shrine", 6, 6, 1); _brief("f_stilt_b", 4, 5, 1); _brief("f_stilt_a", 4, 5)
_brief("f_postmill", 6, 6); _brief("f_farm_a", 13, 7); _brief("f_farm_b", 10, 9); _brief("f_farm_c", 10, 8); _brief("f_barn_a", 14, 9); _brief("f_barn_b", 9, 7); _brief("f_byre", 10, 5)
_brief("f_granary", 5, 6); _brief("f_beehouse", 6, 7); _brief("f_shepherd", 3, 5); _brief("f_roadinn", 13, 11); _brief("f_tollhouse", 6, 6); _brief("f_wellhouse", 3, 3)
_brief("p_fountain", 5, 5)


def with_briefs(cat):
    """Models not built yet stand in as plain lots of the briefed size (so the plan can be drawn early)."""
    for bid, (f, d, pads) in BRIEF.items():
        if bid not in cat:
            centred = bid.startswith("p_")
            cat[bid] = {"id": bid, "name": bid, "kind": "pending", "rect": (-f / 2, -d / 2 if centred else 0.0, f / 2, d / 2 if centred else d), "top": 8.0, "pads": pads,
                        "terrace": False, "bounds": [[-f / 2, 0, 0], [f / 2, d, 8]], "pending": True}
    return cat


def larkhaven(cat, T):
    """The harbour town on the south shore: the quay, the market square a street back from it, lanes in
    between, the craft row running east, and the Crown on its hill behind."""
    S = Site("larkhaven", "Larkhaven", cat, T, seed=11, shadow=4096)
    QZ = 1128.0                                   # the quay's edge
    HX, HZ, HR = -20.0, 964.0, 25.0               # the top of the Crown, and the ring lane round it
    S.hill(HX, HZ, 96.0, 14.0)
    # the quay: made ground, level, with deep water at its foot; a mole and a pier to shelter it
    # the lower town stands on ground made up clear of the beach, the quay a step below it
    S.earth.append({"kind": "raise", "poly": [(-196, QZ), (22, QZ), (70, 1104), (150, 1066), (150, 1024), (-60, 1004), (-200, 1012)], "level": 4.9, "edge": 26.0})
    S.flat([(-178, QZ), (16, QZ), (16, QZ - 30), (-178, QZ - 30)], 4.5, edge=10.0, pave=False)
    QF = QZ + 0.9                                 # the stone face of the quay (the ground stops 3 m behind it, under the paving)
    MOLE = [(-175, QZ + 1), (-184, 1164), (-164, 1192), (-112, 1202)]
    PIER = [(14.0, QF), (19.37, QF + 29.52)]      # 30 m: three lengths of mole
    S.earth.append({"kind": "basin", "poly": [(-172, QZ - 2.0), (12, QZ - 2.0), (56, 1214), (-204, 1214)], "level": -4.5, "edge": 1.0,
                    "calm": [(-174, QZ - 2.0)] + MOLE + [PIER[1], PIER[0], (13, QZ - 2.0)]})
    S.ridge(MOLE, 7.5, 2.7)
    S.ridge(PIER, 6.5, 2.7)

    SQ = (-92.0, 1030.0, -52.0, 1063.4)           # the market square: x0, z0, x1, z1
    S.plaza("square", [(SQ[0], SQ[3]), (SQ[2], SQ[3]), (SQ[2], SQ[1]), (SQ[0], SQ[1])])
    S.plaza("summit", [(HX + 10 * math.cos(a), HZ + 10 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)])
    S.street("quay", [(-172, QZ - 6.5), (-100, QZ - 6.5), (-30, QZ - 6.5), (12, QZ - 6.5)], width=9.0, kind="flagstone")
    S.street("market", [(-176, 1108), (-186, 1088), (-178, 1068), (-140, 1066), (-72, 1066), (0, 1066), (60, 1064), (92, 1056), (118, 1042)], width=5.2)
    S.street("netrow", [(-140, 1096.0), (-106, 1098.5), (-72, 1096.5), (-34, 1099.0), (10, 1097.0)], width=3.8)
    S.street("high", [(-72, QZ - 11.5), (-73, 1092), (-71, 1078), (-72, SQ[3] + 3)], width=5.4)
    S.street("wcross", [(-138, QZ - 11.5), (-137, 1090), (-138, 1069)], width=3.6)
    S.street("ecross", [(8, QZ - 11.5), (9, 1090), (8, 1069)], width=3.8)
    S.street("chapel", [(SQ[0] + 1, SQ[1] + 3), (-116, 1022), (-136, 1004), (-150, 982)], width=4.0)
    S.street("crown", [(SQ[2] - 1, SQ[1] + 1), (-45, 1012), (-37, 998), (HX - 4, HZ + HR + 1)], width=4.4)
    S.street("ring", [(HX + HR * math.cos(a), HZ + HR * math.sin(a)) for a in np.linspace(0.5 * math.pi, 2.5 * math.pi, 17)], width=4.0)
    S.street("summit", [(HX - 2, HZ + HR), (HX - 1, HZ + 9)], width=3.2)
    S.street("north", [(HX, HZ - HR), (HX - 4, 900), (HX - 20, 862), (HX - 44, 824)], width=4.4, kind="dirt")
    S.street("mole", MOLE, width=4.0, kind="flagstone", grade=False)
    S.street("pier", PIER, width=3.6, kind="flagstone", grade=False)
    # the square's edges (not streets: lines to stand buildings along)
    S.street("sq_n", [(SQ[0], SQ[1]), (SQ[2], SQ[1])], width=0.2, kind="edge")
    S.street("sq_w", [(SQ[0], SQ[1]), (SQ[0], SQ[3])], width=0.2, kind="edge")
    S.street("sq_e", [(SQ[2], SQ[1]), (SQ[2], SQ[3])], width=0.2, kind="edge")

    # ---- landmarks, by hand
    S.put("c_observatory", HX + 0.5, HZ - 3.5, 190, force=True)
    S.put("c_gatehouse", HX, HZ - HR - 6, 0, force=True)           # the north road runs through its arch
    S.put("h_crane", -24, QZ - 4.5, 180, force=True)               # on the quay's edge
    S.put("m_markethall", -80, 1038, 180, force=True)              # standing in the square
    S.put("p_fountain", -63, 1052, 0, force=True)

    # ---- the square
    S.line_up("sq_n", 1, ["m_tavern", "m_bakery", "m_couriers"], start=0.4, setback=0.3, gap=(0.1, 0.4), jitter=1.0)
    S.line_up("sq_e", 1, ["m_townhall", "m_tailor"], start=3.5, setback=0.3, jitter=0.5)
    S.line_up("sq_w", -1, ["m_chapel", "m_belltower", "m_cobbler"], start=7.5, setback=0.3, gap=(0.4, 0.8), jitter=0.8)

    # ---- the quay front (west to east)
    S.line_up("quay", 1, ["h_harbourmaster", "h_netloft_a", "h_netloft_b", "h_cottage_a", "h_chandler", "l_narrow_a", "h_inn", "h_customs", "l_narrow_b", "h_fishmarket",
                          "h_sailloft", "h_cottage_b", "h_warehouse", "h_smokehouse", "l_narrow_d", "h_boathouse"], start=3.0, setback=0.6, gap=(0.0, 0.7))
    # ---- net row: the lane behind the quay houses
    S.line_up("netrow", 1, ["h_cottage_c", "l_narrow_g", "l_stair_a", "k_cottage_a", "l_narrow_h", "h_chapel", "h_cottage_d", "l_bakehouse", "l_narrow_e",
                            "k_cottage_b", "l_stair_b", "h_cottage_e", "l_narrow_j", "k_cottage_c", "k_cottage_d", "k_cottage_e"], start=1.5, gap=(0.0, 1.1))
    # ---- market street, west to east: north side, then south side
    S.line_up("market", 1, ["k_bathhouse", "k_school", "m_bookshop", "m_teahouse"], start=46.0, end=108.0, gap=(0.2, 1.0))
    S.line_up("market", 1, ["m_apothecary", "m_grocer", "k_smithy", "k_cooper", "k_pottery", "k_candlemaker", "k_brewhouse", "k_shot"], start=156.0, gap=(0.2, 1.2))
    S.line_up("market", -1, ["l_corner_c", "m_town_a", "l_narrow_c", "m_town_b", "m_guildhall", "l_corner_a", "l_corner_b", "m_town_c", "l_narrow_f", "m_town_d", "l_arch", "m_town_e",
                             "l_narrow_i", "l_corner_d", "k_weaver", "k_glassworks", "k_carpenter", "k_dryingtower", "k_watermill"], start=46.0, gap=(0.0, 0.6))
    S.line_up("chapel", 1, ["c_terrace_a", "k_cottage_f"], start=10.0, gap=(0.5, 2.0))
    S.line_up("chapel", -1, ["c_terrace_b", "c_almshouses"], start=14.0, gap=(0.5, 2.0))
    # ---- the Crown
    S.line_up("crown", 1, ["c_towerhouse_a", "c_terrace_c", "c_terrace_f"], start=4.0, gap=(0.3, 1.2))
    S.line_up("crown", -1, ["c_terrace_d", "c_dovecote", "c_terrace_e"], start=8.0, gap=(0.3, 1.2))
    S.line_up("ring", -1, ["l_turret_a", "c_oldkeep", "c_towerhouse_b", "c_cistern", "c_manor", "c_towerhouse_c", "c_library", "l_turret_b"], start=7.0, gap=(1.5, 5.0), setback=0.6)
    S.line_up("ring", 1, ["c_pavilion"], start=112.0, setback=0.4)

    # ================= dressing: everything that stands between the buildings =================
    QY = 4.46                                           # the quay's paving
    STAIRS = {5: -133.0, 15: -53.0}                     # which lengths of the quay edge are steps, and where
    # ---- the quay's stone edge, with two flights of steps down to the water
    for k in range(24):
        S.prop("p_quay_stairs" if k in STAIRS else ("p_quay" if k % 2 else "p_quay_b"), -173 + 8 * k, QZ - 0.9, 180, y=QY, clear=None)
    # ---- the mole and the pier, stone over the rubble
    # (the basin is dredged right under them: these pieces are the moles, down to the harbour floor)
    DECK = 2.95
    pe, te = S.along(MOLE, 10.0, ["p_mole"], y=DECK)
    S.prop("p_mole_head", pe[0], pe[1], math.degrees(math.atan2(-te[1], -te[0])), y=DECK, clear=None)
    lc = pe + te * 0.2                                  # the Harbour Light stands on the mole's head, its door toward the walk
    S.put("h_light", lc[0] - te[0] * 3.5, lc[1] - te[1] * 3.5, math.degrees(math.atan2(-te[0], te[1])), force=True, y=DECK + 0.06)
    S.along(list(reversed(PIER)), 10.0, ["p_mole"], y=DECK)
    pd = np.array(PIER[1]) - np.array(PIER[0])
    pd = pd / np.linalg.norm(pd)
    S.prop("p_mole_end", PIER[1][0], PIER[1][1], math.degrees(math.atan2(-pd[1], -pd[0])), y=DECK, clear=None)
    S.prop("p_lamp_iron", PIER[1][0] + pd[0] * 1.4, PIER[1][1] + pd[1] * 1.4, 0, y=DECK + 0.06, clear=None)
    S.prop("p_stone_bench", PIER[1][0] - pd[0] * 2.5 - pd[1] * 1.6, PIER[1][1] - pd[1] * 2.5 + pd[0] * 1.6, math.degrees(math.atan2(pd[1], pd[0])) + 90, y=DECK + 0.06, clear=None)
    # ---- a jetty from each flight of steps (the steps pass its deck 2.3 m west of their middle), and the boats
    JY = 0.85
    for cx, n in ((STAIRS[15], 3), (STAIRS[5], 2)):
        jx = cx - 2.3
        for i in range(n):
            S.prop("p_jetty", jx, QF + 0.25 + 3 + 6 * i, 270, y=JY, clear=None)
        S.prop("p_jetty_end", jx, QF + 0.25 + 6 * n + 1.5, 270, y=JY, clear=None)
    ex, wx = STAIRS[15] - 2.3, STAIRS[5] - 2.3
    for bid, x, z, yaw in (("p_ketch", -20, QF + 2.5, 180), ("p_fishing_boat", ex - 2.6, QF + 9.5, 270), ("p_fishing_boat", ex + 2.7, QF + 15.5, 90),
                           ("p_rowboat", ex - 2.2, QF + 17.6, 262), ("p_rowboat", ex + 2.2, QF + 5.5, 84), ("p_fishing_boat", wx - 2.6, QF + 8.0, 270),
                           ("p_rowboat", wx + 2.2, QF + 10.5, 95), ("p_rowboat", -98, QF + 1.25, 180), ("p_rowboat", -158, QF + 1.25, 176),
                           ("p_rowboat", -84, QF + 32, 215), ("p_fishing_boat", -128, 1180, 140), ("p_buoy", -72, 1196, 0), ("p_buoy", -30, 1184, 0)):
        S.prop(bid, x, z, yaw, clear=None)
    # ---- the working quay
    for bid, x, z, yaw in (("p_crane", -116, QZ - 1.7, 180), ("p_net_rack", -160, 1122.6, 0), ("p_net_rack", -92, 1124.0, 6), ("p_lobster_pots", -146, 1123.6, 30),
                           ("p_lobster_pots", -38, 1124.0, 200), ("p_fish_rack", -104, 1123.2, 0), ("p_fish_boxes", -66, 1124.2, 20), ("p_fish_boxes", -12, 1123.8, 150),
                           ("p_boat_upturned", -169, 1121.5, 30), ("p_crates_barrels", -84, 1118.4, 180), ("p_crates_barrels", 0, 1118.6, 180),
                           ("p_crates_barrels", -126, 1118.6, 170), ("p_hand_cart", -46, 1121.2, 40), ("p_gull_statue", -72, 1123.6, 180),
                           ("p_stone_bench", -30, 1124.6, 180), ("p_stone_bench", -122, 1124.6, 180)):
        S.prop(bid, x, z, yaw)
    for k in range(7):
        S.prop("p_lamp_iron", -165 + 28 * k, 1124.9, 180)
    # ---- the boatyard on the green at the quay's east end, and the strand beyond it
    for bid, x, z, yaw in (("p_boat_upturned", -22, 1107, 20), ("p_boat_upturned", -13, 1111, 75), ("p_boat_upturned", -4, 1105, 140), ("p_net_rack", -19, 1114.4, 0),
                           ("p_net_rack", -7, 1114.6, 8), ("p_wood_pile", -27, 1103.5, 90), ("p_fish_rack", 1, 1110.5, 90), ("p_crates_barrels", -29, 1112.5, 250),
                           ("p_lobster_pots", -11, 1104.2, 60), ("p_wheelbarrow", -17, 1103.6, 310), ("p_tree_apple", -1, 1101.2, 0), ("p_tree_pine", 24, 1108, 200),
                           ("p_tree_pine", 37, 1096, 170), ("p_boat_upturned", 27, 1119, 100), ("p_net_rack", 34, 1112, 300), ("p_stone_bench", 20.5, 1122.5, 200),
                           ("p_lamp_timber", 12.4, 1118.2, 270), ("p_signpost", 12.6, 1102, 30)):
        S.prop(bid, x, z, yaw, clear="all")
    # ---- the market square
    for bid, x, z, yaw in (("p_market_cross", -72, 1048, 0), ("p_stall_fruit", -88.2, 1046, 90), ("p_stall_fish", -88.2, 1052.4, 90), ("p_stall_cloth", -83.5, 1059.2, 0),
                           ("p_stall_pots", -76.5, 1059.6, 0), ("p_flower_cart", -58.5, 1043.5, 250), ("p_tree_bench", -58, 1035.5, 0), ("p_bunting", -72, 1041, 0),
                           ("p_bunting", -72, 1056, 0), ("p_tavern_table", -86.5, 1033.4, 0), ("p_tavern_table", -81.5, 1033.2, 8), ("p_stone_bench", -53.8, 1058, 270),
                           ("p_stone_bench", -66, 1061.6, 180), ("p_notice_board", -53.4, 1052.6, 270), ("p_signpost", -68.2, 1069.4, 20),
                           ("p_lamp_iron", -90.4, 1031.8, 0), ("p_lamp_iron", -53.6, 1031.8, 0), ("p_lamp_iron", -90.4, 1061.8, 0), ("p_lamp_iron", -53.6, 1061.8, 0),
                           ("p_horse_trough", -47.5, 1064.6, 0), ("p_well", -119, 1017, 20), ("p_hay_wagon", 96, 1057, 15), ("p_mounting_block", -95, 1064.5, 0)):
        S.prop(bid, x, z, yaw)
    for x in (-160, -132, -104, -40, -12, 16, 44, 72):
        S.prop("p_lamp_timber", x, 1063.7, 180)
    for x, z in ((-120, 1094.6), (-88, 1095.0), (-52, 1095.4), (-18, 1095.2)):
        S.prop("p_lamp_timber", x, z, 180)
    for th in (45, 135, 225, 315):
        S.prop("p_lamp_iron", HX + 27.7 * math.sin(rad_(th)), HZ - 27.7 * math.cos(rad_(th)), th + 180)
    # ---- the orchard in the fork of the two lanes above the square, behind its wall
    S.walled(-97, 997, -67, 1015, door=("s", 2))
    S.rows("p_tree_apple", -92.5, 1001, 5, 3, 5.4, 5.2, seed=4)
    for bid, x, z, yaw in (("p_beehives", -70.5, 1000.5, 250), ("p_pergola", -71.5, 1011.5, 0), ("p_wheelbarrow", -80, 1013.2, 40), ("p_stone_bench", -86, 1013.6, 0)):
        S.prop(bid, x, z, yaw, clear="all")
    # ---- kitchen gardens east of the lane up to the Crown
    S.walled(-27, 1024, -3, 1042, door=("w", 1))
    for bid, x, z, yaw in (("p_veg_patch", -22.5, 1028.2, 0), ("p_veg_patch", -16.5, 1028.4, 0), ("p_veg_patch", -22.5, 1033.2, 0), ("p_veg_patch", -16.5, 1033.4, 0),
                           ("p_flower_bed", -9.5, 1027.4, 90), ("p_beehives", -6, 1039, 200), ("p_pergola", -10, 1034.5, 90), ("p_tree_apple", -22, 1038.6, 0),
                           ("p_scarecrow", -19.5, 1030.8, 200), ("p_wheelbarrow", -13.4, 1038.8, 100), ("p_washing_line", -15, 1040.2, 0), ("p_topiary", -4.6, 1025.6, 0)):
        S.prop(bid, x, z, yaw, clear="all")
    for z in (1001, 1008, 1015, 1022):                  # a row of cypresses up the lane
        S.prop("p_tree_cypress", -30.5 + (z - 1001) * -0.42, z, 0, clear="all")
    S.scatter(["p_tree_apple", "p_hedge", "p_flower_bed", "p_tree_cypress", "p_haystack", "p_tree_apple", "p_veg_patch", "p_tree_cypress"],
              -22, 992, 16, 1020, 12, seed=8, mind=6.5)
    S.scatter(["p_tree_apple", "p_tree_cypress", "p_flower_bed", "p_hedge", "p_tree_apple", "p_topiary"], -104, 985, -52, 996, 7, seed=7, mind=6.0)
    S.scatter(["p_topiary", "p_stone_bench", "p_flower_bed", "p_topiary"], HX - 9, HZ - 9, HX + 9, HZ + 9, 6, seed=9, mind=3.5)
    # ---- back yards between the rows: vegetables, washing, an apple tree
    S.scatter(["p_veg_patch", "p_tree_apple", "p_washing_line", "p_flower_bed", "p_wood_pile", "p_tree_apple", "p_pergola", "p_beehives", "p_wheelbarrow", "p_topiary"],
              -134, 1079.5, 4, 1086.5, 28, seed=5, mind=5.0)
    S.scatter(["p_washing_line", "p_crates_barrels", "p_wood_pile", "p_wheelbarrow", "p_flower_bed", "p_veg_patch"], -168, 1101.4, -34, 1106.2, 14, seed=6, mind=6.0)
    # ---- west of the square: an old orchard, hay, a paddock wall along the lane
    S.rows("p_tree_apple", -176, 1014, 6, 4, 6.2, 6.0, jitter=1.0, seed=12, skew=0.8)
    for bid, x, z, yaw in (("p_haystack", -134, 1040, 0), ("p_haystack", -128, 1046.5, 40), ("p_hay_wagon", -139, 1049, 300), ("p_scarecrow", -150, 1003, 160),
                           ("p_beehives", -183, 1012, 90), ("p_wood_pile", -122, 1049.5, 0)):
        S.prop(bid, x, z, yaw, clear="all")
    S.along([(-196, 1008), (-196, 1056)], 8.0, ["p_wall_field"], clear="lots")
    S.along([(-192, 1004), (-144, 1000)], 8.0, ["p_wall_field"], clear="lots")
    # ---- the road east out of town: field walls, a gate, hay
    S.along([(22, 1060.6), (86, 1056.4)], 8.0, ["p_wall_field"], clear="lots")
    S.along([(24, 1071.2), (64, 1069.4)], 8.0, ["p_wall_field"], clear="lots")
    for bid, x, z, yaw in (("p_haystack", 40, 1050, 0), ("p_haystack", 52, 1046, 30), ("p_tree_apple", 30, 1046, 0), ("p_tree_apple", 66, 1049, 0), ("p_scarecrow", 46, 1038, 190),
                           ("p_veg_patch", 34, 1078, 10), ("p_veg_patch", 41, 1079, 4), ("p_tree_pine", 122, 1082, 180), ("p_tree_pine", 136, 1030, 200),
                           ("p_tree_pine", 62, 1006, 160), ("p_tree_pine", 84, 1084, 190)):
        S.prop(bid, x, z, yaw, clear="all")
    S.prop("p_gate_piers", 119, 1041.6, 62, clear=None)
    S.prop("p_gate_piers", -183.6, 1078, 262, clear=None)
    # ---- what is left of the old town wall, either side of the gate
    for th in (-34, -19, 19, 34):
        S.prop("p_wall_ruin", HX + 33.5 * math.sin(rad_(th)), HZ - 33.5 * math.cos(rad_(th)), th)
    S.prop("p_bastion", HX + 34.5 * math.sin(rad_(-50)), HZ - 34.5 * math.cos(rad_(-50)), -50)
    # ---- the edge of town, north and west
    for x, z in ((-206, 1066), (-212, 1030), (-170, 986), (-128, 968), (28, 934), (-66, 940), (40, 972)):
        S.prop("p_tree_pine", x, z, S.rng.uniform(150, 210), clear="all")
    for bid, x, z, yaw in (("p_haystack", -44, 884, 0), ("p_scarecrow", -58, 872, 200), ("p_wall_field", -6, 902, 78), ("p_wall_field", -10, 894, 82),
                           ("p_haystack", 30, 890, 0), ("p_wall_field", -34, 906, 80), ("p_wall_field", -36, 898, 84), ("p_tree_apple", -52, 896, 0)):
        S.prop(bid, x, z, yaw, clear="all")
    return S


def rad_(d):
    return d * math.pi / 180.0


def cliff_edge(T, x, z0=-1050.0):
    """Walking north from z0, where the ground first falls away."""
    z = z0
    h0 = float(T.at(x, z))
    while z > -1500 and float(T.at(x, z - 3)) > h0 - 12:
        z -= 3
        h0 = max(h0 - 0.5, float(T.at(x, z)))
    return z


def cairnwick(cat, T):
    """The cliff village on the north coast: one lane along the cliff top with a green at its middle, crofts
    behind drystone walls, and the things that stand up into the wind out at the edge."""
    S = Site("cairnwick", "Cairnwick", cat, T, seed=23, shadow=2048)
    ez = cliff_edge(T, 180)
    lz = cliff_edge(T, 118)
    S.plaza("green", [(158, -1194.5), (204, -1192.5), (206, -1166), (156, -1168)], kind="grass")
    S.street("row", [(104, -1200), (140, -1203), (180, -1200), (222, -1195), (256, -1188)], width=4.4)
    S.street("tower", [(181, -1202), (181, -1224), (180, ez + 20)], width=3.2, kind="dirt")
    S.street("south", [(181, -1166), (177, -1140), (161, -1110), (141, -1076)], width=3.8, kind="dirt")
    S.street("lookout", [(138, -1205), (128, -1226), (119, lz + 15)], width=2.4, kind="dirt")
    S.street("pump", [(238, -1190), (247, -1176), (251, -1164)], width=2.4, kind="dirt")
    S.street("green_s", [(156, -1168), (206, -1166)], width=0.2, kind="edge")
    S.street("green_e", [(206, -1166), (204, -1192.5)], width=0.2, kind="edge")
    S.street("green_w", [(158, -1194.5), (156, -1168)], width=0.2, kind="edge")
    S.put("v_signal", 180, ez + 13, 180, force=True)
    S.put("v_lookout", 118, lz + 9, 170, force=True)
    S.put("v_windpump", 252, -1157, 200, force=True)
    # the cliff side of the lane, west to east (the path to the tower leaves between the inn and the weather house)
    S.line_up("row", 1, ["v_longhouse_a", "v_cottage_a", "v_inn"], start=38.0, end=76.0, gap=(1.2, 2.4), jitter=3)
    S.line_up("row", 1, ["v_weather", "v_keepers", "v_smokehouse"], start=80.5, gap=(1.4, 3.0), jitter=3)
    # the landward side, either end of the green
    S.line_up("row", -1, ["v_cottage_c", "v_cottage_b", "v_bothy_a"], start=22.0, end=56.0, gap=(1.5, 3.0), jitter=4)
    S.line_up("row", -1, ["v_cottage_d", "v_longhouse_b"], start=106.0, gap=(1.5, 3.0), jitter=4)
    S.line_up("green_e", -1, ["v_chapel"], start=6.0, setback=1.5)
    S.line_up("green_s", -1, ["v_cottage_e", "v_cottage_f"], start=3.0, setback=1.2, gap=(15.0, 20.0), jitter=5)
    S.line_up("south", 1, ["v_barn_a", "v_bothy_b"], start=24.0, setback=2.0, gap=(6.0, 10.0), jitter=6)
    S.line_up("south", -1, ["v_barn_b"], start=40.0, setback=2.5, jitter=6)

    # ================= dressing =================
    # ---- the green: a well, benches, wind-bent pines
    for bid, x, z, yaw in (("p_well", 181, -1181, 20), ("p_stone_bench", 174.5, -1178, 100), ("p_stone_bench", 186, -1186.5, 200), ("p_tree_pine", 162, -1172.5, 190),
                           ("p_tree_pine", 199, -1188, 170), ("p_horse_trough", 168, -1190.5, 0), ("p_signpost", 184.4, -1196.6, 20), ("p_notice_board", 176, -1195.6, 180),
                           ("p_mounting_block", 196, -1193.8, 0), ("p_hand_cart", 192, -1171, 60)):
        S.prop(bid, x, z, yaw)
    for x, z in ((122, -1198.7), (152, -1199.7), (208, -1193.6), (236, -1189.2)):
        S.prop("p_lamp_timber", x, z, 0)
    S.prop("p_lamp_timber", 183.6, -1206.5, 270)
    # ---- crofts behind drystone walls
    S.walled(112, -1192, 136, -1168, wall="p_wall_field", step=8.0, pier=None, skip="n")
    S.walled(136, -1192, 152, -1168, wall="p_wall_field", step=8.0, pier=None, skip="nw")
    S.walled(210, -1184, 242, -1160, wall="p_wall_field", step=8.0, pier=None, skip="n")
    S.walled(92, -1232, 108, -1208, wall="p_wall_field", step=8.0, pier=None, skip="e")
    for bid, x, z, yaw in (("p_veg_patch", 117, -1186, 0), ("p_veg_patch", 123, -1186.4, 0), ("p_veg_patch", 117, -1180.6, 0), ("p_scarecrow", 120.5, -1183.4, 190),
                           ("p_haystack", 130, -1174, 0), ("p_washing_line", 127, -1187.6, 5), ("p_beehives", 115, -1171, 270), ("p_wood_pile", 141, -1188.6, 90),
                           ("p_veg_patch", 145, -1176, 90), ("p_wheelbarrow", 142.5, -1181, 200), ("p_haystack", 217, -1166.5, 0), ("p_haystack", 224, -1170, 30),
                           ("p_veg_patch", 232, -1178, 0), ("p_veg_patch", 232, -1172.4, 0), ("p_washing_line", 219, -1180.5, 350), ("p_wood_pile", 238, -1166, 0),
                           ("p_hay_wagon", 100, -1220, 250), ("p_haystack", 99, -1228, 0), ("p_beehives", 104.5, -1212, 90), ("p_wall_field", 96, -1198, 0)):
        S.prop(bid, x, z, yaw, clear="all")
    # ---- fish and gear by the smokehouse and along the cliff path
    for bid, x, z, yaw in (("p_fish_rack", 243, -1207, 20), ("p_fish_rack", 250, -1204.6, 15), ("p_net_rack", 226, -1210, 185), ("p_lobster_pots", 235, -1206.5, 40),
                           ("p_crates_barrels", 166.5, -1210.5, 180), ("p_boat_upturned", 203, -1218, 70), ("p_net_rack", 150, -1214, 170), ("p_wood_pile", 113, -1211.5, 0),
                           ("p_stone_bench", 172, ez + 12, 0), ("p_stone_bench", 126, lz + 10.5, 350), ("p_fence_picket", 186.5, ez + 5.5, 0),
                           ("p_fence_picket", 190.5, ez + 5.5, 0), ("p_fence_picket", 173.5, ez + 5.5, 0), ("p_fence_picket", 169.5, ez + 5.5, 0)):
        S.prop(bid, x, z, yaw, clear="all")
    # ---- the road in from the south, between its walls
    S.along([(170.5, -1128), (148, -1088)], 8.0, ["p_wall_field"], clear="all")
    S.along([(183, -1150), (171, -1112)], 8.0, ["p_wall_field"], clear="all")
    S.prop("p_gate_piers", 143.2, -1079.6, 30, clear=None)
    for x, z in ((262, -1178), (88, -1196), (150, -1150), (214, -1146)):
        S.prop("p_tree_pine", x, z, S.rng.uniform(160, 200), clear="all")
    return S


def fields(cat, T):
    """Farms and lone buildings out in the meadows."""
    S = Site("fields", "The Meadows", cat, T, seed=37, shadow=0)

    def frame(x, z, yaw):
        """A yard's own frame: (right, back) in metres from the front middle of its main building."""
        psi = math.radians(yaw)
        r = np.array([-math.cos(psi), -math.sin(psi)]); b = np.array([-math.sin(psi), math.cos(psi)])
        return lambda dx, dy: np.array([x, z]) + r * dx + b * dy

    def group(x, z, yaw, pieces):
        """A farmstead: pieces = [(id, right, back, turn)], offsets in metres in the yard's own frame."""
        at = frame(x, z, yaw)
        for bid, dx, dy, turn in pieces:
            o = at(dx, dy)
            S.put(bid, o[0], o[1], yaw + turn, force=True)

    def dress(x, z, yaw, items):
        """Props in a yard's frame: (id, right, back, turn)."""
        at = frame(x, z, yaw)
        for bid, dx, dy, turn in items:
            o = at(dx, dy)
            S.prop(bid, o[0], o[1], yaw + turn, clear="yard")

    def run(x, z, yaw, bid, step, p0, p1):
        """A line of wall or fence lengths from p0 to p1 in a yard's frame (the distance a multiple of step)."""
        at = frame(x, z, yaw)
        n = max(1, round(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / step))
        turn = -math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        for i in range(n):
            t = (i + 0.5) / n
            o = at(p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)
            S.prop(bid, o[0], o[1], yaw + turn, clear="yard")

    def yard(x, z, yaw, key, x0, y0, x1, y1):
        """Trodden ground: the meadow stops at the yard's edge (a rectangle in its frame, or a round with x1 = radius)."""
        at = frame(x, z, yaw)
        if y1 is None:
            poly = [at(x0 + x1 * math.cos(a), y0 + x1 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)]
        else:
            poly = [at(x0, y0), at(x1, y0), at(x1, y1), at(x0, y1)]
        S.plaza(key, poly, kind="grass")

    def orchard(x, z, yaw, dx0, dy0, nx, ny, sx=6.0, sy=6.0, seed=1, bid="p_tree_apple"):
        at = frame(x, z, yaw)
        rng = random.Random(seed)
        for j in range(ny):
            for i in range(nx):
                o = at(dx0 + i * sx + rng.uniform(-0.8, 0.8), dy0 + j * sy + rng.uniform(-0.8, 0.8))
                S.prop(bid, o[0], o[1], rng.uniform(0, 360), clear="yard")

    # ---- the big farm in the western meadows: house at the back of a walled yard, barn and byre down its sides
    A = (-430, 255, 300)
    yard(*A, "yard_a", -32, -29, 36, 4)
    group(*A, [("f_farm_a", 0, 0, 0), ("f_barn_a", 26, 6, 90), ("f_byre", -24, 14, 270), ("f_wellhouse", 4, -12, 0), ("f_granary", 20, -10, 180)])
    run(*A, "p_wall_field", 8.0, (-34, -30), (-2, -30)); run(*A, "p_wall_field", 8.0, (6, -30), (38, -30))
    run(*A, "p_wall_field", 8.0, (-34, -30), (-34, 2)); run(*A, "p_wall_field", 8.0, (38, -30), (38, -6))
    dress(*A, [("p_gate_piers", 2, -30, 0), ("p_haystack", -20, -20, 0), ("p_haystack", -26, -14, 40), ("p_hay_wagon", -8, -21, 30), ("p_horse_trough", -9, -7, 90),
               ("p_wood_pile", 10.5, -1.6, 0), ("p_wheelbarrow", 13, -14, 200), ("p_crates_barrels", 27, -22, 90), ("p_washing_line", 3, 12, 0),
               ("p_veg_patch", -12, 13, 0), ("p_veg_patch", -12, 18.5, 0), ("p_scarecrow", -8.2, 15.6, 180), ("p_beehives", 15, 28, 180),
               ("p_flower_bed", -4.4, -1.4, 0), ("p_stone_bench", 4.5, -0.8, 0), ("p_tree_pine", -42, -8, 0), ("p_tree_pine", 46, 12, 30)])
    orchard(*A, -8, 24, 4, 3, seed=2)
    # ---- the hop farm east of the river
    Bf = (215, 430, 250)
    yard(*Bf, "yard_b", -29, -27, 38, 4)
    group(*Bf, [("f_farm_b", 0, 0, 0), ("f_barn_b", -22, 8, 270), ("f_beehouse", 20, 16, 40), ("f_oast", 30, -18, 180)])
    run(*Bf, "p_wall_field", 8.0, (-30, -28), (-6, -28)); run(*Bf, "p_wall_field", 8.0, (-30, -28), (-30, -4))
    run(*Bf, "p_fence_picket", 4.0, (-9, -4), (-3, -4)); run(*Bf, "p_fence_picket", 4.0, (3, -4), (9, -4))
    dress(*Bf, [("p_haystack", -20, -18, 0), ("p_hay_wagon", -12, -12, 300), ("p_well", 10, -12, 20), ("p_wood_pile", -8, 11, 90), ("p_flower_bed", -5.2, -1.5, 0),
                ("p_flower_bed", 5.2, -1.5, 0), ("p_veg_patch", 12, 6, 90), ("p_veg_patch", 18, 6, 90), ("p_scarecrow", 15, 3, 200), ("p_washing_line", -2, 14, 0),
                ("p_beehives", 28, 26, 220), ("p_beehives", 31, 21, 250), ("p_wheelbarrow", 22, -8, 100), ("p_crates_barrels", 21, -22, 0), ("p_hand_cart", 38, -10, 60),
                ("p_tree_pine", -40, 4, 0), ("p_pergola", 8, 16, 0)])
    orchard(*Bf, -26, 22, 4, 3, seed=5)
    # ---- the hill farm in the north-west
    Cf = (-760, -250, 20)
    yard(*Cf, "yard_c", -29, -25, 25, 4)
    group(*Cf, [("f_farm_c", 0, 0, 0), ("f_shepherd", 18, 12, 110), ("f_dovecote", -18, -10, 0)])
    run(*Cf, "p_wall_field", 8.0, (-30, -26), (2, -26)); run(*Cf, "p_wall_field", 8.0, (-30, -26), (-30, 6)); run(*Cf, "p_wall_field", 8.0, (10, -26), (26, -26))
    run(*Cf, "p_wall_field", 8.0, (26, -26), (26, -2))
    dress(*Cf, [("p_gate_piers", 6, -26, 0), ("p_haystack", 14, -16, 0), ("p_haystack", 19, -10, 20), ("p_horse_trough", -8, -8, 0), ("p_wood_pile", 8.5, -1.4, 0),
                ("p_well", -8, -17, 0), ("p_veg_patch", -12, 12, 0), ("p_washing_line", 2, 13, 0), ("p_wheelbarrow", -15, 9, 60), ("p_scarecrow", -12, 16.5, 190),
                ("p_stone_bench", -4, -0.9, 0), ("p_tree_pine", 34, 6, 0), ("p_tree_pine", -38, -12, 0), ("p_hay_wagon", 4, -18, 250)])
    # ---- the mills
    Wm = (-70, 560, 315)
    yard(*Wm, "yard_w", 0, 4, 14, None)
    group(*Wm, [("f_windmill", 0, 0, 0)])
    dress(*Wm, [("p_hand_cart", 7, -6, 40), ("p_crates_barrels", -7, -3, 0), ("p_hay_wagon", 12, -14, 300), ("p_wood_pile", -9, 5, 90), ("p_stone_bench", 6.5, -1.5, 0),
                ("p_tree_apple", -15, 12, 0), ("p_tree_apple", -19, 5, 0), ("p_signpost", 3, -18, 0), ("p_haystack", 18, 6, 0)])
    run(*Wm, "p_wall_field", 8.0, (-22, -16), (-6, -16)); run(*Wm, "p_fence_picket", 4.0, (10, 10), (22, 10))
    Pm = (330, 610, 280)
    yard(*Pm, "yard_p", 0, 3, 12, None)
    group(*Pm, [("f_postmill", 0, 0, 0)])
    dress(*Pm, [("p_hand_cart", 6, -5, 320), ("p_crates_barrels", -6, -2, 0), ("p_haystack", -14, 6, 0), ("p_haystack", -18, 0, 0), ("p_wood_pile", 8, 5, 0),
                ("p_tree_pine", 16, 10, 0), ("p_stone_bench", -5, -7, 180), ("p_wheelbarrow", 9, -9, 150)])
    run(*Pm, "p_fence_picket", 4.0, (-12, -12), (4, -12))
    # ---- the inn where the roads cross, and its toll house
    Ri = (-20, 330, 200)
    yard(*Ri, "yard_i", -17, -15, 22, 3)
    group(*Ri, [("f_roadinn", 0, 0, 0), ("f_tollhouse", -26, -12, 200)])
    dress(*Ri, [("p_horse_trough", -9, -3.2, 0), ("p_mounting_block", -5.5, -1.2, 0), ("p_signpost", 10, -9, 0), ("p_tavern_table", 9.5, -3.5, 0), ("p_tavern_table", 13.5, -3.2, 10),
                ("p_hay_wagon", -14, 14, 80), ("p_lamp_timber", 7.4, -1.3, 0), ("p_lamp_timber", -12, -8, 90), ("p_well", 16, 8, 0), ("p_tree_bench", 22, -10, 0),
                ("p_wood_pile", 10, 13, 0), ("p_crates_barrels", -8.5, 12.5, 180), ("p_washing_line", 2, 17, 0), ("p_haystack", -20, 20, 0), ("p_gate_piers", -18, -22, 20),
                ("p_flower_bed", 4.5, -1.3, 0), ("p_veg_patch", 18, 18, 0), ("p_tree_apple", 26, 14, 0), ("p_tree_apple", 30, 20, 0)])
    run(*Ri, "p_wall_field", 8.0, (12, 24), (36, 24)); run(*Ri, "p_wall_field", 8.0, (36, 0), (36, 24))
    # ---- the beacon on the far headland, the shrine in the west, the stilt houses on the south-east shore
    Bc = (-816, -790, 135)
    yard(*Bc, "yard_k", 0, 2, 9, None)
    group(*Bc, [("f_beacon", 0, 0, 0)])
    dress(*Bc, [("p_wood_pile", 6, 2, 90), ("p_wood_pile", 6.4, 6, 80), ("p_stone_bench", -5, -3, 180), ("p_wall_field", -2, -10, 0), ("p_hand_cart", 8, -4, 30)])
    Sh = (-1090, 330, 100)
    yard(*Sh, "yard_s", 0, 0, 11, None)
    group(*Sh, [("f_shrine", 0, 0, 0)])
    dress(*Sh, [("p_stone_bench", -5.5, -6, 200), ("p_stone_bench", 5.5, -6, 160), ("p_flower_bed", -5, -1.4, 0), ("p_flower_bed", 5, -1.4, 0), ("p_tree_cypress", -8, 2, 0),
                ("p_tree_cypress", 8, 2, 0), ("p_tree_cypress", -8, 9, 0), ("p_tree_cypress", 8, 9, 0), ("p_topiary", -3, -9, 0), ("p_topiary", 3, -9, 0), ("p_lamp_iron", 0, -11.5, 0)])
    St = (236, 1124, 190)
    group(*St, [("f_stilt_b", 0, 0, 0), ("f_stilt_a", 12, 3, 20)])
    dress(*St, [("p_boat_upturned", -8, 6, 60), ("p_net_rack", 6, 10, 0), ("p_lobster_pots", -4, 11, 30), ("p_fish_rack", 16, 12, 10), ("p_crates_barrels", 3, 14, 0),
                ("p_wood_pile", -10, 12, 90)])
    return S


def write(sites):
    os.makedirs(OUT, exist_ok=True)
    pend = lambda s, it: s.cat[it["id"]].get("pending")
    json.dump({"towns": [s.layout() for s in sites]}, open(os.path.join(OUT, "layout.json"), "w"), indent=1)
    json.dump({"towns": [s.site() for s in sites]}, open(os.path.join(OUT, "sites.json"), "w"))
    os.makedirs(os.path.join(ROOT, "art", "town"), exist_ok=True)
    for s in sites:
        s.plan(os.path.join(ROOT, "art", "town", f"plan_{s.id}.png"), scale=0.6 if s.id == "fields" else 3.0)
        print(f"{s.id}: {len(s.lots)} buildings and {len(s.deco)} props placed ({sum(1 for it in s.items if pend(s, it))} still to be modelled), "
              f"{sum(1 for l in s.lots if s.cat[l['id']]['pads'])} with landing places; not placed: {sorted(set(s.missing)) or 'none'}")


def base_terrain():
    """The island as the bake left it (art/terrain_base, once tools/town/fit_terrain.py has run): streets are
    planned on that, not on ground the last fit already reshaped."""
    T = Terrain()
    base = os.path.join(ROOT, "art", "terrain_base")
    try:
        m = json.load(open(os.path.join(base, "meta.json")))
        h = np.fromfile(os.path.join(base, "height.u16"), dtype="<u2").reshape(m["n"], m["n"]).astype(np.float32)
        T.h = m["hMin"] + (m["hMax"] - m["hMin"]) * h / 65535.0
    except OSError:
        pass
    return T


if __name__ == "__main__":
    cat = with_briefs(catalogue())
    T = base_terrain()
    print(sum(1 for c in cat.values() if not c.get("pending")), "models built,", sum(1 for c in cat.values() if c.get("pending")), "pending")
    write([larkhaven(cat, T), cairnwick(cat, T), fields(cat, T)])
