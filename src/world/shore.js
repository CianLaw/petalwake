// Shore life: what clings to the rocks and what the tide leaves, and the crabs that live among it.
//
//  - Dressing. Barnacles, mussels, limpets, anemones, urchins, starfish, shells, cobbles, boulders
//    with their tide bands, rockweed that lifts when a swell covers it, kelp that floats on the
//    sea, driftwood and wrack. Placements are deterministic (hashed world lattices), worked out on
//    the CPU a 24 m cell at a time, straight from the height field, wherever the terrain passes
//    through the shore band - so nothing is baked to disk and a reshaped coast needs no rebuild.
//    Each cell's meshes are written into ONE shared vertex buffer, so thirty-odd kinds of mesh
//    cost a single draw call. A cell is held at one of three levels of detail; things shrink away
//    before their level is dropped, and only the cells in view are in the index list.
//  - Tide lines. The terrain's own triangles along the shore are drawn a second time, exactly
//    coplanar, with a procedural layer on top: a barnacle crust, mussel beds, a green film and
//    lichen on rock; the strand line of dried weed on sand. The same pass lays a blob of shade
//    under boulders and logs and draws the crabs' burrows.
//  - Crabs. A few hundred at most, simulated on the CPU, drawn instanced (two levels of detail);
//    the walk cycle is in the vertex shader. They stand about and wander near home, bolt when the
//    rider comes close - to a burrow, under a boulder or into the sea - and come back out later.
//
// Towns (assets/terrain/meta.json `towns`) are kept clear: see TOWN_MAX_R below.
// Draw calls: dressing, tide lines, crabs near, crabs far. The kit of meshes is modelled by
// tools/shore/build_shore.py (Blender) into assets/shore/.
import * as THREE from 'three';
import { U, World, shared } from '../core/ctx.js';
import { NOISE, NOISE_TEX, ATMOSPHERE, CLOUD_SHADOW, TERRAIN_LOOKUP, SHADOW } from '../shaders/common.js';
import { SKY_UNIFORMS } from './sky.js';
import { SEA_STATE } from './water.js';

// ------------------------------------------------------------------------------------ tuning
const CELL = 24;                       // metres: one cell = one leaf node of the terrain quadtree
const TIER_R = [66, 126, 284];         // a cell this close is baked at detail 0 / 1 / 2
const TIER_KEEP = 10;                  // ...and keeps that level this much further out
const FADE = [54, 108, 250];           // small / middling / big things are gone by here
const OFF_RANGE = 8;                   // metres a vertex may sit from its pivot
const WORK_UNITS = 3200;               // vertices' worth of baking per frame
const DENSITY = 1.0;

export const CRAB = {
  max: 360,
  scareRadius: 18,                     // metres from the rider's path (each crab has its own nerve: 0.7 .. 1.1 of this)
  lookAhead: 0.15,                     // seconds of that path: a fast rider is seen from a little further off
  ceiling: 26,                         // a rider this high overhead is nobody's business
  flee: 3.0, walk: 0.6,                // m/s
  drawRadius: 90, nearRadius: 24,
  calm: [5, 11],                       // seconds in hiding after the coast is clear
  stride: 0.085,                       // leg reach, in carapace widths (the shader's too)
};
// Towns: inside the circles listed in assets/terrain/meta.json (`towns`: x, z, r) the ground is
// made stonework. No crab lives there and nothing is strewn there: no boulders, wrack, driftwood,
// shells or kelp. The one thing let in is what grows on wet stone - weed, mussels, barnacles,
// limpets - where the terrain itself stands in the tide as steep rock and nothing is built on it:
// the foot of a quay wall, the flank of a mole. Bigger circles than this are not towns but
// scattered farms: there only the buildings themselves are kept clear (Town.heightAt). And a town
// whose ground stands higher than TOWN_SHORE_MAX_Y above the sea (Cairnwick, on its cliff top)
// has no shore of its own: the beach at the foot of its cliff is left wild.
const TOWN_MAX_R = 400, TOWN_SHORE_MAX_Y = 30;
// A quay wall is not terrain, so its waterline gets a row of growth of its own. Larkhaven's:
// the face runs along x at z (where it meets the deck, `deck` metres above the sea) and leans
// out `batter` per metre down; the sea is on the +z side. (tools/town/layout.py, parts_p.py)
const QUAYS = [{ x0: -176, x1: 14, z: 1128.9, deck: 4.46, batter: 0.04 }];

const SMALL = 0, MID = 1, BIG = 2;     // how far off a thing is still drawn: FADE[...]

// swell: the same eight waves as water.js (replaced by the water's own table when attached)
const SWELL = Math.atan2(0.93, 0.36);
const WAVES = [[71, 0.085, 0.00], [47, 0.080, 0.31], [31, 0.075, -0.38], [19, 0.070, 0.62], [12.5, 0.062, -0.74], [8.1, 0.055, 0.21], [5.3, 0.048, -1.05], [3.4, 0.040, 1.18]]
  .map(([len, steep, off], i) => { const k = (2 * Math.PI) / len, a = SWELL + off; return { dx: Math.cos(a), dz: Math.sin(a), k, amp: steep / k, w: Math.sqrt(9.81 * k), steep, ph: i * 1.7 }; });

const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const sstep = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
const lerp = (a, b, t) => a + (b - a) * t;

