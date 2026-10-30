"""Weave 인트로 v2 배경음악·효과음 합성 (직접 합성, 48kHz 스테레오)

사용: ~/.cache/weave-tools/venv/bin/python tools/music.py  →  out/bgm.wav (음악+효과음), out/bgm_music.wav, out/bgm_sfx.wav
- 참고: Rewind 'iPhone in 30 seconds' 광고 음악 분석(약 114 BPM·다장조, 저음이 두툼하고 고음 반짝임이 거의 없음,
  처음부터 끝까지 고른 그루브). 그래서 '톡톡 튀는' 플럭·하이햇 대신 로즈 피아노 코드, 둥근 베이스, 부드러운 킥·림·셰이커로.
- 100 BPM(한 박 0.6초, 한 마디 2.4초), 다장조. Fmaj9 – Em7 – Dm9 – G13 반복, 36초(16마디째)에 Cmaj9로 마무리.
- 효과음은 out/events.json(render.cjs --events) 시점에 맞춰 작고 따뜻하게.
"""
import json
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve, lfilter

SR = 48000
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out'
EVJ = json.loads((OUT / 'events.json').read_text())
DUR = float(EVJ['duration']) + 0.4
N = int(DUR * SR)
rng = np.random.default_rng(20261029)
BEAT = 0.6; BAR = 2.4; STEP = BEAT / 4; SWING = 0.022


def midi(n): return 440.0 * 2 ** ((n - 69) / 12)


def buf(): return np.zeros((2, N), np.float32)


def add(dst, sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= N or i + (sig.shape[-1]) <= 0: return
    if sig.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l * 1.414, sig * r * 1.414])
    if i < 0: sig = sig[:, -i:]; i = 0
    k = min(N - i, sig.shape[1])
    dst[:, i:i + k] += gain * sig[:, :k]


def lp(x, f, order=2): return sosfilt(butter(order, f / (SR / 2), 'low', output='sos'), x, axis=-1)
def hp(x, f, order=2): return sosfilt(butter(order, f / (SR / 2), 'high', output='sos'), x, axis=-1)
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos'), x, axis=-1)


def make_ir(rt=1.6, pre=0.015, damp=4200, seed=1):
    r = np.random.default_rng(seed)
    n = int(rt * SR); t = np.arange(n) / SR
    ir = r.standard_normal((2, n)) * np.exp(-6.9 * t / rt)
    ir = lp(ir, damp, 1); ir[:, : int(pre * SR)] = 0
    return ir / np.sqrt((ir ** 2).sum(axis=1, keepdims=True))


IR_ROOM = make_ir(1.1, 0.012, 3800, 2)
IR_HALL = make_ir(2.4, 0.025, 3600, 3)


def reverb(x, ir, wet):
    y = np.stack([fftconvolve(x[0], ir[0])[:N], fftconvolve(x[1], ir[1])[:N]])
    return x + y * wet


# ── 악기 ────────────────────────────────────────
def rhodes(f, dur, vel=1.0):
    """FM 로즈 피아노: 1:1 변조(따뜻한 몸통) + 14배 변조(살짝 짖는 소리)를 짧게."""
    n = int((dur + 1.4) * SR); t = np.arange(n) / SR
    decay = 1.6 + 1.2 * (220 / f)
    env = np.exp(-t / decay) * np.minimum(1, t / 0.003)
    off = t > dur
    env = np.where(off, env * np.exp(-(t - dur) / 0.18), env)
    I1 = (1.4 + 1.6 * vel) * np.exp(-t / 0.45) + 0.25
    body = np.sin(2 * np.pi * f * t + I1 * np.sin(2 * np.pi * f * t))
    I2 = 0.9 * vel * np.exp(-t / 0.035)
    tine = np.sin(2 * np.pi * f * t + I2 * np.sin(2 * np.pi * f * 14 * t)) - np.sin(2 * np.pi * f * t)
    s = (body + 0.5 * tine) * env
    s = np.tanh(s * (0.9 + 0.5 * vel)) * 0.5
    return lp(s, 9000, 1)


def bass(f0, f1, dur, glide=0.06):
    n = int((dur + 0.15) * SR); t = np.arange(n) / SR
    f = np.where(t < glide, f0 + (f1 - f0) * (t / glide), f1) if f0 != f1 else np.full(n, f1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
    env = np.minimum(1, t / 0.01) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.04)) * (0.82 + 0.18 * np.exp(-t / 0.25))
    return lp(np.tanh(s * 1.3) * env * 0.55, 900, 2)


