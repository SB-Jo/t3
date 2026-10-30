"""0927_v1 덱 10차 다듬기 (2026-09-28 요청).

- 3쪽: 아래 구분선(가로선 그림 'Presenton Native Image 12') 삭제, 아래 문장 16pt → 17pt(반 단계)
- 5·6·9쪽: 메일 아이콘을 삼성 이메일 공식 아이콘에서 빨간 원만 하늘색→파랑으로 바꾼 것으로
          (claude_0927/assets/icons/galaxy/samsung-email-blue.png, tools/make_email_blue.py). 9차의 Knox Portal 대신
- 18쪽: Q1 '글과 사진의 의미를 벡터로 … 질문도 벡터로 바꿔', Q2 '만들어 연산량이 많고 … 최종 문장만' (claude_0927 15차)
        부제가 없는 장표라 제목만 찾아 머리 규격을 적용하는 전용 채우기(refill18)

사용: python apply_round10.py --test | --deck (백업 11과 같을 때만)
"""
import hashlib
import sys
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

import apply_round2 as r2
import apply_round3 as r3
import apply_round4 as r4
import apply_round6 as r6
import header as hd
import pages_p2_p4 as pg

ROOT = Path(__file__).resolve().parents[1]
CL = ROOT.parent
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '11_10차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round10.pptx')
PURPLE = '6B4EFF'


def p3(slide):
    line = r2.shape(slide, sid=61)
    assert line.name == 'Presenton Native Image 12' and line.image.size == (2304, 118)
    line._element.getparent().remove(line._element)
    pg.drop_unused_images(slide)
    t = r2.shape(slide, sid=148)
    assert t.text_frame.text.startswith('세상 모든 지식은 AI에게 묻는데')
    n = 0
    for r in t._element.iter(qn('a:rPr')):
        if r.get('sz') == '1600':
            r.set('sz', '1700')
            n += 1
    assert n >= 3, n
    return n


def refill18(prs, slide):
    notes = (CL / 'notes' / 'page-16-glossary.txt').read_text(encoding='utf-8').strip()
    r3.ensure_notes_body(prs, slide)
    r3.bp.OUT = CL / 'out'
    r3.bp.fill_slide(slide, 'page-16-glossary', r2.background_from(prs), notes)
    r4.split_fonts(slide)
    texts = [sh for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    chip = [sh for sh in texts if sh.text_frame.text.strip() == '16 / Appendix · Q&A']
    assert len(chip) == 1, [t.text_frame.text for t in texts[:5]]
    chip[0].name = 'Header chip'
    tops = sorted((sh for sh in texts if sh is not chip[0] and (sh.top or 0) / 9525 < 150), key=lambda s: s.top)
    assert len(tops) == 1, [t.text_frame.text for t in tops]      # 이 장표는 부제가 없음
    tops[0].name = 'Header title'
    pg.drop_unused_images(slide)
    return hd.apply(slide, chip_text='Appendix · Q&A')


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    print(3, 'runs resized', p3(slides[2]))
    r = r6.refill(prs, slides[4], ROOT / 'p05' / 'out', 'page-05-solution', (ROOT / 'p05' / 'notes-page-05.txt').read_text(encoding='utf-8').strip(),
                  'SOLUTION: WEAVE ASSIST', title_runs=[('Weave', '6666FF'), ('의 ', None), ('핵심 UX 3가지', '6666FF'), ('를 소개합니다!', None)])
    print(5, r['title'])
    r = r6.refill(prs, slides[5], ROOT / 'p68' / 'out', 'page-06', r4.NOTES[6], r4.HEADERS[6])
    print(6, r['title'])
    notes9 = (CL / 'notes' / 'page-07-pipeline.txt').read_text(encoding='utf-8').strip()
    r = r6.refill(prs, slides[8], CL / 'out', 'page-07-pipeline', notes9, 'HOW IT WORKS',
                  title_runs=[('Weave', PURPLE), ('는 어떻게 ', None), ('기억을 엮을까요', PURPLE), ('?', None)])
    print(9, r['title'], '|', r.get('sub'))
    r = refill18(prs, slides[17])
    print(18, r)
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        apply(BACKUP, TEST_OUT)
