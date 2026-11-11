#!/usr/bin/env python3
"""통합본(Claude) — 인트로 + 모션그래픽~How it Works + 뒷부분 + Appendix를 한 덱으로 → Weave_통합본_Claude.pptx

  python make.py                  덱만
  python make.py --png            + out/png/s01.png… 와 out/한눈에.png (PowerPoint로 렌더)

재료
- 인트로 2~13쪽과 노트: 원본/Weave_결선_중간본_도입부수정.pptx (jjun-0824/t3). 장을 그대로 옮긴다(도형·그림·전환·효과).
- 표지와 모션그래픽 영상 장: 02_PPT/Weave_결선_중간본.pptx의 1쪽(표지 영상 v8)과 4쪽(모션그래픽 v23).
- 솔루션 3장 + How it Works 14장 + Appendix 15장: 09_HowItWorks/장표5_claude/build.py의 장을 그대로 그린다.
- 뒷부분: 원본/Weave_BI_아웃트로_통합_1110_v7.pptx (WIWLEE/t3-2)의 내용을 같은 엔진으로 다시 그린다(slides_new.py).
"""
import argparse
import copy
import re
import shutil
import sys
from pathlib import Path

from pptx import Presentation

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HIWDIR = ROOT / '09_HowItWorks' / '장표5_claude'
sys.path.insert(0, str(HIWDIR))
sys.path.insert(0, str(ROOT / '11_중간본'))
import build as HW  # noqa: E402  (How it Works 엔진: Slide, add_slides, 낭독·영상 도구)
import render_c  # noqa: E402
import samsung_fonts  # noqa: E402

import foreign as F  # noqa: E402

OUT = Path(__file__).resolve().parent / 'out'
OUT.mkdir(exist_ok=True)
for _f in ('blur_sol.png', 'blur_emb.png', 'blur_cloud.png'):       # How it Works의 흐린 배경 그림은 그쪽 것을 그대로
    if not (OUT / _f).exists():
        shutil.copyfile(HW.OUT / _f, OUT / _f)
HW.OUT = OUT                                                      # 낭독(out/tts)과 말에 맞춘 효과의 때를 이 폴더에서 읽고 씀

# ------------------------------------------------------------------ 읽는 소리: 숫자·영문을 소리 나는 대로(How it Works의 tts_text 앞에 한 번 더 거름)
READ_FIRST = [('Weave Assist', '위브 어시스트'), ('Galaxy AI', '갤럭시 에이아이'), ('Now Nudge', '나우 넛지'), ('Finder', '파인더'), ('RAG', '래그'),
              ('Multi-hop', '멀티홉'), ('PDE', '피디이'), ('KEEP', '킵'), ('AI', '에이아이'), ('Samsung', '삼성'), ('Galaxy', '갤럭시'), ("'", '')]
DIGIT = '영일이삼사오육칠팔구'


def say_pre(t):
    for k, v in READ_FIRST:
        t = t.replace(k, v)
    dec = lambda m: '%s 점 %s' % (HW._num_ko(int(m.group(1))), ''.join(DIGIT[int(d)] for d in m.group(2)))
    t = re.sub(r'(\d+)\.(\d+)\s*%', lambda m: dec(m) + ' 퍼센트', t)
    t = re.sub(r'(\d+)\s*%', lambda m: HW._num_ko(int(m.group(1))) + ' 퍼센트', t)
    t = re.sub(r'(\d+)\.(\d+)', dec, t)
    return t


_tts_text = HW.tts_text
HW.tts_text = lambda seg: _tts_text(say_pre(seg))

import slides_new as N  # noqa: E402

BASE = ROOT / '02_PPT' / 'Weave_결선_중간본.pptx'
INTRO = HERE / '원본' / 'Weave_결선_중간본_도입부수정.pptx'
DST = HERE / 'Weave_통합본_Claude.pptx'
q = F.q
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
GRAD = ('<a:gradFill xmlns:a="%s" rotWithShape="1"><a:gsLst><a:gs pos="0"><a:srgbClr val="4E36CF"/></a:gs>'
        '<a:gs pos="100000"><a:srgbClr val="8F66FF"/></a:gs></a:gsLst><a:lin ang="0" scaled="1"/></a:gradFill>') % A


