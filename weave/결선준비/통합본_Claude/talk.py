#!/usr/bin/env python3
"""통합본을 처음부터 끝까지 말하며 넘기는 영상 → Weave_통합본_Claude_미리보기.mp4

  python talk.py                낭독 → 덱(make.py와 같음) → 저절로 넘어가는 사본 → PowerPoint 녹화 → 낭독·자막·모션그래픽 소리를 얹음
                                (1920×1080 원본은 out/…_1080p.mp4, 덱 옆에는 확인용 1280×720)
  python talk.py --remux        녹화(out/_silent.mp4)는 그대로 두고 낭독·자막만 다시 얹음
  python talk.py --time         낭독까지만 하고 장마다 걸리는 시간을 어림(녹화하지 않음)
  python talk.py --proposal     제안 장표 세 장만 따로 → 제안장표_미리보기.mp4
  python talk.py --new          새로 그린 장만(6, 9, 11~12, 14쪽, 뒷부분, 제안 장표) 빨리 찍어 봄 → out/새장_미리보기.mp4
  --check                       낭독을 받아쓰기로 글과 견줌(out/tts_check.txt)

하는 일
- 낭독은 이 컴퓨터 안에서만 만든다(09_HowItWorks/장표5_claude의 tts_c: Supertonic 3, 목소리 F2F1_70, 속도 1.15).
- 인트로 장(다른 덱에서 옮긴 장)은 효과가 저절로 나오므로, 그 장의 말이 끝날 때까지 머물게만 한다. 말할 글은 노트(slides_new.INTRO_NOTES)에서 괄호 속 무대 지시를 뺀 것.
- 새로 그린 장은 How it Works 낭독 영상과 같은 방식: 클릭 묶음마다 그 구간의 말이 끝날 때까지 머문다.
- 장(또는 구간)마다 왼쪽 아래 구석에 작은 색 표를 두고, 녹화에서 그 표가 뜬 때를 찾아 낭독을 그 자리에 놓는다. 표는 마지막에 덮어 지운다.
- 모션그래픽 장은 원본 영상(08_인트로영상/Weave_모션그래픽.mp4)의 화면과 소리를 녹화 속 재생이 시작한 때에 맞춰 얹는다.
- 자막은 문장마다 따로, 그 문장을 말하는 동안만 띄운다.
"""
import argparse
import copy
import json
import re
import shutil
import subprocess
import types
from pathlib import Path

import numpy as np
from lxml import etree
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation

import make as MK

HW, F, N = MK.HW, MK.F, MK.N
import render_c  # noqa: E402
import tts_c  # noqa: E402
from ui import R  # noqa: E402

HERE = MK.HERE
OUT = MK.OUT
FFMPEG = HW.FFMPEG
MP4 = HERE / 'Weave_통합본_Claude_미리보기.mp4'
MP4_P = HERE / '제안장표_미리보기.mp4'
MG_MP4 = MK.MG_MP4
MG_LEN = 111.1                     # 모션그래픽 길이(초)
MG_TAIL = 1.4                      # 영상이 끝난 뒤 그 장에 더 머무는 시간
MG_VOL = 0.8                       # 덱에 넣은 영상 소리 크기(80%)와 같게
END_HOLD = 3.0                     # 말이 없는 끝 화면에 머무는 시간
SPEAKER = '장이준'                 # 노트에 [발표자 이름]이 남아 있으면 읽을 이름
LEADS = {'cover': 1.0, 'in02': 1.2}                     # 장이 열린 뒤 말을 떼기까지(초): 표지, 2쪽(문장이 다 뜬 뒤)
MARK_RGB = ['FF00FF', '00FFFF', '00FF00']               # 구간 표 색(차례로 번갈아). 영상에서 덮어 지움
MARK_BOX = HW.MARK_BOX
FONT = Path.home() / '.cache' / 'weave-tools' / 'fonts' / 'SamsungOneKorean-500.ttf'
P14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
SUB_H = 150                        # 자막 띠 높이(px, 1920×1080 기준). 띠의 아래 끝이 화면 y = 1065


