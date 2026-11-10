// Places: hidden corners of the island. Each has a hero piece or two, plants that grow nowhere
// else, some dressing, and one treasure that floats there until the broom flies through it.
//
// Data: assets/places/<set>.json (west, east; either may be missing):
//   { "places": [ { id, name, hint, pos:[x,y,z], radius,
//       models: { key: "path/to.glb" },                       paths relative to assets/places/
//       items:  [ { model, pos:[x,y,z], yaw, scale } ],       static pieces (instanced per model)
//       flora:  [ { model, center:[x,z], radius, count, seed, scale:[min,max] } ],   scattered on the ground
//       treasure: { id, name, lore, model, pos:[x,y,z] },
//       clear:  [ { x, z, r, grass, flowers } ]               for the terrain bake, not read here
//   } ] }
// Optional extras this module understands (all may be left out):
//   items[]:   rot:[x,y,z] (radians, applied after yaw), agl (seat the piece that far above the ground)
//   flora[]:   inner (no plants inside that radius), clump (0..1), steep:true (allow cliff faces), lift (metres above the ground, for
//              things that float on the river), shed:{color:[r,g,b], height, kind:'fluff'|'petal'}
//   treasure:  color:[r,g,b] (the glint's tint), scale, petals:[[r,g,b], ...] (burst colours)
//   place:     drift:[{ from:[x,y,z], radius, rate, color:[r,g,b], kind:'petal'|'fluff', reach }]
// Every GLB may have a JSON sidecar next to it (same name, .json) like the props in assets/models:
//   { height, radius, baseRadius, slabs:[[x,z,r,y0,y1],...] }   slabs: collision + baked shadows
// and, optionally: solid:[...] (collision discs to use instead of slabs), collide:false,
//   sway (wind response, 1 = default), cloth:[length, amplitude], glow:[r,g,b,strength],
//   glowKey:'amber'|'teal' (the parts of the texture with that colour give off the glow),
//   thin:true (draw both faces), foliage (0..1 leaf translucency), lod0 (flora: metres before thinning).
//
// Nothing is fetched but the two small JSON files until the rider comes within LOAD_DIST of a place.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { U, shared } from '../core/ctx.js';
import { NOISE, NOISE_TEX, ATMOSPHERE, CLOUD_SHADOW, TERRAIN_LOOKUP, WIND, SHADOW } from '../shaders/common.js';
import { SKY_UNIFORMS } from './sky.js';
import { KIND, SPR } from '../fx/particles.js';
import { Journal } from '../ui/journal.js';

const SETS = ['west', 'east'];
const LOAD_DIST = 1500;       // metres: fetch a place's models when the rider (or the eye) is this close
const PICKUP = 4.2;           // metres: fly this close to a treasure to take it
const CELL = 48;              // collision grid
const STORE_KEY = 'petalwake.treasures.v1';
const SHARED = [...SKY_UNIFORMS, 'uTime', 'uLightTex', 'uHeightTex', 'uSplatTex', 'uWorld', 'uNoiseTex', 'uWind', 'uWakeTex', 'uWake', 'uShadowTex', 'uShadowMat', 'uShadowOn'];

