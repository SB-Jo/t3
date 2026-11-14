#!/usr/bin/env python3
"""대본.md를 쓴다: 장마다 말할 글과 영상에서 잰 시간, 구역별 시간, 더 줄일 곳(trim.py가 잰 값), 바꾼 곳, 이전 대본.

  python doc.py        (먼저 talk.py로 영상을, trim.py로 더 줄인 대본의 시간을 만들어 둠)
"""
import json
from pathlib import Path

import make as MK

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
N = MK.N
NAME = {
    'cover': '표지', 'in02': '인트로 2 · "잠깐만요, 찾아보고 다시 알려 드릴게요."', 'in03': '인트로 3 · 막막한 순간 ①', 'in04': '인트로 4 · 막막한 순간 ②',
    'in05': '인트로 5 · 막막한 순간 ③', 'hook': '인트로 6 · 수많은 기록 (새로 그림)', 'in07': '인트로 7 · 설문 93.8%', 'in08': '인트로 8 · 설문 94.9%',
    'hub2': '인트로 9 · 기록을 남기는 곳', 'in09': '인트로 10 · 세상의 모든 지식은 AI에게 묻는데', 'scat': '인트로 11 · 정작 내 기록은',
    'gath': '인트로 12 · 기록 그림이 가운데로 (8차에 나눈 장)', 'link': '인트로 13 · 흩어진 기록이 이어짐', 'in12': '인트로 14 · 내 휴대폰에게 물을 순 없을까요',
    'bridge': '잇는 장 · Weave Assist',
    'mg': '모션그래픽 (말 없음)', 'sol1': '솔루션 ① 기록 통합 검색', 'sol2': '솔루션 ② 단서로 찾는 기억',
    'sol': '솔루션 ③ 먼저 건네는 기억', 'hiw': 'How it works?', 'ask': '질문', 'old': '기존 검색이라면?', 'kw': '키워드 검색',
    'emb': '임베딩 검색', 'step': "Let's think step by step!", 'chain': '중간 단서', 'idx': '00 데이터 색인', 'trig': '01 상황 인식', 'split': '02 질의 재작성',
    'hop1': '03 연쇄 탐색 (Hop 1)', 'hop2': '03 연쇄 탐색 (Hop 2)', 'deliver': '04 결과 제공', 'fx': '기대효과 (AS-IS → TO-BE)',
    'fx1': '기대효과 ①', 'fx2': '기대효과 ②', 'fx3': '기대효과 ③',
    'bi': '비즈니스 임팩트', 'cmp': '기존 기능과의 비교 (찾는 범위와 깊이)', 'tl': 'Why Now · Why Samsung 연표', 'end1': '마무리 ① 인용', 'end2': "마무리 ② '순간'",
    'end3': '마무리 ③ 문장', 'bye': '맺는 장 (아이콘과 Weave)',
    'p_fx1': '제안 · 기대효과 ①', 'p_fx2': '제안 · 기대효과 ②', 'p_fx3': '제안 · 기대효과 ③',
}
SECTION = [('표지와 인트로', 'cover', 'bridge'), ('모션그래픽', 'mg', 'mg'), ('솔루션과 How it Works', 'sol1', 'deliver'), ('뒷부분', 'fx', 'bye')]
PREV = {'표지와 인트로': '2분 52.1초', '모션그래픽': '1분 52.8초', '솔루션과 How it Works': '3분 36.1초', '뒷부분': '2분 17.7초', '모두': '10분 38.7초'}      # 7차(11월 13일 아침, 39장)


