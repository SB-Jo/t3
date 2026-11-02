"""v4 장면 틀 — 시나리오 하나(SPEC) → 모핑으로 이어지는 장면 19~22장 (2026-11-01, 4차 피드백).

v3에서 바꾼 것
- 카메라를 크게 당기고 뺀다. 넓게(0.75배 안팎) → 중간(1.2~1.4배) → 가까이(2~2.6배)를 오가며, 한 장에 한 가지만 크게 보인다.
- 설명은 초점 바로 옆에 붙인다(간격 34px). 카메라는 '초점 + 설명'을 한 덩어리로 보고 화면 가운데에 놓는다.
- 설명은 제목 한두 줄만. 뱃지·부제는 없애고 자세한 말은 발표자 노트로.
- 파이프라인은 01 순간 감지 → 02 질문 다시 쓰기 → 03 연쇄 탐색 → 04 전달. '00 사전 준비'(데이터 전처리)는 뺐다.
- 세계 배치: 왼쪽 폰 / 가운데 엔진(검색창·일반 임베딩 → 질문 다시 쓰기·Reasoning Embedding) / 오른쪽 기록.
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
        col = PURPLE if on else 'C9C0E8'
        out.append(C('top/loop', [a, (a[0], y0 + hh + 24), (b[0], y0 + hh + 24), b], w=2.2 if on else 1.5, color=col))
        out.append(T('top/loop_head', b[0] - 7, y0 + hh - 2, 14, 12, '▲', size=7, color=col, align='c', anchor='ctr'))
        lab = '찾은 단서로 다시 쓰기' if on else '반복'
        lw_ = tw(lab, 8.5, 'b') + 16
        out.append(R('top/loop_bg', (a[0] + b[0]) / 2 - lw_ / 2, y0 + hh + 12, lw_, 18, prst='roundRect', fill='FFFFFF', line=None))
        out.append(T('top/loop_t', (a[0] + b[0]) / 2 - lw_ / 2, y0 + hh + 12, lw_, 18, lab, size=8.5, color=col, weight='b',
                     align='c', anchor='ctr'))
        out.append(R('top/cnt', x3 + w3 - 14, y0 - 6, 20, 20, prst='ellipse', fill=PURPLE, line='FFFFFF', line_w=1.5))
        out.append(T('top/cnt_t', x3 + w3 - 14, y0 - 6, 20, 20, str(h['loop']), size=8.5, color='FFFFFF', weight='b', align='c',
                     anchor='ctr'))
    return out


# ------------------------------------------------------------------ 설명 + 카메라
def cap_measure(cap, side):
    """cap = dict(t=[(글자, 색)], s='부제'). 돌려줌: (제목 줄, 부제 줄, 폭, 높이)."""
    maxw = CAP_W if side in ('left', 'right') else 820
    tl = wrap_runs(cap['t'], CAP_PT, maxw)
    sl = wrap(cap['s'], SUB_PT, maxw, 'r') if cap.get('s') else []
    w = max([line_w(ln, CAP_PT) for ln in tl] + [tw(s, SUB_PT) for s in sl]) + 6
    h = len(tl) * CAP_LH + (8 + len(sl) * SUB_LH if sl else 0)
    return tl, sl, w, h


def frame(box, side, zmax, cw, ch, pad=16):
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
        def fn(style=None, c=c, key=key):
            return card_prims(key, c['kind'], c['x'], c['y'], c['w'], c['title'], c.get('meta', ''), c.get('lines', ()),
                              img=c.get('img'), icon=c.get('icon'), style=style or 'base', img_h=c.get('img_h'))[0]
        _, h, pos = card_prims(key, c['kind'], c['x'], c['y'], c['w'], c['title'], c.get('meta', ''), c.get('lines', ()),
                               img=c.get('img'), icon=c.get('icon'), img_h=c.get('img_h'))
        c['h'] = h
        self.pos[key] = pos
        self.put(key, fn)
        # 글이 카드 폭을 넘는지(대화 말풍선은 안쪽 여백 18 더)
        avail = c['w'] - (12 + 22 + 9) - 12 - (18 if c['kind'] == 'talk' else 0)
        for t in c.get('lines', ()):
            if tw(t, 9.5) > avail:
                print('   ! 카드 %s 글이 넘침: %s (%.0f > %.0f)' % (key, t, tw(t, 9.5), avail))
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
    if kind == 'sheet':   # 키보드의 실타래 버튼으로 여는 기록 통합 검색
        sy = msg_end + 6
        sh = y + H - 10 - sy                  # 자판 자리까지 덮는 판
        sc.put('ui.sheet', [R('ui.sheet/bg', x + 6, sy, w - 12, sh, prst='roundRect', radius=22, fill='FFFFFF', line=LINE2,
                              line_w=1.2, shadow=S.L.SHADOW_LIFT),
                            R('ui.sheet/handle', x + w / 2 - 22, sy + 9, 44, 4, prst='roundRect', fill='D9D4E6', line=None),
                            P('ui.sheet/sp', S.ICON['spool'], x + 22, sy + 24, 20, 20),
                            T('ui.sheet/title', x + 48, sy + 19, 220, 30, '기록 통합 검색', size=12, color=PURPLE, weight='b', anchor='ctr'),
                            R('ui.sheet/sb', x + 18, sy + 58, w - 36, 42, prst='roundRect', fill='F7F5FC', line=LINE2, line_w=1.0),
                            T('ui.sheet/sb_t', x + 30, sy + 58, w - 60, 42, ui['query'], size=fit_pt(ui['query'], w - 64, 10.5, 'r', 8.5),
                              color=INK, anchor='ctr')])
        sc.ui['sheet_y'] = sy
        sc.box['ui.sheet.top'] = (x + 6, sy, w - 12, 108)
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
    ch = 40 + 22 * len(ml) + 10 + 24 * len(rows) + 8 + 36 + 14
    ay = (sc.ui['sheet_y'] + 112) if kind == 'sheet' else ky - ch - 12
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


def qbox_prims(name, x, y, w, runs, pt=10, border=LINE2, fill='FFFFFF', mark=None, color=INK):
    """질문 상자(두 줄까지). mark = 칩처럼 칠할 글자. 돌려줌: (원시 목록, 칠한 자리 또는 None, 높이)."""
    tl = wrap_runs(runs, pt, w - 22, 'sb')[:2]
    lh = pt * 4 / 3 + 5
    h = 20 + lh * len(tl)
    ty = y + 10
    out = [R(name + '/bg', x, y, w, h, prst='roundRect', radius=10, fill=fill, line=border, line_w=1.0)]
    mrect = None
    if mark:
        for j, ln in enumerate(tl):
            txt = ''.join(t for t, _ in ln)
            if mark in txt:
                bx, by_, bw, bh = band((x + 11, ty + j * lh + 2, txt, pt, 'sb'), mark, kind='full')
                mrect = (bx - 3, by_ - 1, bw + 6, bh + 2)
                out.append(R(name + '/mk', *mrect, prst='roundRect', radius=5, fill='E6DEFF', line=None))
                break
    out.append(T(name + '/t', x + 11, ty, w - 14, lh * len(tl) + 2, [[(t, {'color': c}) for t, c in ln] for ln in tl],
                 size=pt, color=color, weight='sb', lnspc=lh * 0.75))
    return out, mrect, h


def runs_of(t, base=INK):
    return [(t, base)] if isinstance(t, str) else list(t)


def plain(t):
    return t if isinstance(t, str) else ''.join(x for x, _ in t)


def engine_block(name, y, title, label, runs, cond, style, mark=None):
    """일반 임베딩(style='gen') / Reasoning Embedding(style='re') 판: 제목, 넣는 질문, (필터), 숫자 막대.
    돌려줌: (원시 목록, 막대 오른쪽 끝 점, 필터 칩 자리 또는 None)."""
    re_ = style == 're'
    col_t, col_l = (PURPLE, PURPLE) if re_ else (SUB, MUTE)
    inner = EW - 32
    qb, mrect, qh = qbox_prims(name + '/q', EX + 16, y + 62, inner, runs, border=RING if re_ else GRAY_LINE,
                               fill='FFFFFF' if re_ else 'F6F5F8', mark=mark, color=INK if re_ else SUB)
    yy = y + 62 + qh + 12
    fc = None
    extra = []
    if cond:
        cpt = fit_pt(cond, inner - BAR_W - 70, 9.5)
        extra += [T(name + '/fl', EX + 16, yy, 40, 28, '필터', size=9, color=PURPLE2, weight='b', anchor='ctr')]
        pr, cw = chip_prims(name + '/fc', EX + 56, yy + 1, cond, style='dash', pt=cpt, h=26, padx=10)
        extra += pr
        fc = (EX + 56, yy + 1, cw, 26)
        if mrect:   # 질문 속 조건 → 필터 칸으로 내려가는 점선 갈래
            mx, my, mw, mh = mrect
            sx, sy = mx + mw / 2, my + mh
            ex_, ey_ = EX + 56 + cw / 2, yy + 1
            extra.append(C(name + '/split', [(sx, sy + 1), (sx, sy + (ey_ - sy) * 0.6), (ex_, ey_ - (ey_ - sy) * 0.6), (ex_, ey_ - 1)],
                           w=1.4, color=PURPLE2, dash='sysDash', tail='triangle'))
    by_ = yy + (1 if cond else 0)
    bars_x = EX + EW - 16 - BAR_W
    h = (yy + 28 + 14 - y) if cond else (yy + 26 + 12 - y)
    out = [R(name + '/bg', EX, y, EW, h, prst='roundRect', radius=16, fill='FFFFFF', line=RING if re_ else GRAY_LINE,
             line_w=1.6 if re_ else 1.2, shadow=S.L.SHADOW_CARD if re_ else S.L.SHADOW_SOFT, glow=(8, RING, 22) if re_ else None),
           T(name + '/title', EX + 16, y + 12, 300, 22, title, size=11.5, color=col_t, weight='b', anchor='ctr'),
           T(name + '/lab', EX + 16, y + 36, 300, 18, label, size=8.5, color=col_l, weight='b', anchor='ctr')]
    out += qb + extra
    out += bars_prims(name + '/bar', bars_x, by_ + 2, PURPLE2 if re_ else 'B9B3C8', plain(runs) + '|' + (cond or ''))
    return out, (EX + EW - 14, by_ + 13), fc, h


def engine_items(sc):
    sp = sc.spec
    hops = sp['hops']
    nh = len(hops)
    # 지금 쓰는 검색 1: 단어로 찾기
    W_ = sp['word']
    mode = '단어로 찾기'
    mw = tw(mode, 9.5, 'b') + 22
    aw = EW - mw - 60
    q = W_['query']
    sc.put('wbox', [R('wbox/bg', EX, 220, EW, 56, prst='roundRect', fill='FFFFFF', line=GRAY_LINE, line_w=1.2, shadow=S.L.SHADOW_CARD),
                    R('wbox/mode', EX + 10, 231, mw, 34, prst='roundRect', fill='EFECF4', line=None),
                    T('wbox/mode_t', EX + 10, 231, mw, 34, mode, size=9.5, color=SUB, weight='b', align='c', anchor='ctr'),
                    T('wbox/q', EX + mw + 22, 220, aw, 56, q, size=fit_pt(q, aw - 4, 12, 'm', 9.5), color=INK, weight='m', anchor='ctr'),
                    R('wbox/lens', EX + EW - 36, 239, 15, 15, prst='ellipse', fill=None, line=MUTE, line_w=2.0),
                    R('wbox/lens2', EX + EW - 23, 253, 8, 2.2, fill=MUTE, line=None)])
    # 지금 쓰는 검색 2: 일반 임베딩
    Sm = sp['sim']
    gi = Sm.get('input', sp['ask'])
    gen, gpt, _, gh = engine_block('gen', 220, '일반 임베딩', Sm.get('label', '처음 질문 그대로'), [(gi, SUB)], None, 'gen')
    sc.put('gen', gen)
    sc.gen_pt = gpt
    # 질문 다시 쓰기 판
    PHH = 112 + nh * ROW_H + 44
    sc.QPH = PHH
    sc.RE_Y = QY + PHH + 22
    sc.put('qp', [R('qp/bg', EX, QY, EW, PHH, prst='roundRect', radius=16, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=S.L.SHADOW_CARD),
                  P('qp/ic', S.ICON['spool'], EX + 16, QY + 14, 20, 20),
                  T('qp/title', EX + 42, QY + 12, 260, 24, '질문 다시 쓰기', size=12, color=PURPLE, weight='b', anchor='ctr')])
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
            out += [R('q%d/b' % i, EX + 16, y, 21, 21, prst='ellipse', fill=PURPLE if (cur or done) else 'ECE8F4', line=None),
                    T('q%d/bt' % i, EX + 16, y, 21, 21, '✓' if done else str(i), size=8.5, color='FFFFFF' if (cur or done) else MUTE,
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
    ay = row_y(nh + 1) - 2
    sc.ans_y = ay
    sc.put('qans', [T('qans/l', EX + 16, ay, 30, 23, '답', size=10.5, color=PURPLE, weight='b', anchor='ctr')])
    sc.put('qans.slot', chip_prims('qans/slot', X0, ay, ' ' * 24, style='dash', pt=10, h=23)[0])
    sc.groups['qp'] = ['qorig', 'qans', 'qans.slot', 'qans.ok'] + ['q%d' % i for i in range(1, nh + 1)] + \
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


# ------------------------------------------------------------------ 시나리오 → 장면
def build(spec):
    sc = Scene(spec)
    for k, c in spec['records'].items():
        sc.card(k, c)
    hops = spec['hops']
    nh = len(hops)
    phone_items(sc)
    engine_items(sc)
    recs = list(spec['records'])
    CP, NT = spec['cap'], spec['notes']
    kind = spec['type']
    owner = sc.owner
    obst = [sc.box[k] for k in recs]

    def tag_at(key, label, style='gray', where='tr', pt=9.5, name=None):
        bx, by, bw, bh = sc.box[key]
        w = tw(label, pt, 'sb') + 22
        x = bx + bw - w - 8 if where in ('tr', 'br') else bx + 10
        y = by - 12 if where in ('tr', 'tl') else by + bh - 12
        return chip_prims(name, x, y, label, style=style, pt=pt, h=24, padx=11, weight='sb')[0]

    def marks_of(k, marks, name, fill=HL, alpha=34):
        rects = [band(sc.pos[k][where], sub, kind='full') for where, sub in marks]
        sc.put(name, [R('%s/%d' % (name, i), *r, prst='roundRect', radius=2.5, fill=fill, alpha=alpha, line=None)
                      for i, r in enumerate(rects)], owner=k)
        return rects

    # 지금 쓰는 검색 1: 단어로 찾기
    W_ = spec['word']
    hits = list(W_['hits'])
    for k, marks in W_['hits'].items():
        marks_of(k, marks, 'wm.' + k, fill=GRAY_HL, alpha=42)
    miss = W_['miss']
    sc.put('miss.word', tag_at(miss, W_.get('miss_tag', '검색 결과에 없어요'), name='miss.word'))
    # 지금 쓰는 검색 2: 일반 임베딩 — 숫자 막대에서 비슷한 기록 셋으로 회색 실, 순위 뱃지
    Sm = spec['sim']
    ranks = Sm['ranks']
    rk, gth = [], []
    for i, k in enumerate(ranks):
        bx, by, bw, bh = sc.box[k]
        sc.put('rank%d' % (i + 1), [R('rank%d/c' % (i + 1), bx - 13, by - 13, 28, 28, prst='ellipse', fill='8E88A0', line='FFFFFF',
                                      line_w=1.6),
                                    T('rank%d/t' % (i + 1), bx - 13, by - 13, 28, 28, str(i + 1), size=10.5, color='FFFFFF',
                                      weight='b', align='c', anchor='ctr')])
        rk.append('rank%d' % (i + 1))
        pts = route(sc.gen_pt, sc.box[k], [b for b in obst if b != sc.box[k]])
        sc.put('gth%d' % (i + 1), [C('gth%d/l' % (i + 1), pts, w=1.8, color='B9B3C8')])
        gth.append('gth%d' % (i + 1))
    top = ranks[0]
    sc.put('sim.tag', tag_at(top, Sm['top_tag'], name='sim.tag'))
    if Sm.get('top_marks'):
        marks_of(top, Sm['top_marks'], 'sm.top', fill=GRAY_HL, alpha=42)

    # 홉마다: 다시 쓴 질문(통째로) + 필터
    re_keys = {}

    def re_key(n):
        if n in re_keys:
            return re_keys[n]
        hop = hops[n - 1]
        cond = hop['filter'].get('cond', hop['filter']['label']) if hop.get('filter') else None
        mark = hops[n - 2]['token'] if n > 1 else hop.get('cond_word')
        key = 're:%d' % n
        prims, pt_, fc, h = engine_block(key, sc.RE_Y, 'Reasoning Embedding', '다시 쓴 질문' if n > 1 else '먼저 풀 질문',
                                         hop_runs(spec, n), cond, 're', mark=mark)
        sc.put(key, prims)
        re_keys[n] = key
        sc.re_pt = pt_
        sc.re_fc = getattr(sc, 're_fc', {})
        sc.re_fc[n] = fc
        return key

    H = []
    for i, hop in enumerate(hops):
        n = i + 1
        h = dict(n=n, hop=hop)
        k_re = re_key(n)
        f = hop.get('filter')
        if f:
            keys = f['keep']
            x0 = min(sc.box[k][0] for k in keys) - 14
            y0 = min(sc.box[k][1] for k in keys) - 18
            x1 = max(sc.box[k][0] + sc.box[k][2] for k in keys) + 14
            y1 = max(sc.box[k][1] + sc.box[k][3] for k in keys) + 14
            lab = f['label']
            lw_ = tw('필터  ' + lab, 10, 'b') + 24
            sc.put('fb%d' % n, [R('fb%d/r' % n, x0, y0, x1 - x0, y1 - y0, prst='roundRect', radius=18, fill=LAV, alpha=30,
                                  line=PURPLE2, line_w=1.6, dash='dash'),
                                R('fb%d/lb' % n, x0 + 14, y0 - 14, lw_, 28, prst='roundRect', fill=PURPLE, line=None),
                                T('fb%d/lt' % n, x0 + 14, y0 - 14, lw_, 28, [[('필터  ', {'color': 'D6CCFF'}), (lab, {'color': 'FFFFFF'})]],
                                  size=10, color='FFFFFF', weight='b', align='c', anchor='ctr')])
            fbox = (x0, y0, x1 - x0, y1 - y0)
            sc.box['fb%d' % n] = fbox
            others = [sc.box[k] for k in recs if k not in keys]
            fc = sc.re_fc[n]
            p0 = (fc[0] + fc[2] + 2, fc[1] + fc[3] / 2)
            p0 = (EX + EW + 2, p0[1])
            sc.put('fl%d' % n, [C('fl%d/l' % n, route_below(p0, fbox, others), w=1.8, color=PURPLE2, dash='dash')])
            for k, lab2 in f.get('drop', {}).items():
                sc.put('drop%d.%s' % (n, k), tag_at(k, lab2, style='grayfill', name='drop%d.%s' % (n, k)))
            for k, marks in f.get('marks', {}).items():
                marks_of(k, marks, 'fm%d.%s' % (n, k), alpha=30)
            h['fbox'] = fbox
        k = hop['target']
        tb = sc.box[k]
        sc.put('th%d' % n, S.thread_prims('th%d' % n, route(sc.re_pt, tb, [b for b in obst if b != tb])))
        if hop.get('marks'):
            rects = marks_of(k, hop['marks'], 'hm%d' % n)
            h['mark0'] = rects[0]
        for ck, lab2 in hop.get('cands', {}).items():
            sc.put('why%d.%s' % (n, ck), tag_at(ck, lab2, style='grayfill', name='why%d.%s' % (n, ck)))
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
            h.setdefault('mark0', r_)
        if hop.get('ok'):
            sc.put('ok%d' % n, tag_at(k, hop['ok'], style='fill', where='tr', name='ok%d' % n))
        h['target'] = k
        # 찾은 단서 칩: 기록 아래(필터 상자 안이면 상자 아래) → 다음 질문의 빈자리로(마지막은 답 칸으로)
        last = n == nh
        lab = spec['answer'] if last else hop['token']
        tkw = chip_prims('x', 0, 0, lab, pt=10, padx=11)[1]
        below = (h['fbox'][1] + h['fbox'][3] + 8) if f else (tb[1] + tb[3] + 10)
        at = hop.get('tok_at', (tb[0] + tb[2] - tkw - 6, below))
        sc.put('tok%d@src' % n, chip_prims('tok%d' % n, at[0], at[1], lab, style='fill', pt=10, h=26, padx=11)[0])
        if last:
            sc.put('tok%d@q' % n, chip_prims('tok%d' % n, sc.X0, sc.ans_y, lab, style='fill', pt=10, h=23, padx=9)[0])
            sc.put('qans.ok', chip_prims('qans.ok', sc.X0 + chip_prims('x', 0, 0, lab, pt=10, padx=9)[1] + 6, sc.ans_y + 1, '멈춤',
                                         style='soft', pt=9, h=21, padx=8)[0])
        else:
            sc.put('tok%d@q' % n, chip_prims('tok%d' % n, sc.X0, sc.row_y(n + 1) - 1, lab, style='fill', pt=10, h=23, padx=9)[0])
        H.append(h)

    def back_arrow(name, h):
        """기록의 근거(형광펜) → 다음 질문 칸의 단서 칩: 점선 화살표. 사이에 다른 카드가 있으면 그 줄 아래 빈 곳으로 돌아감."""
        n = h['n']
        tb_ = sc.box[h['target']]
        mx, my, mw, mh = h.get('mark0') or tb_
        ex_, ey_ = EX + EW - 6, sc.row_y(n + 1) + 10          # 다음 질문 줄의 오른쪽 끝으로(줄 글자를 가로지르지 않게)
        others = [sc.box[k] for k in recs if k != h['target']]
        between = [b for b in others if b[0] + b[2] > EX + EW and b[0] < tb_[0] - 4 and b[1] < tb_[1] + tb_[3] and b[1] + b[3] > tb_[1]]
        if not between:
            sx_, sy_ = mx, my + mh / 2
            pts = [(sx_ - 2, sy_), (sx_ - 70, sy_), (ex_ + 70, ey_), (ex_, ey_)]
        else:
            rb = max([tb_[1] + tb_[3]] + [b[1] + b[3] for b in between])
            below = [b[1] for b in others if b[1] >= rb - 2 and b[0] < tb_[0] + tb_[2] and b[0] + b[2] > EX + EW]
            gy = (rb + min(below)) / 2 if below else rb + 24
            sx_ = mx + min(mw / 2, 40)
            gx = EX + EW + 26
            pts = [(sx_, tb_[1] + tb_[3] + 1), (sx_, gy - 10), (sx_ - 10, gy), (sx_ - 30, gy),
                   (sx_ - 30 - (sx_ - 30 - gx - 30) / 3, gy), (gx + 30 + (sx_ - 30 - gx - 30) / 3, gy), (gx + 30, gy),
                   (gx - 20, gy), (ex_ + 50, ey_), (ex_, ey_)]
        return [C(name + '/l', pts, w=1.6, color=PURPLE2, dash='sysDash', tail='triangle')]

    # -------------------------------------------------------------- 단계 진행
    cur, styles = [], {}

    def show(*ks):
        for k in ks:
            if k not in cur:
                cur.append(k)

    def hide(*ks):
        for k in ks:
            if k in cur:
                cur.remove(k)

    def shot(key, frame_keys, side, focus, hud, zmax, anim=None, half=(), pad=16, cap=None, notes=None, morph=1400, frame_box=None):
        cap = cap or CP[key]
        cap = cap if isinstance(cap, dict) else dict(t=cap)
        shown = list(cur)
        half = set(half)
        focus = set(focus)
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
        cam, crect = frame(box, side, zmax, cw, ch, pad)
        lab = ' '.join(''.join(t for t, _ in cap['t']).split())
        sc.steps.append(Step(key=key, cam=cam, cap=cap, cap_rect=(crect, side), show=shown, focus=focus, half=half, styles=dict(styles),
                             hud=hud, anim=anim or {}, notes=notes if notes is not None else NT[key], morph_ms=morph, label=lab))

    ui_base = ['ui'] + (['ui.glogo', 'ui.sbox'] if kind == 'google' else ['ui.head', 'ui.msg']) + ['ui.kbd', 'ui.keys']
    D = lambda *s: set(s)   # noqa: E731
    show(*ui_base)
    # 1 상황: 폰 위쪽(질문)을 가까이
    shot('open', sc.ui['top'] + (['ui/glogo'] if False else []), 'right', set(ui_base), {}, 2.1,
         frame_box=union([sc.box[k] for k in sc.ui['top']] + ([(PX + 20, PY + 40, PW - 40, 50)] if kind == 'google' else [])))
    # 2 기록 더미: 넓게
    show(*recs)
    shot('cloud', recs + ['ui'], 'top', set(recs), {}, 0.95, morph=1600)
    # 3 단어로 찾기
    show('wbox', *['wm.' + k for k in hits])
    styles.update({k: 'gray' for k in hits})
    shot('word', ['wbox'] + hits + [miss], 'top', set(['wbox'] + hits), {}, 1.35,
         anim={'wm.' + k: dict(kind='zoom_in', delay=300 + 150 * j, dur=300) for j, k in enumerate(hits)})
    # 4 단어로는 못 찾는 이유: 그 기록을 가까이
    show('miss.word')
    styles[miss] = 'gray'
    shot('word_miss', [miss, 'miss.word'], 'right', {miss, 'miss.word'}, {}, 2.5,
         anim={'miss.word': dict(kind='zoom_in', delay=200, dur=350)}, pad=22)
    # 5 비슷한 것 찾기(일반 임베딩)
    hide('miss.word', 'wbox', *['wm.' + k for k in hits])
    for k in hits + [miss]:
        styles.pop(k, None)
    styles.update({k: 'gray' for k in ranks})
    show('gen', *gth, *rk)
    shot('sim', ['gen'] + ranks, 'top', set(['gen'] + ranks + rk + gth), {}, 1.35,
         anim=dict({'gen': dict(kind='rise', delay=0, dur=450)},
                   **{g: dict(kind='wipe_in', dir='left', delay=500 + 200 * j, dur=450) for j, g in enumerate(gth)},
                   **{r_: dict(kind='zoom_in', delay=750 + 200 * j, dur=280) for j, r_ in enumerate(rk)}))
    # 6 일반 임베딩이 1위로 올린 것: 가까이
    hide(*gth, *rk[1:])
    show('sim.tag', *(['sm.top'] if Sm.get('top_marks') else []))
    shot('sim_miss', [top, 'sim.tag', 'rank1'], 'right', {top, 'sim.tag', 'rank1'}, {}, 2.4,
         anim={'sim.tag': dict(kind='zoom_in', delay=250, dur=350), 'sm.top': dict(kind='wipe_in', dir='left', delay=500, dur=400)},
         pad=22)
    # 7 01 순간 감지
    hide('gen', 'sim.tag', 'sm.top', *gth, *rk)
    for k in ranks:
        styles.pop(k, None)
    trig = {'google': ['ui.on', 'ui.tap'], 'sheet': ['ui.on', 'ui.tap', 'ui.sheet'], 'gps': ['ui.loc', 'ui.on']}[kind]
    show(*trig)
    if kind == 'google':
        fb = union([sc.box['ui.glogo'], sc.box['ui.kbd']])
    elif kind == 'sheet':
        fb = union([sc.box['ui.head'], sc.box['ui.msg'], sc.box['ui.sheet.top']])
    else:
        fb = union([sc.box['ui.head'], sc.box['ui.msg'], sc.box['ui.loc'], sc.box['ui.kbd']])
    tf = ['ui']
    shot('trig', tf, 'right', set(ui_base + trig), dict(cur='01'), 2.0,
         anim={k: dict(kind='rise' if k == 'ui.sheet' else 'zoom_in', delay=200 + 200 * j, dur=420) for j, k in enumerate(trig)},
         frame_box=fb, morph=1600)
    hide('ui.tap')
    # 8 02 질문 나누기: 판을 가까이
    qrows = ['q%d' % i for i in range(1, nh + 1)]
    qkeys = ['qp', 'qorig'] + qrows + ['qans', 'qans.slot']
    styles['q1'] = 'cur'
    show(*qkeys)
    shot('split', ['qp'], 'right', set(qkeys), dict(cur='02', done=D('01')), 1.9,
         anim={x: dict(kind='zoom_in', delay=350 + 300 * j, dur=350) for j, x in enumerate(qrows)}, morph=1600)
    # 9 빈칸: 다음 질문 줄을 더 가까이
    shot('blank', ['q2'], 'right', {'qp', 'q2'}, dict(cur='02', done=D('01')), 2.5, pad=22,
         anim={'q2': dict(kind='pulse', delay=300, dur=450, scale=1.04)})
    re_cur = None
    for h in H:
        n, hop = h['n'], h['hop']
        f = hop.get('filter')
        k = hop['target']
        tb = sc.box[k]
        hud3 = dict(cur='03', done=D('01', '02'), loop=n)
        k_re = re_key(n)
        if re_cur != k_re:
            if re_cur:
                hide(re_cur)
            show(k_re)
            re_cur = k_re
        hc = CP['hops'][n - 1]
        hn = NT['hops'][n - 1]
        if n > 1:
            # 다시 쓴 질문이 통째로 Reasoning Embedding에 들어감: 질문 칸을 가까이
            shot('rw%d' % n, [k_re], 'right', {k_re}, hud3, 2.2, cap=hc['rw'], notes=hn['rw'],
                 anim={k_re + '': dict(kind='pulse', delay=300, dur=450, scale=1.03)})
        if f:
            drops = ['drop%d.%s' % (n, x) for x in f.get('drop', {})]
            fms = ['fm%d.%s' % (n, x) for x in f.get('marks', {})]
            show('fb%d' % n, 'fl%d' % n, *drops, *fms)
            focus = set(f['keep'] + ['fb%d' % n, 'fl%d' % n, k_re] + drops)
            shot('filter%d' % n, ['fb%d' % n] + list(f.get('drop', {})), 'top', focus, hud3, 1.5, cap=hc['filter'],
                 notes=hn['filter'],
                 anim=dict({'fl%d' % n: dict(kind='wipe_in', dir='left', delay=0, dur=550),
                            'fb%d' % n: dict(kind='fade_in', delay=400, dur=450)},
                           **{x: dict(kind='zoom_in', delay=850 + 150 * j, dur=300) for j, x in enumerate(drops)},
                           **{x: dict(kind='wipe_in', dir='left', delay=800, dur=400) for x in fms}))
            hide(*drops, 'fl%d' % n, *fms)
        # 03 찾기: 띠 → 실 → 기록 (중간 거리)
        show('th%d' % n)
        styles[k] = 'weave'
        fk = [k_re, k]
        focus = set(fk + ['th%d' % n])
        shot('find%d' % n, fk, 'top', focus, hud3, 1.45, cap=hc['find'], notes=hn['find'],
             anim={'th%d' % n: dict(kind='wipe_in', dir='left', delay=100, dur=700)},
             half=(list(f['keep']) + ['fb%d' % n]) if f else ())
        hide('fb%d' % n)
        # 가까이: 근거에 형광펜 → 단서 칩
        cands = list(hop.get('cands', {}))
        whys = ['why%d.%s' % (n, c) for c in cands]
        pills = ['pl%d.%s' % (n, x) for x in hop.get('pills', {})]
        extra = [x for x in ('hm%d' % n, 'im%d' % n, 'pm%d' % n, 'ok%d' % n) if x in sc.items]
        show(*whys, *pills, *extra, 'tok%d@src' % n)
        hide('th%d' % n)
        focus = set([k, 'tok%d@src' % n] + extra + whys)
        ck = [k, 'tok%d@src' % n] + ([c for c in cands] if hop.get('close_cands', True) else [])
        shot('close%d' % n, ck, hop.get('close_side', 'right'), focus, hud3, 2.4 if not cands else 2.0, cap=hc['close'],
             notes=hn['close'], half=cands, pad=20,
             anim=dict({'hm%d' % n: dict(kind='wipe_in', dir='left', delay=300, dur=500),
                        'im%d' % n: dict(kind='wipe_in', dir='left', delay=300, dur=500),
                        'pm%d' % n: dict(kind='wipe_in', dir='left', delay=400, dur=500),
                        'ok%d' % n: dict(kind='zoom_in', delay=900, dur=300),
                        'tok%d@src' % n: dict(kind='zoom_in', delay=1200, dur=350)},
                       **{x: dict(kind='zoom_in', delay=500 + 150 * j, dur=300) for j, x in enumerate(whys)},
                       **{x: dict(kind='zoom_in', delay=150 + 150 * j, dur=300) for j, x in enumerate(pills)}))
        hide(*whys, 'ok%d' % n)
        if n < nh:
            # 02 다시 쓰기: 칩이 다음 질문의 빈자리로 날아감(중간 거리 — 기록과 판이 함께 보이게)
            hide('tok%d@src' % n)
            show('tok%d@q' % n)
            styles['q%d' % n] = 'done' + ('_rw' if n > 1 else '')
            styles['q%d' % (n + 1)] = 'cur_rw'
            sc.put('bk%d' % n, back_arrow('bk%d' % n, h))
            show('bk%d' % n)
            k_nx = re_key(n + 1)
            hide(re_cur)
            re_cur = None
            shot('loop%d' % n, ['qp', k], 'top', {'q%d' % (n + 1), 'tok%d@q' % n, 'bk%d' % n},
                 dict(cur='02', done=D('01', '03'), loop=n, loop_on=True), 1.45, cap=hc['loop'], notes=hn['loop'], half=[k, 'qp'],
                 anim={'bk%d' % n: dict(kind='fade_in', delay=900, dur=500)}, morph=1700)
            hide('bk%d' % n)
            for x in pills:
                hide(x)
            hide('pm%d' % n, 'im%d' % n)
    # 멈춤: 답이 나오면 그만 — 판의 답 칸을 가까이
    last = H[-1]
    hide('tok%d@src' % nh, 'qans.slot', re_cur, *['pl%d.%s' % (nh, x) for x in hops[-1].get('pills', {})], 'pm%d' % nh, 'im%d' % nh)
    show('tok%d@q' % nh, 'qans.ok')
    styles['q%d' % nh] = 'done' + ('_rw' if nh > 1 else '')
    shot('stop', ['qp'], 'right', set(['qp', 'qorig', 'qans', 'qans.ok'] + qrows + ['tok%d@q' % h['n'] for h in H]),
         dict(cur='03', done=D('01', '02'), loop=nh), 1.9, anim={'qans.ok': dict(kind='zoom_in', delay=700, dur=300)}, morph=1600)
    # 04 전달: 폰의 카드를 가까이. 카드가 열리면 빨간 배지는 사라짐
    hide('ui.loc')
    show('ans', 'ui.tap2')
    styles['ui.on'] = 'nobadge'
    shot('deliver', ['ans'], 'right', set(ui_base + ['ans', 'ui.tap2', 'ui.on'] + (['ui.sheet'] if kind == 'sheet' else [])),
         dict(cur='04', done=D('01', '02', '03')), 1.9,
         anim={'ans': dict(kind='rise', delay=200, dur=550), 'ui.tap2': dict(kind='zoom_in', delay=1500, dur=300)}, morph=1700,
         frame_box=union([sc.box['ans'], sc.box['ui.sheet.top']]) if kind == 'sheet' else None)
    # 결과
    hide('ui.tap2', 'ans', 'ui.on')
    if kind == 'google':
        styles['ui.sbox'] = 'done'
        res_keys = ['ui.res'] if 'ui.res' in sc.items else []
        rf = ['ui.sbox'] + res_keys
    else:
        hide('ui.sheet')
        res_keys = ['res'] if 'res' in sc.items else []
        rf = ['ui.msg'] + res_keys
    show(*res_keys)
    shot('result', rf, 'right', set(ui_base + res_keys), dict(cur='04', done=D('01', '02', '03')), 1.9,
         anim={k: dict(kind='rise', delay=300, dur=500) for k in res_keys})
    # 정리: 질문 줄 → 찾은 기록 실, 기록의 근거 → 다음 질문 칩 점선. 다른 기록은 뺌
    targets = [h['target'] for h in H]
    hide(*[r for r in recs if r not in targets])
    for k in targets:
        styles[k] = 'weave'
    sth = []
    for h in H:
        n = h['n']
        p0 = (EX + EW + 2, sc.row_y(n) + 10)
        sc.put('sth%d' % n, S.thread_prims('sth%d' % n, route(p0, sc.box[h['target']], [sc.box[t] for t in targets if t != h['target']])))
        sth.append('sth%d' % n)
    sbk = []
    for h in H[:-1]:
        sc.put('sbk%d' % h['n'], back_arrow('sbk%d' % h['n'], h))
        sbk.append('sbk%d' % h['n'])
    hm_all = [x for x in ['hm%d' % h['n'] for h in H] + ['im%d' % h['n'] for h in H] if x in sc.items]
    show(*sth, *sbk, *hm_all)
    for i in range(1, nh + 1):
        styles['q%d' % i] = 'done' + ('_rw' if i > 1 else '')
    toks = ['tok%d@q' % h['n'] for h in H]
    shot('sum', ['qp'] + targets, 'top', set(['qp', 'qorig', 'qans', 'qans.ok'] + qrows + toks + targets + sth + sbk + hm_all),
         dict(all=True), 1.05,
         anim=dict({x: dict(kind='wipe_in', dir='left', delay=200 + 500 * j, dur=600) for j, x in enumerate(sth)},
                   **{x: dict(kind='fade_in', delay=500 + 500 * j, dur=500) for j, x in enumerate(sbk)}), morph=1700)
    return sc
