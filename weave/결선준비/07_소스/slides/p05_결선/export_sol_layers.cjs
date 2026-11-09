// Export multi-layer transparent PNGs for Solution: Weave Assist animations
const path = require('node:path');
const fs = require('node:fs');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.PW_CORE || '/home/jaeung/.cache/weave-tools/node/node_modules/playwright-core');

const CHROME = process.env.CHROME || '/home/jaeung/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const HTML = path.resolve(__dirname, 'page-05-solution.html');
const TMP_DIR = process.env.TMP_DIR || '/tmp/sol_layers_raw';
fs.mkdirSync(TMP_DIR, { recursive: true });

const PARTS = [
  'sol1_base', 'sol1_swipe', 'sol1_sheet', 'sol1_q', 'sol1_recs', 'sol1_res',
  'sol2_base', 'sol2_type', 'sol2_tap', 'sol2_card', 'sol2_ok',
  'sol3_base', 'sol3_ctx', 'sol3_glow', 'sol3_card', 'sol3_ok'
];

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME,
    headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--force-color-profile=srgb', '--font-render-hinting=none']
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 2 });
    await page.goto(pathToFileURL(HTML).href);
    await page.waitForFunction(() => window.pageReady === true, null, { timeout: 15000 });
    await page.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all([...document.images].map(i => i.decode().catch(() => null)));
    });

    const summary = await page.evaluate(() => {
      const slide = document.getElementById('slide');
      const S = slide.getBoundingClientRect();
      const box = (el) => {
        const r = el.getBoundingClientRect();
        return {
          l: r.left - S.left, t: r.top - S.top, r: r.right - S.left, b: r.bottom - S.top,
          w: r.width, h: r.height, cx: r.left - S.left + r.width / 2, cy: r.top - S.top + r.height / 2
        };
      };

      // Add caller avatar & label on phone1 screen for sol1_base (covered by #sheet once sol1_sheet rises)
      const caller = document.createElement('div');
      caller.dataset.part = 'sol1_base';
      caller.style.cssText = 'position:absolute;left:394px;top:316px;width:120px;height:130px;z-index:4;display:flex;flex-direction:column;align-items:center;pointer-events:none;';
      caller.innerHTML = `
        <div style="width:64px;height:64px;border-radius:50%;background:linear-gradient(145deg,#E3DCFA,#CBC0F5);display:flex;align-items:center;justify-content:center;box-shadow:0 6px 16px rgba(80,60,140,.12);">
          <svg viewBox="0 0 24 24" width="34" height="34" fill="#6B4EFF"><path d="M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2.5c-3.3 0-10 1.7-10 5V22h20v-2.5c0-3.3-6.7-5-10-5z"/></svg>
        </div>
        <div style="margin-top:10px;font:700 15px/20px 'Noto Sans KR',sans-serif;color:#2B2640;">민수님</div>
        <div style="margin-top:2px;font:500 11px/15px 'Noto Sans KR',sans-serif;color:#6B4EFF;">통화 중</div>
      `;
      slide.appendChild(caller);

      // Add normal white spool circle + purple spool icon on kb3 for sol3_base (covered by sol3_glow)
      const kb3Spool = document.createElement('div');
      kb3Spool.dataset.part = 'sol3_base';
      kb3Spool.style.cssText = 'position:absolute;left:650.5px;top:532.5px;width:29px;height:29px;border-radius:50%;background:#fff;border:1px solid #D8CEFA;z-index:26;display:flex;align-items:center;justify-content:center;box-sizing:border-box;';
      kb3Spool.innerHTML = `<img src="../assets/weave-spool-6B4EFF.png" style="width:18px;height:18px;display:block;">`;
      slide.appendChild(kb3Spool);

      // Classify direct children of #slide
      const hands = [...slide.querySelectorAll('img.handimg')];
      const handParts = ['sol1_swipe', 'sol2_type', 'sol2_type', 'sol2_tap', 'sol3_glow', 'sol2_ok', 'sol3_ok'];
      hands.forEach((h, i) => { h.dataset.part = handParts[i]; });

      for (const el of slide.children) {
        if (el.dataset.part) continue;
        if (el.classList.contains('bg') || el.classList.contains('chip-prev') || el.classList.contains('rule')) {
          el.dataset.part = 'skip';
          continue;
        }
        if (el.tagName.toLowerCase() === 'svg' && el.classList.contains('fx')) continue;
        if (el.hasAttribute('data-x')) {
          el.dataset.part = 'text';
          continue;
        }
        const b = box(el);
        const id = el.id || '';
        if (b.cx < 611) {
          if (b.cy < 200 || id === 'phone1' || el.classList.contains('scr') || id === 'redbtn') el.dataset.part = 'sol1_base';
          else if (b.cx < 310) el.dataset.part = 'sol1_recs';
          else if (id === 'sheet' || id === 'sbar1' || (b.t >= 270 && b.b <= 305 && b.cx < 400)) el.dataset.part = 'sol1_sheet';
          else el.dataset.part = 'sol1_res';
        } else if (b.cy < 398) {
          if (el.classList.contains('cursor')) el.dataset.part = 'sol2_type';
          else if (b.cx < 900) el.dataset.part = 'sol2_base';
          else el.dataset.part = 'sol2_card';
        } else {
          if (id === 'ctx3' || id === 'ctx4' || id === 'ctx4i' || (b.t >= 488 && b.b <= 522 && b.cx < 900)) el.dataset.part = 'sol3_ctx';
          else if (el.tagName === 'IMG' && b.cx < 700 && b.cy > 530 && b.cy < 565) el.dataset.part = 'sol3_glow';
          else if (b.cx < 900) el.dataset.part = 'sol3_base';
          else el.dataset.part = 'sol3_card';
        }
      }

      // Classify children of svg.fx.back
      const svgBack = slide.querySelector('svg.fx.back');
      for (const el of svgBack.children) {
        if (el.tagName.toLowerCase() === 'defs') continue;
        const b = box(el);
        if (b.cx < 611) {
          if (b.r > 310) el.dataset.part = 'sol1_res';
          else el.dataset.part = 'sol1_recs';
        } else if (b.cy < 398) {
          if (b.l > 875) el.dataset.part = 'sol2_tap';
          else el.dataset.part = 'sol2_base';
        } else {
          if (b.l > 875) el.dataset.part = 'sol3_glow';
          else el.dataset.part = 'sol3_base';
        }
      }

      // Classify children of svg.fx.front
      const svgFront = slide.querySelector('svg.fx.front');
      for (const el of svgFront.children) {
        if (el.tagName.toLowerCase() === 'defs') continue;
        const b = box(el);
        if (b.cx < 611) {
          if (b.t < 258) el.dataset.part = 'sol1_base';
          else if (b.t >= 258 && b.b <= 272) el.dataset.part = 'sol1_sheet';
          else if (b.t >= 272 && b.b <= 302) el.dataset.part = 'sol1_q';
          else if (b.t >= 400 && b.b <= 525) el.dataset.part = 'sol1_res';
          else if (b.cx > 485 && b.t >= 530 && b.b <= 615) el.dataset.part = 'sol1_swipe';
          else el.dataset.part = 'sol1_base';
        } else if (b.cy < 398) {
          if (el.tagName.toLowerCase() === 'circle' && Math.abs(b.cx - 665) < 5) el.dataset.part = 'sol2_base';
          else if (b.cx < 700 && b.cy < 290) el.dataset.part = 'sol2_tap';
          else if (b.cx < 900 && b.cy >= 290) el.dataset.part = 'sol2_type';
          else el.dataset.part = 'sol2_ok';
        } else {
          if (b.cx < 720) el.dataset.part = 'sol3_glow';
          else el.dataset.part = 'sol3_ok';
        }
      }

      const counts = {};
      for (const el of slide.querySelectorAll('[data-part]')) {
        const p = el.dataset.part;
        counts[p] = (counts[p] || 0) + 1;
      }
      return counts;
    });

    console.log('Part element counts:', JSON.stringify(summary));

    await page.evaluate(() => {
      document.body.classList.add('art-only');
      document.documentElement.style.background = 'transparent';
      document.body.style.background = 'transparent';
    });

    const slide = await page.$('#slide');
    for (const part of PARTS) {
      await page.evaluate((p) => {
        for (const el of document.querySelectorAll('#slide [data-part]')) {
          el.style.visibility = (el.dataset.part === p) ? 'visible' : 'hidden';
        }
      }, part);
      await slide.screenshot({ path: path.join(TMP_DIR, `${part}.png`), omitBackground: true });
    }
  } finally {
    await browser.close();
  }
})();
