"""Appendix (Argon 개선판): Q&A 대응 및 아키텍처 심층 근거 장표.
How it Works 본문과 동일한 디자인 시스템·배경·카드·글꼴을 사용하며,
임원·비전공자도 한눈에 읽히는 본문 + 전공자·엔지니어를 위한 검증된 학술·시스템 각주를 함께 제공한다.
"""
from build import (AS, BLUE, BLUE_BG, PH, QUERY, Slide)
from ui import (BODY, ICON, INK, LAV, LAV2, LINE, LINE2, MUTE, PURPLE, PURPLE2, RED, RING, SUB, SHADOW_CARD, SHADOW_SOFT, C, P, R, T,
                caption, chip, crop_fit, line, numdot, scurve, thread, tw)

GRAY = '8E88A0'


def apx_badge(s):
    cw = tw('APPENDIX', 10.5, 'sb') + 32
    s.add('apx/badge', [T('apx/badge', 40, 22, cw, 28, 'APPENDIX', size=10.5, color='FFFFFF', weight='sb', align='c', anchor='ctr',
                          spc=0.5, fill=PURPLE, radius=14)])


def head(s, title_runs, sub=None, y=58, size=24):
    apx_badge(s)
    s.add('apx/title', [caption('apx/title', [title_runs], 640, y, size=size)])
    if sub:
        s.add('apx/sub', [T('apx/sub', 100, y + size * 1.42 + 6, 1080, 24, sub, size=13, color=SUB, align='c')])


def foot(s, text, y=682):
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


# ------------------------------------------------------------------ 장표 목록
def a_divider():
    s = Slide('apx0', trans=('fade', 500), bar=False,
              notes='여기부터는 질의응답(Q&A) 시 띄우는 Appendix입니다. 본 발표에서는 넘기지 않습니다.')
    apx_badge(s)
    s.add('apx/d1', [caption('apx/d1', [[('Appendix', PURPLE)]], 640, 260, size=44)])
    s.add('apx/d2', [T('apx/d2', 200, 342, 880, 64,
                       ['단계별 모듈 역할 분담 · Reasoning Embedding 원리 · 삼성 PDE(지식 그래프)와의 보완 관계',
                        '3가지 UX 공통 파이프라인 · 온디바이스 지연시간 및 자원 예산 · 주요 Q&A'],
                       size=14, color=SUB, align='c', lnspc=22)])
    return s


def a_roles():
    s = Slide('apx_roles', trans=('fade', 400), bar=False,
              notes='Weave를 부품별로 나누면 이렇습니다. 질문을 나누는 일은 기기 안 소형 언어 모델이, 중간 근거를 찾는 일은 Reasoning Embedding이 맡습니다. '
                    '날짜는 모델이 지어내지 않고 카톡을 받은 날, 즉 메타데이터에서 가져옵니다. 마지막 이름은 사진 속 라벨을 읽어 출처와 함께 건넵니다.')
    head(s, [('단계마다 ', INK), ('맡는 모듈과 역할', PURPLE), ('이 명확히 나뉩니다', INK)],
         '‘지은이네 집들이 때 마셨던 와인’ 하나가 정답이 되기까지의 모듈별 분담')
    rows = [['02 질의 재작성', '기기 안 소형 언어 모델 (sLLM)', '집들이 날짜를 먼저 묻도록 질문을 단서 순서대로 둘로 나눕니다'],
            ['03-1 중간 근거 검색', 'Reasoning Embedding', '‘집들이’라는 단어가 없는 지은이의 카톡(‘휴지 안 사 와도 돼’)을 찾아냅니다'],
            ['03-2 단서 추출·결합', 'sLLM + 메타데이터 파서', ['‘이따 올 때’와 카톡 수신 시각을 이어', '3월 15일을 두 번째 하위 질문의 빈칸([그날])에 채웁니다']],
            ['03-3 조건 필터 + 재검색', '메타데이터 필터 + Reasoning Embedding', 'date: "2026-03-15" 사진만 남긴 뒤 와인 사진을 고릅니다'],
            ['04 결과 제공', '온디바이스 OCR + sLLM + 키보드 UI', '와인 라벨을 읽고 근거 기록(카톡·사진)과 함께 탭 한 번으로 입력합니다']]
    table(s, 'apx/t', 70, 148, [220, 330, 590], ['단계', '담당 모듈', '와인 검색 시나리오에서 수행하는 역할'], rows, row_h=70, hi=1)
    s.add('apx/n', [T('apx/n', 70, 554, 1140, 60,
                      ['• 00 데이터 색인은 기기가 충전 중이거나 유휴 상태일 때 미리 수행합니다. 01 상황 인식은 키보드 실타래 버튼·통화·위치·탑승권 신호가 맡습니다.',
                       '• 모든 추론 결과는 출처 원문과 함께 제시되며, 최종 입력·전송 여부는 항상 사용자가 직접 결정합니다.'], size=11.5, color=SUB, lnspc=18)])
    return s


