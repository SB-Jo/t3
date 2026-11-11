"""통합본에 새로 그린 장 (How it Works와 같은 엔진: 09_HowItWorks/장표5_claude).

인트로
- hook: 6쪽 자리. 검색해도 없는 기록 → 수많은 기록(앱 화면의 벽에 불이 하나씩 켜짐) → 불이 꺼지고 문구.
- hub2: 8쪽 다음. 8쪽의 앱 네 개가 둥근 자리로 옮겨 가고, 기록을 남기는 곳 일곱과 평균 3.8곳 → (클릭) 두 곳 이상, 세 곳 이상.
- bridge: 인트로와 모션그래픽을 잇는 장. 모션그래픽 첫 화면처럼 가운데 위에 로고, 그 아래 떠 있는 앱들 → (클릭) 실 한 가닥이 넷을 이음.
뒷부분
- fx1~3, bi, cmp, tl, end1~3: 아웃트로 덱(Weave_BI_아웃트로_통합_1110_v7.pptx)의 내용을 우리 틀로 다시 그린 것. 끝 로고는 end3 안으로.
제안 장표(덱 뒤쪽)
- p_fx1~3: 기대효과를 고리 그래프의 움직임으로 보여 주는 안. p_tl: 두 줄 연표(길게 말하는 대본).

좌표는 1280×720 px. 말할 글은 NOTES((클릭) = 그 자리에서 클릭)와 INTRO_NOTES(옮겨 온 인트로 장의 노트)에 있다.
"""
import math
from pathlib import Path

import build as HW
from ui import (BODY, ICON, INK, INK2, LAV, LAV2, LINE, LINE2, MUTE, PURPLE, PURPLE2, RED, RING, SUB, SHADOW_CARD, SHADOW_LIFT, SHADOW_SOFT,
                C, P, R, T, Xf, caption, magnifier, numdot, spark_icon, star4_icon, tw)

import hook_layout as HL

Slide, cue = HW.Slide, HW.cue
HERE = Path(__file__).resolve().parent
AS = HERE / 'assets'
OUTRO = AS / 'outro'
PHOTO = AS / 'photo'
HOOKD = AS / 'hook'
CAMERA = str(HOOKD / 'samsung-camera.png')
NAVY = '3D3654'                    # 인트로 7쪽 고리의 짙은 색(불편을 겪은 사람)
TRACK = 'E4DDF7'                   # 고리의 바탕색(인트로 7·8쪽과 같음)
RING_K = 0.098                     # 고리 굵기 ÷ 바깥지름(인트로 7·8쪽: 298px에 29px)

