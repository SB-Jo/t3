"""낭독 목소리 후보의 추정 나이·성별(audeering wav2vec2 age-gender, 기기 안에서만 돎), 높이(F0), 높낮이 폭, 밝기를 잰다.
  ~/.cache/weave-tools/age-venv/bin/python -I voice_age.py <wav 폴더> [wav 이름 …]
모델은 ~/.cache/weave-tools/age-model-dl (저장소 밖). 소리를 들을 수 없을 때 목소리를 고르는 데 쓴다."""
import sys
import wave
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from transformers import Wav2Vec2Processor
from transformers.models.wav2vec2.modeling_wav2vec2 import Wav2Vec2Model, Wav2Vec2PreTrainedModel

MODEL = Path.home() / '.cache' / 'weave-tools' / 'age-model-dl'


class ModelHead(nn.Module):
    def __init__(self, config, num_labels):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.dropout = nn.Dropout(config.final_dropout)
        self.out_proj = nn.Linear(config.hidden_size, num_labels)

    def forward(self, features, **kwargs):
        x = self.dropout(features)
        x = torch.tanh(self.dense(x))
        x = self.dropout(x)
        return self.out_proj(x)


class AgeGenderModel(Wav2Vec2PreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.wav2vec2 = Wav2Vec2Model(config)
        self.age = ModelHead(config, 1)
        self.gender = ModelHead(config, 3)
        self.post_init()

    def forward(self, input_values):
        h = self.wav2vec2(input_values)[0].mean(dim=1)
        return self.age(h), torch.softmax(self.gender(h), dim=1)


def load(p):
    with wave.open(str(p), 'rb') as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return sr, x


def to16k(x, sr):
    n, fc = 127, 7400 / sr
    h = 2 * fc * np.sinc(2 * fc * (np.arange(n) - (n - 1) / 2)) * np.hamming(n)
    y = np.convolve(x, h / h.sum(), mode='same')
    k = int(round(len(y) * 16000 / sr))
    return np.interp(np.arange(k) * sr / 16000, np.arange(len(y)), y).astype(np.float32)


def f0_track(x, sr, lo=110, hi=420):
    """자기상관으로 프레임마다 F0(유성 구간만)."""
    win, hop = int(sr * 0.04), int(sr * 0.01)
    out = []
    for i in range(0, len(x) - win, hop):
        s = x[i:i + win]
        if np.sqrt((s ** 2).mean()) < 0.02:
            continue
        s = s - s.mean()
        ac = np.correlate(s, s, 'full')[win - 1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        a, b = int(sr / hi), int(sr / lo)
        k = a + int(np.argmax(ac[a:b]))
        if ac[k] > 0.55:
            out.append(sr / k)
    return np.array(out)


def measures(x, sr):
    f0 = f0_track(x, sr)
    st = 12 * np.log2(f0 / np.median(f0))
    win = int(sr * 0.02)
    e = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode='same'))
    voiced = e > max(0.003, 0.03 * e.max())
    spoken = voiced.sum() / sr
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    fr = np.fft.rfftfreq(len(x), 1 / sr)
    cent = (spec * fr).sum() / spec.sum()
    hi = spec[(fr > 4000) & (fr < 8000)].sum() / spec[(fr > 100) & (fr < 4000)].sum()
    return dict(f0=np.median(f0), f0_sd=np.std(st), f0_rng=np.percentile(st, 95) - np.percentile(st, 5), spoken=spoken, cent=cent, hi=hi)


d = Path(sys.argv[1])
names = sys.argv[2:] or sorted(p.stem for p in d.glob('*.wav'))
proc = Wav2Vec2Processor.from_pretrained(str(MODEL))
model = AgeGenderModel.from_pretrained(str(MODEL)).eval()
print('%-10s %5s %5s %5s %5s | %6s %6s %6s | %5s %6s %6s' % ('목소리', '나이', '여', '남', '아이', 'F0', 'F0폭', 'F0sd', '말(초)', '밝기Hz', '고역'))
for n in names:
    sr, x = load(d / (n + '.wav'))
    y = to16k(x, sr)
    ages, gens = [], []
    seg = 16000 * 6
    for i in range(0, max(len(y) - seg // 2, 1), seg):          # 6초씩 나눠 재고 평균
        c = y[i:i + seg]
        if len(c) < 16000 * 2:
            continue
        iv = proc(c, sampling_rate=16000, return_tensors='pt').input_values
        with torch.no_grad():
            a, g = model(iv)
        ages.append(float(a[0, 0]) * 100)
        gens.append(g[0].numpy())
    g = np.mean(gens, axis=0)
    m = measures(x, sr)
    print('%-10s %5.1f %5.2f %5.2f %5.2f | %6.0f %6.1f %6.2f | %5.2f %6.0f %6.3f' % (n, np.mean(ages), g[0], g[1], g[2], m['f0'], m['f0_rng'], m['f0_sd'],
                                                                              m['spoken'], m['cent'], m['hi']))
