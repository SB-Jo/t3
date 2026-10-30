/* Weave 결선 인트로 v2 — GSAP 타임라인 하나(paused)를 시간 t로 탐색해 프레임을 찍는다.
   window.__seek(t), window.__DURATION, window.__events(효과음 시점 → tools/music.py), window.__ready, window.__taps
   v2(2026-10-29 피드백): 100 BPM(한 마디 2.4초) 39.6초, 문구 최소화(배지·설명 없음), 와인 장면 하나로 합침,
   휴대폰 확대·이동(카메라), 손 위치는 글꼴 로드와 카메라 이동이 끝난 뒤 실제 위치를 재서 맞춤 */
gsap.registerPlugin(DrawSVGPlugin, MotionPathPlugin, CustomEase);
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const DUR = 39.6;
const tl = gsap.timeline({ paused: true, defaults: { ease: 'power3.out', duration: 1.0 } });
const EV = [];
const ev = (t, type, o = {}) => EV.push({ t: Math.round(t * 1000) / 1000, type, ...o });
let seed = 20261029;
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const DEBUG = /debug/.test(location.search);

const hand = $('#hand'), spark = $('#spark'), sparks = $$('#spark .sp');
const TIP = { x: 39, y: 8 };                          // 손끝(지문 자리)이 #hand 상자 안에서 놓이는 곳
const rectOf = s => (typeof s === 'string' ? $(s) : s).getBoundingClientRect();
const ctr = s => { const r = rectOf(s); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; };

/* ── 뚝 바뀌는 상태(글자·표시)는 t로 바로 정한다 ───────── */
const PH = '<span style="color:#9a96a6; font-weight:400">메시지 입력</span>';
const QA = '지은이네 집들이 때 먹었던 와인';
const disc = [];
const applyDisc = t => disc.forEach(([c, f]) => f(c(t)));
const seekAll = t => { applyDisc(t); tl.seek(t, false); };

function makeKB(sel) {
  const KB = [['ㅂ','ㅈ','ㄷ','ㄱ','ㅅ','ㅛ','ㅕ','ㅑ','ㅐ','ㅔ'], ['ㅁ','ㄴ','ㅇ','ㄹ','ㅎ','ㅗ','ㅓ','ㅏ','ㅣ'], ['⇧','ㅋ','ㅌ','ㅊ','ㅍ','ㅠ','ㅜ','ㅡ','⌫'], ['!#1','한/영','한국어','.','↗']];
  $(sel).innerHTML = `<div class="tb"><span class="wv"><img src="assets/icons/weave-spool-6B4EFF.png" alt=""></span><svg><use href="#i-emo"/></svg><svg><use href="#i-tr"/></svg><svg><use href="#i-clip"/></svg><svg><use href="#i-gear"/></svg><span style="margin-left:auto">닫기 ⌄</span></div>` +
    KB.map(row => `<div class="krow">${row.map(k => {
      const cls = ['k'];
      if (['⇧', '⌫', '!#1', '한/영'].includes(k)) cls.push('g', 'w2');
      if (k === '한국어') cls.push('sp');
      if (k === '↗') cls.push('snd', 'w2');
      return `<span class="${cls.join(' ')}">${k === '↗' ? '<svg width="18" height="18"><use href="#i-plane"/></svg>' : k}</span>`;
    }).join('')}</div>`).join('');
}

/* ── 손으로 누르기 ─────────────────────────────── */
function handIn(x, y, t, d = 0.75) {
  tl.set(hand, { x: x - TIP.x + 190, y: y - TIP.y + 250, rotation: -12, scale: 1, autoAlpha: 0 }, t - d);
  tl.to(hand, { x: x - TIP.x, y: y - TIP.y, autoAlpha: 1, duration: d, ease: 'power3.out' }, t - d);
}
function handOut(t) { tl.to(hand, { x: '+=190', y: '+=250', autoAlpha: 0, duration: 0.6, ease: 'power2.in' }, t); }
function press(x, y, t, target) {
  tl.to(hand, { scale: 0.9, duration: 0.09, ease: 'power2.out' }, t - 0.06)
    .to(hand, { scale: 1, duration: 0.26, ease: 'power2.out' }, t + 0.06);
  tl.set(spark, { x, y, autoAlpha: 1 }, t)
    .fromTo(sparks, { drawSVG: '0% 0%', opacity: 1 }, { drawSVG: '0% 100%', duration: 0.22, ease: 'power2.out' }, t)
    .to(sparks, { drawSVG: '100% 100%', duration: 0.3, ease: 'power2.in' }, t + 0.24)
    .set(spark, { autoAlpha: 0 }, t + 0.56);
  if (target) tl.to(target, { scale: 0.95, duration: 0.09, yoyo: true, repeat: 1, ease: 'power1.inOut' }, t - 0.04);
  ev(t, 'tap');
}

