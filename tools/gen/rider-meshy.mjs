// Rider: concept views -> Meshy multi-image-to-3D (Meshy 7.1 Ultra geometry + PBR textures).
// Resumable: the task id is checkpointed in art/meshy/tasks.json.
// Usage: node tools/gen/rider-meshy.mjs [variant]
import path from "node:path";
import { meshy, meshyPoll, meshyDownload, falUpload, ROOT, checkpoint } from "./lib.mjs";

const variant = process.argv[2] || "a";
const OUT = path.join(ROOT, "art", "meshy", `rider_${variant}`);
const cp = checkpoint(path.join(ROOT, "art", "meshy", "tasks.json"));
const concept = (n) => path.join(ROOT, "art", "concept", `rider_${n}.png`);

const VARIANTS = {
  // all four views, first = front
  a: { views: ["front", "side", "back", "top34"], body: {} },
  // side-led (the profile is the cleanest, least foreshortened view)
  b: { views: ["side", "back", "top34", "front"], body: {} },
};
const v = VARIANTS[variant];

let id = cp.get(`rider_${variant}`);
if (!id) {
  const urls = [];
  for (const n of v.views) {
    let u = cp.get(`url:${n}`);
    if (!u) { u = await falUpload(concept(n)); await cp.set(`url:${n}`, u); }
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
      target_polycount: 110000,
      image_enhancement: false,
      pose_mode: "",
      target_formats: ["glb"],
      multi_view_thumbnails: true,
      ...v.body,
    }),
  });
  id = result;
  await cp.set(`rider_${variant}`, id);
  console.log(`rider_${variant}: task ${id}`);
}
const task = await meshyPoll("/openapi/v1/multi-image-to-3d", id, `rider_${variant}`);
if (task.status !== "SUCCEEDED") {
  console.error(`FAILED: ${task.status} ${task.task_error?.message ?? ""}`);
  process.exit(1);
}
await meshyDownload(task, OUT, "rider");
for (const [k, url] of Object.entries(task.thumbnail_urls || {})) {
  const { download } = await import("./lib.mjs");
  if (url) await download(url, path.join(OUT, `thumb_${k}.png`));
}
console.log("RIDER DONE", task.consumed_credits ?? "");
