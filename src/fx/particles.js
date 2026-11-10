// CPU-simulated, GPU-instanced particles drawn in the sharp layer (after motion blur):
//   Flakes  - tumbling petals, leaves and pebbles (oriented quads / rock impostors)
//   Sprites - spray, mist, dust, sand and wind streaks (soft camera-facing, velocity-stretched)
//   Ribbon  - the trails the bristles draw in the air
import * as THREE from 'three';
import { U, shared } from '../core/ctx.js';
import { NOISE, ATMOSPHERE } from '../shaders/common.js';
import { SKY_UNIFORMS } from '../world/sky.js';

export const KIND = { PETAL: 0, LEAF: 1, PEBBLE: 2 };
export const SPR = { BLOB: 0, DROP: 1, PUFF: 2, STREAK: 3 };

// ======================================================================================= flakes
export class Flakes {
  constructor(max = 12000) {
    this.max = max;
    this.count = 0;
    this.pos = new Float32Array(max * 3);
    this.vel = new Float32Array(max * 3);
    this.quat = new Float32Array(max * 4);
    this.spin = new Float32Array(max * 3);
    this.col = new Float32Array(max * 3);
    this.life = new Float32Array(max);
    this.maxLife = new Float32Array(max);
    this.size = new Float32Array(max);
    this.kind = new Uint8Array(max);
    this.state = new Uint8Array(max);   // 0 flying, 1 settled
    this.seed = new Float32Array(max);
    this.aspect = new Float32Array(max);
    this.lit = new Float32Array(max);

    // quad grid 3 x 5 so the petal can cup and curl
    const W = 2, L = 4;
    const p = [], idx = [];
    for (let j = 0; j <= L; j++) for (let i = 0; i <= W; i++) p.push((i / W) * 2 - 1, (j / L) * 2 - 1, 0);
    for (let j = 0; j < L; j++) for (let i = 0; i < W; i++) {
      const a = j * (W + 1) + i, b = a + 1, c = a + W + 1, d = c + 1;
      idx.push(a, b, c, b, d, c);
    }
    const g = new THREE.InstancedBufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(p), 3));
    g.setIndex(idx);
    const mk = (n) => { const a = new THREE.InstancedBufferAttribute(new Float32Array(max * n), n); a.setUsage(THREE.DynamicDrawUsage); return a; };
    this.aPos = mk(4); this.aQuat = mk(4); this.aCol = mk(4); this.aMisc = mk(4);
    g.setAttribute('iPos', this.aPos); g.setAttribute('iQuat', this.aQuat); g.setAttribute('iCol', this.aCol); g.setAttribute('iMisc', this.aMisc);
    g.instanceCount = 0;
    this.geo = g;
    this.material = new THREE.ShaderMaterial({
      uniforms: { ...shared(...SKY_UNIFORMS, 'uTime') },
      vertexShader: /* glsl */`
        precision highp float;
        attribute vec4 iPos, iQuat, iCol, iMisc;   // misc: kind, aspect, seed, sun
        varying vec2 vUv;
        varying vec3 vN;
        varying vec3 vWorld;
        varying vec4 vCol;
        varying vec4 vMisc;
        vec3 rot(vec3 v, vec4 q){ return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v); }
        void main(){
          vec2 uv = position.xy;
          float size = iPos.w, kind = iMisc.x;
          vec3 P, n;
          if (kind > 1.5){
            // pebble: a lit impostor facing the eye
            vec3 right = vec3(viewMatrix[0][0], viewMatrix[1][0], viewMatrix[2][0]);
            vec3 up = vec3(viewMatrix[0][1], viewMatrix[1][1], viewMatrix[2][1]);
            float a = iMisc.z * 6.2831853;
            vec2 r = vec2(uv.x * cos(a) - uv.y * sin(a), uv.x * sin(a) + uv.y * cos(a));
            P = iPos.xyz + (right * r.x + up * r.y * iMisc.y) * size * 0.5;
            n = normalize(cameraPosition - P);
          } else {
            // cupped, slightly curled petal / leaf
            float cup = kind < 0.5 ? 0.42 : 0.16;
            float curl = (iMisc.z - 0.5) * 0.9;
            vec3 lp = vec3(uv.x * 0.5 * iMisc.y, uv.y * 0.5, cup * (uv.x * uv.x) * iMisc.y * 0.5 + curl * uv.y * uv.y * 0.22) * size;
            vec3 ln = normalize(vec3(-2.0 * cup * uv.x, -curl * uv.y * 0.9, 1.0));
            P = iPos.xyz + rot(lp, iQuat);
            n = rot(ln, iQuat);
          }
          vUv = uv; vN = n; vWorld = P; vCol = iCol; vMisc = iMisc;
          // the wake carries petals right past the lens: let them thin out instead of filling the frame
          vCol.a *= smoothstep(0.30, 1.10, distance(iPos.xyz, cameraPosition));
          gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0);
        }
      `,
      fragmentShader: /* glsl */`
        precision highp float;
        varying vec2 vUv;
        varying vec3 vN;
        varying vec3 vWorld;
        varying vec4 vCol;
        varying vec4 vMisc;
        ${NOISE}
        ${ATMOSPHERE}
        void main(){
          float kind = vMisc.x;
          vec3 V = normalize(uCamPos - vWorld);
          vec3 N = normalize(vN);
          vec3 alb = vCol.rgb;
          float alpha;
          float thin = 1.0;
          if (kind < 0.5){
            // petal: narrow claw at the base, broad rounded blade, a nick at the tip
            float y = clamp(vUv.y * 0.5 + 0.5, 0.0, 1.0);
            float w = sin(pow(y, 0.72) * 3.14159) * (0.50 + 0.50 * y);
            w *= 1.0 - 0.22 * smoothstep(0.82, 1.0, y) * (0.5 + 0.5 * cos(vUv.x * 11.0));
            float e = abs(vUv.x) - w;
            float fw = max(fwidth(e), 0.02);
            alpha = 1.0 - smoothstep(-fw, fw, e);
            alb *= mix(0.74, 1.08, y);                       // deeper colour toward the claw
            alb *= 0.93 + 0.09 * cos(vUv.x * 16.0);          // veins
          } else if (kind < 1.5){
            float y = clamp(vUv.y * 0.5 + 0.5, 0.0, 1.0);
            float w = sin(y * 3.14159) * 0.82;
            float e = abs(vUv.x) - w;
            float fw = max(fwidth(e), 0.03);
            alpha = 1.0 - smoothstep(-fw, fw, e);
            alb *= 0.85 + 0.25 * y;
          } else {
            // pebble: chipped silhouette, fake sphere shading
            float a = atan(vUv.y, vUv.x);
            float r = length(vUv);
            float edge = 0.80 + 0.14 * sin(a * 3.0 + vMisc.z * 30.0) + 0.06 * sin(a * 7.0 + vMisc.z * 70.0);
            float fw = max(fwidth(r), 0.03);
            alpha = 1.0 - smoothstep(edge - fw, edge + fw, r);
            vec3 right = normalize(cross(vec3(0.0, 1.0, 0.0), V));
            vec3 up = cross(V, right);
            float z = sqrt(max(1.0 - r * r / (edge * edge), 0.0));
            N = normalize(right * vUv.x + up * vUv.y + V * z);
            thin = 0.0;
            alb *= 0.8 + 0.4 * hash12(floor(vUv * 5.0) + vMisc.z * 91.0);
          }
          alpha *= vCol.a;
          if (alpha < 0.02) discard;
          if (thin > 0.5 && dot(N, V) < 0.0) N = -N;
          float sun = vMisc.w;
          float ndl = dot(N, uSunDir);
          float dif = thin > 0.5 ? saturate(ndl * 0.5 + 0.5) : saturate(ndl);
          // thin things glow when the sun is behind them
          float back = thin * pow(saturate(dot(V, -uSunDir) * 0.5 + 0.5), 3.0) * (kind < 0.5 ? 1.0 : 0.6);
          vec3 col = alb * uSunColor * (dif + back * 0.95) * sun;
          col += alb * mix(uAmbGround, uAmbSky, N.y * 0.5 + 0.5) * (thin > 0.5 ? 1.15 : 0.9);
          col = applyAtmosphere(col, vWorld);
          gl_FragColor = vec4(col, alpha);
        }
      `,
      side: THREE.DoubleSide,
      alphaToCoverage: true,
    });
    this.mesh = new THREE.Mesh(g, this.material);
    this.mesh.frustumCulled = false;
    this.mesh.renderOrder = 20;
  }

  /** Returns the slot index, or -1 when full. */
  spawn(x, y, z, vx, vy, vz, kind, size, r, g, b, life, lit = 1, aspect = 0.6) {
    if (this.count >= this.max) return -1;
    const i = this.count++;
    const i3 = i * 3, i4 = i * 4;
    this.pos[i3] = x; this.pos[i3 + 1] = y; this.pos[i3 + 2] = z;
    this.vel[i3] = vx; this.vel[i3 + 1] = vy; this.vel[i3 + 2] = vz;
    // random orientation + spin
    const u1 = Math.random(), u2 = Math.random() * 6.2831853, u3 = Math.random() * 6.2831853;
    const a = Math.sqrt(1 - u1), b2 = Math.sqrt(u1);
    this.quat[i4] = a * Math.sin(u2); this.quat[i4 + 1] = a * Math.cos(u2); this.quat[i4 + 2] = b2 * Math.sin(u3); this.quat[i4 + 3] = b2 * Math.cos(u3);
    const sp = kind === KIND.PEBBLE ? 9 : 7;
    this.spin[i3] = (Math.random() - 0.5) * sp; this.spin[i3 + 1] = (Math.random() - 0.5) * sp; this.spin[i3 + 2] = (Math.random() - 0.5) * sp;
    this.col[i3] = r; this.col[i3 + 1] = g; this.col[i3 + 2] = b;
    this.life[i] = 0; this.maxLife[i] = life; this.size[i] = size; this.kind[i] = kind; this.state[i] = 0;
    this.seed[i] = Math.random(); this.aspect[i] = aspect; this.lit[i] = lit;
    return i;
  }

  _kill(i) {
    const j = --this.count;
    if (i === j) return;
    const i3 = i * 3, j3 = j * 3, i4 = i * 4, j4 = j * 4;
    for (let k = 0; k < 3; k++) { this.pos[i3 + k] = this.pos[j3 + k]; this.vel[i3 + k] = this.vel[j3 + k]; this.spin[i3 + k] = this.spin[j3 + k]; this.col[i3 + k] = this.col[j3 + k]; }
    for (let k = 0; k < 4; k++) this.quat[i4 + k] = this.quat[j4 + k];
    this.life[i] = this.life[j]; this.maxLife[i] = this.maxLife[j]; this.size[i] = this.size[j]; this.kind[i] = this.kind[j];
    this.state[i] = this.state[j]; this.seed[i] = this.seed[j]; this.aspect[i] = this.aspect[j]; this.lit[i] = this.lit[j];
  }

  /**
   * @param env { wind(x,y,z,out), wake(x,y,z,out) -> strength, surface(x,z) }
   */
  update(dt, t, env) {
    const { pos, vel, quat, spin, life, maxLife, kind, state, seed } = this;
    const w = env._w || (env._w = [0, 0, 0]);
    const wk = env._wk || (env._wk = [0, 0, 0, 0]);
    for (let i = 0; i < this.count; i++) {
      life[i] += dt;
      if (life[i] >= maxLife[i]) { this._kill(i); i--; continue; }
      if (state[i]) continue;
      const i3 = i * 3, i4 = i * 4, k = kind[i];
      let x = pos[i3], y = pos[i3 + 1], z = pos[i3 + 2];
      let vx = vel[i3], vy = vel[i3 + 1], vz = vel[i3 + 2];
      env.wind(x, y, z, w);
      // ---- the broom's wake: the simulated vortices swirl the air, draw it toward their cores
      // and drag a bubble of it along behind the rider. Light things simply go where that air goes.
      const ws = env.wake(x, y, z, wk);
      const open = 1 - wk[3];             // the pocket of air riding with the broom shuts the wind out
      let ax, ay, az, drag, grav;
      if (k === KIND.PEBBLE) {
        ax = w[0] * open + wk[0]; ay = w[1] * open + wk[1]; az = w[2] * open + wk[2];
        drag = 0.35 + Math.min(ws, 14) * 0.06; grav = 9.8;
      } else {
        // No two petals fly alike. From its one seed each gets its own weight (how closely it
        // follows the air, how fast it falls), its own grip on the wake (the loose ones lag and
        // are flung wide), and its own flutter - how hard and how fast it side-slips as it tumbles.
        const sd = seed[i], h1 = (sd * 7.31) % 1, h2 = (sd * 13.7) % 1, h3 = (sd * 29.3) % 1;
        const grip = 0.94 + 0.08 * h3;
        ax = w[0] * open + wk[0] * grip; ay = w[1] * open + wk[1] * grip; az = w[2] * open + wk[2] * grip;
        const s = sd * 50, l = life[i], f1 = 4.4 + 5.2 * h2;
        const tb = (0.45 + Math.min(ws, 14) * 0.10) * (0.45 + 1.35 * h1);
        ax += Math.sin(s + l * f1) * tb; az += Math.cos(s * 1.3 + l * f1 * 0.81) * tb; ay += Math.sin(s * 0.7 + l * f1 * 1.38) * tb * 0.6;
        // light enough to follow the air closely: terminal fall is only grav / drag ~ 0.3 - 1.2 m/s
        if (k === KIND.LEAF) { drag = 9 + 9 * h1; grav = 12; } else { drag = 13 + 20 * Math.pow(sd, 1.4); grav = 9 + 6 * h2; }
      }
      const e = 1 - Math.exp(-drag * dt);
      vx += (ax - vx) * e; vy += (ay - vy) * e; vz += (az - vz) * e;
      vy -= grav * dt;
      x += vx * dt; y += vy * dt; z += vz * dt;
      // tumble: faster in fast air
      const rel = Math.min(Math.hypot(vx - w[0], vy - w[1], vz - w[2]) * 0.22 + 0.35, 3.5);
      const ox = spin[i3] * rel * dt * 0.5, oy = spin[i3 + 1] * rel * dt * 0.5, oz = spin[i3 + 2] * rel * dt * 0.5;
      const qx = quat[i4], qy = quat[i4 + 1], qz = quat[i4 + 2], qw = quat[i4 + 3];
      let nxq = qx + ox * qw + oy * qz - oz * qy;
      let nyq = qy - ox * qz + oy * qw + oz * qx;
      let nzq = qz + ox * qy - oy * qx + oz * qw;
      let nwq = qw - ox * qx - oy * qy - oz * qz;
      const nl = 1 / Math.sqrt(nxq * nxq + nyq * nyq + nzq * nzq + nwq * nwq);
      quat[i4] = nxq * nl; quat[i4 + 1] = nyq * nl; quat[i4 + 2] = nzq * nl; quat[i4 + 3] = nwq * nl;
      // ---- landing
      const gy = env.surface(x, z);
      if (gy - y > 1.2) {
        // flew into a wall: back out and rebound off it
        x -= vx * dt * 1.5; z -= vz * dt * 1.5;
        vx *= -0.35; vz *= -0.35;
      } else if (y < gy + 0.03) {
        if (k === KIND.PEBBLE && vy < -2.5 && gy > 0.3) {
          y = gy + 0.03; vy = -vy * 0.32; vx *= 0.55; vz *= 0.55;
        } else if (gy <= 0.3 && k === KIND.PEBBLE) {
          this._kill(i); i--; continue;     // plop
        } else if (ws > 2.5 && k !== KIND.PEBBLE) {
          // the wake is still raking the ground here: skitter along it instead of settling
          y = gy + 0.04 + Math.random() * 0.05;
          if (vy < 0) vy = -vy * 0.25 + ws * 0.05;
          // (jostled as they go, so they do not pile up where the downwash splits on the ground)
          const jk = 1.2 + ws * 0.22;
          vx += (Math.random() - 0.5) * jk; vz += (Math.random() - 0.5) * jk;
        } else {
          y = gy + 0.03; state[i] = 1; vx = vy = vz = 0;
          maxLife[i] = Math.min(maxLife[i], life[i] + 2.2);
        }
      }
      pos[i3] = x; pos[i3 + 1] = y; pos[i3 + 2] = z;
      vel[i3] = vx; vel[i3 + 1] = vy; vel[i3 + 2] = vz;
    }
    this._upload();
  }

  _upload() {
    const n = this.count;
    const P = this.aPos.array, Q = this.aQuat.array, C = this.aCol.array, M = this.aMisc.array;
    for (let i = 0; i < n; i++) {
      const i3 = i * 3, i4 = i * 4;
      const l = this.life[i], ml = this.maxLife[i];
      const fadeIn = Math.min(1, l * 9), fadeOut = Math.min(1, (ml - l) * (this.state[i] ? 0.6 : 1.4));
      P[i4] = this.pos[i3]; P[i4 + 1] = this.pos[i3 + 1]; P[i4 + 2] = this.pos[i3 + 2];
      P[i4 + 3] = this.size[i] * (0.4 + 0.6 * fadeIn);
      Q[i4] = this.quat[i4]; Q[i4 + 1] = this.quat[i4 + 1]; Q[i4 + 2] = this.quat[i4 + 2]; Q[i4 + 3] = this.quat[i4 + 3];
      C[i4] = this.col[i3]; C[i4 + 1] = this.col[i3 + 1]; C[i4 + 2] = this.col[i3 + 2]; C[i4 + 3] = fadeOut;
      M[i4] = this.kind[i]; M[i4 + 1] = this.aspect[i]; M[i4 + 2] = this.seed[i]; M[i4 + 3] = this.lit[i];
    }
    for (const a of [this.aPos, this.aQuat, this.aCol, this.aMisc]) { a.clearUpdateRanges(); a.addUpdateRange(0, n * 4); a.needsUpdate = true; }
    this.geo.instanceCount = n;
    this.mesh.visible = n > 0;
  }
}

