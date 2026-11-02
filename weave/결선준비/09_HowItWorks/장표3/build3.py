#!/usr/bin/env python3
"""HOW IT WORKS v3 — 모핑 장면, 시나리오 8가지.

  python build3.py a1 a2 ...        out/<이름>.pptx
  python build3.py all --png        모두 + PowerPoint 장별 PNG·한눈에 보기
  python build3.py a1 --video       + 미리보기 영상(장마다 3.2초)
"""
import argparse
import copy
import importlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation

import hiw_lib as L
import scene3
import story as S
from hiw_lib import q

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DECK = ROOT / '02_PPT' / 'Weave_결선.pptx'
OUT = HERE / 'out'
ALL = ['a1', 'a2', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3']


def bg_prims():
    return [S.R('bg/base', 0, 0, 1280, 720, fill=None,
                grad=dict(stops=[(0, 'FDFCFF', None), (50, 'F8F5FF', None), (100, 'F2EDFF', None)], ang=70))]


def over_prims():
    return [S.R('mask/top', 0, 0, 1280, 80, fill=None,
                grad=dict(stops=[(0, 'FCFBFF', 100), (70, 'FBFAFF', 96), (100, 'FBFAFF', 0)], ang=90)),
            S.R('bg/glow1', 640, 0, 640, 507, fill=None,
                grad=dict(stops=[(0, 'C6B3FF', 26), (30, 'DED3FF', 12), (60, 'F8F5FF', 0)], path='circle', rect=(85, 8, 15, 92))),
            S.R('bg/glow2', 0, 373, 600, 347, fill=None,
                grad=dict(stops=[(0, 'BAA6FF', 30), (40, 'DCD0FF', 14), (72, 'F8F5FF', 0)], path='circle', rect=(12, 88, 88, 12)))]


def render(sc, dst, name):
    prs = Presentation(str(DECK))
    layout = prs.slides[8].slide_layout
    note_tpl = [copy.deepcopy(sh._element) for sh in prs.slides[8].notes_slide.placeholders]
    lst = prs.slides._sldIdLst
    for s in list(lst):
        prs.part.drop_rel(s.get(q('r:id')))
        lst.remove(s)
    for i, step in enumerate(sc.steps):
        slide = prs.slides.add_slide(layout)
        for ph in list(slide.placeholders):
            ph._element.getparent().remove(ph._element)
        pa = S.Painter(slide)
        spids = {}
        for p in bg_prims():
            pa.prim(p)
        cx, cy, z, vx, vy = step.cam
        _, (crx0, cry0, crx1, cry1) = scene3.cap_region(step.cap.get('side', 'top'))
        side = step.cap.get('side', 'top')
        skipped = set()
        groups = getattr(sc, 'groups', {})
        child_of = {c: p for p, cs in groups.items() for c in cs}
        for key in step.show:
            if child_of.get(key) in skipped:      # 묶음의 바탕(질문 판)이 빠졌으면 안의 것도 뺌
                continue
            prims = sc.items[key](step.styles.get(key))
            alpha = 100 if (step.focus is None or key in step.focus) else (55 if key in step.half else S.DIM)
            if alpha == S.DIM:  # 흐린 것이 화면 끝(위 띠 포함)에 잘려 걸치면 아예 빼서 지저분한 조각을 없앰
                bx, by, bw, bh = sc.box[key]
                X0, Y0 = (bx - cx) * z + vx, (by - cy) * z + vy
                if X0 < -2 or Y0 < 78 or X0 + bw * z > 1282 or Y0 + bh * z > 722:
                    skipped.add(key)
                    continue
                # 설명 판에 걸치는 흐린 것도 뺌(설명 둘레로 조각이 비치지 않게)
                X1, Y1 = X0 + bw * z, Y0 + bh * z
                if (side == 'right' and X1 > crx0 - 60) or (side == 'left' and X0 < crx1 + 60) or (side == 'top' and Y0 < cry1 + 26):
                    skipped.add(key)
                    continue
            spids[key] = [int(pa.prim(p, cam=step.cam, alpha=alpha).find('.//' + q('p:cNvPr')).get('id')) for p in prims]
        panel, cap = scene3.caption_prims(i, step.cap)
        for p in over_prims():
            pa.prim(p)
        for p in scene3.topbar_prims(step.hud):
            pa.prim(p)
        for p in cap:
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
                sp_ids = {int(e.get('id')) for e in slide._element.iter(q('p:cNvPr'))}
                slide._element.append(tl.xml(sp_ids, auto=(0, [0])))
        ns = slide.notes_slide
        if ns.notes_text_frame is None:
            for e in note_tpl:
                ns.shapes._spTree.append(copy.deepcopy(e))
        ns.notes_text_frame.text = step.notes
    prs.save(str(dst))
    return len(sc.steps)


def sheet(pngs, dst, labels, cols=4, w=560):
    ims = [Image.open(p).convert('RGB') for p in pngs]
    h = int(w * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new('RGB', (cols * (w + 10) + 10, rows * (h + 30) + 10), 'white')
    d = ImageDraw.Draw(out)
    fnt = ImageFont.truetype(str(ROOT / '06_에셋' / '글꼴' / 'NotoSansKR-700.ttf'), 16)
    for i, im in enumerate(ims):
        x, y = 10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 30)
        out.paste(im.resize((w, h), Image.LANCZOS), (x, y + 22))
        d.text((x, y), labels[i], fill=(60, 50, 90), font=fnt)
    out.save(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('versions', nargs='+')
    ap.add_argument('--png', action='store_true')
    ap.add_argument('--video', action='store_true')
    a = ap.parse_args()
    vs = ALL if a.versions == ['all'] else a.versions
    OUT.mkdir(exist_ok=True)
    import render2
    for v in vs:
        mod = importlib.import_module(v)
        sc = scene3.build(mod.SPEC)
        name = mod.SPEC['file']
        dst = OUT / (name + '.pptx')
        n = render(sc, dst, name)
        print(v, '장', n, '→', dst.name)
        if a.png:
            od = OUT / (name + '_png')
            render2.png(dst, od)
            labels = ['%d  %s' % (i + 1, ' '.join(''.join(t for t, _ in st.cap['t']).split())) for i, st in enumerate(sc.steps)]
            sheet(sorted(od.glob('s*.png')), OUT / (name + '_한눈에.png'), labels)
        if a.video:
            render2.video(dst, OUT / (name + '_미리보기.mp4'), 3.2)


if __name__ == '__main__':
    main()
