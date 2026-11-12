"""How it Works(Claude판) 그리기 도구: 원시 도형(R/T/P/C) → PowerPoint 도형, 그리고 화면 부품(카드·칩·검색창·위 띠).

좌표는 덱과 같은 1280×720 px. 모든 도형 이름은 '!!키'라서 다음 장에 같은 이름이 있으면 모핑이 위치·크기·투명도를 잇는다.
부품 하나 = 원시 도형 목록. 여러 도형이면 PowerPoint 묶음 하나로 넣어 효과도 묶음 하나에 건다.
"""
import itertools
import math
from pathlib import Path

from lxml import etree

import hiw_lib as L
from hiw_lib import q

HERE = Path(__file__).resolve().parent
AS = HERE / 'assets'

INK, INK2, BODY, SUB, MUTE = '1C1A24', '2B2640', '4E4A57', '6A6474', '8E88A0'
LINE, LINE2 = 'E6E0F5', 'CFC3FF'
PURPLE, PURPLE2, RING, HL = '6B4EFF', '8B6BFF', '8B68F5', 'A67CF2'
LAV, LAV2 = 'F1ECFF', 'F7F4FF'
GRAY_FILL, GRAY_LINE = 'F3F1F7', 'B9B2C9'
RED = 'E5484D'
ICON = {'talk': 'app-kakao.png', 'note': 'app-notes.png', 'cal': 'samsung-calendar.png', 'gallery': 'samsung-gallery.png',
        'mail': 'samsung-email-blue.png', 'phone': 'samsung-phone.png', 'map': 'app-map.png', 'wallet': 'samsung-wallet.png',
        'spool': 'weave-spool-6B4EFF.png', 'spool_w': 'weave-spool-white.png', 'google': 'google.png'}
APP_NAME = {'talk': '카카오톡', 'note': '삼성노트', 'cal': '캘린더', 'gallery': '갤러리', 'mail': '이메일', 'phone': '전화',
            'map': '지도', 'wallet': '삼성 월렛'}


def tw(text, pt, weight='r'):
    return L.width(text, pt, weight)


# ------------------------------------------------------------------ 원시 도형
def R(name, x, y, w, h, **o):
    return ('rect', name, x, y, w, h, o)


def T(name, x, y, w, h, paras, **o):
    return ('text', name, x, y, w, h, paras, o)


def P(name, fname, x, y, w, h, **o):
    return ('pic', name, fname, x, y, w, h, o)


def C(name, pts, **o):
    return ('curve', name, pts, o)


def line(name, a, b, **o):
    return C(name, [a, a, b, b], **o)


def runs(*parts, **base):
    """[(글자, 색 또는 dict)] → 문단 조각."""
    out = []
    for t, c in parts:
        out.append((t, dict(color=c) if isinstance(c, str) else dict(c)))
    return out


class Xf:
    """부품을 통째로 옮기고 줄임: 세계 (ax, ay) → 화면 (bx, by), 배율 s."""

    def __init__(self, ax=0, ay=0, bx=0, by=0, s=1.0):
        self.ax, self.ay, self.bx, self.by, self.s = ax, ay, bx, by, s

    def X(self, v):
        return self.bx + (v - self.ax) * self.s

    def Y(self, v):
        return self.by + (v - self.ay) * self.s


ID = Xf()


