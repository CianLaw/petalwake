// Landing-pad beacons, drawn in the sharp layer (after the motion blur, depth-tested against the
// world): over each pad that is near, a soft shaft of light, a ring on its floor and a low curtain
// of light round the edge. The pad that can be landed on right now is the landing zone: it
// brightens and pulses, with ripples running in to the middle. The pad the parcel is for is gold,
// stands much taller, wears a marker above it, and can be seen from across the island - through
// the haze, which dims and warms it the way it does everything else.
import * as THREE from 'three';
import { shared } from '../core/ctx.js';

export const BEACON = {
  SHOW: 150,        // m: a pad's beacon is fully there inside this...
  FADE: 35,         // ...and gone this much further out
  NEAREST: 7,       // ...and only for this many, the nearest: a town full of pads is not a forest of lights
  FAR: 2100,        // m: the parcel's beacon carries this far
  TALL: 34,         // m: height of a shaft
  TALL_GOLD: 240,   // m: ...and of the parcel's
};

const damp = (cur, target, rate, dt) => cur + (target - cur) * (1 - Math.exp(-rate * dt));
const smooth01 = (x) => { const t = x < 0 ? 0 : x > 1 ? 1 : x; return t * t * (3 - 2 * t); };

// light through the air between it and the eye: dimmer and warmer with distance (see applyAtmosphere)
const HAZE = /* glsl */`
uniform vec4 uFog;
uniform vec3 uCamPos;
vec3 haze(vec3 P){
  vec3 v = P - uCamPos;
  float d = length(v);
  float b = uFog.y;
  float c0 = uFog.x * exp(-max(uCamPos.y, 0.0) * b);
  float t = v.y / max(d, 1e-4) * b;
  float integ = abs(t) > 1e-5 ? (1.0 - exp(-d * t)) / t : d;
  return exp(-c0 * integ * vec3(0.52, 0.86, 1.32));
}
float sq(float x){ return x * x; }
const vec3 PALE = vec3(1.0, 0.60, 0.78);      // a rest stop: petal pink
const vec3 GOLD = vec3(1.0, 0.70, 0.20);      // where the parcel is going
// Light alone washes out to white against a bright sky or sunlit stone. So these are laid on as
// tinted glass as well as light: v of light, and v * body of it covering what is behind.
vec4 lay(vec3 col, float v, float body){ return vec4(col * v, clamp(v * body, 0.0, 0.88)); }
`;
const HEAD = /* glsl */`
precision highp float;
attribute vec4 iPad;        // xyz, radius of clear floor
attribute vec4 iLook;       // shown 0..1, landing zone 0..1, gold 0..1, phase
uniform float uTime;
varying vec2 vUv;
varying vec4 vLook;
varying vec3 vWorld;
`;
const FHEAD = /* glsl */`
precision highp float;
uniform float uTime;
varying vec2 vUv;
varying vec4 vLook;
varying vec3 vWorld;
${HAZE}
`;
const BLEND = {
  transparent: true, depthWrite: false, side: THREE.DoubleSide,
  blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
  blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor,
};

export class Beacons {
  constructor(pads) {
    this.pads = pads;
    const n = pads.length;
    this.group = new THREE.Group();
    this.state = pads.map(() => ({ show: 0, zone: 0, gold: 0 }));
    this.aPad = new THREE.InstancedBufferAttribute(new Float32Array(n * 4), 4);
    this.aLook = new THREE.InstancedBufferAttribute(new Float32Array(n * 4), 4);
    this.aLook.setUsage(THREE.DynamicDrawUsage);
    pads.forEach((p, i) => {
      this.aPad.array.set([p.pos.x, p.pos.y, p.pos.z, Math.max(p.radius, 0.7)], i * 4);
      this.aLook.array[i * 4 + 3] = (i * 0.618) % 1;
    });
    const uniforms = { ...shared('uTime', 'uFog', 'uCamPos') };
    const quad = new Float32Array([-1, -1, 0, 1, -1, 0, -1, 1, 0, 1, 1, 0]);
    const make = (position, index, vertexShader, fragmentShader, order, extra = {}) => {
      const g = new THREE.InstancedBufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(position, 3));
      g.setIndex(index);
      g.setAttribute('iPad', this.aPad);
      g.setAttribute('iLook', this.aLook);
      g.instanceCount = n;
      const mesh = new THREE.Mesh(g, new THREE.ShaderMaterial({ uniforms: { ...uniforms, ...extra }, vertexShader, fragmentShader, ...BLEND }));
      mesh.frustumCulled = false;
      mesh.renderOrder = order;
      this.group.add(mesh);
      return mesh;
    };

