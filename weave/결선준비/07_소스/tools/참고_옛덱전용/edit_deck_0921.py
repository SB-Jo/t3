# 0921/통합_claude0927_반영본.pptx 수정 (2026-09-27 요청)
#   1) 숨김 9번 슬라이드의 앱 화면 3장을 'App Demo'(14 / Appendix) 제목 아래에 배치
#   2) 9번 슬라이드 삭제
#   3) 12번 라벨 '9 / WHY NOW' → '09 / WHY NOW'
# 입력은 수정 전 사본(deck-versions/1_표지교체.pptx), 출력은 0921의 덱. 다시 실행해도 같은 결과가 나옵니다.
#   python tools/edit_deck_0921.py
import copy
import io
import struct
from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.util import Emu

ROOT = Path(__file__).resolve().parent.parent           # claude_0927
SRC = ROOT / 'deck-versions' / '1_표지교체.pptx'
DST = ROOT.parent / '통합_claude0927_반영본.pptx'
ASSET = ROOT / 'assets' / 'app-demo'
PX = 9525                                                 # 1280×720 기준 1px = 9525 EMU

# 세 화면은 같은 폰 프레임(바깥 윤곽 548×1097px)을 서로 다른 여백으로 캡처한 것 → 윤곽 상자만 남기고 바깥(배경·잘린 그림자)은 투명하게
OUTLINE = {'그림 4': (16, 12, 563, 1108), '그림 8': (22, 12, 570, 1108), '그림 10': (6, 2, 553, 1097)}
NAMES = {'그림 4': ('app-demo-1-call.png', 'App Demo 1 · 통화 중 기억 검색', '통화 화면에서 “어제 A사 시연 준비”로 찾은 연결된 기억'),
         '그림 8': ('app-demo-2-weave.png', 'App Demo 2 · Weave 검색', 'Weave에서 “지은이네 집들이 때 먹었던 와인”으로 찾은 기억과 자동 완성 추천'),
         '그림 10': ('app-demo-3-chat.png', 'App Demo 3 · 채팅 자동 완성', '엄마와의 채팅에서 연결된 기억으로 “무화과시루” 답장 자동 완성')}
CORNER_R = 64       # 폰 모서리 반지름(px, 원본 이미지 기준) — 확대 비교로 결정
SS = 4              # 마스크 안티에일리어싱 배율


def emf_bitmap(blob):
    """EMR_HEADER + EMR_STRETCHDIBITS 1개 + EMR_EOF로만 된 EMF에서 비트맵을 꺼냄 (벡터 없음 확인 후 사용)"""
    pos, types, bmp = 0, [], None
    while pos < len(blob):
        t, size = struct.unpack_from('<II', blob, pos)
        types.append(t)
        if t == 81:
            off_bmi, cb_bmi, off_bits, cb_bits = struct.unpack_from('<4I', blob, pos + 48)
            bmi = blob[pos + off_bmi:pos + off_bmi + cb_bmi]
            bits = blob[pos + off_bits:pos + off_bits + cb_bits]
            bmp = b'BM' + struct.pack('<IHHI', 14 + len(bmi) + len(bits), 0, 0, 14 + len(bmi)) + bmi + bits
        if t == 14 or size == 0:
            break
        pos += size
    assert types == [1, 81, 14], f'예상과 다른 EMF 구성: {types}'
    return Image.open(io.BytesIO(bmp)).convert('RGB')


def cutout(im, box):
    L, T, R, B = box
    crop = im.crop((L - 1, T - 1, R + 2, B + 2))            # 윤곽 바깥 1px 여유
    w, h = crop.size
    m = Image.new('L', (w * SS, h * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle([0.5 * SS, 0.5 * SS, (w - 0.5) * SS - 1, (h - 0.5) * SS - 1], radius=CORNER_R * SS, fill=255)
    out = crop.convert('RGBA')
    out.putalpha(m.resize((w, h), Image.LANCZOS))
    return out


def add_shadow(pic):
    # 원본 캡처에 있던 그림자를 대신하는 옅은 그림자 (알파를 따라감)
    spPr = pic._element.spPr
    eff = etree.SubElement(spPr, qn('a:effectLst'))
    sh = etree.SubElement(eff, qn('a:outerShdw'), blurRad=str(14 * PX), dist=str(4 * PX), dir='5400000', algn='t', rotWithShape='0')
    clr = etree.SubElement(sh, qn('a:srgbClr'), val='1C1A24')
    etree.SubElement(clr, qn('a:alpha'), val='16000')


def main():
    prs = Presentation(str(SRC))
    slides = list(prs.slides)
    s9, demo, why_now = slides[8], slides[16], slides[11]
    assert s9._element.get('show') == '0', '9번이 숨김 슬라이드가 아님'
    assert any(sh.has_text_frame and sh.text_frame.text == 'App Demo' for sh in demo.shapes), '17번이 App Demo가 아님'

    # 1) 화면 3장 잘라내기 (원래 순서: 왼쪽→오른쪽)
    ASSET.mkdir(parents=True, exist_ok=True)
    pics = sorted([sh for sh in s9.shapes if sh.shape_type == 13], key=lambda s: s.left)
    cut = []
    for sh in pics:
        img = sh.image
        im = emf_bitmap(img.blob) if img.content_type in ('image/x-emf', 'image/x-wmf') else Image.open(io.BytesIO(img.blob)).convert('RGB')
        c = cutout(im, OUTLINE[sh.name])
        fn, name, descr = NAMES[sh.name]
        c.save(ASSET / fn)
        cut.append((ASSET / fn, name, descr, c.size))

    # 배치: 폰 높이 500px, 제목 아래 영역(y 119~720) 세로 가운데 → top 170, 폰 사이 간격 64px, 가로 가운데
    H, TOP, GAP = 500, 170, 64
    widths = [w * H / h for _, _, _, (w, h) in cut]
    x = (1280 - (sum(widths) + GAP * (len(cut) - 1))) / 2
    for (path, name, descr, _), w in zip(cut, widths):
        pic = demo.shapes.add_picture(str(path), Emu(round(x * PX)), Emu(TOP * PX), Emu(round(w * PX)), Emu(H * PX))
        pic.name = name
        pic._element.nvPicPr.cNvPr.set('descr', descr)
        add_shadow(pic)
        x += w + GAP

    # 2) 9번 슬라이드 삭제
    sld_ids = prs.slides._sldIdLst
    sld = list(sld_ids)[8]
    prs.part.drop_rel(sld.get(qn('r:id')))
    sld_ids.remove(sld)

    # 3) 라벨 번호 두 자리로 (글자 폭 118.8px < 상자 124.2px, 다른 라벨과 같은 여유라 상자는 그대로)
    runs = [r for sh in why_now.shapes if sh.has_text_frame for p in sh.text_frame.paragraphs for r in p.runs if r.text == '9 / WHY NOW']
    assert len(runs) == 1
    runs[0].text = '09 / WHY NOW'

    prs.save(str(DST))
    print('saved', DST, '| slides', len(prs.slides))


if __name__ == '__main__':
    main()
