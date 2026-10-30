"""07번(HOW IT WORKS) 11차: 바깥 여백을 줄이고, 줄어든 만큼 상자·간격·글자를 키움 (사용자 요청 2026-09-27 22시).

- 콘텐츠 영역: x 86~1194 · y 172~640 → x 70~1210 · y 169~654  (좌우 여백 86→70, 아래 80→66, 약 18% 감소)
  위치는 영역에 맞춰 비례 이동, 폭은 kx(1.029), 높이는 ky(1.036), 정사각형(아이콘·번호)은 평균 배율
- 글자: 기본은 1.03배, 작아 보이던 11~13px 글자는 1.06배, 그 사이(13.5~18px)는 1.04배
- 머리(칩·제목·부제)는 theme.css 규격 그대로 두고, 부제 문구만 바꿈

사용: python tools/loosen_page07.py   (pages/page-07-pipeline.html을 고침. 10차본은 v10/에 있음)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'pages' / 'page-07-pipeline.html'

X0, X1, NX0, NX1 = 86.0, 1194.0, 70.0, 1210.0
Y0, Y1, NY0, NY1 = 172.0, 640.0, 169.0, 654.0
KX = (NX1 - NX0) / (X1 - X0)
KY = (NY1 - NY0) / (Y1 - Y0)
KA = (KX + KY) / 2


def fk(px):
    """글자 배율: 작은 글자일수록 조금 더."""
    return 1.06 if px <= 13.01 else (1.04 if px <= 18.01 else 1.03)


def num(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return s


def scale_decl(prop, val, inline):
    """한 CSS 선언의 px 값을 바꿈."""
    def px_list(f):
        return re.sub(r'(-?[0-9.]+)px', lambda m: num(f(float(m.group(1)))) + 'px', val)
    if prop == 'left' and inline:
        return px_list(lambda v: NX0 + (v - X0) * KX)
    if prop == 'top' and inline:
        return px_list(lambda v: NY0 + (v - Y0) * KY)
    if prop in ('width',):
        return px_list(lambda v: v * KX)
    if prop in ('height',):
        return px_list(lambda v: v * KY)
    if prop == 'line-height':
        return px_list(lambda v: v * KY)
    if prop == 'font-size':
        return px_list(lambda v: v * fk(v))
    if prop in ('border-radius', 'gap'):
        return px_list(lambda v: v * KA)
    if prop == 'font':        # 예: 700 12.5px/24px 'Inter'
        m = re.match(r'(\s*\d+\s+)([0-9.]+)px/([0-9.]+)px(.*)', val)
        if m:
            f, lh = float(m.group(2)), float(m.group(3))
            return f'{m.group(1)}{num(f * fk(f))}px/{num(lh * KY)}px{m.group(4)}'
    return val


def scale_style(style, inline):
    decls = [d for d in style.split(';')]
    out = []
    # 정사각형(폭=높이) 요소는 평균 배율로 폭·높이를 같게 유지
    wm = re.search(r'(?:^|;)\s*width\s*:\s*([0-9.]+)px', style)
    hm = re.search(r'(?:^|;)\s*height\s*:\s*([0-9.]+)px', style)
    square = bool(wm and hm and abs(float(wm.group(1)) - float(hm.group(1))) < 0.01)
    for d in decls:
        if ':' not in d:
            out.append(d)
            continue
        prop, val = d.split(':', 1)
        p = prop.strip()
        if square and p in ('width', 'height'):
            val = re.sub(r'([0-9.]+)px', lambda m: num(float(m.group(1)) * KA) + 'px', val)
        else:
            val = scale_decl(p, val, inline)
        out.append(f'{prop}:{val}')
    return ';'.join(out)


def main():
    s = P.read_text(encoding='utf-8')
    head, rest = s.split('</style>', 1)
    css_start = head.index('<style>') + len('<style>')
    css = head[css_start:]

    def css_rule(m):
        sel, body = m.group(1), m.group(2)
        if 'svg.links' in sel:          # 연결선 레이어는 장표 전체 크기 그대로
            return m.group(0)
        return sel + '{' + scale_style(body, inline=False) + '}'
    css = re.sub(r'([^{}]+)\{([^{}]*)\}', css_rule, css)
    head = head[:css_start] + css

    body, script = rest.split('<script>', 1)
    body = re.sub(r'style="([^"]*)"', lambda m: 'style="' + scale_style(m.group(1), inline=True) + '"', body)
    body = body.replace('<div class="t-sub" data-x>무거운 언어모델 대신, 가벼운 임베딩 모델로 기록을 찾고 단서를 잇습니다.</div>',
                        '<div class="t-sub" data-x>찾은 기록이 다음 단서가 되어, 기억나지 않던 답까지 이어집니다.</div>')
    assert '기억나지 않던 답까지' in body
    P.write_text(head + '</style>' + body + '<script>' + script, encoding='utf-8')
    print(f'KX={KX:.4f} KY={KY:.4f}')


if __name__ == '__main__':
    main()
