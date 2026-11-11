"""통합본에 새로 그린 장 (How it Works와 같은 엔진: 09_HowItWorks/장표5_claude).

- bridge: 인트로와 모션그래픽을 잇는 장(인트로 덱 13쪽 자리). 키보드의 실타래 버튼에서 나온 실 한 가닥이 흩어진 앱을 차례로 꿴다.
- fx1~3, bi, cmp, tl, end1~3, endlogo: 뒷부분. 아웃트로 덱(Weave_BI_아웃트로_통합_1110_v7.pptx)의 내용을 우리 틀로 다시 그리고, 한 쪽에 몰려 있던 효과를 쪽과 클릭으로 나눔.
- p_hub, p_tl: 제안 장표(덱 맨 뒤). 설문의 저장 채널 그림, 새 연표.

좌표는 1280×720 px. 글은 NOTES(말할 글, (클릭) = 그 자리에서 클릭)와 각 장 함수 안에 있다.
"""
import math
from pathlib import Path

import build as HW
from ui import (BODY, ICON, INK, INK2, LAV, LAV2, LINE, LINE2, MUTE, PURPLE, PURPLE2, RING, SUB, SHADOW_CARD, SHADOW_LIFT, SHADOW_SOFT,
                C, P, R, T, Xf, caption, check_icon, numdot, spark_icon, star4_icon, tw)

Slide, cue = HW.Slide, HW.cue
HERE = Path(__file__).resolve().parent
AS = HERE / 'assets'
OUTRO = AS / 'outro'
PHOTO = AS / 'photo'
KB_PNG = str(HW.AS / 'keyboard.png')

# ------------------------------------------------------------------ 말할 글
NOTES = {
    'bridge': ("그래서 오늘, 우리는 흩어진 나의 기억들과 지금의 나를 가장 자연스럽게 이어 줄 새로운 연결고리, 'Weave Assist'를 제안합니다. "
               '(클릭) 앱을 일일이 켜고 찾아 헤맬 필요 없이, 내가 매일 쓰는 화면과 키보드 위 실타래 버튼 하나로 흩어진 기억의 단서들을 엮어 '
               '필요한 순간 건네주는 온디바이스 AI입니다.'),
    'fx1': ('저희 설문에서 응답자의 83.8%는 어느 앱에 남겼는지 몰라 앱을 하나씩 열어 본 적이 있다고 답했습니다. '
            '(클릭) 기록 통합 검색은 앱마다 흩어진 기록을 한 번에 찾아 요약해, 헤매는 시간을 줄여 줍니다.'),
    'fx2': ('93.8%는 정확한 이름이 떠오르지 않아 검색으로 바로 찾지 못한 적이 있었습니다. '
            '(클릭) 단서로 찾는 기억은 이름 대신, 기억나는 상황만으로 찾아 줍니다.'),
    'fx3': ('또 82.4%는 챙겨야 할 부탁이나 약속을 나중에야 떠올린 적이 있었습니다. '
            '(클릭) 먼저 건네는 기억은 지금 필요한 기억을 묻기 전에 먼저 알려 줍니다.'),
    'bi': ('스마트폰 사용자는 한 달에 평균 41개의 앱을 씁니다. 기록은 그 41개 앱에 흩어져 있고요. '
           '(클릭) 그리고 69%는 스스로 기록을 지우지 않고 쌓아 두는 편이라고 답했습니다. 지우지 않은 기록은 그냥 쌓이기만 합니다. '
           '(클릭) 이 흩어진 앱과 쌓인 기록을, 갤럭시 안의 Weave가 하나로 엮습니다. '
           '흩어진 기록을 엮어 다시 꺼내 쓰는 것, 그래서 쓸수록 쌓이고 갤럭시를 떠나기 어려워집니다.'),
    'cmp': ('그렇다면 이미 있는 기능과는 무엇이 다를까요? Finder는 자연어로 기록을 찾아 주고, Now Nudge는 지금 보는 대화에 맞춰 사진이나 예약 정보를 제안합니다. '
            '카나나는 카카오톡 안에서 대화를 읽고 먼저 제안하죠. '
            '(클릭) Weave는 여러 앱에 흩어진 단서를 이어서 찾고, 쓰던 화면의 키보드 위에서 바로 건넵니다. '
            '(클릭) 실제로 설문에서 기본 검색창을 자주 쓴다는 응답은 33.8%였고, 94.3%는 단서가 될 기록부터 직접 차례로 찾아봤다고 답했습니다.'),
    'tl': ('이 경험이 갤럭시에서, 그리고 지금 가능한 이유입니다. '
           '(클릭) 검색 기술은 뜻으로 찾는 임베딩에서 찾아서 답하는 RAG를 거쳐, 지난해부터는 추론하며 단서를 이어 찾는 단계까지 왔습니다. '
           '(클릭) 갤럭시는 매일 쓰는 키보드와 기기 위에, Galaxy AI와 개인 데이터 엔진을 차례로 갖췄습니다. '
           '(클릭) 두 흐름이 만나는 지금이, Weave를 시작할 때입니다.'),
    'end1': '당신이 사랑하는 모든 것에 더 가까이 다가가고, 오래도록 이야기하게 될 순간을 담아보세요. 갤럭시가 전해 온 말입니다.',
    'end2': '기기 안에는 그렇게 담아 둔 순간이 쌓여 있습니다.',
    'end3': '갤럭시의 모든 순간이 다시 이야기가 되도록, Weave가 이어 가겠습니다. 지금까지 Weave Assist였습니다. 감사합니다.',
    'endlogo': '',
    # 제안 장표(본 발표 흐름에는 넣지 않음. 넣는다면 이렇게 말함)
    'p_hub': ('기록은 남길 때부터 한곳에 모이지 않습니다. 화면 캡처로, 나와의 채팅으로, 메모 앱과 사진, 캘린더로 나눠 남기죠. '
              '(클릭) 한 사람이 평균 3.8곳에 나눠 남기고 있었습니다. '
              '(클릭) 열 명 중 아홉 명은 두 곳 이상, 네 명 중 세 명은 세 곳 이상이었습니다.'),
    'p_tl': ('이 경험이 갤럭시에서, 그리고 지금 가능한 이유입니다. '
             '(클릭) 검색 기술은 찾아서 답하는 RAG에서 여러 단계로 찾는 Multi-hop으로, 지난해부터는 추론하며 찾는 Reasoning Embedding으로 넘어왔습니다. '
             '(클릭) 갤럭시는 매일 쓰는 키보드 위에 기기 안의 AI 연산과 Galaxy AI, 그리고 개인 데이터를 지키는 PDE와 KEEP을 차례로 갖췄습니다. '
             '(클릭) 기술과 기기가 모두 준비된 지금이, 두 흐름을 Weave로 엮을 때입니다.'),
}
CUES = {
    'bridge.logo': ('bridge', 0, "'Weave Assist'를"),
    'bridge.btn': ('bridge', 1, '실타래 버튼 하나로'),
    'bridge.weave': ('bridge', 1, '흩어진 기억의 단서들을'),
    'bridge.sub': ('bridge', 1, '온디바이스 AI입니다'),
    'fx1.num': ('fx1', 0, '83.8%'),
    'fx2.num': ('fx2', 0, '93.8%'),
    'fx3.num': ('fx3', 0, '82.4%'),
}
HW.NOTES.update(NOTES)
HW.CUES.update(CUES)


# ------------------------------------------------------------------ 공통 조각
def title(key, runs, y=46):
    """덱 머리 규격(29pt Bold, 가운데). runs = [(글, 색)]."""
    return T(key, 0, y, 1280, 50, [[(t, dict(color=c, spc=-0.5, spc_ko=-0.5)) for t, c in runs]], size=29, weight='b',
             align='c', anchor='ctr', lnspc=34.8, spc=-0.5)


def foot(key, text, y=676, pt=9.5):
    return T(key, 60, y, 1160, 18, text, size=pt, color=MUTE, anchor='ctr')


