"""0927_v1 덱을 PNG·PDF로 내보냄 (2026-09-27 23시 요청, 2026-09-28 PowerPoint 렌더로 바꿈).

출력: added_0926/0927_data/weave_png/
  p01.png        표지 (덱 1쪽에 들어간 티저 그림 그대로 꺼냄, 1672×941)
  p02.png        만화 (PPT의 좌우 여백 없이 만화 그림만, 3600×2560). 원본 픽셀·색 프로필 그대로 PNG 압축만 다시 함
                 (원본 파일 14.8MB → 약 8.7MB, 2026-09-29 올리는 곳 한 파일 10MB 제한)
  p03-04.png, p05-09.png, p10-12.png, p13-15.png, p16-19.png
                 장표(2560×1440)를 위아래로 이어 붙임
  seamless/      이음매 없는 판 (SEAM_SETS, 2026-09-28 10차 요청)
                   p03-04           원래 장표 빛 크기 그대로, 4쪽 노랑은 오른쪽 아래 인물 둘레로·3쪽 왼쪽 아래 보라는 50px 아래로
                   p05-09, p05-09_gap20 (장표 사이 20px, 1280 기준)
                   p10-12 (10→11 사이 30px 좁힘), p13-15, p17-18
                                    묶음을 한 장처럼 보고 바탕·노랑/보라 빛을 새로 배치(seams.LAYOUTS)
                   p19              단독 판: 오른쪽 위 노랑·왼쪽 아래 보라만 (16쪽은 데모만 따로 올려 이음매 판에서 뺌)
                   p03-04_divider, p13-15, p17-18  장표 사이에 양옆을 띄운 페이지 구분선
  pngs/          이어 붙이지 않은 한 장씩: p01·p02는 위와 같고, p03~p19는 장표 렌더(2560×1440) (2026-09-28 요청)
added_0926/0927_data/0927_v1.pdf   덱 전체 PDF

렌더 엔진 (기본 ppt)
  ppt  Windows 쪽 PowerPoint가 직접 그림 → PPTX를 PowerPoint로 볼 때와 같음.
       WSL에서 powershell.exe로 PowerPoint를 부름(tools/ppt_export.ps1). 덱 사본을 C:\\Temp\\weave-ppt에 두고
       읽기 전용·창 없이 열어 장표 PNG(Slide.Export)를 만들고 그 사본만 닫음. 켜져 있던 PowerPoint와 열린 파일은 건드리지 않음.
       PDF는 PowerPoint가 그린 장표 그림(3840×2160, JPEG 품질 94·4:4:4)으로 쪽을 만들고, 보이지 않는 글자 층(그리기 모드 3)을
       얹어 검색·복사가 되게 함. PowerPoint의 'PDF로 저장'은 이 PC의 가변 글꼴(Inter·Noto Sans KR)을 넣지 못해 글자를
       '2×2 단색 그림 + 반투명 마스크'로 그리고 투명도 0인 Calibri 글자를 덮는데, 투명 처리를 못 하는 뷰어에서는 글자 대신
       색 상자와 검은 Calibri 글자가 보여서(2026-09-28 사용자: 'PDF는 완전 이상하게 나와') 쓰지 않음.
  lo   이전 방식(LibreOffice). 2026-09-28 전수조사에서 PowerPoint와 글자 자리가 달라 쓰지 않음:
       473개 글자 상자 중 대부분이 1~3.5px 아래로 내려가고(기준선 계산 차이, 동그라미 안 숫자가 어긋나 보임),
       자간이 있는 29pt 제목은 약 2% 넓게 그려짐. 렌더 전용 사본에서 LibreOffice만의 차이 세 가지를 끄던 보정
       (자동 맞춤 → 끔, 영문·한글 자동 간격 → 끔, 손글씨 글꼴 이름 → 'Nanum Pen')은 lo일 때만 씀.

이음매 없는 판:
  1) 배경 도형 3개(전체 그라데이션·오른쪽 위 복숭아빛·왼쪽 아래 라벤더)를 뺀 사본을 흰 바탕(W)·검은 바탕(K)으로 렌더
     → 글자·도형·그림만의 색과 투명도를 정확히 얻음:  결과 = K + (W − K)/255 × 새 배경
     6~8쪽은 인물 뒤 흐린 장면을 뺀 그래픽 층으로 바꿔 렌더(장면은 배경 층으로 따로 그림)
  2) 배경 도형만 남긴 사본(G, 슬라이드 바탕색은 원래대로)을 렌더 → 장표별 원래 배경 (합성 확인용, '자연스럽게 잇기'는 지금 안 씀)
  3) 새 배경 위에 합성 (seams.py): 장면 → 장표 아래로 넘친 그래픽(5쪽 손, 휴대폰·카드 그림자, render_layers.cjs) → 장표들
  4) 확인: 원래 배경(G)으로 합성하면 원래 렌더(N)와 거의 같아야 함 (최대 차이를 출력, 장면을 뺀 6~8쪽은 제외)

사용: python export_png.py [--engine ppt|lo] [--reuse]   (--reuse: 저장해 둔 PowerPoint 렌더로 PNG·seamless만 다시 만듦, PDF는 그대로)
"""
import io
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pymupdf
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.oxml import parse_xml
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT.parents[1] / '02_PPT' / 'Weave_결선.pptx'          # 결선준비/02_PPT
OUT = DECK.parent / 'weave_png'
WORK = Path('/tmp/claude-weave-0927/png-export')
T = Path('/tmp/claude-weave-0927')
COMIC = ROOT / 'comic' / 'out' / 'overview-comic.png'
GROUPS = [(3, 4), (5, 9), (10, 12), (13, 15), (16, 19)]
# 이음매 판(seamless/): (파일 이름, 장표들, 방식, 장표 사이 간격 — 2560 기준 px, 음수면 겹침)
#   16쪽(App Demo)은 데모만 따로 올려서 빼고, 19쪽은 단독 판 (2026-09-28 요청)
#   구분선: 장표 사이에 양옆을 띄운 페이지 구분선 (13-15·17-18은 사용자 요청으로 넣음, 3-4는 넣은 판을 따로)
SEAM_SETS = [
    ('p03-04', [3, 4], 'design', [0], False),                 # 원래 빛 크기로, 4쪽 노랑·3쪽 보라 자리만 옮김(사용자 요청)
    ('p03-04_divider', [3, 4], 'design', [0], True),
    ('p05-09', [5, 6, 7, 8, 9], 'design', [0, 0, 0, 0], False),
    ('p05-09_gap20', [5, 6, 7, 8, 9], 'design', [40, 40, 40, 40], False),   # 장표 사이 20px(1280 기준) 더 벌림(사용자 확인)
    ('p10-12', [10, 11, 12], 'design', [-60, 0], False),                    # 10→11 사이를 30px(1280 기준) 좁힘
    ('p13-15', [13, 14, 15], 'design', [0, 0], True),
    ('p17-18', [17, 18], 'design', [0], True),
    ('p19', [19], 'design', [], False),
]
LAYERS = ROOT / 'layers'             # tools/render_layers.cjs 결과: 5~9쪽 그래픽을 장표 아래 밖까지 찍은 층
LAYER_PAGES = {5: 'page-05-solution', 6: 'page-06', 7: 'page-07', 8: 'page-08', 9: 'page-07-pipeline'}
LAYER_SRC = [ROOT / 'p05' / 'page-05-solution.html', ROOT / 'p68' / 'page-06.html', ROOT / 'p68' / 'page-07.html',
             ROOT / 'p68' / 'page-08.html', ROOT.parent / 'pages' / 'page-07-pipeline.html']
