"""장표를 위아래로 이어 붙인 '이음매 판(seamless)' 배경·합성 (export_png.py에서 씀).

모든 값은 2560×1440(2배) 기준 px, 배치표(LAYOUTS)만 1280 기준.

두 가지 방식
1) 자연스럽게 잇기 (지금은 안 씀 — 3-4쪽도 2)로 바꿈, 2026-09-28): 장표별 원래 배경을 이어 붙이고 경계만 섞음
   canvas_bg  위 장표 끝 BAND + 아래 장표 처음 BAND를 위 마지막 줄 → 아래 첫 줄로 부드럽게
   soften     경계 둘레(±SOFT_B)만 넓게 흐려, 한 줄을 늘여 섞을 때 생기는 세로 줄무늬 없이 번지게
2) 한 장처럼 디자인 (3-4, 5-9, 10-12, 13-15, 17-18, 19쪽 — 사용자 2026-09-28):
   design_bg  장표마다 반복되던 바탕 대신 묶음 전체를 잇는 한 장의 그라데이션 + LAYOUTS 자리의 노랑·보라 빛
              (빛 모양·색은 덱 배경 도형과 같은 타원 그라데이션)
   compose_design
              - 흐린 장면(6~8쪽 인물 뒤)은 배경 층으로 옮겨 아래로 부드럽게 사라지게(장표 끝에서 잘리지 않게)
              - 장표 아래로 넘치는 그래픽(5쪽 손, 휴대폰·카드 그림자)은 Chromium 층에서 가져와 다음 장표 밑에 깔기
              - 인물 아랫단(장표 끝에서 잘린 흉상)만 FADE만큼 약하게 흐림
   dividers   장표 사이 페이지 구분선(양옆을 띄움)
"""
import cv2
import numpy as np

H = 1440
BAND = 300
SOFT_B = 420
FADE = 40
S = 2.0
EXT = 200                                   # Chromium 층에서 장표 아래로 더 찍은 높이(2배 기준, render_layers.cjs의 100×2)

PEACH = dict(r=(769.0, 659.0), stops=[(0.0, (255, 226, 130), .42), (.30, (255, 238, 185), .18), (.60, (255, 250, 235), 0.0)])
LAV = dict(r=(746.7, 431.5), stops=[(0.0, (186, 166, 255), .34), (.40, (220, 208, 255), .16), (.72, (248, 245, 255), 0.0)])
BASE = ((252, 251, 255), (244, 240, 255))  # 묶음 전체 바탕: 위 → 아래
# 덱 크기 빛('p'·'l'): PowerPoint가 실제로 그린 덱 배경 빛의 반경을 3쪽 렌더(배경 도형만)에 맞춰 잰 값.
#   위 PEACH·LAV(도형 정의에서 계산)보다 작고, 원래 장표와 같은 느낌이 필요한 3-4쪽에 씀
PEACH_DECK = dict(r=(525.0, 505.0), stops=PEACH['stops'])   # 초점을 지나는 가로·세로 줄에서 맞춤(평균 오차 0.3~0.5/255)
LAV_DECK = dict(r=(490.0, 360.0), stops=LAV['stops'])
KINDS = {'P': PEACH, 'L': LAV, 'p': PEACH_DECK, 'l': LAV_DECK}

