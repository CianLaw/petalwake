// Coming in to land on a pad, getting off the broom, waiting there, getting back on and leaving.
// While any of that is going on this flies the broom (flight.auto), poses the rider (rider.seat,
// rider.off) and has the camera circle her (chase.circle).
//
//   approach  the planned way in (approach.js): reined in to a canter, bled off to a walk, flared
//   settle    the last hand's breadth down
//   dismount  a hop off the broom: crouch, spring, a puff of dust at the top of it (which is where
//             the seated model gives way to the standing one), a turn in the air to face the view,
//             boots down on the mark with a squash
//   landed    she stands there for as long as you like
//   mount     the hop back on
//   launch    off the edge the way she was facing, a dip to pick up speed, and the broom is yours
//
// A pad says which way to come in and which way she faces. Both are checked against what really
// stands round it (way()): if a neighbour blocks the line, the nearest clear heading is flown
// instead, and a pad with no way in at all is left alone.
//
// Pads are small and often have a wall at the back (a gallery round a tower). A broom is longer
// than such a pad is deep, so it stops short - `hover`, nose just off the wall - and she hops the
// rest of the way on to the mark (`spot`); it waits for her at `away`, tail just off the wall,
// facing out. On an open pad all three are the middle of it.
//
// The standing rider is a model of its own (rider.standing, from rider_stand.glb). Until there is
// one she stays on the broom and sets it down on its bristles, nose in the air.
import * as THREE from 'three';
import { planApproach, APPROACH } from './approach.js';
import { SPEEDS } from '../player/flight.js';
import { puff, dustRing, twinkle, PALE } from './sparks.js';

const TAU = Math.PI * 2;
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const damp = (cur, target, rate, dt) => cur + (target - cur) * (1 - Math.exp(-rate * dt));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a), 0, 1);          // 0..1 across [a, b]
const smooth = (t) => t * t * (3 - 2 * t);
const easeOut = (t) => 1 - (1 - t) * (1 - t);
const easeIn = (t) => t * t;
const ring = (t, w, z) => (t < 0 ? 0 : Math.exp(-z * t) * Math.cos(w * t));   // a damped wobble, 1 at t = 0
const turn = (a) => Math.atan2(Math.sin(a), Math.cos(a));         // an angle brought into -pi..pi

export const LAND = {
  RANGE: 60,        // m: a pad this close can be landed on
  V_APP: 12,        // m/s held on the way round to the final
  V_WALK: 1.5,      // m/s over the last of the way
  BLEED: 0.62,      // 1/s: how the speed runs off with the distance left (v = V_WALK + BLEED * left)
  BRAKE: 1.9,       // 1/s: how hard the broom is reined in when the landing begins
  BANK: 0.6,        // rad: the most it leans into the turns on the way round
  FLARE: 0.30,      // rad: nose-up as it arrives
  FLARE_D: 7,       // m from the end at which the flare begins
  PIVOT_D: 2.4,     // m from the end at which the broom starts to square up to the view (no standing model)
  CAM_D: 6,         // m from the end at which the camera starts to come round
  CAM_OUT: 6,       // m out from the pad, leaving, at which it falls in behind her again
  NOSE: 1.5,        // m: room the broom needs ahead of its middle (handle and lantern, and a little)
  TAIL: 1.45,       // m: ...and behind it (the bristles)
  WALL: 0.9,        // m above a pad's floor: anything taller beside it is a wall, not a kerb
  SIT: 0.44,        // rad: nose-up of the broom once it is set down (when there is no standing model)
  T_OFF: 1.2,       // s: the dismount
  T_SWAP: 0.46,     // s into it: the top of the hop, where the models change places
  T_TOUCH: 0.78,    // s into it: boots on the floor
  T_ON: 0.62,       // s: the hop back on, up to the moment the broom moves off
  T_LAUNCH: 1.7,    // s: from moving off to handing the broom back at a cruise
  IN_SLOPE: 0.8,    // a way in is open if a descent no steeper than this clears what stands along it...
  OUT_SLOPE: 0.5,   // ...and a way out if a climb no steeper than this does
  ORBIT: { dist: 6.6, height: 1.9, spin: 0.085, fov: 56 },
};

