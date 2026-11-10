// GLSL building blocks shared by every material so sky, haze, lighting and the meadow palette
// agree everywhere by construction.

export const NOISE = /* glsl */`
float hash11(float p){ p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash12(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
vec2 hash22(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973)); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.xx + p3.yz) * p3.zy); }
vec3 hash32(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973)); p3 += dot(p3, p3.yxz + 33.33); return fract((p3.xxy + p3.yzz) * p3.zyx); }
float hash13(vec3 p3){ p3 = fract(p3 * 0.1031); p3 += dot(p3, p3.zyx + 31.32); return fract((p3.x + p3.y) * p3.z); }
vec4 hash42(vec2 p){ vec4 p4 = fract(vec4(p.xyxy) * vec4(0.1031, 0.1030, 0.0973, 0.1099)); p4 += dot(p4, p4.wzxy + 33.33); return fract((p4.xxyz + p4.yzzw) * p4.zywx); }

float vnoise(vec2 p){
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash12(i), hash12(i + vec2(1, 0)), u.x), mix(hash12(i + vec2(0, 1)), hash12(i + vec2(1, 1)), u.x), u.y);
}
float vnoise3(vec3 p){
  vec3 i = floor(p), f = fract(p);
  vec3 u = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(mix(hash13(i), hash13(i + vec3(1,0,0)), u.x), mix(hash13(i + vec3(0,1,0)), hash13(i + vec3(1,1,0)), u.x), u.y),
    mix(mix(hash13(i + vec3(0,0,1)), hash13(i + vec3(1,0,1)), u.x), mix(hash13(i + vec3(0,1,1)), hash13(i + vec3(1,1,1)), u.x), u.y), u.z);
}
const mat2 ROT2 = mat2(0.8, -0.6, 0.6, 0.8);
float fbm2(vec2 p){ float s = 0.0, a = 0.5; for (int i = 0; i < 2; i++){ s += a * vnoise(p); p = ROT2 * p * 2.03; a *= 0.5; } return s / 0.75; }
float fbm3(vec2 p){ float s = 0.0, a = 0.5; for (int i = 0; i < 3; i++){ s += a * vnoise(p); p = ROT2 * p * 2.03; a *= 0.5; } return s / 0.875; }
float fbm4(vec2 p){ float s = 0.0, a = 0.5; for (int i = 0; i < 4; i++){ s += a * vnoise(p); p = ROT2 * p * 2.03; a *= 0.5; } return s / 0.9375; }
float fbm5(vec2 p){ float s = 0.0, a = 0.5; for (int i = 0; i < 5; i++){ s += a * vnoise(p); p = ROT2 * p * 2.03; a *= 0.5; } return s / 0.96875; }
float saturate(float x){ return clamp(x, 0.0, 1.0); }
vec3 saturate(vec3 x){ return clamp(x, 0.0, 1.0); }
float remap(float v, float a, float b){ return clamp((v - a) / (b - a), 0.0, 1.0); }
`;

/** Tileable noise texture lookups (cheaper than hash noise in hot fragment paths). */
export const NOISE_TEX = /* glsl */`
uniform sampler2D uNoiseTex;   // RGBA: four independent tileable noise fields, 256px
vec4 ntex(vec2 p){ return texture(uNoiseTex, p / 256.0); }
`;