# ------------------------------------------------------------------ 말할 글
def say_text(key, note):
    """옮겨 온 장의 노트 → 소리 내어 말할 글(괄호 속 지시를 뺌)."""
    return F.spoken(note).replace('[발표자 이름]', SPEAKER)


def foreign_units():
    """표지와 옮겨 온 인트로 장: [(키, 덱 노트, 말할 글)]. 노트는 slides_new.INTRO_NOTES(새 대본)."""
    return [(k, N.INTRO_NOTES[k], say_text(k, N.INTRO_NOTES[k])) for k in ['cover'] + MK.INTRO_KEYS]


own_specs = MK.own_specs


def disp_sents(seg):
    """자막에 띄울 문장들: 낭독 토막(HW._sents)과 같은 자리에서 끊되, 글자는 원문 그대로(영문·숫자·따옴표)."""
    out = []
    for part in ' '.join(seg.split()).split(HW.REST):
        out += [t for t in re.split(r'''(?<=[.?!])(?=\s)|(?<=[.?!]['’”"])(?=\s)''', part.strip()) if t.strip()]
    return [t.strip() for t in out]


def narrate_all(check=False):
    """본 발표와 제안 장표의 말을 한 번에 낭독한다(HW.narrate가 out/tts를 비우고 다시 쓰므로 늘 함께).
    돌려줌: (옮겨 온 장 목록, {키: [구간마다 걸리는 시간]}, {키: [wav]})."""
    fu = foreign_units()
    proxies = [types.SimpleNamespace(key=k, notes=say) for k, _, say in fu]
    own = own_specs()
    specs = proxies + [sp for name in ('hook', 'hub2', 'rec', 'bridge', 'hiw', 'back', 'prop') for sp in own[name] if sp.notes.strip()]
    says, clips = HW.narrate(specs, None, check)
    for p in proxies:               # 옮겨 온 장: 말 떼기까지의 틈을 장마다 따로
        lead = LEADS.get(p.key, HW.LAT_START)
        says[p.key] = [lead + tts_c.wav_len(clips[p.key][0]) + HW.seg_gaps(p)[0]]
    return fu, says, clips


# ------------------------------------------------------------------ 저절로 넘어가는 사본
def talkify(specs, says, k, plan):
    """새로 그린 장: 구간마다 그 구간의 말이 끝날 때까지 머물게 하고(sp.holds), 구간이 시작할 때 뜨는 표를 붙인다."""
    for sp in specs:
        say = says.get(sp.key) or [END_HOLD] * len(sp.groups)
        assert len(say) == len(sp.groups), (sp.key, len(say), len(sp.groups))
        sp.holds = [max(round(say[j] * 1000) - HW._group_len(g), 0) for j, g in enumerate(sp.groups)]
        marks = []
        for j, grp in enumerate(sp.groups):
            key = 'mk/%s/%d' % (sp.key, j)
            sp.add(key, [R(key, *MARK_BOX, fill=MARK_RGB[k % 3], line=None)])
            grp.insert(0, (key, 'appear', 0, 1, {}))
            marks.append(k)
            k += 1
        plan.append(dict(key=sp.key, kind='own', marks=marks, leads=HW.seg_leads(sp) if sp.notes.strip() else [],
                         segs=sp.notes.split('(클릭)') if sp.notes.strip() else []))
    return k


PART = {'proposal': ['prop'], 'new': ['hook', 'hub2', 'rec', 'bridge', 'back', 'prop']}       # 따로 찍는 묶음