def arc_pts(cx, cy, r, a0, a1):
    """원호(시계 방향, 도 단위: 0 = 12시)를 3차 베지어 마디로. 돌려줌: 점 3n+1개."""
    n = max(1, math.ceil(abs(a1 - a0) / 60))
    step = math.radians((a1 - a0) / n)
    k = 4 / 3 * math.tan(step / 4) * r
    pts = []
    for i in range(n):
        t0 = math.radians(a0) + step * i
        t1 = t0 + step
        p0 = (cx + r * math.sin(t0), cy - r * math.cos(t0))
        p1 = (cx + r * math.sin(t1), cy - r * math.cos(t1))
        c0 = (p0[0] + k * math.cos(t0), p0[1] + k * math.sin(t0))
        c1 = (p1[0] - k * math.cos(t1), p1[1] - k * math.sin(t1))
        pts += ([p0] if i == 0 else []) + [c0, c1, p1]
    return pts


def ring(key, cx, cy, r, pct, w=17, color=PURPLE, track='E7E0FA'):
    """고리 그래프: 바탕 고리와 12시에서 시계 방향으로 pct%만큼의 호. 돌려줌: (바탕 원시 목록, 호 원시 목록)."""
    base = [R(key + '/track', cx - r, cy - r, 2 * r, 2 * r, prst='ellipse', fill=None, line=track, line_w=w)]
    arc = [C(key + '/arc', arc_pts(cx, cy, r, 0, 360 * pct / 100), w=w, color=color)]
    return base, arc


def logo(key, x, cy, mark=58, pt=44):
    """표지와 같은 로고: 보라 네모 + 흰 실타래, 그 옆에 'Weave Assist'(글꼴과 그라데이션은 make.py의 logo_style이 입힘)."""
    ic = mark * 2 / 3
    return ([R(key + '/mark', x, cy - mark / 2, mark, mark, prst='roundRect', radius=mark * 15 / 56, line=None,
               grad=dict(stops=[(0, '8D6BFF', None), (55, '6B4EFF', None), (100, '5A3FE0', None)], ang=55), shadow=(20, 8, '6B4EFF', 30)),
             P(key + '/icon', ICON['spool_w'], x + (mark - ic) / 2, cy - ic / 2, ic, ic)],
            [T(key + '/logo_word', x + mark + 13, cy - pt * 0.8, 470, pt * 1.6, 'Weave Assist', size=pt, color=PURPLE, weight='b', anchor='ctr',
               spc=-0.5)])


# ------------------------------------------------------------------ 인트로 → 모션그래픽을 잇는 장
BR_KB = (688, 356, 504, 310)                              # 자판(How it Works의 01 상황 인식 장과 같은 그림)
BR_SPOOL = (BR_KB[0] + 102 * BR_KB[2] / 1300, BR_KB[1] + 82 * BR_KB[3] / 800)
BR_Y = 218                                                # 실에 꿰인 앱이 놓이는 줄
BR_X = [768, 866, 964, 1062, 1160]
BR_APPS = ['talk', 'gallery', 'note', 'cal', 'mail']
BR_FROM = [(-158, -68), (-276, 212), (-64, -98), (-2, 82), (30, -78)]  # 처음엔 흩어져 있던 자리(줄에서 떨어진 만큼). 자판이 올라올 자리는 비워 둠
BR_DRIFT = [(10, -8), (-8, -10), (-10, 8), (9, 9), (-9, 7)]             # 흩어져 있는 동안 천천히 흘러가는 만큼
BR_SZ = 56


def br_thread():
    """실 한 가닥: 실타래 버튼 → 위로 → 앱을 하나씩 위아래로 번갈아 지나감 → 끝에 별. 돌려줌: [(키, 점들, 닦아 내는 방향)]."""
    sx, sy = BR_SPOOL
    y = BR_Y
    out = [('br/th0', [(sx, sy - 18), (sx - 8, sy - 96), (BR_X[0] - 50, y + 56), (BR_X[0], y)], 'up')]
    for i in range(len(BR_X) - 1):
        a, b = BR_X[i], BR_X[i + 1]
        dy = -44 if i % 2 == 0 else 44
        out.append(('br/th%d' % (i + 1), [(a, y), (a + 32, y + dy), (b - 32, y + dy), (b, y)], 'left'))
    e = BR_X[-1]
    out.append(('br/th5', [(e, y), (e + 24, y - 30), (e + 44, y - 42), (e + 64, y - 42)], 'left'))
    return out


def s_bridge():
    """인트로 13쪽 자리. 흩어진 앱 → 'Weave Assist' → (클릭) 자판의 실타래 버튼이 켜지고 실 한 가닥이 앱을 차례로 꿰어 가지런히 → 한 줄 소개."""
    s = Slide('bridge', trans=('fade', 600), bar=False, notes=NOTES['bridge'])
    mark, word = logo('br/logo', 74, 326)
    s.add('br/mark', mark)
    s.add('br/word', word)
    s.add('br/sub', [T('br/sub', 76, 374, 520, 34, [[('흩어진 기억을 엮어 건네는 ', dict(color=INK2)), ('온디바이스 AI', dict(color=PURPLE))]],
                       size=20, weight='b', anchor='ctr')])
    s.add('br/kb', [P('br/kb', KB_PNG, *BR_KB, radius=17, crop=(0, 3 / 800, 0, 0), line='D9D4E8', line_w=1.2, shadow=SHADOW_LIFT)])
    s.add('br/glow', [R('br/glow', BR_SPOOL[0] - 27, BR_SPOOL[1] - 27, 54, 54, prst='ellipse', fill=None, line=PURPLE, line_w=3,
                        glow=(14, RING, 50))])
    th = br_thread()
    for key, pts, _ in th:
        s.add(key, [C(key, pts, w=3.2)])
    ex = BR_X[-1] + 64
    s.add('br/star', star4_icon('br/star', ex + 13, BR_Y - 42, r=9))
    for i, (app, x, d) in enumerate(zip(BR_APPS, BR_X, BR_FROM)):
        s.add('br/app%d' % i, [P('br/app%d' % i, ICON[app], x - BR_SZ / 2, BR_Y - BR_SZ / 2, BR_SZ, BR_SZ, shadow=(14, 4, '6B4EFF', 16))], start=d)
    # 장이 열리면: 흩어져 있는 앱(처음부터 보임) → 'Weave Assist'
    for i in range(len(BR_APPS)):          # 서서히 나타나(장이 넘어올 때는 숨어 있음) 제자리에서 조금씩 흘러감
        k, d, f = 'br/app%d' % i, BR_FROM[i], BR_DRIFT[i]
        s.on(k, 'fade_in', 150 + i * 110, 450)
        s.on(k, 'goto', 0)
        s.on(k, 'move', 30, 9500, dx=f[0], dy=f[1], base=d, accel=0, decel=0)
    t = max(cue('bridge.logo', 5200, ahead=0.25), 900)
    s.on('br/mark', 'zoom_in', t, 420, **{'from': 0.7})
    s.on('br/word', 'rise', t + 120, 520, dy=12)
    s.click()      # 1: 자판 → 실타래 버튼이 켜짐 → 실이 앱을 하나씩 꿰며 가지런히 → 한 줄 소개
    s.on('br/kb', 'rise', 200, 520, dy=16)
    tb = max(cue('bridge.btn', 5200, ahead=0.2), 900)
    s.on('br/glow', 'zoom_in', tb, 320, **{'from': 0.55})
    s.on('br/glow', 'pulse', tb + 360, 170, scale=1.14)
    tw_ = max(cue('bridge.weave', 6700, ahead=0.2), tb + 700)
    s.on('br/th0', 'wipe_in', tw_, 420, dir='up')
    step = 330
    for i in range(len(BR_APPS)):
        ti = tw_ + 380 + i * step
        d = (BR_FROM[i][0] + BR_DRIFT[i][0], BR_FROM[i][1] + BR_DRIFT[i][1])
        s.on('br/app%d' % i, 'fly', ti - 160, 520, dx=d[0], dy=d[1], bend=0, show=False, fade=False)
        s.on('br/app%d' % i, 'pulse', ti + 340, 130, scale=1.1)
        s.on('br/th%d' % (i + 1), 'wipe_in', ti + 120, step, dir='left')
    te = tw_ + 380 + len(BR_APPS) * step
    s.on('br/star', 'zoom_in', te + 120, 320, **{'from': 0.4})
    s.on('br/sub', 'rise', max(cue('bridge.sub', te + 600, ahead=0.3), te + 500), 520, dy=10)
    return s


