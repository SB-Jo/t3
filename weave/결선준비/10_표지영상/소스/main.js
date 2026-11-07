/* Weave 결선 표지 루프 v6 — 24초, 끝과 처음이 똑같아 끊김 없이 반복된다.
   모든 상태는 시간 t의 순수 함수(render(t)). 떠다니는 움직임은 주기가 24초(또는 12초)인 사인파.
   window.__seek(t), window.__DURATION, window.__ready, window.__probe(t)
   이야기는 How it Works A1(장표5/a1.py)과 같다:
   빈 구글 검색창에 '지은이네 집들이 때 마셨던 와인'을 침 → 실타래 버튼 → 지은 카톡
   → 질문의 '지은'이 카드의 보낸 사람 '지은'으로. 메시지의 '박스 정리', '휴지 안 사 와도 돼'에 형광펜 → 질문의 '집들이' 표가 메시지로 건너가 그대로 머묾
   → 단서 '3/15 (일)'가 그날 사진(3/15 20:14)으로 → 라벨 'SAUVIGNON BLANC' → 추천 '배비치 소비뇽 블랑'
   → 입력하기 → 검색어가 '배비치 소비뇽 블랑'으로 바뀜 → 검색 키 → 쇼핑 결과 → 처음 화면(빈 검색창)으로
   v5: 전체를 천천히(18 → 24초), 첫 연결에서 추론이 보이게
   v6: 입력을 마쳐도 검색창 글자 폭이 그대로, 검색어 형광펜은 '지은이네 집들이'와 '와인', 라벨 글자는 사진을 읽은 뒤에 뜸 */
const LOOP = 24.0;
// 오른쪽 장면(#world)은 (846, 540)을 기준으로 줄임. 안쪽 계산은 모두 줄이기 전 좌표(1920×1080)로 하고, 검사용 값만 화면 좌표로 바꿈
const WS = 0.93, WO = { x: 846, y: 540 };
const toScreen = p => ({ x: WO.x + (p.x - WO.x) * WS, y: WO.y + (p.y - WO.y) * WS });
const QTEXT = '지은이네 집들이 때 마셨던 와인';   // 2026-11-05 최종 시나리오(화이트/레드 구분 없음)
const ANS = '배비치 소비뇽 블랑';
const QHTML = '<span class="hl" id="qH"><span id="qJ">지은</span>이네 <span id="qHw">집들이</span></span> 때 마셨던 <span class="hl" id="qW">와인</span>';   // 다 친 뒤의 검색어(형광펜과 표가 나가는 자리)
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, u) => a + (b - a) * u;
const TAU = Math.PI * 2;
const E = n => gsap.parseEase(n);
const e2io = E('power2.inOut'), e2o = E('power2.out'), e2i = E('power2.in'), e3o = E('power3.out'), eBack = E('back.out(1.8)'), eExpo = E('expo.out');
const seg = (t, t0, d) => clamp((t - t0) / d);
// 켜졌다가(t0부터 d0초) 꺼짐(t1부터 d1초): 0..1
const pulse = (t, t0, d0, t1, d1, ein = e2o, eout = e2io) => Math.min(ein(seg(t, t0, d0)), 1 - eout(seg(t, t1, d1)));

/* ── 시각(초) ── */
const THR = { A: 0.9, B: 0.85, C: 0.9 };   // 실 한 가닥이 그려지는 시간
const T = {
  type0: 0.9, cps: 9,                // 타자 시작, 초당 글자 수(띄어쓰기는 더 빠르게)
  tap: 4.1, wave: 4.2, shim: 4.3,    // 실타래 버튼(손은 0.8초 전부터 들어옴)
  t1: 4.7, litJ: 5.35,               // 실 → 지은 카톡이 켜짐
  qH: 5.7, tJ: 5.95, tJd: 0.85, hlN: 6.75,                // 질문의 '지은이네 집들이'에 형광펜 → '지은' 표가 카드의 보낸 사람으로
  hlB: 7.35, hlJ: 7.7, tH: 8.25, tHd: 0.9,                // 메시지의 '박스 정리', '휴지 안 사 와도 돼'에 형광펜 → '집들이' 표가 메시지로 건너가 머묾
  hlK: 10.0,                         // 이 카톡을 받은 날이 단서
  t2: 10.5, qW: 10.5, tokIn: 10.55, tokRide: 10.65, tokDur: 0.95, litP: 11.45, hlD: 11.55,   // 질문의 '와인'에 형광펜 → 받은 날이 그날 사진으로
  scan: 12.1, ocrbox: 12.65, ocrT: 13.05, hlL: 13.5,      // 사진을 읽은 다음에 라벨 글자가 뜸
  t3: 14.05, sug: 14.75,             // 추천 카드
  tapIn: 17.15,                      // 입력하기(추천 카드를 2.4초 읽을 시간)
  sel: 17.3, swap: 17.7,             // 검색어가 선택됐다가 '배비치 소비뇽 블랑'으로 바뀜
  reset: 17.45,                      // 실·카드·형광펜이 걷힘
  tapS: 18.55,                       // 검색 키
  res: 18.7, mark: 19.65,            // 쇼핑 결과, 결과 속 이름에 형광펜
  back: 22.15,                       // 처음 화면(빈 검색창)으로 0.9초, 23.05초부터 쉬는 모습
};
// 타자 시각: 글자마다 조금씩 다르게(씨앗 고정이라 늘 같음)
const TYPE_T = (() => {
  let s = 7;
  const r = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const times = [];
  let t = T.type0;
  for (const c of [...QTEXT]) { times.push(t); t += (1 / T.cps) * (0.75 + r() * 0.5) * (c === ' ' ? 0.6 : 1); }
  return times;
})();
const TYPE_END = TYPE_T[TYPE_T.length - 1];

