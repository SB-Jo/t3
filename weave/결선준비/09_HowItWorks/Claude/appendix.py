"""Appendix(Claude판, 2026-11-08 전면 수정): Q&A에 띄우는 장. How it Works와 같은 바탕·카드·글꼴.

근거는 리서치_Appendix근거.md(PDE 논문, Apple 발표, HippoRAG 오류 분석)와 기존 덱의 검증된 출처만 쓴다.
본문은 임원이 읽는 말로 쓰고, RDFox·OWL·트리플 같은 용어는 각주에만 둔다.
"""
from build import (AS, BLUE, BLUE_BG, PH, QUERY, Slide)
from ui import (BODY, ICON, INK, LAV, LAV2, LINE, LINE2, MUTE, PURPLE, PURPLE2, RED, RING, SUB, SHADOW_CARD, SHADOW_SOFT, C, P, R, T,
                caption, chip, crop_fit, line, numdot, scurve, thread, tw)

GRAY = '8E88A0'


def apx_badge(s):
    cw = tw('APPENDIX', 10.5, 'sb') + 32
    s.add('apx/badge', [T('apx/badge', 40, 22, cw, 28, 'APPENDIX', size=10.5, color='FFFFFF', weight='sb', align='c', anchor='ctr',
                          spc=0.5, fill=PURPLE, radius=14)])


def head(s, title_runs, sub=None, y=60, size=24):
    apx_badge(s)
    s.add('apx/title', [caption('apx/title', [title_runs], 640, y, size=size)])
    if sub:
        s.add('apx/sub', [T('apx/sub', 140, y + size * 1.42 + 6, 1000, 24, sub, size=13, color=SUB, align='c')])


def foot(s, text, y=690):
    s.add('apx/foot', [T('apx/foot', 50, y, 1180, 34, text, size=8.5, color=GRAY, wrap=True, lnspc=12)])


def cell(name, x, y, w, h, text, size=11.5, color=INK, weight='r', align='l', lh=None):
    lines = text if isinstance(text, list) else [text]
    lh = lh or size * 1.33 * 1.32
    th = lh * len(lines)
    return T(name, x, y + (h - th) / 2, w, th + 4, lines, size=size, color=color, weight=weight, align=align, lnspc=lh * 0.75)


def table(s, key, x, y, cols, header, rows, row_h=70, hi=None, pt=11.5, head_pt=11, first_bold=True):
    """카드 표. cols = 칸 폭 목록, rows = [[칸 글(문자열이나 줄 목록)]]. hi = 강조할 줄 번호."""
    w = sum(cols)
    hh = 40
    h = hh + row_h * len(rows)
    out = [R(key + '/bg', x, y, w, h, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=SHADOW_CARD),
           R(key + '/hd', x + 1, y + 1, w - 2, hh, prst='roundRect', radius=19, fill=LAV, line=None),
           R(key + '/hd2', x + 1, y + hh - 18, w - 2, 18, fill=LAV, line=None)]
    cx = x
    for j, (cw, t) in enumerate(zip(cols, header)):
        out.append(cell(key + '/h%d' % j, cx + 18, y, cw - 26, hh, t, size=head_pt, color=PURPLE, weight='b'))
        cx += cw
    for i, row in enumerate(rows):
        ry = y + hh + i * row_h
        if hi is not None and i == hi:
            out.append(R(key + '/hi', x + 6, ry + 4, w - 12, row_h - 8, prst='roundRect', radius=14, fill=LAV2, line=RING, line_w=1.6))
        if i:
            out.append(R(key + '/sep%d' % i, x + 16, ry, w - 32, 1, fill='EEE9F8', line=None))
        cx = x
        for j, (cw, t) in enumerate(zip(cols, row)):
            wt = 'b' if (j == 0 and first_bold) else 'r'
            col = INK if j == 0 else BODY
            if hi is not None and i == hi and j == 0:
                col = PURPLE
            out.append(cell(key + '/c%d_%d' % (i, j), cx + 18, ry, cw - 28, row_h, t, size=pt, color=col, weight=wt))
            cx += cw
    s.add(key, out)
    return h


def qcard(s, key, x, y, w, h, q, a_lines, sub_lines=None, pt=12):
    out = [R(key + '/bg', x, y, w, h, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=SHADOW_CARD),
           T(key + '/q', x + 22, y + 18, w - 44, 26, q, size=14, color=PURPLE, weight='b')]
    lh = pt * 1.33 * 1.4
    out.append(T(key + '/a', x + 22, y + 56, w - 44, lh * len(a_lines) + 6, a_lines, size=pt, color=INK, lnspc=lh * 0.75))
    if sub_lines:
        sy = y + 56 + lh * len(a_lines) + 14
        out.append(R(key + '/sbg', x + 16, sy, w - 32, (pt - 1.5) * 1.33 * 1.4 * len(sub_lines) + 22, prst='roundRect', radius=12,
                     fill='F7F5FC', line=None))
        out.append(T(key + '/s', x + 30, sy + 11, w - 60, (pt - 1.5) * 1.33 * 1.4 * len(sub_lines) + 4, sub_lines, size=pt - 1.5,
                     color=SUB, lnspc=(pt - 1.5) * 1.33 * 1.4 * 0.75))
    s.add(key, out)


