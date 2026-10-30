"""0927_v1 덱 2차 다듬기 (2026-09-27 20시 요청). 5~8쪽은 칩 문구만 바꿈(나머지는 다음 요청).

- 공통: 칩을 작게·얇게(높이 26, 11pt, SemiBold), 칩과 제목 사이 넓힘, 영문 칩은 PowerPoint 글꼴 상자에도 Inter로 보이게
- 3쪽: 공통 배경, 하단 '내 기억' 굵게
- 4쪽: 공통 배경, 말풍선 꼬리를 얼굴 높이로, 행 제목 '그 어디'·'그 이름'·'그 얘기를' 보라, 본문-보조 문구 간격 좁힘
- 9쪽: 제목·부제, 04 반짝임 제거(7차 그래픽 레이어)      - 10쪽: 부제, 하단 두 상자 '~합니다'
- 11쪽: 문구, Weave 실타래 아이콘                            - 12쪽: 칩·부제, 표 높이 +10%, Weave 열 선·색, ○△×
- 13~15쪽: 칩 '기대 효과 0N', 제목 앞 번호 삭제             - 16쪽: 칩 'Appendix · App Demo', 제목 삭제
- 19쪽: 양서윤 '개발 T/F'

사용: python apply_round2.py --test (/tmp 사본) | --deck (실제 덱, 백업과 같을 때만)
"""
import copy
import hashlib
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.oxml import parse_xml
from pptx.oxml.ns import qn
from pptx.util import Emu

import header as hd
import pages_p2_p4 as pg
from inspect_slide import abs_boxes
from textmeasure import width

ROOT = Path(__file__).resolve().parents[1]                  # deck-0927v1
CL = ROOT.parent                                             # claude_0927
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '3_2차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round2.pptx')
PX = 9525
NS = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
INTER_OF = {'Noto Sans KR': 'Inter', 'Noto Sans KR SemiBold': 'Inter SemiBold', 'Noto Sans KR Medium': 'Inter Medium'}


def emu(v):
    return int(round(v * PX))


# ------------------------------------------------------------------ 공용 도우미
def shape(slide, name=None, sid=None, text_start=None):
    hits = []
    for sh, _ in abs_boxes(slide.shapes):
        if sid is not None and sh.shape_id != sid:
            continue
        if name is not None and sh.name != name:
            continue
        if text_start is not None and not (sh.has_text_frame and sh.text_frame.text.strip().startswith(text_start)):
            continue
        hits.append(sh)
    assert len(hits) == 1, (name, sid, text_start, len(hits))
    return hits[0]


def set_fill(rPr, color):
    for t in ('a:noFill', 'a:solidFill', 'a:gradFill', 'a:blipFill', 'a:pattFill', 'a:grpFill'):
        for el in rPr.findall(qn(t)):
            rPr.remove(el)
    sf = etree.Element(qn('a:solidFill'))
    etree.SubElement(sf, qn('a:srgbClr'), val=color)
    ln = rPr.find(qn('a:ln'))
    if ln is not None:
        ln.addnext(sf)
    else:
        rPr.insert(0, sf)


def set_fonts(rPr, latin, ea):
    for t in ('a:latin', 'a:ea', 'a:cs'):
        for el in rPr.findall(qn(t)):
            rPr.remove(el)
    after = next((rPr.find(qn(t)) for t in ('a:sym', 'a:hlinkClick', 'a:hlinkMouseOver', 'a:rtl', 'a:extLst') if rPr.find(qn(t)) is not None), None)
    for tag, face in (('a:latin', latin), ('a:ea', ea), ('a:cs', ea)):
        el = etree.Element(qn(tag), typeface=face)
        if after is not None:
            after.addprevious(el)
        else:
            rPr.append(el)