# ------------------------------------------------------------------ 그리기
class Painter:
    def __init__(self, slide):
        self.slide = slide
        self.part = slide.part
        self.ids = itertools.count(10)
        self.rids = {}
        self.tree = slide.shapes._spTree
        self.spids = {}            # 부품 키 → [spid]
        self.boxes = {}

    def sid(self):
        return next(self.ids)

    def rid(self, fname):
        if fname not in self.rids:
            p = Path(fname)
            if not p.is_absolute():
                p = AS / fname
            _, r = self.part.get_or_add_image_part(str(p))
            self.rids[fname] = r
        return self.rids[fname]

    def el(self, p, alpha=100, xf=ID):
        a = alpha / 100.0
        s = xf.s
        kind, name = p[0], '!!' + p[1]
        if kind == 'rect':
            _, _, x, y, w, h, o = p
            fa = o.get('alpha', 100) * a if o.get('fill', 'FFFFFF') else None
            la = o.get('line_alpha', 100) * a
            shadow = o.get('shadow') if a > 0.6 else None
            glow = o.get('glow') if a > 0.6 else None
            return L.shape(self.sid(), name, xf.X(x), xf.Y(y), w * s, h * s, prst=o.get('prst', 'rect'),
                           radius=(o['radius'] * s) if o.get('radius') is not None else None,
                           fill=o.get('fill', 'FFFFFF'), alpha=None if fa is None or fa >= 99.9 else fa,
                           line=o.get('line'), line_w=max(0.5, o.get('line_w', 0.75) * s),
                           line_alpha=None if la >= 99.9 else la, dash=o.get('dash'), shadow=shadow, glow=glow,
                           grad_fill=o.get('grad'), soft=o.get('soft'))
        if kind == 'text':
            _, _, x, y, w, h, paras, o = p
            ta = o.get('alpha', 100) * a
            if s != 1.0 and not isinstance(paras, str):
                paras = [[(t, dict(d, size=d['size'] * s) if 'size' in d else d) for t, d in para]
                         if not isinstance(para, str) else para for para in paras]
            e = L.text(self.sid(), name, xf.X(x), xf.Y(y), w * s, h * s, paras, size=o.get('size', 10) * s,
                       color=o.get('color', INK), weight=o.get('weight', 'r'), align=o.get('align', 'l'),
                       anchor=o.get('anchor', 't'), pen=o.get('pen', False), alpha=None if ta >= 99.9 else ta,
                       spc=o.get('spc', 0) * s, lnspc=(o['lnspc'] * s) if o.get('lnspc') else None,
                       wrap=o.get('wrap', False), fill=o.get('fill'), radius=(o['radius'] * s) if o.get('radius') else None)
            if o.get('fill') and o.get('fill_alpha') is not None:
                sf = e.find(q('p:spPr')).find(q('a:solidFill'))
                if sf is not None:
                    c = sf.find(q('a:srgbClr'))
                    L.el('a:alpha', c, val=int(o['fill_alpha'] * a * 1000))
            return e
        if kind == 'pic':
            _, _, fname, x, y, w, h, o = p
            pa = o.get('alpha', 100) * a
            e = L.picture(self.sid(), name, self.rid(fname), xf.X(x), xf.Y(y), w * s, h * s, crop=o.get('crop'),
                          radius=(o['radius'] * s) if o.get('radius') else None, alpha=None if pa >= 99.9 else pa,
                          line=o.get('line'), line_w=o.get('line_w', 0.75) * s, shadow=o.get('shadow') if a > 0.6 else None)
            return e
        if kind == 'curve':
            _, _, pts, o = p
            ca = o.get('alpha', 100) * a
            tp = [(xf.X(px), xf.Y(py)) for px, py in pts]
            al = None if ca >= 99.9 else ca
            return L.curve(self.sid(), name, tp, w=max(0.6, o.get('w', 2.4) * s), color=o.get('color'), alpha=al,
                           dash=o.get('dash'), tail=o.get('tail'),
                           stops=o.get('stops') or [(0, 'B597FF', al), (100, '6B4EFF', al)])
        raise ValueError(kind)

    def put(self, key, prims, alpha=100, xf=ID, group=None):
        """부품 하나를 장에 넣음. 돌려줌: spid 목록."""
        if not prims:
            return []
        els = [self.el(p, alpha, xf) for p in prims]
        if group is None:
            group = len(els) > 1
        if group and len(els) > 1:
            g = L.group(self.sid(), '!!' + key, els)
            self.tree.append(g)
            ids = [int(g.find(q('p:nvGrpSpPr')).find(q('p:cNvPr')).get('id'))]
        else:
            ids = []
            for e in els:
                self.tree.append(e)
                ids.append(int(e.find('.//' + q('p:cNvPr')).get('id')))
        self.spids[key] = self.spids.get(key, []) + ids
        return ids


def crop_fit(fname, bw, bh, focus=(0.5, 0.5)):
    """사진을 상자 비율에 맞게 잘라냄(늘어나 보이지 않게). focus = 남길 중심(비율)."""
    from PIL import Image
    iw, ih = Image.open(AS / fname if not Path(fname).is_absolute() else fname).size
    ba, ia = bw / bh, iw / ih
    if abs(ba - ia) / ia < 0.01:
        return None
    if ba > ia:          # 위아래를 자름
        keep = ia / ba
        t = min(max(focus[1] - keep / 2, 0), 1 - keep)
        return (0, t, 0, 1 - keep - t)
    keep = ba / ia
    l_ = min(max(focus[0] - keep / 2, 0), 1 - keep)
    return (l_, 0, 1 - keep - l_, 0)


