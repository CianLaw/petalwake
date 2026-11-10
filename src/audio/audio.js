// Procedural sound: everything is synthesised, nothing is loaded.
//   wind   - broadband noise that gets louder and airier with speed, with slow gusts
//   skim   - what the broom is brushing past: flower rustle, spray hiss, grit off rock
//   surf   - the sea, louder near the shore
//   chimes - a bell when a seed is caught
// Nothing here holds a pitch: no oscillator runs continuously, and no filter is resonant enough
// or swept far enough to be heard as a tone (an earlier build had a pad drone that glided between
// chords and a wind band that swept two octaves with speed; both read as a whine and are gone).
const SURF = { NONE: 0, WATER: 1, FLOWERS: 2, GRASS: 3, ROCK: 4, SAND: 5 };

export class Sound {
  constructor() {
    this.ctx = null;
    this.muted = false;
    this.t = 0;
    this.gust = 0;
  }

  start() {
    if (this.ctx) { this.ctx.resume(); return; }
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    const ctx = (this.ctx = new AC());
    const out = (this.master = ctx.createGain());
    out.gain.value = 0;
    const comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -14; comp.ratio.value = 3; comp.attack.value = 0.01; comp.release.value = 0.3;
    out.connect(comp).connect(ctx.destination);
    out.gain.linearRampToValueAtTime(0.9, ctx.currentTime + 2.5);

    // shared noise bed
    const len = ctx.sampleRate * 4;
    const buf = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let c = 0; c < 2; c++) {
      const d = buf.getChannelData(c);
      let b0 = 0, b1 = 0, b2 = 0;
      for (let i = 0; i < len; i++) {
        // pink-ish (Paul Kellet's economy filter)
        const w = Math.random() * 2 - 1;
        b0 = 0.99765 * b0 + w * 0.0990460; b1 = 0.96300 * b1 + w * 0.2965164; b2 = 0.57000 * b2 + w * 1.0526913;
        d[i] = (b0 + b1 + b2 + w * 0.1848) * 0.22;
      }
    }
    this.noiseBuf = buf;      // (the one-shots below cut their rushes of air from it too)
    const noise = (rate = 1) => { const s = ctx.createBufferSource(); s.buffer = buf; s.loop = true; s.playbackRate.value = rate; s.start(0, Math.random() * 3); return s; };
    const band = (type, f, q) => { const b = ctx.createBiquadFilter(); b.type = type; b.frequency.value = f; b.Q.value = q; return b; };
    const gain = (v = 0) => { const g = ctx.createGain(); g.gain.value = v; return g; };

    // wind: body + hiss. The body's band is wide and barely moves; speed is heard as loudness and
    // as more hiss on top, not as a rising note.
    this.windF = band('bandpass', 420, 0.35);
    this.windG = gain(0);
    this.pan = ctx.createStereoPanner ? ctx.createStereoPanner() : gain(1);
    noise(1).connect(this.windF).connect(this.windG).connect(this.pan).connect(out);
    this.hissF = band('highpass', 2600, 0.5);
    this.hissG = gain(0);
    noise(1.31).connect(this.hissF).connect(this.hissG).connect(this.pan);
    this.rumF = band('lowpass', 130, 0.7);
    this.rumG = gain(0);
    noise(0.71).connect(this.rumF).connect(this.rumG).connect(out);

    // skim layer
    this.skimF = band('bandpass', 3000, 0.8);
    this.skimG = gain(0);
    noise(1.17).connect(this.skimF).connect(this.skimG).connect(this.pan);

    // surf
    this.surfF = band('lowpass', 520, 0.4);
    this.surfG = gain(0);
    noise(0.83).connect(this.surfF).connect(this.surfG).connect(out);