export const ATMOSPHERE = /* glsl */`
uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform vec3 uSkyZenith;
uniform vec3 uSkyMid;
uniform vec3 uSkyHorizon;
uniform vec3 uSunHalo;
uniform vec3 uAmbSky;
uniform vec3 uAmbGround;
uniform vec4 uFog;
uniform vec3 uCamPos;

// Clear-sky radiance for a view direction (no sun disc, no clouds).
vec3 skyBase(vec3 d){
  float y = max(d.y, 0.0);
  float mu = dot(d, uSunDir);
  float hz = pow(1.0 - y, 5.0);
  vec3 c = mix(uSkyMid, uSkyZenith, pow(y, 0.62));
  c = mix(c, uSkyHorizon, hz);
  // forward-scattering glow around the sun, strongest in the thick air near the horizon
  float m = max(mu, 0.0);
  c += uSunHalo * (pow(m, 7.0) * 0.20 + pow(m, 40.0) * 0.28 + pow(m, 600.0) * 1.4) * (0.55 + 0.9 * hz);
  // slightly darker, bluer sky opposite the sun
  c *= 1.0 - 0.14 * pow(max(-mu, 0.0), 2.0) * (1.0 - hz);
  return c;
}

// Aerial perspective: height fog with blue-biased extinction, converging on the sky at the horizon.
vec3 applyAtmosphere(vec3 col, vec3 P){
  vec3 v = P - uCamPos;
  float d = length(v);
  vec3 dir = v / max(d, 1e-4);
  float b = uFog.y;
  float c0 = uFog.x * exp(-max(uCamPos.y, 0.0) * b);
  float t = dir.y * b;
  float integ = abs(t) > 1e-5 ? (1.0 - exp(-d * t)) / t : d;
  float od = c0 * integ;
  vec3 ext = exp(-od * vec3(0.52, 0.86, 1.32));
  vec3 fd = normalize(vec3(dir.x, max(dir.y, 0.0) * 0.5 + 0.035, dir.z));
  vec3 ins = skyBase(fd);
  return col * ext + ins * (1.0 - ext);
}

// Soft cloud shadows drifting over the land and sea.
float cloudShadow(vec2 xz, float time);
`;

export const CLOUD_SHADOW = /* glsl */`
float cloudShadow(vec2 xz, float time){
  vec2 p = xz * 0.00042 + vec2(time * 0.0036, time * 0.0021);
  float n = fbm4(p * 2.0 + 3.7);
  n = n * 0.72 + 0.28 * fbm2(p * 7.0 - 1.3);
  return mix(0.50, 1.0, smoothstep(0.50, 0.30, n));
}
`;

/** World-space lookups into the baked terrain maps. */
export const TERRAIN_LOOKUP = /* glsl */`
uniform sampler2D uHeightTex;
uniform sampler2D uSplatTex;
uniform sampler2D uLightTex;
uniform vec4 uWorld;   // size, 1/size, texel(uv), lodBias
vec2 worldUV(vec2 xz){ return xz * uWorld.y + 0.5; }
// light map blue channel -> metres offshore (+) / inland (-); stored as d / (|d| + 16)
float shoreDist(float b){ float t = b * 2.0 - 1.0; return 16.0 * t / max(1.0 - abs(t), 0.004); }
float terrainH(vec2 xz){ return textureLod(uHeightTex, worldUV(xz), 0.0).r; }
float terrainHLod(vec2 xz, float lod){ return textureLod(uHeightTex, worldUV(xz), lod).r; }
vec3 terrainN(vec2 xz, float lod){
  vec2 uv = worldUV(xz);
  float e = uWorld.z * exp2(lod);
  float hl = textureLod(uHeightTex, uv - vec2(e, 0.0), lod).r;
  float hr = textureLod(uHeightTex, uv + vec2(e, 0.0), lod).r;
  float hd = textureLod(uHeightTex, uv - vec2(0.0, e), lod).r;
  float hu = textureLod(uHeightTex, uv + vec2(0.0, e), lod).r;
  return normalize(vec3(hl - hr, 2.0 * e * uWorld.x, hd - hu));
}
`;