def mmss(t):
    return '%d분 %04.1f초' % (t // 60, t % 60) if t >= 60 else '%.1f초' % t


def flat(t):
    return ' '.join(t.split())


def main():
    tm = json.loads((OUT / 'timing.json').read_text(encoding='utf-8'))
    plan = json.loads((OUT / '_talk.json').read_text(encoding='utf-8'))['plan']
    say = {p['key']: ' (클릭) '.join(flat(s) for s in p['segs']) for p in plan}
    rows = tm['rows']
    keys = [r[0] for r in rows]
    L = ['# Weave 통합본(Claude) 대본과 시간 (8차)', '',
         '`Weave_통합본_Claude_미리보기.mp4`에서 잰 시간이에요. 낭독은 이 컴퓨터 안에서 만든 목소리(Supertonic 3, F2F1_70, 속도 1.15)이고, '
         '문장 사이 숨과 클릭 전후의 틈은 How it Works 낭독 영상과 같은 값이에요.', '',
         '## 구역별 시간', '', '| 구역 | 쪽 | 시간 | 7차 때 |', '| --- | --- | --- | --- |']
    for name, a, b in SECTION:
        i, j = keys.index(a), keys.index(b)
        L.append('| %s | %s | %s | %s |' % (name, '%d' % (i + 1) if i == j else '%d~%d' % (i + 1, j + 1), mmss(sum(r[2] for r in rows[i:j + 1])), PREV[name]))
    L += ['| **모두** | 1~%d | **%s** | %s |' % (len(rows), mmss(tm['total']), PREV['모두']), '',
          '## 장마다 말할 글과 시간', '',
          '(클릭)은 그 자리에서 클릭이에요. 옮겨 온 인트로 장(2~5쪽, 7~15쪽)은 효과가 저절로 나와서 클릭이 없어요. 3쪽만 한 번 눌러요: '
          '장이 열리면 옅은 기록 조각만 떠다니고, 클릭하면 첫 인물과 말풍선이 떠요. '
          '6쪽은 장이 열리면 검색 화면이 "검색 결과가 없습니다"를 띄우는 3초 동안 말없이 기다렸다가, 화면이 물러나며 벽이 드러날 때 말을 시작하고, '
          '"카톡 대화, 사진, 메모, 일정, 메일까지"는 쉼표마다 한 번씩 클릭해요. '
          '11쪽에서 12쪽으로 넘기면 기록 그림만 가운데로 옮겨 오고, 13쪽으로 넘기면 기록이 반듯해지며 이어져요. '
          '23쪽은 네 번 눌러요: 결과 셋, ✕ 셋, 그날 사진, 사진의 ✕. '
          '33쪽은 "Weave는 이러한 불편함을 해결합니다."에서 한 번, 그 뒤로 기능마다 한 번씩 눌러요. '
          '앞 칸의 숫자가 다 줄기 전에 다음 클릭을 눌러도 효과가 끊기지 않고 이어져요. '
          '35쪽은 클릭하면 그 줄의 마디 넷이 한꺼번에 떠요.', '',
          '| 쪽 | 장 | 말할 글 | 시작 | 길이 |', '| --- | --- | --- | --- | --- |']
    for i, (k, a, d) in enumerate(rows, 1):
        L.append('| %d | %s | %s | %d:%02d | %.1f초 |' % (i, NAME.get(k, k), say.get(k) or '—', a // 60, a % 60, d))
    L += ['']
    L += (HERE / '대본_덧붙임.md').read_text(encoding='utf-8').rstrip('\n').split('\n') + ['']
    f = OUT / 'trim.json'
    if f.exists():
        trim = json.loads(f.read_text(encoding='utf-8'))
        L += ['## 10분 안으로 줄여야 할 때', '',
              '지금 길이에서 덜어 낼 곳을 차례로 적고, 같은 목소리로 낭독해 쟀어요(`trim.py`).', '',
              '| 순서 | 줄이는 곳 | 줄어드는 시간 | 여기까지 줄이면 |', '| --- | --- | --- | --- |']
        for g in trim['groups']:
            L.append('| %d | %s | %.1f초 | %s |' % (g['n'], g['name'], g['cut'], mmss(g['left'])))
        L += ['']
        for g in trim['groups']:
            L += ['### %d. %s' % (g['n'], g['name']), '', '| 장 | 지금 | 줄인 뒤 | 줄인 글 |', '| --- | --- | --- | --- |']
            for x in g['slides']:
                txt = g['text'][x['key']]
                L.append('| %s | %.1f초 | %.1f초 | %s |' % (NAME.get(x['key'], x['key']), x['now'], x['after'],
                                                           flat(txt) if txt else '(본 발표에서 뺌)'))
            L.append('')
    if N.SLIDES_PROPOSAL:           # 6차부터 제안 장표 묶음은 없음
        L += ['## 제안 장표에서 할 말', '', '덱 뒤쪽 제안 장표의 노트예요(`제안장표_미리보기.mp4`).', '']
        f = OUT / 'timing_p.json'
        tp = {k: d for k, a, d in json.loads(f.read_text(encoding='utf-8'))['rows']} if f.exists() else {}
        L += ['| 장 | 말할 글 | 길이 |', '| --- | --- | --- |']
        for k in ('p_fx1', 'p_fx2', 'p_fx3'):
            L.append('| %s | %s | %s |' % (NAME[k], flat(N.NOTES[k]), ('%.1f초' % tp[k]) if k in tp else '—'))
        L += ['']
    L += (HERE / '대본_이전판.md').read_text(encoding='utf-8').rstrip('\n').split('\n') + ['']
    (HERE / '대본.md').write_text('\n'.join(L), encoding='utf-8')
    print('→ 대본.md', len(L), '줄')


if __name__ == '__main__':
    main()
