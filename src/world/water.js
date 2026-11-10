// Ocean: camera-centred radial grid, Gerstner swell, analytic seabed refraction, shore surf,
// sky + planar reflections, foam and the rider's wake.
import * as THREE from 'three';
import { U, World, shared } from '../core/ctx.js';
import { NOISE, NOISE_TEX, ATMOSPHERE, CLOUD_SHADOW, TERRAIN_LOOKUP, SHADOW } from '../shaders/common.js';
import { SKY_UNIFORMS, CLOUD_LOOKUP } from './sky.js';

const NW = 8;
// swell runs toward the south-south-east so it meets the north cliffs head on
const SWELL = Math.atan2(0.93, 0.36);
const WAVES = [
  // wavelength (m), steepness, direction offset (rad)
  [71, 0.085, 0.00],
  [47, 0.080, 0.31],
  [31, 0.075, -0.38],
  [19, 0.070, 0.62],
  [12.5, 0.062, -0.74],
  [8.1, 0.055, 0.21],
  [5.3, 0.048, -1.05],
  [3.4, 0.040, 1.18],
].map(([len, steep, off], i) => {
  const k = (2 * Math.PI) / len;
  const a = SWELL + off;
  return { dx: Math.cos(a), dz: Math.sin(a), k, amp: steep / k, w: Math.sqrt(9.81 * k), steep, ph: i * 1.7 };
});

export const SEA_STATE = { value: 0.62 };

/** CPU mirror of the vertex displacement: sea surface height at world xz. */
export function waveHeight(x, z, t, shelter = 1) {
  let y = 0;
  const s = SEA_STATE.value * shelter;
  for (const w of WAVES) y += w.amp * s * Math.sin(w.k * (w.dx * x + w.dz * z) - w.w * t + w.ph);
  return y;
}

const WAVE_GLSL = /* glsl */`
const int NW = ${NW};
uniform vec4 uWaveA[NW];   // dir.xz, k, amp
uniform vec4 uWaveB[NW];   // omega, steep, phase, -
uniform float uSea;
// displacement + analytic normal; fold = how hard the crests pinch (drives whitecaps)
vec3 gerstner(vec2 xz, float t, float amp, out vec3 nrm, out float fold){
  vec3 d = vec3(0.0);
  vec2 slope = vec2(0.0);
  float ny = 0.0;
  fold = 0.0;
  for (int i = 0; i < NW; i++){
    vec4 a = uWaveA[i]; vec4 b = uWaveB[i];
    float ph = a.z * dot(a.xy, xz) - b.x * t + b.z;
    float s = sin(ph), c = cos(ph);
    float A = a.w * amp;
    d.xz += a.xy * (b.y / a.z) * amp * c;
    d.y += A * s;
    slope += a.xy * (a.z * A * c);
    ny += b.y * amp * s;
    fold += b.y * amp * s;
  }
  nrm = normalize(vec3(-slope.x, 1.0 - ny, -slope.y));
  return d;
}
`;

export function makeWaveNormalTexture() {
  // tileable ripple field: slopes in RG, height in B, a second decorrelated height in A
  const S = 256;
  const data = new Uint8Array(S * S * 4);
  let seed = 99;
  const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  const comps = [];
  for (let i = 0; i < 44; i++) {
    const kx = Math.round((rnd() * 2 - 1) * 20), ky = Math.round((rnd() * 2 - 1) * 20);
    const kk = Math.hypot(kx, ky);
    if (kk < 2) continue;
    comps.push({ kx, ky, a: Math.pow(kk, -1.55), p: rnd() * 6.283, g: i % 2 });
  }
  const H = new Float32Array(S * S), HX = new Float32Array(S * S), HY = new Float32Array(S * S), H2 = new Float32Array(S * S);
  const tau = (2 * Math.PI) / S;
  for (const c of comps) {
    for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
      const ph = (c.kx * x + c.ky * y) * tau + c.p;
      const s = Math.sin(ph), co = Math.cos(ph);
      const i = y * S + x;
      if (c.g === 0) { H[i] += c.a * s; HX[i] += c.a * c.kx * co; HY[i] += c.a * c.ky * co; }
      else H2[i] += c.a * s;
      if (c.g === 1) { HX[i] += 0.5 * c.a * c.kx * co; HY[i] += 0.5 * c.a * c.ky * co; }
    }
  }
  const norm = (a) => { let m = 0; for (const v of a) m = Math.max(m, Math.abs(v)); return m || 1; };
  const mH = norm(H), mS = Math.max(norm(HX), norm(HY)), mH2 = norm(H2);
  for (let i = 0; i < S * S; i++) {
    data[i * 4] = 127.5 + 127.5 * (HX[i] / mS);
    data[i * 4 + 1] = 127.5 + 127.5 * (HY[i] / mS);
    data[i * 4 + 2] = 127.5 + 127.5 * (H[i] / mH);
    data[i * 4 + 3] = 127.5 + 127.5 * (H2[i] / mH2);
  }
  const t = new THREE.DataTexture(data, S, S, THREE.RGBAFormat, THREE.UnsignedByteType);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.generateMipmaps = true;
  t.minFilter = THREE.LinearMipmapLinearFilter;
  t.magFilter = THREE.LinearFilter;
  t.anisotropy = 8;
  t.needsUpdate = true;
  return t;
}

