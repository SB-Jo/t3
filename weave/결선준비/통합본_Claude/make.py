#!/usr/bin/env python3
"""통합본(Claude) — 인트로 + 모션그래픽~How it Works + 뒷부분 + Appendix를 한 덱으로 → Weave_통합본_Claude.pptx

  python make.py                  덱만
  python make.py --png            + out/png/s01.png… 와 out/한눈에.png (PowerPoint로 렌더)

재료
- 인트로 2~5, 7~14쪽: 원본/통합본_인트로수정_87bf80b.pptx (jjun-0824/t3 87bf80b: 우리 3차 덱의 7~14쪽을 팀원이 손본 판)의 장을 그대로 옮긴다(도형·그림·전환·효과·노트).
  4·5쪽의 둘째 말풍선만 '그 이름이 뭐였지?' → '정확한 이름이 뭐였지?'로 바꾼다(patch_ask2).
  6차(11-13)에 더 손본 곳: 3쪽은 인물과 말풍선이 클릭해야 뜨고(patch_person_click), 3~5쪽의 옅은 기록 조각이 세 층으로 떠다닌다(patch_floats).
  7쪽 머리글, 9쪽 퍼센트와 이름의 글자 크기, 10쪽 AI 답변의 글(patch_heading7, patch_hub, patch_answer).
  4차까지는 원본/Weave_결선_중간본_도입부수정.pptx의 장을 옮겨 손보고(patch_intro) 9, 11~12, 14쪽은 새로 그렸다(slides_new.py의 s_hub2, s_scat, s_link, s_bridge).
- 6쪽(수많은 기록): 새로 그린다(slides_new.py).
- 바꾸기 전의 장: 원본/통합본_5차.pptx (git show fcf8346:…), 원본/통합본_4차.pptx (git show 406c351:…), 원본/통합본_3차.pptx (git show ab0c460:…), 원본/통합본_2차.pptx (git show 9a8bddb:…), 원본/통합본_1차.pptx (git show ab7ab74:…)에서 옮겨 덱 맨 뒤에 둔다.
- 표지와 모션그래픽 영상 장: 02_PPT/Weave_결선_중간본.pptx의 1쪽과 4쪽. 표지는 영상을 v9(10_표지영상/표지_루프.mp4, 18초)로 바꾸고 제목을 조금 줄인다(patch_cover).
  모션그래픽은 영상을 v24(08_인트로영상/Weave_모션그래픽.mp4: 제목의 색과 자간을 표지와 같게)로 바꿔 끼운다(patch_mg).
- 솔루션 3장 + How it Works 13장 + Appendix 15장: 09_HowItWorks/장표5_claude/build.py의 장을 그대로 그린다.
- 뒷부분: 원본/Weave_BI_아웃트로_통합_1110_v7.pptx (WIWLEE/t3-2)의 내용을 같은 엔진으로 다시 그린다(slides_new.py).
  6차: 기대효과는 한 장(fx_new.s_fx), 기존 기능과의 비교는 Appendix 맨 앞으로(cmp_new.s_cmp_apx), 제안 장표 묶음은 없앰.
"""
import argparse
import copy
import hashlib
import itertools
import re
import shutil
import sys
from pathlib import Path

