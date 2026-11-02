"""v3 장면 틀 — 시나리오 하나(SPEC) → 모핑으로 이어지는 장면 20장 안팎.

바뀐 점(v2 대비, 2026-11-01 피드백)
- 고정 머리(칩·제목·부제) 없음. 설명은 장면마다 비어 있는 쪽(왼쪽·오른쪽·위·아래)에 놓고, 카메라는 그 자리를 비워 두고 비춘다.
- 위에 'HOW IT WORKS' + 5단계 파이프라인 띠가 처음부터 있고, Weave 차례가 되면 사전 준비부터 하나씩 켜진다.
- 쓰지 않는 기록은 확실히 흐리게(17%). 지금 보는 곳에만 보라 형광펜·실·토큰.
- 왼쪽 열 = 질문을 어떻게 다루나: 지금의 검색(검색창 + 일반 임베딩: 질문 하나 → 비슷한 기록) ↔
  Weave(탐색 메모 + Reasoning Embedding: 질문 + 지금 단서 → 이어지는 기록). 단서는 형광펜에서 토큰이 되어 메모와 다음 검색 칸으로 간다.
- 화면 세 가지: google(키보드로 구글 검색) · sheet(기록 통합 검색) · gps(위치가 바뀌면 먼저 건네기).
"""
from dataclasses import dataclass, field

import hiw_lib as L
import story as S
from story import (BODY, GRAY_FILL, GRAY_HL, GRAY_LINE, HL, INK, INK2, LAV, LAV2, LINE, LINE2, MUTE, PURPLE, PURPLE2,
                   RING, SUB, C, P, R, T, band, card_prims, chip_prims, scurve, tw, vcurve)

VIEW = (40, 84, 1240, 708)          # 카메라가 비추는 화면(위 띠 아래)
CAP_W = 380                         # 왼쪽·오른쪽 설명 폭


@dataclass
class Step:
    cap: dict
    cam: tuple
    show: list
    focus: object = None
    styles: dict = field(default_factory=dict)
    hud: dict = field(default_factory=dict)
    anim: dict = field(default_factory=dict)
    notes: str = ''
    morph_ms: int = 1300
    half: set = field(default_factory=set)


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


# ------------------------------------------------------------------ 글줄 나누기
# 줄 길이를 고르게 나누되, 조사·어미·쉼표 뒤에서 끊는 쪽을 고름('다음 / 검색'처럼 꾸밈말 뒤는 피함). '\n'은 그 자리에서 줄바꿈.
GOOD_END = ('이', '가', '은', '는', '을', '를', '에', '엔', '도', '만', '로', '고', '서', '면', '데', '요', '려', '며', '어', '아',
            '해', '지만', '께', '부터', '까지', '처럼', '보다', '마다', '에게', '한테', '지', '자', '게', '야', '나')


BOUND = {'수', '것', '것이', '것을', '것은', '게', '건', '줄', '뿐', '듯', '때'}


def _brk_cost(word, nxt=None):
    t = ''.join(x for x, _ in word).rstrip('’”\'")')
    if nxt is not None and (''.join(x for x, _ in nxt) in BOUND or ''.join(x for x, _ in nxt).startswith('싶')):
        return 160
    if t and t[-1] in ',?!…':
        return -80
    return 0 if t.endswith(GOOD_END) else 120


def _segments(runs):
    """[(글자, 색)] → 강제 줄바꿈 단위 → 낱말 목록. 낱말 = [(글자, 색)]."""
    segs, cur = [[]], []
    for t, c in runs:
        for ch in t:
            if ch == '\n' or ch == ' ':
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
    from itertools import combinations
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
    """[(글자, 색)] → 줄마다 [(글자, 색)]."""
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
    """글자 하나 → 줄 목록."""
    return [''.join(t for t, _ in ln) for ln in wrap_runs([(text, None)], pt, width, weight)]


# ------------------------------------------------------------------ 위 띠
STAGES = [('00', '사전 준비'), ('01', '순간 감지'), ('02', '질문 다시 쓰기'), ('03', '연쇄 탐색'), ('04', '전달')]


def bar_layout():
    widths = [24 + 8 + tw(ko, 10.5, 'b') + 20 for _, ko in STAGES]
    gap = 28
    total = sum(widths) + gap * 4
    x = 740 - total / 2
    out = []
    for w in widths:
        out.append((x, w))
        x += w + gap
    return out


def topbar_prims(h):
    """h = dict(cur, done, loop, loop_on, all)."""
    y0, hh = 16, 40
    cw = tw('HOW IT WORKS', 10.5, 'sb') + 26 + 6
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
        if i < 4:
            out.append(T('top/a%d' % i, x + w + 3, y0, 22, hh, '→', size=10, color='C9C0E8', align='c', anchor='ctr'))
    if h.get('loop'):
        (x2, w2), (x3, w3) = lay[2], lay[3]
        a, b = (x3 + w3 / 2, y0 + hh - 1), (x2 + w2 / 2, y0 + hh - 1)
        on = h.get('loop_on')
        col = PURPLE if on else 'C9C0E8'
        out.append(C('top/loop', [a, (a[0], y0 + hh + 24), (b[0], y0 + hh + 24), b], w=2.2 if on else 1.5, color=col))
        out.append(T('top/loop_head', b[0] - 7, y0 + hh - 2, 14, 12, '▲', size=7, color=col, align='c', anchor='ctr'))
        lab = '찾은 단서로 질문 다시 쓰기' if on else '반복'
        lw_ = tw(lab, 8.5, 'b') + 16
        out.append(R('top/loop_bg', (a[0] + b[0]) / 2 - lw_ / 2, y0 + hh + 12, lw_, 18, prst='roundRect', fill='FFFFFF', line=None))
        out.append(T('top/loop_t', (a[0] + b[0]) / 2 - lw_ / 2, y0 + hh + 12, lw_, 18, lab, size=8.5, color=col, weight='b',
                     align='c', anchor='ctr'))
        out.append(R('top/cnt', x3 + w3 - 14, y0 - 6, 20, 20, prst='ellipse', fill=PURPLE, line='FFFFFF', line_w=1.5))
        out.append(T('top/cnt_t', x3 + w3 - 14, y0 - 6, 20, 20, str(h['loop']), size=8.5, color='FFFFFF', weight='b', align='c',
                     anchor='ctr'))
    return out


# ------------------------------------------------------------------ 설명(자유 배치)
def cap_region(side):
    x0, y0, x1, y1 = VIEW
    if side == 'right':
        return (x0, y0, 1240 - CAP_W - 40, y1), (1240 - CAP_W, y0, 1240, y1)
    if side == 'left':
        return (x0 + CAP_W + 40, y0, x1, y1), (x0, y0, x0 + CAP_W, y1)
    if side == 'top':
        return (x0, y0 + 118, x1, y1), (x0, y0 + 6, x1, y0 + 112)
    return (x0, y0, x1, y1 - 126), (x0, y1 - 120, x1, y1)


def caption_prims(i, cap):
    """cap = dict(t=[(글자, 색)], s='부제', side, badge) → (바탕 판, 글). 장마다 다른 이름 → 자리 옮길 때 겹쳐 사라지고 나타남."""
    side = cap.get('side', 'top')
    _, (rx0, ry0, rx1, ry1) = cap_region(side)
    nm = 'cap%d' % i
    out = []
    if side in ('left', 'right'):
        W = rx1 - rx0
        tl = wrap_runs(cap['t'], 22, W)
        sl = wrap(cap.get('s', ''), 12.5, W) if cap.get('s') else []
        bh = (30 if cap.get('badge') else 0) + len(tl) * 34 + (10 + len(sl) * 21 if sl else 0)
        y = (ry0 + ry1) / 2 - bh / 2 + cap.get('dy', 0)
        x = rx0
        if side == 'right':
            panel = [R(nm + '/bg', rx0 - 70, -80, 1280 - rx0 + 160, 900, fill='F9F7FF', alpha=93, line=None, soft=36)]
        else:
            panel = [R(nm + '/bg', -90, -80, rx1 + 160, 900, fill='F9F7FF', alpha=93, line=None, soft=36)]
        if cap.get('badge'):
            bw = tw(cap['badge'], 9.5, 'b') + 22
            out += [R(nm + '/bdg', x, y, bw, 24, prst='roundRect', fill=LAV, line=None),
                    T(nm + '/bdg_t', x, y, bw, 24, cap['badge'], size=9.5, color=PURPLE, weight='b', align='c', anchor='ctr')]
            y += 30
        out.append(T(nm + '/t', x, y, W + 20, len(tl) * 34, [[(t, {'color': c}) for t, c in ln] for ln in tl], size=22,
                     color=INK, weight='b', lnspc=25.5, spc=-0.3))
        y += len(tl) * 34 + 10
        if sl:
            out.append(T(nm + '/s', x, y, W + 20, len(sl) * 21, sl, size=12.5, color='5B5866', lnspc=15.5))
        return panel, out
    W = 1000
    tl = wrap_runs(cap['t'], 22, W)
    sl = wrap(cap.get('s', ''), 12.5, W) if cap.get('s') else []
    bh = (30 if cap.get('badge') else 0) + len(tl) * 34 + (8 + len(sl) * 21 if sl else 0)
    y = (ry0 + ry1) / 2 - bh / 2
    panel = [R(nm + '/bg', -90, -80, 1460, y + bh + 30 + 80, fill='F9F7FF', alpha=93, line=None, soft=36)]
    if cap.get('badge'):
        bw = tw(cap['badge'], 9.5, 'b') + 22
        out += [R(nm + '/bdg', 640 - bw / 2, y, bw, 24, prst='roundRect', fill=LAV, line=None),
                T(nm + '/bdg_t', 640 - bw / 2, y, bw, 24, cap['badge'], size=9.5, color=PURPLE, weight='b', align='c',
                  anchor='ctr')]
        y += 30
    out.append(T(nm + '/t', 140, y, 1000, len(tl) * 34, [[(t, {'color': c}) for t, c in ln] for ln in tl], size=22, color=INK,
                 weight='b', align='c', lnspc=25.5, spc=-0.3))
    y += len(tl) * 34 + 8
    if sl:
        out.append(T(nm + '/s', 140, y, 1000, len(sl) * 21, sl, size=12.5, color='5B5866', align='c', lnspc=15.5))
    return panel, out