# ------------------------------------------------------------------ 뒷부분 1: 기대효과 세 장
FX_TITLE = [('찾는 시간은 줄이고, ', INK), ('놓친 기억은 되살립니다', PURPLE)]
FX_SRC = "* 출처: 자체 사용자 설문 ('예' 응답 비율, 응답자 210명)"
FX_CX, FX_CY, FX_R = 262, 398, 96
FX = {      # 장 키: (번호, 불편(두 줄), %, 명, 기능 이름, 한 줄 설명, UX 묶음, 묶음 자리, 이름표 y)
    'fx1': (1, ['어느 앱인지 몰라', '앱을 하나씩 열어 봤어요'], 83.8, 176, '기록 통합 검색', '앱마다 흩어진 같은 일의 기록을, 하나로 엮어 보여 줍니다',
            'ux1', Xf(40, 218, 628, 196, 0.98), 150),
    'fx2': (2, ['이름이 떠오르지 않아', '검색으로 바로 찾지 못했어요'], 93.8, 197, '단서로 찾는 기억', '정확한 이름 대신, 기억나는 상황만으로 찾아 줍니다',
            'ux2', Xf(640, 218, 566, 330, 1.12), 270),
    'fx3': (3, ['챙겨야 할 부탁, 약속을', '나중에야 떠올렸어요'], 82.4, 173, '먼저 건네는 기억', '지금 도움이 될 기억을, 먼저 알려 줍니다',
            'ux3', Xf(640, 492, 566, 328, 1.12), 270),
}


def s_fx(key, first=False):
    """기대효과 한 장: 왼쪽에 설문의 불편(말 + 고리 그래프), (클릭) 오른쪽에 그 불편에 답하는 기능과 화면.
    아웃트로 덱은 클릭하면 고리가 비고 숫자가 줄어들었는데, 숫자는 근거라서 남겨 두고 오른쪽 화면만 띄운다."""
    n, stmt, pct, cnt, name, sub, ux, xf, ly = FX[key]
    s = Slide(key, trans=('fade', 500) if first else ('morph', 800), bar=False, notes=NOTES[key])
    s.add('fx/title', [title('fx/title', FX_TITLE)])
    s.add('fx/stmt', [caption('fx/stmt', [[(ln, INK)] for ln in stmt], FX_CX, 170, size=21, lh=32)])
    base, arc = ring('fx/ring', FX_CX, FX_CY, FX_R, pct)
    s.add('fx/ring', base)
    s.add('fx/arc', arc)
    pt = 36
    num = '%.1f' % pct
    nw = tw(num, pt, 'b') + tw('%', 19, 'b') + 2
    s.add('fx/num', [T('fx/num', FX_CX - nw / 2 - 4, FX_CY - 34, nw + 16, 52, [[(num, dict(size=pt)), ('%', dict(size=19))]], size=pt, color=PURPLE,
                       weight='b', anchor='ctr', spc=-0.5)])
    s.add('fx/yes', [T('fx/yes', FX_CX - 80, FX_CY + 18, 160, 22, "'예' 응답", size=11.5, color=MUTE, align='c', anchor='ctr')])
    s.add('fx/cnt', [T('fx/cnt', FX_CX - 150, FX_CY + FX_R + 30, 300, 24,
                       [[('응답자 210명 중 ', dict(color=MUTE)), ('%d명' % cnt, dict(color=SUB, weight='b'))]], size=12.5, align='c', anchor='ctr')])
    s.add('fx/rule', [R('fx/rule', 520, 150, 1, 500, fill='D9CEFA', line=None)])
    lx = 566
    s.add('fx/no', numdot('fx/no', lx + 16, ly + 16, n, r=16, pt=12.5))
    nwid = tw(name, 19, 'b')
    s.add('fx/name', [T('fx/name', lx + 44, ly, nwid + 12, 32, name, size=19, color=INK, weight='b', anchor='ctr')])
    s.add('fx/sub', [T('fx/sub', lx + 44 + nwid + 22, ly + 1, 560, 32, sub, size=13, color=SUB, anchor='ctr')])
    keys = []
    for k in HW.SOL_Z[ux]:
        kk = 'sol/%s/%s' % (ux, k)
        if (ux, k) == ('ux2', 'q'):                # 검색창에는 찾은 이름이 들어가 있음(솔루션 장의 마지막 모습)
            s.add('sol/ux2/a', HW.sol_answer(), xf=xf)
            s.add('sol/ux2/cur', [HW.sol_cursor(HW.ANSWER)], xf=xf)
            keys += ['sol/ux2/a', 'sol/ux2/cur']
            continue
        s.add(kk, HW.sol_piece('%s/%s' % (ux, k)), xf=xf, alpha=HW.SOL_ALPHA.get('%s/%s' % (ux, k), 100))
        keys.append(kk)
    s.add('fx/src', [foot('fx/src', FX_SRC)])
    # 장이 열리면: 불편 한마디 → 고리가 차오르고 숫자
    s.on('fx/stmt', 'rise', 200, 500, dy=12)
    s.on('fx/ring', 'fade_in', 450, 350)
    tn = max(cue(key + '.num', 1600, ahead=0.3), 700)
    s.on('fx/arc', 'wheel_in', tn, 900)
    s.on(['fx/num', 'fx/yes'], 'fade_in', tn + 350, 400)
    s.on('fx/cnt', 'fade_in', tn + 900, 400)
    s.click()      # 1: 이 불편에 답하는 기능과 화면
    s.on('fx/rule', 'fade_in', 0, 300)
    s.on(['fx/no', 'fx/name'], 'rise', 80, 420, dy=10)
    s.on('fx/sub', 'fade_in', 320, 400)
    s.on(keys, 'rise', 420, 560, dy=14)
    return s




# ------------------------------------------------------------------ 뒷부분 2: 비즈니스 임팩트
BI_APPS = ['gallery', 'messages', 'kakao', 'camera', 'calendar', 'music', 'video', 'notes', 'store', 'email', 'health', 'maps', 'cloud',
           'wallet', 'phone', 'internet', 'penup', 'recorder', 'clock']
BI_LX, BI_RX = 252, 1028                                    # 왼쪽 묶음 가운데, 오른쪽 묶음 가운데
BI_PS = 380 / 456                                           # 휴대폰: 솔루션 장의 틀(ux1_phone.png, 몸통 272×456)을 높이 380으로
BI_PH = (640 - 272 * BI_PS / 2, 172, 272 * BI_PS, 380)      # 몸통 상자
BI_SRC = '* 출처: ¹ UK Ofcom(영국 정보통신청), "Online Nation 2025 Report" (2025. 12)   ² Compare and Recycle, "Digital Declutter Statistics 2025" (2025. 12)'


def bi_stat(key, cx, num, unit, label, cap):
    """큰 숫자 + 설명 + 가는 줄 + 한 줄 결론. 돌려줌: 원시 목록."""
    pt = 54
    nw = tw(num, pt, 'b') + tw(unit, 26, 'b') + 3
    out = [T(key + '/num', cx - nw / 2 - 2, 352, nw + 12, 78, [[(num, dict(size=pt)), (unit, dict(size=26))]], size=pt, color=PURPLE, weight='b',
             anchor='ctr', spc=-1),
           T(key + '/label', cx - 200, 432, 400, 28, label, size=14.5, color=INK2, align='c', anchor='ctr'),
           R(key + '/rule', cx - 150, 474, 300, 1, fill='D9CEFA', line=None),
           T(key + '/cap', cx - 200, 488, 400, 34, [[(t, dict(color=c)) for t, c in cap]], size=17, weight='b', align='c', anchor='ctr')]
    return out


