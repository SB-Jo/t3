/* Weave 결선 인트로 — GSAP 타임라인 하나(paused)를 시간 t로 탐색해 프레임을 찍는다.
   window.__seek(t), window.__DURATION, window.__events(효과음 시점 → tools/music.py), window.__ready */
gsap.registerPlugin(DrawSVGPlugin, MotionPathPlugin, CustomEase);
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const DUR = 28;
const tl = gsap.timeline({ paused: true, defaults: { ease: 'power3.out', duration: 0.8 } });
const EV = [];
const ev = (t, type, o = {}) => EV.push({ t: Math.round(t * 1000) / 1000, type, ...o });
let seed = 20261029;
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
CustomEase.create('soft', 'M0,0 C0.22,0.9 0.32,1 1,1');
CustomEase.create('swing', 'M0,0 C0.65,0 0.25,1 1,1');

/* ── 손으로 누르기 ─────────────────────────────── */
const hand = $('#hand'), spark = $('#spark'), TIP = { x: 42, y: 5 };
const sparks = $$('#spark .sp');
gsap.set(hand, { x: 2100, y: 1200, rotation: -12, autoAlpha: 0 });
gsap.set(spark, { autoAlpha: 0 });
function handIn(x, y, t, d = 0.5) {
  tl.set(hand, { x: x - TIP.x + 150, y: y - TIP.y + 210, autoAlpha: 0 }, t - d);
  tl.to(hand, { x: x - TIP.x, y: y - TIP.y, autoAlpha: 1, duration: d, ease: 'power3.out' }, t - d);
}
function handMove(x, y, t, d = 0.35) { tl.to(hand, { x: x - TIP.x, y: y - TIP.y, duration: d, ease: 'power2.inOut' }, t - d); }
function handOut(t) { tl.to(hand, { x: '+=170', y: '+=230', autoAlpha: 0, duration: 0.45, ease: 'power2.in' }, t); }
function press(x, y, t, target) {
  tl.to(hand, { scale: 0.92, duration: 0.07, ease: 'power2.out' }, t - 0.05)
    .to(hand, { scale: 1, duration: 0.2, ease: 'power2.out' }, t + 0.04);
  tl.set(spark, { x, y, autoAlpha: 1 }, t)
    .fromTo(sparks, { drawSVG: '0% 0%', opacity: 1 }, { drawSVG: '0% 100%', duration: 0.18, ease: 'power2.out' }, t)
    .to(sparks, { drawSVG: '100% 100%', duration: 0.24, ease: 'power2.in' }, t + 0.2)
    .set(spark, { autoAlpha: 0 }, t + 0.46);
  if (target) tl.to(target, { scale: 0.965, duration: 0.07, yoyo: true, repeat: 1, ease: 'power1.inOut' }, t - 0.03);
  ev(t, 'tap');
}

/* ── 글자 입력 ─────────────────────────────────── */
function typeIn(el, text, t0, cps = 16, sfx = 'key') {
  const ch = [...text], times = [];
  let t = t0;
  for (const c of ch) { times.push(t); t += (1 / cps) * (0.72 + rnd() * 0.56) * (c === ' ' ? 0.55 : 1); }
  const d = t - t0, o = { p: 0 };
  el.textContent = '';
  tl.to(o, { p: 1, duration: d, ease: 'none', onUpdate() {
    const now = t0 + o.p * d; let n = 0; while (n < ch.length && times[n] <= now + 1e-6) n++;
    el.textContent = ch.slice(0, n).join('');
  } }, t0);
  if (sfx) times.forEach((tt, i) => ch[i] !== ' ' && ev(tt, sfx));
  return t;
}
const center = el => { const r = (typeof el === 'string' ? $(el) : el).getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2, r }; };

