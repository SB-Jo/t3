"""기대효과 한 장 — 5차까지의 세 장(fx1~3)을 한 장 + 여러 효과로. 11-13에 후보 L을 손본 판으로 정해 덱에 들어감(s_fx, 키 fx. 이 파일 끝).
아래는 고르기까지 만든 후보들(A~L). tools/fx_try.py로 다시 찍어 볼 수 있다.

같은 뼈대
- 설문 셋이 하나씩 뜬다: 첫째는 가운데 → (클릭) 왼쪽으로 비키고 둘째가 가운데 → (클릭) 셋째가 오른쪽. 인트로 3~5쪽의 세 사람이 뜨던 차례와 같다.
- 고리 그래프 대신 얼굴 열 개. 불편을 겪은 만큼 짙은 색(83.8%면 여덟 개와 0.38개)이고 처음엔 입꼬리가 내려가 있다.
- (클릭) Weave로 풀리면 짙은 얼굴이 보라로 바뀌고 입꼬리가 반 바퀴 돌아 웃는다. Weave는 아이콘으로만 나온다(UX 화면은 앞에서 충분히 봄).

후보 1차(얼굴 열 개)
- fxa '실 세 가닥': 불편 문장 → 얼굴 → 숫자. 아래 가운데의 Weave 아이콘에서 실이 뻗어 기능 이름에 닿고, 그 기능을 말할 때 그 칸이 웃는다.
- fxb '세 물음': 인트로의 말풍선 물음 → 얼굴 → 숫자와 한 줄. 기능을 말할 때 말풍선이 뒤집혀 Weave의 답(기능 이름)이 된다.
- fxc '물결': 숫자 → 얼굴 → 불편 문장. Weave 아이콘에서 물결이 퍼지며 닿는 얼굴부터 웃고, 문장의 둘째 줄이 달라진 일상으로 바뀐다.

후보 2차(11-12 밤: '사람 10개가 보기 좋지는 않다' → 고리 그래프와 표정을 합침. 풀리는 모습은 모두 C처럼 물결)
- fxd '고리 얼굴': 고리 그래프가 곧 얼굴의 테두리. 고리 안에 눈과 입, 그 아래 숫자와 불편 문장. 풀리면 고리가 보라로 차오르고 입꼬리가 돈다.
- fxe '고리 속 얼굴': 고리 그래프 안에 꽉 찬 얼굴(프로필 사진 둘레의 고리처럼). 풀리면 얼굴과 고리가 보라로.
- fxf 'AS-IS → TO-BE': fxd에 가벼운 뱃지. 처음엔 위 가운데에 AS-IS, 풀릴 때 TO-BE로 뒤집히고 그 아래에 제목.
- fxg '줄어드는 숫자': 표정 없이 고리 안에 숫자. 풀리면 숫자가 0까지 줄고 고리도 비워진다.
- fxh '몸통 있는 사람': fxc의 얼굴 열 개를 머리와 몸통이 있는 사람 열 명으로.

후보 3차(11-12 밤: '표정이 변하는 것은 좋은데 숫자와 시각화는 여전히 그 퍼센트를 가리켜 이질감' → 풀린 뒤에는 숫자도 고리도 퍼센트를 가리키지 않게)
셋 모두 fxd의 고리 얼굴에서 시작하고, 풀리면 고리가 보라로 한 바퀴 닫혀 그래프가 아니라 얼굴의 테두리가 된다. 숫자는 화면에서 물러난다.
- fxj '숫자가 기능 이름으로': 기능을 말할 때마다 Weave 아이콘에서 실이 뻗고, 숫자가 뒤집혀 그 기능의 이름이 된다. 그 아래에 달라진 한 줄.
- fxk '숫자가 물러남': 물결이 닿으면 숫자가 사라지고 그 자리에 달라진 두 줄이 올라온다.
- fxl '숫자가 0으로': fxk와 같되 숫자가 0까지 줄어든 뒤 사라진다.

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
# 11-12 밤: '이름이' → '정확한 이름이', '검색으로 바로 찾지' → '검색으로 찾지'(덱 전체와 함께).
# 달라진 두 줄은 제안 장표(slides_new.FX)의 글. 셋째만 'Weave가 먼저 알려 줘요' → '묻기 전에 먼저 알려 줘요'(세 줄 모두 주어 없이, 대본의 말과 같게)
SURVEY = [
    (83.8, ['어느 앱인지 몰라', '앱을 하나씩 열어 봤어요'], '기록 통합 검색', ['어느 앱인지 몰라도', '한 번의 검색으로 찾아요'],
     [('어디에', 1), (' 적어 놨더라?', 0)]),
    (93.8, ['정확한 이름이 떠오르지 않아', '검색으로 찾지 못했어요'], '단서로 찾는 기억', ['정확한 이름이 떠오르지 않아도', '기억나는 상황으로 찾아요'],
     [('정확한 ', 0), ('이름', 1), ('이 뭐였지?', 0)]),       # 11-12 밤: '그 이름' → '정확한 이름'(인트로 4·5쪽과 함께)
    (82.4, ['챙겨야 할 부탁, 약속을', '나중에야 떠올렸어요'], '먼저 건네는 기억', ['챙겨야 할 부탁, 약속을', '묻기 전에 먼저 알려 줘요'],
     [('그런 ', 0), ('얘기', 1), ('가 있었나?', 0)]),
]

NOTES = {
    'fxa': ('저희 설문에서 83.8%는 어느 앱에 남겼는지 몰라 앱을 하나씩 열어 봤고, '
            '(클릭) 93.8%는 정확한 이름이 떠오르지 않아 검색으로 찾지 못했으며, '
            '(클릭) 82.4%는 부탁이나 약속을 나중에야 떠올렸습니다. '
            '(클릭) Weave가 있다면 달라집니다. 기록 통합 검색은 헤매는 시간을 줄이고, 단서로 찾는 기억은 기억나는 상황만으로 찾아 주고, '
            '먼저 건네는 기억은 묻기 전에 먼저 알려 줍니다.'),
    'fxb': ('‘어디에 적어 놨더라?’ 저희 설문에서 83.8%는 앱을 하나씩 열어 봤습니다. '
            '(클릭) ‘정확한 이름이 뭐였지?’ 93.8%는 검색으로 찾지 못했고, '
            '(클릭) ‘그런 얘기가 있었나?’ 82.4%는 부탁이나 약속을 나중에야 떠올렸습니다. '
            '(클릭) 이 세 질문에 Weave가 답합니다. 기록 통합 검색, 단서로 찾는 기억, 먼저 건네는 기억입니다.'),
    'fxc': ('설문에 답한 열 명 중 여덟 명은 어느 앱에 남겼는지 몰라 앱을 하나씩 열어 봤고, '
            '(클릭) 아홉 명은 정확한 이름이 떠오르지 않아 검색으로 찾지 못했고, '
            '(클릭) 여덟 명은 부탁이나 약속을 나중에야 떠올렸습니다. '
            '(클릭) Weave가 있다면 이 표정이 달라집니다. 찾는 시간은 줄이고, 놓친 기억은 되살립니다.'),
}
PCT_HEAD = ('저희 설문에서 83.8%는 어느 앱에 남겼는지 몰라 앱을 하나씩 열어 봤고, '
            '(클릭) 93.8%는 정확한 이름이 떠오르지 않아 검색으로 찾지 못했으며, '
            '(클릭) 82.4%는 부탁이나 약속을 나중에야 떠올렸습니다. ')
TAIL = '(클릭) Weave가 있다면 이 %s 달라집니다. 찾는 시간은 줄이고, 놓친 기억은 되살립니다.'
NOTES.update(fxd=PCT_HEAD + TAIL % '표정이', fxe=PCT_HEAD + TAIL % '표정이', fxf=PCT_HEAD + TAIL % '표정이', fxg=PCT_HEAD + TAIL % '숫자가',
             fxh=NOTES['fxc'])
CUES = {
    'fxa.n1': ('fxa', 0, '83.8%'),
    'fxa.f1': ('fxa', 3, '기록 통합 검색은'), 'fxa.f2': ('fxa', 3, '단서로 찾는 기억은'), 'fxa.f3': ('fxa', 3, '먼저 건네는 기억은'),
    'fxb.n1': ('fxb', 0, '83.8%'), 'fxb.n2': ('fxb', 1, '93.8%'), 'fxb.n3': ('fxb', 2, '82.4%'),
    'fxb.f1': ('fxb', 3, '기록 통합 검색,'), 'fxb.f2': ('fxb', 3, '단서로 찾는 기억,'), 'fxb.f3': ('fxb', 3, '먼저 건네는 기억입니다'),
    'fxc.n1': ('fxc', 0, '열 명 중'),
    'fxc.face': ('fxc', 3, '이 표정이'), 'fxc.title': ('fxc', 3, '찾는 시간은'),
    'fxh.n1': ('fxh', 0, '열 명 중'),
    'fxh.face': ('fxh', 3, '이 표정이'), 'fxh.title': ('fxh', 3, '찾는 시간은'),
}
for _k, _w in (('fxd', '이 표정이'), ('fxe', '이 표정이'), ('fxf', '이 표정이'), ('fxg', '이 숫자가')):
    CUES.update({_k + '.n1': (_k, 0, '83.8%'), _k + '.face': (_k, 3, _w), _k + '.title': (_k, 3, '찾는 시간은')})
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


# ------------------------------------------------------------------ Weave 아이콘과 물결(후보 C~H가 함께 씀)
RR, T_RING, S0 = 780, 1700, 0.07            # 물결: 다 퍼졌을 때의 반지름, 퍼지는 시간, 처음 크기


def add_weave(s, key, icy):
    """아래 가운데의 Weave 아이콘, 그 둘레의 빛, 퍼져 나갈 고리 셋(잠깐만 보임)."""
    s.add(key + '/halo', [halo(key + '/halo', 640, icy, 104)])
    for j in range(3):
        s.add('%s/rg%d' % (key, j), [R('%s/rg%d' % (key, j), 640 - RR, icy - RR, 2 * RR, 2 * RR, prst='ellipse', fill=None, line=PURPLE2, line_w=2.4,
                                       line_alpha=62 - j * 14)], temp=True)
    s.add(key + '/icon', weave_mark(key + '/icon', 640, icy, 56))


def weave_in(s, key):
    s.on(key + '/icon', 'zoom_in', 0, 340, **{'from': 0.6})
    s.on(key + '/halo', 'fade_in', 100, 500)


def wave(s, key, icy, t0):
    """Weave 아이콘에서 물결 셋이 퍼진다. 돌려줌: reach(x, y) = 물결의 앞 끝이 그 자리에 닿는 때."""
    for j in range(3):
        s.on('%s/rg%d' % (key, j), 'jump', t0 + j * 240)
        s.on('%s/rg%d' % (key, j), 'ring', t0 + j * 240, T_RING, **{'from': S0, 'to': 1.0})
    s.on(key + '/icon', 'pulse', t0, 170, scale=1.1)

    def reach(x, y):        # 고리는 처음에 빠르고 점점 느려짐: 지나온 비율 = 1 − (1 − u)²
        f = min(max((math.hypot(x - 640, y - icy) / RR - S0) / (1 - S0), 0), 0.98)
        return t0 + T_RING * (1 - math.sqrt(1 - f))
    return reach


# ------------------------------------------------------------------ 몸통 있는 사람 열 명(후보 H)
PW, PHD, PBH, PGX, PGY = 54, 38, 27, 8, 14      # 사람 폭, 머리 지름, 몸통 높이, 옆 사이, 줄 사이
PH = PHD + 3 + PBH                              # 사람 높이


def person_shapes(key, x, y, color, part=None, pad=0.0):
    """사람 하나(머리 동그라미 + 반달 몸통). part = 왼쪽에서 칠할 비율(0~1, 없으면 다). pad만큼 넉넉하게(보라가 짙은 색을 덮을 때)."""
    hx, by = x + (PW - PHD) / 2, y + PHD + 3
    hb = (hx - pad, y - pad, PHD + 2 * pad, PHD + 2 * pad)
    bb = (x - pad, by - pad, PW + 2 * pad, 2 * (PBH + 2 * pad))            # 반달 = 타원의 위쪽 반(아래 반은 그리지 않음)
    half = dict(adj1=10800000, adj2=0)
    if part is None:
        return [R(key + '/h', *hb, prst='ellipse', fill=color, line=None), R(key + '/b', *bb, prst='pie', fill=color, line=None, adj=half)]
    g = lambda f: dict(stops=[(0, color, 100), (f, color, 100), (f, color, 0), (100, color, 0)], ang=0)
    fh = (part * PW - (PW - PHD) / 2 + pad) / (PHD + 2 * pad) * 100
    out = [R(key + '/h', *hb, prst='ellipse', fill=None, line=None, grad=g(min(fh, 100)))] if fh > 1 else []
    return out + [R(key + '/b', *bb, prst='pie', fill=None, line=None, grad=g((part * PW + pad) / (PW + 2 * pad) * 100), adj=half)]


def put_people(s, key, cx, y, pct, st=None):
    """사람 열 명(다섯씩 두 줄)을 장에 넣는다. put_faces와 같은 모양의 키를 돌려준다(짙은 색과 보라는 사람마다 머리 + 몸통 한 묶음)."""
    x0 = cx - (5 * PW + 4 * PGX) / 2
    full = int(pct // 10)
    frac = pct / 10 - full
    track, eyes, navy, purple, mouth, at = [], [], [], [], [], []
    for i in range(10):
        r_, c_ = divmod(i, 5)
        x, yy = x0 + c_ * (PW + PGX), y + r_ * (PH + PGY)
        fx, fy, d = x + PW / 2, yy + PHD / 2, PHD
        at.append((fx, yy + PH / 2))
        track += person_shapes('%s/t%d' % (key, i), x, yy, F_TRACK)
        if i < full or (i == full and frac > 0.004):
            part = None if i < full else frac
            navy.append((i, person_shapes('%s/n%d' % (key, i), x, yy, NAVY, part)))
            purple.append((i, person_shapes('%s/p%d' % (key, i), x, yy, PURPLE, part, PAD)))
        ex, ey, ew, eh = 0.167 * d, 0.125 * d, 0.10 * d, 0.117 * d
        for side, sx in (('a', -1), ('b', 1)):
            eyes.append(R('%s/e%d%s' % (key, i, side), fx + sx * ex - ew / 2, fy - ey - eh / 2, ew, eh, prst='ellipse', fill='FFFFFF', line=None))
        a, b, my = 0.2 * d, 0.075 * d, fy + 0.2 * d
        mouth.append(C('%s/m%d' % (key, i), [(fx - a, my - b), (fx - a * 0.5, my + b), (fx + a * 0.5, my + b), (fx + a, my - b)], color='FFFFFF', w=2.0))
    nm = dict(track=s.add(key + '/track', track, start=st), navy=[], purple={}, mouth=[], at=at)
    for i, ps in navy:
        nm['navy'].append(s.add('%s/n%d' % (key, i), ps, start=st))
    for i, ps in purple:
        nm['purple'][i] = s.add('%s/p%d' % (key, i), ps)
    nm['eyes'] = s.add(key + '/eyes', eyes, start=st)
    for i, m in enumerate(mouth):
        nm['mouth'].append(s.add('%s/m%d' % (key, i), [m], start=st))
    return nm


# ------------------------------------------------------------------ 후보 C: 물결 (H: 같은 장에 몸통 있는 사람)
def s_fxc(key='fxc', people=False):
    """숫자 → 얼굴(또는 사람) → 불편 문장. (클릭) 아래 가운데에 Weave 아이콘 → 물결이 퍼지며 닿는 얼굴부터 웃고, 문장의 둘째 줄이 달라진 일상으로 바뀐다 → 제목."""
    s = Slide(key, trans=('fade', 500), bar=False, notes=NOTES[key])
    Y_N, Y_F, Y_ST, ICY = (148, 232, 400, 588) if people else (160, 246, 390, 584)
    put = put_people if people else put_faces
    s.add(key + '/title', [N.title(key + '/title', N.FX_TITLE)])
    cols = []
    for i, (pct, stmt, _, after, _) in enumerate(SURVEY):
        cx, k = CXS[i], '%s/c%d' % (key, i + 1)
        st = (SHIFT, 0) if i == 0 else None
        s.add(k + '/num', [pct_text(k + '/num', cx, Y_N, pct, PURPLE, pt=48, small=25)])
        s.add(k + '/num0', [pct_text(k + '/num0', cx, Y_N, pct, NAVY, pt=48, small=25)], temp=True)
        nm = put(s, k, cx, Y_F, pct, st)
        s.add(k + '/st', [caption(k + '/st', [[(after[0], INK)], [(after[1], PURPLE)]], cx, Y_ST, size=ST_PT, lh=ST_LH)])
        s.add(k + '/st0', [caption(k + '/st0', [[(ln, INK)] for ln in stmt], cx, Y_ST, size=ST_PT, lh=ST_LH)], temp=True)
        cols.append((k, nm, st))
    add_weave(s, key, ICY)
    s.add(key + '/src', [N.foot(key + '/src', N.SURVEY_SRC)])

    def card_in(i, t, t_fill):
        k, nm, st = cols[i]
        end = faces_in(s, nm, t, t_fill, st)
        show(s, k + '/st0', 'fade_in', t + 150, 400, st, temp=True)
        show(s, k + '/num0', 'zoom_in', end - 120, 320, st, temp=True, **{'from': 0.86})
    card_in(0, 150, max(cue(key + '.n1', 1500, ahead=0.3), 600))
    s.click()      # 1
    slide_left(s, movers(cols[0][1]) + [cols[0][0] + '/st0', cols[0][0] + '/num0'])
    card_in(1, 380, 640)
    s.click()      # 2
    card_in(2, 0, 260)
    s.click()      # 3: Weave에서 물결이 퍼지고, 닿는 얼굴부터 웃음
    weave_in(s, key)
    t0 = max(cue(key + '.face', 1500, ahead=0.3), 450)
    reach = wave(s, key, ICY, t0)
    for k, nm, _ in cols:
        times = [reach(x, y) - 60 for x, y in nm['at']]
        cheer(s, nm, times)
        tm = sum(times) / len(times)
        s.on(k + '/num0', 'fade_out', tm + 120, 260)
        s.on(k + '/num', 'fade_in', tm + 120, 300)
        s.on(k + '/st0', 'fade_out', tm + 200, 240)
        s.on(k + '/st', 'fade_in', tm + 440, 340)
    s.on(key + '/title', 'rise', max(cue(key + '.title', 4300, ahead=0.3), t0 + T_RING * 0.75), 520, dy=12)
    return s


# ------------------------------------------------------------------ 고리 그래프와 표정(후보 D~G)
RO = 90                             # 고리의 바깥 반지름


def ring_set(key, cx, cy, pct, ro=RO, k=N.RING_K):
    """고리 그래프(인트로 7·8쪽과 같은 모양). 돌려줌: (바탕 고리, 짙은 호, 보라 호) 원시 목록."""
    track, navy = N.ring(key + '/r0', cx, cy, ro, pct, color=NAVY, k=k)
    return track, navy, N.ring(key + '/r1', cx, cy, ro, pct, color=PURPLE, k=k)[1]


def big_face(key, cx, cy, color, d=150.0, w=None):
    """큰 얼굴의 눈과 입(웃는 모양). d = 얼굴 지름. 돌려줌: (눈 원시 목록, 입 원시)."""
    ex, ey, ew, eh = 0.17 * d, 0.115 * d, 0.085 * d, 0.1 * d
    eyes = [R('%s/e%s' % (key, n), cx + sx * ex - ew / 2, cy - ey - eh / 2, ew, eh, prst='ellipse', fill=color, line=None)
            for n, sx in (('a', -1), ('b', 1))]
    a, b, my = 0.19 * d, 0.07 * d, cy + 0.18 * d
    return eyes, C(key + '/m', [(cx - a, my - b), (cx - a * 0.5, my + b), (cx + a * 0.5, my + b), (cx + a, my - b)], color=color, w=w or 0.045 * d)


def state_badge(key, cx, y, label, on):
    """가벼운 상태 뱃지(AS-IS, TO-BE). on이면 보라."""
    pt, h = 11, 26
    w = tw(label, pt, 'b') + 30
    return [R(key + '/bg', cx - w / 2, y, w, h, prst='roundRect', fill=PURPLE if on else 'E7E3EF', line=None),
            T(key + '/t', cx - w / 2, y, w, h, label, size=pt, color='FFFFFF' if on else SUB, weight='b', align='c', anchor='ctr', spc=0.6)]


def s_fxd(key='fxd', badge=False):
    """고리 얼굴: 고리 그래프가 얼굴의 테두리, 그 안에 눈과 입 → 숫자 → 불편 문장. (클릭) Weave 아이콘에서 물결이 닿으면 고리가 보라로 차오르고
    입꼬리가 돌아 웃는다. 문장의 둘째 줄이 달라진 일상으로 바뀐다 → 제목. badge면 위 가운데에 AS-IS → TO-BE 뱃지(제목은 그 아래)."""
    s = Slide(key, trans=('fade', 500), bar=False, notes=NOTES[key])
    dy = 10 if badge else 0
    CY, Y_N, Y_ST, ICY = 250 + dy, 350 + dy, 418 + dy, 584 + dy / 2
    s.add(key + '/title', [N.title(key + '/title', N.FX_TITLE, y=58 if badge else 46)])
    if badge:
        s.add(key + '/to', state_badge(key + '/to', 640, 24, 'TO-BE', True))
        s.add(key + '/as', state_badge(key + '/as', 640, 24, 'AS-IS', False), temp=True)
    cols = []
    for i, (pct, stmt, _, after, _) in enumerate(SURVEY):
        cx, k = CXS[i], '%s/c%d' % (key, i + 1)
        st = (SHIFT, 0) if i == 0 else None
        track, navy, purple = ring_set(k, cx, CY, pct)
        s.add(k + '/track', track, start=st)
        s.add(k + '/arc0', navy, temp=True)
        s.add(k + '/arc', purple)
        e0, m0 = big_face(k + '/f0', cx, CY, NAVY)
        e1, m1 = big_face(k + '/f1', cx, CY, PURPLE)
        s.add(k + '/eyes0', e0, temp=True)
        s.add(k + '/m0', [m0], temp=True)
        s.add(k + '/eyes', e1)
        s.add(k + '/m', [m1])
        s.add(k + '/num', [pct_text(k + '/num', cx, Y_N, pct, PURPLE, pt=40)])
        s.add(k + '/num0', [pct_text(k + '/num0', cx, Y_N, pct, NAVY, pt=40)], temp=True)
        s.add(k + '/st', [caption(k + '/st', [[(after[0], INK)], [(after[1], PURPLE)]], cx, Y_ST, size=ST_PT, lh=ST_LH)])
        s.add(k + '/st0', [caption(k + '/st0', [[(ln, INK)] for ln in stmt], cx, Y_ST, size=ST_PT, lh=ST_LH)], temp=True)
        cols.append((k, cx, st))
    add_weave(s, key, ICY)
    s.add(key + '/src', [N.foot(key + '/src', N.SURVEY_SRC)])
    first = ['/track', '/arc0', '/eyes0', '/m0', '/num0', '/st0']

    def card_in(i, t, t_fill):
        k, _, st = cols[i]
        show(s, k + '/track', 'fade_in', t, 350, st)
        show(s, k + '/eyes0', 'fade_in', t, 350, st, temp=True)
        show(s, k + '/m0', 'fade_in', t, 350, st, temp=True)
        s.on(k + '/m0', 'spin', t, 1, by=180)                      # 웃는 모양으로 그린 입을 반 바퀴 돌려 둠
        show(s, k + '/st0', 'fade_in', t + 150, 400, st, temp=True)
        show(s, k + '/arc0', 'wheel_in', t_fill, 800, st, temp=True)
        show(s, k + '/num0', 'zoom_in', t_fill + 620, 320, st, temp=True, **{'from': 0.86})
    if badge:
        show(s, key + '/as', 'fade_in', 100, 350, temp=True)
    card_in(0, 150, max(cue(key + '.n1', 1500, ahead=0.35), 600))
    s.click()      # 1
    slide_left(s, [cols[0][0] + x for x in first])
    card_in(1, 380, 640)
    s.click()      # 2
    card_in(2, 0, 260)
    s.click()      # 3: Weave에서 물결이 퍼지고, 닿는 고리부터 보라로 차오르며 웃음
    weave_in(s, key)
    t0 = max(cue(key + '.face', 1500, ahead=0.3), 450)
    reach = wave(s, key, ICY, t0)
    if badge:
        s.on(key + '/as', 'flip_out', t0, 180)
        s.on(key + '/to', 'flip_in', t0 + 180, 240)
    for k, cx, _ in cols:
        t = reach(cx, CY) - 60
        s.on(k + '/arc', 'wheel_in', t, 750)
        s.on(k + '/m0', 'spin', t + 230, 330, by=180, accel=30000, decel=70000)
        s.on([k + '/eyes0', k + '/m0'], 'fade_out', t + 560, 200)
        s.on([k + '/eyes', k + '/m'], 'fade_in', t + 540, 220)
        s.on(k + '/arc0', 'fade_out', t + 760, 150)
        s.on(k + '/num0', 'fade_out', t + 500, 240)
        s.on(k + '/num', 'fade_in', t + 500, 280)
        s.on(k + '/st0', 'fade_out', t + 640, 240)
        s.on(k + '/st', 'fade_in', t + 880, 340)
    s.on(key + '/title', 'rise', max(cue(key + '.title', 4300, ahead=0.3), t0 + T_RING * 0.75), 520, dy=12)
    return s


def s_fxe():
    """고리 속 얼굴: 고리 그래프 안에 꽉 찬 얼굴(짙은 색, 흰 눈과 입) → 숫자 → 불편 문장. (클릭) 물결이 닿으면 얼굴과 고리가 보라로 바뀌고 웃는다."""
    key = 'fxe'
    s = Slide(key, trans=('fade', 500), bar=False, notes=NOTES[key])
    CY, Y_N, Y_ST, ICY = 250, 350, 418, 584
    RK, GAP = 13 / (2 * RO), 9                 # 고리 굵기 13px, 고리와 얼굴 사이
    rf = RO - 13 - GAP                         # 얼굴 반지름
    s.add(key + '/title', [N.title(key + '/title', N.FX_TITLE)])
    cols = []
    for i, (pct, stmt, _, after, _) in enumerate(SURVEY):
        cx, k = CXS[i], '%s/c%d' % (key, i + 1)
        st = (SHIFT, 0) if i == 0 else None
        track, navy, purple = ring_set(k, cx, CY, pct, k=RK)
        s.add(k + '/track', track, start=st)
        s.add(k + '/arc0', navy, temp=True)
        s.add(k + '/arc', purple)
        s.add(k + '/disc0', [R(k + '/disc0', cx - rf, CY - rf, 2 * rf, 2 * rf, prst='ellipse', fill=NAVY, line=None)], temp=True)
        s.add(k + '/disc', [R(k + '/disc', cx - rf - PAD, CY - rf - PAD, 2 * (rf + PAD), 2 * (rf + PAD), prst='ellipse', fill=PURPLE, line=None)])
        eyes, m = big_face(k + '/f', cx, CY, 'FFFFFF', d=2 * rf, w=7)
        s.add(k + '/eyes', eyes, start=st)
        s.add(k + '/m', [m], start=st)
        s.add(k + '/num', [pct_text(k + '/num', cx, Y_N, pct, PURPLE, pt=40)])
        s.add(k + '/num0', [pct_text(k + '/num0', cx, Y_N, pct, NAVY, pt=40)], temp=True)
        s.add(k + '/st', [caption(k + '/st', [[(after[0], INK)], [(after[1], PURPLE)]], cx, Y_ST, size=ST_PT, lh=ST_LH)])
        s.add(k + '/st0', [caption(k + '/st0', [[(ln, INK)] for ln in stmt], cx, Y_ST, size=ST_PT, lh=ST_LH)], temp=True)
        cols.append((k, cx, st))
    add_weave(s, key, ICY)
    s.add(key + '/src', [N.foot(key + '/src', N.SURVEY_SRC)])
    first = ['/track', '/arc0', '/disc0', '/eyes', '/m', '/num0', '/st0']

    def card_in(i, t, t_fill):
        k, _, st = cols[i]
        show(s, k + '/track', 'fade_in', t, 350, st)
        show(s, k + '/disc0', 'zoom_in', t, 380, st, temp=True, **{'from': 0.8})
        show(s, k + '/eyes', 'fade_in', t + 80, 300, st)
        show(s, k + '/m', 'fade_in', t + 80, 300, st)
        s.on(k + '/m', 'spin', t + 80, 1, by=180)
        show(s, k + '/st0', 'fade_in', t + 150, 400, st, temp=True)
        show(s, k + '/arc0', 'wheel_in', t_fill, 800, st, temp=True)
        show(s, k + '/num0', 'zoom_in', t_fill + 620, 320, st, temp=True, **{'from': 0.86})
    card_in(0, 150, max(cue(key + '.n1', 1500, ahead=0.35), 600))
    s.click()      # 1
    slide_left(s, [cols[0][0] + x for x in first])
    card_in(1, 380, 640)
    s.click()      # 2
    card_in(2, 0, 260)
    s.click()      # 3
    weave_in(s, key)
    t0 = max(cue(key + '.face', 1500, ahead=0.3), 450)
    reach = wave(s, key, ICY, t0)
    for k, cx, _ in cols:
        t = reach(cx, CY) - 60
        s.on(k + '/arc', 'wheel_in', t, 750)
        s.on(k + '/disc', 'zoom_in', t + 120, 380, **{'from': 0.3})
        s.on(k + '/m', 'spin', t + 230, 330, by=180, accel=30000, decel=70000)
        s.on(k + '/arc0', 'fade_out', t + 760, 150)
        s.on(k + '/num0', 'fade_out', t + 500, 240)
        s.on(k + '/num', 'fade_in', t + 500, 280)
        s.on(k + '/st0', 'fade_out', t + 640, 240)
        s.on(k + '/st', 'fade_in', t + 880, 340)
    s.on(key + '/title', 'rise', max(cue(key + '.title', 4300, ahead=0.3), t0 + T_RING * 0.75), 520, dy=12)
    return s


def num_text(key, cx, cy, text, color, pt=40, small=21):
    """고리 한가운데의 숫자(가운데 맞춤)."""
    return T(key, cx - 110, cy - 34, 220, 68, [[(text, dict(size=pt)), ('%', dict(size=small))]], size=pt, color=color, weight='b', align='c',
             anchor='ctr', spc=-0.5)


def count_down(pct, n=12):
    """pct에서 0까지 줄어드는 동안 잠깐씩 보일 숫자들(처음과 끝은 천천히, 가운데는 빨리. 같은 숫자는 한 번만)."""
    out = []
    for j in range(1, n + 1):
        u = j / (n + 1)
        v = round(pct * (1 - u * u * (3 - 2 * u)))
        if 0 < v and (not out or out[-1] != v):
            out.append(v)
    return out


def s_fxg():
    """줄어드는 숫자: 표정 없이 고리 안에 숫자 → 불편 문장. (클릭) 물결이 닿으면 숫자가 0까지 줄고 고리도 비워진다. 불편 문장은 옅어진다 → 제목."""
    key = 'fxg'
    s = Slide(key, trans=('fade', 500), bar=False, notes=NOTES[key])
    ROG, CY, Y_ST, ICY, T_C = 100, 262, 384, 584, 1400
    s.add(key + '/title', [N.title(key + '/title', N.FX_TITLE)])
    cols = []
    for i, (pct, stmt, _, _, _) in enumerate(SURVEY):
        cx, k = CXS[i], '%s/c%d' % (key, i + 1)
        st = (SHIFT, 0) if i == 0 else None
        track, navy, _ = ring_set(k, cx, CY, pct, ro=ROG)
        s.add(k + '/track', track, start=st)
        s.add(k + '/arc0', navy, temp=True)
        s.add(k + '/num', [num_text(k + '/num', cx, CY, '0', PURPLE)])
        s.add(k + '/num0', [num_text(k + '/num0', cx, CY, '%.1f' % pct, NAVY)], temp=True)
        frames = []
        for j, v in enumerate(count_down(pct)):
            frames.append(s.add('%s/n%d' % (k, j), [num_text('%s/n%d' % (k, j), cx, CY, str(v), PURPLE)], temp=True))
        s.add(k + '/st', [caption(k + '/st', [[(ln, GRAY)] for ln in stmt], cx, Y_ST, size=ST_PT, lh=ST_LH)])
        s.add(k + '/st0', [caption(k + '/st0', [[(ln, INK)] for ln in stmt], cx, Y_ST, size=ST_PT, lh=ST_LH)], temp=True)
        cols.append((k, cx, st, frames))
    add_weave(s, key, ICY)
    s.add(key + '/src', [N.foot(key + '/src', N.SURVEY_SRC)])
    first = ['/track', '/arc0', '/num0', '/st0']

    def card_in(i, t, t_fill):
        k, _, st, _ = cols[i]
        show(s, k + '/track', 'fade_in', t, 350, st)
        show(s, k + '/st0', 'fade_in', t + 150, 400, st, temp=True)
        show(s, k + '/arc0', 'wheel_in', t_fill, 800, st, temp=True)
        show(s, k + '/num0', 'zoom_in', t_fill + 420, 320, st, temp=True, **{'from': 0.86})
    card_in(0, 150, max(cue(key + '.n1', 1500, ahead=0.35), 600))
    s.click()      # 1
    slide_left(s, [cols[0][0] + x for x in first])
    card_in(1, 380, 640)
    s.click()      # 2
    card_in(2, 0, 260)
    s.click()      # 3: 물결이 닿으면 숫자가 0까지 줄고 고리가 비워짐
    weave_in(s, key)
    t0 = max(cue(key + '.face', 1500, ahead=0.3), 450)
    reach = wave(s, key, ICY, t0)
    for k, cx, _, frames in cols:
        t = reach(cx, CY) - 60
        dt = T_C / (len(frames) + 1)
        s.on(k + '/arc0', 'wheel_out', t, T_C)
        s.on(k + '/num0', 'fade_out', t + dt, 1)
        for j, fk in enumerate(frames):
            s.on(fk, 'jump', t + (j + 1) * dt)
            s.on(fk, 'appear', t + (j + 1) * dt, 1)
            s.on(fk, 'fade_out', t + (j + 2) * dt, 1)
        s.on(k + '/num', 'appear', t + T_C, 1)
        s.on(k + '/st0', 'fade_out', t + T_C - 300, 260)
        s.on(k + '/st', 'fade_in', t + T_C - 300, 300)
    s.on(key + '/title', 'rise', max(cue(key + '.title', 4300, ahead=0.3), t0 + T_RING * 0.75), 520, dy=12)
    return s


# ------------------------------------------------------------------ 3차 후보(J~L): 풀린 뒤에는 숫자도 그림도 그 퍼센트를 가리키지 않게
J_TAIL = ('(클릭) Weave가 있다면 이 표정이 달라집니다. '
          '기록 통합 검색, 단서로 찾는 기억, 먼저 건네는 기억이 찾는 시간은 줄이고, 놓친 기억은 되살립니다.')
NOTES3 = dict(fxj=PCT_HEAD + J_TAIL, fxk=PCT_HEAD + TAIL % '표정이', fxl=PCT_HEAD + TAIL % '표정이')
CUES3 = {'fxj.n1': ('fxj', 0, '83.8%'),
         'fxj.f1': ('fxj', 3, '기록 통합 검색,'), 'fxj.f2': ('fxj', 3, '단서로 찾는 기억,'), 'fxj.f3': ('fxj', 3, '먼저 건네는 기억이'),
         'fxj.title': ('fxj', 3, '찾는 시간은')}
for _k in ('fxk', 'fxl'):
    CUES3.update({_k + '.n1': (_k, 0, '83.8%'), _k + '.face': (_k, 3, '이 표정이'), _k + '.title': (_k, 3, '찾는 시간은')})
NOTES.update(NOTES3)
CUES.update(CUES3)
HW.NOTES.update(NOTES3)
HW.CUES.update(CUES3)
RING_FIRST = ['/track', '/arc0', '/eyes0', '/m0', '/num0', '/st0']       # 처음 모습의 부품(첫째 칸은 이것들이 가운데에서 왼쪽으로 옮겨 감)


def donut(key, cx, cy, ro, thick, color):
    """한 바퀴 닫힌 고리. thick = 굵기(px)."""
    return R(key, cx - ro, cy - ro, 2 * ro, 2 * ro, prst='donut', fill=color, line=None, adj=dict(adj=round(thick / (2 * ro) * 100000)))


def ring_faces(s, key, CY, Y_N, Y_ST):
    """고리 얼굴 셋의 처음 모습(바탕 고리, 짙은 호, 시무룩한 얼굴, 짙은 숫자, 불편 문장)과 풀린 뒤의 얼굴(한 바퀴 닫힌 보라 고리, 웃는 얼굴)을 넣는다.
    처음에만 보이는 것은 temp. 돌려줌: [(부품 키 앞머리, 가운데 x, 처음 자리까지)]."""
    cols = []
    thick = N.RING_K * 2 * RO
    for i, (pct, stmt, _, _, _) in enumerate(SURVEY):
        cx, k = CXS[i], '%s/c%d' % (key, i + 1)
        st = (SHIFT, 0) if i == 0 else None
        track, navy, _ = ring_set(k, cx, CY, pct)
        s.add(k + '/track', track, start=st)
        s.add(k + '/arc0', navy, temp=True)
        s.add(k + '/full', [donut(k + '/full', cx, CY, RO + PAD, thick + 2 * PAD, PURPLE)])     # 짙은 호와 빈 자리를 함께 덮음
        e0, m0 = big_face(k + '/f0', cx, CY, NAVY)
        e1, m1 = big_face(k + '/f1', cx, CY, PURPLE)
        s.add(k + '/eyes0', e0, temp=True)
        s.add(k + '/m0', [m0], temp=True)
        s.add(k + '/eyes', e1)
        s.add(k + '/m', [m1])
        s.add(k + '/num0', [pct_text(k + '/num0', cx, Y_N, pct, NAVY, pt=40)], temp=True)
        s.add(k + '/st0', [caption(k + '/st0', [[(ln, INK)] for ln in stmt], cx, Y_ST, size=ST_PT, lh=ST_LH)], temp=True)
        cols.append((k, cx, st))
    return cols


def ring_in(s, col, t, t_fill):
    """고리 얼굴 하나가 뜬다: 바탕 고리와 시무룩한 얼굴 → 불편 문장 → 짙은 호가 차오르고 숫자."""
    k, _, st = col
    show(s, k + '/track', 'fade_in', t, 350, st)
    show(s, k + '/eyes0', 'fade_in', t, 350, st, temp=True)
    show(s, k + '/m0', 'fade_in', t, 350, st, temp=True)
    s.on(k + '/m0', 'spin', t, 1, by=180)                      # 웃는 모양으로 그린 입을 반 바퀴 돌려 둠
    show(s, k + '/st0', 'fade_in', t + 150, 400, st, temp=True)
    show(s, k + '/arc0', 'wheel_in', t_fill, 800, st, temp=True)
    show(s, k + '/num0', 'zoom_in', t_fill + 620, 320, st, temp=True, **{'from': 0.86})


def ring_open(s, key, cols):
    """장이 열릴 때부터 세 설문이 다 뜰 때까지: 첫째는 가운데에 → (클릭) 왼쪽으로 비키고 둘째 → (클릭) 셋째."""
    ring_in(s, cols[0], 150, max(cue(key + '.n1', 1500, ahead=0.35), 600))
    s.click()
    slide_left(s, [cols[0][0] + x for x in RING_FIRST])
    ring_in(s, cols[1], 380, 640)
    s.click()
    ring_in(s, cols[2], 0, 260)


def ring_smile(s, k, t, dur=780, turn=230, spin=330):
    """고리가 보라로 한 바퀴 닫히고(그래프 → 얼굴의 테두리) 입꼬리가 돌아 웃는다. turn = 입꼬리가 돌기 시작하는 때(t부터), spin = 도는 시간."""
    s.on(k + '/full', 'wheel_in', t, dur)
    s.on(k + '/m0', 'spin', t + turn, spin, by=180, accel=30000, decel=70000)
    s.on([k + '/eyes0', k + '/m0'], 'fade_out', t + turn + spin, 200)
    s.on([k + '/eyes', k + '/m'], 'fade_in', t + turn + spin - 20, 220)
    s.on(k + '/arc0', 'fade_out', t + dur, 150)


def s_fxj():
    """숫자가 기능 이름으로: 고리 얼굴, 숫자, 불편 문장. (클릭) 아래 가운데에 Weave 아이콘 → 기능을 말할 때마다 실이 뻗어 그 칸에 닿고,
    고리가 닫히며 웃고, 숫자가 뒤집혀 기능 이름이 되고, 불편 문장이 달라진 한 줄로 바뀐다 → 제목."""
    key = 'fxj'
    s = Slide(key, trans=('fade', 500), bar=False, notes=NOTES[key])
    CY, Y_N, Y_ST, ICY = 244, 344, 412, 590
    s.add(key + '/title', [N.title(key + '/title', N.FX_TITLE)])
    cols = ring_faces(s, key, CY, Y_N, Y_ST)
    for i, (k, cx, _) in enumerate(cols):
        s.add(k + '/lab', feat_label(k + '/lab', cx, Y_N + 12, i + 1, SURVEY[i][2], pt=21, r=15))
        s.add(k + '/gain', [caption(k + '/gain', [[(SURVEY[i][3][1], PURPLE)]], cx, Y_ST, size=ST_PT, lh=ST_LH)])
    z, ey = 56, Y_ST + 54
    paths = [[(640 - z / 2 - 3, ICY), (460, ICY), (CXS[0], ICY + 6), (CXS[0], ey)],
             [(640, ICY - z / 2 - 3)] * 2 + [(CXS[1], ey)] * 2,
             [(640 + z / 2 + 3, ICY), (820, ICY), (CXS[2], ICY + 6), (CXS[2], ey)]]
    for i, pts in enumerate(paths):
        s.add('%s/th%d' % (key, i + 1), thread('%s/th%d' % (key, i + 1), pts, w=2.6))
    s.add(key + '/halo', [halo(key + '/halo', 640, ICY, 96)])
    s.add(key + '/rg', [R(key + '/rg', 640 - 74, ICY - 74, 148, 148, prst='ellipse', fill=None, line=PURPLE2, line_w=2.6, line_alpha=80)], temp=True)
    s.add(key + '/icon', weave_mark(key + '/icon', 640, ICY, z))
    s.add(key + '/src', [N.foot(key + '/src', N.SURVEY_SRC)])
    ring_open(s, key, cols)
    s.click()      # 3: Weave와 제목 → 기능을 말할 때마다 그 칸이 풀림
    s.on(key + '/icon', 'zoom_in', 0, 340, **{'from': 0.6})
    s.on(key + '/halo', 'fade_in', 100, 500)
    s.on(key + '/rg', 'jump', 160)
    s.on(key + '/rg', 'ring', 160, 900, **{'from': 0.4, 'to': 1.0})
    ts = [cue(key + '.f1', 2900, ahead=0.45), cue(key + '.f2', 4300, ahead=0.45), cue(key + '.f3', 5800, ahead=0.45)]
    ts[0] = max(ts[0], 700)
    s.on(key + '/title', 'rise', max(cue(key + '.title', 7600, ahead=0.3), ts[2] + 900), 520, dy=12)       # 제목은 그 말을 할 때
    for i, (k, _, _) in enumerate(cols):
        t = ts[i]
        s.on(k + '/st0', 'fade_out', t, 240)                       # 불편 문장이 먼저 물러나고(실 끝이 그 자리를 지남)
        s.on('%s/th%d' % (key, i + 1), 'wipe_in', t + 60, 380, dir=('right', 'up', 'left')[i])
        t2 = t + 340
        ring_smile(s, k, t2)
        s.on(k + '/num0', 'flip_out', t2 + 240, 190)
        s.on(k + '/lab', 'flip_in', t2 + 430, 260)
        s.on(k + '/gain', 'fade_in', t2 + 620, 320)
    return s


def num_under(key, cx, y, text, color, pt=40, small=20):
    """고리 아래 숫자(가운데 맞춤). pct_text와 같은 자리에 놓인다(줄어드는 숫자의 토막)."""
    return T(key, cx - 114, y, 220, round(pt * 1.42), [[(text, dict(size=pt)), ('%', dict(size=small))]], size=pt, color=color, weight='b',
             align='c', anchor='ctr', spc=-0.5)


def s_fxk(key='fxk', count=False):
    """숫자가 물러남: 고리 얼굴, 숫자, 불편 문장. (클릭) Weave 아이콘에서 물결이 퍼지고, 닿는 칸부터 고리가 닫히며 웃는다.
    숫자는 사라지고(count면 0까지 줄어든 뒤 사라지고) 그 자리에 달라진 두 줄이 올라온다 → 제목."""
    s = Slide(key, trans=('fade', 500), bar=False, notes=NOTES[key])
    CY, Y_N, Y_ST, Y_G, ICY, T_C = 250, 350, 418, 366, 584, 1100
    s.add(key + '/title', [N.title(key + '/title', N.FX_TITLE)])
    cols = ring_faces(s, key, CY, Y_N, Y_ST)
    frames = {}
    for i, (k, cx, _) in enumerate(cols):
        after = SURVEY[i][3]
        s.add(k + '/st', [caption(k + '/st', [[(after[0], INK)], [(after[1], PURPLE)]], cx, Y_G, size=21, lh=32)])
        if count:
            frames[k] = [s.add('%s/n%d' % (k, j), [num_under('%s/n%d' % (k, j), cx, Y_N, str(v), NAVY)], temp=True)
                         for j, v in enumerate(count_down(SURVEY[i][0]) + [0])]
    add_weave(s, key, ICY)
    s.add(key + '/src', [N.foot(key + '/src', N.SURVEY_SRC)])
    ring_open(s, key, cols)
    s.click()      # 3: 물결이 닿는 칸부터 풀림
    weave_in(s, key)
    t0 = max(cue(key + '.face', 1500, ahead=0.3), 450)
    reach = wave(s, key, ICY, t0)
    for k, cx, _ in cols:
        t = reach(cx, CY) - 60
        if count:                               # 숫자가 줄어드는 동안 고리가 닫힘
            fr = frames[k]
            dt = T_C / len(fr)
            ring_smile(s, k, t, dur=T_C, turn=T_C - 420)       # 숫자가 0에 가까워질 때 웃음
            s.on(k + '/num0', 'fade_out', t + dt, 1)
            for j, fk in enumerate(fr):
                s.on(fk, 'jump', t + (j + 1) * dt)
                s.on(fk, 'appear', t + (j + 1) * dt, 1)
                last = j == len(fr) - 1
                s.on(fk, 'fade_out', t + (j + 2) * dt + (260 if last else 0), 240 if last else 1)      # 0은 잠깐 머물다 사라짐
            t_out = t + T_C + dt + 500
        else:
            ring_smile(s, k, t)
            s.on(k + '/num0', 'zoom_out', t + 300, 280, to=0.8)
            t_out = t + 800
        s.on(k + '/st0', 'fade_out', t + (T_C - 500 if count else 360), 240)
        s.on(k + '/st', 'rise', t_out, 420, dy=10)
    s.on(key + '/title', 'rise', max(cue(key + '.title', 4300, ahead=0.3), t0 + T_RING * 0.75), 520, dy=12)
    return s


# ------------------------------------------------------------------ 확정(11-13 6차): 후보 L(숫자가 0으로)을 손본 판 — 덱의 기대효과 한 장(키 fx)
# 사용자 검토로 바꾼 곳
# - 위 제목은 AS-IS(짙은 고리가 뜨는 동안) → Weave가 뜨면 TO-BE. 예전 제목(찾는 시간은 줄이고, 놓친 기억은 되살립니다)은 아래 가운데로.
#   위에서부터 위 제목, 고리 얼굴, Weave 아이콘, 아래 제목 차례가 되게 고리를 조금 줄이고 아이콘을 올림.
# - Weave 아이콘에서 칸마다 실이 뻗는다(후보 J처럼, 달라진 글 바로 아래까지). 기능을 말하는 차례로 한 칸씩 풀린다.
# - 고리 아래 숫자를 고리 한가운데에 맞춤(왼쪽으로 4px 치우쳐 있었음). 숫자가 줄어드는 속도와 표정이 바뀌는 속도를 조금 늦춤.
# - 글: '앱을 하나씩 열어 봤어요' → '하나씩 열어 봤어요', '검색으로 찾지 못했어요' → '검색하지 못했어요'. 달라진 글은 더 짧게.
# 11-13 7차
# - 첫 칸의 숫자를 설문의 83.8%에서 '59분'으로(최종제출본의 기대효과에 쓰던 Qatalog와 코넬대의 조사. 글은 그대로). 고리는 한 시간 가운데 59분만큼 차고,
#   풀릴 때 0분까지 줄어든다. 출처가 둘이 되어 불편 문장 끝에 번호를 달고 각주에 둘 다 적음.
# - 실 세 가닥을 클릭 셋으로 나눔(발표자가 기능 이름마다 누름). 이름 사이는 0.2초만 쉬므로 앞 칸의 효과가 끝나기 전에 다음 클릭이 온다
#   → 장을 free로(클릭해도 앞 효과가 끊기지 않고 이어짐).
# - 실을 조금 굵게(2.6 → 3.8px). 숫자가 0이 되면 곧바로 달라진 글로 바뀌게(0이 0.5초쯤 머물던 것을 없앰).
FX_SRC = '* ¹ Qatalog & Cornell University Ellis Idea Lab, "Workgeist Report" (2021. 06)   ² ' + N.SURVEY_SRC[2:]
FX_ROWS = [     # (숫자, 단위, 고리에 차는 만큼(%), 불편 두 줄, 달라진 두 줄, 출처 번호)
    (59, '분', 59 / 60 * 100, ['어느 앱인지 몰라', '하나씩 열어 봤어요'], ['어느 앱인지 몰라도', '통합 검색으로 찾아요'], '¹'),
    (93.8, '%', 93.8, ['정확한 이름이 떠오르지 않아', '검색하지 못했어요'], ['정확한 이름을 몰라도', '단서로 찾아요'], '²'),
    (82.4, '%', 82.4, ['챙겨야 할 부탁, 약속을', '나중에야 떠올렸어요'], ['챙겨야 할 부탁, 약속을', '묻기 전에 알려 줘요'], '²'),
]
# 11-13 8차: 발표자가 다시 쓴 글. 기능 이름만 늘어놓던 끝 문장이 기능마다 한 마디씩이 되어('어느 앱인지 몰라도 통합 검색으로 바로 찾고, …'),
#   이름 사이를 0.2초로 좁히던 틈 조정(GAP_EXTRA, LEAD_EXTRA)은 없앰. 첫째, 둘째 고리가 숫자를 말할 때까지 기다리던 것도 없앰(아래 s_fx).
FX_NOTE = ('조사에 따르면, 직장인은 여러 앱에 흩어진 정보를 찾아 활용하는 데 하루 59분을 쓰고 있었습니다. '       # 59분: Workgeist Report(미국과 영국의 원격 근무자 설문). 7차 뒤: '찾는 데' → '찾아 활용하는 데', '쓰고 있습니다' → '쓰고 있었습니다'(사용자 글)
           '(클릭) 93.8%는 정확한 이름이 떠오르지 않아 검색하지 못했으며, '       # 93.8%는 인트로 7쪽에서 본 숫자(같은 설문 6번)
           '(클릭) 82.4%는 부탁이나 약속을 잊었다가, 나중에야 떠올린 경험이 있었습니다. '
           '(클릭) Weave는 이러한 불편함을 해결합니다. '
           '(클릭) 어느 앱인지 몰라도 통합 검색으로 바로 찾고, (클릭) 정확한 이름을 몰라도 단서로 찾고, '
           '(클릭) 챙겨야 할 부탁이나 약속을 필요한 순간에 알려줌으로써, 찾는 시간은 줄이고, 놓친 기억은 되살립니다.')
FX_CUES = {'fx.title': ('fx', 6, '찾는 시간은')}
NOTES['fx'] = FX_NOTE
CUES.update(FX_CUES)
HW.NOTES['fx'] = FX_NOTE
HW.CUES.update(FX_CUES)
FX_RO = 82                          # 고리의 바깥 반지름(후보 때는 90)
FX_RK = 0.085                       # 고리 굵기 ÷ 바깥지름. 7차 뒤: 띠를 살짝 가늘게(인트로 7·8쪽과 같던 0.098 → 0.085, 164px 고리에서 16 → 14px)
FX_CY, FX_YN, FX_YST, FX_YG = 236, 326, 392, 338      # 고리 가운데, 숫자, 불편 문장, 달라진 문장의 위 끝
FX_ICY, FX_YB = 520, 584            # Weave 아이콘의 가운데, 아래 제목의 위 끝
FX_TC, FX_TURN = 1300, 400          # 숫자가 0까지 줄어드는 시간, 입꼬리가 도는 시간(후보 L은 1100, 330)
FX_TH = 3.8                         # 실의 굵기(7차: 2.6 → 3.8px. 모션그래픽과 14쪽의 실은 5.6px)


def num_mid(key, cx, y, text, color, pt=40, small=20, unit='%'):
    """고리 아래 숫자: 고리의 가운데 x에 가운데 맞춤."""
    return T(key, cx - 120, y, 240, round(pt * 1.42), [[(text, dict(size=pt)), (unit, dict(size=small))]], size=pt, color=color, weight='b',
             align='c', anchor='ctr', spc=-0.5)


def s_fx():
    """기대효과 한 장. 불편 셋이 고리 얼굴로 하나씩 뜨고(위 제목 AS-IS) → (클릭) Weave 아이콘이 뜨며 제목이 TO-BE로 뒤집히고,
    (클릭 셋) 기능을 말할 때마다 아이콘에서 실이 뻗어 그 칸에 닿는다. 닿은 칸은 숫자가 0까지 줄며 고리가 보라로 닫히고 웃는다.
    숫자가 0이 되면 곧바로 달라진 두 줄로 바뀌고, '찾는 시간은 …'을 말할 때 아래 제목이 뜬다."""
    key = 'fx'
    s = Slide(key, trans=('fade', 500), bar=False, notes=NOTES[key], free=True)
    s.add(key + '/to', [N.title(key + '/to', [('TO-BE', PURPLE)])])
    s.add(key + '/as', [N.title(key + '/as', [('AS-IS', NAVY)])], temp=True)
    thick = FX_RK * 2 * FX_RO
    cols, frames = [], {}
    for i, (num, unit, fill, stmt, after, ref) in enumerate(FX_ROWS):
        cx, k = CXS[i], '%s/c%d' % (key, i + 1)
        st = (SHIFT, 0) if i == 0 else None
        track, navy, _ = ring_set(k, cx, FX_CY, fill, ro=FX_RO, k=FX_RK)
        s.add(k + '/track', track, start=st)
        s.add(k + '/arc0', navy, temp=True)
        s.add(k + '/full', [donut(k + '/full', cx, FX_CY, FX_RO + PAD, thick + 2 * PAD, PURPLE)])     # 짙은 호와 빈 자리를 함께 덮음
        d = 150 * FX_RO / RO
        e0, m0 = big_face(k + '/f0', cx, FX_CY, NAVY, d=d)
        e1, m1 = big_face(k + '/f1', cx, FX_CY, PURPLE, d=d)
        s.add(k + '/eyes0', e0, temp=True)
        s.add(k + '/m0', [m0], temp=True)
        s.add(k + '/eyes', e1)
        s.add(k + '/m', [m1])
        s.add(k + '/num0', [num_mid(k + '/num0', cx, FX_YN, '%g' % num, NAVY, unit=unit)], temp=True)
        # 불편 문장: 둘째 줄 끝에 출처 번호(글은 가운데 맞춤 그대로 두고 번호만 줄 끝 바깥에 붙임)
        ref_x = cx + tw(stmt[1], ST_PT, 'b') / 2 + 1
        s.add(k + '/st0', [caption(k + '/st0/t', [[(ln, INK)] for ln in stmt], cx, FX_YST, size=ST_PT, lh=ST_LH),
                           T(k + '/st0/ref', ref_x, FX_YST + ST_LH, 16, 20, ref, size=13.5, color=SUB)], temp=True)
        s.add(k + '/st', [caption(k + '/st', [[(after[0], INK)], [(after[1], PURPLE)]], cx, FX_YG, size=21, lh=32)])
        frames[k] = [s.add('%s/n%d' % (k, j), [num_mid('%s/n%d' % (k, j), cx, FX_YN, str(v), NAVY, unit=unit)], temp=True)
                     for j, v in enumerate(count_down(num) + [0])]
        cols.append((k, cx, st))
    # 아래 가운데의 Weave와 칸마다 뻗는 실(달라진 글 바로 아래까지)
    z, ey = 56, FX_YG + 2 * 32 + 14
    paths = [[(640 - z / 2 - 3, FX_ICY), (460, FX_ICY), (CXS[0], FX_ICY + 6), (CXS[0], ey)],
             [(640, FX_ICY - z / 2 - 3)] * 2 + [(CXS[1], ey)] * 2,
             [(640 + z / 2 + 3, FX_ICY), (820, FX_ICY), (CXS[2], FX_ICY + 6), (CXS[2], ey)]]
    for i, pts in enumerate(paths):
        s.add('%s/th%d' % (key, i + 1), thread('%s/th%d' % (key, i + 1), pts, w=FX_TH))
    s.add(key + '/halo', [halo(key + '/halo', 640, FX_ICY, 96)])
    s.add(key + '/rg', [R(key + '/rg', 640 - 56, FX_ICY - 56, 112, 112, prst='ellipse', fill=None, line=PURPLE2, line_w=2.6, line_alpha=80)], temp=True)      # 위의 불편 문장에 닿지 않는 크기
    s.add(key + '/icon', weave_mark(key + '/icon', 640, FX_ICY, z))
    s.add(key + '/sub', [N.title(key + '/sub', N.FX_TITLE, y=FX_YB)])
    s.add(key + '/src', [N.foot(key + '/src', FX_SRC)])
    # 장이 열리면: AS-IS, 첫째 불편이 가운데에 → (클릭) 왼쪽으로 비키고 둘째 → (클릭) 셋째
    # 11-13 8차: 첫째, 둘째 고리도 셋째처럼 뜨자마자 곧바로 차오름(전에는 '59분', '93.8%'를 말할 때까지 기다려서 눌러도 한참 뒤에 움직였음)
    show(s, key + '/as', 'fade_in', 100, 350, temp=True)
    ring_in(s, cols[0], 150, 410)
    s.click()
    slide_left(s, [cols[0][0] + x for x in RING_FIRST], dur=560)                 # 첫째가 왼쪽으로 비키자마자(0.45초) 둘째가 그 자리에
    ring_in(s, cols[1], 280, 540)
    s.click()
    ring_in(s, cols[2], 0, 260)
    s.click()      # 3: Weave가 뜨고 제목이 TO-BE로
    s.on(key + '/icon', 'zoom_in', 0, 340, **{'from': 0.6})
    s.on(key + '/halo', 'fade_in', 100, 500)
    s.on(key + '/rg', 'jump', 160)
    s.on(key + '/rg', 'ring', 160, 900, **{'from': 0.4, 'to': 1.0})
    s.on(key + '/as', 'flip_out', 220, 190)
    s.on(key + '/to', 'flip_in', 410, 260)
    for i, (k, _, _) in enumerate(cols):
        s.click()      # 4~6: 기능 이름을 말할 때마다 실이 그 칸으로 뻗고, 닿으면 숫자가 줄며 고리가 닫힘
        s.on(k + '/st0', 'fade_out', 0, 240)                       # 불편 문장이 먼저 물러나고(실 끝이 그 자리를 지남)
        s.on('%s/th%d' % (key, i + 1), 'wipe_in', 60, 420, dir=('right', 'up', 'left')[i])
        t2 = 400
        fr = frames[k]
        dt = FX_TC / len(fr)
        ring_smile(s, k, t2, dur=FX_TC, turn=FX_TC - FX_TURN - 120, spin=FX_TURN)      # 숫자가 0에 가까워질 때 웃음
        s.on(k + '/num0', 'fade_out', t2 + dt, 1)
        for j, fk in enumerate(fr):
            s.on(fk, 'jump', t2 + (j + 1) * dt)
            s.on(fk, 'appear', t2 + (j + 1) * dt, 1)
            last = j == len(fr) - 1
            s.on(fk, 'fade_out', t2 + (j + 2) * dt + (-10 if last else 0), 130 if last else 1)      # 0은 뜨자마자 물러남
        s.on(k + '/st', 'rise', t2 + FX_TC + dt + 50, 400, dy=10)                                  # 그 자리에 달라진 두 줄
    s.on(key + '/sub', 'rise', max(cue(key + '.title', 2600, ahead=0.3), 900), 520, dy=12)       # 아래 제목은 그 말을 할 때(셋째 실의 클릭 뒤)
    return s


CANDIDATES = [('A', 'fxa', s_fxa, '실 세 가닥'), ('B', 'fxb', s_fxb, '세 물음'), ('C', 'fxc', s_fxc, '물결'),
              ('D', 'fxd', s_fxd, '고리 얼굴'), ('E', 'fxe', s_fxe, '고리 속 얼굴'), ('F', 'fxf', lambda: s_fxd('fxf', badge=True), 'AS-IS → TO-BE'),
              ('G', 'fxg', s_fxg, '줄어드는 숫자'), ('H', 'fxh', lambda: s_fxc('fxh', people=True), '몸통 있는 사람'),
              ('J', 'fxj', s_fxj, '숫자가 기능 이름으로'), ('K', 'fxk', s_fxk, '숫자가 물러남'), ('L', 'fxl', lambda: s_fxk('fxl', count=True), '숫자가 0으로'),
              ('M', 'fx', s_fx, 'L을 손본 판')]
CURRENT = 'M'                       # 지금 장(11-13: 3차의 L을 골라 손본 판, 덱의 32쪽). A~L은 앞선 차수(영상은 기대효과_후보/이전판, 저장소에는 올리지 않음)
