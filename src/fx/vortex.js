// The broom's wake, simulated: a counter-rotating pair of trailing vortices shed from either side of
// the rider, the same pair that rolls off the wingtips of anything that flies.
//
// The trail is a ring of "stations" - cross-sections of the wake laid down every metre or two.
// Each station carries its two cores and evolves on its own, in its cross-plane:
//   - the cores drive each other (the pair sinks) and feel their mirror images under the ground
//     (near the deck they run apart along it instead of sinking through);
//   - they fatten and weaken as they age, faster once they are scrubbing the ground;
//   - the whole trail drifts on the wind and goes wavy before it dies.
// A fresh station is as strong as the broom is fast, so speed makes the vortices.
//
// Nothing about it is tidy. The shedding is unsteady (strength gusts, the two sides are never quite
// equal, the outer one is stronger in a turn, every station is laid a little off true), and the
// air between and around the cores is turbulent: eddies a few metres across ride along the trail
// and grow as the vortices age and break down.
//
// Two things read the simulation:
//   sample()  - air velocity at a point, for petals, spray and dust (CPU);
//   ribbon    - a strip of geometry the wake field draws to get the wind over the ground, which
//               is what bends the grass and flowers and ruffles the water (GPU).
import * as THREE from 'three';

const N = 256;                       // stations kept along the trail
const LIFE = 6.5;                    // seconds before a station has spun itself out
const CELL = 7, G = 96;              // lookup grid: a 672 m square around the rider
const REACH = 10;                    // a station's swirl is negligible beyond this (m)
const LEAD = 3.0;                    // the field builds up over this distance ahead of the broom
const RC0 = 0.20;                    // core radius at birth (m)
// The wake opens like a trumpet. At the broom the sheet of air has only begun to roll up: the
// vortices are tight, close together and not yet at full strength. Over the next few metres they
// wind up, move apart, and the ring of air each one carries round it widens.
const R_TIGHT = 0.32;                // radius of that ring at the broom (m)...
const R_WIDE = 1.05;                 // ...and how much it gains once the wake has opened (more when strong)
const OPEN_D = 6;                    // distance behind the broom over which it opens (m)
const SPREAD = 1.3;                  // how far each core moves outboard as it does (m)
const ROLL0 = 0.3;                   // fraction of full swirl right at the broom
const GRIP0 = 1.0;                   // how much harder the tight end holds what it has caught
const F0 = 0.985, INV_F0 = 1 / F0, TAU_AX = 0.62;   // air right behind the broom is dragged along at F0 of its speed,
                                     // falling off as exp(-(age / TAU_AX)^2): a pocket that rides with her
const R_AX = 2.4;                    // ...within about this far of either core: the oval of air that
                                     // travels with a vortex pair (m). Stronger vortices carry more.
const K_IN = 0.5;                    // draw onto the rings, per unit of swirl. Its reach grows with
                                     // the ring (0.6 m + 1.1 radii): the tight end only gathers what
                                     // is close by, and never pulls across from the other core
const GROUND_SLIP = 0.6;             // how freely the cores run apart along the ground
const REBOUND = 0.34;                // vortices that come down on the ground lift off it again
const TURB = 0.26;                   // eddy speed as a fraction of the swirl, once the trail has aged

export const VORTEX = { N, LIFE, LEAD, R_AX };

/**
 * Shaders for drawing the trail's ribbon into a top-down map: the scrolling wake field (wake.js)
 * and the island-wide map of stripped flowers (strip.js). uCenter / uExtent say which patch of the
 * world the map covers.
 */
export const RIBBON_VERT = /* glsl */`
  attribute vec4 aCore, aParm, aDir;
  uniform vec2 uCenter;
  uniform float uExtent;
  varying float vLat;
  varying vec2 vXZ;
  varying vec4 vCore, vParm, vDir;
  void main(){
    vLat = position.z; vXZ = position.xy; vCore = aCore; vParm = aParm; vDir = aDir;
    gl_Position = vec4((position.xy - uCenter) / uExtent * 2.0, 0.0, 1.0);
  }`;
