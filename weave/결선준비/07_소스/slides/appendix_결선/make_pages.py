#!/usr/bin/env python3
"""결선 Appendix 새 장 7개를 HTML로 만든다(2026-11-05 2차). render.cjs → out/*.art.png, *.layout.json → apply_appendix.py.

  python make_pages.py   → page-a1 ~ page-a7 .html, notes-page-a1 ~ a7 .txt

이전 파이프라인 장(07_소스/pages/page-07-pipeline.html)과 같은 카드, 번호 원, 칩, 앱 아이콘, 손글씨를 쓴다.
글은 줄바꿈을 직접 넣고, 폭은 덱 글꼴(SamsungOneKorean)로 잰다.
"""
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
FONTS = Path.home() / '.cache' / 'weave-tools' / 'fonts'
A = '../../assets'
HIW = '../../../09_HowItWorks/장표5/assets'
ICON = {'cal': f'{A}/icons/galaxy/samsung-calendar.png', 'note': f'{A}/icons/app-notes.png', 'mail': f'{A}/icons/galaxy/samsung-email-blue.png',
        'talk': f'{A}/icons/app-kakao.png', 'gal': f'{A}/icons/galaxy/samsung-gallery.png', 'wal': f'{HIW}/samsung-wallet.png',
        'map': f'{A}/icons/app-map.png', 'spool': '../assets/weave-spool-6B4EFF.png', 'spoolw': '../assets/weave-spool-white.png'}
WINE, LABEL = f'{A}/crops/ux2-wine-photo.png', f'{A}/crops/ux2-label-text.png'
BOTTLE, TABLE = '../p05_결선/assets/wife-bottle.jpg', f'{HIW}/photo-table.jpg'
STAR = 'M12 2.5c.6 4.6 2.9 6.9 7.5 7.5-4.6.6-6.9 2.9-7.5 7.5-.6-4.6-2.9-6.9-7.5-7.5 4.6-.6 6.9-2.9 7.5-7.5z'

_F = {}


def tw(text, px, bold=False):
    """덱 글꼴로 잰 글자 폭(px)."""
    k = 'SamsungOneKorean-700.ttf' if bold else 'SamsungOneKorean-400.ttf'
    if k not in _F:
        _F[k] = ImageFont.truetype(str(FONTS / k), 100)
    return _F[k].getlength(text) / 100 * px


CSS = """
  .t-label { top: 30px; } .t-title { top: 62px; } .t-sub { top: 116px; font-size: 16.5px; }
  .card { position: absolute; background: #fff; border: 1px solid var(--card-line); border-radius: 18.59px; box-shadow: 0 10px 28px rgba(107,78,255,.07); }
  .card.on { border: 1.8px solid #8B6BFF; box-shadow: 0 10px 28px rgba(107,78,255,.16); }
  .card.soft { background: rgba(255,255,255,.86); }
  .loopbox { position: absolute; border: 1.5px dashed #B7A6FF; border-radius: 24.78px; background: rgba(241,236,255,.38); }
  .abs { position: absolute; }
  .no { position: absolute; width: 24px; height: 24px; border-radius: 12px; background: var(--purple); }
  .no.w { background: #fff; border: 1.5px solid var(--purple); }
  .no-t { position: absolute; width: 24px; height: 24px; line-height: 24px; text-align: center; font-size: 12.5px; font-weight: 700; color: #fff; }
  .no-t.w { color: var(--purple); }
  .nm { position: absolute; font-size: 18.7px; line-height: 24.9px; font-weight: 700; color: var(--ink); white-space: nowrap; }
  .en { position: absolute; font-size: 13px; line-height: 24.9px; font-weight: 600; color: var(--purple-2); letter-spacing: .01em; white-space: nowrap; }
  .q { position: absolute; font-family: 'Nanum Pen Script'; font-size: 22.66px; line-height: 26.94px; color: var(--purple); white-space: nowrap; }
  .desc { position: absolute; font-size: 14px; line-height: 20.7px; color: var(--body); white-space: nowrap; }
  .desc b { color: var(--ink); font-weight: 700; }
  .chip { position: absolute; height: 23.8px; border-radius: 12.4px; background: #fff; border: 1px solid var(--purple-line); }
  .chip.fill { background: var(--purple); border-color: var(--purple); }
  .chip.soft { background: var(--tile); border-color: var(--tile); }
  .chip.dash { background: #F7F4FF; border: 1.3px dashed #8B6BFF; }
  .ct { position: absolute; text-align: center; font-size: 12.5px; font-weight: 700; color: var(--purple); white-space: nowrap; }
  .ct.fill { color: #fff; }
  .ct.gray { color: var(--body); font-weight: 600; }
  .mini { position: absolute; background: #fff; border: 1px solid var(--card-line); border-radius: 12.4px; }
  .mini.on { border: 1.6px solid #8B6BFF; box-shadow: 0 4px 12px rgba(107,78,255,.14); }
  .mini.off { background: #FAF9FC; border-color: #ECE8F4; }
  .pill { position: absolute; background: var(--soft); border: 1px solid var(--soft-line); border-radius: 12.4px; }
  .lav { position: absolute; background: #F4F0FF; border: 1px solid #E3D9FF; border-radius: 11px; }
  .tile { position: absolute; border-radius: 8.3px; background: var(--tile); }
  .ico { position: absolute; color: var(--purple); }
  .app { position: absolute; }
  .photo { position: absolute; border-radius: 9px; overflow: hidden; }
  .photo img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .btn { position: absolute; background: var(--purple); border-radius: 10px; }
  .bar { position: absolute; background: #EEE9FA; }
  .t10 { position: absolute; font-size: 10.5px; line-height: 14px; color: var(--muted); white-space: nowrap; }
  .t10m { position: absolute; font-size: 10.5px; line-height: 14px; color: var(--muted-2); white-space: nowrap; }
  .t10b { position: absolute; font-size: 10.5px; line-height: 14px; font-weight: 700; color: var(--ink); white-space: nowrap; }
  .t10p { position: absolute; font-size: 10.5px; line-height: 14px; font-weight: 700; color: var(--purple); white-space: nowrap; }
  .t11 { position: absolute; font-size: 11.5px; line-height: 16px; color: var(--body); white-space: nowrap; }
  .t11 b { color: var(--ink); font-weight: 700; }
  .t11 em { font-style: normal; font-weight: 700; color: var(--purple); }
  .t11m { position: absolute; font-size: 11.5px; line-height: 16px; color: var(--muted-2); white-space: nowrap; }
  .t11b { position: absolute; font-size: 11.5px; line-height: 16px; font-weight: 700; color: var(--ink); white-space: nowrap; }
  .t11p { position: absolute; font-size: 11.5px; line-height: 16px; font-weight: 700; color: var(--purple); white-space: nowrap; }
  .t12 { position: absolute; font-size: 12.7px; line-height: 18px; color: var(--body); white-space: nowrap; }
  .t12 b { color: var(--ink); font-weight: 700; }
  .t12 em { font-style: normal; font-weight: 700; color: var(--purple); }
  .t12b { position: absolute; font-size: 12.7px; line-height: 17px; font-weight: 700; color: var(--ink); white-space: nowrap; }
  .t12p { position: absolute; font-size: 12.7px; line-height: 17px; font-weight: 700; color: var(--purple); white-space: nowrap; }
  .t14b { position: absolute; font-size: 14.5px; line-height: 20px; font-weight: 700; color: var(--ink); white-space: nowrap; }
  .t15b { position: absolute; font-size: 16px; line-height: 22px; font-weight: 700; color: var(--ink); white-space: nowrap; }
  .t18b { position: absolute; font-size: 17px; line-height: 24px; font-weight: 700; color: var(--ink); white-space: nowrap; }
  .src { position: absolute; font-size: 11px; line-height: 15px; color: #8E88A0; white-space: nowrap; }
  svg.links { position: absolute; left: 0; top: 0; width: 1280px; height: 720px; pointer-events: none; overflow: visible; z-index: 3; }
  .app, .ico, .photo { z-index: 4; }
"""

DEFS = """<defs>
    <marker id="ah" viewBox="0 0 10 10" refX="7.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1.2 8.5 5 1 8.8" fill="none" stroke="#6B4EFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></marker>
    <marker id="ah2" viewBox="0 0 10 10" refX="7.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1.2 8.5 5 1 8.8" fill="none" stroke="#8B6BFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></marker>
  </defs>"""


def page(name, chip, title, sub, body, svg='', notes=''):
    html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{chip}</title>
<link rel="stylesheet" href="../../pages/theme.css">
<style>{CSS}</style>
</head>
<body>
<script src="../../pages/icons.js"></script>
<div class="slide" id="slide">
  <div class="bg bg-base"></div><div class="bg bg-peach"></div><div class="bg bg-lav"></div>
  <div class="t-label" data-x>{chip}</div>
  <div class="t-title" data-x>{title}</div>
  <div class="t-sub" data-x>{sub}</div>
{body}
  <svg class="links" viewBox="0 0 1280 720">{DEFS}{svg}</svg>
