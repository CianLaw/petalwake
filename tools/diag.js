// Dev-only measurements for the wake vortices, the dive flare and the flower shells.
// From the page console:  const d = await import('/tools/diag.js?' + Date.now());  d.swirl(33)
const PW = () => window.PW;

export async function ready() {
  await new Promise((r) => { const t0 = Date.now(); const iv = setInterval(() => { if ((window.PW && window.PW.ready) || Date.now() - t0 > 40000) { clearInterval(iv); r(); } }, 150); });
  return !!(window.PW && window.PW.ready);
}

/** Rider-relative coordinates of flake i: [distance behind, lateral (+right), height]. */
function rel(i) {
  const f = PW().flight, F = PW().fx.flakes;
  const rx = Math.cos(f.yaw), rz = Math.sin(f.yaw);
  const dx = F.pos[i * 3] - f.pos.x, dy = F.pos[i * 3 + 1] - f.pos.y, dz = F.pos[i * 3 + 2] - f.pos.z;
  const hl = Math.hypot(f.fwd.x, f.fwd.z) || 1;
  return [-(dx * f.fwd.x + dz * f.fwd.z) / hl, dx * rx + dz * rz, dy];
}

/** How long petals stay with the broom and how many times they go round a core. */
export function swirl(speed = 33, ctl = {}, x = 300, z = -700, yaw = 200, agl = 1.3, warm = 3) {
  const g = PW(), out = {};
  g.fly(x, z, agl, yaw, speed);
  g.sim(warm, ctl);
  const f = g.flight, F = g.fx.flakes, V = g.vortex, N = 256;
  const marks = [];
  for (let i = 0; i < F.count && marks.length < 80; i++) if (!F.state[i] && F.life[i] < 0.12 && F.kind[i] === 0) marks.push(F.seed[i]);
  const st = marks.map(() => ({ ang: 0, prev: null, t7: null, t12: null, done: false, maxH: -9 }));
  const steps = 300;
  for (let s = 0; s < steps; s++) {
    g.sim(1 / 60, ctl);
    const idx = new Map();
    for (let i = 0; i < F.count; i++) idx.set(F.seed[i], i);
    marks.forEach((m, k) => {
      const S = st[k];
      if (S.done) return;
      const j = idx.get(m);
      if (j === undefined || F.state[j]) { S.done = true; S.t7 ??= s / 60; S.t12 ??= s / 60; return; }
      const [D, , h] = rel(j);
      if (D > 7) S.t7 ??= s / 60;
      if (D > 12) S.t12 ??= s / 60;
      const r = V.nearest(F.pos[j * 3], F.pos[j * 3 + 1], F.pos[j * 3 + 2]);
      if (r < 0) { S.prev = null; return; }
      const i = (V.head - r + N) % N;
      const dx = F.pos[j * 3] - V.ox[i], dy = F.pos[j * 3 + 1] - V.oy[i], dz = F.pos[j * 3 + 2] - V.oz[i];
      const py = dx * V.lx[i] + dz * V.lz[i], pz = dx * V.ux[i] + dy * V.uy[i] + dz * V.uz[i];
      const side = py > 0.5 * (V.yl[i] + V.yr[i]) ? 1 : -1;
      const a = Math.atan2(pz - (side > 0 ? V.zr[i] : V.zl[i]), py - (side > 0 ? V.yr[i] : V.yl[i]));
      if (S.prev && S.prev.side === side) { let d = a - S.prev.a; d = Math.atan2(Math.sin(d), Math.cos(d)); S.ang += d * side; }
      S.prev = { a, side };
      S.maxH = Math.max(S.maxH, h);
    });
  }
  const avg = (a) => (a.length ? +(a.reduce((p, q) => p + q, 0) / a.length).toFixed(2) : null);
  out.tracked = marks.length;
  out.secondsWithin7m = avg(st.map((s) => s.t7 ?? steps / 60));
  out.secondsWithin12m = avg(st.map((s) => s.t12 ?? steps / 60));
  out.turns = avg(st.map((s) => s.ang / 6.283));
  out.turnsMax = +Math.max(...st.map((s) => s.ang / 6.283)).toFixed(2);
  out.peakHeight = avg(st.map((s) => s.maxH));
  let near7 = 0, near15 = 0, fly = 0;
  for (let i = 0; i < F.count; i++) { if (F.state[i]) continue; fly++; const [D] = rel(i); if (D > -3 && D < 7) near7++; if (D > -3 && D < 15) near15++; }
  out.petals = { flying: fly, within7m: near7, within15m: near15, total: F.count, sprites: g.fx.sprites.count };
  out.cores = [1, 10, 25, 50, 90, 140].filter((r) => r < V.count).map((r) => {
    const i = (V.head - r + N) % N;
    return `age ${V.age[i].toFixed(2)}: y ${V.yl[i].toFixed(1)}/${V.yr[i].toFixed(1)} h ${V.hl[i].toFixed(1)}/${V.hr[i].toFixed(1)} k ${V.k[i].toFixed(1)} rc ${Math.sqrt(V.rc2[i]).toFixed(2)}`;
  });
  out.k = +V.strength.toFixed(1); out.speed = +f.speed.toFixed(1); out.agl = +f.agl.toFixed(2);
  out.cross = cross();
  return out;
}