# ------------------------------------------------------------------ 장
def a_divider():
    s = Slide('apx0', trans=('fade', 500), bar=False,
              notes='여기부터는 질문에 답할 때 띄우는 Appendix입니다. 본 발표에서는 넘기지 않습니다.')
    apx_badge(s)
    s.add('apx/d1', [caption('apx/d1', [[('Appendix', PURPLE)]], 640, 270, size=44)])
    s.add('apx/d2', [T('apx/d2', 240, 350, 800, 60, ['역할 분담, Reasoning Embedding, 지식 그래프와의 관계,', '세 가지 UX, 자주 받을 질문'],
                       size=14, color=SUB, align='c', lnspc=21)])
    return s


def a_roles():
    s = Slide('apx_roles', trans=('fade', 400), bar=False,
              notes='Weave를 부품별로 나누면 이렇습니다. 질문을 나누는 일은 기기 안 소형 언어 모델이, 중간 근거를 찾는 일은 Reasoning Embedding이 맡습니다. '
                    '날짜는 모델이 지어내지 않고 카톡을 받은 날, 즉 메타데이터에서 가져옵니다. 마지막 이름은 사진 속 라벨을 읽어 출처와 함께 건넵니다.')
    head(s, [('단계마다 ', INK), ('맡는 부품', PURPLE), ('이 다릅니다', INK)], '‘지은이네 집들이 때 마셨던 와인’ 하나가 답이 되기까지')
    rows = [['질의 재작성', '기기 안 소형 언어 모델(sLLM)', '집들이 날짜를 먼저 묻도록 질문을 둘로 나눕니다'],
            ['중간 근거 검색', 'Reasoning Embedding', '‘집들이’라는 말이 없는 지은이의 카톡을 찾습니다'],
            ['근거 읽기', 'sLLM + 메타데이터', ['‘이따 올 때’와 카톡을 받은 날을 이어', '3월 15일을 다음 단서로 씁니다']],
            ['조건 적용, 다음 검색', '메타데이터 필터 + Reasoning Embedding', '3월 15일 사진 가운데 와인 사진을 찾습니다'],
            ['결과 제공', 'OCR + sLLM + 키보드 화면', '라벨을 읽고, 출처와 함께 이름을 건넵니다']]
    table(s, 'apx/t', 70, 150, [210, 330, 600], ['단계', '맡는 부품', '와인 질문에서 하는 일'], rows, row_h=70, hi=1)
    s.add('apx/n', [T('apx/n', 70, 556, 1140, 60,
                      ['데이터 색인은 기기가 충전 중이거나 쉴 때 미리 해 둡니다. 상황 인식은 키보드의 실타래 버튼이나 위치, 탑승권 같은 신호가 맡습니다.',
                       '사용자가 고른 내용만 입력되고, 보내기는 사용자가 직접 누릅니다.'], size=11.5, color=SUB, lnspc=18)])
    return s