/* ── 흩어진 기록(장표5 a1.py 채움 + scene5 EXTRA + A1의 헷갈리는 기록) ── */
const CHIPS = [
  ['app-kakao', '팀 단톡방', '회의록 공유해요'],
  ['samsung-email-blue', '관리비 고지서', '2월분 관리비'],
  ['samsung-calendar', '치과 예약', '3/4 (수) 오전 10:30'],
  ['app-notes', '장 볼 것', '우유, 계란, 휴지'],
  ['app-kakao', '엄마', '반찬 보냈다'],
  ['samsung-gallery', 'IMG_2433.jpg', '3월 8일 12:40'],
  ['samsung-email-blue', '[예약 확인] 오사카 호텔', '2월 27일'],
  ['app-kakao', '민호', '주말에 축구 콜?'],
  ['samsung-calendar', '팀 회식', '3/20 (금) 19:00'],
  ['app-notes', '회의록 3/14', '다음 주 시연 리허설'],
  ['samsung-email-blue', 'Q1_Demo_v3.pdf', '어제 오후 6:20'],
  ['app-kakao', '택배', '문 앞에 두고 갔어요'],
  ['app-map', '저장한 장소', '성수 카페'],
  ['samsung-phone', '부재중 전화', '어제 오후 3:12'],
  ['app-notes', '집들이 선물', '디퓨저로 결정!'],
  ['samsung-gallery', '스크린샷', '와인 고르는 법'],
  ['samsung-gallery', 'IMG_2475.jpg', '3월 15일 19:52', 'photo-table.jpg'],
  ['samsung-gallery', 'IMG_2510.jpg', '3월 20일 21:10', 'photo-bar.jpg'],
  ['samsung-wallet', '멤버십', '적립 1,200P'],
  ['samsung-calendar', '헬스', '화, 목 오전 7:00'],
  ['app-kakao', '회사 동기', '점심 뭐 먹지?'],
  ['app-map', '최근 경로', '회사에서 집'],
  ['samsung-email-blue', '뉴스레터', '이번 주 소식'],
];
const LAYER = { near: { s: 0.92, o: 0.38, a: 6 }, mid: { s: 0.8, o: 0.3, a: 5 }, far: { s: 0.68, o: 0.22, a: 3.5 } };
const ORDER = ['near', 'mid', 'far', 'near', 'mid', 'near', 'far', 'mid'];
// 손으로 고친 자리(자동 배치 뒤 덮어씀): 인덱스 → [x, y]
const PIN = {};

let seed = 20261102;
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

const chips = [];
let G = null;                         // 재어 둔 자리(휴대폰·카드·버튼 등, 화면 좌표)

function makeKB() {
  const KB = [['ㅂ','ㅈ','ㄷ','ㄱ','ㅅ','ㅛ','ㅕ','ㅑ','ㅐ','ㅔ'], ['ㅁ','ㄴ','ㅇ','ㄹ','ㅎ','ㅗ','ㅓ','ㅏ','ㅣ'], ['⇧','ㅋ','ㅌ','ㅊ','ㅍ','ㅠ','ㅜ','ㅡ','⌫'], ['!#1','한/영','한국어','.','↗']];
  $('#kb').innerHTML = `<div class="wvfx"><i class="glow"></i><i class="rg"></i><i class="rg"></i></div>` +
    `<div class="tb"><i class="clip"><i class="shim"></i></i><span class="wv"><img src="assets/icons/weave-spool-6B4EFF.png" alt=""><img class="lit" src="assets/icons/weave-spool-white.png" alt=""></span><svg><use href="#i-emo"/></svg><svg><use href="#i-tr"/></svg><svg><use href="#i-clip"/></svg><svg><use href="#i-gear"/></svg><span style="margin-left:auto">닫기 ⌄</span></div>` +
    KB.map(row => `<div class="krow">${row.map(k => {
      const cls = ['k'];
      if (['⇧', '⌫', '!#1', '한/영'].includes(k)) cls.push('g', 'w2');
      if (k === '한국어') cls.push('sp');
      if (k === '↗') cls.push('snd', 'w2', 'srch');
      return `<span class="${cls.join(' ')}">${k === '↗' ? '<svg width="20" height="20" style="color:#fff"><use href="#i-search"/></svg>' : k}</span>`;
    }).join('')}</div>`).join('');
}

const R = el => { const r = (typeof el === 'string' ? $(el) : el).getBoundingClientRect(); return { l: r.left, t: r.top, r: r.right, b: r.bottom, w: r.width, h: r.height, cx: r.left + r.width / 2, cy: r.top + r.height / 2 }; };
const grow = (r, m) => ({ l: r.l - m, t: r.t - m, r: r.r + m, b: r.b + m });
const hit = (a, b) => a.l < b.r && b.l < a.r && a.t < b.b && b.t < a.b;
const rdist = (a, b) => { const dx = Math.max(0, Math.max(a.l, b.l) - Math.min(a.r, b.r)), dy = Math.max(0, Math.max(a.t, b.t) - Math.min(a.b, b.b)); return Math.hypot(dx, dy); };

