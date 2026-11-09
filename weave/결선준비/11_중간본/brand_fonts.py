#!/usr/bin/env python3
"""중간본 덱의 글꼴 시안: 한글은 Samsung Korean Sans, 영문·숫자는 Samsung Sharp Sans (2026-11-09).

02_PPT/Weave_결선_중간본.pptx는 그대로 두고 02_PPT/Weave_결선_중간본_SharpSans.pptx를 새로 만든다.
pptx 안의 장·레이아웃·마스터·테마 XML에서 글꼴만 바꾸고, 영상·그림·노트는 바이트 그대로 옮긴다.

- 굵기: SamsungOneKorean 700 → 굵게(b=1) = Korean Sans Bold + Sharp Sans Bold.
        SamsungOneKorean 400·500 → 보통(b=0) = Korean Sans Medium + Sharp Sans Medium.
  Korean Sans는 Medium·Bold 두 굵기뿐이고, Sharp Sans Regular는 Medium 한글 옆에서 너무 가늘어서 보통 글은 Medium끼리 맞춘다.
- PowerPoint는 글자마다 영문 칸(latin)과 한글 칸(ea)의 글꼴을 따로 쓴다. ‘’ “” 같은 기호는 한글 칸 글꼴로 나온다.
- 손글씨(Nanum Pen Script)와 표지 로고(Samsung Sharp Sans)는 그대로 둔다.
- 글꼴 때문에 어긋나는 곳을 고친다: Sharp Sans가 SamsungOne보다 넓어서 옆 글과 붙거나 상자를 넘는 곳(fix_slide),
  원 숫자(①②③)·물결표(~)·따옴표(‘’“”)처럼 두 글꼴 중 한쪽 모양이 어색한 글자(_special_face).
- 글꼴 파일(06_에셋/글꼴/SOURCES.md)은 저장소에 올리지 않는다. PowerPoint용으로 Korean Sans 두 굵기는
  'Samsung Korean Sans' 한 가족(보통 = Medium, 굵게 = Bold)으로, Sharp Sans Medium은 'Samsung Sharp Sans Medium'으로
  이름을 묶어 ~/.cache/weave-tools/fonts에 두고 Windows 사용자 글꼴로 설치했다.

  python brand_fonts.py                  변환 → PowerPoint로 장별 PNG·한눈에
  python brand_fonts.py --no-png
"""
import argparse
import copy
import re
import shutil
import zipfile
from collections import Counter
from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / '02_PPT' / 'Weave_결선_중간본.pptx'
DST = ROOT / '02_PPT' / 'Weave_결선_중간본_SharpSans.pptx'
FONTS = Path.home() / '.cache' / 'weave-tools' / 'fonts'

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
KO = 'Samsung Korean Sans'
EN = {True: 'Samsung Sharp Sans', False: 'Samsung Sharp Sans Medium'}      # 굵게 → Bold 얼굴, 보통 → Medium
CIRCLED = 'SamsungOneKorean 400'                 # 원 숫자만 쓰는 글꼴(_special_face)
KEEP = {'Nanum Pen Script', 'Samsung Sharp Sans'}
FACES = ('latin', 'ea', 'cs')
RPR = (A + 'rPr', A + 'defRPr', A + 'endParaRPr')
AFTER = {A + t for t in ('sym', 'hlinkClick', 'hlinkMouseOver', 'rtl', 'extLst')}
PARTS = re.compile(r'ppt/(slides/slide|slideLayouts/slideLayout|slideMasters/slideMaster)\d+\.xml$')
EMU = 12700                                      # 1pt

# 글 폭 재기(글꼴 파일 = PowerPoint에 설치한 것과 같은 파일)
FILES = {'SamsungOneKorean 400': 'SamsungOneKorean-400.ttf', 'SamsungOneKorean 500': 'SamsungOneKorean-500.ttf',
         'SamsungOneKorean 700': 'SamsungOneKorean-700.ttf', 'Samsung Sharp Sans Medium': 'SamsungSharpSans-Medium.otf',
         ('Samsung Sharp Sans', False): 'SamsungSharpSans-Regular.ttf', ('Samsung Sharp Sans', True): 'SamsungSharpSans-Bold.ttf',
         (KO, False): 'SamsungKoreanSans-Medium.ttf', (KO, True): 'SamsungKoreanSans-Bold.ttf'}
_cache = {}


