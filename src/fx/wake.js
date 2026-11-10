// The wake field: a world-space texture that scrolls with the rider and holds what the broom's
// vortices are doing to the surface below. Grass, flowers, trees and the water all read it.
//   xy = lean of vegetation (the wind over the ground, in lean units), z = agitation 0..1,
//   w  = foam on water: 1 just churned, falling slowly as it ages.
//
// Two passes a frame:
//   1. wind  - the vortex trail is drawn as a strip; each fragment works out the wind over the
//              ground under that cross-section of the wake (two cores and their images).
//   2. state - vegetation follows that wind with a little lag and springs back; foam is laid,
//              drifts, frays and fades.
import * as THREE from 'three';
import { U } from '../core/ctx.js';
import { RIBBON_VERT, RIBBON_WIND } from './vortex.js';

const LEAN = 0.105;       // lean per m/s of wind: a 10 m/s gale lays the blades nearly flat
const FOAM_TAU = 9.0;     // seconds for foam freshness to fall by 1/e (the water shaders age it from this)

const tri = (() => {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 3, -1, 0, -1, 3, 0]), 3));
  return g;
})();

export class Wake {
  constructor(renderer, vortex, size = 1024, extent = 512) {
    this.renderer = renderer;
    this.vortex = vortex;
    this.size = size;
    this.extent = extent;
    this.texel = extent / size;
    const opt = { type: THREE.HalfFloatType, format: THREE.RGBAFormat, depthBuffer: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, wrapS: THREE.ClampToEdgeWrapping, wrapT: THREE.ClampToEdgeWrapping };
    this.a = new THREE.WebGLRenderTarget(size, size, opt);
    this.b = new THREE.WebGLRenderTarget(size, size, opt);
    this.vel = new THREE.WebGLRenderTarget(size, size, opt);
    this.center = new THREE.Vector2(1e9, 1e9);
    this.prevGround = new THREE.Vector2();
    this.hasPrev = false;
    this.cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

    // ---- pass 1: wind over the ground from the vortex trail
    this.velMat = new THREE.ShaderMaterial({
      uniforms: { uCenter: { value: new THREE.Vector2() }, uExtent: { value: extent }, uTime: U.uTime },
      vertexShader: RIBBON_VERT,
      fragmentShader: /* glsl */`
        precision highp float;
        ${RIBBON_WIND}
        void main(){ gl_FragColor = groundWind(); }`,
      depthTest: false, depthWrite: false, side: THREE.DoubleSide, transparent: true,
      blending: THREE.CustomBlending, blendEquation: THREE.AddEquation,
      blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor,
    });
    const strip = new THREE.Mesh(vortex.ribbon, this.velMat);
    strip.frustumCulled = false;
    this.velScene = new THREE.Scene();
    this.velScene.add(strip);

    // ---- pass 2: the state the world reads
    this.mat = new THREE.ShaderMaterial({
      uniforms: {
        tPrev: { value: null },
        tVel: { value: this.vel.texture },
        uShift: { value: new THREE.Vector2() },
        uRate: { value: new THREE.Vector4() },   // lean rise, lean fall, agitation keep, foam keep
        uA: { value: new THREE.Vector2() },
        uB: { value: new THREE.Vector2() },
        uSplat: { value: new THREE.Vector4() },  // foam radius, agitation, foam, gale foam
        uFoam: { value: new THREE.Vector2() },   // drift per m/s of wind (uv), -
        uCenter: { value: new THREE.Vector2() },
        uExtent: { value: extent },
      },
      vertexShader: /* glsl */`varying vec2 vUv; void main(){ vUv = position.xy * 0.5 + 0.5; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
      fragmentShader: /* glsl */`
        precision highp float;
        varying vec2 vUv;
        uniform sampler2D tPrev, tVel;
        uniform vec2 uShift, uA, uB, uCenter, uFoam;
        uniform vec4 uRate, uSplat;
        uniform float uExtent;
        vec4 prevAt(vec2 uv){
          vec2 e = min(uv, 1.0 - uv);
          return texture(tPrev, uv) * step(0.0, min(e.x, e.y));
        }
        void main(){
          vec2 uv = vUv + uShift;
          vec4 v = texture(tVel, vUv);
          vec4 p = prevAt(uv);
          float wind = length(v.xy);

          // foam only ages (the water shaders turn its freshness into churn, lace, then flecks) and
          // creeps a little with the wind while the vortices are over it. It is not blurred: that
          // would thin a narrow track out long before its time.
          p.w = (wind > 0.5 ? prevAt(uv - v.xy * uFoam.x).w : p.w) * uRate.w;

          // vegetation leans with the wind at once and springs back more slowly
          vec2 target = v.xy * ${LEAN.toFixed(3)};
          float tl = length(target);
          target *= min(1.0, 1.75 / max(tl, 1e-4));
          float rising = step(dot(p.xy, p.xy), dot(target, target));
          p.xy = mix(p.xy, target, mix(uRate.y, uRate.x, rising));
          // agitation: how hard things are being thrashed (and pressed down under the downwash)
          float ag = clamp(wind / 12.0 + max(-v.z, 0.0) / 8.0, 0.0, 1.25);
          p.z = max(p.z * uRate.z, ag);

          // the broom itself skimming water: a churned track right under it
          vec2 world = uCenter + (vUv - 0.5) * uExtent;
          vec2 pa = world - uA, ba = uB - uA;
          float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-6), 0.0, 1.0);
          float d = length(pa - ba * h);
          // (its edge wanders, so the track is not a ruled line)
          float rad = uSplat.x * (0.72 + 0.20 * sin(world.x * 1.31 + world.y * 0.73) + 0.16 * sin(world.x * 0.47 - world.y * 1.93));
          float ff = 1.0 - smoothstep(rad * 0.2, rad, d);
          p.w = max(p.w, ff * uSplat.z);
          p.z = max(p.z, ff * uSplat.y);
          // and the vortices' wind tearing the surface to either side
          p.w = max(p.w, clamp((wind - 6.0) / 9.0, 0.0, 1.0) * uSplat.w);
          gl_FragColor = p;
        }
      `,
      depthTest: false, depthWrite: false,
    });
    this.quad = new THREE.Mesh(tri, this.mat);
    this.quad.frustumCulled = false;
    this.scene = new THREE.Scene();
    this.scene.add(this.quad);
    U.uWake.value.set(0, 0, 1 / extent, FOAM_TAU);
  }

  /**
   * Call after the vortex simulation has stepped.
   * @param flight Flight state (pos, vel, agl, overWater, speed)
   */
  update(dt, flight) {
    const u = this.mat.uniforms;
    // snap the window to whole texels so the history does not blur as it scrolls
    const cx = Math.round(flight.pos.x / this.texel) * this.texel;
    const cz = Math.round(flight.pos.z / this.texel) * this.texel;
    const fresh = this.center.x > 1e8;
    if (fresh) this.center.set(cx, cz);
    u.uShift.value.set((cx - this.center.x) / this.extent, (cz - this.center.y) / this.extent);
    if (fresh) u.uShift.value.set(10, 10);   // sample outside the old window: clears the history
    this.center.set(cx, cz);
    u.uCenter.value.copy(this.center);
    this.velMat.uniforms.uCenter.value.copy(this.center);

    u.uRate.value.set(1 - Math.exp(-dt / 0.05), 1 - Math.exp(-dt / 0.42), Math.exp(-dt / 1.2), Math.exp(-dt / FOAM_TAU));
    u.uFoam.value.set(0.06 * dt / this.extent, 0);

    const gx = flight.pos.x, gz = flight.pos.z;
    if (!this.hasPrev) { this.prevGround.set(gx, gz); this.hasPrev = true; }
    // the broom churns the water only when it is skimming; faster = harder
    const near = THREE.MathUtils.clamp(1 - (flight.agl - 1.1) / 9.5, 0, 1);
    const sp = THREE.MathUtils.clamp(flight.speed / 33, 0.3, 2.2);
    const k = Math.pow(near, 1.6) * sp;
    u.uA.value.copy(this.prevGround);
    u.uB.value.set(gx, gz);
    u.uSplat.value.set(1.5 + flight.agl * 0.3 + sp * 0.35, Math.min(1, 1.1 * k), flight.overWater ? Math.min(1, k * 1.15) : 0, 0.30);
    this.prevGround.set(gx, gz);

    const r = this.renderer;
    r.setRenderTarget(this.vel);
    r.setClearColor(0x000000, 0);
    r.render(this.velScene, this.cam);
    u.tPrev.value = this.a.texture;
    r.setRenderTarget(this.b);
    r.render(this.scene, this.cam);
    r.setRenderTarget(null);
    r.setClearColor(0x000000, 1);
    const t = this.a; this.a = this.b; this.b = t;
    U.uWakeTex.value = this.a.texture;
    U.uWake.value.set(this.center.x, this.center.y, 1 / this.extent, FOAM_TAU);
    this.strength = k;
  }

  reset() { this.hasPrev = false; this.center.set(1e9, 1e9); }
}
