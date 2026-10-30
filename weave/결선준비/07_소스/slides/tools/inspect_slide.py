"""장표 도형 요약 (읽기 전용). 그룹 변환을 반영한 절대 좌표(px), 채우기, 글자 크기·색·굵기를 한 줄씩 출력.

사용: python inspect_slide.py deck.pptx 4 [id ...]
"""
import sys

from pptx import Presentation
from pptx.oxml.ns import qn

PX = 9525


def abs_boxes(shapes, tf=(1, 1, 0, 0)):
    """(shape, (x, y, w, h)) — 그룹 안 도형은 그룹 변환을 적용."""
    sx, sy, ox, oy = tf
    for sh in shapes:
        x, y, w, h = (sh.left or 0), (sh.top or 0), (sh.width or 0), (sh.height or 0)
        box = (x * sx + ox, y * sy + oy, w * sx, h * sy)
        yield sh, tuple(v / PX for v in box)
        if sh.shape_type == 6:
            xfrm = sh._element.find(qn('p:grpSpPr')).find(qn('a:xfrm'))
            off, ext = xfrm.find(qn('a:off')), xfrm.find(qn('a:ext'))
            choff, chext = xfrm.find(qn('a:chOff')), xfrm.find(qn('a:chExt'))
            gx, gy, gw, gh = (int(off.get('x')), int(off.get('y')), int(ext.get('cx')), int(ext.get('cy')))
            cx, cy, cw, ch = (int(choff.get('x')), int(choff.get('y')), int(chext.get('cx')), int(chext.get('cy')))
            ksx, ksy = (gw / cw if cw else 1), (gh / ch if ch else 1)
            # 자식 좌표 → 그룹 좌표 → 부모 변환
            ntf = (sx * ksx, sy * ksy, ox + sx * (gx - cx * ksx), oy + sy * (gy - cy * ksy))
            yield from abs_boxes(sh.shapes, ntf)


def fill_of(sh):
    spPr = sh._element.find(qn('p:spPr'))
    if spPr is None:
        return ''
    sf = spPr.find(qn('a:solidFill'))
    if sf is not None:
        c = sf[0]
        a = c.find(qn('a:alpha'))
        return f"fill={c.get('val')}" + (f"@{int(a.get('val'))//1000}%" if a is not None else '')
    gf = spPr.find(qn('a:gradFill'))
    if gf is not None:
        return 'fill=grad(' + ','.join(g[0].get('val') or '?' for g in gf.iter(qn('a:gs'))) + ')'
    ln = spPr.find(qn('a:ln'))
    if ln is not None and ln.find(qn('a:solidFill')) is not None:
        return f"line={ln.find(qn('a:solidFill'))[0].get('val')}"
    return ''


def runs_of(sh):
    out = []
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            rPr = r._r.find(qn('a:rPr'))
            col = None
            if rPr is not None and rPr.find(qn('a:solidFill')) is not None:
                col = rPr.find(qn('a:solidFill'))[0].get('val')
            lat = rPr.find(qn('a:latin')).get('typeface') if rPr is not None and rPr.find(qn('a:latin')) is not None else None
            out.append(f"'{r.text}'({r.font.size.pt if r.font.size else '-'}pt,b={rPr.get('b') if rPr is not None else None},{col},{lat},spc={rPr.get('spc') if rPr is not None else None})")
        out.append('¶')
    return ' '.join(out[:-1])


def main():
    prs = Presentation(sys.argv[1])
    slide = prs.slides[int(sys.argv[2]) - 1]
    ids = {int(a) for a in sys.argv[3:]}
    for sh, (x, y, w, h) in abs_boxes(slide.shapes):
        if ids and sh.shape_id not in ids:
            continue
        geo = ''
        g = sh._element.find('.//' + qn('a:prstGeom'))
        if g is not None:
            geo = g.get('prst')
        txt = runs_of(sh) if sh.has_text_frame and sh.text_frame.text.strip() else ''
        print(f'[{sh.shape_id}] {sh.shape_type} {sh.name!r} ({x:.1f},{y:.1f},{w:.1f},{h:.1f}) rot={getattr(sh, "rotation", 0)} {geo} {fill_of(sh)} {txt}')


if __name__ == '__main__':
    main()