// ------------------------------------------------------------------------------------ hashing
function hash2(ix, iz, salt) {
  let h = Math.imul(ix | 0, 374761393) ^ Math.imul(iz | 0, 668265263) ^ Math.imul(salt | 0, 0x9E3779B1);
  h = Math.imul(h ^ (h >>> 15), 0x85EBCA77);
  h = Math.imul(h ^ (h >>> 13), 0xC2B2AE3D);
  return (h ^ (h >>> 16)) >>> 0;
}
let _seed = 1;
const seed = (h) => { _seed = h | 0; };
function rnd() {
  _seed = (_seed + 0x6D2B79F5) | 0;
  let t = Math.imul(_seed ^ (_seed >>> 15), 1 | _seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}
const rr = (a, b) => a + (b - a) * rnd();
/** Smooth value noise over the plane, 0..1. */
function vnoise(x, z, salt) {
  const ix = Math.floor(x), iz = Math.floor(z);
  let tx = x - ix, tz = z - iz;
  tx = tx * tx * (3 - 2 * tx); tz = tz * tz * (3 - 2 * tz);
  const a = hash2(ix, iz, salt), b = hash2(ix + 1, iz, salt), c = hash2(ix, iz + 1, salt), d = hash2(ix + 1, iz + 1, salt);
  return ((a + (b - a) * tx) * (1 - tz) + (c + (d - c) * tx) * tz) / 4294967296;
}

// ------------------------------------------------------------------------------------ buffers
/** One growing-and-shrinking mesh: vertex blocks handed out to chunks, the index list rebuilt from the chunks in view. */
class Pool {
  constructor(layout, maxVerts, maxIndex, block = 128) {
    this.block = block;
    this.nBlocks = Math.floor(maxVerts / block);
    this.maxVerts = this.nBlocks * block;
    this.used = new Uint8Array(this.nBlocks);
    this.cursor = 0;
    this.geo = new THREE.BufferGeometry();
    this.attrs = [];
    for (const [name, Ctor, size, norm] of layout) {
      const a = new THREE.BufferAttribute(new Ctor(this.maxVerts * size), size, !!norm);
      a.setUsage(THREE.DynamicDrawUsage);
      this.geo.setAttribute(name, a);
      this.attrs.push(a);
      this[name] = a.array;
    }
    this.index = new THREE.BufferAttribute(new Uint32Array(maxIndex), 1);
    this.index.setUsage(THREE.DynamicDrawUsage);
    this.geo.setIndex(this.index);
    this.geo.setDrawRange(0, 0);
    this.chunks = new Set();
    this.dirty = false;
    this.vertsLive = 0;
    this.tris = 0;
  }
  alloc(nv) {
    const k = Math.ceil(nv / this.block), n = this.nBlocks, used = this.used;
    if (k > n) return -1;
    let run = 0, b = this.cursor >= n ? 0 : this.cursor, seen = 0;
    while (seen < n + k) {
      if (b >= n) { b = 0; run = 0; }
      if (used[b]) run = 0; else if (++run === k) {
        const b0 = b - k + 1;
        used.fill(1, b0, b + 1);
        this.cursor = b + 1;
        this.vertsLive += k * this.block;
        return b0 * this.block;
      }
      b++; seen++;
    }
    return -1;
  }
  free(v0, nv) {
    const k = Math.ceil(nv / this.block), b0 = v0 / this.block;
    this.used.fill(0, b0, b0 + k);
    this.vertsLive -= k * this.block;
  }
  touch(v0, nv) {
    for (const a of this.attrs) { a.addUpdateRange(v0 * a.itemSize, nv * a.itemSize); a.needsUpdate = true; }
  }
  rebuild() {
    const arr = this.index.array;
    let o = 0;
    for (const c of this.chunks) {
      if (!c.vis || o + c.idx.length > arr.length) continue;
      arr.set(c.idx, o);
      o += c.idx.length;
    }
    if (o > 0) { this.index.addUpdateRange(0, o); this.index.needsUpdate = true; }
    this.geo.setDrawRange(0, o);
    this.tris = o / 3;
    this.dirty = false;
  }
}

// ------------------------------------------------------------------------------------ the kit
async function loadKit(base) {
  const [dir, bin] = await Promise.all([
    fetch(`${base}/shore/shore.json`).then((r) => { if (!r.ok) throw new Error(`shore.json: ${r.status}`); return r.json(); }),
    fetch(`${base}/shore/shore.bin`).then((r) => { if (!r.ok) throw new Error(`shore.bin: ${r.status}`); return r.arrayBuffer(); }),
  ]);
  const sec = (name, Ctor) => { const [o, n] = dir.sections[name]; return new Ctor(bin, o, n / Ctor.BYTES_PER_ELEMENT); };
  const S = { pos: sec('static.pos', Float32Array), nrm: sec('static.nrm', Int8Array), col: sec('static.col', Uint8Array), aux: sec('static.aux', Uint8Array), idx: sec('static.idx', Uint16Array) };
  const C = { pos: sec('crab.pos', Float32Array), piv: sec('crab.piv', Float32Array), nrm: sec('crab.nrm', Int8Array), col: sec('crab.col', Uint8Array), aux: sec('crab.aux', Uint8Array), idx: sec('crab.idx', Uint16Array) };
  const meshes = {}, list = [];
  for (const [name, m] of Object.entries(dir.meshes)) {
    const src = m.set === 'crab' ? C : S;
    const rec = {
      name, id: list.length, nv: m.nv, ni: m.ni, radius: m.radius, height: m.height, low: m.low,
      pos: src.pos.subarray(m.v0 * 3, (m.v0 + m.nv) * 3), nrm: src.nrm.subarray(m.v0 * 4, (m.v0 + m.nv) * 4),
      col: src.col.subarray(m.v0 * 4, (m.v0 + m.nv) * 4), aux: src.aux.subarray(m.v0 * 4, (m.v0 + m.nv) * 4),
      idx: src.idx.subarray(m.i0, m.i0 + m.ni),
      piv: m.set === 'crab' ? src.piv.subarray(m.v0 * 3, (m.v0 + m.nv) * 3) : null,
      anchors: m.anchors || null,
    };
    meshes[name] = rec;
    list.push(rec);
  }
  return { meshes, list };
}

// ------------------------------------------------------------------------------------ Shore
export class Shore {
  static async load(renderer, terrain, base = './assets') {
    const kit = await loadKit(base);
    return new Shore(renderer, terrain, kit);
  }

  constructor(renderer, terrain, kit) {
    this.renderer = renderer;
    this.terrain = terrain;
    this.kit = kit;
    this.group = new THREE.Group();
    this.group.matrixAutoUpdate = false;
    this.camera = null;
    this.fx = null;
    this.town = null;
    this.stats = { cells: 0, tris: 0, decalTris: 0, verts: 0, crabs: 0, crabsDrawn: 0, crabTris: 0, ms: 0, work: 0 };
    this.frame = 0;
    this.time = 0;
    this.enabled = true;

    this._buildMasks();
    this.discs = ((terrain.meta && terrain.meta.towns) || []).filter((t) => t.r <= TOWN_MAX_R && terrain.heightAt(t.x, t.z) < TOWN_SHORE_MAX_Y).map((t) => [t.x, t.z, t.r]);
    this._cling = false;
    const nt = U.uNoiseTex.value;
    this.noise = nt && nt.image && nt.image.data && nt.image.width === 256 ? nt.image.data : null;
    this.waveA = WAVES.map((w) => new THREE.Vector4(w.dx, w.dz, w.k, w.amp));
    this.waveB = WAVES.map((w) => new THREE.Vector4(w.w, w.steep, w.ph, 0));
    const T = terrain.material.uniforms;
    this.uLod = { uLodAlt: T.uLodAlt, uLodRange: T.uLodRange };

    // ---- pools
    this.pool = new Pool([['position', Float32Array, 3], ['aOff', Int16Array, 4, true], ['aNrm', Int8Array, 4, true], ['aCol', Uint8Array, 4, true], ['aAux', Uint8Array, 4]], 120000, 480000);
    this.decals = new Pool([['position', Float32Array, 3], ['aDecal', Float32Array, 4], ['aMisc', Uint8Array, 4, true]], 40000, 160000);

    const common = shared(...SKY_UNIFORMS, 'uTime', 'uLightTex', 'uHeightTex', 'uSplatTex', 'uWorld', 'uNoiseTex', 'uShadowTex', 'uShadowMat', 'uShadowOn');
    const waves = { uWaveA: { value: this.waveA }, uWaveB: { value: this.waveB }, uSea: SEA_STATE };
    this.matDress = new THREE.ShaderMaterial({
      uniforms: { ...common, ...waves, uSand: { value: new THREE.Vector3(0.66, 0.50, 0.295) }, uMatC: T.uMatC },
      vertexShader: DRESS_VERT, fragmentShader: DRESS_FRAG, side: THREE.DoubleSide,
    });
    const towns = [0, 1, 2].map((i) => (this.discs[i] ? new THREE.Vector3(...this.discs[i]) : new THREE.Vector3(0, 0, -1e4)));
    this.matDecal = new THREE.ShaderMaterial({
      uniforms: { ...common, ...this.uLod, uTowns: { value: towns } },
      vertexShader: DECAL_VERT, fragmentShader: DECAL_FRAG,
      transparent: true, depthWrite: false,
      blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
      blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor,
    });
    this.meshDress = new THREE.Mesh(this.pool.geo, this.matDress);
    this.meshDecal = new THREE.Mesh(this.decals.geo, this.matDecal);
    this.meshDress.renderOrder = 290;          // before the terrain (which is drawn last, behind everything)
    this.meshDecal.renderOrder = 20;           // first of the see-through things
    for (const m of [this.meshDress, this.meshDecal]) { m.frustumCulled = false; m.matrixAutoUpdate = false; m.visible = false; this.group.add(m); }

    this._initCrabs();

    // ---- streaming state
    this.cells = new Map();
    this._todo = [];
    this._last = new THREE.Vector3(1e9, 0, 0);
    this._fr = new THREE.Frustum();
    this._m4 = new THREE.Matrix4();
    this._box = new THREE.Box3();
    this._v = new THREE.Vector3();
    this._n = new THREE.Vector3();
    this._items = new Float32Array(22 * 1024);
    this._grid = new Int32Array(17 * 17);
    this._cullAt = 0;
  }

  /**
   * Optional hook-ups: the camera to stream around, the particle director (sand puffs), the water
   * (its wave table), the towns (nothing is put where something is built, and crabs keep clear),
   * and the frame's sharp layer: given that, the crabs are drawn there with the rider and the
   * petals, after the motion blur - small scurrying things smear to nothing in a blurred world.
   */
  attach({ camera, fx, water, town, overlay } = {}) {
    if (camera) this.camera = camera;
    if (fx) this.fx = fx;
    if (town && town.heightAt) this.town = town;
    if (overlay && overlay.add) overlay.add(this.crabNear.mesh, this.crabFar.mesh);
    const u = water && water.material && water.material.uniforms;
    if (u && u.uWaveA && u.uWaveB) {
      const m = this.matDress.uniforms;
      m.uWaveA = u.uWaveA; m.uWaveB = u.uWaveB;
      if (u.uSea) m.uSea = u.uSea;
    }
    return this;
  }

  // ---------------------------------------------------------------------------------- terrain queries
  _buildMasks() {
    const T = this.terrain, L = T.mm[0];
    this.gridN = L.n;
    // cells the shore band passes through (kelp reaches a little deeper, lichen a little higher)
    const mask = (this.mask = new Uint8Array(L.n * L.n));
    for (let i = 0; i < mask.length; i++) mask[i] = L.mn[i] < 4.6 && L.mx[i] > -3.4 ? 1 : 0;
    // (a quay wall is not terrain: the ground under it may be all sea bed, so mark its cells by hand)
    for (const q of QUAYS) {
      const cz = Math.floor((q.z + World.half) / CELL);
      for (let cx = Math.floor((q.x0 + World.half) / CELL); cx <= Math.floor((q.x1 + World.half) / CELL); cx++) if (cx >= 0 && cx < L.n && cz >= 0 && cz < L.n) mask[cz * L.n + cx] = 1;
    }
    // cliffness (light map alpha), a quarter of the island's resolution is plenty
    const S = (this.cliffN = 1024);
    const cliff = (this.cliff = new Uint8Array(S * S));
    try {
      const img = T.lightTex.image;
      const c = document.createElement('canvas');
      c.width = c.height = S;
      const g = c.getContext('2d', { willReadFrequently: true });
      g.globalCompositeOperation = 'copy';
      g.drawImage(img, 0, 0, S, S);
      const px = g.getImageData(0, 0, S, S).data;
      for (let i = 0; i < S * S; i++) cliff[i] = px[i * 4 + 3];
    } catch (e) {
      // no pixels to be had: call the north of the island rock and the south sand
      for (let z = 0; z < S; z++) cliff.fill(z < S * 0.6 ? 255 : 0, z * S, (z + 1) * S);
    }
  }
  /** The shaders' ntex(), on the CPU: channel ch of the tileable noise at p (bilinear, as the GPU magnifies it). */
  _ntex(px, pz, ch) {
    const d = this.noise;
    if (!d) return 0.5;
    let x = (px - 0.5) % 256, z = (pz - 0.5) % 256;
    if (x < 0) x += 256; if (z < 0) z += 256;
    const ix = x | 0, iz = z | 0, tx = x - ix, tz = z - iz, ix1 = (ix + 1) & 255, iz1 = (iz + 1) & 255;
    const a = d[(iz * 256 + ix) * 4 + ch], b = d[(iz * 256 + ix1) * 4 + ch], c = d[(iz1 * 256 + ix) * 4 + ch], e = d[(iz1 * 256 + ix1) * 4 + ch];
    return ((a + (b - a) * tx) * (1 - tz) + (c + (e - c) * tx) * tz) / 255;
  }
  /** Height of the strand line on the sand at a spot, and how much weed that stretch holds (0..1). Mirrors the tide-line shader. */
  strand(x, z, out) {
    out[0] = 1.14 + (this._ntex(x * 1.3 + 9, z * 1.3 + 9, 0) - 0.5) * 0.40 + (this._ntex(x * 6.0, z * 6.0, 1) - 0.5) * 0.07;
    out[1] = sstep(0.30, 0.52, this._ntex(x * 0.9 + 3, z * 0.9 + 3, 3));
    return out;
  }
  /** Inside a town's circle (or within `margin` of it)? */
  inTown(x, z, margin = 0) {
    for (const d of this.discs) { const r = d[2] + margin, dx = x - d[0], dz = z - d[1]; if (dx * dx + dz * dz < r * r) return true; }
    return false;
  }
  /** Does something built stand at (x, z), or within `margin` metres of it? (a quay, a pier, a house) */
  solid(x, z, margin = 0) {
    const t = this.town;
    if (!t) return false;
    if (t.heightAt(x, z) > -1e8) return true;
    if (margin > 0) for (let i = 0; i < 8; i++) { const a = i * 0.7854; if (t.heightAt(x + Math.cos(a) * margin, z + Math.sin(a) * margin) > -1e8) return true; }
    return false;
  }
  /** Made ground: in a town, or built on. Crabs and loose things keep off it. */
  built(x, z, margin = 0) { return this.inTown(x, z, margin) || this.solid(x, z, margin); }
  /** 0 on the sandy south shore .. 1 on the cliff coasts. */
  cliffAt(x, z) {
    const S = this.cliffN;
    let fx = (x + World.half) / World.size * S - 0.5, fz = (z + World.half) / World.size * S - 0.5;
    fx = clamp(fx, 0, S - 1.001); fz = clamp(fz, 0, S - 1.001);
    const ix = fx | 0, iz = fz | 0, tx = fx - ix, tz = fz - iz, c = this.cliff, i = iz * S + ix;
    return ((c[i] + (c[i + 1] - c[i]) * tx) * (1 - tz) + (c[i + S] + (c[i + S + 1] - c[i + S]) * tx) * tz) / 255;
  }
  /**
   * Height of the terrain's finest mesh at a point: the very triangle that is drawn there (the
   * grid's diagonals alternate), not the bilinear patch. Small things must sit on this.
   * With `out`, also the triangle's normal.
   */
  surf(x, z, out) {
    const T = this.terrain, N = T.N;
    let fx = (x + World.half) / T.cell - 0.5, fz = (z + World.half) / T.cell - 0.5;
    if (fx < 0) fx = 0; else if (fx > N - 1.001) fx = N - 1.001;
    if (fz < 0) fz = 0; else if (fz > N - 1.001) fz = N - 1.001;
    const ix = fx | 0, iz = fz | 0, tx = fx - ix, tz = fz - iz;
    const h = T.h, i = iz * N + ix;
    const a = h[i], b = h[i + 1], c = h[i + N], d = h[i + N + 1];
    let gx, gz, y;
    if ((ix + iz) & 1) {
      if (tx + tz <= 1) { gx = b - a; gz = c - a; y = a + gx * tx + gz * tz; }
      else { gx = d - c; gz = d - b; y = d - gx * (1 - tx) - gz * (1 - tz); }
    } else if (tx >= tz) { gx = b - a; gz = d - b; y = a + gx * tx + gz * tz; }
    else { gx = d - c; gz = c - a; y = a + gx * tx + gz * tz; }
    if (out) {
      const k = 1 / T.cell, nx = -gx * k, nz = -gz * k, l = 1 / Math.sqrt(nx * nx + 1 + nz * nz);
      out.set(nx * l, l, nz * l);
    }
    return y;
  }

  // ---------------------------------------------------------------------------------- placement
  /** Append an item to the scratch list. e = its x axis (unit, perpendicular to n). */
  _put(mesh, far, x, y, z, n, e, sx, sy, sz, tr, tg, tb, tier, phase, shR = 0, shH = 0) {
    // made ground takes nothing - except, in a town, what clings to wet rock (this._cling)
    if (this._cling === 2 ? false : this._cling ? this.solid(x, z, 0.4) : this.built(x, z)) return -1;
    let a = this._items;
    if ((this._ni + 1) * 22 > a.length) { const b = new Float32Array(a.length * 2); b.set(a); a = this._items = b; }
    const o = this._ni++ * 22;
    a[o] = x; a[o + 1] = y; a[o + 2] = z; a[o + 3] = n.x; a[o + 4] = n.y; a[o + 5] = n.z; a[o + 6] = e.x; a[o + 7] = e.y; a[o + 8] = e.z;
    a[o + 9] = sx; a[o + 10] = sy; a[o + 11] = sz; a[o + 12] = mesh.id; a[o + 13] = far ? far.id : -1;
    a[o + 14] = tr; a[o + 15] = tg; a[o + 16] = tb; a[o + 17] = tier; a[o + 18] = phase; a[o + 19] = shR; a[o + 20] = shH; a[o + 21] = 0;
    return o;
  }

  /** Everything that lives in one cell: dressing items and crab homes. Deterministic. */
  _generate(cell) {
    const K = this.kit.meshes, self = this;
    const x0 = cell.cx * CELL - World.half, z0 = cell.cz * CELL - World.half;
    this._ni = 0;
    const crabs = [], burrows = [];
    const n = new THREE.Vector3(), e = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0), t0 = new THREE.Vector3(), t1 = new THREE.Vector3(), an = new THREE.Vector3(), ae = new THREE.Vector3(), ez = new THREE.Vector3();
    let small = 0;
    // an x axis for a thing standing on normal n, turned by yaw
    const axis = (nn, yaw, out) => {
      if (Math.abs(nn.x) < 0.9) t0.set(1, 0, 0); else t0.set(0, 0, 1);
      t0.addScaledVector(nn, -t0.dot(nn)).normalize();
      t1.crossVectors(t0, nn);
      return out.copy(t0).multiplyScalar(Math.cos(yaw)).addScaledVector(t1, Math.sin(yaw));
    };
    // an x axis that leaves the thing's z axis pointing down the slope
    const axisDown = (nn, out) => {
      t0.set(nn.x * nn.y, nn.y * nn.y - 1, nn.z * nn.y);
      if (t0.lengthSq() < 1e-5) return axis(nn, rnd() * 6.283, out);
      t0.normalize();
      return out.crossVectors(nn, t0).normalize();
    };
    const lattice = (s, salt, fn) => {
      const gx0 = Math.ceil(x0 / s), gx1 = Math.ceil((x0 + CELL) / s), gz0 = Math.ceil(z0 / s), gz1 = Math.ceil((z0 + CELL) / s);
      for (let gz = gz0; gz < gz1; gz++) for (let gx = gx0; gx < gx1; gx++) {
        seed(hash2(gx, gz, salt));
        fn((gx + rnd()) * s, (gz + rnd()) * s);
      }
    };
    const STAR = [[1.0, 0.50, 0.16], [0.96, 0.30, 0.22], [0.70, 0.36, 0.78], [1.0, 0.74, 0.30], [1.0, 0.56, 0.64]];
    const SHELL = [[1.0, 0.95, 0.84], [1.0, 0.76, 0.70], [1.0, 0.72, 0.46], [0.86, 0.74, 0.90], [0.98, 0.90, 0.72]];
    // ---- small things that sit flat on a surface
    const flat = (mesh, x, y, z, nn, s, tint, tier = SMALL, sink = 0.004, yaw = rnd() * 6.283) => {
      if (tier === SMALL && ++small > 300 * DENSITY) return;
      axis(nn, yaw, e);
      const t = tint || [1, 1, 1], v = rr(0.86, 1.1);
      self._put(mesh, null, x - nn.x * sink, y - nn.y * sink, z - nn.z * sink, nn, e, s, s, s, t[0] * v, t[1] * v, t[2] * v, tier, rnd());
    };
    const weed = (x, y, z, nn, s, tier = MID) => {
      const steep = nn.y < 0.72;
      if (steep) axisDown(nn, e); else axis(nn, rnd() * 6.283, e);
      const g = rnd();
      // mostly olive rockweed; now and then a tuft of bright sea lettuce or dark red dulse
      const t = g < 0.68 ? [1, 1, 1] : g < 0.86 ? [0.55, 1.12, 0.55] : [1.05, 0.50, 0.42];
      const v = rr(0.8, 1.1);
      self._put(steep ? K.rockweed_b : K.rockweed_a, null, x, y, z, nn, e, s, s, s, t[0] * v, t[1] * v, t[2] * v, tier, rnd());
    };
    // ---- what grows on a patch of wet rock, by height above the sea
    const grow = (x, y, z, nn, bare, plain = false) => {
      let q = rnd();
      if (plain && y < 0.5) q *= 0.48;                             // (a harbour wall: weed and mussels, no starfish or urchins)
      if (y < 0.5) {
        if (q < 0.26) weed(x, y, z, nn, rr(0.6, 1.15));
        else if (q < 0.48) flat(rnd() < 0.5 ? K.mussels_a : K.mussels_b, x, y, z, nn, rr(0.8, 1.35));
        else if (q < 0.60) flat(K.anemones, x, y, z, nn, rr(0.8, 1.3), [0.82, 0.8, 0.8]);
        else if (q < 0.66) flat(K.anemone_open, x, y, z, nn, rr(0.6, 0.95), rnd() < 0.5 ? [1, 1, 1] : [0.6, 1.1, 0.75]);
        else if (q < 0.78 && nn.y > 0.5) flat(rnd() < 0.5 ? K.starfish_a : K.starfish_b, x, y, z, nn, rr(0.13, 0.20), STAR[(rnd() * STAR.length) | 0]);
        else if (q < 0.86 && nn.y > 0.6) flat(K.urchin, x, y, z, nn, rr(0.045, 0.065), rnd() < 0.7 ? [1, 1, 1] : [1.5, 0.5, 0.6]);
        else if (!bare) flat(K.barnacles_b, x, y, z, nn, rr(0.8, 1.3));
      } else if (y < 1.6) {
        if (q < 0.42) flat(q < 0.16 ? K.barnacles_a : q < 0.30 ? K.barnacles_b : K.barnacles_c, x, y, z, nn, rr(0.75, 1.4));
        else if (q < 0.62) flat(K.limpets, x, y, z, nn, rr(0.8, 1.5));
        else if (q < 0.74 && y < 0.9) flat(K.mussels_b, x, y, z, nn, rr(0.8, 1.2));
        else if (q < 0.80 && y < 0.8) weed(x, y, z, nn, rr(0.55, 0.9));
      } else if (q < 0.30) flat(q < 0.18 ? K.limpets : K.barnacles_c, x, y, z, nn, rr(0.7, 1.2));
    };
    const ROCKS = [[K.rock_a, K.rock_a_far], [K.rock_b, K.rock_b_far], [K.rock_c, K.rock_c_far], [K.rock_d, K.rock_d_far]];
    const rock = (x, z, R, cl) => {
      const h = self.surf(x, z, n);
      if (h < -1.4 || h > 3.4) return;
      const v = cl > 0.4 ? (rnd() < 0.42 ? 0 : rnd() < 0.5 ? 1 : rnd() < 0.55 ? 3 : 2) : (rnd() < 0.6 ? 0 : 1);
      const [m, mf] = ROCKS[v];
      let sy = R * rr(0.78, 1.08);
      // nothing stands taller than a skimming broom clears
      const top = h < 0 ? 0.9 - h : 0.95;
      if (m.height * sy > top) sy = top / m.height;
      if (h + m.height * sy < 0.22) return;                       // drowned: nobody would see it
      an.copy(up).lerp(n, 0.45).normalize();
      axis(an, rnd() * 6.283, e);
      const sx = R * rr(0.86, 1.14), sz = R * rr(0.86, 1.14);
      // slate and sandstone under the cliffs; paler, sun-warmed stone on the sand
      const warm = vnoise(x / 9, z / 9, 77), b = rr(0.80, 1.12) * (cl < 0.3 ? 1.22 : 1);
      const tr = lerp(0.88, 1.06, warm) * b, tg = lerp(0.91, 0.99, warm) * b, tb = lerp(1.0, 0.88, warm) * b;
      const tier = R > 0.62 ? BIG : R > 0.3 ? MID : SMALL;
      if (tier === SMALL && ++small > 300 * DENSITY) return;
      const py = h - 0.05 * R;
      // (small stones get the plain mesh at any distance; big ones the full mesh only close by)
      self._put(R > 0.5 ? m : mf, R > 0.5 ? mf : null, x, py, z, an, e, sx, sy, sz, tr, tg, tb, tier, rnd(), R > 0.26 ? m.radius * R * 0.92 : 0, m.height * sy * 0.8);
      // ---- who lives under it: a crab or two, with a bolt-hole just inside its skirt
      if (R > 0.45 && cl > 0.4 && h > 0.12 && h < 2.2 && rnd() < 0.62 && !self.built(x, z, 6)) {
        for (let i = 1 + ((rnd() * 2.3) | 0); i > 0; i--) {
          const a = rnd() * 6.283, d = m.radius * R * 0.55;
          crabs.push(x + Math.cos(a) * d, z + Math.sin(a) * d, 1, rr(0.25, 0.37), rnd());
        }
      }
      // ---- what has settled on it
      if (R < 0.28 || !m.anchors) return;
      ez.crossVectors(e, an);
      ae.copy(e);
      const A = m.anchors, want = Math.min(A.length, Math.round(4 + R * 9));
      const start = (rnd() * A.length) | 0;
      for (let k = 0; k < want; k++) {
        const a = A[(start + k) % A.length];
        const wx = x + ae.x * a[0] * sx + an.x * a[1] * sy + ez.x * a[2] * sz;
        const wy = py + ae.y * a[0] * sx + an.y * a[1] * sy + ez.y * a[2] * sz;
        const wz = z + ae.z * a[0] * sx + an.z * a[1] * sy + ez.z * a[2] * sz;
        if (wy < -0.25 || wy > 2.3 || wy < self.surf(wx, wz) + 0.05) continue;
        n.set(ae.x * a[3] / sx + an.x * a[4] / sy + ez.x * a[5] / sz, ae.y * a[3] / sx + an.y * a[4] / sy + ez.y * a[5] / sz, ae.z * a[3] / sx + an.z * a[4] / sy + ez.z * a[5] / sz).normalize();
        if (rnd() < 0.42) grow(wx, wy, wz, n, false);
      }
    };

    // ============ rock coasts
    // boulders: singly and in falls, thickest at the water's edge
    lattice(6.5, 11, (x, z) => {
      const h = self.terrain.heightAt(x, z);
      if (h < -1.2 || h > 3.0) return;
      const cl = self.cliffAt(x, z);
      if (cl > 0.4) {
        const fall = sstep(0.38, 0.72, vnoise(x / 34, z / 34, 5));
        const band = sstep(-1.2, -0.3, h) * (1 - 0.6 * sstep(1.2, 3.0, h));
        if (rnd() > (0.34 + 0.6 * fall) * band * DENSITY) return;
        const R = 0.4 + 1.25 * Math.pow(rnd(), 2.2) * (0.55 + 0.6 * fall);
        rock(x, z, R, cl);
        const litter = 2 + ((rnd() * (3 + 4 * fall)) | 0);
        for (let i = 0; i < litter; i++) {
          const a = rnd() * 6.283, d = R * rr(0.9, 2.6);
          rock(x + Math.cos(a) * d, z + Math.sin(a) * d, R * rr(0.16, 0.5), cl);
        }
      } else if (cl < 0.3 && h > 0.25 && h < 2.5) {
        // a rare stone on the sand, with a couple of smaller ones beside it
        if (rnd() > 0.035 * DENSITY) return;
        const R = rr(0.3, 0.8);
        rock(x, z, R, cl);
        for (let i = (rnd() * 3) | 0; i > 0; i--) { const a = rnd() * 6.283, d = R * rr(1.0, 2.4); rock(x + Math.cos(a) * d, z + Math.sin(a) * d, R * rr(0.2, 0.45), cl); }
      }
    });
    // what clings to the rock itself, and lies among the cobbles
    lattice(1.0, 13, (x, z) => {
      const h = self.surf(x, z, n);
      if (h < -0.28 || h > 2.4) return;
      const cl = self.cliffAt(x, z);
      if (cl < 0.42) return;
      const steep = 1 - n.y;
      if (self.inTown(x, z)) {
        // a harbour: only what grows at the waterline, on its rock and on the rubble of its moles
        if (h > (steep > 0.24 ? 1.7 : 0.85)) return;
        self._cling = true;
        if (rnd() < (steep > 0.24 ? 0.55 : 0.36) * DENSITY) grow(x, h, z, n, true, true);
        self._cling = false;
      } else if (steep > 0.24) {
        if (rnd() < 0.42 * DENSITY) grow(x, h, z, n, false);
      } else {
        const p = h < 0.55 ? 0.24 : h < 1.4 ? 0.10 : 0.05;
        if (rnd() > p * DENSITY) return;
        const q = rnd();
        if (q < 0.20) flat(rnd() < 0.6 ? K.cobbles_a : K.cobbles_b, x, h, z, n, rr(0.8, 1.5), [rr(0.78, 1.0), rr(0.80, 1.0), rr(0.84, 1.02)], SMALL, 0.02);
        else if (q < 0.84) grow(x, h, z, n, true);
        else if (q < 0.89) flat(K.whelk, x, h, z, n, rr(0.10, 0.16), SHELL[(rnd() * SHELL.length) | 0]);
        else flat(K.limpets, x, h, z, n, rr(0.8, 1.3));
      }
    });
    // kelp afloat off the rocks, streaming along the shore
    lattice(4.6, 15, (x, z) => {
      const h = self.terrain.heightAt(x, z);
      if (h > -0.45 || h < -3.3) return;
      if (self.cliffAt(x, z) < 0.42) return;
      const bed = sstep(0.40, 0.66, vnoise(x / 26, z / 26, 9));
      if (rnd() > (0.10 + 0.62 * bed) * DENSITY) return;
      self.terrain.normalAt(x, z, n, 3);
      // along the shore, on the side the swell runs to
      let tx = -n.z, tz = n.x;
      const l = Math.hypot(tx, tz);
      if (l < 0.02) { tx = WAVES[0].dx; tz = WAVES[0].dz; } else { tx /= l; tz /= l; }
      if (tx * WAVES[0].dx + tz * WAVES[0].dz < 0) { tx = -tx; tz = -tz; }
      const a = Math.atan2(tz, tx) + rr(-0.6, 0.6);
      e.set(Math.cos(a), 0, Math.sin(a));
      const s = rr(0.75, 1.35), b = rr(0.85, 1.1);
      const v = rnd() < 0.6;
      self._put(v ? K.kelp_a : K.kelp_b, v ? K.kelp_a_far : K.kelp_b_far, x, 0, z, up, e, s, 1, s, b, b * rr(0.9, 1.05), b * 0.9, BIG, rnd());
    });

    // ============ sand
    const sl = [0, 0];
    lattice(1.0, 16, (x, z) => {
      const h = self.surf(x, z, n);
      if (h < 0.2 || h > 2.7) return;
      if (self.cliffAt(x, z) > 0.3) return;
      self.strand(x, z, sl);
      const d = h - sl[0];
      if (Math.abs(d) < 0.045) {
        // the strand line: weed, sticks and shells left by the last high tide
        if (rnd() > (0.05 + 0.24 * sl[1]) * DENSITY) return;
        const q = rnd();
        if (q < 0.56) flat(rnd() < 0.6 ? K.wrack_a : K.wrack_b, x, h, z, n, rr(0.7, 1.4), null, MID, 0.0);
        else if (q < 0.70) flat(K.stick, x, h, z, n, rr(0.7, 1.6), null, SMALL, 0.0);
        else if (q < 0.90) flat(q < 0.77 ? K.scallop : q < 0.84 ? K.cockle : K.whelk, x, h, z, n, q < 0.84 ? rr(0.055, 0.10) : rr(0.10, 0.16), SHELL[(rnd() * SHELL.length) | 0]);
        else if (q < 0.95) flat(K.cobbles_a, x, h, z, n, rr(0.6, 1.1), null, SMALL, 0.01);
        else flat(K.branch, x, h, z, n, rr(0.7, 1.2), null, MID, 0.0);
      } else if (Math.abs(d - 0.72) < 0.05) {
        // an older, higher line: sparse and bleached
        if (rnd() > 0.07 * DENSITY) return;
        const q = rnd();
        if (q < 0.5) flat(K.wrack_a, x, h, z, n, rr(0.6, 1.0), [1.4, 1.35, 1.25], MID, 0.0);
        else if (q < 0.8) flat(K.stick, x, h, z, n, rr(0.8, 1.6), null, SMALL, 0.0);
        else flat(K.branch, x, h, z, n, rr(0.8, 1.3), null, MID, 0.0);
      }
    });
    // shells, and the odd starfish at the water's edge
    lattice(2.6, 17, (x, z) => {
      const h = self.surf(x, z, n);
      if (h < 0.24 || h > 2.4 || self.cliffAt(x, z) > 0.3) return;
      const p = 0.05 + 0.18 * sstep(0.9, 0.3, h);
      if (rnd() > p * DENSITY) return;
      const q = rnd();
      if (q < 0.14 && h < 0.75) flat(rnd() < 0.5 ? K.starfish_a : K.starfish_b, x, h, z, n, rr(0.13, 0.19), STAR[(rnd() * STAR.length) | 0]);
      else flat(q < 0.5 ? K.scallop : q < 0.8 ? K.cockle : K.whelk, x, h, z, n, q < 0.8 ? rr(0.055, 0.10) : rr(0.10, 0.16), SHELL[(rnd() * SHELL.length) | 0]);
    });
    // driftwood, thrown up above the strand line
    lattice(15, 18, (x, z) => {
      const h = self.surf(x, z, n);
      if (h < 1.45 || h > 2.75 || self.cliffAt(x, z) > 0.3) return;
      if (rnd() > 0.26 * DENSITY) return;
      if (self.built(x, z, 12)) return;                           // the harbour keeps its strand clear
      self.terrain.normalAt(x, z, an, 4);
      const a = Math.atan2(an.x, -an.z) + rr(-0.6, 0.6);           // roughly along the beach
      e.set(Math.cos(a), 0, Math.sin(a)).addScaledVector(n, -(Math.cos(a) * n.x + Math.sin(a) * n.z)).normalize();
      const v = rnd() < 0.55, s = rr(0.75, 1.25), b = rr(0.9, 1.08);
      const m = v ? K.log_a : K.log_b;
      const o = self._put(m, v ? K.log_a_far : K.log_b_far, x, h - 0.02, z, n, e, s, s, s, b, b, b, BIG, rnd(), -m.radius * s, 0.2 * s);
      if (o >= 0) self._items[o + 21] = 1;                         // a long thing: its shade is a strip, not a blob
    });
    // crab towns: a scatter of burrows, each one somebody's home. Few and populous, so that a
    // whole colony bolts at once when the broom comes over.
    lattice(21, 19, (x, z) => {
      const h = self.terrain.heightAt(x, z);
      if (h < 0.85 || h > 2.3 || self.cliffAt(x, z) > 0.25) return;
      if (self.built(x, z, 10)) return;
      if (rnd() > 0.50 + 0.4 * sstep(0.35, 0.65, vnoise(x / 47, z / 47, 6))) return;
      const count = 8 + ((rnd() * 12) | 0), R = rr(3.4, 6.4);
      const pts = [];
      for (let i = 0; i < count; i++) {
        let bx = 0, bz = 0, ok = false;
        for (let t = 0; t < 8 && !ok; t++) {
          const a = rnd() * 6.283, d = R * Math.sqrt(rnd());
          bx = x + Math.cos(a) * d; bz = z + Math.sin(a) * d;
          ok = pts.every((p) => (p[0] - bx) ** 2 + (p[1] - bz) ** 2 > 1.5);
        }
        if (!ok) continue;
        const bh = self.surf(bx, bz, n);
        if (bh < 0.7 || bh > 2.6 || self.built(bx, bz, 4)) continue;
        pts.push([bx, bz]);
        const size = rr(0.30, 0.44);
        burrows.push(bx, bz, size * 1.3, rnd() * 6.283);            // x, z, reach of the spoil, which way it was thrown
        crabs.push(bx, bz, 0, size, rnd());
      }
    });
    // crabs out among the cobbles, with nowhere to hide but the sea
    lattice(5.6, 21, (x, z) => {
      const h = self.surf(x, z, n);
      if (h < 0.25 || h > 1.7 || n.y < 0.80 || self.cliffAt(x, z) < 0.45 || self.built(x, z, 6)) return;
      if (rnd() > 0.30) return;
      for (let i = 1 + ((rnd() * 2.4) | 0); i > 0; i--) {
        const bx = x + rr(-1.2, 1.2), bz = z + rr(-1.2, 1.2), bh = self.surf(bx, bz);
        if (bh > 0.2 && bh < 1.9) crabs.push(bx, bz, 2, rr(0.25, 0.37), rnd());
      }
    });

    // ============ a quay wall: weed, mussels and barnacles along its waterline
    for (const q of QUAYS) {
      const town = this.town;
      if (!town || q.z < z0 || q.z >= z0 + CELL || q.x1 < x0 || q.x0 > x0 + CELL) continue;
      this._cling = 2;                                              // (on the built thing itself)
      n.set(0, q.batter, 1).normalize();
      const s = 0.8;
      for (let gx = Math.ceil(Math.max(x0, q.x0) / s); gx * s < Math.min(x0 + CELL, q.x1); gx++) {
        seed(hash2(gx, 7, 23));
        const x = (gx + rnd()) * s;
        // only where the wall really stands: its deck behind, open water in front (not a stair, not a jetty)
        if (!(town.heightAt(x, q.z - 1.0) > 2) || town.heightAt(x, q.z + 1.3) > -1e8 || self.terrain.heightAt(x, q.z + 1.3) > -0.5) continue;
        const thick = sstep(0.30, 0.60, vnoise(x / 6.5, 3.3, 8));        // it comes in stretches
        const put = (mesh, y, sc, tier = SMALL) => {
          axisDown(n, e);
          if (tier === SMALL && ++small > 300 * DENSITY) return;
          const v = rr(0.55, 0.70);                                // (the wall stands between it and half the sky)
          self._put(mesh, null, x, y, q.z + q.batter * (q.deck - y) + 0.01, n, e, sc, sc, sc, v, v, v, tier, rnd());
        };
        if (rnd() < 0.18 + 0.5 * thick) put(K.rockweed_b, rr(0.35, 0.9), rr(0.8, 1.3), MID);
        if (rnd() < 0.18 + 0.3 * thick) put(rnd() < 0.5 ? K.mussels_a : K.mussels_b, rr(0.15, 0.7), rr(0.9, 1.4));
        if (rnd() < 0.36) { const k = rnd(); put(k < 0.3 ? K.barnacles_a : k < 0.65 ? K.barnacles_b : K.barnacles_c, rr(0.6, 1.5), rr(0.9, 1.6)); }
        if (rnd() < 0.15) put(K.limpets, rr(0.7, 2.0), rr(0.9, 1.5));
      }
      this._cling = false;
    }

    cell.items = this._items.slice(0, this._ni * 22);
    cell.n = this._ni;
    cell.crabs = crabs;
    cell.burrows = burrows;
    return this._ni * 6 + 400;
  }

  // ---------------------------------------------------------------------------------- baking
  /** Write the cell's dressing for a level of detail into the shared buffer. Returns the new chunk or null. */
  _bake(cell, tier) {
    const items = cell.items, list = this.kit.list, P = this.pool;
    let nv = 0, ni = 0;
    for (let k = 0, o = 0; k < cell.n; k++, o += 22) {
      if (items[o + 17] < tier) continue;
      const m = list[tier >= 1 && items[o + 13] >= 0 ? items[o + 13] : items[o + 12]];
      nv += m.nv; ni += m.ni;
    }
    if (!nv) return { v0: -1, nv: 0, idx: new Uint32Array(0), vis: true, box: new THREE.Box3() };
    const v0 = P.alloc(nv);
    if (v0 < 0) return null;
    const idx = new Uint32Array(ni);
    const pos = P.position, off = P.aOff, nrm = P.aNrm, col = P.aCol, aux = P.aAux;
    const Q = 32767 / OFF_RANGE;
    let v = v0, io = 0, ymin = 1e9, ymax = -1e9, xmin = 1e9, xmax = -1e9, zmin = 1e9, zmax = -1e9;
    for (let k = 0, o = 0; k < cell.n; k++, o += 22) {
      const itier = items[o + 17];
      if (itier < tier) continue;
      const m = list[tier >= 1 && items[o + 13] >= 0 ? items[o + 13] : items[o + 12]];
      const px = items[o], py = items[o + 1], pz = items[o + 2];
      const nx = items[o + 3], ny = items[o + 4], nz = items[o + 5], ex = items[o + 6], ey = items[o + 7], ez = items[o + 8];
      // z axis = x cross y
      const fx = ey * nz - ez * ny, fy = ez * nx - ex * nz, fz = ex * ny - ey * nx;
      const sx = items[o + 9], sy = items[o + 10], sz = items[o + 11];
      const ix = 1 / sx, iy = 1 / sy, iz = 1 / sz;
      const tr = items[o + 14], tg = items[o + 15], tb = items[o + 16];
      const fade = Math.min(255, Math.round(FADE[itier] / 2)), ph = (items[o + 18] * 255) | 0;
      const mp = m.pos, mn = m.nrm, mc = m.col, ma = m.aux, n = m.nv;
      const reach = m.radius * Math.max(sx, sz);
      if (px - reach < xmin) xmin = px - reach; if (px + reach > xmax) xmax = px + reach;
      if (pz - reach < zmin) zmin = pz - reach; if (pz + reach > zmax) zmax = pz + reach;
      if (py + m.low * sy < ymin) ymin = py + m.low * sy; if (py + m.height * sy > ymax) ymax = py + m.height * sy;
      for (let j = 0; j < n; j++, v++) {
        const j3 = j * 3, j4 = j * 4, v3 = v * 3, v4 = v * 4;
        const lx = mp[j3] * sx, ly = mp[j3 + 1] * sy, lz = mp[j3 + 2] * sz;
        pos[v3] = px; pos[v3 + 1] = py; pos[v3 + 2] = pz;
        off[v4] = (ex * lx + nx * ly + fx * lz) * Q;
        off[v4 + 1] = (ey * lx + ny * ly + fy * lz) * Q;
        off[v4 + 2] = (ez * lx + nz * ly + fz * lz) * Q;
        off[v4 + 3] = ma[j4 + 1] * 128.5;                         // how far along its frond
        const ax = mn[j4] * ix, ay = mn[j4 + 1] * iy, az = mn[j4 + 2] * iz;
        let wx = ex * ax + nx * ay + fx * az, wy = ey * ax + ny * ay + fy * az, wz = ez * ax + nz * ay + fz * az;
        const l = 127 / (Math.sqrt(wx * wx + wy * wy + wz * wz) || 1);
        nrm[v4] = wx * l; nrm[v4 + 1] = wy * l; nrm[v4 + 2] = wz * l; nrm[v4 + 3] = mn[j4 + 3];
        const r = mc[j4] * tr, g = mc[j4 + 1] * tg, b = mc[j4 + 2] * tb;
        col[v4] = r > 255 ? 255 : r; col[v4 + 1] = g > 255 ? 255 : g; col[v4 + 2] = b > 255 ? 255 : b; col[v4 + 3] = mc[j4 + 3];
        aux[v4] = ma[j4]; aux[v4 + 1] = fade; aux[v4 + 2] = (ph + ma[j4 + 2]) & 255; aux[v4 + 3] = 0;
      }
      const base = v - n, mi = m.idx, c = m.ni;
      for (let j = 0; j < c; j++) idx[io++] = base + mi[j];
    }
    P.touch(v0, nv);
    const box = new THREE.Box3(new THREE.Vector3(xmin, Math.min(ymin, -1.5), zmin), new THREE.Vector3(xmax, ymax + 1.5, zmax));
    return { v0, nv, idx, vis: true, box };
  }

  /** The cell's tide lines (the terrain's own triangles, where the tide marks them) and blobs of shade. */
  _bakeDecals(cell) {
    const T = this.terrain, N = T.N, h = T.h, D = this.decals;
    const ix0 = cell.cx * 16, iz0 = cell.cz * 16;
    if (ix0 + 16 >= N || iz0 + 16 >= N) return { v0: -1, nv: 0, idx: new Uint32Array(0), vis: true, box: new THREE.Box3() };
    const cellM = T.cell, half = World.half;
    // ---- count first: which quads carry a tide line?
    const quads = this._quads || (this._quads = new Uint8Array(256)), discs = this.discs, line = [0, 0];
    const cl = this.cliffAt((cell.cx + 0.5) * CELL - half, (cell.cz + 0.5) * CELL - half);
    let nq = 0;
    for (let z = 0; z < 16; z++) for (let x = 0; x < 16; x++) {
      const i = (iz0 + z) * N + ix0 + x;
      const a = h[i], b = h[i + 1], c = h[i + N], d = h[i + N + 1];
      const lo = Math.min(a, b, c, d), hi = Math.max(a, b, c, d);
      // rock and cobbles: the whole band; sand: only where the strand line runs
      // (above the barnacles only bedrock carries anything - lichen, the tar line - so level cobbles are left out)
      const gx = (b - a + d - c) * 0.5 / cellM, gz = (c - a + d - b) * 0.5 / cellM, steep = 1 - 1 / Math.sqrt(1 + gx * gx + gz * gz) > 0.05;
      let on = cl > 0.34 ? (hi > -0.55 && lo < (steep ? 4.3 : 1.6)) : (hi > 0.70 && lo < 1.58);
      if (on && cl <= 0.34) {
        // (the line's own height just here, with room for the loose bits strewn either side of it)
        const h0 = this.strand((ix0 + x + 1) * cellM - half, (iz0 + z + 1) * cellM - half, line)[0];
        on = lo < h0 + 0.24 && hi > h0 - 0.28;
      }
      if (discs.length && (hi > -0.55 && lo < 2.6)) {
        const qx = (ix0 + x + 1) * cellM - half, qz = (iz0 + z + 1) * cellM - half;
        // in a town: only rock standing in the tide (a quay's foot, a mole's flank), and nothing built over
        if (this.inTown(qx, qz, -2)) on = this.cliffAt(qx, qz) > 0.34 && !this.solid(qx, qz);
      } else if (on && discs.length) {
        const qx = (ix0 + x + 1) * cellM - half, qz = (iz0 + z + 1) * cellM - half;
        if (this.inTown(qx, qz, -2)) on = false;
      }
      quads[z * 16 + x] = on ? 1 : 0;
      nq += on ? 1 : 0;
    }
    // ---- shade under the big things
    const items = cell.items, shade = [];
    const sun = U.uSunDir.value, sl = Math.hypot(sun.x, sun.z) || 1, sdx = -sun.x / sl, sdz = -sun.z / sl, cot = sl / Math.max(sun.y, 0.15);
    for (let k = 0, o = 0; k < cell.n && shade.length < 60 * 9; k++, o += 22) {
      const r = items[o + 19];
      if (r === 0 || items[o + 17] < MID) continue;
      const hgt = items[o + 20];
      const len = hgt * cot;                                       // how far the shade is thrown
      if (items[o + 21] > 0) {
        // a log: a strip of shade lying along it. (centre, half-axis, radius)
        const L = -r * 0.92, ex = items[o + 6], ez = items[o + 8], rad = 0.13 + len * 0.5;
        shade.push(items[o] + sdx * len * 0.5, items[o + 2] + sdz * len * 0.5, ex * L, ez * L, rad, 128, 0.60, Math.abs(ex) * L + rad, Math.abs(ez) * L + rad);
      } else if (items[o + 1] > -0.6) {
        // a boulder: an ellipse drawn out down-sun. (centre, half-length, half-width)
        const a = r + len * 0.5;
        shade.push(items[o] + sdx * len * 0.5, items[o + 2] + sdz * len * 0.5, a, r, 0, 255, 0.72, Math.abs(sdx) * a + Math.abs(sdz) * r, Math.abs(sdz) * a + Math.abs(sdx) * r);
      }
    }
    // ---- crab holes: a dark pit and the spoil thrown out of it
    const B = cell.burrows || [];
    for (let k = 0; k < B.length; k += 4) shade.push(B[k], B[k + 1], B[k + 2], B[k + 3], 0, 64, 1, B[k + 2], B[k + 2]);
    let nv = nq ? 289 : 0, ni = nq * 6;
    const spans = [];
    for (let s = 0; s < shade.length; s += 9) {
      const cx = shade[s], cz = shade[s + 1], ex = shade[s + 7] + 0.1, ez = shade[s + 8] + 0.1;
      let qx0 = Math.floor((cx - ex + half) / cellM - 0.5), qx1 = Math.floor((cx + ex + half) / cellM - 0.5);
      let qz0 = Math.floor((cz - ez + half) / cellM - 0.5), qz1 = Math.floor((cz + ez + half) / cellM - 0.5);
      qx0 = clamp(qx0, 0, N - 2); qx1 = clamp(qx1, 0, N - 2); qz0 = clamp(qz0, 0, N - 2); qz1 = clamp(qz1, 0, N - 2);
      if (qx1 - qx0 > 7 || qz1 - qz0 > 7) continue;
      spans.push(qx0, qx1, qz0, qz1, s);
      nv += (qx1 - qx0 + 2) * (qz1 - qz0 + 2); ni += (qx1 - qx0 + 1) * (qz1 - qz0 + 1) * 6;
    }
    if (!nv) return { v0: -1, nv: 0, idx: new Uint32Array(0), vis: true, box: new THREE.Box3() };
    const v0 = D.alloc(nv);
    if (v0 < 0) return null;
    const idx = new Uint32Array(ni);
    const pos = D.position, dec = D.aDecal, misc = D.aMisc;
    let v = v0, io = 0, ymin = 1e9, ymax = -1e9;
    const vert = (ix, iz, dx, dz, da, db, kind, str, rad) => {
      const y = h[iz * N + ix], v3 = v * 3, v4 = v * 4;
      pos[v3] = (ix + 0.5) * cellM - half; pos[v3 + 1] = y; pos[v3 + 2] = (iz + 0.5) * cellM - half;
      dec[v4] = dx; dec[v4 + 1] = dz; dec[v4 + 2] = da; dec[v4 + 3] = db;
      misc[v4] = kind; misc[v4 + 1] = str; misc[v4 + 2] = rad; misc[v4 + 3] = 0;
      if (y < ymin) ymin = y; if (y > ymax) ymax = y;
      return v++;
    };
    const quad = (ix, iz, a, b, c, d) => {
      // the terrain's own triangulation: the diagonal alternates
      if ((ix + iz) & 1) { idx[io++] = a; idx[io++] = c; idx[io++] = b; idx[io++] = b; idx[io++] = c; idx[io++] = d; }
      else { idx[io++] = a; idx[io++] = c; idx[io++] = d; idx[io++] = a; idx[io++] = d; idx[io++] = b; }
    };
    if (nq) {
      const base = v;
      for (let z = 0; z <= 16; z++) for (let x = 0; x <= 16; x++) vert(ix0 + x, iz0 + z, 0, 0, 0, 0, 0, 255, 0);
      for (let z = 0; z < 16; z++) for (let x = 0; x < 16; x++) {
        if (!quads[z * 16 + x]) continue;
        const a = base + z * 17 + x;
        quad(ix0 + x, iz0 + z, a, a + 1, a + 17, a + 18);
      }
    }
    for (let s = 0; s < spans.length; s += 5) {
      const qx0 = spans[s], qx1 = spans[s + 1], qz0 = spans[s + 2], qz1 = spans[s + 3], k = spans[s + 4];
      const w = qx1 - qx0 + 2, base = v;
      const str = Math.round(shade[k + 6] * 255), rad = Math.min(255, Math.round(shade[k + 4] * 64));
      for (let z = qz0; z <= qz1 + 1; z++) for (let x = qx0; x <= qx1 + 1; x++) vert(x, z, shade[k], shade[k + 1], shade[k + 2], shade[k + 3], shade[k + 5], str, rad);
      for (let z = qz0; z <= qz1; z++) for (let x = qx0; x <= qx1; x++) {
        const a = base + (z - qz0) * w + (x - qx0);
        quad(x, z, a, a + 1, a + w, a + w + 1);
      }
    }
    D.touch(v0, nv);
    const x0 = cell.cx * CELL - half, z0 = cell.cz * CELL - half;
    const box = new THREE.Box3(new THREE.Vector3(x0 - 4, ymin - 1, z0 - 4), new THREE.Vector3(x0 + CELL + 4, ymax + 1, z0 + CELL + 4));
    return { v0, nv, idx: io < ni ? idx.slice(0, io) : idx, vis: true, box };
  }

  _drop(pool, chunk) {
    if (!chunk) return;
    pool.chunks.delete(chunk);
    if (chunk.v0 >= 0) pool.free(chunk.v0, chunk.nv);
    pool.dirty = true;
  }

  /** Bring a cell to the level of detail it should have. Returns the work it cost. */
  _advance(cell) {
    const want = cell.want;
    if (want === 3) {
      this._drop(this.pool, cell.dress); this._drop(this.decals, cell.decal);
      if (cell.hasCrabs) this._despawn(cell);
      cell.dress = cell.decal = null;
      cell.tier = 3;
      this.cells.delete(cell.key);
      return 20;
    }
    if (!cell.items) return this._generate(cell);
    const dress = this._bake(cell, want);
    if (!dress) { cell.retry = this.frame + 45; return 50; }
    let decal = cell.decal;
    if (want <= 1 && !decal) {
      decal = this._bakeDecals(cell);
      if (decal) { this.decals.chunks.add(decal); this.decals.dirty = true; }
    } else if (want > 1 && decal) { this._drop(this.decals, decal); decal = null; }
    this._drop(this.pool, cell.dress);
    this.pool.chunks.add(dress);
    this.pool.dirty = true;
    cell.dress = dress; cell.decal = decal;
    cell.tier = want;
    if (want <= 1 && !cell.hasCrabs) this._spawn(cell);
    else if (want > 1 && cell.hasCrabs) this._despawn(cell);
    return dress.nv + (decal ? decal.nv * 0.3 : 0) + 60;
  }

  // ---------------------------------------------------------------------------------- crabs
  _initCrabs() {
    const M = CRAB.max;
    const f = () => new Float32Array(M);
    this.c = {
      n: 0, x: f(), y: f(), z: f(), yaw: f(), hx: f(), hz: f(), tx: f(), tz: f(), timer: f(), gait: f(), amp: f(), claw: f(), hide: f(),
      size: f(), seed: f(), nx: f(), nz: f(), calm: f(), sgn: f(), raise: f(), wave: f(),
      state: new Uint8Array(M), kind: new Uint8Array(M), cell: new Int32Array(M), tick: new Uint8Array(M),
    };
    const K = this.kit.meshes;
    this.matCrab = new THREE.ShaderMaterial({
      uniforms: {
        ...shared(...SKY_UNIFORMS, 'uTime', 'uLightTex', 'uHeightTex', 'uSplatTex', 'uWorld', 'uNoiseTex', 'uShadowTex', 'uShadowMat', 'uShadowOn'),
      },
      vertexShader: CRAB_VERT, fragmentShader: CRAB_FRAG, side: THREE.DoubleSide,
      transparent: true, depthWrite: true,
      blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
      blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor,
    });
    const mk = (m) => {
      const g = new THREE.InstancedBufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(m.pos, 3));
      g.setAttribute('aPiv', new THREE.BufferAttribute(m.piv, 3));
      g.setAttribute('aNrm', new THREE.BufferAttribute(m.nrm, 4, true));
      g.setAttribute('aCol', new THREE.BufferAttribute(m.col, 4, true));
      g.setAttribute('aLeg', new THREE.BufferAttribute(m.aux, 4));
      // the blob of shade first, so a crab is drawn over its own
      const idx = Array.from(m.idx), sh = [], body = [];
      for (let i = 0; i < idx.length; i += 3) (m.aux[idx[i] * 4 + 2] === 5 ? sh : body).push(idx[i], idx[i + 1], idx[i + 2]);
      g.setIndex(sh.concat(body));
      const inst = {};
      for (const name of ['iA', 'iB', 'iC', 'iD']) {
        const a = new THREE.InstancedBufferAttribute(new Float32Array(M * 4), 4);
        a.setUsage(THREE.DynamicDrawUsage);
        g.setAttribute(name, a);
        inst[name] = a;
      }
      g.instanceCount = 0;
      const mesh = new THREE.Mesh(g, this.matCrab);
      mesh.frustumCulled = false; mesh.matrixAutoUpdate = false; mesh.visible = false;
      mesh.renderOrder = 30;
      this.group.add(mesh);
      return { mesh, geo: g, inst, tris: m.ni / 3, count: 0 };
    };
    this.crabNear = mk(K.crab);
    this.crabFar = mk(K.crab_far);
  }

  _spawn(cell) {
    cell.hasCrabs = true;
    const c = this.c, L = cell.crabs;
    for (let i = 0; i < L.length && c.n < CRAB.max; i += 5) {
      const k = c.n++;
      seed(hash2((L[i] * 16) | 0, (L[i + 1] * 16) | 0, 99));
      c.hx[k] = L[i]; c.hz[k] = L[i + 1]; c.kind[k] = L[i + 2]; c.size[k] = L[i + 3]; c.seed[k] = L[i + 4];
      // out and about near home (a few are still below)
      let x = L[i], z = L[i + 1];
      const a = rnd() * 6.283, d = rr(0.3, 1.5), ox = x + Math.cos(a) * d, oz = z + Math.sin(a) * d, oh = this.surf(ox, oz);
      const below = c.kind[k] === 0 && rnd() < 0.14;
      if (!below && oh > 0.45 && oh < 2.8 && c.kind[k] !== 1) { x = ox; z = oz; }
      else if (c.kind[k] === 1) { x = L[i] + (L[i] - ox) * 0.9; z = L[i + 1] + (L[i + 1] - oz) * 0.9; }
      c.x[k] = x; c.z[k] = z; c.y[k] = this.surf(x, z, this._n);
      c.nx[k] = this._n.x; c.nz[k] = this._n.z;
      c.yaw[k] = rnd() * 6.283; c.tx[k] = x; c.tz[k] = z;
      c.gait[k] = rnd(); c.amp[k] = 0; c.claw[k] = 0; c.raise[k] = 0; c.sgn[k] = 1; c.wave[k] = 0;
      c.state[k] = below ? 5 : 0; c.hide[k] = below ? 1 : 0; c.calm[k] = below ? rr(1, 6) : 0;
      c.timer[k] = rr(0.2, 3.5); c.cell[k] = cell.key; c.tick[k] = (rnd() * 4) | 0;
    }
  }
  _despawn(cell) {
    cell.hasCrabs = false;
    const c = this.c;
    for (let k = c.n - 1; k >= 0; k--) {
      if (c.cell[k] !== cell.key) continue;
      const j = --c.n;
      if (k !== j) for (const key in c) { const a = c[key]; if (a.length) a[k] = a[j]; }
    }
  }

  /** A puff of sand and a few thrown grains (through the game's particle system, if attached). */
  _puff(x, y, z, k = 1) {
    const fx = this.fx;
    if (!fx || !fx.sprites) return;
    const sun = fx.sunTint ? fx.sunTint(0.85) : [1.2, 1.2, 1.2];
    for (let i = 0; i < 2 * k; i++) {
      const a = Math.random() * 6.283, s = 0.25 + Math.random() * 0.5, b = 0.40 + Math.random() * 0.14;
      fx.sprites.spawn(x, y + 0.10, z, Math.cos(a) * s, 0.5 + Math.random() * 0.7, Math.sin(a) * s, {
        type: 2, r: 0.80 * sun[0] * b, g: 0.68 * sun[1] * b, b: 0.48 * sun[2] * b, alpha: 0.34 + Math.random() * 0.18, size: 0.26 + Math.random() * 0.16, grow: 0.8 + Math.random() * 0.5,
        life: 0.7 + Math.random() * 0.6, drag: 3.0, add: 0, wind: 0.5, wake: 0.3,
      });
    }
    if (fx.flakes) for (let i = 0; i < 3 * k; i++) {
      const a = Math.random() * 6.283, s = 0.5 + Math.random() * 1.3, v = 0.6 + Math.random() * 0.5;
      fx.flakes.spawn(x, y + 0.04, z, Math.cos(a) * s, 1.0 + Math.random() * 1.6, Math.sin(a) * s, 2, 0.018 + Math.random() * 0.022, 0.62 * v, 0.55 * v, 0.42 * v, 0.8 + Math.random() * 0.6, 0.9, 0.85);
    }
  }

  _crabs(dt, flight, time, cam) {
    const c = this.c, n = c.n;
    const rp = flight.pos, rv = flight.vel;
    const vx = rv.x, vz = rv.z, v2 = vx * vx + vz * vz;
    const R2 = CRAB.scareRadius * CRAB.scareRadius, look = CRAB.lookAhead;
    const self = this, nrm = this._n;
    const near = this.crabNear, far = this.crabFar;
    const NA = near.inst, FA = far.inst;
    let nn = 0, nf = 0;
    // which way the camera looks (to skip what is behind it)
    let cdx = 0, cdz = 0;
    if (this.camera) { const e = this.camera.matrixWorld.elements; cdx = -e[8]; cdz = -e[10]; }
    const DR = CRAB.drawRadius, DR2 = DR * DR, NR2 = CRAB.nearRadius * CRAB.nearRadius;
    const turn = (k, want, rate) => {
      let d = want - c.yaw[k];
      d = Math.atan2(Math.sin(d), Math.cos(d));
      c.yaw[k] += d * Math.min(1, rate * dt);
    };
    // head for the target; sideways, as crabs go
    const move = (k, speed) => {
      const dx = c.tx[k] - c.x[k], dz = c.tz[k] - c.z[k], d = Math.hypot(dx, dz);
      if (d < 1e-3) return 0;
      const st = Math.min(d, speed * dt);
      c.x[k] += (dx / d) * st; c.z[k] += (dz / d) * st;
      c.gait[k] = (c.gait[k] + st / (4 * CRAB.stride * c.size[k])) % 1;
      const a = Math.atan2(dx, dz);
      // whichever flank is nearer leads
      let d0 = a - Math.PI / 2 - c.yaw[k];
      d0 = Math.atan2(Math.sin(d0), Math.cos(d0));
      const lead = Math.abs(d0) <= Math.PI / 2 ? 1 : -1;
      c.sgn[k] = lead;
      turn(k, a - lead * Math.PI / 2, speed > 1.5 ? 16 : 7);
      c.y[k] = self.surf(c.x[k], c.z[k]);
      if ((c.tick[k] = (c.tick[k] + 1) & 7) === 0) { self.surf(c.x[k], c.z[k], nrm); c.nx[k] = nrm.x; c.nz[k] = nrm.z; }
      return d - st;
    };
    const wander = (k) => {
      for (let t = 0; t < 4; t++) {
        const a = Math.random() * 6.283, d = 0.35 + Math.random() * 1.6;
        let x = c.x[k] + Math.cos(a) * d, z = c.z[k] + Math.sin(a) * d;
        // never far from home
        const hx = x - c.hx[k], hz = z - c.hz[k], hd = Math.hypot(hx, hz), lim = c.kind[k] ? 2.6 : 2.9;
        if (hd > lim) { x = c.hx[k] + (hx / hd) * lim; z = c.hz[k] + (hz / hd) * lim; }
        // (a rock crab keeps clear of its own boulder until it needs it)
        else if (c.kind[k] === 1 && hd < 0.9) { x = c.hx[k] + (hx / (hd || 1)) * 1.1; z = c.hz[k] + (hz / (hd || 1)) * 1.1; }
        const h = self.terrain.heightAt(x, z);
        if (h < (c.kind[k] ? 0.12 : 0.55) || h > 2.9) continue;
        if (self.built(x, z, 1.5)) continue;
        c.tx[k] = x; c.tz[k] = z;
        return true;
      }
      return false;
    };

    for (let k = 0; k < n; k++) {
      // ---- is the rider coming this way?
      const dxr = c.x[k] - rp.x, dzr = c.z[k] - rp.z, dyr = rp.y - c.y[k];
      let scared = false;
      if (dyr < CRAB.ceiling && Math.abs(dxr) < 90 && Math.abs(dzr) < 90) {
        const s = v2 > 1 ? clamp((dxr * vx + dzr * vz) / v2, 0, look) : 0;
        const ex = dxr - vx * s, ez = dzr - vz * s, ey = dyr * 0.55, nerve = 0.7 + 0.4 * c.seed[k];
        scared = ex * ex + ez * ez + ey * ey < R2 * nerve * nerve;
      }
      let st = c.state[k];
      let ampT = 0, clawT = 0, raiseT = 0;
      switch (st) {
        case 0: // idle: stand about, wave a claw now and then
          if (scared) { st = 2; c.timer[k] = 0.03 + Math.random() * 0.2; break; }
          if (c.wave[k] > 0) { c.wave[k] -= dt; clawT = 0.5 + 0.5 * Math.sin(c.wave[k] * 9.0); raiseT = 0.3; }
          if ((c.timer[k] -= dt) <= 0) {
            if (Math.random() < 0.68 && wander(k)) st = 1;
            else { c.timer[k] = 0.7 + Math.random() * 3.2; if (Math.random() < 0.35) c.wave[k] = 1.2 + Math.random() * 1.4; }
          }
          break;
        case 1: // a short scuttle
          if (scared) { st = 2; c.timer[k] = 0.03 + Math.random() * 0.16; break; }
          ampT = 1;
          if (move(k, CRAB.walk * (0.7 + c.seed[k] * 0.7)) < 0.03) { st = 0; c.timer[k] = 0.5 + Math.random() * 3.0; }
          break;
        case 2: // seen something: up on its toes, claws out
          clawT = 1; raiseT = 1;
          if ((c.timer[k] -= dt) <= 0) {
            st = 3;
            if (c.kind[k] === 0) self._puff(c.x[k], c.y[k], c.z[k], 0.5);
            if (c.kind[k] < 2) { c.tx[k] = c.hx[k]; c.tz[k] = c.hz[k]; c.calm[k] = 0; }
            else {
              // no hole to go to: down the shore and into the sea
              self.terrain.normalAt(c.x[k], c.z[k], nrm, 2.5);
              let gx = nrm.x, gz = nrm.z; const gl = Math.hypot(gx, gz);
              if (gl < 0.02) { gx = -dxr; gz = -dzr; }
              const l = Math.hypot(gx, gz) || 1;
              c.tx[k] = c.x[k] + (gx / l) * 30; c.tz[k] = c.z[k] + (gz / l) * 30; c.calm[k] = 1;
            }
          }
          break;
        case 3: { // run for it
          ampT = 1; clawT = 0.45; raiseT = 0.4;
          const left = move(k, CRAB.flee * (0.85 + 0.3 * c.seed[k]) * (0.8 + c.size[k] * 1.2));
          if (c.calm[k] > 0.5) {
            // into the water
            if (c.y[k] < -0.5 || left < 0.05) { st = 5; c.hide[k] = 1; c.calm[k] = CRAB.calm[0] + Math.random() * (CRAB.calm[1] - CRAB.calm[0]); }
          } else if (left < 0.07) {
            st = 4; c.timer[k] = 0.16;
            if (c.kind[k] === 0) self._puff(c.x[k], c.y[k], c.z[k]);
          }
          if (Math.random() < dt * 5 && c.kind[k] === 0 && st === 3) self._puff(c.x[k], c.y[k], c.z[k], 0.5);
          break;
        }
        case 4: // down the hole (or tight under its rock)
          c.hide[k] = Math.min(1, c.hide[k] + dt / 0.16);
          if (c.hide[k] >= 1) { st = 5; c.calm[k] = CRAB.calm[0] + Math.random() * (CRAB.calm[1] - CRAB.calm[0]); }
          break;
        case 5: // hidden: wait until it has been quiet for a while
          if (scared) c.calm[k] = Math.max(c.calm[k], 3 + Math.random() * 3);
          else if ((c.calm[k] -= dt) <= 0) {
            if (c.kind[k] === 2) { st = 1; c.hide[k] = 0; c.tx[k] = c.hx[k]; c.tz[k] = c.hz[k]; }   // walk back up out of the sea
            else { st = 6; c.timer[k] = 0.9 + Math.random() * 1.8; }
          }
          break;
        case 6: // peep out: eyes and claw tips over the rim
          if (scared) { st = 4; break; }
          c.hide[k] += (0.70 - c.hide[k]) * Math.min(1, dt * 7);
          if ((c.timer[k] -= dt) <= 0) st = 7;
          break;
        default: // climb out
          if (scared) { st = 4; break; }
          c.hide[k] = Math.max(0, c.hide[k] - dt / 0.4);
          if (c.hide[k] <= 0) { st = 0; c.timer[k] = 0.4 + Math.random() * 1.5; }
      }
      c.state[k] = st;
      const e = Math.min(1, dt * 11);
      c.amp[k] += (ampT - c.amp[k]) * e; c.claw[k] += (clawT - c.claw[k]) * e; c.raise[k] += (raiseT - c.raise[k]) * e;

      // ---- draw it?
      if (c.hide[k] > 0.985) continue;
      const cx = c.x[k] - cam.x, cy = c.y[k] - cam.y, cz = c.z[k] - cam.z, d2 = cx * cx + cy * cy + cz * cz;
      if (d2 > DR2 || cx * cdx + cz * cdz < -2.5) continue;
      const nearOne = d2 < NR2;
      const A = nearOne ? NA : FA, o = (nearOne ? nn++ : nf++) * 4;
      const fade = 1 - sstep(DR * 0.84, DR, Math.sqrt(d2));
      const mir = c.seed[k] > 0.5 ? 1 : -1;           // which claw is the big one
      const a = A.iA.array, b = A.iB.array, cc = A.iC.array, dd = A.iD.array;
      a[o] = c.x[k]; a[o + 1] = c.y[k]; a[o + 2] = c.z[k]; a[o + 3] = c.yaw[k];
      b[o] = c.size[k] * fade * mir; b[o + 1] = c.nx[k]; b[o + 2] = c.nz[k]; b[o + 3] = c.hide[k];
      cc[o] = c.gait[k]; cc[o + 1] = c.amp[k]; cc[o + 2] = c.claw[k]; cc[o + 3] = c.seed[k];
      dd[o] = c.sgn[k]; dd[o + 1] = c.raise[k]; dd[o + 2] = c.kind[k] ? 1 : 0; dd[o + 3] = 0;
    }
    for (const [L, count] of [[near, nn], [far, nf]]) {
      L.count = count;
      L.geo.instanceCount = count;
      L.mesh.visible = count > 0 && this.enabled;
      if (!count) continue;
      for (const name in L.inst) { const a = L.inst[name]; a.clearUpdateRanges(); a.addUpdateRange(0, count * 4); a.needsUpdate = true; }
    }
    this.stats.crabs = n; this.stats.crabsDrawn = nn + nf; this.stats.crabTris = nn * near.tris + nf * far.tris;
  }

  // ---------------------------------------------------------------------------------- frame
  /**
   * @param flight the broom (its pos and vel scare the crabs)
   * @param time game time
   */
  update(dt, flight, time) {
    if (this.failed) return;
    try { this._update(dt, flight, time); } catch (e) {
      // decoration must never take the game down with it
      this.failed = true;
      this.group.visible = this.crabNear.mesh.visible = this.crabFar.mesh.visible = false;
      console.error('shore: switched off after an error', e);
    }
  }

  _update(dt, flight, time) {
    const t0 = performance.now();
    this.frame++;
    this.time = time;
    const cam = this.camera ? this.camera.position : U.uCamPos.value;
    const jump = cam.distanceToSquared(this._last) > 45 * 45;
    this._last.copy(cam);

    // ---- which cells should be at which level of detail?
    const half = World.half, G = this.gridN, mask = this.mask;
    const ccx = Math.floor((cam.x + half) / CELL), ccz = Math.floor((cam.z + half) / CELL);
    const R = TIER_R[2] + TIER_KEEP, span = Math.ceil(R / CELL);
    const alt = Math.max(0, cam.y - 14);
    const todo = this._todo;
    todo.length = 0;
    if (alt < R) {
      for (let cz = Math.max(0, ccz - span); cz <= Math.min(G - 1, ccz + span); cz++) for (let cx = Math.max(0, ccx - span); cx <= Math.min(G - 1, ccx + span); cx++) {
        if (!mask[cz * G + cx]) continue;
        const x0 = cx * CELL - half, z0 = cz * CELL - half;
        const dx = cam.x < x0 ? x0 - cam.x : cam.x > x0 + CELL ? cam.x - x0 - CELL : 0;
        const dz = cam.z < z0 ? z0 - cam.z : cam.z > z0 + CELL ? cam.z - z0 - CELL : 0;
        const d = Math.sqrt(dx * dx + dz * dz + alt * alt);
        const key = cz * G + cx;
        let cell = this.cells.get(key);
        const cur = cell ? cell.tier : 3;
        // stay at the present level a little past where it would be chosen afresh
        let want = d < TIER_R[0] ? 0 : d < TIER_R[1] ? 1 : d < TIER_R[2] ? 2 : 3;
        if (want > cur && cur < 3 && d < TIER_R[cur] + TIER_KEEP) want = cur;
        if (want === cur) { if (cell) { cell.want = want; cell.seen = this.frame; } continue; }
        if (!cell) this.cells.set(key, (cell = { key, cx, cz, tier: 3, want, items: null, n: 0, crabs: null, dress: null, decal: null, hasCrabs: false, retry: 0, seen: 0 }));
        cell.want = want; cell.d = d; cell.seen = this.frame;
        if (cell.retry <= this.frame) todo.push(cell);
      }
    }
    // cells left behind altogether (a teleport, a climb)
    if (this.frame % 16 === 0 || jump) for (const cell of this.cells.values()) if (cell.seen !== this.frame) { cell.want = 3; cell.d = 1e9; todo.push(cell); }

    // ---- do a frame's worth of it, nearest first
    let work = 0;
    if (todo.length) {
      todo.sort((a, b) => a.d - b.d);
      const budget = jump || this.frame < 3 ? Infinity : WORK_UNITS;
      // (a cell may take two steps: lay it out, then bake it)
      for (let pass = 0; pass < 2 && work < budget; pass++) for (let i = 0; i < todo.length && work < budget; i++) {
        const cell = todo[i];
        if (cell.tier === cell.want || cell.retry > this.frame) continue;
        work += this._advance(cell);
      }
    }
    this.stats.work = work;

    this._crabs(dt, flight, time, cam);
    this._cull();

    const s = this.stats;
    s.cells = this.cells.size; s.tris = this.pool.tris; s.decalTris = this.decals.tris; s.verts = this.pool.vertsLive;
    s.ms += (performance.now() - t0 - s.ms) * 0.05;
    s.peak = Math.max((s.peak || 0) * 0.995, performance.now() - t0);
  }

  /** Keep only the chunks in (or about to be in) view in the index lists. */
  _cull() {
    const cam = this.camera;
    let changed = false;
    if (cam) {
      cam.updateMatrixWorld();
      this._m4.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse);
      this._fr.setFromProjectionMatrix(this._m4, cam.coordinateSystem, cam.reversedDepth);
      const box = this._box, fr = this._fr;
      for (const pool of [this.pool, this.decals]) for (const c of pool.chunks) {
        // generous: the list is only rebuilt now and then, and the view can swing a long way meanwhile
        box.copy(c.box).expandByScalar(16);
        const vis = fr.intersectsBox(box);
        if (vis !== c.vis) { c.vis = vis; pool.changed = true; changed = true; }
      }
    }
    for (const pool of [this.pool, this.decals]) {
      if (pool.dirty || (pool.changed && this.frame >= this._cullAt)) { pool.rebuild(); pool.changed = false; if (changed) this._cullAt = this.frame + 4; }
    }
    this.meshDress.visible = this.enabled && this.pool.tris > 0;
    this.meshDecal.visible = this.enabled && this.decals.tris > 0;
  }

  /** Bake everything in range now (after a teleport, before a capture). */
  settle() { this._last.set(1e9, 0, 0); }

  // ---------------------------------------------------------------------------------- debug
  /** What is loaded right now, by kind of mesh: [instances, triangles]. */
  census() {
    const out = {}, list = this.kit.list;
    for (const cell of this.cells.values()) {
      if (cell.tier > 2 || !cell.items) continue;
      for (let k = 0, o = 0; k < cell.n; k++, o += 22) {
        if (cell.items[o + 17] < cell.tier) continue;
        const m = list[cell.tier >= 1 && cell.items[o + 13] >= 0 ? cell.items[o + 13] : cell.items[o + 12]];
        const e = out[m.name] || (out[m.name] = [0, 0]);
        e[0]++; e[1] += m.ni / 3;
      }
    }
    return out;
  }
  /** Stand every mesh of the kit in rows on the ground at (x, z), for a close look. */
  lineup(x, z, cols = 8, gap = 1.5) {
    if (this._lineup) { this._drop(this.pool, this._lineup); this._lineup = null; }
    const unit = { urchin: 0.055, starfish_a: 0.17, starfish_b: 0.17, scallop: 0.08, whelk: 0.13, cockle: 0.07 };
    const n = new THREE.Vector3(), e = new THREE.Vector3(1, 0, 0);
    this._ni = 0;
    let i = 0;
    for (const m of this.kit.list) {
      if (m.piv || m.name.startsWith('kelp')) continue;
      const px = x + (i % cols) * gap, pz = z + Math.floor(i / cols) * gap;
      i++;
      const h = this.surf(px, pz, n);
      e.set(1, 0, 0).addScaledVector(n, -n.x).normalize();
      const s = unit[m.name] || (m.name.startsWith('rock') ? 0.6 : 1);
      this._put(m, null, px, h, pz, n, e, s, s, s, 1, 1, 1, SMALL, 0.3);
    }
    const cell = { items: this._items.slice(0, this._ni * 22), n: this._ni };
    const chunk = this._bake(cell, 0);
    if (chunk) { this.pool.chunks.add(chunk); this.pool.dirty = true; this._lineup = chunk; }
    return i;
  }
  /** Drop a few crabs at a spot (they belong to no cell, so they stay). kind: 0 burrower, 1 under a rock, 2 runs for the sea. */
  crabsAt(x, z, count = 6, kind = 0, spread = 2) {
    const c = this.c;
    for (let i = 0; i < count && c.n < CRAB.max; i++) {
      const k = c.n++, a = Math.random() * 6.283, d = Math.sqrt(Math.random()) * spread;
      c.hx[k] = c.x[k] = c.tx[k] = x + Math.cos(a) * d; c.hz[k] = c.z[k] = c.tz[k] = z + Math.sin(a) * d;
      c.y[k] = this.surf(c.x[k], c.z[k], this._n); c.nx[k] = this._n.x; c.nz[k] = this._n.z;
      c.kind[k] = kind; c.size[k] = 0.27 + Math.random() * 0.13; c.seed[k] = Math.random(); c.yaw[k] = Math.random() * 6.283;
      c.gait[k] = 0; c.amp[k] = 0; c.claw[k] = 0; c.raise[k] = 0; c.sgn[k] = 1; c.wave[k] = 0; c.hide[k] = 0; c.calm[k] = 0;
      c.state[k] = 0; c.timer[k] = Math.random() * 2; c.cell[k] = -1; c.tick[k] = 0;
    }
    return c.n;
  }
}

