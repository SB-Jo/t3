"""vEsB(선제 알림 버튼) 재료 만들기 — 원본 assets는 읽기만 함.

원본 `assets/teaser-ui-light.svg`가 휴대폰 자판 줄의 실타래 버튼을 그림:
  타원 (618, 569) 반지름 22.5×21.5 #CEADF0 + 31×31 아이콘 그림(보라 선) + 빛줄기를 버튼 밖에만 칠하는 가림 타원.
사진(`assets/teaser-retouched-base.png`)에도 같은 자리에 옅은 연보라 원이 있음.

만드는 것
  src/teaser-ui-light-btn.svg  원: 같은 색조의 짙은 보라(FILL), 아이콘: 같은 선 그림을 흰색으로(0.25px 두껍게),
                               원·아이콘·가림 타원을 K배로(버튼 중심 기준)
  src/teaser-base-btn.png      사진 사본에서 원래 연보라 원을 주변 자판 배경으로 지움(K<1이면 줄어든 가장자리에 옛 원이 보이지 않게)

사용: python tools/make-btn-variant.py   → 그다음 node tools/render-teasers.cjs vEsB
"""
import base64
import io
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
L, C, HUE = 0.60, 0.15, 305        # 2차: 채도 0.175 → 0.15, 명도 0.58 → 0.60 (1차 #9359CC)
K = 0.95                            # 버튼 크기 5% 줄임
CX, CY, RX, RY = 618, 569, 22.5, 21.5


def oklch_hex(L, C, h):
    a, b = C * np.cos(np.radians(h)), C * np.sin(np.radians(h))
    l_ = L + .3963377774 * a + .2158037573 * b
    m_ = L - .1055613458 * a - .0638541728 * b
    s_ = L - .0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    rgb = (4.0767416621 * l - 3.3077115913 * m + .2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - .3413193965 * s,
           -.0041960863 * l - .7034186147 * m + 1.7076147010 * s)
    f = lambda c: 255 * (12.92 * c if c <= .0031308 else 1.055 * c ** (1 / 2.4) - .055)
    return '#%02X%02X%02X' % tuple(int(round(min(255, max(0, f(c))))) for c in rgb)


def main():
    fill = oklch_hex(L, C, HUE)
    s = (ASSETS / 'teaser-ui-light.svg').read_text(encoding='utf-8')
    # 아이콘: 알파만 써서 흰색, 8배로 키워 0.25px(1배 기준) 두껍게 → 4배(124px)로 저장
    pat = r'<image x="605" y="553" width="31" height="31" href="data:image/png;base64,([^"]+)"'
    m = re.search(pat, s)
    icon = Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGBA')
    a = icon.getchannel('A').resize((248, 248), Image.BICUBIC).filter(ImageFilter.MaxFilter(5)).resize((124, 124), Image.LANCZOS)
    white = Image.new('RGBA', (124, 124), (255, 255, 255, 0))
    white.putalpha(a)
    buf = io.BytesIO()
    white.save(buf, 'PNG')
    ix, iy, iw = CX + (605 - CX) * K, CY + (553 - CY) * K, 31 * K
    s = s.replace(m.group(0), f'<image x="{ix:.2f}" y="{iy:.2f}" width="{iw:.2f}" height="{iw:.2f}" href="data:image/png;base64,'
                  + base64.b64encode(buf.getvalue()).decode() + '"')
    face = f'<ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="#CEADF0"/>'
    hole = f'<ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="black"/>'
    assert s.count(face) == 1 and s.count(hole) == 1
    s = s.replace(face, f'<ellipse cx="{CX}" cy="{CY}" rx="{RX * K:.2f}" ry="{RY * K:.2f}" fill="{fill}"/>')
    s = s.replace(hole, f'<ellipse cx="{CX}" cy="{CY}" rx="{RX * K:.2f}" ry="{RY * K:.2f}" fill="black"/>')
    s = s.replace('<!-- Flat active button face: no radial light or beam inside the circle. -->',
                  f'<!-- Flat active button face: no radial light or beam inside the circle. (claude_0927 vEsB: fill #CEADF0 -> {fill}, '
                  f'button x{K} about its centre, ink below recolored white with the same shape, ~0.25px bolder) -->')
    (ROOT / 'src' / 'teaser-ui-light-btn.svg').write_text(s, encoding='utf-8')

    # 사진 사본: 옛 연보라 원(재어 둔 타원 (618.2, 567.5) 22.8×21.4, −7.5°)을 2.5px 넓혀 지우고 주변으로 채움
    base = cv2.imread(str(ASSETS / 'teaser-retouched-base.png'), cv2.IMREAD_UNCHANGED)
    mask = np.zeros(base.shape[:2], np.uint8)
    cv2.ellipse(mask, ((618.2, 567.5), (2 * (22.8 + 2.5), 2 * (21.4 + 2.5)), -7.5), 255, -1)
    out = base.copy()
    out[..., :3] = cv2.inpaint(np.ascontiguousarray(base[..., :3]), mask, 6, cv2.INPAINT_TELEA)
    cv2.imwrite(str(ROOT / 'src' / 'teaser-base-btn.png'), out)
    print('fill', fill, '| button', f'{RX * K:.2f}x{RY * K:.2f}', '| icon', f'{iw:.2f}px at ({ix:.2f},{iy:.2f})')


if __name__ == '__main__':
    main()
