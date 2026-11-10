// Sky: analytic clear-sky gradient + sun, with a cloud layer baked into a lat-long texture.
import * as THREE from 'three';
import { U, shared } from '../core/ctx.js';
import { NOISE, ATMOSPHERE } from '../shaders/common.js';

export const SKY_UNIFORMS = ['uSunDir', 'uSunColor', 'uSkyZenith', 'uSkyMid', 'uSkyHorizon', 'uSunHalo', 'uAmbSky', 'uAmbGround', 'uFog', 'uCamPos'];

const tri = () => {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 3, -1, 0, -1, 3, 0]), 3));
  return g;
};

/** Cloud lookup shared with the water (reflections). Cloud map: RGB = lit colour (premultiplied), A = opacity. */
export const CLOUD_LOOKUP = /* glsl */`
uniform sampler2D uCloudTex;
uniform float uCloudOn;
// direction -> lat-long uv (upper hemisphere stretched so the horizon gets the texels)
vec2 cloudUV(vec3 d){
  float az = atan(d.z, d.x) * 0.15915494 + 0.5;
  float el = asin(clamp(d.y, -1.0, 1.0)) * 0.63661977;       // 0 at horizon, 1 at zenith
  return vec2(az, sqrt(clamp(el, 0.0, 1.0)));
}
vec4 sampleClouds(vec3 d){
  if (uCloudOn < 0.5 || d.y < -0.005) return vec4(0.0);
  vec2 uv = cloudUV(d);
  // manual gradients avoid the seam at the azimuth wrap
  vec2 dx = dFdx(uv), dy = dFdy(uv);
  dx.x -= floor(dx.x + 0.5); dy.x -= floor(dy.x + 0.5);
  return textureGrad(uCloudTex, uv, dx, dy);
}
`;

export class Sky {
  constructor() {
    this.cloudTex = { value: null };
    this.cloudOn = { value: 0 };
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        ...shared(...SKY_UNIFORMS),
        uProjInv: { value: new THREE.Vector2(1, 1) },
        uCamWorld: { value: new THREE.Matrix4() },
        uCloudTex: this.cloudTex,
        uCloudOn: this.cloudOn,
        uEnv: { value: 0 },
      },
      vertexShader: /* glsl */`
        varying vec2 vNdc;
        void main(){ vNdc = position.xy; gl_Position = vec4(position.xy, 0.0, 1.0); }
      `,
      fragmentShader: /* glsl */`
        precision highp float;
        varying vec2 vNdc;
        uniform vec2 uProjInv;
        uniform mat4 uCamWorld;
        uniform float uEnv;       // 1 while baking the rider's environment map
        ${NOISE}
        ${ATMOSPHERE}
        ${CLOUD_LOOKUP}
        void main(){
          vec3 d = normalize(mat3(uCamWorld) * vec3(vNdc * uProjInv, -1.0));
          vec3 col = skyBase(d);
          float mu = dot(d, uSunDir);
          // sun: hot core with a soft limb; the bloom pass does the rest
          float disc = smoothstep(0.99982, 0.99994, mu);
          float corona = pow(max(mu, 0.0), 3000.0);
          vec3 sun = uSunColor * (disc * 55.0 + corona * 6.0) * (1.0 - uEnv);
          vec4 cl = sampleClouds(d);
          col = col * (1.0 - cl.a) + cl.rgb + sun * (1.0 - cl.a) * (1.0 - cl.a);
          // under the horizon: haze into deep sea colour (only ever seen in reflections / at great height)
          float below = smoothstep(0.0, -0.08, d.y);
          col = mix(col, mix(uSkyHorizon * vec3(0.55, 0.7, 0.85), uAmbGround * 2.4, uEnv), below);
          gl_FragColor = vec4(col, 1.0);
        }
      `,
      depthTest: false,
      depthWrite: false,
    });
    this.mesh = new THREE.Mesh(tri(), this.material);
    this.mesh.frustumCulled = false;
    this.mesh.renderOrder = -1000;
    const sync = (renderer, scene, camera) => {
      const u = this.material.uniforms;
      u.uProjInv.value.set(1 / camera.projectionMatrix.elements[0], 1 / camera.projectionMatrix.elements[5]);
      u.uCamWorld.value.copy(camera.matrixWorld);
      this.material.uniformsNeedUpdate = true;
    };
    this.mesh.onBeforeRender = sync;
    this.envMesh = new THREE.Mesh(this.mesh.geometry, this.material);
    this.envMesh.frustumCulled = false;
    this.envMesh.onBeforeRender = sync;
  }

  /** Prefiltered environment (sky + clouds, no sun disc) for the rider's PBR materials. */
  bakeEnvironment(renderer) {
    const pmrem = new THREE.PMREMGenerator(renderer);
    const scene = new THREE.Scene();
    scene.add(this.envMesh);
    this.material.uniforms.uEnv.value = 1;
    const rt = pmrem.fromScene(scene, 0, 0.1, 100);
    this.material.uniforms.uEnv.value = 0;
    pmrem.dispose();
    return rt.texture;
  }
}
