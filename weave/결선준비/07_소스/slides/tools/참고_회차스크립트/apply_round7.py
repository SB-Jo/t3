"""0927_v1 덱 7차 다듬기 (2026-09-27 23시 요청).

- 4쪽: 지현 인용문 '한마디도' → '한마디를'
- 5쪽: 번호 원 입체감 없앰, 밀어 올리기 표시 7px 왼쪽
- 6~8쪽: 배지 숫자 1px 왼쪽, 6쪽 ① 말풍선 안쪽 여백 2배·가운데로, 6쪽 손은 화살표 아래,
         7쪽 ① 말풍선 가운데로·'맞아, 이거였어!' 손글씨, 8쪽 ① 대화 조각 오른쪽으로·'하마터면 잊을 뻔했네!' 손글씨
- 9쪽: 04 'sLLM이 상황에 맞는 모양으로' (claude_0927 원본 12차)
- 11쪽: 하단 두 문장을 위 상자에서 10px 더 떨어뜨림

사용: python apply_round7.py --test | --deck (백업 8과 같을 때만)
"""
import hashlib
import sys
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

import apply_round2 as r2
import apply_round4 as r4
import apply_round6 as r6

ROOT = Path(__file__).resolve().parents[1]
CL = ROOT.parent
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '8_7차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round7.pptx')
PURPLE = '6B4EFF'


def p4(slide):
    t = r2.shape(slide, sid=335)
    hits = [r for r in t._element.iter(qn('a:r')) if '한마디도' in (r.find(qn('a:t')).text or '')]
    assert len(hits) == 1, t.text_frame.text
    tt = hits[0].find(qn('a:t'))
    tt.text = tt.text.replace('한마디도', '한마디를')


def p11(slide):
    t = r2.shape(slide, sid=36)
    assert t.text_frame.text.startswith('기록은 이미 충분합니다.')
    x, y, w, h = r2.xywh(t)
    r2.put(t, y=y + 10)
    return round(y, 1), round(y + 10, 1)


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    p4(slides[3])
    r = r6.refill(prs, slides[4], ROOT / 'p05' / 'out', 'page-05-solution', (ROOT / 'p05' / 'notes-page-05.txt').read_text(encoding='utf-8').strip(),
                  'SOLUTION: WEAVE ASSIST', title_runs=[('Weave', '6666FF'), ('의 ', None), ('핵심 UX 3가지', '6666FF'), ('를 소개합니다!', None)])
    print(5, r['title'])
    for n in (6, 7, 8):
        r = r6.refill(prs, slides[n - 1], ROOT / 'p68' / 'out', f'page-0{n}', r4.NOTES[n], r4.HEADERS[n])
        print(n, r['title'])
    notes9 = (CL / 'notes' / 'page-07-pipeline.txt').read_text(encoding='utf-8').strip()
    r = r6.refill(prs, slides[8], CL / 'out', 'page-07-pipeline', notes9, 'HOW IT WORKS',
                  title_runs=[('Weave', PURPLE), ('는 어떻게 ', None), ('기억을 엮을까요', PURPLE), ('?', None)])
    print(9, r['title'], '|', r.get('sub'))
    print(11, 'text y', p11(slides[10]))
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        apply(BACKUP, TEST_OUT)