const _o = { x: 0, y: 0, z: 0, yaw: 0, k: 0, slope: 0 };
// headings tried, as offsets from the pad's own, when something stands in the way it gives
const SWEEP = [0, 25, -25, 50, -50, 75, -75, 105, -105, 135, -135, 165, -165, 180].map((d) => (d * Math.PI) / 180);

export class Landing {
  /**
   * @param game  the game object (flight, rider, chase, fx, sound, terrain)
   * @param on    { touch(pad), leave(pad), broke() } - boots on the pad; moving off it; landing broken off
   */
  constructor(game, on = {}) {
    this.game = game;
    this.on = on;
    this.state = 'fly';
    this.pad = null;
    this.t = 0;
    this.path = null;
    this.s = 0;                 // metres along the path, and the speed along it
    this.v = 0;
    this.yaw = 0; this.pitch = 0; this.roll = 0;
    this.piv = { on: false, t: 0, T: 1, from: 0, d: 0 };
    this.hover = new THREE.Vector3();   // where the broom stops (its middle, at hover height)
    this.spot = new THREE.Vector3();    // where she stands: over the middle of the pad
    this.away = new THREE.Vector3();    // where the broom waits for her to get back on
    this.focus = new THREE.Vector3();   // what the camera circles
    this.rest = APPROACH.HOVER;         // height of flight.pos over the pad's floor once she is off / has set the broom down
    this.since = 1e9;                   // seconds since she got back on (the broom is still bobbing under her)
    this.cam = false;
    this.stand = false;                 // is there a standing model to change to (else the broom is set down)
    this.spin = false;                  // does she turn to face the view in the hop (else the broom turns first)
    this.fired = {};
    this.dep = null;
    this.out = 0;                       // the heading she leaves on
    this._ways = new WeakMap();         // pad -> the ways on and off it that are open (see way())
    this.script = { step: (dt, time, f) => this._step(dt, time, f), quiet: false };
  }

  get busy() { return this.state !== 'fly'; }
  get landed() { return this.state === 'landed'; }

  /** Top of the land, the water or a building at (x, z), as far as landing on `pad` goes. */
  _floor(pad, x, z) {
    const g = this.game, f = g.flight;
    let h = Math.max(g.terrain.heightAt(x, z), 0);
    if (f.river) { const r = f.river.levelAt(x, z); if (r > h) h = r; }
    if (f.solid) {
      // (on the pad itself its own floor is the truth: the grid of roof heights is too coarse to
      // tell a mark painted at the foot of a wall from the wall)
      if (pad && (x - pad.pos.x) ** 2 + (z - pad.pos.z) ** 2 < (pad.radius + 0.6) ** 2) h = Math.max(h, pad.pos.y);
      else { const s = f.solid.heightAt(x, z); if (s > h) h = s; }
    }
    return h;
  }

  floorAt(x, z) { return this._floor(this.pad, x, z); }

  /**
   * The ways on to and off a pad that are really open, going by what stands round it: the pad's
   * own approach and facing where nothing is in them, else the nearest headings that are clear
   * (a neighbour may have been built across the line since the pad was laid out).
   * @returns { approach, short, depart, back, own } - headings, how far the broom stands off the
   *          middle of the pad on each, and whether both are the pad's own - or null: no way in.
   */
  way(pad) {
    if (this._ways.has(pad)) return this._ways.get(pad);
    let w = null;
    const inn = this._firstClear(pad.approach, (a) => this._clearIn(pad, a));
    const out = inn && this._firstClear(pad.yaw, (a) => this._clearOut(pad, a));
    if (out) w = { approach: inn.a, short: inn.v, depart: out.a, back: out.v, own: inn.i === 0 && out.i === 0 };
    this._ways.set(pad, w);
    return w;
  }

  /** The buildings have changed: what was open may not be. */
  forget() { this._ways = new WeakMap(); }