const rand = (a = 1, b) => (b === undefined ? Math.random() * a : a + Math.random() * (b - a));
function rng(seed) {
  let s = (seed * 2654435761) >>> 0 || 1;
  return () => { s = (s + 0x6d2b79f5) >>> 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
function vnoise(x, z, seed) {
  const h = (ix, iz) => { let n = (Math.imul(ix, 374761393) + Math.imul(iz, 668265263) + Math.imul(seed | 0, 2246822519)) | 0; n = Math.imul(n ^ (n >>> 13), 1274126177); return ((n ^ (n >>> 16)) >>> 0) / 4294967296; };
  const ix = Math.floor(x), iz = Math.floor(z), fx = x - ix, fz = z - iz;
  const ux = fx * fx * (3 - 2 * fx), uz = fz * fz * (3 - 2 * fz);
  const a = h(ix, iz), b = h(ix + 1, iz), c = h(ix, iz + 1), d = h(ix + 1, iz + 1);
  return (a + (b - a) * ux) * (1 - uz) + (c + (d - c) * ux) * uz;
}

export class Places {
  static async load(renderer, terrain, base = './assets') {
    const sets = await Promise.all(SETS.map(async (name) => {
      try {
        const res = await fetch(`${base}/places/${name}.json`);
        if (!res.ok) return [];
        const data = await res.json();
        return Array.isArray(data.places) ? data.places : [];
      } catch (e) {
        console.warn(`places: could not read ${name}.json (${e.message})`);
        return [];
      }
    }));
    return new Places(renderer, terrain, base, sets.flat());
  }

  constructor(renderer, terrain, base, defs) {
    this.renderer = renderer;
    this.terrain = terrain;
    this.base = `${base}/places/`;
    this.group = new THREE.Group();        // the places themselves: goes in the world scene
    this.overlay = new THREE.Group();      // treasure glints: drawn sharp, after the motion blur
    this.grid = new Map();
    this.models = new Map();               // url -> promise of { prims, info }
    this.loader = new GLTFLoader();
    this.game = null;
    this.journal = null;
    this.time = 0;

    const found = this._restore();
    const seen = new Set();
    this.list = [];
    for (const def of defs) {
      if (!def || !def.id || !Array.isArray(def.pos) || seen.has(def.id)) continue;
      seen.add(def.id);
      const t = def.treasure && Array.isArray(def.treasure.pos) ? def.treasure : null;
      this.list.push({
        def, id: def.id, state: 0, ready: null,
        pos: new THREE.Vector3().fromArray(def.pos), radius: def.radius || 40,
        group: null, meshes: [], flora: [], shed: [], drift: (def.drift || []).map((d) => ({ ...d, acc: 0 })),
        treasure: t && {
          def: t, id: t.id || def.id, pos: new THREE.Vector3().fromArray(t.pos), found: found.has(t.id || def.id),
          tint: t.color || [1.0, 0.86, 0.62], alive: 0, taken: 0, mesh: null, phase: (def.pos[0] * 0.37 + def.pos[2] * 0.21) % 6.283,
        },
        visited: false,
      });
    }
    this.byId = new Map(this.list.map((p) => [p.id, p]));
    this._buildGlints();
  }

  get total() { return this.list.filter((p) => p.treasure).length; }
  get count() { return this.list.filter((p) => p.treasure && p.treasure.found).length; }

  /** Wire up what a pickup needs (particles, sound, the HUD) and let the broom bump into the pieces. */
  bind(game) {
    this.game = game;
    try { this.journal = new Journal(this, game); } catch (e) { console.warn('places: no journal', e); }
    const f = game.flight;
    if (f) {
      const solid = f.props;
      const self = this;
      f.props = { collide(pos, radius, out) { const a = solid ? solid.collide(pos, radius, out) : false; return self.collide(pos, radius, out) || a; } };
    }
    /** Debug: put the rider beside a place, looking at it. Resolves once its models are in. */
    game.gotoPlace = (id, dist = 60, agl = 14, bearing = 200) => {
      const pl = this.byId.get(id);
      if (!pl) return Promise.resolve(`no such place: ${id} (${[...this.byId.keys()].join(', ')})`);
      const a = (bearing * Math.PI) / 180;     // where we stand, as a compass bearing from the place
      const x = pl.pos.x + Math.sin(a) * dist, z = pl.pos.z - Math.cos(a) * dist;
      game.fly(x, z, agl, (bearing + 180) % 360, 24);
      return this.ensure(id).then(() => `${pl.def.name} [${pl.pos.toArray().map((v) => Math.round(v))}]`);
    };
  }

  // ------------------------------------------------------------------------------ persistence
  _restore() {
    try { return new Set(JSON.parse(localStorage.getItem(STORE_KEY) || '[]')); } catch { return new Set(); }
  }
  _save() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(this.list.filter((p) => p.treasure && p.treasure.found).map((p) => p.treasure.id))); } catch { /* private mode: the journal lasts the session */ }
  }
  /** Debug: forget everything that has been found. */
  reset() {
    for (const p of this.list) if (p.treasure) { p.treasure.found = false; p.treasure.taken = 0; if (p.treasure.mesh) p.treasure.mesh.visible = true; }
    this._save();
    this.journal?.refresh();
  }

  // ------------------------------------------------------------------------------ loading
  /** Load a place now (it would load by itself once the rider is near). */
  ensure(id) {
    const pl = this.byId.get(id);
    if (!pl) return Promise.reject(new Error(`no such place: ${id}`));
    if (!pl.ready) pl.ready = this._load(pl);
    return pl.ready;
  }

  _model(path) {
    const url = this.base + path;
    let m = this.models.get(url);
    if (!m) {
      m = Promise.all([
        this.loader.loadAsync(url),
        fetch(url.replace(/\.glb$/i, '.json')).then((r) => (r.ok ? r.json() : {})).catch(() => ({})),
      ]).then(([gltf, info]) => {
        gltf.scene.updateMatrixWorld(true);
        const prims = [];
        const box = new THREE.Box3();
        gltf.scene.traverse((o) => {
          if (!o.isMesh) return;
          const g = o.geometry;
          if (g.attributes.color) { g.setAttribute('aColor', g.attributes.color); g.deleteAttribute('color'); }
          if (!g.attributes.normal) g.computeVertexNormals();
          g.computeBoundingBox();
          box.union(g.boundingBox.clone().applyMatrix4(o.matrixWorld));
          const mats = Array.isArray(o.material) ? o.material : [o.material];
          for (const sm of mats) for (const t of [sm.map, sm.normalMap, sm.roughnessMap]) if (t) t.anisotropy = 8;
          prims.push({ geometry: g, matrix: o.matrixWorld.clone(), src: mats[0] });
        });
        if (!prims.length) throw new Error(`${path}: no meshes`);
        const size = box.getSize(new THREE.Vector3());
        info.height ??= Math.max(box.max.y, 0.01);
        info.radius ??= Math.max(Math.hypot(box.max.x, box.max.z), Math.hypot(box.min.x, box.min.z), 0.01);
        info.size = Math.max(size.x, size.y, size.z);
        return { prims, info, path };
      });
      this.models.set(url, m);
    }
    return m;
  }

  async _load(pl) {
    pl.state = 1;
    const def = pl.def;
    try {
      const keys = Object.keys(def.models || {});
      const loaded = {};
      await Promise.all(keys.map(async (k) => {
        try { loaded[k] = await this._model(def.models[k]); } catch (e) { console.warn(`places: ${pl.id}: model "${k}" failed (${e.message})`); }
      }));
      const group = new THREE.Group();
      group.name = pl.id;
      const keepout = [];
      this._buildItems(pl, loaded, group, keepout);
      this._buildFlora(pl, loaded, group, keepout);
      this._buildTreasure(pl, loaded, group);
      pl.group = group;
      // compile the new programs before the place is shown, so arriving does not hitch
      const g = this.game;
      if (g && g.camera && g.world && this.renderer.compileAsync) {
        try { await this.renderer.compileAsync(group, g.camera, g.world); } catch { /* it will compile on first draw */ }
      }
      this.group.add(group);
      pl.state = 2;
    } catch (e) {
      console.warn(`places: ${pl.id} failed to load`, e);
      pl.state = -1;
    }
    return pl;
  }

  _material(prim, info, kind) {
    const g = prim.geometry, sm = prim.src || {};
    const defines = {};
    const hasWind = !!g.attributes._wind;
    if (sm.map) defines.HAS_MAP = '';
    if (sm.normalMap) { defines.HAS_NORMALMAP = ''; if (!g.attributes.tangent) defines.NORMAL_DERIV = ''; }
    if (sm.roughnessMap) defines.HAS_ROUGHMAP = '';
    if (g.attributes.aColor) defines.HAS_VCOLOR = '';
    if (hasWind) defines.HAS_WIND = '';
    if (kind === 'flora') defines.FLORA = '';
    if (kind === 'gem') defines.GEM = '';
    // (generated meshes are flagged double-sided but are closed solids: like the props, draw their fronts only)
    const thin = info.thin ?? (kind === 'flora');
    if (thin) defines.THIN = '';
    if (info.cloth) defines.CLOTH = '';
    if (info.glowKey === 'amber') defines.GLOW_AMBER = ''; else if (info.glowKey === 'teal') defines.GLOW_TEAL = '';
    const glow = Array.isArray(info.glow) ? info.glow : info.glow ? [1, 1, 1, info.glow] : [1, 1, 1, 0];
    // (a vertex-coloured model carries its colour in the vertices; the material's own tint is for textured ones)
    const base = sm.color && !g.attributes.aColor ? sm.color : { r: 1, g: 1, b: 1 };
    const mat = new THREE.ShaderMaterial({
      uniforms: {
        ...shared(...SHARED),
        tMap: { value: sm.map || null }, tNormal: { value: sm.normalMap || null }, tRough: { value: sm.roughnessMap || null },
        uBase: { value: new THREE.Vector3(base.r, base.g, base.b) },
        uFoliage: { value: info.foliage ?? (hasWind ? 1 : 0) },
        uSelf: { value: (info.radius || 1) * 1.3 + 1.5 },
        uSway: { value: new THREE.Vector4(info.sway ?? 1, info.height || 1, 0, 0) },
        uCloth: { value: new THREE.Vector2(...(info.cloth || [0, 0])) },
        uGlow: { value: new THREE.Vector4(glow[0], glow[1], glow[2], glow[3] ?? 3) },
        uLod: { value: new THREE.Vector3(1e9, 1, 0) },
        uGem: { value: new THREE.Vector4(0, 0, 0, 1) },
      },
      defines, vertexShader: VERT, fragmentShader: FRAG,
      side: thin ? THREE.DoubleSide : THREE.FrontSide,
    });
    return mat;
  }

  _buildItems(pl, loaded, group, keepout) {
    const by = new Map();
    for (const it of pl.def.items || []) {
      if (!loaded[it.model] || !Array.isArray(it.pos)) continue;
      if (!by.has(it.model)) by.set(it.model, []);
      by.get(it.model).push(it);
    }
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), q2 = new THREE.Quaternion(), e = new THREE.Euler();
    const up = new THREE.Vector3(0, 1, 0), p = new THREE.Vector3(), sc = new THREE.Vector3(), tmp = new THREE.Matrix4();
    for (const [key, list] of by) {
      const { prims, info } = loaded[key];
      const leafy = prims.some((pr) => pr.geometry.attributes._wind);
      let maxS = 0;
      const mats = list.map((it) => {
        const s = Array.isArray(it.scale) ? it.scale : [it.scale ?? 1, it.scale ?? 1, it.scale ?? 1];
        const yaw = it.yaw || 0;
        const y = it.agl !== undefined ? this.terrain.heightAt(it.pos[0], it.pos[2]) + it.agl : it.pos[1];
        q.setFromAxisAngle(up, yaw);
        if (it.rot) q.multiply(q2.setFromEuler(e.set(it.rot[0] || 0, it.rot[1] || 0, it.rot[2] || 0, 'YXZ')));
        const su = Math.max(s[0], s[1], s[2]);
        maxS = Math.max(maxS, su);
        // collision discs (same transform the bake uses for the shadows)
        if (info.collide !== false) {
          const c = Math.cos(yaw), sn = Math.sin(yaw);
          const discs = info.solid || info.slabs || [];
          const shrink = info.solid ? 1 : leafy ? 0.6 : 0.92;
          for (const [lx, lz, r, y0, y1] of discs) {
            this._addDisc({ x: (lx * c + lz * sn) * su + it.pos[0], z: (-lx * sn + lz * c) * su + it.pos[2], r: r * su * shrink, y0: y + y0 * su, y1: y + y1 * su });
          }
        }
        // plants keep off the foot of it
        keepout.push([it.pos[0], it.pos[2], (info.baseRadius ?? Math.min(info.radius, 1.5)) * su * 0.9]);
        return new THREE.Matrix4().compose(p.set(it.pos[0], y, it.pos[2]), q, sc.set(s[0], s[1], s[2]));
      });
      for (const prim of prims) {
        const mat = this._material(prim, info, 'item');
        mat.uniforms.uSelf.value = info.radius * maxS * 1.3 + 1.5;
        const mesh = new THREE.InstancedMesh(prim.geometry, mat, mats.length);
        mats.forEach((m, i) => mesh.setMatrixAt(i, tmp.multiplyMatrices(m, prim.matrix)));
        mesh.instanceMatrix.needsUpdate = true;
        mesh.computeBoundingSphere();
        mesh.boundingSphere.radius += 2.5;
        mesh.renderOrder = 300;
        group.add(mesh);
        // (drawn until it is a few pixels tall: a 15 m tree to about 2 km, a lamp to 300 m)
        pl.meshes.push({ mesh, far: THREE.MathUtils.clamp(info.size * maxS * 130, 300, 2600) });
      }
    }
  }

  _buildFlora(pl, loaded, group, keepout) {
    const T = this.terrain;
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), p = new THREE.Vector3(), sc = new THREE.Vector3(), tmp = new THREE.Matrix4();
    for (const f of pl.def.flora || []) {
      const model = loaded[f.model];
      if (!model || !Array.isArray(f.center) || !(f.count > 0)) continue;
      const { prims, info } = model;
      const R = rng(f.seed ?? 1);
      const [cx, cz] = f.center, rad = f.radius || 8, inner = f.inner || 0, clump = f.clump || 0;
      const [s0, s1] = Array.isArray(f.scale) ? f.scale : [f.scale ?? 1, f.scale ?? 1];
      const n = Math.min(f.count | 0, 4000);
      const mats = [], tint = new Float32Array(n * 4), spots = [];
      for (let tries = 0; mats.length < n && tries < n * 12; tries++) {
        const a = R() * 6.2831853, rr = Math.sqrt(inner * inner + (rad * rad - inner * inner) * R());
        const x = cx + Math.cos(a) * rr, z = cz + Math.sin(a) * rr;
        const r1 = R(), r2 = R(), r3 = R(), r4 = R();
        if (clump > 0 && r1 > 1 - clump + clump * THREE.MathUtils.smoothstep(vnoise(x * 0.42, z * 0.42, f.seed | 0), 0.34, 0.62)) continue;
        const h = T.heightAt(x, z);
        if (h < 0.25 && !f.lift) continue;                                    // not in the sea
        if (!f.steep && T.normalAt(x, z, _n, 1.5).y < 0.74) continue;          // nor on a cliff face
        let blocked = false;
        for (const k of keepout) if ((x - k[0]) ** 2 + (z - k[1]) ** 2 < k[2] * k[2]) { blocked = true; break; }
        if (blocked) continue;
        const s = s0 + (s1 - s0) * Math.pow(r2, 1.35);
        q.setFromEuler(e.set((r3 - 0.5) * 0.24, R() * 6.2831853, (r4 - 0.5) * 0.24, 'YXZ'));
        mats.push(new THREE.Matrix4().compose(p.set(x, h + (f.lift || 0), z), q, sc.set(s, s, s)));
        const i = mats.length - 1, v = 0.86 + 0.28 * R(), hue = (R() - 0.5) * 0.14;
        tint[i * 4] = v * (1 + hue); tint[i * 4 + 1] = v; tint[i * 4 + 2] = v * (1 - hue); tint[i * 4 + 3] = R();
        spots.push(x, h + (f.lift || 0), z, s);
      }
      if (!mats.length) continue;
      const aTint = new THREE.InstancedBufferAttribute(tint.subarray(0, mats.length * 4), 4);
      const entry = { meshes: [], n: mats.length, cx, cz, rad, lod0: info.lod0 ?? 70 };
      for (const prim of prims) {
        // share the vertex buffers, add the per-plant tint
        const g = new THREE.BufferGeometry();
        g.setIndex(prim.geometry.index);
        for (const name in prim.geometry.attributes) g.setAttribute(name, prim.geometry.attributes[name]);
        if (!g.attributes._wind) g.setAttribute('_wind', heightWind(prim.geometry, info.height));
        g.boundingBox = prim.geometry.boundingBox; g.boundingSphere = prim.geometry.boundingSphere;
        g.setAttribute('aTint', aTint);
        const mat = this._material({ geometry: g, src: prim.src }, info, 'flora');
        const mesh = new THREE.InstancedMesh(g, mat, mats.length);
        mats.forEach((m, i) => mesh.setMatrixAt(i, tmp.multiplyMatrices(m, prim.matrix)));
        mesh.instanceMatrix.needsUpdate = true;
        mesh.computeBoundingSphere();
        mesh.boundingSphere.radius += 3 + info.height * 3;
        mesh.renderOrder = 150;
        group.add(mesh);
        entry.meshes.push(mesh);
      }
      pl.flora.push(entry);
      if (f.shed) pl.shed.push({ spots, n: mats.length, last: new Float32Array(mats.length).fill(-1e3), height: (f.shed.height ?? info.height), color: f.shed.color || [1, 1, 1], kind: f.shed.kind || 'fluff', reach: f.shed.reach ?? 3.2 });
    }
  }

  _buildTreasure(pl, loaded, group) {
    const t = pl.treasure;
    if (!t) return;
    const model = loaded[t.def.model];
    if (!model) return;
    const holder = new THREE.Group();
    const s = t.def.scale ?? 1;
    for (const prim of model.prims) {
      const mat = this._material(prim, model.info, 'gem');
      mat.uniforms.uSelf.value = 0;
      mat.uniforms.uGem.value.set(t.tint[0], t.tint[1], t.tint[2], 1);
      const mesh = new THREE.Mesh(prim.geometry, mat);
      mesh.matrixAutoUpdate = false;
      mesh.matrix.copy(prim.matrix);
      mesh.frustumCulled = false;
      mesh.renderOrder = 290;
      holder.add(mesh);
    }
    // turn about the middle of the thing, not its base
    t.half = (model.info.height || 0) * 0.5;
    t.scale = s;
    holder.visible = !t.found;
    group.add(holder);
    t.mesh = holder;
  }

  // ------------------------------------------------------------------------------ glints
  _buildGlints() {
    const items = this.list.filter((p) => p.treasure);
    const n = Math.max(items.length, 1);
    const g = new THREE.InstancedBufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 1, -1, 0, -1, 1, 0, 1, 1, 0]), 3));
    g.setIndex([0, 1, 2, 1, 3, 2]);
    this.aGem = new THREE.InstancedBufferAttribute(new Float32Array(n * 4), 4);
    this.aGem.setUsage(THREE.DynamicDrawUsage);
    const tint = new Float32Array(n * 4);
    items.forEach((p, i) => {
      p.treasure.slot = i;
      p.treasure.alive = p.treasure.found ? 0 : 1;
      this.aGem.array.set([p.treasure.pos.x, p.treasure.pos.y, p.treasure.pos.z, p.treasure.alive], i * 4);
      tint.set([...p.treasure.tint, p.treasure.phase], i * 4);
    });
    g.setAttribute('iGem', this.aGem);
    g.setAttribute('iTint', new THREE.InstancedBufferAttribute(tint, 4));
    g.instanceCount = items.length;
    const mat = new THREE.ShaderMaterial({
      uniforms: { ...shared('uTime') },
      vertexShader: GLINT_VERT, fragmentShader: GLINT_FRAG,
      transparent: true, depthWrite: false, side: THREE.DoubleSide,
      blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
      blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor,
    });
    const mesh = new THREE.Mesh(g, mat);
    mesh.frustumCulled = false;
    mesh.renderOrder = 52;
    mesh.visible = items.length > 0;
    this.overlay.add(mesh);
  }

  // ------------------------------------------------------------------------------ collision
  _addDisc(d) {
    const x0 = Math.floor((d.x - d.r - 2) / CELL), x1 = Math.floor((d.x + d.r + 2) / CELL);
    const z0 = Math.floor((d.z - d.r - 2) / CELL), z1 = Math.floor((d.z + d.r + 2) / CELL);
    for (let cz = z0; cz <= z1; cz++) for (let cx = x0; cx <= x1; cx++) {
      const k = cx * 4096 + cz;
      let a = this.grid.get(k);
      if (!a) this.grid.set(k, (a = []));
      a.push(d);
    }
  }

  /**
   * Push a point (the broom) out of any piece it has entered. Same contract as Props.collide.
   * @returns true when something was hit; `out` gets the surface normal (xz) of the last contact.
   */
  collide(pos, radius, out) {
    const a = this.grid.get(Math.floor(pos.x / CELL) * 4096 + Math.floor(pos.z / CELL));
    if (!a) return false;
    let hit = false;
    for (const d of a) {
      if (pos.y < d.y0 - radius || pos.y > d.y1 + radius) continue;
      const dx = pos.x - d.x, dz = pos.z - d.z, rr = d.r + radius;
      const l2 = dx * dx + dz * dz;
      if (l2 >= rr * rr) continue;
      const l = Math.sqrt(l2) || 1e-3;
      // skim over the top if we are nearly clear of it, otherwise slide around
      if (pos.y > d.y1 - 0.4) { pos.y = d.y1 + radius; continue; }
      pos.x = d.x + (dx / l) * rr; pos.z = d.z + (dz / l) * rr;
      out.set(dx / l, 0, dz / l);
      hit = true;
    }
    return hit;
  }

  // ------------------------------------------------------------------------------ per frame
  update(dt, flight, time) {
    this.time = time;
    const p = flight.pos, eye = U.uCamPos.value;
    const arr = this.aGem.array;
    for (const pl of this.list) {
      const c = pl.pos;
      const dR = Math.hypot(p.x - c.x, p.z - c.z);
      const dE = Math.hypot(eye.x - c.x, eye.y - c.y, eye.z - c.z);
      if (pl.state === 0 && Math.min(dR, dE) < LOAD_DIST) this.ensure(pl.id);

      // ---- the treasure: bob, turn, and wait to be flown through
      const t = pl.treasure;
      if (t) {
        const bob = Math.sin(time * 1.3 + t.phase) * 0.22;
        const y = t.pos.y + bob;
        if (!t.found) {
          const dx = p.x - t.pos.x, dy = p.y - y, dz = p.z - t.pos.z;
          if (dx * dx + dy * dy + dz * dz < PICKUP * PICKUP) this._take(pl, flight);
        }
        const want = t.found ? 0 : 1;
        if (t.alive !== want) t.alive = want > t.alive ? Math.min(1, t.alive + dt * 2) : Math.max(0, t.alive - dt * 3.5);
        const o = t.slot * 4;
        arr[o + 1] = y; arr[o + 3] = t.alive;
        if (t.mesh) {
          if (t.found) t.taken += dt;
          // taken: it spins up, swells and is gone
          const k = t.found ? Math.max(0, 1 - t.taken / 0.45) : 1;
          t.mesh.visible = k > 0 && dE < 900;
          if (t.mesh.visible) {
            const s = t.scale * (t.found ? k * (1 + 1.4 * (1 - k)) : 1);
            t.mesh.position.set(t.pos.x, y, t.pos.z);
            t.mesh.rotation.set(Math.sin(time * 0.7 + t.phase) * 0.16, time * (0.9 + 9 * (1 - k)) + t.phase, Math.cos(time * 0.9 + t.phase) * 0.12);
            t.mesh.scale.setScalar(s);
            t.mesh.updateMatrix();
            // sit the model so its middle is at the float point
            t.mesh.matrix.multiply(_m.makeTranslation(0, -t.half, 0));
            t.mesh.matrixAutoUpdate = false;
            t.mesh.matrixWorldNeedsUpdate = true;
          }
        }
      }
      if (pl.state !== 2) continue;

      // ---- draw only what can be seen from here; thin the plants with distance
      for (const m of pl.meshes) m.mesh.visible = dE < m.far + pl.radius;
      for (const f of pl.flora) {
        const d = Math.max(0, Math.hypot(eye.x - f.cx, eye.z - f.cz, eye.y - c.y) - f.rad);
        const show = d < 900;
        const frac = d < f.lod0 ? 1 : Math.max(Math.pow(f.lod0 / d, 1.5), 0.05);
        const n = Math.max(1, Math.ceil(f.n * frac));
        for (const mesh of f.meshes) {
          mesh.visible = show;
          mesh.count = n;
          mesh.material.uniforms.uLod.value.set(n, 1 / Math.sqrt(frac), 0);
        }
      }

      const fx = this.game && this.game.fx;
      if (!fx) continue;
      // ---- arriving: say where we are, once
      if (!pl.visited && dR < pl.radius * 0.9 && Math.abs(p.y - c.y) < 70 && this.game.state === 'play') {
        pl.visited = true;
        this.journal?.arrive(pl);
      }
      // ---- things on the air: blossom coming down, seed fluff going by
      if (dE < 260) {
        const lit = 0.3 + 0.7 * (this.game.rider ? this.game.rider.sunVis : 1);
        for (const d of pl.drift) {
          d.acc += (d.rate ?? 8) * dt * (0.5 + fx.gustAt(d.from[0], d.from[2]));
          while (d.acc >= 1) {
            d.acc -= 1;
            const a = rand(6.2831853), r = Math.sqrt(Math.random()) * (d.radius ?? 4);
            this._flake(fx, d.kind, d.color, d.from[0] + Math.cos(a) * r, d.from[1] + rand(-1, 1) * (d.spread ?? 1.2), d.from[2] + Math.sin(a) * r, rand(-0.6, 0.6), rand(-0.4, 0.5), rand(-0.6, 0.6), lit, rand(5, 9));
          }
        }
        // ---- plants that let go of their seeds when the broom tears past
        if (pl.shed.length && dR < pl.radius + 20) {
          const sp = flight.speed;
          for (const s of pl.shed) {
            const reach2 = s.reach * s.reach;
            for (let i = 0; i < s.n; i++) {
              const o = i * 4, top = s.spots[o + 1] + s.height * s.spots[o + 3];
              const dx = p.x - s.spots[o], dz = p.z - s.spots[o + 2], dy = p.y - top;
              if (dx * dx + dz * dz + dy * dy * 0.6 > reach2 * s.spots[o + 3] || time - s.last[i] < 2.5) continue;
              s.last[i] = time;
              const n = Math.round(14 + sp * 0.5);
              for (let k = 0; k < n; k++) {
                const a = rand(6.2831853), u = rand(-1, 1), rr = Math.sqrt(1 - u * u) * 0.5 * s.spots[o + 3];
                this._flake(fx, s.kind, s.color, s.spots[o] + Math.cos(a) * rr, top + u * 0.5, s.spots[o + 2] + Math.sin(a) * rr,
                  flight.vel.x * 0.25 + Math.cos(a) * rand(0.5, 3), rand(0.2, 2.5), flight.vel.z * 0.25 + Math.sin(a) * rand(0.5, 3), lit, rand(4, 8));
              }
            }
          }
        }
      }
    }
    this.aGem.needsUpdate = true;
    this.journal?.update(dt);
  }

  _flake(fx, kind, color = [1, 1, 1], x, y, z, vx, vy, vz, lit, life) {
    const v = rand(0.88, 1.1);
    if (kind === 'fluff') {
      // a seed on its parasol: a bright mote the wind and the wake carry off
      fx.sprites.spawn(x, y, z, vx, vy, vz, { type: SPR.BLOB, r: color[0] * v * 1.5, g: color[1] * v * 1.5, b: color[2] * v * 1.5, alpha: rand(0.5, 0.85), size: rand(0.07, 0.15), life, drag: 3.2, grav: 0.35, add: 0.35, wind: 1, wake: 1 });
    } else {
      fx.flakes.spawn(x, y, z, vx, vy, vz, KIND.PETAL, rand(0.10, 0.18), color[0] * v, color[1] * v, color[2] * v, life, lit, rand(0.62, 0.86));
    }
  }

  /** The broom has flown through a treasure. */
  _take(pl, flight) {
    const t = pl.treasure;
    if (!t || t.found) return;
    t.found = true;
    t.taken = 0;
    this._save();
    const g = this.game;
    if (g) {
      const fx = g.fx, x = t.pos.x, y = t.pos.y, z = t.pos.z;
      if (fx) {
        const lit = 0.3 + 0.7 * (g.rider ? g.rider.sunVis : 1);
        const c = t.tint;
        // a ring of sparks thrown outward, a slower shower that hangs and falls
        for (let i = 0; i < 90; i++) {
          const a = rand(6.2831853), u = rand(-1, 1), s = Math.sqrt(1 - u * u), sp = i < 40 ? rand(7, 13) : rand(1.5, 6);
          fx.sprites.spawn(x, y, z, Math.cos(a) * s * sp + flight.vel.x * 0.3, u * sp * 0.8 + 1.5, Math.sin(a) * s * sp + flight.vel.z * 0.3, {
            type: SPR.BLOB, r: (1.2 + c[0]) * 1.4, g: (1.2 + c[1]) * 1.3, b: (1.2 + c[2]) * 1.2, alpha: rand(0.6, 1), size: i < 40 ? rand(0.05, 0.11) : rand(0.07, 0.17),
            life: i < 40 ? rand(0.5, 1.0) : rand(1.2, 2.6), drag: i < 40 ? 3.5 : 1.6, grav: i < 40 ? 0 : 2.2, add: 1, wind: 0.2, wake: 0.6, stretch: i < 40 ? 0.03 : 0,
          });
        }
        const pal = t.def.petals || [[0.97, 0.76, 0.87], [0.97, 0.96, 0.90], c];
        for (let i = 0; i < 70; i++) {
          const a = rand(6.2831853), u = rand(-1, 1), s = Math.sqrt(1 - u * u) * rand(0.3, 1) * 7;
          const col = pal[(Math.random() * pal.length) | 0];
          this._flake(fx, 'petal', col, x, y, z, Math.cos(a) * s + flight.vel.x * 0.2, u * 5 + 2.5, Math.sin(a) * s + flight.vel.z * 0.2, lit, rand(3, 6));
        }
      }
      if (g.sound) (g.sound.treasure ? g.sound.treasure(this.count - 1) : g.sound.chime(this.count + 3));
      flight.gust = 1;
    }
    this.journal?.found(pl);
  }

  /** Debug: take a place's treasure as if the broom had flown through it. */
  collect(id) {
    const pl = this.byId.get(id);
    if (pl && this.game) this._take(pl, this.game.flight);
    return pl ? pl.treasure.def.name : null;
  }
}

