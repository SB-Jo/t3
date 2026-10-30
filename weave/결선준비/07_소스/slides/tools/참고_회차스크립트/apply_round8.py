"""0927_v1 덱 8차 다듬기 (2026-09-27 23시 반 요청).

- 1쪽: 티저 휴대폰 자판 줄의 실타래 버튼: 원은 같은 색조의 짙은 보라(#CEADF0 → #9565C7), 아이콘은 같은 선 그림을 흰색으로,
       버튼(원·아이콘)은 5% 작게. 사진 속 옛 원은 사진 사본에서 지움(claude-teasers/tools/make-btn-variant.py)
       claude_0927/claude-teasers 'vEsB' 안(`out/teaser-vEsB.png`) = 기존 표지(vEs)와 버튼 원 안만 다름
- 5쪽: (3) 추천 카드의 출처 두 줄을 (2)처럼 회색 상자에 (p05/page-05-solution.html, 7차본은 p05/v4/)
- 4쪽: 아래 두 인물(성빈·지현) 8% 확대. 말풍선 쪽 아래 모서리를 기준으로 키워 말풍선과 겹치지 않고 바깥·위로 커짐
- 6쪽: ① 말풍선을 다시 왼쪽 정렬(6차 자리 44px). 글자는 ③ 카드들처럼 왼쪽에 붙임(왼쪽 여백 20px),
       말풍선 폭은 7차처럼 글자 폭 + 80px라 남는 공간은 오른쪽. ② 보내기 버튼에 터치 표시(손 + 반짝임)
- 7쪽: ②③과 휴대폰 20px 왼쪽 (휴대폰 → 단서 카드 선은 그만큼 길어짐). ① 생각 말풍선은 7차처럼 휴대폰 왼쪽 공간의
       가운데(오른쪽 여백이 조금 적게). 글자는 왼쪽에 붙임(왼쪽 22px, 오른쪽 34px).
       ① 문구 '마신 와인, 그거' → '마신 와인 좋았는데, 그거'
- 8쪽: 현재 위치 카드 오른쪽 여백 79px → 30px, 손글씨 '하마터면 잊을 뻔했네!' → '휴, / Weave 덕분에 / 기억했네!'
- 6~8쪽: 왼쪽 인물 뒤에만 흐린 장면(1 집 · 2 와인샵 · 3 카페, Codex 생성 `p68/scenes/`)을 부드럽게 번지게
- 9쪽: 04 '입력하기' 손에 반짝임 선 3개 (덱 공통 터치 표시, claude_0927 원본 13차)
- 10·11쪽: 손글씨('모두 삼성 안에서!', '이제는 가능해요!') 글자 속성을 5~9쪽 손글씨와 같게
  (lang en-US → ko-KR, 한글 글꼴의 중국어 문자 집합 표시 charset=-122 등 삭제).
  PDF(LibreOffice)에서 이 두 곳만 손글씨가 아닌 Noto Sans KR로 그려지던 원인
- 10쪽: 손글씨 '모두 삼성 안에서!'를 10px 오른쪽으로 (휴대폰 테두리와 붙어 있던 것을 약 12px 띄움)
- 12쪽: 차별화 포인트 표 Kanana 마지막 행(상황 맞춤형 선제안) '제한적' 앞 아이콘 ✕ → △
- 17쪽: 출처 줄의 위 첨자 '⁵'만 Inter로 (Noto Sans KR에 이 글자가 없어 PDF에서 다른 글꼴로 대체되던 곳)

사용: python apply_round8.py --test | --deck (백업 9와 같을 때만)
"""
import copy
import hashlib
import sys
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

import apply_round2 as r2
import apply_round4 as r4
import apply_round6 as r6
import pages_p2_p4 as pg

ROOT = Path(__file__).resolve().parents[1]
CL = ROOT.parent
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '9_8차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round8.pptx')
PURPLE = '6B4EFF'
PEN = 'Nanum Pen Script'
TEASER = CL / 'claude-teasers' / 'out' / 'teaser-vEsB.png'


def p4(slide, k=1.08):
    out = []
    for name, keep in (('성빈 (6쪽 그림체)', 'right'), ('지현 (8쪽 그림체)', 'left')):
        sh = r2.shape(slide, name=name)
        x, y, w, h = r2.xywh(sh)
        nw, nh = w * k, h * k
        nx = x + w - nw if keep == 'right' else x          # 말풍선 쪽 모서리 고정
        r2.put(sh, x=nx, y=y + h - nh, w=nw, h=nh)          # 아래 끝(말풍선 아래 끝과 같은 선) 고정
        out.append((name, [round(v, 1) for v in (x, y, w, h)], [round(v, 1) for v in (nx, y + h - nh, nw, nh)]))
    return out