export const RIBBON_WIND = /* glsl */`
  uniform float uTime;
  varying float vLat;
  varying vec2 vXZ;
  varying vec4 vCore, vParm, vDir;
  // flow about a line vortex of swirl k at c, softened inside its core
  vec2 vort(vec2 p, vec2 c, float k, float rc2){ vec2 d = p - c; return k * vec2(-d.y, d.x) / (dot(d, d) + rc2); }
  // Wind under this cross-section of the wake: xy = over the ground (world xz, m/s), z = vertical,
  // w = speed across the trail.
  vec4 groundWind(){
    // sampled at the height of the flower heads; the images keep the flow from going through the ground
    vec2 p = vec2(vLat, 0.45);
    float k = vParm.x, rc2 = vParm.y;
    // the two sides are never quite equal
    float kr = k * (1.0 + vDir.w), kl = k * (1.0 - vDir.w);
    vec2 v = vort(p, vec2(vCore.z, vCore.w), kr, rc2) + vort(p, vec2(vCore.z, -vCore.w), -kr, rc2)
           + vort(p, vec2(vCore.x, vCore.y), -kl, rc2) + vort(p, vec2(vCore.x, -vCore.y), kl, rc2);
    // gusty, not a steady blast: the wind over the ground comes in ragged pulses
    v *= 1.0 + 0.30 * sin(dot(vXZ, vec2(0.83, 1.31)) + uTime * 2.6) * sin(dot(vXZ, vec2(-1.17, 0.61)) - uTime * 1.9 + 1.3);
    // the air dragged along under the broom
    vec2 dl = p - vCore.xy, dr = p - vCore.zw;
    float ra = min(dot(dl, dl), dot(dr, dr)) * vDir.z;
    float ax = vParm.z / (1.0 + ra * ra);
    float edge = 1.0 - smoothstep(0.72, 1.0, abs(vLat) / vParm.w);
    // (the heading is the lateral axis turned a quarter turn)
    return vec4((vDir.xy * v.x + vec2(vDir.y, -vDir.x) * ax) * edge, v.y * edge, length(v) * edge);
  }`;

export class VortexWake {
  constructor(terrain) {
    this.terrain = terrain;
    this.river = null;
    const f = () => new Float32Array(N);
    // origin, tangent, level lateral axis (ly = 0), and the cross-plane's "up" = lateral x tangent
    this.ox = f(); this.oy = f(); this.oz = f();
    this.tx = f(); this.ty = f(); this.tz = f();
    this.lx = f(); this.lz = f();
    this.ux = f(); this.uy = f(); this.uz = f();
    // the two cores in the cross-plane (y along the lateral axis, z along up)
    this.yl = f(); this.zl = f(); this.yr = f(); this.zr = f();
    this.hl = f(); this.hr = f();      // height above the ground (world metres)
    this.dl = f(); this.dr = f();      // distance to the ground measured in the cross-plane
    this.gk = f();                     // how much the ground matters (0 in a vertical dive)
    this.kb = f(); this.k = f();       // swirl: speed x radius (circulation / 2 pi), raw and as it acts now
    this.ki = f();                     // strength of the draw onto the rings
    this.r0 = f();                     // radius of the ring of air each core carries (m)
    this.rc2 = f();                    // core radius squared
    this.age = f();
    this.ax0 = f(); this.ax = f();     // speed of the air dragged along the trail: when shed, and now
    this.irx = f();                    // 1 / (radius of that pocket of air)^2
    this.asym = f();                   // imbalance between the two cores: right is (1 + a) k, left (1 - a) k
    this.s = f();                      // distance along the trail when shed (phase for the waviness)
    this.head = 0; this.count = 0; this.arc = 0; this.frame = 0;
    this.strength = 0;
    this.time = 0;
    this._emit = new THREE.Vector3();
    this.cell = new Int16Array(G * G);
    this.cellD = new Float32Array(G * G);
    this.gx0 = 0; this.gz0 = 0;
    this._w = [0, 0, 0];

    // ---- ground-wind ribbon: two vertices per station (plus a lead-in ahead of the broom)
    const NV = (N + 1) * 2;
    const g = new THREE.BufferGeometry();
    const mk = (n) => { const a = new THREE.BufferAttribute(new Float32Array(NV * n), n); a.setUsage(THREE.DynamicDrawUsage); return a; };
    this.aPos = mk(3);      // world x, world z, signed distance from the centreline
    this.aCore = mk(4);     // left core: lateral offset, height; right core: lateral offset, height
    this.aParm = mk(4);     // swirl, core radius squared, dragged-air speed, half width
    this.aDir = mk(4);      // lateral axis xz, 1 / (pocket radius)^2, imbalance between the cores
    g.setAttribute('position', this.aPos); g.setAttribute('aCore', this.aCore);
    g.setAttribute('aParm', this.aParm); g.setAttribute('aDir', this.aDir);
    this.aIndex = new THREE.BufferAttribute(new Uint16Array(N * 6), 1);
    this.aIndex.setUsage(THREE.DynamicDrawUsage);
    g.setIndex(this.aIndex);
    g.setDrawRange(0, 0);
    this.ribbon = g;
  }

