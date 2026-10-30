"""Weave 인트로 v5 배경음악 — 기존 곡(Mixkit, 무료 상업 이용 가능)을 영상에 맞춰 편집하고, 꼭 필요한 순간에만 작은 효과음을 얹는다 (48kHz 스테레오)

사용: ~/.cache/weave-tools/venv/bin/python tools/music.py            → out/bgm.wav(음악+효과음), out/bgm_music.wav, out/bgm_sfx.wav  (기본 곡)
      ~/.cache/weave-tools/venv/bin/python tools/music.py --all      → 위 + out/bgm_<곡번호>.wav (비교용 다른 곡들)
입력: out/events.json(효과음 시점, node tools/render.cjs --events), ~/.cache/weave-tools/music/<번호>.mp3

편집 원칙
- 곡을 새로 만들거나 리믹스하지 않는다. 마디 단위로만 잘라 붙여(템포·박자 그대로) 길이를 맞추고, 이음매는 40ms로 겹친다.
- 도입(질문 장면)은 조금 작고 먹먹하게 두었다가, 01 장면이 시작될 때 곡이 제대로 터지도록 연다.
- 로고(LOGO)는 곡의 마지막 한 방(기본 곡) 또는 마디 첫 박(다른 곡)에 맞춘다. 끝 화면이 하얗게 사라질 때 소리도 같이 사라진다.
- 효과음: 손으로 누를 때 작은 '톡', 글자 입력은 아주 작게, 정답 카드에 '딩', 03 Weave 버튼이 반짝일 때 아주 짧은 '띵', 답장에 '뽁'. 바람·탬버린 같은 소리는 넣지 않는다.
- v5: v4 곡(Digital Clouds)보다 밝은 장조 곡으로 바꿈. 기본은 'A Special Feeling', 비교용 'Uplift Me', 'Hollidays'.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sosfilt_zi, fftconvolve, lfilter

SR = 48000
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out'
LIB = Path.home() / '.cache/weave-tools/music'
FFMPEG = Path.home() / '.cache/weave-tools/bin/ffmpeg'
EVJ = json.loads((OUT / 'events.json').read_text())
DUR = float(EVJ['duration'])
N = int(round(DUR * SR))
LOGO = next(e['t'] for e in EVJ['events'] if e['type'] == 'logo')
D1 = 9.5                                                   # 01 장면에서 기본 곡이 터지는 순간(main.js의 D1)

# ── 곡 정보: 마디 길이(bar)와 첫 마디 시작(g0)은 박 검출로 잰 값. segs = [(영상 시작초, 그때 곡의 마디 번호), ...]
#    drop = 곡이 터지는 영상 시각, hit = 로고 자리가 곡의 마지막 한 방인지(아니면 로고에 작은 반짝임 효과음), hall = 마지막 한 방 뒤 울림 ──
TRACKS = {
    '1087': dict(name='A Special Feeling', artist='Michael Ramir C.', bpm=100.0, g0=0.0, key='C# 장조',
                 # 도입은 곡의 8~11마디(가볍게) → 9.5초에 12마디(킥·베이스가 들어옴), 19마디 끝에서 31마디로 건너뜀
                 # → 32마디(다시 들어옴)가 02의 위로 올리기에, 40마디(곡의 마지막 한 방)가 로고에
                 segs=lambda T: [(0.0, 12 - D1 / T['bar']), (D1 + 8 * T['bar'], 31)], drop=lambda T: D1, hit=True, hall=0.22),
    '35': dict(name='Uplift Me', artist='Ahjay Stelino', bpm=120.0, g0=0.25, key='D 장조',
               # 박 없는 도입 → 4마디에서 베이스·킥(로고 21마디 전), 7마디 끝에서 31마디(한 마디 빌드업)로 → 32마디부터 큰 후렴, 48마디(마지막 한 방)가 로고에
               segs=lambda T: [(0.0, 4 - (LOGO - 21 * T['bar']) / T['bar']), (LOGO - 17 * T['bar'], 31)], drop=lambda T: LOGO - 21 * T['bar'], hit=True, hall=0.0),
    '690': dict(name='Hollidays', artist='Grigoriy Nuzhny', bpm=108.0, g0=0.034, key='G 장조',
                # 기타만 나오는 도입(5~8마디) → 9마디에서 드럼·베이스(로고 19마디 전), 24마디 끝에서 30마디(쉬어 가는 구간 끝)로 → 33마디(다시 들어옴)가 로고에
                segs=lambda T: [(0.0, 9 - (LOGO - 19 * T['bar']) / T['bar']), (LOGO - 3 * T['bar'], 30)], drop=lambda T: LOGO - 19 * T['bar'], hit=False, hall=0.0),
}
MAIN = '1087'
for T in TRACKS.values():
    T['bar'] = 4 * 60.0 / T['bpm']


def lp(x, f, order=2): return sosfilt(butter(order, f / (SR / 2), 'low', output='sos'), x, axis=-1)
def hp(x, f, order=2): return sosfilt(butter(order, f / (SR / 2), 'high', output='sos'), x, axis=-1)
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos'), x, axis=-1)


def decode(path):
    raw = subprocess.run([str(FFMPEG), '-hide_banner', '-loglevel', 'error', '-i', str(path), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()


def smooth(a, b, x):                                       # 0→1 사이를 부드럽게(코사인)
    u = np.clip((x - a) / max(b - a, 1e-9), 0, 1)
    return 0.5 - 0.5 * np.cos(np.pi * u)


def edit(T):
    """마디 단위로 잘라 붙인 곡(2×N)과 이음매 목록"""
    src = decode(LIB / f"{T['id']}.mp3")
    bar, g0 = T['bar'], T['g0']
    segs = T['segs'](T)
    out = np.zeros((2, N), np.float32)
    XF = int(0.040 * SR)
    joins = []
    for i, (v0, b0) in enumerate(segs):
        v1 = segs[i + 1][0] if i + 1 < len(segs) else DUR
        off = g0 + b0 * bar - v0                            # 곡 시각 = 영상 시각 + off
        a, b = int(round(v0 * SR)), int(round(v1 * SR))
        a2, b2 = max(0, a - XF // 2), min(N, b + XF // 2)   # 이음매에서 겹칠 만큼 앞뒤로 조금 더
        idx = np.arange(a2, b2) + int(round(off * SR))
        ok = (idx >= 0) & (idx < src.shape[1])
        seg = np.zeros((2, b2 - a2), np.float32); seg[:, ok] = src[:, idx[ok]]
        w = np.ones(b2 - a2, np.float32)
        if i > 0: w[:XF] = np.sin(np.linspace(0, np.pi / 2, XF)) ** 2            # 들어올 때
        if i + 1 < len(segs): w[-XF:] = np.cos(np.linspace(0, np.pi / 2, XF)) ** 2  # 나갈 때
        out[:, a2:b2] += seg * w
        joins.append((round(v0, 3), round(off + v0, 3), round(b0, 3)))
    return out, joins


def hook_open(x, drop, bar):
    """도입부: 4dB 작고 고역을 누른 상태(1.6kHz) → 터지기 1.5마디 전부터 열려서 drop에 원래 소리"""
    t = np.arange(N) / SR
    o0, o1 = drop - 1.5 * bar, drop
    fc = 1600 * (18000 / 1600) ** smooth(o0, o1, t)
    y = np.zeros_like(x); blk = 256
    zi = None
    end = int(min(N, (drop + 0.05) * SR))
    for i in range(0, end, blk):
        sos = butter(2, min(fc[i], 20000) / (SR / 2), 'low', output='sos')
        if zi is None: zi = np.stack([sosfilt_zi(sos) * x[c, 0] for c in range(2)])
        for c in range(2):
            y[c, i:i + blk], zi[c] = sosfilt(sos, x[c, i:i + blk], zi=zi[c])
    wet = 1 - smooth(drop - 0.02, drop + 0.05, t)             # drop 직후엔 원래 소리로
    g = 10 ** (-4 * (1 - smooth(o0, o1, t)) / 20)
    return (y * wet + x * (1 - wet)) * g


def make_ir(rt=3.0, pre=0.02, damp=5000, seed=7):
    r = np.random.default_rng(seed); n = int(rt * SR); t = np.arange(n) / SR
    ir = r.standard_normal((2, n)) * np.exp(-6.9 * t / rt); ir = lp(ir, damp, 1); ir[:, : int(pre * SR)] = 0
    return (ir / np.sqrt((ir ** 2).sum(axis=1, keepdims=True))).astype(np.float32)


def music_for(key):
    T = dict(TRACKS[key]); T['id'] = key
    drop = T['drop'](T) if callable(T['drop']) else T['drop']
    x, joins = edit(T)
    x = hook_open(x, drop, T['bar'])
    t = np.arange(N) / SR
    x *= smooth(0, 1.2, t)                                   # 처음 1.2초 동안 천천히 들어옴
    if T['hall'] > 0:                                        # 마지막 한 방 뒤 울림을 조금 길게(홀 잔향) — 끝 화면이 조용히 이어지도록
        a, b = int(LOGO * SR), int(min(N, (LOGO + 2.0) * SR))
        hall = make_ir()
        tail = np.stack([fftconvolve(x[c, a:b], hall[c]) for c in range(2)])[:, : N - a]
        x[:, a:a + tail.shape[1]] += T['hall'] * tail * smooth(LOGO + 0.3, LOGO + 1.2, t[a:a + tail.shape[1]])
    x *= 1 - smooth(DUR - 1.3, DUR - 0.02, t)                # 끝 화면이 하얗게 사라질 때 같이 사라짐
    return x.astype(np.float32), joins, drop


# ── 효과음: 꼭 필요한 순간에만, 작게 ──────────────────
rng = np.random.default_rng(20261029)
def env(n, dec, att=0.002):
    t = np.arange(n) / SR
    return np.minimum(1, t / att) * np.exp(-t / dec)
def sine(f, n, ph=0.0):
    f = np.broadcast_to(np.asarray(f, float), (n,))
    return np.sin(2 * np.pi * np.cumsum(f) / SR + ph)
def tone(f, dur, dec, parts=((1, 1.0), (2, 0.28), (3, 0.08))):
    n = int(dur * SR); e = env(n, dec, 0.003)
    return sum(a * sine(f * k, n) for k, a in parts) * e
def st(m, pan=0.0):
    l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
    return np.stack([m * l, m * r]).astype(np.float32)

def sfx_tap():                                               # 화면을 누르는 작은 '톡'
    n = int(0.09 * SR)
    click = hp(rng.standard_normal(n), 2500) * env(n, 0.0035) * 0.35
    body = sine(1250, n) * env(n, 0.010) * 0.55 + sine(320, n) * env(n, 0.028) * 0.45
    return st(click + body)
def sfx_key():                                               # 자판 입력, 아주 작게
    n = int(0.04 * SR)
    return st(hp(rng.standard_normal(n), 3200) * env(n, 0.0025) * 0.5 + sine(2100, n) * env(n, 0.004) * 0.3, rng.uniform(-.15, .15))
def sfx_answer():                                            # 정답 카드: 맑은 두 음 '딩'
    a = tone(1046.5, 1.6, 0.42); b = tone(1396.9, 1.6, 0.5)
    m = np.zeros(int(1.8 * SR)); m[:len(a)] += a * 0.8; k = int(0.09 * SR); m[k:k + len(b)] += b * 0.7
    return st(m)
def sfx_msg():                                               # 답장 도착 '뽁'
    n = int(0.16 * SR); t = np.arange(n) / SR
    f = 520 + (1180 - 520) * (1 - np.exp(-t / 0.012))
    return st(sine(f, n) * env(n, 0.045, 0.002) * 0.9)
def sfx_glint():                                             # 03 Weave 버튼이 '반짝': 아주 짧고 높은 두 음
    m = np.zeros(int(0.9 * SR))
    for i, f in enumerate([2093.0, 2637.0]):
        a = tone(f, 0.7, 0.16, ((1, 1.0), (2, 0.12))); k = int(i * 0.06 * SR); m[k:k + len(a)] += a * (0.6 - 0.15 * i)
    return st(m)
def sfx_logo():                                              # (다른 곡용) 로고에 작은 반짝임
    m = np.zeros(int(1.6 * SR))
    for i, f in enumerate([1396.9, 1760.0, 2093.0]):
        a = tone(f, 1.2, 0.35, ((1, 1.0), (2, 0.15))); k = int(i * 0.07 * SR); m[k:k + len(a)] += a * (0.55 - 0.1 * i)
    return st(m)

def add(dst, sig, t0, gain):
    i = int(round(t0 * SR))
    if i >= N: return
    k = min(N - i, sig.shape[1]); dst[:, i:i + k] += gain * sig[:, :k]

def sfx_track(with_logo):
    s = np.zeros((2, N), np.float32)
    for e in EVJ['events']:
        t0, ty = e['t'], e['type']
        if ty == 'tap': add(s, sfx_tap(), t0, 0.22)
        elif ty == 'key': add(s, sfx_key(), t0, 0.06)
        elif ty == 'answer': add(s, sfx_answer(), t0, 0.11)
        elif ty == 'msg': add(s, sfx_msg(), t0, 0.17)
        elif ty == 'glint': add(s, sfx_glint(), t0, 0.07)
        elif ty == 'logo' and with_logo: add(s, sfx_logo(), t0 + 0.05, 0.07)
    ir = make_ir(1.1, 0.01, 6000, 3)
    wet = np.stack([fftconvolve(s[c], ir[c])[:N] for c in range(2)])
    return (s + 0.18 * wet).astype(np.float32)


# ── 음량 맞추기 ────────────────────────────────────
def k_weight(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=-1), axis=-1)
def lufs(x):
    y = k_weight(x); blk = int(0.4 * SR); hop = int(0.1 * SR)
    ms = np.array([(y[:, i:i + blk] ** 2).mean(axis=1).sum() for i in range(0, y.shape[1] - blk, hop)])
    l = -0.691 + 10 * np.log10(ms + 1e-12); g1 = ms[l > -70]; lg = -0.691 + 10 * np.log10(g1.mean())
    return -0.691 + 10 * np.log10(g1[(-0.691 + 10 * np.log10(g1 + 1e-12)) > lg - 10].mean())
def limit(x, ceil=0.89, look=0.004, rel=0.08):              # 봉우리만 -1 dBFS 아래로 누름(전체 음량은 그대로)
    from scipy.ndimage import minimum_filter1d
    g = np.minimum(1.0, ceil / np.maximum(np.abs(x).max(0), 1e-9))
    g1 = minimum_filter1d(g, size=2 * int(look * SR) + 1, mode='nearest')
    r = np.exp(-1 / (rel * SR)); g2 = lfilter([1 - r], [1, -r], g1, zi=[g1[0] * r])[0]
    return x * np.minimum(g1, g2)
def write(p, x):
    x = limit(x)
    wavfile.write(str(p), SR, (np.clip(x, -1, 1).T * 32767).astype(np.int16))
    return 20 * np.log10(np.abs(x).max() + 1e-12)

TARGET = -16.0
def render(key, path_mix, extra=False):
    m, joins, drop = music_for(key)
    g = 10 ** ((TARGET - lufs(m)) / 20); m *= g
    s = sfx_track(with_logo=not TRACKS[key]['hit'])
    mix = m + s
    pk = write(path_mix, mix)
    T = TRACKS[key]
    print(f"{path_mix.name:16s} {T['name']} ({T['bpm']:.0f} BPM)  drop {drop:.2f}s  logo {LOGO:.2f}s  joins {joins}  {lufs(mix):.1f} LUFS  peak {pk:.1f} dBFS")
    if extra:
        write(OUT / 'bgm_music.wav', m); write(OUT / 'bgm_sfx.wav', s)


if __name__ == '__main__':
    render(MAIN, OUT / 'bgm.wav', extra=True)
    if '--all' in sys.argv:
        for k in TRACKS:
            render(k, OUT / f'bgm_{k}.wav')
