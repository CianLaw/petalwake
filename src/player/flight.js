// Broom flight: an arcade model tuned for skimming. No fail state - the ground has a soft cushion,
// a dive rounds itself out before it gets there and lands with a bounce, walls shove you off, and
// the wind turns you home if you wander out to sea.
import * as THREE from 'three';
import { World } from '../core/ctx.js';
import { waveHeight } from '../world/water.js';

const CRUISE = 33, BOOST = 62, SLOW = 13, VMIN = 8, VMAX = 92;
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const damp = (cur, target, rate, dt) => cur + (target - cur) * (1 - Math.exp(-rate * dt));
const smooth01 = (x) => { const t = clamp(x, 0, 1); return t * t * (3 - 2 * t); };
const CLEAR = 1.15;        // skim height: boots just brushing the flower heads
const FLARE_RATE = 1.5;    // rad/s: how hard the automatic pull-out likes to turn the nose up

export class Flight {
  constructor(terrain) {
    this.terrain = terrain;
    this.pos = new THREE.Vector3(0, 120, 0);
    this.vel = new THREE.Vector3();
    this.fwd = new THREE.Vector3(0, 0, -1);
    this.yaw = 0;      // radians, 0 = north (-z), positive turns east (+x)
    this.pitch = 0;    // radians, positive = nose up
    this.roll = 0;     // visual bank, positive = right wing down
    this.speed = CRUISE;
    this.turnRate = 0;
    this.pitchRate = 0;
    this.gust = 0.35;  // boost meter 0..1
    this.boosting = 0; // 0..1 smoothed
    this.agl = 100;    // height above ground or sea
    this.overWater = false;
    this.surfaceY = 0;
    this.bump = 0;     // impact impulse for camera shake
    this.accel = new THREE.Vector3();
    this.homing = 0;   // 0..1 when the wind is steering us back
    this.time = 0;
    this.holdAgl = -1;
    this.flare = 0;      // 0..1 while the broom is pulling itself out of a dive
    this.bob = 0;        // landing bounce: offset from the riding height (m) and its speed
    this.bobV = 0;
    this.touchdown = 0;  // set for one step when a dive lands: how hard (m/s)
    this._sink = 0;
    this._air = false;
    this._n = new THREE.Vector3();
    this._wn = new THREE.Vector3();
    this._prevVel = new THREE.Vector3();
  }

  place(x, z, agl, yawDeg) {
    this.pos.set(x, this.surfaceAt(x, z, 0) + agl, z);
    this.yaw = (yawDeg * Math.PI) / 180;
    this.pitch = 0; this.roll = 0; this.turnRate = 0; this.pitchRate = 0;
    this.speed = CRUISE;
    this.holdAgl = -1;
    this.agl = agl;
    this.flare = 0; this.bob = 0; this.bobV = 0; this.touchdown = 0; this._sink = 0; this._air = false;
    this._dir();
    this.vel.copy(this.fwd).multiplyScalar(this.speed);
    this._prevVel.copy(this.vel);
  }

  /** Top of whatever is below: terrain or the swell. */
  surfaceAt(x, z, t) {
    const h = this.terrain.heightAt(x, z);
    if (this.river) { const r = this.river.levelAt(x, z); if (r > h) return r; }
    if (h > 0.4) return h;
    const w = waveHeight(x, z, t, 0.8);
    return Math.max(h, w);
  }

  /** Turn the heading so it runs along a wall with horizontal normal (nx, nz). */
  _slide(nx, nz, strength, dt) {
    const fl = Math.hypot(this.fwd.x, this.fwd.z) || 1;
    const fx = this.fwd.x / fl, fz = this.fwd.z / fl;
    const d = fx * nx + fz * nz;
    if (d >= 0) return 0;
    const rx = fx - 1.35 * d * nx, rz = fz - 1.35 * d * nz;
    let dy = Math.atan2(rx, -rz) - this.yaw;
    dy = Math.atan2(Math.sin(dy), Math.cos(dy));
    this.yaw += dy * Math.min(1, dt * 15 * strength);
    return -d;     // how head-on the approach was: 0 glancing .. 1 square on
  }