BG_RECTS = [(0, 0, 1280, 720), (640, 0, 640, 506.7), (0, 373.3, 600, 346.7)]
PX = 9525
DPI = 192            # 13.333in × 192 = 2560px
FONT_KR = ROOT.parent / 'assets' / 'fonts' / 'NotoSansKR-400.ttf'   # 보이지 않는 글자 층
PDF_W, PDF_H = 3840, 2160
WINTMP = Path('/mnt/c/Temp/weave-ppt')          # PowerPoint가 여는 사본을 두는 Windows 쪽 임시 폴더 (C:\\Temp\\weave-ppt)
PS1 = ROOT / 'tools' / 'ppt_export.ps1'


def soffice(src, fmt, outdir):
    env = {'LD_LIBRARY_PATH': f'{T}/lo-sysroot/usr/lib/libreoffice/program:{T}/lo-sysroot/usr/lib/x86_64-linux-gnu',
           'FONTCONFIG_FILE': f'{T}/fonts.conf', 'SAL_USE_VCLPLUGIN': 'svp', 'HOME': f'{T}/home', 'PATH': '/usr/bin:/bin'}
    subprocess.run([f'{T}/lo-sysroot/usr/lib/libreoffice/program/soffice', '--headless', '--convert-to', fmt,
                    f'-env:UserInstallation=file://{T}/lo-profile', '--outdir', str(outdir), str(src)],
                   env=env, check=True, capture_output=True, timeout=900)