def _font(face, bold):
    name = FILES.get((face, bold)) or FILES.get(face) or FILES['SamsungOneKorean 400']
    if name not in _cache:
        _cache[name] = ImageFont.truetype(str(FONTS / name), 1000)
    return _cache[name]


def _is_ea(ch):
    o = ord(ch)
    return (0xAC00 <= o <= 0xD7A3 or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F or 0x3000 <= o <= 0x303F
            or 0x2460 <= o <= 0x24FF or 0x2018 <= o <= 0x201D)


def run_width(r):
    """글 조각 하나의 폭(pt): 한글 칸·영문 칸 글꼴을 글자마다 나눠 잰다."""
    rp = r.find(A + 'rPr')
    t = r.findtext(A + 't') or ''
    sz = int(rp.get('sz', 1800)) / 100 if rp is not None else 18.0
    bold = rp is not None and rp.get('b') in ('1', 'true')
    face = {f: (rp.find(A + f).get('typeface') if rp is not None and rp.find(A + f) is not None else None) for f in FACES}
    lat = face['latin'] or 'SamsungOneKorean 400'
    ea = face['ea'] or lat
    spc = int(rp.get('spc', 0)) / 100 if rp is not None else 0
    w, seg, cur = 0.0, '', None
    for ch in t + '\0':
        k = None if ch == '\0' else _is_ea(ch)
        if seg and (ch == '\0' or k != cur):
            w += _font(ea if cur else lat, bold).getlength(seg) * sz / 1000 + spc * len(seg)
            seg = ''
        if ch != '\0':
            seg += ch
            cur = k
    return w


def para_width(p):
    return sum(run_width(r) for r in p.iter(A + 'r'))


def _face(rp, tag, face):
    """rPr 안의 latin·ea·cs 하나를 순서(… latin, ea, cs, sym, hlink …)에 맞춰 넣거나 고친다."""
    e = rp.find(A + tag)
    if e is None:
        e = etree.Element(A + tag)
        later = {A + t for t in FACES[FACES.index(tag) + 1:]} | AFTER
        for i, ch in enumerate(rp):
            if ch.tag in later:
                rp.insert(i, e)
                break
        else:
            rp.append(e)
    e.set('typeface', face)
    for k in ('panose', 'pitchFamily', 'charset'):
        e.attrib.pop(k, None)


SPECIAL = re.compile(r'([\u2460-\u2473]+|~+|[\u2018\u2019\u201c\u201d]+)')


def _special_face(s, bold):
    """따로 떼어 쓸 글자의 글꼴과 굵게 여부.
    ①~⑳: Korean Sans 것은 작고 뒤 글자에 붙어서 SamsungOne 400.
    ~   : Sharp Sans 물결표는 위로 떠서(1~2B가 1˜2B처럼 보임) SamsungOne(굵기 맞춤).
    ‘’“”: Korean Sans 작은따옴표는 아래로 처진 쉼표처럼 작아서 Sharp Sans로."""
    if s[0] == '~':
        return ('SamsungOneKorean 700' if bold else 'SamsungOneKorean 400'), False
    if '\u2460' <= s[0] <= '\u2473':
        return CIRCLED, False
    return EN[bold], bold


def _split_special(r, n):
    rp0 = r.find(A + 'rPr')
    lat = rp0.find(A + 'latin') if rp0 is not None else None
    if lat is None or lat.get('typeface') not in EN.values():
        return                                   # 손글씨·로고 글은 그대로
    t = r.findtext(A + 't') or ''
    parts = [x for x in SPECIAL.split(t) if x]
    if not any(SPECIAL.fullmatch(x) for x in parts):
        return
    bold = rp0.get('b') == '1'
    tpl, prev = copy.deepcopy(r), r
    for x in parts:
        nr = copy.deepcopy(tpl)
        nr.find(A + 't').text = x
        if SPECIAL.fullmatch(x):
            face, b = _special_face(x, bold)
            rp = nr.find(A + 'rPr')
            for f in FACES:
                _face(rp, f, face)
            rp.set('b', '1' if b else '0')
            n['special ' + x[0]] += 1
        prev.addnext(nr)
        prev = nr
    r.getparent().remove(r)


