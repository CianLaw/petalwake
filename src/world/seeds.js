// Wind seeds: glowing wisps scattered around the island's best lines. Catching one rings a bell,
// throws petals and tops up the gust. They give the flying a reason to go low and close.
import * as THREE from 'three';
import { U, World, shared } from '../core/ctx.js';

function rng(seed) {
  let s = seed >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

/** Choose seed positions from the baked terrain so they sit where the flying is good. */
export function placeSeeds(terrain, meta) {
  const R = rng(4242), out = [];
  const sp = [0, 0, 0, 0];
  const add = (x, y, z, kind) => out.push({ x, y, z, kind, got: false });
  const far = (x, z, d) => out.every((s) => (s.x - x) ** 2 + (s.z - z) ** 2 > d * d);

  // flower meadows: low, in the thick of the drifts
  for (let tries = 0, n = 0; tries < 4000 && n < 13; tries++) {
    const x = (R() - 0.5) * World.size * 0.7, z = (R() - 0.5) * World.size * 0.6;
    const h = terrain.heightAt(x, z);
    if (h < 12 || h > 190) continue;
    terrain.splatAt(x, z, sp);
    if (sp[0] < 0.62 || sp[3] < 0.8 || !far(x, z, 330)) continue;
    add(x, h + 2.6, z, 'meadow'); n++;
  }
  // the fjord: skim the water between the walls
  for (let i = 0; i < meta.fjord.length - 1; i++) {
    const a = meta.fjord[i], b = meta.fjord[i + 1];
    add((a[0] + b[0]) / 2, 3.0, (a[1] + b[1]) / 2, 'water');
  }
  // sea stacks: over the tops of the tall ones, between the short ones
  for (const s of meta.stacks) {
    if (s[3] > 55) add(s[0], terrain.heightAt(s[0], s[1]) + 7, s[1], 'stack');
  }
  for (let i = 0; i + 1 < meta.stacks.length && out.length < 31; i += 3) {
    const a = meta.stacks[i], b = meta.stacks[i + 1];
    const x = (a[0] + b[0]) / 2, z = (a[1] + b[1]) / 2;
    if (terrain.heightAt(x, z) < 0) add(x, 3.0, z, 'water');
  }
  // cliff faces: halfway down, just off the rock
  for (let tries = 0, n = 0; tries < 6000 && n < 6; tries++) {
    const x = (R() - 0.5) * World.size * 0.75, z = -600 - R() * 1100;
    const h = terrain.heightAt(x, z);
    if (h < 70) continue;
    // walk north until we step off the edge
    let zz = z, found = false;
    for (let k = 0; k < 40; k++) { zz -= 8; if (terrain.heightAt(x, zz) < 1) { found = true; break; } }
    if (!found || !far(x, zz - 26, 380)) continue;
    add(x, Math.max(h * 0.45, 22), zz - 26, 'cliff'); n++;
  }
  // the lagoon
  const L = meta.lagoon;
  for (let i = 0; i < 4; i++) {
    const a = -Math.PI * (0.25 + 0.5 * (i / 3)), r = L[2] * 0.55;
    const x = L[0] + Math.cos(a) * r, z = L[1] + Math.sin(a) * r;
    if (terrain.heightAt(x, z) < 0) add(x, 2.6, z, 'water');
  }
  // the summit
  add(meta.peak[0], meta.peak[1] + 9, meta.peak[2], 'summit');
  return out;
}

export class Seeds {
  constructor(terrain, meta) {
    this.items = placeSeeds(terrain, meta);
    this.total = this.items.length;
    this.count = 0;
    const n = this.total;
    const g = new THREE.InstancedBufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 1, -1, 0, -1, 1, 0, 1, 1, 0]), 3));
    g.setIndex([0, 1, 2, 1, 3, 2]);
    this.aSeed = new THREE.InstancedBufferAttribute(new Float32Array(n * 4), 4);
    this.aSeed.setUsage(THREE.DynamicDrawUsage);
    this.items.forEach((s, i) => this.aSeed.array.set([s.x, s.y, s.z, 1], i * 4));
    g.setAttribute('iSeed', this.aSeed);
    g.instanceCount = n;
    const common = {
      transparent: true, depthWrite: false, side: THREE.DoubleSide,
      blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
      blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor,
    };
    const VERT = (beam) => /* glsl */`
      precision highp float;
      attribute vec4 iSeed;      // xyz, alive (1) .. collected (0)
      uniform float uTime;
      varying vec2 vUv;
      varying float vAlive;
      varying float vDist;
      void main(){
        float ph = iSeed.x * 0.37 + iSeed.z * 0.21;
        vec3 c = iSeed.xyz + vec3(0.0, sin(uTime * 1.3 + ph) * 0.35, 0.0);
        vec4 mv = viewMatrix * vec4(c, 1.0);
        vDist = -mv.z;
        ${beam ? /* glsl */`
          // a tall shaft that stays upright and turns to face the eye
          vec3 up = vec3(0.0, 1.0, 0.0);
          vec3 side = normalize(cross(up, cameraPosition - c));
          float w = 0.5 + vDist * 0.006;
          vec3 P = c + side * position.x * w + up * (position.y * 0.5 + 0.5) * 90.0;
          gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0);
        ` : /* glsl */`
          float size = (1.7 + 0.25 * sin(uTime * 3.1 + ph)) * (1.0 + min(vDist, 500.0) * 0.006);
          mv.xy += position.xy * size;
          gl_Position = projectionMatrix * mv;
        `}
        vUv = position.xy;
        vAlive = iSeed.w;
      }`;
    this.glowMat = new THREE.ShaderMaterial({
      uniforms: { ...shared('uTime') },
      vertexShader: VERT(false),
      fragmentShader: /* glsl */`
        precision highp float;
        varying vec2 vUv; varying float vAlive; varying float vDist;
        uniform float uTime;
        void main(){
          float r = length(vUv);
          float core = exp(-r * r * 60.0) * 3.0;
          float halo = exp(-r * r * 6.0) * 0.55;
          // four soft rays that slowly turn
          float a = atan(vUv.y, vUv.x) + uTime * 0.3;
          float rays = pow(abs(cos(a * 2.0)), 24.0) * exp(-r * 3.2) * 0.9;
          float v = (core + halo + rays) * vAlive * (1.0 - smoothstep(0.8, 1.0, r));
          v *= smoothstep(1.5, 5.0, vDist) * (1.0 - 0.75 * smoothstep(500.0, 1500.0, vDist));
          gl_FragColor = vec4(vec3(1.0, 0.86, 0.50) * v * 1.6, v);
        }`,
      ...common,
    });
    this.beamMat = new THREE.ShaderMaterial({
      uniforms: { ...shared('uTime') },
      vertexShader: VERT(true),
      fragmentShader: /* glsl */`
        precision highp float;
        varying vec2 vUv; varying float vAlive; varying float vDist;
        void main(){
          float y = vUv.y * 0.5 + 0.5;
          float v = pow(max(1.0 - abs(vUv.x), 0.0), 2.5) * pow(clamp(1.0 - y, 0.0, 1.0), 1.6) * smoothstep(0.0, 0.03, y);
          // only a guide from afar: fade it out as you close in
          v *= 0.10 * vAlive * smoothstep(40.0, 160.0, vDist);
          gl_FragColor = vec4(vec3(1.0, 0.88, 0.60) * v, v);
        }`,
      ...common,
    });
    this.group = new THREE.Group();
    for (const m of [this.beamMat, this.glowMat]) {
      const mesh = new THREE.Mesh(g, m);
      mesh.frustumCulled = false;
      mesh.renderOrder = 50;
      this.group.add(mesh);
    }
  }

  /** @returns the seed just collected, or null. */
  update(dt, pos) {
    let hit = null, dirty = false;
    const arr = this.aSeed.array;
    for (let i = 0; i < this.items.length; i++) {
      const s = this.items[i];
      if (s.got) {
        if (arr[i * 4 + 3] > 0) { arr[i * 4 + 3] = Math.max(0, arr[i * 4 + 3] - dt * 4); dirty = true; }
        continue;
      }
      const dx = s.x - pos.x, dy = s.y - pos.y, dz = s.z - pos.z;
      if (dx * dx + dy * dy + dz * dz < 5.5 * 5.5) { s.got = true; this.count++; hit = s; dirty = true; }
    }
    if (dirty) this.aSeed.needsUpdate = true;
    return hit;
  }

  /** Nearest uncollected seed, for the HUD compass. */
  nearest(pos) {
    let best = null, bd = 1e18;
    for (const s of this.items) {
      if (s.got) continue;
      const d = (s.x - pos.x) ** 2 + (s.z - pos.z) ** 2;
      if (d < bd) { bd = d; best = s; }
    }
    return best ? { seed: best, dist: Math.sqrt(bd) } : null;
  }
}
