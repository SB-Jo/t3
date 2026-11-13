#!/usr/bin/env python3
"""인트로 장과 연표에 쓰는 그림을 만든다.

  python tools/intro_assets.py            assets/src/floats.html → assets/intro/floats.png (3~5쪽 제목과 말풍선 사이의 옅은 기록 조각)
                                                                    + floats-a.png, floats-b.png, floats-c.png (세 층으로 나눈 것. 덱에서 따로 떠다님)
                                          assets/src/icons.html → assets/outro/ic-npu.png (연표의 NPU 마디 아이콘)
  python tools/intro_assets.py --blur     out/png의 12쪽(기록이 이어진 모습)을 흐리게 → assets/intro/blur_link.jpg (13쪽 배경). 먼저 make.py --png
  python -I tools/intro_assets.py --aura   팀원 덱(원본/통합본_인트로수정_87bf80b.pptx) 5쪽의 인물 그림 셋의 윤곽을 크게 흐려 옅은 보라 그라데이션으로
                                          → assets/intro/aura-1.png, aura-2.png, aura-3.png (3~5쪽 인물 뒤에 까는 그림)
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
INTRO2 = HERE / '원본' / '통합본_인트로수정_87bf80b.pptx'
PERSON_PAGE = 5                         # 세 인물이 다 있는 쪽
# 인물 뒤의 옅은 보라 그라데이션: 인물 윤곽(투명도)을 크게 흐린 것. 몸 안쪽에서 가장 진하고(인물에 가려짐) 바깥으로 갈수록 고르게 옅어져 띠나 테두리가 생기지 않는다.
AURA_PAD = 170                          # 인물 그림의 왼쪽, 오른쪽, 위로 더 넓히는 만큼(장의 px). make.py의 AURA_PAD와 같아야 함
AURA_BLUR = ((38, 0.45), (78, 0.55))    # (흐림 반지름 σ(장의 px), 섞는 비율) — 가까이에서 조금 더 진하고 멀리까지 길게 번지게 두 겹
AURA_RGB, AURA_MAX = (150, 124, 255), 0.26      # 색(연한 보라), 가장 진한 곳(몸 안쪽)의 진하기. 윤곽 바로 밖은 그 절반쯤


def auras():
    """인물마다 그 뒤에 깔 그라데이션 그림을 만든다. 크기는 인물 그림의 상자(장의 px)에 AURA_PAD만큼 왼쪽, 오른쪽, 위를 넓힌 것."""
    import io

    import numpy as np
    from pptx import Presentation
    from scipy import ndimage
    ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main', 'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
          'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    sl = list(Presentation(str(INTRO2)).slides)[PERSON_PAGE - 1]
    for pic in sl._element.iter('{%s}pic' % ns['p']):
        name = pic.find('.//{%s}cNvPr' % ns['p']).get('name')
        if name not in ('!!p1', '!!p2', '!!p3'):
            continue
        ext = pic.find('.//{%s}xfrm' % ns['a']).find('{%s}ext' % ns['a'])
        w, h = round(int(ext.get('cx')) / 9525), round(int(ext.get('cy')) / 9525)
        blob = sl.part.related_part(pic.find('.//{%s}blip' % ns['a']).get('{%s}embed' % ns['r'])).blob
        a = np.asarray(Image.open(io.BytesIO(blob)).convert('RGBA').resize((w, h), Image.LANCZOS))[..., 3] / 255.0
        a = np.where(a > 0.06, a, 0.0)                              # 투명한 곳에 남은 옅은 잔티는 뺌
        cv = np.zeros((h + AURA_PAD, w + 2 * AURA_PAD))
        cv[AURA_PAD:, AURA_PAD:AURA_PAD + w] = a
        soft = sum(k * ndimage.gaussian_filter(cv, sg, mode='nearest') for sg, k in AURA_BLUR)      # 아래 끝은 몸이 이어지는 것으로(가장자리 값을 늘려 흐림)
        px = np.zeros(cv.shape + (4,), dtype=np.uint8)
        px[..., :3] = AURA_RGB
        px[..., 3] = np.clip(np.round(soft * AURA_MAX * 255), 0, 255)
        dst = DST / ('aura-%s.png' % name[-1])
        Image.fromarray(px).save(dst, optimize=True)
        print('→ assets/intro/%s' % dst.name, px.shape[1], px.shape[0], '가장 진한 곳 %d/255, 가장자리 %d/255' % (px[..., 3].max(), max(px[0, :, 3].max(), px[:, 0, 3].max(), px[:, -1, 3].max())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--blur', action='store_true')
    ap.add_argument('--aura', action='store_true')
    a = ap.parse_args()
    DST.mkdir(parents=True, exist_ok=True)
    if a.aura:
        auras()
        return
    if a.blur:
        src = HERE / 'out' / 'png' / ('s%02d.png' % LINK_PAGE)
        im = Image.open(src).convert('RGB').resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.GaussianBlur(BLUR))
        Image.blend(im, Image.new('RGB', im.size, (250, 248, 255)), VEIL).save(DST / 'blur_link.jpg', quality=88)
        print('→', (DST / 'blur_link.jpg').relative_to(HERE), src.name)
        return
    subprocess.run(['node', str(HERE / 'tools' / 'shot.cjs'), str(SRC / 'floats.html'), str(DST), '--scale', '2'], check=True)
    for n in ('floats', 'floats-a', 'floats-b', 'floats-c'):
        print('→ assets/intro/%s.png' % n, Image.open(DST / (n + '.png')).size)
    subprocess.run(['node', str(HERE / 'tools' / 'shot.cjs'), str(SRC / 'icons.html'), str(HERE / 'assets' / 'outro')], check=True)


if __name__ == '__main__':
    sys.exit(main())