# ------------------------------------------------------------------ 공통 부품
SHADOW_CARD = (22, 6, '6B4EFF', 9)
SHADOW_SOFT = L.SHADOW_SOFT
SHADOW_LIFT = L.SHADOW_LIFT


def bg_prims():
    return [R('bg/base', 0, 0, 1280, 720, fill=None,
              grad=dict(stops=[(0, 'FDFCFF', None), (50, 'F8F5FF', None), (100, 'F2EDFF', None)], ang=70)),
            R('bg/glow1', 640, 0, 640, 507, fill=None,
              grad=dict(stops=[(0, 'C6B3FF', 22), (30, 'DED3FF', 10), (60, 'F8F5FF', 0)], path='circle', rect=(85, 8, 15, 92))),
            R('bg/glow2', 0, 373, 600, 347, fill=None,
              grad=dict(stops=[(0, 'BAA6FF', 24), (40, 'DCD0FF', 12), (72, 'F8F5FF', 0)], path='circle', rect=(12, 88, 88, 12)))]


STAGES = [('00', '데이터 색인'), ('01', '상황 인식'), ('02', '질의 재작성'), ('03', '연쇄 탐색'), ('04', '결과 제공')]
BAR_PT = 10.5


def bar_layout():
    widths = [24 + 8 + tw(ko, BAR_PT, 'b') + 20 for _, ko in STAGES]
    gap = 30
    total = sum(widths) + gap * (len(STAGES) - 1)
    x = 724 - total / 2
    out = []
    for w in widths:
        out.append((x, w))
        x += w + gap
    return out


def badge_prims():
    cw = tw('HOW IT WORKS', 10.5, 'sb') + 32
    return [T('top/badge', 40, 22, cw, 28, 'HOW IT WORKS', size=10.5, color='FFFFFF', weight='sb', align='c', anchor='ctr',
              spc=0.5, fill=PURPLE, radius=14)]


BADGE_BOX = (40, 22, tw('HOW IT WORKS', 10.5, 'sb') + 32, 28)


def topbar_prims(cur=None, done=(), alpha=100):
    """위 띠(00~04). cur = 지금 단계, done = 끝난 단계."""
    y0, hh = 16, 40
    lay = bar_layout()
    x0, x1 = lay[0][0], lay[-1][0] + lay[-1][1]
    out = [R('top/bar', x0 - 12, y0, x1 - x0 + 24, hh, prst='roundRect', fill='FFFFFF', alpha=94, line=LINE, shadow=SHADOW_SOFT)]
    if cur:
        i = [s for s, _ in STAGES].index(cur)
        x, w = lay[i]
        out.append(R('top/hl', x - 4, y0 + 4, w + 8, hh - 8, prst='roundRect', fill=LAV, line=RING, line_w=1.6, glow=(8, RING, 30)))
    for i, ((no, ko), (x, w)) in enumerate(zip(STAGES, lay)):
        state = 'cur' if no == cur else ('done' if no in done else 'todo')
        bf, bt, lc, lw = {'cur': (PURPLE, 'FFFFFF', INK, 'b'), 'done': ('DCD3FF', PURPLE, PURPLE, 'b'),
                          'todo': ('F1EEF8', 'C3BDD2', 'BDB7CC', 'sb')}[state]
        cy = y0 + hh / 2
        out.append(R('top/b%s' % no, x + 8, cy - 11, 22, 22, prst='ellipse', fill=bf, line=None))
        out.append(T('top/bn%s' % no, x + 8, cy - 11, 22, 22, '✓' if state == 'done' else no, size=8, color=bt, weight='b',
                     align='c', anchor='ctr'))
        out.append(T('top/l%s' % no, x + 36, y0, w - 34, hh, ko, size=BAR_PT, color=lc, weight=lw, anchor='ctr'))
        if i < len(STAGES) - 1:
            gx = lay[i + 1][0] - x - w
            out.append(T('top/a%d' % i, x + w + gx / 2 - 11, y0, 22, hh, '→', size=10, color='C9C0E8', align='c', anchor='ctr'))
    return out


