"""모핑(Morph)으로 이어지는 '카메라' 장면 엔진.

한 시나리오 = 세계(world) 좌표에 놓인 기록·메모·실·토큰 + 단계(step) 목록.
단계마다 슬라이드 한 장을 만들고, 카메라(cx, cy, z)로 세계를 비춘 모습을 그린 뒤 모핑 전환을 건다.
같은 요소는 모든 장에서 같은 이름('!!키/부분')을 써서 모핑이 위치·크기·투명도를 부드럽게 잇는다.
머리(칩·자막)와 아래 파이프라인 띠는 카메라와 무관하게 제자리에 있다.
"""
import itertools
import math
from dataclasses import dataclass, field
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
GRAY_HL, GRAY_LINE, GRAY_FILL = 'B4AEC2', 'B9B2C9', 'F3F1F7'
ICON = {'talk': 'app-kakao.png', 'note': 'app-notes.png', 'mail': 'samsung-email-blue.png', 'cal': 'samsung-calendar.png',
        'gallery': 'samsung-gallery.png', 'phone': 'samsung-phone.png', 'map': 'app-map.png', 'spool': 'weave-spool-6B4EFF.png',
        'spool_w': 'weave-spool-white.png', 'wallet': 'samsung-wallet.png', 'google': 'google.png'}

VX, VY = 640, 392            # 카메라 화면의 가운데(머리와 아래 띠 사이)
DIM = 10                     # 흐린 요소의 불투명도(%) — 쓰지 않는 기록은 읽히지 않을 만큼 뒤로
MC = 'http://schemas.openxmlformats.org/markup-compatibility/2006'
P14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
P159 = 'http://schemas.microsoft.com/office/powerpoint/2015/09/main'


# ------------------------------------------------------------------ 세계 요소(원시 도형 목록)
def R(name, x, y, w, h, **o):
    return ('rect', name, x, y, w, h, o)


def T(name, x, y, w, h, paras, **o):
    return ('text', name, x, y, w, h, paras, o)


def P(name, fname, x, y, w, h, **o):
    return ('pic', name, fname, x, y, w, h, o)


def C(name, pts, **o):
    return ('curve', name, pts, o)


def tw(text, pt, weight='r'):
    return L.width(text, pt, weight)


def chip_prims(name, x, y, label, style='outline', pt=9, h=24, padx=11, weight='b', icon=None):
    """알약 칩(세계 좌표). 돌려줌: (원시 목록, 폭)."""
    w = tw(label, pt, weight) + padx * 2 + (18 if icon else 0)
    look = {'fill': (PURPLE, None, 'FFFFFF'), 'outline': ('FFFFFF', LINE2, PURPLE), 'soft': (LAV, None, PURPLE),
            'dash': (LAV2, PURPLE2, PURPLE), 'gray': ('FFFFFF', GRAY_LINE, SUB), 'grayfill': ('EFECF4', None, SUB),
            'white': ('FFFFFF', LINE, INK2)}[style]
    f, ln, col = look
    out = [R(name + '/bg', x, y, w, h, prst='roundRect', fill=f, line=ln, line_w=1.0, dash='dash' if style == 'dash' else None)]
    tx = x + padx
    if icon:
        out.append(P(name + '/ic', ICON[icon], x + padx - 2, y + (h - 15) / 2, 15, 15))
        tx += 18
    out.append(T(name + '/t', tx, y, w, h, label, size=pt, color=col, weight=weight, anchor='ctr'))
    return out, w


FRAG_S = 1.3                 # 흩어진 조각 크기(6차 피드백: 많이 뜰 때 작아 보임 → 1.3배)
FRAG_H = round(46 * FRAG_S)
FRAG_PAD, FRAG_IC, FRAG_GAP = 16, 29, 13
FRAG_PT, FRAG_PT2 = 12.5, 10.5
_IMG_SIZE = {}


