#!/usr/bin/env python3
"""9쪽 HOW IT WORKS 새 장표 — 발표자가 클릭 10번으로 넘기는 한 장.

  python build_hiw.py           out/HowItWorks.pptx            한 장(클릭 애니메이션 + 발표자 노트)
                                out/HowItWorks_자동재생.pptx     클릭 없이 저절로 넘어가는 판(미리보기 영상용)
                                out/HowItWorks_단계확인.pptx     클릭 0~10 상태를 한 장씩 정적으로(렌더 확인용)
  python build_hiw.py --deck    out/Weave_결선_HIW검토.pptx      작업 덱 사본에서 9쪽만 이 장표로 바꾼 검토용
                                (02_PPT/Weave_결선.pptx 원본은 건드리지 않음)

시나리오(고도화한 와인): "지은이네 집들이 때 마신 화이트 와인" — 캘린더엔 일정이 없고, 3/12(목) 지은의 카톡
"이번 일요일 6시, 이사 기념으로 우리 집에서 저녁 먹자!"만 남아 있음('집들이'라는 말이 없음). 그날(3/15 일) 저녁 사진 두 장
(레드 19:52, 화이트 20:14) 중 라벨 'SAUVIGNON BLANC'이 화이트임을 추론해 '배비치 소비뇽 블랑'을 출처와 함께 건넴.
"""
import argparse
import copy
import itertools
import shutil
from pathlib import Path

from lxml import etree
from pptx import Presentation

import hiw_lib as L
from hiw_lib import q

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                                   # weave/결선준비
DECK = ROOT / '02_PPT' / 'Weave_결선.pptx'
SLIDE_NO = 9
AS = HERE / 'assets'
OUT = HERE / 'out'

# 색 (덱 9쪽과 인트로에서 그대로)
INK, INK2, BODY, SUB, MUTE = '1C1A24', '2B2640', '4E4A57', '6A6474', '8E88A0'
LINE, LINE2 = 'E6E0F5', 'CFC3FF'
PURPLE, PURPLE2, RING, HL = '6B4EFF', '8B6BFF', '8B68F5', 'A67CF2'
LAV, LAV2 = 'F1ECFF', 'F7F4FF'
GRAY_HL, GRAY_LINE, GRAY_FILL = 'B4AEC2', 'B9B2C9', 'F3F1F7'
VEIL = 'FBFAFF'

ICON = {'talk': 'app-kakao.png', 'note': 'app-notes.png', 'mail': 'samsung-email-blue.png',
        'cal': 'samsung-calendar.png', 'gallery': 'samsung-gallery.png', 'spool': 'weave-spool-6B4EFF.png'}

# ------------------------------------------------------------------ 기록 벽 (x, y, w는 px)
WALL = (304, 186, 640, 454)
CARDS = {
    'N1': dict(kind='note', x=318, y=200, w=160, title='와인 메모', meta='2/28', lines=['달지 않은 화이트로']),
    'S1': dict(kind='shot', x=494, y=196, w=212, title='스크린샷', meta='3/10', lines=['집들이 선물 와인 BEST 5']),
    'A1': dict(kind='talk', x=392, y=292, w=236, title='지은', meta='3/12 (목)',
               lines=['이번 일요일 6시, 이사 기념으로', '우리 집에서 저녁 먹자!']),
    'E1': dict(kind='mail', x=318, y=398, w=160, title='[쿠팡] 배송 완료', meta='3/9', lines=['와인잔 4개입']),
    'K3': dict(kind='talk', x=494, y=404, w=172, title='팀 단톡방', meta='3/20', lines=['회식은 와인바 어때요?']),
    'C1': dict(kind='photo', x=724, y=200, w=206, title='갤러리', meta='3/15 (일) 19:52', img='photo-red.jpg'),
    'C2': dict(kind='photo', x=724, y=430, w=206, title='갤러리', meta='3/15 (일) 20:14', img='photo-white.jpg'),
    'Cal1': dict(kind='cal', x=318, y=462, w=160, title='지은 생일', meta='7/2 (목) · 종일'),
    'N2': dict(kind='note', x=494, y=480, w=172, title='장보기', meta='3/14', lines=['우유, 계란, 치즈']),
    'E2': dict(kind='mail', x=318, y=518, w=160, title='호텔 예약 확인', meta='2/27', lines=['오사카 · 4/3–4/5']),
    'Cal2': dict(kind='cal', x=494, y=546, w=172, title='팀 회의', meta='3/16 (월) 10:00'),
    'G3': dict(kind='cal', x=318, y=582, w=160, title='사진 3장', meta='3/8 (일) 13:02', icon='gallery'),
    'Cal3': dict(kind='cal', x=724, y=370, w=206, title='치과 예약', meta='3/22 (일) 10:30'),
}
LINE_STEP = 15          # 카드 본문 줄 간격(px)


def card_h(c):
    if c['kind'] == 'photo':
        return 34 + 116 + 10
    if c['kind'] == 'cal':
        return 46
    if c['kind'] == 'talk':
        return 30 + len(c['lines']) * LINE_STEP + 8 + 10
    return 30 + len(c['lines']) * LINE_STEP + 8


for _c in CARDS.values():
    _c['h'] = card_h(_c)
    _c['y'] += 6                     # 벽 이름표와 순위 배지가 겹치지 않게 전체를 조금 내림


class Deck:
    """한 슬라이드에 도형을 쌓으며, 클릭 단계별 등장·퇴장과 추가 효과를 모아 둠."""

    def __init__(self, slide, state=None):
        self.slide, self.part, self.state = slide, slide.part, state
        self.ids = itertools.count(10)
        self.items = []          # [element, show, hide, enter, exit]
        self.extra = []          # (step, kind, element, kw)
        self.rids = {}

    def sid(self):
        return next(self.ids)

    def rid(self, fname):
        if fname not in self.rids:
            _, r = self.part.get_or_add_image_part(str(AS / fname))
            self.rids[fname] = r
        return self.rids[fname]

    def add(self, e, show=0, hide=None, enter=None, exit=None):
        self.items.append([e, show, hide, enter or {}, exit or {}])
        return e

    def fx(self, step, kind, e, **kw):
        self.extra.append((step, kind, e, kw))

    # -------------------------------------------------------------- 출력
    def visible(self, show, hide, s):
        return show <= s and (hide is None or hide > s)

    def write(self, timing=True, auto=None):
        tree = self.slide.shapes._spTree
        for c in list(tree)[2:]:
            tree.remove(c)
        keep = []
        for e, show, hide, enter, exit in self.items:
            if self.state is not None and not self.visible(show, hide, self.state):
                continue
            tree.append(e)
            keep.append((e, show, hide, enter, exit))
        sld = self.slide._element
        for old in sld.findall(q('p:timing')):
            sld.remove(old)
        if self.state is not None or not timing:
            return
        tl = L.Timeline()
        OFF = 1600          # px. 잠깐 나왔다 사라지는 도형(1~3번 비교, 중간 단계)은 슬라이드 오른쪽 밖에 두고 그 클릭에서 순간 이동

        nsteps = max([s for _, s, _, _, _ in keep] + [h or 0 for _, _, h, _, _ in keep] + [s for s, *_ in self.extra])
        events = {k: [] for k in range(1, nsteps + 1)}
        spid = lambda e: int(e.find('.//' + q('p:cNvPr')).get('id'))
        for e, show, hide, enter, exit in keep:
            if show > 0:
                d = dict(kind='fade_in', delay=0, dur=400)
                d.update(enter)
                dl = d.pop('delay')
                events[show].append((dl, d.pop('kind'), spid(e), d))
                if hide is not None:
                    xf = e.find(q('p:spPr') + '/' + q('a:xfrm'))
                    if xf is None:
                        xf = e.find(q('p:grpSpPr') + '/' + q('a:xfrm'))
                    off = xf.find(q('a:off'))
                    off.set('x', str(int(off.get('x')) + OFF * L.PX))
                    events[show].append((dl, 'move', spid(e), dict(dur=10, dx=-OFF, dy=0)))
            if hide is not None:
                d = dict(kind='fade_out', delay=0, dur=280)
                d.update(exit)
                events[hide].append((d.pop('delay'), d.pop('kind'), spid(e), d))
        for step, kind, e, kw in self.extra:
            kw = dict(kw)
            events[step].append((kw.pop('delay', 0), kind, spid(e), kw))
        for k in range(1, nsteps + 1):
            tl.step()
            for delay, kind, sp, kw in sorted(events[k], key=lambda t: t[0]):
                dur = kw.pop('dur', 400)
                tl.add(kind, sp, delay=delay, dur=dur, **kw)
        sp_ids = {spid(e) for e, *_ in keep if e.tag == q('p:sp')}
        timing_el = tl.xml(sp_ids, auto=auto)
        # p:sld 안 순서: cSld, clrMapOvr, transition, timing, extLst
        ext = sld.find(q('p:extLst'))
        if ext is not None:
            ext.addprevious(timing_el)
        else:
            sld.append(timing_el)
        self.timeline = tl


