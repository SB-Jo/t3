# 비교 시트·진단 그림 생성 — render-teasers.cjs 실행 후 사용
#   python tools/make-sheets.py
# 결과: out/compare-title.png(제목 100%), out/compare-far.png(멀리서 본 크기), out/compare-full.png(전체 1/2),
#       analysis/diagnosis-v0.png(원본 진단: 3:1 미만 픽셀 · 정렬선 · 흑백)
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT, AN = ROOT / 'out', ROOT / 'analysis'
FONT = ROOT.parent / 'assets' / 'fonts'
F_B = ImageFont.truetype(str(FONT / 'NotoSansKR-700.ttf'), 22)
F_R = ImageFont.truetype(str(FONT / 'NotoSansKR-500.ttf'), 17)
F_S = ImageFont.truetype(str(FONT / 'NotoSansKR-500.ttf'), 15)

VARIANTS = [
    ('v0', '원본', 'Weave 그라데이션 + 타원 음영 · 92px · 자간 −0.041em'),
    ('vA', 'A · 흰색 단색 (추천)', '88px · 자간 −0.02em · 부제 왼쪽 정렬 · 모서리 비네트'),
    ('vB', 'B · Weave 연보라 단색', 'Weave #DDD2FF · 나머지는 A와 같음'),
    ('vC', 'C · Weave Bold + Assist Regular', '굵기로 위계 · 나머지는 A와 같음'),
    ('vD', 'D · 가운데 정렬', '제목·부제 중심축 x≈1350 · 나머지는 A와 같음'),
    ('vE', 'E · 최소 변경', '원본 유지 + Weave만 밝은 가로 그라데이션 · 부제는 원본 위치'),
]
TITLE_BOX = (960, 60, 1672, 310)
BG = (246, 245, 250)
INK = (28, 26, 36)
SUB = (110, 104, 128)


def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


LUT = [lin(i) for i in range(256)]


def lum(p):
    return 0.2126 * LUT[p[0]] + 0.7152 * LUT[p[1]] + 0.0722 * LUT[p[2]]


def load(v):
    return Image.open(OUT / f'teaser-{v}.png').convert('RGB')


def label(d, x, y, title, sub):
    d.text((x, y), title, font=F_B, fill=INK)
    d.text((x, y + 30), sub, font=F_S, fill=SUB)


