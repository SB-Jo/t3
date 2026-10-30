# PowerPoint로 장표를 PNG(·PDF)로 내보냄. 열린 창·다른 프레젠테이션은 건드리지 않음:
# 사본을 읽기 전용·창 없이 열고, 끝나면 이 사본만 닫음 (PowerPoint가 원래 켜져 있으면 끄지 않음)
param([string]$Pptx, [string]$OutDir, [int]$W = 2560, [int]$H = 1440, [string]$Pdf = "")
$ErrorActionPreference = "Stop"
$running = @(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Pptx, -1, 0, 0)
try {
  if ($OutDir) {
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
    for ($i = 1; $i -le $pres.Slides.Count; $i++) {
      $pres.Slides.Item($i).Export((Join-Path $OutDir ("s{0:D2}.png" -f $i)), "PNG", $W, $H)
    }
  }
  if ($Pdf) {
    # print-quality PDF via the Office interop enums; if the interop assembly is missing, fall back to SaveAs(ppSaveAsPDF = 32)
    try {
      Add-Type -AssemblyName Microsoft.Office.Interop.PowerPoint
      $pres.ExportAsFixedFormat($Pdf, [Microsoft.Office.Interop.PowerPoint.PpFixedFormatType]::ppFixedFormatTypePDF,
        [Microsoft.Office.Interop.PowerPoint.PpFixedFormatIntent]::ppFixedFormatIntentPrint)
      "pdf ExportAsFixedFormat(print)"
    } catch {
      $pres.SaveAs($Pdf, 32)
      "pdf SaveAs(32)"
    }
  }
  "slides " + $pres.Slides.Count
} finally {
  $pres.Close()
  if (-not $running) { $app.Quit() }
  [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres)
  [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($app)
}