def set_text(sh, paras):
    """글자를 paras=[[(text, color|None, bold|None), ...], ...]로 바꿈. 첫 글자 서식을 틀로 쓰고, 영문 조각은 Inter."""
    txBody = sh._element.find(qn('p:txBody'))
    ps = txBody.findall(qn('a:p'))
    rs = list(txBody.iter(qn('a:r')))
    tmpl_rpr = copy.deepcopy(rs[0].find(qn('a:rPr'))) if rs else etree.Element(qn('a:rPr'))
    tmpl_p = copy.deepcopy(ps[0])
    for p in ps:
        txBody.remove(p)
    lat0, ea0 = tmpl_rpr.find(qn('a:latin')), tmpl_rpr.find(qn('a:ea'))
    ea_face = ea0.get('typeface') if ea0 is not None else 'Noto Sans KR'
    lat_face = lat0.get('typeface') if lat0 is not None else ea_face
    lat_face = INTER_OF.get(lat_face, lat_face if lat_face.startswith('Inter') else 'Inter')
    for runs in paras:
        p = copy.deepcopy(tmpl_p)
        for el in list(p):
            if el.tag in (qn('a:r'), qn('a:br'), qn('a:fld')):
                p.remove(el)
        end = p.find(qn('a:endParaRPr'))
        prev = 'ko'
        for text, color, bold in runs:
            for seg, cls in hd.split_script(text, prev):
                prev = cls
                rPr = copy.deepcopy(tmpl_rpr)
                for k in ('err', 'altLang', 'lang'):
                    rPr.attrib.pop(k, None)
                rPr.set('lang', 'en-US' if cls == 'latin' else 'ko-KR')
                if cls != 'latin':
                    rPr.set('altLang', 'en-US')
                if color:
                    set_fill(rPr, color)
                if bold is not None:
                    rPr.set('b', '1' if bold else '0')
                set_fonts(rPr, lat_face, lat_face if cls == 'latin' else ea_face)
                r = etree.Element(qn('a:r'))
                r.append(rPr)
                etree.SubElement(r, qn('a:t')).text = seg
                if end is not None:
                    end.addprevious(r)
                else:
                    p.append(r)
        txBody.append(p)


def no_autofit(sh, wrap='none', algn=None):
    bp = sh._element.find(qn('p:txBody')).find(qn('a:bodyPr'))
    if wrap:
        bp.set('wrap', wrap)
    for ch in list(bp):
        if ch.tag in (qn('a:normAutofit'), qn('a:spAutoFit'), qn('a:noAutofit')):
            bp.remove(ch)
    etree.SubElement(bp, qn('a:noAutofit'))
    if algn:
        for p in sh._element.find(qn('p:txBody')).findall(qn('a:p')):
            pPr = p.find(qn('a:pPr'))
            if pPr is None:
                pPr = etree.Element(qn('a:pPr'))
                p.insert(0, pPr)
            pPr.set('algn', algn)


def xywh(sh):
    xf = sh._element.find(qn('p:spPr')).find(qn('a:xfrm'))
    o, e = xf.find(qn('a:off')), xf.find(qn('a:ext'))
    return int(o.get('x')) / PX, int(o.get('y')) / PX, int(e.get('cx')) / PX, int(e.get('cy')) / PX


def put(sh, x=None, y=None, w=None, h=None):
    xf = sh._element.find(qn('p:spPr')).find(qn('a:xfrm'))
    o, e = xf.find(qn('a:off')), xf.find(qn('a:ext'))
    if x is not None: o.set('x', str(emu(x)))
    if y is not None: o.set('y', str(emu(y)))
    if w is not None: e.set('cx', str(emu(w)))
    if h is not None: e.set('cy', str(emu(h)))


def shift_group(grp, dy):
    off = grp._element.find(qn('p:grpSpPr')).find(qn('a:xfrm')).find(qn('a:off'))
    off.set('y', str(int(off.get('y')) + emu(dy)))


def add_sp(slide, xml, name):
    el = parse_xml(xml)
    slide.shapes._spTree.append(el)
    pg.fresh_id(el)
    el.find('.//' + qn('p:cNvPr')).set('name', name)
    return el


# ------------------------------------------------------------------ 공통 배경 (10쪽 이후와 같은 도형 3개)
def background_from(prs):
    src = next(s for s in prs.slides if any(sh.name == 'Header chip' and sh.text_frame.text == 'WHY SAMSUNG' for sh in s.shapes))
    els = [sh._element for sh in list(src.shapes)[:3]]
    assert [e.find('.//' + qn('p:cNvPr')).get('name') for e in els] == ['Shape 0', 'Shape 1', 'Shape 2']
    return els


