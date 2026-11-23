// Data-driven comic pages (load after lib.js and comic.js).
// An episode page is a generic HTML shell that calls comicEpisode('script.json', 'fankit.json'): every scene's
// "page" object in the script describes its panels, art, bubbles and effects, so long episodes are written as
// data instead of hand-coded scenes. Times ("at") accept: seconds, "line:N[+/-s]" (start of dialogue line N),
// "lineend:N[+/-s]", "word:foo[#n][+/-s]", or "end-s" (seconds before the scene ends).
/* eslint-disable no-unused-vars */
function loadJSONSync(url) { const x = new XMLHttpRequest(); x.open('GET', url, false); x.send(); return JSON.parse(x.responseText); }

const WIDE = W > H;
// Usable page area: wide pages leave the bottom band for narrator subtitles.
const AREA = WIDE ? [40, 30, W - 80, 880] : [40, 110, 1000, 1330];
const GAP = 26;
const LAYOUTS = {
  '1': [[0, 0, 1, 1]],
  '2': [[0, 0, .5, 1], [.5, 0, .5, 1]],
  '2v': [[0, 0, 1, .5], [0, .5, 1, .5]],
  '3v': [[0, 0, 1, 1 / 3], [0, 1 / 3, 1, 1 / 3], [0, 2 / 3, 1, 1 / 3]],
  '3': [[0, 0, 1 / 3, 1], [1 / 3, 0, 1 / 3, 1], [2 / 3, 0, 1 / 3, 1]],
  '1+2': [[0, 0, .58, 1], [.58, 0, .42, .5], [.58, .5, .42, .5]],
  '2+1': [[0, 0, .42, .5], [0, .5, .42, .5], [.42, 0, .58, 1]],
  '4': [[0, 0, .5, .5], [.5, 0, .5, .5], [0, .5, .5, .5], [.5, .5, .5, .5]],
  '1/2': [[0, 0, 1, .56], [0, .56, .5, .44], [.5, .56, .5, .44]],
  '2/1': [[0, 0, .5, .44], [.5, 0, .5, .44], [0, .44, 1, .56]],
  '1/3': [[0, 0, 1, .56], [0, .56, 1 / 3, .44], [1 / 3, .56, 1 / 3, .44], [2 / 3, .56, 1 / 3, .44]],
};
function layoutRects(name) {
  const [ax, ay, aw, ah] = AREA;
  return (LAYOUTS[name] || LAYOUTS['1']).map(([fx, fy, fw, fh]) => {
    const x = ax + fx * aw + (fx > 0 ? GAP / 2 : 0), y = ay + fy * ah + (fy > 0 ? GAP / 2 : 0);
    const w = fw * aw - (fx > 0 ? GAP / 2 : 0) - (fx + fw < 0.999 ? GAP / 2 : 0);
    const h = fh * ah - (fy > 0 ? GAP / 2 : 0) - (fy + fh < 0.999 ? GAP / 2 : 0);
    return [x, y, w, h];
  });
}

