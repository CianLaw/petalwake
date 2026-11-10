// The river: a ribbon that follows the valley carved into the terrain, then leaps off the fjord
// cliff as a waterfall. Water levels are read off the heightfield, so it always sits in its bed.
import * as THREE from 'three';
import { U, shared } from '../core/ctx.js';
import { NOISE, NOISE_TEX, ATMOSPHERE, CLOUD_SHADOW, TERRAIN_LOOKUP, SHADOW } from '../shaders/common.js';
import { SKY_UNIFORMS, CLOUD_LOOKUP } from './sky.js';
import { makeWaveNormalTexture } from './water.js';

const STEP = 1.5;         // metres between ribbon rows
const DEPTH = 0.55;       // water depth over the middle of the channel
const SPR_PUFF = 2;

export class River {
  constructor(terrain, meta, sky) {
    this.terrain = terrain;
    // ---- resample the path
    const path = meta.river;
    const rows = [];
    let s0 = 0, next = 0;
    for (let i = 0; i < path.length - 1; i++) {
      const a = path[i], b = path[i + 1];
      const dx = b[0] - a[0], dz = b[1] - a[1], len = Math.hypot(dx, dz);
      for (; next <= s0 + len; next += STEP) {
        const t = (next - s0) / len;
        rows.push({ x: a[0] + dx * t, z: a[1] + dz * t, hw: a[2] + (b[2] - a[2]) * t, tx: dx / len, tz: dz / len, s: next });
      }
      s0 += len;
    }
    // ---- water level: bed + depth, never rising downstream; stop at the brink
    let level = Infinity, end = rows.length;
    for (let i = 0; i < rows.length; i++) {
      const bed = terrain.heightAt(rows[i].x, rows[i].z);
      if (level < Infinity && bed < level - DEPTH - 3.0) { end = i; break; }   // the ground falls away: the brink
      level = Math.min(level, bed + DEPTH);
      rows[i].y = level;
      if (bed < 0.3) { end = i; break; }
    }
    this.rows = rows.slice(0, end);
    const R = this.rows, n = R.length;
    // ease the surface so steps in the bed read as glides
    for (let pass = 0; pass < 3; pass++) for (let i = 1; i < n - 1; i++) R[i].y = Math.min(R[i].y, (R[i - 1].y + R[i].y * 2 + R[i + 1].y) / 4 + 0.02);
    for (let i = 0; i < n; i++) {
      const a = R[Math.max(i - 2, 0)], b = R[Math.min(i + 2, n - 1)];
      R[i].slope = Math.max(0, (a.y - b.y) / Math.max(b.s - a.s, 1e-3));
    }

    // ---- ribbon
    const AC = 5;
    const pos = new Float32Array(n * AC * 3), flow = new Float32Array(n * AC * 4), dir = new Float32Array(n * AC * 2);
    for (let i = 0; i < n; i++) {
      const r = R[i], w = r.hw * 1.12;
      for (let j = 0; j < AC; j++) {
        const u = (j / (AC - 1)) * 2 - 1, k = i * AC + j;
        pos[k * 3] = r.x - r.tz * u * w; pos[k * 3 + 1] = r.y; pos[k * 3 + 2] = r.z + r.tx * u * w;
        flow[k * 4] = u; flow[k * 4 + 1] = r.s; flow[k * 4 + 2] = r.slope; flow[k * 4 + 3] = w;
        dir[k * 2] = r.tx; dir[k * 2 + 1] = r.tz;
      }
    }
    const idx = [];
    for (let i = 0; i < n - 1; i++) for (let j = 0; j < AC - 1; j++) {
      const a = i * AC + j, b = a + 1, c = a + AC, d = c + 1;
      idx.push(a, b, c, b, d, c);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.setAttribute('aFlow', new THREE.BufferAttribute(flow, 4));
    g.setAttribute('aDir', new THREE.BufferAttribute(dir, 2));
    g.setIndex(idx);
    const ripple = makeWaveNormalTexture();
    const uniforms = {
      ...shared(...SKY_UNIFORMS, 'uTime', 'uHeightTex', 'uLightTex', 'uWorld', 'uNoiseTex', 'uWakeTex', 'uWake', 'uShadowTex', 'uShadowMat', 'uShadowOn'),
      uRipple: { value: ripple },
      uCloudTex: sky.cloudTex,
      uCloudOn: sky.cloudOn,
    };
    this.material = new THREE.ShaderMaterial({ uniforms, vertexShader: RIVER_VERT, fragmentShader: RIVER_FRAG, side: THREE.DoubleSide });
    this.mesh = new THREE.Mesh(g, this.material);
    this.mesh.frustumCulled = false;
    this.mesh.renderOrder = 12;
    this.group = new THREE.Group();
    this.group.add(this.mesh);

    // ---- waterfall: a ballistic sheet from the brink to whatever it lands on
    const last = R[n - 1];
    const V0 = 5.0, G = 9.8;
    const top = new THREE.Vector3(last.x + last.tx * 1.0, last.y - 0.1, last.z + last.tz * 1.0);
    let T = 0;
    for (let t = 0; t < 12; t += 0.02) {
      const x = top.x + last.tx * V0 * t, z = top.z + last.tz * V0 * t, y = top.y - 0.5 * G * t * t;
      T = t;
      if (t > 0.3 && y < Math.max(terrain.heightAt(x, z), 0) + 0.2) break;
    }
    this.fall = {
      top, dir: new THREE.Vector2(last.tx, last.tz), T, hw: last.hw,
      base: new THREE.Vector3(top.x + last.tx * V0 * T, Math.max(top.y - 0.5 * G * T * T, 0), top.z + last.tz * V0 * T),
      height: 0.5 * G * T * T,
    };
    const FR = 56, FA = 7, layers = 3;
    const fpos = [], fa = [], fidx = [];
    for (let L = 0; L < layers; L++) {
      const off = (L - 1) * 0.9, wk = L === 1 ? 1.0 : 0.72, base0 = fpos.length / 3;
      for (let i = 0; i <= FR; i++) {
        const t = Math.pow(i / FR, 0.8) * T;
        const cx = top.x + last.tx * (V0 * t + off), cz = top.z + last.tz * (V0 * t + off), cy = top.y - 0.5 * G * t * t;
        const w = Math.max(last.hw, 4.2) * wk * (1.0 + 1.1 * (t / T));
        for (let j = 0; j < FA; j++) {
          const u = (j / (FA - 1)) * 2 - 1;
          // the sheet bows outward a little in the middle
          const bow = (1 - u * u) * 0.6 * (t / T);
          fpos.push(cx - last.tz * u * w + last.tx * bow, cy, cz + last.tx * u * w + last.tz * bow);
          fa.push(u, t, t / T, L * 7.31);
        }
      }
      for (let i = 0; i < FR; i++) for (let j = 0; j < FA - 1; j++) {
        const a = base0 + i * FA + j, b = a + 1, c = a + FA, d = c + 1;
        fidx.push(a, b, c, b, d, c);
      }
    }
    const fg = new THREE.BufferGeometry();
    fg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(fpos), 3));
    fg.setAttribute('aFall', new THREE.BufferAttribute(new Float32Array(fa), 4));
    fg.setIndex(fidx);
    this.fallMat = new THREE.ShaderMaterial({
      uniforms: { ...shared(...SKY_UNIFORMS, 'uTime', 'uNoiseTex', 'uLightTex', 'uWorld') },
      vertexShader: FALL_VERT, fragmentShader: FALL_FRAG, side: THREE.DoubleSide, alphaToCoverage: true,
    });
    this.fallMesh = new THREE.Mesh(fg, this.fallMat);
    this.fallMesh.frustumCulled = false;
    this.fallMesh.renderOrder = 13;
    this.group.add(this.fallMesh);

