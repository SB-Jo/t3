/* Weave 결선 인트로 v8 — GSAP 타임라인 하나(paused)를 시간 t로 탐색해 프레임을 찍는다.
   window.__seek(t), window.__DURATION, window.__events(효과음 시점 → tools/music.py), window.__ready, window.__taps, window.__marks, window.__probe(t)
   v6(2026-10-30 피드백): 전체를 천천히(74초), 단계마다 멈추며 단서가 이어지는 게 보이게
   - 도입: 조각은 처음부터 흐리게 등장, 자막 간격 1.55초
   - 01: 캘린더 날짜 강조 → 같은 날짜(3월 15일)가 사진 카드로 건너가 강조, '라벨엔 뭐라고?'는 글자를 읽은 뒤 답 카드 위,
         검색 뒤에는 검색창 대신 결과의 이름 부분을 강조
   - 02: 통화 말풍선은 휴대폰 왼쪽 위에 계속 있고, 통화 → 검색 → 기록(형광펜) → 답변 말풍선 순서로 천천히. 시트 속 'A사 시연 준비' 칩은 뺌
   - 03: 문장·플로팅을 오른쪽으로 더 옮김. 첫 세 메시지는 확대만(카메라 이동 없음).
         위치(대전역)를 강조 → '대전'이 가족 단체방의 '대전'으로 건너감 → Weave 버튼이 빛·물결·별·배지와 함께 크게 반짝
   v7(2026-10-30 두 번째 피드백): 장면 뱃지를 빼고 문장을 크게, 03 끝에서 입력·보낸 말을 크게 확대, 02 '노트였나…'는 왼쪽(확대되는 휴대폰과 안 겹치게),
         검색창 밑줄은 글자 길이만큼, 가족 단체방은 카카오톡처럼 이름 → 사진 → 말풍선
   v8(2026-10-30 세 번째 피드백, 03만): 대화 세 개 사이를 조금씩 더 띄움(합쳐서 1.45초), 가족 단체방에서도 '대전'·'성심당 무화과시루'를 형광펜으로,
         Weave 시트는 1초 더 머물며 추천 문장을 확대해 '먹고 싶다던 무화과시루'에 형광펜, 입력하기 → 전송 → 답장 간격도 조금씩 더(로고 74.1초, 79.1초)
   상태가 겹치기 쉬운 것(조각 밝기, 글자, 화면 전환)은 tween 대신 cont(시간 t의 순수 함수)로 매 프레임 다시 계산한다. */
gsap.registerPlugin(DrawSVGPlugin, MotionPathPlugin, CustomEase);
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];

/* ── 음악 마디에 맞춘 시각(tools/music.py와 같은 값) ── */
const D1 = 11.7, BAR = 2.4;                            // 곡(Mixkit 'A Special Feeling', 100 BPM)이 터지는 순간, 한 마디 길이

/* ── 장면 시각(초) ── */
const C1 = 11.25, P0 = 12.7;                           // 01 카드, 01 휴대폰 등장
const T2 = P0 + 16.7, X1 = T2 + 5.3;                   // 01 입력하기, 01 끝
const C2 = X1 + 0.45, s2 = C2 + 1.0;                   // 02 카드, 02 시작
const dragT = s2 + 4.5, dragD = 1.05, X2 = dragT + 9.2; // 위로 끌기, 02 끝
const C3 = X2 + 0.5, s3 = C3 + 1.05;                   // 03 카드, 03 시작(곡이 새 구간으로 넘어가는 즈음)
const g3 = s3 + 6.1;                                   // 03 위치 카드(대화 세 개를 읽은 뒤)
const th3 = g3 + 4.4;                                  // 두 기록이 휴대폰으로 엮이는 실(가족 단체방 강조 뒤)
const pTapW = th3 + 2.65, pTapI = pTapW + 3.0, pTapS = pTapI + 1.8;    // Weave 버튼 · 입력하기(추천 문장을 읽을 시간) · 전송
const tRead = pTapS + 1.05, tReply = pTapS + 2.1;     // 읽음(1이 사라짐) → 답장
const LOGO_MIN = tReply + 1.95;                        // 답장을 읽을 시간
const LOGO = D1 + Math.ceil((LOGO_MIN - D1) / BAR - 1e-6) * BAR;   // 로고는 곡의 마디 첫 박에(마지막 한 방)
const DUR = LOGO + 5.0;                                // 끝 화면 5초

const tl = gsap.timeline({ paused: true, defaults: { ease: 'power3.out', duration: 1.0 } });
const EV = [];
const ev = (t, type, o = {}) => EV.push({ t: Math.round(t * 1000) / 1000, type, ...o });
let seed = 20261029;
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const DEBUG = /debug/.test(location.search);
const svgNS = 'http://www.w3.org/2000/svg';
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, u) => a + (b - a) * u;

const hand = $('#hand'), spark = $('#spark'), sparks = $$('#spark .sp');
const TIP = { x: 39, y: 8 };
const rectOf = s => (typeof s === 'string' ? $(s) : s).getBoundingClientRect();
const ctr = s => { const r = rectOf(s); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; };

const PH = '<span style="color:#9a96a6; font-weight:400">메시지 입력</span>';
const QA = '지은이네 집들이 때 먹었던 와인', ANS = '배비치 소비뇽 블랑';
const cont = [];                                       // 매 프레임 tl.seek 뒤에 부르는 함수들
const seekAll = t => { tl.seek(t, false); for (const f of cont) f(t); };
const when = (test, fn) => { let last; cont.push(t => { const v = test(t); if (v !== last) { last = v; fn(v); } }); };

/* ── 글자: 원소마다 [시작 시각, 내용] 목록. 내용은 글자, {html}, 또는 타자 {type, cps} ── */
const texts = new Map();
function textAt(el, t0, v) {
  if (!texts.has(el)) {
    const segs = []; texts.set(el, segs);
    const init = el.innerHTML;
    let last;
    cont.push(t => {
      let s = null; for (const g of segs) if (g.t0 <= t + 1e-9) s = g;
      let html;
      if (!s) html = init;
      else if (s.type) { let n = 0; while (n < s.times.length && s.times[n] <= t + 1e-9) n++; html = esc(s.type.slice(0, n).join('')); }
      else html = s.html != null ? s.html : esc(s.text);
      if (html !== last) { el.innerHTML = html; last = html; }
    });
  }
  texts.get(el).push({ t0, ...v });
  texts.get(el).sort((a, b) => a.t0 - b.t0);
}
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
function typeIn(el, text, t0, cps = 12, sfx = 'key') {
  const ch = [...text], times = [];
  let t = t0;
  for (const c of ch) { times.push(t); t += (1 / cps) * (0.75 + rnd() * 0.5) * (c === ' ' ? 0.6 : 1); }
  textAt(el, t0, { type: ch, times });
  if (sfx) times.forEach((tt, i) => ch[i] !== ' ' && ev(tt, sfx));
  return t;
}
const STAR = '<svg viewBox="0 0 24 24"><path d="M12 1.5C12.9 8.6 15.4 11.1 22.5 12 15.4 12.9 12.9 15.4 12 22.5 11.1 15.4 8.6 12.9 1.5 12 8.6 11.1 11.1 8.6 12 1.5Z" fill="currentColor"/></svg>';

