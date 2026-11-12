#!/usr/bin/env python3
"""마무리 세 장(39~41쪽)에 후보 사진을 대 본 시안. `마무리사진_후보/`의 사진을 지금 장의 글, 어둠과 함께 PowerPoint로 찍어 한 장에 모은다.
덱은 바꾸지 않는다(시안 덱은 out/closing_try.pptx).

  python tools/closing_try.py        → 마무리사진_후보/후보_한눈에.jpg, 시안_한눈에.jpg
"""
import copy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import make as MK  # noqa: E402
import slides_new as N  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from pptx import Presentation  # noqa: E402

CAND = HERE / '마무리사진_후보'
FONT = Path.home() / '.cache' / 'weave-tools' / 'fonts' / 'SamsungOneKorean-500.ttf'
LIGHT = ((0, 46), (55, 36), (100, 34))                    # 얼굴이 보이는 사진: 40쪽의 어둠을 옅게
BRIGHT39 = ((0, 60), (38, 60), (62, 56), (100, 32))       # 가운데가 밝은 사진: 39쪽 글 자리를 조금 더 어둡게
BRIGHT41 = ((0, 50), (30, 60), (62, 60), (100, 34))
# (줄 이름, [(쪽, 사진 코드, 바꿀 값)]) — hand = 40쪽 손글씨 '순간'의 (가운데 x, 가운데 y, 폭)
TRIES = [
    ('가. 찍어 주는 순간', [(39, 'A5', {}), (40, 'A1', dict(hand=(800, 150, 340))), (41, 'C2', dict(stops=BRIGHT41))]),
    ('나. 삼성 휴대폰이 보이는 사진', [(39, 'C1', dict(stops=BRIGHT39)), (40, 'A2', dict(hand=(215, 112, 300))), (41, 'C6', {})]),
    ('다. 얼굴이 보이는 사진', [(39, 'C4', dict(stops=BRIGHT39)), (40, 'B3', dict(hand=(250, 150, 320), stops=LIGHT)), (41, 'C9', dict(stops=BRIGHT41))]),
    ('라. 노을과 실루엣', [(39, 'C5', {}), (40, 'A6', dict(hand=(330, 170, 380))), (41, 'C10', {})]),
    ('40쪽에 놓을 다른 사진', [(40, 'B1', dict(hand=(1010, 175, 330), stops=LIGHT)), (40, 'B2', dict(hand=(640, 78, 230), stops=LIGHT)),
                        (40, 'A3', dict(hand=(250, 112, 300)))]),
    ('', [(40, 'B4', dict(hand=(185, 125, 250), stops=LIGHT)), (40, 'A4', dict(hand=(330, 250, 400))), (40, 'A8', dict(hand=(300, 160, 360)))]),
]
MAKE = {39: N.s_end1, 40: N.s_end2, 41: N.s_end3}
TW, TH, GAP, LEFT, TOP, CAPH = 640, 360, 14, 16, 16, 30


def photo(code):
    return str(next(p for p in CAND.glob(code + '_*.jpg')))


def name(code):
    return next(CAND.glob(code + '_*.jpg')).stem.split('_', 1)[1].replace('_', ' ')


GROUPS = [('A. 찍어 주는 순간', 'A'), ('B. 얼굴이 보이는 행복한 순간', 'B'), ('C. 해 질 녘의 가족과 친구 (가운데가 비어 글을 얹기 좋은 사진)', 'C')]


def candidates_sheet():
    """후보 사진을 묶음별로 한 장에 → 후보_한눈에.jpg."""
    font = ImageFont.truetype(str(FONT), 17) if FONT.exists() else ImageFont.load_default()
    head = ImageFont.truetype(str(FONT), 22) if FONT.exists() else ImageFont.load_default()
    cols, tw, th = 4, 480, 270
    rows = []
    for label, g in GROUPS:
        files = sorted(CAND.glob(g + '[0-9]*_*.jpg'), key=lambda p: int(p.stem.split('_')[0][1:]))
        rows.append((label, files))
    height = TOP * 2 + sum(34 + ((len(f) + cols - 1) // cols) * (th + CAPH) for _, f in rows)
    sheet = Image.new('RGB', (LEFT * 2 + cols * tw + (cols - 1) * GAP, height), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    y = TOP
    for label, files in rows:
        d.text((LEFT, y + 2), label, fill=(60, 50, 90), font=head)
        y += 34
        for k, f in enumerate(files):
            x, yy = LEFT + (k % cols) * (tw + GAP), y + (k // cols) * (th + CAPH)
            sheet.paste(Image.open(f).convert('RGB').resize((tw, th), Image.LANCZOS), (x, yy))
            code, nm = f.stem.split('_', 1)
            d.text((x + 2, yy + th + 4), '%s  %s' % (code, nm.replace('_', ' ')), fill=(40, 40, 50), font=font)
        y += ((len(files) + cols - 1) // cols) * (th + CAPH)
    out = CAND / '후보_한눈에.jpg'
    sheet.save(out, quality=88, optimize=True)
    print('→', out.name, sheet.size, '%.2f MB' % (out.stat().st_size / 1e6))


def main():
    candidates_sheet()
    prs = Presentation(str(MK.BASE))
    old = list(prs.slides)
    layout = old[5].slide_layout
    note_tpl = [copy.deepcopy(sh._element) for sh in old[5].notes_slide.placeholders]
    flat = [(row, page, code, kw) for row, items in TRIES for page, code, kw in items]
    specs = [MAKE[page](photo=photo(code), **kw) for _, page, code, kw in flat]
    MK.HW.add_slides(prs, layout, note_tpl, specs)
    MK.drop_slides(prs, old)
    MK.samsung_fonts.remap_prs(prs)
    dst = MK.OUT / 'closing_try.pptx'
    prs.save(str(dst))
    pngs = sorted(MK.render_c.png(dst, MK.OUT / 'closing_try', 1280, 720), key=lambda p: int(p.stem[1:]))
    assert len(pngs) == len(flat), (len(pngs), len(flat))
    font = ImageFont.truetype(str(FONT), 19) if FONT.exists() else ImageFont.load_default()
    head = ImageFont.truetype(str(FONT), 22) if FONT.exists() else ImageFont.load_default()
    rows = len(TRIES)
    rh = TH + CAPH + 34
    sheet = Image.new('RGB', (LEFT * 2 + TW * 3 + GAP * 2, TOP * 2 + rows * rh), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    k = 0
    for r, (label, items) in enumerate(TRIES):
        y = TOP + r * rh
        d.text((LEFT, y + 2), label, fill=(60, 50, 90), font=head)
        for c, (page, code, _) in enumerate(items):
            x = LEFT + c * (TW + GAP)
            sheet.paste(Image.open(pngs[k]).convert('RGB').resize((TW, TH), Image.LANCZOS), (x, y + 34))
            d.text((x + 2, y + 34 + TH + 4), '%d쪽  ·  %s %s' % (page, code, name(code)), fill=(40, 40, 50), font=font)
            k += 1
    out = CAND / '시안_한눈에.jpg'
    sheet.save(out, quality=88, optimize=True)
    print('→', out.name, sheet.size, '%.2f MB' % (out.stat().st_size / 1e6))


if __name__ == '__main__':
    main()