  /** Swirl (m/s at one metre from the core) of a vortex shed at this airspeed. */
  static strengthAt(speed, boosting = 0) {
    return Math.min(13 * Math.pow(speed / 33, 1.25), 44) * (1 + 0.15 * boosting);
  }

  reset() { this.count = 0; this.ribbon.setDrawRange(0, 0); }

  _ground(x, z) {
    const h = this.terrain.heightAt(x, z);
    if (this.river) { const r = this.river.levelAt(x, z); if (r > h) return r; }
    return h > 0 ? h : 0;
  }

  /** Where station i's cores are above the ground; keeps them out of it. */
  _touch(i) {
    const lx = this.lx[i], lz = this.lz[i], ux = this.ux[i], uy = this.uy[i], uz = this.uz[i];
    const ox = this.ox[i], oy = this.oy[i], oz = this.oz[i];
    const up = uy > 0.3 ? uy : 0.3;
    this.gk[i] = uy <= 0.3 ? 0 : uy >= 0.6 ? 1 : (uy - 0.3) / 0.3;
    const hmin = 0.28 + 0.45 * Math.sqrt(this.rc2[i]);
    let y = this.yl[i], z = this.zl[i];
    let h = oy + uy * z - this._ground(ox + lx * y + ux * z, oz + lz * y + uz * z);
    if (h < hmin) { this.zl[i] = z + (hmin - h) / up; h = hmin; }
    this.hl[i] = h; this.dl[i] = h / up;
    y = this.yr[i]; z = this.zr[i];
    h = oy + uy * z - this._ground(ox + lx * y + ux * z, oz + lz * y + uz * z);
    if (h < hmin) { this.zr[i] = z + (hmin - h) / up; h = hmin; }
    this.hr[i] = h; this.dr[i] = h / up;
  }

  _copy(a, b) {
    for (const k of ['ox', 'oy', 'oz', 'tx', 'ty', 'tz', 'lx', 'lz', 'ux', 'uy', 'uz', 'yl', 'zl', 'yr', 'zr', 'hl', 'hr', 'dl', 'dr', 'gk', 'kb', 'k', 'ki', 'r0', 'rc2', 'age', 'ax0', 'ax', 'irx', 'asym', 's']) this[k][b] = this[k][a];
  }

