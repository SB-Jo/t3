"""Weave 인트로 v3 배경음악·효과음 — 실제 악기 녹음 샘플로 연주 (48kHz 스테레오)

사용: ~/.cache/weave-tools/venv/bin/python tools/music.py  →  out/bgm.wav (음악+효과음), out/bgm_music.wav, out/bgm_sfx.wav
- 샘플: VSCO 2 Community Edition (Versilian Studios, CC0 1.0 퍼블릭 도메인), ~/.cache/weave-tools/samples/vsco2
  업라이트 피아노(Simon Dalzell / Ivy Audio), 콘트라베이스 피치카토, 하프, 글로켄슈필, 마림바, 탬버린·콩가·스네어 탭·베이스드럼
- 100 BPM(한 박 0.6초, 한 마디 2.4초), 다장조. Fmaj – G – Em7 – Am7 반복, 38.4초(17마디째)에 Cmaj9로 마무리.
- v2의 합성 로즈·쉭쉭거리는 바람 효과음은 빼고, 연결·정답 순간은 하프·글로켄 같은 실제 악기 소리로.
"""
import json, re
from fractions import Fraction
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve, lfilter, resample_poly
import warnings; warnings.filterwarnings('ignore')

SR = 48000
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out'
SMP = Path.home() / '.cache/weave-tools/samples/vsco2'
EVJ = json.loads((OUT / 'events.json').read_text())
DUR = float(EVJ['duration']) + 0.6
N = int(DUR * SR)
rng = np.random.default_rng(20261029)
BEAT = 0.6; BAR = 2.4; STEP = BEAT / 4; SWING = 0.012
PCS = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def lp(x, f, order=2): return sosfilt(butter(order, f / (SR / 2), 'low', output='sos'), x, axis=-1)
def hp(x, f, order=2): return sosfilt(butter(order, f / (SR / 2), 'high', output='sos'), x, axis=-1)


def buf(): return np.zeros((2, N), np.float32)


