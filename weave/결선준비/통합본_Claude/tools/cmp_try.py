#!/usr/bin/env python3
"""기존 기능과의 비교 장 후보(cmp_new.py)를 말하며 넘기는 영상으로 찍는다. 덱은 바꾸지 않는다.

  python tools/cmp_try.py              → 후보 가~라 모두: 비교장표_후보/후보가_….mp4 … 과 비교장표_후보.pptx(클릭으로 넘김), 한눈에.jpg
  python tools/cmp_try.py --only 가,다  → 그 후보만
  python tools/cmp_try.py --quick 가    → 낭독 없이 그 장만 빨리 찍어 봄(out/cmp_try/quick_가.mp4)
  python tools/cmp_try.py --deck       → 후보를 모은 덱과 정적 그림(out/cmp_try/png)만
  python tools/cmp_try.py --check      → 영상에 넣은 낭독을 받아쓰기로 글과 견줌

영상은 그 장 하나예요(말할 글은 지금 35쪽과 같음). 낭독과 녹화는 out/cmp_try/<후보>/에 따로 둔다.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'tools'))
import make as MK  # noqa: E402
import talk as TK  # noqa: E402
import fx_try as FT  # noqa: E402  (틀을 빌리는 frame, 한눈에 그림 sheet)
import cmp_new as CM  # noqa: E402

HW = MK.HW
WORK = MK.OUT / 'cmp_try'
DST = HERE / '비교장표_후보'
FILE = {'가': '후보가_두띠', '나': '후보나_넓이와깊이', '다': '후보다_네칸', '라': '후보라_계단'}


def use(code):
    d = WORK / code
    d.mkdir(parents=True, exist_ok=True)
    HW.OUT = TK.OUT = d
    HW._CUE_CACHE.clear()
    return d


def pick(code):
    return next(c for c in CM.CANDIDATES if c[0] == code)


def save(prs, old, dst):
    MK.drop_slides(prs, old)
    MK.samsung_fonts.remap_prs(prs)
    prs.save(str(dst))


def quick(code, hold=1500):
    _, key, fn, _ = pick(code)
    use(code)
    sp = fn()
    sp.holds = [hold] * len(sp.groups)
    prs, old, layout, note_tpl = FT.frame()
    _, _, secs = HW.add_slides(prs, layout, note_tpl, [sp], auto=True)
    auto, mp4 = WORK / ('quick_%s.pptx' % code), WORK / ('quick_%s.mp4' % code)
    save(prs, old, auto)
    print(MK.render_c.video(auto, mp4, secs))
    FT.sheet(mp4, WORK / ('quick_%s.jpg' % code))
    print('→', mp4, '%.1f초' % HW.video_len(mp4))


def record(code):
    _, key, fn, label = pick(code)
    d = use(code)
    silent, auto, meta = d / '_silent.mp4', d / '_auto.pptx', d / '_talk.json'
    says, clips = HW.narrate([fn()], None, False)
    specs = [fn()]                      # 낭독에서 잰 때로 효과를 다시 맞춤
    prs, old, layout, note_tpl = FT.frame()
    plan = []
    TK.talkify(specs, says, 0, plan)
    _, _, secs = HW.add_slides(prs, layout, note_tpl, specs, auto=True)
    for p, sec, sp in zip(plan, secs, specs):
        p['secs'], p['trans'] = sec, (sp.trans[1] / 1000 if sp.trans else 0)
    save(prs, old, auto)
    TK.seg_secs(plan, says)
    meta.write_text(json.dumps(dict(plan=plan, clips={k: [str(c) for c in v] for k, v in clips.items()}), ensure_ascii=False), encoding='utf-8')
    print('녹화 %s' % code)
    print(MK.render_c.video(auto, silent, secs))
    full = d / (FILE[code] + '_1080p.mp4')
    rows, end = TK.finish(silent, full, plan, clips)
    DST.mkdir(exist_ok=True)
    TK.shrink(full, DST / (FILE[code] + '.mp4'))
    (d / 'timing.json').write_text(json.dumps(dict(rows=rows, total=round(end, 2)), ensure_ascii=False), encoding='utf-8')
    print('   %s %.1f초' % (key, end))


def check(code):
    _, key, fn, _ = pick(code)
    d = use(code)
    m = json.loads((d / '_talk.json').read_text(encoding='utf-8'))
    return HW.narrate_check([fn()], {k: [Path(c) for c in v] for k, v in m['clips'].items()})


def deck():
    specs = []
    for code, key, fn, label in CM.CANDIDATES:
        use(code)
        specs.append(fn())
    prs, old, layout, note_tpl = FT.frame()
    _, report, _ = HW.add_slides(prs, layout, note_tpl, specs)
    DST.mkdir(exist_ok=True)
    dst = DST / '비교장표_후보.pptx'
    save(prs, old, dst)
    for key, nclick, nnote, _ in report:
        if nclick != nnote:
            print('   ! %s: 클릭 %d ≠ 노트 (클릭) %d' % (key, nclick, nnote))
    print('→', dst.name, '%.1f MB' % (dst.stat().st_size / 1e6))
    return dst


def overview():
    """후보마다 두 순간(기존 기능이 다 뜬 때, Weave가 뜬 뒤)을 녹화에서 뽑아 한 장에 → 비교장표_후보/한눈에.jpg"""
    from PIL import Image, ImageDraw, ImageFont
    cands = [c for c in CM.CANDIDATES if (WORK / c[0] / 'timing.json').exists()]
    if not cands:
        return
    font, small = ImageFont.truetype(str(TK.FONT), 26), ImageFont.truetype(str(TK.FONT), 19)
    w, h, pad, head, left = 800, 442, 14, 46, 150
    im = Image.new('RGB', (left + 2 * (w + pad) + pad, head + len(cands) * (h + pad) + pad), '#FFFFFF')
    d = ImageDraw.Draw(im)
    for j, t in enumerate(['기존 기능이 다 뜬 때', '(클릭) Weave가 뜬 뒤']):
        d.text((left + pad + j * (w + pad) + w / 2, head / 2 + 4), t, font=small, fill='#6A6474', anchor='mm')
    for i, (code, key, _, label) in enumerate(cands):
        wd = WORK / code
        plan = json.loads((wd / '_talk.json').read_text(encoding='utf-8'))['plan']
        end = json.loads((wd / 'timing.json').read_text(encoding='utf-8'))['total']
        p_ = plan[0]
        y = head + i * (h + pad)
        d.text((left / 2 + 6, y + h / 2 - 18), '후보 ' + code, font=font, fill='#1C1A24', anchor='mm')
        d.text((left / 2 + 6, y + h / 2 + 16), label, font=small, fill='#6B4EFF', anchor='mm')
        for j, t in enumerate((p_['trans'] + p_['seg_secs'][0] - 0.35, end - 0.6)):
            png = wd / ('_still%d.png' % j)
            subprocess.run([HW.FFMPEG, '-y', '-loglevel', 'error', '-ss', '%.2f' % t, '-i', str(wd / '_silent.mp4'), '-frames:v', '1',
                            '-vf', 'crop=1920:1062:0:0,scale=%d:-1' % w, str(png)], check=True)
            im.paste(Image.open(png).convert('RGB'), (left + pad + j * (w + pad), y))
            png.unlink()
    DST.mkdir(exist_ok=True)
    im.save(DST / '한눈에.jpg', quality=90)
    print('→ 한눈에.jpg', im.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only')
    ap.add_argument('--quick')
    ap.add_argument('--deck', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--sheet', action='store_true')
    a = ap.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    codes = [c[0] for c in CM.CANDIDATES if not a.only or c[0] in a.only.split(',')]
    if a.quick:
        for code in a.quick.split(','):
            quick(code)
        return
    if a.check:
        for code in codes:
            check(code)
        return
    if a.sheet:
        overview()
        return
    if not a.deck:
        for code in codes:
            record(code)
    dst = deck()
    print(MK.render_c.png(dst, WORK / 'png', 1600, 900))
    if not a.deck:
        overview()


if __name__ == '__main__':
    main()
