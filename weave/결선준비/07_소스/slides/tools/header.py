"""0927_v1 덱 공통 머리(칩 · 제목 · 부제).

규격 (1280×720 px, 2차 요청 반영: 칩을 작게·얇게, 칩과 제목 사이를 넓게)
- 칩: 진한 보라(#6B4EFF) 알약 + 흰 글자, 높이 26px, 좌우 여백 14px, 가운데 정렬, y=28
      영문·숫자 Inter SemiBold 11pt(자간 +0.5pt), 한글 Noto Sans KR SemiBold 11pt(자간 0)
- 제목: 29pt Bold, 기본색 #1C1A24(강조색은 장표별 그대로), 자간 -0.5pt, 상자 x=0 w=1280 y=68 h=50
- 부제: 14pt Regular #5B5866(11~13 기대효과의 단계 표시는 색 그대로), 상자 x=0 w=1280 y=124 h=26
- 글자는 영문·숫자 조각과 한글 조각으로 나눠 씀
  영문 조각: lang=en-US, latin=ea=cs=Inter 계열 → PowerPoint 글꼴 상자에도 Inter로 보임
  한글 조각: lang=ko-KR, latin=Inter 계열, ea=cs=Noto Sans KR 계열
"""
import re

from lxml import etree
from pptx.oxml.ns import qn

from textmeasure import width

PX = 9525
CHIP = dict(y=28, h=26, pad=14, pad_ko=18, pt=11, spc_latin=50, fill='6B4EFF', latin='Inter SemiBold', ea='Noto Sans KR SemiBold', weight=600)
TITLE = dict(y=68, h=50, pt=29, spc=-50, lnspc=3480, color='1C1A24')
SUB = dict(y=124, h=26, pt=14, lnspc=1690, color='5B5866')
LABEL_RE = re.compile(r'^\s*\d{1,2}\s*/\s*(.+?)\s*$')
GRAYS = ('5B5866', '8E88A0', '6A6474', '4E4A57')
BASE_INKS = ('000000', '15151C', '1C1A24', '2B2640')


def emu(v):
    return str(int(round(v * PX)))


# ------------------------------------------------------------------ 글자 조각
def char_class(ch):
    o = ord(ch)
    if 0xAC00 <= o <= 0xD7A3 or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF:
        return 'ko'
    if ch.isalnum():
        return 'latin'
    return None          # 공백·기호: 앞 조각에 붙임(맨 앞이면 뒤 조각에)


def split_script(text, default='latin'):
    """[(조각, 'latin'|'ko')]. 기호·공백만 있는 글자는 default(앞 조각의 종류)를 따름."""
    out, cur, cls, pending = [], '', None, ''
    for ch in text:
        c = char_class(ch)
        if c is None:
            if cls is None:
                pending += ch
            else:
                cur += ch
            continue
        if cls is None:
            cls, cur = c, pending + ch
            pending = ''
        elif c == cls:
            cur += ch
        else:
            out.append((cur, cls))
            cls, cur = c, ch
    if cls is None:
        return [(pending, default)] if pending else []
    out.append((cur + pending, cls))
    return out


# ------------------------------------------------------------------ 도형
def set_xfrm(sp, x, y, w, h):
    spPr = sp.find(qn('p:spPr'))
    xfrm = spPr.find(qn('a:xfrm'))
    if xfrm is None:
        xfrm = etree.Element(qn('a:xfrm'))
        spPr.insert(0, xfrm)
    for ch in list(xfrm):
        xfrm.remove(ch)
    for k in ('rot', 'flipH', 'flipV'):
        xfrm.attrib.pop(k, None)
    etree.SubElement(xfrm, qn('a:off'), x=emu(x), y=emu(y))
    etree.SubElement(xfrm, qn('a:ext'), cx=emu(w), cy=emu(h))


def set_geom(sp, prst, fill=None):
    spPr = sp.find(qn('p:spPr'))
    for tag in ('a:prstGeom', 'a:custGeom', 'a:noFill', 'a:solidFill', 'a:gradFill', 'a:pattFill', 'a:blipFill', 'a:ln', 'a:effectLst'):
        for el in spPr.findall(qn(tag)):
            spPr.remove(el)
    g = etree.SubElement(spPr, qn('a:prstGeom'), prst=prst)
    av = etree.SubElement(g, qn('a:avLst'))
    if prst == 'roundRect':
        etree.SubElement(av, qn('a:gd'), name='adj', fmla='val 50000')
    if fill:
        sf = etree.SubElement(spPr, qn('a:solidFill'))
        etree.SubElement(sf, qn('a:srgbClr'), val=fill)
    else:
        etree.SubElement(spPr, qn('a:noFill'))
    ln = etree.SubElement(spPr, qn('a:ln'))
    etree.SubElement(ln, qn('a:noFill'))


