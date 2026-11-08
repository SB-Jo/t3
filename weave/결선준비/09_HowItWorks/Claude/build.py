#!/usr/bin/env python3
"""How it Works — Claude판 (2026-11-08 사용자 피드백 반영, 솔루션 장부터 정리 장까지 2분 30초~3분).

  python build.py                 → ../HowItWorks_Claude.pptx (발표용: 클릭마다 한 박자)
  python build.py --png           + out/png/s01.png… 와 out/한눈에.png (PowerPoint로 렌더, 정적 = 마지막 상태)
  python build.py --video         + out/HowItWorks_Claude_미리보기.mp4 (클릭 효과도 저절로 나오는 사본을 PowerPoint로 녹화)

흐름(장): 솔루션 → How it works? → 질문 → 흩어진 단서 → 기존 검색이라면? → 키워드 → 임베딩 → Let's think step by step!
→ 끊어진 고리 → 00 데이터 색인 → 01 상황 인식 → 02 질의 재작성 → 03 Hop 1 → 03 Hop 2 → 04 결과 제공 → 한눈에 보기.
'흐려지며 큰 글자'는 앞 장을 PowerPoint로 찍은 그림을 흐리게 해 깔고(2번 빌드), 나머지 움직임은 모핑과 motion.py 효과로 낸다.
"""
import argparse
import copy
import random
import shutil
import sys
from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pptx import Presentation

import hiw_lib as L
import motion as M
import render_c
from hiw_lib import q
from ui import (BODY, GRAY_FILL, HL, ICON, INK, INK2, LAV, LAV2, LINE, LINE2, MUTE, PURPLE, PURPLE2, RED, RING, SUB,
                SHADOW_CARD, SHADOW_LIFT, SHADOW_SOFT, BADGE_BOX, C, P, Painter, R, T, Xf, badge_prims, bg_prims, caption, card,
                chip, crop_fit, gallery, hl_band, line, magnifier, numdot, qbadge, scurve, search_pill, thread, topbar_prims, tw,
                vcurve, xmark)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / '11_중간본'))
import samsung_fonts  # noqa: E402

DECK = ROOT / '02_PPT' / 'Weave_결선_중간본.pptx'
SOL_INDEX = 4                      # 중간본 5쪽 = 솔루션(세 시나리오 정리)
DST = HERE.parent / 'HowItWorks_Claude.pptx'
OUT = HERE / 'out'
AS = HERE / 'assets'

QUERY = '지은이네 집들이 때 마셨던 와인'
OFF = 1600                         # 잠깐 보이는 것을 둘 화면 밖 거리(px)
MC = 'http://schemas.openxmlformats.org/markup-compatibility/2006'
P14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
P159 = 'http://schemas.microsoft.com/office/powerpoint/2015/09/main'

# 사진(실제 사진으로 바꿀 자리). (파일, 날짜, 초점)
PH = {
    'babich': ('photo-babich.png', '2026. 3. 15', (0.5, 0.45)),
    'table': ('photo-homedinner.jpg', '2026. 3. 15', (0.5, 0.5)),
    'w1': ('photo-seaside.jpg', '2025. 7. 19', (0.62, 0.5)),
    'w2': ('photo-meadow.jpg', '2025. 9. 27', (0.66, 0.6)),
    'w3': ('photo-champagne.jpg', '2025. 12. 31', (0.62, 0.45)),
    'glass': ('photo-glass.jpg', '2026. 1. 9', (0.45, 0.45)),
}
WINE4 = ['babich', 'w3', 'w2', 'w1']          # 키워드·끊어진 고리 장의 와인 사진 넷(갤러리처럼 최신순, 첫째가 집들이 날)
BLUE, BLUE_HL, BLUE_BG = '4F7BFF', '7EA2FF', 'EEF3FF'    # 둘째 하위 질문 색(①은 보라, ②는 파랑)


# ------------------------------------------------------------------ 장
class Slide:
    def __init__(self, key, notes='', trans=('morph', 900), advance=None, bar=True, cur=None, done=(), bg=True):
        self.key, self.notes, self.trans, self.advance = key, notes, trans, advance
        self.bar, self.cur, self.done, self.bg = bar, cur, set(done), bg
        self.items = []
        self.groups = [[]]

    def add(self, key, prims, alpha=100, xf=None, group=None, temp=False, start=None):
        """temp: 잠깐만 보이는 것. 화면 밖(+1600px)에 두고 처음 나타날 때 'jump'로 제자리에 옮김(정적 보기·내보내기엔 안 보임).
          PowerPoint는 이동 경로를 더하지 않고 바꿔 끼우므로, 그 뒤 'fly'·'move'는 화면 밖 기준(base)으로 바꿔 넣음.
        start = (dx, dy): 놓인 자리는 마지막 자리. 'goto'로 처음 자리에 옮겨 두고, 되돌아올 땐 'fly'(dx, dy)."""
        self.items.append((key, prims, alpha, xf, group, temp, start))
        return key

    def on(self, keys, kind, delay=0, dur=400, **kw):
        for k in ([keys] if isinstance(keys, str) else keys):
            self.groups[-1].append((k, kind, delay, dur, kw))

    def click(self):
        self.groups.append([])

    def clicks(self):
        return len(self.groups) - 1


def morph_xml(ms, adv=None):
    a = ' advTm="%d"' % adv if adv else ''
    return ('<mc:AlternateContent xmlns:mc="%s" xmlns:p="%s" xmlns:p14="%s"><mc:Choice xmlns:p159="%s" Requires="p159">'
            '<p:transition spd="slow" p14:dur="%d"%s><p159:morph option="byObject"/></p:transition></mc:Choice>'
            '<mc:Fallback><p:transition spd="slow"%s><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>') % (
        MC, L.NS['p'], P14, P159, ms, a, a)


def fade_xml(ms, adv=None):
    a = ' advTm="%d"' % adv if adv else ''
    return ('<mc:AlternateContent xmlns:mc="%s" xmlns:p="%s" xmlns:p14="%s"><mc:Choice Requires="p14">'
            '<p:transition spd="med" p14:dur="%d"%s><p:fade/></p:transition></mc:Choice>'
            '<mc:Fallback><p:transition spd="med"%s><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>') % (
        MC, L.NS['p'], P14, ms, a, a)


def set_transition(slide, trans, adv=None):
    sld = slide._element
    for old in sld.findall(q('p:transition')):
        sld.remove(old)
    for old in sld.findall('{%s}AlternateContent' % MC):
        sld.remove(old)
    if not trans and not adv:
        return
    kind, ms = trans if trans else ('none', 0)
    if kind == 'morph':
        x = morph_xml(ms, adv)
    elif kind == 'fade':
        x = fade_xml(ms, adv)
    else:
        x = '<p:transition xmlns:p="%s"%s/>' % (L.NS['p'], ' advTm="%d"' % adv if adv else '')
    sld.find(q('p:clrMapOvr')).addnext(etree.fromstring(x))


# ------------------------------------------------------------------ 자주 쓰는 조각
def put_card(s, key, *a, **kw):
    prims, h, pos = card(key, *a, **kw)
    s.add(key, prims)
    return h, pos


def band(name, pos, sub, kind='low', start=0, alpha=34):
    x, y, text, pt, wt = pos
    return hl_band(name, x, y, text, sub, pt, wt, start=start, kind=kind, alpha=alpha)


def tag_red(name, cx, y, label, pt=10.5):
    prims, w = chip(name, cx, y, label, 'red', pt=pt, h=28, padx=13, align='c')
    return prims


def dim_over(name, box, radius=12, alpha=62):
    x, y, w, h = box
    return R(name, x, y, w, h, prst='roundRect', radius=radius, fill='FFFFFF', alpha=alpha, line=None)


def star(name, cx, cy, r=15):
    return [R(name + '/glow', cx - r * 1.9, cy - r * 1.9, r * 3.8, r * 3.8, prst='ellipse', fill=None,
              grad=dict(stops=[(0, 'B9A2FF', 55), (60, 'D9CCFF', 18), (100, 'F8F5FF', 0)], path='circle', rect=(50, 50, 50, 50))),
            R(name + '/s', cx - r, cy - r, 2 * r, 2 * r, prst='star5', fill=PURPLE, line='FFFFFF', line_w=2)]


def mini_chip(name, x, y, kind, label, sub=None, pt=10.5, alpha=100, img=None):
    """임베딩 공간 속 기록 점: 아이콘 + 짧은 이름(+ 회색 한 줄). 돌려줌: (원시, 폭, 높이)."""
    h = 34 if not sub else 46
    isz = 22
    w = 12 + isz + 8 + max(tw(label, pt, 'b'), tw(sub, pt - 1.5) if sub else 0) + 14
    out = [R(name + '/bg', x, y, w, h, prst='roundRect', radius=12, fill='FFFFFF', line=LINE, line_w=1.0, shadow=SHADOW_SOFT,
             alpha=alpha, line_alpha=alpha)]
    if img:
        out.append(P(name + '/ic', img, x + 8, y + (h - 30) / 2, 30, 30, radius=6, crop=crop_fit(img, 30, 30), alpha=alpha))
        w += 8
        tx = x + 8 + 30 + 8
    else:
        out.append(P(name + '/ic', ICON[kind], x + 12, y + (h - isz) / 2, isz, isz, alpha=alpha))
        tx = x + 12 + isz + 8
    if sub:
        out.append(T(name + '/t', tx, y + 6, w, 18, label, size=pt, color=INK, weight='b', alpha=alpha))
        out.append(T(name + '/s', tx, y + 24, w, 16, sub, size=pt - 1.5, color=MUTE, alpha=alpha))
    else:
        out.append(T(name + '/t', tx, y, w, h, label, size=pt, color=INK, weight='b', anchor='ctr', alpha=alpha))
    return out, w, h


def ring_box(name, box, pad=5, radius=20, w=2.4):
    x, y, bw, bh = box
    return R(name, x - pad, y - pad, bw + 2 * pad, bh + 2 * pad, prst='roundRect', radius=radius, fill=None, line=RING, line_w=w,
             glow=(10, RING, 30))


# ------------------------------------------------------------------ 0. 솔루션 → How it works?
def s_hiw():
    s = Slide('hiw', trans=('fade', 700), bar=False,
              notes='그럼 Weave는 어떻게 동작할까요? 두 번째 와인 장면으로 따라가 보겠습니다.')
    s.add('bg/blur', [P('bg/blur', str(OUT / 'blur_sol.png'), 0, 0, 1280, 720)])
    s.add('hiw/big', [caption('hiw/big', [[('How it ', INK), ('works?', PURPLE)]], 640, 300, size=80)])
    s.on('hiw/big', 'pop', 250, 750, **{'from': 0.72, 'over': 1.04})
    return s


# ------------------------------------------------------------------ 1. 질문
PHONE = (150, 196, 636, 620)


def phone_prims(key, alpha=100):
    x, y, w, h = PHONE
    gw = 230
    gh = gw * 276 / 816
    return [R(key + '/body', x, y, w, h, prst='roundRect', radius=64, fill='FFFFFF', line=LINE2, line_w=1.6, shadow=SHADOW_LIFT),
            R(key + '/notch', x + w / 2 - 56, y + 22, 112, 14, prst='roundRect', fill='ECE8F4', line=None),
            P(key + '/g', ICON['google'], x + w / 2 - gw / 2, y + 92, gw, gh)]


def s_ask():
    s = Slide('ask', trans=('morph', 1000),
              notes='집들이 때 마셨던 와인이 맛있어서 다시 사려는데, 이름이 떠오르지 않습니다.')
    bx, by, bw, bh = BADGE_BOX
    s.add('hiw/big', [T('hiw/big', bx, by - 4, bw, bh + 8, [[('How it ', {'color': INK}), ('works?', {'color': PURPLE})]],
                        size=10.5, weight='b', align='c', anchor='ctr', alpha=0)])
    s.add('ask/phone', phone_prims('ask/phone'))
    pill, txt, cur, _ = search_pill('ask/sp', 188, 404, 560, 84, QUERY, pt=19)
    s.add('ask/sp', pill)
    s.add('ask/q', [txt])
    s.add('ask/cur', [cur])
    s.add('ask/cap', [caption('ask/cap', [[('집들이 때 마셨던 와인,', INK)], [('이름이 뭐였더라?', PURPLE)]], 820, 380, size=30, align='l')])
    s.on('ask/cap', 'rise', 350, 550, dy=16)
    n = len(QUERY)
    s.on('ask/q', 'type', 1000, 1, ms=55, n=n)
    t_end = 1000 + 55 * n + 60
    s.on('ask/cur', 'appear', t_end, 1)
    s.on('ask/cur', 'blink', t_end + 30, 1000)
    return s


