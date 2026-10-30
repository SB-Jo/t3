/* Weave 결선 인트로 v3 — GSAP 타임라인 하나(paused)를 시간 t로 탐색해 프레임을 찍는다.
   window.__seek(t), window.__DURATION, window.__events(효과음 시점 → tools/music.py), window.__ready, window.__taps
   v3(2026-10-29 피드백): 삼성 글꼴, 41.6초(100 BPM), 도입 4구절·느리게, 구글 검색 화면('다시 사고 싶은데'),
   통화·카톡 장면은 휴대폰을 왼쪽에 두고 오른쪽에 큼직한 기록 카드가 실로 이어짐, 카톡은 연결 → 추천 → 누르기 순서로 천천히 */
gsap.registerPlugin(DrawSVGPlugin, MotionPathPlugin, CustomEase);
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const DUR = 41.6;
const tl = gsap.timeline({ paused: true, defaults: { ease: 'power3.out', duration: 1.0 } });
const EV = [];
const ev = (t, type, o = {}) => EV.push({ t: Math.round(t * 1000) / 1000, type, ...o });
let seed = 20261029;
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const DEBUG = /debug/.test(location.search);
const svgNS = 'http://www.w3.org/2000/svg';

const hand = $('#hand'), spark = $('#spark'), sparks = $$('#spark .sp');
const TIP = { x: 39, y: 8 };
const rectOf = s => (typeof s === 'string' ? $(s) : s).getBoundingClientRect();
const ctr = s => { const r = rectOf(s); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; };

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
function cam(t, pose, d = 1.1, ease = 'power3.inOut') { tl.to('#phone', { ...pose, duration: d, ease }, t); }
const edge = t => tl.fromTo('#phone .frame', { boxShadow: '0 60px 110px rgba(52,30,130,.26), 0 18px 34px rgba(52,30,130,.14), 0 0 0 0 rgba(139,104,245,0)' },
  { boxShadow: '0 60px 110px rgba(52,30,130,.26), 0 18px 34px rgba(52,30,130,.14), 0 0 52px 8px rgba(139,104,245,.55)', duration: 0.45, yoyo: true, repeat: 1, repeatDelay: 0.35, ease: 'power2.out' }, t);

/* ── 연결 표시 ─────────────────────────────────── */
function linkCards(sheetSel, svgSel, cardSels, t, d = 0.7, merge = null) {   // 시트 안 카드 오른쪽 점선
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
  ev(t, 'link');
}
function thread(id, a, b, t, d = 0.5, bend = 0.45, w = 5) {          // 화면 위 실(그라데이션, 흰 테두리)
  const dx = b.x - a.x;
  const path = `M${a.x} ${a.y} C ${a.x + dx * bend} ${a.y}, ${b.x - dx * bend} ${b.y}, ${b.x} ${b.y}`;
  const g = document.createElementNS(svgNS, 'g'); g.id = id;
  g.innerHTML = `<path class="thr-halo" d="${path}" style="stroke-width:${w + 6}"/><path class="thr" d="${path}" style="stroke-width:${w}"/>`;
  $('#uxThreads').appendChild(g);
  gsap.set(`#${id} path`, { drawSVG: '0% 0%' });
  tl.to(`#${id} path`, { drawSVG: '0% 100%', duration: d, ease: 'power2.inOut' }, t);
  ev(t, 'thread');
  return `#${id}`;
}
function dashed(svgSel, pathD, knots, t, d = 0.8) {                  // 화면 위 보라 점선(덱 5·6쪽 모양)
  const svg = $(svgSel), id = svg.id + 'M';
  svg.innerHTML = `<defs><mask id="${id}" maskUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080"><path class="mk" d="${pathD}" stroke="#fff" stroke-width="22" fill="none" stroke-linecap="round" stroke-linejoin="round"/></mask></defs>` +
    `<g mask="url(#${id})"><path class="dh" d="${pathD}"/><path class="dl" d="${pathD}"/></g>` + knots.map(p => `<circle class="kn" cx="${p.x}" cy="${p.y}" r="8"/>`).join('');
  gsap.set(svg.querySelector('.mk'), { drawSVG: '0% 0%' });
  gsap.set(svg.querySelectorAll('.kn'), { opacity: 0, scale: 0, transformOrigin: '50% 50%' });
  tl.to(svg.querySelector('.mk'), { drawSVG: '0% 100%', duration: d, ease: 'power1.inOut' }, t);
  tl.to(svg.querySelectorAll('.kn'), { opacity: 1, scale: 1, duration: 0.4, stagger: d / knots.length, ease: 'back.out(3)' }, t + 0.05);
  ev(t, 'link');
}

