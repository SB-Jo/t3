#!/usr/bin/env python3
"""인트로 장과 연표에 쓰는 그림을 만든다.

  python tools/intro_assets.py            assets/src/floats.html → assets/intro/floats.png (3~5쪽 제목과 말풍선 사이의 옅은 기록 조각)
                                          assets/src/icons.html → assets/outro/ic-npu.png (38쪽 연표의 NPU 마디 아이콘)
  python tools/intro_assets.py --blur     out/png의 12쪽(기록이 이어진 모습)을 흐리게 → assets/intro/blur_link.jpg (13쪽 배경). 먼저 make.py --png
"""
import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent.parent
SRC = HERE / 'assets' / 'src'
DST = HERE / 'assets' / 'intro'
LINK_PAGE = 12                          # 기록이 이어지는 장(덱에서의 쪽)
BLUR, VEIL = 30, 0.46                   # 흐림 반지름(1920px 기준), 흰 막의 세기


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--blur', action='store_true')
    a = ap.parse_args()
    DST.mkdir(parents=True, exist_ok=True)
    if a.blur:
        src = HERE / 'out' / 'png' / ('s%02d.png' % LINK_PAGE)
        im = Image.open(src).convert('RGB').resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.GaussianBlur(BLUR))
        Image.blend(im, Image.new('RGB', im.size, (250, 248, 255)), VEIL).save(DST / 'blur_link.jpg', quality=88)
        print('→', (DST / 'blur_link.jpg').relative_to(HERE), src.name)
        return
    subprocess.run(['node', str(HERE / 'tools' / 'shot.cjs'), str(SRC / 'floats.html'), str(DST), '--scale', '2'], check=True)
    im = Image.open(DST / 'floats.png')
    print('→ assets/intro/floats.png', im.size)
    subprocess.run(['node', str(HERE / 'tools' / 'shot.cjs'), str(SRC / 'icons.html'), str(HERE / 'assets' / 'outro')], check=True)


if __name__ == '__main__':
    sys.exit(main())