def caption(name, lines, x, y, size=24, align='c', w=None, lh=None, color=INK):
    """여러 줄 제목. lines = [[(글자, 색)], ...]. 돌려줌: 원시 하나."""
    lh = lh or size * 1.42
    paras = [[(t, dict(color=c)) for t, c in ln] for ln in lines]
    widest = max(sum(tw(t, size, 'b') for t, _ in ln) for ln in lines)
    w = w or widest + 24
    x0 = {'c': x - w / 2, 'l': x, 'r': x - w}[align]
    return T(name, x0, y, w, lh * len(lines) + 4, paras, size=size, color=color, weight='b', align=align, lnspc=lh * 0.75,
             spc=-0.3)


def chip(name, x, y, label, style='outline', pt=10, h=26, padx=12, weight='b', icon=None, align='l'):
    """알약 칩. 돌려줌: (원시 목록, 폭)."""
    w = tw(label, pt, weight) + padx * 2 + (h * 0.62 + 4 if icon else 0)
    if align == 'c':
        x -= w / 2
    elif align == 'r':
        x -= w
    look = {'fill': (PURPLE, None, 'FFFFFF'), 'outline': ('FFFFFF', LINE2, PURPLE), 'soft': (LAV, None, PURPLE),
            'dash': (LAV2, PURPLE2, PURPLE), 'gray': ('FFFFFF', GRAY_LINE, SUB), 'grayfill': ('EFECF4', None, SUB),
            'white': ('FFFFFF', LINE, INK2), 'red': ('FFFFFF', 'F2B8BA', 'C8323A')}[style]
    f, ln, col = look
    out = [R(name + '/bg', x, y, w, h, prst='roundRect', fill=f, line=ln, line_w=1.0, dash='dash' if style == 'dash' else None,
             shadow=SHADOW_SOFT if style in ('fill', 'red', 'white') else None)]
    tx = x + padx
    if icon:
        isz = h * 0.62
        out.append(P(name + '/ic', ICON.get(icon, icon), x + padx - 2, y + (h - isz) / 2, isz, isz))
        tx += isz + 4
    out.append(T(name + '/t', tx, y, w, h, label, size=pt, color=col, weight=weight, anchor='ctr'))
    return out, w


def qbadge(name, cx, y, label, pt=13):
    """모션그래픽의 단서 질문 말풍선(보라 알약 + 아래 꼬리)."""
    w = tw(label, pt, 'b') + 34
    h = pt * 1.33 + 18
    x = cx - w / 2
    return [R(name + '/tail', cx - 7, y + h - 8, 14, 14, prst='diamond', fill=PURPLE, line=None),
            R(name + '/bg', x, y, w, h, prst='roundRect', fill=PURPLE, line=None, shadow=(16, 5, '6B4EFF', 22)),
            T(name + '/t', x, y, w, h, label, size=pt, color='FFFFFF', weight='b', align='c', anchor='ctr')]


def magnifier(name, cx, cy, r=10, color='8E88A0', w=2.6):
    """돋보기: 동그라미 + 45° 손잡이."""
    k = r * 0.72
    a = (cx + k, cy + k)
    b = (cx + r * 1.55, cy + r * 1.55)
    return [R(name + '/c', cx - r, cy - r, 2 * r, 2 * r, prst='ellipse', fill=None, line=color, line_w=w),
            line(name + '/h', a, b, color=color, w=w * 1.1)]


def xmark(name, cx, cy, s=40, w=5.5):
    """빨간 ✕(두 획, 둥근 끝) + 흰 테두리."""
    h = s / 2
    out = []
    for i, (a, b) in enumerate((((cx - h, cy - h), (cx + h, cy + h)), ((cx + h, cy - h), (cx - h, cy + h)))):
        out.append(line(name + '/u%d' % i, a, b, color='FFFFFF', w=w + 4))
    for i, (a, b) in enumerate((((cx - h, cy - h), (cx + h, cy + h)), ((cx + h, cy - h), (cx - h, cy + h)))):
        out.append(line(name + '/l%d' % i, a, b, color=RED, w=w))
    return out


def hl_band(name, x, y, text, sub, pt, weight='r', start=0, kind='low', color=HL, alpha=34):
    """글자 위 형광펜(모션그래픽처럼 글자 아래쪽 반). x, y = 글 상자 왼쪽 위."""
    i = text.index(sub, start)
    ox, w = tw(text[:i], pt, weight), tw(sub, pt, weight)
    S = pt * 4 / 3
    if kind == 'low':
        return R(name, x + ox - 2, y + S * 0.58, w + 4, S * 0.55, prst='roundRect', radius=3, fill=color, alpha=alpha, line=None)
    return R(name, x + ox - 3, y + S * 0.06, w + 6, S * 1.14, prst='roundRect', radius=5, fill=color, alpha=alpha, line=None)


