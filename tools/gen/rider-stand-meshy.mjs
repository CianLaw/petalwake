// Standing rider: concept views -> Meshy multi-image-to-3D (Meshy 7.1 geometry + PBR textures).
// The same request as tools/gen/rider-meshy.mjs, with the standing views from
// tools/gen/rider-stand-concept.mjs and a lower triangle target (see TARGET_TRIS).
// Resumable: the task id is checkpointed in art/meshy/rider_stand/tasks.json, so a re-run polls and
// downloads the same task instead of spending credits again.
// Usage: node --env-file=<file with MESHY_API_KEY> tools/gen/rider-stand-meshy.mjs [variant]
//   variant "a" (default) writes to art/meshy/rider_stand/, any other one to art/meshy/rider_stand/<variant>/
import path from "node:path";
import fs from "node:fs";
import { meshy, meshyPoll, meshyDownload, falUpload, download, ROOT, checkpoint } from "./lib.mjs";

const variant = process.argv[2] || "a";
const BASE = path.join(ROOT, "art", "meshy", "rider_stand");
const OUT = variant === "a" ? BASE : path.join(BASE, variant);
const cp = checkpoint(path.join(BASE, "tasks.json"));
const concept = (n) => path.join(ROOT, "art", "concept", `stand_${n}.png`);

// The game asset has to stay under 8 MB with the seated rider's vertex layout (64 bytes a vertex:
// position, normal, tangent, uv, _WIND). Meshy's UV atlas splits about 1.17 vertices per triangle,
// so a triangle costs about 87 bytes and 2K WebP textures about 1.1 MB: roughly 75k triangles fit.
// Meshy lands within a few percent of the target, hence 72k.
const TARGET_TRIS = 72000;

const VARIANTS = {
  // front first, then her right profile, the back, and the view from above and behind-left
  a: { views: ["front", "side", "back", "34"], body: {} },
  // only for a retry after a clearly bad result: the three orthogonal views alone
  b: { views: ["front", "side", "back"], body: {} },
};
const v = VARIANTS[variant];
if (!v) throw new Error(`unknown variant "${variant}" (${Object.keys(VARIANTS).join(", ")})`);

let id = cp.get(`rider_stand_${variant}`);
if (!id) {
  const urls = [];
  for (const n of v.views) {
    const file = concept(n);
    const st = fs.statSync(file);
    const key = `url:${n}:${st.size}:${Math.round(st.mtimeMs)}`; // a regenerated view is uploaded again
    let u = cp.get(key);
    if (!u) { u = await falUpload(file); await cp.set(key, u); }
    urls.push(u);
  }
  const { result } = await meshy("/openapi/v1/multi-image-to-3d", {
    method: "POST",
    body: JSON.stringify({
      image_urls: urls,
      ai_model: "meshy-7.1",
      geometry_resolution: "2k",
      should_texture: true,
      texture_model: "meshy-7",
      enable_pbr: true,
      texture_resolution: "4k",
      should_remesh: true,
      topology: "triangle",
      target_polycount: TARGET_TRIS,
      image_enhancement: false,
      pose_mode: "",
      target_formats: ["glb"],
      multi_view_thumbnails: true,
      ...v.body,
    }),
  });
  id = result;
  await cp.set(`rider_stand_${variant}`, id);
  console.log(`rider_stand_${variant}: task ${id}`);
}
const task = await meshyPoll("/openapi/v1/multi-image-to-3d", id, `rider_stand_${variant}`);
if (task.status !== "SUCCEEDED") {
  console.error(`FAILED: ${task.status} ${task.task_error?.message ?? ""}`);
  process.exit(1);
}
await meshyDownload(task, OUT, "rider_stand");
for (const [k, url] of Object.entries(task.thumbnail_urls || {})) {
  if (url) await download(url, path.join(OUT, `thumb_${k}.png`));
}
console.log("RIDER STAND DONE", task.consumed_credits ?? "");