def a_rem():
    s = Slide('apx_rem', trans=('fade', 400), bar=False,
              notes='Reasoning Embedding의 몫을 좁혀서 말하면 이렇습니다. 다음에 찾을 것을 질문에 넣는 일은 질문 다시 쓰기가, '
                    '답을 직접 말하지 않는 기록까지 가까이 두는 일은 Reasoning Embedding이 맡습니다. 두 효과는 따로 볼 수 있습니다. '
                    '논문에서도 일반 검색에 강한 모델이 추론이 필요한 검색에서는 크게 약해지고, 추론용으로 학습한 검색 모델에 다시 쓴 질문을 넣으면 더 좋아졌습니다. '
                    '수치는 각 논문의 공개 벤치마크 결과입니다.')
    head(s, [('찾는 일은 ', INK), ('Reasoning Embedding', PURPLE), ('이, 잇는 일은 ', INK), ('질문 다시 쓰기', PURPLE), ('가 맡습니다', INK)],
         '두 가지 효과를 나눠서 봅니다', size=23)
    # 왼쪽: 질문 다시 쓰기
    x, y, w, h = 70, 150, 545, 300
    out = [R('apx/l/bg', x, y, w, h, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=SHADOW_CARD),
           P('apx/l/ic', ICON['spool'], x + 22, y + 20, 26, 26),
           T('apx/l/t', x + 56, y + 18, 300, 30, 'Query Rewriting', size=15, color=PURPLE, weight='b', anchor='ctr'),
           T('apx/l/s', x + 22, y + 58, w - 44, 22, '다음에 찾을 것을 질문에 직접 넣습니다', size=12.5, color=INK, weight='b'),
           R('apx/l/q0', x + 22, y + 96, w - 44, 40, prst='roundRect', radius=12, fill='F7F5FC', line=None),
           T('apx/l/q0t', x + 38, y + 96, w - 70, 40, QUERY, size=12.5, color=SUB, anchor='ctr'),
           T('apx/l/arr', x + w / 2 - 10, y + 138, 20, 24, '↓', size=14, color=PURPLE2, weight='b', align='c', anchor='ctr'),
           R('apx/l/q1', x + 22, y + 166, w - 44, 40, prst='roundRect', radius=12, fill=LAV, line=None)]
    out += numdot('apx/l/n1', x + 44, y + 186, 1, r=10, pt=8.5)
    out.append(T('apx/l/q1t', x + 62, y + 166, w - 90, 40, '지은이네 집들이는 언제였지?', size=12.5, color=INK, weight='m', anchor='ctr'))
    out.append(R('apx/l/q2', x + 22, y + 214, w - 44, 40, prst='roundRect', radius=12, fill=BLUE_BG, line=None))
    out += numdot('apx/l/n2', x + 44, y + 234, 2, r=10, pt=8.5, fill=BLUE)
    tk, tkw = chip('apx/l/tk', x + 62, y + 222, '3/15 (일)', 'fill', pt=10, h=24, padx=8)
    out += tk
    out.append(T('apx/l/q2t', x + 62 + tkw + 6, y + 214, w - 100 - tkw, 40, '마셨던 와인은?', size=12.5, color=INK, weight='m', anchor='ctr'))
    out.append(T('apx/l/f', x + 22, y + 264, w - 44, 22, '빈칸(그날)은 앞에서 찾은 단서로 채웁니다', size=10.5, color=SUB))
    s.add('apx/l', out)
    # 오른쪽: Reasoning Embedding(공간 그림)
    x2 = 665
    out = [R('apx/r/bg', x2, y, w, h, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=SHADOW_CARD),
           T('apx/r/t', x2 + 22, y + 18, 300, 30, 'Reasoning Embedding', size=15, color=PURPLE, weight='b', anchor='ctr'),
           T('apx/r/s', x2 + 22, y + 58, w - 44, 22, '답을 직접 말하지 않는 기록도 가까이 둡니다', size=12.5, color=INK, weight='b')]
    cx, cy = x2 + 150, y + 190
    out.append(R('apx/r/near', cx - 92, cy - 70, 184, 140, prst='ellipse', fill=None, line=PURPLE2, line_w=1.5, dash='dash'))
    out.append(R('apx/r/star', cx - 11, cy - 11, 22, 22, prst='star5', fill=PURPLE, line='FFFFFF', line_w=1.5))
    out.append(T('apx/r/sl', cx - 60, cy + 12, 120, 18, '질문 ①', size=9.5, color=PURPLE, weight='b', align='c'))
    # 일반 임베딩: 카톡은 멀리 / Reasoning Embedding: 가까이
    out.append(R('apx/r/k0', x2 + 380, y + 230, 120, 30, prst='roundRect', radius=10, fill='FFFFFF', line=LINE, line_w=1.0, dash='dash'))
    out.append(P('apx/r/k0i', ICON['talk'], x2 + 388, y + 235, 20, 20, alpha=55))
    out.append(T('apx/r/k0t', x2 + 412, y + 230, 90, 30, '지은 카톡', size=10, color=MUTE, anchor='ctr'))
    out.append(T('apx/r/k0l', x2 + 372, y + 262, 140, 18, '일반 임베딩', size=9, color=MUTE, align='c'))
    out.append(R('apx/r/k1', cx + 16, cy - 46, 120, 30, prst='roundRect', radius=10, fill='FFFFFF', line=RING, line_w=1.8))
    out.append(P('apx/r/k1i', ICON['talk'], cx + 24, cy - 41, 20, 20))
    out.append(T('apx/r/k1t', cx + 48, cy - 46, 90, 30, '지은 카톡', size=10, color=INK, weight='b', anchor='ctr'))
    out.append(C('apx/r/arr', [(x2 + 378, y + 238), (x2 + 330, y + 200), (cx + 180, cy - 40), (cx + 138, cy - 31)], w=1.8, color=PURPLE2,
                 dash='dash', tail='triangle'))
    out.append(T('apx/r/q', x2 + 300, y + 112, 220, 40, ['‘박스 정리 다 했어!', '휴지 안 사 와도 돼’'], size=10, color=SUB, lnspc=14))
    out.append(T('apx/r/f', x2 + 22, y + 264, w - 44, 22, '같은 구조의 임베딩을 추론형 데이터로 튜닝합니다', size=10.5, color=SUB))
    s.add('apx/r', out)
    # 아래: 논문 근거
    by = 474
    out = [R('apx/b/bg', 70, by, 1140, 150, prst='roundRect', radius=18, fill=LAV2, line=LINE2, line_w=1.0),
           T('apx/b/t', 92, by + 14, 400, 24, '두 효과를 나눠 보면', size=12.5, color=PURPLE, weight='b')]
    items = [('추론이 필요한 검색', ['일반 검색에 강한 임베딩도 추론이 필요한 검색에서는 크게 약해집니다.', '같은 모델 BEIR 59.0 → BRIGHT 18.3 (nDCG@10)¹']),
             ('추론형 학습 + 다시 쓴 질문', ['추론용으로 학습한 검색 모델에 다시 쓴 질문을 넣으면 더 올라갑니다.', 'ReasonIR-8B, BRIGHT 24.4 → 29.9 (원래 질문 → 다시 쓴 질문)²'])]
    for i, (t, ls) in enumerate(items):
        ix = 92 + i * 560
        out.append(T('apx/b/i%dt' % i, ix, by + 50, 520, 22, t, size=12, color=INK, weight='b'))
        out.append(T('apx/b/i%dl' % i, ix, by + 76, 530, 60, ls, size=11, color=BODY, lnspc=17))
    s.add('apx/b', out)
    foot(s, '¹ Su et al., "BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval", ICLR 2025 (SFR-Embedding-Mistral)   '
            '² Shao et al., "ReasonIR: Training Retrievers for Reasoning Tasks", COLM 2025.  수치는 각 논문의 공개 벤치마크 결과입니다.', y=640)
    return s


