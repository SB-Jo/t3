// 세 장을 벡터 PDF로 내보냅니다 (글자 선택 가능). 사용: node tools/export_pdf.cjs
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.PW_CORE || '/tmp/claude-weave-0927/node_modules/playwright-core');
const CHROME = process.env.CHROME || '/home/jaeung/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
const ROOT = path.resolve(__dirname, '..');
const PAGES_DIR = process.env.PAGES_DIR ? path.resolve(process.env.PAGES_DIR) : path.join(ROOT, 'pages');
const OUT_DIR = process.env.OUT_DIR ? path.resolve(process.env.OUT_DIR) : path.join(ROOT, 'out');
const pages = ['page-07-pipeline', 'page-15-qna', 'page-16-glossary'];
(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--no-sandbox', '--disable-gpu', '--force-color-profile=srgb'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  for (const name of pages) {
    await page.goto(pathToFileURL(path.join(PAGES_DIR, `${name}.html`)).href);
    await page.waitForFunction(() => window.pageReady === true);
    await page.evaluate(async () => { await document.fonts.ready; });
    await page.addStyleTag({ content: '@page { size: 1280px 720px; margin: 0 } html, body { background: #fff !important; width: 1280px; height: 720px; overflow: hidden; }' });
    await page.pdf({ path: path.join(OUT_DIR, `${name}.pdf`), width: '1280px', height: '720px', printBackground: true, pageRanges: '1' });
  }
  await browser.close();
  console.log('ok');
})().catch(e => { console.error(e); process.exit(1); });