function makeKB(sel, action) {
  const KB = [['ㅂ','ㅈ','ㄷ','ㄱ','ㅅ','ㅛ','ㅕ','ㅑ','ㅐ','ㅔ'], ['ㅁ','ㄴ','ㅇ','ㄹ','ㅎ','ㅗ','ㅓ','ㅏ','ㅣ'], ['⇧','ㅋ','ㅌ','ㅊ','ㅍ','ㅠ','ㅜ','ㅡ','⌫'], ['!#1','한/영','한국어','.','↗']];
  $(sel).innerHTML = `<div class="wvfx under"><i class="glow"></i><i class="rg"></i><i class="rg"></i><i class="rg"></i></div>` +
    `<div class="tb"><i class="clip"><i class="shim"></i></i><span class="wv"><img src="assets/icons/weave-spool-6B4EFF.png" alt=""><img class="lit" src="assets/icons/weave-spool-white.png" alt=""></span><svg><use href="#i-emo"/></svg><svg><use href="#i-tr"/></svg><svg><use href="#i-clip"/></svg><svg><use href="#i-gear"/></svg><span style="margin-left:auto">닫기 ⌄</span></div>` +
    KB.map(row => `<div class="krow">${row.map(k => {
      const cls = ['k'];
      if (['⇧', '⌫', '!#1', '한/영'].includes(k)) cls.push('g', 'w2');
      if (k === '한국어') cls.push('sp');
      if (k === '↗') cls.push('snd', 'w2', ...(action === 'search' ? ['srch'] : []));
      const icon = action === 'search' ? '<svg width="20" height="20" style="color:#fff"><use href="#i-search"/></svg>' : '<svg width="18" height="18"><use href="#i-plane"/></svg>';
      return `<span class="${cls.join(' ')}">${k === '↗' ? icon : k}</span>`;
    }).join('')}</div>`).join('') +
    `<div class="wvfx over"><i class="badge">1</i>${[0, 1, 2, 3].map(() => `<i class="st">${STAR}</i>`).join('')}</div>`;
}

/* ── 손으로 누르기 ─────────────────────────────── */
function handIn(x, y, t, d = 0.75) {
  tl.set(hand, { x: x - TIP.x + 190, y: y - TIP.y + 250, rotation: -12, scale: 1, autoAlpha: 0 }, t - d);
  tl.to(hand, { x: x - TIP.x, y: y - TIP.y, autoAlpha: 1, duration: d, ease: 'power3.out' }, t - d);
}
function handOut(t) { tl.to(hand, { x: '+=190', y: '+=250', autoAlpha: 0, duration: 0.6, ease: 'power2.in' }, t); }
function sparkAt(x, y, t) {
  tl.set(spark, { x, y, autoAlpha: 1 }, t)
    .fromTo(sparks, { drawSVG: '0% 0%', opacity: 1 }, { drawSVG: '0% 100%', duration: 0.22, ease: 'power2.out', immediateRender: false }, t)
    .to(sparks, { drawSVG: '100% 100%', duration: 0.3, ease: 'power2.in' }, t + 0.24)
    .set(spark, { autoAlpha: 0 }, t + 0.56);
}
function press(x, y, t, target) {
  tl.to(hand, { scale: 0.9, duration: 0.09, ease: 'power2.out' }, t - 0.06)
    .to(hand, { scale: 1, duration: 0.26, ease: 'power2.out' }, t + 0.06);
  sparkAt(x, y, t);
  if (target) tl.to(target, { scale: 0.95, duration: 0.09, yoyo: true, repeat: 1, ease: 'power1.inOut' }, t - 0.04);
  ev(t, 'tap');
}
const mark = (sel, t, d = 0.5, color = '#5B3FE6') => {                                  // 형광펜 긋기 + 글자를 보라색으로
  tl.to(sel, { backgroundSize: '100% 100%', duration: d, ease: 'power2.inOut', stagger: 0.12 }, t);
  if (color) tl.to(sel, { color, duration: 0.35, stagger: 0.12 }, t);
};

/* ── 카메라 ─────────────────────────────────────────
   휴대폰: 기본 자리의 중심은 화면 중심(960, 540). 기본 배치에서 잰 점 f를 배율 s로 화면의 점 T에 놓는다.
   01 사슬(#w1): 왼쪽 위 기준. 사슬 좌표의 점 f를 배율 s로 화면의 점 T에 놓는다. */
const PC = { x: 960, y: 540 };
const camPose = (s, f, T) => ({ x: T.x - PC.x - s * (f.x - PC.x), y: T.y - PC.y - s * (f.y - PC.y), scale: s });
function cam(t, pose, d = 1.0, ease = 'power3.inOut') { tl.to('#phone', { ...pose, duration: d, ease }, t); }
const wPose = (s, f, T) => ({ x: T.x - s * f.x, y: T.y - s * f.y, scale: s });
function wcam(t, pose, d = 0.9, ease = 'power3.inOut') { tl.to('#w1', { ...pose, duration: d, ease }, t); }
const edge = t => tl.fromTo('#phone .frame', { boxShadow: '0 60px 110px rgba(52,30,130,.26), 0 18px 34px rgba(52,30,130,.14), 0 0 0 0 rgba(139,104,245,0)' },
  { boxShadow: '0 60px 110px rgba(52,30,130,.26), 0 18px 34px rgba(52,30,130,.14), 0 0 52px 8px rgba(139,104,245,.55)', duration: 0.45, yoyo: true, repeat: 1, repeatDelay: 0.35, ease: 'power2.out', immediateRender: false }, t);

/* ── 연결선: 모두 같은 모양(보라 그라데이션 곡선 + 흰 테두리), 동그라미 없음 ── */
function curve(id, d, t, dur = 0.55, w = 5.5) {
  const g = document.createElementNS(svgNS, 'g'); g.id = id;
  g.innerHTML = `<path class="thr-halo" d="${d}" style="stroke-width:${w + 6}"/><path class="thr" d="${d}" style="stroke-width:${w}"/>`;
  $('#uxThreads').appendChild(g);
  gsap.set(`#${id} path`, { drawSVG: '0% 0%' });
  tl.to(`#${id} path`, { drawSVG: '0% 100%', duration: dur, ease: 'power2.inOut' }, t);
  return `#${id}`;
}
const bez = (a, b, bend = 0.5) => { const dx = b.x - a.x; return `M${a.x} ${a.y} C ${a.x + dx * bend} ${a.y}, ${b.x - dx * bend} ${b.y}, ${b.x} ${b.y}`; };
// 같은 단서가 다음 기록으로 건너간다: 작은 보라 표(토큰)가 a에서 b로 둥글게 날아감
function hop(sel, a, b, t, d = 0.7, lift = 70) {
  const mid = { x: (a.x + b.x) / 2, y: Math.min(a.y, b.y) - lift };
  gsap.set(sel, { x: a.x, y: a.y, xPercent: -50, yPercent: -50, autoAlpha: 0, scale: 0.6 });
  tl.to(sel, { autoAlpha: 1, scale: 1, duration: 0.25, ease: 'back.out(2)' }, t);
  tl.to(sel, { motionPath: { path: [a, mid, b], curviness: 1.25 }, duration: d, ease: 'power2.inOut' }, t + 0.2);
  tl.to(sel, { autoAlpha: 0, scale: 0.7, duration: 0.2, ease: 'power2.in' }, t + 0.2 + d);
}

/* ── 챕터 카드 · 헤드라인 ─────────────────────────── */
const chapIn = (id, t) => { tl.set(id, { autoAlpha: 1 }, t); tl.fromTo(`${id} > *`, { y: 44, opacity: 0 }, { y: 0, opacity: 1, duration: 0.85, stagger: 0.11, ease: 'expo.out', immediateRender: false }, t); };
const chapOut = (id, t) => { tl.to(`${id} > *`, { y: -26, opacity: 0, duration: 0.35, stagger: 0.04, ease: 'power2.in' }, t); tl.set(id, { autoAlpha: 0 }, t + 0.45); };
const headIn = (id, t) => { tl.set(id, { autoAlpha: 1 }, t); tl.fromTo(`${id} > *`, { y: 26, opacity: 0 }, { y: 0, opacity: 1, duration: 0.9, stagger: 0.1, ease: 'expo.out', immediateRender: false }, t); };
const headOut = (id, t) => { tl.to(`${id} > *`, { y: -16, opacity: 0, duration: 0.45, ease: 'power2.in' }, t); tl.set(id, { autoAlpha: 0 }, t + 0.5); };

