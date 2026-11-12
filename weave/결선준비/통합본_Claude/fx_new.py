"""기대효과 한 장(후보 셋) — 지금의 세 장(fx1~3)을 한 장 + 여러 효과로 바꾸는 안. 11-12 6차.

같은 뼈대
- 설문 셋이 하나씩 뜬다: 첫째는 가운데 → (클릭) 왼쪽으로 비키고 둘째가 가운데 → (클릭) 셋째가 오른쪽. 인트로 3~5쪽의 세 사람이 뜨던 차례와 같다.
- 고리 그래프 대신 얼굴 열 개. 불편을 겪은 만큼 짙은 색(83.8%면 여덟 개와 0.38개)이고 처음엔 입꼬리가 내려가 있다.
- (클릭) Weave로 풀리면 짙은 얼굴이 보라로 바뀌고 입꼬리가 반 바퀴 돌아 웃는다. Weave는 아이콘으로만 나온다(UX 화면은 앞에서 충분히 봄).

후보
- fxa '실 세 가닥': 불편 문장 → 얼굴 → 숫자. 아래 가운데의 Weave 아이콘에서 실이 뻗어 기능 이름에 닿고, 그 기능을 말할 때 그 칸이 웃는다.
- fxb '세 물음': 인트로의 말풍선 물음 → 얼굴 → 숫자와 한 줄. 기능을 말할 때 말풍선이 뒤집혀 Weave의 답(기능 이름)이 된다.
- fxc '물결': 숫자 → 얼굴 → 불편 문장. Weave 아이콘에서 물결이 퍼지며 닿는 얼굴부터 웃고, 문장의 둘째 줄이 달라진 일상으로 바뀐다.

그리는 법: 입은 웃는 모양으로 그려 두고 처음 뜰 때 반 바퀴 돌려 둔다. 풀리기 전에만 보이는 것(짙은 숫자, 처음 문장, 물음 말풍선)은 temp.
그래서 정적 보기와 내보내기에는 마지막 모습(웃는 얼굴)이 나온다. 첫째 칸은 놓인 자리가 왼쪽이고 처음에만 가운데로 옮겨 둔다(start).
"""
import math

import build as HW
from ui import ICON, INK, LINE, MUTE, PURPLE, PURPLE2, SUB, SHADOW_CARD, C, P, R, T, caption, numdot, thread, tw

import slides_new as N

Slide, cue = HW.Slide, HW.cue
NAVY = N.NAVY
F_TRACK = 'DCD4F3'                  # 불편을 겪지 않은 사람(옅은 얼굴)
GRAY = 'A9A3BA'                     # 풀린 뒤의 불편 문장(지나간 일)
CXS = (240, 640, 1040)              # 세 칸의 가운데
SHIFT = CXS[1] - CXS[0]             # 첫째 칸이 처음 뜨는 자리(가운데)까지
FD, FG = 56, 12                     # 얼굴 지름, 얼굴 사이
ST_PT, ST_LH = 20, 30               # 불편 문장의 글 크기, 줄 높이
PAD = 0.75                          # 보라 얼굴은 짙은 얼굴보다 이만큼 넉넉하게(가장자리에 짙은 테가 비치지 않게)
# (%, 불편 두 줄, 기능 이름, 달라진 두 줄, 인트로의 물음[(글, 보라인가)])
# 달라진 두 줄은 제안 장표(slides_new.FX)의 글. 셋째만 'Weave가 먼저 알려 줘요' → '묻기 전에 먼저 알려 줘요'(세 줄 모두 주어 없이, 대본의 말과 같게)
SURVEY = [
    (83.8, ['어느 앱인지 몰라', '앱을 하나씩 열어 봤어요'], '기록 통합 검색', ['어느 앱인지 몰라도', '한 번의 검색으로 찾아요'],
     [('어디에', 1), (' 적어 놨더라?', 0)]),
    (93.8, ['이름이 떠오르지 않아', '검색으로 바로 찾지 못했어요'], '단서로 찾는 기억', ['이름이 떠오르지 않아도', '기억나는 상황으로 찾아요'],
     [('그 ', 0), ('이름', 1), ('이 뭐였지?', 0)]),
    (82.4, ['챙겨야 할 부탁, 약속을', '나중에야 떠올렸어요'], '먼저 건네는 기억', ['챙겨야 할 부탁, 약속을', '묻기 전에 먼저 알려 줘요'],
     [('그런 ', 0), ('얘기', 1), ('가 있었나?', 0)]),
]

