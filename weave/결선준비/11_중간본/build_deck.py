#!/usr/bin/env python3
"""결선 중간본 덱 조립. 원본 02_PPT/Weave_결선.pptx는 고치지 않고, 새 파일 02_PPT/Weave_결선_중간본.pptx를 만든다.

본편: 표지(반복 영상) → Motivation → Pain Points → 인포그래픽 영상 자리 → Solution(새 시나리오 셋)
      → How it Works(장표5 A1 덱용 00판, --hiw a1_deck이면 00 없는 판) → Why Samsung → Why Now → 차별화 → 기대효과 1~3 → END
부록: App Demo, Q&A 2장
참고(발표에서 안 씀): 구분 장 → 이전 표지, 만화, 이전 시나리오 1~3, 이전 How it Works, 인트로 영상 79초

  python build_deck.py              조립 → 삼성 글꼴로 바꾸기 → PowerPoint로 영상 넣기 → 장별 PNG·한눈에
  python build_deck.py --no-png     PNG 없이
  python build_deck.py --hiw a1_deck --out /tmp/중간본_00없음.pptx   How it Works를 00 없는 판으로
  python build_deck.py --team-style side      표지 팀 이름을 '이름 둘 | 팀 두 줄'로
  python build_deck.py --embed-fonts          글꼴을 pptx 안에 넣어 저장(받는 사람이 글꼴 없이도 보게, 용량 늘어남)

영상은 PowerPoint(COM)로 넣는다: 표지 = 자동 재생 + 끝나면 반복, 인트로 = 자동 재생 한 번.
열려 있는 PowerPoint 창은 건드리지 않는다(C:\\Temp 사본을 창 없이 열고 그 사본만 닫음).
"""
import argparse
import copy
import shutil
import subprocess
import sys
from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / '02_PPT' / 'Weave_결선.pptx'
DST = ROOT / '02_PPT' / 'Weave_결선_중간본.pptx'
HIW = ROOT / '09_HowItWorks' / '장표5'
SOL = ROOT / '07_소스' / 'slides' / 'p05_결선' / 'apply_solution.py'
COVER_MP4 = ROOT / '10_표지영상' / '표지_루프.mp4'
INTRO_MP4 = ROOT / '08_인트로영상' / 'Weave_인트로_79초.mp4'
VENV_PY = Path.home() / '.cache' / 'weave-tools' / 'venv' / 'bin' / 'python'

sys.path.insert(0, str(HIW))
import build5            # noqa: E402
import render2           # noqa: E402
import scene5            # noqa: E402
import story as S        # noqa: E402
from hiw_lib import q    # noqa: E402
import samsung_fonts     # noqa: E402

COVER_NOTES = ('표지(반복 영상). 구글 검색창에 ‘지은이네 집들이 때 마신 화이트 와인’을 적고 실타래 버튼을 누르면, 흩어진 기록 가운데 '
               '지은의 카톡과 그날 사진이 보라색 실로 이어져 ‘배비치 소비뇽 블랑’을 건네고, 입력하기를 누르면 검색어가 바뀌는 장면이 반복됩니다. '
               '발표를 시작하기 전부터 띄워 둡니다.')
INTRO_NOTES = ('참고: 인트로 영상 79초(v8). 01 와인은 캘린더판, 02는 A사 시연 통화, 03은 무화과시루라서 '
               '새 시나리오(요청 자료, 갈색병)와 맞지 않아 본편에서 뺐습니다. 쓰려면 02·03 장면을 새 시나리오로 바꿔야 합니다.')


def text_slide(prs, layout, name, lines, notes):
    """참고 구분 장처럼 글만 있는 장(HIW와 같은 바탕·글꼴)."""
    s = prs.slides.add_slide(layout)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    pa = S.Painter(s)
    for p in build5.bg_prims():
        pa.prim(p)
    cw = S.tw(name, 10.5, 'sb') + 32
    pa.prim(S.R('ref/chip', 640 - cw / 2, 250, cw, 28, prst='roundRect', fill=S.PURPLE, line=None))
    pa.prim(S.T('ref/chip_t', 640 - cw / 2, 250, cw, 28, name, size=10.5, color='FFFFFF', weight='sb', align='c', anchor='ctr', spc=0.5))
    pa.prim(S.T('ref/title', 140, 296, 1000, 50, lines[0], size=26, color=S.INK, weight='b', align='c', anchor='ctr'))
    pa.prim(S.T('ref/sub', 140, 356, 1000, 90, list(lines[1:]), size=13, color='5B5866', align='c', lnspc=20))
    set_notes(s, notes)
    return s


