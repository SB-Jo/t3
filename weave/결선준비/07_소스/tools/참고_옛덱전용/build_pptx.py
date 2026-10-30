"""HTML 렌더 결과(out/*.layout.json, out/*.art.png)로 PPTX 슬라이드를 만듭니다.

층 구성(아래→위): 덱 배경 도형 3개(통합.pptx 11번 슬라이드 XML 복사) → 카드·칩 등 네이티브 도형
→ 아이콘·사진·화살표 그래픽 레이어(PNG) → 편집 가능한 텍스트박스.
텍스트박스는 덱의 기존 Presenton 변환과 같은 규칙(요소 위치 그대로, 여백 0, 줄간격 '고정')을 따릅니다.

출력
  out/weave-claude0927-3slides.pptx   새 슬라이드 3장만 (통합.pptx 마스터 사용)
  out/통합_claude0927_반영본.pptx      통합.pptx 사본의 10·18·19번 슬라이드를 교체한 검토본
원본 통합.pptx는 읽기만 합니다.
"""
import copy
import json
import re
import shutil
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.util import Emu
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out'
SRC_DECK = ROOT.parent / 'added_0926' / '통합.pptx'
PX = 9525  # 1px = 9525 EMU (1280×720 캔버스 = 12192000×6858000 EMU)

PAGES = [  # (html 이름, 통합.pptx에서 교체할 슬라이드 번호, 발표자 노트 파일)
    ('page-07-pipeline', 10, 'notes/page-07-pipeline.txt'),
    ('page-15-qna', 18, 'notes/page-15-qna.txt'),
    ('page-16-glossary', 19, 'notes/page-16-glossary.txt'),
]

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'


def emu(v):
    return int(round(float(v) * PX))


def font_for(fam, weight):
    """브라우저 글꼴 → 덱에서 이미 쓰는 PowerPoint 글꼴 이름."""
    w = int(weight or 400)
    if fam.startswith('Nanum Pen'):
        return 'Nanum Pen Script', False
    if fam.startswith('Inter'):
        if w >= 700:
            return 'Inter', True
        if w >= 600:
            return 'Inter SemiBold', False
        return 'Inter', False
    if w >= 700:
        return 'Noto Sans KR', True
    if w >= 600:
        return 'Noto Sans KR SemiBold', False
    return 'Noto Sans KR', False


def solid_fill(parent, hexv, alpha=1.0):
    sf = etree.SubElement(parent, f'{{{A}}}solidFill')
    c = etree.SubElement(sf, f'{{{A}}}srgbClr', val=hexv)
    if alpha < 0.999:
        etree.SubElement(c, f'{{{A}}}alpha', val=str(int(round(alpha * 100000))))
    return sf


def parse_shadow(css):
    # 예: "rgba(107, 78, 255, 0.07) 0px 10px 28px 0px"
    m = re.match(r'rgba?\(([^)]+)\)\s+(-?[\d.]+)px\s+(-?[\d.]+)px\s+([\d.]+)px', css or '')
    if not m:
        return None
    p = [float(v) for v in m.group(1).split(',')]
    hexv = ''.join(f'{int(round(v)):02X}' for v in p[:3])
    return {'hex': hexv, 'a': p[3] if len(p) > 3 else 1.0, 'dx': float(m.group(2)), 'dy': float(m.group(3)), 'blur': float(m.group(4))}