/* ── 실 모양 ── */
const bezH = (a, b, bend = 0.55) => { const dx = b.x - a.x; return [a, { x: a.x + dx * bend, y: a.y }, { x: b.x - dx * bend, y: b.y }, b]; };
const bezV = (a, b, bend = 0.5) => { const dy = b.y - a.y; return [a, { x: a.x, y: a.y + dy * bend }, { x: b.x, y: b.y - dy * bend }, b]; };
const bAt = (P, u) => { const v = 1 - u; return { x: v * v * v * P[0].x + 3 * v * v * u * P[1].x + 3 * v * u * u * P[2].x + u * u * u * P[3].x,
  y: v * v * v * P[0].y + 3 * v * v * u * P[1].y + 3 * v * u * u * P[2].y + u * u * u * P[3].y }; };
const dOf = P => `M${P[0].x.toFixed(2)} ${P[0].y.toFixed(2)} C ${P[1].x.toFixed(2)} ${P[1].y.toFixed(2)}, ${P[2].x.toFixed(2)} ${P[2].y.toFixed(2)}, ${P[3].x.toFixed(2)} ${P[3].y.toFixed(2)}`;

/* ── 카드: 쉬는 자리 + 떠다님 + 켜질 때 살짝 커짐(가운데 기준) ── */
const drift = (d, t) => ({ x: d.ax * Math.sin(TAU * d.kx * t / LOOP + d.px), y: d.ay * Math.sin(TAU * d.ky * t / LOOP + d.py) });
const DJ = { ax: 5, kx: 1, px: 0.6, ay: 4, ky: 1, py: 2.1 }, DP = { ax: 4.5, kx: 1, px: 2.4, ay: 5, ky: 1, py: 0.3 };
const litJ = t => pulse(t, T.litJ, 0.48, T.reset + 0.15, 0.7);
const litP = t => pulse(t, T.litP, 0.48, T.reset + 0.25, 0.7);
function cardBox(base, d, s, t) {        // 화면에서의 카드 상자
  const o = drift(d, t), w = base.w * s, h = base.h * s, cx = base.cx + o.x, cy = base.cy + o.y;
  return { l: cx - w / 2, t: cy - h / 2, r: cx + w / 2, b: cy + h / 2, w, h, cx, cy, s, ox: o.x, oy: o.y };
}
const inCard = (box, base, p) => ({ x: box.cx + (p.x - base.cx) * box.s, y: box.cy + (p.y - base.cy) * box.s });
const sJ = t => 1 + 0.035 * litJ(t), sP = t => 1 + 0.035 * litP(t);
const ocrV = t => pulse(t, T.ocrT, 0.42, T.reset + 0.1, 0.45, e2io, e2io);   // 0: 라벨 글자 접힘, 1: 펼침
const baseP = v => ({ cx: G.cP.cx, cy: lerp(G.cP0.cy, G.cP.cy, v), w: G.cP.w, h: lerp(G.cP0.h, G.cP.h, v) });

function threadPts(t, v = ocrV(t)) {
  const bP = baseP(v);
  const J = cardBox(G.cJ, DJ, sJ(t), t), P = cardBox(bP, DP, sP(t), t);
  const A = bezH({ x: G.frame.l + 5, y: G.tb.cy }, { x: J.r - 3, y: J.cy }, 0.55);
  const hj = inCard(J, G.cJ, { x: G.hlJ.cx, y: G.hlJ.cy }), hd = inCard(P, bP, { x: G.hlD.cx, y: lerp(G.hlD0.cy, G.hlD.cy, v) });
  const B = bezV({ x: hj.x, y: J.t + 3 }, { x: hd.x, y: P.b - 3 }, 0.5);
  const C = bezH({ x: P.r - 3, y: P.cy }, { x: G.frame.l + 5, y: G.sug.cy }, 0.55);
  return { A, B, C, J, P };
}

/* ── 조각 배치: 왼쪽 글자 자리(PPT 제목·이름)·휴대폰·두 카드를 피해 고르게. 실은 조각 사이를 지나가게(실 길에서 조금 띄움).
   씨앗 여러 개로 해 보고 가장 많이 들어간 배치를 씀(결과는 늘 같음, v1과 같은 배치) ── */
const TEXT_SAFE = { l: -200, t: -200, r: 846, b: 1300 };   // x 0–846은 비워 둠(PPT 글자 자리 0–820 + 여유)
function tryLayout(sd) {
  let s_ = sd;
  const rn = () => (s_ = (s_ * 16807) % 2147483647) / 2147483647;
  const th = threadPts(0, 1);             // 라벨 글자가 펼쳐진 카드 기준(그때 실이 다 그려져 있음)
  const lane = [];
  for (const P of [th.A, th.B, th.C]) for (let i = 0; i <= 60; i++) lane.push(bAt(P, i / 60));
  const avoid = [TEXT_SAFE, grow(G.frame, 22), grow(G.cJ, 24), grow(G.cP, 24)];
  const placed = [], pos = {};
  const order = chips.map((c, i) => i).sort((a, b) => chips[b].w * chips[b].h - chips[a].w * chips[a].h);
  for (const i of order) {
    const c = chips[i];
    const m = c.d.ax + 2;                 // 떠다니는 폭만큼 여유
    let best = null, bestS = -1;
    for (let k = 0; k < 700; k++) {
      const x = 860 + rn() * (1920 - 14 - 860 - c.w), y = 14 + rn() * (1080 - 28 - c.h);
      const r = { l: x - m, t: y - m, r: x + c.w + m, b: y + c.h + m };
      if (avoid.some(a => hit(r, a))) continue;
      if (lane.some(p => p.x > r.l - 14 && p.x < r.r + 14 && p.y > r.t - 14 && p.y < r.b + 14)) continue;
      if (placed.some(p => hit(grow(r, 12), p))) continue;
      const sc = Math.min(70, ...placed.map(p => rdist(r, p)), ...avoid.slice(1).map(a => rdist(r, a) * 1.4)) + 6 * rn();
      if (sc > bestS) { bestS = sc; best = { x, y, r }; }
    }
    if (!best) continue;
    pos[i] = [best.x, best.y]; placed.push(best.r);
  }
  return pos;
}
function layoutChips() {
  let best = null;
  for (let sd = 1; sd <= 40; sd++) {
    const pos = tryLayout(9000 + sd * 7919);
    const n = Object.keys(pos).length;
    if (!best || n > best.n) best = { n, pos, sd };
    if (n === chips.length) break;
  }
  chips.forEach((c, i) => { const p = PIN[i] || best.pos[i]; if (p) { c.x = p[0]; c.y = p[1]; } else { c.x = -999; c.y = -999; console.error('no room for chip', i, c.title); } });
  window.__layout = { placed: best.n, of: chips.length, seed: best.sd };
}

