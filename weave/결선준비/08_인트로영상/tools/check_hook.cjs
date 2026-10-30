// 도입부를 프레임마다(1/60초) 검사: 자막의 앱과 밝아진 조각이 맞는지, 조각이 제목·자막과 겹치지 않는지
// 사용: node tools/check_hook.cjs [--from 2.5 --to 10.6]
const path = require('path'), { pathToFileURL } = require('url');
const HOME = process.env.HOME;
const { chromium } = require(path.join(HOME, '.cache/weave-tools/node/node_modules/playwright-core'));
const CHROME = path.join(HOME, '.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell');
const ROOT = path.resolve(__dirname, '..');
const arg = (k, d) => { const i = process.argv.indexOf(k); return i < 0 ? d : Number(process.argv[i + 1]); };
const hit = (a, b, pad = 0) => a[0] < b[2] + pad && b[0] < a[2] + pad && a[1] < b[3] + pad && b[1] < a[3] + pad;
(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(pathToFileURL(path.join(ROOT, '소스', 'index.html')).href);
  await page.evaluate(() => window.__ready);
  const from = arg('--from', 2.5), to = arg('--to', 10.6);
  const bad = { overlapTitle: [], overlapSub: [], wrongLit: [], brightenOff: [], brightBeforeFirst: [] };
  let prev = null, minGapTitle = 1e9, minGapSub = 1e9, frames = 0;
  for (let i = Math.round(from * 60); i <= Math.round(to * 60); i++) {
    const t = i / 60, P = await page.evaluate(tt => window.__probe(tt), t);
    frames++;
    let ci = -1; P.clT.forEach((c, k) => { if (t >= c) ci = k; });
    P.frags.forEach((f, k) => {
      if (f.op > 0.03 && P.hookOp > 0.05) for (const L of P.hook) { if (hit(f.r, L)) bad.overlapTitle.push([t.toFixed(3), k, f.kind]); minGapTitle = Math.min(minGapTitle, f.r[1] - L[3]); }
      if (f.op > 0.03) for (const c of P.clauses) if (c.op > 0.05) { if (hit(f.r, c.r)) bad.overlapSub.push([t.toFixed(3), k]); minGapSub = Math.min(minGapSub, c.r[1] - f.r[3]); }
      // 첫 자막 전: 모든 조각이 흐린 상태로 등장(밝게 나왔다가 어두워지지 않음)
      if (ci < 0 && (f.op > P.offOp + 0.005 || f.ring > 0.005)) bad.brightBeforeFirst.push([t.toFixed(3), k, f.kind, f.op.toFixed(2)]);
      // 자막 전환이 끝난 뒤(0.45초)에는: 지금 앱 조각만 밝고 테두리, 나머지는 어둡게
      const settled = ci >= 0 && t >= P.clT[ci] + 0.46 && t >= P.t0[k] + 0.56;
      if (settled) {
        const on = f.kind === P.clK[ci];
        if (on && (f.op < 0.98 || f.ring < 0.98)) bad.wrongLit.push([t.toFixed(3), k, f.kind, 'on but dim', f.op.toFixed(2)]);
        if (!on && (f.op > P.offOp + 0.01 || f.ring > 0.02)) bad.wrongLit.push([t.toFixed(3), k, f.kind, 'off but lit', f.op.toFixed(2), f.ring.toFixed(2)]);
      }
      // 첫 자막 이후: 지금 앱이 아닌 조각은 절대 다시 밝아지지 않는다
      if (prev && ci >= 0 && f.kind !== P.clK[ci] && f.op > prev[k] + 0.004 && t >= P.t0[k] + 0.56) bad.brightenOff.push([t.toFixed(3), k, f.kind, prev[k].toFixed(3), f.op.toFixed(3)]);
    });
    prev = P.frags.map(f => f.op);
  }
  console.log(`frames checked: ${frames} (${from}–${to}s at 60fps)`);
  for (const [k, v] of Object.entries(bad)) console.log(`${k}: ${v.length}`, v.slice(0, 6).map(x => x.join(' ')).join(' | '));
  console.log(`closest frag top to title bottom: ${minGapTitle}px, closest frag bottom to subtitle top: ${minGapSub}px`);
  await browser.close();
})();
