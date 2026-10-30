# 삼성 공식 KV 조사 시트 — research/crops의 잘라 둔 이미지로 research/samsung-kv-reference.png 생성
#   python tools/make-research.py
# 원본 출처는 README.md '조사' 절 참고. 자간 실측 수치는 README와 같은 방법(x높이 대비 잉크 전체 폭)으로 계산해 표시합니다.
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / 'research' / 'crops'
FONT = ROOT.parent / 'assets' / 'fonts'
F_B = ImageFont.truetype(str(FONT / 'NotoSansKR-700.ttf'), 22)
F_S = ImageFont.truetype(str(FONT / 'NotoSansKR-500.ttf'), 16)
BG, INK, SUB = (246, 245, 250), (28, 26, 36), (110, 104, 128)
PW = 900


def fit(im, w):
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def segs(g, thr):
    w, h = g.size
    px = g.load()
    cols = [any(px[x, y] < thr for y in range(h)) for x in range(w)]
    out, s = [], None
    for x, c in enumerate(cols + [False]):
        if c and s is None:
            s = x
        if not c and s is not None:
            out.append((s, x - 1))
            s = None
    return out


def width_per_xheight(im, thr=128):
    # 첫 글자 G 다음의 'a'로 x높이를 재고, 잉크 전체 폭을 x높이로 나눔
    g = im.convert('L')
    ss = segs(g, thr)
    px = g.load()
    a0, a1 = ss[1]
    ys = [y for y in range(g.height) if any(px[x, y] < thr for x in range(a0, a1 + 1))]
    return (ss[-1][1] - ss[0][0] + 1) / (ys[-1] - ys[0] + 1), ys[-1] - ys[0] + 1


def main():
    ref = Image.open(C / 's26-presale-kv-galaxy-s26-series.png')
    r0 = Image.open(C / 'sharpsans-bold-render-track0.png')
    r4 = Image.open(C / 'sharpsans-bold-render-track-0.041.png')
    k_ref, xh_ref = width_per_xheight(ref)
    k0, xh0 = width_per_xheight(r0)
    k4, _ = width_per_xheight(r4)

    panels = [
        ('① Galaxy Unpacked 2026 초대장 (Samsung Global Newsroom)', 'Sharp Sans Bold 흰색 단색 · 날짜 줄은 작고 가는 굵기 · 두 줄 왼쪽 정렬',
         fit(Image.open(C / 'unpacked2026-invitation-title.png'), PW)),
        ('② Galaxy S26 Ultra 공개 무대 화면 (Samsung Global Newsroom)', "제목 Bold · 'Galaxy AI' Regular · 글자는 연보라 단색(사진 측정 #F1E2FC 근사) · 그라데이션은 별 아이콘에만 · 가운데 정렬",
         fit(Image.open(C / 's26-launch-stage-title.png'), PW)),
        ('③ 갤럭시 S26 시리즈 사전 판매 KV (삼성전자 뉴스룸)', "'Galaxy S26 Series' Bold · 'Galaxy AI' Regular + 그라데이션 별 아이콘 · 한글은 굵게 · 전부 단색 · 가운데 정렬",
         fit(Image.open(C / 's26-presale-kv-title.png'), round(PW * 0.62))),
    ]
    s = xh_ref / xh0
    rows = [
        (f'공식 KV 실측 — x높이 대비 전체 폭 {k_ref:.2f}', ref),
        (f'같은 서체 · 자간 0 — {k0:.2f}  ← 공식 KV와 거의 같음', r0.resize((round(r0.width * s), round(r0.height * s)), Image.LANCZOS)),
        (f'같은 서체 · 자간 −0.041em (원본 티저) — {k4:.2f}  ← 약 {100 * (1 - k4 / k0):.0f}% 좁음', r4.resize((round(r4.width * s), round(r4.height * s)), Image.LANCZOS)),
    ]
    track = Image.new('RGB', (PW, 3 * 118 + 10), 'white')
    td = ImageDraw.Draw(track)
    for i, (name, im) in enumerate(rows):
        im = fit(im, round(im.width * 0.42))
        y = 6 + i * 118
        track.paste(im.crop((0, 0, min(im.width, 720), min(im.height, 92))), (0, y + 22))
        td.text((4, y), name, font=F_S, fill=INK)
    panels.append(('④ 자간 실측: ③의 “Galaxy S26 Series” vs 같은 서체 렌더', 'x높이를 맞춘 뒤 잉크 전체 폭 비교 — 공식 KV는 기본 자간(0)에 해당', track))

    pad, head = 24, 62
    H = pad + sum(head + p[2].height + pad for p in panels)
    sheet = Image.new('RGB', (pad * 2 + PW, H), BG)
    d = ImageDraw.Draw(sheet)
    y = pad
    for t, sub, im in panels:
        d.text((pad, y), t, font=F_B, fill=INK)
        d.text((pad, y + 30), sub, font=F_S, fill=SUB)
        sheet.paste(im, (pad, y + head))
        y += head + im.height + pad
    sheet.save(ROOT / 'research' / 'samsung-kv-reference.png')
    print(f'ref {k_ref:.3f} · track0 {k0:.3f} · track-0.041 {k4:.3f}')


if __name__ == '__main__':
    main()
