"""0927_v1 덱 1차 다듬기 (2026-09-27 사용자 요청: 공통 + 2~4쪽).

순서: 2~4쪽 개별 수정 → 모든 장표 머리(칩·제목·부제) 통일 → 마지막 장(20번) 삭제.

사용:
  python apply_round1.py --test          # /tmp 사본에만 적용 (확인용)
  python apply_round1.py --deck          # added_0926/0927_data/0927_v1.pptx에 적용
    - 적용 전 backups/에 사본을 먼저 둘 것. 파일이 백업 이후 바뀌었으면(다른 사람이 수정) 멈춤.
"""
import hashlib
import sys
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

import header
import pages_p2_p4 as pg

ROOT = Path(__file__).resolve().parents[1]                     # claude_0927/deck-0927v1
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '0_원본_1807.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round1.pptx')


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 20, len(slides)

    print('p2 dropped', pg.edit_p2(slides[1], ROOT / 'comic' / 'out' / 'overview-comic.png'))
    _, title3, _ = header.find_header(slides[2])
    pg.edit_p3(slides[2], title3)
    _, _, sub4 = header.find_header(slides[3])
    print('p4 dropped', pg.edit_p4(slides[3], sub4, ROOT / 'characters' / 'sungbin-v1.png', ROOT / 'characters' / 'jihyun-v1.png'))

    for i, s in enumerate(slides, 1):
        r = header.apply(s, keep_sub_colors=i in (13, 14, 15))
        if r:
            print(i, r['chip'], '|', r['title'], '|', r.get('sub', ''))

    # 마지막 장: 이 폴더 도구로 만든 Members(그림 이름 'Member 1 · …') — 19번의 다른 Members 장표가 마지막이 됨
    last = slides[19]
    assert any(sh.shape_type == 13 and sh.name.startswith('Member 1 · ') for sh in last.shapes)
    sld = list(prs.slides._sldIdLst)[19]
    prs.part.drop_rel(sld.get(qn('r:id')))
    prs.slides._sldIdLst.remove(sld)
    prs.save(str(dst))
    print('saved', dst, '| slides', len(prs.slides))


if __name__ == '__main__':
    if '--deck' in sys.argv:
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        apply(BACKUP, TEST_OUT)
