// Seamless PBR materials for the towns' buildings and streets, via fal PATINA.
// Usage: node tools/gen/town-textures.mjs [name ...]   (default: all missing)   -> art/textures/town/<name>/
import path from "node:path";
import fs from "node:fs";
import { fal, download, ROOT } from "./lib.mjs";

const OUT = path.join(ROOT, "art", "textures", "town");
const MAPS = ["basecolor", "normal", "roughness", "height"];
const FLAT = "flat even overcast lighting, no cast shadows, no perspective, no objects, no vegetation";

const MATERIALS = {
  masonry:
    "seamless tileable old rubble stone wall seen straight on, chunky irregular warm honey-coloured sandstone blocks of mixed sizes " +
    "with softly rounded worn edges, laid in rough horizontal courses, pale lime mortar joints slightly recessed, a few darker and " +
    "paler stones, gently stylised like a hand-built storybook village wall, " + FLAT,
  ashlar:
    "seamless tileable wall of large dressed pale cream limestone blocks seen straight on, regular horizontal courses of long and " +
    "short rectangular blocks with worn softly rounded edges, thin recessed joints, subtle weathering and warm staining, " + FLAT,
  plaster:
    "seamless tileable old hand-trowelled lime plaster wall seen straight on, warm off-white, gently uneven surface with soft " +
    "trowel sweeps, faint hairline cracks and very subtle weather staining, mostly plain, " + FLAT,
  timber:
    "seamless tileable extreme close-up of the face of one single huge old oak beam filling the whole image, one continuous " +
    "piece of dark brown weathered wood with no joints and no separate boards, long straight grain lines running left to right, " +
    "shallow adze marks, fine cracks along the grain, a few small knots, " + FLAT,
  planks:
    "seamless tileable wall of weathered pale grey-brown wooden boards seen straight on, vertical planks of slightly different " +
    "widths with narrow dark gaps between them, fine vertical grain, a few knots, unpainted, " + FLAT,
  slate:
    "seamless tileable roof of thick dark blue-grey slate shingles seen straight on, regular horizontal rows of chunky rectangular " +
    "slates with slightly uneven bottom edges and a staggered bond, each row overlapping the one below, subtle colour variation " +
    "from charcoal to blue-grey, a little lichen, " + FLAT,
  tiles:
    "seamless tileable roof of old terracotta clay tiles seen straight on, regular horizontal rows of flat round-ended beaver-tail " +
    "tiles in a staggered bond, each row overlapping the one below, warm orange and red with some sun-bleached and some darker " +
    "tiles, chunky and slightly uneven, " + FLAT,
  thatch:
    "seamless tileable golden straw thatched roof seen straight on, dense combed reed and straw running vertically, soft and " +
    "thick, warm wheat colour with slightly darker weathered streaks, " + FLAT,
  shingle:
    "seamless tileable wall of weathered silver-grey wooden shingles seen straight on, regular horizontal rows of hand-split " +
    "rectangular cedar shakes with uneven bottom edges in a staggered bond, " + FLAT,
  brick:
    "seamless tileable old soft red brick wall seen straight on, hand-made bricks with rounded worn edges in a running bond, " +
    "warm red and orange with a few darker headers, pale sandy mortar, " + FLAT,
  cobble:
    "seamless tileable old cobblestone street seen from directly above, rounded warm grey and tan stones of mixed sizes tightly " +
    "packed with sandy joints, worn smooth, gently stylised storybook village paving, " + FLAT,
  flagstone:
    "seamless tileable paving of large irregular pale sandstone flagstones seen from directly above, worn smooth slabs of mixed " +
    "shapes fitted together with narrow sandy joints and a little moss in the gaps, " + FLAT,
  ivy:
    "seamless tileable dense wall of small glossy green ivy leaves seen straight on, overlapping heart-shaped leaves completely " +
    "covering the surface, fresh mid green with some lighter young leaves, " + FLAT,
};

const want = process.argv.slice(2);
const names = (want.length ? want : Object.keys(MATERIALS)).filter(
  (n) => want.length || !fs.existsSync(path.join(OUT, n, "basecolor.png")),
);

await Promise.all(names.map(async (name) => {
  const i = Object.keys(MATERIALS).indexOf(name);
  const res = await fal("fal-ai/patina/material", {
    prompt: MATERIALS[name],
    image_size: "square_hd",
    num_inference_steps: 8,
    seed: 4100 + i * 13 + Number(process.env.SEED_SHIFT || 0),
    num_images: 1,
    enable_prompt_expansion: false,
    enable_safety_checker: true,
    tiling_mode: "both",
    tile_size: 128,
    tile_stride: 64,
    maps: MAPS,
    output_format: "png",
    upscale_factor: 0,
  }, { label: `town/${name}` });
  for (const img of res.images ?? []) {
    const kind = img.map_type ?? "basecolor";
    await download(img.url, path.join(OUT, name, `${kind}.png`));
  }
}));
console.log("town textures done:", names.join(", ") || "(nothing to do)");