  _firstClear(a0, test) {
    for (let i = 0; i < SWEEP.length; i++) { const v = test(a0 + SWEEP[i]); if (v >= 0) return { a: a0 + SWEEP[i], v, i }; }
    return null;
  }

  /** Can the broom come down on to `pad` flying heading a? @returns how far short it stops, or -1. */
  _clearIn(pad, a) {
    const A = APPROACH, L = LAND;
    const short = this._standoff(pad, a, L.NOSE);
    const dx = Math.sin(a), dz = -Math.cos(a), rx = -dz, rz = dx;
    const hx = pad.pos.x - dx * short, hz = pad.pos.z - dz * short, y0 = pad.pos.y + A.HOVER + A.SETTLE - A.BOOT + 0.2;
    for (let d = 0.5; d <= 13; d += 0.5) {
      const x = hx - dx * d, z = hz - dz * d, y = y0 + d * L.IN_SLOPE;
      if (this._floor(pad, x, z) > y || this._floor(pad, x + rx * 0.7, z + rz * 0.7) > y || this._floor(pad, x - rx * 0.7, z - rz * 0.7) > y) return -1;
    }
    return short;
  }

  /** Can it leave `pad` on heading a? @returns how far out from the middle it waits for her, or -1. */
  _clearOut(pad, a) {
    const A = APPROACH, L = LAND;
    const back = this._standoff(pad, a + Math.PI, L.TAIL);
    const dx = Math.sin(a), dz = -Math.cos(a), rx = -dz, rz = dx;
    const wx = pad.pos.x + dx * back, wz = pad.pos.z + dz * back, y0 = pad.pos.y + A.HOVER - A.BOOT + 0.4;
    for (let d = 0.5; d <= 14; d += 0.5) {
      const x = wx + dx * d, z = wz + dz * d, y = y0 + d * L.OUT_SLOPE;
      if (this._floor(pad, x, z) > y || this._floor(pad, x + rx * 0.7, z + rz * 0.7) > y || this._floor(pad, x - rx * 0.7, z - rz * 0.7) > y) return -1;
    }
    return back;
  }

  /**
   * How far from the middle of a pad the broom's own middle has to stay for `reach` metres of it
   * to fit in front of a wall that stands along `dir` (a heading) from there. 0 on an open pad.
   */
  _standoff(pad, dir, reach) {
    const S = this.game.flight.solid;
    if (!S) return 0;
    const dx = Math.sin(dir), dz = -Math.cos(dir);
    for (let d = 0; d <= reach; d += 0.25) {
      if (S.heightAt(pad.pos.x + dx * d, pad.pos.z + dz * d) > pad.pos.y + LAND.WALL) return clamp(reach - d + 0.25, 0, reach + 0.25);
    }
    return 0;
  }

  /**
   * Which way round a pad a camera `dist` out and `height` up can see her: null if every way,
   * else { mid, half } - the middle of the widest open stretch (a bearing) and half its width.
   */
  _openArc(pad, dist, height) {
    const S = this.game.flight.solid, T = this.game.terrain;
    if (!S) return null;
    const N = 36, open = [], F = this.focus;
    let all = true;
    for (let k = 0; k < N; k++) {
      const az = (k / N) * TAU, sx = Math.sin(az), sz = -Math.cos(az);
      let ok = true;
      for (let j = 3; j <= 10 && ok; j++) {
        const u = j / 10, x = F.x + sx * dist * u, z = F.z + sz * dist * u, y = F.y + 0.2 + (height - 0.2) * u;
        if (Math.max(S.heightAt(x, z), T.heightAt(x, z)) > y - 0.5) ok = false;
      }
      open.push(ok);
      if (!ok) all = false;
    }
    if (all) return null;
    let best = 0, at = 0;
    for (let k = 0; k < N; k++) {
      if (!open[k] || open[(k + N - 1) % N]) continue;      // k starts a run
      let n = 0;
      while (n < N && open[(k + n) % N]) n++;
      if (n > best) { best = n; at = k; }
    }
    if (best < 3) return { mid: pad.yaw, half: 0.2 };       // hemmed in: stay out in front of her
    const step = TAU / N;
    return { mid: (at + (best - 1) / 2) * step, half: Math.max(0.2, ((best - 1) / 2) * step - 0.26) };
  }