TEAMS = [('AI System Team', ['이재웅', '양서윤']), ('AI Core Team', ['장이준', '이지현']), ('오디오개발Lab', ['조성빈'])]
TITLE, TAGLINE = 'Weave Assist', '흩어진 기억을 엮어, 지금을 완성하다'     # 이전 표지와 같은 문구
CX = 70                                         # 표지 글 왼쪽 끝. 영상의 왼쪽 빈 자리는 x < 564(1280 기준)
MARK = 56                                       # 'Weave' 앞 아이콘(인트로 끝 화면의 보라 네모 + 흰 실타래)
FONTS = Path.home() / '.cache' / 'weave-tools' / 'fonts'
GRAD = ('<a:gradFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" rotWithShape="1">'
        '<a:gsLst><a:gs pos="0"><a:srgbClr val="4E36CF"/></a:gs><a:gs pos="100000"><a:srgbClr val="8F66FF"/>'
        '</a:gs></a:gsLst><a:lin ang="0" scaled="1"/></a:gradFill>')


def fw(text, pt, face):
    """실제 삼성 글꼴로 잰 글 폭(px, 1280 기준). 글꼴 파일이 없으면 엔진 어림값."""
    try:
        f = ImageFont.truetype(str(FONTS / face), 1000)
        return f.getlength(text) / 1000 * pt * 96 / 72
    except OSError:
        return S.tw(text, pt, 'b' if '700' in face else 'r')


def cover_text(slide, team_style='under'):
    """표지 왼쪽 글: 아이콘 + 제목(보라 그라데이션) · 부제 · 팀별 이름. 영상은 PowerPoint로 맨 뒤에 깔림.

    team_style: 'under' = 팀원 이름을 한 줄로 두고 그 아래 가는 선 + 팀 이름(세 팀이 한 줄)
                'side'  = 이름 둘을 위아래로, 오른쪽에 팀 이름을 두 줄로(사용자 제안 'AI System / Team')
    """
    pa = S.Painter(slide)                        # 바탕은 영상이 깔므로 도형 바탕은 그리지 않음(영상이 그 뒤로 숨지 않게)
    cy = 260                                     # 제목 줄 가운데
    pa.prim(S.R('cover/mark', CX, cy - MARK / 2, MARK, MARK, prst='roundRect', radius=15, line=None,
                grad=dict(stops=[(0, '8D6BFF', None), (55, '6B4EFF', None), (100, '5A3FE0', None)], ang=55),
                shadow=(18, 7, '6B4EFF', 30)))
    ic = MARK * 2 / 3
    pa.prim(S.P('cover/mark_icon', 'weave-spool-white.png', CX + (MARK - ic) / 2, cy - ic / 2, ic, ic))
    tx = CX + MARK + 13
    t = pa.prim(S.T('cover/title', tx - 2, cy - 38, 470, 76, TITLE, size=48, color=S.PURPLE, weight='b', anchor='ctr',
                    spc=-0.5))
    for rp in t.iter(q('a:rPr'), q('a:endParaRPr')):
        for tag in ('a:latin', 'a:ea', 'a:cs'):          # 로고 글꼴(인트로 끝 화면과 같음). 굵게는 이 글꼴의 Bold
            e = rp.find(q(tag))
            if e is not None:
                e.set('typeface', 'Samsung Sharp Sans')
        old = rp.find(q('a:solidFill'))
        if old is None:
            continue
        old.addprevious(etree.fromstring(GRAD))
        rp.remove(old)
    pa.prim(S.T('cover/sub', CX + 1, 306, 520, 40, TAGLINE, size=20, color=S.INK2, weight='m', anchor='ctr'))

    x = CX + 1
    if team_style == 'under':
        for k, (team, names) in enumerate(TEAMS):
            nw = [fw(n, 13, 'SamsungOneKorean-700.ttf') for n in names]
            gap = 14
            names_w = sum(nw) + gap * (len(names) - 1)
            gw = max(names_w, fw(team, 9.5, 'SamsungOneKorean-400.ttf'))
            nx = x
            for i, n in enumerate(names):
                pa.prim(S.T('cover/n%d%d' % (k, i), nx, 584, nw[i] + 8, 22, n, size=13, color=S.INK, weight='b'))
                nx += nw[i] + gap
            pa.prim(S.R('cover/line%d' % k, x, 611, gw, 1.3, fill='C3B6F7', line=None))
            pa.prim(S.T('cover/team%d' % k, x, 617, gw + 12, 18, team, size=9.5, color=S.SUB))
            x += gw + 40
    else:
        for k, (team, names) in enumerate(TEAMS):
            nw = max(fw(n, 13, 'SamsungOneKorean-700.ttf') for n in names)
            for i, n in enumerate(names):
                pa.prim(S.T('cover/n%d%d' % (k, i), x, 578 + i * 26, nw + 8, 22, n, size=13, color=S.INK, weight='b'))
            lx = x + nw + 11
            rows = team.rsplit(' ', 1) if len(names) > 1 and ' ' in team else [team]
            pa.prim(S.R('cover/line%d' % k, lx, 582, 1.3, 26 * len(names) - 8, fill='C3B6F7', line=None))
            tw_ = max(fw(r, 10, 'SamsungOneKorean-400.ttf') for r in rows)
            for i, r in enumerate(rows):
                pa.prim(S.T('cover/team%d%d' % (k, i), lx + 11, 581 + i * 26, tw_ + 12, 20, r, size=10, color=S.SUB))
            x = lx + 11 + tw_ + 36