// =====================================================================================
// shaders
// =====================================================================================
const SWELL_GLSL = /* glsl */`
uniform vec4 uWaveA[8];    // dir.xz, k, amp
uniform vec4 uWaveB[8];    // omega, steep, phase, -
uniform float uSea;
// how hard the sea is running at a spot (the water's own rule: sheltered inshore)
float seaAmp(vec2 xz){
  float off = shoreDist(textureLod(uLightTex, worldUV(xz), 0.0).b);
  float r = distance(xz, floor(uCamPos.xz * 0.5 + 0.5) * 2.0);
  return uSea * mix(0.30, 1.0, smoothstep(0.0, 110.0, off)) / (1.0 + pow(r / 1400.0, 2.0));
}
// where the water that rests at xz is now: the sea's own displacement, and the lie of its surface
vec3 swell(vec2 xz, float t, float amp, out vec2 slope){
  vec3 d = vec3(0.0);
  slope = vec2(0.0);
  for (int i = 0; i < 8; i++){
    vec4 a = uWaveA[i]; vec4 b = uWaveB[i];
    float ph = a.z * dot(a.xy, xz) - b.x * t + b.z;
    float s = sin(ph), c = cos(ph);
    float A = a.w * amp;
    d.xz += a.xy * (b.y / a.z) * amp * c;
    d.y += A * s;
    slope += a.xy * (a.z * A * c);
  }
  return d;
}
`;