    this._buildGrid();
    this.acc = [0, 0, 0];
  }

  /** Coarse grid of water levels so particles and the flight model can ask "is there river here?". */
  _buildGrid() {
    const R = this.rows, C = (this.gc = 2.5);
    let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
    for (const r of R) { x0 = Math.min(x0, r.x - 12); x1 = Math.max(x1, r.x + 12); z0 = Math.min(z0, r.z - 12); z1 = Math.max(z1, r.z + 12); }
    this.gx0 = x0; this.gz0 = z0;
    const W = (this.gw = Math.ceil((x1 - x0) / C)), H = (this.gh = Math.ceil((z1 - z0) / C));
    const g = (this.grid = new Float32Array(W * H).fill(-Infinity));
    for (const r of R) {
      const rad = r.hw * 1.05, k = Math.ceil(rad / C);
      const cx = Math.floor((r.x - x0) / C), cz = Math.floor((r.z - z0) / C);
      for (let dz = -k; dz <= k; dz++) for (let dx = -k; dx <= k; dx++) {
        const ix = cx + dx, iz = cz + dz;
        if (ix < 0 || iz < 0 || ix >= W || iz >= H) continue;
        const px = x0 + (ix + 0.5) * C - r.x, pz = z0 + (iz + 0.5) * C - r.z;
        if (px * px + pz * pz > rad * rad) continue;
        g[iz * W + ix] = Math.max(g[iz * W + ix], r.y);
      }
    }
  }

  /** Water surface height at xz, or -Infinity away from the river. */
  levelAt(x, z) {
    const ix = Math.floor((x - this.gx0) / this.gc), iz = Math.floor((z - this.gz0) / this.gc);
    if (ix < 0 || iz < 0 || ix >= this.gw || iz >= this.gh) return -Infinity;
    return this.grid[iz * this.gw + ix];
  }

  /** Mist: hanging at the foot of the fall and peeling off the sheet on the way down. */
  update(dt, sprites, camPos, sun) {
    const f = this.fall;
    const d = camPos.distanceTo(f.base);
    this.near = Math.max(0, 1 - d / 420);
    if (d > 900) return;
    const rnd = (a, b) => a + Math.random() * (b - a);
    const spawn = (i, rate) => { this.acc[i] += rate * dt; const n = this.acc[i] | 0; this.acc[i] -= n; return n; };
    for (let i = spawn(0, 22); i > 0; i--) {
      const a = Math.random() * 6.283, r = Math.random() * f.hw * 1.6;
      sprites.spawn(f.base.x + Math.cos(a) * r, f.base.y + rnd(0.5, 4), f.base.z + Math.sin(a) * r,
        Math.cos(a) * rnd(1, 5) + f.dir.x * 2, rnd(1.5, 6), Math.sin(a) * rnd(1, 5) + f.dir.y * 2, {
          type: SPR_PUFF, r: 0.82 * sun[0], g: 0.88 * sun[1], b: 0.94 * sun[2], alpha: rnd(0.07, 0.16), size: rnd(4, 8), grow: rnd(14, 24), life: rnd(4, 8), drag: 0.9, grav: -0.25, add: 0.15,
        });
    }
    for (let i = spawn(1, 16); i > 0; i--) {
      const t = rnd(0.35, 1) * f.T, u = rnd(-1, 1);
      const x = f.top.x + f.dir.x * 5 * t - f.dir.y * u * f.hw, z = f.top.z + f.dir.y * 5 * t + f.dir.x * u * f.hw, y = f.top.y - 4.9 * t * t;
      sprites.spawn(x, y, z, f.dir.x * 4 + rnd(-1.5, 1.5), -9.8 * t * 0.35, f.dir.y * 4 + rnd(-1.5, 1.5), {
        type: SPR_PUFF, r: 0.85 * sun[0], g: 0.90 * sun[1], b: 0.95 * sun[2], alpha: rnd(0.08, 0.18), size: rnd(1.5, 3.5), grow: rnd(6, 11), life: rnd(2, 4), drag: 1.2, grav: 1.5, add: 0.15,
      });
    }
  }
}

