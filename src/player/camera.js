// Chase camera with an FPV-drone feel: it trails the broom with a little lag, rolls with the bank,
// widens with speed and never dips under the ground.
import * as THREE from 'three';
import { SPEEDS } from './flight.js';

const damp = (cur, target, rate, dt) => cur + (target - cur) * (1 - Math.exp(-rate * dt));
const dampAngle = (cur, target, rate, dt) => {
  let d = target - cur;
  d = Math.atan2(Math.sin(d), Math.cos(d));
  return cur + d * (1 - Math.exp(-rate * dt));
};

// look = how far ahead of the rider the camera aims, drop = how far below her (tilts the view down
// so the ground streaming between camera and broom fills the lower frame)
// zoom = [slow, fast]: how the following distance scales with airspeed (1 at a cruise) - the chase
// camera closes in when the broom dawdles and drops back as it sprints
export const CAM_MODES = [
  { name: 'chase', dist: 7.2, height: 1.65, look: 5.5, drop: 0.55, fov: 70, roll: 0.62, lag: 3.4, zoom: [0.64, 1.42] },
  { name: 'low', dist: 5.2, height: 0.75, look: 9, drop: 0.25, fov: 82, roll: 0.78, lag: 4.6 },
  { name: 'far', dist: 14, height: 4.2, look: 6, drop: 1.0, fov: 60, roll: 0.45, lag: 2.6 },
];

export class ChaseCamera {
  constructor(camera, flight) {
    this.camera = camera;
    this.flight = flight;
    this.mode = 0;
    this.yaw = flight.yaw;
    this.pitch = flight.pitch;
    this.roll = 0;
    this.dist = CAM_MODES[0].dist;
    this.height = CAM_MODES[0].height;
    this.fov = 70;
    this.fovOut = 70;
    this.shake = 0;
    this.orbit = 0;         // title-screen orbit angle offset
    this.orbitPitch = 0;
    this._target = new THREE.Vector3();
    this._pos = new THREE.Vector3();
    this._up = new THREE.Vector3();
    this._q = new THREE.Quaternion();
    this._z = new THREE.Vector3(0, 0, 1);
  }

  snap() {
    this.yaw = this.flight.yaw;
    this.pitch = this.flight.pitch;
    this.roll = this.flight.roll * CAM_MODES[this.mode].roll;
  }

  next() { this.mode = (this.mode + 1) % CAM_MODES.length; return CAM_MODES[this.mode].name; }

  update(dt, time, surfaceAt) {
    const f = this.flight, m = CAM_MODES[this.mode], cam = this.camera;
    this.yaw = dampAngle(this.yaw, f.yaw + this.orbit, m.lag, dt);
    this.pitch = damp(this.pitch, f.pitch * 0.86 + this.orbitPitch, m.lag * 0.9, dt);
    this.roll = damp(this.roll, f.roll * m.roll, 4.2, dt);
    const sk = Math.max(0, (f.speed - 33) / 30);
    let zoom = 1 + 0.16 * f.boosting + sk * 0.5 / m.dist;
    if (m.zoom) {
      const { SLOW, CRUISE, BOOST } = SPEEDS, v = f.speed;
      if (v < CRUISE) {
        const t = Math.min(1, (CRUISE - v) / (CRUISE - SLOW));
        zoom = 1 - (1 - m.zoom[0]) * t * t * (3 - 2 * t);
      } else {
        // (keeps easing out past boost speed, in a dive)
        zoom = 1 + (m.zoom[1] - 1) * (1 - Math.exp(-(v - CRUISE) / 22)) / (1 - Math.exp(-(BOOST - CRUISE) / 22));
      }
    }
    this.dist = damp(this.dist, m.dist * zoom, 2.4, dt);
    // rise and sink with the distance so the broom stays framed the same way
    this.height = damp(this.height, m.height * (0.4 + 0.6 * zoom), 2.4, dt);
    this.fov = damp(this.fov, m.fov + 11 * Math.min(sk, 1.3) + 7 * f.boosting, 2.6, dt);

    const cp = Math.cos(this.pitch), sp = Math.sin(this.pitch);
    const dx = Math.sin(this.yaw) * cp, dy = sp, dz = -Math.cos(this.yaw) * cp;
    // sit behind and above, measured in the camera's own tilted frame so dives stay framed
    const ux = -Math.sin(this.yaw) * sp, uy = cp, uz = Math.cos(this.yaw) * sp;
    // the camera rides out most of a landing bounce, so the broom is seen to dip and spring back
    const fy = f.pos.y - (f.bob || 0) * 0.65;
    const p = this._pos.set(
      f.pos.x - dx * this.dist + ux * this.height,
      fy - dy * this.dist + uy * this.height,
      f.pos.z - dz * this.dist + uz * this.height,
    );
    // keep out of the ground and the swell
    const floor = surfaceAt(p.x, p.z) + 0.45;
    if (p.y < floor) p.y = floor;

    // shake: a fine buzz at speed plus a kick on impact
    this.shake = damp(this.shake, 0.012 * sk + 0.035 * f.boosting + f.bump * 0.22, 8, dt);
    const s = this.shake;
    p.x += (Math.sin(time * 37.1) + Math.sin(time * 61.7)) * 0.5 * s;
    p.y += (Math.sin(time * 43.3 + 1) + Math.sin(time * 71.9)) * 0.5 * s;

    cam.position.copy(p);
    const t = this._target.set(
      f.pos.x + f.fwd.x * m.look, fy + f.fwd.y * m.look - m.drop, f.pos.z + f.fwd.z * m.look,
    );
    this._up.set(0, 1, 0);
    cam.up.copy(this._up);
    cam.lookAt(t);
    // roll about the view axis
    this._q.setFromAxisAngle(this._z, -this.roll + Math.sin(time * 29.0) * s * 0.06);
    cam.quaternion.multiply(this._q);
    this.fovOut = this.fov;
  }
}