/* ── 글자 입력 ─────────────────────────────────── */
function typeIn(el, text, t0, cps = 12, sfx = 'key') {
  const ch = [...text], times = [];
  let t = t0;
  for (const c of ch) { times.push(t); t += (1 / cps) * (0.75 + rnd() * 0.5) * (c === ' ' ? 0.6 : 1); }
  const d = t - t0, o = { p: 0 };
  tl.to(o, { p: 1, duration: d, ease: 'none', onUpdate() {
    const now = t0 + o.p * d; let n = 0; while (n < ch.length && times[n] <= now + 1e-6) n++;
    el.textContent = ch.slice(0, n).join('');
  } }, t0);
  disc.push([tt => tt < t0, on => { if (on) el.textContent = ''; }]);
  if (sfx) times.forEach((tt, i) => ch[i] !== ' ' && ev(tt, sfx));
  return t;
}

/* ── 카메라(휴대폰 확대·이동) ──────────────────────
   휴대폰 기본 자리의 중심은 화면 중심(960, 540). 기본 배치에서 잰 점 f를 배율 s로 화면의 점 T에 놓는다. */
const PC = { x: 960, y: 540 };
const camPose = (s, f, T) => ({ x: T.x - PC.x - s * (f.x - PC.x), y: T.y - PC.y - s * (f.y - PC.y), scale: s });
function cam(t, pose, d = 1.1, ease = 'power3.inOut') { tl.to('#phone', { ...pose, duration: d, ease }, t); ev(t, 'zoom', { d }); }
const edge = t => tl.fromTo('#phone .frame', { boxShadow: '0 60px 110px rgba(52,30,130,.26), 0 18px 34px rgba(52,30,130,.14), 0 0 0 0 rgba(139,104,245,0)' },
  { boxShadow: '0 60px 110px rgba(52,30,130,.26), 0 18px 34px rgba(52,30,130,.14), 0 0 52px 8px rgba(139,104,245,.55)', duration: 0.45, yoyo: true, repeat: 1, repeatDelay: 0.35, ease: 'power2.out' }, t);

/* ── 연결 표시 ───────────────────────────────────
   시트 안: 카드 오른쪽을 잇는 보라 점선(흰 테두리, 5·4) — 덱 5·6쪽과 같은 모양. 마스크를 그려 가며 드러낸다.
   휴대폰 밖: 흩어진 기록 칩 → 실 → 시트 안 카드(또는 추천 문장)로 빨려 들어간다. */
const svgNS = 'http://www.w3.org/2000/svg';
function linkCards(sheetSel, svgSel, cardSels, t, d = 0.7, merge = null) {
  const sheet = $(sheetSel), svg = $(svgSel), W = sheet.offsetWidth, H = sheet.offsetHeight;
  const ys = cardSels.map(c => { const e = $(c); return e.offsetTop + e.offsetHeight / 2; });
  const xr = W - 17, xl = W - 7;
  let dp, knots;
  if (merge) {
    const e = $(merge), ty = e.offsetTop + e.offsetHeight / 2;
    dp = `M${xr} ${ys[0]} H${xl} V${ty} H${xr}` + ys.slice(1).map(y => ` M${xr} ${y} H${xl}`).join('');
    knots = [...ys, ty];
  } else {
    dp = `M${xr} ${ys[0]} H${xl} V${ys[ys.length - 1]} H${xr}` + ys.slice(1, -1).map(y => ` M${xl} ${y} H${xr}`).join('');
    knots = ys;
  }
  const id = svg.id + 'M';
  svg.innerHTML = `<defs><mask id="${id}" maskUnits="userSpaceOnUse" x="-40" y="-40" width="${W + 80}" height="${H + 80}"><path class="mk" d="${dp}" stroke="#fff" stroke-width="16" fill="none" stroke-linecap="round" stroke-linejoin="round"/></mask></defs>` +
    `<g mask="url(#${id})"><path class="dh" d="${dp}"/><path class="dl" d="${dp}"/></g>` + knots.map(y => `<circle class="kn" cx="${xl}" cy="${y}" r="4.3"/>`).join('');
  gsap.set(svg.querySelector('.mk'), { drawSVG: '0% 0%' });
  gsap.set(svg.querySelectorAll('.kn'), { opacity: 0, scale: 0, transformOrigin: '50% 50%' });
  tl.to(svg.querySelector('.mk'), { drawSVG: '0% 100%', duration: d, ease: 'power1.inOut' }, t);
  tl.to(svg.querySelectorAll('.kn'), { opacity: 1, scale: 1, duration: 0.35, stagger: d / knots.length, ease: 'back.out(3)' }, t + 0.05);
  ev(t, 'link', { d });
}
function chipTo(chipSel, cr, b, tThread, tFly, id) {
  const a = { x: cr.left - 4, y: cr.top + cr.height / 2 }, dx = a.x - b.x;
  const g = document.createElementNS(svgNS, 'g'); g.id = id;
  const path = `M${a.x} ${a.y} C ${a.x - dx * 0.45} ${a.y}, ${b.x + dx * 0.45} ${b.y}, ${b.x} ${b.y}`;
  g.innerHTML = `<path class="thr-halo" d="${path}" style="stroke-width:11"/><path class="thr" d="${path}" style="stroke-width:5"/>`;
  $('#uxThreads').appendChild(g);
  gsap.set(`#${id} path`, { drawSVG: '0% 0%' });
  tl.to(`#${id} path`, { drawSVG: '0% 100%', duration: 0.55, ease: 'power2.inOut' }, tThread);
  ev(tThread, 'thread', { d: 0.55 });
  // 칩은 실을 따라 카드로 빨려 들어가고, 실은 카드 쪽으로 감긴다
  tl.to(chipSel, { x: b.x - (cr.left + cr.width / 2), y: b.y - (cr.top + cr.height / 2), scale: 0.3, autoAlpha: 0, duration: 0.5, ease: 'power3.in' }, tFly);
  tl.to(`#${id} path`, { drawSVG: '100% 100%', duration: 0.5, ease: 'power3.in' }, tFly);
}