def body(sp, anchor):
    txBody = sp.find(qn('p:txBody'))
    bp = txBody.find(qn('a:bodyPr'))
    for k in list(bp.attrib):
        del bp.attrib[k]
    for k, v in dict(wrap='none', lIns='0', tIns='0', rIns='0', bIns='0', rtlCol='0', anchor=anchor, anchorCtr='0').items():
        bp.set(k, v)
    for ch in list(bp):
        bp.remove(ch)
    etree.SubElement(bp, qn('a:noAutofit'))
    return txBody


def make_rpr(tag, pt, color, bold, spc, cls, faces):
    """faces = (latin, ea_for_ko). 영문 조각은 ea·cs도 latin 글꼴로."""
    latin, ea = faces
    lang = 'en-US' if cls == 'latin' else 'ko-KR'
    rPr = etree.Element(qn(tag), lang=lang, sz=str(int(round(pt * 100))), b='1' if bold else '0', i='0', spc=str(spc), dirty='0')
    if cls != 'latin':
        rPr.set('altLang', 'en-US')
    sf = etree.SubElement(rPr, qn('a:solidFill'))
    etree.SubElement(sf, qn('a:srgbClr'), val=color)
    etree.SubElement(rPr, qn('a:latin'), typeface=latin)
    etree.SubElement(rPr, qn('a:ea'), typeface=latin if cls == 'latin' else ea)
    etree.SubElement(rPr, qn('a:cs'), typeface=latin if cls == 'latin' else ea)
    return rPr


def write_paragraphs(txBody, paras, pt, lnspc, faces, spc_of):
    """paras: [[(text, color, bold), ...], ...]. 조각마다 글꼴·언어를 나눠 씀."""
    for p in txBody.findall(qn('a:p')):
        txBody.remove(p)
    for runs in paras:
        p = etree.SubElement(txBody, qn('a:p'))
        pPr = etree.SubElement(p, qn('a:pPr'), algn='ctr')
        ls = etree.SubElement(pPr, qn('a:lnSpc'))
        if lnspc:
            etree.SubElement(ls, qn('a:spcPts'), val=str(lnspc))
        else:
            etree.SubElement(ls, qn('a:spcPct'), val='100000')
        for tag in ('a:spcBef', 'a:spcAft'):
            s = etree.SubElement(pPr, qn(tag))
            etree.SubElement(s, qn('a:spcPts'), val='0')
        etree.SubElement(pPr, qn('a:buNone'))
        last, prev = None, 'latin'
        for text, color, bold in runs:
            for seg, cls in split_script(text, prev):
                prev = cls
                r = etree.SubElement(p, qn('a:r'))
                last = (color, bold, cls)
                r.append(make_rpr('a:rPr', pt, color, bold, spc_of(cls), cls, faces))
                etree.SubElement(r, qn('a:t')).text = seg
        color, bold, cls = last
        p.append(make_rpr('a:endParaRPr', pt, color, bold, spc_of(cls), cls, faces))


def run_color(r):
    rPr = r.find(qn('a:rPr'))
    if rPr is not None:
        c = rPr.find(qn('a:solidFill') + '/' + qn('a:srgbClr'))
        if c is not None:
            return c.get('val').upper()
    return None


def collect_runs(sh):
    """단락별 [(text, color, bold)]. 빈 단락은 버림, 줄바꿈(a:br)은 단락 경계로. 이웃한 같은 서식 조각은 합침."""
    paras = []
    for p in sh.text_frame._txBody.findall(qn('a:p')):
        cur = []
        for el in p:
            if el.tag == qn('a:r'):
                t = el.find(qn('a:t')).text or ''
                rPr = el.find(qn('a:rPr'))
                b = rPr is not None and rPr.get('b') == '1'
                c = run_color(el)
                if t:
                    if cur and cur[-1][1] == c and cur[-1][2] == b:
                        cur[-1] = (cur[-1][0] + t, c, b)
                    else:
                        cur.append((t, c, b))
            elif el.tag == qn('a:br'):
                paras.append(cur); cur = []
        paras.append(cur)
    paras = [pp for pp in paras if ''.join(t for t, _, _ in pp).strip()]
    for pp in paras:
        t, c, b = pp[0]; pp[0] = (t.lstrip(), c, b)
        t, c, b = pp[-1]; pp[-1] = (t.rstrip(), c, b)
    return paras


# ------------------------------------------------------------------ 찾기
def top_px(sh):
    return sh.top / PX if sh.top is not None else 9999


def max_pt(sh):
    sizes = [r.font.size.pt for p in sh.text_frame.paragraphs for r in p.runs if r.font.size]
    return max(sizes) if sizes else 0


