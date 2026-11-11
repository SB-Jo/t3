#!/usr/bin/env python3
"""How it Works — _claude판 8차(2026-11-11) → ../HowItWorks_Argon_claude.pptx
솔루션 세 장(조각마다 하나씩 움직임) + How it Works 14장 + Appendix 15장(한눈에 보기 포함). 뱃지는 어느 장에도 없다.

  python build.py                 → ../HowItWorks_Argon_claude.pptx (발표용: 클릭마다 한 박자)
  python build.py --png           + out/png/s01.png… 와 out/한눈에.png (PowerPoint로 렌더, 정적 = 마지막 상태)
  python build.py --video         + out/HowItWorks_Argon_claude_미리보기.mp4 (본문 17장만. 클릭 효과가 저절로 나오는 사본을 PowerPoint로 녹화하되,
                                  구간마다 그 구간의 노트를 말하는 시간만큼 머물고 그 말을 자막으로 띄움 → 영상 길이 = 발표 시간 어림)
  python build.py --skip-blur     흐린 배경 그림(out/blur_*.png)을 다시 만들지 않음(있는 것을 씀)
  python build.py --time          덱은 만들지 않고 발표 시간만 어림(본문 17장: 장마다 클릭 수, 음절 수, 걸리는 시간)
  python build.py --time --tts    노트를 낭독해서(tts_c.py, 기기 안의 음성 합성) 그 길이로 잼. --check를 붙이면 낭독을 받아쓰기로 글과 견줌
  python build.py --video --tts   미리보기 영상에 낭독을 넣음(낭독 길이만큼 머묾). --voice로 목소리, --remux로 녹화는 두고 낭독만 다시
                                  낭독 영상은 덱 옆(../HowItWorks_Argon_claude_미리보기.mp4)에도 복사됨

흐름(장): 솔루션 1·2·3 → How it works? → 질문 → 흩어진 단서 → 기존 검색이라면? → 키워드 → 임베딩 → Let's think step by step!
→ 끊어진 고리 → 00 데이터 색인 → 01 상황 인식 → 02 질의 재작성 → 03 Hop 1 → 03 Hop 2 → 04 결과 제공 | Appendix(한눈에 보기, …).
'흐려지는' 장면은 앞 상태를 PowerPoint로 찍은 그림을 흐리게 해 깔고(2번 빌드), 나머지 움직임은 모핑과 motion.py 효과로 낸다.
솔루션 세 장은 07_소스/slides/p05_결선/page-05-solution_claude.html을 조각(data-l)마다 찍은 그림(out_claude/layers)과 글상자로 만든다
(HTML을 고쳤으면 먼저 그 폴더에서 node export_layers_claude.cjs). 그림(assets)은 Argon판(../장표5/assets) 것을 읽기만 한다.
"""
import argparse
import copy
import json
import random
import re
import shutil
import subprocess
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
                SHADOW_CARD, SHADOW_LIFT, SHADOW_SOFT, C, P, Painter, R, T, Xf, bg_prims, caption, card,
                check_icon, chip, crop_fit, gallery, hl_band, line, magnifier, numdot, qbadge, scurve, search_pill, spark_icon,
                thread, topbar_prims, tw, vcurve, xmark)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / '11_중간본'))
import samsung_fonts  # noqa: E402

SRC = ROOT / '02_PPT' / 'Weave_결선.pptx'          # 원본 덱(읽기만): 장 틀과 노트 틀만 빌려 씀
LAYOUT_INDEX = 8                   # 중간본 조립(build_deck.py)과 같은 장 틀·노트 틀
DST = HERE.parent / 'HowItWorks_Argon_claude.pptx'
OUT = HERE / 'out'
AS = HERE.parent / '장표5' / 'assets'   # 그림은 Argon판 것을 읽기만 함
SOLDIR = ROOT / '07_소스' / 'slides' / 'p05_결선' / 'out_claude'      # 솔루션 조각 그림과 글상자(export_layers_claude.cjs)

QUERY = '지은이네 집들이 때 마셨던 와인'
OFF = 1600                         # 잠깐 보이는 것을 둘 화면 밖 거리(px)
SPEED = 0.8                        # 11-09 '길고 유치함' → 모든 효과와 장 넘김을 0.8배 길이로
PASS1 = False                      # 흐린 그림을 만들려고 찍는 1차 빌드(흩어진 단서 장은 글 없이)
MC = 'http://schemas.openxmlformats.org/markup-compatibility/2006'
P14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
P159 = 'http://schemas.microsoft.com/office/powerpoint/2015/09/main'

# 사진(실제 사진으로 바꿀 자리). (파일, 날짜, 초점)
PH = {
    'babich': ('photo-babich.png', '2026. 3. 15', (0.5, 0.45)),
    'table': ('photo-homedinner.jpg', '2026. 3. 15', (0.5, 0.5)),
    'cheers': ('photo-cheers.jpg', '2026. 3. 15', (0.5, 0.5)),
    'w1': ('photo-seaside.jpg', '2025. 7. 19', (0.62, 0.5)),
    'w2': ('photo-meadow.jpg', '2025. 9. 27', (0.66, 0.6)),
    'w3': ('photo-champagne.jpg', '2025. 12. 31', (0.62, 0.45)),
    'glass': ('photo-glass.jpg', '2026. 1. 9', (0.45, 0.45)),
    'bar': ('photo-bar.jpg', '2025. 11. 22', (0.5, 0.5)),          # 다른 날 마신 화이트 와인(임베딩 장의 둘째 와인 사진)
}
WINE4 = ['babich', 'w3', 'w2', 'w1']          # 키워드·끊어진 고리 장의 와인 사진 넷(갤러리처럼 최신순, 첫째가 집들이 날)
BLUE, BLUE_HL, BLUE_BG = '4F7BFF', '7EA2FF', 'EEF3FF'    # 둘째 하위 질문 색(①은 보라, ②는 파랑)
ORANGE, ORANGE2 = 'F26B3A', 'F59B76'                     # 일반 임베딩(Reasoning Embedding의 보라와 맞서는 색, 노란 기 없는 주황)
ANSWER = '배비치 소비뇽 블랑'


# ------------------------------------------------------------------ 장
class Slide:
    def __init__(self, key, notes='', trans=('morph', 900), advance=None, bar=True, cur=None, done=(), bg=True):
        self.key, self.notes, self.advance = key, notes, advance
        self.trans = (trans[0], round(trans[1] * SPEED)) if trans else trans
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
        # 11-09: 튀는 확대(pop)는 넘침 없는 짧은 확대로, 모든 효과는 SPEED배 길이로, 휘어 나는 길은 절반만 휨
        if kind == 'pop':
            kind, kw, dur = 'zoom_in', {'from': max(0.9, kw.get('from', 0.9))}, min(dur, 320)
        if kind == 'fly' and 'bend' in kw:
            kw = dict(kw, bend=kw['bend'] * 0.5)
        if kind == 'type':
            kw = dict(kw, ms=max(1, round(kw['ms'] * SPEED)))
        delay = round(delay * SPEED)
        if kind not in ('type', 'blink', 'jump', 'goto', 'appear'):
            dur = max(1, round(dur * SPEED))
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


def band(name, pos, sub, kind='low', start=0, alpha=34, pad=(2, 0.5)):
    x, y, text, pt, wt = pos
    return hl_band(name, x, y, text, sub, pt, wt, start=start, kind=kind, alpha=alpha, pad=pad)


def tag_red(name, cx, y, label, pt=10.5):
    clean = label.lstrip('✕ ').strip()
    h = 28
    w = 13 + 9 + 7 + tw(clean, pt, 'b') + 13
    x = cx - w / 2
    xc, yc, r = x + 17.5, y + h / 2, 4.0
    return [R(name + '/bg', x, y, w, h, prst='roundRect', fill='FFFFFF', line='F2B8BA', line_w=1.0, shadow=SHADOW_SOFT),
            line(name + '/x1', (xc - r, yc - r), (xc + r, yc + r), color='C8323A', w=1.8),
            line(name + '/x2', (xc + r, yc - r), (xc - r, yc + r), color='C8323A', w=1.8),
            T(name + '/t', x + 28, y, w - 28, h, clean, size=pt, color='C8323A', weight='b', anchor='ctr')]


def dim_over(name, box, radius=12, alpha=62):
    x, y, w, h = box
    return R(name, x, y, w, h, prst='roundRect', radius=radius, fill='FFFFFF', alpha=alpha, line=None)


def star(name, cx, cy, r=15, color=PURPLE):
    glow = [(0, 'FFB494', 55), (60, 'FFD9C8', 18), (100, 'FFF6F1', 0)] if color == ORANGE else \
        [(0, 'B9A2FF', 55), (60, 'D9CCFF', 18), (100, 'F8F5FF', 0)]
    return [R(name + '/glow', cx - r * 1.9, cy - r * 1.9, r * 3.8, r * 3.8, prst='ellipse', fill=None,
              grad=dict(stops=glow, path='circle', rect=(50, 50, 50, 50))),
            R(name + '/s', cx - r, cy - r, 2 * r, 2 * r, prst='star5', fill=color, line='FFFFFF', line_w=2)]


def mini_chip(name, x, y, kind, label, sub=None, pt=10.5, alpha=100, img=None, ring=False):
    """임베딩 공간 속 기록 점: 아이콘(img면 사진) + 짧은 이름(+ 회색 한 줄). ring이면 보라 테두리('단서'인 기록).
    돌려줌: (원시, 폭, 높이) — 폭은 바탕 상자의 폭 그대로(11-10: 사진 칩은 테두리가 8px 넓게 나오던 것을 맞춤)."""
    h = 34 if not sub else 46
    isz, padl = (30, 8) if img else (22, 12)
    w = padl + isz + 8 + max(tw(label, pt, 'b'), tw(sub, pt - 1.5) if sub else 0) + 14
    out = [R(name + '/bg', x, y, w, h, prst='roundRect', radius=12, fill='FFFFFF', line=RING if ring else LINE, line_w=2.0 if ring else 1.0,
             shadow=SHADOW_SOFT, alpha=alpha, line_alpha=alpha)]
    tx = x + padl + isz + 8
    if img:
        out.append(P(name + '/ic', img, x + padl, y + (h - isz) / 2, isz, isz, radius=6, crop=crop_fit(img, isz, isz), alpha=alpha))
    else:
        out.append(P(name + '/ic', ICON[kind], x + padl, y + (h - isz) / 2, isz, isz, alpha=alpha))
    tw_ = w - (tx - x) - 6
    if sub:
        out.append(T(name + '/t', tx, y + 6, tw_, 18, label, size=pt, color=INK, weight='b', alpha=alpha))
        out.append(T(name + '/s', tx, y + 24, tw_, 16, sub, size=pt - 1.5, color=MUTE, alpha=alpha))
    else:
        out.append(T(name + '/t', tx, y, tw_, h, label, size=pt, color=INK, weight='b', anchor='ctr', alpha=alpha))
    return out, w, h


def ring_box(name, box, pad=5, radius=20, w=2.4):
    x, y, bw, bh = box
    return R(name, x - pad, y - pad, bw + 2 * pad, bh + 2 * pad, prst='roundRect', radius=radius, fill=None, line=RING, line_w=w,
             glow=(10, RING, 30))


def card_fit(title, meta, lines, pt=11.5, title_pt=13.5, meta_pt=9.5, bubble=False, slack=8):
    """기록 카드가 글을 담는 폭(오른쪽 여백을 왼쪽 16px과 비슷하게). 11-10: 카드마다 오른쪽이 휑하던 것을 글에 맞춤."""
    head = 34 + 11 + max(tw(title, title_pt, 'b'), tw(meta, meta_pt))
    body = max([tw(t, pt) for t in lines] or [0]) + (28 if bubble else 0)
    return round(32 + max(head, body) + slack)


def clue_tag(name, x, y, soft=False):
    """기록 칩·카드 왼쪽 위 모서리에 붙는 '단서' 표. soft면 옅은 보라(아직 찾지 못한 단서를 살짝 귀띔할 때)."""
    w = tw('단서', 10, 'b') + 18
    fill, ln, col = (LAV, PURPLE2, PURPLE) if soft else (PURPLE, 'FFFFFF', 'FFFFFF')
    return [R(name + '/bg', x - 9, y - 12, w, 22, prst='roundRect', fill=fill, line=ln, line_w=1.2 if soft else 1.6, shadow=SHADOW_SOFT),
            T(name + '/t', x - 9, y - 12, w, 22, '단서', size=10, color=col, weight='b', align='c', anchor='ctr')]


def verdict(xname, vname, cx, cy, label, xs=40, xw=5.2, pt=11.5, h=28):
    """빨간 ✕와 그 옆에 뒤따라 나오는 한마디(흰 알약, 빨간 글자). (cx, cy) = 둘을 합친 묶음의 가운데.
    돌려줌: (✕ 원시, 알약 원시) — ✕가 먼저 뜨고 알약이 왼쪽부터 닦여 나오게 따로 넣는다."""
    pw = tw(label, pt, 'b') + 26
    gap = 8
    x0 = cx - (xs + gap + pw) / 2
    px = x0 + xs + gap
    pill = [R(vname + '/bg', px, cy - h / 2, pw, h, prst='roundRect', fill='FFFFFF', line='F2B8BA', line_w=1.0, shadow=SHADOW_SOFT),
            T(vname + '/t', px, cy - h / 2, pw, h, label, size=pt, color='C8323A', weight='b', align='c', anchor='ctr')]
    return xmark(xname, x0 + xs / 2, cy, s=xs, w=xw), pill


JIEUN_META = ('카카오톡 · ', '3월 15일 (일)', ' 오후 4:12')
JIEUN_LINES = ['박스 정리 다 했어! 이따 올 때', '휴지 안 사 와도 돼']


def jieun_fit(pt=12.5, title_pt=14, meta_pt=10):
    """지은 카톡 카드가 글을 담는 폭(날짜를 굵게 쓴 줄까지)."""
    pre, dt, post = JIEUN_META
    w = card_fit('지은', pre + dt + post, JIEUN_LINES, pt=pt, title_pt=title_pt, meta_pt=meta_pt, bubble=True)
    return max(w, round(32 + 45 + tw(pre, meta_pt) + tw(dt, meta_pt, 'b') + tw(post, meta_pt) + 8))


def jieun_card(key, x, y, w, pt=12.5, title_pt=14, meta_pt=10, date=True):
    """지은 카톡 카드. date면 받은 날짜를 보라 굵은 글씨로 — 날짜 뱃지를 따로 두지 않고 그 자리에서 강조한다(11-10).
    돌려줌: card()와 같음. 자리['date'] = 날짜 글자의 (x, y, 폭, 글자 높이)."""
    pre, dt, post = JIEUN_META
    out, h, pos = card(key, 'talk', x, y, w, '지은', pre + dt + post, JIEUN_LINES, pt=pt, title_pt=title_pt, meta_pt=meta_pt)
    if date:
        for i, p_ in enumerate(out):
            if p_[0] == 'text' and p_[1] == key + '/meta':
                out[i] = T(p_[1], p_[2], p_[3], p_[4], p_[5],
                           [[(pre, dict(color=MUTE)), (dt, dict(color=PURPLE, weight='b')), (post, dict(color=MUTE))]], **p_[7])
        pos['date'] = (pos['meta'][0] + tw(pre, meta_pt), pos['meta'][1], tw(dt, meta_pt, 'b'), meta_pt * 4 / 3)
    return out, h, pos


def date_band(name, pos, alpha=40):
    """지은 카톡 카드의 날짜 아래 형광펜."""
    x, y, w, S = pos['date']
    return R(name, x - 2, y + S * 0.58, w + 2.5, S * 0.55, prst='roundRect', radius=3, fill=HL, alpha=alpha, line=None)


# ------------------------------------------------------------------ 0. 솔루션 세 장: 조각마다 PowerPoint 묶음 하나(그림 + 글상자)
SOL_TITLE_Y = 46                                   # 뱃지·부제 없이 제목만(덱 머리 규격 29pt Bold)
SOL_DY = -14                                       # 뱃지가 빠진 만큼 내용 전체를 14px 위로(위아래 여백을 맞춤)
SOL_END = Xf(0, 0, 0, SOL_DY, 1.0)                 # 세 UX가 다 모인 마지막 자리(HTML 좌표 그대로, 위로 14px)
SOL_ONE = Xf(315, 416, 640, 404, 1.08)             # 1쪽: UX 1 묶음(기록 + 휴대폰)만 가운데에 조금 크게
SOL_LAB_DY = 10                                    # 11-11 6차: 번호·이름을 아래 UI 쪽으로 10px(사이 28 → 18px, 세 묶음 모두 같은 간격)
SOL_MID = Xf(0, 280, 0, 416 + SOL_DY, 1.0)         # 2쪽: UX 2(이름표 168 ~ 카드 아래 392)는 오른쪽 칸의 세로 가운데
SOL_Z = {                                          # 겹침 순서(아래 → 위). 이름표는 sol_label()이 따로 그림
    'ux1': ['th1', 'th2', 'th3', 'tm', 'tc', 'note0', 'arr', 'note', 'mail', 'cal', 'phone', 'call', 'swipe', 'sheet', 'go', 'q',
            'sum', 'sl1', 'sl2', 'sl3', 'ttl', 'r1', 'r2', 'r3'],
    'ux2': ['field', 'q', 'kb', 'arrow', 'card', 'tap', 'pen', 'ok'],
    'ux3': ['gps', 'wallet', 'kb', 'arrow', 'card', 'glow', 'badge', 'tap', 'pen', 'ok'],
}
SOL_PHONE = ['phone', 'call', 'swipe', 'sheet', 'go', 'q', 'sum']     # 1쪽에서 휴대폰과 함께 옮겨 가는 조각(그 뒤에 뜨는 조각은 제자리에서 나타남)
SOL_ALPHA = {'ux1/note0': 62}                      # 11-10 5차: 이전 회의록(11/3)은 조각 전체를 옅게(두 회의록의 머리글은 같은 모양)
SOL_LABEL = {'ux1': (1, '기록 통합 검색'), 'ux2': (2, '단서로 찾는 기억'), 'ux3': (3, '먼저 건네는 기억')}
SOL_Q1 = '삼성기술전 시연 내용'
SOL_QPT = 12.5 * 0.75                              # (2) 검색창 글자 크기(pt)
# 발표자 노트(말할 글). (클릭)은 그 자리에서 클릭해 다음 효과를 띄운다는 표시. 장 키 → 글. 발표 시간은 python build.py --time [--tts]로 잰다
NOTES = {
    'sol1': ('방금 보신 첫 번째 장면은 기록 통합 검색입니다. '
             '(클릭) 통화 중이더라도, 간편하게 여러 앱에 흩어진 기록을 찾아 요약할 수 있었습니다.'),
    'sol2': '두 번째는 단서로 찾는 기억입니다. 이름이 떠오르지 않아도, 단서를 통해 정확한 이름을 찾을 수 있었습니다.',
    'sol': '세 번째는 먼저 건네는 기억입니다. 묻기도 전에, 필요한 기억을 먼저 꺼내 주었습니다.',
    'hiw': '이는 어떻게 가능했을까요? 두 번째 시나리오를 통해 알아보도록 하겠습니다.',
    'ask': '친구 집들이에서 마신 와인을 다시 사려는데, 이름이 생각나지 않는 상황입니다.',
    'cloud': '답은 분명 제 기기 안에 있습니다. (클릭) 하지만, 단서는 여러 앱에 흩어져 있죠.',
    'old': '그럼 지금 쓰는 검색으로 한번 찾아볼까요?',
    'kw': ('먼저 키워드 검색은 글자가 같은 기록을 찾습니다. '
           '(클릭) ‘지은이네’로는 (클릭) 지은이네 집 주소가, (클릭) ‘집들이’로는 (클릭) 다른 사람 집들이가, '
           '(클릭) ‘와인’으로는 (클릭) 다른 날 결제 내역이 나오죠. '
           '(클릭) 그럼 그날 찍은 사진은요? (클릭) 키워드가 없으니 아예 검색이 안 됩니다.'),
    'emb': ('임베딩 검색은 글자 대신 뜻으로 찾는데요. (클릭) 질문을 고차원 벡터로 바꾸고 '
            '(클릭) 뜻이 비슷할수록 가까이 놓이는 임베딩 공간에서 (클릭) 질문과 가까운 기록을 가져옵니다. '
            '(클릭) 그런데 가져온 건 관련 없는 메모와 (클릭) 다른 날 마신 와인입니다. 정작 단서는 멀리 있죠.'),
    'step': ('왜 이럴까요? 우리는 키워드가 아니라 대화의 맥락으로 기억하기 때문입니다. '
             '따라서 검색도 사람처럼 한 단계씩 생각해야 하며, 저희는 다음과 같이 단계를 거쳐 검색하는 과정을 제시합니다.'),
    'chain': ('이 질문에는 빠진 고리가 하나 있습니다. (클릭) 바로 이 카카오톡 대화인데요. ‘박스 정리 다 했어! 이따 올 때 휴지 안 사 와도 돼.’ '
              '집들이라는 말은 없지만, 우리는 이날이 집들이라는 걸 바로 알죠. 이 중간 단서를 Weave는 어떻게 찾아낼까요?'),
    'idx': ('먼저, 기록이 쌓일 때마다 미리 색인해 둡니다. '
            '(클릭) 문장은 임베딩 모델을 거쳐 뜻을 담은 숫자, 의미 벡터가 되고요. (클릭) 언제, 어느 앱에서, 누가 보냈는지 등은 메타데이터로 저장합니다.'),
    'trig': '단서를 포함한 질의를 입력하고 실타래 버튼을 누르면, Weave는 사용자가 입력한 질의를 가져옵니다.',
    'split': '이 질문을 의미 단위로 나누어 다시 씁니다. (클릭) 집들이가 언제였는지 먼저 묻고, 와인을 마셨던 날은 빈칸으로 남겨 두게 되죠.',
    'hop1': ('첫 질문인 ‘지은이네 집들이는 언제였지?’를 일반 임베딩으로 찾으면, 지은이의 카톡은 여전히 멀리 있는데요. '
             '(클릭) Reasoning Embedding은 추론에 필요한 단서도 잘 찾도록 튜닝한 임베딩 모델입니다. '
             '‘박스 정리, 휴지 안 사 와도 돼’가 함의한 의미가 집들이 초대라는 걸 알아보고, 질문 곁으로 끌어오죠. '
             '이 카톡을 받은 3월 15일이 다음 단서가 됩니다.'),
    'hop2': '이 날짜를 두 번째 질문의 빈칸에 넣으면 (클릭) 메타데이터로 그날 사진만 필터링할 수 있고 (클릭) 그중 와인 사진에서 이름을 찾아낼 수 있습니다.',
    'deliver': ('이렇게 찾은 답은 근거와 함께 건네고, (클릭) 사용자는 ‘입력하기’만 누르면 됩니다. '
                '그럼 Weave가 우리 일상을 어떻게 바꿀까요?'),
}

