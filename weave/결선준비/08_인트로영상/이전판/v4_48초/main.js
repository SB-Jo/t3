/* Weave 결선 인트로 v4 — GSAP 타임라인 하나(paused)를 시간 t로 탐색해 프레임을 찍는다.
   window.__seek(t), window.__DURATION, window.__events(효과음 시점 → tools/music.py), window.__ready, window.__taps, window.__marks
   v4(2026-10-29 피드백): 시나리오마다 01·02·03 챕터 카드, 장면마다 다른 배치(01 가운데 → 02 휴대폰 오른쪽·카드 왼쪽 → 03 휴대폰 가운데·카드 양옆),
   구글 검색은 검색창 확대 → Weave 아이콘 확대, 연결선은 모두 같은 곡선(동그라미 없음), 끝 화면 더 길게.
   음악은 기존 곡(Mixkit 'Digital Clouds')을 편집해서 씀: 9.5초에 곡이 터지고(D1), 18마디 뒤 곡의 마지막 한 방에 로고(LOGO) */
gsap.registerPlugin(DrawSVGPlugin, MotionPathPlugin, CustomEase);
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const D1 = 9.5, BAR = 1.86;                           // 음악(Digital Clouds, 129 BPM)이 터지는 순간과 한 마디 길이
const LOGO = D1 + 18 * BAR;                           // 42.98초: 곡의 마지막 한 방에 로고
const DUR = LOGO + 5.0;                               // 끝 화면 5초
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
function cam(t, pose, d = 1.0, ease = 'power3.inOut') { tl.to('#phone', { ...pose, duration: d, ease }, t); }
const edge = t => tl.fromTo('#phone .frame', { boxShadow: '0 60px 110px rgba(52,30,130,.26), 0 18px 34px rgba(52,30,130,.14), 0 0 0 0 rgba(139,104,245,0)' },
  { boxShadow: '0 60px 110px rgba(52,30,130,.26), 0 18px 34px rgba(52,30,130,.14), 0 0 52px 8px rgba(139,104,245,.55)', duration: 0.45, yoyo: true, repeat: 1, repeatDelay: 0.35, ease: 'power2.out' }, t);

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

/* ── 챕터 카드 ─────────────────────────────────── */
const chapIn = (id, t) => { tl.set(id, { autoAlpha: 1 }, t); tl.fromTo(`${id} > *`, { y: 44, opacity: 0 }, { y: 0, opacity: 1, duration: 0.85, stagger: 0.11, ease: 'expo.out' }, t); };
const chapOut = (id, t) => { tl.to(`${id} > *`, { y: -26, opacity: 0, duration: 0.35, stagger: 0.04, ease: 'power2.in' }, t); tl.set(id, { autoAlpha: 0 }, t + 0.45); };
const headIn = (id, t) => { tl.set(id, { autoAlpha: 1 }, t); tl.fromTo(`${id} > *`, { y: 26, opacity: 0 }, { y: 0, opacity: 1, duration: 0.9, stagger: 0.1, ease: 'expo.out' }, t); };
const headOut = (id, t) => { tl.to(`${id} > *`, { y: -16, opacity: 0, duration: 0.45, ease: 'power2.in' }, t); tl.set(id, { autoAlpha: 0 }, t + 0.5); };

