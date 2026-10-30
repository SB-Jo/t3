"""9쪽(HOW IT WORKS) 그래픽 레이어만 교체: 04 '입력하기' 손에 반짝임 선 3개(덱 공통 터치 표시).
글자·도형 배치(layout.json)는 7차와 같아 그래픽 레이어 그림만 바꿈.
사용: python touch_p9.py <deck.pptx>
"""
import hashlib
import io
import sys
from pathlib import Path

from pptx import Presentation

import pages_p2_p4 as pg

ROOT = Path(__file__).resolve().parents[2]            # claude_0927
OLD = ROOT / 'v7' / 'out' / 'page-07-pipeline.art.png'
NEW = ROOT / 'out' / 'page-07-pipeline.art.png'


def main(deck):
    prs = Presentation(deck)
    old = hashlib.md5(OLD.read_bytes()).hexdigest()
    hits = [(s, sh) for s in prs.slides for sh in s.shapes
            if sh.shape_type == 13 and sh.name.startswith('Weave graphics layer') and hashlib.md5(sh.image.blob).hexdigest() == old]
    assert len(hits) == 1, len(hits)
    slide, pic = hits[0]
    pg.replace_picture(slide, pic, NEW.read_bytes(), crop_zero=False)
    print('slide', list(prs.slides).index(slide) + 1, 'dropped', pg.drop_unused_images(slide))
    prs.save(deck)


if __name__ == '__main__':
    main(sys.argv[1])