async function build() {
  const fams = ['400 20px "Noto Sans KR"', '500 20px "Noto Sans KR"', '600 20px "Noto Sans KR"', '700 20px "Noto Sans KR"', '400 20px Inter', '500 20px Inter', '600 20px Inter', '700 20px Inter', '20px "Nanum Pen Script"', '700 20px "Samsung Sharp Sans"'];
  await Promise.all(fams.map(f => document.fonts.load(f, '가A')));
  await document.fonts.ready;
  makeKB('#kbA'); makeKB('#kbC');
  $('#sqA').textContent = QA; $('#kinTx').innerHTML = PH;          // 잴 때는 완성된 모습으로
  await Promise.all([...document.images].map(im => im.decode().catch(() => {})));

  /* 기본 배치(휴대폰 변형 전)에서 잰 점 */
  const B = {};
  for (const k of ['#kbA .wv', '#scrA .sbar', '#r1', '#handle', '#b1', '#b2', '#b3', '#sgC', '#btnC', '#chatIn', '.kin']) B[k] = ctr(k);
  const CR = {}; for (const k of ['#fb1', '#fb2', '#fb3', '#fc1', '#fc2']) CR[k] = rectOf(k);
  gsap.set(['#fb1', '#fb2', '#fb3', '#fc1', '#fc2'], { autoAlpha: 0, scale: 0.85, y: 16 });
  $('#wbChip').style.top = ($('#wB .ttl').offsetTop - 1) + 'px';
  const wBtop = rectOf('#wB').top, lift = B['#handle'].y - wBtop - 14;

  /* ── 1. 질문 → "카톡이었나, 사진이었나, 캘린더였나…" (0 – 7.2초) ── */
  const FR = [
    ['app-kakao', '지은', '다들 와줘서 고마워 ㅎㅎ', 'k', -700, -170, -220], ['samsung-gallery', 'IMG_2481.jpg', '3월 15일 20:14', 'g', -230, -170, -380, 1],
    ['samsung-calendar', '지은 집들이', '3월 15일 (일) 18:00', 'c', 250, -170, -120], ['app-notes', '와인 메모', '달지 않은 화이트?', 'n', 700, -170, -330],
    ['samsung-email-blue', '[예약 확인] 오사카 호텔', '2월 27일', 'm', -480, 0, -420], ['app-kakao', '민호', '그 와인 맛있더라', 'k', 20, 0, 40],
    ['samsung-gallery', 'IMG_2475.jpg', '3월 15일 19:52', 'g', 500, 0, -200, 1], ['samsung-calendar', '팀 회식', '3월 20일 19:00', 'c', -720, 170, -60],
    ['app-kakao', '가족 단체방', '성심당 무화과시루 먹고 싶다', 'k', -250, 170, -300], ['app-notes', '장보기', '우유, 계란, 무화과', 'n', 240, 170, 80],
    ['samsung-gallery', '스크린샷', '3월 18일 13:02', 'g', 720, 170, -150], ['samsung-calendar', '치과 예약', '3월 22일 10:30', 'c', -470, 335, -120],
    ['app-map', '대전역', '최근 방문', 'p', 20, 335, -380], ['samsung-email-blue', 'Q1_Demo_v3.pdf', '어제 오후 6:20', 'm', 470, 335, -60],
  ];
  const cam3 = $('#cam'), frags = [];
  FR.forEach(f => {
    const d = document.createElement('div');
    d.className = 'frag kr';
    d.innerHTML = `<i class="ring"></i><img class="ic" src="assets/icons/${f[0]}.png" alt="">${f[7] ? '<img class="ph" src="assets/img/ux2-wine-photo.png" alt="">' : ''}<div><div class="t">${f[1]}</div><div class="m">${f[2]}</div></div>`;
    cam3.appendChild(d);
    frags.push({ d, kind: f[3], x: f[4] * 1.04 + (rnd() - 0.5) * 50, y: f[5] + (rnd() - 0.5) * 30, z: f[6] * 0.55 + 90 });
  });
  await Promise.all($$('#cam img').map(im => im.decode().catch(() => {})));

  const hookW = $$('#hook .w');
  gsap.set(hookW, { y: 60, opacity: 0, filter: 'blur(12px)' });
  tl.to(hookW.slice(0, 3), { y: 0, opacity: 1, filter: 'blur(0px)', duration: 1.1, stagger: 0.13, ease: 'expo.out' }, 0.3);
  tl.to(hookW.slice(3), { y: 0, opacity: 1, filter: 'blur(0px)', duration: 1.1, stagger: 0.15, ease: 'expo.out' }, 1.15);
  ev(0.3, 'word'); ev(1.15, 'word');
  tl.to('#hook', { y: -330, scale: 0.6, duration: 1.3, ease: 'expo.inOut' }, 2.55);

  frags.forEach((f, i) => {
    gsap.set(f.d, { x: f.x, y: f.y, z: f.z - 500, opacity: 0, xPercent: -50, yPercent: -50 });
    tl.to(f.d, { z: f.z, opacity: 1, duration: 1.8, ease: 'expo.out' }, 2.75 + (i % 7) * 0.07 + rnd() * 0.25);
  });
  ev(2.75, 'rise');
  gsap.set(cam3, { rotationY: 6, rotationX: 4, z: -80 });
  tl.to(cam3, { rotationY: -4, rotationX: -1, z: 70, duration: 5.2, ease: 'sine.inOut' }, 2.4);

  const clauses = ['#c1', '#c2', '#c3'], kinds = ['k', 'g', 'c'], times = [3.55, 4.65, 5.75];
  gsap.set(clauses, { y: 30, opacity: 0 });
  clauses.forEach((c, i) => {
    const t = times[i];
    tl.to(c, { y: 0, opacity: 1, duration: 0.8, ease: 'expo.out' }, t);
    ev(t, 'hl', { n: i });
    frags.forEach(f => {
      const on = f.kind === kinds[i];
      tl.to(f.d, { opacity: on ? 1 : 0.32, scale: on ? 1.07 : 0.98, duration: 0.6, ease: 'power2.out' }, t);
      tl.to(f.d.querySelector('.ring'), { opacity: on ? 1 : 0, duration: 0.45 }, t);
    });
    if (i > 0) tl.to(clauses[i - 1], { color: '#9C97AC', duration: 0.5 }, t);
  });
  tl.to(['#hook', '#where'], { opacity: 0, y: '-=24', filter: 'blur(8px)', duration: 0.6, ease: 'power2.in' }, 6.75);
  tl.to('#space', { opacity: 0, scale: 1.08, filter: 'blur(14px)', duration: 0.75, ease: 'power2.in' }, 6.7);
  ev(6.7, 'swish');

  /* ── 2. 와인 하나로: 휴대폰 → 확대 → Weave → 단서 엮기 → 정확한 이름으로 (7.2 – 21초) ── */
  const phone = $('#phone');
  gsap.set(phone, { autoAlpha: 0, x: 0, y: 160, scale: 0.92, transformOrigin: '50% 50%' });
  gsap.set(['#scrB', '#scrC'], { xPercent: 100 });
  gsap.set(['#r1', '#r2', '#r3'], { autoAlpha: 0 });
  tl.to(phone, { autoAlpha: 1, y: 0, scale: 1, duration: 1.2, ease: 'power3.out' }, 7.2); ev(7.2, 'rise');
  typeIn($('#sqA'), QA, 8.1, 12);
  tl.fromTo('#caretA', { opacity: 1 }, { opacity: 0, duration: 0.01, repeat: 11, yoyo: true, repeatDelay: 0.3, ease: 'none' }, 7.6);
  // 검색어와 키보드 도구줄(Weave 아이콘)이 함께 크게 보이게
  const qa = { x: B['#scrA .sbar'].x, y: (B['#scrA .sbar'].y + B['#kbA .wv'].y) / 2 };
  cam(9.5, camPose(1.55, qa, { x: 960, y: 520 }), 1.15);
  const pTap1 = 10.95;
  edge(11.0);
  tl.fromTo('#kbA .wv', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)' }, { boxShadow: '0 0 0 14px rgba(107,78,255,0)', duration: 0.6, ease: 'power2.out' }, 11.0);
  // 휴대폰은 왼쪽으로 치워지고, 검색어가 Weave 검색창으로 날아오른다
  tl.to(phone, { x: -1400, y: 60, scale: 0.9, rotation: -4, duration: 1.15, ease: 'power3.inOut' }, 11.35);
  tl.to(phone, { autoAlpha: 0, duration: 0.3 }, 12.2);
  ev(11.35, 'fly');

  gsap.set(['#cA', '#cB', '#cC'], { autoAlpha: 0, scale: 0.9, y: 26 });
  gsap.set(['#tA .thr', '#tA .thr-halo', '#tB .thr', '#tB .thr-halo', '#tC .thr', '#tC .thr-halo'], { drawSVG: '0% 0%' });
  gsap.set('.pen', { clipPath: 'inset(-10% 100% -10% -4%)' });
  gsap.set('.knot', { scale: 0, opacity: 0 });
  gsap.set('#scan', { y: -80, opacity: 0 });
  gsap.set('#ocrbox', { opacity: 0, scale: 1.25 });
  gsap.set('#h2', { y: 34, opacity: 0 });
  gsap.set('#pill', { autoAlpha: 0 });
  const draw = (g, t, d) => { tl.to(`${g} .thr, ${g} .thr-halo`, { drawSVG: '0% 100%', duration: d, ease: 'power2.inOut' }, t); ev(t, 'thread', { d }); };
  const penIn = (id, t) => tl.to(id, { clipPath: 'inset(-10% -4% -10% -4%)', duration: 0.7, ease: 'power1.inOut' }, t);
  const knot = (id, t) => tl.fromTo(id, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.5, ease: 'back.out(3)' }, t);
  const cardIn = (id, t) => { tl.to(id, { autoAlpha: 1, scale: 1, y: 0, duration: 0.9, ease: 'back.out(1.3)' }, t); ev(t, 'card'); };
  draw('#tA', 12.3, 0.8); penIn('#pen1', 12.45); knot('#k1', 13.05); cardIn('#cA', 13.0);
  draw('#tB', 13.85, 0.55); penIn('#pen2', 13.9); knot('#k2', 14.4); cardIn('#cB', 14.35);
  tl.to('#scan', { opacity: 1, duration: 0.1 }, 15.25).to('#scan', { y: 240, duration: 0.7, ease: 'power1.inOut' }, 15.25).to('#scan', { opacity: 0, duration: 0.2 }, 15.85);
  ev(15.25, 'scan');
  tl.to('#ocrbox', { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(2)' }, 15.75);
  penIn('#pen3', 15.8);
  typeIn($('#ocr'), 'BABICH SAUVIGNON BLANC', 15.9, 40, 'tick');
  draw('#tC', 16.5, 0.55); knot('#k3', 17.0); cardIn('#cC', 17.0); ev(17.05, 'answer');
  tl.fromTo('#cC', { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 0 rgba(166,124,242,.55)' },
    { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 28px rgba(166,124,242,0)', duration: 1.1, ease: 'power2.out' }, 17.1);
  tl.to('#h2', { y: 0, opacity: 1, duration: 1.0, ease: 'expo.out' }, 17.35); ev(17.35, 'word');
  const pTap2 = 18.45;                                    // '입력하기'
  tl.to(['#pill', '#cA', '#cB', '#threads', '.pen', '.knot', '#h2'], { autoAlpha: 0, filter: 'blur(8px)', scale: 0.97, duration: 0.6, ease: 'power2.in', stagger: 0.02 }, 18.85);
  tl.to('#cC', { x: -420, y: -150, scale: 0.55, autoAlpha: 0, filter: 'blur(4px)', duration: 0.75, ease: 'power3.in' }, 18.9);
  // 돌아온 휴대폰: 정확한 이름으로 검색된 화면을 크게
  disc.push([t => t >= 18.8, on => { const q = $('#sqA'); if (on) { q.textContent = '배비치 소비뇽 블랑'; q.style.color = '#6B4EFF'; q.style.fontWeight = 700; } else { q.style.color = ''; q.style.fontWeight = ''; } }]);
  disc.push([t => t >= 18.8, on => { $('#kbA').style.display = on ? 'none' : ''; $('#caretA').style.display = on ? 'none' : ''; }]);
  tl.set(['#r1', '#r2', '#r3'], { autoAlpha: 1 }, 18.8);
  const res = camPose(1.6, { x: B['#scrA .sbar'].x, y: (B['#scrA .sbar'].y + B['#r1'].y) / 2 }, { x: 960, y: 450 });
  tl.set(phone, { x: res.x - 1500, y: res.y + 40, scale: res.scale * 0.92, rotation: 4, autoAlpha: 1 }, 18.9);
  tl.to(phone, { x: res.x, y: res.y, scale: res.scale, rotation: 0, duration: 1.25, ease: 'power3.out' }, 18.95); ev(18.95, 'fly');
  tl.fromTo('#scrA .sbar', { boxShadow: '0 0 0 0 rgba(107,78,255,.5)' }, { boxShadow: '0 0 0 14px rgba(107,78,255,0)', duration: 1.0 }, 20.0);
  ev(20.0, 'answer2');

  /* ── 3. 흩어진 기록을, 한 번에 (통화) (21 – 27.3초) ── */
  const R = { x: 330, y: 0, scale: 1 }, L = { x: -330, y: 0, scale: 1 };
  cam(21.0, R, 1.15);
  tl.to('#scrA', { xPercent: -100, duration: 0.85, ease: 'power3.inOut' }, 21.05);
  tl.to('#scrB', { xPercent: 0, duration: 0.85, ease: 'power3.inOut' }, 21.05); ev(21.05, 'swish');
  gsap.set('.head', { autoAlpha: 0 });
  gsap.set('.head h3', { y: 30, opacity: 0 });
  const headIn = (id, t) => { tl.set(id, { autoAlpha: 1 }, t); tl.to(`${id} h3`, { y: 0, opacity: 1, duration: 1.0, ease: 'expo.out' }, t); ev(t, 'word'); };
  const headOut = (id, t) => tl.to(`${id} h3`, { y: -20, opacity: 0, duration: 0.5, ease: 'power2.in' }, t).set(id, { autoAlpha: 0 }, t + 0.55);
  headIn('#hdB', 21.5);
  const ct = { s: 48 };
  tl.to(ct, { s: 54, duration: 6.3, ease: 'none', onUpdate() { $('#ctime').textContent = `00:${String(Math.floor(ct.s)).padStart(2, '0')}`; } }, 21.0);
  const dragT = 22.2, dragD = 0.95;                        // 시트 윗변이 손끝을 따라 올라온다
  gsap.set('#wB', { y: lift + 14, autoAlpha: 0 });
  tl.set('#wB', { autoAlpha: 1 }, dragT);
  tl.to('#wB', { y: 0, duration: dragD, ease: 'power2.inOut' }, dragT); ev(dragT, 'swipe');
  edge(dragT + 0.3);
  typeIn($('#qB'), 'A사 시연 관련 자료', 23.25, 12);
  // 앱마다 흩어진 기록이 휴대폰 밖에 떠오르고 → 실로 이어져 → 시트 안 카드가 된다(실·흡수는 아래 '나중에'에서)
  tl.to(['#fb1', '#fb2', '#fb3'], { autoAlpha: 1, scale: 1, y: 0, duration: 0.8, stagger: 0.16, ease: 'back.out(1.5)' }, 23.6);
  ev(23.6, 'card'); ev(23.76, 'card'); ev(23.92, 'card');
  gsap.set(['#b1', '#b2', '#b3'], { opacity: 0, scale: 0.96 });
  tl.to(['#b1', '#b2', '#b3'], { opacity: 1, scale: 1, duration: 0.6, stagger: 0.15, ease: 'power2.out' }, 24.9);
  const TB = { thread: 24.25, fly: 24.8 };
  linkCards('#wB', '#wbLink', ['#b1', '#b2', '#b3'], 25.3, 0.7);
  gsap.set('#wbChip', { autoAlpha: 0, scale: 0.8 });
  tl.to('#wbChip', { autoAlpha: 1, scale: 1, duration: 0.5, ease: 'back.out(2)' }, 25.45);
  const cardsC = { x: B['#b2'].x, y: (B['#b1'].y + B['#b3'].y) / 2 };
  cam(25.6, camPose(1.7, cardsC, { x: 1260, y: 540 }), 1.0);

  /* ── 4. 떠올리기 전에, 먼저 건네요 (카톡) (27.3 – 36초) ── */
  headOut('#hdB', 27.3);
  cam(27.3, L, 1.2);
  tl.to('#scrB', { xPercent: -100, duration: 0.85, ease: 'power3.inOut' }, 27.4);
  tl.to('#scrC', { xPercent: 0, duration: 0.85, ease: 'power3.inOut' }, 27.4); ev(27.4, 'swish');
  disc.push([t => t >= 27.75, on => { $('#sbt').textContent = on ? '10:31' : '13:00'; }]);
  headIn('#hdC', 27.95);
  // 지금 위치(GPS)와 가족 단체방 기록이 떠오른다
  tl.to(['#fc1', '#fc2'], { autoAlpha: 1, scale: 1, y: 0, duration: 0.8, stagger: 0.22, ease: 'back.out(1.5)' }, 28.3);
  ev(28.3, 'card'); ev(28.52, 'card');
  tl.fromTo('#fc1 .pulse', { scale: 1, opacity: 0.9 }, { scale: 2.4, opacity: 0, duration: 1.1, repeat: 1, stagger: 0.55, ease: 'power1.out' }, 28.45);
  gsap.set('#wC', { y: 540 }); gsap.set('#scrimC', { opacity: 0 });
  tl.fromTo('#kbC .wv', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)', scale: 1 }, { boxShadow: '0 0 0 14px rgba(107,78,255,0)', scale: 1.14, duration: 0.55, yoyo: true, repeat: 1, ease: 'power2.out' }, 28.7);
  tl.to('#wC', { y: 0, duration: 0.85, ease: 'power3.out' }, 28.95); ev(28.95, 'swish');
  tl.to('#scrimC', { opacity: 1, duration: 0.6 }, 28.95);
  edge(29.05);
  const TC = { thread: 29.75, fly: 30.25 };
  tl.fromTo('#sgC', { boxShadow: '0 0 0 0 rgba(139,104,245,.6)' }, { boxShadow: '0 0 0 12px rgba(139,104,245,0)', duration: 0.8, ease: 'power2.out' }, 30.55);
  linkCards('#wC', '#wcLink', ['#c1card', '#c2card'], 30.6, 0.6, '#sgC');
  const sugC = { x: B['#sgC'].x, y: (B['#sgC'].y + B['#btnC'].y) / 2 };
  cam(30.75, camPose(1.8, sugC, { x: 680, y: 520 }), 1.0);
  const pTap3 = 32.3;                                     // '입력하기'
  tl.to('#wC', { y: 540, duration: 0.6, ease: 'power3.in' }, 32.6);
  tl.to('#scrimC', { opacity: 0, duration: 0.5 }, 32.65);
  disc.push([t => t >= 32.85 && t < 33.9, on => { if (on) $('#kinTx').textContent = '엄마, 전에 먹고 싶다던 무화과시루 사갈까?'; }]);
  disc.push([t => t < 32.85 || t >= 33.9, on => { if (on) $('#kinTx').innerHTML = PH; }]);
  cam(32.7, camPose(1.3, { x: B['#chatIn'].x, y: B['.kin'].y - 150 }, { x: 640, y: 560 }), 0.95);
  const pTap4 = 33.8;                                     // 보내기
  disc.push([t => t >= 33.9, on => { $('#mSent').style.display = on ? 'flex' : 'none'; }]);
  tl.fromTo('#mSent .bub', { scale: 0.6, transformOrigin: '100% 100%', opacity: 0 }, { scale: 1, opacity: 1, duration: 0.55, ease: 'back.out(1.6)' }, 33.9); ev(33.9, 'send');
  disc.push([t => t >= 34.5, on => { $('#mReply').style.display = on ? 'flex' : 'none'; }]);
  tl.fromTo('#mReply', { y: 22, opacity: 0 }, { y: 0, opacity: 1, duration: 0.7, ease: 'expo.out' }, 34.5); ev(34.5, 'msg');

  /* ── 5. 엔드 카드 (36 – 39.6초) ── */
  headOut('#hdC', 35.45);
  tl.to(phone, { y: '+=70', scale: '-=0.15', autoAlpha: 0, filter: 'blur(6px)', duration: 0.65, ease: 'power3.in' }, 35.45);
  ev(35.45, 'swish');
  gsap.set('#logo .mark', { scale: 0.4, rotation: -30, opacity: 0 });
  gsap.set('#logo .word', { clipPath: 'inset(-50% 100% -50% -4%)', x: -30 });
  gsap.set(['#tag', '#sub'], { y: 24, opacity: 0 });
  gsap.set('#fin', { opacity: 0 });
  tl.to('#logo .mark', { scale: 1, rotation: 0, opacity: 1, duration: 1.0, ease: 'back.out(1.6)' }, 35.9); ev(36.0, 'logo');
  tl.to('#logo .word', { clipPath: 'inset(-50% -5% -50% -4%)', x: 0, duration: 1.0, ease: 'expo.out' }, 36.15);
  tl.fromTo('#logo .wv', { backgroundPosition: '170% 0%, 0% 0%' }, { backgroundPosition: '-70% 0%, 0% 0%', duration: 1.3, ease: 'power2.inOut' }, 36.75);
  tl.to('#tag', { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, 36.9); ev(36.9, 'word');
  tl.to('#sub', { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, 37.35);
  tl.to('#end', { scale: 1.02, duration: 3.7, ease: 'none' }, 35.9);
  tl.to('#fin', { opacity: 1, duration: 0.75, ease: 'power1.inOut' }, DUR - 0.75);

  /* 배경은 전체 내내 천천히 */
  tl.to('.g1', { x: 220, y: 60, duration: DUR, ease: 'none' }, 0);
  tl.to('.g2', { x: -160, y: -40, duration: DUR, ease: 'none' }, 0);
  tl.fromTo('.g3', { scale: 0.9, opacity: 0.7 }, { scale: 1.25, opacity: 1, duration: DUR, ease: 'none' }, 0);
  tl.set({}, {}, DUR);

  /* ── 손: 카메라·시트가 움직인 뒤의 실제 자리를 재서 그 자리를 누른다 ── */
  const at = (t, sel) => { seekAll(t); return ctr(sel); };
  const p1 = at(pTap1 - 0.1, '#kbA .wv');
  const p2 = at(pTap2 - 0.1, '#btnCC');
  const p3 = at(pTap3 - 0.1, '#btnC');
  const p4 = at(pTap4 - 0.1, '#kSend');
  const h0 = at(dragT - 0.05, '#handle');
  const atR = (t, sel) => { seekAll(t); return rectOf(sel); };
  const rB = ['#b1', '#b2', '#b3'].map(k => atR(TB.fly, k));
  const rS = atR(TC.fly, '#sgC');
  seekAll(0);
  ['#fb1', '#fb2', '#fb3'].forEach((k, i) => chipTo(k, CR[k], { x: rB[i].right - 22, y: rB[i].top + rB[i].height / 2 }, TB.thread + i * 0.08, TB.fly + i * 0.1, `ob${i}`));
  ['#fc1', '#fc2'].forEach((k, i) => chipTo(k, CR[k], { x: rS.right - 18, y: rS.top + rS.height * (i ? 0.66 : 0.34) }, TC.thread + i * 0.1, TC.fly + i * 0.1, `oc${i}`));
  if (DEBUG) $('#dbg').innerHTML = [p1, p2, p3, p4, h0].map(p => `<i style="left:${p.x}px; top:${p.y}px"></i>`).join('');

  gsap.set(hand, { x: 2100, y: 1200, rotation: -12, autoAlpha: 0 });
  gsap.set(spark, { autoAlpha: 0 });
  handIn(p1.x, p1.y, pTap1); press(p1.x, p1.y, pTap1, '#kbA .wv'); handOut(pTap1 + 0.3);
  // Weave 검색창이 누른 자리에서 날아올라 위에 놓인다
  tl.fromTo('#pill', { x: p1.x - 960, y: p1.y - 162, scale: 0.22, autoAlpha: 0 }, { x: 0, y: 0, scale: 1, autoAlpha: 1, duration: 1.1, ease: 'expo.out', immediateRender: false }, 11.5);
  ev(11.5, 'pill');
  handIn(p2.x, p2.y, pTap2); press(p2.x, p2.y, pTap2, '#btnCC'); handOut(pTap2 + 0.3);
  handIn(h0.x, h0.y, dragT, 0.65);
  tl.to(hand, { scale: 0.92, duration: 0.1 }, dragT - 0.05);
  tl.to(hand, { y: `-=${lift}`, duration: dragD, ease: 'power2.inOut' }, dragT);
  tl.to(hand, { scale: 1, duration: 0.12 }, dragT + dragD);
  handOut(dragT + dragD + 0.1);
  handIn(p3.x, p3.y, pTap3); press(p3.x, p3.y, pTap3, '#btnC'); handOut(pTap3 + 0.3);
  handIn(p4.x, p4.y, pTap4, 0.6); press(p4.x, p4.y, pTap4, '#kSend'); handOut(pTap4 + 0.3);

  window.__events = EV.sort((a, b) => a.t - b.t);
  window.__taps = { p1, p2, p3, p4, h0, lift };
  seekAll(0);
  return true;
}

window.__DURATION = DUR;
window.__seek = t => seekAll(t);
window.__ready = build();