</div>
<script>document.fonts.ready.then(() => {{ window.pageReady = true; }});</script>
</body>
</html>
"""
    (HERE / f'{name}.html').write_text(html, encoding='utf-8')
    (HERE / f'notes-{name}.txt').write_text(notes.strip() + '\n', encoding='utf-8')


def T(cls, x, y, html, w=None, extra=''):
    wd = f' width:{w}px;' if w else ''
    return f'  <div class="{cls}" data-x style="left:{x}px; top:{y}px;{wd}{extra}">{html}</div>\n'


def BOX(cls, x, y, w, h, extra=''):
    return f'  <div class="{cls}" style="left:{x}px; top:{y}px; width:{w}px; height:{h}px;{extra}"></div>\n'


def IMG(key, x, y, s, r=0, extra=''):
    rr = f' border-radius:{r}px;' if r else ''
    return f'  <img class="app" src="{ICON[key]}" alt="" style="left:{x}px; top:{y}px; width:{s}px; height:{s}px;{rr}{extra}">\n'


def USE(sym, x, y, s, color=None):
    c = f' color:{color};' if color else ''
    return f'  <svg class="ico" style="left:{x}px; top:{y}px; width:{s}px; height:{s}px;{c}"><use href="#{sym}"/></svg>\n'


def SPARK(x, y, s, fill='#6B4EFF'):
    return f'  <svg class="app" viewBox="0 0 24 24" style="left:{x}px; top:{y}px; width:{s}px; height:{s}px;"><path d="{STAR}" fill="{fill}"/></svg>\n'


def PHOTO(src, x, y, w, h, r=9, pos=None):
    p = f' style="object-position:{pos};"' if pos else ''
    return f'  <div class="photo" style="left:{x}px; top:{y}px; width:{w}px; height:{h}px; border-radius:{r}px;"><img src="{src}" alt=""{p}></div>\n'


def CHIP(cls, x, y, w, text, h=23.8, tcls='', size=None):
    fs = f' font-size:{size}px;' if size else ''
    return BOX(f'chip {cls}', x, y, w, h, f' border-radius:{h / 2}px;') + T(f'ct {tcls or cls}', x, y, text, w, f' height:{h}px; line-height:{h}px;{fs}')


def LINE(d, c='#6B4EFF', w=2, mk='ah', dash=''):
    ds = f' stroke-dasharray="{dash}"' if dash else ''
    m = f' marker-end="url(#{mk})"' if mk else ''
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round"{ds}{m}/>'


def STEP(no, x, y, name, en, white=False):
    w = ' w' if white else ''
    return BOX(f'no{w}', x, y, 24, 24) + T(f'no-t{w}', x, y, no) + T('nm', x + 33, y - 0.4, name) + T('en', x + 33 + tw(name, 18.7, True) + 8, y - 0.4, en)


def sources(cits, y, x=64, max_w=1150, size=11):
    """각주: 논문 하나가 두 줄로 갈리지 않게 항목 사이에서만 줄을 바꾸고, 둘째 줄은 첫 논문과 왼쪽을 맞춘다."""
    pre = '* 출처: '
    px = tw(pre, size)
    lines, cur = [], ''
    for c in cits:
        t = (cur + ' · ' + c) if cur else c
        if tw(t, size) > max_w - px and cur:
            lines.append(cur)
            cur = c
        else:
            cur = t
    lines.append(cur)
    out = T('src', x, y, pre)
    for i, ln in enumerate(lines):
        out += T('src', round(x + px, 1), y + i * 15, ln)
    return out


# ───────────────────────────────── A1 파이프라인 (이전 How it Works 장과 같은 구성)
def a1():
    b = ''
    # 연쇄 탐색 루프
    b += BOX('loopbox', 300.5, 181.4, 648.2, 339.9)
    b += BOX('chip', 319, 169, 234.6, 25.9, ' border-radius:13.4px; border-color:#B7A6FF;')
    b += USE('i-refresh', 330.3, 174.2, 15.5)
    b += T('t12p', 349.9, 173.1, '필요한 정보가 채워질 때까지 반복')
    # 01
    b += BOX('card', 70, 200, 207.8, 308.8)
    b += STEP('01', 84.4, 214.6, '순간 감지', 'Trigger')
    b += T('q', 84.4, 247.8, '“지금, 도와줄 순간일까?”')
    rows = [(287.1, 'up', '위로 밀기', '통화 화면 · UX 1'), (340, 'spool', '실타래 버튼', '키보드 · UX 2'), (392.9, 'ctx', '먼저 반짝', '위치 · 탑승권 · 대화 · UX 3')]
    for y, ic, t1, t2 in rows:
        b += BOX('pill', 84.4, y, 179, 41.5)
        b += BOX('tile', 90.6, y + 6.2, 28.9, 28.9)
        if ic == 'up':
            b += f'  <svg class="ico" viewBox="0 0 24 24" style="left:96.8px; top:{y + 12.4}px; width:16.5px; height:16.5px;"><path d="M12 20V5M5.5 11.5 12 5l6.5 6.5" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>\n'
        elif ic == 'spool':
            b += IMG('spool', 95.7, y + 11.3, 18.6)
        else:
            b += USE('i-msg', 94.7, y + 10.3, 12.4) + USE('i-pin', 102.9, y + 18.6, 12.4)
        b += T('t12b', 127.6, y + 3.1, t1)
        b += T('t10', 127.6, y + 22, t2)
    b += T('desc', 84.4, 453, '<b>사용자가 직접</b> 부르거나,<br><b>맥락 파악</b> 후 조건을 감지합니다')
    # 02
    b += BOX('card', 314.9, 200, 250, 308.8)
    b += BOX('no', 329.3, 214.6, 24, 24) + T('no-t', 329.3, 214.6, '02') + T('nm', 362.2, 214.2, '질문 다시 쓰기', extra=' font-size:17px;')
    b += T('en', 362 + tw('질문 다시 쓰기', 17, True) + 7, 214.2, 'Query Rewriting', extra=' font-size:11.5px;')
    b += T('q', 329.3, 247.8, '“한 번에 찾을 수 있을까?”')
    x0, y0 = 329.3, 283
    b += BOX('mini', x0, y0, 222, 164)
    bx = x0 + 10
    b += T('t10p', bx, y0 + 7, '① 1차 통합 검색') + T('t10m', bx + tw('① 1차 통합 검색', 10.5, True) + 14, y0 + 7, 'Single-Hop')
    b += BOX('pill', bx, y0 + 24, 202, 22, ' border-radius:11px;') + T('t10', bx + 9, y0 + 28, '지은이네 집들이 때 마셨던 와인')
    b += BOX('bar', bx, y0 + 52, 202, 1)
    b += T('t10p', bx, y0 + 57, '② 하위 질문 분해') + T('t10m', bx + tw('② 하위 질문 분해', 10.5, True) + 14, y0 + 57, 'Decomposition')
    b += T('t10', bx, y0 + 74, '1. 지은이네 집들이는 언제였지?')
    b += BOX('chip dash', bx + 12, y0 + 90, 34, 17, ' border-radius:8.5px;') + T('ct', bx + 12, y0 + 90, '그날', 34, ' height:17px; line-height:17px; font-size:10px;')
    b += T('t10', bx, y0 + 91.5, '2.') + T('t10', bx + 50, y0 + 91.5, '마셨던 와인은?')
    b += BOX('bar', bx, y0 + 112, 202, 1)
    b += T('t10p', bx, y0 + 117, '④ 단서 결합·질의 재작성')
    b += BOX('chip fill', bx, y0 + 136, 58, 18, ' border-radius:9px;') + T('ct fill', bx, y0 + 136, '3/15 (일)', 58, ' height:18px; line-height:18px; font-size:10.5px;')
    b += T('t10b', bx + 62, y0 + 138, '에 마셨던 와인은?')
    b += T('desc', 329.3, 453, '막히면 <b>하위 질문으로 나누고</b>,<br>찾은 단서로 <b>질문을 다시 씁니다</b>')
    # 03
    b += BOX('card', 604, 200, 330, 308.8)
    b += STEP('03', 618, 214.6, '연쇄 탐색', 'Multi-hop Search')
    b += T('q', 618, 247.8, '“찾은 기록에, 다음 단서가 있을까?”')
    b += T('t10p', 618, 284, '③ 멀티홉 추론 검색') + T('t10m', 618 + tw('③ 멀티홉 추론 검색', 10.5, True) + 14, 284, 'Hop Retrieval')
    hx = [618, 722, 826]
    b += BOX('mini on', hx[0], 303, 92, 76)
    b += IMG('talk', hx[0] + 8, 311, 20, 5) + T('t10b', hx[0] + 33, 314, '지은')
    b += T('t10', hx[0] + 8, 335, '휴지 안 사 와도 돼') + T('t10p', hx[0] + 8, 355, '3/15 (일)')
    b += PHOTO(WINE, hx[1], 303, 92, 76, 10)
    b += BOX('abs', hx[1] + 6, 355, 60, 18, ' border-radius:9px; background:rgba(255,255,255,.92); z-index:5;')
    b += T('t10b', hx[1] + 6, 357, '3/15 20:14', 60, ' text-align:center; z-index:6;')
    b += IMG('gal', hx[1] + 70, 308, 17, 0, ' z-index:6;')
    b += BOX('mini', hx[2], 303, 92, 76)
    b += PHOTO(LABEL, hx[2] + 5, 310, 82, 41, 7)
    b += USE('i-scan', hx[2] + 7, 356, 13) + T('t10', hx[2] + 23, 355.5, '사진 속 글자')
    for x, t, c in [(hx[0], '추론 검색', 'fill'), (hx[1], '시간 필터', 'soft'), (hx[2], 'OCR', 'soft')]:
        b += BOX(f'chip {c}', x, 386, 92, 19.7, ' border-radius:10px;') + T(f'ct {"fill" if c == "fill" else ""}', x, 386, t, 92, ' height:19.7px; line-height:19.7px; font-size:11.5px;')
    b += T('t10m', 618, 413, '같은 방식으로')
    b += BOX('pill', 618, 430, 148, 25, ' border-radius:12.5px;')
    b += IMG('note', 624, 434, 16, 4) + IMG('mail', 643, 434, 16) + T('t10', 664, 435, '바뀐 회의록 → 최종본')
    b += BOX('pill', 772, 430, 148, 25, ' border-radius:12.5px;')
    b += IMG('talk', 778, 434, 16, 4) + IMG('gal', 797, 434, 16) + T('t10', 818, 435, '갈색병 → 에스티 로더')
    b += T('desc', 618, 467, '<b>찾은 단서가 다음 검색의 조건</b>이 됩니다')
    # 04
    b += BOX('card', 975.4, 200, 234.6, 308.8)
    b += STEP('04', 989.8, 214.6, '전달', 'Delivery')
    b += T('q', 989.8, 247.8, '“골라서, 직접 완성해 볼까?”')
    b += BOX('mini', 989.8, 283, 205.8, 112, ' border-color:#D9CEFF; background:#FBFAFF;')
    b += SPARK(999, 291, 12) + T('t10p', 1015, 290, '자동 완성 추천')
    b += T('t12b', 999, 308, '배비치 소비뇽 블랑', extra=' font-size:15.5px; line-height:21px;')
    b += IMG('talk', 999, 335, 15, 4) + IMG('gal', 1017, 335, 15) + T('t10', 1038, 335.5, '연결된 기억 · 카톡, 갤러리')
    b += BOX('btn', 999, 358, 187, 26, ' border-radius:13px;')
    b += USE('i-check', 1063, 365, 12, '#fff')
    b += T('ct fill', 1079, 358, '입력하기', 60, ' height:26px; line-height:26px; font-size:11.5px; text-align:left;')
    b += T('t10p', 989.8, 403, '⑤ 근거 기반 응답 생성') + T('t10m', 989.8, 418, 'Grounded Synthesis')
    for x, w, t in [(989.8, 60, '요약'), (1054, 80, '정확한 이름'), (1138, 57.6, '보낼 말')]:
        b += BOX('pill', x, 436, w, 24, ' border-radius:12px;') + T('ct gray', x, 436, t, w, ' height:24px; line-height:24px; font-size:11.5px;')
    b += T('desc', 989.8, 467, '<b>출처와 함께</b> 건넵니다', extra=' font-size:13.5px;')
    # 핵심 엔진
    b += BOX('chip', 310.8, 506.8, 627.6, 29, ' border-radius:14.5px; border-color:#8B6BFF; box-shadow:0 6px 16px rgba(107,78,255,.14);')
    b += USE('i-nodes', 329.3, 513.1, 16.5)
    b += T('t12p', 351.9, 513, '핵심 엔진 · 온디바이스 Reasoning Embedding', extra=' font-size:13.2px;')
    b += T('t12', 650.3, 512.5, '지금 단서로부터 <b>‘이어지는’</b> 기록을 찾는 경량 모델', extra=' font-size:13.2px;')
    # 00
    b += BOX('card soft', 70, 550.4, 1140, 103.6)
    b += STEP('00', 86.5, 564.9, '사전 준비', 'Indexing', white=True)
    b += T('q', 86.5, 597, '“어디에 뭐가 있는지,<br>미리 정리해 둘까?”', extra=' font-size:21.6px; line-height:22.8px;')
    b += BOX('pill', 290.2, 562.8, 179, 78.8, ' background:#fff;')
    for i, k in enumerate(['talk', 'note', 'mail', 'cal', 'gal']):
        b += IMG(k, 302.5 + i * 31.9, 575.2, 26.9, 7.2 if k in ('talk', 'note') else 0)
    b += T('t12', 302.5, 613, '허용한 기록만 가져오기', extra=' font-weight:600;')
    b += BOX('pill', 496, 562.8, 222.2, 78.8, ' background:#fff;')
    for i, k in enumerate(['i-user', 'i-clock', 'i-pin', 'i-scan']):
        x = 508.3 + i * 30.9
        b += BOX('tile', x, 574.2, 26.9, 26.9) + USE(k, x + 5.2, 579.4, 16.5)
    b += T('t12', 508.3, 613, '사람·시간·장소와 사진 속 글자 정리', extra=' font-weight:600;')
    b += BOX('pill', 745, 562.8, 222.2, 78.8, ' background:#fff; border-color:#D9CEFF;')
    b += BOX('tile', 754, 578.4, 30, 47.7, ' border-radius:9.3px;') + USE('i-db', 758, 591.5, 22)
    b += T('t12p', 792, 565.5, '기억 색인')
    b += T('t11', 792, 582, '<b>키워드 색인</b> · BM25')
    b += T('t11', 792, 599, '<b>벡터 색인</b> · Reasoning Embedding')
    b += T('t11', 792, 616, '<b>메타데이터</b> · date, app, from')
    b += BOX('pill', 993.9, 562.8, 201.7, 78.8, ' background:#fff;')
    for y, k, t in [(574.2, 'i-refresh', '바뀐 기록만 갱신'), (596, 'i-battery', '충전·유휴 시간에'), (617.7, 'i-lock', '기기 밖으로 보내지 않음')]:
        b += USE(k, 1006.3, y, 15.5) + T('t12', 1026.9, y - 1.5, t, extra=' font-weight:600;')
    b += sources(['Wei et al., "A Survey of Reasoning-Intensive Retrieval", ACL 2026', 'Kim et al., "Hi-Q", NeurIPS 2026', 'Trivedi et al., "IRCoT", ACL 2023'], 662, x=72)
    svg = ''
    mid = 349
    svg += LINE(f'M282.8 {mid} L308 {mid}', w=2.4) + f'<circle cx="282.8" cy="{mid}" r="3" fill="#6B4EFF"/>'
    svg += LINE(f'M569.8 {mid} L598 {mid}', w=2.4) + f'<circle cx="569.8" cy="{mid}" r="3" fill="#6B4EFF"/>'
    svg += LINE(f'M939 {mid} L969 {mid}', w=2.4) + f'<circle cx="939" cy="{mid}" r="3" fill="#6B4EFF"/>'
    svg += LINE('M710.5 341 L720 341') + LINE('M814.5 341 L824 341')
    for x in (475, 724, 973.5):
        svg += LINE(f'M{x - 3} 602 L{x + 12} 602', c='#8B6BFF', mk='ah2')
    notes = """Appendix · 파이프라인. Weave의 전체 구조입니다. 기술 질문이 오면 이 장을 먼저 띄웁니다. 칸을 누르면 관련 장으로 넘어갑니다.
