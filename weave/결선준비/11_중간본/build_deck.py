#!/usr/bin/env python3
"""결선 중간본 덱 조립. 원본 02_PPT/Weave_결선.pptx는 고치지 않고, 새 파일 02_PPT/Weave_결선_중간본.pptx를 만든다.

본편: 표지(반복 영상) → Motivation → Pain Points → 인포그래픽 영상(세 시나리오) → Solution
      → How it Works(장표5 A1 덱용 00판, --hiw a1_deck이면 00 없는 판) → Why Samsung → Why Now → 차별화 → 기대효과 1~3 → END
부록: 파이프라인, 관련 연구, Reasoning Embedding, UX 1~3 상세, 비교, Q&A 2장
참고(발표에서 안 씀): 구분 장 → 앱 데모, 이전 표지, 만화, 이전 시나리오 1~3, 이전 How it Works

  python build_deck.py              조립 → 삼성 글꼴로 바꾸기 → PowerPoint로 영상 넣기 → 장별 PNG·한눈에
  python build_deck.py --no-png     PNG 없이
  python build_deck.py --hiw a1_deck --out /tmp/중간본_00없음.pptx   How it Works를 00 없는 판으로
  python build_deck.py --team-style side      표지 팀 이름을 '이름 둘 | 팀 두 줄'로
  python build_deck.py --embed-fonts          글꼴을 pptx 안에 넣어 저장(받는 사람이 글꼴 없이도 보게, 용량 늘어남)

영상은 PowerPoint(COM)로 넣는다: 표지 = 자동 재생 + 끝나면 반복, 인포그래픽 = 자동 재생 한 번.
열려 있는 PowerPoint 창은 건드리지 않는다(C:\\Temp 사본을 창 없이 열고 그 사본만 닫음).
"""
import argparse
import copy
import shutil
import subprocess
import sys
from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / '02_PPT' / 'Weave_결선.pptx'
DST = ROOT / '02_PPT' / 'Weave_결선_중간본.pptx'
HIW = ROOT / '09_HowItWorks' / '장표5'
SOL = ROOT / '07_소스' / 'slides' / 'p05_결선' / 'apply_solution.py'
APX = ROOT / '07_소스' / 'slides' / 'appendix_결선' / 'apply_appendix.py'
COVER_MP4 = ROOT / '10_표지영상' / '표지_루프.mp4'
INTRO_MP4 = ROOT / '08_인트로영상' / 'Weave_인포그래픽_120초.mp4'
VENV_PY = Path.home() / '.cache' / 'weave-tools' / 'venv' / 'bin' / 'python'

sys.path.insert(0, str(HIW))
import build5            # noqa: E402
import render2           # noqa: E402
import scene5            # noqa: E402
import story as S        # noqa: E402
from hiw_lib import q    # noqa: E402
import samsung_fonts     # noqa: E402

COVER_NOTES = ('표지입니다. 발표를 시작하기 전부터 반복 영상을 띄워 둡니다. 구글 검색창에 지은이네 집들이 때 마셨던 와인을 적고 실타래 버튼을 누르면, '
               '흩어진 기록 가운데 지은의 카톡과 그날 사진이 보라색 실로 이어져 배비치 소비뇽 블랑을 건네고, 입력하기를 누르면 검색어가 바뀝니다.')


def text_slide(prs, layout, name, lines, notes):
    """참고 구분 장처럼 글만 있는 장(HIW와 같은 바탕·글꼴)."""
    s = prs.slides.add_slide(layout)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    pa = S.Painter(s)
    for p in build5.bg_prims():
        pa.prim(p)
    cw = S.tw(name, 10.5, 'sb') + 32
    pa.prim(S.R('ref/chip', 640 - cw / 2, 250, cw, 28, prst='roundRect', fill=S.PURPLE, line=None))
    pa.prim(S.T('ref/chip_t', 640 - cw / 2, 250, cw, 28, name, size=10.5, color='FFFFFF', weight='sb', align='c', anchor='ctr', spc=0.5))
    pa.prim(S.T('ref/title', 140, 296, 1000, 50, lines[0], size=26, color=S.INK, weight='b', align='c', anchor='ctr'))
    pa.prim(S.T('ref/sub', 140, 356, 1000, 90, list(lines[1:]), size=13, color='5B5866', align='c', lnspc=20))
    set_notes(s, notes)
    return s


TEAMS = [('Samsung Research', 'AI System Team', ['이재웅', '양서윤']), ('Samsung Research', 'AI Core Team', ['장이준', '이지현']), ('하만협력', '오디오개발Lab', ['조성빈'])]
TITLE, TAGLINE = 'Weave Assist', '흩어진 기억을 엮어, 지금을 완성하다'     # 이전 표지와 같은 문구
CX = 70                                         # 표지 글 왼쪽 끝. 영상의 왼쪽 빈 자리는 x < 564(1280 기준)
MARK = 56                                       # 'Weave' 앞 아이콘(인트로 끝 화면의 보라 네모 + 흰 실타래)
FONTS = Path.home() / '.cache' / 'weave-tools' / 'fonts'
GRAD = ('<a:gradFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" rotWithShape="1">'
        '<a:gsLst><a:gs pos="0"><a:srgbClr val="4E36CF"/></a:gs><a:gs pos="100000"><a:srgbClr val="8F66FF"/>'
        '</a:gs></a:gsLst><a:lin ang="0" scaled="1"/></a:gradFill>')


