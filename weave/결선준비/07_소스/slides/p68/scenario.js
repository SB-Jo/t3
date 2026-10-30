// 6~8쪽 공통 그리기 도구. 페이지는 SC.run(async (sc) => { ... })로 그림을 그리고, 끝나면 window.pageReady = true.
const SC = (() => {
  const NS = 'http://www.w3.org/2000/svg';
  const slide = () => document.getElementById('slide');
  const R = (el) => {
    const s = slide().getBoundingClientRect();
    const r = (typeof el === 'string' ? document.getElementById(el) : el).getBoundingClientRect();
    return { l: r.left - s.left, t: r.top - s.top, r: r.right - s.left, b: r.bottom - s.top, w: r.width, h: r.height,
             cx: r.left - s.left + r.width / 2, cy: r.top - s.top + r.height / 2 };
  };
  const svgLayer = (cls) => {
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('class', 'fx ' + cls);
    svg.innerHTML = `<defs>
      <marker id="ah-${cls}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 9 5 1 9z" fill="#8B6BFF"/></marker>
      <linearGradient id="spark-${cls}" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#A67CF2"/><stop offset="1" stop-color="#7B4BD8"/></linearGradient>
      <radialGradient id="glow-${cls}"><stop offset=".45" stop-color="#8B6BFF" stop-opacity=".55"/><stop offset="1" stop-color="#8B6BFF" stop-opacity="0"/></radialGradient>
      <linearGradient id="up-${cls}" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#8B6BFF" stop-opacity="0"/><stop offset=".45" stop-color="#8B6BFF" stop-opacity=".8"/><stop offset="1" stop-color="#6B4EFF"/></linearGradient>
      <filter id="bshadow-${cls}" x="-20%" y="-30%" width="140%" height="170%"><feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#6B4EFF" flood-opacity=".13"/></filter>
    </defs>`;
    slide().appendChild(svg);
    return svg;
  };
  const el = (parent, tag, attrs) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; };

  // 말풍선: 둥근 사각형 + (꼬리 | 생각 방울). tail = {edge:'bottom'|'top'|'left'|'right', at: 모서리 시작점에서의 거리, to:[x,y], w: 꼬리 밑변}
  function bubble(svg, o) {
    const { x, y, w, h } = o, r = o.r || 18;
    const t = o.tail;
    let d = `M${x + r} ${y}`;
    const seg = (edge, x1, y1) => {
      if (t && !o.thought && t.edge === edge) {
        const bw = t.w || 22;
        if (edge === 'top')    d += ` L${x + t.at - bw / 2} ${y} Q${x + t.at - bw * .1} ${y} ${t.to[0]} ${t.to[1]} Q${x + t.at + bw * .25} ${y} ${x + t.at + bw / 2} ${y}`;
        if (edge === 'right')  d += ` L${x + w} ${y + t.at - bw / 2} Q${x + w} ${y + t.at - bw * .1} ${t.to[0]} ${t.to[1]} Q${x + w} ${y + t.at + bw * .25} ${x + w} ${y + t.at + bw / 2}`;
        if (edge === 'bottom') d += ` L${x + t.at + bw / 2} ${y + h} Q${x + t.at + bw * .1} ${y + h} ${t.to[0]} ${t.to[1]} Q${x + t.at - bw * .25} ${y + h} ${x + t.at - bw / 2} ${y + h}`;
        if (edge === 'left')   d += ` L${x} ${y + t.at + bw / 2} Q${x} ${y + t.at + bw * .1} ${t.to[0]} ${t.to[1]} Q${x} ${y + t.at - bw * .25} ${x} ${y + t.at - bw / 2}`;
      }
      d += ` L${x1} ${y1}`;
    };
    seg('top', x + w - r, y);       d += ` Q${x + w} ${y} ${x + w} ${y + r}`;
    seg('right', x + w, y + h - r); d += ` Q${x + w} ${y + h} ${x + w - r} ${y + h}`;
    seg('bottom', x + r, y + h);    d += ` Q${x} ${y + h} ${x} ${y + h - r}`;
    seg('left', x, y + r);          d += ` Q${x} ${y} ${x + r} ${y} Z`;
    const g = el(svg, 'g', { filter: `url(#bshadow-${svg.classList[1]})` });
    el(g, 'path', { d, fill: o.fill || '#FFFFFF', stroke: o.stroke || '#DCD2FA', 'stroke-width': 1.4, 'stroke-linejoin': 'round' });
    if (o.thought && t) {   // 생각 방울 두 개
      const ex = x + (t.edge === 'left' ? 0 : t.edge === 'right' ? w : t.at), ey = y + (t.edge === 'top' ? 0 : t.edge === 'bottom' ? h : t.at);
      [[.42, 6.5], [.78, 4]].forEach(([k, rr]) => el(g, 'circle', { cx: ex + (t.to[0] - ex) * k, cy: ey + (t.to[1] - ey) * k, r: rr, fill: '#fff', stroke: '#DCD2FA', 'stroke-width': 1.3 }));
    }
    return g;
  }

  // 실(연결선): from/to = [x,y], 부드러운 S자. dash면 점선, dot면 양 끝 점
  function thread(svg, a, b, o = {}) {
    const dx = (b[0] - a[0]) * (o.k || .5);
    const d = `M${a[0]} ${a[1]} C ${a[0] + dx} ${a[1]}, ${b[0] - dx} ${b[1]}, ${b[0]} ${b[1]}`;
    el(svg, 'path', { d, fill: 'none', stroke: '#FFFFFF', 'stroke-width': (o.w || 2) + 2.6, 'stroke-linecap': 'round', opacity: .9 });
    el(svg, 'path', { d, fill: 'none', stroke: o.c || '#8B6BFF', 'stroke-width': o.w || 2, 'stroke-linecap': 'round', ...(o.dash ? { 'stroke-dasharray': o.dash } : {}),
      ...(o.arrow ? { 'marker-end': `url(#ah-${svg.classList[1]})` } : {}) });
    if (o.dots !== false) { el(svg, 'circle', { cx: a[0], cy: a[1], r: 3.4, fill: o.c || '#8B6BFF', stroke: '#fff', 'stroke-width': 1.5 });
      if (!o.arrow) el(svg, 'circle', { cx: b[0], cy: b[1], r: 3.4, fill: o.c || '#8B6BFF', stroke: '#fff', 'stroke-width': 1.5 }); }
  }

  // 반짝임 선 (덱 공통 터치 표시)
  function spark(svg, c, r0, angles, lens, wide) {
    const d = angles.map((ang, i) => { const t = ang * Math.PI / 180, L = lens[i];
      return `M${c[0] + r0 * Math.cos(t)} ${c[1] + r0 * Math.sin(t)}L${c[0] + (r0 + L) * Math.cos(t)} ${c[1] + (r0 + L) * Math.sin(t)}`; }).join('');
    el(svg, 'path', { d, stroke: '#fff', 'stroke-width': wide ? 4.2 : 3.3, 'stroke-linecap': 'round', fill: 'none' });
    el(svg, 'path', { d, stroke: `url(#spark-${svg.classList[1]})`, 'stroke-width': wide ? 2.3 : 1.75, 'stroke-linecap': 'round', fill: 'none' });
  }

  // 누르는 손 (2쪽 만화 4컷과 같은 아이콘). tip = 손끝 좌표, rot = 기울기(누르기 -12, 밀기 0), k = 크기 배율,
  // left = 왼손(좌우 반전 아이콘, 기울기는 보통 +12)
  function hand(tip, rot = -12, k = 1, left = false) {
    const W = 27.6 * k, H = 35.5 * k;
    const TIP = left ? [48.7 / 80, 4.4 / 102] : [31.3 / 80, 4.4 / 102], ORG = left ? [.65, .08] : [.35, .08];
    const tx = TIP[0] * W, ty = TIP[1] * H, ox = ORG[0] * W, oy = ORG[1] * H, a = rot * Math.PI / 180, rx = tx - ox, ry = ty - oy;
    const x2 = ox + rx * Math.cos(a) - ry * Math.sin(a), y2 = oy + rx * Math.sin(a) + ry * Math.cos(a);
    const img = document.createElement('img');
    img.src = left ? '../../assets/icons/tap-hand-left.svg' : '../../assets/icons/tap-hand.svg';
    img.className = 'app handimg';
    Object.assign(img.style, { left: (tip[0] - x2) + 'px', top: (tip[1] - y2) + 'px', width: W + 'px', height: H + 'px', zIndex: 28,
      transform: `rotate(${rot}deg)`, transformOrigin: `${ORG[0] * 100}% ${ORG[1] * 100}%` });
    slide().appendChild(img);
    return img;
  }

  // 글자에 맞춰 상자(말풍선·카드) 크기를 정함. anchor='right'면 상자 오른쪽 끝을 고정. 글자 상자도 함께 옮김.
  function fit(textId, boxId, o = {}) {
    const t = document.getElementById(textId), b = document.getElementById(boxId);
    const tr = R(t), br = R(b);
    const px = o.px ?? 12, py = o.py ?? 6;
    const w = tr.w + 2 * px, h = tr.h + 2 * py;
    const left = o.left ?? (o.anchor === 'right' ? (o.right ?? br.r) - w : br.l);
    const top = o.top ?? br.t;
    Object.assign(b.style, { left: left + 'px', top: top + 'px', width: w + 'px', height: h + 'px' });
    Object.assign(t.style, { left: (left + px) + 'px', top: (top + py) + 'px' });
    return R(b);
  }
  // 요소를 (x, y)로 옮김 (왼쪽 위 기준)
  function moveTo(id, x, y) { const e = document.getElementById(id); if (x != null) e.style.left = x + 'px'; if (y != null) e.style.top = y + 'px'; return R(e); }

  // 흐름 배지: 번호 + 두세 단어. (x, y) = 왼쪽 위
  function step(n, label, x, y) {
    const s = slide();
    const probe = document.createElement('span');
    probe.style.cssText = 'position:absolute;visibility:hidden;font-size:12.5px;font-weight:700;font-family:Inter,"Noto Sans KR";white-space:nowrap';
    probe.textContent = label; s.appendChild(probe);
    const tw = probe.getBoundingClientRect().width; probe.remove();
    const box = document.createElement('div');
    box.className = 'step'; Object.assign(box.style, { left: x + 'px', top: y + 'px', width: (tw + 36) + 'px' });
    box.appendChild(document.createElement('i'));
    s.appendChild(box);
    const nn = document.createElement('div'); nn.className = 'step-n'; nn.dataset.x = '';
    Object.assign(nn.style, { left: (x + 3.5) + 'px', top: (y + 3.5) + 'px' }); nn.textContent = n; s.appendChild(nn);
    const t = document.createElement('div'); t.className = 'step-t'; t.dataset.x = '';
    Object.assign(t.style, { left: (x + 27) + 'px', top: (y + 4) + 'px' }); t.textContent = label; s.appendChild(t);
  }

  // 휴대폰: 화면 캡처 폭 sw(px)로. 반환: 화면 원점과 배율 (캡처 좌표 → 장표 좌표)
  function phone(id, x, y, sw, src, natW, natH) {
    const k = sw / natW, sh = natH * k;
    const box = document.createElement('div');
    box.className = 'phone'; box.id = id;
    Object.assign(box.style, { left: x + 'px', top: y + 'px', width: (sw + 18) + 'px', height: (sh + 18) + 'px' });
    const img = document.createElement('img'); img.className = 'screen'; img.src = src;
    Object.assign(img.style, { width: sw + 'px', height: sh + 'px' });
    box.appendChild(img); slide().appendChild(box);
    return { x0: x + 9, y0: y + 9, k, at: (px, py) => [x + 9 + px * k, y + 9 + py * k] };
  }

  async function run(fn) {
    await document.fonts.ready;
    await Promise.all([...document.images].map((i) => i.decode().catch(() => null)));
    const sc = { R, el, bubble, thread, spark, hand, fit, moveTo, step, phone, back: svgLayer('back'), front: svgLayer('front') };
    await fn(sc);
    await Promise.all([...document.images].map((i) => i.decode().catch(() => null)));
    window.pageReady = true;
  }
  return { run };
})();