def s_bi():
    """41개 앱에 흩어진 기록 → (클릭) 지우지 않고 쌓이는 기록 → (클릭) 갤럭시 안의 Weave가 엮음. 아웃트로 덱 4쪽을 세 박자로 나눔."""
    s = Slide('bi', trans=('fade', 500), bar=False, notes=NOTES['bi'])
    s.add('bi/title', [title('bi/title', [('쓸수록 쌓여, ', INK), ('갤럭시를 떠나기 어려워집니다', PURPLE)])])
    # 왼쪽: 앱 19개(6·7·6)
    apps, sz, gx, gy = [], 44, 54, 54
    rows = [BI_APPS[:6], BI_APPS[6:13], BI_APPS[13:]]
    for r_, names in enumerate(rows):
        x0 = BI_LX - (len(names) - 1) * gx / 2
        for c_, nm in enumerate(names):
            jig = ((r_ * 7 + c_ * 5) % 9) - 4
            apps.append(P('bi/app/%s' % nm, str(OUTRO / ('app-%s.png' % nm)), x0 + c_ * gx - sz / 2, 172 + r_ * gy + jig, sz, sz))
    s.add('bi/apps', apps)
    s.add('bi/l', bi_stat('bi/l', BI_LX, '41', '개', '사용자가 월평균 쓰는 앱 수¹',
                          [('기록은 ', INK), ('41개 앱에 흩어져', PURPLE), (' 있고', INK)]))
    # 오른쪽: 고리 69%
    base, arc = ring('bi/pie', BI_RX, 252, 62, 69, w=15)
    s.add('bi/pie', base)
    s.add('bi/arc', arc)
    s.add('bi/r', bi_stat('bi/r', BI_RX, '69', '%', '기록을 지우지 않고 쌓아 둔다고 답한 사용자²',
                          [('지우지 않은 기록은 ', INK), ('쌓이기만', PURPLE), (' 합니다', INK)]))
    # 가운데: 갤럭시 안의 Weave
    px, py, pw, ph = BI_PH
    cx = px + pw / 2
    s.add('bi/glow', [R('bi/glow', cx - 200, py + ph / 2 - 200, 400, 400, prst='ellipse', fill=None, line=None,
                        grad=dict(stops=[(0, '8B6BFF', 30), (55, 'B9A6FF', 12), (100, 'F2EDFF', 0)], path='circle'))])
    s.add('bi/phone', [P('bi/phone/frame', str(HW.SOLDIR / 'layers' / 'ux1_phone.png'), px - 32 * BI_PS, py - 14 * BI_PS, 336 * BI_PS, 520 * BI_PS),
                       P('bi/phone/sp', ICON['spool'], cx - 26, py + 118, 52, 52),
                       T('bi/phone/w', px, py + 178, pw, 36, 'Weave', size=22, color=PURPLE, weight='b', align='c', anchor='ctr'),
                       T('bi/phone/t', px, py + 222, pw, 44, [[('흩어진 기록을 엮어', {})], [('다시 꺼내 씁니다', {})]], size=12.5, color=INK2, align='c',
                         lnspc=16)])
    yl = py + ph / 2 + 10
    s.add('bi/thl', [C('bi/thl', [(BI_LX + 172, yl)] * 2 + [(px - 10, yl)] * 2, w=2.6)])
    s.add('bi/thr', [C('bi/thr', [(BI_RX - 172, yl)] * 2 + [(px + pw + 10, yl)] * 2, w=2.6)])
    s.add('bi/src', [foot('bi/src', BI_SRC, pt=9)])
    # 장이 열리면: 앱이 모이고 41개
    s.on('bi/apps', 'zoom_in', 200, 520, **{'from': 0.86})
    s.on('bi/l', 'rise', 520, 520, dy=12)
    s.click()      # 1: 지우지 않고 쌓이는 기록
    s.on('bi/pie', 'fade_in', 0, 300)
    s.on('bi/arc', 'wheel_in', 150, 850)
    s.on('bi/r', 'rise', 420, 520, dy=12)
    s.click()      # 2: 갤럭시 안의 Weave가 엮음
    s.on('bi/glow', 'fade_in', 0, 500)
    s.on('bi/phone', 'rise', 100, 560, dy=16)
    s.on('bi/thl', 'wipe_in', 620, 420, dir='left')
    s.on('bi/thr', 'wipe_in', 620, 420, dir='right')
    s.on('bi/phone', 'pulse', 1080, 170, scale=1.04)
    return s


# ------------------------------------------------------------------ 뒷부분 3: 기존 기능과의 비교
CMP_COLS = [   # (키, 이름, 딸린 말, [찾는 곳, 찾는 방식, 쓰는 자리])
    ('finder', 'Samsung Finder', 'One UI 8.5', ['선택한 앱의 기록', '자연어로 한 번 검색', '홈 화면 검색창']),
    ('nudge', 'Now Nudge', 'Galaxy S26', ['갤러리 사진, 예약 정보 등', '대화 맥락에 맞춰 한 번 제안', '삼성 키보드 위']),
    ('kanana', '카나나 인 카카오톡', '카카오', ['카카오톡 대화', '대화를 읽고 먼저 제안', '카카오톡 안']),
    ('weave', 'Weave Assist', '제안', ['여러 앱에 흩어진 기록', '단서를 이어 여러 단계로', '쓰던 화면의 키보드 위']),
]
CMP_ROWS = ['찾는 범위', '찾는 방식', '쓰는 자리']
CMP_X0, CMP_W, CMP_GAP, CMP_TOP = 178, 228, 16, 126
CMP_HEAD, CMP_RH = 112, 92
CMP_SRC = '* Samsung 지원 페이지(Finder), Samsung Newsroom(Galaxy S26, 2026. 2), 카카오 발표(2026. 3)의 공식 설명을 기준으로 함'


def cmp_icon(key, kind, cx, cy):
    """열 머리의 작은 그림(38px 칸)."""
    z = 38
    tile = R(key + '/tile', cx - z / 2, cy - z / 2, z, z, prst='roundRect', radius=11, fill='F1EEF8', line=None)
    if kind == 'finder':
        r = 7.5
        return [tile, R(key + '/c', cx - r - 2, cy - r - 2, 2 * r, 2 * r, prst='ellipse', fill=None, line=SUB, line_w=2.4),
                C(key + '/h', [(cx + 3.6, cy + 3.6)] * 2 + [(cx + 9.5, cy + 9.5)] * 2, color=SUB, w=2.6)]
    if kind == 'nudge':
        return [tile] + spark_icon(key + '/s', cx - 12, cy - 12, size=24, color=SUB)
    if kind == 'kanana':
        return [P(key + '/k', ICON['talk'], cx - z / 2, cy - z / 2, z, z)]
    return [R(key + '/tile', cx - z / 2, cy - z / 2, z, z, prst='roundRect', radius=11, line=None,
              grad=dict(stops=[(0, '8D6BFF', None), (100, '5A3FE0', None)], ang=55)),
            P(key + '/sp', ICON['spool_w'], cx - 12, cy - 12, 24, 24)]