/* ── 손으로 누르기 ── */
const TIP = { x: 39, y: 8 };
const pressAt = (t, tp) => t < tp - 0.06 ? 1 : t < tp + 0.03 ? lerp(1, 0.9, e2o(seg(t, tp - 0.06, 0.09))) : lerp(0.9, 1, e2o(seg(t, tp + 0.03, 0.28)));
// 첫째: 오른쪽 아래에서 들어와 실타래 버튼 → 빠짐. 둘째: 들어와 입력하기 → 검색 키로 옮겨 누름 → 빠짐
function handPose(t) {
  if (t < (T.tap + T.tapIn) / 2) {
    const P = { x: G.wv.cx + 3, y: G.wv.cy + 3 };
    const ain = e3o(seg(t, T.tap - 0.8, 0.8)), aout = e2i(seg(t, T.tap + 0.42, 0.62)), off = (1 - ain) + aout;
    return { x: P.x + 190 * off, y: P.y + 250 * off, vis: clamp(ain * 1.4) * (1 - aout), press: pressAt(t, T.tap) };
  }
  const P2 = { x: G.btn.cx + 12, y: G.btn.cy + 4 }, P3 = { x: G.srch.cx + 2, y: G.srch.cy + 2 };
  const ain = e3o(seg(t, T.tapIn - 0.78, 0.78)), aout = e2i(seg(t, T.tapS + 0.4, 0.62)), off = (1 - ain) + aout;
  const mv = e2io(seg(t, T.tapIn + 0.36, T.tapS - T.tapIn - 0.43));
  const x = lerp(P2.x, P3.x, mv), y = lerp(P2.y, P3.y, mv) - 36 * Math.sin(Math.PI * mv);   // 살짝 들어 올려 옮김
  return { x: x + 190 * off, y: y + 250 * off, vis: clamp(ain * 1.4) * (1 - aout), press: Math.min(pressAt(t, T.tapIn), pressAt(t, T.tapS)) };
}

async function build() {
  const fams = ['400 20px SamsungOneKorean', '500 20px SamsungOneKorean', '700 20px SamsungOneKorean', '400 20px SamsungOne', '500 20px SamsungOne', '700 20px SamsungOne', '700 20px "Samsung Sharp Sans"'];
  await Promise.all(fams.map(f => document.fonts.load(f, '가A')));
  await document.fonts.ready;
  makeKB();
  // 조각 만들기
  CHIPS.forEach((f, i) => {
    const el = document.createElement('div');
    el.className = 'chip kr';
    el.innerHTML = `<img class="ic" src="assets/icons/${f[0]}.png" alt="">${f[3] ? `<img class="ph" src="assets/img/${f[3]}" alt="">` : ''}<div><div class="t">${f[1]}</div><div class="m">${f[2]}</div></div>`;
    $('#chips').appendChild(el);
    const layer = ORDER[i % ORDER.length], L = LAYER[layer];
    chips.push({ el, i, title: f[1], layer, s: L.s, o: L.o,
      d: { ax: L.a * (0.7 + 0.6 * rnd()), kx: 1 + Math.floor(rnd() * 2), px: rnd() * TAU, ay: L.a * (0.6 + 0.5 * rnd()), ky: 1 + Math.floor(rnd() * 2), py: rnd() * TAU } });
  });
  await Promise.all([...document.images].map(im => im.decode().catch(() => {})));
  chips.forEach(c => { const r = c.el.getBoundingClientRect(); c.w0 = r.width; c.h0 = r.height; c.w = c.w0 * c.s; c.h = c.h0 * c.s; });

  // 재어 둘 자리(모든 것이 쉬는 상태에서)
  $('#sug').style.opacity = '1';
  G = { frame: R('#phone .frame'), tb: R('#kb .tb'), wv: R('#kb .wv'), sug: R('#sug'), btn: R('#sug .b'), srch: R('#kb .srch'),
        cJ: R('#cJ'), cP: R('#cP'), hlJ: R('#hlJ'), hlD: R('#hlD'), hlL: R('#hlL'), hlN: R('#hlN'), eqH: R('#eqH'), kb: R('#kb'), q: R('#q') };
  $('#q').innerHTML = QHTML; G.qJ = R('#qJ'); G.qH = R('#qHw'); $('#q').innerHTML = '';
  // 사진 카드: 라벨 글자를 접었을 때의 자리도 잰다(처음에는 접혀 있음)
  G.ocrH = R('#ocrW').h; $('#ocrW').style.height = '0px'; G.cP0 = R('#cP'); G.hlD0 = R('#hlD');
  $('#sug').style.opacity = '0';
  // 버튼 효과를 버튼 한가운데에(키보드 기준, 휴대폰 배율을 되돌려서)
  { const k = G.kb, w = G.wv, sc = G.frame.w / 452; const fx = $('#kb .wvfx'); fx.style.left = `${(w.cx - k.l) / sc}px`; fx.style.top = `${(w.cy - k.t) / sc}px`; }
  // 바뀐 검색어 밑줄: '배비치 소비뇽 블랑' 너비만큼(검색창 안 좌표)
  { const q = $('#q'), tx = $('.gbox .tx'); q.textContent = ANS;
    Object.assign($('#gsweep').style, { left: `${tx.offsetLeft + q.offsetLeft}px`, width: `${q.offsetWidth + 2}px` }); q.textContent = ''; }
  layoutChips();
  $('#world').style.transform = `scale(${WS})`;       // 재고 배치한 뒤에 줄임(안쪽 좌표는 그대로)
  render(0);
  return true;
}