/* ── 흩어진 기록 조각 ───────────────────────────── */
const FR = [
  ['samsung-calendar', '지은 집들이', '3월 15일 (일) 18:00'], ['samsung-gallery', 'IMG_2481.jpg', '3월 15일 20:14', 1],
  ['app-kakao', '지은', '다들 와줘서 고마워 ㅎㅎ'], ['app-notes', 'A사 시연 준비회의', '설치 → 연결 → 사용 예시'],
  ['samsung-email-blue', 'A사 시연 자료 중 내일 수정할 것', '나에게 보냄 · 어제'], ['app-kakao', '가족 단체방', '성심당 무화과시루 먹고 싶다'],
  ['samsung-calendar', '치과 예약', '3월 22일 10:30'], ['app-map', '대전역', '최근 방문'],
  ['app-kakao', '재웅 선배', '내일 8:40 1층 로비'], ['app-notes', '장보기', '우유, 계란, 무화과'],
  ['samsung-gallery', '스크린샷', '3월 18일 13:02'], ['samsung-email-blue', '[예약 확인] 오사카 호텔', '2월 27일'],
  ['app-kakao', '엄마', '출장 다녀오느라 고생했어!'], ['samsung-calendar', '팀 회식', '3월 20일 19:00'],
  ['app-notes', '와인 메모', '달지 않은 화이트?'], ['samsung-gallery', 'IMG_2475.jpg', '3월 15일 19:52', 1],
  ['app-kakao', '민호', '그 와인 맛있더라'], ['samsung-email-blue', 'Q1_Demo_v3.pdf', '어제 오후 6:20'],
  ['samsung-calendar', '엄마 생신', '4월 2일'], ['app-map', '성심당 대전역점', '저장한 장소'],
  ['app-notes', '회의록 3/14', '다음 주 시연 리허설'], ['app-kakao', '지은', '사진 보내줄게!'],
  ['samsung-gallery', 'IMG_2502.jpg', '3월 16일 11:20', 1], ['samsung-calendar', '오사카 여행', '2월 28일 – 3월 2일'],
];
const cam = $('#cam'), frags = [];
const slots = [];
for (let r = 0; r < 4; r++) for (let c = 0; c < 6; c++) slots.push([-840 + c * 336, -400 + r * 196 + (c % 2) * 52]);
FR.forEach((f, i) => {
  const d = document.createElement('div');
  d.className = 'frag kr';
  d.innerHTML = `<img class="ic" src="assets/icons/${f[0]}.png" alt="">${f[3] ? '<img class="ph" src="assets/img/ux2-wine-photo.png" alt="">' : ''}<div><div class="t">${f[1]}</div><div class="m">${f[2]}</div></div>`;
  cam.appendChild(d);
  const [sx, sy] = slots[(i * 7 + 3) % slots.length];
  const z = -1050 + rnd() * 1120;
  const x = sx + (rnd() - 0.5) * 120, y = sy + (rnd() - 0.5) * 90;
  frags.push({ d, x, y, z });
});

/* ── 1. 질문 · 흩어진 기록 (0 – 6초) ───────────────── */
const hookW = $$('#hook .w');
gsap.set(hookW, { y: 60, opacity: 0, filter: 'blur(12px)' });
tl.to(hookW.slice(0, 3), { y: 0, opacity: 1, filter: 'blur(0px)', duration: 0.9, stagger: 0.11, ease: 'expo.out' }, 0.25);
tl.to(hookW.slice(3), { y: 0, opacity: 1, filter: 'blur(0px)', duration: 0.9, stagger: 0.13, ease: 'expo.out' }, 1.0);
ev(0.25, 'word'); ev(0.36, 'word'); ev(0.47, 'word'); ev(1.0, 'word2'); ev(1.13, 'word2');
tl.to('#hook', { y: -120, scale: 0.9, opacity: 0, filter: 'blur(14px)', duration: 0.75, ease: 'power2.in' }, 2.0);

