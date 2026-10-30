"""0927_v1 덱 2~4쪽 개별 수정 (사용자 요청 2026-09-27 19시).

2쪽  만화 그림을 터치 효과(보라 선) 넣은 판으로 교체 — comic/out/overview-comic.png
3쪽  제목 문구, 커서 위치, '사라진 건 아니니' 강조 타원, 하단 문구('내 기억' 보라)
4쪽  부제 강조, 01~03 보조 문구, 오른쪽 상자 폭 10% 축소(+메일 아이콘, 검색어), 페르소나 이름 표기·인용, 인물 그림 교체
"""
import copy
import io
import math

from lxml import etree
from PIL import Image
from pptx.oxml import parse_xml
from pptx.oxml.ns import qn

from inspect_slide import abs_boxes

PX = 9525
P3_HL = '6666FF'   # 3·4쪽 강조색(제목 강조와 같은 색)


def emu(v):
    return int(round(v * PX))


def shape_by_id(slide, sid):
    hits = [sh for sh, _ in abs_boxes(slide.shapes) if sh.shape_id == sid]
    assert len(hits) == 1, (sid, len(hits))
    return hits[0]


def xfrm(sh):
    el = sh._element
    sp = el.find(qn('p:spPr'))
    return sp.find(qn('a:xfrm'))


def move_abs(sh, x=None, y=None, w=None, h=None):
    """최상위(그룹 밖) 도형 전용: 절대 px 좌표 지정."""
    xf = xfrm(sh)
    off, ext = xf.find(qn('a:off')), xf.find(qn('a:ext'))
    if x is not None: off.set('x', str(emu(x)))
    if y is not None: off.set('y', str(emu(y)))
    if w is not None: ext.set('cx', str(emu(w)))
    if h is not None: ext.set('cy', str(emu(h)))


def shift(sh, dx=0.0, dy=0.0):
    xf = xfrm(sh)
    off = xf.find(qn('a:off'))
    off.set('x', str(int(off.get('x')) + emu(dx)))
    off.set('y', str(int(off.get('y')) + emu(dy)))


def pos(sh):
    xf = xfrm(sh)
    off, ext = xf.find(qn('a:off')), xf.find(qn('a:ext'))
    return int(off.get('x')) / PX, int(off.get('y')) / PX, int(ext.get('cx')) / PX, int(ext.get('cy')) / PX


def set_runs(sh, runs, para=0, inter=True):
    """para번째 단락의 글자를 runs=[(text, color|None), ...]로 바꿈. 첫 글자의 서식을 틀로 씀."""
    txBody = sh._element.find(qn('p:txBody'))
    p = txBody.findall(qn('a:p'))[para]
    old = p.findall(qn('a:r'))
    tmpl = copy.deepcopy(old[0].find(qn('a:rPr')))
    for r in old:
        p.remove(r)
    for br in p.findall(qn('a:br')):
        p.remove(br)
    end = p.find(qn('a:endParaRPr'))
    for text, color in runs:
        r = etree.Element(qn('a:r'))
        rPr = copy.deepcopy(tmpl)
        rPr.attrib.pop('err', None)
        if color:
            for sf in rPr.findall(qn('a:solidFill')):
                rPr.remove(sf)
            sf = etree.Element(qn('a:solidFill'))
            etree.SubElement(sf, qn('a:srgbClr'), val=color)
            # solidFill은 ln 다음, latin 앞
            anchor = rPr.find(qn('a:ln'))
            if anchor is not None:
                anchor.addnext(sf)
            else:
                rPr.insert(0, sf)
        if inter:
            lat = rPr.find(qn('a:latin'))
            if lat is None:
                lat = etree.Element(qn('a:latin'))
                nxt = rPr.find(qn('a:ea')) if rPr.find(qn('a:ea')) is not None else rPr.find(qn('a:cs'))
                if nxt is not None:
                    nxt.addprevious(lat)
                else:
                    rPr.append(lat)
            for k in list(lat.attrib):
                del lat.attrib[k]
            lat.set('typeface', 'Inter')
        r.append(rPr)
        etree.SubElement(r, qn('a:t')).text = text
        if end is not None:
            end.addprevious(r)
        else:
            p.append(r)


def wrap_none(sh):
    bp = sh._element.find(qn('p:txBody')).find(qn('a:bodyPr'))
    bp.set('wrap', 'none')