# ------------------------------------------------------------------ 글자 자리
def span(text, sub, pt, weight='r', start=0):
    """한 줄 글자에서 sub가 시작하는 x(px)와 폭."""
    i = text.index(sub, start)
    return L.width(text[:i], pt, weight), L.width(sub, pt, weight)


def band(x, y, text, sub, pt, weight='r', kind='full', start=0):
    """형광펜 자리 (x, y, w, h). kind='full'은 글자 높이 전체, 'low'는 글자 아래쪽 띠(인트로 형광펜)."""
    ox, w = span(text, sub, pt, weight, start)
    S = pt * 4 / 3
    if kind == 'low':
        return x + ox - 1.5, y + S * 0.56, w + 3, S * 0.52
    return x + ox - 2, y + S * 0.02, w + 4, S * 1.12


# ------------------------------------------------------------------ 카드
def card(d, key, style='base', scale=1.0, marks=(), split=False, name=None):
    """기록 카드. style: base(벽) · gray(기존 방식이 집은 카드) · weave(Weave가 찾은 카드).
    scale: 가운데 기준 배율(포커스 복제 1.07). marks: [(줄 번호|'title', 글자)] 회색 형광펜(카드 안).
    split=True면 (바탕 묶음, 글자 묶음)을 따로 돌려줌 — 사이에 보라 형광펜을 끼우려고."""
    c = CARDS[key]
    x, y, w, h = c['x'], c['y'], c['w'], c['h']
    cx, cy = x + w / 2, y + h / 2
    s = scale

    def X(v):
        return cx + (v - cx) * s

    def Y(v):
        return cy + (v - cy) * s

    nm = name or ('%s_%s' % (key, style))
    bg_parts, tx_parts = [], []
    line, lw, shadow, glow = LINE, 0.75, L.SHADOW_SOFT, None
    if style == 'gray':
        line, lw, shadow = GRAY_LINE, 1.0, L.SHADOW_CARD
    if style == 'weave':
        line, lw, shadow, glow = RING, 2.0, L.SHADOW_LIFT, (9, RING, 30)
    bg_parts.append(L.shape(d.sid(), nm + ' 바탕', X(x), Y(y), w * s, h * s, prst='roundRect', radius=11 * s,
                            fill='FFFFFF', line=line, line_w=lw, shadow=shadow, glow=glow,
                            dash='dash' if style == 'gray' else None))
    isz = 20 if c['kind'] != 'photo' else 18
    bg_parts.append(L.picture(d.sid(), nm + ' 아이콘', d.rid(ICON[c.get('icon') or ('gallery' if c['kind'] in ('photo', 'shot') else c['kind'])]),
                              X(x + 10), Y(y + 9), isz * s, isz * s))
    tx0 = x + 10 + isz + 8
    title_pt = 9 if c['kind'] != 'talk' else 9.5
    tx_parts.append(L.text(d.sid(), nm + ' 제목', X(tx0), Y(y + 9), 150 * s, 16 * s, c['title'], size=title_pt * s,
                           color=INK, weight='b'))
    meta_pt = 7.5
    mw = L.width(c['meta'], meta_pt) + 2
    if c['kind'] == 'cal':
        tx_parts.append(L.text(d.sid(), nm + ' 날짜', X(tx0), Y(y + 26), 150 * s, 14 * s, c['meta'], size=8 * s, color=SUB))
    else:
        tx_parts.append(L.text(d.sid(), nm + ' 날짜', X(x + w - 10 - mw), Y(y + 11), mw * s, 13 * s, c['meta'],
                               size=meta_pt * s, color=MUTE))
    body_pt = 8.5 if key != 'A1' else 9
    lines = c.get('lines', [])
    if c['kind'] == 'talk' and lines:
        bw = max(L.width(t, body_pt) for t in lines) + 16
        bh = len(lines) * LINE_STEP + 8
        bg_parts.append(L.shape(d.sid(), nm + ' 말풍선', X(tx0), Y(y + 29), bw * s, bh * s, prst='roundRect', radius=8 * s,
                                fill=GRAY_FILL, line=None))
        bx = tx0 + 8
        by0 = y + 32
    else:
        bx = tx0
        by0 = y + 28
    for i, t in enumerate(lines):
        tx_parts.append(L.text(d.sid(), nm + ' 본문%d' % (i + 1), X(bx), Y(by0 + i * LINE_STEP), 190 * s, 15 * s, t,
                               size=body_pt * s, color=BODY))
    if c['kind'] == 'photo':
        bg_parts.append(L.picture(d.sid(), nm + ' 사진', d.rid(c['img']), X(x + 10), Y(y + 34), (w - 20) * s, 116 * s,
                                  radius=7 * s))
    # 회색 형광펜(카드 안, 글자 뒤)
    mk = []
    for where, sub in marks:
        if where == 'title':
            bx_, by_, t_, pt_, wt_ = tx0, y + 9, c['title'], title_pt, 'b'
        else:
            bx_, by_, t_, pt_, wt_ = bx, by0 + where * LINE_STEP, lines[where], body_pt, 'r'
        mx, my, mw_, mh = band(bx_, by_, t_, sub, pt_, wt_)
        mk.append(L.shape(d.sid(), nm + ' 회색 표시', X(mx), Y(my), mw_ * s, mh * s, prst='roundRect', radius=3 * s,
                          fill=GRAY_HL, alpha=34, line=None))
    if split:
        return (L.group(d.sid(), nm + ' 바탕묶음', bg_parts + mk), L.group(d.sid(), nm + ' 글자묶음', tx_parts))
    return L.group(d.sid(), nm, bg_parts + mk + tx_parts)


def card_text_pos(key, line=None, scale=1.0):
    """보라 형광펜 계산용: (글자 x, 글자 y, 글자, pt) — 배율 반영 전 좌표와 배율 함수."""
    c = CARDS[key]
    isz = 20
    tx0 = c['x'] + 10 + isz + 8
    if c['kind'] == 'talk':
        return tx0 + 8, c['y'] + 32
    return tx0, c['y'] + 28


def scaled(key, s):
    c = CARDS[key]
    cx, cy = c['x'] + c['w'] / 2, c['y'] + c['h'] / 2
    return (lambda v: cx + (v - cx) * s), (lambda v: cy + (v - cy) * s)


