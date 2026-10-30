"""0927_v1 덱 14차 (2026-09-29 밤, 2쪽 만화 6컷 검색 결과).

- 6컷: 휴대폰 화면(결과 페이지)을 옆에 확대해 띄움(comic/index.html + revision-claude-14.css).
  흰 박스 왼쪽 위에 4컷처럼 '실타래 + Weave 검색 결과', 아래는 휴대폰 화면 그대로(사진·가게 이름·종류·위치),
  맨 아래 줄은 출처 앱 아이콘(캘린더·갤러리·카카오톡) + '원본 보기'. 휴대폰 속 화면도 같은 UI로 맞춤.
  테두리는 4컷 검색 카드와 같음, 연결선 없음, 남자 오른쪽 어깨·몸 위(얼굴·말풍선·아래 문구는 가리지 않음)
- 바꾸기 전 만화 HTML·PNG는 backups/14차전_원본/

사용: python apply_round14.py --test | --deck (백업 15와 같을 때만)
"""
import hashlib
import sys
from pathlib import Path

from pptx import Presentation

import pages_p2_p4 as pg

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '15_14차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round14.pptx')
COMIC = ROOT / 'comic' / 'out' / 'overview-comic.png'


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    pics = [sh for sh in slides[1].shapes if sh.shape_type == 13]
    assert len(pics) == 1, [sh.name for sh in slides[1].shapes]
    pg.replace_picture(slides[1], pics[0], COMIC.read_bytes(), crop_zero=False)
    pg.drop_unused_images(slides[1])
    print(2, 'comic replaced', pics[0].name)
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        TEST_OUT.parent.mkdir(parents=True, exist_ok=True)
        apply(BACKUP, TEST_OUT)