def a_kg():
    s = Slide('apx_kg', trans=('fade', 400), bar=False,
              notes='삼성 Personal Data Engine은 여러 앱의 기록을 AI로 분석해 기기 안 개인 지식 그래프에 쌓고, 규칙으로 따라 나오는 사실까지 미리 계산해 둡니다. '
                    '그래서 정리된 사실은 빠르고 확실하게 답합니다. Weave는 같은 기록을 원문 그대로 색인해 두었다가, 질문이 들어오면 그 질문에 맞춰 원문 속 연결을 찾습니다. '
                    '그래프는 기록이 들어올 때 잇고, Weave는 질문이 들어올 때 잇습니다. 둘은 대신하는 관계가 아니라 보완하는 관계입니다.')
    head(s, [('그래프는 ', INK), ('기록이 들어올 때', PURPLE), (' 잇고, Weave는 ', INK), ('질문이 들어올 때', PURPLE), (' 잇습니다', INK)],
         '기존 개인 데이터 기반을 대신하지 않고, 그 위에 더합니다', size=23)

    def lane(key, y, title, sub, steps, strong, on=False):
        out = [R(key + '/bg', 70, y, 1140, 150, prst='roundRect', radius=20, fill='FFFFFF', line=RING if on else LINE2,
                 line_w=1.8 if on else 1.2, shadow=SHADOW_CARD),
               T(key + '/t', 92, y + 18, 300, 26, title, size=14.5, color=PURPLE if on else INK, weight='b'),
               T(key + '/s', 92, y + 46, 300, 20, sub, size=10.5, color=SUB)]
        sx = 300
        for i, (t, hl) in enumerate(steps):
            wdt = 170
            out.append(R(key + '/p%d' % i, sx, y + 30, wdt, 54, prst='roundRect', radius=14, fill=LAV if hl else 'F7F5FC',
                         line=RING if hl else None, line_w=1.4))
            out.append(cell(key + '/pt%d' % i, sx + 8, y + 30, wdt - 16, 54, t, size=10.5, color=INK if hl else BODY, align='c',
                            weight='b' if hl else 'r'))
            if i < len(steps) - 1:
                out.append(T(key + '/a%d' % i, sx + wdt, y + 30, 26, 54, '→', size=12, color=PURPLE2, align='c', anchor='ctr'))
            sx += wdt + 26
        out.append(R(key + '/st', 300, y + 98, 890, 36, prst='roundRect', radius=12, fill=LAV2, line=None))
        out.append(T(key + '/stt', 316, y + 98, 870, 36, strong, size=11.5, color=PURPLE if on else SUB, weight='b', anchor='ctr'))
        return out
    s.add('apx/kg1', lane('apx/kg1', 150, '개인 지식 그래프', '삼성 Personal Data Engine¹',
                          [('여러 앱의 기록', False), ('AI가 분석해 사실로 저장', False), (['규칙으로 따라 나오는', '사실까지 미리 계산'], True),
                           ('질문하면 바로 조회', False)],
                          '강점: 사람, 날짜, 장소처럼 정리된 사실을 빠르고 확실하게 잇습니다'))
    s.add('apx/kg2', lane('apx/kg2', 320, 'Weave', '질문할 때 잇는 검색',
                          [('여러 앱의 기록', False), (['원문, 벡터, 메타데이터로', '색인'], False), (['질문이 오면 그 질문에', '맞춰 연결을 찾음'], True),
                           ('찾은 단서로 다시 묻기', False)],
                          '강점: 미리 정리하지 않은 말 속 연결(‘휴지 안 사 와도 돼’ → 집들이)을 원문에서 찾습니다', on=True))
    out = [R('apx/k3/bg', 70, 490, 1140, 120, prst='roundRect', radius=20, fill=LAV2, line=LINE2, line_w=1.0),
           T('apx/k3/t', 92, 506, 400, 24, '함께 쓰면', size=13, color=PURPLE, weight='b'),
           T('apx/k3/l', 92, 536, 1100, 70,
             ['정확한 사실(날짜, 사람, 앱)은 메타데이터와 그래프로 거르고, 말 속 연결은 Weave가 원문에서 찾습니다.',
              '기존 개인 데이터 기반(PDE)을 활용할 수 있도록 설계하고, 사용자가 확인한 결과는 다음에 바로 쓰도록 남기는 연계도 검토합니다.'],
             size=11.5, color=BODY, lnspc=18)]
    s.add('apx/k3', out)
    foot(s, '¹ Crocker, Horrocks, Nenov, "Semantic Technology in Your Pocket", ISWC 2025 Industry Track (CEUR-WS Vol-4085): 기기 안 RDFox로 '
            '그래프를 저장하고, 규칙으로 따라 나오는 사실을 미리 계산(materialisation)하며, 바뀐 기록만 다시 계산합니다.   '
            'GraphRAG(Edge et al., 2024)도 색인 시점과 질문 시점을 나눠 설명합니다.', y=630)
    return s