def _fit_crop(img, bw, bh):
    """사진을 상자 비율에 맞게 가운데서 잘라냄(늘어나 보이지 않게). 돌려줌: (l, t, r, b) 비율 또는 None."""
    if img not in _IMG_SIZE:
        from PIL import Image
        _IMG_SIZE[img] = Image.open(AS / img).size
    iw, ih = _IMG_SIZE[img]
    ba, ia = bw / bh, iw / ih
    if abs(ba - ia) / ia < 0.01:
        return None
    if ba > ia:                       # 상자가 더 넓음 → 위아래를 자름
        cut = (1 - ia / ba) / 2
        return (0, cut, 0, cut)
    cut = (1 - ba / ia) / 2
    return (cut, 0, cut, 0)
LINK_H = 66


def frag_w(title, meta):
    return FRAG_PAD + FRAG_IC + FRAG_GAP + max(tw(title, FRAG_PT, 'b'), tw(meta, FRAG_PT2)) + 22


def bottle_prims(name, x, y, s):
    """링크 미리보기의 작은 제품 사진: 갈색 유리병(스포이트 뚜껑) + 크림색 라벨. 노란색은 쓰지 않음."""
    bw, bh = s * 0.38, s * 0.5
    bx, by = x + s / 2 - bw / 2, y + s * 0.4
    return [R(name + '/tb', x, y, s, s, prst='roundRect', radius=s * 0.16, fill='F3EEE8', line=None),
            R(name + '/shadow', bx - s * 0.04, by + bh - s * 0.03, bw + s * 0.08, s * 0.06, prst='ellipse', fill='D9D0C6', line=None),
            R(name + '/body', bx, by, bw, bh, prst='roundRect', radius=s * 0.06, fill='6E3417', line=None),
            R(name + '/neck', x + s / 2 - bw * 0.2, by - s * 0.06, bw * 0.4, s * 0.07, fill='4A230F', line=None),
            R(name + '/cap', x + s / 2 - bw * 0.3, by - s * 0.27, bw * 0.6, s * 0.22, prst='roundRect', radius=s * 0.04, fill='1C1A24',
              line=None),
            R(name + '/lab', bx + bw * 0.12, by + bh * 0.3, bw * 0.76, bh * 0.36, fill='F3EBDD', line=None),
            R(name + '/lab1', bx + bw * 0.24, by + bh * 0.4, bw * 0.52, s * 0.025, fill='5A3A22', line=None),
            R(name + '/lab2', bx + bw * 0.3, by + bh * 0.52, bw * 0.4, s * 0.02, fill='8A6A50', line=None),
            R(name + '/shine', bx + bw * 0.1, by + bh * 0.08, bw * 0.09, bh * 0.78, prst='roundRect', fill='FFFFFF', alpha=22, line=None)]


