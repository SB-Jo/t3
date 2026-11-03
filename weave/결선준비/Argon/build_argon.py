#!/usr/bin/env python3
"""Argon 폴더에 고도화된 결선 PPTX 6종 생성 스크립트.

원본(01_최종제출본, 02_PPT/Weave_결선.pptx, 02_PPT/Weave_결선_중간본.pptx)은 전혀 수정하지 않고,
/home/jaeung/samsung/t3/weave/결선준비/Argon/ 폴더 안에 다음 6개의 PPTX를 생성합니다:

1. Weave_결선_Argon_와인고도화.pptx        (35장 전체 결선 덱 — 표지 루프 영상 + 인트로 79초 영상 보존 + 와인 고도화 + 전 장표 문체 교정)
2. Weave_결선_Argon_병원교체안.pptx        (35장 전체 결선 덱 — 표지 루프 영상 + 인트로 79초 영상 보존 + 도수치료 병원 교체안 + 전 장표 문체 교정)
3. HIW_UX1_통합검색_A사요청자료_고도화.pptx  (단독 How it Works 13장 — A사 유럽 배터리 안전성 성적서)
4. HIW_UX2A_자동완성_집들이와인_고도화.pptx  (단독 How it Works 12장 — 집들이 와인 00판 고도화)
5. HIW_UX2B_자동완성_도수치료병원_신규.pptx  (단독 How it Works 12장 — 현우 선배 추천 도수치료 병원 00판)
6. HIW_UX3_먼저건네기_면세점갈색병_고도화.pptx (단독 How it Works 13장 — 출장길 인천공항 면세점 갈색병 00판)
"""
import copy
import importlib
import sys
from pathlib import Path

from pptx import Presentation

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HIW_DIR = ROOT / '09_HowItWorks' / '장표5'
MID_DIR = ROOT / '11_중간본'

#argon_scene5를 scene5로 우선 로드하도록 설정
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'specs'))
sys.path.insert(0, str(HIW_DIR))
sys.path.insert(0, str(MID_DIR))

import argon_scene5 as scene5  # noqa: E402
sys.modules['scene5'] = scene5
import build5                  # noqa: E402
import samsung_fonts           # noqa: E402
import story as S              # noqa: E402
from hiw_lib import q          # noqa: E402

BASE_DECK = ROOT / '02_PPT' / 'Weave_결선_중간본.pptx'


def walk_shapes(shapes):
    for sh in shapes:
        if sh.shape_type == 6:  # GROUP
            yield from walk_shapes(sh.shapes)
        elif sh.has_text_frame:
            yield sh


def set_shape_text(sh, new_text, min_w_px=None):
    """문단·런의 첫 번째 서식(글꼴 크기, 굵기, 색상, 줄간격, 정렬)을 유지하며 텍스트만 교체."""
    tf = sh.text_frame
    lines = new_text.split('\n')
    p0 = tf.paragraphs[0]
    r0_pPr = copy.deepcopy(p0._p.find(q('a:pPr')))
    r0_rPr = copy.deepcopy(p0.runs[0]._r.find(q('a:rPr'))) if p0.runs else None

    # 기존 문단 모두 비우기 (첫 문단만 남기고 제거)
    for p in list(tf.paragraphs)[1:]:
        p._p.getparent().remove(p._p)
    for r in list(p0.runs):
        r._r.getparent().remove(r._r)
    for br in list(p0._p.findall(q('a:br'))):
        p0._p.remove(br)

    for idx, ln in enumerate(lines):
        p = p0 if idx == 0 else tf.add_paragraph()
        if idx > 0 and r0_pPr is not None:
            old_pPr = p._p.find(q('a:pPr'))
            if old_pPr is not None:
                p._p.remove(old_pPr)
            p._p.insert(0, copy.deepcopy(r0_pPr))
        run = p.add_run()
        run.text = ln
        if r0_rPr is not None:
            old_rPr = run._r.find(q('a:rPr'))
            if old_rPr is not None:
                run._r.remove(old_rPr)
            run._r.insert(0, copy.deepcopy(r0_rPr))

    if min_w_px is not None:
        target_emu = int(min_w_px * 9525)
        if sh.width < target_emu:
            sh.width = target_emu