# (쪽 순서, x, 그 장표 안 y — 1280 기준, 'P' 노랑·'L' 보라('p'·'l'은 덱 크기), 크기 배율, 세기 배율)
LAYOUTS = {
    (3, 4): [                              # 원래 장표 빛(덱 크기) 그대로에서 두 곳만 옮김 (사용자 요청)
        (0, 1184, 40.5, 'p', 1.0, 1.0),   # 3쪽 오른쪽 위 노랑 (원래 자리)
        (0, 40, 742, 'l', 1.30, 0.78),    # 3쪽 왼쪽 아래 보라: 멍든 듯 진해서 넓게·연하게, 중심은 왼쪽 아래로 더 (사용자 요청)
        (1, 1143, 606, 'p', 1.0, 1.0),    # 4쪽 노랑: 오른쪽 위에서 오른쪽 아래 인물(지현) 둘레로
        (1, 72, 678.4, 'l', 1.0, 1.0),    # 4쪽 왼쪽 아래 보라 (원래 자리)
    ],
    (5, 9): [
        (0, 1200, 40, 'L', 1.00, 0.80),   # 5쪽 오른쪽 위 보라
        (0, 1230, 610, 'P', 0.70, 0.60),  # 5쪽 (3) 카드 옆 작은 노랑
        (0, 50, 700, 'L', 1.15, 0.90),    # 5→6 경계 왼쪽 보라
        (1, 1250, 300, 'L', 0.90, 0.75),  # 6쪽 카드 뒤 보라
        (1, 1230, 700, 'L', 0.95, 0.80),  # 6→7 경계 오른쪽 보라
        (2, 110, 560, 'L', 1.30, 1.00),   # 7쪽 왼쪽 인물(보라 옷) 둘레 보라
        (2, 1180, 640, 'L', 1.10, 1.00),  # 7쪽 오른쪽 인물 둘레 보라
        (3, 120, 560, 'P', 1.30, 1.00),   # 8쪽 왼쪽 인물(노란 옷) 둘레 노랑
        (3, 1180, 640, 'P', 1.10, 1.00),  # 8쪽 오른쪽 인물 둘레 노랑
        (3, 1240, 130, 'L', 0.85, 0.65),  # 8쪽 오른쪽 위 옅은 보라
        (4, 60, 80, 'L', 0.95, 0.70),     # 9쪽 왼쪽 위 보라
        (4, 1220, 420, 'L', 1.00, 0.80),  # 9쪽 오른쪽 보라
        (4, 72, 690, 'L', 1.00, 0.95),    # 9쪽 왼쪽 아래(끝)
    ],
    (10, 12): [
        (0, 1190, 40, 'P', 1.00, 0.85),   # 10쪽 오른쪽 위 노랑
        (0, 60, 420, 'L', 1.00, 0.80),    # 10쪽 왼쪽 보라
        (1, 1220, -20, 'L', 1.05, 0.80),  # 10→11 경계 오른쪽 보라
        (1, 70, 380, 'P', 0.85, 0.70),    # 11쪽 왼쪽 노랑
        (1, 1210, 520, 'L', 0.85, 0.65),  # 11쪽 오른쪽 아래 보라
        (2, 60, -10, 'L', 1.00, 0.80),    # 11→12 경계 왼쪽 보라
        (2, 1230, 330, 'L', 0.95, 0.70),  # 12쪽 오른쪽 보라
        (2, 80, 690, 'L', 1.00, 0.95),    # 12쪽 왼쪽 아래(끝)
    ],
    (13, 15): [
        (0, 1200, 40, 'P', 0.95, 0.80),   # 13쪽 오른쪽 위 노랑
        (0, 60, 640, 'L', 1.10, 0.90),    # 13쪽 왼쪽 아래 → 14쪽으로 걸침
        (1, 60, 715, 'P', 0.80, 0.65),    # 14→15 사이 왼쪽 빈 곳 작은 노랑 (14쪽 왼쪽 위에서 옮김: 13쪽 보라와 겹쳐 어색 — 사용자)
        (1, 1230, 600, 'L', 1.00, 0.80),  # 14쪽 오른쪽 아래 보라
        (2, 1220, 40, 'L', 0.90, 0.70),   # 15쪽 오른쪽 위 보라
        (2, 1200, 660, 'P', 0.80, 0.70),  # 15쪽 오른쪽 아래 노랑
        (2, 80, 690, 'L', 1.05, 0.95),    # 15쪽 왼쪽 아래(끝)
    ],
    (17, 18): [
        (0, 1200, 40, 'P', 0.95, 0.75),   # 17쪽 오른쪽 위 노랑
        (0, 60, 690, 'L', 1.05, 0.80),    # 17→18 경계 왼쪽 보라
        (1, 1230, 400, 'P', 0.90, 0.70),  # 18쪽 오른쪽 노랑 (보라였던 것 — 사용자 요청)
        (1, 80, 690, 'L', 1.00, 0.90),    # 18쪽 왼쪽 아래(끝)
    ],
    (19, 19): [                            # 19쪽(Members) 단독: 오른쪽 위 노랑·왼쪽 아래 보라만 (사용자 요청)
        (0, 1190, 60, 'P', 1.10, 0.80),   # 오른쪽 위 노랑
        (0, 90, 680, 'L', 1.05, 0.80),    # 왼쪽 아래 보라
    ],
}


def smooth(u):
    return u * u * (3 - 2 * u)


def offsets(n, gaps):
    offs = [0]
    for g in gaps:
        offs.append(offs[-1] + H + g)
    return offs