def title_sheet():
    w, h = TITLE_BOX[2] - TITLE_BOX[0], TITLE_BOX[3] - TITLE_BOX[1]
    pad, head = 24, 60
    W = pad + 2 * (w + pad)
    H = pad + 3 * (head + h + pad)
    s = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(s)
    for i, (v, t, sub) in enumerate(VARIANTS):
        x = pad + (i % 2) * (w + pad)
        y = pad + (i // 2) * (head + h + pad)
        label(d, x, y, t, sub)
        s.paste(load(v).crop(TITLE_BOX), (x, y + head))
    s.save(OUT / 'compare-title.png')


def far_sheet(scale=1 / 6, show=2):
    # 1/6로 줄였다가 2배로 키워 보여줌 = 원본 1/3 크기로, 멀리서 봤을 때처럼 해상도가 떨어진 상태
    sw, sh = round(1672 * scale), round(941 * scale)
    w, h = sw * show, sh * show
    pad, head = 20, 60
    W = pad + 3 * (w + pad)
    H = pad + 2 * (head + h + pad)
    s = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(s)
    for i, (v, t, sub) in enumerate(VARIANTS):
        x = pad + (i % 3) * (w + pad)
        y = pad + (i // 3) * (head + h + pad)
        label(d, x, y, t, '')
        small = load(v).resize((sw, sh), Image.LANCZOS).resize((w, h), Image.BILINEAR)
        s.paste(small, (x, y + head - 22))
    s.save(OUT / 'compare-far.png')


def full_sheet():
    w, h = 836, 471
    pad, head = 20, 44
    W = pad + 2 * (w + pad)
    H = pad + 3 * (head + h + pad)
    s = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(s)
    for i, (v, t, sub) in enumerate(VARIANTS):
        x = pad + (i % 2) * (w + pad)
        y = pad + (i // 2) * (head + h + pad)
        d.text((x, y), t, font=F_B, fill=INK)
        s.paste(load(v).resize((w, h), Image.LANCZOS), (x, y + head))
    s.save(OUT / 'compare-full.png')


def ink_box(alpha, box, thr=128):
    a = alpha.crop(box).load()
    bw, bh = box[2] - box[0], box[3] - box[1]
    xs = [x for x in range(bw) if any(a[x, y] > thr for y in range(bh))]
    ys = [y for y in range(bh) if any(a[x, y] > thr for x in range(bw))]
    return box[0] + xs[0], box[1] + ys[0], box[0] + xs[-1], box[1] + ys[-1]


def diagnosis():
    v = 'v0'
    comp, bg = load(v), Image.open(AN / 'bg-v0.png').convert('RGB')
    alpha = Image.open(AN / f'headline-{v}.png').getchannel('A')
    boxes = json.loads((AN / f'boxes-{v}.json').read_text())
    cv = json.loads((AN / 'contrast-all.json').read_text())[v]
    x0, y0, x1, y1 = TITLE_BOX
    crop = comp.crop(TITLE_BOX)
    # ① 대비 3:1 미만 글자 픽셀을 빨강으로
    hot = crop.copy()
    hp, cp, bp, ap = hot.load(), comp.load(), bg.load(), alpha.load()
    for key in ('weave', 'assist', 'tagline'):
        bx0, by0, bx1, by1 = boxes[key]
        if key != 'tagline':
            by1 = min(by1, boxes['tagline'][1] - 1)   # contrast.py와 같은 기준 (부제와 겹치는 줄 상자 아래쪽 제외)
        for y in range(by0, by1 + 1):
            for x in range(bx0, bx1 + 1):
                if ap[x, y] >= 230:
                    lt, lb = lum(cp[x, y]), lum(bp[x, y])
                    r = (max(lt, lb) + .05) / (min(lt, lb) + .05)
                    if r < 3:
                        hp[x - x0, y - y0] = (255, 40, 60)
    # ② 정렬선: 제목·부제의 잉크 왼쪽 끝과 중심
    guide = crop.copy()
    g = ImageDraw.Draw(guide)
    t = ink_box(alpha, (1040, 95, 1672, 205))
    s = ink_box(alpha, (1040, 206, 1672, 262))
    for xx, col in ((t[0], (0, 230, 255)), (s[0], (255, 214, 0))):
        g.line([(xx - x0, 0), (xx - x0, y1 - y0)], fill=col, width=2)
    tc, sc = (t[0] + t[2]) / 2, (s[0] + s[2]) / 2
    for xx, col in ((tc, (0, 230, 255)), (sc, (255, 214, 0))):
        for yy in range(0, y1 - y0, 10):
            g.line([(xx - x0, yy), (xx - x0, yy + 5)], fill=col, width=2)
    # ③ 흑백: 색을 빼면 Weave 앞부분이 배경 밝기에 묻힘
    gray = ImageOps.grayscale(crop).convert('RGB')
    gray_a = ImageOps.grayscale(load('vA').crop(TITLE_BOX)).convert('RGB')

    w, h = crop.size
    pad, head = 24, 64
    W = pad + 2 * (w + pad)
    H = pad + 2 * (head + h + pad)
    sheet = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(sheet)
    panels = [
        (hot, '① 대비 3:1 미만 글자 픽셀 (빨강)', f"Weave {cv['weave']['below_3']}% · Assist {cv['assist']['below_3']}% · 부제 {cv['tagline']['below_3']}% — W·e의 보라 시작색과 상단 하이라이트 경계"),
        (guide, '② 정렬: 제목(하늘색)과 부제(노랑)의 왼쪽 끝·중심', f'왼쪽 끝 {t[0]} vs {s[0]} ({s[0] - t[0]}px 차이) · 중심 {tc:.0f} vs {sc:.0f} — 어느 쪽에도 맞지 않음'),
        (gray, '③ 흑백으로 본 원본', '색을 빼면 Weave의 W·e가 배경 밝기에 묻히고 Assist만 남음'),
        (gray_a, '③ 흑백으로 본 A (흰색 단색)', '두 단어의 밝기가 같아 한 덩어리의 워드마크로 읽힘'),
    ]
    for i, (im, tt, sub) in enumerate(panels):
        x = pad + (i % 2) * (w + pad)
        y = pad + (i // 2) * (head + h + pad)
        label(d, x, y, tt, sub)
        sheet.paste(im, (x, y + head))
    sheet.save(AN / 'diagnosis-v0.png')
    return t, s


E_STEPS = [
    ('v0', '원본', '시작 #986BCB · 24° 사선 + 상단 흰 하이라이트'),
    ('vE', 'E · 이전', '시작 #D2C3FF · 가로 그라데이션'),
    ('vE35', 'E35 · 원본 보라 쪽으로 35%', '시작 #BDA4ED'),
    ('vE50', 'E50 · 원본과 E의 중간 (요청안)', '시작 #B597E5'),
    ('vE65', 'E65 · 원본 보라 쪽으로 65%', '시작 #AC8ADD'),
    ('vEs', 'E · 채도 우선', '시작 #BE9CFA · 채도는 E50보다 높고 밝기는 덜 낮춤'),
]


def e_sheet():
    # E 시작색 단계 비교: 왼쪽 제목 100% · 오른쪽 멀리서 본 크기(1/6 해상도를 2배로)
    contrast = json.loads((AN / 'contrast-all.json').read_text())
    cw, ch = TITLE_BOX[2] - TITLE_BOX[0], TITLE_BOX[3] - TITLE_BOX[1]
    sw, sh = round(1672 / 6), round(941 / 6)
    fw, fh = sw * 2, sh * 2
    pad, head, gap = 24, 60, 16
    rowh = head + max(ch, fh) + pad
    W = pad * 2 + cw + gap + fw
    H = pad + rowh * len(E_STEPS)
    s = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(s)
    for i, (v, t, sub) in enumerate(E_STEPS):
        y = pad + i * rowh
        c = contrast[v]['weave']
        label(d, pad, y, t, f"{sub} · Weave 글자 픽셀 3:1 미만 {c['below_3']}% · 하위 10% 대비 {c['p10_ratio']}:1")
        im = load(v)
        s.paste(im.crop(TITLE_BOX), (pad, y + head))
        s.paste(im.resize((sw, sh), Image.LANCZOS).resize((fw, fh), Image.BILINEAR), (pad + cw + gap, y + head))
    s.save(OUT / 'compare-E-steps.png')


if __name__ == '__main__':
    title_sheet()
    far_sheet()
    full_sheet()
    e_sheet()
    t, s = diagnosis()
    print('title ink', t, 'tagline ink', s)