// Barnacles, mussels and the rest, drawn as cells of a jittered grid. Shared by the boulders and
// the tide lines on the terrain so the two agree.
const CRUST_GLSL = /* glsl */`
// nearest feature point: xy = vector to it, z = its random number, w = distance
vec4 cells(vec2 p){
  vec2 i = floor(p), f = fract(p);
  vec4 best = vec4(0.0, 0.0, 0.0, 8.0);
  for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++){
    vec2 g = vec2(float(x), float(y));
    vec3 h = hash32(i + g);
    vec2 d = g + 0.5 + (h.xy - 0.5) * 0.72 - f;
    float dd = dot(d, d);
    if (dd < best.w) best = vec4(d, h.z, dd);
  }
  best.w = sqrt(best.w);
  return best;
}
// Acorn barnacles over uv (metres): a crust of small cones, shoulder to shoulder, each with a slit
// of an opening. cover = share of the places taken, px = metres per pixel.
// rgb albedo, a opacity; bump = how the surface leans, in the uv plane.
vec4 barnacles(vec2 uv, float cover, float px, out vec2 bump){
  const float S = 0.046;
  vec4 c = cells(uv / S);
  float keep = step(fract(c.z * 13.7), cover * 1.1);
  float r = mix(0.30, 0.60, fract(c.z * 7.31));
  float d = min(c.w / r, 1.5);
  float body = (1.0 - smoothstep(0.80, 1.0, d)) * keep;
  float ang = c.z * 40.0;
  vec2 ax = vec2(cos(ang), sin(ang));
  vec2 e = vec2(dot(c.xy, ax), dot(c.xy, vec2(-ax.y, ax.x))) / r;
  float slit = 1.0 - smoothstep(0.14, 0.28, length(e * vec2(1.0, 1.9)));
  vec3 shell = mix(vec3(0.19, 0.175, 0.14), vec3(0.40, 0.385, 0.33), fract(c.z * 3.17));
  shell *= 0.68 + 0.40 * smoothstep(1.0, 0.25, d);                           // paler up the cone
  shell *= 0.90 + 0.10 * sin(atan(c.y, c.x) * 6.0 + c.z * 20.0);             // its plates
  vec3 col = mix(shell, vec3(0.045, 0.038, 0.032), slit);
  // where they stand thick the rock between them is grown over too: old shells, young ones
  float crust = smoothstep(0.50, 0.90, cover) * 0.78;
  col = mix(vec3(0.155, 0.145, 0.118) * (0.75 + 0.5 * fract(c.z * 5.7)), col, body);
  bump = normalize(c.xy + 1e-5) * mix(-0.9, 1.0, slit) * body;               // the wall leans out, the crater in
  // far off it all runs together into a pale wash
  float far = smoothstep(0.35, 1.3, px / S);
  bump *= 1.0 - far;
  return vec4(mix(col, vec3(0.245, 0.235, 0.195), far), mix(max(body, crust), min(cover, 1.0) * 0.80, far));
}
// Mussels packed side by side, long axis along uv.y.
vec4 mussels(vec2 uv, float cover, float px, out vec2 bump){
  const vec2 S = vec2(0.052, 0.10);
  vec4 c = cells(uv / S);
  float keep = step(fract(c.z * 13.7), cover * 1.25);
  vec2 e = c.xy;
  float d = length(vec2(e.x * (1.22 + 0.7 * e.y), e.y)) * 1.05;
  float body = (1.0 - smoothstep(0.38, 0.47, d)) * keep;
  vec3 col = mix(vec3(0.006, 0.008, 0.018), vec3(0.030, 0.042, 0.085), smoothstep(0.42, 0.05, d)) * (0.7 + 0.6 * fract(c.z * 5.3));
  bump = -e * 2.0 * body;
  float far = smoothstep(0.35, 1.3, px / S.x);
  bump *= 1.0 - far;
  return vec4(mix(col, vec3(0.014, 0.019, 0.036), far), mix(body, min(cover, 1.0) * 0.66, far));
}
// pick a plane to lay a pattern on: the one the surface faces most squarely
void plane(vec3 P, vec3 N, out vec2 uv, out vec3 tu, out vec3 tv){
  vec3 an = abs(N);
  if (an.y >= an.x && an.y >= an.z){ uv = P.xz; tu = vec3(1.0, 0.0, 0.0); tv = vec3(0.0, 0.0, 1.0); }
  else if (an.x > an.z){ uv = P.zy; tu = vec3(0.0, 0.0, 1.0); tv = vec3(0.0, 1.0, 0.0); }
  else { uv = P.xy; tu = vec3(1.0, 0.0, 0.0); tv = vec3(0.0, 1.0, 0.0); }
}
`;