def find_by_name(slide, name):
    return [sh for sh in walk_shapes(slide.shapes) if sh.name == name]


def set_notes(slide, text, note_tpl):
    ns = slide.notes_slide
    if ns.notes_text_frame is None:
        for e in note_tpl:
            ns.shapes._spTree.append(copy.deepcopy(e))
    ns.notes_text_frame.text = text


def reorder_slides(prs, order):
    lst = prs.slides._sldIdLst
    by_part = {prs.part.related_part(e.get(q('r:id'))): e for e in list(lst)}
    assert len(order) == len(by_part) == len(set(id(s) for s in order)), (len(order), len(by_part))
    for e in list(lst):
        lst.remove(e)
    for s in order:
        lst.append(by_part[s.part])


def apply_copywriting_upgrades(prs, note_tpl, variant='wine'):
    """Weave_결선_중간본.pptx의 본편·부록 장표(2, 3, 5, 18~24, 26~27) 문체·정합성 일괄 고도화."""
    slides = list(prs.slides)

    # 1. Slide 1 (Cover) 발표자 노트 다듬기
    if variant == 'hospital':
        set_notes(
            slides[0],
            '표지(반복 영상). 안녕하십니까, 흩어진 기억을 엮어 지금을 완성하는 온디바이스 AI, Weave Assist 발표를 맡은 발표자입니다. '
            '본 덱은 UX 2를 현우 선배 추천 도수치료 병원(바른마디 마취통증의학과) 시나리오로 구성한 Argon 교체안입니다.',
            note_tpl,
        )
    else:
        set_notes(
            slides[0],
            '표지(반복 영상). 안녕하십니까, 흩어진 기억을 엮어 지금을 완성하는 온디바이스 AI, Weave Assist 발표를 맡은 발표자입니다. '
            '구글 검색창에 집들이 때 마신 화이트 와인을 적고 실타래 버튼을 누르면 지은의 카톡과 그날 사진이 보라색 실로 이어져 배비치 소비뇽 블랑을 건네는 장면이 반복됩니다.',
            note_tpl,
        )

    # 2. Slide 2 (Motivation)
    s2 = slides[1]
    taglines = [sh for sh in walk_shapes(s2.shapes) if sh.name == 'Phone tagline']
    if len(taglines) >= 2:
        set_shape_text(
            taglines[0],
            '내 휴대폰 안에는 이미 모든 답이 들어 있습니다.\n여러 앱에 흩어져 있을 뿐, 사라진 건 아니니까요.',
        )
        set_shape_text(
            taglines[1],
            '대화도, 사진도, 메모도 분명 다 남아 있는데\n막상 꺼내 쓰려면 여전히 내가 직접 앱을 뒤져야 합니다.',
        )
    set_notes(
        s2,
        '우리는 매일 카카오톡, 갤러리, 삼성노트, 이메일에 수많은 기록을 남깁니다. '
        '휴대폰 안에는 이미 내가 찾는 모든 답이 들어 있습니다. 여러 앱에 흩어져 있을 뿐 사라진 건 아니니까요. '
        '하지만 대화도, 사진도, 메모도 분명 다 남아 있는데 막상 꺼내 쓰려면 여전히 사용자가 직접 앱을 하나씩 뒤져야 합니다.',
        note_tpl,
    )

    # 3. Slide 3 (Pain Points)
    s3 = slides[2]
    s3_replacements = {
        '그 어디에 있더라?': '어느 앱에 있더라?',
        '찾을 내용은 알지만, 어느 앱에 있는지 모릅니다.': '찾으려는 내용은 알지만, 어느 앱에 남겼는지 헷갈립니다.',
        '노트, 메일, 대화내역을 하나씩 확인합니다.': '노트, 메일, 대화 내역을 하나씩 열어보며 확인합니다.',
        '정확한 이름이 떠오르지 않아, 검색부터 막힙니다.': '상황만 어렴풋이 기억나고 정확한 이름이 안 떠올라 막힙니다.',
        '필요한 순간에도, 그런 기억이 있었는지 떠오르지 않습니다.': '정작 필요한 순간에는 그런 기억이 있었는지조차 잊어버립니다.',
    }
    for sh in walk_shapes(s3.shapes):
        txt = sh.text_frame.text.strip()
        if txt in s3_replacements:
            set_shape_text(sh, s3_replacements[txt], min_w_px=sh.width / 9525 + 24)
    set_notes(
        s3,
        '일상에서 기억을 꺼내 쓰려 할 때 우리는 세 가지 벽에 부딪힙니다. '
        '첫째, 어느 앱에 있더라? 지난주 미팅 때 요청받은 자료처럼 찾을 내용은 알지만 노트에 적었는지 메일로 받았는지 헷갈려 앱을 하나씩 열어봅니다. '
        '둘째, 이름이 뭐였더라? 상황만 어렴풋이 기억나고 정확한 이름이 떠오르지 않아 검색창 앞에서부터 막힙니다. '
        '셋째, 아 맞다, 깜빡했다! 아내가 출장길 면세점에서 사다 달라던 화장품처럼 정작 필요한 순간에는 그런 부탁이 있었는지조차 잊어버립니다.',
        note_tpl,
    )

    # 4. Slide 5 (Solution: Weave Assist)
    s5 = slides[4]
    s5_map = {
        'Header subtitle': ('여러 앱에 흩어진 기록을 하나로 엮어, 지금 쓰는 화면 위로 바로 건네는 온디바이스 AI', 1280),
        'Weave text 5': ('여러 앱에 흩어진 같은 일의 기록을 한눈에 엮어 보여줍니다.', 405),
        'Weave text 9': ('A사: 유럽 배터리 인증 요청', 165),
        'Weave text 10': ('→ 민수 수석님이 성적서 정리', 165),
        'Weave text 17': ('EU_Safety_Report.pdf', 155),
        'Weave text 18': ('메일 · 민수 수석 · 10월 30일', 155),
        'Weave text 25': ('정확한 이름이 안 떠올라도, 기억나는 상황만으로 찾아줍니다.', 395),
        'Weave text 35': ('미처 못 챙긴 약속과 부탁도, 필요한 순간에 먼저 알려줍니다.', 385),
    }
    if variant == 'hospital':
        s5_map.update({
            'Weave text 26': ('현우 선배 추천 도수치료 병원', 172),
            'Weave text 29': ('바른마디 통증의학과', 195),
            'Weave text 30': ('카카오톡 · 현우 선배 ‘역삼역 수기 교정’ 10/14', 242),
            'Weave text 31': ('갤러리 · 네이버 지도 캡처 10월 14일 12:34', 232),
        })
    for name, (new_txt, min_w) in s5_map.items():
        for sh in find_by_name(s5, name):
            set_shape_text(sh, new_txt, min_w_px=min_w)

    if variant == 'hospital':
        set_notes(
            s5,
            '이 세 가지 불편을 해결하는 Weave Assist의 핵심 UX 세 가지입니다. '
            '첫째, 기록 통합 검색입니다. 카톡에서 A사 요청 자료를 질문받았을 때 키보드 실타래 버튼을 올리면 삼성노트 회의록과 민수 수석님의 영문 성적서 메일을 한눈에 엮어 보여줍니다. '
            '둘째, 단서로 찾는 기억입니다. 현우 선배가 추천한 도수치료 병원처럼 정확한 이름이 기억나지 않아도 카톡 대화와 네이버 지도 캡처를 연결해 바른마디 마취통증의학과를 바로 찾아줍니다. '
            '셋째, 먼저 건네는 기억입니다. 출장길 인천공항 면세구역에 들어서면 아내가 부탁했던 갈색병 카톡과 면세점 상품 캡처를 엮어 먼저 알려줍니다.',
            note_tpl,
        )
    else:
        set_notes(
            s5,
            '이 세 가지 불편을 해결하는 Weave Assist의 핵심 UX 세 가지입니다. '
            '첫째, 기록 통합 검색입니다. 카톡에서 A사 요청 자료를 질문받았을 때 키보드 실타래 버튼을 올리면 삼성노트 회의록과 민수 수석님의 영문 성적서 메일을 한눈에 엮어 보여줍니다. '
            '둘째, 단서로 찾는 기억입니다. 집들이 때 마신 화이트 와인처럼 정확한 이름이 기억나지 않아도 지은의 카톡 약속과 그날 찍은 라벨 사진을 연결해 배비치 소비뇽 블랑을 바로 찾아줍니다. '
            '셋째, 먼저 건네는 기억입니다. 출장길 인천공항 면세구역에 들어서면 아내가 부탁했던 갈색병 카톡과 면세점 상품 캡처를 엮어 먼저 알려줍니다.',
            note_tpl,
        )

    # 5. Slide 18 (Why Samsung)
    s18 = slides[17]
    for sh in find_by_name(s18, 'Text 18'):
        set_shape_text(
            sh,
            '여러 앱에 흩어진 일상 데이터를 삼성 PDE와 연계해\n기기 안에서 통합 이해하고, 나에게 꼭 맞는 기억 경험을 제공합니다',
        )
    for sh in find_by_name(s18, 'Text 23'):
        set_shape_text(
            sh,
            '개인의 모든 기억과 색인 데이터는 KEEP 및 Knox Vault로 기기 내부에 암호화 보호되어, 외부 유출 걱정 없이 안심하고 쓸 수 있습니다',
        )
    for sh in find_by_name(s18, 'Text 24'):
        set_shape_text(sh, '오직 갤럭시\n안에서!')
    set_notes(
        s18,
        '왜 이 기술이 삼성 갤럭시여야 할까요? '
        '첫째, 여러 앱을 아우르는 시스템 레벨 접근성입니다. 개별 서드파티 앱은 다른 앱의 기록에 접근할 수 없지만, 갤럭시는 삼성 키보드라는 공통 접점 위에서 모든 앱의 맥락을 하나로 이을 수 있습니다. '
        '둘째, Personal Data Engine과의 시너지입니다. 사용자의 선호와 패턴을 이해하는 PDE 위에 구체적인 에피소드 기억을 연쇄 탐색하는 Weave가 더해져 초개인화 경험이 완성됩니다. '
        '셋째, 타협 없는 온디바이스 보안입니다. 가장 사적인 대화와 사진을 다루는 만큼, KEEP과 Knox Vault 기반 암호화로 외부 서버 유출 걱정 없이 오직 갤럭시 안에서 안전하게 동작합니다.',
        note_tpl,
    )

    # 6. Slide 19 (Why Now)
    s19 = slides[18]
    for sh in find_by_name(s19, 'Text 26'):
        set_shape_text(
            sh,
            '기록을 저장하는 기술은 이미 충분합니다.\n이제는 쌓인 기록을 필요한 순간에 꺼내 쓰는 경험에 집중할 때입니다.',
        )
    for sh in find_by_name(s19, 'Text 27'):
        set_shape_text(sh, '지금,\n가능합니다!')
    set_notes(
        s19,
        '왜 지금이어야 할까요? 첫째, 갤럭시 NPU와 온디바이스 추론형 임베딩 기술의 성숙으로, 과거 서버에서만 가능했던 멀티홉 추론 검색이 이제 모바일 기기 안에서 빠르게 돌아갑니다. '
        '둘째, 삼성 키보드와 Knox 보안 인프라가 이미 준비되어 있습니다. '
        '셋째, AI 에이전트 시장의 화두가 단순 요약·저장에서 장기 기억 활용으로 이동하고 있습니다. 쌓인 기록을 필요한 순간에 꺼내 쓰는 경험, 지금 바로 가능합니다.',
        note_tpl,
    )

    # 7. Slide 20 (차별화 포인트)
    s20 = slides[19]
    for sh in find_by_name(s20, 'Header subtitle'):
        set_shape_text(
            sh,
            '단일 앱이나 단편적인 안내에 머물던 기존 AI를 넘어, 기기 전체의 기록을 입체적으로 엮어내는 유일한 온디바이스 AI입니다.',
            min_w_px=1280,
        )
    set_notes(
        s20,
        '기존 서비스들과 비교하면 Weave의 차별점이 더욱 분명해집니다. '
        '단일 앱 안의 키워드 검색이나 사진만 찾는 기능, 혹은 정해진 일정 브리핑에 머물던 기존 AI와 달리, '
        'Weave는 카톡·갤러리·노트·메일·월렛 등 기기 전체의 멀티모달 기록을 연쇄 추론으로 엮어 지금 쓰는 키보드 위로 즉시 건네줍니다.',
        note_tpl,
    )

    # 8. Slide 21 (기대효과 1: 시간 절감)
    s21 = slides[20]
    for sh in find_by_name(s21, 'Text 11'):
        set_shape_text(sh, '직장인이 하루 평균 여러 앱에 흩어진\n정보를 찾느라 흘려보내는 시간, 59분')
    for sh in find_by_name(s21, 'Text 16'):
        set_shape_text(sh, '메모·카톡·갤러리를 번갈아 열며 스크롤을 올리고,\n오래된 대화와 사진을 일일이 뒤지던 과정을 줄입니다.')
    for sh in find_by_name(s21, 'Text 18'):
        set_shape_text(sh, '쓰던 키보드에서 필요한 내용을 바로 제안받고,\n여러 앱에 흩어진 기록을 한 번에 찾습니다.')
    set_notes(
        s21,
        '기대효과 첫 번째는 탐색 시간의 획기적인 단축입니다. '
        '직장인이 하루 평균 여러 앱에 흩어진 정보를 찾느라 흘려보내는 시간이 59분에 달합니다. '
        '메모장, 카톡, 갤러리를 번갈아 열며 끝없이 스크롤을 올리던 시간을 줄이고, 쓰던 키보드 위에서 단 몇 초 만에 필요한 기억을 바로 꺼내 쓸 수 있습니다.',
        note_tpl,
    )

    # 9. Slide 22 (기대효과 2: 관계의 디테일 - '무화과시루' 잔재 완전 제거!)
    s22 = slides[21]
    for sh in find_by_name(s22, 'Text 16'):
        if variant == 'hospital':
            set_shape_text(
                sh,
                '아내가 지나가듯 말했던 면세점 갈색병이,\n현우 선배가 추천해 준 역삼역 도수치료 병원이\n꼭 필요한 순간에 떠오릅니다.',
            )
        else:
            set_shape_text(
                sh,
                '아내가 지나가듯 말했던 면세점 갈색병이,\n친구가 집들이 때 내어준 소비뇽 블랑이\n꼭 필요한 순간에 떠오릅니다.',
            )
    set_notes(
        s22,
        '두 번째 기대효과는 일상의 세심한 배려와 관계의 완성입니다. '
        '아내가 지나가듯 말했던 면세점 갈색병 50ml, 지인이 추천해 주었던 소중한 기억이 꼭 필요한 순간에 먼저 떠올라 소중한 사람들과의 관계를 더욱 깊게 만들어 줍니다.',
        note_tpl,
    )

    # 10. Slide 23 (기대효과 3: 갤럭시 락인)
    s23 = slides[22]
    for sh in find_by_name(s23, 'Text 21'):
        set_shape_text(
            sh,
            "갤럭시를 오래 쓸수록 나를 가장 잘 아는 기억 자산이 깊어지며,\n사용자는 '내 기록을 가장 잘 활용해 주는 갤럭시'의\n대체 불가능한 가치를 경험합니다.",
        )
    set_notes(
        s23,
        '세 번째 기대효과는 강력한 갤럭시 생태계 락인입니다. '
        '갤럭시를 오래 쓸수록 기기 안에 축적된 기억의 연결망이 깊어지고, 사용자는 내 기억을 가장 잘 이해하고 챙겨주는 갤럭시만의 대체 불가능한 가치를 경험하게 됩니다.',
        note_tpl,
    )

    # 11. Slide 24 (END / 팀원 소개 — 표지 소속팀 통일 + 온라인 투표 문구 제거!)
    s24 = slides[23]
    for sh in find_by_name(s24, 'Shape 9'):
        set_shape_text(sh, 'AI System Team', min_w_px=130)
    for sh in find_by_name(s24, 'Shape 12'):
        set_shape_text(sh, 'AI Core Team', min_w_px=120)
    for sh in find_by_name(s24, 'Shape 19'):
        set_shape_text(sh, '경청해 주셔서 감사합니다!')
    for sh in find_by_name(s24, 'Shape 20'):
        set_shape_text(sh, '흩어진 기억을 엮어, 지금을 완성하는 Weave Assist였습니다.')
    set_notes(
        s24,
        '지금까지 여러 앱에 흩어진 기억을 하나로 엮어 지금을 완성하는 온디바이스 AI, Weave Assist였습니다. 경청해 주셔서 감사합니다.',
        note_tpl,
    )

    # 12. Slide 26 (Appendix Q&A 1)
    s26 = slides[25]
    for sh in find_by_name(s26, 'Weave text 6'):
        set_shape_text(
            sh,
            '사용자가 알림 접근을 허용하면 새로 도착하는 메시지 텍스트를 기기 안에 안전하게 색인합니다.\n이전 대화나 내가 보낸 메시지는 카카오톡 ‘대화 내용 내보내기’로 손쉽게 가져올 수 있습니다.',
        )
    for sh in find_by_name(s26, 'Weave text 12'):
        set_shape_text(
            sh,
            '무거운 색인 작업은 충전 중이나 유휴 시간에 미리 끝내 두고, 사용 중에는 가벼운 검색만 수행합니다.\n1차 탐색은 경량 임베딩 모델이 맡고 언어모델(LLM)은 최종 문장 정리만 담당해 배터리와 발열 부담을 최소화합니다.',
        )
    for sh in find_by_name(s26, 'Weave text 18'):
        set_shape_text(
            sh,
            '사용자가 허용한 앱의 기록만 기기 안에서 처리하며, 외부 서버로는 어떠한 원본 데이터도 전송하지 않습니다.\n모든 제안에는 원문 출처를 함께 표시하고, 사용자가 직접 확인해 선택한 내용만 입력창에 반영됩니다.',
        )

    # 13. Slide 27 (Appendix Q&A 2 — 구버전 '탐색 메모' 잔재 완전 제거!)
    s27 = slides[26]
    for sh in find_by_name(s27, 'Weave text 46'):
        set_shape_text(
            sh,
            '복합 질문을 하위 질문으로 나누고(Query Rewriting), 1차 탐색에서 찾은 단서(날짜·담당자·특징)를\n빈칸에 채워 두 번째 질문을 완성한 뒤 다음 근거를 연쇄 탐색합니다.',
        )
    if variant == 'hospital':
        for sh in find_by_name(s27, 'Weave text 10'):
            set_shape_text(sh, '현우 선배 카톡', min_w_px=110)
        for sh in find_by_name(s27, 'Weave text 11'):
            set_shape_text(sh, '네이버 지도 캡처', min_w_px=110)
        for sh in find_by_name(s27, 'Weave text 51'):
            set_shape_text(sh, '현우 카톡 · 10/14', min_w_px=115)
        for sh in find_by_name(s27, 'Weave text 53'):
            set_shape_text(sh, '질문+10/14', min_w_px=68)
        for sh in find_by_name(s27, 'Weave text 54'):
            set_shape_text(sh, '바른마디', min_w_px=68)
    else:
        for sh in find_by_name(s27, 'Weave text 10'):
            set_shape_text(sh, '지은 카톡 약속', min_w_px=110)
        for sh in find_by_name(s27, 'Weave text 51'):
            set_shape_text(sh, '지은 카톡 · 3/15', min_w_px=115)