# 말에 맞춰 뜨는 효과: 이름 → (장 키, 구간(클릭 번호), 그 효과가 떠야 할 때 말하는 구절). cue()가 낭독에서 그 구절을 말하는 때를 찾아 준다
CUES = {
    'emb.clue': ('emb', 5, '정작 단서는'),           # 9쪽: 멀리 있는 단서(지은 카톡)가 두 번 튐
    'chain.h1': ('chain', 1, '박스 정리'),          # 11쪽: 카톡의 '박스 정리' 형광펜
    'chain.h2': ('chain', 1, '휴지 안 사'),         # 11쪽: '휴지 안 사 와도 돼' 형광펜
    'chain.hd': ('chain', 1, '이날이'),             # 11쪽: 받은 날짜 형광펜 → 실이 이어져 그날 사진과 이름
    'chain.bridge': ('chain', 1, '이 중간 단서를'),  # 11쪽: 아래 물음 글
    'trig.press': ('trig', 0, '누르면'),            # 13쪽: 손이 실타래 버튼을 누름
    'trig.take': ('trig', 0, '사용자가 입력한'),     # 13쪽: 검색창의 질의에 형광펜(질의를 가져옴)
    'split.q2': ('split', 1, '와인을 마셨던 날은'),  # 14쪽: 둘째 질의(②)
    'hop1.ev': ('hop1', 1, '박스 정리'),            # 15쪽: 카톡 근거 '박스 정리' 형광펜
    'hop1.ev2': ('hop1', 1, '휴지 안 사'),          # 15쪽: 카톡 근거 '휴지 안 사 와도 돼' 형광펜
    'hop1.date': ('hop1', 1, '이 카톡을 받은'),     # 15쪽: 받은 날짜 형광펜
    'deliver.tap': ('deliver', 1, '입력하기'),      # 17쪽: 손이 '입력하기'를 누름
}
SLIDE_KEYS = ['sol1', 'sol2', 'sol', 'hiw', 'ask', 'cloud', 'old', 'kw', 'emb', 'step', 'chain', 'idx', 'trig', 'split', 'hop1', 'hop2', 'deliver']
TIMING_NAMES = ('LAT_START', 'LAT_CLICK', 'LAT_MID', 'GAP_SLIDE', 'GAP_SENT', 'GAP_MID', 'GAP_Q', 'S_BEAT', 'Q_BEAT', 'X_BEAT', 'R_BEAT')


def use_variant(name):
    """대본과 낭독만 다른 판으로 바꾼다(화면과 효과는 같음). 설정은 <name>/notes.json:
      {"notes": {"1": 글, …, "17": 글}, "voice": 목소리, "speed": 속도, "cues": {이름: 구절}, "timing": {틈 이름: 초}, "read_as": {영문: 읽는 소리}}
    notes 말고는 없어도 된다. 장마다 (클릭) 수는 기본판과 같아야 한다.
    덱은 ../HowItWorks_Argon_claude_<name>.pptx, 나머지(낭독, 영상, png)는 out/<name>/에 나온다."""
    global DST, OUT
    import tts_c
    cfg = json.loads((HERE / name / 'notes.json').read_text(encoding='utf-8'))
    notes = {SLIDE_KEYS[int(k) - 1] if str(k).isdigit() else k: ' '.join(v.split()) for k, v in cfg['notes'].items()}
    assert set(notes) == set(SLIDE_KEYS), '노트는 17장 모두: 빠진 장 %s' % sorted(set(SLIDE_KEYS) - set(notes))
    for i, k in enumerate(SLIDE_KEYS, 1):
        assert notes[k].count('(클릭)') == NOTES[k].count('(클릭)'), '%d쪽(%s): (클릭)은 %d번이어야 함(지금 %d번)' % (
            i, k, NOTES[k].count('(클릭)'), notes[k].count('(클릭)'))
    NOTES.update(notes)
    for k, phrase in cfg.get('cues', {}).items():
        assert k in CUES, 'cues에 없는 이름 %s (쓸 수 있는 이름: %s)' % (k, ', '.join(CUES))
        CUES[k] = (CUES[k][0], CUES[k][1], phrase) if phrase else None
    for k, v in cfg.get('timing', {}).items():
        assert k in TIMING_NAMES, 'timing에 없는 이름 %s (쓸 수 있는 이름: %s)' % (k, ', '.join(TIMING_NAMES))
        globals()[k] = float(v)
    READ_AS.update(cfg.get('read_as', {}))
    if cfg.get('voice'):
        tts_c.VOICE = cfg['voice']
        tts_c.SPEEDS[cfg['voice']] = float(cfg.get('speed', tts_c.SPEEDS.get(cfg['voice'], tts_c.SPEED)))
    main_out = OUT
    DST = HERE.parent / ('HowItWorks_Argon_claude_%s.pptx' % name)
    OUT = HERE / 'out' / name
    OUT.mkdir(parents=True, exist_ok=True)
    for f in ('blur_sol.png', 'blur_emb.png', 'blur_cloud.png'):      # 흐린 배경은 화면이 같으니 기본판 것을 그대로 씀
        if not (OUT / f).exists():
            shutil.copyfile(main_out / f, OUT / f)


_SOL = {}


def sol_data():
    if not _SOL:
        _SOL.update(json.loads((SOLDIR / 'layers.json').read_text(encoding='utf-8')))
    return _SOL


def sol_text(name, t):
    """HTML 글자 상자 하나 → 글상자(07_소스/tools/참고_옛덱전용/build_pptx.py add_textbox와 같은 규칙: 자리 그대로, 여백 0, 줄 간격 고정)."""
    px = t['size']
    lines = t['lines'] or [[]]
    x, y, w, h, lh = t['x'], t['y'], t['w'], t['h'], t['lh']
    if len(lines) == 1:                 # 한 줄: 줄 간격을 글자 크기 × 1.3으로 두고 CSS 줄 상자의 세로 가운데에
        tight = px * 1.3
        y, h, lh = y + (lh - tight) / 2, tight, tight
    align = {'center': 'c', 'right': 'r', 'end': 'r'}.get(t['align'], 'l')
    if align == 'l':
        w += 24
    first = lines[0][0]
    ls = t['ls'] * 0.75

    def wt(b):
        return 'b' if b >= 700 else ('sb' if b >= 600 else 'r')
    paras = [[(r['t'].replace(' ', ' '), dict(color=r['c']['hex'], weight=wt(r['b']), size=r['sz'] * 0.75, spc=ls, spc_ko=ls))
              for r in ln] for ln in lines]
    return T(name, x, y, w, h, paras, size=px * 0.75, color=first['c']['hex'], weight=wt(first['b']), align=align, anchor='t',
             lnspc=lh * 0.75, spc=ls, pen=first['fam'].startswith('Nanum Pen'))


def sol_piece(layer):
    """조각 하나의 원시 도형: 그림(있으면) + 그 조각의 글상자들. 이름이 장마다 같아서 모핑이 잇는다."""
    d = sol_data()
    key = 'sol/' + layer
    out = []
    art = d['layers'].get(layer)
    if art:
        out.append(P(key + '/art', str(SOLDIR / 'layers' / art['file']), art['x'], art['y'], art['w'], art['h']))
    out += [sol_text('%s/t%d' % (key, i), t) for i, t in enumerate(t for t in d['texts'] if t['l'] == layer)]
    assert out, layer
    return out


def sol_title():
    runs = [('흩어진 기억을 잇는 ', INK), ('Weave', '6666FF'), ('의 ', INK), ('핵심 UX 3가지', '6666FF')]
    return T('sol/title', 0, SOL_TITLE_Y, 1280, 50, [[(t, dict(color=c, spc=-0.5, spc_ko=-0.5)) for t, c in runs]], size=29, weight='b',
             align='c', anchor='ctr', lnspc=34.8, spc=-0.5)


def sol_label(ux):
    """번호 + 이름. 11-10 5차: 다시 묶음의 왼쪽 위(HTML의 GEOM.lab = 왼쪽 끝). 덱 글꼴로 그린다."""
    n, name = SOL_LABEL[ux]
    x, y = sol_data()['geom']['lab'][ux]
    y += SOL_LAB_DY
    key = 'sol/%s/label' % ux
    pt = 23 * 0.75
    nw = tw(name, pt, 'b')
    return [R(key + '/c', x, y, 32, 32, prst='ellipse', fill=PURPLE, line=None),
            T(key + '/n', x, y, 32, 32, str(n), size=17 * 0.75, color='FFFFFF', weight='b', align='c', anchor='ctr'),
            T(key + '/t', x + 44, y, nw + 16, 32, name, size=pt, color=INK, weight='b', anchor='ctr')]


def sol_cursor(text=QUERY, name='sol/ux2/cur'):
    x, y, w, h = sol_data()['geom']['q2']          # (2) 검색어 글상자. 커서는 덱 글꼴로 잰 글자 끝에
    return R(name, x + tw(text, SOL_QPT) + 2, y + 2, 2, 14, fill=PURPLE, line=None)


def sol_answer():
    """(2) 검색창에 들어간 답: 검색어 글상자와 같은 자리·모양에 글자만 찾은 이름으로."""
    t = copy.deepcopy(next(t for t in sol_data()['texts'] if t['id'] == 'q2'))
    t['lines'] = [[dict(t['lines'][0][0], t=ANSWER)]]
    return [sol_text('sol/ux2/a', t)]


def sol_skel():
    x, y, w, h = sol_data()['geom']['sum1']        # (1) 요약 상자: 글이 써지기 전 빈 줄 셋(잠깐만 보임)
    return [R('sol/ux1/skel/%d' % i, x + 8, y + 25.5 + i * 15, ww, 6, prst='roundRect', radius=3, fill='E1D8FA', line=None)
            for i, ww in enumerate((188, 172, 148))]


def sol_rule(which):
    if which == 'v':
        return R('sol/rule_v', 611, 158, 1, 516, fill='D2C4FA', line=None)
    return R('sol/rule_h', 636, 412, 604, 1, fill='D2C4FA', line=None)


def sol_static(s, ux, xf=SOL_END):
    """이미 설명한 UX 묶음을 마지막 모습 그대로(효과 없음)."""
    s.add('sol/%s/label' % ux, sol_label(ux), xf=xf)
    for k in SOL_Z[ux]:
        if (ux, k) == ('ux2', 'q'):                # 검색창에는 검색어 대신 찾은 이름이 들어가 있음
            s.add('sol/ux2/a', sol_answer(), xf=xf)
            s.add('sol/ux2/cur', [sol_cursor(ANSWER)], xf=xf)
            continue
        s.add('sol/%s/%s' % (ux, k), sol_piece('%s/%s' % (ux, k)), xf=xf, alpha=SOL_ALPHA.get('%s/%s' % (ux, k), 100))


def s_sol1():
    """1쪽 기록 통합 검색: 통화 화면 → (클릭) 위로 밀어 올려 검색 시트 → 입력·검색 → 휴대폰이 오른쪽으로, 이름표는 묶음의 왼쪽 위로 →
    실 셋이 한꺼번에 뻗어 기록에 닿음 → 요약. 11-10 5차: 클릭 한 번에 끝까지(빠르기는 3차와 4차의 사이), 이름표는 처음엔 휴대폰 왼쪽 위."""
    s = Slide('sol1', trans=('fade', 500), bar=False, notes=NOTES['sol1'])
    xf = SOL_ONE
    dxa = 640 - xf.X(454)                      # 처음(A)엔 휴대폰만 장표 가운데 → 기록이 이어질 때 제자리(B, 오른쪽)로
    lab = xf.X(318) + dxa - xf.X(sol_data()['geom']['lab']['ux1'][0])      # 이름표: 처음엔 휴대폰의 왼쪽 끝 위 → 실이 뻗을 때 묶음의 왼쪽 위로
    s.add('sol/title', [sol_title()])

    def K(k):
        return 'sol/ux1/' + k
    s.add(K('label'), sol_label('ux1'), xf=xf, start=(lab, 0))
    for k in SOL_Z['ux1']:
        s.add(K(k), sol_piece('ux1/' + k), xf=xf, start=(dxa, 0) if k in SOL_PHONE else None, alpha=SOL_ALPHA.get('ux1/' + k, 100))
        if k == 'sum':
            s.add(K('skel'), sol_skel(), xf=xf, temp=True)

    def enter(k, kind, t, dur=400, **kw):      # 처음 자리(A)에서 나타남: 나타나는 효과를 먼저 적고(그래야 처음에 숨음) 같은 순간 자리 옮김
        s.on(K(k), kind, t, dur, **kw)
        s.on(K(k), 'goto', t)
    # 장이 열리면: 이름표와 통화 중인 휴대폰(재웅 선배)
    enter('label', 'fade_in', 100, 400)
    enter('phone', 'fade_in', 150, 500)
    enter('call', 'fade_in', 150, 500)
    s.click()      # 1: 위로 밀어 올림 → 검색 시트 → 한 글자씩 입력 → 검색 버튼 → 요약 자리 → 휴대폰은 오른쪽으로 → 실 셋 → 기록과 결과 줄 → 요약이 한 줄씩
    enter('swipe', 'wipe_in', 0, 520, dir='up')
    s.on(K('sheet'), 'fade_in', 450, 320)          # 시트는 아래에서 밀려 올라옴: 처음 자리(A)의 70px 아래에서 A로(이동 경로 하나)
    s.on(K('sheet'), 'move', 450, 560, dx=0, dy=-70, base=(dxa, 70), accel=0, decel=100000)
    enter('go', 'appear', 1030, 1)
    t = 1250
    enter('q', 'type', t, 1, ms=78, n=len(SOL_Q1))
    t += 78 * len(SOL_Q1) + 90
    s.on(K('go'), 'pulse', t, 140, scale=0.86)
    t += 340
    enter('sum', 'fade_in', t, 300)
    s.on(K('skel'), 'jump', t, to=(dxa, 0))
    s.on(K('skel'), 'fade_in', t, 300)
    t += 260
    s.on([K(k) for k in SOL_PHONE] + [K('skel')], 'fly', t, 720, dx=dxa, dy=0, bend=0, show=False, fade=False)
    s.on(K('label'), 'fly', t, 720, dx=lab, dy=0, bend=0, show=False, fade=False)
    t += 640
    s.on([K('th1'), K('th2'), K('th3')], 'wipe_in', t, 400, dir='right')        # 휴대폰(오른쪽)에서 기록 쪽으로 셋이 동시에
    t += 320
    for k in ('note', 'mail', 'cal'):                                           # 실 끝에서 기록이 뜸
        s.on(K(k), 'zoom_in', t, 340, **{'from': 0.8})
    s.on(K('ttl'), 'fade_in', t, 280)
    for i, k in enumerate(('r1', 'r2', 'r3')):                                  # 휴대폰 속 '연결된 기억' 세 줄
        s.on(K(k), 'zoom_in', t + 50 + i * 80, 320, **{'from': 0.94})
    s.on(K('tm'), 'wipe_in', t + 380, 280, dir='down')                          # 민수님 → 민수 메일
    s.on(K('tc'), 'wipe_in', t + 620, 280, dir='down')                          # 메일 → 캘린더
    s.on(K('note0'), 'zoom_in', t + 380, 340, **{'from': 0.85})                 # 11/3 준비 회의(바뀌기 전)
    s.on(K('arr'), 'wipe_in', t + 660, 220, dir='down')                         # ↓ 11/10 주간 회의
    t += 1120
    s.on(K('skel'), 'fade_out', t, 220)
    for i, k in enumerate(('sl1', 'sl2', 'sl3')):
        s.on(K(k), 'wipe_in', t + 70 + i * 390, 450)
    return s


def sol_result(s, K, t0=0, ok=1600):
    """(2)(3) 공통: 실타래 버튼을 누름 → 화살표 → 추천 카드가 떠오름 → (읽을 틈) → 입력하기를 누르는 손. t0 = 시작하는 때, 돌려줌: 눌린 때(ms)."""
    s.on(K('tap'), 'zoom_in', t0, 300, **{'from': 1.3})
    s.on(K('tap'), 'pulse', t0 + 320, 140, scale=0.9)
    s.on(K('arrow'), 'wipe_in', t0 + 500, 340)
    s.on(K('card'), 'zoom_in', t0 + 780, 500, **{'from': 0.9})
    s.on(K('ok'), 'zoom_in', t0 + ok, 320, **{'from': 1.3})
    s.on(K('ok'), 'pulse', t0 + ok + 350, 140, scale=0.9)
    return t0 + ok + 490


def s_sol2():
    """2쪽 단서로 찾는 기억: UX 1은 왼쪽으로(모핑) → 한 글자씩 입력 → 실타래 버튼 → 추천 카드 → 입력하기 →
    답이 칩이 되어 검색창으로 가고 검색어가 찾은 이름으로 바뀜(모션그래픽과 같은 순서). 11-10 5차: 장이 열리면 끝까지 저절로(클릭 없음)."""
    s = Slide('sol2', trans=('morph', 880), bar=False, notes=NOTES['sol2'])
    s.add('sol/title', [sol_title()])
    sol_static(s, 'ux1')
    s.add('sol/rule_v', [sol_rule('v')], xf=SOL_END)
    xf = SOL_MID
    g = sol_data()['geom']
    qx, qy = g['q2'][:2]

    def K(k):
        return 'sol/ux2/' + k

    def band_(name, text, color, alpha):           # 검색창 글자 위 띠(선택 표시, 바뀐 글 훑기)
        return [R(name, qx - 2, qy + 1, tw(text, SOL_QPT) + 4, 16, prst='roundRect', radius=3, fill=color, alpha=alpha, line=None)]
    s.add(K('label'), sol_label('ux2'), xf=xf)
    for k in SOL_Z['ux2']:
        if k == 'q':       # 검색어·선택 띠·커서는 잠깐만(temp), 그 자리에 찾은 이름이 남음
            s.add(K('sel'), band_(K('sel'), QUERY, 'B9A2FF', 55), xf=xf, temp=True)
            s.add(K('q'), sol_piece('ux2/q'), xf=xf, temp=True)
            s.add(K('cur0'), [sol_cursor(QUERY, K('cur0'))], xf=xf, temp=True)
            s.add(K('sweep'), band_(K('sweep'), ANSWER, HL, 36), xf=xf, temp=True)
            s.add(K('a'), sol_answer(), xf=xf)
            s.add(K('cur'), [sol_cursor(ANSWER)], xf=xf)
            continue
        s.add(K(k), sol_piece('ux2/' + k), xf=xf)
    ax, ay, aw, ah = g['ans2']                     # 카드 속 답 글자 → 검색창 글자 자리로 날아가는 칩
    fly, fw = chip(K('fly'), qx - 10, qy - 3, ANSWER, 'fill', pt=SOL_QPT, h=24, padx=10)
    s.add(K('fly'), fly, xf=xf, temp=True)
    fdx, fdy = (ax + aw / 2) - (qx - 10 + fw / 2), (ay + ah / 2) - (qy + 9)
    s.on('sol/rule_v', 'fade_in', 100, 400)
    s.on(K('label'), 'fade_in', 250, 400)
    s.on(K('field'), 'rise', 400, 450, dy=10)
    s.on(K('kb'), 'rise', 480, 450, dy=10)
    s.on(K('q'), 'type', 1050, 1, ms=66, n=len(QUERY))
    s.on(K('q'), 'jump', 1050)
    t = 1050 + 66 * len(QUERY) + 60
    s.on(K('cur0'), 'jump', t)
    s.on(K('cur0'), 'blink', t + 30, 1000)
    t += 420       # 실타래 버튼 톡 → 추천 카드 → 입력하기 → 검색창의 글이 찾은 이름으로
    s.on(K('pen'), 'zoom_in', t + 260, 300, **{'from': 0.6})
    t = sol_result(s, K, t0=t, ok=2050) + 60
    s.on(K('sel'), 'wipe_in', t, 260)              # 검색어가 선택되고
    s.on(K('sel'), 'jump', t)
    s.on(K('fly'), 'fade_in', t, 130)              # 답이 칩이 되어 검색창으로
    s.on(K('fly'), 'fly', t, 620, dx=fdx, dy=fdy, bend=0.3, show=False, fade=False, grow=1.5)
    t += 620
    s.on([K('q'), K('sel')], 'fade_out', t - 40, 80)
    s.on(K('cur0'), 'move', t, 1, dx=OFF, dy=0)    # 깜빡이던 커서는 화면 밖으로
    s.on(K('a'), 'appear', t, 1)                   # 타이핑 없이 바로 바뀜
    s.on(K('sweep'), 'wipe_in', t, 320)
    s.on(K('sweep'), 'jump', t)
    s.on(K('fly'), 'fade_out', t, 160)
    s.on(K('cur'), 'appear', t + 40, 1)
    s.on(K('cur'), 'blink', t + 70, 1000)
    s.on(K('sweep'), 'fade_out', t + 680, 300)
    return s


def s_sol3():
    """3쪽 먼저 건네는 기억: UX 2는 오른쪽 위로(모핑) → 위치 → 탑승권 → 실타래 버튼에 알림 → 누름 → 추천 카드.
    11-10 5차: 장이 열리면 끝까지 저절로(클릭 없음)."""
    s = Slide('sol', trans=('morph', 880), bar=False, notes=NOTES['sol'])
    s.add('sol/title', [sol_title()])
    sol_static(s, 'ux1')
    s.add('sol/rule_v', [sol_rule('v')], xf=SOL_END)
    sol_static(s, 'ux2')
    s.add('sol/rule_h', [sol_rule('h')], xf=SOL_END)

    def K(k):
        return 'sol/ux3/' + k
    s.add(K('label'), sol_label('ux3'), xf=SOL_END)
    for k in SOL_Z['ux3']:
        s.add(K(k), sol_piece('ux3/' + k), xf=SOL_END)
    s.on('sol/rule_h', 'fade_in', 100, 400)
    s.on(K('label'), 'fade_in', 250, 400)
    s.on(K('kb'), 'rise', 400, 450, dy=10)
    s.on(K('gps'), 'zoom_in', 1000, 360, **{'from': 0.8})                # 위치
    s.on(K('wallet'), 'zoom_in', 1650, 360, **{'from': 0.8})             # 탑승권(삼성 월렛)
    s.on(K('glow'), 'zoom_in', 2400, 440, **{'from': 0.5})               # 알림: 실타래 버튼이 켜지고
    s.on(K('badge'), 'zoom_in', 2660, 300, **{'from': 0.3})              # 빨간 1
    s.on(K('pen'), 'zoom_in', 2600, 300, **{'from': 0.6})                # 반짝!
    s.on(K('glow'), 'pulse', 2980, 190, scale=1.12)
    sol_result(s, K, t0=3750, ok=1750)             # 켜진 버튼을 누름 → 추천 카드 → 입력하기
    return s