// ------------------------------------------------------------------------------------ dressing
const DRESS_VERT = /* glsl */`
precision highp float;
attribute vec4 aOff;     // offset from the pivot / ${OFF_RANGE} m; w = how far along its frond (weeds)
attribute vec4 aNrm;     // normal; w = baked occlusion
attribute vec4 aCol;     // albedo (gamma 2.2); a = gloss
attribute vec4 aAux;     // kind, fade distance / 2, phase, -
uniform float uTime;
uniform vec3 uCamPos;
${TERRAIN_LOOKUP}
${SWELL_GLSL}
varying vec3 vWorld;
varying vec3 vN;
varying vec4 vCol;
varying vec4 vInfo;      // occlusion, kind, baked sun, cliffness
varying vec4 vMore;      // pivot height, frond t, phase, distance from the pivot
void main(){
  vec3 pivot = position;
  float kind = aAux.x;
  float dist = distance(pivot, uCamPos);
  float fadeD = aAux.y * 2.0;
  float fade = 1.0 - smoothstep(fadeD * 0.82, fadeD, dist);
  if (fade <= 0.0){ gl_Position = vec4(2.0, 2.0, 2.0, 1.0); return; }
  vec3 off = aOff.xyz * ${OFF_RANGE.toFixed(1)} * fade;
  float t = aOff.w;
  float ph = aAux.z / 255.0;
  vec3 n = aNrm.xyz;
  vec3 wp = pivot + off;
  vec4 light = textureLod(uLightTex, worldUV(pivot.xz), 0.0);
  if (kind > 3.5 && kind < 4.5){
    // ---- kelp: every vertex is a bit of the sea's surface, and goes where that water goes
    float w = sin(t * 5.0 - uTime * 0.7 + ph * 6.2831) * 0.16 * t * t;
    vec2 q = wp.xz + vec2(-off.z, off.x) / max(length(off.xz), 0.05) * w;
    vec2 sl;
    vec3 d = swell(q, uTime, seaAmp(q), sl);
    float lift = 0.022 + dist * 0.00045;
    wp = vec3(q.x + d.x, d.y + lift + off.y * 1.5 - (1.0 - smoothstep(0.0, 0.14, t)) * 0.5, q.y + d.z);
    n = normalize(vec3(-sl.x, 1.0, -sl.y) + n * 0.35);
  } else if (kind > 2.5 && kind < 3.5){
    // ---- rockweed: hangs limp in the air; a swell that covers it floats the tips and drags them about
    vec2 sl;
    vec3 d = swell(pivot.xz, uTime, seaAmp(pivot.xz), sl);
    float under = smoothstep(-0.03, 0.22, d.y - wp.y);
    wp.y = mix(wp.y, max(wp.y, d.y + 0.012), under * t);
    wp.xz += d.xz * 1.6 * under * t;
    wp.xz += vec2(sin(uTime * 2.3 + ph * 40.0), cos(uTime * 1.9 + ph * 31.0)) * 0.007 * t * (1.0 - under);
  }
  vWorld = wp;
  vN = n;
  vCol = vec4(pow(aCol.rgb, vec3(2.2)), aCol.a);
  vInfo = vec4(aNrm.w, kind, light.r, light.a);
  vMore = vec4(pivot.y, t, ph, length(aOff.xyz) * ${OFF_RANGE.toFixed(1)});
  gl_Position = projectionMatrix * viewMatrix * vec4(wp, 1.0);
}
`;