async function build() {
  const fams = ['400 20px SamsungOneKorean', '500 20px SamsungOneKorean', '700 20px SamsungOneKorean', '400 20px SamsungOne', '500 20px SamsungOne', '700 20px SamsungOne', '700 20px "Samsung Sharp Sans"'];
  await Promise.all(fams.map(f => document.fonts.load(f, '가A')));
  await document.fonts.ready;
  makeKB('#kbA'); makeKB('#kbC');
  $('#sqA').textContent = QA; $('#kinTx').innerHTML = PH;
  await Promise.all([...document.images].map(im => im.decode().catch(() => {})));

  const resultState = on => {
    $('#glogo').style.display = on ? 'none' : ''; $('.gtop').style.display = on ? 'none' : '';
    $('#gbox').style.top = on ? '104px' : ''; $('#gres').style.display = on ? '' : 'none';
    $('#kbA').style.display = on ? 'none' : ''; $('#caretA').style.display = on ? 'none' : '';
    const q = $('#sqA');
    if (on) { q.textContent = '배비치 소비뇽 블랑'; q.style.color = '#1a0dab'; q.style.fontWeight = 700; } else { q.style.color = ''; q.style.fontWeight = ''; }
  };
  const B = {};
  for (const k of ['#kbA .wv', '#gbox', '#handle', '#b1', '#b2', '#b3', '#sgC', '#btnC', '#chatIn', '.kin']) B[k] = ctr(k);
  resultState(true); B.gboxR = ctr('#gbox'); B.r1 = ctr('#r1'); resultState(false);
  const wBtop = rectOf('#wB').top, lift = B['#handle'].y - wBtop - 14;
  const FLR = {}; for (const k of ['#fl1', '#fl2', '#fl3', '#fg', '#fk']) FLR[k] = rectOf(k);
  gsap.set('.chap', { autoAlpha: 0 });
  gsap.set('.head', { autoAlpha: 0 });
  gsap.set(['#fl1', '#fl2', '#fl3', '#fg', '#fk', '#frec', '#flChip', '#flLink'], { autoAlpha: 0 });

  /* ── 도입: "그때 그 와인, 다시 사고 싶은데 / 이름이 뭐였더라?" → 어디서 찾지? (0 – 9초) ── */
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
  tl.to('#hook', { y: -330, scale: 0.6, duration: 1.4, ease: 'expo.inOut' }, 2.8);
  frags.forEach((f, i) => {
    gsap.set(f.d, { x: f.x, y: f.y, z: f.z - 500, opacity: 0, xPercent: -50, yPercent: -50 });
    tl.to(f.d, { z: f.z, opacity: 1, duration: 2.2, ease: 'expo.out' }, 2.95 + (i % 7) * 0.09 + rnd() * 0.3);
  });
  gsap.set(cam3, { rotationY: 6, rotationX: 4, z: -80 });
  tl.to(cam3, { rotationY: -4, rotationX: -1, z: 60, duration: 6.4, ease: 'sine.inOut' }, 2.7);
  const clauses = ['#c1', '#c2', '#c3', '#c4'], kinds = ['k', 'g', 'c', 'n'], times = [3.9, 5.1, 6.3, 7.5];
  gsap.set(clauses, { y: 30, opacity: 0 });
  clauses.forEach((c, i) => {
    const t = times[i];
    tl.to(c, { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, t);
    frags.forEach(f => {
      const on = f.kind === kinds[i];
      tl.to(f.d, { opacity: on ? 1 : 0.32, scale: on ? 1.07 : 0.98, duration: 0.7, ease: 'power2.out' }, t);
      tl.to(f.d.querySelector('.ring'), { opacity: on ? 1 : 0, duration: 0.5 }, t);
    });
    if (i > 0) tl.to(clauses[i - 1], { color: '#9C97AC', duration: 0.6 }, t);
  });
  tl.to(['#hook', '#where'], { opacity: 0, y: '-=24', filter: 'blur(8px)', duration: 0.6, ease: 'power2.in' }, 8.35);
  tl.to('#space', { opacity: 0, scale: 1.08, filter: 'blur(14px)', duration: 0.65, ease: 'power2.in' }, 8.3);

  /* ── 01 단서로 찾기 (9.05 – 23.55초) ── */
  chapIn('#ch1', 9.05); chapOut('#ch1', 10.2);
  const phone = $('#phone');
  gsap.set(phone, { autoAlpha: 0, x: 0, y: 160, scale: 0.92, transformOrigin: '50% 50%' });
  gsap.set(['#scrB', '#scrC'], { xPercent: 100 });
  gsap.set('#gres', { display: 'none' });
  tl.to(phone, { autoAlpha: 1, y: 0, scale: 1, duration: 1.1, ease: 'power3.out' }, 10.5);
  // 검색할 때는 검색창을 크게
  cam(11.2, camPose(2.3, B['#gbox'], { x: 960, y: 430 }), 0.9);
  typeIn($('#sqA'), QA, 12.0, 12);
  tl.fromTo('#caretA', { opacity: 1 }, { opacity: 0, duration: 0.01, repeat: 9, yoyo: true, repeatDelay: 0.3, ease: 'none' }, 10.9);
  // Weave를 누를 때는 키보드의 Weave 아이콘 쪽을 크게
  cam(13.65, camPose(2.3, { x: B['#kbA .wv'].x + 90, y: B['#kbA .wv'].y }, { x: 960, y: 600 }), 0.85);
  const pTap1 = 14.75;
  edge(14.8);
  tl.fromTo('#kbA .wv', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)' }, { boxShadow: '0 0 0 14px rgba(107,78,255,0)', duration: 0.6, ease: 'power2.out' }, 14.8);
  tl.to(phone, { x: -1500, y: 60, scale: 1.4, rotation: -4, duration: 1.05, ease: 'power3.inOut' }, 15.1);
  tl.to(phone, { autoAlpha: 0, duration: 0.3 }, 15.85);

  gsap.set(['#cA', '#cB', '#cC'], { autoAlpha: 0, scale: 0.9, y: 26 });
  gsap.set(['#tA .thr', '#tA .thr-halo', '#tB .thr', '#tB .thr-halo', '#tC .thr', '#tC .thr-halo'], { drawSVG: '0% 0%' });
  gsap.set('.pen', { autoAlpha: 0, y: 12 });
  gsap.set('#scan', { y: -80, opacity: 0 });
  gsap.set('#ocrbox', { opacity: 0, scale: 1.25 });
  gsap.set('#h2', { y: 34, opacity: 0 });
  gsap.set('#pill', { autoAlpha: 0 });
  const draw = (g, t, d) => tl.to(`${g} .thr, ${g} .thr-halo`, { drawSVG: '0% 100%', duration: d, ease: 'power2.inOut' }, t);
  const penIn = (id, t) => tl.to(id, { autoAlpha: 1, y: 0, duration: 0.6, ease: 'back.out(2)' }, t);
  const cardIn = (id, t) => tl.to(id, { autoAlpha: 1, scale: 1, y: 0, duration: 0.9, ease: 'back.out(1.3)' }, t);
  draw('#tA', 16.1, 0.7); penIn('#pen1', 16.2); cardIn('#cA', 16.7);
  draw('#tB', 17.3, 0.6); penIn('#pen2', 17.35); cardIn('#cB', 17.7);
  tl.to('#scan', { opacity: 1, duration: 0.1 }, 18.35).to('#scan', { y: 240, duration: 0.65, ease: 'power1.inOut' }, 18.35).to('#scan', { opacity: 0, duration: 0.2 }, 18.9);
  tl.to('#ocrbox', { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(2)' }, 18.8);
  penIn('#pen3', 18.85);
  typeIn($('#ocr'), 'BABICH SAUVIGNON BLANC', 18.9, 40, null);
  draw('#tC', 19.45, 0.6); cardIn('#cC', 19.9); ev(19.95, 'answer');
  tl.fromTo('#cC', { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 0 rgba(166,124,242,.55)' },
    { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 28px rgba(166,124,242,0)', duration: 1.1, ease: 'power2.out' }, 20.0);
  tl.to('#h2', { y: 0, opacity: 1, duration: 1.0, ease: 'expo.out' }, 17.1);   // 문장은 사슬이 엮이는 동안 계속 보이게
  const pTap2 = 21.2;
  tl.to(['#pill', '#cA', '#cB', '#threads', '.pen', '#h2'], { autoAlpha: 0, filter: 'blur(8px)', scale: 0.97, duration: 0.6, ease: 'power2.in', stagger: 0.02 }, 21.55);
  tl.to('#cC', { x: -420, y: -150, scale: 0.55, autoAlpha: 0, filter: 'blur(4px)', duration: 0.75, ease: 'power3.in' }, 21.6);
  disc.push([t => t >= 21.6, on => resultState(on)]);
  const res = camPose(1.45, { x: B.gboxR.x, y: (B.gboxR.y + B.r1.y) / 2 }, { x: 960, y: 470 });
  tl.set(phone, { x: res.x - 1500, y: res.y + 40, scale: res.scale * 0.92, rotation: 4, autoAlpha: 1 }, 21.65);
  tl.to(phone, { x: res.x, y: res.y, scale: res.scale, rotation: 0, duration: 1.15, ease: 'power3.out' }, 21.7);
  tl.fromTo('#gbox', { boxShadow: '0 1px 6px rgba(32,33,36,.28), 0 0 0 0 rgba(26,115,232,.45)' }, { boxShadow: '0 1px 6px rgba(32,33,36,.28), 0 0 0 12px rgba(26,115,232,0)', duration: 1.0 }, 22.45);

  /* ── 02 한 번에 모아 보기 (23.45 – 32.05초): 휴대폰 오른쪽, 큰 카드 왼쪽 ── */
  tl.to(phone, { x: '-=420', autoAlpha: 0, filter: 'blur(6px)', duration: 0.45, ease: 'power3.in' }, 23.1);
  chapIn('#ch2', 23.45); chapOut('#ch2', 24.45);
  tl.set('#scrA', { xPercent: -100 }, 23.6); tl.set('#scrB', { xPercent: 0 }, 23.6);
  const R = { x: 470, y: 0, scale: 1 };
  tl.set(phone, { x: 1400, y: 0, scale: 1, rotation: 0, filter: 'blur(0px)', autoAlpha: 1 }, 24.45);
  tl.to(phone, { x: R.x, duration: 1.05, ease: 'power3.out' }, 24.55);
  headIn('#hdB', 24.8);
  const ct = { s: 48 };
  tl.to(ct, { s: 55, duration: 7.5, ease: 'none', onUpdate() { $('#ctime').textContent = `00:${String(Math.floor(ct.s)).padStart(2, '0')}`; } }, 24.55);
  const dragT = 25.85, dragD = 0.95;
  gsap.set('#wB', { y: lift + 14, autoAlpha: 0 });
  tl.set('#wB', { autoAlpha: 1 }, dragT);
  tl.to('#wB', { y: 0, duration: dragD, ease: 'power2.inOut' }, dragT);
  edge(dragT + 0.3);
  typeIn($('#qB'), 'A사 시연 관련 자료', 26.95, 12);
  gsap.set(['#b1', '#b2', '#b3'], { opacity: 0, y: 14 });
  tl.to(['#b1', '#b2', '#b3'], { opacity: 1, y: 0, duration: 0.55, stagger: 0.15, ease: 'expo.out' }, 27.75);
  const TB = { thread: 28.15, pop: 28.5, step: 0.45 };
  ['#fl1', '#fl2', '#fl3'].forEach((k, i) => {
    gsap.set(k, { autoAlpha: 0, scale: 0.92, x: 40 });
    tl.to(k, { autoAlpha: 1, scale: 1, x: 0, duration: 0.8, ease: 'back.out(1.4)' }, TB.pop + i * TB.step);
  });
  // 세 기록을 하나로 엮는 곡선(카드 왼쪽 가장자리를 지나는 한 가닥)
  const L1 = ['#fl1', '#fl2', '#fl3'].map(k => ({ x: FLR[k].left + 2, y: FLR[k].top + FLR[k].height / 2 }));
  const xb = L1[0].x - 70;
  curve('flc', `M${L1[0].x} ${L1[0].y} C ${xb} ${L1[0].y}, ${xb} ${L1[1].y}, ${L1[1].x} ${L1[1].y} C ${xb} ${L1[1].y}, ${xb} ${L1[2].y}, ${L1[2].x} ${L1[2].y}`, 29.95, 0.8, 5.5);
  gsap.set('#flChip', { left: FLR['#fl1'].left, top: FLR['#fl1'].top - 52, x: 0, scale: 0.85 });
  tl.to('#flChip', { autoAlpha: 1, scale: 1, duration: 0.6, ease: 'back.out(2)' }, 30.15);

  /* ── 03 먼저 건네기 (32.3 – 42.5초): 휴대폰 가운데, 큰 카드 양옆 ── */
  tl.to(['#fl1', '#fl2', '#fl3', '#flChip', '#flc'], { autoAlpha: 0, x: -30, duration: 0.45, ease: 'power2.in', stagger: 0.03 }, 31.95);
  headOut('#hdB', 31.95);
  tl.to(phone, { x: '+=420', autoAlpha: 0, filter: 'blur(6px)', duration: 0.45, ease: 'power3.in' }, 32.0);
  chapIn('#ch3', 32.3); chapOut('#ch3', 33.3);
  tl.set('#scrB', { xPercent: -100 }, 32.6); tl.set('#scrC', { xPercent: 0 }, 32.6);
  disc.push([t => t >= 32.6, on => { $('#sbt').textContent = on ? '10:31' : '13:00'; }]);
  const C3 = { x: 0, y: 70, scale: 0.86 };
  tl.set(phone, { x: 0, y: 760, scale: 0.86, filter: 'blur(0px)', autoAlpha: 1 }, 33.5);
  tl.to(phone, { y: C3.y, duration: 1.05, ease: 'power3.out' }, 33.6);
  headIn('#hdC', 33.8);
  tl.fromTo('#chatIn .msg:nth-child(2) .bub', { boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { boxShadow: '0 0 0 4px rgba(107,78,255,.55)', duration: 0.4, yoyo: true, repeat: 1, repeatDelay: 0.5 }, 34.4);
  gsap.set(['#fg', '#fk'], { autoAlpha: 0, scale: 0.92 });
  gsap.set('#fg', { x: -40 }); gsap.set('#fk', { x: 40 });
  tl.to('#fg', { autoAlpha: 1, scale: 1, x: 0, duration: 0.85, ease: 'back.out(1.4)' }, 34.8);
  tl.fromTo('#fg .pulse', { scale: 1, opacity: 0.9 }, { scale: 2.2, opacity: 0, duration: 1.2, repeat: 1, stagger: 0.6, ease: 'power1.out' }, 35.05);
  tl.to('#fk', { autoAlpha: 1, scale: 1, x: 0, duration: 0.85, ease: 'back.out(1.4)' }, 35.4);
  const TC = { thread: 36.05 };
  gsap.set('#wC', { y: 540 }); gsap.set('#scrimC', { opacity: 0 });
  tl.fromTo('#kbC .wv', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)', scale: 1 }, { boxShadow: '0 0 0 16px rgba(107,78,255,0)', scale: 1.18, duration: 0.5, yoyo: true, repeat: 1, ease: 'power2.out' }, 36.65);
  tl.to('#wC', { y: 0, duration: 0.85, ease: 'power3.out' }, 36.8);
  tl.to('#scrimC', { opacity: 1, duration: 0.6 }, 36.8);
  edge(36.9);
  tl.to(['#fg', '#fk'], { autoAlpha: 0, duration: 0.5, ease: 'power2.in' }, 37.5);
  headOut('#hdC', 37.5);
  const sugC = { x: B['#sgC'].x, y: (B['#sgC'].y + B['#btnC'].y) / 2 };
  cam(37.65, camPose(1.7, sugC, { x: 960, y: 540 }), 1.0);
  const pTap3 = 39.2;
  tl.to('#wC', { y: 540, duration: 0.6, ease: 'power3.in' }, 39.5);
  tl.to('#scrimC', { opacity: 0, duration: 0.5 }, 39.55);
  disc.push([t => t >= 39.8 && t < 40.8, on => { if (on) $('#kinTx').textContent = '엄마, 전에 먹고 싶다던 무화과시루 사갈까?'; }]);
  disc.push([t => t < 39.8 || t >= 40.8, on => { if (on) $('#kinTx').innerHTML = PH; }]);
  cam(39.6, camPose(1.3, { x: B['#chatIn'].x, y: B['.kin'].y - 150 }, { x: 960, y: 560 }), 0.9);
  const pTap4 = 40.7;
  disc.push([t => t >= 40.8, on => { $('#mSent').style.display = on ? 'flex' : 'none'; }]);
  tl.fromTo('#mSent .bub', { scale: 0.6, transformOrigin: '100% 100%', opacity: 0 }, { scale: 1, opacity: 1, duration: 0.55, ease: 'back.out(1.6)' }, 40.8);
  disc.push([t => t >= 41.3, on => { $('#mReply').style.display = on ? 'flex' : 'none'; }]);
  tl.fromTo('#mReply', { y: 22, opacity: 0 }, { y: 0, opacity: 1, duration: 0.7, ease: 'expo.out' }, 41.3); ev(41.3, 'msg');

  /* ── 끝 화면 (42.98 – 47.98초): 로고·문구를 충분히 읽을 수 있게 ── */
  tl.to(phone, { y: '+=70', scale: '-=0.15', autoAlpha: 0, filter: 'blur(6px)', duration: 0.5, ease: 'power3.in' }, 42.5);
  gsap.set('#logo .mark', { scale: 0.4, rotation: -30, opacity: 0 });
  gsap.set('#logo .word', { clipPath: 'inset(-50% 100% -50% -4%)', x: -30 });
  gsap.set(['#tag', '#sub'], { y: 24, opacity: 0 });
  gsap.set('#fin', { opacity: 0 });
  tl.to('#logo .mark', { scale: 1, rotation: 0, opacity: 1, duration: 1.0, ease: 'back.out(1.6)' }, LOGO - 0.05); ev(LOGO, 'logo');
  tl.to('#logo .word', { clipPath: 'inset(-50% -5% -50% -4%)', x: 0, duration: 1.0, ease: 'expo.out' }, LOGO + 0.25);
  tl.fromTo('#logo .wv', { backgroundPosition: '170% 0%, 0% 0%' }, { backgroundPosition: '-70% 0%, 0% 0%', duration: 1.3, ease: 'power2.inOut' }, LOGO + 0.8);
  tl.to('#tag', { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, LOGO + 0.9);
  tl.to('#sub', { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, LOGO + 1.4);
  tl.to('#end', { scale: 1.02, duration: DUR - LOGO, ease: 'none' }, LOGO);
  tl.to('#fin', { opacity: 1, duration: 1.2, ease: 'power1.inOut' }, DUR - 1.2);

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
  const wvC = at(TC.thread, '#kbC .wv');
  const frC = atR(TC.thread, '#phone .frame');
  seekAll(0);
  if (DEBUG) $('#dbg').innerHTML = [p1, p2, p3, p4, h0, wvC].map(p => `<i style="left:${p.x}px; top:${p.y}px"></i>`).join('');

  gsap.set(hand, { x: 2100, y: 1200, rotation: -12, autoAlpha: 0 });
  gsap.set(spark, { autoAlpha: 0 });
  handIn(p1.x, p1.y, pTap1); press(p1.x, p1.y, pTap1, '#kbA .wv'); handOut(pTap1 + 0.3);
  tl.fromTo('#pill', { x: p1.x - 960, y: p1.y - 162, scale: 0.3, autoAlpha: 0 }, { x: 0, y: 0, scale: 1, autoAlpha: 1, duration: 1.1, ease: 'expo.out', immediateRender: false }, 15.25);
  handIn(p2.x, p2.y, pTap2); press(p2.x, p2.y, pTap2, '#btnCC'); handOut(pTap2 + 0.3);
  handIn(h0.x, h0.y, dragT, 0.65);
  tl.to(hand, { scale: 0.92, duration: 0.1 }, dragT - 0.05);
  tl.to(hand, { y: `-=${lift}`, duration: dragD, ease: 'power2.inOut' }, dragT);
  tl.to(hand, { scale: 1, duration: 0.12 }, dragT + dragD);
  handOut(dragT + dragD + 0.1);
  // 02: 휴대폰 속 카드 → 왼쪽 큰 카드로 곡선이 뻗어 나간다
  const tb = ['#fl1', '#fl2', '#fl3'].map((k, i) => curve(`tb${i}`, bez({ x: rb[i].left + 8, y: rb[i].top + rb[i].height / 2 }, { x: FLR[k].right - 2, y: FLR[k].top + FLR[k].height / 2 }, 0.55), TB.thread + i * TB.step, 0.5));
  tl.to(tb, { autoAlpha: 0, duration: 0.45 }, 31.95);
  // 03: 위치(GPS)·가족 단체방 카드 → 키보드의 Weave로 곡선이 모인다
  const ga = { x: FLR['#fg'].right - 2, y: FLR['#fg'].top + FLR['#fg'].height / 2 }, ka = { x: FLR['#fk'].left + 2, y: FLR['#fk'].top + FLR['#fk'].height / 2 };
  const kR = { x: frC.right - 6, y: wvC.y };            // 오른쪽 실은 휴대폰 오른쪽 가장자리, 키보드 도구줄 높이로 들어간다
  const tg = [curve('tg1', bez(ga, wvC, 0.6), TC.thread, 0.6, 6), curve('tg2', bez(ka, kR, 0.6), TC.thread + 0.1, 0.6, 6)];
  tl.to(tg, { autoAlpha: 0, duration: 0.5 }, 37.5);
  handIn(p3.x, p3.y, pTap3); press(p3.x, p3.y, pTap3, '#btnC'); handOut(pTap3 + 0.3);
  handIn(p4.x, p4.y, pTap4, 0.6); press(p4.x, p4.y, pTap4, '#kSend'); handOut(pTap4 + 0.3);

  window.__events = EV.sort((a, b) => a.t - b.t);
  window.__taps = { p1, p2, p3, p4, h0, lift, wvC };
  window.__marks = { logo: LOGO, drop: D1, bar: BAR, ch1: 9.05, ch2: 23.45, ch3: 32.3 };
  seekAll(0);
  return true;
}

window.__DURATION = DUR;
window.__seek = t => seekAll(t);
window.__ready = build();