/* ── 검색창 글자: 빈칸 → 한 글자씩 → 선택 → 바뀐 이름 → (처음 화면) 빈칸 ── */
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
function qState(t) {
  const blink = ph => (((ph % 1) + 1) % 1) < 0.5;
  if (t < T.type0) return { html: '', caret: blink(t) };
  if (t < T.sel) {
    let n = 0; while (n < TYPE_T.length && TYPE_T[n] <= t + 1e-9) n++;
    const solid = t < TYPE_END + 0.45;                         // 치는 동안은 깜빡이지 않음
    return { html: n >= TYPE_T.length ? QHTML : esc([...QTEXT].slice(0, n).join('')), caret: solid || blink(t - TYPE_END - 0.45) };
  }
  if (t < T.swap) return { html: `<span class="sel">${esc(QTEXT)}</span>`, caret: false };
  if (t < T.back + 0.36) return { html: esc(ANS), caret: t < T.tapS + 0.05 };
  return { html: '', caret: blink(t) };
}
let lastQ = null;

/* ── 한 장면 그리기 ── */
function render(t) {
  t = ((t % LOOP) + LOOP) % LOOP;
  // 배경 빛: 한 바퀴에 한 번 오가는 움직임
  const w1 = Math.sin(TAU * t / LOOP);
  $('.g1').style.transform = `translate(${80 * w1}px, ${26 * Math.sin(TAU * t / LOOP + 1.2)}px)`;
  $('.g2').style.transform = `translate(${-60 * Math.sin(TAU * t / LOOP + 0.7)}px, ${-24 * w1}px)`;
  $('.g3').style.transform = `scale(${1 + 0.06 * Math.sin(TAU * t / LOOP + 2.0)})`;

  // 누른 뒤 물결(버튼에서 화면 끝까지)
  const wo = { x: G.wv.cx, y: G.wv.cy };
  const waveR = k => { const u = seg(t, T.wave + k * 0.26, 1.58); return { u, r: 1950 * e2o(u) }; };
  [['#wv1', 0], ['#wv2', 1]].forEach(([id, k]) => {
    const { u, r } = waveR(k), c = $(id);
    c.setAttribute('cx', wo.x); c.setAttribute('cy', wo.y); c.setAttribute('r', r.toFixed(1));
    c.style.opacity = (u > 0 && u < 1) ? String(0.42 * (1 - u) * (k ? 0.6 : 1)) : '0';
  });

  // 조각: 흐리게 떠다니고, 물결이 지나갈 때만 잠깐 밝아짐
  const W0 = waveR(0);
  for (const c of chips) {
    if (c.x < -900) { c.el.style.opacity = '0'; continue; }
    const o = drift(c.d, t);
    const cx = c.x + c.w / 2 + o.x, cy = c.y + c.h / 2 + o.y;
    let bump = 0;
    if (W0.u > 0 && W0.u < 1) { const dd = Math.hypot(cx - wo.x, cy - wo.y) - W0.r; bump = 0.2 * Math.exp(-((dd / 150) ** 2)) * (1 - W0.u * 0.6); }
    c.el.style.transform = `translate(${(c.x + o.x).toFixed(2)}px, ${(c.y + o.y).toFixed(2)}px) scale(${c.s})`;
    c.el.style.opacity = (c.o + bump).toFixed(3);
    c.el.style.filter = c.layer === 'far' ? 'blur(0.7px)' : 'none';
  }

  // 두 카드
  const th = threadPts(t);
  const lj = litJ(t), lp = litP(t);
  const cardStyle = (sel, box, lit) => {
    const el = $(sel);
    el.style.transform = `translate(${box.ox.toFixed(2)}px, ${box.oy.toFixed(2)}px) scale(${box.s.toFixed(4)})`;
    el.style.opacity = lerp(0.36, 1, lit).toFixed(3);
    el.querySelector('.ring').style.opacity = lit.toFixed(3);
  };
  cardStyle('#cJ', th.J, lj); cardStyle('#cP', th.P, lp);

  // 형광펜(같은 단서) — 켜질 때 왼쪽에서 오른쪽으로, 걷힐 때 반대로
  const hl = (el, v) => { el.style.setProperty('--w', `${(100 * v).toFixed(1)}%`); el.style.color = v > 0.02 ? '#5B3FE6' : ''; };
  hl($('#hlN'), pulse(t, T.hlN, 0.4, T.reset, 0.45, e2io, e2io));
  hl($('#hlB'), pulse(t, T.hlB, 0.42, T.reset, 0.45, e2io, e2io));
  hl($('#hlJ'), pulse(t, T.hlJ, 0.42, T.reset, 0.45, e2io, e2io));
  hl($('#hlK'), pulse(t, T.hlK, 0.4, T.reset, 0.45, e2io, e2io));
  hl($('#hlD'), pulse(t, T.hlD, 0.46, T.reset + 0.05, 0.45, e2io, e2io));
  hl($('#hlL'), pulse(t, T.hlL, 0.48, T.reset + 0.1, 0.45, e2io, e2io));

  // 사진 라벨 읽기: 훑는 빛 → 라벨 테두리 → 라벨 글자(카드가 그만큼 늘어남)
  const su = seg(t, T.scan, 0.62);
  $('#scan').style.opacity = (su > 0 && su < 1) ? String(Math.sin(Math.PI * su)) : '0';
  $('#scan').style.transform = `translateY(${lerp(-64, 202, e2io(su)).toFixed(1)}px)`;
  const ob = pulse(t, T.ocrbox, 0.42, T.reset + 0.1, 0.45, eBack, e2io);
  $('#ocrbox').style.opacity = clamp(ob).toFixed(3);
  $('#ocrbox').style.transform = `scale(${lerp(1.25, 1, clamp(seg(t, T.ocrbox, 0.42) ? eBack(seg(t, T.ocrbox, 0.42)) : 0)).toFixed(3)})`;

  { const v = ocrV(t);
    $('#ocrW').style.height = `${(G.ocrH * v).toFixed(2)}px`;
    $('#ocr').style.opacity = clamp(v * 1.5 - 0.5).toFixed(3); }

  // 실 세 가닥: 그려지고(머리가 나아감) → 입력하기 뒤 함께 옅어짐
  const fade = 1 - e2io(seg(t, T.reset, 0.7));
  [['#tA', th.A, T.t1, THR.A], ['#tB', th.B, T.t2, THR.B], ['#tC', th.C, T.t3, THR.C]].forEach(([id, P, t0, d]) => {
    const p = e2io(seg(t, t0, d)), d_ = dOf(P);
    $$(`${id} path`).forEach(pa => { pa.setAttribute('d', d_); pa.style.strokeDashoffset = (1 - p).toFixed(4); });
    $(id).style.opacity = p > 0.002 ? fade.toFixed(3) : '0';
  });

  // 단서 표 '3/15 (일)': 지은 카톡에서 나와 실을 타고 그날 사진의 날짜로
  {
    const tok = $('#tok');
    const a = clamp(eBack(seg(t, T.tokIn, 0.28))), out = e2i(seg(t, T.tokRide + T.tokDur - 0.05, 0.24));
    const vis = a * (1 - out);
    if (vis <= 0.001) tok.style.opacity = '0';
    else {
      const u = e2io(seg(t, T.tokRide, T.tokDur));
      const p3 = inCard(th.P, G.cP0, { x: G.hlD.cx, y: G.hlD0.cy });   // 실의 끝과 x가 같음(라벨 글자가 뜨기 전)
      const B = th.B, U0 = 0.1;
      let p;
      if (u < 0.9) p = bAt(B, U0 + (1 - U0) * u / 0.9);
      else p = { x: lerp(B[3].x, p3.x, (u - 0.9) / 0.1), y: lerp(B[3].y, p3.y, (u - 0.9) / 0.1) };
      tok.style.opacity = vis.toFixed(3);
      tok.style.transform = `translate(${p.x.toFixed(2)}px, ${p.y.toFixed(2)}px) translate(-50%, -50%) scale(${lerp(0.6, 1, a).toFixed(3)})`;
    }
  }

  // 질문의 낱말 표: '지은' → 카드의 보낸 사람, '집들이' → 메시지 끝. 표가 날아가는 동안 카드는 천천히 떠다님
  const rideTok = (el, tIn, tRide, dur, P, stay = 0) => {
    const a = clamp(eBack(seg(t, tIn, 0.28))), out = stay ? e2io(seg(t, T.reset, 0.4)) : e2i(seg(t, tRide + dur - 0.05, 0.2)), vis = a * (1 - out);
    if (vis <= 0.001) { el.style.opacity = '0'; return; }
    const u = e2io(seg(t, tRide, dur)), p = bAt(P, u);
    el.style.opacity = vis.toFixed(3);
    el.style.transform = `translate(${p.x.toFixed(2)}px, ${p.y.toFixed(2)}px) translate(-50%, -50%) scale(${(lerp(0.6, 1, a) * lerp(1, stay || 1, u)).toFixed(3)})`;
  };
  rideTok($('#tokN'), T.tJ, T.tJ + 0.1, T.tJd, bezH({ x: G.qJ.cx, y: G.qJ.cy }, inCard(th.J, G.cJ, { x: G.hlN.cx, y: G.hlN.cy }), 0.55));
  rideTok($('#tokH'), T.tH, T.tH + 0.1, T.tHd, bezH({ x: G.qH.cx, y: G.qH.cy }, inCard(th.J, G.cJ, { x: G.eqH.cx, y: G.eqH.cy }), 0.55), 0.8);   // 작아져 메시지 끝에 앉아 머묾

  // 휴대폰: 버튼 누름 → 버튼이 보라로, 빛·물결, 휴대폰 테두리 빛, 도구줄을 지나는 빛
  const bt = pulse(t, T.tap, 0.25, T.tap + 1.25, 0.45);
  $('#kb .wv').style.backgroundColor = `rgb(${Math.round(lerp(230, 107, bt))}, ${Math.round(lerp(222, 78, bt))}, ${Math.round(lerp(255, 255, bt))})`;
  $('#kb .wv').style.boxShadow = bt > 0.01 ? `0 6px 16px rgba(107,78,255,${(0.55 * bt).toFixed(3)})` : 'none';
  $('#kb .wv img.lit').style.opacity = bt.toFixed(3);
  $('#kb .wv img:not(.lit)').style.opacity = (1 - bt).toFixed(3);
  const gl = pulse(t, T.tap, 0.42, T.tap + 0.82, 0.52);
  $('#kb .wvfx .glow').style.opacity = gl.toFixed(3);
  $('#kb .wvfx .glow').style.transform = `scale(${lerp(0.2, 1, e2o(seg(t, T.tap, 0.42))).toFixed(3)})`;
  $$('#kb .wvfx .rg').forEach((r, k) => { const u = seg(t, T.tap + 0.05 + 0.28 * k, 0.95); r.style.opacity = (u > 0 && u < 1) ? (0.9 * (1 - u)).toFixed(3) : '0'; r.style.transform = `scale(${lerp(1, 3.4, e2o(u)).toFixed(3)})`; });
  const eg = pulse(t, T.tap + 0.05, 0.42, T.tap + 0.8, 0.5);
  $('#phone .frame').style.boxShadow = `0 60px 110px rgba(52,30,130,.26), 0 18px 34px rgba(52,30,130,.14), 0 0 ${Math.round(52 * eg)}px ${(8 * eg).toFixed(1)}px rgba(139,104,245,${(0.55 * eg).toFixed(3)})`;
  const sh = seg(t, T.shim, 0.52);
  $('#kb .shim').style.opacity = (sh > 0 && sh < 1) ? String(Math.sin(Math.PI * sh)) : '0';
  $('#kb .shim').style.transform = `translateX(${lerp(-40, 440, e2io(sh)).toFixed(1)}px)`;

  // 검색창 글자와 깜빡이
  const qs = qState(t);
  if (qs.html !== lastQ) { $('#q').innerHTML = qs.html; lastQ = qs.html; }
  if (qs.html === QHTML) {                                  // 질문의 단서: 추론하는 동안 형광펜(글자가 바뀌기 전에 걷힘)
    hl($('#qH'), pulse(t, T.qH, 0.45, T.reset - 0.45, 0.4, e2io, e2io));
    hl($('#qW'), pulse(t, T.qW, 0.35, T.reset - 0.45, 0.4, e2io, e2io));
  }
  $('#caret').style.opacity = qs.caret ? '1' : '0';
  const sw = seg(t, T.swap, 0.5);
  $('#gsweep').style.transform = `scaleX(${e2o(sw).toFixed(4)})`;
  $('#gsweep').style.opacity = (sw > 0 ? 1 - e2io(seg(t, T.swap + 0.6, 0.25)) : 0).toFixed(3);

  // 추천 카드(휴대폰 안): 떠오름 → 입력하기 누르면 걷힘
  const sg = pulse(t, T.sug, 0.5, T.tapIn + 0.14, 0.35, e3o, e2io);
  const sgEl = $('#sug');
  sgEl.style.opacity = sg.toFixed(3);
  sgEl.style.transform = `translateY(${((1 - sg) * 14).toFixed(2)}px) scale(${lerp(0.96, 1, sg).toFixed(4)})`;
  const rp = seg(t, T.sug + 0.1, 1.05);
  sgEl.style.boxShadow = `0 16px 34px rgba(84,56,190,.20), 0 0 0 1.5px #D9CBFF inset, 0 0 0 ${(rp > 0 && rp < 1 ? 26 * e2o(rp) : 0).toFixed(1)}px rgba(166,124,242,${(rp > 0 && rp < 1 ? 0.55 * (1 - rp) : 0).toFixed(3)})`;
  const bp = pulse(t, T.tapIn - 0.04, 0.08, T.tapIn + 0.08, 0.25);
  $('#sug .b').style.transform = `scale(${(1 - 0.04 * bp).toFixed(4)})`;
  $('#sug .b').style.background = `rgb(${Math.round(lerp(107, 78, bp))}, ${Math.round(lerp(78, 54, bp))}, ${Math.round(lerp(255, 207, bp))})`;

  // 검색 키 누름 → 불러오기 줄 → 결과 화면(키보드 내려감, 검색창 위로, 결과 하나씩) → 처음 화면으로
  const kp = pulse(t, T.tapS - 0.04, 0.08, T.tapS + 0.08, 0.25), kr = seg(t, T.tapS, 0.6);
  $('#kb .srch').style.background = `rgb(${Math.round(lerp(47, 31, kp))}, ${Math.round(lerp(107, 85, kp))}, ${Math.round(lerp(255, 224, kp))})`;
  $('#kb .srch').style.boxShadow = (kr > 0 && kr < 1) ? `0 0 0 ${(12 * e2o(kr)).toFixed(2)}px rgba(47,107,255,${(0.55 * (1 - kr)).toFixed(3)})` : 'none';
  const ld = seg(t, T.tapS + 0.05, 0.45);
  $('#gload').style.transform = `scaleX(${E('power1.inOut')(ld).toFixed(4)})`;
  $('#gload').style.opacity = (ld > 0 ? 1 - seg(t, T.tapS + 0.5, 0.15) : 0).toFixed(3);
  const inR = e3o(seg(t, T.res, 0.45));                    // 0: 처음 화면, 1: 결과 화면
  const out1 = e2io(seg(t, T.back, 0.34));                 // 결과 화면이 걷힘
  const in1 = e2o(seg(t, T.back + 0.36, 0.55));             // 처음 화면이 다시 나타남
  const resOn = t >= T.res && t < T.back + 0.36;
  const kbDown = t < T.res ? 0 : t < T.back + 0.34 ? inR : 1 - e3o(seg(t, T.back + 0.34, 0.55));   // 1이면 키보드가 화면 아래로
  $('#kb').style.transform = `translateY(${(340 * kbDown).toFixed(2)}px)`;
  const homeOp = t < T.res ? 1 : resOn ? 1 - clamp(inR * 2) : in1;
  $('.glogo').style.opacity = homeOp.toFixed(3); $('.gtop').style.opacity = homeOp.toFixed(3);
  $('.gbox').style.transform = `translateY(${(resOn ? -178 * inR : 0).toFixed(2)}px)`;
  $('.gbox').style.opacity = (t < T.back ? 1 : t < T.back + 0.36 ? 1 - out1 : in1).toFixed(3);
  $('#gres').style.opacity = (resOn ? 1 - out1 : 0).toFixed(3);
  $$('#gres > *').forEach((el, k) => {
    const u = eExpo(seg(t, T.res + 0.14 + 0.08 * k, 0.55));
    el.style.opacity = (resOn ? u : 0).toFixed(3);
    el.style.transform = `translateY(${((1 - u) * 14).toFixed(2)}px)`;
  });
  $$('#gres .hl').forEach((el, k) => hl(el, resOn ? e2io(seg(t, T.mark + 0.05 * k, 0.45)) : 0));

  // 손
  {
    const hand = $('#hand'), H = handPose(t);
    hand.style.opacity = H.vis.toFixed(3);
    hand.style.transform = `translate(${(H.x - TIP.x).toFixed(2)}px, ${(H.y - TIP.y).toFixed(2)}px) rotate(-12deg) scale(${H.press.toFixed(3)})`;
    const sp = $('#spark'), su2 = seg(t, T.tap, 0.56);
    sp.style.opacity = (su2 > 0 && su2 < 1) ? '1' : '0';
    sp.style.transform = `translate(${G.wv.cx}px, ${G.wv.cy}px)`;
    const draw = e2o(seg(t, T.tap, 0.22)), undraw = e2i(seg(t, T.tap + 0.24, 0.3));
    // 그려지는 머리(0→1) 뒤로 꼬리가 따라감(0→1)
    $$('#spark .sp').forEach(pa => { pa.style.strokeDasharray = `${Math.max(0.0001, draw - undraw).toFixed(4)} 2`; pa.style.strokeDashoffset = (-undraw).toFixed(4); });
  }
}

