#!/usr/bin/env python3
"""기대효과 한 장(fx_new.py)을 앞뒤 장과 함께 말하며 넘기는 영상으로 찍는다. 덱은 바꾸지 않는다.

  python tools/fx_try.py              → 지금 장(fx_new.CURRENT = M, 11-13에 후보 L을 손본 판): 기대효과_후보/확정_L을손본판.mp4와 기대효과_후보.pptx(클릭으로 넘김), 한눈에.jpg
  python tools/fx_try.py --only D,E   → 그 후보만(앞선 차수 A~L은 기대효과_후보/이전판에 나옴)
  python tools/fx_try.py --quick J    → 낭독 없이 그 장만 빨리 찍어 봄(out/fx_try/quick_J.mp4와 한눈에 보는 그림. 구간마다 잠깐 머묾)
  python tools/fx_try.py --deck       → 지금 장을 담은 덱만
  python tools/fx_try.py --remux      → 녹화는 두고 낭독과 자막만 다시 얹음
  python tools/fx_try.py --check      → 영상에 넣은 낭독을 받아쓰기로 글과 견줌
  python tools/fx_try.py --sheet      → 찍어 둔 영상에서 후보마다 세 순간을 뽑아 한 장에(기대효과_후보/한눈에.jpg)

영상 = 31쪽(결과 제공) → 그 장 → 33쪽(7차부터 기존 기능과의 비교, 6차까지는 비즈니스 임팩트). 낭독은 이 컴퓨터 안에서만 만든다(talk.py와 같은 목소리).
낭독과 녹화는 out/fx_try/<후보>/에 따로 둔다(본 발표의 낭독 out/tts는 건드리지 않음).
"""
import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import make as MK  # noqa: E402
import talk as TK  # noqa: E402
import fx_new as FX  # noqa: E402
from pptx import Presentation  # noqa: E402

HW, N = MK.HW, MK.N
WORK = MK.OUT / 'fx_try'
DST = HERE / '기대효과_후보'
FILE = {'A': '후보A_실세가닥', 'B': '후보B_세물음', 'C': '후보C_물결', 'D': '후보D_고리얼굴', 'E': '후보E_고리속얼굴', 'F': '후보F_뱃지',
        'G': '후보G_줄어드는숫자', 'H': '후보H_몸통있는사람', 'J': '후보J_숫자가기능이름으로', 'K': '후보K_숫자가물러남', 'L': '후보L_숫자가0으로',
        'M': '확정_L을손본판'}
OLD = DST / '이전판'                # 앞선 차수(A~L)의 영상과 그림. 저장소에는 올리지 않음
SHEETS = [('한눈에.jpg', FX.CURRENT), ('이전판/한눈에_1차.jpg', 'ABC'), ('이전판/한눈에_2차.jpg', 'DEFGH'), ('이전판/한눈에_3차.jpg', 'JKL')]
HEAD = {'M': '32쪽'}               # 한눈에 그림의 줄 이름(없으면 '후보 X')


def out_dir(code):
    d = DST if code in FX.CURRENT else OLD
    d.mkdir(parents=True, exist_ok=True)
    return d


def frame():
    prs = Presentation(str(MK.BASE))
    old = list(prs.slides)
    layout = old[5].slide_layout
    note_tpl = [copy.deepcopy(sh._element) for sh in old[5].notes_slide.placeholders]
    return prs, old, layout, note_tpl


def use(code):
    """이 후보의 낭독 폴더를 쓴다(말에 맞춘 효과의 때도 여기서 읽음)."""
    d = WORK / code
    d.mkdir(parents=True, exist_ok=True)
    HW.OUT = TK.OUT = d
    HW._CUE_CACHE.clear()
    return d


def trio(fn):
    d = HW.s_deliver()
    d.trans = ('fade', 320)             # 영상의 첫 장: 앞 장이 없으므로 모핑 대신 가볍게
    return [d, fn(), N.s_cmp_main()]