def s_cmp():
    """기존 기능 셋과 Weave를 세 가지로만 견준다(찾는 범위·찾는 방식·쓰는 자리). 네 칸의 틀과 기존 기능이 먼저 뜨고, (클릭) Weave 칸이 켜지며 채워지고, (클릭) 설문 근거."""
    s = Slide('cmp', trans=('fade', 500), bar=False, notes=NOTES['cmp'])
    s.add('cmp/title', [title('cmp/title', [('한 번의 검색을 넘어, ', INK), ('단서를 이어 찾는 검색', PURPLE), ('으로', INK)])])
    h = CMP_HEAD + CMP_RH * 3 + 10
    labs = []
    for r_, lab in enumerate(CMP_ROWS):
        y = CMP_TOP + CMP_HEAD + r_ * CMP_RH
        labs.append(T('cmp/lab%d' % r_, CMP_X0 - 168, y, 150, CMP_RH, lab, size=14, color=SUB, weight='b', align='r', anchor='ctr'))
    s.add('cmp/labs', labs)
    for i, (k, name, tag, cells) in enumerate(CMP_COLS):
        x = CMP_X0 + i * (CMP_W + CMP_GAP)
        me = k == 'weave'
        cx = x + CMP_W / 2
        col = [R('cmp/%s/bg' % k, x, CMP_TOP, CMP_W, h, prst='roundRect', radius=20, fill='FFFFFF', line=LINE, line_w=1.0, shadow=SHADOW_CARD)]
        col += cmp_icon('cmp/%s/ic' % k, k, cx, CMP_TOP + 34)
        col += [T('cmp/%s/name' % k, x, CMP_TOP + 60, CMP_W, 26, name, size=15, color=PURPLE if me else INK, weight='b', align='c', anchor='ctr'),
                T('cmp/%s/tag' % k, x, CMP_TOP + 84, CMP_W, 20, tag, size=10.5, color=PURPLE2 if me else MUTE, align='c', anchor='ctr')]
        body = []
        for r_, cell in enumerate(cells):
            y = CMP_TOP + CMP_HEAD + r_ * CMP_RH
            col.append(R('cmp/%s/sep%d' % (k, r_), x + 18, y, CMP_W - 36, 1, fill='E4DCF8' if me else 'EEE9F8', line=None))
            body.append(T('cmp/%s/c%d' % (k, r_), x + 8, y, CMP_W - 16, CMP_RH, cell, size=14.5, color=PURPLE if me else INK2,
                          weight='b' if me else 'm', align='c', anchor='ctr'))
        s.add('cmp/' + k, col + ([] if me else body))
        if me:
            s.add('cmp/weave/hi', [R('cmp/weave/hi', x, CMP_TOP, CMP_W, h, prst='roundRect', radius=20, fill=None, line=RING, line_w=2.4,
                                     glow=(10, RING, 24))])
            s.add('cmp/weave/cells', body)
    sy = CMP_TOP + h + 24
    txt = [[('설문 210명  ', dict(color=MUTE, weight='b', size=11.5)), ('기본 검색창을 자주 쓴다 ', dict(color=INK2)), ('33.8%', dict(color=PURPLE, weight='b')),
            ('      단서가 될 기록부터 직접 차례로 찾아봤다 ', dict(color=INK2)), ('94.3%', dict(color=PURPLE, weight='b'))]]
    s.add('cmp/survey', [R('cmp/survey/bg', CMP_X0, sy, 960, 44, prst='roundRect', fill=LAV2, line=LINE2, line_w=1.0),
                         T('cmp/survey/t', CMP_X0, sy, 960, 44, txt, size=14, align='c', anchor='ctr')])
    s.add('cmp/src', [foot('cmp/src', CMP_SRC)])
    s.on('cmp/labs', 'fade_in', 150, 400)
    for i, k in enumerate(('finder', 'nudge', 'kanana', 'weave')):
        s.on('cmp/' + k, 'rise', 300 + i * 240, 480, dy=14)
    s.click()      # 1: Weave 칸이 켜지고 채워짐
    s.on('cmp/weave/hi', 'fade_in', 0, 420)
    s.on('cmp/weave/cells', 'rise', 200, 480, dy=10)
    s.click()      # 2: 설문 근거
    s.on('cmp/survey', 'rise', 0, 480, dy=10)
    return s


# ------------------------------------------------------------------ 뒷부분 4: Why Now · Why Samsung 연표(아웃트로 덱의 내용 그대로, 한 박자씩)
TL_Y = 384
TL_EV = [   # (x, 위 = 'now' | 아래 = 'sam', 해, 한마디, 근거, 아이콘)
    (266, 'sam', '2010', '키보드와 기기', 'Galaxy · Keyboard⁵', 'ic-keyboard.png'),
    (390, 'now', '2019', '뜻으로 찾기', 'Sentence-BERT¹', 'ic-sbert.png'),
    (514, 'now', '2020', '찾아서 답하기', 'RAG²', 'ic-rag.png'),
    (638, 'sam', '2024. 01', 'Galaxy AI 등장', 'Galaxy S24⁶', 'ic-galaxyai.png'),
    (762, 'sam', '2025. 01', '개인 데이터 엔진', 'PDE · Galaxy S25⁷', 'ic-pde.png'),
    (886, 'now', '2025. 04', '추론하며 찾기', 'ReasonIR³', 'ic-reason.png'),
    (1010, 'now', '2025. 10', '단서를 잇는 검색', 'Multi-hop Retrieval⁴', 'ic-hop.png'),
]
TL_W, TL_X0, TL_OLD = 1146, 206, 576          # Weave 마디, 줄이 시작하는 곳, 여기까지는 회색 줄(2020년까지)
TL_SRC = ('* ¹ Reimers & Gurevych, "Sentence-BERT" (EMNLP 2019)   ² Lewis 외, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (NeurIPS 2020)   '
          '³ Shao 외, "ReasonIR" (COLM 2025)   ⁴ Nahid & Rafiei, "PRISM" (arXiv 2510.14278)   '
          '⁵ ⁶ ⁷ Samsung Newsroom, Galaxy S (2010), Galaxy S24 · Galaxy AI (2024. 01), Galaxy S25 · Personal Data Engine (2025. 01)')


def tl_event(x, side, year, word, ref, icon, old=False):
    key = 'tl/e%d' % x
    col = SUB if old else PURPLE
    out = [R(key + '/dot', x - 8, TL_Y - 8, 16, 16, prst='ellipse', fill='FFFFFF', line='B9B2C9' if old else PURPLE, line_w=3)]
    if side == 'now':
        out += [P(key + '/ic', str(OUTRO / icon), x - 17, TL_Y - 158, 34, 34),
                T(key + '/w', x - 90, TL_Y - 114, 180, 24, word, size=14, color=INK, weight='b', align='c', anchor='ctr'),
                T(key + '/r', x - 90, TL_Y - 90, 180, 20, ref, size=10.5, color=MUTE, align='c', anchor='ctr'),
                T(key + '/y', x - 60, TL_Y - 54, 120, 28, year, size=15.5, color=col, weight='b', align='c', anchor='ctr')]
    else:
        out += [T(key + '/y', x - 60, TL_Y + 26, 120, 28, year, size=15.5, color=col, weight='b', align='c', anchor='ctr'),
                T(key + '/w', x - 90, TL_Y + 64, 180, 24, word, size=14, color=INK, weight='b', align='c', anchor='ctr'),
                T(key + '/r', x - 90, TL_Y + 88, 180, 20, ref, size=10.5, color=MUTE, align='c', anchor='ctr'),
                P(key + '/ic', str(OUTRO / icon), x - 17, TL_Y + 122, 34, 34)]
    return key, out


