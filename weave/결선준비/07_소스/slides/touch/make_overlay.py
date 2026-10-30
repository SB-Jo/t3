"""덱 공통 터치 표시(누르는 손 + 보라 반짝임 선) 오버레이 PNG 생성.

기준은 2쪽 만화(overview-comic 사본, revision-claude-touch.css)의 4컷·3컷:
- 손: overview-comic/assets/icons/swipe-hand.svg, 장표 크기에서 폭 27.6px(만화 49px × 0.5628)
  누르기(tap)는 rotate(-12deg), 기준점 (35%, 8%) / 밀어 올리기(swipe)는 회전 없음
- 반짝임: 선 3개(누르기, 213°·258°·303°) 또는 2개(밀기, 손끝 양옆 192°·348°)
  굵기 1.75px, 길이 4.8/5.9/4.8px, 보라 그라데이션 #A67CF2→#7B4BD8, 흰 테두리 3.3px
  누르는 대상(버튼·키) 바깥에서 시작: r0 = 대상 반지름 + 3px

사용: python make_overlay.py  → touch/out/*.svg, *.png (render-overlay.cjs로 8배 렌더)
"""
import json
import math
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
HAND_SVG = Path(__file__).resolve().parents[1] / 'comic' / 'assets' / 'icons' / 'swipe-hand.svg'
HW, HH = 27.6, 35.5          # 손 상자 (장표 px)
TIP = (31.3 / 80, 4.4 / 102)  # 회전 전 손끝(검지 끝) 위치 비율
ORIGIN = (0.35, 0.08)         # rotate 기준점 비율
STROKE_W, HALO_W = 1.75, 3.3


def hand_box_for_tip(tip, rotate):
    """손끝이 tip(장표 px)에 오도록 하는 손 상자 왼쪽 위."""
    tx, ty = TIP[0] * HW, TIP[1] * HH
    ox, oy = ORIGIN[0] * HW, ORIGIN[1] * HH
    a = math.radians(rotate)
    rx, ry = tx - ox, ty - oy
    x2 = ox + rx * math.cos(a) - ry * math.sin(a)
    y2 = oy + rx * math.sin(a) + ry * math.cos(a)
    return tip[0] - x2, tip[1] - y2


def strokes(center, r0, angles, lens):
    out = []
    for a, l in zip(angles, lens):
        t = math.radians(a)
        out.append((center[0] + r0 * math.cos(t), center[1] + r0 * math.sin(t),
                    center[0] + (r0 + l) * math.cos(t), center[1] + (r0 + l) * math.sin(t)))
    return out


def build(name, tip, rotate, segs, pad=6):
    """tip: 손끝(장표 px), segs: 반짝임 선분 목록. 캔버스는 손·선을 모두 담는 최소 상자 + 여백."""
    bx, by = hand_box_for_tip(tip, rotate)
    xs = [bx, bx + HW] + [s[0] for s in segs] + [s[2] for s in segs]
    ys = [by, by + HH] + [s[1] for s in segs] + [s[3] for s in segs]
    x0, y0 = math.floor(min(xs) - pad), math.floor(min(ys) - pad)
    x1, y1 = math.ceil(max(xs) + pad), math.ceil(max(ys) + pad)
    hand = HAND_SVG.read_text()
    inner = hand[hand.index('>') + 1: hand.rindex('</svg>')].replace('id="skin"', f'id="skin-{name}"').replace('url(#skin)', f'url(#skin-{name})')
    d = ''.join(f'M{a - x0:.2f} {b - y0:.2f}L{c - x0:.2f} {e - y0:.2f}' for a, b, c, e in segs)
    ox, oy = bx - x0 + ORIGIN[0] * HW, by - y0 + ORIGIN[1] * HH
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x1 - x0} {y1 - y0}" width="{(x1 - x0) * 8}" height="{(y1 - y0) * 8}">
  <defs>
    <linearGradient id="spark-{name}" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#A67CF2"/><stop offset="1" stop-color="#7B4BD8"/></linearGradient>
    <filter id="shadow-{name}" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="1.7" stdDeviation="1.2" flood-color="#5F3D73" flood-opacity="0.2"/></filter>
  </defs>
  <g fill="none" stroke-linecap="round">
    <path d="{d}" stroke="#FFFFFF" stroke-width="{HALO_W}"/>
    <path d="{d}" stroke="url(#spark-{name})" stroke-width="{STROKE_W}"/>
  </g>
  <g filter="url(#shadow-{name})" transform="rotate({rotate} {ox:.2f} {oy:.2f})">
    <svg x="{bx - x0:.2f}" y="{by - y0:.2f}" width="{HW}" height="{HH}" viewBox="0 0 80 102" preserveAspectRatio="none">{inner}</svg>
  </g>
</svg>'''
    out = HERE / 'out'
    out.mkdir(exist_ok=True)
    (out / f'{name}.svg').write_text(svg)
    return dict(name=name, x=x0, y=y0, w=x1 - x0, h=y1 - y0, tip=tip, rotate=rotate)


def tap(name, tip, target_center, target_r, angles=(213, 258, 303)):
    return build(name, tip, -12, strokes(target_center, target_r + 3.0, angles, (4.8, 5.9, 4.8)))


def swipe(name, tip):
    center = (tip[0], tip[1] + 4.2)
    return build(name, tip, 0, strokes(center, 5.6, (192, 348), (4.8, 4.8)))


if __name__ == '__main__':
    specs = [
        # 5쪽 카드 2: 키보드의 실타래 키(원 중심 68.8,616.0 · 반지름 19.1)를 누름
        tap('p05-card2-tap', tip=(75.7, 616.4), target_center=(68.8, 616.0), target_r=19.1),
        # 5쪽 카드 1: '위로 올려 기억 검색' — 화살표 오른쪽에서 밀어 올림
        swipe('p05-card1-swipe', tip=(504.6, 378.2)),
        # 8쪽: '입력하기' 버튼(y 573.9~608.3) 오른쪽을 누름 — 옛 커서 끝 자리. 선은 버튼 위쪽으로
        tap('p08-input-tap', tip=(1048.4, 584.1), target_center=(1048.4, 584.1), target_r=13, angles=(235, 275, 315)),
    ]
    (HERE / 'out' / 'overlays.json').write_text(json.dumps(specs, ensure_ascii=False, indent=1))
    subprocess.run(['node', str(HERE / 'render-overlay.cjs')] + [s['name'] for s in specs], check=True,
                   env={'NODE_PATH': '/tmp/claude-weave-0927/node_modules', 'LD_LIBRARY_PATH': '/tmp/claude-weave-0927/chrome-sysroot/usr/lib/x86_64-linux-gnu', 'PATH': '/usr/bin:/bin:/home/jaeung/.nvm/versions/node/v24.19.0/bin'})
    print(json.dumps(specs, ensure_ascii=False))