def replace_picture(slide, pic, png_bytes, crop_zero=True):
    """그림 도형의 이미지를 바꾸고, 더 이상 안 쓰는 이전 그림 관계는 호출 쪽에서 정리."""
    image_part, rId = slide.part.get_or_add_image_part(io.BytesIO(png_bytes))
    blip = pic._element.find('.//' + qn('a:blip'))
    old = blip.get(qn('r:embed'))
    blip.set(qn('r:embed'), rId)
    if crop_zero:
        src = pic._element.find('.//' + qn('a:srcRect'))
        if src is not None:
            for k in ('l', 't', 'r', 'b'):
                src.attrib.pop(k, None)
    return old


def drop_unused_images(slide):
    xml = etree.tostring(slide._element).decode()
    dropped = []
    for rId, rel in list(slide.part.rels.items()):
        if rel.reltype.endswith('/image') and f'"{rId}"' not in xml:
            slide.part.drop_rel(rId)
            dropped.append(rId)
    return dropped


# ---------------------------------------------------------------- 2쪽
def edit_p2(slide, comic_png_path):
    pics = [sh for sh in slide.shapes if sh.shape_type == 13]
    assert len(pics) == 1 and pics[0].image.size == (3600, 2560)
    replace_picture(slide, pics[0], open(comic_png_path, 'rb').read(), crop_zero=False)
    return drop_unused_images(slide)


# ---------------------------------------------------------------- 3쪽
def edit_p3(slide, title_shape):
    set_runs(title_shape, [('분명 기록해 뒀는데, ', None), ('찾을 수 없는 기억', P3_HL)])
    # 커서: '어제 간 이자카야 집 이름' 글자 끝 바로 옆 (글자 폭 186.3px, Noto Sans KR SemiBold 14pt 자간 -0.2pt)
    q = shape_by_id(slide, 330)
    assert q.text_frame.text == '어제 간 이자카야 집 이름'
    qx = pos(q)[0]
    cur = shape_by_id(slide, 331)
    move_abs(cur, x=qx + 186.3 + 3.0)
    # 강조 타원: '사라진 건 아니니'(x≈876~1023, 글자 세로 가운데 y≈567)를 덮도록
    ell = shape_by_id(slide, 151)
    assert ell.name == 'Ground shadow'
    move_abs(ell, x=866, y=557.5, w=166, h=20)
    # 하단 문구
    bottom = shape_by_id(slide, 148)
    assert bottom.text_frame.text.startswith('세상 모든 지식은')
    set_runs(bottom, [('세상 모든 지식은 AI에게 묻는데, 정작 ', None), ('내 기억', P3_HL), ('은 아직도 찾아 헤매곤 합니다.', None)])


# ---------------------------------------------------------------- 4쪽
MAIL_TILE = ('E3F4F0', 'B7E1D6')   # 민트 (노트 파랑·톡 노랑·갤러리 보라와 구별)
MAIL_INK = '2F6F63'


def fresh_id(el):
    """복제한 도형에 장표 안에서 겹치지 않는 id를 줌."""
    tree = el.getroottree().getroot()
    used = {int(c.get('id')) for c in tree.iter(qn('p:cNvPr')) if c.get('id', '').isdigit()}
    el.find('.//' + qn('p:cNvPr')).set('id', str(max(used) + 1))


def clone_after(anchor, el):
    new = copy.deepcopy(el)
    anchor.addnext(new)
    fresh_id(new)
    return new


def recolor_grad(sp_el, c0, c1):
    gs = sp_el.find(qn('p:spPr')).find(qn('a:gradFill')).find(qn('a:gsLst')).findall(qn('a:gs'))
    gs[0][0].set('val', c0)
    gs[-1][0].set('val', c1)


def set_off(el, x, y):
    off = el.find(qn('p:spPr')).find(qn('a:xfrm')).find(qn('a:off'))
    off.set('x', str(emu(x)))
    off.set('y', str(emu(y)))


