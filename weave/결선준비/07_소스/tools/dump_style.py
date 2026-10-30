"""슬라이드별 도형 위치·채움·글꼴 색/크기를 출력(읽기 전용)."""
import sys
from pptx import Presentation
from pptx.dml.color import RGBColor
prs = Presentation(sys.argv[1])
targets = [int(x) for x in sys.argv[2].split(',')]
def walk(shapes, d=0):
    for sh in shapes:
        yield sh, d
        if sh.shape_type == 6:
            yield from walk(sh.shapes, d+1)
def col(font):
    try:
        if font.color and font.color.type is not None and font.color.rgb is not None:
            return str(font.color.rgb)
    except Exception:
        return 'theme'
    return None
for idx in targets:
    s = prs.slides[idx-1]
    print(f'==== slide {idx}')
    bg = s.background.fill
    for sh, d in walk(s.shapes):
        box = [round(v/9525,1) if v is not None else None for v in (sh.left, sh.top, sh.width, sh.height)]
        fill = ''
        try:
            if sh.fill.type == 1:
                fill = 'fill=' + str(sh.fill.fore_color.rgb)
        except Exception:
            pass
        line = ''
        try:
            if sh.line and sh.line.fill.type == 1:
                line = 'line=' + str(sh.line.color.rgb)
        except Exception:
            pass
        txt = ''
        if sh.has_text_frame and sh.text_frame.text.strip():
            runs = []
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    runs.append(f'"{r.text[:40]}"({r.font.name},{r.font.size.pt if r.font.size else None},b={r.font.bold},c={col(r.font)})')
            txt = ' '.join(runs)[:400]
        img = ''
        if sh.shape_type == 13:
            img = 'IMG ' + str(sh.image.content_type) + ' ' + str(sh.image.size)
        print('  '*d + f'- {sh.name[:40]} {box} {fill} {line} {img} {txt}')