from lxml import etree
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
READ_FIRST = [('Weave Assist', '위브 어시스트'), ('Writing Assist', '라이팅 어시스트'), ('Galaxy AI', '갤럭시 에이아이'), ('Now Nudge', '나우 넛지'), ('Finder', '파인더'), ('RAG', '래그'),
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
PREV3 = HERE / '원본' / '통합본_3차.pptx'                # 11월 12일 3차 통합본
PREV4 = HERE / '원본' / '통합본_4차.pptx'                # 11월 12일 4차 통합본
PREV5 = HERE / '원본' / '통합본_5차.pptx'                # 11월 12일 5차 통합본(밤의 낱말 수정까지, fcf8346)
INTRO2 = HERE / '원본' / '통합본_인트로수정_87bf80b.pptx'   # 팀원이 7~14쪽을 손본 덱(jjun-0824/t3 87bf80b). 2~5쪽과 7~14쪽을 여기서 옮김
MG_MP4 = ROOT / '08_인트로영상' / 'Weave_모션그래픽.mp4'      # 모션그래픽 v24(111.1초). 중간본에 든 v23과 길이와 소리가 같음
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


# 옮겨 오는 인트로 장: {키: INTRO2의 쪽}. in..의 숫자는 처음 인트로 덱의 쪽(이름을 그대로 둠). 6쪽은 새로 그림(hook)
FOREIGN = {'in02': 2, 'in03': 3, 'in04': 4, 'in05': 5, 'in07': 7, 'in08': 8, 'hub2': 9, 'in09': 10, 'scat': 11, 'link': 12, 'in12': 13, 'bridge': 14}
INTRO_KEYS = list(FOREIGN)
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
SEQ = ['cover', 'in02', 'in03', 'in04', 'in05', ('own', 'hook'), 'in07', 'in08', 'hub2', 'in09', 'scat', 'link', 'in12', 'bridge',
       'mg', ('own', 'hiw'), ('own', 'back')]
PREV_KEEP = list(range(2, 14)) + list(range(32, 42)) + [59]      # 1차 통합본에서 남겨 두는 장: 인트로 2~13쪽, 뒷부분 32~41쪽, 저장 채널 그림(59쪽)
PREV2_KEEP = list(range(2, 15)) + [26] + list(range(32, 42)) + [62]      # 2차 통합본에서: 인트로 2~14쪽, 빠진 고리(26쪽), 뒷부분 32~41쪽, 두 줄 연표 제안(62쪽)
# 5차 통합본에서: 6차에 화면이나 대본이 바뀐 장(2, 3, 7, 9, 10, 17, 18, 21~25, 28~30쪽), 기대효과 세 장(32~34), 비교 지도(35), 비즈니스 임팩트(36),
# 마무리 세 장(38~40), 제안 장표 묶음(57~60)
PREV5_KEEP = [2, 3, 7, 9, 10, 17, 18, 21, 22, 23, 24, 25, 28, 29, 30, 32, 33, 34, 35, 36, 38, 39, 40, 57, 58, 59, 60]
PREV4_KEEP = list(range(7, 15))                         # 4차 통합본에서: 우리가 그리거나 손본 7~14쪽(팀원이 손본 장으로 바뀜)
PREV3_KEEP = [16] + list(range(21, 27)) + [30, 37]      # 3차 통합본에서: 16쪽(대본), 21쪽(뺀 장), 22~26쪽과 30쪽(화면 번호와 대본), 37쪽(비교 표)


def own_specs():
    """새로 그린 장의 묶음(덱과 낭독 영상이 같은 것을 씀)."""
    return dict(hook=[N.s_hook()],
                hiw=[f() for f in HW.SOL_SLIDES] + [f() for f in HW.SLIDES], back=[f() for f in N.SLIDES_BACK],
                prop=[f() for f in N.SLIDES_PROPOSAL])


def appendix_specs():
    """Appendix: 가름 장 → 기존 기능과의 비교(6차: 본 발표에서 옮김) → How it Works Appendix → 사진과 영상 출처."""
    import cmp_new
    hw = HW.appendix_specs()
    return hw[:1] + [cmp_new.s_cmp_apx()] + hw[1:] + [N.s_credits2()]


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


def patch_mg(mg):
    """모션그래픽 장: 중간본에 든 영상을 지금 것(MG_MP4)으로 바꿔 끼운다. 길이와 소리가 같아 재생 설정은 그대로 둔다."""
    media = {r.target_part for r in mg.part.rels.values() if r.reltype.endswith(('/video', '/media'))}
    assert len(media) == 1, len(media)
    media.pop()._blob = MG_MP4.read_bytes()


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


# 11-12 밤: 덱 전체에서 '이름이' → '정확한 이름이'(설문 6번의 말 '정확한 이름이 떠오르지 않아'와 같게).
# 옮겨 온 4·5쪽은 둘째 말풍선(b2) '그 이름이 뭐였지?' → '정확한 이름이 뭐였지?', 4쪽 노트는 slides_new.INTRO_NOTES
ASK2_OLD, ASK2_HEAD = '그 이름이 뭐였지?', ('그 ', '정확한 ')         # 말풍선의 글, 바꾸는 첫 토막
ASK2_KEYS = ('in04', 'in05')
NOTE_FIX = [(ASK2_OLD, ASK2_HEAD[1] + ASK2_OLD[len(ASK2_HEAD[0]):]),          # 옮겨 온 덱의 노트에서 우리가 바꾼 곳(견줄 때 먼저 바꿔 놓음)
            ('둘째, 이름이 떠오르지', '둘째, 정확한 이름이 떠오르지')]


def patch_ask2(sl):
    """둘째 말풍선(b2)의 첫 토막을 바꾸고, 글이 늘어난 만큼 말풍선을 양옆으로 넓힌다(가운데와 꼬리는 그대로)."""
    body = by_name(sl, '!!b2/body')
    runs = list(body.iter('{%s}r' % A))
    ts = [r.find('{%s}t' % A) for r in runs]
    assert ''.join(t.text for t in ts) == ASK2_OLD and ts[0].text == ASK2_HEAD[0], [t.text for t in ts]
    pt = int(runs[0].find('{%s}rPr' % A).get('sz')) / 100
    d = N.tw(ASK2_HEAD[1], pt, 'b') - N.tw(ASK2_HEAD[0], pt, 'b')
    ts[0].text = ASK2_HEAD[1]
    x, _, w, _ = box(body)
    place(body, x=x - d / 2, w=w + d)
    gx = by_name(sl, '!!b2').find(q('p:grpSpPr')).find('{%s}xfrm' % A)       # 묶음의 상자와 자식 좌표계도 같은 만큼(배율 1 그대로)
    for o, e in (('off', 'ext'), ('chOff', 'chExt')):
        off, ext = gx.find('{%s}%s' % (A, o)), gx.find('{%s}%s' % (A, e))
        off.set('x', str(int(off.get('x')) - round(d / 2 * 9525)))
        ext.set('cx', str(int(ext.get('cx')) + round(d * 9525)))


# ------------------------------------------------------------------ 6차(11-13): 옮겨 온 인트로 장에서 더 손보는 곳
P_NS = F.NS['p']
FLOAT_LAYERS = (('a', 7, -11, 4000), ('b', -6, 10, 4800), ('c', 5, 11, 3400))      # 층, 떠 가는 만큼(x, y px), 한쪽으로 가는 데 걸리는 시간(ms)
GROUP_XML = ('<p:par xmlns:p="%s"><p:cTn id="%%d" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0">'
             '<p:tn val="%%s"/></p:cond></p:stCondLst><p:childTnLst><p:par><p:cTn id="%%d" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
             '<p:childTnLst/></p:cTn></p:par></p:childTnLst></p:cTn></p:par>') % P_NS
DRIFT_XML = ('<p:par xmlns:p="%s"><p:cTn id="%%d" presetID="0" presetClass="path" presetSubtype="0" repeatCount="indefinite" autoRev="1" '
             'accel="50000" decel="50000" fill="hold" nodeType="%%s"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
             '<p:animMotion origin="layout" path="M 0 0 L %%.5f %%.5f E" pathEditMode="relative" rAng="0" ptsTypes="">'
             '<p:cBhvr><p:cTn id="%%d" dur="%%d" fill="hold"/><p:tgtEl><p:spTgt spid="%%d"/></p:tgtEl>'
             '<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr>'
             '<p:rCtr x="0" y="0"/></p:animMotion></p:childTnLst></p:cTn></p:par>') % P_NS


def patch_person_click(sl):
    """3쪽: 장이 열리면 저절로 뜨던 인물과 말풍선을 클릭해야 뜨게 한다(그 전에는 떠다니는 기록 조각만 보임).
    저절로 시작하던 묶음을 클릭 묶음으로 바꾸고, 첫 효과가 클릭하자마자 시작하게 앞의 틈을 없앤다."""
    (g, auto), = F.groups(sl)
    assert auto
    ct = g.find(q('p:cTn'))
    for c in ct.find(q('p:stCondLst')).findall(q('p:cond')):
        if c.get('evt') == 'onBegin':
            c.getparent().remove(c)
    effs = [e for e in ct.iter(q('p:cTn')) if e.get('presetID')]
    d0 = F._delay(effs[0])
    for e in effs:
        e.find(q('p:stCondLst')).find(q('p:cond')).set('delay', str(F._delay(e) - d0))
    effs[0].set('nodeType', 'clickEffect')


def patch_floats(sl):
    """3~5쪽: 옅은 기록 조각 한 장(!!floats)을 세 층으로 나눠 끼우고(assets/intro/floats-a·b·c.png), 층마다 다른 쪽으로 천천히 갔다가 되돌아오기를
    되풀이하게 한다(장이 열리면 저절로, 장이 넘어갈 때까지). 세 장의 층 이름이 같아 장이 넘어가도 이어진다."""
    old = by_name(sl, '!!floats')
    x, y, w, h = box(old)
    pa = painter(sl)
    prev, spids = old, []
    for n, *_ in FLOAT_LAYERS:
        el = pa.el(P('floats/' + n, str(INTRO_AS / ('floats-%s.png' % n)), x, y, w, h))
        prev.addnext(el)
        prev = el
        spids.append(int(el.find(q('p:nvPicPr')).find(q('p:cNvPr')).get('id')))
    rid = old.find('.//{%s}blip' % A).get(q('r:embed'))
    old.getparent().remove(old)
    if not any(rid in e.attrib.values() for e in sl._element.iter()):
        sl.part.drop_rel(rid)
    ids = itertools.count(F._next_id(sl))
    auto = next((g for g, a in F.groups(sl) if a), None)
    if auto is None:                                        # 저절로 시작하는 묶음이 없으면(3쪽) 맨 앞에 만든다
        main = sl._element.find('.//' + q('p:cTn') + '[@nodeType="mainSeq"]')
        auto = etree.fromstring(GROUP_XML % (next(ids), main.get('id'), next(ids)))
        main.find(q('p:childTnLst')).insert(0, auto)
    inner = auto.find(q('p:cTn')).find(q('p:childTnLst'))[0].find(q('p:cTn')).find(q('p:childTnLst'))
    for (n, dx, dy, ms), spid in zip(FLOAT_LAYERS, spids):
        node = 'withEffect' if len(inner) else 'afterEffect'
        inner.append(etree.fromstring(DRIFT_XML % (next(ids), node, dx / 1280, dy / 720, next(ids), ms, spid)))


HEAD7 = ('원하는 정보를 한 번에 찾지 못한 경험', '정확한 이름이 떠오르지 않아 검색으로 찾지 못한 경험')      # 7쪽 머리글: 설문 6번의 말 그대로(33쪽과 같은 숫자, 같은 말)


def patch_heading7(sl):
    hit = [e for e in by_name(sl, '!!stat1/heading').iter('{%s}t' % A) if e.text == HEAD7[0]]
    assert len(hit) == 1, len(hit)
    hit[0].text = HEAD7[1]


HUB_PT = {'p': (1550, 1800), 'n': (1200, 1300)}       # 9쪽: 퍼센트와 그 아래 이름의 글자 크기(1/100pt). 지금 → 6차(퍼센트는 한 단계, 이름은 반 단계)


def patch_hub(sl):
    for i in range(7):
        for part, (a, b) in HUB_PT.items():
            rps = list(by_name(sl, '!!hub2/l%d/%s' % (i, part)).iter('{%s}rPr' % A, '{%s}endParaRPr' % A))
            assert rps and all(rp.get('sz') == str(a) for rp in rps), (i, part, [rp.get('sz') for rp in rps])
            for rp in rps:
                rp.set('sz', str(b))


# 10쪽 AI 답변: 세 줄. 가장 긴 첫 줄(17pt에 427px)이 말풍선 오른쪽 끝에 거의 닿는 크기(오른쪽 여백 7px). 묶음을 키워도 글자 크기는 그대로임(15pt였음).
# (글, 보라 굵게인가)
ANSWER = [[('임베딩 모델은 텍스트, 이미지, 오디오 같은 복잡한', 0)],
          [('데이터를 컴퓨터가 이해할 수 있도록 고차원의', 0)],
          [('숫자 배열(벡터)', 1), ('로 변환하는 모델입니다.', 0)]]
ANSWER_PT, ANSWER_LN = 1700, 130000                   # 글자 크기(1/100pt), 줄 간격(1/1000 %, 15pt 때는 135%): 셋째 줄 아래에 말풍선 끝까지 13px쯤 남게


def patch_answer(sl):
    """10쪽: AI 답변의 글을 바꾼다. 문단(줄) 셋의 틀은 그대로 두고 글 토막만 새로 넣는다."""
    body = by_name(sl, 'Answer text').find(q('p:txBody'))
    paras = body.findall('{%s}p' % A)
    assert len(paras) == len(ANSWER), len(paras)
    plain = copy.deepcopy(paras[0].findall('{%s}r' % A)[0])           # 보통 글 토막의 틀
    bold = copy.deepcopy(paras[0].findall('{%s}r' % A)[1])            # 보라 굵은 글 토막의 틀
    assert plain.find('{%s}rPr' % A).find('{%s}latin' % A).get('typeface').endswith('400')
    assert bold.find('{%s}rPr' % A).find('{%s}latin' % A).get('typeface').endswith('700')
    for p, runs in zip(paras, ANSWER):
        for r in p.findall('{%s}r' % A):
            p.remove(r)
        p.find('{%s}pPr' % A).find('{%s}lnSpc' % A).find('{%s}spcPct' % A).set('val', str(ANSWER_LN))
        end = p.find('{%s}endParaRPr' % A)
        for text, hl in runs:
            r = copy.deepcopy(bold if hl else plain)
            r.find('{%s}rPr' % A).set('sz', str(ANSWER_PT))
            r.find('{%s}t' % A).text = text
            if end is not None:
                end.addprevious(r)
            else:
                p.append(r)
        if end is not None:
            end.set('sz', str(ANSWER_PT))


NOTE_OURS = {'in02', 'in03', 'in07', 'hub2'}          # 6차에 우리가 노트를 바꾼 장(옮겨 온 덱의 노트와 견주지 않음)
INTRO_PATCH = {                                       # 옮겨 온 장마다 6차에 더 손보는 일
    'in03': [patch_person_click, patch_floats], 'in04': [patch_floats], 'in05': [patch_floats],
    'in07': [patch_heading7], 'hub2': [patch_hub], 'in09': [patch_answer],
}


def copy_intro(prs, note_tpl):
    """팀원이 손본 덱(INTRO2)에서 인트로 장을 그대로 옮긴다. 노트는 INTRO_NOTES(그 덱의 노트와 같은 글인지 견줘 다르면 알림). 돌려줌: {키: 장}.
    4·5쪽은 둘째 말풍선의 글을 바꾸고(patch_ask2), 6차에 더 손본 곳은 INTRO_PATCH."""
    src = list(Presentation(str(INTRO2)).slides)
    out = {}
    for k, page in FOREIGN.items():
        sl = F.copy_slide(prs, src[page - 1], note_tpl)
        theirs = F.note_text(src[page - 1])
        for old_, new_ in NOTE_FIX:
            theirs = theirs.replace(old_, new_)
        if k not in NOTE_OURS and ' '.join(theirs.split()) != ' '.join(N.INTRO_NOTES[k].split()):
            print('   ! %s(%d쪽): INTRO_NOTES가 옮겨 온 덱의 노트와 다름' % (k, page))
        if k in ASK2_KEYS:
            patch_ask2(sl)
        for fn in INTRO_PATCH.get(k, []):
            fn(sl)
        F.set_notes(sl, N.INTRO_NOTES[k], note_tpl)
        out[k] = sl
    return out


def build(dst):
    prs = Presentation(str(BASE))
    old = list(prs.slides)
    cover, mg = old[0], old[3]
    layout = old[5].slide_layout                       # How it Works 장과 같은 틀
    note_tpl = [copy.deepcopy(sh._element) for sh in old[5].notes_slide.placeholders]
    src = list(Presentation(str(INTRO)).slides)        # 처음 인트로 덱: '이전 판 (1차)'의 마지막 장에만 씀
    intro = copy_intro(prs, note_tpl)
    patch_cover(cover)
    patch_mg(mg)
    F.set_notes(cover, N.INTRO_NOTES['cover'], note_tpl)
    report = []

    def draw(specs):
        slides, rep, _ = HW.add_slides(prs, layout, note_tpl, specs)
        report.extend(rep)
        return slides
    specs = own_specs()
    own = {k: draw(v) for k, v in specs.items() if k != 'prop'}
    main = []
    for item in SEQ:
        main += own[item[1]] if isinstance(item, tuple) else [cover if item == 'cover' else mg if item == 'mg' else intro[item]]
    n_main = len(main)
    appx = draw(appendix_specs())
    prop = draw([N.s_divider('p0', '제안 장표', ['본 발표에 넣을지 정하지 않은 장'],
                             '여기부터는 제안 장표입니다. 본 발표에서는 넘기지 않습니다.')] + specs['prop']) if specs['prop'] else []      # 6차: 없음
    prev5, prev4, prev3, prev2, prev1 = (list(Presentation(str(f)).slides) for f in (PREV5, PREV4, PREV3, PREV2, PREV))
    old5 = draw([N.s_divider('o5', '이전 판 (5차)', ['11월 12일 5차 통합본에서 6차에 화면이나 대본이 바뀐 장: 2, 3, 7, 9, 10, 17, 18, 21~25, 28~30쪽',
                                                    '기대효과 세 장(32~34쪽), 비교 지도(35쪽), 비즈니스 임팩트(36쪽), 마무리 세 장(38~40쪽), 제안 장표(57~60쪽)',
                                                    '노트에 그때의 대본이 그대로 있습니다'],
                             '여기부터는 바꾸기 전의 장입니다. 본 발표에서는 넘기지 않습니다.')])
    old5 += [F.copy_slide(prs, prev5[i - 1], note_tpl) for i in PREV5_KEEP]
    old4 = draw([N.s_divider('o4', '이전 판 (4차)', ['11월 12일 4차 통합본의 7~14쪽 (팀원이 손본 장으로 바뀌기 전)',
                                                    '노트에 그때의 대본이 그대로 있습니다'],
                             '여기부터는 바꾸기 전의 장입니다. 본 발표에서는 넘기지 않습니다.')])
    old4 += [F.copy_slide(prs, prev4[i - 1], note_tpl) for i in PREV4_KEEP]
    old3 = draw([N.s_divider('o3', '이전 판 (3차)', ['11월 12일 3차 통합본의 16쪽, 뺀 21쪽, 22~26쪽, 30쪽, 비교 표(37쪽)',
                                                    '노트에 그때의 대본이 그대로 있습니다'],
                             '여기부터는 바꾸기 전의 장입니다. 본 발표에서는 넘기지 않습니다.')])
    old3 += [F.copy_slide(prs, prev3[i - 1], note_tpl) for i in PREV3_KEEP]
    old2 = draw([N.s_divider('o2', '이전 판 (2차)', ['11월 11일 2차 통합본의 인트로 2~14쪽, 빠진 고리(26쪽), 뒷부분 32~41쪽, 두 줄 연표 제안(62쪽)',
                                                    '노트에 그때의 대본이 그대로 있습니다'],
                             '여기부터는 바꾸기 전의 장입니다. 본 발표에서는 넘기지 않습니다.')])
    old2 += [F.copy_slide(prs, prev2[i - 1], note_tpl) for i in PREV2_KEEP]
    old1 = draw([N.s_divider('o1', '이전 판 (1차)', ['11월 11일 1차 통합본의 인트로 2~13쪽, 뒷부분 32~41쪽, 저장 채널 그림(59쪽)', '그 뒤는 인트로 덱의 13쪽',
                                                    '노트에 그때의 대본이 그대로 있습니다'],
                             '여기부터는 바꾸기 전의 장입니다. 본 발표에서는 넘기지 않습니다.')])
    old1 += [F.copy_slide(prs, prev1[i - 1], note_tpl) for i in PREV_KEEP] + [F.copy_slide(prs, src[12], note_tpl)]
    order = [*main, *appx, *prop, *old5, *old4, *old3, *old2, *old1]
    drop_slides(prs, [s for s in old if s not in (cover, mg)])
    reorder(prs, order)
    samsung_fonts.remap_prs(prs)
    build.n_old5, build.n_old4 = len(old5), len(old4)
    build.n_main, build.n_appx, build.n_prop, build.n_old3, build.n_old2, build.n_old1 = n_main, len(appx), len(prop), len(old3), len(old2), len(old1)
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
