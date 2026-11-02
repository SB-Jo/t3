#!/usr/bin/env python3
"""HOW IT WORKS 모핑 장면 버전 만들기.

  python build2.py v1            out/V1_국숫집.pptx
  python build2.py v1 v2 v3      세 버전 모두
  python build2.py v1 --png      + PowerPoint로 장별 PNG(out/V1_png/)와 한눈에 보기
  python build2.py v1 --video    + 미리보기 영상(장마다 3.2초)

장마다 다음 장으로 '모핑' 전환(1.3초)이 걸려 있어 카메라가 확대·이동하듯 이어지고, 장 안의 실·형광펜·토큰은
전환이 끝나면 저절로 나타난다(발표자는 다음 장으로 넘기기만 하면 됨).
"""
import argparse
import importlib
import itertools
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation

import hiw_lib as L
import scenario
import story as S
from hiw_lib import q

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DECK = ROOT / '02_PPT' / 'Weave_결선.pptx'
OUT = HERE / 'out'
NAMES = {'v1': 'V1_국숫집', 'v2': 'V2_기사님번호', 'v3': 'V3_보고서마감'}


def bg_prims():
    return [S.R('bg/base', 0, 0, 1280, 720, fill=None,
                grad=dict(stops=[(0, 'FDFCFF', None), (50, 'F8F5FF', None), (100, 'F2EDFF', None)], ang=70))]


def mask_prims():
    """세계 위에 덮는 위·아래 가림막(머리 글자와 아래 띠 뒤로 기록이 비치지 않게) + 빛 번짐."""
    return [S.R('mask/top', 0, 0, 1280, 172, fill=None,
                grad=dict(stops=[(0, 'FCFBFF', 100), (80, 'FAF8FF', 98), (100, 'FAF8FF', 0)], ang=90)),
            S.R('mask/bot', 0, 600, 1280, 120, fill=None,
                grad=dict(stops=[(0, 'F5F1FF', 0), (45, 'F4F0FF', 92), (100, 'F3EFFF', 100)], ang=90)),
            S.R('bg/glow1', 640, 0, 640, 507, fill=None,
                grad=dict(stops=[(0, 'C6B3FF', 30), (30, 'DED3FF', 14), (60, 'F8F5FF', 0)], path='circle', rect=(85, 8, 15, 92))),
            S.R('bg/glow2', 0, 373, 600, 347, fill=None,
                grad=dict(stops=[(0, 'BAA6FF', 34), (40, 'DCD0FF', 16), (72, 'F8F5FF', 0)], path='circle', rect=(12, 88, 88, 12)))]


def render(sc, dst):
    prs = Presentation(str(DECK))
    layout = prs.slides[8].slide_layout
    # 덱의 노트 마스터엔 칸이 없어 새 장 노트가 비므로, 기존 9쪽 노트의 칸(그림·본문·번호)을 본떠 넣음
    import copy as _copy
    note_tpl = [_copy.deepcopy(sh._element) for sh in prs.slides[8].notes_slide.placeholders]
    lst = prs.slides._sldIdLst
    for s in list(lst):
        prs.part.drop_rel(s.get(q('r:id')))
        lst.remove(s)
    st = sc.st
    for i, step in enumerate(st.steps):
        slide = prs.slides.add_slide(layout)
        for ph in list(slide.placeholders):
            ph._element.getparent().remove(ph._element)
        pa = S.Painter(slide)
        spids = {}
        for p in bg_prims():
            pa.prim(p)
        for key in step.show:
            fn = st.items[key]
            prims = fn(step.styles.get(key))
            alpha = 100 if (step.focus is None or key in step.focus) else S.DIM
            ids = []
            for p in prims:
                e = pa.prim(p, cam=step.cam, alpha=alpha)
                ids.append(int(e.find('.//' + q('p:cNvPr')).get('id')))
            spids[key] = ids
        for p in mask_prims():
            pa.prim(p)
        for p in scenario.header_prims(step.title, step.sub):
            pa.prim(p)
        if step.hud is not None:
            for p in scenario.hud_prims(step.hud):
                pa.prim(p)
        if i > 0:
            S.morph_transition(slide, step.morph_ms)
        if step.anim:
            tl = L.Timeline()
            tl.step()
            for key, a in step.anim.items():
                if key not in spids:
                    continue
                a = dict(a)
                kind, delay, dur = a.pop('kind'), a.pop('delay', 0), a.pop('dur', 400)
                for sp in spids[key]:
                    tl.add(kind, sp, delay=delay, dur=dur, **a)
            if tl.steps[0]:
                sp_set = {int(e.get('id')) for e in slide._element.iter(q('p:cNvPr'))}
                timing = tl.xml(sp_set & {int(x) for v in spids.values() for x in v if True}, auto=(0, [0]))
                # 도형(p:sp)만 bldP 대상: 그림·곡선 섞여도 무방
                slide._element.append(timing)
        ns = slide.notes_slide
        if ns.notes_text_frame is None:
            for e in note_tpl:
                ns.shapes._spTree.append(_copy.deepcopy(e))
        ns.notes_text_frame.text = step.notes
    prs.save(str(dst))
    return len(st.steps)


def sheet(pngs, dst, cols=4, w=560, labels=None):
    ims = [Image.open(p).convert('RGB') for p in pngs]
    h = int(w * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new('RGB', (cols * (w + 10) + 10, rows * (h + 30) + 10), 'white')
    d = ImageDraw.Draw(out)
    fnt = ImageFont.truetype(str(ROOT / '06_에셋' / '글꼴' / 'NotoSansKR-700.ttf'), 16)
    for i, im in enumerate(ims):
        x, y = 10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 30)
        out.paste(im.resize((w, h), Image.LANCZOS), (x, y + 22))
        d.text((x, y), (labels[i] if labels else '%d' % (i + 1)), fill=(60, 50, 90), font=fnt)
    out.save(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('versions', nargs='+')
    ap.add_argument('--png', action='store_true')
    ap.add_argument('--video', action='store_true')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    import render2
    for v in a.versions:
        mod = importlib.import_module(v)
        sc = scenario.build(mod.SPEC)
        dst = OUT / (NAMES[v] + '.pptx')
        n = render(sc, dst)
        print(v, '장', n, '→', dst.name)
        if a.png:
            od = OUT / (NAMES[v] + '_png')
            render2.png(dst, od)
            pngs = sorted(od.glob('s*.png'))
            sheet(pngs, OUT / (NAMES[v] + '_한눈에.png'),
                  labels=['%d  %s' % (i + 1, ''.join(t for t, _ in st.title)) for i, st in enumerate(sc.st.steps)])
        if a.video:
            render2.video(dst, OUT / (NAMES[v] + '_미리보기.mp4'), 3.2)


if __name__ == '__main__':
    main()
