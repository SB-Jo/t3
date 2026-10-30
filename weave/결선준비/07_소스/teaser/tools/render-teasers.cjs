// 티저 제목 후보 렌더러 — 원본(0921/added_0926/teaser-refinement-v19/render-floating-rims.cjs)과 같은 합성 방식
//   사진 베이스 + 1× 레이어(UI 빛·테두리·보정 글자·음영·제목·로고) + 4× 작은 글자 레이어(말풍선·입력 버튼)
// 사용: node tools/render-teasers.cjs v0 vA vB ...      (v0 = 원본 설정, teaser-final.png와 비교)
//       node tools/render-teasers.cjs --analysis         (진단용: 제목·음영을 모두 뺀 사진 배경)
//   후보마다 out/teaser-{v}.png, analysis/bg-{v}.png(제목만 뺀 배경), analysis/headline-{v}.png(제목만), analysis/boxes-{v}.json 저장
const path = require('node:path');
const fs = require('node:fs');
const { pathToFileURL } = require('node:url');
const NM = process.env.NM || '/tmp/claude-weave-0927/node_modules';
const sharp = require(path.join(NM, 'sharp'));
const { chromium } = require(path.join(NM, 'playwright-core'));

const ROOT = path.resolve(__dirname, '..');
const ASSETS = path.resolve(ROOT, 'assets');
const SRC = path.join(ROOT, 'src', 'teaser-candidates.html');
const W = 1672, H = 941;

async function open(browser, v, scale) {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: scale });
  await page.goto(pathToFileURL(SRC).href + '?v=' + v);
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode())); });
  return page;
}

async function composite(browser, v, { hide = '' } = {}) {
  const page = await open(browser, v, 1);
  await page.addStyleTag({ content: `.photo,.incoming-copy,.cta-repair${hide ? ',' + hide : ''}{visibility:hidden!important}` });
  const overlay = await page.screenshot({ omitBackground: true });
  await page.close();
  const fine = await open(browser, v, 4);
  await fine.addStyleTag({ content: '.photo,.ui-light,.card-correction,.headline-shade,.corner-scrim,.headline,.galaxy-logo{display:none!important}' });
  const fineOverlay = await sharp(await fine.screenshot({ omitBackground: true })).resize(W, H, { kernel: 'lanczos3' }).png().toBuffer();
  await fine.close();
  // vEsB는 사진 사본(옛 버튼 원을 지운 것, tools/make-btn-variant.py)을 씀
  const base = v === 'vEsB' ? path.join(ROOT, 'src', 'teaser-base-btn.png') : path.join(ASSETS, 'teaser-retouched-base.png');
  return sharp(base).composite([{ input: overlay }, { input: fineOverlay }]).png().toBuffer();
}

async function headlineOnly(browser, v) {
  const page = await open(browser, v, 1);
  await page.addStyleTag({ content: 'body > :not(.headline){visibility:hidden!important} .headline *{visibility:visible!important}' });
  const buf = await page.screenshot({ omitBackground: true });
  const boxes = await page.evaluate(() => {
    const r = sel => { const e = document.querySelector(sel); if (!e) return null; const g = document.createRange(); g.selectNodeContents(e); const b = g.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom].map(Math.round); };
    return { weave: r('.weave-word'), assist: r('.assist-word'), tagline: r('.tagline'), brand: r('.brand') };
  });
  await page.close();
  return { buf, boxes };
}

(async () => {
  const args = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: '/home/jaeung/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', headless: true, args: ['--no-sandbox', '--disable-gpu', '--force-color-profile=srgb'] });
  try {
    if (args.includes('--analysis')) {
      const A = path.join(ROOT, 'analysis');
      // 원본에서 제목과 타원 음영을 모두 뺀 사진 배경 (음영 전후 비교용). 제목 포함 배경·제목 레이어는 아래 후보 루프에서 v0로 만듭니다
      fs.writeFileSync(path.join(A, 'bg-no-shade.png'), await composite(browser, 'v0', { hide: '.headline,.headline-shade' }));
      console.log('analysis: bg-no-shade.png');
    }
    for (const v of args.filter(a => !a.startsWith('--'))) {
      const buf = await composite(browser, v);
      const out = path.join(ROOT, 'out', `teaser-${v}.png`);
      fs.writeFileSync(out, buf);
      if (v === 'v0') {
        const [a, b] = await Promise.all([sharp(buf).ensureAlpha().raw().toBuffer(), sharp(path.join(ROOT, 'assets', 'teaser-final.png')).ensureAlpha().raw().toBuffer()]);
        let diff = 0, maxd = 0;
        for (let i = 0; i < a.length; i += 4) { const d = Math.max(Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]), Math.abs(a[i + 2] - b[i + 2])); if (d) { diff++; maxd = Math.max(maxd, d); } }
        console.log(`v0 vs teaser-final.png: differing pixels ${diff} / ${W * H}, max channel diff ${maxd}`);
      }
      fs.writeFileSync(path.join(ROOT, 'analysis', `bg-${v}.png`), await composite(browser, v, { hide: '.headline' }));
      const h = await headlineOnly(browser, v);
      fs.writeFileSync(path.join(ROOT, 'analysis', `headline-${v}.png`), h.buf);
      fs.writeFileSync(path.join(ROOT, 'analysis', `boxes-${v}.json`), JSON.stringify(h.boxes));
      console.log('rendered', v, h.boxes);
    }
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exit(1); });