async function build() {
  const fams = ['400 20px SamsungOneKorean', '500 20px SamsungOneKorean', '700 20px SamsungOneKorean', '400 20px SamsungOne', '500 20px SamsungOne', '700 20px SamsungOne', '700 20px "Samsung Sharp Sans"'];
  await Promise.all(fams.map(f => document.fonts.load(f, '가A')));
  await document.fonts.ready;
  makeKB('#kbA', 'search'); makeKB('#kbC', 'send');
  $('#sqA').textContent = ''; $('#kinTx').innerHTML = PH;
  await Promise.all([...document.images].map(im => im.decode().catch(() => {})));

  /* ── 기본 배치에서 잰 자리(휴대폰 그대로, 화면 셋이 겹친 상태, 사슬은 확대 전) ── */
  const resultState = on => {
    $('#glogo').style.display = on ? 'none' : ''; $('.gtop').style.display = on ? 'none' : '';
    $('#gbox').style.top = on ? '104px' : ''; $('#gres').style.display = on ? '' : 'none';
    $('#kbA').style.display = on ? 'none' : ''; $('#caretA').style.display = on ? 'none' : '';
  };
  const B = {};
  for (const k of ['#kbA .wv', '#kbA .srch', '#gbox', '#handle', '#qB', '#sgC', '#btnC', '#chatIn', '.kin', '#kbC .wv', '#kbC .tb']) B[k] = ctr(k);
  resultState(true); B.gboxR = ctr('#gbox'); B.r1 = ctr('#r1'); B.r3 = ctr('#r3'); resultState(false);
  { $('#sqA').textContent = ANS; const g = rectOf('#gbox'), q = rectOf('#sqA'); $('#sqA').textContent = '';   // 검색창 밑줄은 바뀐 검색어 길이만큼
    Object.assign($('#gsweep').style, { left: `${q.left - g.left}px`, right: 'auto', width: `${q.width + 2}px` }); }
  const wBtop = rectOf('#wB').top, lift = B['#handle'].y - wBtop - 14;
  // Weave 버튼 효과 두 겹을 버튼 한가운데에(키보드 기준)
  { const kb = rectOf('#kbC'), wv = B['#kbC .wv']; $$('#kbC .wvfx').forEach(e => { e.style.left = `${wv.x - kb.left}px`; e.style.top = `${wv.y - kb.top}px`; }); }
  // 03 대화: 메시지가 하나씩 도착(높이 0 → 원래 높이). 단계 n(도착한 메시지 수)마다 말풍선 자리를 미리 잰다
  const MSG = ['#m2', '#m3', '#mSent', '#mReply'];
  const natH = {}; MSG.forEach(k => natH[k] = rectOf(k).height);
  const stage = n => MSG.forEach((k, i) => gsap.set(k, { height: i < n ? natH[k] : 0, marginTop: i < n ? 10 : 0, overflow: 'hidden' }));
  const MS = [];
  for (let n = 0; n <= 4; n++) { stage(n); MS[n] = {}; for (const k of ['#m1', ...MSG]) MS[n][k] = ctr(`${k} .bub`); MS[n].kin = ctr('.kin'); }
  stage(0);
  const FLR = {}; for (const k of ['#fl1', '#fl2', '#fl3', '#fg', '#fk']) FLR[k] = rectOf(k);
  const DT = { a: ctr('#dtA'), b: ctr('#dtB'), g: ctr('#gpsDj'), k: ctr('#kkDj') };   // 같은 단서(날짜·대전)의 자리
  gsap.set('.chap', { autoAlpha: 0 });
  gsap.set('.head', { autoAlpha: 0 });
  gsap.set(['#fl1', '#fl2', '#fl3', '#fg', '#fk', '#frec', '#flChip', '#flLink', '#callQ', '#callT', '#callA', '#flyChip', '#topScrim', '#gai', '#tokA', '#tokC'], { autoAlpha: 0 });

  /* ── 도입 (0 – 11.2초): "그때 그 와인, 다시 사고 싶은데 / 이름이 뭐였더라?" → 카톡·사진·캘린더·노트 ──
     조각은 처음부터 흐리게 떠 있다가, 자막이 나올 때 그 앱 조각만 밝아진다(매 프레임 계산). */
  const FR = [
    ['app-kakao', '지은', '다들 와줘서 고마워 ㅎㅎ', 'k', -700, 0], ['samsung-gallery', 'IMG_2481.jpg', '3월 15일 20:14', 'g', -235, 0, 1],
    ['samsung-calendar', '지은 집들이', '3월 15일 (일) 18:00', 'c', 235, 0], ['app-notes', '와인 메모', '달지 않은 화이트?', 'n', 700, 0],
    ['samsung-email-blue', '[예약 확인] 오사카 호텔', '2월 27일', 'm', -480, 1], ['app-kakao', '민호', '그 와인 맛있더라', 'k', 20, 1],
    ['samsung-gallery', 'IMG_2475.jpg', '3월 15일 19:52', 'g', 500, 1, 1], ['samsung-calendar', '팀 회식', '3월 20일 19:00', 'c', -720, 2],
    ['app-kakao', '가족 단체방', '성심당 무화과시루 먹고 싶다', 'k', -250, 2], ['app-notes', '장보기', '우유, 계란, 무화과', 'n', 240, 2],
    ['samsung-gallery', '스크린샷', '3월 18일 13:02', 'g', 720, 2], ['samsung-calendar', '치과 예약', '3월 22일 10:30', 'c', -470, 3],
    ['app-notes', '회의록 3/14', '다음 주 시연 리허설', 'n', 20, 3], ['samsung-email-blue', 'Q1_Demo_v3.pdf', '어제 오후 6:20', 'm', 470, 3],
  ];
  const ROWY = [-138, 4, 146, 288];                    // #cam(화면 y 450) 기준 줄 높이
  const cam3 = $('#cam'), frags = [];
  FR.forEach((f, i) => {
    const d = document.createElement('div');
    d.className = 'frag kr';
    d.innerHTML = `<i class="ring"></i><img class="ic" src="assets/icons/${f[0]}.png" alt="">${f[6] ? '<img class="ph" src="assets/img/ux2-wine-photo.png" alt="">' : ''}<div><div class="t">${f[1]}</div><div class="m">${f[2]}</div></div>`;
    cam3.appendChild(d);
    const row = f[5];
    frags.push({ d, ring: d.querySelector('.ring'), kind: f[3], row,
      x: f[4] * 1.02 + (rnd() - 0.5) * 40, y: ROWY[row] + (rnd() - 0.5) * 16, z: (rnd() - 0.5) * 120,
      t0: (row < 2 ? 3.55 : 3.3) + (i % 4) * 0.07 + rnd() * 0.18 });
  });
  await Promise.all($$('#cam img').map(im => im.decode().catch(() => {})));
  const hookW = $$('#hook .w');
  gsap.set(hookW, { y: 60, opacity: 0, filter: 'blur(12px)' });
  tl.to(hookW.slice(0, 6), { y: 0, opacity: 1, filter: 'blur(0px)', duration: 1.1, stagger: 0.12, ease: 'expo.out' }, 0.3);
  tl.to(hookW.slice(6), { y: 0, opacity: 1, filter: 'blur(0px)', duration: 1.1, stagger: 0.15, ease: 'expo.out' }, 1.35);
  tl.to('#hook', { y: -338, scale: 0.6, duration: 1.0, ease: 'expo.inOut' }, 2.65);
  frags.forEach(f => gsap.set(f.d, { x: f.x, y: f.y, z: f.z - 500, opacity: 0, xPercent: -50, yPercent: -50 }));
  gsap.set(cam3, { rotationY: 5, rotationX: 3, z: -60 });
  tl.to(cam3, { rotationY: -3, rotationX: -1, z: 30, duration: 8.4, ease: 'sine.inOut' }, 2.7);
  const CL = ['#c1', '#c2', '#c3', '#c4'], CL_K = ['k', 'g', 'c', 'n'], CL_T = [4.45, 6.0, 7.55, 9.1];
  gsap.set(CL, { y: 30, opacity: 0 });
  CL.forEach((c, i) => {
    tl.to(c, { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, CL_T[i]);
    if (i > 0) tl.to(CL[i - 1], { color: '#A29DB2', duration: 0.5 }, CL_T[i]).to(`${CL[i - 1]} b`, { color: '#B9A8F3', duration: 0.5 }, CL_T[i]);
  });
  const E_IN = gsap.parseEase('expo.out'), E_HL = gsap.parseEase('power2.out');
  const HS = { on: [1, 1.07, 1], off: [0.28, 0.97, 0] };   // [밝기, 크기, 테두리] — 첫 자막 전에도 흐린 상태
  const hlOf = (f, i) => (i >= 0 && f.kind === CL_K[i]) ? HS.on : HS.off;
  cont.push(t => {
    let i = -1; for (let k = 0; k < CL_T.length; k++) if (t >= CL_T[k]) i = k;
    const u = i < 0 ? 1 : E_HL(clamp((t - CL_T[i]) / 0.45));
    for (const f of frags) {
      const a = clamp((t - f.t0) / 1.8), op = clamp((t - f.t0) / 0.55);
      const A = hlOf(f, i - 1), Bs = hlOf(f, i);
      const o = lerp(A[0], Bs[0], u), s = lerp(A[1], Bs[1], u), r = lerp(A[2], Bs[2], u);
      gsap.set(f.d, { z: f.z - 500 * (1 - E_IN(a)), opacity: op * o, scale: s });
      f.ring.style.opacity = String(op * r);
    }
  });
  tl.to(['#hook', '#where'], { opacity: 0, y: '-=24', filter: 'blur(8px)', duration: 0.6, ease: 'power2.in' }, 10.65);
  tl.to('#space', { opacity: 0, scale: 1.08, filter: 'blur(14px)', duration: 0.65, ease: 'power2.in' }, 10.6);

  /* ── 01 단서로 찾기 ── */
  chapIn('#ch1', C1); chapOut('#ch1', C1 + 1.15);
  const phone = $('#phone');
  gsap.set(phone, { autoAlpha: 0, x: 0, y: 160, scale: 0.92, transformOrigin: '50% 50%' });
  gsap.set(['#scrB', '#scrC'], { xPercent: 100 });
  gsap.set('#gres', { display: 'none' });
  tl.to(phone, { autoAlpha: 1, y: 0, scale: 1, duration: 1.1, ease: 'power3.out' }, P0);
  tl.fromTo('#caretA', { opacity: 1 }, { opacity: 0, duration: 0.01, repeat: 9, yoyo: true, repeatDelay: 0.3, ease: 'none' }, P0 + 0.4);
  cam(P0 + 0.7, camPose(2.3, B['#gbox'], { x: 960, y: 430 }), 0.9);                          // 검색할 때는 검색창을 크게
  typeIn($('#sqA'), QA, P0 + 1.5, 12);
  cam(P0 + 3.3, camPose(2.3, { x: B['#kbA .wv'].x + 90, y: B['#kbA .wv'].y }, { x: 960, y: 600 }), 0.85);   // Weave를 누를 때는 Weave 아이콘 쪽
  const pTap1 = P0 + 4.4;
  edge(pTap1 + 0.05);
  tl.fromTo('#kbA .wv', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)' }, { boxShadow: '0 0 0 14px rgba(107,78,255,0)', duration: 0.6, ease: 'power2.out', immediateRender: false }, pTap1 + 0.05);
  tl.to(phone, { y: '+=2300', duration: 0.55, ease: 'power2.in' }, pTap1 + 0.25);       // 휴대폰은 아래로 빠지고, 물음은 위로
  tl.set(phone, { autoAlpha: 0 }, pTap1 + 0.85);

  // 사슬: 단계마다 카메라가 그 자리로 가서 확대하고, 같은 단서가 다음 기록으로 건너가는 걸 보여 준다
  gsap.set('#w1', { transformOrigin: '0 0', x: 0, y: 0, scale: 1 });
  gsap.set(['#cA', '#cB', '#cC'], { autoAlpha: 0, scale: 0.9, y: 26 });
  gsap.set(['#tA .thr', '#tA .thr-halo', '#tB .thr', '#tB .thr-halo', '#tC .thr', '#tC .thr-halo'], { drawSVG: '0% 0%' });
  gsap.set('.pen', { autoAlpha: 0, y: 12 });
  gsap.set('#scan', { y: -80, opacity: 0 });
  gsap.set('#ocrbox', { opacity: 0, scale: 1.25 });
  gsap.set('#pill', { autoAlpha: 0 });
  const draw = (g, t, d) => tl.to(`${g} .thr, ${g} .thr-halo`, { drawSVG: '0% 100%', duration: d, ease: 'power2.inOut' }, t);
  const penIn = (id, t) => tl.to(id, { autoAlpha: 1, y: 0, duration: 0.6, ease: 'back.out(2)' }, t);
  const cardIn = (id, t) => tl.to(id, { autoAlpha: 1, scale: 1, y: 0, duration: 0.9, ease: 'back.out(1.3)' }, t);
  tl.to('#topScrim', { autoAlpha: 1, duration: 0.5 }, pTap1 + 0.75); headIn('#h1', pTap1 + 0.75);
  wcam(P0 + 5.6, wPose(1.45, { x: 330, y: 470 }, { x: 720, y: 600 }), 1.0);                 // 언제였지? → 캘린더
  draw('#tA', P0 + 5.85, 0.7); penIn('#pen1', P0 + 5.95); cardIn('#cA', P0 + 6.4);
  mark('#dtA', P0 + 7.2);                                                                     // 그날 날짜에 형광펜
  wcam(P0 + 8.0, wPose(1.2, { x: 640, y: 560 }, { x: 960, y: 600 }), 0.9);                  // 그날 찍은 사진엔? → 캘린더와 사진을 한 화면에
  draw('#tB', P0 + 8.2, 0.6); penIn('#pen2', P0 + 8.25); cardIn('#cB', P0 + 8.65);
  hop('#tokA', DT.a, DT.b, P0 + 9.45, 0.65);                                                 // 같은 날짜(3월 15일)가 사진 카드로 건너감
  mark('#dtB', P0 + 10.3);                                                                    // 표가 도착하는 순간
  wcam(P0 + 11.0, wPose(1.6, { x: 930, y: 700 }, { x: 960, y: 610 }), 0.85);                // 사진 속 라벨 글자 읽기
  tl.to('#scan', { opacity: 1, duration: 0.1 }, P0 + 11.2).to('#scan', { y: 240, duration: 0.65, ease: 'power1.inOut' }, P0 + 11.2).to('#scan', { opacity: 0, duration: 0.2 }, P0 + 11.75);
  tl.to('#ocrbox', { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(2)' }, P0 + 11.65);
  typeIn($('#ocr'), 'BABICH SAUVIGNON BLANC', P0 + 11.75, 40, null);
  tl.fromTo('#ocr', { boxShadow: '0 0 0 0 rgba(123,75,216,0)' }, { boxShadow: '0 0 0 3px rgba(123,75,216,.7)', duration: 0.35, ease: 'power2.out', immediateRender: false }, P0 + 12.4);
  wcam(P0 + 13.2, { x: 0, y: 0, scale: 1 }, 0.95);                                            // 한눈에: 라벨엔 뭐라고? → 답
  penIn('#pen3', P0 + 13.5);
  draw('#tC', P0 + 13.75, 0.6); cardIn('#cC', P0 + 14.2); ev(P0 + 14.25, 'answer');
  tl.fromTo('#cC', { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 0 rgba(166,124,242,.55)' },
    { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 28px rgba(166,124,242,0)', duration: 1.1, ease: 'power2.out', immediateRender: false }, P0 + 14.3);
  wcam(P0 + 15.6, wPose(1.35, { x: 1560, y: 745 }, { x: 1180, y: 720 }), 0.8);              // 답 카드 · 입력하기
  // 입력하기 → 답이 검색창으로 들어가 글자가 바뀜 → 검색 키 → 결과의 이름 부분에 표시
  tl.to(['#w1'], { autoAlpha: 0, filter: 'blur(8px)', duration: 0.5, ease: 'power2.in' }, T2 + 0.2);
  tl.to(['#topScrim'], { autoAlpha: 0, duration: 0.45 }, T2 + 0.15); headOut('#h1', T2 + 0.1);
  const boxPose = camPose(2.0, B['#gbox'], { x: 960, y: 400 });
  tl.set(phone, { ...boxPose, y: boxPose.y + 1150, rotation: 0, autoAlpha: 1 }, T2 + 0.1);
  tl.to(phone, { y: boxPose.y, duration: 0.85, ease: 'power3.out' }, T2 + 0.15);
  textAt($('#sqA'), T2 + 0.75, { html: `<span class="sel">${QA}</span>` });
  textAt($('#sqA'), T2 + 1.15, { text: ANS });
  tl.fromTo('#gsweep', { scaleX: 0, opacity: 1 }, { scaleX: 1, duration: 0.45, ease: 'power2.out', immediateRender: false }, T2 + 1.15).to('#gsweep', { opacity: 0, duration: 0.3 }, T2 + 1.85);
  const both = camPose(1.3, { x: (B['#gbox'].x + B['#kbA .srch'].x) / 2, y: (B['#gbox'].y + B['#kbA .srch'].y) / 2 }, { x: 960, y: 560 });
  cam(T2 + 1.9, both, 0.75);                                                                  // 바뀐 검색어와 검색 키를 한 화면에
  const pTap3 = T2 + 3.0;
  tl.fromTo('#kbA .srch', { boxShadow: '0 0 0 0 rgba(47,107,255,.55)' }, { boxShadow: '0 0 0 12px rgba(47,107,255,0)', duration: 0.6, ease: 'power2.out', immediateRender: false }, T2 + 2.4);
  tl.fromTo('#gload', { scaleX: 0, opacity: 1 }, { scaleX: 1, duration: 0.4, ease: 'power1.inOut', immediateRender: false }, pTap3 + 0.07).to('#gload', { opacity: 0, duration: 0.15 }, pTap3 + 0.47);
  when(t => t >= pTap3 + 0.15, on => resultState(on));
  tl.fromTo(['#gres .gchips', '#gres .res'], { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.07, ease: 'expo.out', immediateRender: false }, pTap3 + 0.15);
  cam(pTap3 + 0.15, camPose(1.5, { x: B.gboxR.x, y: (B.r1.y + B.r3.y) / 2 }, { x: 960, y: 560 }), 0.9);   // 결과 목록을 크게
  cam(pTap3 + 1.1, camPose(1.95, { x: B.r1.x, y: B.r1.y + 40 }, { x: 960, y: 520 }), 0.8);     // 첫 결과를 크게
  mark('#gres mark.rm', pTap3 + 1.5, 0.4);                                                    // 결과 속 '배비치 … 소비뇽 블랑'에 표시
  tl.fromTo('#r1', { boxShadow: '0 0 0 0 rgba(123,75,216,0)' }, { boxShadow: '0 0 0 2.5px rgba(123,75,216,.8)', duration: 0.4, ease: 'power2.out', immediateRender: false }, pTap3 + 1.5);

  /* ── 02 한 번에 모아 보기: 휴대폰 오른쪽. 통화 중 요청 → 위로 올려 검색 → 기록(형광펜) → 답변 ── */
  tl.to(phone, { x: '-=420', autoAlpha: 0, filter: 'blur(6px)', duration: 0.45, ease: 'power3.in' }, X1);
  chapIn('#ch2', C2); chapOut('#ch2', C2 + 1.0);
  tl.set('#scrA', { xPercent: -100 }, C2 + 0.15); tl.set('#scrB', { xPercent: 0 }, C2 + 0.15);
  const R2 = { x: 560, y: 0, scale: 1 };
  tl.set(phone, { x: 1400, y: 0, scale: 1, rotation: 0, filter: 'blur(0px)', autoAlpha: 1 }, s2 - 0.1);
  tl.to(phone, { x: R2.x, duration: 1.05, ease: 'power3.out' }, s2);
  headIn('#hdB', s2 + 0.3);
  cont.push(t => { $('#ctime').textContent = `00:${String(48 + Math.floor(clamp((t - s2) / 1.0, 0, 11))).padStart(2, '0')}`; });
  tl.fromTo('#callQ', { autoAlpha: 0, x: -24, scale: 0.96, transformOrigin: '100% 60%' }, { autoAlpha: 1, x: 0, scale: 1, duration: 0.75, ease: 'back.out(1.4)', immediateRender: false }, s2 + 0.8);
  $$('#callQ .eq i').forEach((b, i) => {
    const d = 0.13 + 0.04 * ((i * 7) % 5);
    tl.fromTo(b, { scaleY: 0.25 }, { scaleY: 1, duration: d, repeat: Math.floor(3.0 / d), yoyo: true, ease: 'sine.inOut', immediateRender: false }, s2 + 0.85 + i * 0.03);
  });
  mark('#callQ .qk', s2 + 1.8, 0.45);                                                         // 물어보는 것: A사 시연 순서 · 오늘 집합 시간
  tl.fromTo('#callT', { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.7, ease: 'expo.out', immediateRender: false }, s2 + 2.5);
  const hPose = camPose(1.35, B['#handle'], { x: 1605, y: 880 });
  const qPose = camPose(2.0, B['#qB'], { x: 1330, y: 610 });
  cam(s2 + 3.4, hPose, 0.8);                                                                  // 아래 손잡이 쪽을 크게
  gsap.set('#chevB svg', { opacity: 0 });
  tl.fromTo('#chevB svg', { y: 8, opacity: 0 }, { y: -8, opacity: 1, duration: 0.42, stagger: 0.1, repeat: 1, repeatDelay: 0.08, ease: 'power1.out', immediateRender: false }, s2 + 3.55);
  tl.to('#chevB svg', { opacity: 0, duration: 0.15 }, dragT);
  tl.fromTo('#scrB .hlab', { scale: 1 }, { scale: 1.12, duration: 0.3, yoyo: true, repeat: 1, ease: 'power1.inOut', immediateRender: false }, s2 + 3.65);
  tl.fromTo('#handle', { y: 0, boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { y: -7, boxShadow: '0 0 12px 3px rgba(107,78,255,.55)', duration: 0.22, yoyo: true, repeat: 3, ease: 'sine.inOut', immediateRender: false }, s2 + 3.6);
  tl.to('#callT', { autoAlpha: 0, y: -10, duration: 0.4, ease: 'power2.in' }, dragT);
  gsap.set('#wB', { y: lift + 14, autoAlpha: 0 });
  tl.set('#wB', { autoAlpha: 1 }, dragT);
  tl.to('#wB', { y: 0, duration: dragD, ease: 'power2.inOut' }, dragT);
  when(t => t >= dragT && t < dragT + dragD + 0.25, on => $('#wB').classList.toggle('drag', on));
  cam(dragT, qPose, dragD, 'power2.inOut');                                                   // 카메라가 손을 따라 올라가 검색창으로
  edge(dragT + 0.3);
  typeIn($('#qB'), '어제 A사 시연 준비', dragT + 1.2, 12);
  cam(dragT + 2.5, R2, 0.8);
  gsap.set(['#b1', '#b2', '#b3'], { opacity: 0, y: 14 });
  tl.to(['#b1', '#b2', '#b3'], { opacity: 1, y: 0, duration: 0.55, stagger: 0.12, ease: 'expo.out' }, dragT + 2.7);
  const TB = { thread: dragT + 3.3, pop: dragT + 3.5 };
  ['#fl1', '#fl2', '#fl3'].forEach((k, i) => {
    gsap.set(k, { autoAlpha: 0, scale: 0.92, x: 40 });
    tl.to(k, { autoAlpha: 1, scale: 1, x: 0, duration: 0.8, ease: 'back.out(1.4)' }, TB.pop + i * 0.08);
  });
  const L1 = ['#fl1', '#fl2', '#fl3'].map(k => ({ x: FLR[k].left + 2, y: FLR[k].top + FLR[k].height / 2 }));
  const xb = L1[0].x - 70;
  curve('flc', `M${L1[0].x} ${L1[0].y} C ${xb} ${L1[0].y}, ${xb} ${L1[1].y}, ${L1[1].x} ${L1[1].y} C ${xb} ${L1[1].y}, ${xb} ${L1[2].y}, ${L1[2].x} ${L1[2].y}`, dragT + 4.4, 0.7, 5.5);
  gsap.set('#flChip', { left: FLR['#fl1'].left, top: FLR['#fl1'].top - 52, x: 0, scale: 0.85 });
  tl.to('#flChip', { autoAlpha: 1, scale: 1, duration: 0.6, ease: 'back.out(2)' }, dragT + 4.6);
  mark('#mk1', dragT + 4.95); mark('#mk2', dragT + 5.3); mark('#mk3', dragT + 5.65);       // 물어본 답(시연 순서·5분·집합 시간)에 형광펜
  tl.fromTo('#callA', { autoAlpha: 0, x: -20, scale: 0.96, transformOrigin: '100% 50%' }, { autoAlpha: 1, x: 0, scale: 1, duration: 0.7, ease: 'back.out(1.4)', immediateRender: false }, dragT + 6.5);
  mark('#ua1', dragT + 7.1, 0.45); mark('#ua2', dragT + 7.4, 0.35); mark('#ua3', dragT + 7.7, 0.4);   // 형광펜 친 기록 그대로 답한다

  /* ── 03 먼저 건네기: 휴대폰 왼쪽, 문장·플로팅 오른쪽 ── */
  tl.to(['#fl1', '#fl2', '#fl3', '#flChip', '#flc', '#callQ', '#callA'], { autoAlpha: 0, x: -30, duration: 0.45, ease: 'power2.in', stagger: 0.03 }, X2);
  headOut('#hdB', X2);
  tl.to(phone, { x: '+=420', autoAlpha: 0, filter: 'blur(6px)', duration: 0.45, ease: 'power3.in' }, X2 + 0.05);
  chapIn('#ch3', C3); chapOut('#ch3', C3 + 1.0);
  tl.set('#scrB', { xPercent: -100 }, C3 + 0.3); tl.set('#scrC', { xPercent: 0 }, C3 + 0.3);
  when(t => t >= C3 + 0.3, on => { $('#sbt').textContent = on ? '22:44' : '13:00'; });
  const R3 = { x: -430, y: 0, scale: 1 };
  tl.set(phone, { x: -1500, y: 0, scale: 1, rotation: 0, filter: 'blur(0px)', autoAlpha: 1 }, s3 - 0.1);
  tl.to(phone, { x: R3.x, duration: 1.0, ease: 'power3.out' }, s3);
  headIn('#hdC', s3 + 0.3);
  // 대화: 엄마 → 나 → 엄마. 첫 세 메시지는 카메라를 옮기지 않고 확대만
  const chatPose = camPose(1.75, { x: 960, y: MS[2]['#m2'].y + 10 }, { x: 500, y: 560 });
  const reveal = (k, t) => {
    tl.to(k, { height: natH[k], marginTop: 10, duration: 0.38, ease: 'power2.out' }, t);
    tl.fromTo(`${k} .bub`, { scale: 0.7, opacity: 0, transformOrigin: $(k).classList.contains('me') ? '100% 100%' : '0% 0%' },
      { scale: 1, opacity: 1, duration: 0.45, ease: 'back.out(1.6)', immediateRender: false }, t + 0.05);
  };
  gsap.set(['#m2 .bub', '#m3 .bub', '#mSent .bub', '#mReply .bub'], { opacity: 0 });
  cam(s3 + 0.6, chatPose, 0.9);
  tl.fromTo('#m1 .bub', { boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { boxShadow: '0 0 0 3px rgba(107,78,255,.45)', duration: 0.35, yoyo: true, repeat: 1, repeatDelay: 0.4, immediateRender: false }, s3 + 1.45);
  reveal('#m2', s3 + 2.6);                                                                    // 말풍선마다 읽을 틈을 조금씩 더
  reveal('#m3', s3 + 4.3);
  cam(g3 - 0.25, R3, 0.85);
  // 지금 위치(대전역)를 보고 → 2주 전 가족 단체방의 '대전'이 떠오른다
  gsap.set(['#fg', '#fk'], { autoAlpha: 0, scale: 0.94, x: 40 });
  tl.to('#fg', { autoAlpha: 1, scale: 1, x: 0, duration: 0.8, ease: 'back.out(1.4)' }, g3);
  tl.fromTo('#fg .pulse', { scale: 1, opacity: 0.9 }, { scale: 2.2, opacity: 0, duration: 1.2, repeat: 1, stagger: 0.6, ease: 'power1.out', immediateRender: false }, g3 + 0.25);
  mark('#gpsDj', g3 + 0.85);
  tl.to('#fk', { autoAlpha: 1, scale: 1, x: 0, duration: 0.8, ease: 'back.out(1.4)' }, g3 + 1.45);
  hop('#tokC', DT.g, DT.k, g3 + 2.25, 0.65, 40);
  // 가족 단체방에서도 같은 단서를 짚는다: 날아온 '대전' → 그때 사 주기로 한 '성심당 무화과시루', 내 말풍선에 테두리
  mark('#kkDj', g3 + 3.05, 0.45);
  mark('#kkSs', g3 + 3.55, 0.55);
  tl.fromTo('#kkMe', { boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { boxShadow: '0 0 0 3px rgba(107,78,255,.85)', duration: 0.4, ease: 'power2.out', immediateRender: false }, g3 + 3.55);
  const TC = { thread: th3 };
  // 두 기록이 휴대폰(키보드 도구줄 높이)으로 엮이면, 빛이 도구줄을 따라가 Weave 버튼이 크게 반짝 — 누르라는 신호
  tl.fromTo('#kbC .shim', { x: 380, opacity: 0 }, { x: -60, opacity: 1, duration: 0.45, ease: 'power1.in', immediateRender: false }, th3 + 0.55).to('#kbC .shim', { opacity: 0, duration: 0.15 }, th3 + 1.0);
  const wvGlow = th3 + 0.95;
  ev(wvGlow, 'glint');
  tl.to('#kbC .wv', { backgroundColor: '#6B4EFF', boxShadow: '0 6px 16px rgba(107,78,255,.55)', duration: 0.3, ease: 'power2.out' }, wvGlow);
  tl.to('#kbC .wv img.lit', { opacity: 1, duration: 0.3 }, wvGlow);
  tl.fromTo('#kbC .wv', { scale: 1 }, { scale: 1.55, duration: 0.42, ease: 'back.out(3)', immediateRender: false }, wvGlow)
    .to('#kbC .wv', { scale: 1.3, duration: 0.3, ease: 'power2.inOut' }, wvGlow + 0.42)
    .to('#kbC .wv', { scale: 1.42, duration: 0.42, yoyo: true, repeat: 3, ease: 'sine.inOut' }, wvGlow + 0.75);
  tl.fromTo('#kbC .wvfx .glow', { scale: 0.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.45, ease: 'power2.out', immediateRender: false }, wvGlow)
    .to('#kbC .wvfx .glow', { scale: 1.25, opacity: 0.65, duration: 0.42, yoyo: true, repeat: 2, ease: 'sine.inOut' }, wvGlow + 0.5);
  tl.fromTo('#kbC .wvfx .rg', { scale: 1, opacity: 0.9 }, { scale: 3.4, opacity: 0, duration: 1.0, stagger: 0.3, repeat: 1, ease: 'power2.out', immediateRender: false }, wvGlow + 0.05);
  tl.fromTo('#kbC .wvfx .badge', { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: 'back.out(3)', immediateRender: false }, wvGlow + 0.2);
  const SO = [[-34, -26], [38, -30], [44, 16], [-30, 22]];
  $$('#kbC .wvfx .st').forEach((e, i) => {
    gsap.set(e, { x: SO[i][0], y: SO[i][1] });
    tl.fromTo(e, { scale: 0, opacity: 0, rotation: -30 }, { scale: 1, opacity: 1, rotation: 0, duration: 0.3, yoyo: true, repeat: 3, repeatDelay: 0.12, ease: 'back.out(2)', immediateRender: false }, wvGlow + 0.1 + i * 0.12);
  });
  tl.set(['#kbC .wvfx .badge', '#kbC .wvfx .glow'], { opacity: 0 }, pTapW + 0.1);              // 누르면 배지·빛은 사라지고 시트가 뜬다
  tl.set('#kbC .wv', { scale: 1, backgroundColor: '#E6DEFF', boxShadow: 'none' }, pTapW + 1.0); tl.set('#kbC .wv img.lit', { opacity: 0 }, pTapW + 1.0);
  cam(th3 + 1.4, camPose(1.9, { x: 900, y: B['#kbC .tb'].y + 30 }, { x: 520, y: 540 }), 0.8);
  gsap.set('#wC', { y: 540 }); gsap.set('#scrimC', { opacity: 0 });
  tl.to('#wC', { y: 0, duration: 0.75, ease: 'power3.out' }, pTapW + 0.15);
  tl.to('#scrimC', { opacity: 1, duration: 0.5 }, pTapW + 0.15);
  edge(pTapW + 0.2);
  tl.to(['#fg', '#fk'], { autoAlpha: 0, x: 30, duration: 0.45, ease: 'power2.in' }, pTapW + 0.3);
  headOut('#hdC', pTapW + 0.3);
  cam(pTapW + 0.3, camPose(1.7, { x: B['#sgC'].x, y: (B['#sgC'].y + B['#btnC'].y) / 2 }, { x: 760, y: 560 }), 0.85);
  cam(pTapW + 1.3, camPose(2.1, { x: B['#sgC'].x, y: (B['#sgC'].y + B['#btnC'].y) / 2 }, { x: 760, y: 560 }), 0.7);   // 추천 문장을 크게
  tl.fromTo('#sgC', { boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { boxShadow: '0 0 0 2.5px rgba(107,78,255,.8)', duration: 0.4, ease: 'power2.out', immediateRender: false }, pTapW + 1.6);
  mark('#sgK', pTapW + 1.6, 0.55);                                                           // 기억에서 온 부분: '먹고 싶다던 무화과시루'
  tl.to('#wC', { y: 540, duration: 0.55, ease: 'power3.in' }, pTapI + 0.25);
  tl.to('#scrimC', { opacity: 0, duration: 0.45 }, pTapI + 0.3);
  const MSGTX = '엄마, 전에 먹고 싶다던 무화과시루 사갈까?';
  textAt($('#kinTx'), pTapI + 0.4, { text: MSGTX });
  cam(pTapI + 0.3, camPose(2.35, { x: MS[2].kin.x, y: MS[2].kin.y - 18 }, { x: 900, y: 560 }), 0.8);          // 입력창을 크게: 들어간 말이 읽히게
  textAt($('#kinTx'), pTapS + 0.1, { html: PH });
  reveal('#mSent', pTapS + 0.1);
  cam(pTapS + 0.15, camPose(2.05, { x: 985, y: MS[3]['#mSent'].y }, { x: 900, y: 520 }), 0.8);                 // 보낸 말을 크게
  cam(tReply - 0.15, camPose(2.05, { x: 970, y: (MS[4]['#mSent'].y + MS[4]['#mReply'].y) / 2 }, { x: 900, y: 540 }), 0.75);   // 답장이 오면 둘 다
  tl.to('#rdSent', { opacity: 0, duration: 0.2 }, tRead);
  reveal('#mReply', tReply); ev(tReply, 'msg');

  /* ── 끝 화면 (LOGO ~ DUR): 로고·문구를 충분히 읽을 수 있게 ── */
  tl.to(phone, { y: '+=70', scale: '-=0.15', autoAlpha: 0, filter: 'blur(6px)', duration: 0.5, ease: 'power3.in' }, LOGO - 0.45);
  gsap.set('#logo .mark', { scale: 0.4, rotation: -30, opacity: 0 });
  gsap.set('#logo .word', { clipPath: 'inset(-50% 100% -50% -4%)', x: -30, autoAlpha: 0 });   // 감춰 두지 않으면 글자 그림자가 처음부터 옅게 비침
  gsap.set(['#tag', '#sub'], { y: 24, opacity: 0 });
  gsap.set('#fin', { opacity: 0 });
  tl.to('#logo .mark', { scale: 1, rotation: 0, opacity: 1, duration: 1.0, ease: 'back.out(1.6)' }, LOGO - 0.05); ev(LOGO, 'logo');
  tl.set('#logo .word', { autoAlpha: 1 }, LOGO + 0.25);
  tl.to('#logo .word', { clipPath: 'inset(-50% -5% -50% -4%)', x: 0, duration: 1.0, ease: 'expo.out' }, LOGO + 0.25);
  tl.fromTo('#logo .wv', { backgroundPosition: '170% 0%, 0% 0%' }, { backgroundPosition: '-70% 0%, 0% 0%', duration: 1.3, ease: 'power2.inOut', immediateRender: false }, LOGO + 0.8);
  tl.to('#tag', { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, LOGO + 0.9);
  tl.to('#sub', { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, LOGO + 1.4);
  tl.to('#gai', { autoAlpha: 1, duration: 0.8, ease: 'power1.out' }, LOGO + 1.6);
  tl.to('#end', { scale: 1.02, duration: DUR - LOGO, ease: 'none' }, LOGO);
  tl.to('#fin', { opacity: 1, duration: 1.2, ease: 'power1.inOut' }, DUR - 1.2);

  tl.to('.g1', { x: 220, y: 60, duration: DUR, ease: 'none' }, 0);
  tl.to('.g2', { x: -160, y: -40, duration: DUR, ease: 'none' }, 0);
  tl.fromTo('.g3', { scale: 0.9, opacity: 0.7 }, { scale: 1.25, opacity: 1, duration: DUR, ease: 'none' }, 0);
  tl.set({}, {}, DUR);

  /* ── 손·실·날아가는 답: 카메라·시트가 움직인 뒤의 실제 자리를 재서 맞춘다 ── */
  const at = (t, sel) => { seekAll(t); return ctr(sel); };
  const atR = (t, sel) => { seekAll(t); return rectOf(sel); };
  const p1 = at(pTap1 - 0.1, '#kbA .wv');
  const p2 = at(T2 - 0.1, '#btnCC');
  const p3 = at(pTap3 - 0.1, '#kbA .srch');
  const pW = at(pTapW - 0.1, '#kbC .wv');
  const pI = at(pTapI - 0.1, '#btnC');
  const pS = at(pTapS - 0.1, '#kSend');
  const h0 = at(dragT - 0.05, '#wB .grab');
  const ansR = atR(T2 + 0.05, '#ansC');
  const ansFs = parseFloat(getComputedStyle($('#ansC')).fontSize);
  const sqR = atR(T2 + 1.2, '#sqA');
  const rb = ['#b1', '#b2', '#b3'].map(k => atR(TB.thread, k));
  const frC = atR(TC.thread, '#phone .frame');
  const wvG = at(wvGlow, '#kbC .wv');
  const tbC = at(TC.thread, '#kbC .tb');
  // 02: 위로 끄는 동안 손끝이 시트 윗부분을 따라가도록 자리를 촘촘히 잰다(카메라도 같이 움직이므로)
  const NS = 21, dragPts = [];
  for (let i = 0; i <= NS; i++) { const t = dragT + dragD * i / NS; dragPts.push({ t, ...at(t, '#wB .grab') }); }
  seekAll(0);
  if (DEBUG) $('#dbg').innerHTML = [p1, p2, p3, pW, pI, pS, h0].map(p => `<i style="left:${p.x}px; top:${p.y}px"></i>`).join('');

  gsap.set(hand, { x: 2100, y: 1200, rotation: -12, autoAlpha: 0 });
  gsap.set(spark, { autoAlpha: 0 });
  gsap.set('#htrail', { rotation: 12, height: 0 }); gsap.set('#htouch', { opacity: 0, scale: 0.6 });
  handIn(p1.x, p1.y, pTap1); press(p1.x, p1.y, pTap1, '#kbA .wv'); handOut(pTap1 + 0.2);
  tl.fromTo('#pill', { x: p1.x - 960, y: p1.y - 262, scale: 0.3, autoAlpha: 0 }, { x: 0, y: 0, scale: 1, autoAlpha: 1, duration: 1.1, ease: 'expo.out', immediateRender: false }, pTap1 + 0.5);
  handIn(p2.x, p2.y, T2); press(p2.x, p2.y, T2, '#btnCC'); handOut(T2 + 0.3);
  // 답이 칩이 되어 검색창으로 날아간다
  const sc0 = ansFs * 1.35 / 44, sc1 = 15.5 * boxPose.scale / 44;     // 답 글자 크기(사슬 1.35배) → 검색창 글자 크기(휴대폰 2배)
  gsap.set('#flyChip', { x: ansR.left - 26 * sc0, y: ansR.top + ansR.height / 2, yPercent: -50, scale: sc0, transformOrigin: '0% 50%' });
  tl.to('#flyChip', { autoAlpha: 1, duration: 0.08 }, T2 + 0.12);
  tl.set('#ansC', { opacity: 0 }, T2 + 0.2);                                         // 카드의 글자가 칩이 되어 떠난다
  tl.to('#flyChip', { scale: sc0 * 1.06, duration: 0.25, ease: 'power2.out' }, T2 + 0.12);
  tl.to('#flyChip', { x: sqR.left - 26 * sc1, y: sqR.top + sqR.height / 2, scale: sc1, duration: 0.6, ease: 'power3.inOut' }, T2 + 0.55);
  tl.to('#flyChip', { autoAlpha: 0, duration: 0.18 }, T2 + 1.1);
  handIn(p3.x, p3.y, pTap3, 0.6); press(p3.x, p3.y, pTap3, '#kbA .srch'); handOut(pTap3 + 0.3);
  // 02: 손잡이를 누르고 위로 끌어 올린다
  handIn(h0.x, h0.y + 6, dragT, 0.65);
  tl.to(hand, { scale: 0.92, duration: 0.1 }, dragT - 0.05);
  ev(dragT - 0.02, 'tap');
  tl.to('#htouch', { opacity: 1, scale: 1, duration: 0.15 }, dragT - 0.05);
  for (let i = 1; i <= NS; i++) tl.to(hand, { x: dragPts[i].x - TIP.x, y: dragPts[i].y + 6 - TIP.y, duration: dragD / NS, ease: 'none' }, dragPts[i - 1].t);
  tl.to('#htrail', { height: 190, duration: 0.35, ease: 'power2.out' }, dragT + 0.05).to('#htrail', { height: 0, opacity: 0, duration: 0.3, ease: 'power2.in' }, dragT + dragD - 0.2);
  tl.to('#htouch', { opacity: 0, scale: 1.3, duration: 0.25 }, dragT + dragD);
  tl.to(hand, { scale: 1, duration: 0.12 }, dragT + dragD);
  handOut(dragT + dragD + 0.1);
  tl.set('#htrail', { opacity: 1 }, dragT + dragD + 0.6);
  // 02: 휴대폰 속 카드 → 왼쪽 큰 카드로 곡선 세 가닥이 한 번에(답변이 나오기 전에 걷힘)
  const tb = ['#fl1', '#fl2', '#fl3'].map((k, i) => curve(`tb${i}`, bez({ x: rb[i].left + 8, y: rb[i].top + rb[i].height / 2 }, { x: FLR[k].right - 2, y: FLR[k].top + FLR[k].height / 2 }, 0.55), TB.thread, 0.6));
  tl.to(tb, { autoAlpha: 0, duration: 0.4 }, dragT + 6.3);
  // 03: 위치(GPS)·가족 단체방 → 휴대폰 오른쪽, 키보드 도구줄 높이로 모인다
  const K = { x: frC.right - 6, y: tbC.y };
  const ga = { x: FLR['#fg'].left + 2, y: FLR['#fg'].top + FLR['#fg'].height / 2 }, ka = { x: FLR['#fk'].left + 2, y: FLR['#fk'].top + FLR['#fk'].height * 0.78 };
  const tg = [curve('tg1', bez(ga, K, 0.6), TC.thread, 0.6, 6), curve('tg2', bez(ka, K, 0.6), TC.thread, 0.6, 6)];
  tl.to(tg, { autoAlpha: 0, duration: 0.35 }, th3 + 1.3);
  sparkAt(wvG.x, wvG.y, wvGlow); sparkAt(wvG.x, wvG.y, wvGlow + 0.65);
  handIn(pW.x, pW.y, pTapW); press(pW.x, pW.y, pTapW, null); handOut(pTapW + 0.3);
  handIn(pI.x, pI.y, pTapI); press(pI.x, pI.y, pTapI, '#btnC'); handOut(pTapI + 0.3);
  handIn(pS.x, pS.y, pTapS, 0.6); press(pS.x, pS.y, pTapS, '#kSend'); handOut(pTapS + 0.3);

  window.__events = EV.sort((a, b) => a.t - b.t);
  window.__taps = { p1, p2, p3, pW, pI, pS, h0, lift };
  window.__marks = { logo: LOGO, logoMin: LOGO_MIN, drop: D1, bar: BAR, ch1: C1, p0: P0, t2: T2, ch2: C2, s2, dragT, x2: X2, ch3: C3, s3, g3, th3, wvGlow, tapW: pTapW, tapI: pTapI, tapS: pTapS, reply: tReply, dur: DUR };
  window.__probe = t => {
    seekAll(t);
    const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom].map(v => Math.round(v)); };
    return { frags: frags.map(f => ({ kind: f.kind, row: f.row, op: +getComputedStyle(f.d).opacity, ring: +f.ring.style.opacity, r: R(f.d) })),
      hook: $$('#hook .line').map(R), hookOp: +getComputedStyle($('#hook')).opacity, clauses: CL.map(c => ({ op: +getComputedStyle($(c)).opacity, r: R($(c)) })), clT: CL_T, clK: CL_K, t0: frags.map(f => f.t0), offOp: HS.off[0] };
  };
  seekAll(0);
  return true;
}

window.__DURATION = DUR;
window.__seek = t => seekAll(t);
window.__ready = build();
