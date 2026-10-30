"""0927_v1 덱 5차 다듬기 (2026-09-27 21시 40분 요청).

- 5쪽: 다시 구성(p05/page-05-solution.html 5차) — 제목 'Weave' 보라, 부제 '여러 앱에 흩어진 기억을 엮어, …',
       번호·기능 이름·한 줄 설명 크게, 번호에 입체감, (1) 휴대폰 안 UI + 노트 카드 + 메일·카카오 아이콘,
       (2) 캘린더·갤러리 시나리오(와인), (3) 추천 문장 + 입력하기, 누르는 곳마다 손 + 반짝임
- 9쪽: 제목 'Weave' 보라 — 4차에서 이미 반영됨(확인만)
- 10쪽: '갤러리 · 삼성노트 · 캘린더' → '… 등'
- 11쪽(요청서의 [12p] 항목 — 모두 11쪽 WHY NOW에 있는 문구): '이미지 이해 · 요약 등', 'Samsung Gauss Series',
       '흩어진 기록을 엮어, 지금의 입력에 연결', '이제, 기기 안에서 꺼내는 과정에 집중할 때입니다.'(가운데 구절 보라)

사용: python apply_round5.py --test | --deck (백업 6과 같을 때만)
"""
import hashlib
import sys
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

import apply_round2 as r2
import apply_round3 as r3
import apply_round4 as r4
import header as hd
import pages_p2_p4 as pg
from textmeasure import width

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '6_5차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round5.pptx')
shape, xywh, put, set_text, no_autofit = r2.shape, r2.xywh, r2.put, r2.set_text, r2.no_autofit
PURPLE, INK = '6B4EFF', '1C1A24'


def p5(prs, slide, bg):
    r3.ensure_notes_body(prs, slide)
    r3.bp.OUT = ROOT / 'p05' / 'out'
    r3.bp.fill_slide(slide, 'page-05-solution', bg, (ROOT / 'p05' / 'notes-page-05.txt').read_text(encoding='utf-8').strip())
    r4.split_fonts(slide)
    texts = [sh for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    chip = [sh for sh in texts if sh.text_frame.text.strip() == 'SOLUTION: WEAVE ASSIST']
    assert len(chip) == 1
    chip[0].name = 'Header chip'
    tops = sorted((sh for sh in texts if sh is not chip[0] and (sh.top or 0) / 9525 < 150), key=lambda s: s.top)
    assert [t.text_frame.text for t in tops] == ['Weave의 핵심 UX 3가지를 소개합니다!', '여러 앱에 흩어진 기억을 엮어, 필요한 순간 건네는 온디바이스 AI'], [t.text_frame.text for t in tops]
    tops[0].name, tops[1].name = 'Header title', 'Header subtitle'
    pg.drop_unused_images(slide)
    return hd.apply(slide, title_runs=[('Weave', '6666FF'), ('의 ', None), ('핵심 UX 3가지', '6666FF'), ('를 소개합니다!', None)])


def check_p9(slide):
    t = shape(slide, name='Header title')
    runs = [(r.find(qn('a:t')).text, r.find(qn('a:rPr')).find(qn('a:solidFill'))[0].get('val')) for r in t._element.iter(qn('a:r'))]
    assert runs[0] == ('Weave', PURPLE), runs
    return runs


def p10(slide):
    t = shape(slide, name='Text 7')
    assert t.text_frame.text == '갤러리 · 삼성노트 · 캘린더'
    x, y, w, h = xywh(t)
    cx = x + w / 2
    set_text(t, [[('갤러리 · 삼성노트 · 캘린더 등', None, None)]])
    no_autofit(t, algn='ctr')
    nw = w + 24
    put(t, x=cx - nw / 2, w=nw)


def p11(slide):
    t = shape(slide, sid=21); assert t.text_frame.text == '이미지 이해 · 요약'
    set_text(t, [[('이미지 이해 · 요약 등', None, None)]]); no_autofit(t)
    t = shape(slide, sid=25); assert t.text_frame.text == 'Samsung Gauss'
    set_text(t, [[('Samsung Gauss Series', None, None)]]); no_autofit(t)
    t = shape(slide, sid=35); assert t.text_frame.text == '남은 기록을 찾아, 지금의 입력에 연결'
    set_text(t, [[('흩어진 기록을 엮어, 지금의 입력에 연결', None, None)]]); no_autofit(t)
    t = shape(slide, sid=36)
    assert t.text_frame.text.replace('\n', ' / ').startswith('기록은 이미 충분합니다.'), t.text_frame.text
    set_text(t, [[('기록은 이미 충분합니다.', INK, True)],
                 [('이제, ', INK, True), ('기기 안에서 꺼내는 과정', PURPLE, True), ('에 집중할 때입니다.', INK, True)]])
    no_autofit(t)


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    labels = r2.labels(prs)
    assert [labels[i] for i in (4, 8, 9, 10)] == ['SOLUTION: WEAVE ASSIST', 'HOW IT WORKS', 'WHY SAMSUNG', 'WHY NOW'], labels
    bg = r2.background_from(prs)
    r = p5(prs, slides[4], bg)
    print(5, r['chip'], '|', r['title'], '|', r.get('sub', ''))
    print(9, 'title runs (already purple):', check_p9(slides[8]))
    p10(slides[9])
    p11(slides[10])
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        apply(BACKUP, TEST_OUT)