def add_background(slide, els):
    if any(sh.name.startswith('Background · ') for sh in slide.shapes):
        return
    tree = slide.shapes._spTree
    at = list(tree).index(tree.find(qn('p:grpSpPr'))) + 1
    for k, (el, nm) in enumerate(zip(els, ('base', 'peach', 'lavender'))):
        e = copy.deepcopy(el)
        tree.insert(at + k, e)
        pg.fresh_id(e)
        e.find('.//' + qn('p:cNvPr')).set('name', f'Background · {nm}')


# ------------------------------------------------------------------ 3쪽
def p3(s, bg):
    add_background(s, bg)
    t = shape(s, text_start='세상 모든 지식은')
    hit = [r for r in t._element.iter(qn('a:r')) if r.find(qn('a:t')).text == '내 기억']
    assert len(hit) == 1
    hit[0].find(qn('a:rPr')).set('b', '1')


# ------------------------------------------------------------------ 4쪽
# 말풍선: 꼬리를 아래 모서리에서 왼쪽 변의 얼굴 높이(위에서 약 42%)로 옮김. 지현 쪽은 flipH라 오른쪽.
BUBBLE_PATH = (
    f'<a:pathLst {NS}><a:path w="3980000" h="850000">'
    '<a:moveTo><a:pt x="589000" y="0"/></a:moveTo>'
    '<a:lnTo><a:pt x="3691000" y="0"/></a:lnTo>'
    '<a:arcTo wR="289000" hR="289000" stAng="16200000" swAng="5400000"/>'
    '<a:lnTo><a:pt x="3980000" y="561000"/></a:lnTo>'
    '<a:arcTo wR="289000" hR="289000" stAng="0" swAng="5400000"/>'
    '<a:lnTo><a:pt x="589000" y="850000"/></a:lnTo>'
    '<a:arcTo wR="289000" hR="289000" stAng="5400000" swAng="5400000"/>'
    '<a:lnTo><a:pt x="300000" y="540000"/></a:lnTo>'
    '<a:cubicBezTo><a:pt x="300000" y="470000"/><a:pt x="165000" y="424000"/><a:pt x="0" y="360000"/></a:cubicBezTo>'
    '<a:cubicBezTo><a:pt x="110000" y="346000"/><a:pt x="225000" y="330000"/><a:pt x="300000" y="322000"/></a:cubicBezTo>'
    '<a:lnTo><a:pt x="300000" y="289000"/></a:lnTo>'
    '<a:arcTo wR="289000" hR="289000" stAng="10800000" swAng="5400000"/>'
    '<a:close/></a:path></a:pathLst>')

ROW_TOPS = (183.9, 294.9, 405.9)      # 01~03 행 구분선 그림의 위쪽
MAIN_REL, SUB_REL = 29.0, 63.3         # 본문·보조 문구 상자 위치(행 위쪽 기준). 보조 문구를 약 5px 올림


def p4(s, bg):
    add_background(s, bg)
    bubbles = [sh for sh in s.shapes if sh.name == 'Persona bubble']
    assert len(bubbles) == 2
    for b in bubbles:
        cg = b._element.find(qn('p:spPr')).find(qn('a:custGeom'))
        old = cg.find(qn('a:pathLst'))
        old.addprevious(parse_xml(BUBBLE_PATH))
        cg.remove(old)
    # 행 제목
    HL, INK = '6666FF', '15151C'
    t1 = shape(s, sid=202); assert t1.text_frame.text.replace(' ', '') == '그어디에있더라?'
    set_text(t1, [[('그 어디', HL, True), ('에 있더라?', INK, True)]])
    t2 = shape(s, sid=236); assert t2.text_frame.text.replace(' ', '') == '그이름이뭐였더라?'
    set_text(t2, [[('그 이름', HL, True), ('이 뭐였더라?', INK, True)]])
    t3 = shape(s, sid=30); assert t3.text_frame.text.replace(' ', '') == '그얘길했었나?'
    set_text(t3, [[('그 얘기를', HL, True), (' 했었나?', INK, True)]])
    no_autofit(t3)
    # 본문-보조 문구 간격: 세 행 모두 같은 위치로
    boxes = dict((sh.shape_id, (sh, box)) for sh, box in abs_boxes(s.shapes))
    for row, (main_grp, main_tb, sub_grp, sub_tb) in enumerate(((206, 207, 221, 222), (240, 241, 253, 254), (274, 275, 289, 290))):
        top = ROW_TOPS[row]
        for grp, tb, rel in ((main_grp, main_tb, MAIN_REL), (sub_grp, sub_tb, SUB_REL)):
            cur = boxes[tb][1][1]
            shift_group(boxes[grp][0], top + rel - cur)