def a_rem():
    s = Slide('apx_rem', trans=('fade', 400), bar=False,
              notes='Reasoning Embedding의 몫을 좁혀서 말하면 이렇습니다. 다음에 찾을 것을 질문에 넣는 일은 질문 다시 쓰기가, '
                    '답을 직접 말하지 않는 기록까지 가까이 두는 일은 Reasoning Embedding이 맡습니다. 두 효과는 따로 볼 수 있습니다.')
    head(s, [('찾는 일은 ', INK), ('Reasoning Embedding', PURPLE), ('이, 잇는 일은 ', INK), ('질의 재작성', PURPLE), ('이 맡습니다', INK)],
         'Query Rewriting과 Reasoning Embedding의 상호보완 효과 및 벤치마크 근거', size=23)
    x, y, w, h = 70, 148, 545, 300
    out = [R('apx/l/bg', x, y, w, h, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=SHADOW_CARD),
           P('apx/l/ic', ICON['spool'], x + 22, y + 20, 26, 26),
           T('apx/l/t', x + 56, y + 18, 300, 30, 'Query Rewriting (질의 재작성)', size=14.5, color=PURPLE, weight='b', anchor='ctr'),
           T('apx/l/s', x + 22, y + 58, w - 44, 22, '복합 질문을 탐색 가능한 순서로 쪼개고 단서를 대입합니다', size=12, color=INK, weight='b'),
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
    out.append(T('apx/l/f', x + 22, y + 264, w - 44, 22, '빈칸(그날)은 Hop 1에서 찾은 단서(3/15)로 채워 Hop 2를 실행합니다', size=10.5, color=SUB))
    s.add('apx/l', out)
    # 오른쪽: Reasoning Embedding
    x2 = 665
    out = [R('apx/r/bg', x2, y, w, h, prst='roundRect', radius=20, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=SHADOW_CARD),
           T('apx/r/t', x2 + 22, y + 18, 340, 30, 'Reasoning Embedding (추론 임베딩)', size=14.5, color=PURPLE, weight='b', anchor='ctr'),
           T('apx/r/s', x2 + 22, y + 58, w - 44, 22, '단어가 안 겹쳐도 답의 단서가 될 기록을 가깝게 배치합니다', size=12, color=INK, weight='b')]
    cx, cy = x2 + 150, y + 190
    out.append(R('apx/r/near', cx - 92, cy - 70, 184, 140, prst='ellipse', fill=None, line=PURPLE2, line_w=1.5, dash='dash'))
    out.append(R('apx/r/star', cx - 11, cy - 11, 22, 22, prst='star5', fill=PURPLE, line='FFFFFF', line_w=1.5))
    out.append(T('apx/r/sl', cx - 60, cy + 12, 120, 18, '질문 ①', size=9.5, color=PURPLE, weight='b', align='c'))
    out.append(R('apx/r/k0', x2 + 380, y + 230, 120, 30, prst='roundRect', radius=10, fill='FFFFFF', line=LINE, line_w=1.0, dash='dash'))
    out.append(P('apx/r/k0i', ICON['talk'], x2 + 388, y + 235, 20, 20, alpha=55))
    out.append(T('apx/r/k0t', x2 + 412, y + 230, 90, 30, '지은 카톡', size=10, color=MUTE, anchor='ctr'))
    out.append(T('apx/r/k0l', x2 + 372, y + 262, 140, 18, '일반 임베딩 (멈)', size=9, color=MUTE, align='c'))
    out.append(R('apx/r/k1', cx + 16, cy - 46, 120, 30, prst='roundRect', radius=10, fill='FFFFFF', line=RING, line_w=1.8))
    out.append(P('apx/r/k1i', ICON['talk'], cx + 24, cy - 41, 20, 20))
    out.append(T('apx/r/k1t', cx + 48, cy - 46, 90, 30, '지은 카톡', size=10, color=INK, weight='b', anchor='ctr'))
    out.append(C('apx/r/arr', [(x2 + 378, y + 238), (x2 + 330, y + 200), (cx + 180, cy - 40), (cx + 138, cy - 31)], w=1.8, color=PURPLE2,
                 dash='dash', tail='triangle'))
    out.append(T('apx/r/q', x2 + 300, y + 112, 220, 40, ['‘박스 정리 다 했어!', '휴지 안 사 와도 돼’'], size=10, color=SUB, lnspc=14))
    out.append(T('apx/r/f', x2 + 22, y + 264, w - 44, 22, '동일 크기의 경량 임베딩 모델을 추론형 쌍(Query-Clue)으로 파인튜닝합니다', size=10.5, color=SUB))
    s.add('apx/r', out)
    # 아래: 논문 근거
    by = 472
    out = [R('apx/b/bg', 70, by, 1140, 150, prst='roundRect', radius=18, fill=LAV2, line=LINE2, line_w=1.0),
           T('apx/b/t', 92, by + 14, 500, 24, '학술 벤치마크에서 입증된 두 가지 독립 효과', size=12.5, color=PURPLE, weight='b')]
    items = [('1. 일반 임베딩의 추론형 검색 한계', ['단어 유사도 중심 임베딩은 추론이 필요한 검색에서 급격히 취약해집니다.', '동일 모델 기준 BEIR 59.0 → BRIGHT 18.3 (nDCG@10)¹']),
             ('2. 추론형 임베딩 + 질의 재작성 결합 시너지', ['추론용으로 학습한 임베딩 모델에 재작성된 질의를 넣으면 성능이 가장 높습니다.', 'ReasonIR-8B 기준 BRIGHT 24.4 → 29.9 (원래 질문 → 재작성 질문)²'])]
    for i, (t, ls) in enumerate(items):
        ix = 92 + i * 560
        out.append(T('apx/b/i%dt' % i, ix, by + 50, 520, 22, t, size=12, color=INK, weight='b'))
        out.append(T('apx/b/i%dl' % i, ix, by + 76, 530, 60, ls, size=11, color=BODY, lnspc=17))
    s.add('apx/b', out)
    foot(s, '¹ Su et al., "BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval", ICLR 2025 (SFR-Embedding-Mistral)   '
            '² Shao et al., "ReasonIR: Training Retrievers for Reasoning Tasks", COLM 2025.', y=640)
    return s


def a_kg():
    s = Slide('apx_kg', trans=('fade', 400), bar=False,
              notes='삼성 Personal Data Engine은 여러 앱의 기록을 AI로 분석해 기기 안 개인 지식 그래프에 쌓고, 규칙으로 따라 나오는 사실까지 미리 계산해 둡니다. '
                    'Weave는 같은 기록을 원문 그대로 색인해 두었다가, 질문이 들어오면 그 질문에 맞춰 원문 속 연결을 찾습니다. '
                    '그래프는 기록이 들어올 때 잇고, Weave는 질문이 들어올 때 잇습니다. 둘은 보완 관계입니다.')
    head(s, [('지식 그래프는 ', INK), ('기록이 들어올 때', PURPLE), (' 잇고, Weave는 ', INK), ('질문이 들어올 때', PURPLE), (' 잇습니다', INK)],
         '기존 삼성 개인 데이터 기반(PDE)을 대체하지 않고, 암묵적 단서 연결을 보완합니다', size=23)

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
    s.add('apx/kg1', lane('apx/kg1', 148, '개인 지식 그래프', '삼성 Personal Data Engine¹',
                          [('여러 앱의 기록', False), ('개체·관계 추출 저장', False), (['규칙으로 따라 나오는', '사실까지 미리 계산'], True),
                           ('질문 시 즉시 조회', False)],
                          '강점: 사람·날짜·장소처럼 스키마로 정리된 사실을 빠르고 정확하게 조회합니다'))
    s.add('apx/kg2', lane('apx/kg2', 316, 'Weave', '질문 시점에 잇는 추론 검색',
                          [('여러 앱의 기록', False), (['원문·벡터·메타데이터', 'Hybrid Index'], False), (['질문이 오면 그 질문에', '맞춰 암묵적 단서 탐색'], True),
                           ('찾은 단서로 연쇄 탐색', False)],
                          '강점: 미리 정의되지 않은 일상 표현(‘휴지 안 사 와도 돼’ → 집들이 초대)을 원문에서 직접 찾아 잇습니다', on=True))
    out = [R('apx/k3/bg', 70, 486, 1140, 122, prst='roundRect', radius=20, fill=LAV2, line=LINE2, line_w=1.0),
           T('apx/k3/t', 92, 502, 500, 24, 'PDE + Weave 상호보완 아키텍처', size=13, color=PURPLE, weight='b'),
           T('apx/k3/l', 92, 532, 1100, 70,
             ['• 명시적 사실(날짜·사람·앱·장소)은 메타데이터와 PDE 지식 그래프로 정확히 거르고, 비정형 대화 속 암묵적 단서는 Weave가 원문에서 찾습니다.',
              '• Weave가 연쇄 탐색으로 찾아내어 사용자가 최종 선택한 연결 결과는 향후 PDE 그래프의 새로운 관계 노드로 승격·캐싱할 수 있습니다.'],
             size=11.5, color=BODY, lnspc=18)]
    s.add('apx/k3', out)
    foot(s, '¹ Crocker, Horrocks, Nenov, "Semantic Technology in Your Pocket", ISWC 2025 Industry Track (CEUR-WS Vol-4085): 기기 안 RDFox로 '
            '그래프를 저장하고 규칙 기반 사실 계산(materialisation)을 수행.   GraphRAG(Edge et al., 2024) 또한 색인 시점과 질의 시점을 구분.', y=628)
    return s


def a_hops():
    s = Slide('apx_hops', trans=('fade', 400), bar=False,
              notes='와인 질문을 홉별로 보면, 그래프로 막히는 곳은 첫 단서 하나입니다. 그날 사진을 찾고 라벨을 읽는 일은 그래프도 잘할 수 있습니다. '
                    '문제는 지은이의 카톡이 집들이 초대라는 사실이 그래프에 들어 있을 가능성이 낮다는 점입니다.')
    head(s, [('지식 그래프만으로 막히는 곳은 ', INK), ('첫 번째 암묵적 단서(Hop 1)', PURPLE), ('입니다', INK)],
         '와인 시나리오를 Hop별로 분해해 본 지식 그래프 단독 방식 vs Weave 보완 방식')
    rows = [['① 집들이 날짜 찾기', '지은이네 집들이 = 3월 15일', ['‘집들이’라는 단어도, 캘린더 일정도 없어', '수신 시점에 집들이 이벤트로 추출되기 어렵습니다'],
             ['‘박스 정리 다 했어, 휴지 안 사 와도 돼’를', '질의 시점에 집들이 초대로 추론해 찾아냅니다']],
            ['② 그날 사진 추리기', '3월 15일 저녁 촬영 사진', '날짜·시간 조건 매칭이므로 그래프도 잘합니다', '메타데이터 필터(date: 2026-03-15)로 즉시 거릅니다'],
            ['③ 와인 이름 읽기', '와인병 라벨 텍스트', 'OCR 텍스트가 색인돼 있으면 조회 가능합니다', '온디바이스 OCR + sLLM으로 라벨에서 이름을 읽습니다']]
    table(s, 'apx/t', 70, 148, [200, 240, 350, 350], ['탐색 단계', '필요한 사실', '지식 그래프 단독', 'Weave (하이브리드 연쇄 탐색)'], rows, row_h=84, hi=0)
    out = [R('apx/n/bg', 70, 468, 1140, 122, prst='roundRect', radius=18, fill=LAV2, line=LINE2, line_w=1.0),
           T('apx/n/t', 92, 484, 600, 24, '왜 모든 카톡을 색인 시점에 미리 그래프로 변환하지 않나요?', size=13, color=PURPLE, weight='b'),
           T('apx/n/l', 92, 514, 1100, 70,
             ['• 사용자가 나중에 어떤 질문을 할지 모르는 상태에서 매일 쌓이는 모든 일상 메시지를 LLM으로 사전 해석하면 배터리·연산 부담이 과도합니다.',
              '• 또한 그래프 기반 멀티홉 검색(HippoRAG)의 오류 분석에서도 전체 오류 100건 중 76건이 사전 개체·관계 추출(OpenIE/NER) 누락에서 발생했습니다¹.'],
             size=11.5, color=BODY, lnspc=18)]
    s.add('apx/n', out)
    foot(s, '¹ Gutiérrez et al., "HippoRAG", NeurIPS 2024, Appendix F (MuSiQue 오류 100건 분석): 질의 개체 추출 오류 48건 + 문서 정보 추출(OpenIE) 누락 28건 = 76%.',
         y=612)
    return s


def a_compare():
    s = Slide('apx_cmp', trans=('fade', 400), bar=False,
              notes='방식마다 잘하는 일과 필요한 조건이 다릅니다. 어느 한 방식이 못 한다는 비교가 아니라, 이 질문에서 무엇이 필요한지의 비교입니다.')
    head(s, [('검색 방식마다 ', INK), ('강점과 전제 조건', PURPLE), ('이 다릅니다', INK)],
         '온디바이스 개인 기록 검색을 위한 4가지 접근법 비교')
    rows = [['지식 그래프 단독', '정리된 개체와 관계를 일관되게 잇고 빠르게 조회합니다', '행사·사진·와인의 관계가 색인 시점에 미리 추출돼 있어야 합니다'],
            ['일반 임베딩 + 멀티홉', '원문에서 단계별로 단서를 이어 탐색합니다', '표면 단어가 전혀 안 겹치는 일상 대화(Hop 1)에서 검색이 흔들립니다'],
            ['Weave (제안 방식)', ['추론형 임베딩(Reasoning Embedding)과 질의 재작성,', '메타데이터 필터를 결합해 암묵적 단서를 연쇄 탐색합니다'], '한국어 일상 기록에 맞춘 추론형 임베딩 파인튜닝 데이터가 필요합니다'],
            ['지식 그래프 + Weave 결합', '정형 관계(PDE)와 비정형 원문 추론(Weave)을 함께 활용합니다', '향후 삼성 PDE 위에서 가장 완성도 높은 온디바이스 검색이 됩니다']]
    table(s, 'apx/t', 70, 148, [240, 450, 450], ['접근 방식', '핵심 강점', '와인 질문 시나리오에서의 전제 조건 및 한계'], rows, row_h=80, hi=2)
    foot(s, '그래프와 원문 벡터 검색을 상호보완적으로 결합할 때 멀티홉 성능이 극대화됨: Gutiérrez et al., HippoRAG (NeurIPS 2024); Han et al., "RAG vs. GraphRAG" (arXiv 2025).',
         y=540)
    return s


def a_ux():
    s = Slide('apx_ux', trans=('fade', 400), bar=False,
              notes='세 가지 UX는 같은 다섯 단계로 움직입니다. 통화 중에는 일정과 최신 회의록과 메일을 이어 요약하고, 검색창에서는 카톡과 사진을 이어 이름을 찾고, '
                    '공항에서는 위치와 탑승권으로 Weave가 먼저 질문을 만들어 아내의 카톡과 링크를 이어 보낼 말을 추천합니다.')
    head(s, [('세 가지 UX 시나리오 모두 ', INK), ('동일한 5단계 파이프라인', PURPLE), ('으로 동작합니다', INK)],
         '00 데이터 색인 위에서 01 상황 인식 → 02 질의 재작성 → 03 연쇄 탐색 → 04 결과 제공으로 이어지는 공통 엔진')
    rows = [[['UX 1  기억 통합 검색', '통화 중 업무 파악'], '통화 화면에서\n위로 쓸어 올려 검색', ['‘언제 어디서 회의?’ →', '‘최신 회의록·안건은?’'], ['캘린더 일정 → 최신 회의 노트', '→ 민수 님 이메일 연쇄 탐색'], ['핵심 3줄 요약 카드', '+ 연결된 원본 기록']],
            [['UX 2  단서로 찾는 기억', '검색창 자동 완성'], '키보드 위\nWeave 실타래 버튼 탭', ['‘집들이는 언제였지?’ →', '‘[그날] 마셨던 와인은?’'], ['지은 카톡(3월 15일 추출)', '→ 3/15 갤러리 사진 + OCR'], ['배비치 소비뇽 블랑', '탭 한 번에 자동 완성']],
            [['UX 3  먼저 건네는 기억', '공항 도착 선제 추천'], ['위치(공항) + 탑승권 +', '아내와의 카톡 맥락 감지'], ['상황 신호로 Weave가', '내부 질의를 자동 생성'], ['아내 카톡(‘갈색병 사다 줘’)', '→ 링크 프리뷰 정식 명칭 확인'], ['보낼 카톡 문구 선제 추천', '(에스티 로더 갈색병)']]]
    table(s, 'apx/t', 70, 148, [230, 190, 230, 260, 230], ['시나리오', '01 상황 인식', '02 질의 재작성', '03 연쇄 탐색 (Hop 1 → 2)', '04 결과 제공'], rows,
          row_h=96, hi=1, pt=11)
    s.add('apx/n', [T('apx/n', 70, 488, 1140, 50,
                      ['• 중간 단서는 날짜(UX 2)뿐만 아니라 담당자 이름(UX 1, ‘민수 님’), 별칭·상품 링크(UX 3, ‘갈색병’ → 정식 제품명)까지 동일하게 이어집니다.',
                       '• 모든 시나리오에서 앱을 전환하지 않고 현재 보고 있던 화면·키보드 위에서 즉시 결과를 전달합니다.'], size=11.5, color=SUB, lnspc=18)])
    return s


def a_perf():
    s = Slide('apx_perf', trans=('fade', 400), bar=False,
              notes='온디바이스 실행 시간과 자원 예산입니다. 무거운 색인은 충전 중 유휴 시간에 미리 해 두고, 실시간 검색에서는 짧은 질의 분해와 경량 벡터 내적, 조건 필터만 수행해 1초 안에 응답합니다.')
    head(s, [('온디바이스 ', INK), ('실시간 응답 지연시간과 메모리 예산', PURPLE), (' 설계', INK)],
         '무거운 색인은 유휴 시간에 미리 끝내고, 검색 시점에는 꼭 필요한 경량 연산만 수행합니다', size=23)
    rows = [['00 데이터 색인 (사전 작업)', '충전 중 · 기기 유휴 시 (WorkManager)', '실시간 지연 0 ms', '신규 메시지·사진 증분 임베딩 및 메타데이터 색인 (배터리 영향 최소화)'],
            ['01 상황 인식 + 02 질의 재작성', '온디바이스 sLLM (짧은 하위 질문 생성)', '약 300 ~ 400 ms', '수십 토큰 이내의 구조화된 하위 질의 2개만 생성해 생성 지연 최소화'],
            ['03 연쇄 탐색 (Hop 1 → Hop 2)', 'Reasoning Embedding + 메타데이터 필터', '약 150 ~ 250 ms', '수만 건 개인 기록 벡터 내적(< 15 ms) + 날짜 필터링 + 타겟 사진 1장 OCR'],
            ['04 결과 제공 (전체 체감 시간)', '키보드·바텀시트 UI 즉시 렌더링', '총 0.6 ~ 0.9초 이내', '전체 기록을 LLM이 매번 읽지 않고 최종 후보 1~2건만 정제해 즉시 응답']]
    table(s, 'apx/t', 70, 148, [250, 280, 190, 420], ['파이프라인 단계', '실행 시점 및 담당 엔진', '목표 지연시간', '온디바이스 최적화 핵심 설계'], rows, row_h=74, hi=3, pt=11)
    out = [R('apx/p/bg', 70, 498, 1140, 116, prst='roundRect', radius=18, fill=LAV2, line=LINE2, line_w=1.0),
           T('apx/p/t', 92, 512, 600, 24, '메모리(RAM) 및 전력 최적화 전략', size=13, color=PURPLE, weight='b'),
           T('apx/p/l', 92, 540, 1100, 64,
             ['• 모델 가중치 공유: 질의 재작성용 sLLM은 갤럭시 시스템 내장 온디바이스 LLM에 경량 LoRA 어댑터만 올려 추가 RAM 점유를 최소화합니다.',
              '• 추론형 임베딩 경량화: Reasoning Embedding은 모델 크기를 키우지 않고 추론 데이터셋(Query-Clue 쌍) 파인튜닝과 INT4/INT8 양자화로 NPU/GPU에서 구동합니다.'],
             size=11.5, color=BODY, lnspc=18)]
    s.add('apx/p', out)
    foot(s, '참고: Android WorkManager 충전·유휴 제약 조건(JobScheduler) 및 온디바이스 INT4 양자화 sLLM/Embedding 추론 파이프라인 기준.', y=630)
    return s


def q_pde():
    s = Slide('apx_q_pde', trans=('fade', 400), bar=False,
              notes='맞습니다. 지식 그래프는 여러 단계 연결에 강하고, 저희도 날짜는 그래프처럼 필터로 정확히 거릅니다. 다만 지은 씨 카톡에는 집들이라는 말도 일정도 없습니다.')
    head(s, [('Q. ', PURPLE), ('삼성 PDE(개인 지식 그래프)로도 가능한 것 아닌가요?', INK)])
    qcard(s, 'apx/q1', 70, 140, 1140, 300, 'A. 정형 사실은 PDE가 빠르고, 그래프에 없는 암묵적 단서는 Weave가 채웁니다',
          ['• 지식 그래프(PDE)는 미리 정의된 개체·관계 연결에 강하며, Weave도 날짜·앱 같은 정형 조건은 필터로 정확히 거릅니다.',
           '• 다만 첫 단서인 지은이의 카톡(‘박스 정리 다 했어! 휴지 안 사 와도 돼’)에는 ‘집들이’라는 단어도, 캘린더 일정도 없습니다.',
           '• 이를 그래프로만 풀려면 메시지 수신 시점마다 모든 대화를 ‘집들이 초대’로 미리 추론·저장해야 해 연산 부담과 누락 위험이 큽니다.',
           '• Weave는 질문이 발생한 시점에 그 질문에 맞춰 원문에서 연결 고리를 찾아내므로, PDE를 대체하지 않고 빈틈을 보완합니다.'],
          ['요약: 기록이 들어올 때 정리하는 PDE(지식 그래프) + 질문이 들어올 때 원문 단서를 잇는 Weave의 상호보완 구조입니다.'], pt=13)
    chips_ = [('색인 시점에 정리하는 PDE 그래프', 'outline'), ('질의 시점에 단서를 잇는 Weave', 'fill'), ('정형 조건(날짜·앱)은 필터로 결합', 'soft')]
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
              notes='같은 날 찍었다는 이유만으로 그 집들이 와인이라고 정하지 않습니다. 메시지의 이따 올 때가 받은 날과 모임 날을 이어 주고, 사진의 시각과 장소와 내용이 뒷받침합니다.')
    head(s, [('Q. ', PURPLE), ('같은 날 찍은 사진이면 무조건 집들이 와인이라고 단정하나요?', INK)], size=23)
    qcard(s, 'apx/q2', 70, 140, 600, 330, 'A. 날짜 하나로 단정하지 않고 다중 근거를 교차 확인합니다',
          ['• 메시지의 ‘이따 올 때’ 표현이 카톡 수신일과 모임 당일을 이어 주고,',
           '• 사진의 촬영 시각(저녁 8시), 위치 정보, 시각적 내용(식탁·와인병)이',
           '  그 모임에서 찍은 사진인지를 함께 뒷받침합니다.',
           '• 만약 같은 날 다른 와인 사진이 더 있거나 근거가 모호하면,',
           '  단정하지 않고 후보 사진과 원문 출처를 함께 보여 주어 사용자가 고릅니다.'], pt=13)
    ev = [('talk', '‘이따 올 때’ (대화 맥락)', '카톡을 받은 날 = 집들이 모임 당일 (3월 15일)'),
          ('gallery', '저녁 8시 14분 (촬영 시각)', '오후 4시 12분 카톡 이후 저녁 모임 시간대에 촬영'),
          ('map', '지은이네 집 근처 (위치 메타데이터)', '사진 EXIF 위치 정보와 초대 장소의 일치'),
          ('gallery', '와인 병과 라벨 (시각·OCR 근거)', '식탁 사진 속 와인 병 라벨에서 BABICH 확인')]
    out = []
    for i, (ic, a, b) in enumerate(ev):
        y = 140 + i * 84
        out += [R('apx/ev%d/bg' % i, 700, y, 510, 70, prst='roundRect', radius=16, fill='FFFFFF', line=LINE2, line_w=1.2, shadow=SHADOW_SOFT),
                P('apx/ev%d/ic' % i, ICON[ic], 720, y + 19, 32, 32),
                T('apx/ev%d/a' % i, 768, y + 12, 420, 24, a, size=13, color=INK, weight='b'),
                T('apx/ev%d/b' % i, 768, y + 38, 420, 20, b, size=11, color=SUB)]
    out.append(R('apx/ev/ans', 700, 480, 510, 44, prst='roundRect', radius=14, fill=PURPLE, line=None))
    out.append(T('apx/ev/anst', 700, 480, 510, 44, '다중 근거 일치  →  배비치 소비뇽 블랑 (출처 함께 제시)', size=13, color='FFFFFF', weight='b', align='c', anchor='ctr'))
    s.add('apx/ev', out)
    return s


