#!/usr/bin/env python3
"""HOW IT WORKS v5 — 모핑 카메라 장면(흩어진 기록 더미, 키워드·임베딩 실패, 13~15장), 시나리오 7가지.

  python build5.py a1 a2 ...        out/<이름>.pptx (+ 검사: 초점이 화면 밖·설명에 걸치는지)
  python build5.py all --png        모두 + PowerPoint 장별 PNG·한눈에 보기
  python build5.py a1 --video       + 미리보기 영상(장마다 3.4초)
"""
import argparse
import copy
import importlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation

import hiw_lib as L
import scene5
import story as S
from hiw_lib import q

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / '11_중간본'))
import samsung_fonts  # noqa: E402  덱과 같은 글꼴(SamsungOneKorean)로 저장
DECK = ROOT / '02_PPT' / 'Weave_결선.pptx'
OUT = HERE / 'out'
ALL = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'c3']


def bg_prims():
    return [S.R('bg/base', 0, 0, 1280, 720, fill=None,
                grad=dict(stops=[(0, 'FDFCFF', None), (50, 'F8F5FF', None), (100, 'F2EDFF', None)], ang=70))]


def over_prims():
    return [S.R('mask/top', 0, 0, 1280, 86, fill=None,
                grad=dict(stops=[(0, 'FCFBFF', 100), (72, 'FBFAFF', 96), (100, 'FBFAFF', 0)], ang=90)),
            S.R('bg/glow1', 640, 0, 640, 507, fill=None,
                grad=dict(stops=[(0, 'C6B3FF', 22), (30, 'DED3FF', 10), (60, 'F8F5FF', 0)], path='circle', rect=(85, 8, 15, 92))),
            S.R('bg/glow2', 0, 373, 600, 347, fill=None,
                grad=dict(stops=[(0, 'BAA6FF', 24), (40, 'DCD0FF', 12), (72, 'F8F5FF', 0)], path='circle', rect=(12, 88, 88, 12)))]


def screen_box(box, cam):
    cx, cy, z, vx, vy = cam
    bx, by, bw, bh = box
    return ((bx - cx) * z + vx, (by - cy) * z + vy, bw * z, bh * z)


def hits(a, b, m=0):
    return a[0] < b[0] + b[2] + m and b[0] < a[0] + a[2] + m and a[1] < b[1] + b[3] + m and b[1] < a[1] + a[3] + m


LINES = ('th', 'gth', 'fl', 'bk', 'sth', 'sbk', 'lc')
CUT_SKIP = ('ui.glogo', 'ui.head', 'ui.msg', 'ui.sbox', 'res', 'ui.res', 'qp.head')


def is_frame(key):
    """잘려도 되는 큰 바탕(폰·질문 판·엔진 판). 가까이 볼 때 화면 끝에 걸치는 게 자연스러움."""
    return (key == 'ui' or (key.startswith('ui.') and key not in CUT_SKIP) or key in ('qp', 'gen', 'kw', 'emb') or key.startswith('re:')
            or key.startswith('fl') or '.th' in key
            or key.startswith('th') or key.startswith('gth') or key.startswith('bk') or key.startswith('sth') or key.startswith('sbk'))