def fw(text, pt, face):
    """실제 삼성 글꼴로 잰 글 폭(px, 1280 기준). 글꼴 파일이 없으면 엔진 어림값."""
    try:
        f = ImageFont.truetype(str(FONTS / face), 1000)
        return f.getlength(text) / 1000 * pt * 96 / 72
    except OSError:
        return S.tw(text, pt, 'b' if '700' in face else 'r')


def cover_text(slide, team_style='under'):
    """표지 왼쪽 글: 아이콘 + 제목(보라 그라데이션) · 부제 · 팀별 이름. 영상은 PowerPoint로 맨 뒤에 깔림.

    team_style: 'under' = 팀원 이름을 한 줄로 두고 그 아래 가는 선 + 팀 이름(세 팀이 한 줄)
                'side'  = 이름 둘을 위아래로, 오른쪽에 팀 이름을 두 줄로(사용자 제안 'AI System / Team')
    """
    pa = S.Painter(slide)                        # 바탕은 영상이 깔므로 도형 바탕은 그리지 않음(영상이 그 뒤로 숨지 않게)
    cy = 260                                     # 제목 줄 가운데
    pa.prim(S.R('cover/mark', CX, cy - MARK / 2, MARK, MARK, prst='roundRect', radius=15, line=None,
                grad=dict(stops=[(0, '8D6BFF', None), (55, '6B4EFF', None), (100, '5A3FE0', None)], ang=55),
                shadow=(18, 7, '6B4EFF', 30)))
    ic = MARK * 2 / 3
    pa.prim(S.P('cover/mark_icon', 'weave-spool-white.png', CX + (MARK - ic) / 2, cy - ic / 2, ic, ic))
    tx = CX + MARK + 13
    t = pa.prim(S.T('cover/title', tx - 2, cy - 38, 470, 76, TITLE, size=48, color=S.PURPLE, weight='b', anchor='ctr',
                    spc=-0.5))
    for rp in t.iter(q('a:rPr'), q('a:endParaRPr')):
        for tag in ('a:latin', 'a:ea', 'a:cs'):          # 로고 글꼴(인트로 끝 화면과 같음). 굵게는 이 글꼴의 Bold
            e = rp.find(q(tag))
            if e is not None:
                e.set('typeface', 'Samsung Sharp Sans')
        old = rp.find(q('a:solidFill'))
        if old is None:
            continue
        old.addprevious(etree.fromstring(GRAD))
        rp.remove(old)
    pa.prim(S.T('cover/sub', CX + 1, 306, 520, 40, TAGLINE, size=20, color=S.INK2, weight='b', anchor='ctr'))

    x = CX + 1
    if team_style == 'under':
        for k, (dept, team, names) in enumerate(TEAMS):
            nw = [fw(n, 13, 'SamsungOneKorean-700.ttf') for n in names]
            gap = 14
            names_w = sum(nw) + gap * (len(names) - 1)
            gw = max(names_w, fw(team, 9.5, 'SamsungOneKorean-400.ttf'), fw(dept, 9.5, 'SamsungOneKorean-400.ttf'))
            nx = x
            for i, n in enumerate(names):
                pa.prim(S.T('cover/n%d%d' % (k, i), nx, 572, nw[i] + 8, 22, n, size=13, color=S.INK, weight='b'))
                nx += nw[i] + gap
            pa.prim(S.R('cover/line%d' % k, x, 599, gw, 1.3, fill='C3B6F7', line=None))
            pa.prim(S.T('cover/dept%d' % k, x, 605, gw + 12, 18, dept, size=9.5, color=S.SUB))
            pa.prim(S.T('cover/team%d' % k, x, 622, gw + 12, 18, team, size=9.5, color=S.SUB))
            x += gw + 40
    else:
        for k, (dept, team, names) in enumerate(TEAMS):
            nw = max(fw(n, 13, 'SamsungOneKorean-700.ttf') for n in names)
            for i, n in enumerate(names):
                pa.prim(S.T('cover/n%d%d' % (k, i), x, 578 + i * 26, nw + 8, 22, n, size=13, color=S.INK, weight='b'))
            lx = x + nw + 11
            rows = [dept, team]
            pa.prim(S.R('cover/line%d' % k, lx, 582, 1.3, 26 * len(names) - 8, fill='C3B6F7', line=None))
            tw_ = max(fw(r, 10, 'SamsungOneKorean-400.ttf') for r in rows)
            for i, r in enumerate(rows):
                pa.prim(S.T('cover/team%d%d' % (k, i), lx + 11, 581 + i * 26, tw_ + 12, 20, r, size=10, color=S.SUB))
            x = lx + 11 + tw_ + 36


