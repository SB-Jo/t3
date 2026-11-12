#!/usr/bin/env python3
"""6쪽(수많은 기록)에 쓰는 그림을 만든다.

  python tools/hook_assets.py
    1) assets/src/screens.html → assets/hook/screens/*.jpg  (앱 화면 18장, 360×780. 불이 켜질 때 얹는 밝은 화면)
    2) 그 화면들을 hook_layout.py의 자리에 놓고 어둡게 한 벽 → assets/hook/mosaic.jpg (2560×1440)
    3) assets/src/camera.html → assets/hook/samsung-camera.png (갤럭시 카메라 아이콘을 보고 그린 것, 테두리 모양은 갤러리 아이콘과 같게)
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageEnhance

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import hook_layout as H  # noqa: E402

HOOK = HERE / 'assets' / 'hook'
SRC = HERE / 'assets' / 'src'
TMP = HERE / 'out' / '_hook'
K = 2                                   # 벽 그림은 1280×720의 두 배
DIM, GRAY = 0.34, 0.25                  # 꺼진 화면의 밝기, 채도를 덜어 내는 만큼
BG = (10, 10, 14)


def shot(html, dst):
    subprocess.run(['node', str(HERE / 'tools' / 'shot.cjs'), str(html), str(dst)], check=True)


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    (HOOK / 'screens').mkdir(parents=True, exist_ok=True)
    shot(SRC / 'screens.html', TMP)
    png = {f.stem: Image.open(f).convert('RGBA') for f in TMP.glob('*.png') if f.stem != 'camera_raw'}
    for name, im in png.items():        # 밝은 화면: 흰 바탕 JPG(모서리는 장표에서 둥글게 자름)
        flat = Image.new('RGB', im.size, 'white')
        flat.paste(im, (0, 0), im)
        flat.save(HOOK / 'screens' / (name + '.jpg'), quality=90)
    wall = Image.new('RGB', (1280 * K, 720 * K), BG)
    w, h = round(H.PW * K), round(H.PH * K)
    cells = {k: v[1] for k, v in H.CELLS.items()}
    cells.update(H.EDGE)
    for (c, r), name in cells.items():
        x, y = H.pos(c, r)
        im = png[name].resize((w, h), Image.LANCZOS)
        wall.paste(im, (round(x * K), round(y * K)), im)
    wall = ImageEnhance.Color(wall).enhance(1 - GRAY)
    wall = Image.blend(Image.new('RGB', wall.size, BG), wall, DIM)
    wall.save(HOOK / 'mosaic.jpg', quality=88)
    shot(SRC / 'camera.html', TMP)
    raw = Image.open(TMP / 'camera_raw.png').convert('RGBA')
    raw.putalpha(Image.open(HERE.parent / '05_아이콘' / '갤럭시앱' / 'samsung-gallery.png').convert('RGBA').split()[3])
    raw.save(HOOK / 'samsung-camera.png')
    size = sum(f.stat().st_size for f in HOOK.rglob('*') if f.is_file()) / 1e6
    print('화면 %d장, 벽 %s, 모두 %.1f MB' % (len(png), wall.size, size))


if __name__ == '__main__':
    main()
