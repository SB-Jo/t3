#!/usr/bin/env python3
"""줄인 대본 안의 시간을 잰다: 줄인 문장을 같은 목소리로 낭독해 장마다 걸리는 시간을 지금 대본과 견준다.

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

# 줄인 대본 안. 될 수 있으면 문장을 통째로 빼고, 남긴 문장은 그대로 둠. (클릭)은 그 자리에서 클릭.
# 위에서부터 차례로 적용한다(뒤 묶음이 앞 묶음에서 줄인 장을 한 번 더 줄이기도 함).
GROUPS = [   # (차례, 이름, {장: 줄인 글})
    (1, '인트로 3~5쪽: 세 순간의 사례 설명을 뺌(바로 뒤 모션그래픽이 같은 세 장면을 보여 줌)', {
        'in03': '저희는 이런 막막한 순간을 세 가지로 나눠 보았습니다. 첫째, 어디에 있는지 모를 때입니다. 찾을 내용은 분명한데 어느 앱에 남겼는지 모릅니다.',
        'in04': '둘째, 이름이 떠오르지 않을 때입니다. 그날의 장면은 선명한데, 검색할 정확한 단어가 없습니다.',
        'in05': ('셋째, 기억조차 나지 않을 때입니다. 가족이 지나가듯 말한 부탁이나 작은 약속은 대화방에 그대로 남아 있지만, 정작 챙겨야 할 순간에는 떠오르지 않습니다. '
                 '세 순간 모두, 필요한 기록은 이미 내 휴대폰 안에 있습니다.'),
    }),
    (2, '뒷부분 기대효과 세 장과 비교 장: 인트로에서 말한 설문 숫자는 화면에 맡김', {
        'fx1': '저희 설문에서 응답자의 83.8%는 어느 앱에 남겼는지 몰라 앱을 하나씩 열어 봤다고 답했습니다. (클릭) 기록 통합 검색이 이 헤매는 시간을 줄여 줍니다.',
        'fx2': '93.8%는 이름이 떠오르지 않아 검색으로 바로 찾지 못했습니다. (클릭) 단서로 찾는 기억은 기억나는 상황만으로 찾아 줍니다.',
        'fx3': '82.4%는 부탁이나 약속을 나중에야 떠올렸습니다. (클릭) 먼저 건네는 기억이 묻기 전에 먼저 알려 줍니다.',
        'cmp': ('그렇다면 이미 있는 기능과는 무엇이 다를까요? Finder와 Now Nudge, 카나나는 정해진 범위 안에서 한 번 찾거나 제안합니다. '
                '(클릭) Weave는 여러 앱에 흩어진 단서를 이어서 찾고, 쓰던 화면의 키보드 위에서 바로 건넵니다.'),
    }),
    (3, '인트로 7~8쪽: 설문 두 장은 숫자와 결론만', {
        'in07': '이건 저희만의 이야기가 아니었습니다. 설문 응답자 210명 가운데 93.8%가 정확한 이름이 떠오르지 않아 검색으로 바로 찾지 못한 적이 있다고 답했습니다.',
        'in08': '그리고 그 가운데 94.9%는 단서가 될 다른 기록부터 차례로 찾아봤다고 답했습니다. 결국 사람이 직접 기억의 단서를 잡고 여러 앱을 뒤지고 있었던 겁니다.',
    }),
    (4, '인트로 6쪽, 10~11쪽: 되풀이되는 문장을 뺌', {
        'in06': ('우리는 매일 셀 수 없이 많은 기록을 남깁니다. 그런데 그중 단 하나가 필요한 순간, 단순 검색은 아무것도 찾아 주지 못하고, '
                 '우리는 단서를 쫓아 이 앱 저 앱을 직접 헤매기 시작합니다. (쉼) 저희는 바로 이 문제에서 출발했습니다.'),
        'in10': "'왜 정작 나에 대한 모든 기록이 담긴 내 휴대폰 안에서는, 아직도 이렇게 찾아 헤매야 할까요?' 대화도, 메모도, 사진도 사라진 게 아닙니다.",
        'in11': "그저 여러 앱에 파편처럼 흩어져 있을 뿐이죠. 앱마다 흩어져 있는 어제의 기록들을 하나로 엮어, 오늘의 나에게 데려와 줄 '연결고리'가 없었을 뿐입니다.",
    }),
    (5, '인트로 2쪽, 잇는 장, 비즈니스 임팩트, 연표: 문장 다듬기', {
        'in02': "여러분, 통화하다가 이런 말 해 보신 적 있으시죠. '잠깐만요, 찾아보고 다시 알려 드릴게요.' 저희가 210명에게 물었더니, 열 명 중 아홉 명이 이 말을 해 봤다고 답했습니다.",
        'bridge': ("그래서 오늘, 우리는 흩어진 나의 기억들과 지금의 나를 이어 줄 새로운 연결고리, 'Weave Assist'를 제안합니다. "
                   '(클릭) 내가 매일 쓰는 키보드 위 실타래 버튼 하나로 흩어진 기억의 단서들을 엮어 필요한 순간 건네주는 온디바이스 AI입니다.'),
        'bi': ('스마트폰 사용자는 한 달에 평균 41개의 앱을 씁니다. (클릭) 그리고 69%는 기록을 지우지 않고 쌓아 둔다고 답했습니다. '
               '(클릭) 이렇게 흩어지고 쌓인 기록을 갤럭시 안의 Weave가 하나로 엮습니다. 그래서 쓸수록 쌓이고 갤럭시를 떠나기 어려워집니다.'),
        'tl': ('이 경험이 갤럭시에서, 그리고 지금 가능한 이유입니다. (클릭) 검색 기술은 지난해부터 추론하며 단서를 이어 찾는 단계까지 왔고, '
               '(클릭) 갤럭시는 매일 쓰는 키보드 위에 Galaxy AI와 개인 데이터 엔진을 갖췄습니다. (클릭) 두 흐름이 만나는 지금이, Weave를 시작할 때입니다.'),
    }),
    (6, '그래도 모자랄 때: 세 순간은 이름만, 마무리는 한 문장씩', {
        'in03': '저희는 이런 막막한 순간을 세 가지로 나눠 보았습니다. 첫째, 어디에 있는지 모를 때입니다.',
        'in04': '둘째, 이름이 떠오르지 않을 때입니다.',
        'in05': '셋째, 기억조차 나지 않을 때입니다. 세 순간 모두, 필요한 기록은 이미 내 휴대폰 안에 있습니다.',
        'end1': '당신이 사랑하는 모든 것에 더 가까이 다가가고, 오래도록 이야기하게 될 순간을 담아보세요.',
        'end3': '갤럭시의 모든 순간이 다시 이야기가 되도록, Weave가 이어 가겠습니다. 감사합니다.',
    }),
    (7, '중간까지 손대도 된다면: 솔루션 세 장은 이름만(모션그래픽에서 본 장면)', {
        'sol1': '방금 보신 첫 번째 장면은 (클릭) 기록 통합 검색입니다.',
        'sol2': '두 번째는 단서로 찾는 기억입니다.',
        'sol': '세 번째는 먼저 건네는 기억입니다.',
    }),
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
    proxies = [types.SimpleNamespace(key='g%d_%s' % (n, k), slide=k, notes=v) for n, _, d in GROUPS for k, v in d.items()]
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
            a = after['g%d_%s' % (n, k)]
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