# ------------------------------------------------------------------ 말할 글
# 표지와 옮겨 온 인트로 장(2~5, 7~12쪽)의 노트. 괄호 속은 무대 지시(팀원 노트 그대로), 나머지가 말할 글.
INTRO_NOTES = {
    'cover': ('(화면: 흩어진 기억을 엮어, 지금을 완성하다 — Weave Assist)\n'
              '안녕하세요. 흩어진 기억을 엮어 지금을 완성하는 온디바이스 AI, Weave Assist 발표를 맡은 장이준입니다.'),
    'in02': ('(장이 열리면 통화 중 00:48 표시가 뜨고 "잠깐만요, 찾아보고 다시 알려 드릴게요." 문장이 한 글자씩 나타납니다. '
             '문장이 다 뜰 때까지 1초쯤 기다립니다. 클릭 없음)\n'
             "여러분, 통화하다가 이런 말 해 보신 적 있으시죠. '잠깐만요, 찾아보고 다시 알려 드릴게요.'"),
    'in03': ("(장이 열리면 첫 번째 인물과 '그게 어디에 있더라?' 말풍선이 저절로 나타납니다.)\n"
             '저희는 이런 막막한 순간을 세 가지로 나눠 보았습니다.\n'
             '첫째, 어디에 있는지 모를 때입니다. 찾을 내용은 분명한데 어느 앱에 남겼는지 모릅니다.'),
    'in04': ("(장이 열리면 첫 인물이 옆으로 비켜서고, 두 번째 인물과 '그 이름이 뭐였지?' 말풍선이 나타납니다.)\n"
             '둘째, 이름이 떠오르지 않을 때입니다. 그날의 장면은 선명한데, 검색할 정확한 단어가 없습니다.'),
    'in05': ("(장이 열리면 세 번째 인물과 '그런 얘기가 있었나?' 말풍선이 나타납니다.)\n"
             '셋째, 기억조차 나지 않을 때입니다. 부탁이나 약속은 대화방에 그대로 남아 있지만, 정작 챙겨야 할 순간에는 떠오르지 않습니다.\n'
             '(톤을 한 단계 높여) 세 순간 모두, 필요한 기록은 이미 내 휴대폰 안에 있습니다. (0.5초 쉬고 다음 장)'),
    'in07': ('(장이 열리면 왼쪽 링이 93.8%까지 채워지고 오른쪽 수치 197명이 나타납니다. 따로 클릭하지 않아도 됩니다.)\n'
             "실제로, 저희가 사용자 210명을 대상으로 설문조사를 진행한 결과, 무려 93.8%인 197명이 '찾고 싶은 정보를 바로 찾지 못한 경험이 있다'고 답했습니다."),
    'in08': ('(장이 열리면 같은 링 안에서 그 197명 중 187명(94.9%)이 보라색으로 채워지고, 돋보기 표시가 앱 넷을 차례로 건너뛰다 처음 앱으로 되돌아갑니다. '
             '따로 클릭하지 않아도 됩니다.)\n'
             '그리고 그 197명 가운데 94.9%인 187명은 단서가 될 기록부터 다시 찾아봤다고 답했습니다.\n'
             '저장했던 곳이 떠오르지 않으니, 결국 사람이 직접 기억의 단서를 잡고 여러 앱을 찾아다니고 있었던 겁니다.'),
    'in09': ('(장이 열리면 왼쪽 ✦ AI 어시스턴트 ("삼성 기술전이 뭐야?" ➔ ✦ AI 답변) 대화 화면이 차례로 나타납니다.)\n'
             '여기서 저희는 한 가지 중요한 의문이 들었습니다.\n'
             "'세상의 모든 지식은 이렇게 AI에게 물어 단 1초 만에 답을 받는데,'"),
    'in10': ("(장이 열리면 오른쪽 '지금의 나'를 둘러싼 기록들(메일, 캘린더, 노트, 카톡)이 선으로 이어지며 나타납니다.)\n"
             "'왜 정작 나에 대한 모든 기록이 담긴 내 휴대폰 안에서는, 아직도 이렇게 찾아 헤매야 할까요?'\n"
             '대화도, 메모도, 사진도 사라진 게 아닙니다.'),
    'in11': ("(넘어가면 '지금의 나'와 기록들을 잇던 연결선이 사라지고 기록들이 흩어집니다.)\n"
             "앱마다 흩어져 있는 어제의 기록들을 하나로 엮어, 오늘의 나에게 데려와 줄 '연결고리'가 없었을 뿐입니다."),
    'in12': '(톤을 한 단계 높여) 그렇다면, AI에게 물어보듯 내 휴대폰에게 바로 물을 수는 없을까요? (0.5초 쉬고 다음 장)',
}
NOTES = {
    'hook': ('우리는 매일 셀 수 없이 많은 기록을 남깁니다. 카톡 대화, 사진, 메모, 일정, 메일까지. '
             '(클릭) 수많은 기록 속에서, 지금 필요한 기록을 찾아 헤매는 것. 저희는 바로 이 문제에서 출발했습니다.'),
    'hub2': ('기록을 남길 때부터 한 사람이 평균 3.8곳에 나눠 저장하기 때문입니다. '
             '(클릭) 91.4%는 두 곳 이상에, 74.8%는 세 곳 이상에 나눠 남기고 있었습니다.'),
    'bridge': ("그래서 오늘, 우리는 흩어진 나의 기억들과 지금의 나를 이어 줄 새로운 연결고리, 'Weave Assist'를 제안합니다. "
               '(클릭) 앱을 일일이 켜고 찾아 헤맬 필요 없이, 흩어진 기억의 단서들을 엮어 필요한 순간 건네주는 온디바이스 AI입니다.'),
    'fx1': ('저희 설문에서 응답자의 83.8%는 어느 앱에 남겼는지 몰라 앱을 하나씩 열어 봤다고 답했습니다. '
            '(클릭) 기록 통합 검색이 이 헤매는 시간을 줄여 줍니다.'),
    'fx2': ('93.8%는 이름이 떠오르지 않아 검색으로 바로 찾지 못했습니다. '
            '(클릭) 단서로 찾는 기억은 기억나는 상황만으로 찾아 줍니다.'),
    'fx3': ('82.4%는 부탁이나 약속을 나중에야 떠올렸습니다. '
            '(클릭) 먼저 건네는 기억이 묻기 전에 먼저 알려 줍니다.'),
    'bi': ('스마트폰 사용자는 한 달에 평균 41개의 앱을 씁니다. '
           '(클릭) 그리고 69%는 기록을 지우지 않고 쌓아 둔다고 답했습니다. '
           '(클릭) 이렇게 흩어지고 쌓인 기록을 갤럭시 안의 Weave가 하나로 엮습니다. 그래서 쓸수록 쌓이고 갤럭시를 떠나기 어려워집니다.'),
    'cmp': ('그렇다면 이미 있는 기능과는 무엇이 다를까요? Finder와 Now Nudge, 카나나는 정해진 범위 안에서 한 번 찾거나 제안합니다. '
            '(클릭) Weave는 여러 앱에 흩어진 단서를 이어서 찾고, 쓰던 화면의 키보드 위에서 바로 건넵니다.'),
    'tl': ('이 경험이 갤럭시에서, 그리고 지금 가능한 이유입니다. '
           '(클릭) 검색 기술은 뜻으로 찾는 임베딩에서 찾아서 답하는 RAG를 거쳐, 지난해부터는 추론하며 단서를 이어 찾는 단계까지 왔습니다. '
           '(클릭) 갤럭시는 매일 쓰는 키보드와 기기 위에, Galaxy AI와 개인 데이터 엔진을 차례로 갖췄습니다. '
           '(클릭) 두 흐름이 만나는 지금이, Weave를 시작할 때입니다.'),
    'end1': '당신이 사랑하는 모든 것에 더 가까이 다가가고, 오래도록 이야기하게 될 순간을 담아보세요.',
    'end2': '기기 안에는 그렇게 담아 둔 순간이 쌓여 있습니다.',
    'end3': '갤럭시의 모든 순간이 다시 이야기가 되도록, Weave가 이어 가겠습니다. 감사합니다.',
    # 제안 장표(본 발표 흐름에는 넣지 않음. 넣는다면 이렇게 말함)
    'p_fx1': ('저희 설문에서 응답자의 83.8%는 어느 앱에 남겼는지 몰라 앱을 하나씩 열어 봤다고 답했습니다. '
              '(클릭) 기록 통합 검색이 있으면, 이 83.8%는 앱을 하나씩 여는 대신 한 번의 검색으로 찾습니다.'),
    'p_fx2': ('93.8%는 이름이 떠오르지 않아 검색으로 바로 찾지 못했습니다. '
              '(클릭) 단서로 찾는 기억이 있으면, 이름 대신 기억나는 상황만으로 찾습니다.'),
    'p_fx3': ('82.4%는 부탁이나 약속을 나중에야 떠올렸습니다. '
              '(클릭) 먼저 건네는 기억이 있으면, 떠올리기 전에 Weave가 먼저 알려 줍니다.'),
    'p_tl': ('이 경험이 갤럭시에서, 그리고 지금 가능한 이유입니다. '
             '(클릭) 먼저 기술입니다. 2020년 RAG가 찾아서 답하는 길을 열었고, 이듬해에는 여러 단계를 이어 찾는 Multi-hop 검색이 나왔습니다. '
             '지난해에는 추론이 필요한 단서까지 찾는 Reasoning Embedding이, 올해는 추론 과정까지 검색에 쓰는 AgentIR이 나왔습니다. '
             '(클릭) 갤럭시도 준비를 마쳤습니다. 매일 쓰는 키보드와 기기 위에 2019년에는 기기 안에서 AI를 돌리는 NPU가 들어왔고, '
             '2024년에는 Galaxy AI가, 지난해에는 개인 데이터를 기기 안에서 다루는 PDE와 이를 지키는 KEEP이 더해졌습니다. '
             '(클릭) 기술과 기기가 모두 준비된 지금이, 두 흐름을 Weave로 엮을 때입니다.'),
}
CUES = {
    'hook.talk': ('hook', 0, '카톡 대화'),
    'hook.gallery': ('hook', 0, '사진'),
    'hook.note': ('hook', 0, '메모'),
    'hook.cal': ('hook', 0, '일정'),
    'hook.mail': ('hook', 0, '메일까지'),
    'hub2.avg': ('hub2', 0, '3.8곳'),
    'hub2.three': ('hub2', 1, '74.8%'),
    'bridge.logo': ('bridge', 0, "'Weave Assist'를"),
    'bridge.weave': ('bridge', 1, '흩어진 기억의 단서들을'),
    'fx1.num': ('fx1', 0, '83.8%'),
    'fx2.num': ('fx2', 0, '93.8%'),
    'fx3.num': ('fx3', 0, '82.4%'),
    'p_fx1.num': ('p_fx1', 0, '83.8%'),
    'p_fx2.num': ('p_fx2', 0, '93.8%'),
    'p_fx3.num': ('p_fx3', 0, '82.4%'),
    'end3.logo': ('end3', 0, 'Weave가'),
    'p_tl.u0': ('p_tl', 1, '2020년'), 'p_tl.u1': ('p_tl', 1, '이듬해에는'), 'p_tl.u2': ('p_tl', 1, '지난해에는'), 'p_tl.u3': ('p_tl', 1, '올해는'),
    'p_tl.d0': ('p_tl', 2, '매일 쓰는'), 'p_tl.d1': ('p_tl', 2, '2019년에는'), 'p_tl.d2': ('p_tl', 2, '2024년에는'), 'p_tl.d3': ('p_tl', 2, '지난해에는'),
}
HK_LEAD = 3.0                      # 6쪽: 검색 화면('검색 결과가 없습니다')을 말없이 보여 주는 시간(초). 그 뒤에 말을 뗌
HW.NOTES.update(NOTES)
HW.CUES.update(CUES)
HW.LEAD_EXTRA[('hook', 0)] = HK_LEAD