def drop_slides(prs, slides):
    parts = {s.part for s in slides}
    lst = prs.slides._sldIdLst
    for e in list(lst):
        if prs.part.related_part(e.get(q('r:id'))) in parts:
            prs.part.drop_rel(e.get(q('r:id')))
            lst.remove(e)


def reorder(prs, order):
    lst = prs.slides._sldIdLst
    by_part = {prs.part.related_part(e.get(q('r:id'))): e for e in list(lst)}
    assert len(order) == len(by_part) == len({id(s) for s in order}), (len(order), len(by_part))
    for e in list(lst):
        lst.remove(e)
    for s in order:
        lst.append(by_part[s.part])


def logo_style(slides):
    """이름이 logo_word로 끝나는 글상자를 표지 제목처럼: 글꼴 Samsung Sharp Sans, 보라 그라데이션."""
    from lxml import etree
    n = 0
    for sl in slides:
        for sp in sl._element.iter(q('p:sp')):
            nv = sp.find(q('p:nvSpPr') + '/' + q('p:cNvPr'))
            if nv is None or not nv.get('name', '').endswith('logo_word'):
                continue
            for rp in sp.iter('{%s}rPr' % A, '{%s}endParaRPr' % A):
                for tag in ('latin', 'ea', 'cs'):
                    e = rp.find('{%s}%s' % (A, tag))
                    if e is not None:
                        e.set('typeface', 'Samsung Sharp Sans')
                rp.set('b', '1')
                old = rp.find('{%s}solidFill' % A)
                if old is not None:
                    old.addprevious(etree.fromstring(GRAD))
                    rp.remove(old)
            n += 1
    return n


def build(dst):
    prs = Presentation(str(BASE))
    old = list(prs.slides)
    cover, mg = old[0], old[3]
    layout = old[5].slide_layout                       # How it Works 장과 같은 틀
    note_tpl = [copy.deepcopy(sh._element) for sh in old[5].notes_slide.placeholders]
    src = Presentation(str(INTRO))
    intro = [F.copy_slide(prs, s, note_tpl) for s in list(src.slides)[1:13]]
    F.set_notes(cover, F.note_text(src.slides[0]), note_tpl)
    report = []

    def draw(specs):
        slides, rep, _ = HW.add_slides(prs, layout, note_tpl, specs)
        report.extend(rep)
        return slides
    bridge = draw([N.s_bridge()])
    hiw = draw([f() for f in HW.SOL_SLIDES] + [f() for f in HW.SLIDES])
    back = draw([f() for f in N.SLIDES_BACK])
    appx = draw(HW.appendix_specs() + [N.s_credits2()])
    n_main = 1 + 11 + 1 + 1 + len(hiw) + len(back)
    tl_no = n_main - 4                                  # 기존 연표 쪽 번호(마무리 3장과 끝 화면 앞)
    prop = draw([N.s_p_divider(['설문의 저장 채널 그림: 인트로 8쪽 뒤에 넣는 안',
                                '새 연표: %d쪽 연표 자리에 넣는 안' % tl_no,
                                '교체 전: 인트로 덱의 13쪽 (지금은 13쪽 자리에 새 장이 들어가 있음)'])] + [f() for f in N.SLIDES_PROPOSAL])
    order = [cover, *intro[:11], *bridge, mg, *hiw, *back, *appx, *prop, intro[11]]
    drop_slides(prs, [s for s in old if s not in (cover, mg)])
    reorder(prs, order)
    samsung_fonts.remap_prs(prs)
    logo_style(bridge + back)
    build.n_main = n_main
    prs.save(str(dst))
    for key, nclick, nnote, _ in report:
        if nclick != nnote:
            print('   ! %s: 클릭 %d ≠ 노트 (클릭) %d' % (key, nclick, nnote))
    return order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--png', action='store_true')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    order = build(DST)
    print('→', DST.name, '%.1f MB' % (DST.stat().st_size / 1e6), len(order), '장')
    if a.png:
        pngs = render_c.png(DST, OUT / 'png', 1600, 900)
        print('png', len(pngs))


if __name__ == '__main__':
    main()
