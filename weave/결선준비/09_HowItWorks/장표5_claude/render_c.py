#!/usr/bin/env python3
"""PowerPoint(Windows, COM)로 확인용 렌더. 열린 PowerPoint 창과 다른 프레젠테이션은 건드리지 않음
(사본을 창 없이 열고 그 사본만 닫으며, PowerPoint가 원래 켜져 있었으면 끄지 않음). 다른 작업과 겹치지 않게 flock으로 줄 세움.

  python render_c.py png <pptx> <outdir> [W H]
  python render_c.py video <pptx> <mp4> <장별 초,...>     클릭 효과까지 저절로 나오는 사본(build.py --auto)을 녹화
"""
import fcntl
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WINTMP = Path('/mnt/c/Temp/weave-ppt')
POWERSHELL = '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
PS_EXPORT = ROOT / '07_소스' / 'slides' / 'tools' / 'ppt_export.ps1'
LOCK = '/tmp/weave-ppt.lock'

VIDEO_PS1 = r'''param([string]$Pptx, [string]$Mp4, [string]$Secs, [int]$H = 1080)
$ErrorActionPreference = "Stop"
$running = @(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Pptx, 0, 0, 0)
try {
  $t = $Secs.Split(',')
  $i = 0
  foreach ($s in $pres.Slides) { $s.SlideShowTransition.AdvanceOnTime = -1; $s.SlideShowTransition.AdvanceTime = [double]$t[[Math]::Min($i, $t.Count - 1)]; $i++ }
  $pres.CreateVideo($Mp4, $true, 3, $H, 30, 92)
  $w = 0
  while ($pres.CreateVideoStatus -eq 1 -or $pres.CreateVideoStatus -eq 2) { Start-Sleep -Seconds 2; $w += 2; if ($w -gt 3000) { break } }
  "status " + $pres.CreateVideoStatus
} finally {
  $pres.Saved = -1
  $pres.Close()
  if (-not $running) { $app.Quit() }
}
'''


@contextmanager
def ppt_lock():
    with open(LOCK, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def winpath(p):
    return subprocess.run(['wslpath', '-w', str(p)], capture_output=True, text=True, check=True).stdout.strip()


def ps(script, *args, timeout=3600):
    err = ''
    for i in range(20):
        try:
            r = subprocess.run([POWERSHELL, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', winpath(script), *args],
                               cwd=WINTMP, capture_output=True, timeout=timeout)
            return r.returncode, (r.stdout + r.stderr).decode('utf-8', 'replace')
        except OSError as e:          # WSL 연동이 가끔 'Invalid argument'로 실패함 → 점점 길게 기다렸다 다시
            err = str(e)
            time.sleep(min(30, 2 * (i + 1)))
    return 1, err


def png(src, outdir, W=1920, H=1080):
    WINTMP.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PS_EXPORT, WINTMP / 'ppt_export.ps1')
    tag = 'claude-png-%d' % int(time.time() * 1000)
    tmp = WINTMP / (tag + '.pptx')
    od = WINTMP / tag
    shutil.copyfile(src, tmp)
    try:
        with ppt_lock():
            code, log = ps(WINTMP / 'ppt_export.ps1', '-Pptx', winpath(tmp), '-OutDir', winpath(od), '-W', str(W), '-H', str(H))
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
    assert code == 0, log
    outdir = Path(outdir)
    shutil.rmtree(outdir, ignore_errors=True)
    outdir.mkdir(parents=True)
    for p in sorted(od.glob('s*.png')):
        shutil.copyfile(p, outdir / p.name)
    shutil.rmtree(od, ignore_errors=True)
    return sorted(outdir.glob('s*.png'))


def video(src, mp4, secs):
    WINTMP.mkdir(parents=True, exist_ok=True)
    (WINTMP / 'claude_video.ps1').write_text('﻿' + VIDEO_PS1, encoding='utf-8')
    tag = 'claude-video-%d' % int(time.time() * 1000)
    tmp = WINTMP / (tag + '.pptx')
    out = WINTMP / (tag + '.mp4')
    shutil.copyfile(src, tmp)
    with ppt_lock():
        code, log = ps(WINTMP / 'claude_video.ps1', '-Pptx', winpath(tmp), '-Mp4', winpath(out), '-Secs',
                       ','.join('%.2f' % s for s in secs))
    assert code == 0 and out.exists(), log
    shutil.copyfile(out, mp4)
    out.unlink()
    tmp.unlink()
    return log.strip()[-40:]


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'png':
        print(png(sys.argv[2], sys.argv[3], *(int(v) for v in sys.argv[4:6])))
    elif cmd == 'video':
        print(video(sys.argv[2], sys.argv[3], [float(v) for v in sys.argv[4].split(',')]))
