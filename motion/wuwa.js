// Shared look for the Wuthering Waves lore series (load after lib.js).
// Full-frame press-kit art with slow camera moves, serif titles, glass labels, petals and butterflies,
// and an art credit on every frame.
/* eslint-disable no-unused-vars */
const SERIF = 'Caladea, serif';
const LAV = ['#FFFFFF', '#F1E4FF', '#C9A7FF'];
window.FONTS = (window.FONTS || []).concat(['bold 100px Caladea', 'italic 100px Caladea']);

// Full-frame image with a slow camera move: focus (fx, fy) in 0..1 image coords, zoom >= 1 over "cover".
// box = [x0, y0, x1, y1] (0..1) limits the move to part of the image; defaults to the whole image.
function cover(ctx, name, t, dur, from, to, opts = {}) {
  const img = ARTS[name].img;
  const k = ease.inOutCubic(clamp(t / dur));
  const fx = lerp(from[0], to[0], k), fy = lerp(from[1], to[1], k), z = lerp(from[2], to[2], k);
  const s = Math.max(W / img.width, H / img.height) * z;
  let x = W / 2 - fx * img.width * s, y = H / 2 - fy * img.height * s;
  x = Math.min(0, Math.max(W - img.width * s, x));
  y = Math.min(0, Math.max(H - img.height * s, y));
  ctx.save();
  if (opts.clip) ctx.clip(opts.clip);
  if (opts.filter) ctx.filter = opts.filter;
  if (opts.alpha !== undefined) ctx.globalAlpha = opts.alpha;
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(img, x, y, img.width * s, img.height * s);
  ctx.restore();
}

// Draw an image into a region (rx, ry, rw, rh) like "cover", with its own slow zoom.
function coverIn(ctx, name, rx, ry, rw, rh, fx, fy, z) {
  const img = ARTS[name].img;
  const s = Math.max(rw / img.width, rh / img.height) * z;
  let x = rx + rw / 2 - fx * img.width * s, y = ry + rh / 2 - fy * img.height * s;
  x = Math.min(rx, Math.max(rx + rw - img.width * s, x));
  y = Math.min(ry, Math.max(ry + rh - img.height * s, y));
  ctx.save();
  ctx.beginPath(); ctx.rect(rx, ry, rw, rh); ctx.clip();
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(img, x, y, img.width * s, img.height * s);
  ctx.restore();
}

function serif(ctx, str, x, y, size, { alpha = 1, fill = LAV, italic = false, glowColor = 'rgba(190,150,255,0.9)' } = {}) {
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.font = `${italic ? 'italic' : 'bold'} ${size}px ${SERIF}`;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  if ('letterSpacing' in ctx) ctx.letterSpacing = `${size * 0.04}px`;
  ctx.shadowColor = glowColor; ctx.shadowBlur = size * 0.35;
  ctx.lineWidth = size * 0.06; ctx.strokeStyle = 'rgba(30,10,60,0.85)';
  ctx.strokeText(str, x, y);
  ctx.shadowBlur = 0;
  ctx.fillStyle = vgrad(ctx, y - size / 2, y + size / 2, fill.map((c, i) => [i / (fill.length - 1), c]));
  ctx.fillText(str, x, y);
  ctx.restore();
}

function plate(ctx, str, x, y, t, t0, size = 46, { border = 'rgba(220,190,255,0.85)', bg = 'rgba(20,8,45,0.62)', color = '#F4EAFF' } = {}) {
  const k = ease.outCubic(prog(t, t0, 0.5));
  if (k <= 0) return;
  ctx.save();
  ctx.globalAlpha = k;
  ctx.font = `bold ${size}px ${SERIF}`;
  if ('letterSpacing' in ctx) ctx.letterSpacing = `${size * 0.12}px`;
  const w = ctx.measureText(str).width + size * 1.6, h = size * 1.7, yy = y + (1 - k) * 30;
  ctx.fillStyle = bg; ctx.fill(rectPath(x - w / 2, yy - h / 2, w, h, h / 2));
  ctx.lineWidth = 3; ctx.strokeStyle = border; ctx.stroke(rectPath(x - w / 2, yy - h / 2, w, h, h / 2));
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = color;
  ctx.fillText(str, x, yy + 2);
  ctx.restore();
}

function petals(ctx, t, { n = 26, seed = 11, speed = 70 } = {}) {
  const r = rng(seed);
  for (let i = 0; i < n; i++) {
    const x0 = r() * W, y0 = r() * H, sz = 10 + r() * 16, sp = 0.5 + r(), ph = r() * 6.28;
    const x = x0 + Math.sin(t * 0.7 + ph) * 60, y = ((y0 + t * speed * sp) % (H + 100)) - 50;
    withT(ctx, x, y, 1, t * (0.6 + r()) + ph, () => {
      ctx.fillStyle = `rgba(255,250,255,${0.45 + 0.35 * Math.sin(t * 2 + ph) ** 2})`;
      ctx.beginPath(); ctx.ellipse(0, 0, sz, sz * 0.45, 0, 0, Math.PI * 2); ctx.fill();
    });
  }
}

function butterfly(ctx, t, x, y, s = 1, ph = 0) {
  const flap = Math.abs(Math.sin(t * 9 + ph));
  withT(ctx, x + Math.sin(t * 0.9 + ph) * 80, y + Math.sin(t * 1.4 + ph) * 50, s, Math.sin(t + ph) * 0.3, () => {
    glow(ctx, 0, 0, 60, '120,170,255', 0.5);
    for (const side of [-1, 1]) {
      ctx.save(); ctx.scale(side * (0.25 + 0.75 * flap), 1);
      const g = ctx.createLinearGradient(0, -30, 40, 20);
      g.addColorStop(0, '#BFE3FF'); g.addColorStop(1, '#2F5BFF');
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.ellipse(22, -12, 24, 16, -0.5, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(16, 12, 14, 10, 0.5, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }
    ctx.fillStyle = '#1A1030'; ctx.fillRect(-2, -16, 4, 30);
  });
}

function credit(ctx, text = 'Art © Kuro Games · official Wuthering Waves press kit') {
  ctx.save();
  ctx.font = `22px ${FONT}`; ctx.textAlign = 'center'; ctx.fillStyle = 'rgba(255,255,255,0.75)';
  ctx.shadowColor = 'rgba(0,0,0,0.8)'; ctx.shadowBlur = 6;
  ctx.fillText(text, W / 2, H - 70);
  ctx.restore();
}

function finish(ctx, { wash = 0.12 } = {}) {
  ctx.fillStyle = `rgba(60,20,110,${wash})`; ctx.fillRect(0, 0, W, H);
  vignette(ctx, 0.7);
  credit(ctx);
}
