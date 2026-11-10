// Seamless PBR ground/rock materials via fal PATINA.
// Usage: node tools/gen/textures.mjs [name ...]   (default: all missing)
import path from "node:path";
import fs from "node:fs";
import { fal, download, ROOT } from "./lib.mjs";

const OUT = path.join(ROOT, "art", "textures");
const MAPS = ["basecolor", "normal", "roughness", "height"];

const MATERIALS = {
  cliff:
    "seamless tileable photorealistic sea cliff rock wall seen straight on, strongly layered horizontal sedimentary strata, " +
    "thin stacked beds of dark charcoal shale alternating with thicker weathered grey-brown sandstone, " +
    "horizontal ledges, fine vertical fractures, crumbling edges, deep crisp relief, overcast neutral lighting, no vegetation, no sky",
  rock:
    "seamless tileable photorealistic weathered grey coastal rock surface seen from directly above, " +
    "rough fractured stone with cracks, pits and small lichen flecks, neutral overcast lighting, strong crisp relief",
  scree:
    "seamless tileable photorealistic mountain scree seen from directly above, loose angular grey and tan stones and gravel " +
    "of mixed sizes packed together, neutral overcast lighting, crisp relief",
  ground:
    "seamless tileable photorealistic meadow floor seen from directly above, dense short green grass and clover with a little " +
    "dry straw thatch and tiny leaves, even coverage, soft neutral overcast lighting, no flowers, no shadows",
  sand:
    "seamless tileable photorealistic pale golden beach sand seen from directly above, fine grains with soft shallow wind ripples " +
    "and a few tiny shell fragments, neutral overcast lighting",
  pebbles:
    "seamless tileable photorealistic wet beach shingle seen from directly above, smooth rounded dark grey, slate blue and " +
    "rust-brown pebbles of mixed sizes tightly packed, neutral overcast lighting, crisp relief",
};

const want = process.argv.slice(2);
const names = (want.length ? want : Object.keys(MATERIALS)).filter(
  (n) => want.length || !fs.existsSync(path.join(OUT, n, "basecolor.png")),
);

await Promise.all(names.map(async (name, i) => {
  const res = await fal("fal-ai/patina/material", {
    prompt: MATERIALS[name],
    image_size: "square_hd",
    num_inference_steps: 8,
    seed: 1200 + i * 7,
    num_images: 1,
    enable_prompt_expansion: false,
    enable_safety_checker: true,
    tiling_mode: "both",
    tile_size: 128,
    tile_stride: 64,
    maps: MAPS,
    output_format: "png",
    upscale_factor: 0,
  }, { label: `tex/${name}` });
  for (const img of res.images ?? []) {
    const kind = img.map_type ?? "basecolor";
    await download(img.url, path.join(OUT, name, `${kind}.png`));
  }
}));
console.log("textures done:", names.join(", ") || "(nothing to do)");
