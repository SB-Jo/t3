"""기존 기능과의 비교 장(5차 35쪽) 후보 — 두 축 지도(slides_new.s_cmp)를 바꾸는 안. 11-12 밤.
11-13 6차: 비교 장은 본 발표에서 빼고, 후보 나에 글을 보탠 판을 Appendix 맨 앞에 둔다(s_cmp_apx. 이 파일 끝).

사용자 검토
- 그림이 조금 오른쪽으로 치우쳐 있다.
- 우리 주장은 이산적인데(한 번에 찾기 아니면 단서를 이어 여러 단계로) 축이 연속적으로 보여 어색하다.
  → 이산에 맞는 그림을 쓰거나, 축 이름을 연속적인 것으로 바꾸고 기존 기능을 나란히가 아니라 조금씩 들쭉날쭉 놓는다. Weave만 오른쪽 위.

후보(넷 모두 그림 전체를 장 한가운데 x 640에 맞추고, Weave는 오른쪽 위. 제목과 말할 글은 지금 35쪽 그대로)
- cmpa '두 띠': 세로는 띠 둘(한 번에 찾는 검색 / 단서를 이어 찾는 검색), 가로는 찾는 범위. 기존 기능은 아래 띠 안에 높낮이를 달리해 놓인다.
  위 띠는 처음엔 비어 있다가(점선) 클릭하면 켜지며 Weave가 뜬다. 띠 안의 높낮이에는 뜻이 없다(자리 배치일 뿐).
- cmpb '넓이와 깊이': 가로 찾는 범위(좁게 → 넓게), 세로 찾는 깊이(얕게 → 깊게). 눈금과 점선 없이 끝 이름만. 기존 기능은 얕은 쪽에 들쭉날쭉.
  높낮이는 맥락을 얼마나 읽는지에 따라 조금만 달리했다(쓰는 글만 다듬는 Writing Assist가 가장 아래, 물은 말로 한 번 검색하는 Finder,
  지금 보는 대화에 맞춰 제안하는 Now Nudge, 대화를 읽고 먼저 제안하는 카나나 차례로 조금씩 위).
- cmpc '네 칸': 2×2 칸(앱 하나 안에서 / 여러 앱에 걸쳐 × 한 번에 / 단서를 이어 여러 단계로). 기존 기능은 아래 두 칸, Weave는 오른쪽 위 칸.
- cmpd '계단': 한 번에 찾는 검색이 아랫단, 단서를 이어 찾는 검색이 윗단.
기존 기능은 이름을 말할 때 하나씩 뜨고, (클릭) Weave가 뜬다(지금 장과 같은 차례).
"""
import build as HW
from ui import ICON, INK, INK2, LAV, LINE, LINE2, MUTE, PURPLE, SUB, C, P, R, T, thread

import slides_new as N

Slide, cue = HW.Slide, HW.cue
TITLE = [('한 번의 검색을 넘어, ', INK), ('단서를 이어 찾는 검색', PURPLE), ('으로', INK)]
SERV = [('wa', 'writing', 'Writing Assist'), ('kanana', 'kanana', '카나나'), ('nudge', 'nudge', 'Now Nudge'), ('finder', 'finder', 'Finder')]
KEYS = ('cmpa', 'cmpb', 'cmpc', 'cmpd')
NOTES = {k: N.NOTES['cmp'] for k in KEYS}
CUES = {}
for _k in KEYS:
    CUES.update({_k + '.wa': (_k, 0, 'Writing Assist는'), _k + '.kn': (_k, 0, '카나나는'), _k + '.nn': (_k, 0, 'Now Nudge와')})
HW.NOTES.update(NOTES)
HW.CUES.update(CUES)
ONCE, MULTI = '한 번에 찾는 검색', '단서를 이어 찾는 검색'
GRAD = dict(stops=[(0, '8D6BFF', None), (100, '5A3FE0', None)], ang=55)


