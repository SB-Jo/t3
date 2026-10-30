"""0927_v1 덱 3차 다듬기 (2026-09-27 21시 요청).

- 3쪽: 왼쪽 검색 카드 높이 +3.8%·위로 14px(안쪽 요소 함께), 강조 타원은 '사라진 건 아니'까지만
- 4쪽: '그 얘기'만 보라('를'은 검정), 성빈·지현 표정을 살짝 고민하는 얼굴로(characters/*-v2.png)
- 5쪽: 새로 구성(p05/page-05-solution.html → 그래픽 레이어 + 편집 가능한 글자·도형), 제목 "Weave의 핵심 UX 3가지를 소개합니다!"
- 6~8쪽 칩 'USER SCENARIO 1~3', 13~15쪽 칩 '기대 효과 1~3'
- 10쪽 부제 '앱과 키보드를 잇는, …'
- 12쪽: 표 카드 아래 여백을 위와 같게, 열 이름 'Weave Assist', 아래에 출시 시기(회색)
- 13~15쪽: 두 상자 안 요소를 9px 위로
- 16쪽: 휴대폰 화면 3장을 6% 키우고 칩 아래 공간 가운데로

사용: python apply_round3.py --test | --deck (백업 4와 같을 때만)
"""
import copy
import hashlib
import importlib.util
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.oxml.ns import qn

import apply_round2 as r2
import header as hd
import pages_p2_p4 as pg
from textmeasure import width

ROOT = Path(__file__).resolve().parents[1]
CL = ROOT.parent
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '4_3차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round3.pptx')
shape, xywh, put, set_text, no_autofit = r2.shape, r2.xywh, r2.put, r2.set_text, r2.no_autofit


# ------------------------------------------------------------------ 3쪽
def p3(s):
    card = shape(s, name='Search card')
    x, y, w, h = xywh(card)
    assert abs(y - 217.6) < 1 and abs(h - 237.5) < 1
    up, grow = 14.0, 9.0                      # 위로 14px, 높이 +9px(+3.8%) → 아래 끝은 5px 올라감
    put(card, y=y - up, h=h + grow)
    for sid in (327, 328, 329, 330, 331, 332, 333, 334):     # 검색창 줄
        sh = shape(s, sid=sid); put(sh, y=xywh(sh)[1] - up)
    for sid in (2, 3, 4):                                    # '검색 결과가 없습니다' 알약: 남은 공간 가운데 유지
        sh = shape(s, sid=sid); put(sh, y=xywh(sh)[1] - (up - grow / 2 - 0.5))
    # 타원: '사라진 건 아니'까지만 덮도록 오른쪽 끝을 줄임 (16pt 굵게, 줄 가운데 x=903.1)
    line2 = '흩어져 있을 뿐, 사라진 건 아니니까요.'
    px = 16 * 4 / 3
    W2 = width(line2, px, 700, -0.4)
    x0 = 653.1 + 250 - W2 / 2
    end = x0 + width('흩어져 있을 뿐, 사라진 건 아니', px, 700, -0.4)
    ell = shape(s, name='Ground shadow')
    ex = xywh(ell)[0]
    put(ell, w=end + 5 - ex)
    return round(end + 5 - ex, 1)


# ------------------------------------------------------------------ 4쪽
def p4(s):
    t3 = shape(s, sid=30)
    assert t3.text_frame.text == '그 얘기를 했었나?'
    set_text(t3, [[('그 얘기', '6666FF', True), ('를 했었나?', '15151C', True)]])
    no_autofit(t3)
    sb = shape(s, name='성빈 (6쪽 그림체)'); jh = shape(s, name='지현 (8쪽 그림체)')
    H, bottom = 130.0, 676.0
    for pic, path, crop, mirror, cx in ((sb, ROOT / 'characters' / 'sungbin-v2.png', (0, 80, 1254, 1040), False, 155.0),
                                        (jh, ROOT / 'characters' / 'jihyun-v2.png', (0, 30, 1254, 1040), True, 1137.0)):
        pg.replace_picture(s, pic, pg.portrait_png(path, crop, mirror=mirror))
        w = H * (crop[2] - crop[0]) / (crop[3] - crop[1])
        put(pic, x=cx - w / 2, y=bottom - H, w=w, h=H)
    pg.drop_unused_images(s)