우리는 Multi-hop Retrieval 파이프라인을 씁니다. 홉 사이는 질문 다시 쓰기가 잇고, 각 홉의 기록은 Reasoning Embedding이 찾습니다.
평소에는 허용한 기록을 키워드 색인, 벡터 색인, 메타데이터로 정리해 둡니다. 사용자가 부르거나 상황이 맞으면 먼저 1차 통합 검색을 합니다. 여기서 답이 나오면 바로 전달하고, 막히면 하위 질문으로 나눕니다. 찾은 단서를 결합해 질의를 재작성하고, 다음 기록을 찾습니다. 이름은 기록에서 복사하고 날짜는 규칙으로 계산합니다. 2~3홉 안에서 답을 찾으면 sLLM이 요약, 정확한 이름, 보낼 말 가운데 상황에 맞는 모양으로 근거와 함께 건넵니다. 입력과 전송은 사용자가 합니다."""
    page('page-a1', 'Appendix · 파이프라인', '<span class="hl">Weave</span> 파이프라인 전체 구조', '홉 사이는 질문 다시 쓰기가 잇고, 각 홉의 기록은 Reasoning Embedding이 찾습니다.', b, svg, notes)


# ───────────────────────────────── A2 관련 연구 지도
def diagram(kind, x, y):
    """갈래마다 홉을 잇는 모양을 그린 작은 그림(폭 250, 높이 60)."""
    s = f'<g transform="translate({x} {y})">'
    P, L = '#6B4EFF', '#CFC3FF'
    if kind == 'graph':
        pts = [(26, 30), (72, 12), (72, 48), (122, 30), (172, 12), (172, 48), (222, 30)]
        for a, c in [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 6), (5, 6)]:
            s += f'<line x1="{pts[a][0]}" y1="{pts[a][1]}" x2="{pts[c][0]}" y2="{pts[c][1]}" stroke="{L}" stroke-width="2"/>'
        for i, (px, py) in enumerate(pts):
            s += f'<circle cx="{px}" cy="{py}" r="{8 if i in (0, 6) else 6}" fill="{P if i in (0, 3, 6) else "#fff"}" stroke="{P if i in (0, 3, 6) else L}" stroke-width="2"/>'
    elif kind == 'rewrite':
        s += f'<rect x="6" y="14" width="62" height="24" rx="12" fill="#F1ECFF" stroke="{L}"/><rect x="94" y="14" width="62" height="24" rx="8" fill="#fff" stroke="{L}"/><rect x="182" y="14" width="62" height="24" rx="12" fill="{P}"/>'
        s += f'<path d="M70 26H90" stroke="{P}" stroke-width="2" marker-end="url(#ah)"/><path d="M158 26H178" stroke="{P}" stroke-width="2" marker-end="url(#ah)"/>'
        s += f'<path d="M125 40C125 58 37 58 37 42" fill="none" stroke="#8B6BFF" stroke-width="2" stroke-dasharray="4 4" marker-end="url(#ah2)"/>'
    elif kind == 'dense':
        for i in range(3):
            xx = 12 + i * 84
            s += f'<rect x="{xx}" y="16" width="56" height="28" rx="8" fill="{"#F1ECFF" if i < 2 else P}" stroke="{L if i < 2 else P}"/>'
            for j in range(4):
                s += f'<rect x="{xx + 8 + j * 10}" y="{26 - j % 2 * 3}" width="6" height="{8 + j % 2 * 6}" rx="1.5" fill="{"#8B6BFF" if i < 2 else "#fff"}"/>'
            if i < 2:
                s += f'<path d="M{xx + 58} 30H{xx + 80}" stroke="{P}" stroke-width="2" marker-end="url(#ah)"/>'
    else:
        s += f'<rect x="8" y="10" width="72" height="40" rx="8" fill="#2B2640"/><path d="M26 22l-8 8 8 8M62 22l8 8-8 8M49 20l-10 20" fill="none" stroke="#CFC3FF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
        for yy in (8, 30, 52):
            s += f'<path d="M84 30C108 30 108 {yy} 132 {yy}" fill="none" stroke="{L}" stroke-width="2"/><circle cx="140" cy="{yy}" r="7" fill="#fff" stroke="{P}" stroke-width="2"/>'
        s += f'<path d="M150 30H186" stroke="{P}" stroke-width="2" marker-end="url(#ah)"/><circle cx="204" cy="30" r="10" fill="{P}"/>'
    return s + '</g>'


def a2():
    b, svg = '', ''
    stages = ['① 1차 통합 검색', '② 하위 질문 분해', '③ 멀티홉 추론 검색', '④ 단서 결합·질의 재작성', '⑤ 근거 기반 응답 생성']
    w, gap, x0 = 200, 20, 80
    for i, t in enumerate(stages):
        x = x0 + i * (w + gap)
        b += CHIP('', x, 160, w, t, h=28, size=12.5)
        if i < 4:
            svg += LINE(f'M{x + w + 3} 174 L{x + w + gap - 4} 174')
    cards = [
        ('graph', '사전 그래프 구축형', 'Graph-based', 'HippoRAG 2 · PropRAG · GRASP',
         '색인할 때 LLM으로 관계를 뽑아<br>그래프를 만들고 그래프를 따라 탐색',
         '정해 둔 관계를 여러 단계로 연결하고<br>근거를 설명하기 쉬움',
         '기록이 들어올 때마다 관계 추출 필요', None),
        ('rewrite', '반복 질의 재작성형', 'Iterative Rewriting', 'IRCoT · Hi-Q · DER-RAG',
         '찾은 단서를 넣어 질문을 다시 쓰고<br>한 번 더 검색',
         '그래프와 추가 학습 없이<br>임베딩을 갈아 끼울 수 있음',
         '홉마다 LLM 호출 필요<br>1~2B sLLM으로 경량화', 'Weave 기본 경로'),
        ('dense', '다중홉 밀집 임베딩형', 'Multi-Hop Dense', 'MDR · GRITHopper',
         '질문과 찾은 기록을 함께 인코딩해<br>다음 기록을 탐색',
         '글을 생성하지 않아<br>탐색이 빠름',
         '개인 대화 데이터로 학습 필요', 'Weave 보조 경로'),
        ('code', '코드 에이전트 탐색형', 'Agentic Search', '코딩 에이전트 · RLM · PyRAG',
         'LLM이 코퍼스를 프로그램처럼 탐색하고<br>하위 호출을 반복',
         '중간 상태를 명시하고<br>실행 결과를 그대로 활용',
         '코드를 짜고 실행할 LLM 필요', None),
    ]
    cw, cg, cx0, cy, ch = 278, 13.3, 64, 200, 342
    for i, (k, nm, en, pp, m1, m2, m3, tag) in enumerate(cards):
        x = cx0 + i * (cw + cg)
        on = tag == 'Weave 기본 경로'
        b += BOX('card on' if on else 'card', x, cy, cw, ch)
        svg += diagram(k, x + 14, cy + 12)
        tx = x + 16
        b += T('t15b', tx, cy + 80, nm)
        b += T('t11p', tx, cy + 103, en)
        b += T('t10m', tx, cy + 121, pp)
        if tag:
            tw_ = tw(tag, 10.5, True) + 30
            b += BOX('chip fill' if on else 'chip soft', x + cw - tw_ - 10, cy + 100, tw_, 20, ' border-radius:10px;')
            b += IMG('spoolw' if on else 'spool', x + cw - tw_ - 4, cy + 103, 14)
            b += T('ct fill' if on else 'ct', x + cw - tw_ + 12, cy + 100, tag, tw_ - 20, ' height:20px; line-height:20px; font-size:10.5px; text-align:left;')
        b += BOX('bar', tx, cy + 142, cw - 32, 1)
        for j, (lab, txt) in enumerate([('핵심 연결 메커니즘', m1), ('강점', m2), ('온디바이스 적용 시 한계', m3)]):
            yy = cy + 150 + j * 64
            b += T('t10p', tx, yy, lab)
            b += T('t12', tx, yy + 17, txt, extra=' font-size:12.3px; line-height:17.5px;')
    # Hi-Q 한 줄
    b += BOX('lav', 64, 552, 1152, 54, ' border-radius:14px;')
    b += IMG('spool', 78, 567, 24)
    b += T('t12', 112, 560, '<b>Hi-Q(NeurIPS 2026)</b>는 막힌 질문만 계층적으로 나눠, IRCoT와 같은 LLM 호출 수에서 입력 토큰을 <em>9.4배</em> 줄이면서 멀티홉 정확도를 높였습니다.<br><b>Weave는 이 구조를 1~2B 온디바이스 sLLM에 맞게 경량화하여 적용합니다.</b>', extra=' font-size:13px; line-height:19px;')
    b += sources(['Gutiérrez et al., "HippoRAG 2", ICML 2025', 'Jenkins et al., "GRASP", arXiv 2605.16598', 'Trivedi et al., "IRCoT", ACL 2023', 'Kim et al., "Hi-Q", NeurIPS 2026',
                  'Lee & Lim, "DER-RAG", arXiv 2609.06065', 'Xiong et al., "MDR", ICLR 2021', 'Erker et al., "GRITHopper", EACL 2026'], 616)
    notes = """Appendix · 관련 연구. Multi-hop Retrieval에는 정해진 표준이 없고, 논문들이 공유하는 뼈대가 있습니다. 위의 다섯 단계입니다. 홉을 잇는 방법에 따라 갈래는 넷입니다.
