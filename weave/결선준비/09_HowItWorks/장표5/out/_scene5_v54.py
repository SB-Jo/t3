"""v5 장면 틀 — 시나리오 하나(SPEC) → 모핑 장면 13~15장 (2026-11-01, 5차 피드백).

v4에서 바꾼 것
- 기록은 격자가 아니라 여기저기 흩어진 조각이다(인트로 첫 부분처럼, 더 많이). 처음엔 옅게 떠 있고, 단계마다 일부만 진해진다.
- 실패는 일반 검색이 '어떻게' 찾는지 보여 준다. 키워드 검색(BM25)은 같은 단어에 형광펜, 임베딩 검색은 뜻이 비슷한 기록.
  근거가 분명한 판은 한 장(일반 검색 = 둘을 합친 것), 실패 유형을 보여 줄 판은 두 장(키워드 → 임베딩, 합쳐도 안 됨).
- 장을 합쳤다. 질문 나누기 + 빈칸, 빈칸 채우기 + 다시 쓴 질문. 멈춤은 정리 장의 '멈춤' 알약으로.
- 가까이 볼 때는 기록 하나만 크게(후보와 이유 태그는 찾기 장에서).
- 기술 용어를 조금 쓴다: Query Rewriting, Reasoning Embedding의 Hop 1·2, 키워드 검색 BM25, 임베딩 검색.
- 설명은 짧은 어구로. '~요'만 이어지지 않게.
"""
from dataclasses import dataclass, field
from itertools import combinations

import hiw_lib as L
import story as S
from story import (BODY, GRAY_FILL, GRAY_HL, GRAY_LINE, HL, INK, INK2, LAV, LAV2, LINE, LINE2, MUTE, PURPLE, PURPLE2,
                   RING, SUB, C, P, R, T, band, card_prims, chip_prims, scurve, tw, vcurve)

VIEW = (40, 96, 1240, 704)      # 카메라가 비추는 화면(위 띠 아래)
CAP_PT, CAP_LH = 23, 33         # 설명 제목 글자 크기, 줄 높이
SUB_PT, SUB_LH = 13, 19
CAP_W = 330                     # 옆에 붙는 설명의 최대 폭
GAP = 34                        # 초점과 설명 사이
MARGIN = 26


@dataclass
class Step:
    key: str
    cam: tuple
    cap: list
    cap_rect: tuple
    show: list
    focus: set
    half: set = field(default_factory=set)
    styles: dict = field(default_factory=dict)
    hud: dict = field(default_factory=dict)
    anim: dict = field(default_factory=dict)
    notes: str = ''
    morph_ms: int = 1400
    label: str = ''
    alpha: dict = field(default_factory=dict)      # 키 → 불투명도(%) 따로 줄 때(옅은 기록 더미 등)


def bbox(prims):
    xs, ys = [], []
    for p in prims:
        if p[0] in ('rect', 'text'):
            x, y, w, h = p[2], p[3], p[4], p[5]
        elif p[0] == 'pic':
            x, y, w, h = p[3], p[4], p[5], p[6]
        else:
            xs += [q[0] for q in p[2]]
            ys += [q[1] for q in p[2]]
            continue
        xs += [x, x + w]
        ys += [y, y + h]
    return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


def union(boxes):
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes)
    y1 = max(b[1] + b[3] for b in boxes)
    return (x0, y0, x1 - x0, y1 - y0)


# ------------------------------------------------------------------ 글줄 나누기(조사·어미·쉼표 뒤에서 고르게)
GOOD_END = ('이', '가', '은', '는', '을', '를', '에', '엔', '도', '만', '로', '고', '서', '면', '데', '요', '려', '며', '어', '아',
            '해', '지만', '께', '부터', '까지', '처럼', '보다', '마다', '에게', '한테', '지', '자', '게', '야', '나', '?')
BOUND = {'수', '것', '것이', '것을', '것은', '게', '건', '줄', '뿐', '듯', '때'}


def _brk_cost(word, nxt=None):
    t = ''.join(x for x, _ in word).rstrip('’”\'")')
    if nxt is not None and (''.join(x for x, _ in nxt) in BOUND or ''.join(x for x, _ in nxt).startswith('싶')):
        return 160
    if t and t[-1] in ',?!…':
        return -80
    return 0 if t.endswith(GOOD_END) else 120


def _segments(runs):
    segs, cur = [[]], []
    for t, c in runs:
        for ch in t:
            if ch in ('\n', ' '):
                if cur:
                    segs[-1].append(cur)
                    cur = []
                if ch == '\n':
                    segs.append([])
            elif cur and cur[-1][1] == c:
                cur[-1] = (cur[-1][0] + ch, c)
            else:
                cur.append((ch, c))
    if cur:
        segs[-1].append(cur)
    return [sg for sg in segs if sg]


def _split(words, pt, maxw, weight):
    n = len(words)
    txt = [''.join(x for x, _ in w) for w in words]

    def W(a, b):
        return tw(' '.join(txt[a:b]), pt, weight)
    greedy, i = [], 0
    while i < n:
        j = i + 1
        while j < n and W(i, j + 1) <= maxw:
            j += 1
        greedy.append((i, j))
        i = j
    k = len(greedy)
    if k == 1 or n > 16:
        return greedy
    best, best_c = greedy, None
    for br in combinations(range(1, n), k - 1):
        bd = [0] + list(br) + [n]
        segs = list(zip(bd[:-1], bd[1:]))
        ws = [W(a, b) for a, b in segs]
        if max(ws) > maxw:
            continue
        c = max(ws) + sum(_brk_cost(words[b - 1], words[b]) for b in br)
        if best_c is None or c < best_c:
            best, best_c = segs, c
    return best


def wrap_runs(runs, pt, width, weight='b'):
    out = []
    for words in _segments(runs):
        for a, b in _split(words, pt, width, weight):
            line = []
            for k, w in enumerate(words[a:b]):
                parts = list(w)
                if k < b - a - 1:
                    parts[-1] = (parts[-1][0] + ' ', parts[-1][1])
                for t, c in parts:
                    if line and line[-1][1] == c:
                        line[-1] = (line[-1][0] + t, c)
                    else:
                        line.append((t, c))
            out.append(line)
    return out


def wrap(text, pt, width, weight='r'):
    return [''.join(t for t, _ in ln) for ln in wrap_runs([(text, None)], pt, width, weight)]


def line_w(line, pt, weight='b'):
    return tw(''.join(t for t, _ in line).rstrip(), pt, weight)


def fit_pt(text, maxw, pt=9.5, weight='b', lo=7.5):
    while tw(text, pt, weight) > maxw and pt > lo:
        pt -= 0.5
    return pt


# ------------------------------------------------------------------ 위 띠(01~04)
STAGES = [('01', '순간 감지'), ('02', '질문 다시 쓰기'), ('03', '연쇄 탐색'), ('04', '전달')]
STAGES0 = [('00', '사전 준비')] + STAGES        # 00판: 기록을 미리 벡터 + 메타데이터로 저장하는 단계까지


def bar_layout(stages=STAGES):
    widths = [24 + 8 + tw(ko, 10.5, 'b') + 22 for _, ko in stages]
    gap = 30 if len(stages) <= 4 else 28
    total = sum(widths) + gap * (len(stages) - 1)
    x = 720 - total / 2
    out = []
    for w in widths:
        out.append((x, w))
        x += w + gap
    return out


def topbar_prims(h):
    """h = dict(cur, done, loop, loop_on, all)."""
    y0, hh = 16, 40
    cw = tw('HOW IT WORKS', 10.5, 'sb') + 32
    out = [R('top/chip', 40, y0 + 6, cw, 28, prst='roundRect', fill=PURPLE, line=None),
           T('top/chip_t', 40, y0 + 6, cw, 28, 'HOW IT WORKS', size=10.5, color='FFFFFF', weight='sb', align='c', anchor='ctr',
             spc=0.5)]
    stages = h.get('stages', STAGES)
    ids = [s_ for s_, _ in stages]
    lay = bar_layout(stages)
    x0, x1 = lay[0][0], lay[-1][0] + lay[-1][1]
    out.append(R('top/bar', x0 - 12, y0, x1 - x0 + 24, hh, prst='roundRect', fill='FFFFFF', alpha=94, line=LINE,
                 shadow=S.L.SHADOW_SOFT))
    cur, done = h.get('cur'), h.get('done', set())
    if cur:
        i = ids.index(cur)
        x, w = lay[i]
        out.append(R('top/hl', x - 4, y0 + 4, w + 8, hh - 8, prst='roundRect', fill=LAV, line=RING, line_w=1.6, glow=(8, RING, 30)))
    for i, ((no, ko), (x, w)) in enumerate(zip(stages, lay)):
        state = 'cur' if no == cur else ('done' if (no in done or h.get('all')) else 'todo')
        bf, bt, lc, lw = {'cur': (PURPLE, 'FFFFFF', INK, 'b'), 'done': ('DCD3FF', PURPLE, PURPLE, 'b'),
                          'todo': ('F1EEF8', 'C3BDD2', 'BDB7CC', 'sb')}[state]
        cy = y0 + hh / 2
        out.append(R('top/b%s' % no, x + 8, cy - 11, 22, 22, prst='ellipse', fill=bf, line=None))
        out.append(T('top/bn%s' % no, x + 8, cy - 11, 22, 22, '✓' if state == 'done' else no, size=8, color=bt, weight='b',
                     align='c', anchor='ctr'))
        out.append(T('top/l%s' % no, x + 36, y0, w - 34, hh, ko, size=10.5, color=lc, weight=lw, anchor='ctr'))
        if i < len(stages) - 1:
            gx_ = (lay[i + 1][0] - x - w)
            out.append(T('top/a%d' % i, x + w + gx_ / 2 - 11, y0, 22, hh, '→', size=10, color='C9C0E8', align='c', anchor='ctr'))
    if h.get('loop'):
        (x2, w2), (x3, w3) = lay[ids.index('02')], lay[ids.index('03')]
        a, b = (x3 + w3 / 2, y0 + hh - 1), (x2 + w2 / 2, y0 + hh - 1)
        on = h.get('loop_on')
        col = PURPLE if on else '9A90C8'
        out.append(C('top/loop', [a, (a[0], y0 + hh + 26), (b[0], y0 + hh + 26), b], w=2.4 if on else 1.8, color=col))
        out.append(T('top/loop_head', b[0] - 7, y0 + hh - 2, 14, 12, '▲', size=7.5, color=col, align='c', anchor='ctr'))
        lab = '반복'
        lw_ = tw(lab, 10, 'b') + 20
        out.append(R('top/loop_bg', (a[0] + b[0]) / 2 - lw_ / 2, y0 + hh + 13, lw_, 22, prst='roundRect', fill='FFFFFF', line=None))
        out.append(T('top/loop_t', (a[0] + b[0]) / 2 - lw_ / 2, y0 + hh + 13, lw_, 22, lab, size=10, color=col, weight='b',
                     align='c', anchor='ctr'))
        out.append(R('top/cnt', x3 + w3 - 14, y0 - 6, 20, 20, prst='ellipse', fill=PURPLE, line='FFFFFF', line_w=1.5))
        out.append(T('top/cnt_t', x3 + w3 - 14, y0 - 6, 20, 20, str(h['loop']), size=8.5, color='FFFFFF', weight='b', align='c',
                     anchor='ctr'))
    return out


# ------------------------------------------------------------------ 설명 + 카메라
def cap_measure(cap, side):
    """cap = dict(t=[(글자, 색)], s='부제', pill='배지'). 돌려줌: (제목 줄, 부제 줄, 폭, 높이)."""
    maxw = CAP_W if side in ('left', 'right') else 820
    tl = wrap_runs(cap['t'], CAP_PT, maxw)
    sl = wrap(cap['s'], SUB_PT, maxw, 'r') if cap.get('s') else []
    pw = (tw(cap['pill'], 13, 'b') + 64) if cap.get('pill') else 0
    w = max([line_w(ln, CAP_PT) for ln in tl] + [tw(s, SUB_PT) for s in sl] + [pw]) + 6
    h = len(tl) * CAP_LH + (8 + len(sl) * SUB_LH if sl else 0) + (14 + 34 if cap.get('pill') else 0)
    return tl, sl, w, h


def frame(box, side, zmax, cw, ch, pad=16, cap_y=None, cap_x=None):
    """초점 상자(세계) + 옆에 붙을 설명(cw×ch) → 카메라 (cx, cy, z, vx, vy)와 설명 자리(화면)."""
    vx0, vy0, vx1, vy1 = VIEW
    VW, VH = vx1 - vx0, vy1 - vy0
    bx, by, bw, bh = box[0] - pad, box[1] - pad, box[2] + 2 * pad, box[3] + 2 * pad
    if side in ('left', 'right'):
        z = min(zmax, (VW - 2 * MARGIN - GAP - cw) / bw, (VH - 2 * MARGIN) / bh)
        Wt = bw * z + GAP + cw
        Lx = vx0 + (VW - Wt) / 2
        fx0 = Lx if side == 'right' else Lx + cw + GAP
        fcx, fcy = fx0 + bw * z / 2, vy0 + VH / 2
        capx = fx0 + bw * z + GAP if side == 'right' else Lx
        capy = min(max(fcy - ch / 2, vy0 + 12), vy1 - ch - 12)
    else:
        z = min(zmax, (VW - 2 * MARGIN) / bw, (VH - 2 * MARGIN - GAP - ch) / bh)
        Ht = bh * z + GAP + ch
        Ty = vy0 + (VH - Ht) / 2
        fy0 = Ty + ch + GAP if side == 'top' else Ty
        fcx, fcy = vx0 + VW / 2, fy0 + bh * z / 2
        capy = Ty if side == 'top' else fy0 + bh * z + GAP
        capx = fcx - cw / 2
    cam = (bx + bw / 2, by + bh / 2, z, fcx, fcy)
    if cap_y is not None and side in ('left', 'right'):
        capy = min(max((cap_y - cam[1]) * z + fcy - ch / 2, vy0 + 12), vy1 - ch - 12)
    if cap_x is not None and side in ('top', 'bottom'):
        capx = min(max((cap_x - cam[0]) * z + fcx - cw / 2, vx0 + 12), vx1 - cw - 12)
    return cam, (capx, capy, cw, ch)


def caption_prims(i, cap, side, rect):
    x, y, w, h = rect
    tl, sl, _, _ = cap_measure(cap, side)
    al = {'right': 'l', 'left': 'r', 'top': 'c', 'bottom': 'c'}[side]
    nm = 'cap%d' % i
    out = [T(nm + '/t', x - 4, y, w + 8, len(tl) * CAP_LH, [[(t, {'color': c}) for t, c in ln] for ln in tl], size=CAP_PT, color=INK,
             weight='b', align=al, lnspc=CAP_LH * 0.75, spc=-0.3)]
    if sl:
        out.append(T(nm + '/s', x - 4, y + len(tl) * CAP_LH + 8, w + 8, len(sl) * SUB_LH, sl, size=SUB_PT, color='5B5866', align=al,
                     lnspc=SUB_LH * 0.75))
    if cap.get('pill'):
        pw = tw(cap['pill'], 13, 'b') + 64
        px = {'l': x, 'r': x + w - pw, 'c': x + w / 2 - pw / 2}[al]
        py = y + len(tl) * CAP_LH + 14
        out += [R(nm + '/pill', px, py, pw, 34, prst='roundRect', fill=LAV, line=RING, line_w=1.2),
                R(nm + '/pill_d', px + 16, py + 12, 10, 10, prst='ellipse', fill=PURPLE, line=None),
                T(nm + '/pill_t', px + 32, py, pw - 40, 34, cap['pill'], size=13, color=PURPLE, weight='b', anchor='ctr')]
    return out