def sheet(mp4, dst, fps=4, cols=6, w=480):
    n = int(HW.video_len(mp4) * fps) + 1
    rows = (n + cols - 1) // cols
    subprocess.run([HW.FFMPEG, '-y', '-loglevel', 'error', '-i', str(mp4), '-vf',
                    'fps=%d,scale=%d:-1,tile=%dx%d' % (fps, w, cols, rows), '-frames:v', '1', '-q:v', '3', str(dst)], check=True)


def quick(code, hold=1300):
    _, key, fn, _ = next(c for c in FX.CANDIDATES if c[0] == code)
    use(code)
    sp = fn()
    sp.holds = [hold] * len(sp.groups)
    prs, old, layout, note_tpl = frame()
    _, _, secs = HW.add_slides(prs, layout, note_tpl, [sp], auto=True)
    MK.drop_slides(prs, old)
    MK.samsung_fonts.remap_prs(prs)
    auto, mp4 = WORK / ('quick_%s.pptx' % code), WORK / ('quick_%s.mp4' % code)
    prs.save(str(auto))
    print(MK.render_c.video(auto, mp4, secs))
    sheet(mp4, WORK / ('quick_%s.jpg' % code))
    print('→', mp4, '%.1f초' % HW.video_len(mp4))


def record(code, remux=False):
    _, key, fn, label = next(c for c in FX.CANDIDATES if c[0] == code)
    d = use(code)
    silent, auto, meta = d / '_silent.mp4', d / '_auto.pptx', d / '_talk.json'
    if remux and silent.exists() and meta.exists():
        m = json.loads(meta.read_text(encoding='utf-8'))
        plan, clips = m['plan'], {k: [Path(c) for c in v] for k, v in m['clips'].items()}
    else:
        says, clips = HW.narrate(trio(fn), None, False)
        specs = trio(fn)                # 낭독에서 잰 때로 효과를 다시 맞춤
        prs, old, layout, note_tpl = frame()
        plan = []
        TK.talkify(specs, says, 0, plan)
        _, _, secs = HW.add_slides(prs, layout, note_tpl, specs, auto=True)
        for p, sec, sp in zip(plan, secs, specs):
            p['secs'], p['trans'] = sec, (sp.trans[1] / 1000 if sp.trans else 0)
        MK.drop_slides(prs, old)
        MK.samsung_fonts.remap_prs(prs)
        prs.save(str(auto))
        TK.seg_secs(plan, says)
        meta.write_text(json.dumps(dict(plan=plan, clips={k: [str(c) for c in v] for k, v in clips.items()}), ensure_ascii=False), encoding='utf-8')
        print('녹화 %s: %d장' % (code, len(secs)))
        print(MK.render_c.video(auto, silent, secs))
    full = d / (FILE[code] + '_1080p.mp4')
    rows, end = TK.finish(silent, full, plan, clips)
    TK.shrink(full, out_dir(code) / (FILE[code] + '.mp4'))
    (d / 'timing.json').write_text(json.dumps(dict(rows=rows, total=round(end, 2)), ensure_ascii=False), encoding='utf-8')
    for k, a, n in rows:
        print('   %-8s %5.1f초부터 %5.1f초' % (k, a, n))
    return rows, end


def check(code):
    """영상에 넣은 낭독을 받아쓰기로 글과 견준다(out/fx_try/<후보>/tts_check.txt)."""
    _, key, fn, _ = next(c for c in FX.CANDIDATES if c[0] == code)
    d = use(code)
    m = json.loads((d / '_talk.json').read_text(encoding='utf-8'))
    clips = {k: [Path(c) for c in v] for k, v in m['clips'].items()}
    return HW.narrate_check(trio(fn), clips)


def deck():
    """지금 장(fx_new.CURRENT)을 담은 덱(클릭으로 넘김, 노트에 대본). 효과의 때는 자기 낭독에서 잰 값."""
    specs = []
    for code, key, fn, label in FX.CANDIDATES:
        if code not in FX.CURRENT:
            continue
        use(code)
        specs.append(fn())
    prs, old, layout, note_tpl = frame()
    _, report, _ = HW.add_slides(prs, layout, note_tpl, specs)
    MK.drop_slides(prs, old)
    MK.samsung_fonts.remap_prs(prs)
    DST.mkdir(exist_ok=True)
    dst = DST / '기대효과_후보.pptx'
    prs.save(str(dst))
    for key, nclick, nnote, _ in report:
        if nclick != nnote:
            print('   ! %s: 클릭 %d ≠ 노트 (클릭) %d' % (key, nclick, nnote))
    print('→', dst.name, '%.1f MB' % (dst.stat().st_size / 1e6))
    return dst