def pad(freqs, dur):
    n = int((dur + 1.0) * SR); t = np.arange(n) / SR
    out = np.zeros((2, n))
    for ch in (0, 1):
        for f in freqs:
            for dv in (-0.004, 0.004):
                ff = f * (1 + dv + (0.0015 if ch else -0.0015))
                w = sum(np.sin(2 * np.pi * ff * k * t + rng.uniform(0, 6.28)) / k * np.exp(-k / 5) for k in range(1, 9))
                out[ch] += w
    env = np.clip(t / 0.9, 0, 1) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.5))
    return lp(out * env / (len(freqs) * 3), 1500, 2)


def kick(v=1.0):
    n = int(0.38 * SR); t = np.arange(n) / SR
    f = 48 + 52 * np.exp(-t * 26)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8.0)
    s += lp(rng.standard_normal(n), 1200) * np.exp(-t * 180) * 0.12
    return np.tanh(s * 1.4) * 0.8 * v


def rim(v=1.0):
    n = int(0.22 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 38) * 0.5
    snap = bp(rng.standard_normal(n), 1500, 6500) * np.exp(-t * 48) * 1.3
    return (body + snap) * 0.45 * v


def shaker(v=1.0):
    n = int(0.08 * SR); t = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 3200, 8800, 2)
    env = np.minimum(1, t / 0.008) * np.exp(-t * 55)
    return s * env * 0.22 * v


def glass(f, dur):
    n = int((dur + 0.8) * SR); t = np.arange(n) / SR
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5.0 * t) * np.clip(t / 0.4, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    s = np.sin(ph) + 0.18 * np.sin(2 * ph)
    env = np.clip(t / 0.06, 0, 1) * np.where(t < dur, np.exp(-t / (dur * 2.5)), np.exp(-dur / (dur * 2.5)) * np.exp(-(t - dur) / 0.35))
    return s * env * 0.3


def swell(dur, lo=300, hi=2600):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); out = np.zeros(n); blk = 1024
    for i in range(0, n, blk):
        p = i / n; fc = lo * (hi / lo) ** p
        seg = x[max(0, i - 2048): i + blk]
        y = bp(seg, max(40, fc * 0.6), min(SR / 2 - 200, fc * 1.4), 1)
        out[i:i + blk] = y[-min(blk, n - i):]
    return out * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5


# ── 화음 진행 ─────────────────────────────────────
V = {'Fmaj9': (41, [57, 60, 64, 67]), 'Em7': (40, [55, 59, 62, 64]), 'Dm9': (38, [53, 57, 60, 64]),
     'G13s': (43, [53, 57, 60, 64]), 'G13': (43, [53, 57, 59, 64]), 'Cmaj9': (36, [52, 55, 59, 62, 64])}
LOOP = ['Fmaj9', 'Em7', 'Dm9', 'G13']
CH = []                                   # (시작, 길이, 이름)
for b in range(15):
    t0 = b * BAR; name = LOOP[b % 4]
    if name == 'G13':
        CH += [(t0, BAR / 2, 'G13s'), (t0 + BAR / 2, BAR / 2, 'G13')]
    elif b == 14:
        CH += [(t0, BAR / 2, 'Dm9'), (t0 + BAR / 2, BAR / 2, 'G13')]
    else:
        CH.append((t0, BAR, name))
CH.append((15 * BAR, DUR - 15 * BAR, 'Cmaj9'))
END = 15 * BAR                            # 36.0초: 로고

ep = buf(); bs = buf(); dr = buf(); pd = buf(); ld = buf(); fx = buf()
st = lambda k: k * STEP + (SWING if k % 2 else 0) + rng.normal(0, 0.004)

# 로즈 코드 (0초부터)
for (t0, d, name) in CH:
    notes = V[name][1]
    if t0 >= END:
        for j, n_ in enumerate(notes):
            add(ep, rhodes(midi(n_), 3.4, 0.55), t0 + j * 0.018, 0.2, pan=-0.25 + 0.12 * j)
        continue
    nb = int(round(d / STEP))
    hits = [(0, min(7, nb), 0.75), (7, 3, 0.45), (11, 4, 0.6)] if nb >= 16 else [(0, nb, 0.7)]
    for (k, ln, vel) in hits:
        if k >= nb: continue
        for j, n_ in enumerate(notes):
            add(ep, rhodes(midi(n_), ln * STEP * 0.95, vel * rng.uniform(0.9, 1.05)), t0 + st(k) + j * 0.007, 0.16, pan=-0.25 + 0.15 * j)

# 패드 (아주 낮게)
for (t0, d, name) in CH:
    add(pd, pad([midi(n_) for n_ in V[name][1]], d + 0.05), t0, 0.5)

