#!/usr/bin/env python3
"""Pack the towns' PATINA materials into game textures, with a per-material grade so they sit in
the game's palette:
   assets/town/tex/<name>_c.webp   RGB = base colour (sRGB), A = height
   assets/town/tex/<name>_n.webp   RG = normal xy, B = roughness
   assets/town/tex/materials.json  order (= layer index in the shader's texture array), tile size in
                                   metres, mean linear colour
Usage: tools/.venv/bin/python tools/town/pack_textures.py
"""
import json, os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "art", "textures", "town")
OUT = os.path.join(ROOT, "assets", "town", "tex")
os.makedirs(OUT, exist_ok=True)
S = 512

# layer order is the material id used by tools/town/kit.py and src/world/town.js: keep in step
#          name        tile (m)  saturation  gain   tint (multiplied, sRGB-ish)   contrast
MATERIALS = [
    ("masonry",   2.6, 0.34, 0.98, (0.97, 0.97, 0.96), 1.05),
    ("ashlar",    3.0, 0.80, 0.90, (1.00, 0.97, 0.90), 1.10),
    ("plaster",   3.2, 0.55, 0.97, (1.00, 0.99, 0.97), 1.60),
    ("timber",    1.6, 0.85, 0.80, (1.00, 0.93, 0.84), 1.05),
    ("planks",    1.8, 0.60, 1.05, (1.00, 0.98, 0.94), 1.05),
    ("slate",     2.4, 0.22, 0.95, (0.95, 0.98, 1.03), 1.05),
    ("tiles",     2.4, 0.82, 0.90, (1.00, 0.95, 0.90), 1.00),
    ("thatch",    2.2, 0.58, 0.92, (1.00, 0.97, 0.90), 1.05),
    ("shingle",   2.2, 0.80, 0.90, (1.00, 0.98, 0.94), 1.00),
    ("brick",     2.2, 0.62, 0.84, (1.00, 0.95, 0.90), 1.00),
    ("cobble",    2.8, 0.60, 0.88, (1.00, 0.98, 0.95), 1.05),
    ("flagstone", 3.6, 0.55, 0.88, (1.00, 0.98, 0.94), 1.10),
    ("ivy",       2.0, 0.72, 1.35, (0.98, 1.00, 0.90), 0.95),
]


def srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


meta = {"order": [m[0] for m in MATERIALS], "size": S, "tile": {}, "mean": {}}
for name, tile, sat, gain, tint, contrast in MATERIALS:
    d = os.path.join(SRC, name)
    col = np.asarray(Image.open(os.path.join(d, "basecolor.png")).convert("RGB").resize((S, S), Image.LANCZOS)).astype(np.float32) / 255
    hgt = np.asarray(Image.open(os.path.join(d, "height.png")).convert("L").resize((S, S), Image.LANCZOS)).astype(np.float32)
    nrm = np.asarray(Image.open(os.path.join(d, "normal.png")).convert("RGB").resize((S, S), Image.LANCZOS)).astype(np.float32)
    rgh = np.asarray(Image.open(os.path.join(d, "roughness.png")).convert("L").resize((S, S), Image.LANCZOS)).astype(np.float32)
    # grade: saturation about the luma, contrast about the mean, gain, tint
    luma = (col * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    col = luma + (col - luma) * sat
    mean = col.mean((0, 1), keepdims=True)
    col = mean + (col - mean) * contrast
    col = np.clip(col * gain * np.array(tint, np.float32), 0, 1)
    lo, hi = np.percentile(hgt, [1, 99])
    hgt = np.clip((hgt - lo) / max(hi - lo, 1e-3), 0, 1)
    c = np.dstack([col, hgt]) * 255
    n = np.dstack([nrm[..., 0], nrm[..., 1], rgh])
    Image.fromarray(c.round().clip(0, 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, f"{name}_c.webp"), quality=92, method=6, exact=True)
    Image.fromarray(n.round().clip(0, 255).astype(np.uint8), "RGB").save(os.path.join(OUT, f"{name}_n.webp"), quality=93, method=6)
    lin = srgb_to_lin(col).reshape(-1, 3).mean(0)
    meta["tile"][name] = tile
    meta["mean"][name] = [round(float(v), 4) for v in lin]
    print(f"{name:10s} tile {tile} m  mean lin {meta['mean'][name]}  rough {rgh.mean() / 255:.2f}")
json.dump(meta, open(os.path.join(OUT, "materials.json"), "w"), indent=1)
print("packed", len(MATERIALS), "materials ->", os.path.relpath(OUT, ROOT),
      "%.2f MB" % (sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)) / 1e6))