SOL_SLIDES = [s_sol1, s_sol2, s_sol3]


# ------------------------------------------------------------------ 0. 솔루션 → How it works?
def s_hiw():
    s = Slide('hiw', trans=('fade', 500), bar=False,
              notes=NOTES['hiw'])
    s.add('bg/blur', [P('bg/blur', str(OUT / 'blur_sol.png'), 0, 0, 1280, 720)])
    s.add('hiw/big', [caption('hiw/big', [[('How it ', INK), ('works?', PURPLE)]], 640, 300, size=80)])
    s.on('hiw/big', 'rise', 120, 450, dy=10)
    return s


# ------------------------------------------------------------------ 1. 질문
PHONE = (100, 110, 636, 706)       # 11-10: 뱃지가 빠져 휴대폰 + 글 묶음을 가운데로(왼쪽으로 50px). 아래는 계속 잘림


def phone_prims(key, alpha=100):
    x, y, w, h = PHONE
    gw = 230
    gh = gw * 276 / 816
    return [R(key + '/body', x, y, w, h, prst='roundRect', radius=64, fill='FFFFFF', line=LINE2, line_w=1.6, shadow=SHADOW_LIFT),
            R(key + '/notch', x + w / 2 - 56, y + 22, 112, 14, prst='roundRect', fill='ECE8F4', line=None),
            P(key + '/g', ICON['google'], x + w / 2 - gw / 2, y + 92, gw, gh)]


def s_ask():
    s = Slide('ask', trans=('morph', 1000), bar=False,
              notes=NOTES['ask'])
    s.add('ask/phone', phone_prims('ask/phone'))
    pill, txt, cur, _ = search_pill('ask/sp', PHONE[0] + 38, 318, 560, 84, QUERY, pt=19)
    s.add('ask/sp', pill)
    s.add('ask/q', [txt])
    s.add('ask/cur', [cur])
    s.add('ask/cap', [caption('ask/cap', [[('집들이 때 마셨던 와인,', INK)], [('이름이 뭐였더라?', PURPLE)]], PHONE[0] + PHONE[2] + 38, 315, size=30,
                              align='l')])
    s.on('ask/cap', 'rise', 350, 550, dy=16)
    n = len(QUERY)
    s.on('ask/q', 'type', 1000, 1, ms=55, n=n)
    t_end = 1000 + 55 * n + 60
    s.on('ask/cur', 'appear', t_end, 1)
    s.on('ask/cur', 'blink', t_end + 30, 1000)
    return s


# ------------------------------------------------------------------ 2. 흩어진 단서
FLOATS = [
    # (키, 종류, 제목, 한 줄, x, y, 배율, 투명도) — 표지처럼 크기를 섞음. 가운데 제목 자리(x 262~1018, y 290~366)는 비움
    # 11-10: 글자를 키움(제목 13 → 14.5pt, 한 줄 10.5 → 11.5pt, 배율도 0.8 → 0.86부터). 뱃지가 빠져 위쪽까지 고르게
    ('f_note1', 'note', '지은이네 주소', '경기도 수원시 영통구…', 414, 116, 1.0, 72),
    ('f_note2', 'note', '장 볼 것', '우유, 계란, 휴지', 706, 62, 0.9, 42),
    ('f_talk4', 'talk', '택배', '문 앞에 두고 갔어요', 790, 176, 0.86, 36),
    ('f_mail1', 'mail', '관리비 고지서', '2월분 관리비', 36, 290, 0.95, 46),
    ('f_cal3', 'cal', '팀 회식', '3/20 (금) 19:00', 52, 404, 0.92, 42),
    ('f_talk3', 'talk', '엄마', '반찬 보냈다', 88, 514, 0.9, 42),
    ('f_mail2', 'mail', '[예약 확인] 오사카 호텔', '2월 27일', 56, 622, 0.86, 36),
    ('f_note3', 'note', '소믈리에 추천', '샤토 마고', 548, 424, 1.0, 54),
    ('f_phone', 'phone', '부재중 전화', '어제 오후 3:12', 778, 430, 0.86, 34),
    ('f_cal2', 'cal', '치과 예약', '3/4 (수) 오전 10:30', 716, 610, 0.95, 44),
    ('f_cal1', 'cal', '성빈이 신혼집들이', '2025. 10. 18 (토)', 966, 408, 1.0, 68),
    ('f_talk2', 'talk', '팀 단톡방', '회의록 공유해요', 1066, 516, 0.95, 48),
    ('f_gal2', 'gallery', 'IMG_2433.jpg', '3월 8일 12:40', 1030, 624, 0.9, 38),
    ('f_map', 'map', '저장한 장소', '성수 카페', 528, 566, 0.86, 36),
]


def frag(key, kind, title, meta, x, y, s=1.0, alpha=100, style='base'):
    """흩어진 작은 기록 조각(아이콘 + 제목 + 한 줄)."""
    pt1, pt2 = 14.5 * s, 11.5 * s
    isz = 32 * s
    h = 66 * s
    w = 16 * s + isz + 12 * s + max(tw(title, pt1, 'b'), tw(meta, pt2)) + 22 * s
    tx = x + 16 * s + isz + 12 * s
    ln = {'base': (LINE, 1.0), 'weave': (RING, 2.4)}[style]
    return [R(key + '/bg', x, y, w, h, prst='roundRect', radius=16 * s, fill='FFFFFF', line=ln[0], line_w=ln[1], shadow=SHADOW_SOFT,
              glow=(12, RING, 30) if style == 'weave' else None),
            P(key + '/ic', ICON[kind], x + 16 * s, y + (h - isz) / 2, isz, isz),
            T(key + '/t', tx, y + 10 * s, w, 24 * s, title, size=pt1, color=INK, weight='b'),
            T(key + '/m', tx, y + 36 * s, w, 20 * s, meta, size=pt2, color=MUTE)], w, h


CL_TALK = ('지은', '카카오톡 · 3월 15일 (일)', ['박스 정리 다 했어! 이따 올 때', '휴지 안 사 와도 돼'])
CL_PT = 38                         # 가운데 두 문장 글자 크기


def cloud_cards():
    """큰 카드 셋(지은 카톡, 그날 와인 사진, 다른 날 와인 사진). 돌려줌: [(키, card() 결과, (x, y, w), 투명도)]."""
    tw_ = card_fit(CL_TALK[0], CL_TALK[1], CL_TALK[2], pt=12.5, title_pt=15, meta_pt=10.5, bubble=True)
    talk = card('cl_talk', 'talk', 60, 84, tw_, CL_TALK[0], CL_TALK[1], CL_TALK[2], pt=12.5, title_pt=15, meta_pt=10.5)
    photo = card('cl_photo', 'photo', 984, 56, 244, '갤러리', '3월 15일 (일) 20:14', img=PH['babich'][0], img_h=142,
                 img_focus=PH['babich'][2], title_pt=15, meta_pt=10.5)
    photo2 = card('cl_photo2', 'photo', 308, 448, 204, '갤러리', '2025. 9. 27', img=PH['w2'][0], img_h=104, img_focus=PH['w2'][2],
                  title_pt=15, meta_pt=10.5)
    return [('cl_photo2', photo2, (308, 448, 204), 62), ('cl_talk', talk, (60, 84, tw_), 72), ('cl_photo', photo, (984, 56, 244), 72)]


def s_cloud():
    s = Slide('cloud', trans=('morph', 900), bar=False,
              notes=NOTES['cloud'])
    order = []
    for key, kind, title, meta, x, y, sc, al in FLOATS:
        prims, w, h = frag(key, kind, title, meta, x, y, sc)
        s.add(key, prims, alpha=al)
        order.append(key)
    for key, c, _, al in cloud_cards():
        s.add(key, c[0], alpha=al)
    keys = order[:]
    random.Random(7).shuffle(keys)
    keys = ['cl_talk', 'cl_photo'] + keys[:5] + ['cl_photo2'] + keys[5:]
    for i, k in enumerate(keys):
        s.on(k, 'rise', 120 + i * 55, 480, dy=14)
    if PASS1:                      # 흐린 그림을 만들 1차 빌드: 조각만(글과 흐린 그림 없이)
        return s
    # 둘째 문장으로 넘어갈 때 주변 조각이 살짝 흐려짐: 같은 화면을 PowerPoint로 찍어 흐리게 한 그림이 위에 겹쳐 나타남
    s.add('cl/blur', [P('cl/blur', str(OUT / 'blur_cloud.png'), 0, 0, 1280, 720)])
    # 첫 문장은 잠깐만(temp: 화면 밖에 두고 장이 열리면 제자리로) → 클릭하면 둘째 문장으로 바뀜. 정적 보기엔 둘째 문장만
    # 11-10 4차: 두 문장 모두 34 → 38pt
    s.add('cl_t1', [caption('cl_t1', [[('정답은 분명 ', INK), ('기기 안', PURPLE), ('에', INK)]], 640, 302, size=CL_PT)], temp=True)
    s.add('cl_t2', [caption('cl_t2', [[('그러나, ', INK), ('여러 앱에 흩어져 있는 단서들', PURPLE)]], 640, 302, size=CL_PT)])
    s.on('cl_t1', 'jump', 700)
    s.on('cl_t1', 'fade_in', 700, 500)
    s.click()
    s.on('cl/blur', 'fade_in', 0, 650)
    s.on('cl_t1', 'fade_out', 0, 250)
    s.on('cl_t2', 'rise', 250, 500, dy=14)
    return s


# ------------------------------------------------------------------ 3. 기존 검색이라면?
def old_title(y=300, size=54):
    return caption('old/title', [[('기존 검색', PURPLE), ('이라면?', INK)]], 640, y, size=size)


def s_old():
    s = Slide('old', trans=('fade', 600), bar=False, notes=NOTES['old'])      # 흐려진 앞 장에서 그대로 걷힘
    s.add('old/title', [old_title(300, 56)])
    s.on('old/title', 'pop', 0, 650, **{'from': 0.7, 'over': 1.05})
    return s


# 키워드 장의 자리
OLD_Y = 72                         # '기존 검색이라면?' 작은 제목(키워드·임베딩 장)
KW_PANEL = (370, 132, 540, 124)
KW_FIELD = (392, 182, 496, 54)
KW_PT, KW_TPT, KW_MPT = 12, 14.5, 10.5      # 11-10: 결과 카드 글자를 조금 키움(11 → 12pt)
KW_CARDS = [    # (종류, 제목, 앱 · 날짜, 본문, 겹친 단어)
    ('note', '지은이네 주소', '삼성노트 · 2025. 9. 2', ['경기도 수원시 영통구 매탄로 77', '푸른숲아파트 103동 1204호'], '지은이네'),
    ('cal', '성빈이 신혼집들이', '캘린더 · 2025. 10. 18 (토)', ['오후 6:00  성빈이네'], '집들이'),
    ('wallet', '와인앤모어 성수점', '삼성 월렛 · 2025. 12. 24', ['결제 38,000원'], '와인'),
]
KW_Y = 334
KW_GAL = (375, 490, 530)
# 11-10 4차: ✕가 뜰 때 옆에 따라 나오는 한마디(카드 셋 + 갤러리).
# 5차: '다른 날 와인 결제' → '다른 날 결제 내역', 갤러리는 '읽을 수 없는 사진' → '키워드가 없는 사진'(키워드 검색은 같은 글자를 찾는데 사진에는 '와인'도 '집들이'도 적혀 있지 않음)
KW_VERDICT = ['관련 없는 주소 정보', '다른 사람 집들이', '다른 날 결제 내역', '키워드가 없는 사진']      # 11-11 8차: '관련 없는 집 주소' → '관련 없는 주소 정보'


def method_chip(name, x, y, title, label, title_pt=16):
    """판 제목 옆 작은 회색 뱃지(키워드 검색 → BM25, 임베딩 검색 → One-hop)."""
    return chip(name, x + tw(title, title_pt, 'b') + 10, y + 3, label, 'grayfill', pt=9.5, h=22, padx=9)[0]


def kw_layout():
    """결과 카드 셋의 자리와 폭. 11-10: 폭을 글에 맞춰 오른쪽 여백을 줄임 → 전체 폭이 줄어 다음 장에서 덜 작아짐."""
    ws = [card_fit(t, m, ls, pt=KW_PT, title_pt=KW_TPT, meta_pt=KW_MPT, slack=14) for _, t, m, ls, _ in KW_CARDS]
    gap = 22
    x = 640 - (sum(ws) + gap * (len(ws) - 1)) / 2
    xs = []
    for w in ws:
        xs.append(x)
        x += w + gap
    return xs, ws


def kw_parts(dimmed=()):
    """키워드 검색 구성(판, 단어 셋 → 결과 셋, 실이 닿지 않는 갤러리). 돌려줌: [(키, 원시)] 와 자리 정보.
    11-09: 지은이네 → 주소 메모, 집들이 → 다른 사람 신혼집들이, 와인 → 월렛 결제. 사진 속 글자는 라벨의 영문뿐이라 '와인'으로는 닿지 않음."""
    px, py, pw, ph = KW_PANEL
    fx, fy, fw, fh = KW_FIELD
    parts = [('kw/panel', [R('kw/panel/bg', px, py, pw, ph, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.4,
                             shadow=SHADOW_CARD),
                           T('kw/panel/l', px + 24, py + 13, 200, 28, '키워드 검색', size=16, color=INK, weight='b')] +
              method_chip('kw/panel/m', px + 24, py + 13, '키워드 검색', 'BM25') +
              [R('kw/panel/f', fx, fy, fw, fh, prst='roundRect', fill='F7F5FC', line=LINE, line_w=1.0)])]
    qpt = 16.5
    S = qpt * 4 / 3
    qx, qy = fx + 20, fy + (fh - S * 1.2) / 2
    parts.append(('kw/q', [T('kw/q', qx, qy, fw - 30, S * 1.3, QUERY, size=qpt, color=INK)]))
    qpos = (qx, qy, QUERY, qpt, 'r')
    bands = [band('kw/h%d' % (i + 1), qpos, c[4]) for i, c in enumerate(KW_CARDS)]
    for i, b in enumerate(bands):
        parts.append(('kw/h%d' % (i + 1), [b]))
    # 결과 셋: 판 아래 가운데에 한 줄
    xs, ws = kw_layout()
    cards = [card('kw/c%d' % (i + 1), c[0], xs[i], KW_Y, ws[i], c[1], c[2], c[3], bubble=False, pt=KW_PT, title_pt=KW_TPT, meta_pt=KW_MPT)
             for i, c in enumerate(KW_CARDS)]
    boxes = {}
    for i, c in enumerate(cards):
        k = 'kw/c%d' % (i + 1)
        parts.append((k, c[0]))
        boxes[k] = (xs[i], KW_Y, ws[i], c[1])
    for i, c in enumerate(cards):                                                     # 카드 안 같은 단어
        parts.append(('kw/m%d' % (i + 1), [band('kw/m%d' % (i + 1), c[2]['title'], KW_CARDS[i][4], pad=(1, -1))]))      # 굵은 글자는 띠가 더 튀어 보여 안쪽으로
    for i, b in enumerate(bands):                                                     # 실: 단어 아래 → 카드 위
        x, y, w, h = boxes['kw/c%d' % (i + 1)]
        parts.append(('kw/t%d' % (i + 1), thread('kw/t%d' % (i + 1), vcurve((b[2] + b[4] / 2, py + ph - 2), (x + w / 2, y + 2), 0.55), w=2.4)))
    for i in range(3):                                                                # ✕와 그 옆 한마디(카드 가운데에 한 묶음으로)
        x, y, w, h = boxes['kw/c%d' % (i + 1)]
        xm, pill = verdict('kw/x%d' % (i + 1), 'kw/v%d' % (i + 1), x + w / 2, y + h / 2 + 4, KW_VERDICT[i])
        parts += [('kw/x%d' % (i + 1), xm), ('kw/v%d' % (i + 1), pill)]
    gx, gy, gw = KW_GAL
    g = gallery('kw/gal', gx, gy, gw, [PH[k] for k in WINE4], cols=4, ph=96, date_pt=10)
    parts.append(('kw/gal', g[0]))
    boxes['kw/gal'] = (gx, gy, gw, g[1])
    xm, pill = verdict('kw/x4', 'kw/v4', gx + gw / 2, gy + g[1] / 2 + 4, KW_VERDICT[3], xs=50, xw=5.5, pt=12.5, h=30)
    parts += [('kw/x4', xm), ('kw/v4', pill)]
    return parts, boxes


def kw_small():
    """임베딩 장 왼쪽 칸(x 36~588)에 줄여 넣는 키워드 구성. 11-10: 카드 폭이 줄어 0.6 → 약 0.75배."""
    _, boxes = kw_parts()
    x0 = min(KW_PANEL[0], min(b[0] for b in boxes.values()))
    x1 = max(KW_PANEL[0] + KW_PANEL[2], max(b[0] + b[2] for b in boxes.values()))
    y0, y1 = KW_PANEL[1], max(b[1] + b[3] for b in boxes.values())
    s = min(0.8, 552 / (x1 - x0))
    return Xf(ax=x0, ay=y0, bx=36 + (552 - (x1 - x0) * s) / 2, by=404 - (y1 - y0) * s / 2, s=s)


KW_KEYS = ['kw/t1', 'kw/t2', 'kw/t3', 'kw/c1', 'kw/c2', 'kw/c3', 'kw/gal', 'kw/panel', 'kw/q', 'kw/m1', 'kw/m2', 'kw/m3',
           'kw/h1', 'kw/h2', 'kw/h3', 'kw/x1', 'kw/v1', 'kw/x2', 'kw/v2', 'kw/x3', 'kw/v3', 'kw/x4', 'kw/v4']


def s_kw():
    s = Slide('kw', trans=('morph', 900), bar=False,
              notes=NOTES['kw'])
    s.add('old/title', [old_title(OLD_Y, 30)])
    parts, _ = kw_parts()
    pm = dict(parts)
    for k in KW_KEYS:
        s.add(k, pm[k])
    s.on('kw/panel', 'rise', 100, 500, dy=14)
    s.on('kw/q', 'fade_in', 300, 400)
    for n in (1, 2, 3):          # 단어 → 실 → 결과 → 같은 단어, 다음 클릭에 ✕와 그 옆 한마디(발표자가 누름)
        s.click()
        s.on('kw/h%d' % n, 'wipe_in', 0, 380)
        s.on('kw/t%d' % n, 'wipe_in', 300, 450, dir='down')
        s.on('kw/c%d' % n, 'rise', 650, 450, dy=14)
        s.on('kw/m%d' % n, 'wipe_in', 1000, 300)
        s.click()
        s.on('kw/x%d' % n, 'zoom_in', 0, 300, **{'from': 0.8})
        s.on('kw/v%d' % n, 'wipe_in', 160, 320)
        s.on(['kw/c%d' % n, 'kw/m%d' % n], 'dim', 0, 350, to=0.45)
    s.click()                    # 실이 닿지 않는 그날 사진들, 다음 클릭에 ✕
    s.on('kw/gal', 'rise', 0, 450, dy=14)
    s.click()
    s.on('kw/x4', 'zoom_in', 0, 300, **{'from': 0.8})
    s.on('kw/v4', 'wipe_in', 160, 340)
    s.on('kw/gal', 'dim', 0, 350, to=0.45)
    return s


# 임베딩 장
EM_PANEL = (624, 132, 600, 124)
EM_FIELD = (646, 182, 556, 54)
SPACE = (624, 314, 600, 330)
STAR = (884, 494)
SPACE_NOTE = '* 임베딩 공간에서는 의미가 비슷할수록 가까이 위치함'      # 11-11 7차: 각주는 '~함' 말씨로


def space_note(name, box, text, pt=10):
    """임베딩 공간 그림 아래(오른쪽 끝)의 작은 각주."""
    x, y, w, h = box
    tw_ = tw(text, pt) + 8
    return T(name, x + w - tw_ - 4, y + h + 7, tw_ + 4, 18, text, size=pt, color=MUTE, align='r')


