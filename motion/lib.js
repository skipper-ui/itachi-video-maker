// Motion-graphics toolkit for canvas scenes. Every draw call is a pure function of time `t`
// (seconds since the scene started), so frames can be rendered in any order.
/* eslint-disable no-unused-vars */

const W = 1080, H = 1920;

// ---- timing & easing --------------------------------------------------------
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, k) => a + (b - a) * k;
const prog = (t, start, dur) => clamp((t - start) / dur);
const ease = {
  outCubic: k => 1 - Math.pow(1 - k, 3),
  inCubic: k => k * k * k,
  inOutCubic: k => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2),
  outBack: (k, s = 1.9) => 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2),
  outElastic: k => (k === 0 || k === 1 ? k : Math.pow(2, -10 * k) * Math.sin((k * 10 - 0.75) * (2 * Math.PI / 3)) + 1),
  outExpo: k => (k === 1 ? 1 : 1 - Math.pow(2, -10 * k)),
};
// Pop-in scale: 0 -> overshoot -> 1.
const pop = (t, start, dur = 0.45) => ease.outBack(prog(t, start, dur));
// Fade out near the end of a scene so crossfades look clean.
const outro = (t, dur, len = 0.35) => 1 - prog(t, dur - len, len);

function rng(seed) {
  let s = seed >>> 0 || 1;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

// Time (s) at which `word` is spoken in this scene's narration (nth occurrence), or `fallback`.
function when(word, nth = 0, fallback = 0) {
  const norm = w => String(w).toLowerCase().replace(/[^a-z0-9]/g, '');
  const hits = (window.WORDS || []).filter(x => norm(x[0]) === norm(word));
  return hits[nth] ? hits[nth][1] : fallback;
}

// ---- palette ------------------------------------------------------------------
const C = {
  gold: '#FFC83D', goldHi: '#FFF1A8', goldLo: '#D98A0B', orange: '#FF8A1E',
  purple: '#7B3FE4', purpleHi: '#B98BFF', purpleLo: '#2A0F5C', night: '#120826',
  ink: '#1C0E05', white: '#FFFFFF', blue: '#5EC8FF', red: '#FF4D4D', green: '#59D163',
  stone: '#9AA3B5', stoneLo: '#5B6375', wood: '#9A5B2E', woodLo: '#5E3215',
};

// ---- drawing primitives -----------------------------------------------------------
function withT(ctx, x, y, s, rot, fn) {
  ctx.save();
  ctx.translate(x, y);
  if (rot) ctx.rotate(rot);
  if (s !== 1) ctx.scale(s, s);
  fn();
  ctx.restore();
}

function vgrad(ctx, y0, y1, stops) {
  const g = ctx.createLinearGradient(0, y0, 0, y1);
  stops.forEach(([o, c]) => g.addColorStop(o, c));
  return g;
}

// Chunky game-UI shape: fill with vertical gradient, thick dark outline, glossy top highlight.
function chunky(ctx, path, top, bottom, { stroke = C.ink, lw = 10, y0 = -100, y1 = 100, gloss = true } = {}) {
  ctx.fillStyle = vgrad(ctx, y0, y1, [[0, top], [1, bottom]]);
  ctx.fill(path);
  if (gloss) {
    ctx.save();
    ctx.clip(path);
    ctx.fillStyle = 'rgba(255,255,255,0.18)';
    ctx.fillRect(-2000, y0 - 10, 4000, (y1 - y0) * 0.38);
    ctx.restore();
  }
  ctx.lineJoin = 'round';
  ctx.lineWidth = lw;
  ctx.strokeStyle = stroke;
  ctx.stroke(path);
}

function rectPath(x, y, w, h, r = 0) {
  const p = new Path2D();
  p.roundRect(x, y, w, h, r);
  return p;
}

function polyPath(pts) {
  const p = new Path2D();
  pts.forEach(([x, y], i) => (i ? p.lineTo(x, y) : p.moveTo(x, y)));
  p.closePath();
  return p;
}

function starPath(r1, r2, n = 5) {
  const pts = [];
  for (let i = 0; i < n * 2; i++) {
    const a = -Math.PI / 2 + (i * Math.PI) / n;
    const r = i % 2 ? r2 : r1;
    pts.push([Math.cos(a) * r, Math.sin(a) * r]);
  }
  return polyPath(pts);
}

function shieldPath(w, h) {
  const p = new Path2D();
  p.moveTo(-w / 2, -h / 2);
  p.lineTo(w / 2, -h / 2);
  p.lineTo(w / 2, h * 0.05);
  p.quadraticCurveTo(w / 2, h * 0.35, 0, h / 2);
  p.quadraticCurveTo(-w / 2, h * 0.35, -w / 2, h * 0.05);
  p.closePath();
  return p;
}

// ---- text ---------------------------------------------------------------------------
const FONT = '"Inter Display Black", "Inter Black", "Inter", sans-serif';

// Big game-style title: gold gradient fill, thick dark outline, drop shadow.
function title(ctx, str, x, y, size, opts = {}) {
  const { fill = [C.goldHi, C.gold, C.goldLo], stroke = C.ink, align = 'center', alpha = 1,
          spacing = 0, lw = size * 0.16, shadow = true } = opts;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.font = `${size}px ${FONT}`;
  ctx.textAlign = align;
  ctx.textBaseline = 'middle';
  if ('letterSpacing' in ctx) ctx.letterSpacing = `${spacing}px`;
  if (shadow) {
    ctx.fillStyle = 'rgba(0,0,0,0.55)';
    ctx.fillText(str, x, y + size * 0.09);
  }
  ctx.lineJoin = 'round';
  ctx.lineWidth = lw;
  ctx.strokeStyle = stroke;
  ctx.strokeText(str, x, y);
  ctx.fillStyle = Array.isArray(fill)
    ? vgrad(ctx, y - size * 0.5, y + size * 0.5, fill.map((c, i) => [i / (fill.length - 1), c]))
    : fill;
  ctx.fillText(str, x, y);
  ctx.restore();
}

// Pill-shaped label, e.g. "NEW!" or "TH19 ONLY".
function pill(ctx, str, x, y, size, bg = [C.red, '#B81E1E'], fg = C.white) {
  ctx.save();
  ctx.font = `${size}px ${FONT}`;
  const w = ctx.measureText(str).width + size * 1.1, h = size * 1.55;
  withT(ctx, x, y, 1, 0, () => {
    chunky(ctx, rectPath(-w / 2, -h / 2, w, h, h / 2), bg[0], bg[1], { lw: size * 0.14, y0: -h / 2, y1: h / 2 });
    // Dark text on a light pill gets a light outline; light text gets the usual dark one.
    const dark = fg === C.ink;
    title(ctx, str, 0, size * 0.04, size, { fill: fg, stroke: dark ? bg[0] : C.ink, lw: dark ? 0.01 : size * 0.12, shadow: false });
  });
  ctx.restore();
}

// ---- backgrounds & effects ------------------------------------------------------------
function background(ctx, t, { top = C.purpleLo, mid = C.purple, bottom = C.night, rays = true,
                              rayColor = 'rgba(255,214,120,0.10)', cx = W / 2, cy = H * 0.42 } = {}) {
  const g = ctx.createRadialGradient(cx, cy, 50, cx, cy, H * 0.85);
  g.addColorStop(0, mid);
  g.addColorStop(0.55, top);
  g.addColorStop(1, bottom);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  if (rays) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(t * 0.12);
    ctx.fillStyle = rayColor;
    for (let i = 0; i < 14; i++) {
      ctx.rotate((Math.PI * 2) / 14);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(-90, -H * 1.2);
      ctx.lineTo(90, -H * 1.2);
      ctx.closePath();
      ctx.fill();
    }
    ctx.restore();
  }
  // faint hexagon grid, drifting slowly
  ctx.save();
  ctx.strokeStyle = 'rgba(255,255,255,0.045)';
  ctx.lineWidth = 2;
  const s = 70, hgt = s * Math.sqrt(3), off = (t * 12) % hgt;
  for (let row = -1; row < H / hgt + 2; row++) {
    for (let col = -1; col < W / (s * 1.5) + 1; col++) {
      const x = col * s * 1.5, y = row * hgt + (col % 2 ? hgt / 2 : 0) + off;
      ctx.beginPath();
      for (let k = 0; k < 6; k++) {
        const a = (Math.PI / 3) * k;
        ctx.lineTo(x + Math.cos(a) * s * 0.92, y + Math.sin(a) * s * 0.92);
      }
      ctx.closePath();
      ctx.stroke();
    }
  }
  ctx.restore();
}

