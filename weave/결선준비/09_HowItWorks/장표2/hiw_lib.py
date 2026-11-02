"""How it Works 장표용 도우미: 도형·글자·그림·실(곡선)·묶음 XML과 클릭 애니메이션(p:timing).

좌표는 모두 덱과 같은 1280×720 px(1px = 9525 EMU). 글자는 영문·숫자 조각(Inter)과 한글 조각(Noto Sans KR)으로 나눠 씀
(07_소스/slides/tools/header.py와 같은 규칙). 글자 폭은 PIL로 같은 TTF를 재서 형광펜 자리를 계산함.
"""
import math
from functools import lru_cache
from itertools import count
from pathlib import Path

from lxml import etree
from PIL import ImageFont

PX = 9525
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
FONTDIR = Path(__file__).resolve().parents[2] / '06_에셋' / '글꼴'

# 굵기 → (영문 글꼴, 한글 글꼴, b 속성). 덱에서 쓰는 이름 그대로.
FACES = {
    'r': ('Inter', 'Noto Sans KR', False),
    'm': ('Inter Medium', 'Noto Sans KR Medium', False),
    'sb': ('Inter SemiBold', 'Noto Sans KR SemiBold', False),
    'b': ('Inter', 'Noto Sans KR', True),
}
WEIGHT = {'r': 400, 'm': 500, 'sb': 600, 'b': 700}
PEN = 'Nanum Pen Script'


def q(tag):
    ns, t = tag.split(':')
    return '{%s}%s' % (NS[ns], t)


def E(v):
    return str(int(round(v * PX)))


def el(tag, parent=None, **attrs):
    e = etree.SubElement(parent, q(tag)) if parent is not None else etree.Element(q(tag), nsmap=NS if tag.startswith('p:') else None)
    for k, v in attrs.items():
        e.set(k.replace('__', ':') if '__' in k else k, str(v))
    return e


# ------------------------------------------------------------------ 글자 폭
@lru_cache(None)
def _font(fam, w):
    f = {'inter': f'Inter-{w}.ttf', 'noto': f'NotoSansKR-{w}.ttf', 'pen': 'NanumPenScript-Regular.ttf'}[fam]
    return ImageFont.truetype(str(FONTDIR / f), size=200)


def is_ko(ch):
    o = ord(ch)
    return (0xAC00 <= o <= 0xD7A3 or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F
            or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF)


def _measure_font(ch, run_ko):
    """PowerPoint가 이 글자를 어느 글꼴로 그리는지: 한글 조각 안의 따옴표·가운뎃점은 한글 글꼴(ea), 나머지 기호·공백은 Inter."""
    if is_ko(ch):
        return 'noto'
    if run_ko and ch in '“”‘’·…':
        return 'noto'
    return 'inter'


def width(text, pt, weight='r', pen=False, spc=0.0):
    """글자 폭(px). pt는 덱 글자 크기(1pt = 4/3 px). spc = 글자 사이 간격(pt, PowerPoint spc/100)."""
    px = pt * 4 / 3
    if pen:
        return _font('pen', 400).getlength(text) * px / 200 + spc * 4 / 3 * len(text)
    total = 0.0
    for seg, cls in split_script(text):
        run_ko = cls == 'ko'
        cur, buf = None, ''
        for ch in seg:
            fam = _measure_font(ch, run_ko)
            if fam != cur and buf:
                total += _font(cur, WEIGHT[weight]).getlength(buf)
                buf = ''
            cur = fam
            buf += ch
        if buf:
            total += _font(cur, WEIGHT[weight]).getlength(buf)
    return total * px / 200 + spc * 4 / 3 * len(text)


def char_class(ch):
    if is_ko(ch):
        return 'ko'
    if ch.isalnum():
        return 'latin'
    return None


def split_script(text, default='latin'):
    """[(조각, 'latin'|'ko')]. 공백·기호는 앞 조각에 붙임(맨 앞이면 뒤 조각에). header.py와 같은 규칙."""
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


