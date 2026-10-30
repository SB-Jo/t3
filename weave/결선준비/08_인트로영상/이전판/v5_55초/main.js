/* Weave 결선 인트로 v5 — GSAP 타임라인 하나(paused)를 시간 t로 탐색해 프레임을 찍는다.
   window.__seek(t), window.__DURATION, window.__events(효과음 시점 → tools/music.py), window.__ready, window.__taps, window.__marks, window.__probe(t)
   v5(2026-10-29 피드백)
   - 도입: 기록 조각의 밝기·테두리를 매 프레임 계산해 자막과 정확히 맞춘다(카톡 → 사진 → 캘린더 → 노트). 제목이 올라간 뒤에 조각이 뜬다
   - 01: 사슬의 단계마다 카메라가 따라가며 확대, 뱃지·문장은 위. 입력하기 → 답이 검색창으로 들어가 글자가 바뀜 → 검색 키 → 결과
   - 02: 통화 상황(말풍선)부터. 위로 올리면 카메라가 손을 따라 올라가 검색창을 확대, 실 세 가닥은 한 번에
   - 03: 휴대폰 왼쪽·문장과 플로팅 오른쪽. 대화를 하나씩 따라 확대 → 두 기록이 엮여 Weave 버튼이 반짝 → 누름 → 입력 → 전송 → 읽음 뒤 답장
   - 끝: Weave got it!, Galaxy AI는 오른쪽 아래 모서리
   상태가 겹치기 쉬운 것(조각 밝기, 글자, 화면 전환)은 tween 대신 cont(시간 t의 순수 함수)로 매 프레임 다시 계산한다. */
gsap.registerPlugin(DrawSVGPlugin, MotionPathPlugin, CustomEase);
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];

/* ── 음악 마디에 맞춘 시각(tools/music.py와 같은 값) ── */
const D1 = 9.5, BAR = 2.4;                             // 곡(Mixkit 'A Special Feeling', 100 BPM)이 터지는 순간, 한 마디 길이

/* ── 장면 시각(초) ── */
const C2 = 26.5, s2 = C2 + 1.0;                        // 02 카드(01 휴대폰이 다 빠진 뒤), 02 시작
const dragT = s2 + 2.95, dragD = 1.05, X2 = dragT + 5.3; // 위로 끌기(곡이 다시 들어오는 마디), 02 끝
const C3 = X2 + 0.5, s3 = C3 + 1.05;                   // 03 카드(02가 다 빠진 뒤), 03 시작
const pTapW = s3 + 6.55, pTapI = pTapW + 1.6, pTapS = pTapI + 1.25;    // Weave 버튼 · 입력하기 · 전송
const tRead = pTapS + 0.85, tReply = pTapS + 1.65;    // 읽음(1이 사라짐) → 답장
const LOGO_MIN = tReply + 1.9;                         // 답장을 읽을 시간
const LOGO = D1 + Math.ceil((LOGO_MIN - D1) / BAR - 1e-6) * BAR;   // 로고는 곡의 마디 첫 박에
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