const _m = new THREE.Matrix4(), _n = new THREE.Vector3();

/** A stand-in wind attribute for plants that came without one: sway grows with height. */
function heightWind(geometry, height) {
  const pos = geometry.attributes.position, n = pos.count;
  const a = new Float32Array(n * 4);
  const H = Math.max(height || geometry.boundingBox.max.y, 1e-3);
  for (let i = 0; i < n; i++) {
    const t = Math.min(Math.max(pos.getY(i) / H, 0), 1);
    a[i * 4] = t * 0.6; a[i * 4 + 1] = Math.pow(t, 1.5); a[i * 4 + 2] = 0; a[i * 4 + 3] = 1;
  }
  return new THREE.BufferAttribute(a, 4);
}

// =========================================================================================
// One material family for everything in a place. Pieces are lit exactly as the props are
// (src/world/props.js): sun through the baked light map, sky and meadow bounce, haze. Plants
// are lit as the meadow's flowers are. Defines pick the inputs a model actually has.
// =========================================================================================
const VERT = /* glsl */`
precision highp float;
#if defined(HAS_NORMALMAP) && !defined(NORMAL_DERIV)
attribute vec4 tangent;
#endif
#ifdef HAS_WIND
attribute vec4 _wind;      // r leaf flutter, g sway with height, b glow, a 1 - cloth
#endif
#ifdef HAS_VCOLOR
attribute vec4 aColor;
#endif
#ifdef FLORA
attribute vec4 aTint;      // rgb tint, a phase
#endif
uniform float uTime;
uniform vec4 uSway;        // wind response, model height (m), -, -
uniform vec2 uCloth;       // length (m), amplitude (m)
uniform vec3 uLod;         // plants shown, how much the survivors have grown, -
${NOISE_TEX}
${TERRAIN_LOOKUP}
${WIND}
varying vec3 vWorld;
varying vec3 vN;
varying vec4 vT;
varying vec2 vUv;
varying vec3 vInfo;        // height above the foot, leafiness, gust
varying vec4 vColor;
varying vec4 vExtra;       // baked sun at the foot, baked sky, glow, -
void main(){
  #ifdef USE_INSTANCING
    mat4 M = modelMatrix * instanceMatrix;
  #else
    mat4 M = modelMatrix;
  #endif
  vec3 lp = position;
  vec3 foot = M[3].xyz;
  float leaf = 0.0, gust = 0.0, glow = 0.0, ph = dot(foot.xz, vec2(0.37, 0.21));
  vec4 base = vec4(1.0);
  #ifdef FLORA
    // the patch thins with distance and what is left grows, so it keeps its colour from the air
    float shown = 1.0 - smoothstep(uLod.x * 0.8, uLod.x, float(gl_InstanceID) + 0.5);
    lp *= uLod.y * shown;
    ph += aTint.a * 6.2831853;
    base = textureLod(uLightTex, worldUV(foot.xz), 0.0);
  #endif
  vec4 wp = M * vec4(lp, 1.0);
  #ifdef HAS_WIND
    gust = windGust(foot.xz, uTime);
    leaf = _wind.r; glow = _wind.b;
    vec3 wd = vec3(uWind.x, 0.0, uWind.y);
    vec3 across = vec3(-wd.z, 0.0, wd.x);
    #ifdef FLORA
      // stems lean with the gust fronts and nod on top of that, as the meadow's flowers do
      float H = uSway.y * length(M[1].xyz) * uLod.y;
      vec2 lean = uWind.xy * (0.05 + 0.42 * gust) * uWind.z + vec2(-uWind.y, uWind.x) * sin(uTime * (2.3 + aTint.a * 1.9) + ph) * (0.05 + 0.11 * gust);
      vec4 wk = wakeAt(foot.xz);
      float whip = sin(uTime * 19.0 + ph * 7.0) * 0.45 * min(wk.z, 1.0);
      lean = lean * uSway.x + wk.xy * 0.85 * (1.0 + whip);
      float ll = length(lean), tilt = min(ll, 1.2) * _wind.g;
      vec2 ld = lean / max(ll, 1e-4);
      float up = wp.y - foot.y;
      wp.xz += ld * sin(tilt) * up;
      wp.y -= (1.0 - cos(tilt)) * up;
      vec3 fl = vec3(sin(uTime * 7.3 + wp.x * 3.1 + wp.y * 2.3), sin(uTime * 8.9 + wp.z * 3.7), sin(uTime * 6.1 + wp.x * 2.9 + wp.z * 2.1));
      wp.xyz += fl * (0.006 + 0.016 * gust) * leaf * min(H, 2.0);
    #else
      // the crown leans and recovers with each gust; leaves shiver on top of that
      float sway = (0.10 + 0.34 * gust) * (0.6 + 0.4 * sin(uTime * 1.7 + ph)) * _wind.g * uSway.x;
      wp.xyz += wd * sway * 0.9 + across * sin(uTime * 1.1 + ph * 1.7) * 0.10 * _wind.g * uSway.x;
      vec3 fl = vec3(sin(uTime * 7.3 + wp.x * 3.1 + wp.y * 2.3), sin(uTime * 8.9 + wp.z * 3.7), sin(uTime * 6.1 + wp.x * 2.9 + wp.z * 2.1));
      wp.xyz += fl * (0.018 + 0.05 * gust) * leaf;
      // the broom's slipstream thrashes the branches
      vec4 wk = wakeAt(wp.xz);
      wp.xz += wk.xy * 0.35 * _wind.g;
      #ifdef CLOTH
        // cloth streams downwind: a wave runs out along it, bigger toward the free end and in the
        // gusts; in the lulls it hangs
        float cloth = 1.0 - _wind.a;
        float s = cloth * uCloth.x;
        float w1 = sin(s * 1.5 - uTime * (4.6 + 3.2 * gust) + ph);
        float w2 = sin(s * 2.6 - uTime * (7.4 + 3.6 * gust) + ph * 2.3);
        float amp = uCloth.y * (0.45 + 0.9 * gust) * pow(cloth, 1.15);
        wp.xyz += across * (w1 * 0.64 + w2 * 0.17) * amp + vec3(0.0, 1.0, 0.0) * (w2 * 0.18 + w1 * 0.16) * amp;
        wp.y -= cloth * cloth * uCloth.x * 0.30 * (1.0 - gust);
        wp.xz += wk.xy * 0.9 * cloth;
        leaf = max(leaf, cloth * 0.55);
      #endif
    #endif
  #endif
  vWorld = wp.xyz;
  mat3 R = mat3(M);
  vN = normalize(R * normal);
  #if defined(HAS_NORMALMAP) && !defined(NORMAL_DERIV)
    vT = vec4(normalize(R * tangent.xyz), tangent.w);
  #else
    vT = vec4(1.0, 0.0, 0.0, 1.0);
  #endif
  vUv = uv;
  vInfo = vec3(wp.y - foot.y, leaf, gust);
  #ifdef HAS_VCOLOR
    vColor = aColor;
  #else
    vColor = vec4(1.0);
  #endif
  #ifdef FLORA
    vColor.rgb *= aTint.rgb;
  #endif
  vExtra = vec4(base.r, base.g, glow, 0.0);
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const FRAG = /* glsl */`
precision highp float;
uniform float uTime;
#ifdef HAS_MAP
uniform sampler2D tMap;
#endif
#ifdef HAS_NORMALMAP
uniform sampler2D tNormal;
#endif
#ifdef HAS_ROUGHMAP
uniform sampler2D tRough;
#endif
uniform vec3 uBase;
uniform float uFoliage;
uniform float uSelf;       // how far up-sun to step to get clear of our own baked shadow
uniform vec4 uGlow;        // tint, strength: light the thing gives off where its glow weight says so
uniform vec4 uGem;         // treasure: rim tint, fade
varying vec3 vWorld;
varying vec3 vN;
varying vec4 vT;
varying vec2 vUv;
varying vec3 vInfo;
varying vec4 vColor;
varying vec4 vExtra;
${NOISE}
${ATMOSPHERE}
${CLOUD_SHADOW}
${TERRAIN_LOOKUP}
${SHADOW}
void main(){
  vec3 alb = vColor.rgb * uBase;
  #ifdef HAS_MAP
    alb *= texture(tMap, vUv).rgb;
  #endif
  vec3 V = normalize(uCamPos - vWorld);
  vec3 N = normalize(vN);
  #ifdef THIN
    if (!gl_FrontFacing) N = -N;
  #endif
  #ifdef HAS_NORMALMAP
    vec3 nt = texture(tNormal, vUv).xyz * 2.0 - 1.0;
    #ifdef NORMAL_DERIV
      // the file carries no tangents (they are a third of its size): take the frame from how
      // position and uv change across the pixel
      vec3 q0 = dFdx(vWorld), q1 = dFdy(vWorld);
      vec2 st0 = dFdx(vUv), st1 = dFdy(vUv);
      vec3 q1p = cross(q1, N), q0p = cross(N, q0);
      vec3 T = q1p * st0.x + q0p * st1.x, B = q1p * st0.y + q0p * st1.y;
      float det = max(dot(T, T), dot(B, B));
      float tsc = det == 0.0 ? 0.0 : inversesqrt(det);
      N = normalize(T * (tsc * nt.x) - B * (tsc * nt.y) + N * nt.z);
    #else
      vec3 T = normalize(vT.xyz - N * dot(vT.xyz, N)), B = cross(N, T) * vT.w;
      N = normalize(T * nt.x + B * nt.y + N * nt.z);
    #endif
  #endif
  float rough = 0.8;
  #ifdef HAS_ROUGHMAP
    rough = texture(tRough, vUv).g;
  #endif
  float leaf = clamp(vInfo.y, 0.0, 1.0) * uFoliage;
  float glow = clamp(vExtra.z, 0.0, 1.0);
  vec3 col;
  #ifdef FLORA
    // small plants: thin, lit from both sides, glowing when the sun is behind them (as the meadow's are)
    float sun = vExtra.x * cloudShadow(vWorld.xz, uTime) * riderShadow(vWorld);
    float ndl = dot(N, uSunDir);
    float dif = saturate(ndl * 0.5 + 0.5);
    float back = pow(saturate(dot(V, -uSunDir) * 0.5 + 0.5), 3.0) * leaf;
    float foot = smoothstep(-0.05, 0.45, vInfo.x);
    col = alb * uSunColor * (dif + back * 0.9) * sun;
    col += alb * mix(uAmbGround, uAmbSky, N.y * 0.5 + 0.5) * (0.55 + 0.45 * vExtra.y) * mix(0.60, 1.0, foot) * mix(0.85, 1.25, leaf);
  #else
    vec4 light = texture(uLightTex, worldUV(vWorld.xz));
    // The baked map already holds this piece's own shadow on the ground beneath it, so it reads
    // the terrain's shadow from a little up-sun of itself, and climbs out of it with height.
    vec2 upSun = normalize(uSunDir.xz) * (uSelf + vInfo.x * 0.6);
    float baked = max(texture(uLightTex, worldUV(vWorld.xz + upSun)).r, smoothstep(4.0, 14.0, vInfo.x) * light.r);
    float sun = baked * cloudShadow(vWorld.xz, uTime) * riderShadow(vWorld);
    float ndl = dot(N, uSunDir);
    // leaves pass light through and scatter it around; stone does not
    alb *= mix(1.0, 1.75, leaf);
    float dif = mix(saturate(ndl), saturate(ndl * 0.55 + 0.45), leaf);
    float foot = smoothstep(-0.2, 1.6, vInfo.x);                       // contact shade where it meets the ground
    #ifdef GEM
      foot = 1.0;
    #endif
    float ao = mix(0.55, 1.0, foot) * mix(1.0, 0.6 + 0.4 * saturate(N.y * 0.5 + 0.7), leaf);
    vec3 amb = mix(uAmbGround, uAmbSky, N.y * 0.5 + 0.5) * ao * 1.15;
    // the sunlit meadow throws warm green light back up into every face that looks its way
    amb += uSunColor * vec3(0.17, 0.23, 0.08) * 0.30 * saturate(0.62 - N.y * 0.62) * light.g * foot;
    col = alb * (uSunColor * dif * sun + amb);
    // sun pouring through the crown
    float back = pow(saturate(dot(V, -uSunDir) * 0.5 + 0.5), 2.0) * leaf;
    col += alb * uSunColor * vec3(0.85, 1.0, 0.40) * (0.10 + 0.55 * back) * sun;
    vec3 H = normalize(uSunDir + V);
    float a = max(rough * rough, 0.03);
    float ndh = saturate(dot(N, H));
    float D = a * a / (3.14159 * pow(ndh * ndh * (a * a - 1.0) + 1.0, 2.0));
    col += uSunColor * sun * saturate(ndl) * min(D, 30.0) * 0.04 * (1.0 - leaf);
    #ifdef GEM
      // a treasure carries a little light of its own, and a bright rim, so it reads in any shade
      float rim = pow(1.0 - saturate(dot(N, V)), 2.4);
      col += alb * 0.55 + uGem.rgb * rim * 1.6 + uSunColor * min(D, 60.0) * 0.05 * saturate(ndl);
    #endif
  #endif
  #ifdef GLOW_AMBER
    // lamp glass: the warm bright parts of the texture give off light
    glow = max(glow, smoothstep(0.28, 0.58, alb.r - alb.b) * smoothstep(0.42, 0.75, alb.r));
  #endif
  #ifdef GLOW_TEAL
    // sea glass: lit from within
    glow = max(glow, smoothstep(0.10, 0.28, min(alb.g, alb.b) - alb.r));
  #endif
  col += alb * uGlow.rgb * (uGlow.a * glow);
  col = applyAtmosphere(col, vWorld);
  gl_FragColor = vec4(col, 1.0);
}
`;

// The glint: a small star that turns, breathes and flares, so a treasure catches the eye from a
// couple of hundred metres without a beam to give it away.
const GLINT_VERT = /* glsl */`
precision highp float;
attribute vec4 iGem;       // xyz, alive (1) .. taken (0)
attribute vec4 iTint;      // rgb, phase
uniform float uTime;
varying vec2 vUv;
varying vec4 vTint;
varying vec3 vK;           // alive, distance, flare
void main(){
  vec3 toCam = cameraPosition - iGem.xyz;
  float d = length(toCam);
  // stand a little toward the eye so the thing itself does not hide its own light
  vec3 c = iGem.xyz + toCam / max(d, 1e-3) * min(0.9, d * 0.4);
  vec4 mv = viewMatrix * vec4(c, 1.0);
  float ph = iTint.a;
  float flare = pow(max(sin(uTime * 1.9 + ph * 3.0), 0.0), 24.0);
  // (close to, the thing itself can be seen: the star shrinks to a sparkle on it)
  float size = (1.25 + 0.18 * sin(uTime * 2.7 + ph) + 0.9 * flare) * (1.0 + min(d, 520.0) * 0.0085) * mix(0.42, 1.0, smoothstep(9.0, 70.0, d));
  mv.xy += position.xy * size;
  vUv = position.xy;
  vTint = iTint;
  vK = vec3(iGem.w, d, flare);
  gl_Position = projectionMatrix * mv;
}
`;
const GLINT_FRAG = /* glsl */`
precision highp float;
uniform float uTime;
varying vec2 vUv;
varying vec4 vTint;
varying vec3 vK;
void main(){
  float r = length(vUv);
  float core = exp(-r * r * 70.0) * 2.6;
  float halo = exp(-r * r * 7.0) * 0.42;
  float a = atan(vUv.y, vUv.x) + uTime * 0.22 + vTint.a;
  // a four-pointed star, with a fainter one turned between its arms
  float rays = pow(abs(cos(a * 2.0)), 40.0) * exp(-r * 2.6) * (0.9 + 1.6 * vK.z);
  rays += pow(abs(sin(a * 2.0)), 60.0) * exp(-r * 4.6) * 0.45;
  float v = (core + halo + rays) * (1.0 - smoothstep(0.8, 1.0, r));
  v *= vK.x * smoothstep(1.2, 4.5, vK.y) * (1.0 - 0.8 * smoothstep(420.0, 1300.0, vK.y)) * mix(0.5, 1.0, smoothstep(9.0, 60.0, vK.y));
  vec3 col = mix(vec3(1.0, 0.97, 0.90), vTint.rgb, clamp(r * 2.4, 0.0, 1.0));
  gl_FragColor = vec4(col * v * 1.5, v);
}
`;