# ------------------------------------------------------------------ 함께 쓰는 조각
def base(key):
    s = Slide(key, trans=('fade', 500), bar=False, notes=NOTES[key])
    s.add(key + '/title', [N.title(key + '/title', TITLE)])
    return s


def weave_tile(key, x, y, z=66, name_y=None):
    """Weave 아이콘 + 이름(지금 비교 장과 같은 모양). name_y를 주면 이름을 그 높이에."""
    k = z / 66
    return [R(key + '/tile', x - z / 2, y - z / 2, z, z, prst='roundRect', radius=19 * k, line='FFFFFF', line_w=2.5, shadow=(18, 6, '6B4EFF', 30),
              grad=GRAD),
            P(key + '/sp', ICON['spool_w'], x - 20 * k, y - 20 * k, 40 * k, 40 * k),
            T(key + '/name', x - 110, y + z / 2 + 6 if name_y is None else name_y, 220, 28, 'Weave Assist', size=17, color=PURPLE, weight='b',
              align='c', anchor='ctr')]


def glow(key, x, y, r=120):
    return R(key, x - r, y - r, 2 * r, 2 * r, prst='ellipse', fill=None, line=None,
             grad=dict(stops=[(0, '8B6BFF', 40), (36, 'B9A6FF', 15), (70, 'F2EDFF', 0), (100, 'F2EDFF', 0)], path='circle'))


def add_points(s, key, pts):
    for k, kind, name in SERV:
        s.add('%s/%s' % (key, k), N.map_point('%s/%s' % (key, k), kind, name, *pts[k]))


def reveal(s, key):
    """기존 기능은 이름을 말할 때 하나씩(Now Nudge와 Finder는 한 문장에 이어 나와 바로 뒤따름)."""
    t_wa, t_kn, t_nn = cue(key + '.wa', 3300, ahead=0.2), cue(key + '.kn', 5600, ahead=0.2), cue(key + '.nn', 7700, ahead=0.2)
    for k, t in (('wa', t_wa), ('kanana', t_kn), ('nudge', t_nn), ('finder', t_nn + 620)):
        s.on('%s/%s' % (key, k), 'zoom_in', t, 380, **{'from': 0.6})


def weave_on(s, key, t):
    s.on(key + '/weave', 'zoom_in', t, 420, **{'from': 0.6})
    s.on(key + '/weave', 'pulse', t + 460, 180, scale=1.08)


