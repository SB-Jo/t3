#!/usr/bin/env python3
"""미리보기 영상에 넣을 낭독(TTS). 모두 이 컴퓨터 안에서 만든다(글을 밖으로 보내지 않는다).

목소리는 둘 가운데 하나를 쓴다.
  - Supertonic 3(신경망 음성, ONNX, CPU): 목소리 F1~F5, M1~M5. 기본은 F2(밝고 젊은 여성 목소리. 11-10 5차: 발표자가 20대 여성이라 F3에서 바꿈).
    따로 둔 환경과 모델이 있어야 한다(없으면 아래 Windows 음성으로 넘어감):
      ~/.cache/weave-tools/tts-venv      pip install supertonic        (받아쓰기 점검까지 하려면 faster-whisper도)
      ~/.cache/weave-tools/supertonic-3  Hugging Face Supertone/supertonic-3의 onnx/, voice_styles/, config.json
      ~/.cache/weave-tools/whisper-turbo faster-whisper large-v3-turbo (점검용, 없어도 됨)
  - 'heami': Windows에 깔려 있는 한국어 음성(Microsoft Heami, SAPI). PowerShell은 render_c와 같은 방식으로 부른다.

  python tts_c.py "읽을 글" [목소리]        → out/tts_test.wav 와 길이(초)
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np

import render_c

HERE = Path(__file__).resolve().parent
TOOLS = Path.home() / '.cache' / 'weave-tools'
NEURAL_PY = TOOLS / 'tts-venv' / 'bin' / 'python'
NEURAL_MODEL = TOOLS / 'supertonic-3'
ASR_MODEL = TOOLS / 'whisper-turbo'
WORKER = HERE / 'tts_worker.py'

VOICE = 'F2'                       # Supertonic 3 목소리. 'heami'면 Windows 음성
SPEED = 1.05                       # Supertonic 속도(1.05가 모델 기본). 이 속도에서 F2는 1초에 6.1음절쯤, F3는 5.6음절쯤 읽음
SPEEDS = {}                        # 목소리마다 속도를 따로 줄 때: {'M3': 0.85}처럼(M3와 F4는 기본 속도로는 말이 빠름)
STEPS = 12                         # Supertonic 합성 단계 수(기본 8, 많을수록 고름)
SAPI_VOICE = 'Microsoft Heami Desktop'
SAPI_RATE = 0                      # SAPI 속도(-10~10). 0이 기본(낱말을 1초에 5.5~6음절로 읽음), 한 칸에 약 1.1배

TTS_PS1 = r'''param([string]$List, [string]$OutDir, [string]$Voice, [int]$Rate = 0)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.SelectVoice($Voice)
$s.Rate = $Rate
$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(22050, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
$n = 0
foreach ($line in [System.IO.File]::ReadAllLines($List, [System.Text.Encoding]::UTF8)) {
  if ($line.Trim().Length -eq 0) { continue }
  $i = $line.IndexOf("`t")
  $name = $line.Substring(0, $i)
  $text = $line.Substring($i + 1)
  $s.SetOutputToWaveFile((Join-Path $OutDir ($name + ".wav")), $fmt)
  $s.Speak($text)
  $n++
}
$s.SetOutputToNull()
$s.Dispose()
"done " + $n
'''


def has_neural():
    return NEURAL_PY.exists() and (NEURAL_MODEL / 'onnx' / 'vocoder.onnx').exists()


def pick_voice(voice=None):
    """쓸 목소리 이름. 따로 고르지 않으면 Supertonic(VOICE), 그 환경이 없으면 'heami'."""
    return voice or (VOICE if has_neural() else 'heami')


def _list_file(path, texts):
    path.write_text(''.join('%s\t%s\n' % (n, t.replace('\t', ' ').replace('\n', ' ')) for n, t in texts), encoding='utf-8')


def _worker(*args):
    """tts_worker.py를 따로 둔 환경의 파이썬으로 돌린다(-I: 그 환경 밖의 코드는 읽지 않음, 인터넷은 쓰지 않음)."""
    env = dict(os.environ, HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1')
    r = subprocess.run([str(NEURAL_PY), '-I', str(WORKER)] + [str(a) for a in args], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


def synth(texts, outdir, voice=None, speed=None):
    """texts = [(이름, 읽을 글)] → outdir/<이름>.wav. 돌려줌: {이름: 길이(초)}."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    voice = pick_voice(voice)
    if voice == 'heami':
        wt = render_c.WINTMP / ('claude-tts-%d' % int(time.time() * 1000))
        wt.mkdir(parents=True, exist_ok=True)
        (render_c.WINTMP / 'claude_tts.ps1').write_text(TTS_PS1, encoding='utf-8')
        _list_file(wt / 'list.txt', texts)
        code, log = render_c.ps(render_c.WINTMP / 'claude_tts.ps1', '-List', render_c.winpath(wt / 'list.txt'), '-OutDir', render_c.winpath(wt),
                                '-Voice', SAPI_VOICE, '-Rate', str(SAPI_RATE))
        assert code == 0 and 'done %d' % len(texts) in log, log
        for n, _ in texts:
            shutil.copyfile(wt / (n + '.wav'), outdir / (n + '.wav'))
        shutil.rmtree(wt, ignore_errors=True)
    else:
        assert has_neural(), 'Supertonic 환경이 없음(tts_c.py 머리말)'
        speed = speed or SPEEDS.get(voice, SPEED)
        cache = HERE / 'out' / 'tts_cache'                  # 같은 목소리·속도·글은 늘 같은 소리라, 한 번 만든 토막은 다시 만들지 않음
        cache.mkdir(parents=True, exist_ok=True)
        key = {n: cache / ('%s_%s.wav' % (voice, hashlib.sha1(('%s|%s|%s' % (speed, STEPS, t)).encode('utf-8')).hexdigest()[:16])) for n, t in texts}
        todo = [(n, t) for n, t in texts if not key[n].exists()]
        if todo:
            _list_file(outdir / '_list.txt', todo)
            log = _worker('synth', NEURAL_MODEL, outdir / '_list.txt', outdir, voice, speed, STEPS)
            assert 'done %d' % len(todo) in log, log
            (outdir / '_list.txt').unlink()
            for n, _ in todo:
                shutil.copyfile(outdir / (n + '.wav'), key[n])
        for n, _ in texts:
            shutil.copyfile(key[n], outdir / (n + '.wav'))
    return {n: wav_len(outdir / (n + '.wav')) for n, _ in texts}