def s_emb():
    """11-10 4차: 가까운 기록은 '소믈리에 추천' 메모와 다른 날 와인 사진 두 장(레드, 화이트). ✕는 메모 → 와인 둘(한마디와 함께) 순서로,
    멀리 있는 지은 카톡에는 공간이 펼쳐질 때부터 '단서' 표(5차: 보라, 처음부터)."""
    s = Slide('emb', trans=('morph', 1000), bar=False,
              notes=NOTES['emb'])
    s.add('old/title', [old_title(OLD_Y, 30)])
    parts, _ = kw_parts()
    pm = dict(parts)
    small = kw_small()
    for k in KW_KEYS:
        s.add(k, pm[k], alpha=24 if k.startswith(('kw/c', 'kw/m', 'kw/gal')) else 40, xf=small)
    s.add('em/div', [line('em/div', (602, 170), (602, 640), color='E2DBF5', w=1.4)])
    px, py, pw, ph = EM_PANEL
    fx, fy, fw, fh = EM_FIELD
    s.add('em/panel', [R('em/panel/bg', px, py, pw, ph, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.4,
                         shadow=SHADOW_CARD),
                       T('em/panel/l', px + 24, py + 13, 200, 28, '임베딩 검색', size=16, color=INK, weight='b')] +
          method_chip('em/panel/m', px + 24, py + 13, '임베딩 검색', 'One-hop') +
          [R('em/panel/f', fx, fy, fw, fh, prst='roundRect', fill='F7F5FC', line=LINE, line_w=1.0)])
    qpt = 16.5
    S = qpt * 4 / 3
    qx, qy = fx + 20, fy + (fh - S * 1.2) / 2
    s.add('em/hl', [hl_band('em/hl', qx, qy, QUERY, QUERY, qpt, kind='low', alpha=36)])
    s.add('em/q', [T('em/q', qx, qy, fw - 30, S * 1.3, QUERY, size=qpt, color=INK)])
    # 벡터 줄
    vy = 268
    vec = '[0.80, 0.30, −0.83, 0.90, −0.02, …]'
    vtx = qx + tw(QUERY, qpt) / 2
    s.add('em/vt', thread('em/vt', [(vtx, fy + fh + 2)] * 2 + [(vtx, vy - 4)] * 2, w=2.2))
    s.add('em/vl', [T('em/vl', px + 24, vy, 60, 30, '벡터', size=13.5, color=PURPLE, weight='b', anchor='ctr')])
    s.add('em/vec', [T('em/vec', px + 84, vy, 460, 30, vec, size=15.5, color=PURPLE, weight='m', anchor='ctr')])
    # 임베딩 공간(클릭 2에 펼쳐짐)
    sx, sy, sw, sh_ = SPACE
    s.add('em/space', [R('em/space/bg', sx, sy, sw, sh_, prst='roundRect', radius=20, fill='FFFFFF', alpha=86, line=LINE2, line_w=1.2),
                       T('em/space/l', sx + 18, sy + 12, 200, 24, '임베딩 공간', size=12, color=PURPLE, weight='b')])
    s.add('em/note', [space_note('em/note', SPACE, SPACE_NOTE)])
    # 질문 곁의 기록 셋: 메모(왼쪽 위), 와인 사진 둘(오른쪽에 위아래로 — 둘 사이에 '다른 날 마신 와인'이 걸침)
    memo, mw, mh = mini_chip('em/r_memo', STAR[0] - 196, STAR[1] - 74, 'note', '소믈리에 추천', '샤토 마고', pt=11.5)
    pic1, pw1, ph1 = mini_chip('em/r_pic', STAR[0] + 56, STAR[1] - 58, 'gallery', '와인 사진', PH['glass'][1], pt=11.5, img=PH['glass'][0])
    pic2, pw2, ph2 = mini_chip('em/r_pic2', STAR[0] + 56, STAR[1] + 2, 'gallery', '와인 사진', PH['bar'][1], pt=11.5, img=PH['bar'][0])
    memo_box = (STAR[0] - 196, STAR[1] - 74, mw, mh)
    pic1_box = (STAR[0] + 56, STAR[1] - 58, pw1, ph1)
    pic2_box = (STAR[0] + 56, STAR[1] + 2, pw2, ph2)
    far = [('em/r_mail', 'mail', '관리비 고지서', sx + 22, sy + 38), ('em/r_cal', 'cal', '팀 회식', sx + 458, sy + 50),
           ('em/r_talk2', 'talk', '택배', sx + 28, sy + 274), ('em/r_note', 'note', '지은이네 주소', sx + 424, sy + 278),
           ('em/r_jieun', 'talk', '지은', sx + 500, sy + 152)]
    far_p = []
    keep_out = [memo_box, pic1_box, pic2_box, (memo_box[0], memo_box[1] + mh, mw, 34)]
    for k, kind, label, x_, y_ in far:
        prims, w_, h_ = mini_chip(k, x_, y_, kind, label, pt=11.5, alpha=70)
        far_p.append((k, prims))
        keep_out.append((x_, y_, w_, h_))
    rnd = random.Random(11)
    dots = []
    for i in range(30):         # 배경 점은 별과 기록 칩 자리를 피해 찍음(옅어진 칩 뒤로 점이 비치지 않게)
        while True:
            x_, y_ = sx + 24 + rnd.random() * (sw - 48), sy + 46 + rnd.random() * (sh_ - 66)
            if (abs(x_ - STAR[0]) > 40 or abs(y_ - STAR[1]) > 40) and not any(
                    bx - 10 < x_ < bx + bw + 10 and by - 10 < y_ < by + bh + 10 for bx, by, bw, bh in keep_out):
                break
        r_ = 3.2 + rnd.random() * 2.4
        dots.append(R('em/dot%d' % i, x_ - r_, y_ - r_, 2 * r_, 2 * r_, prst='ellipse', fill='CBC0EC', alpha=80, line=None))
    s.add('em/dots', dots)
    # 가까운 원(점선)은 기록 칩보다 먼저 그려 칩 글자 위로 지나가지 않게
    s.add('em/near', [R('em/near', STAR[0] - 196, STAR[1] - 120, 392, 240, prst='ellipse', fill=None, line=PURPLE2, line_w=1.8,
                        dash='dash')])
    for k, prims in far_p:
        s.add(k, prims)
    jx, jy = far[-1][3], far[-1][4]
    s.add('em/clue', clue_tag('em/clue', jx, jy))                  # 멀리 있는 지은 카톡이 '단서'(11-10 5차: 다른 장과 같은 보라 표, 공간이 펼쳐질 때부터)
    s.add('em/r_memo', memo)
    s.add('em/r_pic', pic1)
    s.add('em/r_pic2', pic2)
    s.add('em/star', star('em/star', *STAR) + [T('em/star/l', STAR[0] - 30, STAR[1] + 18, 60, 20, '질문', size=10.5, color=PURPLE,
                                                 weight='b', align='c')])
    s.add('em/k1', [ring_box('em/k1', memo_box, pad=4, radius=14, w=2.2)])
    s.add('em/k2', [ring_box('em/k2', pic1_box, pad=4, radius=14, w=2.2)])
    s.add('em/k3', [ring_box('em/k3', pic2_box, pad=4, radius=14, w=2.2)])
    # ✕와 한마디: 메모는 칩 바로 아래에, 와인 사진은 두 장 사이에 걸쳐서
    x1, v1 = verdict('em/x1', 'em/v1', memo_box[0] + mw / 2, memo_box[1] + mh + 19, '관련 없는 메모', xs=20, xw=4.0, pt=10.5, h=24)
    x2, v2 = verdict('em/x2', 'em/v2', pic1_box[0] + pw1 / 2, (pic1_box[1] + ph1 + pic2_box[1]) / 2, '다른 날 마신 와인', xs=20, xw=4.0,
                     pt=10.5, h=24)
    s.add('em/x1', x1)
    s.add('em/v1', v1)
    s.add('em/x2', x2)
    s.add('em/v2', v2)
    # 효과
    s.on('em/div', 'fade_in', 200, 400)
    s.on('em/panel', 'rise', 300, 500, dy=14)
    s.on('em/q', 'fade_in', 500, 400)
    s.click()   # 1: 질문 전체 → 벡터
    s.on('em/hl', 'wipe_in', 0, 650)
    s.on('em/vt', 'wipe_in', 550, 300, dir='down')
    s.on('em/vl', 'fade_in', 800, 250)
    s.on('em/vec', 'type', 850, 1, ms=26, n=len(vec))
    s.click()   # 2: 기록이 놓인 공간이 가까운 것부터 펼쳐짐
    s.on('em/space', 'zoom_in', 0, 500, **{'from': 0.94})
    s.on('em/dots', 'fade_in', 250, 500)
    for i, k in enumerate(['em/r_memo', 'em/r_pic', 'em/r_pic2', 'em/r_jieun', 'em/r_note', 'em/r_cal', 'em/r_mail', 'em/r_talk2']):
        s.on(k, 'zoom_in', 350 + i * 80, 400, **{'from': 0.7})
    s.on('em/clue', 'zoom_in', 350 + 3 * 80 + 120, 320, **{'from': 0.6})
    s.on('em/note', 'fade_in', 900, 400)
    s.click()   # 3: 질문 별이 공간에 앉고 가장 가까운 세 기록
    vx_, vy_ = px + 84 + tw(vec, 15.5) / 2, vy + 15
    s.on('em/star', 'fly', 0, 800, dx=vx_ - STAR[0], dy=vy_ - STAR[1], bend=0.12)
    s.on('em/near', 'zoom_in', 750, 450, **{'from': 0.4})
    s.on(['em/k1', 'em/k2', 'em/k3'], 'zoom_in', 1150, 350, **{'from': 1.12})
    s.click()   # 4: 메모 ✕(발표자가 누름)
    s.on('em/x1', 'zoom_in', 0, 300, **{'from': 0.8})
    s.on('em/v1', 'wipe_in', 150, 300)
    s.on(['em/r_memo', 'em/k1'], 'dim', 0, 380, to=0.45)
    s.click()   # 5: 와인 사진 둘이 함께 흐려지고 그 사이에 ✕ → 멀리 있는 지은 카톡에 '단서'
    s.on(['em/r_pic', 'em/r_pic2', 'em/k2', 'em/k3'], 'dim', 0, 380, to=0.45)
    s.on('em/x2', 'zoom_in', 100, 300, **{'from': 0.8})
    s.on('em/v2', 'wipe_in', 250, 300)
    tc = max(cue('emb.clue', 950, ahead=0.1), 950)          # 끝에 짚어 줌: 진짜 단서는 저 멀리. '정작 단서는'을 말할 때(CUES)
    for i in range(2):                                      # 11-11 8차: 조금 더 크게(1.1 → 1.16), 두 번 튐
        s.on(['em/r_jieun', 'em/clue'], 'pulse', tc + i * 420, 170, scale=1.16)
    return s


# ------------------------------------------------------------------ 4. Let's think step by step → 끊어진 고리
def step_title(y, size):
    return caption('step/title', [[("Let's think ", INK), ('step by step!', PURPLE)]], 640, y, size=size)


def s_step():
    s = Slide('step', trans=('fade', 600), bar=False, notes=NOTES['step'])
    s.add('bg/blur', [P('bg/blur', str(OUT / 'blur_emb.png'), 0, 0, 1280, 720)])
    s.add('step/title', [step_title(306, 62)])
    s.on('step/title', 'pop', 200, 700, **{'from': 0.62, 'over': 1.06})
    return s


TALK_K = 1.2                        # 11-11 6차: 끊어진 고리·데이터 색인 장의 지은 카톡 카드를 1.2배로('약간 작네')


def _gap():
    """빠진 고리 자리. 클릭하면 이 자리에 지은 카톡(중간 단서)이 들어옴(키운 카드 + 사방 16px, 가운데는 그대로)."""
    w = jieun_fit()
    h = jieun_card('ch/talk', 0, 0, w)[1]
    gw, gh = round(w * TALK_K) + 32, round(h * TALK_K) + 32
    return (640 - gw / 2, 366 - gh / 2, gw, gh)


GAP = _gap()
CH_GAL = (874, 228, 360)


def chain_talk(x, y, w=356):
    """00 데이터 색인 장의 지은 카톡(날짜 강조 없이). 끊어진 고리 장의 카드(jieun_card)와 같은 키라 모핑으로 이어진다."""
    return jieun_card('ch/talk', x, y, w, date=False)


def s_chain():
    """11-10 4차: 처음엔 물음표 자리와 흐린 와인 사진 넷 → (클릭) 물음표 자리에 중간 단서(지은 카톡: 근거 두 군데와 날짜 강조)가 들어오고
    실이 이어져 그날 사진에 테두리와 이름."""
    s = Slide('chain', trans=('morph', 1000), bar=False,
              notes=NOTES['chain'])
    s.add('step/title', [step_title(OLD_Y, 30)])
    gx, gy, gw, gh = GAP
    cy = gy + gh / 2
    cx_, cy_, cw_ = CH_GAL
    gal = gallery('ch/gal', cx_, cy_, cw_, [PH[k] for k in WINE4], cols=2, show_dates=False, ph=104, gap=10)
    spots = gal[2]
    a1, b1 = (46 + 360, cy), (gx, cy)
    a2, b2 = (gx + gw, cy), (cx_, cy_ + gal[1] / 2)
    s.add('ch/l1', [C('ch/l1', scurve(a1, b1), w=2.2, color='C9BEEB', dash='dash')])
    s.add('ch/l2', [C('ch/l2', scurve(a2, b2), w=2.2, color='C9BEEB', dash='dash')])
    # 이어진 뒤의 실(점선 위에 겹쳐 그려짐). 양 끝은 검색창·카드·갤러리 아래로 조금 들어감
    s.add('ch/t1', thread('ch/t1', scurve((a1[0] - 6, cy), (gx + 24, cy)), w=2.4))
    s.add('ch/t2', thread('ch/t2', scurve((gx + gw - 24, cy), (b2[0] + 6, b2[1])), w=2.4))
    pill, txt, _, _ = search_pill('ch/sp', 46, cy - 30, 360, 60, QUERY, pt=14.5, icon='spool', cursor=False)
    s.add('ch/sp', pill + [txt])
    s.add('ch/gap', [R('ch/gap/bg', gx, gy, gw, gh, prst='roundRect', radius=24, fill=LAV2, alpha=80, line=PURPLE2, line_w=2.2,
                       dash='dash'),
                     T('ch/gap/q', gx, gy, gw, gh, '?', size=72, color=PURPLE, weight='b', align='c', anchor='ctr')], temp=True)
    s.add('ch/gal', gal[0])
    wi = WINE4.index('babich')
    s.add('ch/dim', [dim_over('ch/dim%d' % i, sp, radius=10, alpha=68) for i, sp in enumerate(spots) if i != wi])
    s.add('ch/dimb', [dim_over('ch/dimb', spots[wi], radius=10, alpha=68)], temp=True)      # 정답 사진도 처음엔 흐림(잠깐만)
    tk_w = jieun_fit()
    tk_h = jieun_card('ch/talk', 0, 0, tk_w)[1]
    tx, ty = gx + (gw - tk_w) / 2, cy - tk_h / 2
    talk = jieun_card('ch/talk', tx, ty, tk_w)
    kx = Xf(gx + gw / 2, cy, gx + gw / 2, cy, TALK_K)      # 카드와 그 위 표시를 가운데 기준으로 함께 키움
    s.add('ch/talk', talk[0], xf=kx)
    tp = talk[2]
    s.add('ch/h1', [band('ch/h1', tp[0], '박스 정리')], xf=kx)
    s.add('ch/h2', [band('ch/h2', tp[1], '휴지 안 사 와도 돼')], xf=kx)
    s.add('ch/hd', [date_band('ch/hd', tp)], xf=kx)
    s.add('ch/tag', clue_tag('ch/tag', tx, ty), xf=kx)
    s.add('ch/pring', [ring_box('ch/pring', spots[wi], pad=4, radius=12, w=3.0)])
    px_, py_, pw_, ph_ = spots[wi]
    ans, _ = chip('ch/ans', px_ + pw_ - 44, py_ - 17, ANSWER, 'fill', pt=13, h=34, padx=16)        # 정답 사진의 오른쪽 위 모서리에
    s.add('ch/ans', ans)
    s.add('ch/bridge', [caption('ch/bridge', [[('이 중간 단서를 ', INK), ('Weave는 어떻게 찾아낼까요?', PURPLE)]], 640, 600, size=26)])
    s.on('ch/sp', 'rise', 150, 500, dy=14)
    s.on('ch/l1', 'wipe_in', 450, 400)
    s.on('ch/gap', 'fade_in', 600, 450)
    s.on('ch/gap', 'jump', 600)
    s.on('ch/l2', 'wipe_in', 900, 400)
    s.on(['ch/gal', 'ch/dim'], 'fade_in', 1050, 450)
    s.on('ch/dimb', 'fade_in', 1050, 450)
    s.on('ch/dimb', 'jump', 1050)
    s.click()   # 물음표 자리에 중간 단서 → 실이 이어짐 → 그날 사진과 이름
    # 11-10 5차: 카톡을 소리 내어 읽는 박자에 맞춤(근거 두 군데가 읽는 차례로) → 날짜 → 실 → 그날 사진과 이름 → 끝으로 물음
    s.on('ch/gap', 'fade_out', 100, 250)
    s.on('ch/t1', 'wipe_in', 150, 300)
    s.on('ch/talk', 'zoom_in', 300, 450, **{'from': 0.9})
    s.on('ch/tag', 'zoom_in', 650, 300, **{'from': 0.6})
    # 11-11 7차: 때를 손으로 적지 않고 cue()가 낭독에서 그 말을 하는 때를 찾음(CUES). 기본값은 6차에 잰 값
    t1 = max(cue('chain.h1', 2200), 950)
    t2 = max(cue('chain.h2', 5000), t1 + 500)
    td = max(cue('chain.hd', 9500), t2 + 600)
    s.on('ch/h1', 'wipe_in', t1, 300)
    s.on('ch/h2', 'wipe_in', t2, 400)
    s.on('ch/hd', 'wipe_in', td, 350)
    s.on('ch/t2', 'wipe_in', td + 500, 300)
    s.on('ch/dimb', 'fade_out', td + 750, 300)
    s.on('ch/pring', 'zoom_in', td + 815, 400, **{'from': 1.12})
    s.on('ch/ans', 'zoom_in', td + 1175, 350, **{'from': 0.8})
    s.on('ch/bridge', 'rise', max(cue('chain.bridge', 12275), td + 1700), 500, dy=14)
    return s


# ------------------------------------------------------------------ 5. 00 데이터 색인
IDX_Y, IDX_H = 248, 300
IDX_ORIG = '박스 정리 다 했어! 이따 올 때 휴지 안 사 와도 돼'
IDX_VEC = '[0.86, −0.08, 0.33, 0.46, 0.60, 0.83, 0.90, …]'
IDX_META = '{ date: "2026-03-15", app: "kakaotalk", from: "지은", … }'      # 11-10: 보낸 사람(from)도


def s_idx():
    s = Slide('idx', trans=('morph', 1000), cur='00',
              notes=NOTES['idx'])
    s.add('idx/cap', [caption('idx/cap', [[('기록이 쌓이는 대로, ', INK), ('미리 색인', PURPLE), ('해 둡니다', INK)]], 640, 92, size=25)])
    # 11-10: 카톡 카드와 색인 카드 모두 폭을 글에 맞추고(오른쪽 여백), 둘을 한 묶음으로 가운데에. 뒤에 겹쳐 보이던 카드 두 장은 뺌
    lab_w = 124
    tk_w = jieun_fit()
    w = round(30 + lab_w + max(tw(IDX_ORIG, 14), tw(IDX_VEC, 15.5, 'm'), tw(IDX_META, 15.5, 'm')) + 34)
    gap = 80
    tkw = tk_w * TALK_K                 # 카톡 카드는 앞 장과 같은 배율로(모핑으로 이어짐)
    x0 = 640 - (tkw + gap + w) / 2
    x, y, h = x0 + tkw + gap, IDX_Y, IDX_H
    cy = y + h / 2
    talk = chain_talk(x0 + (tkw - tk_w) / 2, cy - chain_talk(0, 0, tk_w)[1] / 2, tk_w)
    s.add('ch/talk', talk[0], xf=Xf(x0 + tkw / 2, cy, x0 + tkw / 2, cy, TALK_K))
    s.add('idx/arr', thread('idx/arr', scurve((x0 + tkw + 3, cy), (x - 4, cy)), w=2.6))
    rows_y = [y + 84, y + 158, y + 232]
    s.add('idx/card', [R('idx/card/bg', x, y, w, h, prst='roundRect', radius=22, fill='FFFFFF', line=RING, line_w=2.2, glow=(10, RING, 22),
                         shadow=SHADOW_LIFT),
                       P('idx/card/ic', ICON['spool'], x + 26, y + 22, 30, 30),
                       T('idx/card/t', x + 66, y + 22, 300, 30, 'Hybrid Index', size=17, color=PURPLE, weight='b', anchor='ctr'),
                       R('idx/card/s1', x + 26, rows_y[1] - 18, w - 52, 1, fill='EEE9F8', line=None),
                       R('idx/card/s2', x + 26, rows_y[2] - 18, w - 52, 1, fill='EEE9F8', line=None)])
    vx = x + 30 + lab_w
    s.add('idx/l0', [T('idx/l0', x + 30, rows_y[0], lab_w, 34, '원문', size=13.5, color=SUB, weight='b', anchor='ctr')])
    s.add('idx/r0', [T('idx/r0', vx, rows_y[0], w - 170, 34, IDX_ORIG, size=14, color=BODY, anchor='ctr')])
    s.add('idx/l1', [T('idx/l1', x + 30, rows_y[1], lab_w, 34, '의미 벡터', size=13.5, color=PURPLE, weight='b', anchor='ctr')])
    s.add('idx/r1', [T('idx/r1', vx, rows_y[1], w - 170, 34, IDX_VEC, size=15.5, color=PURPLE, weight='m', anchor='ctr')])
    s.add('idx/l2', [T('idx/l2', x + 30, rows_y[2], lab_w, 34, '메타데이터', size=13.5, color=PURPLE, weight='b', anchor='ctr')])
    s.add('idx/r2', [T('idx/r2', vx, rows_y[2], w - 170, 34, IDX_META, size=15.5, color=PURPLE, weight='m', anchor='ctr')])   # 11-11 8차: 의미 벡터처럼 보라
    s.on('idx/card', 'rise', 250, 550, dy=14)
    s.on('idx/arr', 'wipe_in', 500, 450)
    s.on(['idx/l0', 'idx/r0'], 'fade_in', 750, 400)
    s.click()   # 1: 의미 벡터
    s.on('idx/l1', 'fade_in', 150, 300)
    s.on('idx/r1', 'type', 250, 1, ms=24, n=len(IDX_VEC))
    s.click()   # 2: 메타데이터(11-10 5차: 설명이 길어져 줄마다 따로. 언제, 어느 앱, 누가를 말하는 빠르기로 찍힘)
    s.on('idx/l2', 'fade_in', 0, 300)
    s.on('idx/r2', 'type', 120, 1, ms=38, n=len(IDX_META))
    return s


# ------------------------------------------------------------------ 6. 01 상황 인식 · 02 질의 재작성
TR_SP = (668, 176, 548, 70)
KB = (668, 266, 548, 337)
SPOOL = (KB[0] + 102 * KB[2] / 1300, KB[1] + 82 * KB[3] / 800)
HAND_H = 128                       # 11-09: 214 → 128(자판을 가리지 않게)


def trig_parts(alpha=100):
    out = []
    x, y, w, h = TR_SP
    pill, txt, cur, tx0 = search_pill('tr/sp', x, y, w, h, QUERY, pt=17.5)
    out.append(('tr/sp', pill))
    # 11-10 5차: 그림 맨 위 흰 줄(2px)을 잘라 내고, 옅은 바탕과 구분되게 테두리를 조금 진하게 + 그림자를 깊게
    # 11-11 8차: '테두리 너무 진함' → 조금 연하게(CDC8DC 1.3 → D9D4E8 1.2). 흐려진 자판(14쪽)은 테두리도 함께 흐려짐(ui.Painter)
    out.append(('tr/kb', [P('tr/kb', str(AS / 'keyboard.png'), *KB, radius=18, crop=(0, 3 / 800, 0, 0), line='D9D4E8', line_w=1.2,
                            shadow=SHADOW_LIFT)]))
    hw = HAND_H * 773 / 960
    hx, hy = SPOOL[0] - hw * 0.388, SPOOL[1] - HAND_H * 0.015 + 8
    out.append(('tr/glow', [R('tr/glow', SPOOL[0] - 30, SPOOL[1] - 30, 60, 60, prst='ellipse', fill=None, line=PURPLE, line_w=3,
                              glow=(14, RING, 50))]))
    out.append(('tr/hand', [P('tr/hand', str(AS / 'hand.png'), hx, hy, hw, HAND_H)]))
    return out, txt, cur, tx0