INFO_NOTES = ('인포그래픽 영상 자리(약 1분 20초, 자동 재생). 새 인포그래픽 영상을 이 장에 넣고, 가운데 안내 표시는 지웁니다. '
              'Pain Points의 세 불편 바로 뒤에서, 영상의 세 장면이 하나씩 답하고 Weave Assist 로고로 끝나 Solution으로 이어 갑니다.')


def info_slide(prs, layout):
    """인포그래픽 영상이 들어갈 자리(본편 2쪽). 영상 넣기 전까지 보이는 안내 표시."""
    s = blank_slide(prs, layout, INFO_NOTES)
    pa = S.Painter(s)
    for p in build5.bg_prims():
        pa.prim(p)
    pa.prim(S.R('info/frame', 70, 50, 1140, 620, prst='roundRect', radius=26, fill='FFFFFF', alpha=45,
                line='9C86F7', line_w=1.6, dash='dash'))
    pa.prim(S.R('info/play', 640 - 40, 240, 80, 80, prst='ellipse', fill=S.PURPLE, line=None, shadow=(24, 8, '6B4EFF', 24)))
    tri = pa.prim(S.R('info/tri', 640 - 11, 280 - 15, 30, 30, prst='triangle', fill='FFFFFF', line=None))
    tri.find('.//' + q('a:xfrm')).set('rot', str(90 * 60000))          # 위를 보는 삼각형 → 오른쪽(재생 표시)
    cw = S.tw('영상 넣을 자리', 10.5, 'sb') + 32
    pa.prim(S.R('info/chip', 640 - cw / 2, 352, cw, 28, prst='roundRect', fill=S.PURPLE, line=None))
    pa.prim(S.T('info/chip_t', 640 - cw / 2, 352, cw, 28, '영상 넣을 자리', size=10.5, color='FFFFFF', weight='sb', align='c',
                anchor='ctr', spc=0.5))
    pa.prim(S.T('info/title', 140, 392, 1000, 50, '인포그래픽 영상', size=28, color=S.INK, weight='b', align='c', anchor='ctr'))
    pa.prim(S.T('info/sub', 140, 446, 1000, 50, ['약 1분 20초, 전체 화면으로 자동 재생', '영상을 넣으면 이 안내는 지워 주세요'],
                size=13, color='5B5866', align='c', lnspc=21))
    return s


def blank_slide(prs, layout, notes):
    s = prs.slides.add_slide(layout)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    set_notes(s, notes)
    return s


NOTE_TPL = []


def set_notes(slide, text):
    ns = slide.notes_slide
    if ns.notes_text_frame is None:
        for e in NOTE_TPL:
            ns.shapes._spTree.append(copy.deepcopy(e))
    ns.notes_text_frame.text = text


def reorder(prs, order):
    lst = prs.slides._sldIdLst
    by_part = {}
    for e in list(lst):
        by_part[prs.part.related_part(e.get(q('r:id')))] = e
    assert len(order) == len(by_part) == len(set(id(s) for s in order)), (len(order), len(by_part))
    for e in list(lst):
        lst.remove(e)
    for s in order:
        lst.append(by_part[s.part])


