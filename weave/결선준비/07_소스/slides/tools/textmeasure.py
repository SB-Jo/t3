"""글자 폭 측정 (PowerPoint 배치 계산용). 영어·숫자·기호는 Inter, 한글은 Noto Sans KR로 잰다."""
from functools import lru_cache
from pathlib import Path
from PIL import ImageFont

FONTS = Path(__file__).resolve().parents[2] / 'assets' / 'fonts'


@lru_cache(None)
def font(family, weight, px):
    f = {'inter': f'Inter-{weight}.ttf', 'noto': f'NotoSansKR-{weight}.ttf'}[family]
    return ImageFont.truetype(str(FONTS / f), size=px, layout_engine=ImageFont.Layout.BASIC)


def is_latin(ch):
    return ord(ch) < 0x2E80 and ch not in '“”‘’·'  # 따옴표·가운뎃점은 PowerPoint에서 한글 글꼴(ea)로 그려짐


def width(text, px, weight=400, spc_px=0.0, latin_font='inter', family=None):
    """text 폭(px). spc_px = 글자 사이 간격(PowerPoint spc, 마지막 글자 뒤에도 붙음).
    family='inter'|'noto'를 주면 모든 글자를 그 글꼴로 잼(글꼴을 조각별로 지정한 글자용)."""
    if family:
        return font(family, weight, px).getlength(text) + spc_px * len(text)
    total = 0.0
    run, cur = '', None
    def flush(r, fam):
        return font(fam, weight, px).getlength(r) if r else 0.0
    for ch in text:
        fam = latin_font if is_latin(ch) else 'noto'
        if fam != cur and run:
            total += flush(run, cur); run = ''
        cur = fam; run += ch
    total += flush(run, cur)
    return total + spc_px * len(text)


if __name__ == '__main__':
    import sys
    print(width(sys.argv[1], float(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 400))