# ------------------------------------------------------------------ 2. 흩어진 단서
FLOATS = [
    # (키, 종류, 제목, 한 줄, x, y, 배율, 투명도) — 표지처럼 크기를 섞음. 가운데 제목 자리(x 300~980, y 270~392)는 비움
    ('f_note1', 'note', '지은이네 주소', '경기도 수원시 영통구…', 430, 150, 1.0, 72),
    ('f_note2', 'note', '장 볼 것', '우유, 계란, 휴지', 690, 116, 0.85, 40),
    ('f_talk4', 'talk', '택배', '문 앞에 두고 갔어요', 800, 206, 0.8, 34),
    ('f_mail1', 'mail', '관리비 고지서', '2월분 관리비', 64, 318, 0.9, 44),
    ('f_cal3', 'cal', '팀 회식', '3/20 (금) 19:00', 60, 428, 0.88, 40),
    ('f_talk3', 'talk', '엄마', '반찬 보냈다', 92, 536, 0.85, 40),
    ('f_mail2', 'mail', '[예약 확인] 오사카 호텔', '2월 27일', 70, 638, 0.82, 34),
    ('f_note3', 'note', '와인 메모', '산미 있는 화이트', 560, 428, 0.95, 52),
    ('f_phone', 'phone', '부재중 전화', '어제 오후 3:12', 782, 430, 0.8, 32),
    ('f_cal2', 'cal', '치과 예약', '3/4 (수) 오전 10:30', 722, 612, 0.9, 42),
    ('f_cal1', 'cal', '성빈이 신혼집들이', '2025. 10. 18 (토)', 960, 418, 1.0, 66),
    ('f_talk2', 'talk', '팀 단톡방', '회의록 공유해요', 1082, 520, 0.9, 46),
    ('f_gal2', 'gallery', 'IMG_2433.jpg', '3월 8일 12:40', 1040, 622, 0.85, 36),
    ('f_map', 'map', '저장한 장소', '성수 카페', 530, 566, 0.8, 34),
]


def frag(key, kind, title, meta, x, y, s=1.0, alpha=100, style='base'):
    """흩어진 작은 기록 조각(아이콘 + 제목 + 한 줄)."""
    pt1, pt2 = 13 * s, 10.5 * s
    isz = 30 * s
    h = 62 * s
    w = 16 * s + isz + 12 * s + max(tw(title, pt1, 'b'), tw(meta, pt2)) + 22 * s
    tx = x + 16 * s + isz + 12 * s
    ln = {'base': (LINE, 1.0), 'weave': (RING, 2.4)}[style]
    return [R(key + '/bg', x, y, w, h, prst='roundRect', radius=16 * s, fill='FFFFFF', line=ln[0], line_w=ln[1], shadow=SHADOW_SOFT,
              glow=(12, RING, 30) if style == 'weave' else None),
            P(key + '/ic', ICON[kind], x + 16 * s, y + (h - isz) / 2, isz, isz),
            T(key + '/t', tx, y + 10 * s, w, 22 * s, title, size=pt1, color=INK, weight='b'),
            T(key + '/m', tx, y + 34 * s, w, 18 * s, meta, size=pt2, color=MUTE)], w, h


def s_cloud():
    s = Slide('cloud', trans=('morph', 900),
              notes='사실 정답은 이미 기기 안에 있습니다. (클릭) 다만 그 단서가 카톡과 갤러리처럼 여러 앱에 흩어져 있습니다.')
    talk = card('cl_talk', 'talk', 70, 126, 300, '지은', '카카오톡 · 3월 15일 (일)', ['박스 정리 다 했어! 이따 올 때', '휴지 안 사 와도 돼'], pt=11.5)
    photo = card('cl_photo', 'photo', 990, 128, 240, '갤러리', '3월 15일 (일) 20:14', img=PH['babich'][0], img_h=140,
                 img_focus=PH['babich'][2])
    photo2 = card('cl_photo2', 'photo', 300, 470, 196, '갤러리', '2025. 9. 27', img=PH['w2'][0], img_h=100, img_focus=PH['w2'][2])
    order = []
    for key, kind, title, meta, x, y, sc, al in FLOATS:
        prims, w, h = frag(key, kind, title, meta, x, y, sc)
        s.add(key, prims, alpha=al)
        order.append(key)
    s.add('cl_photo2', photo2[0], alpha=62)
    s.add('cl_talk', talk[0])
    s.add('cl_photo', photo[0])
    s.add('cl_ring1', [ring_box('cl_ring1', (70, 126, 300, talk[1]))])
    s.add('cl_ring2', [ring_box('cl_ring2', (990, 128, 240, photo[1]))])
    s.add('cl_t1', [caption('cl_t1', [[('정답은 이미 기기 안에', INK)]], 640, 278, size=32)])
    s.add('cl_t2', [caption('cl_t2', [[('그러나, ', INK), ('여러 앱에 흩어져 있는 단서들', PURPLE)]], 640, 328, size=32)])
    keys = order[:]
    random.Random(7).shuffle(keys)
    keys = ['cl_talk', 'cl_photo'] + keys[:5] + ['cl_photo2'] + keys[5:]
    for i, k in enumerate(keys):
        s.on(k, 'rise', 120 + i * 55, 480, dy=14)
    s.on('cl_t1', 'rise', 700, 600, dy=16)
    s.click()
    s.on('cl_t2', 'rise', 0, 550, dy=16)
    for k in order + ['cl_photo2']:
        s.on(k, 'dim', 250, 500, to=0.45)
    s.on(['cl_ring1', 'cl_ring2'], 'zoom_in', 350, 450, **{'from': 1.08})
    return s


# ------------------------------------------------------------------ 3. 기존 검색이라면?
def old_title(y=300, size=54):
    return caption('old/title', [[('기존 검색', PURPLE), ('이라면?', INK)]], 640, y, size=size)


def s_old():
    s = Slide('old', trans=('morph', 600), advance=1900, notes='기존 검색이라면 어떨까요?')
    s.add('old/title', [old_title(300, 56)])
    s.on('old/title', 'pop', 0, 650, **{'from': 0.7, 'over': 1.05})
    return s


# 키워드 장의 자리
KW_PANEL = (370, 136, 540, 120)
KW_FIELD = (392, 186, 496, 50)


def kw_parts(dimmed=()):
    """키워드 검색 구성(판, 결과 셋, 형광펜, 실, 판정). 돌려줌: [(키, 원시)] 와 자리 정보."""
    px, py, pw, ph = KW_PANEL
    fx, fy, fw, fh = KW_FIELD
    parts = []
    lab_w = tw('키워드 검색', 15, 'b')
    bm, bmw = chip('kw/bm', px + 24 + lab_w + 10, py + 15, 'BM25', 'soft', pt=10, h=24, padx=10)
    parts.append(('kw/panel', [R('kw/panel/bg', px, py, pw, ph, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.4,
                                 shadow=SHADOW_CARD),
                               T('kw/panel/l', px + 24, py + 13, 200, 26, '키워드 검색', size=15, color=INK, weight='b')] + bm +
                  [R('kw/panel/f', fx, fy, fw, fh, prst='roundRect', fill='F7F5FC', line=LINE, line_w=1.0)]))
    qpt = 15.5
    S = qpt * 4 / 3
    qx, qy = fx + 20, fy + (fh - S * 1.2) / 2
    parts.append(('kw/q', [T('kw/q', qx, qy, fw - 30, S * 1.3, QUERY, size=qpt, color=INK)]))
    qpos = (qx, qy, QUERY, qpt, 'r')
    words = ['지은이네', '집들이', '와인']
    bands = [band('kw/h%d' % (i + 1), qpos, wd) for i, wd in enumerate(words)]
    for i, b in enumerate(bands):
        parts.append(('kw/h%d' % (i + 1), [b]))
    # 결과 셋: 1·2 왼쪽, 3 오른쪽
    c1 = card('kw/c1', 'note', 64, 334, 300, '지은이네 주소', '삼성노트 · 2025. 9. 2', ['경기도 수원시 영통구 매탄로 77', '푸른숲아파트 103동 1204호'],
              bubble=False, pt=11)
    c2 = card('kw/c2', 'cal', 384, 334, 272, '성빈이 신혼집들이', '캘린더 · 2025. 10. 18 (토)', ['오후 6:00  성빈이네 새집'], bubble=False, pt=11)
    g = gallery('kw/c3', 686, 334, 530, [PH[k] for k in WINE4], cols=4, tag='와인', ph=96)
    parts += [('kw/c1', c1[0]), ('kw/c2', c2[0]), ('kw/c3', g[0])]
    boxes = {'kw/c1': (64, 334, 300, c1[1]), 'kw/c2': (384, 334, 272, c2[1]), 'kw/c3': (686, 334, 530, g[1])}
    # 카드 안 형광펜(같은 단어)
    parts.append(('kw/m1', [band('kw/m1', c1[2]['title'], '지은이네')]))
    parts.append(('kw/m2', [band('kw/m2', c2[2]['title'], '집들이')]))
    # 실: 단어 아래 → 카드 위
    tops = []
    for i, (b, k) in enumerate(zip(bands, ['kw/c1', 'kw/c2', 'kw/c3'])):
        bx = b[2] + b[4] / 2
        x, y, w, h = boxes[k]
        a = (bx, py + ph - 2)
        e = (x + w / 2 if k != 'kw/c3' else x + 120, y + 2)
        parts.append(('kw/t%d' % (i + 1), thread('kw/t%d' % (i + 1), vcurve(a, e, 0.55), w=2.4)))
        tops.append(e)
    for i, k in enumerate(['kw/c1', 'kw/c2', 'kw/c3']):
        x, y, w, h = boxes[k]
        parts.append(('kw/n%d' % (i + 1), numdot('kw/n%d' % (i + 1), x + 4, y + 4, i + 1)))
    # 판정
    for i, (k, label) in enumerate((('kw/c1', '와인 정보가 없는 메모'), ('kw/c2', '다른 사람의 집들이 일정'))):
        x, y, w, h = boxes[k]
        parts.append(('kw/x%d' % (i + 1), xmark('kw/x%d' % (i + 1), x + w / 2, y + h / 2 + 4, s=46)))
        parts.append(('kw/v%d' % (i + 1), tag_red('kw/v%d' % (i + 1), x + w / 2, y + h + 12, '✕  ' + label)))
    # 사진 날짜 형광펜 + 물음
    gx, gy, gw, gh = boxes['kw/c3']
    dates = []
    for i, (px_, py_, pw_, ph_) in enumerate(g[2]):
        d = PH[WINE4[i]][1]
        dw = tw(d, 9)
        dates.append(R('kw/d%d' % i, px_ + pw_ / 2 - dw / 2 - 4, py_ + ph_ + 3, dw + 8, 17, prst='roundRect', radius=4, fill=HL, alpha=30,
                       line=None))
    parts.append(('kw/dates', dates))
    parts.append(('kw/qb', qbadge('kw/qb', gx + gw / 2, gy - 50, '어느 날이 집들이였지?', pt=12)))
    parts.append(('kw/end', [caption('kw/end', [[('정답은 이 사진들 중에 있지만,', INK)], [('집들이가 언제였는지 알 수 없습니다', PURPLE)]], 640, 566,
                                     size=27)]))
    return parts, boxes


KW_SMALL = Xf(ax=40, ay=120, bx=30, by=168, s=0.46)


def s_kw():
    s = Slide('kw', trans=('morph', 900),
              notes=('키워드 검색은 (클릭) 질문 속 단어가 든 기록을 찾습니다. (클릭) 지은이네로는 와인 정보가 없는 주소 메모가, '
                    '(클릭) 집들이로는 작년 성빈이네 집들이 일정이 나옵니다. (클릭) 와인 사진도 여러 장 나오고, 정답도 이 안에 있습니다. '
                    '하지만 지은이의 초대 카톡에는 집들이라는 단어가 없어서, 그날이 언제였는지 알 수 없습니다.'))
    s.add('old/title', [old_title(78, 30)])
    parts, boxes = kw_parts()
    order = ['kw/t1', 'kw/t2', 'kw/t3', 'kw/c1', 'kw/c2', 'kw/c3', 'kw/panel', 'kw/q', 'kw/m1', 'kw/m2', 'kw/h1', 'kw/h2', 'kw/h3',
             'kw/n1', 'kw/n2', 'kw/n3', 'kw/dates', 'kw/x1', 'kw/v1', 'kw/x2', 'kw/v2', 'kw/qb', 'kw/end']
    pm = dict(parts)
    for k in order:
        s.add(k, pm[k])
    s.on('kw/panel', 'rise', 100, 500, dy=14)
    s.on('kw/q', 'fade_in', 300, 400)
    s.click()   # 1: 단어 셋 → 결과 셋
    for i in range(3):
        s.on('kw/h%d' % (i + 1), 'wipe_in', i * 160, 380)
        s.on('kw/t%d' % (i + 1), 'wipe_in', 420 + i * 120, 500, dir='down')
    for i, k in enumerate(['kw/c1', 'kw/c2', 'kw/c3']):
        s.on(k, 'rise', 800 + i * 140, 500, dy=16)
        s.on('kw/n%d' % (i + 1), 'pop', 1150 + i * 140, 420, **{'from': 0.4, 'over': 1.15})
    s.on(['kw/m1', 'kw/m2'], 'wipe_in', 1500, 380)
    s.click()   # 2: 주소 메모
    s.on('kw/c1', 'dim', 0, 400, to=0.32)
    s.on('kw/n1', 'dim', 0, 400, to=0.32)
    s.on('kw/m1', 'dim', 0, 400, to=0.32)
    s.on('kw/x1', 'pop', 250, 450, **{'from': 0.3, 'over': 1.15})
    s.on('kw/v1', 'pop', 420, 420, **{'from': 0.6, 'over': 1.08})
    s.click()   # 3: 다른 집들이
    s.on('kw/c2', 'dim', 0, 400, to=0.32)
    s.on('kw/n2', 'dim', 0, 400, to=0.32)
    s.on('kw/m2', 'dim', 0, 400, to=0.32)
    s.on('kw/x2', 'pop', 250, 450, **{'from': 0.3, 'over': 1.15})
    s.on('kw/v2', 'pop', 420, 420, **{'from': 0.6, 'over': 1.08})
    s.click()   # 4: 사진 여러 장 → 큰 문장
    s.on('kw/dates', 'wipe_in', 0, 450)
    s.on('kw/qb', 'pop', 200, 450, **{'from': 0.6, 'over': 1.08})
    s.on('kw/end', 'rise', 900, 600, dy=18)
    return s