function vignette(ctx, strength = 0.65) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.75);
  g.addColorStop(0, 'rgba(0,0,0,0)');
  g.addColorStop(1, `rgba(0,0,0,${strength})`);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
}

// Drifting glowing sparks across the whole frame.
function sparks(ctx, t, { n = 70, seed = 7, color = '255,210,120', rise = 60, size = 5 } = {}) {
  const r = rng(seed);
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) {
    const x0 = r() * W, y0 = r() * H, sp = 0.4 + r(), ph = r() * 6.28, sz = size * (0.4 + r());
    const x = x0 + Math.sin(t * 0.8 + ph) * 25;
    const y = ((y0 - t * rise * sp) % H + H) % H;
    const a = 0.35 + 0.65 * Math.abs(Math.sin(t * 2 + ph));
    const g = ctx.createRadialGradient(x, y, 0, x, y, sz * 3);
    g.addColorStop(0, `rgba(${color},${a})`);
    g.addColorStop(1, `rgba(${color},0)`);
    ctx.fillStyle = g;
    ctx.fillRect(x - sz * 3, y - sz * 3, sz * 6, sz * 6);
  }
  ctx.restore();
}

// Radial particle explosion starting at time t0.
function burst(ctx, t, t0, x, y, { n = 40, color = '255,200,90', speed = 900, life = 0.9, seed = 3, size = 9 } = {}) {
  const k = (t - t0) / life;
  if (k < 0 || k > 1) return;
  const r = rng(seed);
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) {
    const a = r() * Math.PI * 2, v = speed * (0.35 + r() * 0.65), sz = size * (0.5 + r());
    const d = v * ease.outCubic(k) * life;
    const px = x + Math.cos(a) * d, py = y + Math.sin(a) * d + 300 * k * k;
    ctx.fillStyle = `rgba(${color},${1 - k})`;
    ctx.beginPath();
    ctx.arc(px, py, sz * (1 - k * 0.6), 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

// Expanding shockwave ring.
function ring(ctx, t, t0, x, y, { maxR = 650, life = 0.6, color = '255,230,160', width = 26 } = {}) {
  const k = (t - t0) / life;
  if (k < 0 || k > 1) return;
  ctx.save();
  ctx.strokeStyle = `rgba(${color},${1 - k})`;
  ctx.lineWidth = width * (1 - k) + 2;
  ctx.beginPath();
  ctx.arc(x, y, maxR * ease.outCubic(k), 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}

// Soft glow disc behind a hero element.
function glow(ctx, x, y, r, color = '255,200,90', a = 0.55) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, `rgba(${color},${a})`);
  g.addColorStop(1, `rgba(${color},0)`);
  ctx.fillStyle = g;
  ctx.fillRect(x - r, y - r, r * 2, r * 2);
}

function flash(ctx, t, t0, { life = 0.35, color = '255,255,255', peak = 0.85 } = {}) {
  const k = (t - t0) / life;
  if (k < 0 || k > 1) return;
  ctx.fillStyle = `rgba(${color},${peak * (1 - k)})`;
  ctx.fillRect(0, 0, W, H);
}

// Camera shake offset that decays after an impact at t0.
function shakeAt(t, t0, amp = 22, decay = 5) {
  if (t < t0) return [0, 0];
  const e = amp * Math.exp(-(t - t0) * decay);
  return [Math.sin(t * 61) * e, Math.cos(t * 47) * e];
}

// ---- icons (drawn centred on 0,0, roughly 200px tall at scale 1) ------------------------
const icon = {
  townHall(ctx, t = 0) {
    // keep
    chunky(ctx, rectPath(-150, -40, 300, 200, 14), C.stone, C.stoneLo, { y0: -40, y1: 160 });
    // side towers
    for (const sx of [-1, 1]) {
      chunky(ctx, rectPath(sx * 150 - 55, -120, 110, 280, 12), '#B3BBCC', C.stoneLo, { y0: -120, y1: 160 });
      chunky(ctx, polyPath([[sx * 150 - 72, -110], [sx * 150, -230], [sx * 150 + 72, -110]]), C.purpleHi, C.purple, { y0: -230, y1: -110 });
      chunky(ctx, rectPath(sx * 150 - 18, -60, 36, 56, 18), '#3B1E6E', C.purpleLo, { lw: 6, gloss: false, y0: -60, y1: -4 });
    }
    // central roof & spire
    chunky(ctx, polyPath([[-120, -40], [0, -200], [120, -40]]), C.gold, C.goldLo, { y0: -200, y1: -40 });
    chunky(ctx, rectPath(-10, -270, 20, 80, 6), C.goldHi, C.goldLo, { lw: 6, y0: -270, y1: -190 });
    const fl = Math.sin(t * 6) * 8;
    chunky(ctx, polyPath([[10, -268], [80, -250 + fl], [10, -226]]), C.red, '#B81E1E', { lw: 6, y0: -268, y1: -226 });
    // door with glowing light
    chunky(ctx, rectPath(-48, 50, 96, 110, 48), '#FFE08A', C.orange, { lw: 8, y0: 50, y1: 160 });
    // gold trim
    chunky(ctx, rectPath(-160, -50, 320, 26, 8), C.goldHi, C.goldLo, { lw: 7, y0: -50, y1: -24 });
  },
  sword(ctx) {
    chunky(ctx, polyPath([[-16, -150], [0, -190], [16, -150], [16, 40], [-16, 40]]), '#F2F6FF', '#9DA8C0', { y0: -190, y1: 40 });
    chunky(ctx, rectPath(-70, 36, 140, 28, 12), C.gold, C.goldLo, { lw: 8, y0: 36, y1: 64 });
    chunky(ctx, rectPath(-14, 62, 28, 80, 10), C.wood, C.woodLo, { lw: 8, y0: 62, y1: 142 });
    chunky(ctx, rectPath(-24, 138, 48, 34, 17), C.gold, C.goldLo, { lw: 8, y0: 138, y1: 172 });
  },
  bow(ctx) {
    const p = new Path2D();
    p.moveTo(-30, -170);
    p.quadraticCurveTo(120, 0, -30, 170);
    p.lineTo(-10, 170);
    p.quadraticCurveTo(140, 0, -10, -170);
    p.closePath();
    chunky(ctx, p, C.wood, C.woodLo, { y0: -170, y1: 170 });
    ctx.strokeStyle = '#EDE3D0';
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.moveTo(-26, -166);
    ctx.lineTo(-26, 166);
    ctx.stroke();
    chunky(ctx, rectPath(-110, -7, 170, 14, 6), C.wood, C.woodLo, { lw: 6, gloss: false, y0: -7, y1: 7 });
    chunky(ctx, polyPath([[60, -20], [100, 0], [60, 20]]), '#E8EEF8', '#9DA8C0', { lw: 6, y0: -20, y1: 20 });
    chunky(ctx, polyPath([[-110, -7], [-140, -30], [-128, 0], [-140, 30], [-110, 7]]), C.red, '#B81E1E', { lw: 6, y0: -30, y1: 30 });
  },
  staff(ctx, t = 0) {
    chunky(ctx, rectPath(-13, -110, 26, 280, 10), C.wood, C.woodLo, { y0: -110, y1: 170 });
    glow(ctx, 0, -150, 120, '120,200,255', 0.7 + 0.2 * Math.sin(t * 5));
    const orb = new Path2D();
    orb.arc(0, -150, 52, 0, Math.PI * 2);
    chunky(ctx, orb, '#D8F3FF', C.blue, { y0: -202, y1: -98 });
    chunky(ctx, polyPath([[-40, -110], [-60, -150], [-30, -120]]), C.gold, C.goldLo, { lw: 6 });
    chunky(ctx, polyPath([[40, -110], [60, -150], [30, -120]]), C.gold, C.goldLo, { lw: 6 });
  },
  crown(ctx) {
    const p = polyPath([[-150, 80], [-170, -70], [-85, 5], [0, -110], [85, 5], [170, -70], [150, 80]]);
    chunky(ctx, p, C.goldHi, C.goldLo, { y0: -110, y1: 80 });
    chunky(ctx, rectPath(-160, 70, 320, 50, 14), C.gold, C.goldLo, { y0: 70, y1: 120 });
    for (const [x, y, c] of [[-170, -70, C.red], [0, -110, C.blue], [170, -70, C.green]]) {
      const g = new Path2D();
      g.arc(x, y, 20, 0, Math.PI * 2);
      chunky(ctx, g, '#FFFFFF', c, { lw: 6, y0: y - 20, y1: y + 20 });
    }
    for (const x of [-90, 0, 90]) {
      const g = new Path2D();
      g.arc(x, 95, 14, 0, Math.PI * 2);
      chunky(ctx, g, '#FFFFFF', C.purple, { lw: 5, y0: 81, y1: 109 });
    }
  },
  spikyTower(ctx) {
    chunky(ctx, polyPath([[-90, 170], [-70, -90], [70, -90], [90, 170]]), '#AEB6C8', C.stoneLo, { y0: -90, y1: 170 });
    chunky(ctx, rectPath(-105, -130, 210, 50, 10), '#C8CFDD', C.stoneLo, { y0: -130, y1: -80 });
    for (let i = -3; i <= 3; i++) {
      chunky(ctx, polyPath([[i * 30 - 14, -128], [i * 30, -200 - (i % 2 ? 0 : 20)], [i * 30 + 14, -128]]), '#F2F6FF', '#8892A8', { lw: 6, y0: -220, y1: -128 });
    }
    for (const [y, dir] of [[0, -1], [0, 1], [90, -1], [90, 1]]) {
      chunky(ctx, polyPath([[dir * 70, y - 16], [dir * 135, y], [dir * 70, y + 16]]), '#F2F6FF', '#8892A8', { lw: 6, y0: y - 16, y1: y + 16 });
    }
  },
  firecrackerTower(ctx) {
    chunky(ctx, polyPath([[-85, 170], [-65, -40], [65, -40], [85, 170]]), C.wood, C.woodLo, { y0: -40, y1: 170 });
    chunky(ctx, rectPath(-100, -70, 200, 44, 10), C.red, '#9E1414', { y0: -70, y1: -26 });
    // rocket launcher tubes
    for (const [x, c] of [[-50, C.red], [0, C.gold], [50, C.blue]]) {
      withT(ctx, x, -90, 1, x * 0.004, () => {
        chunky(ctx, rectPath(-20, -110, 40, 110, 10), c, '#55331A', { lw: 7, y0: -110, y1: 0 });
      });
    }
  },
  rocket(ctx, color = C.red) {
    chunky(ctx, rectPath(-14, -40, 28, 80, 8), color, '#55331A', { lw: 6, y0: -40, y1: 40 });
    chunky(ctx, polyPath([[-14, -40], [0, -70], [14, -40]]), C.goldHi, C.goldLo, { lw: 6, y0: -70, y1: -40 });
  },
  shrine(ctx, t = 0) {
    chunky(ctx, rectPath(-170, 110, 340, 50, 12), '#C8CFDD', C.stoneLo, { y0: 110, y1: 160 });
    for (const x of [-120, 120]) chunky(ctx, rectPath(x - 22, -60, 44, 175, 10), '#E5E9F2', '#8E97AB', { y0: -60, y1: 115 });
    chunky(ctx, polyPath([[-190, -60], [0, -170], [190, -60]]), C.purpleHi, C.purple, { y0: -170, y1: -60 });
    glow(ctx, 0, 30, 140, '160,120,255', 0.6 + 0.2 * Math.sin(t * 4));
    const gem = polyPath([[0, -40], [45, 30], [0, 100], [-45, 30]]);
    chunky(ctx, gem, '#F1E6FF', C.purple, { lw: 7, y0: -40, y1: 100 });
  },
  cake(ctx) {
    chunky(ctx, rectPath(-120, -10, 240, 110, 18), '#FFD9A8', '#D9935A', { y0: -10, y1: 100 });
    chunky(ctx, rectPath(-130, -50, 260, 60, 28), '#FF8FC8', '#E0478F', { y0: -50, y1: 10 });
    const ch = new Path2D();
    ch.arc(0, -78, 30, 0, Math.PI * 2);
    chunky(ctx, ch, '#FF6B6B', '#B81E1E', { lw: 7, y0: -108, y1: -48 });
  },
  lollipop(ctx, t = 0) {
    chunky(ctx, rectPath(-10, 0, 20, 180, 8), '#FFFFFF', '#C9CED8', { lw: 7, y0: 0, y1: 180 });
    const c = new Path2D();
    c.arc(0, -40, 90, 0, Math.PI * 2);
    chunky(ctx, c, '#B98BFF', C.purple, { y0: -130, y1: 50 });
    ctx.save();
    ctx.clip(c);
    ctx.strokeStyle = 'rgba(255,255,255,0.75)';
    ctx.lineWidth = 14;
    ctx.beginPath();
    for (let a = 0; a < 18; a += 0.1) ctx.lineTo(Math.cos(a + t * 2) * a * 5, -40 + Math.sin(a + t * 2) * a * 5);
    ctx.stroke();
    ctx.restore();
  },
  star(ctx) {
    chunky(ctx, starPath(120, 52), C.goldHi, C.goldLo, { y0: -120, y1: 110 });
  },
  barracks(ctx) {
    chunky(ctx, rectPath(-160, -30, 320, 190, 14), C.wood, C.woodLo, { y0: -30, y1: 160 });
    chunky(ctx, polyPath([[-190, -20], [0, -170], [190, -20]]), C.red, '#9E1414', { y0: -170, y1: -20 });
    chunky(ctx, rectPath(-55, 50, 110, 110, 55), '#3A1E0C', '#1E0E05', { lw: 8, gloss: false, y0: 50, y1: 160 });
    for (const x of [-120, 120]) chunky(ctx, rectPath(x - 25, 20, 50, 50, 8), '#FFE08A', C.orange, { lw: 7, y0: 20, y1: 70 });
  },
  lock(ctx) {
    ctx.lineWidth = 34;
    ctx.strokeStyle = C.ink;
    ctx.beginPath();
    ctx.arc(0, -40, 70, Math.PI, 0);
    ctx.stroke();
    ctx.lineWidth = 20;
    ctx.strokeStyle = '#C8CFDD';
    ctx.stroke();
    chunky(ctx, rectPath(-100, -40, 200, 160, 24), C.gold, C.goldLo, { y0: -40, y1: 120 });
    chunky(ctx, rectPath(-14, 10, 28, 60, 14), C.ink, C.ink, { lw: 4, gloss: false });
  },
  tap(ctx, t = 0) {
    // hand pointer
    const p = new Path2D();
    p.moveTo(-20, -120);
    p.quadraticCurveTo(0, -150, 20, -120);
    p.lineTo(20, -20);
    p.lineTo(80, -10);
    p.quadraticCurveTo(110, 0, 100, 60);
    p.lineTo(80, 140);
    p.lineTo(-40, 140);
    p.lineTo(-90, 40);
    p.quadraticCurveTo(-100, 10, -70, 10);
    p.lineTo(-20, 50);
    p.closePath();
    chunky(ctx, p, '#FFE3C8', '#E3A97A', { y0: -150, y1: 140 });
  },
  chat(ctx) {
    const p = new Path2D();
    p.roundRect(-150, -110, 300, 190, 50);
    p.moveTo(-60, 78);
    p.lineTo(-100, 140);
    p.lineTo(0, 78);
    chunky(ctx, p, '#FFFFFF', '#C9D3E6', { y0: -110, y1: 140 });
    for (const x of [-70, 0, 70]) {
      const d = new Path2D();
      d.arc(x, -15, 18, 0, Math.PI * 2);
      ctx.fillStyle = C.purple;
      ctx.fill(d);
    }
  },
};

// Round troop token with an icon inside (for armies and squads).
function token(ctx, kind, t = 0) {
  const c = new Path2D();
  c.arc(0, 0, 70, 0, Math.PI * 2);
  const colors = { sword: [C.orange, '#B85A0B'], bow: ['#FF7EC0', '#C23C82'], staff: [C.blue, '#2370B8'] }[kind];
  chunky(ctx, c, colors[0], colors[1], { lw: 9, y0: -70, y1: 70 });
  withT(ctx, 0, 0, 0.3, kind === 'bow' ? 0 : -0.6, () => icon[kind](ctx, t));
}

// ---- official art ---------------------------------------------------------------------------
// A page lists the images it uses in window.ART = {name: 'relative/path.png'}; they load before frame 0.
// art() draws an image scaled (never recoloured or cropped) and centred on its visible pixels, so
// renders with lots of transparent padding still line up.
const ARTS = {};

function loadArt() {
  const entries = Object.entries(window.ART || {});
  return Promise.all(entries.map(([name, src]) => new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      // Find the bounding box of non-transparent pixels on a small copy.
      const s = 256 / Math.max(img.width, img.height);
      const w = Math.max(1, Math.round(img.width * s)), h = Math.max(1, Math.round(img.height * s));
      const c = document.createElement('canvas');
      c.width = w; c.height = h;
      const g = c.getContext('2d');
      g.drawImage(img, 0, 0, w, h);
      const px = g.getImageData(0, 0, w, h).data;
      let x0 = w, y0 = h, x1 = 0, y1 = 0;
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        if (px[(y * w + x) * 4 + 3] > 12) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
      }
      ARTS[name] = { img, box: [x0 / s, y0 / s, (x1 + 1) / s, (y1 + 1) / s] };
      resolve();
    };
    img.onerror = () => reject(new Error(`art '${name}' failed to load: ${src}`));
    img.src = src;
  })));
}