def is_bg(sh, k):
    if k > 2:
        return False
    x, y, w, h = [(v or 0) / PX for v in (sh.left, sh.top, sh.width, sh.height)]
    return any(abs(x - a) < 3 and abs(y - b) < 3 and abs(w - c) < 3 and abs(h - d) < 3 for a, b, c, d in BG_RECTS)


def set_slide_bg(slide, hexv):
    cSld = slide._element.find(qn('p:cSld'))
    old = cSld.find(qn('p:bg'))
    if old is not None:
        cSld.remove(old)
    bg = parse_xml(f'<p:bg xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                   f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:bgPr><a:solidFill><a:srgbClr val="{hexv}"/></a:solidFill>'
                   f'<a:effectLst/></p:bgPr></p:bg>')
    cSld.insert(0, bg)


def make_variant(kind, dst, lo=False):
    """kind: 'N' 원래 · 'W' 배경 빼고 흰 바탕 · 'K' 배경 빼고 검은 바탕 · 'G' 배경 도형만 · 'B' 바탕 도형만.  lo=True면 LibreOffice용 보정도"""
    prs = Presentation(str(DECK))
    for i, s in enumerate(prs.slides, 1):
        if lo:
            for bp in s._element.iter(qn('a:bodyPr')):      # 저장된 축소 비율이 없는 자동 맞춤 → 끔
                na = bp.find(qn('a:normAutofit'))
                if na is not None and na.get('fontScale') is None and na.get('lnSpcReduction') is None:
                    bp.replace(na, etree.Element(qn('a:noAutofit')))
            for f in s._element.iter(qn('a:latin'), qn('a:ea'), qn('a:cs')):
                if f.get('typeface') == 'Nanum Pen Script':
                    f.set('typeface', 'Nanum Pen')
        if kind == 'N' or i < 3:
            continue
        shapes = list(s.shapes)
        bgs = [sh for k, sh in enumerate(shapes) if is_bg(sh, k)]
        assert len(bgs) == 3, (i, [sh.name for sh in shapes[:4]])
        if kind in ('W', 'K'):
            for sh in bgs:
                sh._element.getparent().remove(sh._element)
            set_slide_bg(s, 'FFFFFF' if kind == 'W' else '000000')
            if i in (6, 7, 8):          # 인물 뒤 흐린 장면은 이음매 판에서 배경 층으로 따로 그림 → 여기선 장면 없는 그래픽 층으로
                art = [sh for sh in s.shapes if sh.shape_type == 13 and sh.name.startswith('Weave graphics layer')]
                assert len(art) == 1, i
                png = WORK / f'noscene-art-{i}.png'
                Image.open(LAYERS / f'{LAYER_PAGES[i]}.noscene.png').crop((0, 0, 2560, 1440)).save(png)
                _, rId = s.part.get_or_add_image_part(str(png))
                art[0]._element.find('.//' + qn('a:blip')).set(qn('r:embed'), rId)
        elif kind == 'G':
            for sh in shapes:
                if sh not in bgs:
                    sh._element.getparent().remove(sh._element)
        elif kind == 'B':                                    # 흐름 판용: 가장 아래 바탕 그라데이션 도형만
            for sh in shapes:
                if sh is not bgs[0] and sh != bgs[0]:
                    sh._element.getparent().remove(sh._element)
    prs.save(str(dst))


