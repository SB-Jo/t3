/* Weave 결선 모션그래픽 v21 (2026-11-09) — Pain Points 뒤에 트는 세 시나리오 소개 영상.
   오프닝(로고와 한 문장) → 1 기록 통합 검색(통화, 요약) → 2 단서로 찾는 기억(구글 창, 와인) → 3 먼저 건네는 기억(카톡 링크 미리보기) → 세 화면 → 로고.
   v11: 85초 → 약 2분. 한 번에 하나씩(제목 → 말풍선 → 생각 → 검색 → 기록 하나씩 → 요약을 크게 → 답변), 장면 카드는 별 없이 번호와 이름에 빛, 메일 버튼과 갤러리 삭제.
   v12: 120초 → 100초. 순서와 비트는 그대로 두고 머무는 시간과 비트 안의 간격만 줄임(v10보다 늘어난 34초 중 24초가 1에 몰려 있어서 1을 가장 많이 줄임).
   v13: 100초 → 107.5초. 장면 카드 빛은 이름에 한 번, 01 제목은 왼쪽 위로 옮겨 남음, 검색하면 연결된 기억이 바로 뜸, 02 검색어가 두 질문으로 갈라짐, 03 위치 → 탑승권 → 카톡 세 실, 끝 장면은 GIF처럼.
   v14: 107.5초 → 115초. 빛은 글자를 천천히 한 번 지나감, 01 제목은 왼쪽에 그대로 남고 말풍선은 한 글자씩(상상 말풍선 삭제), 02는 왼쪽 큰 글과 오른쪽 휴대폰으로 시작, 03 플로팅은 위치와 탑승권을 나란히 잇고 위치와 카톡을 휴대폰으로, 끝 장면은 거의 실제 빠르기로.
   v15: 115초 → 117초. 장면 카드 글자가 번쩍였다 다시 뜨던 버그 수정, 02 처음 글과 위쪽 띠(배경은 그대로 두고 사슬만 위에서 흐려짐), 03 위치와 탑승권은 곧은 실, 끝 장면을 조금 크고 느리게.
   v16: 117초 → 118.3초. 곡을 첫 마디부터(오프닝 두 마디, 4.8초에 첫 장면 카드와 함께 터짐), 01 형광펜 뒤 0.5초 줄임과 답변 문장, 요약의 '3번 부스',
        02 갤러리 카드는 날짜가 건너온 뒤에 날짜와 사진이 뜸, 01과 03 제목은 02처럼 걷힘(03 빛 없음), 로고 글자 끝을 진하게, 세 화면 번호에 입체감.
   v17: 길이 그대로(118.3초). 02 처음 큰 글은 둘째 줄이 보라, 02 제목은 '기억 속 단서를 엮어,'가 보라, 갤러리 카드 제목은 처음부터(날짜만 건너온 뒤),
        03 탑승권을 0.5초 더 보여 줌, 03 제목 둘째 줄 '필요한 말을 먼저 추천합니다', 추천 시트의 'Weave'를 보라로, 끝 장면 GIF에서 검색 불러오기 줄을 뺌.
   v18: 첫 문장 '우리들의 흩어진 기억, Weave가 잇습니다', 01의 '민수님'(붙여 씀).
   v21: 첫 문장 '일상 속 흩어진 기억, Weave가 이어 줍니다'(잇습니다 → 이어 줍니다). 끝 장면 세 화면을 30fps로(20fps는 끊겨 보임), 번호 원의 입체감을 줄임.
        수미상관: 첫 문장을 끝 화면 한 줄 소개와 같은 글꼴(두 줄 모두 54px)로, 끝 화면의 '그때 그거? Weave got it!'을 빼고 한 줄 소개를 로고 아래 같은 간격·박자로.
   v20: 01 요약에서 돌아올 때 제목을 다시 띄우지 않고, 말풍선 + 휴대폰을 290px 왼쪽으로(묶음이 화면 가운데). 03 아내 카톡은 위 두 플로팅 묶음의 가운데에.
        음악은 북이 빠지는 마디 없이 다시 편집.
   v19: 첫 문장 '일상 속 흩어진 기억, Weave가 잇습니다'. 01 검색 뒤 기록이 하나씩 뜨는 구간을 1.2배 빠르게(SPD1, 1.8초 줄어 남는 시간은 03 답장 뒤에 붙음).
        음악은 곡 순서대로 흐르게 다시 편집(tools/music.py).
   순서와 장면 이름은 5쪽 Solution과 같다. 코드 안의 01·02·03 표시는 옛 이름(01 = 와인, 02 = 통화, 03 = 카톡)으로 남겨 두었다.
   이전: Weave 결선 인트로 v8 — GSAP 타임라인 하나(paused)를 시간 t로 탐색해 프레임을 찍는다.
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
const D1 = 4.8, BAR = 2.4;                             // 곡(Mixkit 'A Special Feeling', 100 BPM)이 터지는 순간(첫 장면 카드), 한 마디 길이. 오프닝은 곡의 첫 두 마디

/* ── 장면 시각(초): 한 번에 하나씩. 새 요소가 혼자 뜨고, 읽을 시간을 준 뒤에 다음 요소가 온다 ── */
const OP = { mark: 0.1, word: 0.45, sub: 1.2, glint: 1.75, out: 4.25 };    // 오프닝: 곡의 첫 박과 함께 로고 → 글자 → 문장 → 둘째 마디에 빛 → 걷힘
const CH = 2.35;                                       // 장면 카드: 글자가 올라옴 → 잠깐 쉼 → 빛이 천천히 한 번 → 걷힘
// 1 통화
const C2 = D1 + 0.05, s2 = C2 + CH;                    // 카드, 시작(제목만 보이는 때)
const tCall = s2 + 2.5;                                // 재웅 선배 말풍선(글자는 한 글자씩)
const tFocus = tCall + 3.7, dragT = tFocus + 1.2, dragD = 1.1;    // 말풍선을 걷고 손잡이로, 위로 끌기(형광펜 뒤 약 0.8초 머묾)
const tType = dragT + dragD + 0.1, tGo = tType + 1.8;  // 검색창을 크게 보며 입력, 손으로 검색 버튼
const SPD1 = 1.2;                                      // v19: 검색 뒤 기록이 실로 이어지며 하나씩 뜨는 구간을 1.2배 빠르게(요약이 다시 보여 주므로)
const tSmall = tGo + 0.45, tRec = tSmall + 1.1 / SPD1; // 누른 순간 연결된 기억이 뜨고 화면이 작아짐, 하나씩 크게 보기 시작
const REC = [0, 2.5, 4.6, 7.5].map(d => tRec + d / SPD1);   // 기록 네 개를 실로 이어 하나씩 크게
const tWoven = tRec + 9.0 / SPD1, tSum = tWoven + 0.75 / SPD1;   // 네 기록을 실로 엮음, 요약을 크게
const tBack = tSum + 6.1, tAns = tBack + 1.05, X2 = tAns + 4.8;   // 작아지고 말풍선이 돌아옴, 답변(한 글자씩), 장면 끝
// 2 와인
const C1 = X2 + 0.35, P0 = C1 + CH;                    // 카드, 휴대폰 등장(왼쪽에 큰 글)
const tZ = P0 + 3.7;                                   // 큰 글이 걷히고 휴대폰이 가운데로 와서 검색창을 크게
const pTap1 = tZ + 3.85;                               // Weave 버튼
const c1 = pTap1 + 1.65, c2 = c1 + 4.8, c3 = c2 + 5.5, c4 = c3 + 2.5;   // 카메라가 옮겨 가는 때: 첫째 단서, 둘째 단서(날짜가 건너간 뒤 사진이 뜸), 라벨, 답
const T2 = c4 + 3.5, X1 = T2 + 5.3;                    // 입력하기, 장면 끝(결과를 보며 1초 남짓 머문 뒤)
// 3 카톡: 대화와 입력하기 → 전송 → 답장은 v10보다 빨라지지 않게(사용자가 늘려 달라고 한 곳)
const C3 = X1 + 0.35, s3 = C3 + CH + 0.05;             // 카드, 시작(제목만 보이는 때)
const tChat = s3 + 3.6, tM2 = tChat + 3.0, tM3 = tM2 + 1.8;   // 대화: 아내 → 나(입력해서 전송) → 아내
const g3 = tM3 + 1.75, tW = g3 + 2.0, tK = tW + 2.1, tL = tK + 2.45;  // 플로팅: 위치 → 탑승권(오른쪽에 이어짐, 실 뒤에 읽을 틈) → 아내 카톡 → 링크 미리보기
const th3 = tL + 1.95;                                 // 위치와 카톡이 휴대폰으로 엮이는 실
const pTapW = th3 + 2.1, pTapI = pTapW + 3.6, pTapS = pTapI + 1.6;    // Weave 버튼 · 입력하기 · 전송
const tRead = pTapS + 1.05, tReply = pTapS + 2.1;      // 읽음(1이 사라짐) → 답장
const tTrioD = 5.2;                                    // 세 화면이 머무는 시간(GIF처럼 움직임)
const LOGO_MIN = tReply + 2.1 + 0.35 + tTrioD;         // 답장을 읽을 시간 + 휴대폰이 빠지는 시간 + 세 화면(로고가 마디에 맞아 남는 시간은 답장 뒤에 붙음)
const LOGO = D1 + Math.ceil((LOGO_MIN - D1) / BAR - 1e-6) * BAR;   // 로고는 곡의 마디 첫 박에(마지막 한 방)
const tTrio = LOGO - tTrioD;                           // 세 화면이 모이는 때
const DUR = LOGO + 5.5;                                // 끝 화면 5.5초
const GIF = { w: 374, h: 777, cols: 12, fps: 30, n: 144, off: [0, 0.15, 0.3] };   // v21: 20 → 30fps(60fps 영상에서 한 장이 세 프레임씩 머물러 끊겨 보였음)   // 끝 장면 스프라이트(tools/trio.cjs가 같은 값을 읽음)

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
const QA = '지은이네 집들이 때 마셨던 와인', ANS = '배비치 소비뇽 블랑', MSGTX = '여보, 전에 말한 에스티 로더 갈색병<br>면세점에서 사 갈까?';
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
// 말풍선 글자를 한 글자씩: 자리는 미리 잡혀 있고(말풍선 크기가 그대로) 글자마다 보이는 때만 다르다. 글자들과 시각을 돌려준다
function typeChars(root, t0, cps) {
  const chs = [];
  (function walk(n) { for (const c of [...n.childNodes]) {
    if (c.nodeType === 3) {
      const f = document.createDocumentFragment();
      for (const g of c.textContent) { const s = document.createElement('span'); s.textContent = g; f.appendChild(s); chs.push(s); }
      c.replaceWith(f);
    } else if (c.nodeName !== 'BR') walk(c);
  } })(root);
  const times = []; let t = t0, last = -1;
  for (const s of chs) { times.push(t); t += (1 / cps) * (0.75 + rnd() * 0.5) * (s.textContent === ' ' ? 0.6 : 1); }
  cont.push(tt => { let n = 0; while (n < times.length && times[n] <= tt + 1e-9) n++;
    if (n !== last) { chs.forEach((s, i) => { s.style.opacity = i < n ? 1 : 0; }); last = n; } });
  const spanOf = sel => { const cs = [...$(sel).querySelectorAll('span')]; return [times[chs.indexOf(cs[0])], times[chs.indexOf(cs[cs.length - 1])]]; };
  return { end: t, spanOf };
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
function hop(sel, a, b, t, d = 0.7, lift = 70, o = {}) {
  const mid = o.mid || { x: (a.x + b.x) / 2, y: Math.min(a.y, b.y) - lift }, hold = o.hold || 0;
  gsap.set(sel, { x: a.x, y: a.y, xPercent: -50, yPercent: -50, autoAlpha: 0, scale: 0.6 });
  tl.to(sel, { autoAlpha: 1, scale: 1, duration: 0.25, ease: 'back.out(2)' }, t);
  tl.to(sel, { motionPath: { path: [a, mid, b], curviness: 1.25 }, duration: d, ease: o.ease || 'power2.inOut' }, t + 0.2 + hold);
  tl.to(sel, { autoAlpha: 0, scale: 0.7, duration: 0.2, ease: 'power2.in' }, t + 0.2 + hold + d);
}

/* ── 챕터 카드 · 헤드라인 ─────────────────────────── */
const sweep = (sel, t, d = 1.1) => tl.fromTo(sel, { backgroundPosition: '100% 0%, 0% 0%' }, { backgroundPosition: '0% 0%, 0% 0%', duration: d, ease: 'sine.inOut', immediateRender: false }, t);   // 빛이 글자 위를 지나는 구간만 쓴다(예전 값은 대부분 글자 밖이라 글자 위는 순식간에 지나감)
const chapIn = (id, t) => {
  const lines = [`${id} .no`, `${id} .tt`];
  gsap.set(lines, { y: 30, opacity: 0 });                                              // 처음부터 감춰 둔다. 안 그러면 늦게 시작하는 줄이 먼저 보였다가 사라졌다 다시 뜬다
  tl.set(id, { autoAlpha: 1 }, t);
  tl.to(lines, { y: 0, opacity: 1, duration: 0.9, stagger: 0.08, ease: 'power3.out' }, t);
  sweep(`${id} .tt`, t + 1.0);                                                         // 글자가 다 올라오고 잠깐 쉰 뒤 이름에 빛이 한 번
};
const chapOut = (id, t) => { tl.to([`${id} .no`, `${id} .tt`], { y: -26, opacity: 0, duration: 0.35, stagger: 0.04, ease: 'power2.in' }, t); tl.set(id, { autoAlpha: 0 }, t + 0.45); };
const titleIn = (id, t) => { tl.set(id, { autoAlpha: 1 }, t); tl.fromTo(`${id} .tl`, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8, ease: 'expo.out', immediateRender: false }, t); };   // 큰 제목: 두 줄을 한 번에
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
  for (const k of ['#kbA .wv', '#kbA .srch', '#gbox', '#handle', '#qB', '#sgB', '#sgC', '#btnC', '#chatIn', '.kin', '#kbC .wv', '#kbC .tb']) B[k] = ctr(k);
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
  { const G = 14; let H = -G; for (const k of ['#fl1', '#fl2', '#fl3', '#fl4']) H += rectOf(k).height + G;   // 네 기록을 화면 세로 가운데에 쌓음
    let y = (1080 - H) / 2; for (const k of ['#fl1', '#fl2', '#fl3', '#fl4']) { $(k).style.top = `${y}px`; y += rectOf(k).height + G; } }
  { const a = rectOf('#fg'), b = rectOf('#fw'), k = rectOf('#fk'), el = $('#fk');          // v20: 아내 카톡을 위 두 플로팅(위치 → 탑승권) 묶음의 가운데에
    el.style.left = `${el.offsetLeft + (a.left + b.right) / 2 - (k.left + k.width / 2)}px`; }
  const natMore = rectOf('#kkMore').height;
  const FLR = {}; for (const k of ['#fl1', '#fl2', '#fl3', '#fl4', '#fg', '#fw', '#fk']) FLR[k] = rectOf(k);
  const DT = { a: ctr('#dtA'), b: ctr('#dtB'), g: ctr('#gpsDj'), k: ctr('#kkDj'), qa: ctr('#qa1'), qb: ctr('#qa2'), pill: ctr('#pill'), p1: ctr('#pen1'), p2: ctr('#pen2') };   // 같은 단서(날짜·면세점)와 검색어 조각의 자리
  const R2 = { x: 560, y: 0, scale: 1 };                                                     // 01·02에서 휴대폰이 오른쪽에 있을 때
  // 02: 검색어 조각 → 질문을 잇는 실
  { const pb = rectOf('#pill').bottom, r1 = rectOf('#pen1'), r2 = rectOf('#pen2'), y1 = (r1.top + r1.bottom) / 2;
    const setD = (g, d) => $$(`${g} path`).forEach(p => p.setAttribute('d', d));
    setD('#tA', `M${DT.qa.x} ${pb} C ${DT.qa.x} ${pb + 120}, ${r1.right + 130} ${y1}, ${r1.right + 2} ${y1}`);
    setD('#tQ2', `M${DT.qb.x} ${pb} C ${DT.qb.x} ${pb + 34}, ${DT.qb.x - 44} ${r2.top - 30}, ${DT.qb.x - 44} ${r2.top + 2}`); }   // 곧은 세로줄은 그라데이션이 안 그려져서 살짝 휜다
  gsap.set('.chap', { autoAlpha: 0 });
  gsap.set('.head', { autoAlpha: 0 });
  gsap.set(['#fl1', '#fl2', '#fl3', '#fl4', '#fg', '#fw', '#fk', '#flLink', '#callQ', '#callA', '#flyChip', '#gai', '#tokA', '#tokC', '#qc1', '#qc2', '#trio'], { autoAlpha: 0 });

  /* ── 오프닝: 로고와 한 문장(끝 화면과 같은 로고) ── */
  gsap.set('#op .mark', { scale: 0.4, rotation: -30, opacity: 0 });
  gsap.set('#op .word', { clipPath: 'inset(-50% 100% -50% -4%)', x: -24, autoAlpha: 0 });
  gsap.set('#opSub', { y: 24, opacity: 0 });
  tl.to('#op .mark', { scale: 1, rotation: 0, opacity: 1, duration: 0.8, ease: 'back.out(1.6)' }, OP.mark);
  tl.set('#op .word', { autoAlpha: 1 }, OP.word);
  tl.to('#op .word', { clipPath: 'inset(-50% -5% -50% -4%)', x: 0, duration: 0.8, ease: 'expo.out' }, OP.word);
  sweep('#op .word', OP.glint, 1.3);                                                          // 빛이 글자 가운데를 지날 때 곡의 둘째 마디(2.4초)
  tl.to('#opSub', { y: 0, opacity: 1, duration: 0.7, ease: 'expo.out' }, OP.sub);
  tl.to('#op', { opacity: 0, y: -20, filter: 'blur(8px)', duration: 0.5, ease: 'power2.in' }, OP.out);

  /* ── 2 단서로 찾기 ── */
  chapIn('#ch1', C1); chapOut('#ch1', C1 + CH);
  const phone = $('#phone');
  gsap.set(phone, { autoAlpha: 0, x: 0, y: 160, scale: 0.92, transformOrigin: '50% 50%' });
  gsap.set(['#scrA', '#scrC'], { xPercent: 100 }); gsap.set('#scrB', { xPercent: 0 });
  tl.set('#scrB', { xPercent: -100 }, C1 + 0.15); tl.set('#scrA', { xPercent: 0 }, C1 + 0.15);
  gsap.set('#gres', { display: 'none' });
  tl.set(phone, { x: 1400, y: 0, scale: 1, rotation: 0, filter: 'blur(0px)', autoAlpha: 1 }, P0 - 0.1);
  tl.to(phone, { x: R2.x, duration: 1.05, ease: 'power3.out' }, P0);
  titleIn('#hd2', P0 + 0.4); headOut('#hd2', tZ - 0.35);                                       // 01처럼 왼쪽에 큰 글이 먼저
  tl.fromTo('#caretA', { opacity: 1 }, { opacity: 0, duration: 0.01, repeat: 13, yoyo: true, repeatDelay: 0.3, ease: 'none' }, P0 + 0.4);
  cam(tZ, camPose(2.3, B['#gbox'], { x: 960, y: 430 }), 1.0);                                  // 휴대폰이 가운데로 오며 검색창을 크게
  typeIn($('#sqA'), QA, tZ + 0.7, 11);
  cam(tZ + 2.45, camPose(2.3, { x: B['#kbA .wv'].x + 90, y: B['#kbA .wv'].y }, { x: 960, y: 600 }), 0.85);   // Weave를 누를 때는 Weave 아이콘 쪽
  edge(pTap1 + 0.05);
  tl.fromTo('#kbA .wv', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)' }, { boxShadow: '0 0 0 14px rgba(107,78,255,0)', duration: 0.6, ease: 'power2.out', immediateRender: false }, pTap1 + 0.05);
  tl.to(phone, { y: '+=2300', duration: 0.55, ease: 'power2.in' }, pTap1 + 0.25);       // 휴대폰은 아래로 빠지고, 물음은 위로
  tl.set(phone, { autoAlpha: 0 }, pTap1 + 0.85);

  // 사슬: 단계마다 카메라가 그 자리로 옮겨 가고, 질문이 먼저 혼자 뜬 다음에 실이 이어지고 기록이 나온다
  gsap.set('#w1', { transformOrigin: '0 0', x: 0, y: 0, scale: 1 });
  gsap.set(['#cA', '#cB', '#cC'], { autoAlpha: 0, scale: 0.9, y: 26 });
  gsap.set(['#cBd', '#cB .photo img'], { opacity: 0 });
  gsap.set(['#tA .thr', '#tA .thr-halo', '#tQ2 .thr', '#tQ2 .thr-halo', '#tB .thr', '#tB .thr-halo', '#tC .thr', '#tC .thr-halo'], { drawSVG: '0% 0%' });
  gsap.set('.pen', { autoAlpha: 0, y: 16, scale: 0.6, transformOrigin: '12% 100%' });
  gsap.set('#scan', { y: -80, opacity: 0 }); gsap.set('#ocr', { opacity: 0 });
  gsap.set('#ocrbox', { opacity: 0, scale: 1.25 });
  gsap.set('#pill', { autoAlpha: 0 });
  const draw = (g, t, d) => tl.to(`${g} .thr, ${g} .thr-halo`, { drawSVG: '0% 100%', duration: d, ease: 'power2.inOut' }, t);
  const penIn = (id, t) => {
    tl.to(id, { autoAlpha: 1, y: 0, scale: 1, duration: 0.65, ease: 'back.out(2.2)' }, t); ev(t, 'pen');
    tl.fromTo(id, { boxShadow: '0 14px 30px rgba(107,78,255,.34), 0 0 0 0 rgba(107,78,255,.55)' }, { boxShadow: '0 14px 30px rgba(107,78,255,.34), 0 0 0 26px rgba(107,78,255,0)', duration: 0.9, ease: 'power2.out', immediateRender: false }, t + 0.3);
  };
  const cardIn = (id, t) => tl.to(id, { autoAlpha: 1, scale: 1, y: 0, duration: 0.9, ease: 'back.out(1.3)' }, t);
  headIn('#h1', pTap1 + 0.75);
  // 검색어 조각에 형광펜 → 조각이 떨어져 나와 실을 끌고 날아가 질문이 된다
  const splitQ = (seg, chip, g, pen, a, path, t, d) => {
    mark(seg, t, 0.4);
    gsap.set(chip, { x: a.x, y: a.y, xPercent: -50, yPercent: -50 });
    tl.to(chip, { autoAlpha: 1, scale: 1.03, duration: 0.2, ease: 'back.out(2)' }, t + 0.35);
    tl.to(chip, { motionPath: { path, curviness: 1 }, scale: 1, duration: d, ease: 'power2.inOut' }, t + 0.5);
    draw(g, t + 0.5, d);
    tl.to(chip, { autoAlpha: 0, duration: 0.14, ease: 'power1.in' }, t + 0.5 + d - 0.14);       // 칩이 걷히는 자리에 질문이 뜬다
    penIn(pen, t + 0.5 + d - 0.03);
  };
  wcam(c1, wPose(1.5, { x: 300, y: 450 }, { x: 800, y: 620 }), 1.0);                         // '지은이네 집들이 때' → 집들이가 언제였지? → 지은 카톡
  splitQ('#qa1', '#qc1', '#tA', '#pen1', DT.qa, [DT.qa, { x: DT.qa.x - 30, y: DT.qa.y + 130 }, { x: DT.p1.x + 230, y: DT.p1.y }, DT.p1], c1 + 0.6, 0.7);
  cardIn('#cA', c1 + 2.4);
  mark('#hlT0', c1 + 3.15, 0.4); mark('#hlT', c1 + 3.55, 0.5);                                 // '박스 정리', '휴지 안 사 와도 돼' = 집들이
  mark('#dtA', c1 + 4.1, 0.45);                                                               // 카톡을 받은 날이 그날
  wcam(c2, wPose(1.25, { x: 640, y: 500 }, { x: 960, y: 620 }), 1.0);                       // 그날 찍은 와인 사진은? → 카톡과 사진을 한 화면에
  splitQ('#qa2', '#qc2', '#tQ2', '#pen2', DT.qb, [DT.qb, { x: DT.qb.x - 10, y: (DT.qb.y + DT.p2.y) / 2 }, DT.p2], c2 + 0.6, 0.55);   // '마셨던 와인' → 그날 찍은 와인 사진은?
  draw('#tB', c2 + 2.1, 0.6); cardIn('#cB', c2 + 2.35);                                           // 갤러리 카드는 제목('와인 사진', 질문에 있는 말)만 있고 날짜와 사진은 아직 없음
  hop('#tokA', DT.a, DT.b, c2 + 2.95, 1.0, 70, { hold: 0.3, ease: 'sine.inOut' });               // 같은 날짜(3월 15일)가 사진 카드로 건너감
  tl.to('#cBd', { opacity: 1, duration: 0.3, ease: 'power1.out' }, c2 + 4.4);                   // 표가 내려앉는 자리에 날짜가 생기고
  mark('#dtB', c2 + 4.6, 0.4);
  tl.fromTo('#cB .photo img', { opacity: 0, scale: 1.04 }, { opacity: 1, scale: 1, duration: 0.6, ease: 'power2.out', immediateRender: false }, c2 + 4.7);   // 그날의 와인 사진이 뜬다
  wcam(c3, wPose(1.6, { x: 930, y: 700 }, { x: 960, y: 610 }), 1.0);                        // 사진 속 라벨 글자 읽기
  tl.to('#scan', { opacity: 1, duration: 0.1 }, c3 + 0.9).to('#scan', { y: 240, duration: 0.7, ease: 'power1.inOut' }, c3 + 0.9).to('#scan', { opacity: 0, duration: 0.2 }, c3 + 1.5);
  tl.to('#ocrbox', { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(2)' }, c3 + 1.3);
  tl.to('#ocr', { opacity: 1, duration: 0.15 }, c3 + 1.35);
  typeIn($('#ocr'), 'BABICH SAUVIGNON BLANC', c3 + 1.4, 36, null);
  tl.fromTo('#ocr', { boxShadow: '0 0 0 0 rgba(123,75,216,0)' }, { boxShadow: '0 0 0 3px rgba(123,75,216,.7)', duration: 0.35, ease: 'power2.out', immediateRender: false }, c3 + 2.05);
  // 줌아웃 없이 옆으로: 사진을 왼쪽에 둔 채 라벨 → 질문 → 답으로 이어 간다
  const wsA = 1.5;
  wcam(c4, wPose(wsA, { x: 1560, y: 650 }, { x: 1180, y: 640 }), 1.2, 'power2.inOut');
  penIn('#pen3', c4 + 0.8);
  draw('#tC', c4 + 1.5, 0.6); cardIn('#cC', c4 + 1.85); ev(c4 + 1.9, 'answer');
  tl.fromTo('#cC', { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 0 rgba(166,124,242,.55)' },
    { boxShadow: '0 34px 80px rgba(84,56,190,.24), 0 0 0 2px #DCCFFF inset, 0 0 0 28px rgba(166,124,242,0)', duration: 1.1, ease: 'power2.out', immediateRender: false }, c4 + 1.95);
  // 입력하기 → 답이 검색창으로 들어가 글자가 바뀜 → 검색 키 → 결과의 이름 부분에 표시
  tl.to(['#w1'], { autoAlpha: 0, filter: 'blur(8px)', duration: 0.5, ease: 'power2.in' }, T2 + 0.2);
  headOut('#h1', T2 + 0.1);
  const boxPose = camPose(2.0, B['#gbox'], { x: 960, y: 400 });
  tl.set(phone, { ...boxPose, y: boxPose.y + 1150, rotation: 0, autoAlpha: 1 }, T2 + 0.1);
  tl.to(phone, { y: boxPose.y, duration: 0.85, ease: 'power3.out' }, T2 + 0.15);
  textAt($('#sqA'), T2 + 0.85, { html: `<span class="sel">${QA}</span>` });
  textAt($('#sqA'), T2 + 1.3, { text: ANS });
  tl.fromTo('#gsweep', { scaleX: 0, opacity: 1 }, { scaleX: 1, duration: 0.45, ease: 'power2.out', immediateRender: false }, T2 + 1.3).to('#gsweep', { opacity: 0, duration: 0.3 }, T2 + 1.85);
  const both = camPose(1.3, { x: (B['#gbox'].x + B['#kbA .srch'].x) / 2, y: (B['#gbox'].y + B['#kbA .srch'].y) / 2 }, { x: 960, y: 560 });
  cam(T2 + 1.65, both, 0.65);                                                                   // 바뀐 검색어와 검색 키를 한 화면에
  const pTap3 = T2 + 2.4;
  tl.fromTo('#kbA .srch', { boxShadow: '0 0 0 0 rgba(47,107,255,.55)' }, { boxShadow: '0 0 0 12px rgba(47,107,255,0)', duration: 0.6, ease: 'power2.out', immediateRender: false }, T2 + 1.95);
  tl.fromTo('#gload', { scaleX: 0, opacity: 1 }, { scaleX: 1, duration: 0.4, ease: 'power1.inOut', immediateRender: false }, pTap3 + 0.07).to('#gload', { opacity: 0, duration: 0.15 }, pTap3 + 0.47);
  when(t => t >= pTap3 + 0.15, on => resultState(on));
  tl.fromTo(['#gres .gchips', '#gres .res'], { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.07, ease: 'expo.out', immediateRender: false }, pTap3 + 0.15);
  cam(pTap3 + 0.15, camPose(1.95, { x: B.r1.x, y: B.r1.y + 40 }, { x: 960, y: 520 }), 1.0);  // 결과를 보며 첫 결과로 한 번에
  mark('#gres mark.rm', pTap3 + 1.1, 0.45);                                                   // 결과 속 '배비치 … 소비뇽 블랑'에 표시
  tl.fromTo('#r1', { boxShadow: '0 0 0 0 rgba(123,75,216,0)' }, { boxShadow: '0 0 0 2.5px rgba(123,75,216,.8)', duration: 0.4, ease: 'power2.out', immediateRender: false }, pTap3 + 1.1);

  /* ── 1 한 번에 모아 보기: 휴대폰 오른쪽. 제목 → 통화 말풍선 → 위로 올려 검색 → 검색 버튼 → 기록 하나씩 → 요약을 크게 → 답변 ── */
  tl.to(phone, { x: '-=420', autoAlpha: 0, filter: 'blur(6px)', duration: 0.45, ease: 'power3.in' }, X1);
  chapIn('#ch2', C2); chapOut('#ch2', C2 + CH);
  tl.set(phone, { x: 1400, y: 0, scale: 1, rotation: 0, filter: 'blur(0px)', autoAlpha: 1 }, s2 - 0.1);
  tl.to(phone, { x: R2.x, duration: 1.05, ease: 'power3.out' }, s2);
  titleIn('#hdB', s2 + 0.4);                                                                  // 제목만 먼저
  headOut('#hdB', tFocus);                                                                    // 검색창을 키우는 동안만 걷힘(02, 03 제목과 같은 걷힘)
  cont.push(t => { const v = 48 + Math.floor(clamp(t - s2, 0, 200)); $('#ctime').textContent = `${String(Math.floor(v / 60)).padStart(2, '0')}:${String(v % 60).padStart(2, '0')}`; });
  // 재웅 선배가 말한다: 말풍선이 뜨고 한 글자씩, 끝나면 물어보는 것에 형광펜
  tl.fromTo('#callQ', { autoAlpha: 0, x: -24, scale: 0.96, transformOrigin: '100% 60%' }, { autoAlpha: 1, x: 0, scale: 1, duration: 0.7, ease: 'back.out(1.4)', immediateRender: false }, tCall);
  const tq = typeChars($('#callQ .q'), tCall + 0.3, 17);
  $$('#callQ .eq i').forEach((b, i) => {
    const d = 0.13 + 0.04 * ((i * 7) % 5);
    tl.fromTo(b, { scaleY: 0.25 }, { scaleY: 1, duration: d, repeat: Math.floor((tq.end - tCall - 0.3) / d), yoyo: true, ease: 'sine.inOut', immediateRender: false }, tCall + 0.3 + i * 0.03);
  });
  mark('#callQ .qk', tq.end + 0.1, 0.55);
  // 말풍선을 걷고 손잡이로: 내용을 이해한 뒤라 휴대폰만 크게 본다
  tl.to('#callQ', { autoAlpha: 0, x: -24, duration: 0.45, ease: 'power2.in' }, tFocus);
  const hPose = camPose(2.1, B['#handle'], { x: 960, y: 800 });
  const qPose = camPose(2.7, B['#qB'], { x: 960, y: 430 });
  cam(tFocus + 0.1, hPose, 0.85);
  gsap.set('#chevB svg', { opacity: 0 });
  tl.fromTo('#chevB svg', { y: 8, opacity: 0 }, { y: -8, opacity: 1, duration: 0.4, stagger: 0.08, ease: 'power1.out', immediateRender: false }, tFocus + 0.5);
  tl.to('#chevB svg', { opacity: 0, duration: 0.15 }, dragT);
  tl.fromTo('#scrB .hlab', { scale: 1 }, { scale: 1.12, duration: 0.3, yoyo: true, repeat: 1, ease: 'power1.inOut', immediateRender: false }, tFocus + 0.45);
  tl.fromTo('#handle', { y: 0, boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { y: -7, boxShadow: '0 0 12px 3px rgba(107,78,255,.55)', duration: 0.22, yoyo: true, repeat: 1, ease: 'sine.inOut', immediateRender: false }, tFocus + 0.5);
  gsap.set('#wB', { y: lift + 14, autoAlpha: 0 });
  tl.set('#wB', { autoAlpha: 1 }, dragT);
  tl.to('#wB', { y: 0, duration: dragD, ease: 'power2.inOut' }, dragT);
  when(t => t >= dragT && t < dragT + dragD + 0.25, on => $('#wB').classList.toggle('drag', on));
  cam(dragT, qPose, dragD, 'power2.inOut');                                                   // 카메라가 손을 따라 올라가 검색창을 화면 가운데에 크게
  edge(dragT + 0.3);
  typeIn($('#qB'), '삼성기술전 시연 내용', tType, 9);
  // 손으로 검색 버튼을 누른 다음에야 화면이 작아진다
  tl.fromTo('#wB .go', { boxShadow: '0 0 0 0 rgba(107,78,255,.6)' }, { boxShadow: '0 0 0 12px rgba(107,78,255,0)', duration: 0.6, ease: 'power2.out', immediateRender: false }, tGo + 0.05);
  cam(tSmall, R2, 1.05 / SPD1);
  const rowsB = ['#b1', '#b2', '#b3', '#b4'], FL = ['#fl1', '#fl2', '#fl3', '#fl4'];
  gsap.set(rowsB, { opacity: 0, y: 14 }); gsap.set(['#sgB', '#ttlB'], { opacity: 0, y: 10 });
  // 검색을 누른 순간 요약 자리와 연결된 기억이 바로 뜬다(앱은 빠르다)
  tl.to(['#sgB', '#ttlB'], { opacity: 1, y: 0, duration: 0.22, stagger: 0.04, ease: 'expo.out' }, tGo + 0.1);
  tl.to(rowsB, { opacity: 1, y: 0, duration: 0.28, stagger: 0.05, ease: 'expo.out' }, tGo + 0.18);
  // 그다음에 하나씩: 휴대폰 속 줄 → 실 → 줄이 커지듯 카드 → 형광펜. 다음 기록이 오면 앞의 카드는 옅어진다
  gsap.set(FL, { autoAlpha: 0, scale: 0.6, x: 90, transformOrigin: '100% 50%' });
  REC.forEach((t, i) => {
    tl.fromTo(rowsB[i], { boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { boxShadow: '0 0 0 2.5px rgba(107,78,255,.75)', duration: 0.3, immediateRender: false }, t);
    tl.to(rowsB[i], { boxShadow: '0 0 0 0 rgba(107,78,255,0)', duration: 0.35 }, (REC[i + 1] || tWoven) - 0.1);
    tl.to(FL[i], { autoAlpha: 1, scale: 1, x: 0, duration: 0.7 / SPD1, ease: 'back.out(1.2)' }, t + 0.3 / SPD1);
    if (i) tl.to(FL[i - 1], { opacity: 0.5, duration: 0.4 / SPD1 }, t + 0.25 / SPD1);
  });
  mark('#mk1', REC[0] + 1.05 / SPD1, 0.55 / SPD1); mark('#mk4', REC[0] + 1.6 / SPD1, 0.45 / SPD1);                       // 언제 어디서
  mark('#mk6', REC[1] + 0.95 / SPD1, 0.8 / SPD1);                                                           // 그때의 시연 순서 전체
  mark('#mk2', REC[2] + 1.0 / SPD1, 1.0 / SPD1);                                                            // 바뀐 순서
  mark('#mk3', REC[2] + 2.2 / SPD1, 0.45 / SPD1);
  mark('#mk5', REC[3] + 1.0 / SPD1, 0.55 / SPD1);                                                           // 최종본 파일
  // 네 기록이 다 나오면 밝아지고 왼쪽에서 실로 엮인다
  tl.to(['#fl1', '#fl2', '#fl3'], { opacity: 1, duration: 0.4 }, tWoven);
  const L1 = FL.map(k => ({ x: FLR[k].left + 2, y: FLR[k].top + FLR[k].height / 2 }));
  const xb = L1[0].x - 70;
  curve('flc', `M${L1[0].x} ${L1[0].y}` + [1, 2, 3].map(i => ` C ${xb} ${L1[i - 1].y}, ${xb} ${L1[i].y}, ${L1[i].x} ${L1[i].y}`).join(''), tWoven - 0.1, 0.6 / SPD1, 5.5);
  // 요약: 카드를 걷고 요약 상자를 화면 가운데에 크게. 세 문장이 읽는 속도로 한 줄씩
  tl.to([...FL, '#flc'], { autoAlpha: 0, x: -30, duration: 0.45, ease: 'power2.in', stagger: 0.03 }, tSum);
  const sumPose = camPose(2.85, B['#sgB'], { x: 960, y: 462 });
  cam(tSum + 0.1, sumPose, 1.0);
  tl.to(['#wB .wpill', '#ttlB', '#b1', '#b2', '#b3', '#b4'], { opacity: 0.2, duration: 0.5 }, tSum + 0.3);
  tl.to('#sgB', { boxShadow: '0 0 0 2.5px rgba(107,78,255,.8)', duration: 0.4, ease: 'power2.out' }, tSum + 0.7);
  gsap.set(['#sl1', '#sl2', '#sl3'], { clipPath: 'inset(-20% 100% -20% 0)' });
  const SUMD = 1.4;                                                                           // 한 줄을 쓰는 시간. 줄 사이에 멈추지 않는다
  ['#sl1', '#sl2', '#sl3'].forEach((k, i) => {
    const t = tSum + 1.0 + i * SUMD, r = rectOf(k);
    tl.to(`.sumv .skel:nth-child(${i + 1})`, { opacity: 0, duration: 0.25 }, t);
    tl.to(k, { clipPath: 'inset(-20% 0% -20% 0)', duration: SUMD, ease: 'none' }, t);
    $$(`${k} .sumk`).forEach(e => { const m = e.getBoundingClientRect();                       // 글자가 써지는 대로 형광펜이 함께 지나간다(한 줄에 둘이면 둘 다)
      const f0 = (m.left - r.left) / r.width, f1 = (m.right - r.left) / r.width;
      mark(e, t + f0 * SUMD, (f1 - f0) * SUMD); });
  });
  // 작아진 다음에 통화 말풍선이 돌아오고, 답변이 한 줄씩
  tl.to('#sgB', { boxShadow: '0 0 0 0px rgba(107,78,255,0)', duration: 0.4 }, tBack);
  tl.to(['#wB .wpill', '#ttlB', '#b1', '#b2', '#b3', '#b4'], { opacity: 1, duration: 0.5 }, tBack + 0.1);
  const ANS_DX = 290;                                                                         // v20: 제목 없이 말풍선 + 휴대폰 묶음을 화면 가운데로
  cam(tBack, { ...R2, x: R2.x - ANS_DX }, 0.9);
  tl.set('#callQ', { x: -ANS_DX - 24 }, tBack + 0.55);
  tl.to('#callQ', { autoAlpha: 1, x: -ANS_DX, duration: 0.5, ease: 'power2.out' }, tBack + 0.6);
  tl.fromTo('#callA', { autoAlpha: 0, x: -ANS_DX - 20, scale: 0.96, transformOrigin: '100% 50%' }, { autoAlpha: 1, x: -ANS_DX, scale: 1, duration: 0.7, ease: 'back.out(1.4)', immediateRender: false }, tAns);
  const ta = typeChars($('#callA .q'), tAns + 0.3, 20);                                       // 문장이 길어진 만큼 조금 빠르게(초당 18 → 20자)
  ['#ua1', '#ua1b', '#ua2', '#ua2b', '#ua3'].forEach(k => { const [a, b] = ta.spanOf(k); mark(k, a, Math.max(0.2, b - a + 0.06)); });   // 글자가 써지는 대로 형광펜이 함께

  /* ── 3 먼저 건네기: 휴대폰 왼쪽. 제목 → 대화 → 위치 → 탑승권 → 아내 카톡 → 링크 미리보기 → 실 → Weave 버튼 → 추천 → 답장 ── */
  tl.to(['#callQ', '#callA'], { autoAlpha: 0, x: '-=30', duration: 0.45, ease: 'power2.in', stagger: 0.03 }, X2);
  tl.to(phone, { x: '+=420', autoAlpha: 0, filter: 'blur(6px)', duration: 0.45, ease: 'power3.in' }, X2 + 0.05);
  chapIn('#ch3', C3); chapOut('#ch3', C3 + CH);
  tl.set('#scrA', { xPercent: -100 }, C3 + 0.3); tl.set('#scrC', { xPercent: 0 }, C3 + 0.3);
  when(t => t >= C3 + 0.3, on => { $('#sbt').textContent = on ? '15:41' : '13:00'; });
  const R3 = { x: -430, y: 0, scale: 1 };
  tl.set(phone, { x: -1500, y: 0, scale: 1, rotation: 0, filter: 'blur(0px)', autoAlpha: 1 }, s3 - 0.1);
  tl.to(phone, { x: R3.x, duration: 1.0, ease: 'power3.out' }, s3);
  titleIn('#hdC', s3 + 0.4); headOut('#hdC', tChat - 0.45);                                   // 제목이 한 번 뜨고, 02처럼 걷힘(빛 없음)
  // 대화: 아내 → 나 → 아내. 제목이 걷히면 휴대폰을 가운데로 크게
  const chatPose = camPose(2.1, { x: 960, y: MS[2]['#m2'].y + 10 }, { x: 960, y: 560 });
  const reveal = (k, t) => {
    tl.to(k, { height: natH[k], marginTop: 10, duration: 0.38, ease: 'power2.out' }, t);
    tl.fromTo(`${k} .bub`, { scale: 0.7, opacity: 0, transformOrigin: $(k).classList.contains('me') ? '100% 100%' : '0% 0%' },
      { scale: 1, opacity: 1, duration: 0.45, ease: 'back.out(1.6)', immediateRender: false }, t + 0.05);
  };
  gsap.set(['#m2 .bub', '#m3 .bub', '#mSent .bub', '#mReply .bub'], { opacity: 0 });
  cam(tChat - 0.1, chatPose, 0.9);
  tl.fromTo('#m1 .bub', { boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { boxShadow: '0 0 0 3px rgba(107,78,255,.45)', duration: 0.35, yoyo: true, repeat: 1, repeatDelay: 0.4, immediateRender: false }, tChat + 0.7);
  // 나의 답은 입력해서 보낸다
  typeIn($('#kinTx'), '응 방금 도착했어', tM2 - 1.15, 11);
  textAt($('#kinTx'), tM2 + 0.06, { html: PH });
  reveal('#m2', tM2 + 0.06);
  reveal('#m3', tM3);
  cam(g3 - 0.3, R3, 0.9);
  // 플로팅은 하나씩: 위치(면세점 근처) → 그 오른쪽에 탑승권(귀국 중), 둘이 이어짐 → 아래에 아내 카톡(면세점) → 링크 미리보기(이 갈색병의 이름)
  gsap.set(['#fw', '#fg', '#fk'], { autoAlpha: 0, scale: 0.94, x: 40 });
  const popF = (k, t) => tl.to(k, { autoAlpha: 1, scale: 1, x: 0, duration: 0.8, ease: 'back.out(1.4)' }, t);
  popF('#fg', g3 + 0.45);
  tl.fromTo('#fg .pulse', { scale: 1, opacity: 0.9 }, { scale: 2.2, opacity: 0, duration: 1.2, repeat: 1, stagger: 0.6, ease: 'power1.out', immediateRender: false }, g3 + 0.7);
  mark('#gpsDj', g3 + 1.15, 0.5);
  popF('#fw', tW);
  { const a = FLR['#fg'], b = FLR['#fw'], y = a.top + a.height / 2, x0 = a.right - 2, x1 = b.left + 2;   // 위치 → 탑승권: 곧은 실
    const gr = document.createElementNS(svgNS, 'linearGradient');                               // 곧은 줄은 글상자 기준 그라데이션이 안 그려져서 화면 좌표로
    gr.id = 'tgH'; gr.setAttribute('gradientUnits', 'userSpaceOnUse');
    [['x1', x0], ['y1', y], ['x2', x1], ['y2', y]].forEach(([k, v]) => gr.setAttribute(k, v));
    gr.innerHTML = '<stop offset="0" stop-color="#A67CF2"/><stop offset="1" stop-color="#7B4BD8"/>';
    $('#uxThreads').appendChild(gr);
    curve('tgw', `M${x0} ${y} L${x1} ${y}`, tW + 0.65, 0.45, 6);
    $('#tgw .thr').style.stroke = 'url(#tgH)'; }
  tl.to(['#fg', '#fw', '#tgw'], { opacity: 0.5, duration: 0.4 }, tK + 0.1);
  popF('#fk', tK);
  hop('#tokC', DT.g, DT.k, tK + 0.55, 0.85, 40, { mid: { x: Math.max(DT.g.x, DT.k.x) + 110, y: (DT.g.y + DT.k.y) / 2 } });   // 위치의 '면세점'이 아내 카톡의 '면세점'으로
  mark('#kkDj', tK + 1.5, 0.4);
  mark('#kkSs', tK + 1.85, 0.45);                                                             // 그때 말한 '이 갈색병'
  tl.fromTo('#kkBub', { boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { boxShadow: '0 0 0 3px rgba(107,78,255,.85)', duration: 0.4, ease: 'power2.out', immediateRender: false }, tK + 1.85);
  // 아내가 함께 보낸 링크와 미리보기가 펼쳐지고, 제품 이름에 형광펜
  gsap.set('#kkMore', { height: 0, opacity: 0, overflow: 'hidden' });
  tl.to('#kkMore', { height: natMore, opacity: 1, duration: 0.65, ease: 'power2.inOut' }, tL);
  tl.set('#kkMore', { overflow: 'visible' }, tL + 0.67);
  tl.fromTo('#kkPv', { boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { boxShadow: '0 0 0 3px rgba(107,78,255,.85)', duration: 0.4, ease: 'power2.out', immediateRender: false }, tL + 0.8);
  mark('#kkNm', tL + 0.85, 0.5);
  tl.to(['#fg', '#fw', '#tgw'], { opacity: 1, duration: 0.4 }, th3 - 0.35);                    // 실로 엮기 전에 다시 밝게
  const TC = { thread: th3 };
  // 기록들이 휴대폰(키보드 도구줄 높이)으로 엮이면, 빛이 도구줄을 따라가 Weave 버튼이 크게 반짝 — 누르라는 신호
  tl.fromTo('#kbC .shim', { x: 380, opacity: 0 }, { x: -60, opacity: 1, duration: 0.45, ease: 'power1.in', immediateRender: false }, th3 + 0.45).to('#kbC .shim', { opacity: 0, duration: 0.15 }, th3 + 0.9);
  const wvGlow = th3 + 0.85;
  ev(wvGlow, 'glint');
  tl.to('#kbC .wv', { backgroundColor: '#6B4EFF', boxShadow: '0 6px 16px rgba(107,78,255,.55)', duration: 0.3, ease: 'power2.out' }, wvGlow);
  tl.to('#kbC .wv img.lit', { opacity: 1, duration: 0.3 }, wvGlow);
  tl.fromTo('#kbC .wv', { scale: 1 }, { scale: 1.55, duration: 0.42, ease: 'back.out(3)', immediateRender: false }, wvGlow)
    .to('#kbC .wv', { scale: 1.3, duration: 0.3, ease: 'power2.inOut' }, wvGlow + 0.42)
    .to('#kbC .wv', { scale: 1.42, duration: 0.42, yoyo: true, repeat: 2, ease: 'sine.inOut' }, wvGlow + 0.75);
  tl.fromTo('#kbC .wvfx .glow', { scale: 0.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.45, ease: 'power2.out', immediateRender: false }, wvGlow)
    .to('#kbC .wvfx .glow', { scale: 1.25, opacity: 0.65, duration: 0.36, yoyo: true, repeat: 1, ease: 'sine.inOut' }, wvGlow + 0.5);
  tl.fromTo('#kbC .wvfx .rg', { scale: 1, opacity: 0.9 }, { scale: 3.4, opacity: 0, duration: 1.0, stagger: 0.3, ease: 'power2.out', immediateRender: false }, wvGlow + 0.05);
  tl.fromTo('#kbC .wvfx .badge', { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: 'back.out(3)', immediateRender: false }, wvGlow + 0.2);
  const SO = [[-34, -26], [38, -30], [44, 16], [-30, 22]];
  $$('#kbC .wvfx .st').forEach((e, i) => {
    gsap.set(e, { x: SO[i][0], y: SO[i][1] });
    tl.fromTo(e, { scale: 0, opacity: 0, rotation: -30 }, { scale: 1, opacity: 1, rotation: 0, duration: 0.3, yoyo: true, repeat: 1, repeatDelay: 0.12, ease: 'back.out(2)', immediateRender: false }, wvGlow + 0.1 + i * 0.12);
  });
  tl.set(['#kbC .wvfx .badge', '#kbC .wvfx .glow'], { opacity: 0 }, pTapW + 0.1);              // 누르면 배지·빛은 사라지고 시트가 뜬다
  tl.set('#kbC .wv', { scale: 1, backgroundColor: '#E6DEFF', boxShadow: 'none' }, pTapW + 1.0); tl.set('#kbC .wv img.lit', { opacity: 0 }, pTapW + 1.0);
  tl.to(['#fw', '#fg', '#fk'], { autoAlpha: 0, x: 30, duration: 0.4, ease: 'power2.in' }, th3 + 1.25);   // 실이 모이면 플로팅은 걷히고 버튼만
  cam(th3 + 1.25, camPose(1.9, { x: 900, y: B['#kbC .tb'].y + 30 }, { x: 720, y: 540 }), 0.75);
  gsap.set('#wC', { y: 760 }); gsap.set('#scrimC', { opacity: 0 });
  tl.to('#wC', { y: 0, duration: 0.75, ease: 'power3.out' }, pTapW + 0.15);
  tl.to('#scrimC', { opacity: 1, duration: 0.5 }, pTapW + 0.15);
  edge(pTapW + 0.2);
  // 추천 문장을 시트 폭이 다 들어오는 크기로 한 번에 크게
  cam(pTapW + 0.3, camPose(3.0, { x: B['#sgC'].x, y: (B['#sgC'].y + B['#btnC'].y) / 2 }, { x: 960, y: 500 }), 1.05);
  tl.fromTo('#sgC', { boxShadow: '0 0 0 0 rgba(107,78,255,0)' }, { boxShadow: '0 0 0 2.5px rgba(107,78,255,.8)', duration: 0.4, ease: 'power2.out', immediateRender: false }, pTapW + 1.3);
  mark('#sgK', pTapW + 1.35, 0.6); mark('#sgK2', pTapW + 2.0, 0.4);                                                         // 기억에서 온 부분: '에스티 로더 갈색병', '면세점'
  tl.to('#wC', { y: 760, duration: 0.55, ease: 'power3.in' }, pTapI + 0.25);
  tl.to('#scrimC', { opacity: 0, duration: 0.45 }, pTapI + 0.3);
  textAt($('#kinTx'), pTapI + 0.4, { html: MSGTX });
  cam(pTapI + 0.3, camPose(2.05, { x: 970, y: (MS[4]['#mSent'].y + MS[4]['#mReply'].y) / 2 }, { x: 960, y: 540 }), 0.85);   // 입력하기 뒤로는 한 자리: 입력창과 대화가 함께 담긴다
  textAt($('#kinTx'), pTapS + 0.1, { html: PH });
  reveal('#mSent', pTapS + 0.1);
  tl.to('#rdSent', { opacity: 0, duration: 0.2 }, tRead);
  reveal('#mReply', tReply); ev(tReply, 'msg');

  /* ── 끝 화면 (LOGO ~ DUR): 로고·문구를 충분히 읽을 수 있게 ── */
  tl.to(phone, { y: '+=70', scale: '-=0.15', autoAlpha: 0, filter: 'blur(6px)', duration: 0.5, ease: 'power3.in' }, tTrio - 0.35);
  // 세 화면이 나란히 모여 5쪽 Solution으로 이어진다
  gsap.set('#trio .tp', { y: 90, opacity: 0, scale: 0.94 });
  tl.set('#trio', { autoAlpha: 1 }, tTrio - 0.05);
  tl.to('#trio .tp', { y: 0, opacity: 1, scale: 1, duration: 0.85, stagger: 0.16, ease: 'expo.out' }, tTrio);
  tl.to('#trio', { opacity: 0, y: -30, filter: 'blur(8px)', duration: 0.45, ease: 'power2.in' }, LOGO - 0.42);
  const gifs = $$('#trio .gif img');                                                          // 옛 데모 GIF처럼: 저마다 20fps로 넘어가고(거의 실제 빠르기), 시작이 조금씩 어긋난다
  cont.push(t => { if (t < tTrio - 0.3 || t > LOGO + 0.1) return;
    gifs.forEach((im, i) => { const f = clamp(Math.floor((t - tTrio - GIF.off[i]) * GIF.fps), 0, GIF.n - 1);
      if (im._f !== f) { im._f = f; im.style.transform = `translate(${-(f % GIF.cols) * GIF.w}px, ${-Math.floor(f / GIF.cols) * GIF.h}px)`; } }); });
  gsap.set('#logo .mark', { scale: 0.4, rotation: -30, opacity: 0 });
  gsap.set('#logo .word', { clipPath: 'inset(-50% 100% -50% -4%)', x: -30, autoAlpha: 0 });   // 감춰 두지 않으면 글자 그림자가 처음부터 옅게 비침
  gsap.set('#sub', { y: 24, opacity: 0 });
  gsap.set('#fin', { opacity: 0 });
  tl.to('#logo .mark', { scale: 1, rotation: 0, opacity: 1, duration: 1.0, ease: 'back.out(1.6)' }, LOGO - 0.05); ev(LOGO, 'logo');
  tl.set('#logo .word', { autoAlpha: 1 }, LOGO + 0.25);
  tl.to('#logo .word', { clipPath: 'inset(-50% -5% -50% -4%)', x: 0, duration: 1.0, ease: 'expo.out' }, LOGO + 0.25);
  sweep('#logo .word', LOGO + 1.1, 1.3);
  tl.to('#sub', { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out' }, LOGO + 0.95);           // v21: 오프닝처럼 로고 글자 0.7초 뒤에 한 줄(수미상관)
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
  const pM = at(tM2 - 0.1, '#kSend');
  const p1 = at(pTap1 - 0.1, '#kbA .wv');
  const p2 = at(T2 - 0.1, '#btnCC');
  const p3 = at(pTap3 - 0.1, '#kbA .srch');
  const pW = at(pTapW - 0.1, '#kbC .wv');
  const pI = at(pTapI - 0.1, '#btnC');
  const pS = at(pTapS - 0.1, '#kSend');
  const h0 = at(dragT - 0.05, '#wB .grab');
  const pGo = at(tGo - 0.1, '#wB .go');
  const ansR = atR(T2 + 0.05, '#ansC');
  const ansFs = parseFloat(getComputedStyle($('#ansC')).fontSize);
  const sqR = atR(T2 + 1.35, '#sqA');
  const rb = rowsB.map(k => atR(tWoven, k));
  const frC = atR(TC.thread, '#phone .frame');
  const wvG = at(wvGlow, '#kbC .wv');
  const tbC = at(TC.thread, '#kbC .tb');
  // 1: 위로 끄는 동안 손끝이 시트 윗부분을 따라가도록 자리를 촘촘히 잰다(카메라도 같이 움직이므로)
  const NS = 21, dragPts = [];
  for (let i = 0; i <= NS; i++) { const t = dragT + dragD * i / NS; dragPts.push({ t, ...at(t, '#wB .grab') }); }
  seekAll(0);
  if (DEBUG) $('#dbg').innerHTML = [p1, p2, p3, pW, pI, pS, h0, pGo].map(p => `<i style="left:${p.x}px; top:${p.y}px"></i>`).join('');

  gsap.set(hand, { x: 2100, y: 1200, rotation: -12, autoAlpha: 0 });
  gsap.set(spark, { autoAlpha: 0 });
  gsap.set('#htrail', { rotation: 12, height: 0 }); gsap.set('#htouch', { opacity: 0, scale: 0.6 });
  handIn(pM.x, pM.y, tM2, 0.6); press(pM.x, pM.y, tM2, '#kSend'); handOut(tM2 + 0.3);
  handIn(p1.x, p1.y, pTap1); press(p1.x, p1.y, pTap1, '#kbA .wv'); handOut(pTap1 + 0.2);
  tl.fromTo('#pill', { x: p1.x - DT.pill.x, y: p1.y - DT.pill.y, scale: 0.3, autoAlpha: 0 }, { x: 0, y: 0, scale: 1, autoAlpha: 1, duration: 1.1, ease: 'expo.out', immediateRender: false }, pTap1 + 0.5);
  tl.to(['#pill', '#tA', '#tQ2', '#pen1'], { autoAlpha: 0, duration: 0.5 }, c3);              // 검색창이 걷히면 거기서 나온 실과 첫 질문도 같이
  handIn(p2.x, p2.y, T2); press(p2.x, p2.y, T2, '#btnCC'); handOut(T2 + 0.3);
  // 답이 칩이 되어 검색창으로 날아간다
  const sc0 = ansFs * wsA / 44, sc1 = 15.5 * boxPose.scale / 44;     // 답 글자 크기(사슬 wsA배) → 검색창 글자 크기(휴대폰 2배)
  gsap.set('#flyChip', { x: ansR.left - 26 * sc0, y: ansR.top + ansR.height / 2, yPercent: -50, scale: sc0, transformOrigin: '0% 50%' });
  tl.to('#flyChip', { autoAlpha: 1, duration: 0.08 }, T2 + 0.12);
  tl.set('#ansC', { opacity: 0 }, T2 + 0.2);                                         // 카드의 글자가 칩이 되어 떠난다
  tl.to('#flyChip', { scale: sc0 * 1.06, duration: 0.25, ease: 'power2.out' }, T2 + 0.12);
  tl.to('#flyChip', { x: sqR.left - 26 * sc1, y: sqR.top + sqR.height / 2, scale: sc1, duration: 0.7, ease: 'power3.inOut' }, T2 + 0.55);
  tl.to('#flyChip', { autoAlpha: 0, duration: 0.18 }, T2 + 1.2);
  handIn(p3.x, p3.y, pTap3, 0.6); press(p3.x, p3.y, pTap3, '#kbA .srch'); handOut(pTap3 + 0.3);
  // 1: 손잡이를 누르고 위로 끌어 올린다
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
  // 1: 입력을 마치면 손으로 검색 버튼을 누른다(누른 다음에 화면이 작아진다)
  handIn(pGo.x, pGo.y, tGo, 0.65); press(pGo.x, pGo.y, tGo, '#wB .go'); handOut(tGo + 0.2);
  // 1: 기록마다 휴대폰 속 줄 → 왼쪽 큰 카드로 실이 한 가닥씩. 다음 기록이 오면 앞의 실은 옅어지고, 요약 전에 걷힘
  const tb = FL.map((k, i) => curve(`tb${i}`, bez({ x: rb[i].left + 8, y: rb[i].top + rb[i].height / 2 }, { x: FLR[k].right - 2, y: FLR[k].top + FLR[k].height / 2 }, 0.55), REC[i] + 0.06, 0.5));
  tb.forEach((g, i) => { if (REC[i + 1]) tl.to(g, { opacity: 0.3, duration: 0.4 / SPD1 }, REC[i + 1] + 0.25 / SPD1); });
  tl.to(tb, { opacity: 1, duration: 0.4 }, tWoven);
  tl.to(tb, { autoAlpha: 0, duration: 0.4 }, tSum);
  // 3: 위치와 아내 카톡이 휴대폰 오른쪽 키보드 도구줄 높이로 모인다(탑승권은 위치에 이어져 있음)
  const K = { x: frC.right - 6, y: tbC.y };
  const lm = (k, u = 0.5) => ({ x: FLR[k].left + 2, y: FLR[k].top + FLR[k].height * u });
  const tg = [curve('tg1', bez(lm('#fg'), K, 0.6), TC.thread, 0.55, 6), curve('tg3', bez(lm('#fk', 0.42), K, 0.6), TC.thread + 0.15, 0.55, 6)];
  tl.to([...tg, '#tgw'], { autoAlpha: 0, duration: 0.35 }, th3 + 1.25);
  sparkAt(wvG.x, wvG.y, wvGlow);
  handIn(pW.x, pW.y, pTapW); press(pW.x, pW.y, pTapW, null); handOut(pTapW + 0.3);
  handIn(pI.x, pI.y, pTapI); press(pI.x, pI.y, pTapI, '#btnC'); handOut(pTapI + 0.3);
  handIn(pS.x, pS.y, pTapS, 0.6); press(pS.x, pS.y, pTapS, '#kSend'); handOut(pTapS + 0.3);

  window.__events = EV.sort((a, b) => a.t - b.t);
  window.__taps = { p1, p2, p3, pW, pI, pS, h0, pGo, lift };
  window.__gif = GIF;
  window.__marks = { pTap3, tZ, tW, tRead, logo: LOGO, logoMin: LOGO_MIN, trio: tTrio, x1: X1, x2: X2, drop: D1, bar: BAR, ch1: C1, p0: P0, pTap1, c1, c2, c3, c4, t2: T2, ch2: C2, s2, tCall, tFocus, dragT, tType, tGo, tSmall, tRec, rec: REC, tWoven, tSum, tBack, tAns, ch3: C3, s3, tChat, tM2, tM3, g3, tK, tL, th3, wvGlow, tapW: pTapW, tapI: pTapI, tapS: pTapS, reply: tReply, dur: DUR };
  seekAll(0);
  return true;
}

window.__DURATION = DUR;
window.__seek = t => seekAll(t);
window.__ready = build();
