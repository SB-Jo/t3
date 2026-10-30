"""Weave 인트로 배경음악·효과음 합성 (저작권 걱정 없는 직접 합성, 48kHz 스테레오)

사용: ~/.cache/weave-tools/venv/bin/python tools/music.py   →  out/bgm.wav (음악+효과음), out/bgm_music.wav, out/bgm_sfx.wav
- 120 BPM(한 박 0.5초, 한 마디 2초), 다장조. 6초에 본편(드롭), 24초에 로고 마무리 화음.
- 진행: 도입 Am7 – Fmaj7 – G6 / 본편 Fmaj7 – G6 – Em7 – Am7 ×2 / 22초 Fmaj7 – G 쌓기 / 24초 Cmaj9.
- 효과음 시점은 out/events.json(render.cjs --events, main.js의 ev() 호출)을 따른다.
"""
import json
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out'
ev = json.loads((OUT / 'events.json').read_text())
DUR = float(ev['duration']) + 0.6
N = int(DUR * SR)
rng = np.random.default_rng(20261029)
BEAT = 0.5; BAR = 2.0


def midi(n): return 440.0 * 2 ** ((n - 69) / 12)


NOTE = {n: i for i, n in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}
def m(s):   # 'E4' → midi
    return NOTE[s[:-1]] + 12 * (int(s[-1]) + 1)


def buf(): return np.zeros((2, N), np.float32)


def add(dst, sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= N: return
    if sig.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l * 1.414, sig * r * 1.414])
    j = min(N, i + sig.shape[1]); k = j - i
    if i < 0:
        sig = sig[:, -i:]; i = 0; k = min(sig.shape[1], N)
    dst[:, i:i + k] += gain * sig[:, :k]


def lp(x, f, order=2): return sosfilt(butter(order, f / (SR / 2), 'low', output='sos'), x, axis=-1)
def hp(x, f, order=2): return sosfilt(butter(order, f / (SR / 2), 'high', output='sos'), x, axis=-1)
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos'), x, axis=-1)


def env_adsr(n, a, d, s, r, hold):
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), np.where(t < a + d, 1 - (1 - s) * (t - a) / max(d, 1e-4), s))
    rel = t > hold
    e = np.where(rel, e * np.exp(-(t - hold) / max(r, 1e-4) * 3.0), e)
    return e


# ── 리버브(합성 임펄스) ────────────────────────────
def make_ir(rt=1.9, pre=0.018, damp=5200):
    n = int(rt * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((2, n)) * np.exp(-6.9 * t / rt)
    ir = lp(ir, damp, 1)
    ir[:, : int(pre * SR)] = 0
    early = np.zeros((2, n))
    for d, g in [(0.011, .5), (0.017, .4), (0.023, .35), (0.031, .3), (0.041, .22)]:
        early[0, int(d * SR)] += g; early[1, int((d + 0.003) * SR)] += g
    ir = ir + early
    return ir / np.sqrt((ir ** 2).sum(axis=1, keepdims=True))


IR = make_ir()
IR_BIG = make_ir(3.2, 0.03, 4200)


def reverb(x, ir=IR, wet=0.3):
    y = np.stack([fftconvolve(x[0], ir[0])[:N], fftconvolve(x[1], ir[1])[:N]])
    return x * (1 - wet * 0.35) + y * wet


def delay_pp(x, dt=0.375, fb=0.38, mix=0.32, lpf=4200):
    d = int(dt * SR); y = np.zeros_like(x); src = x.copy()
    for k in range(1, 6):
        src = lp(np.roll(src, d, axis=1), lpf, 1); src[:, :d] = 0
        ch = (k % 2)
        y[ch] += src[0 if ch else 1] * (fb ** (k - 1))
    return x + mix * y


# ── 악기 ────────────────────────────────────────
def pad_note(f, dur, bright=1.0, det=0.0045):
    n = int((dur + 1.2) * SR); t = np.arange(n) / SR
    out = np.zeros((2, n))
    for ch, sgn in ((0, -1), (1, 1)):
        for v, dv in enumerate((-1, 0, 1)):
            ff = f * (1 + dv * det + sgn * 0.0012)
            ph = rng.uniform(0, 2 * np.pi)
            k_max = int(min(28, 7000 * bright / ff))
            w = np.zeros(n)
            for k in range(1, max(2, k_max)):
                w += np.sin(2 * np.pi * ff * k * t + ph * k) / k * np.exp(-k / (9 * bright))
            out[ch] += w
    e = env_adsr(n, 0.45, 0.6, 0.8, 0.55, dur)
    return out * e / 6


def pluck(f, dur=0.6, bright=1.0, hard=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    w = np.zeros(n)
    for k, a in enumerate([1, .55, .3, .22, .12, .08, .05, .03], 1):
        w += a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (5.5 + 3.2 * k / bright))
    att = np.minimum(1, t / 0.003)
    w = w * att * (1 + 0.6 * hard * np.exp(-t * 60))
    return w * 0.5


def bell(f, dur=2.2, idx=2.2, ratio=3.5):
    n = int(dur * SR); t = np.arange(n) / SR
    I = idx * np.exp(-t * 3.0)
    s = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * ratio * t))
    s += 0.35 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 5)
    return s * np.exp(-t * 2.2) * np.minimum(1, t / 0.002) * 0.5


