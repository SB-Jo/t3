"""0927_v1 덱 6차 다듬기 (2026-09-27 22시 요청).

- 4쪽: 지현 인용문 '가족 친구들이' → '가족 · 친구들이'
- 5쪽: p05/page-05-solution.html 6차본으로 다시 채움
- 6~8쪽: p68/page-06~08.html 6차본으로 다시 채움 (8쪽 지현은 연노랑 니트)
- 9쪽: claude_0927/pages/page-07-pipeline.html 11차본(여백 축소·글자 확대, 새 부제)으로 다시 채움
- 12쪽: Now Nudge '앱 간 연계' △ 일부 가능 → ✕ 제한적

사용: python apply_round6.py --test | --deck (백업 7과 같을 때만)
"""
import hashlib
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.oxml.ns import qn

import apply_round2 as r2
import apply_round3 as r3
import apply_round4 as r4
import header as hd
import pages_p2_p4 as pg
from textmeasure import width

ROOT = Path(__file__).resolve().parents[1]
CL = ROOT.parent
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '7_6차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round6.pptx')
shape, xywh, put, set_text, no_autofit = r2.shape, r2.xywh, r2.put, r2.set_text, r2.no_autofit
PURPLE = '6B4EFF'


def refill(prs, slide, out_dir, name, notes, chip, title_runs=None, sub_runs=None):
    """HTML 렌더 결과로 장표를 다시 채우고, 머리 도형을 공통 규격으로."""
    r3.ensure_notes_body(prs, slide)
    r3.bp.OUT = out_dir
    r3.bp.fill_slide(slide, name, r2.background_from(prs), notes)
    r4.split_fonts(slide)
    texts = [sh for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    c = [sh for sh in texts if sh.text_frame.text.strip() == chip]
    assert len(c) == 1, chip
    c[0].name = 'Header chip'
    tops = sorted((sh for sh in texts if sh is not c[0] and (sh.top or 0) / 9525 < 150), key=lambda s: s.top)
    assert len(tops) == 2, [t.text_frame.text for t in tops]
    tops[0].name, tops[1].name = 'Header title', 'Header subtitle'
    pg.drop_unused_images(slide)
    return hd.apply(slide, title_runs=title_runs, sub_runs=sub_runs)


def p4(slide):
    t = shape(slide, sid=335)
    hits = [r for r in t._element.iter(qn('a:r')) if '가족 친구들이' in (r.find(qn('a:t')).text or '')]
    assert len(hits) == 1, t.text_frame.text
    tt = hits[0].find(qn('a:t'))
    tt.text = tt.text.replace('가족 친구들이', '가족 · 친구들이')


def p12(slide):
    t = shape(slide, name='Text 49')
    assert t.text_frame.text == '일부 가능'
    old = shape(slide, name='Status icon · tri · 일부 가능')
    x, y, w, h = xywh(t)
    cx = x - 16 + (16 + w - 6) / 2                  # 2차에서 [아이콘 11 + 간격 5 + 글자]를 이 가운데로 맞췄음
    tw = width('제한적', 13 * 4 / 3, 700)
    gx = cx - (16 + tw) / 2
    set_text(t, [[('제한적', None, None)]])
    no_autofit(t, algn='l')
    put(t, x=gx + 16, w=tw + 6)
    old._element.getparent().remove(old._element)
    r2.add_sp(slide, r2.icon_xml('x', gx, y + 11.4 - 5.5, 11.0), 'Status icon · x · 제한적 (Now Nudge)')


NOTES9 = (CL / 'notes' / 'page-07-pipeline.txt').read_text(encoding='utf-8').strip()


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    labels = r2.labels(prs)
    assert [labels[i] for i in (4, 5, 6, 7, 8, 11)] == ['SOLUTION: WEAVE ASSIST', 'USER SCENARIO 1', 'USER SCENARIO 2', 'USER SCENARIO 3', 'HOW IT WORKS', '차별화 포인트'], labels
    p4(slides[3])
    r = refill(prs, slides[4], ROOT / 'p05' / 'out', 'page-05-solution', (ROOT / 'p05' / 'notes-page-05.txt').read_text(encoding='utf-8').strip(),
               'SOLUTION: WEAVE ASSIST', title_runs=[('Weave', '6666FF'), ('의 ', None), ('핵심 UX 3가지', '6666FF'), ('를 소개합니다!', None)])
    print(5, r['chip'], '|', r['title'], '|', r.get('sub', ''))
    for n in (6, 7, 8):
        r = refill(prs, slides[n - 1], ROOT / 'p68' / 'out', f'page-0{n}', r4.NOTES[n], r4.HEADERS[n])
        print(n, r['chip'], '|', r['title'], '|', r.get('sub', ''))
    r = refill(prs, slides[8], CL / 'out', 'page-07-pipeline', NOTES9, 'HOW IT WORKS',
               title_runs=[('Weave', PURPLE), ('는 어떻게 ', None), ('기억을 엮을까요', PURPLE), ('?', None)])
    print(9, r['chip'], '|', r['title'], '|', r.get('sub', ''))
    p12(slides[11])
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        apply(BACKUP, TEST_OUT)