def thread(name, pts, w=2.6, alpha=100, dash=None, color=None, tail=None):
    """인트로와 같은 보라 그라데이션 실(아래 흰 테두리). tail='triangle'이면 끝에 화살촉."""
    return [C(name + '/under', pts, w=w + 3.6, color='FFFFFF', alpha=92 * alpha / 100),
            C(name + '/line', pts, w=w, alpha=alpha, dash=dash, color=color or (PURPLE2 if tail else None), tail=tail)]


def scurve(a, b, k=0.5):
    (x0, y0), (x1, y1) = a, b
    dx = (x1 - x0) * k
    return [a, (x0 + dx, y0), (x1 - dx, y1), b]


def vcurve(a, b, k=0.5):
    (x0, y0), (x1, y1) = a, b
    dy = (y1 - y0) * k
    return [a, (x0, y0 + dy), (x1, y1 - dy), b]


def numdot(name, cx, cy, n, r=13, fill=PURPLE, pt=10):
    return [R(name + '/c', cx - r, cy - r, 2 * r, 2 * r, prst='ellipse', fill=fill, line='FFFFFF', line_w=2, shadow=SHADOW_SOFT),
            T(name + '/t', cx - r, cy - r, 2 * r, 2 * r, str(n), size=pt, color='FFFFFF', weight='b', align='c', anchor='ctr')]


# ------------------------------------------------------------------ 기록 카드
def card(key, kind, x, y, w, title, meta='', lines=(), pt=11.5, title_pt=13.5, meta_pt=9.5, bubble=None, style='base',
         img=None, img_h=None, img_focus=(0.5, 0.5), meta_under=True, icon=None):
    """모션그래픽과 같은 기록 카드: 앱 아이콘 + 제목 + (앱 · 날짜) + 본문(말풍선이면 회색 상자).
    돌려줌: (원시 목록, 높이, 자리 dict). 자리 dict: 'title', 'meta', 0.. = (x, y, 글, pt, 굵기)."""
    isz = 34
    pad = 16
    ic = icon or kind
    tx = x + pad + isz + 11
    bubble = (kind == 'talk') if bubble is None else bubble
    lh = pt * 1.33 * 1.32
    pos = {}
    body_y = y + pad + isz + 12
    if kind == 'photo':
        ih = img_h or round((w - 2 * pad) * 0.6)
        h = body_y - y + ih + pad
    elif lines:
        h = body_y - y + len(lines) * lh + (20 if bubble else 4) + pad - 4
    else:
        h = pad * 2 + isz
    border = {'base': (LINE, 1.0), 'weave': (RING, 2.4), 'gray': (GRAY_LINE, 1.3), 'dash': (PURPLE2, 1.6)}[style]
    out = [R(key + '/bg', x, y, w, h, prst='roundRect', radius=18, fill='FFFFFF', line=border[0], line_w=border[1],
             dash='dash' if style == 'dash' else None, shadow=SHADOW_LIFT if style == 'weave' else SHADOW_CARD,
             glow=(10, RING, 26) if style == 'weave' else None)]
    out.append(P(key + '/ic', ICON['gallery' if ic == 'photo' else ic], x + pad, y + pad, isz, isz))
    if meta_under:
        out.append(T(key + '/title', tx, y + pad - 3, w - (tx - x) - pad, 22, title, size=title_pt, color=INK, weight='b'))
        out.append(T(key + '/meta', tx, y + pad + 19, w - (tx - x) - pad, 18, meta, size=meta_pt, color=MUTE))
        pos['title'] = (tx, y + pad - 3, title, title_pt, 'b')
        pos['meta'] = (tx, y + pad + 19, meta, meta_pt, 'r')
    else:
        out.append(T(key + '/title', tx, y + pad + 5, w, 22, title, size=title_pt, color=INK, weight='b'))
        mw = tw(meta, meta_pt) + 4
        out.append(T(key + '/meta', x + w - pad - mw, y + pad + 8, mw + 2, 18, meta, size=meta_pt, color=MUTE))
        pos['title'] = (tx, y + pad + 5, title, title_pt, 'b')
        pos['meta'] = (x + w - pad - mw, y + pad + 8, meta, meta_pt, 'r')
    if kind == 'photo':
        out.append(P(key + '/img', img, x + pad, body_y, w - 2 * pad, ih, radius=12, crop=crop_fit(img, w - 2 * pad, ih, img_focus)))
        pos['img'] = (x + pad, body_y, w - 2 * pad, ih)
    elif lines:
        bx = x + pad
        if bubble:
            bw = max(tw(t, pt) for t in lines) + 28
            out.append(R(key + '/bubble', bx, body_y, bw, len(lines) * lh + 16, prst='roundRect', radius=14, fill=GRAY_FILL, line=None))
            ty = body_y + 8
            tx2 = bx + 14
        else:
            ty = body_y
            tx2 = bx
        for i, t in enumerate(lines):
            out.append(T(key + '/l%d' % i, tx2, ty + i * lh, w - 2 * pad, lh, t, size=pt, color=BODY))
            pos[i] = (tx2, ty + i * lh, t, pt, 'r')
    return out, h, pos


