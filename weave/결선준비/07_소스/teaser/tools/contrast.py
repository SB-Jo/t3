# 제목 글자 대비 측정 — render-teasers.cjs 실행 후 사용
#   python tools/contrast.py [v0 vA ...]      (인자 없으면 out/teaser-*.png 전부)
# 방법: WCAG 대비비. 제목 레이어(analysis/headline-{v}.png) 알파 ≥ 230인 글자 내부 픽셀마다
#       최종 합성(out/teaser-{v}.png)의 글자 색과, 같은 위치의 제목 없는 배경(analysis/bg-{v}.png: 음영·비네트 포함) 색을 비교.
#       글자 그림자가 만드는 대비는 배경에 넣지 않았으므로 보수적인 값입니다. 결과는 analysis/contrast-all.json
import json
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT, AN = ROOT / 'out', ROOT / 'analysis'


def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


LUT = [lin(i) for i in range(256)]


def lum(p):
    return 0.2126 * LUT[p[0]] + 0.7152 * LUT[p[1]] + 0.0722 * LUT[p[2]]


def measure(v):
    comp = Image.open(OUT / f'teaser-{v}.png').convert('RGB').load()
    bg = Image.open(AN / f'bg-{v}.png').convert('RGB').load()
    a = Image.open(AN / f'headline-{v}.png').getchannel('A').load()
    boxes = json.loads((AN / f'boxes-{v}.json').read_text())
    out = {}
    for k in ('weave', 'assist', 'tagline'):
        x0, y0, x1, y1 = boxes[k]
        if k != 'tagline':
            # 단어 상자(줄 상자)는 아래로 부제 윗부분과 겹치므로, 부제 상자 위에서 자름 (제목 잉크는 y≈196까지)
            y1 = min(y1, boxes['tagline'][1] - 1)
        rs, tl, bl = [], [], []
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if a[x, y] >= 230:
                    lt, lb = lum(comp[x, y]), lum(bg[x, y])
                    rs.append((max(lt, lb) + .05) / (min(lt, lb) + .05))
                    tl.append(lt)
                    bl.append(lb)
        rs.sort()
        n = len(rs)
        out[k] = {'pixels': n, 'median_ratio': round(rs[n // 2], 2), 'p10_ratio': round(rs[n // 10], 2),
                  'below_3': round(100 * sum(r < 3 for r in rs) / n, 1), 'below_4_5': round(100 * sum(r < 4.5 for r in rs) / n, 1),
                  'text_lum_mean': round(sum(tl) / n, 3), 'bg_lum_mean': round(sum(bl) / n, 3)}
    return out


if __name__ == '__main__':
    vs = sys.argv[1:] or sorted(p.stem.removeprefix('teaser-') for p in OUT.glob('teaser-v*.png'))
    path = AN / 'contrast-all.json'
    res = json.loads(path.read_text()) if path.exists() else {}
    res['method'] = ('WCAG 대비비. 제목 레이어 알파 ≥ 230인 글자 내부 픽셀마다, 최종 합성 이미지의 글자 색과 같은 위치의 '
                     '제목 없는 배경(analysis/bg-{v}.png, 음영·비네트 포함, 글자 그림자 제외) 색을 비교')
    for v in vs:
        res[v] = measure(v)
        print(v, ' | '.join(f"{k}: 중앙값 {o['median_ratio']} 하위10% {o['p10_ratio']} 3:1미만 {o['below_3']}%" for k, o in res[v].items()))
    path.write_text(json.dumps(res, ensure_ascii=False, indent=1))