// ======================================================================================= sprites
export class Sprites {
  constructor(depthUniform, max = 6000) {
    this.max = max;
    this.count = 0;
    this.pos = new Float32Array(max * 3);
    this.vel = new Float32Array(max * 3);
    this.col = new Float32Array(max * 3);
    this.life = new Float32Array(max);
    this.maxLife = new Float32Array(max);
    this.size0 = new Float32Array(max);
    this.size1 = new Float32Array(max);
    this.alpha = new Float32Array(max);
    this.type = new Uint8Array(max);
    this.grav = new Float32Array(max);
    this.drag = new Float32Array(max);
    this.stretch = new Float32Array(max);
    this.add = new Float32Array(max);
    this.seed = new Float32Array(max);
    this.windK = new Float32Array(max);
    this.wakeK = new Float32Array(max);

    const g = new THREE.InstancedBufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 1, -1, 0, -1, 1, 0, 1, 1, 0]), 3));
    g.setIndex([0, 1, 2, 1, 3, 2]);
    const mk = (n) => { const a = new THREE.InstancedBufferAttribute(new Float32Array(max * n), n); a.setUsage(THREE.DynamicDrawUsage); return a; };
    this.aPos = mk(4); this.aVel = mk(4); this.aCol = mk(4); this.aMisc = mk(4);
    g.setAttribute('iPos', this.aPos); g.setAttribute('iVel', this.aVel); g.setAttribute('iCol', this.aCol); g.setAttribute('iMisc', this.aMisc);
    g.instanceCount = 0;
    this.geo = g;
    this.camVel = new THREE.Vector3();
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        ...shared(...SKY_UNIFORMS, 'uTime', 'uNoiseTex'),
        tDepth: depthUniform,
        uCamVel: { value: this.camVel },
        uDepth: { value: new THREE.Vector3(0.3, 60000, 0) },   // near, far, reversed
        uRes: { value: new THREE.Vector2(1, 1) },
      },
      vertexShader: /* glsl */`
        precision highp float;
        attribute vec4 iPos, iVel, iCol, iMisc;   // vel.w = stretch seconds; misc: type, additive, seed, -
        uniform vec3 uCamVel;
        varying vec2 vUv;
        varying vec4 vCol;
        varying vec4 vMisc;
        varying float vViewZ;
        varying float vSize;
        varying vec3 vWorld;
        void main(){
          vec4 mv = viewMatrix * vec4(iPos.xyz, 1.0);
          vec2 uv = position.xy;
          float size = iPos.w;
          // streak along the motion as the camera sees it
          vec3 rel = (viewMatrix * vec4(iVel.xyz - uCamVel, 0.0)).xyz;
          float sl = length(rel.xy);
          vec2 axis = sl > 1e-3 ? rel.xy / sl : vec2(0.0, 1.0);
          float len = sl * iVel.w;
          vec2 perp = vec2(axis.y, -axis.x);   // right-handed with the axis, so the quad keeps its winding
          vec2 off = perp * uv.x * size * 0.5 + axis * uv.y * (size * 0.5 + len * 0.5);
          if (iVel.w <= 0.0){
            float a = iMisc.z * 6.2831853;
            off = vec2(uv.x * cos(a) - uv.y * sin(a), uv.x * sin(a) + uv.y * cos(a)) * size * 0.5;
          }
          mv.xy += off;
          vUv = uv; vCol = iCol; vMisc = iMisc; vViewZ = -mv.z;
          vSize = size;
          vWorld = iPos.xyz;
          gl_Position = projectionMatrix * mv;
        }
      `,
      fragmentShader: /* glsl */`
        precision highp float;
        varying vec2 vUv;
        varying vec4 vCol;
        varying vec4 vMisc;
        varying float vViewZ;
        varying float vSize;
        varying vec3 vWorld;
        uniform sampler2D tDepth;
        uniform sampler2D uNoiseTex;
        uniform vec3 uDepth;
        uniform vec2 uRes;
        ${NOISE}
        ${ATMOSPHERE}
        float viewZ(float d){
          return uDepth.z > 0.5 ? uDepth.x * uDepth.y / (uDepth.x + d * (uDepth.y - uDepth.x))
                                : uDepth.x * uDepth.y / (uDepth.y - d * (uDepth.y - uDepth.x));
        }
        void main(){
          float type = vMisc.x;
          float r2 = dot(vUv, vUv);
          float a;
          if (type < 0.5) a = exp(-r2 * 3.2) * (1.0 - smoothstep(0.7, 1.0, r2));                   // blob
          else if (type < 1.5){
            // droplet streak: bright bead at the head, tapering tail
            float along = vUv.y * 0.5 + 0.5;
            a = exp(-vUv.x * vUv.x * 4.5) * (1.0 - smoothstep(0.75, 1.0, vUv.x * vUv.x)) * smoothstep(0.0, 0.25, along) * pow(1.0 - smoothstep(0.55, 1.0, along), 1.0) * (0.35 + 0.65 * along);
          }
          else if (type < 2.5){
            // puff: a blob chewed by noise so it billows rather than balloons
            vec2 q = vUv * 0.5 + vMisc.z * 37.0;
            float n = texture(uNoiseTex, q * 0.42).r * 0.65 + texture(uNoiseTex, q * 1.3 + 0.3).g * 0.35;
            a = (1.0 - smoothstep(0.10, 0.92, r2 * 1.25 + (n - 0.5) * 0.7)) * (0.55 + 0.9 * n) * (1.0 - smoothstep(0.62, 0.98, r2));
          } else a = exp(-vUv.x * vUv.x * 9.0) * pow(max(1.0 - vUv.y * vUv.y, 0.0), 1.5);          // wind streak
          // soft where it meets the world
          float scene = viewZ(texture(tDepth, gl_FragCoord.xy / uRes).r);
          float soft = clamp((scene - vViewZ) / max(vMisc.w, 0.02), 0.0, 1.0);
          // big soft things dissolve well before they reach the lens (the wake carries them toward it)
          float nearFade = smoothstep(0.35, 1.2 + vSize * 1.5, vViewZ);
          a *= vCol.a * soft * nearFade;
          if (a < 0.003) discard;
          vec3 col = applyAtmosphere(vCol.rgb, vWorld);
          gl_FragColor = vec4(col * a, a * (1.0 - vMisc.y));
        }
      `,
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
      blending: THREE.CustomBlending,
      blendEquation: THREE.AddEquation,
      blendSrc: THREE.OneFactor,
      blendDst: THREE.OneMinusSrcAlphaFactor,
      blendSrcAlpha: THREE.OneFactor,
      blendDstAlpha: THREE.OneMinusSrcAlphaFactor,
    });
    this.mesh = new THREE.Mesh(g, this.material);
    this.mesh.frustumCulled = false;
    this.mesh.renderOrder = 40;
  }

  spawn(x, y, z, vx, vy, vz, o) {
    if (this.count >= this.max) return -1;
    const i = this.count++, i3 = i * 3;
    this.pos[i3] = x; this.pos[i3 + 1] = y; this.pos[i3 + 2] = z;
    this.vel[i3] = vx; this.vel[i3 + 1] = vy; this.vel[i3 + 2] = vz;
    this.col[i3] = o.r; this.col[i3 + 1] = o.g; this.col[i3 + 2] = o.b;
    this.life[i] = 0; this.maxLife[i] = o.life;
    this.size0[i] = o.size; this.size1[i] = o.grow ?? o.size;
    this.alpha[i] = o.alpha; this.type[i] = o.type;
    this.grav[i] = o.grav ?? 0; this.drag[i] = o.drag ?? 0.5;
    this.stretch[i] = o.stretch ?? 0; this.add[i] = o.add ?? 0;
    this.seed[i] = Math.random(); this.windK[i] = o.wind ?? 1;
    // how much of the wake's swirl it picks up (anything the wind moves, the vortices move)
    this.wakeK[i] = o.wake ?? this.windK[i];
    return i;
  }

  _kill(i) {
    const j = --this.count;
    if (i === j) return;
    const i3 = i * 3, j3 = j * 3;
    for (let k = 0; k < 3; k++) { this.pos[i3 + k] = this.pos[j3 + k]; this.vel[i3 + k] = this.vel[j3 + k]; this.col[i3 + k] = this.col[j3 + k]; }
    for (const a of [this.life, this.maxLife, this.size0, this.size1, this.alpha, this.type, this.grav, this.drag, this.stretch, this.add, this.seed, this.windK, this.wakeK]) a[i] = a[j];
  }

  update(dt, t, env, camera, size, reversed) {
    const { pos, vel, life, maxLife } = this;
    const w = env._w2 || (env._w2 = [0, 0, 0]);
    const wk = env._wk2 || (env._wk2 = [0, 0, 0, 0]);
    for (let i = 0; i < this.count; i++) {
      life[i] += dt;
      if (life[i] >= maxLife[i]) { this._kill(i); i--; continue; }
      const i3 = i * 3;
      let vx = vel[i3], vy = vel[i3 + 1], vz = vel[i3 + 2];
      const wn = this.windK[i], wkK = this.wakeK[i];
      if (wn > 0 || wkK > 0) {
        let ax = 0, ay = 0, az = 0;
        if (wn > 0) { env.wind(pos[i3], pos[i3 + 1], pos[i3 + 2], w); ax = w[0]; ay = w[1]; az = w[2]; }
        if (wkK > 0 && env.wake(pos[i3], pos[i3 + 1], pos[i3 + 2], wk) > 0) {
          const open = 1 - wk[3] * wkK;
          ax = ax * open + wk[0] * wkK; ay = ay * open + wk[1] * wkK; az = az * open + wk[2] * wkK;
        }
        const e = (1 - Math.exp(-this.drag[i] * dt)) * Math.max(wn, wkK);
        vx += (ax - vx) * e; vy += (ay - vy) * e; vz += (az - vz) * e;
      }
      vy -= this.grav[i] * dt;
      pos[i3] += vx * dt; pos[i3 + 1] += vy * dt; pos[i3 + 2] += vz * dt;
      vel[i3] = vx; vel[i3 + 1] = vy; vel[i3 + 2] = vz;
      // droplets end when they fall back into the sea / onto the ground
      if (this.grav[i] > 4 && vy < 0 && pos[i3 + 1] < env.surface(pos[i3], pos[i3 + 2])) { this._kill(i); i--; }
    }
    const n = this.count;
    const P = this.aPos.array, V = this.aVel.array, C = this.aCol.array, M = this.aMisc.array;
    for (let i = 0; i < n; i++) {
      const i3 = i * 3, i4 = i * 4;
      const k = life[i] / maxLife[i];
      // appear at once (a slow fade-in would leave them behind the camera before they show)
      const fade = Math.min(1, life[i] / 0.07) * (1 - k);
      P[i4] = pos[i3]; P[i4 + 1] = pos[i3 + 1]; P[i4 + 2] = pos[i3 + 2];
      P[i4 + 3] = this.size0[i] + (this.size1[i] - this.size0[i]) * (1 - (1 - k) * (1 - k));
      V[i4] = vel[i3]; V[i4 + 1] = vel[i3 + 1]; V[i4 + 2] = vel[i3 + 2]; V[i4 + 3] = this.stretch[i];
      C[i4] = this.col[i3]; C[i4 + 1] = this.col[i3 + 1]; C[i4 + 2] = this.col[i3 + 2]; C[i4 + 3] = this.alpha[i] * fade;
      M[i4] = this.type[i]; M[i4 + 1] = this.add[i]; M[i4 + 2] = this.seed[i]; M[i4 + 3] = Math.max(0.05, this.size0[i] * 0.6);
    }
    for (const a of [this.aPos, this.aVel, this.aCol, this.aMisc]) { a.clearUpdateRanges(); a.addUpdateRange(0, n * 4); a.needsUpdate = true; }
    this.geo.instanceCount = n;
    this.mesh.visible = n > 0;
    const u = this.material.uniforms;
    u.uDepth.value.set(camera.near, camera.far, reversed ? 1 : 0);
    u.uRes.value.copy(size);
  }
}

