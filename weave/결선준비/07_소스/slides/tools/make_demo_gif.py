"""APP DEMO GIF (2026-09-28 요청): 9쪽(HOW IT WORKS) 이미지 바로 아래에 붙일 데모 장면.

- 사용자가 넣어 둔 weave_png/Demo1~3.gif(앱 녹화, 폰 틀 포함, 600px·20fps·약 34~35초)를 예전 App Demo 장표처럼 세 대 나란히
- 칩 'APP DEMO', 제목 없음, 폰 아래 캡션 'UX1: 기록 통합 검색' / 'UX2: 단서로 찾는 기억' / 'UX3: 먼저 건네는 기억'
  (5쪽 핵심 UX 이름, 검정 글씨 #1C1A24 — 사용자 요청)
- 세 데모는 맞춰 재생하지 않고 각자 반복: 시작을 1/3씩 어긋나게 하고, 짧은 데모는 끝 화면에서 잠깐 멈췄다 다시 시작
  (가장 긴 데모 길이 한 바퀴 안에서 모두 이음매 없이 반복)
- 녹화 속 폰 바깥(연회색 배경·잘린 그림자)은 예전 App Demo 그림(claude_0927/assets/app-demo/, 같은 폰 틀·바깥 투명)의
  윤곽으로 잘라 내고, 그림자는 새로 그림
- 배경: 5-9쪽 이미지 맨 아래 색(#F4F0FF)과 9쪽 왼쪽 아래 보라 빛을 이어받음 → 바로 밑에 붙이면 이어져 보임
- 1280 기준 배치, 1.5배(1920px)로 출력 → 폰이 원래 녹화와 거의 같은 해상도(폭 522px)
- GIF 인코딩: gifski

출력: added_0926/0927_data/weave_png/p09_app-demo.gif (20fps), p09_app-demo_10fps.gif (--fps 10, 가벼운 판)
      p09_app-demo_10mb.gif (--upload: 올리는 곳 한 파일 10MB 제한판, 2026-09-29. weave_png/final_0928/p09_app-demo.gif가 이것)
      첫 장면 미리보기 /tmp/claude-weave-0927/demo-gif/preview.png
사용: python make_demo_gif.py [--fps 20|10] [--quality 90] | --upload | --frames-only [--fps 20]
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageSequence

import header as hd
import seams

ROOT = Path(__file__).resolve().parents[1]                     # deck-0927v1
WP = ROOT.parents[1] / '04_동영상·데모'                  # 결선준비/04_동영상·데모 (입력 Demo1~3.gif, 출력 GIF)
SRC = [WP / '녹화_통화.gif', WP / '녹화_검색.gif', WP / '녹화_카톡.gif']   # 예전 Demo1~3.gif
CAPS = [('UX1', '기록 통합 검색'), ('UX2', '단서로 찾는 기억'), ('UX3', '먼저 건네는 기억')]
OUT = WP / 'p09_app-demo.gif'
DEMO = ROOT / 'demo'
WORK = Path('/tmp/claude-weave-0927/demo-gif')
GIFSKI = '/tmp/claude-weave-0927/gifski/linux/gifski'
OLD = ROOT.parent / 'assets' / 'app-demo' / 'app-demo-1-call.png'   # 같은 폰 틀, 바깥 투명(550×1099)
FONTS = '../../assets/fonts'                               # demo/ 기준

K = 1.5                                  # 출력 배율 (1280 기준 → 1920px)
PW1, GAP1 = 348, 60                      # 폰 폭·사이 간격 (1280 기준)
CHIP_Y, PHONE_Y, CAP_GAP, CAP_H, BOTTOM = 28, 84, 20, 28, 34   # 캡션은 폰 아래(사용자 요청)
BG_TOP = (244, 240, 255)                 # 5-9 이미지 맨 아래 색
GLOWS = [(72, -30, 'L', 1.0, 0.95),      # 9쪽 왼쪽 아래 보라 빛(9쪽 y=690)을 이어받음
         (1190, None, 'P', 1.0, 0.75)]   # 오른쪽 아래 노랑 (y는 캔버스 아래에서 60px 위)


def phone_box(frame):
    """녹화 속 폰 틀의 바깥 경계: 가장자리에서 안쪽으로 가며 '처음' 급하게 어두워지는 곳(폰 틀 테두리).
    틀 안쪽에도 선이 여러 개라 가장 큰 변화가 아니라 바깥에서 처음 만나는 변화를 씀. 여러 띠의 가운데값."""
    a = np.asarray(frame.convert('RGB'), np.float32).mean(axis=2)
    h, w = a.shape

    def first_drop(band):                                         # band: (줄 수, 길이) — 바깥→안쪽 방향
        line = band.mean(axis=0)                                  # GIF 디더링 잡음을 줄이려고 11줄 평균
        d = line[:-2] - line[2:]
        idx = np.where(d[1:80] > 12)[0]
        return int(idx[0]) + 2 if len(idx) else None

    ys = range(int(h * .3), int(h * .7), 11)
    xs = range(int(w * .3), int(w * .7), 11)
    x0 = np.median([first_drop(a[y:y + 11]) for y in ys])
    x1 = w - 1 - np.median([first_drop(a[y:y + 11, ::-1]) for y in ys])
    y0 = np.median([first_drop(a[:, x:x + 11].T) for x in xs])
    y1 = h - 1 - np.median([first_drop(a[::-1, x:x + 11].T) for x in xs])
    return float(x0), float(y0), float(x1), float(y1)


def background(W, H):
    bg = np.empty((H, W, 3), np.float32)
    bg[:] = BG_TOP
    for x, y, kind, scale, amul in GLOWS:
        g = seams.KINDS[kind]
        y = (H / K - 60) if y is None else y
        stops = [(st, col, a * amul) for st, col, a in g['stops']]
        seams.blob(bg, K * x, K * y, K * g['r'][0] * scale, K * g['r'][1] * scale, stops)
    return bg


def static_layer(W1, H1, rects, radius1, cap_y):
    """칩·캡션·폰 그림자(투명 바탕) — 장표와 같은 글꼴로 Chromium에서 그림."""
    DEMO.mkdir(exist_ok=True)
    chip_w = round(hd.chip_width('APP DEMO'))
    caps = ''.join(
        f'<div class="cap" style="left:{x:.2f}px;top:{cap_y:.2f}px;width:{w:.2f}px">{ux}: {name}</div>'
        f'<div class="shadow" style="left:{x:.2f}px;top:{y:.2f}px;width:{w:.2f}px;height:{h:.2f}px;border-radius:{radius1:.2f}px"></div>'
        for (ux, name), (x, y, w, h) in zip(CAPS, rects))
    html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'Noto Sans KR'; font-weight: 700; src: url('{FONTS}/NotoSansKR-700.ttf'); }}
@font-face {{ font-family: 'Inter'; font-weight: 600; src: url('{FONTS}/Inter-600.ttf'); }}
@font-face {{ font-family: 'Inter'; font-weight: 700; src: url('{FONTS}/Inter-700.ttf'); }}
html, body {{ margin: 0; background: transparent; }}
#slide {{ position: relative; width: {W1}px; height: {H1}px; overflow: hidden; font-family: 'Inter', 'Noto Sans KR', sans-serif; }}
/* 칩: header.py와 같은 규격 — #6B4EFF, 높이 26, y=28, Inter SemiBold 11pt(14.67px) 자간 +0.5pt, 폭은 header.chip_width()로(장표 칩과 같은 폭),
   글자는 가운데. 줄 높이는 font 묶음 속성 안에 26px로 넣음(따로 쓰면 font 묶음이 줄 높이를 초기화해 글자가 위로 붙음 — 사용자 지적) */
.chip {{ position: absolute; top: {CHIP_Y}px; left: {640 - chip_w / 2}px; width: {chip_w}px; height: 26px; box-sizing: border-box; padding-left: 0.667px;
         text-align: center; border-radius: 13px; background: #6B4EFF; color: #fff; font: 600 14.667px/26px 'Inter'; letter-spacing: 0.667px; white-space: nowrap; }}
.cap {{ position: absolute; height: {CAP_H}px; line-height: {CAP_H}px; text-align: center; font-size: 20px; font-weight: 700; color: #1C1A24; letter-spacing: -0.2px; }}
.shadow {{ position: absolute; background: transparent;
           box-shadow: 0 16px 34px rgba(62, 40, 140, .16), 0 4px 10px rgba(62, 40, 140, .10); }}
</style></head><body><div id="slide"><div class="chip">APP DEMO</div>{caps}</div>
<script>document.fonts.ready.then(() => {{ window.pageReady = true; }});</script></body></html>'''
    (DEMO / 'app-demo.html').write_text(html, encoding='utf-8')
    js = f'''
const {{ chromium }} = require('/tmp/claude-weave-0927/node_modules/playwright-core');
(async () => {{
  const b = await chromium.launch({{ executablePath: '/home/jaeung/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome', headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--force-color-profile=srgb', '--font-render-hinting=none'] }});
  const p = await b.newPage({{ viewport: {{ width: {W1}, height: {H1} }}, deviceScaleFactor: {K} }});
  await p.goto('file://{DEMO / 'app-demo.html'}');
  await p.waitForFunction(() => window.pageReady === true);
  await p.screenshot({{ path: '{WORK / 'static.png'}', omitBackground: true, clip: {{ x: 0, y: 0, width: {W1}, height: {H1} }} }});
  await b.close();
}})().catch(e => {{ console.error(e); process.exit(1); }});'''
    env = {**os.environ, 'LD_LIBRARY_PATH': '/tmp/claude-weave-0927/chrome-sysroot/usr/lib/x86_64-linux-gnu'}
    subprocess.run(['node', '-e', js], env=env, check=True)
    return np.asarray(Image.open(WORK / 'static.png').convert('RGBA'), np.float32)


def build_frames(fps):
    """폰 경계를 재고 바탕·칩·캡션을 그린 뒤, 장면 프레임을 WORK/out/에 PNG로 저장. (W, H, T) 반환."""
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    step = 20 // fps                                          # 원본 20fps에서 몇 장마다 한 장
    old_alpha = Image.open(OLD).getchannel('A')

    # 1) 폰 틀 경계·크기
    PW = round(PW1 * K)
    boxes, heights = [], []
    for f in SRC:
        im = Image.open(f)
        x0, y0, x1, y1 = phone_box(im)
        boxes.append((x0, y0, x1, y1))
        heights.append(round(PW * (y1 - y0) / (x1 - x0)))
        print(f.name, im.size, 'frames', im.n_frames, 'phone box', (x0, y0, x1, y1), '→', PW, 'x', heights[-1])
    PH = max(heights)
    W1 = 1280
    cap_y = PHONE_Y + PH / K + CAP_GAP
    H1 = int(np.ceil(cap_y + CAP_H + BOTTOM))
    W, H = round(W1 * K), round(H1 * K)
    left1 = (W1 - 3 * PW1 - 2 * GAP1) / 2
    rects1 = [(left1 + i * (PW1 + GAP1), PHONE_Y, PW1, heights[i] / K) for i in range(3)]
    radius1 = PW1 * 64 / 550                                  # 예전 그림의 모서리 반경(550px 폭에서 64px)

    # 2) 바탕 + 칩·캡션·그림자
    base = background(W, H)
    st = static_layer(W1, H1, rects1, radius1, cap_y)
    al = st[..., 3:4] / 255.0
    base = base * (1 - al) + st[..., :3] * al
    base_u8 = np.clip(np.rint(base), 0, 255).astype(np.uint8)

    # 3) 데모마다 프레임을 잘라·줄여 저장 (폰 바깥은 예전 그림 윤곽으로 잘라 냄)
    masks, counts = [], []
    for i, f in enumerate(SRC):
        d = WORK / f'd{i}'
        d.mkdir()
        x0, y0, x1, y1 = boxes[i]
        size = (PW, heights[i])
        m = old_alpha.resize(size, Image.LANCZOS)
        masks.append(np.asarray(m, np.float32)[..., None] / 255.0)
        n = 0
        for k, fr in enumerate(ImageSequence.Iterator(Image.open(f))):
            if k % step:
                continue
            # 경계로 잡은 픽셀의 가운데부터 자름(측정이 바깥쪽으로 반~1px 치우침)
            fr.convert('RGB').resize(size, Image.LANCZOS, box=(x0 + .5, y0 + .5, x1 + .5, y1 + .5)).save(d / f'{n:04d}.png', compress_level=1)
            n += 1
        counts.append(n)
    T = max(counts)
    offs = [round(i * T / 3) for i in range(3)]
    print('frames per demo', counts, '| loop', T, 'frames at', fps, 'fps =', T / fps, 's | offsets', offs)

    # 4) 장면 합성
    od = WORK / 'out'
    od.mkdir()
    cache = [(-1, None)] * 3
    X = [round(r[0] * K) for r in rects1]
    Y = round(PHONE_Y * K)
    for t in range(T):
        out = base_u8.copy()
        for i in range(3):
            k = min((t + offs[i]) % T, counts[i] - 1)            # 짧은 데모는 끝 화면에서 멈춰 기다림
            if cache[i][0] != k:
                cache[i] = (k, np.asarray(Image.open(WORK / f'd{i}' / f'{k:04d}.png'), np.float32))
            ph, m = cache[i][1], masks[i]
            h, w = ph.shape[:2]
            reg = out[Y:Y + h, X[i]:X[i] + w].astype(np.float32)
            out[Y:Y + h, X[i]:X[i] + w] = np.clip(np.rint(reg * (1 - m) + ph * m), 0, 255).astype(np.uint8)
        Image.fromarray(out).save(od / f'{t:04d}.png', compress_level=1)
        if t == 0:
            Image.fromarray(out).save(WORK / 'preview.png')
    json.dump(dict(W=W, H=H, T=T, fps=fps, offsets=offs, boxes=boxes, rects1=rects1), open(WORK / 'layout.json', 'w'), indent=1)
    return W, H, T


def encode(out_gif, fps, width, quality=90, motion=None, lossy=None):
    """WORK/out/ 프레임을 모두 gifski로 GIF에 담음(프레임을 버리지 않음). 파일 크기(바이트) 반환."""
    frames = sorted(str(p) for p in (WORK / 'out').glob('*.png'))
    args = [GIFSKI, '--fps', str(fps), '--quality', str(quality), '--width', str(width)]
    if motion:
        args += ['--motion-quality', str(motion)]
    if lossy:
        args += ['--lossy-quality', str(lossy)]
    subprocess.run([*args, '-o', str(out_gif), *frames], check=True, capture_output=True)
    return out_gif.stat().st_size


def main(fps=20, quality=90):
    out_gif = OUT if fps == 20 else OUT.with_name(f'{OUT.stem}_{fps}fps.gif')
    W, H, T = build_frames(fps)
    encode(out_gif, fps, W, quality)
    print('saved', out_gif, round(out_gif.stat().st_size / 1e6, 2), 'MB', W, 'x', H)


# 올리는 곳 한 파일 10MB 제한판 (2026-09-29, 사용자: 화질은 조금 잃어도 되지만 프레임은 빠지면 안 됨)
# 700프레임·20fps 그대로. gifski 설정을 여러 개 비교해 고름(README 12차):
#  - 1920px에서 10MB에 맞추려면 motion 67 안팎이 필요한데, 화면이 바뀔 때 이전 화면 글자가 흐릿하게 남음(잔상)
#  - motion 100(잔상 없음)은 1440px까지 줄여야 10MB → 글자가 흐려짐
#  - motion 85는 잔상이 눈에 띄지 않고, 폭 1800px(6% 축소)에서 10MB 아래
UPLOAD = dict(width=1800, quality=50, motion=85, lossy=75)


def upload():
    lay = WORK / 'layout.json'
    if not lay.exists() or json.load(open(lay))['fps'] != 20:
        build_frames(20)
    out = OUT.with_name(f'{OUT.stem}_10mb.gif')
    size = encode(out, 20, **UPLOAD)
    assert size < 10_000_000, size                            # 10MB를 1000·1024 어느 쪽으로 세도 아래
    print('saved', out, size, 'bytes', UPLOAD)


if __name__ == '__main__':
    a = sys.argv
    if '--upload' in a:
        upload()
    elif '--frames-only' in a:
        print('frames', build_frames(int(a[a.index('--fps') + 1]) if '--fps' in a else 20))
    else:
        main(fps=int(a[a.index('--fps') + 1]) if '--fps' in a else 20,
             quality=int(a[a.index('--quality') + 1]) if '--quality' in a else 90)