def build_auto(dst, fu, says, part=None):
    """녹화용 사본: 본 발표 장만(part를 주면 그 묶음만), 클릭 없이 저절로. 돌려줌: (장마다 머무는 초, 장 계획)."""
    prs = Presentation(str(MK.BASE))
    old = list(prs.slides)
    cover, mg = old[0], old[3]
    layout = old[5].slide_layout
    note_tpl = [copy.deepcopy(sh._element) for sh in old[5].notes_slide.placeholders]
    own = own_specs()               # 낭독 뒤에 다시 만든다(말에 맞춰 뜨는 효과의 때가 낭독에서 나옴)
    plan, k = [], 0

    def draw(specs, k):
        """새로 그린 묶음을 덱 끝에 넣고 계획에 적는다. 돌려줌: (장들, 다음 표 번호)."""
        n0 = len(plan)
        k = talkify(specs, says, k, plan)
        slides, _, secs = HW.add_slides(prs, layout, note_tpl, specs, auto=True)
        for p, sec, sp in zip(plan[n0:], secs, specs):
            p['secs'], p['trans'] = sec, (sp.trans[1] / 1000 if sp.trans else 0)
        return slides, k
    if part:
        slides, k = draw([sp for name in PART[part] for sp in own[name]], k)
        MK.drop_slides(prs, old)
        MK.samsung_fonts.remap_prs(prs)
        MK.logo_style(slides)
        prs.save(str(dst))
        return [p['secs'] for p in plan], plan
    src = list(Presentation(str(MK.INTRO)).slides)
    intro = {key: F.copy_slide(prs, src[int(key[2:]) - 1], note_tpl) for key in MK.INTRO_KEYS}
    MK.patch_intro(intro, note_tpl)
    MK.patch_cover(cover)           # 덱과 같은 표지(영상 v9, 제목 크기)로 찍는다
    MK.patch_mg(mg)                 # 덱과 같은 모션그래픽(v24)
    say_of = {key: say for key, _, say in fu}
    order, logos = [], []
    for item in MK.SEQ:
        if isinstance(item, tuple):
            slides, k = draw(own[item[1]], k)
            order += slides
            logos += slides if item[1] == 'bridge' else []
            continue
        if item == 'mg':
            F.add_mark(mg, MARK_BOX, MARK_RGB[k % 3], 'mk_mg')
            plan.append(dict(key='mg', kind='video', marks=[k], leads=[], segs=[], secs=MG_LEN + MG_TAIL, trans=0))
            order.append(mg)
            k += 1
            continue
        key, slide = item, (cover if item == 'cover' else intro[item])
        hold = says[key][0]
        if key != 'cover':
            hold = max(hold, F.anim_len(slide) / 1000 + 0.3)
        else:                       # 표지 영상(18초)이 끝나야 PowerPoint가 장을 넘기므로, 녹화용 사본에서는 머무는 시간만큼만 재생(뒤를 잘라 둠)
            media_ms = F.anim_len(slide)
            for c in slide._element.iter(F.q('p:cmd')):
                c.find(F.q('p:cBhvr')).find(F.q('p:cTn')).set('dur', str(round(hold * 1000)))
            for m in slide._element.iter('{%s}media' % P14):
                for old_trim in m.findall('{%s}trim' % P14):
                    m.remove(old_trim)
                if media_ms > hold * 1000 + 500:
                    etree.SubElement(m, '{%s}trim' % P14).set('end', str(round(media_ms - hold * 1000)))
        F.add_mark(slide, MARK_BOX, MARK_RGB[k % 3], 'mk_' + key)
        plan.append(dict(key=key, kind='foreign', marks=[k], leads=[LEADS.get(key, HW.LAT_START)], segs=[say_of[key]], secs=hold,
                         trans=F.trans_ms(slide) / 1000))
        order.append(slide)
        k += 1
    MK.drop_slides(prs, [s for s in old if s not in (cover, mg)])
    MK.reorder(prs, order)
    MK.samsung_fonts.remap_prs(prs)
    MK.logo_style(logos)
    prs.save(str(dst))
    return [p['secs'] for p in plan], plan


def expected(plan):
    """장마다 계산으로 어림한 시작 때(초): 앞 장들의 장 넘김 + 머무는 시간."""
    t, out = 0.0, []
    for p in plan:
        t += p['trans']
        out.append(t)
        t += p['secs']
    return out, t


