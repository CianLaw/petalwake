// Concept art for the STANDING rider: the same courier-witch as tools/gen/rider-concept.mjs,
// landed and stepped off her broom, holding it upright beside her. The seated concept views are
// the references (fal nano-banana-pro/edit): first a front view of the new pose, then side, back
// and three-quarter views of that same pose for Meshy multi-image-to-3D.
//
// Usage: node tools/gen/rider-stand-concept.mjs front            (then look at it)
//        node tools/gen/rider-stand-concept.mjs views            (side + back + 34, in parallel)
//        node tools/gen/rider-stand-concept.mjs side|back|34     (one view)
//        ... --redo   moves the existing image(s) to art/concept/stand_rejected/ and generates again
// Output: art/concept/stand_<view>.png
//
// Which hand: the accepted front view (art/concept/stand_front.png) was generated from a wording
// that asked for the broom in her right hand; the model put it in her LEFT hand, on the same side
// as the cross-body satchel, and the picture was otherwise right, so it was kept. The pose text
// below now says LEFT so that the turnaround views describe the image they are orbiting.
import path from "node:path";
import fs from "node:fs";
import { fal, falUpload, download, ROOT, checkpoint } from "./lib.mjs";

const OUT = path.join(ROOT, "art", "concept");
const cp = checkpoint(path.join(OUT, "stand_tasks.json")); // own checkpoint: upload urls + call counts
const args = process.argv.slice(2);
const redo = args.includes("--redo");
const step = args.find((a) => !a.startsWith("--")) || "front";

// Verbatim from rider-concept.mjs (kept whole so the two scripts can be diffed).
const CHARACTER =
  "an original young courier-witch character: she wears a short marigold-yellow travel capelet over a cream linen blouse, " +
  "a wide-brimmed pointed witch hat in deep plum purple with a cream ribbon band and a tiny sprig of white wildflowers tucked in it, " +
  "dark teal trousers, laced chestnut-brown leather ankle boots, fingerless gloves, " +
  "a tan leather satchel with brass buckles and a rolled moss-green blanket strapped on her back, " +
  "chestnut-brown hair tied in one short thick braid. " +
  "She rides a rustic wooden broomstick: a long slightly crooked pale wood handle and a big bushy golden straw bristle head bound with dark cord, " +
  "with a small brass lantern hanging on a short chain under the front tip of the handle";

// The same words, with the broom sentence re-phrased for a broom that is held instead of ridden.
const WITCH = CHARACTER.split(" She rides ")[0];
const BROOM =
  "Her broom is the same rustic wooden broomstick: a long slightly crooked pale wood handle and a big bushy golden straw " +
  "bristle head bound with dark cord, with a small brass lantern hanging on a short chain from a leather loop near the tip of the handle";

const POSE =
  "Pose: she has just landed and stepped off her broom, and now stands still: upright and relaxed on both feet, " +
  "feet a little apart and flat on the ground, toes pointing forward, weight even, shoulders loose, head level, " +
  "looking straight ahead with a calm, friendly expression. " +
  "With her LEFT hand she holds the broomstick upright beside her like a walking staff. The broom is vertical: " +
  "the bushy straw bristle head is at the BOTTOM with the straw tips resting on the ground right next to the outside of her left boot, " +
  "and the handle rises straight up so that its top end is level with the tip of her hat (the broom is as tall as she is including the hat). " +
  "She grips the handle at about the height of her waist, elbow bent, forearm held out to the side, relaxed. " +
  "The broom stands directly beside her (not in front of her, not behind her) with a clear gap of empty background between it and her body, " +
  "and the handle passes outside the hat brim without touching it. " +
  "The small brass lantern hangs from its leather loop and short chain just below the top end of the handle, dangling straight down " +
  "on the outer side of the broom, away from her, touching nothing. " +
  "Her RIGHT arm hangs down relaxed at her side, slightly away from the body, the gloved hand open and empty. " +
  "In still air the marigold capelet hangs straight down from her shoulders, her braid hangs straight down her back, " +
  "the cross-body satchel rests against her left hip (between her and the broom, not touching the broom), " +
  "and the rolled green blanket and the back satchel stay strapped on her back.";

// Same look as the seated concept views (rider-concept.mjs STYLE), worded for a standing figure.
const STYLE =
  "High-end stylized 3D character render in the style of a modern animated feature film, soft appealing shapes, " +
  "clean readable materials, hand-painted texture feel, slightly exaggerated proportions (big hat, small figure). " +
  "Neutral flat even studio lighting with no cast shadows and no rim light, plain solid light-gray background, " +
  "no ground plane, no floor line, no contact shadow under the boots or the broom, no motion blur, no wind effects, " +
  "no particles, no text, no watermark. " +
  "The entire character and the entire broom, from the top end of the handle and the tip of the hat down to the boot soles " +
  "and the straw tips, are fully inside the frame with margin on all sides.";