INFO_NOTES = ('인포그래픽 영상입니다(2분, 자동 재생). 영상이 재생되는 동안에는 말하지 않고, 스크린 옆으로 반 걸음 물러서서 화면을 함께 봅니다. '
              '마지막 로고가 뜨면 무대 중앙으로 돌아와 다음 장으로 넘어갑니다. '
              '현장 음향이 작을 때만 장면 카드가 뜰 때 한 문장씩 얹습니다. '
              '첫째, 급한 통화 중에도 앱을 뒤질 필요 없이, 아래에서 쓸어 올리면 끝납니다. '
              '둘째, 정확한 이름이 생각나지 않아도, 카톡의 날짜 단서와 그날 찍은 사진을 스스로 이어 정답을 찾아냅니다. '
              '셋째, 공항에 내리는 순간, 내 위치와 탑승권, 그리고 3주 전 아내의 카톡까지 엮어 잊고 있던 약속을 먼저 일깨워 줍니다.')


def blank_slide(prs, layout, notes):
    s = prs.slides.add_slide(layout)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    set_notes(s, notes)
    return s


NOTE_TPL = []


def set_notes(slide, text):
    ns = slide.notes_slide
    if ns.notes_text_frame is None:
        for e in NOTE_TPL:
            ns.shapes._spTree.append(copy.deepcopy(e))
    ns.notes_text_frame.text = text


def reorder(prs, order):
    lst = prs.slides._sldIdLst
    by_part = {}
    for e in list(lst):
        by_part[prs.part.related_part(e.get(q('r:id')))] = e
    assert len(order) == len(by_part) == len(set(id(s) for s in order)), (len(order), len(by_part))
    for e in list(lst):
        lst.remove(e)
    for s in order:
        lst.append(by_part[s.part])