def chip(d, name, x, y, label, style='outline', pt=8.5, h=22, padx=10, weight='b', icon=None, dash=None):
    """알약 칩. style: fill(보라 채움) · outline(흰 바탕 보라 테두리) · soft(연보라) · dash(새 단서 자리) · gray."""
    w = L.width(label, pt, weight) + padx * 2 + (16 if icon else 0)
    fills = {'fill': (PURPLE, None, 'FFFFFF'), 'outline': ('FFFFFF', LINE2, PURPLE), 'soft': (LAV, None, PURPLE),
             'dash': (LAV2, PURPLE2, PURPLE), 'gray': ('FFFFFF', GRAY_LINE, SUB), 'grayfill': ('EFECF4', None, SUB)}
    f, ln, col = fills[style]
    parts = [L.shape(d.sid(), name + ' 바탕', x, y, w, h, prst='roundRect', fill=f, line=ln, line_w=0.9,
                     dash=dash or ('dash' if style == 'dash' else None))]
    tx = x + padx
    if icon:
        parts.append(L.picture(d.sid(), name + ' 아이콘', d.rid(icon), x + padx - 2, y + (h - 13) / 2, 13, 13))
        tx += 16
    parts.append(L.text(d.sid(), name + ' 글자', tx, y, w, h, label, size=pt, color=col, weight=weight, anchor='ctr'))
    return L.group(d.sid(), name, parts), w


def thread(d, name, pts, w=2.4):
    """인트로와 같은 실: 흰 테두리(아래) + 보라 그라데이션(위)."""
    under = L.curve(d.sid(), name + ' 테두리', pts, w=w + 3.6, color='FFFFFF', alpha=92)
    top = L.curve(d.sid(), name + ' 실', pts, w=w, stops=[(0, 'B597FF', None), (100, '6B4EFF', None)])
    return L.group(d.sid(), name, [under, top])


def hl_group(d, name, rects, color=HL, alpha=42):
    return L.group(d.sid(), name, [L.shape(d.sid(), name + ' %d' % i, *r, prst='roundRect', radius=2.5, fill=color,
                                           alpha=alpha, line=None) for i, r in enumerate(rects)])


def tag(d, name, x, y, label, style='gray', pt=8, h=19, anchor='l'):
    g, w = chip(d, name, x, y, label, style=style, pt=pt, h=h, padx=8, weight='sb')
    if anchor == 'r':
        g, w = chip(d, name, x - w, y, label, style=style, pt=pt, h=h, padx=8, weight='sb')
    return g, w


