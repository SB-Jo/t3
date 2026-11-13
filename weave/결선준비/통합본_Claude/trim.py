#!/usr/bin/env python3
"""더 줄인 대본 안의 시간을 잰다: 줄인 문장을 같은 목소리로 낭독해 장마다 걸리는 시간을 지금 대본과 견준다.

  python trim.py            → 장마다 지금 / 줄인 뒤 / 줄어든 초, 묶음마다의 합(out/trim.json)

낭독은 영상과 같은 방식(문장마다 따로 읽고 사이에 숨, 말 떼기 전후의 틈)이라 숫자를 그대로 견줄 수 있다.
지금 대본의 시간은 녹화한 영상에서 잰 값(out/timing.json)이 있으면 그것을, 없으면 어림(out/timing_estimate.json)을 쓴다.
"""
import json
import shutil
import types
from pathlib import Path

import make as MK

HW, F, N = MK.HW, MK.F, MK.N
import talk  # noqa: E402
import tts_c  # noqa: E402

OUT = MK.OUT
TMP = OUT / '_trim'

# 10분 안으로 줄여야 할 때의 안. 될 수 있으면 문장을 통째로 빼고, 남긴 문장은 그대로 둠.
# (클릭)은 그 자리에서 클릭. 위에서부터 차례로 적용한다.
# 8차(11-13 낮): 발표자가 다시 쓴 대본과 비교 장을 Appendix로 옮긴 덱이 9분 39초쯤이라(목표 9분 30초 ~ 10분) 줄이는 안을 두지 않는다.
#   7차까지의 안 여섯(솔루션 세 장은 이름만, 인트로 3~5쪽은 이름만, 6쪽과 11쪽의 겹치는 문장, 비교 장의 첫 물음, 2쪽 둘째 문장, 연표의 여는 말)은
#   그때의 대본을 줄인 글이라 지금 대본에는 맞지 않는다(git 기록의 e0a4e14에 있음). 더 줄일 일이 생기면 아래에 (차례, 이름, {장: 줄인 글})을 적는다.
GROUPS = []


def main():
    if not GROUPS:                                  # 줄이는 안이 없으면 예전 결과도 치움(doc.py가 그 절을 쓰지 않게)
        (OUT / 'trim.json').unlink(missing_ok=True)
        print('줄이는 안이 없음(GROUPS) → out/trim.json을 치움')
        return
    f = OUT / 'timing.json'
    how = '영상에서 잼'
    if not f.exists():
        f, how = OUT / 'timing_estimate.json', '어림'
    now = {k: d for k, a, d in json.loads(f.read_text(encoding='utf-8'))['rows']}
    total = json.loads(f.read_text(encoding='utf-8'))['total']
    own = {sp.key: sp for name, specs in talk.own_specs().items() for sp in specs}      # 지금 낭독에 맞춘 효과 길이
    fu = {k: say for k, _, say in talk.foreign_units()}
    deck = list(talk.Presentation(str(MK.DST)).slides)      # 지금 덱(옮겨 온 장을 손본 뒤의 모습)에서 효과 길이를 잼
    page = {k: i for i, k in enumerate(now)}                # 장 키 → 덱에서의 차례
    HW.OUT = TMP                                    # 낭독은 따로 둔 폴더에(영상용 낭독을 건드리지 않음)
    TMP.mkdir(parents=True, exist_ok=True)
    proxies = [types.SimpleNamespace(key='g%d_%s' % (n, k), slide=k, notes=v) for n, _, d in GROUPS for k, v in d.items() if v is not None]
    for p in proxies:                               # 말없이 화면을 먼저 보여 주는 장(6쪽)은 그 시간을 그대로
        if (p.slide, 0) in HW.LEAD_EXTRA:
            HW.LEAD_EXTRA[(p.key, 0)] = HW.LEAD_EXTRA[(p.slide, 0)]
    says, clips = HW.narrate(proxies)
    HW.OUT = OUT
    after = {}
    for p in proxies:
        k = p.slide
        if k in own:                                # 새로 그린 장: 구간마다 max(말, 효과) + 장 넘김
            sp = own[k]
            anim = [HW._group_len(g) / 1000 for g in sp.groups]
            sec = (sp.trans[1] / 1000 if sp.trans else 0) + 0.15
            for j, t in enumerate(says[p.key]):
                sec += max(t, anim[j] if j < len(anim) else 0)
        else:                                       # 옮겨 온 장: 장 넘김 + 구간마다 max(말, 그 구간의 효과). 클릭이 있는 장(3쪽)은 구간이 둘
            sl = deck[page[k]]
            say = [talk.LEADS.get(k, HW.LAT_START) + tts_c.wav_len(clips[p.key][0]) + HW.seg_gaps(p)[0]] + list(says[p.key][1:])
            clicks = F.click_lens(sl)
            assert len(clicks) == len(say) - 1, (k, len(clicks), len(say))
            sec = F.trans_ms(sl) / 1000 + max(say[0], F.anim_len(sl) / 1000 + (0 if clicks else 0.3))
            sec += sum(max(say[j + 1], ms / 1000 + (0.3 if j == len(clicks) - 1 else 0)) for j, ms in enumerate(clicks))
        after[p.key] = round(sec, 1)
    shutil.rmtree(TMP, ignore_errors=True)
    print('지금 대본의 시간: %s (%d:%04.1f)\n' % (how, total // 60, total % 60))
    left, rows, cur = total, [], dict(now)
    for n, name, d in GROUPS:
        slides = []
        for k in d:
            a = 0.0 if d[k] is None else after['g%d_%s' % (n, k)]
            slides.append(dict(key=k, now=cur[k], after=a))
            cur[k] = a
        cut = sum(x['now'] - x['after'] for x in slides)
        left -= cut
        rows.append(dict(n=n, name=name, cut=round(cut, 1), left=round(left, 1), slides=slides, text=d))
        print('%d. %s' % (n, name))
        for x in slides:
            print('     %-7s %5.1f초 → %5.1f초  (-%.1f)' % (x['key'], x['now'], x['after'], x['now'] - x['after']))
        print('     줄어드는 시간 %.1f초 → 여기까지 줄이면 %d:%04.1f\n' % (cut, left // 60, left % 60))
    (OUT / 'trim.json').write_text(json.dumps(dict(total=total, how=how, groups=rows), ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
