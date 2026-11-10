// Hero pieces for the six hidden places in the east of the island:
// concept art (fal nano-banana-pro) -> Meshy image-to-3D, adapted from props.mjs.
// Raw output goes to art/places_east/ (git-ignored); tools/blender/place_east_process.py turns it
// into the game assets under assets/places/models/east_*.glb.
//
// Usage:
//   node tools/gen/places-east.mjs concept <name ...>          draw the concept image(s)
//   node tools/gen/places-east.mjs concept --redo <name ...>   draw again (the old one is kept as .vN.png)
//   node --env-file=<file with MESHY_API_KEY> tools/gen/places-east.mjs mesh <name ...>
//   node tools/gen/places-east.mjs list
// Resumable through art/places_east/tasks.json.
import path from "node:path";
import fs from "node:fs";
import { fal, falUpload, download, meshy, meshyPoll, meshyDownload, ROOT, checkpoint } from "./lib.mjs";

const OUT = path.join(ROOT, "art", "places_east");
const CONCEPT = path.join(OUT, "concept");
const cp = checkpoint(path.join(OUT, "tasks.json"));

const STYLE =
  "High-end stylized 3D asset render in the style of a modern animated feature film: soft appealing shapes, " +
  "clean readable forms, hand-painted texture feel with rich natural detail. A single isolated object, complete and " +
  "fully inside the frame with margin on all sides, seen from a slightly elevated three-quarter view. " +
  "Neutral flat even studio lighting with no cast shadows, plain solid light-gray background, no ground plane, " +
  "no grass, no scenery, no people, no text, no watermark.";

