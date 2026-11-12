// HTML 안의 요소를 하나씩 PNG로 찍는다(투명 바탕). 6쪽의 앱 화면, 카메라 아이콘을 만드는 데 씀.
// 사용: node tools/shot.cjs <html> <나올 폴더> [--scale 1] [--sel .shot]
//   찍는 요소: --sel에 맞는 요소마다 data-name → <나올 폴더>/<data-name>.png
// 환경: ~/.cache/weave-tools/node (playwright-core), ~/.cache/ms-playwright/chromium_headless_shell-1243 (08_인트로영상/tools/render.cjs와 같음)
const path = require('path'), fs = require('fs'), { pathToFileURL } = require('url');
const HOME = process.env.HOME;
const { chromium } = require(path.join(HOME, '.cache/weave-tools/node/node_modules/playwright-core'));
const CHROME = process.env.CHROME || path.join(HOME, '.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell');
const arg = (k, d) => { const i = process.argv.indexOf(k); return i < 0 ? d : process.argv[i + 1]; };

(async () => {
  const html = path.resolve(process.argv[2]), out = path.resolve(process.argv[3]);
  const scale = Number(arg('--scale', 1)), sel = arg('--sel', '.shot');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox', '--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text'] });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: scale });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
  await page.goto(pathToFileURL(html).href);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForLoadState('networkidle');
  const els = await page.locator(sel).all();
  for (const el of els) {
    const name = await el.getAttribute('data-name');
    await el.screenshot({ path: path.join(out, name + '.png'), omitBackground: true });
  }
  console.log(els.length, '→', out);
  await browser.close();
})();