# 베이스 (2.4초부터)
prev = None
for i, (t0, d, name) in enumerate(CH):
    if t0 < BAR: continue
    root = V[name][0]; nxt = V[CH[i + 1][2]][0] if i + 1 < len(CH) else root
    if t0 >= END:
        add(bs, bass(midi(root), midi(root), 3.0), t0, 0.5); continue
    nb = int(round(d / STEP))
    pat = [(0, 5, root), (7, 2, root + 7), (10, 3, root), (14, 2, nxt)] if nb >= 16 else [(0, nb - 1, root)]
    for (k, ln, n_) in pat:
        if k >= nb: continue
        f1 = midi(n_); f0 = midi(prev) if prev is not None else f1
        add(bs, bass(f0, f1, ln * STEP * 0.92, 0.05 if abs(n_ - (prev or n_)) <= 7 else 0.0), t0 + st(k), 0.5 if t0 >= 2 * BAR else 0.32)
        prev = n_

# 드럼: 2.4초 셰이커, 4.8초 킥·림, 36초에 멈춤
kicks = []
for b in range(1, 15):
    t0 = b * BAR
    for k in range(16):
        acc = 1.0 if k % 4 == 2 else (0.6 if k % 2 else 0.45)
        add(dr, shaker(acc * (0.75 if b < 3 else 1.0)), t0 + st(k), 1.05, pan=0.3)
    if b < 2: continue
    for k, v in ((0, 1.0), (7, 0.55), (10, 0.85)) + (((14, 0.4),) if b % 2 else ()):
        add(dr, kick(v), t0 + st(k), 0.9); kicks.append(t0 + st(k))
    for k in (4, 12):
        add(dr, rim(rng.uniform(0.85, 1.0)), t0 + st(k), 0.95, pan=-0.05)
add(dr, kick(0.9), END, 0.8); kicks.append(END)

# 숨쉬기(킥에 맞춰 베이스·패드 살짝 내림)
duck = np.ones(N)
for t0 in kicks:
    i = int(t0 * SR); n = int(0.3 * SR); tt = np.arange(n) / SR
    g = 1 - 0.28 * np.exp(-tt * 10)
    duck[i:i + n] = np.minimum(duck[i:i + n], g[: max(0, min(n, N - i))])
bs *= duck; pd *= duck

# 잔잔한 선율 (19.2초부터, 끝에서 해결)
MEL = [(19.2, 1.2, 76), (20.4, 1.2, 74), (21.6, 2.4, 71), (24.0, 1.2, 72), (25.2, 1.2, 69), (26.4, 2.4, 71),
       (28.8, 1.2, 76), (30.0, 1.2, 74), (31.2, 2.4, 71), (33.6, 1.2, 72), (34.8, 1.2, 74),
       (END, 0.6, 79), (END + 0.6, 0.6, 76), (END + 1.2, 2.0, 74)]
for (t0, d, n_) in MEL:
    add(ld, glass(midi(n_), d), t0 + 0.01, 0.13, pan=0.12)

# 넘어가는 자리의 부드러운 바람 소리
for t0 in (6.0, 18.4, 35.0):
    add(fx, swell(1.2, 250, 2200), t0, 0.1)

music = reverb(ep, IR_ROOM, 0.35) + reverb(ld, IR_HALL, 0.5) + bs + reverb(dr, IR_ROOM, 0.18) + reverb(pd, IR_HALL, 0.3) + reverb(fx, IR_HALL, 0.4)
music = lp(hp(music, 28), 12500, 2)
t = np.arange(N) / SR
g = np.clip(t / 0.35, 0, 1) * np.where(t > DUR - 2.6, np.clip((DUR - 0.3 - t) / 2.3, 0, 1) ** 1.6, 1.0)
music *= g