def bass_note(f, dur):
    n = int((dur + 0.1) * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.22 * np.sin(2 * np.pi * 2 * f * t) + 0.08 * np.sin(2 * np.pi * 3 * f * t)
    e = np.minimum(1, t / 0.008) * np.where(t < dur, 1.0, np.exp(-(t - dur) * 40)) * np.exp(-t * 1.4)
    return s * e * 0.6


def kick(g=1.0):
    n = int(0.42 * SR); t = np.arange(n) / SR
    f = 46 + 95 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5)
    click = hp(rng.standard_normal(n), 2500) * np.exp(-t * 400) * 0.25
    return (s + click) * g


def clap():
    n = int(0.5 * SR); t = np.arange(n) / SR
    noise = bp(rng.standard_normal(n), 900, 3200)
    e = np.zeros(n)
    for d in (0, 0.009, 0.018):
        e += np.where(t >= d, np.exp(-(t - d) * 160), 0)
    e += np.where(t >= 0.025, np.exp(-(t - 0.025) * 22) * 0.55, 0)
    return noise * e * 0.55


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR); t = np.arange(n) / SR
    s = hp(rng.standard_normal(n), 7500, 2)
    return s * np.exp(-t * (18 if open_ else 95)) * 0.35


def noise_sweep(dur, f0, f1, q=0.6, rise=True):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n); blk = 512
    for i in range(0, n, blk):
        p = i / n
        fc = f0 * (f1 / f0) ** p
        lo, hi = max(40, fc * (1 - q / 2)), min(SR / 2 - 100, fc * (1 + q / 2))
        seg = x[max(0, i - 2048): i + blk]
        y = bp(seg, lo, hi, 1)
        out[i:i + blk] = y[-min(blk, n - i):]
    e = (t / dur) ** 2 if rise else np.exp(-t / dur * 4)
    return out * e


# ── 음악 ────────────────────────────────────────
music = buf(); pads = buf(); plk = buf(); drums = buf(); bassb = buf(); bells = buf()

CH = {   # (베이스, 화음 음들)
    'Am7': ('A1', ['A3', 'C4', 'E4', 'G4']), 'Fmaj7': ('F1', ['F3', 'A3', 'C4', 'E4']), 'G6': ('G1', ['G3', 'B3', 'D4', 'E4']),
    'Em7': ('E1', ['E3', 'G3', 'B3', 'D4']), 'G': ('G1', ['G3', 'B3', 'D4', 'G4']), 'Cmaj9': ('C2', ['C3', 'G3', 'B3', 'D4', 'E4']),
}
PROG = [(0, 'Am7'), (2, 'Fmaj7'), (4, 'G6'),
        (6, 'Fmaj7'), (8, 'G6'), (10, 'Em7'), (12, 'Am7'), (14, 'Fmaj7'), (16, 'G6'), (18, 'Em7'), (20, 'Am7'),
        (22, 'Fmaj7'), (23, 'G'), (24, 'Cmaj9')]
for i, (t0, c) in enumerate(PROG):
    t1 = PROG[i + 1][0] if i + 1 < len(PROG) else 27.2
    bright = 0.55 if t0 < 6 else (0.9 if t0 < 14 else 1.05)
    for nn in CH[c][1]:
        add(pads, pad_note(midi(m(nn)), t1 - t0 + 0.05, bright), t0, 0.16)