def add(dst, sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= N: return
    if pan:
        l = np.cos((pan + 1) * np.pi / 4) * 1.414; r = np.sin((pan + 1) * np.pi / 4) * 1.414
        sig = sig * np.array([[l], [r]], np.float32)
    if i < 0: sig = sig[:, -i:]; i = 0
    k = min(N - i, sig.shape[1])
    dst[:, i:i + k] += gain * sig[:, :k]


_raw = {}
def load(p):
    if p not in _raw:
        sr, x = wavfile.read(p)
        scale = 2 ** 31 if x.dtype == np.int32 else (2 ** 15 if x.dtype == np.int16 else 1.0)
        x = x.astype(np.float32) / scale
        if x.ndim == 1: x = np.stack([x, x], 1)
        _raw[p] = (sr, x.T.copy())
    return _raw[p]


_cache = {}
def play(p, semis=0.0, maxlen=6.0):
    key = (p, round(semis, 3), maxlen)
    if key not in _cache:
        sr, x = load(p)
        x = x[:, : int(maxlen * sr)]
        fac = Fraction(SR / sr / (2 ** (semis / 12))).limit_denominator(1500)
        _cache[key] = resample_poly(x, fac.numerator, fac.denominator, axis=1).astype(np.float32)
    return _cache[key]


def env_cut(y, dur, rel=0.3):
    n = y.shape[1]; i = int(dur * SR); r = int(rel * SR)
    if i >= n: return y
    out = y[:, : min(n, i + r)].copy()
    k = out.shape[1] - i
    if k > 0: out[:, i:] *= np.linspace(1, 0, k, dtype=np.float32) ** 1.5
    return out


# ── 악기 표 (이름의 옥타브 표기가 악기마다 달라 실제 음높이를 재서 맞춤) ──
PIANO = {1: {}, 2: {}}
for f in SMP.glob('piano/Player_dyn*_rr1_*.wav'):
    m = re.search(r'dyn(\d)_rr1_(\d+)', f.name); d, idx = int(m.group(1)), int(m.group(2))
    PIANO[d][21 + 2 * idx] = str(f)
def table(glob, rx, octoff):
    t = {}
    for f in sorted(SMP.glob(glob)):
        m = re.search(rx, f.name)
        if m: t.setdefault(PCS[m.group(1)] + 12 * (int(m.group(2)) + octoff), str(f))
    return t
PIZZ = table('pizz/*_v1_rr1.wav', r'Pizz_([A-G]#?)(\d)_', 2)
HARP = table('harp/*.wav', r'KSHarp_([A-G]#?)(\d)_', 1)
GLOCK = table('glock/*.wav', r'medium_([A-G]#?)(\d)', 2)
MARIMBA = table('marimba/*.wav', r'Outrigger_([A-G]#?)(\d)_', 2)
PERC = {k: str(SMP / 'perc' / f'{k}.wav') for k in ['Tamb1-Shake_v1_rr1_Sum', 'Tamb1-Shake_v1_rr2_Sum', 'Snare2-taps_v2_rr1_Sum', 'Snare2-taps_v2_rr2_Sum',
        'Conga-Tap1_v1_rr1_Sum', 'Conga-Tap1_v1_rr2_Sum', 'BDrumNewhit_v1_rr1_Sum', 'BDrumNewhit_v2_rr1_Sum']}


def nearest(tab, n):
    k = min(tab, key=lambda m: (abs(m - n), m))
    return tab[k], n - k


def piano(n, dur, vel):
    layer = 2 if vel > 0.62 else 1
    p, s = nearest(PIANO[layer], n)
    y = env_cut(play(p, s, min(8.0, dur + 1.2)), dur, 0.42)
    return y * (vel ** 1.1) * (4.0 if layer == 1 else 1.0)


def inst(tab, n, dur, maxlen=4.0, rel=0.25):
    p, s = nearest(tab, n)
    return env_cut(play(p, s, maxlen), dur, rel)


# ── 곡 ──────────────────────────────────────────
V = {'F': (41, [53, 57, 60, 64]), 'G': (43, [55, 59, 62, 67]), 'Em': (40, [52, 55, 59, 62]), 'Am': (45, [57, 60, 64, 67]), 'C': (36, [48, 55, 59, 62, 64])}
LOOP = ['F', 'G', 'Em', 'Am']
CH = [(b * BAR, BAR, LOOP[b % 4]) for b in range(14)]
CH += [(14 * BAR, BAR / 2, 'Em'), (14.5 * BAR, BAR / 2, 'Am'), (15 * BAR, BAR / 2, 'F'), (15.5 * BAR, BAR / 2, 'G'), (16 * BAR, DUR - 16 * BAR, 'C')]
END = 16 * BAR                                      # 38.4초: 로고
st = lambda k: k * STEP + (SWING if k % 2 else 0) + rng.normal(0, 0.003)

pn = buf(); bs = buf(); dr = buf(); hpb = buf(); gl = buf()

# 피아노: 처음 두 마디는 펼친 화음, 그다음 잔잔한 리듬 반주
for (t0, d, name) in CH:
    notes = V[name][1]
    if t0 >= END:
        for j, n_ in enumerate(notes):
            add(pn, piano(n_, 3.2, 0.6), t0 + 0.035 * j, 0.5, pan=-0.2 + 0.1 * j)
        continue
    b = int(round(t0 / BAR))
    if b < 2:
        for j, k in enumerate([0, 2, 4, 6, 8, 10, 12, 14]):
            n_ = notes[[0, 1, 2, 3, 2, 1, 2, 3][j]] + (12 if j in (3, 7) else 0)
            add(pn, piano(n_, 0.9, 0.5 + 0.08 * (j % 3)), t0 + st(k), 0.7, pan=-0.15 + 0.05 * (j % 4))
        continue
    nb = int(round(d / STEP))
    pat = [(0, 3, 0.72), (3, 3, 0.48), (6, 2, 0.56), (8, 3, 0.68), (11, 3, 0.48), (14, 2, 0.52)] if nb >= 16 else [(0, 3, 0.68), (3, 3, 0.48), (6, 2, 0.5)]
    if b < 4: pat = [p for p in pat if p[0] in (0, 6, 8, 14)]
    for (k, ln, vel) in pat:
        for j, n_ in enumerate(notes):
            add(pn, piano(n_, ln * STEP * 1.05, vel * rng.uniform(0.92, 1.06)), t0 + st(k) + 0.006 * j, 0.42, pan=-0.2 + 0.12 * j)

# 피아노 선율 (위 음역: 도입, 와인 끝~통화, 카톡)
MOTIF = {'F': [(0, 4, 76), (6, 2, 74), (8, 8, 72)], 'G': [(0, 6, 74), (6, 10, 71)], 'Em': [(0, 2, 67), (2, 2, 71), (4, 4, 74), (8, 8, 76)], 'Am': [(0, 12, 72)]}
for (t0, d, name) in CH:
    b = int(round(t0 / BAR))
    if name not in MOTIF or d < BAR or not (b < 4 or b >= 8): continue
    for (k, ln, n_) in MOTIF[name]:
        add(pn, piano(n_, ln * STEP, 0.66 if b >= 4 else 0.58), t0 + st(k), 0.55, pan=0.1)

# 피치카토 베이스 (4.8초부터)
for i, (t0, d, name) in enumerate(CH):
    if t0 < 2 * BAR: continue
    root = V[name][0]; nxt = V[CH[i + 1][2]][0] if i + 1 < len(CH) else root
    if t0 >= END:
        add(bs, inst(PIZZ, root, 2.0, 3.0, 0.6), t0, 1.0); continue
    nb = int(round(d / STEP))
    pat = [(0, 5, root), (6, 2, root + 7), (8, 4, root), (14, 2, nxt)] if nb >= 16 else [(0, 5, root), (6, 2, root + 7)]
    if t0 < 4 * BAR: pat = [p for p in pat if p[0] in (0, 8)]
    for (k, ln, n_) in pat:
        add(bs, inst(PIZZ, n_, ln * STEP * 1.1, 1.8, 0.12), t0 + st(k), 1.4 if k == 0 else 1.12)

# 타악: 4.8초 탬버린, 9.6초 베이스드럼·스네어 탭, 19.2초 콩가
for b in range(2, 16):
    t0 = b * BAR
    for k in (2, 6, 10, 14):                       # 탬버린은 엇박에만, 작게
        add(dr, play(PERC['Tamb1-Shake_v1_rr1_Sum' if k % 8 == 2 else 'Tamb1-Shake_v1_rr2_Sum'], 0, 0.6), t0 + st(k), 0.36 * (0.7 if b < 4 else 1.0), pan=0.35)
    if b < 4: continue
    for k, v in ((0, 1.0), (8, 0.8)) + (((10, 0.45),) if b % 2 else ()):
        add(dr, lp(env_cut(play(PERC['BDrumNewhit_v1_rr1_Sum'], 0, 1.0), 0.32, 0.12), 220, 2), t0 + st(k), 3.2 * v)
    for k in (4, 12):
        add(dr, play(PERC['Snare2-taps_v2_rr1_Sum' if k == 4 else 'Snare2-taps_v2_rr2_Sum'], 0, 0.8), t0 + st(k), 1.15, pan=-0.05)
    if b >= 8:
        for k in (3, 7, 11, 15):
            add(dr, play(PERC['Conga-Tap1_v1_rr1_Sum' if k % 8 == 3 else 'Conga-Tap1_v1_rr2_Sum'], 0, 0.5), t0 + st(k), 0.7, pan=-0.35)
add(dr, lp(env_cut(play(PERC['BDrumNewhit_v2_rr1_Sum'], 0, 2.0), 1.4, 0.6), 260, 2), END, 2.2)

# 하프: 장면이 열릴 때 올라가는 글리산도, 로고에서 크게
def harp_gliss(t0, lo=60, steps=12, dt=0.045, vel=1.0):
    scale = [0, 2, 4, 7, 9]
    for i in range(steps):
        n_ = lo + 12 * (i // 5) + scale[i % 5]
        add(hpb, inst(HARP, n_, 1.6, 2.4, 0.5), t0 + i * dt, 0.9 * vel * (0.7 + 0.3 * i / steps), pan=-0.3 + 0.6 * i / steps)
for t0, lo, s_, v in [(9.45, 60, 10, 0.7), (21.5, 64, 8, 0.6), (28.7, 64, 8, 0.6), (END - 0.5, 55, 15, 1.0)]:
    harp_gliss(t0, lo, s_, 0.045, v)

# 글로켄: 로고 반짝임
for k, n_ in enumerate([84, 88, 91]):
    add(gl, inst(GLOCK, n_, 2.5, 3.5, 1.0), END + 0.25 + k * 0.09, 0.9, pan=-0.2 + 0.2 * k)

# ── 효과음: 실제 악기 소리로, 작게 (쉭쉭 바람 소리 없음) ──
sfx = buf()
def chord_at(t): return next((V[name][1] for (t0, d, name) in CH if t0 <= t < t0 + d), V['C'][1])
for e in EVJ['events']:
    t0, ty = e['t'], e['type']
    if ty == 'key':
        n = int(0.035 * SR); tt = np.arange(n) / SR
        s = (hp(rng.standard_normal(n), 1800) * np.exp(-tt * 230) * 0.5).astype(np.float32)
        add(sfx, np.stack([s, s]), t0, rng.uniform(0.025, 0.035), pan=rng.uniform(-.2, .2))
    elif ty == 'tick':
        n = int(0.015 * SR); tt = np.arange(n) / SR
        s = (hp(rng.standard_normal(n), 3500) * np.exp(-tt * 320)).astype(np.float32)
        add(sfx, np.stack([s, s]), t0, 0.012)
    elif ty == 'tap':
        add(sfx, inst(MARIMBA, 84, 0.12, 0.6, 0.1), t0, 0.35, pan=0.1)
    elif ty in ('card', 'thread', 'link'):
        ch = chord_at(t0); n_ = ch[int(rng.integers(0, len(ch)))] + 12
        add(sfx, inst(HARP, n_, 1.0, 1.8, 0.4), t0, {'card': 0.55, 'thread': 0.4, 'link': 0.45}[ty], pan=float(rng.uniform(-.25, .25)))
        if ty == 'link':
            add(sfx, inst(HARP, n_ + 4, 1.0, 1.8, 0.4), t0 + 0.12, 0.35)
            add(sfx, inst(HARP, n_ + 7, 1.0, 1.8, 0.4), t0 + 0.24, 0.3)
    elif ty == 'answer':
        add(sfx, inst(GLOCK, 79, 1.8, 2.5, 0.8), t0, 0.7, pan=-0.1)
        add(sfx, inst(GLOCK, 84, 1.8, 2.5, 0.8), t0 + 0.08, 0.6, pan=0.1)
    elif ty == 'msg':
        add(sfx, inst(MARIMBA, 76, 0.8, 1.2, 0.3), t0, 0.5, pan=-0.1)
        add(sfx, inst(MARIMBA, 81, 0.8, 1.2, 0.3), t0 + 0.1, 0.45, pan=-0.1)
    elif ty == 'send':
        add(sfx, inst(MARIMBA, 79, 0.4, 1.0, 0.2), t0, 0.35, pan=0.15)
    elif ty == 'hl':
        add(sfx, inst(MARIMBA, [72, 74, 76, 79][e.get('n', 0) % 4], 0.6, 1.0, 0.3), t0, 0.28, pan=-0.2 + 0.13 * e.get('n', 0))


# ── 믹스·마스터 ─────────────────────────────────
def make_ir(rt=1.6, pre=0.015, damp=4200, seed=1):
    r = np.random.default_rng(seed); n = int(rt * SR); t = np.arange(n) / SR
    ir = r.standard_normal((2, n)) * np.exp(-6.9 * t / rt); ir = lp(ir, damp, 1); ir[:, : int(pre * SR)] = 0
    return ir / np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
ROOM, HALL = make_ir(1.2, 0.012, 5000, 2), make_ir(2.4, 0.022, 4500, 3)
def verb(x, ir, wet): return x + np.stack([fftconvolve(x[0], ir[0])[:N], fftconvolve(x[1], ir[1])[:N]]) * wet

music = verb(pn, ROOM, 0.32) + verb(bs, ROOM, 0.12) + verb(dr, ROOM, 0.2) + verb(hpb, HALL, 0.45) + verb(gl, HALL, 0.5)
music = hp(music, 30)
t = np.arange(N) / SR
music *= np.clip(t / 0.05, 0, 1) * np.where(t > DUR - 2.4, np.clip((DUR - 0.4 - t) / 2.0, 0, 1) ** 1.5, 1.0)
sfx = verb(sfx, ROOM, 0.25)


def k_weight(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=-1), axis=-1)
def lufs(x):
    y = k_weight(x); blk = int(0.4 * SR); hop = int(0.1 * SR)
    ms = np.array([(y[:, i:i + blk] ** 2).mean(axis=1).sum() for i in range(0, y.shape[1] - blk, hop)])
    l = -0.691 + 10 * np.log10(ms + 1e-12); g1 = ms[l > -70]; lg = -0.691 + 10 * np.log10(g1.mean())
    return -0.691 + 10 * np.log10(g1[(-0.691 + 10 * np.log10(g1 + 1e-12)) > lg - 10].mean())
def comp(x, thr=-20.0, ratio=2.2, att=0.01, rel=0.2):
    lvl = np.sqrt(lp((x ** 2).mean(axis=0), 30, 1).clip(1e-12)); db = 20 * np.log10(lvl)
    gr = -np.maximum(0, db - thr) * (1 - 1 / ratio); sm = np.zeros_like(gr); a = np.exp(-1 / (att * SR)); r = np.exp(-1 / (rel * SR)); prev = 0.0
    for i in range(0, len(gr), 64):
        g_ = gr[i:i + 64].min(); c = a if g_ < prev else r; prev = c * prev + (1 - c) * g_; sm[i:i + 64] = prev
    return x * 10 ** (sm / 20)
def master(x, target):
    x = comp(x); x = x * 10 ** ((target - lufs(x)) / 20); x = np.tanh(x * 1.05) / 1.05
    pk = np.abs(x).max()
    if pk > 0.84: x *= 0.84 / pk
    return x, lufs(x)
def write(p, x): wavfile.write(str(p), SR, (np.clip(x, -1, 1).T * 32767).astype(np.int16))

mix, L = master(music + sfx, -15.5); write(OUT / 'bgm.wav', mix)
mm, Lm = master(music.copy(), -16.0); write(OUT / 'bgm_music.wav', mm)
ss, Ls = master(sfx.copy(), -22.0); write(OUT / 'bgm_sfx.wav', ss)
print(f'bgm.wav {DUR:.1f}s  {L:.1f} LUFS  peak {20*np.log10(np.abs(mix).max()):.1f} dBFS | music {Lm:.1f} | sfx {Ls:.1f}')
print('samples', {k: len(v) for k, v in [('piano1', PIANO[1]), ('piano2', PIANO[2]), ('pizz', PIZZ), ('harp', HARP), ('glock', GLOCK), ('marimba', MARIMBA)]})