// Resolve a time anchor to seconds within the scene.
function T(v, dur, dflt = 0) {
  if (v === undefined || v === null) return dflt;
  if (typeof v === 'number') return v;
  const m = String(v).match(/^(line|lineend|word|end)(?::([^+\-#]+))?(?:#(\d+))?([+-][\d.]+)?$/);
  if (!m) return dflt;
  const off = m[4] ? Number(m[4]) : 0, L = window.LINES || [];
  if (m[1] === 'line') { const l = L[Number(m[2])]; return (l ? l[2] : dflt) + off; }
  if (m[1] === 'lineend') { const l = L[Number(m[2])]; return (l ? l[3] : dflt) + off; }
  if (m[1] === 'word') return when(m[2], m[3] ? Number(m[3]) - 1 : 0, dflt) + off;
  if (m[1] === 'end') return dur + (m[4] ? Number(m[4]) : 0);
  return dflt;
}
const nums = s => String(s).split(',').map(Number);

// Panel backgrounds by name.
const SKIES = {
  day: ['#7FD0FF', '#DFF4FF'], dawn: ['#FFB98A', '#FFE9C8'], dusk: ['#5B3B7A', '#F2996B'], night: ['#0E1638', '#33427A'],
  storm: ['#0B1230', '#2C3A6E'], dark: ['#05030C', '#0D0A1A'], warm: ['#FFE7B8', '#FFF4DC'], cool: ['#EBDDFF', '#F6F0FF'],
  red: ['#FFD2C2', '#FFF0E8'], green: ['#D8F5C8', '#F2FFEC'], ash: ['#2B2622', '#4A4038'], gloom: ['#2E2A4A', '#5A5480'],
  paper: ['#F2DFAE', '#F2DFAE'], ice: ['#BFE6FF', '#EAF7FF'], gold: ['#FFE08A', '#FFF6D8'], purple: ['#3A2466', '#7A55B8'],
};
const BURSTS = { gold: ['#FFCF7A', '#FFB347'], purple: ['#D9B8FF', '#B894FF'], blue: ['#BFE6FF', '#8FCBFF'], green: ['#9EE89A', '#6FD06A'],
  red: ['#FFB0A0', '#FF8A7A'], orange: ['#FFB65C', '#FF9A3A'], pink: ['#FFC6E0', '#FF9CC8'], grey: ['#D8D8D8', '#BDBDBD'] };
const SFX_STYLES = { zap: ['#FFFFFF', '#BFE6FF', '#2E8BFF'], fire: ['#FFF6A0', '#FFC83D', '#FF7A1E'], green: ['#E8FFE0', '#9BE08A', '#3E9A3A'],
  red: ['#FFFFFF', '#FF9A9A', '#E02E2E'], gold: ['#FFFFFF', '#FFD86B', '#FF8A1E'], purple: ['#FFFFFF', '#D9B8FF', '#8A4BE0'], white: ['#FFFFFF', '#EEEEEE', '#AAAAAA'] };

function drawBg(c, t, bg, x, y, w, h) {
  const [kind, arg] = String(bg || 'warm').split(':');
  if (kind === 'burst') { const [a, b] = BURSTS[arg] || BURSTS.gold; c.fillStyle = b; c.fillRect(x, y, w, h); sunburst(c, x + w / 2, y + h * 0.6, t, a, b); return; }
  if (kind === 'img') { const [name, at] = arg.split('@'); const [fx, fy, z] = at ? nums(at) : [0.5, 0.5, 1.15]; coverRect(c, name, x, y, w, h, fx, fy, z + 0.03 * t / 10); return; }
  const [top, bot] = SKIES[kind] || SKIES.warm; sky(c, x, y, w, h, top, bot);
}

// Effects, each "name:args@at".
function drawFx(c, t, dur, fx, x, y, w, h, seedBase) {
  for (const [i, f] of (fx || []).entries()) {
    const [head, atS] = f.split('@'), [name, argS] = head.split(':'), at = T(atS, dur, 0), a = argS ? nums(argS) : [];
    const P = (fx, fy) => [x + fx * w, y + fy * h];
    if (t < at) continue;
    const k = prog(t, at, 0.4);
    if (name === 'speed') { const [cx, cy] = a.length ? P(a[0], a[1]) : P(0.5, 0.5); speedLines(c, x, y, w, h, cx, cy, t, a[2] ? `rgba(255,255,255,${a[2]})` : undefined); }
    else if (name === 'stars') { const r = rng(seedBase + i); for (let j = 0; j < 40; j++) { c.fillStyle = `rgba(255,255,255,${0.35 + 0.5 * r() * (0.6 + 0.4 * Math.sin(t * 2 + j))})`; c.beginPath(); c.arc(x + r() * w, y + r() * h * 0.6, 1.5 + r() * 2.5, 0, Math.PI * 2); c.fill(); } }
    else if (name === 'moon') { const [mx, my] = P(a[0] ?? 0.8, a[1] ?? 0.18); glow(c, mx, my, 160, '240,240,210', 0.5); c.fillStyle = '#FFF8DC'; c.beginPath(); c.arc(mx, my, 60, 0, Math.PI * 2); c.fill(); }
    else if (name === 'rain') { const r = rng(seedBase + i); c.strokeStyle = 'rgba(200,220,255,0.55)'; c.lineWidth = 3; for (let j = 0; j < 90; j++) { const rx = x + r() * w, ry = y + ((r() * h + t * 1500) % h); c.beginPath(); c.moveTo(rx, ry); c.lineTo(rx - 12, ry + 44); c.stroke(); } }
    else if (name === 'snow') { const r = rng(seedBase + i); c.fillStyle = 'rgba(255,255,255,0.85)'; for (let j = 0; j < 70; j++) { const sx = x + ((r() * w + Math.sin(t + j) * 30) % w), sy = y + ((r() * h + t * 80) % h); c.beginPath(); c.arc(sx, sy, 2 + r() * 4, 0, Math.PI * 2); c.fill(); } }
    else if (name === 'embers') { c.save(); sparks(c, t, { n: 40, seed: seedBase + i, color: a.length ? '255,150,60' : '255,180,90', rise: 70, size: 5 }); c.restore(); }
    else if (name === 'smoke') { const [sx, sy] = P(a[0], a[1]); smoke(c, t, at, sx, sy, { n: 6, size: a[2] || 50, col: '80,74,70' }); }
    else if (name === 'bolt') { const [x0, y0] = P(a[0], a[1]), [x1, y1] = P(a[2], a[3]); bolt(c, t, x0, y0, x1, y1, { a: k * (a[4] !== undefined ? a[4] : 1), seed: seedBase + i, w: a[5] || 10 }); }
    else if (name === 'flash') flash(c, t, at, { color: a.length ? `${a[0]},${a[1]},${a[2]}` : '255,255,255', peak: 0.85, life: 0.4 });
    else if (name === 'darken') { c.fillStyle = `rgba(4,4,14,${(a[0] ?? 0.6) * prog(t, at, 1.0)})`; c.fillRect(x, y, w, h); }
    else if (name === 'glow') { const [gx, gy] = P(a[0], a[1]); glow(c, gx, gy, a[2] || 300, a.length > 5 ? `${a[3]},${a[4]},${a[5]}` : '255,220,140', 0.5 * k); }
    else if (name === 'eyes') {
      const [ex, ey] = P(a[0], a[1]), eo = ease.outCubic(prog(t, at, 0.5)), col = a.length > 3 ? `${a[3]},${a[4]},${a[5]}` : '255,80,50', sp = (a[2] || 0.12) * w;
      [[ex - sp, ey], [ex + sp, ey]].forEach(([px, py]) => { glow(c, px, py, 120, col, 0.85 * eo); c.fillStyle = `rgba(255,235,220,${eo})`; c.beginPath(); c.ellipse(px, py, 48, 18 * eo + 1, 0, 0, Math.PI * 2); c.fill(); });
    }
    else if (name === 'dizzy') { const [dx, dy] = P(a[0], a[1]); for (let j = 0; j < 5; j++) { const an = t * 3 + j * 1.256; withT(c, dx + Math.cos(an) * 120, dy + Math.sin(an) * 32, 1, an, () => { c.fillStyle = '#FFE15A'; c.fill(starPath(24, 10)); c.lineWidth = 4; c.strokeStyle = INK; c.stroke(starPath(24, 10)); }); } }
    else if (name === 'ring') { const [rx, ry] = P(a[0], a[1]); ring(c, t, at, rx, ry, { maxR: a[2] || 500, life: 0.6, color: '255,230,160', width: 14 }); }
    else if (name === 'burst') { const [bx, by] = P(a[0], a[1]); burst(c, t, at, bx, by, { n: 40, color: '255,210,120', speed: 800, life: 0.8, size: 9 }); }
    else if (name === 'crown') { const [cx, cy] = P(a[0], a[1]); crown(c, cx, cy, (a[2] || 1) * ease.outBack(prog(t, at, 0.5))); }
    else if (name === 'sigil' && window.sigil) { const [sx, sy] = P(a[0], a[1]); window.sigil(c, t, sx, sy, (a[2] || 120) * ease.outBack(prog(t, at, 0.6)), k); }
    else if (name === 'hearts') { const r = rng(seedBase + i); for (let j = 0; j < 10; j++) { const q = ((t - at) * 0.5 + j / 10) % 1; c.fillStyle = `rgba(255,120,150,${Math.sin(q * Math.PI)})`; const hx = x + 0.2 * w + r() * 0.6 * w, hy = y + h - q * h; c.beginPath(); c.moveTo(hx, hy + 14); c.bezierCurveTo(hx - 26, hy - 4, hx - 10, hy - 22, hx, hy - 8); c.bezierCurveTo(hx + 10, hy - 22, hx + 26, hy - 4, hx, hy + 14); c.fill(); } }
  }
}

function drawArt(c, t, dur, a, x, y, w, h) {
  const at = T(a.at, dur, 0);
  if (t < at - 0.001 && a.enter !== 'none') return;
  const k = a.enter === 'none' ? 1 : prog(t, at, a.enter === 'fade' ? 0.6 : 0.45);
  let fx = a.x ?? 0.5, fy = a.y ?? 0.6;
  if (a.move) { const mk = ease.inOutCubic(prog(t, T(a.moveAt, dur, at), T(a.moveEnd, dur, dur) - T(a.moveAt, dur, at))); fx = lerp(fx, a.move[0], mk); fy = lerp(fy, a.move[1], mk); }
  let px = x + fx * w, py = y + fy * h, s = 1, alpha = a.alpha ?? 1;
  if (a.enter === 'pop' || !a.enter) s = ease.outBack(k);
  else if (a.enter === 'left') px -= (1 - ease.outCubic(k)) * (w * 0.7);
  else if (a.enter === 'right') px += (1 - ease.outCubic(k)) * (w * 0.7);
  else if (a.enter === 'up') py += (1 - ease.outCubic(k)) * (h * 0.6);
  else if (a.enter === 'down') py -= (1 - ease.outCubic(k)) * (h * 0.6);
  else if (a.enter === 'fade') alpha *= ease.outCubic(k);
  if (a.exit) alpha *= 1 - prog(t, T(a.exit, dur, dur), 0.4);
  if (alpha <= 0 || s <= 0) return;
  const bob = a.bob ? Math.sin(t * 2 + px) * a.bob : 0;
  art(c, a.name, px, py + bob, (a.h ?? 0.85) * h * s, { shadow: false, flip: !!a.flip, rot: (a.rot || 0) * (a.spinIn ? ease.outCubic(k) : 1), alpha });
}

function drawPanel(c, t, dur, p, rect, idx) {
  const [x, y, w, h] = p.rect || rect;
  panel(c, t, T(p.at, dur, 0), x, y, w, h, (cc, X, Y, Wd, Ht) => {
    drawBg(cc, t, p.bg, X, Y, Wd, Ht);
    drawFx(cc, t, dur, p.under, X, Y, Wd, Ht, 100 + idx * 10);
    for (const a of p.art || []) drawArt(cc, t, dur, a, X, Y, Wd, Ht);
    drawFx(cc, t, dur, p.fx, X, Y, Wd, Ht, 200 + idx * 10);
    for (const s of p.sfx || []) sfxWord(cc, t, T(s.at, dur, 0), s.text, X + (s.x ?? 0.5) * Wd, Y + (s.y ?? 0.3) * Ht, s.size || (WIDE ? 90 : 100), s.rot ?? -0.1, SFX_STYLES[s.style] || SFX_STYLES.fire);
    // A bubble gives way when a later bubble opens in the same spot of the same panel.
    const L = window.LINES || [], bubs = (p.bubbles || []).map(b => {
      const line = b.line !== undefined ? L[b.line] : null;
      return { b, line, at: T(b.at, dur, line ? line[2] - 0.12 : 0) };
    });
    for (const { b, line, at } of bubs) {
      const text = b.text || (line ? line[1] : '');
      const next = bubs.filter(o => o.at > at + 0.05 && Math.abs((o.b.x ?? 0.5) - (b.x ?? 0.5)) < 0.2 && Math.abs((o.b.y ?? 0.2) - (b.y ?? 0.2)) < 0.2);
      const until = b.until !== undefined ? T(b.until, dur, dur) : (next.length ? Math.min(...next.map(o => o.at)) : Infinity);
      if (t > until) continue;
      const bx = X + (b.x ?? 0.5) * Wd, by = Y + (b.y ?? 0.2) * Ht, tail = b.tail || [b.x ?? 0.5, (b.y ?? 0.2) + 0.22];
      bubble(cc, t, at, bx, by, text, X + tail[0] * Wd, Y + tail[1] * Ht, { size: b.size || (WIDE ? 34 : 44), mw: b.w || (WIDE ? 440 : 460), shout: !!b.shout });
    }
    for (const cp of p.caps || []) capBox(cc, t, T(cp.at, dur, 0), X + (cp.x ?? 0.025) * Wd, Y + (cp.y ?? 0.03) * Ht, cp.text, { size: cp.size || (WIDE ? 30 : 36), bg: cp.bg || '#FFE15A' });
  }, { bg: '#FFFFFF', from: p.enter || (T(p.at, dur, 0) <= 0.01 ? 'none' : 'scale') });
}

function drawPage(c, t, dur, pg) {
  paper(c, t);
  const rects = layoutRects(pg.layout || '1');
  const shakes = (pg.shake || []).map(s => T(s, dur, 0));
  let sx = 0, sy = 0;
  for (const s0 of shakes) { const [dx, dy] = shakeAt(t, s0, 18, 5); sx += dx; sy += dy; }
  c.save(); c.translate(sx, sy);
  (pg.panels || []).forEach((p, i) => drawPanel(c, t, dur, p, rects[i] || rects[rects.length - 1], i));
  c.restore();
  for (const tt of pg.titles || []) {
    const at = T(tt.at, dur, 0);
    if (t < at) continue;
    withT(c, (tt.x ?? 0.5) * W, (tt.y ?? 0.45) * H, ease.outBack(prog(t, at, 0.5)), tt.rot ?? -0.04, () => title(c, tt.text, 0, 0, tt.size || 80, { fill: SFX_STYLES[tt.style] || SFX_STYLES.gold, lw: (tt.size || 80) * 0.18 }));
  }
  for (const cp of pg.caps || []) capBox(c, t, T(cp.at, dur, 0), (cp.x ?? 0.03) * W, (cp.y ?? 0.035) * H, cp.text, { size: cp.size || (WIDE ? 34 : 40), bg: cp.bg || '#FFE15A' });
  if (WIDE) { c.save(); c.font = `18px ${FONT}`; c.textAlign = 'right'; c.fillStyle = 'rgba(40,30,20,0.55)'; c.fillText('Fan comic · Art: Supercell Fan Kit · Not endorsed by Supercell', W - 40, H - 14); c.restore(); }
  else comicCredit(c);
}

function comicEpisode(scriptUrl, fankitUrl) {
  const spec = loadJSONSync(scriptUrl), kit = loadJSONSync(fankitUrl);
  window.ART = Object.fromEntries(Object.keys(kit.assets).map(n => [n, `fankit/${n}.png`]));
  window.scenes = spec.scenes.map(sc => (ctx, t, dur) => drawPage(ctx, t, dur, sc.page || {}));
}