def gallery(key, x, y, w, photos, cols=4, title='갤러리', tag=None, gap=10, ph=None, date_pt=9, show_dates=True, alpha_ph=None):
    """갤러리 카드: 앱 아이콘 + 제목 + 사진 격자(사진마다 아래 날짜). photos = [(파일, 날짜, 초점)]. 돌려줌: (원시, 높이, 사진 자리)."""
    pad = 16
    isz = 30
    rows = (len(photos) + cols - 1) // cols
    pw = (w - 2 * pad - gap * (cols - 1)) / cols
    ph = ph or pw * 0.78
    dh = 20 if show_dates else 0
    top = y + pad + isz + 12
    h = top - y + rows * (ph + dh) + (rows - 1) * gap + pad - 4
    out = [R(key + '/bg', x, y, w, h, prst='roundRect', radius=18, fill='FFFFFF', line=LINE, line_w=1.0, shadow=SHADOW_CARD),
           P(key + '/ic', ICON['gallery'], x + pad, y + pad, isz, isz),
           T(key + '/title', x + pad + isz + 10, y + pad + 3, 200, 24, title, size=13.5, color=INK, weight='b')]
    if tag:
        tg, _ = chip(key + '/tag', x + pad + isz + 18 + tw(title, 13.5, 'b'), y + pad + 3, tag, 'soft', pt=9.5, h=24, padx=10)
        out += tg
    spots = []
    for i, (img, date, focus) in enumerate(photos):
        r_, c_ = divmod(i, cols)
        px = x + pad + c_ * (pw + gap)
        py = top + r_ * (ph + dh + gap)
        out.append(P(key + '/p%d' % i, img, px, py, pw, ph, radius=10, crop=crop_fit(img, pw, ph, focus)))
        if show_dates:
            out.append(T(key + '/d%d' % i, px, py + ph + 3, pw, 16, date, size=date_pt, color=SUB, align='c'))
        spots.append((px, py, pw, ph))
    return out, h, spots


def search_pill(key, x, y, w, h, text, pt=17, icon='mag', cursor=True, text_color=INK, fill='FFFFFF', border=LINE2):
    """검색창: 돋보기(또는 실타래) + 글. 글과 커서는 따로 키(타이핑·깜빡임 효과)."""
    out = [R(key + '/bg', x, y, w, h, prst='roundRect', fill=fill, line=border, line_w=1.6, shadow=SHADOW_CARD)]
    r = h * 0.15
    if icon == 'mag':
        out += magnifier(key + '/mag', x + h * 0.52, y + h / 2 - 2, r=r, color='8E88A0', w=max(2.0, h * 0.04))
        tx = x + h * 0.52 + r * 2.4 + 8
    elif icon == 'spool':
        isz = h * 0.5
        out.append(P(key + '/sp', ICON['spool'], x + h * 0.3, y + (h - isz) / 2, isz, isz))
        tx = x + h * 0.3 + isz + 12
    else:
        tx = x + h * 0.45
    th = pt * 1.33 * 1.4
    txt = T(key + '/q', tx, y + (h - th) / 2, w - (tx - x) - 20, th, text, size=pt, color=text_color, anchor='ctr')
    cx = tx + tw(text, pt) + 3
    cur = R(key + '/cur', cx, y + h / 2 - pt * 0.66, 2.4, pt * 1.32, fill=PURPLE, line=None)
    return out, txt, (cur if cursor else None), tx
