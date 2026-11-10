// Props: the lighthouse, standing stones, boulders and wind-bent trees. Instanced, lit by the same
// sun / sky / haze as the land, shadowed through the baked light map (which also carries the
// shadows they throw on the ground). Each prop is also a stack of discs the broom can bump into.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { shared } from '../core/ctx.js';
import { NOISE, NOISE_TEX, ATMOSPHERE, CLOUD_SHADOW, TERRAIN_LOOKUP, WIND, SHADOW } from '../shaders/common.js';
import { SKY_UNIFORMS } from './sky.js';

const CELL = 48;

export class Props {
  static async load(base = './assets') {
    const placements = await fetch(`${base}/terrain/props.json`).then((r) => r.json());
    const loader = new GLTFLoader();
    const loaded = await Promise.all(Object.keys(placements).map(async (name) => {
      const [gltf, info] = await Promise.all([loader.loadAsync(`${base}/models/${name}.glb`), fetch(`${base}/models/${name}.json`).then((r) => r.json())]);
      return { name, gltf, info, list: placements[name] };
    }));
    return new Props(loaded);
  }

  constructor(loaded) {
    this.group = new THREE.Group();
    this.grid = new Map();
    this.counts = {};
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), up = new THREE.Vector3(0, 1, 0), p = new THREE.Vector3(), sc = new THREE.Vector3();
    for (const { name, gltf, info, list } of loaded) {
      let src = null;
      gltf.scene.traverse((o) => { if (o.isMesh && !src) src = o; });
      const g = src.geometry, sm = src.material;
      const hasWind = !!g.attributes._wind;
      for (const t of [sm.map, sm.normalMap, sm.roughnessMap]) if (t) { t.anisotropy = 8; }
      const mat = new THREE.ShaderMaterial({
        uniforms: {
          ...shared(...SKY_UNIFORMS, 'uTime', 'uLightTex', 'uHeightTex', 'uSplatTex', 'uWorld', 'uNoiseTex', 'uWind', 'uWakeTex', 'uWake', 'uShadowTex', 'uShadowMat', 'uShadowOn'),
          tMap: { value: sm.map }, tNormal: { value: sm.normalMap }, tRough: { value: sm.roughnessMap || sm.map },
          uHasRough: { value: sm.roughnessMap ? 1 : 0 },
          uFoliage: { value: hasWind ? 1 : 0 },
          uSelf: { value: info.radius * 1.3 + 1.5 },
        },
        defines: hasWind ? { HAS_WIND: '' } : {},
        vertexShader: VERT, fragmentShader: FRAG,
      });
      const mesh = new THREE.InstancedMesh(g, mat, list.length);
      list.forEach(([x, y, z, yaw, s], i) => {
        q.setFromAxisAngle(up, yaw);
        m4.compose(p.set(x, y, z), q, sc.set(s, s, s));
        mesh.setMatrixAt(i, m4);
        // collision discs (same transform the bake used for the shadows)
        const c = Math.cos(yaw), sn = Math.sin(yaw);
        for (const [lx, lz, r, y0, y1] of info.slabs) {
          this._addDisc({ x: (lx * c + lz * sn) * s + x, z: (-lx * sn + lz * c) * s + z, r: r * s * (hasWind ? 0.6 : 0.92), y0: y + y0 * s, y1: y + y1 * s });
        }
      });
      mesh.instanceMatrix.needsUpdate = true;
      mesh.frustumCulled = false;
      mesh.renderOrder = 300;
      this.group.add(mesh);
      this.counts[name] = list.length;
      if (name === 'lighthouse' && list.length) this._beacon(list[0], info);
    }
  }

  /** The lamp: a warm glint in the lantern room that flares each time the lens sweeps past the eye. */
  _beacon([x, y, z, , s], info) {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 1, -1, 0, -1, 1, 0, 1, 1, 0]), 3));
    g.setIndex([0, 1, 2, 1, 3, 2]);
    const mat = new THREE.ShaderMaterial({
      uniforms: { ...shared('uTime'), uPos: { value: new THREE.Vector3(x, y + info.height * 0.835 * s, z) } },
      vertexShader: /* glsl */`
        uniform vec3 uPos; uniform float uTime;
        varying vec2 vUv; varying float vFlash;
        void main(){
          vec3 toCam = cameraPosition - uPos;
          float d = length(toCam);
          // sit just outside the glass so the lantern itself does not hide the glow
          vec3 c = uPos + toCam / d * 2.1;
          vec4 mv = viewMatrix * vec4(c, 1.0);
          float sweep = cos(uTime * 0.8 - atan(toCam.z, toCam.x));
          vFlash = pow(max(sweep, 0.0), 48.0);
          mv.xy += position.xy * (2.2 + 3.8 * vFlash) * (1.0 + min(d, 900.0) * 0.004);
          vUv = position.xy;
          gl_Position = projectionMatrix * mv;
        }`,
      fragmentShader: /* glsl */`
        precision highp float;
        varying vec2 vUv; varying float vFlash;
        void main(){
          float r = length(vUv);
          float core = exp(-r * r * 46.0) * 2.4;
          float halo = exp(-r * r * 5.0) * 0.30;
          float streak = exp(-vUv.y * vUv.y * 420.0) * exp(-vUv.x * vUv.x * 3.5) * 1.3 * vFlash;
          float v = (core + halo) * (0.22 + 1.5 * vFlash) + streak;
          v *= 1.0 - smoothstep(0.75, 1.0, r);
          gl_FragColor = vec4(vec3(1.0, 0.80, 0.46) * v, v);
        }`,
      transparent: true, depthWrite: false,
      blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
      blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor,
    });
    const m = new THREE.Mesh(g, mat);
    m.frustumCulled = false;
    m.renderOrder = 48;
    this.overlay = new THREE.Group();
    this.overlay.add(m);
  }

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
   * Push a point (the broom) out of any prop it has entered.
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
}