def a_hops():
    s = Slide('apx_hops', trans=('fade', 400), bar=False,
              notes='와인 질문을 홉별로 보면, 그래프로 막히는 곳은 첫 단서 하나입니다. 그날 사진을 찾고 라벨을 읽는 일은 그래프도 잘할 수 있습니다. '
                    '문제는 지은이의 카톡이 집들이 초대라는 사실이 그래프에 들어 있을 가능성이 낮다는 점입니다. '
                    '그 사실을 넣으려면 메시지가 올 때마다 미리 해석해야 하는데, 기록은 계속 쌓이고 질문은 가끔 옵니다.')
    head(s, [('그래프로 막히는 곳은 ', INK), ('첫 단서 하나', PURPLE), ('입니다', INK)], '같은 와인 질문을 홉별로 나눠 봅니다')
    rows = [['① 집들이 날짜', '지은이네 집들이 = 3월 15일', ['그 행사가 그래프에 미리 있어야 합니다.', '일정도 ‘집들이’라는 말도 없습니다'],
             ['‘박스 정리 다 했어, 휴지 안 사 와도 돼’를', '집들이 초대로 읽어 찾습니다']],
            ['② 그날 사진', '3월 15일 저녁 사진', '날짜를 맞추는 일이라 잘합니다', '메타데이터로 거릅니다'],
            ['③ 와인 이름', '라벨의 글자', '라벨 글자가 저장돼 있으면 찾습니다', '사진 속 글자를 읽습니다']]
    table(s, 'apx/t', 70, 150, [190, 250, 350, 350], ['홉', '필요한 사실', '그래프만으로', 'Weave'], rows, row_h=84, hi=0)
    out = [R('apx/n/bg', 70, 470, 1140, 120, prst='roundRect', radius=18, fill=LAV2, line=LINE2, line_w=1.0),
           T('apx/n/t', 92, 486, 600, 24, '①을 그래프에 넣으려면', size=13, color=PURPLE, weight='b'),
           T('apx/n/l', 92, 516, 1100, 70,
             ['메시지가 올 때마다 ‘집들이 초대’라고 미리 해석해 저장해야 합니다. 질문을 모르니 모든 메시지를 해석해야 하고, 놓치면 조용히 빠집니다.',
              '그래프로 찾는 방식의 오류도 대부분 질문과 문서에서 정보를 뽑는 단계에서 나왔습니다(100건 중 76건)¹.'],
             size=11.5, color=BODY, lnspc=18)]
    s.add('apx/n', out)
    foot(s, '¹ Gutiérrez et al., "HippoRAG", NeurIPS 2024, 부록 F(MuSiQue 오류 100건): 질문 쪽 개체 추출 48건, 문서 쪽 정보 추출(OpenIE) 28건, 그래프 탐색 24건.',
         y=612)
    return s


def a_compare():
    s = Slide('apx_cmp', trans=('fade', 400), bar=False,
              notes='방식마다 잘하는 일과 필요한 조건이 다릅니다. 어느 한 방식이 못 한다는 비교가 아니라, 이 질문에서 무엇이 필요한지의 비교입니다. '
                    'Weave는 추론이 필요한 중간 근거를 더 잘 찾도록 튜닝한 임베딩으로 멀티홉 검색을 하고, 개인 기록에 맞춘 학습 데이터가 필요합니다.')
    head(s, [('방식마다 ', INK), ('잘하는 일', PURPLE), ('과 ', INK), ('필요한 조건', PURPLE), ('이 다릅니다', INK)])
    rows = [['지식 그래프 검색', '정리된 개체와 관계를 일관되게 잇고 조회합니다', '행사, 사진, 와인의 관계가 미리 저장돼 있어야 합니다'],
            ['일반 임베딩 + 멀티홉', '원문에서 단계별로 단서를 이어 찾습니다', '질문을 잘 나누고, 중간 근거가 위로 올라와야 합니다'],
            ['Weave', ['추론이 필요한 중간 근거를 더 잘 찾도록', '튜닝한 임베딩으로 멀티홉 검색을 합니다'], '개인 기록에 맞춘 학습 데이터가 필요합니다'],
            ['그래프 + 원문 검색', '정리된 관계와 원문 근거를 함께 씁니다', '데이터 접근과 실행 계획을 함께 설계해야 합니다']]
    table(s, 'apx/t', 70, 140, [240, 450, 450], ['방식', '잘하는 일', '와인 질문에서 필요한 조건'], rows, row_h=78, hi=2)
    foot(s, '그래프와 원문 검색을 함께 쓰면 더 좋아진다는 결과: Gutiérrez et al., HippoRAG(NeurIPS 2024), Han et al., "RAG vs. GraphRAG"(arXiv 2025).',
         y=520)
    return s


