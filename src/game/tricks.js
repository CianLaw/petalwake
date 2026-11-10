// The kickflip: catch ten wind seeds and Q snaps rider and broom through a full roll, with a hop.
// Nothing about the flight changes - it is all in how she is drawn (rider.seat), so the camera
// stays level and the cushion under the broom never knows - plus a spiral of sparks and petals
// thrown off the turning broom, a rush of air, and a little gust for the nerve of it.
import { mote, streak, GOLD, PETAL, PALE } from './sparks.js';

export const FLIP = {
  SEEDS: 10,        // wind seeds to catch before the trick is hers
  T: 0.7,           // s: the roll
  HOP: 0.55,        // m: height of the hop
  GUST: 0.12,       // gust handed back for landing it
  COOL: 1.1,        // s before the next one
};

const TAU = Math.PI * 2;
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const rand = (a, b) => a + Math.random() * (b - a);

/** 0..1 through the roll: a hair of wind-up the wrong way, a whip round, a soft arrival. */
function whip(u) {
  if (u < 0.1) return -0.03 * Math.sin((u / 0.1) * Math.PI);
  const v = (u - 0.1) / 0.9;
  return v < 0.5 ? 4 * v * v * v : 1 - Math.pow(-2 * v + 2, 3) / 2;
}

export class Kickflip {
  constructor(game, store, hud) {
    this.game = game;
    this.store = store;
    this.hud = hud;
    this.unlocked = !!store.get('kickflip.v1', false);
    this.t = -1;              // seconds into the roll (-1: not rolling)
    this.cool = 0;
    this.after = 1e9;         // seconds since it finished (the broom is still settling)
    this.dir = 1;
    this.count = 0;
    this._acc = 0;
  }

  get active() { return this.t >= 0; }

  /** @returns true if a roll started. `force` skips the unlock and the cooldown (debug). */
  start(force = false) {
    const g = this.game, f = g.flight;
    if (this.active || f.auto) return false;
    if (!force && (!this.unlocked || this.cool > 0)) return false;
    this.t = 0;
    // roll into the turn she is in, to the right from level
    this.dir = f.roll < -0.06 ? -1 : 1;
    this.count++;
    g.sound?.whoosh?.(0.9);
    return true;
  }

  /** The seeds are counted elsewhere (world/seeds.js); this only watches the total. */
  _watch() {
    const g = this.game;
    if (this.unlocked || !g.seeds || g.seeds.count < FLIP.SEEDS) return;
    this.unlocked = true;
    this.store.set('kickflip.v1', true);
    g.toast?.('Kickflip unlocked: press Q');
    g.sound?.unlock?.();
  }

  update(dt) {
    const g = this.game, f = g.flight, seat = g.rider.seat;
    this._watch();
    if (this.cool > 0) this.cool -= dt;
    this.after += dt;
    this.hud.trick(this.unlocked && g.state === 'play' ? (this.active || this.cool > 0 ? 'cool' : 'ready') : '');
    if (!this.active) {
      // the broom rocks back level after the roll
      if (this.after < 0.5) seat.flip -= this.dir * 0.11 * Math.exp(-this.after * 9) * Math.sin(this.after * 24);
      return;
    }
    if (f.auto) { this.t = -1; return; }            // (taken over mid-roll: let it go)
    this.t += dt;
    const u = clamp(this.t / FLIP.T, 0, 1);
    const angle = this.dir * TAU * whip(u);
    const s = Math.sin(Math.PI * u);
    seat.flip -= angle;                               // (about the broom, which points along -z: this way is to her right)
    seat.hop += FLIP.HOP * Math.pow(s, 0.85) - 0.06 * Math.sin(Math.PI * clamp(u / 0.12, 0, 1));
    // tucked for the kick, long through the air, a squash as the broom catches her again
    seat.sy *= 1 - 0.12 * Math.sin(Math.PI * clamp(u / 0.14, 0, 1)) + 0.10 * s - 0.10 * Math.sin(Math.PI * clamp((u - 0.86) / 0.14, 0, 1));

    // ---- the spiral: sparks and petals flung off either side of the turning broom. They keep
    // most of her speed, so they hang about her as a corkscrew before the wake takes them.
    const fx = g.fx, lit = 0.3 + 0.7 * g.rider.sunVis;
    const rx = Math.cos(f.yaw), rz = Math.sin(f.yaw);              // her right, level
    const ux = -Math.sin(f.yaw) * Math.sin(f.pitch), uy = Math.cos(f.pitch), uz = Math.cos(f.yaw) * Math.sin(f.pitch);   // her up
    const hopY = seat.hop;
    this._acc += dt * 210 * (0.35 + 0.65 * s);
    const n = this._acc | 0;
    this._acc -= n;
    for (let i = 0; i < n; i++) {
      // a point on the ring the roll sweeps, and the way that point is moving
      const a = angle + (i & 1 ? Math.PI : 0) + rand(-0.35, 0.35), rad = rand(0.55, 1.0);
      const ca = Math.cos(a), sa = Math.sin(a);
      // (roll to the right: her up swings toward her right)
      const ox = (ux * ca + rx * sa) * rad, oy = (uy * ca) * rad, oz = (uz * ca + rz * sa) * rad;
      const tx = (-ux * sa + rx * ca) * this.dir, ty = (-uy * sa) * this.dir, tz = (-uz * sa + rz * ca) * this.dir;
      const back = rand(-0.9, 0.9), keep = rand(0.86, 0.97), spin = rand(3.5, 7.5), outw = rand(0.5, 2.2);
      const x = f.pos.x + ox + f.fwd.x * back, y = f.pos.y + hopY + oy + f.fwd.y * back, z = f.pos.z + oz + f.fwd.z * back;
      const vx = f.vel.x * keep + tx * spin + ox * outw, vy = f.vel.y * keep + ty * spin + oy * outw, vz = f.vel.z * keep + tz * spin + oz * outw;
      const pick = Math.random();
      if (pick < 0.6) mote(fx, x, y, z, vx, vy, vz, pick < 0.36 ? GOLD : pick < 0.5 ? PETAL : PALE, 0.75);
      else if (pick < 0.78) streak(fx, x, y, z, vx, vy, vz, PALE, 0.3);
      else fx._petal(x, y, z, vx * 0.8, vy * 0.8 + 1, vz * 0.8, pick < 0.9 ? 0.2 : 0.86, lit, rand(2.5, 4.5));
    }

    if (this.t >= FLIP.T) {
      this.t = -1;
      this.after = 0;
      this.cool = FLIP.COOL;
      f.gust = Math.min(1, f.gust + FLIP.GUST);
    }
  }
}