# ------------------------------------------------------------------ 9쪽
def p9(s):
    pics = [sh for sh in s.shapes if sh.shape_type == 13 and sh.name.startswith('Weave graphics layer')]
    assert len(pics) == 1
    pg.replace_picture(s, pics[0], (CL / 'out' / 'page-07-pipeline.art.png').read_bytes(), crop_zero=False)
    pg.drop_unused_images(s)


# ------------------------------------------------------------------ 10쪽
def p10(s):
    for sid in (24, 30):
        sh = shape(s, sid=sid)
        hits = [r for r in sh._element.iter(qn('a:r')) if '제공한다' in (r.find(qn('a:t')).text or '')]
        assert len(hits) == 1, sid
        t = hits[0].find(qn('a:t'))
        t.text = t.text.replace('제공한다', '제공합니다')


# ------------------------------------------------------------------ 11쪽
SPOOL = ROOT / 'assets' / 'weave-spool-6B4EFF.png'


def p11(s):
    t = shape(s, sid=13); assert t.text_frame.text == '갤러리 · 삼성노트 · 캘린더'
    set_text(t, [[('갤러리 · 삼성노트 · 캘린더 등', None, None)]]); no_autofit(t); put(t, w=300)
    t = shape(s, sid=20); assert t.text_frame.text.startswith('Android AICore')
    set_text(t, [[('Android AICore', None, None)]]); no_autofit(t)
    t = shape(s, sid=21); assert t.text_frame.text.startswith('이미지 이해')
    set_text(t, [[('이미지 이해 · 요약', None, None)]]); no_autofit(t)
    t = shape(s, sid=24); assert t.text_frame.text == '온디바이스 LLM'
    set_text(t, [[('온디바이스 AI 모델', None, None)]]); no_autofit(t)
    t = shape(s, sid=25); assert t.text_frame.text.startswith('Gemini Nano')
    set_text(t, [[('Samsung Gauss', None, None)]]); no_autofit(t)
    t = shape(s, sid=26); assert t.text_frame.text == '모바일용 경량 언어모델'
    set_text(t, [[('모바일용 경량 AI 모델', None, None)]]); no_autofit(t)
    t = shape(s, sid=35); assert t.text_frame.text.startswith('남은 기록을 찾아')
    set_text(t, [[('남은 기록을 찾아, 지금의 입력에 연결', None, None)]]); no_autofit(t)
    t = shape(s, sid=36); assert t.text_frame.text.startswith('Weave는 개인 기록을')
    set_text(t, [[('기록은 이미 충분합니다.', '1C1A24', True)],
                 [('이제, ', '1C1A24', True), ('필요한 순간 기기 안에서 꺼내', '6B4EFF', True), ('줍니다.', '1C1A24', True)]])
    no_autofit(t)
    # Weave 왼쪽 실타래 아이콘 (아이콘+글자 묶음을 가운데로)
    w = shape(s, sid=34); assert w.text_frame.text == 'Weave'
    set_text(w, [[('Weave', None, None)]]); no_autofit(w, algn='l')
    x, y, bw, bh = xywh(w)
    tw = width('Weave', 17.83 * 4 / 3, 700)
    icon, gap = 24.0, 6.0
    gx = 640 - (icon + gap + tw) / 2
    put(w, x=gx + icon + gap, w=tw + 4)
    pic = s.shapes.add_picture(str(SPOOL), Emu(emu(gx)), Emu(emu(y + bh / 2 - icon / 2 - 1)), Emu(emu(icon)), Emu(emu(icon)))
    pic.name = 'Weave spool icon'
    pic._element.nvPicPr.cNvPr.set('descr', 'Weave 실타래 아이콘')