const TURNAROUND =
  "This is a turnaround sheet task. Image 1 shows a stylized 3D character standing and holding her broomstick upright beside her " +
  "in her left hand, seen from the front. Render the EXACT same character, same outfit, same colors, same proportions, same broom " +
  "and lantern and the exact same frozen pose, as if the camera orbited around a static 3D statue. Same neutral flat even lighting, " +
  "same plain solid light-gray background, no cast shadows, no ground, no floor line, no contact shadows, no motion blur, no text. " +
  "The entire character and the entire broom are fully in frame with margin, drawn at the same size as in image 1. " +
  "The other reference images show the same character earlier, while she was riding the broom: use them ONLY to get the details " +
  "that image 1 does not show, never for the pose.";

const seated = (n) => path.join(OUT, `rider_${n}.png`);
const stand = (n) => path.join(OUT, `stand_${n}.png`);

const VIEWS = {
  front: {
    sources: () => [seated("front"), seated("side"), seated("top34")],
    prompt: () => [
      "New pose for an existing 3D character. The reference images all show ONE and the same stylized 3D character, " +
        "a young courier-witch riding her broomstick: image 1 shows her from the front, image 2 from her left side, " +
        "image 3 from above and behind.",
      "Render the EXACT same character, as if the same 3D model had simply been re-posed: identical face, hair and braid, " +
        "identical hat (same size, same wide brim, cream band, sprig of white wildflowers), identical marigold capelet with its " +
        "round turquoise brooch, cream blouse, belt, dark teal trousers with rolled cuffs, laced brown boots, gloves, " +
        "cross-body satchel, back satchel and rolled green blanket, and the identical broom and brass lantern. " +
        "Same colors, same materials, same body proportions, same level of detail.",
      `Subject: ${WITCH}. ${BROOM}.`,
      POSE,
      "Camera: straight-on front view with the camera at the height of her chest, orthographic-like long lens, no perspective " +
        "distortion. The broom, in her left hand, is on the RIGHT side of the picture, on the same side as the satchel on her hip " +
        "(the satchel side of image 1); her relaxed right arm is on the LEFT side of the picture. " +
        "Her boot soles and the straw tips are on the same horizontal ground level.",
      STYLE,
    ].join("\n\n"),
  },
  // Her right profile: the broom, the satchel and the arm that holds the broom are all on the far
  // side, so this view is a clean outline of the body, the hat and the gear on her back.
  side: {
    sources: () => [stand("front"), seated("side"), seated("back")],
    prompt: () => [
      TURNAROUND,
      "Image 2 shows her from her LEFT side and image 3 from behind: use them for the shape of her face in profile, the hat, " +
        "the braid and the gear strapped on her back.",
      "New camera: exact side view from her RIGHT side (the camera has orbited 90 degrees around her), orthographic-like long lens " +
        "at the height of her chest. She is seen in strict profile facing the RIGHT edge of the picture: nose, chest and boot toes " +
        "point right. Closest to the camera is her right arm, hanging down relaxed at her side with the gloved hand open and empty. " +
        "On her back are the rolled moss-green blanket strapped on top of the tan leather back satchel, and her braid hanging " +
        "straight down behind her neck over the capelet. The capelet hangs straight down around her shoulders. " +
        "The wide plum hat is seen exactly from the side, upright on her head, its pointed tip bent slightly backward.",
      // The accepted image puts the broom a little forward of her body (the handle shows past her chest and the
      // lantern, on the far side, past her face). That is a consistent reading of the front and back views, which
      // cannot show depth. A second wording that insisted on hiding the whole handle behind her gave the same
      // placement and moved the flowers to the wrong side of the hat (stand_rejected/stand_side_2.png).
      "The broom is in her left hand on the FAR side of her body. It stands vertically at the same depth as her feet, so her body " +
        "and her hat hide most of it: draw only the parts that stick out past her silhouette (such as the top end of the handle " +
        "near the tip of the hat, and part of the straw bristle head on the ground behind her boots). Her left arm and the " +
        "cross-body satchel are on the far side as well, hidden behind her torso and hip. Do not move the broom in front of her " +
        "or behind her, and do not put anything in her right hand.",
    ].join("\n\n"),
  },
  back: {
    sources: () => [stand("front"), seated("back"), seated("top34")],
    prompt: () => [
      TURNAROUND,
      "New camera: directly behind her (the camera has orbited 180 degrees around her), orthographic-like long lens at the height " +
        "of her chest. She is seen exactly from the back, so left and right are mirrored compared to image 1: the upright broom in " +
        "her left hand is now on the LEFT side of the picture, vertical, with the straw bristle head on the ground at the bottom " +
        "and the lantern hanging just below the top end of the handle on its outer (left) side; the cross-body satchel on her " +
        "left hip is also on the left, between her and the broom; her relaxed, empty right arm is on the RIGHT side of the picture.",
      "On her back we see the rolled moss-green blanket strapped horizontally on top of the tan leather back satchel with brass " +
        "buckles (as in image 2), the satchel strap crossing her back, the marigold capelet hanging straight down over her shoulders, " +
        "one chestnut braid hanging straight down the middle of her back over the capelet, and the back of the wide plum hat with " +
        "its cream band and the sprig of white flowers (as in image 2 and image 3). Her boots are seen from behind, heels toward " +
        "the camera. Her face is not visible.",
    ].join("\n\n"),
  },
  // Three-quarter view: from above and behind-left, the camera of the seated set's rider_top34.png.
  // It is the second look at the broom side (broom, lantern, gripping hand, hip satchel) and the
  // only look at the tops of the hat, the shoulders and the bedroll. It orbits the standing BACK
  // view, the nearest one. Two front three-quarter attempts were rejected first: one barely left
  // the front view, the other turned her body the wrong way and left the broom where it was
  // (stand_rejected/stand_34_1.png, stand_34_2.png).
  34: {
    sources: () => [stand("back"), stand("front"), seated("top34")],
    prompt: () => [
      "This is a turnaround sheet task. Image 1 shows a stylized 3D character standing and holding her broomstick upright beside " +
        "her in her left hand, seen exactly from behind; image 2 shows the same frozen pose from the front. Render the EXACT same " +
        "character, same outfit, same colors, same proportions, same broom and lantern and the exact same frozen pose, as if the " +
        "camera orbited around a static 3D statue. Same neutral flat even lighting, same plain solid light-gray background, " +
        "no cast shadows, no ground, no floor line, no contact shadows, no motion blur, no text. The entire character and the " +
        "entire broom are fully in frame with margin.",
      "New camera: elevated three-quarter rear view, from above and behind-left. Starting from the rear view of image 1, the camera " +
        "has orbited 40 degrees to the LEFT, toward the side where she holds the broom, and has risen to about 30 degrees above " +
        "horizontal, looking down at her; long lens, no perspective distortion. It is the camera angle of image 3, which shows the " +
        "same character earlier, riding the broom: use image 3 only for the camera angle, the top of the hat and the gear on her " +
        "back, never for the pose.",
      "She has not moved: she stands upright and faces away from us toward the upper left of the picture. We look down on the top " +
        "of the wide plum hat (cream band, the sprig of white flowers on its left side) and on her shoulders under the marigold " +
        "capelet. We see her back, with the braid hanging straight down over the capelet and the rolled moss-green blanket strapped " +
        "on top of the tan leather back satchel, and her left side, with the cross-body satchel on her left hip and her left arm " +
        "reaching out sideways to the broom. Her face is hidden by the hat; at most the edge of her left cheek shows.",
      "The broom is the element nearest to the camera, on the LEFT side of the picture, standing vertically on the ground beside " +
        "her left boot: all of it is visible, from the top end of the handle with the lantern hanging on its outer side, down past " +
        "her gripping left hand, to the big straw bristle head on the ground, with a clear gap between the broom and her body. " +
        "Her relaxed, empty right arm is on the far side, at the right of the picture. Both boots stand flat on the ground, " +
        "heels toward us.",
    ].join("\n\n"),
  },
};