# ------------------------------------------------------------------ 말투·시나리오 전수 수정(2026-11-05). 글자 조각(run)마다 새 글을 적어 색과 굵기를 그대로 둔다
EDITS = {
    2: [(['당신의 휴대폰은 이미 ', '당신', '을 담고 있습니다.'], ['내 휴대폰에는 이미 ', '내 기억', '이 다 들어 있습니다.']),
        (['대화도', ',', ' 사진도', ',', ' 메모도 분명 ', '다 남아있는데'], ['대화도', ',', ' 사진도', ',', ' 메모도 분명 ', '다 남아 있는데']),
        (['다시 ', '꺼내쓰려면', ' 결국 ', '내가 다 찾아야 하죠', '.'], ['다시 ', '꺼내 쓰려면', ' 결국 ', '내가 다 찾아야 합니다', '.'])],
    3: [(['그 어디', '에 있더라?'], ['그게 어디', '에 있더라?']),
        (['찾을 내용은 알지만', ',', ' 어느 앱에 있는지 모릅니다', '.'], ['찾을 내용은 알지만', '', ' 어느 앱에 있는지 모릅니다', '.']),
        (['정확한 이름이 떠오르지 않아', ',', ' 검색부터 막힙니다', '.'], ['정확한 이름이 떠오르지 않아', '', ' 검색부터 막힙니다', '.']),
        (['필요한 순간에도', ',', ' 그런 기억이 있었는지 떠오르지 않습니다', '.'], ['필요한 순간에도', '', ' 그런 기억이 있었는지 떠오르지 않습니다', '.']),
        (['스쳐 간 부탁과 작은 약속들, 기록해 두고도 잊어버리곤 합니다.'], ['스쳐 간 부탁과 작은 약속을 기록해 두고도 잊어버리곤 합니다.']),
        (['노트, 메일, 대화내역을 하나씩 확인합니다.'], ['노트, 메일, 대화 내역을 하나씩 확인합니다.']),
        (['앱을 하나씩 열어보는 중'], ['앱을 하나씩 열어 보는 중']),
        (['“', '가족 · 친구들이 흘린 말 한마디를 놓치지 않고 '], ['“', '가족과 친구들이 흘린 말 한마디를 놓치지 않고 ']),
        (['챙겨주고 싶어요', '.”'], ['챙겨 주고 싶어요', '.”'])],
    9: [(['갤러리 · 삼성노트 · 캘린더 등'], ['갤러리 · 삼성노트 · 캘린더 · 월렛 등']),
        (['여러 앱에 파편화된 일상 데이터를 삼성의 PDE 기술을 이용해'], ['여러 앱에 흩어진 일상 데이터를 삼성 PDE와 연계해']),
        (['통합 분석하여 개인화된 맞춤 경험을 제공합니다'], ['기기 안에서 이해하고 나에게 맞는 경험을 제공합니다'])],
    10: [(['갤러리 · 삼성노트 · 캘린더 등'], ['갤러리 · 삼성노트 · 캘린더 · 월렛 등']),
         (['이제, ', '기기 안에서 꺼내는 과정', '에 집중할 때입니다.'], ['이제 ', '기기 안에서 꺼내 쓰는 과정', '에 집중할 때입니다.'])],
    11: [(['기존 ', 'AI ', '서비스들과 달리, ', 'Weave', '는 단말 전체의 데이터를 유기적으로 연결하는 사용자 경험을 제공합니다.'],
          ['기존 ', 'AI ', '서비스들과 달리 ', 'Weave', '는 기기 전체의 기록을 이어 필요한 순간 건네는 경험을 제공합니다.']),
         (['문자 등 시스템 전반'], ['월렛 등 시스템 전반']),
         (['입력창 진입 시 연관 맥락을'], ['입력창 진입 시 연관 기억을']),
         (['키보드에 먼저 띄움'], ['키보드에 먼저 제안'])],
    12: [(['"잠깐만 찾아볼게" 대신, 하던 일을 이어갑니다'], ['"잠깐만 찾아볼게" 대신 하던 일을 이어 갑니다']),
         (['찾는 시간은 줄이고', ' · 기억은 되살리고 · 기록은 자산으로'], ['찾는 시간은 줄이고', ', 기억은 되살리고, 기록은 자산으로']),
         (['정보를 찾는 데 허비'], ['정보를 찾는 데 씁니다']),
         (['여러 앱의 기록을 한번에', ' 찾습니다.'], ['여러 앱의 기록을 한 번에', ' 찾습니다.'])],
    13: [(['찾는 시간은 줄이고 · ', '기억은 되살리고', ' · 기록은 자산으로'], ['찾는 시간은 줄이고, ', '기억은 되살리고', ', 기록은 자산으로']),
         (['"언젠가 필요할까봐" 캡처나'], ['"언젠가 필요할까 봐" 캡처나']),
         (['메모를 해두지만, 단 한 번도'], ['메모를 해 두지만 단 한 번도']),
         (['열어보지 않고 방치'], ['열어 보지 않습니다']),
         (['엄마가 먹고 싶다던 무화과시루가,'], ['아내가 지나가듯 말한 면세점 갈색병이,']),
         (['친구가 좋아하는 소비뇽 블랑이'], ['친구 집들이에서 마신 소비뇽 블랑이']),
         (['내가 놓쳤던 기억까지 챙겨주는 일상의 조력자', '가 됩니다.'], ['내가 놓쳤던 기억까지 챙겨 주는 일상의 조력자', '가 됩니다.'])],
    14: [(['쌓인 기록이, 갤럭시를 계속 쓰는 이유가 됩니다'], ['쌓인 기록이 갤럭시를 계속 쓰는 이유가 됩니다']),
         (['찾는 시간은 줄이고 · 기억은 되살리고 · ', '기록은 자산으로'], ['찾는 시간은 줄이고, 기억은 되살리고, ', '기록은 자산으로']),
         (['쌓아둔 대화·사진·메모가'], ['쌓아 둔 대화, 사진, 메모가'])],
    18: [(['개발 ', 'T/F'], ['AI System Team', '']),
         (['채용 T/F'], ['AI Core Team']),
         (['읽어주셔서 감사합니다!'], ['경청해 주셔서 감사합니다.']),
         (["'좋아요'", '와 ', "'응원 댓글'", '은 신입사원들에게 큰 힘이 됩니다.'], ['', '흩어진 기억을 엮어 지금을 완성하는 ', 'Weave Assist', '입니다.'])],
}
LABEL = {2: 'Motivation', 3: 'Pain Points', 9: 'Why Samsung', 10: 'Why Now', 11: '차별화', 12: '기대 효과 1', 13: '기대 효과 2', 14: '기대 효과 3', 15: 'App Demo', 16: 'Q&A 데이터 접근', 18: 'END'}
NOTES = {
    2: '세상 모든 지식은 AI에게 물으면서, 정작 내 기억은 아직도 직접 찾아 헤맵니다. 어제 간 이자카야 이름을 검색해도 결과가 없습니다. 내 휴대폰에는 이미 내 기억이 다 들어 있습니다. 흩어져 있을 뿐, 사라진 것은 아닙니다.',
    3: '막막한 순간은 세 가지입니다. 첫째, 찾을 내용은 알지만 어느 앱에 있는지 모릅니다. 신입사원 성빈 씨는 회의 내용을 찾느라 노트와 메일, 대화 내역을 하나씩 확인합니다. 둘째, 정확한 이름이 떠오르지 않아 검색부터 막힙니다. 셋째, 필요한 순간에도 그런 기억이 있었는지 떠오르지 않습니다. 직장인 지현 씨는 가족과 친구가 흘린 말 한마디를 놓치지 않고 챙겨 주고 싶어 합니다. (톤을 한 단계 높여) 어느 앱에 있는지 몰라 헤매는 순간, 이름이 떠오르지 않아 검색창 앞에서 멈칫하는 순간, 그리고 소중한 사람의 스쳐 간 말을 깜빡하는 순간까지. 기억은 분명 내 휴대폰 안에 다 있는데, 왜 매번 내가 직접 찾아 헤매야 할까요? 만약 내 기기가 흩어진 기억의 조각들을 하나의 실처럼 엮어, 지금 필요한 순간에 먼저 건네준다면 어떨까요? Weave Assist가 바꾸어 놓을 우리의 세 가지 일상, 지금 바로 만나 보시죠. (0.5초 쉬고 클릭)',
    9: '왜 삼성일까요? 특정 플랫폼의 앱은 자사 서비스 안의 데이터만 볼 수 있습니다. 삼성은 갤러리, 삼성노트, 캘린더, 월렛처럼 기록이 쌓이는 기본 앱과 이를 다시 꺼내 쓰는 삼성 키보드를 하나의 제품 경험으로 설계할 수 있습니다. 앱 사이의 벽을 넘어 기기 전체에 흩어진 단서를 하나의 실처럼 엮으면, 사용자는 별도의 앱을 켜지 않고 매일 쓰는 키보드에서 필요한 기억을 바로 씁니다. 데이터는 Personal Data Engine과 연계해 기기 안에서 처리하고, KEEP과 Knox Vault로 보호합니다.',
    10: '왜 지금일까요? 기기 안에서 기록을 이해하고 실제 사용으로 연결할 온디바이스 AI 인프라가 갖춰지고 있습니다. 갤러리, 삼성노트, 캘린더, 월렛에 남은 기록을 온디바이스 API인 Android AICore, 모바일용 경량 LLM, 그리고 AI 연산 특화 하드웨어인 NPU가 기기 안에서 이해합니다. Weave는 기록을 더 많이 저장하는 것보다, 이미 남아 있는 기록을 필요한 순간 꺼내 쓰는 과정에 집중합니다.',
    11: '경쟁 서비스와 비교하겠습니다. Samsung Writing Assist는 입력 중인 문장을 생성하고 교정합니다. Now Nudge는 상황을 인지해 정보를 안내합니다. Kanana는 카카오톡이라는 단일 앱 안에서 동작합니다. Weave는 갤러리, 삼성노트, 캘린더, 월렛 등 기기 전체에 흩어진 기록을 찾아 앱을 넘나들며 이어 가고, 데이터를 온디바이스로 처리하며, 대화와 입력 맥락에 맞는 기억을 키보드에 먼저 띄워 줍니다.',
    12: '첫 번째 기대 효과입니다. 사람들은 하루 평균 59분을 여러 앱에 흩어진 정보를 찾는 데 씁니다. Weave는 어느 앱에 기록했는지 찾고, 오래된 대화와 갤러리를 넘기던 과정을 줄입니다. 키보드에서 필요한 내용을 제안받고 여러 앱의 기록을 한 번에 찾으니, 찾는 시간이 줄고 앱을 오가는 일이 줄고 대화와 업무의 흐름이 이어집니다.',
    13: '두 번째 기대 효과입니다. 사용자의 33%가 언젠가 필요할까 봐 캡처나 메모를 해 두지만 한 번도 열어 보지 않습니다. Weave와 함께라면 아내가 지나가듯 말한 면세점 갈색병, 친구 집들이에서 마신 소비뇽 블랑이 필요한 순간에 떠오릅니다. 잊었던 약속을 다시 찾고, 디테일이 감동을 만듭니다. 갤럭시는 저장 도구를 넘어 놓쳤던 기억까지 챙겨 주는 일상의 조력자가 됩니다.',
    14: '세 번째 기대 효과입니다. 스마트폰 사용자는 월평균 41개의 앱을 쓰고, 69%는 기기 내 데이터를 지우지 않고 그대로 씁니다. Weave는 쌓아 둔 대화, 사진, 메모를 오늘의 검색과 답장에 쓰이는 자산으로 바꿉니다. 사용자는 내 기록을 잘 활용해 주는 갤럭시의 가치를 경험하고, 기록이 쌓일수록 갤럭시를 계속 쓸 이유가 생깁니다.',
    15: '참고: 예선 때 만든 앱 데모입니다. 이전 시나리오(A사 시연, 무화과시루, 캘린더 집들이)를 담고 있어 결선 발표에서는 쓰지 않습니다.',
    16: 'Q1 데이터 접근: 삼성 기본 앱은 사용자 동의하에 기기 내부에서 직접 연동합니다. 카카오톡 등 외부 메신저는 Android 공식 API로 사용자가 허용한 앱이 새 알림을 받습니다. Google Gemini도 같은 허용 아래 알림 속 메시지를 읽고 답장합니다. 사진은 갤러리에 저장된 이미지를 활용합니다. 이전 대화는 카카오톡 채팅방 설정의 대화 내용 내보내기로 가져올 수 있습니다. Weave는 통화 내용을 듣지 않습니다. 통화 화면에서는 사용자가 위로 밀어 검색어를 직접 적습니다. 잠금 화면과 홈 화면의 위로 밀기는 지금처럼 삼성 월렛이 씁니다.\n'
        'Q2 속도와 배터리: 무거운 색인은 충전 중, 기기 유휴 같은 조건으로 미리 처리하고, 사용 중에는 필요한 기록만 찾아 읽습니다. 검색은 가벼운 임베딩이 맡고, 언어 모델에는 추려 낸 근거만 전달합니다.\n'
        'Q3 사생활: 허용한 기록만 기기 안에서 처리하고, 언제든 끄거나 색인을 지울 수 있습니다. 기록 저장소의 암호화 키는 Android Keystore로 보호합니다. 근거가 부족하면 후보와 원문을 먼저 보여 주고, 최종 판단은 사용자가 내립니다.',
    18: '경청해 주셔서 감사합니다. 흩어진 기억을 엮어 지금을 완성하는 Weave Assist였습니다.',
}
LINKS = [((84, 287, 180, 42), 3), ((84, 340, 180, 42), 4), ((84, 393, 180, 42), 5), ((329, 290, 222, 56), 6), ((329, 346, 222, 100), 1),
         ((618, 303, 300, 103), 2), ((311, 507, 628, 29), 2)]        # 파이프라인 장의 칸 → 해당 Appendix 장(appx 번호)