  /**
   * @param flight  Flight state (pos, fwd, yaw, roll, speed, boosting)
   * @param windAt  (x, y, z, out) ambient wind, so the trail drifts with the gusts
   */
  update(dt, flight, time, windAt) {
    if (!(dt > 0)) return;
    this.frame++;
    this.time = time;
    const p = flight.pos, f = flight.fwd, V = flight.speed;
    const cy = Math.cos(flight.yaw), sy = Math.sin(flight.yaw);
    const cp = Math.hypot(f.x, f.z);
    // shed from the bristles, a little behind the rider
    const ex = p.x - f.x * 0.5, ey = p.y - f.y * 0.5, ez = p.z - f.z * 0.5;
    const ds = Math.min(2.6, Math.max(1.1, V * 0.03));

    if (!this.count) {
      this.head = 0; this.count = 1;
      this._emit.set(ex, ey, ez);
    } else {
      const e = this._emit;
      let dx = ex - e.x, dy = ey - e.y, dz = ez - e.z;
      let d = Math.hypot(dx, dy, dz);
      if (d > 80) { this.count = 1; e.set(ex, ey, ez); d = 0; }          // teleported: start a new trail
      // leave a station behind every ds metres; the one in hand freezes where it should have been
      while (d >= ds) {
        const q = ds / d, h = this.head;
        e.x += dx * q; e.y += dy * q; e.z += dz * q;
        this.ox[h] = e.x; this.oy[h] = e.y; this.oz[h] = e.z;
        this.age[h] = (d - ds) / Math.max(V, 1);
        this.arc += ds; this.s[h] = this.arc;
        // no two stretches of the trail are alike: each is shed a little stronger or weaker, its
        // cores a little out of place, tight or already loose
        this.kb[h] *= 0.86 + 0.28 * Math.random();
        this.asym[h] += (Math.random() - 0.5) * 0.14;
        this.yl[h] += (Math.random() - 0.5) * 0.36; this.zl[h] += (Math.random() - 0.5) * 0.30;
        this.yr[h] += (Math.random() - 0.5) * 0.36; this.zr[h] += (Math.random() - 0.5) * 0.30;
        this.rc2[h] *= 0.8 + 0.6 * Math.random();
        this.head = (h + 1) % N;
        if (this.count < N) this.count++;
        this._copy(h, this.head);
        dx = ex - e.x; dy = ey - e.y; dz = ez - e.z;
        d = Math.hypot(dx, dy, dz);
      }
    }

    // ---- the station in hand rides with the broom
    {
      const h = this.head;
      this.ox[h] = ex; this.oy[h] = ey; this.oz[h] = ez;
      this.tx[h] = f.x; this.ty[h] = f.y; this.tz[h] = f.z;
      this.lx[h] = cy; this.lz[h] = sy;
      this.ux[h] = -sy * f.y; this.uy[h] = cp; this.uz[h] = cy * f.y;
      // one core off each side, banked with the rider: close in by the bristles to begin with
      const span = 1.1 + 0.004 * V;
      const hy = 0.5 * span * Math.cos(flight.roll), hz = 0.5 * span * Math.sin(flight.roll);
      this.yl[h] = -hy; this.zl[h] = -0.15 + hz;
      this.yr[h] = hy; this.zr[h] = -0.15 - hz;
      // unsteady shedding: the strength gusts, and the two sides trade places as the stronger -
      // in a turn the outside one, which is moving faster through the air
      const gusty = 1 + 0.15 * Math.sin(time * 1.7 + 0.4) + 0.10 * Math.sin(time * 4.3 + 2.1) + 0.06 * Math.sin(time * 9.7);
      const k = VortexWake.strengthAt(V, flight.boosting) * gusty;
      this.kb[h] = k; this.k[h] = k * ROLL0; this.ki[h] = k * (1 + GRIP0); this.r0[h] = R_TIGHT; this.strength = k;
      const turn = Math.max(-0.22, Math.min(0.22, (flight.turnRate || 0) * 0.16));
      this.asym[h] = 0.13 * Math.sin(time * 1.13 + 1.0) + 0.09 * Math.sin(time * 3.7 + 0.3) - turn;
      this.rc2[h] = RC0 * RC0;
      this.age[h] = 0;
      this.ax0[h] = this.ax[h] = V * F0;
      this.irx[h] = 1 / (R_AX * R_AX * (1 + k / 26));
      this.s[h] = this.arc + ds;
      this._touch(h);
    }

    // ---- everything already shed evolves
    const n = this.count;
    const w = this._w;
    const dFree = Math.exp(-dt / 2.9), dLow = Math.exp(-dt / 1.9);
    for (let r = 1; r < n; r++) {
      const i = (this.head - r + N) % N;
      const age = (this.age[i] += dt);
      const low = Math.min(this.dl[i], this.dr[i]) < 1.6;
      const kb = (this.kb[i] *= low ? dLow : dFree);
      const kf = kb * (age > LIFE - 1.5 ? Math.max(0, (LIFE - age) / 1.5) : 1);
      // how far behind the broom this stretch was when it reached its present age, and so how far
      // the trumpet has opened here
      const v0 = this.ax0[i] * INV_F0, D = age * v0;
      const opened = 1 - Math.exp(-D / OPEN_D);
      const r0 = (this.r0[i] = R_TIGHT + R_WIDE * (1 + kb / 45) * opened);
      this.ki[i] = kf * (1 + GRIP0 * Math.exp(-D / 5));
      // the pocket of air carried along grows with the rings inside it
      const rp = R_AX * Math.sqrt(1 + kb / 26) + (r0 - R_TIGHT);
      this.irx[i] = 1 / (rp * rp);
      const k = (this.k[i] = kf * (ROLL0 + (1 - ROLL0) * (1 - Math.exp(-D / 4))));
      const spread = (SPREAD / OPEN_D) * v0 * (1 - opened);
      const an = age / TAU_AX, held = Math.exp(-an * an);
      this.ax[i] = this.ax0[i] * held;
      // cores fatten by turbulent diffusion, quicker when they are strong
      const rc2 = (this.rc2[i] += (0.12 + 0.024 * kb) * dt);
      let yl = this.yl[i], zl = this.zl[i], yr = this.yr[i], zr = this.zr[i];
      // seen from behind, the left core turns clockwise (-k) and the right one anticlockwise (+k):
      // air goes down between them and up outside. Each moves in the other's flow, so the pair sinks.
      const dy = yr - yl, dz = zr - zl;
      const m = k / (dy * dy + dz * dz + rc2);
      let vly = m * dz - spread, vlz = -m * dy, vry = m * dz + spread, vrz = vlz;
      const gk = this.gk[i];
      if (gk > 0.01) {
        const kg = k * gk, dl = this.dl[i], dr = this.dr[i];
        // its own image sends each core outboard along the ground...
        vry += GROUND_SLIP * kg * 2 * dr / (4 * dr * dr + rc2);
        vly -= GROUND_SLIP * kg * 2 * dl / (4 * dl * dl + rc2);
        // ...and the other core's image holds it up
        let ay = dy, az = dz + 2 * dl, q = kg / (ay * ay + az * az + rc2);
        vry += -az * q * GROUND_SLIP; vrz += ay * q;
        ay = -dy; az = -dz + 2 * dr; q = -kg / (ay * ay + az * az + rc2);
        vly += -az * q * GROUND_SLIP; vlz += ay * q;
        // the sheet of air they scrub off the ground rolls up underneath and bounces them back up
        // (only so far: by a couple of metres up they have left it behind)
        vlz += REBOUND * kg / (dl + 0.3) * Math.min(1, Math.max(0, (2.7 - dl) / 1.3));
        vrz += REBOUND * kg / (dr + 0.3) * Math.min(1, Math.max(0, (2.7 - dr) / 1.3));
      }
      // long-wave wobble: the trail goes sinuous before it breaks up
      const s = this.s[i], wob = Math.min(age * 0.8, 1) * (0.35 + 0.05 * kb);
      vly += wob * Math.sin(s * 0.19 + time * 0.8); vlz += wob * 0.6 * Math.sin(s * 0.23 - time * 0.6 + 1.7);
      vry += wob * Math.sin(s * 0.17 - time * 0.7 + 4.1); vrz += wob * 0.6 * Math.sin(s * 0.21 + time * 0.9 + 0.4);
      this.yl[i] = yl + vly * dt; this.zl[i] = zl + vlz * dt;
      this.yr[i] = yr + vry * dt; this.zr[i] = zr + vrz * dt;
      // every other frame: drift on the wind, and feel for the ground again
      if (((i + this.frame) & 1) === 0) {
        if (windAt) {
          windAt(this.ox[i], this.oy[i], this.oz[i], w);
          // (the air the broom still has hold of goes where she goes, not where the wind blows)
          const free = (1 - held) * 2 * dt;
          this.ox[i] += w[0] * free; this.oz[i] += w[2] * free;
        }
        this._touch(i);
      }
    }
    while (this.count > 1 && this.age[(this.head - this.count + 1 + N) % N] > LIFE) this.count--;

    this._buildGrid(p);
    this._buildRibbon();
  }