# ------------------------------------------------------------------ 공통 조각
def _fill(parent, color, alpha=None):
    if color is None:
        el('a:noFill', parent)
        return
    sf = el('a:solidFill', parent)
    c = el('a:srgbClr', sf, val=color)
    if alpha is not None:
        el('a:alpha', c, val=int(alpha * 1000))


def _line(spPr, color=None, w=0.75, alpha=None, dash=None, grad=None, cap=None):
    """w는 px(덱 1px = 0.75pt). color None이면 선 없음."""
    ln = el('a:ln', spPr, w=E(w))
    if cap:
        ln.set('cap', cap)
    if grad:
        gf = el('a:gradFill', ln)
        gl = el('a:gsLst', gf)
        for pos, col, al in grad['stops']:
            c = el('a:srgbClr', el('a:gs', gl, pos=int(pos * 1000)), val=col)
            if al is not None:
                el('a:alpha', c, val=int(al * 1000))
        el('a:lin', gf, ang=int(grad.get('ang', 0) * 60000) % 21600000, scaled=0)
    elif color is None:
        el('a:noFill', ln)
        return ln
    else:
        _fill(ln, color, alpha)
    if dash:
        el('a:prstDash', ln, val=dash)
    el('a:round', ln)
    return ln


def _effects(spPr, shadow=None, glow=None):
    if not (shadow or glow):
        return
    ef = el('a:effectLst', spPr)
    if glow:
        rad, col, al = glow
        g = el('a:glow', ef, rad=E(rad))
        el('a:alpha', el('a:srgbClr', g, val=col), val=int(al * 1000))
    if shadow:
        blur, dist, col, al = shadow
        s = el('a:outerShdw', ef, blurRad=E(blur), dist=E(dist), dir=5400000, algn='t', rotWithShape=0)
        el('a:alpha', el('a:srgbClr', s, val=col), val=int(al * 1000))


def _nv(sp, tag, sid, name, descr=None):
    nv = el(tag, sp)
    c = el('p:cNvPr', nv, id=sid, name=name)
    if descr:
        c.set('descr', descr)
    return nv


# ------------------------------------------------------------------ 도형
SHADOW_CARD = (18, 4, '6B4EFF', 7)       # blur px, dist px, color, alpha %
SHADOW_SOFT = (12, 3, '6B4EFF', 6)
SHADOW_LIFT = (26, 8, '6B4EFF', 14)


def shape(sid, name, x, y, w, h, prst='rect', radius=None, fill='FFFFFF', alpha=None, line=None, line_w=0.75,
          line_alpha=None, dash=None, shadow=None, glow=None, grad_fill=None, custom_path=None):
    """p:sp 하나. radius(px)는 roundRect 모서리. grad_fill = dict(stops=[(pos%, color, alpha%)], path='circle'|None, ang, rect)."""
    sp = etree.Element(q('p:sp'), nsmap=NS)
    nv = _nv(sp, 'p:nvSpPr', sid, name)
    el('p:cNvSpPr', nv)
    el('p:nvPr', nv)
    spPr = el('p:spPr', sp)
    xf = el('a:xfrm', spPr)
    el('a:off', xf, x=E(x), y=E(y))
    el('a:ext', xf, cx=E(max(w, 0.01)), cy=E(max(h, 0.01)))
    if custom_path is not None:
        spPr.append(custom_path)
    else:
        g = el('a:prstGeom', spPr, prst=prst)
        av = el('a:avLst', g)
        if prst == 'roundRect':
            r = 50000 if radius is None else min(50000, int(radius / max(1e-6, min(w, h)) * 100000))
            el('a:gd', av, name='adj', fmla='val %d' % r)
    if grad_fill:
        gf = el('a:gradFill', spPr, rotWithShape=1)
        gl = el('a:gsLst', gf)
        for pos, col, al in grad_fill['stops']:
            c = el('a:srgbClr', el('a:gs', gl, pos=int(pos * 1000)), val=col)
            if al is not None:
                el('a:alpha', c, val=int(al * 1000))
        if grad_fill.get('path'):
            pth = el('a:path', gf, path=grad_fill['path'])
            l, t, r, b = grad_fill.get('rect', (50, 50, 50, 50))
            el('a:fillToRect', pth, l=int(l * 1000), t=int(t * 1000), r=int(r * 1000), b=int(b * 1000))
        else:
            el('a:lin', gf, ang=int(grad_fill.get('ang', 90) * 60000), scaled=0)
    else:
        _fill(spPr, fill, alpha)
    _line(spPr, line, line_w, line_alpha, dash)
    _effects(spPr, shadow, glow)
    tx = el('p:txBody', sp)
    el('a:bodyPr', tx, rtlCol=0, anchor='ctr')
    el('a:lstStyle', tx)
    el('a:p', tx)
    return sp


