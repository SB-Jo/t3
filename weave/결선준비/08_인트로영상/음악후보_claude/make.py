"""모션그래픽 v23(111.1초)에 다른 배경음악을 넣어 보는 후보 — 화면은 그대로 두고 소리만 바꾼다 (48kHz 스테레오)

사용: ~/.cache/weave-tools/venv/bin/python make.py all            → out/<후보>_music.wav, out/<후보>_mix.wav(음악+효과음), 이음매 검사 출력
      ~/.cache/weave-tools/venv/bin/python make.py all --mux      → 위에 더해 <파일>.mp4(1280×720 확인용), out/<파일>_1440p.mp4(화면 원본 그대로)
      ~/.cache/weave-tools/venv/bin/python make.py coffee --mux   → 후보 하나만
입력: events_v23.json(효과음 시점, v23의 out/events.json 그대로), ../Weave_모션그래픽.mp4(화면),
      ~/.cache/weave-tools/music_claude/mixkit/<번호>.mp3 또는 ~/.cache/weave-tools/music/<번호>.mp3 (https://assets.mixkit.co/music/<번호>/<번호>.mp3)

편집 원칙은 지금 판(tools/music.py)과 같다
- 곡을 새로 만들거나 섞지 않는다. 마디 경계에서만 잘라 붙이고(이음매는 40ms 겹침), 빠르기와 음높이는 손대지 않는다.
- 세 곡 모두 영상의 마디에 그대로 맞는 빠르기라서 골랐다: 100 BPM 두 곡은 지금 곡과 마디(2.4초)가 같고, 105 BPM 한 곡은 네 마디 뒤 9.6초에 북이 들어오고 마흔두 마디 뒤가 로고다.
- 북이 들어오는 때는 지금 판처럼 9.6초(첫 말풍선), 곡의 끝은 로고(105.6초)다. 끝 화면이 하얗게 사라질 때 소리도 같이 사라진다.
- 효과음(누르기·입력·단서 질문·정답·반짝임·답장)은 지금 판과 같은 소리, 같은 자리, 같은 크기다. 음이 있는 정답 '딩'과 반짝임만 곡의 조에 맞춘다
  (지금 판의 '딩' C6 → F6은 C# 장조의 시 → 미. 후보도 저마다 시 → 미, 반짝임은 솔 → 시).
- 음량은 지금 판과 같이 −16 LUFS, 최대 −1 dBFS.
"""
import hashlib, json, subprocess, sys
from fractions import Fraction
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve, lfilter, resample_poly

SR = 48000
HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
LIBS = [Path.home() / '.cache/weave-tools/music_claude/mixkit', Path.home() / '.cache/weave-tools/music']
FFMPEG = Path.home() / '.cache/weave-tools/bin/ffmpeg'
VIDEO = HERE.parent / 'Weave_모션그래픽.mp4'              # v23. 화면만 쓴다
VIDEO_SHA = 'f412910d5365b3a9'                             # v23 파일의 sha256 앞 16자(다른 판이면 멈춘다)
EVJ = json.loads((HERE / 'events_v23.json').read_text())
DUR = float(EVJ['duration'])
N = int(round(DUR * SR))
LOGO = next(e['t'] for e in EVJ['events'] if e['type'] == 'logo')
DROP = 9.6                                                 # 첫 말풍선(지금 판에서 곡이 터지는 때)
assert abs(DUR - 111.1) < 1e-6 and abs(LOGO - 105.6) < 1e-6