// Checkpoint writes are serialised: the three views run in parallel and share one file.
let chain = Promise.resolve();
const put = (k, fn) => (chain = chain.then(() => cp.set(k, fn(cp.get(k)))));
const count = (what) => put(`count:${what}`, (n) => (n || 0) + 1);

const uploading = new Map();
function upload(file) {
  // keyed by name + size + mtime so a regenerated view is uploaded again
  const st = fs.statSync(file);
  const key = `upload:${path.basename(file)}:${st.size}:${Math.round(st.mtimeMs)}`;
  const have = cp.get(key);
  if (have) return Promise.resolve(have);
  if (!uploading.has(key)) {
    uploading.set(key, (async () => {
      const u = await falUpload(file);
      await put(key, () => u);
      await count("fal_uploads");
      return u;
    })());
  }
  return uploading.get(key);
}

async function view(name) {
  const v = VIEWS[name];
  if (!v) throw new Error(`unknown view "${name}" (front, side, back, 34)`);
  const out = stand(name);
  if (fs.existsSync(out)) {
    if (!redo) { console.log(`${name}: exists`); return out; }
    const rej = path.join(OUT, "stand_rejected");
    fs.mkdirSync(rej, { recursive: true });
    let n = 1;
    while (fs.existsSync(path.join(rej, `stand_${name}_${n}.png`))) n++;
    fs.renameSync(out, path.join(rej, `stand_${name}_${n}.png`));
    console.log(`${name}: previous image moved to stand_rejected/stand_${name}_${n}.png`);
  }
  const sources = v.sources();
  for (const s of sources) if (!fs.existsSync(s)) throw new Error(`${name}: missing reference ${path.relative(ROOT, s)}`);
  const urls = await Promise.all(sources.map(upload));
  const res = await fal("fal-ai/nano-banana-pro/edit", {
    prompt: v.prompt(), image_urls: urls, num_images: 1, aspect_ratio: "3:4", resolution: "2K", output_format: "png",
  }, { label: `stand/${name}` });
  await count("fal_generations");
  await download(res.images[0].url, out);
  return out;
}

if (step === "views") await Promise.all(["side", "back", "34"].map(view));
else await view(step);
await chain;
console.log("done");
