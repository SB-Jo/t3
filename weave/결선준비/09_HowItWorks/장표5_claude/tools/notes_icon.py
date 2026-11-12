#!/usr/bin/env python3
"""삼성노트 아이콘의 가장자리를 다듬는다 → ../assets/app-notes.png

장표5/assets/app-notes.png(256px)는 흰 바탕에서 오려 낸 그림이라 왼쪽 위 모서리와 아래 가장자리에 흰 테가 남아 있다.
모양(알파)은 그대로 두고, 가장자리 띠의 색만 안쪽 빨강에서 맞춘 색으로 다시 칠한다. 가운데 흰 그림은 건드리지 않는다.

  python tools/notes_icon.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent.parent
SRC = HERE.parent / '장표5' / 'assets' / 'app-notes.png'
DST = HERE / 'assets' / 'app-notes.png'
RING, BLEND = 20, 12               # 가장자리에서 이만큼은 맞춘 색으로, 그 안쪽 BLEND px에 걸쳐 원래 그림으로 이어짐


def main():
    im = np.array(Image.open(SRC).convert('RGBA')).astype(float)
    h, w = im.shape[:2]
    rgb, a = im[..., :3], im[..., 3]
    yy, xx = np.mgrid[0:h, 0:w]
    red = (a > 250) & (rgb[..., 0] > 200) & (rgb[..., 1] < 95) & (rgb[..., 2] < 90)       # 흰 그림과 흰 테를 뺀 빨강 바탕
    u, v = xx / w - 0.5, yy / h - 0.5
    A = np.stack([np.ones_like(u), u, v, u * u, v * v, u * v], -1)
    fit = np.stack([A @ np.linalg.lstsq(A[red], rgb[..., c][red], rcond=None)[0] for c in range(3)], -1)
    # 가장자리까지의 거리(px): 알파를 조금씩 깎아 가며 잰다
    mask = Image.fromarray((a > 127).astype(np.uint8) * 255)
    dist = np.zeros((h, w))
    cur = mask
    for d in range(1, RING + BLEND + 1):
        cur = cur.filter(ImageFilter.MinFilter(3))
        dist += (np.array(cur) > 0)
    k = np.clip((dist - RING) / BLEND, 0, 1)[..., None]          # 0: 맞춘 색, 1: 원래 그림
    out = np.concatenate([np.clip(fit * (1 - k) + rgb * k, 0, 255), a[..., None]], -1)
    DST.parent.mkdir(exist_ok=True)
    Image.fromarray(out.round().astype(np.uint8), 'RGBA').save(DST)
    left = ((out[..., 3] > 200) & (out[..., 1] > 120) & (dist < RING)).sum()
    print('→', DST.relative_to(HERE.parent), '가장자리 띠에 남은 밝은 화소', int(left))


if __name__ == '__main__':
    main()