# ------------------------------------------------------------------ 5쪽 (새 구성)
spec = importlib.util.spec_from_file_location('build_pptx', CL / 'tools' / 'build_pptx.py')
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)
bp.OUT = ROOT / 'p05' / 'out'
P5_NOTES = (ROOT / 'p05' / 'notes-page-05.txt')


def ensure_notes_body(prs, slide):
    ns = slide.notes_slide
    if ns.notes_text_frame is None:
        body = next(copy.deepcopy(sp) for s in prs.slides if s.has_notes_slide
                    for sp in s.notes_slide.shapes._spTree.iter(qn('p:sp')) if sp.xpath('.//p:ph[@type="body"]'))
        ns.shapes._spTree.append(body)


INTER_OF = {'Noto Sans KR': 'Inter', 'Noto Sans KR SemiBold': 'Inter SemiBold'}


def interize(slide):
    """새로 만든 글자 상자에서 영문·숫자 조각을 Inter로(손글씨 Nanum Pen은 그대로)."""
    for sh in slide.shapes:
        if not (sh.has_text_frame and sh.name.startswith('Weave text')):
            continue
        for p in sh.text_frame._txBody.findall(qn('a:p')):
            for r in list(p.findall(qn('a:r'))):
                rPr = r.find(qn('a:rPr'))
                face = rPr.find(qn('a:latin')).get('typeface')
                if face not in INTER_OF:
                    continue
                text = r.find(qn('a:t')).text
                segs = hd.split_script(text, 'ko')
                for seg, cls in segs:
                    nr = copy.deepcopy(r)
                    np_ = nr.find(qn('a:rPr'))
                    nr.find(qn('a:t')).text = seg
                    for k in ('lang', 'altLang'):
                        np_.attrib.pop(k, None)
                    np_.set('lang', 'en-US' if cls == 'latin' else 'ko-KR')
                    if cls != 'latin':
                        np_.set('altLang', 'en-US')
                    r2.set_fonts(np_, INTER_OF[face], INTER_OF[face] if cls == 'latin' else face)
                    r.addprevious(nr)
                p.remove(r)


def p5(prs, s, bg):
    ensure_notes_body(prs, s)
    bp.fill_slide(s, 'page-05-solution', bg, P5_NOTES.read_text(encoding='utf-8').strip())
    interize(s)
    # 머리 도형 이름을 붙여 공통 규격으로
    names = {'SOLUTION: WEAVE ASSIST': 'Header chip', 'Weave의 핵심 UX 3가지를 소개합니다!': 'Header title',
             '대화·메모·캘린더·갤러리에 흩어진 기록을 엮어, 필요한 순간 건네는 온디바이스 AI': 'Header subtitle'}
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() in names:
            sh.name = names.pop(sh.text_frame.text.strip())
    assert not names, names
    pg.drop_unused_images(s)


# ------------------------------------------------------------------ 12쪽
RELEASE = '* 출시: Samsung Writing Assist (2025. 02, Galaxy S25) · Samsung Now Nudge (2026. 03, Galaxy S26) · Kanana in KakaoTalk (2026. 03)'