# 임베딩 장
EM_PANEL = (624, 136, 600, 120)
EM_FIELD = (646, 186, 556, 50)
SPACE = (624, 318, 600, 332)
STAR = (884, 498)


def s_emb():
    s = Slide('emb', trans=('morph', 1000),
              notes=('임베딩 검색은 (클릭) 질문 전체를 벡터 하나로 바꾸고, (클릭) 미리 만들어 둔 임베딩 공간에서 가장 가까운 기록을 한 번에 찾습니다. '
                    '(클릭) 하지만 가까운 건 와인 메모와 다른 날 와인 사진입니다. 뜻은 비슷해도, 집들이가 언제였는지는 여전히 모릅니다.'))
    s.add('old/title', [old_title(78, 30)])
    parts, _ = kw_parts()
    keep = ['kw/t1', 'kw/t2', 'kw/t3', 'kw/c1', 'kw/c2', 'kw/c3', 'kw/panel', 'kw/q', 'kw/m1', 'kw/m2', 'kw/h1', 'kw/h2', 'kw/h3',
            'kw/n1', 'kw/n2', 'kw/n3', 'kw/dates', 'kw/x1', 'kw/v1', 'kw/x2', 'kw/v2', 'kw/qb', 'kw/end']
    pm = dict(parts)
    for k in keep:
        al = 38 if k != 'kw/end' else 70
        if k in ('kw/c1', 'kw/c2', 'kw/n1', 'kw/n2', 'kw/m1', 'kw/m2'):
            al = 22
        s.add(k, pm[k], alpha=al, xf=KW_SMALL)
    s.add('em/div', [line('em/div', (596, 170), (596, 640), color='E2DBF5', w=1.4)])
    # 판
    px, py, pw, ph = EM_PANEL
    fx, fy, fw, fh = EM_FIELD
    lab_w = tw('임베딩 검색', 15, 'b')
    sh, _ = chip('em/sh', px + 24 + lab_w + 10, py + 15, 'Single-hop', 'soft', pt=10, h=24, padx=10)
    s.add('em/panel', [R('em/panel/bg', px, py, pw, ph, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.4,
                         shadow=SHADOW_CARD),
                       T('em/panel/l', px + 24, py + 13, 200, 26, '임베딩 검색', size=15, color=INK, weight='b')] + sh +
          [R('em/panel/f', fx, fy, fw, fh, prst='roundRect', fill='F7F5FC', line=LINE, line_w=1.0)])
    qpt = 15.5
    S = qpt * 4 / 3
    qx, qy = fx + 20, fy + (fh - S * 1.2) / 2
    s.add('em/hl', [hl_band('em/hl', qx, qy, QUERY, QUERY, qpt, kind='low', alpha=36)])
    s.add('em/q', [T('em/q', qx, qy, fw - 30, S * 1.3, QUERY, size=qpt, color=INK)])
    # 벡터 줄
    vy = 270
    vec = '[0.80, 0.30, −0.83, 0.90, −0.02, …]'
    s.add('em/vt', thread('em/vt', [(qx + tw(QUERY, qpt) / 2, fy + fh + 2), (qx + tw(QUERY, qpt) / 2, vy - 4)], w=2.2))
    s.add('em/vl', [T('em/vl', px + 24, vy, 60, 30, '벡터', size=12.5, color=PURPLE, weight='b', anchor='ctr')])
    s.add('em/vec', [T('em/vec', px + 80, vy, 460, 30, vec, size=15, color=PURPLE, weight='m', anchor='ctr')])
    # 임베딩 공간(미리 만들어 둠)
    sx, sy, sw, sh_ = SPACE
    s.add('em/space', [R('em/space/bg', sx, sy, sw, sh_, prst='roundRect', radius=20, fill='FFFFFF', alpha=86, line=LINE2, line_w=1.2),
                       T('em/space/l', sx + 18, sy + 12, 200, 22, '임베딩 공간', size=11, color=PURPLE, weight='b')])
    rnd = random.Random(11)
    dots = []
    for i in range(30):
        while True:
            x_, y_ = sx + 24 + rnd.random() * (sw - 48), sy + 44 + rnd.random() * (sh_ - 64)
            if abs(x_ - STAR[0]) > 40 or abs(y_ - STAR[1]) > 40:
                break
        r_ = 3.2 + rnd.random() * 2.4
        dots.append(R('em/dot%d' % i, x_ - r_, y_ - r_, 2 * r_, 2 * r_, prst='ellipse', fill='CBC0EC', alpha=80, line=None))
    s.add('em/dots', dots)
    far = [('em/r_mail', 'mail', '관리비 고지서', sx + 24, sy + 40), ('em/r_cal', 'cal', '팀 회식', sx + 460, sy + 50),
           ('em/r_talk2', 'talk', '택배', sx + 30, sy + 272), ('em/r_note', 'note', '지은이네 주소', sx + 440, sy + 278),
           ('em/r_jieun', 'talk', '지은', sx + 492, sy + 150)]
    for k, kind, label, x_, y_ in far:
        prims, w_, h_ = mini_chip(k, x_, y_, kind, label, alpha=70)
        s.add(k, prims)
    memo, mw, mh = mini_chip('em/r_memo', STAR[0] - 182, STAR[1] - 64, 'note', '와인 메모', '산미 있는 화이트')
    pic, pw2, ph2 = mini_chip('em/r_pic', STAR[0] + 48, STAR[1] - 8, 'gallery', '와인 사진', '2026. 1. 9', img=PH['glass'][0])
    s.add('em/r_memo', memo)
    s.add('em/r_pic', pic)
    # 별·물결·가까운 원
    s.add('em/near', [R('em/near', STAR[0] - 132, STAR[1] - 108, 264, 216, prst='ellipse', fill=None, line=PURPLE2, line_w=1.8,
                        dash='dash')])
    s.add('em/ring1', [R('em/ring1', STAR[0] - 150, STAR[1] - 150, 300, 300, prst='ellipse', fill=None, line=RING, line_w=2.0)], temp=True)
    s.add('em/ring2', [R('em/ring2', STAR[0] - 150, STAR[1] - 150, 300, 300, prst='ellipse', fill=None, line=RING, line_w=1.6)], temp=True)
    s.add('em/star', star('em/star', *STAR) + [T('em/star/l', STAR[0] - 30, STAR[1] + 18, 60, 18, '질문', size=9.5, color=PURPLE,
                                                 weight='b', align='c')])
    memo_box = (STAR[0] - 182, STAR[1] - 64, mw, mh)
    pic_box = (STAR[0] + 48, STAR[1] - 8, pw2 + 8, ph2)
    s.add('em/k1', [ring_box('em/k1', memo_box, pad=4, radius=14, w=2.2)])
    s.add('em/k2', [ring_box('em/k2', pic_box, pad=4, radius=14, w=2.2)])
    s.add('em/n1', numdot('em/n1', memo_box[0] + 2, memo_box[1] + 2, 1, r=11, pt=9))
    s.add('em/n2', numdot('em/n2', pic_box[0] + 2, pic_box[1] + 2, 2, r=11, pt=9))
    s.add('em/foot', [T('em/foot', sx, sy + sh_ + 6, sw, 18, '가까울수록 뜻이 비슷한 기록', size=9.5, color=MUTE, align='r')])
    # 판정
    s.add('em/x1', xmark('em/x1', memo_box[0] - 18, memo_box[1] + memo_box[3] / 2, s=22, w=4.2))
    s.add('em/x2', xmark('em/x2', pic_box[0] + pic_box[2] + 18, pic_box[1] + pic_box[3] / 2, s=22, w=4.2))
    s.add('em/v1', tag_red('em/v1', memo_box[0] + memo_box[2] / 2 - 10, memo_box[1] - 38, '✕  집들이와 상관없는 와인 메모', pt=10))
    s.add('em/v2', tag_red('em/v2', pic_box[0] + pic_box[2] / 2, pic_box[1] + pic_box[3] + 10, '✕  집들이 날인지 알 수 없는 와인 사진', pt=10))
    # 효과
    s.on('em/div', 'fade_in', 200, 400)
    s.on('em/panel', 'rise', 300, 500, dy=14)
    s.on('em/q', 'fade_in', 500, 400)
    s.on('em/space', 'rise', 650, 500, dy=14)
    s.on(['em/dots', 'em/r_mail', 'em/r_cal', 'em/r_talk2', 'em/r_note', 'em/r_jieun', 'em/r_memo', 'em/r_pic'], 'fade_in', 900, 500)
    s.on('em/foot', 'fade_in', 1100, 400)
    s.click()   # 1: 질문 전체 → 벡터
    s.on('em/hl', 'wipe_in', 0, 650)
    s.on('em/vt', 'wipe_in', 550, 300, dir='down')
    s.on('em/vl', 'fade_in', 800, 250)
    s.on('em/vec', 'type', 850, 1, ms=26, n=len(vec))
    s.click()   # 2: 벡터를 공간에 → 원을 그리며 가장 가까운 것
    vx_, vy_ = px + 80 + tw(vec, 15) / 2, vy + 15
    s.on('em/star', 'fly', 0, 900, dx=vx_ - STAR[0], dy=vy_ - STAR[1], bend=0.12)
    s.on('em/ring1', 'jump', 850)
    s.on('em/ring1', 'ring', 850, 900, **{'from': 0.1, 'to': 1.0})
    s.on('em/ring2', 'jump', 1150)
    s.on('em/ring2', 'ring', 1150, 900, **{'from': 0.1, 'to': 1.0})
    s.on('em/near', 'zoom_in', 1350, 500, **{'from': 0.3})
    s.on(['em/k1', 'em/k2'], 'zoom_in', 1650, 400, **{'from': 1.12})
    s.on(['em/n1', 'em/n2'], 'pop', 1750, 380, **{'from': 0.4, 'over': 1.15})
    s.click()   # 3: 판정
    s.on(['em/r_memo', 'em/r_pic', 'em/k1', 'em/k2', 'em/n1', 'em/n2'], 'dim', 0, 380, to=0.3)
    s.on('em/x1', 'pop', 200, 420, **{'from': 0.3, 'over': 1.15})
    s.on('em/x2', 'pop', 300, 420, **{'from': 0.3, 'over': 1.15})
    s.on('em/v1', 'pop', 380, 450, **{'from': 0.5, 'over': 1.1})
    s.on('em/v2', 'pop', 480, 450, **{'from': 0.5, 'over': 1.1})
    return s


# ------------------------------------------------------------------ 4. Let's think step by step → 끊어진 고리
def step_title(y, size):
    return caption('step/title', [[("Let's think ", INK), ('step by step!', PURPLE)]], 640, y, size=size)


def s_step():
    s = Slide('step', trans=('fade', 600), bar=False, notes='그래서 필요한 건 한 단계씩 생각하는 검색입니다.')
    s.add('bg/blur', [P('bg/blur', str(OUT / 'blur_emb.png'), 0, 0, 1280, 720)])
    s.add('step/title', [step_title(306, 62)])
    s.on('step/title', 'pop', 200, 700, **{'from': 0.62, 'over': 1.06})
    return s


GAP = (452, 262, 376, 206)
CH_GAL = (874, 228, 360)


def chain_talk(x, y, w=356):
    return card('ch/talk', 'talk', x, y, w, '지은', '카카오톡 · 3월 15일 (일) 오후 4:12', ['박스 정리 다 했어! 이따 올 때', '휴지 안 사 와도 돼'],
                pt=12.5, title_pt=14)