def q_apple():
    s = Slide('apx_q_apple', trans=('fade', 400), bar=False,
              notes='Apple은 iOS 27의 Siri AI가 기기 안 Spotlight 색인으로 메시지, 메일, 사진 속 개인 맥락을 찾아 답한다고 발표했습니다.')
    head(s, [('Q. ', PURPLE), ('Apple Siri(Personal Context)도 개인 기록을 찾지 않나요?', INK)])
    qcard(s, 'apx/q3', 70, 140, 560, 380, 'A. 빅테크가 검증한 핵심 방향이며, Weave는 ‘연쇄 추론과 키보드 UX’에 집중합니다',
          ['• Apple도 기기 내 Spotlight 색인으로 메시지·메일·사진 속 개인 맥락을',
           '  찾아 답하는 Personal Context를 발표하며 시장의 방향성을 입증했습니다.',
           '• 이는 온디바이스 개인 기록 검색이 스마트폰 AI의 다음 핵심 경쟁 축이라는',
           '  가장 확실한 시장 신호입니다.'],
          ['Apple Siri AI 타임라인: 발표 후 영어·한국어 베타 순차 도입 중¹'], pt=13)
    out = [R('apx/w/bg', 660, 140, 550, 380, prst='roundRect', radius=20, fill='FFFFFF', line=RING, line_w=1.8, shadow=SHADOW_CARD),
           T('apx/w/t', 684, 158, 500, 26, 'Weave만의 3가지 차별점', size=14, color=PURPLE, weight='b')]
    pts = [('삼성 키보드·화면 위에서 즉시 완결', '음성 비서를 따로 부르지 않고 검색창·통화·메신저 어디서든 키보드 버튼 하나로 동작합니다'),
           ('끊어진 단서를 잇는 멀티홉 연쇄 탐색', '단어가 안 겹치는 일상 대화(Hop 1)에서 단서를 뽑아 다음 검색(Hop 2)으로 잇는 추론에 특화됩니다'),
           ('갤럭시 생태계 및 PDE 결합', '삼성 기본 앱·월렛·위치 신호 및 삼성 Personal Data Engine(PDE)과 유기적으로 결합됩니다')]
    for i, (a, b) in enumerate(pts):
        y = 204 + i * 98
        out += numdot('apx/w/n%d' % i, 698, y + 14, i + 1, r=12, pt=9.5)
        out.append(T('apx/w/a%d' % i, 722, y, 470, 26, a, size=13, color=INK, weight='b'))
        out.append(T('apx/w/b%d' % i, 722, y + 30, 470, 44, b, size=11.5, color=BODY, wrap=True))
    s.add('apx/w', out)
    foot(s, '¹ Apple Newsroom: Personal Context & Spotlight 온디바이스 색인 발표 자료. Siri AI는 기기 내 모델과 Private Cloud Compute를 병행 사용.', y=548)
    return s


