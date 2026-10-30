// 글자(data-x)가 자신을 담은 상자(data-s 또는 .card/.pill/.mini/.chip/.tag) 밖으로 넘치는지 검사
// 사용: node tools/check_fit.cjs pages/page-07-pipeline.html
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.PW_CORE || '/tmp/claude-weave-0927/node_modules/playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: '/home/jaeung/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  await p.goto(pathToFileURL(path.resolve(process.argv[2])).href);
  await p.waitForFunction(() => window.pageReady === true, null, { timeout: 15000 });
  await p.evaluate(() => document.fonts.ready);
  const res = await p.evaluate(() => {
    const S = document.getElementById('slide').getBoundingClientRect();
    const boxes = [...document.querySelectorAll('[data-s]')].map((e) => ({ e, r: e.getBoundingClientRect() }))
      .filter(({ r }) => r.width < 700 && r.height < 400);
    const out = [];
    for (const t of document.querySelectorAll('[data-x]')) {
      const rg = document.createRange(); rg.selectNodeContents(t); const ir = rg.getBoundingClientRect();
      if (!ir.width) continue;
      const cx = ir.left + 2, cy = ir.top + ir.height / 2;
      const inside = boxes.filter(({ r }) => cx >= r.left && cx <= r.right && cy >= r.top && cy <= r.bottom)
        .sort((a, b) => a.r.width * a.r.height - b.r.width * b.r.height);
      if (!inside.length) continue;
      const c = inside[0].r;
      const over = Math.max(ir.right - (c.right - 2), (c.left + 2) - ir.left, ir.bottom - (c.bottom - 1), (c.top + 1) - ir.top);
      if (over > 0) out.push({ text: t.textContent.trim().slice(0, 30), over: +over.toFixed(1), box: [c.left - S.left, c.top - S.top, c.width, c.height].map((v) => +v.toFixed(1)) });
    }
    return out;
  });
  console.log(JSON.stringify(res, null, 1));
  await b.close();
})();