MEDIA_PS1 = r'''param([string]$Pptx, [string]$CoverMp4 = "", [string]$IntroMp4 = "", [int]$CoverIdx = 1, [int]$IntroIdx = 0,
      [string]$CoverPoster = "", [string]$IntroPoster = "", [int]$EmbedFonts = 0)
$ErrorActionPreference = "Stop"
$running = @(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Pptx, 0, 0, 0)
try {
  $W = $pres.PageSetup.SlideWidth; $H = $pres.PageSetup.SlideHeight
  $log = @()
  foreach ($job in @(@($CoverIdx, $CoverMp4, "Cover loop video", -1, $CoverPoster), @($IntroIdx, $IntroMp4, "Intro video 79s", 0, $IntroPoster))) {
    if (-not $job[1]) { continue }
    $s = $pres.Slides.Item($job[0])
    $v = $s.Shapes.AddMediaObject2($job[1], 0, -1, 0, 0, $W, $H)
    $v.Name = $job[2]
    $v.ZOrder(1)
    if ($job[4]) { $v.MediaFormat.SetDisplayPictureFromFile($job[4]) }
    $ps = $v.AnimationSettings.PlaySettings
    $ps.PlayOnEntry = -1
    $ps.LoopUntilStopped = $job[3]
    $ps.HideWhileNotPlaying = 0
    $ps.RewindMovie = 0
    $seq = $s.TimeLine.MainSequence
    $t = "slide " + $job[0] + " effects " + $seq.Count
    for ($i = 1; $i -le $seq.Count; $i++) {
      $e = $seq.Item($i)
      $t += " [type " + $e.EffectType + " trig " + $e.Timing.TriggerType
      if ($e.Timing.TriggerType -eq 1) { $e.Timing.TriggerType = 2; $t += "->2" }
      $t += "]"
    }
    $t += " loop " + $ps.LoopUntilStopped + " playOnEntry " + $ps.PlayOnEntry
    $log += $t
  }
  if ($EmbedFonts) { $pres.SaveAs($Pptx, 24, -1); $log += "fonts embedded" } else { $pres.Save() }
  $log -join "`n"
} finally {
  # 사용자가 PowerPoint를 쓰는 중이면 호출이 잠깐 거부될 수 있음 → 몇 번 다시 시도(이 사본만 닫음)
  for ($k = 0; $k -lt 10; $k++) {
    try { $pres.Close(); break } catch { Start-Sleep -Seconds 2 }
  }
  if (-not $running) { $app.Quit() }
}
'''


def add_media(pptx, cover_idx, intro_idx, embed_fonts=False):
    """PowerPoint로 영상 넣기(1부터 세는 장 번호). embed_fonts면 글꼴을 파일 안에 넣어 저장."""
    tmpd = render2.WINTMP / 'midterm'
    tmpd.mkdir(parents=True, exist_ok=True)
    (tmpd / 'media.ps1').write_text('\ufeff' + MEDIA_PS1, encoding='utf-8')
    work = tmpd / 'deck.pptx'
    shutil.copyfile(pptx, work)
    args = ['-Pptx', render2.winpath(work), '-CoverIdx', str(cover_idx), '-IntroIdx', str(intro_idx),
            '-EmbedFonts', '1' if embed_fonts else '0']
    if COVER_MP4.exists():
        shutil.copyfile(COVER_MP4, tmpd / 'cover.mp4')
        poster = COVER_MP4.parent / '표지_포스터.jpg'          # 4K 포스터는 jpg가 훨씬 가벼움
        shutil.copyfile(poster if poster.exists() else COVER_MP4.parent / '표지_포스터.png', tmpd / 'cover.png')
        args += ['-CoverMp4', render2.winpath(tmpd / 'cover.mp4'), '-CoverPoster', render2.winpath(tmpd / 'cover.png')]
    else:
        print('   ! 표지 영상이 아직 없음:', COVER_MP4)
    shutil.copyfile(INTRO_MP4, tmpd / 'intro.mp4')
    ff = Path.home() / '.cache' / 'weave-tools' / 'bin' / 'ffmpeg'          # 인트로 미리보기 그림 = 첫 질문 장면(2초)
    subprocess.run([str(ff), '-y', '-loglevel', 'error', '-ss', '2', '-i', str(INTRO_MP4), '-frames:v', '1', str(tmpd / 'intro.png')],
                   check=True)
    args += ['-IntroMp4', render2.winpath(tmpd / 'intro.mp4'), '-IntroPoster', render2.winpath(tmpd / 'intro.png')]
    code, log = render2.ps(tmpd / 'media.ps1', *args)
    print(log.strip())
    assert code == 0, log
    shutil.copyfile(work, pptx)
    for f in ('deck.pptx', 'cover.mp4', 'intro.mp4', 'cover.png', 'intro.png'):
        (tmpd / f).unlink(missing_ok=True)