# 도입: 부드러운 오르골 모티프 (4초부터 '잠깐만, 찾아볼게…'에서 멈춤)
motif = [(0.25, 'E5'), (0.75, 'G5'), (1.25, 'A5'), (1.75, 'C6'), (2.25, 'B5'), (2.75, 'A5'), (3.25, 'G5'), (3.6, 'E5')]
for t, nn in motif:
    add(plk, pluck(midi(m(nn)), 1.2, 0.8, 0.6), t, 0.36, pan=rng.uniform(-.3, .3))

# 본편 아르페지오 (6 – 22초, 16분음표), 14초부터 한 옥타브 위로
ARP = {'Fmaj7': ['A4', 'C5', 'E5', 'F5', 'E5', 'C5', 'A4', 'C5'], 'G6': ['B4', 'D5', 'E5', 'G5', 'E5', 'D5', 'B4', 'D5'],
       'Em7': ['G4', 'B4', 'D5', 'E5', 'D5', 'B4', 'G4', 'B4'], 'Am7': ['A4', 'C5', 'E5', 'G5', 'E5', 'C5', 'A4', 'E5'],
       'G': ['B4', 'D5', 'G5', 'B5', 'G5', 'D5', 'B4', 'D5']}
for (t0, c) in PROG:
    if not (6 <= t0 < 24): continue
    span = 1.0 if t0 >= 22 else 2.0
    up = 12 if t0 >= 14 else 0
    for k in range(int(span / 0.125)):
        nn = ARP[c][k % 8]
        vel = [1, .55, .75, .55, .9, .55, .75, .6][k % 8]
        add(plk, pluck(midi(m(nn) + up), 0.5, 1.0, 1.0), t0 + k * 0.125, 0.15 * vel, pan=(-0.35 if k % 2 else 0.35))

# 베이스 (8분음표, 6 – 24초)
for i, (t0, c) in enumerate(PROG):
    if not (6 <= t0 < 24): continue
    t1 = PROG[i + 1][0]
    root = midi(m(CH[c][0]) + 12)
    k = 0
    while t0 + k * 0.25 < t1 - 1e-6:
        oct_ = 2 if k % 4 == 3 else 1
        add(bassb, bass_note(root * oct_, 0.2), t0 + k * 0.25, 0.42)
        k += 1

# 드럼 (6 – 23.5초)
kicks = []
t = 6.0
while t < 22.0 - 1e-6:
    b = round((t - 6.0) / BEAT) % 8         # 두 마디(8박) 패턴
    if b in (0, 4): kicks.append(t)
    if b in (2, 6): add(drums, clap(), t, 0.55, pan=0.05)
    t += BEAT
for t0 in np.arange(6.0, 22.0, BAR):
    kicks += [t0 + 1.75]
for t0 in np.arange(6.0, 22.0, 0.25):
    k = round((t0 - 6.0) / 0.25)
    if t0 >= 14.0 and k % 2 == 1: add(drums, hat(True), t0, 0.2, pan=0.25)
    else: add(drums, hat(False), t0, 0.38 if k % 2 else 0.2, pan=0.25 if k % 2 else -0.2)
# 22초: 쌓기 (스네어 연타 → 24초)
for i, t0 in enumerate(np.arange(22.0, 24.0, 0.125)):
    add(drums, clap(), t0, 0.12 + 0.38 * (i / 16) ** 1.6, pan=0.05)
kicks += [22.0, 22.5, 23.0]
for t0 in kicks: add(drums, kick(), t0, 0.95)
add(drums, kick(1.2), 24.0, 1.0)

# 덕킹(킥이 칠 때 패드·베이스를 살짝 눌러 숨 쉬게)
duck = np.ones(N)
for t0 in kicks + [24.0]:
    i = int(t0 * SR); n = int(0.32 * SR); tt = np.arange(n) / SR
    g = 1 - 0.45 * np.exp(-tt * 9)
    duck[i:i + n] = np.minimum(duck[i:i + n], g[: max(0, min(n, N - i))])
pads *= duck; bassb *= duck

# 로고 마무리: 종소리 화음 + 낮은 울림
for k, nn in enumerate(['C5', 'G5', 'E6', 'B5', 'D6']):
    add(bells, bell(midi(m(nn)), 3.2, 1.6), 24.0 + k * 0.07, 0.16, pan=(-0.4 + 0.2 * k))