# ------------------------------------------------------------------ 가: 두 띠
def s_cmpa():
    """세로는 띠 둘(이산), 가로는 찾는 범위. 기존 기능은 아래 띠 안에 높낮이를 달리해 놓인다. 위 띠는 처음엔 비어 있고(점선),
    (클릭) 켜지며 Finder에서 위로 화살표가 뻗고 Weave가 뜬다."""
    key = 'cmpa'
    s = base(key)
    X0, W = 170, 940
    UY, UH, LY, LH, AY = 148, 152, 312, 232, 570
    pts = {'wa': (322, 468), 'kanana': (524, 410), 'nudge': (726, 460), 'finder': (940, 402)}
    wx, wy = 940, 214
    band = lambda k, y, h, t, col, **o: [R(k + '/bg', X0, y, W, h, prst='roundRect', radius=22, **o),
                                         T(k + '/t', X0 + 24, y + 12, 300, 26, t, size=13.5, color=col, weight='b', anchor='ctr')]
    s.add(key + '/lo', band(key + '/lo', LY, LH, ONCE, SUB, fill='FFFFFF', alpha=70, line=LINE, line_w=1.0))
    s.add(key + '/up0', band(key + '/up0', UY, UH, MULTI, 'A9A3BA', fill=None, line='C9C0E8', line_w=1.3, dash='dash'), temp=True)
    s.add(key + '/up', band(key + '/up', UY, UH, MULTI, PURPLE, fill=LAV, line=LINE2, line_w=1.3))
    s.add(key + '/ax', [C(key + '/ax', [(X0 + 100, AY)] * 2 + [(X0 + W - 6, AY)] * 2, color=N.MAP_AX, w=1.8, tail='triangle')])
    lab = lambda k, x, t, **o: T('%s/axl/%s' % (key, k), x - 80, AY + 8, 160, 24, t, align='c', anchor='ctr', **o)
    s.add(key + '/axl', [T(key + '/axl/n', X0 + 6, AY - 12, 90, 24, '찾는 범위', size=13.5, color=SUB, weight='b', anchor='ctr'),
                         lab('x0', pts['wa'][0], '쓰는 글', size=12.5, color=MUTE), lab('x1', pts['kanana'][0], '앱 하나', size=12.5, color=MUTE),
                         lab('x2', wx, '여러 앱', size=12.5, color=PURPLE, weight='b')])
    add_points(s, key, pts)
    s.add(key + '/arrow', thread(key + '/arrow', [(wx, pts['finder'][1] - 34)] * 2 + [(wx, UY + UH - 8)] * 2, w=2.6, tail='triangle'))
    s.add(key + '/weave', weave_tile(key + '/weave', wx, wy))
    s.add(key + '/src', [N.foot(key + '/src', N.CMP_SRC)])
    s.on(key + '/lo', 'fade_in', 150, 400)
    s.on(key + '/up0', 'jump', 300)
    s.on(key + '/up0', 'fade_in', 300, 400)
    s.on(key + '/ax', 'wipe_in', 450, 500)
    s.on(key + '/axl', 'fade_in', 750, 400)
    reveal(s, key)
    s.click()      # 1: 비어 있던 위 띠가 켜지고, 한 번을 넘어 위로 → Weave
    s.on(key + '/up', 'fade_in', 0, 400)
    s.on(key + '/up0', 'fade_out', 200, 250)
    s.on(key + '/arrow', 'wipe_in', 280, 420, dir='up')
    weave_on(s, key, 560)
    return s


# ------------------------------------------------------------------ 나: 넓이와 깊이(축 이름을 연속적인 것으로)
def s_cmpb():
    """가로 찾는 범위(좁게 → 넓게), 세로 찾는 깊이(얕게 → 깊게). 눈금과 점선 없이 끝 이름만 두고, 기존 기능은 얕은 쪽에 들쭉날쭉. (클릭) Weave."""
    key = 'cmpb'
    s = base(key)
    ox, oy, xe, yt = 262, 566, 1000, 176       # 왼쪽 끝 이름(190)에서 가로축 이름(1090)까지가 장 한가운데
    pts = {'wa': (ox + 118, oy - 64), 'kanana': (ox + 268, oy - 130), 'nudge': (ox + 418, oy - 98), 'finder': (ox + 566, oy - 74)}
    wx, wy = ox + 652, yt + 72
    s.add(key + '/axx', [C(key + '/axx', [(ox, oy)] * 2 + [(xe, oy)] * 2, color=N.MAP_AX, w=1.8, tail='triangle')])
    s.add(key + '/axy', [C(key + '/axy', [(ox, oy)] * 2 + [(ox, yt)] * 2, color=N.MAP_AX, w=1.8, tail='triangle')])
    lab = lambda k, x, y, w, t, **o: T('%s/axl/%s' % (key, k), x, y, w, 24, t, anchor='ctr', **o)
    s.add(key + '/axl', [lab('xn', xe + 10, oy - 12, 90, '찾는 범위', size=13.5, color=SUB, weight='b'),
                         lab('yn', ox - 80, yt - 34, 160, '찾는 깊이', size=13.5, color=SUB, weight='b', align='c'),
                         lab('x0', ox + 14, oy + 10, 80, '좁게', size=12.5, color=MUTE),
                         lab('x1', xe - 100, oy + 10, 80, '넓게', size=12.5, color=PURPLE, weight='b', align='r'),
                         lab('y0', ox - 72, oy - 40, 60, '얕게', size=12.5, color=MUTE, align='r'),
                         lab('y1', ox - 72, yt + 20, 60, '깊게', size=12.5, color=PURPLE, weight='b', align='r')])
    add_points(s, key, pts)
    s.add(key + '/wglow', [glow(key + '/wglow', wx, wy)])
    fx, fy = pts['finder']
    s.add(key + '/arrow', thread(key + '/arrow', [(fx + 8, fy - 36), (fx + 8, fy - 104), (wx, wy + 152), (wx, wy + 76)], w=2.6, tail='triangle'))
    s.add(key + '/weave', weave_tile(key + '/weave', wx, wy))
    s.add(key + '/src', [N.foot(key + '/src', N.CMP_SRC)])
    s.on(key + '/axx', 'wipe_in', 150, 600)
    s.on(key + '/axy', 'wipe_in', 150, 600, dir='up')
    s.on(key + '/axl', 'fade_in', 600, 450)
    reveal(s, key)
    s.click()      # 1: 얕은 쪽을 넘어 깊은 쪽으로 → Weave
    s.on(key + '/arrow', 'wipe_in', 0, 520, dir='up')
    s.on(key + '/wglow', 'fade_in', 300, 500)
    weave_on(s, key, 420)
    return s


