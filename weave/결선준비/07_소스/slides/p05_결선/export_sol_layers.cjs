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
  'sol1_base', 'sol1_call', 'sol1_swipe', 'sol1_sheet', 'sol1_q', 'sol1_recs', 'sol1_res',
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

      // Authentic Galaxy call screen UI (#scrB from 08_인트로영상/소스/index.html: '재웅 선배', '휴대전화 010-1234-5678', 6 call action buttons)
      const callScreen = document.createElement('div');
      callScreen.dataset.part = 'sol1_call';
      callScreen.style.cssText = 'position:absolute;left:338px;top:276px;width:232px;height:252px;z-index:4;display:flex;flex-direction:column;align-items:center;pointer-events:none;font-family:"Noto Sans KR",sans-serif;';
      callScreen.innerHTML = `
        <div style="margin-top:8px;font-size:21px;line-height:26px;font-weight:700;color:#1C1A24;letter-spacing:-0.03em;">재웅 선배</div>
        <div style="margin-top:4px;font-size:10px;line-height:14px;font-weight:500;color:#6E6A7C;">휴대전화 010-1234-5678</div>
        <div style="margin-top:34px;width:208px;display:grid;grid-template-columns:repeat(3,1fr);row-gap:16px;column-gap:8px;">
          <div style="display:flex;flex-direction:column;align-items:center;gap:5px;font-size:9px;color:#4A4658;font-weight:500;">
            <i style="width:40px;height:40px;border-radius:50%;background:#fff;box-shadow:0 3px 8px rgba(52,30,130,.08);display:flex;align-items:center;justify-content:center;">
              <svg viewBox="0 0 24 24" width="17" height="17" style="color:#3A3650"><rect x="2.5" y="7" width="19" height="10" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="8" cy="12" r="2.2" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="16" cy="12" r="2.2" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>
            </i>녹음
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;gap:5px;font-size:9px;color:#4A4658;font-weight:500;">
            <i style="width:40px;height:40px;border-radius:50%;background:#fff;box-shadow:0 3px 8px rgba(52,30,130,.08);display:flex;align-items:center;justify-content:center;">
              <svg viewBox="0 0 24 24" width="17" height="17" style="color:#3A3650"><rect x="9" y="3" width="6" height="11" rx="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M4 4l16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
            </i>내 소리 차단
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;gap:5px;font-size:9px;color:#4A4658;font-weight:500;">
            <i style="width:40px;height:40px;border-radius:50%;background:#fff;box-shadow:0 3px 8px rgba(52,30,130,.08);display:flex;align-items:center;justify-content:center;">
              <svg viewBox="0 0 24 24" width="17" height="17" style="color:#3A3650"><path d="m7 7 10 10-5 4V3l5 4L7 17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </i>블루투스
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;gap:5px;font-size:9px;color:#4A4658;font-weight:500;">
            <i style="width:40px;height:40px;border-radius:50%;background:#fff;box-shadow:0 3px 8px rgba(52,30,130,.08);display:flex;align-items:center;justify-content:center;">
              <svg viewBox="0 0 24 24" width="17" height="17" style="color:#3A3650"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.6 7.6 0 0 1 0 11" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
            </i>스피커
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;gap:5px;font-size:9px;color:#4A4658;font-weight:500;">
            <i style="width:40px;height:40px;border-radius:50%;background:#fff;box-shadow:0 3px 8px rgba(52,30,130,.08);display:flex;align-items:center;justify-content:center;">
              <svg viewBox="0 0 24 24" width="17" height="17" style="color:#3A3650"><g fill="currentColor"><circle cx="6" cy="5" r="1.7"/><circle cx="12" cy="5" r="1.7"/><circle cx="18" cy="5" r="1.7"/><circle cx="6" cy="11" r="1.7"/><circle cx="12" cy="11" r="1.7"/><circle cx="18" cy="11" r="1.7"/><circle cx="6" cy="17" r="1.7"/><circle cx="12" cy="17" r="1.7"/><circle cx="18" cy="17" r="1.7"/><circle cx="12" cy="22" r="1.7"/></g></svg>
            </i>키패드
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;gap:5px;font-size:9px;color:#4A4658;font-weight:500;">
            <i style="width:40px;height:40px;border-radius:50%;background:#fff;box-shadow:0 3px 8px rgba(52,30,130,.08);display:flex;align-items:center;justify-content:center;">
              <svg viewBox="0 0 24 24" width="17" height="17" style="color:#3A3650"><g fill="currentColor"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></g></svg>
            </i>더 보기
          </div>
        </div>
      `;
      slide.appendChild(callScreen);

      // Normal white spool circle + purple spool icon on kb3 for sol3_base (covered by sol3_glow)
      const kb3Spool = document.createElement('div');
      kb3Spool.dataset.part = 'sol3_base';
      kb3Spool.style.cssText = 'position:absolute;left:650.5px;top:546.5px;width:29px;height:29px;border-radius:50%;background:#fff;border:1px solid #D8CEFA;z-index:26;display:flex;align-items:center;justify-content:center;box-sizing:border-box;';
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
          else if (id === 'sheet' || id === 'sbar1' || (b.t >= 275 && b.b <= 310 && b.cx < 400)) el.dataset.part = 'sol1_sheet';
          else el.dataset.part = 'sol1_res';
        } else if (b.cy < 424) {
          if (el.classList.contains('cursor')) el.dataset.part = 'sol2_type';
          else if (b.cx < 900) el.dataset.part = 'sol2_base';
          else el.dataset.part = 'sol2_card';
        } else {
          if (id === 'ctx3' || id === 'ctx4' || id === 'ctx4i' || (b.t >= 500 && b.b <= 536 && b.cx < 900)) el.dataset.part = 'sol3_ctx';
          else if (el.tagName === 'IMG' && b.cx < 700 && b.cy > 544 && b.cy < 580) el.dataset.part = 'sol3_glow';
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
        } else if (b.cy < 424) {
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
          if (b.t < 264) el.dataset.part = 'sol1_base';
          else if (b.t >= 264 && b.b <= 276) el.dataset.part = 'sol1_sheet';
          else if (b.t >= 276 && b.b <= 308) el.dataset.part = 'sol1_q';
          else if (b.t >= 410 && b.b <= 535) el.dataset.part = 'sol1_res';
          else if (b.cx > 485 && b.t >= 535 && b.b <= 625) el.dataset.part = 'sol1_swipe';
          else el.dataset.part = 'sol1_base';
        } else if (b.cy < 424) {
          if (el.tagName.toLowerCase() === 'circle' && Math.abs(b.cx - 665) < 5) el.dataset.part = 'sol2_base';
          else if (b.cx < 700 && b.cy < 305) el.dataset.part = 'sol2_tap';
          else if (b.cx < 900 && b.cy >= 305) el.dataset.part = 'sol2_type';
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