def s_trig():
    s = Slide('trig', trans=('morph', 1000), cur='01', done={'00'},
              notes=NOTES['trig'])
    parts, txt, cur, tx0 = trig_parts()
    pm = dict(parts)
    s.add('tr/sp', pm['tr/sp'])
    s.add('q/text', [txt])
    s.add('tr/kb', pm['tr/kb'])
    s.add('tr/glow', pm['tr/glow'])
    s.add('tr/hand', pm['tr/hand'])
    x, y, w, h = TR_SP
    s.add('tr/qhl', [hl_band('tr/qhl', tx0, y + (h - 17.5 * 4 / 3 * 1.4) / 2 + 3, QUERY, QUERY, 17.5, kind='low', alpha=34)])
    # 11-10 4차: 왼쪽 끝에 붙어 있던 글을 왼쪽 칸의 가운데로(가운데 맞춤), '실타래 버튼'과 'Weave'를 보라로
    s.add('tr/cap', [caption('tr/cap', [[('실타래 버튼', PURPLE), ('을 누르면', INK)], [('Weave', PURPLE), ('가 실행됩니다', INK)]],
                             TR_SP[0] / 2 + 6, 344, size=30)])
    # 11-10 5차: 클릭 없이 장이 열리면 이어서(01은 짧게 지나가는 단계). 글은 손이 들어와 누를 때 함께
    # 11-11 8차: 말이 길어져 말에 맞춤(CUES). 손은 '누르면'을 말할 때 버튼을 누르고, 질의 형광펜은 '사용자가 입력한 질의를'을 말할 때
    t = max(cue('trig.press', 1210, ahead=0.05) - 760, 450)
    s.on('tr/hand', 'fly', t, 700, dx=170, dy=230, bend=0.1)
    s.on('tr/cap', 'rise', t + 200, 550, dy=16)
    s.on('tr/hand', 'pulse', t + 760, 140, scale=0.93)
    s.on('tr/glow', 'zoom_in', t + 860, 300, **{'from': 0.6})
    s.on('tr/qhl', 'wipe_in', max(cue('trig.take', t + 1150), t + 1150), 600)
    return s


QR = (52, 246, 576, 288)          # 11-10 4차: 질의 글 위아래 빈 곳을 절반으로(340 → 288). 글과 판 묶음은 오른쪽 검색창·자판과 세로 가운데를 맞춤


def qr_full():
    """02 장의 Query Rewriting 판(크게)."""
    x, y, w, h = QR
    out = [('sp/card', [R('sp/card/bg', x, y, w, h, prst='roundRect', radius=22, fill='FFFFFF', line=RING, line_w=2.2, glow=(10, RING, 22),
                          shadow=SHADOW_LIFT),
                        P('sp/card/ic', ICON['spool'], x + 24, y + 20, 30, 30),
                        T('sp/card/t', x + 62, y + 20, 300, 30, 'Query Rewriting', size=17, color=PURPLE, weight='b', anchor='ctr')])]
    return out


def s_split():
    s = Slide('split', trans=('morph', 1000), cur='02', done={'00', '01'},
              notes=NOTES['split'])
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
    tqx, tqy = qx + 26, qy + 74
    s.add('q/text', [T('q/text', tqx, tqy, qw - 40, S * 1.4, QUERY, size=qpt, color=INK)])
    qpos = (tqx, tqy, QUERY, qpt, 'r')
    # 11-11 8차: '지은이네 집들이' / '때 마셨던 와인' → '지은이네 집들이 때' / '마셨던 와인'
    b1 = band('sp/b1', qpos, '지은이네 집들이 때', alpha=36)
    b2 = hl_band('sp/b2', tqx, tqy, QUERY, '마셨던 와인', qpt, color=BLUE_HL, alpha=40)
    s.add('sp/b1', [b1])
    s.add('sp/b2', [b2])
    r1y, r2y = qy + 130, qy + 206
    s.add('sp/r1', [R('sp/r1/bg', qx + 22, r1y, qw - 44, 58, prst='roundRect', radius=14, fill=LAV, line=None)] +
          numdot('sp/r1/n', qx + 50, r1y + 29, 1, r=14, pt=11) +
          [T('sp/r1/t', qx + 76, r1y, qw - 110, 58, '지은이네 집들이는 언제였지?', size=17, color=INK, weight='m', anchor='ctr')])
    blank, bw_ = chip('sp/r2/b', qx + 76, r2y + 15, '그날', 'dash', pt=13, h=30, padx=12)
    s.add('sp/r2', [R('sp/r2/bg', qx + 22, r2y, qw - 44, 58, prst='roundRect', radius=14, fill=BLUE_BG, line=None)] +
          numdot('sp/r2/n', qx + 50, r2y + 29, 2, r=14, pt=11, fill=BLUE) + blank +
          [T('sp/r2/t', qx + 76 + bw_ + 6, r2y, qw - 110 - bw_, 58, '마셨던 와인은?', size=17, color=INK, weight='m', anchor='ctr')])
    s.add('sp/cap', [caption('sp/cap', [[('질의를 ', INK), ('의미 단위로 나눠', PURPLE), (' 다시 씁니다', INK)]], qx + qw / 2, qy - 58, size=24)])
    s.on('sp/cap', 'rise', 200, 500, dy=14)
    s.click()
    s.on('sp/b1', 'wipe_in', 0, 450)
    s.on('sp/r1', 'rise', 500, 450, dy=14)
    tq = max(cue('split.q2', 2200), 1100)        # 둘째 질의는 '와인을 마셨던 날은'을 말할 때(CUES)
    s.on('sp/b2', 'wipe_in', tq, 450)
    s.on('sp/r2', 'rise', tq + 400, 450, dy=14)
    return s


# ------------------------------------------------------------------ 7. 03 연쇄 탐색: Hop 1, Hop 2
QC = (40, 229, 420, 188)           # Hop 1 장 왼쪽의 작은 Query Rewriting 판(아래 Query 1 카드와 한 묶음으로 세로 가운데)
H1 = (40, 445, 420, 118)           # Hop 1 장의 Query 1 카드
QC2 = (40, 156, 420, 188)          # Hop 2 장: Query Rewriting 판은 Query 1과 함께 위로 올라감(11-10 5차: 없애지 않고 남김)
Q1B = (40, 366, 420, 118)          # Hop 2 장: 끝난 Query 1
Q2B = (40, 520, 420, 118)          # Hop 2 장: Query 2(아래에 새로 뜸)
TOK = '3/15 (일)'                   # ②의 빈칸(그날)에 들어가는 날짜


def qr_small(box=QC):
    """Hop 1·Hop 2 장 왼쪽 위의 작은 Query Rewriting 판(②는 빈칸). 11-10 4차: '답' 줄 자리를 빼고 줄 사이를 좁힘."""
    x, y, w, h = box
    out = [R('sp/card/bg', x, y, w, h, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.4, shadow=SHADOW_CARD),
           P('sp/card/ic', ICON['spool'], x + 18, y + 14, 24, 24),
           T('sp/card/t', x + 48, y + 14, 220, 24, 'Query Rewriting', size=13.5, color=PURPLE, weight='b', anchor='ctr')]
    q_ = [T('q/text', x + 20, y + 51, w - 30, 22, QUERY, size=12.5, color=INK)]
    r1y, r2y = y + 86, y + 134
    r1 = [R('sp/r1/bg', x + 14, r1y, w - 28, 40, prst='roundRect', radius=12, fill=LAV, line=None)] + \
        numdot('sp/r1/n', x + 36, r1y + 20, 1, r=11, pt=9) + \
        [T('sp/r1/t', x + 56, r1y, w - 80, 40, '지은이네 집들이는 언제였지?', size=12.5, color=INK, weight='m', anchor='ctr')]
    blank, bw_ = chip('sp/r2/b', x + 56, r2y + 8, '그날', 'dash', pt=10.5, h=24, padx=9)
    r2 = [R('sp/r2/bg', x + 14, r2y, w - 28, 40, prst='roundRect', radius=12, fill=BLUE_BG, line=None)] + \
        numdot('sp/r2/n', x + 36, r2y + 20, 2, r=11, pt=9, fill=BLUE) + blank + \
        [T('sp/r2/t', x + 56 + bw_ + 5, r2y, w - 90 - bw_, 40, '마셨던 와인은?', size=12.5, color=INK, weight='m', anchor='ctr')]
    return out, q_, r1, r2, (r1y, r2y)


def query_card(key, box, n, runs, active=True, done=False):
    """하위 질의 카드: 'Query n' + Hop n 칩 + 질의 글. runs = [(글, 'q' | 'blank')] — 'blank'는 점선 빈칸(나중에 날짜 칩이 그 위에 앉음).
    11-10 4차: 카드 이름을 Reasoning Embedding → Query 1, Query 2로. 돌려줌: (원시, 자리) — 자리['blank'] = 빈칸의 (x, y, w, h)."""
    x, y, w, h = box
    ln = (RING, 2.2) if active else (LINE2, 1.4)
    out = [R(key + '/bg', x, y, w, h, prst='roundRect', radius=20, fill='FFFFFF', line=ln[0], line_w=ln[1],
             glow=(10, RING, 22) if active else None, shadow=SHADOW_CARD),
           T(key + '/t', x + 20, y + 14, 200, 24, 'Query %d' % n, size=13.5, color=PURPLE if active else SUB, weight='b', anchor='ctr')]
    hop = 'Hop %d' % n
    hc, _ = chip(key + '/hop', x + w - 20 - (tw(hop, 10, 'b') + 22), y + 14, hop, 'fill' if active else 'outline', pt=10, h=24, padx=11)
    out += hc
    out.append(R(key + '/f', x + 16, y + 52, w - 32, 48, prst='roundRect', radius=14, fill='F7F5FC', line=LINE, line_w=1.0))
    tx = x + 32
    pos = {'q': (tx, y + 76)}
    for i, (t, st) in enumerate(runs):
        if st == 'blank':
            bw = tw(TOK, 11, 'b') + 20          # 빈칸은 들어올 날짜 칩과 같은 폭(채워져도 뒤 글자가 밀리지 않게)
            out += [R(key + '/blank/bg', tx, y + 63, bw, 26, prst='roundRect', fill=LAV2, line=PURPLE2, line_w=1.0, dash='dash'),
                    T(key + '/blank/t', tx, y + 63, bw, 26, t, size=11, color=PURPLE, weight='b', align='c', anchor='ctr')]
            pos['blank'] = (tx, y + 63, bw, 26)
            tx += bw + 6
        else:
            out.append(T(key + '/q%d' % i, tx, y + 52, w - (tx - x) - 20, 48, t, size=13.5, color=INK if (active or done) else MUTE,
                         weight='m', anchor='ctr'))
            pos['qw'] = tw(t, 13.5, 'm')
            tx += pos['qw']
    if done:
        out += check_icon(key + '/ok', x + w - 31, y + 76, s=14, color=PURPLE, w=2.4)
    return out, pos


H1_SPACE = (490, 134, 750, 512)
H1_STAR = (770, 404)
H1_NOTE = '* 임베딩 공간에서는 질문과 가까이 위치할수록 먼저 검색됨'      # 일반 임베딩과 Reasoning Embedding 양쪽에 다 맞는 말로(9쪽 각주와 같은 말씨)
H1_Q = '지은이네 집들이는 언제였지?'
CAP_Y = 84                         # 위 띠 아래 한 줄 설명(Hop 1, Hop 2)
H1_DSHIFT = [(-14, 9), (12, -10), (-9, -13), (15, 7)]      # 일반 임베딩일 때 배경 점 네 무리가 놓이는 자리(Reasoning Embedding 자리 기준 px)


def s_hop1():
    """장이 열리면 ①에서 화살표가 내려가 Query 1 카드가 뜨고, 곧바로 임베딩 공간이 펼쳐진다.
    처음은 일반 임베딩(주황): 질문(주황 별) 곁에 뜻이 비슷한 일정·메모, 보라 테두리의 '단서'(지은 카톡)는 멀리 →
    (클릭) Reasoning Embedding(보라)으로 바꾸면 공간 전체가 조금씩 다시 놓이고(배경 점과 다른 기록도 함께), 단서가 옛 자리에 흐린 흔적과 실선을
    남기며 질문 곁으로 → 이어서(클릭 없이) 단서 바로 곁에 카톡 내용이 펼쳐지고 근거와 받은 날짜에 형광펜.
    11-10 5차: 클릭 2 → 1번. 옮겨 온 뒤 테두리를 한 번 더 그리지 않고, 옛 자리 흔적에는 보라 테두리와 '단서' 표가 없다.
    카톡 내용 카드는 실로 잇지 않고 단서 칩에 겹칠 듯 붙여 둔다. 토글의 주황은 바꾼 뒤 남지 않는다."""
    s = Slide('hop1', trans=('morph', 1100), cur='03', done={'00', '01', '02'}, notes=NOTES['hop1'])
    card_, q_, r1, r2, (r1y, r2y) = qr_small()
    for p_ in card_:
        s.add(p_[1], [p_])
    s.add('q/text', q_)
    s.add('sp/r1', r1)
    s.add('sp/r2', r2)
    # ① → Query 1: 판 왼쪽 바깥으로 도는 화살표(장이 열리면 가장 먼저 그려짐)
    s.add('h1/c', thread('h1/c', [(QC[0] + 14, r1y + 20), (QC[0] - 14, r1y + 20), (H1[0] - 14, H1[1] + 30), (H1[0] - 2, H1[1] + 30)],
                         w=2.2, tail='triangle'))
    q1, qp = query_card('h1/q1', H1, 1, [(H1_Q, 'q')])
    s.add('h1/q1', q1)
    # 제목: 일반 임베딩(잠깐만, temp) → Reasoning Embedding
    s.add('h1/cap0', [caption('h1/cap0', [[('일반 임베딩', ORANGE), ('은 뜻이 비슷한 기록을 가깝게 둡니다', INK)]], 640, CAP_Y, size=22)], temp=True)
    s.add('h1/cap', [caption('h1/cap', [[('Reasoning Embedding', PURPLE), ('은 단서가 될 기록도 가깝게 둡니다', INK)]], 640, CAP_Y, size=22)])
    sx, sy, sw, sh = H1_SPACE
    s.add('h1/space', [R('h1/space/bg', sx, sy, sw, sh, prst='roundRect', radius=22, fill='FFFFFF', alpha=88, line=LINE2, line_w=1.2)])
    s.add('h1/note', [space_note('h1/note', H1_SPACE, H1_NOTE)])
    tx0, ty0 = sx + 20, sy + 16
    tpt = 12
    wa, wb = tw('일반 임베딩', tpt, 'b') + 30, tw('Reasoning Embedding', tpt, 'b') + 30
    s.add('h1/togbg', [R('h1/tog/bg', tx0, ty0, wa + wb + 8, 38, prst='roundRect', fill='F1EEF8', line=None)])
    # 일반 임베딩 쪽이 켜진 토글은 잠깐만(temp): 바꾼 뒤에는 주황이 남지 않는다
    s.add('h1/togA', [R('h1/togA/k', tx0 + 4, ty0 + 4, wa, 30, prst='roundRect', fill=ORANGE, line=None, glow=(8, ORANGE2, 30)),
                      T('h1/togA/a', tx0 + 4, ty0 + 4, wa, 30, '일반 임베딩', size=tpt, color='FFFFFF', weight='b', align='c', anchor='ctr'),
                      T('h1/togA/b', tx0 + 4 + wa, ty0 + 4, wb, 30, 'Reasoning Embedding', size=tpt, color=MUTE, weight='b', align='c',
                        anchor='ctr')], temp=True)
    s.add('h1/togB', [R('h1/togB/k', tx0 + 4 + wa, ty0 + 4, wb, 30, prst='roundRect', fill=PURPLE, line=None, glow=(8, RING, 30)),
                      T('h1/togB/a', tx0 + 4, ty0 + 4, wa, 30, '일반 임베딩', size=tpt, color=MUTE, weight='b', align='c', anchor='ctr'),
                      T('h1/togB/b', tx0 + 4 + wa, ty0 + 4, wb, 30, 'Reasoning Embedding', size=tpt, color='FFFFFF', weight='b', align='c',
                        anchor='ctr')])
    # 기록 칩의 자리: 마지막 자리(Reasoning Embedding)에 놓고, 처음 나타날 때 처음 자리(일반 임베딩)로 옮겨 둠
    SX, SY = H1_STAR
    d1i, d1f = (SX - 150, SY - 96), (sx + 20, sy + 72)
    d2i, d2f = (SX + 12, SY + 34), (sx + 46, sy + 422)
    ki, kf = (SX + 240, SY + 136), (SX + 6, SY + 30)
    d1, d1w, d1h = mini_chip('h1/d1', d1f[0], d1f[1], 'cal', '성빈이 신혼집들이', '2025. 10. 18 (토)', pt=11.5)
    d2, d2w, d2h = mini_chip('h1/d2', d2f[0], d2f[1], 'note', '지은이네 주소', '경기도 수원시…', pt=11.5)
    kk, kw_, kh_ = mini_chip('h1/k', kf[0], kf[1], 'talk', '지은', '박스 정리 다 했어!…', pt=11.5, ring=True)
    gk, _, _ = mini_chip('h1/ghost', ki[0], ki[1], 'talk', '지은', '박스 정리 다 했어!…', pt=11.5)       # 옛 자리의 흔적: 테두리와 '단서' 표 없이 흐리게만
    # 카톡 내용 카드: 단서 칩의 오른쪽 위 모서리에 겹칠 듯 붙여(자세히 보기), 실로 잇지 않음
    cw_ = jieun_fit(pt=12, title_pt=13.5)
    ch_ = jieun_card('h1/card', 0, 0, cw_, pt=12, title_pt=13.5)[1]
    cx_, cy_ = kf[0] + kw_ - 18, kf[1] + 10 - ch_

    def off(a_, b_):
        return (a_[0] - b_[0], a_[1] - b_[1])
    # 멀리 있는 기록: (키, 종류, 이름, 마지막 자리, 처음 자리) — 공간이 다시 놓일 때 조금씩 함께 움직인다.
    # 소믈리에 추천은 처음엔 오른쪽 가운데(비어 보이던 자리), 카톡 내용이 펼쳐질 자리에서 위로 비켜 난다
    far = []
    for k, kind, label, pf, pi in (('h1/f1', 'mail', '관리비 고지서', (sx + 572, sy + 42), (sx + 556, sy + 56)),
                                   ('h1/f2', 'talk', '택배', (sx + 660, sy + 344), (sx + 638, sy + 334)),
                                   ('h1/f3', 'cal', '팀 회식', (sx + 210, sy + 462), (sx + 226, sy + 450)),
                                   ('h1/f4', 'note', '소믈리에 추천', (sx + 598, sy + 118), (sx + 576, sy + 196))):
        prims, w_, h_ = mini_chip(k, pf[0], pf[1], kind, label, pt=11.5, alpha=60)
        far.append((k, prims, (pf[0], pf[1], w_, h_), (pi[0], pi[1], w_, h_), off(pi, pf)))
    # 배경 점: 네 무리가 서로 다른 쪽으로 조금씩 움직인다. 가까운 원과 기록 칩(처음·마지막 자리)을 피하고,
    # 카톡 내용 카드의 테두리에 걸치지 않게 찍는다(카드 안쪽은 괜찮음: 처음엔 그 자리를 채우고, 카드가 뜨면 가려짐)
    keep_out = [(d1f[0], d1f[1], d1w, d1h), (d2f[0], d2f[1], d2w, d2h), (ki[0], ki[1], kw_, kh_), (tx0, ty0, wa + wb + 8, 38)]
    keep_out += [b_ for _, _, b_, _, _ in far] + [b_ for _, _, _, b_, _ in far]
    rnd = random.Random(29)
    groups = [[] for _ in H1_DSHIFT]
    for i in range(38):
        g = i % len(H1_DSHIFT)
        for _ in range(400):
            x_, y_ = sx + 28 + rnd.random() * (sw - 56), sy + 34 + rnd.random() * (sh - 64)
            near_card_edge = (cx_ - 12 < x_ < cx_ + cw_ + 12 and cy_ - 12 < y_ < cy_ + ch_ + 12) and not (
                cx_ + 12 < x_ < cx_ + cw_ - 12 and cy_ + 12 < y_ < cy_ + ch_ - 12)
            if (x_ - SX) ** 2 / 178 ** 2 + (y_ - SY) ** 2 / 140 ** 2 > 1 and not near_card_edge and not any(
                    bx - 26 < x_ < bx + bw + 26 and by - 24 < y_ < by + bh + 24 for bx, by, bw, bh in keep_out) and all(
                    (x_ - px_) ** 2 + (y_ - py_) ** 2 > 30 ** 2 for grp in groups for px_, py_ in grp):
                break
        groups[g].append((x_, y_))
    n = 0
    for g, pts in enumerate(groups):
        prims = []
        for x_, y_ in pts:
            r_ = 3.2 + rnd.random() * 2.4
            prims.append(R('h1/dot%d' % n, x_ - r_, y_ - r_, 2 * r_, 2 * r_, prst='ellipse', fill='CBC0EC', alpha=80, line=None))
            n += 1
        s.add('h1/dots%d' % g, prims, start=H1_DSHIFT[g])
    for k, prims, _, _, st in far:
        s.add(k, prims, start=st)
    near = (SX - 152, SY - 117, 304, 234)
    s.add('h1/near0', [R('h1/near0', *near, prst='ellipse', fill=None, line=ORANGE2, line_w=1.8, dash='dash')], temp=True)
    s.add('h1/near', [R('h1/near', *near, prst='ellipse', fill=None, line=PURPLE2, line_w=1.8, dash='dash')])
    s.add('h1/d1', d1, start=off(d1i, d1f))
    s.add('h1/d2', d2, start=off(d2i, d2f))
    # '단서'가 옮겨 온 길: 옛 자리에 흐린 흔적을 남기고 실선으로 잇는다
    ci, cf = (ki[0] + 3, ki[1] + kh_ / 2 + 4), (kf[0] + kw_ - 10, kf[1] + kh_ - 3)      # 흔적의 왼쪽 끝 → 옮겨 온 칩의 오른쪽 아래(칩 아래로 숨음)
    s.add('h1/trail', [C('h1/trail', [ci, (ci[0] - 34, ci[1] - 2), (cf[0] + 30, cf[1] + 30), cf], w=2.2, color='B9A8F0')])
    s.add('h1/ghost', gk, alpha=34)
    s.add('h1/k', kk + clue_tag('h1/k/tag', kf[0], kf[1]), start=off(ki, kf))     # 보라 테두리와 '단서' 표는 이 칩에만(옮겨 가는 게 보임)
    s.add('h1/star0', star('h1/star0', SX, SY, color=ORANGE), temp=True)          # 일반 임베딩의 질문(주황 별, 잠깐만)
    s.add('h1/star', star('h1/star', SX, SY))
    s.add('h1/starl', chip('h1/starl', SX + 20, SY - 44, 'Query 1', 'white', pt=10.5, h=24, padx=9, weight='b')[0])
    talk = jieun_card('h1/card', cx_, cy_, cw_, pt=12, title_pt=13.5)
    s.add('h1/card', talk[0])
    tp = talk[2]
    s.add('h1/h1', [band('h1/h1', tp[0], '박스 정리')])
    s.add('h1/h2', [band('h1/h2', tp[1], '휴지 안 사 와도 돼')])
    s.add('h1/hd', [date_band('h1/hd', tp)])
    # 효과 — 장이 열리면: ① → Query 1 카드 → 임베딩 공간(일반 임베딩). 뜻이 비슷한 두 기록이 질문 곁에, '단서'는 멀리
    s.on('h1/c', 'wipe_in', 150, 380, dir='down')
    s.on('h1/q1', 'rise', 480, 450, dy=12)
    t = 950
    s.on('h1/space', 'zoom_in', t, 450, **{'from': 0.96})
    s.on('h1/togbg', 'fade_in', t + 100, 350)
    s.on('h1/togA', 'fade_in', t + 100, 350)
    s.on('h1/togA', 'jump', t + 100)
    s.on('h1/cap0', 'fade_in', t + 100, 450)
    s.on('h1/cap0', 'jump', t + 100)
    for g in range(len(H1_DSHIFT)):
        s.on('h1/dots%d' % g, 'fade_in', t + 150, 400)
        s.on('h1/dots%d' % g, 'goto', t + 150)
    for i, (k, _, _, _, _) in enumerate(far):
        s.on(k, 'fade_in', t + 200 + i * 50, 350)
        s.on(k, 'goto', t + 200 + i * 50)
    s.on('h1/note', 'fade_in', t + 350, 400)
    for i, k in enumerate(('h1/d1', 'h1/d2', 'h1/k')):
        s.on(k, 'zoom_in', t + 400 + i * 90, 350, **{'from': 0.8})
        s.on(k, 'goto', t + 400 + i * 90)
    qsrc = (qp['q'][0] + qp['qw'] / 2, qp['q'][1])          # 질문 별은 Query 1의 글에서 날아와 공간에 앉음
    s.on('h1/star0', 'fade_in', t + 800, 200)
    s.on('h1/star0', 'fly', t + 800, 750, dx=qsrc[0] - SX, dy=qsrc[1] - SY, bend=0.12, show=False, fade=False)
    s.on('h1/near0', 'zoom_in', t + 1450, 400, **{'from': 0.4})
    s.on('h1/near0', 'jump', t + 1450)
    s.on('h1/starl', 'fade_in', t + 1550, 300)
    s.click()   # 1: Reasoning Embedding으로 바꿈 — 제목·토글·별·원이 보라로, 공간이 다시 놓이고 '단서'가 질문 곁으로 → 카톡 내용과 근거
    s.on('h1/cap0', 'fade_out', 0, 250)
    s.on('h1/cap', 'rise', 150, 450, dy=12)
    s.on('h1/togA', 'fade_out', 100, 300)
    s.on('h1/togB', 'fade_in', 100, 350)
    s.on(['h1/star0', 'h1/near0'], 'fade_out', 250, 300)
    s.on(['h1/star', 'h1/near'], 'fade_in', 250, 300)
    s.on('h1/k', 'pulse', 450, 150, scale=1.08)
    s.on('h1/d1', 'fly', 700, 1000, dx=d1i[0] - d1f[0], dy=d1i[1] - d1f[1], bend=0.1, show=False, fade=False)
    s.on('h1/d2', 'fly', 700, 1000, dx=d2i[0] - d2f[0], dy=d2i[1] - d2f[1], bend=-0.1, show=False, fade=False)
    s.on(['h1/d1', 'h1/d2'], 'dim', 1300, 400, to=0.4)
    for g, d_ in enumerate(H1_DSHIFT):                      # 배경 점과 멀리 있는 기록도 조금씩 자리를 옮김
        s.on('h1/dots%d' % g, 'fly', 700 + g * 70, 1100, dx=d_[0], dy=d_[1], bend=0, show=False, fade=False)
    for i, (k, _, _, _, st) in enumerate(far):
        s.on(k, 'fly', 740 + i * 80, 1050, dx=st[0], dy=st[1], bend=0.08 if i % 2 else -0.08, show=False, fade=False)
    s.on('h1/ghost', 'fade_in', 800, 300)
    s.on('h1/trail', 'wipe_in', 800, 1200, dir='right')
    s.on('h1/k', 'fly', 800, 1300, dx=ki[0] - kf[0], dy=ki[1] - kf[1], bend=0.15, show=False, fade=False)
    t = 2250    # 단서가 질문 곁에 앉으면 곧바로 카톡 내용이 그 곁에 펼쳐짐(클릭 없이) → 근거 두 곳 → 받은 날짜
    s.on('h1/card', 'zoom_in', t, 480, **{'from': 0.82})
    # 11-10 5차: 근거는 그 말을 할 즈음에(카드가 뜨고 조금 뒤 근거 두 군데, 날짜는 '다음 단서'를 말하기 앞서)
    # 11-11 7차: 근거는 '휴지 안 사 와도 돼'를 말할 때, 날짜는 '이 카톡을 받은 3월 15일'을 말할 때(CUES, cue()가 낭독에서 찾음)
    te = max(cue('hop1.ev', 6875, ahead=0.3), t + 700)
    te2 = max(cue('hop1.ev2', te + 375), te + 375)          # 11-11 8차: '박스 정리'와 '휴지 안 사 와도 돼'를 말하는 차례로
    tdt = max(cue('hop1.date', 13500), te2 + 1000)
    s.on('h1/h1', 'wipe_in', te, 350)
    s.on('h1/h2', 'wipe_in', te2, 450)
    s.on('h1/hd', 'wipe_in', tdt, 400)
    return s


