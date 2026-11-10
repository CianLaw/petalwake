// Shared state: one set of uniform objects referenced by every material, plus world constants.
import * as THREE from 'three';

export const U = {
  uTime: { value: 0 },
  uCamPos: { value: new THREE.Vector3() },
  uSunDir: { value: new THREE.Vector3(0.3, 0.6, -0.5).normalize() },
  uSunColor: { value: new THREE.Vector3(1, 0.95, 0.85) },

  // sky / atmosphere palette (linear)
  uSkyZenith: { value: new THREE.Vector3() },
  uSkyMid: { value: new THREE.Vector3() },
  uSkyHorizon: { value: new THREE.Vector3() },
  uSunHalo: { value: new THREE.Vector3() },
  uAmbSky: { value: new THREE.Vector3() },
  uAmbGround: { value: new THREE.Vector3() },
  uFog: { value: new THREE.Vector4(1.5e-4, 1 / 420, 0, 0) }, // density, falloff, -, -

  // terrain lookups
  uHeightTex: { value: null },
  uSplatTex: { value: null },
  uLightTex: { value: null },
  uTintTex: { value: null },
  uWorld: { value: new THREE.Vector4(6144, 1 / 6144, 1 / 4096, 0) }, // size, 1/size, texel(uv), lodBias

  // wind + wake
  uWind: { value: new THREE.Vector4(0.361, 0.933, 1, 0) }, // dir.xz (toward the SSE), strength, -
  uWakeTex: { value: null },
  uWake: { value: new THREE.Vector4(0, 0, 1 / 160, 0) }, // centre.xz, 1/extent, -
  uStripTex: { value: null },                            // world map: where the wake has stripped the flowers
  uRider: { value: new THREE.Vector4(0, 100, 0, 0) },   // rider position, speed
  uRiderVel: { value: new THREE.Vector3() },

  // rider shadow map
  uShadowTex: { value: null },
  uShadowMat: { value: new THREE.Matrix4() },
  uShadowOn: { value: 0 },
  // the towns' static shadow maps (world/town.js)
  uTownSh0: { value: null },
  uTownSh1: { value: null },
  uTownShM0: { value: new THREE.Matrix4() },
  uTownShM1: { value: new THREE.Matrix4() },
  uTownShP: { value: new THREE.Vector4(0, 0, 1, 1) },
  // the towns' ground masks (paving, bare earth, where nothing grows)
  uTownMask0: { value: null },
  uTownMask1: { value: null },
  uTownRect0: { value: new THREE.Vector4(0, 0, 0, 0) },
  uTownRect1: { value: new THREE.Vector4(0, 0, 0, 0) },

  // detail noise + material textures
  uNoiseTex: { value: null },
};

export const World = {
  size: 6144,
  half: 3072,
  sea: 0,
  meta: null,
};

/** Time-of-day palettes. All colours linear. */
export const ENV = {
  afternoon: {
    sunColor: [3.3, 3.0, 2.55],
    zenith: [0.050, 0.170, 0.560],
    mid: [0.135, 0.380, 0.860],
    horizon: [0.560, 0.760, 0.930],
    halo: [1.0, 0.80, 0.52],
    ambSky: [0.36, 0.52, 0.80],
    ambGround: [0.20, 0.23, 0.14],
    fog: [1.35e-4, 1 / 420],
  },
};

export function applyEnv(name) {
  const e = ENV[name];
  U.uSunColor.value.fromArray(e.sunColor);
  U.uSkyZenith.value.fromArray(e.zenith);
  U.uSkyMid.value.fromArray(e.mid);
  U.uSkyHorizon.value.fromArray(e.horizon);
  U.uSunHalo.value.fromArray(e.halo);
  U.uAmbSky.value.fromArray(e.ambSky);
  U.uAmbGround.value.fromArray(e.ambGround);
  U.uFog.value.set(e.fog[0], e.fog[1], 0, 0);
}

/** Pick the shared uniforms a material needs. */
export function shared(...names) {
  const o = {};
  for (const n of names) {
    if (!U[n]) throw new Error(`unknown shared uniform ${n}`);
    o[n] = U[n];
  }
  return o;
}
