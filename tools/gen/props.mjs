// World props: concept art (fal) -> Meshy image-to-3D. Resumable through art/meshy/tasks.json.
// Usage: node tools/gen/props.mjs [name ...]
import path from "node:path";
import fs from "node:fs";
import { fal, falUpload, download, meshy, meshyPoll, meshyDownload, ROOT, checkpoint } from "./lib.mjs";

const CONCEPT = path.join(ROOT, "art", "concept");
const cp = checkpoint(path.join(ROOT, "art", "meshy", "tasks.json"));

const STYLE =
  "High-end stylized 3D asset render in the style of a modern animated feature film: soft appealing shapes, " +
  "clean readable forms, hand-painted texture feel with rich natural detail. A single isolated object, complete and " +
  "fully inside the frame with margin on all sides, seen from a slightly elevated three-quarter view. " +
  "Neutral flat even studio lighting with no cast shadows, plain solid light-gray background, no ground plane, " +
  "no grass, no scenery, no people, no text, no watermark.";

const PROPS = {
  lighthouse: {
    prompt:
      "A small old sea lighthouse: a slightly tapered round whitewashed stone tower about four storeys tall with one " +
      "broad faded-red band around its middle, a few small deep-set windows, a black iron gallery railing, a glass " +
      "lantern room with a red conical roof topped by a tiny brass weathervane, an arched blue wooden door at the base, " +
      "and a low attached stone keeper's hut with a mossy slate roof and a stubby chimney. It stands on a low round " +
      "plinth of dark rough-cut stones. Weathered paint, lichen, storybook charm.",
    meshy: { geometry_resolution: "2k", target_polycount: 60000, texture_resolution: "4k" },
  },
  boulders: {
    prompt:
      "A cluster of three weathered grey granite boulders of clearly different sizes resting against each other, " +
      "natural rounded-angular shapes with cracks, partly covered with thick green moss on top and pale yellow-grey lichen patches.",
    meshy: { target_polycount: 14000 },
  },
  menhir: {
    prompt:
      "A single tall ancient standing stone (menhir): a rough slab of grey granite about three times taller than wide, " +
      "leaning very slightly, top worn and uneven, patches of orange and pale lichen, moss creeping up from the base, " +
      "a faint weathered spiral carving low on one face.",
    meshy: { target_polycount: 9000 },
  },
  tree: {
    prompt:
      "A lone wind-swept hawthorn tree shaped by sea gales: a short gnarled twisted dark trunk leaning strongly to one " +
      "side, branches streaming the same way, carrying a flattened wedge-shaped canopy made of dense chunky clumps of " +
      "small deep-green leaves dotted with tiny white blossoms. Exposed roots at the base.",
    meshy: { target_polycount: 30000 },
  },
};

const want = process.argv.slice(2);
const names = want.length ? want : Object.keys(PROPS);

await Promise.all(names.map(async (name) => {
  const def = PROPS[name];
  const img = path.join(CONCEPT, `prop_${name}.png`);
  if (!fs.existsSync(img)) {
    const res = await fal("fal-ai/nano-banana-pro", {
      prompt: `${STYLE}\n\nSubject: ${def.prompt}`, num_images: 1, aspect_ratio: "1:1", resolution: "2K", output_format: "png",
    }, { label: `concept/${name}` });
    await download(res.images[0].url, img);
  }
  const out = path.join(ROOT, "art", "meshy", name);
  if (fs.existsSync(path.join(out, `${name}.glb`))) { console.log(`${name}: model exists`); return; }
  let id = cp.get(`prop_${name}`);
  if (!id) {
    let url = cp.get(`url:prop_${name}`);
    if (!url) { url = await falUpload(img); await cp.set(`url:prop_${name}`, url); }
    const { result } = await meshy("/openapi/v1/image-to-3d", {
      method: "POST",
      body: JSON.stringify({
        image_url: url,
        ai_model: "meshy-7.1",
        geometry_resolution: "standard",
        should_texture: true,
        enable_pbr: true,
        texture_resolution: "2k",
        should_remesh: true,
        topology: "triangle",
        target_polycount: 20000,
        image_enhancement: false,
        target_formats: ["glb"],
        ...def.meshy,
      }),
    });
    id = result;
    await cp.set(`prop_${name}`, id);
    console.log(`${name}: task ${id}`);
  }
  const task = await meshyPoll("/openapi/v1/image-to-3d", id, name);
  if (task.status !== "SUCCEEDED") { console.error(`${name} FAILED: ${task.status} ${task.task_error?.message ?? ""}`); return; }
  await meshyDownload(task, out, name);
  console.log(`${name}: done (${task.consumed_credits ?? "?"} credits)`);
}));
console.log("PROPS DONE");