def add_mail_icon(slide, x, y):
    """갤러리 아이콘(1015~1021)을 틀로 메일 아이콘을 만듦. (x, y) = 타일 왼쪽 위(px)."""
    tile, frame, badge, l1, l2 = (shape_by_id(slide, i)._element for i in (1015, 1016, 1019, 1020, 1021))
    anchor = shape_by_id(slide, 1021)._element
    gx, gy = pos(shape_by_id(slide, 1015))[:2]

    def place(el, src_sid, name):
        sx, sy = pos(shape_by_id(slide, src_sid))[:2]
        set_off(el, x + (sx - gx), y + (sy - gy))
        el.find('.//' + qn('p:cNvPr')).set('name', name)

    t = clone_after(anchor, tile); place(t, 1015, 'Mail tile'); recolor_grad(t, *MAIL_TILE)
    # 봉투 몸통: 갤러리 액자와 같은 크기·선 두께, 색만 변경
    f = clone_after(t, frame); place(f, 1016, 'Mail envelope')
    f.find(qn('p:spPr')).find(qn('a:ln')).find(qn('a:solidFill'))[0].set('val', MAIL_INK)
    # 봉투 덮개(V): 몸통 위쪽 모서리 → 가운데
    fx, fy, fw, fh = pos(shape_by_id(slide, 1016))
    fx, fy = x + (fx - gx), y + (fy - gy)
    flap = parse_xml(
        f'<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        f'<p:nvSpPr><p:cNvPr id="0" name="Mail flap"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{emu(fx + 1.2)}" y="{emu(fy + 1.4)}"/><a:ext cx="{emu(fw - 2.4)}" cy="{emu(fh * 0.5)}"/></a:xfrm>'
        f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
        f'<a:pathLst><a:path w="1000" h="1000" fill="none"><a:moveTo><a:pt x="0" y="0"/></a:moveTo><a:lnTo><a:pt x="500" y="1000"/></a:lnTo><a:lnTo><a:pt x="1000" y="0"/></a:lnTo></a:path></a:pathLst></a:custGeom>'
        f'<a:noFill/><a:ln w="12700" cap="rnd"><a:solidFill><a:srgbClr val="{MAIL_INK}"/></a:solidFill><a:round/></a:ln></p:spPr></p:sp>')
    f.addnext(flap)
    fresh_id(flap)
    b = clone_after(flap, badge); place(b, 1019, 'Mail badge')
    m1 = clone_after(b, l1); place(m1, 1020, 'Mail badge x')
    m2 = clone_after(m1, l2); place(m2, 1021, 'Mail badge x')


def add_query_text(slide, bar, x, text, template_tb):
    """검색창 안 입력 문구. 캡션(1022) 서식을 틀로 씀."""
    el = copy.deepcopy(template_tb._element)
    el.find('.//' + qn('p:cNvPr')).set('name', 'Search query')
    bx, by, bw, bh = pos(bar)
    h = 16.8
    xf = el.find(qn('p:spPr')).find(qn('a:xfrm'))
    xf.find(qn('a:off')).set('x', str(emu(x)))
    xf.find(qn('a:off')).set('y', str(emu(by + (bh - h) / 2)))
    xf.find(qn('a:ext')).set('cx', str(emu(bx + bw - x - 8)))
    xf.find(qn('a:ext')).set('cy', str(emu(h)))
    el.find(qn('p:txBody')).find(qn('a:bodyPr')).set('anchor', 'ctr')
    r = el.find('.//' + qn('a:r'))
    r.find(qn('a:t')).text = text
    r.find(qn('a:rPr')).find(qn('a:solidFill'))[0].set('val', '4A4A5A')
    r.find(qn('a:rPr')).find(qn('a:latin')).set('typeface', 'Inter')
    bar._element.addnext(el)
    fresh_id(el)
    return el


def portrait_png(path, crop, mirror=False, height=640):
    im = Image.open(path).convert('RGBA').crop(crop)
    if mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.getvalue()