# ------------------------------------------------------------------ 녹화에서 때 찾기
def _frames(mp4, vf, shape, t0=None, dur=None):
    cmd = [FFMPEG, '-loglevel', 'error']
    if t0 is not None:
        cmd += ['-ss', '%.3f' % t0, '-t', '%.3f' % dur]
    cmd += ['-i', str(mp4), '-vf', vf, '-f', 'rawvideo', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = int(np.prod(shape))
    return np.frombuffer(raw[:len(raw) // n * n], dtype=np.uint8).reshape((-1,) + shape)


def find_marks(mp4, plan, fps=30):
    """구간 표가 뜬 때(초)를 차례로 찾는다(표 색은 차례로 번갈아 바뀌므로, 앞에서부터 다음 색이 처음 고르게 뜨는 프레임).
    돌려줌: ([초], 못 찾아 어림으로 채운 개수)."""
    x, y, w, h = MARK_BOX
    cx, cy = int(x * 1.5 + 8) // 2 * 2, int(y * 1.5 + 3) // 2 * 2
    cw, ch = 48, 6
    fr = _frames(mp4, 'fps=%d,crop=%d:%d:%d:%d:exact=1,format=rgb24' % (fps, cw, ch, cx, cy), (ch, cw, 3)).reshape(-1, ch * cw, 3).mean(axis=1)
    target = np.array([[int(c[i:i + 2], 16) for i in (0, 2, 4)] for c in MARK_RGB], dtype=float)
    d = np.abs(fr[:, None, :] - target[None]).max(axis=2)
    code = np.where(d.min(axis=1) < 70, d.argmin(axis=1), -1)
    out, f, miss = [], 0, 0
    for k in range(sum(len(p['marks']) for p in plan)):
        hit = next((i for i in range(f, len(code) - 3) if (code[i:i + 3] == k % 3).all()), None)
        if hit is None:
            miss += 1
            hit = f
        out.append(hit / fps)
        f = hit + 1
    return out, miss


def find_video_start(silent, t_guess):
    """녹화 속에서 모션그래픽이 실제로 재생을 시작한 때(초): 원본과 녹화의 작은 흑백 프레임을 견주어 가장 잘 맞는 어긋남을 고른다."""
    vf = 'fps=30,scale=64:36,format=gray'
    a0 = max(t_guess - 3.0, 0)
    rec = _frames(silent, vf, (36, 64), a0, MG_LEN + 12).astype(np.float32)
    org = _frames(MG_MP4, vf, (36, 64)).astype(np.float32)
    idx = np.arange(60, len(org) - 60, 15)                  # 원본에서 0.5초마다 한 장
    best, best_lag = None, 0
    for lag in range(0, 30 * 10):
        j = idx + lag
        j = j[j < len(rec)]
        if len(j) < len(idx) * 0.9:
            break
        err = float(np.mean((rec[j] - org[idx[:len(j)]]) ** 2))
        if best is None or err < best:
            best, best_lag = err, lag
    return a0 + best_lag / 30, best


# ------------------------------------------------------------------ 자막
def sub_png(text, dst, pt=30, maxw=1620):
    """자막 한 장(1920×SUB_H, 투명 바탕): 어두운 둥근 판 위 흰 글. 긴 말은 폭에 맞춰 줄을 나눈다. How it Works 낭독 영상의 자막과 같은 모양."""
    font = ImageFont.truetype(str(FONT), pt)
    lines, cur = [], ''
    for w in text.split(' '):
        if cur and font.getlength(cur + ' ' + w) > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    lines.append(cur)
    lh = 39
    bw = int(max(font.getlength(ln) for ln in lines)) + 66
    bh = lh * len(lines) + 24
    im = Image.new('RGBA', (1920, SUB_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y0 = (1920 - bw) // 2, SUB_H - bh
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=18, fill=(28, 26, 36, 209))
    for i, ln in enumerate(lines):
        d.text((960, y0 + 12 + i * lh + lh / 2), ln, font=font, fill=(255, 255, 255, 255), anchor='mm')
    im.save(dst)


def sub_track(events, total, d):
    """events = [(시작 초, 끝 초, 글)] → 자막 그림들과 이어 붙일 차례표(ffmpeg concat). 돌려줌: 차례표 경로."""
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob('*'):
        f.unlink()
    blank = d / 'blank.png'
    Image.new('RGBA', (1920, SUB_H), (0, 0, 0, 0)).save(blank)
    lines, t = ['ffconcat version 1.0'], 0.0
    for i, (a, b, text) in enumerate(events):
        a = max(a, t)
        if b - a < 0.2:
            continue
        if a - t > 0.001:
            lines += ["file '%s'" % blank.name, 'duration %.3f' % (a - t)]
        png = d / ('s%04d.png' % i)
        sub_png(text, png)
        lines += ["file '%s'" % png.name, 'duration %.3f' % (b - a)]
        t = b
    lines += ["file '%s'" % blank.name, 'duration %.3f' % max(total - t, 0.1), "file '%s'" % blank.name]
    lst = d / 'subs.txt'
    lst.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return lst


# ------------------------------------------------------------------ 소리와 자막을 얹음
def finish(silent, mp4, plan, clips, tail=1.0):
    """녹화에 낭독, 자막, 모션그래픽 원본을 얹어 mp4로. 돌려줌: 장마다의 (키, 시작, 길이) 표."""
    cues = json.loads((OUT / 'tts' / '_cues.json').read_text(encoding='utf-8'))
    marks, miss = find_marks(silent, plan)
    vlen = HW.video_len(silent)
    cut = None                      # 표지가 계획보다 오래 머물렀으면(영상이 끝날 때까지 넘어가지 않음) 그만큼 잘라 내고 겹쳐 잇는다
    if plan[0]['key'] == 'cover' and len(marks) > 1:
        c0, c1 = marks[0] + plan[0]['secs'], marks[1] - plan[1]['trans'] - 0.35
        if c1 - c0 > 1.0:
            cut = (c0, c1)
            marks = [marks[0]] + [m - (c1 - c0) for m in marks[1:]]
            vlen -= c1 - c0
            print('표지: 계획보다 %.1f초 더 머물러 그만큼 잘라 냄' % (c1 - c0))
    shift = (cut[1] - cut[0]) if cut else 0.0
    it = iter(marks)
    place, events, starts = [], [], []
    for p in plan:
        ts = [next(it) for _ in p['marks']]
        ss = p.get('seg_secs') or []
        if len(ts) > 1 and ss and ts[1] - ts[0] < ss[0] - 0.3:
            # PowerPoint가 무거운 장을 그리느라 첫 효과(표 포함)를 늦게 띄운 때: 다음 클릭은 제때 오므로 첫 말이 뒤 말에 붙는다 → 첫 말은 계획한 때로 당김
            print('   %s: 첫 효과가 %.2f초 늦게 떠서 첫 말을 그만큼 당김' % (p['key'], ss[0] - (ts[1] - ts[0])))
            ts[0] = ts[1] - ss[0]
        starts.append(ts[0])
        for j, seg in enumerate(p['segs']):
            if not seg.strip():
                continue
            wav = clips[p['key']][j]
            s0 = ts[j] + p['leads'][j]
            place.append((wav, s0))
            pieces = cues['%s_%d' % (p['key'], j)]
            texts = disp_sents(seg)
            if len(texts) != len(pieces):           # 끊는 자리가 다르면 읽은 글 그대로
                print('   ! 자막 %s_%d: 문장 %d ≠ 낭독 토막 %d → 읽은 글로 띄움' % (p['key'], j, len(texts), len(pieces)))
                texts = [c['t'] for c in pieces]
            for c, text in zip(pieces, texts):
                events.append((s0 + c['at'], s0 + c['at'] + c['dur'] + 0.12, text))
    end = max(place[-1][1] + tts_c.wav_len(place[-1][0]) + tail, starts[-1] + plan[-1]['secs'] - 0.3)
    wav = OUT / '_voice.wav'
    tts_c.track(place, end, wav)
    subs = sub_track(events, end, OUT / 'subs')
    x, y, w, h = MARK_BOX
    W, Y = int(w * 1.5) + 9, int(y * 1.5) - 7
    H = 1080 - Y
    more = max(end - vlen, 0) + 0.2
    err = subprocess.run([FFMPEG, '-hide_banner', '-i', str(wav), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    gain = min(max(-16 - float(re.findall(r'I:\s+(-?[\d.]+) LUFS', err)[-1]), -6), 12)
    ins = ['-i', str(silent), '-i', str(wav), '-f', 'concat', '-safe', '0', '-i', str(subs)]
    if cut:
        xf = 0.4
        fc = ['[0:v]fps=30,split[xa][xb]', '[xa]trim=0:%.3f,setpts=PTS-STARTPTS[ca]' % (cut[0] + xf), '[xb]trim=start=%.3f,setpts=PTS-STARTPTS[cb]' % cut[1],
              '[ca][cb]xfade=transition=fade:duration=%.2f:offset=%.3f,tpad=stop_mode=clone:stop_duration=%.2f[v0]' % (xf, cut[0], more)]
    else:
        fc = ['[0:v]fps=30,tpad=stop_mode=clone:stop_duration=%.2f[v0]' % more]
    last = 'v0'
    audio = '[1:a]volume=%.2fdB,alimiter=limit=0.75:attack=3:release=40:level=false:latency=true,aformat=channel_layouts=stereo:sample_rates=44100[va]' % gain
    mgs = [(p, s) for p, s in zip(plan, starts) if p['kind'] == 'video']
    if mgs:
        p, s = mgs[0]
        t0, err_mg = find_video_start(silent, s + shift)
        t0 -= shift
        print('모션그래픽: 장이 열린 때 %.2f초, 재생이 시작한 때 %.2f초(화면 차이 %.1f)' % (s, t0, err_mg))
        t1 = min(t0 + MG_LEN + MG_TAIL - 0.5, starts[plan.index(p) + 1] - 0.05 if plan.index(p) + 1 < len(plan) else end)
        ins += ['-i', str(MG_MP4)]
        fc += ['[3:v]fps=30,scale=1920:1080:flags=lanczos,tpad=stop_mode=clone:stop_duration=%.2f,setpts=PTS-STARTPTS+%.3f/TB[mg]' % (MG_TAIL, t0),
               "[v0][mg]overlay=0:0:enable='between(t,%.3f,%.3f)':eof_action=pass[v1]" % (t0, t1)]
        last = 'v1'
        audio += (';[3:a]volume=%.2f,adelay=%d|%d,aformat=channel_layouts=stereo:sample_rates=44100[ma]'
                  ';[va][ma]amix=inputs=2:normalize=0:duration=longest[au]') % (MG_VOL, round(t0 * 1000), round(t0 * 1000))
        p['video_at'] = t0
    else:
        audio += ';[va]anull[au]'
    fc += ['[%s]split[a][b];[b]crop=%d:%d:0:%d[p];[a][p]overlay=0:%d[v2]' % (last, W, H, Y - H - 2, Y),
           '[2:v]fps=30,format=rgba[sub]', '[v2][sub]overlay=0:%d:eof_action=pass[v]' % (1065 - SUB_H), audio]
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', *ins, '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[au]', '-r', '30',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100',
                    '-t', '%.2f' % end, '-movflags', '+faststart', str(mp4)], check=True)
    wav.unlink()
    rows = []
    for i, p in enumerate(plan):
        a = starts[i] - p['trans'] if i else 0.0                # 그 장으로 넘어가기 시작한 때
        b = (starts[i + 1] - plan[i + 1]['trans']) if i + 1 < len(plan) else end
        rows.append((p['key'], round(a, 2), round(b - a, 2)))
    exp, _ = expected(plan)
    drift = max(abs(a - b) for a, b in zip(starts, exp))
    print('낭독을 넣음: 장 %d, 구간 %d, 표를 못 찾은 구간 %d, 계산한 때와 가장 크게 어긋난 곳 %.2f초, 영상 길이 %d:%04.1f, %.1f MB' % (
        len(plan), len(marks), miss, drift, end // 60, end % 60, mp4.stat().st_size / 1e6))
    return rows, end


# ------------------------------------------------------------------ 시간표
SECTIONS = [('표지와 인트로', lambda k: k == 'cover' or k.startswith('in') or k in ('hook', 'hub2', 'scat', 'link', 'bridge')),
            ('모션그래픽', lambda k: k == 'mg'),
            ('솔루션과 How it Works', lambda k: k in HW.SLIDE_KEYS),
            ('뒷부분', lambda k: True)]


def section_of(key):
    return next(name for name, f in SECTIONS if f(key))


def shrink(src, dst):
    """저장소에 올리는 확인용(1280×720). 1920×1080 원본은 out/에 남긴다."""
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', str(src), '-vf', 'scale=1280:720:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow',
                    '-crf', '24', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(dst)], check=True)
    print('확인용 %s %.1f MB (원본 %s %.1f MB)' % (dst.name, dst.stat().st_size / 1e6, src.name, src.stat().st_size / 1e6))


def report(rows, end, dst):
    """장마다, 구역마다 걸린 시간을 찍고 json으로 남긴다. rows = [(키, 시작, 길이)]."""
    sec = {}
    for key, a, d in rows:
        sec[section_of(key)] = sec.get(section_of(key), 0) + d
    print('\n%-3s %-9s %7s %7s' % ('쪽', '장', '시작', '길이'))
    for i, (key, a, d) in enumerate(rows, 1):
        print('%-3d %-9s %2d:%04.1f %6.1f초' % (i, key, a // 60, a % 60, d))
    print()
    for name, _ in SECTIONS:
        if name in sec:
            print('%-22s %d:%04.1f' % (name, sec[name] // 60, sec[name] % 60))
    print('%-22s %d:%04.1f' % ('모두', end // 60, end % 60))
    dst.write_text(json.dumps(dict(rows=rows, sections=sec, total=round(end, 2)), ensure_ascii=False, indent=1), encoding='utf-8')


def estimate(plan):
    """녹화 없이 어림한 시간표."""
    exp, total = expected(plan)
    rows = [(p['key'], round(e - p['trans'], 2), round(p['trans'] + p['secs'], 2)) for p, e in zip(plan, exp)]
    return rows, total


def seg_secs(plan, says):
    """새로 그린 장의 구간마다 걸리는 시간(표를 찾을 때 다음 구간의 때를 어림하는 데 씀)."""
    for p in plan:
        if p['kind'] == 'own':
            p['seg_secs'] = list(says.get(p['key']) or [END_HOLD] * len(p['marks']))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--remux', action='store_true')
    ap.add_argument('--time', action='store_true')
    ap.add_argument('--proposal', action='store_true')
    ap.add_argument('--new', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    part = 'proposal' if a.proposal else ('new' if a.new else None)
    tag = {'proposal': '_p', 'new': '_n', None: ''}[part]
    mp4 = {'proposal': MP4_P, 'new': OUT / '새장_미리보기.mp4', None: MP4}[part]
    silent, auto, meta = OUT / ('_silent%s.mp4' % tag), OUT / ('_auto%s.pptx' % tag), OUT / ('_talk%s.json' % tag)
    if a.remux and silent.exists() and meta.exists():
        m = json.loads(meta.read_text(encoding='utf-8'))
        plan, clips = m['plan'], {k: [Path(c) for c in v] for k, v in m['clips'].items()}
        assert all(c.exists() for v in clips.values() for c in v), '낭독 파일이 없음 → --remux 없이 다시'
    else:
        fu, says, clips = narrate_all(a.check)
        if not part:
            MK.build(MK.DST)                    # 낭독에 맞춘 효과의 때로 덱을 다시 만듦
        secs, plan = build_auto(auto, fu, says, part)
        seg_secs(plan, says)
        meta.write_text(json.dumps(dict(plan=plan, clips={k: [str(c) for c in v] for k, v in clips.items()}), ensure_ascii=False), encoding='utf-8')
        rows, total = estimate(plan)
        if a.time:
            report(rows, total, OUT / ('timing_estimate%s.json' % tag))
            return
        print('녹화: %d장, 어림 %d:%04.1f' % (len(secs), total // 60, total % 60))
        print(render_c.video(auto, silent, secs))
    full = OUT / (mp4.stem + '_1080p.mp4')
    rows, end = finish(silent, full, plan, clips)
    if part == 'new':
        shutil.copyfile(full, mp4)
    else:
        shrink(full, mp4)
    report(rows, end, OUT / ('timing%s.json' % tag))


if __name__ == '__main__':
    main()