# ------------------------------------------------------------------ 장면
class Scene:
    def __init__(self, spec):
        self.spec = spec
        self.items = {}
        self.box = {}
        self.pos = {}
        self.steps = []

    def put(self, key, prims_or_fn):
        fn = prims_or_fn if callable(prims_or_fn) else (lambda style=None, p=prims_or_fn: p)
        self.items[key] = fn
        self.box[key] = bbox(fn(None))

    def card(self, key, c):
        def fn(style=None, c=c, key=key):
            return card_prims(key, c['kind'], c['x'], c['y'], c['w'], c['title'], c.get('meta', ''), c.get('lines', ()),
                              img=c.get('img'), icon=c.get('icon'), style=style or 'base', img_h=c.get('img_h'))[0]
        _, h, pos = card_prims(key, c['kind'], c['x'], c['y'], c['w'], c['title'], c.get('meta', ''), c.get('lines', ()),
                               img=c.get('img'), icon=c.get('icon'), img_h=c.get('img_h'))
        c['h'] = h
        self.pos[key] = pos
        self.put(key, fn)

    def fit(self, keys, side='top', zmax=1.3, pad=24):
        (fx0, fy0, fx1, fy1), _ = cap_region(side)
        x0 = min(self.box[k][0] for k in keys)
        y0 = min(self.box[k][1] for k in keys)
        x1 = max(self.box[k][0] + self.box[k][2] for k in keys)
        y1 = max(self.box[k][1] + self.box[k][3] for k in keys)
        z = min(zmax, (fx1 - fx0) / (x1 - x0 + 2 * pad), (fy1 - fy0) / (y1 - y0 + 2 * pad))
        return ((x0 + x1) / 2, (y0 + y1) / 2, z, (fx0 + fx1) / 2, (fy0 + fy1) / 2)

    def step(self, keys, cap, side='top', zmax=1.3, pad=24, **kw):
        cap = dict(cap, side=side)
        self.steps.append(Step(cap=cap, cam=self.fit(keys, side, zmax, pad), **kw))


# ------------------------------------------------------------------ 왼쪽 열: 검색창·일반 임베딩 / 질문 다시 쓰기·Reasoning Embedding
# 2026-11-01 개편: 탐색 메모 대신 '질문 다시 쓰기'. 한 번에 안 풀리는 질문을 먼저 풀 질문과 그 답이 들어갈 질문으로 나누고,
# 앞에서 찾은 단서로 다음 질문의 빈자리('그날', '그때')를 채워 다시 쓴 뒤 그 질문으로 Reasoning Embedding 검색(Hi-Q의 정제→검색,
# EfficientRAG의 다음 홉 질의, MDR의 질문+앞 근거 재인코딩과 같은 방향). 다시 쓴 질문은 통째로 임베딩에 들어가고,
# 그 안의 날짜·시간처럼 정확한 조건은 필터로도 따로 건넨다(점선 갈래).
LX, LW = 60, 340
GEN_Y = 246
QY = 150                          # 질문 판 위쪽
CHIP_X = LX + 56                  # 띠 안에서 줄 이름 다음 자리
QB_W = LX + LW - 16 - CHIP_X      # 띠 안 질문 상자 폭
BAR_X = LX + LW - 16 - 61         # 숫자 막대 자리(아래 오른쪽)
ROW_H = 50                        # 하위 질문 한 줄(두 줄 글 + 틈)
RE_H = 146
GEN_H = 146


def fit_pt(text, maxw, pt=9.5, weight='b', lo=7.5):
    while tw(text, pt, weight) > maxw and pt > lo:
        pt -= 0.5
    return pt


def bars_prims(name, x, y, color, seed):
    """숫자 묶음(막대). 넣는 글이 바뀌면 높이가 바뀜(이름이 같아 모핑으로 변함)."""
    import hashlib
    hv = hashlib.md5(seed.encode('utf-8')).digest()
    out = []
    for i in range(9):
        hh = 20 * (0.3 + 0.68 * hv[i] / 255)
        out.append(R('%s%d' % (name, i), x + i * 7, y + 20 - hh, 4.5, hh, prst='roundRect', radius=1.5, fill=color, line=None))
    return out


def runs_of(t, base=INK):
    return [(t, base)] if isinstance(t, str) else list(t)


def plain(t):
    return t if isinstance(t, str) else ''.join(x for x, _ in t)


def qbox_prims(name, x, y, w, runs, pt=9.5, border=LINE2, fill='FFFFFF', h=46, mark=None):
    """띠 안 질문 상자(두 줄까지). mark = 칩처럼 칠할 글자(다시 쓴 단서·조건). 돌려줌: (원시 목록, 칠한 자리 또는 None)."""
    tl = wrap_runs(runs, pt, w - 18, 'sb')[:2]
    lh = pt * 4 / 3 + 4
    th = len(tl) * lh
    ty = y + (h - th) / 2 - 1
    out = [R(name + '/bg', x, y, w, h, prst='roundRect', radius=9, fill=fill, line=border, line_w=1.0)]
    mrect = None
    if mark:
        for j, ln in enumerate(tl):
            txt = ''.join(t for t, _ in ln)
            if mark in txt:
                # 글상자 안쪽 여백이 없으므로 실측 글리프 자리(story.band)와 같은 식으로 계산
                bx, by_, bw, bh = band((x + 9, ty + j * lh + 2, txt, pt, 'sb'), mark, kind='full')
                mrect = (bx - 3, by_ - 1, bw + 6, bh + 2)
                out.append(R(name + '/mk', *mrect, prst='roundRect', radius=5, fill='E6DEFF', line=None))
                break
    out.append(T(name + '/t', x + 9, ty, w - 12, th + 2, [[(t, {'color': c}) for t, c in ln] for ln in tl],
                 size=pt, color=INK, weight='sb', lnspc=lh * 0.75))
    return out, mrect


def re_prims(ry, ask, cond, mark=None):
    """Reasoning Embedding 띠: 다시 쓴 질문(통째로) → 숫자 → 이어지는 기록. 그 안의 정확한 조건은 점선 갈래로 필터에도."""
    out = [R('re/bg', LX, ry, LW, RE_H, prst='roundRect', radius=14, fill='FFFFFF', line=RING, line_w=1.6, shadow=S.L.SHADOW_CARD,
             glow=(8, RING, 22)),
           T('re/t', LX + 16, ry + 10, 300, 20, 'Reasoning Embedding', size=11, color=PURPLE, weight='b', anchor='ctr'),
           T('re/s', LX + 16, ry + 30, 320, 18, '다시 쓴 질문을 숫자로 바꿔, 이어지는 기록을 찾아요', size=9, color=SUB, anchor='ctr'),
           T('re/l', LX + 16, ry + 56, CHIP_X - LX - 18, 46, '질문', size=8.5, color=PURPLE, weight='b', anchor='ctr')]
    pr, mrect = qbox_prims('re/q', CHIP_X, ry + 56, QB_W, runs_of(ask), border=RING, mark=mark)
    out += pr
    if cond:
        cpt = fit_pt(cond, BAR_X - 30 - CHIP_X - 18, 9)
        out += [T('re/fl', LX + 16, ry + 110, CHIP_X - LX - 18, 26, '필터', size=8.5, color=PURPLE2, weight='b', anchor='ctr')]
        out += chip_prims('re/fc', CHIP_X, ry + 110, cond, style='dash', pt=cpt, h=26, padx=9)[0]
        if mrect:   # 질문 속 조건 → 필터 칸으로 내려가는 점선 갈래
            mx, my, mw, mh = mrect
            gx = CHIP_X - 8
            sy, ey = my + mh / 2, ry + 123
            out.append(C('re/split', [(mx - 1, sy), (gx + 2, sy), (gx, sy), (gx, sy + 10), (gx, sy + (ey - sy) / 2),
                                      (gx, ey - 10), (gx, ey - 4), (gx, ey), (gx + 2, ey), (CHIP_X - 1, ey)],
                         w=1.4, color=PURPLE2, dash='sysDash', tail='triangle'))
    # 질문 상자 → 숫자 막대(아래 오른쪽)
    out.append(C('re/arr', [(CHIP_X + QB_W - 24, ry + 103), (CHIP_X + QB_W - 24, ry + 116), (BAR_X - 16, ry + 122), (BAR_X - 5, ry + 122)],
                 w=1.4, color=PURPLE2, tail='triangle'))
    out += bars_prims('re/bar', BAR_X, ry + 112, PURPLE2, plain(ask) + '|' + (cond or ''))
    return out