H2_GAL = (500, 398, 736)           # 11-11 8차: 갤러리와 그 위 카톡을 42px 위로(갤러리 아래가 Query 2 아래와 나란히. 오른쪽 위가 비어 보였음)
H2_PH = 154                        # 갤러리 사진 높이(11-10 5차: 126 → 154, 와인 라벨이 더 잘 보이게)
H2_PHOTOS = ['babich', 'table', 'w1', 'w3', 'w2']


def s_hop2():
    """11-10 5차: Query Rewriting 판은 사라지지 않고 Query 1과 함께 위로 올라간다(모핑). 끝난 ①과 Query 1은 흐리게.
    Query 1 곁에는 그 결과(지은 카톡)가 곡선으로 이어지고, ②에서 화살표가 내려가 Query 2가 뜬다. 카톡의 날짜가 날아와 빈칸을 채움 →
    (클릭) Query 2와 갤러리가 이어지고 날짜 필터로 그날 사진만 → (클릭) 와인 사진에 테두리와 이름."""
    s = Slide('hop2', trans=('morph', 1100), cur='03', done={'00', '01', '02'}, notes=NOTES['hop2'])
    s.add('h2/cap', [caption('h2/cap', [[('찾은 날짜를 단서로,', PURPLE), (' 정확한 이름을 찾습니다', INK)]], 640, CAP_Y, size=22)])
    # Query Rewriting 판(위로 올라옴) — ①은 끝나서 흐리게, ②는 지금 차례
    card_, q_, r1, r2, (r1y, r2y) = qr_small(QC2)
    for p_ in card_:
        s.add(p_[1], [p_])
    s.add('q/text', q_)
    s.add('sp/r1', r1, alpha=56)
    s.add('sp/r2', r2)
    x1, y1, w1, h1_ = Q1B
    x2, y2, w2, h2_ = Q2B
    q1cy, q2cy = y1 + h1_ / 2, y2 + h2_ / 2
    s.add('h1/c', thread('h1/c', [(QC2[0] + 14, r1y + 20), (QC2[0] - 14, r1y + 20), (x1 - 14, y1 + 30), (x1 - 2, y1 + 30)],
                         w=2.2, tail='triangle', alpha=56))
    # Query 1(끝남, 흐리게) —— 그 결과인 지은 카톡(곡선으로 이어짐)
    cw_ = jieun_fit(pt=12, title_pt=13.5)
    th_ = jieun_card('h1/card', 0, 0, cw_, pt=12, title_pt=13.5)[1]
    gx, gy, gw = H2_GAL
    tx, ty = 546, gy - 22 - th_
    s.add('h2/l1', thread('h2/l1', scurve((x1 + w1 - 6, q1cy), (tx + 6, ty + th_ / 2)), w=2.2))
    q1, _ = query_card('h1/q1', Q1B, 1, [(H1_Q, 'q')], active=False, done=True)
    s.add('h1/q1', q1, alpha=64)
    talk = jieun_card('h1/card', tx, ty, cw_, pt=12, title_pt=13.5)
    s.add('h1/card', talk[0])
    tp = talk[2]
    s.add('h1/h1', [band('h1/h1', tp[0], '박스 정리')])
    s.add('h1/h2', [band('h1/h2', tp[1], '휴지 안 사 와도 돼')])
    s.add('h1/hd', [date_band('h1/hd', tp)])
    # ② → Query 2: ①의 화살표 바깥으로 도는 화살표, Query 2(빈칸) + 날아와 앉는 날짜
    s.add('h2/c', thread('h2/c', [(QC2[0] + 14, r2y + 20), (QC2[0] - 34, r2y + 20), (x2 - 34, y2 + 30), (x2 - 2, y2 + 30)],
                         w=2.2, tail='triangle'))
    q2, qp = query_card('h2/q2', Q2B, 2, [('그날', 'blank'), ('마셨던 와인은?', 'q')])
    s.add('h2/q2', q2)
    bx, by, bw, bh = qp['blank']
    s.add('h2/tok', [R('h2/tok/bg', bx - 1, by - 1, bw + 2, bh + 2, prst='roundRect', fill=PURPLE, line=None, shadow=SHADOW_SOFT),      # 빈칸의 점선까지 덮음
                     T('h2/tok/t', bx - 1, by - 1, bw + 2, bh + 2, TOK, size=11, color='FFFFFF', weight='b', align='c', anchor='ctr')])
    dx_, dy_, dw_, dS = tp['date']
    # Query 2 —— 갤러리(날짜 필터)
    n = len(H2_PHOTOS)
    pw = (gw - 32 - 10 * (n - 1)) / n
    ph = H2_PH
    gh = 46 + ph + 26 + 14
    s.add('h2/l2', thread('h2/l2', scurve((x2 + w2 - 6, q2cy), (gx + 6, gy + gh / 2)), w=2.2))
    s.add('h2/gal', [R('h2/gal/bg', gx, gy, gw, gh, prst='roundRect', radius=20, fill='FFFFFF', line=LINE, line_w=1.0, shadow=SHADOW_CARD),
                     P('h2/gal/ic', ICON['gallery'], gx + 16, gy + 12, 26, 26),
                     T('h2/gal/t', gx + 50, gy + 12, 120, 26, '갤러리', size=13, color=INK, weight='b', anchor='ctr')])
    flabel = 'date: "2026-03-15"'
    filt, fw_ = chip('h2/filter', gx + gw - 16 - (tw(flabel, 10.5, 'b') + 24), gy + 11, flabel, 'dash', pt=10.5, h=28, padx=12)
    s.add('h2/filter', filt)
    spots, photos, dates, dtxt = [], [], [], []
    DPT = 10.5
    for i, k in enumerate(H2_PHOTOS):
        img, d, fo = PH[k]
        px_, py_ = gx + 16 + i * (pw + 10), gy + 50
        spots.append((px_, py_, pw, ph))
        photos.append(P('h2/p%d' % i, img, px_, py_, pw, ph, radius=10, crop=crop_fit(img, pw, ph, fo)))
        label = d + (' 20:14' if k == 'babich' else (' 19:52' if k == 'table' else ''))
        dtxt.append(label)
        dates.append(T('h2/d%d' % i, px_, py_ + ph + 5, pw, 18, label, size=DPT, color=SUB, align='c'))
    s.add('h2/photos', photos + dates)
    keep = [i for i, k in enumerate(H2_PHOTOS) if PH[k][1] == '2026. 3. 15']
    s.add('h2/dim', [dim_over('h2/dim%d' % i, spots[i], radius=10, alpha=70) for i in range(n) if i not in keep])
    xm = []
    for i in range(n):
        if i not in keep:
            xm += xmark('h2/x%d' % i, spots[i][0] + pw / 2, spots[i][1] + ph / 2, s=26, w=4.2)
    s.add('h2/x', xm)
    s.add('h2/dhl', [hl_band('h2/dhl%d' % i, spots[i][0] + pw / 2 - tw(dtxt[i], DPT) / 2, spots[i][1] + ph + 5, dtxt[i], dtxt[i][:11], DPT,
                             alpha=40) for i in keep])
    t_i = H2_PHOTOS.index('table')
    w_i = H2_PHOTOS.index('babich')
    s.add('h2/dimt', [dim_over('h2/dimt', spots[t_i], radius=10, alpha=70)])
    s.add('h2/pring', [ring_box('h2/pring', spots[w_i], pad=4, radius=12, w=3.0)])
    ans, _ = chip('h2/ans', spots[w_i][0] + pw - 40, spots[w_i][1] - 17, ANSWER, 'fill', pt=13, h=34, padx=16)     # 끊어진 고리 장과 같은 자리(사진 오른쪽 위)
    s.add('h2/ans', ans)
    s.on('h2/cap', 'rise', 150, 450, dy=14)
    s.on('h2/l1', 'wipe_in', 250, 320)
    s.on('h2/c', 'wipe_in', 650, 420, dir='down')
    s.on('h2/q2', 'rise', 950, 450, dy=12)
    s.on('h2/tok', 'fly', 1550, 900, dx=(dx_ + dw_ / 2) - (bx + bw / 2), dy=(dy_ + dS / 2) - (by + bh / 2), bend=0.2)
    s.click()   # 1: 날짜 필터 — 그날 사진만
    s.on('h2/l2', 'wipe_in', 0, 300)
    s.on(['h2/gal', 'h2/photos'], 'rise', 200, 500, dy=14)
    s.on('h2/filter', 'pop', 650, 420, **{'from': 0.6, 'over': 1.08})
    s.on('h2/dim', 'fade_in', 1050, 400)
    s.on('h2/x', 'pop', 1150, 380, **{'from': 0.3, 'over': 1.15})
    s.on('h2/dhl', 'wipe_in', 1350, 350)
    s.click()   # 2: 그날 사진 가운데 와인 사진 → 이름
    s.on('h2/dimt', 'fade_in', 0, 400)
    s.on('h2/pring', 'zoom_in', 250, 420, **{'from': 1.12})
    s.on('h2/ans', 'zoom_in', 700, 380, **{'from': 0.7})
    return s


# ------------------------------------------------------------------ 8. 04 결과 제공
DL_SP = (140, 166, 560, 66)        # 11-10: 뱃지가 빠져 묶음(검색창 + 시트 + 글)을 가운데로
SHEET = (140, 252, 560, 340)


def s_deliver():
    s = Slide('deliver', trans=('morph', 1000), cur='04', done={'00', '01', '02', '03'},
              notes=NOTES['deliver'])
    x, y, w, h = DL_SP
    QPT = 16.5
    pill, txt, cur, tx0 = search_pill('dl/sp', x, y, w, h, QUERY, pt=QPT)
    S = QPT * 4 / 3

    def band_(name, text, color, alpha):           # 검색창 글자 위 띠(선택 표시, 바뀐 글 훑기)
        return [R(name, tx0 - 3, y + h / 2 - S * 0.62, tw(text, QPT) + 6, S * 1.24, prst='roundRect', radius=5, fill=color, alpha=alpha, line=None)]
    s.add('dl/sp', pill)
    s.add('dl/sel', band_('dl/sel', QUERY, 'B9A2FF', 55), temp=True)
    s.add('dl/q', [txt], temp=True)
    s.add('dl/sweep', band_('dl/sweep', ANSWER, HL, 36), temp=True)
    s.add('dl/q2', [T('dl/q2', txt[2], txt[3], txt[4], txt[5], ANSWER, size=QPT, color=INK, anchor='ctr')])
    s.add('dl/cur', [R('dl/cur', tx0 + tw(ANSWER, QPT) + 3, y + h / 2 - 11, 2.4, 22, fill=PURPLE, line=None)])
    sx, sy, sw, sh = SHEET
    by_ = sy + 128
    rows = [('talk', '지은', '‘휴지 안 사 와도 돼’  3월 15일'), ('gallery', '와인 사진', '3월 15일 20:14')]
    bt_w = tw('입력하기', 14, 'b')
    bt_cx = sx + sw / 2
    out = [R('dl/sheet/bg', sx, sy, sw, sh, prst='roundRect', radius=24, fill='FFFFFF', line=LINE2, line_w=1.4, shadow=SHADOW_LIFT),
           R('dl/sheet/card', sx + 18, sy + 18, sw - 36, 96, prst='roundRect', radius=16, fill=LAV, line=None)] + \
          spark_icon('dl/sheet/star', sx + 32, sy + 31.5, size=19, color=PURPLE) + \
          [T('dl/sheet/lab', sx + 56, sy + 30, 300, 22, '자동 완성 추천', size=12, color=PURPLE, weight='b'),
           T('dl/sheet/ans', sx + 36, sy + 56, sw - 72, 44, ANSWER, size=24, color=INK, weight='b', anchor='ctr'),
           R('dl/sheet/btn', sx + 18, by_, sw - 36, 50, prst='roundRect', radius=14, fill=PURPLE, line=None, shadow=(14, 4, '6B4EFF', 24))] + \
          check_icon('dl/sheet/chk', bt_cx - bt_w / 2 - 11, by_ + 25, s=11.5, color='FFFFFF', w=2.2) + \
          [T('dl/sheet/btnt', sx + 34, by_, sw - 52, 50, '입력하기', size=14, color='FFFFFF', weight='b', align='c', anchor='ctr'),
           T('dl/sheet/mem', sx + 26, by_ + 66, 200, 22, '연결된 기억', size=12, color=SUB, weight='b')]
    for i, (ic, a, b) in enumerate(rows):
        ry = by_ + 96 + i * 40
        out += [P('dl/sheet/ic%d' % i, ICON[ic], sx + 26, ry + 3, 26, 26),
                T('dl/sheet/r%d' % i, sx + 62, ry, sw - 90, 32, [[(a + '  ', {'weight': 'b', 'color': INK}), (b, {'color': SUB})]], size=12.5,
                  anchor='ctr')]
    s.add('dl/sheet', out)
    HD = 96                                    # 11-10 4차: 손 112 → 96(살짝만 작게)
    hw = HD * 773 / 960
    bx, by2 = sx + sw - 120, by_ + 25
    s.add('dl/hand', [P('dl/hand', str(AS / 'hand.png'), bx - hw * 0.388, by2 - HD * 0.015 + 6, hw, HD)])
    # 시트의 답이 칩이 되어 검색창으로(모션그래픽과 같은 순서: 검색어 선택 → 칩 도착 → 글이 바로 바뀜)
    fly, fw = chip('dl/fly', tx0 - 12, y + h / 2 - 17, ANSWER, 'fill', pt=QPT, h=34, padx=12)
    s.add('dl/fly', fly, temp=True)
    fdx, fdy = (sx + 36 + tw(ANSWER, 24, 'b') / 2) - (tx0 - 12 + fw / 2), (sy + 78) - (y + h / 2)
    # 11-10 4차: UX 3(보낼 말을 다듬어 건넴)까지 아우르도록 '다듬어'를 넣음
    s.add('dl/cap', [caption('dl/cap', [[('찾은 답을 다듬어,', INK)], [('근거와 함께 건넵니다', PURPLE)]], sx + sw + 62, 348, size=30, align='l')])
    s.on('dl/q', 'jump', 0)
    s.on('dl/sheet', 'rise', 150, 550, dy=16)
    s.on('dl/cap', 'rise', 450, 550, dy=16)
    s.click()                    # 입력하기 → 검색어가 선택되고 답이 날아와 → 타이핑 없이 바로 찾은 이름으로 바뀜
    th = max(cue('deliver.tap', 500) - 500, 0)     # 11-11 8차: 손은 '입력하기'를 말할 때 버튼을 누름(CUES)
    s.on('dl/hand', 'fly', th, 650, dx=140, dy=200, bend=0.1)
    s.on('dl/hand', 'pulse', th + 680, 140, scale=0.93)
    t = th + 980
    s.on('dl/sel', 'wipe_in', t, 260)
    s.on('dl/sel', 'jump', t)
    s.on('dl/fly', 'fade_in', t, 120)
    s.on('dl/fly', 'fly', t, 520, dx=fdx, dy=fdy, bend=0.3, show=False, fade=False, grow=1.4)
    t += 520
    s.on(['dl/q', 'dl/sel'], 'fade_out', t - 40, 80)
    s.on('dl/q2', 'appear', t, 1)
    s.on('dl/sweep', 'wipe_in', t, 320)
    s.on('dl/sweep', 'jump', t)
    s.on('dl/fly', 'fade_out', t, 150)
    s.on('dl/cur', 'appear', t + 40, 1)
    s.on('dl/cur', 'blink', t + 70, 1000)
    s.on('dl/sweep', 'fade_out', t + 660, 300)
    return s