# ------------------------------------------------------------------ 장표
def compose(slide, state=None, header=None):
    d = Deck(slide, state)
    S, A = d.sid, d.add

    # 배경: 덱 9쪽과 같은 바탕 + 보라 빛 번짐 두 개(오른쪽 위 노랑 → 보라로 교체)
    A(L.shape(S(), '배경', 0, 0, 1280, 720, fill=None,
              grad_fill=dict(stops=[(0, 'FDFCFF', None), (50, 'F8F5FF', None), (100, 'F2EDFF', None)], ang=70)))
    A(L.shape(S(), '빛 번짐 오른쪽 위', 640, 0, 640, 507, fill=None,
              grad_fill=dict(stops=[(0, 'C6B3FF', 30), (30, 'DED3FF', 14), (60, 'F8F5FF', 0)], path='circle',
                             rect=(85, 8, 15, 92))))
    A(L.shape(S(), '빛 번짐 왼쪽 아래', 0, 373, 600, 347, fill=None,
              grad_fill=dict(stops=[(0, 'BAA6FF', 34), (40, 'DCD0FF', 16), (72, 'F8F5FF', 0)], path='circle',
                             rect=(12, 88, 88, 12))))
    for h in header or []:
        h = copy.deepcopy(h)
        h.find('.//' + q('p:cNvPr')).set('id', str(S()))
        A(h)

    # ---------------------------------------------------------- 왼쪽: 질문
    qx, qy, qw, qh = 48, 186, 240, 76
    A(L.shape(S(), '질문 카드', qx, qy, qw, qh, prst='roundRect', radius=16, fill='FFFFFF', line=LINE2, line_w=1.0,
              shadow=L.SHADOW_CARD))
    A(L.picture(S(), '질문 실타래', d.rid(ICON['spool']), qx + 13, qy + 14, 20, 20))
    Q1, Q2, QPT = '지은이네 집들이 때 마신', '화이트 와인', 11.5
    q1x, q1y, q2y = qx + 42, qy + 14, qy + 39
    A(L.text(S(), '질문 1', q1x, q1y, 190, 20, Q1, size=QPT, color=INK, weight='m'))
    A(L.text(S(), '질문 2', q1x, q2y, 120, 20, Q2, size=QPT, color=INK, weight='m'))
    A(L.shape(S(), '질문 보내기', qx + qw - 38, qy + qh - 36, 26, 26, prst='ellipse', fill=PURPLE, line=None))
    A(L.text(S(), '질문 보내기 화살표', qx + qw - 38, qy + qh - 36, 26, 26, '↑', size=11, color='FFFFFF', weight='b',
             align='c', anchor='ctr'))

    # ---------------------------------------------------------- 가운데: 기록 벽
    wx, wy, ww, wh = WALL
    A(L.shape(S(), '기록 벽', wx, wy, ww, wh, prst='roundRect', radius=18, fill=LAV, alpha=38, line='B7A6FF', dash='dash'))
    for key in CARDS:
        A(card(d, key))
    # 사진 위 라벨 글자(빨강 와인 라벨에는 실제 글자가 없어서, 작게 얹어 둠 — 사진 위 글자도 PowerPoint 글자)
    # (사진이 작아 읽히지 않을 크기라 생략)

    # 베일: 기록 벽만 흐리게
    veil = A(L.shape(S(), '베일', wx, wy, ww, wh, prst='roundRect', radius=18, fill=VEIL, alpha=70, line=None),
             show=1, enter=dict(dur=450))
    t_a, t_b = '내 폰 속 기록', '사람·시간·장소·사진 속 글자로 미리 정리'
    wa, wb = L.width(t_a, 8.5, 'b'), L.width(t_b, 8)
    lx, ly = wx + 14, wy - 11
    A(L.group(S(), '기록 벽 이름', [
        L.shape(S(), '기록 벽 이름 바탕', lx, ly, wa + wb + 34, 22, prst='roundRect', fill='FFFFFF', line='B7A6FF', line_w=0.9),
        L.text(S(), '기록 벽 이름 글자', lx + 11, ly, wa + 4, 22, t_a, size=8.5, color=PURPLE, weight='b', anchor='ctr'),
        L.shape(S(), '기록 벽 이름 점', lx + 11 + wa + 6, ly + 10, 2.4, 2.4, prst='ellipse', fill='B7A6FF', line=None),
        L.text(S(), '기록 벽 이름 설명', lx + 11 + wa + 13, ly, wb + 4, 22, t_b, size=8, color=MUTE, anchor='ctr')]))

    # ---------------------------------------------------------- 1 · 단어로 찾기
    gm = []
    for t, y_, sub in ((Q1, q1y, '집들이'), (Q2, q2y, '화이트'), (Q2, q2y, '와인')):
        gm.append(band(q1x, y_, t, sub, QPT, 'm'))
    A(hl_group(d, '1 질문 단어 표시', gm, color=GRAY_HL, alpha=40), show=1, hide=2,
      enter=dict(kind='wipe_in', dir='left', delay=100, dur=400))
    p1 = [L.shape(S(), '1 읽기 바탕', 48, 276, 240, 62, prst='roundRect', radius=12, fill='FFFFFF', alpha=82,
                  line=GRAY_LINE, dash='dash'),
          L.text(S(), '1 읽기 제목', 62, 284, 200, 14, '단어로 찾기 · 글자 그대로', size=8, color=MUTE, weight='sb')]
    cx_ = 62
    for wd in ('집들이', '화이트', '와인'):
        g, w_ = chip(d, '1 단어 ' + wd, cx_, 306, wd, style='gray', pt=8.5, h=22)
        p1.append(g)
        cx_ += w_ + 6
    A(L.group(S(), '1 질문 읽기', p1), show=1, hide=2, enter=dict(kind='rise', delay=150, dur=450))
    f1 = [card(d, 'S1', 'gray', 1.07, marks=[(0, '집들이'), (0, '와인')], name='1 S1'),
          card(d, 'N1', 'gray', 1.07, marks=[('title', '와인'), (0, '화이트')], name='1 N1'),
          card(d, 'E1', 'gray', 1.07, marks=[(0, '와인')], name='1 E1'),
          card(d, 'K3', 'gray', 1.07, marks=[(0, '와인')], name='1 K3')]
    A(L.group(S(), '1 걸린 카드', f1), show=1, hide=2, enter=dict(delay=350, dur=420))
    a1 = CARDS['A1']
    c2 = CARDS['C2']
    t1, _ = tag(d, '1 놓친 이유 A1', a1['x'] + a1['w'] - 6, a1['y'] - 9, "‘집들이’라는 말이 없음", anchor='r')
    t2, _ = tag(d, '1 놓친 이유 C2', c2['x'] + c2['w'] - 6, c2['y'] - 9, "‘화이트’라는 글자 없음", anchor='r')
    A(L.group(S(), '1 놓친 이유', [t1, t2]), show=1, hide=2, enter=dict(delay=700, dur=300))

    # ---------------------------------------------------------- 오른쪽: 같은 질문, 다른 답
    RX, RW = 960, 272
    rows = [
        ('단어로 찾기', '예: 키워드 검색', "→ ‘집들이 선물 와인 BEST 5’ · 와인 메모", "초대엔 ‘집들이’, 라벨엔 ‘화이트’가 없어요"),
        ('관계로 찾기', '예: PDE 방식¹', '→ 이어진 일정 없음', '저장해 둔 사실만 이어요 · 약속은 카톡에만'),
        ('비슷한 것 찾기', '예: 일반 임베딩', "→ ‘BEST 5’ 캡처 · 지은의 카톡 …", '한 번 찾고 끝 · 단서를 따라가지 못해요'),
    ]
    row_els = []
    for i, (lab_, ex, res, why) in enumerate(rows):
        ry = 186 + i * 84
        lw_ = L.width(lab_, 10, 'b')
        parts = [L.shape(S(), '답 %d 바탕' % (i + 1), RX, ry, RW, 74, prst='roundRect', radius=12, fill='FFFFFF',
                         line=LINE, shadow=L.SHADOW_SOFT),
                 L.shape(S(), '답 %d 표시' % (i + 1), RX + RW - 30, ry + 10, 18, 18, prst='ellipse', fill='EFECF4', line=None),
                 L.text(S(), '답 %d 표시 글자' % (i + 1), RX + RW - 30, ry + 10, 18, 18, '✕', size=7.5, color=MUTE,
                        weight='b', align='c', anchor='ctr'),
                 L.text(S(), '답 %d 방식' % (i + 1), RX + 16, ry + 10, 160, 18, lab_, size=10, color=INK2, weight='b'),
                 L.text(S(), '답 %d 예' % (i + 1), RX + 16 + lw_ + 7, ry + 12.5, 120, 14, ex, size=8, color=MUTE),
                 L.text(S(), '답 %d 결과' % (i + 1), RX + 16, ry + 33, 240, 15, res, size=8.5, color=BODY),
                 L.text(S(), '답 %d 막힘' % (i + 1), RX + 16, ry + 51, 240, 15, why, size=8.5, color=SUB, weight='sb')]
        row_els.append(L.group(S(), '답 %d' % (i + 1), parts))
    A(row_els[0], show=1, enter=dict(kind='rise', delay=850, dur=450))

    # ---------------------------------------------------------- 2 · 관계로 찾기
    rm = [band(q1x, q1y, Q1, '지은', QPT, 'm'), band(q1x, q1y, Q1, '집들이', QPT, 'm')]
    A(hl_group(d, '2 질문 관계 표시', rm, color=GRAY_HL, alpha=40), show=2, hide=3,
      enter=dict(kind='wipe_in', dir='left', delay=200, dur=400))
    p2 = [L.shape(S(), '2 읽기 바탕', 48, 276, 240, 62, prst='roundRect', radius=12, fill='FFFFFF', alpha=82,
                  line=GRAY_LINE, dash='dash'),
          L.text(S(), '2 읽기 제목', 62, 284, 200, 14, '관계로 찾기 · 저장된 관계를 따라', size=8, color=MUTE, weight='sb')]
    g, w_ = chip(d, '2 지은', 62, 306, '지은', style='gray', pt=8.5, h=22)
    p2.append(g)
    g2, w2 = chip(d, '2 집들이 일정', 62 + w_ + 34, 306, '집들이 일정 ?', style='gray', pt=8.5, h=22, dash='dash')
    p2.append(L.shape(S(), '2 관계선', 62 + w_ + 4, 316.5, 26, 1.2, fill=GRAY_LINE, line=None))
    p2.append(g2)
    p2.append(L.text(S(), '2 없음', 62 + w_ + 34 + w2 + 6, 306, 40, 22, '없음', size=8, color=MUTE, weight='sb', anchor='ctr'))
    A(L.group(S(), '2 질문 읽기', p2), show=2, hide=3, enter=dict(kind='rise', delay=250, dur=450))
    f2 = [card(d, 'Cal1', 'gray', 1.07, name='2 Cal1'), card(d, 'Cal2', 'gray', 1.07, name='2 Cal2'),
          card(d, 'Cal3', 'gray', 1.07, name='2 Cal3')]
    A(L.group(S(), '2 걸린 일정', f2), show=2, hide=3, enter=dict(delay=450, dur=420))
    t3, _ = tag(d, '2 놓친 이유 A1', a1['x'] + a1['w'] - 6, a1['y'] - 9, '캘린더 일정이 아님', anchor='r')
    A(t3, show=2, hide=3, enter=dict(delay=750, dur=300))
    A(row_els[1], show=2, enter=dict(kind='rise', delay=850, dur=450))
    note = L.text(S(), '출처', 50, 688, 1190, 22,
                  '* 출처: ¹ 삼성전자 뉴스룸, "[갤럭시 언팩 2025] ① ‘내 손안의 AI 시대 열렸다’ 언팩 하이라이트" (2025. 01) — '
                  'PDE는 옥스퍼드 시멘틱 테크놀로지스(지식 그래프)와 협업 개발',
                  size=12, color=MUTE)
    A(note, show=2, enter=dict(delay=850, dur=450))

    # ---------------------------------------------------------- 3 · 비슷한 것 찾기
    A(L.shape(S(), '3 질문 전체 표시', q1x - 6, q1y - 2, 164, 46, prst='roundRect', radius=8, fill=GRAY_HL, alpha=18,
              line=GRAY_LINE, dash='dash'), show=3, hide=4, enter=dict(delay=200, dur=350))
    p3 = [L.shape(S(), '3 읽기 바탕', 48, 276, 240, 62, prst='roundRect', radius=12, fill='FFFFFF', alpha=82,
                  line=GRAY_LINE, dash='dash'),
          L.text(S(), '3 읽기 제목', 62, 284, 200, 14, '비슷한 것 찾기 · 질문 전체를 숫자 하나로', size=8, color=MUTE, weight='sb')]
    g, _ = chip(d, '3 벡터', 62, 306, '[ 0.12, −0.83, 0.47, … , 0.09 ]', style='gray', pt=8, h=22, weight='m')
    p3.append(g)
    A(L.group(S(), '3 질문 읽기', p3), show=3, hide=4, enter=dict(kind='rise', delay=250, dur=450))
    f3 = [card(d, 'S1', 'gray', 1.07, name='3 S1'), card(d, 'A1', 'gray', 1.07, name='3 A1'),
          card(d, 'N1', 'gray', 1.07, name='3 N1')]
    A(L.group(S(), '3 비슷한 카드', f3), show=3, hide=4, enter=dict(delay=450, dur=420))
    ranks = []
    for i, key in enumerate(('S1', 'A1', 'N1')):
        c = CARDS[key]
        X, Y = scaled(key, 1.07)
        ranks.append(L.shape(S(), '3 순위 %d' % (i + 1), X(c['x']) - 7, Y(c['y']) - 7, 20, 20, prst='ellipse',
                             fill='8E88A0', line='FFFFFF', line_w=1.5))
        ranks.append(L.text(S(), '3 순위 글자 %d' % (i + 1), X(c['x']) - 7, Y(c['y']) - 7, 20, 20, str(i + 1), size=8,
                            color='FFFFFF', weight='b', align='c', anchor='ctr'))
    A(L.group(S(), '3 순위', ranks), show=3, hide=4, enter=dict(kind='zoom_in', delay=700, dur=300))
    t4, _ = tag(d, '3 놓친 이유 C2', c2['x'] + c2['w'] - 6, c2['y'] - 9, '질문과 안 닮아 순위 밖', anchor='r')
    A(t4, show=3, hide=4, enter=dict(delay=850, dur=300))
    A(row_els[2], show=3, enter=dict(kind='rise', delay=950, dur=450))

    # ---------------------------------------------------------- 4 · Weave: 탐색 메모
    pm = [band(q1x, q1y, Q1, '지은이네 집들이', QPT, 'm', kind='low'), band(q1x, q2y, Q2, '화이트 와인', QPT, 'm', kind='low')]
    A(hl_group(d, '4 질문 단서 형광펜', pm), show=4, enter=dict(kind='wipe_in', dir='left', delay=250, dur=500))
    mx, my, mw, mh = 48, 276, 240, 274
    memo = [L.shape(S(), '메모 바탕', mx, my, mw, mh, prst='roundRect', radius=14, fill='FFFFFF', line=LINE2, line_w=1.0,
                    shadow=L.SHADOW_CARD)]
    # 메모 아이콘(작은 클립보드)
    memo += [L.shape(S(), '메모 아이콘', mx + 14, my + 13, 12, 15, prst='roundRect', radius=2.5, fill=None, line=PURPLE, line_w=1.4),
             L.shape(S(), '메모 아이콘 줄1', mx + 17, my + 19, 6, 1.4, fill=PURPLE, line=None),
             L.shape(S(), '메모 아이콘 줄2', mx + 17, my + 23, 6, 1.4, fill=PURPLE, line=None),
             L.text(S(), '메모 제목', mx + 32, my + 11, 120, 18, '탐색 메모', size=9.5, color=PURPLE, weight='b'),
             L.text(S(), '메모 단계', mx + mw - 14 - 100, my + 13, 100, 14, '02 단서 정리', size=7.5, color=PURPLE2, weight='sb',
                    align='r'),
             L.shape(S(), '메모 구분선', mx + 14, my + 36, mw - 28, 1, fill='EEE9FA', line=None)]
    rowy = [my + 44 + i * 26 for i in range(5)]
    labels = ['찾을 것', '아는 단서', '먼저 볼 곳', '+ 새 단서', '멈출 때']
    for i, t in enumerate(labels):
        memo.append(L.text(S(), '메모 ' + t, mx + 14, rowy[i], 70, 22, t, size=8.5, color=PURPLE if i == 3 else SUB,
                           weight='b' if i == 3 else 'r', anchor='ctr'))
    CX = mx + 82
    g, w_ = chip(d, '메모 와인 이름', CX, rowy[0], '와인 이름', style='fill')
    memo.append(g)
    g, _ = chip(d, '메모 화이트', CX + w_ + 5, rowy[0], '화이트', style='outline')
    memo.append(g)
    g, w_ = chip(d, '메모 지은', CX, rowy[1], '지은', style='outline')
    memo.append(g)
    g, _ = chip(d, '메모 집들이', CX + w_ + 5, rowy[1], '집들이', style='outline')
    memo.append(g)
    g, w_ = chip(d, '메모 카톡', CX, rowy[2], '카톡', style='soft', icon=ICON['talk'])
    memo.append(g)
    g, _ = chip(d, '메모 캘린더', CX + w_ + 5, rowy[2], '캘린더', style='soft', icon=ICON['cal'])
    memo.append(g)
    stop_txt = '와인 이름을 찾으면'
    memo.append(L.text(S(), '메모 멈출 때 값', CX, rowy[4], 140, 22, stop_txt, size=8.5, color=SUB, anchor='ctr'))
    # 찾은 기록: 빈 줄 ①②③ → 홉마다 한 줄씩 채움
    ly0 = rowy[4] + 32
    memo += [L.shape(S(), '메모 구분선2', mx + 14, ly0, mw - 28, 1, fill='EEE9FA', line=None),
             L.text(S(), '메모 찾은 기록', mx + 14, ly0 + 7, 120, 14, '찾은 기록', size=8, color=SUB, weight='b')]
    logy = [ly0 + 26 + i * 21 for i in range(3)]
    for i in range(3):
        memo += [L.shape(S(), '기록 빈칸 %d 번호' % (i + 1), mx + 14, logy[i], 16, 16, prst='ellipse', fill='FFFFFF', line=LINE2,
                         line_w=0.9),
                 L.text(S(), '기록 빈칸 %d 번호 글자' % (i + 1), mx + 14, logy[i], 16, 16, str(i + 1), size=6.5, color='B7A6FF',
                        weight='b', align='c', anchor='ctr'),
                 L.shape(S(), '기록 빈칸 %d 줄' % (i + 1), mx + 38, logy[i] + 12, mw - 52, 0.9, fill='E9E4F6', line=None)]
    A(L.group(S(), '탐색 메모', memo), show=4, enter=dict(kind='rise', delay=450, dur=550))
    slot, slot_w = chip(d, '메모 새 단서 자리', CX, rowy[3], '            ', style='dash')
    A(slot, show=4, hide=6, enter=dict(delay=450, dur=550), exit=dict(delay=1050, dur=200))
    A(L.text(S(), '펜 무엇을', 54, my + mh + 8, 230, 26, '“무엇을, 어디부터 찾을까?”', size=15, color=PURPLE, pen=True),
      show=4, enter=dict(delay=950, dur=400))

    def log_line(i, method, result):
        y_ = logy[i]
        mw1 = L.width(method, 8, 'b')
        return L.group(S(), '찾은 기록 %d' % (i + 1), [
            L.shape(S(), '찾은 기록 %d 번호' % (i + 1), mx + 14, y_, 16, 16, prst='ellipse', fill=PURPLE, line=None),
            L.text(S(), '찾은 기록 %d 번호 글자' % (i + 1), mx + 14, y_, 16, 16, str(i + 1), size=6.5, color='FFFFFF', weight='b',
                   align='c', anchor='ctr'),
            L.shape(S(), '찾은 기록 %d 가림' % (i + 1), mx + 36, y_ - 1, mw - 48, 18, fill='FFFFFF', line=None),
            L.text(S(), '찾은 기록 %d 글자' % (i + 1), mx + 38, y_ - 2, mw - 50, 20,
                   [[(method, {'color': PURPLE, 'weight': 'b'}), ('  →  ' + result, {})]], size=8, color=INK2, anchor='ctr')])

    # 파이프라인 띠(맨 아래)
    strip_y, strip_h = 650, 32
    stages = [('00', '사전 준비', 'Indexing'), ('01', '순간 감지', 'Trigger'), ('02', '단서 정리', 'Routing'),
              ('03', '연쇄 탐색', 'Multi-hop Search'), ('04', '전달', 'Delivery')]
    base = [L.shape(S(), '파이프라인 띠', 48, strip_y, 1184, strip_h, prst='roundRect', fill='FFFFFF', alpha=88, line=LINE,
                    shadow=L.SHADOW_SOFT)]
    lit = []
    sx = 64
    for i, (no, ko, en) in enumerate(stages):
        kw_, ew_ = L.width(ko, 9, 'b'), L.width(en, 7.5, 'sb')
        bxy = strip_y + (strip_h - 18) / 2
        for state, lst in (('dim', base), ('lit', None)):
            parts = [L.shape(S(), '단계 %s %s 번호' % (no, state), sx, bxy, 18, 18, prst='ellipse',
                             fill=PURPLE if state == 'lit' else LAV, line=None),
                     L.text(S(), '단계 %s %s 번호 글자' % (no, state), sx, bxy, 18, 18, no, size=6.5,
                            color='FFFFFF' if state == 'lit' else PURPLE2, weight='b', align='c', anchor='ctr'),
                     L.text(S(), '단계 %s %s 이름' % (no, state), sx + 24, strip_y, kw_ + 4, strip_h, ko, size=9,
                            color=INK if state == 'lit' else MUTE, weight='b' if state == 'lit' else 'sb', anchor='ctr'),
                     L.text(S(), '단계 %s %s 영문' % (no, state), sx + 24 + kw_ + 6, strip_y + 1, ew_ + 4, strip_h, en,
                            size=7.5, color=PURPLE2 if state == 'lit' else 'B9B3C8', weight='sb', anchor='ctr')]
            if state == 'dim':
                base.extend(parts)
            else:
                lit.append(L.group(S(), '단계 %s 켜짐' % no, parts))
        sx += 24 + kw_ + 6 + ew_ + 12
        if i < 4:
            base.append(L.text(S(), '단계 화살표 %d' % i, sx - 4, strip_y, 14, strip_h, '›', size=11, color='C9C0E8',
                               weight='b', align='c', anchor='ctr'))
            sx += 18
    loop_t = '↻  필요한 정보가 채워질 때까지 반복'
    lpw = L.width(loop_t, 8.5, 'sb')
    base.append(L.text(S(), '반복 안내', 1232 - 18 - lpw - 4, strip_y, lpw + 4, strip_h, loop_t, size=8.5, color=PURPLE2,
                       weight='sb', anchor='ctr'))
    A(L.group(S(), '파이프라인', base), show=4, enter=dict(kind='rise', delay=700, dur=450))
    for i, gl in enumerate(lit[:3]):
        A(gl, show=4, enter=dict(delay=800 + i * 120, dur=350))


    # ---------------------------------------------------------- 5 · 홉 ① 추론 검색 → 지은의 카톡
    ax, ay, aw, ah = a1['x'], a1['y'], a1['w'], a1['h']
    t1p = [(mx + mw, rowy[1] + 11), (mx + mw + 48, rowy[1] + 11), (ax - 52, ay + ah / 2), (ax - 4, ay + ah / 2)]
    A(thread(d, '5 실 메모→카톡', t1p), show=5, enter=dict(kind='wipe_in', dir='left', delay=0, dur=550))
    a_bg, a_tx = card(d, 'A1', 'weave', 1.07, split=True, name='5 A1')
    A(a_bg, show=5, enter=dict(delay=400, dur=450))
    X, Y = scaled('A1', 1.07)
    bx, by = card_text_pos('A1')
    s7 = 1.07
    l1, l2 = CARDS['A1']['lines']
    r_mean = [band(bx, by, l1, '이사 기념으로', 9, kind='low'), band(bx, by + LINE_STEP, l2, '우리 집에서 저녁', 9, kind='low')]
    r_mean = [(X(x_), Y(y_), w_ * s7, h_ * s7) for x_, y_, w_, h_ in r_mean]
    A(hl_group(d, '5 뜻 형광펜', r_mean), show=5, enter=dict(kind='wipe_in', dir='left', delay=850, dur=500))
    r_date = [band(bx, by, l1, '이번 일요일 6시', 9, kind='low')]
    r_date = [(X(x_), Y(y_), w_ * s7, h_ * s7) for x_, y_, w_, h_ in r_date]
    A(hl_group(d, '6 날짜 형광펜', r_date), show=6, enter=dict(kind='wipe_in', dir='left', delay=0, dur=450))
    A(a_tx, show=5, enter=dict(delay=400, dur=450))
    tab1, _ = chip(d, '5 홉1 추론 검색', X(ax) + 12, Y(ay) - 11, '① 추론 검색', style='fill', pt=8, h=20, padx=9)
    A(tab1, show=5, enter=dict(kind='zoom_in', delay=650, dur=300))
    A(L.text(S(), '펜 집들이', X(ax) + 6, Y(ay + ah) + 4, 250, 24, '“집들이 = 이사 기념 저녁”', size=14, color=PURPLE, pen=True),
      show=5, enter=dict(delay=1200, dur=400))
    A(lit[3], show=5, enter=dict(delay=300, dur=350))
    A(log_line(0, '추론 검색', '지은의 카톡'), show=5, enter=dict(delay=1350, dur=350))

    # ---------------------------------------------------------- 6 · 새 단서: 이번 일요일 6시 → 3/15(일) 18:00
    tok, tok_w = chip(d, '6 새 단서 토큰', CX, rowy[3], '3/15 (일) 18:00', style='fill', pt=8.5)
    A(tok, show=6, enter=dict(delay=420, dur=180))
    sx0, sy0, _, _ = r_date[0]
    d.fx(6, 'path', tok, delay=420, dur=750, dx=sx0 - CX, dy=(sy0 - 3) - rowy[3], bend=0.18)

    # ---------------------------------------------------------- 7 · 홉 ② 시간 필터 → 그날 저녁 사진 두 장
    c1 = CARDS['C1']
    X1, Y1 = scaled('C1', 1.07)
    X2, Y2 = scaled('C2', 1.07)
    a_right = X(ax + aw) + 2
    a_mid = Y(ay + ah / 2)
    t2a = [(a_right, a_mid), (a_right + 46, a_mid), (X1(c1['x']) - 46, Y1(c1['y'] + 70)), (X1(c1['x']) - 3, Y1(c1['y'] + 70))]
    t2b = [(a_right, a_mid), (a_right + 46, a_mid), (X2(c2['x']) - 46, Y2(c2['y'] + 70)), (X2(c2['x']) - 3, Y2(c2['y'] + 70))]
    A(thread(d, '7 실 카톡→사진1', t2a), show=7, enter=dict(kind='wipe_in', dir='left', delay=0, dur=550))
    A(thread(d, '7 실 카톡→사진2', t2b), show=7, enter=dict(kind='wipe_in', dir='left', delay=80, dur=550))
    c1_copy = card(d, 'C1', 'weave', 1.07, name='7 C1')
    A(c1_copy, show=7, hide=8, enter=dict(delay=500, dur=450), exit=dict(delay=950, dur=350))
    A(card(d, 'C2', 'weave', 1.07, name='7 C2'), show=7, enter=dict(delay=600, dur=450))
    # 두 갈래 실 사이(카톡 오른쪽 ~ 사진 왼쪽 틈)에 둠
    chip2, c2w = chip(d, '7 홉2 시간 필터', a_right + 8, a_mid + 26, '② 시간 필터', style='outline', pt=8, h=20, padx=8)
    A(chip2, show=7, enter=dict(kind='zoom_in', delay=300, dur=300))
    A(log_line(1, '시간 필터', '그날 저녁 사진 2장'), show=7, enter=dict(delay=1000, dur=350))

    # ---------------------------------------------------------- 8 · 홉 ③ 사진 속 글자 + 추론 검색
    def pill(key, label, style, name):
        c = CARDS[key]
        Xk, Yk = scaled(key, 1.07)
        pw = L.width(label, 7.5, 'b', spc=0.4) + 18
        px0 = Xk(c['x'] + c['w'] / 2) - pw / 2
        py0 = Yk(c['y'] + 34 + 116) - 27
        parts = [L.shape(S(), name + ' 바탕', px0, py0, pw, 20, prst='roundRect', fill='FFFFFF', alpha=94,
                         line=PURPLE if style == 'weave' else GRAY_LINE, line_w=1.1),
                 L.text(S(), name + ' 글자', px0, py0, pw, 20, label, size=7.5, color=PURPLE if style == 'weave' else BODY,
                        weight='b', align='c', anchor='ctr', spc=0.4)]
        return L.group(S(), name, parts), (px0, py0, pw)

    p_c1, _ = pill('C1', 'CABERNET SAUVIGNON', 'gray', '8 라벨 글자 레드')
    p_c2, (p2x, p2y, p2w) = pill('C2', 'BABICH SAUVIGNON BLANC', 'weave', '8 라벨 글자 화이트')
    A(p_c1, show=8, enter=dict(kind='zoom_in', delay=0, dur=350))
    A(p_c2, show=8, enter=dict(kind='zoom_in', delay=100, dur=350))
    lbl = 'BABICH SAUVIGNON BLANC'
    ox, ow = span(lbl, 'SAUVIGNON BLANC', 7.5, 'b')
    ox += 0.4 * 4 / 3 * len('BABICH ')
    ow += 0.4 * 4 / 3 * len('SAUVIGNON BLANC')
    txt_w = L.width(lbl, 7.5, 'b', spc=0.4)
    tx_start = p2x + (p2w - txt_w) / 2
    A(hl_group(d, '8 블랑 형광펜', [(tx_start + ox - 2, p2y + 10, ow + 2, 7.5)]), show=8,
      enter=dict(kind='wipe_in', dir='left', delay=650, dur=450))
    chip3, _ = chip(d, '8 홉3 글자 읽기', X2(c2['x']) + 12, Y2(c2['y']) - 11, '③ 사진 속 글자 + 추론 검색', style='fill', pt=8, h=20,
                    padx=9)
    A(chip3, show=8, enter=dict(kind='zoom_in', delay=300, dur=300))
    red_tag, _ = tag(d, '8 레드', X1(c1['x']) + 16, Y1(c1['y']) + 40, '레드', style='grayfill')
    A(red_tag, show=8, enter=dict(delay=1050, dur=300))
    wh_tag, _ = tag(d, '8 화이트', X2(c2['x']) + 16, Y2(c2['y']) + 40, '블랑 = 화이트 ✓', style='fill')
    A(wh_tag, show=8, enter=dict(kind='zoom_in', delay=1100, dur=300))
    A(log_line(2, '라벨 읽기 + 추론', '화이트 1병'), show=8, enter=dict(delay=1300, dur=350))
    stop, _ = chip(d, '8 멈춤', CX + L.width(stop_txt, 8.5) + 8, rowy[4] + 2, '✓ 멈춤', style='fill', pt=7.5, h=18, padx=7)
    A(stop, show=8, enter=dict(kind='zoom_in', delay=1500, dur=300))

    # ---------------------------------------------------------- 9 · 전달
    wy0 = 186 + 3 * 84
    wv = [L.shape(S(), 'Weave 답 바탕', RX, wy0, RW, 640 - wy0, prst='roundRect', radius=14, fill='FFFFFF', line=PURPLE,
                  line_w=1.5, shadow=L.SHADOW_LIFT),
          L.shape(S(), 'Weave 답 표시', RX + RW - 30, wy0 + 12, 18, 18, prst='ellipse', fill=PURPLE, line=None),
          L.text(S(), 'Weave 답 표시 글자', RX + RW - 30, wy0 + 12, 18, 18, '✓', size=8, color='FFFFFF', weight='b', align='c',
                 anchor='ctr'),
          L.picture(S(), 'Weave 답 실타래', d.rid(ICON['spool']), RX + 15, wy0 + 12, 17, 17),
          L.text(S(), 'Weave 답 방식', RX + 38, wy0 + 11, 160, 18, [[('엮어 찾기', {}), ('  Weave', {'size': 8, 'color': PURPLE2, 'weight': 'sb'})]],
                 size=10, color=PURPLE, weight='b'),
          L.text(S(), 'Weave 답 자동 완성', RX + 16, wy0 + 44, 200, 14, '자동 완성 추천', size=7.5, color=PURPLE2, weight='b'),
          L.text(S(), 'Weave 답 이름', RX + 16, wy0 + 60, 250, 30, '배비치 소비뇽 블랑', size=17, color=INK, weight='b'),
          L.picture(S(), 'Weave 답 출처 카톡', d.rid(ICON['talk']), RX + 16, wy0 + 99, 14, 14),
          L.picture(S(), 'Weave 답 출처 갤러리', d.rid(ICON['gallery']), RX + 33, wy0 + 99, 14, 14),
          L.text(S(), 'Weave 답 출처', RX + 52, wy0 + 98, 210, 16, '출처 · 카톡 3/12, 갤러리 3/15 20:14', size=8, color=SUB),
          L.shape(S(), 'Weave 답 입력하기', RX + 16, wy0 + 126, RW - 32, 32, prst='roundRect', fill=PURPLE, line=None),
          L.text(S(), 'Weave 답 입력하기 글자', RX + 16, wy0 + 126, RW - 32, 32, '✓  입력하기', size=9.5, color='FFFFFF',
                 weight='b', align='c', anchor='ctr'),
          L.text(S(), 'Weave 답 안내', RX + 16, wy0 + 168, RW - 32, 18,
                 ['고른 것만 입력되고, 자동으로 보내지 않아요'], size=7.5, color=MUTE)]
    wcard = L.group(S(), 'Weave 답', wv)
    pr = (p2x + p2w + 2, p2y + 10)
    t3p = [pr, (pr[0] + 16, pr[1]), (RX - 22, wy0 + 76), (RX - 2, wy0 + 76)]
    A(thread(d, '9 실 라벨→답', t3p), show=9, enter=dict(kind='wipe_in', dir='left', delay=0, dur=450))
    A(wcard, show=9, enter=dict(kind='rise', delay=300, dur=550))
    A(lit[4], show=9, enter=dict(delay=300, dur=350))

    # ---------------------------------------------------------- 10 · 핵심 엔진
    bx0, by0, bw0, bh0 = 336, 566, 364, 62
    e1, e2a, e2b, e2c = '핵심 엔진 · 온디바이스 Reasoning Embedding', '지금 단서로부터 ', '‘이어지는’', ' 기록을 찾는 경량 모델'
    banner = L.group(S(), '핵심 엔진', [
        L.shape(S(), '핵심 엔진 바탕', bx0, by0, bw0, bh0, prst='roundRect', radius=14, fill='FFFFFF', line=PURPLE, line_w=1.5,
                shadow=L.SHADOW_LIFT),
        L.picture(S(), '핵심 엔진 실타래', d.rid(ICON['spool']), bx0 + 16, by0 + 14, 22, 22),
        L.text(S(), '핵심 엔진 이름', bx0 + 48, by0 + 10, bw0 - 56, 20, e1, size=10.5, color=PURPLE, weight='b'),
        L.text(S(), '핵심 엔진 설명', bx0 + 48, by0 + 33, bw0 - 56, 18,
               [[(e2a, {}), (e2b, {'weight': 'b', 'color': INK}), (e2c, {})]], size=9, color=BODY)])
    A(banner, show=10, enter=dict(kind='rise', delay=0, dur=550))
    d.fx(10, 'pulse', tab1, delay=650, dur=260, scale=1.12)
    d.fx(10, 'pulse', chip3, delay=900, dur=260, scale=1.12)
    d.veil = veil
    return d