def to_pdf(pptx):
    """PPTX → ODP(영문·한글 자동 간격 끔) → PDF"""
    d = pptx.parent
    soffice(pptx, 'odp', d)
    odp = pptx.with_suffix('.odp')
    fixed = pptx.with_name(pptx.stem + '-fix.odp')
    zin, zout = zipfile.ZipFile(odp), zipfile.ZipFile(fixed, 'w')
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename in ('content.xml', 'styles.xml'):
            s = data.decode('utf8').replace('style:text-autospace="ideograph-alpha"', 'style:text-autospace="none"')
            s = re.sub(r'<style:paragraph-properties(?![^>]*text-autospace)', '<style:paragraph-properties style:text-autospace="none"', s)
            data = s.encode('utf8')
        zout.writestr(item, data, compress_type=zipfile.ZIP_STORED if item.filename == 'mimetype' else zipfile.ZIP_DEFLATED)
    zout.close()
    soffice(fixed, 'pdf', d)
    return fixed.with_suffix('.pdf')


def pages(pdf):
    doc = pymupdf.open(pdf)
    out = {}
    for i in range(len(doc)):
        # LibreOffice PDF의 쪽 폭이 960.009pt라 그냥 그리면 2561px(오른쪽 끝 흰 줄) → 960×540pt로 잘라 2560×1440
        pix = doc[i].get_pixmap(dpi=DPI, clip=pymupdf.Rect(0, 0, 960, 540))
        assert (pix.width, pix.height) == (2560, 1440), (pix.width, pix.height)
        a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].copy()
        out[i + 1] = a
    return out


def winpath(p):
    return subprocess.run(['wslpath', '-w', str(p)], capture_output=True, text=True, check=True).stdout.strip()


def ppt_render(pptx, tag, pdf_out=None, W=2560, H=1440):
    """PowerPoint로 장표 PNG(W×H)를 그리고, pdf_out이 있으면 PowerPoint PDF도(지금은 안 씀). 쓴 임시 파일은 지움."""
    WINTMP.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PS1, WINTMP / 'ppt_export.ps1')
    src, outdir, pdf = WINTMP / f'deck-{tag}.pptx', WINTMP / f'png-{tag}', WINTMP / f'deck-{tag}.pdf'
    shutil.copyfile(pptx, src)
    shutil.rmtree(outdir, ignore_errors=True)
    args = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', winpath(WINTMP / 'ppt_export.ps1'),
            '-Pptx', winpath(src), '-OutDir', winpath(outdir), '-W', str(W), '-H', str(H)]
    if pdf_out:
        args += ['-Pdf', winpath(pdf)]
    r = subprocess.run(args, cwd=WINTMP, capture_output=True, timeout=900)
    log = (r.stdout + r.stderr).decode('utf-8', 'replace')
    n = len(Presentation(str(pptx)).slides)
    assert r.returncode == 0 and f'slides {n}' in log, log
    pages = {}
    for i in range(1, n + 1):
        a = np.array(Image.open(outdir / f's{i:02d}.png').convert('RGB'))
        assert a.shape == (H, W, 3), a.shape
        pages[i] = a
    if pdf_out:
        shutil.copyfile(pdf, pdf_out)
        pdf.unlink()
    shutil.rmtree(outdir)
    src.unlink()
    return pages


def build_pdf(pages, dst):
    """장표 그림으로 쪽을 만든 PDF + 보이지 않는 글자 층(검색·복사용). 모든 뷰어에서 PNG와 같게 보임."""
    import apply_round2 as r2
    from pptx.enum.text import PP_ALIGN
    doc = pymupdf.open()
    font = pymupdf.Font(fontfile=str(FONT_KR))
    k = 0.75                                               # 1px(1280 기준) = 0.75pt
    for n, s in enumerate(Presentation(str(DECK)).slides, 1):
        page = doc.new_page(width=960, height=540)
        buf = io.BytesIO()
        Image.fromarray(pages[n]).save(buf, 'JPEG', quality=94, subsampling=0, optimize=True)
        page.insert_image(page.rect, stream=buf.getvalue())
        page.insert_font(fontname='nkr', fontfile=str(FONT_KR))
        for sh, (x, y, w, h) in r2.abs_boxes(s.shapes):
            if not (sh.has_text_frame and sh.text_frame.text.strip()):
                continue
            top = y * k
            for para in sh.text_frame.paragraphs:
                text = ''.join(r.text for r in para.runs).strip()
                size = next((r.font.size.pt for r in para.runs if r.font.size), 12.0)
                lh = para.line_spacing.pt if hasattr(para.line_spacing, 'pt') else size * 1.2
                if text:
                    tw = font.text_length(text, fontsize=size)
                    x0 = x * k + ((w * k - tw) / 2 if para.alignment == PP_ALIGN.CENTER else (w * k - tw) if para.alignment == PP_ALIGN.RIGHT else 0)
                    page.insert_text((x0, top + lh * 0.8), text, fontname='nkr', fontsize=size, render_mode=3)
                top += lh
    doc.set_metadata({'title': 'Weave Assist', 'author': '', 'subject': '', 'keywords': '', 'creator': 'PowerPoint 렌더(claude_0927/deck-0927v1/tools/export_png.py)', 'producer': ''})
    doc.subset_fonts()
    doc.save(dst, garbage=3, deflate=True)


