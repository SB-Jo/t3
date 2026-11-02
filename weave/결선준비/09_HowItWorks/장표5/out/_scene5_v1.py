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


def bar_layout():
    widths = [24 + 8 + tw(ko, 10.5, 'b') + 22 for _, ko in STAGES]
    gap = 30
    total = sum(widths) + gap * (len(STAGES) - 1)
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
    lay = bar_layout()
    x0, x1 = lay[0][0], lay[-1][0] + lay[-1][1]
    out.append(R('top/bar', x0 - 12, y0, x1 - x0 + 24, hh, prst='roundRect', fill='FFFFFF', alpha=94, line=LINE,
                 shadow=S.L.SHADOW_SOFT))
    cur, done = h.get('cur'), h.get('done', set())
    if cur:
        i = [s for s, _ in STAGES].index(cur)
        x, w = lay[i]
        out.append(R('top/hl', x - 4, y0 + 4, w + 8, hh - 8, prst='roundRect', fill=LAV, line=RING, line_w=1.6, glow=(8, RING, 30)))
    for i, ((no, ko), (x, w)) in enumerate(zip(STAGES, lay)):
        state = 'cur' if no == cur else ('done' if (no in done or h.get('all')) else 'todo')
        bf, bt, lc, lw = {'cur': (PURPLE, 'FFFFFF', INK, 'b'), 'done': ('DCD3FF', PURPLE, PURPLE, 'b'),
                          'todo': ('F1EEF8', 'C3BDD2', 'BDB7CC', 'sb')}[state]
        cy = y0 + hh / 2
        out.append(R('top/b%s' % no, x + 8, cy - 11, 22, 22, prst='ellipse', fill=bf, line=None))
        out.append(T('top/bn%s' % no, x + 8, cy - 11, 22, 22, '✓' if state == 'done' else no, size=8, color=bt, weight='b',
                     align='c', anchor='ctr'))
        out.append(T('top/l%s' % no, x + 36, y0, w - 34, hh, ko, size=10.5, color=lc, weight=lw, anchor='ctr'))
        if i < len(STAGES) - 1:
            out.append(T('top/a%d' % i, x + w + 4, y0, 22, hh, '→', size=10, color='C9C0E8', align='c', anchor='ctr'))
    if h.get('loop'):
        (x2, w2), (x3, w3) = lay[1], lay[2]
        a, b = (x3 + w3 / 2, y0 + hh - 1), (x2 + w2 / 2, y0 + hh - 1)
        on = h.get('loop_on')
        col = PURPLE if on else '9A90C8'
        out.append(C('top/loop', [a, (a[0], y0 + hh + 26), (b[0], y0 + hh + 26), b], w=2.4 if on else 1.8, color=col))
        out.append(T('top/loop_head', b[0] - 7, y0 + hh - 2, 14, 12, '▲', size=7.5, color=col, align='c', anchor='ctr'))
        lab = '찾은 단서로 다시 쓰기' if on else '반복'
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
            return [R('ui.sheet/bg', x + 6, sy, w - 12, bot - sy, prst='roundRect', radius=22, fill='FFFFFF', line=LINE2,
                      line_w=1.2, shadow=S.L.SHADOW_LIFT),
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
    rows = a.get('src_rows', [])
    ml = wrap(a['main'], 13.5, w - 64, 'b') if '\n' not in a['main'] else a['main'].split('\n')
    for ln in ml:
        if tw(ln, 13.5, 'b') > w - 60:
            print('   ! 건네기 카드 글이 넘침: %s (%.0f > %.0f)' % (ln, tw(ln, 13.5, 'b'), w - 60))
    ch = 40 + 22 * len(ml) + 10 + 24 * len(rows) + 8 + 36 + 14 + (34 if a.get('attach') else 0)
    ay = (sc.ui['sheet_y'] + 112) if kind == 'sheet' else ky - ch - 12
    sc.ui['ans_overlaps_msg'] = kind != 'sheet' and ay < msg_end + 6
    card = [R('ans/bg', x + 14, ay, w - 28, ch, prst='roundRect', radius=16, fill='FFFFFF', line=RING, line_w=1.8,
              shadow=S.L.SHADOW_LIFT, glow=(9, RING, 24)),
            P('ans/ic', S.ICON['spool'], x + 28, ay + 13, 18, 18),
            T('ans/lab', x + 52, ay + 11, 220, 22, a.get('label', '찾은 답'), size=9.5, color=PURPLE2, weight='b', anchor='ctr'),
            T('ans/main', x + 28, ay + 40, w - 56, 22 * len(ml), ml, size=13.5, color=INK, weight='b', lnspc=17)]
    ry = ay + 40 + 22 * len(ml) + 10
    for i, (ic, txt) in enumerate(rows):
        card += [P('ans/si%d' % i, S.ICON[ic], x + 28, ry + 4, 16, 16),
                 T('ans/st%d' % i, x + 50, ry, w - 80, 24, txt, size=fit_pt(txt, w - 82, 9, 'r', 7.5), color=SUB, anchor='ctr')]
        ry += 24
    if a.get('attach'):
        card += [R('ans/att', x + 28, ry + 2, w - 56, 28, prst='roundRect', fill='F7F5FC', line=LINE2, line_w=1.0),
                 R('ans/att_d', x + 38, ry + 9, 11, 14, prst='rect', fill='FFFFFF', line=PURPLE2, line_w=1.2),
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
                    R('res/file_d', fx + 12, fy + 9, 12, 16, prst='rect', fill='FFFFFF', line=PURPLE2, line_w=1.2),
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
    PHH = 112 + nh * ROW_H + 44
    sc.QPH = PHH
    sc.RE_Y = QY + PHH + 22
    sc.put('qp', [R('qp/bg', EX, QY, EW, PHH, prst='roundRect', radius=16, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=S.L.SHADOW_CARD)])
    hx = EX + 42 + tw('Query Rewriting', 12.5, 'b') + 8
    sc.put('qp.head', [P('qp.head/ic', S.ICON['spool'], EX + 16, QY + 14, 20, 20),
                       T('qp.head/title', EX + 42, QY + 12, 220, 24, 'Query Rewriting', size=12.5, color=PURPLE, weight='b', anchor='ctr'),
                       T('qp.head/ko', hx, QY + 12, 120, 24, '질문 다시 쓰기', size=9, color=MUTE, weight='sb', anchor='ctr')])
    ol = wrap('“%s”' % sp['ask'], 10.5, EW - 34, 'm')[:2]
    sc.put('qorig', [T('qorig/l', EX + 16, QY + 46, 220, 16, sp.get('ask_label', '처음 질문'), size=8.5, color=MUTE, weight='b', anchor='ctr'),
                     T('qorig/t', EX + 16, QY + 64, EW - 30, 19 * len(ol), ol, size=10.5, color=INK, weight='m', lnspc=14)])
    X0 = EX + 46
    QW = EW - 46 - 16
    sc.X0 = X0

    def row_y(i):
        return QY + 112 + (i - 1) * ROW_H

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


# ------------------------------------------------------------------ 흩어진 기록 더미
REGION = (876, 92, 1776, 704)    # 기록이 떠 있는 자리(세계)


def _overlap(a, b, mx=0, my=0):
    return a[0] < b[0] + b[2] + mx and b[0] < a[0] + a[2] + mx and a[1] < b[1] + b[3] + my and b[1] < a[1] + a[3] + my


def _gap(a, b):
    dx = max(0, max(a[0], b[0]) - min(a[0] + a[2], b[0] + b[2]))
    dy = max(0, max(a[1], b[1]) - min(a[1] + a[3], b[1] + b[3]))
    return (dx * dx + (dy * 1.6) ** 2) ** 0.5


def place_fills(sc, spec):
    """작은 조각을 기록 사이사이에 흩뿌림(후보 여럿 중 가장 비어 있는 자리, 씨앗 고정 → 격자처럼 줄 맞지 않음)."""
    import random
    rnd = random.Random(spec.get('seed', 11))
    x0, y0, x1, y1 = spec.get('region', REGION)
    taken = [sc.box[k] for k in spec['records']]
    keys = []
    for i, (ic, title, meta) in enumerate(spec.get('fill', [])):
        w, h = S.frag_w(title, meta), S.FRAG_H
        best, best_d = None, -1
        for _ in range(90):
            b = (rnd.uniform(x0, x1 - w), rnd.uniform(y0, y1 - h), w, h)
            if any(_overlap(b, t, 18, 12) for t in taken):
                continue
            d = min(_gap(b, t) for t in taken)
            if d > best_d:
                best, best_d = b, d
        if best is None:
            print('   ! 조각 %s 자리 없음' % title)
            continue
        key = 'f%d' % i
        sc.card(key, dict(kind='frag', icon=ic, x=round(best[0]), y=round(best[1]), title=title, meta=meta))
        taken.append(sc.box[key])
        keys.append(key)
    return keys


# ------------------------------------------------------------------ 일반 검색 판(실패): 키워드 검색 / 임베딩 검색 / 둘을 합친 일반 검색
def search_panel(name, y, title, pill, query, words, bars):
    """제목 + 회색 알약 + 검색어(키워드엔 형광펜) + (임베딩이면 숫자 막대). 돌려줌: (원시 목록, 실이 나가는 점, 높이)."""
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
    for i, ln in enumerate(ql):
        out.append(T(name + '/q%d' % i, qx + 12, qy + 7 + 20 * i, inner - 20, 20, ln, size=10.5, color=INK, weight='m'))
    if bars:
        by_ = qy + qh + 10
        out += bars_prims(name + '/bar', EX + EW - 16 - BAR_W, by_, 'B9B3C8', query)
        out.append(T(name + '/bar_l', EX + 16, by_, 200, 24, '뜻을 숫자로 바꿔 비교', size=9, color=MUTE, weight='sb', anchor='ctr'))
        port = (EX + EW - 14, by_ + 13)
    else:
        port = (EX + EW - 2, qy + qh / 2)
    return out, port, h


# ------------------------------------------------------------------ 시나리오 → 장면
def build(spec):
    sc = Scene(spec)
    for k, c in spec['records'].items():
        sc.card(k, c)
    keys = list(spec['records'])
    fills = place_fills(sc, spec)
    recs = keys + fills
    hops = spec['hops']
    nh = len(hops)
    phone_items(sc)
    engine_items(sc)
    CP, NT = spec['cap'], spec['notes']
    kind = spec['type']
    owner = sc.owner

    def tag_at(key, label, style='gray', where='tr', pt=9.5, name=None):
        """카드 위쪽 모서리에 붙는 태그(카드 제목·날짜와 겹치지 않게 위로 비켜 둠)."""
        bx, by, bw, bh = sc.box[key]
        w = tw(label, pt, 'sb') + (22 if pt <= 10 else 26)
        x = bx + bw - w - 8 if where in ('tr', 'br') else bx + 10
        y = by - 20 if where in ('tr', 'tl') else by + bh - 4
        hh = 24 if pt <= 10 else 30
        y = y - (hh - 24) if where in ('tr', 'tl') else y
        return chip_prims(name, x, y, label, style=style, pt=pt, h=hh, padx=11 if pt <= 10 else 13, weight='sb')[0]

    def marks_of(k, marks, name, fill=HL, alpha=34):
        rects = [band(sc.pos[k][where], sub, kind='full') for where, sub in marks]
        sc.put(name, [R('%s/%d' % (name, i), *r, prst='roundRect', radius=2.5, fill=fill, alpha=alpha, line=None)
                      for i, r in enumerate(rects)], owner=k)
        return rects

    def thread_to(p0, box, avoid=()):
        """실은 카드 밑으로 지나가므로 대개 가려짐. 다만 옅게 그리는 카드(답이 있는 기록·후보)는 비쳐 보이니 그 위는 피함."""
        pts = route_elbow(p0, box)
        ty = box[1] + min(box[3] / 2, 34)
        for k_ in avoid:
            b_ = sc.box[k_]
            if b_ != box and b_[1] - 8 < ty < b_[1] + b_[3] + 8 and GX < b_[0] < box[0]:
                print('   ! 실이 옅은 %s 카드 위를 지나감' % k_)
        return pts

    # -------------------------------------------------------------- 실패: 일반 검색이 찾는 방법과 못 찾는 까닭
    F = spec['fail']
    mode = F.get('mode', 'brief')
    PANEL_Y = F.get('panel_y', 236)
    passes = []      # (장 키, 판 키, 맞은 기록, 실, 순위 알약, 태그, 형광펜)
    if mode == 'brief':
        plan = [('fail', 'gen', '일반 검색', '키워드 + 임베딩', F['words'], True, F['hits'])]
    else:
        plan = [('fail_kw', 'kw', '키워드 검색', 'BM25', F['words'], False, F['kw']),
                ('fail_emb', 'emb', '임베딩 검색', '비슷한 뜻', [], True, F['emb'])]
    for skey, pk, title, pill, words, bars, hit in plan:
        prims, port, _ = search_panel(pk, PANEL_Y, title, pill, F['query'], words, bars)
        sc.put(pk, prims)
        ths, rks, tgs, mks = [], [], [], []
        for i, k in enumerate(hit['ranks']):
            bx, by, bw, bh = sc.box[k]
            lab = '%d위' % (i + 1)
            rw_ = tw(lab, 9.5, 'b') + 18
            rk = '%s.rank%d' % (pk, i + 1)
            sc.put(rk, [R('rank%d/c' % (i + 1), bx - 10, by - 13, rw_, 24, prst='roundRect', fill='8E88A0', line='FFFFFF', line_w=1.4),
                        T('rank%d/t' % (i + 1), bx - 10, by - 13, rw_, 24, lab, size=9.5, color='FFFFFF', weight='b', align='c',
                          anchor='ctr')])
            rks.append(rk)
            th = '%s.th%d' % (pk, i + 1)
            sc.put(th, [C(th + '/l', thread_to(port, sc.box[k], avoid=[F['miss']['key']] if pk != 'kw' else []), w=1.8,
                          color='B9B3C8')])
            ths.append(th)
            if hit.get('tags', {}).get(k):
                tg = '%s.tag.%s' % (pk, k)
                sc.put(tg, tag_at(k, hit['tags'][k], name=tg, pt=11), owner=k)
                tgs.append(tg)
            if hit.get('marks', {}).get(k):
                mk = '%s.mk.%s' % (pk, k)
                marks_of(k, hit['marks'][k], mk, alpha=30)
                mks.append(mk)
        passes.append((skey, pk, list(hit['ranks']), ths, rks, tgs, mks))
    # 답이 있는 기록: 옅게 + 점선 테두리 + '?' + 짧은 태그(질문과 닮지 않음)
    M = F['miss']
    mb = sc.box[M['key']]
    mt = M['tag']
    mtw = tw(mt, 11, 'sb') + 26
    mx_ = mb[0] + mb[2] / 2 - mtw / 2
    sc.put('miss', [R('miss/r', mb[0] - 8, mb[1] - 8, mb[2] + 16, mb[3] + 16, prst='roundRect', radius=16, fill=None, line=GRAY_LINE,
                      line_w=1.8, dash='dash'),
                    R('miss/q', mb[0] - 22, mb[1] - 22, 34, 34, prst='ellipse', fill='FFFFFF', line=GRAY_LINE, line_w=1.4),
                    T('miss/qt', mb[0] - 22, mb[1] - 22, 34, 34, '?', size=15, color=MUTE, weight='b', align='c', anchor='ctr'),
                    R('miss/tag', mx_, mb[1] + mb[3] + 14, mtw, 30, prst='roundRect', fill='EFECF4', line=None),
                    T('miss/tag_t', mx_, mb[1] + mb[3] + 14, mtw, 30, mt, size=11, color=SUB, weight='sb', align='c', anchor='ctr')])

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
                sc.put('drop%d.%s' % (n, k), tag_at(k, lab2, style='grayfill', name='drop%d.%s' % (n, k)))
            for k, marks in f.get('marks', {}).items():
                marks_of(k, marks, 'fm%d.%s' % (n, k), alpha=30)
            h['fbox'] = sc.box['fb%d' % n]
        k = hop['target']
        tb = sc.box[k]
        sc.put('th%d' % n, S.thread_prims('th%d' % n, thread_to(sc.re_pt, tb, avoid=list(hop.get('cands', {})))))
        # 후보(가까운 기록 몇 개): 옅은 실 + 이유 태그(찾기 장에서)
        h['cands'] = list(hop.get('cands', {}))
        for ck, lab2 in hop.get('cands', {}).items():
            cb = sc.box[ck]
            sc.put('thc%d.%s' % (n, ck), [C('thc%d.%s/l' % (n, ck), thread_to(sc.re_pt, cb), w=1.6, color='C9BFF0', dash='sysDash')])
            sc.put('why%d.%s' % (n, ck), tag_at(ck, lab2, style='grayfill', where=hop.get('why_at', {}).get(ck, 'tr'),
                                                 name='why%d.%s' % (n, ck), pt=10.5))
        if hop.get('marks'):
            h['mark0'] = marks_of(k, hop['marks'], 'hm%d' % n)[0]
        for pk_, (plab, pst) in hop.get('pills', {}).items():
            ix, iy, iw, ih = sc.pos[pk_]['img']
            pw = tw(plab, 9, 'b') + 22
            px0, py0 = ix + iw / 2 - pw / 2, iy + ih - 32
            sc.put('pl%d.%s' % (n, pk_), [R('pl%d.%s/bg' % (n, pk_), px0, py0, pw, 24, prst='roundRect', fill='FFFFFF', alpha=95,
                                            line=PURPLE if pst == 'weave' else GRAY_LINE, line_w=1.2),
                                          T('pl%d.%s/t' % (n, pk_), px0, py0, pw, 24, plab, size=9,
                                            color=PURPLE if pst == 'weave' else BODY, weight='b', align='c', anchor='ctr')],
                   owner=pk_)
            sc.pos['pl%d.%s' % (n, pk_)] = (px0 + 11, py0 + 12 - 9 * 4 / 3 / 2 - 1, plab, 9, 'b')
        if hop.get('img_marks'):
            from PIL import Image
            for ik, rects_px in hop['img_marks'].items():
                ix, iy, iw, ih = sc.pos[ik]['img']
                IW, IH = Image.open(S.AS / spec['records'][ik]['img']).size
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
            if okx + 44 > EX + EW - 10:       # 답이 길면 '멈춤'은 답 아래 줄로
                sc.put('qans.ok', chip_prims('qans.ok', sc.X0, sc.ans_y + 28, '멈춤', style='soft', pt=9, h=21, padx=8)[0])
            else:
                sc.put('qans.ok', chip_prims('qans.ok', okx, sc.ans_y + 1, '멈춤', style='soft', pt=9, h=21, padx=8)[0])
        else:
            sc.put('tok%d@q' % n, chip_prims('tok%d' % n, sc.X0, sc.row_y(n + 1) - 1, lab, style='fill', pt=10, h=23, padx=9)[0])
        H.append(h)

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
        """실은 카드 밑으로(다른 카드를 지나가도 카드에 가려짐)."""
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
    # 2 기록 더미: 넓게. 여기저기 흩어진 기록이 하나씩 떠오름(옅게)
    show(*recs)
    import random
    order = list(recs)
    random.Random(spec.get('seed', 11) + 1).shuffle(order)
    shot('cloud', recs, 'top', set(recs), {}, 0.95, morph=1700, alpha={k: 62 for k in recs},
         anim={k: dict(kind='zoom_in', delay=120 + 45 * j, dur=380) for j, k in enumerate(order)})
    # 3 실패: 일반 검색이 찾는 방법(키워드는 같은 단어, 임베딩은 비슷한 뜻) → 답이 있는 기록엔 닿지 못함
    prev = []
    for j, (skey, pk, hk, ths, rks, tgs, mks) in enumerate(passes):
        hide(*prev)
        for x in list(styles):
            if x in recs:
                styles.pop(x)
        styles.update({k: 'gray' for k in hk})
        last_pass = j == len(passes) - 1
        extra = ['miss'] if last_pass else []
        show_under(*ths)
        show(pk, *rks, *tgs, *mks, *extra)
        foc = set([pk] + hk + ths + rks + tgs + mks + extra)
        fb = union([sc.box[x] for x in [pk] + hk + extra])
        al = {M['key']: 42} if last_pass else {}
        if last_pass:
            foc.add(M['key'])
        shot(skey, [], 'top', foc, {}, 1.4, frame_box=fb, cap_x=F.get('cap_x'), alpha=al, morph=1600,
             anim=dict({pk: dict(kind='rise', delay=0, dur=420)},
                       **{t_: dict(kind='wipe_in', dir='left', delay=450 + 160 * i, dur=420) for i, t_ in enumerate(ths)},
                       **{m_: dict(kind='wipe_in', dir='left', delay=650 + 160 * i, dur=380) for i, m_ in enumerate(mks)},
                       **{r_: dict(kind='zoom_in', delay=700 + 160 * i, dur=260) for i, r_ in enumerate(rks)},
                       **{t_: dict(kind='zoom_in', delay=1150 + 160 * i, dur=280) for i, t_ in enumerate(tgs)},
                       **({'miss': dict(kind='fade_in', delay=1700, dur=500)} if last_pass else {})))
        prev = [pk] + ths + rks + tgs + mks + extra
    hide(*prev)
    for x in list(styles):
        if x in recs:
            styles.pop(x)
    # 4 01 순간 감지
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
            # 02 다시 쓰기(Query Rewriting): 앞 기록의 단서 칩이 다음 질문의 빈칸으로 날아감(판을 가까이)
            pk_prev = H[n - 2]
            hide('tok%d@src' % (n - 1), *['pl%d.%s' % (n - 1, x) for x in hops[n - 2].get('pills', {})], 'pm%d' % (n - 1),
                 'im%d' % (n - 1), 'hm%d' % (n - 1))
            styles.pop(pk_prev['target'], None)
            show('tok%d@q' % (n - 1))
            styles['q%d' % (n - 1)] = 'done' + ('_rw' if n > 2 else '')
            styles['q%d' % n] = 'cur_rw'
            if re_cur:
                hide(re_cur)
                re_cur = None
            shot('rw%d' % n, ['qp'], 'right', (set(qkeys) - {'qorig', 'q%d' % (n - 1)}) | {'tok%d@q' % (n - 1)},
                 dict(cur='02', done=D('01', '03'), loop=n - 1, loop_on=True), 1.9, cap=hc['rw'], notes=hn['rw'], morph=1800,
                 half=['qorig', 'q%d' % (n - 1)], anim={'q%d' % n: dict(kind='pulse', delay=900, dur=450, scale=1.04)})
            hide('tok%d@q' % (n - 1))
        if re_cur != k_re:
            if re_cur:
                hide(re_cur)
            show(k_re)
            re_cur = k_re
        hop_box = union([sc.box[x] for x in [k_re, k] + cands + (list(f.get('drop', {})) if f else [])] +
                        ([sc.box['fb%d' % n]] if f else []))
        if f:
            drops = ['drop%d.%s' % (n, x) for x in f.get('drop', {})]
            fms = ['fm%d.%s' % (n, x) for x in f.get('marks', {})]
            show('fb%d' % n, *drops, *fms)
            focus = set(list(f['keep']) + list(f.get('drop', {})) + ['fb%d' % n, k_re] + drops)
            shot('filter%d' % n, [], 'top', focus, hud3, 1.45, cap=hc['filter'], notes=hn['filter'], frame_box=hop_box,
                 cap_x=cx_of('fb%d' % n), morph=1700,
                 anim=dict({'fb%d' % n: dict(kind='fade_in', delay=300, dur=500)},
                           **{x: dict(kind='zoom_in', delay=850 + 150 * j, dur=300) for j, x in enumerate(drops)},
                           **{x: dict(kind='wipe_in', dir='left', delay=800, dur=400) for x in fms}))
            hide(*drops, *fms)
        # 03 찾기: 판 → 실 → 기록. 가까운 후보는 옅은 실 + 이유 태그
        whys = ['why%d.%s' % (n, c) for c in cands]
        show_under('th%d' % n, *['thc%d.%s' % (n, c) for c in cands])
        show(*whys)
        styles[k] = 'weave'
        focus = set([k_re, k, 'th%d' % n] + whys)
        shot('find%d' % n, [], 'top', focus, hud3, 1.3, cap=hc['find'], notes=hn['find'], frame_box=hop_box, cap_x=cx_of(k),
             morph=1700 if n == 1 else 1500,
             anim=dict({'th%d' % n: dict(kind='wipe_in', dir='left', delay=500, dur=700)},
                       **{'thc%d.%s' % (n, c): dict(kind='wipe_in', dir='left', delay=100 + 150 * j, dur=500) for j, c in enumerate(cands)},
                       **{w_: dict(kind='zoom_in', delay=1300 + 150 * j, dur=300) for j, w_ in enumerate(whys)}),
             half=cands + ['thc%d.%s' % (n, c) for c in cands] + (list(f['keep']) + ['fb%d' % n] if f else []))
        hide('th%d' % n, *['thc%d.%s' % (n, c) for c in cands], 'fb%d' % n, *whys)
        # 가까이: 기록 하나만 크게. 근거에 형광펜 → 단서 칩
        pills = ['pl%d.%s' % (n, x) for x in hop.get('pills', {})]
        extra = [x for x in ('hm%d' % n, 'im%d' % n, 'pm%d' % n) if x in sc.items]
        show(*pills, *extra, 'tok%d@src' % n)
        focus = set([k, 'tok%d@src' % n] + extra + pills)
        shot('close%d' % n, [k, 'tok%d@src' % n], hop.get('cside', 'right'), focus, hud3, hop.get('zclose', 2.8), cap=hc['close'],
             notes=hn['close'], pad=20, cap_y=cy_of(k), morph=1600, alpha={x: 0 for x in recs if x != k},
             anim=dict({'hm%d' % n: dict(kind='wipe_in', dir='left', delay=300, dur=500),
                        'im%d' % n: dict(kind='wipe_in', dir='left', delay=300, dur=500),
                        'pm%d' % n: dict(kind='wipe_in', dir='left', delay=400, dur=500),
                        'tok%d@src' % n: dict(kind='zoom_in', delay=1100, dur=350)},
                       **{x: dict(kind='zoom_in', delay=150 + 150 * j, dur=300) for j, x in enumerate(pills)}))
    # 04 전달: 카드를 가까이. 카드가 열리면 빨간 배지는 사라지고, 자판은 내려감
    last_h = H[-1]
    hide('tok%d@src' % nh, re_cur, *['pl%d.%s' % (nh, x) for x in hops[-1].get('pills', {})], 'pm%d' % nh, 'im%d' % nh, 'hm%d' % nh,
         *qkeys)
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
    # 정리: 찾은 기록이 질문 판 옆으로 모여듦(같은 이름이라 모핑으로 날아옴). 질문 줄 → 기록에 번호 붙은 짧은 실
    targets = [h['target'] for h in H]
    gx = EX + EW + 70
    gy = QY
    sum_keys, sth = [], []
    for h in H:
        n, k = h['n'], h['target']
        c = dict(spec['records'][k])
        dx, dy = gx - c['x'], gy - c['y']
        c2 = dict(c, x=gx, y=gy)

        def fn(style=None, c2=c2, k=k):
            return card_prims(k, c2['kind'], c2['x'], c2['y'], c2['w'], c2['title'], c2.get('meta', ''), c2.get('lines', ()),
                              img=c2.get('img'), icon=c2.get('icon'), style='weave', img_h=c2.get('img_h'), link=c2.get('link'))[0]
        sc.put('sum.' + k, fn)
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
        gy = tb[1] + tb[3] + 18
    hide(*targets)
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
    return sc
