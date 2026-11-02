#!/usr/bin/env python3
"""PowerPoint(Windows, COM)로 확인용 렌더.

  python render2.py png  <pptx> <outdir> [W H]     장마다 PNG(정적 상태)
  python render2.py video <pptx> <mp4> [secs]       장마다 secs초씩 머물며 모핑 전환·자동 애니메이션까지 녹화
  python render2.py check <pptx>                    장 수, 모핑 전환이 걸린 장 수, 장별 자동 효과 수

열려 있는 PowerPoint 창과 다른 프레젠테이션은 건드리지 않음(사본을 창 없이 열고 그 사본만 닫음).
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WINTMP = Path('/mnt/c/Temp/weave-ppt')
POWERSHELL = '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
PS_EXPORT = ROOT / '07_소스' / 'slides' / 'tools' / 'ppt_export.ps1'

VIDEO_PS1 = r'''param([string]$Pptx, [string]$Mp4, [double]$Secs = 3, [int]$H = 1080)
$ErrorActionPreference = "Stop"
$running = @(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Pptx, 0, 0, 0)
try {
  foreach ($s in $pres.Slides) { $s.SlideShowTransition.AdvanceOnTime = -1; $s.SlideShowTransition.AdvanceTime = $Secs }
  $pres.CreateVideo($Mp4, $true, $Secs, $H, 30, 90)
  $t = 0
  while ($pres.CreateVideoStatus -eq 1 -or $pres.CreateVideoStatus -eq 2) { Start-Sleep -Seconds 2; $t += 2; if ($t -gt 3000) { break } }
  "status " + $pres.CreateVideoStatus
} finally {
  $pres.Saved = -1
  $pres.Close()
  if (-not $running) { $app.Quit() }
}
'''

CHECK_PS1 = r'''param([string]$Pptx)
$ErrorActionPreference = "Stop"
$running = @(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Pptx, -1, 0, 0)
try {
  $m = 0; $out = @()
  foreach ($s in $pres.Slides) {
    $e = $s.SlideShowTransition.EntryEffect
    if ($e -ne 0) { $m++ }
    $out += ("" + $s.SlideIndex + ":" + $s.TimeLine.MainSequence.Count)
  }
  "slides " + $pres.Slides.Count + " morph " + $m
  "effects " + ($out -join " ")
} finally {
  $pres.Close()
  if (-not $running) { $app.Quit() }
}
'''


def winpath(p):
    return subprocess.run(['wslpath', '-w', str(p)], capture_output=True, text=True, check=True).stdout.strip()


def ps(script, *args, timeout=3600):
    for attempt in range(3):
        try:
            r = subprocess.run([POWERSHELL, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', winpath(script), *args],
                               cwd=WINTMP, capture_output=True, timeout=timeout)
            return r.returncode, (r.stdout + r.stderr).decode('utf-8', 'replace')
        except OSError as e:          # WSL 연동이 가끔 'Invalid argument'로 실패함 → 다시 시도
            err = str(e)
    return 1, err


def png(src, outdir, W=1920, H=1080):
    WINTMP.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PS_EXPORT, WINTMP / 'ppt_export.ps1')
    tmp = WINTMP / 'hiw2-png.pptx'
    shutil.copyfile(src, tmp)
    od = WINTMP / 'hiw2-png'
    shutil.rmtree(od, ignore_errors=True)
    code, log = ps(WINTMP / 'ppt_export.ps1', '-Pptx', winpath(tmp), '-OutDir', winpath(od), '-W', str(W), '-H', str(H))
    assert code == 0, log
    outdir = Path(outdir)
    shutil.rmtree(outdir, ignore_errors=True)
    outdir.mkdir(parents=True)
    for p in sorted(od.glob('s*.png')):
        shutil.copyfile(p, outdir / p.name)
    shutil.rmtree(od, ignore_errors=True)
    tmp.unlink()
    print(log.strip()[-80:], '→', outdir)


def video(src, mp4, secs=3.0):
    WINTMP.mkdir(parents=True, exist_ok=True)
    (WINTMP / 'hiw2_video.ps1').write_text('﻿' + VIDEO_PS1, encoding='utf-8')
    tmp = WINTMP / 'hiw2-video.pptx'
    shutil.copyfile(src, tmp)
    out = WINTMP / 'hiw2-video.mp4'
    if out.exists():
        out.unlink()
    code, log = ps(WINTMP / 'hiw2_video.ps1', '-Pptx', winpath(tmp), '-Mp4', winpath(out), '-Secs', str(secs))
    assert code == 0 and out.exists(), log
    shutil.copyfile(out, mp4)
    out.unlink()
    tmp.unlink()
    print(log.strip()[-60:], '→', mp4)


def check(src):
    WINTMP.mkdir(parents=True, exist_ok=True)
    (WINTMP / 'hiw2_check.ps1').write_text('﻿' + CHECK_PS1, encoding='utf-8')
    tmp = WINTMP / 'hiw2-check.pptx'
    shutil.copyfile(src, tmp)
    code, log = ps(WINTMP / 'hiw2_check.ps1', '-Pptx', winpath(tmp))
    tmp.unlink()
    print(log.strip())
    return log


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'png':
        png(sys.argv[2], sys.argv[3], *(int(v) for v in sys.argv[4:6]))
    elif cmd == 'video':
        video(sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 3.0)
    elif cmd == 'check':
        check(sys.argv[2])