# ------------------------------------------------------------------ 다: 네 칸
def s_cmpc():
    """2×2 칸: 가로 찾는 범위(앱 하나 안에서 / 여러 앱에 걸쳐), 세로 찾는 방식(한 번에 / 단서를 이어 여러 단계로). 기존 기능은 아래 두 칸에,
    (클릭) 오른쪽 위 칸이 보라로 켜지며 Weave가 뜬다."""
    key = 'cmpc'
    s = base(key)
    GX, GY, CW, CH, G = 284, 154, 366, 174, 12        # 줄 이름(세워 쓴 글, 왼쪽 30px)까지 넣어 장 한가운데
    cx = [GX, GX + CW + G]
    cy = [GY, GY + CH + G]
    cells = [R('%s/cell/%d%d' % (key, r, c), cx[c], cy[r], CW, CH, prst='roundRect', radius=20, fill='FFFFFF', alpha=68, line=LINE, line_w=1.0)
             for r in (0, 1) for c in (0, 1)]
    s.add(key + '/grid', cells)
    cl = lambda k, c, t, **o: T('%s/hd/%s' % (key, k), cx[c], cy[1] + CH + 8, CW, 26, t, align='c', anchor='ctr', **o)
    s.add(key + '/hd', [cl('c0', 0, '앱 하나 안에서', size=13.5, color=SUB, weight='b'), cl('c1', 1, '여러 앱에 걸쳐', size=13.5, color=PURPLE, weight='b')])
    for k, r, t, col in (('r0', 0, '단서를 이어 여러 단계로', PURPLE), ('r1', 1, '한 번에', SUB)):       # 줄 이름은 칸 왼쪽에 세워 씀
        s.add('%s/hd/%s' % (key, k), [T('%s/hd/%s' % (key, k), GX - 22 - 85, cy[r] + CH / 2 - 13, 170, 26, t, size=13.5, color=col, weight='b', align='c',
                                        anchor='ctr')], rot=270)
    y1 = cy[1] + CH / 2 - 14
    pts = {'wa': (cx[0] + 98, y1 - 8), 'kanana': (cx[0] + 268, y1 + 8), 'nudge': (cx[1] + 98, y1 + 8), 'finder': (cx[1] + 268, y1 - 8)}
    wx, wy = cx[1] + CW / 2, cy[0] + CH / 2 - 16
    add_points(s, key, pts)
    s.add(key + '/hot', [R(key + '/hot', cx[1], cy[0], CW, CH, prst='roundRect', radius=20, fill=LAV, line=LINE2, line_w=1.4, glow=(10, 'A78BFF', 26))])
    s.add(key + '/weave', weave_tile(key + '/weave', wx, wy))
    s.add(key + '/src', [N.foot(key + '/src', N.CMP_SRC)])
    s.on(key + '/grid', 'fade_in', 150, 450)
    s.on([key + '/hd', key + '/hd/r0', key + '/hd/r1'], 'fade_in', 450, 400)
    reveal(s, key)
    s.click()      # 1: 오른쪽 위 칸이 켜지고 Weave
    s.on(key + '/hot', 'fade_in', 0, 420)
    weave_on(s, key, 320)
    return s


