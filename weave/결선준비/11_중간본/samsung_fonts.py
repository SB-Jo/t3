"""덱 글꼴을 삼성 글꼴로 바꾸는 후처리 (2026-11-02).

- Inter, Noto Sans KR, 테마·레이아웃의 Calibri·Arial·맑은 고딕을 굵기대로 SamsungOneKorean으로 바꾼다.
  보통 → SamsungOneKorean 400, Medium → 500, SemiBold·Bold → 700.
- 굵게(b=1)인 글은 700으로 바꾸고 굵게를 끈다. 700 글꼴에 PowerPoint가 가짜 굵게를 또 입히지 않게 하려는 것이다.
- SamsungOneKorean에는 한글과 영문·숫자가 함께 들어 있어서, 영문도 같은 글꼴로 쓴다(굵기 셋을 그대로 쓸 수 있음).
- 손글씨(Nanum Pen Script), 로고 글꼴(Samsung Sharp Sans), 이미 삼성 글꼴인 글은 그대로 둔다.
- 글자 폭이 Inter·Noto보다 2~9% 좁아서 원래 자리에 넣어도 넘치지 않는다(06_에셋/글꼴의 파일로 잼).

쓰는 법: remap_prs(prs) → 바꾼 개수(Counter). python-pptx Presentation을 저장하기 전에 부른다.
"""
from collections import Counter

from lxml import etree

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
KO = {400: 'SamsungOneKorean 400', 500: 'SamsungOneKorean 500', 700: 'SamsungOneKorean 700'}
LOGO = 'Samsung Sharp Sans'                     # 'Weave Assist' 글자(인트로 끝 화면과 같은 글꼴)
PEN = 'Nanum Pen Script'
KEEP = {PEN, LOGO, 'SamsungOne 400', *KO.values()}
FACES = ('latin', 'ea', 'cs')
RPR = (A + 'rPr', A + 'defRPr', A + 'endParaRPr')
AFTER = {A + t for t in ('sym', 'hlinkClick', 'hlinkMouseOver', 'rtl', 'extLst')}


def weight(face):
    f = face.lower().replace(' ', '')
    if any(k in f for k in ('semibold', 'bold', 'black', 'heavy')):
        return 700
    if 'medium' in f:
        return 500
    return 400


def _mappable(face):
    return bool(face) and face not in KEEP


def _ensure(rp, tag, face):
    """rPr 안에 latin·ea·cs 하나를 순서(… latin, ea, cs, sym, hlink …)에 맞춰 넣거나 고친다."""
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


def remap_element(root, n):
    for rp in root.iter(*RPR):
        faces = {t: rp.find(A + t) for t in FACES}
        named = {t: e.get('typeface') for t, e in faces.items() if e is not None}
        if any(f in KEEP and not f.startswith('SamsungOneKorean') for f in named.values()):
            n['kept'] += 1                       # 손글씨·로고 글은 굵기까지 그대로
            continue
        bold = rp.get('b') in ('1', 'true')
        if bold:                                 # 굵게 → 700으로, 빠진 글꼴(테마에서 물려받는 것)도 채워 굵기가 안 빠지게
            for t in FACES:
                _ensure(rp, t, KO[700])
            rp.set('b', '0')
            n['bold'] += 1
            continue
        hit = False
        for t, face in named.items():
            if _mappable(face) and not face.startswith('+'):
                faces[t].set('typeface', KO[weight(face)])
                for k in ('panose', 'pitchFamily', 'charset'):
                    faces[t].attrib.pop(k, None)
                hit = True
            elif face.startswith('+'):
                n['theme_ref'] += 1              # 테마 글꼴을 물려받음 → 테마도 바꾸므로 그대로
        n['runs'] += hit
    return n


def remap_theme(root, n):
    for tag, w in (('majorFont', 700), ('minorFont', 400)):
        f = root.find('.//' + A + tag)
        if f is None:
            continue
        for t in ('latin', 'ea'):
            e = f.find(A + t)
            if e is not None:
                e.set('typeface', KO[w])
                for k in ('panose', 'pitchFamily', 'charset'):
                    e.attrib.pop(k, None)
        for e in f.findall(A + 'font'):          # 문자 체계별 글꼴: 한글(Hang)만 맞춤
            if e.get('script') == 'Hang':
                e.set('typeface', KO[w])
        n['theme'] += 1
    return n


def remap_prs(prs, notes=False):
    n = Counter()
    for part in prs.part.package.iter_parts():
        ct = part.content_type
        if ct.endswith('theme+xml'):
            root = etree.fromstring(part.blob)
            remap_theme(root, n)
            part._blob = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        elif hasattr(part, '_element') and (ct.endswith(('slide+xml', 'slideLayout+xml', 'slideMaster+xml', 'chart+xml'))
                                             or (notes and ct.endswith(('notesSlide+xml', 'notesMaster+xml')))):
            remap_element(part._element, n)
    return n


def faces_used(prs):
    """덱에 남은 글꼴 이름 → 개수(확인용)."""
    c = Counter()
    for part in prs.part.package.iter_parts():
        if hasattr(part, '_element') and part.content_type.endswith(('slide+xml', 'slideLayout+xml', 'slideMaster+xml')):
            for e in part._element.iter(*(A + t for t in FACES)):
                c[e.get('typeface')] += 1
    return c