def sheet(pngs, dst, labels, cols=6, w=400):
    ims = [Image.open(p).convert('RGB') for p in pngs]
    h = int(w * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new('RGB', (cols * (w + 10) + 10, rows * (h + 30) + 10), 'white')
    d = ImageDraw.Draw(out)
    fnt = ImageFont.truetype(str(ROOT / '06_에셋' / '글꼴' / 'NotoSansKR-700.ttf'), 14)
    for i, im in enumerate(ims):
        x, y = 10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 30)
        out.paste(im.resize((w, h), Image.LANCZOS), (x, y + 20))
        d.text((x, y), labels[i], fill=(60, 50, 90), font=fnt)
    out.save(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-png', action='store_true')
    ap.add_argument('--hiw', default='a1_deck00', help='장표5의 SPEC 모듈(a1_deck00 = 00 있는 덱용, a1_deck = 00 없는 판)')
    ap.add_argument('--out', default=str(DST))
    ap.add_argument('--team-style', default='under', choices=['under', 'side'])
    ap.add_argument('--embed-fonts', action='store_true')
    a = ap.parse_args()
    dst = Path(a.out).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    # 1. 솔루션 장표(5쪽)를 새 시나리오로 다시 채운 사본
    step1 = Path('/tmp/midterm_step1.pptx')
    if SOL.exists():
        r = subprocess.run([str(VENV_PY), str(SOL), str(SRC), str(step1)], capture_output=True, text=True, cwd=SOL.parent)
        print(r.stdout.strip()[-400:], r.stderr.strip()[-400:])
        assert r.returncode == 0 and step1.exists(), '솔루션 장표 다시 채우기 실패'
    else:
        print('   ! 솔루션 장표 스크립트가 아직 없음 → 원래 5쪽 그대로')
        shutil.copyfile(SRC, step1)

    prs = Presentation(str(step1))
    orig = list(prs.slides)
    assert len(orig) == 19, len(orig)
    layout = orig[8].slide_layout
    NOTE_TPL[:] = [copy.deepcopy(sh._element) for sh in orig[8].notes_slide.placeholders]

    # 2. How it Works(장표5 A1 덱용)
    import importlib
    sc = scene5.build(importlib.import_module(a.hiw).SPEC)
    hiw, warns = build5.add_steps(prs, sc, layout, NOTE_TPL)
    for w in warns:
        print('   !', w)
    S.morph_transition(hiw[0], 1000)          # 솔루션 → How it Works 첫 장은 부드럽게(겹치는 도형이 없어 페이드처럼)

    # 3. 새 표지(영상은 4단계에서), 참고 구분 장, 인트로 영상 장
    cover = blank_slide(prs, layout, COVER_NOTES)
    cover_text(cover, a.team_style)
    info = info_slide(prs, layout)
    ref = text_slide(prs, layout, 'REFERENCE', ['참고 · 발표에서 쓰지 않는 장표',
                                                '이전 표지, 만화, 이전 시나리오 1~3, 이전 How it Works, 인트로 영상 79초',
                                                '새 구성(표지 영상, 솔루션, How it Works)으로 바뀌기 전 장표입니다.'],
                     '참고용 구분 장. 이 뒤의 장표는 발표에서 쓰지 않습니다.')
    intro = blank_slide(prs, layout, INTRO_NOTES)

    main_ = [cover, orig[2], orig[3], info, orig[4], *hiw, orig[9], orig[10], orig[11], orig[12], orig[13], orig[14], orig[18]]
    appx = [orig[15], orig[16], orig[17]]
    refs = [ref, orig[0], orig[1], orig[5], orig[6], orig[7], orig[8], intro]
    order = main_ + appx + refs
    reorder(prs, order)
    n = samsung_fonts.remap_prs(prs)                 # 글꼴: Inter·Noto Sans KR → SamsungOneKorean 400·500·700
    left = {f: c for f, c in samsung_fonts.faces_used(prs).items() if not f.startswith(('SamsungOne', '+', 'Samsung Sharp'))}
    print('글꼴 바꿈', dict(n), '| 남은 다른 글꼴', left)
    prs.save(str(dst))
    n_main = len(main_)
    print('조립', len(order), '장 (본편 %d, 부록 %d, 참고 %d) →' % (n_main, len(appx), len(refs)), dst)

    # 4. 영상(PowerPoint)
    add_media(dst, 1, len(order), a.embed_fonts)

    # 5. 확인용 PNG
    if not a.no_png:
        od = HERE / ('png' if dst == DST else 'png_' + dst.stem)
        render2.png(dst, od, 1600, 900)
        labels = []
        for i in range(len(order)):
            part = '본편' if i < n_main else ('부록' if i < n_main + len(appx) else '참고')
            labels.append('%d  %s' % (i + 1, part))
        sh = HERE / ('한눈에.png' if dst == DST else '한눈에_%s.png' % dst.stem)
        sheet(sorted(od.glob('s*.png')), sh, labels)
        print('한눈에 →', sh)


if __name__ == '__main__':
    main()
