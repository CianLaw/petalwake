// Hero pieces, dressing and treasures for the six western places: concept art (fal) -> Meshy
// image-to-3D. Resumable through art/places/tasks-west.json.
// Usage: node tools/gen/places-west.mjs concept [name ...]     concept images only (look at them first)
//        node tools/gen/places-west.mjs mesh [name ...]        Meshy, for pieces that have a concept
//        node tools/gen/places-west.mjs redo <name>            throw a concept away and draw it again
import path from "node:path";
import fs from "node:fs";
import { fal, falUpload, download, meshy, meshyPoll, meshyDownload, ROOT, checkpoint } from "./lib.mjs";

const OUT = path.join(ROOT, "art", "places");
const CONCEPT = path.join(OUT, "concept");
const cp = checkpoint(path.join(OUT, "tasks-west.json"));

const STYLE =
  "High-end stylized 3D asset render in the style of a modern animated feature film: soft appealing shapes, " +
  "clean readable forms, hand-painted texture feel with rich natural detail. A single isolated object, complete and " +
  "fully inside the frame with margin on all sides, seen from a slightly elevated three-quarter view. " +
  "Neutral flat even studio lighting with no cast shadows, plain solid light-gray background, no ground plane, " +
  "no grass, no scenery, no people, no text, no watermark.";

export const PIECES = {
  // ---- The Blossom Sister (a sea stack)
  blossom_tree: {
    prompt:
      "An ancient weather-twisted cherry tree in full bloom: a thick gnarled dark trunk that corkscrews and leans to one " +
      "side, heavy exposed roots splayed wide as if gripping bare rock, and a broad layered cloud-like canopy made of " +
      "dense chunky clumps of pale pink and deep rose blossom with a few small fresh green leaves. Old, wind-shaped, storybook.",
    meshy: { target_polycount: 30000 },
  },
  teacup: {
    prompt:
      "A single dainty porcelain teacup sitting on its saucer: creamy white glaze painted with a ring of tiny pink " +
      "cherry blossoms, a thin gold rim, an elegant curled handle, filled almost to the brim with amber tea, with one " +
      "pink petal floating on the tea. Chunky, simple, toy-like proportions.",
    meshy: { target_polycount: 8000 },
  },
  // ---- Farewell Bridge (the river's last pool before the waterfall)
  wisteria_bridge: {
    prompt:
      "Exactly one bridge, alone and centred: a small old humpback stone footbridge, about three times as long as it is " +
      "tall, with one wide round arch, built of mossy weathered grey stone blocks with low parapets, overgrown by a huge " +
      "old wisteria vine: thick twisting woody stems wind along both parapets and long heavy cascades of purple and " +
      "lilac wisteria blossom hang down both sides all along its length, with patches of fresh green leaves. " +
      "The opening under the arch is wide, clear and empty so one can see through it. Storybook charm. Only one bridge in the image.",
    meshy: { target_polycount: 30000 },
  },
  stone_lamp: {
    prompt:
      "A short old wayside stone lamp: a square pillar of mossy rough-carved grey stone on a stepped base, topped by a " +
      "small iron-framed lantern with four glowing warm amber glass panes and a little pointed slate roof with a ball " +
      "finial. Lichen patches, storybook charm.",
    meshy: { target_polycount: 8000 },
  },
  thimble: {
    prompt:
      "A single antique silver sewing thimble, a little dented: its sides covered in neat rows of tiny dimples above an " +
      "engraved band of small raindrops and clouds, a thin gold rim, filled to the brim with clear bright blue water. " +
      "Chunky, simple, toy-like proportions.",
    meshy: { target_polycount: 8000 },
  },
  // ---- The Shipless Mast (the spine of the north-west headland)
  ship_mast: {
    prompt:
      "The upper mast of an old wooden sailing ship standing upright on its own, planted in a low mound of rough grey " +
      "stones: a thick weathered tapering timber mast bound with iron hoops, a round wooden crow's nest platform with a " +
      "plank railing two thirds of the way up, one horizontal yard spar carrying a furled cream canvas sail tied with " +
      "rope, a few thick ropes hanging and coiled, a small brass ship's bell under the crow's nest and a little brass " +
      "weathercock at the very top. No flags. Lichen, weathering, storybook charm.",
    meshy: { target_polycount: 30000 },
  },
  anchor: {
    prompt:
      "An old ship's anchor leaning at an angle as if half sunk: a heavy rust-brown iron shank with two broad curved " +
      "flukes, a weathered wooden stock bound with iron bands, a big iron ring with a few links of thick chain, " +
      "barnacles and patches of orange lichen.",
    meshy: { target_polycount: 10000 },
  },
  whistle: {
    prompt:
      "A single old bosun's whistle made of pale carved bone and polished brass: a slender curved tube ending in a round " +
      "ball chamber, engraved with swirling wind curls, hanging on a loop of thick braided red cord with two small blue " +
      "glass beads. Chunky, simple, toy-like proportions.",
    meshy: { target_polycount: 8000 },
  },
  // ---- The Wreck of the Marigold (the south-west beach)
  flower_boat: {
    prompt:
      "Exactly one boat, alone and centred, nothing else in the image: an old wrecked clinker-built wooden rowing boat " +
      "resting tilted a little to one side: overlapping planks with " +
      "peeling faded sky-blue paint and a worn white gunwale, a cracked hull with a ragged hole near the bow, two plank " +
      "seats, one broken oar lying across it, barnacles and dried seaweed, a rusty iron ring at the bow with a short " +
      "frayed rope. The inside of the hull is filled level with dark earth and green moss like a garden planter, with a " +
      "few trailing green vines over the sides. No flowers.",
    meshy: { target_polycount: 30000 },
  },
  glass_floats: {
    prompt:
      "A small pile of three old glass fishing floats of different sizes, each a hollow sphere of thick sea-green and " +
      "aqua glass held in a knotted net of thick dark tarred rope, resting against a short piece of silvery driftwood.",
    meshy: { target_polycount: 10000 },
  },
  tide_knot: {
    prompt:
      "A single ornate sailor's knot tied from thick pale hemp rope: a round monkey's fist knot above a flat woven " +
      "decorative rope rosette, a small polished brass ring at the top, and three sea-blue glass beads threaded on the " +
      "two short trailing ends. Chunky, simple, toy-like proportions.",
    meshy: { target_polycount: 8000 },
  },
  // ---- The Clock Meadow (the western meadows)
  sundial: {
    prompt:
      "A large ancient stone sundial: a wide round weathered limestone dial slab on a short stout carved pedestal with " +
      "three shallow circular steps, the dial face carved with hour marks, a sun face and curling rays, and a tall " +
      "triangular bronze gnomon turned green with verdigris. Moss in the carvings, lichen patches, a few cracks. Storybook charm.",
    meshy: { target_polycount: 24000 },
  },
  hourglass: {
    prompt:
      "A single small ornate brass hourglass: two glass bulbs holding glowing golden sand, set between two round brass " +
      "end plates joined by three twisted brass pillars decorated with tiny dandelion flowers and leaves. Chunky, " +
      "simple, toy-like proportions.",
    meshy: { target_polycount: 8000 },
  },
  // ---- The Open Hand (the western cliffs)
  stone_hand: {
    prompt:
      "A colossal ancient stone hand rising out of the ground from the wrist, palm turned up and open as if offering " +
      "something, fingers gently curled upward: carved from weathered grey granite with cracks and worn smooth " +
      "knuckles, thick green moss in the creases, yellow lichen patches, a few small ferns growing from the cracks. " +
      "The broken remains of a giant statue, monumental and calm.",
    meshy: { target_polycount: 30000 },
  },
  storm_marble: {
    prompt:
      "A single large glass marble held in a delicate open cage of tarnished silver wire like a pendant with a small " +
      "ring at the top: inside the clear glass sphere swirl dark indigo and violet storm clouds around a tiny bright " +
      "white lightning bolt. Chunky, simple, toy-like proportions.",
    meshy: { target_polycount: 8000 },
  },
};