def add_native_shape(slide, s, idx):
    x, y, w, h = s['x'], s['y'], s['w'], s['h']
    if w < 0.5 or h < 0.5:
        return
    has_fill = s['fill'] and s['fill']['a'] > 0.001
    has_line = s['line'] and s['lineW'] > 0 and s['line']['a'] > 0.001
    if not has_fill and not has_line:
        return
    r = min(s['radius'], min(w, h) / 2)
    geom = 'roundRect' if r > 0.5 else 'rect'
    sp = slide.shapes.add_shape(1, Emu(emu(x)), Emu(emu(y)), Emu(emu(w)), Emu(emu(h)))  # 1 = rectangle
    sp.name = f'Weave shape {idx}'
    spPr = sp._element.spPr
    prst = spPr.find(qn('a:prstGeom'))
    prst.set('prst', geom)
    av = prst.find(qn('a:avLst'))
    if av is None:
        av = etree.SubElement(prst, qn('a:avLst'))
    for g in list(av):
        av.remove(g)
    if geom == 'roundRect':
        etree.SubElement(av, qn('a:gd'), name='adj', fmla=f'val {int(round(r / min(w, h) * 100000))}')
    # 채움
    for tag in ('a:solidFill', 'a:noFill', 'a:gradFill'):
        for e in spPr.findall(qn(tag)):
            spPr.remove(e)
    ln_old = spPr.find(qn('a:ln'))
    if ln_old is not None:
        spPr.remove(ln_old)
    insert_at = list(spPr).index(prst) + 1
    fill_el = etree.Element(qn('a:noFill')) if not has_fill else None
    if has_fill:
        tmp = etree.Element('tmp')
        fill_el = solid_fill(tmp, s['fill']['hex'], s['fill']['a'])
    spPr.insert(insert_at, fill_el)
    ln = etree.Element(qn('a:ln'), w=str(int(round(s['lineW'] * 0.75 * 12700))) if has_line else '0')
    if has_line:
        solid_fill(ln, s['line']['hex'], s['line']['a'])
        if s.get('dash'):
            etree.SubElement(ln, qn('a:prstDash'), val='dash')
    else:
        etree.SubElement(ln, qn('a:noFill'))
    spPr.insert(insert_at + 1, ln)
    sh = parse_shadow(s.get('shadow'))
    if sh and sh['a'] > 0.001:
        eff = etree.Element(qn('a:effectLst'))
        o = etree.SubElement(eff, qn('a:outerShdw'), blurRad=str(emu(sh['blur'])), dist=str(emu(abs(sh['dy']))),
                             dir='5400000', algn='t', rotWithShape='0')
        c = etree.SubElement(o, qn('a:srgbClr'), val=sh['hex'])
        etree.SubElement(c, qn('a:alpha'), val=str(int(round(sh['a'] * 100000))))
        spPr.insert(insert_at + 2, eff)
    # 도형 기본 스타일(테마 색 윤곽·글꼴) 제거
    style = sp._element.find(qn('p:style'))
    if style is not None:
        sp._element.remove(style)
    sp.text_frame.text = ''


def add_textbox(slide, t, idx):
    size_pt = t['size'] * 0.75
    align = {'center': 'ctr', 'right': 'r', 'end': 'r'}.get(t['align'], 'l')
    x, y, w, h = t['x'], t['y'], t['w'], t['h']
    lines = t['lines'] or [[]]
    lh = t['lh']
    if len(lines) == 1:
        # 한 줄 텍스트: 덱의 Presenton 변환과 같이 줄간격을 글자 크기×1.3으로 두고,
        # CSS 줄 상자 안에서 글자가 놓이던 세로 중앙에 맞춰 상자를 옮깁니다.
        tight = t['size'] * 1.3
        y, h, lh = y + (lh - tight) / 2, tight, tight
    lh_pt = lh * 0.75
    if align == 'l':
        w = w + 24  # 줄바꿈 없음 + 좌측 정렬이므로 여유 폭만 추가
    tb = slide.shapes.add_textbox(Emu(emu(x)), Emu(emu(y)), Emu(emu(w)), Emu(emu(h)))
    tb.name = f'Weave text {idx}'
    txBody = tb._element.txBody
    bp = txBody.find(qn('a:bodyPr'))
    for k, v in dict(wrap='none', lIns='0', tIns='0', rIns='0', bIns='0', rtlCol='0', anchor='t').items():
        bp.set(k, v)
    for ch in list(bp):
        bp.remove(ch)
    etree.SubElement(bp, qn('a:noAutofit'))
    if abs(t.get('rot', 0)) > 0.05:
        tb._element.spPr.find(qn('a:xfrm')).set('rot', str(int(round(t['rot'] * 60000))))
    for p in txBody.findall(qn('a:p')):
        txBody.remove(p)
    for line in lines:
        p = etree.SubElement(txBody, qn('a:p'))
        pPr = etree.SubElement(p, qn('a:pPr'), algn=align)
        ls = etree.SubElement(pPr, qn('a:lnSpc'))
        etree.SubElement(ls, qn('a:spcPts'), val=str(int(round(lh_pt * 100))))
        for run in line:
            txt = run['t'].replace(' ', ' ')
            if not txt:
                continue
            fam, bold = font_for(run.get('fam', 'Noto Sans KR'), run.get('b', 400))
            # 위첨자는 크기를 줄이지 않고 baseline만 지정 (PowerPoint·LibreOffice가 자동으로 작게 그림)
            rsz = (t['size'] if run.get('sup') else run.get('sz', t['size'])) * 0.75
            r = etree.SubElement(p, qn('a:r'))
            rPr = etree.SubElement(r, qn('a:rPr'), lang='ko-KR', altLang='en-US', sz=str(int(round(rsz * 100))), dirty='0')
            if bold:
                rPr.set('b', '1')
            if run.get('sup'):
                rPr.set('baseline', '30000')
            if t.get('ls'):
                rPr.set('spc', str(int(round(t['ls'] * 0.75 * 100))))
            c = run.get('c') or {'hex': '1C1A24', 'a': 1}
            solid_fill(rPr, c['hex'], c['a'])
            for tag in ('latin', 'ea', 'cs'):
                etree.SubElement(rPr, qn(f'a:{tag}'), typeface=fam)
            etree.SubElement(r, qn('a:t')).text = txt
        etree.SubElement(p, qn('a:endParaRPr'), lang='ko-KR', altLang='en-US', sz=str(int(round(size_pt * 100))), dirty='0')