# ------------------------------------------------------------------ 12쪽
K12, T12 = 1.1, 159.9
STATUS = [('Text 48', '불가능', 'x'), ('Text 49', '일부 가능', 'tri'), ('Text 51', '제한적', 'x'), ('Text 54', '가능', 'o'),
          ('Text 57', '미지원', 'x'), ('Text 59', '일부 지원', 'tri'), ('Text 61', '제한적', 'x'), ('Text 64', '완벽 지원', 'o')]
ICON_COLOR = {'x': 'E5484D', 'tri': 'F29A2E', 'o': '26A96C'}


def prst(sh):
    g = sh._element.find('.//' + qn('a:prstGeom'))
    return g.get('prst') if g is not None else None


def icon_xml(kind, x, y, s):
    """kind 'x' | 'tri' | 'o', (x, y) = 왼쪽 위(px), s = 크기(px). 선 2px, 둥근 끝."""
    ln = f'<a:ln w="{emu(2.0)}" cap="rnd"><a:solidFill><a:srgbClr val="{ICON_COLOR[kind]}"/></a:solidFill><a:round/></a:ln>'
    if kind == 'o':
        geom, (w, h) = '<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>', (s, s)
    elif kind == 'x':
        w = h = s * 0.84
        x, y = x + (s - w) / 2, y + (s - h) / 2
        geom = ('<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/><a:pathLst>'
                '<a:path w="100" h="100" fill="none"><a:moveTo><a:pt x="0" y="0"/></a:moveTo><a:lnTo><a:pt x="100" y="100"/></a:lnTo>'
                '<a:moveTo><a:pt x="100" y="0"/></a:moveTo><a:lnTo><a:pt x="0" y="100"/></a:lnTo></a:path></a:pathLst></a:custGeom>')
    else:
        w, h = s * 1.1, s * 0.96
        x, y = x - (w - s) / 2, y + (s - h) / 2 - 0.4
        geom = ('<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/><a:pathLst>'
                '<a:path w="100" h="100"><a:moveTo><a:pt x="50" y="0"/></a:moveTo><a:lnTo><a:pt x="100" y="100"/></a:lnTo>'
                '<a:lnTo><a:pt x="0" y="100"/></a:lnTo><a:close/></a:path></a:pathLst></a:custGeom>')
    return (f'<p:sp {NS}><p:nvSpPr><p:cNvPr id="0" name="icon"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>{geom}<a:noFill/>{ln}</p:spPr></p:sp>')


def p12(s):
    f = lambda v: T12 + (v - T12) * K12
    skip = {'Shape 0', 'Shape 1', 'Shape 2', 'Header chip', 'Header title', 'Header subtitle'}
    items = [sh for sh in s.shapes if sh.name not in skip]
    assert all(sh.shape_type != 6 for sh in items)
    for sh in items:
        x, y, w, h = xywh(sh)
        if prst(sh) == 'line':
            put(sh, y=f(y))
        elif (sh.has_text_frame and sh.text_frame.text.strip()) or (prst(sh) == 'roundRect' and h < 35):
            put(sh, y=f(y + h / 2) - h / 2)
        else:
            put(sh, y=f(y), h=h * K12)
    # Weave 열: 머리칸을 아래 칸과 같은 폭으로, 칸은 선과 선 사이를 빈틈없이, 가로선은 칸 위에
    lines = [shape(s, name=n) for n in ('Shape 7', 'Shape 14', 'Shape 25', 'Shape 32', 'Shape 39', 'Shape 46')]
    L = [xywh(l)[1] for l in lines]
    head = shape(s, name='Shape 12')
    cx0, _, cw0, _ = xywh(shape(s, name='Shape 22'))
    hy = xywh(head)[1]
    put(head, x=cx0, w=cw0, y=hy, h=L[0] - hy)
    cells = [shape(s, name=n) for n in ('Shape 22', 'Shape 30', 'Shape 37', 'Shape 44', 'Shape 53', 'Shape 63')]
    last_bottom = xywh(cells[-1])[1] + xywh(cells[-1])[3]
    for i, c in enumerate(cells):
        top = L[i]
        bottom = L[i + 1] if i + 1 < len(L) else last_bottom
        put(c, x=cx0, w=cw0, y=top, h=bottom - top)
    tree = s.shapes._spTree
    for l in lines:
        tree.remove(l._element)
        tree.append(l._element)
    # 마지막 두 행: ○△× 표시
    px13 = 13 * 4 / 3
    for name, text, kind in STATUS:
        t = shape(s, name=name)
        x, y, w, h = xywh(t)
        cx = x + w / 2
        tw = width(text, px13, 700)
        size, gap = 11.0, 5.0
        gx = cx - (size + gap + tw) / 2
        if t.text_frame.text != text:
            set_text(t, [[(text, None, None)]])
        no_autofit(t, algn='l')
        put(t, x=gx + size + gap, w=tw + 6)
        cy = y + 11.4                                   # 13pt, 줄 간격 16.9pt 고정 → 한글 세로 가운데
        add_sp(s, icon_xml(kind, gx, cy - size / 2, size), f'Status icon · {kind} · {text}')