    // ---- the shaft: an upright card that turns to face the eye
    this.shaft = make(quad, [0, 1, 2, 1, 3, 2], /* glsl */`${HEAD}
      varying float vTall;
      varying float vNear;
      void main(){
        vec3 c = iPad.xyz;
        vec3 toCam = cameraPosition - c;
        float d = length(toCam);
        vec3 side = normalize(cross(vec3(0.0, 1.0, 0.0), toCam));
        float gold = iLook.z;
        float tall = mix(${BEACON.TALL.toFixed(1)}, ${BEACON.TALL_GOLD.toFixed(1)}, gold);
        float y = position.y * 0.5 + 0.5;
        // tapering upward, and never thinner than a few pixels however far off it is
        float w = iPad.w * mix(1.0, 0.3, y) + d * mix(0.0018, 0.0075, gold);
        vec3 P = c + side * position.x * w + vec3(0.0, y * tall, 0.0);
        vUv = vec2(position.x, y); vLook = iLook; vTall = tall; vWorld = P;
        // a guide from afar: it thins out as she closes in, and is gone by the time she lands
        vNear = smoothstep(9.0, 46.0, length(toCam.xz));
        gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0);
      }`, /* glsl */`${FHEAD}
      varying float vTall;
      varying float vNear;
      void main(){
        float x = clamp(abs(vUv.x), 0.0, 1.0), y = clamp(vUv.y, 0.0, 1.0);
        float core = pow(1.0 - x, 2.4);
        float up = pow(1.0 - y, 1.7) * smoothstep(0.0, 0.012, y);
        // slow bands of light climbing it
        float climb = 0.74 + 0.26 * sin(y * vTall * 0.5 - uTime * 2.0 + vLook.w * 6.2831853);
        float v = core * up * climb * vLook.x * vNear * mix(0.42, 1.05, vLook.z) * (1.0 + 1.0 * vLook.y);
        vec3 col = mix(PALE, GOLD, vLook.z) * haze(vWorld);
        gl_FragColor = lay(col, v, mix(0.55, 0.95, vLook.z));
      }`, 46);