# ------------------------------------------------------------------ 발표자 노트
NOTES = """HOW IT WORKS — Weave는 어떻게 기억을 엮을까요? (클릭 10번, 약 1분 40초)

[시작] "지은이네 집들이 때 마신 화이트 와인, 이름이 뭐였더라?" 답은 분명 내 폰 안에 있습니다. 가운데가 그 기록들입니다. 이 질문을 지금 쓰이는 세 가지 방식으로 먼저 찾아보겠습니다.

[클릭 1 · 단어로 찾기] 키워드 검색은 글자 그대로 찾습니다. 정확하고 빠르지만, '집들이 선물 와인 BEST 5' 캡처나 와인 메모처럼 글자만 같은 기록이 걸립니다. 정작 약속 메시지엔 '집들이'라는 말이 없고, 와인 라벨엔 '화이트'라는 글자가 없습니다.

[클릭 2 · 관계로 찾기] 관계로 찾는 방식은 미리 저장해 둔 사실과 관계를 따라갑니다. 정확하고 설명할 수 있는 게 강점입니다(예: PDE 방식 — 내부 구조는 공개되지 않았습니다). 그런데 이 약속은 캘린더 일정이 아니라 친구와 나눈 카톡 대화 속에만 있어서, 따라갈 일정이 없습니다.

[클릭 3 · 비슷한 것 찾기] 일반 임베딩은 질문 전체를 숫자 하나로 바꿔 비슷한 기록을 찾습니다. 표현이 달라도 찾을 수 있어서 지은의 카톡까지는 올라옵니다. 하지만 거기서 끝입니다. 정답이 담긴 그날 사진은 질문과 닮은 데가 없어서, 한 번에 찾는 방식으로는 닿지 않습니다.

[클릭 4 · Weave: 단서 정리] Weave는 바로 찾지 않고 먼저 탐색 메모를 씁니다. 찾을 것은 와인 이름, 그중에서도 화이트. 아는 단서는 지은과 집들이. 먼저 볼 곳은 약속이 남는 카톡과 캘린더입니다.

[클릭 5 · 홉 ① 추론 검색] 온디바이스 Reasoning Embedding이 '집들이'와 '이사 기념으로 우리 집에서 저녁'이 같은 일이라는 걸 알아보고, 지은의 카톡을 찾습니다. 비슷한 글이 아니라, 답으로 이어지는 기록을 찾는 겁니다.

[클릭 6 · 새 단서] 이 메시지에서 새 단서가 나옵니다. 3월 12일 목요일에 온 '이번 일요일 6시', 즉 3월 15일 일요일 저녁 6시. 찾은 단서는 메모에 더해지고, 다음 검색의 조건이 됩니다.

[클릭 7 · 홉 ② 시간 필터] 날짜처럼 정확한 조건은 추론하지 않고 필터로 좁힙니다. 그날 저녁 사진은 두 장, 와인도 두 병입니다.

[클릭 8 · 홉 ③ 사진 속 글자 + 추론 검색] 라벨을 읽으면 카베르네 소비뇽과 배비치 소비뇽 블랑. 어디에도 '화이트'라는 글자는 없지만, 소비뇽 블랑은 화이트 와인이죠. 찾을 것이 채워졌으니 여기서 멈춥니다.

[클릭 9 · 전달] 답은 출처와 함께 건넵니다. 배비치 소비뇽 블랑 — 출처는 카톡과 갤러리. 사용자가 확인하고 고른 것만 입력되고, 자동으로 보내지 않습니다.

[클릭 10 · 핵심 엔진] 정리하면, 찾은 기록이 다음 단서가 되어 답까지 이어졌습니다. 이걸 가능하게 하는 게 온디바이스 Reasoning Embedding, 지금 단서로부터 '이어지는' 기록을 찾는 경량 모델입니다. 매 단계 긴 문장을 생성하지 않고, 모든 과정이 기기 안에서 이뤄집니다.

(참고) 기존 방식 이름은 방식의 예시이며 제품 평가가 아닙니다. Finder는 One UI 8.5부터 자연어 검색을 지원하므로 '단어로 찾기'의 예로 쓰지 않았습니다. PDE를 지식 그래프 방식으로 설명한 근거는 삼성전자 뉴스룸(2025. 01, 옥스퍼드 시멘틱 테크놀로지스와 협업 개발)과 OST 블로그(2025. 01)입니다. 상세 근거: 09_HowItWorks/리서치/삼성_현재기술_조사.md"""


