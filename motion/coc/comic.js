// Comic-book kit for the Clash of Clans fan-comic series (load after lib.js).
// Pages are drawn on cream paper with halftone dots; panels have thick ink borders, pop in, and clip their
// contents; speech bubbles, caption boxes and sound-effect words use the game's chunky display font.
// Layout rule: captions are burned in around y = 1300-1440, so pages use a top tier (y 90-1270) and a
// bottom tier (y 1460-1840) with the caption band in the gutter between them.
/* eslint-disable no-unused-vars */
const INK = '#14100C';
const PAPER = '#F4E7C8';
const TOP = [40, 90, 1000, 1180];      // x, y, w, h of the full top tier
const BOT = [40, 1460, 1000, 380];     // full bottom tier

function paper(ctx, t) {
  ctx.fillStyle = PAPER; ctx.fillRect(-40, -40, W + 80, H + 80);
  // Halftone dots.
  ctx.fillStyle = 'rgba(160,110,40,0.10)';
  for (let y = 0; y < H; y += 22) for (let x = (y / 22) % 2 ? 11 : 0; x < W; x += 22) { ctx.beginPath(); ctx.arc(x, y, 3.2, 0, Math.PI * 2); ctx.fill(); }
}

// Panel that pops in at t0; draw(ctx, x, y, w, h) runs clipped inside it.
function panel(ctx, t, t0, x, y, w, h, draw, { bg = '#FFFFFF', from = 'scale', tilt = 0 } = {}) {
  const k = from === 'none' ? 1 : ease.outBack(prog(t, t0, 0.45));
  if (k <= 0) return;
  ctx.save();
  const cx = x + w / 2, cy = y + h / 2;
  ctx.translate(cx, cy); ctx.rotate(tilt * (1 - Math.min(1, k))); ctx.scale(k, k); ctx.translate(-cx, -cy);
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(x + 12, y + 14, w, h);
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  ctx.fillStyle = bg; ctx.fillRect(x, y, w, h);
  draw(ctx, x, y, w, h);
  ctx.restore();
  ctx.lineWidth = 10; ctx.strokeStyle = INK; ctx.strokeRect(x, y, w, h);
  ctx.restore();
}

// Backgrounds for inside panels.
function sky(ctx, x, y, w, h, top = '#7FD0FF', bot = '#DFF4FF') { ctx.fillStyle = vgrad(ctx, y, y + h, [[0, top], [1, bot]]); ctx.fillRect(x, y, w, h); }
function speedLines(ctx, x, y, w, h, cx, cy, t, col = 'rgba(20,16,12,0.16)', n = 48) {
  const r = rng(Math.floor(t * 10) + 7);
  ctx.save(); ctx.fillStyle = col;
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2 + r() * 0.05, a2 = a + 0.025 + r() * 0.02, R = Math.hypot(w, h);
    ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * 140, cy + Math.sin(a) * 140);
    ctx.lineTo(cx + Math.cos(a) * R, cy + Math.sin(a) * R); ctx.lineTo(cx + Math.cos(a2) * R, cy + Math.sin(a2) * R); ctx.fill();
  }
  ctx.restore();
}
function sunburst(ctx, cx, cy, t, c1 = '#FFD86B', c2 = '#FFC23A', n = 18) {
  const R = 2200;
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(t * 0.15);
  for (let i = 0; i < n; i++) { ctx.fillStyle = i % 2 ? c1 : c2; ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, R, (i / n) * Math.PI * 2, ((i + 1) / n) * Math.PI * 2); ctx.fill(); }
  ctx.restore();
}
// Cover-fit an image inside a rect, focused on (fx, fy) with zoom z.
function coverRect(ctx, name, x, y, w, h, fx = 0.5, fy = 0.5, z = 1) {
  const img = ARTS[name].img, s = Math.max(w / img.width, h / img.height) * z;
  let dx = x + w / 2 - fx * img.width * s, dy = y + h / 2 - fy * img.height * s;
  dx = Math.min(x, Math.max(x + w - img.width * s, dx)); dy = Math.min(y, Math.max(y + h - img.height * s, dy));
  ctx.imageSmoothingQuality = 'high'; ctx.drawImage(img, dx, dy, img.width * s, img.height * s);
}

// Wrap words to lines that fit maxW at the current font.
function wrap(ctx, str, maxW) {
  const out = [];
  for (const para of str.split('\n')) {
    let line = '';
    for (const w of para.split(' ')) { const tst = line ? line + ' ' + w : w; if (ctx.measureText(tst).width > maxW && line) { out.push(line); line = w; } else line = tst; }
    out.push(line);
  }
  return out;
}