    // ---- the ring on the floor
    this.ring = make(quad, [0, 1, 2, 1, 3, 2], /* glsl */`${HEAD}
      varying float vRad;
      void main(){
        // (lying a finger above the floor; 1 in vUv is the edge of the clear floor)
        vec3 P = iPad.xyz + vec3(position.x, 0.0, position.y) * (iPad.w * 1.5 + 0.5) + vec3(0.0, 0.07, 0.0);
        vUv = position.xy * (1.5 + 0.5 / iPad.w); vLook = iLook; vWorld = P; vRad = iPad.w;
        gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0);
      }`, /* glsl */`${FHEAD}
      varying float vRad;
      void main(){
        float r = length(vUv), a = atan(vUv.y, vUv.x);
        float aa = fwidth(r) * 1.2;
        float zone = vLook.y, gold = vLook.z;
        // (lines keep their width in metres whatever the size of the pad)
        float edge = exp(-sq((r - 1.0) / (0.016 + 0.05 / vRad + aa)));
        // a broken ring just outside it, turning slowly
        float dash = smoothstep(0.12, 0.2, abs(fract(a * 1.9098593 + uTime * 0.04) - 0.5));
        float outer = exp(-sq((r - 1.22) / (0.008 + 0.03 / vRad + aa))) * dash;
        // the landing zone: ripples run in to the middle, the floor glows, and the lot breathes
        float inside = 1.0 - smoothstep(0.86, 1.0, r);
        float rip = pow(0.5 + 0.5 * sin(r * 10.0 + uTime * 3.6), 4.0) * inside * smoothstep(0.0, 0.25, r);
        float glow = inside * (1.0 - 0.6 * r);
        float breath = 0.75 + 0.25 * sin(uTime * 4.4);
        float v = edge * (0.75 + 1.9 * zone * breath) + outer * (0.35 + 0.5 * zone)
                + zone * (rip * 0.50 + glow * 0.22 * breath) + glow * 0.04;
        v += exp(-r * r * 60.0) * (0.25 + 0.8 * zone);
        v *= vLook.x * (1.0 - smoothstep(1.3, 1.5, r));
        vec3 col = mix(PALE, GOLD, gold) * haze(vWorld);
        gl_FragColor = lay(col, v, 0.6);
      }`, 47);

    // ---- the curtain: a low wall of light standing on the ring, so the zone shows from below too
    const SEG = 48, cp = new Float32Array((SEG + 1) * 2 * 3), ci = [];
    for (let i = 0; i <= SEG; i++) {
      const a = (i / SEG) * Math.PI * 2;
      cp.set([Math.cos(a), 0, Math.sin(a), Math.cos(a), 1, Math.sin(a)], i * 6);
      if (i < SEG) { const k = i * 2; ci.push(k, k + 1, k + 2, k + 1, k + 3, k + 2); }
    }
    this.curtain = make(cp, ci, /* glsl */`${HEAD}
      varying float vClose;
      void main(){
        float tall = mix(1.5, 3.1, iLook.y);
        vec3 P = iPad.xyz + vec3(position.x * iPad.w, 0.05 + position.y * tall, position.z * iPad.w);
        vUv = vec2(atan(position.z, position.x), position.y); vLook = iLook; vWorld = P;
        // (thinner from close by, so it does not hang like a veil in front of her as she lands)
        vClose = mix(0.3, 1.0, smoothstep(6.0, 20.0, distance(cameraPosition, iPad.xyz)));
        gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0);
      }`, /* glsl */`${FHEAD}
      varying float vClose;
      void main(){
        float y = clamp(vUv.y, 0.0, 1.0), a = vUv.x;
        // threads of light rising off the ring
        float thread = pow(0.5 + 0.5 * sin(a * 26.0 + 2.5 * sin(a * 3.0 + uTime * 0.3)), 2.0);
        float rise = 0.6 + 0.4 * sin(y * 7.0 - uTime * 3.2 + a * 4.0);
        float v = pow(1.0 - y, 2.3) * (0.3 + 0.7 * thread * rise) * vLook.x * vClose * (0.16 + 0.85 * vLook.y * (0.8 + 0.2 * sin(uTime * 4.4)));
        vec3 col = mix(PALE, GOLD, vLook.z) * haze(vWorld);
        gl_FragColor = lay(col, v, 0.35);
      }`, 47);