  /** Coarse lookup: for every cell, the station (by rank from the head) nearest its centre. */
  _buildGrid(p) {
    const gx0 = (this.gx0 = p.x - G * CELL * 0.5), gz0 = (this.gz0 = p.z - G * CELL * 0.5);
    const cell = this.cell, cellD = this.cellD;
    cell.fill(-1); cellD.fill(1e9);
    const inv = 1 / CELL;
    for (let r = 0; r < this.count; r++) {
      const i = (this.head - r + N) % N;
      if (r > 0 && this.k[i] < 0.05) continue;
      const x = this.ox[i] - gx0, z = this.oz[i] - gz0;
      let cx0 = Math.floor((x - REACH) * inv), cx1 = Math.floor((x + REACH) * inv);
      let cz0 = Math.floor((z - REACH) * inv), cz1 = Math.floor((z + REACH) * inv);
      if (cx1 < 0 || cz1 < 0 || cx0 >= G || cz0 >= G) continue;
      if (cx0 < 0) cx0 = 0; if (cz0 < 0) cz0 = 0; if (cx1 >= G) cx1 = G - 1; if (cz1 >= G) cz1 = G - 1;
      for (let cz = cz0; cz <= cz1; cz++) {
        const ez = (cz + 0.5) * CELL - z;
        for (let cx = cx0; cx <= cx1; cx++) {
          const ex = (cx + 0.5) * CELL - x, d2 = ex * ex + ez * ez, j = cz * G + cx;
          if (d2 < cellD[j]) { cellD[j] = d2; cell[j] = r; }
        }
      }
    }
  }

