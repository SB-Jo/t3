"""0927_v1 덱 4차 다듬기 (2026-09-27 21시 반 요청): 6~8쪽 USER SCENARIO 새 구성 + 9쪽 제목의 'Weave' 보라.

6~8쪽 원본은 p68/page-0N.html → render.cjs → p68/out/page-0N.{art.png,layout.json}.
장표의 도형을 모두 지우고 [공통 배경 3장 → 그래픽 레이어 1장 → 글자 상자]로 다시 채움(build_pptx.fill_slide).
글자 상자는 영문 조각 Inter, 한글 조각 Noto Sans KR로 나누고, 머리(칩·제목·부제)는 header.py 규격.

사용: python apply_round4.py --test | --deck (백업 5와 같을 때만)
"""
import copy
import hashlib
import sys
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

import apply_round2 as r2
import apply_round3 as r3
import header as hd
import pages_p2_p4 as pg

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '5_4차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round4.pptx')
P68 = ROOT / 'p68'

NOTES = {
    6: """USER SCENARIO 1 — 기록 통합 검색
① 성빈은 버즈로 재웅 선배와 통화하다가, 어제 정한 A사 시연 순서와 오늘 집합 시간을 요청받습니다. 노트에 적었는지 메일에 적었는지 바로 떠오르지 않습니다.
② 통화 화면 아래 Weave 버튼을 위로 밀어 올리고 '어제 A사 시연 준비'를 입력합니다. 통화 내용은 AI가 듣지 않고, 사용자가 직접 검색어를 입력합니다.
③ 삼성노트·메일·카카오톡 나와의 채팅에 흩어진 기록이 출처와 함께 한 번에 나옵니다.
④ 성빈은 통화를 끊지 않고 목록을 보며 바로 답합니다.""",
    7: """USER SCENARIO 2 — 단서로 찾는 기억
① 지은이네 집들이 때 마신 와인을 다시 찾고 싶지만, 이름이 떠오르지 않습니다.
② Google 검색창에 기억나는 대로 '지은이네 집들이 때 먹었던 와인'을 입력하고 키보드의 실타래 버튼을 누릅니다.
③ Weave가 캘린더에서 집들이 날짜(3월 15일 18:00)를 찾고, 그 시간 갤러리 사진 속 와인 라벨 글자(BABICH SAUVIGNON BLANC)를 읽어 '배비치 소비뇽 블랑'을 추천합니다.
④ 출처를 확인하고 입력하기를 누르면, 검색창이 정확한 이름으로 바뀝니다.""",
    8: """USER SCENARIO 3 — 먼저 건네는 기억
① 대전 출장을 마친 지현은 역에서 엄마와 대화 중입니다. 2주 전 가족 단체방에서 무화과시루를 사다 주겠다고 한 약속은 떠올리지 못합니다.
② 답장을 쓰려는 순간, 키보드의 실타래 버튼이 먼저 반짝입니다.
③ Weave가 2주 전 약속과 지금 위치(대전역, 성심당 대전역점 인근)를 이어 '엄마, 전에 먹고 싶다던 무화과시루 사갈까?'를 추천합니다.
④ 입력하기를 누르면 문장이 입력창에 들어가고, 보낼지는 사용자가 정합니다. 엄마는 그 말을 기억해 준 데 감동합니다.""",
}
HEADERS = {6: 'USER SCENARIO 1', 7: 'USER SCENARIO 2', 8: 'USER SCENARIO 3'}
NOTO_OF = {'Inter': 'Noto Sans KR', 'Inter SemiBold': 'Noto Sans KR SemiBold',
           'Noto Sans KR': 'Noto Sans KR', 'Noto Sans KR SemiBold': 'Noto Sans KR SemiBold'}
INTER_OF = {'Inter': 'Inter', 'Inter SemiBold': 'Inter SemiBold', 'Noto Sans KR': 'Inter', 'Noto Sans KR SemiBold': 'Inter SemiBold'}


def split_fonts(slide):
    """새 글자 상자의 조각을 문자 종류로 나눔: 영문·숫자 → Inter 계열(ea·cs도), 한글 → latin Inter / ea·cs Noto Sans KR."""
    for sh in slide.shapes:
        if not (sh.has_text_frame and sh.name.startswith('Weave text')):
            continue
        for p in sh.text_frame._txBody.findall(qn('a:p')):
            prev = 'ko'
            for r in list(p.findall(qn('a:r'))):
                rPr = r.find(qn('a:rPr'))
                face = rPr.find(qn('a:latin')).get('typeface')
                if face not in NOTO_OF:
                    continue                                   # Nanum Pen Script 등은 그대로
                for seg, cls in hd.split_script(r.find(qn('a:t')).text, prev):
                    prev = cls
                    nr = copy.deepcopy(r)
                    nrPr = nr.find(qn('a:rPr'))
                    nr.find(qn('a:t')).text = seg
                    for k in ('lang', 'altLang'):
                        nrPr.attrib.pop(k, None)
                    nrPr.set('lang', 'en-US' if cls == 'latin' else 'ko-KR')
                    if cls != 'latin':
                        nrPr.set('altLang', 'en-US')
                    lat = INTER_OF[face]
                    r2.set_fonts(nrPr, lat, lat if cls == 'latin' else NOTO_OF[face])
                    r.addprevious(nr)
                p.remove(r)


def scenario(prs, n, slide, bg):
    r3.ensure_notes_body(prs, slide)
    r3.bp.OUT = P68 / 'out'
    r3.bp.fill_slide(slide, f'page-0{n}', bg, NOTES[n])
    split_fonts(slide)
    names = {HEADERS[n]: 'Header chip'}
    texts = [sh for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    chip = [sh for sh in texts if sh.text_frame.text.strip() == HEADERS[n]]
    assert len(chip) == 1
    chip[0].name = 'Header chip'
    tops = sorted((sh for sh in texts if sh is not chip[0] and (sh.top or 0) / 9525 < 150), key=lambda s: s.top)
    assert len(tops) == 2, [t.text_frame.text for t in tops]
    tops[0].name, tops[1].name = 'Header title', 'Header subtitle'
    pg.drop_unused_images(slide)
    return hd.apply(slide)


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    labels = r2.labels(prs)
    assert labels[5:9] == ['USER SCENARIO 1', 'USER SCENARIO 2', 'USER SCENARIO 3', 'HOW IT WORKS'], labels
    bg = r2.background_from(prs)
    for n in (6, 7, 8):
        r = scenario(prs, n, slides[n - 1], bg)
        print(n, r['chip'], f"({r['chip_w']}px)", '|', r['title'], '|', r.get('sub', ''))
    r = hd.apply(slides[8], title_runs=[('Weave', '6B4EFF'), ('는 어떻게 ', None), ('기억을 엮을까요', '6B4EFF'), ('?', None)])
    print(9, r['chip'], '|', r['title'])
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        apply(BACKUP, TEST_OUT)
