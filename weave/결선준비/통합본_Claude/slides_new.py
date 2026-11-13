"""통합본에 새로 그린 장 (How it Works와 같은 엔진: 09_HowItWorks/장표5_claude).

인트로
- hook: 6쪽. 검색해도 없는 기록 → 수많은 기록(앱 화면의 벽) → (클릭마다) 카톡 대화, 사진, 메모, 일정, 메일의 화면 한 곳에서 세 곳에 불 → (클릭) 불이 꺼지고 문구.
- hub2: 9쪽. 8쪽의 앱 네 개가 둥근 자리로 옮겨 가고, 기록을 남기는 곳 일곱과 평균 3.8곳 → (클릭) 두 곳 이상, 세 곳 이상.
- scat, link: 11~12쪽. '지금의 나' 둘레에 흩어져 있던 기록이(11쪽) 가운데로 모여 반듯해지고 선으로 이어진다(12쪽). 인트로 덱 10~11쪽의 차례를 뒤집어 다시 그린 것.
- bridge: 14쪽. 모션그래픽 첫 화면처럼 가운데 위에 로고, 그 아래 떠 있는 앱들 → (클릭) 실 한 가닥이 넷을 이음.
뒷부분
- bi, tl, end1~3: 아웃트로 덱(Weave_BI_아웃트로_통합_1110_v7.pptx)의 내용을 우리 틀로 다시 그린 것. 연표(tl)는 두 줄이 Weave에서 만나는 모양.
- 6차(11-13): 기대효과는 한 장(fx_new.s_fx, 키 fx). 여기의 s_fx(세 장, fx1~3)와 제안 장표(p_fx1~3)는 5차까지 쓰던 것.
  기존 기능과의 비교는 Appendix로 옮김(cmp_new.s_cmp_apx). 여기의 s_cmp(두 축 지도)는 5차까지 쓰던 것이고 아이콘과 이름표(cmp_icon, map_point)는 계속 씀.
- 7차(11-13): 비교 장이 다시 본 발표로(cmp_new.s_cmp, 키 cmp. 말할 글은 여기 NOTES['cmp']), 맺는 인사를 하는 마지막 장(s_bye: 아이콘과 Weave 글자만).
  bi는 앱 아이콘을 5차의 묶음(19개)으로 되돌리고 휴대폰 안 동그라미 아래에 'Weave Assist'.

좌표는 1280×720 px. 말할 글은 NOTES((클릭) = 그 자리에서 클릭)와 INTRO_NOTES(옮겨 온 인트로 장의 노트)에 있다.
"""
import math
from pathlib import Path

import build as HW
from ui import (BODY, ICON, INK, INK2, LAV, LAV2, LINE, LINE2, MUTE, PURPLE, PURPLE2, RED, RING, SUB, SHADOW_CARD, SHADOW_LIFT, SHADOW_SOFT,
                C, P, R, T, Xf, caption, magnifier, numdot, spark_icon, star4_icon, thread, tw)

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
# 설문 각주: 7~9쪽과 33~35쪽이 모두 같은 글(11-12 통일). 응답은 2026-10-28 ~ 11-04에 받음
SURVEY_SRC = "* 스마트폰 내 개인 기록 탐색 및 재검색 행태에 관한 자체 설문조사 (응답자 210명, '26.11)"

