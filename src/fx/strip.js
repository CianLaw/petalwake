// Where the wake has been, the flowers have lost petals - most along the middle of the track,
// fewer and fewer toward its edges, and more of them the faster the broom went by.
//
// A map of the whole island (1.5 m a texel) holds, for every spot, the share of its petals that
// are gone. The vortex trail is drawn into it every frame as the same ribbon the wake field uses.
// Each cross-section of the wake stamps a soft bell across the track - a core with a broad, faint
// skirt, so there is no edge to it, only flowers thinning out:
//   - its depth follows the wind the vortices drive over the ground there (their swirl over their
//     height), so a slow pass thins the flowers a little, a cruise takes about half from the middle
//     of the track, and a sprint leaves the middle bare;
//   - its width grows with the swirl too, so a fast pass also reaches further out;
//   - the stronger of the two vortices (the outside one in a turn) takes more on its side, the
//     strength gusts along the trail, and tufts hold on here and there.
// The map keeps the most that has ever been taken from a spot: a second pass at the same speed
// finds nothing left to take, a faster one takes the difference. Nothing grows back.
//
// Flowers read the map and drop their petals one by one as the value climbs (meadow.js); the
// ground loses its flower tint to match (terrain.js); and the emitters lift only the petals a pass
// is actually taking (windfx.js, through the coarse copy kept here).
import * as THREE from 'three';
import { U, World } from '../core/ctx.js';
import { RIBBON_VERT, VORTEX } from './vortex.js';

const SIZE = 4096;         // texels across the island
const CELL = 2;            // metres: cell of the CPU copy
const SKIRT = 0.3, SKIRT_W = 2.3;   // share of the bell that is its skirt, and how many times wider the skirt is
const GW0 = 22;            // wind over the ground (m/s) that takes about two thirds of the petals
const GEXP = 1.6;          // how sharply the share taken rises with that wind
const BRUSH = 0.35;        // extra share the broom itself knocks off when it skims through the heads
const SETTLE = 0.35;       // seconds before a stretch of trail counts as done (in the CPU copy)

const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

/** Width (m) of the core of the bell a wake of swirl k, its cores h above the ground, leaves across its track. */
export function stripWidth(k, h) { return 0.4 + 0.42 * Math.sqrt(Math.max(k, 0)) + 0.2 * h; }

/**
 * Share of the petals one pass takes at a spot `lat` metres off the middle of its track.
 * k = swirl of the vortices, h = their height above the ground, rc2 = their core radius squared,
 * axg = speed of the air dragged along under the broom (it is this that says the broom is close).
 */
export function stripAmount(k, h, lat, rc2 = 0.12, axg = 0) {
  const gw = 2 * k * h / (h * h + rc2);
  const peak = 1 - Math.exp(-Math.pow(gw / GW0, GEXP));
  const q = (lat * lat) / (stripWidth(k, h) ** 2);
  const v = peak * ((1 - SKIRT) * Math.exp(-q) + SKIRT * Math.exp(-q / (SKIRT_W * SKIRT_W)));
  const brush = Math.exp(-(lat * lat) / 0.81) * (1 - smooth(1.7, 3.4, h)) * Math.min(axg * 0.1, 1) * BRUSH;
  return 1 - (1 - v) * (1 - brush);
}

export class Strip {
  constructor(renderer, vortex) {
    this.renderer = renderer;
    this.vortex = vortex;
    this.rt = new THREE.WebGLRenderTarget(SIZE, SIZE, {
      format: THREE.RedFormat, type: THREE.UnsignedByteType, depthBuffer: false,
      minFilter: THREE.LinearMipmapLinearFilter, magFilter: THREE.LinearFilter, generateMipmaps: true,
      wrapS: THREE.ClampToEdgeWrapping, wrapT: THREE.ClampToEdgeWrapping, anisotropy: 4,
    });
    this.cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this.mat = new THREE.ShaderMaterial({
      uniforms: { uCenter: { value: new THREE.Vector2(0, 0) }, uExtent: { value: World.size }, uNoiseTex: U.uNoiseTex },
      vertexShader: RIBBON_VERT,
      // (the same sums as stripAmount() above)
      fragmentShader: /* glsl */`
        precision highp float;
        uniform sampler2D uNoiseTex;
        varying float vLat;
        varying vec2 vXZ;
        varying vec4 vCore, vParm, vDir;
        void main(){
          float ym = 0.5 * (vCore.x + vCore.z), h = 0.5 * (vCore.y + vCore.w);
          float lat = vLat - ym;
          // the stronger vortex takes more on its side
          float k = vParm.x * (1.0 + vDir.w * sign(lat) * smoothstep(0.0, 0.8, abs(lat)));
          float gw = 2.0 * k * h / (h * h + vParm.y);
          float peak = 1.0 - exp(-pow(gw / ${GW0.toFixed(1)}, ${GEXP.toFixed(2)}));
          float sigma = 0.4 + 0.42 * sqrt(max(k, 0.0)) + 0.2 * h;
          float q = lat * lat / (sigma * sigma);
          float v = peak * (${(1 - SKIRT).toFixed(2)} * exp(-q) + ${SKIRT.toFixed(2)} * exp(-q / ${(SKIRT_W * SKIRT_W).toFixed(2)}));
          float brush = exp(-lat * lat / 0.81) * (1.0 - smoothstep(1.7, 3.4, h)) * min(vParm.z * 0.1, 1.0) * ${BRUSH.toFixed(2)};
          v = 1.0 - (1.0 - v) * (1.0 - brush);
          // patchy: tufts a metre or three across hold on, or go early
          float n = texture(uNoiseTex, vXZ * (5.0 / 256.0)).r * 0.6 + texture(uNoiseTex, vXZ * (17.0 / 256.0) + 0.37).g * 0.4;
          v *= 0.62 + 0.76 * n;
          v *= 1.0 - smoothstep(0.75, 1.0, abs(vLat) / vParm.w);
          gl_FragColor = vec4(clamp(v, 0.0, 1.0));
        }`,
      depthTest: false, depthWrite: false, side: THREE.DoubleSide, transparent: true,
      // keep the most that has ever been taken
      blending: THREE.CustomBlending, blendEquation: THREE.MaxEquation,
      blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor,
    });
    const ribbon = new THREE.Mesh(vortex.ribbon, this.mat);
    ribbon.frustumCulled = false;
    this.scene = new THREE.Scene();
    this.scene.add(ribbon);

    renderer.setRenderTarget(this.rt);
    renderer.setClearColor(0x000000, 0);
    renderer.clear();
    renderer.setRenderTarget(null);
    renderer.setClearColor(0x000000, 1);
    U.uStripTex.value = this.rt.texture;

    // coarse copy on the CPU, for the emitters
    this.n = Math.round(World.size / CELL);
    this.grid = new Uint8Array(this.n * this.n);
    this._stamp = 0;
  }