def card_prims(key, kind, x, y, w, title, meta='', lines=(), img=None, icon=None, body_pt=9.5, img_h=None, style='base', link=None):
    """기록 카드. kind: talk·note·mail·cal·shot·photo·pay·call·sms·frag(작은 조각)·link(링크 미리보기 대화).
    돌려줌: (원시 목록, 높이, 글자 자리 정보)."""
    ic = icon or {'photo': 'gallery', 'shot': 'gallery', 'pay': 'talk', 'call': 'phone', 'sms': 'talk', 'pass': 'wallet',
                  'wpay': 'wallet', 'link': 'talk'}.get(kind, kind)
    isz = 22
    tx0 = x + 12 + isz + 9
    out = []
    lines = list(lines)
    border = {'base': (LINE, 0.9, None), 'gray': (GRAY_LINE, 1.5, None), 'weave': (RING, 2.2, None)}[style]
    if kind == 'frag':     # 인트로처럼 흩어져 떠 있는 작은 조각: 아이콘 + 제목 + 한 줄
        w = frag_w(title, meta)
        h = FRAG_H
        tx = x + FRAG_PAD + FRAG_IC + FRAG_GAP
        ty1, ty2 = y + 9, y + 33
        out += [R(key + '/bg', x, y, w, h, prst='roundRect', radius=16, fill='FFFFFF', line=border[0], line_w=border[1],
                  shadow=L.SHADOW_SOFT, glow=(12, RING, 28) if style == 'weave' else None),
                P(key + '/ic', ICON[ic], x + FRAG_PAD, y + (h - FRAG_IC) / 2, FRAG_IC, FRAG_IC),
                T(key + '/title', tx, ty1, w - (tx - x) - 6, 23, title, size=FRAG_PT, color=INK, weight='b'),
                T(key + '/meta', tx, ty2, w - (tx - x) - 6, 18, meta, size=FRAG_PT2, color=MUTE)]
        return out, h, {'title': (tx, ty1, title, FRAG_PT, 'b'), 'meta': (tx, ty2, meta, FRAG_PT2, 'r')}
    if kind == 'link':
        bub = (len(lines) * 17 + 10 + 8) if lines else 0
        h = 34 + bub + LINK_H + 12
    elif kind == 'photo':
        ih = img_h or round((w - 20) * 0.62)
        h = 40 + ih + 10
    elif kind == 'talk' and lines:
        h = 34 + len(lines) * 17 + 10 + 12
    else:
        h = 34 + len(lines) * 17 + (8 if lines else 4)
    out.append(R(key + '/bg', x, y, w, h, prst='roundRect', radius=12, fill='FFFFFF', line=border[0], line_w=border[1],
                 dash=border[2], shadow=L.SHADOW_LIFT if style == 'weave' else L.SHADOW_SOFT,
                 glow=(10, RING, 28) if style == 'weave' else None))
    out.append(P(key + '/ic', ICON[ic], x + 12, y + 10, isz, isz))
    out.append(T(key + '/title', tx0, y + 10, w - (tx0 - x) - 12, 20, title, size=10.5, color=INK, weight='b'))
    if meta:
        mw = tw(meta, 8.5) + 2
        out.append(T(key + '/meta', x + w - 12 - mw, y + 13, mw + 2, 16, meta, size=8.5, color=MUTE))
    pos = {}
    if kind == 'photo':
        out.append(P(key + '/img', img, x + 10, y + 40, w - 20, ih, radius=8, crop=_fit_crop(img, w - 20, ih)))
        pos['img'] = (x + 10, y + 40, w - 20, ih)
    elif kind in ('talk', 'link') and lines:
        bw = max(tw(t, body_pt) for t in lines) + 18
        out.append(R(key + '/bubble', tx0, y + 34, bw, len(lines) * 17 + 10, prst='roundRect', radius=9, fill=GRAY_FILL, line=None))
        for i, t in enumerate(lines):
            out.append(T(key + '/l%d' % i, tx0 + 9, y + 39 + i * 17, bw, 17, t, size=body_pt, color=BODY))
            pos[i] = (tx0 + 9, y + 39 + i * 17, t, body_pt, 'r')
    elif kind != 'link':
        for i, t in enumerate(lines):
            out.append(T(key + '/l%d' % i, tx0, y + 34 + i * 17, w - (tx0 - x) - 10, 17, t, size=body_pt, color=BODY))
            pos[i] = (tx0, y + 34 + i * 17, t, body_pt, 'r')
    if kind == 'link':     # 링크 미리보기: 제품 사진 + 제품 이름(굵게) + 사이트
        ly = y + 34 + bub
        lw = w - (tx0 - x) - 12
        out.append(R(key + '/lk', tx0, ly, lw, LINK_H, prst='roundRect', radius=10, fill='FFFFFF', line=LINE2, line_w=1.0))
        out += bottle_prims(key + '/th', tx0 + 8, ly + 8, LINK_H - 16)
        lx = tx0 + LINK_H
        for i, t in enumerate(link['title']):
            out.append(T(key + '/k%d' % i, lx, ly + 8 + i * 16, lw - (lx - tx0) - 6, 16, t, size=9.5, color=INK, weight='b'))
            pos['k%d' % i] = (lx, ly + 8 + i * 16, t, 9.5, 'b')
        out.append(T(key + '/site', lx, ly + LINK_H - 21, lw - (lx - tx0) - 6, 14, link.get('site', ''), size=8, color=MUTE))
    pos['title'] = (tx0, y + 10, title, 10.5, 'b')
    if meta:
        pos['meta'] = (x + w - 12 - mw, y + 13, meta, 8.5, 'r')
    return out, h, pos


