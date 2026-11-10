#!/usr/bin/env python3
"""Process the generated western pieces (art/places/meshy/<name>/<name>.glb) into game assets
(assets/places/west/<name>.glb + .json), with a preview each in art/places/previews/.

    tools/.venv/bin/python tools/places/west_models.py [name ...]

The plants and cloth are made by tools/blender/place_flora_west.py instead.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glbpack

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLENDER = os.environ.get("BLENDER", "/Applications/Blender.app/Contents/MacOS/Blender")

PIECES = {
    # heroes
    "blossom_tree":    dict(size=9.5, tris=15000, tex=1024, leaf="pink", extra={"sway": 1.0, "foliage": 0.45}),
    "wisteria_bridge": dict(size=13.5, fit="w", tris=15000, tex=1024, align="x", origin="box", discs="grid:1.1", leaf="purple", swaymode="leaf", leaf_from=0.0, back=1, extra={"sway": 0.6, "foliage": 0.8}),
    "ship_mast":       dict(size=15.0, tris=14000, tex=1024),
    "flower_boat":     dict(size=5.4, fit="w", tris=11000, tex=1024, align="x", origin="box", sink=0.22, discs="grid:0.9"),
    "sundial":         dict(size=4.6, fit="w", tris=9000, tex=1024),
    "stone_hand":      dict(size=8.5, tris=15000, tex=1024, discs="grid:1.2", back=1),
    # dressing
    "stone_lamp":      dict(size=2.4, tris=2600, tex=512, extra={"glow": [1.0, 0.62, 0.25, 3.4], "glowKey": "amber"}),
    "anchor":          dict(size=2.7, tris=4000, tex=512, sink=0.2),
    "glass_floats":    dict(size=1.9, fit="w", tris=4500, tex=512, extra={"glow": [0.45, 1.0, 0.85, 0.9], "glowKey": "teal"}),
    # treasures (floating: sized by their longest dimension)
    "teacup":          dict(size=0.85, fit="max", tris=4500, tex=512),
    "thimble":         dict(size=0.70, fit="max", tris=5000, tex=512),
    "whistle":         dict(size=0.90, fit="max", tris=4000, tex=512),
    "tide_knot":       dict(size=0.95, fit="max", tris=4500, tex=512),
    "hourglass":       dict(size=0.90, fit="max", tris=4500, tex=512),
    "storm_marble":    dict(size=0.80, fit="max", tris=4000, tex=512),
}

names = sys.argv[1:] or list(PIECES)
for name in names:
    o = dict(PIECES[name])
    src = os.path.join(ROOT, "art", "places", "meshy", name, f"{name}.glb")
    if not os.path.exists(src):
        print(f"{name}: no source yet ({src})"); continue
    args = []
    for k, v in o.items():
        args.append(f"{k}={json.dumps(v) if isinstance(v, (dict, list)) else v}")
    cmd = [BLENDER, "-b", "-P", os.path.join(ROOT, "tools", "blender", "place_process.py"), "--", src,
           os.path.join(ROOT, "assets", "places", "west", f"{name}.glb"), os.path.join(ROOT, "art", "places", "previews", f"{name}.png"), *args]
    out = subprocess.run(cmd, capture_output=True, text=True)
    lines = [l for l in out.stdout.splitlines() if l.startswith("EXPORTED") or "Error" in l or "Traceback" in l]
    print("\n".join(lines) if lines else f"{name}: FAILED\n{out.stdout[-1500:]}\n{out.stderr[-1500:]}")
    # quantize the vertex data (needs numpy: run this script with tools/.venv/bin/python)
    dst = os.path.join(ROOT, "assets", "places", "west", f"{name}.glb")
    if lines and os.path.exists(dst):
        r = glbpack.pack(dst)
        if r: print(f"   packed {r[0] / 1e6:.2f} -> {r[1] / 1e6:.2f} MB, {r[2][0]} -> {r[2][1]} vertices")