# ------------------------------------------------------------------ 16쪽 · 19쪽
def p16(s):
    t = shape(s, name='Header title')
    assert t.text_frame.text == 'App Demo'
    t._element.getparent().remove(t._element)


def p19(s):
    t = shape(s, sid=9)
    assert t.text_frame.text == '채용 T/F' and abs(xywh(t)[0] - 296) < 1
    set_text(t, [[('개발 T/F', None, None)]])


# ------------------------------------------------------------------ 실행
CHIPS = {5: 'SOLUTION: WEAVE ASSIST', 6: 'USER SCENARIO 01', 7: 'USER SCENARIO 02', 8: 'USER SCENARIO 03',
         12: '차별화 포인트', 13: '기대 효과 01', 14: '기대 효과 02', 15: '기대 효과 03', 16: 'Appendix · App Demo'}
TITLES = {9: [('Weave는 어떻게 ', None), ('기억을 엮을까요', '6B4EFF'), ('?', None)]}
SUBS = {9: [('무거운 언어모델 대신, 가벼운 임베딩 모델로 기록을 찾고 단서를 잇습니다.', None, False)],
        10: [('기본 앱과 키보드를 잇는, 시스템 레벨의 통합 경험', None, False)],
        12: [('기존 AI 서비스들과 달리, Weave는 단말 전체의 데이터를 유기적으로 연결하는 사용자 경험을 제공합니다.', None, False)]}


def labels(prs):
    return [next((sh.text_frame.text for sh in s.shapes if sh.name == 'Header chip'), None) for s in prs.slides]


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    assert labels(prs)[2:] == ['MOTIVATION', 'PAIN POINTS', 'SOLUTION', 'CUSTOMER SCENARIO', 'CUSTOMER SCENARIO', 'CUSTOMER SCENARIO',
                               'HOW IT WORKS', 'WHY SAMSUNG', 'WHY NOW', 'DIFFERENTIATION', 'EXPECTED IMPACT', 'EXPECTED IMPACT',
                               'EXPECTED IMPACT', 'Appendix', 'Appendix · Q&A', 'Appendix · Q&A', 'END'], labels(prs)
    bg = background_from(prs)
    p3(slides[2], bg)
    p4(slides[3], bg)
    p9(slides[8])
    p10(slides[9])
    p11(slides[10])
    p12(slides[11])
    p16(slides[15])
    p19(slides[18])
    for n in (13, 14, 15):                       # 제목 앞 '01'·'02'·'03' 삭제
        _, title, _ = hd.find_header(slides[n - 1])
        runs = hd.collect_runs(title)[0]
        assert runs[0][0] in ('01', '02', '03'), runs
        TITLES[n] = [(runs[1][0].lstrip(), runs[1][1])] + [(t, c) for t, c, _ in runs[2:]]
    for i, s in enumerate(slides, 1):
        r = hd.apply(s, chip_text=CHIPS.get(i), title_runs=TITLES.get(i), sub_runs=SUBS.get(i), keep_sub_colors=i in (13, 14, 15))
        if r:
            print(i, r['chip'], f"({r['chip_w']}px)", '|', r.get('title', '-'), '|', r.get('sub', ''))
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        apply(BACKUP, TEST_OUT)