def rt(ms):
    """실제 시간(ms)으로 적은 값을 s.on()에 넣는 값으로(s.on()이 모든 때와 길이에 SPEED를 곱하므로 미리 나눠 둠)."""
    return ms / HW.SPEED


# ------------------------------------------------------------------ 공통 조각
def title(key, runs, y=46):
    """덱 머리 규격(29pt Bold, 가운데). runs = [(글, 색)]."""
    return T(key, 0, y, 1280, 50, [[(t, dict(color=c, spc=-0.5, spc_ko=-0.5)) for t, c in runs]], size=29, weight='b',
             align='c', anchor='ctr', lnspc=34.8, spc=-0.5)


def foot(key, text, y=676, pt=9.5):
    return T(key, 60, y, 1160, 18, text, size=pt, color=MUTE, anchor='ctr')


def ring(key, cx, cy, ro, pct, color=PURPLE, track=TRACK, k=RING_K):
    """고리 그래프(인트로 7·8쪽과 같은 모양): 바탕 고리 + 12시에서 시계 방향으로 pct%만큼의 호. 호의 끝은 둥글리지 않는다.
    ro = 바깥 반지름, k = 굵기 ÷ 바깥지름. 돌려줌: (바탕 원시 목록, 호 원시 목록)."""
    adj = round(k * 100000)
    end = (16200000 + round(pct / 100 * 21600000)) % 21600000
    box = (cx - ro, cy - ro, 2 * ro, 2 * ro)
    return ([R(key + '/track', *box, prst='donut', fill=track, line=None, adj=dict(adj=adj))],
            [R(key + '/arc', *box, prst='blockArc', fill=color, line=None, adj=dict(adj1=16200000, adj2=end, adj3=adj))])


def logo_word_w(pt):
    """'Weave Assist'(Samsung Sharp Sans Bold, 자간 -0.5pt)의 폭(px). 글꼴 파일이 없으면 어림."""
    f = Path.home() / '.cache' / 'weave-tools' / 'fonts' / 'SamsungSharpSans-Bold.ttf'
    if f.exists():
        from PIL import ImageFont
        return ImageFont.truetype(str(f), 1000).getlength('Weave Assist') * pt * 4 / 3 / 1000 - 11 * 0.5 * 4 / 3
    return tw('Weave Assist', pt, 'b') * 1.1


def logo(key, x, cy, mark=58, pt=44):
    """표지와 같은 로고: 보라 네모 + 흰 실타래, 그 옆에 'Weave Assist'(글꼴과 그라데이션은 make.py의 logo_style이 입힘).
    돌려줌: (네모 원시 목록, 글 원시 목록, 전체 폭)."""
    ic = mark * 2 / 3
    gap = mark * 0.22
    ww = logo_word_w(pt)
    return ([R(key + '/mark', x, cy - mark / 2, mark, mark, prst='roundRect', radius=mark * 15 / 56, line=None,
               grad=dict(stops=[(0, '8D6BFF', None), (55, '6B4EFF', None), (100, '5A3FE0', None)], ang=55), shadow=(20, 8, '6B4EFF', 30)),
             P(key + '/icon', ICON['spool_w'], x + (mark - ic) / 2, cy - ic / 2, ic, ic)],
            [T(key + '/logo_word', x + mark + gap, cy - pt * 0.8, ww + 24, pt * 1.6, 'Weave Assist', size=pt, color=PURPLE, weight='b', anchor='ctr',
               spc=-0.5)],
            mark + gap + ww)


# ------------------------------------------------------------------ 인트로 6쪽: 검색해도 없는 기록 → 수많은 기록 → 문구
HK_BG = '0A0A0E'
HK_HERO = (490, 36, 300, 648)                             # 큰 검색 화면. 줄어들면 벽 한가운데 칸(124×268)에 꼭 맞음
HK_SHRINK = HL.PW / HK_HERO[2]
HK_QUERY = HW.QUERY                                       # '지은이네 집들이 때 마셨던 와인'
HK_WHITE, HK_SOFT = 'F4F4F6', '9B85FF'


def hero_prims(key, fail):
    """큰 휴대폰 화면: 검색창에 질문이 적혀 있고, fail이면 가운데에 '검색 결과가 없습니다'(크게, 빨강)."""
    x, y, w, h = HK_HERO
    qw = tw(HK_QUERY, 11.5, 'm')
    out = [R(key + '/body', x, y, w, h, prst='roundRect', radius=34, fill='FFFFFF', line=None, shadow=(36, 0, 'FFFFFF', 14)),
           T(key + '/time', x + 26, y + 12, 60, 18, '12:30', size=9, color=INK, weight='b', anchor='ctr'),
           R(key + '/bat', x + w - 50, y + 16, 21, 10, prst='roundRect', radius=3, fill=None, line=INK, line_w=1.1),
           R(key + '/batf', x + w - 48, y + 18, 14, 6, prst='roundRect', radius=1.5, fill=INK, line=None),
           R(key + '/field', x + 14, y + 42, w - 28, 40, prst='roundRect', fill='F1F1F5', line=None)]
    out += magnifier(key + '/mag', x + 34, y + 61, r=5.5, color='5A5A64', w=1.7)
    out += [T(key + '/q', x + 50, y + 42, qw + 8, 40, HK_QUERY, size=11.5, color='3A3A42', weight='m', anchor='ctr'),
            R(key + '/cur', x + 50 + qw + 3, y + 52, 1.8, 20, fill=PURPLE, line=None),
            R(key + '/home', x + w / 2 - 45, y + h - 12, 90, 3.5, prst='roundRect', fill='C9C9CF', line=None)]
    if fail:
        out += magnifier(key + '/no', x + w / 2 - 5, y + 214, r=19, color='B8BAC0', w=2.6)
        out += [T(key + '/nt', x, y + 262, w, 40, '검색 결과가 없습니다', size=23, color=RED, weight='b', align='c', anchor='ctr', spc=-0.4)]
    return out