  _set(state) { this.state = state; this.t = 0; this.fired = {}; }
  _once(key) { if (this.fired[key]) return false; this.fired[key] = true; return true; }

  /** Start a landing on `pad` from wherever the broom is. @returns false if there is no way in. */
  begin(pad) {
    if (this.busy) return false;
    const w = this.way(pad);
    if (!w) return false;
    const f = this.game.flight, A = APPROACH, L = LAND;
    this.pad = pad;
    this.stand = !!this.game.rider.standing;      // (decided once: the model may arrive while she is on her way in)
    this.out = w.depart;
    const ax = Math.sin(w.approach), az = -Math.cos(w.approach);
    // She turns to face the view in the air, as she hops off. (Without a standing model the broom
    // turns under her first, hovering - unless it is stood off from a wall, where there is no
    // room to swing it: then broom and all go round in the hop.)
    this.spin = this.stand || w.short > 0.05;
    this.spot.set(pad.pos.x, pad.pos.y + A.HOVER, pad.pos.z);
    this.hover.set(pad.pos.x - ax * w.short, pad.pos.y + A.HOVER, pad.pos.z - az * w.short);
    this.away.set(pad.pos.x + Math.sin(w.depart) * w.back, pad.pos.y + A.HOVER, pad.pos.z - Math.cos(w.depart) * w.back);
    this.focus.set(pad.pos.x, pad.pos.y + 1.15, pad.pos.z);
    const hs = Math.hypot(f.vel.x, f.vel.z);
    const path = planApproach(
      { x: f.pos.x, y: f.pos.y, z: f.pos.z, yaw: f.yaw, slope: Math.tan(clamp(f.pitch, -0.6, 0.6)), speed: hs, run: Math.max(0, hs - L.V_APP) / L.BRAKE },
      { x: this.hover.x, y: this.hover.y + A.SETTLE, z: this.hover.z, approach: w.approach },
      (x, z) => this.floorAt(x, z),
    );
    if (!path) { this.pad = null; return false; }
    this.path = path;
    this.s = 0; this.v = Math.max(hs, 4);
    this.yaw = f.yaw; this.pitch = f.pitch; this.roll = f.roll;
    this.piv.on = false;
    this.cam = false;
    this.since = 1e9;
    this.script.quiet = false;
    this._boost = true;                       // (a boost already held does not count as breaking off)
    f.auto = this.script;
    this._set('approach');
    this.game.sound?.whoosh?.(0.35);
    return true;
  }

  /** Get back on and go. */
  takeoff() {
    if (this.state !== 'landed') return false;
    this._set('mount');
    return true;
  }

  /** Let go of the broom wherever it is (a landing broken off, or the rider moved from outside). */
  abort() {
    const g = this.game, f = g.flight, r = g.rider;
    if (f.auto === this.script) {
      f.auto = null;
      f.speed = Math.max(f.speed, SPEEDS.VMIN);
      if (this.state !== 'approach') { f.pitch = 0; f.roll = 0; }
    }
    r.seat.hop = 0; r.seat.sy = 1; r.seat.calm = 0;
    r.off.on = false; r.off.y = 0; r.off.sy = 1;
    if (this.cam) g.chase.release(0.6);
    this.cam = false;
    this.pad = null; this.path = null; this.dep = null;
    this.since = 1e9;
    this._set('fly');
  }

  /** Once a step, before the flight model: notice the broom being taken away, a landing broken off. */
  update(dt, ctl) {
    if (!this.busy) return;
    const f = this.game.flight;
    if (f.auto !== this.script) { this.abort(); return; }       // placed elsewhere by something else
    if (this.state === 'approach') {
      // a fresh touch of the gust breaks the landing off (not in the last few metres)
      const boost = !!(ctl && ctl.boost);
      if (boost && !this._boost && this.t > 0.25 && this.path.len - this.s > 7) { this.abort(); this.on.broke?.(); return; }
      this._boost = boost;
    }
  }

