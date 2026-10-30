// 인트로 영상 렌더: 소스/index.html의 GSAP 타임라인을 프레임마다 탐색해 찍고 ffmpeg로 묶는다.
// 사용:
//   node tools/render.cjs --events                       → out/events.json (효과음 시점, music.py 입력)
//   node tools/render.cjs --stills 0.5,3,7.5             → out/stills/t00.50.png …
//   node tools/render.cjs --fps 60 --jobs 8 [--blur] [--audio out/bgm.wav] [--from 0 --to 28] [--out out/weave_intro.mp4]
//     --jobs N : 브라우저 N개가 프레임을 나눠 찍음(out/_frames/*.jpg, 끝나면 지움)
//     --blur   : 두 배 빠르기로 찍어 이웃 프레임을 섞음(움직임 흐림, 셔터 180°)
// 환경: ~/.cache/weave-tools (node/playwright-core, bin/ffmpeg), ~/.cache/ms-playwright/chromium_headless_shell-1243
const path = require('path'), fs = require('fs'), { spawn } = require('child_process'), { pathToFileURL } = require('url');
const HOME = process.env.HOME;
const { chromium } = require(path.join(HOME, '.cache/weave-tools/node/node_modules/playwright-core'));
const CHROME = process.env.CHROME || path.join(HOME, '.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell');
const FFMPEG = path.join(HOME, '.cache/weave-tools/bin/ffmpeg');
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'out');
const FR = path.join(OUT, '_frames');
const arg = (k, d) => { const i = process.argv.indexOf(k); return i < 0 ? d : (process.argv[i + 1] && !process.argv[i + 1].startsWith('--') ? process.argv[i + 1] : true); };
const run = (cmd, args) => new Promise((res, rej) => { const p = spawn(cmd, args, { stdio: 'inherit' }); p.on('close', c => c === 0 ? res() : rej(new Error(`${cmd} ${c}`))); });

async function openPage(debug = false) {
  const browser = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox', '--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
  await page.goto(pathToFileURL(path.join(ROOT, '소스', 'index.html')).href + (debug ? '?debug=1' : ''));
  await page.evaluate(() => window.__ready);
  return { browser, page };
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const fps = Number(arg('--fps', 60)), sub = arg('--blur') ? 2 : 1, rate = fps * sub;

  if (arg('--worker')) {                       // 프레임 i0..i1-1을 jpg로
    const { browser, page } = await openPage();
    const from = Number(arg('--from', 0)), i0 = Number(arg('--i0')), i1 = Number(arg('--i1'));
    for (let i = i0; i < i1; i++) {
      await page.evaluate(t => window.__seek(t), from + i / rate);
      await page.screenshot({ path: path.join(FR, `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 96 });
    }
    await browser.close();
    return;
  }

  const { browser, page } = await openPage(!!arg('--debug'));
  const DUR = await page.evaluate(() => window.__DURATION);
  if (arg('--events')) {
    const ev = await page.evaluate(() => window.__events);
    fs.writeFileSync(path.join(OUT, 'events.json'), JSON.stringify({ duration: DUR, events: ev }, null, 1));
    console.log('events', ev.length, '→ out/events.json');
    console.log('taps', JSON.stringify(await page.evaluate(() => window.__taps)));
  }
  const stills = arg('--stills');
  if (stills) {
    const dir = path.join(OUT, 'stills'); fs.mkdirSync(dir, { recursive: true });
    for (const s of String(stills).split(',').map(Number)) {
      await page.evaluate(t => window.__seek(t), s);
      await page.screenshot({ path: path.join(dir, `t${s.toFixed(2).padStart(5, '0')}.png`) });
    }
    console.log('stills', String(stills));
  }
  await browser.close();

  if (arg('--fps')) {
    const from = Number(arg('--from', 0)), to = Number(arg('--to', DUR)), jobs = Number(arg('--jobs', 6));
    const n = Math.round((to - from) * rate);
    fs.rmSync(FR, { recursive: true, force: true }); fs.mkdirSync(FR, { recursive: true });
    const t0 = Date.now();
    const per = Math.ceil(n / jobs), ws = [];
    for (let k = 0; k < jobs; k++) {
      const i0 = k * per, i1 = Math.min(n, i0 + per);
      if (i0 >= i1) break;
      ws.push(run(process.execPath, [__filename, '--worker', '--fps', String(fps), ...(sub > 1 ? ['--blur'] : []), '--from', String(from), '--i0', String(i0), '--i1', String(i1)]));
    }
    const tick = setInterval(() => process.stdout.write(`\rframes ${fs.readdirSync(FR).length}/${n}  ${((Date.now() - t0) / 1000).toFixed(0)}s`), 2000);
    await Promise.all(ws); clearInterval(tick);
    console.log(`\ncaptured ${n} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    const out = path.resolve(ROOT, String(arg('--out', path.join('out', 'weave_intro.mp4'))));
    const audio = arg('--audio');
    const ff = ['-hide_banner', '-loglevel', 'error', '-y', '-framerate', String(rate), '-i', path.join(FR, 'f%05d.jpg')];
    if (audio) ff.push('-ss', String(from), '-i', path.resolve(ROOT, String(audio)));
    const vf = [];
    if (sub > 1) vf.push('tmix=frames=2:weights=1 1', `fps=${fps}`);
    vf.push('scale=in_range=full:out_range=tv', 'format=yuv420p');
    ff.push('-vf', vf.join(','), '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-profile:v', 'high', '-tune', 'animation',
      '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv', '-movflags', '+faststart');
    if (audio) ff.push('-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '256k', '-t', String(to - from));
    ff.push(out);
    await run(FFMPEG, ff);
    if (!arg('--keep')) fs.rmSync(FR, { recursive: true, force: true });
    console.log(`→ ${out}  (${((Date.now() - t0) / 1000).toFixed(0)}s total)`);
  }
})().catch(e => { console.error(e); process.exit(1); });