  /** Share of the petals already gone at a point: 0 untouched .. 1 none left. */
  at(x, z) {
    const n = this.n;
    const ix = ((x + World.half) / CELL) | 0, iz = ((z + World.half) / CELL) | 0;
    if (ix < 0 || iz < 0 || ix >= n || iz >= n) return 0;
    return this.grid[iz * n + ix] * (1 / 255);
  }

  /**
   * Share of the petals the pass now under way will take `off` metres to the side of its track.
   * Read off the stretch of trail a moment behind the broom, where the wake has wound up to full
   * strength - which is what the map is about to be stamped with.
   */
  passAmount(off) {
    const V = this.vortex, N = VORTEX.N;
    let r = Math.min(V.count - 1, 1);
    while (r < V.count - 1 && V.age[(V.head - r + N) % N] < 0.28) r++;
    const i = (V.head - r + N) % N;
    const k = V.k[i] * V.gk[i] * (1 + V.asym[i] * Math.sign(off) * smooth(0, 0.8, Math.abs(off)));
    return stripAmount(k, 0.5 * (V.hl[i] + V.hr[i]), off, V.rc2[i], V.ax[i] * 0.3 * V.gk[i]);
  }

  /** Share of the petals the stretch of trail at rank r takes (or has taken) at a point. */
  stationAmount(r, x, z) {
    const V = this.vortex, i = (V.head - r + VORTEX.N) % VORTEX.N;
    const lat = (x - V.ox[i]) * V.lx[i] + (z - V.oz[i]) * V.lz[i] - 0.5 * (V.yl[i] + V.yr[i]);
    const k = V.k[i] * V.gk[i] * (1 + V.asym[i] * Math.sign(lat) * smooth(0, 0.8, Math.abs(lat)));
    return stripAmount(k, 0.5 * (V.hl[i] + V.hr[i]), lat, V.rc2[i], V.ax[i] * 0.3 * V.gk[i]);
  }

  /** Call after the vortex simulation has stepped. */
  update(dt) {
    const V = this.vortex, r = this.renderer;
    // ---- the map: at most sixty stamps a second (each one regenerates the map's mipmaps)
    this._stamp += dt;
    if (this._stamp >= 1 / 60) {
      this._stamp = 0;
      if (V.ribbon.drawRange.count > 0) {
        const keepAuto = r.autoClear;
        r.autoClear = false;                     // this map accumulates
        r.setRenderTarget(this.rt);
        r.render(this.scene, this.cam);
        r.setRenderTarget(null);
        r.autoClear = keepAuto;
      }
    }

    // ---- the CPU copy. A stretch of trail is entered once it has had a moment to do its work,
    // so the emitters still find petals to lift right behind the broom on a first pass.
    const n = this.n, grid = this.grid, N = VORTEX.N;
    for (let rk = 1; rk < V.count; rk++) {
      const i = (V.head - rk + N) % N;
      if (V.age[i] < SETTLE || V.age[i] > SETTLE + 1.2) continue;
      const kg = V.k[i] * V.gk[i], h = 0.5 * (V.hl[i] + V.hr[i]);
      if (kg / h < 0.5) continue;
      const sigma = stripWidth(kg, h), ym = 0.5 * (V.yl[i] + V.yr[i]);
      for (let s = -7; s <= 7; s++) {
        const lat = s * 0.5 * sigma;
        const x = V.ox[i] + V.lx[i] * (ym + lat), z = V.oz[i] + V.lz[i] * (ym + lat);
        const ix = ((x + World.half) / CELL) | 0, iz = ((z + World.half) / CELL) | 0;
        if (ix < 0 || iz < 0 || ix >= n || iz >= n) continue;
        const v = (this.stationAmount(rk, x, z) * 255) | 0, j = iz * n + ix;
        if (v > grid[j]) grid[j] = v;
      }
    }
  }
}
