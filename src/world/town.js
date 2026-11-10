// The towns: every building is modelled in Blender (tools/town), seated on the terrain and packed
// into chunks by tools/town/assemble.py. This draws them: one material for everything (a texture
// array of stone, plaster, timber, slate, tile ... tinted per face), three levels of detail per
// chunk picked by distance, cloth that flies in the wind and in the broom's wake, turning sails,
// and a sun shadow map per town rendered once at load (the sun never moves), which the buildings,
// the ground and the grass all read so that streets lie in shade and roofs in light.
//
// It also answers two questions for the rest of the game: where the rider can land (pads), and how
// high the roofs are at a point (heightAt), which is what the broom collides with.
import * as THREE from 'three';
import { U, shared } from '../core/ctx.js';
import { NOISE, NOISE_TEX, ATMOSPHERE, CLOUD_SHADOW, TERRAIN_LOOKUP, WIND, SHADOW, TOWN_SHADOW } from '../shaders/common.js';
import { SKY_UNIFORMS } from './sky.js';
import { materialArrays, loadImage, dataTex } from './terrain.js';
import { SPR } from '../fx/particles.js';
import { waveHeight } from './water.js';

const NEAR = 135, MID = 560;       // metres: beyond NEAR the finest detail goes, beyond MID the middle level too
const MAX_TOWNS = 2;               // shadow maps the world shaders can read

export class Town {
  static async load(renderer, base = './assets') {
    let index;
    try { index = await fetch(`${base}/town/index.json`).then((r) => (r.ok ? r.json() : null)); } catch { index = null; }
    const town = new Town(renderer);
    // the ground masks (paving, cleared ground) belong to the terrain's fit and stand even with no buildings
    let masks = null;
    try { masks = await fetch(`${base}/town/masks.json`).then((r) => (r.ok ? r.json() : null)); } catch { masks = null; }
    if (masks) await Promise.all(Object.keys(masks).slice(0, MAX_TOWNS).map(async (id, i) => {
      const m = masks[id];
      U[`uTownMask${i}`].value = dataTex(await loadImage(`${base}/town/${m.file}`), { mips: true, aniso: 4 });
      U[`uTownRect${i}`].value.set(m.x0, m.z0, 1 / m.w, 1 / m.h);
    }));
    if (!index || !index.towns.length) return town;
    const [mats, tiles] = await Promise.all([materialArrays(`${base}/town/tex`), fetch(`${base}/town/tex/materials.json`).then((r) => r.json())]);
    town._material(mats, tiles);
    await Promise.all(index.towns.map(async (t) => {
      const [meta, buf] = await Promise.all([fetch(`${base}/town/${t.id}.json`).then((r) => r.json()), fetch(`${base}/town/${t.id}.bin`).then((r) => r.arrayBuffer())]);
      town._add(meta, buf);
    }));
    return town;
  }

  constructor(renderer) {
    this.renderer = renderer;
    this.group = new THREE.Group();
    this.chunks = [];
    this.spinners = [];
    this.floaters = [];
    this.pads = [];
    this.smokes = [];
    this.lamps = [];
    this.buildings = [];
    this.towns = [];
    this.solids = [];
    this.tris = 0;
  }

