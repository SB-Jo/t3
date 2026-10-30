"""5·8쪽 터치 표시를 덱 공통(누르는 손 + 보라 반짝임)으로 교체.

- 5쪽: 카드 그림 24개가 함께 쓰는 원본 그림(1672×941)을 손·옛 방사선을 지운 판(touch/p5/inpainted-1672.png)으로 바꾸고,
       카드 1(밀어 올리기)·카드 2(실타래 키 누르기) 자리에 touch/out/*.png를 얹음
- 8쪽: 휴대폰+인물 그림(660×798)을 커서·파란 방사선을 지운 판(touch/p8/inpainted.png)으로 바꾸고 오버레이를 얹음
사용: python touch_pages.py <deck.pptx> [p5] [p8]
"""
import hashlib
import io
import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.util import Emu

import pages_p2_p4 as pg

TOUCH = Path(__file__).resolve().parents[1] / 'touch'
PX = 9525


def add_overlay(slide, name, label):
    spec = {s['name']: s for s in json.loads((TOUCH / 'out' / 'overlays.json').read_text())}[name]
    pic = slide.shapes.add_picture(str(TOUCH / 'out' / f'{name}.png'), Emu(int(spec['x'] * PX)), Emu(int(spec['y'] * PX)),
                                   Emu(int(spec['w'] * PX)), Emu(int(spec['h'] * PX)))
    pic.name = f'Touch · {label}'
    pic._element.nvPicPr.cNvPr.set('descr', '누르는 손과 반짝임 (터치 표시)')
    return pic


def swap_shared_image(slide, size, new_png):
    """slide에서 size 크기 그림을 쓰는 모든 도형을 new_png로 바꿈 (자르기 값은 그대로)."""
    pics = [sh for sh in slide.shapes if sh.shape_type == 13 and sh.image.size == size]
    rids = {sh._element.find('.//' + qn('a:blip')).get(qn('r:embed')) for sh in pics}
    assert len(rids) == 1, rids
    _, new_rid = slide.part.get_or_add_image_part(io.BytesIO(Path(new_png).read_bytes()))
    for sh in pics:
        sh._element.find('.//' + qn('a:blip')).set(qn('r:embed'), new_rid)
    return len(pics), pg.drop_unused_images(slide)


def label_of(slide):
    for sh in slide.shapes:
        if sh.name == 'Header chip':
            return sh.text_frame.text
    return None


def p5(prs):
    s = prs.slides[4]
    assert label_of(s) == 'SOLUTION'
    assert not any(sh.name.startswith('Touch · ') for sh in s.shapes), '이미 적용됨'
    n, dropped = swap_shared_image(s, (1672, 941), TOUCH / 'p5' / 'inpainted-1672.png')
    add_overlay(s, 'p05-card1-swipe', '카드 1 위로 올려 기억 검색')
    add_overlay(s, 'p05-card2-tap', '카드 2 실타래 버튼')
    print('p5: swapped', n, 'pictures, dropped', dropped)


def p8(prs):
    s = prs.slides[7]
    assert label_of(s) == 'CUSTOMER SCENARIO' and any(sh.name.startswith('데모 - 휴대폰 화면 + 오른쪽 인물') for sh in s.shapes)
    assert not any(sh.name.startswith('Touch · ') for sh in s.shapes), '이미 적용됨'
    pic = [sh for sh in s.shapes if sh.name.startswith('데모 - 휴대폰 화면 + 오른쪽 인물')][0]
    pg.replace_picture(s, pic, (TOUCH / 'p8' / 'inpainted.png').read_bytes(), crop_zero=False)
    add_overlay(s, 'p08-input-tap', '입력하기 버튼')
    print('p8: dropped', pg.drop_unused_images(s))


if __name__ == '__main__':
    deck = sys.argv[1]
    prs = Presentation(deck)
    for step in sys.argv[2:]:
        {'p5': p5, 'p8': p8}[step](prs)
    prs.save(deck)