def find_header(slide):
    """(chip, title, subtitle) — 이미 통일된 장표는 이름으로, 처음이면 번호 라벨로 찾음."""
    named = {sh.name: sh for sh in slide.shapes if sh.name in ('Header chip', 'Header title', 'Header subtitle')}
    if 'Header chip' in named:
        return named.get('Header chip'), named.get('Header title'), named.get('Header subtitle')
    texts = [sh for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    label = [sh for sh in texts if LABEL_RE.match(sh.text_frame.text.strip()) and top_px(sh) < 80]
    if len(label) != 1:
        return None, None, None
    label = label[0]
    titles = [sh for sh in texts if sh is not label and 55 <= top_px(sh) <= 95 and max_pt(sh) >= 25]
    assert len(titles) == 1, [t.text_frame.text for t in titles]
    subs = [sh for sh in texts if sh not in (label, titles[0]) and 110 <= top_px(sh) <= 140 and 12.5 <= max_pt(sh) <= 15.5
            and abs((sh.left + sh.width / 2) / PX - 640) < 80]
    assert len(subs) <= 1
    return label, titles[0], (subs[0] if subs else None)


# ------------------------------------------------------------------ 적용
def chip_width(text):
    """칩 폭. 조각별로 실제 글꼴(영문 Inter, 한글 Noto Sans KR)로 잼.
    한글은 글자 양옆 여백이 거의 없어 좌우 여백을 4px 더 줌(보이는 여백을 영문 칩과 맞춤)."""
    px = CHIP['pt'] * 4 / 3
    w, has_ko = 0.0, False
    for seg, cls in split_script(text):
        if cls == 'latin':
            w += width(seg, px, CHIP['weight'], CHIP['spc_latin'] / 100 * 4 / 3, family='inter')
        else:
            has_ko = True
            w += width(seg, px, CHIP['weight'], 0.0, family='noto')
    return w + 2 * (CHIP['pad_ko'] if has_ko else CHIP['pad'])


def style_chip(sh, text):
    w = round(chip_width(text))
    sp = sh._element
    set_xfrm(sp, 640 - w / 2, CHIP['y'], w, CHIP['h'])
    set_geom(sp, 'roundRect', CHIP['fill'])
    tx = body(sp, 'ctr')
    write_paragraphs(tx, [[(text, 'FFFFFF', False)]], CHIP['pt'], None, (CHIP['latin'], CHIP['ea']),
                     lambda cls: CHIP['spc_latin'] if cls == 'latin' else 0)
    sh.name = 'Header chip'
    return w


def style_title(sh, runs=None):
    """runs: [(text, color|None)] 주면 문구를 바꿈. None이면 지금 문구를 유지."""
    if runs is None:
        paras = collect_runs(sh)
        assert len(paras) == 1, paras
        runs = [(t, c) for t, c, _ in paras[0]]
    new = [(t, c if (c and c not in BASE_INKS) else TITLE['color'], True) for t, c in runs]
    sp = sh._element
    set_xfrm(sp, 0, TITLE['y'], 1280, TITLE['h'])
    set_geom(sp, 'rect')
    tx = body(sp, 't')
    write_paragraphs(tx, [new], TITLE['pt'], TITLE['lnspc'], ('Inter', 'Noto Sans KR'), lambda cls: TITLE['spc'])
    sh.name = 'Header title'
    return ''.join(t for t, _, _ in new)


def style_sub(sh, runs=None, keep_colors=False):
    """runs: [(text, color|None, bold)] 주면 문구를 바꿈(한 단락)."""
    paras = [runs] if runs is not None else collect_runs(sh)
    new = []
    for pp in paras:
        row = []
        for t, c, b in pp:
            if keep_colors:
                col = c or SUB['color']
            else:
                col = c if (c and c not in GRAYS) else SUB['color']
            row.append((t, col, b))
        new.append(row)
    sp = sh._element
    set_xfrm(sp, 0, SUB['y'], 1280, SUB['h'] * len(new))
    set_geom(sp, 'rect')
    tx = body(sp, 't')
    write_paragraphs(tx, new, SUB['pt'], SUB['lnspc'], ('Inter', 'Noto Sans KR'), lambda cls: 0)
    sh.name = 'Header subtitle'
    return ' / '.join(''.join(t for t, _, _ in pp) for pp in new)


def apply(slide, chip_text=None, title_runs=None, sub_runs=None, keep_sub_colors=False):
    chip, title, sub = find_header(slide)
    if chip is None:
        return None
    if chip_text is None:
        cur = chip.text_frame.text.strip()
        m = LABEL_RE.match(cur)
        chip_text = m.group(1) if m else cur
    out = {'chip': chip_text, 'chip_w': style_chip(chip, chip_text)}
    if title is not None:
        out['title'] = style_title(title, title_runs)
    if sub is not None:
        out['sub'] = style_sub(sub, sub_runs, keep_sub_colors)
    return out