def place(sc, step):
    """장마다 그릴 것과 투명도. 흐린 것이 화면 끝·위 띠·설명에 걸치면 빼고(조각 방지), 화면 밖에 통째로 있으면 그대로 둠(모핑으로 날아감)."""
    (crect, side) = step.cap_rect
    out, skipped, warn = [], set(), []
    child_of = {c: p for p, cs in sc.groups.items() for c in cs}
    fboxes = [screen_box(sc.box[k], step.cam) for k in step.show if k in step.focus and not is_frame(k)]
    for key in step.show:
        foc = key in step.focus
        half = key in step.half
        if child_of.get(key) in skipped and not (foc or half):
            continue
        sb = screen_box(sc.box[key], step.cam)
        alpha = step.alpha.get(key, 100 if foc else (55 if half else S.DIM))
        if alpha <= 0:
            continue
        inside = sb[0] >= -1 and sb[1] >= 90 and sb[0] + sb[2] <= 1281 and sb[1] + sb[3] <= 721
        outside = sb[0] > 1282 or sb[0] + sb[2] < -2 or sb[1] > 722 or sb[1] + sb[3] < -2
        if key in CUT_SKIP and not inside:      # 폰 위쪽 글(로고·대화 머리·말풍선·검색창)은 반쯤 잘려 보이면 뺌
            continue
        if not foc and not half and key.startswith(LINES):        # 흐린 실·점선은 그리지 않음(조각처럼 보임)
            continue
        if foc:
            if not inside and not is_frame(key):
                warn.append('초점 %s 이(가) 화면 밖으로 걸침 %s' % (key, tuple(round(v) for v in sb)))
            if hits(sb, crect, 6) and not is_frame(key):
                warn.append('초점 %s 이(가) 설명과 겹침' % key)
        elif not outside:
            cut_ok = half and is_frame(key)
            if (not inside and not cut_ok) or (hits(sb, crect, 16) and not cut_ok):
                skipped.add(key)
                continue
            if not half and not is_frame(key) and any(hits(sb, fb, 6) for fb in fboxes):
                skipped.add(key)
                continue
        out.append((key, alpha))
    return out, warn


def render(sc, dst):
    prs = Presentation(str(DECK))
    layout = prs.slides[8].slide_layout
    note_tpl = [copy.deepcopy(sh._element) for sh in prs.slides[8].notes_slide.placeholders]
    lst = prs.slides._sldIdLst
    for s in list(lst):
        prs.part.drop_rel(s.get(q('r:id')))
        lst.remove(s)
    _, warns = add_steps(prs, sc, layout, note_tpl)
    samsung_fonts.remap_prs(prs)
    prs.save(str(dst))
    return len(sc.steps), warns


def add_steps(prs, sc, layout, note_tpl):
    """장면의 단계마다 장을 prs 끝에 붙임(덱 조립에서도 씀). 돌려줌: (새 장 목록, 경고)."""
    warns, new = [], []
    for i, step in enumerate(sc.steps):
        slide = prs.slides.add_slide(layout)
        new.append(slide)
        for ph in list(slide.placeholders):
            ph._element.getparent().remove(ph._element)
        pa = S.Painter(slide)
        spids = {}
        for p in bg_prims():
            pa.prim(p)
        items, warn = place(sc, step)
        warns += ['%d장 %s: %s' % (i + 1, step.key, w) for w in warn]
        for key, alpha in items:
            prims = sc.items[key](step.styles.get(key))
            spids[key] = [int(pa.prim(p, cam=step.cam, alpha=alpha).find('.//' + q('p:cNvPr')).get('id')) for p in prims]
        for p in over_prims():
            pa.prim(p)
        for p in scene5.topbar_prims(step.hud):
            pa.prim(p)
        crect, side = step.cap_rect
        for p in scene5.caption_prims(i, step.cap, side, crect):
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
    return new, warns


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
        sc = scene5.build(mod.SPEC)
        name = mod.SPEC['file']
        dst = OUT / (name + '.pptx')
        n, warns = render(sc, dst)
        print(v, '장', n, '→', dst.name)
        for w in warns:
            print('   !', w)
        zs = ' '.join('%.2f' % st.cam[2] for st in sc.steps)
        print('   배율', zs)
        if a.png:
            od = OUT / (name + '_png')
            render2.png(dst, od)
            labels = ['%d  %s  (×%.1f)' % (i + 1, st.label, st.cam[2]) for i, st in enumerate(sc.steps)]
            sheet(sorted(od.glob('s*.png')), OUT / (name + '_한눈에.png'), labels)
        if a.video:
            render2.video(dst, OUT / (name + '_미리보기.mp4'), 3.4)


if __name__ == '__main__':
    main()
