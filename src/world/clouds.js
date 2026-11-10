// Volumetric cumulus + cirrus, ray-marched once into a lat-long texture (premultiplied RGB + opacity).
// The bake is sliced into strips over several frames so loading never stalls, and accumulated over
// a few jittered passes to hide the march's banding.
import * as THREE from 'three';
import { U, shared } from '../core/ctx.js';
import { ATMOSPHERE } from '../shaders/common.js';
import { SKY_UNIFORMS } from './sky.js';

const tri = (() => {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 3, -1, 0, -1, 3, 0]), 3));
  return g;
})();

export class CloudBaker {
  constructor(renderer, W = 4096, H = 1024) {
    this.renderer = renderer;
    this.W = W; this.H = H;
    this.passes = 3;
    this.strips = 16;
    const opt = { type: THREE.HalfFloatType, format: THREE.RGBAFormat, depthBuffer: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, generateMipmaps: false };
    this.acc = new THREE.WebGLRenderTarget(W, H, opt);
    this.final = new THREE.WebGLRenderTarget(W, H, { ...opt, minFilter: THREE.LinearMipmapLinearFilter, generateMipmaps: true });
    this.final.texture.wrapS = THREE.RepeatWrapping;
    this.final.texture.wrapT = THREE.ClampToEdgeWrapping;
    this.final.texture.anisotropy = 8;
    this.mat = new THREE.ShaderMaterial({
      uniforms: {
        ...shared(...SKY_UNIFORMS),
        uJitter: { value: 0 },
        uWeight: { value: 1 },
        uSeed: { value: new THREE.Vector3(13.7, 4.1, 91.3) },
        uCoverage: { value: 0.44 },
      },
      vertexShader: /* glsl */`varying vec2 vUv; void main(){ vUv = position.xy * 0.5 + 0.5; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
      fragmentShader: CLOUD_FRAG,
      depthTest: false, depthWrite: false,
      blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
      blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor,
    });
    this.copy = new THREE.ShaderMaterial({
      uniforms: { tColor: { value: this.acc.texture } },
      vertexShader: /* glsl */`varying vec2 vUv; void main(){ vUv = position.xy * 0.5 + 0.5; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
      fragmentShader: /* glsl */`varying vec2 vUv; uniform sampler2D tColor; void main(){ gl_FragColor = texture(tColor, vUv); }`,
      depthTest: false, depthWrite: false,
    });
    this.quad = new THREE.Mesh(tri, this.mat);
    this.quad.frustumCulled = false;
    this.scene = new THREE.Scene();
    this.scene.add(this.quad);
    this.cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this.cursor = 0;
    this.total = this.passes * this.strips;
    this.done = false;
  }

  get texture() { return this.final.texture; }

  begin() {
    const r = this.renderer;
    r.setRenderTarget(this.acc);
    r.setClearColor(0x000000, 0);
    r.clear();
    r.setClearColor(0x000000, 1);
    r.setRenderTarget(null);
    this.cursor = 0;
    this.done = false;
  }

  /** Render a few strips; returns progress 0..1. */
  step(n = 2) {
    if (this.done) return 1;
    const r = this.renderer;
    const prevAuto = r.autoClear;
    r.autoClear = false;
    this.quad.material = this.mat;
    const sh = this.H / this.strips;
    for (let i = 0; i < n && this.cursor < this.total; i++, this.cursor++) {
      const pass = Math.floor(this.cursor / this.strips), strip = this.cursor % this.strips;
      this.mat.uniforms.uJitter.value = (pass + 0.5) / this.passes;
      this.mat.uniforms.uWeight.value = 1 / this.passes;
      this.acc.scissorTest = true;
      this.acc.scissor.set(0, strip * sh, this.W, sh);
      r.setRenderTarget(this.acc);
      r.render(this.scene, this.cam);
    }
    this.acc.scissorTest = false;
    if (this.cursor >= this.total) {
      this.quad.material = this.copy;
      r.autoClear = true;
      r.setRenderTarget(this.final);
      r.render(this.scene, this.cam);
      this.done = true;
      this.acc.dispose();          // the accumulation buffer has done its job
    }
    r.setRenderTarget(null);
    r.autoClear = prevAuto;
    return this.cursor / this.total;
  }

  /** Bake everything now (blocking). */
  bakeAll() { this.begin(); while (!this.done) this.step(4); }
}

const CLOUD_FRAG = /* glsl */`
precision highp float;
varying vec2 vUv;
uniform float uJitter;
uniform float uWeight;
uniform vec3 uSeed;
uniform float uCoverage;
${ATMOSPHERE}

const float RP = 520000.0;                 // a small planet pulls the cloud deck down to the horizon
const float H0 = 1350.0, H1 = 4700.0;
const float SIGMA = 0.045;

float h13(vec3 p){ p = fract(p * 0.1031); p += dot(p, p.zyx + 31.32); return fract((p.x + p.y) * p.z); }
vec3 h33(vec3 p){ p = fract(p * vec3(0.1031, 0.1030, 0.0973)); p += dot(p, p.yxz + 33.33); return fract((p.xxy + p.yxx) * p.zyx); }
float h12(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float vn2(vec2 p){ vec2 i = floor(p), f = fract(p); vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(h12(i), h12(i + vec2(1, 0)), u.x), mix(h12(i + vec2(0, 1)), h12(i + vec2(1, 1)), u.x), u.y); }
float vn3(vec3 p){ vec3 i = floor(p), f = fract(p); vec3 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(mix(h13(i), h13(i + vec3(1,0,0)), u.x), mix(h13(i + vec3(0,1,0)), h13(i + vec3(1,1,0)), u.x), u.y),
             mix(mix(h13(i + vec3(0,0,1)), h13(i + vec3(1,0,1)), u.x), mix(h13(i + vec3(0,1,1)), h13(i + vec3(1,1,1)), u.x), u.y), u.z); }
float fbm2d(vec2 p){ float s = 0.0, a = 0.5; for (int i = 0; i < 4; i++){ s += a * vn2(p); p = mat2(0.8, -0.6, 0.6, 0.8) * p * 2.03; a *= 0.5; } return s / 0.9375; }
// inverted cellular noise: round billows
float worley(vec3 p){
  vec3 i = floor(p), f = fract(p);
  float d = 1.0;
  for (int z = -1; z <= 1; z++) for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++){
    vec3 g = vec3(float(x), float(y), float(z));
    vec3 o = h33(i + g);
    vec3 r = g + o - f;
    d = min(d, dot(r, r));
  }
  return 1.0 - sqrt(d);
}
float rm(float v, float a, float b){ return clamp((v - a) / (b - a), 0.0, 1.0); }

float coverageAt(vec2 xz){
  vec2 q = xz / 21000.0 + uSeed.xy;
  q += 0.42 * vec2(vn2(q * 1.9 + 3.1), vn2(q * 1.9 - 7.3)) - 0.21;
  float c = fbm2d(q);
  return smoothstep(0.62 - uCoverage * 0.42, 0.86 - uCoverage * 0.30, c);
}

// lod: 0 = full detail, 1 = light march (cheap)
float density(vec3 p, float alt, int lod){
  float hf = (alt - H0) / (H1 - H0);
  if (hf <= 0.0 || hf >= 1.0) return 0.0;
  float cov = coverageAt(p.xz);
  if (cov < 0.01) return 0.0;
  // every cell towers to its own height
  float topN = vn2(p.xz / 3400.0 + uSeed.yz);
  float top = mix(0.24, 1.0, pow(topN, 1.4) * (0.35 + 0.65 * cov));
  float prof = smoothstep(0.0, 0.055, hf) * (1.0 - smoothstep(top * 0.42, top, hf));
  // bases are flat, tops are cauliflower
  vec3 q = p / 2300.0 + vec3(0.0, uSeed.z, 0.0);
  q.y *= 1.25;
  float shape = worley(q) * 0.62 + worley(q * 2.1 + 5.0) * 0.26 + vn3(q * 4.3) * 0.12;
  float base = rm(shape, 1.0 - cov * prof * 0.92, 1.0);
  if (base <= 0.0) return 0.0;
  if (lod == 0){
    float det = worley(q * 5.3 + 2.0) * 0.6 + vn3(q * 11.0) * 0.4;
    base = rm(base, det * 0.46, 1.0);
  }
  // denser toward the top where the updraft condenses
  return base * mix(0.75, 1.25, hf);
}

float hg(float mu, float g){ float g2 = g * g; return (1.0 - g2) / (12.566 * pow(1.0 + g2 - 2.0 * g * mu, 1.5)); }

vec2 shell(vec3 ro, vec3 rd, float r){
  // ro relative to planet centre; returns near/far hit (or -1)
  float b = dot(ro, rd);
  float c = dot(ro, ro) - r * r;
  float h = b * b - c;
  if (h < 0.0) return vec2(-1.0);
  h = sqrt(h);
  return vec2(-b - h, -b + h);
}

void main(){
  // texel -> direction (must match cloudUV in sky.js)
  float az = (vUv.x - 0.5) * 6.2831853;
  float el = vUv.y * vUv.y * 1.5707963;
  vec3 rd = vec3(cos(az) * cos(el), sin(el), sin(az) * cos(el));
  vec3 C = vec3(0.0, -RP, 0.0);
  vec3 ro = vec3(0.0, 80.0, 0.0);
  vec3 col = vec3(0.0);
  float T = 1.0;
  float mu = dot(rd, uSunDir);

  // ---- cumulus
  float t0 = shell(ro - C, rd, RP + H0).y;
  float t1 = shell(ro - C, rd, RP + H1).y;
  if (t0 > 0.0 && t1 > t0){
    t1 = min(t1, t0 + 46000.0);
    const int STEPS = 84;
    float dt = (t1 - t0) / float(STEPS);
    float n = fract(52.9829189 * fract(dot(gl_FragCoord.xy, vec2(0.06711056, 0.00583715))) + uJitter);
    float t = t0 + dt * n;
    float phase = 0.74 + 2.3 * hg(mu, 0.80) + 0.5 * hg(mu, -0.3);
    for (int i = 0; i < STEPS; i++){
      vec3 p = ro + rd * t;
      float alt = length(p - C) - RP;
      float d = density(p, alt, 0);
      if (d > 0.002){
        // light march toward the sun
        float od = 0.0;
        float ls = 70.0;
        vec3 lp = p;
        for (int j = 0; j < 6; j++){
          lp += uSunDir * ls;
          float la = length(lp - C) - RP;
          od += density(lp, la, 1) * ls;
          ls *= 1.75;
        }
        float hf = clamp((alt - H0) / (H1 - H0), 0.0, 1.0);
        // multiple scattering keeps the sunlit side luminous instead of going grey
        float beer = max(exp(-od * SIGMA), 0.62 * exp(-od * SIGMA * 0.22));
        float powder = 1.0 - exp(-d * 90.0 * SIGMA * 2.0);
        vec3 sun = uSunColor * beer * mix(1.0, powder, 0.35) * phase;
        // sky light: lavender in the shaded bases, bright blue-white on top
        vec3 amb = mix(vec3(0.46, 0.52, 0.78), vec3(0.86, 0.96, 1.16), hf) * (0.70 + 0.30 * hf);
        amb += uAmbGround * 0.3 * (1.0 - hf);
        vec3 S = sun * 0.92 + amb * 0.80;
        // aerial perspective: distant towers sink into the haze
        float fogT = exp(-t * 2.6e-5);
        S = mix(skyBase(normalize(vec3(rd.x, max(rd.y, 0.0) * 0.5 + 0.03, rd.z))), S, fogT);
        float a = 1.0 - exp(-d * SIGMA * dt);
        col += T * S * a;
        T *= 1.0 - a;
        if (T < 0.012) break;
      }
      t += dt;
    }
  }

  // ---- cirrus: thin wind-combed ice high above
  float tc = shell(ro - C, rd, RP + 9500.0).y;
  if (tc > 0.0 && T > 0.02){
    vec3 p = ro + rd * tc;
    vec2 q = p.xz / 9000.0 + uSeed.zx;
    q = mat2(0.82, 0.57, -0.57, 0.82) * q;
    q += 0.5 * vec2(vn2(q * 0.7 + 2.0), vn2(q * 0.7 - 5.0));
    float streak = fbm2d(vec2(q.x * 0.55, q.y * 3.2));
    float sheet = fbm2d(q * 0.33 + 9.0);
    float c = smoothstep(0.50, 0.85, streak) * smoothstep(0.42, 0.70, sheet);
    c *= 0.55 * exp(-tc * 1.3e-5);
    vec3 S = uSunColor * (0.22 + hg(mu, 0.7) * 1.6) + vec3(0.5, 0.62, 0.85) * 0.5;
    col += T * S * c;
    T *= 1.0 - c;
  }

  // fade the deck out right at the horizon line so it meets the haze cleanly
  float hz = smoothstep(0.0, 0.035, rd.y);
  gl_FragColor = vec4(col * hz, (1.0 - T) * hz) * uWeight;
}
`;
