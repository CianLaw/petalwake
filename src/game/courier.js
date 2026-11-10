// Deliveries: there is always one parcel, and it is for one pad. Land on that pad and it is
// delivered; the next is handed over on the spot: a hop to another tower in the same town about
// as often as a good flight to somewhere else on the island (never more than two hops running).
// Any other pad is a rest stop. The count is kept between visits.
import { twinkle, GOLD, PETAL } from './sparks.js';
import { far } from './hud.js';

export const COURIER = {
  GOOD: 350,        // m: a "good flight" to another place. Nearer pads are passed over while there are farther ones
  HOP: 70,          // m: the least a hop within a town is worth making
  HOPS: 2,          // hops in a row before the next parcel is for somewhere else
  REST_GUST: 0.35,  // gust handed back for stopping at a pad that is not the parcel's
};

export class Courier {
  constructor(game, store, hud) {
    this.game = game;
    this.store = store;
    this.hud = hud;
    this.pads = [];
    this.target = null;       // the pad the parcel is for
    this.last = null;         // the pad the last one went to
    this.count = Math.max(0, Number(store.get('deliveries.v1', 0)) || 0);
    this.hops = 0;            // parcels in a row that stayed in one town
    this._acc = 0;
  }

  /** The pads have changed (a town arrived): keep the job if its pad is still there. */
  setPads(pads) {
    this.pads = pads;
    if (!pads.includes(this.target)) this.target = null;
    if (!pads.includes(this.last)) this.last = null;
    if (!this.target && pads.length) this.target = this._pick(null, this.game.flight.pos);
    this._show();
  }

  _show() {
    const t = this.target;
    this.hud.job(t ? t.name : null, t ? t.spot : '', this.count);
    this._acc = 1;
  }

  /** The next pad to carry a parcel to, having just been at `from` (or starting out at `pos`). */
  _pick(from, pos, prev = null) {
    let c = this.pads.filter((p) => p !== from);
    if (!c.length) return from;
    // not straight back where the one before came from, if there is a choice
    if (c.length > 1 && prev && prev !== from) { const fresh = c.filter((p) => p !== prev); if (fresh.length) c = fresh; }
    const o = from ? from.pos : pos;
    const d = (p) => Math.hypot(p.pos.x - o.x, p.pos.z - o.z);
    const any = (list) => list[Math.floor(Math.random() * list.length)];
    if (from) {
      const hop = c.filter((p) => p.town === from.town && d(p) >= COURIER.HOP);
      const away = c.filter((p) => p.town !== from.town && d(p) >= COURIER.GOOD);
      if (hop.length >= 2 && (!away.length || (this.hops < COURIER.HOPS && Math.random() < 0.5))) { this.hops++; return any(hop); }
      this.hops = 0;
      if (away.length) return any(away);
    }
    const farthest = Math.max(...c.map(d));
    const good = c.filter((p) => d(p) >= Math.min(farthest, COURIER.GOOD));
    return any(good) || c[0];
  }

  /** Boots on a pad. @returns true if that was the parcel's. */
  arrive(pad) {
    const g = this.game, f = g.flight;
    if (pad !== this.target) {
      // a rest stop: a breather for the broom, and a reminder of where she is bound
      f.gust = Math.min(1, f.gust + COURIER.REST_GUST);
      const t = this.target;
      this.hud.card('rest stop', pad.name, t ? `the parcel is for ${t.name} · ${far(Math.hypot(t.pos.x - pad.pos.x, t.pos.z - pad.pos.z))}` : '', 3.4);
      return false;
    }
    this.count++;
    this.store.set('deliveries.v1', this.count);
    f.gust = 1;
    g.sound?.deliver?.(this.count);
    // gold and petals over the pad
    const lit = 0.3 + 0.7 * g.rider.sunVis;
    twinkle(g.fx, pad.pos.x, pad.pos.y + 1.6, pad.pos.z, 46, GOLD, 4.2, 0, 1.2, 0, 1.3);
    twinkle(g.fx, pad.pos.x, pad.pos.y + 1.2, pad.pos.z, 18, PETAL, 3, 0, 0.8, 0, 1.1);
    g.fx.burst(pad.pos.x, pad.pos.y + 1.4, pad.pos.z, 46, 0.86, lit, 4.5);
    g.fx.burst(pad.pos.x, pad.pos.y + 1.4, pad.pos.z, 24, 0.2, lit, 3.5);
    const prev = this.last;
    this.last = pad;
    this.target = this._pick(pad, pad.pos, prev);
    const t = this.target;
    this.hud.card('delivered', pad.name, t && t !== pad
      ? `parcel no. ${this.count} · the next is for ${t.name}, ${far(Math.hypot(t.pos.x - pad.pos.x, t.pos.z - pad.pos.z))} off`
      : `parcel no. ${this.count}`, 4.6);
    this._show();
    return true;
  }

  /** Where the parcel is going, for the compass (about ten times a second is plenty). */
  update(dt) {
    const t = this.target;
    if (!t) return;
    this._acc += dt;
    if (this._acc < 0.1) return;
    this._acc = 0;
    const f = this.game.flight;
    const dx = t.pos.x - f.pos.x, dz = t.pos.z - f.pos.z;
    this.hud.jobAt(Math.hypot(dx, dz), Math.atan2(dx, -dz) - f.yaw);
  }
}