# ------------------------------------------------------------------ 파일 만들기
def keep_only(prs, keep_idx):
    """슬라이드 keep_idx(0부터)만 남김."""
    lst = prs.slides._sldIdLst
    ids = list(lst)
    for i, sld in enumerate(ids):
        if i != keep_idx:
            prs.part.drop_rel(sld.get(q('r:id')))
            lst.remove(sld)


def header_of(slide):
    return [copy.deepcopy(sh._element) for sh in slide.shapes if sh.name.startswith('Header')]


def clear_old(slide):
    """기존 9쪽 도형과 그림 연결을 지움."""
    tree = slide.shapes._spTree
    for c in list(tree)[2:]:
        tree.remove(c)
    for rId, rel in list(slide.part.rels.items()):
        if rel.reltype.endswith('/image'):
            slide.part.drop_rel(rId)


def set_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def build_single(dst, auto=None):
    prs = Presentation(str(DECK))
    slide = prs.slides[SLIDE_NO - 1]
    hdr = header_of(slide)
    keep_only(prs, SLIDE_NO - 1)
    clear_old(slide)
    d = compose(slide, header=hdr)
    d.write(auto=auto)
    set_notes(slide, NOTES)
    prs.save(str(dst))
    return d


def build_states(dst):
    prs = Presentation(str(DECK))
    slide0 = prs.slides[SLIDE_NO - 1]
    hdr = header_of(slide0)
    layout = slide0.slide_layout
    keep_only(prs, SLIDE_NO - 1)
    clear_old(slide0)
    # 남긴 9쪽(slide9.xml)이 새로 붙일 장 이름과 겹치지 않게 slide1.xml로 바꿈(원래 1쪽은 이미 빠져 저장되지 않음)
    from pptx.opc.packuri import PackURI
    slide0.part.partname = PackURI('/ppt/slides/slide1.xml')
    nst = 10
    for s in range(nst + 1):
        sl = slide0 if s == 0 else prs.slides.add_slide(layout)
        if s > 0:
            for ph in list(sl.placeholders):
                ph._element.getparent().remove(ph._element)
        d = compose(sl, state=s, header=hdr)
        d.write(timing=False)
    prs.save(str(dst))


def build_deck(dst):
    prs = Presentation(str(DECK))
    slide = prs.slides[SLIDE_NO - 1]
    hdr = header_of(slide)
    old_notes = slide.notes_slide.notes_text_frame.text
    clear_old(slide)
    d = compose(slide, header=hdr)
    d.write()
    set_notes(slide, NOTES)
    prs.save(str(dst))
    return old_notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--deck', action='store_true')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.deck:
        old = build_deck(OUT / 'Weave_결선_HIW검토.pptx')
        (OUT / '기존9쪽_발표자노트.txt').write_text(old, encoding='utf-8')
        print('검토용 덱 →', OUT / 'Weave_결선_HIW검토.pptx')
        return
    d = build_single(OUT / 'HowItWorks.pptx')
    print('클릭 단계:', len(d.timeline.steps), ' 단계별 길이(ms):', [d.timeline.step_len(i) for i in range(len(d.timeline.steps))])
    holds = [3200, 3200, 3400, 3200, 3400, 3000, 3000, 3800, 3200, 4500]
    build_single(OUT / 'HowItWorks_자동재생.pptx', auto=(2500, holds))
    build_states(OUT / 'HowItWorks_단계확인.pptx')
    print('→', OUT)


if __name__ == '__main__':
    main()