const [mode = "concept", ...want] = process.argv.slice(2);
const names = want.length ? want : Object.keys(PIECES);
const imgOf = (name) => path.join(CONCEPT, `west_${name}.png`);

async function concept(name) {
  const img = imgOf(name);
  if (fs.existsSync(img)) { console.log(`${name}: concept exists`); return; }
  const res = await fal("fal-ai/nano-banana-pro", {
    prompt: `${STYLE}\n\nSubject: ${PIECES[name].prompt}`, num_images: 1, aspect_ratio: "1:1", resolution: "2K", output_format: "png",
  }, { label: `concept/${name}` });
  await download(res.images[0].url, img);
}

async function mesh(name) {
  const def = PIECES[name], img = imgOf(name);
  if (!fs.existsSync(img)) { console.log(`${name}: no concept yet`); return; }
  const out = path.join(OUT, "meshy", name);
  if (fs.existsSync(path.join(out, `${name}.glb`))) { console.log(`${name}: model exists`); return; }
  let id = cp.get(`mesh:${name}`);
  if (!id) {
    let url = cp.get(`url:${name}`);
    if (!url) { url = await falUpload(img); await cp.set(`url:${name}`, url); }
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
    await cp.set(`mesh:${name}`, id);
    console.log(`${name}: task started`);
  }
  const task = await meshyPoll("/openapi/v1/image-to-3d", id, name);
  if (task.status !== "SUCCEEDED") { console.error(`${name} FAILED: ${task.status} ${task.task_error?.message ?? ""}`); return; }
  await meshyDownload(task, out, name);
  console.log(`${name}: done (${task.consumed_credits ?? "?"} credits)`);
}

for (const n of names) if (!PIECES[n]) { console.error(`unknown piece: ${n}`); process.exit(1); }
if (mode === "redo") {
  for (const n of names) {
    if (fs.existsSync(imgOf(n))) fs.renameSync(imgOf(n), imgOf(n).replace(/\.png$/, `_old${Date.now() % 100000}.png`));
    await cp.set(`url:${n}`, undefined);
    await concept(n);
  }
} else if (mode === "concept") {
  const results = await Promise.allSettled(names.map(concept));
  results.forEach((r, i) => { if (r.status === "rejected") console.error(`${names[i]} FAILED: ${String(r.reason?.message ?? r.reason).slice(0, 300)}`); });
} else if (mode === "mesh") {
  const results = await Promise.allSettled(names.map(mesh));
  results.forEach((r, i) => { if (r.status === "rejected") console.error(`${names[i]} FAILED: ${String(r.reason?.message ?? r.reason).slice(0, 300)}`); });
} else {
  console.error("usage: places-west.mjs concept|mesh|redo [name ...]");
  process.exit(1);
}
console.log("PLACES-WEST DONE");