def q_llm():
    s = Slide('apx_q_llm', trans=('fade', 400), bar=False,
              notes='LLM은 글을 토큰마다 계산하며 만들어 연산량이 많고, 수많은 기록을 매번 읽기 어렵습니다. 임베딩은 입력당 한 번 계산해 후보를 고르고, LLM은 질문을 나누거나 최종 문장을 다듬을 때만 씁니다.')
    head(s, [('Q. ', PURPLE), ('왜 처음부터 LLM에게 모든 기록을 읽히지 않고 임베딩을 쓰나요?', INK)])
    qcard(s, 'apx/q4', 70, 140, 560, 330, 'A. 찾는 일은 가벼운 임베딩에, 나누고 다듬는 일만 sLLM에 맡깁니다',
          ['• LLM은 글자를 토큰마다 반복 생성(Autoregressive)하므로 연산량이 크고,',
           '  수만 건의 개인 기록을 매 질문마다 컨텍스트에 넣어 읽히기 어렵습니다.',
           '• 반면 임베딩은 기록당 미리 한 번만 계산해 두고 벡터 내적으로 즉시 찾으며,',
           '  sLLM은 질문을 쪼개거나(02) 최종 추려진 단서 1~2건을 읽을 때만 호출합니다.'],
          ['기록 벡터는 충전 중이거나 기기가 쉴 때 백그라운드에서 미리 만들어 둡니다.'], pt=13)
    rows = [['출력 형태', '토큰을 하나씩 생성 (문장)', '고정 차원 의미 벡터 1개'],
            ['연산 비용', '생성 토큰 수만큼 반복 연산 (무거움)', '입력당 단일 패스 + 내적 연산 (가벼움)'],
            ['대량 기록 처리', '매 질문마다 원문을 읽어야 함', '미리 색인해 두고 수 밀리초 내 검색']]
    table(s, 'apx/t', 660, 140, [140, 205, 205], ['구분', 'LLM 단독 처리', '임베딩 검색 (Weave)'], rows, row_h=78)
    return s