def s_chain():
    s = Slide('chain', trans=('morph', 1000),
              notes=('질문과 정답 사이에 끊어진 고리가 있습니다. (클릭) Weave는 먼저 지은이의 카톡에서 박스 정리 다 했어, 휴지 안 사 와도 돼를 보고 '
                    '3월 15일이 집들이였다는 걸 알아냅니다. (클릭) 그 날짜로 갤러리를 다시 찾으면 그날 와인 사진이 나옵니다. '
                    '(클릭) 그럼 이 중간 단서를 Weave는 어떻게 찾아낼까요?'))
    s.add('step/title', [step_title(78, 30)])
    pill, txt, _, _ = search_pill('ch/sp', 46, 336, 360, 60, QUERY, pt=14.5, icon='spool', cursor=False)
    s.add('ch/sp', pill + [txt])
    gx, gy, gw, gh = GAP
    s.add('ch/gap', [R('ch/gap/bg', gx, gy, gw, gh, prst='roundRect', radius=24, fill=LAV2, alpha=80, line=PURPLE2, line_w=2.2,
                       dash='dash')])
    s.add('ch/gapq', [T('ch/gapq/q', gx, gy + 22, gw, 96, '?', size=70, color=PURPLE, weight='b', align='c', anchor='ctr'),
                      T('ch/gapq/l', gx, gy + 122, gw, 44, '끊어진 고리', size=24, color=PURPLE, weight='b', align='c', anchor='ctr')],
          temp=True)
    cx_, cy_, cw_ = CH_GAL
    gal = gallery('ch/gal', cx_, cy_, cw_, [PH[k] for k in WINE4], cols=2, show_dates=False, ph=104, gap=10)
    s.add('ch/gal', gal[0])
    spots = gal[2]
    # 실(점선 → 이어지면 실선)
    a1, b1 = (46 + 360, 366), (gx, gy + gh / 2)
    a2, b2 = (gx + gw, gy + gh / 2), (cx_, cy_ + gal[1] / 2)
    s.add('ch/l1', [C('ch/l1', scurve(a1, b1), w=2.2, color='C9BEEB', dash='dash')])
    s.add('ch/l2', [C('ch/l2', scurve(a2, b2), w=2.2, color='C9BEEB', dash='dash')])
    s.add('ch/s1', thread('ch/s1', scurve(a1, b1), w=2.6))
    s.add('ch/s2', thread('ch/s2', scurve(a2, b2), w=2.6))
    talk = chain_talk(gx + 12, gy + 26, gw - 24)
    s.add('ch/talk', talk[0])
    tp = talk[2]
    s.add('ch/h1', [band('ch/h1', tp[0], '박스 정리')])
    s.add('ch/h2', [band('ch/h2', tp[1], '휴지 안 사 와도 돼')])
    s.add('ch/hd', [band('ch/hd', tp['meta'], '3월 15일', alpha=40)])
    s.add('ch/qb1', qbadge('ch/qb1', gx + gw / 2, gy - 58, '집들이가 언제였지?', pt=13))
    s.add('ch/qb2', qbadge('ch/qb2', cx_ + cw_ / 2, cy_ - 58, '그날 찍은 와인 사진은?', pt=13))
    # 날짜(클릭 2에 나타남)
    dl = []
    for i, (px_, py_, pw_, ph_) in enumerate(spots):
        d = PH[WINE4[i]][1]
        dl.append(T('ch/d%d' % i, px_ + 6, py_ + ph_ - 26, pw_ - 12, 20, d, size=9.5, color='FFFFFF', weight='b', align='r',
                    fill='1C1A24', fill_alpha=55, radius=6))
    s.add('ch/dates', dl)
    wi = WINE4.index('babich')
    win = spots[wi]
    s.add('ch/dim', [dim_over('ch/dim%d' % i, sp, radius=10, alpha=68) for i, sp in enumerate(spots) if i != wi])
    s.add('ch/pring', [ring_box('ch/pring', win, pad=4, radius=12, w=3.0)])
    # 날짜 토큰: 카톡 날짜 → 사진 날짜
    tok, tw_ = chip('ch/tok', 0, 0, '3월 15일', 'fill', pt=11, h=28, padx=12)
    tx_, ty_ = win[0] + win[2] / 2 - tw_ / 2, win[1] + win[3] / 2 - 14
    tok, _ = chip('ch/tok', tx_, ty_, '3월 15일', 'fill', pt=11, h=28, padx=12)
    s.add('ch/tok', tok, temp=True)
    mx, my = tp['meta'][0] + tw('카카오톡 · ', 9.5), tp['meta'][1]
    ans, aw = chip('ch/ans', cx_ + cw_ / 2, cy_ + gal[1] + 16, '배비치 소비뇽 블랑', 'fill', pt=13, h=34, padx=16, align='c')
    s.add('ch/ans', ans)
    s.add('ch/bridge', [caption('ch/bridge', [[('이 중간 단서를, ', INK), ('Weave는 어떻게 찾아낼까요?', PURPLE)]], 640, 600, size=26)])
    # 효과
    s.on('ch/sp', 'rise', 150, 500, dy=14)
    s.on('ch/l1', 'wipe_in', 450, 400)
    s.on('ch/gap', 'rise', 600, 500, dy=14)
    s.on('ch/gapq', 'jump', 650)
    s.on('ch/gapq', 'fade_in', 650, 450)
    s.on('ch/l2', 'wipe_in', 900, 400)
    s.on('ch/gal', 'rise', 1050, 500, dy=14)
    s.click()   # 1: 카톡이 고리를 채움
    s.on('ch/gapq', 'fade_out', 0, 250)
    s.on('ch/qb1', 'pop', 0, 420, **{'from': 0.6, 'over': 1.08})
    s.on('ch/talk', 'zoom_in', 250, 500, **{'from': 0.86})
    s.on('ch/s1', 'wipe_in', 300, 450)
    s.on('ch/h1', 'wipe_in', 900, 350)
    s.on('ch/h2', 'wipe_in', 1150, 450)
    s.on('ch/hd', 'wipe_in', 1750, 350)
    s.click()   # 2: 날짜 → 갤러리 → 그날 와인 사진
    s.on('ch/tok', 'fly', 0, 1000, dx=mx + 30 - tx_, dy=my - ty_, bend=0.22)
    s.on('ch/s2', 'wipe_in', 100, 600)
    s.on('ch/qb2', 'pop', 150, 420, **{'from': 0.6, 'over': 1.08})
    s.on('ch/tok', 'fade_out', 1050, 250)
    s.on('ch/dates', 'fade_in', 1000, 350)
    s.on('ch/dim', 'fade_in', 1250, 400)
    s.on('ch/pring', 'zoom_in', 1250, 450, **{'from': 1.1})
    s.on('ch/ans', 'pop', 1750, 450, **{'from': 0.6, 'over': 1.08})
    s.click()   # 3: 이 중간 단서를 어떻게?
    s.on(['ch/sp', 'ch/gal', 'ch/dates', 'ch/dim', 'ch/pring', 'ch/ans', 'ch/qb2', 'ch/s2', 'ch/s1', 'ch/l1', 'ch/l2', 'ch/gap'], 'dim',
         0, 450, to=0.25)
    s.on('ch/talk', 'pulse', 250, 300, scale=1.04)
    s.on('ch/bridge', 'rise', 300, 550, dy=16)
    return s


# ------------------------------------------------------------------ 5. 00 데이터 색인
IDX = (500, 232, 724, 300)


def s_idx():
    s = Slide('idx', trans=('morph', 1000), cur='00',
              notes='먼저 Weave는 평소에 기록을 색인해 둡니다. (클릭) 문장의 뜻은 벡터로, 날짜와 앱 같은 정보는 메타데이터로 나눠 저장합니다.')
    s.add('idx/cap', [caption('idx/cap', [[('Weave는 ', INK), ('평소에', PURPLE), (' 기록을 색인해 둡니다', INK)]], 640, 86, size=26)])
    s.add('idx/cap2', [caption('idx/cap2', [[('뜻은 벡터로, 날짜와 앱은 메타데이터로', SUB)]], 640, 132, size=17)])
    talk = chain_talk(56, 300, 360)
    s.add('ch/talk', talk[0])
    x, y, w, h = IDX
    s.add('idx/st2', [R('idx/st2', x + 20, y + 20, w, h, prst='roundRect', radius=22, fill='FFFFFF', alpha=50, line=LINE, line_w=1)])
    s.add('idx/st1', [R('idx/st1', x + 10, y + 10, w, h, prst='roundRect', radius=22, fill='FFFFFF', alpha=75, line=LINE, line_w=1)])
    s.add('idx/arr', thread('idx/arr', scurve((416, 370), (x - 4, 380)), w=2.6))
    rows_y = [y + 84, y + 158, y + 232]
    s.add('idx/card', [R('idx/card/bg', x, y, w, h, prst='roundRect', radius=22, fill='FFFFFF', line=RING, line_w=2.2, glow=(10, RING, 22),
                         shadow=SHADOW_LIFT),
                       P('idx/card/ic', ICON['spool'], x + 26, y + 22, 30, 30),
                       T('idx/card/t', x + 66, y + 22, 300, 30, 'Hybrid Index', size=16, color=PURPLE, weight='b', anchor='ctr'),
                       T('idx/card/s', x + 66 + tw('Hybrid Index', 16, 'b') + 12, y + 22, 200, 30, '기기 안 색인', size=11, color=MUTE,
                         anchor='ctr'),
                       R('idx/card/s1', x + 26, rows_y[1] - 18, w - 52, 1, fill='EEE9F8', line=None),
                       R('idx/card/s2', x + 26, rows_y[2] - 18, w - 52, 1, fill='EEE9F8', line=None)])
    lab = dict(size=12.5, color=SUB, weight='b', anchor='ctr')
    s.add('idx/l0', [T('idx/l0', x + 30, rows_y[0], 110, 34, '원문', **lab)])
    s.add('idx/r0', [T('idx/r0', x + 150, rows_y[0], w - 170, 34, '박스 정리 다 했어! 이따 올 때 휴지 안 사 와도 돼', size=13, color=BODY,
                       anchor='ctr')])
    vec = '[0.86, −0.08, 0.33, 0.46, 0.60, 0.83, 0.90, …]'
    meta = '{ date: "2026-03-15", app: "kakaotalk", … }'
    s.add('idx/l1', [T('idx/l1', x + 30, rows_y[1], 110, 34, '벡터', size=12.5, color=PURPLE, weight='b', anchor='ctr')])
    s.add('idx/r1', [T('idx/r1', x + 150, rows_y[1], w - 170, 34, vec, size=15, color=PURPLE, weight='m', anchor='ctr')])
    s.add('idx/l2', [T('idx/l2', x + 30, rows_y[2], 110, 34, '메타데이터', size=12.5, color=PURPLE, weight='b', anchor='ctr')])
    s.add('idx/r2', [T('idx/r2', x + 150, rows_y[2], w - 170, 34, meta, size=15, color=INK, weight='m', anchor='ctr')])
    s.on(['idx/st2', 'idx/st1'], 'fade_in', 200, 500)
    s.on('idx/card', 'rise', 250, 550, dy=14)
    s.on('idx/arr', 'wipe_in', 500, 450)
    s.on(['idx/l0', 'idx/r0'], 'fade_in', 750, 400)
    s.click()
    s.on('idx/cap2', 'rise', 0, 450, dy=12)
    s.on('idx/l1', 'fade_in', 150, 300)
    s.on('idx/r1', 'type', 250, 1, ms=24, n=len(vec))
    s.on('idx/l2', 'fade_in', 1300, 300)
    s.on('idx/r2', 'type', 1400, 1, ms=24, n=len(meta))
    return s


# ------------------------------------------------------------------ 6. 01 상황 인식 · 02 질의 재작성
TR_SP = (64, 176, 548, 70)
KB = (64, 266, 548, 337)
SPOOL = (KB[0] + 102 * KB[2] / 1300, KB[1] + 82 * KB[3] / 800)
HAND_H = 214


def trig_parts(alpha=100):
    out = []
    x, y, w, h = TR_SP
    pill, txt, cur, tx0 = search_pill('tr/sp', x, y, w, h, QUERY, pt=17.5)
    out.append(('tr/sp', pill))
    out.append(('tr/kb', [P('tr/kb', str(AS / 'keyboard.png'), *KB, radius=18, shadow=SHADOW_CARD)]))
    hw = HAND_H * 773 / 960
    hx, hy = SPOOL[0] - hw * 0.388, SPOOL[1] - HAND_H * 0.015 + 8
    out.append(('tr/glow', [R('tr/glow', SPOOL[0] - 30, SPOOL[1] - 30, 60, 60, prst='ellipse', fill=None, line=PURPLE, line_w=3,
                              glow=(14, RING, 50))]))
    out.append(('tr/wave', [R('tr/wave', SPOOL[0] - 60, SPOOL[1] - 60, 120, 120, prst='ellipse', fill=None, line=RING, line_w=2.4)]))  # temp
    out.append(('tr/hand', [P('tr/hand', str(AS / 'hand.png'), hx, hy, hw, HAND_H)]))
    return out, txt, cur, tx0