def remap(root, n):
    for rp in root.iter(*RPR):
        named = {t: rp.find(A + t).get('typeface') for t in FACES if rp.find(A + t) is not None}
        if not named:
            n['inherit'] += 1                    # 테마 글꼴을 물려받음 → 테마를 바꿈
            continue
        if any(f in KEEP for f in named.values()):
            n['kept'] += 1
            continue
        if not any(f.startswith('SamsungOne') for f in named.values()):
            n['other'] += 1
            continue
        bold = any(f.endswith('700') for f in named.values()) or rp.get('b') in ('1', 'true')
        _face(rp, 'latin', EN[bold])
        _face(rp, 'ea', KO)
        _face(rp, 'cs', EN[bold])
        rp.set('b', '1' if bold else '0')
        n['bold' if bold else 'regular'] += 1
    for r in list(root.iter(A + 'r')):
        _split_special(r, n)


def remap_theme(root, n):
    for tag in ('majorFont', 'minorFont'):
        f = root.find('.//' + A + tag)
        if f is None:
            continue
        for t, face in (('latin', EN[False]), ('ea', KO)):
            e = f.find(A + t)
            if e is not None:
                e.set('typeface', face)
                for k in ('panose', 'pitchFamily', 'charset'):
                    e.attrib.pop(k, None)
        for e in f.findall(A + 'font'):
            if e.get('script') == 'Hang':
                e.set('typeface', KO)
        n['theme'] += 1


# ---- 글꼴 때문에 어긋나는 곳 고치기 ---------------------------------------------------------------

def _shapes(root):
    """이름 → p:sp (같은 이름이 여럿이면 처음 것)."""
    out = {}
    for sp in root.iter(P + 'sp'):
        out.setdefault(sp.find(P + 'nvSpPr/' + P + 'cNvPr').get('name'), sp)
    return out


def _by_text(root, text):
    return [sp for sp in root.iter(P + 'sp') if ''.join(sp.itertext()).strip() == text]


def _off(sp):
    return sp.find(P + 'spPr/' + A + 'xfrm/' + A + 'off')


def _ext(sp):
    return sp.find(P + 'spPr/' + A + 'xfrm/' + A + 'ext')


def _move(sp, dx):
    o = _off(sp)
    o.set('x', str(int(round(int(o.get('x')) + dx * EMU))))


def _width(sp):
    return max((para_width(p) for p in sp.iter(A + 'p')), default=0)


def _fit(old_sp, new_sp, n, why):
    """한 줄 글이 원래 폭을 넘으면 글자 크기를 줄여 원래 폭에 맞춘다."""
    wo, wn = _width(old_sp), _width(new_sp)
    if wn > wo + 0.3:
        k = wo / wn
        for rp in new_sp.iter(A + 'rPr', A + 'endParaRPr'):
            if rp.get('sz'):
                rp.set('sz', str(int(int(rp.get('sz')) * k)))
        n[why] += 1


