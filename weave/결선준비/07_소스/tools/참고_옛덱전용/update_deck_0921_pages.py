"""0921/통합_claude0927_반영본.pptx(사용자가 이어서 고치는 덱)에서 이 폴더가 만든 장표만 최신 렌더 결과로 다시 채웁니다.

사용: python tools/update_deck_0921_pages.py page-07-pipeline [page-15-qna page-16-glossary]
- render.cjs로 out/<이름>.layout.json · .art.png를 먼저 만들어 둘 것. 채우는 규칙은 build_pptx.py의 fill_slide와 같습니다.
- 장표는 라벨 글자(예: '07 / HOW IT WORKS')로 찾습니다. 덱에서 순서가 바뀌어도 됩니다.
- 배경 도형은 같은 덱의 '08 / WHY SAMSUNG' 장표에서 복사하고, 발표자 노트는 notes/<이름>.txt로 바꿉니다.
- 다른 장표는 건드리지 않습니다. 고치기 전 사본은 deck-versions/에 먼저 저장해 둘 것.
"""
import copy
import importlib.util
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT.parent / '통합_claude0927_반영본.pptx'
LABELS = {'page-07-pipeline': '07 / HOW IT WORKS', 'page-15-qna': '15 / Appendix · Q&A', 'page-16-glossary': '16 / Appendix · Q&A'}

spec = importlib.util.spec_from_file_location('build_pptx', ROOT / 'tools' / 'build_pptx.py')
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)


def find(prs, label):
    hits = [s for s in prs.slides if any(sh.has_text_frame and sh.text_frame.text.strip() == label for sh in s.shapes)]
    assert len(hits) == 1, f"'{label}' 장표가 {len(hits)}개입니다"
    return hits[0]


def main(names):
    prs = Presentation(str(DECK))
    src = find(prs, '08 / WHY SAMSUNG')
    bg = [copy.deepcopy(sh._element) for sh in list(src.shapes)[:3]]
    assert all(not el.xpath('.//a:t') for el in bg), '배경 도형 대신 글자 상자가 잡힘'
    for n in names:
        slide = find(prs, LABELS[n])
        bp.fill_slide(slide, n, bg, (ROOT / 'notes' / f'{n}.txt').read_text(encoding='utf-8').strip())
        # 지운 예전 그래픽 레이어 그림이 파일에 남지 않도록, 더 이상 쓰지 않는 그림 관계를 뺌
        xml = etree.tostring(slide._element).decode()
        for rId, rel in list(slide.part.rels.items()):
            if rel.reltype.endswith('/image') and f'"{rId}"' not in xml:
                slide.part.drop_rel(rId)
        print('refreshed', n, '→ slide', list(prs.slides).index(slide) + 1)
    prs.save(str(DECK))


if __name__ == '__main__':
    args = sys.argv[1:]
    assert args and all(a in LABELS for a in args), f'사용: {list(LABELS)} 중에서 고르기'
    main(args)
