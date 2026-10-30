"""삼성 이메일 공식 아이콘(흰 봉투 + 빨간 원 @)에서 빨간 원만 하늘색→파랑 그라데이션으로 (2026-09-28 사용자 요청).
빨간 원이 삼성노트(빨강)와 비슷해 보여서. 원래 음영(원의 밝기 변화)과 흰 @·봉투는 그대로 둠.
사용: python tools/make_email_blue.py  → assets/icons/galaxy/samsung-email-blue.png
"""
from pathlib import Path

import numpy as np
from PIL import Image

GAL = Path(__file__).resolve().parents[1] / 'assets' / 'icons' / 'galaxy'
SKY, BLUE = np.array([56, 189, 248], np.float32), np.array([37, 99, 235], np.float32)   # 위 하늘색 → 아래 파랑

im = np.array(Image.open(GAL / 'samsung-email.png').convert('RGBA')).astype(np.float32)
rgb, a = im[..., :3], im[..., 3:]
R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
w = np.clip((R - np.maximum(G, B)) / (241 - 27), 0, 1)[..., None]     # 빨간 원이 섞인 정도(가장자리·@ 둘레는 중간값)
neutral = ((G + B) / 2)[..., None].repeat(3, -1)                          # 섞인 흰색·회색 몫
shade = np.clip(R / 241, 0, 1.2)[..., None]                               # 빨간 원 안의 밝기 변화(입체감)
ys, xs = np.nonzero(w[..., 0] > .5)
y0, y1 = ys.min(), ys.max()
t = np.clip((np.arange(im.shape[0]) - y0) / (y1 - y0), 0, 1)[:, None, None]
blue = ((1 - t) * SKY + t * BLUE) * shade
new = w * blue + (1 - w) * neutral
out = np.concatenate([np.clip(new, 0, 255), a], -1).astype(np.uint8)
Image.fromarray(out, 'RGBA').save(GAL / 'samsung-email-blue.png')
print('wrote', GAL / 'samsung-email-blue.png', 'circle rows', y0, y1)