def s_trig():
    s = Slide('trig', trans=('morph', 1000), cur='01', done={'00'},
              notes='그리고 검색하다 막히면 (클릭) 키보드의 실타래 버튼을 누릅니다. Weave는 검색창의 질문을 그대로 받아 옵니다.')
    parts, txt, cur, tx0 = trig_parts()
    pm = dict(parts)
    s.add('tr/sp', pm['tr/sp'])
    s.add('q/text', [txt])
    s.add('tr/kb', pm['tr/kb'])
    s.add('tr/glow', pm['tr/glow'])
    s.add('tr/wave', pm['tr/wave'], temp=True)
    s.add('tr/hand', pm['tr/hand'])
    x, y, w, h = TR_SP
    s.add('tr/qhl', [hl_band('tr/qhl', tx0, y + (h - 17.5 * 4 / 3 * 1.4) / 2 + 3, QUERY, QUERY, 17.5, kind='low', alpha=34)])
    s.add('tr/cap', [caption('tr/cap', [[('검색하다 막히면', INK)], [('실타래 버튼을 누릅니다', PURPLE)]], 690, 352, size=30, align='l')])
    s.on('tr/cap', 'rise', 300, 550, dy=16)
    s.click()
    s.on('tr/hand', 'fly', 0, 700, dx=170, dy=230, bend=0.1)
    s.on('tr/hand', 'pulse', 760, 140, scale=0.93)
    s.on('tr/glow', 'zoom_in', 860, 300, **{'from': 0.6})
    s.on('tr/wave', 'jump', 880)
    s.on('tr/wave', 'ring', 880, 800, **{'from': 0.4, 'to': 1.0})
    s.on('tr/qhl', 'wipe_in', 1150, 600)
    return s


QR = (652, 152, 576, 420)


def qr_full():
    """02 장의 Query Rewriting 판(크게)."""
    x, y, w, h = QR
    out = [('sp/card', [R('sp/card/bg', x, y, w, h, prst='roundRect', radius=22, fill='FFFFFF', line=RING, line_w=2.2, glow=(10, RING, 22),
                          shadow=SHADOW_LIFT),
                        P('sp/card/ic', ICON['spool'], x + 24, y + 20, 30, 30),
                        T('sp/card/t', x + 62, y + 20, 300, 30, 'Query Rewriting', size=17, color=PURPLE, weight='b', anchor='ctr'),
                        T('sp/card/s', x + 62 + tw('Query Rewriting', 17, 'b') + 12, y + 20, 200, 30, '질의 재작성', size=11, color=MUTE,
                          anchor='ctr'),
                        T('sp/card/l', x + 26, y + 70, 200, 20, '처음 질문', size=10.5, color=MUTE, weight='b')])]
    return out


def s_split():
    s = Slide('split', trans=('morph', 1000), cur='02', done={'00', '01'},
              notes='Weave는 이 질문을 단서 순서대로 둘로 나눕니다. (클릭) 지은이네 집들이가 언제였는지 먼저 묻고, '
                    '마셨던 와인은 그날을 빈칸으로 남겨 둡니다.')
    parts, txt, cur, tx0 = trig_parts()
    pm = dict(parts)
    for k in ('tr/sp', 'tr/kb', 'tr/hand'):
        s.add(k, pm[k], alpha=30)
    x, y, w, h = TR_SP
    s.add('tr/q2', [T('tr/q2', tx0, txt[3], w - (tx0 - x) - 20, txt[5], QUERY, size=17.5, color=INK, anchor='ctr', alpha=30)])
    for k, prims in qr_full():
        s.add(k, prims)
    qx, qy, qw, qh = QR
    qpt = 17
    S = qpt * 4 / 3
    tqx, tqy = qx + 26, qy + 94
    s.add('q/text', [T('q/text', tqx, tqy, qw - 40, S * 1.4, QUERY, size=qpt, color=INK)])
    qpos = (tqx, tqy, QUERY, qpt, 'r')
    b1 = band('sp/b1', qpos, '지은이네 집들이', alpha=36)
    b2 = hl_band('sp/b2', tqx, tqy, QUERY, '때 마셨던 와인', qpt, color=BLUE_HL, alpha=40)
    s.add('sp/b1', [b1])
    s.add('sp/b2', [b2])
    s.add('sp/n1', numdot('sp/n1', b1[2] + b1[4] / 2, b1[3] + b1[5] + 20, 1, r=12, pt=9.5))
    s.add('sp/n2', numdot('sp/n2', b2[2] + b2[4] / 2, b2[3] + b2[5] + 20, 2, r=12, pt=9.5, fill=BLUE))
    r1y, r2y, ay = qy + 176, qy + 256, qy + 344
    s.add('sp/r1', [R('sp/r1/bg', qx + 22, r1y, qw - 44, 58, prst='roundRect', radius=14, fill=LAV, line=None)] +
          numdot('sp/r1/n', qx + 50, r1y + 29, 1, r=14, pt=11) +
          [T('sp/r1/t', qx + 76, r1y, qw - 110, 58, '지은이네 집들이는 언제였지?', size=17, color=INK, weight='m', anchor='ctr')])
    blank, bw_ = chip('sp/r2/b', qx + 76, r2y + 15, '그날', 'dash', pt=13, h=30, padx=12)
    s.add('sp/r2', [R('sp/r2/bg', qx + 22, r2y, qw - 44, 58, prst='roundRect', radius=14, fill=BLUE_BG, line=None)] +
          numdot('sp/r2/n', qx + 50, r2y + 29, 2, r=14, pt=11, fill=BLUE) + blank +
          [T('sp/r2/t', qx + 76 + bw_ + 6, r2y, qw - 110 - bw_, 58, '마셨던 와인은?', size=17, color=INK, weight='m', anchor='ctr')])
    s.add('sp/ans', [T('sp/ans/l', qx + 30, ay, 40, 30, '답', size=13, color=MUTE, weight='b', anchor='ctr'),
                     R('sp/ans/slot', qx + 76, ay + 1, 190, 28, prst='roundRect', fill='FFFFFF', line=PURPLE2, line_w=1.2, dash='dash')])
    s.add('sp/cap', [caption('sp/cap', [[('질문을 단서 순서대로 ', INK), ('둘로 나눕니다', PURPLE)]], qx + qw / 2, 92, size=24)])
    s.on('sp/cap', 'rise', 200, 500, dy=14)
    s.click()
    s.on('sp/b1', 'wipe_in', 0, 450)
    s.on('sp/n1', 'pop', 250, 380, **{'from': 0.4, 'over': 1.15})
    s.on('sp/r1', 'rise', 500, 450, dy=14)
    s.on('sp/b2', 'wipe_in', 1300, 450)
    s.on('sp/n2', 'pop', 1550, 380, **{'from': 0.4, 'over': 1.15})
    s.on('sp/r2', 'rise', 1800, 450, dy=14)
    s.on('sp/ans', 'fade_in', 2400, 400)
    return s


# ------------------------------------------------------------------ 7. 03 연쇄 탐색: Hop 1, Hop 2
QC = (40, 134, 420, 240)           # 작게 왼쪽 위로 옮긴 Query Rewriting 판
H1 = (40, 392, 420, 118)
H2 = (40, 528, 420, 118)


def qr_small(state='hop1', alpha=100):
    """왼쪽 위 작은 Query Rewriting 판. state: hop1(②는 빈칸) / hop2(②에 날짜) / done(답까지)."""
    x, y, w, h = QC
    out = [R('sp/card/bg', x, y, w, h, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.4, shadow=SHADOW_CARD),
           P('sp/card/ic', ICON['spool'], x + 18, y + 14, 24, 24),
           T('sp/card/t', x + 48, y + 14, 220, 24, 'Query Rewriting', size=13.5, color=PURPLE, weight='b', anchor='ctr'),
           T('sp/card/s', x + 48 + tw('Query Rewriting', 13.5, 'b') + 10, y + 14, 120, 24, '질의 재작성', size=9.5, color=MUTE,
             anchor='ctr'),
           T('sp/card/l', x + 20, y + 48, 200, 18, '처음 질문', size=9, color=MUTE, weight='b')]
    q_ = [T('q/text', x + 20, y + 64, w - 30, 22, QUERY, size=12.5, color=INK)]
    r1y, r2y, ay = y + 98, y + 146, y + 196
    r1 = [R('sp/r1/bg', x + 14, r1y, w - 28, 40, prst='roundRect', radius=12, fill=LAV, line=None)] + \
        numdot('sp/r1/n', x + 36, r1y + 20, 1, r=11, pt=9) + \
        [T('sp/r1/t', x + 56, r1y, w - 80, 40, '지은이네 집들이는 언제였지?', size=12.5, color=INK, weight='m', anchor='ctr')]
    if state == 'hop1':
        blank, bw_ = chip('sp/r2/b', x + 56, r2y + 8, '그날', 'dash', pt=10.5, h=24, padx=9)
    else:
        blank, bw_ = chip('sp/r2/b', x + 56, r2y + 8, '3/15 (일)', 'fill', pt=10.5, h=24, padx=9)
    r2 = [R('sp/r2/bg', x + 14, r2y, w - 28, 40, prst='roundRect', radius=12, fill=BLUE_BG, line=None)] + \
        numdot('sp/r2/n', x + 36, r2y + 20, 2, r=11, pt=9, fill=BLUE) + blank + \
        [T('sp/r2/t', x + 56 + bw_ + 5, r2y, w - 90 - bw_, 40, '마셨던 와인은?', size=12.5, color=INK, weight='m', anchor='ctr')]
    an = [T('sp/ans/l', x + 22, ay, 30, 28, '답', size=11, color=MUTE, weight='b', anchor='ctr'),
          R('sp/ans/slot', x + 56, ay + 1, tw('배비치 소비뇽 블랑', 11, 'b') + 20, 26, prst='roundRect', fill='FFFFFF', line=PURPLE2,
            line_w=1.2, dash='dash')]
    return out, q_, r1, r2, an, (r1y, r2y, ay)


def re_card(key, box, hop, query_runs, active=True, done=False, alpha=100):
    x, y, w, h = box
    ln = (RING, 2.2) if active else (LINE, 1.2)
    out = [R(key + '/bg', x, y, w, h, prst='roundRect', radius=20, fill='FFFFFF', line=ln[0], line_w=ln[1],
             glow=(10, RING, 22) if active else None, shadow=SHADOW_CARD),
           T(key + '/t', x + 20, y + 14, 260, 24, 'Reasoning Embedding', size=13.5, color=PURPLE if active else SUB, weight='b',
             anchor='ctr')]
    hc, hw_ = chip(key + '/hop', x + w - 20 - (tw('Hop %d' % hop, 10, 'b') + 22), y + 14, 'Hop %d' % hop, 'fill' if active else 'outline',
                   pt=10, h=24, padx=11)
    out += hc
    out.append(R(key + '/f', x + 16, y + 52, w - 32, 48, prst='roundRect', radius=14, fill='F7F5FC', line=LINE, line_w=1.0))
    tx = x + 32
    for i, (t, st) in enumerate(query_runs):
        if st == 'tok':
            c, cw = chip(key + '/tok', tx, y + 64, t, 'fill', pt=11, h=26, padx=10)
            out += c
            tx += cw + 6
        else:
            out.append(T(key + '/q%d' % i, tx, y + 52, w - (tx - x) - 20, 48, t, size=13.5, color=INK if active else MUTE, weight='m',
                         anchor='ctr'))
            tx += tw(t, 13.5, 'm')
    if done:
        out.append(T(key + '/ok', x + w - 46, y + 60, 30, 32, '✓', size=16, color=PURPLE, weight='b', align='c', anchor='ctr'))
    return out


H1_SPACE = (490, 134, 750, 524)
H1_STAR = (780, 404)
H1_CARD = (944, 300, 286)


