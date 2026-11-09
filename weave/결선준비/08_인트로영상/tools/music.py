"""Weave 모션그래픽 v19 배경음악 — 기존 곡(Mixkit, 무료 상업 이용 가능)을 영상에 맞춰 편집하고, 꼭 필요한 순간에만 작은 효과음을 얹는다 (48kHz 스테레오)

사용: ~/.cache/weave-tools/venv/bin/python tools/music.py            → out/bgm.wav(음악+효과음), out/bgm_music.wav, out/bgm_sfx.wav  (기본 곡)
입력: out/events.json(효과음 시점, node tools/render.cjs --events), ~/.cache/weave-tools/music/<번호>.mp3

편집 원칙
- 곡을 새로 만들거나 리믹스하지 않는다. 마디 단위로만 잘라 붙여(템포·박자 그대로) 길이를 맞추고, 이음매는 40ms로 겹친다.
- v16: 곡을 첫 마디부터 그대로 튼다(오프닝 = 곡의 첫 두 마디, I–IV). 01 장면 카드(D1)에서 곡의 12마디(I, 킥·베이스)로 넘어가 터진다.
       (v15까지는 곡의 10.44마디, 즉 곡 중간에서 먹먹하게 시작해서 시작 느낌이 없었음)
- 로고(LOGO)는 곡의 마지막 한 방(기본 곡) 또는 마디 첫 박(다른 곡)에 맞춘다. 끝 화면이 하얗게 사라질 때 소리도 같이 사라진다.
- 효과음: 손으로 누를 때 작은 '톡', 글자 입력은 아주 작게, 단서 질문이 뜰 때 아주 작은 '뽁', 정답 카드에 '딩', 03 Weave 버튼이 반짝일 때 아주 짧은 '띵', 답장에 '뽁'. 바람·탬버린 같은 소리는 넣지 않는다.
- v5: v4 곡(Digital Clouds)보다 밝은 장조 곡으로 바꿈.
- v6: 영상이 74초로 길어짐. 기본 'A Special Feeling', 비교 'Uplift Me' 두 곡만(사용자가 고름). 4마디 단위로만 건너뛰어 화음이 이어지게 함.
- v8: 03이 길어져 79초(로고 74.1초, 두 마디 더). 기본 곡은 거의 같은 마디(33·35)를 이용해 두 마디를 되풀이하고,
      곡2는 2마디 단위로 자르면 화음이 어긋나서 4마디 단위를 지킴 → 비트가 들어오는 때가 13.3초에서 10.1초로.
- v19: 같은 대목을 마디 중간에서 되풀이하던 이음매 두 곳(38.4초 25→21마디, 76.8초 36→25마디)을 없앰. 앞의 것은 들은 지 4초 만에 같은 다섯 마디가 다시 나왔고,
       뒤의 것은 클라이맥스(32–39마디)를 다섯 마디에서 끊고 B로 돌아갔다(사용자: '같은 구간이 애매하게 반복되어 끊겨 보인다').
       곡의 구조는 인트로 0–11(8–11은 북 없이 차오름) · A 12–19 · B 20–27(같은 네 마디 두 번) · 잦아드는 28–31 · 클라이맥스 32–39 · 한 방 40.
       이제는 곡 순서대로 A·B → 11마디 한 마디 쉼(V, 북 없음) → A·B 한 번 더(2절처럼) → 28–31 → 32–39 → 40. 이음매는 4.8초(1→12)와 43.2초(27→11) 두 곳뿐이고,
       43.2초는 B의 끝 박 여운이 0.35초 동안 잦아들며 쉼 마디로 넘어간다. 쉼 마디는 02의 큰 질문 글을 읽는 때, 2절 첫 박(45.6초)은 휴대폰이 가운데로 오는 때(tZ)다.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve, lfilter

SR = 48000
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out'
LIB = Path.home() / '.cache/weave-tools/music'
FFMPEG = Path.home() / '.cache/weave-tools/bin/ffmpeg'
EVJ = json.loads((OUT / 'events.json').read_text())
DUR = float(EVJ['duration'])
N = int(round(DUR * SR))
LOGO = next(e['t'] for e in EVJ['events'] if e['type'] == 'logo')
D1 = 4.8                                                   # 01 장면에서 기본 곡이 터지는 순간(main.js의 D1). 곡의 첫 두 마디 뒤

# ── 곡 정보: 마디 길이(bar)와 첫 마디 시작(g0)은 박 검출로 잰 값. segs = [(영상 시작초, 그때 곡의 마디 번호), ...]
#    drop = 곡이 터지는 영상 시각, hit = 로고 자리가 곡의 마지막 한 방인지(아니면 로고에 작은 반짝임 효과음), hall = 마지막 한 방 뒤 울림 ──
TRACKS = {
    '1087': dict(name='A Special Feeling', artist='Michael Ramir C.', bpm=100.0, g0=0.0, key='C# 장조',
                 # 곡의 화음은 네 마디마다 I–IV–vi–V(C#–F#–A#m–G#). 오프닝은 곡의 0·1마디(I–IV, 곡의 진짜 시작) → 4.8초(D1, 첫 장면 카드)에 12마디(I, 킥·베이스)로 넘어감(IV → I).
                 # v19: 12–27마디(A·B, 4.8–43.2초) → 11마디(V, 북 없는 쉼 한 마디, 43.2–45.6초) → 12마디부터 곡 끝까지 그대로(A·B 2절, 28–31 잦아듦 84.0–93.6초 = 03 플로팅,
                 # 32–39 클라이맥스 93.6초 = 03 실이 휴대폰으로 엮일 때) → 40마디(마지막 한 방)가 로고(112.8초)에. 27(V) → 11(V) → 12(I)라서 화음도 이어진다
                 segs=lambda T: [(0.0, 0), (D1, 12), (D1 + 16 * T['bar'], 11, None, 0.35)], drop=lambda T: D1, hit=True, hall=0.22, hitbar=40),
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
    """마디 단위로 잘라 붙인 곡(2×N)과 이음매 목록. segs의 넷째 값(tail)이 있으면 앞 구간의 소리가 그만큼 이음매 뒤로 잦아들며 남는다"""
    src = decode(LIB / f"{T['id']}.mp3")
    bar, g0 = T['bar'], T['g0']
    segs = T['segs'](T)
    out = np.zeros((2, N), np.float32)
    XF = int(0.040 * SR)
    joins = []
    FI = int(0.02 * SR)
    for i, sg in enumerate(segs):
        v0, b0 = sg[0], sg[1]
        pre_in = sg[2] if len(sg) > 2 else None                       # 이 구간 앞 이음매가 '미리 잦아드는' 이음매인지
        nxt = segs[i + 1] if i + 1 < len(segs) else None
        pre_out = nxt[2] if nxt is not None and len(nxt) > 2 else None
        tail = nxt[3] if nxt is not None and len(nxt) > 3 else None       # 다음 이음매에서 이 구간이 잦아들며 남을 길이(초)
        v1 = nxt[0] if nxt is not None else DUR
        off = g0 + b0 * bar - v0                            # 곡 시각 = 영상 시각 + off
        a, b = int(round(v0 * SR)), int(round(v1 * SR))
        a2 = a if pre_in else max(0, a - XF // 2)            # 이음매에서 겹칠 만큼 앞뒤로 조금 더
        b2 = b if pre_out else (min(N, b + int(tail * SR)) if tail else min(N, b + XF // 2))
        idx = np.arange(a2, b2) + int(round(off * SR))
        ok = (idx >= 0) & (idx < src.shape[1])
        seg = np.zeros((2, b2 - a2), np.float32); seg[:, ok] = src[:, idx[ok]]
        w = np.ones(b2 - a2, np.float32)
        if i > 0:
            k = FI if pre_in else XF
            w[:k] = np.sin(np.linspace(0, np.pi / 2, k)) ** 2            # 들어올 때
        if nxt is not None:
            k = int(pre_out * SR) if pre_out else ((b2 - b) + XF // 2 if tail else XF)
            w[-k:] = np.cos(np.linspace(0, np.pi / 2, k)) ** 2          # 나갈 때
        out[:, a2:b2] += seg * w
        joins.append((round(v0, 3), round(off + v0, 3), round(b0, 3)))
    return out, joins


def make_ir(rt=3.0, pre=0.02, damp=5000, seed=7):
    r = np.random.default_rng(seed); n = int(rt * SR); t = np.arange(n) / SR
    ir = r.standard_normal((2, n)) * np.exp(-6.9 * t / rt); ir = lp(ir, damp, 1); ir[:, : int(pre * SR)] = 0
    return (ir / np.sqrt((ir ** 2).sum(axis=1, keepdims=True))).astype(np.float32)


def music_for(key):
    T = dict(TRACKS[key]); T['id'] = key
    drop = T['drop'](T) if callable(T['drop']) else T['drop']
    x, joins = edit(T)
    s0 = T['segs'](T)[-1]; at_logo = s0[1] + (LOGO - s0[0]) / T['bar']        # 로고 자리에 오는 곡의 마디
    assert abs(at_logo - T['hitbar']) < 1e-6, f"{key}: 로고에 {at_logo:.2f}마디가 옴(마지막 한 방은 {T['hitbar']}마디) — main.js의 LOGO가 바뀌면 segs를 맞출 것"
    t = np.arange(N) / SR
    x *= smooth(0, 0.025, t)                                 # 곡의 첫 소리는 그대로(딸깍 소리만 막게 25ms)
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
        elif ty == 'pen': add(s, sfx_msg(), t0, 0.07)         # 단서 질문이 뜰 때 아주 작게
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