/* ── 검사용 ── */
window.__probe = t => {
  render(t);
  const box = el => { const r = el.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom].map(v => +v.toFixed(1)); };
  const th = threadPts(((t % LOOP) + LOOP) % LOOP);
  const tx = $('.gbox .tx');
  return {
    chips: chips.map(c => ({ i: c.i, title: c.title, layer: c.layer, op: +c.el.style.opacity, r: box(c.el) })),
    cJ: box($('#cJ')), cP: box($('#cP')), frame: box($('#phone .frame')), sug: box($('#sug')), hand: box($('#hand')), handOp: +$('#hand').style.opacity,
    wave: ['#wv1', '#wv2'].map(s => ({ r: +$(s).getAttribute('r') * WS, op: +$(s).style.opacity })), waveO: toScreen({ x: G.wv.cx, y: G.wv.cy }),
    lanes: [th.A, th.B, th.C].map(P => { const pts = []; for (let i = 0; i <= 40; i++) pts.push(toScreen(bAt(P, i / 40))); return pts; }),
    ends: { A: [th.A[0], th.A[3]].map(toScreen), B: [th.B[0], th.B[3]].map(toScreen), C: [th.C[0], th.C[3]].map(toScreen) },
    edges: (() => {   // 화면 가장자리까지 남은 여백(보이는 조각·카드·휴대폰)
      const bs = [...chips.filter(c => +c.el.style.opacity > 0.01).map(c => box(c.el)), box($('#cJ')), box($('#cP')), box($('#phone .frame'))];
      return { top: Math.min(...bs.map(b => b[1])), bottom: 1080 - Math.max(...bs.map(b => b[3])), right: 1920 - Math.max(...bs.map(b => b[2])), phoneRight: 1920 - box($('#phone .frame'))[2], phoneTop: box($('#phone .frame'))[1], phoneBottom: 1080 - box($('#phone .frame'))[3] };
    })(),
    drawn: ['#tA', '#tB', '#tC'].map(id => +getComputedStyle($(id)).opacity),
    hlLines: ['#hlJ', '#hlD', '#hlL', '#q', ...$$('#gres .hl')].map(s => (typeof s === 'string' ? $(s) : s).getClientRects().length),
    hl: ['#hlJ', '#hlD', '#hlL'].map(s => ({ r: box($(s)), w: $(s).style.getPropertyValue('--w') })),
    tok: { op: +$('#tok').style.opacity, r: box($('#tok')) },
    q: { text: $('#q').textContent, scroll: tx.scrollWidth, client: tx.clientWidth },
    resN: $$('#gres .res .n').map(el => Math.round(el.getBoundingClientRect().height / (parseFloat(getComputedStyle(el).lineHeight) * 0.84))),
    screen: box($('#phone .screen')), gres: box($('#gres')), gresOp: +$('#gres').style.opacity,
  };
};
window.__DURATION = LOOP;
window.__seek = t => render(t);
window.__ready = build();