// Each entry: the subject for the concept image, and overrides for the Meshy request.
export const ITEMS = {
  // ---- 1. The Thousand-Wish Pine (high on the mountain's shoulder)
  pine: {
    prompt:
      "An ancient wind-twisted mountain pine shaped by a century of gales: a thick gnarled spiralling trunk of " +
      "silver-grey and russet bark leaning strongly to one side, knuckled exposed roots gripping a low mound of pale " +
      "rock, a few long contorted limbs carrying flat windswept cloud-like pads of dense deep blue-green needles, all " +
      "streaming the same way. Dozens of small white and faded-red paper wish-strips are tied along the lower " +
      "branches and a thick weathered straw rope with white paper tassels is wound around the trunk.",
    meshy: { geometry_resolution: "2k", target_polycount: 16000 },
  },
  cairn: {
    prompt:
      "A small weathered wayside shrine built of stacked flat grey mountain stones: a squat stone lantern with a " +
      "little square window and a mossy cap stone, a tall balanced cairn of seven flat stones beside it, and a short " +
      "wooden post carrying a string of white and faded-red paper wish-strips. Orange and pale lichen, cushions of " +
      "moss, all standing on one flat slab of rock.",
    meshy: { target_polycount: 6000 },
  },
  bell: {
    prompt:
      "A single small antique bronze wind bell: a rounded dome-shaped bell with a ring of tiny engraved swirling wind " +
      "lines, green verdigris in the grooves and warm polished gold highlights, hanging from a short loop of braided " +
      "red cord, with one long narrow strip of cream paper hanging below it as a wind catcher.",
    meshy: { target_polycount: 2500 },
  },

  // ---- 2. The Kettle Pools (hot spring on the mountain's foot)
  pools: {
    prompt:
      "A natural hot-spring terrace as one low mound: a stepped cascade of six shallow scalloped basins of creamy " +
      "white and pale-ochre travertine mineral rock, each basin rimmed with smooth rounded dripping lips and filled " +
      "to the brim with opaque milky turquoise water, the widest basin at the top and smaller ones spilling down one " +
      "side like a staircase, rust-orange and sulphur-yellow mineral stains under the rims, a few rounded grey " +
      "stones at the foot.",
    meshy: { target_polycount: 14000 },
  },
  emberleaf: {
    prompt:
      "A small old ornamental tree with a short forked twisting dark trunk leaning to one side and a low, wide, " +
      "layered canopy made of dense chunky clumps of small leaves in glowing crimson, scarlet and ember orange, the " +
      "branches spreading in flat tiers like clouds. Exposed roots at the base.",
    meshy: { target_polycount: 12000 },
  },
  emberstone: {
    prompt:
      "A single smooth egg-shaped river stone of dark charcoal basalt about the size of two hands, wrapped once " +
      "around with a thin braided straw cord, crossed by a few fine cracks that glow from within in warm molten " +
      "orange and gold like a banked ember.",
    meshy: { target_polycount: 2000 },
  },

  // ---- 3. Starfall Ring (the north-east meadow)
  meteor: {
    prompt:
      "A fallen meteorite half-buried at an angle: one large rounded lump of dark charcoal-black iron-stone with a " +
      "pitted, thumb-printed, melted surface and a rusty brown bloom, split by one deep jagged crack that is packed " +
      "with bright pale icy-blue and white glassy crystals, and a ragged collar of pale-blue fused-glass crystal " +
      "shards pointing outward all around its base.",
    meshy: { target_polycount: 9000 },
  },
  splinter: {
    prompt:
      "A single long faceted splinter of star-glass crystal: a clear pale icy-blue and white shard with sharp " +
      "angled facets and a brighter glowing core, one end still crusted with a cap of dark pitted black meteorite " +
      "iron, tied around the middle with a loop of thin silver wire.",
    meshy: { target_polycount: 2000 },
  },

  // ---- 4. The Conch Garden (the eastern sand islet)
  conch: {
    prompt:
      "A giant spiral conch seashell lying on its side, as big as a garden shed: a tall pointed spire of knobbly " +
      "whorls with a crown of blunt horns, creamy white and warm peach outside with soft tan stripes, and a wide " +
      "flaring glossy lip that opens onto a smooth rose-pink and apricot interior large enough to crawl into. A few " +
      "barnacles and patches of green sea-moss near the bottom.",
    meshy: { target_polycount: 12000 },
  },
  clam: {
    prompt:
      "A giant clam shell gaping wide open like a bowl: two thick fluted shell halves with deeply scalloped wavy " +
      "edges, hinged at the back, pale cream outside with coral-pink ridges and a little green algae, the inside " +
      "lined with a ruffled fleshy mantle of iridescent turquoise and violet with small gold spots, and a smooth " +
      "empty hollow in the middle.",
    meshy: { target_polycount: 7000 },
  },
  coral: {
    prompt:
      "A large branching staghorn coral bush standing dry on a small knob of pale limestone: many smooth rounded " +
      "antler-like branches forking upward and outward in a broad dome, coral-red and salmon-orange with paler " +
      "peach-white tips, a few small purple sea-fans and yellow-green sponges nestled at its foot.",
    meshy: { target_polycount: 8000 },
  },

  // ---- 5. Lantern Roots (the lagoon shore)
  mangrove: {
    prompt:
      "A solitary old mangrove-like tree: a short stout twisting trunk held high above the ground on a wide cage " +
      "of many thick arching stilt roots like a great upturned basket, the root arches tall enough to row a small " +
      "boat beneath, smooth grey-brown bark with pale lichen, and a broad low umbrella-shaped canopy made of dense " +
      "chunky clumps of glossy deep-green leaves dotted with a few pale-yellow blossoms. Several small round paper " +
      "lanterns in warm orange and cream hang on short cords among the roots.",
    meshy: { geometry_resolution: "2k", target_polycount: 18000 },
  },
  skiff: {
    prompt:
      "A small old flat-bottomed wooden rowing skiff: weathered sea-green and cream painted planks with the paint " +
      "peeling, a single plank seat, two oars laid inside, a coil of rope, and a short upright pole at the bow " +
      "carrying one round paper lantern in warm orange. Barnacles along the waterline.",
    meshy: { target_polycount: 6000 },
  },
  ferrylight: {
    prompt:
      "A single small antique ship's lantern: a six-sided frame of dark green-patinated copper with a domed top " +
      "and a ring handle, panes of thick warm amber glass glowing softly from a light inside, a little coiled " +
      "shell ornament on the lid, sea-worn and a little dented.",
    meshy: { target_polycount: 2500 },
  },

  // ---- 6. The Whalebone Arbour (the long south-east beach)
  whale: {
    prompt:
      "The complete sun-bleached skeleton of a great whale lying on its belly, seen from the side and slightly " +
      "above: a long massive skull with broad arched jaw bones, a row of big knobbly vertebrae running back to a " +
      "tapering tail, and a high cage of ten pairs of thick curved ribs arching up and inward like the frame of an " +
      "upturned boat. Ivory-white weathered bone with warm grey and ochre staining, patches of green moss and small " +
      "tufts of pink sea-thrift flowers growing along the spine.",
    meshy: { geometry_resolution: "2k", target_polycount: 18000 },
  },
  driftwood: {
    prompt:
      "A big sun-bleached driftwood tree stump lying on its side with its tangle of twisted roots in the air: " +
      "silver-grey smooth worn wood with deep grain, a few barnacles, a frayed length of old blue fishing rope " +
      "caught in the roots and two green glass fishing floats in a net bag hanging from it.",
    meshy: { target_polycount: 6000 },
  },
  songbone: {
    prompt:
      "A single smooth whale ear-bone the size of a fist: a rounded ivory-white shell-like curl of polished bone " +
      "with a deep spiral hollow, fine carved wave lines along its rim inlaid with dark blue, threaded on a short " +
      "loop of knotted sea-blue cord with two tiny shells.",
    meshy: { target_polycount: 2000 },
  },
};