def left_items(sc):
    sp = sc.spec
    hops = sp['hops']
    nh = len(hops)
    q = sp['word']['query']
    Sm = sp['sim']
    gi = Sm.get('input', q)

    # 지금 쓰는 검색: 검색창(모드 칩 + 검색어). 비슷한 것 찾기 때는 일반 임베딩에 넣는 글과 같게
    def qbox(style=None):
        mode = {'sim': '비슷한 것 찾기'}.get(style, '단어로 찾기')
        txt = gi if style == 'sim' else q
        mw = tw(mode, 9.5, 'b') + 22
        aw = LW - mw - 60
        return [R('qbox/bg', LX, 170, LW, 56, prst='roundRect', fill='FFFFFF', line=GRAY_LINE, line_w=1.2, shadow=S.L.SHADOW_CARD),
                R('qbox/mode', LX + 10, 181, mw, 34, prst='roundRect', fill='EFECF4', line=None),
                T('qbox/mode_t', LX + 10, 181, mw, 34, mode, size=9.5, color=SUB, weight='b', align='c', anchor='ctr'),
                (T('qbox/q', LX + mw + 22, 170, aw, 56, txt, size=fit_pt(txt, aw - 4, 13, 'm', 11), color=INK, weight='m', anchor='ctr')
                 if tw(txt, 11, 'm') <= aw - 4 else
                 T('qbox/q', LX + mw + 22, 170, aw, 56, wrap(txt, 10, aw - 6, 'm')[:2], size=10, color=INK, weight='m', anchor='ctr',
                   lnspc=13)),
                R('qbox/lens', LX + LW - 36, 189, 15, 15, prst='ellipse', fill=None, line=MUTE, line_w=2.0),
                R('qbox/lens2', LX + LW - 23, 203, 8, 2.2, fill=MUTE, line=None)]
    sc.put('qbox', qbox)

    # 일반 임베딩: 처음 질문 하나만 → 숫자 → 비슷한 기록(Reasoning Embedding 띠와 같은 꼴)
    lab = Sm.get('label', '질문')
    sub = Sm.get('gen_sub', '처음 질문 하나만 숫자로 바꿔, 비슷한 기록을 찾아요')
    gen = [R('gen/bg', LX, GEN_Y, LW, GEN_H, prst='roundRect', radius=14, fill='FFFFFF', line=GRAY_LINE, line_w=1.2, shadow=S.L.SHADOW_SOFT),
           T('gen/t', LX + 16, GEN_Y + 10, 220, 20, '일반 임베딩', size=11, color=SUB, weight='b', anchor='ctr'),
           T('gen/s', LX + 16, GEN_Y + 30, 320, 18, sub, size=9, color=MUTE, anchor='ctr'),
           T('gen/l', LX + 16, GEN_Y + 56, CHIP_X - LX - 18, 46, lab, size=8.5, color=MUTE, weight='b', anchor='ctr')]
    gen += qbox_prims('gen/in', CHIP_X, GEN_Y + 56, QB_W, [(gi, SUB)], border=GRAY_LINE, fill='F6F5F8')[0]
    gen.append(C('gen/arr', [(CHIP_X + QB_W - 24, GEN_Y + 103), (CHIP_X + QB_W - 24, GEN_Y + 116), (BAR_X - 16, GEN_Y + 122),
                             (BAR_X - 5, GEN_Y + 122)], w=1.4, color=MUTE, tail='triangle'))
    gen += bars_prims('gen/bar', BAR_X, GEN_Y + 112, 'B9B3C8', gi)
    sc.put('gen', gen)

    # Weave: 질문 다시 쓰기 판
    PH = 126 + nh * ROW_H + 44
    sc.QPH = PH
    sc.RE_Y = QY + PH + 18
    sc.put('qp', [R('qp/bg', LX, QY, LW, PH, prst='roundRect', radius=16, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=S.L.SHADOW_CARD),
                  P('qp/ic', S.ICON['spool'], LX + 16, QY + 13, 20, 20),
                  T('qp/title', LX + 42, QY + 12, 240, 22, '질문 다시 쓰기', size=11.5, color=PURPLE, weight='b'),
                  R('qp/div', LX + 16, QY + 44, LW - 32, 1, fill='EEE9FA', line=None),
                  R('qp/div2', LX + 16, QY + 116, LW - 32, 1, fill='EEE9FA', line=None)])
    ask = sp['ask']
    ol = wrap('“%s”' % ask['text'], 10, LW - 40, 'm')[:2]
    sc.put('qorig', [T('qorig/l', LX + 16, QY + 54, 220, 16, ask.get('label', '처음 질문'), size=8.5, color=MUTE, weight='b', anchor='ctr'),
                     T('qorig/t', LX + 16, QY + 72, LW - 30, 18 * len(ol), ol, size=10, color=INK, weight='m', lnspc=13.5)])
    X0, QW = LX + 44, LW - 44 - 14

    def row_y(i):
        return QY + 126 + (i - 1) * ROW_H

    sc.row_y = row_y

    def lines_after(text, lead):
        """앞자리(lead px)를 비운 첫 줄 + 다음 줄."""
        words = text.split(' ')
        first, rest = [], []
        for wd in words:
            cand = ' '.join(first + [wd])
            if not rest and (tw(cand, 10, 'm') <= QW - lead or not first):
                first.append(wd)
            else:
                rest.append(wd)
        return ' '.join(first), ' '.join(rest)

    def q_text(i, rw):
        hop = hops[i - 1]
        if i == 1:
            return None, hop['q']
        text = hop['q'][2] if (rw and len(hop['q']) > 2) else hop['q'][1]
        return hop['q'][0], text

    def gap_after(text):
        return 6 if text.startswith(' ') else 1      # 조사('을', '에')는 칩에 바짝

    def q_lines(i, rw):
        ph, text = q_text(i, rw)
        if ph is None:
            return lines_after(text.strip(), 0)
        cw = chip_prims('x', 0, 0, hops[i - 2]['token'] if rw else ph, pt=9.5, padx=9 if rw else 7)[1]
        return lines_after(text.strip(), cw + gap_after(text))

    sc.row_lines = {}

    def q_row(i):
        def fn(style=None, i=i):
            st = style or 'plan'
            rw = st.endswith('_rw')
            base = st.replace('_rw', '')
            cur, done = base == 'cur', base == 'done'
            col = INK if cur else (SUB if done else '9C97AB')
            y = row_y(i)
            ph, text = q_text(i, rw)
            t1, t2 = q_lines(i, rw)
            out = []
            if cur:   # 글 줄 수에 맞춘 바탕(위아래 여백 같게)
                hh = 40 if not t2 else 60
                out.append(R('q%d/hl' % i, LX + 8, y - 10, LW - 16, hh, prst='roundRect', radius=10, fill=LAV, line=None))
            out += [R('q%d/b' % i, LX + 16, y, 20, 20, prst='ellipse', fill=PURPLE if (cur or done) else 'ECE8F4', line=None),
                    T('q%d/bt' % i, LX + 16, y, 20, 20, '✓' if done else str(i), size=8, color='FFFFFF' if (cur or done) else MUTE,
                      weight='b', align='c', anchor='ctr')]
            lead = 0
            if ph is not None:
                if rw:
                    lead = chip_prims('x', 0, 0, hops[i - 2]['token'], pt=9.5, padx=9)[1] + gap_after(text)
                else:
                    pr, pw = chip_prims('q%d/ph' % i, X0, y - 1, ph, style='dash', pt=9.5, h=22, padx=7)
                    out += pr
                    lead = pw + gap_after(text)
            out.append(T('q%d/t1' % i, X0 + lead, y, QW - lead + 12, 20, t1, size=10, color=col, weight='m', anchor='ctr'))
            if t2:
                out.append(T('q%d/t2' % i, X0, y + 20, QW + 12, 20, t2, size=10, color=col, weight='m', anchor='ctr'))
            return out
        return fn

    for i in range(1, nh + 1):
        sc.put('q%d' % i, q_row(i))
    ay = row_y(nh + 1) - 2
    sc.ans_y = ay
    sc.put('qans', [T('qans/l', LX + 16, ay, 30, 22, '답', size=10, color=PURPLE, weight='b', anchor='ctr')])
    sc.put('qans.slot', chip_prims('qans/slot', X0, ay, ' ' * 22, style='dash', pt=9.5, h=22)[0])
    sc.X0 = X0
    sc.groups = {'qp': ['qorig', 'qans', 'qans.slot', 'qans.ok'] + ['q%d' % i for i in range(1, nh + 1)] +
                       ['tok%d@q' % i for i in range(1, nh + 1)]}


