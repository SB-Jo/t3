// HTML 슬라이드 → (1) 미리보기 PNG, (2) 텍스트를 숨긴 그래픽 레이어 PNG, (3) PPTX 변환용 레이아웃 JSON
// 사용: node tools/render.cjs pages/page-07-pipeline.html [--preview-only]
const path = require('node:path');
const fs = require('node:fs');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.PW_CORE || '/tmp/claude-weave-0927/node_modules/playwright-core');

const CHROME = process.env.CHROME || '/home/jaeung/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
const ROOT = path.resolve(__dirname, '..');
const OUT = process.env.OUT_DIR ? path.resolve(process.env.OUT_DIR) : path.join(ROOT, 'out');  // OUT_DIR로 출력 폴더 지정 가능 (예: v1/out)
fs.mkdirSync(OUT, { recursive: true });

async function run(file, previewOnly) {
  const name = path.basename(file, '.html');
  const browser = await chromium.launch({ executablePath: CHROME, headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--force-color-profile=srgb', '--font-render-hinting=none'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 2 });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    await page.goto(pathToFileURL(path.resolve(file)).href);
    await page.waitForFunction(() => window.pageReady === true, null, { timeout: 15000 });
    await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode().catch(() => null))); });
    const slide = await page.$('#slide');
    await slide.screenshot({ path: path.join(OUT, `${name}.png`) });

    const report = await page.evaluate(() => {
      const S = document.getElementById('slide').getBoundingClientRect();
      const rel = r => ({ x: +(r.left - S.left).toFixed(2), y: +(r.top - S.top).toFixed(2), w: +r.width.toFixed(2), h: +r.height.toFixed(2) });
      const missing = [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.src);
      const fontsLoaded = [...document.fonts].filter(f => f.status === 'loaded').map(f => `${f.family} ${f.weight}`);
      // 텍스트가 슬라이드 밖으로 나가거나 서로 겹치는지 점검
      const texts = [...document.querySelectorAll('[data-x]')].map(el => ({ el, r: el.getBoundingClientRect() }));
      const out = texts.filter(({ r }) => r.left < S.left - 0.5 || r.top < S.top - 0.5 || r.right > S.right + 0.5 || r.bottom > S.bottom + 0.5).map(({ el }) => el.textContent.trim().slice(0, 40));
      const inkBoxes = texts.map(({ el }) => { const rg = document.createRange(); rg.selectNodeContents(el); const rr = rg.getBoundingClientRect(); return { t: el.textContent.trim().slice(0, 30), r: rr }; });
      const overlaps = [];
      for (let i = 0; i < inkBoxes.length; i++) for (let j = i + 1; j < inkBoxes.length; j++) {
        const a = inkBoxes[i].r, b = inkBoxes[j].r;
        const ix = Math.min(a.right, b.right) - Math.max(a.left, b.left), iy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ix > 1.5 && iy > 3) overlaps.push(`${inkBoxes[i].t} ⟂ ${inkBoxes[j].t} (${ix.toFixed(1)}×${iy.toFixed(1)})`);
      }
      return { missing, fontsLoaded, outOfSlide: out, textOverlaps: overlaps, textCount: texts.length };
    });
    report.errors = errors;
    if (previewOnly) { console.log(JSON.stringify(report, null, 1)); return; }

    // PPTX 변환용 레이아웃 추출
    const layout = await page.evaluate(() => {
      const S = document.getElementById('slide').getBoundingClientRect();
      const rgba = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(s => parseFloat(s)); return { hex: p.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase(), a: p.length > 3 ? p[3] : 1 }; };
      const shapes = [...document.querySelectorAll('[data-s]')].map(el => {
        const cs = getComputedStyle(el), r = el.getBoundingClientRect();
        return { x: r.left - S.left, y: r.top - S.top, w: r.width, h: r.height,
          fill: rgba(cs.backgroundColor), line: parseFloat(cs.borderTopWidth) > 0 ? rgba(cs.borderTopColor) : null,
          lineW: parseFloat(cs.borderTopWidth) || 0, dash: cs.borderTopStyle === 'dashed', radius: parseFloat(cs.borderTopLeftRadius) || 0,
          shadow: cs.boxShadow !== 'none' ? cs.boxShadow : null, rot: el.dataset.rot || null };
      });
      const runsOf = el => {
        const lines = [[]];
        const walk = (node, inherited) => {
          for (const n of node.childNodes) {
            if (n.nodeType === 3) { const txt = n.textContent.replace(/[ \t\n\r]+/g, ' '); if (txt) lines[lines.length - 1].push({ t: txt, ...inherited }); }
            else if (n.nodeName === 'BR') lines.push([]);
            else if (n.nodeType === 1) { const cs = getComputedStyle(n); walk(n, { c: rgba(cs.color), b: +cs.fontWeight, fam: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(), sz: parseFloat(cs.fontSize), sup: inherited.sup || (cs.verticalAlign !== 'baseline' && cs.verticalAlign !== 'middle') }); }
          }
        };
        const cs = getComputedStyle(el);
        walk(el, { c: rgba(cs.color), b: +cs.fontWeight, fam: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(), sz: parseFloat(cs.fontSize) });
        // 줄 앞뒤 공백 정리
        return lines.map(l => { if (l.length) { l[0].t = l[0].t.replace(/^[ \t\n\r]+/, ''); l[l.length - 1].t = l[l.length - 1].t.replace(/[ \t\n\r]+$/, ''); } return l.filter(r => r.t.length); });
      };
      const texts = [...document.querySelectorAll('[data-x]')].map(el => {
        const cs = getComputedStyle(el), r = el.getBoundingClientRect();
        const rg = document.createRange(); rg.selectNodeContents(el); const ink = rg.getBoundingClientRect();
        const tr = cs.transform !== 'none' ? cs.transform : null;
        let rot = 0; if (tr) { const m = tr.match(/matrix\(([^)]+)\)/); if (m) { const [a, b] = m[1].split(',').map(parseFloat); rot = Math.atan2(b, a) * 180 / Math.PI; } }
        const box = tr ? { x: el.offsetLeft, y: el.offsetTop, w: el.offsetWidth, h: el.offsetHeight } : { x: r.left - S.left, y: r.top - S.top, w: r.width, h: r.height };
        return { ...box, inkX: ink.left - S.left, inkW: ink.width,
          align: cs.textAlign, lh: parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.4, ls: parseFloat(cs.letterSpacing) || 0,
          size: parseFloat(cs.fontSize), rot, lines: runsOf(el) };
      });
      return { shapes, texts };
    });
    fs.writeFileSync(path.join(OUT, `${name}.layout.json`), JSON.stringify(layout, null, 1));

    // 그래픽 레이어 (텍스트·네이티브 도형·배경 제외, 투명 배경)
    await page.evaluate(() => { document.body.classList.add('art-only'); document.documentElement.style.background = 'transparent'; document.body.style.background = 'transparent'; });
    await slide.screenshot({ path: path.join(OUT, `${name}.art.png`), omitBackground: true });
    console.log(JSON.stringify(report, null, 1));
  } finally { await browser.close(); }
}

const args = process.argv.slice(2);
const previewOnly = args.includes('--preview-only');
(async () => { for (const f of args.filter(a => !a.startsWith('--'))) { console.log('▶', f); await run(f, previewOnly); } })()
  .catch(e => { console.error(e); process.exit(1); });