def q_data():
    s = Slide('apx_q_data', trans=('fade', 400), bar=False,
              notes='삼성 기본 앱은 사용자 동의 아래 기기 안에서 연동하고, 카카오톡 같은 외부 메신저는 사용자가 허용한 알림만 색인합니다.')
    head(s, [('Q. ', PURPLE), ('외부 앱 데이터 접근 권한과 사생활 보호는 어떻게 하나요?', INK)],
         '사용자가 허용한 기록만, 외부 서버 전송 없이 100% 기기 안에서 처리합니다')
    cards = [('데이터 접근 방식', ['• 삼성 기본 앱(갤러리·노트·캘린더·메일·월렛)은', '  사용자 동의 아래 기기 내 API로 연동합니다.', '• 카카오톡 등 외부 메신저는 사용자가 허용한', '  알림 텍스트(NotificationListener)만 색인합니다¹.'],
              ['통화 음성은 상시 녹음·청취하지 않으며,', '사용자가 직접 실행할 때만 동작합니다.']),
             ('배터리 및 발열 관리', ['• 초기 대량 색인은 기기가 충전 중이거나', '  유휴 상태일 때만 백그라운드로 수행합니다².', '• 실시간 사용 중에는 가벼운 벡터 검색과', '  추려진 단서 1~2건에 대한 sLLM만 실행합니다.'],
              ['평소 배터리 소모와 발열 영향을', '체감할 수 없는 수준으로 억제합니다.']),
             ('사생활 보호 및 제어권', ['• 모든 원본 기록과 색인(Hybrid Index)은', '  클라우드 전송 없이 기기 내부에만 저장됩니다.', '• 암호화 키는 Android Keystore 하드웨어', '  보안 영역으로 철저히 보호합니다³.'],
              ['앱별 색인 허용/차단 및 인덱스 초기화를', '언제든 사용자가 직접 제어할 수 있습니다.'])]
    for i, (t, a, b) in enumerate(cards):
        qcard(s, 'apx/d%d' % i, 70 + i * 386, 150, 368, 340, t, a, b, pt=12)
    foot(s, '¹ Android Developers, "NotificationListenerService"   ² Android Developers, "WorkManager: Define work requests (RequiresCharging, RequiresDeviceIdle)"   '
            '³ Android Developers, "Android Keystore system"', y=512)
    return s