def edit_p4(slide, sub_shape, sungbin_png, jihyun_png):
    from textmeasure import width
    # 부제 강조
    set_runs(sub_shape, [('어디', P3_HL), ('에 있는지, ', None), ('무엇', P3_HL), ('이 있는지, ', None),
                         ('기억이 있었다는 사실', P3_HL), ('까지', None)])
    # 보조 문구
    for sid, old_start, new in [(222, '노트', '노트, 메일, 대화내역을 하나씩 확인합니다.'),
                                (254, '일정에서', '일정에서 날짜를 찾고, 갤러리에서 사진을 확인하고, 검색어를 다시 입력합니다.'),
                                (290, '스쳐', '스쳐 간 부탁과 작은 약속들, 기록해 두고도 잊어버리곤 합니다.')]:
        sh = shape_by_id(slide, sid)
        assert sh.text_frame.text.startswith(old_start), sh.text_frame.text
        set_runs(sh, [(new, None)])
        wrap_none(sh)
    # 페르소나
    for sid, old, new in [(306, '성빈', '성빈 · 28세 신입사원'), (5, '지현', '지현 · 26세 직장인')]:
        sh = shape_by_id(slide, sid)
        assert sh.text_frame.text.startswith(old)
        set_runs(sh, [(new, None)])
        wrap_none(sh)
    q = shape_by_id(slide, 335)
    assert q.text_frame.paragraphs[1].runs[0].text == '제때 챙겨주고 싶어요'
    set_runs(q, [('챙겨주고 싶어요', None), ('.”', None)], para=1)

    # 오른쪽 상자 3개: 오른쪽 끝(1205.3) 고정, 폭 262.5 → 236
    R, NW, PAD = 1205.3, 236.0, 14.7
    L = R - NW
    in_l, in_r = L + PAD, R - PAD                 # 안쪽 984.0 ~ 1190.6
    k = (in_r - in_l) / (1190.6 - 957.5)          # 안쪽 폭 비율
    for sid in (1001, 1023, 1031):
        move_abs(shape_by_id(slide, sid), x=L, w=NW)
    # 상자 1: 아이콘 4개(노트·메일·톡·갤러리) 같은 간격
    step = (in_r - in_l - 22.0) / 3
    xs = [in_l + i * step for i in range(4)]
    groups = {'note': (1002, range(1002, 1009)), 'chat': (1009, range(1009, 1015)), 'gallery': (1015, range(1015, 1022))}
    for key, xnew in (('note', xs[0]), ('chat', xs[2]), ('gallery', xs[3])):
        base, ids = groups[key]
        dx = xnew - pos(shape_by_id(slide, base))[0]
        for sid in ids:
            shift(shape_by_id(slide, sid), dx=dx)
    add_mail_icon(slide, xs[1], pos(shape_by_id(slide, 1015))[1])
    cap = shape_by_id(slide, 1022)
    move_abs(cap, x=in_l, w=in_r - in_l)
    # 상자 2: 검색창 + '그게 이름이 뭐였더라..' + 커서, 가운데 아이콘 쌍
    bar = shape_by_id(slide, 1024)
    dxb = in_l - pos(bar)[0]
    move_abs(bar, x=in_l, w=in_r - in_l)
    for sid in (1025, 1026):
        shift(shape_by_id(slide, sid), dx=dxb)
    mag_r = pos(shape_by_id(slide, 1026))[0] + pos(shape_by_id(slide, 1026))[2]
    qx = mag_r + 5.5
    qtext = '그게 이름이 뭐였더라..'
    add_query_text(slide, bar, qx, qtext, cap)
    qw = width(qtext, 12, 400, -0.2 * 4 / 3)
    move_abs(shape_by_id(slide, 1027), x=qx + qw + 1.5)
    dxc = (L + NW / 2) - (942.8 + 262.5 / 2)
    for sid in range(18, 28):
        shift(shape_by_id(slide, sid), dx=dxc)
    # 상자 3: 두 막대 비율 축소, 점 3개는 간격 유지
    b1, b2 = shape_by_id(slide, 1032), shape_by_id(slide, 1033)
    x1, _, w1, _ = pos(b1); x2, _, w2, _ = pos(b2)
    move_abs(b1, x=in_l + (x1 - 957.5) * k, w=w1 * k)
    move_abs(b2, x=in_l + (x2 - 957.5) * k, w=w2 * k)
    dots = [shape_by_id(slide, i) for i in (35, 36, 37)]
    c_old = (pos(dots[0])[0] + pos(dots[2])[0] + pos(dots[2])[2]) / 2
    c_new = in_l + (c_old - 957.5) * k
    for d in dots:
        shift(d, dx=c_new - c_old)

    # 인물 그림: 6·8쪽 그림체로 새로 만든 성빈·지현 (지현은 말풍선 쪽을 보도록 좌우 반전)
    sb, jh = shape_by_id(slide, 6), shape_by_id(slide, 7)
    assert sb.name == '그림 5' and jh.name == '그림 6'
    # 원본 폭 전체를 쓰고 세로만 잘라 어깨가 옆에서 잘리지 않게 함 (y=1040에서도 옷 끝이 원본 좌우 끝에서 70px 이상 안쪽)
    H, bottom = 130.0, 676.0
    for pic, path, crop, mirror, cx in ((sb, sungbin_png, (0, 80, 1254, 1040), False, 155.0),
                                        (jh, jihyun_png, (0, 30, 1254, 1040), True, 1137.0)):
        replace_picture(slide, pic, portrait_png(path, crop, mirror=mirror))
        w = H * (crop[2] - crop[0]) / (crop[3] - crop[1])
        move_abs(pic, x=cx - w / 2, y=bottom - H, w=w, h=H)
    sb.name, jh.name = '성빈 (6쪽 그림체)', '지현 (8쪽 그림체)'
    return drop_unused_images(slide)
