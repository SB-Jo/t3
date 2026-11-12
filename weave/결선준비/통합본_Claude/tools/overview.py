#!/usr/bin/env python3
"""덱 전체를 한 장에 모은 그림 → 한눈에.jpg  (먼저 make.py --png로 out/png를 만들어 둠)

  python tools/overview.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import make as MK  # noqa: E402
import doc  # noqa: E402

FONT = Path.home() / '.cache' / 'weave-tools' / 'fonts' / 'SamsungOneKorean-500.ttf'
COLS, W, PAD, LAB = 10, 300, 10, 26
CIRCLED = {ord('①'): '1', ord('②'): '2', ord('③'): '3'}        # 이름표 글꼴에 동그라미 숫자가 없음
TINT = {'main': '#1C1A24', 'appx': '#6A6474', 'prop': '#6B4EFF', 'old': '#B0452F'}


def labels():
    own = MK.own_specs()
    out = []
    for item in MK.SEQ:
        for k in ([sp.key for sp in own[item[1]]] if isinstance(item, tuple) else [item]):
            out.append(('main', doc.NAME.get(k, k).split(' (')[0]))
    n_appx = len(MK.HW.appendix_specs()) + 1
    out += [('appx', 'Appendix %d' % (i + 1)) for i in range(n_appx)]
    out += [('prop', '제안 장표 가름')] + [('prop', doc.NAME[sp.key]) for sp in own['prop']]
    out += [('old', '이전 판 (4차) 가름')] + [('old', '이전 판 · 4차 %d쪽' % i) for i in MK.PREV4_KEEP]
    out += [('old', '이전 판 (3차) 가름')] + [('old', '이전 판 · 3차 %d쪽' % i) for i in MK.PREV3_KEEP]
    out += [('old', '이전 판 (2차) 가름')] + [('old', '이전 판 · 2차 %d쪽' % i) for i in MK.PREV2_KEEP]
    out += [('old', '이전 판 (1차) 가름')] + [('old', '이전 판 · 1차 %d쪽' % i) for i in MK.PREV_KEEP] + [('old', '이전 판 · 인트로 덱 13쪽')]
    return out


def main():
    files = sorted((MK.OUT / 'png').glob('s*.png'), key=lambda f: int(f.stem[1:]))       # s100.png이 s11.png 앞에 오지 않게 숫자로
    labs = labels()
    assert len(files) == len(labs), (len(files), len(labs))
    h = W * 9 // 16
    rows = (len(files) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * (W + PAD) + PAD, rows * (h + LAB + PAD) + PAD), 'white')
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 15) if FONT.exists() else ImageFont.load_default()
    for i, (f, (kind, name)) in enumerate(zip(files, labs)):
        x, y = PAD + (i % COLS) * (W + PAD), PAD + (i // COLS) * (h + LAB + PAD)
        lab = '%d  %s' % (i + 1, name.translate(CIRCLED))
        while font.getlength(lab) > W - 6:                 # 칸보다 긴 이름은 줄임
            lab = lab[:-2] + '…'
        d.text((x + 1, y + 3), lab, fill=TINT[kind], font=font)
        sheet.paste(Image.open(f).convert('RGB').resize((W, h), Image.LANCZOS), (x, y + LAB))
        d.rectangle([x - 1, y + LAB - 1, x + W, y + LAB + h], outline='#D5D0E2')
    dst = HERE / '한눈에.jpg'
    sheet.save(dst, quality=84)
    print('→', dst.name, sheet.size, '%.2f MB' % (dst.stat().st_size / 1e6))


if __name__ == '__main__':
    main()