# ------------------------------------------------------------------ 장면
class Scene:
    def __init__(self, spec):
        self.spec = spec
        self.items = {}
        self.box = {}
        self.pos = {}
        self.steps = []
        self.owner = {}
        self.groups = {}

    def put(self, key, prims_or_fn, owner=None):
        fn = prims_or_fn if callable(prims_or_fn) else (lambda style=None, p=prims_or_fn: p)
        self.items[key] = fn
        self.box[key] = bbox(fn(None))
        if owner:
            self.owner[key] = owner

    def card(self, key, c):
        if c['kind'] == 'frag':
            c['w'] = S.frag_w(c['title'], c.get('meta', ''))

        def fn(style=None, c=c, key=key):
            return card_prims(key, c['kind'], c['x'], c['y'], c['w'], c['title'], c.get('meta', ''), c.get('lines', ()),
                              img=c.get('img'), icon=c.get('icon'), style=style or 'base', img_h=c.get('img_h'), link=c.get('link'))[0]
        _, h, pos = card_prims(key, c['kind'], c['x'], c['y'], c['w'], c['title'], c.get('meta', ''), c.get('lines', ()),
                               img=c.get('img'), icon=c.get('icon'), img_h=c.get('img_h'), link=c.get('link'))
        c['h'] = h
        self.pos[key] = pos
        self.put(key, fn)
        if c['kind'] == 'frag':
            return
        # 글이 카드 폭을 넘는지(대화 말풍선은 안쪽 여백 18 더)
        avail = c['w'] - (12 + 22 + 9) - 12 - (18 if c['kind'] in ('talk', 'link') else 0)
        for t in c.get('lines', ()):
            if tw(t, 9.5) > avail:
                print('   ! 카드 %s 글이 넘침: %s (%.0f > %.0f)' % (key, t, tw(t, 9.5), avail))
        if c.get('link'):
            lav = c['w'] - (12 + 22 + 9) - 12 - S.LINK_H - 6
            for t in c['link']['title']:
                if tw(t, 9.5, 'b') > lav:
                    print('   ! 카드 %s 링크 제목이 넘침: %s (%.0f > %.0f)' % (key, t, tw(t, 9.5, 'b'), lav))
        mw = tw(c.get('meta', ''), 8.5) + tw(c['title'], 10.5, 'b') + 43 + 24
        if mw > c['w']:
            print('   ! 카드 %s 제목과 날짜가 겹침 (%.0f > %.0f)' % (key, mw, c['w']))


# ------------------------------------------------------------------ 폰(왼쪽)
PX, PY, PW, PH = 60, 104, 300, 580


def bubble_prims(name, by, msg, tm, mine, pt=10.5):
    x, w = PX, PW
    ml = wrap(msg, pt, w - 120)
    bw = max(tw(t, pt) for t in ml) + 24
    lh = pt * 4 / 3 + 4
    bh = 14 + lh * len(ml)
    bx = x + w - 18 - bw if mine else x + 18
    out = [R(name, bx, by, bw, bh, prst='roundRect', radius=14, fill='EDE7FF' if mine else GRAY_FILL, line=None),
           T(name + '_t', bx + 12, by + 7, bw - 16, lh * len(ml), ml, size=pt, color=INK2, lnspc=lh * 0.75)]
    if tm:
        out.append(T(name + '_tm', (bx - 54) if mine else (bx + bw + 4), by + bh - 16, 50, 15, tm, size=7.5, color=MUTE,
                     anchor='ctr', align='r' if mine else 'l'))
    return out, bh


def phone_items(sc):
    sp = sc.spec
    ui = sp['ui']
    kind = sp['type']
    x, y, w, H = PX, PY, PW, PH
    ky = y + H - 236                     # 키보드 도구 막대(실타래 버튼). 그 아래는 자판
    sc.ui = dict(ky=ky)
    base = [R('ui/bg', x, y, w, H, prst='roundRect', radius=30, fill='FFFFFF', line=LINE, line_w=1.0, shadow=S.L.SHADOW_CARD),
            R('ui/cam', x + w / 2 - 26, y + 10, 52, 7, prst='roundRect', fill='E9E5F2', line=None)]
    msg_end = y + 90
    if kind == 'google':
        sc.put('ui', base)
        sc.put('ui.glogo', [P('ui.glogo/g', 'google.png', x + w / 2 - 60, y + 46, 120, 41)])

        def sbox(style=None):
            txt = ui['answer_q'] if style == 'done' else ui['query']
            tl = wrap(txt, 11, w - 92, 'r')[:2]
            hh = 46 if len(tl) == 1 else 62
            return [R('ui.sbox/bg', x + 18, y + 106, w - 36, hh, prst='roundRect', radius=23, fill='FFFFFF', line='DADCE0', line_w=1.2,
                      shadow=S.L.SHADOW_SOFT),
                    R('ui.sbox/lens', x + 34, y + 106 + hh / 2 - 8, 13, 13, prst='ellipse', fill=None, line='9AA0A6', line_w=1.8),
                    R('ui.sbox/lens2', x + 44, y + 106 + hh / 2 + 3, 6, 2, fill='9AA0A6', line=None),
                    T('ui.sbox/t', x + 58, y + 106, w - 92, hh, tl, size=11, color=INK, anchor='ctr', lnspc=12)]
        sc.put('ui.sbox', sbox)
        res = []
        ry = y + 196
        for i, (rt, rs) in enumerate(ui.get('results', [])):
            res += [T('ui.res/t%d' % i, x + 24, ry, w - 48, 22, rt, size=11, color='1A0DAB', weight='m', anchor='ctr'),
                    T('ui.res/s%d' % i, x + 24, ry + 22, w - 48, 18, rs, size=8.5, color=SUB, anchor='ctr')]
            ry += 58
        if res:
            sc.put('ui.res', res)
        sc.ui['top'] = ['ui.sbox']
    else:
        sc.put('ui', base)
        sc.put('ui.head', [R('ui.head/av', x + 18, y + 30, 34, 34, prst='ellipse', fill='C9B8FF', line=None),
                           T('ui.head/av_t', x + 18, y + 30, 34, 34, ui['name'][0], size=12, color='FFFFFF', weight='b', align='c',
                             anchor='ctr'),
                           T('ui.head/name', x + 60, y + 30, 200, 34, ui['name'], size=13, color=INK, weight='b', anchor='ctr'),
                           P('ui.head/app', S.ICON['talk'], x + w - 40, y + 36, 22, 22),
                           R('ui.head/div', x + 16, y + 76, w - 32, 1, fill='EEE9FA', line=None)])
        by = y + 90
        msgs = []
        for i, (msg, tm, mine) in enumerate(ui['msgs']):
            pr, bh = bubble_prims('ui.msg/m%d' % i, by, msg, tm, mine)
            msgs += pr
            by += bh + 10
        sc.put('ui.msg', msgs)
        msg_end = by
        sc.ui['top'] = ['ui.msg']
    sc.ui['msg_end'] = msg_end
    if kind == 'sheet':   # 키보드의 실타래 버튼으로 여는 기록 통합 검색: 처음엔 도구 막대 위에 작게, 답이 나오면 크게
        sy_s = msg_end + 6
        sy_b = y + 84

        def sheet(style=None):
            sy = sy_b if style == 'big' else sy_s
            bot = (y + H - 10) if style == 'big' else (ky - 8)
            return [R('ui.sheet/bg', x + 6, sy, w - 12, bot - sy, prst='roundRect', radius=22, fill='FFFFFF',
                      line=None if style == 'big' else LINE2, line_w=1.2, shadow=None if style == 'big' else S.L.SHADOW_LIFT),
                    R('ui.sheet/handle', x + w / 2 - 22, sy + 9, 44, 4, prst='roundRect', fill='D9D4E6', line=None),
                    P('ui.sheet/sp', S.ICON['spool'], x + 22, sy + 24, 20, 20),
                    T('ui.sheet/title', x + 48, sy + 19, 220, 30, '기록 통합 검색', size=12, color=PURPLE, weight='b', anchor='ctr'),
                    R('ui.sheet/sb', x + 18, sy + 58, w - 36, 42, prst='roundRect', fill='F7F5FC', line=LINE2, line_w=1.0),
                    T('ui.sheet/sb_t', x + 30, sy + 58, w - 60, 42, ui['query'], size=fit_pt(ui['query'], w - 64, 10.5, 'r', 8.5),
                      color=INK, anchor='ctr')]
        sc.put('ui.sheet', sheet)
        sc.ui['sheet_y'] = sy_b
        sc.box['ui.sheet.top'] = (x + 6, sy_s, w - 12, ky - 8 - sy_s)
        sc.box['ui.sheet.big'] = (x + 6, sy_b, w - 12, 112)
    if kind == 'gps':     # 지금 상황: 키보드 위 작은 판(위치·월렛)
        rows = [('map', '현재 위치', ui['loc'])] + list(ui.get('extra_rows', []))
        ch_ = 12 + 44 * len(rows)
        cy0 = ky - 12 - ch_
        out = [R('ui.loc/bg', x + 14, cy0, w - 28, ch_, prst='roundRect', radius=14, fill='FFFFFF', line=RING, line_w=1.4,
                 shadow=S.L.SHADOW_CARD, glow=(8, RING, 25))]
        for j, (ic, lab, val) in enumerate(rows):
            ry = cy0 + 6 + 44 * j
            out.append(P('ui.loc/ic%d' % j, S.ICON[ic], x + 28, ry + 11, 22, 22))
            out += [T('ui.loc/l%d' % j, x + 60, ry + 2, w - 90, 16, lab, size=8, color=MUTE, anchor='ctr'),
                    T('ui.loc/v%d' % j, x + 60, ry + 18, w - 90, 22, val, size=fit_pt(val, w - 94, 10.5, 'b', 8.5), color=PURPLE,
                      weight='b', anchor='ctr')]
        sc.put('ui.loc', out)
    # 키보드: 도구 막대(실타래 버튼 + 흐린 아이콘) + 자판(글자는 흐리게)
    tb = [R('ui.kbd/bar', x + 14, ky, w - 28, 44, prst='roundRect', radius=12, fill='F6F4FB', line=None),
          R('ui.kbd/sp_bg', x + 24, ky + 6, 32, 32, prst='roundRect', radius=9, fill='FFFFFF', line=LINE, line_w=0.8),
          P('ui.kbd/sp', S.ICON['spool'], x + 29, ky + 11, 22, 22)]
    for j in range(4):
        tb.append(R('ui.kbd/i%d' % j, x + 92 + j * 48, ky + 14, 16, 16, prst='roundRect', radius=4, fill=None, line='C9C3D6',
                    line_w=1.3))
    sc.put('ui.kbd', tb)
    keys = []
    rows_ = ['ㅂㅈㄷㄱㅅㅛㅕㅑㅐㅔ', 'ㅁㄴㅇㄹㅎㅗㅓㅏㅣ', 'ㅋㅌㅊㅍㅠㅜㅡ']
    kw_, kh_, gx_, gy_ = 23.2, 32, 4, 8
    yy = ky + 54
    for r_i, row in enumerate(rows_):
        n = len(row) + (2 if r_i == 2 else 0)
        rw = n * kw_ + (n - 1) * gx_
        xx = x + w / 2 - rw / 2
        cells = (['⇧'] if r_i == 2 else []) + list(row) + (['⌫'] if r_i == 2 else [])
        for c_i, ch in enumerate(cells):
            keys += [R('ui.keys/k%d_%d' % (r_i, c_i), xx, yy, kw_, kh_, prst='roundRect', radius=5, fill='F3F0F9', line=None),
                     T('ui.keys/t%d_%d' % (r_i, c_i), xx, yy, kw_, kh_, ch, size=8, color='B3ADC2', align='c', anchor='ctr')]
            xx += kw_ + gx_
        yy += kh_ + gy_
    keys += [R('ui.keys/sp', x + w / 2 - 70, yy, 140, kh_, prst='roundRect', radius=5, fill='F3F0F9', line=None),
             R('ui.keys/l', x + 22, yy, 52, kh_, prst='roundRect', radius=5, fill='ECE8F4', line=None),
             R('ui.keys/r', x + w - 74, yy, 52, kh_, prst='roundRect', radius=5, fill='ECE8F4', line=None)]
    sc.put('ui.keys', keys)

    def on(style=None):
        out = [R('ui.on/bg', x + 24, ky + 6, 32, 32, prst='roundRect', radius=9, fill=PURPLE, line=None, glow=(10, RING, 45)),
               P('ui.on/sp', S.ICON['spool_w'], x + 29, ky + 11, 22, 22)]
        if kind == 'gps' and style != 'nobadge':
            out += [R('ui.on/badge', x + 48, ky, 16, 16, prst='ellipse', fill='FF4D4F', line='FFFFFF', line_w=1.2),
                    T('ui.on/badge_t', x + 48, ky, 16, 16, '1', size=7, color='FFFFFF', weight='b', align='c', anchor='ctr')]
        return out
    sc.put('ui.on', on)
    sc.put('ui.tap', [P('ui.tap/h', 'touch-tap.png', x + 34, ky + 14, 28, 40)])
    # 건네기 카드
    a = sp['deliver']
    groups = []                       # [(아이콘, [줄])] — 이어지는 같은 앱 근거는 아이콘 하나 아래로 묶음
    for ic, txt in a.get('src_rows', []):
        lns = list(txt) if isinstance(txt, (list, tuple)) else [txt]
        if groups and groups[-1][0] == ic:
            groups[-1][1].extend(lns)
        else:
            groups.append((ic, lns))
    n_src = sum(len(g[1]) for g in groups)
    ml = wrap(a['main'], 13.5, w - 64, 'b') if '\n' not in a['main'] else a['main'].split('\n')
    for ln in ml:
        if tw(ln, 13.5, 'b') > w - 60:
            print('   ! 건네기 카드 글이 넘침: %s (%.0f > %.0f)' % (ln, tw(ln, 13.5, 'b'), w - 60))
    ch = 40 + 22 * len(ml) + 10 + 22 * n_src + 6 * max(0, len(groups) - 1) + 8 + 36 + 14 + (34 if a.get('attach') else 0)
    ay = (sc.ui['sheet_y'] + 112) if kind == 'sheet' else ky - ch - 12
    sc.ui['ans_overlaps_msg'] = kind != 'sheet' and ay < msg_end + 6
    card = [R('ans/bg', x + 14, ay, w - 28, ch, prst='roundRect', radius=16, fill='FFFFFF', line=RING, line_w=1.8,
              shadow=S.L.SHADOW_LIFT, glow=(9, RING, 24)),
            P('ans/ic', S.ICON['spool'], x + 28, ay + 13, 18, 18),
            T('ans/lab', x + 52, ay + 11, 220, 22, a.get('label', '찾은 답'), size=9.5, color=PURPLE2, weight='b', anchor='ctr'),
            T('ans/main', x + 28, ay + 40, w - 56, 22 * len(ml), ml, size=13.5, color=INK, weight='b', lnspc=17)]
    ry = ay + 40 + 22 * len(ml) + 10
    for gi, (ic, lns) in enumerate(groups):
        card.append(P('ans/si%d' % gi, S.ICON[ic], x + 28, ry + 3, 16, 16))
        for li, txt in enumerate(lns):
            card.append(T('ans/st%d_%d' % (gi, li), x + 50, ry, w - 80, 22, txt, size=fit_pt(txt, w - 82, 9, 'r', 7.5), color=SUB,
                          anchor='ctr'))
            ry += 22
        ry += 6
    ry -= 6 if groups else 0
    if a.get('attach'):
        card += [R('ans/att', x + 28, ry + 2, w - 56, 28, prst='roundRect', fill='F7F5FC', line=LINE2, line_w=1.0),
                 R('ans/att_d', x + 37, ry + 7, 13, 16, prst='snip1Rect', fill='FFFFFF', line=PURPLE2, line_w=1.2),
                 R('ans/att_l1', x + 40, ry + 13, 7, 1.4, fill=PURPLE2, line=None),
                 R('ans/att_l2', x + 40, ry + 17, 7, 1.4, fill=PURPLE2, line=None),
                 T('ans/att_t', x + 56, ry + 2, w - 92, 28, a['attach'], size=9.5, color=INK2, weight='sb', anchor='ctr')]
        ry += 34
    btn = a.get('button', '✓  입력하기')
    card += [R('ans/btn', x + 28, ry + 8, w - 56, 36, prst='roundRect', fill=PURPLE, line=None),
             T('ans/btn_t', x + 28, ry + 8, w - 56, 36, btn, size=10.5, color='FFFFFF', weight='b', align='c', anchor='ctr')]
    sc.put('ans', card)
    sc.put('ui.tap2', [P('ui.tap2/h', 'touch-tap.png', x + w - 78, ry + 26, 28, 40)])
    # 결과: 대화에 들어간 말 + 답장
    r = sp.get('result')
    if kind != 'google' and r:
        by = msg_end + 4
        pr, bh = bubble_prims('res/mine', by, r['mine'], r.get('mine_tm', ''), True)
        out = pr
        if r.get('file'):
            fy = by + bh + 8
            fw = tw(r['file'], 10, 'sb') + 54
            fx = x + w - 18 - fw
            out += [R('res/file', fx, fy, fw, 34, prst='roundRect', radius=12, fill='EDE7FF', line=None),
                    R('res/file_d', fx + 11, fy + 8, 13, 17, prst='snip1Rect', fill='FFFFFF', line=PURPLE2, line_w=1.2),
                    R('res/file_l1', fx + 14, fy + 14, 7, 1.4, fill=PURPLE2, line=None),
                    R('res/file_l2', fx + 14, fy + 18, 7, 1.4, fill=PURPLE2, line=None),
                    T('res/file_t', fx + 32, fy, fw - 36, 34, r['file'], size=10, color=INK2, weight='sb', anchor='ctr')]
            bh += 42
        if r.get('reply'):
            pr2, _ = bubble_prims('res/rep', by + bh + 10, r['reply'], r.get('reply_tm', ''), False)
            out += pr2
        sc.put('res', out)