  /** Rank (0 = at the broom) of the station nearest a point, or -1 if the wake is not near. */
  nearest(x, y, z) {
    const fx = (x - this.gx0) / CELL, fz = (z - this.gz0) / CELL;
    if (!(fx >= 0 && fz >= 0 && fx < G && fz < G)) return -1;
    let r = this.cell[(fz | 0) * G + (fx | 0)];
    if (r < 0) return -1;
    const ox = this.ox, oy = this.oy, oz = this.oz, n = this.count;
    let i = (this.head - r + N) % N;
    let dx = x - ox[i], dy = y - oy[i], dz = z - oz[i];
    let d2 = dx * dx + dy * dy + dz * dz;
    // walk along the trail to the closest station
    for (let step = 0; step < 10; step++) {
      if (r > 0) {
        const j = (i + 1) % N, ex = x - ox[j], ey = y - oy[j], ez = z - oz[j], e2 = ex * ex + ey * ey + ez * ez;
        if (e2 < d2) { r--; i = j; d2 = e2; continue; }
      }
      if (r < n - 1) {
        const j = (i - 1 + N) % N, ex = x - ox[j], ey = y - oy[j], ez = z - oz[j], e2 = ex * ex + ey * ey + ez * ez;
        if (e2 < d2) { r++; i = j; d2 = e2; continue; }
      }
      break;
    }
    return d2 > REACH * REACH ? -1 : r;
  }