Weave는 반복 질의 재작성형을 기본 경로로 택했습니다. 그래프를 미리 만들지 않고 임베딩을 바꿔 쓸 수 있어 온디바이스에 맞기 때문입니다. 다중홉 밀집 임베딩형은 보조 경로로 둡니다.
출발점으로 삼은 Hi-Q는 막힌 질문만 나누는 구조로, IRCoT와 같은 LLM 호출 수(2.93회와 2.92회)에서 입력 토큰을 9.4배 줄이고 EM을 10.4점 높였습니다."""
    page('page-a2', 'Appendix · 관련 연구', '<span class="hl">Multi-hop Retrieval</span> 관련 연구 지도', '표준 파이프라인은 없고 공통 뼈대가 있습니다. Weave는 반복 질의 재작성형을 기본으로 합니다.', b, svg, notes)


# ───────────────────────────────── A3 Reasoning Embedding
def a3():
    b, svg = '', ''
    # 왼쪽: 역할
    b += BOX('card', 64, 160, 540, 446)
    b += T('t15b', 84, 174, 'Reasoning Embedding의 역할')
    qx, ex, rx = 84, 306, 424
    for label, y in (('Hop 1', 206), ('Hop 2', 310)):
        b += T('t11p', 84, y, label)
    # Hop 1
    y1 = 226
    b += BOX('mini on', qx, y1, 196, 40) + T('t11b', qx + 12, y1 + 12, '지은이네 집들이는 언제였지?')
    b += BOX('lav', ex, y1, 92, 40) + T('t10p', ex, y1 + 6, 'Reasoning<br>Embedding', 92, ' text-align:center; line-height:14px;')
    b += BOX('mini', rx, y1 - 8, 162, 56)
    b += IMG('talk', rx + 9, y1 - 1, 20, 5) + T('t10b', rx + 35, y1 + 2, '지은')
    b += T('t10', rx + 9, y1 + 26, '휴지 안 사 와도 돼') + T('t10p', rx + 108, y1 + 2, '3/15 (일)')
    svg += LINE(f'M{qx + 199} {y1 + 20} L{ex - 4} {y1 + 20}') + LINE(f'M{ex + 95} {y1 + 20} L{rx - 4} {y1 + 20}')
    # 다시 쓰기
    svg += LINE(f'M{rx + 81} {y1 + 50} C{rx + 81} {y1 + 84} {qx + 98} {y1 + 60} {qx + 98} {y1 + 98}', c='#8B6BFF', mk='ah2', dash='4 4')
    b += T('t10p', 286, y1 + 80, '찾은 날짜로 질문 재작성')
    # Hop 2
    y2 = 330
    b += BOX('mini on', qx, y2, 196, 40)
    b += BOX('chip fill', qx + 8, y2 + 10, 58, 20, ' border-radius:10px;') + T('ct fill', qx + 8, y2 + 10, '3/15 (일)', 58, ' height:20px; line-height:20px; font-size:10.5px;')
    b += T('t11b', qx + 70, y2 + 12, '에 마셨던 와인은?')
    b += BOX('lav', ex, y2, 92, 40) + T('t10p', ex, y2 + 6, 'Reasoning<br>Embedding', 92, ' text-align:center; line-height:14px;')
    b += PHOTO(WINE, rx, y2 - 14, 162, 68, 11)
    b += IMG('gal', rx + 8, y2 - 8, 18, 0, ' z-index:6;')
    svg += LINE(f'M{qx + 199} {y2 + 20} L{ex - 4} {y2 + 20}') + LINE(f'M{ex + 95} {y2 + 20} L{rx - 4} {y2 + 20}')
    b += T('t12', 84, 396, '임베딩 모델은 이전 홉의 상태를 무겁게 유지하는 대신, 1차 검색에서 찾은 단서가 결합된<br><b>재작성 질의(Rewritten Query)를 매 홉마다 독립적으로 인코딩</b>합니다.', extra=' font-size:13px; line-height:20px;')
    # 튜닝 세 가지
    items = [('i-nodes', '추론형 데이터로 튜닝', '단서와 다음 근거를<br>잇도록 학습'), ('i-cards', '헷갈리는 오답으로 학습', '같은 주제의 오답을<br>구분하도록 학습'), ('i-cpu', '온디바이스 경량', '기록 벡터는 미리 저장,<br>질문만 계산')]
    for i, (ic, t1, t2) in enumerate(items):
        x = 84 + i * 168
        b += BOX('pill', x, 450, 160, 140)
        b += BOX('tile', x + 12, 462, 30, 30) + USE(ic, x + 19, 469, 16)
        b += T('t11b', x + 12, 504, t1)
        b += T('t11', x + 12, 528, t2, extra=' line-height:17px;')
    # 오른쪽: 추론 유형
    b += BOX('card', 618, 160, 598, 446)
    b += T('t15b', 638, 174, '우리 시나리오의 추론 유형')
    b += T('t10m', 638 + tw('우리 시나리오의 추론 유형', 16, True) + 10, 180, 'RIR Survey 다섯 유형 기준')
    for i, (nm, kr, d, weave) in enumerate([
        ('Analytical', '분석 추론', '기록이 추론 사슬의 빈칸을 채웁니다.<br>문제를 이어지는 하위 질문으로 나눕니다.', '세 시나리오의 전체 흐름'),
        ('Numerical', '수치 추론', '수치 사실과 규칙으로 값이나 결정을<br>정합니다. 시간 비교를 포함합니다.', 'UX 1: 11/3과 11/10 회의 비교'),
    ]):
        x = 638 + i * 284
        b += BOX('mini on', x, 206, 274, 122)
        b += T('t14b', x + 14, 216, nm) + T('t10p', x + 14 + tw(nm, 14.5, True) + 8, 221, kr)
        b += T('t11', x + 14, 241, d, extra=' line-height:17px;')
        b += BOX('bar', x + 14, 282, 246, 1)
        b += IMG('spool', x + 14, 292, 18) + T('t11b', x + 38, 293, weave)
    b += BOX('pill', 638, 338, 558, 62)
    b += T('t11b', 652, 347, '향후 확장 가능 영역')
    for i, (en, kr) in enumerate([('Deductive', '규칙 적용'), ('Analogical', '유사 사례'), ('Causal', '원인 추적')]):
        x = 652 + i * 180
        b += T('t11p', x, 370, en) + T('t11', x + tw(en, 11.5, True) + 7, 370, kr)
    # 상식 추론
    b += BOX('lav', 638, 410, 558, 180, ' border-radius:14px;')
    b += T('t12b', 652, 420, '일상 상식 추론: 글에 없는 사실을 잇습니다')
    for i, (ic, a, c) in enumerate([('talk', '휴지 안 사 와도 돼', '집들이 초대'), ('talk', '이 갈색병 좋대', '에스티 로더 나이트 리페어')]):
        y = 446 + i * 42
        b += BOX('mini', 652, y, 196, 34)
        b += IMG(ic, 660, y + 8, 18, 5) + T('t11', 684, y + 9, a)
        svg += LINE(f'M852 {y + 17} L880 {y + 17}')
        w_ = tw(c, 12, True) + 26
        b += CHIP('fill', 886, y + 5, w_, c, h=24, size=12)
    b += T('t11', 652, 534, '서베이의 개방형 영역(일반 지식과 상식, 숨은 의도)이고, ImpliRet의 World Knowledge 유형과 같은 구조입니다.')
    b += T('t11', 652, 554, '<b>Weave는 보낸 사람 같은 필터로 후보를 줄인 뒤 추론합니다.</b>')
    b += sources(['Wei et al., "A Survey of Reasoning-Intensive Retrieval", ACL 2026', 'Taghavi et al., "ImpliRet", EMNLP 2025', 'Su et al., "BRIGHT", ICLR 2025', 'Shao et al., "ReasonIR", COLM 2025'], 616)
    notes = """Appendix · Reasoning Embedding. 찾는 일은 임베딩이, 잇는 일은 질문 다시 쓰기가 맡습니다.
