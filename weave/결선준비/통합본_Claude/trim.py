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
GROUPS = [   # (차례, 이름, {장: 줄인 글})
    (1, '솔루션 세 장은 이름만(모션그래픽에서 방금 본 장면)', {
        'sol1': '방금 영상에서 보신 세 가지 기능을 정리해 보겠습니다. 첫 번째는 (클릭) 기록 통합 검색입니다.',
        'sol2': '두 번째는 단서로 찾는 기억입니다.',
        'sol': '세 번째는 먼저 건네는 기억입니다.',
    }),
    (2, '인트로 3~5쪽: 세 순간은 이름만', {
        'in03': '저희는 이러한 순간을 크게 세 가지로 나눌 수 있었습니다. 첫째, 어디에 있는지 모를 때입니다.',
        'in04': '둘째, 이름이 떠오르지 않을 때입니다.',
        'in05': '셋째, 기억조차 나지 않을 때입니다. 세 순간 모두, 필요한 기록은 이미 내 휴대폰 안에 있습니다.',
    }),
    (3, '인트로 6쪽과 11쪽: 화면과 겹치는 문장을 뺌', {
        'hook': ('우리는 매일 셀 수 없이 많은 기록을 남깁니다. (클릭) 카톡 대화, (클릭) 사진, (클릭) 메모, (클릭) 일정, (클릭) 메일까지. '
                 '(클릭) 수많은 기억 속에서, 지금 필요한 기억을 찾아 헤맵니다.'),
        'scat': "'왜 정작 나에 대한 모든 기록이 담긴 내 휴대폰 안에서는, 아직도 이렇게 찾아 헤매야 할까요?'",
    }),
    (4, '비교 장: 첫 물음을 뺌', {
        'cmp': ('Writing Assist는 지금 쓰는 글을 다듬고, 카나나는 카카오톡 대화 안에서, Now Nudge와 Finder는 더 넓은 범위에서 한 번 찾거나 제안합니다. '
                '(클릭) Weave는 여러 앱에 흩어진 단서를 이어서 찾고, 쓰던 화면의 키보드 위에서 바로 건넵니다.'),
    }),
    (5, '비교 장을 Appendix로 옮김(질문이 나오면 꺼냄)', {'cmp': None}),      # None = 그 장을 본 발표에서 뺌
]


def main():
    f = OUT / 'timing.json'
    how = '영상에서 잼'
    if not f.exists():
        f, how = OUT / 'timing_estimate.json', '어림'
    now = {k: d for k, a, d in json.loads(f.read_text(encoding='utf-8'))['rows']}
    total = json.loads(f.read_text(encoding='utf-8'))['total']
    own = {sp.key: sp for name, specs in talk.own_specs().items() for sp in specs}      # 지금 낭독에 맞춘 효과 길이
    fu = {k: say for k, _, say in talk.foreign_units()}
    src = list(talk.Presentation(str(MK.INTRO)).slides)
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
        else:                                       # 옮겨 온 장: 장 넘김 + max(말, 저절로 나오는 효과)
            sl = src[int(k[2:]) - 1]
            lead = talk.LEADS.get(k, HW.LAT_START)
            hold = lead + tts_c.wav_len(clips[p.key][0]) + HW.seg_gaps(p)[0]
            sec = F.trans_ms(sl) / 1000 + max(hold, F.anim_len(sl) / 1000 + 0.3)
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