# ------------------------------------------------------------------ 오른쪽 화면: 구글 · 대화 + 통합 검색 · 대화 + 지금 상황
UX, UY, UW = 1830, 110, 380


def bubble_prims(name, x, by, w, msg, tm, mine):
    ml = wrap(msg, 10.5, w - 130)
    bw = max(tw(t, 10.5) for t in ml) + 24
    bh = 14 + 18 * len(ml)
    bx = x + w - 20 - bw if mine else x + 20
    out = [R(name, bx, by, bw, bh, prst='roundRect', radius=14, fill='EDE7FF' if mine else GRAY_FILL, line=None),
           T(name + '_t', bx + 12, by + 7, bw - 16, 18 * len(ml), ml, size=10.5, color=INK2, lnspc=13)]
    if tm:
        out.append(T(name + '_tm', (bx - 56) if mine else (bx + bw + 4), by + bh - 17, 52, 16, tm, size=7.5, color=MUTE,
                     anchor='ctr', align='r' if mine else 'l'))
    return out, bh


def ui_items(sc):
    sp = sc.spec
    ui = sp['ui']
    kind = sp['type']
    H = ui.get('h', 600 if kind == 'sheet' else 540)
    x, y, w = UX, UY, UW
    sc.ui = dict(x=x, y=y, w=w, h=H)
    base = [R('ui/bg', x, y, w, H, prst='roundRect', radius=28, fill='FFFFFF', line=LINE, line_w=1.0, shadow=S.L.SHADOW_CARD)]
    ky = y + H - 66
    msg_end = y + 82
    if kind == 'google':
        base += [P('ui/glogo', 'google.png', x + w / 2 - 63, y + 36, 126, 43)]

        def sbox(style=None):
            txt = ui['answer_q'] if style == 'done' else ui['query']
            return [R('ui/sb', x + 20, y + 104, w - 40, 50, prst='roundRect', fill='FFFFFF', line='DADCE0', line_w=1.2,
                      shadow=S.L.SHADOW_SOFT),
                    R('ui/sb_lens', x + 38, y + 121, 14, 14, prst='ellipse', fill=None, line='9AA0A6', line_w=1.8),
                    R('ui/sb_lens2', x + 49, y + 133, 7, 2, fill='9AA0A6', line=None),
                    T('ui/sb_t', x + 64, y + 104, w - 110, 50, txt, size=fit_pt(txt, w - 116, 11.5, 'r', 9.5), color=INK, anchor='ctr')]
        sc.put('ui.sbox', sbox)
        res = []
        ry = y + 176
        for i, (rt, rs) in enumerate(ui.get('results', [])):
            res += [T('ui.res/t%d' % i, x + 26, ry, w - 52, 22, rt, size=11, color='1A0DAB', weight='m', anchor='ctr'),
                    T('ui.res/s%d' % i, x + 26, ry + 22, w - 52, 18, rs, size=8.5, color=SUB, anchor='ctr')]
            ry += 58
        if res:
            sc.put('ui.res', res)
    else:   # 대화창
        base += [R('ui/av', x + 20, y + 18, 34, 34, prst='ellipse', fill='C9B8FF', line=None),
                 T('ui/av_t', x + 20, y + 18, 34, 34, ui['name'][0], size=12, color='FFFFFF', weight='b', align='c', anchor='ctr'),
                 T('ui/name', x + 64, y + 18, 220, 34, ui['name'], size=13, color=INK, weight='b', anchor='ctr'),
                 P('ui/app', S.ICON['talk'], x + w - 42, y + 24, 22, 22),
                 R('ui/div', x + 16, y + 66, w - 32, 1, fill='EEE9FA', line=None)]
        by = y + 82
        for i, (msg, tm, mine) in enumerate(ui['msgs']):
            pr, bh = bubble_prims('ui/m%d' % i, x, by, w, msg, tm, mine)
            base += pr
            by += bh + 10
        msg_end = by
    sc.ui['msg_end'] = msg_end
    sc.put('ui', base)
    if kind == 'sheet':   # 키보드의 실타래 버튼으로 여는 기록 통합 검색
        sy = msg_end + 8
        sc.put('ui.sheet', [R('ui.sheet/bg', x + 6, sy, w - 12, ky - 8 - sy, prst='roundRect', radius=22, fill='FFFFFF', line=LINE2,
                              line_w=1.2, shadow=S.L.SHADOW_LIFT),
                            R('ui.sheet/handle', x + w / 2 - 22, sy + 9, 44, 4, prst='roundRect', fill='D9D4E6', line=None),
                            P('ui.sheet/sp', S.ICON['spool'], x + 24, sy + 24, 22, 22),
                            T('ui.sheet/title', x + 54, sy + 20, 220, 30, '기록 통합 검색', size=12.5, color=PURPLE, weight='b', anchor='ctr'),
                            R('ui.sheet/sb', x + 20, sy + 60, w - 40, 44, prst='roundRect', fill='F7F5FC', line=LINE2, line_w=1.0),
                            T('ui.sheet/sb_t', x + 34, sy + 60, w - 66, 44, ui['query'], size=fit_pt(ui['query'], w - 72, 11, 'r', 9),
                              color=INK, anchor='ctr')])
        sc.ui['sheet_y'] = sy
    if kind == 'gps':     # 지금 상황(위치·날짜): 폰 옆 작은 카드
        rows = [('map', '현재 위치', ui['loc'])] + ([('day', '오늘', ui['today'])] if ui.get('today') else []) + \
            list(ui.get('extra_rows', []))
        cw = 236
        cx0, cy0 = x - cw - 24, y + 70
        out = [R('ui.loc/bg', cx0, cy0, cw, 14 + 46 * len(rows), prst='roundRect', radius=14, fill='FFFFFF', line=RING, line_w=1.4,
                 shadow=S.L.SHADOW_CARD, glow=(8, RING, 25))]
        for j, (ic, lab, val) in enumerate(rows):
            ry = cy0 + 8 + 46 * j
            if ic == 'day':   # 날짜 아이콘(앱 아이콘의 '31'이 날짜와 어긋나지 않게 직접 그림)
                dnum = ''.join(ch for ch in val.split('/')[-1] if ch.isdigit()) or val
                out += [R('ui.loc/ic%d' % j, cx0 + 14, ry + 10, 22, 22, prst='roundRect', radius=5, fill='FFFFFF', line=RING, line_w=1.0),
                        R('ui.loc/ic%db' % j, cx0 + 14, ry + 10, 22, 6, prst='rect', fill=PURPLE2, line=None),
                        T('ui.loc/ic%dt' % j, cx0 + 14, ry + 15, 22, 17, dnum, size=8.5, color=PURPLE, weight='b', align='c', anchor='ctr')]
            else:
                out.append(P('ui.loc/ic%d' % j, S.ICON[ic], cx0 + 14, ry + 10, 22, 22))
            out += [T('ui.loc/l%d' % j, cx0 + 46, ry + 2, cw - 56, 16, lab, size=8, color=MUTE, anchor='ctr'),
                    T('ui.loc/v%d' % j, cx0 + 46, ry + 18, cw - 56, 22, val, size=fit_pt(val, cw - 60, 10.5, 'b', 8.5), color=PURPLE,
                      weight='b', anchor='ctr')]
        sc.put('ui.loc', out)
    # 키보드 도구 막대(실타래 버튼)
    sc.put('ui.kbd', [R('ui.kbd/bar', x + 16, ky, w - 32, 46, prst='roundRect', radius=12, fill='F6F4FB', line=None),
                      R('ui.kbd/sp_bg', x + 26, ky + 7, 32, 32, prst='roundRect', radius=9, fill='FFFFFF', line=LINE, line_w=0.8),
                      P('ui.kbd/sp', S.ICON['spool'], x + 31, ky + 12, 22, 22)] +
           [T('ui.kbd/k%d' % j, x + 84 + j * 64, ky, 50, 46, t, size=9, color='A9A3B8', weight='b', align='c', anchor='ctr')
            for j, t in enumerate(['가', 'A', '123', '•••'])])

    def on(style=None):
        out = [R('ui.on/bg', x + 26, ky + 7, 32, 32, prst='roundRect', radius=9, fill=PURPLE, line=None, glow=(10, RING, 45)),
               P('ui.on/sp', S.ICON['spool_w'], x + 31, ky + 12, 22, 22)]
        if kind == 'gps' and style != 'nobadge':
            out += [R('ui.on/badge', x + 50, ky + 1, 16, 16, prst='ellipse', fill='FF4D4F', line='FFFFFF', line_w=1.2),
                    T('ui.on/badge_t', x + 50, ky + 1, 16, 16, '1', size=7, color='FFFFFF', weight='b', align='c', anchor='ctr')]
        return out
    sc.put('ui.on', on)
    sc.put('ui.tap', [P('ui.tap/h', 'touch-tap.png', x + 37, ky + 14, 28, 40)])
    sc.ui['ky'] = ky
    # 건네기 카드
    a = sp['deliver']
    rows = a.get('src_rows', [])
    ml = wrap(a['main'], 14.5, w - 64, 'b')
    ch = 40 + 26 * len(ml) + 8 + 26 * len(rows) + 8 + 36 + 14
    ay = (sc.ui['sheet_y'] + 116) if kind == 'sheet' else ky - ch - 12
    card = [R('ans/bg', x + 16, ay, w - 32, ch, prst='roundRect', radius=16, fill='FFFFFF', line=RING, line_w=1.8,
              shadow=S.L.SHADOW_LIFT, glow=(9, RING, 24)),
            P('ans/ic', S.ICON['spool'], x + 32, ay + 14, 18, 18),
            T('ans/lab', x + 56, ay + 12, 260, 22, a.get('label', '자동 완성 추천'), size=9.5, color=PURPLE2, weight='b', anchor='ctr')]
    card.append(T('ans/main', x + 32, ay + 40, w - 60, 26 * len(ml), ml, size=14.5, color=INK, weight='b', lnspc=19))
    ry = ay + 40 + 26 * len(ml) + 8
    for i, (ic, txt) in enumerate(rows):
        card += [P('ans/si%d' % i, S.ICON[ic], x + 32, ry + 4, 16, 16),
                 T('ans/st%d' % i, x + 54, ry, w - 90, 24, txt, size=fit_pt(txt, w - 92, 9, 'r', 7.5), color=SUB, anchor='ctr')]
        ry += 26
    btn = a.get('button', '✓  입력하기')
    card += [R('ans/btn', x + 32, ry + 8, w - 64, 36, prst='roundRect', fill=PURPLE, line=None),
             T('ans/btn_t', x + 32, ry + 8, w - 64, 36, btn, size=10.5, color='FFFFFF', weight='b', align='c', anchor='ctr')]
    sc.put('ans', card)
    sc.ans = dict(x=x + 16, y=ay, w=w - 32, h=ch, btn_y=ry + 8)
    sc.put('ui.tap2', [P('ui.tap2/h', 'touch-tap.png', x + w / 2 + 40, ry + 22, 28, 40)])
    # 결과: 대화에 들어간 말 + 답장
    r = sp.get('result')
    if kind != 'google' and r:
        by = msg_end + 4
        pr, bh = bubble_prims('res/mine', x, by, w, r['mine'], r.get('mine_tm', ''), True)
        out = pr
        if r.get('reply'):
            pr2, _ = bubble_prims('res/rep', x, by + bh + 10, w, r['reply'], r.get('reply_tm', ''), False)
            out += pr2
        sc.put('res', out)