NOTES = {
    'fxa': ('저희 설문에서 83.8%는 어느 앱에 남겼는지 몰라 앱을 하나씩 열어 봤고, '
            '(클릭) 93.8%는 이름이 떠오르지 않아 검색으로 바로 찾지 못했으며, '
            '(클릭) 82.4%는 부탁이나 약속을 나중에야 떠올렸습니다. '
            '(클릭) Weave가 있다면 달라집니다. 기록 통합 검색은 헤매는 시간을 줄이고, 단서로 찾는 기억은 기억나는 상황만으로 찾아 주고, '
            '먼저 건네는 기억은 묻기 전에 먼저 알려 줍니다.'),
    'fxb': ('‘어디에 적어 놨더라?’ 저희 설문에서 83.8%는 앱을 하나씩 열어 봤습니다. '
            '(클릭) ‘그 이름이 뭐였지?’ 93.8%는 검색으로 바로 찾지 못했고, '
            '(클릭) ‘그런 얘기가 있었나?’ 82.4%는 부탁이나 약속을 나중에야 떠올렸습니다. '
            '(클릭) 이 세 질문에 Weave가 답합니다. 기록 통합 검색, 단서로 찾는 기억, 먼저 건네는 기억입니다.'),
    'fxc': ('설문에 답한 열 명 중 여덟 명은 어느 앱에 남겼는지 몰라 앱을 하나씩 열어 봤고, '
            '(클릭) 아홉 명은 이름이 떠오르지 않아 검색으로 바로 찾지 못했고, '
            '(클릭) 여덟 명은 부탁이나 약속을 나중에야 떠올렸습니다. '
            '(클릭) Weave가 있다면 이 표정이 달라집니다. 찾는 시간은 줄이고, 놓친 기억은 되살립니다.'),
}
CUES = {
    'fxa.n1': ('fxa', 0, '83.8%'),
    'fxa.f1': ('fxa', 3, '기록 통합 검색은'), 'fxa.f2': ('fxa', 3, '단서로 찾는 기억은'), 'fxa.f3': ('fxa', 3, '먼저 건네는 기억은'),
    'fxb.n1': ('fxb', 0, '83.8%'), 'fxb.n2': ('fxb', 1, '93.8%'), 'fxb.n3': ('fxb', 2, '82.4%'),
    'fxb.f1': ('fxb', 3, '기록 통합 검색,'), 'fxb.f2': ('fxb', 3, '단서로 찾는 기억,'), 'fxb.f3': ('fxb', 3, '먼저 건네는 기억입니다'),
    'fxc.n1': ('fxc', 0, '열 명 중'),
    'fxc.face': ('fxc', 3, '이 표정이'), 'fxc.title': ('fxc', 3, '찾는 시간은'),
}
HW.NOTES.update(NOTES)
HW.CUES.update(CUES)


