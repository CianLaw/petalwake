// The way in to a landing pad. Over the ground it is a turn, a straight and a turn - the shortest
// such path from where the broom is, heading as it is, to the head of the final approach - then
// the final straight in over the edge of the platform. A height profile is laid over that: it
// leaves at the slope the broom was flying, eases down (or up) to the glide, and is lifted clear
// of whatever stands underneath. Several ways round are tried and the best one flown.
// (Where it ends is up to the caller: over the middle of an open pad, or stood off from one that
// has a wall behind it. See landing.js.)
const TAU = Math.PI * 2;
const wrap = (a) => { a %= TAU; return a < 0 ? a + TAU : a; };
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);

export const APPROACH = {
  FINAL: 14,        // m: length of the straight run in to the pad (shorter and longer ones are tried too)
  GLIDE: 0.176,     // slope of that run (10 degrees)
  HOVER: 0.82,      // m: how high the broom hangs over the pad once it has settled (boots just off the floor)
  SETTLE: 0.22,     // m: the last of the height, lost once it has arrived
  TURN: 8.5,        // m: radius of the turn on to the final, flown slowly
  CLEAR: 2.2,       // m: kept between the broom and anything it crosses on the way round
  BOOT: 0.9,        // m: ...and over the platform's own edge on the final
  SLOPE: 0.75,      // steepest climb or descent planned for (37 degrees)
};
const DS = 1;       // m between samples of the height profile

/**
 * One way in over the ground: `pre` metres straight on (while the speed comes off), then a turn,
 * a straight and a turn on to the final. null if these two circles do not allow it.
 */
function csc(x0, z0, yaw0, pre, r1, s1, xg, zg, yawA, r2, s2, loops) {
  const xs = x0 + Math.sin(yaw0) * pre, zs = z0 - Math.cos(yaw0) * pre;
  const c1x = xs + s1 * r1 * Math.cos(yaw0), c1z = zs + s1 * r1 * Math.sin(yaw0);
  const c2x = xg + s2 * r2 * Math.cos(yawA), c2z = zg + s2 * r2 * Math.sin(yawA);
  const dx = c2x - c1x, dz = c2z - c1z, d = Math.hypot(dx, dz);
  const k = s2 * r2 - s1 * r1;
  if (d < Math.abs(k) + 1e-4) return null;
  const L = Math.sqrt(d * d - k * k);
  const yawT = Math.atan2(dx, -dz) - Math.atan2(k, L);        // heading of the straight
  let a1 = wrap(s1 * (yawT - yaw0)), a2 = wrap(s2 * (yawA - yawT));
  if (a1 > TAU - 2e-3) a1 = 0;
  if (a2 > TAU - 2e-3) a2 = 0;
  a2 += loops * TAU;
  const l1 = r1 * a1, l2 = r2 * a2;
  return { x0, z0, pre, c1x, c1z, r1, s1, yaw0, l1, L, yawT, c2x, c2z, r2, s2, l2, xg, zg, yawA, len: pre + l1 + L + l2 };
}

/** Where the ground path is s metres along: x, z, heading, curvature (+ = turning right). */
function over(g, s, o) {
  const q = s - g.pre;
  if (q < 0) {
    o.x = g.x0 + Math.sin(g.yaw0) * s; o.z = g.z0 - Math.cos(g.yaw0) * s; o.yaw = g.yaw0; o.k = 0;
  } else if (q < g.l1) {
    const psi = g.yaw0 + (g.s1 * q) / g.r1;
    o.x = g.c1x - g.s1 * g.r1 * Math.cos(psi); o.z = g.c1z - g.s1 * g.r1 * Math.sin(psi); o.yaw = psi; o.k = g.s1 / g.r1;
  } else if (q < g.l1 + g.L) {
    const u = q - g.l1;
    o.x = g.c1x - g.s1 * g.r1 * Math.cos(g.yawT) + Math.sin(g.yawT) * u;
    o.z = g.c1z - g.s1 * g.r1 * Math.sin(g.yawT) - Math.cos(g.yawT) * u;
    o.yaw = g.yawT; o.k = 0;
  } else if (s < g.len) {
    const psi = g.yawT + (g.s2 * (q - g.l1 - g.L)) / g.r2;
    o.x = g.c2x - g.s2 * g.r2 * Math.cos(psi); o.z = g.c2z - g.s2 * g.r2 * Math.sin(psi); o.yaw = psi; o.k = g.s2 / g.r2;
  } else {
    const u = s - g.len;
    o.x = g.xg + Math.sin(g.yawA) * u; o.z = g.zg - Math.cos(g.yawA) * u; o.yaw = g.yawA; o.k = 0;
  }
  return o;
}