# ------------------------------------------------------------------ 엔진(가운데): 검색창·일반 임베딩 / 질문 다시 쓰기·Reasoning Embedding
EX, EW = 470, 360
QY = 110                 # 질문 판 위
ROW_H = 54
BAR_W = 63


def bars_prims(name, x, y, color, seed):
    import hashlib
    hv = hashlib.md5(seed.encode('utf-8')).digest()
    out = []
    for i in range(9):
        hh = 22 * (0.3 + 0.68 * hv[i] / 255)
        out.append(R('%s%d' % (name, i), x + i * 7, y + 22 - hh, 4.5, hh, prst='roundRect', radius=1.5, fill=color, line=None))
    return out


def qchip_prims(name, x, y, w, token, rest, pt=10, border=LINE2, fill='FFFFFF', color=INK, chip_name=None):
    """질문 상자: [단서 칩] + 나머지 글(두 줄까지). 칩 뒤가 조사면 바짝, 낱말이면 한 칸. 돌려줌: (원시 목록, 칩 자리 또는 None, 높이)."""
    out, crect, lead = [], None, 0
    lh = 25
    if token:
        cw = chip_prims('x', 0, 0, token, pt=pt, padx=9)[1]
        lead = cw + (6 if rest.startswith(' ') else 2)
    words = rest.strip().split(' ')
    first, second = [], []
    for wd in words:
        cand = ' '.join(first + [wd])
        if not second and (tw(cand, pt, 'sb') <= w - 22 - lead or not first):
            first.append(wd)
        else:
            second.append(wd)
    t1, t2 = ' '.join(first), ' '.join(second)
    h = 20 + lh * (2 if t2 else 1)
    out.append(R(name + '/bg', x, y, w, h, prst='roundRect', radius=10, fill=fill, line=border, line_w=1.0))
    if token:
        out += chip_prims(chip_name or (name + '/chip'), x + 11, y + 11, token, style='fill', pt=pt, h=23, padx=9)[0]
        crect = (x + 11, y + 11, cw, 23)
    out.append(T(name + '/t1', x + 11 + lead, y + 11, w - 22 - lead + 8, 23, t1, size=pt, color=color, weight='sb', anchor='ctr'))
    if t2:
        out.append(T(name + '/t2', x + 11, y + 11 + lh, w - 14, 23, t2, size=pt, color=color, weight='sb', anchor='ctr'))
    return out, crect, h


def runs_of(t, base=INK):
    return [(t, base)] if isinstance(t, str) else list(t)


def plain(t):
    return t if isinstance(t, str) else ''.join(x for x, _ in t)


def engine_block(name, y, title, label, token, rest, cond, style, chip_name=None):
    """일반 임베딩(style='gen') / Reasoning Embedding(style='re') 판: 제목, 넣는 질문, (필터), 숫자 막대.
    돌려줌: (원시 목록, 막대 오른쪽 끝 점, 필터 칩 자리 또는 None, 높이)."""
    re_ = style == 're'
    col_t, col_l = (PURPLE, PURPLE) if re_ else (SUB, MUTE)
    inner = EW - 32
    qb, crect, qh = qchip_prims(name + '/q', EX + 16, y + 62, inner, token, rest, border=RING if re_ else GRAY_LINE,
                                fill='FFFFFF' if re_ else 'F6F5F8', color=INK if re_ else SUB, chip_name=chip_name)
    yy = y + 62 + qh + 12
    fc = None
    extra = []
    if cond:
        cpt = fit_pt(cond, inner - BAR_W - 70, 9.5)
        extra += [T(name + '/fl', EX + 16, yy, 40, 28, '필터', size=9, color=PURPLE2, weight='b', anchor='ctr')]
        pr, cw = chip_prims(name + '/fc', EX + 56, yy + 1, cond, style='dash', pt=cpt, h=26, padx=10)
        extra += pr
        fc = (EX + 56, yy + 1, cw, 26)
        if crect:   # 질문 속 조건(날짜 칩) → 필터 칸으로 내려가는 점선 갈래
            mx, my, mw, mh = crect
            sx, sy = mx + mw / 2, my + mh
            ex_, ey_ = EX + 56 + cw / 2, yy + 1
            extra.append(C(name + '/split', [(sx, sy + 1), (sx, sy + (ey_ - sy) * 0.6), (ex_, ey_ - (ey_ - sy) * 0.6), (ex_, ey_ - 1)],
                           w=1.4, color=PURPLE2, dash='sysDash', tail='triangle'))
    by_ = yy + (1 if cond else 0)
    bars_x = EX + EW - 16 - BAR_W
    h = (yy + 28 + 14 - y) if cond else (yy + 26 + 12 - y)
    out = [R(name + '/bg', EX, y, EW, h, prst='roundRect', radius=16, fill='FFFFFF', line=RING if re_ else GRAY_LINE,
             line_w=1.6 if re_ else 1.2, shadow=S.L.SHADOW_CARD if re_ else S.L.SHADOW_SOFT, glow=(8, RING, 22) if re_ else None),
           T(name + '/title', EX + 16, y + 12, 320, 22, title, size=11.5 if re_ else 13, color=col_t, weight='b', anchor='ctr'),
           T(name + '/lab', EX + 16, y + 36, 320, 18, label, size=8.5 if re_ else 10.5, color=col_l if re_ else SUB, weight='b',
             anchor='ctr')]
    out += qb + extra
    out += bars_prims(name + '/bar', bars_x, by_ + 2, PURPLE2 if re_ else 'B9B3C8', (token or '') + rest + '|' + (cond or ''))
    return out, (EX + EW - 14, by_ + 13), fc, h


def engine_items(sc):
    sp = sc.spec
    hops = sp['hops']
    nh = len(hops)
    # 질문 다시 쓰기 판
    ctx = sp.get('ctx', [])
    CTX_H = 30 if ctx else 0
    PHH = 112 + CTX_H + nh * ROW_H + 44
    acw = chip_prims('x', 0, 0, sp['answer'], pt=10, padx=9)[1]
    sc.ok_below = EX + 46 + acw + 6 + 46 > EX + EW - 12
    if sc.ok_below:
        PHH += 30
    sc.QPH = PHH
    sc.RE_Y = QY + PHH + 22
    sc.put('qp', [R('qp/bg', EX, QY, EW, PHH, prst='roundRect', radius=16, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=S.L.SHADOW_CARD)])
    hx = EX + 42 + tw('Query Rewriting', 12.5, 'b') + 8
    sc.put('qp.head', [P('qp.head/ic', S.ICON['spool'], EX + 16, QY + 14, 20, 20),
                       T('qp.head/title', EX + 42, QY + 12, 220, 24, 'Query Rewriting', size=12.5, color=PURPLE, weight='b', anchor='ctr'),
                       T('qp.head/ko', hx, QY + 12, 120, 24, '질문 다시 쓰기', size=9, color=MUTE, weight='sb', anchor='ctr')])
    ol = wrap('“%s”' % sp['ask'], 10.5, EW - 34, 'm')[:2]
    qo = [T('qorig/l', EX + 16, QY + 46, 220, 16, sp.get('ask_label', '처음 질문'), size=8.5, color=MUTE, weight='b', anchor='ctr'),
          T('qorig/t', EX + 16, QY + 64, EW - 30, 19 * len(ol), ol, size=10.5, color=INK, weight='m', lnspc=14)]
    cx_, cy0 = EX + 16, QY + 64 + 19 * len(ol) + 6
    for j, (ic, lab) in enumerate(ctx):
        cw = tw(lab, 8.5, 'sb') + 34
        qo += [R('qorig/c%d' % j, cx_, cy0, cw, 22, prst='roundRect', fill='F4F1FB', line=LINE2, line_w=0.9),
               P('qorig/ci%d' % j, S.ICON[ic], cx_ + 7, cy0 + 4, 14, 14),
               T('qorig/ct%d' % j, cx_ + 25, cy0, cw - 27, 22, lab, size=8.5, color=SUB, weight='sb', anchor='ctr')]
        cx_ += cw + 6
    sc.put('qorig', qo)
    X0 = EX + 46
    QW = EW - 46 - 16
    sc.X0 = X0

    def row_y(i):
        return QY + 112 + CTX_H + (i - 1) * ROW_H

    sc.row_y = row_y

    def q_parts(i, rw):
        hop = hops[i - 1]
        if i == 1:
            return None, hop['q']
        text = hop['q'][2] if (rw and len(hop['q']) > 2) else hop['q'][1]
        return hop['q'][0], text

    def lines_after(text, lead, pt=10.5):
        words = text.split(' ')
        first, rest = [], []
        for wd in words:
            cand = ' '.join(first + [wd])
            if not rest and (tw(cand, pt, 'm') <= QW - lead or not first):
                first.append(wd)
            else:
                rest.append(wd)
        return ' '.join(first), ' '.join(rest)

    def gap_after(text):
        return 6 if text.startswith(' ') else 2

    def q_row(i):
        def fn(style=None, i=i):
            st = style or 'plan'
            rw = st.endswith('_rw')
            base = st.replace('_rw', '')
            cur, done = base == 'cur', base == 'done'
            col = INK if cur else (SUB if done else '9C97AB')
            y = row_y(i)
            ph, text = q_parts(i, rw)
            lead = 0
            out = []
            if ph is not None:
                if rw:
                    lead = chip_prims('x', 0, 0, hops[i - 2]['token'], pt=10, padx=9)[1] + gap_after(text)
                else:
                    lead = chip_prims('x', 0, 0, ph, pt=10, padx=8)[1] + gap_after(text)
            t1, t2 = lines_after(text.strip(), lead)
            if cur:
                hh = 42 if not t2 else 62
                out.append(R('q%d/hl' % i, EX + 8, y - 11, EW - 16, hh, prst='roundRect', radius=10, fill=LAV, line=None))
            out += [R('q%d/b' % i, EX + 16, y, 21, 21, prst='ellipse', fill=('DCD3FF' if (cur or done) else 'ECE8F4'),
                      line=RING if cur else None, line_w=1.2),
                    T('q%d/bt' % i, EX + 16, y, 21, 21, '✓' if done else str(i), size=8.5, color=PURPLE if (cur or done) else MUTE,
                      weight='b', align='c', anchor='ctr')]
            if ph is not None and not rw:
                out += chip_prims('q%d/ph' % i, X0, y - 1, ph, style='dash', pt=10, h=23, padx=8)[0]
            out.append(T('q%d/t1' % i, X0 + lead, y, QW - lead + 12, 21, t1, size=10.5, color=col, weight='m', anchor='ctr'))
            if t2:
                out.append(T('q%d/t2' % i, X0, y + 21, QW + 12, 21, t2, size=10.5, color=col, weight='m', anchor='ctr'))
            return out
        return fn

    for i in range(1, nh + 1):
        sc.put('q%d' % i, q_row(i))
        ph, text = q_parts(i, False)
        lead = (chip_prims('x', 0, 0, ph, pt=10, padx=8)[1] + gap_after(text)) if ph else 0
        t1, t2 = lines_after(text.strip(), lead)
        tail = max(tw(t1, 10.5, 'm') + lead, tw(t2, 10.5, 'm') if t2 else 0)
        sc.box['q%d.tight' % i] = (EX + 10, row_y(i) - 8, X0 - EX - 10 + tail + 8, 42 if not t2 else 62)
    ay = row_y(nh + 1) - 2
    sc.ans_y = ay
    sc.put('qans', [T('qans/l', EX + 16, ay, 30, 23, '답', size=10.5, color=PURPLE, weight='b', anchor='ctr')])
    sc.put('qans.slot', chip_prims('qans/slot', X0, ay, ' ' * 24, style='dash', pt=10, h=23)[0])
    sc.groups['qp'] = ['qp.head', 'qorig', 'qans', 'qans.slot', 'qans.ok'] + ['q%d' % i for i in range(1, nh + 1)] + \
        ['tok%d@q' % i for i in range(1, nh + 1)]


def hop_runs(sp, n):
    """n번째 홉에 넣는 질문(다시 쓴 질문이면 단서 칩 글자가 앞에)."""
    hops = sp['hops']
    hop = hops[n - 1]
    if n == 1:
        return [(hop['q'], INK)]
    return [(hops[n - 2]['token'], PURPLE), (hop['q'][2] if len(hop['q']) > 2 else hop['q'][1], INK)]


# ------------------------------------------------------------------ 실 경로
def route(p0, dst, obstacles, top=None):
    """엔진 오른쪽의 점 p0 → 기록 dst. 같은 줄 사이에 다른 카드가 있으면, 시작점이 아래면 그 줄 아래로, 위면 위로 돌아 들어감."""
    sx = p0[0]
    between = [b for b in obstacles if b[0] > sx and b[0] + b[2] < dst[0] + 4 and b[1] < dst[1] + dst[3] and b[1] + b[3] > dst[1]]
    if between:
        gx, tcx = sx + 30, dst[0] + dst[2] / 2
        x_lo, x_hi = sx, dst[0] + dst[2]
        if p0[1] > dst[1] + dst[3] / 2 and top is None:
            rb = max([dst[1] + dst[3]] + [b[1] + b[3] for b in between])
            below = [b[1] for b in obstacles if b[1] >= rb - 2 and b[0] < x_hi and b[0] + b[2] > x_lo]
            cy_ = (rb + min(below)) / 2 if below else rb + 24
            b0, c0 = (gx + 30, cy_), (tcx - 44, cy_)
            return [p0, (gx, p0[1]), (gx, cy_), b0, (b0[0] + (c0[0] - b0[0]) / 3, cy_), (b0[0] + (c0[0] - b0[0]) * 2 / 3, cy_), c0,
                    (tcx - 10, cy_), (tcx, cy_ - 10), (tcx, dst[1] + dst[3] + 2)]
        rt = min([dst[1]] + [b[1] for b in between])
        above = [b[1] + b[3] for b in obstacles if b[1] + b[3] <= rt + 2 and b[0] < x_hi and b[0] + b[2] > x_lo]
        cy_ = (rt + max(above)) / 2 if above else rt - 26
        if top is not None:
            cy_ = min(cy_, top - 22)
        b0, c0 = (gx + 30, cy_), (tcx - 44, cy_)
        return [p0, (gx, p0[1]), (gx, cy_), b0, (b0[0] + (c0[0] - b0[0]) / 3, cy_), (b0[0] + (c0[0] - b0[0]) * 2 / 3, cy_), c0,
                (tcx - 10, cy_), (tcx, cy_ + 10), (tcx, dst[1] - 2)]
    return scurve(p0, (dst[0] - 2, dst[1] + min(dst[3] / 2, 40)), 0.5)