임베딩 모델은 이전 홉의 상태를 무겁게 유지하는 대신, 1차 검색에서 찾은 단서가 결합된 재작성 질의를 매 홉마다 독립적으로 인코딩합니다. 그래서 일반 임베딩과 같은 구조를 유지하면서, 추론형 데이터와 헷갈리는 오답으로 튜닝합니다.
추론 유형으로는 세 시나리오의 전체 흐름이 Analytical이고, UX 1에서 회의 날짜를 비교하는 단계가 Numerical입니다. 휴지 안 사 와도 돼를 집들이 초대로 읽는 단계는 서베이의 개방형 영역, ImpliRet의 World Knowledge 유형과 같은 구조입니다."""
    page('page-a3', 'Appendix · Reasoning Embedding', '<span class="hl">Reasoning Embedding</span>의 역할과 추론 유형', '찾는 일은 임베딩이, 잇는 일은 질문 다시 쓰기가 맡습니다.', b, svg, notes)


# ───────────────────────────────── A4~A6 시나리오 상세: 단계 카드 8개
def rec(x, y, w, ic, title, meta, body=None, on=False, off=False, tag=None, r=5):
    """앱 기록 한 줄(데모 앱의 연결된 기억과 같은 모양)."""
    h = 60 if body else 38
    s = BOX('mini ' + ('on' if on else 'off' if off else ''), x, y, w, h)
    op = ' opacity:.5;' if off else ''
    s += IMG(ic, x + 8, y + 8, 21, r, op)
    s += T('t10b', x + 35, y + 5, title, extra=' color:#8E88A0;' if off else '')
    s += T('t10m', x + 35, y + 19, meta)
    if body:
        s += T('t10', x + 10, y + 39, body, extra=' color:#A8A3B5;' if off else '')
    if tag:
        tw_ = tw(tag, 9.5, True) + 14
        s += BOX('chip soft', x + w - tw_ - 7, y + 8, tw_, 17, ' border-radius:8.5px;') + T('ct', x + w - tw_ - 7, y + 8, tag, tw_, ' height:17px; line-height:17px; font-size:9.5px;')
    return s


def qbar(x, y, w, text):
    """Weave 검색창: 실타래 아이콘 + 검색어 + 보라 버튼."""
    s = BOX('chip', x, y, w, 32, ' border-radius:16px; border-color:#CFC3FF;')
    s += IMG('spool', x + 9, y + 7, 18) + T('t11b', x + 32, y + 8, text)
    s += f'  <svg class="app" viewBox="0 0 24 24" style="left:{x + w - 27}px; top:{y + 5}px; width:22px; height:22px;"><circle cx="12" cy="12" r="12" fill="#6B4EFF"/><path d="M12 18V7M7 11.5 12 6.5l5 5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>\n'
    return s


def subq(x, y, w, items):
    """하위 질문 판: 번호 + 질문, 모르는 말은 점선 칩."""
    s = ''
    for i, it in enumerate(items):
        yy = y + i * 36
        s += BOX('pill', x, yy, w, 30, ' border-radius:10px;' + (' background:#F4F0FF; border-color:#E3D9FF;' if i == 0 else ''))
        s += BOX('no', x + 7, yy + 6, 18, 18, ' border-radius:9px;') + T('no-t', x + 7, yy + 6, str(i + 1), extra=' width:18px; height:18px; line-height:18px; font-size:10.5px;')
        tx = x + 31
        if isinstance(it, tuple):
            cw_ = tw(it[0], 10.5, True) + 16
            s += BOX('chip dash', tx, yy + 6, cw_, 18, ' border-radius:9px;') + T('ct', tx, yy + 6, it[0], cw_, ' height:18px; line-height:18px; font-size:10.5px;')
            s += T('t11b', tx + cw_ + 4, yy + 7, it[1], extra=' color:#8E88A0;')
        else:
            s += T('t11b', tx, yy + 7, it)
    return s


def rewrite(x, y, w, chip, rest, flt):
    """다시 쓴 질문 + 메타데이터 필터."""
    cw_ = tw(chip, 11, True) + 18
    s = BOX('mini on', x, y, w, 36)
    s += BOX('chip fill', x + 8, y + 8, cw_, 20, ' border-radius:10px;') + T('ct fill', x + 8, y + 8, chip, cw_, ' height:20px; line-height:20px; font-size:11px;')
    s += T('t11b', x + 12 + cw_, y + 10, rest)
    fw_ = tw('필터 ' + flt, 10.5, True) + 22
    s += BOX('chip dash', x, y + 46, fw_, 22, ' border-radius:11px;') + T('ct', x, y + 46, '필터 ' + flt, fw_, ' height:22px; line-height:22px; font-size:10.5px;')
    return s


def answer(x, y, w, label, lines, btn=None):
    """✦ 라벨 카드 + (있으면) 보라 버튼. 카드에는 글만."""
    n = len(lines)
    h = 22 + n * 14.5
    s = BOX('lav', x, y - 2, w, h)
    s += SPARK(x + 7, y + 3, 11) + T('t10p', x + 21, y + 1, label)
    s += T('t10b', x + 8, y + 17, '<br>'.join(lines), extra=' font-size:11px; line-height:14.5px;')
    if btn:
        s += BOX('btn', x, y + h + 2, w, 22, ' border-radius:11px;')
        s += T('ct fill', x, y + h + 2, btn, w, ' height:22px; line-height:22px; font-size:11px;')
    return s


def ux_page(name, chip, title, sub, steps, srcs, notes):
    b, svg = '', ''
    cw, gx, x0, ys, ch = 278, 13.3, 64, (158, 386), 216
    for i, st in enumerate(steps):
        col, row = i % 4, i // 4
        x, y = x0 + col * (cw + gx), ys[row]
        on = st.get('on')
        b += BOX('card on' if on else 'card', x, y, cw, ch)
        b += BOX('no', x + 12, y + 12, 24, 24) + T('no-t', x + 12, y + 12, st['no'])
        b += T('t12b', x + 43, y + 9, st['name'], extra=' font-size:13.2px; line-height:17px;')
        b += T('t10p', x + 43, y + 26, st['en'], extra=' color:#8B6BFF; font-weight:600;')
        b += st['ui'](x + 12, y + 46, cw - 24)
        b += T('t11', x + 14, y + 128, st['do'], extra=' line-height:16px; font-size:11.3px;')
        b += BOX('bar', x + 14, y + 166, cw - 28, 1)
        b += T('t10p', x + 14, y + 172, '모델') + T('t10', x + 42, y + 172, st['model'])
        b += T('t10p', x + 14, y + 189, '근거') + T('t10', x + 42, y + 189, st['ref'])
        for v in (st['model'], st['ref']):
            if tw(v, 10.5) > cw - 54:
                print('  ! 칸보다 김:', name, st['no'], v)
        for ln in st['do'].split('<br>'):
            if tw(ln, 11.3) > cw - 26:
                print('  ! 칸보다 김:', name, st['no'], ln)
        if col < 3 and i + 1 < len(steps) and (i + 1) // 4 == row:
            svg += f'<path d="M{x + cw + 2.5} {y + 24} l{gx - 5} 0" stroke="#6B4EFF" stroke-width="2" stroke-linecap="round"/>'
    # 윗줄 끝 → 아랫줄 처음
    xr = x0 + 3 * (cw + gx) + cw / 2
    xl = x0 + cw / 2
    svg += LINE(f'M{xr} {ys[0] + ch + 1} L{xr} {ys[0] + ch + 6} L{xl} {ys[0] + ch + 6} L{xl} {ys[1] - 3}', w=2)
    b += sources(srcs, 610)
    page(name, chip, title, sub, b, svg, notes)


def a4():
    S = '삼성기술전 시연 내용'
    steps = [
        dict(no='01', name='순간 감지', en='Trigger',
             ui=lambda x, y, w: T('t10b', x + 2, y + 2, '재웅 선배') + BOX('chip soft', x + 58, y, 48, 18, ' border-radius:9px; background:#E9F7EE; border-color:#E9F7EE;') + T('ct', x + 58, y, '통화 중', 48, ' height:18px; line-height:18px; font-size:10px; color:#1E9E55;') + qbar(x, y + 28, w, S),
             do='통화 화면에서 위로 밀어 직접 입력합니다.<br>키보드가 없는 화면의 입구입니다.', model='사용자 호출', ref='Weave 온디바이스 UX 설계'),
        dict(no='1', name='1차 통합 검색', en='Single-Hop',
             ui=lambda x, y, w: rec(x, y, w, 'note', '삼성기술전 준비 회의', '삼성노트 · 11월 3일 (화)', '제품 소개 → 라이브 데모 → Q&amp;A', off=True, tag='이전 안'),
             do='11/3 회의록과 v1 파일이 먼저 올라옵니다.<br>답처럼 보이지만 옛 내용입니다.', model='BM25 + Reasoning Embedding', ref='IRCoT (ACL 2023), BRIGHT (ICLR 2025)'),
        dict(no='2', name='하위 질문 분해', en='Decomposition',
             ui=lambda x, y, w: subq(x, y, w, ['언제 어디서 하지?', '무엇을 어떤 순서로 하지?']),
             do='일정과 순서를 따로 찾도록<br>두 개의 하위 질문으로 나눕니다.', model='sLLM 1~2B', ref='Hi-Q (NeurIPS 2026), ReasonIR (COLM 2025)'),
        dict(no='3', name='1홉 추론 검색', en='Hop Retrieval',
             ui=lambda x, y, w: rec(x, y, w, 'cal', '삼성기술전 시연', '캘린더 · 11월 19일 (목)', '오후 2시, 수원 디지털시티 3번 부스', on=True),
             do='1번은 캘린더에서 찾고,<br>2번은 11/3 회의록에서 찾습니다.', model='Reasoning Embedding', ref='ReasonIR, ReasonEmbed (ACL 2026)'),
        dict(no='4', name='단서 결합·질의 재작성', en='Query Rewriting',
             ui=lambda x, y, w: rewrite(x, y, w, '그 순서', '그 뒤에 바뀌었나?', 'date > 2026-11-03'),
             do='찾은 회의 날짜로 질문을 다시 쓰고,<br>더 나중 기록으로 좁힙니다.', model='기록 복사, 날짜 필터 (Numerical)', ref='Hi-Q, IRCoT, RIR Survey (ACL 2026)'),
        dict(no='3', name='2홉 추론 검색', en='Hop Retrieval',
             ui=lambda x, y, w: rec(x, y, w, 'note', '주간 회의', '삼성노트 · 11월 10일 (화)', '문제 상황 → 라이브 데모 → 관람객 체험', on=True),
             do='‘기술전’도 ‘시연’도 없는 주간 회의에서<br>바뀐 순서를 찾습니다.', model='Reasoning Embedding', ref='LongMemEval (ICLR 2025)'),
        dict(no='3', name='3홉 추론 검색', en='Hop Retrieval',
             ui=lambda x, y, w: rec(x, y, w, 'mail', '최종본 공유드려요', '메일 · 민수 · 11월 12일 (목)', '첨부: Demo_Final.pptx', on=True),
             do='‘민수님이 최종 정리 후 공유 예정’을<br>단서로 민수 메일에서 최종본을 찾습니다.', model='보낸 사람·날짜 필터 + Embedding', ref='DER-RAG, MDR (ICLR 2021)'),
        dict(no='5', name='근거 기반 응답 생성', en='Grounded Synthesis', on=True,
             ui=lambda x, y, w: answer(x, y, w, '요약', ['시연은 11월 19일(목) 오후 2시, 수원 3번 부스예요.', '순서는 문제 상황, 라이브 데모, 관람객 체험이에요.', '최종본 Demo_Final.pptx는 민수님 메일에 있어요.']),
             do='날짜순으로 세워 마지막 결정을 요약하고,<br>최종본이 있는 메일까지 알려 줍니다.', model='sLLM, 이름·날짜 복사 검사', ref='LongMemEval (Chain-of-Note), Hi-Q'),
    ]
    srcs = ['Wu et al., "LongMemEval", ICLR 2025', 'Kim et al., "Hi-Q", NeurIPS 2026', 'Trivedi et al., "IRCoT", ACL 2023', 'Su et al., "BRIGHT", ICLR 2025', 'Shao et al., "ReasonIR", COLM 2025',
            'Wei et al., "RIR Survey", ACL 2026', 'Chen et al., "ReasonEmbed", ACL 2026', 'Lee & Lim, "DER-RAG", arXiv 2609.06065', 'Xiong et al., "MDR", ICLR 2021']
    notes = """Appendix · UX 1 상세. 통화 중 재웅 선배의 질문에 답하는 절차입니다.
