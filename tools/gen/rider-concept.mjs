// Generate the rider concept art (an original broom-riding courier witch) with fal,
// then extra views for Meshy multi-image-to-3D.
// Usage: node tools/gen/rider-concept.mjs [main|views]
import path from "node:path";
import fs from "node:fs";
import { fal, falUpload, download, ROOT, checkpoint } from "./lib.mjs";

const OUT = path.join(ROOT, "art", "concept");
const cp = checkpoint(path.join(OUT, "tasks.json"));
const step = process.argv[2] || "main";

const CHARACTER =
  "an original young courier-witch character: she wears a short marigold-yellow travel capelet over a cream linen blouse, " +
  "a wide-brimmed pointed witch hat in deep plum purple with a cream ribbon band and a tiny sprig of white wildflowers tucked in it, " +
  "dark teal trousers, laced chestnut-brown leather ankle boots, fingerless gloves, " +
  "a tan leather satchel with brass buckles and a rolled moss-green blanket strapped on her back, " +
  "chestnut-brown hair tied in one short thick braid. " +
  "She rides a rustic wooden broomstick: a long slightly crooked pale wood handle and a big bushy golden straw bristle head bound with dark cord, " +
  "with a small brass lantern hanging on a short chain under the front tip of the handle";

const POSE =
  "Dynamic flying pose: she sits astride the broom leaning far forward, both hands gripping the handle in front of her, " +
  "knees bent, feet tucked back and resting near the bristle binding, chin up, looking ahead";

const STYLE =
  "High-end stylized 3D character render in the style of a modern animated feature film, soft appealing shapes, " +
  "clean readable materials, hand-painted texture feel, slightly exaggerated proportions (big hat, small figure). " +
  "Neutral flat even studio lighting with no cast shadows and no rim light, plain solid light-gray background, " +
  "no ground plane, no motion blur, no wind effects, no particles, no text, no watermark. " +
  "The entire character and the entire broom from handle tip to bristle ends are fully inside the frame with margin on all sides.";

const VIEWS = {
  main: `${STYLE}\n\nSubject: ${CHARACTER}. ${POSE}.\n\nCamera: exact side profile view, the broom is horizontal and points to the left, orthographic-like long lens.`,
};

async function gen(name, prompt, extra = {}) {
  const out = path.join(OUT, `rider_${name}.png`);
  if (fs.existsSync(out)) { console.log(`${name}: exists`); return out; }
  const res = await fal("fal-ai/nano-banana-pro", {
    prompt, num_images: 1, aspect_ratio: "16:9", resolution: "2K", output_format: "png", ...extra,
  }, { label: `concept/${name}` });
  await download(res.images[0].url, out);
  return out;
}

async function edit(name, prompt, sources) {
  const out = path.join(OUT, `rider_${name}.png`);
  if (fs.existsSync(out)) { console.log(`${name}: exists`); return out; }
  const urls = [];
  for (const s of sources) {
    let u = cp.get(`upload:${path.basename(s)}`);
    if (!u) { u = await falUpload(s); await cp.set(`upload:${path.basename(s)}`, u); }
    urls.push(u);
  }
  const res = await fal("fal-ai/nano-banana-pro/edit", {
    prompt, image_urls: urls, num_images: 1, aspect_ratio: "1:1", resolution: "2K", output_format: "png",
  }, { label: `concept/${name}` });
  await download(res.images[0].url, out);
  return out;
}

if (step === "main") {
  await gen("side", VIEWS.main);
} else if (step === "views") {
  const side = path.join(OUT, "rider_side.png");
  const base =
    "This is a turnaround sheet task. Image 1 shows a 3D character on a broomstick from the side. " +
    "Render the EXACT same character, same outfit, same colors, same proportions, same broom and the exact same frozen pose, " +
    "as if the camera orbited around a static 3D statue. Same neutral flat even lighting, same plain solid light-gray background, " +
    "no cast shadows, no ground, no motion blur, no text. Entire character and broom fully in frame with margin.";
  await Promise.all([
    edit("back", `${base}\n\nNew camera: directly behind the character looking forward along the broom (rear view). We see the bushy straw bristle head closest to camera at the bottom, her back with the leather satchel and rolled green blanket, the yellow capelet, the braid, and the back of the wide plum hat. The broom handle points straight away from the camera.`, [side]),
    edit("front", `${base}\n\nNew camera: directly in front of the character looking back along the broom (front view). We see the front tip of the broom handle with the small hanging brass lantern closest to camera, her face under the wide plum hat brim, her hands gripping the handle, the yellow capelet; the straw bristles are behind her, mostly hidden.`, [side]),
    edit("top34", `${base}\n\nNew camera: elevated three-quarter rear view from above and behind-left (about 35 degrees above horizontal, 40 degrees to the left of straight behind). We see the top of the wide plum hat, the yellow capelet, the satchel and blanket on her back, and the full length of the broom receding diagonally.`, [side]),
  ]);
}
console.log("done");
