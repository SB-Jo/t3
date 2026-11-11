#!/usr/bin/env python3
"""통합본(Claude) — 인트로 + 모션그래픽~How it Works + 뒷부분 + Appendix를 한 덱으로 → Weave_통합본_Claude.pptx

  python make.py                  덱만
  python make.py --png            + out/png/s01.png… 와 out/한눈에.png (PowerPoint로 렌더)

재료
- 인트로 2~5, 7~8, 10, 13쪽: 원본/Weave_결선_중간본_도입부수정.pptx (jjun-0824/t3). 장을 그대로 옮기고(도형·그림·전환·효과) 노트와 화면 몇 곳을 손본다(patch_intro).
- 6쪽(수많은 기록), 9쪽(기록을 남기는 곳), 11~12쪽(흩어진 기록이 이어짐), 14쪽(잇는 장): 새로 그린다(slides_new.py).
- 바꾸기 전의 장: 원본/통합본_2차.pptx (git show 9a8bddb:…)와 원본/통합본_1차.pptx (git show ab7ab74:…)에서 옮겨 덱 맨 뒤에 둔다.
- 표지와 모션그래픽 영상 장: 02_PPT/Weave_결선_중간본.pptx의 1쪽과 4쪽(모션그래픽 v23). 표지는 영상을 v9(10_표지영상/표지_루프.mp4, 18초)로 바꾸고 제목을 조금 줄인다(patch_cover).
- 솔루션 3장 + How it Works 14장 + Appendix 15장: 09_HowItWorks/장표5_claude/build.py의 장을 그대로 그린다.
- 뒷부분: 원본/Weave_BI_아웃트로_통합_1110_v7.pptx (WIWLEE/t3-2)의 내용을 같은 엔진으로 다시 그린다(slides_new.py).
"""
import argparse
import copy
import hashlib
import itertools
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
from ui import P, Painter  # noqa: E402

import foreign as F  # noqa: E402

OUT = Path(__file__).resolve().parent / 'out'
OUT.mkdir(exist_ok=True)
for _f in ('blur_sol.png', 'blur_emb.png', 'blur_cloud.png'):       # How it Works의 흐린 배경 그림은 그쪽 것을 그대로
    if not (OUT / _f).exists():
        shutil.copyfile(HW.OUT / _f, OUT / _f)
HW.OUT = OUT                                                      # 낭독(out/tts)과 말에 맞춘 효과의 때를 이 폴더에서 읽고 씀