def overview():
    """후보마다 세 순간(첫 설문, 세 설문이 다 뜬 때, 풀린 뒤)을 영상에서 뽑아 한 장에 모은다 → 기대효과_후보/한눈에.jpg, 한눈에_2차.jpg"""
    for name, codes in SHEETS:
        if all((WORK / c / 'timing.json').exists() for c in codes):
            sheet_of(name, [c for c in FX.CANDIDATES if c[0] in codes])


def sheet_of(name, cands):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(str(TK.FONT), 26)
    small = ImageFont.truetype(str(TK.FONT), 19)
    w, h, pad, head, left = 640, 360, 14, 46, 210
    cols = ['첫 불편이 가운데에', '불편 셋이 다 뜬 때', 'Weave로 풀린 뒤']
    im = Image.new('RGB', (left + 3 * (w + pad) + pad, head + len(cands) * (h + pad) + pad), '#FFFFFF')
    d = ImageDraw.Draw(im)
    for j, t in enumerate(cols):
        d.text((left + pad + j * (w + pad) + w / 2, head / 2 + 4), t, font=small, fill='#6A6474', anchor='mm')
    for i, (code, key, _, label) in enumerate(cands):
        wd = WORK / code
        plan = json.loads((wd / '_talk.json').read_text(encoding='utf-8'))['plan']
        rows = json.loads((wd / 'timing.json').read_text(encoding='utf-8'))['rows']
        p_ = next(x for x in plan if x['key'] == key)
        _, a, n = next(r for r in rows if r[0] == key)
        ss, t0 = p_['seg_secs'], a + p_['trans']
        y = head + i * (h + pad)
        d.text((left / 2 + 6, y + h / 2 - 18), HEAD.get(code, '후보 ' + code), font=font, fill='#1C1A24', anchor='mm')
        d.text((left / 2 + 6, y + h / 2 + 16), label, font=small, fill='#6B4EFF', anchor='mm')
        for j, t in enumerate((t0 + ss[0] - 0.35, t0 + sum(ss[:3]) - 0.35, a + n - 0.45)):
            png = wd / ('_still%d.png' % j)
            subprocess.run([HW.FFMPEG, '-y', '-loglevel', 'error', '-ss', '%.2f' % t, '-i', str(wd / '_silent.mp4'), '-frames:v', '1',
                            '-vf', 'crop=1920:1062:0:0,scale=%d:-1' % w, str(png)], check=True)      # 자막을 얹기 전의 녹화에서(왼쪽 아래 구간 표만 잘라 냄)
            fr = Image.open(png).convert('RGB')
            im.paste(fr, (left + pad + j * (w + pad), y + (h - fr.height) // 2))
            png.unlink()
    (DST / name).parent.mkdir(parents=True, exist_ok=True)
    im.save(DST / name, quality=90)
    print('→', name, im.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only')
    ap.add_argument('--quick')
    ap.add_argument('--deck', action='store_true')
    ap.add_argument('--png', action='store_true')
    ap.add_argument('--remux', action='store_true')
    ap.add_argument('--sheet', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    if a.quick:
        for code in a.quick.split(','):
            quick(code)
        return
    if a.sheet:
        overview()
        return
    if a.check:
        for code, _, _, _ in FX.CANDIDATES:
            if code in (a.only.split(',') if a.only else FX.CURRENT):
                check(code)
        return
    if not a.deck:
        for code, _, _, _ in FX.CANDIDATES:
            if code in (a.only.split(',') if a.only else FX.CURRENT):
                record(code, a.remux)
    dst = deck()
    if a.png or a.deck:
        print(MK.render_c.png(dst, WORK / 'png', 1600, 900))
    if not a.deck:
        overview()


if __name__ == '__main__':
    main()