  // ------------------------------------------------------------------------------- the script
  _step(dt, time, f) {
    this.t += dt;
    this.since += dt;
    switch (this.state) {
      case 'approach': this._approach(dt, f); break;
      case 'settle': this._settle(dt, f); break;
      case 'dismount': this._dismount(dt, f); break;
      case 'landed': this._wait(dt, f); break;
      case 'mount': this._mount(dt, f); break;
      case 'launch': this._launch(dt, f); break;
      default: f.auto = null;
    }
    this._pose();
  }

  _move(f, x, y, z, dt) {
    const inv = 1 / Math.max(dt, 1e-4);
    f.vel.set((x - f.pos.x) * inv, (y - f.pos.y) * inv, (z - f.pos.z) * inv);
    f.pos.set(x, y, z);
    f.speed = f.vel.length();
  }

  _approach(dt, f) {
    const P = this.path, L = LAND, g = this.game;
    let left = P.len - this.s;
    // rein in to the approach speed, then let it run off to a walk over the last of the way
    const want = Math.min(L.V_APP, L.V_WALK + left * L.BLEED);
    this.v += (want - this.v) * (1 - Math.exp(-(this.v > want ? L.BRAKE : 1.3) * dt));
    this.s = Math.min(P.len, this.s + this.v * dt);
    left = P.len - this.s;
    const o = P.at(this.s, _o);
    // (the plan was laid over a metre-by-metre sounding of what is underneath: never under the real thing)
    const y = Math.max(o.y, this.floorAt(o.x, o.z) + 0.72);
    this._move(f, o.x, y, o.z, dt);

    // heading: along the path. With no standing model to turn in the air, the broom itself squares
    // up to the view as it drifts in
    const prev = this.yaw;
    if (!this.spin && !this.piv.on && left < L.PIVOT_D) this._pivot(o.yaw);
    this.yaw = this.piv.on ? this._pivoted(dt) : o.yaw;
    const rate = turn(this.yaw - prev) / Math.max(dt, 1e-4);
    // nose along the path, coming up into a flare as the speed comes off
    const flare = 1 - smooth(seg(left, 1.2, L.FLARE_D));
    this.pitch = damp(this.pitch, Math.atan(o.slope) * (1 - flare) + L.FLARE * flare, 6, dt);
    this.roll = damp(this.roll, clamp(rate / 1.4, -1, 1) * L.BANK * clamp(this.v / 9, 0.3, 1), 4.6, dt);
    f.yaw = this.yaw; f.pitch = this.pitch; f.roll = this.roll;

    this.script.quiet = left < 4;
    if (!this.cam && left < L.CAM_D) {
      this.cam = true;
      g.chase.circle(this.focus, { ...L.ORBIT, seconds: 1.8, skip: this.pad.radius + 1.0, arc: this._openArc(this.pad, L.ORBIT.dist + 0.8, L.ORBIT.height + 0.5) });
    }
    if (left <= 1e-3) this._set('settle');
  }

  _pivot(from) {
    const p = this.piv, d = turn(this.pad.yaw - from);
    p.on = true; p.t = 0; p.from = from; p.d = d; p.T = 0.4 + 0.5 * Math.abs(d);
  }

  _pivoted(dt) {
    const p = this.piv;
    p.t += dt;
    const u = clamp(p.t / p.T, 0, 1);
    return p.from + p.d * u * u * u * (u * (u * 6 - 15) + 10);
  }