# ------------------------------------------------------------------ 라: 계단
def s_cmpd():
    """계단 두 단(바닥이 같은 높이): 아랫단은 한 번에 찾는 검색(기존 기능 넷이 올라서 있음), (클릭) 윗단이 솟고 그 위에 Weave."""
    key = 'cmpd'
    s = base(key)
    BY = 572                                    # 두 단의 바닥
    LX, LW, LT = 190, 580, 424                  # 아랫단: 왼쪽, 폭, 윗면
    UX, UW, UT = 778, 312, 268                  # 윗단(아랫단 오른쪽에 8px 띄움)
    xs = {'wa': 266, 'kanana': 410, 'nudge': 554, 'finder': 698}
    iy = LT - 29
    s.add(key + '/lo', [R(key + '/lo/bg', LX, LT, LW, BY - LT, prst='roundRect', radius=20, fill='FFFFFF', alpha=74, line=LINE, line_w=1.0),
                        T(key + '/lo/t', LX + 28, BY - 42, 300, 26, ONCE, size=14, color=SUB, weight='b', anchor='ctr')])
    for k, kind, name in SERV:
        kk = '%s/%s' % (key, k)
        s.add(kk, N.cmp_icon(kk + '/ic', kind, xs[k], iy, 46) + [
            T(kk + '/name', xs[k] - 100, LT + 10, 200, 22, name, size=13.5, color=INK2, weight='b', align='c', anchor='ctr')])
    wx, wy = UX + UW / 2, UT - 41
    s.add(key + '/up', [R(key + '/up/bg', UX, UT, UW, BY - UT, prst='roundRect', radius=20, fill=LAV, line=LINE2, line_w=1.3),
                        T(key + '/up/t', UX, BY - 42, UW, 26, MULTI, size=14, color=PURPLE, weight='b', align='c', anchor='ctr')])
    s.add(key + '/weave', weave_tile(key + '/weave', wx, wy, name_y=UT + 12))
    fx = xs['finder']
    s.add(key + '/arrow', thread(key + '/arrow', [(fx + 34, iy - 16), (fx + 44, wy + 36), (UX + 6, wy), (wx - 46, wy)], w=2.6, tail='triangle'))
    s.add(key + '/src', [N.foot(key + '/src', N.CMP_SRC)])
    s.on(key + '/lo', 'rise', 150, 480, dy=14)
    reveal(s, key)
    s.click()      # 1: 윗단이 솟고, 한 단 위에 Weave
    s.on(key + '/up', 'rise', 0, 460, dy=18)
    s.on(key + '/arrow', 'wipe_in', 300, 460, dir='left')
    weave_on(s, key, 560)
    return s


# ------------------------------------------------------------------ Appendix의 비교 장(11-13 6차): 본 발표에서는 빼고, 질문이 나오면 꺼냄
# 후보 나(넓이와 깊이)에 글을 보탬: Writing Assist와 Finder 앞에 Samsung, 이름 아래에 무슨 기능인지 한 줄.
APX_SERV = [    # (키, 아이콘, 이름, 한 줄 설명, 축 원점에서의 자리(x, 위로 y))
    ('wa', 'writing', 'Samsung Writing Assist', '글을 다듬는 키보드 AI', (126, 92)),
    ('kanana', 'kanana', '카나나', '카카오톡 안의 AI 비서', (284, 158)),
    ('nudge', 'nudge', 'Now Nudge', '대화에 맞춰 건네는 제안', (426, 134)),
    ('finder', 'finder', 'Samsung Finder', '기기 안 기록 검색 앱', (592, 96)),
]
APX_WEAVE = '단서를 이어 찾는 키보드 AI'