def a_ux():
    s = Slide('apx_ux', trans=('fade', 400), bar=False,
              notes='세 가지 UX는 같은 다섯 단계로 움직입니다. 통화 중에는 일정과 최신 회의록과 메일을 이어 요약하고, 검색창에서는 카톡과 사진을 이어 이름을 찾고, '
                    '공항에서는 위치와 탑승권으로 Weave가 먼저 질문을 만들어 아내의 카톡과 링크를 이어 보낼 말을 추천합니다.')
    head(s, [('세 가지 UX가 ', INK), ('같은 파이프라인', PURPLE), ('으로 움직입니다', INK)])
    rows = [[['UX 1  기록 통합 검색', '통화 중'], '위로 쓸어 올려 검색', ['‘언제 어디서’와', '‘무엇을 어떤 순서로’'], ['일정 → 최신 주간 회의', '→ 민수님 메일'], ['세 문장 요약', '+ 연결된 기억']],
            [['UX 2  단서로 찾는 기억', '검색창'], '키보드 실타래 버튼', ['‘집들이는 언제?’', '→ ‘그날 와인은?’'], ['지은 카톡(3월 15일)', '→ 그날 와인 사진'], ['배비치 소비뇽 블랑', '자동 완성']],
            [['UX 3  먼저 건네는 기억', '공항 도착'], ['위치, 탑승권,', '아내와의 대화'], ['Weave가 먼저', '질문을 만듭니다'], ['아내 카톡(갈색병)', '→ 링크 미리보기'], ['보낼 말 추천', '(에스티 로더 갈색병)']]]
    table(s, 'apx/t', 70, 140, [250, 200, 220, 250, 220], ['UX', '01 상황 인식', '02 질의 재작성', '03 연쇄 탐색', '04 결과 제공'], rows,
          row_h=96, hi=1, pt=11)
    s.add('apx/n', [T('apx/n', 70, 480, 1140, 50, ['단서는 날짜(UX 2)뿐 아니라 맡은 사람(UX 1, 민수님)과 별명(UX 3, 갈색병)처럼 기록 속 내용입니다.',
                                                  '날짜, 사람, 앱은 메타데이터 필터로 후보를 좁힙니다.'], size=11.5, color=SUB, lnspc=18)])
    return s


def q_pde():
    s = Slide('apx_q_pde', trans=('fade', 400), bar=False,
              notes='맞습니다. 지식 그래프는 여러 단계 연결에 강하고, 저희도 날짜는 그래프처럼 필터로 정확히 거릅니다. '
                    '다만 이번 질문의 첫 단서인 지은 씨 카톡에는 집들이라는 말도, 캘린더 일정도 없습니다. '
                    '그래프로 이으려면 메시지를 받는 순간 집들이 초대라고 미리 해석해 저장해야 하는데, 기록은 계속 쌓이고 질문은 가끔입니다. '
                    'Weave는 질문이 생겼을 때 그 질문에 맞춰 원문에서 연결을 찾습니다. 그래프를 대체하지 않고, 그래프에 아직 없는 연결을 채웁니다.')
    head(s, [('Q. ', PURPLE), ('삼성 PDE(지식 그래프)로 되는 것 아닌가요?', INK)])
    qcard(s, 'apx/q1', 70, 140, 1140, 300, 'A. 그래프에 아직 없는 연결을 채웁니다',
          ['지식 그래프는 여러 단계 연결에 강하고, Weave도 날짜 같은 정확한 조건은 필터로 거릅니다.',
           '다만 첫 단서인 지은이의 카톡에는 ‘집들이’라는 말도, 캘린더 일정도 없습니다.',
           '그래프로 이으려면 메시지를 받을 때 ‘집들이 초대’라고 미리 해석해 저장해야 합니다.',
           'Weave는 질문이 생겼을 때 그 질문에 맞춰 원문에서 연결을 찾습니다.'],
          ['정리된 사실은 그래프가 빠르고, 말 속 연결은 Weave가 찾습니다. 그래서 대체가 아니라 보완입니다.'], pt=13)
    chips_ = [('기록이 들어올 때 잇는 그래프', 'outline'), ('질문이 들어올 때 잇는 Weave', 'fill'), ('날짜와 사람은 필터로 함께', 'soft')]
    x = 70
    out = []
    for i, (t, st) in enumerate(chips_):
        c, w = chip('apx/q1c%d' % i, x, 470, t, st, pt=12, h=36, padx=18)
        out += c
        x += w + 14
    s.add('apx/q1c', out)
    return s


