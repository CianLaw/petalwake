#!/usr/bin/env python3
"""One sheet of every building's preview: art/town/catalogue_<n>.jpg (pages of 12).
    tools/.venv/bin/python tools/town/catalogue.py [prefix ...]
"""
import glob, json, os, sys
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRE = os.path.join(ROOT, "art", "town", "preview")
want = sys.argv[1:]
files = sorted(f for f in glob.glob(os.path.join(PRE, "*.jpg")) if not os.path.basename(f).startswith("_") and (not want or any(os.path.basename(f).startswith(w) for w in want)))
TW, TH, COLS, ROWS = 560, 280, 3, 4
for page in range(0, len(files), COLS * ROWS):
    sheet = Image.new("RGB", (TW * COLS, TH * ROWS), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for k, f in enumerate(files[page:page + COLS * ROWS]):
        im = Image.open(f).convert("RGB").resize((TW, TH), Image.LANCZOS)
        x, y = (k % COLS) * TW, (k // COLS) * TH
        sheet.paste(im, (x, y))
        bid = os.path.splitext(os.path.basename(f))[0]
        try:
            info = json.load(open(os.path.join(ROOT, "art", "town", "build", bid + ".json")))
            label = f"{bid}  {info['tris'][2]} tris  {'PAD' if info['pads'] else ''}"
        except Exception:
            label = bid
        d.rectangle([x, y, x + 8 * len(label) + 8, y + 16], fill=(0, 0, 0))
        d.text((x + 4, y + 2), label, fill=(255, 255, 0))
    out = os.path.join(ROOT, "art", "town", f"catalogue_{'_'.join(want) or 'all'}_{page // (COLS * ROWS)}.jpg")
    sheet.save(out, quality=86)
    print(out)