def route_below(p0, box, obstacles):
    sx = p0[0]
    between = [b for b in obstacles if b[0] > sx and b[0] + b[2] < box[0] + 4 and b[1] < box[1] + box[3] and b[1] + b[3] > box[1]]
    if not between:
        return scurve(p0, (box[0] - 2, box[1] + min(box[3] / 2, 40)), 0.5)
    low = max([box[1] + box[3]] + [b[1] + b[3] for b in between]) + 16
    gx, ex = sx + 30, box[0] + 36
    return [p0, (gx, p0[1]), (gx, low), (gx + 30, low), (gx + 30 + (ex - 24 - gx - 30) / 3, low), (ex - 24 - (ex - 24 - gx - 30) / 3, low),
            (ex - 24, low), (ex - 6, low), (ex, low - 6), (ex, box[1] + box[3] + 1)]


# ------------------------------------------------------------------ 실 경로(세로 골을 타고 내려가 기록 높이에서 꺾어 들어감)
GX = 853          # 엔진 판(오른쪽 끝 830)과 기록 더미(876~) 사이의 세로 골


def route_elbow(p0, box, gx=GX, r=22):
    x0, y0 = p0
    tx, ty = box[0] - 2, box[1] + min(box[3] / 2, 34)
    if abs(ty - y0) < 2 * r + 4 or tx - gx < r + 6:
        return scurve(p0, (tx, ty), 0.5)
    s_ = 1 if ty > y0 else -1
    k = 0.552 * r

    def line(a, b):
        return [(a[0] + (b[0] - a[0]) / 3, a[1] + (b[1] - a[1]) / 3), (a[0] + 2 * (b[0] - a[0]) / 3, a[1] + 2 * (b[1] - a[1]) / 3), b]
    a = (gx - r, y0)
    b = (gx, y0 + s_ * r)
    c = (gx, ty - s_ * r)
    d = (gx + r, ty)
    return ([p0] + line(p0, a) + [(a[0] + k, y0), (gx, b[1] - s_ * k), b] + line(b, c) + [(gx, c[1] + s_ * k), (d[0] - k, ty), d] +
            line(d, (tx, ty)))


# ------------------------------------------------------------------ 흩어진 기록 더미(인트로 첫 부분처럼: 작은 조각 30개 남짓, 옅게, 몇 개만 켜짐)
EXTRA = [('note', '아이디어', '앱 이름 후보'), ('cal', '헬스', '화, 목 오전 7:00'), ('gallery', 'IMG_2210.jpg', '주말 산책'),
         ('mail', '뉴스레터', '이번 주 소식'), ('talk', '회사 동기', '점심 뭐 먹지?'), ('phone', '통화 기록', '2분 14초'),
         ('map', '최근 경로', '회사에서 집'), ('wallet', '멤버십', '적립 1,200P'), ('note', '책 메모', '다 읽은 책 3권'),
         ('gallery', '스크린샷', '영수증 캡처'), ('talk', '반상회 단톡방', '주차 안내'), ('mail', '앱 알림', '비밀번호 변경')]
KIND_ICON = {'talk': 'talk', 'note': 'note', 'mail': 'mail', 'cal': 'cal', 'photo': 'gallery', 'shot': 'gallery', 'pass': 'wallet',
             'sms': 'talk', 'link': 'talk', 'pay': 'talk', 'wpay': 'wallet', 'call': 'phone'}
CLOUD_BOX = (370, 214, 1640, 590)     # 더미 장 카메라가 담는 세계(설명은 그 위)
LIT_ALPHA, CLOUD_ALPHA = 100, 32


def _overlap(a, b, mx=0, my=0):
    return a[0] < b[0] + b[2] + mx and b[0] < a[0] + a[2] + mx and a[1] < b[1] + b[3] + my and b[1] < a[1] + a[3] + my


def _gap(a, b):
    dx = max(0, max(a[0], b[0]) - min(a[0] + a[2], b[0] + b[2]))
    dy = max(0, max(a[1], b[1]) - min(a[1] + a[3], b[1] + b[3]))
    return (dx * dx + (dy * 1.8) ** 2) ** 0.5


def chip_text(c):
    """더미 속 조각에 쓰는 한 줄(답이 미리 읽히지 않게 짧게)."""
    if c.get('chip'):
        return c['chip']
    t = c['lines'][0] if c.get('lines') else c.get('meta', '')
    if not c.get('lines'):           # 사진처럼 날짜뿐이면 '2026. 3. 15 (일) 20:14' → '3월 15일 20:14'(괄호가 잘리지 않게)
        import re
        m = re.match(r'\d{4}\. (\d{1,2})\. (\d{1,2})(?: \((.)\))?(?: (\d{1,2}:\d{2}))?', t)
        if m:
            t = '%s월 %s일' % (m.group(1), m.group(2)) + (' ' + m.group(4) if m.group(4) else (' (%s)' % m.group(3) if m.group(3) else ''))
    return t if len(t) <= 15 else t[:14].rstrip(' ,') + '…'


def scatter(items, rect, avoid, seed):
    """items = [(키, 폭, 높이)] → {키: (x, y)}. 후보 여럿 중 가장 비어 있는 자리(씨앗 고정) → 줄 맞지 않게 고르게 흩어짐."""
    import random
    rnd = random.Random(seed)
    x0, y0, x1, y1 = rect
    taken = list(avoid)
    out = {}
    for key, w, h in items:
        best, best_d = None, -1
        for _ in range(160):
            b = (rnd.uniform(x0, x1 - w), rnd.uniform(y0, y1 - h), w, h)
            if any(_overlap(b, t, 24, 18) for t in taken):
                continue
            d = min(_gap(b, t) for t in taken) if taken else 1e9
            if d > best_d:
                best, best_d = b, d
        if best is None:
            print('   ! 조각 %s 자리 없음' % key)
            continue
        out[key] = (round(best[0]), round(best[1]))
        taken.append(best)
    return out


# ------------------------------------------------------------------ 일반 검색 판(실패): 키워드 검색 / 임베딩 검색 / 둘을 합친 일반 검색
def search_panel(name, y, title, pill, query, words, bars, label=None, under=False, x=None, w=None):
    """제목 + 회색 알약 + 검색어(같은 단어엔 형광펜, 임베딩이면 점선 밑줄) + 숫자 막대. 돌려줌: (원시 목록, 실이 나가는 점, 높이).
    x, w를 주면 그 자리·폭으로(키워드·임베딩을 나란히 놓는 실패 장)."""
    EX, EW = (globals()['EX'] if x is None else x), (globals()['EW'] if w is None else w)
    inner = EW - 32
    ql = wrap(query, 10.5, inner - 24, 'm')[:2]
    qh = 14 + 20 * len(ql)
    h = 50 + qh + (44 if bars else 16)
    out = [R(name + '/bg', EX, y, EW, h, prst='roundRect', radius=16, fill='FFFFFF', line=GRAY_LINE, line_w=1.2, shadow=S.L.SHADOW_SOFT),
           T(name + '/title', EX + 16, y + 12, 220, 24, title, size=13, color=INK2, weight='b', anchor='ctr')]
    if pill:
        px = EX + 16 + tw(title, 13, 'b') + 10
        pw = tw(pill, 9, 'b') + 18
        out += [R(name + '/pill', px, y + 14, pw, 21, prst='roundRect', fill='EFECF4', line=None),
                T(name + '/pill_t', px, y + 14, pw, 21, pill, size=9, color=SUB, weight='b', align='c', anchor='ctr')]
    qx, qy = EX + 16, y + 46
    out.append(R(name + '/qb', qx, qy, inner, qh, prst='roundRect', radius=10, fill='F6F5F8', line=GRAY_LINE, line_w=1.0))
    n = 0
    for i, ln in enumerate(ql):
        ty = qy + 7 + 20 * i
        for wd in words:
            st = 0
            while wd in ln[st:]:
                r_ = band((qx + 12, ty, ln, 10.5, 'm'), wd, kind='full', start=st)
                out.append(R(name + '/hl%d' % n, *r_, prst='roundRect', radius=2.5, fill=HL, alpha=34, line=None))
                n += 1
                st = ln.index(wd, st) + len(wd)
        if under:
            lw_ = tw(ln, 10.5, 'm')
            yl = ty + 10.5 * 4 / 3 + 3
            out.append(C(name + '/ul%d' % i, [(qx + 12, yl), (qx + 12 + lw_ / 3, yl), (qx + 12 + 2 * lw_ / 3, yl), (qx + 12 + lw_, yl)],
                         w=1.8, color=PURPLE2, dash='sysDash'))
    for i, ln in enumerate(ql):
        out.append(T(name + '/q%d' % i, qx + 12, qy + 7 + 20 * i, inner - 20, 20, ln, size=10.5, color=INK, weight='m'))
    if bars:
        by_ = qy + qh + 10
        out += bars_prims(name + '/bar', EX + EW - 16 - BAR_W, by_, 'B9B3C8', query)
        out.append(T(name + '/bar_l', EX + 16, by_, 220, 24, label or '뜻을 숫자로 바꿔 비교', size=9, color=MUTE, weight='sb', anchor='ctr'))
        port = (EX + EW - 14, by_ + 13)
    else:
        port = (EX + EW - 2, qy + qh / 2)
    return out, port, h


def rank_prims(name, x, y, n, fill='8E88A0'):
    return [R(name + '/c', x, y, 26, 26, prst='ellipse', fill=fill, line='FFFFFF', line_w=1.6),
            T(name + '/t', x, y, 26, 26, str(n), size=10, color='FFFFFF', weight='b', align='c', anchor='ctr')]


VEC_COLS = ['F1ECFF', 'DCD3FF', 'B9A6FF', '8B6BFF', '5A3FE0']       # 벡터 칸 색(옅은 → 진한 보라, 노랑 없음)


def vec_prims(name, x, y, n, cw, ch, seed, gap=2):
    """벡터를 색 칸 줄로(Jay Alammar의 단어 임베딩 그림처럼). 칸 색은 글자에서 나온 값(같은 기록이면 늘 같음)."""
    import hashlib
    hv = hashlib.md5(seed.encode('utf-8')).digest()
    return [R('%s/c%d' % (name, i), x + i * (cw + gap), y, cw, ch, prst='roundRect', radius=2.5,
              fill=VEC_COLS[hv[i % len(hv)] % len(VEC_COLS)], line=None) for i in range(n)]


def short_date(meta):
    """'2026. 3. 15 (일) 20:14' → '3/15 (일) 20:14', '2026. 3. 14' → '3/14'."""
    import re
    m = re.match(r'\d{4}\. (\d{1,2})\. (\d{1,2})(?: \((.)\))?(?: (\d{1,2}:\d{2}))?', meta or '')
    if not m:
        return meta
    return '%s/%s' % (m.group(1), m.group(2)) + (' (%s)' % m.group(3) if m.group(3) else '') + (' ' + m.group(4) if m.group(4) else '')


def underline_prims(name, rect, color=PURPLE2):
    x, y, w, h = rect
    yl = y + h + 1.5
    return [C(name, [(x, yl), (x + w / 3, yl), (x + 2 * w / 3, yl), (x + w, yl)], w=2.0, color=color, dash='sysDash')]