def transcribe(paths):
    """받아쓰기(점검용, 기기 안의 Whisper). 돌려줌: {wav 경로: 받아쓴 글} — 점검용 모델이 없으면 None."""
    if not (NEURAL_PY.exists() and (ASR_MODEL / 'model.bin').exists()):
        return None
    lst = Path(paths[0]).parent / '_asr.txt'
    lst.write_text(''.join('%s\n' % p for p in paths), encoding='utf-8')
    log = _worker('asr', ASR_MODEL, lst)
    lst.unlink()
    out = {}
    for line in log.splitlines():
        if '\t' in line:
            p, t = line.split('\t', 1)
            out[p] = t
    return out


def wav_len(path):
    with wave.open(str(path), 'rb') as w:
        return w.getnframes() / w.getframerate()


def _load(path):
    with wave.open(str(path), 'rb') as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).copy()
    return sr, x


def _save(path, sr, x):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(np.clip(x, -32768, 32767).astype(np.int16).tobytes())


def tidy(path, lead=0.05, trail=0.1, gap=0.45):
    """낭독 한 토막을 다듬는다: 앞뒤의 긴 묵음(SAPI는 뒤에 0.8초쯤 붙임)을 잘라 내고, 문장 사이 쉼을 gap초까지로 줄인다.
    돌려줌: 다듬은 길이(초)."""
    sr, x = _load(path)
    win = int(sr * 0.02)
    e = np.sqrt(np.convolve((x / 32768.0) ** 2, np.ones(win) / win, mode='same'))
    voiced = e > max(0.003, 0.03 * e.max())
    idx = np.where(voiced)[0]
    if not len(idx):
        return len(x) / sr
    a, b = max(idx[0] - int(lead * sr), 0), min(idx[-1] + int(trail * sr), len(x))
    keep = np.ones(len(x), dtype=bool)
    keep[:a] = False
    keep[b:] = False
    d = np.diff(voiced[idx[0]:idx[-1] + 1].astype(np.int8))
    for s0, s1 in zip(np.where(d == -1)[0] + idx[0] + 1, np.where(d == 1)[0] + idx[0] + 1):      # 소리 사이의 쉼 [s0, s1)
        extra = (s1 - s0) - int(gap * sr)
        if extra > 0:                           # 쉼의 가운데를 덜어 냄(앞뒤 끝은 그대로 두어 소리가 끊기지 않게)
            mid = (s0 + s1) // 2
            keep[mid - extra // 2:mid - extra // 2 + extra] = False
    y = x[keep].astype(np.float32)
    f = int(sr * 0.008)                         # 자른 자리에서 딱 소리가 나지 않게 앞뒤 8ms를 살짝 줄였다 키움
    if len(y) > 2 * f:
        y[:f] *= np.linspace(0, 1, f)
        y[-f:] *= np.linspace(1, 0, f)
    _save(path, sr, y)
    return len(y) / sr


def track(clips, total, dst, peak=0.89):
    """clips = [(wav 경로, 시작 초)] → 길이 total초짜리 낭독 한 줄(dst, wav). 가장 큰 소리가 peak(-1dB)가 되게 전체를 똑같이 키운다."""
    sr = _load(clips[0][0])[0]
    out = np.zeros(int(total * sr) + sr, dtype=np.float32)
    for path, t0 in clips:
        r, x = _load(path)
        assert r == sr, path
        i = int(t0 * sr)
        x = x[:max(0, len(out) - i)]
        out[i:i + len(x)] += x
    out *= peak * 32767 / max(np.abs(out).max(), 1)
    _save(dst, sr, out)


if __name__ == '__main__':
    d = synth([('tts_test', sys.argv[1])], HERE / 'out', sys.argv[2] if len(sys.argv) > 2 else None)
    print(d)