// Speech bubble centred at (x, y), max width mw, tail pointing to (tx, ty). shout = spiky outline.
function bubble(ctx, t, t0, x, y, str, tx, ty, { size = 46, mw = 520, shout = false, fill = '#FFFFFF', color = INK } = {}) {
  const k = ease.outBack(prog(t, t0, 0.35));
  if (k <= 0) return;
  ctx.save();
  ctx.font = `${size}px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const lines = wrap(ctx, str.toUpperCase(), mw);
  const bw = Math.max(...lines.map(l => ctx.measureText(l).width)) + size * 1.3, bh = lines.length * size * 1.12 + size * 0.95;
  ctx.translate(x, y); ctx.scale(k, k);
  const path = new Path2D();
  if (shout) {
    const n = 22;
    for (let i = 0; i <= n; i++) {
      const a = (i / n) * Math.PI * 2, r = i % 2 ? 0.82 : 1.08;
      const px = Math.cos(a) * bw * 0.62 * r, py = Math.sin(a) * bh * 0.72 * r;
      i ? path.lineTo(px, py) : path.moveTo(px, py);
    }
    path.closePath();
  } else path.ellipse(0, 0, bw * 0.58, bh * 0.62, 0, 0, Math.PI * 2);
  // Tail.
  const lx = (tx - x) / k, ly = (ty - y) / k, ang = Math.atan2(ly, lx), base = Math.min(bw, bh) * 0.16;
  const tail = new Path2D();
  tail.moveTo(Math.cos(ang + Math.PI / 2) * base, Math.sin(ang + Math.PI / 2) * base);
  tail.lineTo(lx * 0.92, ly * 0.92);
  tail.lineTo(Math.cos(ang - Math.PI / 2) * base, Math.sin(ang - Math.PI / 2) * base);
  ctx.lineJoin = 'round'; ctx.lineWidth = 8; ctx.strokeStyle = INK;
  ctx.stroke(tail); ctx.stroke(path);
  ctx.fillStyle = fill; ctx.fill(tail); ctx.fill(path);
  ctx.fillStyle = color;
  lines.forEach((l, i) => ctx.fillText(l, 0, (i - (lines.length - 1) / 2) * size * 1.12 + size * 0.05));
  ctx.restore();
}

// Yellow narration/caption box anchored at its top-left corner.
function capBox(ctx, t, t0, x, y, str, { size = 34, bg = '#FFE15A' } = {}) {
  const k = ease.outCubic(prog(t, t0, 0.3));
  if (k <= 0) return;
  ctx.save(); ctx.globalAlpha *= k;
  ctx.font = `${size}px ${FONT}`; ctx.textBaseline = 'middle';
  const w = ctx.measureText(str.toUpperCase()).width + size * 1.0, h = size * 1.7;
  ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.fillRect(x + 6, y + 6, w, h);
  ctx.fillStyle = bg; ctx.fillRect(x, y, w, h);
  ctx.lineWidth = 6; ctx.strokeStyle = INK; ctx.strokeRect(x, y, w, h);
  ctx.fillStyle = INK; ctx.fillText(str.toUpperCase(), x + size * 0.5, y + h / 2 + 2);
  ctx.restore();
}

// Big sound-effect word.
function sfxWord(ctx, t, t0, str, x, y, size, rot = -0.12, fill = ['#FFF6A0', '#FFC83D', '#FF7A1E']) {
  const k = ease.outBack(prog(t, t0, 0.3), 3);
  if (k <= 0) return;
  withT(ctx, x, y, k, rot, () => title(ctx, str, 0, 0, size, { fill, lw: size * 0.2 }));
}

function crown(ctx, x, y, s) {
  withT(ctx, x, y, s, 0, () => {
    glow(ctx, 0, 0, 120, '255,210,90', 0.5);
    ctx.fillStyle = '#FFC83D'; ctx.strokeStyle = INK; ctx.lineWidth = 8; ctx.lineJoin = 'round';
    const p = polyPath([[-80, 40], [-90, -40], [-45, 0], [0, -60], [45, 0], [90, -40], [80, 40]]);
    ctx.fill(p); ctx.stroke(p);
    ctx.fillStyle = '#FF4D4D'; [[-45, 18], [0, 12], [45, 18]].forEach(([cx, cy]) => { ctx.beginPath(); ctx.arc(cx, cy, 10, 0, Math.PI * 2); ctx.fill(); ctx.stroke(); });
  });
}

function comicCredit(ctx) {
  ctx.save(); ctx.font = `22px ${FONT}`; ctx.textAlign = 'center'; ctx.fillStyle = 'rgba(40,30,20,0.6)';
  ctx.fillText('Fan comic · Art: Supercell Fan Kit · Not endorsed by Supercell', W / 2, H - 40);
  ctx.restore();
}
