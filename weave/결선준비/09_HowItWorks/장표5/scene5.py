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
                   RING, SUB, C, G, P, R, T, band, card_prims, chip_prims, scurve, tw, vcurve)

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
    beats: list = field(default_factory=list)      # 클릭마다 나오는 효과 묶음(발표자가 한 마디씩). anim은 장이 열릴 때 바로
    cap_beat: int = None                            # 설명을 이 클릭 묶음에서 나오게(없으면 장과 함께)


def bbox(prims):
    xs, ys = [], []
    for p in prims:
        if p[0] == 'group':
            gx, gy, gw, gh = bbox(p[2])
            xs += [gx, gx + gw]
            ys += [gy, gy + gh]
            continue
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
        out.append(C('top/loop', [a, (a[0], y0 + hh + 26), (b[0], y0 + hh + 26), (b[0], b[1] + 3)], w=2.4 if on else 1.8, color=col,
                     tail='triangle'))
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


def deliver_sheet(sc, a, groups, n_src, x, w, kind, ky, msg_end):
    """전달 카드(layout='sheet'): 실제 데모 UI와 같은 구조. ✦ 카드에는 글만, 그 아래 버튼, 그 아래 '연결된 기억'."""
    ml = wrap(a['main'], 13.5, w - 72, 'b') if '\n' not in a['main'] else a['main'].split('\n')
    lav_h = 12 + 18 + 22 * len(ml) + 8
    rows_h = 22 * n_src + 6 * max(0, len(groups) - 1)
    ch = 12 + lav_h + 8 + 34 + 10 + 18 + rows_h + 10
    ay = (sc.ui['sheet_y'] + 112) if kind == 'sheet' else ky - ch - 12
    sc.ui['ans_overlaps_msg'] = kind != 'sheet' and ay < msg_end + 6
    lx, lw = x + 22, w - 44
    ly = ay + 12
    card = [R('ans/bg', x + 14, ay, w - 28, ch, prst='roundRect', radius=16, fill='FFFFFF', line=RING, line_w=1.8,
              shadow=S.L.SHADOW_LIFT, glow=(9, RING, 24)),
            R('ans/lav', lx, ly, lw, lav_h, prst='roundRect', radius=11, fill='F4F0FF', line='E3D9FF', line_w=1.0),
            R('ans/star', lx + 10, ly + 12, 11, 11, prst='star4', fill=PURPLE, line=None),
            T('ans/lab', lx + 25, ly + 7, lw - 34, 20, a.get('label', '찾은 답'), size=9.5, color=PURPLE2, weight='b', anchor='ctr'),
            T('ans/main', lx + 10, ly + 29, lw - 20, 22 * len(ml), ml, size=13.5, color=INK, weight='b', lnspc=17)]
    by = ly + lav_h + 8
    btn = a.get('button', '✓  입력하기')
    card += [R('ans/btn', lx, by, lw, 34, prst='roundRect', fill=PURPLE, line=None),
             T('ans/btn_t', lx, by, lw, 34, btn, size=10.5, color='FFFFFF', weight='b', align='c', anchor='ctr'),
             T('ans/ttl', lx + 2, by + 34 + 10, lw, 18, '연결된 기억', size=9.5, color=INK, weight='b', anchor='ctr')]
    ry = by + 34 + 10 + 18
    for gi, (ic, lns) in enumerate(groups):
        card.append(P('ans/si%d' % gi, S.ICON[ic], lx + 2, ry + 3, 16, 16))
        for li, txt in enumerate(lns):
            card.append(T('ans/st%d_%d' % (gi, li), lx + 24, ry, lw - 26, 22, txt, size=fit_pt(txt, lw - 28, 9, 'r', 7.5), color=SUB,
                          anchor='ctr'))
            ry += 22
        ry += 6
    sc.put('ans', card)
    sc.put('ui.tap2', [P('ui.tap2/h', 'touch-tap.png', x + w - 78, by + 18, 28, 40)])


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
            by = y + (72 if style == 'up' else 106)      # 'up' = 전달 카드가 올라올 때 검색창이 가려지지 않게 위로
            return [R('ui.sbox/bg', x + 18, by, w - 36, hh, prst='roundRect', radius=23, fill='FFFFFF', line='DADCE0', line_w=1.2,
                      shadow=S.L.SHADOW_SOFT),
                    R('ui.sbox/lens', x + 34, by + hh / 2 - 8, 13, 13, prst='ellipse', fill=None, line='9AA0A6', line_w=1.8),
                    R('ui.sbox/lens2', x + 44, by + hh / 2 + 3, 6, 2, fill='9AA0A6', line=None),
                    T('ui.sbox/t', x + 58, by, w - 92, hh, tl, size=11, color=INK, anchor='ctr', lnspc=12)]
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
    if a.get('layout') == 'sheet':
        deliver_sheet(sc, a, groups, n_src, x, w, kind, ky, msg_end)
        ml = None
    else:
        ml = wrap(a['main'], 13.5, w - 64, 'b') if '\n' not in a['main'] else a['main'].split('\n')
    for ln in ml or []:
        if tw(ln, 13.5, 'b') > w - 60:
            print('   ! 건네기 카드 글이 넘침: %s (%.0f > %.0f)' % (ln, tw(ln, 13.5, 'b'), w - 60))
    ch = 0 if ml is None else 40 + 22 * len(ml) + 10 + 22 * n_src + 6 * max(0, len(groups) - 1) + 8 + 36 + 14 + (34 if a.get('attach') else 0)
    if ml is not None:
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
    sc.ok_below = EX + 46 + acw + 6 + tw(sp.get('stop_label', '탐색 끝'), 9, 'b') + 28 > EX + EW - 12
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


VEC_COLS = ['E2D9FF', 'C7B7FF', 'A68DFF', '8566FF', '5A3FE0']       # 벡터 칸 색(옅은 → 진한 보라, 노랑 없음, 가장 옅은 칸도 보이게)


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


APP_OF = {'talk': 'kakaotalk', 'link': 'kakaotalk', 'pay': 'kakaotalk', 'sms': 'messages', 'gallery': 'gallery', 'photo': 'gallery',
          'shot': 'gallery', 'note': 'notes', 'mail': 'email', 'cal': 'calendar', 'phone': 'phone', 'call': 'phone', 'map': 'maps',
          'wallet': 'wallet', 'wpay': 'wallet', 'pass': 'wallet'}


def vec_text(seed, n=4):
    """기록의 벡터를 숫자로(예: '[0.12, −0.53, 0.88, …]'). 값은 글자에서 나온 예시값이라 같은 기록이면 늘 같음."""
    import hashlib
    hv = hashlib.md5(seed.encode('utf-8')).digest()
    vals = []
    for i in range(n):
        v = hv[i] / 255 * 1.8 - 0.9
        vals.append(('−' if v < 0 else '') + '%.2f' % abs(v))
    return '[' + ', '.join(vals) + ', …]'