frags.forEach((f, i) => {
  gsap.set(f.d, { x: f.x, y: f.y, z: f.z - 900, opacity: 0, xPercent: -50, yPercent: -50, filter: `blur(${Math.min(2.4, Math.max(0, -f.z / 520)).toFixed(2)}px)` });
  tl.to(f.d, { z: f.z, opacity: 1, duration: 1.35, ease: 'expo.out' }, 2.05 + (i % 8) * 0.06 + rnd() * 0.32);
});
ev(2.05, 'whooshIn');
gsap.set(cam, { rotationY: 9, rotationX: 5, z: -120 });
tl.to(cam, { rotationY: -5, rotationX: -1.5, z: 230, duration: 4.2, ease: 'none' }, 2.0);
gsap.set('#stats .stat', { y: 26, opacity: 0 });
tl.to('#stats .stat', { y: 0, opacity: 1, duration: 0.6, stagger: 0.14, ease: 'back.out(1.6)' }, 2.6);
ev(2.6, 'pop', { n: 0 }); ev(2.74, 'pop', { n: 1 }); ev(2.88, 'pop', { n: 2 });
tl.to('#stats .stat', { y: -14, opacity: 0, duration: 0.4, stagger: 0.05, ease: 'power2.in' }, 3.85);
gsap.set('#statband', { opacity: 0 });
tl.to('#statband', { opacity: 1, duration: 0.5 }, 2.45).to('#statband', { opacity: 0, duration: 0.5 }, 3.9);
tl.to('#space', { opacity: 0.32, filter: 'blur(5px)', duration: 0.6, ease: 'power2.out' }, 3.9);
gsap.set('#quote span', { y: 40, opacity: 0 });
tl.to('#quote .q1', { y: 0, opacity: 1, duration: 0.7, ease: 'expo.out' }, 4.05);
tl.to('#quote .q2', { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, 4.45);
ev(4.05, 'word2'); ev(4.45, 'sigh');
tl.to('#quote', { opacity: 0, scale: 0.96, filter: 'blur(6px)', duration: 0.4, ease: 'power2.in' }, 5.55);
tl.to('#space', { opacity: 0, scale: 1.06, filter: 'blur(14px)', duration: 0.55, ease: 'power2.in' }, 5.6);

/* ── 2. 엮기 (6 – 12초) ─────────────────────────── */
const pill = $('#pill'), sendB = $('#pill .send');
gsap.set(pill, { autoAlpha: 0, scale: 0.9, y: 368 });
tl.to(pill, { autoAlpha: 1, scale: 1, y: 350, duration: 0.7, ease: 'back.out(1.5)' }, 6.0);
tl.to(pill, { y: 0, duration: 0.6, ease: 'expo.inOut' }, 7.12);
ev(6.0, 'drop');
const caret = $('#pill .caret');
tl.fromTo(caret, { opacity: 1 }, { opacity: 0, duration: 0.01, repeat: 9, yoyo: true, repeatDelay: 0.26, ease: 'none' }, 6.95);
typeIn($('#qtx'), '지은이네 집들이 때 마신 와인', 6.12, 19);
const sendC = center(sendB); sendC.y += 350;
handIn(sendC.x, sendC.y, 6.95, 0.45);
press(sendC.x, sendC.y, 7.02, sendB);
handOut(7.25);

const cards = ['#cA', '#cB', '#cC'];
gsap.set(cards, { autoAlpha: 0, scale: 0.9, y: 24 });
gsap.set(['#tA .thr', '#tA .thr-halo', '#tB .thr', '#tB .thr-halo', '#tC .thr', '#tC .thr-halo'], { drawSVG: '0% 0%' });
gsap.set('.pen', { clipPath: 'inset(-10% 100% -10% -4%)' });
gsap.set('.knot', { scale: 0, opacity: 0 });
const draw = (g, t, d) => { tl.to(`${g} .thr, ${g} .thr-halo`, { drawSVG: '0% 100%', duration: d, ease: 'power2.inOut' }, t); ev(t, 'thread', { d }); };
const penIn = (id, t) => tl.to(id, { clipPath: 'inset(-10% -4% -10% -4%)', duration: 0.55, ease: 'power1.inOut' }, t);
const knot = (id, t) => tl.fromTo(id, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.45, ease: 'back.out(3)' }, t);
const cardIn = (id, t) => tl.to(id, { autoAlpha: 1, scale: 1, y: 0, duration: 0.75, ease: 'back.out(1.4)' }, t);