# ------------------------------------------------------------------ 9. 한눈에 보기 (4열 좌→우 직관적 파이프라인) — 11-10: 본문에서 빼고 Appendix 첫 장으로
def s_overview():
    s = Slide('overview', trans=('fade', 500), done={'00', '01', '02', '03', '04'},
              notes='(Appendix) 전체 흐름을 한 장에 모았습니다. 질문을 나누고 찾은 단서로 다시 묻습니다. 이 모든 과정은 기기 안에서 이뤄집니다.')
    s.add('ov/cap', [caption('ov/cap', [[('질문을 나누고, ', INK), ('찾은 단서로 다시 묻습니다', PURPLE)]], 640, 80, size=26)])
    tagw = tw('모든 단계가 기기 안에서', 10.5, 'b') + 48
    s.add('ov/dev', [R('ov/dev/bg', 36, 136, 1208, 558, prst='roundRect', radius=28, fill='FFFFFF', alpha=55, line=LINE2, line_w=1.4),
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

    cy = 166
    # Column 1: 01 상황 인식 (x=54, w=236)
    c1x, c1w = 54, 236
    pill, txt, _, _ = search_pill('ov/q', c1x + 12, cy + 72, c1w - 24, 48, QUERY, pt=9.5, icon='mag', cursor=False)
    tbw = c1w - 24
    tbh = tbw * 168 / 1300
    s.add('ov/q', [R('ov/q/card', c1x, cy + 34, c1w, 332, prst='roundRect', radius=18, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=SHADOW_CARD)] +
          stage_tag('ov/q/tag', c1x, cy, '01', '상황 인식') + pill + [txt] +
          [P('ov/q/kb', str(AS / 'kb-toolbar.png'), c1x + 12, cy + 146, tbw, tbh, radius=8),
           R('ov/q/ring', c1x + 12 + 102 * tbw / 1300 - 15, cy + 146 + 82 * tbh / 168 - 15, 30, 30, prst='ellipse', fill=None, line=PURPLE,
             line_w=2.2, glow=(8, RING, 40))])

    # Column 2: 02 질의 재작성 (x=316, w=264)
    c2x, c2w = 316, 264
    rows = [R('ov/rw/bg', c2x, cy + 34, c2w, 332, prst='roundRect', radius=18, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=SHADOW_CARD),
            T('ov/rw/hd', c2x + 18, cy + 52, 220, 24, 'Query Rewriting', size=12.5, color=PURPLE, weight='b'),
            R('ov/rw/r1', c2x + 14, cy + 96, c2w - 28, 56, prst='roundRect', radius=12, fill=LAV, line=None)]
    rows += numdot('ov/rw/n1', c2x + 32, cy + 124, 1, r=10, pt=8.5)
    rows.append(T('ov/rw/t1', c2x + 48, cy + 96, c2w - 64, 56, '지은이네 집들이는 언제였지?', size=11, color=INK, weight='b', anchor='ctr'))
    rows.append(R('ov/rw/r2', c2x + 14, cy + 172, c2w - 28, 56, prst='roundRect', radius=12, fill=BLUE_BG, line=None))
    rows += numdot('ov/rw/n2', c2x + 32, cy + 200, 2, r=10, pt=8.5, fill=BLUE)
    tk, tkw = chip('ov/rw/tk', c2x + 48, cy + 189, '3/15 (일)', 'fill', pt=9.5, h=22, padx=8)
    rows += tk
    rows.append(T('ov/rw/t2', c2x + 48 + tkw + 5, cy + 172, c2w - 64 - tkw, 56, '마셨던 와인은?', size=11, color=INK, weight='b', anchor='ctr'))
    s.add('ov/rw', stage_tag('ov/rw/tag', c2x, cy, '02', '질의 재작성') + rows)

    # Column 3: 03 연쇄 탐색 (x=606, w=330) — Hop 1 위, Hop 2 아래
    c3x, c3w = 606, 330
    s.add('ov/hoptag', stage_tag('ov/hoptag', c3x, cy, '03', '연쇄 탐색'))

    def hop_box(key, x, y, w, h, n, res_kind, res_label, res_sub):
        out = [R(key + '/bg', x, y, w, h, prst='roundRect', radius=18, fill='FFFFFF', line=RING, line_w=1.8, shadow=SHADOW_CARD),
               T(key + '/t', x + 18, y + 14, 220, 24, 'Query %d' % n, size=12, color=PURPLE, weight='b', anchor='ctr')]      # 본문 15·16쪽과 같은 이름
        hc, _ = chip(key + '/h', x + w - 16 - (tw('Hop %d' % n, 9.5, 'b') + 20), y + 14, 'Hop %d' % n, 'fill', pt=9.5, h=22, padx=10)
        out += hc
        out.append(R(key + '/r', x + 14, y + 52, w - 28, 86, prst='roundRect', radius=12, fill='F7F5FC', line=None))
        out.append(P(key + '/ri', ICON[res_kind], x + 28, y + 79, 32, 32))
        out.append(T(key + '/rt', x + 70, y + 66, w - 88, 24, res_label, size=11.5, color=INK, weight='b', anchor='ctr'))
        out.append(T(key + '/rs', x + 70, y + 94, w - 88, 24, res_sub, size=10.5, color=SUB, anchor='ctr'))
        return out

    s.add('ov/h1', hop_box('ov/h1', c3x, cy + 34, c3w, 154, 1, 'talk',
                           '지은 · 3월 15일 (일)', '‘휴지 안 사 와도 돼’'))
    s.add('ov/h2', hop_box('ov/h2', c3x, cy + 212, c3w, 154, 2, 'gallery',
                           '갤러리 · 3월 15일 20:14', ANSWER))

    # Column 4: 04 결과 제공 (x=962, w=264)
    c4x, c4w = 962, 264
    bt_w = tw('입력하기', 11.5, 'b')
    bt_cx = c4x + c4w / 2
    res = [R('ov/res/bg', c4x, cy + 34, c4w, 332, prst='roundRect', radius=18, fill='FFFFFF', line=RING, line_w=1.8, glow=(8, RING, 22), shadow=SHADOW_CARD),
           R('ov/res/card', c4x + 14, cy + 50, c4w - 28, 92, prst='roundRect', radius=14, fill=LAV, line=None)] + \
          spark_icon('ov/res/star', c4x + 23, cy + 61.5, size=16, color=PURPLE) + \
          [T('ov/res/l', c4x + 42, cy + 60, 200, 20, '자동 완성 추천', size=10, color=PURPLE, weight='b'),
           T('ov/res/a', c4x + 26, cy + 84, c4w - 52, 44, '배비치 소비뇽 블랑', size=16.5, color=INK, weight='b', anchor='ctr'),
           R('ov/res/btn', c4x + 14, cy + 154, c4w - 28, 38, prst='roundRect', radius=10, fill=PURPLE, line=None)] + \
          check_icon('ov/res/chk', bt_cx - bt_w / 2 - 9, cy + 173, s=9.5, color='FFFFFF', w=2.0) + \
          [T('ov/res/btnt', c4x + 26, cy + 154, c4w - 40, 38, '입력하기', size=11.5, color='FFFFFF', weight='b', align='c', anchor='ctr'),
           T('ov/res/ml', c4x + 18, cy + 210, 200, 20, '연결된 기억', size=10, color=SUB, weight='b'),
           P('ov/res/i1', ICON['talk'], c4x + 20, cy + 242, 22, 22),
           T('ov/res/s1', c4x + 50, cy + 238, c4w - 64, 30, '지은  ‘휴지 안 사 와도 돼’ · 3/15', size=10, color=INK, anchor='ctr'),
           P('ov/res/i2', ICON['gallery'], c4x + 20, cy + 282, 22, 22),
           T('ov/res/s2', c4x + 50, cy + 278, c4w - 64, 30, '와인 사진  3월 15일 20:14', size=10, color=INK, anchor='ctr')]
    s.add('ov/res', stage_tag('ov/res/tag', c4x, cy, '04', '결과 제공') + res)

    # Bottom Bar: 00 데이터 색인 (x=54, y=566, w=1172, h=106)
    iy = 566
    idx = [R('ov/idx/bg', 54, iy, 1172, 106, prst='roundRect', radius=18, fill=LAV2, line=LINE2, line_w=1.2)]
    idx += stage_tag('ov/idx/tag', 72, iy + 14, '00', '데이터 색인')
    for i, ic in enumerate(['talk', 'gallery', 'note', 'cal', 'mail']):
        idx.append(P('ov/idx/a%d' % i, ICON[ic], 76 + i * 34, iy + 54, 26, 26))
    cols = [('원문', '박스 정리 다 했어! 이따 올 때…', BODY),
            ('의미 벡터', '[0.86, −0.08, 0.33, …]', PURPLE),
            ('메타데이터', '{ date: "2026-03-15", app, … }', INK)]
    for i, (a, b, col) in enumerate(cols):
        cx_ = 330 + i * 295
        idx.append(T('ov/idx/l%d' % i, cx_, iy + 41, 270, 24, a, size=12, color=PURPLE if i else SUB, weight='b'))
    s.add('ov/idx', idx)

    # 좌 → 우 직관적 화살표 (01 → 02 → 03 Hop1 → 단서 대입 → 03 Hop2 → 04)
    s.add('ov/a1', thread('ov/a1', [(c1x + c1w + 2, cy + 190)] * 2 + [(c2x - 2, cy + 190)] * 2, w=2.4, tail='triangle'))
    s.add('ov/a2', thread('ov/a2', scurve((c2x + c2w + 2, cy + 124), (c3x - 2, cy + 110)), w=2.4, tail='triangle'))
    s.add('ov/loop', thread('ov/loop', scurve((c3x - 2, cy + 148), (c2x + c2w + 2, cy + 196)), w=2.4, tail='triangle'))
    s.add('ov/loopt', chip('ov/loopt', c3x - 13, cy + 162, '3/15 (일)', 'white', pt=8.5, h=20, padx=7, align='c')[0])
    s.add('ov/a3', thread('ov/a3', scurve((c2x + c2w + 2, cy + 216), (c3x - 2, cy + 286)), w=2.4, tail='triangle'))
    s.add('ov/a4', thread('ov/a4', scurve((c3x + c3w + 2, cy + 290), (c4x - 2, cy + 190)), w=2.4, tail='triangle'))
    s.add('ov/u1', [line('ov/u1', (c3x + c3w / 2, iy), (c3x + c3w / 2, cy + 368), color=PURPLE2, w=1.8, dash='dash')])
    order = [('ov/dev', 0), ('ov/idx', 150), ('ov/q', 400), ('ov/a1', 650), ('ov/rw', 750), ('ov/hoptag', 950),
             ('ov/a2', 1000), ('ov/h1', 1100), ('ov/u1', 1300), ('ov/loop', 1450), ('ov/loopt', 1650),
             ('ov/a3', 1750), ('ov/h2', 1850), ('ov/a4', 2150), ('ov/res', 2250)]
    wipes = {'ov/a1': 'left', 'ov/a2': 'left', 'ov/a3': 'left', 'ov/a4': 'left', 'ov/u1': 'up', 'ov/loop': 'right'}
    for k, d in order:
        if k in wipes:
            s.on(k, 'wipe_in', d, 400, dir=wipes[k])
        else:
            s.on(k, 'rise', d, 450, dy=12)
    s.on('ov/cap', 'rise', 2650, 500, dy=14)
    return s


SLIDES = [s_hiw, s_ask, s_cloud, s_old, s_kw, s_emb, s_step, s_chain, s_idx, s_trig, s_split, s_hop1, s_hop2, s_deliver]


def appendix_specs():
    """Appendix: 표지 → 한눈에 보기(11-10: 본문에서 옮김) → 나머지."""
    import appendix
    fs = list(appendix.APPENDIX)
    return [fs[0](), s_overview()] + [f() for f in fs[1:]]


# ------------------------------------------------------------------ 조립
BLUR_SOL = 22                                   # 'How it works?' 뒤 솔루션 장은 조금 더 흐리게(11-09 사용자 요청, 16 → 22)


def blur_png(src, dst, radius=16, veil=0.32):
    im = Image.open(src).convert('RGB').resize((1920, 1080), Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(radius))
    Image.blend(im, Image.new('RGB', im.size, (250, 248, 255)), veil).save(dst)


def add_slides(prs, layout, note_tpl, specs, auto=False, hold=1700):
    """specs를 prs 끝에 한 장씩 그려 넣는다(도형, 효과, 전환, 노트). 중간본 조립도 이걸 불러 HowItWorks_Argon.pptx와 같은 장을 만든다."""
    slides, report, secs = [], [], []
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
                if kind == 'jump':          # 화면 밖(temp)에서 제자리로 순간 이동 — 처음 나타나는 효과와 같은 때에. to = 제자리에서 더 옮길 만큼
                    to = kw.get('to', (0, 0))
                    kind, dur, kw = 'move', 1, dict(dx=-OFF + to[0], dy=to[1], accel=0, decel=0)
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
                holds = getattr(sp, 'holds', None) or [(500 if j == 0 else hold) for j in range(len(tl.steps))]
                slide._element.append(tl.xml(sp_ids, auto=(150, holds)))
                total = 150 + sum(tl.step_len(j) + holds[j] for j in range(len(tl.steps)))
                adv = max(adv or 0, total)
            else:
                slide._element.append(tl.xml(sp_ids, first_auto=True))
        set_transition(slide, sp.trans, adv if (auto or sp.advance) else None)
        if getattr(sp, 'holds', None):          # 발표 속도 미리보기: PowerPoint가 장 넘김 시간을 따로 더하므로 여기서는 더하지 않음
            secs.append((adv or 2500) / 1000)
        else:
            dur_s = ((adv or 2500) + (sp.trans[1] if sp.trans else 0)) / 1000
            secs.append(max(dur_s, 1.6))
        ns = slide.notes_slide
        if ns.notes_text_frame is None:
            for e in note_tpl:
                ns.shapes._spTree.append(copy.deepcopy(e))
        ns.notes_text_frame.text = sp.notes
        report.append((sp.key, sp.clicks(), sp.notes.count('(클릭)'), len(pa.spids)))
        slides.append(slide)
    return slides, report, secs



def build(dst, auto=False, hold=1700, talk=False, says=None):
    """원본 덱에서 장 틀과 노트 틀만 빌려, 새 장을 끝에 다 넣은 뒤 원본 장을 지운다
    (먼저 지우면 python-pptx가 장 파일 이름을 다시 써서 PowerPoint가 못 여는 일이 있었음).
    talk=True면 미리보기 영상용: 본문 17장만, 발표 속도로 머물고 자막을 띄움(talk_specs). says는 낭독 길이(narrate)."""
    prs = Presentation(str(SRC))
    layout = prs.slides[LAYOUT_INDEX].slide_layout
    note_tpl = [copy.deepcopy(sh._element) for sh in prs.slides[LAYOUT_INDEX].notes_slide.placeholders]
    lst = prs.slides._sldIdLst
    old = list(lst)
    specs = talk_specs(says=says) if talk else [f() for f in SOL_SLIDES] + [f() for f in SLIDES] + appendix_specs()
    _, report, secs = add_slides(prs, layout, note_tpl, specs, auto, hold)
    for sid in old:
        prs.part.drop_rel(sid.get(q('r:id')))
        lst.remove(sid)
    samsung_fonts.remap_prs(prs)
    prs.save(str(dst))
    return report, secs


# ------------------------------------------------------------------ 발표 시간 어림(--time)
SPEECH_RATE = 6.6                  # 1초에 말하는 음절 수(쉼을 뺀 말 빠르기). 낭독 영상(--tts)과 맞춘 값(11-11 7차: 목소리 F2F1_70, 속도 1.15)
# 실제 발표에서 생기는 틈. 낭독 영상과 --time 어림이 같은 값을 쓴다
# 11-11 7차: '유튜브 영상처럼 쉬지 않고 쭉쭉 간다' → 말 빠르기는 그대로 두고, 화면이 바뀔 때·물음 뒤·문장 사이에 숨을 돌리게 틈을 늘림
LAT_START = 0.40                   # 장이 열린 뒤 말을 떼기까지(화면이 자리 잡는 것을 보고 말함)
LAT_CLICK = 0.30                   # 클릭한 뒤 새 문장을 시작하기까지(효과가 뜨는 것을 보고 말함)
LAT_MID = 0.10                     # 문장 중간에서 클릭한 뒤 말을 잇기까지
GAP_SLIDE = 0.55                   # 그 장의 말을 마치고 다음 장으로 넘기기까지
GAP_SENT = 0.55                    # 문장을 마치고 다음 클릭을 누르기까지
GAP_MID = 0.25                     # 문장 중간에서 클릭할 때 말이 끊기는 틈
GAP_Q = 0.35                       # 물음으로 끝난 구간·장 뒤에 더 두는 틈(답을 기다리듯 한 박자)
# 한 구간 안에서 문장과 문장 사이에 넣는 쉼(문장마다 따로 읽혀 이어 붙임. 토막 앞뒤에 남는 묵음 PIECE_PAD가 여기에 더해짐)
S_BEAT = 0.50                      # 마침표 뒤(숨 한 번)
Q_BEAT = 0.80                      # 물음 뒤(답을 기다리듯)
X_BEAT = 0.25                      # 느낌표 뒤(따옴표 안의 카톡 글이 이어질 때)
R_BEAT = 0.85                      # 노트에 (쉼)이라고 적은 자리(일부러 한 박자, 1초쯤)
REST = '(쉼)'
PIECE_PAD = 0.15                   # 낭독 토막 앞뒤에 남기는 묵음(tts_c.tidy의 lead + trail)
RATE_MAX, RATE_AIM = 6.9, 6.4      # 낭독: 한 토막이 1초에 RATE_MAX음절보다 빠르면(쉼 없는 짧은 한 문장) 그 토막만 RATE_AIM쯤으로 다시 읽음
READ_AS = {'Reasoning Embedding': '리즈닝 임베딩', 'Query Rewriting': '쿼리 리라이팅', 'Weave': '위브', 'BM25': '비엠 이십오', 'UX': '유엑스'}


def _num_ko(n):
    """숫자를 한자어로 읽은 글(음절 수를 세려고): 15 → 십오, 2026 → 이천이십육."""
    if n == 0:
        return '영'
    out = ''
    for unit, name in ((1000, '천'), (100, '백'), (10, '십'), (1, '')):
        d, n = divmod(n, unit)
        if d:
            out += ('' if d == 1 and unit > 1 else '일이삼사오육칠팔구'[d - 1]) + name
    return out


def syllables(text):
    """소리 내어 읽을 때의 음절 수(한글 글자 수 + 숫자·영문 읽기)."""
    text = text.replace(REST, ' ')
    for k, v in READ_AS.items():
        text = text.replace(k, v)
    text = re.sub(r'\d+', lambda m: _num_ko(int(m.group())), text)
    return sum(1 for ch in text if '가' <= ch <= '힣') + sum(len(re.findall(r'[aeiouAEIOU]+', w)) for w in re.findall(r'[A-Za-z]+', text))


def _group_len(grp):
    """한 묶음(장이 열린 뒤, 또는 클릭 한 번)의 효과가 끝나는 때(ms)."""
    t = 0
    for key, kind, delay, dur, kw in grp:
        d = dur * 2 if kind == 'pulse' else (kw.get('ms', 45) * kw.get('n', 20) if kind == 'type' else
                                            (0 if kind in ('blink', 'jump', 'goto', 'appear') else dur))
        t = max(t, delay + d)
    return t


_CUE_CACHE = {}


def _cue_data():
    """낭독에서 잰 문장마다의 때(out/tts/_cues.json, narrate()가 씀). 없으면 빈 표."""
    f = OUT / 'tts' / '_cues.json'
    if 'd' not in _CUE_CACHE:
        _CUE_CACHE['d'] = json.loads(f.read_text(encoding='utf-8')) if f.exists() else {}
    return _CUE_CACHE['d']


def _in_piece(text, dur, pauses, phrase):
    """토막(text, 길이 dur초) 안에서 phrase를 말하기 시작하는 때(초).
    쉼표마다 잰 쉼 가운데 가장 가까운 것을 짝지어 그 자리를 기준으로 삼고(쉼표에서 쉬지 않고 읽힌 곳은 짝이 없음), 그 사이는 음절 수로 나눈다."""
    i = text.index(phrase)
    cw = 1.8 if pauses is None else 0.6                       # 짝 없는 쉼표 하나의 무게(음절): 낭독 전 어림은 1.8, 잰 토막에서는 0.6
    w = lambda t: syllables(t) + cw * t.count(',')
    t0, t1 = 0.05, max(dur - 0.1, 0.1)
    total = max(w(text), 1)
    segs, c0, a, left = [], 0, t0, [list(z) for z in (pauses or [])]
    for m in re.finditer(',', text):
        e = t0 + (t1 - t0) * w(text[:m.start()]) / total     # 쉼 없이 고르게 읽었다면 이 쉼표가 올 때
        cand = [z for z in left if abs((z[0] + z[1]) / 2 - e) < 0.9]
        if cand:
            z = min(cand, key=lambda z: abs((z[0] + z[1]) / 2 - e))
            left = [y for y in left if y[0] > z[0]]
            segs.append((c0, m.start(), a, z[0]))
            c0, a = m.end(), z[1]
    segs.append((c0, len(text), a, t1))
    for c0, c1, a, b_ in segs:
        if i < c1 or c1 == len(text):
            return a + (b_ - a) * w(text[c0:max(i, c0)]) / max(w(text[c0:c1]), 1)


def cue(name, default, ahead=0.15):
    """말에 맞춰 뜨는 효과의 때(ms, s.on()에 넣는 값). CUES[name] = (장 키, 구간, 그 말을 시작하는 구절).
    낭독에서 잰 값(out/tts/_cues.json)이 지금 노트와 맞으면 그 값으로, 아니면 음절 수로 어림한다. 구절이 노트에 없으면 default."""
    spec = CUES.get(name)
    if not spec:
        return default
    key, j, phrase = spec
    segs = NOTES[key].split('(클릭)')
    phrase = tts_text(phrase)
    pieces = _sents(segs[j])
    hit = [k for k, (t, _) in enumerate(pieces) if phrase in t]
    if not hit:
        print('   ! cue %s: ‘%s’가 %s 노트의 구간 %d에 없음 → 기본값 %d' % (name, phrase, key, j, default))
        return default
    k = hit[0]
    got = _cue_data().get('%s_%d' % (key, j))
    if got and all(isinstance(g, dict) for g in got) and [g['t'] for g in got] == [t for t, _ in pieces]:
        t = got[k]['at'] + _in_piece(got[k]['t'], got[k]['dur'], got[k]['pauses'], phrase)
    else:                                   # 낭독이 없거나 노트가 바뀜: 음절 수로 어림(쉼 없는 말 빠르기 6.9음절/초)
        durs = [syllables(x) / 6.9 + 0.3 * x.count(',') + PIECE_PAD for x, _ in pieces]
        t = sum(durs[:k]) + sum(b for _, b in pieces[:k]) + _in_piece(pieces[k][0], durs[k], None, phrase)
    return max(round((_lead(segs, j) + t - ahead) / SPEED * 1000), 0)


def _ends(seg):
    return seg.replace(REST, ' ').rstrip().endswith(('.', '?', '!'))


def _beat(sent):
    """구간 안에서 그 문장을 마친 뒤 다음 문장까지 넣는 쉼(초)."""
    return Q_BEAT if sent.endswith('?') else (X_BEAT if sent.endswith('!') else S_BEAT)


def _sents(seg):
    """한 구간의 글을 낭독 토막으로 나눈다: [(읽을 글, 그 뒤에 넣는 쉼(초))]. 문장이 끝난 자리와 (쉼) 자리에서 끊는다(마지막 토막의 쉼은 쓰지 않음)."""
    out = []
    parts = tts_text(seg).split(REST)
    for i, part in enumerate(parts):
        ss = [t for t in re.split(r'(?<=[.?!])\s+', part.strip()) if t]
        for k, t in enumerate(ss):
            rest = i + 1 < len(parts) and k == len(ss) - 1          # 이 토막 뒤에 (쉼)이 적혀 있음
            out.append((t, max(_beat(t), R_BEAT) if rest else _beat(t)))
    return out


def _lead(segs, j):
    """구간 j에서 말을 떼기까지의 틈(초): 장이 열린 뒤 첫 구간은 LAT_START, 클릭 뒤 새 문장을 시작하면 LAT_CLICK, 문장 중간의 클릭 뒤는 LAT_MID.
    구간이 (쉼)으로 시작하면 그만큼 더 기다린다."""
    base = LAT_START if j == 0 else (LAT_CLICK if _ends(segs[j - 1]) else LAT_MID)
    return base + (R_BEAT if segs[j].lstrip().startswith(REST) else 0)


def seg_leads(sp):
    """구간마다 말을 떼기까지의 틈(초). _lead()."""
    segs = sp.notes.split('(클릭)')
    return [_lead(segs, j) for j in range(len(segs))]


def seg_gaps(sp):
    """구간마다 말을 마친 뒤의 틈(초): 그 장의 끝 구간은 GAP_SLIDE, 문장이 끝난 구간은 GAP_SENT, 문장 중간에서 누르는 클릭은 GAP_MID.
    물음으로 끝난 구간은 GAP_Q만큼, (쉼)으로 끝난 구간은 R_BEAT만큼 더 둔다."""
    segs = sp.notes.split('(클릭)')
    return [(GAP_SLIDE if j == len(segs) - 1 else (GAP_SENT if _ends(seg) else GAP_MID)) +
            (R_BEAT if seg.rstrip().endswith(REST) else (GAP_Q if seg.rstrip().endswith('?') else 0)) for j, seg in enumerate(segs)]


def _say_times(sp, rate=SPEECH_RATE):
    """노트를 (클릭)으로 나눈 구간마다 걸리는 시간(초) 어림: 말 떼기까지 + 음절 ÷ 속도 + 구간 안 문장 사이 쉼 + 말을 마친 뒤의 틈."""
    out = []
    for seg, lead, gap in zip(sp.notes.split('(클릭)'), seg_leads(sp), seg_gaps(sp)):
        out.append(lead + syllables(seg) / rate + sum(b + PIECE_PAD for _, b in _sents(seg)[:-1]) + gap)
    return out


def rehearse(specs, rate=SPEECH_RATE, says=None):
    """발표를 한 번 해 보는 셈으로 장마다 걸리는 시간을 어림한다.
    한 구간(장이 열린 뒤, 또는 클릭 한 번 뒤) = max(그 구간에 걸리는 말(말 떼기 전후의 틈 포함), 그 구간의 효과 길이). 여기에 장 넘김 시간을 더한다.
    says = {장 키: [구간마다 걸리는 시간(초)]}를 주면 음절로 어림하지 않고 낭독 길이로 잰다(narrate())."""
    rows, total = [], 0.0
    for sp in specs:
        segs = sp.notes.split('(클릭)')
        say = says[sp.key] if says else _say_times(sp, rate)
        anim = [_group_len(g) / 1000 for g in sp.groups]
        sec = ((sp.trans[1] / 1000) if sp.trans else 0) + 0.15
        for i in range(len(segs)):
            sec += max(say[i], anim[i] if i < len(anim) else 0)
        total += sec
        rows.append((sp.key, len(segs) - 1, sum(syllables(g) for g in segs), sec, total))
    return rows


FFMPEG = str(Path.home() / '.cache' / 'weave-tools' / 'bin' / 'ffmpeg')
MARK = ['B9B2C9', '6A6474', '1C1A24']        # 자막마다 번갈아 붙는 왼쪽 아래 작은 표(밝은 회색, 회색, 검정): 영상에서 그 구간이 실제로 시작한 때를 찾는 데 씀
MARK_BOX = (0, 713, 46, 7)


def tts_text(seg):
    """낭독(TTS)에 넘길 글: 영문과 숫자를 읽는 소리로 바꾸고 따옴표를 뺀다."""
    t = ' '.join(seg.split())          # (쉼)은 그대로 둔다(_sents가 그 자리에서 끊음)
    for k, v in READ_AS.items():
        t = t.replace(k, v)
    t = re.sub(r'\d+', lambda m: _num_ko(int(m.group())), t)
    t = re.sub('[‘’“”"]', '', t)
    return re.sub(r'[?!](?=[가-힣])', '', t)          # 따옴표 안의 물음이 문장 가운데 있을 때(‘… 언제였지?’를): 물음표 없이 이어 읽음


def narrate(specs, voice=None, check=False):
    """본문 노트를 (클릭)마다 토막 내어 낭독(wav)을 만든다.
    돌려줌: ({장 키: [구간마다 걸리는 시간 = 말 떼기까지 + 토막 길이 + 말을 마친 뒤의 틈]}, {장 키: [wav 경로]}). 틈은 seg_leads(), seg_gaps().
    voice는 tts_c의 목소리 이름(없으면 기본). check면 낭독을 받아쓰기로 글과 견준다.
    실제 발표처럼 들리게 두 가지를 손본다: 구간 안의 문장은 하나씩 따로 읽혀 사이에 쉼을 넣고(_beat: 마침표 S_BEAT, 물음 Q_BEAT),
    쉼 없이 빨리 읽힌 짧은 토막은 천천히 다시 읽는다(RATE_MAX). 문장마다 구간 안에서 시작하는 때는 out/tts/_cues.json에 남긴다(효과를 말에 맞출 때 봄)."""
    import numpy as np
    import tts_c
    d = OUT / 'tts'
    shutil.rmtree(d, ignore_errors=True)
    todo, parts = [], {}
    for sp in specs:
        for j, seg in enumerate(sp.notes.split('(클릭)')):
            parts[sp.key, j] = []
            for k, (t, beat) in enumerate(_sents(seg)):
                name = '%s_%d_p%d' % (sp.key, j, k)
                parts[sp.key, j].append((name, t, beat))
                todo.append((name, t if t.endswith(('.', '?', '!')) else t.rstrip(', ') + ','))       # 문장 중간에서 끊는 토막은 쉼표로(말끝을 내리지 않게)
    tts_c.synth(todo, d, voice)
    lens = {n: tts_c.tidy(d / (n + '.wav')) for n, _ in todo}
    v = tts_c.pick_voice(voice)
    if v != 'heami':
        base, slow = tts_c.SPEEDS.get(v, tts_c.SPEED), {}
        for n, t in todo:
            rate = syllables(t) / lens[n]
            if rate > RATE_MAX:
                slow.setdefault(round(base * RATE_AIM / rate, 2), []).append((n, t))
        for spd, lst in sorted(slow.items()):
            tts_c.synth(lst, d, voice, speed=spd)
            lens.update({n: tts_c.tidy(d / (n + '.wav')) for n, _ in lst})
            for n, t in lst:                    # 그래도 빠르면(합성 길이가 속도에 딱 비례하지는 않음) 한 번 더 늦춤
                rate = syllables(t) / lens[n]
                if rate > RATE_MAX:
                    tts_c.synth([(n, t)], d, voice, speed=round(spd * RATE_AIM / rate, 2))
                    lens[n] = tts_c.tidy(d / (n + '.wav'))
    says, clips, cues = {}, {}, {}
    for sp in specs:
        segs = sp.notes.split('(클릭)')
        clips[sp.key], durs = [], []
        for j in range(len(segs)):
            xs, at, prev = [], [], None
            for n, t, beat in parts[sp.key, j]:
                sr, x = tts_c._load(d / (n + '.wav'))
                if prev is not None:
                    xs.append(np.zeros(int(sr * prev), dtype=np.int16))
                at.append({'t': t, 'at': round(sum(len(a) for a in xs) / sr, 3), 'dur': round(len(x) / sr, 3), 'pauses': tts_c.pauses(x, sr)})
                xs.append(x)
                prev = beat
                (d / (n + '.wav')).unlink()
            cues['%s_%d' % (sp.key, j)] = at
            dst = d / ('%s_%d.wav' % (sp.key, j))
            tts_c._save(dst, sr, np.concatenate(xs))
            clips[sp.key].append(dst)
            durs.append(tts_c.wav_len(dst))
        says[sp.key] = [lead + t + gap for t, lead, gap in zip(durs, seg_leads(sp), seg_gaps(sp))]
    (d / '_cues.json').write_text(json.dumps(cues, ensure_ascii=False), encoding='utf-8')
    _CUE_CACHE.clear()
    if check:
        narrate_check(specs, clips)
    return says, clips


def narrate_check(specs, clips, ok=0.85):
    """낭독이 글대로 읽혔는지 받아쓰기(기기 안의 Whisper)로 견준다. 장마다 토막을 이어 붙여 듣고, 글과 다르게 들린 장을 찍는다.
    받아쓴 글은 out/tts_check.txt에 남긴다. 점검용 모델이 없으면 건너뛴다."""
    import difflib
    import numpy as np
    import tts_c
    d = OUT / 'tts'
    paths = []
    for sp in specs:
        sr = tts_c._load(clips[sp.key][0])[0]
        xs = []
        for c in clips[sp.key]:
            xs += [tts_c._load(c)[1], np.zeros(int(sr * 0.4), dtype=np.int16)]
        paths.append(str(d / ('_chk_%s.wav' % sp.key)))
        tts_c._save(paths[-1], sr, np.concatenate(xs))
    heard = tts_c.transcribe(paths)
    for p in paths:
        Path(p).unlink()
    if heard is None:
        print('낭독 점검: 받아쓰기 모델이 없어 건너뜀')
        return []
    norm = lambda t: re.sub(r'[^가-힣a-z0-9]', '', tts_text(t.replace('(클릭)', ' ').replace(REST, ' ')).lower())
    bad, lines = [], []
    for sp, p in zip(specs, paths):
        h = heard.get(p, '')
        r = difflib.SequenceMatcher(None, norm(sp.notes), norm(h)).ratio()
        lines.append('%s  %.2f\n   글: %s\n   들린 말: %s\n' % (sp.key, r, ' '.join(sp.notes.split()), h))
        if r < ok:
            bad.append((sp.key, r, h))
    (OUT / 'tts_check.txt').write_text('\n'.join(lines), encoding='utf-8')
    print('낭독 점검(받아쓰기): %d장 가운데 %d장이 글과 다르게 들림 → out/tts_check.txt' % (len(specs), len(bad)))
    for key, r, h in bad:
        print('   %-8s %.2f  들린 말: %s' % (key, r, h))
    return bad


def subtitle(key, text, code=None, pt=15, maxw=1080):
    """미리보기 영상 아래쪽 자막(그 구간에 할 말). 긴 말은 폭에 맞춰 줄을 나눈다.
    code를 주면 왼쪽 아래 구석에 구간 표(MARK[code])를 함께 둔다(낭독을 얹을 때만 쓰고, 얹은 뒤 영상에서 지움)."""
    lines, cur = [], ''
    for w in text.split(' '):
        if cur and tw(cur + ' ' + w, pt, 'm') > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    lines.append(cur)
    lh = 26
    w = max(tw(ln, pt, 'm') for ln in lines) + 44
    h = lh * len(lines) + 16
    x, y = 640 - w / 2, 710 - h
    return [R(key + '/bg', x, y, w, h, prst='roundRect', radius=12, fill='1C1A24', alpha=82, line=None),
            T(key + '/t', x, y + 8, w, lh * len(lines), [[(ln, {})] for ln in lines], size=pt, color='FFFFFF', weight='m', align='c',
              lnspc=lh * 0.75)] + ([] if code is None else [R(key + '/mk', *MARK_BOX, fill=MARK[code % 3], line=None)])


def talk_specs(rate=SPEECH_RATE, says=None):
    """미리보기 영상용 본문 17장(Appendix는 넣지 않음): 구간마다 그 구간에 할 말을 하는 동안 머물고, 그 말을 아래에 자막으로 띄운다.
    그래서 영상 길이가 발표 시간 어림(--time)과 같다. says(narrate()의 낭독 길이)를 주면 그 길이만큼 머문다.
    장마다 sp.starts = [구간이 시작하는 때(영상 처음부터, 초)]를 남긴다."""
    specs = [f() for f in SOL_SLIDES + SLIDES]
    t, k = 0.0, 0
    for sp in specs:
        segs = sp.notes.split('(클릭)')
        say = says[sp.key] if says else _say_times(sp, rate)
        sp.holds = [max(round(say[j] * 1000) - _group_len(g), 0) for j, g in enumerate(sp.groups)]
        t += (sp.trans[1] / 1000 if sp.trans else 0) + 0.15
        sp.starts = []
        for j, grp in enumerate(sp.groups):
            sp.starts.append(t)
            t += (_group_len(grp) + sp.holds[j]) / 1000
            text = ' '.join(segs[j].replace(REST, ' ').split())
            if text:
                key = 'sub/%s/%d' % (sp.key, j)
                sp.add(key, subtitle(key, text, k if says else None))
                grp.insert(0, (key, 'appear', 0, 1, {}))
                if j + 1 < len(sp.groups):
                    sp.groups[j + 1].insert(0, (key, 'fade_out', 0, 100, {}))
            k += 1
    return specs


def video_len(mp4):
    """영상 길이(초). ffprobe가 없어 ffmpeg -i가 찍는 Duration을 읽는다."""
    err = subprocess.run([FFMPEG, '-hide_banner', '-i', str(mp4)], capture_output=True, text=True).stderr
    h, m, sec = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err).groups()
    return int(h) * 3600 + int(m) * 60 + float(sec)


def mark_times(mp4, specs, fps=30):
    """영상의 왼쪽 아래 구간 표를 읽어 구간마다 실제로 시작한 때(초)를 찾는다(PowerPoint 녹화는 계산한 때와 1초쯤 어긋날 수 있음).
    돌려줌: [초] — talk_specs()의 구간 순서대로. 못 찾은 구간은 계산한 때(sp.starts)를 쓴다."""
    import numpy as np
    x, y, w, h = MARK_BOX
    cw, ch = int(w * 1.5 - 12) // 2 * 2, int(h * 1.5 - 4) // 2 * 2          # 표 안쪽만. 짝수로(yuv420p에서 crop이 홀수를 짝수로 내림)
    cx, cy = int(x * 1.5 + 6) // 2 * 2, int(y * 1.5 + 3) // 2 * 2
    raw = subprocess.run([FFMPEG, '-loglevel', 'error', '-i', str(mp4), '-vf', 'fps=%d,crop=%d:%d:%d:%d:exact=1,format=gray' % (fps, cw, ch, cx, cy),
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    n = cw * ch
    assert len(raw) % n == 0, (len(raw), n)
    luma = np.frombuffer(raw, dtype=np.uint8).reshape(-1, n).mean(axis=1)
    assert abs(len(luma) / fps - video_len(mp4)) < 1.0, (len(luma) / fps, video_len(mp4))      # 프레임 수가 영상 길이와 맞아야 때가 맞음
    band = [(140, 198), (72, 140), (0, 72)]                 # MARK 순서대로(밝은 회색, 회색, 검정). 표가 없으면 바탕이라 198보다 밝음
    out, last, k, miss, off = [], 0, 0, 0, 0.0             # off = 지금까지 계산한 때보다 밀린 만큼(다음 구간은 그만큼 옮겨서 찾음)
    for sp in specs:
        for t0 in sp.starts:
            lo, hi = band[k % 3]
            hit = None
            for f in range(max(int((t0 + off - 1.5) * fps), last + 1), min(int((t0 + off + 2.5) * fps), len(luma) - 5)):
                seg = luma[f:f + 5]
                if seg.min() >= lo and seg.max() < hi and seg.max() - seg.min() <= 4:       # 다섯 프레임 내내 같은 밝기(사라지는 중이 아님)
                    hit = f
                    break
            if hit is None:
                miss += 1
                hit = max(int((t0 + off) * fps), last + 1)
            else:
                off = hit / fps - t0
            out.append(hit / fps)
            last = hit
            k += 1
    return out, miss


def add_voice(silent, mp4, says, clips, tail=1.0):
    """소리 없는 미리보기 영상에 낭독을 얹는다: 구간 표로 구간이 실제로 시작한 때를 찾아 낭독 토막을 그 자리에 놓고, 한 줄로 합쳐 넣는다.
    구간 표는 바로 위 바탕을 덮어 지우고(그래서 영상을 다시 인코딩함), 마지막 말이 끝나고 tail초 뒤에 영상을 끝낸다(모자라면 마지막 화면을 늘림)."""
    import tts_c
    specs = talk_specs(says=says)
    starts, miss = mark_times(silent, specs)
    order = [c for sp in specs for c in clips[sp.key]]
    leads = [ld for sp in specs for ld in seg_leads(sp)]
    end = starts[-1] + leads[-1] + tts_c.wav_len(order[-1]) + tail
    wav = OUT / '_voice.wav'
    tts_c.track([(c, t + ld) for c, t, ld in zip(order, starts, leads)], end, wav)
    x, y, w, h = MARK_BOX
    W, Y = int(w * 1.5) + 9, int(y * 1.5) - 7               # 표와 그 둘레(압축 번짐)까지
    H = 1080 - Y
    more = max(end - video_len(silent), 0) + 0.2
    cover = '[0:v]tpad=stop_mode=clone:stop_duration=%.2f,split[a][b];[b]crop=%d:%d:0:%d[p];[a][p]overlay=0:%d[v]' % (more, W, H, Y - H - 2, Y)
    # 소리 크기: 말소리를 -16 LUFS(영상에 흔히 쓰는 크기)에 맞추고, 짧게 튀는 소리만 -2.5dB에서 눌러 줌
    err = subprocess.run([FFMPEG, '-hide_banner', '-i', str(wav), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    gain = min(max(-16 - float(re.findall(r'I:\s+(-?[\d.]+) LUFS', err)[-1]), -6), 12)
    loud = '[1:a]volume=%.2fdB,alimiter=limit=0.75:attack=3:release=40:level=false:latency=true[au]' % gain
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', str(silent), '-i', str(wav), '-filter_complex', cover + ';' + loud,
                    '-map', '[v]', '-map', '[au]', '-r', '30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-t', '%.2f' % end, '-movflags', '+faststart', str(mp4)], check=True)
    wav.unlink()
    drift = max(abs(a - b) for a, b in zip(starts, [t for sp in specs for t in sp.starts]))
    print('낭독을 넣음: 구간 %d개, 표를 못 찾은 구간 %d개, 계산한 때와 가장 크게 어긋난 곳 %.2f초, 영상 길이 %d:%04.1f' % (
        len(starts), miss, drift, end // 60, end % 60))
    return starts


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
    global PASS1
    ap = argparse.ArgumentParser()
    ap.add_argument('--png', action='store_true')
    ap.add_argument('--video', action='store_true')
    ap.add_argument('--skip-blur', action='store_true', help='흐린 그림을 다시 만들지 않음(있는 것을 씀)')
    ap.add_argument('--time', action='store_true', help='덱을 만들지 않고 발표 시간만 어림(본문 17장)')
    ap.add_argument('--tts', action='store_true', help='--time, --video와 함께: 노트를 낭독(기기 안의 음성 합성)해서 그 길이로 재고, 영상에는 소리로 넣음')
    ap.add_argument('--voice', help='낭독 목소리: Supertonic 3의 F1~F5·M1~M5(기본 F2), heami = Windows 한국어 음성')
    ap.add_argument('--check', action='store_true', help='--tts와 함께: 낭독을 받아쓰기로 글과 견줌')
    ap.add_argument('--remux', action='store_true', help='--video --tts와 함께: PowerPoint 녹화(out/_silent.mp4)는 그대로 두고 낭독만 다시 얹음')
    ap.add_argument('--variant', help='대본과 낭독만 다른 판(<이름>/notes.json). 덱은 ../HowItWorks_Argon_claude_<이름>.pptx, 나머지는 out/<이름>/')
    a = ap.parse_args()
    if a.variant:
        use_variant(a.variant)
    if a.time:
        OUT.mkdir(exist_ok=True)
        specs = [f() for f in SOL_SLIDES + SLIDES]
        rows = rehearse(specs, says=narrate(specs, a.voice, a.check)[0] if a.tts else None)
        for i, (key, nclick, syl, sec, cum) in enumerate(rows, 1):
            print('%2d %-8s 클릭 %d  %3d음절  %5.1f초  (누적 %d:%02d)' % (i, key, nclick, syl, sec, cum // 60, cum % 60))
        how = '낭독 길이로 잼' if a.tts else '1초에 %.1f음절로 말할 때' % SPEECH_RATE
        print('본문 %d장  %d음절  %d:%02d  (%s)' % (len(rows), sum(r[2] for r in rows), rows[-1][4] // 60, rows[-1][4] % 60, how))
        return
    OUT.mkdir(exist_ok=True)
    blurs = ('blur_sol.png', 'blur_emb.png', 'blur_cloud.png')
    if not a.skip_blur or not all((OUT / f).exists() for f in blurs):
        # 1차: 흐린 배경 없이 만들고 PowerPoint로 찍어 앞 장(또는 같은 장의 앞 상태)을 흐리게
        for f in blurs:
            if not (OUT / f).exists():
                Image.new('RGB', (1920, 1080), (246, 243, 255)).save(OUT / f)
        tmp = OUT / '_pass1.pptx'
        PASS1 = True
        build(tmp)
        PASS1 = False
        pngs = render_c.png(tmp, OUT / '_pass1_png')
        names = [f.__name__[2:] for f in SOL_SLIDES + SLIDES]
        blur_png(pngs[names.index('sol3')], OUT / 'blur_sol.png', radius=BLUR_SOL)
        blur_png(pngs[names.index('emb')], OUT / 'blur_emb.png')
        blur_png(pngs[names.index('cloud')], OUT / 'blur_cloud.png', radius=7, veil=0.12)      # 살짝만 흐리게(5차: 4 → 5.5, 8차: 5.5 → 7로 조금 더)
        tmp.unlink()
    says = clips = None
    if a.video and a.tts:               # 낭독을 먼저 만든다: 말에 맞춰 뜨는 효과(cue)가 이 낭독에서 때를 찾음
        says, clips = narrate([f() for f in SOL_SLIDES + SLIDES], a.voice, a.check)
    report, secs = build(DST)
    for key, nclick, nnote, nkeys in report:
        flag = '' if nclick == nnote else '   ! 클릭 %d ≠ 노트 (클릭) %d' % (nclick, nnote)
        print('%-9s 클릭 %d%s' % (key, nclick, flag))
    print('→', DST, '%.1f MB' % (DST.stat().st_size / 1e6), '클릭 합계', sum(r[1] for r in report))
    if a.png:
        pngs = render_c.png(DST, OUT / 'png')
        labels = ['%d  %s' % (i + 1, r[0]) for i, r in enumerate(report)]
        sheet(pngs, OUT / '한눈에.png', labels)
        print('png', len(pngs))
    if a.video:
        auto = OUT / '_auto.pptx'
        mp4 = OUT / (DST.stem + '_미리보기.mp4')
        silent = OUT / '_silent.mp4' if a.tts else mp4      # 소리 없는 녹화는 남겨 둠(--remux로 낭독만 다시 얹을 수 있게)
        if not (a.remux and silent.exists()):
            _, secs = build(auto, auto=True, talk=True, says=says)
            print('미리보기 영상: 본문 %d장, %d:%02d' % (len(secs), sum(secs) // 60, sum(secs) % 60))
            print(render_c.video(auto, silent, secs))
            auto.unlink()
        if a.tts:
            add_voice(silent, mp4, says, clips)
            shutil.copyfile(mp4, DST.with_name(mp4.name))       # 낭독 영상은 덱 옆에도 둔다(저장소에 올려 바로 볼 수 있게. out/은 올리지 않음)


if __name__ == '__main__':
    main()