def p12(prs, s):
    card = shape(s, name='Shape 6')
    head = shape(s, name='Shape 12')
    last = shape(s, name='Shape 63')
    cy = xywh(card)[1]
    top_gap = xywh(head)[1] - cy
    bottom = xywh(last)[1] + xywh(last)[3]
    put(card, h=bottom + top_gap - cy)
    t = shape(s, name='Text 13')
    assert t.text_frame.text == 'Weave'
    set_text(t, [[('Weave Assist', None, None)]])
    no_autofit(t, algn='ctr')
    hx, _, hw, _ = xywh(head)
    put(t, x=hx, w=hw)
    # 출시 시기: 13쪽 출처 줄과 같은 서식·위치
    src13 = next(sh for sh in prs.slides[12].shapes if sh.has_text_frame and sh.text_frame.text.startswith('* 출처'))
    el = copy.deepcopy(src13._element)
    s.shapes._spTree.append(el)
    pg.fresh_id(el)
    el.find('.//' + qn('p:cNvPr')).set('name', 'Release dates')
    note = [sh for sh in s.shapes if sh.name == 'Release dates'][0]
    set_text(note, [[(RELEASE, None, None)]])
    no_autofit(note)
    put(note, w=1000)


# ------------------------------------------------------------------ 13~15쪽
BG = ('Shape 0', 'Shape 1', 'Shape 2')


def p13_15(s):
    boxes = [sh for sh in s.shapes if sh.shape_type == 1 and sh.name not in BG and xywh(sh)[3] > 300 and xywh(sh)[1] > 150]
    assert len(boxes) == 2, [b.name for b in boxes]
    moved = 0
    for sh in s.shapes:
        if sh in boxes or sh.name in BG or sh.name.startswith('Header'):
            continue
        x, y, w, h = xywh(sh)
        cx, cy = x + w / 2, y + h / 2
        if any(bx < cx < bx + bw and by < cy < by + bh for bx, by, bw, bh in map(xywh, boxes)):
            put(sh, y=y - 9)
            moved += 1
    return moved


# ------------------------------------------------------------------ 16쪽
def p16(s):
    phones = [sh for sh in s.shapes if sh.name.startswith('App Demo ')]
    assert len(phones) == 3
    k = 1.06
    area_top, area_bottom = 54.0, 720.0                  # 칩 아래 ~ 장표 끝
    for ph in phones:
        x, y, w, h = xywh(ph)
        nw, nh = w * k, h * k
        put(ph, x=x + w / 2 - nw / 2, y=(area_top + area_bottom) / 2 - nh / 2, w=nw, h=nh)


# ------------------------------------------------------------------ 실행
CHIPS = {6: 'USER SCENARIO 1', 7: 'USER SCENARIO 2', 8: 'USER SCENARIO 3', 13: '기대 효과 1', 14: '기대 효과 2', 15: '기대 효과 3'}
TITLES = {5: [('Weave의 ', None), ('핵심 UX 3가지', '6666FF'), ('를 소개합니다!', None)]}
SUBS = {5: [('대화·메모·캘린더·갤러리에 흩어진 기록을 엮어, 필요한 순간 건네는 온디바이스 AI', None, False)],
        10: [('앱과 키보드를 잇는, 시스템 레벨의 통합 경험', None, False)]}


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    assert [r2.labels(prs)[i] for i in (4, 5, 6, 7, 11, 12, 13, 14, 15)] == [
        'SOLUTION: WEAVE ASSIST', 'USER SCENARIO 01', 'USER SCENARIO 02', 'USER SCENARIO 03', '차별화 포인트',
        '기대 효과 01', '기대 효과 02', '기대 효과 03', 'Appendix · App Demo'], r2.labels(prs)
    bg = r2.background_from(prs)
    print('p3 ellipse w', p3(slides[2]))
    p4(slides[3])
    p5(prs, slides[4], bg)
    p12(prs, slides[11])
    for n in (13, 14, 15):
        print(f'p{n} moved', p13_15(slides[n - 1]))
    p16(slides[15])
    for i, s in enumerate(slides, 1):
        if i in CHIPS or i in TITLES or i in SUBS:
            r = hd.apply(s, chip_text=CHIPS.get(i), title_runs=TITLES.get(i), sub_runs=SUBS.get(i), keep_sub_colors=i in (13, 14, 15))
            print(i, r['chip'], f"({r['chip_w']}px)", '|', r.get('title', '-'), '|', r.get('sub', ''))
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        apply(BACKUP, TEST_OUT)