export class Water {
  constructor(sky) {
    // radial grid: dense underfoot, stretching to the horizon
    const RINGS = 230, SEGS = 256;
    const pos = new Float32Array((RINGS + 1) * SEGS * 3);
    let k = 0;
    for (let i = 0; i <= RINGS; i++) {
      const r = i === RINGS ? 60000 : 5.5 * (Math.pow(1.037, i) - 1);
      for (let j = 0; j < SEGS; j++) {
        const a = ((j + (i & 1) * 0.5) / SEGS) * Math.PI * 2;
        pos[k++] = Math.cos(a) * r; pos[k++] = 0; pos[k++] = Math.sin(a) * r;
      }
    }
    const idx = new Uint32Array(RINGS * SEGS * 6);
    k = 0;
    for (let i = 0; i < RINGS; i++) for (let j = 0; j < SEGS; j++) {
      const a = i * SEGS + j, b = i * SEGS + ((j + 1) % SEGS), c = a + SEGS, d = b + SEGS;
      idx[k++] = a; idx[k++] = b; idx[k++] = c; idx[k++] = b; idx[k++] = d; idx[k++] = c;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setIndex(new THREE.BufferAttribute(idx, 1));

    this.reflTex = { value: null };
    this.reflMat = { value: new THREE.Matrix4() };
    this.reflOn = { value: 0 };
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        ...shared(...SKY_UNIFORMS, 'uTime', 'uHeightTex', 'uSplatTex', 'uLightTex', 'uWorld', 'uNoiseTex', 'uWakeTex', 'uWake', 'uShadowTex', 'uShadowMat', 'uShadowOn'),
        uWaveA: { value: WAVES.map((w) => new THREE.Vector4(w.dx, w.dz, w.k, w.amp)) },
        uWaveB: { value: WAVES.map((w) => new THREE.Vector4(w.w, w.steep, w.ph, 0)) },
        uSea: SEA_STATE,
        uCenter: { value: new THREE.Vector2() },
        uRipple: { value: makeWaveNormalTexture() },
        uCloudTex: sky.cloudTex,
        uCloudOn: sky.cloudOn,
        uReflTex: this.reflTex,
        uReflMat: this.reflMat,
        uReflOn: this.reflOn,
        uFallBase: { value: new THREE.Vector3(1e6, 1e6, 1) },
      },
      vertexShader: VERT,
      fragmentShader: FRAG,
    });
    this.mesh = new THREE.Mesh(geo, this.material);
    this.mesh.frustumCulled = false;
    this.mesh.renderOrder = 10;
  }

  update(camera) {
    // snap the grid centre so the fine rings don't swim
    const c = this.material.uniforms.uCenter.value;
    c.set(Math.round(camera.position.x / 2) * 2, Math.round(camera.position.z / 2) * 2);
  }

  /** Planar reflection of the land: a mirrored camera renders the terrain into a half-size target. */
  setupReflection(renderer, terrain) {
    this.renderer = renderer;
    this.terrain = terrain;
    this.reflView = terrain.addView(0.55);
    this.reflScene = new THREE.Scene();
    this.reflScene.add(this.reflView.mesh);
    this.reflCam = new THREE.PerspectiveCamera();
    this.reflRT = new THREE.WebGLRenderTarget(4, 4, { type: THREE.HalfFloatType, format: THREE.RGBAFormat, depthBuffer: true, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter });
    this.reflTex.value = this.reflRT.texture;
    this._v = new THREE.Vector3(); this._t = new THREE.Vector3(); this._up = new THREE.Vector3(); this._save = new THREE.Vector3();
    this._bias = new THREE.Matrix4().set(0.5, 0, 0, 0.5, 0, 0.5, 0, 0.5, 0, 0, 0.5, 0.5, 0, 0, 0, 1);
  }

  renderReflection(camera, size) {
    if (!this.reflRT) return;
    const w = Math.max(8, size.x >> 1), h = Math.max(8, size.y >> 1);
    if (this.reflRT.width !== w || this.reflRT.height !== h) this.reflRT.setSize(w, h);
    // under water or far above there is nothing worth mirroring
    if (camera.position.y < 0.2 || camera.position.y > 900) { this.reflOn.value = 0; return; }
    const vc = this.reflCam;
    vc.fov = camera.fov; vc.aspect = camera.aspect; vc.near = camera.near; vc.far = camera.far;
    vc.updateProjectionMatrix();
    // mirror the eye, its target and its up vector through y = 0
    vc.position.set(camera.position.x, -camera.position.y, camera.position.z);
    const t = this._t.set(0, 0, -1).applyQuaternion(camera.quaternion).add(camera.position);
    t.y = -t.y;
    const up = this._up.set(0, 1, 0).applyQuaternion(camera.quaternion);
    up.y = -up.y;
    vc.up.copy(up);
    vc.lookAt(t);
    vc.updateMatrixWorld();

    const T = this.terrain, r = this.renderer;
    this._save.copy(U.uCamPos.value);
    U.uCamPos.value.copy(vc.position);
    T.material.uniforms.uClipY.value = 1;   // mirrored pass: keep only what stands above the sea
    T.select(this.reflView, vc, 150);
    r.setRenderTarget(this.reflRT);
    r.setClearColor(0x000000, 0);
    r.render(this.reflScene, vc);
    r.setClearColor(0x000000, 1);
    r.setRenderTarget(null);
    T.material.uniforms.uClipY.value = 0;
    U.uCamPos.value.copy(this._save);
    const pv = (this._m4 || (this._m4 = new THREE.Matrix4())).multiplyMatrices(vc.projectionMatrix, vc.matrixWorldInverse);
    this.reflMat.value.multiplyMatrices(this._bias, pv);
    this.reflOn.value = 1;
  }
}