// ======================================================================================= ribbon
/** A fading camera-facing trail from a moving point. */
export class Ribbon {
  constructor(len = 40, life = 0.75) {
    this.len = len;
    this.life = life;
    this.pts = new Float32Array(len * 3);
    this.age = new Float32Array(len).fill(1e9);
    this.head = 0;
    this.n = 0;
    const g = new THREE.BufferGeometry();
    this.aPos = new THREE.BufferAttribute(new Float32Array(len * 2 * 3), 3);
    this.aUv = new THREE.BufferAttribute(new Float32Array(len * 2 * 3), 3);   // across, age, fade
    this.aPos.setUsage(THREE.DynamicDrawUsage); this.aUv.setUsage(THREE.DynamicDrawUsage);
    g.setAttribute('position', this.aPos);
    g.setAttribute('aTrail', this.aUv);      // not 'uv': three declares that one itself, as a vec2
    const idx = [];
    for (let i = 0; i < len - 1; i++) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    g.setIndex(idx);
    this.geo = g;
    this.strength = { value: 0 };
    this.material = new THREE.ShaderMaterial({
      uniforms: { uStrength: this.strength, uColor: { value: new THREE.Vector3(1, 1, 1) } },
      vertexShader: /* glsl */`attribute vec3 aTrail; varying vec3 vUv; void main(){ vUv = aTrail; gl_Position = projectionMatrix * viewMatrix * vec4(position, 1.0); }`,
      fragmentShader: /* glsl */`
        precision highp float;
        varying vec3 vUv;
        uniform float uStrength;
        uniform vec3 uColor;
        void main(){
          float across = max(1.0 - abs(vUv.x * 2.0 - 1.0), 0.0);
          float fy = clamp(vUv.y, 0.0, 1.0);
          float a = pow(across, 1.6) * (1.0 - fy) * (1.0 - fy) * smoothstep(0.0, 0.06, fy) * uStrength * clamp(vUv.z, 0.0, 1.0);
          gl_FragColor = vec4(uColor * a, a * 0.35);
        }
      `,
      transparent: true, depthWrite: false, side: THREE.DoubleSide,
      blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
      blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor,
    });
    this.mesh = new THREE.Mesh(g, this.material);
    this.mesh.frustumCulled = false;
    this.mesh.renderOrder = 45;
    this._acc = 0;
  }

