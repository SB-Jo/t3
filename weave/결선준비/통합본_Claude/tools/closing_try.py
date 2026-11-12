#!/usr/bin/env python3
"""마무리 세 장(39~41쪽)에 후보 사진을 대 본 시안. `마무리사진_후보/`의 사진을 지금 장의 글, 어둠과 함께 PowerPoint로 찍어 한 장에 모은다.
덱은 바꾸지 않는다(시안 덱은 out/closing_try.pptx).

  python tools/closing_try.py              → 1차(A~C), 2차(D~F), 3차(G, H, J), 4차(K~N) 모두
  python tools/closing_try.py --round 2    → 2차만: 마무리사진_후보/후보2_한눈에.jpg, 시안2_한눈에.jpg
  python tools/closing_try.py --round 3    → 3차만: 후보3_한눈에.jpg, 시안3_한눈에.jpg
  python tools/closing_try.py --round 4    → 4차만: 후보4_한눈에.jpg, 시안4_한눈에.jpg
"""
import argparse
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
# 1차(11-12 낮): 일상의 행복한 순간. (줄 이름, [(쪽, 사진 코드, 바꿀 값)]) — hand = 40쪽 손글씨 '순간'의 (가운데 x, 가운데 y, 폭)
TRIES1 = [
    ('가. 찍어 주는 순간', [(39, 'A5', {}), (40, 'A1', dict(hand=(800, 150, 340))), (41, 'C2', dict(stops=BRIGHT41))]),
    ('나. 삼성 휴대폰이 보이는 사진', [(39, 'C1', dict(stops=BRIGHT39)), (40, 'A2', dict(hand=(215, 112, 300))), (41, 'C6', {})]),
    ('다. 얼굴이 보이는 사진', [(39, 'C4', dict(stops=BRIGHT39)), (40, 'B3', dict(hand=(250, 150, 320), stops=LIGHT)), (41, 'C9', dict(stops=BRIGHT41))]),
    ('라. 노을과 실루엣', [(39, 'C5', {}), (40, 'A6', dict(hand=(330, 170, 380))), (41, 'C10', {})]),
    ('40쪽에 놓을 다른 사진', [(40, 'B1', dict(hand=(1010, 175, 330), stops=LIGHT)), (40, 'B2', dict(hand=(640, 78, 230), stops=LIGHT)),
                        (40, 'A3', dict(hand=(250, 112, 300)))]),
    ('', [(40, 'B4', dict(hand=(185, 125, 250), stops=LIGHT)), (40, 'A4', dict(hand=(330, 250, 400))), (40, 'A8', dict(hand=(300, 160, 360)))]),
]
GROUPS1 = [('A. 찍어 주는 순간', 'A'), ('B. 얼굴이 보이는 행복한 순간', 'B'), ('C. 해 질 녘의 가족과 친구 (가운데가 비어 글을 얹기 좋은 사진)', 'C')]
# 2차(11-12 저녁): 연인이나 친구끼리 찍어 주는 모습, 셀카를 찍는 모습
TRIES2 = [
    ('가. 연인: 찍어 주는 순간', [(39, 'E12', {}), (40, 'D1', dict(hand=(180, 300, 230), stops=LIGHT)), (41, 'D10', {})]),
    ('나. 친구: 찍어 주는 순간', [(39, 'D12', dict(stops=BRIGHT39)), (40, 'D3', dict(hand=(220, 290, 300))), (41, 'F13', {})]),
    ('다. 셀카', [(39, 'E11', {}), (40, 'E1', dict(hand=(270, 120, 300), stops=LIGHT)), (41, 'F12', dict(stops=BRIGHT41))]),
    ('40쪽에 놓을 다른 사진', [(40, 'D2', dict(hand=(940, 150, 280), stops=LIGHT)), (40, 'D7', dict(hand=(360, 150, 280), stops=LIGHT)),
                        (40, 'E3', dict(hand=(900, 130, 300)))]),
    ('', [(40, 'E4', dict(hand=(250, 120, 300))), (40, 'F2', dict(hand=(800, 105, 250), stops=LIGHT)),
          (40, 'F3', dict(hand=(200, 110, 240), stops=LIGHT))]),
    ('', [(40, 'D5', dict(hand=(330, 120, 280), stops=LIGHT)), (40, 'E2', dict(hand=(1050, 112, 240), stops=LIGHT)),
          (40, 'F15', dict(hand=(190, 130, 250), stops=LIGHT))]),
]
GROUPS2 = [('D. 찍어 주는 모습 (연인, 친구)', 'D'), ('E. 연인의 셀카', 'E'), ('F. 친구들의 셀카', 'F')]
# 3차(11-12 밤): 사진 찍는 모습 말고 더 다양한 순간 — 파티(술 없음), 식사, 그 밖의 좋은 순간
TRIES3 = [
    ('가. 파티와 축하', [(39, 'G15', {}), (40, 'G3', dict(hand=(1020, 150, 300), stops=LIGHT)), (41, 'J19', {})]),
    ('나. 함께하는 식사', [(39, 'J9', {}), (40, 'H1', dict(hand=(560, 150, 320), stops=LIGHT)), (41, 'J5', {})]),
    ('다. 가족과 아이', [(39, 'J10', dict(stops=BRIGHT39)), (40, 'J12', dict(hand=(930, 110, 280))), (41, 'J25', {})]),
    ('40쪽에 놓을 다른 사진', [(40, 'G6', dict(hand=(1130, 140, 230))), (40, 'H4', dict(hand=(380, 110, 320), stops=LIGHT)),
                        (40, 'H7', dict(hand=(800, 120, 320), stops=LIGHT))]),
    ('', [(40, 'H10', dict(hand=(180, 110, 240), stops=LIGHT)), (40, 'J1', dict(hand=(640, 120, 340))), (40, 'J6', dict(hand=(190, 160, 260)))]),
    ('', [(40, 'J13', dict(hand=(125, 120, 190), stops=LIGHT)), (40, 'G14', dict(hand=(640, 110, 340))), (40, 'J16', dict(hand=(1010, 250, 300)))]),
]
GROUPS3 = [('G. 파티와 축하 (술 없음)', 'G'), ('H. 함께하는 식사', 'H'), ('J. 그 밖의 좋은 순간', 'J')]
# 4차(11-12 밤): 단란한 가정 — 아기와 부모가 함께하는 장면(G6 같은), 그 밖의 행복한 가족 장면
TRIES4 = [
    ('가. 아기와 부모', [(39, 'M16', {}), (40, 'K5', dict(hand=(1130, 110, 230))), (41, 'M15', {})]),
    ('나. 집에서의 저녁', [(39, 'M4', {}), (40, 'L2', dict(hand=(300, 520, 300), stops=LIGHT)), (41, 'M8', {})]),
    ('다. 함께 걷는 가족', [(39, 'M5', dict(stops=BRIGHT39)), (40, 'K12', dict(hand=(260, 110, 300))), (41, 'M7', {})]),
    ('40쪽에 놓을 다른 사진', [(40, 'K1', dict(hand=(1080, 560, 260))), (40, 'L1', dict(hand=(380, 200, 340), stops=LIGHT)),
                        (40, 'L5', dict(hand=(170, 190, 240), stops=LIGHT))]),
    ('', [(40, 'L16', dict(hand=(1080, 130, 280), stops=LIGHT)), (40, 'L19', dict(hand=(170, 220, 240), stops=LIGHT)),
          (40, 'K18', dict(hand=(260, 160, 320)))]),
    ('', [(40, 'M10', dict(hand=(1020, 150, 340))), (40, 'M9', dict(hand=(250, 320, 320))), (40, 'N2', dict(hand=(215, 200, 280)))]),
]
GROUPS4 = [('K. 아기와 부모', 'K'), ('L. 집에서의 단란한 시간', 'L'), ('M. 야외의 가족', 'M'), ('N. 조부모와 아이', 'N')]
ROUNDS = {1: (GROUPS1, TRIES1, '후보_한눈에.jpg', '시안_한눈에.jpg'), 2: (GROUPS2, TRIES2, '후보2_한눈에.jpg', '시안2_한눈에.jpg'),
          3: (GROUPS3, TRIES3, '후보3_한눈에.jpg', '시안3_한눈에.jpg'), 4: (GROUPS4, TRIES4, '후보4_한눈에.jpg', '시안4_한눈에.jpg')}
