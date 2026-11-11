#!/usr/bin/env python3
"""통합본(Claude) — 인트로 + 모션그래픽~How it Works + 뒷부분 + Appendix를 한 덱으로 → Weave_통합본_Claude.pptx

  python make.py                  덱만
  python make.py --png            + out/png/s01.png… 와 out/한눈에.png (PowerPoint로 렌더)

재료
- 인트로 2~5, 7~12쪽: 원본/Weave_결선_중간본_도입부수정.pptx (jjun-0824/t3). 장을 그대로 옮기고(도형·그림·전환·효과) 노트와 화면 글 두 곳, 고리 굵기를 손본다(patch_intro).
- 6쪽(수많은 기록), 8쪽 다음(기록을 남기는 곳), 13쪽(잇는 장): 새로 그린다(slides_new.py).
- 바꾸기 전의 장: 원본/통합본_1차.pptx (git show ab7ab74:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx)에서 옮겨 덱 맨 뒤에 둔다.
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
PREV = HERE / '원본' / '통합본_1차.pptx'                 # 11월 11일 1차 통합본(바꾸기 전의 장을 여기서 옮김)
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


INTRO_KEYS = ['in02', 'in03', 'in04', 'in05', 'in07', 'in08', 'in09', 'in10', 'in11', 'in12']      # 인트로 덱에서 그대로 옮기는 장(6쪽과 13쪽은 새로 그림)
RING_ADJ = ('7741', '9800')                        # 7·8쪽 고리 굵기(도형 크기의 7.7% → 9.8%, 298px에 23px → 29px)
INTRO_TEXT = {                                      # 옮겨 온 장의 화면 글을 바꾸는 곳: {장: [(원래, 지금)]}
    'in07': [('검색으로 바로 찾지 못한 경험', '원하는 정보를 한 번에 찾지 못한 경험')],
    'in12': [('내 폰에 바로 물을 순 없을까요?', '내 휴대폰에게 바로 물을 순 없을까요?')],
}
# 덱 차례(본 발표). 글자 = 옮겨 온 장, ('own', 이름) = 새로 그린 묶음, 'mg' = 모션그래픽
SEQ = ['cover', 'in02', 'in03', 'in04', 'in05', ('own', 'hook'), 'in07', 'in08', ('own', 'hub2'), 'in09', 'in10', 'in11', 'in12',
       ('own', 'bridge'), 'mg', ('own', 'hiw'), ('own', 'back')]
PREV_KEEP = list(range(2, 14)) + list(range(32, 42)) + [59]      # 1차 통합본에서 남겨 두는 장: 인트로 2~13쪽, 뒷부분 32~41쪽, 저장 채널 그림(59쪽)


def own_specs():
    """새로 그린 장의 묶음(덱과 낭독 영상이 같은 것을 씀)."""
    return dict(hook=[N.s_hook()], hub2=[N.s_hub2()], bridge=[N.s_bridge()],
                hiw=[f() for f in HW.SOL_SLIDES] + [f() for f in HW.SLIDES], back=[f() for f in N.SLIDES_BACK],
                prop=[f() for f in N.SLIDES_PROPOSAL])


def patch_intro(slides, note_tpl):
    """옮겨 온 인트로 장을 손본다: 노트(새 대본), 화면 글 두 곳, 7·8쪽 고리 굵기. slides = {키: 장}."""
    for key, sl in slides.items():
        F.set_notes(sl, N.INTRO_NOTES[key], note_tpl)
        for old, new in INTRO_TEXT.get(key, []):
            hit = [e for e in sl._element.iter('{%s}t' % A) if e.text == old]
            assert len(hit) == 1, (key, old, len(hit))
            hit[0].text = new
        if key in ('in07', 'in08'):
            n = 0
            for g in sl._element.iter('{%s}prstGeom' % A):
                if g.get('prst') in ('donut', 'blockArc'):
                    for gd in g.iter('{%s}gd' % A):
                        if gd.get('name') in ('adj', 'adj3') and gd.get('fmla') == 'val ' + RING_ADJ[0]:
                            gd.set('fmla', 'val ' + RING_ADJ[1])
                            n += 1
            assert n >= 2, (key, n)


def build(dst):
    prs = Presentation(str(BASE))
    old = list(prs.slides)
    cover, mg = old[0], old[3]
    layout = old[5].slide_layout                       # How it Works 장과 같은 틀
    note_tpl = [copy.deepcopy(sh._element) for sh in old[5].notes_slide.placeholders]
    src = list(Presentation(str(INTRO)).slides)
    intro = {k: F.copy_slide(prs, src[int(k[2:]) - 1], note_tpl) for k in INTRO_KEYS}
    patch_intro(intro, note_tpl)
    F.set_notes(cover, N.INTRO_NOTES['cover'], note_tpl)
    report = []

    def draw(specs):
        slides, rep, _ = HW.add_slides(prs, layout, note_tpl, specs)
        report.extend(rep)
        return slides
    own = {k: draw(v) for k, v in own_specs().items() if k != 'prop'}
    main = []
    for item in SEQ:
        main += own[item[1]] if isinstance(item, tuple) else [cover if item == 'cover' else mg if item == 'mg' else intro[item]]
    n_main = len(main)
    appx = draw(HW.appendix_specs() + [N.s_credits2()])
    prop = draw([N.s_divider('p0', '제안 장표', ['기대효과 세 장: 기능이 있으면 고리 그래프와 왼쪽 말이 바뀌는 안 (%d~%d쪽 자리)' % (n_main - 8, n_main - 6),
                                                  '새 연표: 두 줄 연표와 길게 말하는 대본 (%d쪽 자리)' % (n_main - 3)],
                             '여기부터는 제안 장표입니다. 본 발표에서는 넘기지 않습니다.')] + own_specs()['prop'])
    prev = list(Presentation(str(PREV)).slides)
    olds = draw([N.s_divider('o0', '이전 판', ['11월 11일 1차 통합본의 인트로 2~13쪽, 뒷부분 32~41쪽, 저장 채널 그림(59쪽)', '그 뒤는 인트로 덱의 13쪽',
                                               '노트에 그때의 대본이 그대로 있습니다'],
                             '여기부터는 바꾸기 전의 장입니다. 본 발표에서는 넘기지 않습니다.')])
    olds += [F.copy_slide(prs, prev[i - 1], note_tpl) for i in PREV_KEEP] + [F.copy_slide(prs, src[12], note_tpl)]
    order = [*main, *appx, *prop, *olds]
    drop_slides(prs, [s for s in old if s not in (cover, mg)])
    reorder(prs, order)
    samsung_fonts.remap_prs(prs)
    logo_style(own['bridge'])
    build.n_main, build.n_appx, build.n_prop, build.n_old = n_main, len(appx), len(prop), len(olds)
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
