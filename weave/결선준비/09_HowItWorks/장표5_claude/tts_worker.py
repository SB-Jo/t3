#!/usr/bin/env python3
"""낭독 일꾼. tts_c.py가 따로 둔 환경(~/.cache/weave-tools/tts-venv)의 파이썬으로 부른다. 모델은 기기 안에서만 돌고 인터넷을 쓰지 않는다.

  python -I tts_worker.py synth <Supertonic 3 폴더> <목록 파일> <나올 폴더> <목소리> <속도> <단계 수>
      목록 파일은 한 줄에 '이름<TAB>읽을 글'. 나올 폴더에 <이름>.wav(16비트 모노)를 쓴다.
      목소리는 F1~F5, M1~M5, 또는 둘을 섞은 'F2F1_70'(F2 30% + F1 70%).
  python -I tts_worker.py asr <Whisper 폴더> <목록 파일>
      목록 파일은 한 줄에 wav 경로 하나. 'wav 경로<TAB>받아쓴 글'을 찍는다(낭독이 글대로 읽혔는지 점검하는 데 씀).
"""
import json
import os
import re
import sys
import tempfile
import wave
import zlib
from pathlib import Path

import numpy as np


def _style(tts, model_dir, voice):
    """목소리 이름 → style. 'F2F1_70'처럼 적으면 기본 목소리 둘의 style 값을 섞는다(앞 목소리 30% + 뒤 목소리 70%)."""
    m = re.fullmatch(r'([FM]\d)([FM]\d)_(\d{1,2})', voice)
    if not m:
        return tts.get_voice_style(voice)
    w = int(m.group(3)) / 100
    ja, jb = (json.loads((Path(model_dir) / 'voice_styles' / (n + '.json')).read_text()) for n in m.group(1, 2))
    for k in ('style_ttl', 'style_dp'):
        ja[k]['data'] = ((1 - w) * np.array(ja[k]['data'], dtype=np.float32) + w * np.array(jb[k]['data'], dtype=np.float32)).tolist()
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(ja, f)
    try:
        return tts.get_voice_style_from_path(f.name)
    finally:
        os.unlink(f.name)


def synth(model_dir, lst, out, voice, speed, steps):
    from supertonic import TTS
    tts = TTS(model='supertonic-3', model_dir=Path(model_dir), auto_download=False)
    style = _style(tts, model_dir, voice)
    n = 0
    for line in Path(lst).read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        name, text = line.split('\t', 1)
        np.random.seed(zlib.crc32(text.encode('utf-8')) & 0x7fffffff)          # 같은 글은 늘 같은 소리로
        wav, _ = tts.synthesize(text, voice_style=style, total_steps=int(steps), speed=float(speed), lang='ko')
        x = np.clip(wav.squeeze(), -1, 1)
        with wave.open(str(Path(out) / (name + '.wav')), 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(tts.sample_rate)
            w.writeframes((x * 32767).astype(np.int16).tobytes())
        n += 1
    print('done %d' % n)


def _to16k(x, sr):
    """Whisper가 듣는 16kHz로 바꾼다(8kHz 위를 걸러 낸 뒤 다시 표본을 뜸). 앞뒤에 0.2초 묵음을 붙인다."""
    y = x
    if sr != 16000:
        n, fc = 127, 7400 / sr
        h = 2 * fc * np.sinc(2 * fc * (np.arange(n) - (n - 1) / 2)) * np.hamming(n)
        y = np.convolve(x, h / h.sum(), mode='same')
        k = int(round(len(y) * 16000 / sr))
        y = np.interp(np.arange(k) * sr / 16000, np.arange(len(y)), y)
    return np.concatenate([np.zeros(3200, np.float32), y.astype(np.float32), np.zeros(3200, np.float32)])


def asr(model_dir, lst):
    from faster_whisper import WhisperModel
    model = WhisperModel(str(model_dir), device='cpu', compute_type='int8', cpu_threads=os.cpu_count() or 4)
    for p in Path(lst).read_text(encoding='utf-8').splitlines():
        if not p.strip():
            continue
        with wave.open(p, 'rb') as w:
            sr = w.getframerate()
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        segs, _ = model.transcribe(_to16k(x, sr), language='ko', beam_size=5, condition_on_previous_text=False, without_timestamps=True)
        print('%s\t%s' % (p, ' '.join(s.text.strip() for s in segs)))


if __name__ == '__main__':
    {'synth': synth, 'asr': asr}[sys.argv[1]](*sys.argv[2:])