// =========================================================================================
const RIVER_VERT = /* glsl */`
precision highp float;
attribute vec4 aFlow;   // across (-1..1), arc length, slope, half width
attribute vec2 aDir;
varying vec3 vWorld;
varying vec4 vFlow;
varying vec2 vDir;
uniform vec3 uCamPos;
void main(){
  vFlow = aFlow; vDir = aDir;
  // far away the terrain mesh is too coarse to hold a channel: float the ribbon up over it
  vec3 p = position;
  p.y += clamp((distance(p, uCamPos) - 110.0) * 0.006, 0.0, 5.0);
  // ...and draw it in a little, so the floating ribbon does not look wider than its bed
  p.xz -= vec2(-aDir.y, aDir.x) * aFlow.x * aFlow.w * 0.25 * smoothstep(110.0, 400.0, distance(position, uCamPos));
  vWorld = p;
  gl_Position = projectionMatrix * viewMatrix * vec4(p, 1.0);
}
`;

const RIVER_FRAG = /* glsl */`
precision highp float;
varying vec3 vWorld;
varying vec4 vFlow;
varying vec2 vDir;
uniform float uTime;
uniform sampler2D uRipple;
uniform sampler2D uWakeTex;
uniform vec4 uWake;
${NOISE}
${NOISE_TEX}
${ATMOSPHERE}
${CLOUD_SHADOW}
${CLOUD_LOOKUP}
${TERRAIN_LOOKUP}
${SHADOW}
void main(){
  vec3 P = vWorld;
  float bed = terrainH(P.xz);
  float depth = P.y - bed;
  float camD = distance(P, uCamPos);
  if (depth < -0.02 && camD < 110.0) discard;
  depth = max(depth, 0.0);
  float u = vFlow.x, s = vFlow.y, slope = vFlow.z, w = vFlow.w;
  vec3 V = normalize(uCamPos - P);
  // the current is quicker mid-stream and on the steeps
  float speed = (1.3 + 9.0 * slope) * (1.0 - 0.45 * u * u);
  vec2 f = vec2(u * w, s);
  vec4 r1 = texture(uRipple, f / vec2(6.0, 11.0) + vec2(0.0, -uTime * speed / 11.0));
  vec4 r2 = texture(uRipple, f / vec2(2.6, 4.6) + vec2(0.37, -uTime * speed * 1.3 / 4.6));
  vec2 rip = (r1.xy - 0.5) * 0.7 + (r2.xy - 0.5) * 0.5;
  vec2 across = vec2(-vDir.y, vDir.x);
  vec2 nxz = (across * rip.x + vDir * rip.y) * (0.28 + 1.4 * slope);
  vec3 N = normalize(vec3(nxz.x, 1.0, nxz.y));

  vec4 light = texture(uLightTex, worldUV(P.xz));
  float sun = light.r * cloudShadow(P.xz, uTime) * riderShadow(P);
  // stony bed seen through clear, slightly peaty water
  vec4 nz = ntex((P.xz + N.xz * 0.6) * 3.0);
  vec3 bedCol = mix(vec3(0.26, 0.22, 0.14), vec3(0.52, 0.48, 0.38), nz.r) * (0.6 + 0.6 * nz.g);
  vec3 absorb = exp(-max(depth, 0.0) * vec3(1.5, 0.62, 0.80));
  vec3 lightIn = uSunColor * 0.32 * (0.2 + 0.8 * sun) + uAmbSky * 0.55;
  vec3 body = bedCol * absorb * lightIn + vec3(0.016, 0.115, 0.095) * (1.0 - absorb.g) * lightIn;
  float F = 0.02 + 0.98 * pow(1.0 - saturate(dot(N, V)), 5.0);
  vec3 R = reflect(-V, N); R.y = abs(R.y) + 0.02; R = normalize(R);
  vec3 sky = skyBase(R);
  vec4 cl = sampleClouds(R);
  sky = sky * (1.0 - cl.a) + cl.rgb;
  // toward the banks the water mirrors the grass leaning over it rather than the sky
  float bankRefl = smoothstep(0.35, 1.0, abs(u)) * (0.45 + 0.4 * (1.0 - saturate(dot(V, vec3(0.0, 1.0, 0.0)))));
  sky = mix(sky * mix(0.72, 1.0, light.g), vec3(0.10, 0.19, 0.045) * (uSunColor * 0.3 * sun + uAmbSky * 0.6), bankRefl);
  vec3 H = normalize(uSunDir + V);
  float spec = pow(saturate(dot(N, H)), 380.0) * 22.0 * sun;
  // from afar a stream is a thread of dulled sky, not a mirror
  float farK = smoothstep(90.0, 320.0, camD);
  sky = mix(sky, sky * vec3(0.50, 0.60, 0.74), farK);
  vec3 col = mix(body, sky, F * mix(1.0, 0.85, farK)) + uSunColor * spec * 0.35 * (1.0 - farK);

  // white water: riffles on the steeps, a seam along each bank, the churn of our own wake
  float streak = ntex(vec2(f.x * 2.2, f.y * 0.45 - uTime * speed * 0.45)).b * 0.6 + ntex(vec2(f.x * 5.0, f.y * 1.3 - uTime * speed * 1.3) + 0.4).a * 0.4;
  float rapids = smoothstep(0.06, 0.34, slope);
  float foam = smoothstep(0.78 - 0.62 * rapids, 0.92 - 0.50 * rapids, streak);
  // a broken seam of froth where the current drags along the banks
  float bank = smoothstep(0.16, 0.02, depth) * smoothstep(0.52, 0.74, streak + 0.5 * rapids) * step(camD, 110.0);
  foam = max(foam, bank * 0.7);
  vec2 wuv = (P.xz - uWake.xy) * uWake.z + 0.5;
  if (wuv.x > 0.0 && wuv.x < 1.0 && wuv.y > 0.0 && wuv.y < 1.0){
    vec4 wk = texture(uWakeTex, wuv);
    // same slow ageing as on the sea: churn, then lace, then flecks
    float ageN = clamp(-log(max(wk.a, 1e-4)) / 3.3, 0.0, 1.0);
    float cut = 0.24 + 0.62 * sqrt(ageN);
    foam = max(foam, smoothstep(cut, cut + 0.16, streak) * (1.0 - smoothstep(0.80, 1.0, ageN)) * step(0.003, wk.a));
  }
  vec3 foamCol = vec3(0.92, 0.95, 0.97) * (uSunColor * 0.30 * (0.25 + 0.75 * sun) + uAmbSky * 0.62);
  col = mix(col, foamCol, saturate(foam));
  col = applyAtmosphere(col, P);
  gl_FragColor = vec4(col, 1.0);
}
`;

