#!/usr/bin/env python3
"""How it Works — _claude판 3차(2026-11-10) → ../HowItWorks_Argon_claude.pptx
솔루션 세 장(조각마다 하나씩 움직임) + How it Works 14장 + Appendix 14장(한눈에 보기 포함). 뱃지는 어느 장에도 없다.

  python build.py                 → ../HowItWorks_Argon_claude.pptx (발표용: 클릭마다 한 박자)
  python build.py --png           + out/png/s01.png… 와 out/한눈에.png (PowerPoint로 렌더, 정적 = 마지막 상태)
  python build.py --video         + out/HowItWorks_Argon_claude_미리보기.mp4 (클릭 효과도 저절로 나오는 사본을 PowerPoint로 녹화)
  python build.py --skip-blur     흐린 배경 그림(out/blur_*.png)을 다시 만들지 않음(있는 것을 씀)

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
                check_icon, chip, crop_fit, gallery, hl_band, line, magnifier, numdot, qbadge, scurve, search_pill, star4_icon,
                thread, topbar_prims, tw, vcurve, xmark)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / '11_중간본'))
import samsung_fonts  # noqa: E402

SRC = ROOT / '02_PPT' / 'Weave_결선.pptx'          # 원본 덱(읽기만): 장 틀과 노트 틀만 빌려 씀
LAYOUT_INDEX = 8                   # 중간본 조립(build_deck.py)과 같은 장 틀·노트 틀
DST = HERE.parent / 'HowItWorks_Argon_claude_argon.pptx'
OUT = HERE / 'out'
AS = HERE.parent / '장표5' / 'assets'   # 그림은 Argon판 것을 읽기만 함
SOLDIR = ROOT / '07_소스' / 'slides' / 'p05_결선' / 'out_claude_argon'      # 솔루션 조각 그림과 글상자(export_layers_claude.cjs)

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
}
WINE4 = ['babich', 'w3', 'w2', 'w1']          # 키워드·끊어진 고리 장의 와인 사진 넷(갤러리처럼 최신순, 첫째가 집들이 날)
BLUE, BLUE_HL, BLUE_BG = '4F7BFF', '7EA2FF', 'EEF3FF'    # 둘째 하위 질문 색(①은 보라, ②는 파랑)
ORANGE, ORANGE_HL, ORANGE_BG = 'E86C1A', 'F4A164', 'FFF4EB'  # 일반 임베딩 대비색(주황)


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


def band(name, pos, sub, kind='low', start=0, alpha=34):
    x, y, text, pt, wt = pos
    return hl_band(name, x, y, text, sub, pt, wt, start=start, kind=kind, alpha=alpha)


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
    stops = [(0, 'F6AD7B', 55), (60, 'FCD8BE', 18), (100, 'FFF8F3', 0)] if color == ORANGE else [
        (0, 'B9A2FF', 55), (60, 'D9CCFF', 18), (100, 'F8F5FF', 0)]
    return [R(name + '/glow', cx - r * 1.9, cy - r * 1.9, r * 3.8, r * 3.8, prst='ellipse', fill=None,
              grad=dict(stops=stops, path='circle', rect=(50, 50, 50, 50))),
            R(name + '/s', cx - r, cy - r, 2 * r, 2 * r, prst='star5', fill=color, line='FFFFFF', line_w=2)]


def mini_chip(name, x, y, kind, label, sub=None, pt=10.5, alpha=100, img=None):
    """임베딩 공간 속 기록 점: 아이콘 + 짧은 이름(+ 회색 한 줄). 돌려줌: (원시, 폭, 높이)."""
    h = 34 if not sub else 46
    if img:
        isz, pad_l, gap, pad_r = 30, 8, 8, 14
    else:
        isz, pad_l, gap, pad_r = 22, 12, 8, 14
    w = pad_l + isz + gap + max(tw(label, pt, 'b'), tw(sub, pt - 1.5) if sub else 0) + pad_r
    out = [R(name + '/bg', x, y, w, h, prst='roundRect', radius=12, fill='FFFFFF', line=LINE, line_w=1.0, shadow=SHADOW_SOFT,
             alpha=alpha, line_alpha=alpha)]
    if img:
        out.append(P(name + '/ic', img, x + pad_l, y + (h - isz) / 2, isz, isz, radius=6, crop=crop_fit(img, isz, isz), alpha=alpha))
    else:
        out.append(P(name + '/ic', ICON[kind], x + pad_l, y + (h - isz) / 2, isz, isz, alpha=alpha))
    tx = x + pad_l + isz + gap
    if sub:
        out.append(T(name + '/t', tx, y + 6, w - (tx - x), 18, label, size=pt, color=INK, weight='b', alpha=alpha))
        out.append(T(name + '/s', tx, y + 24, w - (tx - x), 16, sub, size=pt - 1.5, color=MUTE, alpha=alpha))
    else:
        out.append(T(name + '/t', tx, y, w - (tx - x), h, label, size=pt, color=INK, weight='b', anchor='ctr', alpha=alpha))
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


def clue_tag(name, x, y):
    """기록 칩 왼쪽 위 모서리에 붙는 '단서' 표(칩과 한 묶음이라 같이 움직임)."""
    w = tw('단서', 10, 'b') + 18
    return [R(name + '/bg', x - 9, y - 12, w, 22, prst='roundRect', fill=PURPLE, line='FFFFFF', line_w=1.6, shadow=SHADOW_SOFT),
            T(name + '/t', x - 9, y - 12, w, 22, '단서', size=10, color='FFFFFF', weight='b', align='c', anchor='ctr')]


# ------------------------------------------------------------------ 0. 솔루션 세 장: 조각마다 PowerPoint 묶음 하나(그림 + 글상자)
SOL_TITLE_Y = 46                                   # 뱃지·부제 없이 제목만(덱 머리 규격 29pt Bold)
SOL_DY = -14                                       # 뱃지가 빠진 만큼 내용 전체를 14px 위로(위아래 여백을 맞춤)
SOL_END = Xf(0, 0, 0, SOL_DY, 1.0)                 # 세 UX가 다 모인 마지막 자리(HTML 좌표 그대로, 위로 14px)
SOL_ONE = Xf(315, 416, 640, 404, 1.08)             # 1쪽: UX 1 묶음(기록 + 휴대폰)만 가운데에 조금 크게
SOL_MID = Xf(0, 279, 0, 416 + SOL_DY, 1.0)         # 2쪽: UX 2는 오른쪽 칸의 세로 가운데
SOL_Z = {                                          # 겹침 순서(아래 → 위)
    'ux1': ['th1', 'th2', 'th3', 'tm', 'tc', 'note0', 'arr', 'note', 'mail', 'cal', 'phone', 'call', 'swipe', 'sheet', 'go', 'q',
            'sum', 'sl1', 'sl2', 'sl3', 'ttl', 'r1', 'r2', 'r3', 'label'],
    'ux2': ['label', 'field', 'q', 'q2', 'kb', 'arrow', 'card', 'tap', 'pen', 'ok'],
    'ux3': ['label', 'gps', 'wallet', 'kb', 'arrow', 'card', 'glow', 'badge', 'tap', 'pen', 'ok'],
}
SOL_PHONE = ['phone', 'call', 'swipe', 'sheet', 'go', 'q', 'sum', 'ttl', 'r1', 'r2', 'r3']     # 1쪽에서 휴대폰과 함께 옮겨 가는 조각
SOL_Q1 = '삼성기술전 시연 내용'
SOL_NOTES = [
    '방금 영상으로 보신 세 가지 순간이 Weave가 제안하는 핵심 UX 세 가지입니다. '
    '첫째, 기록 통합 검색입니다. 선배와 통화하던 중 시연 내용을 확인해야 할 때, (클릭) 화면 하단을 쓱 밀어 올리면 검색 시트가 열립니다. '
    '(클릭) 여기에 삼성기술전 시연 내용이라고 입력하면, 노트의 최신 회의록과 민수님의 메일, 캘린더 일정을 한 번에 엮어 필요한 답만 바로 요약해 줍니다.',
    '둘째, 단서로 찾는 기억입니다. 집들이 때 마셨던 와인처럼 정확한 이름이 기억나지 않아도 떠오르는 단서만 적고 '
    '(클릭) 키보드의 실타래 버튼을 누르면, 카톡과 갤러리 사진을 이어 배비치 소비뇽 블랑이라는 이름을 찾아 검색창에 바로 채워 줍니다.',
    '셋째, 먼저 건네는 기억입니다. 귀국길 인천공항 면세점 근처에 도착하면 GPS 위치와 삼성 월렛 탑승권으로 지금 상황을 인식하고, '
    '(클릭) 실타래 버튼이 반짝이며 아내가 부탁했던 갈색병 메시지와 상품 링크를 찾아 보낼 답장까지 먼저 건넵니다. '
    '세 가지 경험 모두 별도 앱을 켤 필요 없이, 지금 보던 화면과 삼성 키보드 위에서 즉시 완결됩니다.',
]
_SOL = {}


def sol_data():
    if not _SOL:
        _SOL.update(json.loads((SOLDIR / 'layers.json').read_text(encoding='utf-8')))
    return _SOL


def sol_text(name, t):
    """HTML 글자 상자 하나 → 글상자."""
    px = t['size']
    lines = t['lines'] or [[]]
    x, y, w, h, lh = t['x'], t['y'], t['w'], t['h'], t['lh']
    if len(lines) == 1:
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


def sol_cursor(ans=False):
    x, y, w, h = sol_data()['geom']['q2_ans' if ans else 'q2']
    txt_ = '배비치 소비뇽 블랑' if ans else QUERY
    wt_ = 'b' if ans else 'r'
    key_ = 'sol/ux2/cur2' if ans else 'sol/ux2/cur'
    return R(key_, x + tw(txt_, 12.5 * 0.75, wt_) + 2, y + 2, 2, 14, fill=PURPLE, line=None)


def sol_rule(which):
    if which == 'v':
        return R('sol/rule_v', 611, 158, 1, 516, fill='D2C4FA', line=None)
    return R('sol/rule_h', 636, 416, 604, 1, fill='D2C4FA', line=None)


def sol_static(s, ux, xf=SOL_END):
    """이미 설명한 UX 묶음을 마지막 모습 그대로(효과 없음)."""
    for k in SOL_Z[ux]:
        if (ux, k) == ('ux2', 'q'):
            continue
        s.add('sol/%s/%s' % (ux, k), sol_piece('%s/%s' % (ux, k)), xf=xf)
        if (ux, k) == ('ux2', 'q2'):
            s.add('sol/ux2/cur2', [sol_cursor(ans=True)], xf=xf)


def s_sol1():
    """1쪽 기록 통합 검색: 통화 화면 → (클릭 1: 위로 올리기) 시트 올라옴 → (클릭 2: 한 단계로) 입력·이동·세 선 동시 연결·결과·요약."""
    s = Slide('sol1', trans=('fade', 500), bar=False, notes=SOL_NOTES[0])
    xf = SOL_ONE
    dxa = 640 - xf.X(454)                      # 처음(A)엔 휴대폰만 장표 가운데(640) → 기록이 이어질 때 제자리(B, 오른쪽)로
    s.add('sol/title', [sol_title()])

    def K(k):
        return 'sol/ux1/' + k
    for k in SOL_Z['ux1']:
        st = (dxa, 0) if k in SOL_PHONE else None   # label은 HTML 중심(315)에 있어 SOL_ONE에서 이미 정중앙(640)
        s.add(K(k), sol_piece('ux1/' + k), xf=xf, start=st)

    def enter(k, kind, t, dur=400, **kw):
        s.on(K(k), kind, t, dur, **kw)
        s.on(K(k), 'goto', t)

    # 0(장 열릴 때): 가운데 위 '1 기록 통합 검색' + 재웅 선배와 통화 중인 휴대폰
    s.on(K('label'), 'fade_in', 100, 400)
    enter('phone', 'fade_in', 150, 500)
    enter('call', 'fade_in', 150, 500)

    # 클릭 1: 위로 밀어 올리는 부분만 분리
    s.click()
    enter('swipe', 'wipe_in', 0, 420, dir='up')
    s.on(K('sheet'), 'fade_in', 340, 280)
    s.on(K('sheet'), 'move', 340, 460, dx=0, dy=-70, base=(dxa, 70), accel=0, decel=100000)
    enter('go', 'appear', 800, 1)

    # 클릭 2: 입력 → 기기 이동 & 기록 등장 → 세 선이 동시에 쭉쭉 빠르게 연결 → 연결된 기억 & 요약까지 한 단계로
    s.click()
    enter('q', 'type', 0, 1, ms=52, n=len(SOL_Q1))
    t = 52 * len(SOL_Q1)
    s.on(K('go'), 'pulse', t + 50, 120, scale=0.86)
    t += 180
    # 휴대폰이 오른쪽으로 이동하면서 동시에 왼쪽 기록들이 빠르게 등장
    s.on([K(k) for k in ('phone', 'call', 'swipe', 'sheet', 'go', 'q')], 'fly', t, 520, dx=dxa, dy=0, bend=0, show=False, fade=False)
    s.on(K('note0'), 'zoom_in', t + 100, 240, **{'from': 0.9})
    s.on(K('arr'), 'wipe_in', t + 240, 150, dir='down')
    s.on(K('note'), 'zoom_in', t + 320, 240, **{'from': 0.9})
    s.on(K('tm'), 'wipe_in', t + 440, 180, dir='down')
    s.on(K('mail'), 'zoom_in', t + 480, 220, **{'from': 0.8})
    s.on(K('tc'), 'wipe_in', t + 540, 180, dir='down')
    s.on(K('cal'), 'zoom_in', t + 580, 220, **{'from': 0.8})
    # 세 선(th1, th2, th3)이 동시에 쭉쭉 빠르게 나가며 연결!
    t_lines = t + 680
    for k in ('th1', 'th2', 'th3'):
        s.on(K(k), 'wipe_in', t_lines, 240)
    # 선이 닿자마자 연결된 기억(ttl, r1, r2, r3)과 요약 상자(sum, sl1~sl3)가 바로 완성
    t_res = t_lines + 180
    s.on(K('ttl'), 'fade_in', t_res, 200)
    for i, k in enumerate(('r1', 'r2', 'r3')):
        s.on(K(k), 'zoom_in', t_res + i * 70, 240, **{'from': 0.94})
    t_sum = t_res + 260
    s.on(K('sum'), 'fade_in', t_sum, 220)
    for i, k in enumerate(('sl1', 'sl2', 'sl3')):
        s.on(K(k), 'wipe_in', t_sum + 100 + i * 240, 340)
    return s


def sol_result(s, K, swap_q=False):
    """(2)(3) 공통: 실타래 버튼을 누름 → 화살표 → 추천 카드가 떠오름 → 입력하기 위 손."""
    s.on(K('tap'), 'zoom_in', 0, 260, **{'from': 1.3})
    s.on(K('tap'), 'pulse', 280, 120, scale=0.9)
    s.on(K('arrow'), 'wipe_in', 420, 280)
    s.on(K('card'), 'zoom_in', 640, 420, **{'from': 0.9})
    s.on(K('ok'), 'zoom_in', 1280, 260, **{'from': 1.3})
    s.on(K('ok'), 'pulse', 1560, 120, scale=0.9)
    if swap_q:
        s.on([K('q'), K('cur')], 'fade_out', 1700, 160)
        s.on([K('q2'), K('cur2')], 'fade_in', 1740, 220)


def s_sol2():
    """2쪽 단서로 찾는 기억: UX 1은 왼쪽으로(모핑) → 한 글자씩 입력(손가락 없음) → (클릭) 실타래 버튼 → 추천 카드 → 입력하기 누르면 검색창이 배비치 소비뇽 블랑으로 바뀜."""
    s = Slide('sol2', trans=('morph', 880), bar=False, notes=SOL_NOTES[1])
    s.add('sol/title', [sol_title()])
    sol_static(s, 'ux1')
    s.add('sol/rule_v', [sol_rule('v')], xf=SOL_END)

    def K(k):
        return 'sol/ux2/' + k
    for k in SOL_Z['ux2']:
        is_temp = (k == 'q')
        s.add(K(k), sol_piece('ux2/' + k), xf=SOL_MID, temp=is_temp)
        if k == 'q':
            s.add(K('cur'), [sol_cursor(ans=False)], xf=SOL_MID, temp=True)
        elif k == 'q2':
            s.add(K('cur2'), [sol_cursor(ans=True)], xf=SOL_MID)
    s.on('sol/rule_v', 'fade_in', 100, 400)
    s.on(K('label'), 'fade_in', 250, 400)
    s.on(K('field'), 'rise', 400, 450, dy=10)
    s.on(K('kb'), 'rise', 480, 450, dy=10)
    s.on(K('q'), 'jump', 950)
    s.on(K('q'), 'type', 950, 1, ms=58, n=len(QUERY))
    t = 950 + 58 * len(QUERY) + 60
    s.on(K('cur'), 'jump', t)
    s.on(K('cur'), 'appear', t, 1)
    s.on(K('cur'), 'blink', t + 30, 900)
    s.click()      # 1: 실타래 버튼 톡 → 추천 카드 → 입력하기 → 검색창 텍스트가 '배비치 소비뇽 블랑'으로 바뀜
    s.on(K('pen'), 'zoom_in', 220, 260, **{'from': 0.6})
    sol_result(s, K, swap_q=True)
    return s


def s_sol3():
    """3쪽 먼저 건네는 기억: UX 2는 오른쪽 위로(모핑) → 위치(GPS) → 탑승권(삼성 월렛) → 실타래 버튼에 알림 → (클릭) 추천 카드."""
    s = Slide('sol', trans=('morph', 880), bar=False, notes=SOL_NOTES[2])
    s.add('sol/title', [sol_title()])
    sol_static(s, 'ux1')
    s.add('sol/rule_v', [sol_rule('v')], xf=SOL_END)
    sol_static(s, 'ux2')
    s.add('sol/rule_h', [sol_rule('h')], xf=SOL_END)

    def K(k):
        return 'sol/ux3/' + k
    for k in SOL_Z['ux3']:
        s.add(K(k), sol_piece('ux3/' + k), xf=SOL_END)
    s.on('sol/rule_h', 'fade_in', 100, 400)
    s.on(K('label'), 'fade_in', 250, 400)
    s.on(K('kb'), 'rise', 400, 450, dy=10)
    s.on(K('gps'), 'zoom_in', 950, 350, **{'from': 0.8})                 # GPS 위치
    s.on(K('wallet'), 'zoom_in', 1500, 350, **{'from': 0.8})             # 삼성 월렛 탑승권
    s.on(K('glow'), 'zoom_in', 2150, 420, **{'from': 0.5})               # 알림: 실타래 버튼이 켜지고
    s.on(K('badge'), 'zoom_in', 2400, 300, **{'from': 0.3})              # 빨간 1
    s.on(K('pen'), 'zoom_in', 2350, 300, **{'from': 0.6})                # 반짝!
    s.on(K('glow'), 'pulse', 2700, 180, scale=1.12)
    s.click()      # 1: 켜진 버튼을 누름 → 추천 카드
    sol_result(s, K, swap_q=False)
    return s


SOL_SLIDES = [s_sol1, s_sol2, s_sol3]


# ------------------------------------------------------------------ 0. 솔루션 → How it works?
def s_hiw():
    s = Slide('hiw', trans=('fade', 500), bar=False,
              notes='그렇다면 Weave는 어떻게 단어 하나 겹치지 않는 흩어진 기록들을 찾아 이어 붙일까요? '
                    '두 번째 집들이 와인 시나리오로 그 동작 원리를 따라가 보겠습니다.')
    s.add('bg/blur', [P('bg/blur', str(OUT / 'blur_sol.png'), 0, 0, 1280, 720)])
    s.add('hiw/big', [caption('hiw/big', [[('How it ', INK), ('works?', PURPLE)]], 640, 300, size=80)])
    s.on('hiw/big', 'rise', 120, 450, dy=10)
    return s


# ------------------------------------------------------------------ 1. 질문
PHONE = (100, 110, 636, 706)


def phone_prims(key, alpha=100):
    x, y, w, h = PHONE
    gw = 230
    gh = gw * 276 / 816
    return [R(key + '/body', x, y, w, h, prst='roundRect', radius=64, fill='FFFFFF', line=LINE2, line_w=1.6, shadow=SHADOW_LIFT),
            R(key + '/notch', x + w / 2 - 56, y + 22, 112, 14, prst='roundRect', fill='ECE8F4', line=None),
            P(key + '/g', ICON['google'], x + w / 2 - gw / 2, y + 92, gw, gh)]


def s_ask():
    s = Slide('ask', trans=('morph', 1000), bar=False,
              notes='지은이네 집들이 때 마셨던 와인이 맛있어서 다시 사려는데, 정확한 이름이 도무지 떠오르지 않습니다. '
                    '구글 검색창에 지은이네 집들이 때 마셨던 와인이라고 적어 보지만 막막하기만 하죠.')
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


# ------------------------------------------------------------------ 2. 흩어진 단서 (6p: 본문 텍스트 34 -> 40pt)
FLOATS = [
    ('f_note1', 'note', '지은이네 주소', '경기도 수원시 영통구…', 414, 108, 1.0, 72),
    ('f_note2', 'note', '장 볼 것', '우유, 계란, 휴지', 706, 58, 0.9, 42),
    ('f_talk4', 'talk', '택배', '문 앞에 두고 갔어요', 790, 170, 0.86, 36),
    ('f_mail1', 'mail', '관리비 고지서', '2월분 관리비', 56, 292, 0.95, 46),
    ('f_cal3', 'cal', '팀 회식', '3/20 (금) 19:00', 52, 404, 0.92, 42),
    ('f_talk3', 'talk', '엄마', '반찬 보냈다', 88, 514, 0.9, 42),
    ('f_mail2', 'mail', '[예약 확인] 오사카 호텔', '2월 27일', 56, 622, 0.86, 36),
    ('f_note3', 'note', '소믈리에 추천', '카베르네 소비뇽', 548, 432, 1.0, 54),
    ('f_phone', 'phone', '부재중 전화', '어제 오후 3:12', 778, 434, 0.86, 34),
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


def cloud_cards():
    """큰 카드 셋(지은 카톡, 그날 와인 사진, 다른 날 와인 사진)."""
    tw_ = card_fit(CL_TALK[0], CL_TALK[1], CL_TALK[2], pt=12.5, title_pt=15, meta_pt=10.5, bubble=True)
    talk = card('cl_talk', 'talk', 60, 80, tw_, CL_TALK[0], CL_TALK[1], CL_TALK[2], pt=12.5, title_pt=15, meta_pt=10.5)
    photo = card('cl_photo', 'photo', 984, 68, 244, '갤러리', '3월 15일 (일) 20:14', img=PH['babich'][0], img_h=142,
                 img_focus=PH['babich'][2], title_pt=15, meta_pt=10.5)
    photo2 = card('cl_photo2', 'photo', 308, 452, 204, '갤러리', '2025. 9. 27', img=PH['w2'][0], img_h=104, img_focus=PH['w2'][2],
                  title_pt=15, meta_pt=10.5)
    return [('cl_photo2', photo2, (308, 452, 204), 62), ('cl_talk', talk, (60, 80, tw_), 72), ('cl_photo', photo, (984, 68, 244), 72)]


def s_cloud():
    s = Slide('cloud', trans=('morph', 900), bar=False,
              notes='사실 정답은 분명 내 기기 안에 있습니다. (클릭) 다만 집들이 날짜는 카카오톡 대화에, 와인 라벨은 갤러리 사진에, '
                    '서로 다른 앱에 파편처럼 흩어져 있을 뿐입니다.')
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
    if PASS1:
        return s
    s.add('cl/blur', [P('cl/blur', str(OUT / 'blur_cloud.png'), 0, 0, 1280, 720)])
    s.add('cl_t1', [caption('cl_t1', [[('정답은 분명 ', INK), ('기기 안', PURPLE), ('에', INK)]], 640, 302, size=40)], temp=True)
    s.add('cl_t2', [caption('cl_t2', [[('그러나, ', INK), ('여러 앱에 흩어져 있는 단서들', PURPLE)]], 640, 302, size=40)])
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
    s = Slide('old', trans=('fade', 600), bar=False,
              notes='이 질문을 기존 검색 방식으로 찾으면 어떻게 될까요?')
    s.add('old/title', [old_title(300, 56)])
    s.on('old/title', 'pop', 0, 650, **{'from': 0.7, 'over': 1.05})
    return s


# 키워드 장의 자리 (8p: BM25 뱃지 + X 표시와 함께 보충 사유 태그 등장)
OLD_Y = 72
KW_PANEL = (370, 132, 540, 124)
KW_FIELD = (392, 182, 496, 54)
KW_PT, KW_TPT, KW_MPT = 12, 14.5, 10.5
KW_CARDS = [    # (종류, 제목, 앱 · 날짜, 본문, 겹친 단어, X 사유)
    ('note', '지은이네 주소', '삼성노트 · 2025. 9. 2', ['경기도 수원시 영통구 매탄로 77', '푸른숲아파트 103동 1204호'], '지은이네', '관련 없는 집 주소'),
    ('cal', '성빈이 신혼집들이', '캘린더 · 2025. 10. 18 (토)', ['오후 6:00  성빈이네'], '집들이', '다른 사람의 집들이'),
    ('wallet', '와인앤모어 성수점', '삼성 월렛 · 2025. 12. 24', ['결제 38,000원'], '와인', '다른 날의 결제 내역'),
]
KW_Y = 330
KW_GAL = (375, 494, 530)


def gray_badge(name, x, y, text, pt=10.5, h=24, padx=10):
    w = tw(text, pt, 'b') + 2 * padx
    return [R(name + '/bg', x, y, w, h, prst='roundRect', fill='F1EFF7', line='D9D4E8', line_w=1.0),
            T(name + '/t', x, y, w, h, text, size=pt, color=SUB, weight='b', align='c', anchor='ctr')], w


def kw_layout():
    ws = [card_fit(t, m, ls, pt=KW_PT, title_pt=KW_TPT, meta_pt=KW_MPT, slack=14) for _, t, m, ls, _, _ in KW_CARDS]
    gap = 22
    x = 640 - (sum(ws) + gap * (len(ws) - 1)) / 2
    xs = []
    for w in ws:
        xs.append(x)
        x += w + gap
    return xs, ws


def kw_parts(dimmed=()):
    px, py, pw, ph = KW_PANEL
    fx, fy, fw, fh = KW_FIELD
    bm_chip, _ = gray_badge('kw/panel/bm', px + 24 + tw('키워드 검색', 16, 'b') + 10, py + 15, 'BM25')
    parts = [('kw/panel', [R('kw/panel/bg', px, py, pw, ph, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.4,
                             shadow=SHADOW_CARD),
                           T('kw/panel/l', px + 24, py + 13, 200, 28, '키워드 검색', size=16, color=INK, weight='b')] + bm_chip +
                          [R('kw/panel/f', fx, fy, fw, fh, prst='roundRect', fill='F7F5FC', line=LINE, line_w=1.0)])]
    qpt = 16.5
    S = qpt * 4 / 3
    qx, qy = fx + 20, fy + (fh - S * 1.2) / 2
    parts.append(('kw/q', [T('kw/q', qx, qy, fw - 30, S * 1.3, QUERY, size=qpt, color=INK)]))
    qpos = (qx, qy, QUERY, qpt, 'r')
    bands = [band('kw/h%d' % (i + 1), qpos, c[4]) for i, c in enumerate(KW_CARDS)]
    for i, b in enumerate(bands):
        parts.append(('kw/h%d' % (i + 1), [b]))
    xs, ws = kw_layout()
    cards = [card('kw/c%d' % (i + 1), c[0], xs[i], KW_Y, ws[i], c[1], c[2], c[3], bubble=False, pt=KW_PT, title_pt=KW_TPT, meta_pt=KW_MPT)
             for i, c in enumerate(KW_CARDS)]
    boxes = {}
    for i, c in enumerate(cards):
        k = 'kw/c%d' % (i + 1)
        parts.append((k, c[0]))
        boxes[k] = (xs[i], KW_Y, ws[i], c[1])
    for i, c in enumerate(cards):
        parts.append(('kw/m%d' % (i + 1), [band('kw/m%d' % (i + 1), c[2]['title'], KW_CARDS[i][4])]))
    for i, b in enumerate(bands):
        x, y, w, h = boxes['kw/c%d' % (i + 1)]
        parts.append(('kw/t%d' % (i + 1), thread('kw/t%d' % (i + 1), vcurve((b[2] + b[4] / 2, py + ph - 2), (x + w / 2, y + 2), 0.55), w=2.4)))
    for i in range(3):
        x, y, w, h = boxes['kw/c%d' % (i + 1)]
        parts.append(('kw/x%d' % (i + 1), xmark('kw/x%d' % (i + 1), x + w / 2, y + h / 2 - 4, s=42)))
        parts.append(('kw/rx%d' % (i + 1), tag_red('kw/rx%d' % (i + 1), x + w / 2, y + h - 14, KW_CARDS[i][5], pt=10.5)))
    gx, gy, gw = KW_GAL
    g = gallery('kw/gal', gx, gy, gw, [PH[k] for k in WINE4], cols=4, ph=94, date_pt=10)
    parts.append(('kw/gal', g[0]))
    boxes['kw/gal'] = (gx, gy, gw, g[1])
    parts.append(('kw/x4', xmark('kw/x4', gx + gw / 2, gy + g[1] / 2 - 6, s=50)))
    parts.append(('kw/rx4', tag_red('kw/rx4', gx + gw / 2, gy + g[1] - 14, '사진 속 의미는 검색 불가', pt=10.5)))
    return parts, boxes


def kw_small():
    _, boxes = kw_parts()
    x0 = min(KW_PANEL[0], min(b[0] for b in boxes.values()))
    x1 = max(KW_PANEL[0] + KW_PANEL[2], max(b[0] + b[2] for b in boxes.values()))
    y0, y1 = KW_PANEL[1], max(b[1] + b[3] + 14 for b in boxes.values())
    s = min(0.8, 552 / (x1 - x0))
    return Xf(ax=x0, ay=y0, bx=36 + (552 - (x1 - x0) * s) / 2, by=404 - (y1 - y0) * s / 2, s=s)


KW_KEYS = ['kw/t1', 'kw/t2', 'kw/t3', 'kw/c1', 'kw/c2', 'kw/c3', 'kw/gal', 'kw/panel', 'kw/q', 'kw/m1', 'kw/m2', 'kw/m3',
           'kw/h1', 'kw/h2', 'kw/h3', 'kw/x1', 'kw/x2', 'kw/x3', 'kw/x4', 'kw/rx1', 'kw/rx2', 'kw/rx3', 'kw/rx4']


def s_kw():
    s = Slide('kw', trans=('morph', 900), bar=False,
              notes=('먼저 BM25 같은 키워드 검색입니다. 질문 속 글자가 그대로 들어간 기록만 찾죠. '
                    '(클릭) 지은이네로는 삼성노트의 주소 메모가 나오지만 (클릭) 와인 내용은 없는 단순 집 주소입니다. '
                    '(클릭) 집들이로는 캘린더 일정이 나오지만 (클릭) 성빈이라는 다른 사람의 집들이입니다. '
                    '(클릭) 와인으로는 월렛 결제 내역이 나오지만 (클릭) 작년 연말에 결제한 다른 날의 내역입니다. '
                    '(클릭) 무엇보다 갤러리 사진들은 (클릭) 사진 속 의미를 키워드로 파악할 수조차 없어 아예 검색되지 않습니다.'))
    s.add('old/title', [old_title(OLD_Y, 30)])
    parts, _ = kw_parts()
    pm = dict(parts)
    for k in KW_KEYS:
        s.add(k, pm[k])
    s.on('kw/panel', 'rise', 100, 500, dy=14)
    s.on('kw/q', 'fade_in', 300, 400)
    for n in (1, 2, 3):
        s.click()
        s.on('kw/h%d' % n, 'wipe_in', 0, 380)
        s.on('kw/t%d' % n, 'wipe_in', 300, 450, dir='down')
        s.on('kw/c%d' % n, 'rise', 650, 450, dy=14)
        s.on('kw/m%d' % n, 'wipe_in', 1000, 300)
        s.click()
        s.on(['kw/x%d' % n, 'kw/rx%d' % n], 'zoom_in', 0, 300, **{'from': 0.8})
        s.on(['kw/c%d' % n, 'kw/m%d' % n], 'dim', 0, 350, to=0.45)
    s.click()
    s.on('kw/gal', 'rise', 0, 450, dy=14)
    s.click()
    s.on(['kw/x4', 'kw/rx4'], 'zoom_in', 0, 300, **{'from': 0.8})
    s.on('kw/gal', 'dim', 0, 350, to=0.45)
    return s


# 임베딩 장 (9p: One-hop 뱃지, 소믈리에 추천 메모 + 와인 사진 2장, 지은 카톡 단서 힌트, 사유 X 태그)
EM_PANEL = (624, 132, 600, 124)
EM_FIELD = (646, 182, 556, 54)
SPACE = (624, 314, 600, 330)
STAR = (868, 492)


def s_emb():
    s = Slide('emb', trans=('morph', 1000), bar=False,
              notes=('그렇다면 의미를 이해한다는 One-hop 임베딩 검색은 어떨까요? '
                    '(클릭) 질문 전체를 하나의 벡터로 바꿔서 (클릭) 기록들이 놓인 임베딩 공간에서 (클릭) 질문과 가장 가까운 기록을 찾습니다. '
                    '(클릭) 하지만 와인이라는 표면적인 의미에 끌려 소믈리에 추천 메모나 다른 날 마신 와인 사진만 가까이에 잡히고, '
                    '정작 집들이 날짜가 적힌 지은이의 카톡은 와인 이야기가 없어 멀리 떨어져 있습니다.'))
    s.add('old/title', [old_title(OLD_Y, 30)])
    parts, _ = kw_parts()
    pm = dict(parts)
    small = kw_small()
    for k in KW_KEYS:
        s.add(k, pm[k], alpha=24 if k.startswith(('kw/c', 'kw/m', 'kw/gal')) else 40, xf=small)
    s.add('em/div', [line('em/div', (602, 170), (602, 640), color='E2DBF5', w=1.4)])
    px, py, pw, ph = EM_PANEL
    fx, fy, fw, fh = EM_FIELD
    oh_chip, _ = gray_badge('em/panel/oh', px + 24 + tw('임베딩 검색', 16, 'b') + 10, py + 15, 'One-hop')
    s.add('em/panel', [R('em/panel/bg', px, py, pw, ph, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.4,
                         shadow=SHADOW_CARD),
                       T('em/panel/l', px + 24, py + 13, 200, 28, '임베딩 검색', size=16, color=INK, weight='b')] + oh_chip +
                      [R('em/panel/f', fx, fy, fw, fh, prst='roundRect', fill='F7F5FC', line=LINE, line_w=1.0)])
    qpt = 16.5
    S = qpt * 4 / 3
    qx, qy = fx + 20, fy + (fh - S * 1.2) / 2
    s.add('em/hl', [hl_band('em/hl', qx, qy, QUERY, QUERY, qpt, kind='low', alpha=36)])
    s.add('em/q', [T('em/q', qx, qy, fw - 30, S * 1.3, QUERY, size=qpt, color=INK)])
    vy = 268
    vec = '[0.80, 0.30, −0.83, 0.90, −0.02, …]'
    s.add('em/vt', thread('em/vt', [(qx + tw(QUERY, qpt) / 2, fy + fh + 2), (qx + tw(QUERY, qpt) / 2, vy - 4)], w=2.2))
    s.add('em/vl', [T('em/vl', px + 24, vy, 60, 30, '벡터', size=13.5, color=PURPLE, weight='b', anchor='ctr')])
    s.add('em/vec', [T('em/vec', px + 84, vy, 460, 30, vec, size=15.5, color=PURPLE, weight='m', anchor='ctr')])
    sx, sy, sw, sh_ = SPACE
    s.add('em/space', [R('em/space/bg', sx, sy, sw, sh_, prst='roundRect', radius=20, fill='FFFFFF', alpha=86, line=LINE2, line_w=1.2),
                       T('em/space/l', sx + 18, sy + 12, 200, 24, '임베딩 공간', size=12, color=PURPLE, weight='b'),
                       T('em/space/fn', sx + sw - 260, sy + sh_ - 24, 244, 18, '* 가까울수록 질문과 의미적으로 가까운 기록', size=9.5, color=SUB, align='r')])
    rnd = random.Random(11)
    dots = []
    for i in range(30):
        while True:
            x_, y_ = sx + 24 + rnd.random() * (sw - 48), sy + 46 + rnd.random() * (sh_ - 70)
            if abs(x_ - STAR[0]) > 45 or abs(y_ - STAR[1]) > 45:
                break
        r_ = 3.2 + rnd.random() * 2.4
        dots.append(R('em/dot%d' % i, x_ - r_, y_ - r_, 2 * r_, 2 * r_, prst='ellipse', fill='CBC0EC', alpha=80, line=None))
    s.add('em/dots', dots)
    s.add('em/near', [R('em/near', STAR[0] - 148, STAR[1] - 112, 316, 224, prst='ellipse', fill=None, line=PURPLE2, line_w=1.8,
                        dash='dash')])
    far = [('em/r_mail', 'mail', '관리비 고지서', sx + 20, sy + 42), ('em/r_cal', 'cal', '팀 회식', sx + 458, sy + 46),
           ('em/r_talk2', 'talk', '택배', sx + 24, sy + 266), ('em/r_note', 'note', '지은이네 주소', sx + 422, sy + 246)]
    for k, kind, label, x_, y_ in far:
        prims, w_, h_ = mini_chip(k, x_, y_, kind, label, pt=11.5, alpha=70)
        s.add(k, prims)
    # 지은 카톡: 멀리 떨어져 있지만 '단서' 태그 힌트가 붙어 있음
    jx, jy = sx + 486, sy + 142
    j_prims, jw, jh = mini_chip('em/r_jieun', jx, jy, 'talk', '지은', pt=11.5, alpha=88)
    s.add('em/r_jieun', j_prims + clue_tag('em/r_jieun/tag', jx, jy))
    # 원 안 가까운 기록: 왼쪽 '소믈리에 추천' 메모 + 오른쪽 와인 사진 2장(레드/화이트)
    mx, my = STAR[0] - 196, STAR[1] - 42
    memo, mw, mh = mini_chip('em/r_memo', mx, my, 'note', '소믈리에 추천', '카베르네 소비뇽', pt=11.5)
    p1x, p1y = STAR[0] + 36, STAR[1] - 68
    p2x, p2y = STAR[0] + 36, STAR[1] - 10
    pic1, pw1, ph1 = mini_chip('em/r_pic1', p1x, p1y, 'gallery', '와인 사진', '2026. 1. 9', pt=11.5, img=PH['glass'][0])
    pic2, pw2, ph2 = mini_chip('em/r_pic2', p2x, p2y, 'gallery', '화이트 와인', '2025. 9. 27', pt=11.5, img=PH['w2'][0])
    s.add('em/r_memo', memo)
    s.add('em/r_pic1', pic1)
    s.add('em/r_pic2', pic2)
    s.add('em/star', star('em/star', *STAR) + [T('em/star/l', STAR[0] - 30, STAR[1] + 18, 60, 20, '질문', size=10.5, color=PURPLE,
                                                 weight='b', align='c')])
    memo_box = (mx, my, mw, mh)
    pic1_box = (p1x, p1y, pw1, ph1)
    pic2_box = (p2x, p2y, pw2, ph2)
    s.add('em/k1', [ring_box('em/k1', memo_box, pad=4, radius=14, w=2.2)])
    s.add('em/k2', [ring_box('em/k2', pic1_box, pad=4, radius=14, w=2.2)])
    s.add('em/k3', [ring_box('em/k3', pic2_box, pad=4, radius=14, w=2.2)])
    s.add('em/x1', tag_red('em/x1', mx + mw / 2, my + mh + 8, '관련 없는 메모', pt=10.5))
    mid_px = p1x + max(pw1, pw2) / 2
    mid_py = (p1y + p2y + ph2) / 2 - 14
    s.add('em/x2', tag_red('em/x2', mid_px, mid_py, '다른 날 마신 와인', pt=10.5))
    # 효과
    s.on('em/div', 'fade_in', 200, 400)
    s.on('em/panel', 'rise', 300, 500, dy=14)
    s.on('em/q', 'fade_in', 500, 400)
    s.click()   # 1: 질문 전체 → 벡터
    s.on('em/hl', 'wipe_in', 0, 650)
    s.on('em/vt', 'wipe_in', 550, 300, dir='down')
    s.on('em/vl', 'fade_in', 800, 250)
    s.on('em/vec', 'type', 850, 1, ms=26, n=len(vec))
    s.click()   # 2: 기록이 놓인 공간이 펼쳐짐
    s.on('em/space', 'zoom_in', 0, 500, **{'from': 0.94})
    s.on('em/dots', 'fade_in', 250, 500)
    for i, k in enumerate(['em/r_memo', 'em/r_pic1', 'em/r_pic2', 'em/r_jieun', 'em/r_note', 'em/r_cal', 'em/r_mail', 'em/r_talk2']):
        s.on(k, 'zoom_in', 350 + i * 80, 380, **{'from': 0.7})
    s.click()   # 3: 질문 별이 공간에 앉고 가장 가까운 기록들
    vx_, vy_ = px + 84 + tw(vec, 15.5) / 2, vy + 15
    s.on('em/star', 'fly', 0, 800, dx=vx_ - STAR[0], dy=vy_ - STAR[1], bend=0.12)
    s.on('em/near', 'zoom_in', 750, 450, **{'from': 0.4})
    s.on(['em/k1', 'em/k2', 'em/k3'], 'zoom_in', 1150, 350, **{'from': 1.12})
    s.click()   # 4: 관련 없는 메모 X → 두 와인 사진 동시에 흐려지며 가운데 '다른 날 마신 와인 X'
    s.on(['em/r_memo', 'em/k1'], 'dim', 0, 320, to=0.4)
    s.on('em/x1', 'zoom_in', 80, 280, **{'from': 0.8})
    s.on(['em/r_pic1', 'em/r_pic2', 'em/k2', 'em/k3'], 'dim', 480, 350, to=0.38)
    s.on('em/x2', 'zoom_in', 560, 300, **{'from': 0.8})
    return s


# ------------------------------------------------------------------ 4. Let's think step by step → 끊어진 고리 (10p, 11p)
def step_title(y, size):
    return caption('step/title', [[("Let's think ", INK), ('step by step!', PURPLE)]], 640, y, size=size)


def s_step():
    s = Slide('step', trans=('fade', 600), bar=False,
              notes='한 번의 검색으로 닿지 않는다면, 사람처럼 한 단계씩 단서를 이어가며 생각해야 합니다.')
    s.add('bg/blur', [P('bg/blur', str(OUT / 'blur_emb.png'), 0, 0, 1280, 720)])
    s.add('step/title', [step_title(306, 62)])
    s.on('step/title', 'pop', 200, 700, **{'from': 0.62, 'over': 1.06})
    return s


GAP = (448, 256, 384, 206)
CH_GAL = (874, 228, 360)


def chain_talk(x, y, w=356):
    return card('ch/talk', 'talk', x, y, w, '지은', '카카오톡 · 3월 15일 (일) 오후 4:12', ['박스 정리 다 했어! 이따 올 때', '휴지 안 사 와도 돼'],
                pt=12.5, title_pt=14)


def s_chain():
    """11p: 처음엔 질문 → ? → 흐린 와인 사진 4장. 클릭하면 가운데 지은 카톡(보라 형광 강조)이 뜨고, 갤러리 첫 사진이 선명해지며 보라 테두리 + 오른쪽 위 배비치 소비뇽 블랑 뱃지 + 하단 질문 등장."""
    s = Slide('chain', trans=('morph', 1000), bar=False,
              notes='질문과 갤러리 속 와인 사진 사이에는 집들이 날짜라는 중간 고리가 빠져 있습니다. '
                    '(클릭) 지은이의 카카오톡에서 3월 15일이 집들이 날이었다는 단서를 먼저 찾고, 그날 찍은 사진에서 배비치 소비뇽 블랑을 찾아야 합니다. '
                    '이 중간 단서를 Weave는 어떻게 찾아낼까요?')
    s.add('step/title', [step_title(OLD_Y, 30)])
    pill, txt, _, _ = search_pill('ch/sp', 46, 336, 360, 60, QUERY, pt=14.5, icon='spool', cursor=False)
    s.add('ch/sp', pill + [txt])
    gx, gy, gw, gh = GAP
    s.add('ch/gap', [R('ch/gap/bg', gx, gy, gw, gh, prst='roundRect', radius=24, fill=LAV2, alpha=80, line=PURPLE2, line_w=2.2,
                       dash='dash'),
                     T('ch/gap/q', gx, gy, gw, gh, '?', size=78, color=PURPLE, weight='b', align='c', anchor='ctr')], temp=True)
    # 클릭 시 가운데에 나타날 지은 카톡 단서 카드 + 보라색 형광 강조
    tk_w = card_fit('지은', '카카오톡 · 3월 15일 (일) 오후 4:12', ['박스 정리 다 했어! 이따 올 때', '휴지 안 사 와도 돼'], pt=12.5, title_pt=14, bubble=True)
    tk_x = gx + (gw - tk_w) / 2
    talk_h = chain_talk(0, 0, tk_w)[1]
    tk_y = gy + (gh - talk_h) / 2
    talk = chain_talk(tk_x, tk_y, tk_w)
    tp = talk[2]
    s.add('ch/talk', talk[0])
    s.add('ch/th1', [band('ch/th1', tp[0], '박스 정리')])
    s.add('ch/th2', [band('ch/th2', tp[1], '휴지 안 사 와도 돼')])
    s.add('ch/thd', [band('ch/thd', tp['meta'], '3월 15일 (일)', alpha=45)])

    cx_, cy_, cw_ = CH_GAL
    gal = gallery('ch/gal', cx_, cy_, cw_, [PH[k] for k in WINE4], cols=2, show_dates=False, ph=104, gap=10)
    s.add('ch/gal', gal[0])
    spots = gal[2]
    a1, b1 = (46 + 360, 366), (gx, gy + gh / 2)
    a2, b2 = (gx + gw, gy + gh / 2), (cx_, cy_ + gal[1] / 2)
    s.add('ch/l1', [C('ch/l1', scurve(a1, b1), w=2.2, color='C9BEEB', dash='dash')])
    s.add('ch/l2', [C('ch/l2', scurve(a2, b2), w=2.2, color='C9BEEB', dash='dash')])
    wi = WINE4.index('babich')
    # 처음엔 4장 모두 흐리게: 1번 사진(babich) 흐림막은 temp=True여서 클릭 시 걷힘
    s.add('ch/dim0', [dim_over('ch/dim0', spots[wi], radius=10, alpha=68)], temp=True)
    s.add('ch/dim', [dim_over('ch/dim%d' % i, sp, radius=10, alpha=68) for i, sp in enumerate(spots) if i != wi])
    s.add('ch/pring', [ring_box('ch/pring', spots[wi], pad=4, radius=12, w=3.0)])
    # 오른쪽 위에 배비치 소비뇽 블랑 뱃지
    ans_w = tw('배비치 소비뇽 블랑', 12.5, 'b') + 30
    ans, _ = chip('ch/ans', cx_ + cw_ - ans_w / 2 - 4, cy_ - 14, '배비치 소비뇽 블랑', 'fill', pt=12.5, h=32, padx=15, align='c')
    s.add('ch/ans', ans)
    s.add('ch/bridge', [caption('ch/bridge', [[('이 중간 단서를 ', INK), ('Weave는 어떻게 찾아낼까요?', PURPLE)]], 640, 600, size=26)])

    s.on('ch/sp', 'rise', 150, 500, dy=14)
    s.on('ch/l1', 'wipe_in', 450, 400)
    s.on('ch/gap', 'jump', 600)
    s.on('ch/gap', 'rise', 600, 500, dy=14)
    s.on('ch/l2', 'wipe_in', 900, 400)
    s.on('ch/dim0', 'jump', 1050)
    s.on(['ch/gal', 'ch/dim0', 'ch/dim'], 'rise', 1050, 500, dy=14)
    s.click()   # 클릭 1: 가운데 지은 카톡(보라 형광) + 갤러리 보라 테두리 & 오른쪽 위 배비치 소비뇽 블랑 뱃지 + 하단 문구
    s.on('ch/gap', 'fade_out', 0, 250)
    s.on('ch/talk', 'zoom_in', 150, 450, **{'from': 0.88})
    s.on('ch/th1', 'wipe_in', 500, 320)
    s.on('ch/th2', 'wipe_in', 700, 380)
    s.on('ch/thd', 'wipe_in', 950, 320)
    s.on('ch/dim0', 'fade_out', 1050, 300)
    s.on('ch/pring', 'zoom_in', 1100, 360, **{'from': 1.12})
    s.on('ch/ans', 'zoom_in', 1300, 340, **{'from': 0.85})
    s.on('ch/bridge', 'rise', 1500, 480, dy=14)
    return s


# ------------------------------------------------------------------ 5. 00 데이터 색인 (12p: '기록이 쌓이는 대로, ' + '원문')
IDX_Y, IDX_H = 248, 300
IDX_ORIG = '박스 정리 다 했어! 이따 올 때 휴지 안 사 와도 돼'
IDX_VEC = '[0.86, −0.08, 0.33, 0.46, 0.60, 0.83, 0.90, …]'
IDX_META = '{ date: "2026-03-15", app: "kakaotalk", from: "지은", … }'


def s_idx():
    s = Slide('idx', trans=('morph', 1000), cur='00',
              notes='먼저 00단계, 데이터 색인입니다. 기록이 쌓이는 대로 기기 안에서 미리 색인해 둡니다. '
                    '(클릭) 원문과 함께 문장의 의미는 벡터로, 날짜와 앱, 보낸 사람 같은 정보는 메타데이터로 구조화해 Hybrid Index에 저장합니다.')
    s.add('idx/cap', [caption('idx/cap', [[('기록이 쌓이는 대로, ', INK), ('미리 색인', PURPLE), ('해 둡니다', INK)]], 640, 92, size=25)])
    lab_w = 124
    tk_w = card_fit('지은', '카카오톡 · 3월 15일 (일) 오후 4:12', ['박스 정리 다 했어! 이따 올 때', '휴지 안 사 와도 돼'], pt=12.5, title_pt=14,
                    bubble=True)
    w = round(30 + lab_w + max(tw(IDX_ORIG, 14), tw(IDX_VEC, 15.5, 'm'), tw(IDX_META, 15.5, 'm')) + 34)
    gap = 80
    x0 = 640 - (tk_w + gap + w) / 2
    x, y, h = x0 + tk_w + gap, IDX_Y, IDX_H
    cy = y + h / 2
    talk = chain_talk(x0, cy - chain_talk(0, 0, tk_w)[1] / 2, tk_w)
    s.add('ch/talk', talk[0])
    s.add('idx/arr', thread('idx/arr', scurve((x0 + tk_w + 3, cy), (x - 4, cy)), w=2.6))
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
    s.add('idx/r2', [T('idx/r2', vx, rows_y[2], w - 170, 34, IDX_META, size=15.5, color=INK, weight='m', anchor='ctr')])
    s.on('idx/card', 'rise', 250, 550, dy=14)
    s.on('idx/arr', 'wipe_in', 500, 450)
    s.on(['idx/l0', 'idx/r0'], 'fade_in', 750, 400)
    s.click()
    s.on('idx/l1', 'fade_in', 150, 300)
    s.on('idx/r1', 'type', 250, 1, ms=24, n=len(IDX_VEC))
    s.on('idx/l2', 'fade_in', 1300, 300)
    s.on('idx/r2', 'type', 1400, 1, ms=22, n=len(IDX_META))
    return s


# ------------------------------------------------------------------ 6. 01 상황 인식 · 02 질의 재작성 (13p, 14p)
TR_SP = (668, 176, 548, 70)
KB = (668, 266, 548, 337)
SPOOL = (KB[0] + 102 * KB[2] / 1300, KB[1] + 82 * KB[3] / 800)
HAND_H = 128


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
    out.append(('tr/hand', [P('tr/hand', str(AS / 'hand.png'), hx, hy, hw, HAND_H)]))
    return out, txt, cur, tx0


def s_trig():
    """13p: 문구를 왼쪽 영역 중앙으로 옮기고 '실타래 버튼'과 'Weave'에 보라색 강조."""
    s = Slide('trig', trans=('morph', 1000), cur='01', done={'00'},
              notes='01단계, 상황 인식입니다. 검색창에 단서를 적다 막히면 (클릭) 키보드의 실타래 버튼을 누릅니다. '
                    '그러면 Weave가 실행되어 검색창에 적어 둔 질의를 그대로 받아 옵니다.')
    parts, txt, cur, tx0 = trig_parts()
    pm = dict(parts)
    s.add('tr/sp', pm['tr/sp'])
    s.add('q/text', [txt])
    s.add('tr/kb', pm['tr/kb'])
    s.add('tr/glow', pm['tr/glow'])
    s.add('tr/hand', pm['tr/hand'])
    x, y, w, h = TR_SP
    s.add('tr/qhl', [hl_band('tr/qhl', tx0, y + (h - 17.5 * 4 / 3 * 1.4) / 2 + 3, QUERY, QUERY, 17.5, kind='low', alpha=34)])
    s.add('tr/cap', [caption('tr/cap', [[('실타래 버튼', PURPLE), ('을 누르면,', INK)], [('Weave', PURPLE), ('가 실행됩니다', INK)]], 136, 336, size=30, align='l')])
    s.click()
    s.on('tr/hand', 'fly', 0, 700, dx=170, dy=230, bend=0.1)
    s.on('tr/cap', 'rise', 200, 550, dy=16)
    s.on('tr/hand', 'pulse', 760, 140, scale=0.93)
    s.on('tr/glow', 'zoom_in', 860, 300, **{'from': 0.6})
    s.on('tr/qhl', 'wipe_in', 1150, 600)
    return s


QR = (52, 180, 576, 276)          # 14p: 질문 위아래 여백을 절반으로 줄여 탄탄하게


def qr_full():
    x, y, w, h = QR
    out = [('sp/card', [R('sp/card/bg', x, y, w, h, prst='roundRect', radius=22, fill='FFFFFF', line=RING, line_w=2.2, glow=(10, RING, 22),
                          shadow=SHADOW_LIFT),
                        P('sp/card/ic', ICON['spool'], x + 24, y + 18, 30, 30),
                        T('sp/card/t', x + 62, y + 18, 300, 30, 'Query Rewriting', size=17, color=PURPLE, weight='b', anchor='ctr')])]
    return out


def s_split():
    s = Slide('split', trans=('morph', 1000), cur='02', done={'00', '01'},
              notes='02단계, 질의 재작성입니다. 한 번에 답이 나오지 않는 복합 질의를 의미 단위로 나눠 다시 씁니다. '
                    '(클릭) 첫 번째 질문은 지은이네 집들이가 언제였는지 묻고, 두 번째 질문은 아직 모르는 날짜를 그날이라는 빈칸으로 둔 채 마셨던 와인을 묻습니다.')
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
    tqx, tqy = qx + 26, qy + 66
    s.add('q/text', [T('q/text', tqx, tqy, qw - 40, S * 1.4, QUERY, size=qpt, color=INK)])
    qpos = (tqx, tqy, QUERY, qpt, 'r')
    b1 = band('sp/b1', qpos, '지은이네 집들이', alpha=36)
    b2 = hl_band('sp/b2', tqx, tqy, QUERY, '때 마셨던 와인', qpt, color=BLUE_HL, alpha=40)
    s.add('sp/b1', [b1])
    s.add('sp/b2', [b2])
    r1y, r2y = qy + 118, qy + 190
    s.add('sp/r1', [R('sp/r1/bg', qx + 22, r1y, qw - 44, 58, prst='roundRect', radius=14, fill=LAV, line=None)] +
          numdot('sp/r1/n', qx + 50, r1y + 29, 1, r=14, pt=11) +
          [T('sp/r1/t', qx + 76, r1y, qw - 110, 58, '지은이네 집들이는 언제였지?', size=17, color=INK, weight='m', anchor='ctr')])
    blank, bw_ = chip('sp/r2/b', qx + 76, r2y + 15, '그날', 'dash', pt=13, h=30, padx=12)
    s.add('sp/r2', [R('sp/r2/bg', qx + 22, r2y, qw - 44, 58, prst='roundRect', radius=14, fill=BLUE_BG, line=None)] +
          numdot('sp/r2/n', qx + 50, r2y + 29, 2, r=14, pt=11, fill=BLUE) + blank +
          [T('sp/r2/t', qx + 76 + bw_ + 6, r2y, qw - 110 - bw_, 58, '마셨던 와인은?', size=17, color=INK, weight='m', anchor='ctr')])
    s.add('sp/cap', [caption('sp/cap', [[('질의를 ', INK), ('의미 단위로 나눠', PURPLE), (' 다시 씁니다', INK)]], qx + qw / 2, 94, size=24)])
    s.on('sp/cap', 'rise', 200, 500, dy=14)
    s.click()
    s.on('sp/b1', 'wipe_in', 0, 450)
    s.on('sp/r1', 'rise', 500, 450, dy=14)
    s.on('sp/b2', 'wipe_in', 1300, 450)
    s.on('sp/r2', 'rise', 1800, 450, dy=14)
    return s


# ------------------------------------------------------------------ 7. 03 연쇄 탐색: Hop 1 (15p), Hop 2 (16p)
QC = (40, 134, 420, 208)           # 작게 왼쪽 위로 옮긴 Query Rewriting 판(질문 위아래 여백 축소)
H1 = (40, 366, 420, 112)           # Query 1 · Hop 1
H2 = (40, 504, 420, 112)           # Query 2 · Hop 2


def qr_small(state='hop1', alpha=100):
    """왼쪽 위 작은 Query Rewriting 판."""
    x, y, w, h = QC
    h_box = 186 if state == 'hop1' else h
    out = [R('sp/card/bg', x, y, w, h_box, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.4, shadow=SHADOW_CARD),
           P('sp/card/ic', ICON['spool'], x + 18, y + 12, 24, 24),
           T('sp/card/t', x + 48, y + 12, 220, 24, 'Query Rewriting', size=13.5, color=PURPLE, weight='b', anchor='ctr')]
    q_ = [T('q/text', x + 20, y + 46, w - 30, 22, QUERY, size=12.5, color=INK)]
    r1y, r2y, ay = y + 76, y + 122, y + 170
    r1 = [R('sp/r1/bg', x + 14, r1y, w - 28, 40, prst='roundRect', radius=12, fill=LAV, line=None)] +         numdot('sp/r1/n', x + 36, r1y + 20, 1, r=11, pt=9) +         [T('sp/r1/t', x + 56, r1y, w - 80, 40, '지은이네 집들이는 언제였지?', size=12.5, color=INK, weight='m', anchor='ctr')]
    if state == 'hop1':
        blank, bw_ = chip('sp/r2/b', x + 56, r2y + 8, '그날', 'dash', pt=10.5, h=24, padx=9)
    else:
        blank, bw_ = chip('sp/r2/b', x + 56, r2y + 8, '3/15 (일)', 'fill', pt=10.5, h=24, padx=9)
    r2 = [R('sp/r2/bg', x + 14, r2y, w - 28, 40, prst='roundRect', radius=12, fill=BLUE_BG, line=None)] +         numdot('sp/r2/n', x + 36, r2y + 20, 2, r=11, pt=9, fill=BLUE) + blank +         [T('sp/r2/t', x + 56 + bw_ + 5, r2y, w - 90 - bw_, 40, '마셨던 와인은?', size=12.5, color=INK, weight='m', anchor='ctr')]
    an = [T('sp/ans/l', x + 22, ay, 30, 28, '답', size=11, color=MUTE, weight='b', anchor='ctr'),
          R('sp/ans/slot', x + 56, ay + 1, tw('배비치 소비뇽 블랑', 11, 'b') + 20, 26, prst='roundRect', fill='FFFFFF', line=PURPLE2,
            line_w=1.2, dash='dash')]
    return out, q_, r1, r2, an, (r1y, r2y, ay)


def re_card(key, box, hop, query_runs, active=True, done=False, alpha=100, q_color=None, theme='purple'):
    """Query 1 (Hop 1) / Query 2 (Hop 2) 실행 카드. theme='orange'면 일반 임베딩 주황 테두리."""
    x, y, w, h = box
    if theme == 'orange':
        ln, t_col, glow_ = (ORANGE_HL, 2.2), ORANGE, (10, ORANGE_HL, 20)
    elif active:
        ln, t_col, glow_ = (RING, 2.2), PURPLE, (10, RING, 22)
    else:
        ln, t_col, glow_ = (LINE2, 1.4), SUB, None
    out = [R(key + '/bg', x, y, w, h, prst='roundRect', radius=20, fill='FFFFFF', line=ln[0], line_w=ln[1],
             glow=glow_, shadow=SHADOW_CARD),
           T(key + '/t', x + 20, y + 13, 200, 24, 'Query %d' % hop, size=14, color=t_col, weight='b', anchor='ctr')]
    hx = x + w - 20 - (tw('Hop %d' % hop, 10, 'b') + 22)
    if theme == 'orange':
        hc = [R(key + '/hop/bg', hx, y + 13, tw('Hop %d' % hop, 10, 'b') + 22, 24, prst='roundRect', fill=ORANGE_BG, line=ORANGE_HL, line_w=1.2),
              T(key + '/hop/t', hx, y + 13, tw('Hop %d' % hop, 10, 'b') + 22, 24, 'Hop %d' % hop, size=10, color=ORANGE, weight='b', align='c', anchor='ctr')]
    else:
        hc, _ = chip(key + '/hop', hx, y + 13, 'Hop %d' % hop, 'fill' if active else 'outline', pt=10, h=24, padx=11)
    out += hc
    out.append(R(key + '/f', x + 16, y + 48, w - 32, 48, prst='roundRect', radius=14, fill='F7F5FC', line=LINE, line_w=1.0))
    tx = x + 30
    for i, (t, st) in enumerate(query_runs):
        if st == 'tok':
            c, cw = chip(key + '/tok', tx, y + 60, t, 'fill', pt=11, h=26, padx=10)
            out += c
            tx += cw + 6
        else:
            out.append(T(key + '/q%d' % i, tx, y + 48, w - (tx - x) - 20, 48, t, size=13.5, color=q_color or (INK if active else MUTE),
                         weight='m', anchor='ctr'))
            tx += tw(t, 13.5, 'm')
    if done:
        out += check_icon(key + '/ok', x + w - 31, y + 72, s=14, color=PURPLE, w=2.4)
    return out


H1_SPACE = (490, 134, 750, 524)
H1_STAR = (780, 404)
H1_CARD_Y = 290
H1_META, H1_LINES = '카카오톡 · 3월 15일 (일) 오후 4:12', ['박스 정리 다 했어! 이따 올 때', '휴지 안 사 와도 돼']
CAP_Y = 84


def s_hop1():
    """15p(Hop 1):
    - Hop 2는 표시하지 않음.
    - 장이 열리자마자 ① → Query 1(Hop 1) 화살표와 박스가 뜨고, 바로 임베딩 공간이 펼쳐짐.
    - 초기(일반 임베딩, 주황색): 주황 별과 주황 원 안에 표면적 의미가 비슷한 캘린더·노트가 있고, 보라 테두리 '단서'인 지은 카톡은 멀리 떨어져 있음.
    - 클릭 1(Reasoning Embedding, 보라색): 토글과 별·원이 보라색으로 바뀌며 공간이 재정렬되고, 기존 자리엔 흐린 흔적(ghost)을 남긴 채 실선 궤적을 따라 보라 테두리 '단서' 지은 카톡이 쿼리 별 옆으로 이동함.
    - 클릭 2: 지은 카톡 상세 카드가 열리며 '카카오톡 · 3월 15일 (일)'의 날짜와 본문 단서가 보라색으로 강조됨(별도 3/15 뱃지 없음)."""
    s = Slide('hop1', trans=('morph', 1100), cur='03', done={'00', '01', '02'},
              notes=('03단계 연쇄 탐색의 첫 번째 홉입니다. 첫 번째 하위 질문인 지은이네 집들이가 언제였는지를 찾습니다. '
                    '만약 일반 임베딩으로 찾으면 집들이나 지은이네처럼 표면적인 뜻이 비슷한 다른 사람의 집들이 일정과 주소 메모만 주황색 원 안에 잡히고, '
                    '정작 진짜 단서인 지은이의 카톡은 멀리 떨어져 있어 찾지 못합니다. '
                    '(클릭) 하지만 Weave의 Reasoning Embedding으로 전환하면 임베딩 공간이 재정렬됩니다. '
                    '휴지 안 사 와도 돼라는 말이 집들이 초대라는 숨은 맥락을 추론해, 멀리 있던 지은이의 카톡 단서를 질문 바로 곁으로 끌어당깁니다. '
                    '(클릭) 이렇게 찾아낸 카톡에서 대화를 나눈 3월 15일 일요일이 바로 집들이 날짜라는 첫 단서를 얻습니다.'))
    card_, q_, r1, r2, an, (r1y, r2y, ay) = qr_small('hop1')
    for p_ in card_:
        s.add(p_[1], [p_])
    s.add('q/text', q_)
    s.add('sp/r1', r1)
    s.add('sp/r2', r2)
    q1 = [('지은이네 집들이는 언제였지?', 'q')]
    # ① → Query 1 화살표와 Query 1 카드(처음엔 주황 일반 임베딩 상태 → 클릭 1에 보라 Reasoning Embedding 상태로)
    s.add('h1/c0', thread('h1/c0', [(QC[0] + 14, r1y + 20), (QC[0] - 14, r1y + 20), (H1[0] - 14, H1[1] + 28), (H1[0] - 2, H1[1] + 28)],
                          w=2.2, color=ORANGE, tail='triangle'), temp=True)
    s.add('h1/c', thread('h1/c', [(QC[0] + 14, r1y + 20), (QC[0] - 14, r1y + 20), (H1[0] - 14, H1[1] + 28), (H1[0] - 2, H1[1] + 28)],
                         w=2.2, tail='triangle'))
    s.add('h1/re0', re_card('h1/re0', H1, 1, q1, active=True, q_color=INK, theme='orange'), temp=True)
    s.add('h1/re', re_card('h1/re', H1, 1, q1, active=True, theme='purple'))

    # 상단 캡션: 일반 임베딩(주황) → Reasoning Embedding(보라)
    s.add('h1/cap0', [caption('h1/cap0', [[('일반 임베딩', ORANGE), ('은 표면적 의미가 비슷한 기록만 가깝게 둡니다', INK)]], 640, CAP_Y, size=22)], temp=True)
    s.add('h1/cap', [caption('h1/cap', [[('Reasoning Embedding', PURPLE), ('은 단서가 될 기록도 가깝게 둡니다', INK)]], 640, CAP_Y, size=22)])

    sx, sy, sw, sh = H1_SPACE
    s.add('h1/space', [R('h1/space/bg', sx, sy, sw, sh, prst='roundRect', radius=22, fill='FFFFFF', alpha=88, line=LINE2, line_w=1.2),
                       T('h1/space/fn', sx + sw - 280, sy + sh - 26, 264, 18, '* 가까울수록 질문과 의미적으로 가까운 기록', size=10, color=SUB, align='r')])
    tx0, ty0 = sx + 20, sy + 16
    tpt = 12
    wa, wb = tw('일반 임베딩', tpt, 'b') + 30, tw('Reasoning Embedding', tpt, 'b') + 30
    s.add('h1/togbg', [R('h1/tog/bg', tx0, ty0, wa + wb + 8, 38, prst='roundRect', fill='F1EEF8', line=None)])
    s.add('h1/togA', [R('h1/togA/k', tx0 + 4, ty0 + 4, wa, 30, prst='roundRect', fill=ORANGE, line=None, glow=(8, ORANGE_HL, 28)),
                      T('h1/togA/a', tx0 + 4, ty0 + 4, wa, 30, '일반 임베딩', size=tpt, color='FFFFFF', weight='b', align='c', anchor='ctr'),
                      T('h1/togA/b', tx0 + 4 + wa, ty0 + 4, wb, 30, 'Reasoning Embedding', size=tpt, color=MUTE, weight='b', align='c',
                        anchor='ctr')], temp=True)
    s.add('h1/togB', [R('h1/togB/bgc', tx0 + 2, ty0 + 2, wa + wb + 4, 34, prst='roundRect', fill='F1EEF8', line=None),
                      R('h1/togB/k', tx0 + 4 + wa, ty0 + 4, wb, 30, prst='roundRect', fill=PURPLE, line=None, glow=(8, RING, 30)),
                      T('h1/togB/a', tx0 + 4, ty0 + 4, wa, 30, '일반 임베딩', size=tpt, color=MUTE, weight='b', align='c', anchor='ctr'),
                      T('h1/togB/b', tx0 + 4 + wa, ty0 + 4, wb, 30, 'Reasoning Embedding', size=tpt, color='FFFFFF', weight='b', align='c',
                        anchor='ctr')])

    cw_ = card_fit('지은', H1_META, H1_LINES, pt=12, title_pt=13.5, bubble=True)
    cx_, cy_ = sx + sw - 12 - cw_, H1_CARD_Y
    d1i, d1f = (644, 316), (510, 212)
    d2i, d2f = (792, 438), (536, 562)
    ki, kf = (1010, 536), (786, 436)
    d1, d1w, d1h = mini_chip('h1/d1', d1f[0], d1f[1], 'cal', '성빈이 신혼집들이', '2025. 10. 18 (토)', pt=11.5)
    d2, d2w, d2h = mini_chip('h1/d2', d2f[0], d2f[1], 'note', '지은이네 주소', '경기도 수원시…', pt=11.5)
    kk, kw_, kh_ = mini_chip('h1/k', kf[0], kf[1], 'talk', '지은', '박스 정리 다 했어!…', pt=11.5)
    # 기존 위치(ki)에 남는 흐린 흔적(ghost)
    kk_ghost, _, _ = mini_chip('h1/k_ghost', ki[0], ki[1], 'talk', '지은', '박스 정리 다 했어!…', pt=11.5, alpha=28)

    far = []
    for k, kind, label, x_, y_ in (('h1/f1', 'mail', '관리비 고지서', 1046, 190), ('h1/f2', 'talk', '택배', 1128, 464),
                                   ('h1/f3', 'cal', '팀 회식', 738, 606), ('h1/f4', 'note', '소믈리에 추천', 872, 612)):
        prims, w_, h_ = mini_chip(k, x_, y_, kind, label, pt=11.5, alpha=60)
        far.append((k, prims, (x_, y_, w_, h_)))
    keep_out = [(cx_, cy_ - 50, cw_, 220), (d1f[0], d1f[1], d1w, d1h), (d2f[0], d2f[1], d2w, d2h), (ki[0], ki[1], kw_, kh_)] + [b for _, _, b in far]
    rnd = random.Random(23)
    dots = []
    for i in range(30):
        while True:
            x_, y_ = sx + 26 + rnd.random() * (sw - 52), sy + 72 + rnd.random() * (sh - 98)
            if ((x_ - H1_STAR[0]) / 185) ** 2 + ((y_ - H1_STAR[1]) / 145) ** 2 < 1:
                continue
            if any(bx - 10 <= x_ <= bx + bw + 10 and by - 10 <= y_ <= by + bh + 10 for bx, by, bw, bh in keep_out):
                continue
            break
        r_ = 3.2 + rnd.random() * 2.4
        dots.append(R('h1/dot%d' % i, x_ - r_, y_ - r_, 2 * r_, 2 * r_, prst='ellipse', fill='CBC0EC', alpha=75, line=None))
    s.add('h1/dots', dots)
    for k, prims, _ in far:
        s.add(k, prims)

    # 일반 임베딩 주황 원(near0) vs Reasoning Embedding 보라 원(near)
    s.add('h1/near0', [R('h1/near0', H1_STAR[0] - 165, H1_STAR[1] - 125, 330, 250, prst='ellipse', fill=None, line=ORANGE_HL, line_w=2.0,
                         dash='dash')], temp=True)
    s.add('h1/near', [R('h1/near', H1_STAR[0] - 165, H1_STAR[1] - 125, 330, 250, prst='ellipse', fill=None, line=PURPLE2, line_w=2.0,
                        dash='dash')])

    def off(a, b):
        return (a[0] - b[0], a[1] - b[1])
    s.add('h1/d1', d1, start=off(d1i, d1f))
    s.add('h1/d2', d2, start=off(d2i, d2f))
    # 기존 위치 흔적(ghost) + 실선(일반 선) 이동 궤적
    s.add('h1/k_ghost', kk_ghost + [ ring_box('h1/k_ghost/ring', (ki[0], ki[1], kw_, kh_), pad=3, radius=14, w=1.6) ], alpha=28)
    ci, cf = (ki[0] + kw_ / 2, ki[1] + kh_ / 2), (kf[0] + kw_ / 2, kf[1] + kh_ / 2)
    s.add('h1/trail', [C('h1/trail', [ci, (ci[0] - 70, ci[1] - 6), (cf[0] + 84, cf[1] + 52), cf], w=2.2, color=PURPLE2, dash=None)],
          temp=True)
    # 단서(지은 카톡) 칩: 처음부터 보라 테두리(ring_box)와 '단서' 태그가 한 묶음으로 붙어 있어 함께 이동!
    k_ring = ring_box('h1/k/ring', (kf[0], kf[1], kw_, kh_), pad=3, radius=14, w=2.4)
    s.add('h1/k', [k_ring] + kk + clue_tag('h1/k/tag', kf[0], kf[1]), start=off(ki, kf))

    # 주황 별(일반 임베딩) → 보라 별(Reasoning Embedding)
    s.add('h1/star0', star('h1/star0', *H1_STAR, color=ORANGE) +
          [R('h1/star0/lbg', H1_STAR[0] + 18, H1_STAR[1] - 46, tw('질문 ①', 10.5, 'b') + 18, 24, prst='roundRect', fill=ORANGE_BG, line=ORANGE_HL, line_w=1.2),
           T('h1/star0/lt', H1_STAR[0] + 18, H1_STAR[1] - 46, tw('질문 ①', 10.5, 'b') + 18, 24, '질문 ①', size=10.5, color=ORANGE, weight='b', align='c', anchor='ctr')],
          temp=True)
    s.add('h1/star', star('h1/star', *H1_STAR, color=PURPLE))
    s.add('h1/starl', chip('h1/starl', H1_STAR[0] + 18, H1_STAR[1] - 46, '질문 ①', 'soft', pt=10.5, h=24, padx=9, weight='b')[0])

    # 클릭 2: 카톡 상세 카드 (별도 3/15 뱃지 없이 '카카오톡 · 3월 15일 (일)' 내부를 진하게 강조)
    talk = card('h1/card', 'talk', cx_, cy_, cw_, '지은', H1_META, H1_LINES, pt=12, title_pt=13.5)
    s.add('h1/link', thread('h1/link', scurve((kf[0] + kw_, kf[1] + kh_ / 2), (cx_, cy_ + 76)), w=2.2))
    s.add('h1/card', talk[0])
    tp = talk[2]
    s.add('h1/h1', [band('h1/h1', tp[0], '박스 정리')])
    s.add('h1/h2', [band('h1/h2', tp[1], '휴지 안 사 와도 돼')])
    s.add('h1/hd', [band('h1/hd', tp['meta'], '3월 15일 (일)', kind='full', alpha=48)])

    # 장이 열릴 때(0): ① → Query 1 화살표와 카드가 먼저 뜨고, 바로 일반 임베딩(주황) 공간이 펼쳐짐
    s.on('h1/c0', 'jump', 50)
    s.on('h1/c0', 'wipe_in', 50, 350, dir='down')
    s.on('h1/re0', 'jump', 200)
    s.on('h1/re0', 'rise', 200, 420, dy=12)
    s.on('h1/cap0', 'jump', 300)
    s.on('h1/cap0', 'fade_in', 300, 400)
    s.on('h1/togA', 'jump', 300)
    s.on('h1/togA', 'fade_in', 300, 350)
    s.on('h1/near0', 'jump', 350)
    s.on('h1/near0', 'zoom_in', 350, 400, **{'from': 0.85})
    s.on('h1/star0', 'jump', 350)
    s.on('h1/star0', 'zoom_in', 350, 380, **{'from': 0.8})
    s.on(['h1/d1', 'h1/d2', 'h1/k'], 'fade_in', 350, 350)
    s.on(['h1/d1', 'h1/d2', 'h1/k'], 'goto', 350)

    # 클릭 1: Reasoning Embedding(보라)으로 전환 — 공간이 재정렬되며 흔적(ghost)과 실선(trail)을 남기고 '단서'가 보라 별 옆으로 이동
    s.click()
    s.on(['h1/cap0', 'h1/togA', 'h1/re0', 'h1/c0', 'h1/near0', 'h1/star0'], 'fade_out', 0, 250)
    s.on('h1/cap', 'rise', 120, 420, dy=12)
    s.on(['h1/togB', 'h1/re', 'h1/c', 'h1/near', 'h1/star', 'h1/starl'], 'fade_in', 100, 350)
    s.on('h1/k_ghost', 'fade_in', 550, 300)
    s.on('h1/d1', 'fly', 600, 950, dx=d1i[0] - d1f[0], dy=d1i[1] - d1f[1], bend=0.1, show=False, fade=False)
    s.on('h1/d2', 'fly', 600, 950, dx=d2i[0] - d2f[0], dy=d2i[1] - d2f[1], bend=-0.1, show=False, fade=False)
    s.on(['h1/d1', 'h1/d2'], 'dim', 1200, 380, to=0.4)
    s.on('h1/trail', 'jump', 650)
    s.on('h1/trail', 'wipe_in', 650, 1050, dir='right')
    s.on('h1/k', 'fly', 650, 1150, dx=ki[0] - kf[0], dy=ki[1] - kf[1], bend=0.15, show=False, fade=False)
    s.on('h1/k', 'pulse', 1850, 180, scale=1.06)

    # 클릭 2: 카톡을 열어 날짜 단서(3월 15일 (일)) 확인
    s.click()
    s.on('h1/trail', 'fade_out', 0, 220)
    s.on('h1/link', 'wipe_in', 0, 350)
    s.on('h1/card', 'zoom_in', 180, 450, **{'from': 0.85})
    s.on('h1/h1', 'wipe_in', 650, 320)
    s.on('h1/h2', 'wipe_in', 900, 400)
    s.on('h1/hd', 'wipe_in', 1350, 350)
    return s


H2_TALK = (500, 142, 340)
H2_GAL = (500, 402, 736)
H2_PHOTOS = ['babich', 'table', 'w1', 'w3', 'w2']


def s_hop2():
    """16p(Hop 2):
    - 왼쪽에 Query 1(Hop 1)이 흐리게 유지되고, 거기서 화살표가 아래 Query 2(Hop 2)로 이어짐.
    - 오른쪽 위의 지은 카톡 플로팅은 Query 1(Hop 1)과 자연스럽게 실선(삼각형 화살촉 없음)으로 연결됨.
    - 상단 문구: '찾은 날짜로 그날 사진만 남기고, 정확한 와인 이름을 찾습니다'."""
    s = Slide('hop2', trans=('morph', 1100), cur='03', done={'00', '01', '02'},
              notes='찾아낸 3월 15일 날짜 단서를 두 번째 질문 빈칸에 넣어 Query 2로 넘어갑니다. '
                    '(클릭) 날짜처럼 명확한 조건은 메타데이터 필터로 걸러 3월 15일에 찍은 사진 두 장만 남기고, '
                    '(클릭) 그중 와인이 찍힌 사진을 찾아 배비치 소비뇽 블랑이라는 정확한 와인 이름을 알아냅니다.')
    card_, q_, r1, r2, an, (r1y, r2y, ay) = qr_small('hop2')
    for p_ in card_:
        s.add(p_[1], [p_])
    s.add('q/text', q_)
    s.add('sp/r1', r1)
    s.add('sp/r2', [p_ for p_ in r2 if not p_[1].startswith('sp/r2/b')])
    s.add('sp/ans', an)

    # Hop 1(Query 1)은 흐리게 유지되고, 그 아래로 화살표가 이어져 Hop 2(Query 2)가 활성화됨
    q1 = [('지은이네 집들이는 언제였지?', 'q')]
    s.add('h1/re', re_card('h1/re', H1, 1, q1, active=False, done=True), alpha=60)
    s.add('h1/c', thread('h1/c', [(QC[0] + 14, r1y + 20), (QC[0] - 14, r1y + 20), (H1[0] - 14, H1[1] + 28), (H1[0] - 2, H1[1] + 28)],
                         w=2.0), alpha=45)
    s.add('h2/re', re_card('h2/re', H2, 2, [('3/15 (일)', 'tok'), ('마셨던 와인은?', 'q')], active=True))
    # Query 1(H1) 아래에서 Query 2(H2) 위로 내려가는 화살표
    hx_mid = H1[0] + H1[2] / 2
    s.add('h2/c', thread('h2/c', [(hx_mid, H1[1] + H1[3] + 2), (hx_mid, H2[1] - 2)], w=2.2, tail='triangle'))

    s.add('h2/cap', [caption('h2/cap', [[('찾은 날짜로 그날 사진만 남기고, ', INK), ('정확한 와인 이름을 찾습니다', PURPLE)]], 640, CAP_Y, size=22)])

    # Hop 1 결과(지은 카톡) — 오른쪽 위, Query 1(Hop 1)과 삼각형 없는 일반 실선으로 연결
    tx, ty, _ = H2_TALK
    tww = card_fit('지은', H1_META, H1_LINES, pt=12, title_pt=13.5, bubble=True)
    talk = card('h1/card', 'talk', tx, ty, tww, '지은', H1_META, H1_LINES, pt=12, title_pt=13.5)
    s.add('h1/card', talk[0])
    tp = talk[2]
    s.add('h1/h1', [band('h1/h1', tp[0], '박스 정리')])
    s.add('h1/h2', [band('h1/h2', tp[1], '휴지 안 사 와도 돼')])
    s.add('h1/hd', [band('h1/hd', tp['meta'], '3월 15일 (일)', kind='full', alpha=48)])
    x, y, w, h = QC
    tok, _ = chip('h1/tok', x + 56, r2y + 8, '3/15 (일)', 'fill', pt=10.5, h=24, padx=9)
    s.add('h1/tok', tok)
    # Query 1(H1) 오른쪽 끝에서 지은 카톡(h1/card) 왼쪽으로 이어지는 부드러운 실선(삼각형 화살촉 없음)
    s.add('h1/link', thread('h1/link', scurve((H1[0] + H1[2] + 2, H1[1] + 46), (tx - 2, ty + talk[1] / 2), 0.45), w=2.0), alpha=65)

    # Hop 2 결과(갤러리) — 오른쪽 아래, Query 2(H2) 오른쪽 끝에서 실선(삼각형 화살촉 없음)으로 연결
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
    lab, lw_ = chip('h2/ocr', spots[w_i][0] + pw / 2, spots[w_i][1] + ph - 31, 'BABICH SAUVIGNON BLANC', 'outline', pt=9, h=23, padx=8,
                    align='c')
    s.add('h2/ocr', lab)
    ans, aw = chip('h2/ans', x + 56, ay + 1, '배비치 소비뇽 블랑', 'fill', pt=11, h=26, padx=10)
    s.add('h2/ans', ans)
    s.add('h2/link', thread('h2/link', scurve((H2[0] + H2[2] + 2, H2[1] + 56), (gx - 2, gy + 104)), w=2.2))

    s.on('h2/cap', 'rise', 150, 450, dy=14)
    s.on('h1/tok', 'zoom_in', 150, 350, **{'from': 0.8})
    s.on('h2/c', 'wipe_in', 350, 380, dir='down')
    s.on('h2/re', 'rise', 500, 450, dy=12)
    s.click()   # 1: 날짜 필터
    s.on('h2/link', 'wipe_in', 0, 420)
    s.on(['h2/gal', 'h2/photos'], 'rise', 180, 480, dy=14)
    s.on('h2/filter', 'pop', 600, 400, **{'from': 0.6, 'over': 1.08})
    s.on('h2/dim', 'fade_in', 980, 380)
    s.on('h2/x', 'pop', 1080, 360, **{'from': 0.3, 'over': 1.15})
    s.on('h2/dhl', 'wipe_in', 1280, 350)
    s.click()   # 2: 와인 사진 → 정확한 와인 이름 확보
    s.on('h2/dimt', 'fade_in', 0, 380)
    s.on('h2/pring', 'zoom_in', 220, 400, **{'from': 1.12})
    s.on('h2/ocr', 'wipe_in', 580, 450)
    s.on('h2/ans', 'fly', 1100, 950, dx=spots[w_i][0] + pw / 2 - (x + 56) - aw / 2, dy=spots[w_i][1] + ph - 20 - (ay + 1), bend=-0.18)
    return s


# ------------------------------------------------------------------ 8. 04 결과 제공 (17p: 문구 '찾은 답을 다듬어, 근거와 함께 건넵니다', 작은 손, 즉시 텍스트 교체)
DL_SP = (140, 166, 560, 66)
SHEET = (140, 252, 560, 340)


def s_deliver():
    s = Slide('deliver', trans=('morph', 1000), cur='04', done={'00', '01', '02', '03'},
              notes='마지막 04단계, 결과 제공입니다. 찾아낸 답을 상황에 맞게 다듬어, 근거가 된 카톡·갤러리 기록과 함께 키보드 위로 건넵니다. '
                    '(클릭) 입력하기를 누르면 검색창에 배비치 소비뇽 블랑이 바로 채워지고, 이 모든 과정은 외부 서버 전송 없이 기기 안에서 이뤄집니다.')
    x, y, w, h = DL_SP
    pill, txt, cur, tx0 = search_pill('dl/sp', x, y, w, h, QUERY, pt=16.5)
    s.add('dl/sp', pill)
    s.add('dl/q', [txt], temp=True)
    ans = '배비치 소비뇽 블랑'
    s.add('dl/q2', [T('dl/q2', txt[2], txt[3], txt[4], txt[5], ans, size=16.5, color=INK, weight='b', anchor='ctr')])
    s.add('dl/cur', [R('dl/cur', tx0 + tw(ans, 16.5, 'b') + 3, y + h / 2 - 11, 2.4, 22, fill=PURPLE, line=None)])
    sx, sy, sw, sh = SHEET
    by_ = sy + 128
    rows = [('talk', '지은', '‘휴지 안 사 와도 돼’  3월 15일'), ('gallery', '와인 사진', '3월 15일 20:14')]
    bt_w = tw('입력하기', 14, 'b')
    bt_cx = sx + sw / 2
    out = [R('dl/sheet/bg', sx, sy, sw, sh, prst='roundRect', radius=24, fill='FFFFFF', line=LINE2, line_w=1.4, shadow=SHADOW_LIFT),
           R('dl/sheet/card', sx + 18, sy + 18, sw - 36, 96, prst='roundRect', radius=16, fill=LAV, line=None)] +           star4_icon('dl/sheet/star', sx + 42, sy + 41, r=6.2, color=PURPLE) +           [T('dl/sheet/lab', sx + 54, sy + 30, 300, 22, '자동 완성 추천', size=12, color=PURPLE, weight='b'),
           T('dl/sheet/ans', sx + 36, sy + 56, sw - 72, 44, ans, size=24, color=INK, weight='b', anchor='ctr'),
           R('dl/sheet/btn', sx + 18, by_, sw - 36, 50, prst='roundRect', radius=14, fill=PURPLE, line=None, shadow=(14, 4, '6B4EFF', 24))] +           check_icon('dl/sheet/chk', bt_cx - bt_w / 2 - 11, by_ + 25, s=11.5, color='FFFFFF', w=2.2) +           [T('dl/sheet/btnt', sx + 34, by_, sw - 52, 50, '입력하기', size=14, color='FFFFFF', weight='b', align='c', anchor='ctr'),
           T('dl/sheet/mem', sx + 26, by_ + 66, 200, 22, '연결된 기억', size=12, color=SUB, weight='b')]
    for i, (ic, a, b) in enumerate(rows):
        ry = by_ + 96 + i * 40
        out += [P('dl/sheet/ic%d' % i, ICON[ic], sx + 26, ry + 3, 26, 26),
                T('dl/sheet/r%d' % i, sx + 62, ry, sw - 90, 32, [[(a + '  ', {'weight': 'b', 'color': INK}), (b, {'color': SUB})]], size=12.5,
                  anchor='ctr')]
    s.add('dl/sheet', out)
    HD = 90                                    # 손 크기를 살짝 줄여 버튼을 가리지 않게
    hw = HD * 773 / 960
    bx, by2 = sx + sw - 112, by_ + 25
    s.add('dl/hand', [P('dl/hand', str(AS / 'hand.png'), bx - hw * 0.388, by2 - HD * 0.015 + 6, hw, HD)])
    s.add('dl/cap', [caption('dl/cap', [[('찾은 답을 다듬어,', INK)], [('근거와 함께 건넵니다', PURPLE)]], sx + sw + 62, 348, size=30, align='l')])
    s.on('dl/q', 'jump', 0)
    s.on('dl/sheet', 'rise', 150, 550, dy=16)
    s.on('dl/cap', 'rise', 450, 550, dy=16)
    s.click()                    # 입력하기 → 모션그래픽처럼 검색창 텍스트가 즉시 '배비치 소비뇽 블랑'으로 바뀜
    s.on('dl/hand', 'fly', 0, 600, dx=120, dy=180, bend=0.1)
    s.on('dl/hand', 'pulse', 630, 130, scale=0.92)
    s.on('dl/q', 'fade_out', 800, 160)
    s.on('dl/q2', 'fade_in', 840, 220)
    s.on('dl/cur', 'appear', 920, 1)
    s.on('dl/cur', 'blink', 960, 1000)
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
               T(key + '/t', x + 18, y + 14, 220, 24, 'Reasoning Embedding', size=12, color=PURPLE, weight='b', anchor='ctr')]
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
                           '갤러리 · 3월 15일 20:14', 'BABICH SAUVIGNON BLANC'))

    # Column 4: 04 결과 제공 (x=962, w=264)
    c4x, c4w = 962, 264
    bt_w = tw('입력하기', 11.5, 'b')
    bt_cx = c4x + c4w / 2
    res = [R('ov/res/bg', c4x, cy + 34, c4w, 332, prst='roundRect', radius=18, fill='FFFFFF', line=RING, line_w=1.8, glow=(8, RING, 22), shadow=SHADOW_CARD),
           R('ov/res/card', c4x + 14, cy + 50, c4w - 28, 92, prst='roundRect', radius=14, fill=LAV, line=None)] + \
          star4_icon('ov/res/star', c4x + 31, cy + 69, r=5.5, color=PURPLE) + \
          [T('ov/res/l', c4x + 41, cy + 60, 200, 20, '자동 완성 추천', size=10, color=PURPLE, weight='b'),
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
    cols = [('원문 · OCR', '박스 정리 다 했어! 이따 올 때…', BODY),
            ('의미 벡터', '[0.86, −0.08, 0.33, …]', PURPLE),
            ('메타데이터', '{ date: "2026-03-15", app, … }', INK)]
    for i, (a, b, col) in enumerate(cols):
        cx_ = 330 + i * 295
        idx.append(T('ov/idx/l%d' % i, cx_, iy + 41, 270, 24, a, size=12, color=PURPLE if i else SUB, weight='b'))
    s.add('ov/idx', idx)

    # 좌 → 우 직관적 화살표 (01 → 02 → 03 Hop1 → 단서 대입 → 03 Hop2 → 04)
    s.add('ov/a1', thread('ov/a1', [(c1x + c1w + 2, cy + 190), (c2x - 2, cy + 190)], w=2.4, tail='triangle'))
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
        slides.append(slide)
    return slides, report, secs



def build(dst, auto=False, hold=1700):
    """원본 덱에서 장 틀과 노트 틀만 빌려, 새 장을 끝에 다 넣은 뒤 원본 장을 지운다
    (먼저 지우면 python-pptx가 장 파일 이름을 다시 써서 PowerPoint가 못 여는 일이 있었음)."""
    prs = Presentation(str(SRC))
    layout = prs.slides[LAYOUT_INDEX].slide_layout
    note_tpl = [copy.deepcopy(sh._element) for sh in prs.slides[LAYOUT_INDEX].notes_slide.placeholders]
    lst = prs.slides._sldIdLst
    old = list(lst)
    specs = [f() for f in SOL_SLIDES] + [f() for f in SLIDES] + appendix_specs()
    _, report, secs = add_slides(prs, layout, note_tpl, specs, auto, hold)
    for sid in old:
        prs.part.drop_rel(sid.get(q('r:id')))
        lst.remove(sid)
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
    global PASS1
    ap = argparse.ArgumentParser()
    ap.add_argument('--png', action='store_true')
    ap.add_argument('--video', action='store_true')
    ap.add_argument('--skip-blur', action='store_true', help='흐린 그림을 다시 만들지 않음(있는 것을 씀)')
    a = ap.parse_args()
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
        blur_png(pngs[names.index('cloud')], OUT / 'blur_cloud.png', radius=4, veil=0.10)      # 살짝만 흐리게
        tmp.unlink()
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
        _, secs = build(auto, auto=True)
        print(render_c.video(auto, OUT / 'HowItWorks_Argon_claude_미리보기.mp4', secs))
        auto.unlink()


if __name__ == '__main__':
    main()