  _settle(dt, f) {
    const H = this.hover, g = this.game;
    const k = 1 - Math.exp(-dt * 6), ky = 1 - Math.exp(-dt * 5);
    this._move(f, f.pos.x + (H.x - f.pos.x) * k, f.pos.y + (H.y - f.pos.y) * ky, f.pos.z + (H.z - f.pos.z) * k, dt);
    const prev = this.yaw;
    let turned = true;
    if (!this.spin) {
      if (!this.piv.on) this._pivot(this.yaw);
      this.yaw = this._pivoted(dt);
      turned = this.piv.t >= this.piv.T;
    }
    const rate = turn(this.yaw - prev) / Math.max(dt, 1e-4);
    this.pitch = damp(this.pitch, 0, 4.5, dt);
    this.roll = damp(this.roll, clamp(rate / 2.6, -1, 1) * 0.3, 5, dt);
    f.yaw = this.yaw; f.pitch = this.pitch; f.roll = this.roll;
    this.script.quiet = true;
    const done = turned && this.t > 0.4 && Math.hypot(H.x - f.pos.x, H.y - f.pos.y, H.z - f.pos.z) < 0.04 && Math.abs(this.pitch) < 0.03;
    if (done || this.t > 4) {
      // where flight.pos ends up: at hover height over the mark (she is standing under it), or -
      // no standing model - as low as the broom sits when it is set down nose-up
      this.rest = this.stand ? APPROACH.HOVER : Math.max(g.rider.restHeight(LAND.SIT) - 0.02, 0.3);
      this.from = this.yaw;
      this._set('dismount');
    }
  }

  _dismount(dt, f) {
    const L = LAND, g = this.game, pad = this.pad, t = this.t, H = this.hover, S = this.spot;
    const stand = this.stand;
    // from the broom's place to hers: with the hop (and, on her own feet, only once she has left the broom)
    const go = smooth(seg(t, stand ? L.T_SWAP - 0.04 : 0.2, L.T_TOUCH - 0.02));
    const down = stand ? 0 : smooth(seg(t, 0.36, L.T_TOUCH));
    this._move(f, lerp(H.x, S.x, go), pad.pos.y + lerp(APPROACH.HOVER, this.rest, down), lerp(H.z, S.z, go), dt);
    // she turns in the air to come down facing the view
    if (this.spin) this.yaw = this.from + turn(pad.yaw - this.from) * (stand ? easeOut(seg(t, L.T_SWAP - 0.04, L.T_TOUCH - 0.04)) : smooth(seg(t, 0.2, L.T_TOUCH - 0.04)));
    else this.yaw = pad.yaw;
    this.pitch = stand ? damp(this.pitch, 0, 6, dt) : L.SIT * smooth(seg(t, 0.2, L.T_TOUCH - 0.02));
    this.roll = damp(this.roll, 0, 6, dt);
    f.yaw = this.yaw; f.pitch = this.pitch; f.roll = this.roll;

    const sun = g.fx.sunTint(g.rider.sunVis);
    if (t >= L.T_SWAP - 0.06 && this._once('puff')) {
      // the top of the hop: a ball of dust and a few petals, and she is on her feet behind it
      puff(g.fx, H.x, pad.pos.y + 1.3, H.z, stand ? 17 : 10, sun, 0.5, 1.7);
      twinkle(g.fx, H.x, pad.pos.y + 1.35, H.z, 10, PALE, 2.4, 0, 0.5, 0, 0.7);
      g.fx.burst(H.x, pad.pos.y + 1.25, H.z, 9, 0.2, 0.3 + 0.7 * g.rider.sunVis, 2.4);
      g.sound?.whoosh?.(0.3);
    }
    if (t >= L.T_TOUCH && this._once('touch')) {
      dustRing(g.fx, S.x, pad.pos.y, S.z, 0.3, 18, sun);
      g.sound?.thump?.(0.7);
      this.on.touch?.(pad);
    }
    if (t >= L.T_OFF) this._set('landed');
  }

  _wait(dt, f) {
    this._move(f, this.spot.x, this.pad.pos.y + this.rest, this.spot.z, dt);
    f.yaw = this.yaw = this.pad.yaw; f.roll = this.roll = 0;
    f.pitch = this.pitch = this.stand ? 0 : LAND.SIT;
  }

