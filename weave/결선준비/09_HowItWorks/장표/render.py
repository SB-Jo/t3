#!/usr/bin/env python3
"""PowerPoint(Windows, COM)로 렌더해 확인.

  python render.py states      out/HowItWorks_단계확인.pptx → out/단계/s01.png… + out/단계_한눈에.png
  python render.py video       out/HowItWorks_자동재생.pptx → out/HowItWorks_미리보기.mp4 (PowerPoint CreateVideo)

열려 있는 PowerPoint 창·다른 프레젠테이션은 건드리지 않음(07_소스/slides/tools/ppt_export.ps1과 같은 방식: 사본을 창 없이 열고
그 사본만 닫으며, PowerPoint가 원래 켜져 있었으면 끄지 않음).
"""
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'out'
WINTMP = Path('/mnt/c/Temp/weave-ppt')
PS_EXPORT = ROOT / '07_소스' / 'slides' / 'tools' / 'ppt_export.ps1'
POWERSHELL = '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'

VIDEO_PS1 = r'''param([string]$Pptx, [string]$Mp4, [int]$Secs = 40, [int]$H = 1080)
$ErrorActionPreference = "Stop"
$running = @(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Pptx, 0, 0, 0)
try {
  foreach ($s in $pres.Slides) { $s.SlideShowTransition.AdvanceOnTime = -1; $s.SlideShowTransition.AdvanceTime = $Secs }
  $pres.CreateVideo($Mp4, $true, $Secs, $H, 30, 90)
  $t = 0
  while ($pres.CreateVideoStatus -eq 1 -or $pres.CreateVideoStatus -eq 2) { Start-Sleep -Seconds 2; $t += 2; if ($t -gt 1500) { break } }
  "status " + $pres.CreateVideoStatus
} finally {
  $pres.Saved = -1
  $pres.Close()
  if (-not $running) { $app.Quit() }
  [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres)
  [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($app)
}
'''


def winpath(p):
    return subprocess.run(['wslpath', '-w', str(p)], capture_output=True, text=True, check=True).stdout.strip()


def ps(script, *args, timeout=1800):
    r = subprocess.run([POWERSHELL, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', winpath(script), *args],
                       cwd=WINTMP, capture_output=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).decode('utf-8', 'replace')


def states(src=OUT / 'HowItWorks_단계확인.pptx', W=1920, H=1080, tag='단계'):
    WINTMP.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PS_EXPORT, WINTMP / 'ppt_export.ps1')
    tmp = WINTMP / ('hiw-%s.pptx' % 'states')
    shutil.copyfile(src, tmp)
    outdir = WINTMP / 'hiw-png'
    shutil.rmtree(outdir, ignore_errors=True)
    code, log = ps(WINTMP / 'ppt_export.ps1', '-Pptx', winpath(tmp), '-OutDir', winpath(outdir), '-W', str(W), '-H', str(H))
    print(log.strip()[-300:])
    assert code == 0, log
    dst = OUT / tag
    shutil.rmtree(dst, ignore_errors=True)
    dst.mkdir(parents=True)
    pngs = sorted(outdir.glob('s*.png'))
    for p in pngs:
        shutil.copyfile(p, dst / p.name)
    shutil.rmtree(outdir, ignore_errors=True)
    tmp.unlink()
    sheet(sorted(dst.glob('s*.png')), OUT / ('%s_한눈에.png' % tag))
    return dst


def sheet(pngs, dst, cols=3, w=640):
    ims = [Image.open(p).convert('RGB') for p in pngs]
    h = int(w * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new('RGB', (cols * (w + 12) + 12, rows * (h + 34) + 12), 'white')
    dr = ImageDraw.Draw(sh)
    try:
        fnt = ImageFont.truetype(str(ROOT / '06_에셋' / '글꼴' / 'NotoSansKR-700.ttf'), 18)
    except OSError:
        fnt = None
    for i, im in enumerate(ims):
        x, y = 12 + (i % cols) * (w + 12), 12 + (i // cols) * (h + 34)
        sh.paste(im.resize((w, h), Image.LANCZOS), (x, y + 24))
        dr.text((x, y), '클릭 %d' % i, fill=(60, 50, 90), font=fnt)
    sh.save(dst)
    print('→', dst)


def video(src=OUT / "HowItWorks_자동재생.pptx", secs=50):
    WINTMP.mkdir(parents=True, exist_ok=True)
    (WINTMP / 'hiw_video.ps1').write_text('﻿' + VIDEO_PS1, encoding='utf-8')
    tmp = WINTMP / 'hiw-auto.pptx'
    shutil.copyfile(src, tmp)
    mp4 = WINTMP / 'hiw-auto.mp4'
    if mp4.exists():
        mp4.unlink()
    code, log = ps(WINTMP / 'hiw_video.ps1', '-Pptx', winpath(tmp), '-Mp4', winpath(mp4), '-Secs', str(secs))
    print(log.strip()[-300:])
    assert code == 0 and mp4.exists(), log
    shutil.copyfile(mp4, OUT / 'HowItWorks_미리보기.mp4')
    mp4.unlink()
    tmp.unlink()
    print('→', OUT / 'HowItWorks_미리보기.mp4')


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'states'
    if what == 'states':
        states()
    elif what == 'video':
        video()