# ── 후보: bpm = 곡의 빠르기(박 검출로 잰 값), g0 = 첫 마디 첫 박 바로 앞(초, 여기서 자른다), segs = [(영상 시작초, 그때 곡의 마디 번호), ...]
#    logobar = 로고에 오는 곡의 마디, end = 끝 모양('chord' 곡의 마지막 화음이 울림 · 'stop' 곡이 멈추고 잔향 · 'fade' 북 없는 대목이 끝 화면과 함께 사라짐)
#    tonic = 으뜸음(장조 기준, 0=C). 단조 곡은 나란한조의 으뜸음 ──
TRACKS = {
    'coffee': dict(id='1168', name='Coffee or Tea', artist='Michael Ramir C.', bpm=105.0, g0=0.150, key='G# 장조', tonic=8, file='A_Coffee_or_Tea',
                   # 곡의 구조(마디): 인트로 0–3(신스 무늬만) · A 4–11 · B 12–19 · A 20–27 · 가벼운 C 28–35 · 잦아드는 D 36–43 · 다시 차오르는 44 · 마지막 A 45–52 · 멈춤 53
                   # 0.457초(로고 글자가 뜰 때)에 곡의 첫 소리 → 네 마디 뒤 9.6초에 4마디(북·베이스) → 곡 순서대로 35마디까지(82.74초)
                   # → 43–44마디(잦아든 끝 두 마디, 82.74–87.31초) → 마지막 A 45–52(87.31–105.6초) → 53마디(멈춤)가 로고에. 이음매는 82.74초(35 → 43) 한 곳
                   segs=lambda bar: [(DROP - 4 * bar, 0), (DROP + 32 * bar, 43)], logobar=53, end='stop', hall=0.30),
    'acoustical': dict(id='769', name='Acoustical', artist='Mauro Urbina', bpm=100.0, g0=0.075, key='C# 장조', tonic=1, file='B_Acoustical',
                       # 곡의 구조: 기타만 0–7(네 마디 두 번, 7마디 끝에 북으로 넘어가는 소리) · 북이 들어온 8–15 · 조금 가벼운 16–23 · 24–39 · 하이햇이 줄어든 40–47 · 마지막 화음 48
                       # 0초 곡의 0–2마디 → 7.2초(01 장면 시작) 7마디 → 9.6초 8마디(북)부터 곡 끝까지 그대로(마흔 마디) → 48마디(마지막 화음)가 로고에. 이음매는 7.2초(2 → 7) 한 곳
                       segs=lambda bar: [(0.0, 0), (DROP - bar, 7)], logobar=48, end='chord', hall=0.22),
    'alone': dict(id='486', name='Alone', artist='Diego Nava', bpm=100.0, g0=0.0, key='A 단조', tonic=0, file='C_Alone',
                  # 곡의 구조: 인트로 0–3 · A 4–15(4마디 첫 박에 크래시) · 하이햇이 들어온 B 16–23 · 북 없는 24–27 · C 28–39(B와 같은 무늬) · 끝 40(북 없는 한 마디)
                  # 0초 곡의 0마디 → 9.6초 4마디(북) → 곡 순서대로 23마디까지(57.6초) → B 16–23 한 번 더(57.6–76.8초) → 북 없는 24–27(76.8–86.4초, 03 대화)
                  # → C 28–35(86.4–105.6초) → 로고에서 북이 빠지고 24마디부터의 북 없는 대목이 끝 화면과 함께 사라짐. 이음매는 57.6초(23 → 16), 105.6초(35 → 24) 두 곳
                  segs=lambda bar: [(0.0, 0), (DROP + 20 * bar, 16), (LOGO, 24)], logobar=24, end='fade', hall=0.0),
}


def lp(x, f, order=2): return sosfilt(butter(order, f / (SR / 2), 'low', output='sos'), x, axis=-1)
def hp(x, f, order=2): return sosfilt(butter(order, f / (SR / 2), 'high', output='sos'), x, axis=-1)


def decode(tid):
    path = next(d / f'{tid}.mp3' for d in LIBS if (d / f'{tid}.mp3').exists())
    info = subprocess.run([str(FFMPEG), '-hide_banner', '-i', str(path)], capture_output=True, text=True).stderr
    sr0 = int(info.split(' Hz')[0].split()[-1])
    raw = subprocess.run([str(FFMPEG), '-hide_banner', '-loglevel', 'error', '-i', str(path), '-f', 'f32le', '-ac', '2', '-ar', str(sr0), '-'], check=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).T
    fr = Fraction(SR, sr0)
    return resample_poly(x, fr.numerator, fr.denominator, axis=1).astype(np.float32)


def smooth(a, b, x):                                       # 0→1 사이를 부드럽게(코사인)
    u = np.clip((x - a) / max(b - a, 1e-9), 0, 1)
    return 0.5 - 0.5 * np.cos(np.pi * u)


