"""0927_v1 덱 9차 다듬기 (2026-09-28 요청: 아이폰 앱 아이콘 → 갤럭시 앱 아이콘).

갤럭시 아이콘: claude_0927/assets/icons/galaxy/
  samsung-calendar.png                     갤럭시 스토어 공식 아이콘(512×512)
  knox-portal.png                          메일: 삼성 사내 메일 Knox Portal(사용자 휴대폰 캡처를 깨끗하게 다시 만듦, tools/make_knox_icon.py).
                                           공식 삼성 이메일(흰 봉투에 빨간 @)은 삼성노트(빨강)와 구분이 어려워 바꿈(사용자 요청)
  samsung-gallery.png, samsung-phone.png   공식 홍보 이미지·S25/S26 홈 화면 사진을 보고 그림(gallery.svg, phone.svg,
                                           tools/make_galaxy_icons.cjs), 모서리 윤곽은 공식 캘린더 아이콘과 같음

- 3쪽: '사진' 아이콘(아이폰 사진 앱 모양) → 갤러리
- 5쪽: 갤러리 1, 메일 2(왼쪽에 떠 있는 아이콘, 휴대폰 목록), 캘린더 1  (p05/page-05-solution.html, 8차본은 p05/v5/)
- 6쪽: 전화 1(① 통화 중), 메일 2(③ 메일 카드, 휴대폰 캡처 속 목록 → 캡처 사본 assets/screen-통화-galaxy.png)
- 7쪽: 캘린더 1, 갤러리 1  (p68, 8차본은 p68/v4/)
- 9쪽: 캘린더 4, 갤러리 3, 메일 2(흰 바탕 빨간 @로 그렸던 것도 Knox Portal로)  (claude_0927 14차, 13차본은 v13/)
- 18쪽: 캘린더 1 — 부제가 없는 장표라 다시 채우지 않고 그래픽 레이어 그림만 바꿈(바뀐 곳은 캘린더 아이콘 자리뿐, 확인함)

사용: python apply_round9.py --test | --deck (백업 10과 같을 때만)
"""
import hashlib
import sys
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

import apply_round2 as r2
import apply_round4 as r4
import apply_round6 as r6
import pages_p2_p4 as pg

ROOT = Path(__file__).resolve().parents[1]
CL = ROOT.parent
GAL = CL / 'assets' / 'icons' / 'galaxy'
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '10_9차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round9.pptx')
PURPLE = '6B4EFF'


def swap_picture(slide, pic, png):
    """그림 도형의 자리·크기는 그대로 두고 그림 파일만 바꿈."""
    blip = pic._element.find('.//' + qn('a:blip'))
    _, rId = slide.part.get_or_add_image_part(str(png))
    blip.set(qn('r:embed'), rId)
    return pg.drop_unused_images(slide)


def p3(slide):
    pic = r2.shape(slide, name='App icon gallery')
    return swap_picture(slide, pic, GAL / 'samsung-gallery.png')


def p18(slide):
    pics = [sh for sh in slide.shapes if sh.shape_type == 13 and sh.name.startswith('Weave graphics layer')]
    assert len(pics) == 1, [p.name for p in pics]
    return swap_picture(slide, pics[0], CL / 'out' / 'page-16-glossary.art.png')


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    print(3, 'gallery icon, dropped', p3(slides[2]))
    r = r6.refill(prs, slides[4], ROOT / 'p05' / 'out', 'page-05-solution', (ROOT / 'p05' / 'notes-page-05.txt').read_text(encoding='utf-8').strip(),
                  'SOLUTION: WEAVE ASSIST', title_runs=[('Weave', '6666FF'), ('의 ', None), ('핵심 UX 3가지', '6666FF'), ('를 소개합니다!', None)])
    print(5, r['title'])
    for n in (6, 7):
        r = r6.refill(prs, slides[n - 1], ROOT / 'p68' / 'out', f'page-0{n}', r4.NOTES[n], r4.HEADERS[n])
        print(n, r['title'])
    notes9 = (CL / 'notes' / 'page-07-pipeline.txt').read_text(encoding='utf-8').strip()
    r = r6.refill(prs, slides[8], CL / 'out', 'page-07-pipeline', notes9, 'HOW IT WORKS',
                  title_runs=[('Weave', PURPLE), ('는 어떻게 ', None), ('기억을 엮을까요', PURPLE), ('?', None)])
    print(9, r['title'], '|', r.get('sub'))
    print(18, 'graphics layer, dropped', p18(slides[17]))
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        apply(BACKUP, TEST_OUT)