처음 검색에는 11월 3일 회의록과 v1 파일이 올라옵니다. Weave는 일정과 순서를 하위 질문으로 나눠 찾고, 찾은 날짜보다 나중 기록으로 좁혀 11월 10일 주간 회의를 찾습니다. 주간 회의의 민수님이 최종 정리 후 공유 예정이라는 말을 단서로 민수의 메일에서 최종본을 찾습니다.
순서는 임베딩이 맞추지 않습니다. 임베딩이 같은 일의 기록을 찾고, 메타데이터 날짜가 앞뒤를 가리고, sLLM이 마지막 결정을 읽습니다. 관련 연구로는 LongMemEval의 Knowledge Update가 같은 문제를 다룹니다."""
    ux_page('page-a4', 'Appendix · UX 1 상세', 'UX 1 <span class="hl">기록 통합 검색</span>: 단계별 모델과 근거', '재웅 선배: “프로님, 우리 팀이 맡은 삼성기술전 시연 어떻게 진행하기로 했었죠?”', steps, srcs, notes)


def a5():
    Q = '지은이네 집들이 때 마셨던 와인'

    def index(x, y, w):
        s = ''
        for i, k in enumerate(['talk', 'gal']):
            s += IMG(k, x + 2 + i * 26, y + 2, 21, 5 if k == 'talk' else 0)
        s += T('t10', x + 58, y + 6, '카톡 글자, 사진')
        s += BOX('mini', x, y + 32, w, 36) + T('t10', x + 10, y + 36, '벡터 [-0.69, -0.60, 0.77, …]') + T('t10b', x + 10, y + 51, '{ date: "2026-03-15", app: "kakaotalk" }')
        return s

    def photo(x, y, w):
        s = PHOTO(WINE, x, y, 96, 72, 10)
        s += BOX('mini on', x + 104, y + 6, w - 104, 34) + T('t10p', x + 112, y + 16, 'BABICH SAUVIGNON')
        s += PHOTO(TABLE, x + 104, y + 46, 40, 26, 6) + T('t10m', x + 150, y + 52, '식탁 사진 탈락')
        return s

    def first(x, y, w):
        return rec(x, y - 2, w, 'note', '집들이 선물', '삼성노트 · 3월 14일', off=True, tag='날짜 없음') + rec(x, y + 38, w, 'gal', '3/20 와인바 사진', '갤러리 · 다른 날', off=True, tag='다른 날')

    steps = [
        dict(no='00', name='사전 준비', en='Indexing', ui=index,
             do='허용한 기록을 벡터, 키워드, 메타데이터로<br>미리 저장합니다.', model='Reasoning Embedding, BM25, OCR', ref='LongMemEval (ICLR 2025)'),
        dict(no='01', name='순간 감지', en='Trigger',
             ui=lambda x, y, w: qbar(x, y + 4, w, Q) + T('t10', x + 4, y + 46, '구글 검색창 + 키보드 실타래 버튼'),
             do='이름이 떠오르지 않을 때<br>실타래 버튼을 직접 누릅니다.', model='사용자 호출', ref='Weave 온디바이스 UX 설계'),
        dict(no='1', name='1차 통합 검색', en='Single-Hop', ui=first,
             do='선물 메모, 다른 날 와인 사진이 올라옵니다.<br>집들이 날짜를 찾지 못합니다.', model='BM25 + Reasoning Embedding', ref='IRCoT (ACL 2023), BRIGHT (ICLR 2025)'),
        dict(no='2', name='하위 질문 분해', en='Decomposition',
             ui=lambda x, y, w: subq(x, y, w, ['지은이네 집들이는 언제였지?', ('그날', '마셨던 와인은?')]),
             do='먼저 풀 질문과<br>빈칸이 있는 질문으로 나눕니다.', model='sLLM 1~2B', ref='Hi-Q (NeurIPS 2026), ReasonIR (COLM 2025)'),
        dict(no='3', name='1홉 추론 검색', en='Hop Retrieval',
             ui=lambda x, y, w: rec(x, y, w, 'talk', '지은', '카카오톡 · 3월 15일 (일)', '박스 정리 다 했어! 이따 올 때 휴지 안 사 와도 돼', on=True),
             do='‘휴지 안 사 와도 돼’를<br>집들이 초대로 추론합니다.', model='보낸 사람 필터 + Reasoning Embedding', ref='ImpliRet (EMNLP 2025), RIR Survey'),
        dict(no='4', name='단서 결합·질의 재작성', en='Query Rewriting',
             ui=lambda x, y, w: rewrite(x, y, w, '3/15 (일)', '에 마셨던 와인은?', 'date: "2026-03-15"'),
             do='카톡에 저장된 날짜를 그대로 넣고<br>그날 기록만 남깁니다.', model='메타데이터 복사, 날짜 필터', ref='Hi-Q, LongMemEval'),
        dict(no='3', name='2홉 추론 검색', en='Hop Retrieval', ui=photo,
             do='그날 사진 중 와인 사진을 찾고<br>라벨을 읽어 이름을 복원합니다.', model='Reasoning Embedding + OCR', ref='DocHop-QA (EMNLP 2026)'),
        dict(no='5', name='근거 기반 응답 생성', en='Grounded Synthesis', on=True,
             ui=lambda x, y, w: answer(x, y, w, '자동 완성 추천', ['배비치 소비뇽 블랑'], '입력하기'),
             do='정확한 이름을 출처와 함께 건넵니다.<br>입력은 사용자가 합니다.', model='sLLM, 이름 복사 검사', ref='Hi-Q (NeurIPS 2026)'),
    ]
    srcs = ['Trivedi et al., "IRCoT", ACL 2023', 'Kim et al., "Hi-Q", NeurIPS 2026', 'Taghavi et al., "ImpliRet", EMNLP 2025', 'Wei et al., "RIR Survey", ACL 2026', 'Wu et al., "LongMemEval", ICLR 2025',
            'Su et al., "BRIGHT", ICLR 2025', 'Shao et al., "ReasonIR", COLM 2025', 'Park et al., "DocHop-QA", EMNLP 2026']
    notes = """Appendix · UX 2 상세. How it Works에서 본 절차를 모델과 근거까지 적은 장입니다.