def s_tl():
    """줄 하나에 위는 기술(Why Now), 아래는 갤럭시(Why Samsung). 줄 → (클릭) 기술 → (클릭) 갤럭시 → (클릭) 2026 Weave."""
    s = Slide('tl', trans=('fade', 500), bar=False, notes=NOTES['tl'])
    s.add('tl/title', [title('tl/title', [('갤럭시라서', PURPLE), (', 그리고 ', INK), ('지금이라서', PURPLE), (' 되는 Weave', INK)])])
    s.add('tl/gray', [C('tl/gray', [(TL_X0, TL_Y)] * 2 + [(TL_OLD, TL_Y)] * 2, color='CFC8DE', w=3)])
    s.add('tl/line', [C('tl/line', [(TL_OLD, TL_Y)] * 2 + [(TL_W - 30, TL_Y)] * 2, w=3)])
    s.add('tl/lnow', [T('tl/lnow/a', 60, TL_Y - 84, 130, 18, 'WHY NOW', size=10, color=PURPLE, weight='b', spc=1.2),
                      T('tl/lnow/b', 60, TL_Y - 64, 130, 26, '지금이라서', size=15, color=INK, weight='b')])
    s.add('tl/lsam', [T('tl/lsam/a', 60, TL_Y + 34, 130, 18, 'WHY SAMSUNG', size=10, color=PURPLE, weight='b', spc=1.2),
                      T('tl/lsam/b', 60, TL_Y + 54, 130, 26, '갤럭시라서', size=15, color=INK, weight='b')])
    keys = {'now': [], 'sam': []}
    for x, side, year, word, ref, icon in TL_EV:
        key, prims = tl_event(x, side, year, word, ref, icon, old=x < TL_OLD)
        s.add(key, prims)
        keys[side].append(key)
    wx = TL_W
    s.add('tl/wglow', [R('tl/wglow', wx - 44, TL_Y - 44, 88, 88, prst='ellipse', fill=None, line=None,
                         grad=dict(stops=[(0, '8B6BFF', 46), (60, 'B9A6FF', 16), (100, 'F2EDFF', 0)], path='circle'))])
    s.add('tl/w', [R('tl/w/c', wx - 24, TL_Y - 24, 48, 48, prst='ellipse', line='FFFFFF', line_w=2.5, shadow=(18, 6, '6B4EFF', 30),
                     grad=dict(stops=[(0, '8D6BFF', None), (100, '5A3FE0', None)], ang=55)),
                   P('tl/w/sp', ICON['spool_w'], wx - 14, TL_Y - 14, 28, 28),
                   T('tl/w/y', wx - 60, TL_Y - 72, 120, 30, '2026', size=19, color=PURPLE, weight='b', align='c', anchor='ctr'),
                   T('tl/w/n', wx - 70, TL_Y + 34, 140, 26, 'Weave', size=16, color=PURPLE, weight='b', align='c', anchor='ctr')])
    s.add('tl/src', [T('tl/src', 60, 648, 1160, 44, TL_SRC, size=9, color=MUTE, wrap=True, lnspc=13)])
    s.on(['tl/lnow', 'tl/lsam'], 'fade_in', 150, 400)
    s.on('tl/gray', 'wipe_in', 300, 450)
    s.on('tl/line', 'wipe_in', 700, 650)
    s.click()      # 1: 기술(위)
    for i, k in enumerate(keys['now']):
        s.on(k, 'rise', i * 420, 460, dy=-12)
    s.click()      # 2: 갤럭시(아래)
    for i, k in enumerate(keys['sam']):
        s.on(k, 'rise', i * 420, 460, dy=12)
    s.click()      # 3: 두 흐름이 만나는 2026
    s.on('tl/wglow', 'fade_in', 0, 500)
    s.on('tl/w', 'zoom_in', 100, 420, **{'from': 0.6})
    s.on('tl/w', 'pulse', 560, 180, scale=1.08)
    return s


# ------------------------------------------------------------------ 뒷부분 5: 마무리(사진 위에 글) + 끝 화면
WHITE, SOFT = 'FFFFFF', 'D9CCFF'


def photo_bg(key, fname, veil=40, top=62, bottom=30):
    """사진을 장 가득 깔고, 글이 읽히게 위에서 아래로 옅어지는 어둠을 얹는다."""
    return [P(key + '/photo', str(PHOTO / fname), 0, 0, 1280, 720),
            R(key + '/veil', 0, 0, 1280, 720, fill=None, line=None,
              grad=dict(stops=[(0, '120A24', top), (55, '120A24', veil), (100, '120A24', bottom)], ang=90))]


def s_end1():
    s = Slide('end1', trans=('fade', 900), bar=False, bg=False, notes=NOTES['end1'])
    s.add('end/bg', photo_bg('end/bg', 'closing-1-sunset-chairs.jpg', veil=34, top=58, bottom=26))
    s.add('end1/q', [T('end1/q', 60, 168, 840, 110,
                       [[('당신이 사랑하는 모든 것에 더 가까이 다가가고,', dict(color=WHITE))],
                        [('오래도록 이야기하게 될 ', dict(color=WHITE)), ('순간', dict(color=SOFT)), ('을 담아보세요', dict(color=WHITE))]],
                       size=30, weight='b', align='c', lnspc=40, spc=-0.4)])
    s.add('end1/by', [T('end1/by', 180, 290, 600, 26, '— Samsung Galaxy 광고 카피 중', size=13, color=WHITE, alpha=78, align='c', anchor='ctr')])
    s.on('end1/q', 'rise', 500, 800, dy=14)
    s.on('end1/by', 'fade_in', 1500, 600)
    return s


HAND = (670, 436)


def s_end2():
    s = Slide('end2', trans=('fade', 900), bar=False, bg=False, notes=NOTES['end2'])
    s.add('end/bg', photo_bg('end/bg', 'closing-2-toast.jpg', veil=52, top=58, bottom=50))
    w = 430
    s.add('end/hand', [P('end/hand', str(OUTRO / 'moment-hand-white.png'), 640 - w / 2, 360 - w * HAND[1] / HAND[0] / 2 - 6, w, w * HAND[1] / HAND[0])])
    s.on('end/hand', 'wipe_in', 500, 1100, dir='left')
    return s


def s_end3():
    s = Slide('end3', trans=('morph', 1100), bar=False, bg=False, notes=NOTES['end3'])
    s.add('end/bg', photo_bg('end/bg', 'closing-3-sunset-picnic.jpg', veil=30, top=60, bottom=22))
    pt = 36
    a, b = '갤럭시의 모든 ', '이'
    hw = 118                                             # 문장 속 손글씨 '순간'의 폭
    wa, wb = tw(a, pt, 'b'), tw(b, pt, 'b')
    x0 = 640 - (wa + hw + 6 + wb) / 2
    y1 = 150
    s.add('end3/a', [T('end3/a', x0, y1, wa + 10, 56, a, size=pt, color=WHITE, weight='b', anchor='ctr', spc=-0.4)])
    s.add('end/hand', [P('end/hand', str(OUTRO / 'moment-hand-white.png'), x0 + wa - 4, y1 + 28 - hw * HAND[1] / HAND[0] / 2 - 4, hw, hw * HAND[1] / HAND[0])])
    s.add('end3/b', [T('end3/b', x0 + wa + hw + 6, y1, wb + 10, 56, b, size=pt, color=WHITE, weight='b', anchor='ctr', spc=-0.4)])
    s.add('end3/c', [T('end3/c', 240, y1 + 62, 800, 56, [[('다시 ', dict(color=WHITE)), ('이야기', dict(color=SOFT)), ('가 되도록', dict(color=WHITE))]],
                       size=pt, weight='b', align='c', anchor='ctr', spc=-0.4)])
    s.on(['end3/a', 'end3/b'], 'fade_in', 200, 600)
    s.on('end3/c', 'rise', 900, 800, dy=12)
    return s


def s_endlogo():
    s = Slide('endlogo', trans=('fade', 900), bar=False, bg=False, notes=NOTES['endlogo'])
    s.add('endlogo/bg', [P('endlogo/bg', str(OUTRO / 'end-bg.png'), 0, 0, 1280, 720)])
    w = 250
    h = w * 421 / 1996
    s.add('endlogo/logo', [P('endlogo/logo', str(OUTRO / 'end-logo.png'), 640 - w / 2, 352 - h / 2, w, h)])
    sw = 262
    s.add('endlogo/sw', [P('endlogo/sw', str(OUTRO / 'end-swoosh.png'), 640 - sw / 2, 352 + h / 2 + 4, sw, sw * 225 / 2156)])
    s.on('endlogo/logo', 'fade_in', 300, 700)
    s.on('endlogo/sw', 'wipe_in', 800, 600, dir='left')
    return s