const DRESS_FRAG = /* glsl */`
precision highp float;
precision highp sampler2DArray;
uniform float uTime;
uniform vec3 uSand;
uniform sampler2DArray uMatC;   // the terrain's materials: layer 1 is its rock
varying vec3 vWorld;
varying vec3 vN;
varying vec4 vCol;
varying vec4 vInfo;
varying vec4 vMore;
${NOISE}
${ATMOSPHERE}
${CLOUD_SHADOW}
${SHADOW}
${CRUST_GLSL}
void main(){
  vec3 P = vWorld;
  vec3 N = normalize(vN);
  if (!gl_FrontFacing) N = -N;
  vec3 V = normalize(uCamPos - P);
  float ao = clamp(vInfo.x, 0.0, 1.0), kind = vInfo.y, cliffy = vInfo.w;
  vec3 alb = max(vCol.rgb, vec3(0.0));
  float gloss = clamp(vCol.a, 0.0, 1.0);
  float px = max(length(dFdx(P)), length(dFdy(P)));
  float y = P.y;
  // the swash zone is wet
  float wet = smoothstep(1.0, 0.12, y);
  float leaf = 0.0;
  if (kind > 0.5 && kind < 1.5){
    // ---- a boulder: the island's own stone, banded by the tide - a weed-green foot, a belt of
    // barnacles, a tar-black line where the spray dries, lichen on the crown
    vec3 Nf = normalize(cross(dFdx(P), dFdy(P)));
    if (dot(Nf, V) < 0.0) Nf = -Nf;
    vec2 uv; vec3 tu, tv;
    plane(P, Nf, uv, tu, tv);
    vec4 tex = texture(uMatC, vec3(uv / 1.7 + vMore.z * 7.0, 1.0));
    float m1 = vnoise3(P * 2.1);
    alb *= tex.rgb * 1.85 * (0.62 + 0.42 * tex.a) * (0.84 + 0.30 * m1);
    float yy = y + (vnoise(P.xz * 0.8) - 0.5) * 0.36 + (tex.a - 0.5) * 0.16;
    alb *= mix(1.0, 0.45, smoothstep(0.80, 0.05, yy));
    float film = smoothstep(0.75, 0.10, yy) * smoothstep(0.32, 0.60, vnoise(uv * 2.6 + 3.0));
    alb = mix(alb, vec3(0.045, 0.100, 0.016), film * 0.8);
    float belt = smoothstep(0.18, 0.42, yy) * (1.0 - smoothstep(0.85, 1.30, yy));
    if (belt > 0.01){
      float patches = smoothstep(0.38, 0.54, vnoise(uv * 1.5 + 7.0) * 0.7 + m1 * 0.3);
      vec2 bump;
      vec4 b = barnacles(uv, belt * patches, px, bump);
      alb = mix(alb, b.rgb, b.a);
      N = normalize(N + (tu * bump.x + tv * bump.y) * 0.6 * b.a);
      gloss = mix(gloss, 0.22, b.a);
    }
    alb *= 1.0 - 0.5 * smoothstep(1.2, 1.5, yy) * (1.0 - smoothstep(1.7, 2.1, yy)) * smoothstep(0.3, 0.7, m1);
    float dry = smoothstep(1.7, 2.2, yy);
    if (dry > 0.01){
      // lichen: grey-green crusts, and gold where it likes the spot
      float l1 = vnoise(uv * 9.0) * 0.62 + vnoise(uv * 24.0 + 3.0) * 0.38;
      alb = mix(alb, vec3(0.30, 0.32, 0.25), smoothstep(0.56, 0.66, l1) * 0.5 * dry);
      float l2 = vnoise(uv * 13.0 + 20.0) * 0.6 + vnoise(uv * 31.0 + 8.0) * 0.4;
      alb = mix(alb, vec3(0.46, 0.27, 0.03), smoothstep(0.66, 0.73, l2) * smoothstep(0.42, 0.60, vnoise(P.xz * 0.45 + 11.0)) * 0.8 * dry);
    }
    gloss = mix(gloss, 0.7, smoothstep(0.55, 0.05, yy));
  } else if (kind > 4.5){
    // ---- driftwood: bleached silver, the grain running the length of it
    float around = vMore.y * 23.0, along = vMore.w;
    float g1 = vnoise(vec2(around * 2.6 + vMore.z * 50.0, along * 1.1));
    float g2 = vnoise(vec2(around * 9.0, along * 3.5 + 7.0));
    alb *= 0.74 + 0.36 * g1 + 0.16 * (g2 - 0.5);
    alb *= 1.0 - 0.55 * (1.0 - smoothstep(0.0, 0.07, abs(g1 - 0.5))) * step(0.5, g2);    // cracks
    alb *= mix(1.0, 0.62, wet);
  } else if (kind > 3.5){
    // kelp afloat: dark amber, sodden, shining
    alb *= 0.30;
    leaf = 0.25;
  } else if (kind > 2.5){
    leaf = 1.0;
    gloss = mix(gloss * 0.45, gloss, wet);
  } else {
    alb *= mix(1.0, 0.72, wet * (1.0 - gloss));
    gloss = max(gloss, wet * 0.45);
  }

  float sun = vInfo.z * cloudShadow(P.xz, uTime) * riderShadow(P);
  float ndl = dot(N, uSunDir);
  float dif = mix(saturate(ndl), saturate(ndl * 0.6 + 0.4), leaf);
  vec3 amb = mix(uAmbGround, uAmbSky, N.y * 0.5 + 0.5) * ao * 1.12;
  // the bright ground all round throws light back up under things
  vec3 ground = mix(uSand, vec3(0.17, 0.19, 0.21), smoothstep(0.25, 0.6, cliffy));
  amb += uSunColor * ground * 0.34 * saturate(0.8 - N.y * 0.8) * sun * ao;
  vec3 col = alb * (uSunColor * dif * sun + amb);
  // weed lights up with the sun behind it
  float back = saturate(dot(V, -uSunDir) * 0.5 + 0.5);
  col += alb * uSunColor * vec3(1.0, 0.86, 0.36) * (0.08 + 0.55 * back * back) * sun * leaf;
  // wet things glint, and show the sky
  vec3 H = normalize(uSunDir + V);
  float rough = mix(0.80, 0.14, gloss);
  float a2 = rough * rough;
  float ndh = saturate(dot(N, H));
  float den = ndh * ndh * (a2 * a2 - 1.0) + 1.0;
  float D = a2 * a2 / (3.14159 * den * den);
  col += uSunColor * sun * saturate(ndl) * min(D, 28.0) * 0.045 * (0.25 + 0.75 * gloss);
  float fres = pow(1.0 - saturate(dot(N, V)), 5.0);
  vec3 R = reflect(-V, N);
  col += skyBase(normalize(vec3(R.x, abs(R.y) + 0.02, R.z))) * (0.04 + 0.96 * fres) * gloss * gloss * 0.55 * ao;
  col = applyAtmosphere(col, P);
  gl_FragColor = vec4(col, 1.0);
}
`;

