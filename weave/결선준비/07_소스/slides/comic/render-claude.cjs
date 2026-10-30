// 2쪽 만화(overview-comic v7.2 사본)에 터치 효과를 얹어 다시 렌더링합니다. 원본 render.cjs와 같은 방식(3배 렌더 → 3600×2560 lanczos 축소).
// 사용: NODE_PATH=/tmp/claude-weave-0927/node_modules LD_LIBRARY_PATH=... node render-claude.cjs [measure]
const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const sharp = require('sharp');
const { chromium } = require('playwright-core');

(async () => {
  const W = 1800, H = 1280;
  const browser = await chromium.launch({
    executablePath: process.env.COMIC_CHROMIUM || '/home/jaeung/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',
    headless: true, args: ['--no-sandbox', '--disable-gpu', '--force-color-profile=srgb'],
  });
  try {
    const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 3 });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(pathToFileURL(path.join(__dirname, 'index.html')).href + '?export');
    await page.evaluate(async () => {
      await document.fonts.ready;
      await window.comicReady;
      await Promise.all([...document.images].map(im => im.decode()));
    });
    const boxes = await page.evaluate(() => {
      const r = s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [b.x, b.y, b.width, b.height].map(v => +v.toFixed(1)); };
      return { p3: r('.p3'), p4: r('.p4'), arrow4: r('.p4 .submit-arrow'), tapHand: r('.p4 .tap-hand'), swipeHand: r('.p3 .swipe-hand'), trail: r('.p3 .drag-trail'),
               touch4: r('.p4 .touch-spark'), touch3: r('.p3 .touch-spark'), missing: [...document.images].filter(i => !i.naturalWidth).map(i => i.src) };
    });
    console.log(JSON.stringify({ boxes, errors }, null, 1));
    if (process.argv[2] === 'measure') return;
    if (errors.length || boxes.missing.length) throw new Error('render errors');
    const out = path.join(__dirname, 'out');
    await fs.mkdir(out, { recursive: true });
    const master = await page.locator('#comic').screenshot();
    await sharp(master).resize(W * 2, H * 2, { kernel: 'lanczos3' }).png().withMetadata({ density: 300 }).toFile(path.join(out, 'overview-comic.png'));
    await sharp(master).resize(W, H, { kernel: 'lanczos3' }).png().toFile(path.join(out, 'overview-comic-preview.png'));
    // 확인용 확대: 3·4컷 손 주변
    for (const [name, x, y, w, h] of [['zoom-p4-tap', 470, 780, 150, 130], ['zoom-p3-swipe', 1600, 400, 190, 200], ['panel4', 12, 646, 584, 622], ['panel3', 1204, 12, 584, 622]]) {
      await sharp(master).extract({ left: x * 3, top: y * 3, width: w * 3, height: h * 3 }).png().toFile(path.join(out, `${name}.png`));
    }
    console.log('saved', out);
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
