// 표지 루프를 프레임마다(1/30초) 검사:
//  - 왼쪽 글자 자리(x 0–846)에 아무것도 없는지(조각·실·손·단서 표)
//  - 조각이 휴대폰·두 카드·다른 조각과 겹치지 않는지, 그려진 실이 조각을 지나가지 않는지
//  - 실의 두 끝이 카드 가장자리·휴대폰 가장자리에 붙어 있는지
//  - 형광펜 글자가 한 줄인지(줄바꿈으로 형광펜이 갈라지지 않는지)
//  - (v2) 검색창 글자가 칸을 넘치지 않는지, 결과 상품 이름이 두 줄 안인지, 손이 왼쪽 글자 자리에 들어오지 않는지
//  - (v3) 보이는 조각·카드·휴대폰이 화면 위·아래·오른쪽 가장자리에서 얼마나 떨어져 있는지(가장 가까운 값)
// 사용: node tools/check_cover.cjs [--fps 30]
const path = require('path'), { pathToFileURL } = require('url');
const HOME = process.env.HOME;
const { chromium } = require(path.join(HOME, '.cache/weave-tools/node/node_modules/playwright-core'));
const CHROME = path.join(HOME, '.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell');
const ROOT = path.resolve(__dirname, '..');
const arg = (k, d) => { const i = process.argv.indexOf(k); return i < 0 ? d : Number(process.argv[i + 1]); };
const hit = (a, b, pad = 0) => a[0] < b[2] + pad && b[0] < a[2] + pad && a[1] < b[3] + pad && b[1] < a[3] + pad;
const SAFE = 846;
(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(pathToFileURL(path.join(ROOT, '소스', 'index.html')).href);
  await page.evaluate(() => window.__ready);
  const DUR = await page.evaluate(() => window.__DURATION), fps = arg('--fps', 30), N = Math.round(DUR * fps);
  const lay = await page.evaluate(() => window.__layout);
  const bad = { safeZone: [], chipPhone: [], chipCard: [], chipChip: [], laneChip: [], endGap: [], hlWrap: [], qOverflow: [], resWrap: [] };
  let maxQ = 0; const edge = { top: 1e9, bottom: 1e9, right: 1e9, phoneRight: 1e9, phoneTop: 1e9, phoneBottom: 1e9 };
  let minChipGap = 1e9, minLaneGap = 1e9, maxEnd = 0;
  for (let i = 0; i <= N; i++) {
    const t = i / fps, P = await page.evaluate(tt => window.__probe(tt), t);
    const vis = P.chips.filter(c => c.op > 0.01);
    for (const c of vis) {
      if (c.r[0] < SAFE) bad.safeZone.push([t.toFixed(2), 'chip', c.title]);
      if (hit(c.r, P.frame)) bad.chipPhone.push([t.toFixed(2), c.title]);
      if (hit(c.r, P.cJ) || hit(c.r, P.cP)) bad.chipCard.push([t.toFixed(2), c.title]);
    }
    for (let a = 0; a < vis.length; a++) for (let b = a + 1; b < vis.length; b++) {
      const A = vis[a].r, B = vis[b].r;
      if (hit(A, B)) bad.chipChip.push([t.toFixed(2), vis[a].title, vis[b].title]);
      const dx = Math.max(0, Math.max(A[0], B[0]) - Math.min(A[2], B[2])), dy = Math.max(0, Math.max(A[1], B[1]) - Math.min(A[3], B[3]));
      minChipGap = Math.min(minChipGap, Math.hypot(dx, dy));
    }
    P.lanes.forEach((lane, k) => {
      if (P.drawn[k] <= 0.01) return;
      for (const p of lane) {
        if (p.x < SAFE) bad.safeZone.push([t.toFixed(2), 'thread', k]);
        for (const c of vis) {
          const inside = p.x > c.r[0] && p.x < c.r[2] && p.y > c.r[1] && p.y < c.r[3];
          if (inside) bad.laneChip.push([t.toFixed(2), k, c.title]);
          const dx = Math.max(c.r[0] - p.x, 0, p.x - c.r[2]), dy = Math.max(c.r[1] - p.y, 0, p.y - c.r[3]);
          minLaneGap = Math.min(minLaneGap, Math.hypot(dx, dy));
        }
      }
    });
    // 실 끝: 카드 가장자리에서 4px 안(카드 안쪽 3px로 묻힘), 휴대폰은 틀 왼쪽 가장자리에서 10px 안
    const E = P.ends, F = P.frame, J = P.cJ, Q = P.cP;
    const gaps = [Math.abs(E.A[0].x - F[0]) <= 10 ? 0 : 99, Math.abs(E.A[1].x - J[2]), Math.abs(E.B[0].y - J[1]), Math.abs(E.B[1].y - Q[3]),
      Math.abs(E.C[0].x - Q[2]), Math.abs(E.C[1].x - F[0]) <= 10 ? 0 : 99];
    const inY = E.A[1].y > J[1] && E.A[1].y < J[3] && E.C[0].y > Q[1] && E.C[0].y < Q[3] && E.B[0].x > J[0] && E.B[0].x < J[2] && E.B[1].x > Q[0] && E.B[1].x < Q[2];
    const g = Math.max(...gaps); maxEnd = Math.max(maxEnd, g);
    if (g > 4 || !inY) bad.endGap.push([t.toFixed(2), gaps.map(v => v.toFixed(1)).join('/'), inY]);
    if (P.hlLines.some((n, k) => k === 3 ? n > 1 : n !== 1)) bad.hlWrap.push([t.toFixed(2), P.hlLines.join(',')]);   // 3번째(#q)는 빈칸이면 0줄
    maxQ = Math.max(maxQ, P.q.scroll - P.q.client);
    for (const k of Object.keys(edge)) edge[k] = Math.min(edge[k], P.edges[k]);
    if (P.q.scroll > P.q.client) bad.qOverflow.push([t.toFixed(2), P.q.text, P.q.scroll, P.q.client]);
    if (P.resN.some(n => n > 2)) bad.resWrap.push([t.toFixed(2), P.resN.join(',')]);
    if (P.tok.op > 0.01 && P.tok.r[0] < SAFE) bad.safeZone.push([t.toFixed(2), 'token']);
    if (P.handOp > 0.01 && P.hand[0] < SAFE) bad.safeZone.push([t.toFixed(2), 'hand']);
  }
  console.log(`layout: ${lay.placed}/${lay.of} chips placed (seed ${lay.seed})`);
  console.log(`frames checked: ${N + 1} (0–${DUR}s at ${fps}fps)`);
  for (const [k, v] of Object.entries(bad)) console.log(`${k}: ${v.length}`, v.slice(0, 5).map(x => x.join(' ')).join(' | '));
  console.log(`edge room (closest over all frames): top ${edge.top.toFixed(1)}px, bottom ${edge.bottom.toFixed(1)}px, right ${edge.right.toFixed(1)}px; phone: top ${edge.phoneTop.toFixed(1)}, bottom ${edge.phoneBottom.toFixed(1)}, right ${edge.phoneRight.toFixed(1)}px`);
  console.log(`search box: widest text needs ${maxQ}px more than the box (≤ 0 means it fits)`);
  console.log(`closest chip-to-chip gap: ${minChipGap.toFixed(1)}px, closest drawn thread to a chip: ${minLaneGap.toFixed(1)}px, worst thread-end gap: ${maxEnd.toFixed(1)}px`);
  await browser.close();
})();