/** The meadow palette: shared by the terrain, the grass blades and the far-field flower tint. */
export const MEADOW = /* glsl */`
// Slow colour drift across the island: emerald hollows, sun-bleached crests.
vec3 meadowTint(vec2 xz, float wet){
  float a = vnoise(xz * 0.0031 + 11.0);
  float b = vnoise(xz * 0.0125 - 5.0);
  float c = vnoise(xz * 0.047 + 2.0);
  vec3 lush = vec3(0.085, 0.235, 0.050);
  vec3 fresh = vec3(0.190, 0.315, 0.068);
  vec3 dry = vec3(0.390, 0.365, 0.130);
  vec3 col = mix(lush, fresh, smoothstep(0.22, 0.78, a * 0.6 + b * 0.4));
  col = mix(col, dry, smoothstep(0.38, 0.80, b * 0.5 + c * 0.5) * (1.0 - wet) * 0.85);
  col = mix(col, lush * 0.92, wet * 0.65);
  return col;
}

// Flower species palette. s = species field (0..1), r = per-flower random.
// Drifts along s: pink cosmos | white daisy | lavender | gold | poppy (a rare accent).
const float SP1 = 0.42, SP2 = 0.60, SP3 = 0.78, SP4 = 0.90;
vec3 flowerPetal(float s, float r){
  vec3 pinkA = vec3(0.90, 0.16, 0.46), pinkB = vec3(0.97, 0.42, 0.66), pinkC = vec3(0.97, 0.76, 0.87);
  vec3 white = vec3(0.97, 0.96, 0.90);
  vec3 lavA = vec3(0.42, 0.26, 0.82), lavB = vec3(0.66, 0.50, 0.93);
  vec3 red = vec3(0.90, 0.07, 0.035), orange = vec3(0.98, 0.36, 0.05);
  vec3 gold = vec3(0.99, 0.72, 0.05), lemon = vec3(0.98, 0.90, 0.30);
  vec3 blue = vec3(0.16, 0.36, 0.92);
  vec3 c;
  if (s < SP1){
    c = r < 0.42 ? pinkA : (r < 0.76 ? pinkB : (r < 0.90 ? pinkC : white));
  } else if (s < SP2){
    c = r < 0.62 ? white : (r < 0.80 ? lemon : (r < 0.92 ? pinkC : gold));
  } else if (s < SP3){
    c = r < 0.48 ? lavA : (r < 0.80 ? lavB : (r < 0.90 ? blue : white));
  } else if (s < SP4){
    c = r < 0.6 ? gold : (r < 0.85 ? lemon : (r < 0.94 ? white : orange));
  } else {
    c = r < 0.66 ? red : (r < 0.84 ? orange : (r < 0.93 ? pinkA : white));
  }
  return c;
}
// species silhouette: x = petal count, y = eye size, z = head size, w = stem height
vec4 flowerShape(float s){
  if (s < SP1) return vec4(8.0, 0.24, 1.12, 1.06);
  if (s < SP2) return vec4(14.0, 0.36, 0.84, 0.80);
  if (s < SP3) return vec4(6.0, 0.20, 0.80, 0.92);
  if (s < SP4) return vec4(5.0, 0.26, 0.74, 0.72);
  return vec4(5.0, 0.30, 1.10, 0.90);
}
// Average colour of a drift, for the far-field tint.
vec3 flowerMean(float s){
  vec3 pink = vec3(0.94, 0.36, 0.60);
  vec3 daisy = vec3(0.96, 0.92, 0.72);
  vec3 lav = vec3(0.52, 0.38, 0.86);
  vec3 gold = vec3(0.98, 0.76, 0.14);
  vec3 poppy = vec3(0.90, 0.20, 0.10);
  vec3 c = mix(pink, daisy, smoothstep(SP1 - 0.03, SP1 + 0.03, s));
  c = mix(c, lav, smoothstep(SP2 - 0.03, SP2 + 0.03, s));
  c = mix(c, gold, smoothstep(SP3 - 0.03, SP3 + 0.03, s));
  c = mix(c, poppy, smoothstep(SP4 - 0.03, SP4 + 0.03, s));
  return c;
}
`;