def pen_props(slide):
    """손글씨 글자 속성을 5~9쪽 손글씨와 같게."""
    n = 0
    for p in slide._element.iter(qn('a:p')):
        hit = False
        for rpr in p.iter(qn('a:rPr')):
            fonts = [rpr.find(qn(t)) for t in ('a:latin', 'a:ea', 'a:cs')]
            if not any(f is not None and f.get('typeface') == PEN for f in fonts):
                continue
            for f in fonts:
                if f is not None:
                    for a in ('pitchFamily', 'charset'):
                        f.attrib.pop(a, None)
            rpr.set('lang', 'ko-KR')
            rpr.set('altLang', 'en-US')
            hit = True
            n += 1
        end = p.find(qn('a:endParaRPr'))
        if hit and end is not None:
            end.set('lang', 'ko-KR')
            end.set('altLang', 'en-US')
    return n


def p17(slide):
    """출처 줄의 '⁵'(U+2075)를 따로 떼어 Inter로. 나머지 글자·속성은 그대로."""
    hits = [r for r in slide._element.iter(qn('a:r')) if '\u2075' in (r.find(qn('a:t')).text or '')]
    assert len(hits) == 1, len(hits)
    r = hits[0]
    t = r.find(qn('a:t')).text
    assert t.count('\u2075') == 1
    before, after = t.split('\u2075')
    parts = [(before, False), ('\u2075', True), (after, False)]
    parent, idx = r.getparent(), r.getparent().index(r)
    parent.remove(r)
    for k, (txt, sup) in enumerate([p for p in parts if p[0]]):
        nr = copy.deepcopy(r)
        nr.find(qn('a:t')).text = txt
        if sup:
            rpr = nr.find(qn('a:rPr'))
            rpr.set('lang', 'en-US')
            for tag in ('a:latin', 'a:ea', 'a:cs'):
                rpr.find(qn(tag)).set('typeface', 'Inter')
        parent.insert(idx + k, nr)
    return before[-12:], after[:24]


def p10(slide):
    t = r2.shape(slide, sid=31)
    assert t.text_frame.text == '모두 삼성\n안에서!', t.text_frame.text
    x, y, w, h = r2.xywh(t)
    r2.put(t, x=x + 10)
    return round(x, 1), round(x + 10, 1)


def p1(slide):
    """표지 그림만 새 티저로 (자리·크기 그대로, 그림 크기 1672×941도 같음)."""
    pics = [sh for sh in slide.shapes if sh.shape_type == 13]
    assert len(pics) == 1 and pics[0].image.size == (1672, 941), [p.name for p in pics]
    blip = pics[0]._element.find('.//' + qn('a:blip'))
    _, rId = slide.part.get_or_add_image_part(str(TEASER))
    blip.set(qn('r:embed'), rId)
    return pg.drop_unused_images(slide)


def p12(slide):
    """Kanana 마지막 행 ✕ → △ (같은 11px 아이콘 칸, 글자와 간격 그대로)."""
    old = r2.shape(slide, sid=74)
    assert old.name == 'Status icon · x · 제한적'
    lab = r2.shape(slide, sid=63)
    assert lab.text_frame.text == '제한적'
    x, y, w, h = r2.xywh(old)
    size = w / 0.84                                     # icon_xml('x')는 칸의 84% 크기로 그림
    x0, y0 = x - (size - w) / 2, y - (size - h) / 2
    old._element.getparent().remove(old._element)
    r2.add_sp(slide, r2.icon_xml('tri', x0, y0, size), 'Status icon · tri · 제한적 (Kanana)')
    return round(x0, 2), round(y0, 2), round(size, 2)


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    print(1, 'teaser replaced, dropped', p1(slides[0]))
    for row in p4(slides[3]):
        print(4, *row)
    r = r6.refill(prs, slides[4], ROOT / 'p05' / 'out', 'page-05-solution', (ROOT / 'p05' / 'notes-page-05.txt').read_text(encoding='utf-8').strip(),
                  'SOLUTION: WEAVE ASSIST', title_runs=[('Weave', '6666FF'), ('의 ', None), ('핵심 UX 3가지', '6666FF'), ('를 소개합니다!', None)])
    print(5, r['title'])
    for n in (6, 7, 8):
        r = r6.refill(prs, slides[n - 1], ROOT / 'p68' / 'out', f'page-0{n}', r4.NOTES[n], r4.HEADERS[n])
        print(n, r['title'])
    notes9 = (CL / 'notes' / 'page-07-pipeline.txt').read_text(encoding='utf-8').strip()
    r = r6.refill(prs, slides[8], CL / 'out', 'page-07-pipeline', notes9, 'HOW IT WORKS',
                  title_runs=[('Weave', PURPLE), ('는 어떻게 ', None), ('기억을 엮을까요', PURPLE), ('?', None)])
    print(9, r['title'], '|', r.get('sub'))
    for n in (10, 11):
        c = pen_props(slides[n - 1])
        assert c == 2, (n, c)
        print(n, 'pen runs', c)
    print(10, 'pen x', p10(slides[9]))
    print(12, 'kanana tri', p12(slides[11]))
    print(17, 'split around ⁵', p17(slides[16]))
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        apply(BACKUP, TEST_OUT)
