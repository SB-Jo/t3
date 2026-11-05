// 끝 장면의 세 화면을 영상과 같은 화면에서 찍는다: 휴대폰만 남기고 투명 배경으로 → 소스/assets/img/trio-1~3.png
// 사용: node tools/trio.cjs  (소스를 고친 뒤 영상 렌더 전에 한 번)
const path = require('path'), { pathToFileURL } = require('url');
const HOME = process.env.HOME;
const { chromium } = require(path.join(HOME, '.cache/weave-tools/node/node_modules/playwright-core'));
const CHROME = path.join(HOME, '.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell');
const ROOT = path.resolve(__dirname, '..');
(async () => {
  const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox', '--force-color-profile=srgb', '--font-render-hinting=none'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await p.goto(pathToFileURL(path.join(ROOT, '소스', 'index.html')).href);
  await p.evaluate(() => window.__ready);
  const m = await p.evaluate(() => window.__marks);
  const shots = [[m.tSend + 0.6, 1], [m.x1 - 0.3, 2], [m.reply + 1.5, 3]];
  await p.addStyleTag({ content: 'html, body { background: transparent !important; } body * { visibility: hidden; } #phone, #phone * { visibility: visible; } .frame { box-shadow: none !important; }' });
  for (const [t, n] of shots) {
    await p.evaluate(t => { window.__seek(t); gsap.set('#phone', { x: 0, y: 0, scale: 1, rotation: 0, filter: 'none', autoAlpha: 1 }); }, t);
    const r = await p.evaluate(() => { const q = document.querySelector('#phone .frame').getBoundingClientRect(); return { x: q.x, y: q.y, width: q.width, height: q.height }; });
    await p.screenshot({ path: path.join(ROOT, '소스', 'assets', 'img', `trio-${n}.png`), clip: r, omitBackground: true });
    console.log('trio', n, 't', t.toFixed(2), JSON.stringify(r));
  }
  await b.close();
})();
