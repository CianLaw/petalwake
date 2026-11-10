#!/usr/bin/env python3
"""Pack the PATINA materials into game textures:
   <name>_c.webp  RGB = base colour (sRGB), A = height
   <name>_n.webp  RG = normal xy, B = roughness
and write assets/textures/materials.json with each material's mean linear colour."""
import json, os, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "art", "textures")
OUT = os.path.join(ROOT, "assets", "textures")
os.makedirs(OUT, exist_ok=True)
ORDER = ["cliff", "rock", "scree", "ground", "sand", "pebbles"]
S = 1024

def srgb_to_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

meta = {"order": ORDER, "size": S, "mean": {}}
for name in ORDER:
    d = os.path.join(SRC, name)
    col = np.asarray(Image.open(os.path.join(d, "basecolor.png")).convert("RGB").resize((S, S), Image.LANCZOS)).astype(np.float32)
    hgt = np.asarray(Image.open(os.path.join(d, "height.png")).convert("L").resize((S, S), Image.LANCZOS)).astype(np.float32)
    nrm = np.asarray(Image.open(os.path.join(d, "normal.png")).convert("RGB").resize((S, S), Image.LANCZOS)).astype(np.float32)
    rgh = np.asarray(Image.open(os.path.join(d, "roughness.png")).convert("L").resize((S, S), Image.LANCZOS)).astype(np.float32)
    # stretch height to the full range so height-blending has contrast
    lo, hi = np.percentile(hgt, [1, 99])
    hgt = np.clip((hgt - lo) / max(hi - lo, 1e-3), 0, 1) * 255.0
    c = np.dstack([col, hgt]).round().clip(0, 255).astype(np.uint8)
    n = np.dstack([nrm[..., 0], nrm[..., 1], rgh]).round().clip(0, 255).astype(np.uint8)
    Image.fromarray(c, "RGBA").save(os.path.join(OUT, f"{name}_c.webp"), quality=93, method=6, exact=True)
    Image.fromarray(n, "RGB").save(os.path.join(OUT, f"{name}_n.webp"), quality=94, method=6)
    lin = srgb_to_lin(col).reshape(-1, 3).mean(0)
    meta["mean"][name] = [round(float(v), 4) for v in lin]
    print(name, "mean lin", meta["mean"][name], "rough mean", round(float(rgh.mean() / 255), 3))
json.dump(meta, open(os.path.join(OUT, "materials.json"), "w"), indent=1)
