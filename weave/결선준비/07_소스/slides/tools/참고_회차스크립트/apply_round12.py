"""0927_v1 덱 12차 (2026-09-29, 12쪽 차별화 포인트 표의 Weave 문구).

사용자 요청: 표 문체(짧은 명사형)에 맞춰 Weave 칸 세 곳과 한 행의 제목을 바꿈.
- 유형 태그: '맥락 맞춤형' → '맥락 연결·탐색형' (옆 태그 '생성·교정형'과 같은 가운뎃점·'형' 꼴)
  글자가 길어져 태그(보라 알약)와 글자 상자를 가운데 기준으로 넓힘. 여백 규칙은 다른 태그와 같음
  (글자 상자 = 글자 폭 + 원래 여유, 알약 = 글자 상자 + 양옆 8pt)
- 핵심 역할 둘째 줄: '연결 및 선제적 제안' → '연결 및 연관 맥락 제공' ('선제적 제안'이 Now Nudge처럼 읽힘)
- 데이터 처리: '온디바이스' → '온디바이스 전용' (글자 상자만 가운데 기준으로 넓힘)
- 행 제목: '앱 간 연계 (Cross-App)' → '앱·기록 간 연계 (Multi-hop)' (새 행을 넣는 대신, Weave 칸 '컨텍스트 기반 연쇄 탐색'과 맞춤)

사용: python apply_round12.py --test | --deck (백업 13과 같을 때만)
"""
import hashlib
import sys
from pathlib import Path

from pptx import Presentation

import textmeasure as tm

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT.parents[1] / 'added_0926' / '0927_data' / '0927_v1.pptx'
BACKUP = ROOT / 'backups' / '13_12차요청전.pptx'
TEST_OUT = Path('/tmp/claude-weave-0927/lo-0927v1/test-round12.pptx')
PX = 9525                                                     # EMU / px (1280 기준)

TEXTS = {  # 도형 이름: [(바꿀 글, 새 글)] — 한 run 안에 그대로 있어야 함(서식 유지)
    'Text 24': [('맥락 맞춤형', '맥락 연결·탐색형')],
    'Text 31': [('연결 및 선제적 제안', '연결 및 연관 맥락 제공')],
    'Text 45': [('온디바이스', '온디바이스 전용')],
    'Text 47': [('앱 간 연계', '앱·기록 간 연계'), ('(Cross-App)', '(Multi-hop)')],
}
WIDEN = {  # 글자 상자: (옛 글, 새 글, 글자 크기 pt, 함께 넓힐 알약)
    'Text 24': ('맥락 맞춤형', '맥락 연결·탐색형', 12, 'Shape 23'),
    'Text 45': ('온디바이스', '온디바이스 전용', 13, None),
}


def apply(src, dst):
    prs = Presentation(str(src))
    slides = list(prs.slides)
    assert len(slides) == 19
    shapes = {sh.name: sh for sh in slides[11].shapes}
    for name, pairs in TEXTS.items():
        for old, new in pairs:
            hits = [r for p in shapes[name].text_frame.paragraphs for r in p.runs if r.text == old]
            assert len(hits) == 1, (name, old, len(hits))
            hits[0].text = new
    for name, (old, new, pt, pill) in WIDEN.items():
        box = shapes[name]
        pad = box.left - shapes[pill].left if pill else 0     # 알약 양옆 여백(8pt) 유지
        grow = (tm.width(new, pt * 4 / 3, 700, family='noto') - tm.width(old, pt * 4 / 3, 700, family='noto')) * PX
        cx = box.left + box.width / 2                         # 가운데는 그대로
        box.width = round(box.width + grow)
        box.left = round(cx - box.width / 2)
        if pill:
            p = shapes[pill]
            p.left, p.width = box.left - pad, box.width + 2 * pad
        print(name, 'x', round(box.left / PX, 1), 'w', round(box.width / PX, 1), '| center', round((box.left + box.width / 2) / PX, 2),
              f'| {pill} x {round(shapes[pill].left / PX, 1)} w {round(shapes[pill].width / PX, 1)}' if pill else '')
    for name in TEXTS:
        print(name, '→', ' / '.join(p.text for p in shapes[name].text_frame.paragraphs))
    prs.save(str(dst))
    print('saved', dst)


if __name__ == '__main__':
    if '--deck' in sys.argv:
        md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
        assert md5(DECK) == md5(BACKUP), '백업 이후 덱이 바뀌었습니다. 새로 백업하고 다시 확인하세요.'
        apply(DECK, DECK)
    else:
        TEST_OUT.parent.mkdir(parents=True, exist_ok=True)
        apply(BACKUP, TEST_OUT)