sub = np.sin(2 * np.pi * 43 * np.arange(int(2.4 * SR)) / SR) * np.exp(-np.arange(int(2.4 * SR)) / SR * 1.8)
add(music, sub, 24.0, 0.5)

# 드롭 전 빨아들이는 소리 · 드롭 순간
add(music, noise_sweep(1.5, 300, 7000, 0.7), 4.5, 0.22, pan=0)
add(music, noise_sweep(1.6, 400, 9000, 0.7), 22.4, 0.24, pan=0)
imp_n = int(1.6 * SR); it = np.arange(imp_n) / SR
impact = np.sin(2 * np.pi * (40 + 60 * np.exp(-it * 18)) * it) * np.exp(-it * 2.6) + lp(rng.standard_normal(imp_n), 1800) * np.exp(-it * 9) * 0.3
add(music, impact, 6.0, 0.55)
add(bells, bell(midi(m('E6')), 2.0, 1.2), 6.0, 0.12, pan=-0.2)
add(bells, bell(midi(m('G6')), 2.0, 1.2), 6.12, 0.1, pan=0.2)

plk = delay_pp(plk)
music += reverb(pads, IR, 0.35) + reverb(plk, IR, 0.32) + reverb(bells, IR_BIG, 0.45) + drums + reverb(drums * 0.25, IR, 0.5) * 0.4 + bassb
music = lp(hp(music, 30), 16000)

# 도입부는 조금 어둡고 조용하게 → 6초에 열림
g = np.ones(N); t = np.arange(N) / SR
g = np.where(t < 6.0, 1.25 + 0.2 * np.clip((t - 4.3) / 1.7, 0, 1), 1.0)
g = np.where((t > 5.80) & (t < 6.0), g * (1 - 0.7 * np.clip((t - 5.80) / 0.12, 0, 1)), g)    # 드롭 직전 숨 고르기
g = np.where(t > 26.7, g * np.clip(1 - (t - 26.7) / 1.5, 0, 1) ** 1.5, g)                     # 끝 정리
music *= g