# ------------------------------------------------------------------ 읽는 소리: 숫자·영문을 소리 나는 대로(How it Works의 tts_text 앞에 한 번 더 거름)
READ_FIRST = [('Weave Assist', '위브 어시스트'), ('Galaxy AI', '갤럭시 에이아이'), ('Now Nudge', '나우 넛지'), ('Finder', '파인더'), ('RAG', '래그'),
              ('AgentIR', '에이전트 아이알'), ('Hi-Q', '하이큐'), ('NPU', '엔피유'), ('Lock-in', '락인'),
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
PREV2 = HERE / '원본' / '통합본_2차.pptx'                # 11월 11일 2차 통합본
COVER_MP4 = ROOT / '10_표지영상' / '표지_루프.mp4'      # 표지 영상 v9(18초)
COVER_JPG = ROOT / '10_표지영상' / '표지_포스터.jpg'
COVER_PT = 48                                          # 표지 제목 크기(54 → 48pt: 'Assist'의 t가 뒤 영상의 '부재중 전화' 조각에 닿지 않게)
INTRO_AS = HERE / 'assets' / 'intro'                   # 3~5쪽의 옅은 기록 조각, 13쪽의 흐린 배경

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


INTRO_KEYS = ['in02', 'in03', 'in04', 'in05', 'in07', 'in08', 'in09', 'in12']      # 인트로 덱에서 옮기는 장(숫자 = 그 덱의 쪽). 6, 10~11, 13쪽은 새로 그림
RING_ADJ = ('7741', '9800')                        # 7·8쪽 고리 굵기(도형 크기의 7.7% → 9.8%, 298px에 23px → 29px)
OLD_SRC = '* 출처: 스마트폰 내 개인 기록 탐색 및 재검색 행태 설문조사 (응답 210명, 2026. 11)'
INTRO_TEXT = {                                      # 옮겨 온 장의 화면 글을 바꾸는 곳: {장: [(원래, 지금)]}
    'in07': [('검색으로 바로 찾지 못한 경험', '원하는 정보를 한 번에 찾지 못한 경험'), (OLD_SRC, N.SURVEY_SRC)],
    'in08': [(OLD_SRC, N.SURVEY_SRC)],
    'in12': [('내 폰에 바로 물을 순 없을까요?', '내 휴대폰에게 바로 물을 순 없을까요?')],
}
# 3~5쪽 말풍선: {장: {말풍선: 옆으로 옮기는 만큼(px)}}. 가운데 인물의 말풍선은 조금 오른쪽, 오른쪽 인물의 말풍선은 조금 왼쪽으로
BUBBLE_DX = {'in04': {'b2': 24}, 'in05': {'b2': 24, 'b3': -40}}
# 말풍선 꼬리(동그라미 둘)의 자리: 몸통 왼쪽 끝에서 큰 동그라미, 작은 동그라미의 가운데까지(px). 없으면 그대로(왼쪽 인물: 왼쪽에서)
BUBBLE_TAIL = {'b2': lambda w: (w / 2, w / 2 - 7),             # 가운데 인물: 말풍선 한가운데에서
               'b3': lambda w: (w - 128.5, w - 114)}           # 오른쪽 인물: 왼쪽 인물과 좌우가 뒤집힌 자리(오른쪽에서)
FLOATS_BOX = (0, 16, 1280, 236)                     # 3~5쪽 말풍선 위에 흩어진 옅은 기록 조각(assets/intro/floats.png). 제목은 빼고 그 자리까지 씀
NOTE_OLD_SHA1 = 'd9375bd6e2'                        # 가장자리에 흰 테가 남은 삼성노트 아이콘(sha1 앞 10자리). 옮겨 온 장에서는 다듬은 것으로 바꿔 끼움
# 덱 차례(본 발표). 글자 = 옮겨 온 장, ('own', 이름) = 새로 그린 묶음, 'mg' = 모션그래픽
SEQ = ['cover', 'in02', 'in03', 'in04', 'in05', ('own', 'hook'), 'in07', 'in08', ('own', 'hub2'), 'in09', ('own', 'rec'), 'in12',
       ('own', 'bridge'), 'mg', ('own', 'hiw'), ('own', 'back')]
PREV_KEEP = list(range(2, 14)) + list(range(32, 42)) + [59]      # 1차 통합본에서 남겨 두는 장: 인트로 2~13쪽, 뒷부분 32~41쪽, 저장 채널 그림(59쪽)
PREV2_KEEP = list(range(2, 15)) + [26] + list(range(32, 42)) + [62]      # 2차 통합본에서: 인트로 2~14쪽, 빠진 고리(26쪽), 뒷부분 32~41쪽, 두 줄 연표 제안(62쪽)


def own_specs():
    """새로 그린 장의 묶음(덱과 낭독 영상이 같은 것을 씀)."""
    return dict(hook=[N.s_hook()], hub2=[N.s_hub2()], rec=[N.s_scat(), N.s_link()], bridge=[N.s_bridge()],
                hiw=[f() for f in HW.SOL_SLIDES] + [f() for f in HW.SLIDES], back=[f() for f in N.SLIDES_BACK],
                prop=[f() for f in N.SLIDES_PROPOSAL])


# ------------------------------------------------------------------ 옮겨 온 장을 손보는 도구
def live_tree(slide):
    return slide._element.find(q('p:cSld')).find(q('p:spTree'))


def painter(slide):
    """옮겨 온 장에 엔진의 원시 도형을 그려 넣는 붓. 옮겨 온 장은 python-pptx의 shapes가 옛 도형 나무를 붙들고 있어서 지금 나무에 직접 넣는다."""
    pa = Painter(slide)
    pa.tree = live_tree(slide)
    ids = [int(e.get('id')) for e in pa.tree.iter() if e.tag.endswith('}cNvPr') and (e.get('id') or '').isdigit()]
    pa.ids = itertools.count(max(ids) + 1)
    return pa


def by_name(slide, name):
    """이름이 name인 도형(묶음, 그림 포함)의 요소."""
    hit = [e.getparent().getparent() for e in live_tree(slide).iter() if e.tag.endswith('}cNvPr') and e.get('name') == name]
    assert len(hit) == 1, (name, len(hit))
    return hit[0]


def has(slide, name):
    return any(e.get('name') == name for e in live_tree(slide).iter() if e.tag.endswith('}cNvPr'))


def xfrm(el):
    return el.find('.//{%s}xfrm' % A)


def shift(el, dx=0, dy=0):
    off = xfrm(el).find('{%s}off' % A)
    off.set('x', str(int(off.get('x')) + round(dx * 9525)))
    off.set('y', str(int(off.get('y')) + round(dy * 9525)))


def box(el):
    x = xfrm(el)
    off, ext = x.find('{%s}off' % A), x.find('{%s}ext' % A)
    return [int(off.get('x')) / 9525, int(off.get('y')) / 9525, int(ext.get('cx')) / 9525, int(ext.get('cy')) / 9525]


def place(el, x=None, y=None, w=None, h=None):
    xf = xfrm(el)
    off, ext = xf.find('{%s}off' % A), xf.find('{%s}ext' % A)
    for e, k, v in ((off, 'x', x), (off, 'y', y), (ext, 'cx', w), (ext, 'cy', h)):
        if v is not None:
            e.set(k, str(round(v * 9525)))


def repoint(slide, pic, path):
    """그림 도형이 다른 그림 파일을 가리키게 한다(같은 그림을 쓰는 다른 장은 그대로)."""
    blip = pic.find('.//{%s}blip' % A)
    old = blip.get(q('r:embed'))
    blip.set(q('r:embed'), slide.part.get_or_add_image_part(str(path))[1])
    if old != blip.get(q('r:embed')) and not any(old in e.attrib.values() for e in slide._element.iter()):
        slide.part.drop_rel(old)                            # 이 장에서 더 쓰지 않는 예전 그림과의 관계는 지움


def patch_cover(cover):
    """표지: 영상을 v9로, 포스터도 그 첫 장으로. 제목과 아이콘을 COVER_PT에 맞춰 줄인다(왼쪽 끝과 세로 가운데는 그대로)."""
    media = {r.target_part for r in cover.part.rels.values() if r.reltype.endswith(('/video', '/media'))}
    assert len(media) == 1, len(media)
    media.pop()._blob = COVER_MP4.read_bytes()
    repoint(cover, by_name(cover, 'Cover loop video'), COVER_JPG)
    ms = round(HW.video_len(COVER_MP4) * 1000)
    for c in cover._element.iter(q('p:cmd')):
        c.find(q('p:cBhvr')).find(q('p:cTn')).set('dur', str(ms))
    title = by_name(cover, '!!cover/title')
    k = COVER_PT / (int(next(title.iter('{%s}rPr' % A)).get('sz')) / 100)
    mark, icon = by_name(cover, '!!cover/mark'), by_name(cover, '!!cover/mark_icon')
    mx, my, mw, mh = box(mark)
    ix, iy, iw, ih = box(icon)
    tx = box(title)[0]
    cy = my + mh / 2
    place(mark, mx, cy - mh * k / 2, mw * k, mh * k)
    place(icon, mx + (mw - iw) * k / 2, cy - ih * k / 2, iw * k, ih * k)
    place(title, x=mx + (tx - mx) * k)
    for rp in title.iter('{%s}rPr' % A, '{%s}endParaRPr' % A):
        if rp.get('sz'):
            rp.set('sz', str(round(COVER_PT * 100)))


def patch_bubbles(key, sl):
    """3~5쪽: 제목('기억이 나지 않는 막막한 순간들')을 빼고 그 자리까지 옅은 기록 조각을 흩어 둠. 첫 말풍선의 글, 말풍선 자리와 꼬리도 바꿈."""
    title = by_name(sl, '!!title')
    title.getparent().remove(title)
    runs = list(by_name(sl, '!!b1/body').iter('{%s}r' % A))
    assert [r.find('{%s}t' % A).text for r in runs] == ['그게 ', '어디에', ' 있더라?'], [r.find('{%s}t' % A).text for r in runs]
    runs[0].getparent().remove(runs[0])                     # '그게 어디에 있더라?' → '어디에 적어 놨더라?'
    runs[2].find('{%s}t' % A).text = ' 적어 놨더라?'
    for b in ('b2', 'b3'):
        if not has(sl, '!!' + b):
            continue
        bx, _, bw, _ = box(by_name(sl, '!!%s/body' % b))
        for dot, cx in zip(('dot1', 'dot2'), BUBBLE_TAIL[b](bw)):
            d = by_name(sl, '!!%s/%s' % (b, dot))
            place(d, x=bx + cx - box(d)[2] / 2)
        shift(by_name(sl, '!!' + b), dx=BUBBLE_DX.get(key, {}).get(b, 0))
    pa = painter(sl)
    x, y, w, h = FLOATS_BOX
    pa.put('floats', [P('floats', str(INTRO_AS / 'floats.png'), x, y, w, h)])
    fl = pa.tree[-1]
    pa.tree.remove(fl)
    by_name(sl, 'Background · lavender').addnext(fl)        # 배경 바로 위, 인물·말풍선 아래


def patch_ai(sl):
    """10쪽: AI 표시를 글꼴의 ✦ 글자 대신 벡터 도형으로(솔루션 장의 '요약', '자동 완성 추천' 옆 표시와 같은 모양). 글꼴이 없는 컴퓨터에서도 같은 모양."""
    pa = painter(sl)
    icon = by_name(sl, 'AI icon')
    ts = list(icon.iter('{%s}t' % A))
    assert [t.text for t in ts] == ['✦'], [t.text for t in ts]
    ts[0].text = ''
    x, y, w, h = box(icon)
    icon.addnext(pa.el(N.spark_icon('ai/spark', x + w / 2 - 12.5, y + h / 2 - 11.5, size=25, color='FFFFFF')[0]))
    lab = by_name(sl, 'Answer label')
    ts = list(lab.iter('{%s}t' % A))
    assert [t.text for t in ts] == ['✦ AI 답변'], [t.text for t in ts]
    ts[0].text = 'AI 답변'
    x, y, w, h = box(lab)
    lab.addnext(pa.el(N.spark_icon('ai/spark2', x - 1, y + h / 2 - 8, size=16, color=N.PURPLE)[0]))
    shift(lab, dx=18)


def patch_intro(slides, note_tpl):
    """옮겨 온 인트로 장을 손본다: 노트(새 대본), 화면 글, 7·8쪽 고리 굵기, 3~5쪽 말풍선과 기록 조각, 10쪽 AI 표시, 13쪽 흐린 배경, 삼성노트 아이콘.
    slides = {키: 장}."""
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
        if key in ('in03', 'in04', 'in05'):
            patch_bubbles(key, sl)
        if key == 'in09':
            patch_ai(sl)
        if key == 'in12':                                   # 흐린 배경: 12쪽의 마지막 모습(기록이 이어진 모습)을 흐리게 한 그림
            f = INTRO_AS / 'blur_link.jpg'
            if f.exists():
                repoint(sl, by_name(sl, '!!blur8'), f)
            else:
                print('   ! assets/intro/blur_link.jpg 없음 → 13쪽 배경은 예전 그림 그대로 (make.py --png 뒤 tools/intro_assets.py --blur)')
        for pic in sl._element.iter(q('p:pic')):            # 삼성노트 아이콘
            rid = pic.find('.//{%s}blip' % A).get(q('r:embed'))
            if hashlib.sha1(sl.part.related_part(rid).blob).hexdigest().startswith(NOTE_OLD_SHA1):
                repoint(sl, pic, N.ICON['note'])


def build(dst):
    prs = Presentation(str(BASE))
    old = list(prs.slides)
    cover, mg = old[0], old[3]
    layout = old[5].slide_layout                       # How it Works 장과 같은 틀
    note_tpl = [copy.deepcopy(sh._element) for sh in old[5].notes_slide.placeholders]
    src = list(Presentation(str(INTRO)).slides)
    intro = {k: F.copy_slide(prs, src[int(k[2:]) - 1], note_tpl) for k in INTRO_KEYS}
    patch_intro(intro, note_tpl)
    patch_cover(cover)
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
    prop = draw([N.s_divider('p0', '제안 장표', ['기대효과 세 장: 기능이 있으면 고리 그래프와 왼쪽 말이 바뀌는 안 (%d~%d쪽 자리)' % (n_main - 8, n_main - 6)],
                             '여기부터는 제안 장표입니다. 본 발표에서는 넘기지 않습니다.')] + own_specs()['prop'])
    prev2, prev1 = list(Presentation(str(PREV2)).slides), list(Presentation(str(PREV)).slides)
    old2 = draw([N.s_divider('o2', '이전 판 (2차)', ['11월 11일 2차 통합본의 인트로 2~14쪽, 빠진 고리(26쪽), 뒷부분 32~41쪽, 두 줄 연표 제안(62쪽)',
                                                    '노트에 그때의 대본이 그대로 있습니다'],
                             '여기부터는 바꾸기 전의 장입니다. 본 발표에서는 넘기지 않습니다.')])
    old2 += [F.copy_slide(prs, prev2[i - 1], note_tpl) for i in PREV2_KEEP]
    old1 = draw([N.s_divider('o1', '이전 판 (1차)', ['11월 11일 1차 통합본의 인트로 2~13쪽, 뒷부분 32~41쪽, 저장 채널 그림(59쪽)', '그 뒤는 인트로 덱의 13쪽',
                                                    '노트에 그때의 대본이 그대로 있습니다'],
                             '여기부터는 바꾸기 전의 장입니다. 본 발표에서는 넘기지 않습니다.')])
    old1 += [F.copy_slide(prs, prev1[i - 1], note_tpl) for i in PREV_KEEP] + [F.copy_slide(prs, src[12], note_tpl)]
    order = [*main, *appx, *prop, *old2, *old1]
    drop_slides(prs, [s for s in old if s not in (cover, mg)])
    reorder(prs, order)
    samsung_fonts.remap_prs(prs)
    logo_style(own['bridge'])
    build.n_main, build.n_appx, build.n_prop, build.n_old2, build.n_old1 = n_main, len(appx), len(prop), len(old2), len(old1)
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