def s_hook():
    """검색 화면 → '검색 결과가 없습니다'(말없이) → 화면이 물러나며 수많은 앱 화면의 벽 → "카톡 대화, 사진, 메모, 일정, 메일까지"에 맞춰
    그 앱의 화면에 불이 켜짐 → (클릭) 불이 꺼지고 문구. 아이콘은 불이 켜진 화면의 왼쪽 위에 붙었다가 함께 꺼진다."""
    s = Slide('hook', trans=('fade', 700), bar=False, bg=False, notes=NOTES['hook'])
    s.add('hk/bg', [R('hk/bg', 0, 0, 1280, 720, fill=HK_BG, line=None)])
    s.add('hk/wall', [P('hk/wall', str(HOOKD / 'mosaic.jpg'), 0, 0, 1280, 720)])
    lit = HL.lit()
    by_app = {a: [] for a in HL.APPS}
    for i, (app, name, x, y) in enumerate(lit):
        k = 'hk/lit%02d' % i
        s.add(k, [P(k + '/s', str(HOOKD / 'screens' / (name + '.jpg')), x, y, HL.PW, HL.PH, radius=HL.RADIUS, shadow=(20, 0, 'FFFFFF', 20)),
                  P(k + '/ic', ICON[app], x - 10, y - 10, 32, 32, shadow=(8, 2, '000000', 45))])
        by_app[app].append(k)
    s.add('hk/veil', [R('hk/veil', 0, 0, 1280, 720, fill='050508', alpha=58, line=None)])
    s.add('hk/hero', hero_prims('hk/hero', False))
    s.add('hk/hero2', hero_prims('hk/hero2', True))
    s.add('hk/l1', [T('hk/l1', 0, 282, 1280, 66, '수많은 기록 속에서,', size=46, color=HK_WHITE, weight='b', align='c', anchor='ctr', spc=-0.6)])
    s.add('hk/l2', [T('hk/l2', 0, 352, 1280, 66, [[('지금 필요한 기록', dict(color=HK_SOFT)), ('을 찾아 헤맵니다', dict(color=HK_WHITE))]],
                      size=46, weight='b', align='c', anchor='ctr', spc=-0.6)])
    # 장이 열리면: 검색 화면 → 결과 없음(천천히, 읽을 시간) → 화면이 물러나며 벽이 드러남
    s.on('hk/hero', 'zoom_in', rt(150), rt(450), **{'from': 0.94})
    s.on('hk/hero2', 'fade_in', rt(1050), rt(700))
    s.on('hk/hero', 'fade_out', rt(1800), rt(40))
    t_out = HK_LEAD * 1000 + 150
    ease = dict(accel=35000, decel=65000)
    s.on('hk/hero2', 'zoom_out', rt(t_out), rt(950), to=HK_SHRINK, **ease)
    s.on('hk/wall', 'zoom_in', rt(t_out), rt(950), **{'from': 1 / HK_SHRINK}, **ease)
    # 말에 맞춰 앱마다 불이 켜짐(천천히)
    t_min = rt(t_out + 950 + 200)
    base = (HK_LEAD + 4.6) * 1000 / HW.SPEED
    for n, app in enumerate(HL.APPS):
        t = max(cue('hook.' + app, base + n * 1100, ahead=0.3), t_min + n * rt(500))
        for j, k in enumerate(by_app[app]):
            s.on(k, 'fade_in', t + rt(j * 90), rt(650))
    s.click()      # 1: 불이 꺼지고 문구
    for k in [k for ks in by_app.values() for k in ks]:
        s.on(k, 'fade_out', 0, rt(520))
    s.on('hk/veil', 'fade_in', rt(120), rt(560))
    s.on('hk/l1', 'rise', rt(380), rt(620), dy=12)
    s.on('hk/l2', 'rise', rt(580), rt(620), dy=12)
    return s


# ------------------------------------------------------------------ 인트로 8쪽 다음: 기록을 남기는 곳(설문 4번)
HB = (336, 372)                    # 가운데(7·8쪽 고리의 가운데)
HB_R = 150                         # 앱이 놓이는 둥근 줄
HB_ITEMS = [   # (키, 이름, %, 아이콘) — 설문 4번(복수 선택), 많이 고른 순서. 위에서 시계 방향. hop/app1~4는 8쪽 오른쪽 아래의 앱 넷(모핑으로 옮겨 옴)
    ('hop/app4', '화면 캡처', 76.7, ICON['gallery']),
    ('hop/app1', '나와의 채팅', 75.7, ICON['talk']),
    ('hop/app3', '메모 앱', 65.2, ICON['note']),
    ('hub2/cam', '사진 촬영', 59.5, CAMERA),
    ('hop/app2', '캘린더', 53.3, ICON['cal']),
    ('hub2/map', '지도 저장', 25.7, ICON['map']),
    ('hub2/mail', '이메일', 14.8, ICON['mail']),
]
HB_TITLE = [('검색해도 안 나오는 내 기록, ', INK), ('찾을 때까지 넘나듭니다', PURPLE)]
HB_SRC = '* 출처: 스마트폰 내 개인 기록 탐색 및 재검색 행태 설문조사 (응답 210명, 2026. 11)'


def hb_pos(i, r=HB_R):
    a = math.radians(-90 + i * 360 / len(HB_ITEMS))
    return HB[0] + r * math.cos(a), HB[1] + r * math.sin(a)


def hb_stat(key, y, head, pct):
    """오른쪽 숫자 한 묶음(7·8쪽 오른쪽과 같은 모양): 한 줄 설명 + 큰 %."""
    num = '%.1f' % pct
    return [T(key + '/h', 570, y, 620, 32, [[(t, dict(color=c)) for t, c in head]], size=18, weight='b', align='c', anchor='ctr'),
            T(key + '/n', 570, y + 28, 620, 98, [[(num, dict(size=60)), ('%', dict(size=28))]], size=60, color=PURPLE, weight='b', align='c',
              anchor='ctr', spc=-1.5)]


