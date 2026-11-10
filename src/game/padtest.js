// Debug fixture (?padtest): three plain stone towers with a landing pad on each, and a flat-roofed
// shed to scrape along, standing in for the town until it is built. It speaks the town's
// interface - pads, heightAt(x, z) on a 0.5 m grid - so everything in game/ can be driven
// without it:
//   town.pads      [{ id, name, town, pos, radius, yaw, approach }]
//   town.heightAt  top of whatever is built at (x, z), -1e9 where nothing is
//   town.group     the meshes (added to the world scene by game/index.js)
import * as THREE from 'three';
import { shared } from '../core/ctx.js';
import { NOISE, ATMOSPHERE, CLOUD_SHADOW, SHADOW } from '../shaders/common.js';
import { SKY_UNIFORMS } from '../world/sky.js';

const RAD = Math.PI / 180;
const CELL = 0.5;
const RIM_H = 0.35, RIM_W = 0.4;

// h: height of the platform above the ground; pad: radius of clear floor;
// yaw: the way she faces once down; approach: heading flown on the way in (degrees, 0 = north)
const TOWERS = [
  { id: 'thrift', name: 'Thrift Perch', town: 'Northdown', x: 150, z: -1010, h: 12, pad: 2.6, yaw: 200, approach: 200 },
  { id: 'heron', name: 'Heron Stair', town: 'Northdown', x: 40, z: -800, h: 22, pad: 2.2, yaw: 120, approach: 300 },
  { id: 'kestrel', name: 'Kestrel Crown', town: 'Eastreach', x: 430, z: -1080, h: 34, pad: 1.8, yaw: 330, approach: 60 },
];
const SHED = { x: 330, z: -935, w: 24, d: 9, h: 6 };

export function buildPadTest(terrain) {
  const group = new THREE.Group();
  const material = stone();
  const pads = [], blocks = [];

  for (const t of TOWERS) {
    // founded on the lowest ground under it, so no side hangs in the air
    const rTop = t.pad + RIM_W + 0.45, rShaft = rTop - 0.8, rBase = rShaft + 0.7;
    let base = Infinity;
    for (let a = 0; a < 8; a++) base = Math.min(base, terrain.heightAt(t.x + Math.cos(a * 0.785) * rBase, t.z + Math.sin(a * 0.785) * rBase));
    const floor = Math.max(base, terrain.heightAt(t.x, t.z)) + t.h;
    // profile (radius, height above the floor of the platform), from the buried foot to the middle of the pad
    const H = floor - base + 3;
    const prof = [
      [rBase + 0.3, -H], [rBase, -H + 3.4], [rShaft, -H + 5.2], [rShaft, -2.2], [rTop, -0.9], [rTop, RIM_H],
      [rTop - RIM_W, RIM_H], [rTop - RIM_W, 0], [0, 0],
    ];
    const mesh = new THREE.Mesh(new THREE.LatheGeometry(prof.map(([r, y]) => new THREE.Vector2(r, y)), 40), material);
    mesh.position.set(t.x, floor, t.z);
    mesh.frustumCulled = false;
    mesh.renderOrder = 320;
    group.add(mesh);

    // what the flight model sees: a 0.5 m grid of roof heights
    const half = Math.ceil((rTop + CELL) / CELL), n = half * 2;
    const g = new Float32Array(n * n).fill(-1e9);
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
      const d = Math.hypot((i - half + 0.5) * CELL, (j - half + 0.5) * CELL);
      if (d <= rTop) g[j * n + i] = floor + (d > rTop - RIM_W ? RIM_H : 0);
    }
    blocks.push({ x0: t.x - half * CELL, z0: t.z - half * CELL, n, g });
    pads.push({
      id: t.id, name: t.name, town: t.town, pos: new THREE.Vector3(t.x, floor, t.z), radius: t.pad,
      yaw: t.yaw * RAD, approach: t.approach * RAD,
    });
  }

  {
    const s = SHED;
    let lo = Infinity, hi = -Infinity;
    for (const [dx, dz] of [[-1, -1], [1, -1], [-1, 1], [1, 1], [0, 0]]) {
      const h = terrain.heightAt(s.x + dx * s.w / 2, s.z + dz * s.d / 2);
      lo = Math.min(lo, h); hi = Math.max(hi, h);
    }
    const top = hi + s.h;
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(s.w, top - lo + 2, s.d), material);
    mesh.position.set(s.x, (top + lo - 2) / 2, s.z);
    mesh.frustumCulled = false;
    mesh.renderOrder = 320;
    group.add(mesh);
    const nx = Math.round(s.w / CELL), nz = Math.round(s.d / CELL), n = Math.max(nx, nz);
    const g = new Float32Array(n * n).fill(-1e9);
    for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) g[j * n + i] = top;
    blocks.push({ x0: s.x - s.w / 2, z0: s.z - s.d / 2, n, g });
  }

  return {
    test: true,
    pads,
    group,
    heightAt(x, z) {
      let top = -1e9;
      for (const b of blocks) {
        const i = Math.floor((x - b.x0) / CELL), j = Math.floor((z - b.z0) / CELL);
        if (i < 0 || j < 0 || i >= b.n || j >= b.n) continue;
        const h = b.g[j * b.n + i];
        if (h > top) top = h;
      }
      return top;
    },
  };
}