def build_standalone_hiw(spec_mod_name):
    mod = importlib.import_module(spec_mod_name)
    spec = copy.deepcopy(mod.SPEC)
    # 단독 HIW 파일에서는 result 장표까지 모두 포함해서 전체 흐름을 볼 수 있게 함
    spec.pop('skip', None)
    sc = scene5.build(spec)
    dst = HERE / f"{spec['file']}.pptx"
    n_slides, warns = build5.render(sc, dst)
    print(f"[Standalone HIW] {dst.name}: {n_slides}장 생성 (경고 {len(warns)}건)")
    for w in warns:
        print("   !", w)
    return dst


def build_full_deck(spec_mod_name, out_name, variant='wine'):
    prs = Presentation(str(BASE_DECK))
    orig = list(prs.slides)
    assert len(orig) == 35, f"Expected 35 slides in {BASE_DECK}, got {len(orig)}"

    layout = orig[5].slide_layout
    note_tpl = [copy.deepcopy(sh._element) for sh in orig[5].notes_slide.placeholders]

    # 1. 새 How it Works 슬라이드 생성 (12장, result 제외)
    mod = importlib.import_module(spec_mod_name)
    spec = copy.deepcopy(mod.SPEC)
    spec['skip'] = ['result']
    sc = scene5.build(spec)
    hiw_slides, warns = build5.add_steps(prs, sc, layout, note_tpl)
    S.morph_transition(hiw_slides[0], 1000)

    # 2. 기존 How it Works 12장(orig[5:17]) 제거 및 새 hiw_slides로 교체
    lst = prs.slides._sldIdLst
    by_part = {prs.part.related_part(e.get(q('r:id'))): e for e in list(lst)}
    for old_s in orig[5:17]:
        e = by_part[old_s.part]
        prs.part.drop_rel(e.get(q('r:id')))
        lst.remove(e)

    new_order = orig[:5] + hiw_slides + orig[17:]
    reorder_slides(prs, new_order)

    # 3. 전 장표 문체·시나리오 정합성 교정
    apply_copywriting_upgrades(prs, note_tpl, variant=variant)

    # 4. 삼성 폰트 일괄 매핑 및 저장
    samsung_fonts.remap_prs(prs)
    dst = HERE / out_name
    prs.save(str(dst))
    print(f"[Full Deck] {dst.name}: {len(new_order)}장 생성 완료 (경고 {len(warns)}건)")
    for w in warns:
        print("   !", w)
    return dst


def main():
    print("=== Argon PPTX 생성 시작 ===")
    # 1. 단독 How it Works 4종 생성
    build_standalone_hiw('ux1_company')
    build_standalone_hiw('ux2_wine')
    build_standalone_hiw('ux2_hospital')
    build_standalone_hiw('ux3_bottle')

    # 2. 결선 전체 35장 덱 2종 생성 (와인 고도화본 / 도수치료 병원 교체안)
    build_full_deck('ux2_wine', 'Weave_결선_Argon_와인고도화.pptx', variant='wine')
    build_full_deck('ux2_hospital', 'Weave_결선_Argon_병원교체안.pptx', variant='hospital')
    print("=== Argon PPTX 6종 생성 완료 ===")


if __name__ == '__main__':
    main()