  _mount(dt, f) {
    const L = LAND, g = this.game, pad = this.pad, t = this.t, S = this.spot, W = this.away;
    const stand = this.stand;
    const go = smooth(seg(t, 0.16, 0.56));                  // from her place to where the broom waits
    const up = stand ? 1 : smooth(seg(t, 0.14, 0.44));
    this._move(f, lerp(S.x, W.x, go), pad.pos.y + lerp(this.rest, APPROACH.HOVER, up), lerp(S.z, W.z, go), dt);
    this.pitch = stand ? 0 : L.SIT * (1 - smooth(seg(t, 0.12, 0.46)));
    // (the way out is the way she is facing, unless something has been built across it)
    f.yaw = this.yaw = pad.yaw + turn(this.out - pad.yaw) * smooth(seg(t, 0.14, 0.44)); f.pitch = this.pitch; f.roll = this.roll = 0;
    if (t >= 0.36 && this._once('puff')) {
      const sun = g.fx.sunTint(g.rider.sunVis);
      puff(g.fx, f.pos.x, pad.pos.y + 1.25, f.pos.z, stand ? 15 : 9, sun, 0.5, 1.6);
      dustRing(g.fx, S.x, pad.pos.y, S.z, 0.3, 12, sun);
      g.sound?.whoosh?.(0.3);
    }
    if (t >= 0.40 && this._once('swap')) this.since = 0;
    this.focus.lerp(f.pos, 1 - Math.exp(-dt * 3));
    if (t >= L.T_ON) this._depart(f);
  }

  /** Lay out the way off the pad: up over its edge, out the way she faces, a dip beyond it. */
  _depart(f) {
    const pad = this.pad, A = APPROACH, W = this.away, g = this.game;
    const dx = Math.sin(this.out), dz = -Math.cos(this.out), rx = -dz, rz = dx;
    const base = pad.pos.y + A.HOVER, N = 44;
    const fl = new Float64Array(N), ys = new Float64Array(N);
    for (let i = 0; i < N; i++) {
      const x = W.x + dx * i, z = W.z + dz * i;
      fl[i] = Math.max(this.floorAt(x, z), this.floorAt(x + rx * 0.7, z + rz * 0.7), this.floorAt(x - rx * 0.7, z - rz * 0.7));
    }
    // the edge: where the floor falls away from under the platform
    let edge = Math.ceil(pad.radius) + 1;
    for (let i = 0; i < 16; i++) if (fl[i] < pad.pos.y - 1.2) { edge = i; break; }
    let lift = 0.3, beyond = -1e9;
    for (let i = 0; i <= edge; i++) lift = Math.max(lift, fl[i] + A.BOOT - base);
    for (let i = edge + 2; i < Math.min(N, edge + 28); i++) beyond = Math.max(beyond, fl[i]);
    const dip = clamp(base - beyond - 3.2, 0, 2.6);
    for (let i = 0; i < N; i++) {
      const out = i - edge;
      const y = base + lift * smooth(seg(i, 0, 1.4)) - (lift + dip) * smooth(seg(out, 0, 8)) + (0.55 * dip + 0.4) * smooth(seg(out, 9, 26));
      ys[i] = Math.max(y, fl[i] + (i <= edge ? A.BOOT : 1.7));
    }
    for (let i = N - 2; i >= 0; i--) if (ys[i] < ys[i + 1] - 0.8) ys[i] = ys[i + 1] - 0.8;
    for (let pass = 0; pass < 2; pass++) for (let i = 1; i < N - 1; i++) ys[i] = Math.max(0.25 * ys[i - 1] + 0.5 * ys[i] + 0.25 * ys[i + 1], Math.min(ys[i], fl[i] + 0.8));
    ys[0] = base;
    this.dep = { x: W.x, z: W.z, dx, dz, ys, d: 0 };
    this.v = 0;
    this.on.leave?.(pad);
    g.sound?.whoosh?.(0.8, true);
    dustRing(g.fx, this.spot.x, pad.pos.y, this.spot.z, 0.5, 16, g.fx.sunTint(g.rider.sunVis));
    this._set('launch');
  }