# ------------------------------------------------------------------ 제안 1: 설문의 저장 채널 그림(인트로 8쪽 뒤에 넣는 안)
HUB = (400, 392)                    # 가운데 원
HUB_R = 78
HUB_RX, HUB_RY = 262, 186           # 둘레 칸이 놓이는 타원
HUB_CARD = (164, 56)
HUB_ITEMS = [   # (이름, %, 아이콘) — 설문 4번(복수 선택), 많이 고른 순서. 위에서 시계 방향으로 놓음
    ('화면 캡처', 76.7, ICON['gallery']),
    ('나와의 채팅', 75.7, ICON['talk']),
    ('메모 앱', 65.2, ICON['note']),
    ('사진 촬영', 59.5, str(OUTRO / 'app-camera.png')),
    ('캘린더', 53.3, ICON['cal']),
    ('지도 저장', 25.7, ICON['map']),
    ('이메일', 14.8, ICON['mail']),
]
HUB_SRC = '* 출처: 자체 사용자 설문 (응답자 210명, 나중에 다시 보려고 정보를 남길 때 쓰는 방법, 복수 선택)'


def hub_pos(i):
    a = math.radians(-90 + i * 360 / len(HUB_ITEMS))
    return HUB[0] + HUB_RX * math.cos(a), HUB[1] + HUB_RY * math.sin(a)


def hub_stat(key, y, pct, word, cnt):
    """오른쪽 근거 한 줄: 큰 % + 한마디 + 응답 수."""
    pt = 44
    num = '%.1f' % pct
    return [T(key + '/n', 836, y, 220, 60, [[(num, dict(size=pt)), ('%', dict(size=22))]], size=pt, color=PURPLE, weight='b', anchor='ctr', spc=-0.8),
            T(key + '/w', 838, y + 62, 360, 28, word, size=17, color=INK, weight='b', anchor='ctr'),
            T(key + '/c', 838, y + 92, 360, 22, [[('응답자 210명 중 ', dict(color=MUTE)), ('%d명' % cnt, dict(color=SUB, weight='b'))]], size=12.5, anchor='ctr')]


def s_p_hub():
    """남기는 곳이 하나씩 뜨고 → (클릭) 가운데 '평균 3.8곳'과 잇는 줄 → (클릭) 두 곳 이상 91.4%, 세 곳 이상 74.8%."""
    s = Slide('p_hub', trans=('fade', 500), bar=False, notes=NOTES['p_hub'])
    s.add('hub/title', [title('hub/title', [('기록은 남길 때부터, ', INK), ('여러 곳에 흩어집니다', PURPLE)])])
    cw, ch = HUB_CARD
    for i, (name, pct, icon) in enumerate(HUB_ITEMS):
        x, y = hub_pos(i)
        # 가운데 원의 둘레에서 칸의 가장자리까지(굵을수록 많이 쓰는 곳)
        dx, dy = x - HUB[0], y - HUB[1]
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        t_edge = min((cw / 2) / abs(ux) if abs(ux) > 1e-6 else 1e9, (ch / 2) / abs(uy) if abs(uy) > 1e-6 else 1e9)
        a = (HUB[0] + ux * (HUB_R + 5), HUB[1] + uy * (HUB_R + 5))
        b = (x - ux * (t_edge + 4), y - uy * (t_edge + 4))
        s.add('hub/ln%d' % i, [C('hub/ln%d' % i, [a, a, b, b], color='C9BBFA', w=1.4 + 4.2 * pct / 76.7)])
        s.add('hub/c%d' % i, [R('hub/c%d/bg' % i, x - cw / 2, y - ch / 2, cw, ch, prst='roundRect', radius=16, fill='FFFFFF', line=LINE, line_w=1.0,
                                shadow=SHADOW_CARD),
                              P('hub/c%d/ic' % i, icon, x - cw / 2 + 12, y - 17, 34, 34),
                              T('hub/c%d/n' % i, x - cw / 2 + 56, y - 22, cw - 60, 22, name, size=12.5, color=INK2, weight='b', anchor='ctr'),
                              T('hub/c%d/p' % i, x - cw / 2 + 56, y - 1, cw - 60, 24, '%.1f%%' % pct, size=15, color=PURPLE, weight='b', anchor='ctr')])
    hx, hy = HUB
    s.add('hub/glow', [R('hub/glow', hx - 128, hy - 128, 256, 256, prst='ellipse', fill=None, line=None,
                         grad=dict(stops=[(0, '8B6BFF', 26), (60, 'B9A6FF', 10), (100, 'F2EDFF', 0)], path='circle'))])
    s.add('hub/core', [R('hub/core/c', hx - HUB_R, hy - HUB_R, 2 * HUB_R, 2 * HUB_R, prst='ellipse', fill='FFFFFF', line=RING, line_w=2.2,
                         shadow=SHADOW_LIFT),
                       T('hub/core/a', hx - 70, hy - 44, 140, 22, '한 사람이 평균', size=12, color=SUB, align='c', anchor='ctr'),
                       T('hub/core/n', hx - 76, hy - 24, 152, 52, [[('3.8', dict(size=38)), ('곳', dict(size=20))]], size=38, color=PURPLE, weight='b',
                         align='c', anchor='ctr', spc=-0.8),
                       T('hub/core/b', hx - 70, hy + 26, 140, 22, '에 나눠 남김', size=12, color=SUB, align='c', anchor='ctr')])
    s.add('hub/rule', [R('hub/rule', 790, 196, 1, 392, fill='D9CEFA', line=None)])
    s.add('hub/s1', hub_stat('hub/s1', 226, 91.4, '두 곳 이상에 나눠 남김', 192))
    s.add('hub/s2', hub_stat('hub/s2', 414, 74.8, '세 곳 이상에 나눠 남김', 157))
    s.add('hub/src', [foot('hub/src', HUB_SRC)])
    # 장이 열리면: 남기는 곳이 많이 쓰는 순서로 하나씩
    for i in range(len(HUB_ITEMS)):
        s.on('hub/c%d' % i, 'zoom_in', 250 + i * 330, 320, **{'from': 0.8})
    s.click()      # 1: 한 사람이 평균 3.8곳
    s.on('hub/glow', 'fade_in', 0, 450)
    s.on('hub/core', 'zoom_in', 60, 380, **{'from': 0.7})
    for i in range(len(HUB_ITEMS)):
        s.on('hub/ln%d' % i, 'fade_in', 380 + i * 90, 300)
    s.click()      # 2: 두 곳 이상, 세 곳 이상
    s.on('hub/rule', 'fade_in', 0, 300)
    s.on('hub/s1', 'rise', 100, 480, dy=12)
    s.on('hub/s2', 'rise', 900, 480, dy=12)
    return s


# ------------------------------------------------------------------ 제안 2: 새 연표(위는 기술, 아래는 갤럭시, 두 줄이 2026년의 Weave에서 만남)
PT_YU, PT_YL, PT_YC = 316, 452, 384            # 위 줄, 아래 줄, 두 줄이 만나는 높이
PT_X0, PT_X1, PT_WX = 60, 1012, 1112           # 줄이 시작하는 곳, 곧게 가는 끝, Weave 마디
PT_NOW = 690                                   # 이보다 오른쪽 마디는 보라(최근), 왼쪽은 회색
PT_UP = [    # (x, 해, 한마디, 근거)
    (470, '2020', '찾아서 답하기', 'RAG¹'),
    (608, '2021', '여러 단계로 찾기', 'Multi-hop Retrieval²'),
    (834, '2025', '추론하며 찾기', 'Reasoning Embedding³'),
    (972, '2026', '추론을 읽는 검색', 'AgentIR⁴'),
]
PT_DN = [
    (244, '2010', '키보드와 기기', 'Galaxy · Keyboard⁵'),
    (382, '2019', '기기 안 AI 연산', 'NPU · Galaxy S10⁶'),
    (696, '2024', 'Galaxy AI', 'Galaxy S24⁷'),
    (834, '2025', '개인 데이터와 보호', 'PDE · KEEP⁸'),
]
PT_SRC = ('* ¹ Lewis 외, "Retrieval-Augmented Generation" (NeurIPS 2020)   ² Xiong 외, "Multi-Hop Dense Retrieval" (ICLR 2021)   ³ Shao 외, "ReasonIR" (COLM 2025)   '
          '⁴ Chen 외, "AgentIR" (arXiv 2603.04384)   ⁵ ⁶ ⁷ ⁸ Samsung Newsroom: Galaxy S (2010), Exynos 9820 NPU (2018. 11), Galaxy S24 · Galaxy AI (2024. 01), '
          'Galaxy S25 · Personal Data Engine (2025. 01), KEEP (2025. 07)')