  /**
   * How fast the nose must come up (rad/s) for the dive we are in to round out above the ground:
   * the gentlest circular arc, starting now, that stays clear of everything along the heading.
   * 0 when there is room to spare.
   */
  _pullOut(time) {
    const g0 = this.pitch;
    if (g0 > -0.10) return 0;
    const V = this.speed, T = this.terrain;
    const dx = Math.sin(this.yaw), dz = -Math.cos(this.yaw);
    const px = this.pos.x, py = this.pos.y, pz = this.pos.z;
    const sg = Math.sin(g0), cg = Math.cos(g0);
    const margin = CLEAR + 0.45;
    const clears = (w) => {
      const R = V / w;
      for (let i = 1; i <= 6; i++) {
        const g = g0 * (1 - i / 6);                         // along the arc, until level
        const x = R * (Math.sin(g) - sg), y = py - R * (Math.cos(g) - cg);
        const sx = px + dx * x, sz = pz + dz * x;
        if (y - this.surfaceAt(sx, sz, time) < margin) {
          // a cliff face in the way is not somewhere to land: the wall code deals with those
          if (T.heightAt(sx, sz) > 0.4 && T.normalAt(sx, sz, this._n, 2.0).y < 0.62) continue;
          return false;
        }
      }
      return true;
    };
    let lo = 0.3, hi = 4.0;
    if (clears(lo)) return 0;
    if (!clears(hi)) return hi;
    for (let i = 0; i < 6; i++) { const mid = 0.5 * (lo + hi); if (clears(mid)) hi = mid; else lo = mid; }
    return hi;
  }

  _dir() {
    const cp = Math.cos(this.pitch);
    this.fwd.set(Math.sin(this.yaw) * cp, Math.sin(this.pitch), -Math.cos(this.yaw) * cp);
  }