def s_hub2():
    """8쪽에서 모핑: 오른쪽 아래의 앱 넷이 왼쪽 둥근 자리로 옮겨 가고 나머지 셋이 뜸 → 앱마다 작은 고리가 그 비율만큼 차오름 →
    가운데 '3.8곳에 분산해 저장' → (클릭) 두 곳 이상 91.4%, 세 곳 이상 74.8%."""
    s = Slide('hub2', trans=('morph', 800), bar=False, notes=NOTES['hub2'])
    s.add('title', [title('title', HB_TITLE)])
    cx, cy = HB
    s.add('hub2/orbit', [R('hub2/orbit', cx - HB_R, cy - HB_R, 2 * HB_R, 2 * HB_R, prst='ellipse', fill=None, line='DCD4F6', line_w=1.3)])
    nodes, rings = [], []
    for i, (key, name, pct, icon) in enumerate(HB_ITEMS):
        x, y = hb_pos(i)
        s.add(key, [R(key + '/halo', x - 28, y - 28, 56, 56, prst='ellipse', fill='FFFFFF', line=TRACK, line_w=1.0, shadow=(14, 3, '6B4EFF', 12)),
                    P(key + '/icon', icon, x - 16, y - 16, 32, 32)])
        base, arc = ring('hub2/r%d' % i, x, y, 35, pct, k=0.062)
        s.add('hub2/r%d/t' % i, base)
        s.add('hub2/r%d/a' % i, arc)
        lx, ly = HB[0] + (HB_R + 84) * math.cos(math.radians(-90 + i * 360 / len(HB_ITEMS))), hb_pos(i, HB_R + 68)[1]   # 숫자와 이름은 고리 바깥, 옆으로는 조금 더 멀리
        s.add('hub2/l%d' % i, [T('hub2/l%d/p' % i, lx - 60, ly - 21, 120, 22, '%.1f%%' % pct, size=14.5, color=PURPLE, weight='b', align='c', anchor='ctr'),
                               T('hub2/l%d/n' % i, lx - 60, ly + 1, 120, 20, name, size=11, color=SUB, align='c', anchor='ctr')])
        nodes.append(key)
        rings.append(i)
    s.add('hub2/core', [T('hub2/core/n', cx - 90, cy - 44, 180, 58, [[('3.8', dict(size=44)), ('곳', dict(size=22))]], size=44, color=PURPLE, weight='b',
                          align='c', anchor='ctr', spc=-1),
                        T('hub2/core/t', cx - 90, cy + 14, 180, 26, '에 분산해 저장', size=15, color=INK2, weight='b', align='c', anchor='ctr')])
    s.add('hub2/a', hb_stat('hub2/a', 212, [('두 곳 이상', PURPLE), ('에 나눠 저장', INK)], 91.4))
    s.add('hub2/b', hb_stat('hub2/b', 398, [('세 곳 이상', PURPLE), ('에 나눠 저장', INK)], 74.8))
    s.add('foot', [T('foot', 100, 664, 1100, 21, HB_SRC, size=12, color=MUTE, anchor='ctr')])
    # 모핑이 끝나면: 둥근 줄 → 새 앱 셋 → 앱마다 고리와 숫자 → 가운데 3.8곳
    s.on('hub2/orbit', 'fade_in', 0, 450)
    new = [k for k in nodes if k.startswith('hub2/')]
    for j, k in enumerate(new):
        s.on(k, 'zoom_in', 150 + j * 130, 360, **{'from': 0.7})
    for i in rings:
        t = 520 + i * 150
        s.on('hub2/r%d/t' % i, 'fade_in', t, 300)
        s.on('hub2/r%d/a' % i, 'wheel_in', t + 80, 700)
        s.on('hub2/l%d' % i, 'fade_in', t + 200, 400)
    tc = max(cue('hub2.avg', 3200, ahead=0.3), 520 + len(rings) * 150 + 300)
    s.on('hub2/core', 'zoom_in', tc, 480, **{'from': 0.8})
    s.click()      # 1: 두 곳 이상, 세 곳 이상
    s.on('hub2/a', 'rise', 150, 520, dy=12)
    s.on('hub2/b', 'rise', max(cue('hub2.three', 3600, ahead=0.3), 900), 520, dy=12)
    return s


# ------------------------------------------------------------------ 인트로 → 모션그래픽을 잇는 장
BR_MARK, BR_PT, BR_CY = 86, 66, 292                       # 로고(모션그래픽 첫 화면과 같은 자리: 가운데, 조금 위)
BR_FLOAT = [   # (키, 아이콘, 가운데 x, y, 크기, 진하기 %, 떠 있는 동안 흘러가는 만큼). 실에 꿰이는 넷은 BR_LINK, 나머지는 실에서 떨어져 작고 옅게
    ('phone', ICON['phone'], 214, 458, 42, 60, (8, -6)),
    ('talk', ICON['talk'], 392, 468, 60, 100, (6, 7)),
    ('map', ICON['map'], 322, 604, 40, 56, (-7, -6)),
    ('gallery', ICON['gallery'], 556, 536, 60, 100, (-6, -7)),
    ('mail', ICON['mail'], 512, 644, 44, 60, (7, -5)),
    ('note', ICON['note'], 724, 470, 60, 100, (7, 6)),
    ('camera', CAMERA, 748, 622, 42, 56, (-6, 6)),
    ('cal', ICON['cal'], 888, 534, 60, 100, (-7, -6)),
    ('wallet', ICON['wallet'], 1066, 588, 44, 60, (-8, 5)),
]
BR_LINK = ['talk', 'gallery', 'note', 'cal']
BR_C0, BR_C1 = (0xB5, 0x97, 0xFF), (0x6B, 0x4E, 0xFF)       # 실의 왼쪽 끝과 오른쪽 끝 색


def br_thread():
    """실 한 가닥: 왼쪽에서 들어와 앱 넷을 물결처럼 지나 오른쪽 끝의 별까지. 앱마다 수평으로 드나들어 매끄럽게 이어진다.
    돌려줌: [(키, 점들, 색 띠)] — 색은 실 전체에 걸쳐 연보라에서 보라로."""
    pos = {k: (x, y) for k, _, x, y, _, _, _ in BR_FLOAT}
    pts = [(292, 504)] + [pos[k] for k in BR_LINK] + [(986, 494)]
    x0, x1 = pts[0][0], pts[-1][0]
    col = lambda x: '%02X%02X%02X' % tuple(round(a + (b - a) * (x - x0) / (x1 - x0)) for a, b in zip(BR_C0, BR_C1))
    out = []
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        d = (b[0] - a[0]) * 0.45
        out.append(('br/th%d' % i, [a, (a[0] + d, a[1]), (b[0] - d, b[1]), b], [(0, col(a[0]), 0 if i == 0 else None), (100, col(b[0]), None)]))   # 왼쪽 끝은 옅게 시작
    return out, pts[-1]