function makeKB(sel, action) {
  const KB = [['ㅂ','ㅈ','ㄷ','ㄱ','ㅅ','ㅛ','ㅕ','ㅑ','ㅐ','ㅔ'], ['ㅁ','ㄴ','ㅇ','ㄹ','ㅎ','ㅗ','ㅓ','ㅏ','ㅣ'], ['⇧','ㅋ','ㅌ','ㅊ','ㅍ','ㅠ','ㅜ','ㅡ','⌫'], ['!#1','한/영','한국어','.','↗']];
  $(sel).innerHTML = `<div class="tb"><span class="wv"><img src="assets/icons/weave-spool-6B4EFF.png" alt=""></span><svg><use href="#i-emo"/></svg><svg><use href="#i-tr"/></svg><svg><use href="#i-clip"/></svg><svg><use href="#i-gear"/></svg><span style="margin-left:auto">닫기 ⌄</span><i class="shim"></i></div>` +
    KB.map(row => `<div class="krow">${row.map(k => {
      const cls = ['k'];
      if (['⇧', '⌫', '!#1', '한/영'].includes(k)) cls.push('g', 'w2');
      if (k === '한국어') cls.push('sp');
      if (k === '↗') cls.push('snd', 'w2', ...(action === 'search' ? ['srch'] : []));
      const icon = action === 'search' ? '<svg width="20" height="20" style="color:#fff"><use href="#i-search"/></svg>' : '<svg width="18" height="18"><use href="#i-plane"/></svg>';
      return `<span class="${cls.join(' ')}">${k === '↗' ? icon : k}</span>`;
    }).join('')}</div>`).join('');
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

  /* ── 기본 배치에서 잰 자리(휴대폰 그대로, 화면 셋이 겹친 상태) ── */
  const resultState = on => {
    $('#glogo').style.display = on ? 'none' : ''; $('.gtop').style.display = on ? 'none' : '';
    $('#gbox').style.top = on ? '104px' : ''; $('#gres').style.display = on ? '' : 'none';
    $('#kbA').style.display = on ? 'none' : ''; $('#caretA').style.display = on ? 'none' : '';
  };
  const B = {};
  for (const k of ['#kbA .wv', '#kbA .srch', '#gbox', '#handle', '#qB', '#sgC', '#btnC', '#chatIn', '.kin', '#kbC .wv', '#kbC .tb']) B[k] = ctr(k);
  resultState(true); B.gboxR = ctr('#gbox'); B.r1 = ctr('#r1'); resultState(false);
  const wBtop = rectOf('#wB').top, lift = B['#handle'].y - wBtop - 14;
  // 03 대화: 메시지가 하나씩 도착(높이 0 → 원래 높이). 단계 n(도착한 메시지 수)마다 말풍선 자리를 미리 잰다
  const MSG = ['#m2', '#m3', '#mSent', '#mReply'];
  const natH = {}; MSG.forEach(k => natH[k] = rectOf(k).height);
  const stage = n => MSG.forEach((k, i) => gsap.set(k, { height: i < n ? natH[k] : 0, marginTop: i < n ? 10 : 0, overflow: 'hidden' }));
  const MS = [];
  for (let n = 0; n <= 4; n++) { stage(n); MS[n] = {}; for (const k of ['#m1', ...MSG]) MS[n][k] = ctr(`${k} .bub`); MS[n].kin = ctr('.kin'); }
  stage(0);
  const FLR = {}; for (const k of ['#fl1', '#fl2', '#fl3', '#fg', '#fk']) FLR[k] = rectOf(k);
  gsap.set('.chap', { autoAlpha: 0 });
  gsap.set('.head', { autoAlpha: 0 });
  gsap.set(['#fl1', '#fl2', '#fl3', '#fg', '#fk', '#frec', '#flChip', '#flLink', '#callQ', '#callT', '#flyChip', '#topScrim', '#gai'], { autoAlpha: 0 });

  /* ── 도입 (0 – 9초): "그때 그 와인, 다시 사고 싶은데 / 이름이 뭐였더라?" → 카톡·사진·캘린더·노트 ──
     조각은 4줄(제목 아래 ~ 자막 위)에만 놓고, 밝기·테두리·크기는 매 프레임 계산한다. */
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
  tl.to(cam3, { rotationY: -3, rotationX: -1, z: 30, duration: 6.4, ease: 'sine.inOut' }, 2.7);
  const CL = ['#c1', '#c2', '#c3', '#c4'], CL_K = ['k', 'g', 'c', 'n'], CL_T = [4.15, 5.2, 6.25, 7.3];
  gsap.set(CL, { y: 30, opacity: 0 });
  CL.forEach((c, i) => {
    tl.to(c, { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, CL_T[i]);
    if (i > 0) tl.to(CL[i - 1], { color: '#A29DB2', duration: 0.5 }, CL_T[i]).to(`${CL[i - 1]} b`, { color: '#B9A8F3', duration: 0.5 }, CL_T[i]);
  });
  const E_IN = gsap.parseEase('expo.out'), E_HL = gsap.parseEase('power2.out');
  const HS = { base: [1, 1, 0], on: [1, 1.07, 1], off: [0.24, 0.97, 0] };   // [밝기, 크기, 테두리]
  const hlOf = (f, i) => i < 0 ? HS.base : (f.kind === CL_K[i] ? HS.on : HS.off);
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
  tl.to(['#hook', '#where'], { opacity: 0, y: '-=24', filter: 'blur(8px)', duration: 0.6, ease: 'power2.in' }, 8.35);
  tl.to('#space', { opacity: 0, scale: 1.08, filter: 'blur(14px)', duration: 0.65, ease: 'power2.in' }, 8.3);

  /* ── 01 단서로 찾기 ── */
  chapIn('#ch1', 9.05); chapOut('#ch1', 10.2);
  const phone = $('#phone');
  gsap.set(phone, { autoAlpha: 0, x: 0, y: 160, scale: 0.92, transformOrigin: '50% 50%' });
  gsap.set(['#scrB', '#scrC'], { xPercent: 100 });
  gsap.set('#gres', { display: 'none' });
  tl.to(phone, { autoAlpha: 1, y: 0, scale: 1, duration: 1.1, ease: 'power3.out' }, 10.5);
  cam(11.2, camPose(2.3, B['#gbox'], { x: 960, y: 430 }), 0.9);              // 검색할 때는 검색창을 크게
  typeIn($('#sqA'), QA, 12.0, 12);
  tl.fromTo('#caretA', { opacity: 1 }, { opacity: 0, duration: 0.01, repeat: 9, yoyo: true, repeatDelay: 0.3, ease: 'none' }, 10.9);
  cam(13.65, camPose(2.3, { x: B['#kbA .wv'].x + 90, y: B['#kbA .wv'].y }, { x: 960, y: 600 }), 0.85);   // Weave를 누를 때는 Weave 아이콘 쪽
  const pTap1 = 14.75;
  edge(14.8);
  tl.fromTo('#kbA .wv', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)' }, { boxShadow: '0 0 0 14px rgba(107,78,255,0)', duration: 0.6, ease: 'power2.out', immediateRender: false }, 14.8);
  tl.to(phone, { y: '+=2300', duration: 0.55, ease: 'power2.in' }, 15.0);              // 휴대폰은 아래로 빠지고, 물음은 위로
  tl.set(phone, { autoAlpha: 0 }, 15.6);

  // 사슬: 단계마다 카메라가 그 자리로 가서 확대한다(#w1 안 좌표 = 확대 전 화면 좌표)
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
  tl.to('#topScrim', { autoAlpha: 1, duration: 0.5 }, 15.5); headIn('#h1', 15.5);
  wcam(15.85, wPose(1.45, { x: 330, y: 470 }, { x: 720, y: 600 }), 1.0);                       // 언제였지? → 캘린더
  draw('#tA', 16.1, 0.7); penIn('#pen1', 16.2); cardIn('#cA', 16.65);
  wcam(17.2, wPose(1.3, { x: 930, y: 600 }, { x: 960, y: 660 }), 0.9);                         // 그날 찍은 사진엔? → 사진
  draw('#tB', 17.3, 0.6); penIn('#pen2', 17.35); cardIn('#cB', 17.7);
  wcam(18.3, wPose(1.6, { x: 930, y: 700 }, { x: 960, y: 610 }), 0.85);                        // 라벨엔 뭐라고? → 글자 읽기
  tl.to('#scan', { opacity: 1, duration: 0.1 }, 18.45).to('#scan', { y: 240, duration: 0.65, ease: 'power1.inOut' }, 18.45).to('#scan', { opacity: 0, duration: 0.2 }, 19.0);
  tl.to('#ocrbox', { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(2)' }, 18.9);
  penIn('#pen3', 18.95);
  typeIn($('#ocr'), 'BABICH SAUVIGNON BLANC', 19.0, 40, null);
  wcam(19.5, { x: 0, y: 0, scale: 1 }, 0.95);                                                   // 한눈에: 사슬 전체 + 답
  draw('#tC', 19.7, 0.6); cardIn('#cC', 20.15); ev(20.2, 'answer');
  tl.fromTo('#cC', { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 0 rgba(166,124,242,.55)' },
    { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 28px rgba(166,124,242,0)', duration: 1.1, ease: 'power2.out', immediateRender: false }, 20.25);
  wcam(21.05, wPose(1.35, { x: 1560, y: 745 }, { x: 1180, y: 720 }), 0.8);                      // 답 카드 · 입력하기
  const pTap2 = 22.15;
  // 입력하기 → 답이 검색창으로 들어가 글자가 바뀜
  tl.to(['#w1'], { autoAlpha: 0, filter: 'blur(8px)', duration: 0.5, ease: 'power2.in' }, 22.35);
  tl.to(['#topScrim'], { autoAlpha: 0, duration: 0.45 }, 22.3); headOut('#h1', 22.25);
  const boxPose = camPose(2.0, B['#gbox'], { x: 960, y: 400 });
  tl.set(phone, { ...boxPose, y: boxPose.y + 1150, rotation: 0, autoAlpha: 1 }, 22.25);
  tl.to(phone, { y: boxPose.y, duration: 0.85, ease: 'power3.out' }, 22.3);
  textAt($('#sqA'), 22.9, { html: `<span class="sel">${QA}</span>` });
  textAt($('#sqA'), 23.3, { text: ANS });
  tl.fromTo('#gsweep', { scaleX: 0, opacity: 1 }, { scaleX: 1, duration: 0.45, ease: 'power2.out', immediateRender: false }, 23.3).to('#gsweep', { opacity: 0, duration: 0.3 }, 24.0);
  const both = camPose(1.3, { x: (B['#gbox'].x + B['#kbA .srch'].x) / 2, y: (B['#gbox'].y + B['#kbA .srch'].y) / 2 }, { x: 960, y: 560 });
  cam(23.6, both, 0.75);                                                                        // 바뀐 검색어와 검색 키를 한 화면에
  const pTap3 = 24.6;
  tl.fromTo('#kbA .srch', { boxShadow: '0 0 0 0 rgba(47,107,255,.55)' }, { boxShadow: '0 0 0 12px rgba(47,107,255,0)', duration: 0.6, ease: 'power2.out', immediateRender: false }, 24.1);
  tl.fromTo('#gload', { scaleX: 0, opacity: 1 }, { scaleX: 1, duration: 0.4, ease: 'power1.inOut', immediateRender: false }, 24.67).to('#gload', { opacity: 0, duration: 0.15 }, 25.07);
  when(t => t >= 24.75, on => resultState(on));
  tl.fromTo(['#gres .gchips', '#gres .res'], { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.07, ease: 'expo.out', immediateRender: false }, 24.75);
  cam(24.75, camPose(1.45, { x: B.gboxR.x, y: (B.gboxR.y + B.r1.y) / 2 }, { x: 960, y: 470 }), 0.9);
  tl.fromTo('#gbox', { boxShadow: '0 1px 6px rgba(32,33,36,.28), 0 0 0 0 rgba(26,115,232,.45)' }, { boxShadow: '0 1px 6px rgba(32,33,36,.28), 0 0 0 12px rgba(26,115,232,0)', duration: 1.0, immediateRender: false }, 25.7);

  /* ── 02 한 번에 모아 보기: 휴대폰 오른쪽, 통화 상황 → 위로 올려 검색 → 세 기록 ── */
  tl.to(phone, { x: '-=420', autoAlpha: 0, filter: 'blur(6px)', duration: 0.45, ease: 'power3.in' }, 26.05);
  chapIn('#ch2', C2); chapOut('#ch2', C2 + 1.0);
  tl.set('#scrA', { xPercent: -100 }, C2 + 0.15); tl.set('#scrB', { xPercent: 0 }, C2 + 0.15);
  const R2 = { x: 470, y: 0, scale: 1 };
  tl.set(phone, { x: 1400, y: 0, scale: 1, rotation: 0, filter: 'blur(0px)', autoAlpha: 1 }, s2 - 0.1);
  tl.to(phone, { x: R2.x, duration: 1.05, ease: 'power3.out' }, s2);
  headIn('#hdB', s2 + 0.25);
  cont.push(t => { $('#ctime').textContent = `00:${String(48 + Math.floor(clamp((t - s2) / 1.0, 0, 9))).padStart(2, '0')}`; });
  tl.fromTo('#callQ', { autoAlpha: 0, x: -30, scale: 0.96 }, { autoAlpha: 1, x: 0, scale: 1, duration: 0.75, ease: 'back.out(1.4)', immediateRender: false }, s2 + 0.5);
  $$('#callQ .eq i').forEach((b, i) => {
    const d = 0.13 + 0.04 * ((i * 7) % 5);
    tl.fromTo(b, { scaleY: 0.25 }, { scaleY: 1, duration: d, repeat: Math.floor(2.4 / d), yoyo: true, ease: 'sine.inOut', immediateRender: false }, s2 + 0.55 + i * 0.03);
  });
  tl.fromTo('#callT', { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.7, ease: 'expo.out', immediateRender: false }, s2 + 1.35);
  const hPose = camPose(1.55, B['#handle'], { x: 1330, y: 860 });
  const qPose = camPose(2.0, B['#qB'], { x: 1250, y: 330 });
  cam(s2 + 2.0, hPose, 0.8);                                                                     // 아래 손잡이 쪽을 크게
  gsap.set('#chevB svg', { opacity: 0 });
  tl.fromTo('#chevB svg', { y: 8, opacity: 0 }, { y: -8, opacity: 1, duration: 0.42, stagger: 0.1, repeat: 1, repeatDelay: 0.08, ease: 'power1.out', immediateRender: false }, s2 + 2.15);
  tl.to('#chevB svg', { opacity: 0, duration: 0.15 }, dragT);
  tl.fromTo('#scrB .hlab', { scale: 1 }, { scale: 1.12, duration: 0.3, yoyo: true, repeat: 1, ease: 'power1.inOut', immediateRender: false }, s2 + 2.25);
  tl.fromTo('#handle', { y: 0, boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { y: -7, boxShadow: '0 0 12px 3px rgba(107,78,255,.55)', duration: 0.22, yoyo: true, repeat: 3, ease: 'sine.inOut', immediateRender: false }, s2 + 2.2);
  gsap.set('#wB', { y: lift + 14, autoAlpha: 0 });
  tl.set('#wB', { autoAlpha: 1 }, dragT);
  tl.to('#wB', { y: 0, duration: dragD, ease: 'power2.inOut' }, dragT);
  when(t => t >= dragT && t < dragT + dragD + 0.25, on => $('#wB').classList.toggle('drag', on));
  cam(dragT, qPose, dragD, 'power2.inOut');                                                       // 카메라가 손을 따라 올라가 검색창으로
  edge(dragT + 0.3);
  typeIn($('#qB'), '어제 A사 시연 준비', dragT + dragD + 0.15, 12);
  tl.to(['#callQ', '#callT'], { autoAlpha: 0, x: -30, duration: 0.4, ease: 'power2.in', stagger: 0.04 }, dragT + 2.0);
  cam(dragT + 2.15, R2, 0.8);
  gsap.set(['#b1', '#b2', '#b3'], { opacity: 0, y: 14 });
  tl.to(['#b1', '#b2', '#b3'], { opacity: 1, y: 0, duration: 0.55, stagger: 0.1, ease: 'expo.out' }, dragT + 2.3);
  const TB = { thread: dragT + 2.75, pop: dragT + 2.95 };
  ['#fl1', '#fl2', '#fl3'].forEach((k, i) => {
    gsap.set(k, { autoAlpha: 0, scale: 0.92, x: 40 });
    tl.to(k, { autoAlpha: 1, scale: 1, x: 0, duration: 0.8, ease: 'back.out(1.4)' }, TB.pop + i * 0.06);
  });
  const L1 = ['#fl1', '#fl2', '#fl3'].map(k => ({ x: FLR[k].left + 2, y: FLR[k].top + FLR[k].height / 2 }));
  const xb = L1[0].x - 70;
  curve('flc', `M${L1[0].x} ${L1[0].y} C ${xb} ${L1[0].y}, ${xb} ${L1[1].y}, ${L1[1].x} ${L1[1].y} C ${xb} ${L1[1].y}, ${xb} ${L1[2].y}, ${L1[2].x} ${L1[2].y}`, dragT + 3.7, 0.7, 5.5);
  gsap.set('#flChip', { left: FLR['#fl1'].left, top: FLR['#fl1'].top - 52, x: 0, scale: 0.85 });
  tl.to('#flChip', { autoAlpha: 1, scale: 1, duration: 0.6, ease: 'back.out(2)' }, dragT + 3.9);
  tl.to('#mk1', { backgroundSize: '100% 100%', duration: 0.5, ease: 'power2.inOut' }, dragT + 4.15);   // 물어본 답(순서·집합 시간)에 표시
  tl.to('#mk3', { backgroundSize: '100% 100%', duration: 0.5, ease: 'power2.inOut' }, dragT + 4.45);

  /* ── 03 먼저 건네기: 휴대폰 왼쪽, 문장·플로팅 오른쪽 ── */
  tl.to(['#fl1', '#fl2', '#fl3', '#flChip', '#flc'], { autoAlpha: 0, x: -30, duration: 0.45, ease: 'power2.in', stagger: 0.03 }, X2);
  headOut('#hdB', X2);
  tl.to(phone, { x: '+=420', autoAlpha: 0, filter: 'blur(6px)', duration: 0.45, ease: 'power3.in' }, X2 + 0.05);
  chapIn('#ch3', C3); chapOut('#ch3', C3 + 1.0);
  tl.set('#scrB', { xPercent: -100 }, C3 + 0.3); tl.set('#scrC', { xPercent: 0 }, C3 + 0.3);
  when(t => t >= C3 + 0.3, on => { $('#sbt').textContent = on ? '22:44' : '13:00'; });
  const R3 = { x: -400, y: 0, scale: 1 };
  tl.set(phone, { x: -1500, y: 0, scale: 1, rotation: 0, filter: 'blur(0px)', autoAlpha: 1 }, s3 - 0.1);
  tl.to(phone, { x: R3.x, duration: 1.0, ease: 'power3.out' }, s3);
  headIn('#hdC', s3 + 0.3);
  // 대화를 하나씩: 엄마 → 나 → 엄마. 카메라는 새 말풍선 쪽으로 조금씩 옮겨 간다
  const mPose = (n, k) => camPose(1.85, { x: lerp(960, MS[n][k].x, 0.45), y: MS[n][k].y }, { x: 490, y: 560 });
  const reveal = (k, t) => {
    tl.to(k, { height: natH[k], marginTop: 10, duration: 0.38, ease: 'power2.out' }, t);
    tl.fromTo(`${k} .bub`, { scale: 0.7, opacity: 0, transformOrigin: $(k).classList.contains('me') ? '100% 100%' : '0% 0%' },
      { scale: 1, opacity: 1, duration: 0.45, ease: 'back.out(1.6)', immediateRender: false }, t + 0.05);
  };
  gsap.set(['#m2 .bub', '#m3 .bub', '#mSent .bub', '#mReply .bub'], { opacity: 0 });
  cam(s3 + 0.6, mPose(0, '#m1'), 0.9);
  tl.fromTo('#m1 .bub', { boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { boxShadow: '0 0 0 3px rgba(107,78,255,.45)', duration: 0.35, yoyo: true, repeat: 1, repeatDelay: 0.4, immediateRender: false }, s3 + 1.2);
  reveal('#m2', s3 + 1.75); cam(s3 + 1.75, mPose(1, '#m2'), 0.7);
  reveal('#m3', s3 + 2.7); cam(s3 + 2.7, mPose(2, '#m3'), 0.7);
  cam(s3 + 3.55, R3, 0.85);
  gsap.set(['#fg', '#fk'], { autoAlpha: 0, scale: 0.94, x: 40 });
  tl.to('#fg', { autoAlpha: 1, scale: 1, x: 0, duration: 0.8, ease: 'back.out(1.4)' }, s3 + 3.75);
  tl.fromTo('#fg .pulse', { scale: 1, opacity: 0.9 }, { scale: 2.2, opacity: 0, duration: 1.2, repeat: 1, stagger: 0.6, ease: 'power1.out', immediateRender: false }, s3 + 4.0);
  tl.to('#fk', { autoAlpha: 1, scale: 1, x: 0, duration: 0.8, ease: 'back.out(1.4)' }, s3 + 3.9);
  const TC = { thread: s3 + 4.35 };
  // 두 실이 휴대폰 오른쪽(키보드 도구줄 높이)으로 들어가면, 빛이 도구줄을 따라 Weave 버튼까지 가고 버튼이 반짝
  tl.fromTo('#kbC .shim', { x: 380, opacity: 0 }, { x: -60, opacity: 1, duration: 0.45, ease: 'power1.in', immediateRender: false }, s3 + 4.85).to('#kbC .shim', { opacity: 0, duration: 0.15 }, s3 + 5.3);
  const wvGlow = s3 + 5.25;
  tl.fromTo('#kbC .wv', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)', scale: 1 }, { boxShadow: '0 0 0 16px rgba(107,78,255,0)', scale: 1.22, duration: 0.45, yoyo: true, repeat: 3, ease: 'power2.out', immediateRender: false }, wvGlow);
  ev(wvGlow, 'glint');
  tl.fromTo('#kbC .wv', { backgroundColor: '#E6DEFF' }, { backgroundColor: '#CBB8FF', duration: 0.3, yoyo: true, repeat: 3, ease: 'sine.inOut', immediateRender: false }, wvGlow);
  const tbPose = camPose(1.7, { x: 900, y: B['#kbC .tb'].y + 30 }, { x: 520, y: 520 });
  cam(s3 + 5.55, tbPose, 0.75);
  gsap.set('#wC', { y: 540 }); gsap.set('#scrimC', { opacity: 0 });
  tl.to('#wC', { y: 0, duration: 0.75, ease: 'power3.out' }, pTapW + 0.15);
  tl.to('#scrimC', { opacity: 1, duration: 0.5 }, pTapW + 0.15);
  edge(pTapW + 0.2);
  tl.to(['#fg', '#fk'], { autoAlpha: 0, x: 30, duration: 0.45, ease: 'power2.in' }, pTapW + 0.3);
  headOut('#hdC', pTapW + 0.3);
  cam(pTapW + 0.3, camPose(1.7, { x: B['#sgC'].x, y: (B['#sgC'].y + B['#btnC'].y) / 2 }, { x: 760, y: 560 }), 0.85);
  tl.to('#wC', { y: 540, duration: 0.55, ease: 'power3.in' }, pTapI + 0.25);
  tl.to('#scrimC', { opacity: 0, duration: 0.45 }, pTapI + 0.3);
  const MSGTX = '엄마, 전에 먹고 싶다던 무화과시루 사갈까?';
  textAt($('#kinTx'), pTapI + 0.4, { text: MSGTX });
  cam(pTapI + 0.3, camPose(1.6, { x: 960, y: MS[2].kin.y - 110 }, { x: 760, y: 600 }), 0.75);
  textAt($('#kinTx'), pTapS + 0.1, { html: PH });
  reveal('#mSent', pTapS + 0.1);
  cam(pTapS + 0.15, camPose(1.5, { x: 960, y: MS[4].kin.y - 190 }, { x: 760, y: 540 }), 0.8);
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
  const p2 = at(pTap2 - 0.1, '#btnCC');
  const p3 = at(pTap3 - 0.1, '#kbA .srch');
  const pW = at(pTapW - 0.1, '#kbC .wv');
  const pI = at(pTapI - 0.1, '#btnC');
  const pS = at(pTapS - 0.1, '#kSend');
  const h0 = at(dragT - 0.05, '#wB .grab');
  const ansR = atR(pTap2 + 0.05, '#ansC');
  const ansFs = parseFloat(getComputedStyle($('#ansC')).fontSize);
  const sqR = atR(23.35, '#sqA');
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
  tl.fromTo('#pill', { x: p1.x - 960, y: p1.y - 262, scale: 0.3, autoAlpha: 0 }, { x: 0, y: 0, scale: 1, autoAlpha: 1, duration: 1.1, ease: 'expo.out', immediateRender: false }, 15.25);
  handIn(p2.x, p2.y, pTap2); press(p2.x, p2.y, pTap2, '#btnCC'); handOut(pTap2 + 0.3);
  // 답이 칩이 되어 검색창으로 날아간다
  const sc0 = ansFs * 1.35 / 44, sc1 = 15.5 * boxPose.scale / 44;     // 답 글자 크기(사슬 1.35배) → 검색창 글자 크기(휴대폰 2배)
  gsap.set('#flyChip', { x: ansR.left - 26 * sc0, y: ansR.top + ansR.height / 2, yPercent: -50, scale: sc0, transformOrigin: '0% 50%' });
  tl.to('#flyChip', { autoAlpha: 1, duration: 0.08 }, pTap2 + 0.12);
  tl.set('#ansC', { opacity: 0 }, pTap2 + 0.2);                                  // 카드의 글자가 칩이 되어 떠난다
  tl.to('#flyChip', { scale: sc0 * 1.06, duration: 0.25, ease: 'power2.out' }, pTap2 + 0.12);
  tl.to('#flyChip', { x: sqR.left - 26 * sc1, y: sqR.top + sqR.height / 2, scale: sc1, duration: 0.6, ease: 'power3.inOut' }, 22.7);
  tl.to('#flyChip', { autoAlpha: 0, duration: 0.18 }, 23.25);
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
  // 02: 휴대폰 속 카드 → 왼쪽 큰 카드로 곡선 세 가닥이 한 번에
  const tb = ['#fl1', '#fl2', '#fl3'].map((k, i) => curve(`tb${i}`, bez({ x: rb[i].left + 8, y: rb[i].top + rb[i].height / 2 }, { x: FLR[k].right - 2, y: FLR[k].top + FLR[k].height / 2 }, 0.55), TB.thread, 0.6));
  tl.to(tb, { autoAlpha: 0, duration: 0.45 }, X2);
  // 03: 위치(GPS)·가족 단체방 → 휴대폰 오른쪽, 키보드 도구줄 높이로 모인다
  const K = { x: frC.right - 6, y: tbC.y };
  const ga = { x: FLR['#fg'].left + 2, y: FLR['#fg'].top + FLR['#fg'].height / 2 }, ka = { x: FLR['#fk'].left + 2, y: FLR['#fk'].top + FLR['#fk'].height * 0.74 };
  const tg = [curve('tg1', bez(ga, K, 0.6), TC.thread, 0.6, 6), curve('tg2', bez(ka, K, 0.6), TC.thread, 0.6, 6)];
  tl.to(tg, { autoAlpha: 0, duration: 0.35 }, s3 + 5.5);
  sparkAt(wvG.x, wvG.y, wvGlow); sparkAt(wvG.x, wvG.y, wvGlow + 0.6);
  handIn(pW.x, pW.y, pTapW); press(pW.x, pW.y, pTapW, '#kbC .wv'); handOut(pTapW + 0.3);
  handIn(pI.x, pI.y, pTapI); press(pI.x, pI.y, pTapI, '#btnC'); handOut(pTapI + 0.3);
  handIn(pS.x, pS.y, pTapS, 0.6); press(pS.x, pS.y, pTapS, '#kSend'); handOut(pTapS + 0.3);

  window.__events = EV.sort((a, b) => a.t - b.t);
  window.__taps = { p1, p2, p3, pW, pI, pS, h0, lift };
  window.__marks = { logo: LOGO, logoMin: LOGO_MIN, drop: D1, bar: BAR, ch1: 9.05, ch2: C2, ch3: C3, s2, s3, dragT, x2: X2, reply: tReply };
  window.__probe = t => {
    seekAll(t);
    const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom].map(v => Math.round(v)); };
    return { frags: frags.map(f => ({ kind: f.kind, row: f.row, op: +getComputedStyle(f.d).opacity, ring: +f.ring.style.opacity, r: R(f.d) })),
      hook: $$('#hook .line').map(R), hookOp: +getComputedStyle($('#hook')).opacity, clauses: CL.map(c => ({ op: +getComputedStyle($(c)).opacity, r: R($(c)) })), clT: CL_T, clK: CL_K, t0: frags.map(f => f.t0) };
  };
  seekAll(0);
  return true;
}

window.__DURATION = DUR;
window.__seek = t => seekAll(t);
window.__ready = build();