  _material(mats, tiles) {
    const tile = new Float32Array(16).fill(2.5);
    const lum = new Float32Array(16).fill(0.5);
    tiles.order.forEach((n, i) => { tile[i] = tiles.tile[n]; const m = tiles.mean[n]; lum[i] = Math.max(0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2], 0.02); });
    const uniforms = {
      ...shared(...SKY_UNIFORMS, 'uTime', 'uLightTex', 'uHeightTex', 'uSplatTex', 'uWorld', 'uNoiseTex', 'uWind', 'uWakeTex', 'uWake', 'uShadowTex', 'uShadowMat', 'uShadowOn',
        'uTownSh0', 'uTownSh1', 'uTownShM0', 'uTownShM1', 'uTownShP'),
      uMatC: { value: mats.color }, uMatN: { value: mats.normal }, uTile: { value: tile }, uLum: { value: lum },
    };
    this.material = new THREE.ShaderMaterial({ uniforms, vertexShader: VERT, fragmentShader: FRAG });
    this.depthMaterial = new THREE.ShaderMaterial({
      uniforms: {}, vertexShader: /* glsl */`void main(){ gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
      fragmentShader: /* glsl */`void main(){ gl_FragColor = vec4(1.0); }`, side: THREE.DoubleSide,
    });
  }

  _mesh(m, buf) {
    const g = new THREE.BufferGeometry();
    const pb = new THREE.InterleavedBuffer(new Int16Array(buf, m.pos, m.verts * 4), 4);
    g.setAttribute('position', new THREE.InterleavedBufferAttribute(pb, 3, 0, false));
    g.setAttribute('aMw', new THREE.InterleavedBufferAttribute(pb, 1, 3, false));
    const nb = new THREE.InterleavedBuffer(new Int8Array(buf, m.nrm, m.verts * 4), 4);
    g.setAttribute('normal', new THREE.InterleavedBufferAttribute(nb, 3, 0, true));
    g.setAttribute('aAo', new THREE.InterleavedBufferAttribute(nb, 1, 3, true));
    g.setAttribute('aUv', new THREE.BufferAttribute(new Int16Array(buf, m.uv, m.verts * 2), 2, false));
    g.setAttribute('aCol', new THREE.BufferAttribute(new Uint8Array(buf, m.col, m.verts * 4), 4, true));
    const n = m.index[2];
    g.setIndex(new THREE.BufferAttribute(m.index32 ? new Uint32Array(buf, m.idx, n) : new Uint16Array(buf, m.idx, n), 1));
    g.boundingBox = new THREE.Box3(new THREE.Vector3(-32767, -32767, -32767), new THREE.Vector3(32767, 32767, 32767));
    g.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 32767 * Math.sqrt(3));
    const mesh = new THREE.Mesh(g, this.material);
    mesh.position.fromArray(m.center);
    mesh.scale.set(m.extent[0] / 32767, m.extent[1] / 32767, m.extent[2] / 32767);
    mesh.renderOrder = 290;
    return mesh;
  }

  _add(meta, buf) {
    const tg = new THREE.Group();
    tg.name = meta.id;
    const box = new THREE.Box3(new THREE.Vector3(meta.aabb[0], meta.aabb[1], meta.aabb[2]), new THREE.Vector3(meta.aabb[3], meta.aabb[4], meta.aabb[5]));
    const t = { id: meta.id, name: meta.name, box, group: tg, shadowSize: meta.shadow ?? 2048, casters: [] };
    for (const c of meta.chunks) {
      const mesh = this._mesh(c, buf);
      mesh.updateMatrixWorld(true);
      const cb = new THREE.Box3(new THREE.Vector3(c.aabb[0], c.aabb[1], c.aabb[2]), new THREE.Vector3(c.aabb[3], c.aabb[4], c.aabb[5]));
      this.chunks.push({ mesh, box: cb, index: c.index, level: 2 });
      tg.add(mesh);
      t.casters.push(mesh);
      this.tris += c.index[2] / 3;
    }
    for (const s of meta.spinners || []) {
      const mesh = this._mesh(s, buf);
      const pivot = new THREE.Group();
      pivot.position.fromArray(s.pivot);
      pivot.add(mesh);
      tg.add(pivot);
      this.spinners.push({ pivot, axis: new THREE.Vector3().fromArray(s.axis).normalize(), speed: s.speed, wind: s.wind, angle: Math.random() * 6.28, index: s.index, mesh });
    }
    for (const f of meta.floaters || []) {
      const mesh = this._mesh(f, buf);
      const pivot = new THREE.Group();
      pivot.position.set(f.x, 0, f.z);
      pivot.add(mesh);
      tg.add(pivot);
      this.floaters.push({ pivot, mesh, x: f.x, z: f.z, draft: f.draft || 0, index: f.index, ph: Math.random() * 6.28 });
    }
    for (const p of meta.pads) {
      this.pads.push({ id: p.id, name: p.name, spot: p.spot, town: meta.name, townId: meta.id, building: p.building, pos: new THREE.Vector3().fromArray(p.pos),
        radius: p.radius, yaw: p.yaw, approach: p.approach, ground: p.ground });
    }
    for (const s of meta.smokes || []) this.smokes.push({ pos: new THREE.Vector3().fromArray(s.pos), strength: s.strength, t: Math.random() });
    for (const l of meta.lamps || []) this.lamps.push({ pos: new THREE.Vector3().fromArray(l.pos), strength: l.strength });
    for (const b of meta.buildings) this.buildings.push({ ...b, town: meta.id });
    for (const so of meta.solids || []) this.solids.push({ ...so, x1: so.x0 + so.nx * so.cell, z1: so.z0 + so.nz * so.cell, grid: new Uint16Array(buf, so.offset, so.nx * so.nz) });
    this.towns.push(t);
    this.group.add(tg);
  }

  /** Draw each town's depth from the sun, once: the sun stands still, and so do the buildings. */
  bakeShadows() {
    if (!this.towns.length) return;
    const r = this.renderer, sun = U.uSunDir.value;
    const reversed = r.capabilities.reversedDepthBuffer === true;
    const biggest = this.towns.filter((t) => t.shadowSize > 0).sort((a, b) => b.shadowSize - a.shadowSize).slice(0, MAX_TOWNS);
    const P = U.uTownShP.value;
    P.set(0, 0, 0, 0);
    const scene = new THREE.Scene();
    scene.overrideMaterial = this.depthMaterial;
    const keepShadow = r.shadowMap.enabled;
    r.shadowMap.enabled = false;
    biggest.forEach((t, i) => {
      const S = t.shadowSize;
      const depth = new THREE.DepthTexture(S, S, THREE.FloatType);
      depth.minFilter = depth.magFilter = THREE.NearestFilter;
      const rt = new THREE.WebGLRenderTarget(S, S, { depthTexture: depth, depthBuffer: true, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
      const c = t.box.getCenter(new THREE.Vector3());
      const cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 1, 2);
      cam.position.copy(c).addScaledVector(sun, 600);
      cam.up.set(0, 1, 0);
      cam.lookAt(c);
      cam.updateMatrixWorld();
      // fit the box of the town (plus the ground its shadows fall on) in light space
      const inv = cam.matrixWorld.clone().invert();
      const lo = new THREE.Vector3(Infinity, Infinity, Infinity), hi = new THREE.Vector3(-Infinity, -Infinity, -Infinity), v = new THREE.Vector3();
      for (let k = 0; k < 8; k++) {
        v.set(k & 1 ? t.box.max.x + 6 : t.box.min.x - 6, k & 2 ? t.box.max.y + 2 : t.box.min.y - 30, k & 4 ? t.box.max.z + 6 : t.box.min.z - 6).applyMatrix4(inv);
        lo.min(v); hi.max(v);
      }
      cam.left = lo.x; cam.right = hi.x; cam.bottom = lo.y; cam.top = hi.y; cam.near = -hi.z - 5; cam.far = -lo.z + 5;
      cam.updateProjectionMatrix();
      const parents = t.casters.map((m) => m.parent);
      t.casters.forEach((m) => scene.add(m));
      r.setRenderTarget(rt);
      r.clear();
      r.render(scene, cam);
      r.setRenderTarget(null);
      t.casters.forEach((m, k) => parents[k].add(m));
      const n = cam.near, f = cam.far;
      const proj = new THREE.Matrix4().set(
        1 / (hi.x - lo.x), 0, 0, -lo.x / (hi.x - lo.x),
        0, 1 / (hi.y - lo.y), 0, -lo.y / (hi.y - lo.y),
        0, 0, -1 / (f - n), -n / (f - n),
        0, 0, 0, 1);
      U[`uTownShM${i}`].value.multiplyMatrices(proj, cam.matrixWorldInverse);
      U[`uTownSh${i}`].value = depth;
      // on flag (1 standard depth, 2 reversed), then metres of depth per unit and the texel size
      if (i === 0) { P.x = reversed ? 2 : 1; P.z = f - n; } else { P.y = reversed ? 2 : 1; P.w = f - n; }
      t.shadow = { rt, cam, texel: (hi.x - lo.x) / S };
    });
    r.shadowMap.enabled = keepShadow;
  }

  /** Top of whatever is built at (x, z), in metres; -1e9 where nothing is. */
  heightAt(x, z) {
    let h = -1e9;
    for (const s of this.solids) {
      if (x < s.x0 || z < s.z0 || x >= s.x1 || z >= s.z1) continue;
      const v = s.grid[((z - s.z0) / s.cell | 0) * s.nx + ((x - s.x0) / s.cell | 0)];
      if (v) { const y = s.y0 + v * s.step; if (y > h) h = y; }
    }
    return h;
  }

  /** The town the point is in (its name), or null. */
  nameAt(x, z) {
    for (const t of this.towns) {
      if (!t.shadowSize) continue;                       // (the lone farms are not a place of their own)
      if (x > t.box.min.x - 25 && x < t.box.max.x + 25 && z > t.box.min.z - 25 && z < t.box.max.z + 25) return t.name;
    }
    return null;
  }

  /** Chimney smoke: it rises, leans with the wind, and is torn up by the broom's wake like everything else. */
  ambient(dt, fx, camera) {
    if (!fx || !fx.sprites) return;
    const p = camera.position;
    for (const s of this.smokes) {
      const d2 = s.pos.distanceToSquared(p);
      if (d2 > 380 * 380) continue;
      s.t -= dt * (d2 < 160 * 160 ? 1 : 0.5);
      if (s.t > 0) continue;
      s.t = 0.30 + Math.random() * 0.25;
      const g = 0.62 + Math.random() * 0.2;
      fx.sprites.spawn(s.pos.x + (Math.random() - 0.5) * 0.12, s.pos.y, s.pos.z + (Math.random() - 0.5) * 0.12,
        (Math.random() - 0.5) * 0.25, 0.9 + Math.random() * 0.5, (Math.random() - 0.5) * 0.25,
        { type: SPR.PUFF, r: g, g: g * 0.985, b: g * 0.96, alpha: 0.20 * s.strength, size: 0.38, grow: 2.3 + Math.random() * 1.2, life: 5 + Math.random() * 3.5, drag: 0.5, grav: -0.05, wind: 0.55 });
    }
  }

  update(dt, time, camera) {
    const p = camera.position;
    for (const c of this.chunks) {
      const d = c.box.distanceToPoint(p);
      const level = d < NEAR ? 2 : d < MID ? 1 : 0;
      if (level !== c.level) { c.level = level; c.mesh.geometry.setDrawRange(0, c.index[level]); }
    }
    // boats ride the harbour's swell and tug at their moorings
    for (const f of this.floaters) {
      const k = 0.43, e = 1.6;
      const h0 = waveHeight(f.x, f.z, time, k);
      f.pivot.position.y = h0 - f.draft;
      f.pivot.rotation.set((waveHeight(f.x, f.z + e, time, k) - waveHeight(f.x, f.z - e, time, k)) / (2 * e) * 0.9, Math.sin(time * 0.23 + f.ph) * 0.05,
        -(waveHeight(f.x + e, f.z, time, k) - waveHeight(f.x - e, f.z, time, k)) / (2 * e) * 0.9);
      const d = f.pivot.position.distanceTo(p);
      f.mesh.geometry.setDrawRange(0, f.index[d < NEAR ? 2 : d < MID ? 1 : 0]);
    }
    const w = U.uWind.value.z;
    for (const s of this.spinners) {
      s.angle += dt * s.speed * 6.2832 * (s.wind ? 0.55 + 0.45 * w : 1);
      s.pivot.quaternion.setFromAxisAngle(s.axis, s.angle);
      const d = s.pivot.position.distanceTo(p);
      s.mesh.geometry.setDrawRange(0, s.index[d < NEAR ? 2 : d < MID ? 1 : 0]);
    }
  }
}

const VERT = /* glsl */`
precision highp float;
attribute float aMw;      // material + 32 * wind weight (0..31)
attribute float aAo;
attribute vec2 aUv;       // 1/256 m
attribute vec4 aCol;      // tint (sRGB), paint amount
uniform float uTime;
${NOISE_TEX}
${WIND}
varying vec3 vWorld;
varying vec3 vN;
varying vec2 vUv;
varying vec4 vCol;
varying vec3 vInfo;       // material, ambient occlusion, wind weight
void main(){
  float mat = mod(aMw, 32.0);
  float wind = floor(aMw / 32.0) / 31.0;
  vec4 wp = modelMatrix * vec4(position, 1.0);
  vec3 n = normalize(mat3(modelMatrix) * (normal / vec3(modelMatrix[0][0], modelMatrix[1][1], modelMatrix[2][2])));
  if (wind > 0.001) {
    // cloth and leaves: stream with the gusts, flutter, and thrash when the broom goes by
    float gust = windGust(wp.xz, uTime);
    vec3 wd = vec3(uWind.x, 0.0, uWind.y);
    float ph = dot(wp.xyz, vec3(1.7, 2.3, 1.1));
    float fl = sin(uTime * 6.1 + ph) * 0.6 + sin(uTime * 9.7 + ph * 1.7) * 0.4;
    wp.xyz += (wd * (0.10 + 0.34 * gust) + n * fl * (0.05 + 0.10 * gust) + vec3(0.0, fl * 0.03, 0.0)) * wind;
    vec4 wk = wakeAt(wp.xz);
    wp.xz += wk.xy * 0.30 * wind;
  }
  vWorld = wp.xyz;
  vN = n;
  vUv = aUv / 256.0;
  vCol = vec4(pow(aCol.rgb, vec3(2.2)), aCol.a);
  vInfo = vec3(mat, aAo, wind);
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const FRAG = /* glsl */`
precision highp float;
precision highp sampler2DArray;
uniform float uTime;
uniform sampler2DArray uMatC;
uniform sampler2DArray uMatN;
uniform float uTile[16];
uniform float uLum[16];     // each material's mean brightness: a painted surface keeps its grain, not its colour
varying vec3 vWorld;
varying vec3 vN;
varying vec2 vUv;
varying vec4 vCol;
varying vec3 vInfo;
${NOISE}
${NOISE_TEX}
${ATMOSPHERE}
${CLOUD_SHADOW}
${TERRAIN_LOOKUP}
${SHADOW}
${TOWN_SHADOW}
void main(){
  int mat = int(vInfo.x + 0.5);
  vec3 N = normalize(vN);
  if (!gl_FrontFacing) N = -N;
  vec3 V = normalize(uCamPos - vWorld);
  vec3 alb = vCol.rgb;
  float rough = 0.85, metal = 0.0, glow = 0.0, glass = 0.0;
  if (mat < 13) {
    float tile = uTile[mat];
    vec3 uvw = vec3(vUv / tile, float(mat));
    vec4 c = texture(uMatC, uvw);
    vec3 nt = texture(uMatN, uvw).xyz;
    // painted wood keeps only the grain's light and dark
    float l = dot(c.rgb, vec3(0.2126, 0.7152, 0.0722));
    alb = mix(c.rgb * vCol.rgb, vec3(min(l / uLum[mat] * 0.92, 1.5)) * vCol.rgb, vCol.a);
    rough = mix(0.62, 0.98, nt.z);
    // tangent frame from the lie of the uvs on the surface
    vec3 dp1 = dFdx(vWorld), dp2 = dFdy(vWorld);
    vec2 du1 = dFdx(vUv), du2 = dFdy(vUv);
    vec3 dp2p = cross(dp2, N), dp1p = cross(N, dp1);
    vec3 T = dp2p * du1.x + dp1p * du2.x, B = dp2p * du1.y + dp1p * du2.y;
    float inv = inversesqrt(max(max(dot(T, T), dot(B, B)), 1e-12));
    vec2 nxy = (nt.xy * 2.0 - 1.0) * vec2(1.0, -1.0);
    float fade = 1.0 - smoothstep(60.0, 260.0, length(uCamPos - vWorld));
    N = normalize(N + (T * nxy.x + B * nxy.y) * inv * 0.85 * fade);
  } else if (mat == 13) {            // metal
    metal = 1.0; rough = 0.42;
  } else if (mat == 14) {            // window glass
    glass = 1.0; rough = 0.08;
    alb = mix(vec3(0.030, 0.045, 0.060), vCol.rgb * 0.5, step(0.01, 1.0 - min(vCol.r, min(vCol.g, vCol.b))) * 0.6);
  } else if (mat == 15) {            // cloth
    float w = ntex(vUv * 60.0).r;
    alb *= 0.95 + 0.08 * w; rough = 0.95;
  } else if (mat == 17) {            // lamp glass
    glow = 1.0;
  } else if (mat == 18) {            // still water in a basin
    alb = vec3(0.035, 0.16, 0.17); rough = 0.06; glass = 0.6;
  }
  float ao = vInfo.y;
  vec4 light = texture(uLightTex, worldUV(vWorld.xz));
  float sunVis = light.r * cloudShadow(vWorld.xz, uTime) * townShadow(vWorld, N) * riderShadow(vWorld);
  float ndl = dot(N, uSunDir);
  float dif = saturate(ndl);
  // sky from above, the warm street and the neighbours' sunlit walls from below and the sides
  vec3 amb = mix(uAmbGround, uAmbSky, N.y * 0.5 + 0.5) * 1.12;
  amb += uSunColor * vec3(0.20, 0.17, 0.12) * 0.30 * saturate(0.75 - N.y * 0.75) * light.g;
  amb *= mix(0.42, 1.0, ao);
  vec3 col = alb * (uSunColor * dif * sunVis * mix(0.80, 1.0, ao) + amb);
  // highlights: a sheen on slate and glass, a glint on metal
  vec3 H = normalize(uSunDir + V);
  float a = max(rough * rough, 0.02);
  float ndh = saturate(dot(N, H));
  float D = a * a / (3.14159 * pow(ndh * ndh * (a * a - 1.0) + 1.0, 2.0));
  vec3 F0 = mix(vec3(0.04), alb, metal);
  col = mix(col, col * 0.35, metal * 0.6);
  col += uSunColor * sunVis * dif * min(D, 40.0) * F0 * mix(0.25, 1.0, max(metal, glass));
  if (glass > 0.0 || metal > 0.0) {
    vec3 R = reflect(-V, N);
    float fres = pow(1.0 - saturate(dot(N, V)), 4.0);
    vec3 sky = skyBase(normalize(vec3(R.x, abs(R.y) * 0.8 + 0.08, R.z)));
    col += sky * mix(0.10 + 0.55 * fres, 0.30, metal) * mix(vec3(1.0), alb, metal) * mix(0.5, 1.0, ao) * max(glass, metal);
  }
  col += vec3(1.0, 0.70, 0.36) * glow * 2.4;
  col = applyAtmosphere(col, vWorld);
  gl_FragColor = vec4(col, 1.0);
}
`;