def rpr(tag, size, color, weight='r', pen=False, cls='latin', spc=0, alpha=None, parent=None):
    lat, ea, bold = FACES[weight]
    if pen:
        lat = ea = PEN
        bold = False
    e = el(tag, parent) if parent is not None else etree.Element(q(tag))
    e.set('lang', 'en-US' if cls == 'latin' else 'ko-KR')
    if cls != 'latin':
        e.set('altLang', 'en-US')
    e.set('sz', str(int(round(size * 100))))
    e.set('b', '1' if bold else '0')
    e.set('i', '0')
    e.set('spc', str(int(round(spc * 100))))
    e.set('dirty', '0')
    c = el('a:srgbClr', el('a:solidFill', e), val=color)
    if alpha is not None:
        el('a:alpha', c, val=int(alpha * 1000))
    el('a:latin', e, typeface=lat)
    el('a:ea', e, typeface=lat if (cls == 'latin' and not pen) else ea)
    el('a:cs', e, typeface=lat if (cls == 'latin' and not pen) else ea)
    return e


def text(sid, name, x, y, w, h, paras, size=10, color='1C1A24', weight='r', align='l', anchor='t', lnspc=None,
         spc=0, pen=False, wrap=False, ins=(0, 0, 0, 0), fill=None, line=None, radius=None, alpha=None):
    """글자 상자. paras = [문단], 문단 = str 또는 [(글자, {color, weight, size, spc, alpha})...].
    lnspc: None이면 100%, 숫자면 고정 줄 간격(pt)."""
    sp = shape(sid, name, x, y, w, h, prst='roundRect' if radius else 'rect', radius=radius, fill=fill, line=line)
    sp.find(q('p:nvSpPr')).find(q('p:cNvSpPr')).set('txBox', '1')
    tx = sp.find(q('p:txBody'))
    for c in list(tx):
        tx.remove(c)
    l, t, r, b = ins
    bp = el('a:bodyPr', tx, wrap='square' if wrap else 'none', lIns=E(l), tIns=E(t), rIns=E(r), bIns=E(b),
            rtlCol=0, anchor=anchor, anchorCtr=0)
    el('a:noAutofit', bp)
    el('a:lstStyle', tx)
    if isinstance(paras, str):
        paras = [paras]
    for para in paras:
        if isinstance(para, str):
            para = [(para, {})]
        p = el('a:p', tx)
        pPr = el('a:pPr', p, algn={'l': 'l', 'c': 'ctr', 'r': 'r'}[align])
        ls = el('a:lnSpc', pPr)
        if lnspc:
            el('a:spcPts', ls, val=int(lnspc * 100))
        else:
            el('a:spcPct', ls, val=100000)
        el('a:spcPts', el('a:spcBef', pPr), val=0)
        el('a:spcPts', el('a:spcAft', pPr), val=0)
        el('a:buNone', pPr)
        last = None
        prev = 'latin'
        for chunk, o in para:
            o = dict(o)
            sz, col, wt = o.get('size', size), o.get('color', color), o.get('weight', weight)
            sc, pn, al = o.get('spc', spc), o.get('pen', pen), o.get('alpha', alpha)
            for seg, cls in split_script(chunk, prev):
                prev = cls
                r_ = el('a:r', p)
                rpr('a:rPr', sz, col, wt, pn, cls, sc if cls == 'latin' else o.get('spc_ko', 0 if not pn else sc), al, parent=r_)
                el('a:t', r_).text = seg
                last = (sz, col, wt, pn, cls, sc, al)
        if last:
            sz, col, wt, pn, cls, sc, al = last
            rpr('a:endParaRPr', sz, col, wt, pn, cls, sc, al, parent=p)
    return sp