def background_xml(deck):
    s11 = deck.slides[10]
    return [copy.deepcopy(sh._element) for sh in list(s11.shapes)[:3]]


def fill_slide(slide, name, bg_elems, notes_text):
    tree = slide.shapes._spTree
    for el in list(tree):
        if el.tag in (qn('p:sp'), qn('p:pic'), qn('p:grpSp'), qn('p:cxnSp'), qn('p:graphicFrame')):
            tree.remove(el)
    for el in bg_elems:
        tree.append(copy.deepcopy(el))
    layout = json.loads((OUT / f'{name}.layout.json').read_text())
    for i, s in enumerate(layout['shapes']):
        add_native_shape(slide, s, i)
    pic = slide.shapes.add_picture(str(OUT / f'{name}.art.png'), 0, 0, Emu(12192000), Emu(6858000))
    pic.name = 'Weave graphics layer (icons, photos, arrows)'
    for i, t in enumerate(layout['texts']):
        add_textbox(slide, t, i)
    # 고유 id 재부여
    for n, el in enumerate(tree.iter(qn('p:cNvPr')), start=2):
        el.set('id', str(n))
    ns = slide.notes_slide
    ns.notes_text_frame.text = notes_text


def drop_slides(prs, keep_idx):
    sldIdLst = prs.slides._sldIdLst
    ids = list(sldIdLst)
    for i, sid in enumerate(ids):
        if i not in keep_idx:
            rId = sid.get(qn('r:id'))
            prs.part.drop_rel(rId)
            sldIdLst.remove(sid)


def main():
    notes = {name: (ROOT / nf).read_text(encoding='utf-8').strip() for name, _, nf in PAGES}

    # (1) 통합.pptx 사본에서 10·18·19번만 교체한 검토본
    review = OUT / '통합_claude0927_반영본.pptx'
    shutil.copyfile(SRC_DECK, review)
    deck = Presentation(review)
    bg = background_xml(deck)
    for name, slide_no, _ in PAGES:
        fill_slide(deck.slides[slide_no - 1], name, bg, notes[name])
    deck.save(review)

    # (2) 새 슬라이드 3장만 담은 파일 (같은 마스터·크기)
    only = OUT / 'weave-claude0927-3slides.pptx'
    shutil.copyfile(review, only)
    prs = Presentation(only)
    drop_slides(prs, keep_idx={slide_no - 1 for _, slide_no, _ in PAGES})
    prs.save(only)
    print('saved', review.name, only.name)


if __name__ == '__main__':
    main()