  _launch(dt, f) {
    const L = LAND, D = this.dep, t = this.t;
    // a moment to lift and drift to the lip, then away
    this.v = t < 0.35 ? 5 * smooth(t / 0.35) : 5 + (SPEEDS.CRUISE - 5) * smooth(seg(t, 0.35, L.T_LAUNCH));
    D.d += this.v * dt;
    const n = D.ys.length, fi = clamp(D.d, 0, n - 1.001), i = Math.floor(fi), u = fi - i;
    const y = lerp(D.ys[i], D.ys[i + 1], u);
    this._move(f, D.x + D.dx * D.d, y, D.z + D.dz * D.d, dt);
    this.pitch = damp(this.pitch, Math.atan(D.ys[i + 1] - D.ys[i]), 5, dt);
    f.yaw = this.yaw = this.out; f.pitch = this.pitch; f.roll = this.roll = damp(this.roll, 0, 5, dt);
    this.script.quiet = D.d < 5;
    this.focus.lerp(f.pos, 1 - Math.exp(-dt * 14));
    // The camera watches her go from where it was, and falls in behind once she is clear of the
    // pad. (Behind her while she stands there is, as often as not, inside the tower.)
    if (this.cam && D.d > LAND.CAM_OUT) { this.cam = false; this.game.chase.release(1.2); }
    if (t >= L.T_LAUNCH || D.d > n - 2) {
      // the broom is hers again, at a cruise, on the heading and slope it has
      if (this.cam) { this.cam = false; this.game.chase.release(1.0); }
      f.auto = null;
      f.speed = Math.max(this.v, SPEEDS.SLOW);
      f.vel.copy(f.fwd).multiplyScalar(f.speed);
      this.pad = null; this.path = null; this.dep = null;
      this._set('fly');
    }
  }

  /** The rider's pose for where the landing has got to: the hop, the squash, which model shows. */
  _pose() {
    const g = this.game, r = g.rider, seat = r.seat, off = r.off, L = LAND, t = this.t;
    const stand = this.stand && !!r.standing;
    seat.hop = 0; seat.sy = 1; seat.calm = 0;
    off.on = false; off.y = 0; off.sy = 1;
    const floorY = this.pad ? this.pad.pos.y - g.flight.pos.y : 0;     // the pad's floor, in the rider's frame
    if (this.state === 'dismount') {
      // crouch, spring up, fall, land
      const crouch = smooth(seg(t, 0, 0.18)), rise = easeOut(seg(t, 0.18, L.T_SWAP + 0.02)), fall = easeIn(seg(t, L.T_SWAP + 0.02, L.T_TOUCH));
      const sy = t < L.T_TOUCH ? lerp(lerp(lerp(1, 0.84, crouch), 1.16, rise), 1.02, fall) : 1 - 0.2 * ring(t - L.T_TOUCH, 15, 8);
      const hop = lerp(lerp(lerp(0, -0.07, crouch), 0.52, rise), 0, fall);
      if (stand && t >= L.T_SWAP) {
        off.on = true; off.sy = sy;
        off.y = floorY + 0.42 * (1 - easeIn(seg(t, L.T_SWAP, L.T_TOUCH)));
      } else { seat.hop = hop; seat.sy = sy; }
      seat.calm = stand ? 0 : smooth(seg(t, 0.1, 0.6));
    } else if (this.state === 'landed') {
      if (stand) { off.on = true; off.y = floorY; } else seat.calm = 1;
    } else if (this.state === 'mount') {
      const crouch = smooth(seg(t, 0, 0.16)), rise = easeOut(seg(t, 0.16, 0.42));
      const sy = lerp(lerp(1, 0.82, crouch), 1.15, rise), hop = 0.5 * rise;
      if (t < 0.40) {
        if (stand) { off.on = true; off.y = floorY + hop; off.sy = sy; } else { seat.hop = hop * 0.8; seat.sy = sy; seat.calm = 1 - smooth(seg(t, 0.1, 0.4)); }
      }
    }
    // back on the broom: it dips under her and bobs back (through the first of the launch too)
    if (this.since < 1.4 && (this.state === 'mount' || this.state === 'launch')) {
      const k = stand ? 0.42 : 0.3;
      seat.hop += k * ring(this.since, 9, 5.5);
      seat.sy *= 1 + 0.13 * ring(this.since, 13, 7);
    }
  }
}