HYBRID_NOTE = '* 추론 유형: Analytical Reasoning (Wei et al., "A Survey of Reasoning-Intensive Retrieval", ACL 2026)'


def iter_paras(shapes):
    for sh in shapes:
        if sh.shape_type == 6:
            yield from iter_paras(sh.shapes)
        elif sh.has_text_frame:
            yield from sh.text_frame.paragraphs


def apply_edits(orig):
    log = []
    for i, items in EDITS.items():
        for old, new in items:
            tgt = ''.join(old)
            hits = [p for p in iter_paras(orig[i].shapes) if ''.join(r.text for r in p.runs) == tgt]
            assert hits, (i, tgt)
            for p in hits:
                rs = p.runs
                assert len(rs) == len(old), (i, tgt, [r.text for r in rs])
                for r, t in zip(rs, new):
                    r.text = t
            log.append((LABEL[i], tgt, ''.join(new)))
    for p in iter_paras(orig[9].shapes):       # 보안 문구: '데이터'가 줄 끝에서 갈리지 않게 '민감한' 뒤에서 줄을 바꿈
        rs = [r for r in p.runs if r.text == ' 민감한 ']
        if rs:
            rs[0].text = ' 민감한'
            br = etree.Element(q('a:br'))
            br.append(copy.deepcopy(rs[0]._r.find(q('a:rPr'))))
            rs[0]._r.addnext(br)
    for i, t in NOTES.items():
        old = orig[i].notes_slide.notes_text_frame.text if orig[i].has_notes_slide else ''
        if old.strip() != t.strip():
            log.append((LABEL[i] + ' 노트', old, t))
        set_notes(orig[i], t)
    return log