def picture(sid, name, rId, x, y, w, h, crop=None, radius=None, line=None, line_w=0.75, shadow=None, alpha=None):
    """p:pic. crop=(l,t,r,b) 비율(0~1). radius px면 모서리 둥글게."""
    pic = etree.Element(q('p:pic'), nsmap=NS)
    nv = _nv(pic, 'p:nvPicPr', sid, name)
    el('a:picLocks', el('p:cNvPicPr', nv), noChangeAspect=1)
    el('p:nvPr', nv)
    bf = el('p:blipFill', pic)
    blip = el('a:blip', bf)
    blip.set(q('r:embed'), rId)
    if alpha is not None:
        el('a:alphaModFix', blip, amt=int(alpha * 1000))
    if crop:
        l, t, r, b = crop
        el('a:srcRect', bf, l=int(l * 100000), t=int(t * 100000), r=int(r * 100000), b=int(b * 100000))
    el('a:fillRect', el('a:stretch', bf))
    spPr = el('p:spPr', pic)
    xf = el('a:xfrm', spPr)
    el('a:off', xf, x=E(x), y=E(y))
    el('a:ext', xf, cx=E(w), cy=E(h))
    g = el('a:prstGeom', spPr, prst='roundRect' if radius else 'rect')
    av = el('a:avLst', g)
    if radius:
        el('a:gd', av, name='adj', fmla='val %d' % min(50000, int(radius / min(w, h) * 100000)))
    if line:
        _line(spPr, line, line_w)
    _effects(spPr, shadow)
    return pic