def s_bridge():
    """모션그래픽 첫 화면처럼 가운데 위에 'Weave Assist', 그 아래 한 줄 소개 자리에는 글 대신 떠 있는 앱들 →
    (클릭) 실 한 가닥이 앱 넷을 차례로 이음."""
    s = Slide('bridge', trans=('fade', 600), bar=False, notes=NOTES['bridge'])
    _, _, total = logo('br/logo', 0, BR_CY, BR_MARK, BR_PT)
    mark, word, _ = logo('br/logo', 640 - total / 2, BR_CY, BR_MARK, BR_PT)
    th, end = br_thread()
    for key, pts, stops in th:
        s.add(key, [C(key, pts, w=3.4, stops=stops)])
    s.add('br/star', star4_icon('br/star', end[0] + 14, end[1], r=9))
    drift = {}
    for k, icon, x, y, sz, al, d in BR_FLOAT:
        key = 'br/' + k
        s.add(key, [P(key, icon, x - sz / 2, y - sz / 2, sz, sz, alpha=al, shadow=(14, 4, '6B4EFF', 16))])
        drift[k] = d
    s.add('br/mark', mark)
    s.add('br/word', word)
    # 장이 열리면: 앱들이 서서히 떠오르고 제자리에서 조금씩 흘러감 → 'Weave Assist'
    for i, (k, *_) in enumerate(BR_FLOAT):
        s.on('br/' + k, 'fade_in', 150 + i * 90, 500)
        s.on('br/' + k, 'move', 200 + i * 90, 9500, dx=drift[k][0], dy=drift[k][1], accel=0, decel=0)
    t = max(cue('bridge.logo', 5200, ahead=0.25), 1100)
    s.on('br/mark', 'zoom_in', t, 420, **{'from': 0.7})
    s.on('br/word', 'rise', t + 120, 520, dy=12)
    s.click()      # 1: 실이 왼쪽에서 들어와 앱 넷을 차례로 이음
    tw_ = max(cue('bridge.weave', 3000, ahead=0.3), 500)
    step = 380
    s.on('br/th0', 'wipe_in', tw_, 300, dir='left')
    for i, k in enumerate(BR_LINK):
        ti = tw_ + 300 + i * step
        s.on('br/' + k, 'fly', ti - 260, 420, dx=drift[k][0], dy=drift[k][1], bend=0, show=False, fade=False)   # 흘러가 있던 자리에서 제자리로
        s.on('br/' + k, 'pulse', ti - 40, 150, scale=1.12)
        s.on('br/th%d' % (i + 1), 'wipe_in', ti, step, dir='left')
    s.on('br/star', 'zoom_in', tw_ + 300 + len(BR_LINK) * step - 60, 320, **{'from': 0.4})
    return s


# ------------------------------------------------------------------ 뒷부분 1: 기대효과 세 장
FX_TITLE = [('찾는 시간은 줄이고, ', INK), ('놓친 기억은 되살립니다', PURPLE)]
FX_SRC = "* 출처: 자체 사용자 설문 ('예' 응답 비율, 응답자 210명)"
FX_CX, FX_CY, FX_RO = 262, 398, 106
FX = {      # 장 키: (번호, 불편(두 줄), %, 명, 기능 이름, UX 묶음, 묶음 자리, 이름표 y, 기능이 있으면(두 줄, 제안 장표에서만))
    'fx1': (1, ['어느 앱인지 몰라', '앱을 하나씩 열어 봤어요'], 83.8, 176, '기록 통합 검색', 'ux1', Xf(40, 218, 628, 196, 0.98), 150,
            ['어느 앱인지 몰라도', '한 번의 검색으로 찾아요']),
    'fx2': (2, ['이름이 떠오르지 않아', '검색으로 바로 찾지 못했어요'], 93.8, 197, '단서로 찾는 기억', 'ux2', Xf(640, 218, 566, 330, 1.12), 270,
            ['이름이 떠오르지 않아도', '기억나는 상황으로 찾아요']),
    'fx3': (3, ['챙겨야 할 부탁, 약속을', '나중에야 떠올렸어요'], 82.4, 173, '먼저 건네는 기억', 'ux3', Xf(640, 492, 566, 328, 1.12), 270,
            ['챙겨야 할 부탁, 약속을', 'Weave가 먼저 알려 줘요']),
}