# ── 효과음 (작고 따뜻하게) ───────────────────────
sfx = buf()
for e in EVJ['events']:
    t0, ty = e['t'], e['type']
    if ty == 'key':
        n = int(0.04 * SR); tt = np.arange(n) / SR
        s = bp(rng.standard_normal(n), 1500, 5000) * np.exp(-tt * 200) * 0.6 + np.sin(2 * np.pi * rng.uniform(160, 210) * tt) * np.exp(-tt * 130) * 0.5
        add(sfx, s, t0, rng.uniform(0.035, 0.05), pan=rng.uniform(-.2, .2))
    elif ty == 'tick':
        n = int(0.02 * SR); tt = np.arange(n) / SR
        add(sfx, bp(rng.standard_normal(n), 2500, 7000) * np.exp(-tt * 260), t0, 0.018, pan=0.1)
    elif ty == 'tap':
        n = int(0.07 * SR); tt = np.arange(n) / SR
        f = 900 * np.exp(-tt * 25) + 520
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 55) + lp(rng.standard_normal(n), 3000) * np.exp(-tt * 400) * 0.2
        add(sfx, s, t0, 0.16, pan=0.1)
    elif ty in ('card', 'rise', 'pill'):
        n = int(0.4 * SR); tt = np.arange(n) / SR
        thud = np.sin(2 * np.pi * (150 + 60 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14) * 0.5
        air = swell(0.4, 600, 2400) * 0.6
        add(sfx, thud + air, t0 - 0.03, {'card': 0.14, 'rise': 0.12, 'pill': 0.12}[ty])
    elif ty == 'hl':
        add(sfx, rhodes(midi([72, 74, 76][e.get('n', 0) % 3]), 0.5, 0.5), t0, 0.16, pan=-0.1 + 0.1 * e.get('n', 0))
    elif ty == 'link':
        add(sfx, swell(e.get('d', 0.6) + 0.2, 900, 3000), t0, 0.1)
    elif ty == 'thread':
        d = e.get('d', 0.5)
        add(sfx, swell(d + 0.25, 700, 3600), t0, 0.16)
    elif ty in ('swish', 'swipe', 'fly', 'zoom'):
        d = {'swish': 0.55, 'swipe': 0.6, 'fly': 0.9, 'zoom': max(0.7, e.get('d', 1.0))}[ty]
        lo, hi = {'swish': (500, 2600), 'swipe': (400, 2400), 'fly': (300, 2200), 'zoom': (200, 900)}[ty]
        s = swell(d, lo, hi)
        st2 = np.stack([s * np.linspace(1.1, 0.6, len(s)), s * np.linspace(0.6, 1.1, len(s))]) if ty in ('fly', 'swish') else s
        add(sfx, st2, t0 - 0.05, {'swish': 0.16, 'swipe': 0.15, 'fly': 0.2, 'zoom': 0.09}[ty])
    elif ty == 'scan':
        add(sfx, hp(swell(0.6, 2500, 6000), 2000), t0, 0.08, pan=-0.1)
    elif ty == 'answer':
        for k, n_ in enumerate([79, 86]):
            add(sfx, rhodes(midi(n_), 1.2, 0.6), t0 + k * 0.06, 0.18, pan=-0.15 + 0.3 * k)
    elif ty == 'answer2':
        add(sfx, rhodes(midi(84), 1.0, 0.5), t0, 0.14, pan=0.15)
    elif ty == 'send':
        n = int(0.16 * SR); tt = np.arange(n) / SR
        f = 520 + 520 * (tt / 0.16)
        add(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 12) * np.minimum(1, tt / 0.005), t0, 0.1, pan=0.15)
    elif ty == 'msg':
        for k, n_ in enumerate([76, 81]):
            add(sfx, rhodes(midi(n_), 0.9, 0.5), t0 + k * 0.1, 0.15, pan=-0.1)
sfx = reverb(sfx, IR_ROOM, 0.22)


# ── 마스터 ──────────────────────────────────────
def k_weight(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=-1), axis=-1)


def lufs(x):
    y = k_weight(x); blk = int(0.4 * SR); hop = int(0.1 * SR)
    ms = np.array([(y[:, i:i + blk] ** 2).mean(axis=1).sum() for i in range(0, y.shape[1] - blk, hop)])
    l = -0.691 + 10 * np.log10(ms + 1e-12); g1 = ms[l > -70]; lg = -0.691 + 10 * np.log10(g1.mean())
    g2 = g1[(-0.691 + 10 * np.log10(g1 + 1e-12)) > lg - 10]
    return -0.691 + 10 * np.log10(g2.mean())


def comp(x, thr=-18.0, ratio=2.5, att=0.01, rel=0.18):
    lvl = np.sqrt(lp((x ** 2).mean(axis=0), 30, 1).clip(1e-12))
    db = 20 * np.log10(lvl); over = np.maximum(0, db - thr); gr = -over * (1 - 1 / ratio)
    sm = np.zeros_like(gr); a = np.exp(-1 / (att * SR)); r = np.exp(-1 / (rel * SR)); prev = 0.0
    for i in range(0, len(gr), 64):
        g_ = gr[i:i + 64].min(); c = a if g_ < prev else r; prev = c * prev + (1 - c) * g_; sm[i:i + 64] = prev
    return x * 10 ** (sm / 20)


def master(x, target):
    x = comp(x)
    x = x * 10 ** ((target - lufs(x)) / 20)
    x = np.tanh(x * 1.1) / 1.1
    pk = np.abs(x).max()
    if pk > 0.84: x *= 0.84 / pk
    return x, lufs(x)


def write(p, x):
    from scipy.io import wavfile
    wavfile.write(str(p), SR, (np.clip(x, -1, 1).T * 32767).astype(np.int16))


mix, L = master(music + sfx, -15.0); write(OUT / 'bgm.wav', mix)
mm, Lm = master(music.copy(), -15.5); write(OUT / 'bgm_music.wav', mm)
ss, Ls = master(sfx.copy(), -21.0); write(OUT / 'bgm_sfx.wav', ss)
print(f'bgm.wav {DUR:.1f}s  {L:.1f} LUFS  peak {20*np.log10(np.abs(mix).max()):.1f} dBFS | music {Lm:.1f} | sfx {Ls:.1f}')
