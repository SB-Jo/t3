#!/usr/bin/env python3
"""export_layers_claude.cjs가 화면 전체 크기로 찍은 조각 그림에서 빈 둘레를 잘라 out_claude/layers/에 넣고, 자리(px)를 layers.json에 적는다.

  python crop_layers_claude.py <raw 폴더> <out_claude 폴더>

그림자·빛까지 그대로 담는다(잘린 자리가 보이지 않게). 그림이 비어 있는 조각(글상자만 있는 조각)은 그림 없이 글상자만 남는다.
"""
import json
import shutil
import sys
from pathlib import Path

from PIL import Image


def main():
    raw, out = Path(sys.argv[1]), Path(sys.argv[2])
    info = json.loads((raw / 'info.json').read_text(encoding='utf-8'))
    k = info['scale']
    dst = out / 'layers'
    shutil.rmtree(dst, ignore_errors=True)
    dst.mkdir(parents=True)
    layers = {}
    total = 0
    for name in info['layers']:
        f = raw / (name.replace('/', '_') + '.png')
        im = Image.open(f).convert('RGBA')
        box = im.getchannel('A').point(lambda v: 255 if v > 2 else 0).getbbox()     # 거의 안 보이는 가장자리(알파 2 이하)는 버림
        if not box:
            layers[name] = None
            continue
        x0, y0, x1, y1 = box
        x0, y0 = max(0, x0 - k), max(0, y0 - k)
        x1, y1 = min(im.width, x1 + k), min(im.height, y1 + k)
        x0, y0 = x0 - x0 % k, y0 - y0 % k                                           # 장표 px 격자에 맞춤
        x1, y1 = min(im.width, x1 + (-x1) % k), min(im.height, y1 + (-y1) % k)
        fn = name.replace('/', '_') + '.png'
        im.crop((x0, y0, x1, y1)).save(dst / fn, optimize=True)
        total += (dst / fn).stat().st_size
        layers[name] = {'file': fn, 'x': x0 / k, 'y': y0 / k, 'w': (x1 - x0) / k, 'h': (y1 - y0) / k,
                        'edge': [x0 == 0, y0 == 0, x1 == im.width, y1 == im.height]}
    cut = [n for n, v in layers.items() if v and any(v['edge'])]
    (out / 'layers.json').write_text(json.dumps({'layers': layers, 'texts': info['texts'], 'geom': info['geom']}, ensure_ascii=False, indent=1),
                                     encoding='utf-8')
    print('그림 %d장 %.1f MB%s' % (sum(1 for v in layers.values() if v), total / 1e6, (' · 장표 끝에 닿은 조각: %s' % cut) if cut else ''))


if __name__ == '__main__':
    main()