const [cmd, ...rest] = process.argv.slice(2);
const redo = rest.includes("--redo");
const names = rest.filter((a) => !a.startsWith("--"));
for (const n of names) if (!ITEMS[n]) { console.error(`unknown item: ${n}`); process.exit(1); }

async function concept(name) {
  const img = path.join(CONCEPT, `${name}.png`);
  if (fs.existsSync(img)) {
    if (!redo) { console.log(`${name}: concept exists`); return img; }
    let v = 1;
    while (fs.existsSync(path.join(CONCEPT, `${name}.v${v}.png`))) v++;
    fs.renameSync(img, path.join(CONCEPT, `${name}.v${v}.png`));
    await cp.set(`url:${name}`, undefined);
  }
  const res = await fal("fal-ai/nano-banana-pro", {
    prompt: `${STYLE}\n\nSubject: ${ITEMS[name].prompt}`, num_images: 1, aspect_ratio: "1:1", resolution: "2K", output_format: "png",
  }, { label: `concept/${name}` });
  await download(res.images[0].url, img);
  return img;
}

async function mesh(name) {
  const def = ITEMS[name];
  const img = path.join(CONCEPT, `${name}.png`);
  if (!fs.existsSync(img)) { console.error(`${name}: no concept image yet`); return; }
  const out = path.join(OUT, "meshy", name);
  if (fs.existsSync(path.join(out, `${name}.glb`)) && !redo) { console.log(`${name}: model exists`); return; }
  let id = redo ? undefined : cp.get(`task:${name}`);
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
        target_polycount: 12000,
        image_enhancement: false,
        target_formats: ["glb"],
        ...def.meshy,
      }),
    });
    id = result;
    await cp.set(`task:${name}`, id);
    await cp.set(`meshyCount`, (cp.get("meshyCount") || 0) + 1);
    console.log(`${name}: task started`);
  }
  const task = await meshyPoll("/openapi/v1/image-to-3d", id, name);
  if (task.status !== "SUCCEEDED") { console.error(`${name} FAILED: ${task.status} ${task.task_error?.message ?? ""}`); return; }
  await meshyDownload(task, out, name);
  console.log(`${name}: done (${task.consumed_credits ?? "?"} credits)`);
}

if (cmd === "list") {
  for (const n of Object.keys(ITEMS)) {
    const c = fs.existsSync(path.join(CONCEPT, `${n}.png`)), m = fs.existsSync(path.join(OUT, "meshy", n, `${n}.glb`));
    console.log(`${n.padEnd(12)} concept:${c ? "yes" : "-  "} model:${m ? "yes" : "-"}`);
  }
} else if (cmd === "concept") {
  const r = await Promise.allSettled(names.map(concept));
  r.forEach((x, i) => { if (x.status === "rejected") console.error(`${names[i]} FAILED: ${x.reason?.message}`); });
  console.log("CONCEPTS DONE");
} else if (cmd === "mesh") {
  const r = await Promise.allSettled(names.map(mesh));
  r.forEach((x, i) => { if (x.status === "rejected") console.error(`${names[i]} FAILED: ${x.reason?.message}`); });
  console.log("MESH DONE");
} else {
  console.error("usage: places-east.mjs concept|mesh|list [--redo] <name ...>");
  process.exit(1);
}