# ── 효과음 ──────────────────────────────────────
sfx = buf()
PENTA = [m(x) for x in ['C6', 'D6', 'E6', 'G6', 'A6', 'C7']]
for e in ev['events']:
    t0, ty = e['t'], e['type']
    if ty == 'key':
        n = int(0.05 * SR); tt = np.arange(n) / SR
        s = bp(rng.standard_normal(n), 1800, 6000) * np.exp(-tt * 180) + np.sin(2 * np.pi * rng.uniform(170, 230) * tt) * np.exp(-tt * 120) * 0.6
        add(sfx, s, t0, rng.uniform(0.05, 0.08), pan=rng.uniform(-.25, .25))
    elif ty == 'tick':
        n = int(0.02 * SR); tt = np.arange(n) / SR
        add(sfx, hp(rng.standard_normal(n), 4000) * np.exp(-tt * 300), t0, 0.03, pan=0.1)
    elif ty == 'tap':
        n = int(0.09 * SR); tt = np.arange(n) / SR
        f = 1500 * np.exp(-tt * 18) + 700
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 45) + hp(rng.standard_normal(n), 3000) * np.exp(-tt * 500) * 0.4
        add(sfx, s, t0, 0.2, pan=0.15)
    elif ty == 'pop':
        f0 = midi(PENTA[e.get('n', 0) % len(PENTA)] - 12)
        n = int(0.18 * SR); tt = np.arange(n) / SR
        f = f0 * (1 + 0.6 * np.exp(-tt * 70))
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 22) * np.minimum(1, tt / 0.002)
        add(sfx, s, t0, 0.14, pan=rng.uniform(-.3, .3))
    elif ty == 'thread':
        d = e.get('d', 0.45)
        s = noise_sweep(d + 0.1, 900, 6000, 0.5) * 0.6
        tt = np.arange(len(s)) / SR
        s += np.sin(2 * np.pi * np.cumsum(500 + 700 * tt / (d + 0.1)) / SR) * np.exp(-tt * 3) * 0.15 * np.minimum(1, tt / 0.03)
        add(sfx, s, t0, 0.22, pan=0)
    elif ty in ('whoosh', 'swoosh', 'swish', 'whooshIn', 'swipe'):
        d = {'whoosh': 0.55, 'swoosh': 0.5, 'swish': 0.38, 'whooshIn': 0.9, 'swipe': 0.38}[ty]
        a, b = {'whoosh': (2500, 500), 'swoosh': (600, 3500), 'swish': (3000, 900), 'whooshIn': (300, 4000), 'swipe': (500, 3200)}[ty]
        s = noise_sweep(d, a, b, 0.9, rise=False)
        tt = np.arange(len(s)) / SR
        s = s * np.sin(np.pi * np.clip(tt / d, 0, 1)) ** 0.8
        pans = np.linspace(-0.6, 0.6, 2)
        st = np.stack([s * np.linspace(1.2, 0.5, len(s)), s * np.linspace(0.5, 1.2, len(s))]) if ty in ('swoosh', 'whooshIn') else s
        add(sfx, st, t0 - 0.05, {'whoosh': 0.32, 'swoosh': 0.3, 'swish': 0.22, 'whooshIn': 0.26, 'swipe': 0.24}[ty])
    elif ty == 'scan':
        s = noise_sweep(0.5, 3000, 9000, 0.4, rise=False) * 0.7
        add(sfx, s, t0, 0.12, pan=-0.1)
    elif ty == 'answer':
        for k, nn in enumerate(['G5', 'C6', 'E6', 'G6']):
            add(sfx, bell(midi(m(nn)), 1.6, 1.4), t0 + k * 0.055, 0.13, pan=-0.3 + 0.2 * k)
    elif ty == 'answer2':
        for k, nn in enumerate(['E6', 'A6']):
            add(sfx, bell(midi(m(nn)), 1.2, 1.2), t0 + k * 0.07, 0.1, pan=0.2)
    elif ty == 'send':
        n = int(0.14 * SR); tt = np.arange(n) / SR
        f = 650 + 900 * (tt / 0.14)
        add(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14) * np.minimum(1, tt / 0.004), t0, 0.16, pan=0.2)
    elif ty == 'msg':
        for k, nn in enumerate(['A5', 'E6']):
            add(sfx, bell(midi(m(nn)), 1.0, 0.9, 2.0), t0 + k * 0.09, 0.1, pan=-0.15)
    elif ty in ('word', 'word2'):
        n = int(0.12 * SR); tt = np.arange(n) / SR
        add(sfx, lp(rng.standard_normal(n), 1400) * np.exp(-tt * 40) * 0.6, t0, 0.05 if ty == 'word' else 0.07)
sfx = reverb(sfx, IR, 0.18)

# ── 마스터 ──────────────────────────────────────
def k_weight(x):   # ITU-R BS.1770 K-가중 근사(고역 선반 + 고역 통과)
    from scipy.signal import lfilter
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=-1), axis=-1)


def lufs(x):
    y = k_weight(x); blk = int(0.4 * SR); hop = int(0.1 * SR)
    ms = [(y[:, i:i + blk] ** 2).mean(axis=1).sum() for i in range(0, y.shape[1] - blk, hop)]
    ms = np.array(ms); l = -0.691 + 10 * np.log10(ms + 1e-12)
    g1 = ms[l > -70]; lg = -0.691 + 10 * np.log10(g1.mean())
    g2 = g1[(-0.691 + 10 * np.log10(g1 + 1e-12)) > lg - 10]
    return -0.691 + 10 * np.log10(g2.mean())


def master(x, target=-15.0):
    x = x * 10 ** ((target - lufs(x)) / 20)
    x = np.tanh(x * 1.15) / 1.15          # 부드러운 제한
    pk = np.abs(x).max()
    if pk > 0.89: x *= 0.89 / pk          # 최대 약 -1 dBFS
    return x, lufs(x)


def write(p, x):
    from scipy.io import wavfile
    wavfile.write(str(p), SR, (np.clip(x, -1, 1).T * 32767).astype(np.int16))


mix = music * 1.0 + sfx * 1.0
mix, L = master(mix)
write(OUT / 'bgm.wav', mix)
mm, Lm = master(music.copy(), -16.0); write(OUT / 'bgm_music.wav', mm)
ss, Ls = master(sfx.copy(), -20.0); write(OUT / 'bgm_sfx.wav', ss)
print(f'bgm.wav {DUR:.1f}s  {L:.1f} LUFS  peak {20*np.log10(np.abs(mix).max()):.1f} dBFS | music {Lm:.1f} | sfx {Ls:.1f}')
