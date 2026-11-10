// page-05-solution_claude.html → 조각(data-l)마다 투명 PNG 한 장 + 글상자·자리 정보.
// 09_HowItWorks/장표5_claude/build.py가 이 조각들을 PowerPoint 묶음으로 넣어 하나씩 움직인다.
//
//   node export_layers_claude.cjs            (07_소스/slides/p05_결선에서)
//   → out_claude/layers/<조각>.png (3배 화소, 그림자까지 담아 빈 둘레만 잘라 냄), out_claude/layers.json, out_claude/page-05-solution_claude.png(미리보기)
//
// 화면 전체 크기로 찍은 뒤 crop_layers_claude.py가 빈 둘레를 잘라 낸다(이 스크립트가 끝에 부름).
const path = require('node:path');
const fs = require('node:fs');
const { pathToFileURL } = require('node:url');
const { execFileSync } = require('node:child_process');
const HOME = process.env.HOME;
const { chromium } = require(process.env.PW_CORE || path.join(HOME, '.cache/weave-tools/node/node_modules/playwright-core'));

const CHROME = process.env.CHROME || path.join(HOME, '.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell');
const PY = process.env.PY || path.join(HOME, '.cache/weave-tools/venv/bin/python');
const HTML = path.resolve(__dirname, 'page-05-solution_claude.html');
const OUT = path.resolve(__dirname, 'out_claude');
const RAW = process.env.RAW_DIR || path.join(OUT, '_raw');
const SCALE = 3;
const PAD = 80;            // 장표 아래로 번지는 그림자까지 찍으려고 아래로 더 넓게 찍음(휴대폰 그림자가 720px 아래로 내려감)
const safe = (l) => l.replace(/\//g, '_');

(async () => {
  fs.rmSync(RAW, { recursive: true, force: true });
  fs.mkdirSync(RAW, { recursive: true });
  const browser = await chromium.launch({ executablePath: CHROME, headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--force-color-profile=srgb', '--font-render-hinting=none'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 720 + PAD }, deviceScaleFactor: SCALE });
    const errors = [];
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    await page.goto(pathToFileURL(HTML).href);
    await page.waitForFunction(() => window.pageReady === true, null, { timeout: 15000 });
    await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map((i) => i.decode().catch(() => null))); });
    const slide = await page.$('#slide');
    await slide.screenshot({ path: path.join(OUT, 'page-05-solution_claude.png') });

    const info = await page.evaluate(() => {
      const S = document.getElementById('slide').getBoundingClientRect();
      const rgba = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map((s) => parseFloat(s)); return { hex: p.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase(), a: p.length > 3 ? p[3] : 1 }; };
      const runsOf = (el) => {
        const lines = [[]];
        const walk = (node, inh) => {
          for (const n of node.childNodes) {
            if (n.nodeType === 3) { const txt = n.textContent.replace(/[ \t\n\r]+/g, ' '); if (txt) lines[lines.length - 1].push({ t: txt, ...inh }); }
            else if (n.nodeName === 'BR') lines.push([]);
            else if (n.nodeType === 1) { const cs = getComputedStyle(n); walk(n, { c: rgba(cs.color), b: +cs.fontWeight, fam: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(), sz: parseFloat(cs.fontSize) }); }
          }
        };
        const cs = getComputedStyle(el);
        walk(el, { c: rgba(cs.color), b: +cs.fontWeight, fam: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(), sz: parseFloat(cs.fontSize) });
        return lines.map((l) => { if (l.length) { l[0].t = l[0].t.replace(/^[ \t\n\r]+/, ''); l[l.length - 1].t = l[l.length - 1].t.replace(/[ \t\n\r]+$/, ''); } return l.filter((r) => r.t.length); });
      };
      const layers = [];
      for (const e of document.querySelectorAll('[data-l]')) if (!layers.includes(e.dataset.l)) layers.push(e.dataset.l);
      const texts = [...document.querySelectorAll('[data-x]')].map((el) => {
        const cs = getComputedStyle(el), r = el.getBoundingClientRect();
        const host = el.closest('[data-l]');
        return { l: host ? host.dataset.l : null, id: el.id || null, x: r.left - S.left, y: r.top - S.top, w: r.width, h: r.height,
          align: cs.textAlign, lh: parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.4, ls: parseFloat(cs.letterSpacing) || 0,
          size: parseFloat(cs.fontSize), lines: runsOf(el) };
      });
      const missing = [...document.images].filter((i) => !i.complete || !i.naturalWidth).map((i) => i.src);
      return { layers, texts, geom: window.GEOM || {}, missing, orphanTexts: texts.filter((t) => !t.l).map((t) => t.lines.flat().map((r) => r.t).join('')) };
    });
    if (errors.length || info.missing.length || info.orphanTexts.length) { console.error({ errors, missing: info.missing, orphanTexts: info.orphanTexts }); process.exit(1); }

    await page.evaluate(() => { document.body.classList.add('art-only'); document.documentElement.style.background = 'transparent'; document.body.style.background = 'transparent';
      document.getElementById('slide').style.overflow = 'visible'; });
    for (const l of info.layers) {
      await page.evaluate((name) => { for (const e of document.querySelectorAll('[data-l]')) e.style.visibility = e.dataset.l === name ? 'visible' : 'hidden'; }, l);
      await page.screenshot({ path: path.join(RAW, safe(l) + '.png'), omitBackground: true, clip: { x: 0, y: 0, width: 1280, height: 720 + PAD } });
    }
    fs.writeFileSync(path.join(RAW, 'info.json'), JSON.stringify({ scale: SCALE, layers: info.layers, texts: info.texts, geom: info.geom }, null, 1));
    console.log('조각', info.layers.length, '· 글상자', info.texts.length);
  } finally { await browser.close(); }
  console.log(execFileSync(PY, [path.join(__dirname, 'crop_layers_claude.py'), RAW, OUT], { encoding: 'utf-8' }).trim());
  if (!process.env.KEEP_RAW) fs.rmSync(RAW, { recursive: true, force: true });
})().catch((e) => { console.error(e); process.exit(1); });