def edit(src, bar, g0, segs):
    """마디 단위로 잘라 붙인 곡(2×N)"""
    out = np.zeros((2, N), np.float32)
    XF = int(0.040 * SR)
    for i, (v0, b0) in enumerate(segs):
        nxt = segs[i + 1] if i + 1 < len(segs) else None
        v1 = nxt[0] if nxt is not None else DUR
        off = g0 + b0 * bar - v0                            # 곡 시각 = 영상 시각 + off
        a, b = int(round(v0 * SR)), int(round(v1 * SR))
        a2 = a if i == 0 else max(0, a - XF // 2)            # 이음매에서 겹칠 만큼 앞뒤로 조금 더
        b2 = min(N, b + XF // 2) if nxt is not None else b
        idx = np.arange(a2, b2) + int(round(off * SR))
        ok = (idx >= 0) & (idx < src.shape[1])
        seg = np.zeros((2, b2 - a2), np.float32); seg[:, ok] = src[:, idx[ok]]
        w = np.ones(b2 - a2, np.float32)
        if i > 0: w[:XF] = np.sin(np.linspace(0, np.pi / 2, XF)) ** 2            # 들어올 때
        if nxt is not None: w[-XF:] = np.cos(np.linspace(0, np.pi / 2, XF)) ** 2  # 나갈 때
        out[:, a2:b2] += seg * w
    return out


def make_ir(rt=3.0, pre=0.02, damp=5000, seed=7):
    r = np.random.default_rng(seed); n = int(rt * SR); t = np.arange(n) / SR
    ir = r.standard_normal((2, n)) * np.exp(-6.9 * t / rt); ir = lp(ir, damp, 1); ir[:, : int(pre * SR)] = 0
    return (ir / np.sqrt((ir ** 2).sum(axis=1, keepdims=True))).astype(np.float32)


def music_for(key):
    T = TRACKS[key]
    bar = 240.0 / T['bpm']
    segs = T['segs'](bar)
    x = edit(decode(T['id']), bar, T['g0'], segs)
    at_logo = segs[-1][1] + (LOGO - segs[-1][0]) / bar
    assert abs(at_logo - T['logobar']) < 1e-6, f"{key}: 로고에 {at_logo:.3f}마디가 옴(와야 하는 마디는 {T['logobar']})"
    t = np.arange(N) / SR
    t0 = segs[0][0]
    x *= smooth(t0, t0 + 0.025, t)                           # 곡의 첫 소리는 그대로(딸깍 소리만 막게 25ms)
    if T['hall'] > 0:                                        # 끝이 조용히 이어지도록 홀 잔향을 조금
        pre = 0.5 if T['end'] == 'stop' else 0.0             # 멈추는 끝은 멈추기 직전 소리의 잔향이 로고 뒤로 남는다
        a, b = int((LOGO - pre) * SR), int(min(N, (LOGO + 2.0) * SR))
        hall = make_ir()
        tail = np.stack([fftconvolve(x[c, a:b], hall[c]) for c in range(2)])[:, : N - a]
        ta = t[a:a + tail.shape[1]]
        x[:, a:a + tail.shape[1]] += T['hall'] * tail * (smooth(LOGO, LOGO + 0.25, ta) if pre else smooth(LOGO + 0.3, LOGO + 1.2, ta))
    x *= 1 - smooth(DUR - 1.3, DUR - 0.02, t)                # 끝 화면이 하얗게 사라질 때 같이 사라짐
    return x.astype(np.float32)


# ── 효과음: tools/music.py와 같은 소리. 음이 있는 것만 곡의 조에 맞춘다 ──────────────────
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
def sfx_answer(f1, f2):                                      # 정답 카드: 맑은 두 음 '딩'
    a = tone(f1, 1.6, 0.42); b = tone(f2, 1.6, 0.5)
    m = np.zeros(int(1.8 * SR)); m[:len(a)] += a * 0.8; k = int(0.09 * SR); m[k:k + len(b)] += b * 0.7
    return st(m)
def sfx_msg():                                               # 답장 도착 '뽁'
    n = int(0.16 * SR); t = np.arange(n) / SR
    f = 520 + (1180 - 520) * (1 - np.exp(-t / 0.012))
    return st(sine(f, n) * env(n, 0.045, 0.002) * 0.9)
def sfx_glint(f1, f2):                                       # 03 Weave 버튼이 '반짝': 아주 짧고 높은 두 음
    m = np.zeros(int(0.9 * SR))
    for i, f in enumerate([f1, f2]):
        a = tone(f, 0.7, 0.16, ((1, 1.0), (2, 0.12))); k = int(i * 0.06 * SR); m[k:k + len(a)] += a * (0.6 - 0.15 * i)
    return st(m)
def sfx_logo(fs):                                            # (마지막 화음이 없는 곡) 로고에 작은 반짝임
    m = np.zeros(int(1.6 * SR))
    for i, f in enumerate(fs):
        a = tone(f, 1.2, 0.35, ((1, 1.0), (2, 0.15))); k = int(i * 0.07 * SR); m[k:k + len(a)] += a * (0.55 - 0.1 * i)
    return st(m)

def add(dst, sig, t0, gain):
    i = int(round(t0 * SR))
    if i >= N: return
    k = min(N - i, sig.shape[1]); dst[:, i:i + k] += gain * sig[:, :k]

def note(pc, near):
    """음이름 번호 pc(0=C)의 주파수 가운데 near(Hz)에 가장 가까운 옥타브"""
    f = 261.6256 * 2 ** ((pc % 12) / 12)
    return f * 2 ** round(np.log2(near / f))

def sfx_track(tonic, with_logo):
    global rng
    rng = np.random.default_rng(20261029)                    # 후보마다 같은 '톡'·입력 소리
    a1 = note(tonic + 11, 1046.5); a2 = a1 * 2 ** (5 / 12)   # 정답: 시 → 미
    g1 = note(tonic + 7, 2093.0); g2 = g1 * 2 ** (4 / 12)    # 반짝임: 솔 → 시
    lg = [note(tonic, 1396.9)]; lg += [lg[0] * 2 ** (4 / 12), lg[0] * 2 ** (7 / 12)]   # 로고: 도 → 미 → 솔
    s = np.zeros((2, N), np.float32)
    for e in EVJ['events']:
        t0, ty = e['t'], e['type']
        if ty == 'tap': add(s, sfx_tap(), t0, 0.22)
        elif ty == 'key': add(s, sfx_key(), t0, 0.06)
        elif ty == 'answer': add(s, sfx_answer(a1, a2), t0, 0.11)
        elif ty == 'msg': add(s, sfx_msg(), t0, 0.17)
        elif ty == 'pen': add(s, sfx_msg(), t0, 0.07)         # 단서 질문이 뜰 때 아주 작게
        elif ty == 'glint': add(s, sfx_glint(g1, g2), t0, 0.07)
        elif ty == 'logo' and with_logo: add(s, sfx_logo(lg), t0 + 0.05, 0.07)
    ir = make_ir(1.1, 0.01, 6000, 3)
    wet = np.stack([fftconvolve(s[c], ir[c])[:N] for c in range(2)])
    return (s + 0.18 * wet).astype(np.float32), [round(v) for v in (a1, a2, g1, g2)]


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


# ── 검사: 이음매·음량·시각을 숫자로 ──────────────────
def flux(x, t, w=0.08):
    """t 앞뒤 80ms 스펙트럼이 얼마나 다른가. 곡 원래 마디 경계와 견준다"""
    n = int(w * SR); b = int(round(t * SR)); a, c = b - n, b + n
    if a < 0 or c > x.shape[1]: return float('nan')
    win = np.hanning(n)
    A = np.abs(np.fft.rfft(x[:, a:b].mean(0) * win)); B = np.abs(np.fft.rfft(x[:, b:c].mean(0) * win))
    return float(np.abs(np.log1p(200 * A / (A.max() + 1e-9)) - np.log1p(200 * B / (B.max() + 1e-9))).mean() * 10)

def loud(x, a, b):
    a, b = max(int(a * SR), 0), min(int(b * SR), x.shape[1])
    return 10 * np.log10((x[:, a:b] ** 2).mean() + 1e-12)

def onset_near(x, t, span=0.2, band=None):
    """t 근처에서 소리가 가장 가파르게 커지는 시각(5ms 창)"""
    y = x.mean(0)
    if band: y = sosfilt(butter(2, [band[0] / (SR / 2), band[1] / (SR / 2)], 'band', output='sos'), y)
    h = int(0.005 * SR); a = int((t - span) * SR); b = int((t + span) * SR)
    e = np.array([np.sqrt((y[i:i + h] ** 2).mean()) for i in range(a, b, h)])
    d = np.diff(20 * np.log10(e + 1e-6)); k = int(np.argmax(d))
    return (a + (k + 1) * h) / SR, float(d[k])

def check(key, x):
    T = TRACKS[key]; bar = 240.0 / T['bpm']; segs = T['segs'](bar)
    t0 = segs[0][0]; joins = [s[0] for s in segs[1:]]
    nat = [t0 + k * bar for k in range(1, int(round((LOGO - t0) / bar))) if all(abs(t0 + k * bar - j) > 0.01 for j in joins)]
    fx = np.array([flux(x, t) for t in nat])
    print(f'  곡 원래 마디 경계 {len(nat)}곳의 스펙트럼 차: 평균 {np.nanmean(fx):.2f}, 최대 {np.nanmax(fx):.2f}')
    for j in joins:
        f = flux(x, j)
        print(f'  이음매 {j:7.3f}초: 스펙트럼 차 {f:.2f}(원래 경계 {(fx < f).mean() * 100:.0f}%보다 큼), 앞뒤 0.6초 음량 {loud(x, j - 0.6, j):.1f} → {loud(x, j, j + 0.6):.1f}dB')
    h = 0.1; n = int((LOGO - t0) / h)
    l4 = np.array([loud(x, t0 + i * h, t0 + i * h + 0.4) for i in range(n)])
    dips = [round(t0 + i * h, 1) for i in range(20, n) if l4[i] < l4[i - 20:i].mean() - 5]
    grp = []
    for t in dips:
        if grp and t - grp[-1][1] <= 0.6: grp[-1][1] = t
        else: grp.append([t, t])
    print('  0.4초 음량이 앞 2초 평균보다 5dB 넘게 떨어지는 곳:', ', '.join(f'{a}–{b + 0.4:.1f}초' for a, b in grp) or '없음')
    first = np.argmax(np.abs(x.mean(0)) > 10 ** (-45 / 20)) / SR
    td, dd = onset_near(x, DROP, band=(40, 180))
    print(f'  첫 소리 {first:.3f}초, 북이 들어오는 때 {td:.3f}초(저음 {dd:+.0f}dB/5ms, 앞뒤 한 마디 {loud(x, DROP - bar, DROP):.1f} → {loud(x, DROP, DROP + bar):.1f}dB), '
          f'로고 앞뒤 0.6초 {loud(x, LOGO - 0.6, LOGO):.1f} → {loud(x, LOGO, LOGO + 0.6):.1f}dB')
    nb = int((DUR - t0) / bar)
    print('  마디 음량(dB):', ' '.join(f'{loud(x, t0 + k * bar, min(t0 + (k + 1) * bar, DUR)):.0f}' for k in range(nb + 1)))


def render(key, mux=False):
    T = TRACKS[key]
    m = music_for(key)
    m *= 10 ** ((TARGET - lufs(m)) / 20)
    s, notes = sfx_track(T['tonic'], with_logo=T['end'] != 'chord')
    OUT.mkdir(exist_ok=True)
    write(OUT / f'{key}_music.wav', m)
    pk = write(OUT / f'{key}_mix.wav', m + s)
    bar = 240.0 / T['bpm']
    print(f"{key}: {T['name']} — {T['artist']} ({T['bpm']:g} BPM, {T['key']}, 마디 {bar:.4f}초)  구간 {[(round(v, 3), b) for v, b in T['segs'](bar)]}  {lufs(m + s):.1f} LUFS  최대 {pk:.1f} dBFS  효과음 음(Hz) {notes}")
    check(key, m)
    if mux:
        assert hashlib.sha256(VIDEO.read_bytes()).hexdigest().startswith(VIDEO_SHA), '화면이 v23이 아님'
        full = OUT / f"{T['file']}_1440p.mp4"; small = HERE / f"{T['file']}.mp4"
        base = [str(FFMPEG), '-hide_banner', '-loglevel', 'error', '-y', '-i', str(VIDEO), '-i', str(OUT / f'{key}_mix.wav'), '-map', '0:v', '-map', '1:a']
        subprocess.run(base + ['-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', str(full)], check=True)
        subprocess.run(base + ['-vf', 'scale=1280:720:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', '-pix_fmt', 'yuv420p',
                               '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(small)], check=True)
        print(f'  → {small.name} ({small.stat().st_size / 1e6:.1f}MB), out/{full.name} ({full.stat().st_size / 1e6:.1f}MB)')


if __name__ == '__main__':
    for k in (list(TRACKS) if sys.argv[1] == 'all' else [sys.argv[1]]):
        render(k, mux='--mux' in sys.argv)