# ------------------------------------------------------------------ 시나리오 → 장면
def build(spec):
    sc = Scene(spec)
    REC = spec['records']
    for k, c in REC.items():
        sc.card(k, c)
    keys = list(REC)
    hops = spec['hops']
    nh = len(hops)
    phone_items(sc)
    engine_items(sc)
    CP, NT = spec['cap'], spec['notes']
    kind = spec['type']
    owner = sc.owner

    def card_at(k, x, y, style='base', img_h=None):
        c = REC[k]
        return card_prims(k, c['kind'], x, y, c['w'], c['title'], c.get('meta', ''), c.get('lines', ()), img=c.get('img'),
                          icon=c.get('icon'), style=style, img_h=img_h or c.get('img_h'), link=c.get('link'))

    LIST_IMG_H = 84      # 결과 목록에서는 사진을 낮게(세 장이 한 화면에 들어오게)

    def frag_at(name, k, x, y, style='base'):
        c = REC[k]
        return card_prims(name, 'frag', x, y, None, c['title'], chip_text(c), icon=c.get('icon') or KIND_ICON.get(c['kind'], 'talk'),
                          style=style)[0]

    def tag_box(box, label, style='gray', where='tr', pt=10.5, name=None):
        """상자 위쪽 모서리에 붙는 태그(제목·날짜와 겹치지 않게 위로 비켜 둠)."""
        bx, by, bw, bh = box
        w = tw(label, pt, 'sb') + (22 if pt <= 10 else 26)
        x = bx + bw - w - 8 if where in ('tr', 'br') else bx + 10
        hh = 24 if pt <= 10 else 28
        y = (by - hh + 4) if where in ('tr', 'tl') else by + bh - 4
        return chip_prims(name, x, y, label, style=style, pt=pt, h=hh, padx=11 if pt <= 10 else 13, weight='sb')[0]

    def marks_at(pos, marks, name, owner_=None, fill=HL, alpha=34):
        rects = [band(pos[where], sub, kind='full') for where, sub in marks]
        sc.put(name, [R('%s/%d' % (name, i), *r, prst='roundRect', radius=2.5, fill=fill, alpha=alpha, line=None)
                      for i, r in enumerate(rects)], owner=owner_)
        return rects

    def thread_to(p0, box):
        return route_elbow(p0, box)

    def pair_items():
        """키워드 검색(왼쪽)과 임베딩 검색(오른쪽)을 한 장에 나란히. 왼쪽은 같은 단어에 형광펜,
        오른쪽은 임베딩 공간에서 질문 점 둘레(점선 원)의 가장 가까운 기록. 답에 필요한 기록은 원 밖 먼 곳."""
        PR = dict(F.get('pair', {}))
        HW, GX_ = PR.get('hw', 480), PR.get('gap', 84)
        LX0 = PR.get('x', 640)
        RX0 = LX0 + HW + GX_
        TOP = PR.get('top', 150)
        kwp, _, kwh = search_panel('kw', TOP, '키워드 검색', 'BM25', F['query'], F['words'], False, x=LX0, w=HW)
        ebp, _, ebh = search_panel('emb', TOP, '임베딩 검색', PR.get('emb_pill', '가장 가까운 뜻'), F['query'], [], False, under=True,
                                   x=RX0, w=HW)
        sc.put('kw', kwp)
        sc.put('emb', ebp)
        under, over, al = [], ['kw', 'emb'], {}
        anim = {'kw': dict(kind='rise', delay=0, dur=420), 'emb': dict(kind='rise', delay=150, dur=420)}
        # 왼쪽: 같은 단어가 든 기록(형광펜). 판 아래 나란히, 순위 동그라미, 이유 태그는 카드 아래
        K = F['kw']
        ws = [REC[k]['w'] for k in K['ranks']]
        n = len(ws)
        gapc = PR.get('kw_gap', 34)
        x = LX0 + (HW - sum(ws) - gapc * (n - 1)) / 2
        ry = TOP + kwh + PR.get('kw_dy', 64)
        kbot = ry
        for i, k in enumerate(K['ranks']):
            pr, h, pos = card_at(k, x, ry, style='gray')
            w_ = REC[k]['w']
            sc.put('kw.res.' + k, pr)
            sx_ = LX0 + HW / 2 + (i - (n - 1) / 2) * 96
            th = 'kw.th%d' % (i + 1)
            sc.put(th, [C(th + '/l', vcurve((sx_, TOP + kwh + 1), (x + w_ / 2, ry - 2)), w=1.8, color='B9B3C8')])
            rk = 'kw.rank%d' % (i + 1)
            sc.put(rk, rank_prims('krank%d' % (i + 1), x - 13, ry - 12, i + 1))
            over += ['kw.res.' + k, rk]
            under.append(th)
            anim[th] = dict(kind='wipe_in', dir='down', delay=380 + 140 * i, dur=380)
            box = (x, ry, w_, h)
            if K.get('marks', {}).get(k):
                marks_at(pos, K['marks'][k], 'kw.mk.' + k, alpha=30)
                over.append('kw.mk.' + k)
                anim['kw.mk.' + k] = dict(kind='wipe_in', dir='left', delay=700 + 120 * i, dur=360)
            if K.get('tags', {}).get(k):
                sc.put('kw.tag.' + k, tag_box(box, K['tags'][k], where='br', name='ktag.' + k, pt=11))
                over.append('kw.tag.' + k)
                anim['kw.tag.' + k] = dict(kind='zoom_in', delay=1050 + 150 * i, dur=280)
            kbot = max(kbot, ry + h)
            x += w_ + gapc
        if PR.get('kw_note'):
            sc.put('kw.note', [T('kw.note/t', LX0, kbot + 52, HW, 24, PR['kw_note'], size=11, color=SUB, weight='sb', align='c',
                                 anchor='ctr')])
            over.append('kw.note')
            anim['kw.note'] = dict(kind='fade_in', delay=1400, dur=400)
        # 오른쪽: 임베딩 공간. 질문도 점 하나로 바뀌고, 그 둘레(점선 원)에 가장 가까운 기록이 결과
        E_ = F['emb']
        my0 = TOP + ebh + PR.get('map_dy', 28)
        mh = PR.get('map_h', 246)
        sx, sy = RX0 + PR.get('star_x', 150), my0 + PR.get('star_y', 128)
        rr = PR.get('ring_r', 100)
        sc.put('emap', [R('emap/bg', RX0, my0, HW, mh, prst='roundRect', radius=18, fill='FFFFFF', alpha=72, line=LINE, line_w=1.0)])
        sc.put('emap.ring', [R('emap/ring', sx - rr, sy - rr, 2 * rr, 2 * rr, prst='ellipse', fill=LAV, alpha=60, line=PURPLE2,
                                line_w=1.5, dash='dash')])
        qx0 = RX0 + 44
        sc.put('emap.link', [C('emap/link', [(qx0, TOP + ebh + 1), (qx0, sy - 8), (sx - 70, sy), (sx - 18, sy)], w=1.6, color=PURPLE2,
                               dash='sysDash', tail='triangle')])
        sc.put('emap.q', [R('emap/q', sx - 14, sy - 14, 28, 28, prst='star5', fill=PURPLE, line='FFFFFF', line_w=1.2, glow=(8, RING, 40)),
                          T('emap/q_t', sx - 70, sy + 8, 48, 18, '질문', size=9.5, color=PURPLE, weight='b', align='r', anchor='ctr')])
        under += ['emap', 'emap.ring', 'emap.link']
        over.append('emap.q')
        anim.update({'emap': dict(kind='fade_in', delay=300, dur=400), 'emap.link': dict(kind='wipe_in', dir='down', delay=560, dur=420),
                     'emap.q': dict(kind='zoom_in', delay=900, dur=300), 'emap.ring': dict(kind='zoom_in', delay=1150, dur=420)})
        offs = PR.get('near', [(42, -48), (64, 42)])
        TW_, TH_ = PR.get('thumb', (70, 52))
        taken = []
        for i, k in enumerate(E_['ranks']):
            dx, dy = offs[i]
            cx_, cy_ = sx + dx, sy + dy
            x0, y0 = cx_ - TW_ / 2, cy_ - TH_ / 2
            img = REC[k]['img']
            sc.put('emb.res.' + k, [R(k + '/bg', x0 - 4, y0 - 4, TW_ + 8, TH_ + 8, prst='roundRect', radius=10, fill='FFFFFF',
                                      line=GRAY_LINE, line_w=1.4, shadow=S.L.SHADOW_SOFT),
                                    P(k + '/img', img, x0, y0, TW_, TH_, radius=7, crop=S._fit_crop(img, TW_, TH_))])
            ln_ = (dx * dx + dy * dy) ** 0.5
            ux, uy = dx / ln_, dy / ln_
            ta = (sx + ux * 15, sy + uy * 15)
            tb = (cx_ - ux * min(TW_ / 2 / max(abs(ux), 1e-3), TH_ / 2 / max(abs(uy), 1e-3)) - ux * 5,
                  cy_ - uy * min(TW_ / 2 / max(abs(ux), 1e-3), TH_ / 2 / max(abs(uy), 1e-3)) - uy * 5)
            ln = 'emb.ln%d' % (i + 1)
            sc.put(ln, [C(ln + '/l', [ta, (ta[0] + (tb[0] - ta[0]) / 3, ta[1] + (tb[1] - ta[1]) / 3),
                                      (ta[0] + 2 * (tb[0] - ta[0]) / 3, ta[1] + 2 * (tb[1] - ta[1]) / 3), tb], w=2.0, color=PURPLE2)])
            rk = 'emb.rank%d' % (i + 1)
            sc.put(rk, rank_prims('erank%d' % (i + 1), x0 - 4 - 34, cy_ - 13, i + 1))
            lab = E_['tags'][k]
            tgw = tw(lab, 10.5, 'sb') + 22
            ty_ = (y0 - 4 - 8 - 26) if dy < 0 else (y0 + TH_ + 4 + 8)
            tg = 'emb.tag.' + k
            sc.put(tg, chip_prims('etag.' + k, cx_ - tgw / 2, ty_, lab, style='grayfill', pt=10.5, h=26, padx=11, weight='sb')[0])
            under.append(ln)
            over += ['emb.res.' + k, rk, tg]
            anim[ln] = dict(kind='wipe_in', dir='right' if dx > 0 else 'left', delay=1350 + 150 * i, dur=300)
            anim[rk] = dict(kind='zoom_in', delay=1500 + 150 * i, dur=260)
            anim[tg] = dict(kind='zoom_in', delay=1700 + 150 * i, dur=280)
            taken += [(x0 - 40, y0 - 8, TW_ + 48, TH_ + 16), (cx_ - tgw / 2 - 6, ty_ - 4, tgw + 12, 34)]
        # 결과 밖의 답: 질문 점에서 먼 곳(점선 테두리 + 먼저 알아야 할 단서 태그)
        M = F['miss']
        mk_ = M['key']
        fw = S.frag_w(REC[mk_]['title'], chip_text(REC[mk_]))
        fx = RX0 + HW - fw - PR.get('miss_dx', 18)
        fy = sy - S.FRAG_H / 2 + PR.get('miss_dy', 0)
        sc.put('missf.' + mk_, frag_at(mk_, mk_, fx, fy))
        al['missf.' + mk_] = 60
        mt = M['tag']
        mtw = tw(mt, 10, 'sb') + 24
        sc.put('emap.far', [C('emap/far', [(sx + 16, sy), (sx + 70, sy), (fx - 50, fy + S.FRAG_H / 2), (fx - 12, fy + S.FRAG_H / 2)],
                              w=1.5, color=GRAY_LINE, dash='sysDash')])
        sc.put('miss', [R('miss/r', fx - 8, fy - 8, fw + 16, S.FRAG_H + 16, prst='roundRect', radius=18, fill=None, line=GRAY_LINE,
                          line_w=1.6, dash='dash'),
                        R('miss/tag', fx + fw / 2 - mtw / 2, fy + S.FRAG_H + 16, mtw, 28, prst='roundRect', fill='EFECF4', line=None),
                        T('miss/tag_t', fx + fw / 2 - mtw / 2, fy + S.FRAG_H + 16, mtw, 28, mt, size=10, color=SUB, weight='sb',
                          align='c', anchor='ctr')])
        mlab = PR.get('map_label', '가까울수록 비슷한 뜻')
        lw_ = tw(mlab, 9, 'sb') + 4
        sc.put('emap.lab', [T('emap/lab', RX0 + HW - 16 - lw_, my0 + mh - 28, lw_, 18, mlab, size=9, color=MUTE, weight='sb', align='r',
                              anchor='ctr')])
        under.append('emap.far')
        over += ['missf.' + mk_, 'miss', 'emap.lab']
        anim.update({'emap.far': dict(kind='wipe_in', dir='right', delay=2050, dur=450), 'miss': dict(kind='fade_in', delay=2250, dur=450),
                     'emap.lab': dict(kind='fade_in', delay=1250, dur=400)})
        taken += [(fx - 12, fy - 12, fw + 24, S.FRAG_H + 60), (RX0 + HW - 20 - lw_, my0 + mh - 32, lw_ + 8, 26), (sx - 74, sy - 18, 92, 50)]
        # 흐린 점(다른 기록들): 원 밖에만, 다른 것과 겹치지 않게(씨앗 고정)
        import random
        rnd = random.Random(spec.get('seed', 11) + 7)
        dots = []
        for _ in range(600):
            if len(dots) >= PR.get('n_dots', 16):
                break
            px_, py_ = rnd.uniform(RX0 + 18, RX0 + HW - 18), rnd.uniform(my0 + 16, my0 + mh - 16)
            if ((px_ - sx) ** 2 + (py_ - sy) ** 2) ** 0.5 < rr + 14:
                continue
            if px_ < qx0 + 26 and py_ < sy + 8:
                continue
            if abs(py_ - sy) < 10 and sx < px_ < fx:
                continue
            if any(_overlap((px_ - 6, py_ - 6, 12, 12), t_, 4, 4) for t_ in taken) or any(abs(px_ - a) < 28 and abs(py_ - b) < 24
                                                                                             for a, b in dots):
                continue
            dots.append((px_, py_))
        sc.put('emap.dots', [R('emap/d%d' % j, a - 4.5, b - 4.5, 9, 9, prst='ellipse', fill='D6D0E4', line=None)
                             for j, (a, b) in enumerate(dots)])
        under.append('emap.dots')
        anim['emap.dots'] = dict(kind='fade_in', delay=500, dur=500)
        tot_h = max(my0 + mh, kbot + 90) - TOP
        sc.put('pair.div', [R('pair/div', LX0 + HW + GX_ / 2 - 0.6, TOP + 8, 1.2, tot_h - 16, fill=LINE2, line=None)])
        under.insert(0, 'pair.div')
        box = union([sc.box[k_] for k_ in under + over])
        recs = list(K['ranks']) + list(E_['ranks']) + [mk_]
        return dict(under=under, over=over, alpha=al, anim=anim, box=box, recs=recs, zmax=PR.get('zmax', 1.3))

    # -------------------------------------------------------------- 1 더미: 이야기 기록도 작은 조각으로, 아무 데나 흩어짐(옅게) → 몇 개만 켜짐
    cap_c = dict(t=CP['cloud'])
    _, _, ccw, cch = cap_measure(cap_c, 'top')
    ccam, ccrect = frame(CLOUD_BOX, 'top', 0.9, ccw, cch)
    cx_, cy_, cz, cvx, cvy = ccam

    def W(sx, sy):
        return ((sx - cvx) / cz + cx_, (sy - cvy) / cz + cy_)
    vx0, vy0 = W(26, 108)
    vx1, vy1 = W(1254, 708)
    ax0, ay0 = W(ccrect[0] - 30, ccrect[1] - 16)
    ax1, ay1 = W(ccrect[0] + ccrect[2] + 30, ccrect[1] + ccrect[3] + 22)
    fills = list(spec.get('fill', [])) + EXTRA
    fills = fills[:max(0, spec.get('n_cloud', 26) - len(keys))]
    items = [('cl.' + k, S.frag_w(REC[k]['title'], chip_text(REC[k])), S.FRAG_H) for k in keys]
    fitems = [('f%d' % i, S.frag_w(t, m), S.FRAG_H) for i, (_, t, m) in enumerate(fills)]
    import random
    random.Random(spec.get('seed', 11)).shuffle(items)
    random.Random(spec.get('seed', 11) + 1).shuffle(fitems)
    items += fitems                  # 조각이 커져 자리가 빠듯하니 이야기 기록부터 자리 잡게(빠지면 안 됨)
    cpos = scatter(items, (vx0, vy0, vx1, vy1), [(ax0, ay0, ax1 - ax0, ay1 - ay0)], spec.get('seed', 11) + 3)
    cloud = []
    for k in keys:
        if 'cl.' + k in cpos:
            x, y = cpos['cl.' + k]
            sc.put('cl.' + k, frag_at(k, k, x, y))
            sc.box['cl.' + k] = (x, y, S.frag_w(REC[k]['title'], chip_text(REC[k])), S.FRAG_H)
            cloud.append('cl.' + k)
    fill_keys = []
    for i, (ic, t, m) in enumerate(fills):
        if 'f%d' % i in cpos:
            x, y = cpos['f%d' % i]
            sc.put('f%d' % i, card_prims('f%d' % i, 'frag', x, y, None, t, m, icon=ic)[0])
            fill_keys.append('f%d' % i)
    F = spec['fail']
    lit = spec.get('lit') or []
    if not lit:
        first = F['hits']['ranks'] if F.get('mode', 'brief') == 'brief' else F['kw']['ranks']
        for k in [hops[0]['target'], first[0], hops[-1]['target']] + list(first[1:]):
            if k not in lit and len(lit) < 4:
                lit.append(k)
    lits = []
    for k in lit:
        x, y = cpos['cl.' + k]
        sc.put('lit.' + k, frag_at('lit.' + k, k, x, y, style='weave'))
        lits.append('lit.' + k)

    # -------------------------------------------------------------- 2 실패: 일반 검색 판 + 결과 목록(1·2·3, 판 옆에 세로로) + 결과 밖의 답
    mode = F.get('mode', 'brief')
    LX = EX + EW + 70
    passes, PAIR, mk_ = [], None, None
    if mode == 'pair':
        PAIR = pair_items()
    else:
        if mode == 'brief':
            plan = [('fail', 'gen', '일반 검색', '키워드 + 임베딩', F['words'], True, F['hits'], '같은 단어 + 비슷한 뜻', False)]
        else:
            plan = [('fail_kw', 'kw', '키워드 검색', 'BM25', F['words'], False, F['kw'], None, False),
                    ('fail_emb', 'emb', '임베딩 검색', '비슷한 뜻', [], True, F['emb'], '뜻을 숫자로 바꿔 비교', True)]
        passes = []
        for skey, pk, title, pill, words, bars, hit, blabel, under in plan:
            ranks = hit['ranks']
            hs = [card_at(k, 0, 0, img_h=LIST_IMG_H)[1] for k in ranks]
            gap = 50
            tot = sum(hs) + gap * (len(hs) - 1)
            mid = F.get('mid_y', 392)
            prims, port, ph = search_panel(pk, 0, title, pill, F['query'], words, bars, label=blabel, under=under)
            py = mid - ph / 2
            prims, port, ph = search_panel(pk, py, title, pill, F['query'], words, bars, label=blabel, under=under)
            sc.put(pk, prims)
            y = mid - tot / 2 + 8
            rs, ths, rks, tgs, mks = [], [], [], [], []
            maxw = 0
            for i, (k, h) in enumerate(zip(ranks, hs)):
                pr, h, pos = card_at(k, LX, y, style='gray', img_h=LIST_IMG_H)
                rk = '%s.res.%s' % (pk, k)
                sc.put(rk, pr)
                rs.append(rk)
                box = (LX, y, REC[k]['w'], h)
                maxw = max(maxw, REC[k]['w'])
                bn = '%s.rank%d' % (pk, i + 1)
                sc.put(bn, [R('rank%d/c' % (i + 1), LX - 13, y - 12, 26, 26, prst='ellipse', fill='8E88A0', line='FFFFFF', line_w=1.6),
                            T('rank%d/t' % (i + 1), LX - 13, y - 12, 26, 26, str(i + 1), size=10, color='FFFFFF', weight='b', align='c',
                              anchor='ctr')])
                rks.append(bn)
                th = '%s.th%d' % (pk, i + 1)
                sc.put(th, [C(th + '/l', scurve(port, (LX - 2, y + min(h / 2, 34)), 0.5), w=1.8, color='B9B3C8')])
                ths.append(th)
                if hit.get('tags', {}).get(k):
                    tg = '%s.tag.%s' % (pk, k)
                    sc.put(tg, tag_box(box, hit['tags'][k], name='tag.' + k, pt=11))
                    tgs.append(tg)
                if hit.get('marks', {}).get(k):
                    mk = '%s.mk.%s' % (pk, k)
                    marks_at(pos, hit['marks'][k], mk, alpha=30)
                    mks.append(mk)
                for j, (where, sub) in enumerate(hit.get('sims', {}).get(k, [])):
                    sm = '%s.sim%d.%s' % (pk, j, k)
                    if where == 'img':
                        ix, iy, iw, ih = pos['img']
                        lab = '≈ ' + sub
                        cw_ = tw(lab, 9.5, 'b') + 22
                        sc.put(sm, [R(sm + '/bg', ix + 8, iy + ih - 32, cw_, 24, prst='roundRect', fill='FFFFFF', line=PURPLE2, line_w=1.3,
                                      dash='dash'),
                                    T(sm + '/t', ix + 8, iy + ih - 32, cw_, 24, lab, size=9.5, color=PURPLE, weight='b', align='c', anchor='ctr')])
                    else:
                        sc.put(sm, underline_prims(sm + '/l', band(pos[where], sub, kind='full')))
                    mks.append(sm)
                y += h + gap
            passes.append(dict(skey=skey, pk=pk, ranks=list(ranks), rs=rs, ths=ths, rks=rks, tgs=tgs, mks=mks, maxw=maxw, mid=mid))
        # 결과 밖의 답: 더미 조각 그대로(답이 미리 읽히지 않게) 목록 오른쪽에 옅게 + 점선 테두리 + 태그(먼저 알아야 할 단서)
        M = F['miss']
        mk_ = M['key']
        lastp = passes[-1]
        mw_ = S.frag_w(REC[mk_]['title'], chip_text(REC[mk_]))
        mx_ = LX + lastp['maxw'] + 74
        my_ = lastp['mid'] - S.FRAG_H / 2
        sc.put('missf.' + mk_, frag_at(mk_, mk_, mx_, my_))
        mt = M['tag']
        mtw = tw(mt, 11, 'sb') + 26
        tx_ = mx_ + mw_ / 2 - mtw / 2
        sc.put('miss', [R('miss/r', mx_ - 10, my_ - 10, mw_ + 20, S.FRAG_H + 20, prst='roundRect', radius=18, fill=None, line=GRAY_LINE,
                          line_w=1.8, dash='dash'),
                        R('miss/tag', tx_, my_ + S.FRAG_H + 22, mtw, 30, prst='roundRect', fill='EFECF4', line=None),
                        T('miss/tag_t', tx_, my_ + S.FRAG_H + 22, mtw, 30, mt, size=11, color=SUB, weight='sb', align='c', anchor='ctr')])

    # -------------------------------------------------------------- 홉마다: Reasoning Embedding 판(다시 쓴 질문 통째로) + 필터
    re_keys = {}

    def re_key(n):
        if n in re_keys:
            return re_keys[n]
        hop = hops[n - 1]
        cond = hop['filter'].get('cond', hop['filter']['label']) if hop.get('filter') else hop.get('cond')
        if n == 1:
            token, rest = None, hop['q']
        else:
            token = hops[n - 2]['token']
            rest = hop['q'][2] if len(hop['q']) > 2 else hop['q'][1]
        key = 're:%d' % n
        prims, pt_, fc, h = engine_block(key, sc.RE_Y, 'Reasoning Embedding',
                                         'Hop %d  %s' % (n, '다시 쓴 질문으로 찾기' if n > 1 else '첫 질문으로 찾기'), token, rest, cond, 're',
                                         chip_name=('tok%d' % (n - 1)) if n > 1 else None)
        sc.put(key, prims)
        re_keys[n] = key
        sc.re_pt = pt_
        return key

    H = []
    for i, hop in enumerate(hops):
        n = i + 1
        h = dict(n=n, hop=hop)
        re_key(n)
        f = hop.get('filter')
        if f:
            fk = f['keep']
            x0 = min(sc.box[k][0] for k in fk) - 14
            y0 = min(sc.box[k][1] for k in fk) - 18
            x1 = max(sc.box[k][0] + sc.box[k][2] for k in fk) + 14
            y1 = max(sc.box[k][1] + sc.box[k][3] for k in fk) + 14
            lab = f['label']
            lw_ = tw('필터  ' + lab, 10, 'b') + 24
            sc.put('fb%d' % n, [R('fb%d/r' % n, x0, y0, x1 - x0, y1 - y0, prst='roundRect', radius=18, fill=LAV, alpha=30,
                                  line=PURPLE2, line_w=1.6, dash='dash'),
                                R('fb%d/lb' % n, x0 + 14, y0 - 14, lw_, 28, prst='roundRect', fill='FFFFFF', line=PURPLE2, line_w=1.4,
                                  dash='dash'),
                                T('fb%d/lt' % n, x0 + 14, y0 - 14, lw_, 28, [[('필터  ', {'color': PURPLE2}), (lab, {'color': PURPLE})]],
                                  size=10, color=PURPLE, weight='b', align='c', anchor='ctr')])
            sc.box['fb%d' % n] = (x0, y0, x1 - x0, y1 - y0)
            for k, lab2 in f.get('drop', {}).items():
                sc.put('drop%d.%s' % (n, k), tag_box(sc.box[k], lab2, style='grayfill', name='drop%d.%s' % (n, k)))
            for k, marks in f.get('marks', {}).items():
                marks_at(sc.pos[k], marks, 'fm%d.%s' % (n, k), owner_=k, alpha=30)
            h['fbox'] = sc.box['fb%d' % n]
        k = hop['target']
        tb = sc.box[k]
        sc.put('th%d' % n, S.thread_prims('th%d' % n, thread_to(sc.re_pt, tb)))
        h['cands'] = list(hop.get('cands', {}))
        for ck, lab2 in hop.get('cands', {}).items():
            cb = sc.box[ck]
            sc.put('thc%d.%s' % (n, ck), [C('thc%d.%s/l' % (n, ck), thread_to(sc.re_pt, cb), w=1.6, color='C9BFF0', dash='sysDash')])
            sc.put('why%d.%s' % (n, ck), tag_box(cb, lab2, style='grayfill', where=hop.get('why_at', {}).get(ck, 'tr'),
                                                  name='why%d.%s' % (n, ck), pt=11))
        if hop.get('marks'):
            h['mark0'] = marks_at(sc.pos[k], hop['marks'], 'hm%d' % n, owner_=k)[0]
        for pk_, (plab, pst) in hop.get('pills', {}).items():
            ix, iy, iw, ih = sc.pos[pk_]['img']
            pw = tw(plab, 9, 'b') + 22
            px0, py0 = ix + iw / 2 - pw / 2, iy + ih - 32
            sc.put('pl%d.%s' % (n, pk_), [R('pl%d.%s/bg' % (n, pk_), px0, py0, pw, 24, prst='roundRect', fill='FFFFFF',
                                            line=PURPLE if pst == 'weave' else GRAY_LINE, line_w=1.2),
                                          T('pl%d.%s/t' % (n, pk_), px0, py0, pw, 24, plab, size=9,
                                            color=PURPLE if pst == 'weave' else BODY, weight='b', align='c', anchor='ctr')],
                   owner=pk_)
            sc.pos['pl%d.%s' % (n, pk_)] = (px0 + 11, py0 + 12 - 9 * 4 / 3 / 2 - 1, plab, 9, 'b')
        if hop.get('img_marks'):
            from PIL import Image
            for ik, rects_px in hop['img_marks'].items():
                ix, iy, iw, ih = sc.pos[ik]['img']
                IW, IH = Image.open(S.AS / REC[ik]['img']).size
                rr = [(ix + (a - 4) * iw / IW, iy + (b - 3) * ih / IH, (c - a + 8) * iw / IW, (d - b + 6) * ih / IH) for a, b, c, d in rects_px]
                sc.put('im%d' % n, [R('im%d/%d' % (n, j), *r_, prst='roundRect', radius=2.5, fill=HL, alpha=38, line=None)
                                    for j, r_ in enumerate(rr)], owner=ik)
                h.setdefault('mark0', rr[0])
        if hop.get('pill_mark'):
            pk_, sub = hop['pill_mark']
            r_ = band(sc.pos['pl%d.%s' % (n, pk_)], sub, kind='full')
            sc.put('pm%d' % n, [R('pm%d/0' % n, *r_, prst='roundRect', radius=2.5, fill=HL, alpha=34, line=None)], owner=pk_)
        h['target'] = k
        # 찾은 단서 칩(꽉 찬 보라는 단서에만): 기록 아래 → 다음 질문의 빈칸으로(마지막은 답). 같은 이름이라 모핑으로 날아감
        last = n == nh
        lab = spec['answer'] if last else hop['token']
        tkw = chip_prims('x', 0, 0, lab, pt=10, padx=11)[1]
        below = (h['fbox'][1] + h['fbox'][3] + 8) if f else (tb[1] + tb[3] + 10)
        at = hop.get('tok_at', (tb[0] + tb[2] - tkw - 6, below))
        sc.put('tok%d@src' % n, chip_prims('tok%d' % n, at[0], at[1], lab, style='fill', pt=10, h=26, padx=11)[0])
        if last:
            cw_ = chip_prims('x', 0, 0, lab, pt=10, padx=9)[1]
            sc.put('tok%d@q' % n, chip_prims('tok%d' % n, sc.X0, sc.ans_y, lab, style='fill', pt=10, h=23, padx=9)[0])
            okx = sc.X0 + cw_ + 6
            if sc.ok_below:       # 답이 길면 '멈춤'은 답 아래 줄로(판도 그만큼 길어짐)
                sc.put('qans.ok', chip_prims('qans.ok', sc.X0, sc.ans_y + 30, '멈춤', style='soft', pt=9, h=21, padx=8)[0])
            else:
                sc.put('qans.ok', chip_prims('qans.ok', okx, sc.ans_y + 1, '멈춤', style='soft', pt=9, h=21, padx=8)[0])
        else:
            sc.put('tok%d@q' % n, chip_prims('tok%d' % n, sc.X0, sc.row_y(n + 1) - 1, lab, style='fill', pt=10, h=23, padx=9)[0])
        H.append(h)

    # -------------------------------------------------------------- Weave 하이브리드 한눈에: 질문 → 중간 단서(가운데 기록) → 답 기록 → 답
    HY = spec.get('hybrid')
    HYB = None
    if HY:
        mid = HY.get('mid', hops[0]['target'])
        ansk = HY.get('ans', hops[-1]['target'])
        cm = REC[mid]
        mx0, my0_, mw0, mh0 = cm['x'], cm['y'], cm['w'], cm['h']
        cyc = my0_ + mh0 / 2
        qt = HY.get('q', spec['ask'])
        qw = tw(qt, 10.5, 'm') + 52
        qx = mx0 - HY.get('gap1', 104) - qw
        sc.put('hy.q', [R('hq/bg', qx, cyc - 22, qw, 44, prst='roundRect', fill='FFFFFF', line=LINE2, line_w=1.2, shadow=S.L.SHADOW_SOFT),
                        R('hq/lens', qx + 17, cyc - 8, 12, 12, prst='ellipse', fill=None, line='9AA0A6', line_w=1.6),
                        R('hq/lens2', qx + 26, cyc + 3, 6, 2, fill='9AA0A6', line=None),
                        T('hq/t', qx + 38, cyc - 22, qw - 44, 44, qt, size=10.5, color=INK, weight='m', anchor='ctr')])
        ca = REC[ansk]
        aimg_h = HY.get('img_h', 84)
        ah = card_at(ansk, 0, 0, img_h=aimg_h)[1]
        ax0 = mx0 + mw0 + HY.get('gap2', 128)
        ay0 = cyc - ah / 2
        apr, ah, apos = card_at(ansk, ax0, ay0, style='weave', img_h=aimg_h)
        sc.put('hy.ans', apr)
        sc.put('hth1', S.thread_prims('hth1', scurve((qx + qw + 2, cyc), (mx0 - 2, cyc), 0.5)))
        sc.put('hth2', S.thread_prims('hth2', scurve((mx0 + mw0 + 2, cyc), (ax0 - 2, cyc), 0.5)))
        tok = hops[0]['token']
        tkw = chip_prims('x', 0, 0, tok, pt=10, padx=9)[1]
        tmx = (mx0 + mw0 + ax0) / 2
        sc.put('htok', chip_prims('htok', tmx - tkw / 2, cyc - 13, tok, style='fill', pt=10, h=26, padx=9)[0])
        ans = spec['answer']
        aw = chip_prims('x', 0, 0, ans, pt=10.5, padx=13)[1]
        acx = ax0 + ca['w'] / 2
        sc.put('hth3', S.thread_prims('hth3', vcurve((acx, ay0 + ah + 2), (acx, ay0 + ah + 24))))
        sc.put('hans', chip_prims('hans', acx - aw / 2, ay0 + ah + 26, ans, style='fill', pt=10.5, h=30, padx=13)[0])
        marks_at(sc.pos[mid], HY.get('marks_mid', []), 'hy.mk1', owner_=mid)
        marks_at(apos, HY.get('marks_ans', []), 'hy.mk2', alpha=30)

        def hlab(name, cx, y, text, style='outline'):
            w = tw(text, 9.5, 'b') + 24
            sc.put(name, chip_prims(name, cx - w / 2, y, text, style=style, pt=9.5, h=24, padx=12)[0])
        l1, l2, l3 = HY['labels']
        hlab('hy.l1', (qx + qw + mx0) / 2, cyc - 46, l1)
        hlab('hy.l2', tmx, cyc - 48, l2)
        mp_ = apos['meta']
        hlab('hy.l3', mp_[0] + tw(mp_[2], mp_[3]) / 2, ay0 - 32, l3)
        mlw = tw(HY.get('mid_label', '중간 단서'), 9.5, 'b') + 24
        hlab('hy.mid', mx0 + 6 + mlw / 2, my0_ - 32, HY.get('mid_label', '중간 단서'), style='soft')
        hu = ['hth1', 'hth2', 'hth3']
        ho = ['hy.q', mid, 'hy.mk1', 'hy.mid', 'htok', 'hy.ans', 'hy.mk2', 'hans', 'hy.l1', 'hy.l2', 'hy.l3']
        ha = {'hth1': dict(kind='wipe_in', dir='left', delay=350, dur=450), 'hy.l1': dict(kind='zoom_in', delay=750, dur=280),
              'hy.mk1': dict(kind='wipe_in', dir='left', delay=850, dur=420), 'hy.mid': dict(kind='zoom_in', delay=1100, dur=280),
              'hth2': dict(kind='wipe_in', dir='left', delay=1400, dur=450), 'htok': dict(kind='zoom_in', delay=1650, dur=300),
              'hy.l2': dict(kind='zoom_in', delay=1850, dur=280), 'hy.mk2': dict(kind='wipe_in', dir='left', delay=2150, dur=420),
              'hy.l3': dict(kind='zoom_in', delay=2300, dur=280), 'hth3': dict(kind='wipe_in', dir='down', delay=2600, dur=300),
              'hans': dict(kind='zoom_in', delay=2800, dur=320)}
        HYB = dict(under=hu, over=ho, anim=ha, mid=mid, box=union([sc.box[k_] for k_ in hu + ho]), zmax=HY.get('zmax', 1.25))

    # -------------------------------------------------------------- 00 사전 준비(00판): 기록 하나 → 벡터 + 메타데이터, 모든 기록 → 기기 안 저장소
    IX = spec.get('index')
    IXD = None
    if IX:
        ik = IX.get('key', hops[0]['target'])
        ck = REC[ik]
        x0_, y0_ = cpos['cl.' + ik]
        cpr, ch_, _ = card_at(ik, x0_, y0_)
        sc.put('ix.card', cpr)
        EWD, EH = IX.get('entry_w', 436), 172
        ex0 = x0_ + ck['w'] + 78
        ey0 = y0_ + ch_ / 2 - EH / 2
        ent = [R('ixe/bg', ex0, ey0, EWD, EH, prst='roundRect', radius=16, fill='FFFFFF', line=RING, line_w=1.6, shadow=S.L.SHADOW_CARD,
                 glow=(8, RING, 22)),
               P('ixe/ic', S.ICON['spool'], ex0 + 16, ey0 + 13, 18, 18),
               T('ixe/h', ex0 + 40, ey0 + 11, 260, 22, IX.get('entry_title', '기기 안에 저장한 모습'), size=10, color=PURPLE2, weight='b',
                 anchor='ctr')]
        LX_, VX_ = ex0 + 18, ex0 + 104
        rows_ = [('글자', ey0 + 46, 20), ('벡터', ey0 + 78, 22), ('메타데이터', ey0 + 128, 26)]
        for j, (lab_, yy_, hh_) in enumerate(rows_):
            ent.append(T('ixe/l%d' % j, LX_, yy_, 84, hh_, lab_, size=9.5, color=PURPLE if j else MUTE, weight='b', anchor='ctr'))
        ent.append(T('ixe/v0', VX_, ey0 + 46, EWD - (VX_ - ex0) - 14, 20, IX.get('text', ''), size=9.5, color=MUTE, anchor='ctr'))
        sc.put('ix.entry', ent)
        sc.put('ix.vec', vec_prims('ixv', VX_, ey0 + 78, IX.get('n_vec', 16), 14, 22, ''.join(ck.get('lines', ())) + ck['title']) +
               [T('ixv/n', VX_, ey0 + 103, 260, 16, IX.get('nums', '[0.12, −0.53, 0.88, …]'), size=8.5, color=MUTE, anchor='ctr')])
        mx_, meta_ = VX_, []
        for j, (ic, lab_) in enumerate(IX['meta']):
            pr, cw_ = chip_prims('ixm%d' % j, mx_, ey0 + 128, lab_, style='outline', pt=9, h=26, padx=10, icon=ic)
            meta_ += pr
            mx_ += cw_ + 8
        sc.put('ix.meta', meta_)
        if mx_ - 8 > ex0 + EWD - 12:
            print('   ! 00 메타데이터 칩이 판을 넘침 (%.0f > %.0f)' % (mx_ - 8, ex0 + EWD - 12))
        sc.put('ixth', S.thread_prims('ixth', scurve((x0_ + ck['w'] + 2, y0_ + ch_ / 2), (ex0 - 2, ey0 + EH / 2), 0.5)))
        close = ['ixth', 'ix.card', 'ix.entry', 'ix.vec', 'ix.meta']
        a1_ = {'ixth': dict(kind='wipe_in', dir='left', delay=300, dur=450), 'ix.entry': dict(kind='rise', delay=600, dur=450),
               'ix.vec': dict(kind='wipe_in', dir='left', delay=1050, dur=700), 'ix.meta': dict(kind='wipe_in', dir='left', delay=1700, dur=600)}
        # 저장소: 이야기 기록은 한 줄씩(아이콘 + 이름 + 작은 벡터 + 날짜), 나머지 조각은 아래 묶음으로 날아 들어감
        rows = IX.get('rows', keys)
        SW, RH, RG = IX.get('store_w', 470), 36, 7
        n_f = len(fill_keys)
        SH = 58 + len(rows) * (RH + RG) + 14 + 30 + 2.5 * n_f + 34
        scx, scy = IX.get('store_c', (CLOUD_BOX[0] + CLOUD_BOX[2] / 2, CLOUD_BOX[1] + CLOUD_BOX[3] / 2))
        sx0, sy0 = scx - SW / 2, scy - SH / 2
        st_ = [R('ixs/bg', sx0, sy0, SW, SH, prst='roundRect', radius=18, fill='FFFFFF', line=LINE2, line_w=1.4, shadow=S.L.SHADOW_CARD),
               P('ixs/ic', S.ICON['spool'], sx0 + 18, sy0 + 17, 20, 20),
               T('ixs/h', sx0 + 46, sy0 + 15, 220, 24, IX.get('store_title', '기기 안 저장소'), size=12, color=PURPLE, weight='b', anchor='ctr'),
               T('ixs/h2', sx0 + SW - 18 - 200, sy0 + 15, 200, 24, '벡터 + 메타데이터', size=9, color=MUTE, weight='sb', align='r', anchor='ctr')]
        sc.put('ix.store', st_)
        store = ['ix.store']
        a2_ = {}
        for j, k in enumerate(rows):
            c = REC[k]
            ry_ = sy0 + 54 + j * (RH + RG)
            ic = c.get('icon') or KIND_ICON.get(c['kind'], 'talk')
            dt = short_date(c.get('meta', ''))
            dw = chip_prims('x', 0, 0, dt, pt=9, padx=9)[1]
            pr = [R(k + '/bg', sx0 + 14, ry_, SW - 28, RH, prst='roundRect', radius=10, fill='FFFFFF', line=LINE, line_w=0.9),
                  P(k + '/ic', S.ICON[ic], sx0 + 26, ry_ + 8, 20, 20),
                  T(k + '/title', sx0 + 54, ry_, 130, RH, c['title'], size=10, color=INK, weight='b', anchor='ctr')]
            pr += vec_prims('ixr%d' % j, sx0 + 190, ry_ + 10, 10, 9, 16, ''.join(c.get('lines', ())) + c['title'] + c.get('meta', ''))
            pr += chip_prims('ixr%d/d' % j, sx0 + SW - 26 - dw, ry_ + 6, dt, style='soft', pt=9, h=24, padx=9)[0]
            sc.put('ixs.' + k, pr)
            store.append('ixs.' + k)
        by_ = sy0 + 54 + len(rows) * (RH + RG) + 10
        stack = []
        for j, fk in enumerate(fill_keys):
            sc.put('ixs.' + fk, [R(fk + '/bg', sx0 + 14 + 6 * (j % 2), by_ + 2.5 * j, SW - 28 - 12, 30, prst='roundRect', radius=10,
                                   fill='FFFFFF', line=LINE, line_w=0.8)])
            stack.append('ixs.' + fk)
        fy_ = by_ + 2.5 * max(0, n_f - 1)
        fxo = sx0 + 14 + 6 * ((n_f - 1) % 2)
        sk = [R('ixs/sk_ic', fxo + 12, fy_ + 7, 16, 16, prst='roundRect', radius=4, fill='E9E5F2', line=None),
              R('ixs/sk_t', fxo + 40, fy_ + 11, 70, 8, prst='roundRect', radius=4, fill='ECE8F4', line=None),
              R('ixs/sk_d', fxo + SW - 40 - 12 - 54, fy_ + 7, 54, 16, prst='roundRect', fill='F1ECFF', line=None)]
        sk += [(p_[0], p_[1], p_[2], p_[3], p_[4], p_[5], dict(p_[6], alpha=45)) for p_ in vec_prims('ixs/sk_v', sx0 + 190, fy_ + 8, 10, 9, 14, 'more')]
        sc.put('ix.more', sk + [T('ixs/more', sx0, by_ + 2.5 * n_f + 34, SW, 22, IX.get('more', '그 밖의 기록도 모두 같은 모양으로'),
                                  size=9.5, color=MUTE, weight='sb', align='c', anchor='ctr')])
        store += stack + ['ix.more']
        a2_ = {'ix.more': dict(kind='fade_in', delay=1500, dur=400)}
        IXD = dict(key=ik, close=close, anim1=a1_, box1=union([sc.box[k_] for k_ in close]), store=store, anim2=a2_,
                   box2=sc.box['ix.store'])

    # -------------------------------------------------------------- 단계 진행
    cur, styles = [], {}

    def show(*ks):
        for k in ks:
            if k not in cur and k in sc.items:
                cur.append(k)

    def hide(*ks):
        for k in ks:
            if k in cur:
                cur.remove(k)

    def show_under(*ks):
        """실은 카드 밑으로."""
        for k in reversed(ks):
            if k not in cur and k in sc.items:
                cur.insert(0, k)

    def shot(key, frame_keys, side, focus, hud, zmax, anim=None, half=(), pad=16, cap=None, notes=None, morph=1400, frame_box=None,
             cap_y=None, cap_x=None, alpha=None):
        cap = cap or CP[key]
        cap = cap if isinstance(cap, dict) else dict(t=cap)
        shown = list(cur)
        half = set(half)
        focus = set(focus)
        if 'qp' in focus:
            focus.add('qp.head')
        if 'qp' in half:
            half.add('qp.head')
        for x in list(shown):
            o = owner.get(x)
            if o is None:
                continue
            if o in focus:
                focus.add(x)
            elif o in half:
                half.add(x)
            else:
                shown.remove(x)
        box = frame_box or union([sc.box[k] for k in frame_keys])
        _, _, cw, ch = cap_measure(cap, side)
        cam, crect = frame(box, side, zmax, cw, ch, pad, cap_y=cap_y, cap_x=cap_x)
        lab = ' '.join(''.join(t for t, _ in cap['t']).split())
        sc.steps.append(Step(key=key, cam=cam, cap=cap, cap_rect=(crect, side), show=shown, focus=focus, half=half, styles=dict(styles),
                             hud=hud, anim=anim or {}, notes=notes if notes is not None else NT[key], morph_ms=morph, label=lab,
                             alpha=dict(alpha or {})))

    def cx_of(k):
        b = sc.box[k]
        return b[0] + b[2] / 2

    def cy_of(k):
        b = sc.box[k]
        return b[1] + b[3] / 2

    ui_base = ['ui'] + (['ui.glogo', 'ui.sbox'] if kind == 'google' else ['ui.head', 'ui.msg']) + ['ui.kbd', 'ui.keys']
    D = lambda *s_: set(s_)   # noqa: E731
    show(*ui_base)
    # 1 상황: 폰 위쪽(질문)을 가까이
    if kind == 'google':
        ob = union([sc.box['ui.sbox'], (PX + 20, PY + 40, PW - 40, 50)])
    else:
        hb = union([sc.box['ui.head'], sc.box['ui.msg']])
        ob = (PX + 4, hb[1], PW - 8, hb[3])
    shot('open', [], 'right', set(ui_base), {}, 2.1, frame_box=ob)
    # 2 더미: 흩어진 조각이 하나씩 떠오르고(옅게), 몇 개만 보라 테두리로 켜짐
    hide(*ui_base)
    all_cloud = cloud + fill_keys
    show(*all_cloud, *lits)
    order = list(all_cloud)
    random.Random(spec.get('seed', 11) + 1).shuffle(order)
    t_end = 120 + 38 * len(order) + 300
    shot('cloud', [], 'top', set(all_cloud + lits), {}, 0.9, frame_box=CLOUD_BOX, morph=1700,
         alpha={k: CLOUD_ALPHA for k in all_cloud},
         anim=dict({k: dict(kind='zoom_in', delay=120 + 38 * j, dur=360) for j, k in enumerate(order)},
                   **{x: dict(kind='zoom_in', delay=t_end + 420 * j, dur=380) for j, x in enumerate(lits)}))
    hide(*lits)
    if IXD:
        # 00 사전 준비(00판): 더미 속 지은 카톡 하나를 가까이 → 벡터 + 메타데이터. 이어서 모든 조각이 기기 안 저장소로 날아 들어감
        hide('cl.' + IXD['key'])
        show(*IXD['close'])
        shot('idx1', [], 'top', set(IXD['close']), {}, IX.get('z1', 1.6), frame_box=IXD['box1'], cap=CP['idx1'], notes=NT['idx1'],
             morph=1700, anim=IXD['anim1'])
        hide(*IXD['close'], *all_cloud, *['cl.' + k for k in keys])
        show(*IXD['store'])
        shot('idx2', [], IX.get('side2', 'left'), set(IXD['store']), {}, IX.get('z2', 1.3), frame_box=IXD['box2'], cap=CP['idx2'], notes=NT['idx2'],
             morph=1900, anim=IXD['anim2'])
        hide(*IXD['store'])
    # 3 실패: 결과는 판 옆에 1·2·3 목록으로 뽑혀 나오고(더미에서 날아옴), 답이 있는 기록은 결과 밖에 옅게 남음
    prev = []
    if PAIR:      # 키워드(왼쪽)와 임베딩(오른쪽)을 한 장에: 둘 다 안 됨
        hide(*all_cloud, *['cl.' + k for k in keys])
        show_under(*PAIR['under'])
        show(*PAIR['over'])
        shot('fail_pair', [], 'top', set(PAIR['under'] + PAIR['over']), {}, PAIR['zmax'], frame_box=PAIR['box'], alpha=PAIR['alpha'],
             morph=1700, anim=PAIR['anim'])
        prev = PAIR['under'] + PAIR['over']
    for j, P_ in enumerate(passes):
        hide(*prev)
        last_pass = j == len(passes) - 1
        moved = ['cl.' + k for k in P_['ranks']] + (['cl.' + mk_] if last_pass else [])
        hide(*moved)
        show(*[('cl.' + k) for k in keys if ('cl.' + k) not in moved and ('cl.' + k) in sc.items])
        extra = (['missf.' + mk_, 'miss'] if last_pass else [])
        show_under(*P_['ths'])
        show(P_['pk'], *P_['rs'], *P_['rks'], *P_['tgs'], *P_['mks'], *extra)
        foc = set([P_['pk']] + P_['rs'] + P_['ths'] + P_['rks'] + P_['tgs'] + P_['mks'] + extra)
        fb = union([sc.box[x] for x in [P_['pk']] + P_['rs'] + P_['tgs'] + extra])
        al = {'missf.' + mk_: 42} if last_pass else {}
        n_r = len(P_['rs'])
        shot(P_['skey'], [], 'top', foc, {}, 1.45, frame_box=fb, alpha=al, morph=1700,
             anim=dict({P_['pk']: dict(kind='rise', delay=0, dur=420)},
                       **{t_: dict(kind='wipe_in', dir='left', delay=380 + 140 * i, dur=380) for i, t_ in enumerate(P_['ths'])},
                       **{m_: dict(kind='wipe_in', dir='left', delay=650 + 120 * i, dur=360) for i, m_ in enumerate(P_['mks'])},
                       **{t_: dict(kind='zoom_in', delay=1000 + 160 * i, dur=280) for i, t_ in enumerate(P_['tgs'])},
                       **({'miss': dict(kind='fade_in', delay=1100 + 160 * n_r, dur=500)} if last_pass else {})))
        prev = [P_['pk']] + P_['rs'] + P_['ths'] + P_['rks'] + P_['tgs'] + P_['mks'] + extra
    if HYB:       # Weave 하이브리드 한눈에: 단서를 잡아 중간 단계를 채움(키워드 + 멀티홉 + 추론)
        hide(*prev)
        prev = []
        styles[HYB['mid']] = 'weave'
        show_under(*HYB['under'])
        show(*HYB['over'])
        shot('hybrid', [], 'top', set(HYB['under'] + HYB['over']), {}, HYB['zmax'], frame_box=HYB['box'],
             cap=dict(t=CP['hybrid'], pill=CP.get('hybrid_pill')), notes=NT['hybrid'], morph=1700, anim=HYB['anim'])
        hide(*HYB['under'], *HYB['over'])
        styles.pop(HYB['mid'], None)
    hide(*prev, *all_cloud)
    # 4 01 순간 감지
    show(*ui_base)
    trig = {'google': ['ui.on', 'ui.tap'], 'sheet': ['ui.on', 'ui.tap', 'ui.sheet'], 'gps': ['ui.loc', 'ui.on']}[kind]
    show(*trig)
    if kind == 'google':
        tb_ = union([sc.box['ui.glogo'], sc.box['ui.kbd']])
    elif kind == 'sheet':
        tb_ = union([sc.box['ui.head'], sc.box['ui.msg'], sc.box['ui.sheet.top'], sc.box['ui.kbd']])
    else:
        tb_ = union([sc.box['ui.head'], sc.box['ui.msg'], sc.box['ui.loc'], sc.box['ui.kbd']])
    tb_ = (PX + 4, tb_[1], PW - 8, tb_[3])
    shot('trig', [], 'right', set(ui_base + trig), dict(cur='01'), 2.0, frame_box=tb_, cap_y=sc.ui['ky'] + 22,
         anim={k: dict(kind='rise' if k == 'ui.sheet' else 'zoom_in', delay=200 + (700 if k == 'ui.sheet' else 250 * j), dur=420)
               for j, k in enumerate(trig)}, morph=1700)
    hide('ui.tap')
    phone_now = [x for x in cur if x == 'ui' or x.startswith('ui.')]
    hide(*phone_now)
    # 5 02 Query Rewriting: 질문을 나누고, 모르는 건 빈칸으로(한 장)
    qrows = ['q%d' % i for i in range(1, nh + 1)]
    qkeys = ['qp', 'qp.head', 'qorig'] + qrows + ['qans', 'qans.slot']
    styles['q1'] = 'cur'
    show(*qkeys)
    shot('split', ['qp'], 'right', set(qkeys), dict(cur='02', done=D('01')), 1.9, morph=1700,
         anim={x: dict(kind='zoom_in', delay=350 + 300 * j, dur=350) for j, x in enumerate(qrows)})
    re_cur = None
    for h in H:
        n, hop = h['n'], h['hop']
        f = hop.get('filter')
        k = hop['target']
        cands = h['cands']
        hud3 = dict(cur='03', done=D('01', '02'), **({'loop': n} if n > 1 else {}))
        k_re = re_key(n)
        hc = CP['hops'][n - 1]
        hn = NT['hops'][n - 1]
        if n > 1:
            # 02 다시 쓰기: 앞 기록의 단서 칩이 다음 질문의 빈칸으로 날아감(판을 가까이)
            pv = H[n - 2]
            hide('tok%d@src' % (n - 1), *['pl%d.%s' % (n - 1, x) for x in hops[n - 2].get('pills', {})], 'pm%d' % (n - 1),
                 'im%d' % (n - 1), 'hm%d' % (n - 1), pv['target'])
            styles.pop(pv['target'], None)
            show(*qkeys, 'tok%d@q' % (n - 1))
            styles['q%d' % (n - 1)] = 'done' + ('_rw' if n > 2 else '')
            styles['q%d' % n] = 'cur_rw'
            if re_cur:
                hide(re_cur)
                re_cur = None
            shot('rw%d' % n, ['qp'], 'right', (set(qkeys) - {'qorig', 'q%d' % (n - 1)}) | {'tok%d@q' % (n - 1)},
                 dict(cur='02', done=D('01', '03'), loop=n - 1, loop_on=True), 1.9, cap=hc['rw'], notes=hn['rw'], morph=1800,
                 half=['qorig', 'q%d' % (n - 1)], anim={'q%d' % n: dict(kind='pulse', delay=900, dur=450, scale=1.04)})
            hide('tok%d@q' % (n - 1))
        hide(*qkeys)
        if re_cur != k_re:
            if re_cur:
                hide(re_cur)
            show(k_re)
            re_cur = k_re
        hop_box = union([sc.box[x] for x in [k_re, k] + cands + (list(f.get('drop', {})) if f else [])] +
                        ([sc.box['fb%d' % n]] if f else []) + [sc.box['why%d.%s' % (n, c)] for c in cands])
        # 03 찾기: 판 → 실 → 기록. 가까운 후보는 옅은 실 + 이유 태그(후보 카드는 옅게). 필터가 있으면 같은 장에서 먼저 거름
        whys = ['why%d.%s' % (n, c) for c in cands]
        drops = ['drop%d.%s' % (n, x) for x in f.get('drop', {})] if f else []
        fms = ['fm%d.%s' % (n, x) for x in f.get('marks', {})] if f else []
        keep_other = [x for x in (f['keep'] if f else []) if x != k and x not in cands]
        show(k, *cands, *keep_other, *(list(f.get('drop', {})) if f else []))
        show_under('th%d' % n, *['thc%d.%s' % (n, c) for c in cands], *(['fb%d' % n] if f else []))
        show(*whys, *drops, *fms)
        styles[k] = 'weave'
        focus = set([k_re, k, 'th%d' % n] + whys + drops + fms + (['fb%d' % n] if f else []))
        tbx = sc.box[k]
        if tbx[1] <= hop_box[1] + 34:
            fside, fkw = 'top', dict(cap_x=cx_of(k))
        elif tbx[1] + tbx[3] >= hop_box[1] + hop_box[3] - 34:
            fside, fkw = 'bottom', dict(cap_x=cx_of(k))
        else:
            fside, fkw = 'right', dict(cap_y=cy_of(k))
        t0 = 900 if f else 0
        anim = dict({'th%d' % n: dict(kind='wipe_in', dir='left', delay=t0 + 500, dur=700)},
                    **{'thc%d.%s' % (n, c): dict(kind='wipe_in', dir='left', delay=t0 + 100 + 150 * j, dur=500) for j, c in enumerate(cands)},
                    **{w_: dict(kind='zoom_in', delay=t0 + 1300 + 150 * j, dur=300) for j, w_ in enumerate(whys)})
        if f:
            anim.update({'fb%d' % n: dict(kind='fade_in', delay=200, dur=450)})
            anim.update({x: dict(kind='zoom_in', delay=600 + 150 * j, dur=300) for j, x in enumerate(drops)})
            anim.update({x: dict(kind='wipe_in', dir='left', delay=550, dur=400) for x in fms})
        dim_c = {c: 40 for c in cands}
        dim_c.update({x: 40 for x in (f.get('drop', {}) if f else {})})
        shot('find%d' % n, [], fside, focus, hud3, 1.45, cap=hc['find'], notes=hn['find'], frame_box=hop_box, morph=1700 if n == 1 else 1500,
             anim=anim, half=cands + ['thc%d.%s' % (n, c) for c in cands] + keep_other + (list(f.get('drop', {})) if f else []),
             alpha=dim_c, **fkw)
        hide('th%d' % n, *['thc%d.%s' % (n, c) for c in cands], 'fb%d' % n, *whys, *drops, *fms, *cands, *keep_other,
             *(list(f.get('drop', {})) if f else []), k_re)
        re_cur = None
        # 가까이: 기록 하나만 크게. 근거에 형광펜 → 단서 칩
        pills = ['pl%d.%s' % (n, x) for x in hop.get('pills', {})]
        extra = [x for x in ('hm%d' % n, 'im%d' % n, 'pm%d' % n) if x in sc.items]
        show(*pills, *extra, 'tok%d@src' % n)
        focus = set([k, 'tok%d@src' % n] + extra + pills)
        shot('close%d' % n, [k, 'tok%d@src' % n], hop.get('cside', 'right'), focus, hud3, hop.get('zclose', 2.8), cap=hc['close'],
             notes=hn['close'], pad=20, cap_y=cy_of(k), morph=1600,
             anim=dict({'hm%d' % n: dict(kind='wipe_in', dir='left', delay=300, dur=500),
                        'im%d' % n: dict(kind='wipe_in', dir='left', delay=300, dur=500),
                        'pm%d' % n: dict(kind='wipe_in', dir='left', delay=400, dur=500),
                        'tok%d@src' % n: dict(kind='zoom_in', delay=1100, dur=350)},
                       **{x: dict(kind='zoom_in', delay=150 + 150 * j, dur=300) for j, x in enumerate(pills)}))
    # 04 전달: 카드를 가까이. 카드가 열리면 빨간 배지는 사라지고, 자판은 내려감
    last_h = H[-1]
    hide('tok%d@src' % nh, *['pl%d.%s' % (nh, x) for x in hops[-1].get('pills', {})], 'pm%d' % nh, 'im%d' % nh, 'hm%d' % nh,
         last_h['target'])
    styles.pop(last_h['target'], None)
    show(*phone_now)
    hide('ui.loc', 'ui.keys')
    if sc.ui.get('ans_overlaps_msg'):
        hide('ui.msg')
    show('ans', 'ui.tap2')
    styles['ui.on'] = 'nobadge'
    if kind == 'sheet':
        styles['ui.sheet'] = 'big'
        hide('ui.kbd', 'ui.on')
        db = union([sc.box['ans'], sc.box['ui.sheet.big']])
        dfocus = ['ui', 'ui.head', 'ui.sheet', 'ans', 'ui.tap2']
    elif kind == 'google':
        db = union([sc.box['ui.sbox'], sc.box['ans'], sc.box['ui.kbd']])
        dfocus = ui_base + ['ans', 'ui.tap2', 'ui.on']
    else:
        db = union([sc.box['ans'], sc.box['ui.kbd']])
        dfocus = ui_base + ['ans', 'ui.tap2', 'ui.on']
    shot('deliver', [], 'right', set(dfocus), dict(cur='04', done=D('01', '02', '03')), 2.3, frame_box=db, cap_y=cy_of('ans'),
         anim={'ans': dict(kind='rise', delay=200, dur=550), 'ui.tap2': dict(kind='zoom_in', delay=1500, dur=300)}, morph=1800)
    # 결과: 조금 빼서 화면 전체
    hide('ui.tap2', 'ans', 'ui.on', 'ui.kbd', 'ui.keys')
    show('ui.msg')
    if kind == 'google':
        styles['ui.sbox'] = 'done'
        res_keys = ['ui.res'] if 'ui.res' in sc.items else []
        rb = union([sc.box['ui.glogo']] + [sc.box[x] for x in ['ui.sbox'] + res_keys])
    else:
        hide('ui.sheet')
        res_keys = ['res'] if 'res' in sc.items else []
        rb = union([sc.box['ui.head'], sc.box['ui.msg']] + [sc.box[x] for x in res_keys])
    rb = (PX + 4, rb[1], PW - 8, rb[3])
    show(*res_keys)
    shot('result', [], 'right', set(ui_base + res_keys), dict(cur='04', done=D('01', '02', '03')), 1.5, frame_box=rb,
         anim={k: dict(kind='rise', delay=300, dur=500) for k in res_keys})
    # 정리: 찾은 기록이 질문 판 옆으로 모여듦. 질문 줄 → 기록에 번호 붙은 짧은 실.
    # 같은 대화방의 기록이 이어지면 카드 하나(앱 아이콘 하나) 아래 말풍선 두 개로 묶음
    gx = EX + EW + 70
    gy = QY
    sum_keys, sth = [], []
    prev = None
    for h in H:
        n, k = h['n'], h['target']
        c = dict(REC[k])
        merge = (prev is not None and c['kind'] == 'talk' and REC[prev['k']]['kind'] == 'talk'
                 and c['title'] == REC[prev['k']]['title'])
        y_ = (prev['box'][1] + prev['box'][3] - 14) if merge else gy
        dx, dy = gx - c['x'], y_ - c['y']
        c2 = dict(c, x=gx, y=y_)
        _, h2, _ = card_prims(k, c2['kind'], gx, y_, c2['w'], c2['title'], c2.get('meta', ''), c2.get('lines', ()), img=c2.get('img'),
                              icon=c2.get('icon'), img_h=c2.get('img_h'), link=c2.get('link'))
        if merge:     # 앞 카드 바탕을 이 말풍선까지 늘리고, 이 카드의 바탕·아이콘·이름은 빼고 날짜는 말풍선 위 작은 글로
            pk = prev['k']
            top = prev['box'][1]
            bh = y_ + h2 - top
            pw_ = max(prev['box'][2], c2['w'])

            def fn_prev(style=None, pc=dict(REC[pk], x=gx, y=top), bh=bh, pw_=pw_, pk=pk):
                pr = card_prims(pk, pc['kind'], pc['x'], pc['y'], pc['w'], pc['title'], pc.get('meta', ''), pc.get('lines', ()),
                                img=pc.get('img'), icon=pc.get('icon'), style='weave', img_h=pc.get('img_h'), link=pc.get('link'))[0]
                return [(p[0], p[1], p[2], p[3], pw_, bh, p[6]) if p[1] == pk + '/bg' else p for p in pr]
            sc.put('sum.' + pk, fn_prev)

        def fn(style=None, c2=c2, k=k, merge=merge):
            pr = card_prims(k, c2['kind'], c2['x'], c2['y'], c2['w'], c2['title'], c2.get('meta', ''), c2.get('lines', ()),
                            img=c2.get('img'), icon=c2.get('icon'), style='weave', img_h=c2.get('img_h'), link=c2.get('link'))[0]
            if merge:
                pr = [p for p in pr if p[1] not in (k + '/bg', k + '/ic', k + '/title')]
            return pr
        sc.put('sum.' + k, fn)
        if merge:
            sc.box['sum.' + k] = (gx, y_ + 14, c2['w'], h2 - 14)
        sum_keys.append('sum.' + k)
        for mk in ('hm%d' % n, 'im%d' % n):
            if mk in sc.items:
                prims = [(p[0], p[1], p[2] + dx, p[3] + dy, p[4], p[5], p[6]) for p in sc.items[mk](None)]
                sc.put('sum.' + mk, prims)
                sum_keys.append('sum.' + mk)
        tb = sc.box['sum.' + k]
        p0 = (EX + EW + 2, sc.row_y(n) + 10)
        p1 = (tb[0] - 2, tb[1] + min(tb[3] / 2, 34))
        pts = scurve(p0, p1, 0.5)
        mx = (p0[0] + p1[0]) / 2
        my = (p0[1] + p1[1]) / 2
        sc.put('sth%d' % n, S.thread_prims('sth%d' % n, pts) +
               [R('sth%d/n' % n, mx - 11, my - 11, 22, 22, prst='ellipse', fill='DCD3FF', line='FFFFFF', line_w=1.4),
                T('sth%d/nt' % n, mx - 11, my - 11, 22, 22, str(n), size=9, color=PURPLE, weight='b', align='c', anchor='ctr')])
        sth.append('sth%d' % n)
        full = (gx, y_, c2['w'], h2)
        prev = dict(k=k, box=(gx, (prev['box'][1] if merge else y_), max(c2['w'], prev['box'][2]) if merge else c2['w'],
                              (y_ + h2 - prev['box'][1]) if merge else h2))
        gy = full[1] + full[3] + 18
    hide(*phone_now, *res_keys)
    show(*qkeys, *sum_keys, *sth, *['tok%d@q' % h['n'] for h in H], 'qans.ok')
    hide('qans.slot')
    for i in range(1, nh + 1):
        styles['q%d' % i] = 'done' + ('_rw' if i > 1 else '')
    toks = ['tok%d@q' % h['n'] for h in H]
    sum_cap = dict(t=CP['sum'], pill=CP.get('sum_pill', '모두 기기 안에서'))
    shot('sum', ['qp'] + sum_keys, 'top', set(['qp', 'qorig', 'qans', 'qans.ok'] + qrows + toks + sum_keys + sth),
         dict(all=True), 1.45, cap=sum_cap,
         anim=dict({x: dict(kind='wipe_in', dir='left', delay=900 + 500 * j, dur=500) for j, x in enumerate(sth)},
                   **{'qans.ok': dict(kind='zoom_in', delay=1900, dur=300)}), morph=1800)
    if IXD:       # 00판: 위 띠는 00~04. 00 다음 장부터는 00에 ✓
        after = False
        for st in sc.steps:
            h_ = dict(st.hud or {})
            h_['stages'] = STAGES0
            if st.key in ('idx1', 'idx2'):
                h_['cur'] = '00'
                after = True
            elif after:
                h_['done'] = set(h_.get('done', ())) | {'00'}
            st.hud = h_
    skip = set(spec.get('skip', ()))         # 덱용 판: 화면 경험(예: 결과 화면)은 앞 장표가 보여 주므로 뺄 수 있음
    sc.steps = [st for st in sc.steps if st.key not in skip]
    return sc