def curve(sid, name, pts, w=2.25, stops=None, alpha=None, dash=None, color=None):
    """3차 베지어 실. pts = [(x0,y0),(c1),(c2),(x1,y1)] px. 기본은 보라 그라데이션(인트로와 같은 S자 실)."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    bx, by = min(xs), min(ys)
    bw, bh = max(max(xs) - bx, 0.5), max(max(ys) - by, 0.5)
    cg = etree.Element(q('a:custGeom'))
    for t in ('a:avLst', 'a:gdLst', 'a:ahLst', 'a:cxnLst'):
        el(t, cg)
    el('a:rect', cg, l='l', t='t', r='r', b='b')
    pl = el('a:pathLst', cg)
    path = el('a:path', pl, w=E(bw), h=E(bh), fill='none')
    (x0, y0), c1, c2, (x1, y1) = pts
    el('a:pt', el('a:moveTo', path), x=E(x0 - bx), y=E(y0 - by))
    cb = el('a:cubicBezTo', path)
    for px_, py_ in (c1, c2, (x1, y1)):
        el('a:pt', cb, x=E(px_ - bx), y=E(py_ - by))
    sp = shape(sid, name, bx, by, bw, bh, fill=None, custom_path=cg)
    spPr = sp.find(q('p:spPr'))
    for ln in spPr.findall(q('a:ln')):
        spPr.remove(ln)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0)) % 360
    if color:
        ln = _line(spPr, color, w, alpha, dash, cap='rnd')
    else:
        stops = stops or [(0, 'B08CFF', alpha), (100, '6B4EFF', alpha)]
        ln = _line(spPr, None, w, None, dash, grad=dict(stops=stops, ang=ang), cap='rnd')
    # 그림자 대신 살짝 번지는 빛(인트로 실의 drop-shadow 느낌)
    return sp


def group(sid, name, children):
    """자식은 슬라이드 절대 좌표 그대로. 묶음 좌표계 = 자식 상자들의 합집합(배율 1)."""
    boxes = []
    for c in children:
        xf = c.find('.//' + q('a:xfrm'))
        off, ext = xf.find(q('a:off')), xf.find(q('a:ext'))
        x, y = int(off.get('x')), int(off.get('y'))
        boxes.append((x, y, x + int(ext.get('cx')), y + int(ext.get('cy'))))
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    g = etree.Element(q('p:grpSp'), nsmap=NS)
    nv = _nv(g, 'p:nvGrpSpPr', sid, name)
    el('p:cNvGrpSpPr', nv)
    el('p:nvPr', nv)
    gp = el('p:grpSpPr', g)
    xf = el('a:xfrm', gp)
    el('a:off', xf, x=x0, y=y0)
    el('a:ext', xf, cx=x1 - x0, cy=y1 - y0)
    el('a:chOff', xf, x=x0, y=y0)
    el('a:chExt', xf, cx=x1 - x0, cy=y1 - y0)
    for c in children:
        g.append(c)
    return g


def box_of(e):
    """요소의 (x, y, w, h) px."""
    xf = e.find('.//' + q('a:xfrm'))
    off, ext = xf.find(q('a:off')), xf.find(q('a:ext'))
    return (int(off.get('x')) / PX, int(off.get('y')) / PX, int(ext.get('cx')) / PX, int(ext.get('cy')) / PX)


# ------------------------------------------------------------------ 애니메이션
class Timeline:
    """클릭 단계별 효과 목록 → p:timing.

    효과 dict: kind(fade_in, fade_out, rise, zoom_in, wipe_in, path, pulse), spid, delay(ms), dur(ms), 기타.
    한 단계 안의 효과는 모두 '이전 효과와 함께 + 지연'으로 넣고, 첫 효과만 클릭으로 시작."""

    def __init__(self):
        self.steps = []

    def step(self):
        self.steps.append([])

    def add(self, kind, spid, delay=0, dur=400, **kw):
        self.steps[-1].append(dict(kind=kind, spid=spid, delay=int(delay), dur=int(dur), **kw))

    def step_len(self, i):
        return max([e['delay'] + e['dur'] * (2 if e.get('autorev') else 1) for e in self.steps[i]] or [0])

    # -------------------------------------------------------------- XML
    def xml(self, sp_ids, auto=None):
        """sp_ids: bldP를 적을 p:sp spid 집합. auto = (첫 대기 ms, [단계별 머무는 ms])면 클릭 없이 자동 재생(미리보기 영상용)."""
        ids = count(1)
        grp_of = {}
        timing = etree.Element(q('p:timing'), nsmap=NS)
        root = el('p:cTn', el('p:par', el('p:tnLst', timing)), id=next(ids), dur='indefinite', restart='never', nodeType='tmRoot')
        seq = el('p:seq', el('p:childTnLst', root), concurrent=1, nextAc='seek')
        main = el('p:cTn', seq, id=next(ids), dur='indefinite', nodeType='mainSeq')
        mkids = el('p:childTnLst', main)
        if auto:
            t0, holds = auto
            outer = el('p:cTn', el('p:par', mkids), id=next(ids), fill='hold')
            sc = el('p:stCondLst', outer)
            el('p:cond', sc, delay='indefinite')
            c = el('p:cond', sc, evt='onBegin', delay=0)
            el('p:tn', c, val=2)
            okids = el('p:childTnLst', outer)
            t = t0
            for i, effs in enumerate(self.steps):
                inner = el('p:cTn', el('p:par', okids), id=next(ids), fill='hold')
                el('p:cond', el('p:stCondLst', inner), delay=t)
                ik = el('p:childTnLst', inner)
                for j, e in enumerate(effs):
                    self._effect(ik, ids, e, 'afterEffect' if j == 0 else 'withEffect', grp_of)
                t += self.step_len(i) + holds[i]
        else:
            for effs in self.steps:
                outer = el('p:cTn', el('p:par', mkids), id=next(ids), fill='hold')
                el('p:cond', el('p:stCondLst', outer), delay='indefinite')
                inner = el('p:cTn', el('p:par', el('p:childTnLst', outer)), id=next(ids), fill='hold')
                el('p:cond', el('p:stCondLst', inner), delay=0)
                ik = el('p:childTnLst', inner)
                for j, e in enumerate(effs):
                    self._effect(ik, ids, e, 'clickEffect' if j == 0 else 'withEffect', grp_of)
        pc = el('p:prevCondLst', seq)
        el('p:sldTgt', el('p:tgtEl', el('p:cond', pc, evt='onPrev', delay=0)))
        nc = el('p:nextCondLst', seq)
        el('p:sldTgt', el('p:tgtEl', el('p:cond', nc, evt='onNext', delay=0)))
        bl = el('p:bldLst', timing)
        for spid, n in sorted(grp_of.items()):
            if spid in sp_ids:
                for g in range(n):
                    el('p:bldP', bl, spid=spid, grpId=g, animBg=1)
        if not len(bl):
            timing.remove(bl)
        return timing

    @staticmethod
    def _tgt(parent, spid):
        el('p:spTgt', el('p:tgtEl', parent), spid=spid)

    def _set_vis(self, kids, ids, spid, val, delay=0):
        s = el('p:set', kids)
        cb = el('p:cBhvr', s)
        ct = el('p:cTn', cb, id=next(ids), dur=1, fill='hold')
        el('p:cond', el('p:stCondLst', ct), delay=delay)
        self._tgt(cb, spid)
        el('p:attrName', el('p:attrNameLst', cb)).text = 'style.visibility'
        el('p:strVal', el('p:to', s), val=val)

    def _anim_effect(self, kids, ids, spid, transition, flt, dur):
        ae = el('p:animEffect', kids, transition=transition, filter=flt)
        cb = el('p:cBhvr', ae)
        el('p:cTn', cb, id=next(ids), dur=dur)
        self._tgt(cb, spid)

    def _anim(self, kids, ids, spid, attr, frm, to, dur, decel=None):
        a = el('p:anim', kids, calcmode='lin', valueType='num')
        cb = el('p:cBhvr', a, additive='base')
        ct = el('p:cTn', cb, id=next(ids), dur=dur, fill='hold')
        if decel:
            ct.set('decel', str(decel))
        self._tgt(cb, spid)
        el('p:attrName', el('p:attrNameLst', cb)).text = attr
        tl = el('p:tavLst', a)
        for tm, v in ((0, frm), (100000, to)):
            el('p:strVal', el('p:val', el('p:tav', tl, tm=tm)), val=v)

    def _effect(self, kids, ids, e, node, grp_of):
        spid, kind, dur = e['spid'], e['kind'], e['dur']
        g = grp_of.get(spid, 0)
        grp_of[spid] = g + 1
        preset = {'fade_in': (10, 'entr', 0), 'fade_out': (10, 'exit', 0), 'rise': (42, 'entr', 0),
                  'zoom_in': (53, 'entr', 16), 'wipe_in': (22, 'entr', {'left': 8, 'right': 2, 'down': 1, 'up': 4}[e.get('dir', 'left')]),
                  'path': (0, 'path', 0), 'move': (0, 'path', 0), 'pulse': (6, 'emph', 0)}[kind]
        par = el('p:par', kids)
        ct = el('p:cTn', par, id=next(ids), presetID=preset[0], presetClass=preset[1], presetSubtype=preset[2], fill='hold', grpId=g, nodeType=node)
        if kind == 'path':
            ct.set('accel', '45000')
            ct.set('decel', '55000')
        if kind == 'pulse':
            ct.set('autoRev', '1')
        el('p:cond', el('p:stCondLst', ct), delay=e['delay'])
        ck = el('p:childTnLst', ct)
        if kind == 'fade_in':
            self._set_vis(ck, ids, spid, 'visible')
            self._anim_effect(ck, ids, spid, 'in', 'fade', dur)
        elif kind == 'fade_out':
            self._anim_effect(ck, ids, spid, 'out', 'fade', dur)
            self._set_vis(ck, ids, spid, 'hidden', delay=max(dur - 1, 0))
        elif kind == 'rise':
            # 아래에서 살짝(기본 10px) 떠오르며 나타남
            dy = e.get('dy', 10) / 720
            self._set_vis(ck, ids, spid, 'visible')
            self._anim_effect(ck, ids, spid, 'in', 'fade', dur)
            self._anim(ck, ids, spid, 'ppt_x', '#ppt_x', '#ppt_x', dur)
            self._anim(ck, ids, spid, 'ppt_y', '#ppt_y+%.4f' % dy, '#ppt_y', dur, decel=100000)
        elif kind == 'zoom_in':
            s0 = e.get('from', 0.88)
            self._set_vis(ck, ids, spid, 'visible')
            self._anim(ck, ids, spid, 'ppt_w', '#ppt_w*%.3f' % s0, '#ppt_w', dur, decel=100000)
            self._anim(ck, ids, spid, 'ppt_h', '#ppt_h*%.3f' % s0, '#ppt_h', dur, decel=100000)
            self._anim_effect(ck, ids, spid, 'in', 'fade', dur)
        elif kind == 'wipe_in':
            flt = {'left': 'wipe(left)', 'right': 'wipe(right)', 'down': 'wipe(down)', 'up': 'wipe(up)'}[e.get('dir', 'left')]
            self._set_vis(ck, ids, spid, 'visible')
            self._anim_effect(ck, ids, spid, 'in', flt, dur)
        elif kind == 'path':
            # 놓인 자리에서 (dx, dy)px 떨어진 곳에서 출발해 곡선으로 제자리에 옴
            dx, dy = e['dx'] / 1280, e['dy'] / 720
            bend = e.get('bend', 0.25)
            # 출발점→도착점(0,0) 3차 곡선, 가운데를 수직 방향으로 휘게
            nx, ny = -dy, dx
            c1 = (dx * 0.62 + nx * bend, dy * 0.62 + ny * bend)
            c2 = (dx * 0.18 + nx * bend * 0.6, dy * 0.18 + ny * bend * 0.6)
            path = 'M %.4f %.4f C %.4f %.4f %.4f %.4f 0 0 E' % (dx, dy, c1[0], c1[1], c2[0], c2[1])
            am = el('p:animMotion', ck, origin='layout', path=path, pathEditMode='relative', rAng=0, ptsTypes='')
            cb = el('p:cBhvr', am)
            el('p:cTn', cb, id=next(ids), dur=dur, fill='hold')
            self._tgt(cb, spid)
            an = el('p:attrNameLst', cb)
            el('p:attrName', an).text = 'ppt_x'
            el('p:attrName', an).text = 'ppt_y'
            el('p:rCtr', am, x=0, y=0)
        elif kind == 'move':
            # 슬라이드 밖에 둔 도형을 순간 이동으로 제자리에 놓음(정적 보기·내보내기엔 안 보이게 하려고)
            path = 'M 0 0 L %.5f %.5f E' % (e['dx'] / 1280, e['dy'] / 720)
            am = el('p:animMotion', ck, origin='layout', path=path, pathEditMode='relative', rAng=0, ptsTypes='')
            cb = el('p:cBhvr', am)
            el('p:cTn', cb, id=next(ids), dur=dur, fill='hold')
            self._tgt(cb, spid)
            an = el('p:attrNameLst', cb)
            el('p:attrName', an).text = 'ppt_x'
            el('p:attrName', an).text = 'ppt_y'
            el('p:rCtr', am, x=0, y=0)
        elif kind == 'pulse':
            sc = int(e.get('scale', 1.06) * 100000)
            asc = el('p:animScale', ck)
            cb = el('p:cBhvr', asc)
            el('p:cTn', cb, id=next(ids), dur=dur, fill='hold')
            self._tgt(cb, spid)
            el('p:by', asc, x=sc, y=sc)