class Path {
  constructor(g, len, ys) { this.g = g; this.len = len; this.gate = g.len; this.ys = ys; }

  height(s) {
    const y = this.ys, n = y.length, f = clamp(s / DS, 0, n - 1);
    const i = Math.min(Math.floor(f), n - 2), t = f - i;
    const p0 = y[Math.max(i - 1, 0)], p1 = y[i], p2 = y[i + 1], p3 = y[Math.min(i + 2, n - 1)];
    return 0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (3 * p1 - p0 - 3 * p2 + p3) * t * t * t);
  }

  /** @returns o = { x, y, z, yaw, k (curvature), slope (dy/ds) } at s metres along. */
  at(s, o) {
    s = clamp(s, 0, this.len);
    over(this.g, s, o);
    o.y = this.height(s);
    o.slope = (this.height(Math.min(s + 0.5, this.len)) - this.height(Math.max(s - 0.5, 0))) / Math.max(Math.min(s + 0.5, this.len) - Math.max(s - 0.5, 0), 1e-3);
    return o;
  }
}

/**
 * @param start   { x, y, z, yaw, slope (dy per metre over the ground), speed (over the ground),
 *                  run (metres it takes to rein the broom in: it can fly those straight and then
 *                  turn tightly, or start a wider turn at once - both are tried) }
 * @param end     { x, y, z, approach }: where the broom is to arrive, and the heading it arrives on
 * @param floorAt (x, z) -> top of the land, the water or a building there
 * @returns the Path to fly (len = metres over the ground to the end), or null
 */
