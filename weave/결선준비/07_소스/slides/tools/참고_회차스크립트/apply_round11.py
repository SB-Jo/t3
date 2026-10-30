"""0927_v1 덱 11차 (2026-09-28 저녁, 팀원 의견: 기대효과 출처 제목).

- 13쪽(기대효과 1): "Workplace Attention Study" → 실제 보고서명 "Workgeist Report".
  같은 출처의 기관명·날짜도 원문대로: Cornell University Ellis Idea Lab, 2021. 06
  (VentureBeat 2021-06-11 "Qatalog: People waste 59 minutes every day trying to find data in apps" — 보고서명·기관명·설문일 2021-03-31)
- 14·15쪽(기대효과 2·3): Compare and Recycle 출처 제목에서 ': Smartphone habits' 삭제.
  원문 제목은 "Digital Declutter Statistics 2025: 69% of Brits Consider Themselves "Digital Hoarders"" (2025-12-12 수정)이고
  'Smartphone habits'라는 제목은 없음 → 앞 제목만 씀

사용: python apply_round11.py --test | --deck (백업 12와 같을 때만)
"""
import hashlib
import sys
from pathlib import Path

from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '12_11차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round11.pptx')

FIXES = {  # 쪽: [(바꿀 글, 새 글)]
    13: [('Cornell University Idea Lab & Qatalog, "Workplace Attention Study" (2021. 09)',
          'Cornell University Ellis Idea Lab & Qatalog, "Workgeist Report" (2021. 06)')],
    14: [('"Digital Declutter Statistics 2025: Smartphone habits"', '"Digital Declutter Statistics 2025"')],
    15: [('"Digital Declutter Statistics 2025: Smartphone habits"', '"Digital Declutter Statistics 2025"')],
}


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    for n, pairs in FIXES.items():
        for old, new in pairs:
            hits = [r for sh in slides[n - 1].shapes if sh.has_text_frame
                    for p in sh.text_frame.paragraphs for r in p.runs if old in r.text]
            assert len(hits) == 1, (n, old, len(hits))            # 글이 한 run 안에 그대로 있어야 함(서식 유지)
            hits[0].text = hits[0].text.replace(old, new)
            print(n, '→', hits[0].text.strip())
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        apply(BACKUP, TEST_OUT)
