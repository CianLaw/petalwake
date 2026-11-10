// Input: keyboard, pointer-lock mouse (sprung virtual stick) and gamepad, merged into one state.
export class Input {
  constructor(canvas) {
    this.canvas = canvas;
    this.keys = new Set();
    this.stickX = 0;   // mouse stick
    this.stickY = 0;
    this.turn = 0;     // -1 left .. +1 right
    this.pitch = 0;    // -1 dive .. +1 climb
    this.boost = false;
    this.brake = false;
    this.invert = false;
    this.locked = false;
    this.enabled = false;
    this.pressed = new Set(); // edge-triggered keys, consumed by the game
    this.sens = 0.0021;

    window.addEventListener('keydown', (e) => {
      if (e.repeat) return;
      this.keys.add(e.code);
      this.pressed.add(e.code);
      if (this.enabled && ['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) e.preventDefault();
    });
    window.addEventListener('keyup', (e) => this.keys.delete(e.code));
    window.addEventListener('blur', () => this.keys.clear());
    document.addEventListener('pointerlockchange', () => { this.locked = document.pointerLockElement === canvas; });
    canvas.addEventListener('click', () => { if (this.enabled && !this.locked) canvas.requestPointerLock?.()?.catch?.(() => {}); });
    window.addEventListener('mousemove', (e) => {
      if (!this.locked || !this.enabled) return;
      this.stickX = Math.max(-1, Math.min(1, this.stickX + e.movementX * this.sens));
      this.stickY = Math.max(-1, Math.min(1, this.stickY + e.movementY * this.sens));
    });
    window.addEventListener('mousedown', (e) => { if (this.locked) { if (e.button === 0) this.mouseBoost = true; if (e.button === 2) this.mouseBrake = true; } });
    window.addEventListener('mouseup', (e) => { if (e.button === 0) this.mouseBoost = false; if (e.button === 2) this.mouseBrake = false; });
    window.addEventListener('contextmenu', (e) => { if (this.enabled) e.preventDefault(); });
  }

  take(code) {
    if (this.pressed.has(code)) { this.pressed.delete(code); return true; }
    return false;
  }

  update(dt) {
    const k = this.keys;
    let x = 0, y = 0;
    if (k.has('KeyA') || k.has('ArrowLeft')) x -= 1;
    if (k.has('KeyD') || k.has('ArrowRight')) x += 1;
    if (k.has('KeyW') || k.has('ArrowUp')) y -= 1;
    if (k.has('KeyS') || k.has('ArrowDown')) y += 1;
    // the mouse stick springs back to centre like a self-centring joystick
    const relax = Math.exp(-dt * 2.6);
    this.stickX *= relax; this.stickY *= relax;
    x += this.stickX * 1.6;
    y += -this.stickY * 1.6;
    let boost = k.has('ShiftLeft') || k.has('ShiftRight') || !!this.mouseBoost;
    let brake = k.has('Space') || !!this.mouseBrake;
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    for (const p of pads) {
      if (!p || !p.connected) continue;
      const dz = (v) => (Math.abs(v) < 0.12 ? 0 : (v - Math.sign(v) * 0.12) / 0.88);
      x += dz(p.axes[0] || 0);
      y += -dz(p.axes[1] || 0);
      if (p.buttons[7]?.value > 0.3 || p.buttons[0]?.pressed) boost = true;
      if (p.buttons[6]?.value > 0.3 || p.buttons[1]?.pressed) brake = true;
      break;
    }
    if (this.invert) y = -y;
    this.turn = Math.max(-1, Math.min(1, x));
    this.pitch = Math.max(-1, Math.min(1, y));
    this.boost = boost;
    this.brake = brake;
    if (!this.enabled) { this.turn = 0; this.pitch = 0; this.boost = false; this.brake = false; }
  }
}