def s_fx(key, first=False, effect=False):
    """기대효과 한 장: 왼쪽에 설문의 불편(말 + 고리 그래프), (클릭) 오른쪽에 그 불편에 답하는 기능과 화면.
    effect=True(제안 장표 p_fx*): 고리가 처음에는 짙은 색(불편을 겪은 사람)이고, 클릭하면 보라가 그 위를 덮으며 왼쪽 말이 '기능이 있으면'으로 바뀐다.
    숫자는 설문 값 그대로 두고 뜻만 바뀐다(불편을 겪은 83.8% → Weave가 돕는 83.8%)."""
    n, stmt, pct, cnt, name, ux, xf, ly, after = FX[key]
    sk = ('p_' + key) if effect else key
    s = Slide(sk, trans=('fade', 500) if first else ('morph', 800), bar=False, notes=NOTES[sk])
    s.add('fx/title', [title('fx/title', FX_TITLE)])
    s.add('fx/stmt', [caption('fx/stmt', [[(ln, INK)] for ln in stmt], FX_CX, 170, size=21, lh=32)])
    base, arc = ring('fx/ring', FX_CX, FX_CY, FX_RO, pct, color=NAVY if effect else PURPLE)
    s.add('fx/ring', base)
    s.add('fx/arc', arc)
    pt = 38
    num = '%.1f' % pct
    nw = tw(num, pt, 'b') + tw('%', 20, 'b') + 2
    numt = lambda k, col: [T(k, FX_CX - nw / 2 - 4, FX_CY - 27, nw + 16, 54, [[(num, dict(size=pt)), ('%', dict(size=20))]], size=pt, color=col,
                             weight='b', anchor='ctr', spc=-0.5)]
    s.add('fx/num', numt('fx/num', NAVY if effect else PURPLE))
    s.add('fx/cnt', [T('fx/cnt', FX_CX - 150, FX_CY + FX_RO + 22, 300, 24,
                       [[('응답자 210명 중 ', dict(color=MUTE)), ('%d명' % cnt, dict(color=SUB, weight='b'))]], size=12.5, align='c', anchor='ctr')])
    if effect:
        s.add('fx/arc2', ring('fx/ring2', FX_CX, FX_CY, FX_RO, pct)[1])
        s.add('fx/num2', numt('fx/num2', PURPLE))
        s.add('fx/after', [caption('fx/after', [[(after[0], INK)], [(after[1], PURPLE)]], FX_CX, 170, size=21, lh=32)])
    s.add('fx/rule', [R('fx/rule', 520, 150, 1, 500, fill='D9CEFA', line=None)])
    lx = 566
    s.add('fx/no', numdot('fx/no', lx + 16, ly + 16, n, r=16, pt=12.5))
    s.add('fx/name', [T('fx/name', lx + 44, ly, tw(name, 19, 'b') + 12, 32, name, size=19, color=INK, weight='b', anchor='ctr')])
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
    tn = max(cue(sk + '.num', 1600, ahead=0.3), 700)
    s.on('fx/arc', 'wheel_in', tn, 900)
    s.on('fx/num', 'fade_in', tn + 350, 400)
    s.on('fx/cnt', 'fade_in', tn + 900, 400)
    s.click()      # 1: 이 불편에 답하는 기능과 화면
    s.on('fx/rule', 'fade_in', 0, 300)
    s.on(['fx/no', 'fx/name'], 'rise', 80, 420, dy=10)
    s.on(keys, 'rise', 320, 560, dy=14)
    if effect:     # 화면이 뜬 뒤: 보라가 고리를 덮고, 숫자와 말이 바뀜
        s.on('fx/arc2', 'wheel_in', 1000, 1000)
        s.on('fx/num', 'fade_out', 1300, 350)
        s.on('fx/num2', 'fade_in', 1450, 400)
        s.on('fx/stmt', 'fade_out', 1000, 350)
        s.on('fx/after', 'rise', 1300, 520, dy=10)
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
    base, arc = ring('bi/pie', BI_RX, 252, 70, 69)
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
CMP_X0, CMP_W, CMP_GAP, CMP_TOP = 178, 228, 16, 162
CMP_HEAD, CMP_RH = 112, 92
CMP_SRC = '* Samsung 지원 페이지(Finder), Samsung Newsroom(Galaxy S26, 2026. 2), 카카오 발표(2026. 3)의 공식 설명을 기준으로 함'


def cmp_icon(key, kind, cx, cy):
    """열 머리의 작은 그림(38px 칸). 기능마다 색을 달리한다: Finder 파랑, Now Nudge 청록, 카나나는 카카오톡 아이콘, Weave 보라."""
    z = 38
    tile = lambda a, b: R(key + '/tile', cx - z / 2, cy - z / 2, z, z, prst='roundRect', radius=11, line=None,
                          grad=dict(stops=[(0, a, None), (100, b, None)], ang=55))
    if kind == 'finder':
        r = 7.5
        return [tile('5B9BFF', '2F6BE6'), R(key + '/c', cx - r - 2, cy - r - 2, 2 * r, 2 * r, prst='ellipse', fill=None, line='FFFFFF', line_w=2.4),
                C(key + '/h', [(cx + 3.6, cy + 3.6)] * 2 + [(cx + 9.5, cy + 9.5)] * 2, color='FFFFFF', w=2.6)]
    if kind == 'nudge':
        return [tile('2CC4B5', '1F8FD6')] + spark_icon(key + '/s', cx - 12, cy - 12, size=24, color='FFFFFF')
    if kind == 'kanana':
        return [P(key + '/k', ICON['talk'], cx - z / 2, cy - z / 2, z, z)]
    return [tile('8D6BFF', '5A3FE0'), P(key + '/sp', ICON['spool_w'], cx - 12, cy - 12, 24, 24)]


def s_cmp():
    """기존 기능 셋과 Weave를 세 가지로만 견준다(찾는 범위·찾는 방식·쓰는 자리). 네 칸의 틀과 기존 기능이 먼저 뜨고, (클릭) Weave 칸이 켜지며 채워진다."""
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
    s.add('cmp/src', [foot('cmp/src', CMP_SRC)])
    s.on('cmp/labs', 'fade_in', 150, 400)
    for i, k in enumerate(('finder', 'nudge', 'kanana', 'weave')):
        s.on('cmp/' + k, 'rise', 300 + i * 240, 480, dy=14)
    s.click()      # 1: Weave 칸이 켜지고 채워짐
    s.on('cmp/weave/hi', 'fade_in', 0, 420)
    s.on('cmp/weave/cells', 'rise', 200, 480, dy=10)
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


# ------------------------------------------------------------------ 뒷부분 5: 마무리(사진 위에 글). 끝 로고는 마지막 장 안에서 뜬다
WHITE, SOFT = 'FFFFFF', 'D9CCFF'
VEIL = '120A24'


def photo_bg(key, fname, veil=40, top=62, bottom=30):
    """사진을 장 가득 깔고, 글이 읽히게 위에서 아래로 옅어지는 어둠을 얹는다."""
    return [P(key + '/photo', str(PHOTO / fname), 0, 0, 1280, 720),
            R(key + '/veil', 0, 0, 1280, 720, fill=None, line=None,
              grad=dict(stops=[(0, VEIL, top), (55, VEIL, veil), (100, VEIL, bottom)], ang=90))]


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


HAND = (670, 436)                  # 손글씨 '순간' 그림의 크기(px)


def s_end2():
    """해 질 녘을 휴대폰으로 담는 사람. 왼쪽 하늘에 손글씨 '순간'."""
    s = Slide('end2', trans=('fade', 900), bar=False, bg=False, notes=NOTES['end2'])
    s.add('end/bg', photo_bg('end/bg', 'closing-2-capture.jpg', veil=50, top=60, bottom=46))
    w = 400
    s.add('end/hand', [P('end/hand', str(OUTRO / 'moment-hand-white.png'), 318 - w / 2, 318 - w * HAND[1] / HAND[0] / 2, w, w * HAND[1] / HAND[0])])
    s.on('end/hand', 'wipe_in', 500, 1100, dir='left')
    return s