SHEET = {3: dict(cols=5, tw=400), 4: dict(cols=5, tw=400)}                        # 사진이 많은 차수는 한 줄에 다섯 장
MAKE = {39: N.s_end1, 40: N.s_end2, 41: N.s_end3}
TW, TH, GAP, LEFT, TOP, CAPH = 640, 360, 14, 16, 16, 30


def photo(code):
    return str(next(p for p in CAND.glob(code + '_*.jpg')))


def name(code):
    return next(CAND.glob(code + '_*.jpg')).stem.split('_', 1)[1].replace('_', ' ')


def fonts(size):
    return ImageFont.truetype(str(FONT), size) if FONT.exists() else ImageFont.load_default()


def candidates_sheet(groups, out_name, cols=4, tw=480):
    """후보 사진을 묶음별로 한 장에."""
    font, head = fonts(17 if tw >= 480 else 15), fonts(22)
    th = tw * 9 // 16
    rows = []
    for label, g in groups:
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
    out = CAND / out_name
    sheet.save(out, quality=88, optimize=True)
    print('→', out.name, sheet.size, '%.2f MB' % (out.stat().st_size / 1e6))


def tries_sheet(tries, out_name):
    """후보 사진을 39~41쪽에 대 보고 PowerPoint로 찍어 한 장에."""
    prs = Presentation(str(MK.BASE))
    old = list(prs.slides)
    layout = old[5].slide_layout
    note_tpl = [copy.deepcopy(sh._element) for sh in old[5].notes_slide.placeholders]
    flat = [(row, page, code, kw) for row, items in tries for page, code, kw in items]
    specs = [MAKE[page](photo=photo(code), **kw) for _, page, code, kw in flat]
    MK.HW.add_slides(prs, layout, note_tpl, specs)
    MK.drop_slides(prs, old)
    MK.samsung_fonts.remap_prs(prs)
    dst = MK.OUT / 'closing_try.pptx'
    prs.save(str(dst))
    pngs = sorted(MK.render_c.png(dst, MK.OUT / 'closing_try', 1280, 720), key=lambda p: int(p.stem[1:]))
    assert len(pngs) == len(flat), (len(pngs), len(flat))
    font, head = fonts(19), fonts(22)
    rh = TH + CAPH + 34
    sheet = Image.new('RGB', (LEFT * 2 + TW * 3 + GAP * 2, TOP * 2 + len(tries) * rh), (250, 250, 252))
    d = ImageDraw.Draw(sheet)
    k = 0
    for r, (label, items) in enumerate(tries):
        y = TOP + r * rh
        d.text((LEFT, y + 2), label, fill=(60, 50, 90), font=head)
        for c, (page, code, _) in enumerate(items):
            x = LEFT + c * (TW + GAP)
            sheet.paste(Image.open(pngs[k]).convert('RGB').resize((TW, TH), Image.LANCZOS), (x, y + 34))
            d.text((x + 2, y + 34 + TH + 4), '%d쪽  ·  %s %s' % (page, code, name(code)), fill=(40, 40, 50), font=font)
            k += 1
    out = CAND / out_name
    sheet.save(out, quality=88, optimize=True)
    print('→', out.name, sheet.size, '%.2f MB' % (out.stat().st_size / 1e6))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--round', type=int, choices=sorted(ROUNDS))
    a = ap.parse_args()
    for n in ([a.round] if a.round else sorted(ROUNDS)):
        groups, tries, cand_name, try_name = ROUNDS[n]
        candidates_sheet(groups, cand_name, **SHEET.get(n, {}))
        tries_sheet(tries, try_name)


if __name__ == '__main__':
    main()
