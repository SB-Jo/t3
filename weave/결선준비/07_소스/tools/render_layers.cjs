// 이음매 판(seamless)용 그래픽 층 렌더 — 2026-09-28
// PowerPoint는 장표 밖(720px 아래)을 잘라 그리므로, 이어 붙일 때 5쪽 손·6~8쪽 휴대폰 그림자·흐린 장면이 잘려 보임.
// 원래 그래픽 층은 이 HTML을 Chromium으로 찍은 것이라, 같은 방식(art-only, 투명 배경)으로 아래를 EXT만큼 더 찍어 씀.
//   <name>.noscene.png  장면(.scene)을 뺀 그래픽 층, 1280×(720+EXT) — 위 720은 W/K 렌더용
//   <name>.spill.png    장면·인물을 뺀 층 — 아래 EXT만 씀(장표 밖으로 넘친 손·그림자)
//   <name>.scene.png    흐린 장면만 (없으면 만들지 않음)
//   <name>.chars.png    인물(.char)만 — 간격판에서 인물 아랫단만 흐리게 할 때 씀
// 사용: OUT_DIR=<폴더> node tools/render_layers.cjs <page.html> ...
const path = require('node:path');
const fs = require('node:fs');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.PW_CORE || '/tmp/claude-weave-0927/node_modules/playwright-core');
const CHROME = process.env.CHROME || '/home/jaeung/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
const EXT = 100;
const OUT = path.resolve(process.env.OUT_DIR || '.');
fs.mkdirSync(OUT, { recursive: true });

async function run(browser, file) {
  const name = path.basename(file, '.html');
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 + EXT }, deviceScaleFactor: 2 });
  await page.goto(pathToFileURL(path.resolve(file)).href);
  await page.waitForFunction(() => window.pageReady === true, null, { timeout: 15000 });
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode().catch(() => null))); });
  await page.evaluate(() => { document.body.classList.add('art-only'); document.documentElement.style.background = 'transparent'; document.body.style.background = 'transparent'; });
  await page.addStyleTag({ content: 'html, body { overflow: visible !important; } #slide { overflow: visible !important; }' });
  const S = await page.evaluate(() => { const r = document.getElementById('slide').getBoundingClientRect(); return { x: r.left, y: r.top }; });
  const clip = { x: S.x, y: S.y, width: 1280, height: 720 + EXT };
  const shot = async (css, file) => {
    const h = await page.addStyleTag({ content: css });
    await page.screenshot({ path: path.join(OUT, file), clip, omitBackground: true });
    await h.evaluate(n => n.remove());
  };
  const hasScene = await page.evaluate(() => !!document.querySelector('#slide > .scene'));
  await shot('#slide > .scene { visibility: hidden !important; }', `${name}.noscene.png`);
  // 장표 아래로 넘친 부분(손·그림자)만 쓰는 층: 인물은 장표 끝에서 잘리게 그린 그림이라 아래로 이어지면 안 됨
  await shot('#slide > .scene, #slide > .char { visibility: hidden !important; }', `${name}.spill.png`);
  if (hasScene) await shot('#slide > *:not(.scene) { visibility: hidden !important; } #slide > .scene { visibility: visible !important; }', `${name}.scene.png`);
  await shot('#slide > *:not(.char) { visibility: hidden !important; } #slide > .char, #slide > .char * { visibility: visible !important; }', `${name}.chars.png`);
  console.log(name, hasScene ? 'noscene + scene + chars' : 'noscene + chars');
  await page.close();
}

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--no-sandbox', '--disable-gpu', '--force-color-profile=srgb', '--font-render-hinting=none'] });
  try { for (const f of process.argv.slice(2)) await run(browser, f); } finally { await browser.close(); }
})().catch((e) => { console.error(e); process.exit(1); });