1홉에서 카톡 문맥 추론으로 집들이 날짜 3월 15일을 알아내고, 그 날짜 필터로 다른 날 마신 와인바 사진을 걸러냅니다. 2홉에서는 그날 저녁 사진 가운데 와인 사진을 찾아 라벨을 읽고 정확한 이름을 복원합니다.
이번 단서는 날짜지만, 별칭이나 맡은 일 같은 내용도 같은 방식으로 잇습니다. UX 1과 UX 3이 그 예입니다."""
    ux_page('page-a5', 'Appendix · UX 2 상세', 'UX 2 <span class="hl">단서로 찾는 기억</span>: 단계별 모델과 근거', '구글 검색창: “지은이네 집들이 때 마셨던 와인”', steps, srcs, notes)


def a6():
    def signals(x, y, w):
        s = BOX('chip', x, y, 108, 24, ' border-radius:12px;') + USE('i-pin', x + 7, y + 5, 14, '#2F7BF6') + T('t10b', x + 24, y + 5, '인천공항 면세점')
        s += BOX('chip', x + 114, y, w - 114, 24, ' border-radius:12px;') + IMG('wal', x + 121, y + 4, 16) + T('t10b', x + 142, y + 5, '싱가포르 → 인천')
        s += BOX('chip', x, y + 30, 112, 24, ' border-radius:12px;') + IMG('talk', x + 7, y + 34, 16, 4) + T('t10b', x + 28, y + 35, '아내와 대화 중')
        s += f'  <svg class="app" viewBox="0 0 40 40" style="left:{x + 128}px; top:{y + 26}px; width:36px; height:36px;"><circle cx="20" cy="20" r="20" fill="#6B4EFF" opacity=".18"/><circle cx="20" cy="20" r="14" fill="#6B4EFF"/></svg>\n'
        s += IMG('spoolw', x + 137, y + 35, 18, 0, ' z-index:6;')
        s += T('t10p', x + 170, y + 37, '먼저 반짝')
        return s

    def preview(x, y, w):
        # 카카오톡 링크 미리보기: 이미지와 제목, 도메인
        s = BOX('mini on', x, y - 2, w, 76)
        s += PHOTO(BOTTLE, x + 6, y + 4, 76, 64, 8, '50% 62%')
        s += T('t10m', x + 90, y + 3, '아내가 보낸 링크 미리보기')
        s += T('t10b', x + 90, y + 19, '[신세계백화점] <span style="color:#6B4EFF">에스티 로더</span><br>어드밴스드 나이트 리페어 50ml', extra=' line-height:14px;')
        s += T('t10m', x + 90, y + 51, 'm.ssg.com')
        return s

    def first(x, y, w):
        return T('t10m', x + 2, y + 2, 'Weave가 지금 상황에서 만든 질문') + qbar(x, y + 22, w, '면세점에서 아내에게 사 갈 것은?')

    steps = [
        dict(no='00', name='사전 준비', en='Indexing',
             ui=lambda x, y, w: ''.join(IMG(k, x + 2 + i * 26, y + 2, 21, 5 if k == 'talk' else 0) for i, k in enumerate(['talk', 'wal'])) + T('t10', x + 58, y + 6, '알림 글자, 링크 미리보기, 탑승권') + BOX('mini', x, y + 32, w, 36) + T('t10', x + 10, y + 36, '벡터와 메타데이터로 색인') + T('t10b', x + 10, y + 51, '{ date, app, from }'),
             do='알림의 글자, 링크 미리보기, 월렛 탑승권을<br>미리 색인합니다.', model='Reasoning Embedding', ref='Open Graph, Kakao 스크랩 문서'),
        dict(no='01', name='순간 감지', en='Trigger', ui=signals,
             do='위치, 탑승권, 대화 상대가 귀국을 가리키면<br>실타래 버튼이 먼저 반짝입니다.', model='멀티시그널 컨텍스트 트리거', ref='Samsung Wallet·GPS 연동, Now Brief'),
        dict(no='1', name='첫 질문 생성', en='Proactive Query', ui=first,
             do='사용자가 묻기 전에<br>Weave가 첫 질문을 만듭니다.', model='상황별 틀 + sLLM', ref='Weave 온디바이스 UX 설계'),
        dict(no='2', name='하위 질문 분해', en='Decomposition',
             ui=lambda x, y, w: subq(x, y, w, ['아내가 면세점에서 바란 건?', ('그것', '의 정확한 제품명은?')]),
             do='먼저 풀 질문과<br>빈칸이 있는 질문으로 나눕니다.', model='sLLM 1~2B', ref='Hi-Q (NeurIPS 2026)'),
        dict(no='3', name='1홉 추론 검색', en='Hop Retrieval',
             ui=lambda x, y, w: rec(x, y, w, 'talk', '아내', '카카오톡 · 3주 전', '여보, 동생이 이 갈색병 좋대. 면세점에서 판다더라', on=True),
             do='카톡 알림 글자에서<br>직접 말하지 않은 부탁을 읽습니다.', model='보낸 사람 필터 + Reasoning Embedding', ref='RIR Survey, BESPOKE, ImpliRet'),
        dict(no='4', name='단서 결합·질의 재작성', en='Query Rewriting',
             ui=lambda x, y, w: rewrite(x, y, w, '갈색병', '의 정확한 제품명은?', '같은 메시지의 링크'),
             do='‘갈색병’을 넣어 질문을 다시 쓰고<br>같은 메시지의 링크로 좁힙니다.', model='기록 복사, 메시지 필터', ref='Hi-Q, IRCoT (ACL 2023)'),
        dict(no='3', name='2홉 추론 검색', en='Hop Retrieval', ui=preview,
             do='링크 미리보기의 제목에서<br>정확한 제품명을 읽습니다.', model='링크 메타데이터 + Reasoning Embedding', ref='DocHop-QA (EMNLP 2026), Open Graph'),
        dict(no='5', name='근거 기반 응답 생성', en='Grounded Synthesis', on=True,
             ui=lambda x, y, w: answer(x, y, w, '자동 완성 추천', ['여보, 전에 말한 에스티 로더 갈색병', '면세점에서 사 갈까?'], '입력하기'),
             do='카톡, 월렛, GPS를 엮어 건넵니다.<br>입력과 전송은 사용자가 합니다.', model='sLLM, 대화 말투 반영', ref='Hi-Q (NeurIPS 2026)'),
    ]
    srcs = ['Wei et al., "RIR Survey", ACL 2026', 'Taghavi et al., "ImpliRet", EMNLP 2025', 'Kim et al., "BESPOKE", 2025', 'Kim et al., "Hi-Q", NeurIPS 2026', 'Trivedi et al., "IRCoT", ACL 2023',
            'Park et al., "DocHop-QA", EMNLP 2026', 'The Open Graph Protocol (ogp.me)', 'Kakao DevTalk, "Scrap(스크랩, 미리보기)란?"', 'Samsung Newsroom, "Galaxy S26 Series" (2026. 02)']
    notes = """Appendix · UX 3 상세. 출장에서 돌아와 인천공항에 내린 순간의 절차입니다. 아내와 메시지 세 개를 주고받은 뒤 실타래 버튼이 반짝입니다.
