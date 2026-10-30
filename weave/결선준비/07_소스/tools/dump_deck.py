"""통합.pptx를 읽기만 하고(수정하지 않음) 슬라이드별 텍스트·폰트·도형 요약을 출력합니다."""
import sys, json, collections
from pathlib import Path
from pptx import Presentation
from pptx.util import Emu

src = Path(sys.argv[1])
prs = Presentation(src)
print('slides', len(prs.slides), 'size(px@96)', prs.slide_width/9525, prs.slide_height/9525)
fonts = collections.Counter()
def walk(shapes, depth=0):
    for sh in shapes:
        yield sh, depth
        if sh.shape_type == 6:  # group
            yield from walk(sh.shapes, depth+1)
for i, slide in enumerate(prs.slides, 1):
    hidden = slide._element.get('show') == '0'
    print(f'\n=== SLIDE {i} {"(hidden)" if hidden else ""} layout={slide.slide_layout.name}')
    for sh, d in walk(slide.shapes):
        if sh.has_text_frame and sh.text_frame.text.strip():
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    f = r.font
                    fonts[(f.name, f.size.pt if f.size else None, f.bold)] += 1
            t = sh.text_frame.text.replace('\n', ' / ')
            x, y = round(sh.left/9525) if sh.left is not None else '?', round(sh.top/9525) if sh.top is not None else '?'
            print('  '*d + f'- [{x},{y}] {t[:160]}')
    if slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip():
        print('  NOTES:', slide.notes_slide.notes_text_frame.text[:300].replace('\n',' / '))
print('\nFONTS (name, size, bold): count')
for k, v in fonts.most_common(40):
    print(' ', k, v)
