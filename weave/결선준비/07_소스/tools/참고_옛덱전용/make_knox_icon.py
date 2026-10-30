"""Knox Portal 아이콘을 사용자 휴대폰 캡처(One UI 홈 화면, 2026-09-28)에서 깨끗하게 다시 만듦.

캡처 속 아이콘은 약 232px라 그대로 키우면 흐려짐 →
  1) 아이콘 부분을 잘라 8배(1856px)로 부드럽게 키운 뒤, 픽셀마다 가장 가까운 색(남색·청록·파랑·밝은 회색)으로 다시 칠함
     = 색 경계를 매끈한 선으로 다시 그리는 효과
  2) 512px로 줄여 가장자리를 부드럽게, 밝은 부분(바탕·마름모·구멍)은 다른 One UI 아이콘처럼 위가 조금 더 밝은 은은한 그라데이션
  3) 모서리 윤곽은 공식 삼성 캘린더 아이콘의 투명도로 잘라 다른 갤럭시 아이콘과 같게
사용: python tools/make_knox_icon.py <캡처.png>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GAL = ROOT / 'assets' / 'icons' / 'galaxy'
PAL = {'navy': (37, 57, 96), 'teal': (12, 183, 172), 'blue': (39, 117, 216), 'light': (230, 230, 230)}


def main(shot):
    src = Image.open(shot).convert('RGB')
    box = (20.5, 27.0, 252.5, 259.0)                      # 캡처 속 아이콘 윤곽(스쿼클) 범위
    crop = src.resize((src.width * 8, src.height * 8), Image.BICUBIC).crop(tuple(int(v * 8) for v in box))
    big = np.array(crop).astype(np.float32)               # 1856×1856
    names = list(PAL)
    cols = np.array([PAL[n] for n in names], np.float32)
    dist = ((big[:, :, None, :] - cols[None, None]) ** 2).sum(-1)
    lab = dist.argmin(-1)
    # 윤곽 가장자리: 캡처의 홈 화면 회색이 섞여 남색·파랑으로 잘못 분류되므로, 윤곽을 안쪽으로 3%(캡처 기준 약 7px) 줄인 바깥은 모두 밝은 바탕
    from PIL import ImageFilter
    from PIL import ImageOps                               # 윤곽이 그림 테두리에 닿아 있어, 바깥을 비운 여백을 붙인 뒤 줄이고 다시 잘라 냄
    rim = ImageOps.expand(Image.open(GAL / 'samsung-calendar.png').getchannel('A').resize(lab.shape[::-1], Image.BILINEAR), border=120, fill=0)
    rim = rim.filter(ImageFilter.MinFilter(111)).crop((120, 120, 120 + lab.shape[1], 120 + lab.shape[0]))
    lab[np.array(rim) < 128] = names.index('light')
    # 밝은 부분: 위 #F4F4F6 → 아래 #E2E2E6 (One UI 아이콘의 은은한 입체감)
    n = lab.shape[0]
    grad = np.linspace(0, 1, n, dtype=np.float32)[:, None, None]
    light = (1 - grad) * np.array([244, 244, 246], np.float32) + grad * np.array([226, 226, 230], np.float32)
    out = np.empty(big.shape, np.float32)
    for i, name in enumerate(names):
        m = lab == i
        out[m] = np.broadcast_to(light, big.shape)[m] if name == 'light' else np.array(PAL[name], np.float32)
    im = Image.fromarray(out.clip(0, 255).astype(np.uint8)).resize((512, 512), Image.LANCZOS).convert('RGBA')
    im.putalpha(Image.open(GAL / 'samsung-calendar.png').getchannel('A'))
    im.save(GAL / 'knox-portal.png')
    print('wrote', GAL / 'knox-portal.png', {k: int((lab == i).mean() * 1000) / 10 for i, k in enumerate(names)})


if __name__ == '__main__':
    main(sys.argv[1])