// Draw art `name` so its visible part is `h` px tall, centred at (x, y). opts: {alpha, rot, flip, shadow}
function art(ctx, name, x, y, h, opts = {}) {
  const a = ARTS[name];
  if (!a) throw new Error(`unknown art '${name}'`);
  const [bx0, by0, bx1, by1] = a.box;
  const s = h / (by1 - by0);
  ctx.save();
  ctx.translate(x, y);
  if (opts.rot) ctx.rotate(opts.rot);
  if (opts.flip) ctx.scale(-1, 1);
  if (opts.alpha !== undefined) ctx.globalAlpha *= opts.alpha;
  if (opts.shadow !== false) {
    // soft contact shadow under the art
    const sw = (bx1 - bx0) * s * 0.42;
    const g = ctx.createRadialGradient(0, h / 2, 0, 0, h / 2, sw);
    g.addColorStop(0, 'rgba(0,0,0,0.45)');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.save(); ctx.scale(1, 0.22); ctx.fillStyle = g; ctx.fillRect(-sw, h / 2 / 0.22 - sw, sw * 2, sw * 2); ctx.restore();
  }
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(a.img, -((bx0 + bx1) / 2) * s, -((by0 + by1) / 2) * s, a.img.width * s, a.img.height * s);
  ctx.restore();
}