PT_STOPS = [(0, 'DAD4E8', None), (48, 'C3B4F5', None), (100, '6B4EFF', None)]


def pt_node(key, x, y, up, year, word, ref):
    new = x >= PT_NOW
    out = [R(key + '/dot', x - 8, y - 8, 16, 16, prst='ellipse', fill='FFFFFF', line=PURPLE if new else 'B9B2C9', line_w=3)]
    ys = (y - 96, y - 68, y - 44) if up else (y + 22, y + 50, y + 74)
    out += [T(key + '/y', x - 60, ys[0], 120, 26, year, size=15, color=PURPLE if new else SUB, weight='b', align='c', anchor='ctr'),
            T(key + '/w', x - 84, ys[1], 168, 24, word, size=14.5, color=INK, weight='b', align='c', anchor='ctr'),
            T(key + '/r', x - 84, ys[2], 168, 20, ref, size=10.5, color=MUTE, align='c', anchor='ctr')]
    return out


def s_p_tl():
    """두 줄(위 = 기술, 아래 = 갤럭시) → (클릭) 기술 → (클릭) 갤럭시 → (클릭) 두 줄이 Weave에서 만남."""
    s = Slide('p_tl', trans=('fade', 500), bar=False, notes=NOTES['p_tl'])
    s.add('pt/title', [title('pt/title', [('갤럭시라서', PURPLE), (', 그리고 ', INK), ('지금이라서', PURPLE), (' 되는 Weave', INK)])])
    s.add('pt/lu', [C('pt/lu', [(PT_X0, PT_YU)] * 2 + [(PT_X1, PT_YU)] * 2, stops=PT_STOPS, w=3)])
    s.add('pt/ll', [C('pt/ll', [(PT_X0, PT_YL)] * 2 + [(PT_X1, PT_YL)] * 2, stops=PT_STOPS, w=3)])
    ex = PT_WX - 30
    s.add('pt/ju', [C('pt/ju', [(PT_X1, PT_YU), (PT_X1 + 44, PT_YU), (ex - 44, PT_YC), (ex, PT_YC)], w=3)])
    s.add('pt/jl', [C('pt/jl', [(PT_X1, PT_YL), (PT_X1 + 44, PT_YL), (ex - 44, PT_YC), (ex, PT_YC)], w=3)])
    s.add('pt/now', [T('pt/now/a', 60, PT_YU + 14, 160, 18, 'WHY NOW', size=10, color=PURPLE, weight='b', spc=1.2),
                     T('pt/now/b', 60, PT_YU + 32, 160, 24, '지금이라서', size=14, color=INK, weight='b')])
    s.add('pt/sam', [T('pt/sam/a', 60, PT_YL - 56, 160, 18, 'WHY SAMSUNG', size=10, color=PURPLE, weight='b', spc=1.2),
                     T('pt/sam/b', 60, PT_YL - 38, 160, 24, '갤럭시라서', size=14, color=INK, weight='b')])
    ups, dns = [], []
    for x, year, word, ref in PT_UP:
        k = 'pt/u%d' % x
        s.add(k, pt_node(k, x, PT_YU, True, year, word, ref))
        ups.append(k)
    for x, year, word, ref in PT_DN:
        k = 'pt/d%d' % x
        s.add(k, pt_node(k, x, PT_YL, False, year, word, ref))
        dns.append(k)
    wx = PT_WX
    s.add('pt/wglow', [R('pt/wglow', wx - 52, PT_YC - 52, 104, 104, prst='ellipse', fill=None, line=None,
                         grad=dict(stops=[(0, '8B6BFF', 46), (60, 'B9A6FF', 16), (100, 'F2EDFF', 0)], path='circle'))])
    s.add('pt/w', [R('pt/w/c', wx - 28, PT_YC - 28, 56, 56, prst='ellipse', line='FFFFFF', line_w=2.5, shadow=(18, 6, '6B4EFF', 30),
                     grad=dict(stops=[(0, '8D6BFF', None), (100, '5A3FE0', None)], ang=55)),
                   P('pt/w/sp', ICON['spool_w'], wx - 16, PT_YC - 16, 32, 32),
                   T('pt/w/n', wx - 70, PT_YC + 36, 140, 28, 'Weave', size=17, color=PURPLE, weight='b', align='c', anchor='ctr')])
    s.add('pt/src', [T('pt/src', 60, 648, 1160, 44, PT_SRC, size=9, color=MUTE, wrap=True, lnspc=13)])
    s.on(['pt/now', 'pt/sam'], 'fade_in', 150, 400)
    s.on(['pt/lu', 'pt/ll'], 'wipe_in', 350, 900)
    s.click()      # 1: 기술(위)
    for i, k in enumerate(ups):
        s.on(k, 'rise', i * 420, 460, dy=-12)
    s.click()      # 2: 갤럭시(아래)
    for i, k in enumerate(dns):
        s.on(k, 'rise', i * 420, 460, dy=12)
    s.click()      # 3: 두 줄이 Weave에서 만남
    s.on(['pt/ju', 'pt/jl'], 'wipe_in', 0, 520)
    s.on('pt/wglow', 'fade_in', 420, 500)
    s.on('pt/w', 'zoom_in', 480, 420, **{'from': 0.6})
    s.on('pt/w', 'pulse', 940, 180, scale=1.08)
    return s


# ------------------------------------------------------------------ 제안 장표 앞 가름 장, 마무리 사진 출처
def s_p_divider(lines):
    s = Slide('p0', trans=('fade', 500), bar=False, notes='여기부터는 제안 장표입니다. 본 발표에서는 넘기지 않습니다.')
    s.add('p0/t', [caption('p0/t', [[('제안 장표', PURPLE)]], 640, 260, size=44)])
    s.add('p0/s', [T('p0/s', 200, 342, 880, 30 * len(lines), lines, size=14, color=SUB, align='c', lnspc=22)])
    return s


PHOTO_CREDITS = [('마무리 1 (해 질 녘)', 'Harli Marten, "Pink sunset couple", Unsplash (Wikimedia Commons 사본), CC0'),
                 ('마무리 2 (건배)', 'Yutacar, "Restaurant Swan Lake Beer, Agano-shi, Niigata-pref, Japan", Unsplash (Wikimedia Commons 사본), CC0'),
                 ('마무리 3 (노을 소풍)', 'Arthur Poulin, "Sunset Picnic", Unsplash (Wikimedia Commons 사본), CC0')]


def s_credits2():
    s = Slide('apx_credit2', trans=('fade', 400), bar=False, notes='마무리 장에 깐 사진의 출처입니다.')
    s.add('cr2/title', [caption('cr2/title', [[('사진 출처', INK)]], 640, 54, size=24)])
    s.add('cr2/sub', [T('cr2/sub', 100, 54 + 24 * 1.42 + 6, 1080, 24, '마무리 장의 배경 사진 출처', size=13, color=SUB, align='c')])
    out = []
    for i, (a, b) in enumerate(PHOTO_CREDITS):
        y = 160 + i * 64
        out += [R('cr2/%d/bg' % i, 160, y, 960, 52, prst='roundRect', radius=14, fill='FFFFFF', line=LINE2, line_w=1.0),
                T('cr2/%d/a' % i, 184, y, 200, 52, a, size=12, color=PURPLE, weight='b', anchor='ctr'),
                T('cr2/%d/b' % i, 390, y, 720, 52, b, size=10.5, color=BODY, anchor='ctr')]
    s.add('cr2/rows', out)
    return s


SLIDES_BACK = [lambda: s_fx('fx1', first=True), lambda: s_fx('fx2'), lambda: s_fx('fx3'), s_bi, s_cmp, s_tl, s_end1, s_end2, s_end3, s_endlogo]
SLIDES_PROPOSAL = [s_p_hub, s_p_tl]
