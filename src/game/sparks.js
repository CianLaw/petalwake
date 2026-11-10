// Small one-off bursts for the landing and the trick, thrown into the wind-effects particle pools
// (fx.sprites: soft dust and additive sparkles; fx.burst: petals).
import { SPR } from '../fx/particles.js';

const rand = (a, b) => a + Math.random() * (b - a);
const TAU = Math.PI * 2;

export const GOLD = [1.0, 0.80, 0.38], PETAL = [1.0, 0.56, 0.74], PALE = [1.0, 0.93, 0.86];

/** A soft ball of pale dust: hides a swap, softens a touchdown. sun = light arriving on it [r, g, b]. */
export function puff(fx, x, y, z, n, sun, spread = 0.45, speed = 1.6) {
  for (let i = 0; i < n; i++) {
    const a = rand(0, TAU), u = rand(-0.4, 1), s = Math.sqrt(1 - u * u * 0.6) * rand(0.2, 1) * speed;
    const b = rand(0.8, 1.05);
    fx.sprites.spawn(x + Math.cos(a) * spread * rand(0, 1), y + rand(-0.25, 0.35), z + Math.sin(a) * spread * rand(0, 1),
      Math.cos(a) * s, u * speed * 0.6 + 0.5, Math.sin(a) * s, {
        type: SPR.PUFF, r: 0.92 * sun[0] * b, g: 0.88 * sun[1] * b, b: 0.82 * sun[2] * b, alpha: rand(0.22, 0.42),
        size: rand(0.35, 0.7), grow: rand(1.1, 2.0), life: rand(0.55, 1.1), drag: 3.2, grav: -0.3, add: 0.05, wind: 0.35, wake: 0,
      });
  }
}

/** A low ring of dust running out over the floor from where she came down. */
export function dustRing(fx, x, y, z, radius, n, sun) {
  for (let i = 0; i < n; i++) {
    const a = (i / n) * TAU + rand(-0.15, 0.15), s = rand(1.8, 3.4), b = rand(0.8, 1.05);
    fx.sprites.spawn(x + Math.cos(a) * radius, y + rand(0.05, 0.18), z + Math.sin(a) * radius, Math.cos(a) * s, rand(0.1, 0.5), Math.sin(a) * s, {
      type: SPR.PUFF, r: 0.90 * sun[0] * b, g: 0.86 * sun[1] * b, b: 0.80 * sun[2] * b, alpha: rand(0.16, 0.30),
      size: rand(0.25, 0.45), grow: rand(0.9, 1.5), life: rand(0.5, 0.95), drag: 4.5, grav: 0, add: 0.05, wind: 0.3, wake: 0,
    });
  }
}

/** Sparkles: small additive motes thrown out from a point, carried along at (vx, vy, vz). */
export function twinkle(fx, x, y, z, n, col = GOLD, speed = 3, vx = 0, vy = 0, vz = 0, life = 0.8) {
  for (let i = 0; i < n; i++) {
    const a = rand(0, TAU), u = rand(-1, 1), s = Math.sqrt(1 - u * u) * rand(0.35, 1) * speed, b = rand(1.2, 2.6);
    fx.sprites.spawn(x, y, z, vx + Math.cos(a) * s, vy + u * speed * 0.8 + 0.6, vz + Math.sin(a) * s, {
      type: SPR.BLOB, r: col[0] * b, g: col[1] * b, b: col[2] * b, alpha: rand(0.55, 0.95), size: rand(0.14, 0.32), grow: 0.04,
      life: rand(0.5, 1) * life, drag: 2.2, grav: 1.6, add: 1, wind: 0.25, wake: 0,
    });
  }
}

/** One sparkle with a velocity of its own (the kickflip's spiral). */
export function mote(fx, x, y, z, vx, vy, vz, col = GOLD, life = 0.7, size = 0.3) {
  const b = rand(1.6, 3.4);
  fx.sprites.spawn(x, y, z, vx, vy, vz, {
    type: SPR.BLOB, r: col[0] * b, g: col[1] * b, b: col[2] * b, alpha: rand(0.6, 1), size: size * rand(0.6, 1.4), grow: 0.05,
    life: life * rand(0.7, 1.2), drag: 0, grav: 0.8, add: 1, wind: 0, wake: 0,
  });
}

/** A short bright streak (the trick's whip lines). */
export function streak(fx, x, y, z, vx, vy, vz, col = PALE, life = 0.35) {
  fx.sprites.spawn(x, y, z, vx, vy, vz, {
    type: SPR.STREAK, r: col[0] * 1.6, g: col[1] * 1.6, b: col[2] * 1.6, alpha: rand(0.35, 0.7), size: rand(0.07, 0.13), life: life * rand(0.7, 1.2),
    drag: 0, grav: 0, stretch: 0.10, add: 1, wind: 0, wake: 0,
  });
}