def band(pos, sub, kind='low', start=0):
    """글자 위 형광펜 자리(세계 좌표). pos = (x, y, 글자, pt). PowerPoint 실측: 한글은 y+0.12S~y+1.0S."""
    x, y, text, pt, wt = pos
    i = text.index(sub, start)
    ox, w = tw(text[:i], pt, wt), tw(sub, pt, wt)
    S = pt * 4 / 3
    if kind == 'low':
        return x + ox - 1.5, y + S * 0.56, w + 3, S * 0.52
    return x + ox - 2, y + S * 0.02, w + 4, S * 1.12


def thread_prims(name, pts, w=2.6):
    return [C(name + '/under', pts, w=w + 3.6, color='FFFFFF', alpha=92),
            C(name + '/line', pts, w=w)]


def scurve(a, b, k=0.5):
    """a→b 가로로 흐르는 S자 곡선 조절점."""
    (x0, y0), (x1, y1) = a, b
    dx = (x1 - x0) * k
    return [a, (x0 + dx, y0), (x1 - dx, y1), b]


def vcurve(a, b, k=0.5):
    (x0, y0), (x1, y1) = a, b
    dy = (y1 - y0) * k
    return [a, (x0, y0 + dy), (x1, y1 - dy), b]


# ------------------------------------------------------------------ 단계
@dataclass
class Step:
    title: list                      # [(글자, 색)] 머리 제목
    sub: str = ''
    cam: tuple = (640, 392, 1.0)     # (cx, cy, z) — 세계 좌표 cx,cy가 화면 가운데(VX,VY)에 오고 z배
    show: list = field(default_factory=list)       # 보이는 요소 키(그린 순서 = 겹침 순서)
    focus: object = None             # None이면 모두 또렷, 집합이면 그 밖은 흐리게
    styles: dict = field(default_factory=dict)     # 키 → 카드 모양(base·gray·weave)
    hud: object = None               # None이면 띠 없음, dict(cur='02', done={'00','01'}, loop=1)
    anim: dict = field(default_factory=dict)       # 키 → 전환 뒤 효과(dict(kind, delay, dur, dir))
    notes: str = ''
    morph_ms: int = 1300


class Story:
    def __init__(self, name, assets=()):
        self.name = name
        self.items = {}              # 키 → 함수(style) → 원시 목록
        self.steps = []

    def item(self, key, fn):
        self.items[key] = fn

    def step(self, **kw):
        self.steps.append(Step(**kw))