  /**
   * Air velocity the wake adds at a point: swirl about both cores (with their images in the
   * ground, so the flow runs along it rather than through it), a draw toward the cores, and the
   * bubble of air dragged along behind the broom.
   * out[3] is the shelter there, 0..1: inside the pocket of air travelling with the broom the
   * ambient wind does not blow through, so callers scale the wind by (1 - shelter).
   * @returns how hard the air is moving across the trail there (m/s), 0 outside the wake
   */
  sample(x, y, z, out) {
    out[0] = 0; out[1] = 0; out[2] = 0; out[3] = 0;
    if (this.count < 1) return 0;
    const r = this.nearest(x, y, z);
    if (r < 0) return 0;
    const i = (this.head - r + N) % N;
    const dx = x - this.ox[i], dy = y - this.oy[i], dz = z - this.oz[i];
    const tx = this.tx[i], ty = this.ty[i], tz = this.tz[i];
    let fade = 1;
    if (r === 0) {
      // ahead of the broom the air has only just begun to move
      const along = dx * tx + dy * ty + dz * tz;
      if (along > 0) { fade = 1 - along / LEAD; if (fade <= 0) return 0; }
    }
    const lx = this.lx[i], lz = this.lz[i], ux = this.ux[i], uy = this.uy[i], uz = this.uz[i];
    const py = dx * lx + dz * lz, pz = dx * ux + dy * uy + dz * uz;
    const k = this.k[i] * fade, rc2 = this.rc2[i];
    const as = this.asym[i], kR = k * (1 + as), kL = k * (1 - as);
    const yl = this.yl[i], zl = this.zl[i], yr = this.yr[i], zr = this.zr[i];
    // right core (+k)
    const ey = py - yr, ez = pz - zr;
    let r2 = ey * ey + ez * ez;
    const rr2 = r2;
    let m = kR / (r2 + rc2);
    let vy = -ez * m, vz = ey * m;
    // air is drawn onto a ring round each core rather than into its centre, which stays hollow;
    // the ring is tight at the broom and wide further back
    const r0 = this.r0[i], kin = K_IN * this.ki[i] * fade * (1 + k * 0.025);
    const rin = 0.6 + 1.1 * r0, INV_RIN2 = 1 / (rin * rin);
    // (only from the outboard side: between the cores the air is going down, and what it carries
    // has to run out along the ground and come up the outside before a ring can take it)
    let rr = Math.sqrt(r2), e = rr - r0;
    let ob = (ey / (rr + 1e-3) + 0.25) / 0.7; ob = ob < 0 ? 0 : ob > 1 ? 1 : ob;
    let q = 1 / (1 + e * e * INV_RIN2); q = q * q * kin * (1 + as) * e / (rr + 1e-3) * ob * ob * (3 - 2 * ob);
    vy -= ey * q; vz -= ez * q;
    // left core (-k)
    const fy = py - yl, fz = pz - zl;
    r2 = fy * fy + fz * fz;
    m = -kL / (r2 + rc2);
    vy += -fz * m; vz += fy * m;
    rr = Math.sqrt(r2); e = rr - r0;
    ob = (-fy / (rr + 1e-3) + 0.25) / 0.7; ob = ob < 0 ? 0 : ob > 1 ? 1 : ob;
    q = 1 / (1 + e * e * INV_RIN2); q = q * q * kin * (1 - as) * e / (rr + 1e-3) * ob * ob * (3 - 2 * ob);
    vy -= fy * q; vz -= fz * q;
    const gk = this.gk[i];
    if (gk > 0.01) {
      let gz = pz - (zr - 2 * this.dr[i]);
      m = -kR * gk / (ey * ey + gz * gz + rc2);
      vy += -gz * m; vz += ey * m;
      gz = pz - (zl - 2 * this.dl[i]);
      m = kL * gk / (fy * fy + gz * gz + rc2);
      vy += -gz * m; vz += fy * m;
    }
    // the pocket of air travelling with the broom, wrapped round both cores
    let ga = (rr2 < r2 ? rr2 : r2) * this.irx[i];
    ga = 1 / (1 + ga * ga);
    let va = this.ax[i] * ga * fade;
    const shelter = va / this.ax0[i];
    // turbulence: eddies a few metres across, fixed to the trail (so what flies back along it is
    // buffeted as it goes) and slowly churning. Mild in the fresh wake, strong once it has aged.
    const age = this.age[i];
    const amp = k * TURB * (0.5 + 0.5 * (age < 1.2 ? age / 1.2 : 1)) * (0.25 + 0.75 * ga);
    if (amp > 0.05) {
      const t = this.time, sa = this.s[i] + dx * tx + dy * ty + dz * tz;
      const a1 = 0.83 * sa + 1.9 * pz + 2.1 * t, a2 = 1.71 * sa - 1.3 * py - 3.3 * t + 1.3, a3 = 0.41 * sa + 2.3 * py + 1.7 * pz + 1.3 * t + 4.0;
      const s1 = Math.sin(a1), c1 = Math.cos(a1), s2 = Math.sin(a2), c2 = Math.cos(a2), s3 = Math.sin(a3), c3 = Math.cos(a3);
      vy += (s1 + c2 + s3) * 0.6 * amp;
      vz += (c1 + s2 - c3) * 0.6 * amp;
      va += (s1 * c2 + 0.7 * s3 * c1) * 0.3 * amp;
    }
    out[0] = lx * vy + ux * vz + tx * va;
    out[1] = uy * vz + ty * va;
    out[2] = lz * vy + uz * vz + tz * va;
    out[3] = shelter;
    return Math.sqrt(vy * vy + vz * vz) + this.ax[i] * ga * fade * 0.12;
  }