def add_links(a1, targets):
    for (x, y, w, h), k in LINKS:
        sh = a1.shapes.add_shape(MSO_SHAPE.RECTANGLE, x * 9525, y * 9525, w * 9525, h * 9525)
        sh.fill.solid()                        # '채우기 없음'은 발표 중 안쪽을 눌러도 반응하지 않아, 완전히 투명한 채우기로 둔다
        sh.fill.fore_color.rgb = RGBColor(255, 255, 255)
        etree.SubElement(sh._element.spPr.find(q('a:solidFill'))[0], q('a:alpha')).set('val', '0')
        sh.line.fill.background()
        sh.shadow.inherit = False
        sh.name = 'Link to Appendix %d' % (k + 1)
        sh.click_action.target_slide = targets[k]


MEDIA_PS1 = r'''param([string]$Pptx, [string]$CoverMp4 = "", [string]$IntroMp4 = "", [int]$CoverIdx = 1, [int]$IntroIdx = 0,
      [string]$CoverPoster = "", [string]$IntroPoster = "", [int]$EmbedFonts = 0)
$ErrorActionPreference = "Stop"
$running = @(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Pptx, 0, 0, 0)
try {
  $W = $pres.PageSetup.SlideWidth; $H = $pres.PageSetup.SlideHeight
  $log = @()
  foreach ($job in @(@($CoverIdx, $CoverMp4, "Cover loop video", -1, $CoverPoster), @($IntroIdx, $IntroMp4, "Infographic video", 0, $IntroPoster))) {
    if (-not $job[1]) { continue }
    $s = $pres.Slides.Item($job[0])
    $v = $s.Shapes.AddMediaObject2($job[1], 0, -1, 0, 0, $W, $H)
    $v.Name = $job[2]
    $v.ZOrder(1)
    if ($job[4]) { $v.MediaFormat.SetDisplayPictureFromFile($job[4]) }
    $ps = $v.AnimationSettings.PlaySettings
    $ps.PlayOnEntry = -1
    $ps.LoopUntilStopped = $job[3]
    $ps.HideWhileNotPlaying = 0
    $ps.RewindMovie = 0
    $seq = $s.TimeLine.MainSequence
    $t = "slide " + $job[0] + " effects " + $seq.Count
    for ($i = 1; $i -le $seq.Count; $i++) {
      $e = $seq.Item($i)
      $t += " [type " + $e.EffectType + " trig " + $e.Timing.TriggerType
      if ($e.Timing.TriggerType -eq 1) { $e.Timing.TriggerType = 2; $t += "->2" }
      $t += "]"
    }
    $t += " loop " + $ps.LoopUntilStopped + " playOnEntry " + $ps.PlayOnEntry
    $log += $t
  }
  if ($EmbedFonts) { $pres.SaveAs($Pptx, 24, -1); $log += "fonts embedded" } else { $pres.Save() }
  $log -join "`n"
} finally {
  # 사용자가 PowerPoint를 쓰는 중이면 호출이 잠깐 거부될 수 있음 → 몇 번 다시 시도(이 사본만 닫음)
  for ($k = 0; $k -lt 10; $k++) {
    try { $pres.Close(); break } catch { Start-Sleep -Seconds 2 }
  }
  if (-not $running) { $app.Quit() }
}
'''