# ------------------------------------------------------------------ 그리기
class Painter:
    def __init__(self, slide):
        self.slide = slide
        self.part = slide.part
        self.ids = itertools.count(10)
        self.rids = {}
        self.tree = slide.shapes._spTree

    def sid(self):
        return next(self.ids)

    def rid(self, fname):
        if fname not in self.rids:
            _, r = self.part.get_or_add_image_part(str(AS / fname))
            self.rids[fname] = r
        return self.rids[fname]

    def add(self, e):
        self.tree.append(e)
        return e

    def prim(self, p, cam=None, alpha=100):
        """원시 도형 하나를 (카메라 변환 + 투명도) 적용해 그림."""
        if cam and len(cam) == 5:
            cx, cy, z, vx, vy = cam
        else:
            cx, cy, z = cam if cam else (VX, VY, 1.0)
            vx, vy = VX, VY

        def X(v):
            return (v - cx) * z + vx

        def Y(v):
            return (v - cy) * z + vy

        a = alpha / 100.0
        kind, name = p[0], '!!' + p[1]
        if kind == 'rect':
            _, _, x, y, w, h, o = p
            fa = o.get('alpha', 100) * a if o.get('fill', 'FFFFFF') else None
            la = o.get('line_alpha', 100) * a
            shadow = o.get('shadow') if a > 0.6 else None
            glow = o.get('glow') if a > 0.6 else None
            e = L.shape(self.sid(), name, X(x), Y(y), w * z, h * z, prst=o.get('prst', 'rect'),
                        radius=(o['radius'] * z) if o.get('radius') is not None else None,
                        fill=o.get('fill', 'FFFFFF'), alpha=None if fa is None or fa >= 99.9 else fa,
                        line=o.get('line'), line_w=max(0.6, o.get('line_w', 0.75) * z),
                        line_alpha=None if la >= 99.9 else la, dash=o.get('dash'), shadow=shadow, glow=glow,
                        grad_fill=o.get('grad'), soft=o.get('soft'))
            return self.add(e)
        if kind == 'text':
            _, _, x, y, w, h, paras, o = p
            ta = o.get('alpha', 100) * a
            sz = o.get('size', 10) * z
            e = L.text(self.sid(), name, X(x), Y(y), w * z, h * z, paras, size=sz, color=o.get('color', INK),
                       weight=o.get('weight', 'r'), align=o.get('align', 'l'), anchor=o.get('anchor', 't'),
                       pen=o.get('pen', False), alpha=None if ta >= 99.9 else ta, spc=o.get('spc', 0) * z,
                       lnspc=(o['lnspc'] * z) if o.get('lnspc') else None, wrap=o.get('wrap', False))
            # 문단 안 조각별 크기도 배율 반영
            if z != 1.0:
                for r in e.iter(q('a:rPr'), q('a:endParaRPr')):
                    pass
            return self.add(e)
        if kind == 'pic':
            _, _, fname, x, y, w, h, o = p
            pa = o.get('alpha', 100) * a
            e = L.picture(self.sid(), name, self.rid(fname), X(x), Y(y), w * z, h * z, crop=o.get('crop'),
                          radius=(o['radius'] * z) if o.get('radius') else None,
                          alpha=None if pa >= 99.9 else pa)
            return self.add(e)
        if kind == 'curve':
            _, _, pts, o = p
            ca = o.get('alpha', 100) * a
            tp = [(X(px), Y(py)) for px, py in pts]
            e = L.curve(self.sid(), name, tp, w=max(0.8, o.get('w', 2.4) * z), color=o.get('color'),
                        alpha=None if ca >= 99.9 else ca, dash=o.get('dash'), tail=o.get('tail'),
                        stops=[(0, 'B597FF', None if ca >= 99.9 else ca), (100, '6B4EFF', None if ca >= 99.9 else ca)])
            return self.add(e)
        raise ValueError(kind)


def morph_transition(slide, ms):
    x = ('<mc:AlternateContent xmlns:mc="%s" xmlns:p="%s" xmlns:p14="%s"><mc:Choice xmlns:p159="%s" Requires="p159">'
         '<p:transition spd="slow" p14:dur="%d"><p159:morph option="byObject"/></p:transition></mc:Choice>'
         '<mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>') % (
        MC, L.NS['p'], P14, P159, ms)
    el = etree.fromstring(x)
    sld = slide._element
    for old in sld.findall(q('p:transition')):
        sld.remove(old)
    for old in sld.findall('{%s}AlternateContent' % MC):
        sld.remove(old)
    sld.find(q('p:clrMapOvr')).addnext(el)