# ---------------------------------------------------------------- 1) 자연스럽게 잇기
def canvas_bg(gs, gaps):
    n, wd = len(gs), gs[0].shape[1]
    offs = offsets(n, gaps)
    bg = np.zeros((offs[-1] + H, wd, 3), np.float32)
    for g, y0 in zip(gs, offs):
        bg[y0:y0 + H] = g
    centers = []
    for i in range(n - 1):
        top_end, bot_start = offs[i] + H, offs[i + 1]
        a0, a1 = min(top_end, bot_start) - BAND, max(top_end, bot_start) + BAND
        ys = np.arange(a0, a1)
        w = smooth((ys - a0) / (a1 - a0)).astype(np.float32)[:, None, None]
        last, first = gs[i][-1].astype(np.float32)[None], gs[i + 1][0].astype(np.float32)[None]
        above = np.where((ys < top_end)[:, None, None], bg[a0:a1], last)
        below = np.where((ys >= bot_start)[:, None, None], bg[a0:a1], first)
        bg[a0:a1] = (1 - w) * above + w * below
        centers.append((top_end + bot_start) / 2)
    return bg, centers


def soften(bg, centers, B=SOFT_B, sy=150, sx=110):
    if not centers:
        return bg
    h, w = bg.shape[:2]
    small = cv2.resize(bg, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), sigmaX=sx / 4, sigmaY=sy / 4, borderType=cv2.BORDER_REFLECT)
    blur = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
    ys = np.arange(h, dtype=np.float32)
    wgt = np.zeros(h, np.float32)
    for c in centers:
        wgt = np.maximum(wgt, 1 - smooth(np.clip(np.abs(ys - c) / B, 0, 1)))
    return wgt[:, None, None] * blur + (1 - wgt[:, None, None]) * bg