async function build() {
  const fams = ['400 20px SamsungOneKorean', '500 20px SamsungOneKorean', '700 20px SamsungOneKorean', '400 20px SamsungOne', '500 20px SamsungOne', '700 20px SamsungOne', '700 20px "Samsung Sharp Sans"'];
  await Promise.all(fams.map(f => document.fonts.load(f, '가A')));
  await document.fonts.ready;
  makeKB('#kbA'); makeKB('#kbC');
  $('#sqA').textContent = QA; $('#kinTx').innerHTML = PH;
  await Promise.all([...document.images].map(im => im.decode().catch(() => {})));

  /* 검색 결과 상태(구글 결과 화면) 켜고 끄기 */
  const resultState = on => {
    $('#glogo').style.display = on ? 'none' : ''; $('.gtop').style.display = on ? 'none' : '';
    $('#gbox').style.top = on ? '104px' : ''; $('#gres').style.display = on ? '' : 'none';
    $('#kbA').style.display = on ? 'none' : ''; $('#caretA').style.display = on ? 'none' : '';
    const q = $('#sqA');
    if (on) { q.textContent = '배비치 소비뇽 블랑'; q.style.color = '#1a0dab'; q.style.fontWeight = 700; } else { q.style.color = ''; q.style.fontWeight = ''; }
  };
  /* 기본 배치(휴대폰 변형 전)에서 잰 점 */
  const B = {};
  for (const k of ['#kbA .wv', '#gbox', '#handle', '#b1', '#b2', '#b3', '#sgC', '#btnC', '#chatIn', '.kin']) B[k] = ctr(k);
  resultState(true); B.gboxR = ctr('#gbox'); B.r1 = ctr('#r1'); resultState(false);
  const wBtop = rectOf('#wB').top, lift = B['#handle'].y - wBtop - 14;
  const FLR = {}; for (const k of ['#fl1', '#fl2', '#fl3', '#fg', '#fk', '#frec']) FLR[k] = rectOf(k);

  /* ── 1. "그때 그 와인, 다시 사고 싶은데 / 이름이 뭐였더라?" → 어디서 찾지? (0 – 9.6초) ── */
  const FR = [
    ['app-kakao', '지은', '다들 와줘서 고마워 ㅎㅎ', 'k', -700, -170, -220], ['samsung-gallery', 'IMG_2481.jpg', '3월 15일 20:14', 'g', -230, -170, -380, 1],
    ['samsung-calendar', '지은 집들이', '3월 15일 (일) 18:00', 'c', 250, -170, -120], ['app-notes', '와인 메모', '달지 않은 화이트?', 'n', 700, -170, -330],
    ['samsung-email-blue', '[예약 확인] 오사카 호텔', '2월 27일', 'm', -480, 0, -420], ['app-kakao', '민호', '그 와인 맛있더라', 'k', 20, 0, 40],
    ['samsung-gallery', 'IMG_2475.jpg', '3월 15일 19:52', 'g', 500, 0, -200, 1], ['samsung-calendar', '팀 회식', '3월 20일 19:00', 'c', -720, 170, -60],
    ['app-kakao', '가족 단체방', '성심당 무화과시루 먹고 싶다', 'k', -250, 170, -300], ['app-notes', '장보기', '우유, 계란, 무화과', 'n', 240, 170, 80],
    ['samsung-gallery', '스크린샷', '3월 18일 13:02', 'g', 720, 170, -150], ['samsung-calendar', '치과 예약', '3월 22일 10:30', 'c', -470, 335, -120],
    ['app-notes', '회의록 3/14', '다음 주 시연 리허설', 'n', 20, 335, -380], ['samsung-email-blue', 'Q1_Demo_v3.pdf', '어제 오후 6:20', 'm', 470, 335, -60],
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
  tl.to(hookW.slice(0, 6), { y: 0, opacity: 1, filter: 'blur(0px)', duration: 1.1, stagger: 0.12, ease: 'expo.out' }, 0.3);
  tl.to(hookW.slice(6), { y: 0, opacity: 1, filter: 'blur(0px)', duration: 1.1, stagger: 0.15, ease: 'expo.out' }, 1.35);
  ev(0.3, 'word'); ev(1.35, 'word');
  tl.to('#hook', { y: -330, scale: 0.6, duration: 1.4, ease: 'expo.inOut' }, 2.9);
  frags.forEach((f, i) => {
    gsap.set(f.d, { x: f.x, y: f.y, z: f.z - 500, opacity: 0, xPercent: -50, yPercent: -50 });
    tl.to(f.d, { z: f.z, opacity: 1, duration: 2.2, ease: 'expo.out' }, 3.05 + (i % 7) * 0.09 + rnd() * 0.3);
  });
  gsap.set(cam3, { rotationY: 6, rotationX: 4, z: -80 });
  tl.to(cam3, { rotationY: -4, rotationX: -1, z: 60, duration: 6.6, ease: 'sine.inOut' }, 2.8);
  const clauses = ['#c1', '#c2', '#c3', '#c4'], kinds = ['k', 'g', 'c', 'n'], times = [4.1, 5.4, 6.7, 8.0];
  gsap.set(clauses, { y: 30, opacity: 0 });
  clauses.forEach((c, i) => {
    const t = times[i];
    tl.to(c, { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, t);
    ev(t, 'hl', { n: i });
    frags.forEach(f => {
      const on = f.kind === kinds[i];
      tl.to(f.d, { opacity: on ? 1 : 0.32, scale: on ? 1.07 : 0.98, duration: 0.7, ease: 'power2.out' }, t);
      tl.to(f.d.querySelector('.ring'), { opacity: on ? 1 : 0, duration: 0.5 }, t);
    });
    if (i > 0) tl.to(clauses[i - 1], { color: '#9C97AC', duration: 0.6 }, t);
  });
  tl.to(['#hook', '#where'], { opacity: 0, y: '-=24', filter: 'blur(8px)', duration: 0.6, ease: 'power2.in' }, 9.0);
  tl.to('#space', { opacity: 0, scale: 1.08, filter: 'blur(14px)', duration: 0.7, ease: 'power2.in' }, 8.95);

  /* ── 2. 구글 검색 → 확대 → Weave → 단서 엮기 → 정확한 이름으로 다시 검색 (9.6 – 21.6초) ── */
  const phone = $('#phone');
  gsap.set(phone, { autoAlpha: 0, x: 0, y: 160, scale: 0.92, transformOrigin: '50% 50%' });
  gsap.set(['#scrB', '#scrC'], { xPercent: 100 });
  gsap.set('#gres', { display: 'none' });
  tl.to(phone, { autoAlpha: 1, y: 0, scale: 1, duration: 1.2, ease: 'power3.out' }, 9.6); ev(9.6, 'rise');
  typeIn($('#sqA'), QA, 10.55, 12);
  tl.fromTo('#caretA', { opacity: 1 }, { opacity: 0, duration: 0.01, repeat: 11, yoyo: true, repeatDelay: 0.3, ease: 'none' }, 9.95);
  const qa = { x: B['#gbox'].x, y: (B['#gbox'].y + B['#kbA .wv'].y) / 2 };
  cam(12.0, camPose(1.55, qa, { x: 960, y: 540 }), 1.05);
  const pTap1 = 13.3;
  edge(13.35);
  tl.fromTo('#kbA .wv', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)' }, { boxShadow: '0 0 0 14px rgba(107,78,255,0)', duration: 0.6, ease: 'power2.out' }, 13.35);
  tl.to(phone, { x: -1400, y: 60, scale: 0.9, rotation: -4, duration: 1.1, ease: 'power3.inOut' }, 13.6);
  tl.to(phone, { autoAlpha: 0, duration: 0.3 }, 14.4);

  gsap.set(['#cA', '#cB', '#cC'], { autoAlpha: 0, scale: 0.9, y: 26 });
  gsap.set(['#tA .thr', '#tA .thr-halo', '#tB .thr', '#tB .thr-halo', '#tC .thr', '#tC .thr-halo'], { drawSVG: '0% 0%' });
  gsap.set('.pen', { autoAlpha: 0, y: 12 });
  gsap.set('.knot', { scale: 0, opacity: 0 });
  gsap.set('#scan', { y: -80, opacity: 0 });
  gsap.set('#ocrbox', { opacity: 0, scale: 1.25 });
  gsap.set('#h2', { y: 34, opacity: 0 });
  gsap.set('#pill', { autoAlpha: 0 });
  const draw = (g, t, d) => { tl.to(`${g} .thr, ${g} .thr-halo`, { drawSVG: '0% 100%', duration: d, ease: 'power2.inOut' }, t); ev(t, 'thread'); };
  const penIn = (id, t) => tl.to(id, { autoAlpha: 1, y: 0, duration: 0.6, ease: 'back.out(2)' }, t);
  const knot = (id, t) => tl.fromTo(id, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.5, ease: 'back.out(3)' }, t);
  const cardIn = (id, t) => { tl.to(id, { autoAlpha: 1, scale: 1, y: 0, duration: 0.9, ease: 'back.out(1.3)' }, t); ev(t, 'card'); };
  draw('#tA', 14.6, 0.7); penIn('#pen1', 14.7); knot('#k1', 15.25); cardIn('#cA', 15.2);
  draw('#tB', 15.8, 0.5); penIn('#pen2', 15.85); knot('#k2', 16.25); cardIn('#cB', 16.2);
  tl.to('#scan', { opacity: 1, duration: 0.1 }, 16.9).to('#scan', { y: 240, duration: 0.65, ease: 'power1.inOut' }, 16.9).to('#scan', { opacity: 0, duration: 0.2 }, 17.45);
  tl.to('#ocrbox', { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(2)' }, 17.35);
  penIn('#pen3', 17.4);
  typeIn($('#ocr'), 'BABICH SAUVIGNON BLANC', 17.45, 40, 'tick');
  draw('#tC', 18.0, 0.5); knot('#k3', 18.45); cardIn('#cC', 18.45); ev(18.5, 'answer');
  tl.fromTo('#cC', { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 0 rgba(166,124,242,.55)' },
    { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 28px rgba(166,124,242,0)', duration: 1.1, ease: 'power2.out' }, 18.55);
  tl.to('#h2', { y: 0, opacity: 1, duration: 1.0, ease: 'expo.out' }, 18.8); ev(18.8, 'word');
  const pTap2 = 19.75;
  tl.to(['#pill', '#cA', '#cB', '#threads', '.pen', '.knot', '#h2'], { autoAlpha: 0, filter: 'blur(8px)', scale: 0.97, duration: 0.6, ease: 'power2.in', stagger: 0.02 }, 20.1);
  tl.to('#cC', { x: -420, y: -150, scale: 0.55, autoAlpha: 0, filter: 'blur(4px)', duration: 0.75, ease: 'power3.in' }, 20.15);
  disc.push([t => t >= 20.15, on => resultState(on)]);
  const res = camPose(1.45, { x: B.gboxR.x, y: (B.gboxR.y + B.r1.y) / 2 }, { x: 960, y: 470 });
  tl.set(phone, { x: res.x - 1500, y: res.y + 40, scale: res.scale * 0.92, rotation: 4, autoAlpha: 1 }, 20.2);
  tl.to(phone, { x: res.x, y: res.y, scale: res.scale, rotation: 0, duration: 1.15, ease: 'power3.out' }, 20.25); ev(20.25, 'rise');
  tl.fromTo('#gbox', { boxShadow: '0 1px 6px rgba(32,33,36,.28), 0 0 0 0 rgba(26,115,232,.45)' }, { boxShadow: '0 1px 6px rgba(32,33,36,.28), 0 0 0 12px rgba(26,115,232,0)', duration: 1.0 }, 21.0);

  /* ── 3. 흩어진 기록을, 한 번에 (통화) (21.6 – 28.8초) ── */
  const L = { x: -480, y: 0, scale: 1 };
  cam(21.6, L, 1.15);
  tl.to('#scrA', { xPercent: -100, duration: 0.85, ease: 'power3.inOut' }, 21.65);
  tl.to('#scrB', { xPercent: 0, duration: 0.85, ease: 'power3.inOut' }, 21.65);
  gsap.set('.head', { autoAlpha: 0 });
  gsap.set('.head h3', { y: 30, opacity: 0 });
  const headIn = (id, t) => { tl.set(id, { autoAlpha: 1 }, t); tl.to(`${id} h3`, { y: 0, opacity: 1, duration: 1.0, ease: 'expo.out' }, t); ev(t, 'word'); };
  const headOut = (id, t) => tl.to(`${id} h3`, { y: -20, opacity: 0, duration: 0.5, ease: 'power2.in' }, t).set(id, { autoAlpha: 0 }, t + 0.55);
  headIn('#hdB', 22.1);
  const ct = { s: 48 };
  tl.to(ct, { s: 55, duration: 7.2, ease: 'none', onUpdate() { $('#ctime').textContent = `00:${String(Math.floor(ct.s)).padStart(2, '0')}`; } }, 21.6);
  const dragT = 22.75, dragD = 0.95;
  gsap.set('#wB', { y: lift + 14, autoAlpha: 0 });
  tl.set('#wB', { autoAlpha: 1 }, dragT);
  tl.to('#wB', { y: 0, duration: dragD, ease: 'power2.inOut' }, dragT);
  edge(dragT + 0.3);
  typeIn($('#qB'), 'A사 시연 관련 자료', 23.85, 12);
  gsap.set(['#b1', '#b2', '#b3'], { opacity: 0, y: 14 });
  tl.to(['#b1', '#b2', '#b3'], { opacity: 1, y: 0, duration: 0.55, stagger: 0.15, ease: 'expo.out' }, 24.75);
  gsap.set(['#fl1', '#fl2', '#fl3', '#fg', '#fk', '#frec', '#flChip'], { autoAlpha: 0, scale: 0.9, x: -30 });
  const TB = { thread: 25.15, pop: 25.5, step: 0.5 };
  ['#fl1', '#fl2', '#fl3'].forEach((k, i) => { tl.to(k, { autoAlpha: 1, scale: 1, x: 0, duration: 0.8, ease: 'back.out(1.4)' }, TB.pop + i * TB.step); ev(TB.pop + i * TB.step, 'card'); });
  // 세 기록을 잇는 보라 점선과 'A사 시연 준비' 칩 (덱 6쪽 모양)
  const xr = FLR['#fl1'].right, xl = xr + 34, ys = ['#fl1', '#fl2', '#fl3'].map(k => FLR[k].top + FLR[k].height / 2);
  dashed('#flLink', `M${xr} ${ys[0]} H${xl} V${ys[2]} H${xr} M${xl} ${ys[1]} H${xr}`, ys.map(y => ({ x: xl, y })), 27.0, 0.75);
  gsap.set('#flChip', { left: xl - 92, top: FLR['#fl1'].top - 64 });
  tl.to('#flChip', { autoAlpha: 1, scale: 1, x: 0, duration: 0.6, ease: 'back.out(2)' }, 27.25);

  /* ── 4. 떠올리기 전에, 먼저 건네요 (카톡) (28.8 – 38.4초) ── */
  tl.to(['#fl1', '#fl2', '#fl3', '#flLink', '#flChip'], { autoAlpha: 0, x: 30, duration: 0.5, ease: 'power2.in', stagger: 0.03 }, 28.45);
  headOut('#hdB', 28.5);
  tl.to('#scrB', { xPercent: -100, duration: 0.85, ease: 'power3.inOut' }, 28.85);
  tl.to('#scrC', { xPercent: 0, duration: 0.85, ease: 'power3.inOut' }, 28.85);
  disc.push([t => t >= 29.2, on => { $('#sbt').textContent = on ? '10:31' : '13:00'; }]);
  headIn('#hdC', 29.35);
  tl.fromTo('#chatIn .msg:nth-child(2) .bub', { boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { boxShadow: '0 0 0 4px rgba(107,78,255,.55)', duration: 0.4, yoyo: true, repeat: 1, repeatDelay: 0.5 }, 29.9);
  tl.to('#fg', { autoAlpha: 1, scale: 1, x: 0, duration: 0.85, ease: 'back.out(1.4)' }, 30.35); ev(30.35, 'card');
  tl.fromTo('#fg .pulse', { scale: 1, opacity: 0.9 }, { scale: 2.2, opacity: 0, duration: 1.2, repeat: 1, stagger: 0.6, ease: 'power1.out' }, 30.6);
  tl.to('#fk', { autoAlpha: 1, scale: 1, x: 0, duration: 0.85, ease: 'back.out(1.4)' }, 31.0); ev(31.0, 'card');
  const rec = FLR['#frec'], recIn = { x: rec.left - 2, y: rec.top + rec.height / 2 };
  thread('tg1', { x: FLR['#fg'].right + 2, y: FLR['#fg'].top + FLR['#fg'].height / 2 }, recIn, 31.75, 0.65, 0.5, 6);
  thread('tg2', { x: FLR['#fk'].right + 2, y: FLR['#fk'].top + FLR['#fk'].height / 2 }, recIn, 31.85, 0.65, 0.5, 6);
  tl.to('#frec', { autoAlpha: 1, scale: 1, x: 0, duration: 0.9, ease: 'back.out(1.3)' }, 32.45); ev(32.5, 'answer');
  tl.fromTo('#frec', { boxShadow: '0 30px 70px rgba(84,56,190,.22), 0 0 0 2px #D9CBFF inset, 0 0 0 0 rgba(166,124,242,.55)' },
    { boxShadow: '0 30px 70px rgba(84,56,190,.22), 0 0 0 2px #D9CBFF inset, 0 0 0 26px rgba(166,124,242,0)', duration: 1.1, ease: 'power2.out' }, 32.55);
  // 추천 문장이 키보드 위 Weave 시트로 건네진다
  gsap.set('#wC', { y: 540 }); gsap.set('#scrimC', { opacity: 0 });
  tl.fromTo('#kbC .wv', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)', scale: 1 }, { boxShadow: '0 0 0 14px rgba(107,78,255,0)', scale: 1.14, duration: 0.5, yoyo: true, repeat: 1, ease: 'power2.out' }, 33.55);
  tl.to('#wC', { y: 0, duration: 0.85, ease: 'power3.out' }, 33.7);
  tl.to('#scrimC', { opacity: 1, duration: 0.6 }, 33.7);
  edge(33.8);
  const TC = { fly: 33.75 };
  linkCards('#wC', '#wcLink', ['#c1card', '#c2card'], 34.4, 0.55, '#sgC');
  const pTap3 = 35.25;
  tl.to(['#fg', '#fk', '#tg1', '#tg2'], { autoAlpha: 0, x: 24, duration: 0.5, ease: 'power2.in', stagger: 0.04 }, 35.3);
  headOut('#hdC', 35.35);
  tl.to('#wC', { y: 540, duration: 0.6, ease: 'power3.in' }, 35.55);
  tl.to('#scrimC', { opacity: 0, duration: 0.5 }, 35.6);
  disc.push([t => t >= 35.75 && t < 36.95, on => { if (on) $('#kinTx').textContent = '엄마, 전에 먹고 싶다던 무화과시루 사갈까?'; }]);
  disc.push([t => t < 35.75 || t >= 36.95, on => { if (on) $('#kinTx').innerHTML = PH; }]);
  cam(35.6, camPose(1.32, { x: B['#chatIn'].x, y: B['.kin'].y - 150 }, { x: 960, y: 570 }), 1.0);
  const pTap4 = 36.85;
  disc.push([t => t >= 36.95, on => { $('#mSent').style.display = on ? 'flex' : 'none'; }]);
  tl.fromTo('#mSent .bub', { scale: 0.6, transformOrigin: '100% 100%', opacity: 0 }, { scale: 1, opacity: 1, duration: 0.55, ease: 'back.out(1.6)' }, 36.95); ev(36.95, 'send');
  disc.push([t => t >= 37.25, on => { $('#mReply').style.display = on ? 'flex' : 'none'; }]);
  tl.fromTo('#mReply', { y: 22, opacity: 0 }, { y: 0, opacity: 1, duration: 0.7, ease: 'expo.out' }, 37.25); ev(37.25, 'msg');

  /* ── 5. 엔드 카드 (38.4 – 41.6초) ── */
  tl.to(phone, { y: '+=70', scale: '-=0.15', autoAlpha: 0, filter: 'blur(6px)', duration: 0.5, ease: 'power3.in' }, 37.95);
  gsap.set('#logo .mark', { scale: 0.4, rotation: -30, opacity: 0 });
  gsap.set('#logo .word', { clipPath: 'inset(-50% 100% -50% -4%)', x: -30 });
  gsap.set(['#tag', '#sub'], { y: 24, opacity: 0 });
  gsap.set('#fin', { opacity: 0 });
  tl.to('#logo .mark', { scale: 1, rotation: 0, opacity: 1, duration: 1.0, ease: 'back.out(1.6)' }, 38.35); ev(38.4, 'logo');
  tl.to('#logo .word', { clipPath: 'inset(-50% -5% -50% -4%)', x: 0, duration: 1.0, ease: 'expo.out' }, 38.55);
  tl.fromTo('#logo .wv', { backgroundPosition: '170% 0%, 0% 0%' }, { backgroundPosition: '-70% 0%, 0% 0%', duration: 1.3, ease: 'power2.inOut' }, 39.1);
  tl.to('#tag', { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, 39.15); ev(39.15, 'word');
  tl.to('#sub', { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, 39.55);
  tl.to('#end', { scale: 1.02, duration: 3.3, ease: 'none' }, 38.3);
  tl.to('#fin', { opacity: 1, duration: 0.7, ease: 'power1.inOut' }, DUR - 0.7);

  tl.to('.g1', { x: 220, y: 60, duration: DUR, ease: 'none' }, 0);
  tl.to('.g2', { x: -160, y: -40, duration: DUR, ease: 'none' }, 0);
  tl.fromTo('.g3', { scale: 0.9, opacity: 0.7 }, { scale: 1.25, opacity: 1, duration: DUR, ease: 'none' }, 0);
  tl.set({}, {}, DUR);

  /* ── 손·실: 카메라·시트가 움직인 뒤의 실제 자리를 재서 맞춘다 ── */
  const at = (t, sel) => { seekAll(t); return ctr(sel); };
  const atR = (t, sel) => { seekAll(t); return rectOf(sel); };
  const p1 = at(pTap1 - 0.1, '#kbA .wv');
  const p2 = at(pTap2 - 0.1, '#btnCC');
  const p3 = at(pTap3 - 0.1, '#btnC');
  const p4 = at(pTap4 - 0.1, '#kSend');
  const h0 = at(dragT - 0.05, '#handle');
  const rb = ['#b1', '#b2', '#b3'].map(k => atR(TB.thread, k));
  const rs = atR(TC.fly + 0.85, '#sgC');
  seekAll(0);
  if (DEBUG) $('#dbg').innerHTML = [p1, p2, p3, p4, h0].map(p => `<i style="left:${p.x}px; top:${p.y}px"></i>`).join('');

  gsap.set(hand, { x: 2100, y: 1200, rotation: -12, autoAlpha: 0 });
  gsap.set(spark, { autoAlpha: 0 });
  handIn(p1.x, p1.y, pTap1); press(p1.x, p1.y, pTap1, '#kbA .wv'); handOut(pTap1 + 0.3);
  tl.fromTo('#pill', { x: p1.x - 960, y: p1.y - 162, scale: 0.22, autoAlpha: 0 }, { x: 0, y: 0, scale: 1, autoAlpha: 1, duration: 1.1, ease: 'expo.out', immediateRender: false }, 13.75);
  handIn(p2.x, p2.y, pTap2); press(p2.x, p2.y, pTap2, '#btnCC'); handOut(pTap2 + 0.3);
  handIn(h0.x, h0.y, dragT, 0.65);
  tl.to(hand, { scale: 0.92, duration: 0.1 }, dragT - 0.05);
  tl.to(hand, { y: `-=${lift}`, duration: dragD, ease: 'power2.inOut' }, dragT);
  tl.to(hand, { scale: 1, duration: 0.12 }, dragT + dragD);
  handOut(dragT + dragD + 0.1);
  // 휴대폰 안 카드 → 오른쪽 큼직한 기록 카드로 실이 뻗어 나간다
  ['#fl1', '#fl2', '#fl3'].forEach((k, i) => thread(`tb${i}`, { x: rb[i].right - 10, y: rb[i].top + rb[i].height / 2 }, { x: FLR[k].left + 2, y: FLR[k].top + FLR[k].height / 2 }, TB.thread + i * TB.step, 0.45, 0.5, 5));
  tl.to(['#tb0', '#tb1', '#tb2'], { autoAlpha: 0, duration: 0.5 }, 28.45);
  // 추천 카드가 실을 남기고 휴대폰 속 추천 자리로 날아간다
  tl.to('#frec', { x: rs.left + rs.width / 2 - (rec.left + rec.width / 2), y: rs.top + rs.height / 2 - (rec.top + rec.height / 2), scale: 0.38, autoAlpha: 0, duration: 0.8, ease: 'power3.inOut' }, TC.fly);
  tl.to(['#tg1 path', '#tg2 path'], { drawSVG: '100% 100%', duration: 0.6, ease: 'power2.in' }, TC.fly + 0.05);
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