def q_sameday():
    s = Slide('apx_q_day', trans=('fade', 400), bar=False,
              notes='같은 날 찍었다는 이유만으로 그 집들이 와인이라고 정하지 않습니다. 메시지의 이따 올 때가 받은 날과 모임 날을 이어 주고, '
                    '사진의 시각과 장소와 내용이 그 모임에서 찍은 사진인지를 뒷받침합니다. 근거가 모자라면 후보와 원문을 함께 보여 주고 사용자가 고르게 합니다.')
    head(s, [('Q. ', PURPLE), ('같은 날 찍은 사진이면 그 집들이 와인이라고 정하나요?', INK)], size=23)
    qcard(s, 'apx/q2', 70, 140, 600, 330, 'A. 날짜 하나로 정하지 않습니다',
          ['메시지의 ‘이따 올 때’가 받은 날과 모임 날을 잇고,', '사진의 시각, 장소, 내용이 그 모임에서', '찍은 사진인지를 뒷받침합니다.',
           '근거가 모자라면 후보와 원문을 함께 보여 주고,', '사용자가 고릅니다.'], pt=13)
    ev = [('talk', '‘이따 올 때’', '카톡을 받은 날 = 모임 날'), ('gallery', '저녁 8시 14분', '모임 시간대에 찍은 사진'),
          ('map', '지은이네 근처', '사진의 위치 정보'), ('gallery', '와인 병과 잔', '사진 속 내용과 라벨')]
    out = []
    for i, (ic, a, b) in enumerate(ev):
        y = 140 + i * 84
        out += [R('apx/ev%d/bg' % i, 700, y, 510, 70, prst='roundRect', radius=16, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=SHADOW_SOFT),
                P('apx/ev%d/ic' % i, ICON[ic], 720, y + 19, 32, 32),
                T('apx/ev%d/a' % i, 768, y + 12, 420, 24, a, size=13, color=INK, weight='b'),
                T('apx/ev%d/b' % i, 768, y + 38, 420, 20, b, size=11, color=SUB)]
    out.append(R('apx/ev/ans', 700, 480, 510, 44, prst='roundRect', radius=14, fill=PURPLE, line=None))
    out.append(T('apx/ev/anst', 700, 480, 510, 44, '근거가 모이면  →  배비치 소비뇽 블랑', size=13, color='FFFFFF', weight='b', align='c', anchor='ctr'))
    s.add('apx/ev', out)
    return s


def q_apple():
    s = Slide('apx_q_apple', trans=('fade', 400), bar=False,
              notes='Apple은 iOS 27의 Siri AI가 기기 안 Spotlight 색인으로 메시지, 메일, 사진 속 개인 맥락을 찾아 답한다고 발표했고, 9월에 영어, 10월 26일에 한국어 베타를 냈습니다. '
                    '개인 기록 검색이 다음 경쟁 축이라는 신호입니다. Weave는 매일 쓰는 갤럭시 키보드에서 바로 시작하고, 질문을 나눠 단서를 이어 찾는 데 집중합니다.')
    head(s, [('Q. ', PURPLE), ('Apple Siri도 개인 기록을 찾지 않나요?', INK)])
    qcard(s, 'apx/q3', 70, 140, 560, 380, 'A. 같은 방향이고, 그래서 지금입니다',
          ['Apple은 iOS 27의 Siri AI가 기기 안 Spotlight 색인으로', '메시지, 메일, 사진 속 개인 맥락을 찾아 답한다고', '발표했습니다.',
           '개인 기록 검색이 다음 경쟁 축이라는 신호입니다.'],
          ['2026. 6. 8 발표   9. 14 영어 베타   10. 26 한국어 베타(iOS 27.2)¹'], pt=13)
    out = [R('apx/w/bg', 660, 140, 550, 380, prst='roundRect', radius=20, fill='FFFFFF', line=RING, line_w=1.8, shadow=SHADOW_CARD),
           T('apx/w/t', 684, 158, 500, 26, 'Weave가 집중하는 것', size=14, color=PURPLE, weight='b')]
    pts = [('키보드에서 바로', '검색창, 통화, 메신저 어디서든 실타래 버튼 하나로 시작합니다'),
           ('단서를 이어 찾기', '질문을 나누고, 먼저 찾은 기록의 단서로 다시 묻습니다'),
           ('갤럭시 기록과 함께', '삼성 기본 앱, 월렛, 위치 신호와 기존 개인 데이터 기반을 함께 씁니다')]
    for i, (a, b) in enumerate(pts):
        y = 204 + i * 98
        out += numdot('apx/w/n%d' % i, 698, y + 14, i + 1, r=12, pt=9.5)
        out.append(T('apx/w/a%d' % i, 722, y, 470, 26, a, size=13, color=INK, weight='b'))
        out.append(T('apx/w/b%d' % i, 722, y + 30, 470, 44, b, size=11.5, color=BODY, wrap=True))
    s.add('apx/w', out)
    foot(s, '¹ Apple Newsroom: "Apple introduces Siri AI…"(2026-06-08), "Siri AI…is here"(2026-09-14), "Siri AI is available in more languages"(2026-10-26).'
            '  Siri AI의 모델은 기기와 Private Cloud Compute 서버를 함께 씁니다.', y=548)
    return s


def q_llm():
    s = Slide('apx_q_llm', trans=('fade', 400), bar=False,
              notes='LLM은 글을 토큰마다 계산하며 만들어 연산량이 많고, 수많은 기록을 매번 읽기 어렵습니다. 임베딩은 입력당 한 번 계산해 후보를 고르고, '
                    'LLM은 질문을 나누거나 최종 문장을 다듬을 때만 씁니다. 기록 벡터는 충전 중이나 쉴 때 미리 만들어 둡니다.')
    head(s, [('Q. ', PURPLE), ('왜 LLM이 아니라 임베딩으로 찾나요?', INK)])
    qcard(s, 'apx/q4', 70, 140, 560, 330, 'A. 찾는 일은 가볍게, 쓰는 일만 LLM에',
          ['LLM은 글을 토큰마다 계산하며 만들어서,', '수많은 기록을 매번 읽기 어렵습니다.', '임베딩은 입력마다 한 번 계산해 후보를 고르고,',
           'LLM은 질문을 나누거나 문장을 다듬을 때만 씁니다.'], ['기록 벡터는 충전 중이나 기기가 쉴 때 미리 만들어 둡니다.'], pt=13)
    rows = [['결과', '글을 만듭니다', '의미 벡터 하나'], ['계산', '토큰마다 반복', '입력마다 한 번'], ['기록', '요청마다 읽기', '미리 저장']]
    table(s, 'apx/t', 660, 140, [130, 210, 210], ['', 'LLM', '임베딩'], rows, row_h=70)
    return s


