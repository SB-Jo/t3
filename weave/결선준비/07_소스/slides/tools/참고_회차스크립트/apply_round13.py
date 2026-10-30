"""0927_v1 덱 13차 (2026-09-29 밤, 기록을 '엮는' 모습이 더 드러나게).

- 2쪽 만화(comic/index.html + revision-claude-13.css를 다시 렌더한 comic/out/overview-comic.png)
  4컷 검색어 '저번주에 일본에서 먹었던 장어덮밥' → '오사카에서 먹었던 장어덮밥집'(검색 카드 폭을 글자 폭만큼 줄임),
  5컷 폰 속 검색어 '오사카 장어덮밥집', 휴대폰 → 캘린더 → 갤러리 → 카카오톡을 한 가닥 실선으로(카드 뒤로 지나감),
  카카오톡 카드의 '우나기 토쿠야'를 6컷 답과 같은 보라로
- 5쪽: (1) 설명 '앱마다 흩어진 같은 일의 기록을, 하나로 엮어 보여줍니다.', 노트 → 메일 → 카카오톡을 한 가닥 점선으로
- 6쪽: 부제 '회의에서 정한 순서부터 뒤늦게 받은 안내까지, 같은 업무에 관한 기록을 연결합니다.',
  오른쪽 카드 역할 칩 3개 + 'A사 시연 준비' 칩과 오른쪽 점선, ③ '업무 관련 기록을 엮어 확인',
  ④ '필요한 내용을 확인하고 바로 답변', 말풍선 속 사실(순서·5분·8시 40분)은 밑줄 강조
  (5·6쪽은 p05/page-05-solution.html, p68/page-06.html을 고쳐 다시 렌더한 결과로 채움. 이전 HTML·렌더는 backups/13차전_원본/)

사용: python apply_round13.py --test | --deck (백업 14와 같을 때만)
"""
import hashlib
import sys
from pathlib import Path

from pptx import Presentation

import apply_round4 as r4
import apply_round6 as r6
import pages_p2_p4 as pg

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '14_13차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round13.pptx')
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
    notes5 = (ROOT / 'p05' / 'notes-page-05.txt').read_text(encoding='utf-8').strip()
    r = r6.refill(prs, slides[4], ROOT / 'p05' / 'out', 'page-05-solution', notes5, 'SOLUTION: WEAVE ASSIST',
                  title_runs=[('Weave', '6666FF'), ('의 ', None), ('핵심 UX 3가지', '6666FF'), ('를 소개합니다!', None)])
    print(5, r['title'])
    r = r6.refill(prs, slides[5], ROOT / 'p68' / 'out', 'page-06', r4.NOTES[6], r4.HEADERS[6])
    print(6, r['title'], '|', r.get('sub'))
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
