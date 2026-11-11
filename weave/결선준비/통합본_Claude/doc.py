#!/usr/bin/env python3
"""대본.md를 쓴다: 장마다 말할 글과 영상에서 잰 시간, 구역별 시간, 줄이는 순서(trim.py가 잰 값).

  python doc.py        (먼저 talk.py로 영상을, trim.py로 줄인 대본의 시간을 만들어 둠)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
NAME = {
    'cover': '표지', 'in02': '인트로 2 · "잠깐만요, 찾아보고 다시 알려 드릴게요."', 'in03': '인트로 3 · 막막한 순간 ①', 'in04': '인트로 4 · 막막한 순간 ②',
    'in05': '인트로 5 · 막막한 순간 ③', 'in06': '인트로 6 · 기록의 늪', 'in07': '인트로 7 · 설문 93.8%', 'in08': '인트로 8 · 설문 94.9%',
    'in09': '인트로 9 · 세상의 모든 지식은 AI에게 묻는데', 'in10': '인트로 10 · 정작 내 기록은', 'in11': '인트로 11 · 흩어진 기록', 'in12': '인트로 12 · 내 폰에 물을 순 없을까요',
    'bridge': '잇는 장 · Weave Assist (새로 그림)', 'mg': '모션그래픽 (말 없음)', 'sol1': '솔루션 ① 기록 통합 검색', 'sol2': '솔루션 ② 단서로 찾는 기억',
    'sol': '솔루션 ③ 먼저 건네는 기억', 'hiw': 'How it works?', 'ask': '질문', 'cloud': '흩어진 단서', 'old': '기존 검색이라면?', 'kw': '키워드 검색',
    'emb': '임베딩 검색', 'step': "Let's think step by step!", 'chain': '빠진 고리', 'idx': '00 데이터 색인', 'trig': '01 상황 인식', 'split': '02 질의 재작성',
    'hop1': '03 연쇄 탐색 (Hop 1)', 'hop2': '03 연쇄 탐색 (Hop 2)', 'deliver': '04 결과 제공', 'fx1': '기대효과 ①', 'fx2': '기대효과 ②', 'fx3': '기대효과 ③',
    'bi': '비즈니스 임팩트', 'cmp': '기존 기능과의 비교 (새로 그림)', 'tl': 'Why Now · Why Samsung 연표', 'end1': '마무리 ① 인용', 'end2': "마무리 ② '순간'",
    'end3': '마무리 ③ 문장', 'endlogo': '끝 화면',
}
SECTION = [('표지와 인트로', 'cover', 'bridge'), ('모션그래픽', 'mg', 'mg'), ('솔루션과 How it Works', 'sol1', 'deliver'), ('뒷부분', 'fx1', 'endlogo')]


def mmss(t):
    return '%d분 %04.1f초' % (t // 60, t % 60) if t >= 60 else '%.1f초' % t


def main():
    tm = json.loads((OUT / 'timing.json').read_text(encoding='utf-8'))
    plan = json.loads((OUT / '_talk.json').read_text(encoding='utf-8'))['plan']
    trim = json.loads((OUT / 'trim.json').read_text(encoding='utf-8'))
    say = {p['key']: ' (클릭) '.join(' '.join(s.split()) for s in p['segs']) for p in plan}
    rows = tm['rows']
    keys = [r[0] for r in rows]
    L = ['# Weave 통합본(Claude) 대본과 시간', '',
         '`Weave_통합본_Claude_미리보기.mp4`에서 잰 시간이에요. 낭독은 이 컴퓨터 안에서 만든 목소리(Supertonic 3, F2F1_70, 속도 1.15)이고, '
         '문장 사이 숨과 클릭 전후의 틈은 How it Works 낭독 영상과 같은 값이에요.', '',
         '## 구역별 시간', '', '| 구역 | 쪽 | 시간 |', '| --- | --- | --- |']
    for name, a, b in SECTION:
        i, j = keys.index(a), keys.index(b)
        L.append('| %s | %s | %s |' % (name, '%d' % (i + 1) if i == j else '%d~%d' % (i + 1, j + 1), mmss(sum(r[2] for r in rows[i:j + 1]))))
    L += ['| **모두** | 1~%d | **%s** |' % (len(rows), mmss(tm['total'])), '',
          '## 장마다 말할 글과 시간', '',
          '(클릭)은 그 자리에서 클릭이에요. 인트로 2~12쪽은 효과가 저절로 나와서 클릭이 없어요. 인트로의 글은 팀원 노트에서 괄호 속 지시만 뺀 것이에요.', '',
          '| 쪽 | 장 | 말할 글 | 시작 | 길이 |', '| --- | --- | --- | --- | --- |']
    for i, (k, a, d) in enumerate(rows, 1):
        L.append('| %d | %s | %s | %d:%02d | %.1f초 |' % (i, NAME.get(k, k), say.get(k) or '—', a // 60, a % 60, d))
    L += ['', '## 줄이는 순서', '',
          '줄인 문장을 같은 목소리로 낭독해서 잰 값이에요(`trim.py`). 위에서부터 차례로 적용해요. 될 수 있으면 문장을 통째로 빼고, 남긴 문장은 그대로 뒀어요.', '',
          '| 순서 | 줄이는 곳 | 줄어드는 시간 | 여기까지 줄이면 |', '| --- | --- | --- | --- |']
    for g in trim['groups']:
        L.append('| %d | %s | %.1f초 | %s |' % (g['n'], g['name'], g['cut'], mmss(g['left'])))
    L += ['']
    for g in trim['groups']:
        L += ['### %d. %s' % (g['n'], g['name']), '', '| 장 | 지금 | 줄인 뒤 | 줄인 글 |', '| --- | --- | --- | --- |']
        for x in g['slides']:
            L.append('| %s | %.1f초 | %.1f초 | %s |' % (NAME.get(x['key'], x['key']), x['now'], x['after'], ' '.join(g['text'][x['key']].split())))
        L.append('')
    L += (HERE / '대본_덧붙임.md').read_text(encoding='utf-8').rstrip('\n').split('\n') + ['']
    (HERE / '대본.md').write_text('\n'.join(L), encoding='utf-8')
    print('→ 대본.md', len(L), '줄')


if __name__ == '__main__':
    main()