// Width the visible part of art `name` takes when drawn `h` tall.
const artWidth = (name, h) => { const [x0, y0, x1, y1] = ARTS[name].box; return (x1 - x0) * h / (y1 - y0); };

// ---- scene framework -------------------------------------------------------------------
// A project page defines `scenes = [(ctx, t, dur) => {...}, ...]` and includes this file.
// The renderer calls window.seek(t) for each frame and screenshots the canvas.
function setupStage() {
  const params = new URLSearchParams(location.search);
  const sceneIdx = Number(params.get('scene') || 0);
  const dur = Number(params.get('dur') || 6);
  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = H;
  document.body.style.margin = '0';
  document.body.style.background = '#000';
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');
  window.seek = t => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'source-over';
    ctx.clearRect(0, 0, W, H);
    // Slow camera push-in over the whole scene.
    const z = 1 + 0.035 * (t / dur);
    ctx.translate(W / 2, H / 2);
    ctx.scale(z, z);
    ctx.translate(-W / 2, -H / 2);
    window.scenes[sceneIdx](ctx, t, dur);
  };
  // Make sure the display font is loaded before the first frame.
  Promise.all([document.fonts.load(`100px ${FONT}`), loadArt()])
    .then(() => { window.seek(0); window.ready = true; })
    .catch(e => { window.loadError = String(e); });
}
window.addEventListener('DOMContentLoaded', setupStage);