위치와 삼성 월렛 탑승권이 귀국 중임을 알려 주고, 대화 상대가 아내이므로 Weave가 첫 질문을 스스로 만듭니다. 1홉에서 아내의 카톡 알림 글자에서 갈색병 부탁을 찾고, 2홉에서 아내가 함께 보낸 링크의 미리보기를 읽어 에스티 로더 어드밴스드 나이트 리페어 50ml라는 정확한 제품명을 찾습니다. 아내는 갈색병이라고만 말했고, 제품 이름은 미리보기 제목에 있습니다. 알림에 온 링크 주소에서 페이지의 Open Graph 제목과 이미지를 기기에서 읽어 함께 색인합니다.
삼성 S26의 Now Brief도 지원 앱 알림, 메시지, Gmail, Samsung Wallet을 회상 데이터로 씁니다. 월렛을 상황 신호로 쓰는 것은 자연스러운 확장입니다. Now Nudge와 다른 점은, 화면에 보이는 말이 ‘조심히 와’뿐인데도 3주 전 카톡과 링크를 이어 무엇을 살지 찾는다는 점입니다."""
    ux_page('page-a6', 'Appendix · UX 3 상세', 'UX 3 <span class="hl">먼저 건네는 기억</span>: 단계별 모델과 근거', '아내 “고생했어 조심히 와~” 뒤에 실타래 버튼이 먼저 반짝입니다.', steps, srcs, notes)


# ───────────────────────────────── A7 비교 (덱의 차별화 표와 같은 모양)
def a7():
    b, svg = '', ''
    x0, y0, lw, cw, wv = 64, 158, 136, 168, 176
    cols = ['키워드 검색<br>(BM25)', '일반 임베딩', '하이브리드 검색', '지식 그래프<br>(PDE 방식)', 'Samsung Finder<br>Now Nudge']
    rows = [
        ('핵심 탐색 기준', ['같은 단어', '가까운 뜻', '두 순위를 합친<br>한 번 검색', '미리 뽑아 둔 관계', '앱별 자연어 검색,<br>화면 맥락 제안'], '찾은 단서로<br>다시 쓴 질문'),
        ('강점', ['이름, 숫자, 파일명', '표현이 다른<br>같은 내용', '두 방식의 장점', '정해 둔 관계의<br>여러 단계 연결', '앱 안의 사진과 메모,<br>화면 속 요청'], '단어가 다르고<br>단계가 빠진 질문'),
        ('사전 색인 구조', ['단어 색인', '기록 벡터', '단어 색인과 벡터', '기록의 관계 추출', '앱별 색인'], '기록 벡터와<br>메타데이터'),
    ]
    last = [('x', '‘집들이’가 없는<br>초대 카톡, 와인 사진'), ('x', '1위에 오른<br>다른 날 와인 사진'), ('x', '처음 질문에 없는<br>집들이 날짜'), ('t', '그래프에 없는<br>‘휴지 = 집들이’'), ('t', '카톡 초대와 그날 사진을<br>잇는 단계'), ('o', '배비치 소비뇽 블랑까지<br>찾아냅니다')]
    tw_all = lw + cw * 5 + wv
    hh, rh, lh = 58, 72, 84
    th = hh + rh * 3 + lh
    b += BOX('card', x0, y0, tw_all, th + 8)
    wx = x0 + lw + cw * 5
    b += BOX('abs', wx, y0 + 4, wv - 4, th, ' background:#F4F0FF; border-radius:14px;')
    b += BOX('abs', wx, y0 + 4, wv - 4, hh - 4, ' background:#6B4EFF; border-radius:14px 14px 0 0;')
    b += T('t12', x0 + 18, y0 + 20, '검색 방식', extra=' font-weight:700; color:#8E88A0; font-size:13px;')
    for i, c in enumerate(cols):
        x = x0 + lw + i * cw
        n = c.count('<br>') + 1
        b += T('t12b', x, y0 + (20 if n == 1 else 11), c, cw, ' text-align:center; line-height:17px; font-size:13.5px;')
    b += T('t18b', wx, y0 + 16, 'Weave Assist', wv - 4, ' text-align:center; color:#fff; line-height:24px;')
    y = y0 + hh
    for lab, vals, me in rows:
        b += BOX('bar', x0 + 12, y, tw_all - 24, 1)
        b += T('t12b', x0 + 18, y + rh / 2 - 9, lab, extra=' font-size:13px;')
        for i, v in enumerate(vals):
            n = v.count('<br>') + 1
            b += T('t12', x0 + lw + i * cw, y + rh / 2 - 9 * n, v, cw, ' text-align:center; font-size:12.3px;')
        n = me.count('<br>') + 1
        b += T('t12b', wx, y + rh / 2 - 9 * n, me, wv - 4, ' text-align:center; line-height:18px; font-size:12.8px;')
        y += rh
    b += BOX('bar', x0 + 12, y, tw_all - 24, 1)
    b += T('t12b', x0 + 18, y + lh / 2 - 18, '멀티홉 질문<br>‘집들이 와인’', extra=' font-size:13px; line-height:18px;')
    for i, (m, v) in enumerate(last):
        me = i == 5
        x = wx if me else x0 + lw + i * cw
        w = wv - 4 if me else cw
        cx, cy = x + w / 2, y + 19
        if m == 'x':
            svg += f'<path d="M{cx - 7} {cy - 7} L{cx + 7} {cy + 7} M{cx + 7} {cy - 7} L{cx - 7} {cy + 7}" stroke="#E5484D" stroke-width="2.4" stroke-linecap="round" fill="none"/>'
        elif m == 't':
            svg += f'<path d="M{cx} {cy - 8} L{cx + 9} {cy + 7} L{cx - 9} {cy + 7} Z" stroke="#E08A2E" stroke-width="2.4" stroke-linejoin="round" fill="none"/>'
        else:
            svg += f'<circle cx="{cx}" cy="{cy}" r="8.5" stroke="#1E9E55" stroke-width="2.4" fill="none"/>'
        b += T('t12b' if me else 't12', x, y + 33, v, w, ' text-align:center; line-height:17px; font-size:' + ('12.3px;' if me else '11.8px;') + (' color:#6B4EFF;' if me else ''))
    y += lh + 18
    b += BOX('lav', x0, y, tw_all, 44, ' border-radius:14px;')
    b += IMG('spool', x0 + 14, y + 11, 22)
    b += T('t12', x0 + 46, y + 12, '<b>기존 방식을 대체하지 않습니다.</b> Weave도 BM25와 임베딩, 메타데이터를 함께 쓰고, 정확한 값은 메타데이터와 PDE로 잇고, 기록 내용 속 연결은 질문할 때 잇습니다.', extra=' font-size:13px;')
    b += sources(['Robertson & Zaragoza, "BM25 and Beyond", 2009', 'Karpukhin et al., "DPR", EMNLP 2020', 'Cormack et al., "Reciprocal Rank Fusion", SIGIR 2009', 'Oxford Semantic Technologies, RDFox 문서',
                  '삼성전자 뉴스룸, "[갤럭시 언팩 2025] ①" (2025. 01)', 'Samsung 지원, "Understanding Finder on Galaxy phones"', 'Samsung Newsroom, "Galaxy S26 Series" (2026. 02)'], y + 54)
    notes = """Appendix · 비교. 같은 와인 질문을 방식마다 어디까지 찾는지 비교한 표입니다. 각 방식이 잘하는 것부터 말하고, 이 질문에서 막히는 곳을 말합니다.
지식 그래프는 여러 단계 연결이 오히려 강점이고, 막히는 곳은 그래프에 없는 사실입니다. Finder는 One UI 8.5부터 자연어 검색을 지원하고, 공식 대상은 음성 녹음, 통화 녹음, 캘린더, 노트, 리마인더, 내 파일입니다.
Weave의 차별점은 온디바이스에서 미리 정한 항목 없이 원문 기록을 이어 가는 추론 검색입니다."""
    page('page-a7', 'Appendix · 비교', '기존 검색 및 온디바이스 AI 대비 <span class="hl">Weave의 차별점</span>', '같은 멀티홉 질문 ‘지은이네 집들이 때 마셨던 와인’을 방식마다 비교했습니다.', b, svg, notes)


if __name__ == '__main__':
    a1(); a2(); a3(); a4(); a5(); a6(); a7()
    print('ok')