const VERT = /* glsl */`
precision highp float;
attribute vec4 tangent;
#ifdef HAS_WIND
attribute vec4 _wind;      // r leaf flutter, g sway with height
#endif
uniform float uTime;
${NOISE_TEX}
${WIND}
varying vec3 vWorld;
varying vec3 vN;
varying vec4 vT;
varying vec2 vUv;
varying vec3 vInfo;        // height above the foot, leafiness, gust
void main(){
  mat4 M = modelMatrix * instanceMatrix;
  vec4 wp = M * vec4(position, 1.0);
  vec3 foot = M[3].xyz;
  float leaf = 0.0, gust = 0.0;
  #ifdef HAS_WIND
    gust = windGust(foot.xz, uTime);
    leaf = _wind.r;
    vec3 wd = vec3(uWind.x, 0.0, uWind.y);
    float ph = dot(foot.xz, vec2(0.37, 0.21));
    // the crown leans and recovers with each gust; leaves shiver on top of that
    float sway = (0.10 + 0.34 * gust) * (0.6 + 0.4 * sin(uTime * 1.7 + ph)) * _wind.g;
    wp.xyz += wd * sway * 0.9 + vec3(-wd.z, 0.0, wd.x) * sin(uTime * 1.1 + ph * 1.7) * 0.10 * _wind.g;
    vec3 fl = vec3(sin(uTime * 7.3 + wp.x * 3.1 + wp.y * 2.3), sin(uTime * 8.9 + wp.z * 3.7), sin(uTime * 6.1 + wp.x * 2.9 + wp.z * 2.1));
    wp.xyz += fl * (0.018 + 0.05 * gust) * leaf;
    // the broom's slipstream thrashes the branches
    vec4 wk = wakeAt(wp.xz);
    wp.xz += wk.xy * 0.35 * _wind.g;
  #endif
  vWorld = wp.xyz;
  mat3 R = mat3(M);
  vN = normalize(R * normal);
  vT = vec4(normalize(R * tangent.xyz), tangent.w);
  vUv = uv;
  vInfo = vec3(wp.y - foot.y, leaf, gust);
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const FRAG = /* glsl */`
precision highp float;
uniform float uTime;
uniform sampler2D tMap;
uniform sampler2D tNormal;
uniform sampler2D tRough;
uniform float uHasRough;
uniform float uFoliage;
uniform float uSelf;       // how far up-sun to step to get clear of our own baked shadow
varying vec3 vWorld;
varying vec3 vN;
varying vec4 vT;
varying vec2 vUv;
varying vec3 vInfo;
${NOISE}
${ATMOSPHERE}
${CLOUD_SHADOW}
${TERRAIN_LOOKUP}
${SHADOW}
void main(){
  vec3 alb = texture(tMap, vUv).rgb;
  vec3 nt = texture(tNormal, vUv).xyz * 2.0 - 1.0;
  vec3 N = normalize(vN), T = normalize(vT.xyz - N * dot(vT.xyz, N)), B = cross(N, T) * vT.w;
  N = normalize(T * nt.x + B * nt.y + N * nt.z);
  vec3 V = normalize(uCamPos - vWorld);
  float rough = mix(0.8, texture(tRough, vUv).g, uHasRough);
  float leaf = vInfo.y * uFoliage;

  vec4 light = texture(uLightTex, worldUV(vWorld.xz));
  // the baked map holds the ground's shadows; a tall prop climbs out of a low one
  // The baked map already holds this prop's own shadow on the ground beneath it, so the prop reads
  // the terrain's shadow from a little up-sun of itself, and climbs out of it with height.
  vec2 upSun = normalize(uSunDir.xz) * (uSelf + vInfo.x * 0.6);
  float baked = max(texture(uLightTex, worldUV(vWorld.xz + upSun)).r, smoothstep(4.0, 14.0, vInfo.x) * light.r);
  float sun = baked * cloudShadow(vWorld.xz, uTime) * riderShadow(vWorld);
  float ndl = dot(N, uSunDir);
  // leaves pass light through and scatter it around; stone does not
  alb *= mix(1.0, 1.75, leaf);
  float dif = mix(saturate(ndl), saturate(ndl * 0.55 + 0.45), leaf);
  float foot = smoothstep(-0.2, 1.6, vInfo.x);                       // contact shade where it meets the ground
  float ao = mix(0.55, 1.0, foot) * mix(1.0, 0.6 + 0.4 * saturate(N.y * 0.5 + 0.7), leaf);
  vec3 amb = mix(uAmbGround, uAmbSky, N.y * 0.5 + 0.5) * ao * 1.15;
  // the sunlit meadow throws warm green light back up into every face that looks its way
  amb += uSunColor * vec3(0.17, 0.23, 0.08) * 0.30 * saturate(0.62 - N.y * 0.62) * light.g * foot;
  vec3 col = alb * (uSunColor * dif * sun + amb);
  // sun pouring through the crown
  float back = pow(saturate(dot(V, -uSunDir) * 0.5 + 0.5), 2.0) * leaf;
  col += alb * uSunColor * vec3(0.85, 1.0, 0.40) * (0.10 + 0.55 * back) * sun;
  vec3 H = normalize(uSunDir + V);
  float a = max(rough * rough, 0.03);
  float ndh = saturate(dot(N, H));
  float D = a * a / (3.14159 * pow(ndh * ndh * (a * a - 1.0) + 1.0, 2.0));
  col += uSunColor * sun * saturate(ndl) * min(D, 30.0) * 0.04 * (1.0 - leaf);
  col = applyAtmosphere(col, vWorld);
  gl_FragColor = vec4(col, 1.0);
}
`;