draw('#tA', 7.7, 0.46); penIn('#pen1', 7.78); knot('#k1', 8.1); cardIn('#cA', 8.04); ev(8.1, 'pop', { n: 0 });
draw('#tB', 8.3, 0.38); penIn('#pen2', 8.32); knot('#k2', 8.66); cardIn('#cB', 8.62); ev(8.66, 'pop', { n: 1 });
gsap.set('#scan', { y: -80, opacity: 0 });
gsap.set('#ocrbox', { opacity: 0, scale: 1.25 });
tl.to('#scan', { opacity: 1, duration: 0.08 }, 9.05).to('#scan', { y: 240, duration: 0.5, ease: 'power1.inOut' }, 9.05).to('#scan', { opacity: 0, duration: 0.15 }, 9.48);
ev(9.05, 'scan');
tl.to('#ocrbox', { opacity: 1, scale: 1, duration: 0.35, ease: 'back.out(2)' }, 9.4);
penIn('#pen3', 9.44);
typeIn($('#ocr'), 'BABICH SAUVIGNON BLANC', 9.5, 56, 'tick');
draw('#tC', 9.96, 0.4); knot('#k3', 10.32); cardIn('#cC', 10.3); ev(10.32, 'answer');
tl.fromTo('#cC', { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 0 rgba(166,124,242,.55)' },
  { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 26px rgba(166,124,242,0)', duration: 0.9, ease: 'power2.out' }, 10.4);
gsap.set('#h2', { y: 34, opacity: 0 });
tl.to('#h2', { y: 0, opacity: 1, duration: 0.8, ease: 'expo.out' }, 10.6); ev(10.6, 'word2');

const S2 = ['#pill', '#cA', '#cB', '#threads', '.pen', '.knot', '#h2'];
tl.to(S2, { autoAlpha: 0, filter: 'blur(8px)', scale: 0.97, duration: 0.5, ease: 'power2.in', stagger: 0.02 }, 11.5);
tl.to('#cC', { x: -150, y: -20, scale: 0.86, autoAlpha: 0, filter: 'blur(4px)', duration: 0.6, ease: 'power3.in' }, 11.55);
ev(11.55, 'whoosh');

/* ── 3. 휴대폰 UX (12 – 24초) ───────────────────── */
// 클릭 위치는 움직이기 전(기본 배치)에서 잰다
const P = { btnA: center('#btnA'), handle: center('#handle'), btnC: center('#btnC'), kSend: center('#kSend'),
  sqA: center('#scrA .sbar'), b2: center('#b2'), sgC: center('#wC .sg'), popA: center('#popA'), popB: center('#popB'), popC: center('#popC') };

// 키보드
const KB = [['ㅂ','ㅈ','ㄷ','ㄱ','ㅅ','ㅛ','ㅕ','ㅑ','ㅐ','ㅔ'], ['ㅁ','ㄴ','ㅇ','ㄹ','ㅎ','ㅗ','ㅓ','ㅏ','ㅣ'], ['⇧','ㅋ','ㅌ','ㅊ','ㅍ','ㅠ','ㅜ','ㅡ','⌫'], ['!#1','한/영','한국어','.','↗']];
$('#kbC').innerHTML = `<div class="tb"><span class="wv"><img src="assets/icons/weave-spool-6B4EFF.png" alt=""></span><svg><use href="#i-emo"/></svg><svg><use href="#i-tr"/></svg><svg><use href="#i-clip"/></svg><svg><use href="#i-gear"/></svg><span style="margin-left:auto">닫기 ⌄</span></div>` +
  KB.map((row, r) => `<div class="krow">${row.map(k => {
    const cls = ['k'];
    if (['⇧', '⌫', '!#1', '한/영'].includes(k)) cls.push('g', 'w2');
    if (k === '한국어') cls.push('sp');
    if (k === '↗') cls.push('snd', 'w2');
    return `<span class="${cls.join(' ')}">${k === '↗' ? '<svg width="18" height="18"><use href="#i-plane"/></svg>' : k}</span>`;
  }).join('')}</div>`).join('');

const phone = $('#phone');
gsap.set(phone, { autoAlpha: 0, x: 380, rotationY: -22, transformPerspective: 1800 });
gsap.set(['#scrB', '#scrC'], { xPercent: 100 });
gsap.set('#wB', { y: 640 });
gsap.set('#wC', { y: 520 });
gsap.set('#scrimC', { opacity: 0 });
gsap.set(['#r1', '#r2', '#r3'], { y: 16, opacity: 0 });
gsap.set(['#b1', '#b2', '#b3'], { y: 16, opacity: 0 });
gsap.set('.head', { autoAlpha: 0 });
gsap.set('.head > *', { y: 26, opacity: 0 });
gsap.set('.pop', { autoAlpha: 0, x: 36, scale: 0.94 });
gsap.set('#popA .old s', { scaleX: 0 });
gsap.set('#popAnew', { y: 18, opacity: 0 });

const headIn = (id, t) => { tl.set(id, { autoAlpha: 1 }, t); tl.to(`${id} > *`, { y: 0, opacity: 1, duration: 0.7, stagger: 0.09, ease: 'expo.out' }, t); };
const headOut = (id, t) => tl.to(`${id} > *`, { y: -18, opacity: 0, duration: 0.35, stagger: 0.04, ease: 'power2.in' }, t).set(id, { autoAlpha: 0 }, t + 0.5);
const popIn = (id, t) => { tl.to(id, { autoAlpha: 1, x: 0, scale: 1, duration: 0.7, ease: 'back.out(1.3)' }, t); ev(t, 'pop', { n: 2 }); };
const popOut = (id, t) => tl.to(id, { autoAlpha: 0, x: -20, scale: 0.97, duration: 0.35, ease: 'power2.in' }, t);
const svgNS = 'http://www.w3.org/2000/svg';
function link(id, a, b, t, d = 0.4) {   // 휴대폰 안 요소 → 확대 카드 실
  const g = document.createElementNS(svgNS, 'g'); g.id = id;
  const path = `M${a.x} ${a.y} C ${a.x + 50} ${a.y}, ${b.x - 50} ${b.y}, ${b.x} ${b.y}`;
  g.innerHTML = `<path class="thr-halo" d="${path}"/><path class="thr" d="${path}"/>`;
  $('#threads').appendChild(g);
  gsap.set(`#${id} path`, { drawSVG: '0% 0%' });
  tl.to(`#${id} path`, { drawSVG: '0% 100%', duration: d, ease: 'power2.inOut' }, t);
  return `#${id}`;
}
// 확대 카드 실은 #threads가 아니라 #ux 쪽에 보여야 하므로 별도 SVG
const uxSvg = document.createElementNS(svgNS, 'svg');
uxSvg.setAttribute('viewBox', '0 0 1920 1080'); uxSvg.setAttribute('width', 1920); uxSvg.setAttribute('height', 1080);
uxSvg.style.cssText = 'position:absolute;inset:0;overflow:visible;pointer-events:none';
uxSvg.id = 'uxThreads'; $('#ux').insertBefore(uxSvg, $('#popA'));
function link2(id, a, b, t, d = 0.4) {
  const g = document.createElementNS(svgNS, 'g'); g.id = id;
  const path = `M${a.x} ${a.y} C ${a.x + 46} ${a.y}, ${b.x - 46} ${b.y}, ${b.x} ${b.y}`;
  g.innerHTML = `<path class="thr-halo" d="${path}" style="stroke-width:10"/><path class="thr" d="${path}" style="stroke-width:4.5"/>`;
  uxSvg.appendChild(g);
  gsap.set(`#${id} path`, { drawSVG: '0% 0%' });
  tl.to(`#${id} path`, { drawSVG: '0% 100%', duration: d, ease: 'power2.inOut' }, t);
  ev(t, 'thread', { d });
  return `#${id}`;
}

const edge = t => tl.fromTo('#phone .frame', { boxShadow: '0 60px 110px rgba(52,30,130,.26), 0 18px 34px rgba(52,30,130,.14), 0 0 0 0 rgba(139,104,245,0)' },
  { boxShadow: '0 60px 110px rgba(52,30,130,.26), 0 18px 34px rgba(52,30,130,.14), 0 0 46px 6px rgba(139,104,245,.55)', duration: 0.35, yoyo: true, repeat: 1, repeatDelay: 0.25, ease: 'power2.out' }, t);
// 3a. 검색 (12 – 15.6초)
tl.to(phone, { autoAlpha: 1, x: 0, rotationY: 0, duration: 0.9, ease: 'expo.out' }, 11.75);
headIn('#hdA', 11.95); edge(12.2);
tl.fromTo('#sgA', { boxShadow: '0 0 0 0 rgba(166,124,242,.6)' }, { boxShadow: '0 0 0 14px rgba(166,124,242,0)', duration: 0.8, ease: 'power2.out' }, 12.35);
handIn(P.btnA.x, P.btnA.y, 12.95, 0.5);
press(P.btnA.x, P.btnA.y, 13.02, '#btnA');
handOut(13.25);
tl.to('#wA', { y: 620, duration: 0.5, ease: 'power3.in' }, 13.12); ev(13.12, 'swish');
tl.to('#scrimA', { opacity: 0, duration: 0.4 }, 13.2);
const sq = $('#sqA');
tl.fromTo('#scrA .sbar', { boxShadow: '0 0 0 0 rgba(107,78,255,.5)' }, { boxShadow: '0 0 0 10px rgba(107,78,255,0)', duration: 0.7 }, 13.42);
tl.to(['#r1', '#r2', '#r3'], { y: 0, opacity: 1, duration: 0.55, stagger: 0.1, ease: 'expo.out' }, 13.6);
const lA = link2('lA', { x: P.sqA.r.right - 6, y: P.sqA.y }, { x: P.popA.r.left, y: P.popA.y - 28 }, 13.45, 0.42);
popIn('#popA', 13.62);
tl.to('#popA .old s', { scaleX: 1, duration: 0.42, ease: 'power2.inOut' }, 14.05);
tl.to('#popA .old', { color: '#BDB8CA', duration: 0.3 }, 14.2);
tl.to('#popAnew', { y: 0, opacity: 1, duration: 0.6, ease: 'expo.out' }, 14.3); ev(14.3, 'answer2');

// 3b. 통화 (15.6 – 19.6초)
headOut('#hdA', 15.3); popOut('#popA', 15.3); tl.to(lA, { autoAlpha: 0, duration: 0.3 }, 15.3);
tl.to('#scrA', { xPercent: -100, duration: 0.7, ease: 'power3.inOut' }, 15.4);
tl.to('#scrB', { xPercent: 0, duration: 0.7, ease: 'power3.inOut' }, 15.4); ev(15.4, 'swoosh');
headIn('#hdB', 15.75);
const ct = { s: 48 };
tl.to(ct, { s: 52, duration: 4, ease: 'none', onUpdate() { $('#ctime').textContent = `00:${String(Math.floor(ct.s)).padStart(2, '0')}`; } }, 15.6);
handIn(P.handle.x, P.handle.y + 6, 16.35, 0.45);
tl.to(hand, { scale: 0.94, duration: 0.08 }, 16.38);
tl.to(hand, { y: `-=${250}`, duration: 0.42, ease: 'power2.inOut' }, 16.48);
tl.to('#wB', { y: 0, duration: 0.55, ease: 'power3.out' }, 16.5); ev(16.48, 'swipe'); edge(16.55);
tl.to(hand, { scale: 1, duration: 0.1 }, 16.9);
handOut(16.95);
typeIn($('#qB'), 'A사 시연 관련 자료', 17.0, 20);
tl.to(['#b1', '#b2', '#b3'], { y: 0, opacity: 1, duration: 0.5, stagger: 0.16, ease: 'expo.out' }, 17.55);
ev(17.55, 'pop', { n: 0 }); ev(17.71, 'pop', { n: 1 }); ev(17.87, 'pop', { n: 2 });
tl.to('#b2', { borderColor: '#CDBDFF', boxShadow: '0 0 0 2px #E7DFFF', duration: 0.3 }, 18.15);
const lB = link2('lB', { x: P.b2.r.right - 2, y: P.b2.y }, { x: P.popB.r.left, y: P.popB.y }, 18.15, 0.4);
popIn('#popB', 18.32);

// 3c. 카톡 (19.6 – 24초)
headOut('#hdB', 19.3); popOut('#popB', 19.3); tl.to(lB, { autoAlpha: 0, duration: 0.3 }, 19.3);
tl.to('#scrB', { xPercent: -100, duration: 0.7, ease: 'power3.inOut' }, 19.4);
tl.to('#scrC', { xPercent: 0, duration: 0.7, ease: 'power3.inOut' }, 19.4); ev(19.4, 'swoosh');
headIn('#hdC', 19.75);
tl.fromTo('#kbC .wv', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)', scale: 1 }, { boxShadow: '0 0 0 12px rgba(107,78,255,0)', scale: 1.12, duration: 0.5, yoyo: true, repeat: 1, ease: 'power2.out' }, 20.15);
tl.to('#wC', { y: 0, duration: 0.55, ease: 'power3.out' }, 20.4); ev(20.4, 'swish');
tl.to('#scrimC', { opacity: 1, duration: 0.4 }, 20.4); edge(20.45);
const lC = link2('lC', { x: P.sgC.r.right - 2, y: P.sgC.y }, { x: P.popC.r.left, y: P.popC.y }, 20.8, 0.4);
popIn('#popC', 20.95);
handIn(P.btnC.x, P.btnC.y, 21.7, 0.5);
press(P.btnC.x, P.btnC.y, 21.78, '#btnC');
tl.to('#wC', { y: 520, duration: 0.45, ease: 'power3.in' }, 21.88);
tl.to('#scrimC', { opacity: 0, duration: 0.35 }, 21.95);
tl.to(lC, { autoAlpha: 0, duration: 0.25 }, 21.88);
handMove(P.kSend.x, P.kSend.y, 22.42, 0.36);
press(P.kSend.x, P.kSend.y, 22.48, '#kSend');
handOut(22.68);
tl.fromTo('#mSent .bub', { scale: 0.6, transformOrigin: '100% 100%', opacity: 0 }, { scale: 1, opacity: 1, duration: 0.45, ease: 'back.out(1.8)' }, 22.56); ev(22.56, 'send');
tl.fromTo('#mReply', { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: 'expo.out' }, 23.1); ev(23.1, 'msg');

// 마무리로 넘어가기
headOut('#hdC', 23.45); popOut('#popC', 23.4);
tl.to(phone, { y: 60, scale: 0.86, autoAlpha: 0, filter: 'blur(6px)', duration: 0.55, ease: 'power3.in' }, 23.5);
ev(23.5, 'whoosh');

/* ── 4. 엔드 카드 (24 – 28초) ──────────────────── */
gsap.set('#logo .mark', { scale: 0.4, rotation: -30, opacity: 0 });
gsap.set('#logo .word', { clipPath: 'inset(-20% 100% -20% 0%)', x: -30 });
gsap.set(['#tag', '#sub'], { y: 24, opacity: 0 });
gsap.set('#fin', { opacity: 0 });
tl.to('#logo .mark', { scale: 1, rotation: 0, opacity: 1, duration: 0.9, ease: 'back.out(1.7)' }, 24.0);
ev(24.0, 'logo');
tl.to('#logo .word', { clipPath: 'inset(-20% -2% -20% 0%)', x: 0, duration: 0.9, ease: 'expo.out' }, 24.25);
tl.to('#tag', { y: 0, opacity: 1, duration: 0.8, ease: 'expo.out' }, 25.0); ev(25.0, 'word2');
tl.to('#sub', { y: 0, opacity: 1, duration: 0.8, ease: 'expo.out' }, 25.45);
tl.to('#end', { scale: 1.02, duration: 4.0, ease: 'none' }, 24.0);
tl.to('#fin', { opacity: 1, duration: 0.7, ease: 'power1.inOut' }, 27.3);

/* ── 배경은 전체 내내 천천히 ───────────────────── */
tl.to('.g1', { x: 220, y: 60, duration: DUR, ease: 'none' }, 0);
tl.to('.g2', { x: -180, y: -40, duration: DUR, ease: 'none' }, 0);
tl.fromTo('.g3', { scale: 0.9, opacity: 0.6 }, { scale: 1.25, opacity: 1, duration: DUR, ease: 'none' }, 0);
tl.fromTo('.g3', { backgroundImage: 'radial-gradient(closest-side, rgba(123,92,255,.10), rgba(123,92,255,0))' },
  { backgroundImage: 'radial-gradient(closest-side, rgba(123,92,255,.24), rgba(123,92,255,0))', duration: 0.6, yoyo: true, repeat: 1, ease: 'power2.out' }, 6.0);
tl.set({}, {}, DUR);

/* ── 바깥에서 쓰는 손잡이 ───────────────────────── */
window.__DURATION = DUR;
window.__events = EV.sort((a, b) => a.t - b.t);
// 글자·표시처럼 뚝 바뀌는 상태는 t로 바로 정한다(어느 시점으로 탐색해도 같은 그림)
const PH = '<span style="color:#9a96a6; font-weight:400">메시지 입력</span>';
const disc = [
  [t => t >= 13.42, on => { sq.textContent = on ? '배비치 소비뇽 블랑' : '지은이네 집들이 때 먹었던 와인'; sq.style.color = on ? '#6B4EFF' : ''; sq.style.fontWeight = on ? 700 : ''; }],
  [t => t >= 19.75, on => { $('#sbt').textContent = on ? '10:31' : '13:00'; }],
  [t => t >= 22.05 && t < 22.56, on => { if (on) $('#kinTx').textContent = '엄마, 전에 먹고 싶다던 무화과시루 사갈까?'; }],
  [t => t < 22.05 || t >= 22.56, on => { if (on) $('#kinTx').innerHTML = PH; }],
  [t => t >= 22.56, on => { $('#mSent').style.display = on ? 'flex' : 'none'; }],
  [t => t >= 23.1, on => { $('#mReply').style.display = on ? 'flex' : 'none'; }],
];
const sq0 = 0;
window.__seek = t => { disc.forEach(([c, f]) => f(c(t))); tl.seek(t, false); };
window.__ready = (async () => {
  const fams = ['400 20px "Noto Sans KR"', '500 20px "Noto Sans KR"', '600 20px "Noto Sans KR"', '700 20px "Noto Sans KR"', '400 20px Inter', '500 20px Inter', '600 20px Inter', '700 20px Inter', '20px "Nanum Pen Script"', '700 20px "Samsung Sharp Sans"'];
  await Promise.all(fams.map(f => document.fonts.load(f, '가A')));
  await document.fonts.ready;
  await Promise.all([...document.images].map(im => im.decode().catch(() => {})));
  tl.seek(0, false);
  return true;
})();