// ------------------------------------------------------------------------------------ tide lines
const DECAL_VERT = /* glsl */`
precision highp float;
attribute vec4 aDecal;   // centre.xz, then: half-length down-sun + half-width (a boulder's shade), half-axis (a log's), reach + bearing (a burrow)
attribute vec4 aMisc;    // 0 tide line / 0.25 burrow / 0.5 a log's shade / 1 a boulder's; strength; a log's radius / 4 m
uniform vec3 uCamPos;
${TERRAIN_LOOKUP}
varying vec3 vWorld;
varying vec4 vDecal;
varying vec3 vMisc;
void main(){
  // the very vertex the terrain draws here: same place, same height lookup
  vec2 xz = position.xz;
  vec3 P = vec3(xz.x, terrainHLod(xz, 0.0), xz.y);
  vWorld = P;
  vDecal = aDecal;
  vMisc = aMisc.xyz;
  // a nudge toward the eye along its own ray: nothing moves on screen, it just wins the depth test
  vec3 toCam = uCamPos - P;
  float d = length(toCam);
  P += toCam / d * (0.010 + d * 0.0007);
  gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0);
}
`;

const DECAL_FRAG = /* glsl */`
precision highp float;
uniform float uTime;
uniform float uLodAlt;
uniform float uLodRange;
uniform vec3 uTowns[3];    // x, z, r: the tide lines stop at a town's edge
varying vec3 vWorld;
varying vec4 vDecal;
varying vec3 vMisc;
${NOISE}
${NOISE_TEX}
${ATMOSPHERE}
${CLOUD_SHADOW}
${TERRAIN_LOOKUP}
${SHADOW}
${CRUST_GLSL}
// lay a colour over what has built up so far (acc is premultiplied)
void over(inout vec4 acc, vec3 c, float a){ acc = vec4(c * a + acc.rgb * (1.0 - a), a + acc.a * (1.0 - a)); }
void main(){
  vec3 P = vWorld;
  // this layer lies on the terrain's finest mesh: it must be gone before that mesh starts to morph
  float lodD = length(vec2(distance(P.xz, uCamPos.xz), uLodAlt)) / uLodRange;
  float lodFade = 1.0 - smoothstep(0.50, 0.68, lodD);
  if (lodFade <= 0.0) discard;
  vec2 tuv = worldUV(P.xz);
  vec4 light = texture(uLightTex, tuv);

  if (vMisc.x > 0.375){
    float sunVis = light.r * cloudShadow(P.xz, uTime) * riderShadow(P);
    // ---- shade under a boulder or a log, thrown down-sun
    vec2 r = P.xz - vDecal.xy;
    float d;
    if (vMisc.x > 0.75){
      vec2 sd = normalize(-uSunDir.xz);
      d = length(vec2(dot(r, sd) / vDecal.z, dot(r, vec2(-sd.y, sd.x)) / vDecal.w));
    } else {
      vec2 ax = vDecal.zw;
      d = length(r - ax * clamp(dot(r, ax) / dot(ax, ax), -1.0, 1.0)) / max(vMisc.z * 3.984, 0.01);
    }
    float a = (1.0 - smoothstep(0.35, 1.0, d)) * vMisc.y * lodFade * sunVis;
    if (a < 0.004) discard;
    // what is left in shade is the sky's light: a little blue comes back
    gl_FragColor = vec4(applyAtmosphere(uAmbSky * 0.10, P) * a, a);
    return;
  }
  if (vMisc.x > 0.125){
    // ---- a crab's burrow: a dark hole, a ring of spoil thrown mostly one way, pellets of sand
    float sunVis = light.r * cloudShadow(P.xz, uTime) * riderShadow(P);
    vec2 r = (P.xz - vDecal.xy) / vDecal.z;
    vec2 fan = vec2(cos(vDecal.w), sin(vDecal.w));
    float side = dot(normalize(r + 1e-5), fan) * 0.5 + 0.5;                 // 1 on the side the spoil went
    float d = length(r) / mix(0.62, 1.0, side) + (vnoise(P.xz * 23.0) - 0.5) * 0.10;
    float pit = 1.0 - smoothstep(0.17, 0.25, d);
    float ring = smoothstep(0.18, 0.32, d) * (1.0 - smoothstep(0.42, 1.0, d));
    // the mound catches the sun on one flank and is shaded on the other
    vec2 sunXZ = normalize(uSunDir.xz);
    float rise = smoothstep(0.75, 0.40, d) - smoothstep(0.34, 0.20, d) * 1.8;   // climbing toward the rim, then down into the hole
    float lit = 1.0 + 0.55 * dot(normalize(r + 1e-5), -sunXZ) * rise * sunVis;
    vec3 sandC = vec3(0.66, 0.50, 0.295) * 1.10 * mix(1.0, 0.5, smoothstep(1.05, 0.12, P.y));
    // pellets: little balls of sand rolled out and left
    vec4 c = cells(P.xz / 0.045);
    float ball = (1.0 - smoothstep(0.20, 0.32, c.w)) * step(fract(c.z * 5.9), 0.34 * smoothstep(1.0, 0.45, d) * smoothstep(0.22, 0.34, d) * (0.3 + 0.7 * side));
    float bl = dot(normalize(c.xy + 1e-5), sunXZ);                               // each lit on its own sunward side
    vec3 lightC = uSunColor * 0.56 * sunVis + mix(uAmbGround, uAmbSky, 0.85) * light.g;
    vec3 col = sandC * lit * lightC;
    col = mix(col, sandC * (0.80 + 0.45 * bl * sunVis) * lightC, ball);
    float a = max(ring * 0.88, ball * 0.95);
    // the hole itself: lit a little way down its sunward wall, black below
    vec3 hole = sandC * lightC * 0.22 * smoothstep(-0.6, 0.9, dot(normalize(r + 1e-5), -sunXZ)) * smoothstep(0.02, 0.24, d);
    col = mix(col, hole, pit);
    a = max(a, pit) * lodFade;
    if (a < 0.004) discard;
    gl_FragColor = vec4(applyAtmosphere(col, P) * a, a);
    return;
  }

  float y = P.y;
  float cliffy = light.a;
  float px = max(length(dFdx(P)), length(dFdy(P)));
  float rocky = smoothstep(0.25, 0.60, cliffy);
  vec3 N = vec3(0.0, 1.0, 0.0);
  float face = 0.0;
  vec4 acc = vec4(0.0);
  vec3 bumpW = vec3(0.0);
  float gloss = 0.2;
  // in a town nothing is strewn about: the strand lines stop at its edge (what grows on rock stays)
  float wild = 1.0;
  for (int i = 0; i < 3; i++) wild *= smoothstep(uTowns[i].z - 2.0, uTowns[i].z + 12.0, distance(P.xz, uTowns[i].xy));

  if (rocky > 0.01){
    N = terrainN(P.xz, 0.0);
    float slope = 1.0 - N.y;
    vec4 nA = ntex(P.xz * 1.7), nB = ntex(P.xz * 9.0);
    // bedrock rather than loose cobbles (the terrain's own rule for where it paints rock)
    face = smoothstep(0.235, 0.39, slope + (nA.r - 0.5) * 0.17 + (nB.g - 0.5) * 0.10 + cliffy * 0.10 * smoothstep(0.08, 0.2, slope)) * rocky;
    float yy = y + (nA.g - 0.5) * 0.55 + (nB.r - 0.5) * 0.18;
    vec2 uv; vec3 tu, tv;
    plane(P, N, uv, tu, tv);
    if (face > 0.01){
      // lichen on the dry rock above the splash: grey-green crusts, a little gold
      float dry = smoothstep(2.1, 2.8, yy) * (1.0 - smoothstep(3.4, 4.2, yy)) * face;
      if (dry > 0.01){
        float l1 = ntex(uv * 190.0).r * 0.6 + ntex(uv * 520.0 + 0.3).g * 0.4;
        over(acc, vec3(0.30, 0.32, 0.25), smoothstep(0.60, 0.70, l1) * 0.42 * dry);
        float l2 = ntex(uv * 260.0 + 0.6).b * 0.6 + ntex(uv * 700.0).a * 0.4;
        over(acc, vec3(0.46, 0.27, 0.03), smoothstep(0.68, 0.75, l2) * smoothstep(0.50, 0.70, nA.b) * 0.7 * dry);
      }
      // the black band: tar lichen where the spray dries
      float tar = smoothstep(1.35, 1.75, yy) * (1.0 - smoothstep(2.1, 2.7, yy)) * face;
      over(acc, vec3(0.020, 0.020, 0.018), tar * (0.30 + 0.35 * nB.b));
      // the barnacle belt, in patches
      float belt = smoothstep(0.24, 0.50, yy) * (1.0 - smoothstep(1.30, 1.80, yy)) * face;
      if (belt > 0.01){
        vec2 bump;
        vec4 b = barnacles(uv, belt * smoothstep(0.30, 0.48, nA.a * 0.65 + nB.b * 0.35), px, bump);
        over(acc, b.rgb, b.a);
        bumpW += (tu * bump.x + tv * bump.y) * 0.6 * b.a;
      }
      // mussel beds below them
      float bed = smoothstep(-0.25, 0.0, yy) * (1.0 - smoothstep(0.35, 0.70, yy)) * smoothstep(0.42, 0.58, nA.b) * face;
      if (bed > 0.01){
        vec2 bump;
        vec4 m = mussels(uv, bed, px, bump);
        over(acc, m.rgb, m.a);
        bumpW += (tu * bump.x + tv * bump.y) * 0.7 * m.a;
        gloss = mix(gloss, 0.8, m.a);
      }
    }
    // green film at the waterline, bright where the swash keeps it wet
    float film = smoothstep(0.42, 0.0, yy) * smoothstep(0.40, 0.68, nB.a * 0.6 + nA.r * 0.4) * rocky;
    over(acc, mix(vec3(0.040, 0.095, 0.014), vec3(0.085, 0.17, 0.025), nB.g), film * mix(0.26, 0.74, face));
    gloss = mix(gloss, 0.6, film);
    // the cobbles' own strand line: scraps of dark weed caught among the stones, on the level ground only
    float line = exp(-pow((yy - 1.20) / 0.11, 2.0)) * (1.0 - smoothstep(0.03, 0.10, slope)) * rocky * wild;
    if (line > 0.02){
      float rag = ntex(P.xz * 31.0).b * 0.6 + ntex(P.xz * 120.0).r * 0.4;
      float far = smoothstep(0.03, 0.14, px);
      over(acc, mix(vec3(0.030, 0.024, 0.010), vec3(0.070, 0.055, 0.016), nB.g), mix(smoothstep(0.56, 0.66, line * 0.55 + (rag - 0.5) * 1.1), line * 0.12, far) * 0.85);
    }
  }
  if (rocky < 0.99 && wild > 0.01){
    // ---- sand: the strand line, wandering along its contour, thick in some stretches and bare in others
    // (shore.js strand() is the same field on the CPU: the weed heaps sit on this line)
    float sand = (1.0 - rocky) * wild;
    float h0 = 1.14 + (ntex(P.xz * 1.3 + 9.0).r - 0.5) * 0.40 + (ntex(P.xz * 6.0).g - 0.5) * 0.07;
    float gate = smoothstep(0.30, 0.52, ntex(P.xz * 0.9 + 3.0).a);
    float dh = y - h0;
    float core = exp(-pow(dh / 0.022, 2.0)) * (0.25 + 0.75 * gate) * sand;
    float halo = exp(-pow((dh + 0.012) / 0.085, 2.0)) * (0.3 + 0.7 * gate) * sand;
    if (halo > 0.02){
      float far = smoothstep(0.025, 0.12, px);
      // heaps: where the line is thickest the weed lies in a mat, ragged and full of holes
      float rag = ntex(P.xz * 34.0).b * 0.5 + ntex(P.xz * 150.0).r * 0.5;
      float mat = smoothstep(0.50, 0.58, core * 0.62 + (rag - 0.5) * 1.25);
      // strands: straps of weed lying every which way, thick on the line and thinning either side
      vec4 c1 = cells(P.xz / 0.17);
      float a1 = c1.z * 31.4;
      vec2 x1 = vec2(cos(a1), sin(a1));
      float s1 = (1.0 - smoothstep(0.06, 0.11, abs(dot(c1.xy, vec2(-x1.y, x1.x)) + 0.05 * sin(dot(c1.xy, x1) * 9.0)))) * (1.0 - smoothstep(0.30, 0.44, abs(dot(c1.xy, x1))));
      s1 *= step(fract(c1.z * 5.9), core * 1.1 + halo * 0.10);
      vec4 c2 = cells(P.xz / 0.065 + 7.7);
      float a2 = c2.z * 31.4;
      vec2 x2 = vec2(cos(a2), sin(a2));
      float s2 = (1.0 - smoothstep(0.05, 0.10, abs(dot(c2.xy, vec2(-x2.y, x2.x))))) * (1.0 - smoothstep(0.26, 0.40, abs(dot(c2.xy, x2))));
      s2 *= step(fract(c2.z * 5.9), core * 0.5 + halo * 0.28);
      // dried weed: mostly near black, some olive, the odd red or straw-pale strand
      float k1 = fract(c1.z * 7.7), k2 = fract(c2.z * 7.7);
      vec3 w1 = k1 < 0.6 ? mix(vec3(0.022, 0.017, 0.010), vec3(0.060, 0.045, 0.020), k1 / 0.6) : (k1 < 0.8 ? vec3(0.075, 0.070, 0.020) : (k1 < 0.92 ? vec3(0.13, 0.035, 0.022) : vec3(0.30, 0.25, 0.13)));
      vec3 w2 = mix(vec3(0.030, 0.022, 0.012), vec3(0.16, 0.11, 0.05), k2 * k2);
      over(acc, vec3(0.026, 0.020, 0.011) * (0.7 + 0.8 * ntex(P.xz * 300.0).g), mat * (1.0 - far) * 0.90);
      over(acc, w1, s1 * (1.0 - far) * 0.95);
      over(acc, w2, s2 * (1.0 - far) * 0.90);
      // from far off, just the dark thread of it along the sand
      over(acc, vec3(0.040, 0.030, 0.016), (core * 0.42 + halo * 0.05) * far);
      // shell grit glints among it
      float grit = step(0.95, fract(c2.z * 13.3)) * (1.0 - smoothstep(0.10, 0.17, c2.w)) * step(0.25, halo) * (1.0 - far);
      over(acc, vec3(0.80, 0.74, 0.64), grit);
    }
  }
  float a = acc.a * lodFade;
  if (a < 0.004) discard;

  // ---- lit as the terrain under it is (only now: most of this layer's pixels are bare and gone by here)
  float sunVis = light.r * cloudShadow(P.xz, uTime) * riderShadow(P);
  if (rocky <= 0.01) N = terrainN(P.xz, 0.0);
  vec3 Nb = normalize(N + bumpW);
  vec3 V = normalize(uCamPos - P);
  float ndl = dot(Nb, uSunDir);
  vec3 amb = mix(uAmbGround, uAmbSky, Nb.y * 0.5 + 0.5) * mix(light.g, 0.35 + 0.65 * light.g, face) * (1.0 + 0.45 * face);
  vec3 col = acc.rgb / max(acc.a, 1e-4) * (uSunColor * saturate(ndl) * sunVis + amb);
  vec3 H = normalize(uSunDir + V);
  float rough = mix(0.8, 0.16, gloss), a2 = rough * rough;
  float ndh = saturate(dot(Nb, H));
  float den = ndh * ndh * (a2 * a2 - 1.0) + 1.0;
  col += uSunColor * sunVis * saturate(ndl) * min(a2 * a2 / (3.14159 * den * den), 30.0) * 0.035 * (0.3 + 0.7 * gloss);
  col = applyAtmosphere(col, P);
  gl_FragColor = vec4(col * a, a);
}
`;

