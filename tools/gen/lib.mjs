// Shared helpers for fal.ai + Meshy generation scripts.
// Keys come from the environment (FAL_KEY, MESHY_API_KEY); they are never printed or written
// anywhere. To take them from an env file instead of exporting them, let node load it:
//   node --env-file=path/to/.env tools/gen/props.mjs
// (Keep that file outside this folder: the dev server serves everything in here.)
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
export const ROOT = path.resolve(here, "..", "..");
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function key(name) {
  const k = process.env[name];
  if (!k) throw new Error(`${name} is not set: export it, or run node with --env-file=<file>`);
  return k;
}
export const falKey = () => key("FAL_KEY");
export const meshyKey = () => key("MESHY_API_KEY");

// ---------- fal ----------
/** Run a fal model through the queue API and return the result JSON. */
export async function fal(endpoint, body, { label = endpoint, timeoutMs = 15 * 60 * 1000 } = {}) {
  const headers = { Authorization: `Key ${falKey()}`, "Content-Type": "application/json" };
  const sub = await fetch(`https://queue.fal.run/${endpoint}`, { method: "POST", headers, body: JSON.stringify(body) });
  const subText = await sub.text();
  if (!sub.ok) throw new Error(`fal submit ${endpoint}: ${sub.status} ${subText.slice(0, 600)}`);
  const { request_id, status_url, response_url } = JSON.parse(subText);
  const start = Date.now();
  let last = "";
  for (;;) {
    await sleep(2500);
    const st = await (await fetch(status_url, { headers })).json();
    if (st.status !== last) { console.log(`  [${label}] ${st.status}`); last = st.status; }
    if (st.status === "COMPLETED") break;
    if (st.status === "FAILED" || st.status === "ERROR") throw new Error(`fal ${endpoint} failed: ${JSON.stringify(st).slice(0, 600)}`);
    if (Date.now() - start > timeoutMs) throw new Error(`fal ${endpoint}: timeout (${request_id})`);
  }
  const res = await fetch(response_url, { headers });
  const text = await res.text();
  if (!res.ok) throw new Error(`fal result ${endpoint}: ${res.status} ${text.slice(0, 800)}`);
  return JSON.parse(text);
}

/** Upload a local file to fal storage and return its URL. */
export async function falUpload(file) {
  const buf = await fsp.readFile(file);
  const ext = path.extname(file).slice(1).toLowerCase();
  const type = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", webp: "image/webp" }[ext] || "application/octet-stream";
  const init = await fetch("https://rest.alpha.fal.ai/storage/upload/initiate", {
    method: "POST",
    headers: { Authorization: `Key ${falKey()}`, "Content-Type": "application/json" },
    body: JSON.stringify({ file_name: path.basename(file), content_type: type }),
  });
  if (!init.ok) throw new Error(`fal upload initiate: ${init.status} ${(await init.text()).slice(0, 300)}`);
  const { upload_url, file_url } = await init.json();
  const put = await fetch(upload_url, { method: "PUT", headers: { "Content-Type": type }, body: buf });
  if (!put.ok) throw new Error(`fal upload put: ${put.status}`);
  return file_url;
}

export function dataUrl(file) {
  const ext = path.extname(file).slice(1).toLowerCase();
  const type = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", webp: "image/webp" }[ext] || "application/octet-stream";
  return `data:${type};base64,${fs.readFileSync(file).toString("base64")}`;
}

export async function download(url, outPath) {
  for (let attempt = 0; attempt < 5; attempt++) {
    try {
      const r = await fetch(url);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const buf = Buffer.from(await r.arrayBuffer());
      await fsp.mkdir(path.dirname(outPath), { recursive: true });
      await fsp.writeFile(outPath, buf);
      console.log(`  wrote ${path.relative(ROOT, outPath)} (${(buf.length / 1e6).toFixed(2)} MB)`);
      return outPath;
    } catch (e) {
      if (attempt === 4) throw e;
      await sleep(3000 * (attempt + 1));
    }
  }
}

// ---------- Meshy ----------
const MESHY = "https://api.meshy.ai";
export async function meshy(pathname, init = {}) {
  for (let attempt = 0; ; attempt++) {
    let res;
    try {
      res = await fetch(`${MESHY}${pathname}`, {
        ...init,
        headers: { Authorization: `Bearer ${meshyKey()}`, "Content-Type": "application/json", ...(init.headers || {}) },
      });
    } catch (e) {
      if (attempt < 5) { await sleep(5000 * (attempt + 1)); continue; }
      throw e;
    }
    const text = await res.text();
    let data;
    try { data = JSON.parse(text); } catch { data = { raw: text }; }
    if (res.ok) return data;
    const msg = data.message ?? data.error ?? `HTTP ${res.status}`;
    if ((res.status === 429 || /NoMorePendingTasks|rate limit/i.test(msg)) && attempt < 10) {
      console.log(`  [${pathname}] ${res.status} ${msg} — backing off`);
      await sleep(15000 * (attempt + 1));
      continue;
    }
    if (res.status >= 500 && attempt < 4) { await sleep(5000 * (attempt + 1)); continue; }
    throw new Error(`${init.method ?? "GET"} ${pathname}: ${res.status} ${msg}`);
  }
}

export async function meshyPoll(endpoint, id, label, timeoutMs = 45 * 60 * 1000) {
  const start = Date.now();
  let last = "";
  for (;;) {
    const task = await meshy(`${endpoint}/${id}`);
    const s = `${task.status} ${task.progress ?? 0}%`;
    if (s !== last) { console.log(`  [${label}] ${s}`); last = s; }
    if (["SUCCEEDED", "FAILED", "CANCELED", "EXPIRED"].includes(task.status)) return task;
    if (Date.now() - start > timeoutMs) throw new Error(`${label}: timeout`);
    await sleep(8000);
  }
}

/** Download model + textures + thumbnail for a finished Meshy task. */
export async function meshyDownload(task, dir, prefix) {
  await fsp.mkdir(dir, { recursive: true });
  for (const [fmt, url] of Object.entries(task.model_urls || {})) {
    if (!url) continue;
    const ext = fmt === "pre_remeshed_glb" ? "pre_remeshed.glb" : fmt;
    await download(url, path.join(dir, `${prefix}.${ext}`));
  }
  for (const [i, tex] of (task.texture_urls || []).entries()) {
    for (const [k, url] of Object.entries(tex)) {
      if (url) await download(url, path.join(dir, `${prefix}_${k}${i ? "_" + i : ""}.png`));
    }
  }
  if (task.thumbnail_url) await download(task.thumbnail_url, path.join(dir, `${prefix}_thumb.png`));
  const redacted = JSON.parse(JSON.stringify(task, (k, v) => (typeof v === "string" && v.startsWith("http") ? v.split("?")[0] : v)));
  await fsp.writeFile(path.join(dir, `${prefix}_task.json`), JSON.stringify(redacted, null, 2));
}

/** Tiny JSON checkpoint store so re-runs resume instead of re-spending credits. */
export function checkpoint(file) {
  let data = {};
  try { data = JSON.parse(fs.readFileSync(file, "utf8")); } catch {}
  return {
    get: (k) => data[k],
    set: async (k, v) => { data[k] = v; await fsp.mkdir(path.dirname(file), { recursive: true }); await fsp.writeFile(file, JSON.stringify(data, null, 2)); },
  };
}