# ------------------------------------------------------------------ 얼굴
def face_prims(key, cx, y, pct, d=FD, gap=FG, cols=5):
    """얼굴 열 개(cols개씩 줄지어, 가운데 x = cx, 위 끝 y). 돌려줌: 층마다의 원시 도형.
    track = 옅은 얼굴 열, navy = 불편을 겪은 만큼의 짙은 얼굴(마지막은 왼쪽 일부만), purple = 그 위에 번질 보라, eyes = 눈, mouth = 입(웃는 모양)."""
    x0 = cx - (cols * d + (cols - 1) * gap) / 2
    full = int(pct // 10)
    frac = pct / 10 - full
    out = dict(track=[], navy=[], purple=[], eyes=[], mouth=[], at=[])
    for i in range(10):
        r_, c_ = divmod(i, cols)
        x, yy = x0 + c_ * (d + gap), y + r_ * (d + gap)
        fx, fy = x + d / 2, yy + d / 2
        out['at'].append((fx, fy))
        out['track'].append(R('%s/t%d' % (key, i), x, yy, d, d, prst='ellipse', fill=F_TRACK, line=None))
        box2 = (x - PAD, yy - PAD, d + 2 * PAD, d + 2 * PAD)
        if i < full:
            out['navy'].append((i, R('%s/n%d' % (key, i), x, yy, d, d, prst='ellipse', fill=NAVY, line=None)))
            out['purple'].append((i, R('%s/p%d' % (key, i), *box2, prst='ellipse', fill=PURPLE, line=None)))
        elif i == full and frac > 0.004:        # 0.38개: 왼쪽에서 그만큼만 칠함(끊긴 그라데이션, 나머지는 투명)
            f1, f2 = frac * 100, (frac * d + PAD) / (d + 2 * PAD) * 100
            part = lambda col, f: dict(stops=[(0, col, 100), (f, col, 100), (f, col, 0), (100, col, 0)], ang=0)
            out['navy'].append((i, R('%s/n%d' % (key, i), x, yy, d, d, prst='ellipse', fill=None, line=None, grad=part(NAVY, f1))))
            out['purple'].append((i, R('%s/p%d' % (key, i), *box2, prst='ellipse', fill=None, line=None, grad=part(PURPLE, f2))))
        ex, ey, ew, eh = 0.167 * d, 0.125 * d, 0.10 * d, 0.117 * d
        for side, sx in (('a', -1), ('b', 1)):
            out['eyes'].append(R('%s/e%d%s' % (key, i, side), fx + sx * ex - ew / 2, fy - ey - eh / 2, ew, eh, prst='ellipse', fill='FFFFFF', line=None))
        a, b, my = 0.2 * d, 0.075 * d, fy + 0.2 * d
        out['mouth'].append((i, C('%s/m%d' % (key, i), [(fx - a, my - b), (fx - a * 0.5, my + b), (fx + a * 0.5, my + b), (fx + a, my - b)],
                                  color='FFFFFF', w=max(0.05 * d, 2.0))))
    return out


def put_faces(s, key, cx, y, pct, st=None, d=FD, gap=FG):
    """얼굴 열 개를 장에 넣는다(아래부터 옅은 얼굴, 짙은 얼굴, 보라, 눈, 입). st = 처음 뜨는 자리까지(첫째 칸). 돌려줌: 부품 키."""
    f = face_prims(key, cx, y, pct, d, gap)
    nm = dict(track=s.add(key + '/track', f['track'], start=st), navy=[], purple={}, mouth=[], at=f['at'])
    for i, p in f['navy']:
        nm['navy'].append(s.add('%s/n%d' % (key, i), [p], start=st))
    for i, p in f['purple']:
        nm['purple'][i] = s.add('%s/p%d' % (key, i), [p])
    nm['eyes'] = s.add(key + '/eyes', f['eyes'], start=st)
    for i, p in f['mouth']:
        nm['mouth'].append(s.add('%s/m%d' % (key, i), [p], start=st))
    return nm


def show(s, k, kind, t, dur=350, st=None, temp=False, **kw):
    """나타나는 효과 하나. 처음 자리가 다른 것(st)은 같은 순간 그 자리로, 잠깐만 보이는 것(temp)은 화면 밖에서 불러옴."""
    if temp:
        s.on(k, 'jump', t, to=st or (0, 0))
    s.on(k, kind, t, dur, **kw)
    if st and not temp:
        s.on(k, 'goto', t)


def faces_in(s, nm, t, t_fill, st=None, step=70):
    """옅은 얼굴 열 개가 시무룩한 입으로 뜨고, t_fill부터 불편을 겪은 만큼 하나씩 짙게 찬다. 돌려줌: 다 찬 때."""
    for k in [nm['track'], nm['eyes']] + nm['mouth']:
        show(s, k, 'fade_in', t, 350, st)
    for k in nm['mouth']:                       # 웃는 모양으로 그린 입을 반 바퀴 돌려 둠
        s.on(k, 'spin', t, 1, by=180)
    for j, k in enumerate(nm['navy']):
        show(s, k, 'zoom_in', t_fill + j * step, 260, st, **{'from': 0.45})
    return t_fill + (len(nm['navy']) - 1) * step + 260


def cheer(s, nm, times):
    """웃는 얼굴로: 보라가 가운데에서 번지고 입꼬리가 반 바퀴 돈다. times = 얼굴마다의 때."""
    for i, mk in enumerate(nm['mouth']):
        if i in nm['purple']:
            s.on(nm['purple'][i], 'zoom_in', times[i], 300, **{'from': 0.35})
        s.on(mk, 'spin', times[i] + 60, 330, by=180, accel=30000, decel=70000)


def movers(nm):
    return [nm['track'], nm['eyes']] + nm['navy'] + nm['mouth']


def slide_left(s, keys, t=0, dur=720):
    """가운데에 떠 있던 첫째 칸이 제자리(왼쪽)로."""
    s.on(keys, 'fly', t, dur, dx=SHIFT, dy=0, bend=0, show=False, fade=False)


def pct_text(key, cx, y, pct, color, pt=38, small=20):
    num = '%.1f' % pct
    nw = tw(num, pt, 'b') + tw('%', small, 'b') + 2
    return T(key, cx - nw / 2 - 4, y, nw + 16, round(pt * 1.42), [[(num, dict(size=pt)), ('%', dict(size=small))]], size=pt, color=color,
             weight='b', anchor='ctr', spc=-0.5)


def weave_mark(key, cx, cy, z=56):
    ic = z * 2 / 3
    return [R(key + '/mark', cx - z / 2, cy - z / 2, z, z, prst='roundRect', radius=z * 15 / 56, line=None,
              grad=dict(stops=[(0, '8D6BFF', None), (55, '6B4EFF', None), (100, '5A3FE0', None)], ang=55), shadow=(20, 8, '6B4EFF', 30)),
            P(key + '/icon', ICON['spool_w'], cx - ic / 2, cy - ic / 2, ic, ic)]


def halo(key, cx, cy, r=110):
    return R(key, cx - r, cy - r, 2 * r, 2 * r, prst='ellipse', fill=None, line=None,
             grad=dict(stops=[(0, '8B6BFF', 34), (36, 'B9A6FF', 13), (70, 'F2EDFF', 0), (100, 'F2EDFF', 0)], path='circle'))   # 70% = 동그라미의 가장자리(네모의 모서리가 100%)


# ------------------------------------------------------------------ 후보 A: 실 세 가닥
def feat_label(key, cx, y, n, name, pt=18, r=14):
    w = 2 * r + 9 + tw(name, pt, 'b')
    x = cx - w / 2
    return numdot(key + '/no', x + r, y + 16, n, r=r, pt=11.5) + [
        T(key + '/name', x + 2 * r + 9, y, tw(name, pt, 'b') + 12, 32, name, size=pt, color=INK, weight='b', anchor='ctr')]


def s_fxa():
    """불편 문장 → 얼굴 → 숫자. (클릭) 아래 가운데에 Weave 아이콘과 위에 제목 → 기능을 말할 때마다 실이 뻗어 기능 이름에 닿고 그 칸이 웃는다."""
    s = Slide('fxa', trans=('fade', 500), bar=False, notes=NOTES['fxa'])
    Y_ST, Y_F, Y_N, Y_L, ICY = 176, 254, 388, 458, 588
    s.add('fxa/title', [N.title('fxa/title', N.FX_TITLE)])
    cols = []
    for i, (pct, stmt, name, _, _) in enumerate(SURVEY):
        cx, k = CXS[i], 'fxa/c%d' % (i + 1)
        st = (SHIFT, 0) if i == 0 else None
        s.add(k + '/st', [caption(k + '/st', [[(ln, GRAY)] for ln in stmt], cx, Y_ST, size=ST_PT, lh=ST_LH)])
        s.add(k + '/st0', [caption(k + '/st0', [[(ln, INK)] for ln in stmt], cx, Y_ST, size=ST_PT, lh=ST_LH)], temp=True)
        nm = put_faces(s, k, cx, Y_F, pct, st)
        s.add(k + '/num', [pct_text(k + '/num', cx, Y_N, pct, PURPLE, pt=40)])
        s.add(k + '/num0', [pct_text(k + '/num0', cx, Y_N, pct, NAVY, pt=40)], temp=True)
        cols.append((k, nm, st))
    # 아래 가운데의 Weave와 실 셋
    z = 56
    ends = [(CXS[0], Y_L + 40), (CXS[1], Y_L + 40), (CXS[2], Y_L + 40)]
    paths = [[(640 - z / 2 - 3, ICY), (460, ICY), (ends[0][0], ICY + 6), ends[0]],
             [(640, ICY - z / 2 - 3)] * 2 + [ends[1]] * 2,
             [(640 + z / 2 + 3, ICY), (820, ICY), (ends[2][0], ICY + 6), ends[2]]]
    for i, pts in enumerate(paths):
        s.add('fxa/th%d' % (i + 1), thread('fxa/th%d' % (i + 1), pts, w=2.6))
    s.add('fxa/halo', [halo('fxa/halo', 640, ICY, 96)])
    s.add('fxa/rg', [R('fxa/rg', 640 - 74, ICY - 74, 148, 148, prst='ellipse', fill=None, line=PURPLE2, line_w=2.6, line_alpha=80)], temp=True)
    s.add('fxa/icon', weave_mark('fxa/icon', 640, ICY, z))
    for i, (_, _, name, _, _) in enumerate(SURVEY):
        s.add('fxa/lab%d' % (i + 1), feat_label('fxa/lab%d' % (i + 1), CXS[i], Y_L, i + 1, name))
    s.add('fxa/src', [N.foot('fxa/src', N.SURVEY_SRC)])

    def card_in(i, t, t_fill):
        k, nm, st = cols[i]
        show(s, k + '/st0', 'fade_in', t, 400, st, temp=True)
        end = faces_in(s, nm, t + 150, t_fill, st)
        show(s, k + '/num0', 'zoom_in', end - 120, 320, st, temp=True, **{'from': 0.86})
    # 장이 열리면: 첫째 설문이 가운데에
    card_in(0, 150, max(cue('fxa.n1', 1500, ahead=0.35), 600))
    s.click()      # 1: 첫째는 왼쪽으로, 둘째가 가운데에
    slide_left(s, movers(cols[0][1]) + [cols[0][0] + '/st0', cols[0][0] + '/num0'])
    card_in(1, 380, 640)
    s.click()      # 2: 셋째가 오른쪽에
    card_in(2, 0, 260)
    s.click()      # 3: Weave와 제목 → 기능을 말할 때마다 실, 이름, 웃는 얼굴
    s.on('fxa/icon', 'zoom_in', 0, 340, **{'from': 0.6})
    s.on('fxa/title', 'rise', 350, 520, dy=12)
    s.on('fxa/halo', 'fade_in', 100, 500)
    s.on('fxa/rg', 'jump', 160)
    s.on('fxa/rg', 'ring', 160, 900, **{'from': 0.4, 'to': 1.0})
    ts = [cue('fxa.f1', 2900, ahead=0.4), cue('fxa.f2', 5600, ahead=0.4), cue('fxa.f3', 9200, ahead=0.4)]
    ts[0] = max(ts[0], 700)
    for i, (k, nm, _) in enumerate(cols):
        t = ts[i]
        s.on('fxa/th%d' % (i + 1), 'wipe_in', t, 380, dir=('right', 'up', 'left')[i])
        s.on('fxa/lab%d' % (i + 1), 'zoom_in', t + 300, 300, **{'from': 0.85})
        t2 = t + 520
        cheer(s, nm, [t2 + j * 45 for j in range(10)])
        s.on(k + '/st0', 'fade_out', t2, 300)
        s.on(k + '/st', 'fade_in', t2, 300)
        s.on(k + '/num0', 'fade_out', t2 + 300, 260)
        s.on(k + '/num', 'fade_in', t2 + 300, 300)
    return s


# ------------------------------------------------------------------ 후보 B: 세 물음
def bubble_box(runs, pt=20, pad=30, icon=0):
    return sum(tw(t, pt, 'b') for t, _ in runs) + 2 * pad + icon


def s_fxb():
    """인트로의 말풍선 물음 → 얼굴 → 숫자와 한 줄. (클릭) 제목이 뜨고, 기능을 말할 때마다 말풍선이 뒤집혀 Weave의 답(기능 이름)이 되고 그 칸이 웃는다."""
    s = Slide('fxb', trans=('fade', 500), bar=False, notes=NOTES['fxb'])
    Y_B, BH, Y_F, Y_N, Y_C = 204, 56, 314, 448, 510
    s.add('fxb/title', [N.title('fxb/title', N.FX_TITLE)])
    cols = []
    for i, (pct, stmt, name, _, ask) in enumerate(SURVEY):
        cx, k = CXS[i], 'fxb/c%d' % (i + 1)
        st = (SHIFT, 0) if i == 0 else None
        runs = [(t, PURPLE if hl else INK) for t, hl in ask]
        w = max(bubble_box(runs), bubble_box([(name, 0)], icon=30))
        x = cx - w / 2
        # 꼬리(작은 동그라미 둘)는 물음과 답이 함께 씀
        s.add(k + '/tail', [R(k + '/tail/a', cx - 7, Y_B + BH + 8, 14, 14, prst='ellipse', fill='FFFFFF', line='DCD3F7', line_w=1.2),
                            R(k + '/tail/b', cx - 15, Y_B + BH + 28, 9, 9, prst='ellipse', fill='FFFFFF', line='DCD3F7', line_w=1.2)], start=st)
        iw = 24
        nw_ = tw(name, 20, 'b')
        ax = cx - (iw + 8 + nw_) / 2
        s.add(k + '/a', [R(k + '/a/bg', x, Y_B, w, BH, prst='roundRect', fill=PURPLE, line=None, shadow=(16, 5, '6B4EFF', 24)),
                         P(k + '/a/ic', ICON['spool_w'], ax, Y_B + (BH - iw) / 2, iw, iw),
                         T(k + '/a/t', ax + iw + 8, Y_B, nw_ + 12, BH, name, size=20, color='FFFFFF', weight='b', anchor='ctr')])
        s.add(k + '/q', [R(k + '/q/bg', x, Y_B, w, BH, prst='roundRect', fill='FFFFFF', line='E3DCF7', line_w=1.0, shadow=SHADOW_CARD),
                         T(k + '/q/t', x, Y_B, w, BH, [[(t, dict(color=c)) for t, c in runs]], size=20, weight='b', align='c', anchor='ctr')],
              temp=True)
        nm = put_faces(s, k, cx, Y_F, pct, st)
        s.add(k + '/num', [pct_text(k + '/num', cx, Y_N, pct, PURPLE, pt=40)])
        s.add(k + '/num0', [pct_text(k + '/num0', cx, Y_N, pct, NAVY, pt=40)], temp=True)
        s.add(k + '/cap', [T(k + '/cap', cx - 190, Y_C, 380, 24, ' '.join(stmt), size=13.5, color=SUB, align='c', anchor='ctr')], start=st)
        cols.append((k, nm, st))
    s.add('fxb/src', [N.foot('fxb/src', N.SURVEY_SRC)])

    def card_in(i, t, t_fill):
        k, nm, st = cols[i]
        show(s, k + '/q', 'zoom_in', t, 340, st, temp=True, **{'from': 0.82})
        show(s, k + '/tail', 'fade_in', t + 120, 300, st)
        end = faces_in(s, nm, t + 260, t_fill, st)
        show(s, k + '/num0', 'zoom_in', end - 120, 320, st, temp=True, **{'from': 0.86})
        show(s, k + '/cap', 'fade_in', end, 350, st)
    card_in(0, 250, max(cue('fxb.n1', 3200, ahead=0.35), 900))
    s.click()      # 1
    slide_left(s, movers(cols[0][1]) + [cols[0][0] + k for k in ('/q', '/tail', '/num0', '/cap')])
    card_in(1, 380, max(cue('fxb.n2', 2500, ahead=0.35), 800))
    s.click()      # 2
    card_in(2, 0, max(cue('fxb.n3', 2500, ahead=0.35), 500))
    s.click()      # 3: 세 물음에 Weave가 답함(제목) → 기능을 말할 때마다 말풍선이 뒤집히고 그 칸이 웃음
    s.on('fxb/title', 'rise', 150, 520, dy=12)
    for k, _, _ in cols:
        s.on(k + '/q', 'pulse', 250, 170, scale=1.05)
    ts = [cue('fxb.f1', 2900, ahead=0.3), cue('fxb.f2', 4300, ahead=0.3), cue('fxb.f3', 5900, ahead=0.3)]
    ts[0] = max(ts[0], 900)
    for i, (k, nm, _) in enumerate(cols):
        t = ts[i]
        s.on(k + '/q', 'flip_out', t, 190)
        s.on(k + '/a', 'flip_in', t + 190, 260)
        t2 = t + 330
        cheer(s, nm, [t2 + j * 45 for j in range(10)])
        s.on(k + '/num0', 'fade_out', t2 + 300, 260)
        s.on(k + '/num', 'fade_in', t2 + 300, 300)
    return s


# ------------------------------------------------------------------ 후보 C: 물결
def s_fxc():
    """숫자 → 얼굴 → 불편 문장. (클릭) 아래 가운데에 Weave 아이콘 → 물결이 퍼지며 닿는 얼굴부터 웃고, 문장의 둘째 줄이 달라진 일상으로 바뀐다 → 제목."""
    s = Slide('fxc', trans=('fade', 500), bar=False, notes=NOTES['fxc'])
    Y_N, Y_F, Y_ST, ICY = 160, 246, 390, 584
    RR, T_RING, S0 = 780, 1700, 0.07            # 물결: 다 퍼졌을 때의 반지름, 퍼지는 시간, 처음 크기
    s.add('fxc/title', [N.title('fxc/title', N.FX_TITLE)])
    cols = []
    for i, (pct, stmt, _, after, _) in enumerate(SURVEY):
        cx, k = CXS[i], 'fxc/c%d' % (i + 1)
        st = (SHIFT, 0) if i == 0 else None
        s.add(k + '/num', [pct_text(k + '/num', cx, Y_N, pct, PURPLE, pt=48, small=25)])
        s.add(k + '/num0', [pct_text(k + '/num0', cx, Y_N, pct, NAVY, pt=48, small=25)], temp=True)
        nm = put_faces(s, k, cx, Y_F, pct, st)
        s.add(k + '/st', [caption(k + '/st', [[(after[0], INK)], [(after[1], PURPLE)]], cx, Y_ST, size=ST_PT, lh=ST_LH)])
        s.add(k + '/st0', [caption(k + '/st0', [[(ln, INK)] for ln in stmt], cx, Y_ST, size=ST_PT, lh=ST_LH)], temp=True)
        cols.append((k, nm, st))
    s.add('fxc/halo', [halo('fxc/halo', 640, ICY, 104)])
    for j in range(3):
        s.add('fxc/rg%d' % j, [R('fxc/rg%d' % j, 640 - RR, ICY - RR, 2 * RR, 2 * RR, prst='ellipse', fill=None, line=PURPLE2, line_w=2.4,
                                 line_alpha=62 - j * 14)], temp=True)
    s.add('fxc/icon', weave_mark('fxc/icon', 640, ICY, 56))
    s.add('fxc/src', [N.foot('fxc/src', N.SURVEY_SRC)])

    def card_in(i, t, t_fill):
        k, nm, st = cols[i]
        end = faces_in(s, nm, t, t_fill, st)
        show(s, k + '/st0', 'fade_in', t + 150, 400, st, temp=True)
        show(s, k + '/num0', 'zoom_in', end - 120, 320, st, temp=True, **{'from': 0.86})
    card_in(0, 150, max(cue('fxc.n1', 1500, ahead=0.3), 600))
    s.click()      # 1
    slide_left(s, movers(cols[0][1]) + [cols[0][0] + '/st0', cols[0][0] + '/num0'])
    card_in(1, 380, 640)
    s.click()      # 2
    card_in(2, 0, 260)
    s.click()      # 3: Weave에서 물결이 퍼지고, 닿는 얼굴부터 웃음
    s.on('fxc/icon', 'zoom_in', 0, 340, **{'from': 0.6})
    s.on('fxc/halo', 'fade_in', 100, 500)
    t0 = max(cue('fxc.face', 1500, ahead=0.3), 450)
    for j in range(3):
        s.on('fxc/rg%d' % j, 'jump', t0 + j * 240)
        s.on('fxc/rg%d' % j, 'ring', t0 + j * 240, T_RING, **{'from': S0, 'to': 1.0})
    s.on('fxc/icon', 'pulse', t0, 170, scale=1.1)

    def reach(x, y):
        """물결의 앞 끝이 (x, y)에 닿는 때(고리는 처음에 빠르고 점점 느려짐: 지나온 비율 = 1 − (1 − u)²)."""
        f = min(max((math.hypot(x - 640, y - ICY) / RR - S0) / (1 - S0), 0), 0.98)
        return t0 + T_RING * (1 - math.sqrt(1 - f))
    for k, nm, _ in cols:
        times = [reach(x, y) - 60 for x, y in nm['at']]
        cheer(s, nm, times)
        tm = sum(times) / len(times)
        s.on(k + '/num0', 'fade_out', tm + 120, 260)
        s.on(k + '/num', 'fade_in', tm + 120, 300)
        s.on(k + '/st0', 'fade_out', tm + 200, 240)
        s.on(k + '/st', 'fade_in', tm + 440, 340)
    s.on('fxc/title', 'rise', max(cue('fxc.title', 4300, ahead=0.3), t0 + T_RING * 0.75), 520, dy=12)
    return s


CANDIDATES = [('A', 'fxa', s_fxa, '실 세 가닥'), ('B', 'fxb', s_fxb, '세 물음'), ('C', 'fxc', s_fxc, '물결')]