def q_data():
    s = Slide('apx_q_data', trans=('fade', 400), bar=False,
              notes='삼성 기본 앱은 사용자 동의 아래 기기 안에서 연동하고, 카카오톡 같은 외부 메신저는 사용자가 허용한 알림만 색인합니다. Weave는 통화 내용을 듣지 않습니다. '
                    '무거운 색인은 충전 중이나 기기가 쉴 때 미리 하고, 사용 중에는 필요한 기록만 찾습니다. '
                    '허용한 기록만 기기 안에서 처리하고 언제든 끄거나 색인을 지울 수 있으며, 근거가 모자라면 후보와 원문을 먼저 보여 줍니다.')
    head(s, [('Q. ', PURPLE), ('데이터 접근, 기기 성능, 사생활은요?', INK)], '허용한 기록만, 기기 안에서, 필요한 만큼만 처리합니다')
    cards = [('데이터 접근', ['삼성 기본 앱(갤러리, 노트, 캘린더, 메일,', '월렛)은 사용자 동의 아래 기기 안에서', '연동합니다. 카카오톡 같은 외부 메신저는',
                          '허용한 알림의 글만 색인합니다¹.'], ['통화 내용은 듣지 않습니다. 통화 중에는', '사용자가 위로 밀어 직접 적습니다.']),
             ('기기 성능', ['무거운 색인은 충전 중이나 기기가 쉴 때', '미리 하고², 사용 중에는 필요한 기록만', '찾아 읽습니다. 검색은 가벼운 임베딩이',
                        '맡고, 언어 모델에는 추린 근거만 넘깁니다.'], None),
             ('사생활 보호', ['허용한 기록만 기기 안에서 처리하고,', '언제든 끄거나 색인을 지울 수 있습니다.', '저장소 암호화 키는 Android Keystore로',
                         '보호합니다³.'], ['근거가 모자라면 후보와 원문을 먼저', '보여 주고, 판단은 사용자가 합니다.'])]
    for i, (t, a, b) in enumerate(cards):
        qcard(s, 'apx/d%d' % i, 70 + i * 386, 150, 368, 330, t, a, b, pt=12)
    foot(s, '¹ Android Developers, "NotificationListenerService"   ² Android Developers, "Define work requests"(충전 중, 유휴 조건)   '
            '³ Android Developers, "Android Keystore system"', y=500)
    return s


APPENDIX = [a_divider, a_roles, a_rem, a_kg, a_hops, a_compare, a_ux, q_pde, q_sameday, q_apple, q_llm, q_data]


CREDITS = [('와인 잔(임베딩 장)', 'Davide Restivo, "A glass of red wine", Wikimedia Commons, CC BY-SA 2.0'),
           ('풀밭 위 와인', 'Jamie Street, "Wine on a meadow", Unsplash(Wikimedia Commons 사본), CC0'),
           ('샴페인', 'L.C. Nøttaasen, "Champagne pouring", Wikimedia Commons, CC BY 2.0'),
           ('바닷가 와인', 'Jez Timms, "Enjoying a bottle of red wine", Unsplash, CC0'),
           ('집 저녁 식탁', 'Jason M. C. Han, "Special foods & cuisines in Chongqing - Family Dinner 3rd", Wikimedia Commons, CC BY-SA 4.0')]


def a_credits():
    s = Slide('apx_credit', trans=('fade', 400), bar=False, notes='How it Works에 쓴 사진의 출처입니다. 크기를 줄이고 잘라 썼습니다.')
    head(s, [('사진 출처', INK)], 'How it Works의 갤러리 사진(크기를 줄이고 잘라 씀)')
    out = []
    for i, (a, b) in enumerate(CREDITS):
        y = 160 + i * 64
        out += [R('apx/cr%d/bg' % i, 160, y, 960, 52, prst='roundRect', radius=14, fill='FFFFFF', line=LINE2, line_w=1.0),
                T('apx/cr%d/a' % i, 184, y, 200, 52, a, size=12, color=PURPLE, weight='b', anchor='ctr'),
                T('apx/cr%d/b' % i, 390, y, 720, 52, b, size=11, color=BODY, anchor='ctr')]
    s.add('apx/cr', out)
    s.add('apx/cr_n', [T('apx/cr_n', 160, 500, 960, 40, '배비치 소비뇽 블랑 사진과 그 밖의 화면은 팀이 만든 것입니다.', size=11, color=SUB, align='c')])
    return s


APPENDIX.append(a_credits)
