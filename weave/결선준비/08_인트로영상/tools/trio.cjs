// 끝 장면의 세 화면을 영상과 같은 화면에서 찍어 스프라이트로 만든다 → 소스/assets/img/trio/trio-1~3.png
// 옛 데모 GIF처럼 세 화면이 각자 움직이게, 장면마다 몇 구간을 빠르게 이어 붙인다.
// 사용: node tools/trio.cjs  (소스를 고친 뒤 영상 렌더 전에 한 번). 스프라이트는 다시 만들 수 있어서 저장소에 올리지 않는다
const path = require('path'), fs = require('fs'), { execFileSync } = require('child_process'), { pathToFileURL } = require('url');
const HOME = process.env.HOME;
const { chromium } = require(path.join(HOME, '.cache/weave-tools/node/node_modules/playwright-core'));
const CHROME = path.join(HOME, '.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell');
const FFMPEG = path.join(HOME, '.cache/weave-tools/bin/ffmpeg');
const ROOT = path.resolve(__dirname, '..');
const DEST = path.join(ROOT, '소스', 'assets', 'img', 'trio');
const TMP = path.join(ROOT, 'out', '_trio');
const URL_ = pathToFileURL(path.join(ROOT, '소스', 'index.html')).href;
const ARGS = ['--no-sandbox', '--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text'];
const pngSize = f => { const b = fs.readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };

(async () => {
  const b = await chromium.launch({ executablePath: CHROME, args: ARGS });
  // 값과 휴대폰 크기를 먼저 읽는다
  const p0 = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await p0.goto(URL_); await p0.evaluate(() => window.__ready);
  const m = await p0.evaluate(() => window.__marks), G = await p0.evaluate(() => window.__gif);
  await p0.close();
  const FW = 452, scale = G.w / FW;                    // 스프라이트 칸 크기로 바로 찍어 글자를 선명하게
  // 구간: [시작, 끝, 칸 수]. 칸 수의 합이 G.n
  const CLIPS = [
    { dim: true, segs: [[m.dragT, m.tGo + 0.55, 25], [m.tSum + 0.9, m.tSum + 4.85, 27]] },                       // 시트 올림 → 입력 → 검색 → 기억 → 요약
    { dim: false, segs: [[m.p0 + 1.3, m.p0 + 2.7, 14], [m.t2 + 0.75, m.t2 + 1.6, 11], [m.pTap3 - 0.25, m.pTap3 + 1.6, 27]] },   // 입력 → 답으로 바뀜 → 검색 결과
    { dim: false, segs: [[m.tM2 - 1.2, m.tM3 + 0.5, 19], [m.tapW - 0.1, m.tapW + 1.0, 8], [m.tapI + 0.1, m.reply + 0.55, 25]] },  // 대화 → 추천 → 보내기 → 답장
  ];
  const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: scale });
  const p = await ctx.newPage();
  p.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await p.goto(URL_); await p.evaluate(() => window.__ready);
  await p.addStyleTag({ content: 'html, body { background: transparent !important; } body * { visibility: hidden; } #phone, #phone * { visibility: visible; } .frame { box-shadow: none !important; }' });
  fs.rmSync(TMP, { recursive: true, force: true }); fs.mkdirSync(DEST, { recursive: true });
  for (const [i, c] of CLIPS.entries()) {
    const dir = path.join(TMP, String(i + 1)); fs.mkdirSync(dir, { recursive: true });
    const n = c.segs.reduce((a, s) => a + s[2], 0);
    if (n !== G.n) throw new Error(`clip ${i + 1}: ${n} frames, expected ${G.n}`);
    let k = 0;
    for (const [t0, t1, cnt] of c.segs) for (let j = 0; j < cnt; j++, k++) {
      const t = t0 + (t1 - t0) * j / Math.max(1, cnt - 1);
      const r = await p.evaluate(({ t, dim }) => {
        window.__seek(t);
        gsap.set('#phone', { x: 0, y: 0, scale: 1, rotation: 0, filter: 'none', autoAlpha: 1 });
        if (dim) gsap.set(['#wB .wpill', '#ttlB', '#b1', '#b2', '#b3', '#b4'], { opacity: 1 });   // 요약 확대 때 옅어진 줄을 그대로 밝게(그 구간만)
        const q = document.querySelector('#phone .frame').getBoundingClientRect();
        return { x: q.x, y: q.y };
      }, { t, dim: c.dim && t >= m.tSum });
      const f = path.join(dir, `f${String(k).padStart(3, '0')}.png`);
      await p.screenshot({ path: f, clip: { x: r.x, y: r.y, width: FW, height: G.h / scale }, omitBackground: true });
      if (k === 0) { const [w, h] = pngSize(f); if (w !== G.w || h !== G.h) throw new Error(`frame ${w}x${h}, expected ${G.w}x${G.h}`); }
    }
    const out = path.join(DEST, `trio-${i + 1}.png`);
    execFileSync(FFMPEG, ['-hide_banner', '-loglevel', 'error', '-y', '-framerate', String(G.fps), '-i', path.join(dir, 'f%03d.png'), '-vf', `tile=${G.cols}x${Math.ceil(G.n / G.cols)}`, '-frames:v', '1', '-pix_fmt', 'rgba', out]);
    console.log('trio', i + 1, out.replace(ROOT + path.sep, ''), `${(fs.statSync(out).size / 1048576).toFixed(1)} MB`);
  }
  fs.rmSync(TMP, { recursive: true, force: true });
  await b.close();
})();