/** Wind: gust fronts that sweep the meadow, shared by blades, flowers and the far-field ground. */
export const WIND = /* glsl */`
uniform vec4 uWind;     // dir.xz, strength, time
float windGust(vec2 xz, float t){
  vec2 d = uWind.xy;
  vec2 a = vec2(dot(xz, d), dot(xz, vec2(-d.y, d.x)));          // along / across the wind
  // long fronts drifting downwind, with faster ripples riding on them
  float g1 = textureLod(uNoiseTex, vec2(a.x - t * 12.0, a.y * 0.42) / 256.0 * 0.62, 0.0).r;
  float g2 = textureLod(uNoiseTex, vec2(a.x - t * 19.0, a.y * 0.55) / 256.0 * 2.3 + 0.31, 0.0).g;
  float g = g1 * 0.72 + g2 * 0.28;
  return smoothstep(0.28, 0.80, g);
}
// the rider's wake: xy = push (m, world xz), z = pressure 0..1, w = foam
uniform sampler2D uWakeTex;
uniform vec4 uWake;
vec4 wakeAt(vec2 xz){
  vec2 uv = (xz - uWake.xy) * uWake.z + 0.5;
  vec2 e = min(uv, 1.0 - uv);
  float inside = smoothstep(0.0, 0.04, min(e.x, e.y));
  return textureLod(uWakeTex, uv, 0.0) * inside;
}
`;

/** Where the wake has torn petals off the flowers: a map of the whole island (fx/strip.js). */
export const STRIP = /* glsl */`
uniform sampler2D uStripTex;
// share of the petals gone: 0 = untouched .. 1 = bare
float strippedAt(vec2 uv){ return textureLod(uStripTex, uv, 0.0).r; }
float strippedFiltered(vec2 uv){ return texture(uStripTex, uv).r; }
`;

/** The rider's shadow on the world: a small sun-space depth map, wider and fainter with distance. */
export const SHADOW = /* glsl */`
uniform sampler2D uShadowTex;
uniform mat4 uShadowMat;
uniform float uShadowOn;   // 0 off, 1 standard depth, 2 reversed depth
float riderShadow(vec3 P){
  if (uShadowOn < 0.5) return 1.0;
  vec3 s = (uShadowMat * vec4(P, 1.0)).xyz;
  if (s.x < 0.0 || s.x > 1.0 || s.y < 0.0 || s.y > 1.0 || s.z > 1.0 || s.z < 0.0) return 1.0;
  float drop = max(s.z - 0.492, 0.0) * 59.0;                 // metres below the rider along the light
  float rad = clamp(1.4 + drop * 2.6, 1.4, 30.0) / 1024.0;
  float rot = fract(52.9829189 * fract(dot(gl_FragCoord.xy, vec2(0.06711056, 0.00583715)))) * 6.2831853;
  float acc = 0.0;
  for (int i = 0; i < 10; i++){
    float fi = float(i);
    float r = sqrt((fi + 0.5) / 10.0);
    float a = fi * 2.3999632 + rot;
    float d = texture(uShadowTex, s.xy + vec2(cos(a), sin(a)) * r * rad).r;
    if (uShadowOn > 1.5) d = 1.0 - d;
    acc += step(s.z - 0.006, d);
  }
  float lit = acc / 10.0;
  float edge = smoothstep(0.0, 0.10, min(min(s.x, 1.0 - s.x), min(s.y, 1.0 - s.y)));
  float fadeOut = 1.0 - smoothstep(22.0, 52.0, drop);
  return mix(1.0, lit, edge * fadeOut);
}
`;

export const TONEMAP = /* glsl */`
// ACES fitted (Stephen Hill), tuned for a bright saturated look
vec3 RRTAndODTFit(vec3 v){ vec3 a = v * (v + 0.0245786) - 0.000090537; vec3 b = v * (0.983729 * v + 0.4329510) + 0.238081; return a / b; }
vec3 acesFilm(vec3 c){
  const mat3 inM = mat3(0.59719, 0.07600, 0.02840, 0.35458, 0.90834, 0.13383, 0.04823, 0.01566, 0.83777);
  const mat3 outM = mat3(1.60475, -0.10208, -0.00327, -0.53108, 1.10813, -0.07276, -0.07367, -0.00605, 1.07602);
  c = inM * c; c = RRTAndODTFit(c); c = outM * c; return clamp(c, 0.0, 1.0);
}
vec3 toSRGB(vec3 c){ return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(0.0031308, c)); }
`;