# ---------------------------------------------------------------- 2) 한 장처럼 디자인
def blob(canvas, cx, cy, rx, ry, stops):
    h, w = canvas.shape[:2]
    reach = max(s for s, _, _ in stops)
    y0, y1 = int(max(0, cy - ry * reach - 2)), int(min(h, cy + ry * reach + 2))
    x0, x1 = int(max(0, cx - rx * reach - 2)), int(min(w, cx + rx * reach + 2))
    if y0 >= y1 or x0 >= x1:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt(((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2)
    A = np.zeros_like(d)
    P = np.zeros(d.shape + (3,), np.float32)
    for (s0, c0, a0), (s1, c1, a1) in zip(stops, stops[1:]):
        m = (d >= s0) & (d < s1)
        f = ((d[m] - s0) / (s1 - s0))[:, None]
        p0, p1 = np.array(c0, np.float32) * a0, np.array(c1, np.float32) * a1
        A[m] = a0 + f[:, 0] * (a1 - a0)
        P[m] = p0 + f * (p1 - p0)
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - A[..., None]) + P


def design_bg(n, gaps, layout, width=2560):
    offs = offsets(n, gaps)
    total = offs[-1] + H
    t = np.linspace(0, 1, total, dtype=np.float32)[:, None, None]
    bg = (1 - t) * np.array(BASE[0], np.float32) + t * np.array(BASE[1], np.float32)
    bg = np.repeat(bg, width, axis=1)
    for page, x, y, kind, scale, amul in layout:
        g = KINDS[kind]
        stops = [(st, col, a * amul) for st, col, a in g['stops']]
        blob(bg, S * x, offs[page] + S * y, S * g['r'][0] * scale, S * g['r'][1] * scale, stops)
    return bg, offs


def over(canvas, y0, rgba):
    """canvas의 y0행부터 RGBA 그림을 덧칠(캔버스 밖은 버림)."""
    h = canvas.shape[0]
    a0, a1 = max(0, y0), min(h, y0 + rgba.shape[0])
    if a0 >= a1:
        return
    part = rgba[a0 - y0:a1 - y0].astype(np.float32)
    al = part[..., 3:4] / 255.0
    canvas[a0:a1] = canvas[a0:a1] * (1 - al) + part[..., :3] * al


def compose_design(Ws, Ks, bg, offs, layers=None, fade=FADE):
    canvas = bg.copy()
    layers = layers or [None] * len(Ws)
    for y0, L in zip(offs, layers):                     # 흐린 장면: 배경 층, 장표 끝까지 부드럽게 사라짐
        if L is not None and L.get('scene') is not None:
            sc = L['scene'][:H].astype(np.float32).copy()
            rows = np.arange(H, dtype=np.float32)
            ramp = 1 - smooth(np.clip((rows - 1220) / 220, 0, 1))     # 610~720px(1280 기준)에서 사라짐 → 아래 장표로 번지지 않음
            sc[..., 3] *= ramp[:, None]
            over(canvas, y0, sc)
    for y0, L in zip(offs, layers):                     # 장표 아래로 넘친 그래픽(손·그림자): 다음 장표 밑에 깔림. 인물은 뺀 층
        if L is not None and L.get('spill') is not None:
            over(canvas, y0 + H, L['spill'][H:H + EXT])
    if fade:
        u = np.clip((H - 1 - np.arange(H)) / fade, 0, 1)
        ramp = smooth(u).astype(np.float32)[:, None, None]
    for y0, w, k, L in zip(offs, Ws, Ks, layers):       # 글자·그림: 장표 순서대로(겹치면 아래 장표가 위)
        k = k.astype(np.float32)
        t = np.clip((w.astype(np.float32) - k) / 255.0, 0, 1)
        if fade and L is not None and L.get('chars') is not None:
            # 인물 아랫단만 흐림: 인물 자리(가장자리 반투명 픽셀까지 2px 넓힘)는 그 픽셀 전체를 같은 비율로 → 윤곽선이 남지 않음
            m = (cv2.dilate((L['chars'][:H, :, 3] > 5).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0).astype(np.float32)[..., None]
            keep = 1 - m * (1 - ramp)
            k, t = k * keep, 1 - (1 - t) * keep
        a0, a1 = max(0, y0), min(canvas.shape[0], y0 + H)
        canvas[a0:a1] = k[a0 - y0:a1 - y0] + t[a0 - y0:a1 - y0] * canvas[a0:a1]
    return np.clip(canvas, 0, 255).astype(np.uint8)


def compose_natural(Ws, Ks, bg, offs):
    return compose_design(Ws, Ks, bg, offs, None, 0)


# ---------------------------------------------------------------- 페이지 구분선 (3-4 구분선 판, 13-15, 17-18 — 사용자 2026-09-28)
DIV_X = (85.5, 1194.5)          # 1280 기준. 장표 내용(카드·표)의 좌우 끝과 맞춰 양옆을 띄움
DIV_W = 1.5                     # 1280 기준 두께
DIV_RGB, DIV_A = (107, 78, 255), 0.25    # 칩 보라(#6B4EFF)를 연하게


def content_rows(w, k):
    t = np.clip((w.astype(np.float32) - k.astype(np.float32)) / 255.0, 0, 1).min(axis=2)
    rows = np.where((t < 0.9).any(axis=1))[0]
    return int(rows.min()), int(rows.max())


def hline(canvas, y, x0, x1, w, rgb, a):
    """둥근 끝의 가로선(가장자리 부드럽게)."""
    r = w / 2
    ya, yb = int(np.floor(y - r - 1)), int(np.ceil(y + r + 1)) + 1
    xa, xb = int(np.floor(x0 - r - 1)), int(np.ceil(x1 + r + 1)) + 1
    ys, xs = np.mgrid[ya:yb, xa:xb].astype(np.float32)
    dx = np.maximum(np.maximum(x0 - xs, xs - x1), 0)
    cov = np.clip(r + 0.5 - np.sqrt(dx ** 2 + (ys - y) ** 2), 0, 1)[..., None] * a
    canvas[ya:yb, xa:xb] = canvas[ya:yb, xa:xb] * (1 - cov) + np.array(rgb, np.float32) * cov


def dividers(img, Ws, Ks, offs):
    """장표 사이마다: 위 장표 내용 끝과 아래 장표 내용 처음(칩)의 한가운데에 구분선."""
    canvas = img.astype(np.float32)
    ext = [content_rows(w, k) for w, k in zip(Ws, Ks)]
    ys = []
    for i in range(len(Ws) - 1):
        y = (offs[i] + ext[i][1] + offs[i + 1] + ext[i + 1][0]) / 2
        hline(canvas, y, S * DIV_X[0], S * DIV_X[1], S * DIV_W, DIV_RGB, DIV_A)
        ys.append(y / S)
    return np.clip(np.rint(canvas), 0, 255).astype(np.uint8), ys