  update(dt, input, time) {
    this.time = time;
    const T = this.terrain;

    // ---- steering
    const speedK = clamp((this.speed - VMIN) / (CRUISE - VMIN), 0.35, 1.6);
    const maxTurn = 1.28 / Math.pow(speedK, 0.42);
    let turnIn = input.turn, pitchIn = input.pitch;

    // the wind turns you home when you stray far out to sea
    const r = Math.hypot(this.pos.x, this.pos.z);
    const edge = World.half * 0.90;
    const homeK = clamp((r - edge) / 260, 0, 1);
    this.homing = damp(this.homing, homeK, 2, dt);
    if (homeK > 0) {
      const toHome = Math.atan2(-this.pos.x, this.pos.z); // yaw that points at the origin
      let d = toHome - this.yaw;
      d = Math.atan2(Math.sin(d), Math.cos(d));
      turnIn = clamp(turnIn * (1 - homeK) + clamp(d * 1.4, -1, 1) * homeK, -1, 1);
    }

    this.turnRate = damp(this.turnRate, turnIn * maxTurn, 5.5, dt);
    this.yaw += this.turnRate * dt;

    const maxPitchRate = 1.35;
    let wantRate = pitchIn * maxPitchRate;
    // ---- dive pull-out. Left alone, a dive is rounded out for you: nothing happens while there is
    // room, then the nose swings up along the gentlest arc that still clears the ground, however
    // the stick is held. (Pull up harder yourself and it never interferes.)
    const need = this._pullOut(time);
    let pull = need * smooth01((need - FLARE_RATE * 0.5) / (FLARE_RATE * 0.5));
    // ease off as the path comes level, so the nose does not swing on past it
    pull = Math.min(pull, Math.max(-this.pitch, 0) * 7 + 0.15);
    const flaring = pull > 0.01 && pull > wantRate;
    if (flaring) wantRate = pull;
    this.pitchRate = damp(this.pitchRate, wantRate, flaring || this.flare > 0.1 ? 13 : 6.5, dt);
    this.flare = damp(this.flare, flaring ? 1 : 0, 8, dt);
    this.pitch += this.pitchRate * dt;
    // hands off the stick: high up the broom levels out; low down it holds its height above
    // the ground and follows the lie of the land, so skimming takes no effort
    if (Math.abs(pitchIn) < 0.05) {
      if (this.holdAgl < 0) this.holdAgl = Math.max(this.agl, 1.25);
      const look = Math.max(this.speed * 0.55, 8);
      const hx = this.fwd.x, hz = this.fwd.z, hl = Math.hypot(hx, hz) || 1;
      const sHere = this.surfaceAt(this.pos.x, this.pos.z, time);
      const sAhead = this.surfaceAt(this.pos.x + (hx / hl) * look, this.pos.z + (hz / hl) * look, time);
      const follow = clamp(1 - (this.agl - 9) / 9, 0, 1);
      const slope = Math.atan2(sAhead - sHere, look);
      const corr = clamp((this.holdAgl - this.agl) * 0.06, -0.22, 0.22);
      this.pitch = damp(this.pitch, (slope + corr) * follow, 0.8 + 2.4 * follow, dt);
    } else {
      this.holdAgl = -1;
    }
    // soft ceiling
    const ceil = clamp((this.pos.y - 820) / 160, 0, 1);
    if (ceil > 0 && this.pitch > 0) this.pitch = damp(this.pitch, 0, 3 * ceil, dt);
    this.pitch = clamp(this.pitch, -1.40, 1.15);

    // bank into the turn
    this.roll = damp(this.roll, clamp(this.turnRate / maxTurn, -1, 1) * 0.92, 4.6, dt);

    // ---- speed
    const wantBoost = input.boost && this.gust > 0.02;
    this.boosting = damp(this.boosting, wantBoost ? 1 : 0, wantBoost ? 5 : 2.2, dt);
    let target = CRUISE + (BOOST - CRUISE) * this.boosting;
    if (input.brake) target = SLOW;
    // gravity trades height for speed
    const grav = -Math.sin(this.pitch) * 17;
    this.speed += ((target - this.speed) * (input.brake ? 1.3 : 0.55) + grav) * dt;
    this.speed = clamp(this.speed, VMIN, VMAX);
    if (wantBoost) this.gust = Math.max(0, this.gust - dt * 0.16);

    // ---- move
    this._dir();
    this._prevVel.copy(this.vel);
    this.vel.copy(this.fwd).multiplyScalar(this.speed);
    this.pos.addScaledVector(this.vel, dt);

    // ---- ground cushion: skim effortlessly, never crash
    const hs = Math.hypot(this.fwd.x, this.fwd.z) * this.speed;       // horizontal speed
    const hx = this.fwd.x * this.speed, hz = this.fwd.z * this.speed;
    const surf = this.surfaceAt(this.pos.x, this.pos.z, time);
    const la = 0.22;
    // rising ground ahead lifts the floor early; a wall ahead is not "ground" and is handled below
    const maxRise = hs * la * 1.3 + 0.8;
    let ahead = this.surfaceAt(this.pos.x + hx * la, this.pos.z + hz * la, time);
    let ahead2 = this.surfaceAt(this.pos.x + hx * 0.5, this.pos.z + hz * 0.5, time);
    if (ahead - surf > maxRise) ahead = surf;
    if (ahead2 - surf > maxRise * 2.3) ahead2 = surf;
    const floor = Math.max(surf, ahead - 0.3, ahead2 - Math.max(0, this.pos.y - surf) - 2.0);
    const clear = CLEAR;
    const cushion = 2.1;
    let h = this.pos.y - floor;
    const n = T.normalAt(this.pos.x, this.pos.z, this._n, 2.0);
    const steep = n.y < 0.62 && T.heightAt(this.pos.x, this.pos.z) > 0.4;   // steeper than ~52 degrees

    // ---- landing: coming out of a dive onto the deck, the broom sinks into its cushion and
    // bounces once or twice before it settles at riding height. The harder the dive, the deeper.
    this._sink = Math.max(this._sink * Math.exp(-dt / 1.2), -this.fwd.y * this.speed);
    this.touchdown = 0;
    if (h > clear + 3.5) this._air = true;
    else if (this._air && h < clear + 0.9 && !steep) {
      this._air = false;
      const hit = clamp((this._sink - 5) * 0.19, 0, 6.5);
      if (hit > 0.3) {
        this.bobV -= hit;
        this.touchdown = hit;
        this.bump = Math.max(this.bump, hit * 0.07);
        if (Math.abs(pitchIn) < 0.05) this.holdAgl = clear + 0.15;   // hands off: settle at riding height
      }
      this._sink = 0;
    }
    {
      // a lightly damped spring about the riding height
      const wb = 7.2, zb = 0.19;
      this.bobV += (-wb * wb * this.bob - 2 * zb * wb * this.bobV) * dt;
      const nb = this.bob + this.bobV * dt;
      this.pos.y += nb - this.bob;
      this.bob = nb;
      h = this.pos.y - floor;
    }
    const ride = clear + Math.min(this.bob, 0);        // while the cushion is squashed, do not fight it
    if (h < cushion && !(steep && h < -1.2)) {
      const k = 1 - clamp((h - clear) / (cushion - clear), 0, 1);
      // close to the deck the nose cannot point below the lie of the land
      const slopeAhead = Math.atan2(ahead - surf, Math.max(hs * la, 0.5));
      if (this.pitch < slopeAhead) this.pitch = damp(this.pitch, slopeAhead, 12 * k * k, dt);
      if (h < ride) {
        this.pos.y = damp(this.pos.y, floor + ride, 16, dt);
        if (this.pos.y < floor + 0.5) this.pos.y = floor + 0.5;
      }
    }
    // ---- walls: steer off them early, and if we touch one anyway, slide along it
    let wallN = null;
    if (steep && h < clear) {
      // inside a wall: step back out along its horizontal normal (never pop up to its top)
      const nl = Math.hypot(n.x, n.z) || 1;
      const nx = n.x / nl, nz = n.z / nl;
      for (let i = 0; i < 28; i++) {
        this.pos.x += nx * 0.6; this.pos.z += nz * 0.6;
        if (this.surfaceAt(this.pos.x, this.pos.z, time) + clear * 0.55 <= this.pos.y) break;
      }
      wallN = this._wn.set(nx, 0, nz);
      this._slide(nx, nz, 1, dt);
      if (this.bump < 0.2) { this.bump = 1; this.speed *= 0.88; }
    } else if (hs > 2) {
      // look a quarter-second down the heading: will the ground there be above us?
      const t1 = 0.30, t0 = 0.12;
      const y1 = this.pos.y + this.fwd.y * this.speed * t1, y0 = this.pos.y + this.fwd.y * this.speed * t0;
      const far = T.heightAt(this.pos.x + hx * t1, this.pos.z + hz * t1) > y1 + 0.6;
      const close = T.heightAt(this.pos.x + hx * t0, this.pos.z + hz * t0) > y0 + 0.6;
      if (far || close) {
        const wn = T.normalAt(this.pos.x + hx * (close ? t0 : t1), this.pos.z + hz * (close ? t0 : t1), this._wn, 3);
        if (wn.y < 0.75) {
          const nl = Math.hypot(wn.x, wn.z) || 1;
          const headOn = this._slide(wn.x / nl, wn.z / nl, close ? 1 : 0.4, dt);
          // square on to a wall there is no room to turn: pull up as well. A glancing pass stays level.
          if (headOn > 0.55) this.pitch = damp(this.pitch, Math.max(this.pitch, 0.55), (close ? 6 : 2.5) * headOn, dt);
        }
      }
    }
    // stones, trees and the lighthouse: slide around them
    if (this.props && this.props.collide(this.pos, 0.9, this._n)) {
      const n = this._n, d = this.fwd.x * n.x + this.fwd.z * n.z;
      if (d < 0) {
        const rx = this.fwd.x - 1.5 * d * n.x, rz = this.fwd.z - 1.5 * d * n.z;
        let dy = Math.atan2(rx, -rz) - this.yaw;
        dy = Math.atan2(Math.sin(dy), Math.cos(dy));
        this.yaw += dy * Math.min(1, dt * 16);
        if (this.bump < 0.2) { this.bump = 1; this.speed *= 0.9; }
      }
    }
    this.bump = Math.max(0, this.bump - dt * 2.4);

    // ---- bookkeeping for effects
    const ground = T.heightAt(this.pos.x, this.pos.z);
    const riverY = this.river ? this.river.levelAt(this.pos.x, this.pos.z) : -Infinity;
    this.overWater = ground < 0.25 || riverY > ground;
    this.surfaceY = riverY > ground ? riverY : this.overWater ? Math.max(surf, 0) : ground;
    this.agl = this.pos.y - this.surfaceY;
    this.accel.copy(this.vel).sub(this._prevVel).multiplyScalar(1 / Math.max(dt, 1e-4));

    // skimming close to anything fills the gust meter
    const near = clamp(1 - (this.agl - 1.0) / 7.0, 0, 1);
    if (!wantBoost) this.gust = Math.min(1, this.gust + dt * (0.035 + 0.17 * near * near));
  }
}

export const SPEEDS = { CRUISE, BOOST, SLOW, VMIN, VMAX };