# ------------------------------------------------------------------ 시나리오 → 단계
def link(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    if bx >= ax + aw - 4:
        return scurve((ax + aw + 2, ay + min(ah / 2, 44)), (bx - 2, by + min(bh / 2, 40)), 0.5)
    if by >= ay + ah - 4:
        return vcurve((ax + aw / 2, ay + ah + 2), (bx + bw / 2, by - 2), 0.5)
    if by + bh <= ay + 4:
        return vcurve((ax + aw / 2, ay - 2), (bx + bw / 2, by + bh + 2), 0.5)
    return scurve((ax - 2, ay + min(ah / 2, 40)), (bx + bw + 2, by + min(bh / 2, 40)), 0.5)


def gap_curve(a, b, how=None):
    """일반 임베딩이 못 잇는 두 기록 사이의 '?' 점선. 같은 줄이면 위로 둥글게, how='left'면 왼쪽으로 돌아감."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    if how == 'left':
        x0 = min(ax, bx) - 34
        return [(ax - 2, ay + ah / 2), (x0, ay + ah / 2), (x0, by + bh / 2), (bx - 2, by + bh / 2)]
    if abs(ay - by) < 30:       # 같은 줄: 위로 아치
        top = min(ay, by) - 56
        return [(ax + aw / 2, ay - 2), (ax + aw / 2, top), (bx + bw / 2, top), (bx + bw / 2, by - 2)]
    return link(a, b)


def route(p0, dst, obstacles, top=None):
    """왼쪽 열의 점 p0 → 기록 dst. 같은 줄에서 사이에 다른 카드가 있으면 그 줄 위로 넘어감(top: 그보다 위로)."""
    sx = p0[0]
    between = [b for b in obstacles if b[0] > sx and b[0] + b[2] < dst[0] + 4 and b[1] < dst[1] + dst[3] and b[1] + b[3] > dst[1]]
    if between:
        cy_ = min([dst[1]] + [b[1] for b in between]) - 30
        if top is not None:
            cy_ = min(cy_, top - 24)
        gx, tcx = sx + 32, dst[0] + dst[2] / 2
        b0, c0 = (gx + 30, cy_), (tcx - 44, cy_)
        return [p0, (gx, p0[1]), (gx, cy_), b0, (b0[0] + (c0[0] - b0[0]) / 3, cy_), (b0[0] + (c0[0] - b0[0]) * 2 / 3, cy_), c0,
                (tcx - 10, cy_), (tcx, cy_ + 10), (tcx, dst[1] - 2)]
    if dst[0] > sx + 10:
        return scurve(p0, (dst[0] - 2, dst[1] + min(dst[3] / 2, 40)), 0.5)
    return vcurve(p0, (dst[0] + dst[2] / 2, dst[1] - 2), 0.5)


def route_below(p0, box, obstacles):
    """필터 점선: 사이에 다른 카드가 있으면 그 줄 아래로 돌아 상자 아랫변으로(빠지는 카드를 감싸 보이지 않게)."""
    sx = p0[0]
    between = [b for b in obstacles if b[0] > sx and b[0] + b[2] < box[0] + 4 and b[1] < box[1] + box[3] and b[1] + b[3] > box[1]]
    if not between:
        return scurve(p0, (box[0] - 2, box[1] + min(box[3] / 2, 40)), 0.5)
    low = max([box[1] + box[3]] + [b[1] + b[3] for b in between]) + 16
    gx, ex = sx + 30, box[0] + 36
    return [p0, (gx, p0[1]), (gx, low), (gx + 30, low), (gx + 30 + (ex - 24 - gx - 30) / 3, low), (ex - 24 - (ex - 24 - gx - 30) / 3, low),
            (ex - 24, low), (ex - 6, low), (ex, low - 6), (ex, box[1] + box[3] + 1)]


def build(spec):
    sc = Scene(spec)
    for k, c in spec['records'].items():
        sc.card(k, c)
    hops = spec['hops']
    nh = len(hops)
    left_items(sc)
    ui_items(sc)
    recs = list(spec['records'])
    X = spec['text']
    kind = spec['type']
    RY = sc.RE_Y
    re_box = (LX, RY, LW, RE_H)
    sc.box['re'] = re_box
    owner = {}          # 형광펜·알약 → 그 카드(카드가 흐려지면 같이 숨김)
    obst = [sc.box[k] for k in recs]

    def tag_at(key, label, style='gray', where='tr', pt=9, name=None):
        bx, by, bw, bh = sc.box[key]
        w = tw(label, pt, 'sb') + 20
        x = bx + bw - w - 8 if where in ('tr', 'br') else bx + 10
        y = by - 11 if where in ('tr', 'tl') else by + bh - 11
        return chip_prims(name, x, y, label, style=style, pt=pt, h=22, padx=10, weight='sb')[0]

    # 지금 쓰는 검색 1: 단어로 찾기
    W_ = spec['word']
    hits = list(W_['hits'])
    for k, marks in W_['hits'].items():
        rects = [band(sc.pos[k][where], sub, kind='full') for where, sub in marks]
        sc.put('wm.' + k, [R('wm.%s/%d' % (k, i), *r, prst='roundRect', radius=3, fill=GRAY_HL, alpha=42, line=None)
                           for i, r in enumerate(rects)])
        owner['wm.' + k] = k
    miss = W_['miss']
    sc.put('miss.word', tag_at(miss, W_.get('miss_tag', '검색 결과에 없어요'), name='miss.word'))
    # 지금 쓰는 검색 2: 비슷한 것 찾기(일반 임베딩)
    Sm = spec['sim']
    ranks = Sm['ranks']
    rk = []
    for i, k in enumerate(ranks):
        bx, by, bw, bh = sc.box[k]
        sc.put('rank%d' % (i + 1), [R('rank%d/c' % (i + 1), bx - 12, by - 12, 26, 26, prst='ellipse', fill='8E88A0', line='FFFFFF',
                                      line_w=1.6),
                                    T('rank%d/t' % (i + 1), bx - 12, by - 12, 26, 26, str(i + 1), size=10, color='FFFFFF',
                                      weight='b', align='c', anchor='ctr')])
        rk.append('rank%d' % (i + 1))
    ga, gb = Sm['gap']
    pts = gap_curve(sc.box[ga], sc.box[gb], Sm.get('gap_route'))
    mid = ((pts[0][0] + 3 * pts[1][0] + 3 * pts[2][0] + pts[3][0]) / 8, (pts[0][1] + 3 * pts[1][1] + 3 * pts[2][1] + pts[3][1]) / 8)
    sc.put('gap', [C('gap/l', pts, w=2.2, color=GRAY_LINE, dash='dash'),
                   R('gap/q', mid[0] - 15, mid[1] - 15, 30, 30, prst='ellipse', fill='FFFFFF', line=GRAY_LINE, line_w=1.4),
                   T('gap/qt', mid[0] - 15, mid[1] - 15, 30, 30, '?', size=13, color=MUTE, weight='b', align='c', anchor='ctr')])
    sc.put('gap.a', tag_at(ga, Sm['tag_a'], name='gap.a'))
    sc.put('gap.b', tag_at(gb, Sm['tag_b'], name='gap.b'))
    gx_keys = list(Sm.get('extra_tags', {}))
    for k, lab_ in Sm.get('extra_tags', {}).items():
        sc.put('gap.x.' + k, tag_at(k, lab_, name='gap.x.' + k))
    missed = set(Sm.get('missed', [gb]))
    # 00 사전 준비 태그
    pk = list(spec['prep']['tags'])
    for k in pk:
        bx, by, bw, bh = sc.box[k]
        x, y = bx + 8, by + bh + 8
        out = []
        for i, t in enumerate(spec['prep']['tags'][k]):
            pr, w = chip_prims('pt.%s/%d' % (k, i), x, y, t, style='soft', pt=8.5, h=21, padx=8, weight='sb')
            out += pr
            x += w + 5
        sc.put('pt.' + k, out)
    ptk = ['pt.' + k for k in pk]

    # 홉마다: 다시 쓴 질문(통째로 띠에) + 필터 조건
    def hop_ask(n):
        hop = hops[n - 1]
        if n == 1:
            return [(hop['q'], INK)]
        return [(hops[n - 2]['token'], PURPLE), (hop['q'][2] if len(hop['q']) > 2 else hop['q'][1], INK)]

    def re_key(n):
        hop = hops[n - 1]
        cond = hop['filter'].get('cond', hop['filter']['label']) if hop.get('filter') else None
        mark = hops[n - 2]['token'] if n > 1 else hop.get('cond_word')
        key = 're:%d' % n
        if key not in sc.items:
            sc.put(key, re_prims(RY, hop_ask(n), cond, mark=mark))
            sc.box[key] = re_box
        return key

    th_y = RY + 122                      # 실이 나가는 높이(숫자 막대 가운데)
    H = []
    for i, hop in enumerate(hops):
        n = i + 1
        h = dict(n=n, hop=hop)
        f = hop.get('filter')
        if f:
            keys = f['keep']
            x0 = min(sc.box[k][0] for k in keys) - 14
            y0 = min(sc.box[k][1] for k in keys) - 16
            x1 = max(sc.box[k][0] + sc.box[k][2] for k in keys) + 14
            y1 = max(sc.box[k][1] + sc.box[k][3] for k in keys) + 14
            lab = f['label']
            lw_ = tw('필터  ' + lab, 9.5, 'b') + 22
            sc.put('fb%d' % n, [R('fb%d/r' % n, x0, y0, x1 - x0, y1 - y0, prst='roundRect', radius=18, fill=LAV, alpha=30,
                                  line=PURPLE2, line_w=1.6, dash='dash'),
                                R('fb%d/lb' % n, x0 + 14, y0 - 13, lw_, 26, prst='roundRect', fill=PURPLE, line=None),
                                T('fb%d/lt' % n, x0 + 14, y0 - 13, lw_, 26, [[('필터  ', {'color': 'D6CCFF'}), (lab, {'color': 'FFFFFF'})]],
                                  size=9.5, color='FFFFFF', weight='b', align='c', anchor='ctr')])
            fbox = (x0, y0, x1 - x0, y1 - y0)
            sc.box['fb%d' % n] = fbox
            others = [sc.box[k] for k in recs if k not in keys]
            sc.put('fl%d' % n, [C('fl%d/l' % n, route_below((LX + LW + 2, RY + 123), fbox, others), w=1.8, color=PURPLE2, dash='dash')])
            for k, lab2 in f.get('drop', {}).items():
                sc.put('drop%d.%s' % (n, k), tag_at(k, lab2, style='grayfill', name='drop%d.%s' % (n, k)))
            for k, marks in f.get('marks', {}).items():
                rects = [band(sc.pos[k][where], sub, kind='full') for where, sub in marks]
                sc.put('fm%d.%s' % (n, k), [R('fm%d.%s/%d' % (n, k, j), *r, prst='roundRect', radius=2.5, fill=HL, alpha=30, line=None)
                                            for j, r in enumerate(rects)])
                owner['fm%d.%s' % (n, k)] = k
            h['fbox'] = fbox
        d = hop['find']
        k = d['target']
        tb = sc.box[k]
        sc.put('th%d' % n, S.thread_prims('th%d' % n, route((LX + LW + 2, th_y), tb, [b for b in obst if b != tb],
                                                            top=(h['fbox'][1] - 13) if f else None)))
        rects = [band(sc.pos[k][where], sub, kind='full') for where, sub in d.get('marks', [])]
        if rects:
            sc.put('hm%d' % n, [R('hm%d/%d' % (n, j), *r, prst='roundRect', radius=2.5, fill=HL, alpha=34, line=None)
                                for j, r in enumerate(rects)])
            owner['hm%d' % n] = k
            h['mark0'] = rects[0]
        for ck, lab2 in d.get('cands', {}).items():
            sc.put('why%d.%s' % (n, ck), tag_at(ck, lab2, style='grayfill', name='why%d.%s' % (n, ck)))
        for pk_, (plab, pst) in d.get('pills', {}).items():
            ix, iy, iw, ih = sc.pos[pk_]['img']
            pw = tw(plab, 8.5, 'b') + 20
            px0, py0 = ix + iw / 2 - pw / 2, iy + ih - 30
            sc.put('pl%d.%s' % (n, pk_), [R('pl%d.%s/bg' % (n, pk_), px0, py0, pw, 22, prst='roundRect', fill='FFFFFF', alpha=95,
                                            line=PURPLE if pst == 'weave' else GRAY_LINE, line_w=1.2),
                                          T('pl%d.%s/t' % (n, pk_), px0, py0, pw, 22, plab, size=8.5,
                                            color=PURPLE if pst == 'weave' else BODY, weight='b', align='c', anchor='ctr')])
            sc.pos['pl%d.%s' % (n, pk_)] = (px0 + 10, py0 + 22 / 2 - 8.5 * 4 / 3 / 2 - 1, plab, 8.5, 'b')
            owner['pl%d.%s' % (n, pk_)] = pk_
        if d.get('pill_mark'):
            pk_, sub = d['pill_mark']
            r_ = band(sc.pos['pl%d.%s' % (n, pk_)], sub, kind='full')
            sc.put('pm%d' % n, [R('pm%d/0' % n, *r_, prst='roundRect', radius=2.5, fill=HL, alpha=34, line=None)])
            owner['pm%d' % n] = pk_
            h.setdefault('mark0', r_)
        # 확인 태그와 '일반 임베딩이 놓친 기록' 태그: 필터 라벨(왼쪽 위)·단서 칩(아래)과 겹치지 않게
        if k in missed:
            sc.put('rc%d' % n, tag_at(k, '일반 임베딩이 놓친 기록', style='gray', where='tr', name='rc%d' % n))
            if d.get('ok') and not f:
                sc.put('ok%d' % n, tag_at(k, d['ok'], style='fill', where='tl', name='ok%d' % n))
        elif d.get('ok'):
            sc.put('ok%d' % n, tag_at(k, d['ok'], style='fill', where='tr' if f else 'tl', name='ok%d' % n))
        h['target'] = k
        # 토큰(찾은 단서): 기록 아래(필터 상자 안이면 상자 아래)에 나타나 → 다음 질문의 빈자리로(마지막은 답 칸으로)
        last = n == nh
        lab = spec['answer'] if last else hop['token']
        tkw = chip_prims('x', 0, 0, lab, pt=9.5, padx=10)[1]
        below = (h['fbox'][1] + h['fbox'][3] + 6) if f else (tb[1] + tb[3] + 8)
        at = hop.get('tok_at', (tb[0] + tb[2] - tkw - 6, below))
        sc.put('tok%d@src' % n, chip_prims('tok%d' % n, at[0], at[1], lab, style='fill', pt=9.5, h=24, padx=10)[0])
        h['tok_src'] = (at[0], at[1], tkw, 24)
        if last:
            sc.put('tok%d@q' % n, chip_prims('tok%d' % n, sc.X0, sc.ans_y, lab, style='fill', pt=9.5, h=22, padx=9)[0])
            sc.put('qans.ok', chip_prims('qans.ok', sc.X0 + chip_prims('x', 0, 0, lab, pt=9.5, padx=9)[1] + 6, sc.ans_y + 1, '멈춤',
                                         style='soft', pt=8.5, h=20, padx=8)[0])
        else:
            sc.put('tok%d@q' % n, chip_prims('tok%d' % n, sc.X0, sc.row_y(n + 1) - 1, lab, style='fill', pt=9.5, h=22, padx=9)[0])
        H.append(h)

    # 기록의 근거(형광펜) → 다음 질문 칸의 단서 칩: 점선 화살표(멈춘 화면에서도 어디서 왔는지 보이게)
    def back_arrow(name, h):
        n = h['n']
        mx, my, mw, mh = h.get('mark0') or sc.box[h['target']]
        sx_, sy_ = mx, my + mh / 2
        cw_ = chip_prims('x', 0, 0, h['hop']['token'], pt=9.5, padx=9)[1]
        ex_, ey_ = sc.X0 + cw_ - 14, sc.row_y(n + 1) - 4        # 칩 오른쪽 위로, 위에서 내려앉게
        return [C(name + '/l', [(sx_ - 2, sy_), (sx_ - 90, sy_), (ex_ + 40, ey_ - 70), (ex_, ey_)], w=1.6, color=PURPLE2, dash='sysDash',
                  tail='triangle')]

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

    def step(keys, cap, side, focus, hud, notes, anim=None, zmax=1.3, pad=24, half=()):
        shown = list(cur)
        half = set(half)
        if focus is not None:
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
        sc.step(keys, cap, side=side, zmax=zmax, pad=pad, show=shown, focus=focus, styles=dict(styles), hud=hud, anim=anim or {},
                notes=notes, half=half)

    ui_base = ['ui', 'ui.kbd'] + (['ui.sbox'] if kind == 'google' else [])
    ctx = ['ui.loc'] if kind == 'gps' else []
    D2 = {'00', '01', '02'}
    show(*ui_base)
    # 1 상황
    step(['ui'], dict(t=X['q'], s=X['q_sub']), 'left', set(ui_base), {}, X['n_open'], zmax=1.15)
    # 2 기록 더미
    show(*recs)
    step(recs, dict(t=[('답은 분명 폰 어딘가에 있어요', INK)], s=X['cloud_sub']), 'top', set(recs), {}, X['n_cloud'], zmax=0.9)
    # 3 단어로 찾기
    show('qbox', *['wm.' + k for k in hits])
    styles.update({k: 'gray' for k in hits})
    step(['qbox'] + hits, dict(t=[('단어로 찾으면?', INK)], s=X['word_sub'], badge='지금 쓰는 검색 1'), 'top',
         set(['qbox'] + hits), {}, X['n_word'],
         anim={'wm.' + k: dict(kind='zoom_in', delay=250 + 150 * j, dur=300) for j, k in enumerate(hits)}, zmax=1.15)
    # 4 단어로는 못 찾는 이유
    show('miss.word')
    styles[miss] = 'gray'
    step([miss, 'miss.word'], dict(t=X['word_miss'], s=X['word_miss_sub']), 'right', {miss, 'miss.word'}, {}, X['n_word_miss'],
         anim={'miss.word': dict(kind='zoom_in', delay=0, dur=350)}, zmax=1.45, pad=40)
    # 5 비슷한 것 찾기(일반 임베딩)
    hide('miss.word', *['wm.' + k for k in hits])
    for k in hits + [miss]:
        styles.pop(k, None)
    styles.update({k: 'gray' for k in ranks})
    styles['qbox'] = 'sim'
    show('gen', *rk)
    step(['qbox', 'gen'] + ranks, dict(t=[('비슷한 것을 찾으면?', INK)], s=X['sim_sub'], badge='지금 쓰는 검색 2'), 'top',
         set(['qbox', 'gen'] + ranks + rk), {}, X['n_sim'],
         anim=dict({'gen': dict(kind='rise', delay=0, dur=450)},
                   **{k: dict(kind='zoom_in', delay=500 + 180 * j, dur=280) for j, k in enumerate(rk)}), zmax=1.25)
    # 6 한 번에는 닿지 않는 이유
    hide(*rk)
    for k in ranks:
        styles.pop(k, None)
    styles.update({ga: 'gray', gb: 'gray'})
    styles.update({k: 'gray' for k in gx_keys})
    gxt = ['gap.x.' + k for k in gx_keys]
    show('gap', 'gap.a', 'gap.b', *gxt)
    step([ga, gb, 'gap.a', 'gap.b', 'gap'] + gx_keys + gxt, dict(t=X['sim_gap'], s=X['sim_gap_sub']), 'right',
         set([ga, gb, 'gap', 'gap.a', 'gap.b'] + gx_keys + gxt), {}, X['n_sim_gap'],
         anim=dict({'gap': dict(kind='wipe_in', dir='left', delay=0, dur=600),
                    'gap.a': dict(kind='zoom_in', delay=500, dur=300), 'gap.b': dict(kind='zoom_in', delay=700, dur=300)},
                   **{x: dict(kind='zoom_in', delay=900 + 150 * j, dur=300) for j, x in enumerate(gxt)}), zmax=1.3, pad=40)
    # 7 00 사전 준비
    hide('qbox', 'gen', 'gap', 'gap.a', 'gap.b', *gxt)
    styles.clear()
    show(*ptk)
    step(pk + ptk, dict(t=X['prep'], s=X['prep_sub'], badge='00 사전 준비'), 'top', set(pk + ptk), dict(cur='00'), X['n_prep'],
         anim={k: dict(kind='zoom_in', delay=200 + 220 * j, dur=320) for j, k in enumerate(ptk)}, zmax=1.25, pad=30)
    hide(*ptk)
    # 8 01 순간 감지
    trig = {'google': ['ui.on', 'ui.tap'], 'sheet': ['ui.on', 'ui.tap', 'ui.sheet'], 'gps': ['ui.loc', 'ui.on']}[kind]
    show(*trig)
    step(['ui'] + ctx, dict(t=X['trig'], s=X['trig_sub'], badge='01 순간 감지'), 'left', set(ui_base + trig),
         dict(cur='01', done={'00'}), X['n_trig'],
         anim={k: dict(kind='rise' if k == 'ui.sheet' else 'zoom_in', delay=150 * j, dur=400) for j, k in enumerate(trig)},
         zmax=1.15)
    hide('ui.tap')
    # 9 02 질문 다시 쓰기: 먼저 풀 질문과, 그 답이 들어갈 질문으로 나눔
    qrows = ['q%d' % i for i in range(1, nh + 1)]
    qkeys = ['qp', 'qorig'] + qrows + ['qans', 'qans.slot']
    styles.update({'q1': 'cur'})
    show(*qkeys)
    step(['qp'], dict(t=X.get('split_t', [('한 번에 안 찾아지면, ', INK), ('\n질문을 나눠요', PURPLE)]),
                      s=X.get('split_s', '먼저 찾을 것부터 묻고, 그 답이 들어갈 자리는 비워 둬요'), badge='02 질문 다시 쓰기'), 'right',
         set(qkeys), dict(cur='02', done={'00', '01'}), X['n_split'],
         anim={x: dict(kind='zoom_in', delay=300 + 250 * j, dur=350) for j, x in enumerate(qrows)}, zmax=1.4)
    re_cur = None
    for h in H:
        n, hop = h['n'], h['hop']
        f, d = hop.get('filter'), hop['find']
        k = d['target']
        badge = '03 연쇄 탐색 %s' % '①②③'[n - 1]
        hud3 = dict(cur='03', done=D2, loop=n)
        k_re = re_key(n)
        if re_cur != k_re:
            if re_cur:
                hide(re_cur)
            show(k_re)
            re_cur = k_re
        if f:
            drops = ['drop%d.%s' % (n, x) for x in f.get('drop', {})]
            fms = ['fm%d.%s' % (n, x) for x in f.get('marks', {})]
            show('fb%d' % n, 'fl%d' % n, *drops, *fms)
            focus = set(f['keep'] + ['fb%d' % n, 'fl%d' % n, k_re] + drops)
            fbx = h['fbox']
            near_drops = [x for x in f.get('drop', {}) if sc.box[x][0] < fbx[0] + fbx[2] + 340]   # 멀리 있는 탈락 카드는 화면 맞춤에서 뺌
            step([k_re] + f['keep'] + near_drops + ['fb%d' % n], dict(t=f['t'], s=f['s'], badge=badge), 'top', focus,
                 hud3, f['note'], anim=dict({'fl%d' % n: dict(kind='wipe_in', dir='left', delay=0, dur=500),
                                             'fb%d' % n: dict(kind='fade_in', delay=300, dur=450)},
                                            **{x: dict(kind='zoom_in', delay=700 + 150 * j, dur=300) for j, x in enumerate(drops)},
                                            **{x: dict(kind='wipe_in', dir='left', delay=650, dur=400) for x in fms}), zmax=1.25)
            hide(*drops, 'fl%d' % n, *fms)
        cands = list(d.get('cands', {}))
        whys = ['why%d.%s' % (n, c) for c in cands]
        pills = ['pl%d.%s' % (n, x) for x in d.get('pills', {})]
        extra = [x for x in ('hm%d' % n, 'pm%d' % n, 'ok%d' % n, 'rc%d' % n) if x in sc.items]
        pshow = ['pt.' + k] if hop.get('prep_show') and ('pt.' + k) in sc.items else []
        show('th%d' % n, *whys, *pills, *extra, *pshow, 'tok%d@src' % n)
        styles[k] = 'weave'
        # 버린 후보 카드는 흐리게(이유 태그만 밝게). 사진 속 글자 알약은 카드가 흐려도 보이게 반쯤
        focus = set([k, 'th%d' % n, 'tok%d@src' % n, k_re] + whys + extra + pshow + (['fb%d' % n] if f else []))
        tcx, tcy = tb[0] + tb[2] / 2, tb[1] + tb[3] / 2

        def near(c):
            bx_, by_, bw_, bh_ = sc.box[c]
            return abs(bx_ + bw_ / 2 - tcx) < 700 and abs(by_ + bh_ / 2 - tcy) < 260
        fitk = [k_re, k, 'tok%d@src' % n] + [c for c in cands if near(c)] + (['fb%d' % n] if f else [])
        step(fitk, dict(t=d['t'], s=d['s'], badge=badge), d.get('side', 'top' if (f or cands) else 'right'), focus, hud3, d['note'],
             anim=dict({'th%d' % n: dict(kind='wipe_in', dir='left', delay=0, dur=650),
                        'hm%d' % n: dict(kind='wipe_in', dir='left', delay=800, dur=450),
                        'pm%d' % n: dict(kind='wipe_in', dir='left', delay=900, dur=450),
                        'ok%d' % n: dict(kind='zoom_in', delay=1150, dur=300),
                        'rc%d' % n: dict(kind='zoom_in', delay=1300, dur=300),
                        'tok%d@src' % n: dict(kind='zoom_in', delay=1550, dur=300)},
                       **{x: dict(kind='zoom_in', delay=650 + 130 * j, dur=280) for j, x in enumerate(whys)},
                       **{x: dict(kind='zoom_in', delay=450 + 130 * j, dur=280) for j, x in enumerate(pills)}), zmax=1.25,
             half=cands)
        hide(*whys, *pshow, 'rc%d' % n, 'fb%d' % n, 'ok%d' % n, 'th%d' % n)
        if n < nh:
            # 찾은 단서가 다음 질문의 빈자리로 → 다시 쓴 질문이 통째로 다음 검색에 들어감
            hide('tok%d@src' % n)
            show('tok%d@q' % n)
            styles['q%d' % n] = 'done' + ('_rw' if n > 1 else '')
            styles['q%d' % (n + 1)] = 'cur_rw'
            k_nx = re_key(n + 1)
            hide(re_cur)
            show(k_nx)
            re_cur = k_nx
            ry_ = sc.row_y(n + 1) + 10
            XR = LX + LW + 22
            ey = RY + 79                     # 띠의 질문 상자 가운데
            lpts = [(LX + LW - 6, ry_), (XR - 8, ry_), (XR, ry_), (XR, ry_ + 16),
                    (XR, ry_ + 16 + (ey - ry_ - 32) / 3), (XR, ry_ + 16 + (ey - ry_ - 32) * 2 / 3), (XR, ey - 16),
                    (XR, ey), (XR - 6, ey), (CHIP_X + QB_W + 3, ey)]
            sc.put('lc%d' % n, [C('lc%d/l' % n, lpts, w=2.2, color=PURPLE2, tail='triangle')])
            sc.put('bk%d' % n, back_arrow('bk%d' % n, h))
            show('lc%d' % n, 'bk%d' % n)
            step(['qp', k_nx, k], dict(t=hop.get('loop_t', [('찾은 단서로\n', INK), ('다음 질문을 다시 써요', PURPLE)]),
                                      s=hop['loop_s'], badge='02 질문 다시 쓰기'), 'right',
                 {'qp', 'q%d' % (n + 1), 'tok%d@q' % n, k_nx, 'lc%d' % n, 'bk%d' % n}, dict(cur='02', done={'00', '01', '03'}, loop=n,
                                                                                            loop_on=True),
                 hop['loop_note'], anim={'bk%d' % n: dict(kind='fade_in', delay=200, dur=500),
                                         'lc%d' % n: dict(kind='wipe_in', dir='up', delay=900, dur=600)}, zmax=1.2, half=[k])
            hide('lc%d' % n, 'bk%d' % n)
    # 멈춤: 답이 나오면 그만
    hide('tok%d@src' % nh, 'qans.slot')
    show('tok%d@q' % nh, 'qans.ok')
    styles['q%d' % nh] = 'done' + ('_rw' if nh > 1 else '')
    step(['qp'], dict(t=X.get('stop_t', [('답이 나오면, ', INK), ('\n거기서 멈춰요', PURPLE)]), s=X['stop_sub']), 'right',
         set(['qp', 'qorig', 'qans', 'qans.ok'] + qrows + ['tok%d@q' % h['n'] for h in H]), dict(cur='03', done=D2, loop=nh), X['n_stop'],
         anim={'qans.ok': dict(kind='zoom_in', delay=500, dur=300)}, zmax=1.4)
    # 04 전달: 카드가 열리면 버튼의 빨간 배지는 사라짐
    show('ans', 'ui.tap2')
    styles['ui.on'] = 'nobadge'
    step(['ui'] + ctx, dict(t=X['deliver'], s=X['deliver_sub'], badge='04 전달'), 'left',
         set(ui_base + ['ans', 'ui.tap2'] + [t for t in trig if t not in ('ui.tap', 'ui.loc')]),
         dict(cur='04', done={'00', '01', '02', '03'}), X['n_deliver'],
         anim={'ans': dict(kind='rise', delay=150, dur=550), 'ui.tap2': dict(kind='zoom_in', delay=1500, dur=300)}, zmax=1.15)
    # 결과
    hide('ui.tap2', 'ans', 'ui.on')
    res_keys = []
    if kind == 'google':
        styles['ui.sbox'] = 'done'
        res_keys = ['ui.res'] if 'ui.res' in sc.items else []
    else:
        hide('ui.sheet')
        res_keys = ['res'] if 'res' in sc.items else []
    show(*res_keys)
    step(['ui'] + ctx, dict(t=X['result'], s=X['result_sub']), 'left', set(ui_base + res_keys),
         dict(cur='04', done={'00', '01', '02', '03'}), X['n_result'],
         anim={k: dict(kind='rise', delay=300, dur=500) for k in res_keys}, zmax=1.15)
    # 정리: 질문 줄마다 찾은 기록으로 실, 기록의 근거는 점선으로 다음 질문 칸에. 다른 기록은 뺌
    hide(re_cur)
    targets = [h['target'] for h in H]
    hide(*[r for r in recs if r not in targets])
    sth = []
    for h in H:
        n = h['n']
        p0 = (LX + LW + 2, sc.row_y(n) + 10)
        sc.put('sth%d' % n, S.thread_prims('sth%d' % n, route(p0, sc.box[h['target']], [sc.box[t] for t in targets if t != h['target']])))
        sth.append('sth%d' % n)
    sbk = []
    for h in H[:-1]:
        sc.put('sbk%d' % h['n'], back_arrow('sbk%d' % h['n'], h))
        sbk.append('sbk%d' % h['n'])
    show(*sth, *sbk)
    for i in range(1, nh + 1):
        styles['q%d' % i] = 'done' + ('_rw' if i > 1 else '')
    toks = ['tok%d@q' % h['n'] for h in H]
    step(['qp'] + targets, dict(t=X.get('sum_t', [('찾은 단서가 다음 질문이 되어, ', INK), ('답까지 이어져요', PURPLE)]),
                                s='핵심 엔진은 지금 단서로부터 ‘이어지는’ 기록을 찾는 온디바이스 Reasoning Embedding이에요'),
         'top', set(['qp', 'qorig', 'qans', 'qans.ok'] + qrows + toks + targets + sth + sbk), dict(all=True), X['n_sum'],
         anim=dict({x: dict(kind='wipe_in', dir='left', delay=200 + 500 * j, dur=600) for j, x in enumerate(sth)},
                   **{x: dict(kind='fade_in', delay=500 + 500 * j, dur=500) for j, x in enumerate(sbk)}), zmax=0.95)
    return sc