# ------------------------------------------------------------------ 말할 글
# 표지와 옮겨 온 인트로 장의 노트. 괄호 속은 무대 지시(팀원 노트 그대로), 나머지가 말할 글.
# 11-12 5차: 7~14쪽은 팀원이 손본 덱(jjun-0824/t3 87bf80b)의 장과 노트를 그대로 옮긴다. 7, 8, 9, 10, 14쪽의 노트가 바뀌었고 9, 11, 12, 14쪽의 노트도 여기로 옮겨 옴.
# 11-12 밤: '이름이' → '정확한 이름이'(덱 전체), 기대효과 문장의 '검색으로 바로 찾지' → '검색으로 찾지'. 4쪽은 말풍선(make.patch_ask2)과 노트.
# 11-13 6차: 2쪽의 끝 문장을 3쪽 첫머리로 옮기고 3쪽에 클릭(그 문장을 말하는 동안에는 떠다니는 기록 조각만 보임), 7쪽은 설문 6번의 말 그대로, 9쪽은 이어 주는 말로.
# 11-13 8차: 발표자가 다시 쓴 대본으로(2~5, 7~12, 14쪽). 12쪽을 둘로 나눔: 기록 그림만 가운데로 옮겨 오는 장(gath, 새 12쪽)과 기록이 이어지는 장(link, 13쪽).
INTRO_NOTES = {
    'cover': ('(화면: 흩어진 기억을 엮어, 지금을 완성하다 — Weave Assist)\n'
              '안녕하세요. 흩어진 기억을 엮어 지금을 완성하는 온디바이스 AI, Weave Assist 발표를 맡은 장이준입니다.'),
    'in02': ('(장이 열리면 통화 중 00:48 표시가 뜨고 "잠깐만요, 찾아보고 다시 알려 드릴게요." 문장이 한 글자씩 나타납니다. '
             '문장이 다 뜰 때까지 1초쯤 기다립니다. 클릭 없음)\n'
             "'잠깐만요, 찾아보고 다시 알려 드릴게요.' 여러분, 통화하다가 이런 말 해 보신 적 없으신가요?\n"
             '분명히 내 휴대폰 어딘가에 기록해 두었는데, 바로 찾지는 못할 때 나오는 말입니다.'),
    'in03': ('(장이 열리면 옅은 기록 조각만 떠다닙니다. 인물은 아직 없습니다.)\n'
             '우리는 필요한 정보를 찾으려 여러 앱을 넘나들곤 합니다.\n'
             "(클릭) (첫 번째 인물과 '어디에 적어 놨더라?' 말풍선이 나타납니다.)\n"
             '이러한 순간을 크게 세 가지로 나눌 수 있는데요.\n'
             '첫째, 찾을 내용은 분명한데, 어느 앱에 남겼는지 모를 때입니다.'),
    'in04': ("(장이 열리면 첫 인물이 옆으로 비켜서고, 두 번째 인물과 '정확한 이름이 뭐였지?' 말풍선이 나타납니다.)\n"
             '둘째, 그날의 장면은 선명한데 검색할 정확한 이름이 떠오르지 않을 때입니다.'),
    'in05': ("(장이 열리면 세 번째 인물과 '그런 얘기가 있었나?' 말풍선이 나타납니다.)\n"
             '셋째, 대화방에 남아 있는 부탁이나 약속 자체를 필요한 순간엔 잊었을 때입니다.'),
    'in07': ('(장이 열리면 왼쪽 링이 93.8%까지 채워지고 오른쪽 수치 197명이 나타납니다. 따로 클릭하지 않아도 됩니다.)\n'
             "실제 사용자 설문에서도, 93.8%가 '정확한 이름이 떠오르지 않아 검색으로 찾지 못한 경험이 있다'고 답했습니다."),
    'in08': ('(장이 열리면 같은 링 안에서 그 197명 중 187명(94.9%)이 보라색으로 채워지고, 돋보기 표시가 앱 넷을 차례로 건너뛰다 처음 앱으로 되돌아갑니다. '
             '따로 클릭하지 않아도 됩니다.)\n'
             '그리고 그중 94.9%는 단서가 될 기록부터 직접 여러 앱을 뒤져 다시 찾고 있었습니다.'),
    'hub2': '이는 우리가 정보를 한 가지 앱에 기록하기보다, 화면 캡처, 카카오톡, 메모처럼 그 순간 가장 편한 곳에 정보를 분산하여 기록하기 때문입니다.',
    'in09': ('(장이 열리면 오른쪽 AI 어시스턴트 ("임베딩 모델이 뭐야?" ➔ AI 답변) 대화 화면이 차례로 나타납니다.)\n'
             '그런데, 문득!! 한 가지 의문이 들었습니다.\n'
             "'세상의 모든 지식은 이렇게 AI에게 묻는데,'"),
    'scat': "'정작 내 기록은 왜 아직도 찾아 헤맬까요?'",
    'gath': ('(왼쪽의 물음이 걷히고, 오른쪽에 흩어져 있던 기록 그림만 화면 가운데로 옮겨 옵니다.)\n'
             '대화도, 메모도, 사진도 사라진 게 아닙니다.'),
    'link': ("(흩어져 있던 기록이 반듯해지고 '지금의 나'와 선으로 이어집니다.)\n"
             "흩어진 기록들을 하나로 잇는 '연결고리'가 없었을 뿐입니다."),
    'in12': '(톤을 한 단계 높여) 그렇다면, AI에게 물어보듯 내 휴대폰에게 바로 물을 수는 없을까요? (0.5초 쉬고 다음 장)',
    'bridge': "오늘, 우리는 흩어진 나의 기억들과 지금의 나를 이어 줄 새로운 연결고리, 'Weave Assist'를 제안합니다.",
}
NOTES = {
    'hook': ('우리는 매일 셀 수 없이 많은 기록을 남깁니다. '
             '(클릭) 카톡 대화, (클릭) 사진, (클릭) 메모, (클릭) 일정, (클릭) 메일까지. '
             '(클릭) 수많은 기억 속에서, 지금 필요한 기억을 찾아 헤매는 것. 저희는 바로 이 문제에서 출발했습니다.'),
    # hub2, scat, link, bridge: 4차까지 여기서 그리던 장의 노트(s_hub2, s_scat, s_link, s_bridge). 5차부터 덱에는 팀원이 손본 장이 들어가고 말할 글은 INTRO_NOTES
    'hub2': ('기록을 남길 때부터 한 사람이 평균 3.8곳에 나눠 저장하기 때문입니다. '
             '(클릭) 91.4%는 두 곳 이상에, 74.8%는 세 곳 이상에 나눠 남기고 있었습니다.'),
    'scat': ("'왜 정작 나에 대한 모든 기록이 담긴 내 휴대폰 안에서는, 아직도 이렇게 찾아 헤매야 할까요?' "
             '대화도, 메모도, 사진도 사라진 게 아닙니다.'),
    'link': "앱마다 흩어져 있는 어제의 기록들을 하나로 엮어, 오늘의 나에게 데려와 줄 '연결고리'가 없었을 뿐입니다.",
    'bridge': ("오늘, 우리는 흩어진 나의 기억들과 지금의 나를 이어 줄 새로운 연결고리, 'Weave Assist'를 제안합니다. "
               '(클릭) 앱을 일일이 켜고 찾아 헤맬 필요 없이, 흩어진 기억의 단서들을 엮어 필요한 순간 건네주는 온디바이스 AI입니다.'),
    'fx1': ('저희 설문에서 응답자의 83.8%는 어느 앱에 남겼는지 몰라 앱을 하나씩 열어 봤다고 답했습니다. '
            '(클릭) 기록 통합 검색이 이 헤매는 시간을 줄여 줍니다.'),
    'fx2': ('93.8%는 정확한 이름이 떠오르지 않아 검색으로 찾지 못했습니다. '
            '(클릭) 단서로 찾는 기억은 기억나는 상황만으로 찾아 줍니다.'),
    'fx3': ('82.4%는 부탁이나 약속을 나중에야 떠올렸습니다. '
            '(클릭) 먼저 건네는 기억이 묻기 전에 먼저 알려 줍니다.'),
    # 11-13 8차: 뒷부분의 말은 발표자가 다시 쓴 글 그대로(bi, cmp, tl, end1, end2, bye)
    'bi': ('사람들은 한 달에 평균 41개의 앱을 사용하며, '
           '(클릭) 69%는 기록을 지우지 않고 쌓아 둔다고 합니다. '
           '(클릭) Weave는 이 기록을 하나의 기록으로 엮어, 쓸수록 갤럭시를 떠나기 어렵게 합니다.'),
    'cmp': ('그렇다면 기존의 AI 서비스들과 무엇이 다를까요? '      # 8차: 이 장은 Appendix로 옮김(cmp_new.s_cmp_apx2). 질문이 나오면 이렇게 말함
            'Writing Assist는 지금 쓰는 글을 다듬고, 카나나는 카카오톡 내에서 대화 요약과 맞춤형 제안을 제공합니다. '
            'Now Nudge와 Finder 역시 지금 화면에 맞춰 제안하거나 한 번 탐색하는 데 그칩니다. '
            '(클릭) Weave는 여러 앱에 흩어진 단서를 찾을 뿐 아니라, 이들을 연결함으로써 사용자가 정말 원하는 답이 무엇인지 찾아줍니다.'),
    'tl': ('그렇다면 왜 지금일까요? '
           '(클릭) 검색 기술은 뜻으로 찾는 임베딩에서, 찾아낸 정보를 바탕으로 답하는 RAG로 발전했고, '
           '지난해에는 추론하며 찾는 Reasoning Embedding이, 올해는 단서를 이어 찾는 AgentIR과 Hi-Q가 나왔습니다. '
           '(클릭) 갤럭시도 준비를 마쳤습니다. 온디바이스 AI 연산을 위한 NPU가 들어왔고, '
           '2024년에는 Galaxy AI가, 지난해에는 개인 데이터를 기기 안에서 다루는 Personal Data Engine, 즉 PDE가 더해졌습니다. '
           '(클릭) 기술과 인프라가 모두 준비된 지금이, Weave가 필요한 때입니다.'),
    'end1': ('당신이 사랑하는 모든 것에 더 가까이 다가가고, 오래도록 이야기하게 될 순간을 담아보세요. '
             '최근 갤럭시 광고 카피 중 일부입니다. 저희는 갤럭시와 함께 더 많은 소중한 순간을 담을 수 있게 되었고,'),      # 문장이 다음 장(end2)으로 이어짐
    'end2': '기기 안에는 그렇게 담아 둔 순간들이 쌓여 있습니다.',
    'end3': '갤럭시의 모든 순간이 다시 이야기가 되도록, Weave가 이어 가겠습니다.',
    'bye': '지금까지 Weave였습니다. 감사합니다.',      # 11-13 7차: 맺는 인사는 마지막 장(아이콘과 Weave 글자만)에서. 8차: 'Weave Assist였습니다' → 'Weave였습니다'
    # 제안 장표(본 발표 흐름에는 넣지 않음. 넣는다면 이렇게 말함)
    'p_fx1': ('저희 설문에서 응답자의 83.8%는 어느 앱에 남겼는지 몰라 앱을 하나씩 열어 봤다고 답했습니다. '
              '(클릭) 기록 통합 검색이 있으면, 이 83.8%는 앱을 하나씩 여는 대신 한 번의 검색으로 찾습니다.'),
    'p_fx2': ('93.8%는 정확한 이름이 떠오르지 않아 검색으로 찾지 못했습니다. '
              '(클릭) 단서로 찾는 기억이 있으면, 이름 대신 기억나는 상황만으로 찾습니다.'),
    'p_fx3': ('82.4%는 부탁이나 약속을 나중에야 떠올렸습니다. '
              '(클릭) 먼저 건네는 기억이 있으면, 떠올리기 전에 Weave가 먼저 알려 줍니다.'),
}
CUES = {
    'hub2.avg': ('hub2', 0, '3.8곳'),
    'hub2.three': ('hub2', 1, '74.8%'),
    'link.weave': ('link', 0, '하나로 엮어'),
    'link.me': ('link', 0, '오늘의 나에게'),
    'bridge.logo': ('bridge', 0, "'Weave Assist'를"),
    'bridge.weave': ('bridge', 1, '흩어진 기억의 단서들을'),
    'fx1.num': ('fx1', 0, '83.8%'),
    'fx2.num': ('fx2', 0, '93.8%'),
    'fx3.num': ('fx3', 0, '82.4%'),
    'p_fx1.num': ('p_fx1', 0, '83.8%'),
    'p_fx2.num': ('p_fx2', 0, '93.8%'),
    'p_fx3.num': ('p_fx3', 0, '82.4%'),
    'bi.weave': ('bi', 2, '하나의 기록으로'),
    # 8차: 비교 장(cmp)과 연표(tl)는 말에 맞춰 하나씩 뜨지 않고 클릭하면 곧바로 한꺼번에 뜸(발표자의 말 빠르기와 어긋나 느리게 보임) → 그 장의 때 맞춤은 없앰
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


def logo_word_w(pt, text='Weave Assist'):
    """로고 글자(Samsung Sharp Sans Bold, 자간 -0.5pt)의 폭(px). 글꼴 파일이 없으면 어림."""
    f = Path.home() / '.cache' / 'weave-tools' / 'fonts' / 'SamsungSharpSans-Bold.ttf'
    if f.exists():
        from PIL import ImageFont
        return ImageFont.truetype(str(f), 1000).getlength(text) * pt * 4 / 3 / 1000 - (len(text) - 1) * 0.5 * 4 / 3
    return tw(text, pt, 'b') * 1.1


def logo(key, x, cy, mark=58, pt=44, text='Weave Assist'):
    """표지와 같은 로고: 보라 네모 + 흰 실타래, 그 옆에 'Weave Assist'(글꼴과 그라데이션은 make.py의 logo_style이 입힘).
    돌려줌: (네모 원시 목록, 글 원시 목록, 전체 폭)."""
    ic = mark * 2 / 3
    gap = mark * 0.22
    ww = logo_word_w(pt, text)
    return ([R(key + '/mark', x, cy - mark / 2, mark, mark, prst='roundRect', radius=mark * 15 / 56, line=None,
               grad=dict(stops=[(0, '8D6BFF', None), (55, '6B4EFF', None), (100, '5A3FE0', None)], ang=55), shadow=(20, 8, '6B4EFF', 30)),
             P(key + '/icon', ICON['spool_w'], x + (mark - ic) / 2, cy - ic / 2, ic, ic)],
            [T(key + '/logo_word', x + mark + gap, cy - pt * 0.8, ww + 24, pt * 1.6, text, size=pt, color=PURPLE, weight='b', anchor='ctr',
               spc=-0.5)],
            mark + gap + ww)


# ------------------------------------------------------------------ 인트로 6쪽: 검색해도 없는 기록 → 수많은 기록 → 문구
HK_BG = '0A0A0E'
HK_HERO = (490, 36, 300, 648)                             # 큰 검색 화면. 줄어들면 벽 한가운데 칸(124×268)에 꼭 맞음
HK_SHRINK = HL.PW / HK_HERO[2]
HK_QUERY = HW.QUERY                                       # '지은이네 집들이 때 마셨던 와인'
HK_WHITE, HK_SOFT = 'F4F4F6', '9B85FF'
HK_FAIL = '검색 결과가 없습니다'


def hero_prims(key, fail):
    """큰 휴대폰 화면: 검색창에 질문이 적혀 있고, fail이면 가운데에 '검색 결과가 없습니다'.
    7쪽의 '일치하는 결과가 없습니다'와 같은 모양(연분홍 알약, 빨간 점, 빨간 굵은 글)으로, 화면 가운데의 돋보기는 두지 않는다."""
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
        pt = 17.5
        fw = tw(HK_FAIL, pt, 'b')
        pw, ph = fw + 66, 46
        px, py = x + (w - pw) / 2, y + 268
        out += [R(key + '/nb', px, py, pw, ph, prst='roundRect', fill='FDECEF', line=None),
                R(key + '/nd', px + 21, py + ph / 2 - 4.5, 9, 9, prst='ellipse', fill='E0566B', line=None),
                T(key + '/nt', px + 40, py, fw + 16, ph, HK_FAIL, size=pt, color='D6455C', weight='b', anchor='ctr')]
    return out


def s_hook():
    """검색 화면 → '검색 결과가 없습니다'(말없이) → 화면이 물러나며 수많은 앱 화면의 벽 →
    (클릭 다섯 번) "카톡 대화, 사진, 메모, 일정, 메일까지"를 하나씩 말할 때마다 그 앱의 화면 한 곳에서 세 곳에만 불이 켜지고 앞의 불은 꺼짐 →
    (클릭) 불이 꺼지고 문구. 아이콘은 불이 켜진 화면의 왼쪽 위에 붙었다가 함께 꺼진다."""
    s = Slide('hook', trans=('fade', 700), bar=False, bg=False, notes=NOTES['hook'])
    s.add('hk/bg', [R('hk/bg', 0, 0, 1280, 720, fill=HK_BG, line=None)])
    s.add('hk/wall', [P('hk/wall', str(HOOKD / 'mosaic.jpg'), 0, 0, 1280, 720)])
    by_app = {a: [] for a in HL.APPS}
    for i, (app, name, x, y) in enumerate(HL.lit()):
        k = 'hk/lit%02d' % i
        s.add(k, [P(k + '/s', str(HOOKD / 'screens' / (name + '.jpg')), x, y, HL.PW, HL.PH, radius=HL.RADIUS, shadow=(22, 0, 'FFFFFF', 26)),
                  P(k + '/ic', ICON[app], x - 11, y - 11, 34, 34, shadow=(8, 2, '000000', 45))])
        by_app[app].append(k)
    s.add('hk/veil', [R('hk/veil', 0, 0, 1280, 720, fill='050508', alpha=58, line=None)])
    s.add('hk/hero', hero_prims('hk/hero', False))
    s.add('hk/hero2', hero_prims('hk/hero2', True))
    s.add('hk/l1', [T('hk/l1', 0, 282, 1280, 66, '수많은 기억 속에서,', size=46, color=HK_WHITE, weight='b', align='c', anchor='ctr', spc=-0.6)])
    s.add('hk/l2', [T('hk/l2', 0, 352, 1280, 66, [[('지금 필요한 기억', dict(color=HK_SOFT)), ('을 찾아 헤맵니다', dict(color=HK_WHITE))]],
                      size=46, weight='b', align='c', anchor='ctr', spc=-0.6)])
    # 장이 열리면: 검색 화면 → 결과 없음(천천히, 읽을 시간) → 화면이 물러나며 벽이 드러남
    s.on('hk/hero', 'zoom_in', rt(150), rt(450), **{'from': 0.94})
    s.on('hk/hero2', 'fade_in', rt(1050), rt(700))
    s.on('hk/hero', 'fade_out', rt(1800), rt(40))
    t_out = HK_LEAD * 1000 + 150
    ease = dict(accel=35000, decel=65000)
    s.on('hk/hero2', 'zoom_out', rt(t_out), rt(950), to=HK_SHRINK, **ease)
    s.on('hk/wall', 'zoom_in', rt(t_out), rt(950), **{'from': 1 / HK_SHRINK}, **ease)
    # 클릭마다: 앞 앱의 불은 꺼지고 이번 앱의 화면(HL.LIT, 한 곳에서 세 곳)에 불
    for n, app in enumerate(HL.APPS):
        s.click()
        if n:
            for k in by_app[HL.APPS[n - 1]]:
                s.on(k, 'fade_out', 0, rt(380))
        for j, k in enumerate(by_app[app]):
            s.on(k, 'fade_in', rt(40 + j * 120), rt(420))
    s.click()      # 불이 꺼지고 문구
    for k in by_app[HL.APPS[-1]]:
        s.on(k, 'fade_out', 0, rt(480))
    s.on('hk/veil', 'fade_in', rt(120), rt(560))
    s.on('hk/l1', 'rise', rt(380), rt(620), dy=12)
    s.on('hk/l2', 'rise', rt(580), rt(620), dy=12)
    return s


# ------------------------------------------------------------------ 인트로 9쪽: 기록을 남기는 곳(설문 4번)
HB = (362, 372)                    # 둥근 줄의 가운데(11-12: 7·8쪽 고리보다 26px 오른쪽 — 오른쪽 숫자와 함께 옮겨 좌우 균형을 맞춤)
HB_R = 154                         # 앱이 놓이는 둥근 줄
HB_STAT_X = 968                    # 오른쪽 숫자 두 묶음의 가운데
HB_ITEMS = [   # (키, 이름, %, 아이콘) — 설문 4번(복수 선택), 많이 고른 순서. 위에서 시계 방향. hop/app1~4는 8쪽 오른쪽 아래의 앱 넷(모핑으로 옮겨 옴)
    ('hop/app4', '화면 캡처', 76.7, ICON['gallery']),
    ('hop/app1', '카톡 대화', 75.7, ICON['talk']),
    ('hop/app3', '메모 앱', 65.2, ICON['note']),
    ('hub2/cam', '사진 촬영', 59.5, CAMERA),
    ('hop/app2', '캘린더', 53.3, ICON['cal']),
    ('hub2/map', '지도 저장', 25.7, ICON['map']),
    ('hub2/mail', '이메일', 14.8, ICON['mail']),
]
HB_TITLE = [('검색해도 안 나오는 내 기록, ', INK), ('찾을 때까지 넘나듭니다', PURPLE)]


def hb_pos(i, r=HB_R):
    a = math.radians(-90 + i * 360 / len(HB_ITEMS))
    return HB[0] + r * math.cos(a), HB[1] + r * math.sin(a)


def hb_stat(key, y, head, pct):
    """오른쪽 숫자 한 묶음(7·8쪽 오른쪽과 같은 모양): 한 줄 설명 + 큰 %."""
    num = '%.1f' % pct
    x = HB_STAT_X - 310
    return [T(key + '/h', x, y, 620, 32, [[(t, dict(color=c)) for t, c in head]], size=18, weight='b', align='c', anchor='ctr'),
            T(key + '/n', x, y + 28, 620, 98, [[(num, dict(size=60)), ('%', dict(size=28))]], size=60, color=PURPLE, weight='b', align='c',
              anchor='ctr', spc=-1.5)]


def s_hub2():
    """8쪽에서 모핑: 오른쪽 아래의 앱 넷이 왼쪽 둥근 자리로 옮겨 가고 나머지 셋이 뜸 → 앱마다 작은 고리가 그 비율만큼 차오름 →
    가운데 '3.8곳 분산 저장' → (클릭) 두 곳 이상 91.4%, 세 곳 이상 74.8%.
    11-12: 아이콘, 고리, 글자를 반 단계씩 키움(아이콘 32 → 36, 고리 반지름 35 → 39, 비율 14.5 → 15.5pt, 이름 11 → 12pt)."""
    s = Slide('hub2', trans=('morph', 800), bar=False, notes=NOTES['hub2'])
    s.add('title', [title('title', HB_TITLE)])
    cx, cy = HB
    s.add('hub2/orbit', [R('hub2/orbit', cx - HB_R, cy - HB_R, 2 * HB_R, 2 * HB_R, prst='ellipse', fill=None, line='DCD4F6', line_w=1.3)])
    nodes, rings = [], []
    for i, (key, name, pct, icon) in enumerate(HB_ITEMS):
        x, y = hb_pos(i)
        s.add(key, [R(key + '/halo', x - 31, y - 31, 62, 62, prst='ellipse', fill='FFFFFF', line=TRACK, line_w=1.0, shadow=(14, 3, '6B4EFF', 12)),
                    P(key + '/icon', icon, x - 18, y - 18, 36, 36)])
        base, arc = ring('hub2/r%d' % i, x, y, 39, pct, k=0.066)
        s.add('hub2/r%d/t' % i, base)
        s.add('hub2/r%d/a' % i, arc)
        lx, ly = HB[0] + (HB_R + 92) * math.cos(math.radians(-90 + i * 360 / len(HB_ITEMS))), hb_pos(i, HB_R + 74)[1]   # 숫자와 이름은 고리 바깥, 옆으로는 조금 더 멀리
        s.add('hub2/l%d' % i, [T('hub2/l%d/p' % i, lx - 60, ly - 23, 120, 24, '%.1f%%' % pct, size=15.5, color=PURPLE, weight='b', align='c', anchor='ctr'),
                               T('hub2/l%d/n' % i, lx - 60, ly + 2, 120, 20, name, size=12, color=SUB, align='c', anchor='ctr')])
        nodes.append(key)
        rings.append(i)
    s.add('hub2/core', [T('hub2/core/n', cx - 90, cy - 48, 180, 62, [[('3.8', dict(size=48)), ('곳', dict(size=24))]], size=48, color=PURPLE, weight='b',
                          align='c', anchor='ctr', spc=-1),
                        T('hub2/core/t', cx - 90, cy + 16, 180, 28, '분산 저장', size=16.5, color=INK2, weight='b', align='c', anchor='ctr')])
    s.add('hub2/a', hb_stat('hub2/a', 212, [('두 곳 이상', PURPLE), ('에 나눠 저장', INK)], 91.4))
    s.add('hub2/b', hb_stat('hub2/b', 398, [('세 곳 이상', PURPLE), ('에 나눠 저장', INK)], 74.8))
    s.add('foot', [T('foot', 100, 664, 1100, 21, SURVEY_SRC, size=12, color=MUTE, anchor='ctr')])
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


# ------------------------------------------------------------------ 인트로 11~12쪽: 흩어져 있던 기록 → 하나로 이어진 기록
# 인트로 덱 10~11쪽(이어져 있다가 흩어짐)의 차례를 뒤집어 다시 그린 것. 조각, '지금의 나', 선의 모양과 색은 그 장의 값 그대로.
RC_ME = {'scat': (896, 364), 'link': (640, 364)}        # '지금의 나'의 가운데: 11쪽은 오른쪽, 12쪽은 화면 가운데
RC_CARDS = [   # (키, 앱, 꼬리표, 글, 글 크기, 폭, 반듯할 때 '지금의 나'에서 왼쪽 위까지 (dx, dy), 흩어졌을 때 더 밀려난 만큼과 기울기 (dx, dy, 도))
    ('rec1', 'talk', '민수', '최종본은 메일로 보내드릴게요', 11, 272.5, (-291.5, -117), (-34, -32, -4.0)),
    ('rec2', 'cal', '11월 19일', '삼성 기술전 시연', 12, 240, (19, -117), (30, -20, 3.0)),
    ('rec3', 'note', '주간 회의', '시연 순서', 12, 272.5, (-291.5, 75), (-22, 26, 3.5)),
    ('rec4', 'mail', '11월 19일', '최종본 공유 메일', 12, 240, (19, 75), (36, 34, -4.5)),
]
RC_APPS = [    # 옅게 떠 있는 앱 아이콘: (키, 앱, 반듯할 때 (dx, dy), 흩어졌을 때 더 (dx, dy))
    ('fapp1', 'mail', (-281.5, -43), (-38, -14)), ('fapp2', 'gallery', (-281.5, 3), (-20, 24)),
    ('fapp3', 'map', (219, -43), (34, -20)), ('fapp4', 'talk', (219, 3), (44, 18)),
]
RC_OUTER = [   # 기록끼리 잇는 선(위, 오른쪽, 아래, 왼쪽): (키, 시작, 끝, 닦아 내는 쪽)
    ('lk/top', (-13, -100), (13, -100), 'left'), ('lk/right', (139, -77), (139, 69), 'down'),
    ('lk/bot', (-13, 92), (13, 92), 'right'), ('lk/left', (-155, -77), (-155, 69), 'up'),
]
RC_INNER = [   # 기록에서 '지금의 나'로 오는 선: (키, 기록 쪽, 나 쪽, 닦아 내는 쪽)
    ('lk/d1', (-119, -77), (-37, -25), 'left'), ('lk/d2', (119, -77), (37, -25), 'right'),
    ('lk/d3', (116.6, 69), (37.7, 21.6), 'right'), ('lk/d4', (-116.6, 69), (-37.7, 21.6), 'left'),
]


def rc_card(key, kind, tag, text, pt, w, x, y):
    """기록 조각 하나: 흰 알약 + 앱 아이콘 + 보라 꼬리표 + 한 줄."""
    tg = tw(tag, 10.5, 'b') + 16
    return [R(key + '/bg', x, y, w, 34, prst='roundRect', fill='FFFFFF', alpha=88, line='E4DDF7', line_w=1.0, shadow=(6, 2, '6B5CB0', 8)),
            P(key + '/ic', ICON[kind], x + 9, y + 7, 20, 20, alpha=80),
            R(key + '/tag', x + 37, y + 7, tg, 20, prst='roundRect', radius=6, fill='F1EDFF', line=None),
            T(key + '/tagt', x + 37, y + 7, tg, 20, tag, size=10.5, color=PURPLE, weight='b', align='c', anchor='ctr'),
            T(key + '/t', x + 37 + tg + 7, y, w - (37 + tg + 7) - 8, 34, text, size=pt, color=BODY, anchor='ctr')]


def rc_me(mx, my):
    return [R('me/halo', mx - 46, my - 46, 92, 92, prst='ellipse', fill='FFFFFF', alpha=55, line=None),
            R('me/node', mx - 31, my - 31, 62, 62, prst='ellipse', fill='FFFFFF', line=PURPLE, line_w=2.33, shadow=(10, 3, '6B4EFF', 18)),
            R('me/head', mx - 5.3, my - 13, 10.6, 10.6, prst='ellipse', fill=PURPLE, line=None),
            R('me/body', mx - 9.8, my - 0.4, 19.6, 15, prst='roundRect', radius=6.3, fill=PURPLE, line=None),
            T('me/label', mx - 60, my + 36, 120, 22, '지금의 나', size=13, color=PURPLE, weight='b', align='c', anchor='ctr')]


def rc_draw(s, key, scattered):
    """기록 넷, 옅은 앱 넷, '지금의 나'를 그린다. scattered면 조각이 바깥으로 밀려나 기울어 있다. 돌려줌: (조각 키, 앱 키)."""
    mx, my = RC_ME[key]
    for k, app, (dx, dy), (sx, sy) in RC_APPS:
        x, y = mx + dx + (sx if scattered else 0), my + dy + (sy if scattered else 0)
        s.add(k, [P(k, ICON[app], x, y, 30, 30, alpha=42)])
    if not scattered:
        for k, a, b, _ in RC_OUTER + RC_INNER:
            p0, p1 = (mx + a[0], my + a[1]), (mx + b[0], my + b[1])
            s.add(k, [C(k, [p0, p0, p1, p1], w=1.87, color=PURPLE2, alpha=85)])
    for k, app, tag, text, pt, w, (dx, dy), (sx, sy, rot) in RC_CARDS:
        x, y = mx + dx + (sx if scattered else 0), my + dy + (sy if scattered else 0)
        s.add(k, rc_card(k, app, tag, text, pt, w, x, y), rot=rot if scattered else None)
    s.add('me', rc_me(mx, my))
    return [c[0] for c in RC_CARDS], [a[0] for a in RC_APPS]


def s_scat():
    """11쪽: 왼쪽에 물음, 오른쪽에 '지금의 나'와 그 둘레에 흩어져 있는 기록들(선 없음)."""
    s = Slide('scat', trans=('morph', 1000), bar=False, notes=NOTES['scat'])
    recs, apps = rc_draw(s, 'scat', True)
    s.add('cap8/2', [T('cap8/2', 118.5, 306.7, 413, 107, [[('정작 내 기록은', dict(color=INK))], [('왜 아직도 찾아 헤맬까요?', dict(color=PURPLE))]],
                       size=30, weight='b', lnspc=40)])
    s.on('me', 'zoom_in', rt(100), rt(220), **{'from': 0.8})
    s.on('cap8/2', 'rise', rt(250), rt(384), dy=12)
    for i, k in enumerate(recs):
        s.on(k, 'rise', rt(450 + i * 110), rt(336), dy=10)
    for i, k in enumerate(apps):
        s.on(k, 'fade_in', rt(900 + i * 60), rt(400))
    return s


def s_link():
    """12쪽: 흩어져 있던 기록이 가운데로 모이며 반듯해지고(모핑), "하나로 엮어"에 기록끼리, "오늘의 나에게"에 '지금의 나'까지 선이 이어진다."""
    s = Slide('link', trans=('morph', 1000), bar=False, notes=NOTES['link'])
    rc_draw(s, 'link', False)
    t1 = max(cue('link.weave', 2300, ahead=0.35), 500)
    for i, (k, _, _, d) in enumerate(RC_OUTER):
        s.on(k, 'wipe_in', t1 + i * 150, 340, dir=d)
    t2 = max(cue('link.me', 4300, ahead=0.3), t1 + 4 * 150 + 400)
    for i, (k, _, _, d) in enumerate(RC_INNER):
        s.on(k, 'wipe_in', t2 + i * 80, 360, dir=d)
    s.on('me', 'pulse', t2 + 520, 180, scale=1.08)
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
BR_C0, BR_C1 = (0xA5, 0x86, 0xFF), (0x5E, 0x40, 0xF5)       # 실의 왼쪽 끝과 오른쪽 끝 색
BR_W = 5.6                                                  # 실 굵기(11-12: 3.4 → 5.6, 표지와 모션그래픽의 실처럼 흰 테두리를 받침)


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
    for i, (key, pts, stops) in enumerate(th):
        under = [(0, 'FFFFFF', 0 if i == 0 else 90), (100, 'FFFFFF', 90)]
        s.add(key, [C(key + '/u', pts, w=BR_W + 4.4, stops=under), C(key, pts, w=BR_W, stops=stops)])
    s.add('br/star', star4_icon('br/star', end[0] + 17, end[1], r=12, color='5E40F5'))
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
FX_CX, FX_CY, FX_RO = 262, 398, 106
FX_LY = 202                        # (2)(3)의 이름표: 왼쪽 불편 문장의 둘째 줄과 같은 높이. 그 아래 화면은 왼쪽 고리의 위 끝(292)에서 시작
FX = {      # 장 키: (번호, 불편(두 줄), %, 명, 기능 이름, UX 묶음, 묶음 자리, 이름표 (x, y), 기능이 있으면(두 줄, 제안 장표에서만))
    'fx1': (1, ['어느 앱인지 몰라', '앱을 하나씩 열어 봤어요'], 83.8, 176, '기록 통합 검색', 'ux1', Xf(40, 218, 628, 196, 0.98), (630, 150),
            ['어느 앱인지 몰라도', '한 번의 검색으로 찾아요']),          # 이름표의 왼쪽 끝을 아래 화면(기록 카드)의 왼쪽 끝에 맞춤
    'fx2': (2, ['정확한 이름이 떠오르지 않아', '검색으로 찾지 못했어요'], 93.8, 197, '단서로 찾는 기억', 'ux2', Xf(640, 218, 566, 292, 1.12), (566, FX_LY),
            ['정확한 이름이 떠오르지 않아도', '기억나는 상황으로 찾아요']),
    'fx3': (3, ['챙겨야 할 부탁, 약속을', '나중에야 떠올렸어요'], 82.4, 173, '먼저 건네는 기억', 'ux3', Xf(640, 492, 566, 292, 1.12), (566, FX_LY),
            ['챙겨야 할 부탁, 약속을', 'Weave가 먼저 알려 줘요']),
}


def s_fx(key, first=False, effect=False):
    """기대효과 한 장: 왼쪽에 설문의 불편(말 + 고리 그래프), (클릭) 오른쪽에 그 불편에 답하는 기능과 화면.
    effect=True(제안 장표 p_fx*): 고리가 처음에는 짙은 색(불편을 겪은 사람)이고, 클릭하면 보라가 그 위를 덮으며 왼쪽 말이 '기능이 있으면'으로 바뀐다.
    숫자는 설문 값 그대로 두고 뜻만 바뀐다(불편을 겪은 83.8% → Weave가 돕는 83.8%)."""
    n, stmt, pct, cnt, name, ux, xf, (lx, ly), after = FX[key]
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
    s.add('fx/src', [foot('fx/src', SURVEY_SRC)])
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
# 11-13 6차에 기록을 남기는 앱이 아닌 다섯(음악, 비디오, 스토어, PENUP, 시계)을 빼서 14개(4·6·4)로 했다가,
# 7차에 5차까지 쓰던 묶음으로 되돌림(19개, 6·7·6. '예전 것이 오밀조밀해서 더 낫다').
# 7차 뒤(11-13): 아이콘 그림과 앱 차례를 팀원 덱(SB-Jo/t3 weave/결선준비/outro/weave_outro_bimpact.pptx)의 왼쪽 묶음 그대로. 자리와 크기는 같고 그림만 실제 앱 아이콘 19개로 바뀜
# (캘린더, 음악, 비디오, 이메일, 지도, PENUP 자리에 리마인더, 연락처, 계산기, 설정, 내 파일, 날씨). 그림은 assets/outro/app-*.png
BI_APPS = ['gallery', 'messages', 'kakao', 'camera', 'reminder', 'contacts', 'calculator', 'notes', 'store', 'settings', 'health', 'myfiles', 'cloud',
           'wallet', 'phone', 'internet', 'weather', 'recorder', 'clock']
BI_ROWS = (6, 7, 6)
BI_NAME_PT = 14                                             # 휴대폰 안 Weave 동그라미 아래의 'Weave Assist'(7차)
BI_LX, BI_RX = 252, 1028                                    # 왼쪽 묶음 가운데, 오른쪽 묶음 가운데
BI_PH = (640 - 113, 168, 226, 388)                          # 가운데 휴대폰(몸통 상자)
BI_WV = (640, 352, 42)                                      # 휴대폰 안의 Weave 동그라미: 가운데 x, y, 반지름
BI_RINGS = (2.4, 3.4, 4.4)                                  # 빛이 퍼질 때의 고리 셋: 다 퍼졌을 때의 크기(동그라미의 몇 배)
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


def bi_phone(key):
    """흰 화면의 휴대폰(틀, 화면, 카메라 구멍, 아래 단추 셋). 화면 안에는 아무 글도 두지 않는다."""
    x, y, w, h = BI_PH
    cx, g = x + w / 2, 'A9A6BA'
    ny = y + h - 24
    return [R(key + '/frame', x, y, w, h, prst='roundRect', radius=38, line='FFFFFF', line_w=1.2, shadow=(34, 14, '5B3FE6', 20),
              grad=dict(stops=[(0, 'D5D8EC', None), (100, 'B7BBD8', None)], ang=60)),
            R(key + '/screen', x + 7, y + 7, w - 14, h - 14, prst='roundRect', radius=31, fill='FFFFFF', line=None),
            R(key + '/cam', cx - 4.5, y + 18, 9, 9, prst='ellipse', fill='23212B', line=None),
            R(key + '/n1a', cx - 52, ny, 1.6, 10, fill=g, line=None), R(key + '/n1b', cx - 48, ny, 1.6, 10, fill=g, line=None),
            R(key + '/n1c', cx - 44, ny, 1.6, 10, fill=g, line=None),
            R(key + '/n2', cx - 5.5, ny - 0.5, 11, 11, prst='roundRect', radius=3, fill=None, line=g, line_w=1.6),
            C(key + '/n3a', [(cx + 49, ny)] * 2 + [(cx + 44, ny + 5)] * 2, color=g, w=1.6),
            C(key + '/n3b', [(cx + 44, ny + 5)] * 2 + [(cx + 49, ny + 10)] * 2, color=g, w=1.6)]


def s_bi():
    """41개 앱에 흩어진 기록 → (클릭) 지우지 않고 쌓이는 기록 → (클릭) 흰 화면의 갤럭시가 뜨고, 양쪽에서 실이 화면 속 Weave 동그라미로 이어지면
    동그라미가 보라로 켜지며 고리 셋과 작은 별이 둥글게 퍼진다(모션그래픽에서 기록이 실타래 버튼에 닿을 때처럼)."""
    s = Slide('bi', trans=('fade', 500), bar=False, notes=NOTES['bi'])
    s.add('bi/title', [title('bi/title', [('쓸수록 쌓여, ', INK), ('갤럭시를 떠나기 어려워집니다', PURPLE)])])
    # 왼쪽: 앱 19개(6·7·6), 44px을 54px 간격으로
    apps, sz, gx, gy = [], 44, 54, 54
    cuts = [sum(BI_ROWS[:i]) for i in range(len(BI_ROWS) + 1)]
    rows = [BI_APPS[a:b] for a, b in zip(cuts, cuts[1:])]
    assert sum(BI_ROWS) == len(BI_APPS)
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
    # 가운데: 갤럭시(흰 화면) 안의 Weave 동그라미
    cx, cy, r = BI_WV
    px = BI_PH[0]
    s.add('bi/glow', [R('bi/glow', cx - 250, cy - 250, 500, 500, prst='ellipse', fill=None, line=None,
                        grad=dict(stops=[(0, '8B6BFF', 34), (50, 'B9A6FF', 14), (100, 'F2EDFF', 0)], path='circle'))])
    s.add('bi/phone', bi_phone('bi/phone'))
    s.add('bi/halo', [R('bi/halo', cx - 96, cy - 96, 192, 192, prst='ellipse', fill=None, line=None,
                        grad=dict(stops=[(0, '8B6BFF', 46), (55, 'B9A6FF', 18), (100, 'FFFFFF', 0)], path='circle'))])
    s.add('bi/thl', [C('bi/thl', [(BI_LX + 172, cy)] * 2 + [(cx - r - 3, cy)] * 2, w=3.2)])
    s.add('bi/thr', [C('bi/thr', [(BI_RX - 172, cy)] * 2 + [(cx + r + 3, cy)] * 2, w=3.2)])
    for i, d in enumerate(BI_RINGS):                       # 퍼져 나가는 고리 셋(잠깐만 보임)
        s.add('bi/rg%d' % i, [R('bi/rg%d' % i, cx - r * d, cy - r * d, 2 * r * d, 2 * r * d, prst='ellipse', fill=None, line=PURPLE2, line_w=3.0,
                                line_alpha=85)], temp=True)
    s.add('bi/wv', [R('bi/wv/c', cx - r, cy - r, 2 * r, 2 * r, prst='ellipse', fill='E6DEFF', line=None),
                    P('bi/wv/sp', ICON['spool'], cx - 23, cy - 23, 46, 46)])
    s.add('bi/wv_on', [R('bi/wv_on/c', cx - r, cy - r, 2 * r, 2 * r, prst='ellipse', line=None, shadow=(22, 6, '6B4EFF', 46),
                         grad=dict(stops=[(0, '8D6BFF', None), (55, '6B4EFF', None), (100, '5A3FE0', None)], ang=55)),
                       P('bi/wv_on/sp', ICON['spool_w'], cx - 23, cy - 23, 46, 46)])
    ny = cy + r + 11                                        # 동그라미 아래 이름: 불이 켜지기 전에는 옅게, 켜지면 보라
    name = lambda k, col: [T(k, cx - 80, ny, 160, 24, 'Weave Assist', size=BI_NAME_PT, color=col, weight='b', align='c', anchor='ctr')]
    s.add('bi/wvn', name('bi/wvn', 'C3B8EE'))
    s.add('bi/wvn_on', name('bi/wvn_on', PURPLE))
    sparks = [(-62, -50, 10), (66, -40, 7.5), (58, 56, 9), (-54, 60, 7)]
    for i, (dx, dy, sr) in enumerate(sparks):               # 반짝이는 작은 별(잠깐만 보임)
        s.add('bi/sk%d' % i, star4_icon('bi/sk%d' % i, cx + dx, cy + dy, r=sr, color=PURPLE2), temp=True)
    s.add('bi/src', [foot('bi/src', BI_SRC, pt=9)])
    # 장이 열리면: 앱이 모이고 41개
    s.on('bi/apps', 'zoom_in', 200, 520, **{'from': 0.86})
    s.on('bi/l', 'rise', 520, 520, dy=12)
    s.click()      # 1: 지우지 않고 쌓이는 기록
    s.on('bi/pie', 'fade_in', 0, 300)
    s.on('bi/arc', 'wheel_in', 150, 850)
    s.on('bi/r', 'rise', 420, 520, dy=12)
    s.click()      # 2: 갤럭시가 뜨고 → 양쪽 기록이 Weave로 이어짐 → 동그라미가 켜지며 빛이 퍼짐
    s.on(['bi/phone', 'bi/wv', 'bi/wvn'], 'rise', 0, 560, dy=16)
    tt = max(cue('bi.weave', 3000, ahead=0.5), 760)
    s.on('bi/thl', 'wipe_in', tt, 440, dir='left')
    s.on('bi/thr', 'wipe_in', tt, 440, dir='right')
    on = tt + 440
    s.on(['bi/wv_on', 'bi/wvn_on'], 'fade_in', on, 280)
    s.on(['bi/halo', 'bi/glow'], 'fade_in', on, 600)
    for i, d in enumerate(BI_RINGS):
        s.on('bi/rg%d' % i, 'jump', on + i * 260)
        s.on('bi/rg%d' % i, 'ring', on + i * 260, 1300, **{'from': 1 / d, 'to': 1.0})
    for i in range(len(sparks)):
        s.on('bi/sk%d' % i, 'jump', on + 120 + i * 110)
        s.on('bi/sk%d' % i, 'zoom_in', on + 120 + i * 110, 260, **{'from': 0.3})
        s.on('bi/sk%d' % i, 'fade_out', on + 560 + i * 110, 420)
    s.on(['bi/wv', 'bi/wv_on'], 'pulse', on + 60, 190, scale=1.1)
    return s


# ------------------------------------------------------------------ 뒷부분 3: 기존 기능과의 비교
# 11-12 4차: 표(네 칸 × 세 줄)를 두 축의 지도로. 가로 = 찾는 범위(앱 하나 → 여러 앱), 세로 = 찾는 방식(한 번 → 단서를 이어 여러 단계).
# 기존 기능 넷(Writing Assist, 카나나, Now Nudge, Finder)은 아래쪽에, Weave는 오른쪽 위. 화면의 글은 축과 이름뿐이고 설명은 발표자가 말한다.
# 3차의 표는 덱 뒤 '이전 판 (3차)'에 남아 있다.
MAP_O = (300, 588)                  # 두 축이 만나는 점
MAP_XE, MAP_YT = 1096, 168          # 가로축의 오른쪽 끝, 세로축의 위 끝
MAP_Y1, MAP_YN = 488, 262           # '한 번'의 높이, '여러 단계'의 높이
MAP_X = [436, 622, 808, 994]        # 쓰는 글, 앱 하나, (그 사이), 여러 앱
MAP_PTS = [   # (키, 아이콘 종류, 이름, 가운데 x) — 왼쪽에서 오른쪽으로 범위가 넓어짐. 넷 모두 '한 번' 줄
    ('wa', 'writing', 'Writing Assist', MAP_X[0]),      # 지금 쓰는 글만 다듬음
    ('kanana', 'kanana', '카나나', MAP_X[1]),            # 카카오톡 대화 안에서
    ('nudge', 'nudge', 'Now Nudge', MAP_X[2]),          # 갤러리 사진, 예약 정보 등
    ('finder', 'finder', 'Finder', MAP_X[3]),           # 선택한 여러 앱의 기록
]
MAP_AX = 'B4ACC9'                   # 축의 색
CMP_SRC = '* Samsung 지원 페이지(Finder, Writing Assist), Samsung Newsroom(Galaxy S26, 2026. 2), 카카오 발표(2026. 3)의 공식 설명을 바탕으로 배치함'


def cmp_icon(key, kind, cx, cy, z=38):
    """기능의 작은 그림(z px 칸). 기능마다 색을 달리한다: Finder 파랑, Now Nudge 청록, Writing Assist 주황, 카나나는 카카오톡 아이콘, Weave 보라."""
    k = z / 38
    tile = lambda a, b: R(key + '/tile', cx - z / 2, cy - z / 2, z, z, prst='roundRect', radius=11 * k, line=None,
                          grad=dict(stops=[(0, a, None), (100, b, None)], ang=55))
    if kind == 'finder':
        r = 7.5 * k
        return [tile('5B9BFF', '2F6BE6'),
                R(key + '/c', cx - r - 2 * k, cy - r - 2 * k, 2 * r, 2 * r, prst='ellipse', fill=None, line='FFFFFF', line_w=2.4 * k),
                C(key + '/h', [(cx + 3.6 * k, cy + 3.6 * k)] * 2 + [(cx + 9.5 * k, cy + 9.5 * k)] * 2, color='FFFFFF', w=2.6 * k)]
    if kind == 'nudge':
        return [tile('2CC4B5', '1F8FD6')] + spark_icon(key + '/s', cx - 12 * k, cy - 12 * k, size=24 * k, color='FFFFFF')
    if kind == 'writing':           # 연필(굵은 사선과 뾰족한 끝) + 작은 별
        return ([tile('FF9E70', 'F26B3A'),
                 C(key + '/p', [(cx - 4.5 * k, cy + 5.5 * k)] * 2 + [(cx + 6 * k, cy - 5 * k)] * 2, color='FFFFFF', w=4.6 * k),
                 C(key + '/t', [(cx - 9 * k, cy + 10 * k)] * 2 + [(cx - 6.5 * k, cy + 7.5 * k)] * 2, color='FFFFFF', w=2.2 * k)] +
                spark_icon(key + '/s', cx - 13 * k, cy - 14 * k, size=13 * k, color='FFFFFF'))
    if kind == 'kanana':
        return [P(key + '/k', ICON['talk'], cx - z / 2, cy - z / 2, z, z)]
    s_ = 24 * k
    return [tile('8D6BFF', '5A3FE0'), P(key + '/sp', ICON['spool_w'], cx - s_ / 2, cy - s_ / 2, s_, s_)]


def map_point(key, kind, name, cx, cy, z=46):
    """지도 위의 한 점: 아이콘 + 그 아래 이름."""
    return cmp_icon(key + '/ic', kind, cx, cy, z) + [
        T(key + '/name', cx - 100, cy + z / 2 + 5, 200, 22, name, size=13.5, color=INK2, weight='b', align='c', anchor='ctr')]


def s_cmp():
    """두 축 위에 기존 기능 넷을 놓고(말하는 차례대로 뜸), (클릭) 오른쪽 위에 Weave가 뜬다."""
    s = Slide('cmp', trans=('fade', 500), bar=False, notes=NOTES['cmp'])
    s.add('cmp/title', [title('cmp/title', [('한 번의 검색을 넘어, ', INK), ('단서를 이어 찾는 검색', PURPLE), ('으로', INK)])])
    ox, oy = MAP_O
    s.add('cmp/axx', [C('cmp/axx', [(ox, oy)] * 2 + [(MAP_XE, oy)] * 2, color=MAP_AX, w=1.8, tail='triangle')])
    s.add('cmp/axy', [C('cmp/axy', [(ox, oy)] * 2 + [(ox, MAP_YT)] * 2, color=MAP_AX, w=1.8, tail='triangle')])
    lab = lambda k, x, y, w, t, **o: T('cmp/' + k, x, y, w, 24, t, anchor='ctr', **o)
    s.add('cmp/axl', [
        # 가로: 찾는 범위(축 이름은 화살표 끝에)
        lab('xn', MAP_XE + 10, oy - 12, 120, '찾는 범위', size=13.5, color=SUB, weight='b'),
        lab('x0', MAP_X[0] - 80, oy + 12, 160, '쓰는 글', size=12.5, color=MUTE, align='c'),
        lab('x1', MAP_X[1] - 80, oy + 12, 160, '앱 하나', size=12.5, color=MUTE, align='c'),
        lab('x2', MAP_X[3] - 80, oy + 12, 160, '여러 앱', size=12.5, color=PURPLE, weight='b', align='c'),
        # 세로: 찾는 방식
        lab('yn', ox - 80, MAP_YT - 34, 160, '찾는 방식', size=13.5, color=SUB, weight='b', align='c'),
        lab('y1', ox - 176, MAP_Y1 - 12, 160, '한 번', size=12.5, color=MUTE, align='r'),
        lab('y2', ox - 176, MAP_YN - 12, 160, '여러 단계', size=12.5, color=PURPLE, weight='b', align='r'),
        # 두 높이를 잇는 옅은 점선
        C('cmp/g1', [(ox + 8, MAP_Y1)] * 2 + [(MAP_XE - 30, MAP_Y1)] * 2, color='E2DBF5', w=1.2, dash='dash'),
        C('cmp/g2', [(ox + 8, MAP_YN)] * 2 + [(MAP_XE - 30, MAP_YN)] * 2, color='E2DBF5', w=1.2, dash='dash'),
    ])
    for k, kind, name, cx in MAP_PTS:
        s.add('cmp/' + k, map_point('cmp/' + k, kind, name, cx, MAP_Y1))
    wx, wy = MAP_X[3], MAP_YN
    s.add('cmp/wglow', [R('cmp/wglow', wx - 120, wy - 112, 240, 240, prst='ellipse', fill=None, line=None,
                          grad=dict(stops=[(0, '8B6BFF', 40), (55, 'B9A6FF', 15), (100, 'F2EDFF', 0)], path='circle'))])
    s.add('cmp/up', thread('cmp/up', [(wx, MAP_Y1 - 34)] * 2 + [(wx, wy + 74)] * 2, w=2.6, tail='triangle'))
    z = 66
    s.add('cmp/weave', [R('cmp/weave/tile', wx - z / 2, wy - z / 2, z, z, prst='roundRect', radius=19, line='FFFFFF', line_w=2.5,
                          shadow=(18, 6, '6B4EFF', 30), grad=dict(stops=[(0, '8D6BFF', None), (100, '5A3FE0', None)], ang=55)),
                        P('cmp/weave/sp', ICON['spool_w'], wx - 20, wy - 20, 40, 40),
                        T('cmp/weave/name', wx - 110, wy + z / 2 + 6, 220, 28, 'Weave Assist', size=17, color=PURPLE, weight='b', align='c',
                          anchor='ctr')])
    s.add('cmp/src', [foot('cmp/src', CMP_SRC)])
    s.on('cmp/axx', 'wipe_in', 150, 600)
    s.on('cmp/axy', 'wipe_in', 150, 600, dir='up')
    s.on('cmp/axl', 'fade_in', 600, 450)
    # 기존 기능은 이름을 말할 때 하나씩(Now Nudge와 Finder는 한 문장에 이어 나와 바로 뒤따름)
    t_wa, t_kn, t_nn = cue('cmp.wa', 3300, ahead=0.2), cue('cmp.kn', 5600, ahead=0.2), cue('cmp.nn', 7700, ahead=0.2)
    s.on('cmp/wa', 'zoom_in', t_wa, 380, **{'from': 0.6})
    s.on('cmp/kanana', 'zoom_in', t_kn, 380, **{'from': 0.6})
    s.on('cmp/nudge', 'zoom_in', t_nn, 380, **{'from': 0.6})
    s.on('cmp/finder', 'zoom_in', t_nn + 620, 380, **{'from': 0.6})
    s.click()      # 1: 한 번을 넘어 위로 → Weave
    s.on('cmp/up', 'wipe_in', 0, 520, dir='up')
    s.on('cmp/wglow', 'fade_in', 300, 500)
    s.on('cmp/weave', 'zoom_in', 420, 420, **{'from': 0.6})
    s.on('cmp/weave', 'pulse', 880, 180, scale=1.08)
    return s


# ------------------------------------------------------------------ 뒷부분 4: Why Now · Why Samsung 연표
# 위는 기술, 아래는 갤럭시. 두 줄이 회색에서 보라로 짙어지며 오른쪽 끝의 Weave에서 만난다(11-12: 2차의 제안 장표 모양을 본 발표로).
# 이름표(WHY NOW, WHY SAMSUNG)는 줄 왼쪽 바깥에, 마디마다 아이콘. 기술 줄의 마지막 마디는 2026년 AgentIR · Hi-Q.
TL_YU, TL_YL, TL_YC = 318, 454, 386            # 위 줄, 아래 줄, 두 줄이 만나는 높이
TL_X0, TL_X1, TL_WX = 206, 1034, 1140          # 줄이 시작하는 곳, 곧게 가는 끝, Weave 마디
TL_NOW = 700                                   # 이보다 오른쪽 마디는 보라(최근), 왼쪽은 회색
TL_UP = [    # (x, 해, 한마디, 근거, 아이콘)
    (420, '2019', '뜻으로 찾기', 'Sentence-BERT¹', 'ic-sbert.png'),
    (556, '2020', '찾아서 답하기', 'RAG²', 'ic-rag.png'),
    (846, '2025', '추론하며 찾기', 'ReasonIR³', 'ic-reason.png'),
    (982, '2026', '단서를 잇는 검색', 'AgentIR · Hi-Q⁴', 'ic-hop.png'),
]
TL_DN = [
    (270, '2010', '키보드와 기기', 'Galaxy · Keyboard⁵', 'ic-keyboard.png'),
    (420, '2019', '온디바이스 AI 연산', 'NPU · Galaxy S10⁶', 'ic-npu.png'),      # 11-13 7차: '기기 안 AI 연산'에서(대본도 '온디바이스 AI 연산을 위한 NPU')
    (706, '2024', 'Galaxy AI 등장', 'Galaxy S24⁷', 'ic-galaxyai.png'),
    (846, '2025', '개인 데이터 엔진', 'PDE · Galaxy S25⁸', 'ic-pde.png'),
]
TL_SRC = ('* ¹ Reimers & Gurevych, "Sentence-BERT" (EMNLP 2019)   ² Lewis 외, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (NeurIPS 2020)   '
          '³ Shao 외, "ReasonIR" (COLM 2025)   ⁴ Chen 외, "AgentIR" (arXiv 2603.04384), Kim 외, "Hi-Q" (NeurIPS 2026)   '
          '⁵ ⁶ ⁷ ⁸ Samsung Newsroom: Galaxy S (2010), Exynos 9820 NPU (2018. 11), Galaxy S24 · Galaxy AI (2024. 01), Galaxy S25 · Personal Data Engine (2025. 01)')
TL_STOPS = [(0, 'DAD4E8', None), (48, 'C3B4F5', None), (100, '6B4EFF', None)]


def tl_node(key, x, y, up, year, word, ref, icon):
    new = x >= TL_NOW
    out = [R(key + '/dot', x - 8, y - 8, 16, 16, prst='ellipse', fill='FFFFFF', line=PURPLE if new else 'B9B2C9', line_w=3)]
    ys = (y - 96, y - 68, y - 44, y - 138) if up else (y + 22, y + 50, y + 74, y + 104)
    out += [T(key + '/y', x - 60, ys[0], 120, 26, year, size=15, color=PURPLE if new else SUB, weight='b', align='c', anchor='ctr'),
            T(key + '/w', x - 84, ys[1], 168, 24, word, size=14.5, color=INK, weight='b', align='c', anchor='ctr'),
            T(key + '/r', x - 84, ys[2], 168, 20, ref, size=10.5, color=MUTE, align='c', anchor='ctr'),
            P(key + '/ic', str(OUTRO / icon), x - 17, ys[3], 34, 34)]
    return out


def tl_label(key, y, en, ko):
    return [T(key + '/a', 60, y - 23, 136, 18, en, size=10, color=PURPLE, weight='b', spc=1.2),
            T(key + '/b', 60, y - 3, 136, 26, ko, size=15, color=INK, weight='b')]


def s_tl():
    """두 줄(위 = 기술, 아래 = 갤럭시) → (클릭) 기술 → (클릭) 갤럭시 → (클릭) 두 줄이 Weave에서 만남.
    11-13 8차: 마디가 말하는 차례대로 하나씩 뜨던 것을, 클릭하면 그 줄의 마디 넷(아이콘, 해, 한마디, 근거)이 곧바로 한꺼번에 뜨게."""
    s = Slide('tl', trans=('fade', 500), bar=False, notes=NOTES['tl'])
    s.add('tl/title', [title('tl/title', [('갤럭시라서', PURPLE), (', 그리고 ', INK), ('지금이라서', PURPLE), (' 되는 Weave', INK)])])
    s.add('tl/lu', [C('tl/lu', [(TL_X0, TL_YU)] * 2 + [(TL_X1, TL_YU)] * 2, stops=TL_STOPS, w=3)])
    s.add('tl/ll', [C('tl/ll', [(TL_X0, TL_YL)] * 2 + [(TL_X1, TL_YL)] * 2, stops=TL_STOPS, w=3)])
    ex = TL_WX - 30
    s.add('tl/ju', [C('tl/ju', [(TL_X1, TL_YU), (TL_X1 + 44, TL_YU), (ex - 44, TL_YC), (ex, TL_YC)], w=3, color=PURPLE)])
    s.add('tl/jl', [C('tl/jl', [(TL_X1, TL_YL), (TL_X1 + 44, TL_YL), (ex - 44, TL_YC), (ex, TL_YC)], w=3, color=PURPLE)])
    s.add('tl/now', tl_label('tl/now', TL_YU, 'WHY NOW', '지금이라서'))
    s.add('tl/sam', tl_label('tl/sam', TL_YL, 'WHY SAMSUNG', '갤럭시라서'))
    ups, dns = [], []
    for x, year, word, ref, icon in TL_UP:
        k = 'tl/u%d' % x
        s.add(k, tl_node(k, x, TL_YU, True, year, word, ref, icon))
        ups.append(k)
    for x, year, word, ref, icon in TL_DN:
        k = 'tl/d%d' % x
        s.add(k, tl_node(k, x, TL_YL, False, year, word, ref, icon))
        dns.append(k)
    wx = TL_WX
    s.add('tl/wglow', [R('tl/wglow', wx - 56, TL_YC - 56, 112, 112, prst='ellipse', fill=None, line=None,
                         grad=dict(stops=[(0, '8B6BFF', 46), (60, 'B9A6FF', 16), (100, 'F2EDFF', 0)], path='circle'))])
    s.add('tl/w', [R('tl/w/c', wx - 30, TL_YC - 30, 60, 60, prst='ellipse', line='FFFFFF', line_w=2.5, shadow=(18, 6, '6B4EFF', 30),
                     grad=dict(stops=[(0, '8D6BFF', None), (100, '5A3FE0', None)], ang=55)),
                   P('tl/w/sp', ICON['spool_w'], wx - 17, TL_YC - 17, 34, 34),
                   T('tl/w/n', wx - 70, TL_YC + 38, 140, 28, 'Weave', size=17, color=PURPLE, weight='b', align='c', anchor='ctr')])
    s.add('tl/src', [T('tl/src', 60, 648, 1160, 44, TL_SRC, size=9, color=MUTE, wrap=True, lnspc=13)])
    s.on(['tl/now', 'tl/sam'], 'fade_in', 150, 400)
    s.on(['tl/lu', 'tl/ll'], 'wipe_in', 350, 900)
    s.click()      # 1: 기술(위) — 2019 ~ 2026 마디 넷이 클릭하자마자 한꺼번에
    s.on(ups, 'rise', 0, 460, dy=-12)
    s.click()      # 2: 갤럭시(아래) — 2010 ~ 2025 마디 넷이 한꺼번에
    s.on(dns, 'rise', 0, 460, dy=12)
    s.click()      # 3: 두 줄이 Weave에서 만남
    s.on(['tl/ju', 'tl/jl'], 'wipe_in', 0, 520)
    s.on('tl/wglow', 'fade_in', 420, 500)
    s.on('tl/w', 'zoom_in', 480, 420, **{'from': 0.6})
    s.on('tl/w', 'pulse', 940, 180, scale=1.08)
    return s


# ------------------------------------------------------------------ 뒷부분 5: 마무리(사진 위에 흰 글). 11-12: 강조색과 끝 로고 없이 글만
WHITE = 'FFFFFF'
VEIL = '120A24'


def photo_bg(key, fname, stops):
    """사진을 장 가득 깔고, 글이 읽히게 어둠을 얹는다. stops = [(자리 %, 어둠 %)] 위에서 아래로."""
    return [P(key + '/photo', str(PHOTO / fname), 0, 0, 1280, 720),
            R(key + '/veil', 0, 0, 1280, 720, fill=None, line=None, grad=dict(stops=[(p, VEIL, a) for p, a in stops], ang=90))]


END1_Y = 285                       # 인용 글상자의 위(11-12: 두 줄과 출처 묶음의 가운데가 화면 세로 가운데 y = 360에 오게, 168 → 285)


END_BY = 'Samsung Galaxy 「A Billion Reasons to Switch」 광고 카피 중'      # 11-13 6차: '— Samsung Galaxy 광고 카피 중'에서(팀원 덱의 표기)


def s_end1(photo='closing-1-sparklers.jpg', stops=((0, 68), (42, 52), (70, 30), (100, 26))):
    """인용 두 줄과 출처를 화면 한가운데(가로, 세로)에. 글은 모두 흰색. photo, stops: 다른 사진을 대 볼 때(tools/closing_try.py)."""
    s = Slide('end1', trans=('fade', 900), bar=False, bg=False, notes=NOTES['end1'])
    s.add('end/bg', photo_bg('end/bg', photo, list(stops)))
    y = END1_Y
    s.add('end1/q', [T('end1/q', 220, y, 840, 110,
                       ['당신이 사랑하는 모든 것에 더 가까이 다가가고,', '오래도록 이야기하게 될 순간을 담아보세요'],
                       size=30, color=WHITE, weight='b', align='c', lnspc=40, spc=-0.4)])
    s.add('end1/by', [T('end1/by', 340, y + 122, 600, 26, END_BY, size=13, color=WHITE, alpha=78, align='c', anchor='ctr')])
    s.on('end1/q', 'rise', 500, 800, dy=14)
    s.on('end1/by', 'fade_in', 1500, 600)
    return s


HAND = (670, 436)                  # 손글씨 '순간' 그림의 크기(px)


def s_end2(photo='closing-2-samsung-phone.jpg', stops=((0, 60), (55, 50), (100, 46)), hand=(215, 112, 300)):
    """순간을 휴대폰으로 담는 사람(6차: 앞면에 SAMSUNG이 보이는 휴대폰). 왼쪽 위에 손글씨 '순간'. hand = 손글씨의 (가운데 x, 가운데 y, 폭)."""
    s = Slide('end2', trans=('fade', 900), bar=False, bg=False, notes=NOTES['end2'])
    s.add('end/bg', photo_bg('end/bg', photo, list(stops)))
    cx, cy, w = hand
    s.add('end/hand', [P('end/hand', str(OUTRO / 'moment-hand-white.png'), cx - w / 2, cy - w * HAND[1] / HAND[0] / 2, w, w * HAND[1] / HAND[0])])
    s.on('end/hand', 'wipe_in', 500, 1100, dir='left')
    return s


def s_end3(photo='closing-3-family-sea.jpg', stops=((0, 54), (30, 58), (62, 58), (100, 30))):
    """손글씨 '순간'이 문장 속으로. 두 줄만 화면 가운데에 두고 말로 맺는다("지금까지 Weave Assist였습니다.").
    11-12: 글 묶음을 화면 가운데로, 로고 뒤의 어두운 둥근 그늘과 끝 로고(Weave 글자와 아이콘)는 없앰. 글은 모두 흰색."""
    s = Slide('end3', trans=('morph', 1100), bar=False, bg=False, notes=NOTES['end3'])
    s.add('end/bg', photo_bg('end/bg', photo, list(stops)))
    pt = 36
    a, b = '갤럭시의 모든 ', '이'
    hw = 118                                             # 문장 속 손글씨 '순간'의 폭
    wa, wb = tw(a, pt, 'b'), tw(b, pt, 'b')
    x0 = 640 - (wa + hw + 6 + wb) / 2
    y1 = 286                                             # 첫 줄. 두 줄 묶음의 가운데가 화면 가운데 바로 위(y ≈ 345)
    s.add('end3/a', [T('end3/a', x0, y1, wa + 10, 56, a, size=pt, color=WHITE, weight='b', anchor='ctr', spc=-0.4)])
    s.add('end/hand', [P('end/hand', str(OUTRO / 'moment-hand-white.png'), x0 + wa - 4, y1 + 28 - hw * HAND[1] / HAND[0] / 2 - 4, hw, hw * HAND[1] / HAND[0])])
    s.add('end3/b', [T('end3/b', x0 + wa + hw + 6, y1, wb + 10, 56, b, size=pt, color=WHITE, weight='b', anchor='ctr', spc=-0.4)])
    s.add('end3/c', [T('end3/c', 240, y1 + 62, 800, 56, '다시 이야기가 되도록', size=pt, color=WHITE, weight='b', align='c', anchor='ctr', spc=-0.4)])
    s.on(['end3/a', 'end3/b'], 'fade_in', 200, 600)
    s.on('end3/c', 'rise', 900, 800, dy=12)
    return s


BYE_MARK, BYE_PT = 86, 68          # 맺는 장의 아이콘 한 변과 글자 크기(14쪽 가운데의 로고와 같은 크기)


def s_bye():
    """맺는 인사("지금까지 Weave Assist였습니다. 감사합니다.")를 하는 마지막 장(11-13 7차): 덱의 기본 바탕 한가운데에 아이콘과 'Weave' 글자만."""
    s = Slide('bye', trans=('fade', 900), bar=False, notes=NOTES['bye'])
    w = BYE_MARK * 1.22 + logo_word_w(BYE_PT, 'Weave')
    mark, word, _ = logo('bye', 640 - w / 2 - 5, 360, mark=BYE_MARK, pt=BYE_PT, text='Weave')      # 글상자의 왼쪽 여백만큼 당겨 보이는 묶음이 한가운데에 오게
    s.add('bye/logo', mark + word)
    s.on('bye/logo', 'rise', 350, 800, dy=12)
    return s


# ------------------------------------------------------------------ 가름 장, 사진 출처
def s_divider(key, head, lines, note):
    s = Slide(key, trans=('fade', 500), bar=False, notes=note)
    s.add(key + '/t', [caption(key + '/t', [[(head, PURPLE)]], 640, 250, size=44)])
    s.add(key + '/s', [T(key + '/s', 160, 336, 960, 26 * len(lines), lines, size=14, color=SUB, align='c', lnspc=20)])
    return s


# 11-13 6차: 마무리 사진 셋을 바꿈(마무리사진_후보의 G15, A2, M4). 모션그래픽의 음악도 함께 적음. How it Works의 사진은 앞 장(apx_credit)에 있음
PHOTO_CREDITS = [('마무리 1 (노을 앞의 불꽃 막대)', 'Vitaly Gariev, Pexels (pexels.com/photo/36713116), Pexels 라이선스'),
                 ('마무리 2 (순간을 담는 휴대폰)', 'Stefan Maass, Unsplash (unsplash.com/photos/zu68hhvQM2M), Unsplash 라이선스'),
                 ('마무리 3 (노을 진 바다의 가족)', 'Radhika Studio, Pexels (pexels.com/photo/11538583), Pexels 라이선스'),
                 ('6쪽 화면 속 사진', 'Unsplash 사진 63장 (Wikimedia Commons 사본), 모두 CC0. 목록은 assets/src/photos/credits.json'),
                 ('15쪽 모션그래픽의 음악', 'Michael Ramir C., "A Special Feeling", Mixkit (Mixkit Stock Music Free License)')]


def s_credits2():
    s = Slide('apx_credit2', trans=('fade', 400), bar=False, notes='마무리 장과 6쪽에 쓴 사진, 모션그래픽에 쓴 음악의 출처입니다.')
    s.add('cr2/title', [caption('cr2/title', [[('사진과 음악 출처', INK)]], 640, 54, size=24)])
    s.add('cr2/sub', [T('cr2/sub', 100, 54 + 24 * 1.42 + 6, 1080, 24, '마무리 장의 배경 사진, 6쪽 휴대폰 화면 속 사진, 모션그래픽의 배경음악', size=13, color=SUB,
                        align='c')])
    out = []
    for i, (a, b) in enumerate(PHOTO_CREDITS):
        y = 160 + i * 64
        out += [R('cr2/%d/bg' % i, 160, y, 960, 52, prst='roundRect', radius=14, fill='FFFFFF', line=LINE2, line_w=1.0),
                T('cr2/%d/a' % i, 184, y, 240, 52, a, size=12, color=PURPLE, weight='b', anchor='ctr'),
                T('cr2/%d/b' % i, 430, y, 680, 52, b, size=10.5, color=BODY, anchor='ctr')]
    s.add('cr2/rows', out)
    return s


def s_fx_one():
    """기대효과 한 장(6차). fx_new가 이 파일을 불러 쓰므로 그릴 때 불러온다."""
    import fx_new
    return fx_new.s_fx()


def s_cmp_main():
    """기존 기능과의 비교(7차: 다시 본 발표로). cmp_new가 이 파일을 불러 쓰므로 그릴 때 불러온다."""
    import cmp_new
    return cmp_new.s_cmp()


# 11-12 4차: 비교 장을 Lock-in 앞으로(기대효과 → 비교 → Lock-in → 연표). Lock-in에서 '지금, 갤럭시에서 가능한 이유'로 바로 이어지게
# 11-13 6차: 기대효과 세 장 → 한 장, 비교 장은 Appendix로(make.appendix_specs). 차례: 기대효과 → Lock-in → 연표 → 마무리
# 11-13 7차: 비교 장을 다시 본 발표로(4차와 같은 자리), 맺는 인사를 하는 마지막 장(s_bye)을 더함. 차례: 기대효과 → 비교 → Lock-in → 연표 → 마무리 셋 → 맺는 장
# 11-13 8차: 비교 장은 다시 Appendix로(make.appendix_specs → cmp_new.s_cmp_apx2). 차례: 기대효과 → Lock-in → 연표 → 마무리 셋 → 맺는 장
SLIDES_BACK = [s_fx_one, s_bi, s_tl, s_end1, s_end2, s_end3, s_bye]
SLIDES_PROPOSAL = []               # 6차: 제안 장표 묶음은 없음(기대효과를 고리의 움직임으로 보여 주던 세 장은 이전 판 (5차)에)