const VERT = /* glsl */`
precision highp float;
uniform vec2 uCenter;
uniform float uTime;
uniform vec3 uCamPos;
${TERRAIN_LOOKUP}
${WAVE_GLSL}
varying vec3 vWorld;
varying vec2 vXZ0;
varying float vAmp;
void main(){
  vec2 xz = position.xz + uCenter;
  float r = length(position.xz);
  // waves calm down in shallow, sheltered water and fade out toward the horizon
  vec4 light = textureLod(uLightTex, worldUV(xz), 0.0);
  float off = shoreDist(light.b);                          // metres offshore (+) / inland (-)
  float shelter = mix(0.30, 1.0, smoothstep(0.0, 110.0, off));
  float amp = uSea * shelter / (1.0 + pow(r / 1400.0, 2.0));
  vec3 n; float fold;
  vec3 d = gerstner(xz, uTime, amp, n, fold);
  d *= 1.0 - smoothstep(4000.0, 9000.0, r);
  vWorld = vec3(xz.x, 0.0, xz.y) + d;
  vXZ0 = xz;
  vAmp = amp;
  gl_Position = projectionMatrix * viewMatrix * vec4(vWorld, 1.0);
}
`;

const FRAG = /* glsl */`
precision highp float;
varying vec3 vWorld;
varying vec2 vXZ0;
varying float vAmp;
uniform float uTime;
uniform sampler2D uRipple;
uniform sampler2D uReflTex;
uniform mat4 uReflMat;
uniform float uReflOn;
uniform vec3 uFallBase;   // xz + radius of the waterfall's plunge pool
uniform sampler2D uWakeTex;
uniform vec4 uWake;
${NOISE}
${NOISE_TEX}
${ATMOSPHERE}
${CLOUD_SHADOW}
${CLOUD_LOOKUP}
${TERRAIN_LOOKUP}
${WAVE_GLSL}

${SHADOW}

void main(){
  vec3 P = vWorld;
  vec3 toCam = uCamPos - P;
  float dist = length(toCam);
  vec3 V = toCam / dist;

  // ---- the rider's wake: xy = wind over the surface (lean units), z = agitation, w = foam freshness
  vec4 wk = vec4(0.0);
  vec2 wuv = (P.xz - uWake.xy) * uWake.z + 0.5;
  vec2 wedge = min(wuv, 1.0 - wuv);
  float wIn = smoothstep(0.0, 0.04, min(wedge.x, wedge.y));
  if (wIn > 0.0) wk = texture(uWakeTex, wuv) * wIn;
  float gale = min(length(wk.xy), 1.6);

  // ---- surface normal: swell (analytic) + two ripple layers + wind chop
  vec3 n; float fold;
  gerstner(vXZ0, uTime, vAmp, n, fold);
  vec2 w1 = vec2(0.36, 0.93);
  vec4 r1 = texture(uRipple, P.xz / 23.0 + w1 * uTime * 0.021);
  vec4 r2 = texture(uRipple, P.xz.yx / 7.3 - w1.yx * uTime * 0.034 + 0.4);
  vec4 r3 = texture(uRipple, P.xz / 61.0 + vec2(-0.3, 0.8) * uTime * 0.012 + 0.7);
  vec2 rip = (r1.xy - 0.5) * 0.9 + (r2.yx - 0.5) * 0.6 + (r3.xy - 0.5) * 0.7;
  float rippleFade = 1.0 / (1.0 + dist * 0.0016);
  // cat's-paws: ruffled patches and glassy slicks drifting with the wind
  float paws = ntex(P.xz * 0.045 + w1 * uTime * 0.9).r * 0.6 + ntex(P.xz * 0.013 - w1.yx * uTime * 0.25).b * 0.4;
  float chop = (0.30 + 0.55 * smoothstep(0.0, 0.8, vAmp)) * mix(0.35, 1.45, smoothstep(0.30, 0.70, paws));
  // the wake vortices rake the surface: two lanes of tight, hurried ripples spreading behind the broom
  vec4 r4 = texture(uRipple, P.xz / 2.3 + vec2(uTime * 0.31, -uTime * 0.23));
  vec4 r5 = texture(uRipple, P.xz.yx / 1.1 - vec2(uTime * 0.43, uTime * 0.37) + 0.6);
  vec2 ruffle = ((r4.xy - 0.5) * 1.3 + (r5.yx - 0.5) * 0.9) * smoothstep(0.12, 1.0, gale) * 1.7;
  vec3 N = normalize(n + vec3(rip.x, 0.0, rip.y) * chop * (0.35 + 0.65 * rippleFade) + vec3(ruffle.x, 0.0, ruffle.y));
  // looking along the surface the micro-normals average out
  float graze = 1.0 - saturate(dot(V, vec3(0.0, 1.0, 0.0)));

  // ---- seabed seen through the water (analytic: no scene copy needed)
  vec2 refr = P.xz - N.xz * 2.5;
  float bedH = terrainH(refr);
  float depth = max(P.y - bedH, 0.0);
  vec4 light = texture(uLightTex, worldUV(P.xz));
  float off = shoreDist(light.b);
  if (off < -30.0) discard;                                    // the sea does not run under the land
  float cliffy = light.a;
  float cs = cloudShadow(P.xz, uTime);
  float sunVis = light.r * cs * riderShadow(P);
  // sand in the lagoons, dark rock under the cliffs
  vec4 nz = ntex(refr * 0.9);
  vec3 bedCol = mix(vec3(0.80, 0.72, 0.52), vec3(0.12, 0.13, 0.12), smoothstep(0.2, 0.7, cliffy + (nz.r - 0.5) * 0.4));
  bedCol *= 0.75 + 0.5 * nz.g;
  // caustics dancing on the shallows
  vec2 cuv = refr * 0.19 + N.xz * 0.6;
  float ca = texture(uRipple, cuv + vec2(uTime * 0.035, 0.0)).b;
  float cb = texture(uRipple, cuv * 1.37 - vec2(0.0, uTime * 0.041)).a;
  float caust = pow(saturate(1.0 - abs(ca - cb) * 2.2), 5.0) * 1.6;
  float pathLen = depth * (1.0 + 1.0 / max(V.y, 0.25)) * 0.5;
  vec3 absorb = exp(-pathLen * vec3(0.46, 0.105, 0.072));
  vec3 bedLit = bedCol * (uSunColor * 0.30 * sunVis * (0.55 + caust * exp(-depth * 0.22)) + uAmbSky * 0.5);
  // light scattered back out of the water column
  vec3 deep = vec3(0.004, 0.105, 0.135);
  vec3 shallow = vec3(0.030, 0.420, 0.380);
  vec3 scat = mix(shallow, deep, saturate(1.0 - exp(-depth * 0.09)));
  scat *= (uSunColor * 0.42 * (0.35 + 0.65 * sunVis) + uAmbSky * 0.60);
  vec3 body = bedLit * absorb + scat * (1.0 - absorb * 0.9);
  // sunlight glowing through the thin crests
  float sss = pow(saturate(dot(V, -uSunDir) * 0.5 + 0.5), 3.0) * saturate(P.y * 0.9 + 0.25) * saturate(vAmp);
  body += vec3(0.02, 0.36, 0.30) * uSunColor * 0.11 * sss * sunVis;

  // ---- reflection
  float ndv = saturate(dot(N, V));
  float F = 0.02 + 0.98 * pow(1.0 - ndv, 5.0);
  F *= 1.0 - 0.35 * graze * graze;                             // rough sea is less mirror-like at the horizon
  vec3 R = reflect(-V, N);
  R.y = abs(R.y) + 0.015;
  R = normalize(R);
  vec3 sky = skyBase(R);
  vec4 cl = sampleClouds(R);
  sky = sky * (1.0 - cl.a) + cl.rgb;
  vec3 refl = sky;
  if (uReflOn > 0.5){
    vec4 rc = uReflMat * vec4(P.x, 0.0, P.z, 1.0);
    vec2 ruv0 = rc.xy / rc.w;
    // a ruffled sea smears a reflection down the screen and washes it out; sheltered water keeps it
    float rough = smoothstep(0.10, 0.62, vAmp);
    vec2 jit = N.xz * vec2(0.035, 0.075) * (0.35 + 1.0 / (1.0 + dist * 0.01));
    vec4 rt = texture(uReflTex, clamp(ruv0 + jit, 0.002, 0.998)) * 0.4
            + texture(uReflTex, clamp(ruv0 + jit * vec2(0.6, 2.2) + vec2(0.0, 0.012 * rough), 0.002, 0.998)) * 0.3
            + texture(uReflTex, clamp(ruv0 + jit * vec2(1.4, -1.6) + vec2(0.0, 0.030 * rough), 0.002, 0.998)) * 0.3;
    vec2 ed = min(ruv0, 1.0 - ruv0);
    refl = mix(sky, rt.rgb / max(rt.a, 1e-3), rt.a * mix(1.0, 0.42, rough) * smoothstep(0.0, 0.03, min(ed.x, ed.y)) * step(0.0, rc.w));
  }
  // sun glitter: tight sparkle up close, a broad shimmering road toward the horizon
  vec3 H = normalize(uSunDir + V);
  float ndh = saturate(dot(N, H));
  float rough = mix(0.035, 0.16, graze);
  float a2 = rough * rough;
  float D = a2 / (3.14159 * pow(ndh * ndh * (a2 - 1.0) + 1.0, 2.0));
  vec3 spec = uSunColor * min(D, 900.0) * 0.022 * sunVis * (0.3 + 0.7 * F / max(F, 0.02) * 0.4);

  vec3 col = mix(body, refl, F) + spec;

  // ---- foam
  vec4 fz1 = ntex(P.xz * 5.5 + vec2(uTime * 0.11, uTime * 0.07));
  vec4 fz2 = ntex(P.xz * 17.0 - vec2(uTime * 0.21, uTime * 0.13));
  float bubbles = fz1.r * 0.62 + fz2.g * 0.38;
  // whitecaps where the swell pinches
  float cap = smoothstep(0.30, 0.52, fold) * smoothstep(0.42, 0.66, bubbles) * smoothstep(40.0, 160.0, off) * 0.85;
  // surf: sets of waves rolling in and washing up the shore
  float shoreD = max(off, 0.0);
  float setNoise = ntex(P.xz * 0.11).b;
  float ph = shoreD * 0.13 + uTime * 0.62 + setNoise * 5.0;
  float roll = pow(saturate(sin(ph) * 0.5 + 0.5), 5.0);
  float beachy = 1.0 - smoothstep(0.05, 0.45, cliffy);
  float surfBand = roll * smoothstep(46.0, 6.0, shoreD) * smoothstep(0.52, 0.30, bubbles * (1.0 - roll * 0.5)) * beachy;
  float wash = smoothstep(7.5, 0.0, shoreD - (sin(uTime * 0.5 + setNoise * 6.0) * 0.5 + 0.5) * 3.0);
  float lace = smoothstep(0.36, 0.60, bubbles + wash * 0.35) * wash * beachy;
  // cliffs churn the water: a ragged collar of froth that surges, wider on some stretches than
  // others, with lace trailing off it
  float surge = sin(uTime * 0.9 + setNoise * 9.0 + shoreD * 0.25) * 0.5 + 0.5;
  float stretch = ntex(P.xz * 0.33 + 4.0).g;                       // calm coves, frothy points
  float reach = (1.6 + 5.2 * stretch) * (0.75 + 0.5 * surge);
  float collar = 1.0 - smoothstep(0.0, reach, shoreD);
  float froth = smoothstep(0.42, 0.74, collar * 1.05 + (bubbles - 0.5) * 0.95);
  float trail = smoothstep(15.0, 2.0, shoreD) * smoothstep(0.52 - 0.12 * surge, 0.72, bubbles + 0.10 * sin(uTime * 1.3 + setNoise * 9.0));
  float churn = max(froth, trail * 0.85) * smoothstep(0.08, 0.5, cliffy);
  float foam = max(max(cap, surfBand * 0.9), max(lace, churn));
  // the rider's wake: a long tail. Foam freshness falls away over half a minute - solid churn at
  // first, then lace, then flecks gathered into windrows - and a pale band of aerated water
  // outlasts the foam itself.
  float boil = 0.0;
  if (wk.a > 0.003){
    float ageN = clamp(-log(max(wk.a, 1e-4)) / 3.3, 0.0, 1.0);    // 0 just laid .. 1 after ~30 s
    float lace = ntex(P.xz * 2.3 + vec2(uTime * 0.04, -uTime * 0.03)).a * 0.55 + bubbles * 0.45;
    float rows = ntex(P.xz * 1.1 + 5.0).g;
    float cut = 0.22 + 0.62 * sqrt(ageN) + (rows - 0.5) * 0.22 * ageN;
    float wf = smoothstep(cut, cut + 0.15, lace) * (1.0 - smoothstep(0.80, 1.0, ageN));
    foam = max(foam, wf);
    boil = wf * (1.0 - smoothstep(0.0, 0.12, ageN));
    float slick = (1.0 - ageN) * (1.0 - ageN);
    col += vec3(0.03, 0.30, 0.27) * (slick * 0.80 + wk.z * 0.4) * (uSunColor * 0.11);
  }
  // the plunge pool under the waterfall boils
  float fd = distance(P.xz, uFallBase.xy);
  if (fd < uFallBase.z * 3.0){
    float ring = sin(fd * 0.9 - uTime * 3.0) * 0.5 + 0.5;
    float boil = smoothstep(uFallBase.z * 3.0, uFallBase.z * 0.4, fd);
    foam = max(foam, smoothstep(0.75 - boil * 0.75, 0.95 - boil * 0.55, bubbles + ring * 0.12 * (1.0 - boil)));
  }
  foam = saturate(foam);
  vec3 foamCol = vec3(0.93, 0.96, 0.98) * (uSunColor * 0.30 * (0.25 + 0.75 * sunVis) * saturate(dot(N, uSunDir) * 0.6 + 0.4) + uAmbSky * 0.62);
  // fresh churn is not a flat white: it boils, with green water showing through the thin patches
  foamCol *= 1.0 - boil * 0.30 * smoothstep(0.62, 0.30, fz2.b * 0.5 + fz1.g * 0.5);
  col = mix(col, foamCol, foam);

  col = applyAtmosphere(col, P);
  gl_FragColor = vec4(col, 1.0);
}
`;