export function planApproach(start, end, floorAt) {
  const A = APPROACH, o = { x: 0, y: 0, z: 0, yaw: 0, k: 0, slope: 0 };
  const yawA = end.approach, fx = Math.sin(yawA), fz = -Math.cos(yawA);
  const yEnd = end.y;
  const r1n = clamp(start.speed * 0.45, A.TURN, 28); // the first turn is flown while the speed is still coming off: wider
  const slope0 = clamp(start.slope, -0.7, 0.7);

  // ---- every way round worth looking at, shortest first
  const run = start.run || 0;
  const ways = [[0, r1n, A.TURN], [0, r1n, r1n], [0, r1n * 1.6, A.TURN]];
  if (run > 2) ways.push([run, A.TURN, A.TURN], [run * 0.6, A.TURN * 1.4, A.TURN]);
  const cand = [];
  for (const lf of [A.FINAL, 9, 20, 5.5]) {
    const xg = end.x - fx * lf, zg = end.z - fz * lf;
    const yGate = yEnd + lf * A.GLIDE;
    // (two turns the same way round on equal circles always join up, so there is always a way in)
    for (const [pre, r1, r2] of ways) {
      for (const s1 of [1, -1]) for (const s2 of [1, -1]) {
        for (let loops = 0; loops <= 2; loops++) {
          const g = csc(start.x, start.z, start.yaw, pre, r1, s1, xg, zg, yawA, r2, s2, loops);
          if (!g) break;
          // too steep to get up or down to the gate in the distance: only a turn or two more will do
          const steep = Math.abs(yGate - start.y) / Math.max(g.len, 1) - A.SLOPE;
          // (a short final is a scramble: it has to save a good deal of flying to be worth it)
          const base = g.len + lf + (lf < A.FINAL ? 3.0 : 0.6) * Math.abs(lf - A.FINAL) + 25 * loops + (steep > 0 ? 120 * steep : 0);
          cand.push({ g, lf, yGate, base });
          if (steep <= 0) break;
        }
      }
    }
  }
  cand.sort((a, b) => a.base - b.base);

  let best = null, bestCost = Infinity;
  for (const c of cand) {
    if (c.base >= bestCost) break;
    const { g, lf, yGate } = c, total = g.len + lf;
    const n = Math.max(3, Math.ceil(total / DS) + 1);
    const ys = new Float64Array(n), req = new Float64Array(n), nom = new Float64Array(n);
    const c0 = Math.max(0.9, start.y - floorAt(start.x, start.z));
    for (let i = 0; i < n; i++) {
      const s = Math.min(i * DS, total), left = total - s;
      over(g, s, o);
      // nominal height: ease from where we are to the gate, leaving at the slope we had; then the glide
      let y;
      if (s <= g.len) {
        const u = g.len > 0 ? s / g.len : 1, u2 = u * u, u3 = u2 * u;
        y = (2 * u3 - 3 * u2 + 1) * start.y + (-2 * u3 + 3 * u2) * yGate + (u3 - u2) * g.len * -A.GLIDE
          + slope0 * s * Math.exp(-s / 8) * (1 - u) * (1 - u);
      } else y = yEnd + left * A.GLIDE;
      nom[i] = y;
      // what is under this stretch (the broom has some width; the final is the pad's own corridor)
      const onFinal = s > g.len - 1, lat = onFinal ? 0.6 : 1.3;
      const rx = Math.cos(o.yaw) * lat, rz = Math.sin(o.yaw) * lat;
      const fl = Math.max(floorAt(o.x, o.z), floorAt(o.x + rx, o.z + rz), floorAt(o.x - rx, o.z - rz));
      const clr = onFinal ? A.BOOT : Math.min(A.CLEAR, c0 + 0.5 * s, A.BOOT + 0.35 * left);
      req[i] = left < 1.0 ? -1e9 : fl + clr;
      ys[i] = Math.max(y, req[i]);
    }
    // an obstacle is climbed to and come down from at a slope the broom can fly
    const up = 0.9 * DS, dn = 0.9 * DS;
    for (let i = n - 2; i >= 0; i--) if (ys[i] < ys[i + 1] - up) ys[i] = ys[i + 1] - up;
    for (let i = 1; i < n; i++) if (ys[i] < ys[i - 1] - dn) ys[i] = ys[i - 1] - dn;
    // ...but it starts where the broom is and ends on the pad, whatever that takes
    let bad = Math.max(0, ys[0] - start.y - 0.05) + Math.max(0, ys[n - 1] - yEnd - 0.05);
    for (let i = 0; i < n; i++) {
      const s = Math.min(i * DS, total);
      ys[i] = Math.min(ys[i], start.y + 0.3 + s * 1.5, yEnd + (total - s) * 1.3);
    }
    for (let pass = 0; pass < 3; pass++) {
      let prev = ys[0];
      for (let i = 1; i < n - 1; i++) { const cur = ys[i]; ys[i] = Math.max(0.25 * prev + 0.5 * cur + 0.25 * ys[i + 1], Math.min(req[i], cur)); prev = cur; }
    }
    ys[0] = start.y; ys[n - 1] = yEnd;
    let lift = 0;
    for (let i = 0; i < n; i++) { lift = Math.max(lift, ys[i] - nom[i]); if (ys[i] < req[i] - 0.6) bad += 0.2; }
    const cost = c.base + 3 * lift + 200 * bad;
    if (cost < bestCost) { bestCost = cost; best = new Path(g, total, ys); best.cost = cost; best.lift = lift; best.bad = bad; best.final = lf; }
  }
  return best;
}