def add_media(pptx, cover_idx, intro_idx, embed_fonts=False):
    """PowerPoint로 영상 넣기(1부터 세는 장 번호). embed_fonts면 글꼴을 파일 안에 넣어 저장."""
    tmpd = render2.WINTMP / 'midterm'
    tmpd.mkdir(parents=True, exist_ok=True)
    (tmpd / 'media.ps1').write_text('\ufeff' + MEDIA_PS1, encoding='utf-8')
    work = tmpd / 'deck.pptx'
    shutil.copyfile(pptx, work)
    args = ['-Pptx', render2.winpath(work), '-CoverIdx', str(cover_idx), '-IntroIdx', str(intro_idx),
            '-EmbedFonts', '1' if embed_fonts else '0']
    if COVER_MP4.exists():
        shutil.copyfile(COVER_MP4, tmpd / 'cover.mp4')
        poster = COVER_MP4.parent / '표지_포스터.jpg'          # 4K 포스터는 jpg가 훨씬 가벼움
        shutil.copyfile(poster if poster.exists() else COVER_MP4.parent / '표지_포스터.png', tmpd / 'cover.png')
        args += ['-CoverMp4', render2.winpath(tmpd / 'cover.mp4'), '-CoverPoster', render2.winpath(tmpd / 'cover.png')]
    else:
        print('   ! 표지 영상이 아직 없음:', COVER_MP4)
    shutil.copyfile(INTRO_MP4, tmpd / 'intro.mp4')
    ff = Path.home() / '.cache' / 'weave-tools' / 'bin' / 'ffmpeg'          # 인포그래픽 미리보기 그림 = 오프닝 로고(2.2초)
    subprocess.run([str(ff), '-y', '-loglevel', 'error', '-ss', '2.2', '-i', str(INTRO_MP4), '-frames:v', '1', str(tmpd / 'intro.png')],
                   check=True)
    args += ['-IntroMp4', render2.winpath(tmpd / 'intro.mp4'), '-IntroPoster', render2.winpath(tmpd / 'intro.png')]
    code, log = render2.ps(tmpd / 'media.ps1', *args)
    print(log.strip())
    assert code == 0, log
    shutil.copyfile(work, pptx)
    for f in ('deck.pptx', 'cover.mp4', 'intro.mp4', 'cover.png', 'intro.png'):
        (tmpd / f).unlink(missing_ok=True)