  /** World position of a core (side -1 left, +1 right) at rank r. */
  core(r, side, out) {
    const i = (this.head - r + N) % N;
    const y = side < 0 ? this.yl[i] : this.yr[i], z = side < 0 ? this.zl[i] : this.zr[i];
    out.x = this.ox[i] + this.lx[i] * y + this.ux[i] * z;
    out.y = this.oy[i] + this.uy[i] * z;
    out.z = this.oz[i] + this.lz[i] * y + this.uz[i] * z;
    return i;
  }

  /** Wind along the ground straight under a core (m/s), counting its image. */
  groundWind(i, side) {
    const h = side < 0 ? this.hl[i] : this.hr[i];
    return 2 * this.k[i] * this.gk[i] * h / (h * h + this.rc2[i]);
  }

  _buildRibbon() {
    const P = this.aPos.array, C = this.aCore.array, Q = this.aParm.array, D = this.aDir.array, I = this.aIndex.array;
    const n = this.count;
    let ni = 0, prev = false;
    for (let r = -1; r < n; r++) {
      const i = (this.head - Math.max(r, 0) + N) % N;
      const v = (r + 1) * 2;
      const lx = this.lx[i], lz = this.lz[i];
      const hx = lz, hz = -lx;                       // level heading
      const hl = this.hl[i], hr = this.hr[i], yl = this.yl[i], yr = this.yr[i];
      const kg = r < 0 ? 0 : this.k[i] * this.gk[i];
      // a station too high or too weak to stir the ground is left out of the strip
      const hm = Math.min(hl, hr);
      const active = r < 0 ? this.k[i] * this.gk[i] > 0.05 && hm < 40 : kg > 0.05 && hm < 40 && kg / hm > 0.12;
      // (wide enough for the faint skirt of the track the wake strips through the flowers)
      const W = Math.min(30, Math.max(Math.abs(yl), Math.abs(yr)) + 2.5 * Math.max(hl, hr) + 8.0);
      const ox = this.ox[i] + (r < 0 ? hx * LEAD : 0), oz = this.oz[i] + (r < 0 ? hz * LEAD : 0);
      const axg = r < 0 ? 0 : this.ax[i] * 0.3 * this.gk[i];
      for (let e = 0; e < 2; e++) {
        const sgn = e ? 1 : -1, o3 = (v + e) * 3, o4 = (v + e) * 4;
        P[o3] = ox + lx * W * sgn; P[o3 + 1] = oz + lz * W * sgn; P[o3 + 2] = W * sgn;
        C[o4] = yl; C[o4 + 1] = hl; C[o4 + 2] = yr; C[o4 + 3] = hr;
        Q[o4] = kg; Q[o4 + 1] = this.rc2[i]; Q[o4 + 2] = axg; Q[o4 + 3] = W;
        D[o4] = lx; D[o4 + 1] = lz; D[o4 + 2] = this.irx[i]; D[o4 + 3] = this.asym[i];
      }
      if (prev && active) {
        const a = v - 2;
        I[ni++] = a; I[ni++] = a + 1; I[ni++] = a + 2; I[ni++] = a + 1; I[ni++] = a + 3; I[ni++] = a + 2;
      }
      prev = active;
    }
    const nv = (n + 1) * 2;
    for (const [a, c] of [[this.aPos, 3], [this.aCore, 4], [this.aParm, 4], [this.aDir, 4]]) {
      a.clearUpdateRanges(); a.addUpdateRange(0, nv * c); a.needsUpdate = true;
    }
    this.aIndex.clearUpdateRanges(); this.aIndex.addUpdateRange(0, ni); this.aIndex.needsUpdate = true;
    this.ribbon.setDrawRange(0, ni);
  }
}
