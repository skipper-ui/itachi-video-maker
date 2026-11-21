// Render one canvas scene to an MP4.
// Usage: node motion/render.js <page.html> <sceneIndex> <seconds> <fps> <out.mp4> [words.json] [--stills t1,t2,...]
// words.json holds [[word, start, end], ...] for the scene's narration so animations can sync to speech.
// With --stills, PNG frames at the given times are written next to <out> instead of a video.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');

// Serve the repository over localhost so pages can read their images' pixels (file:// would taint the canvas).
function serve(root) {
  const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg',
                  '.json': 'application/json', '.webp': 'image/webp' };
  const server = http.createServer((req, res) => {
    const rel = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    const file = path.join(root, rel);
    if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(r => server.listen(0, '127.0.0.1', () => r(server)));
}

async function main() {
  const args = process.argv.slice(2);
  const stillsAt = args.indexOf('--stills');
  const stills = stillsAt >= 0 ? args.splice(stillsAt, 2)[1].split(',').map(Number) : null;
  const [page, scene, seconds, fps, out, wordsPath] = args;
  const frames = Math.round(Number(seconds) * Number(fps));
  const words = wordsPath ? require('fs').readFileSync(wordsPath, 'utf8') : '[]';
  const browser = await chromium.launch();
  const tab = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await tab.addInitScript(`window.WORDS = ${words};`);
  const root = path.resolve(__dirname, '..');
  const server = await serve(root);
  const rel = path.relative(root, path.resolve(page)).split(path.sep).join('/');
  const url = `http://127.0.0.1:${server.address().port}/${rel}?scene=${scene}&dur=${seconds}`;
  const errors = [];
  tab.on('pageerror', e => errors.push(e.message));
  await tab.goto(url);
  await tab.waitForFunction(() => window.ready === true || window.loadError, null, { timeout: 60000 })
    .then(async () => { const e = await tab.evaluate(() => window.loadError); if (e) throw new Error(e); })
    .catch(e => { throw new Error(errors.join('\n') || e.message); });
  const canvas = await tab.$('canvas');

  if (stills) {
    for (const t of stills) {
      await tab.evaluate(x => window.seek(x), t);
      await canvas.screenshot({ path: `${out.replace(/\.[^.]+$/, '')}_${t.toFixed(2)}.png` });
    }
    if (errors.length) throw new Error(errors.join('\n'));
    await browser.close();
    server.close();
    return;
  }

  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps),
    '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out],
  { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', code => (code ? rej(new Error(`ffmpeg exited ${code}`)) : res())));

  for (let i = 0; i < frames; i++) {
    await tab.evaluate(t => window.seek(t), i / Number(fps));
    const buf = await canvas.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await done;
  if (errors.length) throw new Error(errors.join('\n'));
  await browser.close();
  server.close();
}

main().catch(err => { console.error(err); process.exit(1); });