def save_comic(dst):
    """2쪽 만화: 픽셀·색 프로필·해상도 정보는 원본 그대로 두고 PNG 압축만 다시 함(무손실). 원본은 건드리지 않음."""
    im = Image.open(COMIC)
    im.load()
    im.save(dst, optimize=True, **{k: im.info[k] for k in ('icc_profile', 'dpi', 'exif') if k in im.info})
    back = Image.open(dst)
    assert back.mode == im.mode and np.array_equal(np.asarray(back), np.asarray(im)), 'p02 픽셀이 원본과 다름'
    assert back.info.get('icc_profile') == im.info.get('icc_profile')
    print('p02 comic', round(COMIC.stat().st_size / 1e6, 2), '→', round(dst.stat().st_size / 1e6, 2), 'MB (lossless)')


def render_layers():
    env = {**os.environ, 'NODE_PATH': '/tmp/claude-weave-0927/node_modules', 'OUT_DIR': str(LAYERS),
           'LD_LIBRARY_PATH': '/tmp/claude-weave-0927/chrome-sysroot/usr/lib/x86_64-linux-gnu'}
    r = subprocess.run(['node', str(ROOT.parent / 'tools' / 'render_layers.cjs'), *map(str, LAYER_SRC)], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    print(r.stdout.strip())


def main(engine='ppt', reuse=False):
    WORK.mkdir(parents=True, exist_ok=True)
    if not reuse:
        render_layers()
    renders = {}
    for kind in ('N', 'W', 'K', 'G'):
        cache = WORK / 'renders' / kind
        if reuse and (cache / 's19.png').exists():         # 디자인만 고칠 때: 저장해 둔 렌더를 다시 씀
            renders[kind] = {i: np.array(Image.open(cache / f's{i:02d}.png').convert('RGB')) for i in range(1, 20)}
            print('reused', kind)
            continue
        p = WORK / f'deck-{kind}.pptx'
        if engine == 'ppt':
            if kind == 'N':
                shutil.copyfile(DECK, p)                     # 덱 그대로
            else:
                make_variant(kind, p)
            renders[kind] = ppt_render(p, kind)
        else:
            make_variant(kind, p, lo=True)
            pdf = to_pdf(p)
            renders[kind] = pages(pdf)
        cache.mkdir(parents=True, exist_ok=True)
        for i, a in renders[kind].items():
            Image.fromarray(a).save(cache / f's{i:02d}.png')
        print('rendered', engine, kind, len(renders[kind]))
        if kind == 'N' and engine == 'ppt':
            build_pdf(ppt_render(p, 'N-pdf', W=PDF_W, H=PDF_H), DECK.with_suffix('.pdf'))
            print('pdf from PowerPoint renders', PDF_W, 'x', PDF_H)
        elif kind == 'N':
            doc = pymupdf.open(pdf)            # 제목 정보: 원래 덱에서 온 'Weave 차별화 포인트'·'PptxGenJS' 대신
            doc.set_metadata({**doc.metadata, 'title': 'Weave Assist', 'author': '', 'subject': ''})
            doc.save(DECK.with_suffix('.pdf'), garbage=1, deflate=True)

    # 1·2쪽: 덱에 들어간 그림 그대로
    pic = [sh for sh in list(Presentation(str(DECK)).slides)[0].shapes if sh.shape_type == 13]
    assert len(pic) == 1
    Image.open(io.BytesIO(pic[0].image.blob)).convert('RGB').save(OUT / 'p01.png', optimize=True)
    save_comic(OUT / 'p02.png')
    # 한 장씩 (pngs/)
    (OUT / 'pngs').mkdir(exist_ok=True)
    shutil.copyfile(OUT / 'p01.png', OUT / 'pngs' / 'p01.png')
    shutil.copyfile(OUT / 'p02.png', OUT / 'pngs' / 'p02.png')
    for n in range(3, len(renders['N']) + 1):
        Image.fromarray(renders['N'][n]).save(OUT / 'pngs' / f'p{n:02d}.png', optimize=True)

    for a, b in GROUPS:                                     # 이어 붙인 묶음(원래 배경 그대로)
        name = f'p{a:02d}-{b:02d}.png'
        Image.fromarray(np.concatenate([renders['N'][i] for i in range(a, b + 1)], axis=0)).save(OUT / name, optimize=True)
        print('saved', name)

    import seams
    SD = OUT / 'seamless'
    SD.mkdir(parents=True, exist_ok=True)
    (SD / 'p16-19.png').unlink(missing_ok=True)             # 16쪽은 이음매 판에서 뺌 → 17-18, 19로 나눔
    shutil.rmtree(OUT / 'seamless-flow', ignore_errors=True)  # '흐름' 판은 한 장처럼 디자인한 seamless/로 대신함
    layer = {n: {k: np.array(Image.open(f).convert('RGBA')) for k in ('noscene', 'spill', 'scene', 'chars')
                 if (f := LAYERS / f'{nm}.{k}.png').exists()} for n, nm in LAYER_PAGES.items()}
    for n in (6, 7, 8):                                     # 장면 없는 그래픽 층 = 덱 그래픽 층에서 장면만 뺀 것인지(장면 밖은 같아야 함)
        deck_art = [sh for sh in list(Presentation(str(DECK)).slides)[n - 1].shapes if sh.shape_type == 13 and sh.name.startswith('Weave graphics layer')][0]
        a = np.array(Image.open(io.BytesIO(deck_art.image.blob)).convert('RGBA')).astype(np.float32)
        b = layer[n]['noscene'][:1440].astype(np.float32)
        off = layer[n]['scene'][:1440, :, 3] == 0
        print(n, 'noscene art vs deck art outside scene: max', float(np.abs(a - b)[off].max()))
    for nm, ids, how, gaps, div in SEAM_SETS:
        Ws, Ks = [renders['W'][i] for i in ids], [renders['K'][i] for i in ids]
        offs = seams.offsets(len(ids), gaps)
        if how == 'natural':
            bg, centers = seams.canvas_bg([renders['G'][i].astype(np.float32) for i in ids], gaps)
            out = seams.compose_natural(Ws, Ks, seams.soften(bg, centers), offs)
        else:
            bg, offs = seams.design_bg(len(ids), gaps, seams.LAYOUTS[(ids[0], ids[-1])])
            out = seams.compose_design(Ws, Ks, bg, offs, [layer.get(i) for i in ids])
        if div:
            out, ys = seams.dividers(out, Ws, Ks, offs)
            print(nm, 'dividers at y(1280 기준)', [round(v, 1) for v in ys])
        Image.fromarray(out).save(SD / f'{nm}.png', optimize=True)
        chk = [i for i in ids if i not in (6, 7, 8)]          # 6~8쪽(장면을 뺀 렌더) 말고는 원래 배경(G)으로 합성하면 원래 렌더(N)와 같아야 함
        d = [float(np.abs(seams.compose_natural([renders['W'][i]], [renders['K'][i]], renders['G'][i].astype(np.float32), [0]).astype(np.float32)
                          - renders['N'][i]).max()) for i in chk]
        print('saved seamless', nm, out.shape, '| matting check max', dict(zip(chk, [round(v, 1) for v in d])))


if __name__ == '__main__':
    main('lo' if '--engine' in sys.argv and sys.argv[sys.argv.index('--engine') + 1] == 'lo' else 'ppt', reuse='--reuse' in sys.argv)