const FALL_VERT = /* glsl */`
precision highp float;
attribute vec4 aFall;   // across, fall time, fraction, layer seed
varying vec4 vFall;
varying vec3 vWorld;
void main(){
  vFall = aFall; vWorld = position;
  gl_Position = projectionMatrix * viewMatrix * vec4(position, 1.0);
}
`;

const FALL_FRAG = /* glsl */`
precision highp float;
varying vec4 vFall;
varying vec3 vWorld;
uniform float uTime;
uniform sampler2D uLightTex;
uniform vec4 uWorld;
${NOISE}
${NOISE_TEX}
${ATMOSPHERE}
void main(){
  float u = vFall.x, t = vFall.y, k = clamp(vFall.z, 0.0, 1.0), seed = vFall.w;
  // patterns ride down with the water: a feature keeps its (fall time - now) coordinate
  float a = (t - uTime) * 0.55;
  float strands = ntex(vec2((u + seed) * 60.0, a * 256.0 * 0.11)).r * 0.55 + ntex(vec2((u + seed) * 150.0 + 9.0, a * 256.0 * 0.23)).g * 0.45;
  float clumps = ntex(vec2((u + seed) * 20.0 + 3.0, a * 256.0 * 0.05)).b;
  // a glassy lip that tears into strands, then into veils
  float body = mix(1.0, 0.74, smoothstep(0.05, 0.7, k));
  float cut = mix(-0.05, 0.42, smoothstep(0.0, 0.85, k)) - (clumps - 0.5) * 0.35;
  float alpha = smoothstep(cut, cut + 0.22, strands) * body + (1.0 - smoothstep(0.0, 0.06, k)) * 0.9;
  alpha *= pow(max(1.0 - u * u, 0.0), mix(0.35, 0.9, k));
  alpha *= 1.0 - smoothstep(0.90, 1.0, k) * 0.6;
  if (alpha < 0.02) discard;
  float sun = texture(uLightTex, vWorld.xz * uWorld.y + 0.5).r;
  vec3 white = vec3(0.90, 0.94, 0.98) * (uSunColor * 0.30 * (0.3 + 0.7 * sun) + uAmbSky * 0.70);
  vec3 glass = vec3(0.30, 0.55, 0.52) * (uSunColor * 0.2 * sun + uAmbSky * 0.6);
  vec3 col = mix(glass, white, smoothstep(0.0, 0.10, k) * (0.6 + 0.4 * strands));
  col = applyAtmosphere(col, vWorld);
  gl_FragColor = vec4(col, clamp(alpha, 0.0, 1.0));
}
`;