def fix_slide(old, new, n):
    so, sn = _shapes(old), _shapes(new)
    # HIW: 'Query Rewriting' 제목 옆 '질의 분해·재작성'
    if '!!qp.head/title' in sn and '!!qp.head/ko' in sn:
        d = _width(sn['!!qp.head/title']) - _width(so['!!qp.head/title'])
        if d > 0.3:
            _move(sn['!!qp.head/ko'], d)
            n['qp.head'] += 1
    # Appendix 추론 유형: 영문 이름 옆 한글 설명
    for en, ko in (('Analytical', '분석 추론'), ('Numerical', '수치 추론'), ('Deductive', '규칙 적용'),
                   ('Analogical', '유사 사례'), ('Causal', '원인 추적')):
        a_new, b_new, a_old = _by_text(new, en), _by_text(new, ko), _by_text(old, en)
        if len(a_new) == 1 and len(b_new) == 1 and len(a_old) == 1:
            d = _width(a_new[0]) - _width(a_old[0])
            if d > 0.3:
                _move(b_new[0], d)
                n['type label'] += 1
    # Why Samsung: 'Personal Data Engine'이 두 줄로 꺾임 → 상자를 넓힘
    for sp in _by_text(new, 'Personal Data Engine'):
        bp = sp.find('.//' + A + 'bodyPr')
        need = _width(sp) + (int(bp.get('lIns', 91440)) + int(bp.get('rIns', 91440))) / EMU + 3
        e = _ext(sp)
        if int(e.get('cx')) / EMU < need:
            e.set('cx', str(int(need * EMU)))
            n['widen'] += 1
    # Appendix 파이프라인 카드 머리 '질문 다시 쓰기' 옆 'Query Rewriting', 15쪽 와인 라벨 알약: 끝에 닿아 원래 폭에 맞춤
    if _by_text(new, '질문 다시 쓰기'):
        for o, s in zip(_by_text(old, 'Query Rewriting'), _by_text(new, 'Query Rewriting')):
            _fit(o, s, n, 'fit label')
    if '!!pl2.wine/t' in sn:
        _fit(so['!!pl2.wine/t'], sn['!!pl2.wine/t'], n, 'fit label')
    # 표지 팀 이름: 넓어진 'Samsung Research'에 맞춰 밑줄 길이와 팀 간격을 다시 잼
    if '!!cover/line0' in sn:
        shift = 0.0
        for k in range(3):
            if '!!cover/line%d' % k not in sn:
                break
            parts = [nm for nm in sn if re.fullmatch(r'!!cover/(n%d\d|line%d|dept%d|team%d)' % (k, k, k, k), nm)]
            for nm in parts:
                _move(sn[nm], shift)
            names = sorted(nm for nm in parts if re.fullmatch(r'!!cover/n%d\d' % k, nm))
            x0 = int(_off(sn[names[0]]).get('x')) / EMU
            nx = x0
            for nm in names:                     # 이름: 원래 간격(14px = 10.5pt)으로 다시 늘어놓음
                o = _off(sn[nm])
                o.set('x', str(int(nx * EMU)))
                nx += _width(sn[nm]) + 10.5
            names_w = nx - 10.5 - x0
            gw_old = int(_ext(so['!!cover/line%d' % k]).get('cx')) / EMU
            gw = max(names_w, _width(sn['!!cover/dept%d' % k]), _width(sn['!!cover/team%d' % k]))
            _ext(sn['!!cover/line%d' % k]).set('cx', str(int(gw * EMU)))
            for t in ('dept', 'team'):
                _ext(sn['!!cover/%s%d' % (t, k)]).set('cx', str(int((gw + 9) * EMU)))
            shift += gw - gw_old
        n['cover team'] += 1


def convert(src, dst):
    n = Counter()
    tmp = dst.with_suffix('.tmp')
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(tmp, 'w') as zo:
        for info in zi.infolist():
            data = zi.read(info.filename)
            if re.match(r'ppt/theme/theme\d+\.xml$', info.filename):
                root = etree.fromstring(data)
                remap_theme(root, n)
                data = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
            elif PARTS.match(info.filename):
                old = etree.fromstring(data)
                root = etree.fromstring(data)
                remap(root, n)
                if info.filename.startswith('ppt/slides/'):
                    fix_slide(old, root, n)
                data = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
            zo.writestr(info, data, compress_type=info.compress_type)
    shutil.move(tmp, dst)
    return n


def sheet(pngs, dst, n_main=24, n_apx=9, cols=6, w=400):
    """한눈에(build_deck.py와 같은 배치)."""
    ims = [Image.open(p).convert('RGB') for p in pngs]
    h = int(w * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new('RGB', (cols * (w + 10) + 10, rows * (h + 30) + 10), 'white')
    d = ImageDraw.Draw(out)
    fnt = ImageFont.truetype(str(ROOT / '06_에셋' / '글꼴' / 'NotoSansKR-700.ttf'), 14)
    for i, im in enumerate(ims):
        x, y = 10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 30)
        out.paste(im.resize((w, h), Image.LANCZOS), (x, y + 20))
        part = '본편' if i < n_main else ('부록' if i < n_main + n_apx else '참고')
        d.text((x, y), '%d  %s' % (i + 1, part), fill=(60, 50, 90), font=fnt)
    out.save(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-png', action='store_true')
    a = ap.parse_args()
    n = convert(SRC, DST)
    print('글꼴 바꿈', dict(n), '→', DST)
    if not a.no_png:
        import sys
        sys.path.insert(0, str(ROOT / '09_HowItWorks' / 'Claude'))
        import render_c                          # noqa: E402  PowerPoint 잠금(/tmp/weave-ppt.lock)을 스스로 잡음
        od = HERE / 'png_SharpSans'
        for _ in range(6):                       # WSL에서 PowerPoint 호출이 가끔 'Invalid argument'로 실패함
            try:
                render_c.png(DST, od, 1600, 900)
                break
            except AssertionError as e:
                print('   다시 시도:', str(e)[-80:])
        sheet(sorted(od.glob('s*.png')), HERE / '한눈에_SharpSans.png')
        print('PNG →', od)


if __name__ == '__main__':
    main()