/** Character map of where the flying flakes sit in the cross-plane behind the rider (seen from behind). */
export function cross(d0 = 0.5, d1 = 8) {
  const F = PW().fx.flakes;
  const W = 25, H = 9;       // lateral -6..6 (0.5 m), height -2..2.5 (0.5 m)
  const grid = Array.from({ length: H }, () => new Array(W).fill(0));
  for (let i = 0; i < F.count; i++) {
    if (F.state[i]) continue;
    const [D, lat, h] = rel(i);
    if (D < d0 || D > d1) continue;
    const cx = Math.round((lat + 6) / 0.5), cy = Math.round((h + 2) / 0.5);
    if (cx >= 0 && cx < W && cy >= 0 && cy < H) grid[cy][cx]++;
  }
  const ch = ' .:-=+*#%@';
  return grid.reverse().map((row) => row.map((n) => ch[Math.min(ch.length - 1, Math.ceil(n / 3))]).join(''));
}

/** Time a frame: average ms over n rendered frames at the current size. */
export async function frameMs(n = 40, w = 1920, h = 1080) {
  const g = PW();
  g.capturing = true;
  try {
    g.renderer.setPixelRatio(1); g.renderer.setSize(w, h, false); g.pipeline.setSize(w, h, 1);
    g.camera.aspect = w / h;
    const gl = g.renderer.getContext();
    // reading a pixel back is the only thing that reliably waits for the GPU to finish the frame
    const px = new Uint8Array(4);
    for (let i = 0; i < 5; i++) { g.step(1 / 60); g.renderOnce(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); }
    const t0 = performance.now();
    let sim = 0;
    for (let i = 0; i < n; i++) { const a = performance.now(); g.step(1 / 60); sim += performance.now() - a; g.renderOnce(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); }
    return { ms: +((performance.now() - t0) / n).toFixed(2), simMs: +(sim / n).toFixed(2), flakes: g.fx.flakes.count, sprites: g.fx.sprites.count };
  } finally { g.capturing = false; g.resize(); }
}

/** Dive at the ground and log the pull-out and the landing bounce. */
export function dive(agl = 160, pitchDeg = -70, speed = 55, ctl = { pitch: -1 }, x = 450, z = -900, yaw = 250, seconds = 6) {
  const g = PW(), f = g.flight;
  g.fly(x, z, agl, yaw, speed, pitchDeg);
  const rows = [];
  let minAgl = 1e9, maxRate = 0, touch = null, flareAt = null, maxAfter = -1e9, minAfter = 1e9, tLevel = null;
  const n = Math.round(seconds * 60);
  for (let i = 0; i < n; i++) {
    g.sim(1 / 60, ctl);
    const t = (i + 1) / 60;
    minAgl = Math.min(minAgl, f.agl);
    maxRate = Math.max(maxRate, f.pitchRate);
    if (flareAt === null && f.flare > 0.3) flareAt = { t: +t.toFixed(2), agl: +f.agl.toFixed(1), speed: +f.speed.toFixed(0), pitch: +(f.pitch * 57.3).toFixed(0) };
    if (touch === null && f.touchdown > 0) touch = { t: +t.toFixed(2), hit: +f.touchdown.toFixed(2), agl: +f.agl.toFixed(2), speed: +f.speed.toFixed(0) };
    if (touch) { maxAfter = Math.max(maxAfter, f.agl); minAfter = Math.min(minAfter, f.agl); }
    if (tLevel === null && flareAt && f.pitch > -0.05) tLevel = +t.toFixed(2);
    if (i % 6 === 0) rows.push(`${t.toFixed(1)}s agl ${f.agl.toFixed(1)} pitch ${(f.pitch * 57.3).toFixed(0)} rate ${f.pitchRate.toFixed(2)} v ${f.speed.toFixed(0)} bob ${f.bob.toFixed(2)}`);
  }
  return { flareAt, levelAt: tLevel, touch, minAgl: +minAgl.toFixed(2), maxPitchRate: +maxRate.toFixed(2), afterLanding: touch ? { lowest: +minAfter.toFixed(2), highest: +maxAfter.toFixed(2), settled: +f.agl.toFixed(2) } : null, rows };
}

/** Mean colour of the frame in horizontal bands (top to bottom), for comparing two render settings. */
export function bands(w = 960, h = 540, n = 12, x0 = 0.25, x1 = 0.75) {
  const g = PW();
  g.capturing = true;
  try {
    g.renderer.setPixelRatio(1); g.renderer.setSize(w, h, false); g.pipeline.setSize(w, h, 1);
    g.camera.aspect = w / h;
    g.renderOnce(); g.renderOnce();
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const ctx = c.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(g.renderer.domElement, 0, 0);
    const out = [];
    for (let b = 0; b < n; b++) {
      const y0 = Math.floor((b / n) * h), y1 = Math.floor(((b + 1) / n) * h);
      const d = ctx.getImageData(Math.floor(x0 * w), y0, Math.floor((x1 - x0) * w), y1 - y0).data;
      let r = 0, gg = 0, bl = 0;
      for (let i = 0; i < d.length; i += 4) { r += d[i]; gg += d[i + 1]; bl += d[i + 2]; }
      const m = d.length / 4;
      out.push([Math.round(r / m), Math.round(gg / m), Math.round(bl / m)]);
    }
    return out;
  } finally { g.capturing = false; g.resize(); }
}