def s_hop1():
    s = Slide('hop1', trans=('morph', 1100), cur='03', done={'00', '01', '02'},
              notes=('첫 질문을 일반 임베딩으로 찾으면, 다른 사람의 집들이 일정이나 주소 메모처럼 단어가 겹치는 기록이 가깝습니다. '
                    '(클릭) Reasoning Embedding은 휴지 안 사 와도 돼가 집들이 초대라는 걸 알아보고, 지은이의 카톡을 가장 가까이 둡니다. '
                    '(클릭) 이 카톡을 받은 날, 3월 15일이 다음 단서가 됩니다.'))
    card_, q_, r1, r2, an, (r1y, r2y, ay) = qr_small('hop1')
    for p_ in card_:
        s.add(p_[1], [p_])
    s.add('q/text', q_)
    s.add('sp/r1', r1)
    s.add('sp/r2', r2)
    s.add('sp/ans', an)
    s.add('h1/re', re_card('h1/re', H1, 1, [('지은이네 집들이는 언제였지?', 'q')]))
    s.add('h2/re', re_card('h2/re', H2, 2, [('그날 마셨던 와인은?', 'q')], active=False), alpha=45)
    # ① → Hop 1: 판 왼쪽 바깥으로 도는 화살표
    s.add('h1/c', thread('h1/c', [(QC[0] + 14, r1y + 20), (QC[0] - 22, r1y + 20), (H1[0] - 22, H1[1] + 30), (H1[0] - 2, H1[1] + 30)],
                         w=2.2, tail='triangle'))
    s.add('h1/cap', [caption('h1/cap', [[('Reasoning Embedding', PURPLE), ('은 답이 될 기록을 가까이 둡니다', INK)]], 640, 80, size=22)])
    sx, sy, sw, sh = H1_SPACE
    s.add('h1/space', [R('h1/space/bg', sx, sy, sw, sh, prst='roundRect', radius=22, fill='FFFFFF', alpha=88, line=LINE2, line_w=1.2)])
    tx0, ty0 = sx + 20, sy + 16
    wa, wb = tw('일반 임베딩', 11, 'b') + 28, tw('Reasoning Embedding', 11, 'b') + 28
    s.add('h1/togbg', [R('h1/tog/bg', tx0, ty0, wa + wb + 8, 36, prst='roundRect', fill='F1EEF8', line=None)])
    s.add('h1/togA', [R('h1/togA/k', tx0 + 4, ty0 + 4, wa, 28, prst='roundRect', fill='8E88A0', line=None),
                      T('h1/togA/a', tx0 + 4, ty0 + 4, wa, 28, '일반 임베딩', size=11, color='FFFFFF', weight='b', align='c', anchor='ctr'),
                      T('h1/togA/b', tx0 + 4 + wa, ty0 + 4, wb, 28, 'Reasoning Embedding', size=11, color=MUTE, weight='b', align='c',
                        anchor='ctr')])
    s.add('h1/togB', [R('h1/togB/bgc', tx0 + 2, ty0 + 2, wa + wb + 4, 32, prst='roundRect', fill='F1EEF8', line=None),
                      R('h1/togB/k', tx0 + 4 + wa, ty0 + 4, wb, 28, prst='roundRect', fill=PURPLE, line=None, glow=(8, RING, 30)),
                      T('h1/togB/a', tx0 + 4, ty0 + 4, wa, 28, '일반 임베딩', size=11, color=MUTE, weight='b', align='c', anchor='ctr'),
                      T('h1/togB/b', tx0 + 4 + wa, ty0 + 4, wb, 28, 'Reasoning Embedding', size=11, color='FFFFFF', weight='b', align='c',
                        anchor='ctr')])
    rnd = random.Random(23)
    dots = []
    for i in range(30):
        while True:
            x_, y_ = sx + 26 + rnd.random() * (sw - 52), sy + 70 + rnd.random() * (sh - 96)
            if (x_ - H1_STAR[0]) ** 2 / 175 ** 2 + (y_ - H1_STAR[1]) ** 2 / 135 ** 2 > 1 and not (
                    H1_CARD[0] - 10 < x_ < H1_CARD[0] + H1_CARD[2] + 10 and H1_CARD[1] - 50 < y_ < H1_CARD[1] + 170):
                break
        r_ = 3.2 + rnd.random() * 2.4
        dots.append(R('h1/dot%d' % i, x_ - r_, y_ - r_, 2 * r_, 2 * r_, prst='ellipse', fill='CBC0EC', alpha=80, line=None))
    s.add('h1/dots', dots)
    for k, kind, label, x_, y_ in (('h1/f1', 'mail', '관리비 고지서', 1040, 184), ('h1/f2', 'talk', '택배', 1100, 540),
                                   ('h1/f3', 'cal', '팀 회식', 770, 600), ('h1/f4', 'note', '와인 메모', 940, 600)):
        prims, w_, h_ = mini_chip(k, x_, y_, kind, label, alpha=60)
        s.add(k, prims)
    s.add('h1/near', [R('h1/near', H1_STAR[0] - 150, H1_STAR[1] - 115, 300, 230, prst='ellipse', fill=None, line=PURPLE2, line_w=1.8,
                        dash='dash')])
    # 마지막 자리(Reasoning Embedding)에 놓고, 장이 열리면 처음 자리(일반 임베딩)로 옮겨 둠
    d1i, d1f = (650, 318), (512, 214)
    d2i, d2f = (796, 436), (540, 566)
    ki, kf = (1030, 566), (806, 432)
    d1, d1w, d1h = mini_chip('h1/d1', d1f[0], d1f[1], 'cal', '성빈이 신혼집들이', '2025. 10. 18 (토)')
    d2, d2w, d2h = mini_chip('h1/d2', d2f[0], d2f[1], 'note', '지은이네 주소', '경기도 수원시…')
    kk, kw_, kh_ = mini_chip('h1/k', kf[0], kf[1], 'talk', '지은', '박스 정리 다 했어!…')
    off = lambda a, b: (a[0] - b[0], a[1] - b[1])
    s.add('h1/d1', d1, start=off(d1i, d1f))
    s.add('h1/d2', d2, start=off(d2i, d2f))
    s.add('h1/k', kk, start=off(ki, kf))
    s.add('h1/star', star('h1/star', *H1_STAR))
    s.add('h1/starl', chip('h1/starl', H1_STAR[0] + 20, H1_STAR[1] - 44, '질문 ①', 'soft', pt=9.5, h=22, padx=8)[0])
    s.add('h1/x1', xmark('h1/x1', d1f[0] + d1w + 18, d1f[1] + d1h / 2, s=22, w=4))
    s.add('h1/x2', xmark('h1/x2', d2f[0] + d2w + 18, d2f[1] + d2h / 2, s=22, w=4))
    s.add('h1/kring', [ring_box('h1/kring', (kf[0], kf[1], kw_, kh_), pad=4, radius=14, w=2.4)])
    cx_, cy_, cw_ = H1_CARD
    talk = card('h1/card', 'talk', cx_, cy_, cw_, '지은', '카카오톡 · 3월 15일 (일) 오후 4:12', ['박스 정리 다 했어! 이따 올 때', '휴지 안 사 와도 돼'],
                pt=11.5, title_pt=13)
    s.add('h1/link', thread('h1/link', scurve((kf[0] + kw_, kf[1] + kh_ / 2), (cx_, cy_ + 70)), w=2.2))
    s.add('h1/card', talk[0])
    tp = talk[2]
    s.add('h1/h1', [band('h1/h1', tp[0], '박스 정리')])
    s.add('h1/h2', [band('h1/h2', tp[1], '휴지 안 사 와도 돼')])
    s.add('h1/hd', [band('h1/hd', tp['meta'], '3월 15일', alpha=40)])
    tok, tw_ = chip('h1/tok', cx_ + cw_ - 104, cy_ - 42, '3/15 (일)', 'fill', pt=12, h=30, padx=12)
    s.add('h1/tok', tok)
    s.add('h1/foot', [T('h1/foot', sx, sy + sh + 6, sw, 18, '가까울수록 뜻이 비슷한 기록', size=9.5, color=MUTE, align='r')])
    # 효과
    s.on(['h1/d1', 'h1/d2', 'h1/k'], 'fade_in', 0, 300)
    s.on(['h1/d1', 'h1/d2', 'h1/k'], 'goto', 0)
    s.on('h1/cap', 'rise', 200, 500, dy=14)
    s.on('h1/re', 'rise', 300, 500, dy=14)
    s.on('h1/c', 'wipe_in', 600, 400, dir='down')
    s.click()   # 1: Reasoning Embedding으로 바꾸면 자리가 바뀜
    s.on('h1/togB', 'fade_in', 0, 350)
    s.on('h1/d1', 'fly', 250, 1000, dx=d1i[0] - d1f[0], dy=d1i[1] - d1f[1], bend=0.1, show=False, fade=False)
    s.on('h1/d2', 'fly', 250, 1000, dx=d2i[0] - d2f[0], dy=d2i[1] - d2f[1], bend=-0.1, show=False, fade=False)
    s.on(['h1/d1', 'h1/d2'], 'dim', 900, 400, to=0.4)
    s.on('h1/k', 'fly', 350, 1100, dx=ki[0] - kf[0], dy=ki[1] - kf[1], bend=0.15, show=False, fade=False)
    s.on('h1/kring', 'zoom_in', 1450, 400, **{'from': 1.15})
    s.on(['h1/x1', 'h1/x2'], 'pop', 1350, 380, **{'from': 0.3, 'over': 1.15})
    s.click()   # 2: 카톡을 읽어 날짜 단서
    s.on('h1/link', 'wipe_in', 0, 350)
    s.on('h1/card', 'zoom_in', 200, 500, **{'from': 0.8})
    s.on('h1/h1', 'wipe_in', 750, 350)
    s.on('h1/h2', 'wipe_in', 1000, 450)
    s.on('h1/hd', 'wipe_in', 1550, 350)
    s.on('h1/tok', 'pop', 1850, 420, **{'from': 0.5, 'over': 1.1})
    return s


H2_TALK = (520, 150, 330)
H2_GAL = (500, 404, 736)
H2_PHOTOS = ['babich', 'table', 'w3', 'w2', 'w1']


def s_hop2():
    s = Slide('hop2', trans=('morph', 1100), cur='03', done={'00', '01', '02'},
              notes='찾은 날짜를 빈칸에 넣어 질문을 다시 씁니다. (클릭) 날짜는 메타데이터로 걸러 그날 사진만 남기고, '
                    '(클릭) 와인이 보이는 사진의 라벨을 읽어 배비치 소비뇽 블랑을 찾습니다.')
    card_, q_, r1, r2, an, (r1y, r2y, ay) = qr_small('hop2')
    for p_ in card_:
        s.add(p_[1], [p_])
    s.add('q/text', q_)
    s.add('sp/r1', r1)
    s.add('sp/r2', [p_ for p_ in r2 if not p_[1].startswith('sp/r2/b')])
    s.add('sp/ans', an)
    s.add('h1/re', re_card('h1/re', H1, 1, [('지은이네 집들이는 언제였지?', 'q')], active=False, done=True))
    s.add('h2/re', re_card('h2/re', H2, 2, [('3/15 (일)', 'tok'), ('마셨던 와인은?', 'q')]))
    s.add('h2/cap', [caption('h2/cap', [[('찾은 날짜로 그날 사진만 남기고, ', INK), ('라벨에서 이름을 읽습니다', PURPLE)]], 640, 80, size=22)])
    # Hop 1 결과(카톡) — 오른쪽 위. 날짜 토큰이 ② 빈칸으로(모핑)
    tx, ty, tww = H2_TALK
    talk = card('h1/card', 'talk', tx, ty, tww, '지은', '카카오톡 · 3월 15일 (일) 오후 4:12', ['박스 정리 다 했어! 이따 올 때', '휴지 안 사 와도 돼'],
                pt=11.5, title_pt=13)
    s.add('h1/card', talk[0])
    tp = talk[2]
    s.add('h1/h1', [band('h1/h1', tp[0], '박스 정리')])
    s.add('h1/h2', [band('h1/h2', tp[1], '휴지 안 사 와도 돼')])
    s.add('h1/hd', [band('h1/hd', tp['meta'], '3월 15일', alpha=40)])
    x, y, w, h = QC
    tok, _ = chip('h1/tok', x + 56, r2y + 8, '3/15 (일)', 'fill', pt=10.5, h=24, padx=9)
    s.add('h1/tok', tok)
    s.add('h2/back', thread('h2/back', scurve((tx, ty + 30), (x + w + 2, r2y + 20), 0.45), w=2.2, tail='triangle'))
    s.add('h2/c', thread('h2/c', [(x + 14, r2y + 20), (x - 22, r2y + 20), (H2[0] - 22, H2[1] + 30), (H2[0] - 2, H2[1] + 30)],
                         w=2.2, tail='triangle'))
    # Hop 2 결과(갤러리) — 오른쪽 아래
    gx, gy, gw = H2_GAL
    n = len(H2_PHOTOS)
    pw = (gw - 32 - 10 * (n - 1)) / n
    ph = 118
    gh = 46 + ph + 26 + 14
    s.add('h2/gal', [R('h2/gal/bg', gx, gy, gw, gh, prst='roundRect', radius=20, fill='FFFFFF', line=LINE, line_w=1.0, shadow=SHADOW_CARD),
                     P('h2/gal/ic', ICON['gallery'], gx + 16, gy + 12, 26, 26),
                     T('h2/gal/t', gx + 50, gy + 12, 120, 26, '갤러리', size=13, color=INK, weight='b', anchor='ctr')])
    filt, fw_ = chip('h2/filter', gx + gw - 16 - (tw('date: "2026-03-15"', 10.5, 'b') + 24), gy + 11, 'date: "2026-03-15"', 'dash', pt=10.5,
                     h=28, padx=12)
    s.add('h2/filter', filt)
    spots, photos, dates, dtxt = [], [], [], []
    for i, k in enumerate(H2_PHOTOS):
        img, d, fo = PH[k]
        px_, py_ = gx + 16 + i * (pw + 10), gy + 50
        spots.append((px_, py_, pw, ph))
        photos.append(P('h2/p%d' % i, img, px_, py_, pw, ph, radius=10, crop=crop_fit(img, pw, ph, fo)))
        label = d + (' 20:14' if k == 'babich' else (' 19:52' if k == 'table' else ''))
        dtxt.append(label)
        dates.append(T('h2/d%d' % i, px_, py_ + ph + 5, pw, 18, label, size=9.5, color=SUB, align='c'))
    s.add('h2/photos', photos + dates)
    keep = [i for i, k in enumerate(H2_PHOTOS) if PH[k][1] == '2026. 3. 15']
    s.add('h2/dim', [dim_over('h2/dim%d' % i, spots[i], radius=10, alpha=70) for i in range(n) if i not in keep])
    xm = []
    for i in range(n):
        if i not in keep:
            xm += xmark('h2/x%d' % i, spots[i][0] + pw / 2, spots[i][1] + ph / 2, s=26, w=4.2)
    s.add('h2/x', xm)
    s.add('h2/dhl', [hl_band('h2/dhl%d' % i, spots[i][0] + pw / 2 - tw(dtxt[i], 9.5) / 2, spots[i][1] + ph + 5, dtxt[i], dtxt[i][:11], 9.5,
                             alpha=40) for i in keep])
    t_i = H2_PHOTOS.index('table')
    w_i = H2_PHOTOS.index('babich')
    s.add('h2/dimt', [dim_over('h2/dimt', spots[t_i], radius=10, alpha=70)])
    s.add('h2/pring', [ring_box('h2/pring', spots[w_i], pad=4, radius=12, w=3.0)])
    lab, lw_ = chip('h2/ocr', spots[w_i][0] + pw / 2, spots[w_i][1] + ph - 30, 'BABICH SAUVIGNON BLANC', 'outline', pt=8.5, h=22, padx=8,
                    align='c')
    s.add('h2/ocr', lab)
    ans, aw = chip('h2/ans', x + 56, ay + 1, '배비치 소비뇽 블랑', 'fill', pt=11, h=26, padx=10)
    s.add('h2/ans', ans)
    s.add('h2/link', thread('h2/link', scurve((H2[0] + H2[2], H2[1] + 76), (gx, gy + 110)), w=2.2))
    s.on('h2/cap', 'rise', 150, 450, dy=14)
    s.on('h2/back', 'wipe_in', 100, 450, dir='left')
    s.on('h2/c', 'wipe_in', 450, 450, dir='down')
    s.on('h2/re', 'pulse', 900, 220, scale=1.03)
    s.click()   # 1: 날짜 필터
    s.on('h2/link', 'wipe_in', 0, 450)
    s.on(['h2/gal', 'h2/photos'], 'rise', 200, 500, dy=14)
    s.on('h2/filter', 'pop', 650, 420, **{'from': 0.6, 'over': 1.08})
    s.on('h2/dim', 'fade_in', 1050, 400)
    s.on('h2/x', 'pop', 1150, 380, **{'from': 0.3, 'over': 1.15})
    s.on('h2/dhl', 'wipe_in', 1350, 350)
    s.click()   # 2: 와인 사진 → 라벨 → 답
    s.on('h2/dimt', 'fade_in', 0, 400)
    s.on('h2/pring', 'zoom_in', 250, 420, **{'from': 1.12})
    s.on('h2/ocr', 'wipe_in', 650, 500)
    s.on('h2/ans', 'fly', 1250, 1000, dx=spots[w_i][0] + pw / 2 - (x + 56) - aw / 2, dy=spots[w_i][1] + ph - 20 - (ay + 1), bend=-0.18)
    return s