def s_cmp_apx():
    """Appendix의 '기존 기능과의 비교'. 가로 찾는 범위(좁게 → 넓게), 세로 찾는 깊이(얕게 → 깊게). 기존 기능 넷은 장이 열리면 차례로 뜨고, (클릭) Weave.
    기능마다 이름 아래에 무슨 기능인지 한 줄을 붙였다."""
    key = 'apx_map'
    s = Slide(key, trans=('fade', 400), bar=False, notes=N.NOTES['cmp'])
    s.add(key + '/title', [N.title(key + '/title', TITLE)])
    ox, oy, xe, yt = 262, 566, 1000, 176
    wx, wy = ox + 652, yt + 66
    s.add(key + '/axx', [C(key + '/axx', [(ox, oy)] * 2 + [(xe, oy)] * 2, color=N.MAP_AX, w=1.8, tail='triangle')])
    s.add(key + '/axy', [C(key + '/axy', [(ox, oy)] * 2 + [(ox, yt)] * 2, color=N.MAP_AX, w=1.8, tail='triangle')])
    lab = lambda k, x, y, w, t, **o: T('%s/axl/%s' % (key, k), x, y, w, 24, t, anchor='ctr', **o)
    s.add(key + '/axl', [lab('xn', xe + 10, oy - 12, 90, '찾는 범위', size=13.5, color=SUB, weight='b'),
                         lab('yn', ox - 80, yt - 34, 160, '찾는 깊이', size=13.5, color=SUB, weight='b', align='c'),
                         lab('x0', ox + 14, oy + 10, 80, '좁게', size=12.5, color=MUTE),
                         lab('x1', xe - 100, oy + 10, 80, '넓게', size=12.5, color=PURPLE, weight='b', align='r'),
                         lab('y0', ox - 72, oy - 40, 60, '얕게', size=12.5, color=MUTE, align='r'),
                         lab('y1', ox - 72, yt + 20, 60, '깊게', size=12.5, color=PURPLE, weight='b', align='r')])
    pts = {}
    for k, kind, name, what, (dx, dy) in APX_SERV:
        cx, cy = ox + dx, oy - dy
        pts[k] = (cx, cy)
        kk = '%s/%s' % (key, k)
        s.add(kk, N.map_point(kk, kind, name, cx, cy) + [
            T(kk + '/what', cx - 110, cy + 23 + 27, 220, 18, what, size=10.5, color=SUB, align='c', anchor='ctr')])
    s.add(key + '/wglow', [glow(key + '/wglow', wx, wy)])
    fx, fy = pts['finder']
    s.add(key + '/arrow', thread(key + '/arrow', [(fx + 8, fy - 36), (fx + 8, fy - 104), (wx, wy + 172), (wx, wy + 98)], w=2.6, tail='triangle'))
    s.add(key + '/weave', weave_tile(key + '/weave', wx, wy) + [
        T(key + '/weave/what', wx - 120, wy + 33 + 6 + 28, 240, 20, APX_WEAVE, size=11.5, color=PURPLE, align='c', anchor='ctr')])
    s.add(key + '/src', [N.foot(key + '/src', N.CMP_SRC)])
    s.on(key + '/axx', 'wipe_in', 150, 600)
    s.on(key + '/axy', 'wipe_in', 150, 600, dir='up')
    s.on(key + '/axl', 'fade_in', 600, 450)
    for i, (k, *_) in enumerate(APX_SERV):
        s.on('%s/%s' % (key, k), 'zoom_in', 900 + i * 260, 380, **{'from': 0.6})
    s.click()      # 1: 얕은 쪽을 넘어 깊은 쪽으로 → Weave
    s.on(key + '/arrow', 'wipe_in', 0, 520, dir='up')
    s.on(key + '/wglow', 'fade_in', 300, 500)
    weave_on(s, key, 420)
    return s


CANDIDATES = [('가', 'cmpa', s_cmpa, '두 띠'), ('나', 'cmpb', s_cmpb, '넓이와 깊이'), ('다', 'cmpc', s_cmpc, '네 칸'), ('라', 'cmpd', s_cmpd, '계단')]