def iso_date(text, with_time=False, year=2026):
    """'2026. 3. 15 (일) 20:14' → '2026-03-15 20:14'(with_time), '3월 8일' → '2026-03-08', '3/20 (금) 19:00' → '2026-03-20'. 없으면 None."""
    import re
    t = text or ''
    d = None
    for pat in (r'(\d{4})\. (\d{1,2})\. (\d{1,2})', r'()(\d{1,2})/(\d{1,2})', r'()(\d{1,2})월 (\d{1,2})일'):
        m = re.search(pat, t)
        if m:
            d = '%s-%02d-%02d' % (m.group(1) or year, int(m.group(2)), int(m.group(3)))
            break
    if d is None:
        return None
    if with_time:
        m = re.search(r'(\d{1,2}):(\d{2})', t)
        if m:
            d += ' %02d:%s' % (int(m.group(1)), m.group(2))
    return d


def meta_text(date, app, lines=2):
    """메타데이터를 실제 형식으로: { date: "2026-03-12", app: "kakaotalk" } (두 줄이면 줄을 나눔)."""
    if lines == 1:
        return ['{ date: "%s", app: "%s" }' % (date, app)]
    return ['{ date: "%s",' % date, '  app: "%s" }' % app]


def month_day(text):
    """글 속 날짜 → '3/12'. '2026. 3. 12 (목)', '3/20 (금) 19:00', '3월 8일 12:40', '2월 27일' 모두. 없으면 None."""
    import re
    t = text or ''
    for pat in (r'\d{4}\. (\d{1,2})\. (\d{1,2})', r'(\d{1,2})/(\d{1,2})', r'(\d{1,2})월 (\d{1,2})일'):
        m = re.search(pat, t)
        if m:
            return '%s/%s' % (m.group(1), m.group(2))
    return None


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
        """키워드 검색(왼쪽)과 임베딩 검색(오른쪽)을 한 장에. 클릭 순서 = 말하는 순서.
        왼쪽: 판 → 질문 속 단어 형광펜 → 같은 단어가 든 결과 1·2 → 아닌 이유.
        오른쪽: 판 → 질문 벡터(숫자) → 임베딩 공간의 한 점(저장해 둔 기록들 사이) → 질문 점에서 원이 커지며 가장 가까운 기록을 잡음
               → 1·2위와 아닌 이유, 날짜가 든 지은 카톡은 원 밖에."""
        PR = dict(F.get('pair', {}))
        HWL, HWR, GX_ = PR.get('hw', 470), PR.get('hw_r', 520), PR.get('gap', 80)
        LX0 = PR.get('x', 640)
        RX0 = LX0 + HWL + GX_
        TOP = PR.get('top', 150)
        kwp, _, kwh = search_panel('kw', TOP, '키워드 검색', 'BM25', F['query'], [], False, x=LX0, w=HWL)
        ebp, _, ebh = search_panel('emb', TOP, '임베딩 검색', None, F['query'], [], False, x=RX0, w=HWR)
        sc.put('kw', kwp)
        sc.put('emb', ebp)
        # ---- 왼쪽
        qx, qy = LX0 + 16, TOP + 46
        ql = wrap(F['query'], 10.5, HWL - 32 - 24, 'm')[:2]
        hls = []
        for i, ln in enumerate(ql):
            for wd in F['words']:
                st = 0
                while wd in ln[st:]:
                    r_ = band((qx + 12, qy + 7 + 20 * i, ln, 10.5, 'm'), wd, kind='full', start=st)
                    hls.append(R('kw.hl/%d' % len(hls), *r_, prst='roundRect', radius=2.5, fill=HL, alpha=34, line=None))
                    st = ln.index(wd, st) + len(wd)
        sc.put('kw.hl', [G('kw.hl/g', hls)])
        K = F['kw']
        ws = [REC[k]['w'] for k in K['ranks']]
        n = len(ws)
        gapc = PR.get('kw_gap', 30)
        x = LX0 + (HWL - sum(ws) - gapc * (n - 1)) / 2
        ry = TOP + kwh + PR.get('kw_dy', 64)
        kbot = ry
        k2, k3 = {}, {}
        kw_keys = ['kw', 'kw.hl']
        for i, k in enumerate(K['ranks']):
            pr, h, pos = card_at(k, x, ry, style='gray')
            w_ = REC[k]['w']
            sc.put('kw.res.' + k, [G('kw.res.%s/g' % k, pr)])
            sx_ = LX0 + HWL / 2 + (i - (n - 1) / 2) * 96
            th = 'kw.th%d' % (i + 1)
            sc.put(th, [C(th + '/l', vcurve((sx_, TOP + kwh + 1), (x + w_ / 2, ry - 2)), w=1.8, color='B9B3C8')])
            rk = 'kw.rank%d' % (i + 1)
            sc.put(rk, [G(rk + '/g', rank_prims('krank%d' % (i + 1), x - 13, ry - 12, i + 1))])
            kw_keys += [th, 'kw.res.' + k, rk]
            k2[th] = dict(kind='wipe_in', dir='down', delay=0, dur=220)
            k2['kw.res.' + k] = dict(kind='fade_in', delay=120 + 90 * i, dur=220)
            k2[rk] = dict(kind='zoom_in', delay=200 + 90 * i, dur=200)
            box = (x, ry, w_, h)
            if K.get('marks', {}).get(k):
                marks_at(pos, K['marks'][k], 'kw.mk.' + k, alpha=30)
                kw_keys.append('kw.mk.' + k)
                k2['kw.mk.' + k] = dict(kind='wipe_in', dir='left', delay=420 + 90 * i, dur=240)
            if K.get('tags', {}).get(k):
                sc.put('kw.tag.' + k, [G('kw.tag.%s/g' % k, tag_box(box, K['tags'][k], where='br', name='ktag.' + k, pt=11))])
                kw_keys.append('kw.tag.' + k)
                k3['kw.tag.' + k] = dict(kind='zoom_in', delay=90 * i, dur=200)
            kbot = max(kbot, ry + h)
            x += w_ + gapc
        if PR.get('kw_note'):
            sc.put('kw.note', [T('kw.note/t', LX0, kbot + 52, HWL, 24, PR['kw_note'], size=11, color=SUB, weight='sb', align='c',
                                 anchor='ctr')])
            kw_keys.append('kw.note')
            k3['kw.note'] = dict(kind='fade_in', delay=200, dur=220)
        # ---- 오른쪽: 질문 벡터(숫자) → 임베딩 공간
        E_ = F['emb']
        vy = TOP + ebh + 16
        vlab = PR.get('qv_label', '질문 벡터')
        vtx = vec_text(F['query'], 5)
        vlw = tw(vlab, 10, 'b') + 14
        vtw = tw(vtx, 11, 'sb') + 8
        sc.put('emb.qv', [G('emb.qv/g', [T('emb.qv/l', RX0 + 16, vy, vlw, 24, vlab, size=10, color=PURPLE, weight='b', anchor='ctr'),
                                         T('emb.qv/t', RX0 + 16 + vlw, vy, vtw, 24, vtx, size=11, color=PURPLE2, weight='sb',
                                           anchor='ctr')])])
        vcx, vcy = RX0 + 16 + vlw + vtw / 2, vy + 12
        my0 = vy + 40
        mh = PR.get('map_h', 250)
        sx, sy = RX0 + PR.get('star_x', 168), my0 + PR.get('star_y', 128)
        rr = PR.get('ring_r', 98)
        mlab = PR.get('map_label', '임베딩 공간')
        mlab2 = PR.get('map_label2', '가까울수록 비슷한 뜻')
        sc.put('emap', [G('emap/g', [R('emap/bg', RX0, my0, HWR, mh, prst='roundRect', radius=18, fill='FFFFFF', alpha=80, line=LINE,
                                       line_w=1.0),
                                     T('emap/l1', RX0 + 16, my0 + 10, 200, 18, mlab, size=9.5, color=PURPLE, weight='b', anchor='ctr'),
                                     T('emap/l2', RX0 + HWR - 16 - tw(mlab2, 9, 'sb') - 4, my0 + mh - 28, tw(mlab2, 9, 'sb') + 4, 18,
                                       mlab2, size=9, color=MUTE, weight='sb', anchor='ctr')])])
        taken = [(RX0 + 10, my0 + 6, 220, 26), (RX0 + HWR - 30 - tw(mlab2, 9, 'sb'), my0 + mh - 34, tw(mlab2, 9, 'sb') + 24, 30),
                 (sx - 80, sy - 22, 104, 50)]
        # 기록들: 가장 가까운 사진 둘(원 안), 스크린샷·선물 메모(원 밖 조금 멀리), 지은 카톡(멀리)
        near = PR.get('near', {'bar': (46, -46), 'white': (62, 40)})
        TW_, TH_ = PR.get('thumb', (66, 50))
        recs, e2, e3, e4 = [], {'emap': dict(kind='fade_in', delay=0, dur=220)}, {}, {}
        for i, k in enumerate(E_['ranks']):
            dx, dy = near[k]
            cx_, cy_ = sx + dx, sy + dy
            x0, y0 = cx_ - TW_ / 2, cy_ - TH_ / 2
            img = REC[k]['img']
            sc.put('emap.rec.' + k, [G('emap.rec.%s/g' % k, [
                R('er.%s/bg' % k, x0 - 4, y0 - 4, TW_ + 8, TH_ + 8, prst='roundRect', radius=9, fill='FFFFFF', line=GRAY_LINE, line_w=1.3,
                  shadow=S.L.SHADOW_SOFT),
                P('er.%s/img' % k, img, x0, y0, TW_, TH_, radius=6, crop=S._fit_crop(img, TW_, TH_))])])
            recs.append('emap.rec.' + k)
            e2['emap.rec.' + k] = dict(kind='fade_in', delay=80 + 60 * i, dur=200)
            rk = 'emap.rank%d' % (i + 1)
            sc.put(rk, [G(rk + '/g', rank_prims('erank%d' % (i + 1), x0 - 4 - 32, cy_ - 13, i + 1, fill=PURPLE))])
            e4[rk] = dict(kind='zoom_in', delay=80 * i, dur=200)
            lab = E_['tags'][k]
            tgw = tw(lab, 10, 'sb') + 20
            ty_ = (y0 - 4 - 8 - 24) if dy < 0 else (y0 + TH_ + 4 + 8)
            sc.put('emap.tag.' + k, [G('emap.tag.%s/g' % k, chip_prims('etag.' + k, cx_ - tgw / 2, ty_, lab, style='grayfill', pt=10, h=24,
                                                                       padx=10, weight='sb')[0])])
            e4['emap.tag.' + k] = dict(kind='zoom_in', delay=160 + 80 * i, dur=200)
            taken += [(x0 - 40, y0 - 8, TW_ + 48, TH_ + 16), (cx_ - tgw / 2 - 6, ty_ - 4, tgw + 12, 32)]
        for k, (dx, dy) in PR.get('mid', {}).items():          # 원 밖, 조금 먼 기록(아이콘 칩)
            c = REC[k]
            ic = c.get('icon') or KIND_ICON.get(c['kind'], 'talk')
            pr, cw_ = chip_prims('emc.' + k, sx + dx, sy + dy, c['title'], style='white', pt=9, h=24, padx=9, icon=ic)
            sc.put('emap.mid.' + k, [G('emap.mid.%s/g' % k, pr)])
            recs.append('emap.mid.' + k)
            e2['emap.mid.' + k] = dict(kind='fade_in', delay=200, dur=200)
            taken.append((sx + dx - 8, sy + dy - 8, cw_ + 16, 40))
        M = F['miss']
        mk_ = M['key']
        fw = S.frag_w(REC[mk_]['title'], chip_text(REC[mk_]))
        fx = RX0 + HWR - fw - PR.get('miss_dx', 18)
        fy = sy - S.FRAG_H / 2 + PR.get('miss_dy', -6)
        sc.put('emap.miss.rec', [G('emap.miss.rec/g', frag_at('emm.' + mk_, mk_, fx, fy))])
        recs.append('emap.miss.rec')
        e2['emap.miss.rec'] = dict(kind='fade_in', delay=260, dur=200)
        mt = M['tag']
        mtw = tw(mt, 10, 'sb') + 22
        sc.put('emap.miss', [G('emap.miss/g', [
            R('miss/r', fx - 7, fy - 7, fw + 14, S.FRAG_H + 14, prst='roundRect', radius=17, fill=None, line=GRAY_LINE, line_w=1.6,
              dash='dash'),
            R('miss/tag', fx + fw / 2 - mtw / 2, fy + S.FRAG_H + 14, mtw, 26, prst='roundRect', fill='EFECF4', line=None),
            T('miss/tag_t', fx + fw / 2 - mtw / 2, fy + S.FRAG_H + 14, mtw, 26, mt, size=10, color=SUB, weight='sb', align='c',
              anchor='ctr')])])
        e4['emap.miss'] = dict(kind='fade_in', delay=320, dur=220)
        taken += [(fx - 12, fy - 12, fw + 24, S.FRAG_H + 56)]
        import random
        rnd = random.Random(spec.get('seed', 11) + 7)
        dots = []
        for _ in range(800):
            if len(dots) >= PR.get('n_dots', 14):
                break
            px_, py_ = rnd.uniform(RX0 + 18, RX0 + HWR - 18), rnd.uniform(my0 + 30, my0 + mh - 16)
            if ((px_ - sx) ** 2 + (py_ - sy) ** 2) ** 0.5 < rr + 14:
                continue
            if any(_overlap((px_ - 6, py_ - 6, 12, 12), t_, 4, 4) for t_ in taken) or any(abs(px_ - a) < 28 and abs(py_ - b) < 24
                                                                                             for a, b in dots):
                continue
            dots.append((px_, py_))
        sc.put('emap.dots', [G('emap.dots/g', [R('emap/d%d' % j, a - 4.5, b - 4.5, 9, 9, prst='ellipse', fill='D6D0E4', line=None)
                                               for j, (a, b) in enumerate(dots)])])
        e2['emap.dots'] = dict(kind='fade_in', delay=60, dur=220)
        # 질문 점: 벡터 숫자 자리에서 공간 속 자리로 날아옴
        sc.put('emap.q', [G('emap.q/g', [R('emap/q', sx - 14, sy - 14, 28, 28, prst='star5', fill=PURPLE, line='FFFFFF', line_w=1.2,
                                           glow=(8, RING, 40)),
                                         T('emap/q_t', sx - 74, sy + 8, 52, 18, '질문', size=9.5, color=PURPLE, weight='b', align='r',
                                           anchor='ctr')])])
        e2['emap.q'] = [dict(kind='fade_in', delay=320, dur=160), dict(kind='path', delay=320, dur=520, wdx=vcx - sx, wdy=vcy - sy, bend=0.18)]
        # 원: 질문 점에서 커지며 가장 가까운 기록을 잡음(+ 잡힌 기록까지 짧은 선)
        sc.put('emap.ring', [G('emap.ring/g', [R('emap/ring', sx - rr, sy - rr, 2 * rr, 2 * rr, prst='ellipse', fill=LAV, alpha=55,
                                                  line=PURPLE2, line_w=1.6, dash='dash')])])
        e3['emap.ring'] = {'kind': 'zoom_in', 'delay': 0, 'dur': 420, 'from': 0.08}
        lns = []
        for i, k in enumerate(E_['ranks']):
            dx, dy = near[k]
            ln_ = (dx * dx + dy * dy) ** 0.5
            ux, uy = dx / ln_, dy / ln_
            ta = (sx + ux * 15, sy + uy * 15)
            tb = (sx + dx - ux * 38, sy + dy - uy * 30)
            lns.append(C('emap/ln%d' % i, [ta, (ta[0] + (tb[0] - ta[0]) / 3, ta[1] + (tb[1] - ta[1]) / 3),
                                            (ta[0] + 2 * (tb[0] - ta[0]) / 3, ta[1] + 2 * (tb[1] - ta[1]) / 3), tb], w=2.0, color=PURPLE2))
        sc.put('emap.lns', [G('emap.lns/g', lns)])
        e3['emap.lns'] = dict(kind='fade_in', delay=380, dur=200)
        emb_keys = ['emb', 'emb.qv', 'emap', 'emap.dots'] + recs + ['emap.ring', 'emap.lns', 'emap.q'] + \
            ['emap.rank%d' % (i + 1) for i in range(len(E_['ranks']))] + ['emap.tag.' + k for k in E_['ranks']] + ['emap.miss']
        tot_h = max(my0 + mh, kbot + 90) - TOP
        sc.put('pair.div', [R('pair/div', LX0 + HWL + GX_ / 2 - 0.6, TOP + 8, 1.2, tot_h - 16, fill=LINE2, line=None)])
        kwbox = union([sc.box[k_] for k_ in kw_keys])
        embbox = union([sc.box[k_] for k_ in emb_keys])
        e1 = {'emb.qv': dict(kind='wipe_in', dir='left', delay=0, dur=320)}
        return dict(kw=kw_keys, emb=emb_keys, beats=[{'kw.hl': dict(kind='wipe_in', dir='left', delay=0, dur=260)}, k2, k3, e1, e2, e3, e4],
                    kwbox=kwbox, embbox=embbox, box=union([kwbox, embbox]), div='pair.div', zmax=PR.get('zmax', 1.3))

    # -------------------------------------------------------------- 1 더미: 이야기 기록도 작은 조각으로, 아무 데나 흩어짐(옅게) → 몇 개만 켜짐
    cap_c = dict(t=CP['cloud'])
    _, _, ccw, cch = cap_measure(cap_c, 'top')
    CB = tuple(spec.get('cloud_box', CLOUD_BOX))
    ccam, ccrect = frame(CB, 'top', 0.9, ccw, cch)
    cx_, cy_, cz, cvx, cvy = ccam

    def W(sx, sy):
        return ((sx - cvx) / cz + cx_, (sy - cvy) / cz + cy_)
    vx0, vy0 = W(58, 114)            # 화면 가장자리에서 조금 떨어지게(8차: 왼·오른·아래 여백을 늘림, 위 띠와도 떨어짐)
    vx1, vy1 = W(1222, 676)
    ax0, ay0 = W(ccrect[0] - 30, ccrect[1] - 16)
    ax1, ay1 = W(ccrect[0] + ccrect[2] + 30, ccrect[1] + ccrect[3] + 22)
    fills = list(spec.get('fill', [])) + EXTRA
    fills = fills[:max(0, spec.get('n_cloud', 26) - len(keys))]
    IXS = spec.get('index')
    ext = {}       # 00판: 조각 → (벡터 숫자, 메타데이터 줄, 글자 크기, 폭, 높이)
    if IXS:
        pool = ['2026-03-02', '2026-03-05', '2026-03-07', '2026-03-09', '2026-03-11', '2026-03-13', '2026-03-16', '2026-03-17',
                '2026-03-18', '2026-03-19', '2026-03-21', '2026-02-26', '2026-02-28', '2026-03-01', '2026-03-03', '2026-03-06']

        def _ext(seed, date, app, pt):
            vt, ml = vec_text(seed), meta_text(date, app)
            lh = pt * 4 / 3 + 3
            return (vt, ml, pt, max(tw(x, pt, 'sb') for x in [vt] + ml) + 10, lh * (1 + len(ml)))
        for k in keys:
            c = REC[k]
            app = APP_OF.get(c['kind'], 'kakaotalk')
            date = iso_date(c.get('meta', ''), with_time=c['kind'] == 'photo') or pool[0]
            ext['cl.' + k] = _ext(''.join(c.get('lines', ())) + c['title'] + c.get('meta', ''), date, app, IXS.get('pt_key', 12.5))
        for i, (ic, t, m) in enumerate(fills):
            date = iso_date(t + ' ' + m, with_time=ic == 'gallery') or pool[i % len(pool)]
            ext['f%d' % i] = _ext(t + m, date, APP_OF.get(ic, ic), IXS.get('pt_fill', 9))
    def _wh(key, fw):
        if key not in ext:
            return fw, S.FRAG_H
        return max(fw, ext[key][3] + 6), S.FRAG_H + 6 + ext[key][4]
    items = [('cl.' + k,) + _wh('cl.' + k, S.frag_w(REC[k]['title'], chip_text(REC[k]))) for k in keys]
    fitems = [('f%d' % i,) + _wh('f%d' % i, S.frag_w(t, m)) for i, (_, t, m) in enumerate(fills)]
    import random
    random.Random(spec.get('seed', 11)).shuffle(items)
    random.Random(spec.get('seed', 11) + 1).shuffle(fitems)
    items += fitems                  # 조각이 커져 자리가 빠듯하니 이야기 기록부터 자리 잡게(빠지면 안 됨)
    cpos = scatter(items, (vx0, vy0, vx1, vy1), [(ax0, ay0, ax1 - ax0, ay1 - ay0)], spec.get('seed', 11) + 3)
    cloud = []
    zoom_k = (spec.get('index') or {}).get('key', hops[0]['target']) if spec.get('index') else None
    for k in keys:
        if 'cl.' + k in cpos:
            x, y = cpos['cl.' + k]
            pr_ = frag_at(k, k, x, y)
            sc.put('cl.' + k, pr_ if k == zoom_k else [G('cl.%s/g' % k, pr_)])
            sc.box['cl.' + k] = (x, y, S.frag_w(REC[k]['title'], chip_text(REC[k])), S.FRAG_H)
            cloud.append('cl.' + k)
    fill_keys = []
    for i, (ic, t, m) in enumerate(fills):
        if 'f%d' % i in cpos:
            x, y = cpos['f%d' % i]
            sc.put('f%d' % i, [G('f%d/g' % i, card_prims('f%d' % i, 'frag', x, y, None, t, m, icon=ic)[0])])
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
        sc.put('lit.' + k, [G('lit.%s/g' % k, frag_at('lit.' + k, k, x, y, style='weave'))])
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
                                         'Hop %d  %s' % (n, '다시 쓴 질문' if n > 1 else '첫 질문'), token, rest, cond, 're',
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
            # 사진마다 저장해 둔 메타데이터의 날짜(00과 같은 형식). 필터는 이 날짜로 거름
            for r in list(fk) + list(f.get('drop', {})):
                c = REC[r]
                bx_, by_, bw_, bh_ = sc.box[r]
                txt = 'date: "%s"' % iso_date(c.get('meta', ''), with_time=c['kind'] == 'photo')
                pos_ = (bx_ + 8, by_ + bh_ + 6, txt, 9.5, 'sb')
                sc.put('pmeta.' + r, [T('pmeta.%s/t' % r, bx_ + 8, by_ + bh_ + 6, bw_, 18, txt, size=9.5, color=SUB, weight='sb')])
                if r in fk and f.get('date'):
                    sc.put('pmk%d.%s' % (n, r), [R('pmk%d.%s/0' % (n, r), *band(pos_, f['date'], kind='full'), prst='roundRect', radius=2.5,
                                                   fill=HL, alpha=34, line=None)])
            x0 = min(sc.box[k][0] for k in fk) - 14
            y0 = min(sc.box[k][1] for k in fk) - 18
            x1 = max(sc.box[k][0] + sc.box[k][2] for k in fk) + 14
            y1 = max(sc.box[k][1] + sc.box[k][3] for k in fk) + 14 + (26 if f.get('date') else 0)
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
                sc.put('qans.ok', chip_prims('qans.ok', sc.X0, sc.ans_y + 30, sc.spec.get('stop_label', '탐색 끝'), style='soft', pt=9, h=21, padx=8)[0])
            else:
                sc.put('qans.ok', chip_prims('qans.ok', okx, sc.ans_y + 1, sc.spec.get('stop_label', '탐색 끝'), style='soft', pt=9, h=21, padx=8)[0])
        else:
            sc.put('tok%d@q' % n, chip_prims('tok%d' % n, sc.X0, sc.row_y(n + 1) - 1, lab, style='fill', pt=10, h=23, padx=9)[0])
        H.append(h)

    # -------------------------------------------------------------- Weave 한눈에: 질문과 답 사이 빠진 한 단계 → 단서로 채움(클릭마다 추론 → 멀티홉 → 키워드)
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
        qx = mx0 - HY.get('gap1', 118) - qw
        sc.put('hy.q', [R('hq/bg', qx, cyc - 22, qw, 44, prst='roundRect', fill='FFFFFF', line=LINE2, line_w=1.2, shadow=S.L.SHADOW_SOFT),
                        R('hq/lens', qx + 17, cyc - 8, 12, 12, prst='ellipse', fill=None, line='9AA0A6', line_w=1.6),
                        R('hq/lens2', qx + 26, cyc + 3, 6, 2, fill='9AA0A6', line=None),
                        T('hq/t', qx + 38, cyc - 22, qw - 44, 44, qt, size=10.5, color=INK, weight='m', anchor='ctr')])
        ca = REC[ansk]
        aimg_h = HY.get('img_h', 84)
        ah = card_at(ansk, 0, 0, img_h=aimg_h)[1]
        ax0 = mx0 + mw0 + HY.get('gap2', 170)
        ay0 = cyc - ah / 2
        apr, ah, apos = card_at(ansk, ax0, ay0, img_h=aimg_h)
        sc.put('hy.ans', apr)
        # 빠진 한 단계(점선 자리 + ?), 회색 점선으로 질문과 답이 끊겨 있음
        sc.put('hy.gap', [R('hgap/r', mx0, my0_, mw0, mh0, prst='roundRect', radius=12, fill='FBFAFF', line=GRAY_LINE, line_w=1.6, dash='dash'),
                          T('hgap/q', mx0, my0_ + 8, mw0, 40, '?', size=22, color=GRAY_LINE, weight='b', align='c', anchor='ctr'),
                          T('hgap/t', mx0, my0_ + mh0 - 34, mw0, 22, HY.get('gap_label', '빠진 한 단계'), size=10, color=SUB, weight='sb',
                            align='c', anchor='ctr')])
        sc.put('hy.dash', [C('hdash/1', scurve((qx + qw + 2, cyc), (mx0 - 2, cyc), 0.5), w=1.5, color=GRAY_LINE, dash='sysDash'),
                           C('hdash/2', scurve((mx0 + mw0 + 2, cyc), (ax0 - 2, cyc), 0.5), w=1.5, color=GRAY_LINE, dash='sysDash')])
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

        def hlab(name, cx, y, title, desc):
            """이름표: 보라 테두리 알약(이름) + 옆에 짧은 설명."""
            pw = tw(title, 10, 'b') + 24
            dw = tw(desc, 10.5, 'sb') + 4
            x = cx - (pw + 10 + dw) / 2
            sc.put(name, chip_prims(name + '/p', x, y, title, style='outline', pt=10, h=26, padx=12)[0] +
                   [T(name + '/d', x + pw + 10, y, dw + 4, 26, desc, size=10.5, color=INK2, weight='sb', anchor='ctr')])
        (l1, d1), (l2, d2), (l3, d3) = HY['labels']
        hlab('hy.l1', mx0 + mw0 / 2, my0_ - 38, l1, d1)
        hlab('hy.l2', tmx, max(my0_ + mh0, ay0 + ah) + 20, l2, d2)
        hlab('hy.l3', acx, ay0 - 38, l3, d3)
        static = ['hy.q', 'hy.ans', 'hy.dash', 'hy.gap']
        b1 = {'hth1': dict(kind='wipe_in', dir='left', delay=0, dur=260), mid: dict(kind='zoom_in', delay=180, dur=240),
              'hy.mk1': dict(kind='wipe_in', dir='left', delay=480, dur=240), 'hy.l1': dict(kind='fade_in', delay=560, dur=200)}
        b2 = {'hth2': dict(kind='wipe_in', dir='left', delay=0, dur=260), 'htok': dict(kind='zoom_in', delay=200, dur=220),
              'hy.l2': dict(kind='fade_in', delay=380, dur=200)}
        b3 = {'hy.mk2': dict(kind='wipe_in', dir='left', delay=0, dur=240), 'hy.l3': dict(kind='fade_in', delay=120, dur=200),
              'hth3': dict(kind='wipe_in', dir='down', delay=420, dur=200), 'hans': dict(kind='zoom_in', delay=560, dur=220)}
        HYB = dict(static=static, built=['hth1', 'hth2', 'hth3', mid, 'hy.mk1', 'hy.l1', 'htok', 'hy.l2', 'hy.mk2', 'hy.l3', 'hans'],
                   beats=[b1, b2, b3], mid=mid,
                   box=union([sc.box[k_] for k_ in static + ['hy.l1', 'hy.l2', 'hy.l3', 'hans']]), zmax=HY.get('zmax', 1.3))

    # -------------------------------------------------------------- 00 사전 준비(00판): 떠 있는 모든 기록 아래에 벡터(숫자) + 메타데이터(실제 형식), 그다음 기록 하나를 가까이
    IX = spec.get('index')
    IXD = None
    if IX:
        ik = IX.get('key', hops[0]['target'])
        items_ = [x for x in cloud + fill_keys if x in ext]
        strips, dates, b1, b2 = [], [], {}, {}
        for j, it in enumerate(items_):
            bx, by, bw, bh = sc.box[it]
            vt, ml, pt, ew, eh = ext[it]
            lh = pt * 4 / 3 + 3
            key_ = it.startswith('cl.')
            sc.put('vs.' + it, [T('vs.%s/t' % it, bx + 8, by + bh + 6, ew + 6, lh, vt, size=pt, color=PURPLE2, weight='sb',
                                  anchor='ctr')])
            sc.put('vm.' + it, [T('vm.%s/t' % it, bx + 8, by + bh + 6 + lh, ew + 6, lh * len(ml), ml, size=pt,
                                  color=INK2 if key_ else SUB, weight='sb', lnspc=lh * 0.75)])
            strips.append('vs.' + it)
            dates.append('vm.' + it)
            b1['vs.' + it] = dict(kind='fade_in', delay=min(16 * j, 320), dur=220)
            b2['vm.' + it] = dict(kind='fade_in', delay=min(14 * j, 280), dur=220)
        # 기록 하나를 가까이: 조각 → 카드, 그 아래 벡터·메타데이터 글은 '기기 안에 저장한 모습'의 같은 줄로 날아감(같은 이름)
        ck = REC[ik]
        x0_, y0_ = cpos['cl.' + ik]
        cpr, ch_, _ = card_at(ik, x0_, y0_)
        sc.put('ix.card', cpr)
        vt_k, ml_k, _, _, _ = ext['cl.' + ik]
        vlong = vt_k[:-4] + ', ' + vec_text(ck['title'] + ck.get('meta', '') + 'more', 3)[1:]     # 같은 숫자로 시작해 몇 개 더
        mone = ml_k[0] + ' ' + ml_k[1].strip()                                      # 한 줄로
        PT = 11
        EWD = max(IX.get('entry_w', 440), 104 + max(tw(vlong, PT, 'sb'), tw(mone, PT, 'sb'), tw(IX.get('text', ''), 9.5)) + 26)
        EH = 156
        ex0 = x0_ + ck['w'] + 78
        ey0 = y0_ + ch_ / 2 - EH / 2
        ent = [R('ixe/bg', ex0, ey0, EWD, EH, prst='roundRect', radius=16, fill='FFFFFF', line=RING, line_w=1.6, shadow=S.L.SHADOW_CARD,
                 glow=(8, RING, 22)),
               P('ixe/ic', S.ICON['spool'], ex0 + 16, ey0 + 13, 18, 18),
               T('ixe/h', ex0 + 40, ey0 + 11, 260, 22, IX.get('entry_title', '기기 안에 저장한 모습'), size=10, color=PURPLE2, weight='b',
                 anchor='ctr')]
        LX_, VX_ = ex0 + 18, ex0 + 104
        rows_y = [ey0 + 48, ey0 + 82, ey0 + 116]
        for j, lab_ in enumerate(['글자', '벡터', '메타데이터']):
            ent.append(T('ixe/l%d' % j, LX_, rows_y[j], 84, 24, lab_, size=9.5, color=PURPLE if j else MUTE, weight='b', anchor='ctr'))
        ent.append(T('ixe/v0', VX_, rows_y[0], EWD - (VX_ - ex0) - 14, 24, IX.get('text', ''), size=9.5, color=MUTE, anchor='ctr'))
        sc.put('ix.entry', ent)
        sc.put('ix.vec', [T('vs.cl.%s/t' % ik, VX_, rows_y[1], EWD - (VX_ - ex0) - 10, 24, vlong, size=PT, color=PURPLE2, weight='sb',
                            anchor='ctr')])
        sc.put('ix.meta', [T('vm.cl.%s/t' % ik, VX_, rows_y[2], EWD - (VX_ - ex0) - 10, 24, mone, size=PT, color=INK2, weight='sb',
                             anchor='ctr')])
        sc.put('ixth', S.thread_prims('ixth', scurve((x0_ + ck['w'] + 2, y0_ + ch_ / 2), (ex0 - 2, ey0 + EH / 2), 0.5)))
        close = ['ixth', 'ix.card', 'ix.entry', 'ix.vec', 'ix.meta']
        IXD = dict(key=ik, strips=strips, dates=dates, beats=[b1, b2], close=close, box1=union([sc.box[k_] for k_ in close]))

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
             cap_y=None, cap_x=None, alpha=None, beats=None, cap_beat=None):
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
                             alpha=dict(alpha or {}), beats=list(beats or []), cap_beat=cap_beat))

    def cx_of(k):
        b = sc.box[k]
        return b[0] + b[2] / 2

    def cy_of(k):
        b = sc.box[k]
        return b[1] + b[3] / 2

    ui_base = ['ui'] + (['ui.glogo', 'ui.sbox'] if kind == 'google' else ['ui.head', 'ui.msg']) + ['ui.kbd', 'ui.keys']
    D = lambda *s_: set(s_)   # noqa: E731
    if kind == 'google':
        ob = union([sc.box['ui.sbox'], (PX + 20, PY + 40, PW - 40, 50)])
    else:
        hb = union([sc.box['ui.head'], sc.box['ui.msg']])
        ob = (PX + 4, hb[1], PW - 8, hb[3])
    all_cloud = cloud + fill_keys
    order = list(all_cloud)
    random.Random(spec.get('seed', 11) + 1).shuffle(order)
    float_in = {k: dict(kind='zoom_in', delay=min(20 * j, 480), dur=220) for j, k in enumerate(order)}   # 0.7초 안에 모두

    def open_step():
        """상황: 폰 위쪽(질문)을 가까이."""
        show(*ui_base)
        shot('open', [], 'right', set(ui_base), {}, 2.1, frame_box=ob, morph=1500)
        hide(*ui_base)

    phone_now = []

    def trig_step():
        nonlocal phone_now
        # 01 순간 감지: 버튼은 클릭에
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
        shot('trig', [], 'right', set(ui_base + trig), dict(cur='01'), 2.0, frame_box=tb_, cap_y=sc.ui['ky'] + 22, morph=1500,
             beats=[{k: dict(kind='rise' if k == 'ui.sheet' else 'zoom_in', delay=(250 if k == 'ui.sheet' else 120 * j), dur=220)
                     for j, k in enumerate(trig)}])
        hide('ui.tap')
        phone_now = [x for x in cur if x == 'ui' or x.startswith('ui.')]
        hide(*phone_now)

    if IXD:
        # 1 기록 더미가 먼저: 매일 쌓이는 기록들
        show(*all_cloud)
        ca_ = {k: IX.get('cloud_alpha', 72) for k in all_cloud}
        shot('cloud', [], 'top', set(all_cloud), {}, 0.9, frame_box=CB, alpha=ca_, anim=float_in)
        # 2 00 사전 준비: 모든 기록 아래에 벡터 줄(클릭), 날짜(클릭)
        show(*IXD['strips'], *IXD['dates'])
        shot('idx1', [], 'top', set(all_cloud + IXD['strips'] + IXD['dates']), {}, 0.9, frame_box=CB, alpha=ca_, morph=800,
             cap=CP['idx1'], notes=NT['idx1'], beats=IXD['beats'])
        # 3 기록 하나를 가까이: 조각이 카드로, 그 벡터 줄은 '기기 안에 저장한 모습'의 벡터 줄로
        hide(*all_cloud, *IXD['strips'], *IXD['dates'])     # 다른 조각은 걷음(가까이 볼 때 흐린 벡터 줄이 떠 보이지 않게)
        show(*IXD['close'])
        shot('idx2', [], 'top', set(IXD['close']), {}, IX.get('z1', 1.6), frame_box=IXD['box1'], cap=CP['idx2'], notes=NT['idx2'],
             morph=1500)
        hide(*IXD['close'])
        # 4 질문의 순간
        open_step()
    else:
        open_step()
        show(*all_cloud, *lits)
        t_end = min(20 * len(order), 480) + 260
        shot('cloud', [], 'top', set(all_cloud + lits), {}, 0.9, frame_box=CB, morph=1500,
             alpha={k: CLOUD_ALPHA for k in all_cloud},
             anim=dict(float_in, **{x: dict(kind='zoom_in', delay=t_end + 150 * j, dur=220) for j, x in enumerate(lits)}))
        hide(*lits, *all_cloud)
    if spec.get('trig_first'):
        trig_step()
    # 실패: 키워드 검색(왼쪽, 클릭마다) → 임베딩 검색(오른쪽, 클릭마다) → 둘을 나란히
    prev = []
    if PAIR:      # 키워드(왼쪽)와 임베딩(오른쪽)을 한 장에. 맺음 설명은 마지막 클릭에
        show_under(PAIR['div'])
        show(*PAIR['kw'], *PAIR['emb'])
        shot('fail', [], 'top', set(PAIR['kw'] + PAIR['emb'] + [PAIR['div']]), dict(done={'01'}) if spec.get('trig_first') else {}, PAIR['zmax'], frame_box=PAIR['box'], morph=1500,
             beats=PAIR['beats'] + [{}], cap_beat=len(PAIR['beats']))
        prev = PAIR['kw'] + PAIR['emb'] + [PAIR['div']]
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
        shot(P_['skey'], [], 'top', foc, {}, 1.45, frame_box=fb, alpha=al, morph=1500,
             beats=[dict({t_: dict(kind='wipe_in', dir='left', delay=80 * i, dur=240) for i, t_ in enumerate(P_['ths'])},
                         **{m_: dict(kind='wipe_in', dir='left', delay=200 + 80 * i, dur=240) for i, m_ in enumerate(P_['mks'])}),
                    dict({t_: dict(kind='zoom_in', delay=80 * i, dur=200) for i, t_ in enumerate(P_['tgs'])},
                         **({'miss': dict(kind='fade_in', delay=150, dur=240)} if last_pass else {}))])
        prev = [P_['pk']] + P_['rs'] + P_['ths'] + P_['rks'] + P_['tgs'] + P_['mks'] + extra
    if HYB:       # Weave 한눈에: 빠진 한 단계 → 추론 → 멀티홉 → 키워드(클릭마다)
        hide(*prev)
        prev = []
        styles[HYB['mid']] = 'weave'
        show_under('hy.dash', 'hth1', 'hth2', 'hth3')
        show('hy.gap', 'hy.q', 'hy.ans', HYB['mid'], 'hy.mk1', 'hy.l1', 'htok', 'hy.l2', 'hy.mk2', 'hy.l3', 'hans')
        shot('hybrid', [], 'top', set(HYB['static'] + HYB['built']), dict(done={'01'}) if spec.get('trig_first') else {}, HYB['zmax'], frame_box=HYB['box'], morph=1500, beats=HYB['beats'])
        hide('hy.dash', 'hth1', 'hth2', 'hth3', 'hy.gap', 'hy.q', 'hy.ans', HYB['mid'], 'hy.mk1', 'hy.l1', 'htok', 'hy.l2', 'hy.mk2', 'hy.l3',
             'hans')
        styles.pop(HYB['mid'], None)
    hide(*prev, *all_cloud)
    if not spec.get('trig_first'):
        trig_step()
    # 02 Query Rewriting: 처음 질문(정적) → 첫 질문(클릭) → 빈칸이 있는 둘째 질문(클릭)
    qrows = ['q%d' % i for i in range(1, nh + 1)]
    qkeys = ['qp', 'qp.head', 'qorig'] + qrows + ['qans', 'qans.slot']
    styles['q1'] = 'cur'
    show(*qkeys)
    shot('split', ['qp'], 'right', set(qkeys), dict(cur='02', done=D('01')), 1.9, morph=1500,
         beats=[{x: dict(kind='zoom_in', delay=0, dur=220)} for x in qrows])
    # 03 연쇄 탐색: 질문 판은 왼쪽에 그대로 두고, 오른쪽에서 찾기 → 이어지는 기록 → 근거와 단서(마지막 홉은 답).
    # 다음 홉으로 넘어갈 때 단서 칩이 질문 판의 빈칸으로 날아가 질문이 다시 써짐(모핑)
    qp_box = sc.box['qp']
    hop_shown = []
    for h in H:
        n, hop = h['n'], h['hop']
        f = hop.get('filter')
        k = hop['target']
        cands = h['cands']
        k_re = re_key(n)
        hc = CP['hops'][n - 1]
        hn = NT['hops'][n - 1]
        if n > 1:
            pv = H[n - 2]
            hide(*hop_shown)
            styles.pop(pv['target'], None)
            show('tok%d@q' % (n - 1))
            styles['q%d' % (n - 1)] = 'done' + ('_rw' if n > 2 else '')
            styles['q%d' % n] = 'cur_rw'
        whys = ['why%d.%s' % (n, c) for c in cands]
        drops = ['drop%d.%s' % (n, x) for x in f.get('drop', {})] if f else []
        drop_recs = list(f.get('drop', {})) if f else []
        keep_other = [x for x in (f['keep'] if f else []) if x != k and x not in cands]
        recs = [k] + cands + keep_other + drop_recs
        pmeta = [('pmeta.' + x) for x in recs if ('pmeta.' + x) in sc.items] if f else []
        pmks = [x for x in ('pmk%d.%s' % (n, r) for r in (f['keep'] if f else [])) if x in sc.items]
        tbx_ = sc.box[k]
        sc.put('tring%d' % n, [R('tring%d/r' % n, tbx_[0] - 3, tbx_[1] - 3, tbx_[2] + 6, tbx_[3] + 6, prst='roundRect', radius=14,
                                 fill=None, line=RING, line_w=2.4, glow=(10, RING, 28))])
        pills = ['pl%d.%s' % (n, x) for x in hop.get('pills', {})]
        ev = [x for x in ('hm%d' % n, 'im%d' % n, 'pm%d' % n) if x in sc.items]
        tok = 'tok%d@src' % n
        threads = ['th%d' % n] + ['thc%d.%s' % (n, c) for c in cands] + (['fb%d' % n] if f else [])
        show(k_re, *recs, *pmeta)
        show_under(*threads)
        show(*whys, *drops, *pmks, 'tring%d' % n, *pills, *ev, tok)
        shown_now = [k_re] + recs + pmeta + threads + whys + drops + pmks + ['tring%d' % n] + pills + ev + [tok]
        hop_shown = shown_now
        b_rec = ({k: dict(kind='fade_in', delay=0, dur=200)} if not f else {})
        if not f:
            b_rec.update({c: dict(kind='fade_in', delay=80 + 80 * j, dur=200) for j, c in enumerate(cands)})
        b_cand = dict({'thc%d.%s' % (n, c): dict(kind='wipe_in', dir='left', delay=(250 if not f else 0) + 100 * j, dur=260)
                       for j, c in enumerate(cands)},
                      **{w_: dict(kind='zoom_in', delay=(450 if not f else 220) + 100 * j, dur=200) for j, w_ in enumerate(whys)})
        b_hit = {'th%d' % n: dict(kind='wipe_in', dir='left', delay=0, dur=320), 'tring%d' % n: dict(kind='zoom_in', delay=260, dur=220)}
        b_ev = dict({x: dict(kind='wipe_in', dir='left', delay=(220 if x.startswith('pm') else 0), dur=300) for x in ev},
                    **{x: dict(kind='zoom_in', delay=100 * j, dur=200) for j, x in enumerate(pills)})
        b_ev[tok] = dict(kind='zoom_in', delay=520, dur=240)
        if f:
            b_f = dict({'fb%d' % n: dict(kind='fade_in', delay=0, dur=240)},
                       **{x: dict(kind='wipe_in', dir='left', delay=180, dur=240) for x in pmks},
                       **{x: dict(kind='zoom_in', delay=300 + 100 * j, dur=200) for j, x in enumerate(drops)})
            beats_ = [b_f, dict(b_cand, **{kk: dict(v, delay=v['delay'] + 450) for kk, v in b_hit.items()}), b_ev]
        else:
            beats_ = [dict(b_rec, **b_cand), b_hit, b_ev]
        hud3 = dict(cur='03', done=D('01', '02'), **({'loop': n, 'loop_on': True} if n > 1 else {}))
        frame_keys = ['qp'] + [x for x in shown_now if x in sc.box and not x.startswith(('th', 'fb'))] + (['fb%d' % n] if f else [])
        hb = union([sc.box[x] for x in frame_keys])
        dim_c = {c: 45 for c in cands}
        dim_c.update({x: 45 for x in drop_recs})
        shot('hop%d' % n, [], 'top', set(shown_now) | set(qkeys) | {'tok%d@q' % (n - 1)} if n > 1 else set(shown_now) | set(qkeys), hud3,
             1.3, cap=hc['find'], notes=hn.get('hop') or ' '.join(x for x in (hn.get('rw'), hn.get('find'), hn.get('close')) if x), frame_box=hb, morph=1500, beats=beats_, alpha=dim_c,
             half=cands + ['thc%d.%s' % (n, c) for c in cands] + drop_recs)
    hide(*hop_shown)
    for h in H:
        styles.pop(h['target'], None)
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
    show(*qkeys, *sum_keys, *sth, *['tok%d@q' % h['n'] for h in H], 'qans.ok')
    hide('qans.slot')
    for i in range(1, nh + 1):
        styles['q%d' % i] = 'done' + ('_rw' if i > 1 else '')
    toks = ['tok%d@q' % h['n'] for h in H]
    sum_cap = dict(t=CP['sum'], pill=CP.get('sum_pill', '모두 기기 안에서'))
    shot('sum', ['qp'] + sum_keys, 'top', set(['qp', 'qorig', 'qans', 'qans.ok'] + qrows + toks + sum_keys + sth),
         dict(done=D('01', '02', '03')), 1.45, cap=sum_cap,
         anim=dict({x: dict(kind='wipe_in', dir='left', delay=150 + 180 * j, dur=260) for j, x in enumerate(sth)},
                   **{'qans.ok': dict(kind='zoom_in', delay=200 + 180 * len(sth), dur=200)}), morph=1500)
    # 04 전달: 카드를 가까이. 카드가 열리면 빨간 배지는 사라지고, 자판은 내려감
    hide(*qkeys, *sum_keys, *sth, *toks, 'qans.ok')
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
        sb = sc.box['ui.sbox']
        if sc.box['ans'][1] < sb[1] + sb[3] + 8:      # 카드가 검색창에 닿으면 검색창을 올림(구글 로고 자리)
            styles['ui.sbox'] = 'up'
            sb = bbox(sc.items['ui.sbox']('up'))
            hide('ui.glogo')
        db = union([sb, sc.box['ans'], sc.box['ui.kbd']])
        dfocus = ui_base + ['ans', 'ui.tap2', 'ui.on']
    else:
        db = union([sc.box['ans'], sc.box['ui.kbd']])
        dfocus = ui_base + ['ans', 'ui.tap2', 'ui.on']
    shot('deliver', [], 'right', set(dfocus), dict(cur='04', done=D('01', '02', '03')), 2.3, frame_box=db, cap_y=cy_of('ans'),
         anim={'ans': dict(kind='rise', delay=0, dur=260)}, beats=[{'ui.tap2': dict(kind='zoom_in', delay=0, dur=200)}], morph=1500)
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
    shot('result', [], 'right', set(ui_base + res_keys), dict(cur='04', done=D('01', '02', '03')), 1.5, frame_box=rb, morph=1500)
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