    // reverb for the chimes: exponentially decaying noise
    const irLen = ctx.sampleRate * 3.2;
    const ir = ctx.createBuffer(2, irLen, ctx.sampleRate);
    for (let c = 0; c < 2; c++) {
      const d = ir.getChannelData(c);
      for (let i = 0; i < irLen; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / irLen, 2.6);
    }
    this.rev = ctx.createConvolver();
    this.rev.buffer = ir;
    this.revG = gain(0.5);
    this.rev.connect(this.revG).connect(out);
  }

  /** A bell; n picks the note so successive seeds climb a scale. */
  chime(n = 0) {
    if (!this.ctx || this.muted) return;
    const ctx = this.ctx, t = ctx.currentTime;
    const scale = [587.33, 659.25, 739.99, 880.0, 987.77, 1174.66, 1318.51, 1479.98];
    const f = scale[n % scale.length] * (n % 16 >= 8 ? 2 : 1) * 0.5;
    for (const [mul, amp, dur] of [[1, 0.16, 2.4], [2.76, 0.05, 1.3], [5.4, 0.02, 0.7]]) {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = 'sine'; o.frequency.value = f * mul;
      g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(amp, t + 0.006); g.gain.exponentialRampToValueAtTime(0.0004, t + dur);
      o.connect(g); g.connect(this.master); g.connect(this.rev);
      o.start(t); o.stop(t + dur + 0.05);
    }
  }

  /** A treasure found: a short run of bells rising to a held one. One-shot, like the chime. */
  treasure(n = 0) {
    if (!this.ctx || this.muted) return;
    const ctx = this.ctx, t0 = ctx.currentTime;
    const root = [392.0, 440.0, 493.88, 523.25][n % 4];
    [1, 1.25, 1.5, 2, 2.5].forEach((ratio, i) => {
      const t = t0 + i * 0.085, last = i === 4;
      for (const [mul, amp, dur] of [[1, last ? 0.15 : 0.09, last ? 3.0 : 1.1], [2.76, 0.03, 0.8], [5.4, 0.012, 0.4]]) {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.type = 'sine'; o.frequency.value = root * ratio * mul;
        g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(amp, t + 0.006); g.gain.exponentialRampToValueAtTime(0.0004, t + dur);
        o.connect(g); g.connect(this.master); g.connect(this.rev);
        o.start(t); o.stop(t + dur + 0.05);
      }
    });
  }

  /** One bell note at time t (the chime's voice), for the short runs below. */
  _bell(f, t, amp = 0.1, dur = 1.4) {
    const ctx = this.ctx;
    for (const [mul, a, d] of [[1, amp, dur], [2.76, amp * 0.3, dur * 0.55], [5.4, amp * 0.12, dur * 0.3]]) {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = 'sine'; o.frequency.value = f * mul;
      g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(a, t + 0.006); g.gain.exponentialRampToValueAtTime(0.0004, t + d);
      o.connect(g); g.connect(this.master); g.connect(this.rev);
      o.start(t); o.stop(t + d + 0.05);
    }
  }

  /**
   * A rush of air (the kickflip, hopping on and off the broom, leaving a pad): a short cut of the
   * noise bed through a wide band that opens and closes. Broadband, over in under a second.
   */
  whoosh(amount = 1, long = false) {
    if (!this.ctx || this.muted || !this.noiseBuf) return;
    const ctx = this.ctx, t = ctx.currentTime, d = long ? 0.95 : 0.42;
    const s = ctx.createBufferSource(), f = ctx.createBiquadFilter(), g = ctx.createGain();
    s.buffer = this.noiseBuf; s.loop = true;
    f.type = 'bandpass'; f.Q.value = 0.55;
    f.frequency.setValueAtTime(520, t);
    f.frequency.exponentialRampToValueAtTime(long ? 1700 : 2300, t + d * 0.42);
    f.frequency.exponentialRampToValueAtTime(760, t + d);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.55 * amount, t + d * 0.3);
    g.gain.exponentialRampToValueAtTime(0.0005, t + d);
    s.connect(f).connect(g).connect(this.master);
    s.start(t, Math.random() * 3); s.stop(t + d + 0.05);
  }

  /** Boots on stone: a soft pat of low noise. */
  thump(amount = 1) {
    if (!this.ctx || this.muted || !this.noiseBuf) return;
    const ctx = this.ctx, t = ctx.currentTime;
    const s = ctx.createBufferSource(), f = ctx.createBiquadFilter(), g = ctx.createGain();
    s.buffer = this.noiseBuf; s.loop = true; s.playbackRate.value = 0.6;
    f.type = 'lowpass'; f.frequency.value = 260; f.Q.value = 0.5;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.9 * amount, t + 0.008);
    g.gain.exponentialRampToValueAtTime(0.0005, t + 0.2);
    s.connect(f).connect(g).connect(this.master);
    s.start(t, Math.random() * 3); s.stop(t + 0.25);
  }

  /** A parcel delivered: four bells up a chord, the last one left to ring. n moves the key about. */
  deliver(n = 0) {
    if (!this.ctx || this.muted) return;
    const t0 = this.ctx.currentTime + 0.05, root = [293.66, 329.63, 261.63, 349.23][n % 4];
    [1, 1.26, 1.5, 2].forEach((ratio, i) => this._bell(root * ratio, t0 + i * 0.105, i === 3 ? 0.15 : 0.085, i === 3 ? 2.8 : 1.0));
    this._bell(root * 3, t0 + 0.47, 0.035, 1.6);
  }

  /** The trick learned: a quick run up five bells. */
  unlock() {
    if (!this.ctx || this.muted) return;
    const t0 = this.ctx.currentTime + 0.02;
    [587.33, 659.25, 739.99, 880.0, 1174.66].forEach((f, i) => this._bell(f, t0 + i * 0.07, i === 4 ? 0.12 : 0.07, i === 4 ? 2.2 : 0.7));
  }

  toggleMute() {
    this.muted = !this.muted;
    if (this.ctx) this.master.gain.setTargetAtTime(this.muted ? 0 : 0.9, this.ctx.currentTime, 0.2);
    return this.muted;
  }

  /** @param s { speed, boosting, contact, surface, roll, shore (0..1 nearness to the sea), agl } */
  update(dt, s) {
    const ctx = this.ctx;
    if (!ctx) return;
    this.t += dt;
    const t = ctx.currentTime, k = 0.12;
    const v = Math.min(s.speed / 90, 1);
    // gusts wander
    this.gust += (Math.sin(this.t * 0.37) * 0.5 + Math.sin(this.t * 0.83 + 1.7) * 0.3 + Math.sin(this.t * 1.9) * 0.2 - this.gust) * Math.min(1, dt * 2);
    const g = 1 + this.gust * 0.28;
    this.windF.frequency.setTargetAtTime(380 + 240 * v, t, 0.6);
    this.windG.gain.setTargetAtTime((0.05 + 0.5 * Math.pow(v, 1.4)) * g, t, k);
    this.hissG.gain.setTargetAtTime(0.20 * Math.pow(v, 1.9) * g + 0.05 * s.boosting, t, k);
    this.rumG.gain.setTargetAtTime(0.12 * s.boosting + 0.04 * Math.pow(v, 2), t, k);
    if (this.pan.pan) this.pan.pan.setTargetAtTime(Math.max(-0.25, Math.min(0.25, s.roll * 0.28)), t, 0.4);

    // what we are skimming
    let f = 3000, q = 0.8, amp = 0;
    const c = Math.min(s.contact, 1.6);
    if (s.surface === SURF.WATER) { f = 5200; q = 0.5; amp = 0.42 * c; }
    else if (s.surface === SURF.FLOWERS || s.surface === SURF.GRASS) { f = 2800; q = 0.6; amp = 0.30 * c; }
    else if (s.surface === SURF.ROCK) { f = 1500; q = 0.6; amp = 0.32 * c; }
    else if (s.surface === SURF.SAND) { f = 3800; q = 0.6; amp = 0.30 * c; }
    this.skimF.frequency.setTargetAtTime(f, t, 0.25);
    this.skimF.Q.setTargetAtTime(q, t, 0.25);
    this.skimG.gain.setTargetAtTime(amp, t, 0.08);

    // the sea breathes
    const swell = 0.6 + 0.4 * Math.sin(this.t * 0.55);
    this.surfG.gain.setTargetAtTime(0.22 * s.shore * swell * Math.max(0, 1 - s.agl / 260), t, 0.4);
  }
}