# ------------------------------------------------------------------ 8. 04 결과 제공
DL_SP = (70, 150, 560, 66)
SHEET = (70, 236, 560, 340)


def s_deliver():
    s = Slide('deliver', trans=('morph', 1000), cur='04', done={'00', '01', '02', '03'},
              notes='찾은 이름은 근거 기록과 함께 건네고, 입력하기를 누르면 검색창에 바로 들어갑니다.')
    x, y, w, h = DL_SP
    pill, txt, cur, tx0 = search_pill('dl/sp', x, y, w, h, QUERY, pt=16.5)
    s.add('dl/sp', pill)
    s.add('dl/q', [txt], temp=True)
    ans = '배비치 소비뇽 블랑'
    s.add('dl/q2', [T('dl/q2', txt[2], txt[3], txt[4], txt[5], ans, size=16.5, color=INK, anchor='ctr')])
    s.add('dl/cur', [R('dl/cur', tx0 + tw(ans, 16.5) + 3, y + h / 2 - 11, 2.4, 22, fill=PURPLE, line=None)])
    sx, sy, sw, sh = SHEET
    by_ = sy + 128
    rows = [('talk', '지은', '‘휴지 안 사 와도 돼’  3월 15일'), ('gallery', '와인 사진', '3월 15일 20:14')]
    out = [R('dl/sheet/bg', sx, sy, sw, sh, prst='roundRect', radius=24, fill='FFFFFF', line=LINE2, line_w=1.4, shadow=SHADOW_LIFT),
           R('dl/sheet/card', sx + 18, sy + 18, sw - 36, 96, prst='roundRect', radius=16, fill=LAV, line=None),
           T('dl/sheet/lab', sx + 36, sy + 30, 300, 22, [[('✦ ', {'color': PURPLE}), ('자동 완성 추천', {'color': PURPLE})]], size=11.5,
             weight='b'),
           T('dl/sheet/ans', sx + 36, sy + 56, sw - 72, 44, ans, size=24, color=INK, weight='b', anchor='ctr'),
           R('dl/sheet/btn', sx + 18, by_, sw - 36, 50, prst='roundRect', radius=14, fill=PURPLE, line=None, shadow=(14, 4, '6B4EFF', 24)),
           T('dl/sheet/btnt', sx + 18, by_, sw - 36, 50, '✓  입력하기', size=14, color='FFFFFF', weight='b', align='c', anchor='ctr'),
           T('dl/sheet/mem', sx + 26, by_ + 66, 200, 20, '연결된 기억', size=11, color=SUB, weight='b')]
    for i, (ic, a, b) in enumerate(rows):
        ry = by_ + 94 + i * 38
        out += [P('dl/sheet/ic%d' % i, ICON[ic], sx + 26, ry + 4, 24, 24),
                T('dl/sheet/r%d' % i, sx + 60, ry, sw - 90, 32, [[(a + '  ', {'weight': 'b', 'color': INK}), (b, {'color': SUB})]], size=11.5,
                  anchor='ctr')]
    s.add('dl/sheet', out)
    hw = 170 * 773 / 960
    bx, by2 = sx + sw - 120, by_ + 25
    s.add('dl/hand', [P('dl/hand', str(AS / 'hand.png'), bx - hw * 0.388, by2 - 170 * 0.015 + 6, hw, 170)])
    s.add('dl/cap', [caption('dl/cap', [[('찾은 이름을 근거와 함께 건네고', INK)], [('탭 한 번에 검색창을 채웁니다', PURPLE)]], 690, 330, size=28,
                             align='l')])
    s.on('dl/q', 'jump', 0)
    s.on('dl/sheet', 'rise', 150, 550, dy=16)
    s.on('dl/cap', 'rise', 450, 550, dy=16)
    s.on('dl/hand', 'fly', 1100, 650, dx=140, dy=200, bend=0.1)
    s.on('dl/hand', 'pulse', 1780, 140, scale=0.93)
    s.on('dl/q', 'fade_out', 2000, 250)
    s.on('dl/q2', 'type', 2250, 1, ms=60, n=len(ans))
    s.on('dl/cur', 'appear', 2250 + 60 * len(ans) + 40, 1)
    s.on('dl/cur', 'blink', 2250 + 60 * len(ans) + 80, 1000)
    return s


# ------------------------------------------------------------------ 9. 한눈에 보기
def s_overview():
    s = Slide('overview', trans=('morph', 800), done={'00', '01', '02', '03', '04'},
              notes='정리하면, Weave는 평소에 기록을 색인해 두고, 검색하다 막히면 질문을 나눈 뒤 찾은 단서로 다시 묻습니다. '
                    '이 모든 과정은 기기 안에서 이뤄집니다.')
    s.add('ov/cap', [caption('ov/cap', [[('질문을 나누고, ', INK), ('찾은 단서로 다시 묻습니다', PURPLE)]], 640, 80, size=26)])
    tagw = tw('모든 단계가 기기 안에서', 10.5, 'b') + 48
    s.add('ov/dev', [R('ov/dev/bg', 36, 136, 1208, 560, prst='roundRect', radius=30, fill='FFFFFF', alpha=50, line=LINE2, line_w=1.4),
                     R('ov/dev/tag', 60, 122, tagw, 28, prst='roundRect', fill='FFFFFF', line=LINE2, line_w=1.2),
                     R('ov/dev/ph', 74, 128, 11, 16, prst='roundRect', radius=3, fill=None, line=PURPLE, line_w=1.6),
                     R('ov/dev/ph2', 77.5, 141, 4, 1.4, fill=PURPLE, line=None),
                     T('ov/dev/t', 94, 122, tagw - 40, 28, '모든 단계가 기기 안에서', size=10.5, color=PURPLE, weight='b', anchor='ctr')])

    def stage_tag(key, x, y, no, name):
        w = tw(name, 10.5, 'b') + 46
        return [R(key + '/bg', x, y, w, 24, prst='roundRect', fill=LAV, line=None),
                R(key + '/n', x + 4, y + 3, 18, 18, prst='ellipse', fill=PURPLE, line=None),
                T(key + '/nt', x + 4, y + 3, 18, 18, no, size=7.5, color='FFFFFF', weight='b', align='c', anchor='ctr'),
                T(key + '/t', x + 28, y, w, 24, name, size=10.5, color=PURPLE, weight='b', anchor='ctr')]
    # 01 상황 인식: 질문 + 키보드 실타래 버튼
    pill, txt, _, _ = search_pill('ov/q', 62, 210, 300, 52, QUERY, pt=12.5, icon='mag', cursor=False)
    tbw = 300
    tbh = tbw * 168 / 1300
    s.add('ov/q', stage_tag('ov/q/tag', 62, 174, '01', '상황 인식') + pill + [txt] +
          [P('ov/q/kb', str(AS / 'kb-toolbar.png'), 62, 276, tbw, tbh, radius=10),
           R('ov/q/ring', 62 + 102 * tbw / 1300 - 17, 276 + 82 * tbh / 168 - 17, 34, 34, prst='ellipse', fill=None, line=PURPLE, line_w=2.2,
             glow=(8, RING, 40))])
    # 02 질의 재작성
    qx, qy, qw = 420, 174, 330
    rows = [R('ov/rw/bg', qx, qy + 36, qw, 108, prst='roundRect', radius=16, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=SHADOW_CARD)]
    rows += numdot('ov/rw/n1', qx + 22, qy + 64, 1, r=10, pt=8.5)
    rows.append(T('ov/rw/t1', qx + 40, qy + 50, qw - 50, 28, '지은이네 집들이는 언제였지?', size=12, color=INK, weight='m', anchor='ctr'))
    rows += numdot('ov/rw/n2', qx + 22, qy + 112, 2, r=10, pt=8.5, fill=BLUE)
    tk, tkw = chip('ov/rw/tk', qx + 40, qy + 100, '3/15 (일)', 'fill', pt=10, h=24, padx=8)
    rows += tk
    rows.append(T('ov/rw/t2', qx + 40 + tkw + 6, qy + 98, qw - 60 - tkw, 28, '마셨던 와인은?', size=12, color=INK, weight='m', anchor='ctr'))
    s.add('ov/rw', stage_tag('ov/rw/tag', qx, qy, '02', '질의 재작성') + rows)
    # 04 결과 제공
    rx, ry, rw = 846, 174, 360
    res = [R('ov/res/bg', rx, ry + 36, rw, 108, prst='roundRect', radius=16, fill=LAV, line=RING, line_w=1.6, glow=(8, RING, 22)),
           T('ov/res/l', rx + 18, ry + 46, 200, 20, '✦ 자동 완성 추천', size=10, color=PURPLE, weight='b'),
           T('ov/res/a', rx + 18, ry + 66, rw - 30, 34, '배비치 소비뇽 블랑', size=19, color=INK, weight='b', anchor='ctr'),
           P('ov/res/i1', ICON['talk'], rx + 18, ry + 108, 20, 20),
           T('ov/res/s1', rx + 42, ry + 106, 120, 24, '지은 카톡', size=9.5, color=SUB, anchor='ctr'),
           P('ov/res/i2', ICON['gallery'], rx + 130, ry + 108, 20, 20),
           T('ov/res/s2', rx + 154, ry + 106, 180, 24, '와인 사진 3월 15일', size=9.5, color=SUB, anchor='ctr')]
    s.add('ov/res', stage_tag('ov/res/tag', rx, ry, '04', '결과 제공') + res)
    # 03 연쇄 탐색
    hy = 380
    s.add('ov/hoptag', stage_tag('ov/hoptag', 62, hy + 60, '03', '연쇄 탐색') +
          [T('ov/hoptag/s', 62, hy + 90, 300, 40, ['Hop마다 Reasoning Embedding으로', '기록을 찾고, 찾은 단서로 다시 묻습니다'], size=10,
             color=SUB, lnspc=14)])

    def hop_box(key, x, w, n, q1, res_kind, res_label, res_sub):
        out = [R(key + '/bg', x, hy, w, 150, prst='roundRect', radius=18, fill='FFFFFF', line=RING, line_w=1.8, shadow=SHADOW_CARD),
               T(key + '/t', x + 16, hy + 10, 220, 24, 'Reasoning Embedding', size=11.5, color=PURPLE, weight='b', anchor='ctr')]
        hc, _ = chip(key + '/h', x + w - 16 - (tw('Hop %d' % n, 9.5, 'b') + 20), hy + 10, 'Hop %d' % n, 'fill', pt=9.5, h=22, padx=10)
        out += hc
        out.append(T(key + '/q', x + 16, hy + 40, w - 30, 24, q1, size=11, color=SUB, anchor='ctr'))
        out.append(R(key + '/r', x + 16, hy + 74, w - 32, 60, prst='roundRect', radius=12, fill='F7F5FC', line=None))
        out.append(P(key + '/ri', ICON[res_kind], x + 28, hy + 90, 28, 28))
        out.append(T(key + '/rt', x + 66, hy + 80, w - 90, 24, res_label, size=12, color=INK, weight='b', anchor='ctr'))
        out.append(T(key + '/rs', x + 66, hy + 102, w - 90, 22, res_sub, size=10, color=SUB, anchor='ctr'))
        return out
    s.add('ov/h1', hop_box('ov/h1', 420, 330, 1, '① 지은이네 집들이는 언제였지?', 'talk', '지은 카톡', '‘휴지 안 사 와도 돼’  3월 15일'))
    s.add('ov/h2', hop_box('ov/h2', 846, 360, 2, '② 3/15 (일) 마셨던 와인은?  + 날짜 필터', 'gallery', '와인 사진',
                           '라벨 BABICH SAUVIGNON BLANC'))
    # 00 데이터 색인(바닥)
    iy = 572
    idx = [R('ov/idx/bg', 62, iy, 1144, 96, prst='roundRect', radius=18, fill=LAV2, line=LINE2, line_w=1.2)]
    idx += stage_tag('ov/idx/tag', 80, iy + 14, '00', '데이터 색인')
    for i, ic in enumerate(['talk', 'gallery', 'note', 'cal', 'mail']):
        idx.append(P('ov/idx/a%d' % i, ICON[ic], 84 + i * 34, iy + 52, 26, 26))
    cols = [('원문', '박스 정리 다 했어! 이따 올 때…', BODY), ('벡터', '[0.86, −0.08, 0.33, …]', PURPLE), ('메타데이터', '{ date, app, … }', INK)]
    for i, (a, b, col) in enumerate(cols):
        cx_ = 330 + i * 300
        idx.append(T('ov/idx/l%d' % i, cx_, iy + 18, 260, 22, a, size=10.5, color=PURPLE if i else SUB, weight='b'))
        idx.append(T('ov/idx/v%d' % i, cx_, iy + 44, 290, 26, b, size=12, color=col, weight='m'))
    s.add('ov/idx', idx)
    # 화살표: 질문 → 질의 재작성 → Hop 1 → (단서) → ② → Hop 2 → 결과
    s.add('ov/a1', thread('ov/a1', scurve((362, 236), (418, 258)), w=2.2, tail='triangle'))
    s.add('ov/a2', thread('ov/a2', vcurve((470, 318), (500, hy - 2), 0.5), w=2.2, tail='triangle'))
    s.add('ov/loop', thread('ov/loop', [(420, hy + 104), (392, hy + 104), (392, 296), (418, 296)], w=2.6, tail='triangle'))
    s.add('ov/loopt', chip('ov/loopt', 384, 330, '단서로 다시 쓰기', 'white', pt=9.5, h=24, padx=10, align='r')[0])
    s.add('ov/a3', thread('ov/a3', scurve((752, 296), (900, hy - 2), 0.5), w=2.2, tail='triangle'))
    s.add('ov/a4', thread('ov/a4', vcurve((1120, hy), (1120, 320), 0.5), w=2.2, tail='triangle'))
    s.add('ov/u1', [line('ov/u1', (585, iy), (585, hy + 152), color=PURPLE2, w=1.6, dash='dash')])
    s.add('ov/u2', [line('ov/u2', (1026, iy), (1026, hy + 152), color=PURPLE2, w=1.6, dash='dash')])
    order = [('ov/dev', 0), ('ov/idx', 150), ('ov/q', 400), ('ov/a1', 650), ('ov/rw', 750), ('ov/a2', 1000), ('ov/hoptag', 1050),
             ('ov/h1', 1100), ('ov/u1', 1300), ('ov/loop', 1450), ('ov/loopt', 1650), ('ov/a3', 1750), ('ov/h2', 1850), ('ov/u2', 2050),
             ('ov/a4', 2200), ('ov/res', 2300)]
    wipes = {'ov/a1': 'left', 'ov/a2': 'down', 'ov/a3': 'down', 'ov/a4': 'up', 'ov/u1': 'up', 'ov/u2': 'up', 'ov/loop': 'up'}
    for k, d in order:
        if k in wipes:
            s.on(k, 'wipe_in', d, 400, dir=wipes[k])
        else:
            s.on(k, 'rise', d, 450, dy=12)
    s.on('ov/cap', 'rise', 2700, 500, dy=14)
    return s