// ------------------------------------------------------------------------------------ crabs
const CRAB_VERT = /* glsl */`
precision highp float;
attribute vec3 aPiv;     // the joint this vertex hangs from
attribute vec4 aNrm;     // normal; w = baked occlusion
attribute vec4 aCol;     // paint masks: shell, cream, dark; a = gloss
attribute vec4 aLeg;     // gait phase, weight (0 hip .. 255 toe), part
attribute vec4 iA;       // position, yaw
attribute vec4 iB;       // size (negative = mirrored), ground normal x z, hidden 0..1
attribute vec4 iC;       // gait, how hard it is walking, claws raised, seed
attribute vec4 iD;       // which flank leads, up on its toes, kind, -
uniform float uTime;
uniform vec3 uCamPos;
uniform vec3 uSunDir;
${TERRAIN_LOOKUP}
varying vec3 vWorld;
varying vec3 vN;
varying vec4 vCol;
varying vec4 vInfo;      // occlusion, shade opacity, baked sun, cliffness
varying vec3 vShell;
vec3 hsv(float h, float s, float v){ vec3 k = abs(fract(h + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0) - 1.0; return v * mix(vec3(1.0), clamp(k, 0.0, 1.0), s); }
void main(){
  float part = aLeg.z, w = aLeg.y / 255.0, ph0 = aLeg.x / 255.0;
  float gait = iC.x, amp = iC.y, claw = iC.z, sd = iC.w;
  float hide = iB.w, raise = iD.y;
  float size = abs(iB.x), mir = iB.x < 0.0 ? -1.0 : 1.0;
  vec3 p = position, n = aNrm.xyz, piv = aPiv;
  float shade = 0.0;
  if (part > 4.5){
    // the blob of shade on the ground
    shade = w * (1.0 - hide);
  } else if (part > 0.5 && part < 1.5){
    // ---- a leg: reach along the way it is going, lift on the way back
    float ph = (gait + ph0) * 6.2831853;
    float fidget = (1.0 - amp) * max(sin(uTime * 2.3 + ph0 * 19.0 + sd * 40.0) - 0.82, 0.0) * 2.4;
    p.x += -cos(ph) * iD.x * mir * ${CRAB.stride.toFixed(3)} * w * amp;
    p.y += (max(sin(ph), 0.0) * 0.11 * amp + fidget * 0.05) * w * w;
    p.y += raise * 0.10 * (1.0 - w);
  } else {
    // ---- body, eyes and claws ride on the legs
    p.y += raise * 0.10 + sin(gait * 12.566) * 0.014 * amp;
    piv.y += raise * 0.10;
    if (part > 1.5 && part < 3.5){
      // claws swing up about the shoulder; the big one higher
      float a = claw * (part < 2.5 ? 1.05 : 0.7) + (1.0 - claw) * 0.05 * sin(uTime * 1.3 + sd * 30.0);
      float c = cos(a), s = sin(a);
      vec3 d = p - piv;
      d.yz = vec2(d.y * c + d.z * s, d.z * c - d.y * s);
      n.yz = vec2(n.y * c + n.z * s, n.z * c - n.y * s);
      p = piv + d;
    } else if (part > 3.5){
      // eye stalks lean a little as it looks about
      p.x += (p.y - piv.y) * 0.25 * sin(uTime * 1.7 + sd * 50.0 + p.x * 9.0);
    }
  }
  // going down its hole: sink, and draw in
  p.y -= hide * 0.50;
  p.xz *= 1.0 - 0.35 * hide;
  p.x *= mir; n.x *= mir;

  // ---- onto the ground
  vec3 up = normalize(vec3(iB.y, sqrt(max(1.0 - iB.y * iB.y - iB.z * iB.z, 0.04)), iB.z));
  vec3 f0 = vec3(sin(iA.w), 0.0, cos(iA.w));
  vec3 right = normalize(cross(up, f0));
  vec3 fwd = cross(right, up);
  vec3 wp = iA.xyz + (right * p.x + up * p.y + fwd * p.z) * size;
  if (part > 4.5) wp.xz -= uSunDir.xz / max(uSunDir.y, 0.2) * 0.07 * size;
  vWorld = wp;
  vN = right * n.x + up * n.y + fwd * n.z;
  vCol = aCol;
  vec4 light = textureLod(uLightTex, worldUV(iA.xz), 0.0);
  vInfo = vec4(aNrm.w, shade, light.r, light.a);
  // ---- livery: sand crabs run from orange to scarlet, with the odd blue one; rock crabs are darker
  float k = fract(sd * 7.13);
  // (orange rather than pure red: the tonemapper turns a saturated red to raspberry)
  vec3 sandC = k < 0.92 ? hsv(mix(0.075, 0.035, fract(sd * 3.7)), 0.96, mix(0.60, 0.84, fract(sd * 11.1))) : vec3(0.05, 0.17, 0.55);
  vec3 rockC = k < 0.6 ? hsv(mix(0.03, 0.07, fract(sd * 3.7)), 0.86, 0.40) : (k < 0.85 ? vec3(0.42, 0.14, 0.34) : vec3(0.20, 0.30, 0.10));
  vShell = iD.z > 0.5 ? rockC : sandC;
  gl_Position = projectionMatrix * viewMatrix * vec4(wp, 1.0);
}
`;

const CRAB_FRAG = /* glsl */`
precision highp float;
uniform float uTime;
varying vec3 vWorld;
varying vec3 vN;
varying vec4 vCol;
varying vec4 vInfo;
varying vec3 vShell;
${NOISE}
${ATMOSPHERE}
${CLOUD_SHADOW}
${SHADOW}
void main(){
  vec3 P = vWorld;
  float sun = vInfo.z * cloudShadow(P.xz, uTime) * riderShadow(P);
  if (vInfo.y > 0.001){
    float a = clamp(vInfo.y, 0.0, 1.0);
    a = a * a * (3.0 - 2.0 * a) * 0.80 * sun;
    gl_FragColor = vec4(applyAtmosphere(uAmbSky * 0.08, P) * a, a);
    return;
  }
  vec3 N = normalize(vN);
  if (!gl_FrontFacing) N = -N;
  vec3 V = normalize(uCamPos - P);
  vec3 m = clamp(vCol.rgb, 0.0, 1.0);
  vec3 alb = vShell * m.r + vec3(0.80, 0.70, 0.52) * m.g + vec3(0.02, 0.018, 0.022) * m.b;
  float ao = clamp(vInfo.x, 0.0, 1.0);
  float gloss = clamp(vCol.a, 0.0, 1.0);
  float ndl = dot(N, uSunDir);
  vec3 amb = mix(uAmbGround, uAmbSky, N.y * 0.5 + 0.5) * ao * 1.15;
  vec3 ground = mix(vec3(0.66, 0.50, 0.295), vec3(0.17, 0.19, 0.21), smoothstep(0.25, 0.6, vInfo.w));
  amb += uSunColor * ground * 0.34 * saturate(0.8 - N.y * 0.8) * sun * ao;
  vec3 col = alb * (uSunColor * saturate(ndl) * sun + amb);
  // a polished shell: a hard glint and a rim of sky
  vec3 H = normalize(uSunDir + V);
  float rough = mix(0.7, 0.20, gloss), a2 = rough * rough;
  float ndh = saturate(dot(N, H));
  float den = ndh * ndh * (a2 * a2 - 1.0) + 1.0;
  col += uSunColor * sun * saturate(ndl) * min(a2 * a2 / (3.14159 * den * den), 30.0) * 0.05 * gloss;
  float fres = pow(1.0 - saturate(dot(N, V)), 4.0);
  vec3 R = reflect(-V, N);
  col += skyBase(normalize(vec3(R.x, abs(R.y) + 0.02, R.z))) * fres * gloss * 0.35 * ao;
  col = applyAtmosphere(col, P);
  gl_FragColor = vec4(col, 1.0);
}
`;