  reset() { this.age.fill(1e9); this.n = 0; }

  update(dt, p, camPos, width, strength) {
    const L = this.len;
    for (let i = 0; i < L; i++) this.age[i] += dt;
    this._acc += dt;
    if (this._acc > this.life / (L - 2)) {
      this._acc = 0;
      this.head = (this.head + 1) % L;
      this.n = Math.min(this.n + 1, L);
    }
    // the head point always sits on the emitter
    const h3 = this.head * 3;
    this.pts[h3] = p.x; this.pts[h3 + 1] = p.y; this.pts[h3 + 2] = p.z;
    this.age[this.head] = 0;
    const P = this.aPos.array, UV = this.aUv.array;
    let px = p.x, py = p.y, pz = p.z;
    for (let k = 0; k < L; k++) {
      const i = (this.head - k + L * 2) % L, i3 = i * 3;
      const live = k < this.n;
      const x = live ? this.pts[i3] : px, y = live ? this.pts[i3 + 1] : py, z = live ? this.pts[i3 + 2] : pz;
      const j = (this.head - Math.min(k + 1, this.n - 1) + L * 2) % L, j3 = j * 3;
      let tx = x - this.pts[j3], ty = y - this.pts[j3 + 1], tz = z - this.pts[j3 + 2];
      if (k + 1 >= this.n) { tx = px - x || 1e-3; ty = py - y; tz = pz - z; }
      const cx = camPos.x - x, cy = camPos.y - y, cz = camPos.z - z;
      let sx = ty * cz - tz * cy, sy = tz * cx - tx * cz, sz = tx * cy - ty * cx;
      const sl = Math.hypot(sx, sy, sz) || 1;
      const a = Math.min(this.age[i] / this.life, 1);
      const wd = width * (0.35 + 1.4 * a) / sl;
      sx *= wd; sy *= wd; sz *= wd;
      const o = k * 6;
      P[o] = x - sx; P[o + 1] = y - sy; P[o + 2] = z - sz; P[o + 3] = x + sx; P[o + 4] = y + sy; P[o + 5] = z + sz;
      // fade with distance from the bristles, and long before the trail can sweep past the lens
      const dh = Math.hypot(x - p.x, y - p.y, z - p.z), dc = Math.sqrt(cx * cx + cy * cy + cz * cz);
      const fade = Math.max(0, 1 - Math.max(0, dh - 0.8) / 3.4) * Math.min(1, Math.max(0, (dc - 2.5) / 3.5));
      const u = k * 6;
      UV[u] = 0; UV[u + 1] = live ? a : 1; UV[u + 2] = fade; UV[u + 3] = 1; UV[u + 4] = live ? a : 1; UV[u + 5] = fade;
      px = x; py = y; pz = z;
    }
    this.aPos.needsUpdate = true; this.aUv.needsUpdate = true;
    this.strength.value = strength;
    this.mesh.visible = strength > 0.004;
  }
}