def sheet(pngs, dst, labels, cols=6, w=400):
    ims = [Image.open(p).convert('RGB') for p in pngs]
    h = int(w * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new('RGB', (cols * (w + 10) + 10, rows * (h + 30) + 10), 'white')
    d = ImageDraw.Draw(out)
    fnt = ImageFont.truetype(str(ROOT / '06_에셋' / '글꼴' / 'NotoSansKR-700.ttf'), 14)
    for i, im in enumerate(ims):
        x, y = 10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 30)
        out.paste(im.resize((w, h), Image.LANCZOS), (x, y + 20))
        d.text((x, y), labels[i], fill=(60, 50, 90), font=fnt)
    out.save(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-png', action='store_true')
    ap.add_argument('--hiw', default='a1_deck00', help='장표5의 SPEC 모듈(a1_deck00 = 00 있는 덱용, a1_deck = 00 없는 판)')
    ap.add_argument('--out', default=str(DST))
    ap.add_argument('--team-style', default='under', choices=['under', 'side'])
    ap.add_argument('--embed-fonts', action='store_true')
    a = ap.parse_args()
    dst = Path(a.out).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    # 1. 솔루션 장표(5쪽)를 새 시나리오로 다시 채우고, Appendix 새 장을 더한 사본
    step0, step1 = Path('/tmp/midterm_step0.pptx'), Path('/tmp/midterm_step1.pptx')
    r = subprocess.run([str(VENV_PY), str(SOL), str(SRC), str(step0)], capture_output=True, text=True, cwd=SOL.parent)
    print(r.stdout.strip()[-300:], r.stderr.strip()[-400:])
    assert r.returncode == 0 and step0.exists(), '솔루션 장표 다시 채우기 실패'
    r = subprocess.run([str(VENV_PY), str(APX), str(step0), str(step1)], capture_output=True, text=True, cwd=APX.parent)
    print(r.stdout.strip()[-500:], r.stderr.strip()[-800:])
    assert r.returncode == 0 and step1.exists(), 'Appendix 새 장 더하기 실패'

    prs = Presentation(str(step1))
    orig = list(prs.slides)
    assert len(orig) == 26, len(orig)
    layout = orig[8].slide_layout
    NOTE_TPL[:] = [copy.deepcopy(sh._element) for sh in orig[8].notes_slide.placeholders]
    change_log = apply_edits(orig)

    # 2. How it Works(장표5 A1 덱용)
    import importlib
    sc = scene5.build(importlib.import_module(a.hiw).SPEC)
    hiw, warns = build5.add_steps(prs, sc, layout, NOTE_TPL)
    for w in warns:
        print('   !', w)
    hy = [i for i, st in enumerate(sc.steps) if st.key == 'hybrid']
    assert hy, '빠진 한 단계 장이 없음'
    S.Painter(hiw[hy[0]]).prim(S.T('hiw/reason_note', 86, 664, 1100, 20, HYBRID_NOTE, size=10, color='8E88A0', anchor='ctr'))
    S.morph_transition(hiw[0], 1000)          # 솔루션 → How it Works 첫 장은 부드럽게(겹치는 도형이 없어 페이드처럼)

    # 3. 새 표지(영상은 4단계에서), 인포그래픽 영상 장, 참고 구분 장
    cover = blank_slide(prs, layout, COVER_NOTES)
    cover_text(cover, a.team_style)
    info = blank_slide(prs, layout, INFO_NOTES)     # 바탕은 영상이 깖(도형 바탕을 그리면 영상이 그 뒤로 숨음)
    ref = text_slide(prs, layout, 'REFERENCE', ['참고 · 발표에서 쓰지 않는 장표',
                                                '앱 데모, 이전 표지, 만화, 이전 시나리오 1~3, 이전 How it Works',
                                                '새 구성(표지 영상, 인포그래픽, 솔루션, How it Works)으로 바뀌기 전 장표입니다.'],
                     '참고용 구분 장. 이 뒤의 장표는 발표에서 쓰지 않습니다.')

    new_app = orig[19:26]                                  # 파이프라인, 관련 연구, Reasoning Embedding, UX 1~3 상세, 비교
    main_ = [cover, orig[2], orig[3], info, orig[4], *hiw, orig[9], orig[10], orig[11], orig[12], orig[13], orig[14], orig[18]]
    appx = [*new_app, orig[17], orig[16]]
    refs = [ref, orig[15], orig[0], orig[1], orig[5], orig[6], orig[7], orig[8]]
    order = main_ + appx + refs
    reorder(prs, order)
    add_links(new_app[0], new_app)                         # 파이프라인 장의 칸을 누르면 해당 Appendix 장으로
    n = samsung_fonts.remap_prs(prs)                 # 글꼴: Inter·Noto Sans KR → SamsungOneKorean 400·500·700
    left = {f: c for f, c in samsung_fonts.faces_used(prs).items() if not f.startswith(('SamsungOne', '+', 'Samsung Sharp'))}
    print('글꼴 바꿈', dict(n), '| 남은 다른 글꼴', left)
    prs.save(str(dst))
    n_main = len(main_)
    print('조립', len(order), '장 (본편 %d, 부록 %d, 참고 %d) →' % (n_main, len(appx), len(refs)), dst)

    # 4. 영상(PowerPoint)
    add_media(dst, 1, order.index(info) + 1, a.embed_fonts)

    # 문구 변경 목록: 표시 줄 아래를 이번 빌드의 표로 바꾼다(위쪽은 손으로 적은 내용)
    lst, mark = HERE / '문구_변경목록.md', '<!-- 아래 표는 build_deck.py가 적음 -->'
    head = lst.read_text(encoding='utf-8').split(mark)[0] if lst.exists() else '# 문구 변경 목록\n\n'
    lst.write_text(head + mark + '\n\n| 장 | 이전 | 새 문구 |\n|---|---|---|\n' + ''.join('| %s |\n' % ' | '.join(str(x).replace('|', '\\|').replace('\n', ' ') for x in c) for c in change_log), encoding='utf-8')

    # 5. 확인용 PNG
    if not a.no_png:
        od = HERE / ('png' if dst == DST else 'png_' + dst.stem)
        render2.png(dst, od, 1600, 900)
        labels = []
        for i in range(len(order)):
            part = '본편' if i < n_main else ('부록' if i < n_main + len(appx) else '참고')
            labels.append('%d  %s' % (i + 1, part))
        sh = HERE / ('한눈에.png' if dst == DST else '한눈에_%s.png' % dst.stem)
        sheet(sorted(od.glob('s*.png')), sh, labels)
        print('한눈에 →', sh)


if __name__ == '__main__':
    main()