/** Coursed stone, lit by the same sun, sky and haze as the land; the rider's shadow falls on it. */
function stone() {
  return new THREE.ShaderMaterial({
    side: THREE.DoubleSide,
    uniforms: { ...shared(...SKY_UNIFORMS, 'uTime', 'uShadowTex', 'uShadowMat', 'uShadowOn') },
    vertexShader: /* glsl */`
      varying vec3 vWorld;
      varying vec3 vLocal;
      void main(){
        vec4 wp = modelMatrix * vec4(position, 1.0);
        vWorld = wp.xyz; vLocal = position;
        gl_Position = projectionMatrix * viewMatrix * wp;
      }`,
    fragmentShader: /* glsl */`
      precision highp float;
      uniform float uTime;
      varying vec3 vWorld;
      varying vec3 vLocal;
      ${NOISE}
      ${ATMOSPHERE}
      ${CLOUD_SHADOW}
      ${SHADOW}
      void main(){
        vec3 N = normalize(cross(dFdx(vWorld), dFdy(vWorld)));
        if (dot(N, uCamPos - vWorld) < 0.0) N = -N;
        float flat_ = smoothstep(0.75, 0.95, N.y);
        // walls: courses of blocks, each a shade of its own; tops: worn paving
        float course = floor(vWorld.y / 0.55);
        float around = atan(vLocal.z, vLocal.x) * max(length(vLocal.xz), 1.0) + vWorld.x + vWorld.z;
        vec2 cell = vec2(floor(around / 1.1 + mod(course, 2.0) * 0.5), course);
        float joint = min(smoothstep(0.0, 0.05, fract(vWorld.y / 0.55)), smoothstep(0.0, 0.04, fract(around / 1.1 + mod(course, 2.0) * 0.5)));
        vec3 wall = mix(vec3(0.50, 0.46, 0.40), vec3(0.66, 0.62, 0.55), hash12(cell)) * mix(0.72, 1.0, joint);
        float rr = length(vLocal.xz);
        vec3 paving = mix(vec3(0.60, 0.57, 0.52), vec3(0.72, 0.69, 0.63), hash12(floor(vWorld.xz / 0.8))) * mix(0.8, 1.0, smoothstep(0.0, 0.05, fract(rr / 0.8)));
        vec3 alb = mix(wall, paving, flat_);
        alb *= 0.9 + 0.2 * vnoise(vWorld.xz * 0.7 + vWorld.y * 0.9);
        float sun = cloudShadow(vWorld.xz, uTime) * riderShadow(vWorld);
        vec3 col = alb * (uSunColor * saturate(dot(N, uSunDir)) * sun + mix(uAmbGround, uAmbSky, N.y * 0.5 + 0.5) * 1.1);
        col = applyAtmosphere(col, vWorld);
        gl_FragColor = vec4(col, 1.0);
      }`,
  });
}