def s_end3():
    """손글씨 '순간'이 문장 속으로 → "Weave가"에 맞춰 문장 아래에 끝 로고가 뜬다(따로 있던 보라 끝 화면을 이 장에 합침)."""
    s = Slide('end3', trans=('morph', 1100), bar=False, bg=False, notes=NOTES['end3'])
    s.add('end/bg', photo_bg('end/bg', 'closing-3-sunset-picnic.jpg', veil=34, top=62, bottom=24))
    pt = 36
    a, b = '갤럭시의 모든 ', '이'
    hw = 118                                             # 문장 속 손글씨 '순간'의 폭
    wa, wb = tw(a, pt, 'b'), tw(b, pt, 'b')
    x0 = 640 - (wa + hw + 6 + wb) / 2
    y1 = 130
    lw = 214
    lh = lw * 421 / 1996
    ly = y1 + 62 + 56 + 34
    s.add('end3/shade', [R('end3/shade', 640 - 300, ly + lh / 2 - 86, 600, 172, prst='ellipse', fill=None, line=None,
                           grad=dict(stops=[(0, VEIL, 54), (60, VEIL, 22), (100, VEIL, 0)], path='circle'))])
    s.add('end3/a', [T('end3/a', x0, y1, wa + 10, 56, a, size=pt, color=WHITE, weight='b', anchor='ctr', spc=-0.4)])
    s.add('end/hand', [P('end/hand', str(OUTRO / 'moment-hand-white.png'), x0 + wa - 4, y1 + 28 - hw * HAND[1] / HAND[0] / 2 - 4, hw, hw * HAND[1] / HAND[0])])
    s.add('end3/b', [T('end3/b', x0 + wa + hw + 6, y1, wb + 10, 56, b, size=pt, color=WHITE, weight='b', anchor='ctr', spc=-0.4)])
    s.add('end3/c', [T('end3/c', 240, y1 + 62, 800, 56, [[('다시 ', dict(color=WHITE)), ('이야기', dict(color=SOFT)), ('가 되도록', dict(color=WHITE))]],
                       size=pt, weight='b', align='c', anchor='ctr', spc=-0.4)])
    s.add('end3/logo', [P('end3/logo', str(OUTRO / 'end-logo.png'), 640 - lw / 2, ly, lw, lh)])
    sw = lw * 1.05
    s.add('end3/sw', [P('end3/sw', str(OUTRO / 'end-swoosh.png'), 640 - sw / 2, ly + lh + 3, sw, sw * 225 / 2156)])
    s.on(['end3/a', 'end3/b'], 'fade_in', 200, 600)
    s.on('end3/c', 'rise', 900, 800, dy=12)
    tl_ = max(cue('end3.logo', 4200, ahead=0.2), 2000)
    s.on('end3/shade', 'fade_in', tl_, 700)
    s.on('end3/logo', 'rise', tl_ + 100, 800, dy=10)
    s.on('end3/sw', 'wipe_in', tl_ + 600, 700, dir='left')
    return s


# ------------------------------------------------------------------ 제안: 새 연표(위는 기술, 아래는 갤럭시, 두 줄이 2026년의 Weave에서 만남)
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
    """두 줄(위 = 기술, 아래 = 갤럭시) → (클릭) 기술 → (클릭) 갤럭시 → (클릭) 두 줄이 Weave에서 만남. 마디는 말하는 차례대로 하나씩."""
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
    s.click()      # 1: 기술(위) — 말하는 해마다 하나씩
    for i, (k, d) in enumerate(zip(ups, (1500, 5200, 9800, 14200))):
        s.on(k, 'rise', cue('p_tl.u%d' % i, d, ahead=0.2), 460, dy=-12)
    s.click()      # 2: 갤럭시(아래)
    for i, (k, d) in enumerate(zip(dns, (2600, 5200, 9600, 12400))):
        s.on(k, 'rise', cue('p_tl.d%d' % i, d, ahead=0.2), 460, dy=12)
    s.click()      # 3: 두 줄이 Weave에서 만남
    s.on(['pt/ju', 'pt/jl'], 'wipe_in', 0, 520)
    s.on('pt/wglow', 'fade_in', 420, 500)
    s.on('pt/w', 'zoom_in', 480, 420, **{'from': 0.6})
    s.on('pt/w', 'pulse', 940, 180, scale=1.08)
    return s


# ------------------------------------------------------------------ 가름 장, 사진 출처
def s_divider(key, head, lines, note):
    s = Slide(key, trans=('fade', 500), bar=False, notes=note)
    s.add(key + '/t', [caption(key + '/t', [[(head, PURPLE)]], 640, 250, size=44)])
    s.add(key + '/s', [T(key + '/s', 160, 336, 960, 26 * len(lines), lines, size=14, color=SUB, align='c', lnspc=20)])
    return s


PHOTO_CREDITS = [('마무리 1 (해 질 녘)', 'Harli Marten, "Pink sunset couple", Unsplash (Wikimedia Commons 사본), CC0'),
                 ('마무리 2 (순간을 담는 사람)', 'Ben White, "Woman shooting ocean sunset", Unsplash (Wikimedia Commons 사본), CC0'),
                 ('마무리 3 (노을 소풍)', 'Arthur Poulin, "Sunset Picnic", Unsplash (Wikimedia Commons 사본), CC0'),
                 ('6쪽 화면 속 사진', 'Unsplash 사진 63장 (Wikimedia Commons 사본), 모두 CC0. 목록은 assets/src/photos/credits.json')]


def s_credits2():
    s = Slide('apx_credit2', trans=('fade', 400), bar=False, notes='마무리 장과 6쪽에 쓴 사진의 출처입니다.')
    s.add('cr2/title', [caption('cr2/title', [[('사진 출처', INK)]], 640, 54, size=24)])
    s.add('cr2/sub', [T('cr2/sub', 100, 54 + 24 * 1.42 + 6, 1080, 24, '마무리 장의 배경 사진과 6쪽 휴대폰 화면 속 사진', size=13, color=SUB, align='c')])
    out = []
    for i, (a, b) in enumerate(PHOTO_CREDITS):
        y = 160 + i * 64
        out += [R('cr2/%d/bg' % i, 160, y, 960, 52, prst='roundRect', radius=14, fill='FFFFFF', line=LINE2, line_w=1.0),
                T('cr2/%d/a' % i, 184, y, 220, 52, a, size=12, color=PURPLE, weight='b', anchor='ctr'),
                T('cr2/%d/b' % i, 410, y, 700, 52, b, size=10.5, color=BODY, anchor='ctr')]
    s.add('cr2/rows', out)
    return s


SLIDES_BACK = [lambda: s_fx('fx1', first=True), lambda: s_fx('fx2'), lambda: s_fx('fx3'), s_bi, s_cmp, s_tl, s_end1, s_end2, s_end3]
SLIDES_PROPOSAL = [lambda: s_fx('fx1', first=True, effect=True), lambda: s_fx('fx2', effect=True), lambda: s_fx('fx3', effect=True), s_p_tl]
