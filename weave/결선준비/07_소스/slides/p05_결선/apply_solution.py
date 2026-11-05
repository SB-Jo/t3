#!/usr/bin/env python3
"""5쪽 SOLUTION 장표를 결선 시나리오(요청 자료 · 집들이 와인 · 갈색병)로 다시 채웁니다.

  python apply_solution.py <src.pptx> <dst.pptx>

out/page-05-solution.art.png · .layout.json (07_소스/tools/render.cjs 결과)과 notes-page-05.txt로
src의 SOLUTION 장('SOLUTION: WEAVE ASSIST' 머리 칩이 있는 장, 못 찾으면 인덱스 4)을 다시 채워 dst로 저장합니다.
src는 읽기만 합니다(dst가 같은 경로일 때만 덮어씀).

순서는 참고_회차스크립트/apply_round13.py의 apply_round6.refill과 같습니다.
노트 본문 확보 → 배경 도형 3개 + 그래픽 레이어 + 글 상자 → 글꼴 나누기(영문·숫자 Inter) → 머리 도형 이름·규격 → 안 쓰는 그림 정리.
apply_round6은 가져올 때 옛 경로의 노트 파일을 읽어서, refill을 여기 그대로 옮겨 씁니다.

다시 렌더하려면(07_소스에서):
  PW_CORE=~/.cache/weave-tools/node/node_modules/playwright-core \
  CHROME=~/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell \
  OUT_DIR=slides/p05_결선/out node tools/render.cjs slides/p05_결선/page-05-solution.html
"""
import importlib.util as iu
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # 07_소스/slides/p05_결선
SLIDES = HERE.parent                             # 07_소스/slides
S07 = SLIDES.parent                              # 07_소스
sys.path[:0] = [str(SLIDES / 'tools' / '참고_회차스크립트'), str(SLIDES / 'tools')]

_orig = iu.spec_from_file_location


def _redirect(name, location, *a, **k):          # apply_round3이 옛 경로(07_소스/tools/build_pptx.py)를 읽음 → 실제 위치로
    if name == 'build_pptx':
        location = S07 / 'tools' / '참고_옛덱전용' / 'build_pptx.py'
    return _orig(name, location, *a, **k)


iu.spec_from_file_location = _redirect
try:
    import apply_round2 as r2
    import apply_round3 as r3
    import apply_round4 as r4
    import header as hd
    import pages_p2_p4 as pg
finally:
    iu.spec_from_file_location = _orig

from pptx import Presentation  # noqa: E402

NAME = 'page-05-solution'
CHIP = 'SOLUTION: WEAVE ASSIST'
TITLE_RUNS = [('흩어진 기억을 이어 주는 ', None), ('Weave', '6666FF'), ('의 ', None), ('핵심 UX 3가지', '6666FF')]


def find_slide(prs):
    hits = [s for s in prs.slides
            if any(sh.has_text_frame and sh.text_frame.text.strip() == CHIP for sh in s.shapes)]
    if len(hits) == 1:
        return hits[0]
    s = prs.slides[4]
    assert any(sh.has_text_frame and sh.text_frame.text.strip() == CHIP for sh in s.shapes), \
        'SOLUTION 장을 찾지 못했습니다(머리 칩 %r)' % CHIP
    return s


def refill(prs, slide, notes):
    r3.ensure_notes_body(prs, slide)
    r3.bp.OUT = HERE / 'out'
    r3.bp.fill_slide(slide, NAME, r2.background_from(prs), notes)
    r4.split_fonts(slide)
    texts = [sh for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    c = [sh for sh in texts if sh.text_frame.text.strip() == CHIP]
    assert len(c) == 1, CHIP
    c[0].name = 'Header chip'
    tops = sorted((sh for sh in texts if sh is not c[0] and (sh.top or 0) / 9525 < 150), key=lambda s: s.top)
    assert len(tops) == 2, [t.text_frame.text for t in tops]
    tops[0].name, tops[1].name = 'Header title', 'Header subtitle'
    pg.drop_unused_images(slide)
    return hd.apply(slide, title_runs=TITLE_RUNS)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    prs = Presentation(str(src))
    slide = find_slide(prs)
    idx = list(prs.slides).index(slide)
    notes = (HERE / 'notes-page-05.txt').read_text(encoding='utf-8').strip()
    r = refill(prs, slide, notes)
    prs.save(str(dst))
    print('%d쪽 SOLUTION 다시 채움 → %s | %s' % (idx + 1, dst, r))


if __name__ == '__main__':
    main()