    // ---- the marker over the parcel's pad: a small bright lozenge that bobs, and keeps a size on screen
    this.uMark = { value: new THREE.Vector4(0, -1e4, 0, 0) };      // xyz, shown
    const mg = new THREE.BufferGeometry();
    mg.setAttribute('position', new THREE.BufferAttribute(quad, 3));
    mg.setIndex([0, 1, 2, 1, 3, 2]);
    this.mark = new THREE.Mesh(mg, new THREE.ShaderMaterial({
      uniforms: { ...uniforms, uMark: this.uMark },
      vertexShader: /* glsl */`
        precision highp float;
        uniform vec4 uMark;
        uniform float uTime;
        varying vec2 vUv;
        varying float vShow;
        varying vec3 vWorld;
        void main(){
          vec3 c = uMark.xyz + vec3(0.0, 4.6 + 0.35 * sin(uTime * 1.7), 0.0);
          vec4 mv = viewMatrix * vec4(c, 1.0);
          float d = -mv.z;
          mv.xy += position.xy * 1.15 * (1.0 + min(d, 2400.0) * 0.011);
          vUv = position.xy; vWorld = c;
          // (out of the way once she is on the pad under it)
          vShow = uMark.w * smoothstep(7.0, 20.0, d);
          gl_Position = projectionMatrix * mv;
        }`,
      fragmentShader: /* glsl */`
        precision highp float;
        uniform float uTime;
        varying vec2 vUv;
        varying float vShow;
        varying vec3 vWorld;
        ${HAZE}
        void main(){
          vec2 p = vUv * vec2(1.25, 1.0);
          float d = abs(p.x) + abs(p.y);                      // a lozenge
          float fw = fwidth(d) * 1.2;
          float body = 1.0 - smoothstep(0.36 - fw, 0.36 + fw, d);
          float rim = exp(-sq((d - 0.5) / (0.035 + fw))) * 0.7;
          float r = length(vUv);
          float halo = exp(-r * r * 5.5) * 0.35;
          float rays = pow(abs(cos(atan(vUv.y, vUv.x))), 60.0) * exp(-r * 3.4) * 0.5;
          float v = (body * (1.5 + 0.4 * sin(uTime * 3.0)) + rim + halo + rays) * vShow * (1.0 - smoothstep(0.8, 1.0, r));
          gl_FragColor = lay(GOLD * haze(vWorld) * 1.3, v, 0.7);
        }`,
      ...BLEND,
    }));
    this.mark.frustumCulled = false;
    this.mark.renderOrder = 48;
    this.group.add(this.mark);
  }

  /**
   * @param pos    the rider
   * @param zone   the pad that is the landing zone just now (highlighted), or null
   * @param target the pad the parcel is for (gold), or null
   * @param hold   a pad to keep lit whatever the distance (the one she is landing on / standing on)
   */
  update(dt, pos, zone, target, hold) {
    const L = this.aLook.array, D = this._d || (this._d = new Float32Array(this.pads.length)), sorted = this._s || (this._s = new Float32Array(this.pads.length));
    this.pads.forEach((p, i) => { D[i] = Math.hypot(p.pos.x - pos.x, p.pos.y - pos.y, p.pos.z - pos.z); });
    // how far off the last of the nearest few is: pads beyond it stay dark
    sorted.set(D); sorted.sort();
    const cut = sorted[Math.min(BEACON.NEAREST, sorted.length) - 1] + 1;
    let mark = 0;
    this.pads.forEach((p, i) => {
      const s = this.state[i], d = D[i];
      const gold = p === target;
      const show = gold ? 1 - smooth01((d - BEACON.FAR) / 300) : p === hold || p === zone ? 1
        : (1 - smooth01((d - BEACON.SHOW) / BEACON.FADE)) * (1 - smooth01((d - cut) / 12));
      s.show = damp(s.show, show, 3, dt);
      s.zone = damp(s.zone, p === zone ? 1 : 0, p === zone ? 7 : 3.5, dt);
      s.gold = damp(s.gold, gold ? 1 : 0, 2.5, dt);
      L[i * 4] = s.show; L[i * 4 + 1] = s.zone; L[i * 4 + 2] = s.gold;
      if (gold) { this.uMark.value.set(p.pos.x, p.pos.y, p.pos.z, s.show * s.gold); mark = 1; }
    });
    if (!mark) this.uMark.value.w = 0;
    this.aLook.needsUpdate = true;
  }

  dispose() {
    for (const m of this.group.children) { m.geometry.dispose(); m.material.dispose(); }
  }
}
