#!/usr/bin/env python3
"""Appendix 새 장 7개를 덱 끝에 더하고, 27쪽 Q&A 2를 새 설명으로 다시 채웁니다(2026-11-05).

  python apply_appendix.py <src.pptx> <dst.pptx>

out/*.art.png · *.layout.json(07_소스/tools/render.cjs 결과)을 씁니다. src는 읽기만 합니다.
다시 렌더하려면(07_소스에서):
  PW_CORE=~/.cache/weave-tools/node/node_modules/playwright-core \
  CHROME=~/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell \
  OUT_DIR=slides/appendix_결선/out node tools/render.cjs slides/appendix_결선/page-a1.html   (a1 ~ a7, ../../pages/page-16-glossary.html)
"""
import importlib.util as iu
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLIDES = HERE.parent
S07 = SLIDES.parent
sys.path[:0] = [str(SLIDES / 'tools' / '참고_회차스크립트'), str(SLIDES / 'tools')]
_orig = iu.spec_from_file_location


def _redirect(name, location, *a, **k):
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

PAGES = [('page-a1', 'Appendix · 파이프라인'), ('page-a2', 'Appendix · 관련 연구'), ('page-a3', 'Appendix · Reasoning Embedding'),
         ('page-a4', 'Appendix · UX 1 상세'), ('page-a5', 'Appendix · UX 2 상세'), ('page-a6', 'Appendix · UX 3 상세'), ('page-a7', 'Appendix · 비교')]
Q4 = ('Q4 연쇄 탐색: 찾은 단서를 빈칸에 넣어 질문을 다시 쓰고, 다시 쓴 질문을 임베딩으로 찾습니다. 임베딩은 앞 기록을 기억하지 않습니다. 날짜 같은 정확한 조건은 필터로 좁히고, '
      '필요한 정보가 채워지거나 새 단서가 없거나 탐색 한도에 닿으면 멈춥니다. 예상 질문 "임베딩이 앞 기록을 어떻게 기억하나요?"에는 "기억하지 않습니다. 찾은 단서를 넣어 다시 쓴 질문을 받습니다."라고 답합니다. '
      'MDR(Xiong et al., ICLR 2021)은 "we simply concatenate the question and the retrieved passages as the inputs to g(·)"처럼 질문과 앞서 찾은 문서를 함께 인코딩합니다. '
      '글을 생성하지 않아서 Weave는 보조 경로로 검토합니다. 학습 데이터는 \'질문 + 확인한 단서 → 다음 근거\' 쌍과 헷갈리기 쉬운 오답으로 구성합니다(ReasonIR의 hard negative 방식).')


def name_header(slide, chip_text, raw_chip=None, n_tops=2):
    texts = [sh for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    c = [sh for sh in texts if sh.text_frame.text.strip() == (raw_chip or chip_text)]
    assert len(c) == 1, chip_text
    c[0].name = 'Header chip'
    tops = sorted((sh for sh in texts if sh is not c[0] and (sh.top or 0) / 9525 < 146), key=lambda s: s.top)
    assert len(tops) == n_tops, [t.text_frame.text for t in tops]
    tops[0].name = 'Header title'
    if n_tops > 1:
        tops[1].name = 'Header subtitle'


def fill(prs, slide, name, notes, bg):
    r3.ensure_notes_body(prs, slide)
    r3.bp.fill_slide(slide, name, bg, notes)
    r4.split_fonts(slide)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    prs = Presentation(str(src))
    r3.bp.OUT = HERE / 'out'
    bg = r2.background_from(prs)
    slides = list(prs.slides)
    layout = slides[8].slide_layout
    # 27쪽(Q&A 2) 다시 채우기
    qa = [s for s in slides if any(sh.has_text_frame and sh.text_frame.text.strip() == '(Reasoning) Embedding Model이란?' for sh in s.shapes)]
    assert len(qa) == 1
    old = qa[0].notes_slide.notes_text_frame.text
    notes = old[:old.index('Q4 연쇄 탐색')] + Q4
    notes = notes.replace('집들이 일정', '집들이 날짜')
    fill(prs, qa[0], 'page-16-glossary', notes, bg)
    name_header(qa[0], 'Appendix · Q&A', raw_chip='16 / Appendix · Q&A', n_tops=1)
    pg.drop_unused_images(qa[0])
    print('Q&A 2', hd.apply(qa[0], chip_text='Appendix · Q&A'))
    # 새 장
    for name, chip in PAGES:
        s = prs.slides.add_slide(layout)
        for ph in list(s.placeholders):
            ph._element.getparent().remove(ph._element)
        fill(prs, s, name, (HERE / f'notes-{name}.txt').read_text(encoding='utf-8').strip(), bg)
        name_header(s, chip)
        pg.drop_unused_images(s)
        print(name, hd.apply(s, chip_text=chip))
    prs.save(str(dst))
    print('Appendix →', dst, len(prs.slides), '장')


if __name__ == '__main__':
    main()