CREDITS = [('와인 잔 (임베딩 장)', 'Davide Restivo, "A glass of red wine", Wikimedia Commons, CC BY-SA 2.0'),
           ('풀밭 위 와인', 'Jamie Street, "Wine on a meadow", Unsplash (Wikimedia Commons 사본), CC0'),
           ('샴페인', 'L.C. Nøttaasen, "Champagne pouring", Wikimedia Commons, CC BY 2.0'),
           ('바닷가 와인', 'Jez Timms, "Enjoying a bottle of red wine", Unsplash, CC0'),
           ('집 저녁 식탁', 'Jason M. C. Han, "Special foods & cuisines in Chongqing - Family Dinner 3rd", Wikimedia Commons, CC BY-SA 4.0')]


def a_credits():
    s = Slide('apx_credit', trans=('fade', 400), bar=False, notes='How it Works에 쓴 사진의 출처입니다.')
    head(s, [('사진 출처', INK)], 'How it Works 장표 내 갤러리 예시 사진 출처')
    out = []
    for i, (a, b) in enumerate(CREDITS):
        y = 160 + i * 64
        out += [R('apx/cr%d/bg' % i, 160, y, 960, 52, prst='roundRect', radius=14, fill='FFFFFF', line=LINE2, line_w=1.0),
                T('apx/cr%d/a' % i, 184, y, 200, 52, a, size=12, color=PURPLE, weight='b', anchor='ctr'),
                T('apx/cr%d/b' % i, 390, y, 720, 52, b, size=11, color=BODY, anchor='ctr')]
    s.add('apx/cr', out)
    s.add('apx/cr_n', [T('apx/cr_n', 160, 500, 960, 40, '배비치 소비뇽 블랑 사진, 건배 사진 및 UI 화면은 자체 제작 에셋입니다.', size=11, color=SUB, align='c')])
    return s


APPENDIX = [a_divider, a_roles, a_rem, a_kg, a_hops, a_compare, a_ux, a_perf, q_pde, q_sameday, q_apple, q_llm, q_data, a_credits]