SLIDES = [s_hiw, s_ask, s_cloud, s_old, s_kw, s_emb, s_step, s_chain, s_idx, s_trig, s_split, s_hop1, s_hop2, s_deliver, s_overview]

SOL_NOTES = ('방금 보신 세 장면이 Weave의 세 가지 경험입니다. 통화 중 흩어진 업무 기록을 한 번에 요약하는 기록 통합 검색, '
             '떠오르는 단서만으로 이름을 찾아 주는 단서로 찾는 기억, 지금 상황에 필요한 기억을 먼저 건네는 먼저 건네는 기억입니다. '
             '모두 따로 앱을 켜지 않고, 지금 보던 화면과 키보드 위에서 끝납니다.')


# ------------------------------------------------------------------ 조립
def blur_png(src, dst, radius=16, veil=0.32):
    im = Image.open(src).convert('RGB').resize((1920, 1080), Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(radius))
    Image.blend(im, Image.new('RGB', im.size, (250, 248, 255)), veil).save(dst)


def build(dst, auto=False, hold=1700):
    prs = Presentation(str(DECK))
    sol = prs.slides[SOL_INDEX]
    layout = prs.slides[SOL_INDEX + 1].slide_layout
    note_tpl = [copy.deepcopy(sh._element) for sh in prs.slides[SOL_INDEX + 1].notes_slide.placeholders]
    lst = prs.slides._sldIdLst
    for i, sid in enumerate(list(lst)):
        if i != SOL_INDEX:
            prs.part.drop_rel(sid.get(q('r:id')))
            lst.remove(sid)
    from pptx.opc.packuri import PackURI
    sol.part.partname = PackURI('/ppt/slides/slide1.xml')        # 새 장 이름(slide2…)과 겹치지 않게
    sol.notes_slide.notes_text_frame.text = SOL_NOTES
    import appendix
    specs = [f() for f in SLIDES] + [f() for f in appendix.APPENDIX]
    report = []
    secs = [6.0]
    for sp in specs:
        slide = prs.slides.add_slide(layout)
        for ph in list(slide.placeholders):
            ph._element.getparent().remove(ph._element)
        pa = Painter(slide)
        if sp.bg:
            for p in bg_prims():
                pa.put(p[1], [p], group=False)
        temps, starts = set(), {}
        for key, prims, alpha, xf, group, temp, start in sp.items:
            if temp:
                x0 = xf or Xf()
                xf = Xf(x0.ax, x0.ay, x0.bx + OFF, x0.by, x0.s)
                temps.add(key)
            if start:
                starts[key] = start
            pa.put(key, prims, alpha=alpha, xf=xf or Xf(), group=group)
        if sp.bar:
            pa.put('top/badge', badge_prims(), group=False)
            for p in topbar_prims(sp.cur, sp.done):
                pa.put(p[1], [p], group=False)
        # 효과
        tl = M.Timeline()
        missing = []
        for gi, grp in enumerate(sp.groups):
            tl.step()
            for key, kind, delay, dur, kw in grp:
                if key not in pa.spids:
                    missing.append(key)
                    continue
                kw = dict(kw)
                if kind == 'jump':          # 화면 밖(temp)에서 제자리로 순간 이동 — 처음 나타나는 효과와 같은 때에
                    kind, dur, kw = 'move', 1, dict(dx=-OFF, dy=0, accel=0, decel=0)
                elif kind == 'goto':        # 마지막 자리에 놓인 것을 처음 자리(start)로 순간 이동
                    d = starts[key]
                    kind, dur, kw = 'move', 1, dict(dx=d[0], dy=d[1], accel=0, decel=0)
                elif key in temps and kind in ('fly', 'move'):
                    kw['base'] = (-OFF, 0)
                if kind == 'fly' and kw.get('show', True) and key not in temps:
                    # 날아 들어오는 것은 그 전까지 숨김(첫 효과가 나타내기 효과여야 PowerPoint가 처음에 숨김)
                    for spid in pa.spids[key]:
                        tl.add('appear', spid, delay=delay, dur=1)
                for spid in pa.spids[key]:
                    tl.add(kind, spid, delay=delay, dur=dur, **kw)
        if missing:
            print('   ! %s: 효과 대상 없음 %s' % (sp.key, sorted(set(missing))))
        sp_ids = {int(e.find(q('p:nvSpPr')).find(q('p:cNvPr')).get('id')) for e in slide._element.iter(q('p:sp'))}
        sp_ids |= {int(e.find(q('p:nvPicPr')).find(q('p:cNvPr')).get('id')) for e in slide._element.iter(q('p:pic'))}
        sp_ids |= {int(e.find(q('p:nvGrpSpPr')).find(q('p:cNvPr')).get('id')) for e in slide._element.iter(q('p:grpSp'))}
        adv = sp.advance
        if any(tl.steps):
            if auto:
                holds = [(500 if j == 0 else hold) for j in range(len(tl.steps))]
                slide._element.append(tl.xml(sp_ids, auto=(150, holds)))
                total = 150 + sum(tl.step_len(j) + holds[j] for j in range(len(tl.steps)))
                adv = max(adv or 0, total)
            else:
                slide._element.append(tl.xml(sp_ids, first_auto=True))
        set_transition(slide, sp.trans, adv if (auto or sp.advance) else None)
        dur_s = ((adv or 2500) + (sp.trans[1] if sp.trans else 0)) / 1000
        secs.append(max(dur_s, 1.6))
        ns = slide.notes_slide
        if ns.notes_text_frame is None:
            for e in note_tpl:
                ns.shapes._spTree.append(copy.deepcopy(e))
        ns.notes_text_frame.text = sp.notes
        report.append((sp.key, sp.clicks(), sp.notes.count('(클릭)'), len(pa.spids)))
    samsung_fonts.remap_prs(prs)
    prs.save(str(dst))
    return report, secs


def sheet(pngs, dst, labels, cols=4, w=520):
    ims = [Image.open(p).convert('RGB') for p in pngs]
    h = int(w * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new('RGB', (cols * (w + 10) + 10, rows * (h + 30) + 10), 'white')
    d = ImageDraw.Draw(out)
    fnt = ImageFont.truetype(str(ROOT / '06_에셋' / '글꼴' / 'NotoSansKR-700.ttf'), 16)
    for i, im in enumerate(ims):
        x, y = 10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 30)
        out.paste(im.resize((w, h), Image.LANCZOS), (x, y + 22))
        d.text((x, y), labels[i], fill=(60, 50, 90), font=fnt)
    out.save(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--png', action='store_true')
    ap.add_argument('--video', action='store_true')
    ap.add_argument('--skip-blur', action='store_true', help='흐린 그림을 다시 만들지 않음(있는 것을 씀)')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if not a.skip_blur or not (OUT / 'blur_emb.png').exists():
        # 1차: 흐린 배경 없이 만들고 PowerPoint로 찍어 앞 장을 흐리게
        for f in ('blur_sol.png', 'blur_emb.png'):
            if not (OUT / f).exists():
                Image.new('RGB', (1920, 1080), (246, 243, 255)).save(OUT / f)
        tmp = OUT / '_pass1.pptx'
        build(tmp)
        pngs = render_c.png(tmp, OUT / '_pass1_png')
        names = ['sol'] + [f.__name__[2:] for f in SLIDES]
        blur_png(pngs[names.index('sol')], OUT / 'blur_sol.png')
        blur_png(pngs[names.index('emb')], OUT / 'blur_emb.png')
        tmp.unlink()
    report, secs = build(DST)
    for key, nclick, nnote, nkeys in report:
        flag = '' if nclick == nnote else '   ! 클릭 %d ≠ 노트 (클릭) %d' % (nclick, nnote)
        print('%-9s 클릭 %d%s' % (key, nclick, flag))
    print('→', DST, '%.1f MB' % (DST.stat().st_size / 1e6), '클릭 합계', sum(r[1] for r in report))
    if a.png:
        pngs = render_c.png(DST, OUT / 'png')
        labels = ['%d  %s' % (i + 1, k) for i, k in enumerate(['sol'] + [r[0] for r in report])]
        sheet(pngs, OUT / '한눈에.png', labels)
        print('png', len(pngs))
    if a.video:
        auto = OUT / '_auto.pptx'
        _, secs = build(auto, auto=True)
        print(render_c.video(auto, OUT / 'HowItWorks_Claude_미리보기.mp4', secs))
        auto.unlink()


if __name__ == '__main__':
    main()
